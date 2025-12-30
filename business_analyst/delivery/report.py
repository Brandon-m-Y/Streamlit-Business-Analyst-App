"""Report generation."""

from typing import List
from datetime import datetime
from business_analyst.core.insight import Insight, Severity
from business_analyst.insights.explainer import ExplanationGenerator
from business_analyst.insights.prioritizer import InsightPrioritizer


class ReportGenerator:
    """
    Generates weekly business analyst reports.
    
    Combines insights with explanations into a readable report format.
    """
    
    def __init__(
        self,
        explainer: ExplanationGenerator,
        prioritizer: InsightPrioritizer
    ):
        """
        Initialize report generator.
        
        Args:
            explainer: Explanation generator
            prioritizer: Insight prioritizer
        """
        self.explainer = explainer
        self.prioritizer = prioritizer
    
    def generate(
        self,
        insights: List[Insight],
        business_name: str = "Business"
    ) -> str:
        """
        Generate a weekly report from insights.
        
        Args:
            insights: List of insights
            business_name: Name of the business
            
        Returns:
            Formatted report as string
        """
        # Prioritize insights
        prioritized = self.prioritizer.prioritize(insights)
        
        # Generate report sections
        sections = []
        
        # Header
        sections.append(self._generate_header(business_name))
        
        # Executive summary
        sections.append(self._generate_summary(prioritized))
        
        # Detailed insights
        sections.append(self._generate_insights_section(prioritized))
        
        # Footer
        sections.append(self._generate_footer())
        
        return "\n\n".join(sections)
    
    def _generate_header(self, business_name: str) -> str:
        """Generate report header."""
        return f"""
{'=' * 60}
WEEKLY BUSINESS ANALYST REPORT
{business_name}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'=' * 60}
"""
    
    def _generate_summary(self, insights: List[Insight]) -> str:
        """
        Generate executive summary focused on what needs attention.
        
        Framing emphasizes actionable items rather than technical severity counts.
        """
        summary_parts = ["## Executive Summary\n"]
        
        if not insights:
            summary_parts.append("✅ **No issues found.** Your business operations look healthy this week.")
            return "\n".join(summary_parts)
        
        # Count by severity for context
        severity_counts = {}
        critical_insights = []
        high_insights = []
        
        for insight in insights:
            severity = insight.severity.value
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            if insight.severity == Severity.CRITICAL:
                critical_insights.append(insight)
            elif insight.severity == Severity.HIGH:
                high_insights.append(insight)
        
        # Focus on what needs attention
        attention_items = []
        
        # Extract specific counts from stock-out risk insights
        # Only show CRITICAL items in executive summary to align with detailed insights
        stockout_insights = [i for i in insights if i.check_name == 'stockout_risk']
        if stockout_insights:
            for insight in stockout_insights:
                metrics = insight.metrics
                critical_count = metrics.get('critical_count', 0)
                
                if critical_count > 0:
                    if critical_count == 1:
                        attention_items.append("1 product needs immediate attention")
                    else:
                        attention_items.append(f"{critical_count} products need immediate attention")
        
        # Add other critical/high insights
        other_critical = [i for i in critical_insights if i.check_name != 'stockout_risk']
        other_high = [i for i in high_insights if i.check_name != 'stockout_risk']
        
        if other_critical:
            attention_items.append(f"{len(other_critical)} critical issue{'s' if len(other_critical) > 1 else ''} requiring immediate attention")
        if other_high:
            attention_items.append(f"{len(other_high)} high-priority item{'s' if len(other_high) > 1 else ''} to address")
        
        # Build summary text - only highlight most urgent items
        if attention_items:
            summary_parts.append("**What needs attention this week:**")
            for item in attention_items:
                summary_parts.append(f"- {item}")
        elif critical_insights:
            # Fallback: show critical items if no specific extraction
            summary_parts.append("**What needs attention this week:**")
            summary_parts.append(f"- {len(critical_insights)} item{'s' if len(critical_insights) > 1 else ''} requiring immediate attention")
        
        # Only show total if there are non-critical insights
        non_critical_count = len(insights) - len(critical_insights)
        if non_critical_count > 0:
            summary_parts.append(f"\nAdditional items to review: {non_critical_count}")
        
        return "\n".join(summary_parts)
    
    def _generate_insights_section(self, insights: List[Insight]) -> str:
        """Generate detailed insights section with SMB-friendly severity labels."""
        if not insights:
            return "## Insights\n\nNo insights to report."
        
        sections = ["## Detailed Insights\n"]
        
        # Map internal severity to SMB-friendly labels
        severity_labels = {
            Severity.CRITICAL: "Immediate attention",
            Severity.HIGH: "Action needed soon",
            Severity.MEDIUM: "Monitor",
            Severity.LOW: "Informational",
            Severity.INFO: "Informational",
        }
        
        for i, insight in enumerate(insights, 1):
            explanation = self.explainer.explain(insight)
            severity_label = severity_labels.get(insight.severity, insight.severity.value.title())
            
            sections.append(f"### {i}. {insight.title}")
            sections.append(f"**Priority:** {severity_label}")
            sections.append("")
            sections.append(explanation)
            sections.append("")
            sections.append("---")
            sections.append("")
        
        return "\n".join(sections)
    
    def _generate_footer(self) -> str:
        """Generate report footer."""
        return f"""
{'=' * 60}
Report generated by Business Analyst System
For questions or support, contact your system administrator
{'=' * 60}
"""

