"""
Sweet Profiler logic for the Paste Core module.
Placeholder for future implementation of custom sweet profiling and categorization logic.
"""

from __future__ import annotations
from app.database.supabase_client import get_supabase
from .domain import SweetProfile


def _map_category_to_formulation_type(category: str) -> str:
    category = (category or "").lower()
    if "dairy_fried_sugary" in category:
        return "sweet_paste"
    if "gulab" in category or "jalebi" in category or "mithai" in category:
        return "sweet_paste"
    if "nut" in category:
        return "eggs_nuts"
    if "chocolate" in category or "cocoa" in category:
        return "cocoa_chocolate"
    if "sorbet" in category or "fruit" in category:
        return "fruit_sorbet"
    if "dairy" in category:
        return "pure_dairy"
    return "default"


def _infer_intensity_tag(sugars_pct: float, afp_per_100g: float) -> str:
    if sugars_pct >= 45 or afp_per_100g >= 25:
        return "strong"
    if sugars_pct <= 30 and afp_per_100g <= 18:
        return "weak"
    return "medium"


def _make_band(center: float | None, rel_tol: float = 0.15) -> tuple[float, float]:
    """
    Take a single target value from DB and create a [min, max] band around it.
    rel_tol = 0.15 → ±15% of the value.
    """
    if center is None:
        return (0.0, 0.0)
    c = float(center)
    delta = abs(c * rel_tol)
    return (c - delta, c + delta)


def build_sweet_profile_from_db(sweet_id: int) -> SweetProfile:
    """
    Build a SweetProfile by:
      1) Loading sweet_compositions row by id
      2) Using sweet_name to find corresponding sweet_paste_profiles row
      3) Converting single target_*_pct values into min/max bands
    """
    supabase = get_supabase()
    comp_resp = (
        supabase.table("sweet_compositions")
        .select("*")
        .eq("id", sweet_id)
        .single()
        .execute()
    )
    comp_row = comp_resp.data
    if not comp_row:
        raise ValueError(f"sweet_compositions: sweet id {sweet_id} not found")
    sweet_name = comp_row.get("sweet_name") or comp_row.get("name")
    if not sweet_name:
        raise ValueError(f"sweet_compositions id {sweet_id} missing sweet_name/name")
    prof_resp = (
        supabase.table("sweet_paste_profiles")
        .select("*")
        .eq("sweet_name", sweet_name)
        .single()
        .execute()
    )
    prof_row = prof_resp.data
    if not prof_row:
        raise ValueError(
            f"sweet_paste_profiles: no row found for sweet_name='{sweet_name}'"
        )
    category = comp_row.get("category") or "default"
    formulation_type = _map_category_to_formulation_type(category)
    water_pct = float(comp_row.get("moisture_pct") or 0.0)
    sugars_pct = float(comp_row.get("sugar_pct") or comp_row.get("sugars_pct") or 0.0)
    fat_pct = float(comp_row.get("fat_pct") or 0.0)
    msnf_pct = float(comp_row.get("msnf_pct") or 0.0)
    other_pct = float(comp_row.get("other_pct") or 0.0)
    afp_per_100g = float(comp_row.get("afp_per_100g") or 0.0)
    sweet_pct_min = float(prof_row.get("sweet_pct_min") or 40.0)
    sweet_pct_max = float(prof_row.get("sweet_pct_max") or 80.0)
    sweet_pct_default = float(prof_row.get("sweet_pct_default") or 60.0)
    target_sugar_center = prof_row.get("target_sugar_pct")
    target_fat_center = prof_row.get("target_fat_pct")
    target_msnf_center = prof_row.get("target_msnf_pct")
    target_solids_center = prof_row.get("target_total_solids_pct")
    target_sugar_range = _make_band(target_sugar_center, rel_tol=0.15)
    target_fat_range = _make_band(target_fat_center, rel_tol=0.2)
    target_msnf_range = _make_band(target_msnf_center, rel_tol=0.2)
    target_solids_range = _make_band(target_solids_center, rel_tol=0.1)
    target_aw_min = float(prof_row.get("target_aw_min") or 0.68)
    target_aw_max = float(prof_row.get("target_aw_max") or 0.8)
    target_aw_range = (target_aw_min, target_aw_max)
    base_template_id = int(prof_row.get("base_template_id") or 1)
    intensity_tag = _infer_intensity_tag(
        sugars_pct=sugars_pct, afp_per_100g=afp_per_100g
    )
    return SweetProfile(
        sweet_id=sweet_id,
        sweet_name=sweet_name,
        category=category,
        formulation_type=formulation_type,
        water_pct=water_pct,
        sugars_pct=sugars_pct,
        fat_pct=fat_pct,
        msnf_pct=msnf_pct,
        other_pct=other_pct,
        afp_per_100g=afp_per_100g,
        sweet_pct_min=sweet_pct_min,
        sweet_pct_max=sweet_pct_max,
        sweet_pct_default=sweet_pct_default,
        target_sugar_pct_range=target_sugar_range,
        target_fat_pct_range=target_fat_range,
        target_msnf_pct_range=target_msnf_range,
        target_solids_pct_range=target_solids_range,
        target_aw_range=target_aw_range,
        base_template_id=base_template_id,
        intensity_tag=intensity_tag,
    )