"""
Analytics Manager
Unified interface for accessing all social media analytics
"""

import logging
import os
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import pandas as pd
from collections import defaultdict
import numpy as np

from src.collectors.instagram_collector import InstagramCollector
from src.collectors.tiktok_collector import TikTokCollector
from src.collectors.twitter_collector import TwitterCollector
from src.collectors.youtube_collector import YouTubeCollector
from src.collectors.reddit_collector import RedditCollector

from src.analysis.content_analyzer import ContentAnalyzer
from src.analysis.audience_analyzer import create_audience_analyzer
from src.analysis.engagement_analyzer import EngagementAnalyzer
from src.analysis.content_journey_analyzer import ContentJourneyAnalyzer
from src.analysis.predictive_analyzer import PredictiveAnalyzer
from src.visualization.dashboard import AnalyticsDashboard
from src.generation.content_idea_generator import ContentIdeaGenerator
from utils.content_utils import (
    calculate_engagement_score,
    identify_peak_times,
    extract_content_elements,
    analyze_content_themes,
    predict_content_impact
)

class AnalyticsManager:
    def __init__(self):
        """Initialize analytics manager"""
        # Load configuration
        self.config = {
            'api_auth': {
                'instagram': {
                    'client_id': os.getenv('INSTAGRAM_CLIENT_ID', ''),
                    'client_secret': os.getenv('INSTAGRAM_CLIENT_SECRET', ''),
                    'access_token': os.getenv('INSTAGRAM_ACCESS_TOKEN', '')
                },
                'tiktok': {
                    'app_id': os.getenv('TIKTOK_APP_ID', ''),
                    'app_secret': os.getenv('TIKTOK_APP_SECRET', ''),
                    'access_token': os.getenv('TIKTOK_ACCESS_TOKEN', '')
                },
                'twitter': {
                    'api_key': os.getenv('TWITTER_API_KEY', ''),
                    'api_secret': os.getenv('TWITTER_API_SECRET', ''),
                    'bearer_token': os.getenv('TWITTER_BEARER_TOKEN', '')
                },
                'youtube': {
                    'api_key': os.getenv('YOUTUBE_API_KEY', ''),
                    'client_id': os.getenv('YOUTUBE_CLIENT_ID', ''),
                    'client_secret': os.getenv('YOUTUBE_CLIENT_SECRET', '')
                },
                'reddit': {
                    'client_id': os.getenv('REDDIT_CLIENT_ID', ''),
                    'client_secret': os.getenv('REDDIT_CLIENT_SECRET', ''),
                    'user_agent': os.getenv('REDDIT_USER_AGENT', 'EDGLRD Analytics Bot 1.0')
                }
            }
        }
        
        # Initialize collectors
        self.collectors = {
            'instagram': InstagramCollector(self.config['api_auth']['instagram']),
            'tiktok': TikTokCollector(self.config['api_auth']['tiktok']),
            'twitter': TwitterCollector(self.config['api_auth']['twitter']),
            'youtube': YouTubeCollector(self.config['api_auth']['youtube']),
            'reddit': RedditCollector(self.config['api_auth']['reddit'])
        }
        
        # Initialize analyzers
        self.audience_analyzer = create_audience_analyzer('instagram')
        self.content_analyzer = ContentAnalyzer()
        self.engagement_analyzer = EngagementAnalyzer()
        self.journey_analyzer = ContentJourneyAnalyzer()
        self.predictive_analyzer = PredictiveAnalyzer()
        self.content_generator = ContentIdeaGenerator()
        
        # Initialize logger
        self.logger = logging.getLogger(__name__)
        
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file"""
        try:
            import yaml
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            return config
        except Exception as e:
            self.logger.error(f"Error loading config: {str(e)}")
            raise
            
    def collect_platform_data(self, platform: str, start_date: datetime, 
                            end_date: datetime) -> Dict[str, pd.DataFrame]:
        """Collect data from specified platform"""
        try:
            collector = self.collectors.get(platform.lower())
            if not collector:
                raise ValueError(f"Unsupported platform: {platform}")
                
            data = {
                'profile': collector.collect_profile_data(),
                'content': collector.collect_content_data(start_date, end_date),
                'engagement': collector.collect_engagement_data(),
                'audience': collector.collect_audience_data()
            }
            
            return data
        except Exception as e:
            self.logger.error(f"Error collecting {platform} data: {str(e)}")
            raise
            
    def analyze_platform_data(self, platform_data: Dict[str, pd.DataFrame]) -> Dict:
        """
        Run all analyses on collected platform data
        """
        results = {}
        
        try:
            # Structure data for predictive analysis
            analysis_data = {
                'engagement': pd.DataFrame(),
                'content': pd.DataFrame()
            }
            
            # Combine engagement metrics across platforms
            engagement_dfs = []
            content_dfs = []
            
            for platform, data in platform_data.items():
                if not data.empty:
                    # Add platform column
                    data['platform'] = platform
                    
                    # Split into engagement and content metrics
                    engagement_cols = ['followers', 'followers_delta', 'likes', 'comments', 'shares', 'saves', 'platform']
                    content_cols = ['post_id', 'post_type', 'likes', 'comments', 'shares', 'saves', 'platform']
                    
                    engagement_df = data[engagement_cols].copy()
                    content_df = data[content_cols].copy()
                    
                    engagement_dfs.append(engagement_df)
                    content_dfs.append(content_df)
            
            if engagement_dfs:
                analysis_data['engagement'] = pd.concat(engagement_dfs, ignore_index=True)
            if content_dfs:
                analysis_data['content'] = pd.concat(content_dfs, ignore_index=True)
            
            # Run analyses
            results['audience'] = self.audience_analyzer.analyze_audience(platform_data)
            results['content'] = self.content_analyzer.analyze_content(platform_data) 
            results['predictive'] = self.predictive_analyzer.get_predictive_insights(analysis_data)
            results['journey'] = self.journey_analyzer.analyze_content_journey(platform_data)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error analyzing platform data: {str(e)}")
            return results
            
    def generate_visualizations(self, analysis_results: Dict) -> Dict:
        """Generate visualizations for analysis results"""
        try:
            visualizations = {
                'demographics': self.dashboard.plot_audience_demographics(
                    analysis_results['audience_insights']
                ),
                'engagement': self.dashboard.plot_engagement_metrics(
                    analysis_results['engagement_metrics']
                ),
                'content': self.dashboard.plot_content_performance(
                    analysis_results['content_insights']
                )
            }
            
            return visualizations
        except Exception as e:
            self.logger.error(f"Error generating visualizations: {str(e)}")
            raise
            
    def generate_report(self, platform: str, start_date, end_date) -> dict:
        """Generate comprehensive analytics report with detailed metrics."""
        try:
            mock_data = {
                'analysis': {
                    'post_intelligence': {
                        'total_posts': 157,
                        'content_types': {
                            'image': 45,
                            'video': 62,
                            'carousel': 35,
                            'text': 15
                        },
                        'posting_times': {
                            'best_times': ['14:00', '18:30', '20:00'],
                            'timezone': 'EST',
                            'daily_distribution': {
                                'Monday': 22,
                                'Tuesday': 25,
                                'Wednesday': 28,
                                'Thursday': 24,
                                'Friday': 30,
                                'Saturday': 15,
                                'Sunday': 13
                            }
                        },
                        'creator_influence': {
                            'score': 8.5,
                            'reach_multiplier': 2.3,
                            'authority_score': 85
                        },
                        'url_performance': {
                            'click_through_rate': 3.2,
                            'conversion_rate': 1.8,
                            'bounce_rate': 45
                        },
                        'hashtag_metrics': {
                            'brand_hashtags': {
                                '#brandname': {'reach': 25000, 'engagement': 1200},
                                '#campaign2023': {'reach': 15000, 'engagement': 800}
                            }
                        }
                    },
                    'engagement_analytics': {
                        'real_time_metrics': {
                            'current_engagement_rate': 4.8,
                            'hourly_trend': [4.2, 4.5, 4.8, 5.0, 4.9],
                            'live_interaction_count': 256
                        },
                        'true_reach': {
                            'engagement_to_follower': 0.085,
                            'actual_reach_percentage': 28.5,
                            'quality_score': 8.2
                        },
                        'viral_metrics': {
                            'coefficient': 1.8,
                            'spread_rate': 'High',
                            'viral_potential_score': 85
                        },
                        'sentiment_analysis': {
                            'positive': 65,
                            'neutral': 25,
                            'negative': 10,
                            'trending_topics': ['product', 'service', 'support']
                        },
                        'content_value': {
                            'save_ratio': 0.15,
                            'share_ratio': 0.08,
                            'value_score': 8.5
                        }
                    },
                    'audience_insights': {
                        'demographics': {
                            'age_groups': {
                                '18-24': 15,
                                '25-34': 35,
                                '35-44': 25,
                                '45-54': 15,
                                '55+': 10
                            },
                            'gender': {
                                'Female': 58,
                                'Male': 40,
                                'Other': 2
                            },
                            'locations': {
                                'United States': 45,
                                'United Kingdom': 15,
                                'Canada': 12,
                                'Australia': 8,
                                'Others': 20
                            }
                        },
                        'engagement_windows': {
                            'peak_hours': ['09:00-11:00', '14:00-16:00', '19:00-21:00'],
                            'best_days': ['Wednesday', 'Thursday', 'Sunday']
                        },
                        'interest_analysis': {
                            'clusters': ['Technology', 'Fashion', 'Lifestyle'],
                            'trending_topics': ['AI', 'Sustainability', 'Wellness'],
                            'affinity_scores': {'Tech': 0.8, 'Fashion': 0.6}
                        },
                        'audience_loyalty': {
                            'return_rate': 0.65,
                            'engagement_frequency': 'High',
                            'loyalty_score': 8.2
                        }
                    },
                    'content_performance': {
                        'ai_categorization': {
                            'top_categories': ['Educational', 'Promotional', 'Entertainment'],
                            'performance_by_category': {
                                'Educational': 8.5,
                                'Promotional': 7.2,
                                'Entertainment': 8.8
                            }
                        },
                        'competitive_analysis': {
                            'market_position': 3,
                            'engagement_rank': 2,
                            'growth_rank': 4
                        },
                        'predictive_scores': {
                            'next_post_prediction': 8.2,
                            'trend_alignment': 0.85,
                            'viral_potential': 0.75
                        },
                        'content_longevity': {
                            'average_lifespan': '48 hours',
                            'peak_performance': '4-6 hours',
                            'decay_rate': 'Low'
                        }
                    },
                    'strategic_metrics': {
                        'roi_analysis': {
                            'overall_roi': 285,
                            'by_content_type': {
                                'video': 320,
                                'image': 245,
                                'carousel': 295
                            }
                        },
                        'trend_forecast': {
                            '7_day': {'engagement': '+5%', 'followers': '+2.5%'},
                            '30_day': {'engagement': '+15%', 'followers': '+8%'},
                            '90_day': {'engagement': '+35%', 'followers': '+20%'}
                        },
                        'posting_schedule': {
                            'optimal_times': ['09:30', '14:00', '19:30'],
                            'frequency': 'Daily',
                            'best_content_types': ['Video', 'Carousel', 'Image']
                        },
                        'campaign_impact': {
                            'overall_score': 8.5,
                            'reach_impact': 'High',
                            'engagement_impact': 'Very High'
                        },
                        'brand_consistency': {
                            'voice_score': 9.2,
                            'visual_consistency': 8.8,
                            'message_alignment': 8.5
                        }
                    }
                }
            }
            return mock_data
        except Exception as e:
            self.logger.error(f"Error generating report: {str(e)}")
            raise

    def generate_report(self, platform: str, start_date: datetime,
                       end_date: datetime) -> Dict:
        """Generate comprehensive analytics report"""
        try:
            # Collect data
            platform_data = self.collect_platform_data(platform, start_date, end_date)
            
            # Analyze data
            analysis_results = self.analyze_platform_data(platform_data)
            
            # Generate visualizations
            visualizations = self.generate_visualizations(analysis_results)
            
            report = {
                'platform': platform,
                'date_range': {'start': start_date, 'end': end_date},
                'analysis': analysis_results,
                'visualizations': visualizations
            }
            
            return report
        except Exception as e:
            self.logger.error(f"Error generating report: {str(e)}")
            raise

    def generate_content_ideas(
        self,
        platform_data: Dict,
        content_types: List[str] = None,
        num_ideas: int = 5
    ) -> Dict[str, List[Dict]]:
        """
        Generate content ideas based on analyzed data
        
        Args:
            platform_data: Dict containing analyzed data from different platforms
            content_types: List of content types to generate ideas for
            num_ideas: Number of ideas to generate per platform
            
        Returns:
            Dict mapping platform names to lists of content ideas
        """
        try:
            # Set default content types if none provided
            if content_types is None:
                content_types = ['image', 'video', 'text', 'story', 'reel', 'carousel']
            
            # Convert to lowercase for consistency
            content_types = [ct.lower() for ct in content_types]
            
            # Generate ideas for each platform
            ideas = {}
            for platform, data in platform_data.items():
                platform_analysis = {
                    'top_performing_posts': self.get_top_posts(platform),
                    'engagement_patterns': self.analyze_engagement_patterns(platform),
                    'audience_insights': self.get_audience_insights(platform)
                }
                
                # Filter ideas by content type
                all_ideas = self.content_generator.generate_ideas(
                    {platform: platform_analysis}
                )
                filtered_ideas = [
                    idea for idea in all_ideas
                    if idea['content_type'].lower() in content_types
                ]
                
                # Sort by predicted impact and take top N
                filtered_ideas.sort(key=lambda x: x['predicted_impact'], reverse=True)
                ideas[platform] = filtered_ideas[:num_ideas]
            
            return ideas
            
        except Exception as e:
            self.logger.error(f"Error generating content ideas: {str(e)}")
            return {}
            
    def get_combined_performance_insights(self, platform_data: Dict) -> Dict:
        """
        Combine performance insights across platforms
        
        Args:
            platform_data: Dict containing data from different platforms
            
        Returns:
            Dict containing combined performance insights
        """
        try:
            combined_insights = {
                'element_performance': defaultdict(list),
                'peak_times': defaultdict(list),
                'content_themes': defaultdict(list)
            }
            
            # Combine insights from each platform
            for platform, data in platform_data.items():
                patterns = data.get('engagement_patterns', {})
                
                # Combine element performance
                for element, score in patterns.get('element_performance', {}).items():
                    combined_insights['element_performance'][element].append(score)
                
                # Combine peak times
                for hour, score in patterns.get('peak_times', []):
                    combined_insights['peak_times'][hour].append(score)
                
                # Combine content themes
                for theme, score in patterns.get('content_themes', {}).items():
                    combined_insights['content_themes'][theme].append(score)
            
            # Average out the scores
            return {
                'element_performance': {
                    element: np.mean(scores)
                    for element, scores in combined_insights['element_performance'].items()
                },
                'peak_times': sorted(
                    [
                        (hour, np.mean(scores))
                        for hour, scores in combined_insights['peak_times'].items()
                    ],
                    key=lambda x: x[1],
                    reverse=True
                ),
                'content_themes': {
                    theme: np.mean(scores)
                    for theme, scores in combined_insights['content_themes'].items()
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error combining performance insights: {str(e)}")
            return {}
            
    def get_top_posts(self, platform: str, timeframe: str = '7d') -> List[Dict]:
        """Get top performing posts for a platform"""
        try:
            data = self.collectors[platform].get_posts(timeframe)
            if isinstance(data, pd.DataFrame) and not data.empty:
                # Sort by engagement score
                data['engagement_score'] = data.apply(lambda x: calculate_engagement_score(x), axis=1)
                return data.nlargest(10, 'engagement_score').to_dict('records')
            return []
        except Exception as e:
            self.logger.error(f"Error getting top posts: {str(e)}")
            return []

    def analyze_engagement_patterns(self, platform: str, timeframe: str = '30d') -> Dict:
        """Analyze engagement patterns"""
        try:
            data = self.collectors[platform].get_posts(timeframe)
            if isinstance(data, pd.DataFrame) and not data.empty:
                patterns = self.engagement_analyzer.analyze(data)
                return patterns
            return {}
        except Exception as e:
            self.logger.error(f"Error analyzing engagement patterns: {str(e)}")
            return {}

    def get_audience_insights(self, platform: str) -> Dict:
        """Get audience insights for a platform"""
        try:
            data = self.collectors[platform].get_audience_data()
            if isinstance(data, dict):
                return self.audience_analyzer.analyze(data)
            return {}
        except Exception as e:
            self.logger.error(f"Error getting audience insights: {str(e)}")
            return {}
