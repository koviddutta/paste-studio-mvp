from typing import TypedDict, Any, Mapping
from app.database import supabase_client


class GelatoScienceConstants(TypedDict):
    sugar_type: str
    afp_value: float
    sp_value: float
    de_value: float


def calculate_afp(
    sugar_composition: dict[str, float], constants: Mapping[str, GelatoScienceConstants]
) -> float:
    """Calculate Anti-Freezing Power from sugar composition.

    AFP measures how much a sugar depresses the freezing point of water
    compared to sucrose (which has an AFP of 1.0).

    Args:
        sugar_composition: Dict of sugar names to their mass in grams.
        constants: Dict of gelato science constants from the database.

    Returns:
        Total AFP value for the formulation.
    """
    total_afp = 0.0
    for sugar_type, mass_g in sugar_composition.items():
        afp_coefficient = constants.get(sugar_type.lower(), {"afp_value": 1.0}).get(
            "afp_value", 1.0
        )
        total_afp += mass_g / 100.0 * afp_coefficient
    return total_afp


def calculate_sp(
    sugar_composition: dict[str, float], constants: Mapping[str, GelatoScienceConstants]
) -> tuple[float, float]:
    """Calculate Sweetening Power (SP) and Sweetening Power on DR (POD).

    SP measures the perceived sweetness compared to sucrose (SP of 1.0).
    POD normalizes the sweetness against the total sugar mass.

    Args:
        sugar_composition: Dict of sugar names to their mass in grams.
        constants: Dict of gelato science constants from the database.

    Returns:
        A tuple containing (total_sp, pod_percentage).
    """
    total_sp = 0.0
    for sugar_type, mass_g in sugar_composition.items():
        sp_coefficient = constants.get(sugar_type.lower(), {"sp_value": 1.0}).get(
            "sp_value", 1.0
        )
        total_sp += mass_g / 100.0 * sp_coefficient
    total_sugar_mass = sum(sugar_composition.values())
    pod = total_sp / total_sugar_mass * 100.0 if total_sugar_mass > 0 else 0
    return (total_sp, pod)


def calculate_de(
    sugar_composition: dict[str, float], constants: Mapping[str, GelatoScienceConstants]
) -> tuple[float, str]:
    """Calculate weighted Dextrose Equivalence (D.E.) and predict texture.

    D.E. is a measure of the amount of reducing sugars present in a sugar
    product, relative to dextrose (glucose).

    Args:
        sugar_composition: Dict of sugar names to their mass in grams.
        constants: Dict of gelato science constants from the database.

    Returns:
        A tuple containing (weighted_de, texture_prediction).
    """
    total_sugar_mass = sum(sugar_composition.values())
    if total_sugar_mass == 0:
        return (0.0, "UNKNOWN")
    weighted_de = 0.0
    for sugar_type, mass_g in sugar_composition.items():
        de_value = constants.get(sugar_type.lower(), {"de_value": 100.0}).get(
            "de_value", 100.0
        )
        weighted_de += mass_g / total_sugar_mass * de_value
    if weighted_de < 30:
        texture = "COMPACT"
    elif 30 <= weighted_de <= 50:
        texture = "BALANCED"
    else:
        texture = "SOFT"
    return (weighted_de, texture)


def calculate_pac(composition: dict[str, float]) -> float:
    """Calculate Freezing Point Depression (PAC) from all ingredients.

    PAC is the temperature at which the first ice crystals begin to form.

    Args:
        composition: Dict of component masses in grams (sugar_g, protein_g, etc.).

    Returns:
        Total PAC (freezing point depression in °C).
    """
    pac = 0.0
    pac += composition.get("sugar_g", 0.0) * -0.025
    pac += composition.get("protein_g", 0.0) * -0.01
    pac += composition.get("salt_g", 0.0) * -0.1
    pac += composition.get("alcohol_g", 0.0) * -0.05
    return pac


def calculate_characterization_pct(
    classified_ingredients: list[dict[str, float | str | None]],
) -> float:
    """Calculates the percentage of flavoring ingredients.

    Flavoring ingredients are typically from classes B (Nuts), part of A (like cream for some recipes),
    and F (Aromatics, though usually small mass). This is a simplified model where we consider
    the main non-sugar, non-stabilizer, non-water component as the characterization.

    Args:
        classified_ingredients: List of ingredients with their full data.

    Returns:
        Percentage of characterization ingredients in the total mix.
    """
    total_mass = sum((ing.get("mass_g", 0.0) for ing in classified_ingredients))
    if total_mass == 0:
        return 0.0
    char_mass = sum(
        (
            ing.get("mass_g", 0.0)
            for ing in classified_ingredients
            if ing.get("class_name") in ["B_NUT", "F_AROMATIC"]
            or (
                ing.get("class_name") == "D_FAT"
                and "cocoa butter" not in ing.get("name", "")
            )
        )
    )
    return char_mass / total_mass * 100.0


def calculate_final_sugars_pct(composition: dict[str, float]) -> float:
    """Calculates the final percentage of sugars in the total mass.

    Args:
        composition: Dict of component masses in grams.

    Returns:
        The percentage of sugar in the total formulation.
    """
    total_g = composition.get("total_g", 0.0)
    sugar_g = composition.get("sugar_g", 0.0)
    if total_g == 0:
        return 0.0
    return sugar_g / total_g * 100.0


def calculate_compensation(
    classified_ingredients: list[dict[str, float | str | None]],
    composition: dict[str, float],
) -> tuple[str, str]:
    """Determines what needs to be added to balance the formulation.

    This is a simplified compensation logic. A real system would be more complex.

    Args:
        classified_ingredients: List of ingredients.
        composition: Dict of component masses.

    Returns:
        A tuple of (component_to_add, reason).
    """
    final_sugars = calculate_final_sugars_pct(composition)
    has_nuts = any((ing.get("class_name") == "B_NUT" for ing in classified_ingredients))
    has_dairy = any(
        (ing.get("class_name") == "A_DAIRY" for ing in classified_ingredients)
    )
    if has_nuts and final_sugars < 18:
        return (
            "Sugars",
            "Nut pastes require higher sugar for texture and preservation.",
        )
    if not has_nuts and (not has_dairy) and (final_sugars < 20):
        return ("Sugars", "Fruit/sorbet-style pastes need more sugar for body.")
    fat_pct = composition.get("fat_g", 0.0) / composition.get("total_g", 1.0) * 100
    if has_dairy and fat_pct < 7:
        return (
            "Fats (Cream/Butter)",
            "Dairy pastes need sufficient fat for creaminess.",
        )
    return ("None", "The formulation appears reasonably balanced.")