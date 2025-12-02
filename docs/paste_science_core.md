# Paste Studio Science Core

This document defines the **data model**, **formulas**, and **workflow** for converting Indian sweets into stable pastes suitable for gelato, spreads, and fillings.

It is the single source of truth for the Paste Studio backend (not UI, not prompts).

---

## 1. Data Model

### 1.1 Ingredient

Every ingredient is represented as:

- `name` – string
- `quantity_g` – grams in the batch
- `sugars_pct` – % of the ingredient weight that is sugars
- `fat_pct` – % fat
- `msnf_pct` – % milk solids non-fat (lactose + proteins + minerals)
- `other_solids_pct` – % other non-fat, non-sugar solids (starch, fibre, cocoa solids, spices)
- `water_pct` – % water

All percentages are per-ingredient and should ideally sum to ~100%.

In code this maps to a dataclass:

```python
@dataclass
class Ingredient:
    name: str
    quantity_g: float
    sugars_pct: float = 0.0
    fat_pct: float = 0.0
    msnf_pct: float = 0.0
    other_solids_pct: float = 0.0
    water_pct: float = 0.0
