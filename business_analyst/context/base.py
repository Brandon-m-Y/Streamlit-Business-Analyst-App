"""Base business context interface."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List


class BusinessContext(ABC):
    """
    Abstract base class for industry-specific business contexts.
    
    Encapsulates industry norms, thresholds, and business rules
    that analyst checks use to make judgments.
    """
    
    @property
    @abstractmethod
    def industry(self) -> str:
        """Return the industry name."""
        pass
    
    @abstractmethod
    def get_threshold(self, metric_name: str) -> float:
        """
        Get threshold value for a metric.
        
        Args:
            metric_name: Name of the metric
            
        Returns:
            Threshold value
            
        Raises:
            KeyError: If metric not found
        """
        pass
    
    @abstractmethod
    def get_norm(self, norm_name: str) -> Any:
        """
        Get business norm value.
        
        Args:
            norm_name: Name of the norm
            
        Returns:
            Norm value
            
        Raises:
            KeyError: If norm not found
        """
        pass
    
    @abstractmethod
    def get_required_columns(self) -> List[str]:
        """Get list of required columns for this industry."""
        pass
    
    @abstractmethod
    def get_column_types(self) -> Dict[str, type]:
        """Get expected column types for this industry."""
        pass
    
    def has_threshold(self, metric_name: str) -> bool:
        """Check if a threshold exists for a metric."""
        try:
            self.get_threshold(metric_name)
            return True
        except KeyError:
            return False
    
    def has_norm(self, norm_name: str) -> bool:
        """Check if a norm exists."""
        try:
            self.get_norm(norm_name)
            return True
        except KeyError:
            return False

