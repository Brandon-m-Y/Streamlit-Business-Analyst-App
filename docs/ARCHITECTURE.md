# Business Analyst System - Architecture Overview

## High-Level Architecture

The system follows a layered, plugin-based architecture where each component has a single responsibility and can be extended without modifying existing code.

```
┌─────────────────────────────────────────────────────────────┐
│                    AnalyticsEngine                           │
│              (Orchestrates the entire flow)                  │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│ DataIngester  │   │ BusinessContext│   │ AnalystCheck │
│               │   │   Factory      │   │   Registry   │
└───────────────┘   └───────────────┘   └───────────────┘
        │                   │                   │
        ▼                   ▼                   ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│DataValidator  │   │  Industry-    │   │  Individual   │
│               │   │  Specific     │   │  Checks       │
└───────────────┘   │  Contexts     │   └───────────────┘
        │           └───────────────┘
        ▼
┌───────────────┐
│FeatureExtractor│
└───────────────┘
        │
        ▼
┌───────────────┐
│   Insights    │
└───────────────┘
        │
        ▼
┌───────────────┐
│Prioritizer    │
└───────────────┘
        │
        ▼
┌───────────────┐
│ExplanationGen │
└───────────────┘
        │
        ▼
┌───────────────┐
│ReportGenerator│
└───────────────┘
```

## Class Diagrams

### Core Classes

```
AnalyticsEngine
├── context: BusinessContext
├── check_registry: CheckRegistry
├── ingester: DataIngester
├── validator: DataValidator
├── extractor: FeatureExtractor
├── prioritizer: InsightPrioritizer
├── explainer: ExplanationGenerator
└── report_generator: ReportGenerator
    ├── analyze(data_source: str) -> List[Insight]
    ├── generate_report(insights: List[Insight]) -> str
    └── analyze_and_report(data_source: str) -> str
```

### Data Layer

```
DataIngester (ABC)
├── ingest(source: str) -> pd.DataFrame
│
├── CSVIngester
│   └── ingest(source: str) -> pd.DataFrame
│
└── APIIngester
    └── ingest(source: str) -> pd.DataFrame

DataValidator
├── required_columns: List[str]
├── column_types: Dict[str, type]
└── validate(df: pd.DataFrame) -> None

FeatureExtractor
└── extract(df: pd.DataFrame) -> Dict[str, Any]
```

### Context Layer

```
BusinessContext (ABC)
├── industry: str (property)
├── get_threshold(metric_name: str) -> float
├── get_norm(norm_name: str) -> Any
├── get_required_columns() -> List[str]
└── get_column_types() -> Dict[str, type]

RetailContext (BusinessContext)
├── _thresholds: Dict[str, float]
├── _norms: Dict[str, Any]
├── _required_columns: List[str]
└── _column_types: Dict[str, type]

BusinessContextFactory
├── _contexts: Dict[str, Type[BusinessContext]]
├── create(industry: str) -> BusinessContext
├── register(industry: str, context_class: Type)
└── list_industries() -> List[str]
```

### Check Layer

```
AnalystCheck (ABC)
├── name: str (property)
├── description: str (property)
├── execute(features: Dict, context: BusinessContext) -> List[Insight]
└── is_applicable(context: BusinessContext) -> bool

StockOutRiskCheck (AnalystCheck)
└── execute(features: Dict, context: BusinessContext) -> List[Insight]

CheckRegistry
├── _checks: Dict[str, AnalystCheck]
├── register(check: AnalystCheck) -> None
├── get(name: str) -> AnalystCheck
├── list_all() -> List[AnalystCheck]
└── get_applicable(context: BusinessContext) -> List[AnalystCheck]
```

### Insight Layer

```
Insight (dataclass)
├── check_name: str
├── title: str
├── description: str
├── severity: Severity
├── insight_type: InsightType
├── metrics: Dict[str, Any]
├── recommendation: Optional[str]
├── timestamp: datetime
└── metadata: Dict[str, Any]

InsightPrioritizer
├── SEVERITY_WEIGHTS: Dict[Severity, int]
├── prioritize(insights: List[Insight]) -> List[Insight]
├── get_critical(insights: List[Insight]) -> List[Insight]
└── get_by_severity(insights: List[Insight], min_severity: Severity) -> List[Insight]

ExplanationGenerator
├── llm_client: Optional[Any]
├── explain(insight: Insight) -> str
└── explain_all(insights: List[Insight]) -> List[str]
```

### Delivery Layer

```
ReportGenerator
├── explainer: ExplanationGenerator
├── prioritizer: InsightPrioritizer
├── generate(insights: List[Insight], business_name: str) -> str
├── _generate_header(business_name: str) -> str
├── _generate_summary(insights: List[Insight]) -> str
├── _generate_insights_section(insights: List[Insight]) -> str
└── _generate_footer() -> str
```

## Design Patterns

1. **Strategy Pattern**: Each analyst check is a strategy that can be plugged in
2. **Factory Pattern**: Business contexts are created by industry-specific factories
3. **Registry Pattern**: Analyst checks are registered and discovered automatically
4. **Template Method**: Base classes define the flow, subclasses implement specifics
5. **Dependency Injection**: All dependencies are injected for testability

## Key Design Decisions

1. **Separation of Data and Logic**: Raw data is processed into features immediately, allowing raw data deletion
2. **Industry Abstraction**: Business context is abstracted, allowing multiple industries without conditionals
3. **Check Independence**: Each check is self-contained and can be added/removed without affecting others
4. **Deterministic Logic**: All checks use explicit rules, no ML models for decision-making
5. **Explanation Separation**: LLM-based explanation is a separate layer that never influences decisions

