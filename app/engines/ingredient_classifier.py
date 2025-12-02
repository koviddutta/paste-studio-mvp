from app.database.ingredient_mapper import IngredientMapper
from app.constants.ingredient_constants import IngredientCategory


class IngredientClassifier:
    """
    Classifies ingredients into processing categories (A-F).
    """

    @staticmethod
    async def classify_recipe_ingredients(recipe_ingredients: list[dict]) -> list[dict]:
        """
        Enriches ingredient list with processing class and nutritional data.
        """
        classified_ingredients = []
        for ing in recipe_ingredients:
            master_data = await IngredientMapper.map_ingredient(ing["name"])
            processed_ing = {
                **ing,
                "category": master_data.get("category"),
                "processing_class": master_data.get("processing_class", "F"),
                "moisture": float(master_data.get("default_moisture_percent", 0)),
                "fat": float(master_data.get("default_fat_percent", 0)),
                "sugar": float(master_data.get("default_sugar_percent", 0)),
                "protein": float(master_data.get("default_protein_percent", 0)),
            }
            classified_ingredients.append(processed_ing)
        return classified_ingredients