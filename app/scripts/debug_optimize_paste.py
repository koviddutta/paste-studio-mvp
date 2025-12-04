from app.paste_core.metrics import compute_paste_metrics
from app.paste_core.domain import SweetProfile
from app.paste_core.optimizer import optimize_paste
from app.paste_core.validation import validate_paste
from app.database.sweet_profiler import load_sweet_profile_and_base


def main():
    sweet_profile, sweet_comp, base_comp = load_sweet_profile_and_base("Gulab Jamun")
    metrics = compute_paste_metrics(
        sweet_pct=sweet_profile.sweet_pct_default,
        base_pct=100.0 - sweet_profile.sweet_pct_default,
        sweet_comp=sweet_comp,
        base_comp=base_comp,
    )
    report = validate_paste(
        metrics=metrics, formulation_type="sweet_paste", sweet_profile=sweet_profile
    )
    plan = optimize_paste(
        metrics=metrics, formulation_type="sweet_paste", sweet_profile=sweet_profile
    )
    print("=== PASTE METRICS ===")
    print(metrics)
    print("=== VALIDATION ===")
    print(report.overall_status)
    for p in report.parameters:
        print("-", p.name, p.status, ":", p.message)
    print("=== OPTIMIZATION PLAN ===")
    for a in plan.actions:
        print(f"* {a.ingredient_name}: {a.delta_g_per_kg:.1f} g/1kg ({a.reason})")
    print("Notes:")
    for n in plan.notes:
        print("-", n)


if __name__ == "__main__":
    main()