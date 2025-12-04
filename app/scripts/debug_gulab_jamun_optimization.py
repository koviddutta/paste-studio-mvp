"""
Debug script: design Gulab Jamun paste, run validation,
optimize it, apply the optimization, and compare metrics before vs after.
"""

from app.paste_core.metrics import compute_paste_metrics
from app.paste_core.validation import validate_paste
from app.paste_core.optimizer import optimize_paste, apply_plan_to_metrics
from app.paste_core.domain import SweetProfile
from app.database.sweet_profiler import load_sweet_profile_and_base  # adjust import if your function name/path differs


def main():
    # 1. Load Gulab Jamun sweet profile + base composition
    sweet_profile, sweet_comp, base_comp = load_sweet_profile_and_base("Gulab Jamun")

    # 2. Compute initial metrics for default sweet/base ratio
    sweet_pct = sweet_profile.default_sweet_pct  # e.g. 20.0
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

    # 3. Run optimizer on the initial metrics
    plan = optimize_paste(
        metrics=metrics_before,
        formulation_type="sweet_paste",
        sweet_profile=sweet_profile,
    )

    # 4. Apply optimization plan to get new metrics
    metrics_after = apply_plan_to_metrics(metrics_before, plan)

    report_after = validate_paste(
        metrics=metrics_after,
        formulation_type="sweet_paste",
        sweet_profile=sweet_profile,
    )

    # 5. Print comparison
    print("=== GULAB JAMUN PASTE OPTIMIZATION DEBUG ===\n")

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
                f"* {a.ingredient_name}: {a.delta_g_per_kg:.1f} g / 1 kg paste "
                f"({a.reason})"
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
