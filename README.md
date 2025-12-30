# Business Analyst System

A Python-based analytics engine for small local retail shops that produces plain-English insights and recommendations from inventory and sales data. The system identifies business risks (like stock-outs) using deterministic, rule-based logic and presents findings in clear, actionable reports.

## What It Does

The Business Analyst System analyzes your inventory and sales data to identify potential issues before they become problems. It:

- **Calculates stock-out risk** based on current inventory levels and sales velocity
- **Prioritizes products** by business impact (top sellers get higher priority)
- **Generates weekly reports** with plain-English insights and recommendations
- **Works with minimal data** - uses industry estimates when sales history is unavailable

The system is designed for small business owners who need actionable insights without technical complexity.

## Architecture Overview

The system follows a layered, plugin-based architecture where each component has a single responsibility:

```
┌─────────────────────────────────────────┐
│         AnalyticsEngine                 │
│      (Main Orchestrator)                │
└─────────────────────────────────────────┘
              │
    ┌─────────┼─────────┐
    │         │         │
    ▼         ▼         ▼
┌────────┐ ┌────────┐ ┌────────┐
│  Data  │ │Context │ │ Checks │
│ Layer  │ │ Layer  │ │ Layer  │
└────────┘ └────────┘ └────────┘
```

### Core Modules

- **`core/`** - Main orchestrator (`AnalyticsEngine`), insight data structures, and exceptions
- **`data/`** - Data ingestion (CSV), validation, and feature extraction
- **`context/`** - Industry-specific business rules and thresholds (currently supports retail)
- **`checks/`** - Analyst checks that identify business issues (e.g., stock-out risk)
- **`insights/`** - Insight prioritization and natural language explanation
- **`delivery/`** - Report generation (weekly business reports)

### Key Design Patterns

- **Strategy Pattern**: Each analyst check is a pluggable strategy
- **Factory Pattern**: Business contexts created by industry-specific factories
- **Registry Pattern**: Checks are automatically discovered and registered
- **Dependency Injection**: All components are testable and swappable

For detailed architecture documentation, see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Unified CSV Input Format

The system uses a **unified CSV format** that combines inventory snapshot and sales history in a single file. This ensures accurate temporal alignment between inventory levels and sales activity.

### Required Columns

- `as_of_date` - Inventory snapshot date (YYYY-MM-DD)
- `product_id` - Unique product identifier
- `product_name` - Product name
- `price` - Product price
- `starting_quantity` - Stock quantity as of snapshot date (inventory rows only)
- `date` - Sales date (YYYY-MM-DD) (sales rows only)
- `units_sold` - Units sold on that date (sales rows only)

### Format Structure

**Inventory rows**: One row per product with `starting_quantity` filled in  
**Sales rows**: Multiple rows per product with `date` and `units_sold` filled in  
**Temporal alignment**: Sales dates must be **after** `as_of_date`

### Example CSV

```csv
as_of_date,product_id,product_name,price,starting_quantity,date,units_sold
2024-12-01,P001,Widget A,10.50,150,,
2024-12-01,P001,Widget A,10.50,,2024-12-02,3
2024-12-01,P001,Widget A,10.50,,2024-12-03,5
2024-12-01,P001,Widget A,10.50,,2024-12-04,4
2024-12-01,P002,Widget B,25.00,5,,
2024-12-01,P002,Widget B,25.00,,2024-12-02,1
2024-12-01,P002,Widget B,25.00,,2024-12-03,1
```

**Key points:**
- Inventory snapshot is captured as of a specific date (`as_of_date`)
- Sales rows represent activity **after** that date
- Missing sales data is acceptable - system uses industry estimates
- See `sample_unified_data.csv` for a complete example

For detailed CSV format documentation, see [docs/UNIFIED_CSV_REFACTORING.md](docs/UNIFIED_CSV_REFACTORING.md).

## Quick Start

### Prerequisites

- Python 3.8+
- pip

### Installation

1. **Clone or download the repository**

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Running the Streamlit UI (Recommended)

The easiest way to use the system:

```bash
streamlit run streamlit_app.py
```

Then:
1. Open your browser to `http://localhost:8501`
2. Upload your unified CSV file
3. Select your business type (currently "retail")
4. Enter your business name
5. Click "Run Business Check-Up"
6. Review insights and download the report

### Running from Python API

```python
from business_analyst.core.engine import AnalyticsEngine
from business_analyst.context.factory import BusinessContextFactory
from business_analyst.checks.registry import CheckRegistry

# Initialize
context = BusinessContextFactory.create("retail")
registry = CheckRegistry()
engine = AnalyticsEngine(context, registry)

# Analyze data
insights = engine.analyze("your_data.csv")

# Generate report
report = engine.generate_report(insights, business_name="Your Business")
print(report)
```

See `example_usage.py` for a complete example.

## Current Analyst Checks

### Stock-Out Risk Check

**Purpose**: Identifies products at risk of running out of stock based on days-of-stock calculations.

