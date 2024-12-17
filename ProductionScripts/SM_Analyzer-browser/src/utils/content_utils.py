"""
Content Analysis Utilities
Helper functions for content analysis and idea generation
"""

from typing import Dict, List, Union
from datetime import datetime, timedelta
import numpy as np
from collections import Counter

def calculate_engagement_score(metrics: Dict[str, int]) -> float:
    """
    Calculate normalized engagement score
    
    Args:
        metrics: Dict containing engagement metrics (likes, comments, shares, etc.)
        
    Returns:
        float: Normalized engagement score
    """
    weights = {
        'likes': 1,
        'comments': 2,
        'shares': 3,
        'saves': 4,
        'clicks': 2,
        'views': 0.1
    }
    
    score = 0
    for metric, count in metrics.items():
        score += count * weights.get(metric, 1)
        
    return score

def identify_peak_times(timestamps: List[str], engagement_scores: List[float]) -> List[int]:
    """
    Identify optimal posting times based on engagement
    
    Args:
        timestamps: List of ISO format timestamps
        engagement_scores: List of corresponding engagement scores
        
    Returns:
        List of hours (0-23) with highest engagement
    """
    hourly_scores = {}
    
    for timestamp, score in zip(timestamps, engagement_scores):
        hour = datetime.fromisoformat(timestamp).hour
        if hour not in hourly_scores:
            hourly_scores[hour] = []
        hourly_scores[hour].append(score)
    
    # Calculate average score for each hour
    avg_scores = {
        hour: np.mean(scores) for hour, scores in hourly_scores.items()
    }
    
    # Return top 3 hours
    return sorted(avg_scores.items(), key=lambda x: x[1], reverse=True)[:3]

def extract_content_elements(post_data: Dict) -> List[str]:
    """
    Extract key content elements from post data
    
    Args:
        post_data: Dict containing post information
        
    Returns:
        List of identified content elements
    """
    elements = set()
    
    # Check for media types
    if post_data.get('has_image'):
        elements.add('image')
    if post_data.get('has_video'):
        elements.add('video')
    if post_data.get('has_carousel'):
        elements.add('carousel')
        
    # Check for interactive elements
    if post_data.get('has_hashtags'):
        elements.add('hashtags')
    if post_data.get('has_mentions'):
        elements.add('mentions')
    if post_data.get('has_links'):
        elements.add('links')
    if post_data.get('has_emojis'):
        elements.add('emojis')
        
    # Check for content structure
    text = post_data.get('text', '')
    if text:
        if '?' in text:
            elements.add('question')
        if any(call in text.lower() for call in ['comment', 'share', 'like', 'follow']):
            elements.add('call-to-action')
            
    return list(elements)

def analyze_content_themes(posts: List[Dict]) -> Dict[str, float]:
    """
    Analyze common themes in successful posts
    
    Args:
        posts: List of post data dictionaries
        
    Returns:
        Dict mapping themes to their success scores
    """
    theme_scores = defaultdict(list)
    
    for post in posts:
        themes = post.get('themes', [])
        score = post.get('engagement_score', 0)
        
        for theme in themes:
            theme_scores[theme].append(score)
            
    # Calculate average score for each theme
    return {
        theme: np.mean(scores)
        for theme, scores in theme_scores.items()
    }

def predict_content_impact(
    content_type: str,
    elements: List[str],
    historical_data: Dict
) -> float:
    """
    Predict potential impact of content based on historical performance
    
    Args:
        content_type: Type of content (image, video, etc.)
        elements: List of content elements
        historical_data: Dict containing historical performance data
        
    Returns:
        float: Predicted impact score
    """
    base_score = historical_data.get('avg_engagement', 0)
    
    # Apply content type multiplier
    type_multiplier = historical_data.get('type_multipliers', {}).get(content_type, 1.0)
    
    # Calculate element boost
    element_scores = historical_data.get('element_scores', {})
    element_boost = sum(element_scores.get(element, 0) for element in elements)
    
    return base_score * type_multiplier * (1 + element_boost)
