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