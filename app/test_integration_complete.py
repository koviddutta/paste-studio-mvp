import asyncio
import logging
from app.services.sweet_to_paste_engine import SweetToPasteEngine
from app.validators.formulation_validator import FormulationValidator
from app.database.ingredient_mapper import IngredientMapper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_full_flow():
    """
    Runs a complete integration test simulating the formulation of a recipe.
    """
    print("""
🚀 STARTING INTEGRATION TEST: Sweet -> Paste Formulation
""")
    test_recipe = {
        "name": "Test Gulab Jamun Base",
        "ingredients": [
            {"name": "Milk Powder", "quantity": 100},
            {"name": "Maida", "quantity": 30},
            {"name": "Ghee", "quantity": 10},
            {"name": "Milk", "quantity": 50},
        ],
    }
    print(f"📝 Input Recipe: {test_recipe['name']}")
    try:
        print("""
⚙️  Running SweetToPasteEngine...""")
        result = await SweetToPasteEngine.process_recipe(test_recipe, batch_size_kg=1.0)
        print("""
✅ Engine Processing Complete.""")
        comp = result["composition"]
        print(f"\n📊 Calculated Composition:")
        print(f"   - Fat: {comp['fat']}%")
        print(f"   - Sugar: {comp['sugar']}%")
        print(f"   - Moisture: {comp['moisture']}%")
        print(f"   - Protein: {comp['protein']}%")
        props = result["properties"]
        print(f"\n🔬 Calculated Properties:")
        print(f"   - Water Activity (aw): {props['water_activity']}")
        print(f"   - Shelf Life: {props['shelf_life_weeks']} weeks")
        print(f"   - Viscosity: {props['viscosity_pa_s']} Pa.s")
        print("""
🛡️  Running Validators...""")
        validations = FormulationValidator.validate_formulation(result)
        for v in validations:
            status_icon = (
                "✅"
                if v["status"] == "PASS"
                else "⚠️"
                if v["status"] == "WARNING"
                else "❌"
            )
            print(f"   {status_icon} [{v['status']}] {v['check']}: {v['msg']}")
        print(f"\n📋 Generated SOP ({len(result['sop'])} steps):")
        for step in result["sop"]:
            print(f"   {step['step']}. {step['phase']}: {step['action']}")
        print("""
✨ INTEGRATION TEST PASSED SUCCESSFULLY! ✨""")
        return True
    except Exception as e:
        logger.exception("Test Failed")
        print(f"\n❌ TEST FAILED: {e}")
        return False


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_full_flow())