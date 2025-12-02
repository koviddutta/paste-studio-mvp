"""
Gelato infusion logic for the Paste Core module.
Placeholder for future implementation.
"""
# app/paste_core/gelato_infusion.py

from __future__ import annotations

from typing import Dict, List

from .domain import PasteMetrics, GelatoBaseProfile, PasteInfusionRecommendation, SweetProfile


def _solve_linear_constraint(
    base_value: float,
    paste_value: float,
    min_allowed: float | None,
    max_allowed: float | None,
) -> float:
    """
    Solve for p (paste fraction, 0..1) such that:
        value_final = (1 - p)*base_value + p*paste_value
    lies within [min_allowed, max_allowed].

    We return the upper bound p_max allowed by this constraint.
    If paste_value == base_value, constraint has no practical effect (returns 1.0).
    """
    if min_allowed is None and max_allowed is None:
        return 1.0

    v_b = base_value
    v_p = paste_value

    if abs(v_p - v_b) < 1e-9:
        # paste has same value as base -> no constraint
        return 1.0

    p_candidates: List[float] = []

    # Upper bound
    if max_allowed is not None:
        # (1 - p)*v_b + p*v_p <= max
        # p*(v_p - v_b) <= max - v_b
        rhs = max_allowed - v_b
        denom = (v_p - v_b)
        if abs(denom) > 1e-9:
            p_max = rhs / denom
            # If paste_value > base_value, this is a real upper bound.
            # If paste_value < base_value, this might be negative, then it's not limiting.
            p_candidates.append(p_max)

    # Lower bound rarely limits p upwards for paste with higher value,
    # but we include it for completeness.
    if min_allowed is not None:
        # (1 - p)*v_b + p*v_p >= min
        # p*(v_p - v_b) >= min - v_b
        rhs = min_allowed - v_b
        denom = (v_p - v_b)
        if abs(denom) > 1e-9:
            p_min = rhs / denom
            # If paste_value < base_value, lower bound might limit p upwards.
            # For our purpose (upper bound), we can ignore lower-bound-induced maxima.
            # But if p_min > 1, it's infeasible anyway.
            # We'll keep only p <= 1 at the end.
            p_candidates.append(1.0)  # we don't use lower bound to constrain p_max here.

    # Filter and pick the smallest positive upper bound
    p_max_effective = 1.0
    for p in p_candidates:
        if p < 0:
            continue
        p_max_effective = min(p_max_effective, p)

    # Bound p to [0,1]
    p_max_effective = max(0.0, min(1.0, p_max_effective))
    return p_max_effective


def _intensity_cap(intensity_tag: str, p_science_max: float) -> float:
    """
    Apply flavour intensity capping on top of science-based limit.

    strong: cap at 0.12 (12%)
    medium: cap at 0.15 (15%)
    weak:   cap at 0.20 (20%)
    """
    intensity_tag = (intensity_tag or "medium").lower()

    if intensity_tag == "strong":
        cap = 0.12
    elif intensity_tag == "weak":
        cap = 0.20
    else:
        cap = 0.15

    return min(p_science_max, cap)


def recommend_paste_in_gelato(
    paste_metrics: PasteMetrics,
    base_profile: GelatoBaseProfile,
    sweet_profile: SweetProfile | None = None,
) -> PasteInfusionRecommendation:
    """
    Compute how much paste (fraction of total mix weight) can be added
    to a given gelato base without violating sugar, fat, solids constraints.

    Steps:
      - For sugar, fat, solids: compute p_max from each constraint.
      - Take the minimum as p_science_max.
      - Apply intensity-based cap to get p_recommended_max.
      - Pick a default p_recommended_default (e.g. 70% of recommended_max).
    """
    science_limits: Dict[str, float] = {}

    # Sugar constraint
    p_sugar = _solve_linear_constraint(
        base_value=base_profile.sugar_pct,
        paste_value=paste_metrics.sugar_pct,
        min_allowed=base_profile.sugar_min,
        max_allowed=base_profile.sugar_max,
    )
    science_limits["sugar"] = p_sugar

    # Fat constraint
    p_fat = _solve_linear_constraint(
        base_value=base_profile.fat_pct,
        paste_value=paste_metrics.fat_pct,
        min_allowed=base_profile.fat_min,
        max_allowed=base_profile.fat_max,
    )
    science_limits["fat"] = p_fat

    # Solids constraint
    p_solids = _solve_linear_constraint(
        base_value=base_profile.solids_pct,
        paste_value=paste_metrics.solids_pct,
        min_allowed=base_profile.solids_min,
        max_allowed=base_profile.solids_max,
    )
    science_limits["solids"] = p_solids

    # AFP constraint (optional; you can wire it later when base_profile.afp_* are set)
    # For now we ignore it or set to 1.0
    p_afp = 1.0
    science_limits["afp"] = p_afp

    # Science max is the tightest of all
    p_science_max = min(science_limits.values())
    p_science_max = max(0.0, min(1.0, p_science_max))

    # Apply intensity cap
    intensity_tag = sweet_profile.intensity_tag if sweet_profile else "medium"
    p_recommended_max = _intensity_cap(intensity_tag, p_science_max)

    # Default: 70% of recommended max, but not more than science max
    p_recommended_default = min(p_science_max, 0.7 * p_recommended_max)

    commentary: List[str] = []

    commentary.append(
        f"Science-based maximum paste inclusion is {p_science_max * 100:.1f}% "
        f"based on sugar/fat/solids constraints."
    )
    commentary.append(
        f"Flavour intensity '{intensity_tag}' caps recommended paste at "
        f"{p_recommended_max * 100:.1f}% of mix."
    )
    commentary.append(
        f"Suggested working point: {p_recommended_default * 100:.1f}% paste "
        f"in the {base_profile.name} base."
    )

    return PasteInfusionRecommendation(
        base_name=base_profile.name,
        p_science_max=p_science_max,
        p_recommended_max=p_recommended_max,
        p_recommended_default=p_recommended_default,
        science_limits=science_limits,
        commentary=commentary,
    )
