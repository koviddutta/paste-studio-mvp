import logging
from typing import TypedDict, Literal, Any, Optional, Mapping
from app.calculators.property_calculator import FormulationProperties
from app.engines.ingredient_classifier import IngredientData
from app.engines.sop_generator import SOPStep
from app.calculators.gelato_science import (
    calculate_afp,
    calculate_sp,
    calculate_pac,
    calculate_characterization_pct,
    calculate_final_sugars_pct,
)
from app.database import supabase_client
from app.database.gelato_university_client import (
    ExtendedGelatoScienceConstants,
    ExtendedValidationThresholds,
    MSNFStabilizerBalance,
    get_formulation_type_from_ingredients,
    get_sugar_recommendations,
    calculate_texture_prediction,
)
from app.database.supabase_client import ValidationThresholds

ValidationStatus = Literal["OPTIMAL", "ACCEPTABLE", "CRITICAL"]


class ScientificValidationResult(TypedDict):
    """Result of a single scientific validation check."""

    framework_name: str
    status: ValidationStatus
    score: float
    measured_value: str
    target_range: str
    message: str
    explanation: str


class ScientificValidationReport(TypedDict):
    """Complete scientific validation report with confidence score."""

    overall_score: float
    overall_status: ValidationStatus
    validations: list[ScientificValidationResult]
    recommendations: list[str]


def _get_validation_status(
    value: float,
    thresholds: ValidationThresholds | ExtendedValidationThresholds | dict[str, float],
) -> tuple[ValidationStatus, float]:
    """Determines the status and score based on thresholds."""
    optimal_min = thresholds.get("optimal_min")
    optimal_max = thresholds.get("optimal_max")
    acceptable_min = thresholds.get("acceptable_min")
    acceptable_max = thresholds.get("acceptable_max")
    if optimal_min is not None and optimal_max is not None:
        if optimal_min <= value <= optimal_max:
            return ("OPTIMAL", 100.0)
    if acceptable_min is not None and acceptable_max is not None:
        if acceptable_min <= value <= acceptable_max:
            return ("ACCEPTABLE", 75.0)
    return ("CRITICAL", 30.0)


def calculate_confidence_score(
    validations: list[ScientificValidationResult],
) -> tuple[float, ValidationStatus]:
    """Calculate overall scientific confidence score (0-99%)."""
    weights = {
        "AFP Balance": 0.1,
        "SP & POD Balance": 0.1,
        "D.E. Balance": 0.1,
        "PAC Balance": 0.1,
        "Total Solids": 0.1,
        "Fat Emulsification": 0.1,
        "Safety & Shelf-life": 0.1,
        "MSNF & Stabilizer Balance": 0.1,
        "Characterization": 0.1,
        "Final Sugars": 0.05,
        "AFP Total": 0.1,
    }
    total_score = 0.0
    total_weight = 0.0
    for v in validations:
        framework_weight = weights.get(v["framework_name"], 0.0)
        total_score += v["score"] * framework_weight
        total_weight += framework_weight
    overall_score = (
        min(total_score / total_weight * 100, 99.0) if total_weight > 0 else 0
    )
    if overall_score >= 90:
        overall_status: ValidationStatus = "OPTIMAL"
    elif overall_score >= 70:
        overall_status = "ACCEPTABLE"
    else:
        overall_status = "CRITICAL"
    return (overall_score, overall_status)


def _find_threshold(
    param: str,
    formulation_type: str,
    thresholds: Mapping[str, list[ExtendedValidationThresholds] | ValidationThresholds],
) -> Optional[ExtendedValidationThresholds | ValidationThresholds]:
    """Finds the correct threshold object for a parameter and formulation type."""
    param_thresholds = thresholds.get(param)
    if not param_thresholds:
        return None
    if isinstance(param_thresholds, list):
        for t in param_thresholds:
            if t.get("formulation_type") == formulation_type:
                return t
        for t in param_thresholds:
            if t.get("formulation_type") == "default":
                return t
        return None
    if isinstance(param_thresholds, dict):
        return param_thresholds
    return None


