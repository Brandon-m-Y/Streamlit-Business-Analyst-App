# Unified CSV Refactoring Summary

## Overview

The system has been refactored from a dual-CSV model (separate inventory and sales files) to a single unified CSV format. This eliminates confusion around starting inventory levels and sales alignment by ensuring temporal grounding in a single file.

## Files Modified

### 1. `business_analyst/data/extractor.py`
**Changes:**
- Updated `extract()` to detect and parse unified CSV format
- Added `_parse_unified_csv()` method to separate inventory and sales rows
- Updated `_calculate_sales_velocity()` to accept `as_of_date` for temporal alignment
- Only counts sales occurring **after** the inventory snapshot date

**Key Logic:**
- Detects unified format by checking for `as_of_date`, `starting_quantity`, `date`, `units_sold` columns
- Separates inventory rows (those with `starting_quantity`) from sales rows (those with `date` and `units_sold`)
- Groups by `product_id` to extract one inventory snapshot per product
- Filters sales to only those after `as_of_date` for accurate velocity calculation

### 2. `business_analyst/data/validator.py`
**Changes:**
- Updated `validate()` to detect format and route to appropriate validator
- Added `_validate_unified_format()` for unified CSV validation
- Added `_validate_legacy_format()` for backward compatibility

**Validation Rules:**
- Unified format requires: `as_of_date`, `product_id`, `starting_quantity`
- Must have at least one inventory row (with `starting_quantity`)
- Sales rows must have `product_id` if present

### 3. `business_analyst/core/engine.py`
**Changes:**
- Updated `analyze()` method signature (maintains backward compatibility)
- Updated docstrings to reflect unified CSV as preferred format
- Legacy separate file mode still supported

### 4. `business_analyst/checks/stockout_risk.py`
**Changes:**
- Updated to use `starting_quantity` instead of `quantity` when available
- Improved language: "may run out within the next 1-2 weeks **if current demand continues**"
- Updated `_create_insufficient_data_insight()` to use INFO severity and improved language
- Changed title to "Data Coverage: Sales History Missing"

**Language Improvements:**
- Before: "3 products may run out within the next 1-2 weeks"
- After: "3 products may run out within the next 1-2 weeks **if current demand continues**"

### 5. `streamlit_app.py`
**Changes:**
- Removed separate file uploaders
- Single CSV file upload only
- Updated UI copy to explain unified format
- Clear explanation of inventory snapshot vs. sales rows
- Sample CSV format shown in expandable section

**UI Improvements:**
- Clear explanation: "Inventory is captured as of a specific date"
- Explains: "Sales rows represent activity after that date"
- Notes: "Missing sales data reduces confidence (not trust)"

### 6. `sample_unified_data.csv` (New File)
**Purpose:** Example unified CSV showing proper format

**Format:**
```
as_of_date,product_id,product_name,price,starting_quantity,date,units_sold
2024-12-01,P001,Widget A,10.50,150,,
2024-12-01,P001,Widget A,10.50,,2024-12-02,3
2024-12-01,P001,Widget A,10.50,,2024-12-03,5
...
```

## Unified CSV Format

### Structure
- **Inventory rows**: One per product with `starting_quantity` filled in
- **Sales rows**: Multiple per product with `date` and `units_sold` filled in
- **Temporal alignment**: Sales dates must be after `as_of_date`

### Required Columns
- `as_of_date`: Inventory snapshot date (YYYY-MM-DD)
- `product_id`: Unique product identifier
- `product_name`: Product name
- `price`: Product price
- `starting_quantity`: Stock quantity as of snapshot date (inventory rows only)
- `date`: Sales date (YYYY-MM-DD) (sales rows only)
- `units_sold`: Units sold on that date (sales rows only)

### Example Row Structure
```
# Inventory row (one per product)
as_of_date,product_id,product_name,price,starting_quantity,date,units_sold
2024-12-01,P001,Widget A,10.50,150,,

# Sales rows (multiple per product, after as_of_date)
2024-12-01,P001,Widget A,10.50,,2024-12-02,3
2024-12-01,P001,Widget A,10.50,,2024-12-03,5
```

## Temporal Alignment

