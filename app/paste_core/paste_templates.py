from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass
class TemplateIngredientSpec:
    """
    One ingredient within a template, expressed as % of the paste mass.

    pct values are in 0–100 (not 0–1).
    """

    ingredient_name: str
    role: str
    default_pct: float
    min_pct: float
    max_pct: float
    notes: str = ""


@dataclass
class PasteTemplateDefinition:
    """
    Defines a structural template for a class of pastes
    (nut paste, fried-sugar paste, dairy caramel, etc.).
    """

    template_type: str
    description: str
    ingredients: list[TemplateIngredientSpec]
    target_solids_min: float
    target_solids_max: float
    target_aw_chilled_max: float
    target_aw_ambient_max: Optional[float] = None


@dataclass
class SweetTemplateConfig:
    """
    Per-sweet configuration telling the engine how to build the paste:
      - mode: "sweet_dominant", "template_dominant", or "hybrid"
      - template_type: which structural template to use
      - sweet_mass_default_pct: % of final paste mass that is actual finished sweet
    """

    sweet_name: str
    mode: str
    template_type: str
    sweet_mass_default_pct: Optional[float] = None
    sweet_mass_min_pct: Optional[float] = None
    sweet_mass_max_pct: Optional[float] = None
    notes: str = ""


def _nut_paste_template() -> PasteTemplateDefinition:
    """
    Generic nut paste template (pistachio, almond, cashew, hazelnut-like).

    This is structurally similar to commercial nut pastes:
      - majority nuts (55–65%)
      - sugar/glucose for sweetness + structure
      - fat for mouthfeel
      - MSNF/emulsifier for stability

    Exact composition will be refined per nut and per product, but this is a
    high-quality starting point.
    """
    ingredients = [
        TemplateIngredientSpec(
            ingredient_name="Pistachio",
            role="nut",
            default_pct=60.0,
            min_pct=50.0,
            max_pct=70.0,
            notes="Roasted pistachios or equivalent nut mass.",
        ),
        TemplateIngredientSpec(
            ingredient_name="Sugar",
            role="sugar",
            default_pct=15.0,
            min_pct=10.0,
            max_pct=25.0,
            notes="Sucrose; can be partially replaced by glucose/dextrose later.",
        ),
        TemplateIngredientSpec(
            ingredient_name="Ghee",
            role="fat",
            default_pct=15.0,
            min_pct=8.0,
            max_pct=20.0,
            notes="Fat phase; could be neutral oil, cocoa butter, or ghee.",
        ),
        TemplateIngredientSpec(
            ingredient_name="Skim Milk Powder",
            role="msnf",
            default_pct=5.0,
            min_pct=0.0,
            max_pct=10.0,
            notes="Provides milk solids, protein, and improves body.",
        ),
        TemplateIngredientSpec(
            ingredient_name="Water",
            role="water",
            default_pct=5.0,
            min_pct=0.0,
            max_pct=10.0,
            notes="Process water; partially driven off during cooking.",
        ),
    ]
    return PasteTemplateDefinition(
        template_type="nut_paste",
        description="High-solids nut paste template suitable for pistachio/almond/hazelnut style flavour pastes for gelato and ice cream.",
        ingredients=ingredients,
        target_solids_min=62.0,
        target_solids_max=75.0,
        target_aw_chilled_max=0.88,
        target_aw_ambient_max=0.85,
    )


