"""
TikTok Audience Analytics Module
Handles TikTok-specific audience insights and analysis
"""

from typing import Dict, List, Optional
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from .audience_analyzer import AudienceAnalyzer

class TikTokAudienceAnalyzer(AudienceAnalyzer):
    def __init__(self):
        super().__init__('tiktok')
        
    def process_insights(self, insights_data: Dict) -> Dict:
        """
        Process raw TikTok insights data into analyzed metrics
        
        Args:
            insights_data: Dict containing TikTok audience insights
            
        Returns:
            Dict containing processed analytics
        """
        processed_data = {
            'demographics': self._analyze_tiktok_demographics(insights_data.get('user_data', {})),
            'activity': self._analyze_tiktok_activity(insights_data.get('activity_data', {})),
            'engagement': self._analyze_tiktok_engagement(insights_data.get('engagement_data', {})),
            'content_performance': self._analyze_content_metrics(insights_data.get('content_data', {})),
            'summary': self._generate_insights_summary(insights_data),
            'timestamp': insights_data.get('collected_at')
        }
        
        return processed_data
        
    def _analyze_tiktok_demographics(self, user_data: Dict) -> Dict:
        """Process TikTok demographic data"""
        demographics = {
            'age_distribution': {},
            'gender_distribution': {},
            'location_data': {},
            'device_distribution': {},
            'total_followers': 0
        }
        
        if not user_data:
            return demographics
            
        # Process age groups
        age_data = user_data.get('age_groups', {})
        total_users = sum(age_data.values()) if age_data else 0
        demographics['age_distribution'] = {
            age: (count/total_users)*100 if total_users else 0
            for age, count in age_data.items()
        }
        
        # Process gender distribution
        gender_data = user_data.get('gender', {})
        total_gender = sum(gender_data.values()) if gender_data else 0
        demographics['gender_distribution'] = {
            gender: (count/total_gender)*100 if total_gender else 0
            for gender, count in gender_data.items()
        }
        
        # Process location data
        demographics['location_data'] = {
            'countries': user_data.get('countries', {}),
            'cities': user_data.get('cities', {}),
            'regions': user_data.get('regions', {})
        }
        
        # Process device data
        demographics['device_distribution'] = user_data.get('devices', {})
        
        # Set total followers
        demographics['total_followers'] = user_data.get('follower_count', 0)
        
        return demographics
        
    def _analyze_tiktok_activity(self, activity_data: Dict) -> Dict:
        """Process TikTok audience activity patterns"""
        activity_metrics = {
            'hourly_activity': {},
            'weekly_activity': {},
            'peak_times': [],
            'engagement_windows': {}
        }
        
        if not activity_data:
            return activity_metrics
            
        # Process hourly activity
        hourly = activity_data.get('hourly_activity', {})
        total_hourly = sum(hourly.values()) if hourly else 0
        activity_metrics['hourly_activity'] = {
            str(hour): (count/total_hourly)*100 if total_hourly else 0
            for hour, count in hourly.items()
        }
        
        # Process weekly activity
        weekly = activity_data.get('weekly_activity', {})
        total_weekly = sum(weekly.values()) if weekly else 0
        activity_metrics['weekly_activity'] = {
            day: (count/total_weekly)*100 if total_weekly else 0
            for day, count in weekly.items()
        }
        
        # Find peak engagement times
        if hourly:
            peak_hours = sorted(hourly.items(), key=lambda x: x[1], reverse=True)[:3]
            activity_metrics['peak_times'] = [str(hour) for hour, _ in peak_hours]
            
        # Calculate engagement windows
        activity_metrics['engagement_windows'] = self._calculate_engagement_windows(hourly)
        
        return activity_metrics
        
    def _analyze_tiktok_engagement(self, engagement_data: Dict) -> Dict:
        """Process TikTok engagement metrics"""
        engagement_metrics = {
            'overall_engagement_rate': 0,
            'engagement_by_content_type': {},
            'engagement_trends': {},
            'viral_potential': {}
        }
        
        if not engagement_data:
            return engagement_metrics
            
        # Calculate overall engagement rate
        total_interactions = engagement_data.get('total_interactions', 0)
        total_followers = engagement_data.get('follower_count', 1)  # Avoid division by zero
        engagement_metrics['overall_engagement_rate'] = (total_interactions / total_followers) * 100
        
        # Process engagement by content type
        content_engagement = engagement_data.get('content_type_engagement', {})
        engagement_metrics['engagement_by_content_type'] = {
            content_type: {
                'engagement_rate': stats.get('engagement_rate', 0),
                'completion_rate': stats.get('completion_rate', 0),
                'share_rate': stats.get('share_rate', 0)
            }
            for content_type, stats in content_engagement.items()
        }
        
        # Process engagement trends
        engagement_metrics['engagement_trends'] = engagement_data.get('trends', {})
        
        # Calculate viral potential
        engagement_metrics['viral_potential'] = self._calculate_viral_potential(engagement_data)
        
        return engagement_metrics
        
    def _analyze_content_metrics(self, content_data: Dict) -> Dict:
        """Process TikTok content performance metrics"""
        content_metrics = {
            'top_performing_content': [],
            'content_type_distribution': {},
            'hashtag_performance': {},
            'sound_performance': {}
        }
        
        if not content_data:
            return content_metrics
            
        # Process top performing content
        content_metrics['top_performing_content'] = content_data.get('top_posts', [])
        
        # Process content type distribution
        content_metrics['content_type_distribution'] = content_data.get('type_distribution', {})
        
        # Process hashtag performance
        content_metrics['hashtag_performance'] = content_data.get('hashtag_stats', {})
        
        # Process sound performance
        content_metrics['sound_performance'] = content_data.get('sound_stats', {})
        
        return content_metrics
        
    def _calculate_engagement_windows(self, hourly_data: Dict) -> Dict:
        """Calculate optimal engagement windows based on activity patterns"""
        if not hourly_data:
            return {}
            
        # Convert to list for easier processing
        hourly_activity = [(hour, count) for hour, count in hourly_data.items()]
        hourly_activity.sort(key=lambda x: x[1], reverse=True)
        
        # Find windows with consistent high engagement
        engagement_windows = {
            'prime_time': [],
            'secondary_time': [],
            'low_activity': []
        }
        
        # Define thresholds
        max_engagement = max(count for _, count in hourly_activity)
        prime_threshold = max_engagement * 0.8
        secondary_threshold = max_engagement * 0.5
        
        for hour, count in hourly_activity:
            if count >= prime_threshold:
                engagement_windows['prime_time'].append(str(hour))
            elif count >= secondary_threshold:
                engagement_windows['secondary_time'].append(str(hour))
            else:
                engagement_windows['low_activity'].append(str(hour))
                
        return engagement_windows
        
    def _calculate_viral_potential(self, engagement_data: Dict) -> Dict:
        """Calculate viral potential score based on engagement metrics"""
        viral_metrics = {
            'viral_score': 0,
            'contributing_factors': {},
            'trending_indicators': {}
        }
        
        if not engagement_data:
            return viral_metrics
            
        # Extract relevant metrics
        share_rate = engagement_data.get('share_rate', 0)
        save_rate = engagement_data.get('save_rate', 0)
        completion_rate = engagement_data.get('completion_rate', 0)
        engagement_velocity = engagement_data.get('engagement_velocity', 0)
        
        # Calculate viral score (simplified version)
        weights = {
            'share_rate': 0.4,
            'save_rate': 0.2,
            'completion_rate': 0.2,
            'engagement_velocity': 0.2
        }
        
        viral_score = (
            (share_rate * weights['share_rate']) +
            (save_rate * weights['save_rate']) +
            (completion_rate * weights['completion_rate']) +
            (engagement_velocity * weights['engagement_velocity'])
        )
        
        viral_metrics['viral_score'] = min(viral_score, 100)  # Cap at 100
        
        # Identify contributing factors
        viral_metrics['contributing_factors'] = {
            'share_rate': share_rate,
            'save_rate': save_rate,
            'completion_rate': completion_rate,
            'engagement_velocity': engagement_velocity
        }
        
        # Add trending indicators
        viral_metrics['trending_indicators'] = {
            'is_trending': viral_score > 70,
            'trend_direction': 'up' if engagement_velocity > 0 else 'down',
            'viral_potential': 'high' if viral_score > 70 else 'medium' if viral_score > 40 else 'low'
        }
        
        return viral_metrics
        
    def _generate_insights_summary(self, insights_data: Dict) -> Dict:
        """Generate a summary of key insights"""
        demographics = insights_data.get('user_data', {})
        engagement = insights_data.get('engagement_data', {})
        
        total_followers = demographics.get('follower_count', 0)
        engagement_rate = engagement.get('overall_engagement_rate', 0)
        
        return {
            'total_audience': total_followers,
            'engagement_health': self._calculate_engagement_health(engagement_rate),
            'growth_indicators': self._extract_growth_indicators(insights_data),
            'collection_timestamp': insights_data.get('collected_at'),
            'data_quality': self._assess_data_quality(insights_data)
        }
        
    def _calculate_engagement_health(self, engagement_rate: float) -> str:
        """Calculate engagement health status"""
        if engagement_rate >= 15:
            return 'excellent'
        elif engagement_rate >= 10:
            return 'good'
        elif engagement_rate >= 5:
            return 'average'
        else:
            return 'needs improvement'
            
    def _extract_growth_indicators(self, insights_data: Dict) -> Dict:
        """Extract growth indicators from insights data"""
        growth_data = insights_data.get('growth_data', {})
        
        return {
            'follower_growth_rate': growth_data.get('growth_rate', 0),
            'retention_rate': growth_data.get('retention_rate', 0),
            'churn_rate': growth_data.get('churn_rate', 0),
            'growth_trend': growth_data.get('trend', 'stable')
        }
        
    def _assess_data_quality(self, insights_data: Dict) -> Dict:
        """Assess the quality and completeness of the insights data"""
        expected_keys = ['user_data', 'activity_data', 'engagement_data', 'content_data']
        actual_keys = list(insights_data.keys())
        
        completeness = len([k for k in expected_keys if k in actual_keys]) / len(expected_keys)
        
        return {
            'completeness_score': completeness,
            'missing_metrics': [k for k in expected_keys if k not in actual_keys],
            'available_metrics': actual_keys
        }
