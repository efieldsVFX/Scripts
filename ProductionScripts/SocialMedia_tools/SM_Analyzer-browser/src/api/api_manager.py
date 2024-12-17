"""
API Manager
Unified interface for managing all social media API clients
"""

from typing import Dict, List, Optional
from .twitter_client import TwitterClient
from .instagram_client import InstagramClient
from .tiktok_client import TikTokClient
from .youtube_client import YouTubeClient

class APIManager:
    def __init__(self):
        """Initialize API clients"""
        self.clients = {}
        self._init_clients()
        
    def _init_clients(self):
        """Initialize all API clients with error handling"""
        clients = {
            'twitter': TwitterClient,
            'instagram': InstagramClient,
            'tiktok': TikTokClient,
            'youtube': YouTubeClient
        }
        
        for platform, client_class in clients.items():
            try:
                self.clients[platform] = client_class()
                print(f"Successfully initialized {platform} client")
            except Exception as e:
                print(f"Failed to initialize {platform} client: {str(e)}")
                self.clients[platform] = None
                
    def get_platform_data(self, platform: str) -> Dict:
        """Get comprehensive data for a specific platform"""
        if platform not in self.clients or self.clients[platform] is None:
            return {'error': f'Client not available for {platform}'}
            
        client = self.clients[platform]
        data = {}
        
        try:
            if platform == 'twitter':
                # Get Twitter data
                tweets = client.get_user_tweets(max_results=100)
                tweet_ids = [tweet['id'] for tweet in tweets]
                metrics = client.get_tweet_metrics(tweet_ids)
                data = {
                    'posts': tweets,
                    'metrics': metrics
                }
                
            elif platform == 'instagram':
                # Get Instagram data
                media = client.get_media_list()
                insights = []
                for item in media:
                    item_insights = client.get_media_insights(item['id'])
                    insights.append({**item, 'insights': item_insights})
                account_insights = client.get_account_insights()
                data = {
                    'posts': insights,
                    'account_insights': account_insights
                }
                
            elif platform == 'tiktok':
                # Get TikTok data
                videos = client.get_videos_list()
                video_ids = [video['id'] for video in videos]
                video_insights = client.get_video_insights(video_ids)
                account_insights = client.get_account_insights()
                data = {
                    'posts': video_insights,
                    'account_insights': account_insights
                }
                
            elif platform == 'youtube':
                # Get YouTube data
                channel_id = "YOUR_CHANNEL_ID"  # This should be configured
                videos = client.get_videos_list(channel_id)
                channel_stats = client.get_channel_stats(channel_id)
                data = {
                    'posts': videos,
                    'channel_stats': channel_stats
                }
                
        except Exception as e:
            print(f"Error fetching data for {platform}: {str(e)}")
            data = {'error': str(e)}
            
        return data
        
    def get_all_platforms_data(self) -> Dict:
        """Get data from all available platforms"""
        return {
            platform: self.get_platform_data(platform)
            for platform in self.clients.keys()
            if self.clients[platform] is not None
        }
