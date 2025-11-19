import logging
from typing import TypedDict, Any, Optional
from app.database import supabase_client


class MappedIngredient(TypedDict):
    """Represents a single ingredient with its mapped class."""

    name: str
    canonical_name: str
    quantity_grams: float
    class_name: str


class ClassifiedRecipe(TypedDict):
    """Represents a full recipe with all ingredients classified."""

    recipe_id: int
    recipe_name: str
    ingredients: list[MappedIngredient]
    total_mass_grams: float
    unclassified_count: int
    warnings: list[str]


def map_ingredient_to_class(ingredient_canonical_name: str) -> str:
    """Maps an ingredient to its class using the ingredient_mapping table.

    It first attempts an exact case-insensitive match, then a substring match.

    Args:
        ingredient_canonical_name: The canonical name of the ingredient.

    Returns:
        The ingredient's class (e.g., 'A_DAIRY') or 'UNKNOWN' if not found.
    """
    if not ingredient_canonical_name or not supabase_client.supabase:
        return "UNKNOWN"
    try:
        response = (
            supabase_client.supabase.table("ingredient_mapping")
            .select("our_class")
            .ilike("your_ingredient_name", ingredient_canonical_name)
            .limit(1)
            .execute()
        )
        if response.data:
            return response.data[0]["our_class"]
        response = (
            supabase_client.supabase.table("ingredient_mapping")
            .select("our_class")
            .ilike("your_ingredient_name", f"%{ingredient_canonical_name}%")
            .limit(1)
            .execute()
        )
        if response.data:
            return response.data[0]["our_class"]
        logging.warning(f"Could not map ingredient: {ingredient_canonical_name}")
        return "UNKNOWN"
    except Exception as e:
        logging.exception(
            f"Error mapping ingredient '{ingredient_canonical_name}': {e}"
        )
        return "UNKNOWN"


def get_recipe_with_classified_ingredients(
    recipe_name: str,
) -> Optional[ClassifiedRecipe]:
    """Fetches a recipe and classifies all its ingredients using the mapping table.

    Args:
        recipe_name: The name of the recipe to fetch.

    Returns:
        A ClassifiedRecipe dictionary with detailed ingredient data, or None on failure.
    """
    if not supabase_client.supabase:
        logging.error("Supabase client not available.")
        return None
    try:
        recipe_response = (
            supabase_client.supabase.table("desserts_master_v2")
            .select("RecipeID, RecipeName")
            .ilike("RecipeName", recipe_name)
            .limit(1)
            .execute()
        )
        if not recipe_response.data:
            logging.warning(f"Recipe '{recipe_name}' not found.")
            return None
        recipe_id = recipe_response.data[0]["RecipeID"]
        recipe_title = recipe_response.data[0]["RecipeName"]
        ingredients_response = (
            supabase_client.supabase.table("recipe_ingredients_v2")
            .select("IngredientNameCanonical, QuantityInGrams, IngredientNameOriginal")
            .eq("RecipeID", recipe_id)
            .execute()
        )
        if not ingredients_response.data:
            logging.warning(
                f"No ingredients found for recipe '{recipe_name}' (ID: {recipe_id})"
            )
            return {
                "recipe_id": recipe_id,
                "recipe_name": recipe_title,
                "ingredients": [],
                "total_mass_grams": 0.0,
                "unclassified_count": 0,
                "warnings": [f"No ingredients listed for recipe '{recipe_name}'."],
            }
        mapped_ingredients: list[MappedIngredient] = []
        total_mass = 0.0
        unclassified_count = 0
        warnings = []
        for ing in ingredients_response.data:
            canonical_name = ing.get("IngredientNameCanonical")
            if not canonical_name:
                warnings.append(f"Skipping ingredient with no canonical name: {ing}")
                continue
            class_name = map_ingredient_to_class(canonical_name)
            if class_name == "UNKNOWN":
                unclassified_count += 1
                warnings.append(f"Unclassified ingredient: {canonical_name}")
            quantity = float(ing.get("QuantityInGrams") or 0.0)
            total_mass += quantity
            mapped_ingredients.append(
                {
                    "name": ing.get("IngredientNameOriginal") or canonical_name,
                    "canonical_name": canonical_name,
                    "quantity_grams": quantity,
                    "class_name": class_name,
                }
            )
        return {
            "recipe_id": recipe_id,
            "recipe_name": recipe_title,
            "ingredients": mapped_ingredients,
            "total_mass_grams": total_mass,
            "unclassified_count": unclassified_count,
            "warnings": warnings,
        }
    except Exception as e:
        logging.exception(f"Failed to get and classify recipe '{recipe_name}': {e}")
        return None


def get_ingredient_class_distribution(recipe_name: str) -> dict[str, int]:
    """Calculates the distribution of ingredient classes for a given recipe.

    Args:
        recipe_name: The name of the recipe.

    Returns:
        A dictionary with counts for each ingredient class.
    """
    distribution = {
        "A_DAIRY": 0,
        "B_NUT": 0,
        "C_SUGAR": 0,
        "D_FAT": 0,
        "E_STABILIZER": 0,
        "F_AROMATIC": 0,
        "G_GRAIN": 0,
        "H_SEED": 0,
        "UNKNOWN": 0,
    }
    classified_recipe = get_recipe_with_classified_ingredients(recipe_name)
    if not classified_recipe or not classified_recipe.get("ingredients"):
        logging.warning(f"Could not get class distribution for '{recipe_name}'.")
        return distribution
    for ingredient in classified_recipe["ingredients"]:
        class_name = ingredient.get("class_name", "UNKNOWN")
        if class_name in distribution:
            distribution[class_name] += 1
        else:
            distribution["UNKNOWN"] += 1
    return distribution


