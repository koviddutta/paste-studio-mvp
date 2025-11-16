import math
from typing import TypedDict
import logging


class ViscosityParams(TypedDict):
    """Parameters for viscosity calculation."""

    sugar_concentration_pct: float
    temperature_c: float


def calculate_viscosity(
    params: ViscosityParams, constants: dict[str, float]
) -> float | None:
    """Estimates the apparent viscosity of a sugar solution at a given temperature.

    This function uses a simplified model combining the Power Law for shear thinning
    and an Arrhenius-like equation for temperature dependence. It is an estimation.

    Args:
        params: Dictionary containing sugar concentration and temperature.
        constants: Dictionary of formulation constants from the database.

    Returns:
        The estimated viscosity in Pascal-seconds (Pa·s), or None on error.
    """
    k_consistency = constants.get("VISC_K_CONSISTENCY", 0.5)
    n_flow_index = constants.get("VISC_N_FLOW_INDEX", 0.8)
    e_activation = constants.get("VISC_E_ACTIVATION", 20000)
    shear_rate = constants.get("VISC_SHEAR_RATE", 10.0)
    ref_temp_k = constants.get("VISC_REF_TEMP_K", 293.15)
    gas_constant = 8.314
    sugar_conc = params.get("sugar_concentration_pct", 0.0) / 100.0
    temp_k = params.get("temperature_c", 25.0) + 273.15
    if temp_k <= 0:
        logging.error(
            "Temperature must be above absolute zero for viscosity calculation."
        )
        return None
    try:
        conc_factor = math.exp(2.5 * sugar_conc)
        temp_factor = math.exp(
            e_activation / gas_constant * (1 / temp_k - 1 / ref_temp_k)
        )
        base_viscosity = k_consistency * shear_rate ** (n_flow_index - 1)
        viscosity = base_viscosity * conc_factor * temp_factor
        return max(0.001, viscosity)
    except (OverflowError, ValueError) as e:
        logging.exception(f"Error during viscosity calculation: {e}")
        return None