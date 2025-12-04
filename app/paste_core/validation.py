"""
Validation logic for the Paste Core module.

DB-driven thresholds + storage-profile aware behaviour.

Key points:
- Uses validation_thresholds_extended (category/formulation-specific) when available.
- Falls back to validation_thresholds (global) if needed.
- For formulation_type='sweet_paste':
    * AFP / PAC / DE are treated as informational and are NOT used to mark RED.
    * Water activity is interpreted based on storage_profile (ambient vs chilled).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional, Dict, List

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
        logging.exception("Error converting value '%s' to float: %s", value, e)
        return None


def _load_extended_thresholds(formulation_type: str) -> Dict[str, ThresholdRule]:
    """
    Load category/formulation-specific thresholds from validation_thresholds_extended
    for a given formulation_type (e.g. 'sweet_paste', 'pure_dairy', etc.).

    Returns:
        mapping: parameter_name -> ThresholdRule
    """
    supabase = get_supabase()
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

    Returns:
        mapping: parameter_name -> ThresholdRule
    """
    supabase = get_supabase()
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

    # 1. Critical bounds (if defined)
    if rule.critical_min is not None and v < rule.critical_min:
        msg = f"{p} {v:.3f} is below critical_min {rule.critical_min} ({rule.explanation})"
        return ("CRITICAL", 0.0, msg)
    if rule.critical_max is not None and v > rule.critical_max:
        msg = f"{p} {v:.3f} is above critical_max {rule.critical_max} ({rule.explanation})"
        return ("CRITICAL", 0.0, msg)

    # 2. Acceptable bounds (fallback to optimal if not set)
    acceptable_min = (
        rule.acceptable_min if rule.acceptable_min is not None else rule.optimal_min
    )
    acceptable_max = (
        rule.acceptable_max if rule.acceptable_max is not None else rule.optimal_max
    )

    if acceptable_min is not None and v < acceptable_min:
        center = (acceptable_min + (rule.optimal_min or acceptable_min)) / 2.0
        dist = abs(v - center)
        msg = (
            f"{p} {v:.3f} is below acceptable range {rng(acceptable_min, acceptable_max)}. "
            f"{rule.explanation}"
        )
        return ("ACCEPTABLE", dist, msg)

    if acceptable_max is not None and v > acceptable_max:
        center = ((rule.optimal_max or acceptable_max) + acceptable_max) / 2.0
        dist = abs(v - center)
        msg = (
            f"{p} {v:.3f} is above acceptable range {rng(acceptable_min, acceptable_max)}. "
            f"{rule.explanation}"
        )
        return ("ACCEPTABLE", dist, msg)

    # 3. Strictly optimal band
    if rule.optimal_min is not None and v < rule.optimal_min:
        center = 0.5 * (rule.optimal_min + (rule.optimal_max or rule.optimal_min))
        dist = abs(v - center)
        msg = (
            f"{p} {v:.3f} within acceptable but below optimal "
            f"{rng(rule.optimal_min, rule.optimal_max)}. {rule.explanation}"
        )
        return ("ACCEPTABLE", dist, msg)

    if rule.optimal_max is not None and v > rule.optimal_max:
        center = 0.5 * ((rule.optimal_min or rule.optimal_max) + rule.optimal_max)
        dist = abs(v - center)
        msg = (
            f"{p} {v:.3f} within acceptable but above optimal "
            f"{rng(rule.optimal_min, rule.optimal_max)}. {rule.explanation}"
        )
        return ("ACCEPTABLE", dist, msg)

    # 4. Inside optimal range
    center = 0.0
    if rule.optimal_min is not None and rule.optimal_max is not None:
        center = 0.5 * (rule.optimal_min + rule.optimal_max)
    dist = abs(v - center) if center else 0.0
    msg = (
        f"{p} {v:.3f} is within optimal range {rng(rule.optimal_min, rule.optimal_max)}. "
        f"{rule.explanation}"
    )
    return ("OPTIMAL", dist, msg)


