from app.paste_core.sweet_profiler import build_sweet_profile_from_db
from app.paste_core.base_templates import compute_base_template_from_db
from app.paste_core.paste_designer import PasteDesigner
from app.paste_core.domain import DesignedPaste


def design_paste_for_sweet_id(
    sweet_id: int, batch_weight_g: float = 1000.0, sweet_step_pct: float = 2.0
):
    """
    Design a paste formulation for a specific sweet ID.

    Steps:
    1. Load SweetProfile (constraints, targets, base_template_id) from DB.
    2. Load BaseTemplateComposition (balancing base ingredients) from DB.
    3. Run PasteDesigner to optimize sweet vs base ratio.
    4. Return the final DesignedPaste object.
    """
    sweet_profile = build_sweet_profile_from_db(sweet_id)
    base_template = compute_base_template_from_db(sweet_profile.base_template_id)
    designer = PasteDesigner(
        sweet_profile=sweet_profile,
        base_template=base_template,
        batch_weight_g=batch_weight_g,
        sweet_step_pct=sweet_step_pct,
    )
    designed = designer.design()
    return designed