import logging
from typing import TypedDict, Any, Optional
from app.database import supabase_client


class MappedIngredient(TypedDict):
    """Represents a single ingredient with its mapped class."""

    name: str
    canonical_name: str
    quantity_grams: float
    class_name: str


class ClassifiedRecipe(TypedDict):
    """Represents a full recipe with all ingredients classified."""

    recipe_id: int
    recipe_name: str
    ingredients: list[MappedIngredient]
    total_mass_grams: float
    unclassified_count: int
    warnings: list[str]


def map_ingredient_to_class(ingredient_canonical_name: str) -> str:
    """Maps an ingredient to its class using the ingredient_mapping table.

    It first attempts an exact case-insensitive match, then a substring match.

    Args:
        ingredient_canonical_name: The canonical name of the ingredient.

    Returns:
        The ingredient's class (e.g., 'A_DAIRY') or 'UNKNOWN' if not found.
    """
    if not ingredient_canonical_name or not supabase_client.supabase:
        return "UNKNOWN"
    try:
        response = (
            supabase_client.supabase.table("ingredient_mapping")
            .select("our_class")
            .ilike("your_ingredient_name", ingredient_canonical_name)
            .limit(1)
            .execute()
        )
        if response.data:
            return response.data[0]["our_class"]
        response = (
            supabase_client.supabase.table("ingredient_mapping")
            .select("our_class")
            .ilike("your_ingredient_name", f"%{ingredient_canonical_name}%")
            .limit(1)
            .execute()
        )
        if response.data:
            return response.data[0]["our_class"]
        logging.warning(f"Could not map ingredient: {ingredient_canonical_name}")
        return "UNKNOWN"
    except Exception as e:
        logging.exception(
            f"Error mapping ingredient '{ingredient_canonical_name}': {e}"
        )
        return "UNKNOWN"


def get_recipe_with_classified_ingredients(
    recipe_name: str,
) -> Optional[ClassifiedRecipe]:
    """Fetches a recipe and classifies all its ingredients using the mapping table.

    Args:
        recipe_name: The name of the recipe to fetch.

    Returns:
        A ClassifiedRecipe dictionary with detailed ingredient data, or None on failure.
    """
    if not supabase_client.supabase:
        logging.error("Supabase client not available.")
        return None
    try:
        recipe_response = (
            supabase_client.supabase.table("desserts_master_v2")
            .select("RecipeID, RecipeName")
            .ilike("RecipeName", recipe_name)
            .limit(1)
            .execute()
        )
        if not recipe_response.data:
            logging.warning(f"Recipe '{recipe_name}' not found.")
            return None
        recipe_id = recipe_response.data[0]["RecipeID"]
        recipe_title = recipe_response.data[0]["RecipeName"]
        ingredients_response = (
            supabase_client.supabase.table("recipe_ingredients_v2")
            .select("IngredientNameCanonical, QuantityInGrams, IngredientNameOriginal")
            .eq("RecipeID", recipe_id)
            .execute()
        )
        if not ingredients_response.data:
            logging.warning(
                f"No ingredients found for recipe '{recipe_name}' (ID: {recipe_id})"
            )
            return {
                "recipe_id": recipe_id,
                "recipe_name": recipe_title,
                "ingredients": [],
                "total_mass_grams": 0.0,
                "unclassified_count": 0,
                "warnings": [f"No ingredients listed for recipe '{recipe_name}'."],
            }
        mapped_ingredients: list[MappedIngredient] = []
        total_mass = 0.0
        unclassified_count = 0
        warnings = []
        for ing in ingredients_response.data:
            canonical_name = ing.get("IngredientNameCanonical")
            if not canonical_name:
                warnings.append(f"Skipping ingredient with no canonical name: {ing}")
                continue
            class_name = map_ingredient_to_class(canonical_name)
            if class_name == "UNKNOWN":
                unclassified_count += 1
                warnings.append(f"Unclassified ingredient: {canonical_name}")
            quantity = float(ing.get("QuantityInGrams") or 0.0)
            total_mass += quantity
            mapped_ingredients.append(
                {
                    "name": ing.get("IngredientNameOriginal") or canonical_name,
                    "canonical_name": canonical_name,
                    "quantity_grams": quantity,
                    "class_name": class_name,
                }
            )
        return {
            "recipe_id": recipe_id,
            "recipe_name": recipe_title,
            "ingredients": mapped_ingredients,
            "total_mass_grams": total_mass,
            "unclassified_count": unclassified_count,
            "warnings": warnings,
        }
    except Exception as e:
        logging.exception(f"Failed to get and classify recipe '{recipe_name}': {e}")
        return None


def get_ingredient_class_distribution(recipe_name: str) -> dict[str, int]:
    """Calculates the distribution of ingredient classes for a given recipe.

    Args:
        recipe_name: The name of the recipe.

    Returns:
        A dictionary with counts for each ingredient class.
    """
    distribution = {
        "A_DAIRY": 0,
        "B_NUT": 0,
        "C_SUGAR": 0,
        "D_FAT": 0,
        "E_STABILIZER": 0,
        "F_AROMATIC": 0,
        "G_GRAIN": 0,
        "H_SEED": 0,
        "UNKNOWN": 0,
    }
    classified_recipe = get_recipe_with_classified_ingredients(recipe_name)
    if not classified_recipe or not classified_recipe.get("ingredients"):
        logging.warning(f"Could not get class distribution for '{recipe_name}'.")
        return distribution
    for ingredient in classified_recipe["ingredients"]:
        class_name = ingredient.get("class_name", "UNKNOWN")
        if class_name in distribution:
            distribution[class_name] += 1
        else:
            distribution["UNKNOWN"] += 1
    return distribution