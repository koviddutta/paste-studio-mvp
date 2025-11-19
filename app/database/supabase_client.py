import os
import logging
from typing import Any, Optional, Mapping, TypedDict
from supabase import create_client, Client
from postgrest.exceptions import APIError


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
    """Fetches a recipe by its name from the 'desserts_master_v2' table.

    It first tries an exact match, then a match starting with the name, and
    finally a partial match anywhere in the name.

    Args:
        sweet_name: The name of the sweet to search for.

    Returns:
        The first matching recipe dictionary, or None if not found or on error.
    """
    if not supabase:
        return None
    queries = [
        supabase.table("desserts_master_v2").select("*").eq("RecipeName", sweet_name),
        supabase.table("desserts_master_v2")
        .select("*")
        .ilike("RecipeName", f"{sweet_name}%"),
        supabase.table("desserts_master_v2")
        .select("*")
        .ilike("RecipeName", f"%{sweet_name}%"),
    ]
    for query in queries:
        try:
            response = query.limit(1).execute()
            if response.data:
                logging.info(f"Successfully fetched recipe '{sweet_name}'.")
                return response.data[0]
        except Exception as e:
            logging.exception(f"Error fetching recipe '{sweet_name}': {e}")
            return None
    logging.warning(f"Recipe '{sweet_name}' not found after multiple attempts.")
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


class GelatoScienceConstants(TypedDict):
    sugar_type: str
    afp_value: float
    sp_value: float
    de_value: float


def fetch_gelato_science_constants() -> Mapping[str, GelatoScienceConstants]:
    """Fetches all gelato science constants (AFP, SP, DE) from the database."""
    if not supabase:
        return {}
    try:
        response = supabase.table("gelato_science_constants").select("*").execute()
        if response.data:
            return {item["sugar_type"].lower(): item for item in response.data}
        return {}
    except Exception as e:
        logging.exception(f"Error fetching gelato science constants: {e}")
        return {}


class ValidationThresholds(TypedDict):
    optimal_min: float
    optimal_max: float
    acceptable_min: float
    acceptable_max: float
    explanation: str


def fetch_validation_thresholds() -> Mapping[str, ValidationThresholds]:
    """Fetches all scientific validation thresholds from the database."""
    if not supabase:
        return {}
    try:
        response = supabase.table("validation_thresholds").select("*").execute()
        if response.data:
            return {item["parameter_name"]: item for item in response.data}
        return {}
    except Exception as e:
        logging.exception(f"Error fetching validation thresholds: {e}")
        return {}


class MsnfStabilizerBalance(TypedDict):
    formulation_type: str
    msnf_min_pct: float
    msnf_max_pct: float
    stabilizer_min_pct: float
    stabilizer_max_pct: float
    explanation: str


def fetch_msnf_stabilizer_thresholds() -> Mapping[str, MsnfStabilizerBalance]:
    """Fetches all MSNF and Stabilizer balance thresholds from the database."""
    if not supabase:
        return {}
    try:
        response = supabase.table("msnf_stabilizer_balance").select("*").execute()
        if response.data:
            return {item["formulation_type"]: item for item in response.data}
        return {}
    except Exception as e:
        logging.exception(f"Error fetching msnf_stabilizer_balance thresholds: {e}")
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
        "gelato_science_constants": False,
        "validation_thresholds": False,
        "msnf_stabilizer_balance": False,
    }
    tables_to_check = {
        "ingredients_master": "id",
        "processing_rules": "id",
        "formulation_constants": "constant_name",
        "desserts_master_v2": "RecipeName",
        "gelato_science_constants": "sugar_type",
        "validation_thresholds": "parameter_name",
        "msnf_stabilizer_balance": "formulation_type",
    }
    for table_name, column in tables_to_check.items():
        try:
            response = supabase.table(table_name).select(column).limit(1).execute()
            validation_results[table_name] = len(response.data) > 0
        except APIError as e:
            if e.code != "PGRST205":
                logging.exception(
                    f"{table_name} table check failed with unexpected API error: {e}"
                )
        except Exception as e:
            logging.exception(
                f"{table_name} table check failed with general error: {e}"
            )
    return validation_results