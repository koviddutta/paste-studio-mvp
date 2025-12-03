"""
Manual definitions for standard gelato base profiles.
Used for calculating infusion rates of pastes into bases.
"""

# app/paste_core/base_profiles.py

from .domain import GelatoBaseProfile


def white_base_profile() -> GelatoBaseProfile:
    """
    Your actual white base, per 100 g.
    """
    return GelatoBaseProfile(
        name="white_base",

        # Actual composition from your spreadsheet (per 100 g)
        sugar_pct=17.87,
        fat_pct=6.01,
        solids_pct=34.93,

        # Finished gelato target ranges
        sugar_min=18.0,
        sugar_max=22.0,
        fat_min=7.0,
        fat_max=16.0,
        solids_min=37.0,
        solids_max=46.0,
    )


def kulfi_base_profile() -> GelatoBaseProfile:
    """
    Kulfi base (12% sugar).
    """
    return GelatoBaseProfile(
        name="kulfi_base",

        sugar_pct=12.0,
        fat_pct=12.0,
        solids_pct=42.0,

        # Kulfi ranges (thicker, higher solids)
        sugar_min=18.0,
        sugar_max=22.0,
        fat_min=10.0,
        fat_max=18.0,
        solids_min=40.0,
        solids_max=50.0,
    )


def chocolate_base_profile() -> GelatoBaseProfile:
    """
    Your chocolate base, per 100 g.
    """
    return GelatoBaseProfile(
        name="chocolate_base",

        sugar_pct=19.74,
        fat_pct=8.58,
        solids_pct=41.69,

        sugar_min=17.0,
        sugar_max=21.0,
        fat_min=8.0,
        fat_max=14.0,
        solids_min=40.0,
        solids_max=50.0,
    )
