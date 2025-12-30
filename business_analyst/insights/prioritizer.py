"""Insight prioritization."""

from typing import List
from business_analyst.core.insight import Insight, Severity


class InsightPrioritizer:
    """
    Prioritizes insights based on severity and business impact.
    
    Uses deterministic rules to order insights, ensuring
    the most important ones are presented first.
    """
    
    # Severity weights for prioritization
    SEVERITY_WEIGHTS = {
        Severity.CRITICAL: 100,
        Severity.HIGH: 75,
        Severity.MEDIUM: 50,
        Severity.LOW: 25,
        Severity.INFO: 10,
    }
    
    def prioritize(self, insights: List[Insight]) -> List[Insight]:
        """
        Prioritize a list of insights.
        
        Args:
            insights: List of insights to prioritize
            
        Returns:
            Prioritized list of insights
        """
        # Sort by severity weight (descending), then by timestamp (newest first)
        sorted_insights = sorted(
            insights,
            key=lambda i: (
                -self.SEVERITY_WEIGHTS.get(i.severity, 0),
                -i.timestamp.timestamp()
            )
        )
        
        return sorted_insights
    
    def get_critical(self, insights: List[Insight]) -> List[Insight]:
        """Get only critical insights."""
        return [i for i in insights if i.severity == Severity.CRITICAL]
    
    def get_by_severity(
        self,
        insights: List[Insight],
        min_severity: Severity
    ) -> List[Insight]:
        """
        Get insights at or above a minimum severity level.
        
        Args:
            insights: List of insights
            min_severity: Minimum severity level
            
        Returns:
            Filtered list of insights
        """
        min_weight = self.SEVERITY_WEIGHTS.get(min_severity, 0)
        return [
            i for i in insights
            if self.SEVERITY_WEIGHTS.get(i.severity, 0) >= min_weight
        ]

