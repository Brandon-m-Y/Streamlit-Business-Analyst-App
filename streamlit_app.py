"""
Streamlit UI for Business Analyst System

This is a thin presentation layer that:
- Collects user input (CSV file, business name)
- Calls the existing AnalyticsEngine API
- Displays results in plain English

No business logic is implemented here - all analysis is done by the engine.
"""

import streamlit as st
import tempfile
import os
from pathlib import Path

# Import existing engine components (no Streamlit imports in these modules)
from business_analyst.core.engine import AnalyticsEngine
from business_analyst.context.factory import BusinessContextFactory
from business_analyst.checks.registry import CheckRegistry
from business_analyst.core.insight import Severity
from business_analyst.core.exceptions import DataValidationError, FeatureExtractionError, ContextError


# Page configuration
st.set_page_config(
    page_title="Business Check-Up",
    page_icon="📊",
    layout="wide"
)


def save_uploaded_file(uploaded_file) -> str:
    """
    Save uploaded file to temporary location.
    
    Returns path to saved file for use by AnalyticsEngine.
    """
    # Create temporary file
    suffix = Path(uploaded_file.name).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
        # Write uploaded file content to temp file
        tmp_file.write(uploaded_file.getvalue())
        return tmp_file.name


def format_insight_for_display(insight):
    """
    Format a single insight for friendly display.
    
    Maps backend Insight object to user-friendly presentation.
    """
    # Map severity to emoji and SMB-friendly labels
    severity_map = {
        Severity.CRITICAL: ("🔴", "Immediate attention"),
        Severity.HIGH: ("🟠", "Action needed soon"),
        Severity.MEDIUM: ("🟡", "Monitor"),
        Severity.LOW: ("🟢", "Informational"),
        Severity.INFO: ("ℹ️", "Informational"),
    }
    
    emoji, label = severity_map.get(insight.severity, ("•", insight.severity.value))
    
    return {
        "emoji": emoji,
        "severity_label": label,
        "title": insight.title,
        "description": insight.description,
        "recommendation": insight.recommendation,
    }


def display_insights_summary(insights):
    """
    Display a summary of insights grouped by what needs attention.
    
    Uses existing Insight objects - no business logic here.
    """
    if not insights:
        st.success("✅ **Great news!** No issues found. Your stock levels are healthy.")
        return
    
    # Group insights by severity (using existing Severity enum)
    critical = [i for i in insights if i.severity == Severity.CRITICAL]
    high = [i for i in insights if i.severity == Severity.HIGH]
    medium = [i for i in insights if i.severity == Severity.MEDIUM]
    low = [i for i in insights if i.severity == Severity.LOW]
    
    # "What Needs Attention" section
    st.header("🔍 What Needs Attention")
    
    if critical:
        st.error(f"**Immediate Attention ({len(critical)})**")
        st.write("These need action this week:")
        for insight in critical:
            formatted = format_insight_for_display(insight)
            with st.expander(f"{formatted['emoji']} {formatted['title']}", expanded=True):
                st.markdown(formatted['description'])
                if formatted['recommendation']:
                    st.info(f"**What to do:** {formatted['recommendation']}")
    
    if high:
        st.warning(f"**Action Needed Soon ({len(high)})**")
        st.write("These should be addressed in the next 1-2 weeks:")
        for insight in high:
            formatted = format_insight_for_display(insight)
            with st.expander(f"{formatted['emoji']} {formatted['title']}"):
                st.markdown(formatted['description'])
                if formatted['recommendation']:
                    st.info(f"**What to do:** {formatted['recommendation']}")
    
    if medium:
        st.info(f"**Monitor ({len(medium)})**")
        st.write("These should be watched but don't require immediate action:")
        for insight in medium:
            formatted = format_insight_for_display(insight)
            with st.expander(f"{formatted['emoji']} {formatted['title']}"):
                st.markdown(formatted['description'])
                if formatted['recommendation']:
                    st.write(f"**Suggestion:** {formatted['recommendation']}")
    
    if low:
        st.success(f"**Informational ({len(low)})**")
        for insight in low:
            formatted = format_insight_for_display(insight)
            with st.expander(f"{formatted['emoji']} {formatted['title']}"):
                st.markdown(formatted['description'])


