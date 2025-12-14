"""
Lab Analysis Framework
Production-ready registry for sweet compositions
Separates VERIFIED (lab/kitchen tested) from ESTIMATED (formulas)
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json


# ============================================================================
# ENUMS
# ============================================================================

class DataSource(str, Enum):
    """Source of truth for composition data"""
    LAB_TESTED = "lab_tested"  # Professional lab analysis
    KITCHEN_TESTED = "kitchen_tested"  # Your validated kitchen batch
    PUBLISHED_RESEARCH = "published_research"  # Academic/industry papers
    ESTIMATED = "estimated"  # Mathematical calculation/formula


class ConfidenceLevel(str, Enum):
    """How much we trust this composition"""
    CERTIFIED = "certified"  # 95-100% confidence
    HIGHLY_TRUSTED = "highly_trusted"  # 85-95% confidence
    VALIDATED = "validated"  # 70-85% confidence
    DEVELOPING = "developing"  # 50-70% confidence
    PRELIMINARY = "preliminary"  # 30-50% confidence
    ESTIMATED = "estimated"  # <30% confidence


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class LabAnalysisResult:
    """Single composition analysis result"""
    sweet_name: str
    analysis_date: str  # ISO format: YYYY-MM-DD
    components: Dict[str, float]  # ingredient: percentage
    measurement_method: str  # e.g., "Kitchen Scale + Sensory Panel"
    tested_by: str  # person/team name
    data_source: DataSource
    confidence_level: int  # 0-100 scale
    batch_id: str  # unique identifier
    notes: str = ""
    batch_size_g: Optional[float] = None
    shelf_life_days: Optional[int] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for storage"""
        data = asdict(self)
        data['data_source'] = self.data_source.value
        return data


# ============================================================================
# MAIN FRAMEWORK CLASS
# ============================================================================

