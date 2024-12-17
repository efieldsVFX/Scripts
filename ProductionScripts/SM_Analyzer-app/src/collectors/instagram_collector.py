"""
Instagram Data Collector
Handles collection of Instagram posts and comments using the Graph API.
"""

import requests
from typing import List, Dict, Optional
import pandas as pd
from datetime import datetime
#from instagram_private_api import Client, ClientCompatPatch
from src import logger, API_CONFIG

class InstagramCollector:
    def __init__(self, username=None, password=None):
        self.api = Client(username, password)
        self.access_token = API_CONFIG['instagram']['access_token']
        self.account_id = API_CONFIG['instagram']['account_id']
        self.base_url = "https://graph.instagram.com/v12.0"
        logger.info("Instagram collector initialized")
    
    def collect_posts(self, search_term, max_results=1000):
        # Implement Instagram hashtag/keyword search
        # Return DataFrame with columns: id, author, content, created_utc, etc.
        pass
    
    def collect_post_comments(self, post_id, limit=1000):
        # Implement Instagram comment collection
        # Return DataFrame with columns: id, author, content, created_utc, etc.
        pass

    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """
        Make a request to the Instagram Graph API
        
        Args:
            endpoint (str): API endpoint
            params (Dict): Query parameters
            
        Returns:
            Dict: API response
        """
        if params is None:
            params = {}
        params['access_token'] = self.access_token
        
        url = f"{self.base_url}/{endpoint}"
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def collect_user_posts(self, limit: int = 25) -> pd.DataFrame:
        """
        Collect posts from the authenticated user
        
        Args:
            limit (int): Maximum number of posts to collect
            
        Returns:
            pd.DataFrame: Collected posts data
        """
        try:
            posts = []
            params = {
                'fields': 'id,caption,media_type,media_url,timestamp,like_count,comments_count'
            }

            response = self._make_request(f"{self.account_id}/media", params)
            
            for post in response.get('data', [])[:limit]:
                posts.append({
                    'id': post['id'],
                    'text': post.get('caption', ''),
                    'media_type': post['media_type'],
                    'media_url': post.get('media_url'),
                    'created_at': datetime.strptime(post['timestamp'], '%Y-%m-%dT%H:%M:%S%z'),
                    'likes': post.get('like_count', 0),
                    'comments_count': post.get('comments_count', 0),
                    'platform': 'instagram'
                })

            df = pd.DataFrame(posts)
            logger.info(f"Collected {len(df)} Instagram posts")
            return df

        except Exception as e:
            logger.error(f"Error collecting Instagram posts: {str(e)}")
            raise

    def collect_post_comments(self, post_id: str, limit: int = 50) -> pd.DataFrame:
        """
        Collect comments from a specific post
        
        Args:
            post_id (str): Instagram post ID
            limit (int): Maximum number of comments to collect
            
        Returns:
            pd.DataFrame: Collected comments data
        """
        try:
            comments = []
            params = {
                'fields': 'id,text,timestamp,username'
            }

            response = self._make_request(f"{post_id}/comments", params)
            
            for comment in response.get('data', [])[:limit]:
                comments.append({
                    'id': comment['id'],
                    'text': comment['text'],
                    'created_at': datetime.strptime(comment['timestamp'], '%Y-%m-%dT%H:%M:%S%z'),
                    'username': comment['username'],
                    'platform': 'instagram',
                    'post_id': post_id
                })

            df = pd.DataFrame(comments)
            logger.info(f"Collected {len(df)} comments from Instagram post {post_id}")
            return df

        except Exception as e:
            logger.error(f"Error collecting Instagram comments: {str(e)}")
            raise 