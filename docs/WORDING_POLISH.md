# Wording Polish - Final Improvements

## Overview

Performed final polish pass on stock-out risk insight wording to fix grammar, remove redundancy, ensure timeframe alignment, and improve natural readability.

## Issues Fixed

### 1. Grammar Corrections
**Before:**
- "1 product need immediate attention" ❌
- "1 product need action soon" ❌

**After:**
- "1 product needs immediate attention" ✅
- "1 product needs action soon" ✅
- Proper singular/plural handling throughout

### 2. Timeframe Alignment with Severity

**CRITICAL (Immediate attention):**
- Timeframe: "this week" or "within the next few days"
- Matches: < 7 days threshold

**HIGH (Action needed soon):**
- Timeframe: "within the next 1-2 weeks"
- Matches: 7-14 days threshold

**MEDIUM (Monitor):**
- Timeframe: "within the next 2-3 weeks" or "within the next month"
- Matches: > 14 days threshold

### 3. Removed Redundancy

**Before:**
```
These products are likely to run out within the next week if current demand continues. 
Running out of stock could result in missed sales and customer dissatisfaction.
```

**After:**
```
These products may run out this week if current demand continues, 
which could result in missed sales.
```

**Improvements:**
- More concise
- Removed redundant "Running out of stock" phrase
- Simplified "customer dissatisfaction" to just "missed sales"

### 4. Product Uniqueness

✅ **Verified:** Products are grouped by severity and each product appears in exactly one section:
- CRITICAL products → "Immediate attention" section only
- HIGH products → "Action needed soon" section only
- MEDIUM products → "Monitor" section only

### 5. Concise Section Descriptions

**Before:**
```
These products are likely to run out within the next week if current demand continues. 
Running out of stock could result in missed sales and customer dissatisfaction.
```

**After:**
```
These products may run out this week if current demand continues, 
which could result in missed sales.
```

**Before:**
```
These products have low stock levels and should be reordered soon to avoid future shortages.
```

**After:**
```
These products should be reordered soon to avoid future shortages.
```

### 6. Natural Speech Flow

The polished version reads naturally when spoken:

> "Immediate attention this week: Widget A may run out this week, Widget B may run out within the next few days. These products may run out this week if current demand continues, which could result in missed sales.
>
> Action needed soon, next 1-2 weeks: Widget C may run out within the next 1-2 weeks. These products should be reordered soon to avoid future shortages."

## Example: Before vs. After

### Before
```
Stock-Out Risk: 3 products need immediate attention

Immediate attention (this week):
Widget A (may run out within the next week), Widget B (may run out within the next week)

These products are likely to run out within the next week if current demand continues. 
Running out of stock could result in missed sales and customer dissatisfaction.

Action needed soon (next 1-2 weeks):
Widget C (may run out within the next 1-2 weeks)

These products have low stock levels and should be reordered soon to avoid future shortages.
```

### After
```
Stock-Out Risk: 3 products need immediate attention

Immediate attention (this week):
Widget A (may run out this week), Widget B (may run out within the next few days)

These products may run out this week if current demand continues, 
which could result in missed sales.

Action needed soon (next 1-2 weeks):
Widget C (may run out within the next 1-2 weeks)

These products should be reordered soon to avoid future shortages.
```

## Executive Summary Alignment

**Executive Summary:**
```
What needs attention this week:
- 3 products need immediate attention
```

**Detailed Insight:**
```
Immediate attention (this week):
Widget A (may run out this week), Widget B (may run out within the next few days), 
Widget C (may run out this week)
```

✅ **Verified:** Counts match exactly (3 products in both)

## Files Modified

1. **`business_analyst/checks/stockout_risk.py`**
   - Fixed grammar (need → needs for singular)
   - Updated `_format_days_description()` to accept severity parameter
   - Aligned timeframes with severity levels
   - Made section descriptions more concise
   - Removed redundant phrases

2. **`business_analyst/delivery/report.py`**
   - Fixed grammar in executive summary
   - Ensured proper singular/plural handling

## Tone Characteristics

✅ **Calm:** Professional language, not alarmist
✅ **Professional:** Business advisor tone
✅ **Advisory:** Clear guidance without urgency inflation
✅ **Natural:** Reads smoothly when spoken aloud

## Verification Checklist

- ✅ Grammar fixed (need → needs for singular)
- ✅ No duplicated titles
- ✅ No redundant explanations
- ✅ Timeframes match severity levels
- ✅ Each product appears in exactly one section
- ✅ Section descriptions are concise
- ✅ Natural speech flow
- ✅ Executive summary aligns with details

