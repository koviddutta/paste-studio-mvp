"""
Sweet to paste conversion logic for the Paste Core module.
Placeholder for future implementation.
"""

from .domain import Ingredient
from .composition import calculate_paste_composition
from .validation import validate_paste


def formulate_paste(
    sweet: Ingredient,
    base_template: dict[str, float],
    batch_weight_g: float,
    sweet_ratio: float,
    base_composition_lookup: dict[str, Ingredient],
) -> dict[str, object]:
    """
    Build a paste recipe from:
      - one sweet Ingredient (composition known, quantity_g will be set)
      - base_template: {ingredient_name: parts}
      - total batch_weight_g
      - sweet_ratio: fraction of batch weight that comes from the sweet (0–1)
      - base_composition_lookup: {ingredient_name: Ingredient prototype}
    Returns:
      {
        "ingredients": [Ingredient, ...],
        "composition": PasteComposition,
        "validation": PasteValidation,
      }
    """
    if not 0.0 < sweet_ratio < 1.0:
        raise ValueError("sweet_ratio must be between 0 and 1 (exclusive).")
    if batch_weight_g <= 0:
        raise ValueError("batch_weight_g must be positive.")
    if not base_template:
        raise ValueError("base_template cannot be empty.")
    sweet_weight = batch_weight_g * sweet_ratio
    base_weight = batch_weight_g - sweet_weight
    total_parts = sum(base_template.values()) or 1.0
    recipe: list[Ingredient] = []
    recipe.append(
        Ingredient(
            name=sweet.name,
            quantity_g=round(sweet_weight, 2),
            sugars_pct=sweet.sugars_pct,
            fat_pct=sweet.fat_pct,
            msnf_pct=sweet.msnf_pct,
            other_solids_pct=sweet.other_solids_pct,
            water_pct=sweet.water_pct,
        )
    )
    for name, parts in base_template.items():
        fraction = parts / total_parts
        qty = base_weight * fraction
        proto = base_composition_lookup.get(name)
        if proto is None:
            recipe.append(
                Ingredient(name=name, quantity_g=round(qty, 2), other_solids_pct=100.0)
            )
        else:
            recipe.append(
                Ingredient(
                    name=name,
                    quantity_g=round(qty, 2),
                    sugars_pct=proto.sugars_pct,
                    fat_pct=proto.fat_pct,
                    msnf_pct=proto.msnf_pct,
                    other_solids_pct=proto.other_solids_pct,
                    water_pct=proto.water_pct,
                )
            )
    comp = calculate_paste_composition(recipe)
    validation = validate_paste(comp)
    return {"ingredients": recipe, "composition": comp, "validation": validation}