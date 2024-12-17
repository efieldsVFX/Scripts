"""
YouTube API Client
Handles interactions with YouTube Data API v3
"""

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from typing import Dict, List, Optional
from ..config.api_config import APIConfig

class YouTubeClient:
    def __init__(self):
        config = APIConfig.get_youtube_config()
        if not APIConfig.validate_credentials(config):
            raise ValueError("Invalid YouTube API credentials")
            
        self.api_key = config['api_key']
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)
        
    def get_video_stats(self, video_ids: List[str]) -> List[Dict]:
        """Get statistics for specific videos"""
        try:
            request = self.youtube.videos().list(
                part="statistics,snippet",
                id=','.join(video_ids)
            )
            response = request.execute()
            
            return [{
                'id': item['id'],
                'title': item['snippet']['title'],
                'published_at': item['snippet']['publishedAt'],
                'stats': item['statistics']
            } for item in response.get('items', [])]
            
        except Exception as e:
            print(f"Error fetching video stats: {str(e)}")
            return []
            
    def get_channel_stats(self, channel_id: str) -> Dict:
        """Get channel-level statistics"""
        try:
            request = self.youtube.channels().list(
                part="statistics,snippet",
                id=channel_id
            )
            response = request.execute()
            
            if response.get('items'):
                channel = response['items'][0]
                return {
                    'title': channel['snippet']['title'],
                    'stats': channel['statistics']
                }
            return {}
            
        except Exception as e:
            print(f"Error fetching channel stats: {str(e)}")
            return {}
            
    def get_videos_list(self, channel_id: str, max_results: int = 50) -> List[Dict]:
        """Get list of videos from a channel"""
        try:
            request = self.youtube.search().list(
                part="id,snippet",
                channelId=channel_id,
                order="date",
                type="video",
                maxResults=max_results
            )
            response = request.execute()
            
            video_ids = [item['id']['videoId'] for item in response.get('items', [])]
            return self.get_video_stats(video_ids) if video_ids else []
            
        except Exception as e:
            print(f"Error fetching videos list: {str(e)}")
            return []

    def get_behavioral_patterns(self, channel_id: str) -> Dict:
        """Get viewer behavioral patterns using YouTube Analytics API"""
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
            
            # Analyze behavioral patterns
            patterns = {
                'view_patterns': self._analyze_view_patterns(videos_stats.get('items', [])),
                'engagement_patterns': self._analyze_engagement_patterns(videos_stats.get('items', [])),
                'retention_patterns': self._analyze_retention_patterns(videos_stats.get('items', []))
            }
            
            return patterns
            
        except Exception as e:
            print(f"Error fetching behavioral patterns: {str(e)}")
            return {}
            
    def get_recurring_views(self, video_ids: List[str]) -> Dict:
        """Get recurring views data using YouTube Data API"""
        try:
            # Get video statistics
            videos_stats = self.youtube.videos().list(
                part='statistics,snippet',
                id=','.join(video_ids)
            ).execute()
            
            recurring_data = {
                'total_views': 0,
                'recurring_views': 0,
                'recurring_percentage': 0,
                'videos': []
            }
            
            for video in videos_stats.get('items', []):
                stats = video['statistics']
                views = int(stats.get('viewCount', 0))
                # Estimate recurring views based on likes and comments
                engagement = int(stats.get('likeCount', 0)) + int(stats.get('commentCount', 0))
                estimated_recurring = min(views, engagement * 2)  # Conservative estimate
                
                recurring_data['videos'].append({
                    'id': video['id'],
                    'title': video['snippet']['title'],
                    'views': views,
                    'estimated_recurring': estimated_recurring,
                    'recurring_percentage': (estimated_recurring / views * 100) if views > 0 else 0
                })
                
                recurring_data['total_views'] += views
                recurring_data['recurring_views'] += estimated_recurring
            
            if recurring_data['total_views'] > 0:
                recurring_data['recurring_percentage'] = (
                    recurring_data['recurring_views'] / recurring_data['total_views'] * 100
                )
            
            return recurring_data
            
        except Exception as e:
            print(f"Error fetching recurring views: {str(e)}")
            return {}
            
    def get_engagement_loyalty(self, channel_id: str) -> Dict:
        """Get engagement loyalty metrics using YouTube Analytics API"""
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
                part='statistics,snippet',
                id=','.join(video_ids)
            ).execute()
            
            loyalty_data = {
                'overall_loyalty': 0,
                'engagement_consistency': 0,
                'videos': []
            }
            
            total_videos = len(videos_stats.get('items', []))
            total_engagement = 0
            engagement_variations = []
            
            for video in videos_stats.get('items', []):
                stats = video['statistics']
                views = int(stats.get('viewCount', 0))
                likes = int(stats.get('likeCount', 0))
                comments = int(stats.get('commentCount', 0))
                
                engagement_rate = ((likes + comments) / views * 100) if views > 0 else 0
                total_engagement += engagement_rate
                engagement_variations.append(engagement_rate)
                
                loyalty_data['videos'].append({
                    'id': video['id'],
                    'title': video['snippet']['title'],
                    'views': views,
                    'engagement_rate': engagement_rate
                })
            
            if total_videos > 0:
                loyalty_data['overall_loyalty'] = total_engagement / total_videos
                # Calculate consistency using coefficient of variation
                mean_engagement = total_engagement / total_videos
                std_dev = (sum((x - mean_engagement) ** 2 for x in engagement_variations) / total_videos) ** 0.5
                loyalty_data['engagement_consistency'] = (1 - (std_dev / mean_engagement)) * 100 if mean_engagement > 0 else 0
            
            return loyalty_data
            
        except Exception as e:
            print(f"Error fetching engagement loyalty: {str(e)}")
            return {}
            
    def get_video_retention_metrics(self, video_id: str) -> Dict:
        """Get video retention rate metrics"""
        try:
            request = self.youtube.videos().list(
                part="contentDetails,statistics",
                id=video_id
            )
            video_response = request.execute()
            
            analytics_request = self.youtube.videos().getVideoAnalytics(
                id=video_id,
                metrics=['averageViewDuration', 'averageViewPercentage', 'relativeRetentionPerformance']
            )
            analytics_response = analytics_request.execute()
            
            return {
                'duration': video_response['items'][0]['contentDetails']['duration'],
                'retention_metrics': analytics_response.get('rows', [])
            }
        except Exception as e:
            print(f"Error fetching retention metrics: {str(e)}")
            return {}
            
    def get_thumbnail_performance(self, video_id: str) -> Dict:
        """Get thumbnail click-through rate metrics"""
        try:
            request = self.youtube.videos().list(
                part="statistics",
                id=video_id,
                metrics=['thumbnailImpressionRate', 'thumbnailClickRate']
            )
            response = request.execute()
            
            if response.get('items'):
                return {
                    'impressions': response['items'][0]['statistics'].get('thumbnailImpressionCount', 0),
                    'clicks': response['items'][0]['statistics'].get('thumbnailClickCount', 0),
                    'ctr': response['items'][0]['statistics'].get('thumbnailClickRate', 0)
                }
            return {}
            
        except Exception as e:
            print(f"Error fetching thumbnail metrics: {str(e)}")
            return {}
            
    def get_revenue_metrics(self, start_date: str, end_date: str) -> Dict:
        """Get ad revenue metrics from YouTube Partner API"""
        try:
            request = self.youtube.channels().list(
                part="contentDetails",
                mine=True
            )
            channel_response = request.execute()
            
            if not channel_response.get('items'):
                return {}
                
            channel_id = channel_response['items'][0]['id']
            
            analytics_request = self.youtube.channels().getChannelAnalytics(
                id=channel_id,
                startDate=start_date,
                endDate=end_date,
                metrics=[
                    'estimatedRevenue',
                    'estimatedAdRevenue',
                    'grossRevenue',
                    'estimatedRedPartnerRevenue',
                    'monetizedPlaybacks'
                ]
            )
            analytics_response = analytics_request.execute()
            
            return {
                'channel_id': channel_id,
                'revenue_data': analytics_response.get('rows', [])
            }
        except Exception as e:
            print(f"Error fetching revenue metrics: {str(e)}")
            return {}
            
    def _analyze_view_patterns(self, videos: List[Dict]) -> Dict:
        """Analyze viewing patterns from video data"""
        patterns = {
            'peak_hours': {},
            'weekday_distribution': {},
            'video_length_preference': {'short': 0, 'medium': 0, 'long': 0}
        }
        
        for video in videos:
            stats = video['statistics']
            duration = self._parse_duration(video['contentDetails']['duration'])
            views = int(stats.get('viewCount', 0))
            
            # Categorize by video length
            if duration < 300:  # < 5 mins
                patterns['video_length_preference']['short'] += views
            elif duration < 900:  # 5-15 mins
                patterns['video_length_preference']['medium'] += views
            else:  # > 15 mins
                patterns['video_length_preference']['long'] += views
        
        return patterns
        
    def _analyze_engagement_patterns(self, videos: List[Dict]) -> Dict:
        """Analyze engagement patterns from video data"""
        patterns = {
            'engagement_by_length': {'short': 0, 'medium': 0, 'long': 0},
            'engagement_rate_distribution': [],
            'top_engagement_factors': {}
        }
        
        for video in videos:
            stats = video['statistics']
            duration = self._parse_duration(video['contentDetails']['duration'])
            views = int(stats.get('viewCount', 0))
            engagement = int(stats.get('likeCount', 0)) + int(stats.get('commentCount', 0))
            
            engagement_rate = (engagement / views * 100) if views > 0 else 0
            patterns['engagement_rate_distribution'].append(engagement_rate)
            
            # Categorize by video length
            if duration < 300:
                patterns['engagement_by_length']['short'] += engagement
            elif duration < 900:
                patterns['engagement_by_length']['medium'] += engagement
            else:
                patterns['engagement_by_length']['long'] += engagement
        
        return patterns
        
    def _analyze_retention_patterns(self, videos: List[Dict]) -> Dict:
        """Analyze viewer retention patterns"""
        patterns = {
            'avg_view_duration': 0,
            'completion_rate': 0,
            'retention_by_length': {'short': 0, 'medium': 0, 'long': 0}
        }
        
        total_duration = 0
        total_views = 0
        
        for video in videos:
            stats = video['statistics']
            duration = self._parse_duration(video['contentDetails']['duration'])
            views = int(stats.get('viewCount', 0))
            
            total_duration += duration
            total_views += views
            
            # Categorize by video length
            if duration < 300:
                patterns['retention_by_length']['short'] += views
            elif duration < 900:
                patterns['retention_by_length']['medium'] += views
            else:
                patterns['retention_by_length']['long'] += views
        
        if total_views > 0:
            patterns['avg_view_duration'] = total_duration / total_views
            
        return patterns

    def _parse_duration(self, duration: str) -> int:
        """Parse duration string into seconds"""
        # Assuming duration format is PT#H#M#S
        parts = duration.split('T')[1].split('H')
        hours = int(parts[0]) if parts[0] else 0
        minutes = int(parts[1].split('M')[0]) if len(parts) > 1 and parts[1].split('M')[0] else 0
        seconds = int(parts[1].split('M')[1].split('S')[0]) if len(parts) > 1 and parts[1].split('M')[1].split('S')[0] else 0
        
        return hours * 3600 + minutes * 60 + seconds
