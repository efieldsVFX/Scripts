"""
Social Media Data Collector
Collects and analyzes data from various social media platforms using official APIs
"""

import os
import logging
import pandas as pd
import tweepy
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import asyncio
import aiohttp
from dotenv import load_dotenv

# Facebook Business SDK imports
from facebook_business import FacebookAdsApi
from facebook_business.adobjects.page import Page
from facebook_business.adobjects.iguser import IGUser
from facebook_business.adobjects.igmedia import IGMedia
from facebook_business.adobjects.igcomment import IGComment

import requests
import json
import hmac
import hashlib
import time
import numpy as np
from transformers import pipeline

class TikTokAPI:
    def __init__(self):
        self.access_token = os.getenv('TIKTOK_ACCESS_TOKEN')
        self.client_key = os.getenv('TIKTOK_CLIENT_KEY')
        self.client_secret = os.getenv('TIKTOK_CLIENT_SECRET')
        self.base_url = 'https://open.tiktokapis.com/v2'
        
    def _generate_signature(self, params):
        """Generate signature for TikTok API request"""
        sorted_params = sorted(params.items())
        param_str = ''.join([f"{k}{v}" for k, v in sorted_params])
        signature = hmac.new(
            self.client_secret.encode(),
            param_str.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature
        
    def get_user_info(self):
        """Get TikTok user information"""
        endpoint = f"{self.base_url}/user/info/"
        timestamp = str(int(time.time()))
        
        params = {
            'access_token': self.access_token,
            'client_key': self.client_key,
            'timestamp': timestamp
        }
        
        params['sign'] = self._generate_signature(params)
        
        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching TikTok user info: {e}")
            return None
            
    def get_user_videos(self, max_count=20):
        """Get user's TikTok videos"""
        endpoint = f"{self.base_url}/video/list/"
        timestamp = str(int(time.time()))
        
        params = {
            'access_token': self.access_token,
            'client_key': self.client_key,
            'timestamp': timestamp,
            'max_count': max_count
        }
        
        params['sign'] = self._generate_signature(params)
        
        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching TikTok videos: {e}")
            return None
            
    def get_video_metrics(self, video_ids):
        """Get metrics for specific TikTok videos"""
        endpoint = f"{self.base_url}/video/query/"
        timestamp = str(int(time.time()))
        
        params = {
            'access_token': self.access_token,
            'client_key': self.client_key,
            'timestamp': timestamp,
            'video_ids': ','.join(video_ids)
        }
        
        params['sign'] = self._generate_signature(params)
        
        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching TikTok video metrics: {e}")
            return None

class SocialMediaCollector:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
        
        # Initialize API clients
        self._init_twitter()
        self._init_instagram()
        self._init_tiktok()

    def _init_twitter(self):
        """Initialize Twitter API v2 client"""
        try:
            self.twitter_client = tweepy.Client(
                bearer_token=os.getenv('TWITTER_BEARER_TOKEN'),
                consumer_key=os.getenv('TWITTER_API_KEY'),
                consumer_secret=os.getenv('TWITTER_API_SECRET'),
                access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
                access_token_secret=os.getenv('TWITTER_ACCESS_TOKEN_SECRET'),
                wait_on_rate_limit=True
            )
            self.logger.info("Twitter client initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Twitter client: {str(e)}")
            self.twitter_client = None

    def _init_instagram(self):
        """Initialize Instagram Graph API client"""
        try:
            FacebookAdsApi.init(
                app_id=os.getenv('FACEBOOK_APP_ID'),
                app_secret=os.getenv('FACEBOOK_APP_SECRET'),
                access_token=os.getenv('FACEBOOK_ACCESS_TOKEN')
            )
            self.instagram_user_id = os.getenv('INSTAGRAM_BUSINESS_ACCOUNT_ID')
            self.logger.info("Instagram client initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Instagram client: {str(e)}")
            self.instagram_user_id = None

    def _init_tiktok(self):
        """Initialize TikTok API credentials"""
        try:
            self.tiktok_api = TikTokAPI()
            self.logger.info("TikTok credentials loaded successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize TikTok credentials: {str(e)}")
            self.tiktok_api = None

    async def collect_twitter_data(self, query: str, days_back: int = 7) -> pd.DataFrame:
        """Collect Twitter mentions and replies using Twitter API v2"""
        if not self.twitter_client:
            self.logger.warning("Twitter client not initialized")
            return pd.DataFrame()

        try:
            start_time = datetime.utcnow() - timedelta(days=days_back)
            tweets = []
            
            # Search tweets with comprehensive metrics
            search_query = query
            if not query.startswith('@') and not query.startswith('#'):
                search_query = f"{query} -is:retweet"

            response = self.twitter_client.search_recent_tweets(
                query=search_query,
                start_time=start_time,
                tweet_fields=['created_at', 'public_metrics', 'context_annotations', 'entities'],
                user_fields=['username', 'public_metrics'],
                expansions=['author_id'],
                max_results=100
            )

            if response.data:
                users = {user.id: user for user in response.includes['users']}
                
                for tweet in response.data:
                    author = users.get(tweet.author_id)
                    tweets.append({
                        'platform': 'Twitter',
                        'text': tweet.text,
                        'created_at': tweet.created_at,
                        'author': author.username if author else None,
                        'likes': tweet.public_metrics['like_count'],
                        'retweets': tweet.public_metrics['retweet_count'],
                        'replies': tweet.public_metrics['reply_count'],
                        'impressions': tweet.public_metrics['impression_count']
                    })
            
            return pd.DataFrame(tweets)
        except Exception as e:
            self.logger.error(f"Error collecting Twitter data: {str(e)}")
            return pd.DataFrame()

    async def collect_instagram_data(self, username: str, days_back: int = 7) -> pd.DataFrame:
        """Collect Instagram comments using Instagram Graph API"""
        if not self.instagram_user_id:
            self.logger.warning("Instagram client not initialized")
            return pd.DataFrame()

        try:
            comments = []
            user = IGUser(self.instagram_user_id)
            
            # Get recent media
            media = user.get_media()
            since_date = datetime.utcnow() - timedelta(days=days_back)

            for media_obj in media:
                media_details = IGMedia(media_obj['id']).api_get(
                    fields=['timestamp', 'comments_count', 'like_count']
                )
                
                if datetime.strptime(media_details['timestamp'], '%Y-%m-%dT%H:%M:%S%z') < since_date:
                    continue

                # Get comments for each media
                media_comments = IGMedia(media_obj['id']).get_comments(
                    fields=['text', 'timestamp', 'username', 'like_count', 'replies_count']
                )

                for comment in media_comments:
                    comments.append({
                        'platform': 'Instagram',
                        'text': comment['text'],
                        'created_at': comment['timestamp'],
                        'author': comment['username'],
                        'likes': comment['like_count'],
                        'replies': comment.get('replies_count', 0)
                    })

            return pd.DataFrame(comments)
        except Exception as e:
            self.logger.error(f"Error collecting Instagram data: {str(e)}")
            return pd.DataFrame()

    async def collect_tiktok_data(self, username: str, days_back: int = 7) -> pd.DataFrame:
        """Collect TikTok data using TikTok API"""
        if not self.tiktok_api:
            self.logger.warning("TikTok credentials not initialized")
            return pd.DataFrame()

        try:
            comments = []
            user_info = self.tiktok_api.get_user_info()
            if user_info:
                user_id = user_info['data']['user']['user_id']
                
                # Get user's videos
                videos = self.tiktok_api.get_user_videos()
                if videos:
                    video_ids = [video['id'] for video in videos.get('videos', [])]
                    if video_ids:
                        video_metrics = self.tiktok_api.get_video_metrics(video_ids)
                        if video_metrics:
                            for video in video_metrics['data']['videos']:
                                comments.append({
                                    'platform': 'TikTok',
                                    'text': video['desc'],
                                    'created_at': datetime.fromtimestamp(video['create_time']),
                                    'likes': video['like_count'],
                                    'replies': video.get('comment_count', 0)
                                })

            return pd.DataFrame(comments)
        except Exception as e:
            self.logger.error(f"Error collecting TikTok data: {str(e)}")
            return pd.DataFrame()

    async def collect_all_platforms(self, query: str, username: str, days_back: int = 7) -> Dict[str, pd.DataFrame]:
        """Collect data from all platforms concurrently"""
        tasks = [
            self.collect_twitter_data(query, days_back),
            self.collect_instagram_data(username, days_back),
            self.collect_tiktok_data(username, days_back)
        ]
        
        results = await asyncio.gather(*tasks)
        return {
            'twitter': results[0],
            'instagram': results[1],
            'tiktok': results[2]
        }

    def analyze_sentiment(self, texts: List[str]) -> List[Dict]:
        """Analyze sentiment of texts using transformers"""
        try:
            results = self.sentiment_analyzer(texts)
            return results
        except Exception as e:
            self.logger.error(f"Error in sentiment analysis: {str(e)}")
            return []

    def generate_summary(self, data: Dict[str, pd.DataFrame]) -> Dict:
        """Generate summary of social media engagement and sentiment"""
        summary = {
            'total_interactions': 0,
            'sentiment_distribution': {'positive': 0, 'negative': 0, 'neutral': 0},
            'platform_breakdown': {},
            'engagement_metrics': {},
            'top_authors': {},
            'trending_sentiment': None
        }

        try:
            for platform, df in data.items():
                if df.empty:
                    continue

                # Count interactions
                platform_interactions = len(df)
                summary['total_interactions'] += platform_interactions
                summary['platform_breakdown'][platform] = platform_interactions

                # Engagement metrics
                if 'likes' in df.columns:
                    summary['engagement_metrics'][platform] = {
                        'total_likes': df['likes'].sum(),
                        'avg_likes_per_comment': df['likes'].mean(),
                        'total_replies': df['replies'].sum() if 'replies' in df.columns else 0
                    }

                # Top authors
                if 'author' in df.columns:
                    top_authors = df['author'].value_counts().head(5).to_dict()
                    summary['top_authors'][platform] = top_authors

                # Analyze sentiment
                if 'text' in df.columns:
                    sentiments = self.analyze_sentiment(df['text'].tolist())
                    for sentiment in sentiments:
                        label = sentiment['label'].lower()
                        if label == 'positive':
                            summary['sentiment_distribution']['positive'] += 1
                        elif label == 'negative':
                            summary['sentiment_distribution']['negative'] += 1
                        else:
                            summary['sentiment_distribution']['neutral'] += 1

            # Calculate trending sentiment
            if summary['total_interactions'] > 0:
                max_sentiment = max(summary['sentiment_distribution'].items(), key=lambda x: x[1])
                summary['trending_sentiment'] = max_sentiment[0]

        except Exception as e:
            self.logger.error(f"Error generating summary: {str(e)}")

        return summary

# Load environment variables
load_dotenv()
