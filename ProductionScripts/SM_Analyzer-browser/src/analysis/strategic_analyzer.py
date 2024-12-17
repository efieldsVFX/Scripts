"""
Strategic Metrics Analyzer
Handles ROI calculations, trend forecasting, and strategic performance metrics
"""

from typing import Dict, List, Optional, Union
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from statsmodels.tsa.holtwinters import ExponentialSmoothing

class StrategicAnalyzer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.scaler = StandardScaler()
        self.forecasting_model = RandomForestRegressor(n_estimators=100)

    def analyze_roi_metrics(self, campaign_data: pd.DataFrame) -> Dict:
        """Calculate ROI metrics for different content types and campaigns"""
        try:
            roi_metrics = {
                'post_type_roi': self._calculate_post_type_roi(campaign_data),
                'campaign_roi': self._calculate_campaign_roi(campaign_data),
                'platform_roi': self._calculate_platform_roi(campaign_data),
                'content_investment_analysis': self._analyze_content_investment(campaign_data)
            }
            return roi_metrics
        except Exception as e:
            self.logger.error(f"Error analyzing ROI metrics: {str(e)}")
            return {}

    def forecast_trends(
        self, 
        historical_data: pd.DataFrame,
        forecast_periods: List[int] = [7, 30, 90]
    ) -> Dict:
        """Generate performance forecasts for different time periods"""
        try:
            forecasts = {
                f"{period}_day_forecast": self._generate_forecast(
                    historical_data, period
                ) for period in forecast_periods
            }
            
            forecasts.update({
                'trend_confidence': self._calculate_trend_confidence(historical_data),
                'seasonal_patterns': self._identify_seasonal_patterns(historical_data),
                'growth_trajectory': self._analyze_growth_trajectory(historical_data)
            })
            
            return forecasts
        except Exception as e:
            self.logger.error(f"Error forecasting trends: {str(e)}")
            return {}

    def analyze_posting_schedule(self, engagement_data: pd.DataFrame) -> Dict:
        """Determine optimal posting schedule based on engagement patterns"""
        try:
            schedule_metrics = {
                'optimal_times': self._calculate_optimal_times(engagement_data),
                'day_performance': self._analyze_day_performance(engagement_data),
                'timezone_optimization': self._analyze_timezone_impact(engagement_data),
                'frequency_recommendations': self._generate_frequency_recommendations(engagement_data)
            }
            return schedule_metrics
        except Exception as e:
            self.logger.error(f"Error analyzing posting schedule: {str(e)}")
            return {}

    def analyze_campaign_impact(self, campaign_data: pd.DataFrame) -> Dict:
        """Measure campaign success across platforms"""
        try:
            impact_metrics = {
                'overall_impact': self._calculate_overall_impact(campaign_data),
                'platform_performance': self._analyze_platform_performance(campaign_data),
                'audience_growth': self._analyze_audience_growth(campaign_data),
                'engagement_lift': self._calculate_engagement_lift(campaign_data),
                'brand_impact': self._analyze_brand_impact(campaign_data)
            }
            return impact_metrics
        except Exception as e:
            self.logger.error(f"Error analyzing campaign impact: {str(e)}")
            return {}

    def analyze_brand_voice(self, content_data: pd.DataFrame) -> Dict:
        """Analyze brand voice consistency across content"""
        try:
            voice_metrics = {
                'tone_consistency': self._analyze_tone_consistency(content_data),
                'message_alignment': self._analyze_message_alignment(content_data),
                'visual_consistency': self._analyze_visual_consistency(content_data),
                'brand_guidelines_adherence': self._check_guidelines_adherence(content_data)
            }
            return voice_metrics
        except Exception as e:
            self.logger.error(f"Error analyzing brand voice: {str(e)}")
            return {}

    def _calculate_post_type_roi(self, campaign_data: pd.DataFrame) -> Dict:
        """Calculate ROI for different post types"""
        try:
            roi_by_type = {}
            for post_type in campaign_data['post_type'].unique():
                type_data = campaign_data[campaign_data['post_type'] == post_type]
                
                revenue = type_data['revenue'].sum()
                cost = type_data['cost'].sum()
                
                if cost > 0:
                    roi = ((revenue - cost) / cost) * 100
                else:
                    roi = 0
                    
                roi_by_type[post_type] = {
                    'roi_percentage': roi,
                    'total_revenue': revenue,
                    'total_cost': cost,
                    'average_return': revenue / len(type_data) if len(type_data) > 0 else 0
                }
                
            return roi_by_type
        except Exception as e:
            self.logger.error(f"Error calculating post type ROI: {str(e)}")
            return {}

    def _generate_forecast(
        self, 
        historical_data: pd.DataFrame,
        forecast_days: int
    ) -> Dict:
        """Generate forecast for specified number of days"""
        try:
            # Prepare time series data
            ts_data = historical_data.set_index('date')['engagement_rate']
            
            # Fit exponential smoothing model
            model = ExponentialSmoothing(
                ts_data,
                seasonal_periods=7,
                trend='add',
                seasonal='add'
            )
            fitted_model = model.fit()
            
            # Generate forecast
            forecast = fitted_model.forecast(forecast_days)
            
            return {
                'predicted_values': forecast.tolist(),
                'confidence_intervals': self._calculate_confidence_intervals(forecast),
                'trend_direction': 'up' if forecast.mean() > ts_data.mean() else 'down',
                'forecast_accuracy': self._calculate_forecast_accuracy(fitted_model, ts_data)
            }
        except Exception as e:
            self.logger.error(f"Error generating forecast: {str(e)}")
            return {}

    def _calculate_optimal_times(self, engagement_data: pd.DataFrame) -> Dict:
        """Calculate optimal posting times based on engagement patterns"""
        try:
            # Convert to datetime and extract hour
            engagement_data['hour'] = pd.to_datetime(
                engagement_data['timestamp']
            ).dt.hour
            
            # Calculate average engagement by hour
            hourly_engagement = engagement_data.groupby('hour')['engagement_rate'].mean()
            
            # Find top performing hours
            top_hours = hourly_engagement.nlargest(5)
            
            return {
                'best_hours': top_hours.index.tolist(),
                'engagement_by_hour': hourly_engagement.to_dict(),
                'peak_periods': self._identify_peak_periods(hourly_engagement),
                'timezone_adjustments': self._calculate_timezone_adjustments(engagement_data)
            }
        except Exception as e:
            self.logger.error(f"Error calculating optimal times: {str(e)}")
            return {}

    def _analyze_brand_impact(self, campaign_data: pd.DataFrame) -> Dict:
        """Analyze campaign impact on brand metrics"""
        try:
            pre_campaign = campaign_data[campaign_data['phase'] == 'pre']
            during_campaign = campaign_data[campaign_data['phase'] == 'during']
            post_campaign = campaign_data[campaign_data['phase'] == 'post']
            
            return {
                'brand_awareness_lift': self._calculate_awareness_lift(
                    pre_campaign, post_campaign
                ),
                'sentiment_change': self._calculate_sentiment_change(
                    pre_campaign, post_campaign
                ),
                'audience_growth': self._calculate_audience_growth(
                    pre_campaign, post_campaign
                ),
                'engagement_quality': self._analyze_engagement_quality(during_campaign)
            }
        except Exception as e:
            self.logger.error(f"Error analyzing brand impact: {str(e)}")
            return {}

    def _calculate_confidence_intervals(self, forecast: pd.Series) -> Dict:
        """Calculate confidence intervals for forecast"""
        try:
            std_dev = forecast.std()
            return {
                'lower_bound': (forecast - (1.96 * std_dev)).tolist(),
                'upper_bound': (forecast + (1.96 * std_dev)).tolist()
            }
        except Exception as e:
            self.logger.error(f"Error calculating confidence intervals: {str(e)}")
            return {}
