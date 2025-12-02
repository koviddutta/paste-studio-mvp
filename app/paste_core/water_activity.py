"""
Water activity calculations for the Paste Core module.

This module uses a simplified Norrish-style model assuming that the
main Aw-depressing solutes are sugar-like (sucrose, dextrose, syrup).

IMPORTANT:
- Do NOT pass total solids (including fat, cocoa, etc.) as solutes.
- Pass only sugar-like solids mass to get reasonable Aw estimates.
"""

import math

K_NORRISH_SUCROSE = 6.5
MW_WATER_G_PER_MOL = 18.015
MW_SUCROSE_G_PER_MOL = 342.3


def estimate_water_activity(water_g: float, sugar_like_solids_g: float) -> float:
    """
    Estimate water activity (aw) using a simplified Norrish model.

    Model:
        1) Convert water mass and sugar-like solids mass to moles.
        2) Compute mole fraction of water:
               x_water = n_water / (n_water + n_solute)
        3) Apply Norrish-type equation:
               aw = x_water * exp( -K * (1 - x_water)^2 )

    Args:
        water_g:
            Mass of water in grams in the system.
        sugar_like_solids_g:
            Mass of sugar-like dissolved solids (e.g. sucrose, dextrose, syrups)
            in grams. DO NOT include fat, insoluble cocoa solids, or fibres here.

    Returns:
        float: Estimated water activity in the range [0.0, 1.0].
    """
    if water_g <= 0:
        return 0.0
    if sugar_like_solids_g <= 0:
        return 1.0
    moles_water = water_g / MW_WATER_G_PER_MOL
    moles_solute = sugar_like_solids_g / MW_SUCROSE_G_PER_MOL
    total_moles = moles_water + moles_solute
    if total_moles <= 0:
        return 0.0
    x_water = moles_water / total_moles
    x_solute = 1.0 - x_water
    exponent = -K_NORRISH_SUCROSE * x_solute**2
    aw_raw = x_water * math.exp(exponent)
    if aw_raw < 0.0:
        return 0.0
    if aw_raw > 1.0:
        return 1.0
    return aw_raw


def classify_aw(water_activity: float) -> str:
    """
    Classify water activity into risk bands for room temperature (20–25°C).

    Thresholds (MVP for pastes):
        Aw < 0.68       -> "Low"
        0.68–0.75       -> "Safe"
        0.75–0.85       -> "Risky"
        > 0.85          -> "Unsafe"

    Args:
        water_activity: Water activity value (0–1).

    Returns:
        str: One of "Low", "Safe", "Risky", "Unsafe".
    """
    if water_activity > 0.85:
        return "Unsafe"
    elif water_activity > 0.75:
        return "Risky"
    elif water_activity >= 0.68:
        return "Safe"
    else:
        return "Low"


def estimate_shelf_life_weeks(water_activity: float) -> int:
    """
    Roughly estimate shelf life in weeks based on water activity
    at ambient storage (20–25°C).

    This is a heuristic, not a regulatory standard.

    Args:
        water_activity: Water activity value (0–1).

    Returns:
        int: Estimated shelf life in weeks.
    """
    if water_activity > 0.85:
        return 1
    elif water_activity > 0.75:
        return 4
    elif water_activity >= 0.68:
        return 12
    else:
        return 16


if __name__ == "__main__":
    aw1 = estimate_water_activity(water_g=300, sugar_like_solids_g=500)
    print("Example 1 Aw:", round(aw1, 3), classify_aw(aw1))
    aw2 = estimate_water_activity(water_g=400, sugar_like_solids_g=400)
    print("Example 2 Aw:", round(aw2, 3), classify_aw(aw2))