def _fried_sugar_paste_template() -> PasteTemplateDefinition:
    """
    Template for fried-sugar sweets (Jalebi, Imarti, Gulab Jamun coating, etc.)
    when used as a paste base.
    """
    ingredients = [
        TemplateIngredientSpec(
            ingredient_name="__SWEET_MASS__",
            role="sweet_mass",
            default_pct=50.0,
            min_pct=30.0,
            max_pct=70.0,
            notes="Actual finished fried sweet mass (e.g. Jalebi, Gulab Jamun).",
        ),
        TemplateIngredientSpec(
            ingredient_name="Sugar",
            role="sugar",
            default_pct=10.0,
            min_pct=5.0,
            max_pct=20.0,
            notes="Additional sucrose for binding/structure.",
        ),
        TemplateIngredientSpec(
            ingredient_name="Glucose Syrup DE40",
            role="sugar",
            default_pct=10.0,
            min_pct=5.0,
            max_pct=20.0,
            notes="Anti-crystallisation, AFP, and chewiness.",
        ),
        TemplateIngredientSpec(
            ingredient_name="Skim Milk Powder",
            role="msnf",
            default_pct=15.0,
            min_pct=5.0,
            max_pct=25.0,
            notes="Dairy backbone to turn syrupy fried sweets into creamy pastes.",
        ),
        TemplateIngredientSpec(
            ingredient_name="Ghee",
            role="fat",
            default_pct=10.0,
            min_pct=5.0,
            max_pct=20.0,
            notes="Carries fried notes and improves mouthfeel.",
        ),
        TemplateIngredientSpec(
            ingredient_name="Water",
            role="water",
            default_pct=5.0,
            min_pct=0.0,
            max_pct=10.0,
            notes="Process water, largely evaporated to reach target solids.",
        ),
    ]
    return PasteTemplateDefinition(
        template_type="fried_sugar_paste",
        description="Template for Jalebi/Gulab Jamun-style fried-sugar pastes.",
        ingredients=ingredients,
        target_solids_min=60.0,
        target_solids_max=75.0,
        target_aw_chilled_max=0.88,
        target_aw_ambient_max=None,
    )


def _dairy_caramel_paste_template() -> PasteTemplateDefinition:
    """
    Template for rabri/basundi/kulfi-style dairy caramel pastes.
    """
    ingredients = [
        TemplateIngredientSpec(
            ingredient_name="Milk",
            role="dairy",
            default_pct=40.0,
            min_pct=30.0,
            max_pct=60.0,
            notes="Full-fat or buffalo milk boiled down.",
        ),
        TemplateIngredientSpec(
            ingredient_name="Skim Milk Powder",
            role="msnf",
            default_pct=15.0,
            min_pct=5.0,
            max_pct=25.0,
            notes="Boosts MSNF and reduces required evaporation.",
        ),
        TemplateIngredientSpec(
            ingredient_name="Ghee",
            role="fat",
            default_pct=15.0,
            min_pct=5.0,
            max_pct=25.0,
            notes="Milk fat / ghee for richness.",
        ),
        TemplateIngredientSpec(
            ingredient_name="Sugar",
            role="sugar",
            default_pct=20.0,
            min_pct=10.0,
            max_pct=25.0,
            notes="Sucrose; can be partly replaced with glucose/dextrose.",
        ),
        TemplateIngredientSpec(
            ingredient_name="Water",
            role="water",
            default_pct=10.0,
            min_pct=0.0,
            max_pct=20.0,
            notes="Process water, mostly evaporated out.",
        ),
    ]
    return PasteTemplateDefinition(
        template_type="dairy_caramel_paste",
        description="Template for rabri/basundi/kulfi-style dairy caramel pastes.",
        ingredients=ingredients,
        target_solids_min=65.0,
        target_solids_max=78.0,
        target_aw_chilled_max=0.88,
        target_aw_ambient_max=0.85,
    )


def _paneer_paste_template() -> PasteTemplateDefinition:
    """
    Template for paneer/chhena sweets (Rasgulla, Sandesh, Peda) as flavour pastes.
    """
    ingredients = [
        TemplateIngredientSpec(
            ingredient_name="__SWEET_MASS__",
            role="sweet_mass",
            default_pct=50.0,
            min_pct=30.0,
            max_pct=70.0,
            notes="Finished paneer-based sweet mass.",
        ),
        TemplateIngredientSpec(
            ingredient_name="Skim Milk Powder",
            role="msnf",
            default_pct=20.0,
            min_pct=10.0,
            max_pct=30.0,
            notes="Boosts protein and solids for structure.",
        ),
        TemplateIngredientSpec(
            ingredient_name="Ghee",
            role="fat",
            default_pct=15.0,
            min_pct=5.0,
            max_pct=25.0,
            notes="Fat phase for mouthfeel.",
        ),
        TemplateIngredientSpec(
            ingredient_name="Sugar",
            role="sugar",
            default_pct=10.0,
            min_pct=5.0,
            max_pct=20.0,
            notes="Additional sucrose if required.",
        ),
        TemplateIngredientSpec(
            ingredient_name="Water",
            role="water",
            default_pct=5.0,
            min_pct=0.0,
            max_pct=15.0,
            notes="Process water, evaporated as needed.",
        ),
    ]
    return PasteTemplateDefinition(
        template_type="paneer_paste",
        description="Template for Rasgulla/Sandesh/Peda style paneer pastes.",
        ingredients=ingredients,
        target_solids_min=60.0,
        target_solids_max=75.0,
        target_aw_chilled_max=0.88,
        target_aw_ambient_max=None,
    )


