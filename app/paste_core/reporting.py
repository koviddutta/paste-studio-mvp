from __future__ import annotations

from typing import List
from app.paste_core.domain import (
    PasteMetrics,
    PasteDesignReport,
    PasteIngredientLine,
    PasteInfusionRecommendation,
)
from app.paste_core.metrics import compute_paste_metrics
from app.paste_core.validation import validate_paste
from app.paste_core.optimizer import optimize_paste, apply_plan_to_metrics
from app.paste_core.gelato_infusion import recommend_paste_in_gelato
from app.database.sweet_profiler import load_sweet_profile_and_base
from app.database.supabase_client import get_supabase


def _build_ingredient_lines_for_1kg(
    sweet_name: str,
    sweet_pct: float,
    base_pct: float,
    plan_actions,
) -> List[PasteIngredientLine]:
    """
    Build a practical paste recipe per 1 kg final paste, for the user.

    Simplified assumption:
      - We treat 'sweet mass' (finished Indian sweet) as the core ingredient.
      - We treat optimizer actions (SMP, ghee, evaporation) as adjustments.
      - We rescale everything so that final paste is 1000 g.
    """
    # Start from a conceptual 1 kg paste before optimization
    # with sweet_pct vs base_pct. For user-facing recipe,
    # we collapse the underlying base into 'sweet paste base'.
    # To keep it simple, we expose:
    #   - one line: "Sweet mass"
    #   - plus SMP / Ghee additions
    #   - and evaporation as a process note, not as a negative ingredient.

    # 1. Start with 1000 g of "sweet paste base"
    sweet_base_g = 1000.0

    # 2. Add optimizer actions on top (we’ll accumulate grams)
    added_ingredients: dict[str, float] = {}
    evap_water_g = 0.0

    for a in plan_actions:
        if a.ingredient_name == "__EVAPORATE_WATER__":
            evap_water_g += -a.delta_g_per_kg  # delta is negative
            continue
        added_ingredients[a.ingredient_name] = (
            added_ingredients.get(a.ingredient_name, 0.0) + a.delta_g_per_kg
        )

    # 3. Compute total mass after adjustments (before scaling)
    total_mass_raw = sweet_base_g + sum(added_ingredients.values()) - evap_water_g
    if total_mass_raw <= 0:
        total_mass_raw = 1000.0

    scale = 1000.0 / total_mass_raw

    lines: List[PasteIngredientLine] = []
    lines.append(
        PasteIngredientLine(
            ingredient_name=f"{sweet_name} (finished sweet mass)",
            grams_per_kg_final=sweet_base_g * scale,
            note="Use actual Gulab Jamun / Jalebi etc. in this amount per 1 kg final paste.",
        )
    )

    for ing_name, grams in added_ingredients.items():
        lines.append(
            PasteIngredientLine(
                ingredient_name=ing_name,
                grams_per_kg_final=grams * scale,
                note="Optimizer-recommended addition.",
            )
        )

    if evap_water_g > 1.0:
        # We do not list water as an ingredient; we mention it as process.
        lines.append(
            PasteIngredientLine(
                ingredient_name="Evaporation loss (water)",
                grams_per_kg_final=evap_water_g * scale,
                note="Approximate water to evaporate during cooking to reach target Aw and solids.",
            )
        )

    return lines


def _generate_simple_sop(
    sweet_name: str,
    category: str,
    plan_actions,
) -> list[str]:
    """
    Very simple, generic SOP derived from category + evaporation/nature of actions.
    Later you can plug in your SOP generator / processing_rules table.
    """
    steps: list[str] = []

    steps.append(
        f"1. Weigh out the finished sweet: see 'Paste Recipe' for grams of {sweet_name} per 1 kg paste."
    )
    steps.append("2. Break or cut the sweet into small pieces for even blending.")

    # Check if SMP / Ghee are present to tailor instructions
    uses_smp = any("skim" in a.ingredient_name.lower() for a in plan_actions)
    uses_ghee = any("ghee" in a.ingredient_name.lower() for a in plan_actions)
    has_evap = any(a.ingredient_name == "__EVAPORATE_WATER__" for a in plan_actions)

    if uses_smp:
        steps.append(
            "3. Pre-mix Skim Milk Powder with a small portion of warm milk/water to avoid lumping."
        )
    if uses_ghee:
        steps.append(
            "4. Melt ghee gently (40–50°C) and keep warm for incorporation."
        )

    steps.append(
        "5. Combine sweet mass, SMP slurry (if used), melted ghee (if used) and any other additions in a jacketed kettle or heavy-bottom pan."
    )

    if has_evap:
        steps.append(
            "6. Heat the mixture with gentle agitation, targeting a slow simmer. "
            "Cook down until the batch weight matches the target final weight (~1 kg), "
            "corresponding to the specified evaporation loss in the paste recipe."
        )
    else:
        steps.append(
            "6. Heat gently to 75–85°C with continuous stirring for pasteurisation, "
            "without significant evaporation."
        )

    steps.append(
        "7. Blend with a rotor-stator or high-shear blender until smooth, spreadable paste consistency is achieved."
    )
    steps.append(
        "8. Rapidly cool the paste to <10°C and store under refrigeration until use."
    )

    return steps


