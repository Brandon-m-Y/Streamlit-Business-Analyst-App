"""Example usage of the Business Analyst System."""

from business_analyst.core.engine import AnalyticsEngine
from business_analyst.context.factory import BusinessContextFactory
from business_analyst.checks.registry import CheckRegistry


def main():
    """Example of using the business analyst system."""
    
    # Step 1: Create business context for retail industry
    context = BusinessContextFactory.create("retail")
    print(f"Created context for industry: {context.industry}")
    
    # Step 2: Initialize check registry (automatically registers default checks)
    registry = CheckRegistry()
    print(f"Registered checks: {[check.name for check in registry.list_all()]}")
    
    # Step 3: Create analytics engine
    engine = AnalyticsEngine(context, registry)
    
    # Step 4: Analyze data
    try:
        data_source = "sample_data.csv"
        print(f"\nAnalyzing data from: {data_source}")
        insights = engine.analyze(data_source)
        print(f"Generated {len(insights)} insights")
        
        # Step 5: Generate report
        report = engine.generate_report(insights, business_name="My Retail Store")
        print("\n" + "="*60)
        print("GENERATED REPORT:")
        print("="*60)
        print(report)
    except FileNotFoundError:
        print(f"\nNote: {data_source} not found. Using sample data would generate insights.")
        print("To use with your own data:")
        print("1. Create a CSV file with columns: product_id, product_name, quantity, price")
        print("2. Update the data_source variable above")
        print("3. Run the script again")


if __name__ == "__main__":
    main()

