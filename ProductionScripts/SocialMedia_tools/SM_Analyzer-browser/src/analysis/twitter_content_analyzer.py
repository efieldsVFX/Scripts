"""
Twitter-specific content analyzer implementation
"""

from typing import Dict, List, Optional
import numpy as np
from datetime import datetime
from .content_analyzer import ContentAnalyzer

class TwitterContentAnalyzer(ContentAnalyzer):
    """Analyzer for Twitter-specific content metrics"""

    def __init__(self):
        """Initialize Twitter content analyzer"""
        super().__init__('twitter')

    def analyze_tweet_performance(self, tweet_data: Dict) -> Dict:
        """
        Analyze tweet performance metrics
        
        Args:
            tweet_data: Dict containing tweet metrics
            
        Returns:
            Dict containing tweet analysis
        """
        try:
            tweet_metrics = {
                'top_tweets': self._analyze_top_tweets(tweet_data),
                'thread_metrics': self._analyze_thread_momentum(tweet_data),
                'engagement_patterns': self._analyze_engagement_patterns(tweet_data),
                'viral_potential': self._analyze_viral_potential(tweet_data),
                'audience_reach': self._analyze_audience_reach(tweet_data)
            }
            return tweet_metrics
        except Exception as e:
            self.logger.error(f"Error analyzing tweet performance: {str(e)}")
            return {}

    def _analyze_top_tweets(self, tweet_data: Dict) -> Dict:
        """Analyze and identify top performing tweets"""
        try:
            tweets = tweet_data.get('tweets', [])
            if not tweets:
                return {}
            
            # Calculate engagement score for each tweet
            scored_tweets = []
            for tweet in tweets:
                engagement_score = self._calculate_tweet_score(tweet)
                scored_tweets.append({
                    'tweet_id': tweet.get('id'),
                    'score': engagement_score,
                    'metrics': {
                        'likes': tweet.get('like_count', 0),
                        'retweets': tweet.get('retweet_count', 0),
                        'replies': tweet.get('reply_count', 0),
                        'quotes': tweet.get('quote_count', 0),
                        'impressions': tweet.get('impression_count', 0)
                    },
                    'performance_factors': self._identify_performance_factors(tweet)
                })
            
            # Sort tweets by score
            top_tweets = sorted(scored_tweets, key=lambda x: x['score'], reverse=True)
            
            return {
                'top_performers': top_tweets[:10],  # Top 10 tweets
                'performance_distribution': self._calculate_performance_distribution(scored_tweets),
                'engagement_patterns': self._analyze_top_tweet_patterns(top_tweets),
                'content_insights': self._extract_content_insights(top_tweets)
            }
        except Exception as e:
            self.logger.error(f"Error analyzing top tweets: {str(e)}")
            return {}

    def _analyze_thread_momentum(self, tweet_data: Dict) -> Dict:
        """Analyze thread performance and momentum"""
        try:
            threads = tweet_data.get('threads', [])
            if not threads:
                return {}
            
            thread_metrics = []
            for thread in threads:
                thread_momentum = self._calculate_thread_momentum(thread)
                thread_metrics.append({
                    'thread_id': thread.get('id'),
                    'momentum_score': thread_momentum,
                    'engagement_flow': self._analyze_engagement_flow(thread),
                    'retention_metrics': self._calculate_thread_retention(thread),
                    'peak_points': self._identify_thread_peaks(thread)
                })
            
            return {
                'thread_performance': thread_metrics,
                'momentum_patterns': self._analyze_momentum_patterns(thread_metrics),
                'optimal_length': self._determine_optimal_thread_length(thread_metrics),
                'engagement_sustainability': self._analyze_sustainability(thread_metrics)
            }
        except Exception as e:
            self.logger.error(f"Error analyzing thread momentum: {str(e)}")
            return {}

    def _calculate_tweet_score(self, tweet: Dict) -> float:
        """Calculate engagement score for a tweet"""
        try:
            # Weighted engagement metrics
            weights = {
                'likes': 1,
                'retweets': 2,
                'replies': 3,
                'quotes': 2.5,
                'clicks': 1.5,
                'profile_visits': 2
            }
            
            score = sum(
                tweet.get(f"{metric}_count", 0) * weight
                for metric, weight in weights.items()
            )
            
            # Normalize by impressions if available
            impressions = tweet.get('impression_count', 0)
            if impressions > 0:
                score = score / impressions
            
            return float(score)
        except Exception as e:
            self.logger.error(f"Error calculating tweet score: {str(e)}")
            return 0.0

    def _calculate_thread_momentum(self, thread: Dict) -> Dict:
        """Calculate momentum metrics for a thread"""
        try:
            tweets = thread.get('tweets', [])
            if not tweets:
                return {}
            
            # Calculate engagement velocity
            engagement_rates = []
            timestamps = []
            for tweet in tweets:
                engagement = self._calculate_tweet_score(tweet)
                timestamp = datetime.fromisoformat(tweet.get('created_at', ''))
                
                engagement_rates.append(engagement)
                timestamps.append(timestamp)
            
            # Calculate momentum metrics
            momentum = {
                'engagement_velocity': self._calculate_velocity(engagement_rates),
                'sustainability_score': self._calculate_sustainability(engagement_rates),
                'peak_momentum': max(engagement_rates),
                'momentum_consistency': float(np.std(engagement_rates)),
                'temporal_patterns': self._analyze_temporal_patterns(engagement_rates, timestamps)
            }
            
            return momentum
        except Exception as e:
            self.logger.error(f"Error calculating thread momentum: {str(e)}")
            return {}

    def _analyze_engagement_flow(self, thread: Dict) -> Dict:
        """Analyze engagement flow through a thread"""
        try:
            tweets = thread.get('tweets', [])
            if not tweets:
                return {}
            
            # Track engagement progression
            engagement_flow = []
            for i, tweet in enumerate(tweets):
                engagement = {
                    'position': i + 1,
                    'engagement_rate': self._calculate_tweet_score(tweet),
                    'retention_rate': tweet.get('impression_count', 0) / tweets[0].get('impression_count', 1),
                    'completion_impact': self._calculate_completion_impact(tweet, thread)
                }
                engagement_flow.append(engagement)
            
            return {
                'engagement_progression': engagement_flow,
                'flow_patterns': self._identify_flow_patterns(engagement_flow),
                'critical_points': self._identify_critical_points(engagement_flow),
                'audience_retention': self._calculate_audience_retention(engagement_flow)
            }
        except Exception as e:
            self.logger.error(f"Error analyzing engagement flow: {str(e)}")
            return {}
