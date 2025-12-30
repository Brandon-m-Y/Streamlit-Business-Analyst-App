"""Natural language explanation generation."""

from typing import List, Optional, Any
from business_analyst.core.insight import Insight


class ExplanationGenerator:
    """
    Generates natural language explanations for insights.
    
    This layer can use LLMs for explanation generation, but never
    for decision-making. All insights are already determined by
    deterministic checks before reaching this layer.
    """
    
    def __init__(self, llm_client: Optional[Any] = None):
        """
        Initialize explanation generator.
        
        Args:
            llm_client: Optional LLM client for generating explanations.
                       If None, uses template-based explanations.
        """
        self.llm_client = llm_client
        self._use_llm = llm_client is not None
    
    def explain(self, insight: Insight) -> str:
        """
        Generate a natural language explanation for an insight.
        
        Args:
            insight: Insight to explain
            
        Returns:
            Natural language explanation
        """
        if self._use_llm:
            return self._explain_with_llm(insight)
        else:
            return self._explain_with_template(insight)
    
    def _explain_with_template(self, insight: Insight) -> str:
        """
        Generate explanation using templates.
        
        This is the default deterministic method.
        """
        explanation_parts = [
            f"**{insight.title}**",
            "",
            insight.description,
        ]
        
        if insight.recommendation:
            explanation_parts.extend([
                "",
                "**Recommendation:**",
                insight.recommendation,
            ])
        
        # Add key metrics
        if insight.metrics:
            explanation_parts.extend([
                "",
                "**Key Metrics:**",
            ])
            for key, value in insight.metrics.items():
                if not key.startswith('_'):
                    if isinstance(value, float):
                        explanation_parts.append(f"- {key}: {value:.2f}")
                    else:
                        explanation_parts.append(f"- {key}: {value}")
        
        return "\n".join(explanation_parts)
    
    def _explain_with_llm(self, insight: Insight) -> str:
        """
        Generate explanation using LLM.
        
        This is optional and only used for explanation generation,
        never for decision-making.
        """
        # Placeholder for LLM-based explanation
        # In production, this would call the LLM client with the insight
        # and return a more natural explanation
        
        # For now, fall back to template
        return self._explain_with_template(insight)
    
    def explain_all(self, insights: List[Insight]) -> List[str]:
        """
        Generate explanations for all insights.
        
        Args:
            insights: List of insights
            
        Returns:
            List of explanations in the same order
        """
        return [self.explain(insight) for insight in insights]

