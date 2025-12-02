from dataclasses import dataclass, field


@dataclass
class Ingredient:
    """
    Represents a single ingredient in a formulation with its nutritional breakdown.
    All percentages should ideally sum to ~100% (excluding water which is calculated or explicit).
    """

    name: str
    quantity_g: float
    sugars_pct: float = 0.0
    fat_pct: float = 0.0
    msnf_pct: float = 0.0
    other_solids_pct: float = 0.0
    water_pct: float = 0.0

    @property
    def total_solids_pct(self) -> float:
        """Calculates total solids percentage."""
        return self.sugars_pct + self.fat_pct + self.msnf_pct + self.other_solids_pct


@dataclass
class PasteComposition:
    """
    Represents the calculated chemical composition of the final paste mixture.
    Used for property calculations (viscosity, aw, shelf-life).
    """

    total_weight_g: float
    total_fat_pct: float
    total_sugars_pct: float
    total_msnf_pct: float
    total_other_solids_pct: float
    total_water_pct: float

    @property
    def total_solids_pct(self) -> float:
        """Calculates total solids percentage."""
        return (
            self.total_fat_pct
            + self.total_sugars_pct
            + self.total_msnf_pct
            + self.total_other_solids_pct
        )


@dataclass
class ValidationRuleResult:
    """
    The result of a single validation rule check.
    """

    rule_name: str
    status: str
    message: str
    value: float | str | None = None
    threshold: str | None = None


@dataclass
class PasteValidation:
    """
    Aggregated validation results for a formulation.
    """

    is_valid: bool
    results: list[ValidationRuleResult] = field(default_factory=list)

    @property
    def has_warnings(self) -> bool:
        """Checks if there are any warnings."""
        return any((r.status == "WARNING" for r in self.results))

    @property
    def has_failures(self) -> bool:
        """Checks if there are any failures."""
        return any((r.status == "FAIL" for r in self.results))

    from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional


@dataclass
class Ingredient:
    """
    Generic ingredient model with composition expressed as percentages (0–100).
    quantity_g is per-batch amount when used in a formulation.
    """
    name: str
    quantity_g: float = 0.0
    water_pct: float = 0.0
    sugars_pct: float = 0.0
    fat_pct: float = 0.0
    msnf_pct: float = 0.0
    other_pct: float = 0.0
    # Optional: AFP, POD etc. per 100 g if you want to cache
    afp_per_100g: float = 0.0
    pod_per_100g: float = 0.0
    de_equivalent: float = 0.0


@dataclass
class SweetProfile:
    """
    Fully resolved profile of one Indian sweet, combining:
    - composition from sweet_compositions
    - target paste spec from sweet_paste_profiles
    - formulation family for validation thresholds
    """
    sweet_id: int
    sweet_name: str
    category: str                # e.g. "dairy_fried_sugary", "nut_rich"
    formulation_type: str        # maps to validation families: "eggs_nuts", "pure_dairy", etc.

    # per-100 g sweet composition
    water_pct: float
    sugars_pct: float
    fat_pct: float
    msnf_pct: float
    other_pct: float
    afp_per_100g: float

    # paste spec inputs from sweet_paste_profiles
    sweet_pct_min: float         # as percentage of paste weight, e.g. 40.0
    sweet_pct_max: float
    sweet_pct_default: float

    target_sugar_pct_range: Tuple[float, float]
    target_fat_pct_range: Tuple[float, float]
    target_msnf_pct_range: Tuple[float, float]
    target_solids_pct_range: Tuple[float, float]
    target_aw_range: Tuple[float, float]

    base_template_id: int
    intensity_tag: str = "medium"  # "strong", "medium", "weak"


@dataclass
class BaseTemplateComposition:
    """
    Aggregated composition of the base formulation template as if it were a single ingredient.
    All values are per-100 g of the base.
    """
    template_id: int
    name: str
    water_pct: float
    sugars_pct: float
    fat_pct: float
    msnf_pct: float
    other_pct: float
    afp_per_100g: float
    pod_per_100g: float
    de_equivalent: float
    # Optional: keep the detailed ingredient breakdown if needed
    ingredient_breakdown: Dict[str, float] = field(default_factory=dict)  # name -> pct


@dataclass
class PasteMetrics:
    """
    Extended metrics for the designed paste, beyond basic composition.
    All values are per-100 g paste unless otherwise noted.
    """
    sugar_pct: float
    fat_pct: float
    msnf_pct: float
    other_pct: float
    solids_pct: float
    water_pct: float

    afp_total: float
    pod_sweetness: float
    de_total: float
    pac_total: float
    sp_total: float

    water_activity: float


@dataclass
class ParameterStatus:
    name: str
    value: float
    status: str             # "CRITICAL", "ACCEPTABLE", "OPTIMAL"
    message: str
    distance_from_optimal: float


@dataclass
class ValidationReport:
    parameters: List[ParameterStatus] = field(default_factory=list)
    overall_status: str = "UNKNOWN"     # "GREEN", "AMBER", "RED"
    key_recommendations: List[str] = field(default_factory=list)


@dataclass
class DesignedPaste:
    """
    Final output of the PasteDesigner.
    """
    sweet_profile: SweetProfile
    sweet_pct: float
    base_pct: float
    base_template: BaseTemplateComposition
    batch_weight_g: float

    metrics: PasteMetrics
    validation: Optional[ValidationReport] = None

    # Optional: full ingredient breakdown when we expand base into actual ingredients
    ingredient_breakdown: Dict[str, float] = field(default_factory=dict)  # name -> grams
