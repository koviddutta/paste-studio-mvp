import os
import sys
import logging

sys.path.insert(0, os.getcwd())
from app.services.design_paste_from_sweet import design_paste_for_sweet_id


def main():
    logging.basicConfig(level=logging.INFO)
    print("----------------------------------------------------------------")
    print(" DEBUG SCRIPT: Design Paste")
    print("----------------------------------------------------------------")
    try:
        result = design_paste_for_sweet_id(1)
        sp = result.sweet_profile
        print(f"Sweet Name:      {sp.sweet_name}")
        print(f"Category:        {sp.category}")
        print(f"Formulation:     {sp.formulation_type}")
        print("----------------------------------------------------------------")
        print(f"DESIGNED RATIO:")
        print(f"  Sweet: {result.sweet_pct}%")
        print(f"  Base:  {result.base_pct}%")
        print("----------------------------------------------------------------")
        print(f"METRICS (per 100g):")
        m = result.metrics
        print(f"  Sugars: {m.sugar_pct:.1f}%")
        print(f"  Fat:    {m.fat_pct:.1f}%")
        print(f"  MSNF:   {m.msnf_pct:.1f}%")
        print(f"  Solids: {m.solids_pct:.1f}%")
        print(f"  Water:  {m.water_pct:.1f}%")
        print(f"  Aw:     {m.water_activity:.3f}")
        print("----------------------------------------------------------------")
        print(f"VALIDATION:")
        if result.validation:
            print(f"  Overall: {result.validation.overall_status}")
            for p in result.validation.parameters:
                print(f"   - {p.name}: {p.value:.2f} -> {p.status} ({p.message})")
            if result.validation.key_recommendations:
                print("""
  Recommendations:""")
                for rec in result.validation.key_recommendations:
                    print(f"   * {rec}")
        else:
            print("  (No validation report)")
    except Exception as e:
        logging.exception(f"CRASHED: {e}")


if __name__ == "__main__":
    main()