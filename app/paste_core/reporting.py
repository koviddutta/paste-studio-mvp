from __future__ import annotations
from app.paste_core.domain import (
    PasteMetrics,
    PasteDesignReport,
    PasteIngredientLine,
    PasteInfusionRecommendation,
    GelatoBaseProfile,
)
from app.paste_core.metrics import compute_paste_metrics
from app.paste_core.validation import validate_paste
from app.paste_core.optimizer import optimize_paste, apply_plan_to_metrics
from app.paste_core.gelato_infusion import recommend_paste_in_gelato
from app.paste_core.sweet_profiler import build_sweet_profile_from_db
from app.paste_core.base_templates import compute_base_template_from_db
from app.database.supabase_client import get_supabase


def _build_ingredient_lines_for_1kg(
    sweet_name: str, sweet_pct: float, base_pct: float, plan_actions
) -> list[PasteIngredientLine]:
    """
    Build a practical paste recipe per 1 kg final paste, for the user.

    Simplified assumption:
      - We treat 'sweet mass' (finished Indian sweet) as the core ingredient.
      - We treat optimizer actions (SMP, ghee, evaporation) as adjustments.
      - We rescale everything so that final paste is 1000 g.
    """
    sweet_base_g = 1000.0
    added_ingredients: dict[str, float] = {}
    evap_water_g = 0.0
    for a in plan_actions:
        if a.ingredient_name == "__EVAPORATE_WATER__":
            evap_water_g += -a.delta_g_per_kg
            continue
        added_ingredients[a.ingredient_name] = (
            added_ingredients.get(a.ingredient_name, 0.0) + a.delta_g_per_kg
        )
    total_mass_raw = sweet_base_g + sum(added_ingredients.values()) - evap_water_g
    if total_mass_raw <= 0:
        total_mass_raw = 1000.0
    scale = 1000.0 / total_mass_raw
    lines: list[PasteIngredientLine] = []
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
        lines.append(
            PasteIngredientLine(
                ingredient_name="Evaporation loss (water)",
                grams_per_kg_final=evap_water_g * scale,
                note="Approximate water to evaporate during cooking to reach target Aw and solids.",
            )
        )
    return lines


def _generate_simple_sop(sweet_name: str, category: str, plan_actions) -> list[str]:
    """
    Very simple, generic SOP derived from category + evaporation/nature of actions.
    Later you can plug in your SOP generator / processing_rules table.
    """
    steps: list[str] = []
    steps.append(
        f"1. Weigh out the finished sweet: see 'Paste Recipe' for grams of {sweet_name} per 1 kg paste."
    )
    steps.append("2. Break or cut the sweet into small pieces for even blending.")
    uses_smp = any(("skim" in a.ingredient_name.lower() for a in plan_actions))
    uses_ghee = any(("ghee" in a.ingredient_name.lower() for a in plan_actions))
    has_evap = any((a.ingredient_name == "__EVAPORATE_WATER__" for a in plan_actions))
    if uses_smp:
        steps.append(
            "3. Pre-mix Skim Milk Powder with a small portion of warm milk/water to avoid lumping."
        )
    if uses_ghee:
        steps.append("4. Melt ghee gently (40–50°C) and keep warm for incorporation.")
    steps.append(
        "5. Combine sweet mass, SMP slurry (if used), melted ghee (if used) and any other additions in a jacketed kettle or heavy-bottom pan."
    )
    if has_evap:
        steps.append(
            "6. Heat the mixture with gentle agitation, targeting a slow simmer. Cook down until the batch weight matches the target final weight (~1 kg), corresponding to the specified evaporation loss in the paste recipe."
        )
    else:
        steps.append(
            "6. Heat gently to 75–85°C with continuous stirring for pasteurisation, without significant evaporation."
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
    supabase = get_supabase()
    resp = (
        supabase.table("sweet_compositions")
        .select("id")
        .ilike("sweet_name", f"%{sweet_name}%")
        .limit(1)
        .execute()
    )
    if not resp.data:
        raise ValueError(f"Sweet '{sweet_name}' not found in sweet_compositions table.")
    sweet_id = resp.data[0]["id"]
    sweet_profile = build_sweet_profile_from_db(sweet_id)
    base_template = compute_base_template_from_db(sweet_profile.base_template_id)
    sweet_comp = {
        "water_pct": sweet_profile.water_pct,
        "sugars_pct": sweet_profile.sugars_pct,
        "fat_pct": sweet_profile.fat_pct,
        "msnf_pct": sweet_profile.msnf_pct,
        "other_pct": sweet_profile.other_pct,
    }
    base_comp = {
        "water_pct": base_template.water_pct,
        "sugars_pct": base_template.sugars_pct,
        "fat_pct": base_template.fat_pct,
        "msnf_pct": base_template.msnf_pct,
        "other_pct": base_template.other_pct,
    }
    sweet_pct = sweet_profile.sweet_pct_default
    base_pct = 100.0 - sweet_pct
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
    plan = optimize_paste(
        metrics=metrics_before,
        formulation_type=formulation_type,
        sweet_profile=sweet_profile,
    )
    metrics_after = apply_plan_to_metrics(metrics_before, plan)
    validation_after = validate_paste(
        metrics=metrics_after,
        formulation_type=formulation_type,
        sweet_profile=sweet_profile,
    )
    base_profile = GelatoBaseProfile(
        name=base_for_infusion,
        sugar_pct=17.87,
        fat_pct=6.01,
        solids_pct=34.93,
        afp_total=None,
    )
    infusion_rec = recommend_paste_in_gelato(
        paste_metrics=metrics_after,
        base_profile=base_profile,
        sweet_profile=sweet_profile,
    )
    ingredients = _build_ingredient_lines_for_1kg(
        sweet_name=sweet_name,
        sweet_pct=sweet_pct,
        base_pct=base_pct,
        plan_actions=plan.actions,
    )
    sop_steps = _generate_simple_sop(
        sweet_name=sweet_name,
        category=sweet_profile.category,
        plan_actions=plan.actions,
    )
    key_notes: list[str] = []
    key_notes.append(
        f"Paste optimized from solids {metrics_before.solids_pct:.1f}% → {metrics_after.solids_pct:.1f}%, fat {metrics_before.fat_pct:.1f}% → {metrics_after.fat_pct:.1f}%, Aw {metrics_before.water_activity:.3f} → {metrics_after.water_activity:.3f}."
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