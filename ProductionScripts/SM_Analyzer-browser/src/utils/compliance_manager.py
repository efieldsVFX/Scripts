"""
Compliance Manager
Handles data privacy, retention, and platform-specific compliance rules
"""

import pandas as pd
import numpy as np
from typing import Dict, List
import logging
import hashlib
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)

class ComplianceManager:
    def __init__(self):
        self.privacy_rules = {
            'pii_fields': ['username', 'email', 'phone', 'location'],
            'retention_period': 30,  # days
            'data_usage_purposes': ['analytics', 'trends', 'recommendations']
        }
        
        # Platform-specific compliance limits
        self.platform_limits = {
            'reddit': {
                'rate_limit': 60,  # requests per minute
                'allowed_fields': ['title', 'text', 'author', 'created_utc', 'score', 'num_comments', 'url', 'subreddit'],
                'max_posts': 1000,
                'max_comments': 2000
            },
            'twitter': {
                'rate_limit': 450,  # requests per 15 minutes
                'allowed_fields': ['text', 'user', 'created_at', 'retweet_count', 'favorite_count', 'hashtags'],
                'max_tweets': 3200
            },
            'instagram': {
                'rate_limit': 200,  # requests per hour
                'allowed_fields': ['caption', 'user', 'timestamp', 'like_count', 'comment_count', 'media_type'],
                'max_posts': 100
            }
        }
        
    def get_platform_limits(self, platform: str) -> Dict:
        """Get platform-specific API and data collection limits"""
        if platform.lower() not in self.platform_limits:
            logger.warning(f"No limits defined for platform: {platform}")
            return {
                'rate_limit': float('inf'),
                'allowed_fields': [],
                'max_posts': float('inf')
            }
        return self.platform_limits[platform.lower()]
        
    def validate_data_collection(self, platform: str, data_fields: List[str]) -> bool:
        """Validate data collection against platform policies"""
        platform_limits = self.get_platform_limits(platform)
        logger.debug(f"Validating fields: {data_fields}")
        logger.debug(f"Allowed fields: {platform_limits['allowed_fields']}")
        
        valid_fields = [field for field in data_fields if field in platform_limits['allowed_fields']]
        return len(valid_fields) > 0
    
    def anonymize_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Anonymize PII data"""
        df = data.copy()
        for field in self.privacy_rules['pii_fields']:
            if field in df.columns:
                df[field] = df[field].apply(self._hash_identifier)
        return df
    
    def validate_api_usage(self, platform: str, request_count: int) -> bool:
        """Check API rate limits compliance"""
        platform_limits = self.get_platform_limits(platform)
        return request_count <= platform_limits['rate_limit']
        
    def _hash_identifier(self, value: str) -> str:
        """Hash sensitive identifiers"""
        if pd.isna(value):
            return value
        return hashlib.sha256(str(value).encode()).hexdigest()[:12]