### Key Concept
The system uses `as_of_date` as the inventory anchor point. Only sales occurring **after** this date are used for velocity calculations.

### Why This Matters
- Ensures accurate inventory velocity: we know starting stock and only count sales after that point
- Prevents confusion: no ambiguity about which sales correspond to which inventory level
- Trust-first: clear temporal relationship between inventory and sales

### Implementation
```python
# In _calculate_sales_velocity()
if as_of_date is not None:
    as_of_date = pd.to_datetime(as_of_date)
    sales_df = sales_df[sales_df['date'] > as_of_date].copy()
```

## Days-of-Stock Calculation

### Formula
```
days_of_stock = starting_quantity / average_daily_sales
```

Where `average_daily_sales` is calculated from sales **after** `as_of_date`:
```
average_daily_sales = total_units_sold (after as_of_date) / days_with_data
```

### Severity Thresholds
- < 7 days → HIGH (or CRITICAL if top seller)
- 7-14 days → MEDIUM (or HIGH if top seller)
- > 14 days → LOW (or MEDIUM if top seller)

## Data Coverage Insights

### When Generated
- No sales data provided, OR
- Less than 50% of products have sales data

### Insight Details
- **Title**: "Data Coverage: Sales History Missing"
- **Severity**: INFO (not LOW - this is informational, not a problem)
- **Type**: ANOMALY (data quality issue)
- **Language**: Explains what's missing and how to provide it

### Example Output
```
Data Coverage: Sales History Missing

Sales data was not provided in your file. Stock-out risk assessments are 
based on estimated sales patterns rather than your actual sales history. 
This reduces the accuracy of timing predictions. To improve accuracy, 
include sales rows (with date and units_sold) in your CSV file.

To improve accuracy, add sales rows to your CSV file with date, product_id, 
and units_sold columns. This allows the system to calculate actual inventory 
velocity for more precise stock-out predictions. Sales should represent 
activity after your inventory snapshot date.
```

## Language Improvements

### Preferred Phrasing
- ✅ "This product may run out within the next 1-2 weeks **if current demand continues**"
- ✅ Focus on consequences: "This could result in missed sales and customer dissatisfaction"
- ✅ Clear confidence statements: "This assessment is based on recent average sales and may change if demand shifts"

### Avoided Language
- ❌ Raw statistics without context
- ❌ Minimizing percentages ("1.5% of inventory value")
- ❌ Technical jargon

## Example Report Output

### With Sales Data
```
Stock-Out Risk: 2 products at risk

Two products may run out within the next 1-2 weeks if current demand continues, 
including 1 top seller. This could result in missed sales and customer dissatisfaction.

Products needing immediate attention: Widget B, Widget D

This assessment is based on recent average sales and may change if demand shifts.
```

### Without Sales Data
```
Stock-Out Risk: 2 products at risk

Two products may run out within the next 1-2 weeks if current demand continues. 
Running out of stock could lead to lost sales.

This assessment is based on estimated sales patterns. Providing actual sales data 
will significantly improve accuracy. Stock-out timing may vary if demand changes.

---

Data Coverage: Sales History Missing

Sales data was not provided in your file. Stock-out risk assessments are 
based on estimated sales patterns rather than your actual sales history. 
This reduces the accuracy of timing predictions. To improve accuracy, 
include sales rows (with date and units_sold) in your CSV file.
```

## Backward Compatibility

The system maintains backward compatibility:
- Legacy separate file format still supported
- Detects format automatically
- Validates appropriately based on format detected

## Architecture Compliance

✅ **No architecture changes** - All changes are additive/extensions
✅ **Deterministic logic** - Same inputs produce same outputs
✅ **Testable** - All logic is explicit and traceable
✅ **Explainable** - Temporal alignment clearly documented
✅ **Trust-first** - Missing data reduces confidence, not trust

## Benefits

1. **Eliminates confusion**: Single file with clear temporal relationship
2. **Accurate velocity**: Only counts sales after inventory snapshot
3. **Simpler UI**: One file upload instead of two
4. **Clear data model**: Inventory snapshot + sales activity in one place
5. **Better alignment**: No ambiguity about which sales correspond to which inventory

