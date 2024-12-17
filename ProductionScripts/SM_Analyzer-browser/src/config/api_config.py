"""
API Configuration Module
Handles API credentials and configuration for various social media platforms
"""

import os
from typing import Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class APIConfig:
    @staticmethod
    def get_twitter_config() -> Dict:
        """Get Twitter API credentials"""
        return {
            'api_key': os.getenv('TWITTER_API_KEY'),
            'api_secret': os.getenv('TWITTER_API_SECRET'),
            'access_token': os.getenv('TWITTER_ACCESS_TOKEN'),
            'access_token_secret': os.getenv('TWITTER_ACCESS_TOKEN_SECRET'),
            'bearer_token': os.getenv('TWITTER_BEARER_TOKEN')
        }
    
    @staticmethod
    def get_instagram_config() -> Dict:
        """Get Instagram Graph API credentials"""
        return {
            'app_id': os.getenv('INSTAGRAM_APP_ID'),
            'app_secret': os.getenv('INSTAGRAM_APP_SECRET'),
            'access_token': os.getenv('INSTAGRAM_ACCESS_TOKEN'),
            'business_account_id': os.getenv('INSTAGRAM_BUSINESS_ACCOUNT_ID')
        }
    
    @staticmethod
    def get_tiktok_config() -> Dict:
        """Get TikTok API credentials"""
        return {
            'app_id': os.getenv('TIKTOK_APP_ID'),
            'app_secret': os.getenv('TIKTOK_APP_SECRET'),
            'access_token': os.getenv('TIKTOK_ACCESS_TOKEN'),
            'open_id': os.getenv('TIKTOK_OPEN_ID')
        }
    
    @staticmethod
    def get_youtube_config() -> Dict:
        """Get YouTube API credentials"""
        return {
            'api_key': os.getenv('YOUTUBE_API_KEY'),
            'client_id': os.getenv('YOUTUBE_CLIENT_ID'),
            'client_secret': os.getenv('YOUTUBE_CLIENT_SECRET'),
            'refresh_token': os.getenv('YOUTUBE_REFRESH_TOKEN')
        }
    
    @staticmethod
    def validate_credentials(config: Dict) -> bool:
        """Validate that all required credentials are present"""
        return all(value is not None and value != '' for value in config.values())
