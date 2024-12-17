"""
Audience Analytics Module
Handles demographic analysis, audience insights, and growth tracking across different social media platforms
"""

from typing import Dict, List, Optional
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class AudienceAnalyzer(ABC):
    """Base class for analyzing social media audience data"""

    def __init__(self, platform: str):
        """Initialize analyzer for specific platform"""
        self.platform = platform
        self.logger = logging.getLogger(__name__)

    def process_insights(self, insights: Dict) -> Dict:
        """Process platform-specific audience insights"""
        processed = {
            'demographics': self.analyze_demographics(insights.get('demographics', {})),
            'active_times': self.analyze_active_times(insights.get('activity', {})),
            'interests': self.analyze_interests(insights.get('interests', {})),
            'engagement': self.analyze_engagement(insights.get('engagement', {})),
            'growth': self.analyze_growth(insights.get('growth', {})),
            'age_content_affinity': self.analyze_age_content_affinity(
                insights.get('demographics', {}),
                insights.get('engagement', {})
            )
        }
        return processed

    def analyze_demographics(self, data: Dict) -> Dict:
        """Analyze audience demographics"""
        try:
            demographics = {
                'age_distribution': self._process_age_data(data.get('age_data', {})),
                'gender_distribution': self._process_gender_data(data.get('gender_data', {})),
                'location_distribution': self._process_location_data(data.get('location_data', {})),
                'language_distribution': self._process_language_data(data.get('language_data', {})),
                'income_distribution': self._process_income_data(data.get('income_data', {}))
            }
            return demographics
        except Exception as e:
            self.logger.error(f"Error analyzing demographics: {str(e)}")
            return {}

    def analyze_active_times(self, data: Dict) -> Dict:
        """Analyze audience active times"""
        try:
            active_times = {
                'hourly_activity': self._analyze_hourly_patterns(data.get('hourly_data', {})),
                'daily_activity': self._analyze_daily_patterns(data.get('daily_data', {})),
                'timezone_distribution': self._analyze_timezone_patterns(data.get('timezone_data', {})),
                'peak_engagement_times': self._identify_peak_times(data),
                'optimal_posting_windows': self._calculate_posting_windows(data)
            }
            return active_times
        except Exception as e:
            self.logger.error(f"Error analyzing active times: {str(e)}")
            return {}

    def analyze_age_content_affinity(self, demographics: Dict, engagement: Dict) -> Dict:
        """Analyze content preferences by age group"""
        try:
            age_groups = demographics.get('age_data', {})
            content_engagement = engagement.get('content_engagement', {})
            
            affinity_metrics = {}
            for age_group in age_groups:
                group_engagement = self._filter_engagement_by_age(
                    content_engagement, 
                    age_group
                )
                
                affinity_metrics[age_group] = {
                    'top_content_types': self._get_top_content_types(group_engagement),
                    'preferred_formats': self._get_format_preferences(group_engagement),
                    'topic_interests': self._get_topic_interests(group_engagement),
                    'engagement_patterns': self._get_engagement_patterns(group_engagement),
                    'time_spent': self._calculate_time_spent(group_engagement)
                }
            
            return affinity_metrics
        except Exception as e:
            self.logger.error(f"Error analyzing age content affinity: {str(e)}")
            return {}

    def analyze_growth(self, data: Dict) -> Dict:
        """Analyze follower growth patterns"""
        try:
            self.logger.debug(f"Starting growth analysis with data keys: {data.keys()}")
            growth_metrics = {
                'daily_growth': self._calculate_daily_growth(data),
                'growth_rate': self._calculate_growth_rate(data),
                'churn_rate': self._calculate_churn_rate(data),
                'retention_metrics': self._analyze_retention(data),
                'growth_sources': self._analyze_growth_sources(data),
                'follower_quality': self._analyze_follower_quality(data)
            }
            self.logger.debug(f"Completed growth analysis with metrics: {list(growth_metrics.keys())}")
            return growth_metrics
        except Exception as e:
            self.logger.error(f"Error analyzing growth: {str(e)}\nData: {data}")
            return {}

    def _calculate_daily_growth(self, data: Dict) -> Dict:
        """Calculate daily follower gains and losses"""
        try:
            daily_data = data.get('daily_data', [])
            return {
                'net_growth': [d['followers_gained'] - d['followers_lost'] for d in daily_data],
                'gains': [d['followers_gained'] for d in daily_data],
                'losses': [d['followers_lost'] for d in daily_data],
                'dates': [d['date'] for d in daily_data]
            }
        except Exception as e:
            self.logger.error(f"Error calculating daily growth: {str(e)}")
            return {}

    def _analyze_growth_sources(self, data: Dict) -> Dict:
        """Analyze sources of follower growth"""
        try:
            sources = data.get('growth_sources', {})
            return {
                'organic_growth': sources.get('organic', 0),
                'paid_growth': sources.get('paid', 0),
                'referral_growth': sources.get('referral', 0),
                'cross_platform': sources.get('cross_platform', 0),
                'source_conversion_rates': self._calculate_source_conversion(sources)
            }
        except Exception as e:
            self.logger.error(f"Error analyzing growth sources: {str(e)}")
            return {}

    def _analyze_follower_quality(self, data: Dict) -> Dict:
        """Analyze the quality and authenticity of followers"""
        try:
            return {
                'engagement_rate': data.get('engagement_rate', 0),
                'active_followers': data.get('active_followers', 0),
                'authentic_followers': data.get('authentic_followers', 0),
                'follower_health_score': self._calculate_follower_health(data),
                'engagement_consistency': self._calculate_engagement_consistency(data)
            }
        except Exception as e:
            self.logger.error(f"Error analyzing follower quality: {str(e)}")
            return {}

    def _filter_engagement_by_age(self, engagement: Dict, age_group: str) -> Dict:
        """Filter engagement data for specific age group"""
        try:
            return {
                content_id: metrics
                for content_id, metrics in engagement.items()
                if metrics.get('age_group') == age_group
            }
        except Exception as e:
            self.logger.error(f"Error filtering engagement by age: {str(e)}")
            return {}

    def _get_top_content_types(self, engagement: Dict) -> List[Dict]:
        """Get most engaging content types for an age group"""
        try:
            content_performance = {}
            for content_id, metrics in engagement.items():
                content_type = metrics.get('content_type')
                if content_type:
                    if content_type not in content_performance:
                        content_performance[content_type] = []
                    content_performance[content_type].append(metrics.get('engagement_rate', 0))
            
            return [
                {
                    'type': content_type,
                    'avg_engagement': np.mean(rates)
                }
                for content_type, rates in content_performance.items()
            ]
        except Exception as e:
            self.logger.error(f"Error getting top content types: {str(e)}")
            return []

    def _process_age_data(self, data: Dict) -> Dict:
        """Process age distribution data"""
        return {age: count for age, count in data.items()}

    def _process_gender_data(self, data: Dict) -> Dict:
        """Process gender distribution data"""
        return {gender: percentage for gender, percentage in data.items()}

    def _process_location_data(self, data: Dict) -> Dict:
        """Process geographic location data"""
        return {location: count for location, count in sorted(
            data.items(), key=lambda x: x[1], reverse=True
        )[:10]}

    def _process_language_data(self, data: Dict) -> Dict:
        """Process language preference data"""
        return {lang: count for lang, count in sorted(
            data.items(), key=lambda x: x[1], reverse=True
        )[:5]}

    def _process_income_data(self, data: Dict) -> Dict:
        """Process income distribution data"""
        return {income: count for income, count in sorted(
            data.items(), key=lambda x: x[1], reverse=True
        )[:5]}

    def _analyze_hourly_patterns(self, data: Dict) -> Dict:
        """Analyze hourly activity patterns"""
        return {str(hour): count for hour, count in sorted(data.items())}

    def _analyze_daily_patterns(self, data: Dict) -> Dict:
        """Analyze daily activity patterns"""
        return {day: count for day, count in sorted(data.items())}

    def _analyze_timezone_patterns(self, data: Dict) -> Dict:
        """Analyze timezone distribution data"""
        return {tz: count for tz, count in sorted(
            data.items(), key=lambda x: x[1], reverse=True
        )[:5]}

    def _identify_peak_times(self, data: Dict) -> List[int]:
        """Identify peak activity times"""
        if not data:
            return []
        sorted_hours = sorted(data.items(), key=lambda x: x[1], reverse=True)
        return [int(hour) for hour, _ in sorted_hours[:3]]

    def _calculate_posting_windows(self, data: Dict) -> List[int]:
        """Calculate optimal posting windows"""
        if not data:
            return []
        sorted_hours = sorted(data.items(), key=lambda x: x[1], reverse=True)
        return [int(hour) for hour, _ in sorted_hours[:3]]

    def _calculate_growth_rate(self, data: Dict) -> float:
        """Calculate growth rate"""
        try:
            return data.get('growth_rate', 0)
        except Exception:
            return 0

    def _calculate_churn_rate(self, data: Dict) -> float:
        """Calculate churn rate"""
        try:
            return data.get('churn_rate', 0)
        except Exception:
            return 0

    def _analyze_retention(self, data: Dict) -> Dict:
        """Analyze audience retention"""
        try:
            return data
        except Exception:
            return {}

    def _calculate_source_conversion(self, sources: Dict) -> Dict:
        """Calculate source conversion rates"""
        try:
            return {
                source: rate
                for source, rate in sources.items()
            }
        except Exception:
            return {}

    def _calculate_follower_health(self, data: Dict) -> float:
        """Calculate follower health score"""
        try:
            return data.get('follower_health_score', 0)
        except Exception:
            return 0

    def _calculate_engagement_consistency(self, data: Dict) -> float:
        """Calculate engagement consistency"""
        try:
            return data.get('engagement_consistency', 0)
        except Exception:
            return 0

    def _get_format_preferences(self, engagement: Dict) -> List[Dict]:
        """Get preferred content formats for an age group"""
        try:
            format_performance = {}
            for content_id, metrics in engagement.items():
                content_format = metrics.get('content_format')
                if content_format:
                    if content_format not in format_performance:
                        format_performance[content_format] = []
                    format_performance[content_format].append(metrics.get('engagement_rate', 0))
            
            return [
                {
                    'format': content_format,
                    'avg_engagement': np.mean(rates)
                }
                for content_format, rates in format_performance.items()
            ]
        except Exception as e:
            self.logger.error(f"Error getting format preferences: {str(e)}")
            return []

    def _get_topic_interests(self, engagement: Dict) -> List[Dict]:
        """Get topic interests for an age group"""
        try:
            topic_performance = {}
            for content_id, metrics in engagement.items():
                topic = metrics.get('topic')
                if topic:
                    if topic not in topic_performance:
                        topic_performance[topic] = []
                    topic_performance[topic].append(metrics.get('engagement_rate', 0))
            
            return [
                {
                    'topic': topic,
                    'avg_engagement': np.mean(rates)
                }
                for topic, rates in topic_performance.items()
            ]
        except Exception as e:
            self.logger.error(f"Error getting topic interests: {str(e)}")
            return []

    def _get_engagement_patterns(self, engagement: Dict) -> List[Dict]:
        """Get engagement patterns for an age group"""
        try:
            engagement_patterns = {}
            for content_id, metrics in engagement.items():
                engagement_type = metrics.get('engagement_type')
                if engagement_type:
                    if engagement_type not in engagement_patterns:
                        engagement_patterns[engagement_type] = []
                    engagement_patterns[engagement_type].append(metrics.get('engagement_rate', 0))
            
            return [
                {
                    'type': engagement_type,
                    'avg_engagement': np.mean(rates)
                }
                for engagement_type, rates in engagement_patterns.items()
            ]
        except Exception as e:
            self.logger.error(f"Error getting engagement patterns: {str(e)}")
            return []

    def _calculate_time_spent(self, engagement: Dict) -> float:
        """Calculate time spent by an age group"""
        try:
            return np.mean([metrics.get('time_spent', 0) for metrics in engagement.values()])
        except Exception as e:
            self.logger.error(f"Error calculating time spent: {str(e)}")
            return 0

class InstagramAudienceAnalyzer(AudienceAnalyzer):
    def __init__(self):
        super().__init__('instagram')
        
    def process_insights(self, insights: Dict) -> Dict:
        # Add Instagram-specific insights processing logic here
        processed = {
            'demographics': self.analyze_demographics(insights.get('demographics', {})),
            'active_times': self.analyze_active_times(insights.get('activity', {})),
            'interests': self.analyze_interests(insights.get('interests', {})),
            'engagement': self.analyze_engagement(insights.get('engagement', {})),
            'growth': self.analyze_growth(insights.get('growth', {}))
        }
        return processed

def create_audience_analyzer(platform: str) -> AudienceAnalyzer:
    if platform.lower() == 'instagram':
        return InstagramAudienceAnalyzer()
    else:
        raise ValueError(f"Unsupported platform: {platform}. Currently only Instagram is supported.")