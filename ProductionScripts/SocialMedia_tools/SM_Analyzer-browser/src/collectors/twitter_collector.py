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
from utils.test_data import TWITTER_TEST_DATA

logger = logging.getLogger(__name__)

class TwitterCollector:
    def __init__(self, config: Dict):
        """Initialize Twitter API client"""
        try:
            self.client = tweepy.Client(
                bearer_token=config.get('bearer_token', ''),
                consumer_key=config.get('api_key', ''),
                consumer_secret=config.get('api_secret', ''),
                access_token=config.get('access_token', ''),
                access_token_secret=config.get('access_token_secret', '')
            )
            self.using_test_data = False
            logger.info("Twitter collector initialized with API keys")
        except Exception as e:
            self.client = None
            self.using_test_data = True
            logger.warning(f"Twitter API initialization failed, using test data: {str(e)}")

    def collect_tweets(self, query: str, max_results: int = 100) -> pd.DataFrame:
        """
        Collect tweets based on search query
        
        Args:
            query (str): Search query string
            max_results (int): Maximum number of tweets to collect
            
        Returns:
            pd.DataFrame: Collected tweets data
        """
        if self.using_test_data:
            logger.info("Using test data for tweet collection")
            tweets = []
            for tweet_data in TWITTER_TEST_DATA['tweets'][:max_results]:
                tweets.append({
                    'id': tweet_data['id'],
                    'text': tweet_data['text'],
                    'created_at': tweet_data['created_at'],
                    'likes': tweet_data['public_metrics']['like_count'],
                    'retweets': tweet_data['public_metrics']['retweet_count'],
                    'replies': tweet_data['public_metrics']['reply_count'],
                    'platform': 'twitter'
                })
            return pd.DataFrame(tweets)

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
        if self.using_test_data:
            logger.info("Using test data for user tweet collection")
            tweets = []
            for tweet_data in TWITTER_TEST_DATA['user_tweets'][:max_results]:
                tweets.append({
                    'id': tweet_data['id'],
                    'text': tweet_data['text'],
                    'created_at': tweet_data['created_at'],
                    'likes': tweet_data['public_metrics']['like_count'],
                    'retweets': tweet_data['public_metrics']['retweet_count'],
                    'replies': tweet_data['public_metrics']['reply_count'],
                    'platform': 'twitter',
                    'username': username
                })
            return pd.DataFrame(tweets)

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

    def get_trending_topics(self, woeid: int = 1) -> List[Dict]:
        """
        Get current trending topics globally or by location
        woeid: Where On Earth ID (1 for global)
        """
        if self.using_test_data:
            logger.info("Using test data for trending topics")
            return TWITTER_TEST_DATA['trending_topics']

        try:
            trends = self.client.get_place_trends(woeid)
            trending_topics = []
            
            for trend in trends[0]:
                trending_topics.append({
                    'name': trend['name'],
                    'volume': trend['tweet_volume'] or 0,
                    'url': trend['url'],
                    'timestamp': datetime.now()
                })
            
            return trending_topics
        except Exception as e:
            logger.error(f"Error fetching trending topics: {str(e)}")
            return []

    def analyze_media_impact(self, tweets_df: pd.DataFrame) -> Dict:
        """
        Analyze impact of different media types in tweets
        """
        if tweets_df.empty:
            return {}

        # Identify tweets with media
        media_patterns = {
            'image': r'https?://[^\s]+\.(?:jpg|jpeg|png|gif)',
            'video': r'https?://[^\s]+\.(?:mp4|mov|avi)',
            'link': r'https?://[^\s]+'
        }

        media_metrics = {}
        for media_type, pattern in media_patterns.items():
            media_tweets = tweets_df[tweets_df['text'].str.contains(pattern, na=False)]
            if not media_tweets.empty:
                media_metrics[media_type] = {
                    'count': len(media_tweets),
                    'avg_likes': media_tweets['likes'].mean(),
                    'avg_retweets': media_tweets['retweets'].mean(),
                    'avg_replies': media_tweets['replies'].mean(),
                    'engagement_rate': (media_tweets['likes'] + media_tweets['retweets'] + 
                                     media_tweets['replies']).mean() / len(media_tweets)
                }

        return media_metrics

    def track_topics(self, topics: List[str], days: int = 7) -> pd.DataFrame:
        """
        Track specified topics over time
        """
        if self.using_test_data:
            logger.info("Using test data for topic tracking")
            topic_data = []
            for topic in topics:
                for tweet_data in TWITTER_TEST_DATA['topic_tweets'][topic][:days]:
                    topic_data.append({
                        'topic': topic,
                        'created_at': tweet_data['created_at'],
                        'engagement': (tweet_data['public_metrics']['like_count'] + 
                                    tweet_data['public_metrics']['retweet_count'] + 
                                    tweet_data['public_metrics']['reply_count']),
                        'text': tweet_data['text']
                    })
            return pd.DataFrame(topic_data)

        topic_data = []
        end_time = datetime.now()
        start_time = end_time - pd.Timedelta(days=days)

        for topic in topics:
            response = self.client.search_recent_tweets(
                query=f"{topic} -is:retweet lang:en",
                start_time=start_time,
                end_time=end_time,
                max_results=100,
                tweet_fields=['created_at', 'public_metrics']
            )
            
            if response.data:
                for tweet in response.data:
                    topic_data.append({
                        'topic': topic,
                        'created_at': tweet.created_at,
                        'engagement': (tweet.public_metrics['like_count'] + 
                                    tweet.public_metrics['retweet_count'] + 
                                    tweet.public_metrics['reply_count']),
                        'text': tweet.text
                    })

        return pd.DataFrame(topic_data)

    def analyze_effective_content(self, tweets_df: pd.DataFrame, min_engagement: int = 10) -> Dict:
        """
        Analyze characteristics of highly engaging tweets
        """
        if tweets_df.empty:
            return {}

        # Calculate engagement score
        tweets_df['engagement_score'] = (tweets_df['likes'] + 
                                       tweets_df['retweets'] * 2 + 
                                       tweets_df['replies'] * 3)

        # Get high-performing tweets
        high_performing = tweets_df[tweets_df['engagement_score'] > min_engagement]

        if high_performing.empty:
            return {}

        # Analyze content patterns
        analysis = {
            'top_tweets': high_performing.nlargest(5, 'engagement_score')[
                ['text', 'engagement_score', 'likes', 'retweets']
            ].to_dict('records'),
            'avg_length': high_performing['text'].str.len().mean(),
            'has_media': high_performing['text'].str.contains(
                r'https?://[^\s]+\.(?:jpg|jpeg|png|gif|mp4|mov|avi)', 
                na=False
            ).mean(),
            'has_hashtags': high_performing['text'].str.contains(r'#\w+', na=False).mean(),
            'has_mentions': high_performing['text'].str.contains(r'@\w+', na=False).mean(),
            'posting_times': high_performing['created_at'].dt.hour.value_counts()
                .nlargest(3).to_dict()
        }

        return analysis

    def collect_audience_insights(self, user_id: str) -> Dict:
        """
        Collect comprehensive audience insights for a Twitter user
        
        Args:
            user_id: Twitter user ID to analyze
            
        Returns:
            Dict containing audience insights data
        """
        if self.using_test_data:
            logger.info("Using test data for audience insights")
            return TWITTER_TEST_DATA['audience_insights']

        insights = {
            'follower_data': self._collect_follower_demographics(user_id),
            'activity_data': self._collect_activity_patterns(user_id),
            'engagement_data': self._collect_engagement_metrics(user_id),
            'interest_data': self._collect_audience_interests(user_id),
            'collected_at': datetime.now().isoformat()
        }
        
        return insights
        
    def _collect_follower_demographics(self, user_id: str) -> Dict:
        """Collect follower demographic information"""
        try:
            user = self.client.get_user(id=user_id)
            followers = self.client.get_users_followers(id=user_id, max_results=1000)  # Sample size of 1000
            
            demographics = {
                'total_followers': user.data.public_metrics['followers_count'],
                'age_groups': self._estimate_age_distribution(followers),
                'gender': self._estimate_gender_distribution(followers),
                'countries': self._analyze_location_data(followers, 'country'),
                'cities': self._analyze_location_data(followers, 'city'),
                'regions': self._analyze_location_data(followers, 'region'),
                'languages': self._analyze_languages(followers)
            }
            
            return demographics
            
        except Exception as e:
            logger.error(f"Error collecting follower demographics: {str(e)}")
            return {}
            
    def _collect_activity_patterns(self, user_id: str) -> Dict:
        """Collect audience activity patterns"""
        try:
            # Get user's recent tweets
            tweets = self.client.get_users_tweets(id=user_id, max_results=200)
            
            # Analyze tweet timestamps
            timestamps = [tweet.created_at for tweet in tweets.data]
            
            activity_data = {
                'hourly_activity': self._analyze_hourly_activity(timestamps),
                'weekly_activity': self._analyze_weekly_activity(timestamps),
                'tweet_frequency': self._calculate_tweet_frequency(timestamps)
            }
            
            return activity_data
            
        except Exception as e:
            logger.error(f"Error collecting activity patterns: {str(e)}")
            return {}
            
    def _collect_engagement_metrics(self, user_id: str) -> Dict:
        """Collect engagement metrics"""
        try:
            tweets = self.client.get_users_tweets(id=user_id, max_results=200)
            
            total_likes = sum(tweet.public_metrics['like_count'] for tweet in tweets.data)
            total_retweets = sum(tweet.public_metrics['retweet_count'] for tweet in tweets.data)
            total_replies = sum(1 for tweet in tweets.data if tweet.in_reply_to_user_id is not None)
            
            engagement_data = {
                'total_interactions': total_likes + total_retweets + total_replies,
                'likes_rate': total_likes / len(tweets.data) if tweets.data else 0,
                'retweet_rate': total_retweets / len(tweets.data) if tweets.data else 0,
                'reply_rate': total_replies / len(tweets.data) if tweets.data else 0,
                'trends': self._analyze_engagement_trends(tweets.data)
            }
            
            return engagement_data
            
        except Exception as e:
            logger.error(f"Error collecting engagement metrics: {str(e)}")
            return {}
            
    def _collect_audience_interests(self, user_id: str) -> Dict:
        """Collect audience interests and topics"""
        try:
            # Get user's followers
            followers = self.client.get_users_followers(id=user_id, max_results=1000)
            
            # Collect recent tweets from followers
            follower_tweets = []
            for follower in followers.data:
                try:
                    tweets = self.client.get_users_tweets(id=follower.id, max_results=50)
                    follower_tweets.extend(tweets.data)
                except:
                    continue
                    
            interest_data = {
                'topics': self._extract_topics(follower_tweets),
                'hashtags': self._analyze_hashtags(follower_tweets),
                'mentions': self._analyze_mentions(follower_tweets),
                'clusters': self._identify_interest_clusters(follower_tweets)
            }
            
            return interest_data
            
        except Exception as e:
            logger.error(f"Error collecting audience interests: {str(e)}")
            return {}
            
    def _analyze_hourly_activity(self, timestamps: List[datetime]) -> Dict[int, int]:
        """Analyze hourly activity patterns"""
        hourly_counts = {hour: 0 for hour in range(24)}
        
        for ts in timestamps:
            hourly_counts[ts.hour] += 1
            
        return hourly_counts
        
    def _analyze_weekly_activity(self, timestamps: List[datetime]) -> Dict[str, int]:
        """Analyze weekly activity patterns"""
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        weekly_counts = {day: 0 for day in days}
        
        for ts in timestamps:
            day = days[ts.weekday()]
            weekly_counts[day] += 1
            
        return weekly_counts
        
    def _calculate_tweet_frequency(self, timestamps: List[datetime]) -> Dict:
        """Calculate tweet frequency metrics"""
        if not timestamps:
            return {'daily_average': 0, 'weekly_average': 0}
            
        # Sort timestamps
        sorted_ts = sorted(timestamps)
        
        # Calculate time span
        time_span = sorted_ts[-1] - sorted_ts[0]
        days_span = time_span.days or 1  # Avoid division by zero
        
        return {
            'daily_average': len(timestamps) / days_span,
            'weekly_average': (len(timestamps) / days_span) * 7
        }
        
    def _analyze_engagement_trends(self, tweets: List) -> Dict:
        """Analyze engagement trends over time"""
        trends = {
            'likes_trend': [],
            'retweets_trend': [],
            'replies_trend': []
        }
        
        # Group tweets by day
        tweet_days = {}
        for tweet in tweets:
            day = tweet.created_at.date()
            if day not in tweet_days:
                tweet_days[day] = []
            tweet_days[day].append(tweet)
            
        # Calculate daily averages
        for day in sorted(tweet_days.keys()):
            day_tweets = tweet_days[day]
            trends['likes_trend'].append({
                'date': day.isoformat(),
                'value': sum(t.public_metrics['like_count'] for t in day_tweets) / len(day_tweets)
            })
            trends['retweets_trend'].append({
                'date': day.isoformat(),
                'value': sum(t.public_metrics['retweet_count'] for t in day_tweets) / len(day_tweets)
            })
            trends['replies_trend'].append({
                'date': day.isoformat(),
                'value': sum(1 for t in day_tweets if t.in_reply_to_user_id is not None) / len(day_tweets)
            })
            
        return trends
        
    def _extract_topics(self, tweets: List) -> Dict[str, int]:
        """Extract and count topics from tweets"""
        topics = {}
        
        for tweet in tweets:
            # Extract hashtags as topics
            if hasattr(tweet, 'entities') and 'hashtags' in tweet.entities:
                for hashtag in tweet.entities['hashtags']:
                    topic = hashtag['tag'].lower()
                    topics[topic] = topics.get(topic, 0) + 1
                    
        return dict(sorted(topics.items(), key=lambda x: x[1], reverse=True)[:20])
        
    def _analyze_hashtags(self, tweets: List) -> Dict[str, int]:
        """Analyze hashtag usage"""
        hashtags = {}
        
        for tweet in tweets:
            if hasattr(tweet, 'entities') and 'hashtags' in tweet.entities:
                for hashtag in tweet.entities['hashtags']:
                    tag = hashtag['tag'].lower()
                    hashtags[tag] = hashtags.get(tag, 0) + 1
                    
        return dict(sorted(hashtags.items(), key=lambda x: x[1], reverse=True)[:20])
        
    def _analyze_mentions(self, tweets: List) -> Dict[str, int]:
        """Analyze mentioned accounts"""
        mentions = {}
        
        for tweet in tweets:
            if hasattr(tweet, 'entities') and 'mentions' in tweet.entities:
                for mention in tweet.entities['mentions']:
                    username = mention['username']
                    mentions[username] = mentions.get(username, 0) + 1
                    
        return dict(sorted(mentions.items(), key=lambda x: x[1], reverse=True)[:20])
        
    def _identify_interest_clusters(self, tweets: List) -> Dict:
        """Identify clusters of related interests"""
        # Simple clustering based on co-occurring hashtags
        clusters = {}
        
        # Create co-occurrence matrix
        cooccurrence = {}
        for tweet in tweets:
            if hasattr(tweet, 'entities') and 'hashtags' in tweet.entities:
                hashtags = [h['tag'].lower() for h in tweet.entities['hashtags']]
                for i, h1 in enumerate(hashtags):
                    for h2 in hashtags[i+1:]:
                        pair = tuple(sorted([h1, h2]))
                        cooccurrence[pair] = cooccurrence.get(pair, 0) + 1
                        
        # Create basic clusters
        processed = set()
        cluster_id = 1
        
        for (h1, h2), count in sorted(cooccurrence.items(), key=lambda x: x[1], reverse=True):
            if h1 not in processed or h2 not in processed:
                cluster_name = f"Interest_Cluster_{cluster_id}"
                clusters[cluster_name] = {
                    'size': count,
                    'topics': [h1, h2],
                    'engagement_rate': self._calculate_cluster_engagement([h1, h2], tweets)
                }
                processed.add(h1)
                processed.add(h2)
                cluster_id += 1
                
        return clusters
        
    def _calculate_cluster_engagement(self, topics: List[str], tweets: List) -> float:
        """Calculate engagement rate for a cluster of topics"""
        cluster_tweets = []
        
        for tweet in tweets:
            if hasattr(tweet, 'entities') and 'hashtags' in tweet.entities:
                hashtags = [h['tag'].lower() for h in tweet.entities['hashtags']]
                if any(topic in hashtags for topic in topics):
                    cluster_tweets.append(tweet)
                    
        if not cluster_tweets:
            return 0.0
            
        total_engagement = sum(
            tweet.public_metrics['like_count'] + tweet.public_metrics['retweet_count']
            for tweet in cluster_tweets
        )
        
        return total_engagement / len(cluster_tweets)