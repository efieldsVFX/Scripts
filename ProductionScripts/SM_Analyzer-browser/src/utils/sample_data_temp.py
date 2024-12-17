"""
Sample data generator for testing and demonstration
"""

from datetime import datetime, timedelta
import random
import time
from typing import Dict, List

# Cache for sample data
_sample_data_cache = {}
_cache_timestamp = None
_cache_ttl = 300  # 5 minutes

def get_cached_sample_data() -> Dict:
    """Get sample data from cache or generate new data if cache expired"""
    global _sample_data_cache, _cache_timestamp
    
    current_time = time.time()
    
    # Check if cache is valid
    if _cache_timestamp and current_time - _cache_timestamp < _cache_ttl:
        return _sample_data_cache
        
    try:
        # Generate new data and update cache
        _sample_data_cache = generate_sample_data()
        _cache_timestamp = current_time
        return _sample_data_cache
    except Exception as e:
        logger.error(f"Error generating sample data: {str(e)}")
        return None

def generate_sample_data() -> Dict:
    """Generate sample social media data for testing"""
    platforms = ['Instagram', 'Twitter', 'TikTok', 'YouTube']
    current_time = datetime.now()
    
    sample_data = {}
    for platform in platforms:
        try:
            platform_data = {
                'posts': generate_sample_posts(platform, current_time),
                'engagement_patterns': generate_engagement_patterns(),
                'audience_insights': generate_audience_insights(),
                'metrics': {
                    'followers': random.randint(100000, 1000000),
                    'engagement_rate': round(random.uniform(2.0, 8.0), 2),
                    'revenue': random.randint(1000, 15000),
                    'posts_count': random.randint(100, 1000),
                    'reach': random.randint(50000, 500000),
                    'impressions': random.randint(100000, 1000000)
                }
            }
            sample_data[platform] = platform_data
        except Exception as e:
            logger.error(f"Error generating data for platform {platform}: {str(e)}")
            continue
    
    if not sample_data:
        raise ValueError("Failed to generate data for any platform")
    
    # Add aggregated metrics
    try:
        sample_data['followers'] = {
            platform: data['metrics']['followers']
            for platform, data in sample_data.items()
            if isinstance(data, dict) and 'metrics' in data
        }
        
        sample_data['engagement'] = {
            platform: data['metrics']['engagement_rate']
            for platform, data in sample_data.items()
            if isinstance(data, dict) and 'metrics' in data
        }
        
        sample_data['revenue'] = {
            platform: data['metrics']['revenue']
            for platform, data in sample_data.items()
            if isinstance(data, dict) and 'metrics' in data
        }
        
        sample_data['top_posts'] = {
            platform: data['posts'][:2]  # Take top 2 posts
            for platform, data in sample_data.items()
            if isinstance(data, dict) and 'posts' in data
        }
    except Exception as e:
        logger.error(f"Error generating aggregated metrics: {str(e)}")
    
    # Add Reddit-specific data
    try:
        sample_data['reddit_specific'] = {
            'subreddit_distribution': {
                'r/EDGLRD': random.randint(10000, 50000),
                'r/streetwear': random.randint(10000, 30000),
                'r/fashion': random.randint(5000, 25000),
                'r/sustainability': random.randint(5000, 20000),
                'r/brandname': random.randint(5000, 15000)
            },
            'post_types': {
                'Image': random.randint(30, 50),
                'Text': random.randint(20, 30),
                'Link': random.randint(10, 25),
                'Video': random.randint(5, 15)
            },
            'karma_stats': {
                'Post Karma': random.randint(50000, 100000),
                'Comment Karma': random.randint(20000, 50000)
            }
        }
    except Exception as e:
        logger.error(f"Error generating Reddit-specific data: {str(e)}")
    
    return sample_data

