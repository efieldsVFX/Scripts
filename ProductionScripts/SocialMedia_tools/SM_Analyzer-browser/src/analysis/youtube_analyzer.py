"""
YouTube Analytics Module
Handles YouTube-specific audience insights and analysis
"""

from typing import Dict, List, Optional
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from .audience_analyzer import AudienceAnalyzer

class YouTubeAudienceAnalyzer(AudienceAnalyzer):
    def __init__(self):
        super().__init__('youtube')
        
    def process_insights(self, insights_data: Dict) -> Dict:
        """
        Process raw YouTube insights data into analyzed metrics
        
        Args:
            insights_data: Dict containing YouTube audience insights
            
        Returns:
            Dict containing processed analytics
        """
        processed_data = {
            'demographics': self._analyze_demographics(insights_data.get('demographics', {})),
            'engagement': self._analyze_engagement(insights_data.get('engagement_data', {})),
            'content_performance': self._analyze_content_performance(insights_data.get('content_data', {})),
            'audience_retention': self._analyze_audience_retention(insights_data.get('retention_data', {})),
            'traffic_sources': self._analyze_traffic_sources(insights_data.get('traffic_data', {})),
            'summary': self._generate_insights_summary(insights_data),
            'timestamp': insights_data.get('collected_at')
        }
        
        return processed_data
        
    def _analyze_demographics(self, demographics_data: Dict) -> Dict:
        """Process YouTube demographic data"""
        demographics = {
            'age_gender': self._process_age_gender_metrics(demographics_data.get('age_gender', {})),
            'geography': self._process_geographic_metrics(demographics_data.get('geography', {})),
            'devices': self._process_device_metrics(demographics_data.get('devices', {})),
            'subscriber_status': self._process_subscriber_metrics(demographics_data.get('subscribers', {}))
        }
        
        return demographics
        
    def _process_age_gender_metrics(self, age_gender_data: Dict) -> Dict:
        """Process age and gender distribution metrics"""
        metrics = {
            'age_groups': {},
            'gender_distribution': {},
            'age_gender_combined': {}
        }
        
        if not age_gender_data:
            return metrics
            
        # Process age groups
        age_data = age_gender_data.get('age_groups', {})
        total_viewers = sum(age_data.values()) if age_data else 0
        metrics['age_groups'] = {
            age: (count/total_viewers)*100 if total_viewers else 0
            for age, count in age_data.items()
        }
        
        # Process gender distribution
        gender_data = age_gender_data.get('gender', {})
        total_gender = sum(gender_data.values()) if gender_data else 0
        metrics['gender_distribution'] = {
            gender: (count/total_gender)*100 if total_gender else 0
            for gender, count in gender_data.items()
        }
        
        # Process combined age-gender data
        combined_data = age_gender_data.get('combined', {})
        total_combined = sum(combined_data.values()) if combined_data else 0
        metrics['age_gender_combined'] = {
            group: (count/total_combined)*100 if total_combined else 0
            for group, count in combined_data.items()
        }
        
        return metrics
        
    def _process_geographic_metrics(self, geography_data: Dict) -> Dict:
        """Process geographic distribution metrics"""
        metrics = {
            'countries': {},
            'regions': {},
            'top_locations': []
        }
        
        if not geography_data:
            return metrics
            
        # Process country distribution
        country_data = geography_data.get('countries', {})
        total_views = sum(country_data.values()) if country_data else 0
        metrics['countries'] = {
            country: (views/total_views)*100 if total_views else 0
            for country, views in country_data.items()
        }
        
        # Process region distribution
        region_data = geography_data.get('regions', {})
        total_regions = sum(region_data.values()) if region_data else 0
        metrics['regions'] = {
            region: (views/total_regions)*100 if total_regions else 0
            for region, views in region_data.items()
        }
        
        # Get top locations
        metrics['top_locations'] = sorted(
            [{'location': k, 'percentage': v} 
             for k, v in metrics['countries'].items()],
            key=lambda x: x['percentage'],
            reverse=True
        )[:10]
        
        return metrics
        
    def _process_device_metrics(self, device_data: Dict) -> Dict:
        """Process device usage metrics"""
        metrics = {
            'device_types': {},
            'operating_systems': {},
            'device_categories': {}
        }
        
        if not device_data:
            return metrics
            
        # Process device types
        device_types = device_data.get('types', {})
        total_devices = sum(device_types.values()) if device_types else 0
        metrics['device_types'] = {
            device: (count/total_devices)*100 if total_devices else 0
            for device, count in device_types.items()
        }
        
        # Process operating systems
        os_data = device_data.get('operating_systems', {})
        total_os = sum(os_data.values()) if os_data else 0
        metrics['operating_systems'] = {
            os: (count/total_os)*100 if total_os else 0
            for os, count in os_data.items()
        }
        
        # Process device categories
        categories = device_data.get('categories', {})
        total_categories = sum(categories.values()) if categories else 0
        metrics['device_categories'] = {
            category: (count/total_categories)*100 if total_categories else 0
            for category, count in categories.items()
        }
        
        return metrics
        
    def _process_subscriber_metrics(self, subscriber_data: Dict) -> Dict:
        """Process subscriber status metrics"""
        metrics = {
            'subscriber_ratio': {},
            'subscriber_growth': {},
            'subscriber_sources': {}
        }
        
        if not subscriber_data:
            return metrics
            
        # Process subscriber ratio
        total_viewers = subscriber_data.get('total_viewers', 0)
        if total_viewers:
            metrics['subscriber_ratio'] = {
                'subscribed': (subscriber_data.get('subscribed', 0) / total_viewers) * 100,
                'non_subscribed': (subscriber_data.get('non_subscribed', 0) / total_viewers) * 100
            }
            
        # Process subscriber growth
        growth_data = subscriber_data.get('growth', {})
        metrics['subscriber_growth'] = {
            'net_change': growth_data.get('net_change', 0),
            'gained': growth_data.get('gained', 0),
            'lost': growth_data.get('lost', 0),
            'growth_rate': growth_data.get('growth_rate', 0)
        }
        
        # Process subscriber sources
        source_data = subscriber_data.get('sources', {})
        total_sources = sum(source_data.values()) if source_data else 0
        metrics['subscriber_sources'] = {
            source: (count/total_sources)*100 if total_sources else 0
            for source, count in source_data.items()
        }
        
        return metrics
        
    def _analyze_engagement(self, engagement_data: Dict) -> Dict:
        """Analyze engagement metrics"""
        engagement_metrics = {
            'overall_engagement': self._calculate_overall_engagement(engagement_data),
            'engagement_trends': self._analyze_engagement_trends(engagement_data.get('trends', {})),
            'interaction_types': self._analyze_interaction_types(engagement_data.get('interactions', {})),
            'time_based_engagement': self._analyze_time_based_engagement(engagement_data.get('time_based', {}))
        }
        
        return engagement_metrics
        
    def _calculate_overall_engagement(self, data: Dict) -> Dict:
        """Calculate overall engagement metrics"""
        total_views = data.get('views', 0)
        metrics = {
            'engagement_rate': 0,
            'viewer_engagement_score': 0,
            'interaction_rate': 0
        }
        
        if total_views:
            total_interactions = (
                data.get('likes', 0) +
                data.get('comments', 0) +
                data.get('shares', 0)
            )
            metrics.update({
                'engagement_rate': (total_interactions / total_views) * 100,
                'viewer_engagement_score': total_interactions / total_views,
                'interaction_rate': total_interactions / (total_views * 3)  # Normalized to max possible interactions
            })
            
        return metrics
        
    def _analyze_engagement_trends(self, trends_data: Dict) -> Dict:
        """Analyze engagement trends over time"""
        return {
            'daily_trends': trends_data.get('daily', {}),
            'weekly_trends': trends_data.get('weekly', {}),
            'monthly_trends': trends_data.get('monthly', {}),
            'trend_indicators': self._calculate_trend_indicators(trends_data)
        }
        
    def _analyze_interaction_types(self, interaction_data: Dict) -> Dict:
        """Analyze different types of interactions"""
        total_interactions = sum(interaction_data.values()) if interaction_data else 0
        
        return {
            'distribution': {
                itype: (count/total_interactions)*100 if total_interactions else 0
                for itype, count in interaction_data.items()
            },
            'top_interactions': sorted(
                interaction_data.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
        }
        
    def _analyze_time_based_engagement(self, time_data: Dict) -> Dict:
        """Analyze engagement patterns based on time"""
        return {
            'hourly_patterns': time_data.get('hourly', {}),
            'daily_patterns': time_data.get('daily', {}),
            'peak_times': self._identify_peak_times(time_data)
        }
        
    def _analyze_content_performance(self, content_data: Dict) -> Dict:
        """Analyze content performance metrics"""
        return {
            'top_performing_content': self._analyze_top_content(content_data.get('top_content', [])),
            'content_types': self._analyze_content_types(content_data.get('types', {})),
            'performance_by_length': self._analyze_performance_by_length(content_data.get('by_length', {})),
            'topic_performance': self._analyze_topic_performance(content_data.get('topics', {}))
        }
        
    def _analyze_audience_retention(self, retention_data: Dict) -> Dict:
        """Analyze audience retention metrics"""
        return {
            'average_view_duration': retention_data.get('avg_view_duration', 0),
            'retention_curve': retention_data.get('retention_curve', {}),
            'audience_drop_off': self._analyze_drop_off_points(retention_data.get('drop_off', {})),
            'retention_by_type': retention_data.get('by_type', {})
        }
        
    def _analyze_traffic_sources(self, traffic_data: Dict) -> Dict:
        """Analyze traffic source metrics"""
        return {
            'source_distribution': self._calculate_source_distribution(traffic_data.get('sources', {})),
            'external_sources': self._analyze_external_sources(traffic_data.get('external', {})),
            'discovery_methods': self._analyze_discovery_methods(traffic_data.get('discovery', {})),
            'source_engagement': self._analyze_source_engagement(traffic_data.get('engagement', {}))
        }
        
    def _generate_insights_summary(self, insights_data: Dict) -> Dict:
        """Generate a summary of key insights"""
        return {
            'audience_size': self._calculate_audience_size(insights_data),
            'engagement_health': self._calculate_engagement_health(insights_data),
            'growth_indicators': self._calculate_growth_indicators(insights_data),
            'content_recommendations': self._generate_content_recommendations(insights_data),
            'key_metrics': self._extract_key_metrics(insights_data)
        }
        
    def _calculate_audience_size(self, data: Dict) -> Dict:
        """Calculate total audience size and growth"""
        subscriber_data = data.get('demographics', {}).get('subscriber_status', {})
        return {
            'total_subscribers': subscriber_data.get('total_subscribers', 0),
            'active_viewers': subscriber_data.get('active_viewers', 0),
            'growth_rate': subscriber_data.get('growth_rate', 0)
        }
        
    def _calculate_engagement_health(self, data: Dict) -> str:
        """Calculate overall engagement health status"""
        engagement_rate = data.get('engagement_data', {}).get('overall_engagement', {}).get('engagement_rate', 0)
        
        if engagement_rate >= 15:
            return 'excellent'
        elif engagement_rate >= 10:
            return 'very_good'
        elif engagement_rate >= 5:
            return 'good'
        elif engagement_rate >= 2:
            return 'average'
        else:
            return 'needs_improvement'
            
    def _calculate_growth_indicators(self, data: Dict) -> Dict:
        """Calculate growth indicators"""
        subscriber_data = data.get('demographics', {}).get('subscriber_status', {})
        engagement_data = data.get('engagement_data', {})
        
        return {
            'subscriber_growth': subscriber_data.get('growth_rate', 0),
            'engagement_growth': engagement_data.get('growth_rate', 0),
            'view_growth': engagement_data.get('view_growth', 0)
        }
        
    def _generate_content_recommendations(self, data: Dict) -> List[Dict]:
        """Generate content recommendations based on performance data"""
        content_data = data.get('content_data', {})
        top_content = content_data.get('top_performing_content', [])
        
        recommendations = []
        if top_content:
            # Analyze common patterns in top performing content
            for content in top_content[:5]:
                recommendations.append({
                    'type': content.get('type', ''),
                    'optimal_length': content.get('length', ''),
                    'best_publishing_time': content.get('publish_time', ''),
                    'recommended_topics': content.get('topics', [])
                })
                
        return recommendations
        
    def _extract_key_metrics(self, data: Dict) -> Dict:
        """Extract key performance metrics"""
        return {
            'views_per_video': data.get('engagement_data', {}).get('avg_views_per_video', 0),
            'avg_engagement_rate': data.get('engagement_data', {}).get('overall_engagement', {}).get('engagement_rate', 0),
            'subscriber_conversion': data.get('demographics', {}).get('subscriber_status', {}).get('conversion_rate', 0),
            'avg_view_duration': data.get('retention_data', {}).get('average_view_duration', 0)
        }
