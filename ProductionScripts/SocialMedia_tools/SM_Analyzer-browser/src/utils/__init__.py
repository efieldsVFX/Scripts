import logging
from pathlib import Path

# Setup logging
logger = logging.getLogger('sm_analyzer')

# Model configuration
MODEL_CONFIG = {
    'sentiment': {
        'transformer': 'cardiffnlp/twitter-roberta-base-sentiment',
        'vader_lexicon': 'vader_lexicon',
        'default': 'transformer'  # which model to use by default
    }
}

# Load API configuration
API_CONFIG = {
    'reddit': {
        'client_id': '',
        'client_secret': '',
        'user_agent': 'SM_Analyzer/1.0'
    },
    'instagram': {
        'access_token': '',
        'client_secret': ''
    },
    'twitter': {
        'api_key': '',
        'api_secret': ''
    }
}

# Import utility modules
from .paths import setup_analysis_folders
from .compliance_manager import ComplianceManager
from .brand_alignment import BrandAlignmentManager
from .network_manager import NetworkManager
from .exceptions import (
    AnalysisError,
    InitializationError,
    DataCollectionError,
    AnalysisCancelled,
    ComplianceError
)

__all__ = [
    'logger',
    'API_CONFIG',
    'MODEL_CONFIG',
    'setup_analysis_folders',
    'ComplianceManager',
    'BrandAlignmentManager',
    'NetworkManager',
    'AnalysisError',
    'InitializationError',
    'DataCollectionError',
    'AnalysisCancelled',
    'ComplianceError'
]
