from app.constants.gelato_science_constants import GelatoConstants


class GelatoScience:
    """
    Core scientific calculations for gelato formulation.
    """

    @staticmethod
    def calculate_dosage(sugar_pct: float) -> int:
        """
        Calculates suggested dosage in g/kg of base mix.
        Inverse relationship with sugar content.
        Formula: 3500 / sugar_pct
        """
        if sugar_pct <= 0:
            return 100
        dosage = 3500 / sugar_pct
        return int(min(max(dosage, 30), 250))

    @staticmethod
    def calculate_afp(sugar_pct: float, alcohol_pct: float = 0) -> float:
        """
        Anti-Freezing Power calculation.
        Sucrose = 1.0 baseline.
        """
        return round(sugar_pct * 1.0 + alcohol_pct * 1.9, 1)

    @staticmethod
    def calculate_sp(sugar_pct: float) -> float:
        """
        Sweetening Power calculation.
        """
        return round(sugar_pct * 1.0, 1)