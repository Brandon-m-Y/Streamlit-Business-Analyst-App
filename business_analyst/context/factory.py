"""Factory for creating business contexts."""

from typing import Dict, Type
from business_analyst.context.base import BusinessContext
from business_analyst.context.retail import RetailContext
from business_analyst.core.exceptions import ContextError


class BusinessContextFactory:
    """
    Factory for creating industry-specific business contexts.
    
    Supports multiple industries without large conditionals by using
    a registry pattern.
    """
    
    _contexts: Dict[str, Type[BusinessContext]] = {
        'retail': RetailContext,
    }
    
    @classmethod
    def create(cls, industry: str) -> BusinessContext:
        """
        Create a business context for the specified industry.
        
        Args:
            industry: Industry name (e.g., 'retail')
            
        Returns:
            BusinessContext instance
            
        Raises:
            ContextError: If industry is not supported
        """
        industry_lower = industry.lower()
        
        if industry_lower not in cls._contexts:
            available = ', '.join(cls._contexts.keys())
            raise ContextError(
                f"Industry '{industry}' not supported. "
                f"Available industries: {available}"
            )
        
        context_class = cls._contexts[industry_lower]
        return context_class()
    
    @classmethod
    def register(cls, industry: str, context_class: Type[BusinessContext]) -> None:
        """
        Register a new industry context.
        
        Args:
            industry: Industry name
            context_class: BusinessContext subclass
        """
        if not issubclass(context_class, BusinessContext):
            raise ContextError(
                f"Context class must be a subclass of BusinessContext"
            )
        
        cls._contexts[industry.lower()] = context_class
    
    @classmethod
    def list_industries(cls) -> list:
        """List all supported industries."""
        return list(cls._contexts.keys())

