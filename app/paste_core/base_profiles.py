"""
Manual definitions for standard gelato base profiles.
Used for calculating infusion rates of pastes into bases.
"""

from app.paste_core.domain import GelatoBaseProfile


def white_base_profile() -> GelatoBaseProfile:
    """
    Returns a standard 'White Base' (Fiordilatte) profile.
    Typically milk-based, neutral flavor, moderate fat.
    """
    return GelatoBaseProfile(
        name="Standard White Base",
        sugar_pct=18.0,
        fat_pct=4.5,
        solids_pct=38.0,
        sugar_min=16.0,
        sugar_max=22.0,
        fat_min=4.0,
        fat_max=10.0,
        solids_min=36.0,
        solids_max=42.0,
        afp_total=30.0,
        afp_min=25.0,
        afp_max=35.0,
    )


def kulfi_base_profile() -> GelatoBaseProfile:
    """
    Returns a 'Kulfi Base' profile.
    Rich, reduced milk style, higher solids, higher fat tolerance.
    """
    return GelatoBaseProfile(
        name="Rich Kulfi Base",
        sugar_pct=16.0,
        fat_pct=10.0,
        solids_pct=42.0,
        sugar_min=16.0,
        sugar_max=25.0,
        fat_min=8.0,
        fat_max=15.0,
        solids_min=38.0,
        solids_max=48.0,
        afp_total=28.0,
        afp_min=24.0,
        afp_max=36.0,
    )