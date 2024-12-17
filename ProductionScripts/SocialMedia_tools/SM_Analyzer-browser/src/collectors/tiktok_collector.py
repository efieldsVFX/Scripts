"""
TikTok data collector for EDGLRD analytics.
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import requests
import logging
import pandas as pd
from .base_collector import BaseCollector
from utils.test_data import TIKTOK_TEST_DATA

logger = logging.getLogger(__name__)

class TikTokCollector(BaseCollector):
    """Collector for TikTok Business Account data."""
    
    def __init__(self, auth_config: Dict):
        """Initialize TikTok collector with Business API authentication."""
        super().__init__(auth_config.get('api_key', ''), auth_config.get('api_secret', ''))
        try:
            self.access_token = auth_config['access_token']
            self.business_id = auth_config['business_id']
            self.base_url = "https://business-api.tiktok.com/open_api/v1.3"
            self.using_test_data = False
            logger.info("TikTok collector initialized with API keys")
        except KeyError as e:
            self.access_token = None
            self.business_id = None
            self.using_test_data = True
            logger.warning(f"TikTok API initialization failed, using test data: {str(e)}")
        
    def authenticate(self) -> bool:
        """Authenticate with the TikTok API"""
        if self.using_test_data:
            return True
            
        try:
            headers = {
                'Access-Token': self.access_token,
                'Content-Type': 'application/json'
            }
            response = requests.get(
                f"{self.base_url}/business/get_account/",
                headers=headers,
                params={'business_id': self.business_id}
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            return False

    def collect_profile_data(self, profile_id: str = None) -> pd.DataFrame:
        """Collect profile/account data"""
        if self.using_test_data:
            logger.info("Using test data for profile data")
            return pd.DataFrame([{
                'id': 'test_profile',
                'username': 'test_account',
                'followers': 10000,
                'following': 500,
                'likes': 50000,
                'video_count': 100,
                'platform': 'tiktok'
            }])

        try:
            headers = {
                'Access-Token': self.access_token,
                'Content-Type': 'application/json'
            }
            response = requests.get(
                f"{self.base_url}/business/get_profile/",
                headers=headers,
                params={'business_id': self.business_id}
            )
            if response.status_code == 200:
                data = response.json()['data']
                return pd.DataFrame([{
                    'id': data['id'],
                    'username': data['username'],
                    'followers': data['follower_count'],
                    'following': data['following_count'],
                    'likes': data['likes_count'],
                    'video_count': data['video_count'],
                    'platform': 'tiktok'
                }])
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"Error collecting profile data: {str(e)}")
            return pd.DataFrame()

    def collect_content_data(self, profile_id: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Collect content/posts data"""
        if self.using_test_data:
            logger.info("Using test data for content data")
            videos = []
            for video in TIKTOK_TEST_DATA['videos']:
                if start_date.timestamp() <= video['create_time'] <= end_date.timestamp():
                    videos.append({
                        'id': video['id'],
                        'title': video['title'],
                        'created_at': datetime.fromtimestamp(video['create_time']),
                        'views': video['metrics']['video_views'],
                        'likes': video['metrics']['likes'],
                        'comments': video['metrics']['comments'],
                        'shares': video['metrics']['shares'],
                        'platform': 'tiktok'
                    })
            return pd.DataFrame(videos)

        try:
            videos = self.get_video_performance()
            video_data = []
            for video in videos:
                created_time = datetime.fromtimestamp(video['create_time'])
                if start_date <= created_time <= end_date:
                    video_data.append({
                        'id': video['id'],
                        'title': video['title'],
                        'created_at': created_time,
                        'views': video['metrics']['video_views'],
                        'likes': video['metrics']['likes'],
                        'comments': video['metrics']['comments'],
                        'shares': video['metrics']['shares'],
                        'platform': 'tiktok'
                    })
            return pd.DataFrame(video_data)
        except Exception as e:
            logger.error(f"Error collecting content data: {str(e)}")
            return pd.DataFrame()

    def collect_audience_data(self, profile_id: str) -> pd.DataFrame:
        """Collect audience demographics and insights"""
        if self.using_test_data:
            logger.info("Using test data for audience data")
            demographics = TIKTOK_TEST_DATA['audience']['demographics']
            audience_data = []
            
            # Process age groups
            for age_group, percentage in demographics['age_groups'].items():
                audience_data.append({
                    'type': 'age_group',
                    'category': age_group,
                    'percentage': percentage,
                    'platform': 'tiktok'
                })
            
            # Process gender distribution
            for gender, percentage in demographics['gender'].items():
                audience_data.append({
                    'type': 'gender',
                    'category': gender,
                    'percentage': percentage,
                    'platform': 'tiktok'
                })
            
            return pd.DataFrame(audience_data)

        try:
            demographics = self.get_audience_demographics()
            audience_data = []
            
            # Process actual API response similar to test data
            for category, data in demographics.items():
                for subcategory, value in data.items():
                    audience_data.append({
                        'type': category,
                        'category': subcategory,
                        'percentage': value,
                        'platform': 'tiktok'
                    })
            
            return pd.DataFrame(audience_data)
        except Exception as e:
            logger.error(f"Error collecting audience data: {str(e)}")
            return pd.DataFrame()

    def collect_engagement_data(self, content_ids: List[str]) -> pd.DataFrame:
        """Collect engagement metrics for content"""
        if self.using_test_data:
            logger.info("Using test data for engagement data")
            engagement_data = []
            for video in TIKTOK_TEST_DATA['videos']:
                if video['id'] in content_ids:
                    metrics = video['metrics']
                    engagement_data.append({
                        'content_id': video['id'],
                        'engagement_type': 'views',
                        'count': metrics['video_views'],
                        'platform': 'tiktok'
                    })
                    engagement_data.append({
                        'content_id': video['id'],
                        'engagement_type': 'likes',
                        'count': metrics['likes'],
                        'platform': 'tiktok'
                    })
                    engagement_data.append({
                        'content_id': video['id'],
                        'engagement_type': 'comments',
                        'count': metrics['comments'],
                        'platform': 'tiktok'
                    })
                    engagement_data.append({
                        'content_id': video['id'],
                        'engagement_type': 'shares',
                        'count': metrics['shares'],
                        'platform': 'tiktok'
                    })
            return pd.DataFrame(engagement_data)

        try:
            engagement_data = []
            for video_id in content_ids:
                metrics = self.get_video_metrics(video_id)
                if metrics:
                    for metric_type, value in metrics.items():
                        engagement_data.append({
                            'content_id': video_id,
                            'engagement_type': metric_type,
                            'count': value,
                            'platform': 'tiktok'
                        })
            return pd.DataFrame(engagement_data)
        except Exception as e:
            logger.error(f"Error collecting engagement data: {str(e)}")
            return pd.DataFrame()

    def get_account_insights(self) -> Dict:
        """Get comprehensive account insights."""
        try:
            metrics = [
                'profile_views',
                'follower_count',
                'following_count',
                'likes_count',
                'video_views',
                'comment_count',
                'share_count'
            ]
            
            headers = {
                'Access-Token': self.access_token,
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                f"{self.base_url}/business/get_account_insights/",
                headers=headers,
                params={'business_id': self.business_id}
            )
            
            if response.status_code == 200:
                return response.json()['data']
            else:
                logger.error(f"Error getting account insights: {response.text}")
                return {}
                
        except Exception as e:
            logger.error(f"Error getting account insights: {str(e)}")
            return {}
            
    def get_audience_demographics(self) -> Dict:
        """Get detailed audience demographics."""
        try:
            metrics = [
                'audience_countries',
                'audience_gender',
                'audience_ages',
                'audience_interests',
                'audience_devices'
            ]
            
            headers = {
                'Access-Token': self.access_token,
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                f"{self.base_url}/business/get_audience_demographics/",
                headers=headers,
                params={'business_id': self.business_id}
            )
            
            if response.status_code == 200:
                return response.json()['data']
            else:
                logger.error(f"Error getting audience demographics: {response.text}")
                return {}
                
        except Exception as e:
            logger.error(f"Error getting audience demographics: {str(e)}")
            return {}
            
    def get_video_performance(self, days: int = 30) -> List[Dict]:
        """Get detailed performance metrics for recent videos."""
        if self.using_test_data:
            logger.info("Using test data for video performance")
            return TIKTOK_TEST_DATA['videos']

        try:
            headers = {
                'Access-Token': self.access_token,
                'Content-Type': 'application/json'
            }
            
            # Get video list
            videos_response = requests.get(
                f"{self.base_url}/business/get_videos/",
                headers=headers,
                params={
                    'business_id': self.business_id,
                    'fields': ['id', 'title', 'create_time', 'share_url', 'cover_image_url']
                }
            )
            
            if videos_response.status_code != 200:
                logger.error(f"Error getting videos list: {videos_response.text}")
                return []
                
            videos = videos_response.json()['data']['videos']
            start_time = datetime.now() - timedelta(days=days)
            
            performance_data = []
            for video in videos:
                video_time = datetime.fromtimestamp(video['create_time'])
                if video_time < start_time:
                    continue
                    
                # Get metrics for each video
                metrics_response = requests.get(
                    f"{self.base_url}/business/get_video_metrics/",
                    headers=headers,
                    params={
                        'business_id': self.business_id,
                        'video_id': video['id'],
                        'metrics': [
                            'video_views',
                            'play_duration',
                            'likes',
                            'comments',
                            'shares',
                            'reach',
                            'total_time_watched',
                            'average_watch_time',
                            'completion_rate'
                        ]
                    }
                )
                
                if metrics_response.status_code == 200:
                    video['metrics'] = metrics_response.json()['data']
                    performance_data.append(video)
                    
            return performance_data
                
        except Exception as e:
            logger.error(f"Error getting video performance: {str(e)}")
            return []
            
    def get_video_metrics(self, video_id: str) -> Dict:
        """Get metrics for a specific video."""
        try:
            headers = {
                'Access-Token': self.access_token,
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                f"{self.base_url}/business/get_video_metrics/",
                headers=headers,
                params={
                    'business_id': self.business_id,
                    'video_id': video_id,
                    'metrics': [
                        'video_views',
                        'play_duration',
                        'likes',
                        'comments',
                        'shares',
                        'reach',
                        'total_time_watched',
                        'average_watch_time',
                        'completion_rate'
                    ]
                }
            )
            
            if response.status_code == 200:
                return response.json()['data']
            else:
                logger.error(f"Error getting video metrics: {response.text}")
                return {}
                
        except Exception as e:
            logger.error(f"Error getting video metrics: {str(e)}")
            return {}
            
    def get_hashtag_analytics(self, hashtags: List[str]) -> Dict:
        """Get analytics for specific hashtags."""
        try:
            headers = {
                'Access-Token': self.access_token,
                'Content-Type': 'application/json'
            }
            
            hashtag_data = {}
            for hashtag in hashtags:
                response = requests.get(
                    f"{self.base_url}/business/get_hashtag_analytics/",
                    headers=headers,
                    params={
                        'business_id': self.business_id,
                        'hashtag': hashtag
                    }
                )
                
                if response.status_code == 200:
                    hashtag_data[hashtag] = response.json()['data']
                    
            return hashtag_data
                
        except Exception as e:
            logger.error(f"Error getting hashtag analytics: {str(e)}")
            return {}
            
    def get_live_streaming_metrics(self) -> Dict:
        """Get metrics for live streaming performance."""
        try:
            headers = {
                'Access-Token': self.access_token,
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                f"{self.base_url}/business/get_live_metrics/",
                headers=headers,
                params={
                    'business_id': self.business_id,
                    'metrics': [
                        'total_viewers',
                        'max_viewers',
                        'average_watch_time',
                        'likes',
                        'comments',
                        'shares',
                        'diamonds_received'
                    ]
                }
            )
            
            if response.status_code == 200:
                return response.json()['data']
            else:
                logger.error(f"Error getting live streaming metrics: {response.text}")
                return {}
                
        except Exception as e:
            logger.error(f"Error getting live streaming metrics: {str(e)}")
            return {}
            
    def get_shopping_metrics(self) -> Dict:
        """Get metrics for shopping features."""
        try:
            headers = {
                'Access-Token': self.access_token,
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                f"{self.base_url}/business/get_shopping_metrics/",
                headers=headers,
                params={
                    'business_id': self.business_id,
                    'metrics': [
                        'product_views',
                        'product_clicks',
                        'product_purchases',
                        'total_sales',
                        'conversion_rate'
                    ]
                }
            )
            
            if response.status_code == 200:
                return response.json()['data']
            else:
                logger.error(f"Error getting shopping metrics: {response.text}")
                return {}
                
        except Exception as e:
            logger.error(f"Error getting shopping metrics: {str(e)}")
            return {}