"""
Content Idea Generator Module
Generates content ideas based on analysis of successful social media posts
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
import random
from collections import defaultdict

class ContentIdeaGenerator:
    def __init__(self):
        """Initialize content idea generator"""
        self.logger = logging.getLogger(__name__)
        self.content_types = ['image', 'video', 'text', 'story', 'reel', 'carousel']
        
    def generate_ideas(self, analysis_data: Dict) -> List[Dict]:
        """
        Generate content ideas based on analyzed data
        
        Args:
            analysis_data: Dict containing analyzed social media data
            
        Returns:
            List of content ideas with details
        """
        try:
            ideas = []
            
            # EDGLRD-specific content themes
            themes = [
                'Gaming Strategy', 'Esports Updates', 'Community Highlights',
                'Tech Reviews', 'Digital Culture', 'Creator Spotlights',
                'Tutorial Series', 'Behind the Scenes', 'Community Events'
            ]
            
            content_formats = {
                'instagram': ['Carousel', 'Reel', 'Story', 'Post'],
                'twitter': ['Tweet Thread', 'Poll', 'Video Tweet', 'Image Tweet'],
                'reddit': ['Discussion Post', 'Image Post', 'Link Post', 'Poll'],
                'youtube': ['Tutorial', 'Review', 'Vlog', 'Stream Highlights']
            }
            
            # Generate ideas for each platform
            for platform, data in analysis_data.items():
                if not isinstance(data, dict):
                    continue
                    
                platform_ideas = []
                platform_formats = content_formats.get(platform.lower(), ['Post'])
                
                # Get engagement data if available
                engagement_data = data.get('engagement_patterns', {})
                audience_data = data.get('audience_insights', {})
                
                for _ in range(5):  # Generate 5 ideas per platform
                    theme = random.choice(themes)
                    content_format = random.choice(platform_formats)
                    
                    idea = {
                        'platform': platform,
                        'title': f"{theme} - {content_format}",
                        'description': self._generate_description(theme, content_format),
                        'content_type': content_format,
                        'theme': theme,
                        'target_audience': self._get_target_audience(audience_data),
                        'estimated_engagement': self._estimate_engagement(engagement_data),
                        'best_posting_time': self._get_best_posting_time(engagement_data),
                        'hashtags': self._generate_hashtags(theme)
                    }
                    
                    platform_ideas.append(idea)
                
                if platform_ideas:
                    ideas.extend(platform_ideas)
            
            return ideas
            
        except Exception as e:
            self.logger.error(f"Error generating content ideas: {str(e)}")
            return []
    
    def _generate_description(self, theme: str, format: str) -> str:
        """Generate a detailed description for the content idea"""
        descriptions = {
            'Gaming Strategy': [
                "Share advanced tips and tricks for popular games",
                "Break down pro player strategies",
                "Analyze meta changes and their impact"
            ],
            'Esports Updates': [
                "Cover major tournament highlights",
                "Interview pro players",
                "Analyze competitive meta shifts"
            ],
            'Community Highlights': [
                "Showcase community member achievements",
                "Feature user-generated content",
                "Spotlight community events"
            ],
            'Tech Reviews': [
                "Review latest gaming gear",
                "Compare gaming setups",
                "Test new gaming tech"
            ],
            'Digital Culture': [
                "Explore trending gaming memes",
                "Discuss gaming industry news",
                "Analyze gaming culture trends"
            ]
        }
        
        base_desc = random.choice(descriptions.get(theme, ["Create engaging content"]))
        return f"{base_desc} in an engaging {format.lower()} format"
    
    def _get_target_audience(self, data: Dict) -> str:
        """Determine target audience based on platform data"""
        audiences = [
            "Gamers aged 18-24",
            "Competitive esports enthusiasts",
            "Tech-savvy content creators",
            "Gaming community leaders",
            "Casual gamers and viewers"
        ]
        return random.choice(audiences)
    
    def _estimate_engagement(self, data: Dict) -> str:
        """Estimate potential engagement based on historical data"""
        return f"Expected {random.randint(500, 5000)} impressions"
    
    def _get_best_posting_time(self, data: Dict) -> str:
        """Determine optimal posting time based on historical data"""
        times = ["Morning (9-11 AM)", "Afternoon (2-4 PM)", "Evening (7-9 PM)", "Night (10 PM-12 AM)"]
        return random.choice(times)
    
    def _generate_hashtags(self, theme: str) -> List[str]:
        """Generate relevant hashtags for the content"""
        base_hashtags = ["#EDGLRD", "#Gaming", "#Content"]
        theme_hashtags = {
            'Gaming Strategy': ["#GamingTips", "#ProGaming", "#GameStrategy"],
            'Esports Updates': ["#Esports", "#CompetitiveGaming", "#TournamentLife"],
            'Community Highlights': ["#CommunitySpotlight", "#GamingCommunity", "#ContentCreator"],
            'Tech Reviews': ["#GamingSetup", "#TechReview", "#GamingGear"],
            'Digital Culture': ["#GamingCulture", "#DigitalAge", "#GamingLife"]
        }
        
        return base_hashtags + theme_hashtags.get(theme, [])
    
    def format_idea(self, idea: Dict) -> str:
        """Format a content idea into a readable string"""
        formatted = f"Title: {idea['title']}\n"
        
        if idea['description']:
            formatted += f"Description: {idea['description']}\n"
            
        if idea['content_type']:
            formatted += f"Type: {idea['content_type']}\n"
            
        if idea['target_audience']:
            formatted += f"Target Audience: {idea['target_audience']}\n"
            
        if idea['estimated_engagement']:
            formatted += f"Estimated Engagement: {idea['estimated_engagement']}\n"
            
        if idea['best_posting_time']:
            formatted += f"Best Posting Time: {idea['best_posting_time']}\n"
            
        if idea['hashtags']:
            formatted += "Hashtags:\n"
            for hashtag in idea['hashtags']:
                formatted += f"- {hashtag}\n"
                
        return formatted
