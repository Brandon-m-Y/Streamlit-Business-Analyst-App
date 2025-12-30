"""Data validation."""

from typing import List, Dict, Any, Optional
import pandas as pd

from business_analyst.core.exceptions import DataValidationError


class DataValidator:
    """Validates incoming data against expected schema and constraints."""
    
    def __init__(self, required_columns: List[str], column_types: Optional[Dict[str, type]] = None):
        """
        Initialize validator.
        
        Args:
            required_columns: List of required column names
            column_types: Optional mapping of column names to expected types
        """
        self.required_columns = required_columns
        self.column_types = column_types or {}
    
    def validate(self, df: pd.DataFrame) -> None:
        """
        Validate DataFrame structure and content.
        
        Supports both unified CSV format and legacy separate format.
        
        Args:
            df: DataFrame to validate
            
        Raises:
            DataValidationError: If validation fails
        """
        if df.empty:
            raise DataValidationError("DataFrame is empty")
        
        # Check if this is unified format
        is_unified = (
            'as_of_date' in df.columns and
            'starting_quantity' in df.columns and
            'date' in df.columns and
            'units_sold' in df.columns
        )
        
        if is_unified:
            # Validate unified format
            self._validate_unified_format(df)
        else:
            # Validate legacy format
            self._validate_legacy_format(df)
    
    def _validate_unified_format(self, df: pd.DataFrame) -> None:
        """Validate unified CSV format."""
        # Required columns for unified format
        required_unified = ['as_of_date', 'product_id', 'starting_quantity']
        missing = set(required_unified) - set(df.columns)
        if missing:
            raise DataValidationError(
                f"Unified format missing required columns: {', '.join(missing)}"
            )
        
        # Check that we have inventory rows (starting_quantity not null)
        inventory_rows = df['starting_quantity'].notna()
        if not inventory_rows.any():
            raise DataValidationError(
                "Unified format must have at least one row with starting_quantity (inventory snapshot)"
            )
        
        # Check that product_id is consistent for inventory rows
        inventory_df = df[inventory_rows]
        if inventory_df['product_id'].isnull().any():
            raise DataValidationError(
                "All inventory rows must have a product_id"
            )
        
        # Check for sales rows (date and units_sold)
        sales_rows = df['date'].notna() & df['units_sold'].notna()
        if sales_rows.any():
            sales_df = df[sales_rows]
            if sales_df['product_id'].isnull().any():
                raise DataValidationError(
                    "All sales rows must have a product_id"
                )
    
    def _validate_legacy_format(self, df: pd.DataFrame) -> None:
        """Validate legacy separate format."""
        # Check required columns
        missing_columns = set(self.required_columns) - set(df.columns)
        if missing_columns:
            raise DataValidationError(
                f"Missing required columns: {', '.join(missing_columns)}"
            )
        
        # Check column types
        for column, expected_type in self.column_types.items():
            if column not in df.columns:
                continue
            
            if not df[column].dtype == expected_type:
                # Try to convert
                try:
                    df[column] = df[column].astype(expected_type)
                except (ValueError, TypeError):
                    raise DataValidationError(
                        f"Column '{column}' has incorrect type. "
                        f"Expected {expected_type}, got {df[column].dtype}"
                    )
        
        # Check for null values in required columns
        null_columns = df[self.required_columns].isnull().any()
        if null_columns.any():
            columns_with_nulls = null_columns[null_columns].index.tolist()
            raise DataValidationError(
                f"Required columns contain null values: {', '.join(columns_with_nulls)}"
            )

