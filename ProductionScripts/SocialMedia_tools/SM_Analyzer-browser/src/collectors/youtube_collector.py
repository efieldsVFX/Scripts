"""
YouTube Data Collector
Handles collection of YouTube videos, shorts, and comments using YouTube Data API.
"""

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from typing import List, Dict, Optional
import pandas as pd
from datetime import datetime
from utils import logger
from textblob import TextBlob
from utils.test_data import YOUTUBE_TEST_DATA

class YouTubeCollector:
    def __init__(self, config: Dict):
        """Initialize YouTube API client"""
        self.api_key = config.get('api_key', '')
        if not self.api_key:
            logger.warning("No YouTube API key provided, using test data")
            self.youtube = None
            self.using_test_data = True
            return
        
        try:
            self.youtube = build('youtube', 'v3', credentials=None, developerKey=self.api_key)
            self.using_test_data = False
            logger.info("YouTube collector initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize YouTube collector: {str(e)}")
            self.youtube = None
            self.using_test_data = True

    def collect_videos(self, query: str, video_type: str = 'video', max_results: int = 50) -> pd.DataFrame:
        """
        Collect YouTube videos based on search query
        """
        if not self.youtube and not self.using_test_data:
            logger.error("YouTube client not initialized. Cannot collect videos.")
            return pd.DataFrame()

        if self.using_test_data:
            logger.info("Using test data for video collection")
            return pd.DataFrame(YOUTUBE_TEST_DATA['videos'])

        try:
            videos = []
            search_response = self.youtube.search().list(
                q=query,
                part='id,snippet',
                maxResults=min(max_results, 50),
                type='video',
                videoDuration='short' if video_type == 'short' else 'any'
            ).execute()

            video_ids = [item['id']['videoId'] for item in search_response.get('items', [])]
            
            # Get detailed video statistics
            videos_response = self.youtube.videos().list(
                part='statistics,contentDetails,snippet',
                id=','.join(video_ids)
            ).execute()

            for video in videos_response.get('items', []):
                stats = video['statistics']
                videos.append({
                    'id': video['id'],
                    'title': video['snippet']['title'],
                    'description': video['snippet']['description'],
                    'published_at': video['snippet']['publishedAt'],
                    'channel_id': video['snippet']['channelId'],
                    'channel_title': video['snippet']['channelTitle'],
                    'views': int(stats.get('viewCount', 0)),
                    'likes': int(stats.get('likeCount', 0)),
                    'comments': int(stats.get('commentCount', 0)),
                    'tags': video['snippet'].get('tags', []),
                    'duration': video['contentDetails']['duration'],
                    'type': video_type
                })

            return pd.DataFrame(videos)

        except Exception as e:
            logger.error(f"Error collecting YouTube videos: {str(e)}")
            return pd.DataFrame()

    def collect_comments(self, video_id: str, max_results: int = 100) -> pd.DataFrame:
        """Collect comments for a specific video"""
        if not self.youtube and not self.using_test_data:
            logger.error("YouTube client not initialized. Cannot collect comments.")
            return pd.DataFrame()

        if self.using_test_data:
            logger.info("Using test data for comment collection")
            return pd.DataFrame(YOUTUBE_TEST_DATA['comments'])

        try:
            comments = []
            request = self.youtube.commentThreads().list(
                part='snippet',
                videoId=video_id,
                maxResults=min(max_results, 100),
                textFormat='plainText'
            )

            while request and len(comments) < max_results:
                response = request.execute()
                
                for item in response['items']:
                    comment = item['snippet']['topLevelComment']['snippet']
                    comments.append({
                        'id': item['id'],
                        'text': comment['textDisplay'],
                        'author': comment['authorDisplayName'],
                        'likes': comment['likeCount'],
                        'published_at': comment['publishedAt'],
                        'video_id': video_id
                    })

                request = self.youtube.commentThreads().list_next(request, response)

            return pd.DataFrame(comments)

        except Exception as e:
            logger.error(f"Error collecting YouTube comments: {str(e)}")
            return pd.DataFrame()

    def analyze_video_performance(self, videos_df: pd.DataFrame) -> Dict:
        """Analyze video performance metrics"""
        if videos_df.empty:
            return {}

        # Calculate engagement metrics
        videos_df['engagement_score'] = (
            videos_df['likes'] * 2 + 
            videos_df['comments'] * 3
        ) / videos_df['views']

        performance_metrics = {
            'total_videos': len(videos_df),
            'total_views': videos_df['views'].sum(),
            'avg_engagement_rate': videos_df['engagement_score'].mean(),
            'top_performing_videos': self._get_top_videos(videos_df),
            'tag_analysis': self._analyze_tags(videos_df),
            'content_analysis': self._analyze_content_types(videos_df)
        }

        return performance_metrics

    def _get_top_videos(self, df: pd.DataFrame) -> List[Dict]:
        """Get top performing videos"""
        return df.nlargest(5, 'engagement_score')[
            ['title', 'views', 'likes', 'comments', 'engagement_score']
        ].to_dict('records')

    def _analyze_tags(self, df: pd.DataFrame) -> Dict:
        """Analyze tag performance"""
        all_tags = []
        for tags in df['tags']:
            if isinstance(tags, list):
                all_tags.extend(tags)

        tag_stats = pd.Series(all_tags).value_counts().head(20)
        return tag_stats.to_dict()

    def _analyze_content_types(self, df: pd.DataFrame) -> Dict:
        """Analyze performance by content type"""
        content_patterns = {
            'tutorial': r'how\s+to|tutorial|guide|tips',
            'entertainment': r'funny|amazing|awesome|cool',
            'news': r'news|update|latest|breaking',
            'review': r'review|unboxing|comparison'
        }

        content_metrics = {}
        for content_type, pattern in content_patterns.items():
            content_videos = df[
                df['title'].str.contains(pattern, case=False, na=False) |
                df['description'].str.contains(pattern, case=False, na=False)
            ]
            if not content_videos.empty:
                content_metrics[content_type] = {
                    'count': len(content_videos),
                    'avg_views': content_videos['views'].mean(),
                    'avg_engagement': content_videos['engagement_score'].mean()
                }

        return content_metrics

    def collect_audience_insights(self, channel_id: str) -> Dict:
        """
        Collect comprehensive audience insights for a YouTube channel
        
        Args:
            channel_id: YouTube channel ID to analyze
            
        Returns:
            Dict containing audience insights data
        """
        if not self.youtube and not self.using_test_data:
            logger.error("YouTube client not initialized. Cannot collect insights.")
            return {}

        if self.using_test_data:
            logger.info("Using test data for audience insights")
            return YOUTUBE_TEST_DATA['audience_insights']

        try:
            insights = {
                'demographics': self._collect_demographic_data(channel_id),
                'engagement_data': self._collect_engagement_data(channel_id),
                'content_data': self._collect_content_data(channel_id),
                'retention_data': self._collect_retention_data(channel_id),
                'traffic_data': self._collect_traffic_data(channel_id),
                'collected_at': datetime.now().isoformat()
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Error collecting YouTube audience insights: {str(e)}")
            return {}
            
    def _collect_demographic_data(self, channel_id: str) -> Dict:
        """Collect demographic information about channel audience"""
        if self.using_test_data:
            logger.info("Using test data for demographic data")
            return YOUTUBE_TEST_DATA['demographics']

        try:
            # Get channel statistics
            channel_response = self.youtube.channels().list(
                part='statistics,snippet',
                id=channel_id
            ).execute()
            
            if not channel_response.get('items'):
                return {}
                
            channel_stats = channel_response['items'][0]['statistics']
            
            # Get viewer demographics through Analytics API
            demographics = {
                'age_gender': self._get_age_gender_metrics(channel_id),
                'geography': self._get_geographic_metrics(channel_id),
                'devices': self._get_device_metrics(channel_id),
                'subscribers': {
                    'total_subscribers': int(channel_stats.get('subscriberCount', 0)),
                    'hidden_subscriber_count': channel_stats.get('hiddenSubscriberCount', False),
                    'subscriber_gained': 0,  # Requires Analytics API
                    'subscriber_lost': 0     # Requires Analytics API
                }
            }
            
            return demographics
            
        except Exception as e:
            logger.error(f"Error collecting demographic data: {str(e)}")
            return {}
            
    def _collect_engagement_data(self, channel_id: str) -> Dict:
        """Collect engagement metrics for the channel"""
        if self.using_test_data:
            logger.info("Using test data for engagement data")
            return YOUTUBE_TEST_DATA['engagement_data']

        try:
            # Get channel's recent videos
            videos_response = self.youtube.search().list(
                part='id',
                channelId=channel_id,
                maxResults=50,
                order='date',
                type='video'
            ).execute()
            
            video_ids = [item['id']['videoId'] for item in videos_response.get('items', [])]
            
            if not video_ids:
                return {}
                
            # Get detailed video statistics
            videos_stats = self.youtube.videos().list(
                part='statistics,contentDetails',
                id=','.join(video_ids)
            ).execute()
            
            # Calculate engagement metrics
            total_views = 0
            total_likes = 0
            total_comments = 0
            
            for video in videos_stats.get('items', []):
                stats = video['statistics']
                total_views += int(stats.get('viewCount', 0))
                total_likes += int(stats.get('likeCount', 0))
                total_comments += int(stats.get('commentCount', 0))
                
            engagement_data = {
                'overall_engagement': {
                    'views': total_views,
                    'likes': total_likes,
                    'comments': total_comments,
                    'avg_views_per_video': total_views / len(video_ids) if video_ids else 0
                },
                'trends': self._calculate_engagement_trends(videos_stats.get('items', [])),
                'interactions': {
                    'likes': total_likes,
                    'comments': total_comments
                }
            }
            
            return engagement_data
            
        except Exception as e:
            logger.error(f"Error collecting engagement data: {str(e)}")
            return {}
            
    def _collect_content_data(self, channel_id: str) -> Dict:
        """Collect content performance data"""
        if self.using_test_data:
            logger.info("Using test data for content data")
            return YOUTUBE_TEST_DATA['content_data']

        try:
            # Get channel's videos
            videos_response = self.youtube.search().list(
                part='id,snippet',
                channelId=channel_id,
                maxResults=50,
                order='viewCount',
                type='video'
            ).execute()
            
            video_ids = [item['id']['videoId'] for item in videos_response.get('items', [])]
            
            if not video_ids:
                return {}
                
            # Get detailed video statistics
            videos_stats = self.youtube.videos().list(
                part='statistics,contentDetails,snippet',
                id=','.join(video_ids)
            ).execute()
            
            content_data = {
                'top_content': self._analyze_top_content(videos_stats.get('items', [])),
                'types': self._analyze_content_types(videos_stats.get('items', [])),
                'by_length': self._analyze_content_by_length(videos_stats.get('items', [])),
                'topics': self._extract_content_topics(videos_stats.get('items', []))
            }
            
            return content_data
            
        except Exception as e:
            logger.error(f"Error collecting content data: {str(e)}")
            return {}
            
    def _collect_retention_data(self, channel_id: str) -> Dict:
        """Collect audience retention metrics"""
        if self.using_test_data:
            logger.info("Using test data for retention data")
            return YOUTUBE_TEST_DATA['retention_data']

        # Note: Detailed retention data requires YouTube Analytics API
        try:
            # Get channel's recent videos
            videos_response = self.youtube.search().list(
                part='id',
                channelId=channel_id,
                maxResults=50,
                order='date',
                type='video'
            ).execute()
            
            video_ids = [item['id']['videoId'] for item in videos_response.get('items', [])]
            
            if not video_ids:
                return {}
                
            # Get video statistics and duration
            videos_stats = self.youtube.videos().list(
                part='statistics,contentDetails',
                id=','.join(video_ids)
            ).execute()
            
            retention_data = {
                'avg_view_duration': self._calculate_avg_view_duration(videos_stats.get('items', [])),
                'retention_by_type': self._analyze_retention_by_type(videos_stats.get('items', []))
            }
            
            return retention_data
            
        except Exception as e:
            logger.error(f"Error collecting retention data: {str(e)}")
            return {}
            
    def _collect_traffic_data(self, channel_id: str) -> Dict:
        """Collect traffic source data"""
        if self.using_test_data:
            logger.info("Using test data for traffic data")
            return {
                'total_views': int(YOUTUBE_TEST_DATA['channel_stats']['viewCount']),
                'sources': {
                    'direct': 25,
                    'external': 30,
                    'suggested_videos': 35,
                    'youtube_search': 10
                }
            }

        try:
            # Get channel statistics
            channel_response = self.youtube.channels().list(
                part='statistics',
                id=channel_id
            ).execute()
            
            if not channel_response.get('items'):
                return {}
                
            channel_stats = channel_response['items'][0]['statistics']
            
            traffic_data = {
                'total_views': int(channel_stats.get('viewCount', 0)),
                'sources': {
                    'direct': 0,  # Requires Analytics API
                    'external': 0,
                    'suggested_videos': 0,
                    'youtube_search': 0
                }
            }
            
            return traffic_data
            
        except Exception as e:
            logger.error(f"Error collecting traffic data: {str(e)}")
            return {}
            
    def _calculate_engagement_trends(self, videos: List[Dict]) -> Dict:
        """Calculate engagement trends from video data"""
        trends = {
            'daily': {},
            'weekly': {},
            'monthly': {}
        }
        
        for video in videos:
            published_at = datetime.strptime(
                video['snippet']['publishedAt'],
                '%Y-%m-%dT%H:%M:%SZ'
            )
            stats = video['statistics']
            
            day_key = published_at.strftime('%Y-%m-%d')
            week_key = published_at.strftime('%Y-%W')
            month_key = published_at.strftime('%Y-%m')
            
            # Daily trends
            if day_key not in trends['daily']:
                trends['daily'][day_key] = {'views': 0, 'likes': 0, 'comments': 0}
            trends['daily'][day_key]['views'] += int(stats.get('viewCount', 0))
            trends['daily'][day_key]['likes'] += int(stats.get('likeCount', 0))
            trends['daily'][day_key]['comments'] += int(stats.get('commentCount', 0))
            
            # Weekly trends
            if week_key not in trends['weekly']:
                trends['weekly'][week_key] = {'views': 0, 'likes': 0, 'comments': 0}
            trends['weekly'][week_key]['views'] += int(stats.get('viewCount', 0))
            trends['weekly'][week_key]['likes'] += int(stats.get('likeCount', 0))
            trends['weekly'][week_key]['comments'] += int(stats.get('commentCount', 0))
            
            # Monthly trends
            if month_key not in trends['monthly']:
                trends['monthly'][month_key] = {'views': 0, 'likes': 0, 'comments': 0}
            trends['monthly'][month_key]['views'] += int(stats.get('viewCount', 0))
            trends['monthly'][month_key]['likes'] += int(stats.get('likeCount', 0))
            trends['monthly'][month_key]['comments'] += int(stats.get('commentCount', 0))
            
        return trends
        
    def _analyze_top_content(self, videos: List[Dict]) -> List[Dict]:
        """Analyze top performing content"""
        video_metrics = []
        
        for video in videos:
            stats = video['statistics']
            engagement_score = (
                int(stats.get('likeCount', 0)) * 2 +
                int(stats.get('commentCount', 0)) * 3
            ) / int(stats.get('viewCount', 1))
            
            video_metrics.append({
                'id': video['id'],
                'title': video['snippet']['title'],
                'views': int(stats.get('viewCount', 0)),
                'likes': int(stats.get('likeCount', 0)),
                'comments': int(stats.get('commentCount', 0)),
                'engagement_score': engagement_score,
                'duration': video['contentDetails']['duration'],
                'published_at': video['snippet']['publishedAt']
            })
            
        return sorted(video_metrics, key=lambda x: x['engagement_score'], reverse=True)[:10]
        
    def _analyze_content_by_length(self, videos: List[Dict]) -> Dict:
        """Analyze content performance by video length"""
        length_categories = {
            'short': {'count': 0, 'views': 0, 'engagement': 0},  # < 5 mins
            'medium': {'count': 0, 'views': 0, 'engagement': 0}, # 5-15 mins
            'long': {'count': 0, 'views': 0, 'engagement': 0}    # > 15 mins
        }
        
        for video in videos:
            duration = self._parse_duration(video['contentDetails']['duration'])
            stats = video['statistics']
            
            category = 'short' if duration < 300 else 'medium' if duration < 900 else 'long'
            
            length_categories[category]['count'] += 1
            length_categories[category]['views'] += int(stats.get('viewCount', 0))
            length_categories[category]['engagement'] += (
                int(stats.get('likeCount', 0)) +
                int(stats.get('commentCount', 0))
            )
            
        # Calculate averages
        for category in length_categories.values():
            if category['count'] > 0:
                category['avg_views'] = category['views'] / category['count']
                category['avg_engagement'] = category['engagement'] / category['count']
                
        return length_categories
        
    def _parse_duration(self, duration: str) -> int:
        """Convert YouTube duration format to seconds"""
        import re
        import isodate
        return int(isodate.parse_duration(duration).total_seconds())
        
    def _extract_content_topics(self, videos: List[Dict]) -> Dict:
        """Extract and analyze content topics"""
        topics = {}
        
        for video in videos:
            # Extract topics from title and tags
            title_words = set(video['snippet']['title'].lower().split())
            tags = set(video['snippet'].get('tags', []))
            
            all_topics = title_words.union(tags)
            stats = video['statistics']
            
            for topic in all_topics:
                if topic not in topics:
                    topics[topic] = {
                        'count': 0,
                        'views': 0,
                        'engagement': 0
                    }
                    
                topics[topic]['count'] += 1
                topics[topic]['views'] += int(stats.get('viewCount', 0))
                topics[topic]['engagement'] += (
                    int(stats.get('likeCount', 0)) +
                    int(stats.get('commentCount', 0))
                )
                
        # Calculate averages and sort by engagement
        for topic in topics.values():
            topic['avg_views'] = topic['views'] / topic['count']
            topic['avg_engagement'] = topic['engagement'] / topic['count']
            
        return dict(sorted(
            topics.items(),
            key=lambda x: x[1]['avg_engagement'],
            reverse=True
        )[:20])