# app/paste_core/sugar_science.py
"""
Scientific sugar model for PAC / AFP / POD / DE calculations.

- Values are relative to sucrose (POD = 1.0, PAC = 1.0).
- Based on standard gelato PAC/POD tables from professional sources.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Mapping
import logging

try:
    from app.database.supabase_client import get_supabase
except Exception:  # pragma: no cover - paste_core can be used without DB in tests
    get_supabase = None  # type: ignore


@dataclass
class SugarFactors:
    pod_rel: float   # sweetening power vs sucrose
    pac_rel: float   # anti-freezing power vs sucrose
    de_value: float  # DE or effective "dextrose equivalent" index


# Conservative defaults from gelato practice (normalized vs sucrose=1.0)
# and typical PAC/POD equivalences. :contentReference[oaicite:1]{index=1}
SUGAR_FACTORS_DEFAULT: Dict[str, SugarFactors] = {
    "sucrose": SugarFactors(pod_rel=1.0,  pac_rel=1.0,  de_value=100.0),
    "dextrose": SugarFactors(pod_rel=0.75, pac_rel=1.8, de_value=100.0),
    "fructose": SugarFactors(pod_rel=1.7,  pac_rel=1.9, de_value=100.0),
    "lactose": SugarFactors(pod_rel=0.16, pac_rel=1.0, de_value=100.0),
    # Invert sugar is roughly glucose+fructose with some water
    "invert_sugar": SugarFactors(pod_rel=1.3, pac_rel=1.9, de_value=75.0),
    # Glucose syrups – PAC scales with DE, POD is low
    "glucose_syrup_de40": SugarFactors(pod_rel=0.3, pac_rel=0.7, de_value=40.0),
    "glucose_syrup_de60": SugarFactors(pod_rel=0.6, pac_rel=1.0, de_value=60.0),
    # Maltodextrin: solids with almost no POD/PAC
    "maltodextrin_de10": SugarFactors(pod_rel=0.05, pac_rel=0.2, de_value=10.0),
}


def load_sugar_factors_from_db() -> Dict[str, SugarFactors]:
    """
    Optional override: try to load sugar factors from Supabase table
    'gelato_science_constants' if present.

    Expected columns (adapt to your real schema if needed):
      - sugar_type (text)
      - pod_rel   (float)
      - pac_rel   (float)
      - de_value  (float)
    """
    if get_supabase is None:
        return {}

    try:
        supabase = get_supabase()
        resp = supabase.table("gelato_science_constants").select("*").execute()
        rows = resp.data or []
    except Exception as e:
        logging.warning("Could not load gelato_science_constants from DB: %s", e)
        return {}

    factors: Dict[str, SugarFactors] = {}
    for row in rows:
        stype = (row.get("sugar_type") or "").strip().lower()
        if not stype:
            continue
        try:
            pod = float(row.get("pod_rel") or row.get("pod_factor") or 0.0)
            pac = float(row.get("pac_rel") or row.get("pac_factor") or 0.0)
            de  = float(row.get("de_value") or row.get("de") or 0.0)
        except (TypeError, ValueError):
            logging.warning("Invalid numeric data in gelato_science_constants row: %r", row)
            continue
        if pod <= 0.0 and pac <= 0.0:
            continue
        factors[stype] = SugarFactors(pod_rel=pod, pac_rel=pac, de_value=de)
    return factors


def get_sugar_factors() -> Dict[str, SugarFactors]:
    """
    Merge DB overrides (if any) on top of hard-coded defaults.
    """
    factors = dict(SUGAR_FACTORS_DEFAULT)
    db_factors = load_sugar_factors_from_db()
    factors.update(db_factors)
    return factors


def normalise_sugar_profile(
    sugar_profile: Mapping[str, float] | None,
) -> Dict[str, float]:
    """
    Normalise sugar profile so values sum to 1.0.

    sugar_profile can be:
      - fractions of total sugars (0–1)
      - percentages (0–100)
      - or grams per 100 g paste (we normalise anyway).

    Returns a dict sugar_type -> fraction_of_total_sugars (0–1).
    """
    if not sugar_profile:
        return {}

    # Drop non-positive entries and lower-case keys
    cleaned = {k.strip().lower(): float(v) for k, v in sugar_profile.items() if float(v) > 0.0}
    total = sum(cleaned.values())
    if total <= 0.0:
        return {}
    return {k: v / total for k, v in cleaned.items()}


def compute_sugar_system(
    total_sugars_pct: float,
    sugar_profile: Mapping[str, float] | None,
) -> dict[str, float]:
    """
    Compute PAC/AFP, POD, DE, SP from a sugar spectrum.

    Args:
        total_sugars_pct: total sugars in the paste (g per 100 g paste).
        sugar_profile: mapping sugar_type -> fraction/percentage/grams.

    Returns:
        dict with keys:
          - afp_total  (alias of pac_total)
          - pac_total
          - pod_sweetness
          - de_total
          - sp_total
    """
    factors = get_sugar_factors()
    fractions = normalise_sugar_profile(sugar_profile)

    # If no profile given, fall back to your house 70/10/20 split
    if not fractions:
        # Kovid's known default: 70% sucrose, 10% dextrose, 20% glucose syrup
        fractions = {
            "sucrose": 0.70,
            "dextrose": 0.10,
            "glucose_syrup_de40": 0.20,
        }

    pac_equiv = 0.0  # PAC/AFP index (sucrose equivalents)
    pod_equiv = 0.0  # POD index (sucrose equivalents)
    de_weighted_sum = 0.0

    for sugar_type, frac in fractions.items():
        grams = total_sugars_pct * frac  # g per 100 g paste
        sf = factors.get(sugar_type, factors["sucrose"])

        pac_equiv += grams * sf.pac_rel
        pod_equiv += grams * sf.pod_rel
        de_weighted_sum += grams * sf.de_value

    if total_sugars_pct > 0:
        de_total = de_weighted_sum / total_sugars_pct
    else:
        de_total = 0.0

    return {
        "afp_total": pac_equiv,          # AFP ≈ PAC
        "pac_total": pac_equiv,
        "pod_sweetness": pod_equiv,      # sucrose-equivalent sweetness
        "de_total": de_total,
        "sp_total": pod_equiv,           # SP ~ POD for our purposes
    }
