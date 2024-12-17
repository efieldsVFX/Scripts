"""
TikTok API Client
Handles interactions with TikTok API
"""

import requests
from typing import Dict, List, Optional
from ..config.api_config import APIConfig
from datetime import datetime

class TikTokClient:
    def __init__(self):
        config = APIConfig.get_tiktok_config()
        if not APIConfig.validate_credentials(config):
            raise ValueError("Invalid TikTok API credentials")
            
        self.access_token = config['access_token']
        self.open_id = config['open_id']
        self.base_url = 'https://open.tiktokapis.com/v2'
        
    def get_video_insights(self, video_ids: List[str]) -> List[Dict]:
        """Get insights for specific videos"""
        try:
            url = f"{self.base_url}/video/query/"
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            payload = {
                'video_ids': video_ids,
                'fields': ['id', 'create_time', 'share_count', 'comment_count', 'like_count', 'view_count']
            }
            
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json().get('data', {}).get('videos', [])
            
        except Exception as e:
            print(f"Error fetching video insights: {str(e)}")
            return []
            
    def get_account_insights(self) -> Dict:
        """Get account-level insights"""
        try:
            url = f"{self.base_url}/research/user/info/"
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            payload = {
                'user_id': self.open_id,
                'fields': ['follower_count', 'following_count', 'likes_count', 'video_count']
            }
            
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json().get('data', {})
            
        except Exception as e:
            print(f"Error fetching account insights: {str(e)}")
            return {}
            
    def get_videos_list(self, max_count: int = 20) -> List[Dict]:
        """Get list of videos"""
        try:
            url = f"{self.base_url}/video/list/"
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            payload = {
                'fields': ['id', 'create_time', 'share_count', 'comment_count', 'like_count', 'view_count'],
                'max_count': max_count
            }
            
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json().get('data', {}).get('videos', [])
            
        except Exception as e:
            print(f"Error fetching videos list: {str(e)}")
            return []

    def get_behavioral_patterns(self, video_ids: List[str]) -> Dict:
        """Get viewer behavioral patterns using TikTok Business API"""
        try:
            insights = self.get_video_insights(video_ids)
            
            patterns = {
                'view_patterns': self._analyze_view_patterns(insights),
                'engagement_patterns': self._analyze_engagement_patterns(insights),
                'retention_patterns': self._analyze_retention_patterns(insights)
            }
            
            return patterns
            
        except Exception as e:
            print(f"Error fetching behavioral patterns: {str(e)}")
            return {}
            
    def get_recurring_views(self, video_ids: List[str]) -> Dict:
        """Get recurring views data using TikTok Insights API"""
        try:
            insights = self.get_video_insights(video_ids)
            
            recurring_data = {
                'total_views': 0,
                'recurring_views': 0,
                'recurring_percentage': 0,
                'videos': []
            }
            
            for video in insights:
                views = int(video.get('view_count', 0))
                # Estimate recurring views based on likes and comments
                engagement = int(video.get('like_count', 0)) + int(video.get('comment_count', 0))
                estimated_recurring = min(views, engagement * 2)  # Conservative estimate
                
                recurring_data['videos'].append({
                    'id': video['id'],
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
            
    def get_engagement_loyalty(self, video_ids: List[str]) -> Dict:
        """Get engagement loyalty metrics using TikTok Insights API"""
        try:
            insights = self.get_video_insights(video_ids)
            
            loyalty_data = {
                'overall_loyalty': 0,
                'engagement_consistency': 0,
                'videos': []
            }
            
            total_videos = len(insights)
            total_engagement = 0
            engagement_variations = []
            
            for video in insights:
                views = int(video.get('view_count', 0))
                likes = int(video.get('like_count', 0))
                comments = int(video.get('comment_count', 0))
                shares = int(video.get('share_count', 0))
                
                engagement_rate = ((likes + comments + shares) / views * 100) if views > 0 else 0
                total_engagement += engagement_rate
                engagement_variations.append(engagement_rate)
                
                loyalty_data['videos'].append({
                    'id': video['id'],
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
            
    def get_video_completion_metrics(self, video_ids: List[str]) -> List[Dict]:
        """Get video completion and looping rates"""
        try:
            url = f"{self.base_url}/business/video/metrics/"
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            payload = {
                'video_ids': video_ids,
                'metrics': ['video_view_completion_rate', 'video_loop_rate', 'average_watch_time']
            }
            
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json().get('data', [])
        except Exception as e:
            print(f"Error fetching video completion metrics: {str(e)}")
            return []

    def get_conversion_metrics(self, start_date: str, end_date: str) -> Dict:
        """Get conversion metrics including sales and leads"""
        try:
            url = f"{self.base_url}/business/conversion/metrics/"
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            payload = {
                'start_date': start_date,
                'end_date': end_date,
                'metrics': ['total_conversions', 'total_sales', 'total_leads', 'conversion_rate']
            }
            
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json().get('data', {})
        except Exception as e:
            print(f"Error fetching conversion metrics: {str(e)}")
            return {}
            
    def get_shopping_metrics(self, start_date: str, end_date: str) -> Dict:
        """Get shopping post performance metrics"""
        try:
            url = f"{self.base_url}/business/shopping/metrics/"
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            payload = {
                'start_date': start_date,
                'end_date': end_date,
                'metrics': [
                    'product_views',
                    'product_clicks',
                    'product_sales',
                    'total_revenue',
                    'conversion_rate'
                ]
            }
            
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json().get('data', {})
        except Exception as e:
            print(f"Error fetching shopping metrics: {str(e)}")
            return {}
            
    def get_trend_analysis(self, keywords: List[str], start_date: str, end_date: str) -> Dict:
        """Get trend analysis for specific keywords or topics"""
        try:
            url = f"{self.base_url}/business/insights/trends/"
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            payload = {
                'keywords': keywords,
                'start_date': start_date,
                'end_date': end_date,
                'metrics': [
                    'search_volume',
                    'growth_rate',
                    'engagement_rate',
                    'related_topics'
                ]
            }
            
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json().get('data', {})
        except Exception as e:
            print(f"Error fetching trend analysis: {str(e)}")
            return {}
            
    def _analyze_view_patterns(self, videos: List[Dict]) -> Dict:
        """Analyze viewing patterns from video data"""
        patterns = {
            'peak_hours': {},
            'weekday_distribution': {},
            'video_performance': []
        }
        
        for video in videos:
            views = int(video.get('view_count', 0))
            create_time = video.get('create_time', '')
            
            if create_time:
                # Extract hour and weekday from create_time
                try:
                    timestamp = datetime.fromisoformat(create_time.replace('Z', '+00:00'))
                    hour = timestamp.hour
                    weekday = timestamp.strftime('%A')
                    
                    patterns['peak_hours'][hour] = patterns['peak_hours'].get(hour, 0) + views
                    patterns['weekday_distribution'][weekday] = patterns['weekday_distribution'].get(weekday, 0) + views
                except ValueError:
                    pass
            
            patterns['video_performance'].append({
                'id': video['id'],
                'views': views
            })
        
        return patterns
        
    def _analyze_engagement_patterns(self, videos: List[Dict]) -> Dict:
        """Analyze engagement patterns from video data"""
        patterns = {
            'engagement_rate_distribution': [],
            'engagement_by_type': {
                'likes': [],
                'comments': [],
                'shares': []
            }
        }
        
        for video in videos:
            views = int(video.get('view_count', 0))
            likes = int(video.get('like_count', 0))
            comments = int(video.get('comment_count', 0))
            shares = int(video.get('share_count', 0))
            
            engagement_rate = ((likes + comments + shares) / views * 100) if views > 0 else 0
            patterns['engagement_rate_distribution'].append(engagement_rate)
            
            patterns['engagement_by_type']['likes'].append(likes)
            patterns['engagement_by_type']['comments'].append(comments)
            patterns['engagement_by_type']['shares'].append(shares)
        
        return patterns
        
    def _analyze_retention_patterns(self, videos: List[Dict]) -> Dict:
        """Analyze viewer retention patterns"""
        patterns = {
            'avg_completion_rate': 0,
            'retention_distribution': [],
            'performance_by_duration': {}
        }
        
        total_views = 0
        total_completion = 0
        
        for video in videos:
            views = int(video.get('view_count', 0))
            likes = int(video.get('like_count', 0))
            
            # Estimate completion rate based on likes (this is a rough estimate)
            estimated_completion = min(100, (likes / views * 200) if views > 0 else 0)
            patterns['retention_distribution'].append(estimated_completion)
            
            total_views += views
            total_completion += estimated_completion
        
        if len(videos) > 0:
            patterns['avg_completion_rate'] = total_completion / len(videos)
        
        return patterns
