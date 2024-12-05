"""
Twitter Data Collector
Handles collection of Twitter data using Twitter API.
"""

import tweepy
from typing import List, Dict, Optional
import pandas as pd
from datetime import datetime
import logging
import os

logger = logging.getLogger(__name__)

class TwitterCollector:
    def __init__(self):
        """Initialize Twitter API client"""
        self.client = tweepy.Client(
            bearer_token=os.getenv('TWITTER_BEARER_TOKEN'),
            consumer_key=os.getenv('TWITTER_API_KEY'),
            consumer_secret=os.getenv('TWITTER_API_SECRET'),
            wait_on_rate_limit=True
        )
        logger.info("Twitter collector initialized")

    def collect_tweets(self, query: str, max_results: int = 100) -> pd.DataFrame:
        """
        Collect tweets based on search query
        
        Args:
            query (str): Search query string
            max_results (int): Maximum number of tweets to collect
            
        Returns:
            pd.DataFrame: Collected tweets data
        """
        try:
            tweets = []
            # Search for tweets
            response = self.client.search_recent_tweets(
                query=f"{query} -is:retweet lang:en",
                max_results=max_results,
                tweet_fields=['created_at', 'public_metrics', 'lang']
            )
            
            if not response.data:
                logger.warning(f"No tweets found for query: {query}")
                return pd.DataFrame()

            # Process tweets
            for tweet in response.data:
                tweets.append({
                    'id': tweet.id,
                    'text': tweet.text,
                    'created_at': tweet.created_at,
                    'likes': tweet.public_metrics['like_count'],
                    'retweets': tweet.public_metrics['retweet_count'],
                    'replies': tweet.public_metrics['reply_count'],
                    'platform': 'twitter'
                })

            df = pd.DataFrame(tweets)
            logger.info(f"Collected {len(df)} tweets for query: {query}")
            return df

        except Exception as e:
            logger.error(f"Error collecting tweets: {str(e)}")
            raise

    def collect_user_tweets(self, username: str, max_results: int = 100) -> pd.DataFrame:
        """
        Collect tweets from a specific user
        
        Args:
            username (str): Twitter username
            max_results (int): Maximum number of tweets to collect
            
        Returns:
            pd.DataFrame: Collected tweets data
        """
        try:
            # Get user ID
            user = self.client.get_user(username=username)
            if not user.data:
                logger.warning(f"User not found: {username}")
                return pd.DataFrame()

            user_id = user.data.id
            tweets = []

            # Get user's tweets
            response = self.client.get_users_tweets(
                user_id,
                max_results=max_results,
                tweet_fields=['created_at', 'public_metrics', 'lang']
            )

            if not response.data:
                logger.warning(f"No tweets found for user: {username}")
                return pd.DataFrame()

            # Process tweets
            for tweet in response.data:
                tweets.append({
                    'id': tweet.id,
                    'text': tweet.text,
                    'created_at': tweet.created_at,
                    'likes': tweet.public_metrics['like_count'],
                    'retweets': tweet.public_metrics['retweet_count'],
                    'replies': tweet.public_metrics['reply_count'],
                    'platform': 'twitter',
                    'username': username
                })

            df = pd.DataFrame(tweets)
            logger.info(f"Collected {len(df)} tweets from user: {username}")
            return df

        except Exception as e:
            logger.error(f"Error collecting user tweets: {str(e)}")
            raise 