"""
Kitchen Testing Protocol
Production-ready batch testing and quality scoring system
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json


# ============================================================================
# ENUMS
# ============================================================================

class TestResult(str, Enum):
    """Outcome of kitchen test"""
    PASS = "pass"
    NEEDS_MINOR_ADJUSTMENT = "needs_minor_adjustment"
    NEEDS_MAJOR_ADJUSTMENT = "needs_major_adjustment"
    FAILED = "failed"


class ViscosityObserved(str, Enum):
    """Observed viscosity during test"""
    VERY_THIN = "very_thin"
    THIN = "thin"
    MEDIUM = "medium"
    THICK = "thick"
    VERY_THICK = "very_thick"


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class KitchenTest:
    """Single batch kitchen test result"""
    sweet_name: str
    batch_date: str  # ISO format: YYYY-MM-DD
    batch_size_g: float
    formulation_used: Dict[str, float]
    formulation_source: str
    
    # Sensory Scores (0-10)
    taste_score: int
    texture_score: int
    appearance_score: int
    flavor_authenticity_score: int
    
    # Stability Observations
    shelf_life_observed_days: int
    separation_noticed: bool
    mold_growth: bool
    discoloration: bool
    viscosity_observed: ViscosityObserved
    spreadability: str
    
    # Metadata
    tested_by: str
    tester_experience: str
    test_facility: str
    tester_notes: str
    adjustments_needed: List[str]
    overall_result: TestResult
    confidence_in_result: int
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for storage"""
        data = asdict(self)
        data['viscosity_observed'] = self.viscosity_observed.value
        data['overall_result'] = self.overall_result.value
        return data
    
    def get_quality_score(self) -> int:
        """Calculate overall quality score (0-100)"""
        # Weight sensory scores
        sensory_avg = (
            self.taste_score +
            self.texture_score +
            self.appearance_score +
            self.flavor_authenticity_score
        ) / 4 * 10  # Convert to 0-100
        
        # Stability penalty
        stability_score = 100
        if self.separation_noticed:
            stability_score -= 20
        if self.mold_growth:
            stability_score -= 30
        if self.discoloration:
            stability_score -= 10
        
        # Shelf life bonus
        shelf_bonus = min(20, self.shelf_life_observed_days / 6)
        
        # Result weighting
        result_factor = {
            TestResult.PASS: 100,
            TestResult.NEEDS_MINOR_ADJUSTMENT: 75,
            TestResult.NEEDS_MAJOR_ADJUSTMENT: 40,
            TestResult.FAILED: 0
        }[self.overall_result]
        
        # Final score
        final = (
            sensory_avg * 0.4 +
            stability_score * 0.3 +
            shelf_bonus * 0.1 +
            result_factor * 0.2
        )
        
        return int(round(max(0, min(100, final))))


# ============================================================================
# MAIN PROTOCOL CLASS
# ============================================================================

