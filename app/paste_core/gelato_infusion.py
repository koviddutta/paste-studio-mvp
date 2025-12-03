# app/paste_core/gelato_infusion.py

from __future__ import annotations
from typing import Dict, List

from .domain import (
    PasteMetrics,
    GelatoBaseProfile,
    PasteInfusionRecommendation,
    SweetProfile,
)


def _solve_linear_constraint(
    base_value: float,
    paste_value: float,
    min_allowed: float | None,
    max_allowed: float | None,
) -> float:
    if min_allowed is None and max_allowed is None:
        return 1.0

    v_b = base_value
    v_p = paste_value

    if abs(v_p - v_b) < 1e-9:
        return 1.0

    p_candidates: List[float] = []

    if max_allowed is not None:
        rhs = max_allowed - v_b
        denom = (v_p - v_b)
        if abs(denom) > 1e-9:
            p_max = rhs / denom
            p_candidates.append(p_max)

    if min_allowed is not None:
        rhs = min_allowed - v_b
        denom = (v_p - v_b)
        if abs(denom) > 1e-9:
            # Lower bound seldom restricts paste %, so we just ensure feasibility.
            p_candidates.append(1.0)

    p_max_effective = 1.0
    for p in p_candidates:
        if p < 0:
            continue
        p_max_effective = min(p_max_effective, p)

    p_max_effective = max(0.0, min(1.0, p_max_effective))
    return p_max_effective


def _intensity_cap(intensity_tag: str, p_science_max: float) -> float:
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
    Computes how much paste can be added to a finished gelato base
    without violating sugar / fat / solids constraints.
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

    # AFP constraint – optional for now
    p_afp = 1.0
    science_limits["afp"] = p_afp

    # Final science max
    p_science_max = min(science_limits.values())
    p_science_max = max(0.0, min(1.0, p_science_max))

    # Apply flavour intensity logic
    intensity_tag = sweet_profile.intensity_tag if sweet_profile else "medium"
    p_recommended_max = _intensity_cap(intensity_tag, p_science_max)

    # Suggested default inclusion
    p_recommended_default = min(p_science_max, 0.7 * p_recommended_max)

    commentary: List[str] = []
    commentary.append(
        f"Science max inclusion = {p_science_max*100:.1f}% based on sugar/fat/solids."
    )
    commentary.append(
        f"Intensity '{intensity_tag}' caps recommended inclusion at {p_recommended_max*100:.1f}%."
    )
    commentary.append(
        f"Suggested working point = {p_recommended_default*100:.1f}% paste."
    )

    return PasteInfusionRecommendation(
        base_name=base_profile.name,
        p_science_max=p_science_max,
        p_recommended_max=p_recommended_max,
        p_recommended_default=p_recommended_default,
        science_limits=science_limits,
        commentary=commentary,
    )
