"""
Advanced Metrics Analyzer Module
Handles complex social media metrics including engagement intelligence, content analysis, and predictive metrics
"""

from typing import Dict, List, Optional, Union
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from textblob import TextBlob
from sklearn.metrics import mean_squared_error
from scipy import stats

class MetricsAnalyzer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def calculate_sentiment_engagement(self, content_data: pd.DataFrame) -> Dict[str, float]:
        """Calculate engagement metrics weighted by sentiment"""
        try:
            def get_sentiment(text):
                return TextBlob(str(text)).sentiment.polarity

            content_data['sentiment'] = content_data['text'].apply(get_sentiment)
            
            sentiment_metrics = {
                'positive_engagement': content_data[content_data['sentiment'] > 0]['engagement_rate'].mean(),
                'neutral_engagement': content_data[
                    (content_data['sentiment'] >= -0.1) & 
                    (content_data['sentiment'] <= 0.1)
                ]['engagement_rate'].mean(),
                'negative_engagement': content_data[content_data['sentiment'] < 0]['engagement_rate'].mean()
            }
            return sentiment_metrics
        except Exception as e:
            self.logger.error(f"Error calculating sentiment engagement: {str(e)}")
            return {}

    def calculate_contextual_engagement_rate(
        self, 
        content_data: pd.DataFrame,
        audience_segments: Dict[str, List]
    ) -> Dict[str, float]:
        """Calculate Contextual Engagement Rate (CER) based on content type and audience"""
        try:
            cer_metrics = {}
            
            for content_type in content_data['content_type'].unique():
                type_data = content_data[content_data['content_type'] == content_type]
                
                # Weight by time of day
                type_data['time_weight'] = type_data['posted_at'].dt.hour.apply(
                    lambda x: 1.5 if 8 <= x <= 22 else 1.0
                )
                
                # Calculate weighted engagement
                weighted_engagement = (
                    type_data['engagement_count'] * 
                    type_data['time_weight'] * 
                    type_data['audience_reach']
                ).sum() / type_data['audience_reach'].sum()
                
                cer_metrics[content_type] = weighted_engagement
                
            return cer_metrics
        except Exception as e:
            self.logger.error(f"Error calculating CER: {str(e)}")
            return {}

    def calculate_engagement_velocity(
        self, 
        content_data: pd.DataFrame,
        time_window: str = 'hour'
    ) -> pd.DataFrame:
        """Calculate engagement velocity over time"""
        try:
            content_data = content_data.copy()
            content_data['timestamp'] = pd.to_datetime(content_data['engagement_timestamp'])
            
            if time_window == 'hour':
                grouped = content_data.groupby(pd.Grouper(key='timestamp', freq='H'))
            else:  # day
                grouped = content_data.groupby(pd.Grouper(key='timestamp', freq='D'))
                
            velocity_data = grouped.agg({
                'engagement_count': 'sum',
                'content_id': 'count'
            }).reset_index()
            
            velocity_data['engagement_velocity'] = (
                velocity_data['engagement_count'] / 
                velocity_data['content_id']
            )
            
            return velocity_data
        except Exception as e:
            self.logger.error(f"Error calculating engagement velocity: {str(e)}")
            return pd.DataFrame()

    def analyze_content_journey(
        self, 
        user_interactions: pd.DataFrame
    ) -> Dict[str, List[Dict]]:
        """Analyze user content consumption patterns"""
        try:
            journeys = {}
            
            for user_id in user_interactions['user_id'].unique():
                user_data = user_interactions[
                    user_interactions['user_id'] == user_id
                ].sort_values('timestamp')
                
                journey = []
                for _, interaction in user_data.iterrows():
                    journey.append({
                        'content_type': interaction['content_type'],
                        'timestamp': interaction['timestamp'],
                        'engagement_type': interaction['engagement_type']
                    })
                    
                journeys[user_id] = journey
                
            return journeys
        except Exception as e:
            self.logger.error(f"Error analyzing content journey: {str(e)}")
            return {}

    def calculate_virality_coefficient(
        self, 
        content_data: pd.DataFrame,
        window_days: int = 7
    ) -> float:
        """Calculate virality coefficient (K-factor)"""
        try:
            # Calculate new followers gained per engaged user
            total_engaged_users = content_data['unique_engagers'].sum()
            new_followers = content_data['new_followers'].sum()
            
            if total_engaged_users == 0:
                return 0.0
                
            k_factor = (new_followers / total_engaged_users) * \
                      (content_data['engagement_rate'].mean())
                      
            return k_factor
        except Exception as e:
            self.logger.error(f"Error calculating virality coefficient: {str(e)}")
            return 0.0

    def predict_follower_decay(
        self, 
        historical_data: pd.DataFrame,
        prediction_days: int = 30
    ) -> Dict[str, Union[float, List[float]]]:
        """Predict follower decay rate and future unfollows"""
        try:
            historical_data = historical_data.sort_values('date')
            
            # Calculate daily decay rate
            daily_decay = (
                historical_data['unfollows'] / 
                historical_data['total_followers']
            ).mean()
            
            # Predict future unfollows
            current_followers = historical_data['total_followers'].iloc[-1]
            predicted_unfollows = []
            
            for day in range(prediction_days):
                predicted_unfollow = current_followers * daily_decay
                predicted_unfollows.append(predicted_unfollow)
                current_followers -= predicted_unfollow
                
            return {
                'decay_rate': daily_decay,
                'predicted_unfollows': predicted_unfollows,
                'retention_rate': 1 - daily_decay
            }
        except Exception as e:
            self.logger.error(f"Error predicting follower decay: {str(e)}")
            return {}

    def analyze_video_metrics(
        self, 
        video_data: pd.DataFrame
    ) -> Dict[str, Dict[str, float]]:
        """Analyze detailed video performance metrics"""
        try:
            metrics = {}
            
            # Calculate watch patterns
            metrics['watch_patterns'] = {
                'avg_watch_duration': video_data['watch_time'].mean(),
                'completion_rate': (
                    video_data['completed_views'] / 
                    video_data['total_views']
                ).mean(),
                'rewatch_rate': (
                    video_data['rewatches'] / 
                    video_data['total_views']
                ).mean()
            }
            
            # Calculate viewer loyalty
            metrics['viewer_loyalty'] = {
                'returning_viewers': (
                    video_data['returning_viewers'] / 
                    video_data['unique_viewers']
                ).mean(),
                'subscriber_views': (
                    video_data['subscriber_views'] / 
                    video_data['total_views']
                ).mean()
            }
            
            return metrics
        except Exception as e:
            self.logger.error(f"Error analyzing video metrics: {str(e)}")
            return {}

    def analyze_platform_specific_metrics(
        self, 
        platform: str,
        content_data: pd.DataFrame
    ) -> Dict[str, float]:
        """Analyze platform-specific engagement metrics"""
        try:
            metrics = {}
            
            if platform == 'tiktok':
                metrics = {
                    'loop_rate': (
                        content_data['total_plays'] / 
                        content_data['unique_viewers']
                    ).mean(),
                    'completion_rate': (
                        content_data['completed_views'] / 
                        content_data['total_views']
                    ).mean(),
                    'share_rate': (
                        content_data['shares'] / 
                        content_data['views']
                    ).mean()
                }
            elif platform == 'instagram':
                metrics = {
                    'carousel_engagement': self._analyze_carousel_engagement(content_data),
                    'story_completion': (
                        content_data['story_completions'] / 
                        content_data['story_impressions']
                    ).mean(),
                    'swipe_up_rate': (
                        content_data['swipe_ups'] / 
                        content_data['story_impressions']
                    ).mean()
                }
            elif platform == 'youtube':
                metrics = {
                    'avg_view_duration': content_data['watch_time'].mean(),
                    'retention_rate': (
                        content_data['average_percentage_viewed']
                    ).mean(),
                    'subscriber_conversion': (
                        content_data['new_subscribers'] / 
                        content_data['unique_viewers']
                    ).mean()
                }
                
            return metrics
        except Exception as e:
            self.logger.error(f"Error analyzing platform metrics: {str(e)}")
            return {}

    def _analyze_carousel_engagement(self, content_data: pd.DataFrame) -> Dict[str, float]:
        """Analyze Instagram carousel post engagement"""
        carousel_data = content_data[content_data['type'] == 'carousel']
        
        metrics = {
            'avg_slides_viewed': carousel_data['avg_slides_viewed'].mean(),
            'last_slide_reached': (
                carousel_data['last_slide_reached'] / 
                carousel_data['impressions']
            ).mean(),
            'optimal_slide_count': carousel_data.groupby('slide_count')['engagement_rate'].mean().idxmax()
        }
        
        return metrics

    def calculate_revenue_metrics(
        self, 
        content_data: pd.DataFrame,
        conversion_data: pd.DataFrame
    ) -> Dict[str, float]:
        """Calculate revenue and conversion metrics"""
        try:
            metrics = {
                'avg_revenue_per_post': content_data['revenue'].mean(),
                'conversion_rate': (
                    conversion_data['conversions'] / 
                    conversion_data['impressions']
                ).mean(),
                'revenue_per_impression': (
                    content_data['revenue'].sum() / 
                    content_data['impressions'].sum()
                ),
                'roi': (
                    (content_data['revenue'].sum() - content_data['cost'].sum()) / 
                    content_data['cost'].sum()
                ) * 100
            }
            
            return metrics
        except Exception as e:
            self.logger.error(f"Error calculating revenue metrics: {str(e)}")
            return {}
