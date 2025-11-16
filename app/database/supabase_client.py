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
    """Fetches a recipe by its name with partial matching.

    Args:
        sweet_name: The name of the sweet to search for.

    Returns:
        The first matching recipe dictionary, or None if not found or on error.
    """
    if not supabase:
        return None
    try:
        response = (
            supabase.table("recipes")
            .select("*")
            .ilike("name", f"%{sweet_name}%")
            .limit(1)
            .execute()
        )
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        logging.exception(f"Error fetching recipe '{sweet_name}': {e}")
        return None


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


def seed_initial_data():
    """Seeds the database with initial ingredients and constants. This is for demonstration.

    In a real application, this would be a migration script.
    """
    if not supabase:
        logging.error("Cannot seed data, Supabase client is not available.")
        return
    ingredients_to_seed = [
        {
            "name": "khoya",
            "class": "A_DAIRY",
            "aliases": ["mawa"],
            "moisture_pct": 30,
            "fat_pct": 25,
            "protein_pct": 18,
        },
        {
            "name": "milk",
            "class": "A_DAIRY",
            "moisture_pct": 87,
            "fat_pct": 4,
            "protein_pct": 3.5,
        },
        {
            "name": "paneer",
            "class": "A_DAIRY",
            "moisture_pct": 55,
            "fat_pct": 22,
            "protein_pct": 18,
        },
        {
            "name": "cream",
            "class": "A_DAIRY",
            "moisture_pct": 58,
            "fat_pct": 35,
            "protein_pct": 2,
        },
        {
            "name": "pistachio",
            "class": "B_NUT",
            "moisture_pct": 4,
            "fat_pct": 45,
            "protein_pct": 20,
        },
        {
            "name": "almond",
            "class": "B_NUT",
            "moisture_pct": 5,
            "fat_pct": 50,
            "protein_pct": 21,
        },
        {
            "name": "cashew",
            "class": "B_NUT",
            "moisture_pct": 5,
            "fat_pct": 44,
            "protein_pct": 18,
        },
        {
            "name": "walnut",
            "class": "B_NUT",
            "moisture_pct": 4,
            "fat_pct": 65,
            "protein_pct": 15,
        },
        {
            "name": "sucrose",
            "class": "C_SUGAR",
            "moisture_pct": 0,
            "fat_pct": 0,
            "protein_pct": 0,
        },
        {
            "name": "jaggery",
            "class": "C_SUGAR",
            "moisture_pct": 4,
            "fat_pct": 0,
            "protein_pct": 0.4,
        },
        {
            "name": "glucose",
            "class": "C_SUGAR",
            "moisture_pct": 0,
            "fat_pct": 0,
            "protein_pct": 0,
        },
        {
            "name": "ghee",
            "class": "D_FAT",
            "moisture_pct": 0,
            "fat_pct": 100,
            "protein_pct": 0,
        },
        {
            "name": "butter",
            "class": "D_FAT",
            "moisture_pct": 16,
            "fat_pct": 81,
            "protein_pct": 1,
        },
        {
            "name": "oil",
            "class": "D_FAT",
            "moisture_pct": 0,
            "fat_pct": 100,
            "protein_pct": 0,
        },
        {
            "name": "lbg",
            "class": "E_STABILIZER",
            "aliases": ["locust bean gum"],
            "moisture_pct": 0,
            "fat_pct": 0,
            "protein_pct": 0,
        },
        {
            "name": "guar",
            "class": "E_STABILIZER",
            "aliases": ["guar gum"],
            "moisture_pct": 0,
            "fat_pct": 0,
            "protein_pct": 0,
        },
        {
            "name": "xanthan",
            "class": "E_STABILIZER",
            "aliases": ["xanthan gum"],
            "moisture_pct": 0,
            "fat_pct": 0,
            "protein_pct": 0,
        },
        {
            "name": "cardamom",
            "class": "F_AROMATIC",
            "moisture_pct": 8,
            "fat_pct": 7,
            "protein_pct": 11,
        },
        {
            "name": "saffron",
            "class": "F_AROMATIC",
            "moisture_pct": 12,
            "fat_pct": 6,
            "protein_pct": 11,
        },
        {
            "name": "rose water",
            "class": "F_AROMATIC",
            "moisture_pct": 99,
            "fat_pct": 0,
            "protein_pct": 0,
        },
    ]
    try:
        supabase.table("ingredients_master").upsert(
            ingredients_to_seed, on_conflict="name"
        ).execute()
        logging.info("Successfully seeded ingredients data.")
    except Exception as e:
        logging.exception(f"Error seeding ingredients data: {e}")