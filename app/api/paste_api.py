from app.services.design_paste_from_sweet import design_paste_for_sweet_id
from app.paste_core.base_profiles import (
    white_base_profile,
    kulfi_base_profile,
    chocolate_base_profile,
)
from app.paste_core.gelato_infusion import recommend_paste_in_gelato


def get_base_profile(base_name: str):
    base_name = (base_name or "").lower()
    if base_name == "white":
        return white_base_profile()
    if base_name == "kulfi":
        return kulfi_base_profile()
    if base_name == "chocolate":
        return chocolate_base_profile()
    return white_base_profile()


def design_paste_and_infusion(
    sweet_id: int, base_name: str = "white", batch_weight_g: float = 1000.0
) -> dict:
    designed = design_paste_for_sweet_id(
        sweet_id=sweet_id, batch_weight_g=batch_weight_g
    )
    base = get_base_profile(base_name)
    rec = recommend_paste_in_gelato(
        paste_metrics=designed.metrics,
        base_profile=base,
        sweet_profile=designed.sweet_profile,
    )
    m = designed.metrics
    v = designed.validation
    return {
        "sweet_name": designed.sweet_profile.sweet_name,
        "base_name": base.name,
        "sweet_pct": designed.sweet_pct,
        "base_pct": designed.base_pct,
        "metrics": {
            "sugar_pct": m.sugar_pct,
            "fat_pct": m.fat_pct,
            "msnf_pct": m.msnf_pct,
            "other_pct": m.other_pct,
            "solids_pct": m.solids_pct,
            "water_pct": m.water_pct,
            "water_activity": m.water_activity,
            "afp_total": m.afp_total,
            "pod_sweetness": m.pod_sweetness,
            "de_total": m.de_total,
            "pac_total": m.pac_total,
        },
        "validation": {
            "overall_status": v.overall_status,
            "parameters": [
                {
                    "name": p.name,
                    "value": p.value,
                    "status": p.status,
                    "message": p.message,
                }
                for p in v.parameters
            ],
            "key_recommendations": v.key_recommendations,
        },
        "infusion": {
            "science_max": rec.p_science_max,
            "recommended_max": rec.p_recommended_max,
            "recommended_default": rec.p_recommended_default,
            "limits": rec.science_limits,
            "commentary": rec.commentary,
        },
    }