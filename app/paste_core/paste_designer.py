"""
Paste design logic for the Paste Core module.
Placeholder for future implementation.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple, List

from .domain import SweetProfile, BaseTemplateComposition, DesignedPaste, PasteMetrics
from .metrics import compute_paste_metrics
from .validation_engine import validate_paste  # you will implement this next


@dataclass
class PasteCandidate:
    sweet_pct: float
    base_pct: float
    metrics: PasteMetrics
    score: float
    debug_notes: List[str]


class PasteDesigner:
    """
    Core engine responsible for choosing:
      - sweet_pct (how much mithai in the paste)
      - base_pct  (how much balancing base)
    such that the final paste is solid scientifically and practical as a spread.
    """

    def __init__(
        self,
        sweet_profile: SweetProfile,
        base_template: BaseTemplateComposition,
        batch_weight_g: float = 1000.0,
        sweet_step_pct: float = 2.0,
    ) -> None:
        self.sweet_profile = sweet_profile
        self.base_template = base_template
        self.batch_weight_g = batch_weight_g
        self.sweet_step_pct = sweet_step_pct

    def design(self) -> DesignedPaste:
        """
        Main entry point:
          - search over sweet_pct in [min, max] at sweet_step_pct
          - evaluate each candidate
          - pick the lowest-score candidate
          - run full validation on best candidate
        """
        best: Optional[PasteCandidate] = None

        for sweet_pct in self._sweet_pct_range():
            base_pct = 100.0 - sweet_pct
            metrics = compute_paste_metrics(
                sweet_pct=sweet_pct,
                base_pct=base_pct,
                sweet_comp=self._sweet_composition_dict(),
                base_comp=self._base_composition_dict(),
            )
            score, notes = self._score_candidate(sweet_pct, base_pct, metrics)

            candidate = PasteCandidate(
                sweet_pct=sweet_pct,
                base_pct=base_pct,
                metrics=metrics,
                score=score,
                debug_notes=notes,
            )

            if best is None or candidate.score < best.score:
                best = candidate

        if best is None:
            raise RuntimeError("PasteDesigner could not find any candidate. Check ranges.")

        # Run full validation using DB-driven thresholds
        validation = validate_paste(
            metrics=best.metrics,
            formulation_type=self.sweet_profile.formulation_type,
            sweet_profile=self.sweet_profile,
        )

        # For now, we do not expand the base template into individual ingredients.
        # That can be added later (using base_template.ingredient_breakdown).
        return DesignedPaste(
            sweet_profile=self.sweet_profile,
            sweet_pct=best.sweet_pct,
            base_pct=best.base_pct,
            base_template=self.base_template,
            batch_weight_g=self.batch_weight_g,
            metrics=best.metrics,
            validation=validation,
        )

    # -----------------------
    # Internal helpers
    # -----------------------

    def _sweet_pct_range(self):
        """
        Generates sweet% candidates from min to max using the configured step.
        Uses profile defaults if min/max are missing or inconsistent.
        """
        sp = self.sweet_profile
        sweet_min = max(10.0, sp.sweet_pct_min or 0.0)
        sweet_max = min(90.0, sp.sweet_pct_max or 100.0)

        if sweet_min > sweet_max:
            # Fallback to default ± 10%
            default = sp.sweet_pct_default or 60.0
            sweet_min = max(10.0, default - 10.0)
            sweet_max = min(90.0, default + 10.0)

        current = sweet_min
        while current <= sweet_max + 1e-6:
            yield round(current, 2)
            current += self.sweet_step_pct

    def _sweet_composition_dict(self) -> dict:
        sp = self.sweet_profile
        return {
            "water_pct": sp.water_pct,
            "sugars_pct": sp.sugars_pct,
            "fat_pct": sp.fat_pct,
            "msnf_pct": sp.msnf_pct,
            "other_pct": sp.other_pct,
        }

    def _base_composition_dict(self) -> dict:
        bt = self.base_template
        return {
            "water_pct": bt.water_pct,
            "sugars_pct": bt.sugars_pct,
            "fat_pct": bt.fat_pct,
            "msnf_pct": bt.msnf_pct,
            "other_pct": bt.other_pct,
        }

    def _score_candidate(
        self,
        sweet_pct: float,
        base_pct: float,
        metrics: PasteMetrics,
    ) -> Tuple[float, List[str]]:
        """
        Heuristic scoring from a food technologist viewpoint.
        Lower score is better.

        We penalise:
          - deviations from target composition bands (sugar, fat, msnf, solids)
          - water activity outside target range
          - obvious extremes (sweet_pct too low/high for this category)

        Later, this can be augmented with:
          - AFP/POD/DE-based penalties using validation_thresholds_extended
        """
        sp = self.sweet_profile
        notes: List[str] = []

        score = 0.0

        def penalty_for_range(
            value: float,
            target: Tuple[float, float],
            weight: float,
            name: str,
        ) -> float:
            t_min, t_max = target
            if t_min is None or t_max is None:
                return 0.0
            if t_min <= value <= t_max:
                return 0.0
            # Outside target: squared distance scaled
            center = 0.5 * (t_min + t_max)
            dist = abs(value - center)
            notes.append(f"{name} {value:.2f} outside target {t_min}-{t_max}, dist={dist:.2f}")
            return weight * (dist ** 2)

        # Core composition penalties
        score += penalty_for_range(
            metrics.sugar_pct,
            sp.target_sugar_pct_range,
            weight=1.5,
            name="sugar_pct",
        )
        score += penalty_for_range(
            metrics.fat_pct,
            sp.target_fat_pct_range,
            weight=1.2,
            name="fat_pct",
        )
        score += penalty_for_range(
            metrics.msnf_pct,
            sp.target_msnf_pct_range,
            weight=1.0,
            name="msnf_pct",
        )
        score += penalty_for_range(
            metrics.solids_pct,
            sp.target_solids_pct_range,
            weight=1.5,
            name="solids_pct",
        )

        # Water activity penalty
        aw_min, aw_max = sp.target_aw_range
        if not (aw_min <= metrics.water_activity <= aw_max):
            center = 0.5 * (aw_min + aw_max)
            dist = abs(metrics.water_activity - center)
            notes.append(
                f"water_activity {metrics.water_activity:.3f} outside target {aw_min}-{aw_max}, "
                f"dist={dist:.3f}"
            )
            score += 3.0 * (dist ** 2)

        # Soft penalty for sweet_pct away from default
        default_sp = sp.sweet_pct_default or ((sp.sweet_pct_min + sp.sweet_pct_max) / 2.0)
        dist_sp = abs(sweet_pct - default_sp)
        score += 0.05 * (dist_sp ** 2)

        # Guardrails: ultra-high or ultra-low sweet ratios get extra penalty
        if sweet_pct > sp.sweet_pct_max:
            score += 50.0
            notes.append(f"sweet_pct {sweet_pct:.1f} > sweet_pct_max {sp.sweet_pct_max:.1f}")
        if sweet_pct < sp.sweet_pct_min:
            score += 50.0
            notes.append(f"sweet_pct {sweet_pct:.1f} < sweet_pct_min {sp.sweet_pct_min:.1f}")

        return score, notes