class LabAnalysisFramework:
    """
    Registry and manager for all sweet composition analyses.
    
    Keeps track of:
    - Which sweets have VERIFIED data (lab/kitchen tested)
    - Which sweets have ESTIMATED data (formulas only)
    - Confidence scores for each
    - Testing priority (what needs real data next)
    """
    
    def __init__(self):
        """Initialize with empty result registry"""
        self.results: List[LabAnalysisResult] = []
        self.sweet_aliases: Dict[str, str] = {
            "Gulab Jamun": "Gulab Jamun",
            "Jalebi": "Jalebi",
            "Rasgulla": "Rasgulla",
            "Barfi": "Barfi",
            "Kaju Katli": "Kaju Katli",
            "Peda": "Peda",
            "Sandesh": "Sandesh",
            "Mysore Pak": "Mysore Pak",
            "Laddu": "Laddu",
            "Halwa": "Halwa",
            "Kheer": "Kheer",
            "Rasmalai": "Rasmalai",
            "Kulfi": "Kulfi",
            "Coconut Barfi": "Coconut Barfi",
        }
    
    # ========================================================================
    # CORE METHODS
    # ========================================================================
    
    def add_result(self, result: LabAnalysisResult) -> Tuple[bool, str]:
        """
        Register a new composition analysis.
        
        Args:
            result: LabAnalysisResult object with all composition details
            
        Returns:
            (success: bool, message: str)
        """
        # Validate components sum to ~100%
        total_pct = sum(result.components.values())
        if not (95 <= total_pct <= 105):
            return False, f"Components must sum to ~100% (got {total_pct}%)"
        
        # Check for duplicates (same sweet, same batch_id)
        for existing in self.results:
            if (existing.sweet_name == result.sweet_name and 
                existing.batch_id == result.batch_id):
                return False, f"Batch {result.batch_id} already registered"
        
        # Add to registry
        self.results.append(result)
        return True, f"✅ Added {result.sweet_name} (confidence: {result.confidence_level}/100)"
    
    def get_confidence_for_sweet(self, sweet_name: str) -> Dict:
        """
        Get confidence level and data source for a sweet.
        
        Args:
            sweet_name: Name of sweet to check
            
        Returns:
            Dict with confidence data
        """
        results = self._get_results_for_sweet(sweet_name)
        
        if not results:
            return {
                "level": ConfidenceLevel.ESTIMATED.value,
                "score": 0,
                "data_source": DataSource.ESTIMATED.value,
                "batch_id": None,
                "safe_for_production": False,
                "message": f"No verified data for {sweet_name}"
            }
        
        # Get best (highest confidence) result
        best = max(results, key=lambda r: r.confidence_level)
        
        # Determine confidence level from score
        if best.confidence_level >= 95:
            level = ConfidenceLevel.CERTIFIED
        elif best.confidence_level >= 85:
            level = ConfidenceLevel.HIGHLY_TRUSTED
        elif best.confidence_level >= 70:
            level = ConfidenceLevel.VALIDATED
        elif best.confidence_level >= 50:
            level = ConfidenceLevel.DEVELOPING
        elif best.confidence_level >= 30:
            level = ConfidenceLevel.PRELIMINARY
        else:
            level = ConfidenceLevel.ESTIMATED
        
        # Safe for production if tested (not estimated) and >80% confidence
        safe = best.data_source != DataSource.ESTIMATED and best.confidence_level >= 80
        
        return {
            "level": level.value,
            "score": best.confidence_level,
            "data_source": best.data_source.value,
            "batch_id": best.batch_id,
            "safe_for_production": safe,
            "message": f"Confidence: {best.confidence_level}/100"
        }
    
    def get_best_composition(self, sweet_name: str) -> Optional[Dict]:
        """
        Get highest-confidence composition for a sweet.
        
        Args:
            sweet_name: Sweet to look up
            
        Returns:
            Dict with components, or None if not found
        """
        results = self._get_results_for_sweet(sweet_name)
        if not results:
            return None
        
        best = max(results, key=lambda r: r.confidence_level)
        return {
            "components": best.components,
            "confidence": best.confidence_level,
            "data_source": best.data_source.value,
            "batch_id": best.batch_id,
            "tested_by": best.tested_by,
            "analysis_date": best.analysis_date
        }
    
    def get_all_results_for_sweet(self, sweet_name: str) -> List[Dict]:
        """
        Get all composition analyses for a sweet (testing history).
        
        Args:
            sweet_name: Sweet to look up
            
        Returns:
            List of all results, newest first
        """
        results = self._get_results_for_sweet(sweet_name)
        # Sort by date, newest first
        results.sort(key=lambda r: r.analysis_date, reverse=True)
        return [r.to_dict() for r in results]
    
    def get_data_quality_summary(self) -> Dict:
        """
        Get overview of data quality across all sweets.
        
        Returns:
            Dict with verification statistics
        """
        sweets_verified = set()
        sweets_estimated = set()
        
        for result in self.results:
            if result.data_source == DataSource.ESTIMATED:
                sweets_estimated.add(result.sweet_name)
            else:
                sweets_verified.add(result.sweet_name)
        
        total = len(sweets_verified) + len(sweets_estimated)
        pct = (len(sweets_verified) / total * 100) if total > 0 else 0
        
        return {
            "total_sweets_in_db": total,
            "verified_sweets": sorted(list(sweets_verified)),
            "verified_count": len(sweets_verified),
            "estimated_sweets": sorted(list(sweets_estimated)),
            "estimated_count": len(sweets_estimated),
            "verification_percentage": round(pct, 1)
        }
    
    def get_testing_priority_list(self) -> List[Dict]:
        """
        Get list of sweets needing testing, ranked by importance.
        
        Returns:
            List of sweets, lowest confidence first
        """
        sweet_names = self.sweet_aliases.values()
        priorities = []
        
        for sweet in sweet_names:
            conf = self.get_confidence_for_sweet(sweet)
            priorities.append({
                "sweet_name": sweet,
                "confidence_score": conf["score"],
                "confidence_level": conf["level"],
                "data_source": conf["data_source"],
                "needs_testing": conf["score"] < 80,
                "priority": "HIGH" if conf["score"] < 50 else "MEDIUM" if conf["score"] < 80 else "LOW"
            })
        
        # Sort by confidence score, lowest first
        priorities.sort(key=lambda x: x["confidence_score"])
        return priorities
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def _get_results_for_sweet(self, sweet_name: str) -> List[LabAnalysisResult]:
        """Get all results for a specific sweet"""
        canonical_name = self.sweet_aliases.get(sweet_name, sweet_name)
        return [r for r in self.results if r.sweet_name == canonical_name]
    
    def export_to_json(self, filepath: str) -> bool:
        """Export all results to JSON file"""
        try:
            data = {
                "exported_at": datetime.now().isoformat(),
                "total_results": len(self.results),
                "results": [r.to_dict() for r in self.results]
            }
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Export failed: {e}")
            return False
    
    def import_from_json(self, filepath: str) -> Tuple[bool, str]:
        """Import results from JSON file"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            count = 0
            for result_dict in data.get("results", []):
                result_dict['data_source'] = DataSource(result_dict['data_source'])
                result = LabAnalysisResult(**result_dict)
                success, msg = self.add_result(result)
                if success:
                    count += 1
            
            return True, f"Imported {count} results"
        except Exception as e:
            return False, f"Import failed: {e}"


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    framework = LabAnalysisFramework()
    
    gulab_result = LabAnalysisResult(
        sweet_name="Gulab Jamun",
        analysis_date="2025-12-14",
        components={
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
        measurement_method="Kitchen Scale + Sensory Panel",
        tested_by="Your Team",
        data_source=DataSource.KITCHEN_TESTED,
        confidence_level=90,
        batch_id="GB_001_Dec14_2025",
        batch_size_g=500,
        shelf_life_days=120,
        notes="Authentic taste, safe for commercial use"
    )
    
    success, msg = framework.add_result(gulab_result)
    print(msg)
    
    conf = framework.get_confidence_for_sweet("Gulab Jamun")
    print(f"\nGulab Jamun Confidence: {conf}")
    
    priorities = framework.get_testing_priority_list()
    print(f"\nTesting Priority (top 3):")
    for p in priorities[:3]:
        print(f"  {p['sweet_name']}: {p['priority']} ({p['confidence_score']}/100)")
