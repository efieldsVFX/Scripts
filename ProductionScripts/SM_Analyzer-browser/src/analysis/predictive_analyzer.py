"""
Predictive Analytics Module
Handles virality prediction, follower decay analysis, and trend detection
"""

from typing import Dict, List, Optional
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import logging

logger = logging.getLogger(__name__)

class PredictiveAnalyzer:
    def __init__(self):
        self.scaler = StandardScaler()
        self.trend_threshold = 0.75  # Threshold for trend detection
        
    def calculate_virality_coefficient(self, data: pd.DataFrame) -> Dict:
        """Calculate virality coefficient based on follower growth and engagement"""
        try:
            if data.empty:
                return {}

            # Calculate average follower gain
            avg_follower_gain = data['follower_gain'].mean()
            
            # Calculate engagement rate
            total_engagement = data['engagement_metrics'].mean()
            total_followers = data['followers'].mean()
            engagement_rate = total_engagement / total_followers if total_followers > 0 else 0
            
            # Calculate virality coefficient (normalized between 0 and 1)
            virality_coef = (avg_follower_gain * engagement_rate) / (avg_follower_gain + engagement_rate)
            if pd.isna(virality_coef):
                virality_coef = 0
                
            return {
                'coefficient': float(virality_coef),
                'follower_gain_rate': float(avg_follower_gain),
                'engagement_rate': float(engagement_rate)
            }
            
        except Exception as e:
            logger.error(f"Error calculating virality coefficient: {str(e)}")
            return {}
        
    def predict_follower_decay(self, data: pd.DataFrame) -> Dict:
        """Predict follower decay rate based on historical data"""
        try:
            if data.empty:
                return {}
                
            # Convert date to datetime if needed
            if 'date' not in data.columns:
                return {}
                
            # Sort by date
            data = data.sort_values('date')
            
            # Calculate daily follower changes
            data['follower_change'] = data['followers'].diff()
            
            # Prepare data for regression
            X = (data['date'] - data['date'].min()).dt.days.values.reshape(-1, 1)
            y = data['follower_change'].fillna(0).values
            
            # Fit linear regression
            model = LinearRegression()
            model.fit(X, y)
            
            # Calculate metrics
            decay_rate = float(model.coef_[0])
            r2_score = float(model.score(X, y))
            
            return {
                'decay_rate': decay_rate,
                'confidence': r2_score,
                'days_analyzed': len(data)
            }
            
        except Exception as e:
            logger.error(f"Error predicting follower decay: {str(e)}")
            return {}
        
    def estimate_lifetime_value(self, data: pd.DataFrame) -> Dict:
        """Estimate lifetime value based on engagement and conversion metrics"""
        try:
            if data.empty:
                return {}
                
            # Calculate average engagement value
            avg_engagement = data['engagement_metrics'].mean()
            
            # Calculate conversion rate (using engagement as proxy)
            total_engagement = data['engagement_metrics'].sum()
            total_interactions = len(data)
            conversion_rate = total_engagement / total_interactions if total_interactions > 0 else 0
            
            # Estimate lifetime value
            avg_lifetime = 365  # Assume 1 year average lifetime
            daily_value = (avg_engagement * conversion_rate) / 30  # Monthly average
            lifetime_value = daily_value * avg_lifetime
            
            return {
                'estimated_value': float(lifetime_value),
                'daily_value': float(daily_value),
                'conversion_rate': float(conversion_rate)
            }
            
        except Exception as e:
            logger.error(f"Error estimating lifetime value: {str(e)}")
            return {}
            
    def detect_trends(self, data: pd.DataFrame) -> Dict:
        """Detect engagement trends and patterns"""
        try:
            if data.empty:
                return {}
                
            # Calculate engagement trends
            engagement_by_type = data.groupby('post_type')['engagement_metrics'].agg([
                'mean', 'std', 'count'
            ]).round(2).to_dict('index')
            
            # Find trending content types
            trends = []
            for content_type, metrics in engagement_by_type.items():
                if metrics['mean'] > data['engagement_metrics'].mean():
                    trends.append({
                        'type': content_type,
                        'engagement_rate': float(metrics['mean']),
                        'sample_size': int(metrics['count'])
                    })
            
            return {
                'trending_types': trends,
                'total_analyzed': len(data)
            }
            
        except Exception as e:
            logger.error(f"Error detecting trends: {str(e)}")
            return {}
        
    def get_predictive_insights(self, data: Dict[str, pd.DataFrame]) -> Dict:
        """
        Generate comprehensive predictive insights
        
        Args:
            data: Dict containing DataFrames with platform data
            
        Returns:
            Dict containing overall predictive metrics
        """
        try:
            # Preprocess engagement data
            engagement_df = data.get('engagement', pd.DataFrame())
            if not engagement_df.empty:
                if 'follower_gain' not in engagement_df.columns:
                    engagement_df['follower_gain'] = engagement_df.get('followers_delta', 0)
                if 'engagement_metrics' not in engagement_df.columns:
                    engagement_df['engagement_metrics'] = engagement_df.apply(
                        lambda x: sum([
                            x.get('likes', 0),
                            x.get('comments', 0) * 2,
                            x.get('shares', 0) * 3,
                            x.get('saves', 0) * 4
                        ]),
                        axis=1
                    )
                if 'conversion_value' not in engagement_df.columns:
                    engagement_df['conversion_value'] = engagement_df['engagement_metrics'] * 0.1

            # Preprocess content data
            content_df = data.get('content', pd.DataFrame())
            if not content_df.empty and 'engagement_metrics' not in content_df.columns:
                content_df['engagement_metrics'] = content_df.apply(
                    lambda x: sum([
                        x.get('likes', 0),
                        x.get('comments', 0) * 2,
                        x.get('shares', 0) * 3,
                        x.get('saves', 0) * 4
                    ]),
                    axis=1
                )

            # Generate predictions
            predictions = {
                'virality': self.calculate_virality_coefficient(engagement_df) if not engagement_df.empty else {},
                'follower_decay': self.predict_follower_decay(engagement_df) if not engagement_df.empty else {},
                'lifetime_value': self.estimate_lifetime_value(engagement_df) if not engagement_df.empty else {},
                'trends': self.detect_trends(content_df) if not content_df.empty else {}
            }
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error generating predictive insights: {str(e)}")
            return {}
