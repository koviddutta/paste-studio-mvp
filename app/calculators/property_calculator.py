import logging
from typing import TypedDict, Optional, Any
from app.engines.ingredient_classifier import IngredientData
from app.database import supabase_client
from .water_activity import calculate_water_activity, estimate_shelf_life, Composition
from .viscosity import calculate_viscosity, ViscosityParams


class FormulationProperties(TypedDict):
    """Structured data for all calculated formulation properties."""

    water_activity: Optional[float]
    shelf_life_weeks: int
    shelf_life_risk: str
    viscosity_pas: Optional[float]
    dosage_g_per_kg_base: int
    composition: Composition
    composition_pct: dict[str, float]


def _calculate_composition(
    classified_ingredients: list[IngredientData], batch_size_g: float
) -> tuple[Composition, dict[str, float]]:
    """Calculates the total mass composition from classified ingredients."""
    comp: Composition = {
        "water_g": 0.0,
        "sugar_g": 0.0,
        "protein_g": 0.0,
        "fat_g": 0.0,
        "other_g": 0.0,
        "total_g": 0.0,
    }
    for ing in classified_ingredients:
        ing_mass = ing.get("mass_g", 0.0)
        comp["water_g"] += ing_mass * (ing.get("moisture_pct", 0.0) / 100.0)
        comp["sugar_g"] += ing_mass * (ing.get("sugar_pct", 0.0) / 100.0)
        comp["protein_g"] += ing_mass * (ing.get("protein_pct", 0.0) / 100.0)
        comp["fat_g"] += ing_mass * (ing.get("fat_pct", 0.0) / 100.0)
    comp["total_g"] = sum((ing.get("mass_g", 0.0) for ing in classified_ingredients))
    solids = comp["sugar_g"] + comp["protein_g"] + comp["fat_g"]
    comp["other_g"] = comp["total_g"] - comp["water_g"] - solids
    comp_pct = {
        k.replace("_g", ""): v / comp["total_g"] * 100 if comp["total_g"] > 0 else 0
        for k, v in comp.items()
    }
    return (comp, comp_pct)


def _calculate_dosage(sugar_concentration_pct: float) -> int:
    """Calculates gelato dosage based on sweetness."""
    if sugar_concentration_pct == 0:
        return 100
    dosage = int(3500 / sugar_concentration_pct)
    return min(max(dosage, 60), 150)


def calculate_all_properties(
    classified_ingredients: list[IngredientData], batch_size_g: float
) -> FormulationProperties | None:
    """Orchestrates the calculation of all formulation properties.

    Args:
        classified_ingredients: A list of ingredients with their properties and mass.
        batch_size_g: The total batch size in grams.

    Returns:
        A dictionary containing all calculated properties, or None on critical failure.
    """
    constants = supabase_client.fetch_constants()
    if not constants:
        logging.error("Could not fetch formulation constants. Aborting calculation.")
        return None
    composition, composition_pct = _calculate_composition(
        classified_ingredients, batch_size_g
    )
    aw = calculate_water_activity(composition, constants)
    shelf_life_weeks, shelf_life_risk = estimate_shelf_life(
        aw if aw is not None else 1.0
    )
    viscosity_params: ViscosityParams = {
        "sugar_concentration_pct": composition_pct.get("sugar", 0.0),
        "temperature_c": 25.0,
    }
    viscosity = calculate_viscosity(viscosity_params, constants)
    dosage = _calculate_dosage(composition_pct.get("sugar", 0.0))
    return {
        "water_activity": aw,
        "shelf_life_weeks": shelf_life_weeks,
        "shelf_life_risk": shelf_life_risk,
        "viscosity_pas": viscosity,
        "dosage_g_per_kg_base": dosage,
        "composition": composition,
        "composition_pct": composition_pct,
    }