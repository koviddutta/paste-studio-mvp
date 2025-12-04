import os
import sys
import logging

sys.path.insert(0, os.getcwd())
from app.paste_core.reporting import generate_paste_design_report


def print_header(title: str):
    print(
        """
"""
        + "=" * 60
    )
    print(f" {title}")
    print("=" * 60)


def print_sub_header(title: str):
    print(f"\n--- {title} ---")


def main():
    logging.basicConfig(level=logging.INFO)
    print("DEBUG SCRIPT: Generating Paste Design Report for 'Gulab Jamun'...")
    try:
        report = generate_paste_design_report(
            sweet_name="Gulab Jamun",
            formulation_type="sweet_paste",
            base_for_infusion="white_base",
        )
        print_header(f"REPORT: {report.sweet_name}")
        print(f"Category:        {report.category}")
        print(f"Formulation Type: {report.formulation_type}")
        print_sub_header("PASTE RECIPE (per 1 kg)")
        print(f"{'Ingredient':<35} {'Grams':<10} {'Note'}")
        print("-" * 80)
        for line in report.ingredients:
            print(
                f"{line.ingredient_name:<35} {line.grams_per_kg_final:<10.1f} {line.note}"
            )
        print_sub_header("OPTIMIZATION IMPACT")
        mb = report.metrics_before
        ma = report.metrics_after
        print(f"{'Metric':<15} {'Before':<10} {'After':<10}")
        print("-" * 40)
        print(f"{'Sugars':<15} {mb.sugar_pct:<10.2f}% {ma.sugar_pct:<10.2f}%")
        print(f"{'Fat':<15} {mb.fat_pct:<10.2f}% {ma.fat_pct:<10.2f}%")
        print(f"{'Solids':<15} {mb.solids_pct:<10.2f}% {ma.solids_pct:<10.2f}%")
        print(f"{'Aw':<15} {mb.water_activity:<10.3f}  {ma.water_activity:<10.3f}")
        print(f"{'AFP':<15} {mb.afp_total:<10.1f}  {ma.afp_total:<10.1f}")
        if report.infusion_recommendation:
            ir = report.infusion_recommendation
            print_sub_header(f"INFUSION INTO {ir.base_name.upper()}")
            print(f"Science Max:      {ir.p_science_max * 100:.1f}%")
            print(f"Rec. Max (Cap):   {ir.p_recommended_max * 100:.1f}%")
            print(f"Rec. Default:     {ir.p_recommended_default * 100:.1f}%")
            print("""
Limiting Factors (Max allowed paste %):""")
            for factor, limit in ir.science_limits.items():
                print(f"  - {factor}: {limit * 100:.1f}%")
            print("""
Commentary:""")
            for c in ir.commentary:
                print(f"  * {c}")
        else:
            print("""
(No infusion recommendations available)""")
        print_sub_header("SOP PROCESS STEPS")
        for step in report.sop_steps:
            print(step)
        print_sub_header("KEY NOTES")
        for note in report.key_notes:
            print(f"- {note}")
    except Exception as e:
        logging.exception(f"Report generation failed: {e}")


if __name__ == "__main__":
    main()