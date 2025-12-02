import os
import sys
import logging

sys.path.insert(0, os.getcwd())
from app.services.design_paste_from_sweet import design_paste_for_sweet_id
from app.paste_core.gelato_infusion import recommend_paste_in_gelato
from app.paste_core.base_profiles import white_base_profile


def main():
    logging.basicConfig(level=logging.INFO)
    print("----------------------------------------------------------------")
    print(" DEBUG SCRIPT: Paste Infusion Recommendation")
    print("----------------------------------------------------------------")
    try:
        print("""1. Designing Paste for Sweet ID 1 (Gulab Jamun)...
""")
        paste_result = design_paste_for_sweet_id(sweet_id=1)
        metrics = paste_result.metrics
        sweet_profile = paste_result.sweet_profile
        print(f"   Paste Composition (per 100g):")
        print(f"     - Sugars: {metrics.sugar_pct:.2f}%")
        print(f"     - Fat:    {metrics.fat_pct:.2f}%")
        print(f"     - Solids: {metrics.solids_pct:.2f}%")
        print(f"   Sweet Intensity Tag: '{sweet_profile.intensity_tag}'")
        print("""
2. Loading Standard White Base Profile...
""")
        base = white_base_profile()
        print(f"   Base: {base.name}")
        print(
            f"   Base Composition: Sugar={base.sugar_pct}%, Fat={base.fat_pct}%, Solids={base.solids_pct}%"
        )
        print(f"   Target Constraints:")
        print(f"     - Sugar: [{base.sugar_min}, {base.sugar_max}] %")
        print(f"     - Fat:   [{base.fat_min}, {base.fat_max}] %")
        print(f"     - Solids: [{base.solids_min}, {base.solids_max}] %")
        print("""
3. Calculating Infusion Recommendations...
""")
        rec = recommend_paste_in_gelato(
            paste_metrics=metrics, base_profile=base, sweet_profile=sweet_profile
        )
        print("----------------------------------------------------------------")
        print(" RECOMMENDATION REPORT")
        print("----------------------------------------------------------------")
        print(
            f"Science-based Max Limit:   {rec.p_science_max * 100:.2f}% (Strict composition limits)"
        )
        print(
            f"Recommended Max (Capped):  {rec.p_recommended_max * 100:.2f}% (Flavor intensity cap)"
        )
        print(
            f"Recommended Default:       {rec.p_recommended_default * 100:.2f}% (Suggested starting point)"
        )
        print("""
Limiting Factors (Max allowed paste % by constraint):""")
        for factor, limit in rec.science_limits.items():
            print(f"  - {factor.capitalize()}: {limit * 100:.1f}%")
        print("""
Analysis Commentary:""")
        for note in rec.commentary:
            print(f"  * {note}")
        print("----------------------------------------------------------------")
    except Exception as e:
        logging.exception(f"CRASHED: {e}")


if __name__ == "__main__":
    main()