def generate_sample_posts(platform: str, current_time: datetime) -> List[Dict]:
    """Generate sample posts for a platform"""
    posts = []
    content_types = {
        'Instagram': ['image', 'video', 'carousel', 'reel', 'story'],
        'Twitter': ['text', 'image', 'video'],
        'TikTok': ['video', 'story'],
        'YouTube': ['video', 'short']
    }
    
    themes = [
        'behind the scenes', 'product showcase', 'user testimonial',
        'industry insights', 'how-to tutorial', 'trending topic',
        'company culture', 'customer success story', 'expert interview'
    ]
    
    elements = [
        'hashtags', 'mentions', 'emojis', 'call-to-action',
        'question', 'poll', 'link', 'location tag'
    ]
    
    try:
        for i in range(20):  # Generate 20 posts per platform
            post_time = current_time - timedelta(days=random.randint(0, 30))
            content_type = random.choice(content_types.get(platform, ['text']))
            
            engagement_metrics = {
                'likes': random.randint(100, 10000),
                'comments': random.randint(10, 1000),
                'shares': random.randint(5, 500),
                'saves': random.randint(20, 2000),
                'views': random.randint(1000, 100000)
            }
            
            post = {
                'id': f"{platform.lower()}_post_{i}",
                'type': content_type,
                'created_at': post_time.isoformat(),
                'metrics': engagement_metrics,
                'themes': random.sample(themes, random.randint(1, 3)),
                'elements': random.sample(elements, random.randint(2, 5)),
                'reactions': {
                    'love': random.randint(50, 5000),
                    'laugh': random.randint(20, 2000),
                    'wow': random.randint(10, 1000),
                    'sad': random.randint(5, 500)
                }
            }
            
            # Add platform-specific fields
            if platform == 'Instagram':
                post.update({
                    'image': 'sample_image_url.jpg' if content_type in ['image', 'carousel'] else None,
                    'video_url': 'sample_video_url.mp4' if content_type in ['video', 'reel'] else None,
                    'caption': f"Sample {content_type} post caption with #{' #'.join(random.sample(themes, 2))}"
                })
            elif platform == 'Twitter':
                post.update({
                    'text': f"Sample tweet about {random.choice(themes)} #{' #'.join(random.sample(themes, 1))}",
                    'image': 'sample_image_url.jpg' if content_type == 'image' else None
                })
            elif platform == 'TikTok':
                post.update({
                    'video_url': 'sample_video_url.mp4',
                    'video_thumbnail': 'sample_thumbnail.jpg',
                    'caption': f"#{' #'.join(random.sample(themes, 3))}"
                })
            elif platform == 'YouTube':
                post.update({
                    'title': f"Sample {random.choice(themes)} Video",
                    'thumbnail': 'sample_thumbnail.jpg',
                    'duration': random.randint(60, 3600) if content_type == 'video' else random.randint(15, 60)
                })
            
            posts.append(post)
        
        # Sort by engagement score
        for post in posts:
            post['engagement_score'] = sum(
                score * weight
                for metric, score in post['metrics'].items()
                for metric_name, weight in [
                    ('likes', 1),
                    ('comments', 2),
                    ('shares', 3),
                    ('saves', 4),
                    ('views', 0.1)
                ]
                if metric == metric_name
            )
        
        posts.sort(key=lambda x: x['engagement_score'], reverse=True)
        return posts
    except Exception as e:
        logger.error(f"Error generating sample posts for {platform}: {str(e)}")
        return []

def generate_engagement_patterns() -> Dict:
    """Generate sample engagement patterns"""
    try:
        hours = list(range(24))
        peak_times = sorted([
            (hour, random.uniform(0.5, 1.0))
            for hour in hours
        ], key=lambda x: x[1], reverse=True)
        
        return {
            'element_performance': {
                'hashtags': random.uniform(0.6, 0.9),
                'mentions': random.uniform(0.4, 0.7),
                'emojis': random.uniform(0.5, 0.8),
                'call-to-action': random.uniform(0.7, 1.0),
                'question': random.uniform(0.5, 0.9),
                'poll': random.uniform(0.4, 0.8),
                'link': random.uniform(0.3, 0.6),
                'location tag': random.uniform(0.4, 0.7)
            },
            'peak_times': peak_times,
            'content_themes': {
                'behind the scenes': random.uniform(0.7, 1.0),
                'product showcase': random.uniform(0.6, 0.9),
                'user testimonial': random.uniform(0.7, 0.95),
                'industry insights': random.uniform(0.5, 0.8),
                'how-to tutorial': random.uniform(0.6, 0.9),
                'trending topic': random.uniform(0.8, 1.0),
                'company culture': random.uniform(0.5, 0.8),
                'customer success story': random.uniform(0.7, 0.95),
                'expert interview': random.uniform(0.6, 0.85)
            }
        }
    except Exception as e:
        logger.error(f"Error generating engagement patterns: {str(e)}")
        return {}

def generate_audience_insights() -> Dict:
    """Generate sample audience insights"""
    try:
        return {
            'demographics': {
                'age_groups': {
                    '18-24': random.uniform(0.1, 0.3),
                    '25-34': random.uniform(0.2, 0.4),
                    '35-44': random.uniform(0.15, 0.25),
                    '45-54': random.uniform(0.1, 0.2),
                    '55+': random.uniform(0.05, 0.15)
                },
                'gender': {
                    'male': random.uniform(0.4, 0.6),
                    'female': random.uniform(0.4, 0.6)
                },
                'locations': {
                    'United States': random.uniform(0.3, 0.5),
                    'United Kingdom': random.uniform(0.1, 0.2),
                    'Canada': random.uniform(0.05, 0.15),
                    'Australia': random.uniform(0.05, 0.1),
                    'Others': random.uniform(0.1, 0.2)
                }
            },
            'interests': [
                'Technology', 'Business', 'Entertainment',
                'Lifestyle', 'Fashion', 'Sports', 'Travel'
            ],
            'active_times': {
                'weekday': {
                    'morning': random.uniform(0.2, 0.4),
                    'afternoon': random.uniform(0.3, 0.5),
                    'evening': random.uniform(0.4, 0.6),
                    'night': random.uniform(0.1, 0.3)
                },
                'weekend': {
                    'morning': random.uniform(0.3, 0.5),
                    'afternoon': random.uniform(0.4, 0.6),
                    'evening': random.uniform(0.3, 0.5),
                    'night': random.uniform(0.2, 0.4)
                }
            }
        }
    except Exception as e:
        logger.error(f"Error generating audience insights: {str(e)}")
        return {}
