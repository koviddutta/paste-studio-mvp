import reflex as rx
from typing import TypedDict, Any, Optional
import asyncio
import logging
from app.database import supabase_client
from app.engines.ingredient_classifier import classify_ingredient, IngredientData
from app.engines.sop_generator import generate_sop, SOPStep
from app.calculators.property_calculator import (
    calculate_all_properties,
    FormulationProperties,
)
from app.validators.formulation_validator import (
    validate_formulation,
    FullValidationReport,
)


class RecipeIngredient(TypedDict):
    name: str
    mass_g: float
    classified_data: Optional[IngredientData]


class FormulationResult(TypedDict):
    sweet_name: str
    batch_size_kg: float
    ingredients: list[RecipeIngredient]
    properties: Optional[FormulationProperties]
    sop: list[SOPStep]
    validation: Optional[FullValidationReport]
    warnings: list[str]


class FormulationState(rx.State):
    """Manages the state for recipe searching and formulation generation."""

    search_query: str = ""
    search_results: list[dict[str, str]] = []
    is_searching: bool = False
    selected_recipe_name: str = ""
    batch_size_kg: float = 1.0
    is_generating: bool = False
    formulation_result: Optional[FormulationResult] = None
    error_message: str = ""

    def _reset_formulation(self):
        self.formulation_result = None
        self.error_message = ""

    @rx.event
    def on_search_query_change(self, query: str):
        """Handle search input changes with debounce."""
        self.search_query = query
        self.selected_recipe_name = ""
        if not query.strip():
            self.search_results = []
            self.is_searching = False
            return
        self.is_searching = True
        return FormulationState.search_recipes

    @rx.event(background=True)
    async def search_recipes(self):
        """Fetches recipe suggestions from the database."""
        async with self:
            if not self.search_query.strip():
                self.search_results = []
                self.is_searching = False
                return
        results = supabase_client.search_recipes(self.search_query, limit=5)
        async with self:
            if self.search_query.strip():
                self.search_results = results
            else:
                self.search_results = []
            self.is_searching = False

    @rx.event
    def select_recipe(self, recipe_name: str):
        """Select a recipe from the search results."""
        self.selected_recipe_name = recipe_name
        self.search_query = recipe_name
        self.search_results = []
        self.error_message = ""

    @rx.event(background=True)
    async def generate_formulation(self):
        """The main pipeline for generating a full formulation."""
        async with self:
            if not self.selected_recipe_name:
                self.error_message = "Please select a recipe first."
                return
            if self.batch_size_kg <= 0:
                self.error_message = "Batch size must be greater than zero."
                return
            self._reset_formulation()
            self.is_generating = True
        try:
            recipe_data = supabase_client.fetch_recipe(self.selected_recipe_name)
            if not recipe_data:
                async with self:
                    self.error_message = (
                        f"Recipe '{self.selected_recipe_name}' not found."
                    )
                    self.is_generating = False
                return
            ingredients_str = recipe_data.get("Ingredients", "")
            parsed_ings = [i.strip().split(":") for i in ingredients_str.split(",")]
            total_recipe_mass = sum(
                [
                    float(p[1])
                    for p in parsed_ings
                    if len(p) == 2 and p[1].strip().replace(".", "", 1).isdigit()
                ]
            )
            if total_recipe_mass == 0:
                async with self:
                    self.error_message = (
                        "Could not parse ingredients or masses are zero."
                    )
                    self.is_generating = False
                return
            classified_ingredients_with_mass = []
            all_ingredients: list[RecipeIngredient] = []
            formulation_warnings = []
            for p in parsed_ings:
                if len(p) != 2:
                    continue
                name, mass_str = (p[0].strip(), p[1].strip())
                try:
                    mass_g = float(mass_str) * (
                        self.batch_size_kg * 1000 / total_recipe_mass
                    )
                    classified_data = classify_ingredient(name)
                    all_ingredients.append(
                        {
                            "name": name.capitalize(),
                            "mass_g": round(mass_g, 2),
                            "classified_data": classified_data,
                        }
                    )
                    if classified_data:
                        classified_data["mass_g"] = mass_g
                        classified_ingredients_with_mass.append(classified_data)
                    else:
                        formulation_warnings.append(f"Unclassified ingredient: {name}")
                except (ValueError, TypeError) as e:
                    logging.exception(f"Error parsing mass for ingredient {name}: {e}")
                    formulation_warnings.append(
                        f"Could not parse mass for ingredient: {name}"
                    )
            properties = calculate_all_properties(
                classified_ingredients_with_mass, self.batch_size_kg * 1000
            )
            sop, sop_warnings = generate_sop(classified_ingredients_with_mass)
            validation = (
                validate_formulation(properties, classified_ingredients_with_mass)
                if properties
                else None
            )
            formulation_warnings.extend(sop_warnings)
            async with self:
                self.formulation_result = {
                    "sweet_name": self.selected_recipe_name,
                    "batch_size_kg": self.batch_size_kg,
                    "ingredients": all_ingredients,
                    "properties": properties,
                    "sop": sop,
                    "validation": validation,
                    "warnings": formulation_warnings,
                }
                self.is_generating = False
        except Exception as e:
            logging.exception(f"Error generating formulation: {e}")
            async with self:
                self.error_message = "An unexpected error occurred during formulation."
                self.is_generating = False