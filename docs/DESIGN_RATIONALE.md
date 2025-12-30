# Design Rationale

This document explains the key design decisions and why this architecture fits the problem domain.

## Core Principles Implementation

### 1. Encode Analyst Judgment, Not Generic Analytics

**Decision**: Each `AnalystCheck` is a self-contained class that encodes specific business judgment rules.

**Rationale**: 
- Checks are opinionated and domain-specific (e.g., "stock-out risk" uses specific thresholds)
- No generic "analyze data" functions that require configuration
- Each check represents a concrete business question with a deterministic answer

**Example**: `StockOutRiskCheck` doesn't just flag low quantities—it uses industry-specific thresholds from `BusinessContext` to make judgments.

### 2. Opinionated Defaults Over Customization

**Decision**: Business contexts provide fixed thresholds and norms. Checks use these without allowing per-check customization.

**Rationale**:
- Reduces configuration complexity
- Ensures consistency across checks
- Makes the system easier to understand and maintain
- Users get expert defaults, not blank slates

**Example**: `RetailContext` defines `low_stock_ratio: 0.2` as a fixed default. All retail checks use this.

### 3. Explainability Over Model Complexity

**Decision**: All logic is rule-based and explicit. No black-box models.

**Rationale**:
- Every insight can be traced to specific rules and thresholds
- Metrics are explicitly included in insights
- Explanations are generated from the same logic that created the insight
- No "model says X" without understanding why

**Example**: Stock-out risk insight includes exact metrics (threshold, count, percentage) that explain the judgment.

### 4. Deterministic and Testable Logic

**Decision**: All checks are pure functions (given same inputs, same outputs). No randomness or non-deterministic behavior.

**Rationale**:
- Enables unit testing of every check
- Results are reproducible
- Debugging is straightforward
- No surprises in production

**Example**: `StockOutRiskCheck.execute()` always produces the same insights for the same input data and context.

### 5. AI Only for Explanation, Never for Decision-Making

**Decision**: LLMs are isolated in `ExplanationGenerator` and only called after insights are already determined.

**Rationale**:
- Decisions are made by deterministic checks
- LLMs can only enhance explanations, never influence what matters
- System remains testable and debuggable even if LLM is unavailable
- Clear separation of concerns

**Example**: `ExplanationGenerator` receives fully-formed `Insight` objects. It never sees raw data or makes decisions.

## Architecture Patterns

### Strategy Pattern for Checks

**Decision**: Each analyst check is a strategy that can be plugged in.

**Rationale**:
- New checks can be added without modifying existing code
- Checks are independent and testable in isolation
- Easy to enable/disable checks
- Supports different check types (risk, opportunity, anomaly, etc.)

### Factory Pattern for Contexts

**Decision**: `BusinessContextFactory` creates industry-specific contexts.

**Rationale**:
- Supports multiple industries without large if/else chains
- Easy to add new industries by registering new context classes
- Contexts are self-contained and testable
- Clear separation between industry-specific logic and generic logic

### Registry Pattern for Checks

**Decision**: `CheckRegistry` manages all checks and can discover applicable ones.

**Rationale**:
- Checks are automatically discovered and registered
- Easy to add new checks without modifying core engine
- Supports filtering by industry (via `is_applicable()`)
- Enables dynamic check loading in the future

### Dependency Injection

**Decision**: All components receive dependencies via constructor injection.

**Rationale**:
- Enables easy testing with mocks
- Components are loosely coupled
- Clear dependencies make the system easier to understand
- Supports different implementations (e.g., different data ingesters)

## Separation of Concerns

### Data Layer (Ingestion → Validation → Extraction)

**Decision**: Raw data flows through: Ingestion → Validation → Feature Extraction → Deletion

**Rationale**:
- Each step has a single responsibility
- Validation happens before expensive processing
- Feature extraction allows raw data deletion (privacy/compliance)
- Features are industry-agnostic, enabling reuse

### Business Context Layer

**Decision**: Industry-specific knowledge is isolated in `BusinessContext` subclasses.

