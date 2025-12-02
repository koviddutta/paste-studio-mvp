"""
Validation logic for the Paste Core module.
Placeholder for future implementation.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from app.database.supabase_client import get_client
from .domain import (
    PasteMetrics,
    SweetProfile,
    ValidationReport,
    ParameterStatus,
)


@dataclass
class ThresholdRule:
    parameter_name: str
    optimal_min: Optional[float]
    optimal_max: Optional[float]
    acceptable_min: Optional[float]
    acceptable_max: Optional[float]
    critical_min: Optional[float]
    critical_max: Optional[float]
    explanation: str
    scientific_basis: str = ""
    unit: str = ""


def _to_float(value) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _load_extended_thresholds(formulation_type: str) -> Dict[str, ThresholdRule]:
    """
    Load category-specific thresholds from validation_thresholds_extended
    for a given formulation_type (e.g. 'cocoa_chocolate', 'eggs_nuts', 'pure_dairy', etc.).
    Returns mapping: parameter_name -> ThresholdRule
    """
    supabase = get_client()
    resp = (
        supabase.table("validation_thresholds_extended")
        .select("*")
        .eq("formulation_type", formulation_type)
        .execute()
    )
    rows = resp.data or []

    rules: Dict[str, ThresholdRule] = {}
    for row in rows:
        pname = row.get("parameter_name")
        if not pname:
            continue

        rules[pname] = ThresholdRule(
            parameter_name=pname,
            optimal_min=_to_float(row.get("optimal_min")),
            optimal_max=_to_float(row.get("optimal_max")),
            acceptable_min=_to_float(row.get("acceptable_min")),
            acceptable_max=_to_float(row.get("acceptable_max")),
            critical_min=_to_float(row.get("critical_min")),
            critical_max=_to_float(row.get("critical_max")),
            explanation=row.get("explanation") or "",
            scientific_basis=row.get("scientific_basis") or "",
            unit=row.get("measurement_unit") or "",
        )

    return rules


def _load_global_thresholds() -> Dict[str, ThresholdRule]:
    """
    Load generic thresholds from validation_thresholds (no formulation_type).
    Returns mapping: parameter_name -> ThresholdRule
    """
    supabase = get_client()
    resp = supabase.table("validation_thresholds").select("*").execute()
    rows = resp.data or []

    rules: Dict[str, ThresholdRule] = {}
    for row in rows:
        pname = row.get("parameter_name")
        if not pname:
            continue

        rules[pname] = ThresholdRule(
            parameter_name=pname,
            optimal_min=_to_float(row.get("optimal_min")),
            optimal_max=_to_float(row.get("optimal_max")),
            acceptable_min=_to_float(row.get("acceptable_min")),
            acceptable_max=_to_float(row.get("acceptable_max")),
            critical_min=None,   # base table usually has only optimal + acceptable
            critical_max=None,
            explanation=row.get("explanation") or "",
            scientific_basis="",
            unit="",
        )

    return rules


def _classify_value(
    value: float,
    rule: ThresholdRule,
) -> tuple[str, float, str]:
    """
    Classify a parameter against its thresholds.

    Returns:
        status: "CRITICAL" | "ACCEPTABLE" | "OPTIMAL"
        distance_from_center: float
        message: str
    """
    v = value
    p = rule.parameter_name

    # Helper to construct message
    def rng(a, b):
        if a is None or b is None:
            return "n/a"
        return f"{a}–{b}"

    # 1) Critical check (if defined)
    if rule.critical_min is not None and v < rule.critical_min:
        msg = (
            f"{p} {v:.3f} is below critical_min {rule.critical_min} "
            f"({rule.explanation})"
        )
        return "CRITICAL", 0.0, msg
    if rule.critical_max is not None and v > rule.critical_max:
        msg = (
            f"{p} {v:.3f} is above critical_max {rule.critical_max} "
            f"({rule.explanation})"
        )
        return "CRITICAL", 0.0, msg

    # 2) Acceptable range
    acceptable_min = rule.acceptable_min if rule.acceptable_min is not None else rule.optimal_min
    acceptable_max = rule.acceptable_max if rule.acceptable_max is not None else rule.optimal_max

    if acceptable_min is not None and v < acceptable_min:
        center = (acceptable_min + (rule.optimal_min or acceptable_min)) / 2.0
        dist = abs(v - center)
        msg = (
            f"{p} {v:.3f} is below acceptable range {rng(acceptable_min, acceptable_max)}. "
            f"{rule.explanation}"
        )
        return "ACCEPTABLE", dist, msg

    if acceptable_max is not None and v > acceptable_max:
        center = ((rule.optimal_max or acceptable_max) + acceptable_max) / 2.0
        dist = abs(v - center)
        msg = (
            f"{p} {v:.3f} is above acceptable range {rng(acceptable_min, acceptable_max)}. "
            f"{rule.explanation}"
        )
        return "ACCEPTABLE", dist, msg

    # 3) Within acceptable → check optimal band
    if rule.optimal_min is not None and v < rule.optimal_min:
        center = 0.5 * (rule.optimal_min + (rule.optimal_max or rule.optimal_min))
        dist = abs(v - center)
        msg = (
            f"{p} {v:.3f} within acceptable but below optimal {rng(rule.optimal_min, rule.optimal_max)}. "
            f"{rule.explanation}"
        )
        return "ACCEPTABLE", dist, msg

    if rule.optimal_max is not None and v > rule.optimal_max:
        center = 0.5 * (rule.optimal_min or rule.optimal_max + rule.optimal_max)
        dist = abs(v - center)
        msg = (
            f"{p} {v:.3f} within acceptable but above optimal {rng(rule.optimal_min, rule.optimal_max)}. "
            f"{rule.explanation}"
        )
        return "ACCEPTABLE", dist, msg

    # 4) Fully optimal
    center = 0.0
    if rule.optimal_min is not None and rule.optimal_max is not None:
        center = 0.5 * (rule.optimal_min + rule.optimal_max)
    dist = abs(v - center) if center else 0.0
    msg = (
        f"{p} {v:.3f} is within optimal range {rng(rule.optimal_min, rule.optimal_max)}. "
        f"{rule.explanation}"
    )
    return "OPTIMAL", dist, msg


def validate_paste(
    metrics: PasteMetrics,
    formulation_type: str,
    sweet_profile: SweetProfile | None = None,
) -> ValidationReport:
    """
    DB-driven validator:
      - Load category-specific thresholds from validation_thresholds_extended.
      - Load global thresholds from validation_thresholds as fallback.
      - Evaluate key parameters and return a full ValidationReport.
    """
    ext_rules = _load_extended_thresholds(formulation_type=formulation_type)
    global_rules = _load_global_thresholds()

    # Map code-level metric names -> parameter_name in DB
    value_map: Dict[str, float] = {
        "afp_total": metrics.afp_total,
        "pod_sweetness": metrics.pod_sweetness,
        "de_total": metrics.de_total,
        "pac_total": metrics.pac_total,
        "solids_total": metrics.solids_pct,
        "fat_total": metrics.fat_pct,
        "water_activity": metrics.water_activity,
        # Some tables call it final_sugars_pct; paste uses sugar_pct:
        "final_sugars_pct": metrics.sugar_pct,
    }

    params: List[ParameterStatus] = []
    worst_severity = "OPTIMAL"

    severity_rank = {"OPTIMAL": 0, "ACCEPTABLE": 1, "CRITICAL": 2}

    for pname, value in value_map.items():
        # Prefer extended rule for that formulation_type
        rule = ext_rules.get(pname)

        # If not found, fallback to global table with a compatible name
        if rule is None:
            # e.g. solids_total might be recorded just as "solids_total" or "total_solids_pct"
            if pname in global_rules:
                rule = global_rules[pname]
            elif pname == "solids_total" and "total_solids_pct" in global_rules:
                rule = global_rules["total_solids_pct"]
            elif pname == "final_sugars_pct" and "final_sugars_pct" in global_rules:
                rule = global_rules["final_sugars_pct"]

        if rule is None:
            # No rule defined – skip this parameter
            continue

        status, dist, msg = _classify_value(value=value, rule=rule)

        # Include scientific_basis if available
        if rule.scientific_basis:
            msg = f"{msg} Science: {rule.scientific_basis}"

        params.append(
            ParameterStatus(
                name=pname,
                value=value,
                status=status,
                message=msg,
                distance_from_optimal=dist,
            )
        )

        if severity_rank[status] > severity_rank[worst_severity]:
            worst_severity = status

    # Overall status mapping
    if worst_severity == "CRITICAL":
        overall = "RED"
    elif worst_severity == "ACCEPTABLE":
        overall = "AMBER"
    else:
        overall = "GREEN"

    key_recs = [p.message for p in params if p.status != "OPTIMAL"]

    return ValidationReport(
        parameters=params,
        overall_status=overall,
        key_recommendations=key_recs,
    )

