"""
Sweet Profiler logic for the Paste Core module.
Placeholder for future implementation of custom sweet profiling and categorization logic.
"""

from __future__ import annotations
from app.database.supabase_client import get_client
from .domain import SweetProfile


def _map_category_to_formulation_type(category: str) -> str:
    """
    Map sweet_compositions.category to a formulation_type
    used by validation_thresholds_extended / msnf_stabilizer_balance.

    Adjust this mapping to match your actual category strings.
    """
    category = (category or "").lower()
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
    """
    Rough heuristic for flavour intensity.
    You can refine later with more signals (fried, caramelised, etc.).
    """
    if sugars_pct >= 45 or afp_per_100g >= 25:
        return "strong"
    if sugars_pct <= 30 and afp_per_100g <= 18:
        return "weak"
    return "medium"


def _range_from_row(row: dict, prefix: str) -> tuple[float, float]:
    """
    Utility to read min/max ranges from sweet_paste_profiles row.
    Expects columns like target_sugar_min, target_sugar_max etc.
    """
    return (
        float(row.get(f"{prefix}_min") or 0.0),
        float(row.get(f"{prefix}_max") or 0.0),
    )


def build_sweet_profile_from_db(sweet_id: int) -> SweetProfile:
    """
    Build a SweetProfile by joining:
      - sweet_compositions
      - sweet_paste_profiles

    Assumes:
      - sweet_compositions has: id, name, category, sugar_pct, fat_pct,
        msnf_pct, other_pct, moisture_pct, afp_per_100g
      - sweet_paste_profiles has: sweet_id (FK-ish to sweet_compositions.id),
        sweet_pct_min, sweet_pct_max, sweet_pct_default,
        target_sugar_min, target_sugar_max,
        target_fat_min, target_fat_max,
        target_msnf_min, target_msnf_max,
        target_solids_min, target_solids_max,
        target_aw_min, target_aw_max,
        base_template_id
    Adapt column names where yours differ.
    """
    supabase = get_client()
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
    prof_resp = (
        supabase.table("sweet_paste_profiles")
        .select("*")
        .eq("sweet_id", sweet_id)
        .single()
        .execute()
    )
    prof_row = prof_resp.data
    if not prof_row:
        raise ValueError(f"sweet_paste_profiles: sweet_id {sweet_id} not found")
    name = comp_row.get("sweet_name") or comp_row.get("name") or f"sweet_{sweet_id}"
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
    target_sugar_range = _range_from_row(prof_row, "target_sugar")
    target_fat_range = _range_from_row(prof_row, "target_fat")
    target_msnf_range = _range_from_row(prof_row, "target_msnf")
    target_solids_range = _range_from_row(prof_row, "target_solids")
    target_aw_range = (
        float(prof_row.get("target_aw_min") or 0.68),
        float(prof_row.get("target_aw_max") or 0.75),
    )
    base_template_id = int(prof_row.get("base_template_id") or 1)
    intensity_tag = _infer_intensity_tag(
        sugars_pct=sugars_pct, afp_per_100g=afp_per_100g
    )
    return SweetProfile(
        sweet_id=sweet_id,
        sweet_name=name,
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