**Rationale**:
- No hardcoded industry logic in checks
- Easy to add new industries
- Contexts are testable independently
- Clear contract (thresholds, norms, schema)

### Check Layer

**Decision**: Checks are independent, stateless classes that use context and features.

**Rationale**:
- Checks don't know about other checks
- Easy to add/remove checks
- Each check can be tested in isolation
- Checks can be parallelized in the future

### Insight Processing Layer

**Decision**: Insights are prioritized and explained separately from their generation.

**Rationale**:
- Prioritization logic is centralized and consistent
- Explanation generation is pluggable (template vs. LLM)
- Insights are immutable data structures
- Easy to add new prioritization or explanation strategies

### Delivery Layer

**Decision**: Report generation is separate from analysis.

**Rationale**:
- Same insights can be formatted differently
- Easy to add new delivery formats (email, PDF, etc.)
- Report generation doesn't affect analysis logic
- Supports different report frequencies (daily, weekly, etc.)

## Extensibility Points

### Adding New Checks

1. Create a class inheriting from `AnalystCheck`
2. Implement `name`, `description`, and `execute()` methods
3. Register with `CheckRegistry`
4. No modification to existing code required

### Adding New Industries

1. Create a class inheriting from `BusinessContext`
2. Implement required methods with industry-specific values
3. Register with `BusinessContextFactory`
4. Existing checks automatically work if `is_applicable()` returns True

### Adding New Data Sources

1. Create a class inheriting from `DataIngester`
2. Implement `ingest()` method
3. Pass to `AnalyticsEngine` constructor
4. No modification to other components required

### Adding New Explanation Methods

1. Extend `ExplanationGenerator` or create a new class
2. Implement explanation logic
3. Pass to `AnalyticsEngine` constructor
4. No modification to checks required

## Testability

### Unit Testing

- Each component can be tested in isolation
- Dependencies are injected, enabling mocks
- Checks are pure functions (same input → same output)
- Contexts are simple data containers

### Integration Testing

- `AnalyticsEngine` orchestrates the full flow
- Can test with real data files
- Can verify end-to-end behavior
- Can test error handling at each layer

### Example Test Structure

```python
# Test individual check
check = StockOutRiskCheck()
insights = check.execute(features, context)
assert len(insights) > 0

# Test context
context = RetailContext()
threshold = context.get_threshold('low_stock_ratio')
assert threshold == 0.2

# Test engine
engine = AnalyticsEngine(context, registry)
insights = engine.analyze('data.csv')
report = engine.generate_report(insights)
```

## Why This Architecture Fits

1. **Scalability**: New checks and industries can be added without touching existing code
2. **Maintainability**: Clear separation of concerns makes code easy to understand and modify
3. **Testability**: Dependency injection and pure functions enable comprehensive testing
4. **Determinism**: All logic is explicit and rule-based, no surprises
5. **Explainability**: Every insight can be traced to specific rules and metrics
6. **Flexibility**: Components can be swapped (different ingesters, explainers, etc.)
7. **Production-Ready**: Error handling, validation, and clear interfaces throughout

## Trade-offs

### Pros
- Clear separation of concerns
- Highly extensible
- Easy to test
- Deterministic and explainable
- Production-ready structure

### Cons
- More classes than a simple script (but necessary for scalability)
- Some indirection (but enables flexibility)
- Initial setup more complex (but pays off as system grows)

## Future Enhancements

The architecture supports these without major refactoring:

- **Caching**: Add caching layer between feature extraction and checks
- **Parallelization**: Checks can run in parallel (they're independent)
- **Streaming**: Can process data in chunks with same architecture
- **API Integration**: Add more `DataIngester` implementations
- **Advanced Explanation**: Enhance `ExplanationGenerator` with LLMs
- **Multi-Industry Checks**: Checks can implement `is_applicable()` to filter by industry
- **Historical Analysis**: Add time-series features to context
- **Alerting**: Add delivery mechanism for critical insights

