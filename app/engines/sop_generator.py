import logging
from typing import TypedDict, Optional, Any
from app.database import supabase_client
from app.engines.ingredient_classifier import IngredientData


class SOPStep(TypedDict):
    """Represents a single step in the Standard Operating Procedure."""

    step: int
    title: str
    action: str
    temperature_c: Optional[int]
    time_minutes: Optional[int]
    equipment: Optional[str]
    science_reason: Optional[str]


def generate_sop(
    classified_ingredients: list[IngredientData],
) -> tuple[list[SOPStep], list[str]]:
    """Generates a detailed Standard Operating Procedure (SOP) based on ingredient classes.

    This function orchestrates the SOP generation by fetching processing rules for each
    ingredient class present in the recipe, sequencing them logically, and adding critical
    safety checks like pasteurization.

    Args:
        classified_ingredients: A list of classified ingredient data dictionaries.

    Returns:
        A tuple containing the list of SOP steps and a list of validation warnings.
    """
    warnings = []
    if not classified_ingredients:
        return ([], ["Cannot generate SOP: No ingredients provided."])
    ingredient_classes = sorted(
        list(
            {
                ing["class_name"]
                for ing in classified_ingredients
                if ing.get("class_name")
            }
        )
    )
    all_rules: dict[str, dict[str, str | int | float | None]] = {}
    for iclass in ingredient_classes:
        rules = supabase_client.fetch_processing_rules(iclass)
        if not rules:
            warnings.append(
                f"No processing rules found for ingredient class '{iclass}'."
            )
        for rule in rules:
            rule_key = f"{rule['ingredient_class']}_{rule['step_order']}"
            all_rules[rule_key] = rule
    sorted_rule_keys = sorted(all_rules.keys())
    sop: list[SOPStep] = []
    step_counter = 1
    for key in sorted_rule_keys:
        rule = all_rules[key]
        sop_step: SOPStep = {
            "step": step_counter,
            "title": f"Process: {rule['ingredient_class'].split('_')[-1]}",
            "action": rule.get("action", "N/A"),
            "temperature_c": rule.get("temperature_c"),
            "time_minutes": rule.get("time_minutes"),
            "equipment": rule.get("equipment"),
            "science_reason": rule.get("science_reason"),
        }
        sop.append(sop_step)
        step_counter += 1
    if "A_DAIRY" in ingredient_classes:
        pasteurization_found = any(
            (
                step["action"]
                and "pasteurize" in step["action"].lower()
                and (step.get("temperature_c", 0) >= 72)
                for step in sop
            )
        )
        if not pasteurization_found:
            warnings.append(
                "Safety Warning: Dairy is present but no pasteurization step (>=72\\[DEG]C) was found."
            )
    logging.info(f"Generated SOP with {len(sop)} steps and {len(warnings)} warnings.")
    return (sop, warnings)