def _grain_paste_template() -> PasteTemplateDefinition:
    """
    Template for halwa / grain-based sweets (gajar, suji, moong dal) as pastes.
    """
    ingredients = [
        TemplateIngredientSpec(
            ingredient_name="__SWEET_MASS__",
            role="sweet_mass",
            default_pct=50.0,
            min_pct=30.0,
            max_pct=70.0,
            notes="Finished halwa mass (grain+fat+sugar).",
        ),
        TemplateIngredientSpec(
            ingredient_name="Skim Milk Powder",
            role="msnf",
            default_pct=15.0,
            min_pct=5.0,
            max_pct=25.0,
            notes="Provides dairy backbone.",
        ),
        TemplateIngredientSpec(
            ingredient_name="Ghee",
            role="fat",
            default_pct=15.0,
            min_pct=5.0,
            max_pct=25.0,
            notes="Maintains rich halwa character.",
        ),
        TemplateIngredientSpec(
            ingredient_name="Sugar",
            role="sugar",
            default_pct=10.0,
            min_pct=5.0,
            max_pct=20.0,
            notes="Optional extra sweetness.",
        ),
        TemplateIngredientSpec(
            ingredient_name="Water",
            role="water",
            default_pct=10.0,
            min_pct=0.0,
            max_pct=20.0,
            notes="Process water for blending; evaporated later.",
        ),
    ]
    return PasteTemplateDefinition(
        template_type="grain_paste",
        description="Template for halwa-style grain-based pastes.",
        ingredients=ingredients,
        target_solids_min=60.0,
        target_solids_max=75.0,
        target_aw_chilled_max=0.88,
        target_aw_ambient_max=None,
    )


_TEMPLATE_REGISTRY: dict[str, PasteTemplateDefinition] = {
    "nut_paste": _nut_paste_template(),
    "fried_sugar_paste": _fried_sugar_paste_template(),
    "dairy_caramel_paste": _dairy_caramel_paste_template(),
    "paneer_paste": _paneer_paste_template(),
    "grain_paste": _grain_paste_template(),
}


def get_template_definition(template_type: str) -> PasteTemplateDefinition:
    """
    Get a template definition by type string.
    Raises KeyError if not found.
    """
    if template_type not in _TEMPLATE_REGISTRY:
        raise KeyError(f"Unknown paste template_type: {template_type}")
    return _TEMPLATE_REGISTRY[template_type]


