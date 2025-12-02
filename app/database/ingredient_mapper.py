import reflex as rx
import logging
from app.constants.ingredient_constants import IngredientCategory, IngredientSubCategory
from app.database.supabase_client import get_supabase


class IngredientMapper:
    """
    Maps raw recipe ingredient names to standardized database entries
    and determines their processing class.
    """

    COMMON_INGREDIENTS = {
        "milk powder": {
            "moisture": 3.0,
            "fat": 25.0,
            "protein": 25.0,
            "sugar": 38.0,
            "class": "A_DAIRY",
            "category": IngredientCategory.DAIRY,
        },
        "maida": {
            "moisture": 12.0,
            "fat": 1.0,
            "protein": 10.0,
            "sugar": 1.0,
            "class": "E_STABILIZER",
            "category": IngredientCategory.FLOUR_GRAIN,
        },
        "flour": {
            "moisture": 12.0,
            "fat": 1.0,
            "protein": 10.0,
            "sugar": 1.0,
            "class": "E_STABILIZER",
            "category": IngredientCategory.FLOUR_GRAIN,
        },
        "cardamom": {
            "moisture": 10.0,
            "fat": 5.0,
            "protein": 8.0,
            "sugar": 5.0,
            "class": "F_FLAVORING",
            "category": IngredientCategory.SPICE_FLAVOR,
        },
        "baking soda": {
            "moisture": 0.0,
            "fat": 0.0,
            "protein": 0.0,
            "sugar": 0.0,
            "class": "E_STABILIZER",
            "category": IngredientCategory.ADDITIVE,
        },
        "rose water": {
            "moisture": 95.0,
            "fat": 0.0,
            "protein": 0.0,
            "sugar": 0.0,
            "class": "F_FLAVORING",
            "category": IngredientCategory.LIQUID,
        },
        "saffron": {
            "moisture": 12.0,
            "fat": 6.0,
            "protein": 11.0,
            "sugar": 10.0,
            "class": "F_FLAVORING",
            "category": IngredientCategory.SPICE_FLAVOR,
        },
        "water": {
            "moisture": 100.0,
            "fat": 0.0,
            "protein": 0.0,
            "sugar": 0.0,
            "class": "A_DAIRY",
            "category": IngredientCategory.LIQUID,
        },
    }

    @staticmethod
    async def map_ingredient(name: str) -> dict:
        """
        Finds the best match for an ingredient in the master database.
        Maps DB columns (moisture_pct) to App keys (default_moisture_percent).
        """
        supabase = get_supabase()
        try:
            response = (
                supabase.table("ingredients_master")
                .select("*")
                .ilike("name", f"%{name}%")
                .limit(1)
                .execute()
            )
        except Exception as e:
            logging.exception(f"Error querying ingredient database: {e}")
            response = None
        if response and response.data:
            data = response.data[0]
            return {
                "name": data.get("name", name),
                "category": data.get("category", IngredientCategory.OTHER),
                "processing_class": data.get("class", "F"),
                "default_moisture_percent": float(data.get("moisture_pct", 0) or 0),
                "default_fat_percent": float(data.get("fat_pct", 0) or 0),
                "default_sugar_percent": float(data.get("sugar_pct", 0) or 0),
                "default_protein_percent": float(data.get("protein_pct", 0) or 0),
            }
        name_lower = name.lower()
        for key, val in IngredientMapper.COMMON_INGREDIENTS.items():
            if key in name_lower:
                return {
                    "name": name,
                    "category": val["category"],
                    "processing_class": val["class"],
                    "default_moisture_percent": val["moisture"],
                    "default_fat_percent": val["fat"],
                    "default_sugar_percent": val["sugar"],
                    "default_protein_percent": val["protein"],
                }
        return {
            "name": name,
            "category": IngredientCategory.OTHER,
            "processing_class": "F",
            "default_moisture_percent": 10.0,
            "default_fat_percent": 0.0,
            "default_sugar_percent": 0.0,
            "default_protein_percent": 0.0,
        }

    @staticmethod
    def get_processing_class(ingredient_data: dict) -> str:
        return ingredient_data.get("processing_class", "F")