class KitchenTestingProtocol:
    """
    Record and analyze kitchen batch tests.
    """
    
    def __init__(self):
        """Initialize with empty test registry"""
        self.tests: List[KitchenTest] = []
    
    # ========================================================================
    # CORE METHODS
    # ========================================================================
    
    def add_test(self, test: KitchenTest) -> Tuple[bool, str]:
        """
        Register a new kitchen test.
        
        Args:
            test: KitchenTest object with all sensory and stability data
            
        Returns:
            (success: bool, message: str)
        """
        # Validate scores are 0-10
        scores = [
            test.taste_score,
            test.texture_score,
            test.appearance_score,
            test.flavor_authenticity_score,
            test.confidence_in_result / 10  # 0-100 → 0-10
        ]
        
        for score in scores:
            if not (0 <= score <= 10):
                return False, "All sensory scores must be 0-10"
        
        # Validate formulation sums to ~100%
        total_pct = sum(test.formulation_used.values())
        if not (95 <= total_pct <= 105):
            return False, f"Formulation must sum to ~100% (got {total_pct}%)"
        
        # Add to registry
        self.tests.append(test)
        quality_score = test.get_quality_score()
        
        return True, f"✅ Test recorded: {test.sweet_name} (Quality: {quality_score}/100)"
    
    def get_tests_for_sweet(self, sweet_name: str) -> List[Dict]:
        """Get all tests for a specific sweet, newest first"""
        tests = [t for t in self.tests if t.sweet_name == sweet_name]
        tests.sort(key=lambda t: t.batch_date, reverse=True)
        return [t.to_dict() for t in tests]
    
    def get_best_test_for_sweet(self, sweet_name: str) -> Optional[Dict]:
        """Get highest quality test for a sweet"""
        tests = [t for t in self.tests if t.sweet_name == sweet_name]
        if not tests:
            return None
        
        best = max(tests, key=lambda t: t.get_quality_score())
        result_dict = best.to_dict()
        result_dict['quality_score'] = best.get_quality_score()
        return result_dict
    
    def get_summary_for_sweet(self, sweet_name: str) -> Dict:
        """Get comprehensive test summary for a sweet"""
        tests = [t for t in self.tests if t.sweet_name == sweet_name]
        
        if not tests:
            return {
                "total_batches_tested": 0,
                "average_quality_score": 0,
                "best_batch": None,
                "latest_batch": None,
                "improvements_needed": ["No tests recorded yet"],
                "recommendation": "⚠️ Run first kitchen test",
                "ready_for_production": False
            }
        
        # Calculate metrics
        quality_scores = [t.get_quality_score() for t in tests]
        avg_quality = sum(quality_scores) / len(quality_scores)
        
        best = max(tests, key=lambda t: t.get_quality_score())
        tests_sorted = sorted(tests, key=lambda t: t.batch_date, reverse=True)
        latest = tests_sorted[0]
        
        # Determine recommendation
        if avg_quality >= 85:
            recommendation = "✅ PRODUCTION READY - All tests passed"
            ready = True
        elif avg_quality >= 70:
            recommendation = "⚠️ ACCEPTABLE - Minor adjustments may help"
            ready = True
        elif avg_quality >= 50:
            recommendation = "🔄 NEEDS WORK - Major adjustments required"
            ready = False
        else:
            recommendation = "❌ NOT SUITABLE - Consider different formulation"
            ready = False
        
        return {
            "sweet_name": sweet_name,
            "total_batches_tested": len(tests),
            "average_quality_score": round(avg_quality, 1),
            "best_batch": {
                "date": best.batch_date,
                "quality_score": best.get_quality_score(),
                "result": best.overall_result.value
            },
            "latest_batch": {
                "date": latest.batch_date,
                "quality_score": latest.get_quality_score(),
                "result": latest.overall_result.value
            },
            "improvements_needed": latest.adjustments_needed if latest.adjustments_needed else ["None - batch is good"],
            "recommendation": recommendation,
            "ready_for_production": ready and latest.overall_result in [TestResult.PASS, TestResult.NEEDS_MINOR_ADJUSTMENT]
        }
    
    def get_improvement_trends(self, sweet_name: str) -> Dict:
        """Get quality trend over multiple batches"""
        tests = [t for t in self.tests if t.sweet_name == sweet_name]
        tests.sort(key=lambda t: t.batch_date)
        
        if len(tests) < 2:
            return {
                "sweet_name": sweet_name,
                "batches_analyzed": len(tests),
                "trend": "INSUFFICIENT_DATA",
                "scores_timeline": [t.get_quality_score() for t in tests],
                "improvement_rate": None,
                "message": "Need at least 2 tests to analyze trend"
            }
        
        scores = [t.get_quality_score() for t in tests]
        first_score = scores[0]
        last_score = scores[-1]
        improvement = last_score - first_score
        
        if improvement > 5:
            trend = "IMPROVING"
        elif improvement < -5:
            trend = "DECLINING"
        else:
            trend = "STABLE"
        
        return {
            "sweet_name": sweet_name,
            "batches_analyzed": len(tests),
            "trend": trend,
            "first_score": first_score,
            "last_score": last_score,
            "total_improvement": improvement,
            "scores_timeline": scores,
            "dates_timeline": [t.batch_date for t in tests],
            "improvement_rate": round(improvement / (len(tests) - 1), 2)
        }
    
    def compare_formulations(self, sweet_name: str) -> Dict:
        """Compare quality across different formulations"""
        tests = [t for t in self.tests if t.sweet_name == sweet_name]
        
        if not tests:
            return {
                "sweet_name": sweet_name,
                "formulations_tested": 0,
                "comparison": []
            }
        
        # Group by formulation source
        by_source = {}
        for test in tests:
            source = test.formulation_source
            if source not in by_source:
                by_source[source] = []
            by_source[source].append(test.get_quality_score())
        
        comparison = []
        for source, scores in by_source.items():
            comparison.append({
                "formulation_source": source,
                "batches": len(scores),
                "average_quality": round(sum(scores) / len(scores), 1),
                "best_quality": max(scores),
                "worst_quality": min(scores)
            })
        
        # Sort by average quality, best first
        comparison.sort(key=lambda x: x['average_quality'], reverse=True)
        
        return {
            "sweet_name": sweet_name,
            "formulations_tested": len(by_source),
            "comparison": comparison,
            "recommendation": f"Best formulation: {comparison[0]['formulation_source']}" if comparison else "No data"
        }
    
    def generate_testing_checklist(self, sweet_name: str) -> Dict:
        """Generate checklist for next kitchen test"""
        latest = self.get_best_test_for_sweet(sweet_name)
        
        checklist = {
            "sweet_name": sweet_name,
            "checklist": [
                {"task": "Weigh all ingredients", "category": "Preparation"},
                {"task": "Mix according to formulation", "category": "Preparation"},
                {"task": "Record batch time", "category": "Preparation"},
                {"task": "Taste and score flavor (0-10)", "category": "Sensory"},
                {"task": "Evaluate texture/mouthfeel (0-10)", "category": "Sensory"},
                {"task": "Score appearance (0-10)", "category": "Sensory"},
                {"task": "Rate authenticity (0-10)", "category": "Sensory"},
                {"task": "Check for separation", "category": "Stability"},
                {"task": "Check for mold or discoloration", "category": "Stability"},
                {"task": "Note spreadability", "category": "Stability"},
                {"task": "Record shelf life observations", "category": "Stability"},
                {"task": "Document any adjustments needed", "category": "Notes"},
                {"task": "Rate tester confidence (0-100)", "category": "Notes"},
            ],
            "previous_results": latest.get("overall_result") if latest else None,
            "tips": "If previous test was poor, focus on the adjustments_needed items"
        }
        
        return checklist
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def export_to_json(self, filepath: str) -> bool:
        """Export all tests to JSON file"""
        try:
            data = {
                "exported_at": datetime.now().isoformat(),
                "total_tests": len(self.tests),
                "tests": [t.to_dict() for t in self.tests]
            }
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Export failed: {e}")
            return False
    
    def import_from_json(self, filepath: str) -> Tuple[bool, str]:
        """Import tests from JSON file"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            count = 0
            for test_dict in data.get("tests", []):
                test_dict['viscosity_observed'] = ViscosityObserved(test_dict['viscosity_observed'])
                test_dict['overall_result'] = TestResult(test_dict['overall_result'])
                test = KitchenTest(**test_dict)
                success, msg = self.add_test(test)
                if success:
                    count += 1
            
            return True, f"Imported {count} tests"
        except Exception as e:
            return False, f"Import failed: {e}"


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    protocol = KitchenTestingProtocol()
    
    test = KitchenTest(
        sweet_name="Gulab Jamun",
        batch_date="2025-12-14",
        batch_size_g=500,
        formulation_used={
            "fresh_gulab": 60,
            "cream": 10,
            "skim_milk_powder": 6,
            "glucose_syrup": 6,
            "dextrose": 4,
            "ghee": 3,
            "toned_milk": 4,
            "rose_water": 2,
            "gulab_syrup": 2,
            "cardamom": 0.5,
            "stabilizer": 1,
            "saffron": 0.2
        },
        formulation_source="Kitchen Tested",
        taste_score=9,
        texture_score=8,
        appearance_score=9,
        flavor_authenticity_score=9,
        shelf_life_observed_days=120,
        separation_noticed=False,
        mold_growth=False,
        discoloration=False,
        viscosity_observed=ViscosityObserved.MEDIUM,
        spreadability="Easy",
        tested_by="Your Team",
        tester_experience="Expert",
        test_facility="Commercial Kitchen",
        tester_notes="Authentic and production-ready",
        adjustments_needed=[],
        overall_result=TestResult.PASS,
        confidence_in_result=95
    )
    
    success, msg = protocol.add_test(test)
    print(msg)
    
    summary = protocol.get_summary_for_sweet("Gulab Jamun")
    print(f"\nSummary:")
    print(f"  Quality: {summary['average_quality_score']}/100")
    print(f"  Recommendation: {summary['recommendation']}")
    print(f"  Production Ready: {summary['ready_for_production']}")
