import logging
from typing import TypedDict, Any, Optional, Mapping
from app.database import supabase_client


class ExtendedGelatoScienceConstants(TypedDict):
    """Enhanced gelato science constants with complete Gelato University data."""

    sugar_type: str
    sp_value: float
    afp_value: float
    de_value: float
    dry_residual_pct: float
    texture_impact: str
    stability_notes: str


class MSNFStabilizerBalance(TypedDict):
    """MSNF and Stabilizer balance rules by formulation type."""

    formulation_type: str
    msnf_min_pct: float
    msnf_max_pct: float
    stabilizer_min_pct: float
    stabilizer_max_pct: float
    fat_min_pct: float
    fat_max_pct: float
    explanation: str
    scientific_reason: str


class ExtendedValidationThresholds(TypedDict):
    """Extended validation thresholds with formulation type specificity."""

    parameter_name: str
    formulation_type: str
    optimal_min: Optional[float]
    optimal_max: Optional[float]
    acceptable_min: float
    acceptable_max: float
    critical_min: Optional[float]
    critical_max: Optional[float]
    explanation: str
    scientific_basis: str
    measurement_unit: str


def fetch_extended_gelato_constants() -> Mapping[str, ExtendedGelatoScienceConstants]:
    """Fetches comprehensive gelato science constants from enhanced table.

    Returns:
        Dictionary mapping sugar type to complete scientific data.
    """
    if not supabase_client.supabase:
        logging.error("Supabase client not available for extended gelato constants.")
        return {}
    try:
        response = (
            supabase_client.supabase.table("gelato_science_constants")
            .select("*")
            .execute()
        )
        if response.data:
            return {item["sugar_type"].lower(): item for item in response.data}
        return {}
    except Exception as e:
        logging.exception(f"Error fetching extended gelato science constants: {e}")
        return {}


def fetch_msnf_stabilizer_balance_rules() -> Mapping[str, MSNFStabilizerBalance]:
    """Fetches MSNF and stabilizer balance rules by formulation type.

    Returns:
        Dictionary mapping formulation type to balance rules.
    """
    if not supabase_client.supabase:
        logging.error("Supabase client not available for MSNF balance rules.")
        return {}
    try:
        response = (
            supabase_client.supabase.table("msnf_stabilizer_balance")
            .select("*")
            .execute()
        )
        if response.data:
            return {item["formulation_type"]: item for item in response.data}
        return {}
    except Exception as e:
        logging.exception(f"Error fetching MSNF stabilizer balance rules: {e}")
        return {}


def fetch_extended_validation_thresholds() -> Mapping[
    str, list[ExtendedValidationThresholds]
]:
    """Fetches extended validation thresholds with formulation type specificity.

    Returns:
        Dictionary mapping parameter name to list of threshold data by formulation type.
    """
    if not supabase_client.supabase:
        logging.error(
            "Supabase client not available for extended validation thresholds."
        )
        return {}
    try:
        response = (
            supabase_client.supabase.table("validation_thresholds_extended")
            .select("*")
            .execute()
        )
        if response.data:
            grouped_thresholds = {}
            for item in response.data:
                param_name = item["parameter_name"]
                if param_name not in grouped_thresholds:
                    grouped_thresholds[param_name] = []
                grouped_thresholds[param_name].append(item)
            return grouped_thresholds
        return {}
    except Exception as e:
        logging.exception(f"Error fetching extended validation thresholds: {e}")
        return {}


def get_formulation_type_from_ingredients(classified_ingredients: list[dict]) -> str:
    """Determines formulation type based on classified ingredients.

    Args:
        classified_ingredients: List of ingredients with their full data.

    Returns:
        Formulation type string for threshold lookup.
    """
    has_chocolate = any(
        (
            "chocolate" in ing.get("name", "").lower()
            or "cocoa" in ing.get("name", "").lower()
            for ing in classified_ingredients
        )
    )
    has_nuts = any((ing.get("class_name") == "B_NUT" for ing in classified_ingredients))
    has_eggs = any(
        ("egg" in ing.get("name", "").lower() for ing in classified_ingredients)
    )
    has_dairy = any(
        (ing.get("class_name") == "A_DAIRY" for ing in classified_ingredients)
    )
    has_fruit = any(
        (
            "fruit" in ing.get("name", "").lower()
            or any(
                (
                    fruit in ing.get("name", "").lower()
                    for fruit in ["mango", "strawberry", "orange", "lemon", "apple"]
                )
            )
            for ing in classified_ingredients
        )
    )
    if has_chocolate:
        return "cocoa_chocolate"
    elif has_nuts or has_eggs:
        return "eggs_nuts"
    elif has_fruit and has_dairy:
        return "dairy_fruit"
    elif has_dairy and (not has_fruit):
        return "pure_dairy"
    elif has_fruit and (not has_dairy):
        return "fruit_sorbet"
    else:
        return "dairy_fruit"


