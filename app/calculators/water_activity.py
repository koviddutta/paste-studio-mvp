import math
import logging
from app.constants.gelato_science_constants import GelatoConstants


class WaterActivityCalculator:
    """
    Calculates Water Activity (aw) using the Norrish Equation.
    aw = Xw * exp(-K * Xs^2)
    """

    @staticmethod
    def calculate_aw(water_fraction: float, solute_fractions: dict) -> float:
        """
        Args:
            water_fraction: Mole fraction of water
            solute_fractions: Dict of {solute_type: mole_fraction}
                             e.g., {'sugar': 0.2, 'protein': 0.05}
        Returns:
            float: Estimated water activity (0.0 - 1.0)
        """
        if water_fraction <= 0:
            return 0.0
        if water_fraction >= 1:
            return 1.0
        exponent_sum = 0.0
        if "sugar" in solute_fractions:
            x_sugar = solute_fractions["sugar"]
            exponent_sum += GelatoConstants.K_SUGAR * x_sugar**2
        if "protein" in solute_fractions:
            x_protein = solute_fractions["protein"]
            exponent_sum += GelatoConstants.K_PROTEIN * x_protein**2
        try:
            aw = water_fraction * math.exp(-exponent_sum)
            return round(min(max(aw, 0.0), 1.0), 3)
        except OverflowError:
            logging.exception("Overflow error in calculate_aw")
            return 0.0

    @staticmethod
    def estimate_shelf_life_weeks(aw: float) -> int:
        """
        Estimates shelf life based on Aw at standard storage temps.
        """
        if aw > 0.85:
            return 1
        elif aw > 0.8:
            return 2
        elif aw > 0.75:
            return 4
        elif aw >= 0.68:
            return 12
        else:
            return 16