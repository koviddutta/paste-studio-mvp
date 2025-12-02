import reflex as rx
import logging
from typing import TypedDict, Optional
from app.services.sweet_to_paste_engine import SweetToPasteEngine
from app.database.gelato_university_client import GelatoUniversityClient
from app.validators.formulation_validator import FormulationValidator


class Composition(TypedDict):
    moisture: float
    fat: float
    sugar: float
    protein: float


class Properties(TypedDict):
    water_activity: float
    shelf_life_weeks: int
    viscosity_pa_s: float
    dosage_g_kg: int
    afp: float
    sp: float


class Ingredient(TypedDict):
    name: str
    quantity: float
    category: str | None
    processing_class: str
    moisture: float
    fat: float
    sugar: float
    protein: float
    batch_weight_g: float


class SOPStep(TypedDict):
    step: int
    phase: str
    action: str
    details: str
    temp: str


class FormulationResult(TypedDict):
    recipe_name: str
    batch_size_kg: float
    ingredients: list[Ingredient]
    composition: Composition
    properties: Properties
    sop: list[SOPStep]


class FormulationState(rx.State):
    """
    Manages the state of the formulation process.
    """

    search_query: str = ""
    search_results: list[dict] = []
    selected_recipe: dict = {}
    batch_size: float = 1.0
    is_generating: bool = False
    formulation_result: Optional[FormulationResult] = None
    validation_results: list[dict] = []

    @rx.var
    def composition_chart_data(self) -> list[dict[str, str | float]]:
        if not self.formulation_result:
            return []
        comp = self.formulation_result["composition"]
        return [
            {"name": "Fat", "value": comp["fat"], "fill": "#F59E0B"},
            {"name": "Sugar", "value": comp["sugar"], "fill": "#EC4899"},
            {"name": "Protein", "value": comp["protein"], "fill": "#8B5CF6"},
            {"name": "Moisture", "value": comp["moisture"], "fill": "#3B82F6"},
            {
                "name": "Other",
                "value": round(
                    100
                    - (
                        comp["fat"] + comp["sugar"] + comp["protein"] + comp["moisture"]
                    ),
                    2,
                ),
                "fill": "#9CA3AF",
            },
        ]

    @rx.event
    async def handle_search(self, query: str):
        self.search_query = query
        if len(query) > 2:
            self.search_results = await GelatoUniversityClient.search_recipes(query)
        else:
            self.search_results = []

    @rx.event
    def select_recipe(self, recipe: dict):
        self.selected_recipe = recipe
        self.search_results = []
        self.search_query = recipe.get("name", "")
        self.formulation_result = None

    @rx.event
    async def generate_formulation(self):
        if not self.selected_recipe:
            return
        self.is_generating = True
        yield
        try:
            result = await SweetToPasteEngine.process_recipe(
                self.selected_recipe, self.batch_size
            )
            self.formulation_result = result
            self.validation_results = FormulationValidator.validate_formulation(result)
        except Exception as e:
            logging.exception(f"Generation error: {e}")
        finally:
            self.is_generating = False