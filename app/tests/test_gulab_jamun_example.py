import unittest
import logging
from app.paste_core.examples.gulab_jamun import build_gulab_jamun_example


class TestGulabJamunExample(unittest.TestCase):
    """
    Test suite for verifying the Gulab Jamun paste formulation example.
    Ensures the calculated composition falls within acceptable ranges for a stable paste.
    """

    def setUp(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def test_gulab_jamun_paste_composition(self):
        """
        Validates that the Gulab Jamun paste composition meets target specifications:
        - Sugars: 30-60%
        - Fat: 5-25%
        - Solids: 60-85%
        - Water Activity: 0.6-0.95
        """
        self.logger.info("🧪 Starting Gulab Jamun Composition Test...")
        result = build_gulab_jamun_example()
        comp = result["composition"]
        self.logger.info(f"📊 Calculated Composition: {comp}")
        self.assertGreaterEqual(
            comp.total_sugars_pct,
            30.0,
            f"❌ Sugar content {comp.total_sugars_pct}% is too low (min 30%)",
        )
        self.assertLessEqual(
            comp.total_sugars_pct,
            60.0,
            f"❌ Sugar content {comp.total_sugars_pct}% is too high (max 60%)",
        )
        self.logger.info(f"✅ Sugars: {comp.total_sugars_pct}% (Target: 30-60%)")
        self.assertGreaterEqual(
            comp.total_fat_pct,
            5.0,
            f"❌ Fat content {comp.total_fat_pct}% is too low (min 5%)",
        )
        self.assertLessEqual(
            comp.total_fat_pct,
            25.0,
            f"❌ Fat content {comp.total_fat_pct}% is too high (max 25%)",
        )
        self.logger.info(f"✅ Fat: {comp.total_fat_pct}% (Target: 5-25%)")
        self.assertGreaterEqual(
            comp.total_solids_pct,
            60.0,
            f"❌ Total solids {comp.total_solids_pct}% is too low (min 60%)",
        )
        self.assertLessEqual(
            comp.total_solids_pct,
            85.0,
            f"❌ Total solids {comp.total_solids_pct}% is too high (max 85%)",
        )
        self.logger.info(f"✅ Solids: {comp.total_solids_pct}% (Target: 60-85%)")
        self.assertGreaterEqual(
            comp.water_activity,
            0.6,
            f"❌ Water activity {comp.water_activity} is too low (min 0.6)",
        )
        self.assertLessEqual(
            comp.water_activity,
            0.95,
            f"❌ Water activity {comp.water_activity} is too high (max 0.95)",
        )
        self.logger.info(f"✅ Water Activity: {comp.water_activity} (Target: 0.6-0.95)")
        self.logger.info("✨ Gulab Jamun composition validation passed successfully.")


if __name__ == "__main__":
    unittest.main()