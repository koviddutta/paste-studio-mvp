"""
Sugar science calculations for the Paste Core module.

This module handles the calculation of:
- AFP (Anti-Freezing Power) / PAC (Potere Anti-Congelante)
- POD (Sweetening Power / Potere Dolcificante)
- DE (Dextrose Equivalent) for glucose syrups

These metrics are critical for:
1. Controlling the hardness/scoopability of the gelato (PAC/AFP).
2. Balancing the sweetness profile (POD).
3. Managing freezing point depression.
"""

from dataclasses import dataclass


@dataclass
class SugarProperties:
    name: str
    pod: float
    pac: float
    solids: float


SUGAR_LIBRARY = {
    "sucrose": SugarProperties("Sucrose", 1.0, 1.0, 1.0),
    "dextrose": SugarProperties("Dextrose", 0.7, 1.9, 1.0),
    "glucose_syrup_de40": SugarProperties("Glucose DE40", 0.3, 0.8, 0.8),
    "fructose": SugarProperties("Fructose", 1.7, 1.9, 1.0),
    "lactose": SugarProperties("Lactose", 0.16, 1.0, 1.0),
    "honey": SugarProperties("Honey", 1.3, 1.9, 0.82),
    "invert_sugar": SugarProperties("Invert Sugar", 1.3, 1.9, 1.0),
    "maltodextrin": SugarProperties("Maltodextrin", 0.1, 0.5, 0.95),
}


def get_sugar_properties(sugar_name: str) -> SugarProperties:
    """
    Retrieves properties for a known sugar type.
    Defaults to Sucrose if unknown.
    """
    key = sugar_name.lower().replace(" ", "_")
    return SUGAR_LIBRARY.get(key, SUGAR_LIBRARY["sucrose"])


def calculate_net_pod(sugar_mix: dict[str, float]) -> float:
    """
    Calculates the weighted average POD of a mix of sugars.

    Args:
        sugar_mix: Dict of {sugar_name: weight_g}

    Returns:
        float: Total POD units contributed.
    """
    total_pod = 0.0
    for name, weight in sugar_mix.items():
        props = get_sugar_properties(name)
        total_pod += weight * props.pod
    return total_pod


def calculate_net_pac(sugar_mix: dict[str, float]) -> float:
    """
    Calculates the weighted average PAC (AFP) of a mix of sugars.

    Args:
        sugar_mix: Dict of {sugar_name: weight_g}

    Returns:
        float: Total PAC units contributed.
    """
    total_pac = 0.0
    for name, weight in sugar_mix.items():
        props = get_sugar_properties(name)
        total_pac += weight * props.pac
    return total_pac


def estimate_molecular_weight_from_de(de: float) -> float:
    """
    Estimates average molecular weight of a glucose syrup based on DE (Dextrose Equivalent).

    Formula approximation:
    MW = 18016 / DE

    Args:
        de: Dextrose Equivalent (0-100)

    Returns:
        float: Estimated Molecular Weight
    """
    if de <= 0:
        return 10000.0
    return 18016.0 / de