"""
Data Confidence Dashboard
Production-ready system for tracking and displaying data quality across all sweets
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional
from datetime import datetime


# ============================================================================
# ENUMS
# ============================================================================

class ConfidenceLevel(str, Enum):
    """Overall confidence in sweet data"""
    CERTIFIED = "certified"  # Professional lab analysis (95-100%)
    HIGHLY_TRUSTED = "highly_trusted"  # Multiple kitchen tests (85-95%)
    VALIDATED = "validated"  # Kitchen tested with good results (70-85%)
    DEVELOPING = "developing"  # Some testing, needs more (50-70%)
    PRELIMINARY = "preliminary"  # Initial testing only (30-50%)
    ESTIMATED = "estimated"  # Formula only, no testing (<30%)


class ProductionReadiness(str, Enum):
    """Can this be used in production?"""
    READY = "ready"
    CONDITIONAL = "conditional"
    NOT_READY = "not_ready"


# ============================================================================
# DATA CLASS
# ============================================================================

@dataclass
class SweetConfidenceData:
    """Confidence data for a single sweet"""
    sweet_name: str
    confidence_level: ConfidenceLevel
    confidence_score: int  # 0-100
    data_source: str
    batches_tested: int
    production_ready: ProductionReadiness
    warning_message: Optional[str]
    last_updated: str
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "sweet_name": self.sweet_name,
            "confidence_level": self.confidence_level.value,
            "confidence_score": self.confidence_score,
            "data_source": self.data_source,
            "batches_tested": self.batches_tested,
            "production_ready": self.production_ready.value,
            "warning_message": self.warning_message,
            "last_updated": self.last_updated
        }


# ============================================================================
# MAIN DASHBOARD CLASS
# ============================================================================

class DataConfidenceDashboard:
    """
    Central system for tracking data confidence across all sweets.
    
    Keeps track of:
    - Which sweets have VERIFIED data (safe for production)
    - Which sweets have ESTIMATED data (use with caution)
    - What warnings to show users
    - Which sweets need testing next
    """
    
    def __init__(self):
        """Initialize with all 14 sweets in ESTIMATED state"""
        self.sweet_data: Dict[str, SweetConfidenceData] = {}
        self._initialize_sweets()
    
    def _initialize_sweets(self):
        """Set up all 14 sweets as ESTIMATED (no real data yet)"""
        sweets = [
            "Gulab Jamun",
            "Jalebi",
            "Rasgulla",
            "Barfi",
            "Kaju Katli",
            "Peda",
            "Sandesh",
            "Mysore Pak",
            "Laddu",
            "Halwa",
            "Kheer",
            "Rasmalai",
            "Kulfi",
            "Coconut Barfi"
        ]
        
        for sweet in sweets:
            self.sweet_data[sweet] = SweetConfidenceData(
                sweet_name=sweet,
                confidence_level=ConfidenceLevel.ESTIMATED,
                confidence_score=0,
                data_source="estimated",
                batches_tested=0,
                production_ready=ProductionReadiness.NOT_READY,
                warning_message=f"⚠️ {sweet}: No verified data. Using formula only.",
                last_updated=datetime.now().isoformat()
            )
    
    # ========================================================================
    # CORE METHODS
    # ========================================================================
    
    def mark_as_tested(
        self,
        sweet_name: str,
        confidence: int,
        tested_date: Optional[str] = None,
        tested_by: Optional[str] = None,
        notes: str = ""
    ) -> bool:
        """
        Mark a sweet as tested (move from ESTIMATED to VALIDATED/CERTIFIED).
        """
        if sweet_name not in self.sweet_data:
            print(f"Sweet {sweet_name} not in database")
            return False
        
        if not (0 <= confidence <= 100):
            print("Confidence must be 0-100")
            return False
        
        tested_date = tested_date or datetime.now().isoformat()
        
        # Determine confidence level from score
        if confidence >= 95:
            level = ConfidenceLevel.CERTIFIED
        elif confidence >= 85:
            level = ConfidenceLevel.HIGHLY_TRUSTED
        elif confidence >= 70:
            level = ConfidenceLevel.VALIDATED
        elif confidence >= 50:
            level = ConfidenceLevel.DEVELOPING
        elif confidence >= 30:
            level = ConfidenceLevel.PRELIMINARY
        else:
            level = ConfidenceLevel.ESTIMATED
        
        # Determine readiness
        if level == ConfidenceLevel.CERTIFIED:
            readiness = ProductionReadiness.READY
            warning = f"✅ {sweet_name}: Certified for production"
        elif level == ConfidenceLevel.HIGHLY_TRUSTED:
            readiness = ProductionReadiness.READY
            warning = f"✅ {sweet_name}: Highly trusted. Production ready."
        elif level == ConfidenceLevel.VALIDATED:
            readiness = ProductionReadiness.READY
            warning = f"✅ {sweet_name}: Validated. Production ready."
        elif level == ConfidenceLevel.DEVELOPING:
            readiness = ProductionReadiness.CONDITIONAL
            warning = f"⚠️ {sweet_name}: Under development. Monitor quality."
        elif level == ConfidenceLevel.PRELIMINARY:
            readiness = ProductionReadiness.CONDITIONAL
            warning = f"⚠️ {sweet_name}: Preliminary data. More testing needed."
        else:
            readiness = ProductionReadiness.NOT_READY
            warning = f"❌ {sweet_name}: No verified data. Using formula only."
        
        # Update data
        self.sweet_data[sweet_name] = SweetConfidenceData(
            sweet_name=sweet_name,
            confidence_level=level,
            confidence_score=confidence,
            data_source="kitchen_tested" if confidence >= 50 else "estimated",
            batches_tested=self.sweet_data[sweet_name].batches_tested + 1,
            production_ready=readiness,
            warning_message=warning + (f" ({tested_by})" if tested_by else "") + (f" - {notes}" if notes else ""),
            last_updated=tested_date
        )
        
        return True
    
    def get_sweet_confidence(self, sweet_name: str) -> Dict:
        """Get confidence data for a specific sweet"""
        if sweet_name not in self.sweet_data:
            return {
                "error": f"Sweet {sweet_name} not found",
                "sweet_name": sweet_name
            }
        
        data = self.sweet_data[sweet_name]
        return data.to_dict()
    
    def can_use_in_production(self, sweet_name: str) -> bool:
        """Check if a sweet is safe to use in production"""
        if sweet_name not in self.sweet_data:
            return False
        
        data = self.sweet_data[sweet_name]
        return data.production_ready in [
            ProductionReadiness.READY,
            ProductionReadiness.CONDITIONAL
        ]
    
    def get_production_ready_sweets(self) -> List[Dict]:
        """Get all sweets that are READY for production"""
        ready = []
        for sweet_name, data in self.sweet_data.items():
            if data.production_ready == ProductionReadiness.READY:
                ready.append(data.to_dict())
        
        # Sort by confidence score, highest first
        ready.sort(key=lambda x: x["confidence_score"], reverse=True)
        return ready
    
    def get_testing_needed_sweets(self) -> List[Dict]:
        """Get all sweets that need testing"""
        needs_testing = []
        for sweet_name, data in self.sweet_data.items():
            if data.production_ready != ProductionReadiness.READY:
                needs_testing.append(data.to_dict())
        
        # Sort by confidence score, lowest first
        needs_testing.sort(key=lambda x: x["confidence_score"])
        return needs_testing
    
    def get_warning_for_sweet(self, sweet_name: str) -> Optional[str]:
        """Get user-facing warning message for a sweet"""
        if sweet_name not in self.sweet_data:
            return f"Unknown sweet: {sweet_name}"
        
        data = self.sweet_data[sweet_name]
        
        # Only show warning if NOT ready
        if data.production_ready == ProductionReadiness.NOT_READY:
            return data.warning_message
        elif data.production_ready == ProductionReadiness.CONDITIONAL:
            return data.warning_message
        
        return None
    
    def get_dashboard_summary(self) -> Dict:
        """Get overall dashboard summary"""
        ready = []
        conditional = []
        not_ready = []
        
        for data in self.sweet_data.values():
            if data.production_ready == ProductionReadiness.READY:
                ready.append(data.sweet_name)
            elif data.production_ready == ProductionReadiness.CONDITIONAL:
                conditional.append(data.sweet_name)
            else:
                not_ready.append(data.sweet_name)
        
        total = len(self.sweet_data)
        verified = len(ready) + len(conditional)
        pct = (verified / total * 100) if total > 0 else 0
        
        # Count by confidence level
        by_level = {}
        for level in ConfidenceLevel:
            count = len([d for d in self.sweet_data.values() if d.confidence_level == level])
            if count > 0:
                by_level[level.value] = count
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_sweets": total,
            "production_ready_count": len(ready),
            "conditional_count": len(conditional),
            "not_ready_count": len(not_ready),
            "production_ready": sorted(ready),
            "conditional": sorted(conditional),
            "not_ready": sorted(not_ready),
            "verification_percentage": round(pct, 1),
            "by_confidence_level": by_level,
            "next_priority": sorted(self.get_testing_needed_sweets(), key=lambda x: x["confidence_score"])[0]["sweet_name"] if not_ready or conditional else None
        }
    
    def generate_report(self) -> str:
        """Generate human-readable dashboard report"""
        summary = self.get_dashboard_summary()
        
        lines = [
            "=" * 70,
            "DATA CONFIDENCE DASHBOARD",
            f"Generated: {summary['timestamp']}",
            "=" * 70,
            "",
            f"📊 OVERALL STATUS",
            f"  Total Sweets: {summary['total_sweets']}",
            f"  Production Ready: {summary['production_ready_count']}/{summary['total_sweets']} ({summary['verification_percentage']}%)",
            f"  Conditional: {summary['conditional_count']}",
            f"  Needs Testing: {summary['not_ready_count']}",
            "",
            "✅ PRODUCTION READY SWEETS",
        ]
        
        if summary['production_ready']:
            for sweet in summary['production_ready']:
                data = self.sweet_data[sweet]
                lines.append(f"  • {sweet} (Confidence: {data.confidence_score}/100)")
        else:
            lines.append("  (None yet)")
        
        lines.extend([
            "",
            "⚠️ CONDITIONAL SWEETS (Monitor Quality)",
        ])
        
        if summary['conditional']:
            for sweet in summary['conditional']:
                data = self.sweet_data[sweet]
                lines.append(f"  • {sweet} (Confidence: {data.confidence_score}/100)")
        else:
            lines.append("  (None)")
        
        lines.extend([
            "",
            "🔬 SWEETS NEEDING TESTING",
        ])
        
        if summary['not_ready']:
            for sweet in summary['not_ready']:
                data = self.sweet_data[sweet]
                level = "HIGH" if data.confidence_score < 50 else "MEDIUM"
                lines.append(f"  {level:6s} - {sweet:15s} (Confidence: {data.confidence_score:3d}/100)")
        else:
            lines.append("  (All tested!)")
        
        lines.extend([
            "",
            "📌 NEXT PRIORITY",
            f"  {summary['next_priority'] if summary['next_priority'] else 'All sweets verified!'}",
            "",
            "=" * 70,
        ])
        
        return "\n".join(lines)
    
    def get_status_for_formulation_engine(self, sweet_name: str) -> Dict:
        """Get status info for formulation engine to display"""
        if sweet_name not in self.sweet_data:
            return {
                "warning_level": "unknown",
                "message": f"Unknown sweet: {sweet_name}"
            }
        
        data = self.sweet_data[sweet_name]
        
        if data.production_ready == ProductionReadiness.READY:
            return {
                "warning_level": "none",
                "message": f"✅ {data.warning_message}",
                "badge": "VERIFIED DATA",
                "color": "green"
            }
        elif data.production_ready == ProductionReadiness.CONDITIONAL:
            return {
                "warning_level": "warning",
                "message": f"⚠️ {data.warning_message}",
                "badge": "PRELIMINARY DATA",
                "color": "yellow"
            }
        else:
            return {
                "warning_level": "error",
                "message": f"❌ {data.warning_message}",
                "badge": "FORMULA ONLY",
                "color": "red"
            }


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    dashboard = DataConfidenceDashboard()
    
    # Mark Gulab Jamun as tested
    dashboard.mark_as_tested(
        "Gulab Jamun",
        confidence=90,
        tested_by="Your Team",
        notes="Kitchen batch verified"
    )
    
    # Check if safe
    print(f"Safe for production: {dashboard.can_use_in_production('Gulab Jamun')}")
    
    # Get status for display
    status = dashboard.get_status_for_formulation_engine("Gulab Jamun")
    print(f"Status: {status['badge']}")
    
    # Print full report
    print(dashboard.generate_report())