_SWEET_TEMPLATE_CONFIGS: dict[str, SweetTemplateConfig] = {
    "gulab jamun": SweetTemplateConfig(
        sweet_name="Gulab Jamun",
        mode="sweet_dominant",
        template_type="fried_sugar_paste",
        sweet_mass_default_pct=80.0,
        sweet_mass_min_pct=60.0,
        sweet_mass_max_pct=90.0,
        notes="Use finished Gulab Jamun as main mass, then adjust with SMP/ghee/glucose.",
    ),
    "jalebi": SweetTemplateConfig(
        sweet_name="Jalebi",
        mode="sweet_dominant",
        template_type="fried_sugar_paste",
        sweet_mass_default_pct=80.0,
        sweet_mass_min_pct=60.0,
        sweet_mass_max_pct=90.0,
        notes="Use a mix of crispy + soaked Jalebi pieces as sweet mass.",
    ),
    "rasgulla": SweetTemplateConfig(
        sweet_name="Rasgulla",
        mode="sweet_dominant",
        template_type="paneer_paste",
        sweet_mass_default_pct=70.0,
        sweet_mass_min_pct=50.0,
        sweet_mass_max_pct=85.0,
        notes="Finished Rasgulla (squeezed of excess syrup) as main mass.",
    ),
    "sandesh": SweetTemplateConfig(
        sweet_name="Sandesh",
        mode="sweet_dominant",
        template_type="paneer_paste",
        sweet_mass_default_pct=70.0,
        sweet_mass_min_pct=50.0,
        sweet_mass_max_pct=85.0,
        notes="Soft Sandesh mass as main input.",
    ),
    "peda": SweetTemplateConfig(
        sweet_name="Peda",
        mode="sweet_dominant",
        template_type="paneer_paste",
        sweet_mass_default_pct=70.0,
        sweet_mass_min_pct=50.0,
        sweet_mass_max_pct=85.0,
        notes="Peda mass acts like condensed dairy + sugar base.",
    ),
    "kulfi": SweetTemplateConfig(
        sweet_name="Kulfi",
        mode="hybrid",
        template_type="dairy_caramel_paste",
        sweet_mass_default_pct=60.0,
        sweet_mass_min_pct=40.0,
        sweet_mass_max_pct=80.0,
        notes="Kulfi sweet mass plus dairy caramel template.",
    ),
    "rabri": SweetTemplateConfig(
        sweet_name="Rabri",
        mode="template_dominant",
        template_type="dairy_caramel_paste",
        sweet_mass_default_pct=None,
        notes="Use dairy caramel template; rabri profile guides sugar/fat targets.",
    ),
    "halwa": SweetTemplateConfig(
        sweet_name="Halwa",
        mode="sweet_dominant",
        template_type="grain_paste",
        sweet_mass_default_pct=70.0,
        sweet_mass_min_pct=50.0,
        sweet_mass_max_pct=85.0,
        notes="Halwa mass plus dairy/fat corrections.",
    ),
    "pistachio": SweetTemplateConfig(
        sweet_name="Pistachio",
        mode="template_dominant",
        template_type="nut_paste",
        sweet_mass_default_pct=None,
        notes="Build a true pistachio paste; use sweet reference only for flavour targets.",
    ),
    "pistachio burfi": SweetTemplateConfig(
        sweet_name="Pistachio Burfi",
        mode="hybrid",
        template_type="nut_paste",
        sweet_mass_default_pct=40.0,
        sweet_mass_min_pct=20.0,
        sweet_mass_max_pct=60.0,
        notes="Hybrid: pistachio burfi mass plus structural nut paste template.",
    ),
    "kaju katli": SweetTemplateConfig(
        sweet_name="Kaju Katli",
        mode="template_dominant",
        template_type="nut_paste",
        sweet_mass_default_pct=None,
        notes="Cashew-based paste built mostly from nut template.",
    ),
    "barfi": SweetTemplateConfig(
        sweet_name="Barfi",
        mode="hybrid",
        template_type="dairy_caramel_paste",
        sweet_mass_default_pct=50.0,
        sweet_mass_min_pct=30.0,
        sweet_mass_max_pct=70.0,
        notes="Dairy-rich barfi mass plus dairy caramel template.",
    ),
}


def get_sweet_template_config(
    sweet_name: str, category: Optional[str] = None
) -> SweetTemplateConfig:
    """
    Fetch a SweetTemplateConfig for a given sweet by name (case-insensitive).
    If not found, fall back to a category-based heuristic, then a generic default.
    """
    key = sweet_name.strip().lower()
    if key in _SWEET_TEMPLATE_CONFIGS:
        return _SWEET_TEMPLATE_CONFIGS[key]
    if category:
        c = category.lower()
        if "fried" in c or "jalebi" in c:
            return _SWEET_TEMPLATE_CONFIGS["jalebi"]
        if "paneer" in c or "chhena" in c:
            return _SWEET_TEMPLATE_CONFIGS["rasgulla"]
        if "grain" in c or "halwa" in c:
            return _SWEET_TEMPLATE_CONFIGS["halwa"]
        if "nut" in c:
            return _SWEET_TEMPLATE_CONFIGS["pistachio"]
        if "dairy" in c:
            return _SWEET_TEMPLATE_CONFIGS["barfi"]
    return SweetTemplateConfig(
        sweet_name=sweet_name,
        mode="sweet_dominant",
        template_type="fried_sugar_paste",
        sweet_mass_default_pct=80.0,
        sweet_mass_min_pct=60.0,
        sweet_mass_max_pct=90.0,
        notes="Fallback config: treat as sweet-dominant fried/sugary paste.",
    )
