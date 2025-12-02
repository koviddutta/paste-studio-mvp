"""
Validation logic for the Paste Core module.
Placeholder for future implementation.
"""

from __future__ import annotations
from .domain import PasteMetrics, SweetProfile, ValidationReport, ParameterStatus


def validate_paste(
    metrics: PasteMetrics,
    formulation_type: str,
    sweet_profile: SweetProfile | None = None,
) -> ValidationReport:
    """
    TEMPORARY VALIDATOR:
      - Accepts metrics + formulation_type + sweet_profile
      - Returns a ValidationReport with simple checks
    Replace this later with the DB-driven version.
    """
    params: list[ParameterStatus] = []

    def add_param(name: str, value: float, optimal_min: float, optimal_max: float):
        if optimal_min <= value <= optimal_max:
            status = "OPTIMAL"
            msg = f"{name} {value:.2f} within optimal {optimal_min}-{optimal_max}."
            dist = 0.0
        else:
            status = "ACCEPTABLE"
            center = 0.5 * (optimal_min + optimal_max)
            dist = abs(value - center)
            msg = f"{name} {value:.2f} outside optimal {optimal_min}-{optimal_max}."
        params.append(
            ParameterStatus(
                name=name,
                value=value,
                status=status,
                message=msg,
                distance_from_optimal=dist,
            )
        )

    add_param("sugar_pct", metrics.sugar_pct, 30.0, 50.0)
    add_param("fat_pct", metrics.fat_pct, 8.0, 25.0)
    add_param("solids_pct", metrics.solids_pct, 70.0, 80.0)
    add_param("water_activity", metrics.water_activity, 0.68, 0.75)
    overall = "GREEN"
    key_recs = []
    for p in params:
        if p.status != "OPTIMAL":
            overall = "AMBER"
            key_recs.append(p.message)
    return ValidationReport(
        parameters=params, overall_status=overall, key_recommendations=key_recs
    )