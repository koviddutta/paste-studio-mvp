from typing import TypedDict, Literal
from app.calculators.property_calculator import FormulationProperties
from app.engines.ingredient_classifier import IngredientData

ValidationStatus = Literal["PASS", "WARNING", "FAIL"]


class ValidationResult(TypedDict):
    """Represents the result of a formulation validation check."""

    status: ValidationStatus
    message: str


class FullValidationReport(TypedDict):
    """Contains the overall validation status and a list of all checks."""

    overall_status: ValidationStatus
    results: list[ValidationResult]


def validate_formulation(
    properties: FormulationProperties, classified_ingredients: list[IngredientData]
) -> FullValidationReport:
    """Runs a series of validation checks on the formulation properties and composition.

    Args:
        properties: The calculated properties of the formulation.
        classified_ingredients: A list of ingredients with their classifications.

    Returns:
        A full validation report with an overall status and detailed results.
    """
    results: list[ValidationResult] = []
    overall_status: ValidationStatus = "PASS"
    aw = properties.get("water_activity")
    if aw is not None:
        if not 0.68 <= aw <= 0.75:
            status: ValidationStatus = "FAIL" if aw > 0.85 else "WARNING"
            results.append(
                {
                    "status": status,
                    "message": f"Water Activity is {aw:.3f}, outside the optimal range of 0.68-0.75. Shelf life is compromised.",
                }
            )
            if status == "FAIL":
                overall_status = "FAIL"
            elif overall_status != "FAIL":
                overall_status = "WARNING"
        else:
            results.append(
                {
                    "status": "PASS",
                    "message": f"Water Activity is {aw:.3f}, within the optimal range.",
                }
            )
    sugar_pct = properties["composition_pct"].get("sugar", 0.0)
    if not 20.0 <= sugar_pct <= 40.0:
        results.append(
            {
                "status": "WARNING",
                "message": f"Sugar content is {sugar_pct:.1f}%, outside the typical range of 20-40%.",
            }
        )
        if overall_status != "FAIL":
            overall_status = "WARNING"
    else:
        results.append(
            {
                "status": "PASS",
                "message": f"Sugar content is {sugar_pct:.1f}%, within range.",
            }
        )
    fat_pct = properties["composition_pct"].get("fat", 0.0)
    if not 10.0 <= fat_pct <= 20.0:
        results.append(
            {
                "status": "WARNING",
                "message": f"Fat content is {fat_pct:.1f}%, outside the typical range of 10-20%.",
            }
        )
        if overall_status != "FAIL":
            overall_status = "WARNING"
    else:
        results.append(
            {
                "status": "PASS",
                "message": f"Fat content is {fat_pct:.1f}%, within range.",
            }
        )
    stabilizer_mass = sum(
        (
            ing.get("mass_g", 0.0)
            for ing in classified_ingredients
            if ing.get("class_name") == "E_STABILIZER"
        )
    )
    total_mass = properties["composition"].get("total_g", 0.0)
    if total_mass > 0:
        stabilizer_pct = stabilizer_mass / total_mass * 100
        if not 0.25 <= stabilizer_pct <= 0.5 and stabilizer_mass > 0:
            results.append(
                {
                    "status": "WARNING",
                    "message": f"Stabilizer content is {stabilizer_pct:.2f}%, outside the recommended range of 0.25-0.50%.",
                }
            )
            if overall_status != "FAIL":
                overall_status = "WARNING"
        elif stabilizer_mass > 0:
            results.append(
                {
                    "status": "PASS",
                    "message": f"Stabilizer content is {stabilizer_pct:.2f}%, within range.",
                }
            )
    if not results:
        results.append({"status": "PASS", "message": "All checks passed."})
    return {"overall_status": overall_status, "results": results}