"""
Metrics calculation logic for the Paste Core module.
Placeholder for future implementation.
"""

from .water_activity import estimate_water_activity
from .domain import PasteMetrics


def compute_basic_composition_from_mix(
    sweet_pct: float,
    base_pct: float,
    sweet_comp: dict[str, float],
    base_comp: dict[str, float],
) -> dict[str, float]:
    """
    Weighted-average composition of sweet + base for 100 g paste.
    sweet_pct and base_pct are in 0–100 (% of paste).
    sweet_comp/base_comp contain water, sugars, fat, msnf, other (all %).
    """
    s = sweet_pct / 100.0
    b = base_pct / 100.0

    def mix(key: str) -> float:
        return s * sweet_comp[key] + b * base_comp[key]

    water = mix("water_pct")
    sugars = mix("sugars_pct")
    fat = mix("fat_pct")
    msnf = mix("msnf_pct")
    other = mix("other_pct")
    solids = sugars + fat + msnf + other
    return {
        "water_pct": water,
        "sugars_pct": sugars,
        "fat_pct": fat,
        "msnf_pct": msnf,
        "other_pct": other,
        "solids_pct": solids,
    }


def compute_afp_and_pod(
    sugars_pct: float, sugar_mix_profile: dict[str, float] | None = None
) -> dict[str, float]:
    """
    Placeholder for AFP/POD/PAC/SP computations.
    For now we assume:
      - afp_total roughly proportional to total sugars
      - pod_sweetness equals sugars_pct (will be refined with sugar spectrum)
    sugar_mix_profile: optional dict of sugar_type -> pct within sugars
    You will later plug in gelato_science_constants here.
    """
    afp_total = sugars_pct * 0.9
    pod_sweetness = sugars_pct
    de_total = 70.0
    pac_total = sugars_pct * 1.7
    sp_total = sugars_pct * 0.8
    return {
        "afp_total": afp_total,
        "pod_sweetness": pod_sweetness,
        "de_total": de_total,
        "pac_total": pac_total,
        "sp_total": sp_total,
    }


def compute_paste_metrics(
    sweet_pct: float,
    base_pct: float,
    sweet_comp: dict[str, float],
    base_comp: dict[str, float],
) -> PasteMetrics:
    """
    High-level wrapper:
      - compute basic composition
      - compute AFP/POD/DE/PAC/SP
      - compute water activity
    All per 100 g paste.
    """
    basic = compute_basic_composition_from_mix(
        sweet_pct=sweet_pct,
        base_pct=base_pct,
        sweet_comp=sweet_comp,
        base_comp=base_comp,
    )
    sugar_pct = basic["sugars_pct"]
    fat_pct = basic["fat_pct"]
    msnf_pct = basic["msnf_pct"]
    other_pct = basic["other_pct"]
    solids_pct = basic["solids_pct"]
    water_pct = basic["water_pct"]
    water_g = water_pct
    sugar_like_solids_g = sugar_pct
    aw = estimate_water_activity(
        water_g=water_g, sugar_like_solids_g=sugar_like_solids_g
    )
    afp_pod = compute_afp_and_pod(sugars_pct=sugar_pct)
    return PasteMetrics(
        sugar_pct=sugar_pct,
        fat_pct=fat_pct,
        msnf_pct=msnf_pct,
        other_pct=other_pct,
        solids_pct=solids_pct,
        water_pct=water_pct,
        afp_total=afp_pod["afp_total"],
        pod_sweetness=afp_pod["pod_sweetness"],
        de_total=afp_pod["de_total"],
        pac_total=afp_pod["pac_total"],
        sp_total=afp_pod["sp_total"],
        water_activity=aw,
    )
    @dataclass
class PasteMetrics:
    total_solids_pct: float
    fat_pct: float
    sugars_pct: float
    water_activity: float
    lactose_pct: float | None  # can be None if not computed

    # …whatever else you already have: afp_total, pac_total, pod, etc.
