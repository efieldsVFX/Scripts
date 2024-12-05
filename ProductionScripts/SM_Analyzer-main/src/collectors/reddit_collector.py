"""
Reddit Data Collector
Handles collection of Reddit posts and comments using PRAW.
"""

import praw
from typing import List, Dict, Optional
import pandas as pd
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class RedditCollector:
    def __init__(self):
        """Initialize Reddit API client"""
        try:
            self.reddit = praw.Reddit(
                client_id="fKZZCHZERy6y5xgHY5_jRQ",
                client_secret="_Ly4iNrBj0iszak_0gT7s4zzmyForw",
                user_agent="SocialMediaAnalyzer/0.1 by Former-Click-5185"
            )
            logger.info("Reddit collector initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Reddit collector: {str(e)}")
            raise

    def collect_subreddit_posts(self, subreddit_name: str, limit: int = 100) -> pd.DataFrame:
        """
        Collect posts from a specific subreddit
        
        Args:
            subreddit_name (str): Name of the subreddit
            limit (int): Maximum number of posts to collect
            
        Returns:
            pd.DataFrame: Collected posts data
        """
        try:
            posts = []
            subreddit = self.reddit.subreddit(subreddit_name)
            
            for post in subreddit.hot(limit=limit):
                posts.append({
                    'id': post.id,
                    'title': post.title,
                    'text': post.selftext,
                    'author': str(post.author),
                    'subreddit': subreddit_name,
                    'score': post.score,
                    'num_comments': post.num_comments,
                    'created_utc': datetime.fromtimestamp(post.created_utc),
                    'url': post.url,
                    'platform': 'reddit'
                })
            
            df = pd.DataFrame(posts)
            logger.info(f"Collected {len(df)} posts from r/{subreddit_name}")
            return df
            
        except Exception as e:
            logger.error(f"Error collecting subreddit posts: {str(e)}")
            return pd.DataFrame()

    def collect_post_comments(self, post_id: str, limit: int = 1000) -> pd.DataFrame:
        """
        Collect comments from a specific Reddit post.
        
        Args:
            post_id (str): The ID of the Reddit post
            limit (int): Maximum number of comments to collect (default: 1000)
            
        Returns:
            pd.DataFrame: DataFrame of collected comments with their metadata
        """
        try:
            submission = self.reddit.submission(id=post_id)
            submission.comments.replace_more(limit=None)  # Expand all comment trees
            
            comments = []
            for comment in submission.comments.list()[:limit]:
                comment_data = {
                    'id': comment.id,
                    'author': str(comment.author) if comment.author else '[deleted]',
                    'body': comment.body,
                    'score': comment.score,
                    'created_utc': comment.created_utc,
                    'parent_id': comment.parent_id,
                    'is_submitter': comment.is_submitter
                }
                comments.append(comment_data)
            
            if comments:
                logger.info(f"Collected {len(comments)} comments from post {post_id}")
                return pd.DataFrame(comments)
            return pd.DataFrame()  # Return empty DataFrame if no comments
            
        except Exception as e:
            logger.error(f"Error collecting comments for post {post_id}: {str(e)}")
            return pd.DataFrame()

    def search_reddit_posts(self, query, subreddits=None, limit=1000):
        """
        Search Reddit for posts matching the query.
        
        Args:
            query (str): Search term to look for
            subreddits (list): Optional list of subreddits to search in. If None, searches all of Reddit
            limit (int): Maximum number of posts to retrieve
            
        Returns:
            pd.DataFrame: DataFrame containing the search results
        """
        posts_data = []
        try:
            if subreddits:
                # Search in specific subreddits
                subreddit_str = '+'.join(subreddits)
                search_target = self.reddit.subreddit(subreddit_str)
            else:
                # Search all of Reddit
                search_target = self.reddit.subreddit('all')
                
            for submission in search_target.search(query, limit=limit):
                posts_data.append({
                    'id': submission.id,
                    'title': submission.title,
                    'text': submission.selftext,
                    'score': submission.score,
                    'url': submission.url,
                    'created_utc': datetime.fromtimestamp(submission.created_utc),
                    'subreddit': submission.subreddit.display_name,
                    'num_comments': submission.num_comments,
                    'author': str(submission.author),
                })
            
            return pd.DataFrame(posts_data)
        except Exception as e:
            logger.error(f"Error searching Reddit posts: {str(e)}")
            return pd.DataFrame()  # Return empty DataFrame on error