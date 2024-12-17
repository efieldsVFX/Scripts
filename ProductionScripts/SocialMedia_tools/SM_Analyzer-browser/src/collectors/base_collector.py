"""
Base Collector Module
Provides base functionality for social media data collection
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import pandas as pd
import logging
from datetime import datetime, timedelta

class BaseCollector(ABC):
    def __init__(self, api_key: str, api_secret: str = None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.logger = logging.getLogger(self.__class__.__name__)
        
    @abstractmethod
    def authenticate(self) -> bool:
        """Authenticate with the platform API"""
        pass
        
    @abstractmethod
    def collect_profile_data(self, profile_id: str) -> pd.DataFrame:
        """Collect profile/account data"""
        pass
        
    @abstractmethod
    def collect_content_data(self, profile_id: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Collect content/posts data"""
        pass
        
    @abstractmethod
    def collect_engagement_data(self, content_ids: List[str]) -> pd.DataFrame:
        """Collect engagement metrics for content"""
        pass
        
    @abstractmethod
    def collect_audience_data(self, profile_id: str) -> pd.DataFrame:
        """Collect audience demographics and insights"""
        pass
        
    def handle_rate_limit(self, wait_time: int = 60):
        """Handle rate limiting by implementing exponential backoff"""
        self.logger.warning(f"Rate limit hit. Waiting {wait_time} seconds...")
        time.sleep(wait_time)
        
    def validate_dates(self, start_date: datetime, end_date: datetime):
        """Validate date ranges for data collection"""
        if start_date > end_date:
            raise ValueError("Start date must be before end date")
        if end_date > datetime.now():
            raise ValueError("End date cannot be in the future")
            
    def format_response(self, data: Dict) -> pd.DataFrame:
        """Convert API response to pandas DataFrame"""
        try:
            df = pd.DataFrame(data)
            return df
        except Exception as e:
            self.logger.error(f"Error formatting response: {str(e)}")
            raise
