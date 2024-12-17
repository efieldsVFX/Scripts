"""
Post Intelligence and Content Performance Analyzer
Handles post-level analytics, content journey tracking, and predictive performance metrics
"""

from typing import Dict, List, Optional, Union
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from textblob import TextBlob
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder

class PostAnalyzer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.label_encoder = LabelEncoder()
        self.performance_model = RandomForestRegressor(n_estimators=100)

    def analyze_post_intelligence(self, post_data: pd.DataFrame) -> Dict:
        """Analyze post-level metrics and creator influence"""
        try:
            intelligence = {
                'post_metrics': self._analyze_post_metrics(post_data),
                'creator_influence': self._calculate_creator_influence(post_data),
                'url_performance': self._analyze_url_performance(post_data),
                'hashtag_analytics': self._analyze_hashtag_performance(post_data)
            }
            return intelligence
        except Exception as e:
            self.logger.error(f"Error analyzing post intelligence: {str(e)}")
            return {}

    def analyze_content_journey(self, user_interactions: pd.DataFrame) -> Dict:
        """Track user content consumption patterns"""
        try:
            journey_metrics = {
                'content_flow': self._map_content_flow(user_interactions),
                'format_transitions': self._analyze_format_transitions(user_interactions),
                'engagement_sequence': self._analyze_engagement_sequence(user_interactions),
                'retention_patterns': self._analyze_retention_patterns(user_interactions)
            }
            return journey_metrics
        except Exception as e:
            self.logger.error(f"Error analyzing content journey: {str(e)}")
            return {}

    def predict_content_performance(self, content_data: pd.DataFrame) -> Dict:
        """Predict content performance using historical data"""
        try:
            predictions = {
                'engagement_forecast': self._forecast_engagement(content_data),
                'virality_potential': self._calculate_virality_potential(content_data),
                'audience_fit': self._calculate_audience_fit(content_data),
                'longevity_score': self._predict_content_longevity(content_data)
            }
            return predictions
        except Exception as e:
            self.logger.error(f"Error predicting content performance: {str(e)}")
            return {}

    def _analyze_post_metrics(self, post_data: pd.DataFrame) -> Dict:
        """Analyze basic post metrics"""
        try:
            metrics = {
                'content_type_distribution': post_data['content_type'].value_counts().to_dict(),
                'media_format_performance': self._analyze_format_performance(post_data),
                'posting_patterns': self._analyze_posting_patterns(post_data),
                'engagement_by_type': self._analyze_engagement_by_type(post_data)
            }
            return metrics
        except Exception as e:
            self.logger.error(f"Error analyzing post metrics: {str(e)}")
            return {}

    def _calculate_creator_influence(self, post_data: pd.DataFrame) -> Dict:
        """Calculate creator influence metrics"""
        try:
            influence = {
                'engagement_potential': self._calculate_engagement_potential(post_data),
                'authority_score': self._calculate_authority_score(post_data),
                'audience_reach': self._calculate_audience_reach(post_data),
                'content_consistency': self._analyze_content_consistency(post_data)
            }
            return influence
        except Exception as e:
            self.logger.error(f"Error calculating creator influence: {str(e)}")
            return {}

    def _analyze_url_performance(self, post_data: pd.DataFrame) -> Dict:
        """Analyze URL click-through performance"""
        try:
            url_metrics = {
                'click_through_rate': self._calculate_ctr(post_data),
                'traffic_sources': self._analyze_traffic_sources(post_data),
                'conversion_paths': self._analyze_conversion_paths(post_data),
                'url_engagement': self._analyze_url_engagement(post_data)
            }
            return url_metrics
        except Exception as e:
            self.logger.error(f"Error analyzing URL performance: {str(e)}")
            return {}

    def _analyze_hashtag_performance(self, post_data: pd.DataFrame) -> Dict:
        """Analyze hashtag reach and impact"""
        try:
            hashtag_metrics = {
                'reach_by_hashtag': self._calculate_hashtag_reach(post_data),
                'engagement_by_hashtag': self._calculate_hashtag_engagement(post_data),
                'trending_hashtags': self._identify_trending_hashtags(post_data),
                'hashtag_recommendations': self._generate_hashtag_recommendations(post_data)
            }
            return hashtag_metrics
        except Exception as e:
            self.logger.error(f"Error analyzing hashtag performance: {str(e)}")
            return {}

    def _map_content_flow(self, user_interactions: pd.DataFrame) -> List[Dict]:
        """Map user content consumption flow"""
        try:
            flows = []
            for user_id in user_interactions['user_id'].unique():
                user_flow = user_interactions[
                    user_interactions['user_id'] == user_id
                ].sort_values('timestamp')
                
                flow = {
                    'user_id': user_id,
                    'content_sequence': user_flow['content_type'].tolist(),
                    'engagement_sequence': user_flow['engagement_type'].tolist(),
                    'time_gaps': self._calculate_time_gaps(user_flow['timestamp'])
                }
                flows.append(flow)
            return flows
        except Exception as e:
            self.logger.error(f"Error mapping content flow: {str(e)}")
            return []

    def _analyze_format_transitions(self, user_interactions: pd.DataFrame) -> Dict:
        """Analyze transitions between content formats"""
        try:
            transitions = {}
            for user_id in user_interactions['user_id'].unique():
                user_flow = user_interactions[
                    user_interactions['user_id'] == user_id
                ].sort_values('timestamp')
                
                content_types = user_flow['content_type'].tolist()
                for i in range(len(content_types) - 1):
                    transition = f"{content_types[i]} → {content_types[i+1]}"
                    transitions[transition] = transitions.get(transition, 0) + 1
                    
            return transitions
        except Exception as e:
            self.logger.error(f"Error analyzing format transitions: {str(e)}")
            return {}

    def _predict_content_longevity(self, content_data: pd.DataFrame) -> Dict:
        """Predict how long content will remain relevant"""
        try:
            features = self._extract_content_features(content_data)
            
            # Train model on historical engagement decay
            historical_longevity = self._calculate_historical_longevity(content_data)
            self.performance_model.fit(features, historical_longevity)
            
            # Predict longevity for new content
            longevity_predictions = self.performance_model.predict(features)
            
            return {
                'predicted_lifetime': float(np.mean(longevity_predictions)),
                'engagement_decay_rate': self._calculate_decay_rate(content_data),
                'peak_engagement_window': self._identify_peak_window(content_data),
                'evergreen_score': self._calculate_evergreen_score(content_data)
            }
        except Exception as e:
            self.logger.error(f"Error predicting content longevity: {str(e)}")
            return {}

    def _calculate_time_gaps(self, timestamps: pd.Series) -> List[float]:
        """Calculate time gaps between content interactions"""
        timestamps = pd.to_datetime(timestamps)
        return [
            (timestamps.iloc[i+1] - timestamps.iloc[i]).total_seconds() / 3600
            for i in range(len(timestamps)-1)
        ]

    def _extract_content_features(self, content_data: pd.DataFrame) -> np.ndarray:
        """Extract features for content performance prediction"""
        try:
            # Encode categorical features
            content_data['content_type_encoded'] = self.label_encoder.fit_transform(
                content_data['content_type']
            )
            
            features = content_data[[
                'content_type_encoded',
                'media_count',
                'text_length',
                'hashtag_count',
                'hour_posted',
                'day_of_week'
            ]].values
            
            return features
        except Exception as e:
            self.logger.error(f"Error extracting content features: {str(e)}")
            return np.array([])
