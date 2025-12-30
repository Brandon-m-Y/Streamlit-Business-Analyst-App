# Communication Quality Improvements

## Overview

Refined the stock-out risk insight wording and report formatting to improve clarity, consistency, and human readability for small local shop owners. All underlying analyst logic remains unchanged.

## Files Modified

### 1. `business_analyst/checks/stockout_risk.py`
**Changes:**
- Restructured description to separate urgency levels clearly
- Products listed in order: CRITICAL → HIGH → MEDIUM
- Each section names products with time estimates
- Improved recommendation clarity and action-orientation

### 2. `business_analyst/delivery/report.py`
**Changes:**
- Executive summary only highlights CRITICAL items (aligns with detailed insights)
- Added SMB-friendly severity labels (CRITICAL → "Immediate attention", etc.)
- Removed mixing of severity levels in summary

### 3. `streamlit_app.py`
**Changes:**
- Updated severity labels to match report formatting
- Changed section headers to match new language
- Uses markdown rendering for better formatting

## Before vs. After Examples

### Before (Old Format)

**Title:**
```
Stock-Out Risk: 3 products at risk, 1 product running low
```

**Description:**
```
3 products may run out within the next 1-2 weeks if current demand continues, 
including 1 top seller. This could result in missed sales and customer dissatisfaction. 
Another 1 product is running low and should be monitored.

Products needing immediate attention: Widget A, Widget B

Note: Sales velocity estimates are based on typical industry patterns. 
Actual stock-out timing may vary if demand changes.
```

**Recommendation:**
```
Prioritize reordering for top sellers to avoid revenue loss. 
Review sales patterns and consider placing orders for products 
with less than 2 weeks of stock remaining.
```

**Executive Summary:**
```
What needs attention this week:
- 2 products at risk of running out this week
- 1 high-priority item to address soon
```

### After (New Format)

**Title:**
```
Stock-Out Risk: 2 products need immediate attention
```

**Description:**
```
Immediate attention (this week):
Widget A (may run out within the next week), Widget B (may run out within the next week)

These products are likely to run out within the next week if current demand continues. 
Running out of stock could result in missed sales and customer dissatisfaction.

Action needed soon (next 1-2 weeks):
Widget C (may run out within the next 1-2 weeks)

These products have low stock levels and should be reordered soon to avoid future shortages.

Monitor:
Widget D (may run out within the next 2-3 weeks)

These products should be watched but do not require immediate action.

This assessment is based on recent average sales and may change if demand shifts.
```

**Recommendation:**
```
Prioritize reordering items with less than one week of stock remaining. 
Plan reorders soon for products with less than two weeks of stock to avoid future shortages. 
Pay special attention to top-selling products to avoid revenue loss.
```

**Executive Summary:**
```
What needs attention this week:
- 2 products need immediate attention

Additional items to review: 2
```

## Key Improvements

### 1. Clear Urgency Separation
- ✅ Products grouped by urgency level
- ✅ Each section clearly labeled
- ✅ No mixing of severity levels in single sentences

### 2. Product Ordering
- ✅ CRITICAL products listed first
- ✅ HIGH products listed second
- ✅ MEDIUM products listed last
- ✅ Within each group, sorted by days-of-stock (most urgent first)

### 3. Structured Sections
- ✅ "Immediate attention (this week)" - CRITICAL
- ✅ "Action needed soon (next 1-2 weeks)" - HIGH
- ✅ "Monitor" - MEDIUM
- ✅ Each product includes time estimate: "Widget A (may run out within the next week)"

### 4. Executive Summary Alignment
- ✅ Only shows CRITICAL items in main summary
- ✅ Counts match detailed insights exactly
- ✅ Lower-severity items shown as "Additional items to review"

### 5. SMB-Friendly Language
- ✅ CRITICAL → "Immediate attention"
- ✅ HIGH → "Action needed soon"
- ✅ MEDIUM → "Monitor"
- ✅ LOW → "Informational"
- ✅ Internal severity enums unchanged

### 6. Action-Oriented Recommendations
- ✅ "Prioritize reordering items with less than one week of stock remaining"
- ✅ "Plan reorders soon for products with less than two weeks of stock"
- ✅ Clear, concise, no analyst jargon

## Natural Language Flow

The new format reads naturally when spoken:

> "Immediate attention this week: Widget A may run out within the next week, Widget B may run out within the next week. These products are likely to run out within the next week if current demand continues. Running out of stock could result in missed sales and customer dissatisfaction.
>
> Action needed soon, next 1-2 weeks: Widget C may run out within the next 1-2 weeks. These products have low stock levels and should be reordered soon to avoid future shortages."

## Tone Characteristics

- ✅ **Clear**: Structured sections make it easy to scan
- ✅ **Calm**: Professional language, not alarmist
- ✅ **Professional**: Business advisor tone, not system alert
- ✅ **Human**: Natural phrasing, appropriate for non-technical owners

## Architecture Compliance

✅ **No logic changes** - All analyst calculations unchanged
✅ **No new insights** - Only wording improvements
✅ **No UI logic** - Presentation layer only
✅ **Deterministic** - Same inputs produce same outputs (with better wording)

## Example Complete Report Section

```
### 1. Stock-Out Risk: 2 products need immediate attention
**Priority:** Immediate attention

Immediate attention (this week):
Widget A (may run out within the next week), Widget B (may run out within the next week)

These products are likely to run out within the next week if current demand continues. 
Running out of stock could result in missed sales and customer dissatisfaction.

Action needed soon (next 1-2 weeks):
Widget C (may run out within the next 1-2 weeks)

These products have low stock levels and should be reordered soon to avoid future shortages.

**Recommendation:**
Prioritize reordering items with less than one week of stock remaining. 
Plan reorders soon for products with less than two weeks of stock to avoid future shortages. 
Pay special attention to top-selling products to avoid revenue loss.

This assessment is based on recent average sales and may change if demand shifts.
```

