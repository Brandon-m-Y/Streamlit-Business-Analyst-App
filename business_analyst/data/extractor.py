"""Feature extraction from raw data."""

from typing import Dict, Any, Optional
import pandas as pd
from datetime import datetime, timedelta

from business_analyst.core.exceptions import FeatureExtractionError


class FeatureExtractor:
    """
    Extracts business-relevant features from raw data.
    
    This allows raw data to be deleted after feature extraction,
    as only the extracted features are needed for analysis.
    """
    
    def extract(
        self,
        df: pd.DataFrame,
        sales_df: Optional[pd.DataFrame] = None
    ) -> Dict[str, Any]:
        """
        Extract features from unified CSV or separate inventory/sales DataFrames.
        
        Supports two modes:
        1. Unified CSV: Single DataFrame with inventory snapshot + sales rows
        2. Separate DataFrames: Inventory df + optional sales_df (legacy support)
        
        Args:
            df: Raw DataFrame (unified format or inventory-only)
            sales_df: Optional separate sales DataFrame (legacy mode)
            
        Returns:
            Dictionary of extracted features
            
        Raises:
            FeatureExtractionError: If extraction fails
        """
        try:
            features = {}
            
            # Check if this is a unified CSV format
            is_unified = (
                'as_of_date' in df.columns and
                'starting_quantity' in df.columns and
                'date' in df.columns and
                'units_sold' in df.columns
            )
            
            if is_unified:
                # Parse unified CSV format
                inventory_df, sales_df_from_unified = self._parse_unified_csv(df)
                features['data_format'] = 'unified'
                features['as_of_date'] = inventory_df['as_of_date'].iloc[0] if 'as_of_date' in inventory_df.columns else None
            else:
                # Legacy format: separate inventory and sales
                inventory_df = df.copy()
                sales_df_from_unified = sales_df
                features['data_format'] = 'separate'
            
            # Basic statistics from inventory
            features['row_count'] = len(inventory_df)
            features['column_count'] = len(inventory_df.columns)
            features['columns'] = inventory_df.columns.tolist()
            
            # Numeric column statistics
            numeric_cols = inventory_df.select_dtypes(include=['number']).columns
            for col in numeric_cols:
                if col not in ['as_of_date']:  # Skip date columns
                    features[f'{col}_sum'] = float(inventory_df[col].sum())
                    features[f'{col}_mean'] = float(inventory_df[col].mean())
                    features[f'{col}_min'] = float(inventory_df[col].min())
                    features[f'{col}_max'] = float(inventory_df[col].max())
                    features[f'{col}_std'] = float(inventory_df[col].std()) if len(inventory_df) > 1 else 0.0
            
            # Categorical column statistics
            categorical_cols = inventory_df.select_dtypes(include=['object', 'category']).columns
            for col in categorical_cols:
                if col not in ['as_of_date', 'date']:  # Skip date columns
                    features[f'{col}_unique_count'] = int(inventory_df[col].nunique())
                    features[f'{col}_value_counts'] = inventory_df[col].value_counts().to_dict()
            
            # Process sales data
            if sales_df_from_unified is not None and not sales_df_from_unified.empty:
                try:
                    # Get as_of_date for temporal alignment
                    as_of_date = features.get('as_of_date')
                    if as_of_date:
                        as_of_date = pd.to_datetime(as_of_date)
                    
                    # Calculate daily sales velocity per product
                    sales_velocity = self._calculate_sales_velocity(
                        sales_df_from_unified,
                        as_of_date=as_of_date
                    )
                    
                    # Merge sales velocity into inventory DataFrame
                    if 'product_id' in inventory_df.columns and 'product_id' in sales_velocity.columns:
                        inventory_df = inventory_df.merge(sales_velocity, on='product_id', how='left')
                        features['has_sales_data'] = True
                        features['products_with_sales_data'] = int(inventory_df['daily_sales'].notna().sum())
                    else:
                        features['has_sales_data'] = False
                except Exception as e:
                    # Sales processing failure is not fatal
                    features['has_sales_data'] = False
                    features['sales_processing_error'] = str(e)
            else:
                features['has_sales_data'] = False
            
            # Store the full DataFrame for checks that need it
            features['_dataframe'] = inventory_df
            
            return features
            
        except Exception as e:
            raise FeatureExtractionError(f"Feature extraction failed: {str(e)}")
    
    def _parse_unified_csv(self, df: pd.DataFrame) -> tuple:
        """
        Parse unified CSV format into separate inventory and sales DataFrames.
        
        Unified CSV contains:
        - Inventory fields: as_of_date, product_id, product_name, price, starting_quantity
        - Sales fields: date, units_sold (can repeat per product)
        
        Args:
            df: Unified DataFrame
            
        Returns:
            Tuple of (inventory_df, sales_df)
        """
        df = df.copy()
        
        # Ensure date columns are datetime
        if 'as_of_date' in df.columns:
            df['as_of_date'] = pd.to_datetime(df['as_of_date'])
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
        
        # Identify inventory rows (those with starting_quantity, not null)
        inventory_mask = df['starting_quantity'].notna()
        inventory_df = df[inventory_mask].copy()
        
        # Identify sales rows (those with date and units_sold, not null)
        sales_mask = df['date'].notna() & df['units_sold'].notna()
        sales_df = df[sales_mask].copy()
        
        # Extract inventory snapshot (one row per product)
        # Group by product_id and take first row (inventory fields should be consistent)
        if len(inventory_df) > 0:
            inventory_df = inventory_df.groupby('product_id').first().reset_index()
            # Ensure we have required inventory columns
            required_inv_cols = ['product_id', 'starting_quantity']
            if 'as_of_date' in inventory_df.columns:
                required_inv_cols.append('as_of_date')
            if 'product_name' in inventory_df.columns:
                required_inv_cols.append('product_name')
            if 'price' in inventory_df.columns:
                required_inv_cols.append('price')
            
            # Rename starting_quantity to quantity for compatibility
            if 'starting_quantity' in inventory_df.columns:
                inventory_df['quantity'] = inventory_df['starting_quantity']
        
        # Extract sales data (keep date, product_id, units_sold)
        if len(sales_df) > 0:
            sales_df = sales_df[['date', 'product_id', 'units_sold']].copy()
        
        return inventory_df, sales_df
    
    def _calculate_sales_velocity(
        self,
        sales_df: pd.DataFrame,
        lookback_days: int = 30,
        as_of_date: Optional[pd.Timestamp] = None
    ) -> pd.DataFrame:
        """
        Calculate average daily sales per product from sales summary data.
        
        Uses temporal alignment: only counts sales after as_of_date (inventory snapshot date).
        This ensures we calculate velocity based on sales that occurred after the inventory
        snapshot, not before.
        
        Args:
            sales_df: DataFrame with date, product_id, units_sold
            lookback_days: Number of days to look back for sales calculation
            as_of_date: Inventory snapshot date (sales before this are ignored)
            
        Returns:
            DataFrame with product_id and daily_sales columns
        """
        # Ensure date column is datetime
        if 'date' not in sales_df.columns or len(sales_df) == 0:
            return pd.DataFrame(columns=['product_id', 'daily_sales'])
        
        sales_df = sales_df.copy()
        sales_df['date'] = pd.to_datetime(sales_df['date'])
        
        # Filter to sales after as_of_date (temporal alignment)
        if as_of_date is not None:
            as_of_date = pd.to_datetime(as_of_date)
            sales_df = sales_df[sales_df['date'] > as_of_date].copy()
        
        if len(sales_df) == 0:
            return pd.DataFrame(columns=['product_id', 'daily_sales'])
        
        # Filter to recent sales (last N days from as_of_date or now)
        reference_date = as_of_date if as_of_date is not None else datetime.now()
        cutoff_date = reference_date - timedelta(days=lookback_days)
        recent_sales = sales_df[sales_df['date'] >= cutoff_date].copy()
        
        if len(recent_sales) > 0:
            # Aggregate daily sales by product
            daily_sales = recent_sales.groupby('product_id')['units_sold'].sum()
            
            # Calculate average daily sales (total sales / number of days with data)
            days_with_data = recent_sales.groupby('product_id')['date'].nunique()
            avg_daily_sales = daily_sales / days_with_data
            
            # Create result DataFrame
            result = pd.DataFrame({
                'product_id': avg_daily_sales.index,
                'daily_sales': avg_daily_sales.values
            })
            
            return result
        
        # Return empty DataFrame with correct structure if no valid data
        return pd.DataFrame(columns=['product_id', 'daily_sales'])
    
    def get_dataframe(self, features: Dict[str, Any]) -> pd.DataFrame:
        """
        Retrieve DataFrame from features if available.
        
        Args:
            features: Feature dictionary
            
        Returns:
            DataFrame if available, None otherwise
        """
        return features.get('_dataframe')

