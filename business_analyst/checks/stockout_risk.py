"""Stock-out risk analyst check."""

from typing import List, Dict, Any, Tuple, Optional
import pandas as pd
from business_analyst.checks.base import AnalystCheck
from business_analyst.core.insight import Insight, Severity, InsightType
from business_analyst.core.exceptions import CheckExecutionError
from business_analyst.context.base import BusinessContext
from business_analyst.data.extractor import FeatureExtractor


class StockOutRiskCheck(AnalystCheck):
    """
    Identifies products at risk of stock-out.
    
    Uses days-of-stock calculation based on sales velocity to determine
    when products may run out. Severity is contextual - top sellers
    receive higher priority even with similar stock levels.
    """
    
    @property
    def name(self) -> str:
        """Return the name of this check."""
        return "stockout_risk"
    
    @property
    def description(self) -> str:
        """Return a description of what this check does."""
        return "Identifies products at risk of running out of stock based on days of cover"
    
    def _estimate_daily_sales(
        self,
        quantity: float,
        context: BusinessContext
    ) -> float:
        """
        Estimate average daily sales for a product.
        
        If sales velocity data is not available, estimates based on
        typical stock turnover norms for the industry.
        
        Assumption: Uses typical_stock_turnover (times per year) to estimate
        daily sales rate. This is a reasonable default for small retail shops
        where detailed sales history may not be available.
        
        Args:
            quantity: Current stock quantity
            context: Business context with industry norms
            
        Returns:
            Estimated average daily sales
        """
        try:
            # Try to get typical stock turnover from context
            annual_turnover = context.get_norm('typical_stock_turnover')
            # Estimate: if stock turns over X times per year, daily sales ≈ quantity / (365 / X)
            daily_sales = quantity / (365 / annual_turnover)
            return max(daily_sales, 0.01)  # Minimum to avoid division by zero
        except KeyError:
            # Fallback: assume 12x annual turnover (once per month)
            daily_sales = quantity / (365 / 12)
            return max(daily_sales, 0.01)
    
    def _calculate_days_of_stock(
        self,
        df: pd.DataFrame,
        context: BusinessContext
    ) -> pd.DataFrame:
        """
        Calculate days-of-stock (days of cover) for each product.
        
        days_of_stock = current_quantity / average_daily_sales
        
        Uses actual sales data when available (from sales summary CSV),
        otherwise estimates from industry norms.
        
        Args:
            df: DataFrame with product data (may include daily_sales from sales data)
            context: Business context
            
        Returns:
            DataFrame with added 'days_of_stock', 'sales_velocity_source', and 'confidence' columns
        """
        df = df.copy()
        
        # Check if we have actual sales velocity data (from sales summary)
        if 'daily_sales' in df.columns:
            # Use actual sales data
            df['days_of_stock'] = df['quantity'] / df['daily_sales'].fillna(0.01).clip(lower=0.01)
            df['sales_velocity_source'] = df['daily_sales'].notna().map({
                True: 'actual_sales',
                False: 'estimated'
            })
            # Products with actual sales data have higher confidence
            df['confidence'] = df['daily_sales'].notna().map({
                True: 'high',
                False: 'low'
            })
            # For products without sales data, estimate
            missing_mask = df['daily_sales'].isna()
            if missing_mask.any():
                df.loc[missing_mask, 'estimated_daily_sales'] = df.loc[missing_mask, 'quantity'].apply(
                    lambda q: self._estimate_daily_sales(q, context)
                )
                df.loc[missing_mask, 'days_of_stock'] = (
                    df.loc[missing_mask, 'quantity'] / 
                    df.loc[missing_mask, 'estimated_daily_sales']
                )
        elif 'sales_per_day' in df.columns:
            # Legacy column name support
            df['days_of_stock'] = df['quantity'] / df['sales_per_day'].clip(lower=0.01)
            df['sales_velocity_source'] = 'provided'
            df['confidence'] = 'high'
        elif 'weekly_sales' in df.columns or 'sales_per_week' in df.columns:
            # Weekly sales data
            sales_col = 'weekly_sales' if 'weekly_sales' in df.columns else 'sales_per_week'
            df['days_of_stock'] = (df['quantity'] / df[sales_col].clip(lower=0.01)) * 7
            df['sales_velocity_source'] = 'provided'
            df['confidence'] = 'high'
        else:
            # No sales data available - estimate from industry norms
            df['estimated_daily_sales'] = df['quantity'].apply(
                lambda q: self._estimate_daily_sales(q, context)
            )
            df['days_of_stock'] = df['quantity'] / df['estimated_daily_sales']
            df['sales_velocity_source'] = 'estimated'
            df['confidence'] = 'low'
        
        return df
    
    def _identify_top_sellers(
        self,
        df: pd.DataFrame,
        context: BusinessContext
    ) -> pd.Series:
        """
        Identify top-selling products by revenue.
        
        Uses revenue (quantity * price) to determine top sellers.
        Top sellers are those in the top percentile defined by context.
        
        Args:
            df: DataFrame with product data
            context: Business context
            
        Returns:
            Boolean Series indicating top sellers
        """
        if 'price' not in df.columns or 'quantity' not in df.columns:
            # If we can't calculate revenue, assume no top sellers
            return pd.Series([False] * len(df), index=df.index)
        
        # Calculate revenue (using current stock as proxy for typical stock)
        # In a real system, this would use historical sales revenue
        df['revenue_proxy'] = df['quantity'] * df['price']
        
        # Get top seller percentile threshold
        try:
            percentile = context.get_threshold('top_seller_revenue_percentile')
        except KeyError:
            percentile = 0.3  # Default: top 30%
        
        # Identify top sellers
        threshold = df['revenue_proxy'].quantile(1 - percentile)
        return df['revenue_proxy'] >= threshold
    
    def _determine_severity(
        self,
        days_of_stock: float,
        is_top_seller: bool,
        context: BusinessContext
    ) -> Severity:
        """
        Determine severity based on days-of-stock and product importance.
        
        Severity rules:
        - < 7 days → HIGH (or CRITICAL if top seller)
        - 7-14 days → MEDIUM (or HIGH if top seller)
        - > 14 days → LOW (or MEDIUM if top seller)
        
        Top sellers get elevated severity because stock-outs have
        greater business impact.
        
        Args:
            days_of_stock: Calculated days of stock remaining
            is_top_seller: Whether product is a top seller
            context: Business context
            
        Returns:
            Severity level
        """
        critical_threshold = context.get_threshold('critical_days_of_stock')
        medium_threshold = context.get_threshold('medium_days_of_stock')
        
        if days_of_stock < critical_threshold:
            # Less than 7 days
            return Severity.CRITICAL if is_top_seller else Severity.HIGH
        elif days_of_stock < medium_threshold:
            # 7-14 days
            return Severity.HIGH if is_top_seller else Severity.MEDIUM
        else:
            # More than 14 days - still worth noting if top seller
            return Severity.MEDIUM if is_top_seller else Severity.LOW
    
    def _create_insufficient_data_insight(
        self,
        has_sales_data: bool,
        products_with_sales: int,
        total_products: int,
        context: BusinessContext
    ) -> Optional[Insight]:
        """
        Create an insight when sales data is missing or insufficient.
        
        This ensures we don't silently report "no issues" when we lack
        the data needed to make accurate assessments.
        
        Args:
            has_sales_data: Whether any sales data was provided
            products_with_sales: Number of products with sales data
            total_products: Total number of products
            context: Business context
            
        Returns:
            Insight about insufficient data, or None if data is sufficient
        """
        if has_sales_data and products_with_sales >= (total_products * 0.5):
            # Have sufficient data
            return None
        
        if not has_sales_data:
            description = (
                "Sales data was not provided in your file. Stock-out risk assessments are "
                "based on estimated sales patterns rather than your actual sales history. "
                "This reduces the accuracy of timing predictions. "
                "To improve accuracy, include sales rows (with date and units_sold) in your CSV file."
            )
            recommendation = (
                "Add sales rows to your CSV file with date, product_id, and units_sold columns. "
                "This allows the system to calculate actual sales rates for more precise "
                "stock-out predictions. Sales should represent activity after your inventory snapshot date."
            )
        else:
            coverage_pct = (products_with_sales / total_products) * 100
            description = (
                f"Sales data is available for only {products_with_sales} of {total_products} products "
                f"({coverage_pct:.0f}% coverage). Stock-out assessments for products without sales data "
                f"rely on industry estimates and may be less accurate."
            )
            recommendation = (
                "Consider adding sales rows for all products in your CSV file. "
                "More complete sales data improves the accuracy of stock-out predictions."
            )
        
        return Insight(
            check_name=self.name,
            title="Data Coverage: Sales History Missing",
            description=description,
            severity=Severity.INFO,
            insight_type=InsightType.ANOMALY,  # Using ANOMALY for data quality issues
            metrics={
                'has_sales_data': has_sales_data,
                'products_with_sales_data': products_with_sales,
                'total_products': total_products,
                'coverage_percentage': (products_with_sales / total_products * 100) if total_products > 0 else 0,
            },
            recommendation=recommendation,
            metadata={
                'data_quality_issue': True,
                'data_coverage': 'incomplete',
            }
        )
    
    def _format_days_description(self, days: float, severity: Severity = None) -> str:
        """
        Format days-of-stock into human-readable description.
        
        Aligns timeframes with severity levels for consistency.
        
        Args:
            days: Days of stock remaining
            severity: Optional severity level to ensure alignment
            
        Returns:
            Formatted string matching severity timeframe
        """
        # Align with severity thresholds
        if severity == Severity.CRITICAL or days < 7:
            # Immediate attention - this week
            return "this week"
        elif severity == Severity.HIGH or days < 14:
            # Action needed soon - next 1-2 weeks
            return "in the next 1–2 weeks"
        else:
            # Monitor - beyond 2 weeks (not used in product descriptions, but kept for consistency)
            return "in the next few weeks"
    
    def execute(
        self,
        features: Dict[str, Any],
        context: BusinessContext
    ) -> List[Insight]:
        """
        Execute stock-out risk analysis using days-of-stock calculation.
        
        Args:
            features: Extracted features
            context: Business context
            
        Returns:
            List of insights about stock-out risks
        """
        try:
            # Retrieve DataFrame from features
            extractor = FeatureExtractor()
            df = extractor.get_dataframe(features)
            
            if df is None:
                return []
            
            # Check if required columns exist
            # Support both 'quantity' (legacy) and 'starting_quantity' (unified format)
            if 'starting_quantity' in df.columns:
                # Unified format: use starting_quantity
                df['quantity'] = df['starting_quantity']
            elif 'quantity' not in df.columns:
                return []
            
            required_cols = ['product_id', 'quantity']
            if not all(col in df.columns for col in required_cols):
                return []
            
            insights = []
            
            # Check if we have sales data
            has_sales_data = features.get('has_sales_data', False)
            products_with_sales = features.get('products_with_sales_data', 0)
            total_products = len(df)
            
            # Generate insufficient data insight if sales data is missing or very limited
            min_sales_days = context.get_threshold('min_sales_days_required')
            if not has_sales_data or products_with_sales < (total_products * 0.5):
                # Less than 50% of products have sales data
                insufficient_data_insight = self._create_insufficient_data_insight(
                    has_sales_data,
                    products_with_sales,
                    total_products,
                    context
                )
                if insufficient_data_insight:
                    insights.append(insufficient_data_insight)
            
            # Calculate days-of-stock for all products
            df = self._calculate_days_of_stock(df, context)
            
            # Identify top sellers
            df['is_top_seller'] = self._identify_top_sellers(df, context)
            
            # Get severity thresholds
            critical_threshold = context.get_threshold('critical_days_of_stock')
            medium_threshold = context.get_threshold('medium_days_of_stock')
            
            # Find products at risk (less than medium threshold days)
            at_risk = df[df['days_of_stock'] < medium_threshold].copy()
            
            if len(at_risk) == 0:
                return insights
            
            # Determine severity for each product
            at_risk['severity'] = at_risk.apply(
                lambda row: self._determine_severity(
                    row['days_of_stock'],
                    row['is_top_seller'],
                    context
                ),
                axis=1
            )
            
            # Group by severity for reporting
            critical_products = at_risk[at_risk['severity'] == Severity.CRITICAL]
            high_products = at_risk[at_risk['severity'] == Severity.HIGH]
            medium_products = at_risk[at_risk['severity'] == Severity.MEDIUM]
            low_products = at_risk[at_risk['severity'] == Severity.LOW]
            
            # Determine overall severity (highest among at-risk products)
            if len(critical_products) > 0:
                overall_severity = Severity.CRITICAL
            elif len(high_products) > 0:
                overall_severity = Severity.HIGH
            elif len(medium_products) > 0:
                overall_severity = Severity.MEDIUM
            else:
                overall_severity = Severity.LOW
            
            # Count top sellers at risk
            top_sellers_at_risk = at_risk[at_risk['is_top_seller']].shape[0]
            
            # Get product names if available
            product_name_col = 'product_name' if 'product_name' in at_risk.columns else 'product_id'
            
            # Build structured description by urgency level
            description_parts = []
            
            # Immediate attention (CRITICAL) - this week
            if len(critical_products) > 0:
                description_parts.append("**Immediate attention:**")
                critical_sorted = critical_products.sort_values('days_of_stock')
                product_list = []
                for _, product in critical_sorted.iterrows():
                    product_name = product[product_name_col]
                    days = product['days_of_stock']
                    time_estimate = self._format_days_description(days, Severity.CRITICAL)
                    product_list.append(f"{product_name} (may run out {time_estimate} at the current rate of sales)")
                
                description_parts.append(", ".join(product_list))
                description_parts.append("")
                description_parts.append(
                    "These products may run out this week at the current rate of sales. "
                    "This could result in missed sales and customer dissatisfaction."
                )
                description_parts.append("")
            
            # Action needed soon (HIGH) - next 1-2 weeks
            if len(high_products) > 0:
                description_parts.append("**Action needed soon:**")
                high_sorted = high_products.sort_values('days_of_stock')
                product_list = []
                for _, product in high_sorted.iterrows():
                    product_name = product[product_name_col]
                    days = product['days_of_stock']
                    time_estimate = self._format_days_description(days, Severity.HIGH)
                    product_list.append(f"{product_name} (may run out {time_estimate} at the current rate of sales)")
                
                description_parts.append(", ".join(product_list))
                description_parts.append("")
                description_parts.append(
                    "These products should be reordered soon to avoid future shortages."
                )
                description_parts.append("")
            
            # Monitor (MEDIUM) - beyond 2 weeks
            if len(medium_products) > 0:
                description_parts.append("**Monitor:**")
                medium_sorted = medium_products.sort_values('days_of_stock')
                product_list = []
                for _, product in medium_sorted.iterrows():
                    product_name = product[product_name_col]
                    product_list.append(product_name)
                
                description_parts.append(", ".join(product_list))
                description_parts.append("")
                description_parts.append(
                    "Stock levels should be monitored for these products."
                )
                description_parts.append("")
            
            description = "\n".join(description_parts).strip()
            
            # Build action-oriented recommendation by urgency
            recommendation_parts = []
            
            if len(critical_products) > 0:
                recommendation_parts.append(
                    "Prioritize reordering items that may run out this week at the current rate of sales. "
                )
            
            if len(high_products) > 0:
                recommendation_parts.append(
                    "Plan reorders soon for products that may run out in the next 1–2 weeks at the current rate of sales. "
                )
            
            if len(medium_products) > 0 and len(critical_products) == 0 and len(high_products) == 0:
                recommendation_parts.append(
                    "Monitor stock levels and plan reorders before products reach critical levels. "
                )
            
            if top_sellers_at_risk > 0:
                recommendation_parts.append(
                    "Pay special attention to top-selling products to avoid revenue loss."
                )
            
            recommendation = "".join(recommendation_parts).strip()
            
            # Determine confidence statement based on data quality
            has_actual_sales = (at_risk['sales_velocity_source'] == 'actual_sales').any()
            has_estimated_sales = (at_risk['sales_velocity_source'] == 'estimated').any()
            
            if has_actual_sales and not has_estimated_sales:
                # All products have actual sales data
                confidence_note = (
                    "This assessment is based on recent sales at the current rate of sales and may change if demand shifts."
                )
            elif has_actual_sales and has_estimated_sales:
                # Mixed: some products have sales data, some don't
                estimated_count = (at_risk['sales_velocity_source'] == 'estimated').sum()
                confidence_note = (
                    f"This assessment uses actual sales data where available. "
                    f"For {estimated_count} product{'s' if estimated_count > 1 else ''} without sales history, "
                    f"estimates are based on typical industry patterns at the current rate of sales and may be less accurate."
                )
            else:
                # All products use estimates
                confidence_note = (
                    "This assessment is based on estimated sales patterns at the current rate of sales. "
                    "Providing actual sales data will significantly improve accuracy. "
                    "Stock-out timing may vary if demand changes."
                )
            
            # Create insight title based on most urgent items
            if len(critical_products) > 0:
                if len(critical_products) == 1:
                    title = "Stock-Out Risk: 1 product needs immediate attention"
                else:
                    title = f"Stock-Out Risk: {len(critical_products)} products need immediate attention"
            elif len(high_products) > 0:
                if len(high_products) == 1:
                    title = "Stock-Out Risk: 1 product needs action soon"
                else:
                    title = f"Stock-Out Risk: {len(high_products)} products need action soon"
            elif len(medium_products) > 0:
                if len(medium_products) == 1:
                    title = "Stock-Out Risk: 1 product to monitor"
                else:
                    title = f"Stock-Out Risk: {len(medium_products)} products to monitor"
            else:
                if len(at_risk) == 1:
                    title = "Stock-Out Risk: 1 product needs attention"
                else:
                    title = f"Stock-Out Risk: {len(at_risk)} products need attention"
            
            # Add confidence note to description
            full_description = f"{description}\n\n{confidence_note}"
            
            insight = Insight(
                check_name=self.name,
                title=title,
                description=full_description,
                severity=overall_severity,
                insight_type=InsightType.RISK,
                metrics={
                    'at_risk_count': len(at_risk),
                    'critical_count': len(critical_products),
                    'high_count': len(high_products),
                    'medium_count': len(medium_products),
                    'top_sellers_at_risk': top_sellers_at_risk,
                    'min_days_of_stock': float(at_risk['days_of_stock'].min()),
                    'avg_days_of_stock': float(at_risk['days_of_stock'].mean()),
                    'total_products': len(df),
                },
                recommendation=recommendation,
                metadata={
                    'at_risk_product_ids': at_risk['product_id'].head(20).tolist(),
                    'sales_velocity_estimated': has_estimated_sales,
                    'critical_product_ids': critical_products['product_id'].tolist() if len(critical_products) > 0 else [],
                }
            )
            insights.append(insight)
            
            return insights
            
        except Exception as e:
            raise CheckExecutionError(
                f"Stock-out risk check failed: {str(e)}"
            )