**How it works**:
- Calculates `days_of_stock = current_quantity / average_daily_sales`
- Uses actual sales data when available, otherwise estimates from industry norms
- Assigns severity based on days remaining and product importance (top sellers get higher priority)

**Severity thresholds**:
- **CRITICAL** (Immediate attention): < 7 days of stock, or top seller with < 7 days
- **HIGH** (Action needed soon): 7-14 days of stock, or top seller with 7-14 days
- **MEDIUM** (Monitor): > 14 days but top seller, or regular product with 7-14 days

**Output example**:
```
Stock-Out Risk: 2 products need immediate attention

Immediate attention:
Widget A (may run out this week at the current rate of sales), 
Widget B (may run out this week at the current rate of sales)

These products may run out this week at the current rate of sales. 
This could result in missed sales and customer dissatisfaction.

Action needed soon:
Widget C (may run out in the next 1–2 weeks at the current rate of sales)

These products should be reordered soon to avoid future shortages.
```

**Data quality handling**:
- Generates informational insight when sales data is missing or incomplete
- Clearly indicates when estimates are being used vs. actual sales data
- Confidence statements explain data quality impact on accuracy

For detailed implementation, see [docs/STOCKOUT_RISK_REFINEMENT.md](docs/STOCKOUT_RISK_REFINEMENT.md).

## Design Principles

### Trust-First
- Missing data reduces **confidence**, not trust
- Clear statements about data quality and estimation methods
- No hidden assumptions - all logic is explicit

### Explainable
- Every insight can be traced to specific rules and thresholds
- Metrics are included in insights for transparency
- Plain-English explanations, not technical jargon

### Deterministic Logic
- All checks use rule-based logic (no ML models for decision-making)
- Same inputs always produce same outputs
- Fully testable and debuggable

### Streamlit as Thin UI
- All business logic is in the engine, not the UI
- Streamlit only handles presentation and user input
- Backend can be used independently (API, scripts, etc.)

### LLM Only for Wording (If Applicable)
- Decision-making logic is never influenced by LLMs
- LLMs (if used) only enhance explanations after insights are determined
- System remains functional even if LLM is unavailable

For detailed design rationale, see [docs/DESIGN_RATIONALE.md](docs/DESIGN_RATIONALE.md).

## Roadmap / Next Improvements

- **Additional analyst checks**:
  - Slow-moving inventory detection
  - Price optimization opportunities
  - Seasonal demand patterns
  - Cash flow risk from inventory levels

- **Enhanced data sources**:
  - Direct POS system integration
  - API-based data ingestion
  - Historical trend analysis

- **Report enhancements**:
  - PDF report generation
  - Email delivery
  - Scheduled weekly reports
  - Customizable report templates

- **Multi-industry support**:
  - Restaurant/food service context
  - Manufacturing inventory context
  - Service business context

- **Advanced features**:
  - Historical comparison (week-over-week, month-over-month)
  - Predictive alerts (notify before stock-out)
  - Reorder point recommendations
  - Supplier performance tracking

- **UI improvements**:
  - Interactive charts and visualizations
  - Historical trend graphs
  - Product detail drill-down
  - Export to Excel/CSV

- **Performance optimizations**:
  - Caching for large datasets
  - Parallel check execution
  - Incremental data processing

## Project Structure

```
business_analyst/
├── core/           # Main orchestrator, insight types, exceptions
├── data/           # Data ingestion, validation, feature extraction
├── context/         # Industry-specific business rules
├── checks/         # Analyst checks (stock-out risk, etc.)
├── insights/       # Insight prioritization and explanation
├── delivery/       # Report generation
└── tests/          # Test suite

streamlit_app.py    # Streamlit UI (thin presentation layer)
example_usage.py     # Python API usage example
requirements.txt    # Python dependencies
```

## Dependencies

- `pandas>=2.0.0` - Data manipulation
- `streamlit>=1.28.0` - Web UI (optional, only needed for Streamlit interface)

## Contributing

To add a new analyst check:

1. Create a class inheriting from `AnalystCheck` in `business_analyst/checks/`
2. Implement `name`, `description`, and `execute()` methods
3. Register with `CheckRegistry` (or add to default registration)

See [docs/IMPLEMENTATION_SUMMARY.md](docs/IMPLEMENTATION_SUMMARY.md) for detailed examples.

## Documentation

- [Architecture Details](docs/ARCHITECTURE.md) - Detailed system architecture and class diagrams
- [Design Rationale](docs/DESIGN_RATIONALE.md) - Design decisions and trade-offs
- [Implementation Summary](docs/IMPLEMENTATION_SUMMARY.md) - Component overview and extension guide
- [Unified CSV Format](docs/UNIFIED_CSV_REFACTORING.md) - Detailed CSV format documentation
- [Stock-Out Risk Check](docs/STOCKOUT_RISK_REFINEMENT.md) - Stock-out risk check implementation details

## License

[Add your license here]

## Support

For questions or issues, please [open an issue] or contact the maintainers.
