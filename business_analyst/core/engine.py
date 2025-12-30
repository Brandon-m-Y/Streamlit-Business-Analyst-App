"""Main analytics engine orchestrator."""

from typing import List
from business_analyst.core.insight import Insight
from business_analyst.core.exceptions import DataValidationError, FeatureExtractionError
from business_analyst.data.ingester import DataIngester, CSVIngester
from business_analyst.data.validator import DataValidator
from business_analyst.data.extractor import FeatureExtractor
from business_analyst.context.base import BusinessContext
from business_analyst.checks.registry import CheckRegistry
from business_analyst.insights.prioritizer import InsightPrioritizer
from business_analyst.insights.explainer import ExplanationGenerator
from business_analyst.delivery.report import ReportGenerator


class AnalyticsEngine:
    """
    Main orchestrator for the business analyst system.
    
    Coordinates data ingestion, validation, feature extraction,
    check execution, insight prioritization, and report generation.
    """
    
    def __init__(
        self,
        context: BusinessContext,
        check_registry: CheckRegistry,
        ingester: DataIngester = None,
        explainer: ExplanationGenerator = None
    ):
        """
        Initialize analytics engine.
        
        Args:
            context: Business context for industry-specific rules
            check_registry: Registry of analyst checks
            ingester: Data ingester (defaults to CSVIngester)
            explainer: Explanation generator (defaults to template-based)
        """
        self.context = context
        self.check_registry = check_registry
        self.ingester = ingester or CSVIngester()
        self.explainer = explainer or ExplanationGenerator()
        
        # Initialize components
        self.validator = DataValidator(
            required_columns=context.get_required_columns(),
            column_types=context.get_column_types()
        )
        self.extractor = FeatureExtractor()
        self.prioritizer = InsightPrioritizer()
        self.report_generator = ReportGenerator(
            self.explainer,
            self.prioritizer
        )
    
    def analyze(
        self,
        data_source: str,
        sales_data_source: str = None
    ) -> List[Insight]:
        """
        Analyze data and generate insights.
        
        Supports two modes:
        1. Unified CSV: Single file with inventory snapshot + sales (preferred)
        2. Separate files: Inventory + optional sales (legacy support)
        
        Args:
            data_source: Path to unified CSV file OR inventory snapshot CSV file
            sales_data_source: Optional path to sales summary CSV file (legacy mode only)
            
        Returns:
            List of insights
            
        Raises:
            DataValidationError: If data validation fails
            FeatureExtractionError: If feature extraction fails
        """
        # Step 1: Ingest data
        raw_data = self.ingester.ingest(data_source)
        
        # Step 2: Validate data (will validate based on format detected)
        self.validator.validate(raw_data)
        
        # Step 3: Ingest sales data if provided (legacy mode only)
        sales_data = None
        if sales_data_source:
            try:
                sales_data = self.ingester.ingest(sales_data_source)
            except Exception as e:
                # Sales data ingestion failure is not fatal - we'll note it in insights
                print(f"Warning: Could not load sales data: {str(e)}")
        
        # Step 4: Extract features (extractor handles unified vs separate formats)
        features = self.extractor.extract(raw_data, sales_data)
        
        # Step 5: Execute all applicable checks
        insights = []
        applicable_checks = self.check_registry.get_applicable(self.context)
        
        for check in applicable_checks:
            try:
                check_insights = check.execute(features, self.context)
                insights.extend(check_insights)
            except Exception as e:
                # Log error but continue with other checks
                print(f"Warning: Check '{check.name}' failed: {str(e)}")
                continue
        
        # Step 6: Prioritize insights
        prioritized_insights = self.prioritizer.prioritize(insights)
        
        return prioritized_insights
    
    def generate_report(
        self,
        insights: List[Insight],
        business_name: str = "Business"
    ) -> str:
        """
        Generate a formatted report from insights.
        
        Args:
            insights: List of insights
            business_name: Name of the business
            
        Returns:
            Formatted report string
        """
        return self.report_generator.generate(insights, business_name)
    
    def analyze_and_report(
        self,
        data_source: str,
        business_name: str = "Business",
        sales_data_source: str = None
    ) -> str:
        """
        Analyze data and generate a complete report.
        
        Convenience method that combines analyze() and generate_report().
        
        Args:
            data_source: Path to inventory snapshot CSV file
            business_name: Name of the business
            sales_data_source: Optional path to sales summary CSV file
            
        Returns:
            Formatted report string
        """
        insights = self.analyze(data_source, sales_data_source)
        return self.generate_report(insights, business_name)

