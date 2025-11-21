from dataclasses import dataclass
from typing import Optional, TypedDict
import logging
from app.database.supabase_client import get_supabase_client
from app.constants import gelato_science_constants as gsc

SupabaseData = dict[str, str | int | float | bool | None | list | dict]


@dataclass
class IngredientPortion:
    name: str
    quantity_grams: float
    percentage_of_batch: float


@dataclass
class PasteProperties:
    total_sugar_pct: float
    total_fat_pct: float
    total_msnf_pct: float
    total_solids_pct: float
    afp_value: float


@dataclass
class PasteValidation:
    sugar_ok: bool
    fat_ok: bool
    msnf_ok: bool
    afp_ok: bool
    aw_ok: bool


class SweetToPasteEngine:
    """Engine to convert Indian Sweets into Gelato Pastes."""

    def __init__(self, supabase_client=None):
        """Initialize the engine with a Supabase client."""
        self.supabase = supabase_client or get_supabase_client()

    def _load_sweet_profile(self, sweet_name: str) -> SupabaseData:
        """Load the specific sweet profile from the database."""
        if not self.supabase:
            raise ValueError("Database connection not available.")
        try:
            response = (
                self.supabase.table("sweet_paste_profiles")
                .select("*")
                .eq("sweet_name", sweet_name)
                .execute()
            )
            if not response.data:
                raise ValueError(f"Sweet profile for '{sweet_name}' not found.")
            return response.data[0]
        except Exception as e:
            logging.exception(f"Error loading sweet profile: {e}")
            raise ValueError(f"Failed to load profile for {sweet_name}: {e}")

    def _load_base_template(self, template_id: int) -> SupabaseData:
        """Load the base formulation template."""
        if not self.supabase:
            raise ValueError("Database connection not available.")
        try:
            response = (
                self.supabase.table("base_formulation_templates")
                .select("*")
                .eq("id", template_id)
                .execute()
            )
            if not response.data:
                raise ValueError(f"Base template ID {template_id} not found.")
            return response.data[0]
        except Exception as e:
            logging.exception(f"Error loading base template: {e}")
            raise ValueError(f"Failed to load base template {template_id}: {e}")

    def _calculate_properties(
        self,
        ingredients: list[IngredientPortion],
        batch_size_grams: float,
        sweet_profile: SupabaseData,
    ) -> PasteProperties:
        """Calculate the physicochemical properties of the paste formulation."""
        total_sugar = 0.0
        total_fat = 0.0
        total_msnf = 0.0
        total_afp_points = 0.0
        for ing in ingredients:
            mass = ing.quantity_grams
            name_upper = ing.name.upper().replace(" ", "_")
            if ing.name == sweet_profile["sweet_name"]:
                total_sugar += mass * (
                    sweet_profile.get("sweet_sugar_pct", 0.0) / 100.0
                )
                total_fat += mass * (sweet_profile.get("sweet_fat_pct", 0.0) / 100.0)
                total_msnf += mass * (sweet_profile.get("sweet_msnf_pct", 0.0) / 100.0)
                sweet_afp = 100
                total_afp_points += (
                    mass
                    * (sweet_profile.get("sweet_sugar_pct", 0.0) / 100.0)
                    * sweet_afp
                )
                continue
            sugar_pct = 100.0 if name_upper in gsc.AFP_VALUES else 0.0
            fat_content = gsc.FAT_CONTENT.get(name_upper, 0.0)
            total_fat += mass * (fat_content / 100.0)
            msnf_content = gsc.MSNF_CONTENT.get(name_upper, 0.0)
            total_msnf += mass * (msnf_content / 100.0)
            afp_val = gsc.AFP_VALUES.get(name_upper, 0.0)
            if afp_val > 0:
                total_sugar += mass * 1.0
                total_afp_points += mass * afp_val
        total_solids = total_sugar + total_fat + total_msnf
        if batch_size_grams > 0:
            return PasteProperties(
                total_sugar_pct=round(total_sugar / batch_size_grams * 100, 2),
                total_fat_pct=round(total_fat / batch_size_grams * 100, 2),
                total_msnf_pct=round(total_msnf / batch_size_grams * 100, 2),
                total_solids_pct=round(total_solids / batch_size_grams * 100, 2),
                afp_value=round(total_afp_points / batch_size_grams, 2),
            )
        return PasteProperties(0, 0, 0, 0, 0)

    def _validate_properties(
        self, properties: PasteProperties, sweet_profile: SupabaseData
    ) -> PasteValidation:
        """Validate the calculated properties against the target profile ranges."""
        tolerance = 2.0
        target_sugar = sweet_profile.get("target_sugar_pct", 30.0)
        target_fat = sweet_profile.get("target_fat_pct", 8.0)
        target_msnf = sweet_profile.get("target_msnf_pct", 8.0)
        target_afp = sweet_profile.get("target_afp", 25.0)
        sugar_ok = abs(properties.total_sugar_pct - target_sugar) <= tolerance
        fat_ok = abs(properties.total_fat_pct - target_fat) <= tolerance
        msnf_ok = abs(properties.total_msnf_pct - target_msnf) <= tolerance
        afp_ok = abs(properties.afp_value - target_afp) <= 5.0
        aw_ok = properties.total_solids_pct > 60.0
        return PasteValidation(
            sugar_ok=sugar_ok,
            fat_ok=fat_ok,
            msnf_ok=msnf_ok,
            afp_ok=afp_ok,
            aw_ok=aw_ok,
        )

    def generate_paste_recipe(
        self,
        sweet_name: str,
        batch_size_grams: float,
        sweet_pct: Optional[float] = None,
    ) -> SupabaseData:
        """Orchestrate the generation of a complete paste formulation."""
        profile = self._load_sweet_profile(sweet_name)
        if sweet_pct is None:
            sweet_pct = profile.get("optimal_sweet_pct", 30.0)
        template_id = profile.get("default_base_template_id")
        if not template_id:
            raise ValueError(f"No base template assigned for {sweet_name}.")
        template = self._load_base_template(template_id)
        base_ingredients_map = template.get("ingredients", {})
        sweet_mass = batch_size_grams * (sweet_pct / 100.0)
        remaining_mass = batch_size_grams - sweet_mass
        total_base_parts = sum(base_ingredients_map.values())
        if total_base_parts == 0:
            raise ValueError("Base template has no ingredients.")
        recipe_ingredients: list[IngredientPortion] = []
        recipe_ingredients.append(
            IngredientPortion(
                name=sweet_name,
                quantity_grams=round(sweet_mass, 2),
                percentage_of_batch=round(sweet_pct, 2),
            )
        )
        for ing_name, parts in base_ingredients_map.items():
            ing_mass = parts / total_base_parts * remaining_mass
            ing_pct = ing_mass / batch_size_grams * 100.0
            recipe_ingredients.append(
                IngredientPortion(
                    name=ing_name,
                    quantity_grams=round(ing_mass, 2),
                    percentage_of_batch=round(ing_pct, 2),
                )
            )
        properties = self._calculate_properties(
            recipe_ingredients, batch_size_grams, profile
        )
        validation = self._validate_properties(properties, profile)
        return {
            "sweet_name": sweet_name,
            "batch_size_grams": batch_size_grams,
            "sweet_pct": sweet_pct,
            "ingredients": [vars(ing) for ing in recipe_ingredients],
            "properties": vars(properties),
            "validation": vars(validation),
        }