def validate_paste(
    metrics: PasteMetrics,
    formulation_type: str,
    sweet_profile: SweetProfile | None = None,
    storage_profile: str = "chilled",  # "ambient" | "chilled" | "immediate_freezing"
) -> ValidationReport:
    """
    DB-driven validator:

      - Load category-specific thresholds from validation_thresholds_extended.
      - Load global thresholds from validation_thresholds as fallback.
      - Evaluate key parameters and return a full ValidationReport.

    Important behaviour:
      - For formulation_type == 'sweet_paste':
          * AFP / PAC / DE are informational only (not used to mark RED).
          * water_activity is interpreted with storage_profile:
              - ambient: strict Aw limits (<= 0.85 typical).
              - chilled / immediate_freezing: Aw > 0.92 → CRITICAL, 0.90–0.92 → AMBER.
    """
    ext_rules = _load_extended_thresholds(formulation_type=formulation_type)
    global_rules = _load_global_thresholds()

    # Key parameters we currently track
    value_map: Dict[str, float] = {
        "afp_total": metrics.afp_total,
        "pod_sweetness": metrics.pod_sweetness,
        "de_total": metrics.de_total,
        "pac_total": metrics.pac_total,
        "solids_total": metrics.solids_pct,
        "fat_total": metrics.fat_pct,
        "water_activity": metrics.water_activity,
        "final_sugars_pct": metrics.sugar_pct,
    }

    params: List[ParameterStatus] = []
    worst_severity = "OPTIMAL"
    severity_rank = {"OPTIMAL": 0, "ACCEPTABLE": 1, "CRITICAL": 2}

    for pname, value in value_map.items():
        # Skip parameters we do not want to enforce for certain formulation types
        if formulation_type == "sweet_paste" and pname in {
            "afp_total",
            "pac_total",
            "de_total",
        }:
            # Still keep them visible through metrics, but do not classify here.
            continue

        # Special handling for water_activity based on storage_profile
        if pname == "water_activity":
            aw_val = value
            if storage_profile == "ambient":
                # Use DB thresholds (strict) for ambient pastes
                rule = ext_rules.get("water_activity") or global_rules.get(
                    "water_activity"
                )
                if rule is None:
                    # No rule in DB; fall back to a simple heuristic
                    if aw_val > 0.90:
                        status = "CRITICAL"
                        dist = 0.0
                        msg = (
                            f"Aw {aw_val:.3f} very high for ambient storage; "
                            "risk of microbial growth."
                        )
                    elif aw_val > 0.85:
                        status = "ACCEPTABLE"
                        dist = 0.0
                        msg = (
                            f"Aw {aw_val:.3f} slightly above classic 0.85 cutoff for ambient shelf-stable foods."
                        )
                    else:
                        status = "OPTIMAL"
                        dist = 0.0
                        msg = f"Aw {aw_val:.3f} suitable for ambient shelf-stable paste."
                else:
                    status, dist, msg = _classify_value(value=aw_val, rule=rule)
                if status == "CRITICAL":
                    worst_severity = "CRITICAL"
                elif status == "ACCEPTABLE" and severity_rank[status] > severity_rank[worst_severity]:
                    worst_severity = "ACCEPTABLE"

                params.append(
                    ParameterStatus(
                        name=pname,
                        value=aw_val,
                        status=status,
                        message=msg,
                        distance_from_optimal=dist,
                    )
                )
                continue

            else:
                # chilled / immediate_freezing: more relaxed interpretation
                if aw_val > 0.92:
                    status = "CRITICAL"
                    msg = (
                        f"Aw {aw_val:.3f} is too high even for chilled use; "
                        "very short shelf life and high microbial risk."
                    )
                elif aw_val > 0.90:
                    status = "ACCEPTABLE"
                    msg = (
                        f"Aw {aw_val:.3f} is high for chilled paste; "
                        "use rapid cold chain and short shelf life."
                    )
                else:
                    status = "OPTIMAL"
                    msg = (
                        f"Aw {aw_val:.3f} is compatible with chilled/frozen paste use."
                    )

                dist = 0.0
                if severity_rank[status] > severity_rank[worst_severity]:
                    worst_severity = status

                params.append(
                    ParameterStatus(
                        name=pname,
                        value=aw_val,
                        status=status,
                        message=msg,
                        distance_from_optimal=dist,
                    )
                )
                continue

        # Normal parameters: look up rule
        rule = ext_rules.get(pname)
        if rule is None:
            # Some naming compatibility / fallback
            if pname in global_rules:
                rule = global_rules[pname]
            elif pname == "solids_total" and "total_solids_pct" in global_rules:
                rule = global_rules["total_solids_pct"]
            elif pname == "final_sugars_pct" and "final_sugars_pct" in global_rules:
                rule = global_rules["final_sugars_pct"]

        if rule is None:
            # No rule defined at all → ignore parameter for now
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

    # Derive overall status from worst parameter
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