def generate_paste_design_report(
    sweet_name: str,
    formulation_type: str = "sweet_paste",
    base_for_infusion: str = "white_base",
) -> PasteDesignReport:
    """
    High-level orchestrator:
      - Load sweet profile + base composition
      - Compute metrics
      - Validate
      - Optimize (solids, fat, Aw)
      - Apply optimization
      - Re-validate
      - Compute gelato infusion recommendation
      - Build a 1kg paste recipe + SOP for user
    """
    sweet_profile, sweet_comp, base_comp = load_sweet_profile_and_base(sweet_name)

    sweet_pct = sweet_profile.default_sweet_pct
    base_pct = 100.0 - sweet_pct

    # 1. Before optimization
    metrics_before = compute_paste_metrics(
        sweet_pct=sweet_pct,
        base_pct=base_pct,
        sweet_comp=sweet_comp,
        base_comp=base_comp,
    )
    validation_before = validate_paste(
        metrics=metrics_before,
        formulation_type=formulation_type,
        sweet_profile=sweet_profile,
    )

    # 2. Optimization
    plan = optimize_paste(
        metrics=metrics_before,
        formulation_type=formulation_type,
        sweet_profile=sweet_profile,
    )

    # 3. After optimization
    metrics_after = apply_plan_to_metrics(metrics_before, plan)
    validation_after = validate_paste(
        metrics=metrics_after,
        formulation_type=formulation_type,
        sweet_profile=sweet_profile,
    )

    # 4. Infusion recommendation into a gelato base
    # You likely have base profiles in DB; here we assume a helper exists.
    base_profile = GelatoBaseProfile(
        name=base_for_infusion,
        sugar_pct=17.87,  # example: your actual white base
        fat_pct=6.01,
        solids_pct=34.93,
        afp_total=None,
    )
    infusion_rec = recommend_paste_in_gelato(
        paste_metrics=metrics_after,
        base_profile=base_profile,
        sweet_profile=sweet_profile,
    )

    # 5. 1kg paste recipe lines (for practical use)
    ingredients = _build_ingredient_lines_for_1kg(
        sweet_name=sweet_name,
        sweet_pct=sweet_pct,
        base_pct=base_pct,
        plan_actions=plan.actions,
    )

    # 6. Simple SOP
    sop_steps = _generate_simple_sop(
        sweet_name=sweet_name,
        category=sweet_profile.category,
        plan_actions=plan.actions,
    )

    key_notes: list[str] = []
    key_notes.append(
        f"Paste optimized from solids {metrics_before.solids_pct:.1f}% → {metrics_after.solids_pct:.1f}%, "
        f"fat {metrics_before.fat_pct:.1f}% → {metrics_after.fat_pct:.1f}%, "
        f"Aw {metrics_before.water_activity:.3f} → {metrics_after.water_activity:.3f}."
    )
    key_notes.extend(validation_after.key_recommendations)

    return PasteDesignReport(
        sweet_name=sweet_name,
        category=sweet_profile.category,
        formulation_type=formulation_type,
        ingredients=ingredients,
        metrics_before=metrics_before,
        metrics_after=metrics_after,
        validation_before=validation_before,
        validation_after=validation_after,
        infusion_recommendation=infusion_rec,
        key_notes=key_notes,
        sop_steps=sop_steps,
    )
