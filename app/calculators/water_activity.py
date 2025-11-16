import math
from typing import TypedDict
import logging


class Composition(TypedDict):
    """Represents the mass composition of a formulation."""

    water_g: float
    sugar_g: float
    protein_g: float
    fat_g: float
    other_g: float
    total_g: float


MOLAR_MASS_WATER = 18.015
MOLAR_MASS_SUGAR = 342.3
MOLAR_MASS_PROTEIN = 1000


def calculate_water_activity(
    composition: Composition, constants: dict[str, float]
) -> float | None:
    """Calculates water activity (Aw) using the Norrish equation.

    Args:
        composition: A dictionary with the mass of water, sugar, and protein.
        constants: A dictionary of formulation constants from the database.

    Returns:
        The calculated water activity (Aw) value, or None on error.
    """
    k_sugar = constants.get("K_SUGAR_NORRISH")
    k_protein = constants.get("K_PROTEIN_NORRISH")
    if k_sugar is None or k_protein is None:
        logging.error("Norrish constants (K_SUGAR/K_PROTEIN) not found.")
        return None
    total_g = composition.get("total_g", 0.0)
    if total_g == 0:
        return 1.0
    moles_water = composition["water_g"] / MOLAR_MASS_WATER
    moles_sugar = composition["sugar_g"] / MOLAR_MASS_SUGAR
    moles_protein = composition["protein_g"] / MOLAR_MASS_PROTEIN
    total_moles = moles_water + moles_sugar + moles_protein
    if total_moles == 0:
        return 1.0
    x_water = moles_water / total_moles
    x_sugar = moles_sugar / total_moles
    x_protein = moles_protein / total_moles
    try:
        exponent = -(k_sugar * x_sugar**2 + k_protein * x_protein**2)
        aw = x_water * math.exp(exponent)
        return min(max(aw, 0.0), 1.0)
    except (OverflowError, ValueError) as e:
        logging.exception(f"Error in water activity calculation: {e}")
        return None


def estimate_shelf_life(water_activity: float) -> tuple[int, str]:
    """Estimates shelf life in weeks based on water activity.

    Args:
        water_activity: The calculated water activity of the product.

    Returns:
        A tuple containing the estimated shelf life in weeks and a risk assessment string.
    """
    if water_activity < 0.68:
        return (16, "Low (Rancidity Risk)")
    if 0.68 <= water_activity <= 0.75:
        return (12, "Safe (Target Range)")
    if 0.75 < water_activity <= 0.85:
        return (4, "Risky (Slow Mold Growth)")
    return (1, "Unsafe (Fast Mold Growth)")