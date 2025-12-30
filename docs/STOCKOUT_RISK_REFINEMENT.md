# Stock-Out Risk Check Refinement

## Overview

The stock-out risk analyst check has been refined to better reflect how a human analyst would reason and communicate risk to a local shop owner. The changes focus on practical business judgment rather than abstract statistics.

## Files Changed

### 1. `business_analyst/context/retail.py`
**Changes:**
- Added `critical_days_of_stock` threshold (7 days)
- Added `medium_days_of_stock` threshold (14 days)
- Added `top_seller_revenue_percentile` threshold (0.3 = top 30%)

**Rationale:** Provides industry-specific thresholds for days-of-stock calculations and top seller identification.

### 2. `business_analyst/checks/stockout_risk.py`
**Major Refactoring:**
- Replaced absolute quantity thresholds with days-of-stock calculation
- Implemented contextual severity based on product importance (top sellers)
- Improved language to focus on consequences rather than statistics
- Added confidence/assumption qualifiers

**Key Methods Added:**
- `_estimate_daily_sales()`: Estimates sales velocity from industry norms when data unavailable
- `_calculate_days_of_stock()`: Calculates days of cover for each product
- `_identify_top_sellers()`: Identifies top 30% by revenue
- `_determine_severity()`: Contextual severity considering days-of-stock AND product importance
- `_format_days_description()`: Converts days to human-readable timeframes

### 3. `business_analyst/delivery/report.py`
**Changes:**
- Improved executive summary to focus on "what needs attention"
- Extracts specific actionable items from insights
- Avoids technical severity counts as primary message

## Days-of-Stock Calculation

### Formula
```
days_of_stock = current_quantity / average_daily_sales
```

### Sales Velocity Estimation
When sales velocity data is not available, the system estimates daily sales using:
- Industry norm: `typical_stock_turnover` (default: 12 times per year)
- Calculation: `daily_sales = quantity / (365 / annual_turnover)`
- Minimum: 0.01 units/day to avoid division by zero

### Assumptions Documented
1. **Sales Velocity Estimation**: Uses typical stock turnover norms when actual sales data unavailable
2. **Top Seller Definition**: Top 30% by revenue (quantity × price)
3. **Severity Thresholds**: 
   - < 7 days → HIGH/CRITICAL
   - 7-14 days → MEDIUM/HIGH
   - > 14 days → LOW/MEDIUM

## Severity Logic

Severity is now **contextual**, not purely numeric:

| Days of Stock | Regular Product | Top Seller |
|---------------|----------------|------------|
| < 7 days      | HIGH           | CRITICAL   |
| 7-14 days     | MEDIUM         | HIGH       |
| > 14 days     | LOW            | MEDIUM     |

**Rationale:** Top sellers have greater business impact when out of stock, so they receive elevated severity even with similar stock levels.

## Language Improvements

### Before (Old Output)
```
"3 products are below the low stock threshold (27 units). 
This represents 1.5% of total inventory value."
```

### After (New Output)
```
"3 products may run out within the next 1-2 weeks, including 1 top seller. 
This could result in missed sales and customer dissatisfaction.

Products needing immediate attention: Widget A, Widget B, Widget C

Note: Sales velocity estimates are based on typical industry patterns. 
Actual stock-out timing may vary if demand changes."
```

### Key Changes
- ✅ Focuses on **consequences** ("missed sales", "customer dissatisfaction")
- ✅ Uses **timeframes** ("within the next 1-2 weeks") instead of raw quantities
- ✅ **Highlights top sellers** explicitly
- ✅ Includes **confidence qualifiers** about estimates
- ✅ Avoids **minimizing percentages** that reduce perceived urgency

## Executive Summary Improvements

### Before
```
## Executive Summary
Total Insights: 3
- Critical: 1
- High: 2
```

### After
```
## Executive Summary

What needs attention this week:
- 2 products at risk of running out this week
- 1 high-priority item to address soon

Total insights: 3
```

### Key Changes
- ✅ Leads with **actionable items** ("What needs attention")
- ✅ Uses **plain language** ("products at risk of running out")
- ✅ Avoids **technical severity labels** as primary message
- ✅ Provides **specific counts** from insights when available

## Example Output

### Insight Title
```
Stock-Out Risk: 3 products at risk, 1 product running low
```

### Insight Description
```
3 products may run out within the next 1-2 weeks, including 1 top seller. 
This could result in missed sales and customer dissatisfaction. 
Another 1 product is running low and should be monitored.

Products needing immediate attention: Widget A, Widget B

Note: Sales velocity estimates are based on typical industry patterns. 
Actual stock-out timing may vary if demand changes.
```

### Recommendation
```
Prioritize reordering for top sellers to avoid revenue loss. 
Review sales patterns and consider placing orders for products 
with less than 2 weeks of stock remaining.
```

### Metrics (for traceability)
```python
{
    'at_risk_count': 4,
    'critical_count': 1,
    'high_count': 2,
    'medium_count': 1,
    'top_sellers_at_risk': 1,
    'min_days_of_stock': 4.2,
    'avg_days_of_stock': 9.8,
    'total_products': 25
}
```

## Testing Considerations

The refined check maintains:
- ✅ **Determinism**: Same inputs produce same outputs
- ✅ **Testability**: All logic is explicit and traceable
- ✅ **Explainability**: Every severity decision can be traced to specific rules
- ✅ **Architecture compliance**: No changes to core architecture

## Backward Compatibility

- Legacy `low_stock_ratio` threshold remains in context (may be used by other checks)
- New thresholds are additive, not replacements
- Existing insights structure unchanged (only content improved)

