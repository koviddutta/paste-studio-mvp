"""
Validation logic for the Paste Core module.
Placeholder for future implementation.
"""

from .domain import PasteComposition, PasteValidation
from .water_activity import classify_aw


def validate_paste(comp: PasteComposition) -> PasteValidation:
    notes: list[str] = []
    solids_ok = 60.0 <= comp.total_solids_pct <= 80.0
    if not solids_ok:
        notes.append(
            f"Total solids {comp.total_solids_pct:.1f}% outside 60–80% window (too low → runny / perishable, too high → hard/glassy)."
        )
    aw_status = classify_aw(comp.water_activity)
    aw_ok = "Target Range" in aw_status
    if not aw_ok:
        notes.append(f"Water activity {comp.water_activity:.3f}: {aw_status}")
    if solids_ok and aw_ok:
        notes.append(
            "Formulation is within basic solids and Aw targets for a spreadable, stable paste."
        )
    return PasteValidation(is_solid_range_ok=solids_ok, is_aw_ok=aw_ok, notes=notes)