def validate_formulation_scientifically(
    properties: FormulationProperties,
    classified_ingredients: list[IngredientData],
    sop: list[SOPStep],
    thresholds: Mapping[str, list[ExtendedValidationThresholds] | ValidationThresholds],
    gelato_constants: Mapping[str, ExtendedGelatoScienceConstants],
) -> ScientificValidationReport:
    """Runs the full suite of Gelato University scientific validation checks."""
    validations: list[ScientificValidationResult] = []
    formulation_type = get_formulation_type_from_ingredients(classified_ingredients)
    sugar_composition = {
        ing["name"].lower(): ing.get("mass_g", 0.0)
        for ing in classified_ingredients
        if ing["class_name"] == "C_SUGAR"
    }
    if not sugar_composition:
        sugar_composition = {"sucrose": properties["composition"].get("sugar_g", 0.0)}
    measured_afp = calculate_afp(sugar_composition, gelato_constants)
    measured_sp, measured_pod = calculate_sp(sugar_composition, gelato_constants)
    measured_de, texture, de_analysis = calculate_texture_prediction(
        sugar_composition, gelato_constants
    )
    recommendations = get_sugar_recommendations(
        measured_afp, measured_sp, formulation_type, thresholds
    )
    afp_thresh = _find_threshold("afp_total", formulation_type, thresholds)
    if afp_thresh:
        afp_status, afp_score = _get_validation_status(measured_afp, afp_thresh)
        validations.append(
            {
                "framework_name": "AFP Total",
                "status": afp_status,
                "score": afp_score,
                "measured_value": f"{measured_afp:.1f}",
                "target_range": f"{afp_thresh['acceptable_min']}-{afp_thresh['acceptable_max']}",
                "message": f"Total Anti-Freezing Power is {afp_status.lower()}.".capitalize(),
                "explanation": afp_thresh["explanation"],
            }
        )
    pod_thresh = _find_threshold("pod_sweetness", formulation_type, thresholds)
    if pod_thresh:
        pod_status, pod_score = _get_validation_status(measured_pod, pod_thresh)
        validations.append(
            {
                "framework_name": "SP & POD Balance",
                "status": pod_status,
                "score": pod_score,
                "measured_value": f"{measured_pod:.1f}%",
                "target_range": f"{pod_thresh['acceptable_min']}-{pod_thresh['acceptable_max']}%",
                "message": f"Sweetness level (POD) is {pod_status.lower()}.".capitalize(),
                "explanation": pod_thresh["explanation"],
            }
        )
    de_thresh = _find_threshold("de_total", formulation_type, thresholds)
    if de_thresh:
        de_status, de_score = _get_validation_status(measured_de, de_thresh)
        validations.append(
            {
                "framework_name": "D.E. Balance",
                "status": de_status,
                "score": de_score,
                "measured_value": f"{measured_de:.1f} ({texture})",
                "target_range": f"{de_thresh['acceptable_min']}-{de_thresh['acceptable_max']}",
                "message": f"Texture is predicted to be {texture.replace('_', ' ').lower()}.".capitalize(),
                "explanation": f"{de_thresh['explanation']} Analysis: {de_analysis}",
            }
        )
    pac_thresh = _find_threshold("pac_total", formulation_type, thresholds)
    if pac_thresh:
        measured_pac = calculate_pac(properties["composition"])
        pac_status, pac_score = _get_validation_status(measured_pac, pac_thresh)
        validations.append(
            {
                "framework_name": "PAC Balance",
                "status": pac_status,
                "score": pac_score,
                "measured_value": f"{measured_pac:.2f}°C",
                "target_range": f"{pac_thresh['acceptable_min']:.1f} to {pac_thresh['acceptable_max']:.1f}°C",
                "message": f"Freezing point depression is {pac_status.lower()}.".capitalize(),
                "explanation": pac_thresh["explanation"],
            }
        )
    solids_thresh = _find_threshold("solids_total", formulation_type, thresholds)
    if solids_thresh:
        total_solids_pct = 100.0 - properties["composition_pct"].get("water", 100.0)
        solids_status, solids_score = _get_validation_status(
            total_solids_pct, solids_thresh
        )
        validations.append(
            {
                "framework_name": "Total Solids",
                "status": solids_status,
                "score": solids_score,
                "measured_value": f"{total_solids_pct:.1f}%",
                "target_range": f"{solids_thresh['acceptable_min']}-{solids_thresh['acceptable_max']}%",
                "message": f"Total solids are {solids_status.lower()}.".capitalize(),
                "explanation": solids_thresh["explanation"],
            }
        )
    fat_thresh = _find_threshold("fat_total", formulation_type, thresholds)
    if fat_thresh:
        fat_pct = properties["composition_pct"].get("fat", 0.0)
        fat_status, fat_score = _get_validation_status(fat_pct, fat_thresh)
        validations.append(
            {
                "framework_name": "Fat Emulsification",
                "status": fat_status,
                "score": fat_score,
                "measured_value": f"{fat_pct:.1f}%",
                "target_range": f"{fat_thresh['acceptable_min']}-{fat_thresh['acceptable_max']}%",
                "message": f"Fat content is {fat_status.lower()}.".capitalize(),
                "explanation": fat_thresh["explanation"],
            }
        )
    balance_rules = supabase_client.fetch_msnf_stabilizer_thresholds().get(
        formulation_type
    )
    if balance_rules:
        total_g = properties["composition"]["total_g"]
        msnf_pct = (
            sum(
                (
                    ing.get("protein_pct", 0.0) * ing.get("mass_g", 0.0) / 100
                    + ing.get("other_g", 0.0) / 100
                    for ing in classified_ingredients
                    if ing["class_name"] == "A_DAIRY"
                )
            )
            / total_g
            * 10000
            if total_g > 0
            else 0
        )
        stabilizer_pct = (
            sum(
                (
                    ing.get("mass_g", 0.0)
                    for ing in classified_ingredients
                    if ing["class_name"] == "E_STABILIZER"
                )
            )
            / total_g
            * 100
            if total_g > 0
            else 0
        )
        msnf_status, msnf_score = _get_validation_status(msnf_pct, balance_rules)
        stabilizer_status, stabilizer_score = _get_validation_status(
            stabilizer_pct, balance_rules
        )
        avg_score = (msnf_score + stabilizer_score) / 2
        overall_status: ValidationStatus = (
            "CRITICAL"
            if "CRITICAL" in [msnf_status, stabilizer_status]
            else "ACCEPTABLE"
            if "ACCEPTABLE" in [msnf_status, stabilizer_status]
            else "OPTIMAL"
        )
        validations.append(
            {
                "framework_name": "MSNF & Stabilizer Balance",
                "status": overall_status,
                "score": avg_score,
                "measured_value": f"MSNF: {msnf_pct:.1f}%, Stb: {stabilizer_pct:.2f}%",
                "target_range": f"MSNF: {balance_rules['msnf_min_pct']}-{balance_rules['msnf_max_pct']}%, Stb: {balance_rules['stabilizer_min_pct']}-{balance_rules['stabilizer_max_pct']}%",
                "message": f"MSNF & Stabilizer balance is {overall_status.lower()}.".capitalize(),
                "explanation": balance_rules["explanation"],
            }
        )
    aw_thresh = _find_threshold("water_activity", formulation_type, thresholds)
    if aw_thresh:
        aw = properties.get("water_activity", 1.0)
        aw_status, aw_score = _get_validation_status(aw, aw_thresh)
        has_dairy = any(
            (ing["class_name"] == "A_DAIRY" for ing in classified_ingredients)
        )
        pasteurization_ok = not has_dairy or any(
            (
                "pasteurize" in step["action"].lower()
                and step.get("temperature_c", 0) >= 85
                for step in sop
            )
        )
        safety_score = (aw_score + (100.0 if pasteurization_ok else 30.0)) / 2
        safety_status: ValidationStatus = (
            "CRITICAL"
            if aw_status == "CRITICAL" or not pasteurization_ok
            else "ACCEPTABLE"
            if aw_status == "ACCEPTABLE"
            else "OPTIMAL"
        )
        validations.append(
            {
                "framework_name": "Safety & Shelf-life",
                "status": safety_status,
                "score": safety_score,
                "measured_value": f"Aw: {aw:.3f}",
                "target_range": f"Aw: {aw_thresh['acceptable_min']}-{aw_thresh['acceptable_max']}",
                "message": f"Shelf-life safety is {safety_status.lower()}.".capitalize(),
                "explanation": f"{aw_thresh['explanation']}. Pasteurization: {('OK' if pasteurization_ok else 'MISSING')}",
            }
        )
        if not pasteurization_ok and has_dairy:
            recommendations.append(
                "CRITICAL: Add a pasteurization step (85°C for 30s) for dairy safety."
            )
    overall_score, overall_status = calculate_confidence_score(validations)
    return {
        "overall_score": overall_score,
        "overall_status": overall_status,
        "validations": validations,
        "recommendations": recommendations,
    }