"""Retail-specific business context."""

from typing import Dict, Any, List
from business_analyst.context.base import BusinessContext


class RetailContext(BusinessContext):
    """
    Business context for retail industry.
    
    Contains retail-specific thresholds, norms, and expectations.
    """
    
    def __init__(self):
        """Initialize retail context with industry-specific values."""
        # Thresholds for various metrics
        self._thresholds = {
            'low_stock_ratio': 0.2,  # 20% of average stock level (legacy, may be used by other checks)
            'high_stock_ratio': 2.0,  # 200% of average stock level
            'slow_moving_days': 30,   # Days without sales
            'fast_moving_threshold': 5,  # Sales per week
            'reorder_point_multiplier': 1.5,  # Safety stock multiplier
            # Days-of-stock thresholds for stock-out risk
            'critical_days_of_stock': 7,   # < 7 days → HIGH severity
            'medium_days_of_stock': 14,    # 7-14 days → MEDIUM severity
            'top_seller_revenue_percentile': 0.3,  # Top 30% by revenue considered top sellers
            'sales_lookback_days': 30,     # Use last 30 days of sales for velocity calculation
            'min_sales_days_required': 7,  # Minimum days of sales data needed for reliable estimate
        }
        
        # Business norms
        self._norms = {
            'typical_stock_turnover': 12,  # Times per year
            'typical_margin': 0.30,  # 30% margin
            'seasonal_variation_factor': 1.5,  # Peak season multiplier
            'weekend_sales_boost': 1.2,  # 20% boost on weekends
        }
        
        # Expected data schema
        self._required_columns = ['product_id', 'product_name', 'quantity', 'price']
        self._column_types = {
            'product_id': str,
            'product_name': str,
            'quantity': int,
            'price': float,
        }
    
    @property
    def industry(self) -> str:
        """Return the industry name."""
        return "retail"
    
    def get_threshold(self, metric_name: str) -> float:
        """Get threshold value for a metric."""
        if metric_name not in self._thresholds:
            raise KeyError(f"Threshold '{metric_name}' not found in retail context")
        return self._thresholds[metric_name]
    
    def get_norm(self, norm_name: str) -> Any:
        """Get business norm value."""
        if norm_name not in self._norms:
            raise KeyError(f"Norm '{norm_name}' not found in retail context")
        return self._norms[norm_name]
    
    def get_required_columns(self) -> List[str]:
        """Get list of required columns for retail."""
        return self._required_columns.copy()
    
    def get_column_types(self) -> Dict[str, type]:
        """Get expected column types for retail."""
        return self._column_types.copy()

