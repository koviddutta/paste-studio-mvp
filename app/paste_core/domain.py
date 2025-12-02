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