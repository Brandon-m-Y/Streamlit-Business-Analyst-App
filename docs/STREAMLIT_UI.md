# Streamlit UI Documentation

## Overview

The Streamlit UI (`streamlit_app.py`) is a **thin presentation layer** that provides a user-friendly interface for the Business Analyst System. It does not contain any business logic - all analysis is performed by the existing `AnalyticsEngine`.

## Architecture Compliance

✅ **No Streamlit imports in backend modules** - All Streamlit code is isolated in `streamlit_app.py`

✅ **No business logic in UI** - The UI only:
- Collects user input (CSV file, business name, industry selection)
- Calls existing engine APIs (`engine.analyze()`, `engine.generate_report()`)
- Formats and displays results

✅ **No modifications to existing engine** - All backend code remains unchanged

## Key Components

### File Upload Handler
```python
save_uploaded_file(uploaded_file) -> str
```
- Saves uploaded CSV to temporary file
- Returns path for `AnalyticsEngine.analyze()`
- Cleans up temp file after analysis

### Display Formatter
```python
format_insight_for_display(insight) -> dict
```
- Maps backend `Insight` objects to user-friendly format
- Adds emojis and severity labels
- No business logic - pure presentation

### Insights Display
```python
display_insights_summary(insights)
```
- Groups insights by severity (using existing `Severity` enum)
- Emphasizes "What needs attention" (critical/high priority)
- Shows "What to do next" (recommendations)
- Uses Streamlit components for friendly display

## User Flow

1. **Upload CSV** → File saved temporarily
2. **Select Industry** → Uses `BusinessContextFactory.create()`
3. **Enter Business Name** → Used in report generation
4. **Run Analysis** → Calls `engine.analyze(temp_file_path)`
5. **View Results** → Displays insights grouped by priority
6. **Download Report** → Uses `engine.generate_report()`

## Integration Points

### Uses Existing Classes
- `AnalyticsEngine` - Main orchestrator
- `BusinessContextFactory` - Industry context creation
- `CheckRegistry` - Check discovery
- `Severity` enum - Insight prioritization
- `DataValidationError`, `FeatureExtractionError` - Error handling

### No Modifications Required
- All engine components work as-is
- No adapter layers needed
- Direct API calls to existing methods

## Running the UI

```bash
# Install dependencies
pip install -r requirements.txt

# Run Streamlit app
streamlit run streamlit_app.py
```

The app will open in your browser at `http://localhost:8501`

## UI Features

### Main Interface
- **File Upload**: Drag-and-drop CSV upload
- **Industry Selection**: Dropdown from available industries
- **Business Name**: Customizable for reports
- **Analysis Button**: Triggers engine analysis

### Results Display
- **Summary Metrics**: Critical, High, Medium, Low counts
- **Priority Grouping**: Insights organized by severity
- **Expandable Sections**: Details hidden by default
- **Action Items**: Clear "What to do" recommendations
- **Full Report**: Complete text report with download option

### Error Handling
- Data validation errors (missing columns, wrong types)
- Processing errors (feature extraction failures)
- User-friendly error messages with guidance

## Design Principles

1. **Non-Technical Language**: All text is plain English
2. **Action-Oriented**: Focus on "What needs attention" and "What to do next"
3. **Minimal Configuration**: No complex settings panels
4. **Clear Feedback**: Success/error states clearly indicated
5. **Progressive Disclosure**: Details available but not overwhelming

## Future Enhancements

The UI can be extended without modifying backend:
- Multiple file upload support
- Historical comparison views
- Email report delivery
- Custom report templates
- Industry-specific guidance

All enhancements would use existing engine APIs.

