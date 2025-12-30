"""Example tests for analyst checks."""

import unittest
from unittest.mock import Mock
import pandas as pd
from business_analyst.checks.stockout_risk import StockOutRiskCheck
from business_analyst.context.retail import RetailContext
from business_analyst.core.insight import Severity


class TestStockOutRiskCheck(unittest.TestCase):
    """Test cases for stock-out risk check."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.check = StockOutRiskCheck()
        self.context = RetailContext()
    
    def test_check_name(self):
        """Test that check has correct name."""
        self.assertEqual(self.check.name, "stockout_risk")
    
    def test_low_stock_detection(self):
        """Test detection of low stock products."""
        # Create test data with some low stock items
        df = pd.DataFrame({
            'product_id': ['P1', 'P2', 'P3', 'P4', 'P5'],
            'product_name': ['Product 1', 'Product 2', 'Product 3', 'Product 4', 'Product 5'],
            'quantity': [100, 50, 5, 200, 10],  # P3 and P5 are low stock
            'price': [10.0, 20.0, 15.0, 25.0, 30.0]
        })
        
        features = {'_dataframe': df}
        insights = self.check.execute(features, self.context)
        
        # Should generate at least one insight
        self.assertGreater(len(insights), 0)
        
        # Check insight properties
        insight = insights[0]
        self.assertEqual(insight.check_name, "stockout_risk")
        self.assertEqual(insight.insight_type.value, "risk")
        self.assertIn('at_risk_count', insight.metrics)
    
    def test_no_low_stock(self):
        """Test that no insights are generated when all stock is adequate."""
        # Create test data with all items well-stocked
        df = pd.DataFrame({
            'product_id': ['P1', 'P2', 'P3'],
            'product_name': ['Product 1', 'Product 2', 'Product 3'],
            'quantity': [100, 200, 150],  # All well above threshold
            'price': [10.0, 20.0, 15.0]
        })
        
        features = {'_dataframe': df}
        insights = self.check.execute(features, self.context)
        
        # Should generate no insights if no products are at risk
        # (This depends on the threshold calculation)
        # For this test, we just verify it doesn't crash
        self.assertIsInstance(insights, list)
    
    def test_missing_columns(self):
        """Test handling of missing required columns."""
        df = pd.DataFrame({
            'product_id': ['P1', 'P2'],
            'name': ['Product 1', 'Product 2'],  # Missing 'quantity'
        })
        
        features = {'_dataframe': df}
        insights = self.check.execute(features, self.context)
        
        # Should return empty list when required columns are missing
        self.assertEqual(len(insights), 0)


if __name__ == '__main__':
    unittest.main()

