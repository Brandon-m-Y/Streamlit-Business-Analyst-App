"""Registry for analyst checks."""

from typing import List, Dict, Type
from business_analyst.checks.base import AnalystCheck
from business_analyst.checks.stockout_risk import StockOutRiskCheck


class CheckRegistry:
    """
    Registry for managing analyst checks.
    
    Allows checks to be registered and discovered automatically.
    New checks can be added without modifying existing code.
    """
    
    def __init__(self):
        """Initialize registry with default checks."""
        self._checks: Dict[str, AnalystCheck] = {}
        self._register_defaults()
    
    def _register_defaults(self) -> None:
        """Register default checks."""
        self.register(StockOutRiskCheck())
    
    def register(self, check: AnalystCheck) -> None:
        """
        Register an analyst check.
        
        Args:
            check: AnalystCheck instance
        """
        if not isinstance(check, AnalystCheck):
            raise TypeError("Check must be an instance of AnalystCheck")
        
        self._checks[check.name] = check
    
    def get(self, name: str) -> AnalystCheck:
        """
        Get a check by name.
        
        Args:
            name: Check name
            
        Returns:
            AnalystCheck instance
            
        Raises:
            KeyError: If check not found
        """
        if name not in self._checks:
            raise KeyError(f"Check '{name}' not found in registry")
        return self._checks[name]
    
    def list_all(self) -> List[AnalystCheck]:
        """List all registered checks."""
        return list(self._checks.values())
    
    def get_applicable(
        self,
        context
    ) -> List[AnalystCheck]:
        """
        Get all checks applicable to the given context.
        
        Args:
            context: Business context
            
        Returns:
            List of applicable checks
        """
        return [
            check for check in self._checks.values()
            if check.is_applicable(context)
        ]

