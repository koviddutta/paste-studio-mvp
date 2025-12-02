import reflex as rx
import logging
import re
from app.database.supabase_client import get_supabase


class GelatoUniversityClient:
    """
    Client for accessing scientific data and processing rules from the database.
    """

    @staticmethod
    def _parse_quantity(text: str) -> float:
        """
        Extracts quantity from ingredient string.
        Handles '1/2 teaspoon', '250 grams', '2.5 kg' etc.
        Defaults to 100.0 if no number found.
        """
        if not text:
            return 100.0
        fraction_match = re.search("(\\d+)\\s*/\\s*(\\d+)", text)
        if fraction_match:
            try:
                num = float(fraction_match.group(1))
                den = float(fraction_match.group(2))
                if den != 0:
                    return round(num / den, 2)
            except (ValueError, ZeroDivisionError) as e:
                logging.exception(f"Error parsing fraction: {e}")
        number_match = re.search("(\\d*\\.?\\d+)", text)
        if number_match:
            try:
                val = float(number_match.group(1))
                return val
            except ValueError as e:
                logging.exception(f"Error parsing number: {e}")
        return 100.0

    @staticmethod
    async def get_processing_rules(class_code: str) -> dict:
        supabase = get_supabase()
        try:
            response = (
                supabase.table("processing_rules")
                .select("*")
                .eq("class_code", class_code)
                .single()
                .execute()
            )
            return response.data
        except Exception:
            logging.exception("Error in get_processing_rules")
            return {
                "class_code": class_code,
                "min_temp": 25,
                "max_temp": 30,
                "process_action": "Mix gently",
                "equipment_needed": ["Bowl"],
            }

    @staticmethod
    async def search_recipes(query: str):
        supabase = get_supabase()
        try:
            response = (
                supabase.table("desserts_master_v2")
                .select("*")
                .ilike("RecipeName", f"%{query}%")
                .limit(10)
                .execute()
            )
            mapped_results = []
            if response.data:
                for item in response.data:
                    raw_ing_str = item.get("Ingredients", "")
                    ingredients_list = []
                    if raw_ing_str:
                        items = [i.strip() for i in raw_ing_str.split(",")]
                        for i in items:
                            if i:
                                qty = GelatoUniversityClient._parse_quantity(i)
                                ingredients_list.append({"name": i, "quantity": qty})
                    mapped_results.append(
                        {
                            "id": item.get("RecipeID"),
                            "name": item.get("RecipeName"),
                            "ingredients": ingredients_list,
                            "original_data": item,
                        }
                    )
            return mapped_results
        except Exception as e:
            logging.exception(f"Search error: {e}")
            return []

    @staticmethod
    async def get_recipe_by_id(recipe_id: str):
        supabase = get_supabase()
        try:
            response = (
                supabase.table("desserts_master_v2")
                .select("*")
                .eq("RecipeID", recipe_id)
                .single()
                .execute()
            )
            item = response.data
            if not item:
                return None
            raw_ing_str = item.get("Ingredients", "")
            ingredients_list = []
            if raw_ing_str:
                items = [i.strip() for i in raw_ing_str.split(",")]
                for i in items:
                    if i:
                        qty = GelatoUniversityClient._parse_quantity(i)
                        ingredients_list.append({"name": i, "quantity": qty})
            return {
                "id": item.get("RecipeID"),
                "name": item.get("RecipeName"),
                "ingredients": ingredients_list,
                "original_data": item,
            }
        except Exception:
            logging.exception("Error in get_recipe_by_id")
            return None