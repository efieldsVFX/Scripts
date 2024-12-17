"""
Instagram Audience Analytics Module
Handles Instagram-specific audience insights and analysis
"""

from typing import Dict, List
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from .audience_analyzer import AudienceAnalyzer
import logging

class InstagramAudienceAnalyzer(AudienceAnalyzer):
    """Analyzer for Instagram audience insights"""

    def __init__(self):
        """Initialize Instagram audience analyzer"""
        super().__init__('instagram')
        self.logger = logging.getLogger(__name__)

    def process_insights(self, insights_data: Dict) -> Dict:
        """
        Process raw Instagram insights data into analyzed metrics
        
        Args:
            insights_data: Dict containing Instagram audience insights
            
        Returns:
            Dict containing processed analytics
        """
        try:
            if not insights_data:
                return {}

            analysis = {
                'demographics': self.analyze_demographics(insights_data.get('audience_demographics', {})),
                'active_times': self.analyze_active_times(insights_data.get('audience_activity', {})),
                'interests': self.analyze_interests(insights_data.get('audience_interests', {})),
                'age_interactions': self.analyze_age_interactions(insights_data.get('age_insights', {})),
                'follower_growth': self.analyze_follower_growth(insights_data.get('follower_metrics', {})),
                'story_insights': self._analyze_story_insights(insights_data.get('story_metrics', {})),
                'reel_insights': self._analyze_reel_insights(insights_data.get('reel_metrics', {})),
                'shopping_insights': self._analyze_shopping_insights(insights_data.get('shopping_metrics', {}))
            }

            return analysis
        except Exception as e:
            self.logger.error(f"Error processing Instagram insights: {str(e)}")
            return {}

    def analyze_demographics(self, demographics: Dict) -> Dict:
        """Process Instagram demographic data"""
        gender_age = demographics.get('gender_age', {})
        total_followers = demographics.get('total_followers', 0)
        
        # Split gender-age combinations and calculate percentages
        gender_dist = {'M': 0, 'F': 0}
        age_dist = {'13-17': 0, '18-24': 0, '25-34': 0, '35-44': 0, '45-54': 0, '55+': 0}
        
        for key, value in gender_age.items():
            gender = key[0]  # First character is gender (M/F)
            age_range = key[2:]  # Rest is age range
            gender_dist[gender] += value
            age_dist[age_range] += value
            
        # Calculate percentages
        gender_pct = {k: (v/total_followers)*100 if total_followers else 0 
                     for k, v in gender_dist.items()}
        age_pct = {k: (v/total_followers)*100 if total_followers else 0 
                  for k, v in age_dist.items()}
        
        return {
            'gender_distribution': gender_pct,
            'age_distribution': age_pct,
            'gender_age_matrix': gender_age,
            'total_followers': total_followers
        }

    def analyze_active_times(self, activity_data: Dict) -> Dict:
        """Process Instagram audience activity patterns"""
        hourly_activity = activity_data.get('hourly', {})
        
        # Convert hourly data to percentage of total activity
        total_activity = sum(hourly_activity.values()) if hourly_activity else 0
        hourly_pct = {str(k): (v/total_activity)*100 if total_activity else 0 
                     for k, v in hourly_activity.items()}
        
        # Find peak hours (top 3 most active hours)
        peak_hours = sorted(hourly_pct.items(), key=lambda x: x[1], reverse=True)[:3]
        
        return {
            'hourly_distribution': hourly_pct,
            'peak_hours': [hour for hour, _ in peak_hours],
            'peak_activity_times': {hour: pct for hour, pct in peak_hours}
        }

    def analyze_interests(self, interests_data: Dict) -> Dict:
        """Process Instagram audience interests"""
        interests = interests_data.get('interests', {})
        
        # Get top interests
        top_interests = dict(sorted(interests.items(), key=lambda x: x[1], reverse=True)[:10])
        
        return {
            'top_interests': top_interests
        }

    def analyze_age_interactions(self, age_data: Dict) -> Dict:
        """Process Instagram audience age interactions"""
        age_interactions = age_data.get('age_interactions', {})
        
        # Get top age interactions
        top_age_interactions = dict(sorted(age_interactions.items(), key=lambda x: x[1], reverse=True)[:10])
        
        return {
            'top_age_interactions': top_age_interactions
        }

    def analyze_follower_growth(self, follower_data: Dict) -> Dict:
        """Process Instagram follower growth"""
        follower_growth = follower_data.get('follower_growth', {})
        
        # Get follower growth rate
        follower_growth_rate = follower_growth.get('growth_rate', 0)
        
        return {
            'follower_growth_rate': follower_growth_rate
        }

    def _analyze_story_insights(self, story_data: Dict) -> Dict:
        """Analyze Instagram Story metrics"""
        try:
            story_insights = {
                'views': {
                    'total_views': story_data.get('total_views', 0),
                    'unique_viewers': story_data.get('unique_viewers', 0),
                    'completion_rate': story_data.get('completion_rate', 0),
                    'exit_rate': story_data.get('exit_rate', 0)
                },
                'interactions': {
                    'replies': story_data.get('replies', 0),
                    'sticker_taps': story_data.get('sticker_taps', 0),
                    'link_clicks': story_data.get('link_clicks', 0),
                    'profile_visits': story_data.get('profile_visits', 0)
                },
                'performance': {
                    'best_performing_stories': story_data.get('top_stories', []),
                    'optimal_posting_times': story_data.get('optimal_times', []),
                    'sticker_performance': story_data.get('sticker_performance', {})
                }
            }
            return story_insights
        except Exception as e:
            self.logger.error(f"Error analyzing story insights: {str(e)}")
            return {}

    def _analyze_reel_insights(self, reel_data: Dict) -> Dict:
        """Analyze Instagram Reels metrics"""
        try:
            reel_insights = {
                'views': {
                    'total_plays': reel_data.get('total_plays', 0),
                    'unique_viewers': reel_data.get('unique_viewers', 0),
                    'average_watch_time': reel_data.get('avg_watch_time', 0),
                    'completion_rate': reel_data.get('completion_rate', 0)
                },
                'engagement': {
                    'likes': reel_data.get('likes', 0),
                    'comments': reel_data.get('comments', 0),
                    'shares': reel_data.get('shares', 0),
                    'saves': reel_data.get('saves', 0)
                },
                'reach': {
                    'accounts_reached': reel_data.get('reach', 0),
                    'non_follower_reach': reel_data.get('non_follower_reach', 0),
                    'reach_rate': reel_data.get('reach_rate', 0)
                },
                'performance': {
                    'top_performing_reels': reel_data.get('top_reels', []),
                    'optimal_posting_times': reel_data.get('optimal_times', []),
                    'audio_performance': reel_data.get('audio_performance', {})
                }
            }
            return reel_insights
        except Exception as e:
            self.logger.error(f"Error analyzing reel insights: {str(e)}")
            return {}

    def _analyze_shopping_insights(self, shopping_data: Dict) -> Dict:
        """Analyze Instagram Shopping metrics"""
        try:
            shopping_insights = {
                'product_views': {
                    'total_views': shopping_data.get('product_views', 0),
                    'unique_viewers': shopping_data.get('unique_viewers', 0),
                    'product_view_rate': shopping_data.get('view_rate', 0)
                },
                'product_interactions': {
                    'product_clicks': shopping_data.get('product_clicks', 0),
                    'product_saves': shopping_data.get('product_saves', 0),
                    'product_shares': shopping_data.get('product_shares', 0)
                },
                'sales': {
                    'total_sales': shopping_data.get('total_sales', 0),
                    'conversion_rate': shopping_data.get('conversion_rate', 0),
                    'average_order_value': shopping_data.get('avg_order_value', 0)
                },
                'performance': {
                    'top_products': shopping_data.get('top_products', []),
                    'best_selling_categories': shopping_data.get('top_categories', []),
                    'shopping_tags_performance': shopping_data.get('tag_performance', {})
                }
            }
            return shopping_insights
        except Exception as e:
            self.logger.error(f"Error analyzing shopping insights: {str(e)}")
            return {}

    def _generate_insights_summary(self, insights_data: Dict) -> Dict:
        """Generate a summary of key insights"""
        demographics = insights_data.get('demographics', {})
        locations = insights_data.get('locations', {})
        
        total_followers = demographics.get('total_followers', 0)
        countries_reached = len(locations.get('countries', {}))
        
        return {
            'total_audience': total_followers,
            'geographic_reach': countries_reached,
            'collection_timestamp': insights_data.get('collected_at'),
            'data_quality': self._assess_data_quality(insights_data)
        }
        
    def _assess_data_quality(self, insights_data: Dict) -> Dict:
        """Assess the quality and completeness of the insights data"""
        expected_keys = ['demographics', 'active_times', 'locations']
        actual_keys = list(insights_data.keys())
        
        completeness = len([k for k in expected_keys if k in actual_keys]) / len(expected_keys)
        
        return {
            'completeness_score': completeness,
            'missing_metrics': [k for k in expected_keys if k not in actual_keys],
            'available_metrics': actual_keys
        }
