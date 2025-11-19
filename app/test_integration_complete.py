import sys
import os
import time
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.database import supabase_client
from app.database.ingredient_mapper import get_recipe_with_classified_ingredients
from app.engines.ingredient_classifier import classify_ingredient
from app.engines.sop_generator import generate_sop
from app.calculators.property_calculator import calculate_all_properties
from app.validators.formulation_validator import validate_formulation

logging.basicConfig(
    level=logging.WARNING, format="%(asctime)s - %(levelname)s - %(message)s"
)


class TestResult:
    """A simple class to hold test results."""

    def __init__(self):
        self.passed = True
        self.message = ""


def run_test(test_func, description):
    """Helper function to run a test, time it, and print results."""
    print(f"\n{'=' * 20} RUNNING TEST: {description} {'=' * 20}")
    start_time = time.time()
    try:
        result = test_func()
        end_time = time.time()
        if result.passed:
            print(
                f"\x1b[92m✅ PASS\x1b[0m - {result.message} (took {end_time - start_time:.4f}s)"
            )
            return True
        else:
            print(
                f"\x1b[91m❌ FAIL\x1b[0m - {result.message} (took {end_time - start_time:.4f}s)"
            )
            return False
    except Exception as e:
        end_time = time.time()
        print(
            f"\x1b[91m❌ ERROR\x1b[0m - An unexpected error occurred: {e} (took {end_time - start_time:.4f}s)"
        )
        logging.exception("Test failed due to an exception.")
        return False


def test_db_connection_and_setup():
    """Tests Supabase connection and verifies all required tables exist."""
    result = TestResult()
    if not supabase_client.supabase:
        result.passed = False
        result.message = "Supabase client could not be initialized. Check .env file for SUPABASE_URL and SUPABASE_KEY."
        return result
    db_validation = supabase_client.validate_database_setup()
    if not all(db_validation.values()):
        missing_tables = [k for k, v in db_validation.items() if not v]
        result.passed = False
        result.message = f"Database setup is incomplete. Missing tables: {', '.join(missing_tables)}. Please run the SQL script in 'app/database/schema.sql' in your Supabase dashboard."
        return result
    result.message = (
        "Supabase connection is active and all required tables are present."
    )
    return result


def test_recipe_search():
    """Tests the ability to search for recipes."""
    result = TestResult()
    recipes = supabase_client.search_recipes("Gulab Jamun")
    if recipes and any(("Gulab Jamun" in r["name"] for r in recipes)):
        result.message = "Successfully found 'Gulab Jamun' in recipe search."
        return result
    else:
        all_recipes = supabase_client.search_recipes("a", limit=1)
        if all_recipes:
            result.passed = True
            result.message = (
                "Could not find 'Gulab Jamun', but successfully fetched another recipe."
            )
            return result
        else:
            result.passed = False
            result.message = "Failed to find 'Gulab Jamun' and could not fetch any other recipe from 'desserts_master_v2'."
            return result


def test_ingredient_classification():
    """Tests that ingredients from a recipe can be successfully classified."""
    result = TestResult()
    classified_recipe = get_recipe_with_classified_ingredients("Gulab Jamun")
    if not classified_recipe:
        all_recipes = supabase_client.search_recipes("a", limit=1)
        if not all_recipes:
            result.passed = False
            result.message = "Could not fetch any recipe to test classification."
            return result
        recipe_name = all_recipes[0]["name"]
        classified_recipe = get_recipe_with_classified_ingredients(recipe_name)
    if not classified_recipe:
        result.passed = False
        result.message = f"Failed to fetch or classify recipe."
        return result
    if classified_recipe["unclassified_count"] > 0:
        result.passed = False
        result.message = f"{classified_recipe['unclassified_count']} ingredients could not be classified. Check 'ingredient_mapping' table."
        return result
    result.message = f"Successfully classified all ingredients for recipe '{classified_recipe['recipe_name']}'."
    return result


def test_full_formulation_pipeline():
    """Tests the entire formulation generation pipeline from end to end."""
    result = TestResult()
    recipe_name = "Gulab Jamun Recipe With Khoya"
    batch_size_kg = 1.0
    classified_recipe = get_recipe_with_classified_ingredients(recipe_name)
    if not classified_recipe:
        result.passed = False
        result.message = (
            f"Could not find or process recipe '{recipe_name}' to start the pipeline."
        )
        return result
    ingredients_with_mass = []
    recipe_total_mass = classified_recipe["total_mass_grams"]
    if recipe_total_mass <= 0:
        result.passed = False
        result.message = f"Recipe '{recipe_name}' has zero total mass, cannot proceed."
        return result
    scaling_factor = batch_size_kg * 1000 / recipe_total_mass
    for ing in classified_recipe["ingredients"]:
        classified_data = classify_ingredient(ing["canonical_name"])
        if classified_data:
            classified_data["mass_g"] = ing["quantity_grams"] * scaling_factor
            ingredients_with_mass.append(classified_data)
    properties = calculate_all_properties(ingredients_with_mass, batch_size_kg * 1000)
    if not properties or properties.get("water_activity") is None:
        result.passed = False
        result.message = "Property calculation failed."
        return result
    sop, _ = generate_sop(ingredients_with_mass)
    if not sop:
        result.passed = False
        result.message = "SOP generation failed."
        return result
    validation_report = validate_formulation(properties, ingredients_with_mass)
    if not validation_report:
        result.passed = False
        result.message = "Formulation validation failed."
        return result
    result.message = f"Full pipeline successful for '{recipe_name}'. Aw: {properties['water_activity']:.3f}, SOP Steps: {len(sop)}, Validation: {validation_report['overall_status']}."
    return result


def test_error_handling():
    """Tests expected failures for non-existent recipes and invalid inputs."""
    result = TestResult()
    non_existent = get_recipe_with_classified_ingredients("NonExistentRecipe12345")
    if non_existent is not None:
        result.passed = False
        result.message = "Error handling failed: A non-existent recipe was found."
        return result
    props = calculate_all_properties([], 0)
    if props is None:
        result.passed = False
        result.message = "Error handling failed: `calculate_all_properties` failed with zero batch size."
        return result
    result.message = (
        "Successfully handled non-existent recipe and invalid batch size gracefully."
    )
    return result


def main():
    """Main function to run all integration tests."""
    print("""
*** Paste Studio MVP - Complete Integration Test Suite ***""")
    print(
        "This script will test the full application pipeline against your Supabase instance."
    )
    print("Ensure your .env file is correctly configured.")
    if not run_test(
        test_db_connection_and_setup, "Database Connection & Setup Verification"
    ):
        print("""
\x1b[91mCritical test failed. Aborting further tests.\x1b[0m""")
        sys.exit(1)
    tests_to_run = [
        (test_recipe_search, "Recipe Search Functionality"),
        (test_ingredient_classification, "Ingredient Classification Mapping"),
        (test_full_formulation_pipeline, "Full Formulation Generation Pipeline"),
        (test_error_handling, "Error Handling for Invalid Inputs"),
    ]
    results = [run_test(func, desc) for func, desc in tests_to_run]
    passed_count = sum(results)
    total_count = len(results)
    print(f"\n{'=' * 20} TEST SUMMARY {'=' * 20}")
    print(f"Tests Passed: {passed_count}/{total_count}")
    if passed_count == total_count:
        print("\x1b[92m✅ All integration tests passed successfully!\x1b[0m")
    else:
        print(
            "\x1b[91m❌ Some integration tests failed. Please review the output above.\x1b[0m"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()