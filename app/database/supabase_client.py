import os
import logging
from typing import Any, Optional
from supabase import create_client, Client


def get_supabase_client() -> Optional[Client]:
    """Initializes and returns a Supabase client if credentials are available.

    Returns:
        An initialized Supabase client or None if credentials are not found.
    """
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY")
    if not supabase_url or not supabase_key:
        logging.error("Supabase URL or Key not found in environment variables.")
        return None
    try:
        return create_client(supabase_url, supabase_key)
    except Exception as e:
        logging.exception(f"Error initializing Supabase client: {e}")
        return None


supabase = get_supabase_client()


def fetch_recipe(
    sweet_name: str,
) -> Optional[dict[str, str | int | float | None | list[str]]]:
    """Fetches a recipe by its name with partial matching from the 'desserts_master_v2' table.

    Args:
        sweet_name: The name of the sweet to search for.

    Returns:
        The first matching recipe dictionary, or None if not found or on error.
    """
    if not supabase:
        return None
    try:
        response = (
            supabase.table("desserts_master_v2")
            .select("*")
            .ilike("RecipeName", f"%{sweet_name}%")
            .limit(1)
            .execute()
        )
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        logging.exception(f"Error fetching recipe '{sweet_name}': {e}")
        return None


def search_recipes(query: str, limit: int = 10) -> list[dict[str, str]]:
    """Searches for recipes with autocomplete functionality.

    Args:
        query: The search query for recipe names.
        limit: Maximum number of results to return.

    Returns:
        A list of matching recipes with id and name fields.
    """
    if not supabase or not query:
        return []
    try:
        response = (
            supabase.table("desserts_master_v2")
            .select("RecipeName")
            .ilike("RecipeName", f"%{query}%")
            .limit(limit)
            .execute()
        )
        return [{"name": recipe["RecipeName"]} for recipe in response.data]
    except Exception as e:
        logging.exception(f"Error searching recipes for query '{query}': {e}")
        return []


def fetch_ingredient(
    name: str,
) -> Optional[dict[str, str | int | float | None | list[str]]]:
    """Fetches an ingredient by its name or alias.

    Args:
        name: The name or alias of the ingredient.

    Returns:
        The ingredient's data as a dictionary, or None if not found or on error.
    """
    if not supabase:
        return None
    try:
        response = (
            supabase.table("ingredients_master")
            .select("*")
            .eq("name", name)
            .limit(1)
            .execute()
        )
        if response.data:
            return response.data[0]
        response = (
            supabase.table("ingredients_master")
            .select("*")
            .contains("aliases", [name])
            .limit(1)
            .execute()
        )
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        logging.exception(f"Error fetching ingredient '{name}': {e}")
        return None


def fetch_processing_rules(
    ingredient_class: str,
) -> list[dict[str, str | int | float | None]]:
    """Fetches all processing rules for a given ingredient class, ordered by step.

    Args:
        ingredient_class: The class of the ingredient (e.g., 'A_DAIRY').

    Returns:
        A list of processing rule dictionaries, or an empty list if none are found or on error.
    """
    if not supabase:
        return []
    try:
        response = (
            supabase.table("processing_rules")
            .select("*")
            .eq("ingredient_class", ingredient_class)
            .order("step_order")
            .execute()
        )
        return response.data or []
    except Exception as e:
        logging.exception(
            f"Error fetching processing rules for class '{ingredient_class}': {e}"
        )
        return []


def fetch_constants() -> dict[str, float]:
    """Fetches all formulation constants from the database.

    Returns:
        A dictionary of constant names to their float values, or an empty dict on error.
    """
    if not supabase:
        return {}
    try:
        response = (
            supabase.table("formulation_constants")
            .select("constant_name, value")
            .execute()
        )
        if response.data:
            return {item["constant_name"]: item["value"] for item in response.data}
        return {}
    except Exception as e:
        logging.exception(f"Error fetching formulation constants: {e}")
        return {}


def validate_database_setup() -> dict[str, bool]:
    """Validates that all required tables exist and have data.

    Returns:
        A dictionary indicating which components are properly set up.
    """
    if not supabase:
        return {
            "connection": False,
            "ingredients_master": False,
            "processing_rules": False,
            "formulation_constants": False,
            "desserts_master_v2": False,
        }
    validation_results = {
        "connection": True,
        "ingredients_master": False,
        "processing_rules": False,
        "formulation_constants": False,
        "desserts_master_v2": False,
    }
    try:
        response = supabase.table("ingredients_master").select("id").limit(1).execute()
        validation_results["ingredients_master"] = len(response.data) > 0
    except Exception as e:
        logging.exception(f"ingredients_master table check failed: {e}")
    try:
        response = supabase.table("processing_rules").select("id").limit(1).execute()
        validation_results["processing_rules"] = len(response.data) > 0
    except Exception as e:
        logging.exception(f"processing_rules table check failed: {e}")
    try:
        response = (
            supabase.table("formulation_constants")
            .select("constant_name")
            .limit(1)
            .execute()
        )
        validation_results["formulation_constants"] = len(response.data) > 0
    except Exception as e:
        logging.exception(f"formulation_constants table check failed: {e}")
    try:
        response = (
            supabase.table("desserts_master_v2").select("RecipeName").limit(1).execute()
        )
        validation_results["desserts_master_v2"] = len(response.data) > 0
    except Exception as e:
        logging.exception(f"desserts_master_v2 table check failed: {e}")
    return validation_results