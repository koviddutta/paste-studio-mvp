"""
Base template logic for the Paste Core module.
Placeholder for future implementation.
"""

from __future__ import annotations
from app.database.supabase_client import get_supabase
from .domain import BaseTemplateComposition, Ingredient


def _fetch_base_template_row(template_id: int) -> dict:
    supabase = get_supabase()
    resp = (
        supabase.table("base_formulation_templates")
        .select("*")
        .eq("id", template_id)
        .single()
        .execute()
    )
    row = resp.data
    if not row:
        raise ValueError(f"base_formulation_templates: id {template_id} not found")
    return row


def _fetch_ingredient_composition(name: str) -> Ingredient:
    """
    Fetch one ingredient from ingredients_master as a composition prototype.

    Assumes ingredients_master has:
      - name
      - moisture_pct
      - sugar_pct (or sugars_pct)
      - fat_pct
      - msnf_pct (or derivable later)
    """
    supabase = get_supabase()
    resp = (
        supabase.table("ingredients_master")
        .select("*")
        .ilike("name", name)
        .limit(1)
        .execute()
    )
    rows = resp.data or []
    if not rows:
        raise ValueError(f"ingredients_master: ingredient '{name}' not found")
    row = rows[0]
    water_pct = float(row.get("moisture_pct") or 0.0)
    sugar_pct = float(row.get("sugar_pct") or row.get("sugars_pct") or 0.0)
    fat_pct = float(row.get("fat_pct") or 0.0)
    msnf_pct = float(row.get("msnf_pct") or 0.0)
    other_pct = max(0.0, 100.0 - (water_pct + sugar_pct + fat_pct + msnf_pct))
    return Ingredient(
        name=row.get("name") or name,
        water_pct=water_pct,
        sugars_pct=sugar_pct,
        fat_pct=fat_pct,
        msnf_pct=msnf_pct,
        other_pct=other_pct,
    )


def _extract_ingredients_map(base_ingredients: dict | list) -> dict[str, float]:
    """
    Normalises base_ingredients JSONB to a simple:
        { ingredient_name: parts_or_percent, ... }

    Supports:
      A) {"Milk 3%": 45, "Cream 25%": 15, ...}
      B) [{"name": "Milk 3%", "relative_pct_of_base": 0.5}, ...]
    """
    if base_ingredients is None:
        raise ValueError("base_ingredients is NULL")
    if isinstance(base_ingredients, dict):
        if all((isinstance(v, (int, float)) for v in base_ingredients.values())):
            return {str(k): float(v) for k, v in base_ingredients.items()}
        raise ValueError(
            f"Unsupported dict structure in base_ingredients: {base_ingredients}"
        )
    if isinstance(base_ingredients, list):
        ingredients_map: dict[str, float] = {}
        for item in base_ingredients:
            if not isinstance(item, dict):
                raise ValueError(f"Unsupported item in base_ingredients list: {item}")
            name = item.get("name") or item.get("ingredient") or item.get("label")
            if not name:
                raise ValueError(f"No ingredient name field in: {item}")
            parts = (
                item.get("relative_pct_of_base")
                or item.get("percent")
                or item.get("parts")
                or item.get("ratio")
                or item.get("amount")
            )
            if parts is None:
                raise ValueError(
                    f"No numeric relative_pct_of_base/percent/etc in: {item}"
                )
            ingredients_map[str(name)] = float(parts)
        return ingredients_map
    raise ValueError(f"Unsupported base_ingredients type: {type(base_ingredients)}")


def compute_base_template_from_db(template_id: int) -> BaseTemplateComposition:
    """
    Loads a base formulation template from the database (by id)
    and computes its aggregate composition (per 100g of base).
    """
    row = _fetch_base_template_row(template_id)
    template_name = row.get("name") or f"Base Template #{template_id}"
    base_ingredients_raw = row.get("base_ingredients")
    ingredients_map = _extract_ingredients_map(base_ingredients_raw)
    if not ingredients_map:
        raise ValueError(f"Base template {template_id} has no ingredients.")
    total_parts = sum(ingredients_map.values())
    if total_parts <= 0:
        raise ValueError(f"Base template {template_id} total parts <= 0")
    agg_water = 0.0
    agg_sugars = 0.0
    agg_fat = 0.0
    agg_msnf = 0.0
    agg_other = 0.0
    agg_afp = 0.0
    agg_pod = 0.0
    agg_de = 0.0
    breakdown_pct = {}
    for ing_name, parts in ingredients_map.items():
        fraction = parts / total_parts
        breakdown_pct[ing_name] = round(fraction * 100, 2)
        ing = _fetch_ingredient_composition(ing_name)
        agg_water += ing.water_pct * fraction
        agg_sugars += ing.sugars_pct * fraction
        agg_fat += ing.fat_pct * fraction
        agg_msnf += ing.msnf_pct * fraction
        agg_other += ing.other_pct * fraction
        agg_afp += ing.afp_per_100g * fraction
        agg_pod += ing.pod_per_100g * fraction
        agg_de += ing.de_equivalent * fraction
    return BaseTemplateComposition(
        template_id=template_id,
        name=template_name,
        water_pct=round(agg_water, 2),
        sugars_pct=round(agg_sugars, 2),
        fat_pct=round(agg_fat, 2),
        msnf_pct=round(agg_msnf, 2),
        other_pct=round(agg_other, 2),
        afp_per_100g=round(agg_afp, 1),
        pod_per_100g=round(agg_pod, 1),
        de_equivalent=round(agg_de, 1),
        ingredient_breakdown=breakdown_pct,
    )