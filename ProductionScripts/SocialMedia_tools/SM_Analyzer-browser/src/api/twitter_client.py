"""
Twitter API Client
Handles interactions with Twitter API v2
"""

import tweepy
from typing import Dict, List, Optional
from src.config.api_config import APIConfig

class TwitterClient:
    def __init__(self):
        config = APIConfig.get_twitter_config()
        if not APIConfig.validate_credentials(config):
            raise ValueError("Invalid Twitter API credentials")
            
        self.client = tweepy.Client(
            bearer_token=config['bearer_token'],
            consumer_key=config['api_key'],
            consumer_secret=config['api_secret'],
            access_token=config['access_token'],
            access_token_secret=config['access_token_secret']
        )
        
    def get_user_tweets(self, user_id: str, max_results: int = 100) -> List[Dict]:
        """Get tweets for a specific user"""
        try:
            tweets = self.client.get_users_tweets(
                user_id,
                max_results=max_results,
                tweet_fields=['created_at', 'public_metrics', 'text']
            )
            
            return [{
                'id': tweet.id,
                'text': tweet.text,
                'created_at': tweet.created_at,
                'metrics': tweet.public_metrics
            } for tweet in tweets.data] if tweets.data else []
            
        except Exception as e:
            print(f"Error fetching tweets: {str(e)}")
            return []
            
    def get_tweet_metrics(self, tweet_ids: List[str]) -> List[Dict]:
        """Get engagement metrics for specific tweets"""
        try:
            tweets = self.client.get_tweets(
                tweet_ids,
                tweet_fields=['public_metrics', 'created_at']
            )
            
            return [{
                'id': tweet.id,
                'created_at': tweet.created_at,
                'metrics': tweet.public_metrics
            } for tweet in tweets.data] if tweets.data else []
            
        except Exception as e:
            print(f"Error fetching tweet metrics: {str(e)}")
            return []
