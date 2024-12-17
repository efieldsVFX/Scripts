"""
Targeted analysis for r/HarmonyKorrine and EDGLRD content
"""

import pandas as pd
from typing import Dict, List
import logging
from datetime import datetime, timedelta
from collections import defaultdict

from ..collectors.reddit_collector import RedditCollector

logger = logging.getLogger(__name__)

class TargetedAnalyzer:
    def __init__(self):
        self.collector = RedditCollector()
        
    def analyze_target_community(self, timeframe_days: int = 30) -> Dict:
        """
        Perform targeted analysis of r/HarmonyKorrine and EDGLRD content
        
        Args:
            timeframe_days: Number of days of data to analyze
            
        Returns:
            Dict containing analysis results
        """
        try:
            # Collect data from r/HarmonyKorrine
            subreddit_posts = self.collector.collect_subreddit_posts('HarmonyKorrine', limit=500)
            
            # Search for EDGLRD across Reddit
            edglrd_posts = self.collector.search_reddit_posts('EDGLRD', limit=500)
            
            # Combine the datasets
            all_posts = pd.concat([subreddit_posts, edglrd_posts]).drop_duplicates()
            
            # Filter for recent posts
            cutoff_date = datetime.now() - timedelta(days=timeframe_days)
            recent_posts = all_posts[all_posts['created_utc'] > cutoff_date]
            
            # Perform various analyses
            analysis_results = {
                'keyword_metrics': self.collector.analyze_trending_keywords(recent_posts),
                'content_suggestions': self.collector.get_content_suggestions(recent_posts),
                'audience_patterns': self.collector.get_audience_activity_patterns(recent_posts),
                'community_stats': self._get_community_stats(recent_posts)
            }
            
            return analysis_results
            
        except Exception as e:
            logger.error(f"Error in targeted analysis: {str(e)}")
            return {}
    
    def _get_community_stats(self, posts_df: pd.DataFrame) -> Dict:
        """Calculate community-specific statistics"""
        try:
            stats = {
                'total_posts': len(posts_df),
                'unique_authors': posts_df['author'].nunique(),
                'avg_score': posts_df['score'].mean(),
                'avg_comments': posts_df['num_comments'].mean(),
                'post_frequency': self._calculate_post_frequency(posts_df)
            }
            
            # Get top contributors
            top_authors = posts_df.groupby('author').agg({
                'score': 'sum',
                'num_comments': 'sum'
            }).sort_values('score', ascending=False).head(5)
            
            stats['top_contributors'] = [
                {
                    'author': author,
                    'total_score': row['score'],
                    'total_comments': row['num_comments']
                }
                for author, row in top_authors.iterrows()
            ]
            
            return stats
            
        except Exception as e:
            logger.error(f"Error calculating community stats: {str(e)}")
            return {}
    
    def _calculate_post_frequency(self, posts_df: pd.DataFrame) -> Dict:
        """Calculate posting frequency patterns"""
        try:
            posts_df['date'] = posts_df['created_utc'].dt.date
            daily_posts = posts_df.groupby('date').size()
            
            return {
                'posts_per_day': daily_posts.mean(),
                'max_posts_day': daily_posts.max(),
                'min_posts_day': daily_posts.min()
            }
        except Exception as e:
            logger.error(f"Error calculating post frequency: {str(e)}")
            return {}
