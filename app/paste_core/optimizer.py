"""
Optimizer logic for the Paste Core module.
Placeholder for future implementation of optimization algorithms that automatically adjust
ingredient ratios to meet specific nutritional or functional targets (e.g. specific fat content, solids, or cost).
"""

# app/paste_core/optimizer.py

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Optional, List
import logging

from app.database.supabase_client import get_supabase
from .domain import (
    PasteMetrics,
    SweetProfile,
    PasteOptimizationPlan,
    PasteAdjustment,
)
from .validation import ThresholdRule, _load_extended_thresholds


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
        logging.warning("Could not load ingredient '%s' from ingredients_master: %s", name_ilike, e)
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
    # Try Ghee
    for name in ["Ghee", "ghee"]:
        row = _load_ingredient_row(name)
        if row:
            return row
    # Try Cream
    for name in ["Cream", "cream"]:
        row = _load_ingredient_row(name)
        if row:
            return row
    # Fallback: any D_FAT
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
        logging.warning("Could not pick generic fat source: %s", e)
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

    actions: List[PasteAdjustment] = []
    notes: List[str] = []

    # --- SOLIDS TARGET ---
    solids_rule = (
        ext_rules.get("paste_total_solids_pct")
        or ext_rules.get("solids_total")
        or ext_rules.get("total_solids_pct")
    )
    target_solids_pct = _get_target_from_rule(solids_rule) if solids_rule else None

    if target_solids_pct is not None and metrics.solids_pct < target_solids_pct:
        deficit_pct = target_solids_pct - metrics.solids_pct  # % points per 100 g
        # For 1 kg paste, each 1% solids = 10 g solids.
        needed_solids_g_per_kg = deficit_pct * 10.0

        smp_row = _load_ingredient_row("Skim Milk Powder")
        if smp_row is None:
            notes.append(
                f"Total solids {metrics.solids_pct:.1f}% < target {target_solids_pct:.1f}%, "
                f"but 'Skim Milk Powder' not found in ingredients_master. Add a high-solids dairy ingredient manually."
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
                        reason=(
                            f"Raise total solids from {metrics.solids_pct:.1f}% "
                            f"to ≈{target_solids_pct:.1f}% using a dairy MSNF source."
                        ),
                    )
                )
                notes.append(
                    f"Total solids are low ({metrics.solids_pct:.1f}% < {target_solids_pct:.1f}%). "
                    f"Add ≈{smp_g_per_kg:.1f} g SMP per 1 kg paste to reach solids target; "
                    "re-run validation to confirm new Aw and texture."
                )

    # --- FAT TARGET ---
    fat_rule = (
        ext_rules.get("paste_fat_pct")
        or ext_rules.get("fat_total")
        or ext_rules.get("fat_pct")
    )
    target_fat_pct = _get_target_from_rule(fat_rule) if fat_rule else None

    if target_fat_pct is not None and metrics.fat_pct < target_fat_pct:
        deficit_fat_pct = target_fat_pct - metrics.fat_pct
        needed_fat_g_per_kg = deficit_fat_pct * 10.0  # 1% fat ~ 10 g fat per 1 kg

        fat_source = _pick_fat_source()
        if fat_source is None:
            notes.append(
                f"Fat {metrics.fat_pct:.1f}% < target {target_fat_pct:.1f}%, "
                f"but no suitable fat source (Ghee/Cream/D_FAT) found in ingredients_master."
            )
        else:
            ff = _fat_fraction(fat_source)
            if ff <= 0:
                notes.append(
                    f"Selected fat source '{fat_source.get('name','?')}' has zero fat_pct; check ingredients_master."
                )
            else:
                fat_ing_g_per_kg = needed_fat_g_per_kg / ff
                actions.append(
                    PasteAdjustment(
                        ingredient_name=fat_source.get("name", "Fat source"),
                        delta_g_per_kg=fat_ing_g_per_kg,
                        reason=(
                            f"Raise fat from {metrics.fat_pct:.1f}% to ≈{target_fat_pct:.1f}% "
                            f"for better mouthfeel and cryoprotection."
                        ),
                    )
                )
                notes.append(
                    f"Fat is low ({metrics.fat_pct:.1f}% < {target_fat_pct:.1f}%). "
                    f"Add ≈{fat_ing_g_per_kg:.1f} g of {fat_source.get('name','fat source')} per 1 kg paste "
                    "to reach fat target; re-run validation to confirm AFP and Aw."
                )

    # --- SUGARS TARGET (only notes in v1) ---
    sugars_rule = (
        ext_rules.get("paste_sugars_pct")
        or ext_rules.get("final_sugars_pct")
        or ext_rules.get("sugars_total")
    )
    target_sugars_pct = _get_target_from_rule(sugars_rule) if sugars_rule else None

    if target_sugars_pct is not None:
        if metrics.sugar_pct > target_sugars_pct:
            notes.append(
                f"Sugars {metrics.sugar_pct:.1f}% > target {target_sugars_pct:.1f}%. "
                "In v1, optimizer does not auto-swap sucrose → DE syrups; "
                "consider reducing sucrose or partially replacing with DE40/DE60 to bring sweetness and AFP into range."
            )
        elif metrics.sugar_pct < target_sugars_pct:
            notes.append(
                f"Sugars {metrics.sugar_pct:.1f}% < target {target_sugars_pct:.1f}%. "
                "Consider increasing sugars (or using higher-AFP sugars) if sweetness and freezing softness are insufficient."
            )

    if not actions:
        notes.append(
            "No quantitative adjustments suggested: either paste already meets solids/fat targets, "
            "or required target rules not found. Use validation messages as guidance."
        )

    return PasteOptimizationPlan(
        formulation_type=formulation_type,
        target_solids_pct=target_solids_pct,
        target_fat_pct=target_fat_pct,
        target_sugars_pct=target_sugars_pct,
        actions=actions,
        notes=notes,
    )
