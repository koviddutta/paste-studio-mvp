import math
import logging
from app.constants.gelato_science_constants import GelatoConstants


class ViscosityCalculator:
    """
    Calculates viscosity using Power Law and Arrhenius models.
    """

    @staticmethod
    def calculate_viscosity(total_solids_pct: float, temperature_c: float) -> float:
        """
        Estimates viscosity in Pa.s using a simplified Kruger-Dougherty model for dispersion
        and Arrhenius for temperature dependence.
        """
        if total_solids_pct < 1:
            return 0.001
        if total_solids_pct > 99:
            return 1000.0
        phi = total_solids_pct / 100.0
        phi_max = 0.8
        if phi >= phi_max:
            return 1000.0
        try:
            base = 1 - phi / phi_max
            if base <= 0:
                rel_viscosity = 10000.0
            else:
                rel_viscosity = base ** (-2.5)
        except Exception:
            logging.exception("Error calculating relative viscosity")
            rel_viscosity = 10000.0
        try:
            base_viscosity = 0.001 * rel_viscosity
            ref_temp_k = 293.15
            target_temp_k = temperature_c + 273.15
            Ea_R = 2500
            temp_factor = math.exp(Ea_R * (1 / target_temp_k - 1 / ref_temp_k))
            viscosity = base_viscosity * temp_factor
            shear_rate = 50
            n = GelatoConstants.FLOW_INDEX_N
            apparent_viscosity = viscosity * shear_rate ** (n - 1)
            return round(apparent_viscosity, 2)
        except Exception:
            logging.exception("Error calculating final viscosity")
            return 10.0