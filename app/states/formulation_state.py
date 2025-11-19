import reflex as rx
from typing import TypedDict, Any, Optional
import asyncio
import logging
from app.database import supabase_client
from app.database.ingredient_mapper import (
    get_recipe_with_classified_ingredients,
    get_ingredient_class_distribution,
)
from app.engines.ingredient_classifier import classify_ingredient, IngredientData
from app.engines.sop_generator import generate_sop, SOPStep
from app.calculators.property_calculator import (
    calculate_all_properties,
    FormulationProperties,
)
from app.validators.scientific_validator import (
    validate_formulation_scientifically,
    ScientificValidationReport,
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
    validation: Optional[ScientificValidationReport]
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
    completed_sop_steps: list[int] = []
    ingredient_distribution: dict[str, int] = {
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

    @rx.event
    def toggle_sop_step(self, step_number: int):
        """Toggles the completion status of an SOP step."""
        if step_number in self.completed_sop_steps:
            self.completed_sop_steps.remove(step_number)
        else:
            self.completed_sop_steps.append(step_number)

    def _reset_formulation(self):
        self.formulation_result = None
        self.error_message = ""
        self.completed_sop_steps = []

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
            db_validation = supabase_client.validate_database_setup()
            if not all(db_validation.values()):
                missing_tables = [k for k, v in db_validation.items() if not v]
                async with self:
                    self.error_message = f"Database setup is incomplete. Missing: {', '.join(missing_tables)}. Please run the setup script."
                    self.is_generating = False
                return
            logging.info(
                f"Fetching classified ingredients for '{self.selected_recipe_name}'"
            )
            classified_recipe = get_recipe_with_classified_ingredients(
                self.selected_recipe_name
            )
            async with self:
                self.ingredient_distribution = get_ingredient_class_distribution(
                    self.selected_recipe_name
                )
                logging.info(
                    f"Ingredient class distribution: {self.ingredient_distribution}"
                )
            if not classified_recipe:
                async with self:
                    self.error_message = f"Could not find or process recipe '{self.selected_recipe_name}'."
                    self.is_generating = False
                return
            classified_ingredients_with_mass = []
            all_ingredients: list[RecipeIngredient] = []
            formulation_warnings = classified_recipe.get("warnings", [])
            if classified_recipe.get("total_mass_grams", 0) > 0:
                logging.info(
                    "Using pre-classified ingredients with defined quantities."
                )
                recipe_total_mass = classified_recipe["total_mass_grams"]
                scaling_factor = self.batch_size_kg * 1000 / recipe_total_mass
                for ing in classified_recipe["ingredients"]:
                    scaled_mass_g = ing["quantity_grams"] * scaling_factor
                    classified_data = classify_ingredient(ing["canonical_name"])
                    all_ingredients.append(
                        {
                            "name": (ing["name"] or ing["canonical_name"]).capitalize(),
                            "mass_g": round(scaled_mass_g, 2),
                            "classified_data": classified_data,
                        }
                    )
                    if classified_data:
                        classified_data["mass_g"] = scaled_mass_g
                        classified_ingredients_with_mass.append(classified_data)
            else:
                logging.warning(
                    "No pre-defined quantities. Falling back to estimation."
                )
                formulation_warnings.append(
                    "Warning: Ingredient masses are estimated with equal weight distribution due to missing recipe data."
                )
                async with self:
                    self.error_message = "Recipe data is incomplete. Could not determine ingredient quantities."
                    self.is_generating = False
                return
            if not classified_ingredients_with_mass:
                async with self:
                    self.error_message = "Could not classify any ingredients for the formulation. Check ingredient_master table."
                    self.is_generating = False
                return
            properties = calculate_all_properties(
                classified_ingredients_with_mass, self.batch_size_kg * 1000
            )
            sop, sop_warnings = generate_sop(classified_ingredients_with_mass)
            gelato_constants = supabase_client.fetch_gelato_science_constants()
            thresholds = supabase_client.fetch_validation_thresholds()
            validation = (
                validate_formulation_scientifically(
                    properties,
                    classified_ingredients_with_mass,
                    sop,
                    thresholds,
                    gelato_constants,
                )
                if properties and thresholds and gelato_constants
                else None
            )
            if not thresholds or not gelato_constants:
                formulation_warnings.append(
                    "Could not fetch scientific validation constants from database."
                )
            formulation_warnings.extend(sop_warnings)
            if validation and validation.get("recommendations"):
                formulation_warnings.extend(validation["recommendations"])
            async with self:
                self.formulation_result = {
                    "sweet_name": self.selected_recipe_name,
                    "batch_size_kg": self.batch_size_kg,
                    "ingredients": all_ingredients,
                    "properties": properties,
                    "sop": sop,
                    "validation": validation,
                    "warnings": list(set(formulation_warnings)),
                }
                self.is_generating = False
        except Exception as e:
            logging.exception(f"Error generating formulation: {e}")
            async with self:
                self.error_message = "An unexpected error occurred during formulation."
                self.is_generating = False