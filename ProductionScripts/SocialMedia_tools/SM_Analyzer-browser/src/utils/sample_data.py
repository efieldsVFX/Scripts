"""
Sample data generator for testing and demonstration
"""

from datetime import datetime, timedelta
import random
import time
import logging
import sys
from typing import Dict, List

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Cache for sample data
_sample_data_cache = {}
_cache_timestamp = None
_cache_ttl = 300  # 5 minutes

def get_cached_sample_data() -> Dict:
    """Get sample data from cache or generate new data if cache expired"""
    global _sample_data_cache, _cache_timestamp
    
    current_time = time.time()
    logger.info("Checking sample data cache...")
    
    # Check if cache is valid
    if _cache_timestamp and current_time - _cache_timestamp < _cache_ttl:
        logger.info("Using cached data")
        return _sample_data_cache
        
    try:
        logger.info("Generating new sample data...")
        # Generate new data and update cache
        _sample_data_cache = generate_sample_data()
        _cache_timestamp = current_time
        logger.info("Successfully generated new sample data")
        return _sample_data_cache
    except Exception as e:
        logger.error(f"Error generating sample data: {str(e)}", exc_info=True)
        return None

def generate_sample_data() -> Dict:
    """Generate sample social media data for testing"""
    platforms = ['Instagram', 'Twitter', 'TikTok', 'YouTube']
    current_time = datetime.now()
    logger.info("Starting sample data generation...")
    
    sample_data = {}
    
    for platform in platforms:
        try:
            logger.info(f"Generating data for platform: {platform}")
            
            # Generate engagement patterns
            engagement_patterns = generate_engagement_patterns()
            
            # Generate posts
            posts = generate_sample_posts(platform, current_time)
            
            # Generate audience insights
            audience_data = generate_audience_insights()
            
            # Calculate metrics from posts
            total_engagement = sum(post['engagement_score'] for post in posts)
            total_posts = len(posts)
            engagement_rate = total_engagement / total_posts if total_posts > 0 else 0
            
            sample_data[platform] = {
                'metrics': {
                    'followers': random.randint(10000, 1000000),
                    'engagement_rate': round(engagement_rate, 2),
                    'total_posts': total_posts,
                    'total_engagement': total_engagement
                },
                'posts': posts,
                'engagement_patterns': engagement_patterns,
                'audience_insights': audience_data,
                'content_performance': {
                    'top_posts': sorted(posts, key=lambda x: x['engagement_score'], reverse=True)[:5],
                    'growth_trends': {
                        'followers': [random.randint(1000, 5000) for _ in range(30)],
                        'engagement': [random.uniform(2.0, 8.0) for _ in range(30)]
                    },
                    'optimal_times': {
                        'daily': engagement_patterns['daily_engagement'],
                        'hourly': engagement_patterns['hourly_engagement']
                    },
                    'content_themes': {
                        theme: random.uniform(0.5, 5.0)
                        for theme in ['educational', 'entertainment', 'promotional', 'user-generated']
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating data for {platform}: {str(e)}")
            continue
    
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
    
    # Use placeholder images from a reliable source
    def get_placeholder_image(width=800, height=600, id=None):
        if id is None:
            id = random.randint(1, 1000)
        # Using Unsplash's reliable image service
        return f"https://source.unsplash.com/random/{width}x{height}?sig={id}"
    
    try:
        logger.info(f"Generating sample posts for {platform}...")
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
                    'image': get_placeholder_image() if content_type in ['image', 'carousel'] else None,
                    'video_url': get_placeholder_image() if content_type in ['video', 'reel'] else None,
                    'caption': f"Sample {content_type} post caption with #{' #'.join(random.sample(themes, 2))}"
                })
            elif platform == 'Twitter':
                post.update({
                    'text': f"Sample tweet about {random.choice(themes)} #{' #'.join(random.sample(themes, 1))}",
                    'image': get_placeholder_image() if content_type == 'image' else None
                })
            elif platform == 'TikTok':
                post.update({
                    'video_url': get_placeholder_image(),
                    'video_thumbnail': get_placeholder_image(width=400, height=600),
                    'caption': f"#{' #'.join(random.sample(themes, 3))}"
                })
            elif platform == 'YouTube':
                post.update({
                    'title': f"Sample {random.choice(themes)} Video",
                    'thumbnail': get_placeholder_image(width=1280, height=720),
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
        logger.info(f"Successfully generated sample posts for {platform}")
        return posts
    except Exception as e:
        logger.error(f"Error generating sample posts for {platform}: {str(e)}", exc_info=True)
        return []

def generate_content_ideas(platform: str, platform_data: Dict) -> List[Dict]:
    """Generate content ideas based on platform and performance data"""
    content_types = {
        'Instagram': ['Photo', 'Carousel', 'Reel', 'Story'],
        'Twitter': ['Text', 'Image', 'Poll', 'Thread'],
        'TikTok': ['Short-form Video', 'Duet', 'Challenge', 'Tutorial'],
        'YouTube': ['Long-form Video', 'Shorts', 'Live Stream', 'Series']
    }
    
    themes = [
        'Behind the Scenes', 'Product Showcase', 'Industry Insights',
        'User Success Stories', 'How-to Guide', 'Trending Topics',
        'Company Culture', 'Innovation Spotlight', 'Expert Interview'
    ]
    
    ideas = []
    num_ideas = random.randint(3, 5)
    
    for _ in range(num_ideas):
        content_type = random.choice(content_types.get(platform, content_types['Instagram']))
        theme = random.choice(themes)
        
        idea = {
            'content_type': content_type,
            'theme': theme,
            'suggested_elements': [
                f"Include {random.choice(['trending', 'branded', 'custom'])} hashtags",
                f"Feature {random.choice(['customer testimonial', 'product demo', 'team member'])}",
                f"Add {random.choice(['call-to-action', 'question', 'poll'])}",
                f"Incorporate {random.choice(['music', 'sound effects', 'voice over'])}"
            ],
            'optimal_posting_time': random.randint(8, 20),
            'predicted_impact': round(random.uniform(7.5, 9.8), 2),
            'target_reactions': {
                '👍 Likes': random.randint(1000, 5000),
                '💬 Comments': random.randint(100, 500),
                '🔄 Shares': random.randint(50, 250)
            }
        }
        ideas.append(idea)
    
    return ideas

def generate_engagement_patterns() -> Dict:
    """Generate realistic engagement patterns with daily and hourly breakdowns"""
    days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    peak_hours = [(8, 10), (12, 14), (19, 22)]  # Common peak engagement times
    
    patterns = {
        'daily_engagement': {},
        'hourly_engagement': {},
        'content_performance': {
            'photos': round(random.uniform(3.5, 7.0), 2),
            'videos': round(random.uniform(5.0, 12.0), 2),
            'stories': round(random.uniform(2.5, 5.0), 2),
            'reels': round(random.uniform(8.0, 15.0), 2),
            'live_streams': round(random.uniform(6.0, 10.0), 2)
        },
        'engagement_quality': {
            'comments_sentiment': {
                'positive': round(random.uniform(65, 85), 1),
                'neutral': round(random.uniform(10, 25), 1),
                'negative': round(random.uniform(5, 15), 1)
            },
            'share_rate': round(random.uniform(15, 35), 1),
            'save_rate': round(random.uniform(10, 25), 1),
            'viral_coefficient': round(random.uniform(1.5, 3.0), 2)
        }
    }
    
    # Generate daily engagement with realistic patterns
    total = 100
    daily_values = []
    for _ in range(7):
        value = random.uniform(10, 20)
        daily_values.append(value)
    
    # Normalize to percentages
    total = sum(daily_values)
    for day, value in zip(days_of_week, daily_values):
        patterns['daily_engagement'][day] = round((value / total) * 100, 1)
    
    # Generate hourly engagement with peak times
    for hour in range(24):
        base_engagement = 2.0  # Base engagement percentage
        for peak_start, peak_end in peak_hours:
            if peak_start <= hour <= peak_end:
                base_engagement = random.uniform(6.0, 10.0)
                break
        patterns['hourly_engagement'][str(hour).zfill(2)] = round(base_engagement, 1)
    
    return patterns

def generate_audience_insights() -> Dict:
    """Generate detailed audience insights with demographic and behavioral data"""
    return {
        'demographics': {
            'age_distribution': {
                '18-24': round(random.uniform(25, 35), 1),
                '25-34': round(random.uniform(30, 40), 1),
                '35-44': round(random.uniform(15, 25), 1),
                '45-54': round(random.uniform(8, 15), 1),
                '55+': round(random.uniform(5, 10), 1)
            },
            'gender_distribution': {
                'male': round(random.uniform(45, 55), 1),
                'female': round(random.uniform(45, 55), 1),
                'other': round(random.uniform(1, 3), 1)
            },
            'top_locations': {
                'United States': round(random.uniform(35, 45), 1),
                'United Kingdom': round(random.uniform(10, 15), 1),
                'Canada': round(random.uniform(8, 12), 1),
                'Australia': round(random.uniform(5, 10), 1),
                'Germany': round(random.uniform(5, 8), 1)
            }
        },
        'interests': {
            'Technology': round(random.uniform(70, 90), 1),
            'Business': round(random.uniform(60, 80), 1),
            'Innovation': round(random.uniform(65, 85), 1),
            'Investment': round(random.uniform(55, 75), 1),
            'Startups': round(random.uniform(50, 70), 1)
        },
        'behavior': {
            'average_session_duration': round(random.uniform(8, 15), 1),
            'return_visitor_rate': round(random.uniform(35, 55), 1),
            'content_interaction_rate': round(random.uniform(25, 45), 1),
            'brand_affinity_score': round(random.uniform(75, 95), 1)
        },
        'growth_metrics': {
            'follower_growth_rate': round(random.uniform(3.5, 7.5), 2),
            'engagement_growth_rate': round(random.uniform(4.0, 8.0), 2),
            'retention_rate': round(random.uniform(65, 85), 1),
            'brand_mention_growth': round(random.uniform(25, 45), 1)
        }
    }
