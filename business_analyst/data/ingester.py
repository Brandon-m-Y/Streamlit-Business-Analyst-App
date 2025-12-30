"""Data ingestion interface and implementations."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
import pandas as pd
from pathlib import Path

from business_analyst.core.exceptions import DataValidationError


class DataIngester(ABC):
    """Abstract base class for data ingestion."""
    
    @abstractmethod
    def ingest(self, source: str) -> pd.DataFrame:
        """
        Ingest data from a source.
        
        Args:
            source: Path to data file or API endpoint
            
        Returns:
            DataFrame containing the raw data
            
        Raises:
            DataValidationError: If ingestion fails
        """
        pass


class CSVIngester(DataIngester):
    """Ingests data from CSV files."""
    
    def ingest(self, source: str) -> pd.DataFrame:
        """Ingest data from a CSV file."""
        try:
            path = Path(source)
            if not path.exists():
                raise DataValidationError(f"File not found: {source}")
            
            df = pd.read_csv(source)
            if df.empty:
                raise DataValidationError(f"CSV file is empty: {source}")
            
            return df
        except pd.errors.EmptyDataError:
            raise DataValidationError(f"CSV file is empty: {source}")
        except Exception as e:
            raise DataValidationError(f"Failed to ingest CSV: {str(e)}")


class APIIngester(DataIngester):
    """Ingests data from API endpoints (placeholder for future implementation)."""
    
    def __init__(self, api_client):
        """
        Initialize API ingester.
        
        Args:
            api_client: Client for making API requests
        """
        self.api_client = api_client
    
    def ingest(self, source: str) -> pd.DataFrame:
        """Ingest data from an API endpoint."""
        # Placeholder for future implementation
        raise NotImplementedError("API ingestion not yet implemented")

