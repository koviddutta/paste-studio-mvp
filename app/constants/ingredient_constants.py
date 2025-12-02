"""
Constants and classifications for ingredients used in Indian Sweets formulation.
"""


class IngredientCategory:
    """Primary categories for ingredient classification."""

    DAIRY = "Dairy"
    SWEETENER = "Sweetener"
    FAT_OIL = "Fat/Oil"
    FLOUR_GRAIN = "Flour/Grain"
    NUT_SEED = "Nut/Seed"
    SPICE_FLAVOR = "Spice/Flavor"
    LIQUID = "Liquid"
    FRUIT_VEG = "Fruit/Vegetable"
    ADDITIVE = "Additive"
    OTHER = "Other"


class IngredientSubCategory:
    """Specific sub-types of ingredients for detailed processing logic."""

    MILK_LIQUID = "Milk (Liquid)"
    MILK_POWDER = "Milk Powder"
    KHOA = "Khoa"
    PANEER = "Paneer"
    CHENNA = "Chenna"
    CURD = "Curd/Yogurt"
    GHEE = "Ghee"
    BUTTER = "Butter"
    SUGAR = "Sugar"
    JAGGERY = "Jaggery"
    HONEY = "Honey"
    SYRUP = "Syrup"
    WHEAT_FLOUR = "Wheat Flour"
    MAIDA = "Maida"
    BESAN = "Besan (Gram Flour)"
    RICE_FLOUR = "Rice Flour"
    SEMOLINA = "Semolina (Rava/Suji)"


class ProcessingState:
    """State of the ingredient during processing."""

    RAW = "Raw"
    BOILED = "Boiled"
    ROASTED = "Roasted"
    FRIED = "Fried"
    POWDERED = "Powdered"
    PASTE = "Paste"
    SOAKED = "Soaked"
    GRATED = "Grated"


class UnitType:
    """Standard units of measurement."""

    GRAM = "g"
    KILOGRAM = "kg"
    MILLILITER = "ml"
    LITER = "l"
    CUP = "cup"
    TABLESPOON = "tbsp"
    TEASPOON = "tsp"
    PIECE = "pc"


FUNCTIONAL_PROPERTIES = {
    "moisture": "Moisture Content (%)",
    "fat": "Fat Content (%)",
    "sugar": "Sugar Content (%)",
    "protein": "Protein Content (%)",
    "water_activity": "Water Activity (aw)",
    "acidity": "Acidity (pH)",
}
WATER_ACTIVITY_DRIVERS = [
    IngredientCategory.DAIRY,
    IngredientCategory.LIQUID,
    IngredientCategory.FRUIT_VEG,
]
HUMECTANTS = [IngredientCategory.SWEETENER]