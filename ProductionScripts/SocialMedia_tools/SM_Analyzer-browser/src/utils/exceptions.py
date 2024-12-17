class AnalysisError(Exception):
    """Base class for analysis exceptions"""
    pass

class InitializationError(AnalysisError):
    """Raised when component initialization fails"""
    pass

class DataCollectionError(AnalysisError):
    """Raised when data collection fails"""
    pass

class AnalysisCancelled(AnalysisError):
    """Raised when analysis is cancelled by user"""
    pass

class ComplianceError(AnalysisError):
    """Raised for compliance-related issues"""
    pass
