import logging
from typing import Optional, TypedDict
from app.database import supabase_client


class IngredientData(TypedDict):
    """Represents the structured data for a single ingredient."""

    id: int
    name: str
    class_name: str
    aliases: list[str]
    moisture_pct: Optional[float]
    fat_pct: Optional[float]
    protein_pct: Optional[float]
    sugar_pct: Optional[float]
    processing_temp_c: Optional[int]
    processing_time_min: Optional[int]
    equipment_type: Optional[str]


def classify_ingredient(ingredient_name: str) -> Optional[IngredientData]:
    """Fetches and classifies an ingredient from the database by name or alias.

    Args:
        ingredient_name: The name or alias of the ingredient to classify.

    Returns:
        A dictionary containing the ingredient's properties and classification,
        or None if the ingredient is not found.
    """
    if not ingredient_name:
        return None
    normalized_name = ingredient_name.lower().strip()
    try:
        ingredient_db = supabase_client.fetch_ingredient(normalized_name)
        if not ingredient_db:
            logging.warning(
                f"Ingredient '{normalized_name}' not found. This may need to be added to ingredients_master."
            )
            return None
        ingredient_data: IngredientData = {
            "id": ingredient_db.get("id"),
            "name": ingredient_db.get("name"),
            "class_name": ingredient_db.get("class"),
            "aliases": ingredient_db.get("aliases", []),
            "moisture_pct": ingredient_db.get("moisture_pct"),
            "fat_pct": ingredient_db.get("fat_pct"),
            "protein_pct": ingredient_db.get("protein_pct"),
            "sugar_pct": ingredient_db.get("sugar_pct"),
            "processing_temp_c": ingredient_db.get("processing_temp_c"),
            "processing_time_min": ingredient_db.get("processing_time_min"),
            "equipment_type": ingredient_db.get("equipment_type"),
        }
        return ingredient_data
    except Exception as e:
        logging.exception(
            f"An error occurred while classifying ingredient '{normalized_name}': {e}"
        )
        return None


def validate_ingredient_data(ingredient_data: IngredientData) -> list[str]:
    """Validates that essential properties of an ingredient are present.

    Args:
        ingredient_data: The ingredient's data dictionary.

    Returns:
        A list of validation error messages. An empty list means the data is valid.
    """
    errors = []
    if not ingredient_data:
        return ["Ingredient data is missing."]
    if not ingredient_data.get("class_name"):
        errors.append(
            f"Ingredient '{ingredient_data.get('name')}' has no assigned class."
        )
    if ingredient_data.get("moisture_pct") is None:
        errors.append(
            f"Ingredient '{ingredient_data.get('name')}' is missing moisture percentage."
        )
    if ingredient_data.get("fat_pct") is None:
        errors.append(
            f"Ingredient '{ingredient_data.get('name')}' is missing fat percentage."
        )
    return errors
