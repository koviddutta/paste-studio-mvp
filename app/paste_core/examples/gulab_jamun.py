"""
Example implementation for Gulab Jamun.
Placeholder for future implementation.
"""

from app.paste_core.domain import Ingredient
from app.paste_core.sweet_to_paste import formulate_paste


def build_gulab_jamun_example():
    gulab_jamun = Ingredient(
        name="Gulab Jamun",
        quantity_g=0.0,
        sugars_pct=51.9,
        fat_pct=6.0,
        msnf_pct=8.0,
        other_pct=4.1,
        water_pct=30.0,
    )
    base_lookup = {
        "Cream": Ingredient(
            "Cream",
            0.0,
            sugars_pct=0.0,
            fat_pct=25.0,
            msnf_pct=6.8,
            other_pct=0.0,
            water_pct=68.2,
        ),
        "Skim Milk Powder": Ingredient(
            "Skim Milk Powder",
            0.0,
            sugars_pct=0.0,
            fat_pct=1.0,
            msnf_pct=93.0,
            other_pct=0.0,
            water_pct=3.5,
        ),
        "Glucose Syrup DE40": Ingredient(
            "Glucose Syrup DE40",
            0.0,
            sugars_pct=80.0,
            fat_pct=0.0,
            msnf_pct=0.0,
            other_pct=0.0,
            water_pct=20.0,
        ),
        "Ghee": Ingredient(
            "Ghee",
            0.0,
            sugars_pct=0.0,
            fat_pct=100.0,
            msnf_pct=0.0,
            other_pct=0.0,
            water_pct=0.0,
        ),
    }
    base_template = {
        "Cream": 2.0,
        "Skim Milk Powder": 1.0,
        "Glucose Syrup DE40": 1.0,
        "Ghee": 0.5,
    }
    batch_g = 1000.0
    sweet_ratio = 0.6
    result = formulate_paste(
        sweet=gulab_jamun,
        base_template=base_template,
        batch_weight_g=batch_g,
        sweet_ratio=sweet_ratio,
        base_composition_lookup=base_lookup,
    )
    return result


if __name__ == "__main__":
    result = build_gulab_jamun_example()
    print("INGREDIENTS:")
    for ing in result["ingredients"]:
        pct = ing.quantity_g / 1000.0 * 100
        print(f"  {ing.name:20} {ing.quantity_g:6.1f} g ({pct:5.1f}%)")
    print("""
COMPOSITION:""")
    print(result["composition"])
    print("""
VALIDATION:""")
    for note in result["validation"].notes:
        print(" -", note)