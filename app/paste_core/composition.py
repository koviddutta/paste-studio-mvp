"""
Composition logic for the Paste Core module.
Placeholder for future implementation.
"""

from .domain import Ingredient, PasteComposition
from .water_activity import estimate_water_activity


def _aggregate_masses(ingredients: list[Ingredient]) -> dict[str, float]:
    totals = {
        "sugars_g": 0.0,
        "fat_g": 0.0,
        "msnf_g": 0.0,
        "other_g": 0.0,
        "water_g": 0.0,
        "total_g": 0.0,
    }
    for ing in ingredients:
        q = ing.quantity_g
        totals["total_g"] += q
        totals["sugars_g"] += q * ing.sugars_pct / 100.0
        totals["fat_g"] += q * ing.fat_pct / 100.0
        totals["msnf_g"] += q * ing.msnf_pct / 100.0
        totals["other_g"] += q * ing.other_pct / 100.0
        if ing.water_pct > 0:
            totals["water_g"] += q * ing.water_pct / 100.0
    if totals["water_g"] == 0.0:
        solids_g = (
            totals["sugars_g"] + totals["fat_g"] + totals["msnf_g"] + totals["other_g"]
        )
        totals["water_g"] = max(totals["total_g"] - solids_g, 0.0)
    return totals


def calculate_paste_composition(ingredients: list[Ingredient]) -> PasteComposition:
    totals = _aggregate_masses(ingredients)
    total_g = totals["total_g"] or 1.0
    sugars_pct = totals["sugars_g"] / total_g * 100.0
    fat_pct = totals["fat_g"] / total_g * 100.0
    msnf_pct = totals["msnf_g"] / total_g * 100.0
    other_pct = totals["other_g"] / total_g * 100.0
    water_pct = totals["water_g"] / total_g * 100.0
    solids_pct = sugars_pct + fat_pct + msnf_pct + other_pct
    aw = estimate_water_activity(
        water_g=totals["water_g"],
        sugar_like_solids_g=totals["sugars_g"]
        + totals["fat_g"]
        + totals["msnf_g"]
        + totals["other_g"],
    )
    return PasteComposition(
        total_weight_g=round(total_g, 2),
        total_sugars_pct=round(sugars_pct, 2),
        total_fat_pct=round(fat_pct, 2),
        total_msnf_pct=round(msnf_pct, 2),
        total_other_pct=round(other_pct, 2),
        total_water_pct=round(water_pct, 2),
        water_activity=round(aw, 3),
    )