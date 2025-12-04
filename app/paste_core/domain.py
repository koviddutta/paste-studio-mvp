from dataclasses import dataclass, field
from dataclasses import dataclass
from typing import List, Optional

# ... existing imports and dataclasses ...

@dataclass
class PasteComposition:
    """
    Represents the calculated chemical composition of the final paste mixture.
    Used for property calculations (viscosity, aw, shelf-life).
    """

    total_weight_g: float = 0.0
    total_fat_pct: float = 0.0
    total_sugars_pct: float = 0.0
    total_msnf_pct: float = 0.0
    total_other_pct: float = 0.0
    total_water_pct: float = 0.0
    water_activity: float = 0.0

    @property
    def total_solids_pct(self) -> float:
        """Calculates total solids percentage."""
        return (
            self.total_fat_pct
            + self.total_sugars_pct
            + self.total_msnf_pct
            + self.total_other_pct
        )

    @property
    def sugar_pct(self) -> float:
        return self.total_sugars_pct

    @property
    def fat_pct(self) -> float:
        return self.total_fat_pct

    @property
    def msnf_pct(self) -> float:
        return self.total_msnf_pct

    @property
    def other_pct(self) -> float:
        return self.total_other_pct

    @property
    def solids_pct(self) -> float:
        return self.total_solids_pct


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


from typing import Optional


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
    category: str
    formulation_type: str
    water_pct: float
    sugars_pct: float
    fat_pct: float
    msnf_pct: float
    other_pct: float
    afp_per_100g: float
    sweet_pct_min: float
    sweet_pct_max: float
    sweet_pct_default: float
    target_sugar_pct_range: tuple[float, float]
    target_fat_pct_range: tuple[float, float]
    target_msnf_pct_range: tuple[float, float]
    target_solids_pct_range: tuple[float, float]
    target_aw_range: tuple[float, float]
    base_template_id: int
    intensity_tag: str = "medium"


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
    ingredient_breakdown: dict[str, float] = field(default_factory=dict)


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
    status: str
    message: str
    distance_from_optimal: float


@dataclass
class ValidationReport:
    parameters: list[ParameterStatus] = field(default_factory=list)
    overall_status: str = "UNKNOWN"
    key_recommendations: list[str] = field(default_factory=list)


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
    ingredient_breakdown: dict[str, float] = field(default_factory=dict)
    from typing import Optional


@dataclass
class GelatoBaseProfile:
    """
    Represents a finished gelato base (without paste).

    All composition values are in % of mix weight.
    Ranges are the allowed finished ranges for that base.
    """

    name: str
    sugar_pct: float
    fat_pct: float
    solids_pct: float
    sugar_min: float
    sugar_max: float
    fat_min: float
    fat_max: float
    solids_min: float
    solids_max: float
    afp_total: float = 0.0
    afp_min: float = 0.0
    afp_max: float = 0.0


@dataclass
class PasteInfusionRecommendation:
    base_name: str
    p_science_max: float
    p_recommended_max: float
    p_recommended_default: float
    science_limits: dict[str, float]
    commentary: list[str] = field(default_factory=list)




@dataclass
class PasteAdjustment:
    """
    A single ingredient-level adjustment to move the paste towards target specs.
    delta_g_per_kg is grams to ADD (>0) or REMOVE (<0) per 1 kg of paste.
    """
    ingredient_name: str
    delta_g_per_kg: float
    reason: str


@dataclass
class PasteOptimizationPlan:
    """
    High-level optimization plan for a paste formulation.
    """
    formulation_type: str
    target_solids_pct: Optional[float]
    target_fat_pct: Optional[float]
    target_sugars_pct: Optional[float]
    actions: List[PasteAdjustment]
    notes: List[str]
