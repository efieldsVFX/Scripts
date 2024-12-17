"""
Test data module for social media collectors when API keys are not available.
"""

from datetime import datetime, timedelta
import random

def generate_timestamp(days_ago=0):
    return (datetime.now() - timedelta(days=days_ago)).isoformat()

INSTAGRAM_TEST_DATA = {
    'profile': {
        'username': 'test_account',
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
            'created_at': generate_timestamp(i)
        } for i in range(30)
    ],
    'engagement': {
        'total_likes': 25000,
        'total_comments': 1200,
        'avg_likes_per_post': 350,
        'avg_comments_per_post': 45
    }
}

TWITTER_TEST_DATA = {
    'tweets': [
        {
            'id': f'tweet_{i}',
            'text': f'Sample tweet {i} #test #social',
            'created_at': generate_timestamp(i),
            'public_metrics': {
                'like_count': random.randint(10, 1000),
                'retweet_count': random.randint(5, 200),
                'reply_count': random.randint(1, 50)
            }
        } for i in range(50)
    ],
    'trending_topics': [
        {'name': '#trending1', 'volume': 50000},
        {'name': '#viral', 'volume': 45000},
        {'name': '#social', 'volume': 40000}
    ]
}

TIKTOK_TEST_DATA = {
    'videos': [
        {
            'id': f'video_{i}',
            'title': f'Test TikTok Video {i}',
            'create_time': int((datetime.now() - timedelta(days=i)).timestamp()),
            'share_url': f'https://tiktok.com/video_{i}',
            'cover_image_url': f'https://tiktok.com/cover_{i}.jpg',
            'metrics': {
                'video_views': random.randint(1000, 100000),
                'likes': random.randint(100, 10000),
                'comments': random.randint(10, 1000),
                'shares': random.randint(5, 500)
            }
        } for i in range(20)
    ],
    'audience': {
        'demographics': {
            'age_groups': {
                '13-17': 15,
                '18-24': 35,
                '25-34': 30,
                '35-44': 15,
                '45+': 5
            },
            'gender': {
                'female': 60,
                'male': 38,
                'other': 2
            }
        }
    }
}

YOUTUBE_TEST_DATA = {
    'channel_stats': {
        'viewCount': '1000000',
        'subscriberCount': '50000',
        'videoCount': '200'
    },
    'videos': [
        {
            'id': f'video_{i}',
            'snippet': {
                'title': f'Test YouTube Video {i}',
                'description': f'Description for video {i}',
                'publishedAt': generate_timestamp(i),
                'thumbnails': {
                    'default': {'url': f'https://youtube.com/thumb_{i}.jpg'}
                }
            },
            'statistics': {
                'viewCount': str(random.randint(1000, 100000)),
                'likeCount': str(random.randint(100, 10000)),
                'commentCount': str(random.randint(10, 1000))
            }
        } for i in range(30)
    ]
}
