"""
Engagement Intelligence Module for Social Media Analytics
Handles advanced engagement metrics including sentiment, contextual engagement, and velocity
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from textblob import TextBlob

class EngagementIntelligence:
    def __init__(self):
        self.sentiment_analyzer = TextBlob
        
    def calculate_sentiment_engagement(self, content_data: pd.DataFrame) -> Dict:
        """
        Calculate sentiment-based engagement metrics
        
        Args:
            content_data: DataFrame containing content and engagement data
            
        Returns:
            Dict containing sentiment engagement metrics
        """
        if 'text' not in content_data.columns:
            return {'error': 'Text content not found in data'}
            
        # Calculate sentiment scores
        content_data['sentiment'] = content_data['text'].apply(
            lambda x: self.sentiment_analyzer(str(x)).sentiment.polarity
        )
        
        # Calculate engagement weighted by sentiment
        sentiment_engagement = {
            'positive_engagement': content_data[content_data['sentiment'] > 0]['engagement'].sum(),
            'neutral_engagement': content_data[abs(content_data['sentiment']) < 0.1]['engagement'].sum(),
            'negative_engagement': content_data[content_data['sentiment'] < 0]['engagement'].sum(),
            'sentiment_score': content_data['sentiment'].mean(),
            'engagement_sentiment_ratio': (
                content_data[content_data['sentiment'] > 0]['engagement'].sum() /
                (content_data['engagement'].sum() or 1)
            )
        }
        
        return sentiment_engagement
        
    def calculate_contextual_engagement_rate(self, 
        content_data: pd.DataFrame,
        follower_count: int
    ) -> Dict:
        """
        Calculate Contextual Engagement Rate (CER)
        
        Args:
            content_data: DataFrame containing content and engagement data
            follower_count: Number of followers for normalization
            
        Returns:
            Dict containing CER metrics
        """
        if follower_count <= 0:
            return {'error': 'Invalid follower count'}
            
        # Calculate base engagement rate
        content_data['base_er'] = content_data['engagement'] / follower_count * 100
        
        # Calculate time-weighted engagement
        current_time = datetime.now()
        content_data['time_weight'] = content_data['timestamp'].apply(
            lambda x: 1 / (1 + (current_time - x).total_seconds() / 86400)  # 24h decay
        )
        
        # Calculate CER
        cer_metrics = {
            'avg_cer': (content_data['base_er'] * content_data['time_weight']).mean(),
            'max_cer': content_data['base_er'].max(),
            'recent_cer': content_data.nlargest(5, 'timestamp')['base_er'].mean(),
            'engagement_consistency': content_data['base_er'].std()
        }
        
        return cer_metrics
        
    def calculate_engagement_velocity(self, 
        content_data: pd.DataFrame,
        time_window: str = '24h'
    ) -> Dict:
        """
        Calculate engagement velocity metrics
        
        Args:
            content_data: DataFrame containing content and engagement data
            time_window: Time window for velocity calculation
            
        Returns:
            Dict containing velocity metrics
        """
        # Convert time window to timedelta
        window_map = {
            '1h': timedelta(hours=1),
            '24h': timedelta(hours=24),
            '7d': timedelta(days=7),
            '30d': timedelta(days=30)
        }
        window = window_map.get(time_window, window_map['24h'])
        
        # Calculate engagement changes over time
        current_time = datetime.now()
        recent_mask = (current_time - content_data['timestamp']) <= window
        recent_data = content_data[recent_mask]
        
        if len(recent_data) < 2:
            return {'error': 'Insufficient data for velocity calculation'}
            
        # Calculate velocity metrics
        velocity_metrics = {
            'engagement_rate_change': (
                recent_data['engagement'].diff().mean() / 
                (recent_data['timestamp'].diff().dt.total_seconds() / 3600)  # per hour
            ),
            'acceleration': recent_data['engagement'].diff().diff().mean(),
            'peak_velocity': recent_data['engagement'].diff().max(),
            'velocity_consistency': recent_data['engagement'].diff().std()
        }
        
        return velocity_metrics
        
    def get_engagement_intelligence_summary(self,
        content_data: pd.DataFrame,
        follower_count: int,
        time_window: str = '24h'
    ) -> Dict:
        """
        Get comprehensive engagement intelligence summary
        
        Args:
            content_data: DataFrame containing content and engagement data
            follower_count: Number of followers
            time_window: Time window for velocity calculation
            
        Returns:
            Dict containing all engagement intelligence metrics
        """
        return {
            'sentiment_engagement': self.calculate_sentiment_engagement(content_data),
            'contextual_engagement': self.calculate_contextual_engagement_rate(
                content_data, follower_count
            ),
            'engagement_velocity': self.calculate_engagement_velocity(
                content_data, time_window
            )
        }
