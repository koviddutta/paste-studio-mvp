"""
Validation logic for the Paste Core module.
Placeholder for future implementation.
"""

from __future__ import annotations
import logging
from dataclasses import dataclass
from typing import Optional
from app.database.supabase_client import get_supabase
from .domain import PasteMetrics, SweetProfile, ValidationReport, ParameterStatus


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
    except (TypeError, ValueError) as e:
        logging.exception(f"Error converting value '{value}' to float: {e}")
        return None


def _load_extended_thresholds(formulation_type: str) -> dict[str, ThresholdRule]:
    """
    Load category-specific thresholds from validation_thresholds_extended
    for a given formulation_type (e.g. 'cocoa_chocolate', 'eggs_nuts', 'pure_dairy', etc.).
    Returns mapping: parameter_name -> ThresholdRule
    """
    supabase = get_supabase()
    resp = (
        supabase.table("validation_thresholds_extended")
        .select("*")
        .eq("formulation_type", formulation_type)
        .execute()
    )
    rows = resp.data or []
    rules: dict[str, ThresholdRule] = {}
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


def _load_global_thresholds() -> dict[str, ThresholdRule]:
    """
    Load generic thresholds from validation_thresholds (no formulation_type).
    Returns mapping: parameter_name -> ThresholdRule
    """
    supabase = get_supabase()
    resp = supabase.table("validation_thresholds").select("*").execute()
    rows = resp.data or []
    rules: dict[str, ThresholdRule] = {}
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
            critical_min=None,
            critical_max=None,
            explanation=row.get("explanation") or "",
            scientific_basis="",
            unit="",
        )
    return rules


def _classify_value(value: float, rule: ThresholdRule) -> tuple[str, float, str]:
    """
    Classify a parameter against its thresholds.

    Returns:
        status: "CRITICAL" | "ACCEPTABLE" | "OPTIMAL"
        distance_from_center: float
        message: str
    """
    v = value
    p = rule.parameter_name

    def rng(a, b):
        if a is None or b is None:
            return "n/a"
        return f"{a}–{b}"

    if rule.critical_min is not None and v < rule.critical_min:
        msg = f"{p} {v:.3f} is below critical_min {rule.critical_min} ({rule.explanation})"
        return ("CRITICAL", 0.0, msg)
    if rule.critical_max is not None and v > rule.critical_max:
        msg = f"{p} {v:.3f} is above critical_max {rule.critical_max} ({rule.explanation})"
        return ("CRITICAL", 0.0, msg)
    acceptable_min = (
        rule.acceptable_min if rule.acceptable_min is not None else rule.optimal_min
    )
    acceptable_max = (
        rule.acceptable_max if rule.acceptable_max is not None else rule.optimal_max
    )
    if acceptable_min is not None and v < acceptable_min:
        center = (acceptable_min + (rule.optimal_min or acceptable_min)) / 2.0
        dist = abs(v - center)
        msg = f"{p} {v:.3f} is below acceptable range {rng(acceptable_min, acceptable_max)}. {rule.explanation}"
        return ("ACCEPTABLE", dist, msg)
    if acceptable_max is not None and v > acceptable_max:
        center = ((rule.optimal_max or acceptable_max) + acceptable_max) / 2.0
        dist = abs(v - center)
        msg = f"{p} {v:.3f} is above acceptable range {rng(acceptable_min, acceptable_max)}. {rule.explanation}"
        return ("ACCEPTABLE", dist, msg)
    if rule.optimal_min is not None and v < rule.optimal_min:
        center = 0.5 * (rule.optimal_min + (rule.optimal_max or rule.optimal_min))
        dist = abs(v - center)
        msg = f"{p} {v:.3f} within acceptable but below optimal {rng(rule.optimal_min, rule.optimal_max)}. {rule.explanation}"
        return ("ACCEPTABLE", dist, msg)
    if rule.optimal_max is not None and v > rule.optimal_max:
        center = 0.5 * (rule.optimal_min or rule.optimal_max + rule.optimal_max)
        dist = abs(v - center)
        msg = f"{p} {v:.3f} within acceptable but above optimal {rng(rule.optimal_min, rule.optimal_max)}. {rule.explanation}"
        return ("ACCEPTABLE", dist, msg)
    center = 0.0
    if rule.optimal_min is not None and rule.optimal_max is not None:
        center = 0.5 * (rule.optimal_min + rule.optimal_max)
    dist = abs(v - center) if center else 0.0
    msg = f"{p} {v:.3f} is within optimal range {rng(rule.optimal_min, rule.optimal_max)}. {rule.explanation}"
    return ("OPTIMAL", dist, msg)


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
    value_map: dict[str, float] = {
        # Existing global / legacy parameters
        "afp_total": metrics.afp_total,
        "pod_sweetness": metrics.pod_sweetness,
        "de_total": metrics.de_total,
        "pac_total": metrics.pac_total,

        # Solids
        "solids_total": metrics.solids_pct,
        "total_solids_pct": metrics.solids_pct,      # if global table uses this
        "paste_total_solids_pct": metrics.solids_pct,  # new paste-specific rule

        # Fat
        "fat_total": metrics.fat_pct,
        "paste_fat_pct": metrics.fat_pct,            # new paste-specific rule

        # Sugars
        "final_sugars_pct": metrics.sugar_pct,
        "paste_sugars_pct": metrics.sugar_pct,       # new paste-specific rule

        # Water activity
        "water_activity": metrics.water_activity,
        "paste_aw": metrics.water_activity,          # new paste-specific rule
    }

    # Optional lactose mapping if you added lactose_pct to PasteMetrics
    if getattr(metrics, "lactose_pct", None) is not None:
        value_map["paste_lactose_pct"] = metrics.lactose_pct

    params: list[ParameterStatus] = []
    worst_severity = "OPTIMAL"
    severity_rank = {"OPTIMAL": 0, "ACCEPTABLE": 1, "CRITICAL": 2}
    for pname, value in value_map.items():
        rule = ext_rules.get(pname)
        if rule is None:
            if pname in global_rules:
                rule = global_rules[pname]
            elif pname == "solids_total" and "total_solids_pct" in global_rules:
                rule = global_rules["total_solids_pct"]
            elif pname == "final_sugars_pct" and "final_sugars_pct" in global_rules:
                rule = global_rules["final_sugars_pct"]
        if rule is None:
            continue
        status, dist, msg = _classify_value(value=value, rule=rule)
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
    if worst_severity == "CRITICAL":
        overall = "RED"
    elif worst_severity == "ACCEPTABLE":
        overall = "AMBER"
    else:
        overall = "GREEN"
    key_recs = [p.message for p in params if p.status != "OPTIMAL"]
    return ValidationReport(
        parameters=params, overall_status=overall, key_recommendations=key_recs
    )