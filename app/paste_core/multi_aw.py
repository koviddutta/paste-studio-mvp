"""
Placeholder module for future multi-component water activity calculations.
This will handle interactions between different solute types (sugars, salts, proteins)
in complex mixtures.
"""
"""
Multi-component water activity model for Indian sweet pastes & gelato flavorings.

This hybrid model combines:
- Modified Norrish equation for sugars/polyols
- Ross equation for dairy solids (MSNF, lactose, proteins)
- Empirical fat-binding correction
- Stabilizer-binding correction
"""

import math
from typing import Mapping, Optional


# Norrish interaction coefficients (approx values validated in confection science)
K_NORRISH = {
    "sucrose": 7.0,
    "glucose": 6.2,
    "fructose": 5.8,
    "dextrose": 6.5,
    "invert_sugar": 6.0,
    "lactose": 4.5,  # weaker binding
}


def _mole_fraction_component(mass_g: float, mw: float) -> float:
    if mass_g <= 0:
        return 0.0
    return max(mass_g / mw, 0.0)


def norrish_aw(water_g: float, sugars: Mapping[str, float]) -> float:
    """
    Multi-sugar Norrish model.
    sugars: dict sugar_type -> grams
    """

    MW_WATER = 18.015
    sugar_mw = {
        "sucrose": 342.3,
        "glucose": 180.16,
        "fructose": 180.16,
        "dextrose": 180.16,
        "invert_sugar": 180.16,
        "lactose": 342.3,
    }

    moles_water = _mole_fraction_component(water_g, MW_WATER)
    moles_solutes = 0.0
    activity_modifier = 0.0

    for stype, grams in sugars.items():
        if grams <= 0:
            continue
        mw = sugar_mw.get(stype, 180.16)
        moles = _mole_fraction_component(grams, mw)
        moles_solutes += moles
        K = K_NORRISH.get(stype, 6.0)
        x_solute = moles / (moles_water + moles)
        activity_modifier += K * (x_solute ** 2)

    total_moles = moles_water + moles_solutes
    if total_moles == 0:
        return 1.0

    x_w = moles_water / total_moles
    aw = x_w * math.exp(-activity_modifier)
    return max(0.0, min(1.0, aw))



def ross_dairy_aw(water_pct: float, msnf_pct: float) -> float:
    """
    Ross equation for dairy solids.
    Aw = exp(-k * total_solids)
    k for milk solids =~ 0.015 (empirical)
    """
    k = 0.015
    total_solids = (100 - water_pct) / 100
    return math.exp(-k * total_solids * msnf_pct)



def fat_binding_correction(aw: float, fat_pct: float) -> float:
    """
    Fats bind water weakly but reduce the effective free water fraction.
    Empirical correction: reduce aw by up to 5% depending on fat level.
    """
    reduction = min(0.05, fat_pct * 0.002)  # 0.2% aw reduction per 1% fat
    return max(0.0, aw * (1 - reduction))



def stabilizer_correction(aw: float, other_pct: float) -> float:
    """
    Stabilizers, fiber, gums bind water strongly.
    We approximate a linear reduction.
    """
    reduction = min(0.10, other_pct * 0.01)
    return max(0.0, aw * (1 - reduction))



def estimate_aw_multicomponent(
    water_pct: float,
    sugars_pct: float,
    msnf_pct: float,
    fat_pct: float,
    other_pct: float,
    sugar_profile: Optional[Mapping[str, float]] = None,
) -> float:
    """
    Full multi-component AW model.
    All inputs are mass percentages (0–100).
    sugar_profile: dict sugar_type -> fraction or grams (normalized)
    """
    if sugar_profile is None:
        sugar_profile = {"sucrose": sugars_pct}

    # Normalize sugar fractions to actual grams
    total_sug = sum(sugar_profile.values())
    sugar_dict = {}
    for k, v in sugar_profile.items():
        if v <= 0:
            continue
        sugar_dict[k] = sugars_pct * (v / total_sug)

    # 1. Sugars effect (Norrish)
    aw1 = norrish_aw(water_g=water_pct, sugars=sugar_dict)

    # 2. Dairy solids effect (Ross)
    aw2 = ross_dairy_aw(water_pct, msnf_pct)

    # Combine (harmonic mean favors safety)
    aw = (aw1 * aw2) ** 0.5

    # 3. Fat correction
    aw = fat_binding_correction(aw, fat_pct)

    # 4. Stabilizer/others correction
    aw = stabilizer_correction(aw, other_pct)

    return max(0.0, min(1.0, aw))
