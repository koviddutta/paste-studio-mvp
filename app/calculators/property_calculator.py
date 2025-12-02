from app.calculators.water_activity import WaterActivityCalculator
from app.calculators.viscosity import ViscosityCalculator
from app.calculators.gelato_science import GelatoScience
from app.constants.gelato_science_constants import GelatoConstants


class PropertyCalculator:
    """
    Aggregator for all physical and chemical property calculations.
    """

    @staticmethod
    def calculate_all_properties(composition: dict) -> dict:
        """
        Takes composition (fat, sugar, moisture, protein percents) and returns complete property profile.
        """
        moisture = composition.get("moisture", 0)
        sugar = composition.get("sugar", 0)
        fat = composition.get("fat", 0)
        protein = composition.get("protein", 0)
        total_solids = 100 - moisture
        moles_water = moisture / 18.0
        moles_sugar = sugar / 342.0
        total_moles = moles_water + moles_sugar
        x_water = moles_water / total_moles if total_moles > 0 else 0
        x_sugar = moles_sugar / total_moles if total_moles > 0 else 0
        aw = WaterActivityCalculator.calculate_aw(x_water, {"sugar": x_sugar})
        shelf_life = WaterActivityCalculator.estimate_shelf_life_weeks(aw)
        viscosity = ViscosityCalculator.calculate_viscosity(total_solids, 25.0)
        dosage = GelatoScience.calculate_dosage(sugar)
        return {
            "water_activity": aw,
            "shelf_life_weeks": shelf_life,
            "viscosity_pa_s": viscosity,
            "dosage_g_kg": dosage,
            "afp": GelatoScience.calculate_afp(sugar),
            "sp": GelatoScience.calculate_sp(sugar),
        }