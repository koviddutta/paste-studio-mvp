"""
Scientific constants for gelato formulation and property calculations.
Derived from FICSI and IDF standards.
"""


class GelatoConstants:
    """Physical and chemical constants for gelato science."""

    K_SUGAR = 6.47
    K_PROTEIN = 4.2
    K_INVERT = 5.2
    AW_MIN_OPTIMAL = 0.68
    AW_MAX_OPTIMAL = 0.75
    AW_MOLD_RISK = 0.8
    AW_BACTERIA_RISK = 0.85
    FAT_MIN = 10.0
    FAT_MAX = 20.0
    SUGAR_MIN = 20.0
    SUGAR_MAX = 40.0
    MSNF_MIN = 8.0
    MSNF_MAX = 12.0
    TOTAL_SOLIDS_MIN = 55.0
    TOTAL_SOLIDS_MAX = 70.0
    PASTEURIZATION_TEMP_HIGH = 85
    PASTEURIZATION_TIME_HIGH = 15
    PASTEURIZATION_TEMP_LOW = 65
    PASTEURIZATION_TIME_LOW = 1800
    HOMOGENIZATION_PRESSURE = 150
    AGING_TEMP = 4
    AGING_TIME_MIN = 4
    VISCOSITY_TARGET_PA_S = 10.0
    FLOW_INDEX_N = 0.6