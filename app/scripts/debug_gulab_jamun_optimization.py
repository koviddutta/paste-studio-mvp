"""
Debug script: design Gulab Jamun paste, run validation,
optimize it, apply the optimization, and compare metrics before vs after.
"""

from app.paste_core.metrics import compute_paste_metrics
from app.paste_core.validation import validate_paste
from app.paste_core.optimizer import optimize_paste, apply_plan_to_metrics
from app.paste_core.domain import SweetProfile
from app.paste_core.sweet_profiler import build_sweet_profile_from_db
from app.paste_core.base_templates import compute_base_template_from_db
from app.database.supabase_client import get_supabase


def load_sweet_profile_and_base(sweet_name: str):
    """
    Helper to resolve name -> ID -> objects -> composition dicts.
    """
    supabase = get_supabase()
    resp = (
        supabase.table("sweet_compositions")
        .select("id")
        .ilike("sweet_name", f"%{sweet_name}%")
        .limit(1)
        .execute()
    )
    if resp.data:
        sweet_id = resp.data[0]["id"]
    else:
        print(f"Warning: '{sweet_name}' not found. Trying ID=1.")
        sweet_id = 1
    sweet_profile = build_sweet_profile_from_db(sweet_id)
    base_template = compute_base_template_from_db(sweet_profile.base_template_id)
    sweet_comp = {
        "water_pct": sweet_profile.water_pct,
        "sugars_pct": sweet_profile.sugars_pct,
        "fat_pct": sweet_profile.fat_pct,
        "msnf_pct": sweet_profile.msnf_pct,
        "other_pct": sweet_profile.other_pct,
    }
    base_comp = {
        "water_pct": base_template.water_pct,
        "sugars_pct": base_template.sugars_pct,
        "fat_pct": base_template.fat_pct,
        "msnf_pct": base_template.msnf_pct,
        "other_pct": base_template.other_pct,
    }
    return (sweet_profile, sweet_comp, base_comp)


def main():
    sweet_profile, sweet_comp, base_comp = load_sweet_profile_and_base("Gulab Jamun")
    sweet_pct = sweet_profile.sweet_pct_default
    base_pct = 100.0 - sweet_pct
    metrics_before = compute_paste_metrics(
        sweet_pct=sweet_pct,
        base_pct=base_pct,
        sweet_comp=sweet_comp,
        base_comp=base_comp,
    )
    report_before = validate_paste(
        metrics=metrics_before,
        formulation_type="sweet_paste",
        sweet_profile=sweet_profile,
    )
    plan = optimize_paste(
        metrics=metrics_before,
        formulation_type="sweet_paste",
        sweet_profile=sweet_profile,
    )
    metrics_after = apply_plan_to_metrics(metrics_before, plan)
    report_after = validate_paste(
        metrics=metrics_after,
        formulation_type="sweet_paste",
        sweet_profile=sweet_profile,
    )
    print("""=== GULAB JAMUN PASTE OPTIMIZATION DEBUG ===
""")
    print("---- BEFORE OPTIMIZATION ----")
    print(f"Sugars: {metrics_before.sugar_pct:.2f}%")
    print(f"Fat:    {metrics_before.fat_pct:.2f}%")
    print(f"MSNF:   {metrics_before.msnf_pct:.2f}%")
    print(f"Solids: {metrics_before.solids_pct:.2f}%")
    print(f"Water:  {metrics_before.water_pct:.2f}%")
    print(f"Aw:     {metrics_before.water_activity:.3f}")
    print(f"AFPt:   {metrics_before.afp_total:.1f}")
    print(f"Status: {report_before.overall_status}")
    for p in report_before.parameters:
        print(" -", p.name, p.status, ":", p.message)
    print()
    print("---- OPTIMIZATION PLAN ----")
    if plan.actions:
        for a in plan.actions:
            print(
                f"* {a.ingredient_name}: {a.delta_g_per_kg:.1f} g / 1 kg paste ({a.reason})"
            )
    else:
        print("No quantitative actions suggested.")
    print("Notes:")
    for n in plan.notes:
        print(" -", n)
    print()
    print("---- AFTER OPTIMIZATION ----")
    print(f"Sugars: {metrics_after.sugar_pct:.2f}%")
    print(f"Fat:    {metrics_after.fat_pct:.2f}%")
    print(f"MSNF:   {metrics_after.msnf_pct:.2f}%")
    print(f"Solids: {metrics_after.solids_pct:.2f}%")
    print(f"Water:  {metrics_after.water_pct:.2f}%")
    print(f"Aw:     {metrics_after.water_activity:.3f}")
    print(f"AFPt:   {metrics_after.afp_total:.1f}")
    print(f"Status: {report_after.overall_status}")
    for p in report_after.parameters:
        print(" -", p.name, p.status, ":", p.message)
    print()


if __name__ == "__main__":
    main()