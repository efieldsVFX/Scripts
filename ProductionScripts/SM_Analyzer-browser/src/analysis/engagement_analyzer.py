"""
Engagement Intelligence Module
Handles sentiment analysis, contextual engagement rate, and engagement velocity tracking
"""

from typing import Dict, List, Optional
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from textblob import TextBlob
import logging

# Initialize logger
logger = logging.getLogger(__name__)

class EngagementAnalyzer:
    def __init__(self):
        self.engagement_weights = {
            'like': 1,
            'comment': 2,
            'share': 3,
            'save': 4
        }
        
    def analyze_sentiment_engagement(self, data: pd.DataFrame) -> Dict:
        """
        Score engagement by sentiment (positive/neutral/negative)
        
        Args:
            data: DataFrame with columns ['content_id', 'text', 'engagement_type']
            
        Returns:
            Dict containing sentiment scores and engagement metrics
        """
        try:
            logger.debug(f"Starting sentiment analysis with columns: {data.columns.tolist()}")
            def get_sentiment(text):
                return TextBlob(str(text)).sentiment.polarity
                
            data['sentiment_score'] = data['text'].apply(get_sentiment)
            data['sentiment_category'] = pd.cut(
                data['sentiment_score'],
                bins=[-1, -0.1, 0.1, 1],
                labels=['negative', 'neutral', 'positive']
            )
            
            sentiment_metrics = {
                'sentiment_distribution': data['sentiment_category'].value_counts().to_dict(),
                'avg_sentiment_score': data['sentiment_score'].mean(),
                'engagement_by_sentiment': data.groupby(['sentiment_category', 'engagement_type']).size().unstack().fillna(0).to_dict()
            }
            logger.debug(f"Completed sentiment analysis with metrics: {list(sentiment_metrics.keys())}")
            return sentiment_metrics
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {str(e)}\nData columns: {data.columns.tolist() if isinstance(data, pd.DataFrame) else 'Invalid data format'}")
            return {}
        
    def calculate_contextual_engagement_rate(self, data: pd.DataFrame) -> Dict:
        """
        Calculate engagement rate weighted by content type, time, and audience segment
        
        Args:
            data: DataFrame with columns ['content_id', 'content_type', 'timestamp', 'audience_segment', 'engagement_type']
            
        Returns:
            Dict containing contextual engagement metrics
        """
        try:
            logger.debug(f"Starting contextual engagement rate calculation with columns: {data.columns.tolist()}")
            data['engagement_weight'] = data['engagement_type'].map(self.engagement_weights)
            data['timestamp'] = pd.to_datetime(data['timestamp'])
            
            cer_metrics = {
                'engagement_by_type': data.groupby('content_type')['engagement_weight'].mean().to_dict(),
                'engagement_by_segment': data.groupby('audience_segment')['engagement_weight'].mean().to_dict(),
                'hourly_engagement': data.groupby(data['timestamp'].dt.hour)['engagement_weight'].mean().to_dict()
            }
            logger.debug(f"Completed contextual engagement rate calculation with metrics: {list(cer_metrics.keys())}")
            return cer_metrics
        except Exception as e:
            logger.error(f"Error in contextual engagement rate calculation: {str(e)}\nData columns: {data.columns.tolist() if isinstance(data, pd.DataFrame) else 'Invalid data format'}")
            return {}
        
    def track_engagement_velocity(self, data: pd.DataFrame) -> Dict:
        """
        Measure engagement traction over time
        
        Args:
            data: DataFrame with columns ['content_id', 'timestamp', 'engagement_type']
            
        Returns:
            Dict containing velocity metrics
        """
        try:
            logger.debug(f"Starting engagement velocity tracking with columns: {data.columns.tolist()}")
            data['timestamp'] = pd.to_datetime(data['timestamp'])
            data['engagement_weight'] = data['engagement_type'].map(self.engagement_weights)
            
            # Calculate engagement per hour
            hourly_engagement = data.set_index('timestamp').resample('H')['engagement_weight'].sum()
            
            velocity_metrics = {
                'hourly_velocity': hourly_engagement.diff().to_dict(),
                'acceleration': hourly_engagement.diff().diff().to_dict(),
                'peak_velocity': hourly_engagement.diff().max(),
                'avg_velocity': hourly_engagement.diff().mean()
            }
            logger.debug(f"Completed engagement velocity tracking with metrics: {list(velocity_metrics.keys())}")
            return velocity_metrics
        except Exception as e:
            logger.error(f"Error in engagement velocity tracking: {str(e)}\nData columns: {data.columns.tolist() if isinstance(data, pd.DataFrame) else 'Invalid data format'}")
            return {}
        
    def get_engagement_summary(self, data: pd.DataFrame) -> Dict:
        """
        Generate comprehensive engagement summary
        
        Args:
            data: DataFrame containing all engagement data
            
        Returns:
            Dict containing overall engagement metrics
        """
        try:
            logger.debug(f"Starting engagement summary generation with columns: {data.columns.tolist()}")
            sentiment_metrics = self.analyze_sentiment_engagement(data)
            cer_metrics = self.calculate_contextual_engagement_rate(data)
            velocity_metrics = self.track_engagement_velocity(data)
            
            logger.debug(f"Completed engagement summary generation with metrics: {list(sentiment_metrics.keys()) + list(cer_metrics.keys()) + list(velocity_metrics.keys())}")
            return {
                'sentiment_analysis': sentiment_metrics,
                'contextual_engagement': cer_metrics,
                'engagement_velocity': velocity_metrics
            }
        except Exception as e:
            logger.error(f"Error in engagement summary generation: {str(e)}\nData columns: {data.columns.tolist() if isinstance(data, pd.DataFrame) else 'Invalid data format'}")
            return {}
