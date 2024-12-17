"""
Twitter Audience Analytics Module
Handles Twitter-specific audience insights and analysis
"""

from typing import Dict, List, Optional
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from .audience_analyzer import AudienceAnalyzer

class TwitterAudienceAnalyzer(AudienceAnalyzer):
    def __init__(self):
        super().__init__('twitter')
        
    def process_insights(self, insights_data: Dict) -> Dict:
        """
        Process raw Twitter insights data into analyzed metrics
        
        Args:
            insights_data: Dict containing Twitter audience insights
            
        Returns:
            Dict containing processed analytics
        """
        processed_data = {
            'demographics': self._analyze_twitter_demographics(insights_data.get('follower_data', {})),
            'activity': self._analyze_twitter_activity(insights_data.get('activity_data', {})),
            'engagement': self._analyze_twitter_engagement(insights_data.get('engagement_data', {})),
            'interests': self._analyze_twitter_interests(insights_data.get('interest_data', {})),
            'summary': self._generate_insights_summary(insights_data),
            'timestamp': insights_data.get('collected_at')
        }
        
        return processed_data
        
    def _analyze_twitter_demographics(self, follower_data: Dict) -> Dict:
        """Process Twitter demographic data"""
        demographics = {
            'age_distribution': {},
            'gender_distribution': {},
            'location_data': {},
            'language_distribution': {},
            'total_followers': 0
        }
        
        if not follower_data:
            return demographics
            
        # Process age groups
        age_data = follower_data.get('age_groups', {})
        total_users = sum(age_data.values()) if age_data else 0
        demographics['age_distribution'] = {
            age: (count/total_users)*100 if total_users else 0
            for age, count in age_data.items()
        }
        
        # Process gender distribution
        gender_data = follower_data.get('gender', {})
        total_gender = sum(gender_data.values()) if gender_data else 0
        demographics['gender_distribution'] = {
            gender: (count/total_gender)*100 if total_gender else 0
            for gender, count in gender_data.items()
        }
        
        # Process location data
        demographics['location_data'] = {
            'countries': follower_data.get('countries', {}),
            'cities': follower_data.get('cities', {}),
            'regions': follower_data.get('regions', {})
        }
        
        # Process language distribution
        lang_data = follower_data.get('languages', {})
        total_lang = sum(lang_data.values()) if lang_data else 0
        demographics['language_distribution'] = {
            lang: (count/total_lang)*100 if total_lang else 0
            for lang, count in lang_data.items()
        }
        
        # Set total followers
        demographics['total_followers'] = follower_data.get('total_followers', 0)
        
        return demographics
        
    def _analyze_twitter_activity(self, activity_data: Dict) -> Dict:
        """Process Twitter audience activity patterns"""
        activity_metrics = {
            'hourly_activity': {},
            'weekly_activity': {},
            'peak_times': [],
            'tweet_frequency': {}
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
            
        # Calculate tweet frequency
        activity_metrics['tweet_frequency'] = activity_data.get('tweet_frequency', {})
        
        return activity_metrics
        
    def _analyze_twitter_engagement(self, engagement_data: Dict) -> Dict:
        """Process Twitter engagement metrics"""
        engagement_metrics = {
            'overall_engagement_rate': 0,
            'engagement_by_type': {},
            'engagement_trends': {},
            'conversation_metrics': {}
        }
        
        if not engagement_data:
            return engagement_metrics
            
        # Calculate overall engagement rate
        total_interactions = engagement_data.get('total_interactions', 0)
        total_followers = engagement_data.get('follower_count', 1)  # Avoid division by zero
        engagement_metrics['overall_engagement_rate'] = (total_interactions / total_followers) * 100
        
        # Process engagement by type
        engagement_metrics['engagement_by_type'] = {
            'likes': engagement_data.get('likes_rate', 0),
            'retweets': engagement_data.get('retweet_rate', 0),
            'replies': engagement_data.get('reply_rate', 0),
            'quotes': engagement_data.get('quote_rate', 0)
        }
        
        # Process engagement trends
        engagement_metrics['engagement_trends'] = engagement_data.get('trends', {})
        
        # Process conversation metrics
        engagement_metrics['conversation_metrics'] = {
            'reply_rate': engagement_data.get('reply_rate', 0),
            'mentions_received': engagement_data.get('mentions_received', 0),
            'conversation_rate': engagement_data.get('conversation_rate', 0)
        }
        
        return engagement_metrics
        
    def _analyze_twitter_interests(self, interest_data: Dict) -> Dict:
        """Process Twitter audience interests"""
        interest_metrics = {
            'topics': {},
            'hashtags': {},
            'mentioned_accounts': {},
            'interest_clusters': {}
        }
        
        if not interest_data:
            return interest_metrics
            
        # Process topics of interest
        topics = interest_data.get('topics', {})
        total_topics = sum(topics.values()) if topics else 0
        interest_metrics['topics'] = {
            topic: (count/total_topics)*100 if total_topics else 0
            for topic, count in topics.items()
        }
        
        # Process hashtag usage
        interest_metrics['hashtags'] = interest_data.get('hashtags', {})
        
        # Process mentioned accounts
        interest_metrics['mentioned_accounts'] = interest_data.get('mentions', {})
        
        # Process interest clusters
        interest_metrics['interest_clusters'] = self._process_interest_clusters(
            interest_data.get('clusters', {})
        )
        
        return interest_metrics
        
    def _process_interest_clusters(self, cluster_data: Dict) -> Dict:
        """Process audience interest clusters"""
        clusters = {}
        
        for cluster_name, cluster_info in cluster_data.items():
            clusters[cluster_name] = {
                'size': cluster_info.get('size', 0),
                'main_topics': cluster_info.get('topics', []),
                'engagement_rate': cluster_info.get('engagement_rate', 0),
                'growth_rate': cluster_info.get('growth_rate', 0)
            }
            
        return clusters
        
    def _generate_insights_summary(self, insights_data: Dict) -> Dict:
        """Generate a summary of key insights"""
        follower_data = insights_data.get('follower_data', {})
        engagement_data = insights_data.get('engagement_data', {})
        
        total_followers = follower_data.get('total_followers', 0)
        engagement_rate = engagement_data.get('overall_engagement_rate', 0)
        
        return {
            'total_audience': total_followers,
            'engagement_health': self._calculate_engagement_health(engagement_rate),
            'audience_segments': self._identify_audience_segments(insights_data),
            'collection_timestamp': insights_data.get('collected_at'),
            'data_quality': self._assess_data_quality(insights_data)
        }
        
    def _calculate_engagement_health(self, engagement_rate: float) -> str:
        """Calculate engagement health status"""
        if engagement_rate >= 3.0:
            return 'excellent'
        elif engagement_rate >= 1.5:
            return 'good'
        elif engagement_rate >= 0.5:
            return 'average'
        else:
            return 'needs improvement'
            
    def _identify_audience_segments(self, insights_data: Dict) -> List[Dict]:
        """Identify key audience segments based on behavior and interests"""
        segments = []
        interest_data = insights_data.get('interest_data', {})
        engagement_data = insights_data.get('engagement_data', {})
        
        if interest_data and engagement_data:
            # Process interest-based segments
            for cluster, info in interest_data.get('clusters', {}).items():
                segments.append({
                    'name': cluster,
                    'size': info.get('size', 0),
                    'engagement_rate': info.get('engagement_rate', 0),
                    'key_interests': info.get('topics', [])[:3]
                })
            
            # Process engagement-based segments
            engagement_levels = {
                'high_engagement': engagement_data.get('high_engagement_users', 0),
                'medium_engagement': engagement_data.get('medium_engagement_users', 0),
                'low_engagement': engagement_data.get('low_engagement_users', 0)
            }
            
            for level, count in engagement_levels.items():
                segments.append({
                    'name': level,
                    'size': count,
                    'type': 'engagement_based'
                })
                
        return segments
        
    def _assess_data_quality(self, insights_data: Dict) -> Dict:
        """Assess the quality and completeness of the insights data"""
        expected_keys = ['follower_data', 'activity_data', 'engagement_data', 'interest_data']
        actual_keys = list(insights_data.keys())
        
        completeness = len([k for k in expected_keys if k in actual_keys]) / len(expected_keys)
        
        return {
            'completeness_score': completeness,
            'missing_metrics': [k for k in expected_keys if k not in actual_keys],
            'available_metrics': actual_keys
        }