def main():
    """Main Streamlit application."""
    
    # Header
    st.title("📊 Weekly Business Check-Up")
    st.markdown("Upload your business data to get plain-English insights and recommendations.")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("Settings")
        
        # Industry selection (uses existing BusinessContextFactory)
        available_industries = BusinessContextFactory.list_industries()
        selected_industry = st.selectbox(
            "Business Type",
            available_industries,
            index=0 if "retail" in available_industries else 0
        )
        
        # Business name input
        business_name = st.text_input(
            "Business Name",
            value="Your Business",
            help="This will appear in your report"
        )
    
    # Main content area
    st.header("Upload Your Data")
    
    st.write("""
    Upload a single CSV file containing both your inventory snapshot and sales history.
    This unified format ensures accurate inventory velocity calculations.
    """)
    
    # Single unified CSV upload
    uploaded_file = st.file_uploader(
        "Choose your business data CSV file",
        type=['csv'],
        help="Upload a unified CSV with inventory snapshot and sales data"
    )
    
    if uploaded_file is not None:
        # Show file info
        st.success(f"✅ File uploaded: {uploaded_file.name}")
        
        # Initialize engine components (using existing classes)
        try:
            # Create business context (existing factory)
            context = BusinessContextFactory.create(selected_industry)
            
            # Create check registry (existing registry)
            registry = CheckRegistry()
            
            # Create analytics engine (existing engine - no modifications)
            engine = AnalyticsEngine(context, registry)
            
            # Show what checks will run
            with st.expander("ℹ️ What will be analyzed"):
                checks = registry.get_applicable(context)
                st.write(f"Running {len(checks)} business checks:")
                for check in checks:
                    st.write(f"- {check.description}")
            
            # Run analysis button
            if st.button("🔍 Run Business Check-Up", type="primary", use_container_width=True):
                with st.spinner("Analyzing your business data..."):
                    try:
                        # Save uploaded file temporarily
                        temp_file_path = save_uploaded_file(uploaded_file)
                        
                        try:
                            # Call existing engine API (unified CSV format)
                            insights = engine.analyze(temp_file_path)
                            
                            # Display results
                            st.success(f"✅ Analysis complete! Found {len(insights)} insights.")
                            
                            # Summary statistics
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                critical_count = len([i for i in insights if i.severity == Severity.CRITICAL])
                                st.metric("Critical", critical_count)
                            with col2:
                                high_count = len([i for i in insights if i.severity == Severity.HIGH])
                                st.metric("High Priority", high_count)
                            with col3:
                                medium_count = len([i for i in insights if i.severity == Severity.MEDIUM])
                                st.metric("To Review", medium_count)
                            with col4:
                                st.metric("Total Insights", len(insights))
                            
                            st.divider()
                            
                            # Display insights in user-friendly format
                            display_insights_summary(insights)
                            
                            # Full report section (uses existing ReportGenerator)
                            st.divider()
                            st.header("📄 Full Report")
                            with st.expander("View complete report", expanded=False):
                                # Use existing report generator (no modifications)
                                full_report = engine.generate_report(insights, business_name)
                                st.text(full_report)
                                # Download button for report
                                st.download_button(
                                    label="📥 Download Report",
                                    data=full_report,
                                    file_name=f"business_checkup_{business_name.replace(' ', '_')}.txt",
                                    mime="text/plain"
                                )
                            
                        finally:
                            # Clean up temporary file
                            if os.path.exists(temp_file_path):
                                os.unlink(temp_file_path)
                    
                    except DataValidationError as e:
                        st.error(f"❌ Data Error: {str(e)}")
                        st.info("Please check that your CSV file has the correct columns and format.")
                    
                    except FeatureExtractionError as e:
                        st.error(f"❌ Processing Error: {str(e)}")
                        st.info("There was a problem processing your data. Please check the file format.")
                    
                    except Exception as e:
                        st.error(f"❌ Unexpected Error: {str(e)}")
                        st.info("Something went wrong. Please try again or contact support.")
        
        except ContextError as e:
            st.error(f"❌ Configuration Error: {str(e)}")
            st.info("Please select a valid business type from the sidebar.")
        
        except Exception as e:
            st.error(f"❌ Initialization Error: {str(e)}")
            st.info("There was a problem setting up the analysis system. Please try again.")
    
    else:
        # Instructions when no file uploaded
        st.info("👆 **Get started:** Upload a CSV file with your business data above.")
        
        with st.expander("📋 What data format do I need?"):
            st.write("""
            **Unified CSV Format**
            
            Your CSV file should contain both inventory snapshot and sales data in one file.
            
            **Required Columns:**
            - `as_of_date`: Date of your inventory snapshot (YYYY-MM-DD)
            - `product_id`: Unique identifier for each product
            - `product_name`: Name of the product
            - `price`: Product price
            - `starting_quantity`: Stock quantity as of the snapshot date
            - `date`: Sales date (YYYY-MM-DD) - can repeat per product
            - `units_sold`: Units sold on that date - can repeat per product
            
            **How it works:**
            - **Inventory rows**: One row per product with `starting_quantity` filled in
            - **Sales rows**: Multiple rows per product with `date` and `units_sold` filled in
            - Sales dates should be **after** your `as_of_date` (inventory snapshot date)
            
            **Example CSV:**
            ```
            as_of_date,product_id,product_name,price,starting_quantity,date,units_sold
            2024-12-01,P001,Widget A,10.50,150,,
            2024-12-01,P001,Widget A,10.50,,2024-12-02,3
            2024-12-01,P001,Widget A,10.50,,2024-12-03,5
            2024-12-01,P002,Widget B,25.00,5,,
            2024-12-01,P002,Widget B,25.00,,2024-12-02,1
            ```
            
            **Why this format?**
            
            This unified format ensures the system knows exactly when your inventory snapshot was taken
            and only uses sales that occurred after that date. This gives accurate inventory velocity
            calculations for precise stock-out predictions.
            
            **Missing sales data?**
            
            If you don't include sales rows, the system will use industry estimates. This reduces
            accuracy but still provides useful insights. The system will clearly indicate when
            estimates are being used.
            """)
        
        with st.expander("❓ How does this work?"):
            st.write("""
            1. **Upload your unified CSV** - Contains inventory snapshot and sales history in one file
            2. **Temporal alignment** - System uses inventory as of a specific date, and only counts sales after that date
            3. **Calculate velocity** - Determines how fast products are selling based on actual sales data
            4. **Days-of-stock** - Calculates how many days of stock remain at current sales rates
            5. **Get insights** - Plain-English insights about products that may run out
            6. **Take action** - Focus on products at risk of running out
            
            **Key points:**
            - Inventory is captured as of a specific date (`as_of_date`)
            - Sales rows represent activity after that date
            - Missing sales data reduces confidence (not trust) - system clearly indicates when estimates are used
            - All analysis uses deterministic business rules - no AI guessing
            """)
    
    # Footer
    st.divider()
    st.caption("Business Analyst System - Providing clear, actionable insights for small businesses")


if __name__ == "__main__":
    main()

