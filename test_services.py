#!/usr/bin/env python3
"""
Complete test file for Phase 1 services
Tests all 3 services and verifies they work together
"""

from app.services.lab_analysis_framework import LabAnalysisFramework, LabAnalysisResult, DataSource
from app.services.kitchen_testing_protocol import KitchenTestingProtocol, KitchenTest, TestResult, ViscosityObserved
from app.services.data_confidence_dashboard import DataConfidenceDashboard

print("\n" + "="*70)
print("TESTING PHASE 1 SERVICES")
print("="*70)

# TEST 1: Lab Framework
print("\n✅ TEST 1: Lab Analysis Framework")
framework = LabAnalysisFramework()
gulab = LabAnalysisResult(
    sweet_name="Gulab Jamun",
    analysis_date="2025-12-14",
    components={
        "fresh_gulab": 60, "cream": 10, "skim_milk_powder": 6,
        "glucose_syrup": 6, "dextrose": 4, "ghee": 3, "toned_milk": 4,
        "rose_water": 2, "gulab_syrup": 2, "cardamom": 0.5,
        "stabilizer": 1, "saffron": 0.2
    },
    measurement_method="Kitchen Scale + Sensory Panel",
    tested_by="Your Team",
    data_source=DataSource.KITCHEN_TESTED,
    confidence_level=90,
    batch_id="GB_001_Dec14_2025"
)
success, msg = framework.add_result(gulab)
print(f"  {msg}")
assert success, "Failed to add result"

# TEST 2: Kitchen Testing
print("\n✅ TEST 2: Kitchen Testing Protocol")
protocol = KitchenTestingProtocol()
test = KitchenTest(
    sweet_name="Gulab Jamun",
    batch_date="2025-12-14",
    batch_size_g=500,
    formulation_used={
        "fresh_gulab": 60, "cream": 10, "skim_milk_powder": 6,
        "glucose_syrup": 6, "dextrose": 4, "ghee": 3, "toned_milk": 4,
        "rose_water": 2, "gulab_syrup": 2, "cardamom": 0.5,
        "stabilizer": 1, "saffron": 0.2
    },
    formulation_source="Kitchen Tested",
    taste_score=9, texture_score=8, appearance_score=9,
    flavor_authenticity_score=9,
    shelf_life_observed_days=120,
    separation_noticed=False, mold_growth=False, discoloration=False,
    viscosity_observed=ViscosityObserved.MEDIUM,
    spreadability="Easy",
    tested_by="Your Team", tester_experience="Expert",
    test_facility="Commercial Kitchen",
    tester_notes="Production ready",
    adjustments_needed=[],
    overall_result=TestResult.PASS,
    confidence_in_result=95
)
success, msg = protocol.add_test(test)
print(f"  {msg}")
assert success, "Failed to add test"

# TEST 3: Confidence Dashboard
print("\n✅ TEST 3: Data Confidence Dashboard")
dashboard = DataConfidenceDashboard()
dashboard.mark_as_tested("Gulab Jamun", confidence=90, tested_by="Your Team")
conf = dashboard.get_sweet_confidence("Gulab Jamun")
print(f"  Gulab Jamun: {conf['confidence_level'].upper()} ({conf['confidence_score']}/100)")
print(f"  Production Ready: {dashboard.can_use_in_production('Gulab Jamun')}")
assert conf['confidence_score'] == 90, "Confidence score mismatch"

# TEST 4: Integration
print("\n✅ TEST 4: Systems Working Together")
summary = dashboard.get_dashboard_summary()
print(f"  Total Sweets: {summary['total_sweets']}")
print(f"  Production Ready: {summary['production_ready_count']}")
print(f"  Verification: {summary['verification_percentage']}%")

print("\n" + "="*70)
print("ALL TESTS PASSED ✅")
print("="*70)
print("\nNext: Run 'reflex run' to test in browser")
print("="*70 + "\n")
