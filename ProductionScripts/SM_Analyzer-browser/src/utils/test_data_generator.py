"""
Test Data Generator
Generates realistic test data for each social media platform
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from typing import Dict, List

class TestDataGenerator:
    def __init__(self):
        self.start_date = datetime.now() - timedelta(days=30)
        self.usernames = ['user' + str(i) for i in range(1, 21)]
        self.hashtags = ['#EDGLRD', '#gaming', '#esports', '#streaming', '#content', 
                        '#community', '#tech', '#digital', '#social', '#creator']
        
    def generate_instagram_data(self) -> Dict:
        """Generate test data for Instagram"""
        posts = []
        stories = []
        reels = []
        
        for _ in range(50):
            post_date = self.start_date + timedelta(
                days=random.randint(0, 29),
                hours=random.randint(0, 23)
            )
            
            posts.append({
                'id': f'post_{random.randint(1000, 9999)}',
                'type': random.choice(['image', 'carousel', 'video']),
                'caption': f'Test post with {random.choice(self.hashtags)}',
                'likes': random.randint(100, 1000),
                'comments': random.randint(10, 100),
                'shares': random.randint(5, 50),
                'saves': random.randint(10, 200),
                'reach': random.randint(1000, 5000),
                'impressions': random.randint(2000, 10000),
                'engagement_rate': random.uniform(2.0, 8.0),
                'posted_at': post_date
            })
            
        return {
            'posts': pd.DataFrame(posts),
            'audience': {
                'followers': random.randint(5000, 10000),
                'following': random.randint(1000, 2000),
                'demographics': {
                    'age_ranges': {
                        '13-17': 0.05,
                        '18-24': 0.35,
                        '25-34': 0.40,
                        '35-44': 0.15,
                        '45+': 0.05
                    },
                    'gender': {
                        'male': 0.65,
                        'female': 0.35
                    },
                    'top_locations': [
                        ('United States', 0.40),
                        ('United Kingdom', 0.15),
                        ('Canada', 0.10),
                        ('Germany', 0.08),
                        ('Australia', 0.07)
                    ]
                }
            }
        }
    
    def generate_twitter_data(self) -> Dict:
        """Generate test data for Twitter"""
        tweets = []
        
        for _ in range(100):
            tweet_date = self.start_date + timedelta(
                days=random.randint(0, 29),
                hours=random.randint(0, 23)
            )
            
            tweets.append({
                'id': f'tweet_{random.randint(1000, 9999)}',
                'text': f'Test tweet about EDGLRD {random.choice(self.hashtags)}',
                'likes': random.randint(50, 500),
                'retweets': random.randint(10, 100),
                'replies': random.randint(5, 50),
                'impressions': random.randint(1000, 5000),
                'engagement_rate': random.uniform(1.0, 5.0),
                'created_at': tweet_date
            })
            
        return {
            'tweets': pd.DataFrame(tweets),
            'audience': {
                'followers': random.randint(3000, 8000),
                'following': random.randint(500, 1500),
                'demographics': {
                    'interests': [
                        'Gaming',
                        'Technology',
                        'Esports',
                        'Entertainment',
                        'Digital Culture'
                    ]
                }
            }
        }
    
    def generate_reddit_data(self) -> Dict:
        """Generate test data for Reddit"""
        # Reddit data is intentionally disabled to use actual API data
        return {}

    def generate_youtube_data(self) -> Dict:
        """Generate test data for YouTube"""
        videos = []
        
        for _ in range(20):
            video_date = self.start_date + timedelta(
                days=random.randint(0, 29),
                hours=random.randint(0, 23)
            )
            
            duration = random.randint(180, 1800)  # 3-30 minutes
            views = random.randint(1000, 50000)
            
            videos.append({
                'id': f'video_{random.randint(1000, 9999)}',
                'title': f'EDGLRD Gaming {random.choice(self.hashtags)}',
                'views': views,
                'likes': int(views * random.uniform(0.05, 0.15)),
                'comments': int(views * random.uniform(0.01, 0.05)),
                'duration': duration,
                'avg_watch_time': random.uniform(duration * 0.3, duration * 0.7),
                'retention_rate': random.uniform(0.3, 0.7),
                'published_at': video_date
            })
            
        return {
            'videos': pd.DataFrame(videos),
            'channel_stats': {
                'subscribers': random.randint(10000, 50000),
                'total_views': random.randint(500000, 2000000),
                'avg_view_duration': random.uniform(300, 900),
                'demographics': {
                    'age_ranges': {
                        '13-17': 0.10,
                        '18-24': 0.40,
                        '25-34': 0.35,
                        '35-44': 0.10,
                        '45+': 0.05
                    },
                    'gender': {
                        'male': 0.70,
                        'female': 0.30
                    }
                }
            }
        }

    def generate_all_platforms_data(self) -> Dict:
        """Generate test data for all platforms"""
        return {
            'instagram': self.generate_instagram_data(),
            'twitter': self.generate_twitter_data(),
            # Reddit data is intentionally disabled to use actual API data
            'youtube': self.generate_youtube_data()
        }
