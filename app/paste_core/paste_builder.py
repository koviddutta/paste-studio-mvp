from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Optional

from .paste_templates import (
    get_template_definition,
    get_sweet_template_config,
    PasteTemplateDefinition,
    TemplateIngredientSpec,
    SweetTemplateConfig,
)


# ---------------------------
# Public Data Structures
# ---------------------------


@dataclass
class PasteIngredientAllocation:
    """
    One ingredient in a designed paste recipe.
    pct_of_paste: percentage of final paste mass (0–100).
    grams_per_kg: grams in a 1000 g batch (derived from pct_of_paste).
    """
    ingredient_name: str
    role: str
    pct_of_paste: float
    grams_per_kg: float
    notes: str = ""


@dataclass
class PasteDesignResult:
    """
    High-level result from the paste builder, before metrics/validation.

    This is what you can feed into:
      - composition calculators
      - optimizer
      - reporting
      - UI (as a first-pass paste recipe)

    Later we will add hooks here for metrics_before/after, validation etc.
    """
    sweet_name: str
    mode: str                     # "sweet_dominant" | "template_dominant" | "hybrid"
    template_type: str
    allocations: List[PasteIngredientAllocation]
    target_solids_min: float
    target_solids_max: float
    target_aw_chilled_max: float
    target_aw_ambient_max: Optional[float]
    notes: str = ""


# ---------------------------
# Internal Helpers
# ---------------------------


def _normalize_percentages(ingredients: List[TemplateIngredientSpec]) -> List[TemplateIngredientSpec]:
    """
    If the sum of default_pct is not exactly 100, rescale them to sum to 100.
    This is useful for template_dominant mode where we want a fully structural paste.
    """
    total = sum(i.default_pct for i in ingredients)
    if total <= 0:
        return ingredients
    scale = 100.0 / total
    scaled = []
    for spec in ingredients:
        scaled.append(
            TemplateIngredientSpec(
                ingredient_name=spec.ingredient_name,
                role=spec.role,
                default_pct=spec.default_pct * scale,
                min_pct=spec.min_pct,
                max_pct=spec.max_pct,
                notes=spec.notes,
            )
        )
    return scaled


def _build_allocations_template_dominant(
    template: PasteTemplateDefinition,
    cfg: SweetTemplateConfig,
    sweet_name: str,
) -> List[PasteIngredientAllocation]:
    """
    For template-dominant mode:
      - Ignore any 'sweet_mass' role in % calculations.
      - Use the template's structural ingredients (nut, sugar, fat, msnf, etc.).
      - Normalize to sum to 100%.
    The sweet is used conceptually (flavour profile, targets) but not as a bulk ingredient.
    """
    # Filter out any explicit sweet_mass placeholders
    structural_specs = [s for s in template.ingredients if s.role != "sweet_mass"]
    structural_specs = _normalize_percentages(structural_specs)

    allocations: List[PasteIngredientAllocation] = []
    for spec in structural_specs:
        pct = spec.default_pct
        grams = pct * 10.0  # 1000 g batch
        allocations.append(
            PasteIngredientAllocation(
                ingredient_name=spec.ingredient_name,
                role=spec.role,
                pct_of_paste=pct,
                grams_per_kg=grams,
                notes=spec.notes,
            )
        )
    return allocations


def _build_allocations_sweet_dominant_or_hybrid(
    template: PasteTemplateDefinition,
    cfg: SweetTemplateConfig,
    sweet_name: str,
) -> List[PasteIngredientAllocation]:
    """
    For sweet_dominant or hybrid mode:

      - Assign a fixed % of the paste to the finished sweet mass (sweet_mass_default_pct).
      - Distribute the remaining % across the other template ingredients, preserving
        their relative default_pct ratios.

    Requirements:
      - Template must contain exactly one ingredient with role 'sweet_mass'
        (usually with ingredient_name='__SWEET_MASS__').
    """
    sweet_spec_list = [s for s in template.ingredients if s.role == "sweet_mass"]
    if len(sweet_spec_list) != 1:
        raise ValueError(
            f"Template '{template.template_type}' used in mode '{cfg.mode}' "
            f"must define exactly one 'sweet_mass' ingredient."
        )
    sweet_spec = sweet_spec_list[0]

    if cfg.sweet_mass_default_pct is None:
        sweet_pct = sweet_spec.default_pct
    else:
        sweet_pct = cfg.sweet_mass_default_pct

    if sweet_pct <= 0.0 or sweet_pct >= 100.0:
        raise ValueError(
            f"Invalid sweet_mass_default_pct={sweet_pct} for '{sweet_name}'. "
            "Expected a value between 0 and 100."
        )

    others = [s for s in template.ingredients if s is not sweet_spec]
    total_default_others = sum(s.default_pct for s in others)
    if total_default_others <= 0:
        raise ValueError(
            f"Template '{template.template_type}' has no structural ingredients "
            "other than sweet_mass."
        )

    remaining_pct = 100.0 - sweet_pct
    scale = remaining_pct / total_default_others

    allocations: List[PasteIngredientAllocation] = []

    # 1) Sweet mass allocation (actual finished mithai mass)
    allocations.append(
        PasteIngredientAllocation(
            ingredient_name=sweet_name,  # replace placeholder with real sweet
            role="sweet_mass",
            pct_of_paste=sweet_pct,
            grams_per_kg=sweet_pct * 10.0,
            notes=cfg.notes or sweet_spec.notes,
        )
    )

    # 2) Structural ingredients (SMP, ghee, glucose, etc.)
    for spec in others:
        pct = spec.default_pct * scale
        grams = pct * 10.0
        allocations.append(
            PasteIngredientAllocation(
                ingredient_name=spec.ingredient_name,
                role=spec.role,
                pct_of_paste=pct,
                grams_per_kg=grams,
                notes=spec.notes,
            )
        )

    return allocations


# ---------------------------
# Public Builder API
# ---------------------------


def design_paste_recipe_for_sweet_name(
    sweet_name: str,
    category: Optional[str] = None,
) -> PasteDesignResult:
    """
    Main entry point for v1 paste builder.

    Given a sweet_name (and optional category hint), this will:
      - Look up SweetTemplateConfig (mode, template_type, sweet_mass %).
      - Fetch the corresponding PasteTemplateDefinition.
      - Generate a 1 kg paste recipe as a list of ingredient allocations.

    At this stage, this is purely structural:
      - It does NOT yet compute composition, Aw, validation, or optimization.
      - It is meant to be fed into your existing Paste Core (metrics + optimizer).
    """
    cfg = get_sweet_template_config(sweet_name=sweet_name, category=category)
    template = get_template_definition(cfg.template_type)

    mode = cfg.mode.lower().strip()
    if mode == "template_dominant":
        allocations = _build_allocations_template_dominant(
            template=template,
            cfg=cfg,
            sweet_name=sweet_name,
        )
    elif mode in ("sweet_dominant", "hybrid"):
        allocations = _build_allocations_sweet_dominant_or_hybrid(
            template=template,
            cfg=cfg,
            sweet_name=sweet_name,
        )
    else:
        raise ValueError(f"Unknown paste mode '{cfg.mode}' for sweet '{sweet_name}'.")

    return PasteDesignResult(
        sweet_name=sweet_name,
        mode=cfg.mode,
        template_type=cfg.template_type,
        allocations=allocations,
        target_solids_min=template.target_solids_min,
        target_solids_max=template.target_solids_max,
        target_aw_chilled_max=template.target_aw_chilled_max,
        target_aw_ambient_max=template.target_aw_ambient_max,
        notes=cfg.notes,
    )
