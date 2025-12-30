"""Custom exceptions for the business analyst system."""


class BusinessAnalystError(Exception):
    """Base exception for all business analyst errors."""
    pass


class DataValidationError(BusinessAnalystError):
    """Raised when data validation fails."""
    pass


class FeatureExtractionError(BusinessAnalystError):
    """Raised when feature extraction fails."""
    pass


class CheckExecutionError(BusinessAnalystError):
    """Raised when an analyst check fails to execute."""
    pass


class ContextError(BusinessAnalystError):
    """Raised when business context operations fail."""
    pass

