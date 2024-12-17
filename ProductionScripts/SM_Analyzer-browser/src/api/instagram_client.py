"""
Instagram Graph API Client
Handles interactions with Instagram Graph API
"""

import requests
from typing import Dict, List, Optional
from ..config.api_config import APIConfig

class InstagramClient:
    def __init__(self):
        config = APIConfig.get_instagram_config()
        if not APIConfig.validate_credentials(config):
            raise ValueError("Invalid Instagram API credentials")
            
        self.access_token = config['access_token']
        self.business_account_id = config['business_account_id']
        self.base_url = 'https://graph.facebook.com/v18.0'
        
    def get_media_insights(self, media_id: str) -> Dict:
        """Get insights for a specific media post"""
        try:
            url = f"{self.base_url}/{media_id}/insights"
            params = {
                'metric': 'engagement,impressions,reach,saved',
                'access_token': self.access_token
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            print(f"Error fetching media insights: {str(e)}")
            return {}
            
    def get_account_insights(self, period: str = 'day', metrics: List[str] = None) -> Dict:
        """Get account-level insights"""
        if metrics is None:
            metrics = ['reach', 'impressions', 'profile_views', 'follower_count']
            
        try:
            url = f"{self.base_url}/{self.business_account_id}/insights"
            params = {
                'metric': ','.join(metrics),
                'period': period,
                'access_token': self.access_token
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            print(f"Error fetching account insights: {str(e)}")
            return {}
            
    def get_media_list(self, limit: int = 25) -> List[Dict]:
        """Get recent media posts"""
        try:
            url = f"{self.base_url}/{self.business_account_id}/media"
            params = {
                'fields': 'id,caption,media_type,timestamp,like_count,comments_count',
                'limit': limit,
                'access_token': self.access_token
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json().get('data', [])
        except Exception as e:
            print(f"Error fetching media list: {str(e)}")
            return []
