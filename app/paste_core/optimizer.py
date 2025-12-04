"""
Optimizer logic for the Paste Core module.
Analyzes formulation deficiencies and suggests specific ingredient adjustments
using database thresholds and ingredient properties.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import logging
from app.database.supabase_client import get_supabase
from .domain import PasteMetrics, SweetProfile, PasteOptimizationPlan, PasteAdjustment
from .validation import ThresholdRule, _load_extended_thresholds
from app.paste_core.multi_aw import estimate_aw_multicomponent
from app.paste_core.sugar_science import compute_sugar_system
from app.paste_core.domain import PasteMetrics
from .validation import _load_extended_thresholds  # already imported above in your file


def _load_ingredient_row(name_ilike: str) -> Optional[dict]:
    """
    Load a single ingredient row from ingredients_master by name (ILIKE).
    Returns None if not found.
    """
    supabase = get_supabase()
    try:
        resp = (
            supabase.table("ingredients_master")
            .select("*")
            .ilike("name", name_ilike)
            .limit(1)
            .single()
            .execute()
        )
        return resp.data
    except Exception as e:
        logging.exception(
            "Could not load ingredient '%s' from ingredients_master: %s", name_ilike, e
        )
        return None


def _solids_fraction(row: dict) -> float:
    """
    Compute solids fraction (0–1) from ingredients_master row.
    solids = 100 - moisture_pct
    """
    moisture = float(row.get("moisture_pct", 0.0) or 0.0)
    solids = max(0.0, 100.0 - moisture)
    if solids <= 0:
        return 0.0
    return solids / 100.0


def _fat_fraction(row: dict) -> float:
    """
    Fat fraction (0–1) from ingredients_master row.
    """
    fat = float(row.get("fat_pct", 0.0) or 0.0)
    if fat <= 0:
        return 0.0
    return fat / 100.0


def _pick_fat_source() -> Optional[dict]:
    """
    Try to pick a high-fat ingredient as primary fat source.
    Prefer 'Ghee', then 'Cream', then any class D_FAT ingredient.
    """
    supabase = get_supabase()
    for name in ["Ghee", "ghee"]:
        row = _load_ingredient_row(name)
        if row:
            return row
    for name in ["Cream", "cream"]:
        row = _load_ingredient_row(name)
        if row:
            return row
    try:
        resp = (
            supabase.table("ingredients_master")
            .select("*")
            .eq("class", "D_FAT")
            .limit(1)
            .execute()
        )
        rows = resp.data or []
        return rows[0] if rows else None
    except Exception as e:
        logging.exception("Could not pick generic fat source: %s", e)
        return None


def _get_target_from_rule(rule: ThresholdRule) -> Optional[float]:
    """
    Choose a reasonable target value from a ThresholdRule.
    Prefer optimal_min; else acceptable_min; else critical_min.
    """
    for attr in ("optimal_min", "acceptable_min", "critical_min"):
        val = getattr(rule, attr)
        if val is not None:
            return float(val)
    return None


def optimize_paste(
    metrics: PasteMetrics,
    formulation_type: str,
    sweet_profile: SweetProfile | None = None,
) -> PasteOptimizationPlan:
    """
    v1 Paste Optimizer:
      - Uses DB thresholds to identify if solids and fat are below target.
      - Suggests ingredient-level adjustments (SMP for solids; ghee/cream for fat).
      - Returns actions in grams per 1 kg paste, plus explanatory notes.

    It does NOT try to perfectly solve aw or sugars in v1: those are re-checked
    by the existing validation engine after adjustments are applied.
    """
    ext_rules = _load_extended_thresholds(formulation_type=formulation_type)
    actions: list[PasteAdjustment] = []
    notes: list[str] = []
    solids_rule = (
        ext_rules.get("paste_total_solids_pct")
        or ext_rules.get("solids_total")
        or ext_rules.get("total_solids_pct")
    )
    target_solids_pct = _get_target_from_rule(solids_rule) if solids_rule else None
    if target_solids_pct is not None and metrics.solids_pct < target_solids_pct:
        deficit_pct = target_solids_pct - metrics.solids_pct
        needed_solids_g_per_kg = deficit_pct * 10.0
        smp_row = _load_ingredient_row("Skim Milk Powder")
        if smp_row is None:
            notes.append(
                f"Total solids {metrics.solids_pct:.1f}% < target {target_solids_pct:.1f}%, but 'Skim Milk Powder' not found in ingredients_master. Add a high-solids dairy ingredient manually."
            )
        else:
            smp_sf = _solids_fraction(smp_row)
            if smp_sf <= 0:
                notes.append(
                    f"Skim Milk Powder row has zero solids fraction; check ingredients_master.moisture_pct."
                )
            else:
                smp_g_per_kg = needed_solids_g_per_kg / smp_sf
                actions.append(
                    PasteAdjustment(
                        ingredient_name=smp_row.get("name", "Skim Milk Powder"),
                        delta_g_per_kg=smp_g_per_kg,
                        reason=f"Raise total solids from {metrics.solids_pct:.1f}% to ≈{target_solids_pct:.1f}% using a dairy MSNF source.",
                    )
                )
                notes.append(
                    f"Total solids are low ({metrics.solids_pct:.1f}% < {target_solids_pct:.1f}%). Add ≈{smp_g_per_kg:.1f} g SMP per 1 kg paste to reach solids target; re-run validation to confirm new Aw and texture."
                )
    fat_rule = (
        ext_rules.get("paste_fat_pct")
        or ext_rules.get("fat_total")
        or ext_rules.get("fat_pct")
    )
    target_fat_pct = _get_target_from_rule(fat_rule) if fat_rule else None
    if target_fat_pct is not None and metrics.fat_pct < target_fat_pct:
        deficit_fat_pct = target_fat_pct - metrics.fat_pct
        needed_fat_g_per_kg = deficit_fat_pct * 10.0
        fat_source = _pick_fat_source()
        if fat_source is None:
            notes.append(
                f"Fat {metrics.fat_pct:.1f}% < target {target_fat_pct:.1f}%, but no suitable fat source (Ghee/Cream/D_FAT) found in ingredients_master."
            )
        else:
            ff = _fat_fraction(fat_source)
            if ff <= 0:
                notes.append(
                    f"Selected fat source '{fat_source.get('name', '?')}' has zero fat_pct; check ingredients_master."
                )
            else:
                fat_ing_g_per_kg = needed_fat_g_per_kg / ff
                actions.append(
                    PasteAdjustment(
                        ingredient_name=fat_source.get("name", "Fat source"),
                        delta_g_per_kg=fat_ing_g_per_kg,
                        reason=f"Raise fat from {metrics.fat_pct:.1f}% to ≈{target_fat_pct:.1f}% for better mouthfeel and cryoprotection.",
                    )
                )
                notes.append(
                    f"Fat is low ({metrics.fat_pct:.1f}% < {target_fat_pct:.1f}%). Add ≈{fat_ing_g_per_kg:.1f} g of {fat_source.get('name', 'fat source')} per 1 kg paste to reach fat target; re-run validation to confirm AFP and Aw."
                )
    sugars_rule = (
        ext_rules.get("paste_sugars_pct")
        or ext_rules.get("final_sugars_pct")
        or ext_rules.get("sugars_total")
    )
    target_sugars_pct = _get_target_from_rule(sugars_rule) if sugars_rule else None
    if target_sugars_pct is not None:
        if metrics.sugar_pct > target_sugars_pct:
            notes.append(
                f"Sugars {metrics.sugar_pct:.1f}% > target {target_sugars_pct:.1f}%. In v1, optimizer does not auto-swap sucrose → DE syrups; consider reducing sucrose or partially replacing with DE40/DE60 to bring sweetness and AFP into range."
            )
        elif metrics.sugar_pct < target_sugars_pct:
            notes.append(
                f"Sugars {metrics.sugar_pct:.1f}% < target {target_sugars_pct:.1f}%. Consider increasing sugars (or using higher-AFP sugars) if sweetness and freezing softness are insufficient."
            )
    if not actions:
        notes.append(
            "No quantitative adjustments suggested: either paste already meets solids/fat targets, or required target rules not found. Use validation messages as guidance."
        )
    return PasteOptimizationPlan(
        formulation_type=formulation_type,
        target_solids_pct=target_solids_pct,
        target_fat_pct=target_fat_pct,
        target_sugars_pct=target_sugars_pct,
        actions=actions,
        notes=notes,
    )



def apply_plan_to_metrics(
    metrics: PasteMetrics,
    plan: PasteOptimizationPlan,
) -> PasteMetrics:
    """
    Apply a PasteOptimizationPlan (actions in g per 1 kg) to the current
    PasteMetrics, using ingredients_master composition, and recompute
    full PasteMetrics for the 'optimized' paste.

    Assumptions:
      - Start from a nominal 1 kg batch whose composition matches `metrics`.
      - Each action.delta_g_per_kg is added to that batch.
      - Ingredient composition is taken from ingredients_master:
          water_pct   <- moisture_pct
          sugars_pct  <- sugar_pct
          fat_pct     <- fat_pct
          msnf_pct    <- protein_pct  (proxy for MSNF)
          other_pct   <- remaining % (100 - moisture - fat - sugar - protein)
    """

    # 1. Convert current metrics (percentages) to grams for a 1 kg batch
    total_mass_g = 1000.0

    sugar_g = metrics.sugar_pct * 10.0
    fat_g = metrics.fat_pct * 10.0
    msnf_g = metrics.msnf_pct * 10.0
    other_g = metrics.other_pct * 10.0
    water_g = metrics.water_pct * 10.0

    # 2. For each adjustment, fetch ingredient composition and update grams
    for action in plan.actions:
        delta = action.delta_g_per_kg
        if abs(delta) < 1e-6:
            continue

        row = _load_ingredient_row(action.ingredient_name)
        if row is None:
            logging.warning(
                "apply_plan_to_metrics: ingredient '%s' not found in ingredients_master; skipping.",
                action.ingredient_name,
            )
            continue

        moisture_pct = float(row.get("moisture_pct", 0.0) or 0.0)
        fat_pct = float(row.get("fat_pct", 0.0) or 0.0)
        sugar_pct = float(row.get("sugar_pct", 0.0) or 0.0)
        protein_pct = float(row.get("protein_pct", 0.0) or 0.0)

        used_pct = moisture_pct + fat_pct + sugar_pct + protein_pct
        other_pct = max(0.0, 100.0 - used_pct)

        # grams contributed by this action
        water_add = delta * moisture_pct / 100.0
        sugar_add = delta * sugar_pct / 100.0
        fat_add = delta * fat_pct / 100.0
        msnf_add = delta * protein_pct / 100.0
        other_add = delta * other_pct / 100.0

        total_mass_g += delta
        water_g += water_add
        sugar_g += sugar_add
        fat_g += fat_add
        msnf_g += msnf_add
        other_g += other_add

    if total_mass_g <= 0:
        raise ValueError("apply_plan_to_metrics: total_mass_g became non-positive")

    # 3. Recompute percentages per 100 g for the new paste
    sugar_pct_new = 100.0 * sugar_g / total_mass_g
    fat_pct_new = 100.0 * fat_g / total_mass_g
    msnf_pct_new = 100.0 * msnf_g / total_mass_g
    other_pct_new = 100.0 * other_g / total_mass_g
    solids_pct_new = 100.0 * (sugar_g + fat_g + msnf_g + other_g) / total_mass_g
    water_pct_new = 100.0 * water_g / total_mass_g

    # 4. Recompute aw using the multi-component model
    aw_new = estimate_aw_multicomponent(
        water_pct=water_pct_new,
        sugars_pct=sugar_pct_new,
        msnf_pct=msnf_pct_new,
        fat_pct=fat_pct_new,
        other_pct=other_pct_new,
        sugar_profile=None,  # you can later pass a real sugar spectrum here
    )

    # 5. Recompute sugar science (AFP/PAC/POD/DE/SP)
    sugar_model = compute_sugar_system(
        total_sugars_pct=sugar_pct_new,
        sugar_profile=None,  # or real spectrum once wired
    )

    # 6. Return a fresh PasteMetrics instance
    return PasteMetrics(
        sugar_pct=sugar_pct_new,
        fat_pct=fat_pct_new,
        msnf_pct=msnf_pct_new,
        other_pct=other_pct_new,
        solids_pct=solids_pct_new,
        water_pct=water_pct_new,
        afp_total=sugar_model["afp_total"],
        pod_sweetness=sugar_model["pod_sweetness"],
        de_total=sugar_model["de_total"],
        pac_total=sugar_model["pac_total"],
        sp_total=sugar_model["sp_total"],
        water_activity=aw_new,
    )
