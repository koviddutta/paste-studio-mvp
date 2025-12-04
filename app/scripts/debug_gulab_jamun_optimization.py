import os
import sys
import logging

sys.path.insert(0, os.getcwd())
from app.services.design_paste_from_sweet import design_paste_for_sweet_id
from app.paste_core.optimizer import optimize_paste, apply_plan_to_metrics
from app.paste_core.validation import validate_paste


def print_metrics(title, m):
    print(f"\n--- {title} ---")
    print(f"  Sugars: {m.sugar_pct:.2f}%")
    print(f"  Fat:    {m.fat_pct:.2f}%")
    print(f"  Solids: {m.solids_pct:.2f}%")
    print(f"  Water:  {m.water_pct:.2f}%")
    print(f"  Aw:     {m.water_activity:.3f}")
    print(f"  AFP:    {m.afp_total:.1f}")


def main():
    logging.basicConfig(level=logging.INFO)
    print("===============================================================")
    print(" DEBUG: Gulab Jamun Paste Optimization Cycle")
    print("===============================================================")
    print("""
1. DESIGNING PASTE (Sweet ID=1)...""")
    try:
        designed = design_paste_for_sweet_id(sweet_id=1, batch_weight_g=1000.0)
    except Exception as e:
        logging.exception(f"Failed to design paste: {e}")
        return
    metrics_initial = designed.metrics
    sp = designed.sweet_profile
    print(f"   Sweet: {sp.sweet_name} ({sp.category})")
    print(f"   Formulation Type: {sp.formulation_type}")
    print_metrics("INITIAL METRICS", metrics_initial)
    print("""
2. INITIAL VALIDATION...""")
    report_initial = validate_paste(
        metrics=metrics_initial, formulation_type=sp.formulation_type, sweet_profile=sp
    )
    print(f"   Overall Status: {report_initial.overall_status}")
    for p in report_initial.parameters:
        if p.status != "OPTIMAL":
            print(f"   [{p.status}] {p.name}: {p.message}")
    print("""
3. RUNNING OPTIMIZER...""")
    plan = optimize_paste(
        metrics=metrics_initial, formulation_type=sp.formulation_type, sweet_profile=sp
    )
    if not plan.actions:
        print("   No quantitative actions suggested.")
    else:
        print(f"   Generated {len(plan.actions)} adjustments:")
        for action in plan.actions:
            print(
                f"   -> ADD {action.ingredient_name}: {action.delta_g_per_kg:.1f} g/kg"
            )
            print(f"      Reason: {action.reason}")
    print("""
   Optimizer Notes:""")
    for note in plan.notes:
        print(f"   * {note}")
    if plan.actions:
        print("""
4. APPLYING OPTIMIZATIONS...""")
        try:
            metrics_optimized = apply_plan_to_metrics(metrics_initial, plan)
            print_metrics("OPTIMIZED METRICS", metrics_optimized)
            print("""
5. RE-VALIDATING OPTIMIZED PASTE...""")
            report_final = validate_paste(
                metrics=metrics_optimized,
                formulation_type=sp.formulation_type,
                sweet_profile=sp,
            )
            print(f"   Overall Status: {report_final.overall_status}")
            for p in report_final.parameters:
                if p.status != "OPTIMAL":
                    print(f"   [{p.status}] {p.name}: {p.message}")
            print("""
--- COMPARISON ---""")
            print(
                f"Solids: {metrics_initial.solids_pct:.1f}% -> {metrics_optimized.solids_pct:.1f}%"
            )
            print(
                f"Fat:    {metrics_initial.fat_pct:.1f}% -> {metrics_optimized.fat_pct:.1f}%"
            )
            print(
                f"Aw:     {metrics_initial.water_activity:.3f} -> {metrics_optimized.water_activity:.3f}"
            )
        except Exception as e:
            logging.exception(f"Failed to apply plan: {e}")
    else:
        print("""
No actions to apply. Optimization cycle complete.""")
    print("""
===============================================================""")
    print(" END DEBUG")
    print("===============================================================")


if __name__ == "__main__":
    main()