def get_sugar_recommendations(
    current_afp: float,
    current_sp: float,
    formulation_type: str,
    thresholds: Mapping[str, list[ExtendedValidationThresholds]],
) -> list[str]:
    """Provides sugar substitution recommendations based on scientific targets.

    Args:
        current_afp: Current Anti-Freezing Power
        current_sp: Current Sweetening Power
        formulation_type: Type of formulation (dairy, nuts, etc.)
        thresholds: Extended validation thresholds

    Returns:
        List of recommendation strings for sugar adjustments.
    """
    recommendations = []
    afp_thresholds = thresholds.get(f"afp_total_{formulation_type}")
    if afp_thresholds:
        afp_threshold = afp_thresholds[0]
        if current_afp < afp_threshold["acceptable_min"]:
            recommendations.append(
                "Increase AFP by adding dextrose, fructose, or invert sugar for better freeze-thaw stability."
            )
        elif current_afp > afp_threshold["acceptable_max"]:
            recommendations.append(
                "Reduce AFP by replacing some sugars with sucrose or glucose syrups (DE 21-38) for firmer texture."
            )
    pod_thresholds = thresholds.get(f"pod_sweetness_{formulation_type}")
    if pod_thresholds:
        pod_threshold = pod_thresholds[0]
        pod_current = current_sp * 100
        if pod_current < pod_threshold["acceptable_min"]:
            recommendations.append(
                "Increase sweetness by adding fructose or enhancing with honey for better taste balance."
            )
        elif pod_current > pod_threshold["acceptable_max"]:
            recommendations.append(
                "Reduce sweetness by replacing some sucrose with lower SP sugars like lactose or glucose syrup."
            )
    return recommendations


def calculate_texture_prediction(
    sugar_composition: dict[str, float],
    gelato_constants: Mapping[str, ExtendedGelatoScienceConstants],
) -> tuple[float, str, str]:
    """Calculates comprehensive texture prediction using extended DE analysis.

    Args:
        sugar_composition: Dictionary of sugar types to masses in grams.
        gelato_constants: Extended gelato science constants.

    Returns:
        Tuple of (weighted_de, texture_prediction, detailed_analysis).
    """
    total_sugar_mass = sum(sugar_composition.values())
    if total_sugar_mass == 0:
        return (0.0, "UNKNOWN", "No sugars present for analysis.")
    weighted_de = 0.0
    texture_contributions = []
    for sugar_type, mass_g in sugar_composition.items():
        sugar_data = gelato_constants.get(sugar_type.lower())
        if sugar_data:
            de_value = sugar_data["de_value"]
            texture_impact = sugar_data["texture_impact"]
            contribution = mass_g / total_sugar_mass
            weighted_de += contribution * de_value
            if contribution > 0.1:
                texture_contributions.append(
                    f"{sugar_type.title()}: {contribution * 100:.1f}% ({texture_impact.lower()})"
                )
    if weighted_de < 20:
        texture = "VERY_COMPACT"
        description = "Very firm, chewy texture - may be too hard for some applications"
    elif weighted_de < 35:
        texture = "COMPACT"
        description = "Firm, structured texture - good for traditional sweets"
    elif weighted_de < 50:
        texture = "BALANCED"
        description = "Ideal texture balance - smooth yet structured"
    elif weighted_de < 65:
        texture = "SOFT"
        description = "Smooth, creamy texture - melts well"
    else:
        texture = "VERY_SOFT"
        description = "Very soft, may be difficult to hold shape"
    detailed_analysis = (
        f"{description}. Contributors: {'; '.join(texture_contributions)}"
    )
    return (weighted_de, texture, detailed_analysis)


def validate_scientific_framework_completeness() -> dict[str, bool]:
    """Validates that all required Gelato University scientific data is available.

    Returns:
        Dictionary indicating completeness of each scientific framework.
    """
    validation_results = {
        "extended_gelato_constants": False,
        "msnf_stabilizer_balance": False,
        "extended_validation_thresholds": False,
        "sugar_variety_coverage": False,
        "formulation_type_coverage": False,
    }
    if not supabase_client.supabase:
        return validation_results
    try:
        constants_response = (
            supabase_client.supabase.table("gelato_science_constants")
            .select("sugar_type")
            .execute()
        )
        if constants_response.data and len(constants_response.data) >= 10:
            validation_results["extended_gelato_constants"] = True
            validation_results["sugar_variety_coverage"] = True
        balance_response = (
            supabase_client.supabase.table("msnf_stabilizer_balance")
            .select("formulation_type")
            .execute()
        )
        if balance_response.data and len(balance_response.data) >= 4:
            validation_results["msnf_stabilizer_balance"] = True
            validation_results["formulation_type_coverage"] = True
        thresholds_response = (
            supabase_client.supabase.table("validation_thresholds_extended")
            .select("parameter_name")
            .execute()
        )
        if thresholds_response.data and len(thresholds_response.data) >= 15:
            validation_results["extended_validation_thresholds"] = True
    except Exception as e:
        logging.exception(f"Error validating scientific framework completeness: {e}")
    return validation_results


def calculate_characterization_pct(classified_ingredients: list[dict]) -> float:
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
    classified_ingredients: list[dict], composition: dict[str, float]
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