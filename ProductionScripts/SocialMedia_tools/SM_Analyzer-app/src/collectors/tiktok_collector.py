"""
TikTok Data Collector
Handles collection of TikTok videos and comments using TikTok API.
"""

import requests
from typing import List, Dict, Optional
import pandas as pd
from datetime import datetime
from src import logger, API_CONFIG

class TikTokCollector:
    def __init__(self):
        """Initialize TikTok API client"""
        self.api_key = API_CONFIG['tiktok']['api_key']
        self.base_url = "https://open-api.tiktok.com/v2"
        logger.info("TikTok collector initialized")

    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """
        Make a request to the TikTok API
        
        Args:
            endpoint (str): API endpoint
            params (Dict): Query parameters
            
        Returns:
            Dict: API response
        """
        if params is None:
            params = {}
        params['access_token'] = self.api_key
        
        url = f"{self.base_url}/{endpoint}"
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def collect_trending_videos(self, limit: int = 50) -> pd.DataFrame:
        """
        Collect trending videos from TikTok
        
        Args:
            limit (int): Maximum number of videos to collect
            
        Returns:
            pd.DataFrame: Collected videos data
        """
        try:
            videos = []
            params = {
                'count': min(limit, 50)  # TikTok API usually limits per request
            }

            response = self._make_request("video/list/", params)
            
            for video in response.get('videos', []):
                videos.append({
                    'id': video['id'],
                    'text': video.get('description', ''),
                    'created_at': datetime.fromtimestamp(video['create_time']),
                    'likes': video.get('like_count', 0),
                    'comments': video.get('comment_count', 0),
                    'shares': video.get('share_count', 0),
                    'views': video.get('view_count', 0),
                    'video_url': video.get('video_url'),
                    'platform': 'tiktok'
                })

            df = pd.DataFrame(videos)
            logger.info(f"Collected {len(df)} TikTok videos")
            return df

        except Exception as e:
            logger.error(f"Error collecting TikTok videos: {str(e)}")
            raise

    def collect_video_comments(self, video_id: str, limit: int = 50) -> pd.DataFrame:
        """
        Collect comments from a specific video
        
        Args:
            video_id (str): TikTok video ID
            limit (int): Maximum number of comments to collect
            
        Returns:
            pd.DataFrame: Collected comments data
        """
        try:
            comments = []
            params = {
                'video_id': video_id,
                'count': min(limit, 50)
            }

            response = self._make_request("comment/list/", params)
            
            for comment in response.get('comments', []):
                comments.append({
                    'id': comment['id'],
                    'text': comment['text'],
                    'created_at': datetime.fromtimestamp(comment['create_time']),
                    'likes': comment.get('like_count', 0),
                    'username': comment.get('user', {}).get('username'),
                    'platform': 'tiktok',
                    'video_id': video_id
                })

            df = pd.DataFrame(comments)
            logger.info(f"Collected {len(df)} comments from TikTok video {video_id}")
            return df

        except Exception as e:
            logger.error(f"Error collecting TikTok comments: {str(e)}")
            raise 