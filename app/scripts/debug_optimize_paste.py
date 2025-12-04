import os
import sys
import logging

sys.path.insert(0, os.getcwd())
from app.services.design_paste_from_sweet import design_paste_for_sweet_id
from app.paste_core.optimizer import optimize_paste


def main():
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    print("----------------------------------------------------------------")
    print(" DEBUG SCRIPT: Optimization Logic Check")
    print("----------------------------------------------------------------")
    try:
        print("""
1. Designing Paste for Sweet ID 1 (Gulab Jamun)...""")
        result = design_paste_for_sweet_id(sweet_id=1)
        metrics = result.metrics
        sp = result.sweet_profile
        print(f"   Current Metrics (per 100g):")
        print(f"     - Solids: {metrics.solids_pct:.2f}%")
        print(f"     - Fat:    {metrics.fat_pct:.2f}%")
        print(f"     - Sugar:  {metrics.sugar_pct:.2f}%")
        print(f"     - Aw:     {metrics.water_activity:.3f}")
        print(f"\n   Validation Status: {result.validation.overall_status}")
        if result.validation.key_recommendations:
            for rec in result.validation.key_recommendations:
                print(f"     * {rec}")
        print("""
2. Running Paste Optimizer...""")
        plan = optimize_paste(
            metrics=metrics, formulation_type=sp.formulation_type, sweet_profile=sp
        )
        print("----------------------------------------------------------------")
        print(f" OPTIMIZATION PLAN: {plan.formulation_type}")
        print("----------------------------------------------------------------")
        print(f"   Targets detected:")
        print(f"     - Solids Target: {plan.target_solids_pct}%")
        print(f"     - Fat Target:    {plan.target_fat_pct}%")
        print(f"     - Sugar Target:  {plan.target_sugars_pct}%")
        print("""
   Suggested Actions:""")
        if not plan.actions:
            print("     (No specific quantitative actions suggested)")
        else:
            for action in plan.actions:
                print(
                    f"     [ADD] {action.ingredient_name:20} : {action.delta_g_per_kg:.1f} g/kg"
                )
                print(f"           Reason: {action.reason}")
        print("""
   Optimization Notes:""")
        for note in plan.notes:
            print(f"     * {note}")
        print("----------------------------------------------------------------")
    except Exception as e:
        logging.exception(f"CRASHED: {e}")


if __name__ == "__main__":
    main()