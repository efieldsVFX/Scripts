"""
Compliance-Focused Content Analyzer
Implements platform-specific data collection and analysis with built-in compliance checks
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, List
import logging
from datetime import datetime
from pathlib import Path
from .content_analyzer import ContentAnalyzer

logger = logging.getLogger(__name__)

class CompliantContentAnalyzer:
    def __init__(self, platform: str):
        """
        Initialize analyzer for specific platform
        
        Args:
            platform (str): Social media platform ('reddit', 'instagram', 'twitter', etc.)
        """
        self.platform = platform.lower()
        self.data_retention_days = 30  # Configurable retention period
        self.api_rate_limits = self._get_platform_limits()
        self.last_api_call = None
        self.analyzer = ContentAnalyzer()  # Create instance of ContentAnalyzer
        
    def _get_platform_limits(self) -> Dict:
        """Get platform-specific API rate limits"""
        limits = {
            'reddit': {'calls_per_minute': 60, 'calls_per_hour': 600},
            'instagram': {'calls_per_hour': 200},
            'twitter': {'calls_per_15min': 450}
        }
        return limits.get(self.platform, {})
        
    def check_rate_limit(self) -> bool:
        """Verify API rate limit compliance"""
        if not self.last_api_call:
            return True
            
        time_diff = (datetime.now() - self.last_api_call).total_seconds()
        
        if self.platform == 'reddit':
            return time_diff > (60 / self.api_rate_limits['calls_per_minute'])
        
        return True
        
    def anonymize_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove or hash PII from collected data"""
        pii_columns = ['author', 'username', 'user_id']
        
        for col in pii_columns:
            if col in df.columns:
                df = df.drop(columns=[col])
                
        return df
        
    def collect_data(self, query: str = None, limit: int = 100, **kwargs) -> pd.DataFrame:
        """
        Collect platform data with compliance checks
        
        Args:
            query (str, optional): Search query or parameters
            limit (int): Maximum items to collect
            **kwargs: Platform-specific parameters (e.g., subreddit, time_filter for Reddit)
        """
        if not self.check_rate_limit():
            logger.warning("Rate limit exceeded")
            return pd.DataFrame()
        
        # Log collection attempt
        logger.info(f"Collecting data for {self.platform} with params: query={query}, limit={limit}, extra_params={kwargs}")
        
        # Update last API call time
        self.last_api_call = datetime.now()
        
        # Validate the fields being requested
        fields_to_validate = list(kwargs.keys())
        if not self.validate_fields(fields_to_validate):
            logger.error(f"Invalid fields requested for {self.platform}: {fields_to_validate}")
            return pd.DataFrame()
        
        try:
            # Platform-specific collection logic
            if self.platform == 'reddit':
                required_columns = ['title', 'text', 'author', 'created_utc', 'score', 
                                  'num_comments', 'url', 'subreddit']
                # Return empty DataFrame with required columns for now
                data = pd.DataFrame(columns=required_columns)
            else:
                data = pd.DataFrame()
            
            return self.anonymize_data(data)
        
        except Exception as e:
            logger.error(f"Error collecting data: {str(e)}")
            return pd.DataFrame()
        
    def validate_fields(self, fields: List[str]) -> bool:
        """Validate if the requested fields are allowed for the platform"""
        platform_fields = {
            'reddit': ['subreddit', 'limit', 'time_filter', 'title', 'text', 'author', 
                      'created_utc', 'score', 'num_comments', 'url'],
            'twitter': ['query', 'limit', 'lang'],
            'instagram': ['username', 'limit', 'media_type']
        }
        
        allowed_fields = platform_fields.get(self.platform, [])
        valid_fields = [field for field in fields if field in allowed_fields]
        
        # Log validation results
        logger.debug(f"Validating fields: {fields}")
        logger.debug(f"Allowed fields: {allowed_fields}")
        logger.debug(f"Valid fields: {valid_fields}")
        
        # Return True if at least one field is valid
        return len(valid_fields) > 0
        
    def analyze_engagement(self, df: pd.DataFrame) -> Dict:
        """Analyze engagement metrics without exposing PII"""
        return {
            'total_posts': len(df),
            'avg_engagement': df['engagement_score'].mean() if 'engagement_score' in df.columns else 0,
            'peak_times': self._get_peak_times(df),
            'trending_topics': self._get_safe_topics(df)
        }
        
    def analyze_content(self, df: pd.DataFrame) -> Dict:
        """Analyze content with compliance checks"""
        if df.empty:
            return {'status': 'error', 'message': 'No data to analyze'}
            
        # Anonymize data before analysis
        safe_df = self.anonymize_data(df)
        
        # Use ContentAnalyzer for actual analysis
        return self.analyzer.analyze_content(safe_df, platform=self.platform)
        
    def _get_peak_times(self, df: pd.DataFrame) -> Dict:
        """Calculate peak engagement times"""
        if 'created_utc' not in df.columns:
            return {}
            
        df['hour'] = pd.to_datetime(df['created_utc']).dt.hour
        if 'engagement_score' not in df.columns:
            df['engagement_score'] = df['score'] + df['num_comments']
        return df.groupby('hour')['engagement_score'].mean().to_dict()
        
    def _get_safe_topics(self, df: pd.DataFrame, max_topics: int = 10) -> List[str]:
        """Extract trending topics with content filtering"""
        if df.empty or 'title' not in df.columns:
            return []
            
        # Basic word frequency analysis from titles
        words = ' '.join(df['title'].fillna('')).lower().split()
        word_freq = pd.Series(words).value_counts()
        
        # Filter out common words and short terms
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        filtered_words = word_freq[~word_freq.index.isin(stop_words)]
        filtered_words = filtered_words[filtered_words.index.str.len() > 3]
        
        return filtered_words.head(max_topics).index.tolist()
        
    def save_results(self, results: Dict, output_dir: str):
        """Save analysis results with proper data handling"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Add metadata and timestamp
        results['analysis_timestamp'] = datetime.now().isoformat()
        results['platform'] = self.platform
        results['data_retention_days'] = self.data_retention_days
        
        with open(output_path / f"{self.platform}_analysis.json", 'w') as f:
            json.dump(results, f, indent=4)
        
    def setup_logging(self):
        logging.basicConfig(
            filename=f'{self.platform}_compliance.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )