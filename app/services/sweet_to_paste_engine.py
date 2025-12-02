from app.engines.ingredient_classifier import IngredientClassifier
from app.engines.sop_generator import SOPGenerator
from app.calculators.property_calculator import PropertyCalculator


class SweetToPasteEngine:
    """
    Main orchestrator for converting a sweet recipe to a paste formulation.
    """

    @staticmethod
    async def process_recipe(recipe: dict, batch_size_kg: float = 1.0):
        """
        Full pipeline: Recipe -> Classification -> Calculation -> SOP.
        """
        raw_ingredients = recipe.get("ingredients", [])
        if isinstance(raw_ingredients, str):
            import json
            import logging

            try:
                raw_ingredients = json.loads(raw_ingredients)
            except:
                logging.exception("Error parsing ingredients JSON")
                raw_ingredients = []
        classified_ingredients = await IngredientClassifier.classify_recipe_ingredients(
            raw_ingredients
        )
        total_weight = 0
        total_moisture = 0
        total_fat = 0
        total_sugar = 0
        total_protein = 0
        input_total = sum(
            (float(ing.get("quantity", 0)) for ing in classified_ingredients)
        )
        scale_factor = batch_size_kg * 1000 / input_total if input_total > 0 else 1
        processed_batch = []
        for ing in classified_ingredients:
            qty = float(ing.get("quantity", 0)) * scale_factor
            m_moisture = qty * (ing["moisture"] / 100)
            m_fat = qty * (ing["fat"] / 100)
            m_sugar = qty * (ing["sugar"] / 100)
            m_protein = qty * (ing["protein"] / 100)
            total_weight += qty
            total_moisture += m_moisture
            total_fat += m_fat
            total_sugar += m_sugar
            total_protein += m_protein
            processed_batch.append({**ing, "batch_weight_g": round(qty, 1)})
        final_composition = {
            "moisture": round(total_moisture / total_weight * 100, 2)
            if total_weight
            else 0,
            "fat": round(total_fat / total_weight * 100, 2) if total_weight else 0,
            "sugar": round(total_sugar / total_weight * 100, 2) if total_weight else 0,
            "protein": round(total_protein / total_weight * 100, 2)
            if total_weight
            else 0,
        }
        properties = PropertyCalculator.calculate_all_properties(final_composition)
        sop_steps = await SOPGenerator.generate_sop(processed_batch)
        return {
            "recipe_name": recipe.get("name"),
            "batch_size_kg": batch_size_kg,
            "ingredients": processed_batch,
            "composition": final_composition,
            "properties": properties,
            "sop": sop_steps,
        }