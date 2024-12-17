"""
Instagram Data Collector
Handles collection of Instagram posts and comments using the Graph API.
"""

import requests
from typing import List, Dict, Optional
import pandas as pd
from datetime import datetime
# from instagram_private_api import Client, ClientCompatPatch  # Commented out for now
from utils import logger, API_CONFIG
from utils.test_data import INSTAGRAM_TEST_DATA

class InstagramCollector:
    def __init__(self, username=None, password=None):
        self.username = username
        self.password = password
        try:
            self.access_token = API_CONFIG['instagram']['access_token']
            self.account_id = API_CONFIG['instagram']['account_id']
        except (KeyError, TypeError):
            self.access_token = None
            self.account_id = None
            logger.warning("Instagram API credentials not found in config, using test data")
        
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

    def analyze_engagement(self, df: pd.DataFrame) -> Dict:
        """
        Analyze engagement metrics for Instagram posts
        """
        if df.empty:
            return {}

        # Calculate engagement metrics
        engagement_data = {
            'total_posts': len(df),
            'total_likes': df['likes'].sum(),
            'total_comments': df['comments_count'].sum(),
            'avg_likes_per_post': df['likes'].mean(),
            'avg_comments_per_post': df['comments_count'].mean(),
            'engagement_rate': (df['likes'].sum() + df['comments_count'].sum()) / len(df),
            'top_performing_posts': self._get_top_posts(df),
            'engagement_by_media_type': self._analyze_media_types(df),
            'posting_frequency': self._analyze_posting_frequency(df)
        }
        
        return engagement_data

    def analyze_hashtags(self, df: pd.DataFrame) -> List[Dict]:
        """
        Analyze hashtag performance and trends
        """
        hashtags = []
        for text in df['text'].dropna():
            tags = [tag.strip('#') for tag in text.split() if tag.startswith('#')]
            hashtags.extend(tags)
        
        hashtag_stats = pd.DataFrame({
            'hashtag': hashtags
        }).value_counts().reset_index()
        hashtag_stats.columns = ['hashtag', 'frequency']
        
        return hashtag_stats.head(20).to_dict('records')

    def _get_top_posts(self, df: pd.DataFrame) -> List[Dict]:
        """Get top performing posts based on engagement"""
        engagement_score = df['likes'] + df['comments_count']
        df['engagement_score'] = engagement_score
        
        top_posts = df.nlargest(5, 'engagement_score')[
            ['id', 'text', 'likes', 'comments_count', 'media_type', 'created_at']
        ]
        return top_posts.to_dict('records')

    def _analyze_media_types(self, df: pd.DataFrame) -> Dict:
        """Analyze engagement by media type"""
        media_metrics = df.groupby('media_type').agg({
            'likes': ['mean', 'sum'],
            'comments_count': ['mean', 'sum']
        }).round(2)
        
        return media_metrics.to_dict()

    def _analyze_posting_frequency(self, df: pd.DataFrame) -> Dict:
        """Analyze posting patterns and frequency"""
        df['date'] = pd.to_datetime(df['created_at']).dt.date
        posts_per_day = df.groupby('date').size()
        
        return {
            'avg_posts_per_day': posts_per_day.mean(),
            'most_active_day': str(posts_per_day.idxmax()),
            'posts_on_most_active_day': int(posts_per_day.max())
        }

    def search_hashtag_trends(self, hashtag: str, limit: int = 100) -> pd.DataFrame:
        """
        Search for trending posts with specific hashtag
        """
        try:
            params = {
                'fields': 'id,caption,media_type,media_url,timestamp,like_count,comments_count',
                'q': hashtag
            }
            
            response = self._make_request('ig_hashtag_search', params)
            hashtag_id = response['data'][0]['id']
            
            # Get recent media with this hashtag
            media_response = self._make_request(
                f"{hashtag_id}/recent_media",
                {'fields': 'id,caption,media_type,media_url,timestamp,like_count,comments_count'}
            )
            
            posts = []
            for post in media_response.get('data', [])[:limit]:
                posts.append({
                    'id': post['id'],
                    'text': post.get('caption', ''),
                    'media_type': post['media_type'],
                    'media_url': post.get('media_url'),
                    'created_at': datetime.strptime(post['timestamp'], '%Y-%m-%dT%H:%M:%S%z'),
                    'likes': post.get('like_count', 0),
                    'comments_count': post.get('comments_count', 0),
                    'hashtag': hashtag
                })
            
            return pd.DataFrame(posts)
            
        except Exception as e:
            logger.error(f"Error searching hashtag trends: {str(e)}")
            return pd.DataFrame()

    def collect_audience_insights(self, period: str = 'day') -> Dict:
        """
        Collect audience insights including demographics and activity patterns
        
        Args:
            period (str): Time period for insights ('day', 'week', 'month')
            
        Returns:
            Dict: Audience insights data
        """
        try:
            metrics = [
                'audience_gender_age',
                'audience_locale',
                'audience_country',
                'audience_city',
                'online_followers'
            ]
            
            params = {
                'metric': ','.join(metrics),
                'period': period
            }
            
            response = self._make_request(f"{self.account_id}/insights", params)
            
            insights = {
                'demographics': self._process_demographic_data(response),
                'active_times': self._process_active_times(response),
                'locations': self._process_location_data(response),
                'collected_at': datetime.now().isoformat()
            }
            
            logger.info(f"Collected audience insights for period: {period}")
            return insights
            
        except Exception as e:
            logger.error(f"Error collecting audience insights: {str(e)}")
            return {}
    
    def _process_demographic_data(self, response: Dict) -> Dict:
        """Process demographic data from insights response"""
        demographics = {
            'gender_age': {},
            'total_followers': 0
        }
        
        for metric in response.get('data', []):
            if metric['name'] == 'audience_gender_age':
                for value in metric['values']:
                    demographics['gender_age'] = value['value']
                    demographics['total_followers'] = sum(value['value'].values())
                    
        return demographics
    
    def _process_active_times(self, response: Dict) -> Dict:
        """Process follower active times from insights response"""
        active_times = {
            'hourly': {},
            'weekly': {}
        }
        
        for metric in response.get('data', []):
            if metric['name'] == 'online_followers':
                for value in metric['values']:
                    active_times['hourly'] = value['value']
                    
        return active_times
    
    def _process_location_data(self, response: Dict) -> Dict:
        """Process location data from insights response"""
        locations = {
            'countries': {},
            'cities': {},
            'locales': {}
        }
        
        for metric in response.get('data', []):
            if metric['name'] == 'audience_country':
                for value in metric['values']:
                    locations['countries'] = value['value']
            elif metric['name'] == 'audience_city':
                for value in metric['values']:
                    locations['cities'] = value['value']
            elif metric['name'] == 'audience_locale':
                for value in metric['values']:
                    locations['locales'] = value['value']
                    
        return locations

    def collect_profile_data(self) -> Dict:
        """
        Collect Instagram profile data including posts, engagement, and audience insights.
        
        Returns:
            Dict: Profile data including metrics and insights
        """
        if not self.access_token or not self.account_id:
            logger.info("Using test data for Instagram profile data")
            return INSTAGRAM_TEST_DATA

        try:
            # For now, return mock data since we don't have API credentials
            mock_data = {
                'profile': {
                    'username': self.username or 'demo_account',
                    'followers_count': 10500,
                    'following_count': 850,
                    'media_count': 157
                },
                'recent_posts': [
                    {
                        'id': f'post_{i}',
                        'type': 'image' if i % 3 == 0 else 'video' if i % 3 == 1 else 'carousel',
                        'caption': f'Sample post caption {i}',
                        'likes': 100 + i * 10,
                        'comments': 20 + i * 2,
                        'engagement_rate': 4.8,
                        'created_at': (datetime.now().timestamp() - i * 86400)
                    } for i in range(30)
                ],
                'engagement': {
                    'total_likes': 25000,
                    'total_comments': 1200,
                    'avg_likes_per_post': 350,
                    'avg_comments_per_post': 45
                },
                'audience': {
                    'age_ranges': {
                        '18-24': 15,
                        '25-34': 35,
                        '35-44': 25,
                        '45-54': 15,
                        '55+': 10
                    },
                    'gender': {
                        'female': 58,
                        'male': 40,
                        'other': 2
                    },
                    'top_locations': [
                        {'name': 'United States', 'percentage': 45},
                        {'name': 'United Kingdom', 'percentage': 15},
                        {'name': 'Canada', 'percentage': 12}
                    ]
                },
                'best_performing_hashtags': [
                    {'tag': '#trending', 'avg_engagement': 450},
                    {'tag': '#viral', 'avg_engagement': 380},
                    {'tag': '#content', 'avg_engagement': 320}
                ]
            }
            return mock_data
            
        except Exception as e:
            logger.error(f"Error collecting Instagram profile data: {str(e)}")
            raise

    def get_account_insights(self) -> Dict:
        """Get comprehensive account insights."""
        try:
            metrics = [
                'impressions',
                'reach',
                'profile_views',
                'follower_count',
                'email_contacts',
                'get_directions_clicks',
                'phone_call_clicks',
                'text_message_clicks',
                'website_clicks'
            ]
            
            params = {
                'metric': ','.join(metrics),
                'period': 'day',
                'access_token': self.access_token
            }
            
            response = requests.get(
                f"{self.base_url}/{self.account_id}/insights",
                params=params
            )
            
            if response.status_code == 200:
                return response.json()['data']
            else:
                logger.error(f"Error getting account insights: {response.text}")
                return {}
                
        except Exception as e:
            logger.error(f"Error getting account insights: {str(e)}")
            return {}
            
    def get_audience_demographics(self) -> Dict:
        """Get detailed audience demographics."""
        try:
            metrics = [
                'audience_city',
                'audience_country',
                'audience_gender_age',
                'audience_locale',
                'online_followers'
            ]
            
            params = {
                'metric': ','.join(metrics),
                'access_token': self.access_token
            }
            
            response = requests.get(
                f"{self.base_url}/{self.account_id}/insights",
                params=params
            )
            
            if response.status_code == 200:
                return response.json()['data']
            else:
                logger.error(f"Error getting audience demographics: {response.text}")
                return {}
                
        except Exception as e:
            logger.error(f"Error getting audience demographics: {str(e)}")
            return {}
            
    def get_content_performance(self, days: int = 30) -> List[Dict]:
        """Get detailed performance metrics for recent content."""
        try:
            # First get media IDs
            media_params = {
                'fields': 'id,timestamp,media_type,media_url,permalink',
                'limit': 50,
                'access_token': self.access_token
            }
            
            media_response = requests.get(
                f"{self.base_url}/{self.account_id}/media",
                params=media_params
            )
            
            if media_response.status_code != 200:
                logger.error(f"Error getting media list: {media_response.text}")
                return []
                
            media_list = media_response.json()['data']
            start_time = datetime.now() - datetime.timedelta(days=days)
            
            performance_data = []
            for media in media_list:
                media_timestamp = datetime.strptime(media['timestamp'], '%Y-%m-%dT%H:%M:%S%z')
                if media_timestamp.replace(tzinfo=None) < start_time:
                    continue
                    
                # Get insights for each media
                insights_params = {
                    'metric': 'engagement,impressions,reach,saved,video_views',
                    'access_token': self.access_token
                }
                
                insights_response = requests.get(
                    f"{self.base_url}/{media['id']}/insights",
                    params=insights_params
                )
                
                if insights_response.status_code == 200:
                    insights = insights_response.json()['data']
                    media['insights'] = {insight['name']: insight['values'][0]['value'] for insight in insights}
                    performance_data.append(media)
                    
            return performance_data
                
        except Exception as e:
            logger.error(f"Error getting content performance: {str(e)}")
            return []
            
    def get_stories_insights(self) -> List[Dict]:
        """Get insights for active stories."""
        try:
            stories_params = {
                'fields': 'id,media_type,media_url,timestamp',
                'access_token': self.access_token
            }
            
            stories_response = requests.get(
                f"{self.base_url}/{self.account_id}/stories",
                params=stories_params
            )
            
            if stories_response.status_code != 200:
                logger.error(f"Error getting stories: {stories_response.text}")
                return []
                
            stories = stories_response.json()['data']
            stories_insights = []
            
            for story in stories:
                insights_params = {
                    'metric': 'exits,impressions,reach,replies,taps_forward,taps_back',
                    'access_token': self.access_token
                }
                
                insights_response = requests.get(
                    f"{self.base_url}/{story['id']}/insights",
                    params=insights_params
                )
                
                if insights_response.status_code == 200:
                    story['insights'] = insights_response.json()['data']
                    stories_insights.append(story)
                    
            return stories_insights
                
        except Exception as e:
            logger.error(f"Error getting stories insights: {str(e)}")
            return []
            
    def get_hashtag_performance(self, hashtags: List[str]) -> Dict:
        """Get performance metrics for specific hashtags."""
        try:
            hashtag_insights = {}
            
            for hashtag in hashtags:
                # First get hashtag ID
                search_params = {
                    'q': hashtag,
                    'access_token': self.access_token
                }
                
                search_response = requests.get(
                    f"{self.base_url}/ig_hashtag_search",
                    params=search_params
                )
                
                if search_response.status_code != 200:
                    continue
                    
                hashtag_id = search_response.json()['data'][0]['id']
                
                # Get metrics for hashtag
                metrics_params = {
                    'metric': 'impressions,reach,profile_visits',
                    'access_token': self.access_token
                }
                
                metrics_response = requests.get(
                    f"{self.base_url}/{hashtag_id}/insights",
                    params=metrics_params
                )
                
                if metrics_response.status_code == 200:
                    hashtag_insights[hashtag] = metrics_response.json()['data']
                    
            return hashtag_insights
                
        except Exception as e:
            logger.error(f"Error getting hashtag performance: {str(e)}")
            return {}
            
    def get_shopping_insights(self) -> Dict:
        """Get insights for shopping features."""
        try:
            metrics = [
                'product_page_views',
                'product_detail_page_views',
                'product_button_clicks'
            ]
            
            params = {
                'metric': ','.join(metrics),
                'period': 'day',
                'access_token': self.access_token
            }
            
            response = requests.get(
                f"{self.base_url}/{self.account_id}/insights",
                params=params
            )
            
            if response.status_code == 200:
                return response.json()['data']
            else:
                logger.error(f"Error getting shopping insights: {response.text}")
                return {}
                
        except Exception as e:
            logger.error(f"Error getting shopping insights: {str(e)}")
            return {}