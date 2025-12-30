# Sales Data Implementation Summary

## Overview

The system has been updated to support sales summary data for improved inventory velocity calculations and more accurate stock-out risk assessments.

## Files Modified

### 1. `business_analyst/core/engine.py`
**Changes:**
- Updated `analyze()` method to accept optional `sales_data_source` parameter
- Sales data ingestion is non-fatal (warnings logged if ingestion fails)
- Updated `analyze_and_report()` to pass sales data through

**Rationale:** Maintains backward compatibility while adding sales data support.

### 2. `business_analyst/data/extractor.py`
**Changes:**
- Updated `extract()` to accept optional `sales_df` parameter
- Added `_calculate_sales_velocity()` method to compute average daily sales from sales summary
- Uses 30-day lookback window by default
- Merges sales velocity into inventory DataFrame when available

**Key Logic:**
- Calculates: `daily_sales = total_units_sold / days_with_data`
- Only uses sales from last 30 days (configurable via context)
- Handles missing sales data gracefully

### 3. `business_analyst/checks/stockout_risk.py`
**Changes:**
- Updated `_calculate_days_of_stock()` to use actual sales data when available
- Added confidence tracking (`high` for actual sales, `low` for estimates)
- Added `_create_insufficient_data_insight()` to generate insights when sales data is missing
- Improved confidence language in descriptions
- Updated execute method to check for sales data availability

**Key Features:**
- Uses actual sales velocity when available
- Falls back to industry estimates when sales data missing
- Generates "Insufficient Data" insight when < 50% of products have sales data
- Clear confidence statements in all insights

### 4. `business_analyst/context/retail.py`
**Changes:**
- Added `sales_lookback_days` threshold (30 days)
- Added `min_sales_days_required` threshold (7 days minimum for reliable estimate)

**Rationale:** Configurable thresholds for sales data analysis.

### 5. `streamlit_app.py`
**Changes:**
- Added separate file uploader for sales summary (optional)
- Updated UI copy to explain both inventory snapshot and sales summary
- Added helpful tips about why sales data improves accuracy
- Updated data requirements documentation
- Handles both file uploads and passes to engine

**User Experience:**
- Clear separation between required (inventory) and optional (sales) data
- Explains benefits of providing sales data
- Shows when sales data is missing

### 6. `sample_sales_data.csv` (New File)
**Purpose:** Example sales summary CSV showing required format

**Format:**
```
date,product_id,units_sold
2024-12-01,P001,3
2024-12-01,P002,1
...
```

## Data Model

### Inventory Snapshot (Required)
- `product_id`: Links to sales data
- `product_name`: Product name
- `quantity`: Current stock level
- `price`: Product price

### Sales Summary (Optional)
- `date`: Sale date (YYYY-MM-DD)
- `product_id`: Must match inventory snapshot
- `units_sold`: Units sold that day

**Note:** Sales data is aggregated at daily level - no transaction IDs required.

## Days-of-Stock Calculation

### With Sales Data
```
days_of_stock = current_quantity / average_daily_sales
where average_daily_sales = total_units_sold (last 30 days) / days_with_data
```

### Without Sales Data
```
days_of_stock = current_quantity / estimated_daily_sales
where estimated_daily_sales = quantity / (365 / typical_stock_turnover)
```

## Confidence Levels

### High Confidence
- Actual sales data available for product
- Based on recent sales history (last 30 days)
- Language: "This assessment is based on recent average sales and may change if demand shifts."

### Low Confidence
- No sales data available
- Uses industry estimates
- Language: "This assessment is based on estimated sales patterns. Providing actual sales data will significantly improve accuracy."

### Mixed Confidence
- Some products have sales data, others don't
- Language: "This assessment uses actual sales data where available. For X products without sales history, estimates are based on typical industry patterns."

## Insufficient Data Insight

Generated when:
- No sales data provided, OR
- Less than 50% of products have sales data

**Purpose:** Ensures we don't silently report "no issues" when lacking data needed for accurate assessment.

**Example:**
```
Title: "Insufficient Sales Data for Accurate Analysis"
Severity: LOW
Description: "Sales summary data was not provided. Stock-out risk assessments are based on estimated sales patterns rather than your actual sales history. This reduces the accuracy of timing predictions."
Recommendation: "To improve accuracy, provide a sales summary CSV with date, product_id, and units_sold columns."
```

## Example Report Output

### With Sales Data
```
Stock-Out Risk: 3 products at risk

Three products may run out within the next 1-2 weeks, including 1 top seller. 
This could result in missed sales and customer dissatisfaction.

Products needing immediate attention: Widget A, Widget B

This assessment is based on recent average sales and may change if demand shifts.
```

### Without Sales Data
```
Stock-Out Risk: 3 products at risk

Three products may run out within the next 1-2 weeks, including 1 top seller. 
This could result in missed sales and customer dissatisfaction.

Products needing immediate attention: Widget A, Widget B

This assessment is based on estimated sales patterns. Providing actual sales data 
will significantly improve accuracy. Stock-out timing may vary if demand changes.

---

Insufficient Sales Data for Accurate Analysis

Sales summary data was not provided. Stock-out risk assessments are based on 
estimated sales patterns rather than your actual sales history. This reduces 
the accuracy of timing predictions.

To improve accuracy, provide a sales summary CSV with date, product_id, and 
units_sold columns. This allows the system to calculate actual inventory velocity 
for more precise stock-out predictions.
```

## Language Improvements

### Before
- "3 products are below the low stock threshold"
- "This represents 1.5% of total inventory value"

### After
- "Three products may run out within the next 1-2 weeks if current demand continues"
- Focus on consequences: "This could result in missed sales and customer dissatisfaction"
- Clear confidence statements about data quality

## Architecture Compliance

✅ **No architecture changes** - All changes are additive
✅ **Deterministic logic** - Same inputs produce same outputs
✅ **Testable** - All logic is explicit and traceable
✅ **Explainable** - Confidence levels clearly communicated
✅ **Backward compatible** - Works without sales data (uses estimates)

## Testing Considerations

- Test with sales data provided
- Test without sales data (should use estimates)
- Test with partial sales data (some products have data, others don't)
- Test insufficient data insight generation
- Verify confidence language matches data quality

