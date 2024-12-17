"""
Reddit data collector focused on essential metrics
"""

import asyncpraw
import asyncio
import nest_asyncio
import pandas as pd
import logging
import time
from typing import Dict, List
from datetime import datetime
from collections import defaultdict
import os

# Configure logging
logger = logging.getLogger(__name__)

# Enable nested event loops (needed for Jupyter/Streamlit environments)
nest_asyncio.apply()

class RedditCollector:
    """Reddit data collector class"""
    
    def __init__(self, config: Dict = None):
        """Initialize Reddit API client
        
        Args:
            config (Dict): Configuration dictionary containing API credentials
        """
        try:
            # Set up event loop
            try:
                self.loop = asyncio.get_event_loop()
            except RuntimeError:
                self.loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self.loop)
            
            # Store credentials
            if config and config.get('client_id') and config.get('client_secret'):
                self.client_id = config['client_id']
                self.client_secret = config['client_secret']
                self.user_agent = config.get('user_agent', 'SocialMediaAnalyzer/0.1')
            else:
                # Fallback to default credentials
                self.client_id = "fKZZCHZERy6y5xgHY5_jRQ"
                self.client_secret = "_Ly4iNrBj0iszak_0gT7s4zzmyForw"
                self.user_agent = "SocialMediaAnalyzer/0.1 by Former-Click-5185"
            
            # Initialize Reddit client
            self.reddit = asyncpraw.Reddit(
                client_id=self.client_id,
                client_secret=self.client_secret,
                user_agent=self.user_agent
            )
            
            self._cache = {}
            self._cache_ttl = 300  # 5 minutes
            self.logger = logger
            logger.info("Reddit collector initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Reddit collector: {str(e)}")
            raise

    async def async_init(self):
        """Asynchronous initialization"""
        try:
            # Test the connection by getting the authenticated user
            await self.reddit.user.me()
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Reddit connection: {e}")
            return False

    async def get_basic_stats(self) -> Dict:
        """Get basic statistics from Reddit"""
        try:
            subreddit = await self.reddit.subreddit('HarmonyKorine')
            
            # Get basic stats from Reddit API
            stats = {
                'connection_status': 'connected',
                'api_status': 'healthy',
                'timestamp': datetime.now().isoformat()
            }
            
            # Get subscriber count and active users
            stats['total_subscribers'] = subreddit.subscribers
            stats['active_users'] = subreddit.active_user_count
            
            # Get recent posts for engagement metrics
            recent_posts = [post async for post in subreddit.new(limit=100)]
            total_comments = sum(post.num_comments for post in recent_posts)
            total_score = sum(post.score for post in recent_posts)
            
            # Calculate engagement metrics
            stats['total_karma'] = total_score
            stats['post_karma'] = sum(1 for post in recent_posts if post.score > 0)
            stats['comment_karma'] = total_comments
            stats['avg_comments_per_post'] = total_comments / len(recent_posts) if recent_posts else 0
            stats['engagement_rate'] = (total_comments / len(recent_posts) * 100) if recent_posts else 0
            stats['daily_posts'] = len(recent_posts) / 7  # Assuming posts from last 7 days
            
            # Analyze content types
            content_types = {}
            for post in recent_posts:
                post_type = self._get_post_type(post)
                content_types[post_type] = content_types.get(post_type, 0) + 1
            stats['content_breakdown'] = content_types
            
            # Get peak activity hours
            activity_hours = [datetime.fromtimestamp(post.created_utc).hour for post in recent_posts]
            hour_counts = {}
            for hour in activity_hours:
                hour_counts[hour] = hour_counts.get(hour, 0) + 1
            peak_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:3]
            stats['peak_activity_hours'] = peak_hours
            
            # Get top posts
            top_posts = [post async for post in subreddit.top('month', limit=5)]
            stats['top_posts'] = [{
                'title': post.title,
                'score': post.score,
                'num_comments': post.num_comments,
                'upvote_ratio': post.upvote_ratio,
                'created_utc': post.created_utc,
                'url': f"https://reddit.com{post.permalink}"
            } for post in top_posts]
            
            return stats
        except Exception as e:
            self.logger.error(f"Error getting basic stats: {str(e)}")
            return {
                'connection_status': 'error',
                'api_status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def _get_cached_data(self, key: str) -> Dict:
        """Get data from cache if not expired"""
        if key in self._cache:
            data, timestamp = self._cache[key]
            if time.time() - timestamp < self._cache_ttl:
                return data
        return None

    def _cache_data(self, key: str, data: Dict):
        """Cache data with timestamp"""
        self._cache[key] = (data, time.time())

    async def get_subreddit_insights(self, subreddit_name: str, limit: int = 50) -> Dict:
        """Get essential insights from a subreddit"""
        cache_key = f"insights_{subreddit_name}"
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data

        try:
            subreddit = await self.reddit.subreddit(subreddit_name)
            insights = {
                'subreddit_stats': {
                    'subscribers': subreddit.subscribers,
                    'active_users': subreddit.active_user_count
                },
                'posts': []
            }

            # Collect post data efficiently
            async for post in subreddit.hot(limit=limit):
                post_data = {
                    'title': post.title,
                    'score': post.score,
                    'num_comments': post.num_comments,
                    'created_utc': post.created_utc,
                    'is_self': post.is_self,
                    'url': f"https://reddit.com{post.permalink}"
                }
                insights['posts'].append(post_data)

            self._cache_data(cache_key, insights)
            return insights

        except Exception as e:
            logger.error(f"Error getting subreddit insights: {str(e)}")
            return {}

    async def search_relevant_posts(self, query: str, limit: int = 25) -> List[Dict]:
        """Search for relevant posts across Reddit"""
        cache_key = f"search_{query}"
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data

        try:
            posts = []
            async for post in self.reddit.subreddit('all').search(query, limit=limit):
                post_data = {
                    'title': post.title,
                    'score': post.score,
                    'num_comments': post.num_comments,
                    'created_utc': post.created_utc,
                    'subreddit': post.subreddit.display_name,
                    'url': f"https://reddit.com{post.permalink}"
                }
                posts.append(post_data)

            self._cache_data(cache_key, posts)
            return posts

        except Exception as e:
            logger.error(f"Error searching posts: {str(e)}")
            return []

    async def search_reddit_posts(self, query: str, subreddits: List[str] = None, limit: int = 25) -> List[Dict]:
        """Search for posts across specified subreddits or all of Reddit
        
        Args:
            query (str): Search query
            subreddits (List[str], optional): List of subreddits to search in. If None, searches all of Reddit
            limit (int, optional): Maximum number of posts to return. Defaults to 25
            
        Returns:
            List[Dict]: List of posts matching the search criteria
        """
        try:
            async with asyncpraw.Reddit(
                client_id=self.client_id,
                client_secret=self.client_secret,
                user_agent=self.user_agent
            ) as reddit:
                if subreddits:
                    # Search in specific subreddits
                    results = []
                    for subreddit_name in subreddits:
                        try:
                            subreddit = await reddit.subreddit(subreddit_name)
                            async for post in subreddit.search(query, limit=limit):
                                results.append({
                                    'title': post.title,
                                    'score': post.score,
                                    'num_comments': post.num_comments,
                                    'created_utc': post.created_utc,
                                    'subreddit': post.subreddit.display_name,
                                    'url': f"https://reddit.com{post.permalink}"
                                })
                        except Exception as e:
                            self.logger.error(f"Error searching subreddit {subreddit_name}: {str(e)}")
                    return results
                else:
                    # If no subreddits specified, use the existing search_relevant_posts method
                    return await self.search_relevant_posts(query, limit)

        except Exception as e:
            logger.error(f"Error searching posts: {str(e)}")
            return []

    async def collect_data(self) -> Dict:
        """Collect data from Reddit"""
        try:
            # Get basic stats which includes most metrics
            stats = await self.get_basic_stats()
            
            # Get additional metrics
            subreddit = await self.reddit.subreddit('HarmonyKorine')
            
            # Add subreddit info
            stats['subreddit_info'] = {
                'name': subreddit.display_name,
                'title': subreddit.title,
                'description': subreddit.description if hasattr(subreddit, 'description') else '',
                'subscribers': subreddit.subscribers,
                'created_utc': datetime.fromtimestamp(subreddit.created_utc).isoformat()
            }
            
            # Add audience stats
            audience_data = await self.collect_audience_insights('HarmonyKorine')
            if audience_data:
                stats['audience_stats'] = audience_data
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error collecting Reddit data: {str(e)}")
            return {}

    async def analyze_reddit_content(self, df: pd.DataFrame) -> Dict:
        """Analyze Reddit-specific content"""
        try:
            # First perform compliance checks
            if not self.validate_fields(df.columns):
                self.logger.error("Invalid fields in data")
                return {'status': 'error', 'message': 'Invalid fields'}
            
            # Then analyze content
            analysis_results = await self.analyze_content(df)
            
            # Add Reddit-specific metrics
            reddit_metrics = await self.analyze_engagement(df)
            analysis_results['platform_metrics'] = reddit_metrics
            
            return analysis_results
            
        except Exception as e:
            self.logger.error(f"Error in Reddit content analysis: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }

    async def collect_audience_insights(self, subreddit_name: str) -> Dict:
        """
        Collect comprehensive audience insights for a subreddit
        
        Args:
            subreddit_name: Name of the subreddit to analyze
        
        Returns:
            Dict containing audience insights data
        """
        try:
            subreddit = await self.reddit.subreddit(subreddit_name)
            
            insights = {
                'community_data': await self._collect_community_data(subreddit),
                'engagement_data': await self._collect_engagement_data(subreddit),
                'content_data': await self._collect_content_data(subreddit),
                'behavior_data': await self._collect_behavior_data(subreddit),
                'topic_data': await self._collect_topic_data(subreddit),
                'collected_at': datetime.now().isoformat()
            }
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Error collecting Reddit audience insights: {str(e)}")
            return {}

    async def _collect_community_data(self, subreddit) -> Dict:
        """Collect community metrics"""
        try:
            # Get subscriber and active user counts
            subscriber_data = {
                'total': subreddit.subscribers,
                'active': subreddit.active_user_count,
                'daily_growth': 0,  # Requires historical data
                'weekly_growth': 0,
                'monthly_growth': 0
            }
            
            # Get community growth metrics
            growth_data = {
                'trends': await self._get_growth_trends(subreddit.display_name),
                'growth_rate': 0,  # Requires historical data
                'retention_rate': 0,
                'churn_rate': 0
            }
            
            # Get activity metrics
            activity_data = await self._get_activity_metrics(subreddit)
            
            # Get user flair data
            flair_data = await self._get_flair_metrics(subreddit)
            
            return {
                'subscribers': subscriber_data,
                'growth': growth_data,
                'activity': activity_data,
                'flairs': flair_data
            }
            
        except Exception as e:
            self.logger.error(f"Error collecting community data: {str(e)}")
            return {}

    async def _get_flair_metrics(self, subreddit: str) -> Dict:
        """Analyze user flair distribution and metrics"""
        try:
            flair_data = {
                'distribution': {},
                'total_flaired_users': 0,
                'unique_flairs': 0,
                'top_flairs': []
            }
            
            # Get recent posts to analyze flairs
            posts = [post async for post in subreddit.new(limit=100)]
            comments = [comment async for comment in subreddit.comments(limit=100)]
            
            # Track user flairs from posts
            for post in posts:
                if post.author_flair_text:
                    flair = post.author_flair_text
                    flair_data['distribution'][flair] = flair_data['distribution'].get(flair, 0) + 1
                    flair_data['total_flaired_users'] += 1
            
            # Track user flairs from comments
            for comment in comments:
                if hasattr(comment, 'author_flair_text') and comment.author_flair_text:
                    flair = comment.author_flair_text
                    flair_data['distribution'][flair] = flair_data['distribution'].get(flair, 0) + 1
                    flair_data['total_flaired_users'] += 1
            
            # Calculate unique flairs
            flair_data['unique_flairs'] = len(flair_data['distribution'])
            
            # Get top flairs
            flair_data['top_flairs'] = sorted(
                [{'flair': k, 'count': v} for k, v in flair_data['distribution'].items()],
                key=lambda x: x['count'],
                reverse=True
            )[:10]
            
            return flair_data
        except Exception as e:
            self.logger.error(f"Error getting flair metrics: {str(e)}")
            return {}

    async def _collect_engagement_data(self, subreddit) -> Dict:
        """Collect engagement metrics"""
        try:
            # Get recent posts for analysis
            posts = [post async for post in subreddit.hot(limit=100)]
            
            total_upvotes = sum(post.score for post in posts)
            total_comments = sum(post.num_comments for post in posts)
            total_awards = sum(len(post.all_awardings) for post in posts)
            
            engagement_data = {
                'total_posts': len(posts),
                'upvotes': total_upvotes,
                'comments': total_comments,
                'awards': total_awards,
                'trends': await self._calculate_engagement_trends(subreddit.display_name),
                'interactions': {
                    'upvotes': total_upvotes,
                    'comments': total_comments,
                    'awards': total_awards
                },
                'time_based': await self._analyze_time_based_engagement(posts)
            }
            
            return engagement_data
            
        except Exception as e:
            self.logger.error(f"Error collecting engagement data: {str(e)}")
            return {}

    async def _collect_content_data(self, subreddit) -> Dict:
        """Collect content performance data"""
        try:
            # Get posts sorted by different criteria
            hot_posts = [post async for post in subreddit.hot(limit=50)]
            new_posts = [post async for post in subreddit.new(limit=50)]
            top_posts = [post async for post in subreddit.top(time_filter='month', limit=50)]
            
            content_data = {
                'top_posts': await self._analyze_top_posts(subreddit, hot_posts + new_posts + top_posts),
                'types': await self._analyze_post_types(hot_posts + new_posts + top_posts),
                'timing': await self._analyze_post_timing(hot_posts + new_posts),
                'awards': await self._analyze_post_awards(top_posts)
            }
            
            return content_data
            
        except Exception as e:
            self.logger.error(f"Error collecting content data: {str(e)}")
            return {}

    async def _collect_behavior_data(self, subreddit) -> Dict:
        """Collect audience behavior data"""
        try:
            # Get recent posts and comments for analysis
            posts = [post async for post in subreddit.hot(limit=100)]
            
            behavior_data = {
                'participation': await self._analyze_participation_patterns(subreddit, posts),
                'voting': await self._analyze_voting_patterns(posts),
                'commenting': await self._analyze_commenting_patterns(posts),
                'cross_subreddit': await self._analyze_cross_subreddit_activity(posts)
            }
            
            return behavior_data
            
        except Exception as e:
            self.logger.error(f"Error collecting behavior data: {str(e)}")
            return {}

    async def _collect_topic_data(self, subreddit) -> Dict:
        """Collect topic and discussion data"""
        try:
            # Get posts for topic analysis
            posts = [post async for post in subreddit.hot(limit=200)]
            
            topic_data = {
                'trending': await self._get_trending_topics(subreddit, posts),
                'engagement': await self._get_topic_engagement(posts),
                'sentiment': await self._analyze_topic_sentiment(posts),
                'relationships': await self._analyze_topic_relationships(posts)
            }
            
            return topic_data
            
        except Exception as e:
            self.logger.error(f"Error collecting topic data: {str(e)}")
            return {}

    async def _get_activity_metrics(self, subreddit) -> Dict:
        """Get detailed activity metrics"""
        try:
            posts = [post async for post in subreddit.new(limit=100)]
            
            # Calculate posts per day
            if posts:
                time_span = (datetime.utcnow() - datetime.fromtimestamp(posts[-1].created_utc)).days or 1
                posts_per_day = len(posts) / time_span
            else:
                posts_per_day = 0
                
            # Calculate comments per post
            total_comments = sum(post.num_comments for post in posts)
            comments_per_post = total_comments / len(posts) if posts else 0
            
            # Analyze activity distribution
            activity_dist = await self._get_activity_distribution(posts)
            
            return {
                'posts_per_day': posts_per_day,
                'comments_per_post': comments_per_post,
                'daily_active_users': subreddit.active_user_count,
                'peak_times': await self._get_peak_activity_times(posts),
                'distribution': activity_dist
            }
            
        except Exception as e:
            self.logger.error(f"Error getting activity metrics: {str(e)}")
            return {}

    async def _get_activity_distribution(self, posts: List) -> Dict:
        """Get hourly activity distribution"""
        hourly_dist = {hour: 0 for hour in range(24)}
        
        for post in posts:
            hour = datetime.fromtimestamp(post.created_utc).hour
            hourly_dist[hour] += 1
            
        return hourly_dist
        
    async def _get_peak_activity_times(self, posts: List) -> List[Dict]:
        """Get peak activity times"""
        hourly_dist = await self._get_activity_distribution(posts)
        
        # Get top 5 active hours
        peak_hours = sorted(
            hourly_dist.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        return [{'hour': hour, 'activity_count': count} for hour, count in peak_hours]

    async def _analyze_post_types(self, posts: List) -> Dict:
        """Analyze different types of posts"""
        type_metrics = {
            'text': {'count': 0, 'engagement': 0},
            'link': {'count': 0, 'engagement': 0},
            'image': {'count': 0, 'engagement': 0},
            'video': {'count': 0, 'engagement': 0}
        }
        
        for post in posts:
            post_type = self._get_post_type(post)
            engagement = post.score + post.num_comments
            
            type_metrics[post_type]['count'] += 1
            type_metrics[post_type]['engagement'] += engagement
            
        # Calculate averages
        for metrics in type_metrics.values():
            if metrics['count'] > 0:
                metrics['avg_engagement'] = metrics['engagement'] / metrics['count']
                
        return type_metrics
        
    async def _get_post_type(self, post) -> str:
        """Determine post type"""
        if post.is_self:
            return 'text'
        elif any(post.url.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif']):
            return 'image'
        elif any(post.url.lower().endswith(ext) for ext in ['.mp4', '.webm']):
            return 'video'
        else:
            return 'link'
            
    async def _analyze_topic_sentiment(self, posts: List) -> Dict:
        """Analyze sentiment for different topics"""
        topic_sentiment = {}
        
        for post in posts:
            # Extract topics from title and text
            topics = set(post.title.lower().split())
            if post.selftext:
                topics.update(post.selftext.lower().split())
                
            # Calculate sentiment
            text = f"{post.title} {post.selftext}"
            sentiment = TextBlob(text).sentiment.polarity
            
            for topic in topics:
                if topic not in topic_sentiment:
                    topic_sentiment[topic] = {
                        'count': 0,
                        'total_sentiment': 0
                    }
                topic_sentiment[topic]['count'] += 1
                topic_sentiment[topic]['total_sentiment'] += sentiment
                
        # Calculate average sentiment
        for topic in topic_sentiment.values():
            topic['avg_sentiment'] = topic['total_sentiment'] / topic['count']
            
        return dict(sorted(
            topic_sentiment.items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )[:20])

    async def _get_growth_trends(self, subreddit_name: str) -> Dict:
        """Get subreddit growth trends"""
        try:
            # Get the subreddit object using the name string
            subreddit = await self.reddit.subreddit(subreddit_name)
            return {
                'subscribers': subreddit.subscribers,
                'active_users': subreddit.active_user_count,
                'created_utc': subreddit.created_utc
            }
        except Exception as e:
            self.logger.error(f"Error getting growth trends: {str(e)}")
            return {}

    async def _calculate_engagement_trends(self, subreddit_name: str, limit: int = 100) -> Dict:
        """Calculate engagement trends from recent posts"""
        try:
            # Get the subreddit object using the name string
            subreddit = await self.reddit.subreddit(subreddit_name)
            posts = [post async for post in subreddit.hot(limit=limit)]
            
            engagement_data = {
                'total_posts': 0,
                'total_comments': 0,
                'total_score': 0,
                'avg_score': 0,
                'avg_comments': 0
            }
            
            for post in posts:
                engagement_data['total_posts'] += 1
                engagement_data['total_comments'] += post.num_comments
                engagement_data['total_score'] += post.score
            
            if engagement_data['total_posts'] > 0:
                engagement_data['avg_score'] = engagement_data['total_score'] / engagement_data['total_posts']
                engagement_data['avg_comments'] = engagement_data['total_comments'] / engagement_data['total_posts']
            
            return engagement_data
        except Exception as e:
            self.logger.error(f"Error calculating engagement trends: {str(e)}")
            return {}

    async def _analyze_top_posts(self, subreddit_name: str, posts: List, limit: int = 50) -> Dict:
        """Analyze top posts for content insights"""
        try:
            content_data = {
                'post_types': {},
                'top_domains': {},
                'posting_times': [],
                'top_posts': []
            }
            
            for post in posts:
                # Track post type
                post_type = 'text' if post.is_self else 'link'
                if hasattr(post, 'post_hint'):
                    post_type = post.post_hint
                content_data['post_types'][post_type] = content_data['post_types'].get(post_type, 0) + 1
                
                # Track domain
                if not post.is_self:
                    domain = post.domain
                    content_data['top_domains'][domain] = content_data['top_domains'].get(domain, 0) + 1
                
                # Track posting time
                content_data['posting_times'].append(post.created_utc)
                
                # Track top posts
                content_data['top_posts'].append({
                    'title': post.title,
                    'score': post.score,
                    'comments': post.num_comments,
                    'created_utc': post.created_utc
                })
            
            return content_data
        except Exception as e:
            self.logger.error(f"Error analyzing top posts: {str(e)}")
            return {}

    async def _analyze_participation_patterns(self, subreddit_name: str, posts: List, limit: int = 100) -> Dict:
        """Analyze user participation patterns"""
        try:
            comments = [comment async for comment in subreddit_name.comments(limit=limit)]
            
            behavior_data = {
                'unique_authors': set(),
                'comment_lengths': [],
                'response_times': [],
                'participation_hours': []
            }
            
            for comment in comments:
                # Track unique authors
                if comment.author:
                    behavior_data['unique_authors'].add(comment.author.name)
                
                # Track comment lengths
                behavior_data['comment_lengths'].append(len(comment.body))
                
                # Track comment times
                behavior_data['participation_hours'].append(
                    datetime.fromtimestamp(comment.created_utc).hour
                )
                
                # Track response times if it's a reply
                if comment.parent_id.startswith('t1_'):
                    try:
                        parent = await self.reddit.comment(comment.parent_id[3:])
                        response_time = comment.created_utc - parent.created_utc
                        behavior_data['response_times'].append(response_time)
                    except:
                        pass
            
            # Convert set to length for JSON serialization
            behavior_data['unique_authors'] = len(behavior_data['unique_authors'])
            
            return behavior_data
        except Exception as e:
            self.logger.error(f"Error analyzing participation patterns: {str(e)}")
            return {}

    async def _get_trending_topics(self, subreddit_name: str, posts: List, limit: int = 100) -> Dict:
        """Analyze trending topics and discussions"""
        try:
            topic_data = {
                'common_words': {},
                'flairs': {},
                'trending_topics': []
            }
            
            # Common words to ignore
            stop_words = {'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i', 'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at'}
            
            for post in posts:
                # Track post flairs
                if post.link_flair_text:
                    topic_data['flairs'][post.link_flair_text] = topic_data['flairs'].get(post.link_flair_text, 0) + 1
                
                # Analyze words in titles
                words = post.title.lower().split()
                for word in words:
                    if word not in stop_words and len(word) > 3:
                        topic_data['common_words'][word] = topic_data['common_words'].get(word, 0) + 1
                
                # Track trending topics
                topic_data['trending_topics'].append({
                    'title': post.title,
                    'flair': post.link_flair_text,
                    'score': post.score,
                    'created_utc': post.created_utc
                })
            
            # Sort and limit common words
            topic_data['common_words'] = dict(
                sorted(topic_data['common_words'].items(), key=lambda x: x[1], reverse=True)[:20]
            )
            
            return topic_data
        except Exception as e:
            self.logger.error(f"Error getting trending topics: {str(e)}")
            return {}

    async def _analyze_post_timing(self, posts: List) -> Dict:
        """Analyze post timing patterns"""
        try:
            timing_data = {
                'hour_distribution': {},
                'day_distribution': {},
                'month_distribution': {}
            }
            
            for post in posts:
                dt = datetime.fromtimestamp(post.created_utc)
                
                # Track distributions
                hour = dt.hour
                day = dt.strftime('%A')
                month = dt.strftime('%B')
                
                timing_data['hour_distribution'][hour] = timing_data['hour_distribution'].get(hour, 0) + 1
                timing_data['day_distribution'][day] = timing_data['day_distribution'].get(day, 0) + 1
                timing_data['month_distribution'][month] = timing_data['month_distribution'].get(month, 0) + 1
            
            return timing_data
        except Exception as e:
            self.logger.error(f"Error analyzing post timing: {str(e)}")
            return {}

    async def _analyze_voting_patterns(self, posts: List) -> Dict:
        """Analyze voting patterns"""
        try:
            voting_data = {
                'upvote_ratio_distribution': {},
                'score_distribution': {},
                'controversial_posts': []
            }
            
            for post in posts:
                # Track upvote ratio
                ratio = round(post.upvote_ratio, 1)
                voting_data['upvote_ratio_distribution'][ratio] = \
                    voting_data['upvote_ratio_distribution'].get(ratio, 0) + 1
                
                # Track score distribution
                score_range = f"{(post.score // 100) * 100}-{((post.score // 100) + 1) * 100}"
                voting_data['score_distribution'][score_range] = \
                    voting_data['score_distribution'].get(score_range, 0) + 1
                
                # Track controversial posts
                if post.upvote_ratio < 0.5:
                    voting_data['controversial_posts'].append({
                        'title': post.title,
                        'score': post.score,
                        'upvote_ratio': post.upvote_ratio
                    })
            
            return voting_data
        except Exception as e:
            self.logger.error(f"Error analyzing voting patterns: {str(e)}")
            return {}

    async def _get_topic_engagement(self, posts: List) -> Dict:
        """Analyze topic engagement"""
        try:
            engagement_data = {
                'flair_engagement': {},
                'keyword_engagement': {},
                'time_based_engagement': {}
            }
            
            for post in posts:
                # Track flair engagement
                if post.link_flair_text:
                    if post.link_flair_text not in engagement_data['flair_engagement']:
                        engagement_data['flair_engagement'][post.link_flair_text] = {
                            'posts': 0,
                            'total_score': 0,
                            'total_comments': 0
                        }
                    
                    engagement_data['flair_engagement'][post.link_flair_text]['posts'] += 1
                    engagement_data['flair_engagement'][post.link_flair_text]['total_score'] += post.score
                    engagement_data['flair_engagement'][post.link_flair_text]['total_comments'] += post.num_comments
                
                # Track time-based engagement
                hour = datetime.fromtimestamp(post.created_utc).hour
                if hour not in engagement_data['time_based_engagement']:
                    engagement_data['time_based_engagement'][hour] = {
                        'posts': 0,
                        'avg_score': 0,
                        'avg_comments': 0
                    }
                
                engagement_data['time_based_engagement'][hour]['posts'] += 1
                engagement_data['time_based_engagement'][hour]['avg_score'] = \
                    (engagement_data['time_based_engagement'][hour]['avg_score'] * 
                     (engagement_data['time_based_engagement'][hour]['posts'] - 1) + 
                     post.score) / engagement_data['time_based_engagement'][hour]['posts']
                engagement_data['time_based_engagement'][hour]['avg_comments'] = \
                    (engagement_data['time_based_engagement'][hour]['avg_comments'] * 
                     (engagement_data['time_based_engagement'][hour]['posts'] - 1) + 
                     post.num_comments) / engagement_data['time_based_engagement'][hour]['posts']
            
            return engagement_data
        except Exception as e:
            self.logger.error(f"Error analyzing topic engagement: {str(e)}")
            return {}

    async def _analyze_time_based_engagement(self, posts: List) -> Dict:
        """Analyze engagement patterns based on posting time"""
        try:
            time_data = {
                'hourly_engagement': {},
                'daily_engagement': {},
                'peak_hours': [],
                'peak_days': [],
                'engagement_trends': {}
            }
            
            for post in posts:
                dt = datetime.fromtimestamp(post.created_utc)
                hour = dt.hour
                day = dt.strftime('%A')
                
                # Initialize if not exists
                if hour not in time_data['hourly_engagement']:
                    time_data['hourly_engagement'][hour] = {
                        'posts': 0,
                        'total_score': 0,
                        'total_comments': 0,
                        'avg_score': 0,
                        'avg_comments': 0
                    }
                if day not in time_data['daily_engagement']:
                    time_data['daily_engagement'][day] = {
                        'posts': 0,
                        'total_score': 0,
                        'total_comments': 0,
                        'avg_score': 0,
                        'avg_comments': 0
                    }
                
                # Update hourly stats
                hour_stats = time_data['hourly_engagement'][hour]
                hour_stats['posts'] += 1
                hour_stats['total_score'] += post.score
                hour_stats['total_comments'] += post.num_comments
                hour_stats['avg_score'] = hour_stats['total_score'] / hour_stats['posts']
                hour_stats['avg_comments'] = hour_stats['total_comments'] / hour_stats['posts']
                
                # Update daily stats
                day_stats = time_data['daily_engagement'][day]
                day_stats['posts'] += 1
                day_stats['total_score'] += post.score
                day_stats['total_comments'] += post.num_comments
                day_stats['avg_score'] = day_stats['total_score'] / day_stats['posts']
                day_stats['avg_comments'] = day_stats['total_comments'] / day_stats['posts']
            
            # Find peak hours (top 3)
            time_data['peak_hours'] = sorted(
                [(hour, stats['avg_score']) for hour, stats in time_data['hourly_engagement'].items()],
                key=lambda x: x[1],
                reverse=True
            )[:3]
            
            # Find peak days (top 3)
            time_data['peak_days'] = sorted(
                [(day, stats['avg_score']) for day, stats in time_data['daily_engagement'].items()],
                key=lambda x: x[1],
                reverse=True
            )[:3]
            
            return time_data
        except Exception as e:
            self.logger.error(f"Error analyzing time-based engagement: {str(e)}")
            return {}

    async def _analyze_post_awards(self, posts: List) -> Dict:
        """Analyze post awards and their impact"""
        try:
            awards_data = {
                'total_awards': 0,
                'unique_awards': set(),
                'award_distribution': {},
                'award_impact': {},
                'top_awarded_posts': []
            }
            
            for post in posts:
                if hasattr(post, 'all_awardings'):
                    # Track awards
                    post_awards = len(post.all_awardings)
                    awards_data['total_awards'] += post_awards
                    
                    # Track unique awards
                    for award in post.all_awardings:
                        award_name = award.get('name', 'Unknown')
                        awards_data['unique_awards'].add(award_name)
                        awards_data['award_distribution'][award_name] = \
                            awards_data['award_distribution'].get(award_name, 0) + 1
                    
                    # Track award impact
                    if post_awards > 0:
                        impact_key = f"{(post_awards // 5) * 5}-{((post_awards // 5) + 1) * 5}"
                        if impact_key not in awards_data['award_impact']:
                            awards_data['award_impact'][impact_key] = {
                                'posts': 0,
                                'avg_score': 0,
                                'avg_comments': 0
                            }
                        
                        impact = awards_data['award_impact'][impact_key]
                        impact['posts'] += 1
                        impact['avg_score'] = (impact['avg_score'] * (impact['posts'] - 1) + post.score) / impact['posts']
                        impact['avg_comments'] = (impact['avg_comments'] * (impact['posts'] - 1) + post.num_comments) / impact['posts']
                    
                    # Track top awarded posts
                    if post_awards > 0:
                        awards_data['top_awarded_posts'].append({
                            'title': post.title,
                            'awards': post_awards,
                            'score': post.score,
                            'comments': post.num_comments
                        })
            
            # Convert set to list for JSON serialization
            awards_data['unique_awards'] = list(awards_data['unique_awards'])
            
            # Sort top awarded posts
            awards_data['top_awarded_posts'] = sorted(
                awards_data['top_awarded_posts'],
                key=lambda x: x['awards'],
                reverse=True
            )[:10]
            
            return awards_data
        except Exception as e:
            self.logger.error(f"Error analyzing post awards: {str(e)}")
            return {}

    async def _analyze_commenting_patterns(self, posts: List) -> Dict:
        """Analyze commenting patterns and discussion dynamics"""
        try:
            comment_data = {
                'total_comments': 0,
                'avg_comment_length': 0,
                'comment_depth_distribution': {},
                'response_times': [],
                'discussion_metrics': {
                    'avg_thread_length': 0,
                    'max_thread_depth': 0,
                    'branching_factor': 0
                },
                'user_participation': {
                    'unique_commenters': set(),
                    'repeat_commenters': {},
                    'top_commenters': []
                }
            }
            
            total_threads = 0
            total_length = 0
            
            for post in posts:
                post.comments.replace_more(limit=0)  # Fetch comment tree
                
                # Track total comments
                comment_data['total_comments'] += post.num_comments
                
                # Analyze comment tree
                async def process_comment_tree(comment, depth=0):
                    nonlocal total_length
                    
                    # Track comment depth
                    comment_data['comment_depth_distribution'][depth] = \
                        comment_data['comment_depth_distribution'].get(depth, 0) + 1
                    
                    # Track comment length
                    if hasattr(comment, 'body'):
                        total_length += len(comment.body)
                    
                    # Track user participation
                    if hasattr(comment, 'author') and comment.author:
                        author_name = comment.author.name
                        comment_data['user_participation']['unique_commenters'].add(author_name)
                        comment_data['user_participation']['repeat_commenters'][author_name] = \
                            comment_data['user_participation']['repeat_commenters'].get(author_name, 0) + 1
                    
                    # Track response times for replies
                    if hasattr(comment, 'parent_id') and comment.parent_id.startswith('t1_'):
                        try:
                            parent = await self.reddit.comment(comment.parent_id[3:])
                            response_time = comment.created_utc - parent.created_utc
                            comment_data['response_times'].append(response_time)
                        except:
                            pass
                    
                    # Process replies
                    if hasattr(comment, 'replies'):
                        for reply in comment.replies:
                            await process_comment_tree(reply, depth + 1)
                
                # Process each comment tree
                for top_level_comment in post.comments:
                    await process_comment_tree(top_level_comment)
                    total_threads += 1
            
            # Calculate averages and metrics
            if comment_data['total_comments'] > 0:
                comment_data['avg_comment_length'] = total_length / comment_data['total_comments']
            
            if total_threads > 0:
                comment_data['discussion_metrics']['avg_thread_length'] = \
                    comment_data['total_comments'] / total_threads
            
            # Calculate max thread depth
            if comment_data['comment_depth_distribution']:
                comment_data['discussion_metrics']['max_thread_depth'] = \
                    max(comment_data['comment_depth_distribution'].keys())
            
            # Calculate branching factor
            if len(comment_data['comment_depth_distribution']) > 1:
                total_parents = sum(count for depth, count in comment_data['comment_depth_distribution'].items() if depth < max(comment_data['comment_depth_distribution'].keys()))
                total_children = sum(count for depth, count in comment_data['comment_depth_distribution'].items() if depth > 0)
                if total_parents > 0:
                    comment_data['discussion_metrics']['branching_factor'] = total_children / total_parents
            
            # Convert set to list for JSON serialization
            comment_data['user_participation']['unique_commenters'] = \
                list(comment_data['user_participation']['unique_commenters'])
            
            # Get top commenters
            comment_data['user_participation']['top_commenters'] = sorted(
                [{'user': k, 'comments': v} for k, v in comment_data['user_participation']['repeat_commenters'].items()],
                key=lambda x: x['comments'],
                reverse=True
            )[:10]
            
            return comment_data
        except Exception as e:
            self.logger.error(f"Error analyzing commenting patterns: {str(e)}")
            return {}

    async def get_subscriber_metrics(self) -> Dict:
        """Get subscriber-related metrics for the subreddit"""
        try:
            current_subscribers = (await self.reddit.subreddit('HarmonyKorine')).subscribers
            
            # Get historical data if available (need to implement storage)
            # For now, return current metrics
            metrics = {
                'total_subscribers': current_subscribers,
                'active_users': (await self.reddit.subreddit('HarmonyKorine')).active_user_count,
                'created_utc': (await self.reddit.subreddit('HarmonyKorine')).created_utc,
                'subreddit_type': (await self.reddit.subreddit('HarmonyKorine')).subreddit_type,
                'last_updated': datetime.now().isoformat()
            }
            
            return metrics
        except Exception as e:
            self.logger.error(f"Error getting subscriber metrics: {str(e)}")
            return {}

    async def analyze_content_preferences(self, timeframe: str = 'month') -> Dict:
        """Analyze content preferences and trends"""
        try:
            if timeframe == 'month':
                posts = [post async for post in (await self.reddit.subreddit('HarmonyKorine')).top(time_filter='month', limit=100)]
            elif timeframe == 'week':
                posts = [post async for post in (await self.reddit.subreddit('HarmonyKorine')).top(time_filter='week', limit=100)]
            else:
                posts = [post async for post in (await self.reddit.subreddit('HarmonyKorine')).top(time_filter='all', limit=100)]

            content_analysis = {
                'post_types': {},
                'top_domains': {},
                'flair_distribution': {},
                'posting_patterns': {
                    'by_hour': {},
                    'by_day': {}
                },
                'engagement_stats': {
                    'avg_score': 0,
                    'avg_comments': 0,
                    'upvote_ratio': 0
                }
            }

            total_score = 0
            total_comments = 0
            total_ratio = 0

            for post in posts:
                # Analyze post type
                post_type = 'text' if post.is_self else 'link'
                if hasattr(post, 'post_hint'):
                    post_type = post.post_hint
                content_analysis['post_types'][post_type] = content_analysis['post_types'].get(post_type, 0) + 1
                
                # Track domains for link posts
                if not post.is_self:
                    domain = post.domain
                    content_analysis['top_domains'][domain] = content_analysis['top_domains'].get(domain, 0) + 1
                
                # Track flairs
                if post.link_flair_text:
                    content_analysis['flair_distribution'][post.link_flair_text] = \
                        content_analysis['flair_distribution'].get(post.link_flair_text, 0) + 1
                
                # Track posting time
                post_time = datetime.fromtimestamp(post.created_utc)
                
                # Track distributions
                hour = post_time.hour
                day = post_time.strftime('%A')
                
                content_analysis['posting_patterns']['by_hour'][hour] = \
                    content_analysis['posting_patterns']['by_hour'].get(hour, 0) + 1
                content_analysis['posting_patterns']['by_day'][day] = \
                    content_analysis['posting_patterns']['by_day'].get(day, 0) + 1

                # Aggregate engagement metrics
                total_score += post.score
                total_comments += post.num_comments
                total_ratio += post.upvote_ratio

            # Calculate averages
            num_posts = len(posts)
            if num_posts > 0:
                content_analysis['engagement_stats']['avg_score'] = total_score / num_posts
                content_analysis['engagement_stats']['avg_comments'] = total_comments / num_posts
                content_analysis['engagement_stats']['upvote_ratio'] = total_ratio / num_posts

            # Sort dictionaries by value for better insights
            content_analysis['post_types'] = dict(sorted(
                content_analysis['post_types'].items(),
                key=lambda x: x[1],
                reverse=True
            ))
            content_analysis['top_domains'] = dict(sorted(
                content_analysis['top_domains'].items(),
                key=lambda x: x[1],
                reverse=True
            ))
            content_analysis['flair_distribution'] = dict(sorted(
                content_analysis['flair_distribution'].items(),
                key=lambda x: x[1],
                reverse=True
            ))

            return content_analysis
        except Exception as e:
            self.logger.error(f"Error analyzing content preferences: {str(e)}")
            return {}

    async def get_subreddit_stats(self) -> Dict:
        """Get detailed statistics about the HarmonyKorine subreddit"""
        stats = {
            'subscriber_count': 0,
            'active_users': 0,
            'daily_posts': 0,
            'daily_comments': 0,
            'avg_score': 0,
            'engagement_rate': 0,
            'post_frequency': defaultdict(int),
            'top_contributors': defaultdict(int),
            'content_breakdown': defaultdict(int),
            'flair_distribution': defaultdict(int)
        }

        try:
            subreddit = await self.reddit.subreddit('HarmonyKorine')
            stats['subscriber_count'] = subreddit.subscribers
            stats['active_users'] = subreddit.active_user_count
            
            # Analyze recent posts
            total_score = 0
            post_count = 0
            unique_authors = set()
            
            posts = [post async for post in subreddit.new(limit=100)]
            
            for post in posts:
                post_count += 1
                total_score += post.score
                
                if post.author:
                    unique_authors.add(post.author.name)
                    stats['top_contributors'][post.author.name] += 1
                
                # Track post types
                if post.is_self:
                    stats['content_breakdown']['text'] += 1
                elif hasattr(post, 'post_hint'):
                    stats['content_breakdown'][post.post_hint] += 1
                else:
                    stats['content_breakdown']['other'] += 1
                    
                # Track post flairs
                if post.link_flair_text:
                    stats['flair_distribution'][post.link_flair_text] += 1
                    
                # Track posting time
                post_hour = datetime.fromtimestamp(post.created_utc).hour
                stats['post_frequency'][post_hour] += 1
            
            if post_count > 0:
                stats['avg_score'] = total_score / post_count
                
            # Get daily post and comment counts
            daily_posts = len([post async for post in subreddit.new(time_filter='day')])
            daily_comments = len([comment async for comment in subreddit.comments(time_filter='day')])
            
            stats['daily_posts'] = daily_posts
            stats['daily_comments'] = daily_comments
            
            if stats['subscriber_count'] > 0:
                stats['engagement_rate'] = ((daily_posts + daily_comments) / stats['subscriber_count']) * 100
                
            # Process the data
            stats['top_contributors'] = dict(sorted(
                stats['top_contributors'].items(),
                key=lambda x: x[1],
                reverse=True
            )[:10])
            
            stats['content_breakdown'] = dict(stats['content_breakdown'])
            stats['flair_distribution'] = dict(stats['flair_distribution'])
            stats['post_frequency'] = dict(stats['post_frequency'])
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error in get_subreddit_stats: {str(e)}")
            return stats

    async def get_subreddit_stats(self, subreddit_name: str) -> Dict:
        """
        Get detailed statistics about a subreddit and its users.
        
        Args:
            subreddit_name (str): Name of the subreddit to analyze
            
        Returns:
            Dict: Dictionary containing various subreddit statistics
        """
        try:
            subreddit = await self.reddit.subreddit(subreddit_name)
            stats = {
                'basic_stats': {
                    'subscribers': subreddit.subscribers,
                    'active_users': subreddit.active_user_count,
                    'created_utc': datetime.fromtimestamp(subreddit.created_utc),
                    'description': subreddit.description,
                },
                'content_stats': await self._get_content_stats(subreddit),
                'user_stats': await self._get_user_stats(subreddit),
                'activity_stats': await self._get_activity_stats(subreddit),
            }
            self.logger.info(f"Successfully collected stats for r/{subreddit_name}")
            return stats
        except Exception as e:
            self.logger.error(f"Error collecting subreddit stats: {str(e)}")
            return {}
            
    async def _get_user_stats(self, subreddit) -> Dict:
        """Get statistics about subreddit users"""
        try:
            # Analyze contributors from recent posts and comments
            posts = [post async for post in subreddit.new(limit=100)]  # Reduced from 500 to improve speed
            users = set()
            user_data = []
            
            # First pass: collect unique users
            for post in posts:
                if post.author and post.author != '[deleted]':
                    users.add(post.author)
                
                # Get a sample of commenters
                try:
                    post.comments.replace_more(limit=0)
                    for comment in post.comments.list()[:5]:  # Reduced from 10 to improve speed
                        if comment.author and comment.author != '[deleted]':
                            users.add(comment.author)
                except Exception:
                    pass

            # Process users in batches with rate limiting
            for user_batch in batch_generator(list(users), batch_size=25):
                batch_data = await self._process_user_batch(user_batch)
                user_data.extend([d for d in batch_data if d])

            if not user_data:
                return {}

            # Calculate statistics
            comment_karma = [d['comment_karma'] for d in user_data]
            account_ages = [d['account_age'] for d in user_data]
            
            return {
                'unique_contributors': len(users),
                'karma_stats': {
                    'mean': sum(comment_karma) / len(comment_karma) if comment_karma else 0,
                    'median': sorted(comment_karma)[len(comment_karma)//2] if comment_karma else 0,
                    'max': max(comment_karma) if comment_karma else 0,
                    'min': min(comment_karma) if comment_karma else 0
                },
                'account_age_stats': {
                    'mean_days': sum(account_ages) / len(account_ages) if account_ages else 0,
                    'median_days': sorted(account_ages)[len(account_ages)//2] if account_ages else 0,
                    'oldest_days': max(account_ages) if account_ages else 0,
                    'newest_days': min(account_ages) if account_ages else 0
                }
            }
        except Exception as e:
            self.logger.error(f"Error collecting user stats: {str(e)}")
            return {}

    async def get_top_posts(self, time_filter: str = 'month', limit: int = 100) -> pd.DataFrame:
        """Get and analyze top posts from EDGLRD subreddit"""
        try:
            posts_data = []
            async for post in self.reddit.subreddit('EDGLRD').top(time_filter=time_filter, limit=limit):
                post_data = {
                    'title': post.title,
                    'score': post.score,
                    'upvote_ratio': post.upvote_ratio,
                    'num_comments': post.num_comments,
                    'created_utc': post.created_utc,
                    'author': str(post.author),
                    'is_original_content': post.is_original_content,
                    'link_flair_text': post.link_flair_text,
                    'post_hint': getattr(post, 'post_hint', None),
                    'url': post.url,
                    'selftext': post.selftext if post.is_self else '',
                    'engagement_score': post.score * post.upvote_ratio * (1 + post.num_comments/100)
                }
                posts_data.append(post_data)
            
            df = pd.DataFrame(posts_data)
            return df
        except Exception as e:
            self.logger.error(f"Error collecting top posts: {str(e)}")
            return pd.DataFrame()

    async def analyze_user_demographics(self, sample_size: int = 100) -> Dict:
        """Analyze user demographics and interests based on active users"""
        demographics = {
            'subreddit_interests': defaultdict(int),
            'active_hours': defaultdict(int),
            'account_ages': [],
            'karma_distribution': [],
            'top_active_subreddits': defaultdict(int),
            'content_preferences': defaultdict(int),
            'engagement_patterns': defaultdict(int)
        }
        
        try:
            # Get recent active users from comments and posts
            active_users = await self.collect_users()

            # Process users in batches
            for user_batch in batch_generator(list(active_users), batch_size=25):
                user_data = await self._process_user_batch(user_batch)
                for data in user_data:
                    if data:
                        demographics['account_ages'].append(data['account_age'])
                        demographics['karma_distribution'].append({
                            'comment_karma': data['comment_karma'],
                            'total_karma': data['total_karma']
                        })

            # Process the collected data
            if demographics['account_ages']:
                demographics['avg_account_age'] = sum(demographics['account_ages']) / len(demographics['account_ages'])
                
            if demographics['karma_distribution']:
                avg_comment_karma = sum(k['comment_karma'] for k in demographics['karma_distribution']) / len(demographics['karma_distribution'])
                avg_total_karma = sum(k['total_karma'] for k in demographics['karma_distribution']) / len(demographics['karma_distribution'])
                demographics['avg_karma'] = {
                    'comment_karma': avg_comment_karma,
                    'total_karma': avg_total_karma
                }
            
            return demographics
            
        except Exception as e:
            self.logger.error(f"Error analyzing user demographics: {str(e)}")
            return demographics

    async def get_subreddit_stats(self) -> Dict:
        """Get detailed statistics about the EDGLRD subreddit"""
        stats = {
            'subscriber_count': 0,
            'active_users': 0,
            'daily_posts': 0,
            'daily_comments': 0,
            'avg_score': 0,
            'engagement_rate': 0,
            'post_frequency': defaultdict(int),
            'top_contributors': defaultdict(int),
            'content_breakdown': defaultdict(int),
            'flair_distribution': defaultdict(int)
        }
        
        try:
            subreddit = await self.reddit.subreddit('EDGLRD')
            stats['subscriber_count'] = subreddit.subscribers
            stats['active_users'] = subreddit.active_user_count
            
            # Analyze recent posts
            total_score = 0
            post_count = 0
            unique_authors = set()
            
            posts = [post async for post in subreddit.new(limit=100)]
            
            for post in posts:
                post_count += 1
                total_score += post.score
                
                if post.author:
                    unique_authors.add(post.author.name)
                    stats['top_contributors'][post.author.name] += 1
                
                # Track post types
                if post.is_self:
                    stats['content_breakdown']['text'] += 1
                elif hasattr(post, 'post_hint'):
                    stats['content_breakdown'][post.post_hint] += 1
                else:
                    stats['content_breakdown']['other'] += 1
                    
                # Track post flairs
                if post.link_flair_text:
                    stats['flair_distribution'][post.link_flair_text] += 1
                    
                # Track posting time
                post_hour = datetime.fromtimestamp(post.created_utc).hour
                stats['post_frequency'][post_hour] += 1
            
            if post_count > 0:
                stats['avg_score'] = total_score / post_count
                
            # Get daily post and comment counts
            daily_posts = len([post async for post in subreddit.new(time_filter='day')])
            daily_comments = len([comment async for comment in subreddit.comments(time_filter='day')])
            
            stats['daily_posts'] = daily_posts
            stats['daily_comments'] = daily_comments
            
            if stats['subscriber_count'] > 0:
                stats['engagement_rate'] = ((daily_posts + daily_comments) / stats['subscriber_count']) * 100
                
            # Process the data
            stats['top_contributors'] = dict(sorted(
                stats['top_contributors'].items(),
                key=lambda x: x[1],
                reverse=True
            )[:10])
            
            stats['content_breakdown'] = dict(stats['content_breakdown'])
            stats['flair_distribution'] = dict(stats['flair_distribution'])
            stats['post_frequency'] = dict(stats['post_frequency'])
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error in get_subreddit_stats: {str(e)}")
            return stats

    async def get_subreddit_stats(self, subreddit_name: str) -> Dict:
        """
        Get detailed statistics about a subreddit and its users.
        
        Args:
            subreddit_name (str): Name of the subreddit to analyze
            
        Returns:
            Dict: Dictionary containing various subreddit statistics
        """
        try:
            subreddit = await self.reddit.subreddit(subreddit_name)
            stats = {
                'basic_stats': {
                    'subscribers': subreddit.subscribers,
                    'active_users': subreddit.active_user_count,
                    'created_utc': datetime.fromtimestamp(subreddit.created_utc),
                    'description': subreddit.description,
                },
                'content_stats': await self._get_content_stats(subreddit),
                'user_stats': await self._get_user_stats(subreddit),
                'activity_stats': await self._get_activity_stats(subreddit),
            }
            self.logger.info(f"Successfully collected stats for r/{subreddit_name}")
            return stats
        except Exception as e:
            self.logger.error(f"Error collecting subreddit stats: {str(e)}")
            return {}
            
    async def _get_user_stats(self, subreddit) -> Dict:
        """Get statistics about subreddit users"""
        try:
            # Analyze contributors from recent posts and comments
            posts = [post async for post in subreddit.new(limit=100)]  # Reduced from 500 to improve speed
            users = set()
            user_data = []
            
            # First pass: collect unique users
            for post in posts:
                if post.author and post.author != '[deleted]':
                    users.add(post.author)
                
                # Get a sample of commenters
                try:
                    post.comments.replace_more(limit=0)
                    for comment in post.comments.list()[:5]:  # Reduced from 10 to improve speed
                        if comment.author and comment.author != '[deleted]':
                            users.add(comment.author)
                except Exception:
                    pass

            # Process users in batches with rate limiting
            for user_batch in batch_generator(list(users), batch_size=25):
                batch_data = await self._process_user_batch(user_batch)
                user_data.extend([d for d in batch_data if d])

            if not user_data:
                return {}

            # Calculate statistics
            comment_karma = [d['comment_karma'] for d in user_data]
            account_ages = [d['account_age'] for d in user_data]
            
            return {
                'unique_contributors': len(users),
                'karma_stats': {
                    'mean': sum(comment_karma) / len(comment_karma) if comment_karma else 0,
                    'median': sorted(comment_karma)[len(comment_karma)//2] if comment_karma else 0,
                    'max': max(comment_karma) if comment_karma else 0,
                    'min': min(comment_karma) if comment_karma else 0
                },
                'account_age_stats': {
                    'mean_days': sum(account_ages) / len(account_ages) if account_ages else 0,
                    'median_days': sorted(account_ages)[len(account_ages)//2] if account_ages else 0,
                    'oldest_days': max(account_ages) if account_ages else 0,
                    'newest_days': min(account_ages) if account_ages else 0
                }
            }
        except Exception as e:
            self.logger.error(f"Error collecting user stats: {str(e)}")
            return {}

    async def analyze_trending_keywords(self, posts_df: pd.DataFrame) -> Dict:
        """
        Analyze trending keywords and phrases in posts
        """
        try:
            from collections import Counter
            import re
            
            # Combine title and text for analysis
            all_text = ' '.join(posts_df['title'].fillna('') + ' ' + posts_df['text'].fillna(''))
            
            # Clean text and extract words
            words = re.findall(r'\b\w+\b', all_text.lower())
            
            # Remove common stop words
            stop_words = {'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i', 'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at'}
            words = [word for word in words if word not in stop_words and len(word) > 2]
            
            # Get word frequencies
            word_freq = Counter(words).most_common(20)
            
            # Calculate engagement per keyword
            keyword_engagement = defaultdict(list)
            for _, row in posts_df.iterrows():
                engagement = row['score'] + row['num_comments']
                text = f"{row['title']} {row['text']}"
                for word, _ in word_freq:
                    if word in text.lower():
                        keyword_engagement[word].append(engagement)
            
            # Calculate average engagement per keyword
            keyword_metrics = {
                word: {
                    'frequency': freq,
                    'avg_engagement': sum(keyword_engagement[word])/len(keyword_engagement[word]) if keyword_engagement[word] else 0
                }
                for word, freq in word_freq
            }
            
            return keyword_metrics
            
        except Exception as e:
            logger.error(f"Error analyzing trending keywords: {str(e)}")
            return {}

    async def get_content_suggestions(self, posts_df: pd.DataFrame) -> Dict:
        """
        Generate content suggestions based on historical performance
        """
        try:
            suggestions = {
                'best_post_types': {},
                'optimal_timing': {},
                'engaging_topics': [],
                'title_patterns': []
            }
            
            if posts_df.empty:
                return suggestions
                
            # Analyze post types (text vs link)
            posts_df['is_text'] = posts_df['url'].apply(lambda x: x.startswith('https://www.reddit.com/r/'))
            post_types = posts_df.groupby('is_text').agg({
                'score': 'mean',
                'num_comments': 'mean'
            }).to_dict('index')
            
            suggestions['best_post_types'] = {
                'text_posts': {'avg_score': post_types.get(True, {}).get('score', 0)},
                'link_posts': {'avg_score': post_types.get(False, {}).get('score', 0)}
            }
            
            # Analyze posting time
            posts_df['hour'] = posts_df['created_utc'].dt.hour
            time_performance = posts_df.groupby('hour').agg({
                'score': 'mean',
                'num_comments': 'mean'
            }).to_dict('index')
            
            suggestions['optimal_timing'] = {
                hour: {'avg_score': metrics['score'], 'avg_comments': metrics['num_comments']}
                for hour, metrics in time_performance.items()
            }
            
            # Find engaging topics
            high_performing = posts_df[posts_df['score'] > posts_df['score'].mean()]
            topics = [
                {
                    'title': row['title'],
                    'score': row['score'],
                    'comments': row['num_comments']
                }
                for _, row in high_performing.nlargest(5, 'score').iterrows()
            ]
            suggestions['engaging_topics'] = topics
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error generating content suggestions: {str(e)}")
            return {}

    async def get_audience_activity_patterns(self, posts_df: pd.DataFrame) -> Dict:
        """
        Analyze audience activity patterns
        """
        try:
            patterns = {
                'daily_activity': {},
                'engagement_trends': {},
                'community_growth': {}
            }
            
            if posts_df.empty:
                return patterns
                
            # Daily activity analysis
            posts_df['day_of_week'] = posts_df['created_utc'].dt.day_name()
            daily_stats = posts_df.groupby('day_of_week').agg({
                'score': ['mean', 'count'],
                'num_comments': 'mean'
            }).to_dict('index')
            
            patterns['daily_activity'] = {
                day: {
                    'posts_count': stats[('score', 'count')],
                    'avg_score': stats[('score', 'mean')],
                    'avg_comments': stats[('num_comments', 'mean')]
                }
                for day, stats in daily_stats.items()
            }
            
            # Engagement trends over time
            posts_df['date'] = posts_df['created_utc'].dt.date
            engagement_trends = posts_df.groupby('date').agg({
                'score': 'mean',
                'num_comments': 'mean'
            }).to_dict('index')
            
            patterns['engagement_trends'] = {
                str(date): {
                    'avg_score': metrics['score'],
                    'avg_comments': metrics['num_comments']
                }
                for date, metrics in engagement_trends.items()
            }
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error analyzing audience patterns: {str(e)}")
            return {}

    async def collect_profile_data(self) -> pd.DataFrame:
        """Collect subreddit profile data"""
        try:
            subreddit = await self.reddit.subreddit('HarmonyKorrine')
            profile_data = {
                'name': subreddit.display_name,
                'subscribers': subreddit.subscribers,
                'active_users': subreddit.active_user_count,
                'description': subreddit.description,
                'created_utc': datetime.fromtimestamp(subreddit.created_utc),
                'over18': subreddit.over18,
                'platform': 'reddit'
            }
            return pd.DataFrame([profile_data])
        except Exception as e:
            logger.error(f"Error collecting profile data: {str(e)}")
            return pd.DataFrame()

    async def collect_content_data(self, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Collect content data within date range"""
        try:
            # Collect posts from subreddit
            subreddit_posts = await self.collect_subreddit_posts('HarmonyKorrine', limit=500)
            
            # Collect EDGLRD search results
            edglrd_posts = await self.search_reddit_posts('EDGLRD', limit=500)
            
            # Combine and filter by date
            all_posts = pd.concat([subreddit_posts, edglrd_posts]).drop_duplicates()
            
            mask = (all_posts['created_utc'] >= start_date) & (all_posts['created_utc'] <= end_date)
            return all_posts[mask]
            
        except Exception as e:
            logger.error(f"Error collecting content data: {str(e)}")
            return pd.DataFrame()

    async def collect_engagement_data(self) -> pd.DataFrame:
        """Collect engagement metrics"""
        try:
            # Get recent posts for engagement analysis
            posts_df = await self.collect_subreddit_posts('HarmonyKorrine', limit=100)
            
            if posts_df.empty:
                return pd.DataFrame()
            
            engagement_data = []
            for _, post in posts_df.iterrows():
                engagement_data.append({
                    'post_id': post['id'],
                    'score': post['score'],
                    'num_comments': post['num_comments'],
                    'upvote_ratio': getattr(self.reddit.submission(id=post['id']), 'upvote_ratio', 0),
                    'created_utc': post['created_utc'],
                    'platform': 'reddit'
                })
            
            return pd.DataFrame(engagement_data)
            
        except Exception as e:
            logger.error(f"Error collecting engagement data: {str(e)}")
            return pd.DataFrame()

    async def collect_audience_data(self, subreddit_name: str, time_period: str = 'month') -> Dict:
        """Collect comprehensive audience data with investor-focused metrics
        
        Args:
            subreddit_name (str): Name of subreddit to analyze
            time_period (str): Time period for analysis ('day', 'week', 'month')
            
        Returns:
            Dict containing audience metrics and growth indicators
        """
        try:
            subreddit = await self.reddit.subreddit(subreddit_name)
            
            # Collect comprehensive metrics
            metrics = {
                'subscriber_count': await subreddit.subscribers,
                'active_users': 0,  # Will be populated
                'growth_rate': 0,   # Will be calculated
                'engagement_metrics': {
                    'total_posts': 0,
                    'total_comments': 0,
                    'total_engagement': 0,
                    'engagement_rate': 0
                },
                'conversion_metrics': {
                    'click_through_rate': 0,
                    'conversion_rate': 0
                },
                'content_performance': {
                    'viral_posts': [],
                    'top_performing_topics': {},
                    'best_posting_times': {}
                },
                'timestamp': datetime.now().isoformat()
            }
            
            # Get active users
            metrics['active_users'] = await subreddit.active_user_count
            
            # Analyze recent posts for engagement metrics
            async for submission in subreddit.new(limit=100):
                metrics['engagement_metrics']['total_posts'] += 1
                metrics['engagement_metrics']['total_comments'] += submission.num_comments
                engagement = submission.score + submission.num_comments
                metrics['engagement_metrics']['total_engagement'] += engagement
                
                # Track viral posts (high engagement)
                if engagement > 1000:
                    metrics['content_performance']['viral_posts'].append({
                        'title': submission.title,
                        'score': submission.score,
                        'comments': submission.num_comments,
                        'url': submission.url
                    })
                
                # Track posting time performance
                post_hour = datetime.fromtimestamp(submission.created_utc).hour
                metrics['content_performance']['best_posting_times'][post_hour] = \
                    metrics['content_performance']['best_posting_times'].get(post_hour, 0) + engagement
            
            # Calculate engagement rate
            if metrics['subscriber_count'] > 0:
                metrics['engagement_metrics']['engagement_rate'] = \
                    (metrics['engagement_metrics']['total_engagement'] / metrics['subscriber_count']) * 100
            
            # Estimate conversion metrics (based on available data)
            metrics['conversion_metrics']['click_through_rate'] = \
                (metrics['engagement_metrics']['total_engagement'] / (metrics['subscriber_count'] or 1)) * 100
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting audience data: {str(e)}")
            return {}

    async def collect_users(self) -> set:
        """Collect active users from recent posts and comments"""
        active_users = set()
        try:
            # Get users from recent posts
            async for post in self.reddit.subreddit('EDGLRD').new(limit=50):
                if post.author:
                    active_users.add(post.author)
            
            # Get users from recent comments
            async for comment in self.reddit.subreddit('EDGLRD').comments(limit=100):
                if comment.author:
                    active_users.add(comment.author)
                    
            return active_users
            
        except Exception as e:
            self.logger.error(f"Error collecting users: {str(e)}")
            return active_users

    async def collect_subreddit_data(self, subreddit_name: str = "HarmonyKorrine", limit: int = 100) -> List[Dict]:
        """Collect data from specified subreddit
        
        Args:
            subreddit_name (str): Name of subreddit to collect from
            limit (int): Maximum number of posts to collect
            
        Returns:
            List[Dict]: List of collected post data
        """
        try:
            posts = []
            async with asyncpraw.Reddit(
                client_id=self.client_id,
                client_secret=self.client_secret,
                user_agent=self.user_agent
            ) as reddit:
                subreddit = await reddit.subreddit(subreddit_name)
                
                # Collect hot posts
                async for post in subreddit.hot(limit=limit):
                    post_data = await self._extract_post_data(post)
                    posts.append(post_data)
                    
                # Collect posts with EDGLRD keyword
                async for post in subreddit.search("EDGLRD", limit=limit):
                    post_data = await self._extract_post_data(post)
                    posts.append(post_data)
                    
            return posts
        except Exception as e:
            self.logger.error(f"Error collecting subreddit data: {str(e)}")
            return []

    async def collect_related_interests(self) -> Dict:
        """Collect data about related interests of r/HarmonyKorrine users"""
        try:
            related_subs = defaultdict(int)
            user_posts = []
            
            # Get users from HarmonyKorrine subreddit
            async with asyncpraw.Reddit(
                client_id=self.client_id,
                client_secret=self.client_secret,
                user_agent=self.user_agent
            ) as reddit:
                subreddit = await reddit.subreddit("HarmonyKorrine")
                async for post in subreddit.hot(limit=50):
                    author = post.author
                    if author:
                        async for user_post in author.submissions.new(limit=20):
                            sub = user_post.subreddit.display_name
                            if sub != "HarmonyKorrine":
                                related_subs[sub] += 1
                            user_posts.append(await self._extract_post_data(user_post))
            
            return {
                'related_subreddits': dict(sorted(related_subs.items(), key=lambda x: x[1], reverse=True)),
                'user_posts': user_posts
            }
        except Exception as e:
            self.logger.error(f"Error collecting related interests: {str(e)}")
            return {'related_subreddits': {}, 'user_posts': []}

    async def _extract_post_data(self, post) -> Dict:
        """Extract relevant data from a post"""
        return {
            'id': post.id,
            'title': post.title,
            'author': str(post.author) if post.author else '[deleted]',
            'created_utc': post.created_utc,
            'score': post.score,
            'num_comments': post.num_comments,
            'upvote_ratio': post.upvote_ratio,
            'subreddit': post.subreddit.display_name,
            'url': post.url,
            'is_self': post.is_self,
            'selftext': post.selftext if post.is_self else '',
            'link_flair_text': post.link_flair_text if hasattr(post, 'link_flair_text') else None
        }

    async def collect_subreddit_analytics(self, subreddit_name: str = "HarmonyKorrine", time_filter: str = "year", limit: int = 500) -> Dict:
        """Collect comprehensive subreddit analytics data
        
        Args:
            subreddit_name (str): Target subreddit name
            time_filter (str): Time filter for posts (day/week/month/year/all)
            limit (int): Maximum number of posts to analyze
            
        Returns:
            Dict: Comprehensive subreddit analytics data
        """
        try:
            analytics_data = {
                'top_posts': [],
                'controversial_posts': [],
                'trending_topics': defaultdict(int),
                'content_types': defaultdict(int),
                'user_engagement': defaultdict(int),
                'time_series_data': [],
                'media_metrics': defaultdict(int)
            }
            
            async with asyncpraw.Reddit(
                client_id=self.client_id,
                client_secret=self.client_secret,
                user_agent=self.user_agent
            ) as reddit:
                subreddit = await reddit.subreddit(subreddit_name)
                
                # Collect posts from different sort methods for comprehensive analysis
                async for post in subreddit.top(time_filter=time_filter, limit=limit):
                    post_data = await self._extract_post_data(post)
                    analytics_data['top_posts'].append(post_data)
                    await self._update_analytics(analytics_data, post_data)
                
                async for post in subreddit.controversial(time_filter=time_filter, limit=limit):
                    post_data = await self._extract_post_data(post)
                    analytics_data['controversial_posts'].append(post_data)
                    await self._update_analytics(analytics_data, post_data)
                
                # Get specific EDGLRD content
                async for post in subreddit.search("EDGLRD", time_filter=time_filter, limit=limit):
                    post_data = await self._extract_post_data(post)
                    if post_data not in analytics_data['top_posts']:
                        await self._update_analytics(analytics_data, post_data)
            
            return analytics_data
            
        except Exception as e:
            self.logger.error(f"Error collecting subreddit analytics: {str(e)}")
            return {}

    async def _update_analytics(self, analytics_data: Dict, post_data: Dict):
        """Update analytics data with post information"""
        try:
            # Extract topics and keywords from title and text
            text = f"{post_data['title']} {post_data['selftext']}"
            words = text.lower().split()
            for word in words:
                if len(word) > 3 and word not in STOP_WORDS:  # You'll need to define STOP_WORDS
                    analytics_data['trending_topics'][word] += 1
            
            # Track content types
            content_type = self._determine_content_type(post_data)
            analytics_data['content_types'][content_type] += 1
            
            # Track user engagement
            analytics_data['user_engagement'][post_data['author']] += 1
            
            # Add time series data point
            analytics_data['time_series_data'].append({
                'timestamp': post_data['created_utc'],
                'score': post_data['score'],
                'num_comments': post_data['num_comments']
            })
            
            # Track media metrics
            if post_data.get('is_video'):
                analytics_data['media_metrics']['videos'] += 1
            elif post_data.get('url').endswith(('.jpg', '.jpeg', '.png', '.gif')):
                analytics_data['media_metrics']['images'] += 1
                
        except Exception as e:
            self.logger.error(f"Error updating analytics: {str(e)}")

    def _determine_content_type(self, post_data: Dict) -> str:
        """Determine the type of content in a post"""
        if post_data.get('is_video'):
            return 'video'
        elif post_data.get('url').endswith(('.jpg', '.jpeg', '.png', '.gif')):
            return 'image'
        elif post_data.get('is_self'):
            return 'text'
        else:
            return 'link'

    async def collect_subreddit_posts(self, subreddit_name: str, limit: int = 100) -> List[Dict]:
        """
        Collect posts from a specific subreddit
        
        Args:
            subreddit_name (str): Name of subreddit to collect from
            limit (int): Maximum number of posts to collect
            
        Returns:
            List[Dict]: List of collected post data
        """
        try:
            posts = []
            async with asyncpraw.Reddit(
                client_id=self.client_id,
                client_secret=self.client_secret,
                user_agent=self.user_agent
            ) as reddit:
                subreddit = await reddit.subreddit(subreddit_name)
                
                # Collect hot posts
                async for post in subreddit.hot(limit=limit):
                    post_data = await self._extract_post_data(post)
                    posts.append(post_data)
                    
            return posts
            
        except Exception as e:
            self.logger.error(f"Error collecting subreddit posts: {str(e)}")
            return []

    async def close(self):
        """Close the Reddit client session"""
        try:
            await self.reddit.close()
        except Exception as e:
            self.logger.error(f"Error closing Reddit client session: {str(e)}")

    def __del__(self):
        """Destructor to ensure client session is closed"""
        try:
            if hasattr(self, 'reddit'):
                self.loop.run_until_complete(self.close())
        except Exception as e:
            self.logger.error(f"Error in destructor: {str(e)}")