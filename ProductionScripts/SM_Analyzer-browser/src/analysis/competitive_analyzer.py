"""
Competitive Analysis Module
Analyzes market position and competitive landscape across social media platforms
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import logging
from datetime import datetime
from textblob import TextBlob

logger = logging.getLogger(__name__)

class CompetitiveAnalyzer:
    def analyze_market_position(self, our_content: pd.DataFrame, 
                              competitor_content: pd.DataFrame) -> Dict:
        """Analyze competitive position and identify opportunities"""
        return {
            'market_gaps': self._identify_content_gaps(our_content, competitor_content),
            'differentiation_opportunities': self._analyze_differentiation(our_content, competitor_content),
            'trend_adaptation': self._analyze_trend_adoption(our_content, competitor_content),
            'engagement_comparison': self._compare_engagement_metrics(our_content, competitor_content),
            'content_strategy_recommendations': self._generate_strategy_recommendations(our_content, competitor_content)
        }

    def _identify_content_gaps(self, our_content: pd.DataFrame, 
                             competitor_content: pd.DataFrame) -> Dict:
        """Identify content types and topics that competitors are missing"""
        try:
            if competitor_content.empty:
                return {
                    'untapped_topics': [],
                    'content_opportunities': [],
                    'timing_gaps': []
                }

            # Analyze content types and topics
            our_topics = self._extract_topics(our_content)
            competitor_topics = self._extract_topics(competitor_content)
            
            return {
                'untapped_topics': list(set(our_topics) - set(competitor_topics)),
                'content_opportunities': self._identify_opportunities(our_content, competitor_content),
                'timing_gaps': self._analyze_posting_gaps(our_content, competitor_content)
            }
        except Exception as e:
            logger.error(f"Error identifying content gaps: {e}")
            return {}

    def _analyze_differentiation(self, our_content: pd.DataFrame, 
                               competitor_content: pd.DataFrame) -> Dict:
        """Analyze areas where we can differentiate from competitors"""
        try:
            if competitor_content.empty:
                return {
                    'unique_strengths': [],
                    'tone_differences': {},
                    'engagement_advantages': []
                }

            return {
                'unique_strengths': self._identify_unique_strengths(our_content),
                'tone_differences': self._analyze_tone_differences(our_content, competitor_content),
                'engagement_advantages': self._identify_engagement_advantages(our_content, competitor_content)
            }
        except Exception as e:
            logger.error(f"Error analyzing differentiation: {e}")
            return {}

    def _analyze_trend_adoption(self, our_content: pd.DataFrame, 
                              competitor_content: pd.DataFrame) -> Dict:
        """Analyze how quickly we and competitors adopt trends"""
        try:
            if competitor_content.empty:
                return {
                    'trend_responsiveness': 0.0,
                    'trending_topics': [],
                    'missed_opportunities': []
                }

            return {
                'trend_responsiveness': self._calculate_trend_responsiveness(our_content, competitor_content),
                'trending_topics': self._identify_trending_topics(competitor_content),
                'missed_opportunities': self._identify_missed_trends(our_content, competitor_content)
            }
        except Exception as e:
            logger.error(f"Error analyzing trend adoption: {e}")
            return {}

    def _compare_engagement_metrics(self, our_content: pd.DataFrame, 
                                  competitor_content: pd.DataFrame) -> Dict:
        """Compare engagement metrics between our content and competitors"""
        try:
            if competitor_content.empty:
                return {
                    'engagement_rate': self._calculate_engagement_rate(our_content),
                    'comparative_metrics': {},
                    'top_performing_content': self._identify_top_content(our_content)
                }

            return {
                'engagement_rate': self._calculate_engagement_rate(our_content),
                'comparative_metrics': self._calculate_comparative_metrics(our_content, competitor_content),
                'top_performing_content': self._identify_top_content(our_content)
            }
        except Exception as e:
            logger.error(f"Error comparing engagement metrics: {e}")
            return {}

    def _generate_strategy_recommendations(self, our_content: pd.DataFrame, 
                                        competitor_content: pd.DataFrame) -> List[Dict]:
        """Generate strategic recommendations based on competitive analysis"""
        try:
            if competitor_content.empty:
                return [{
                    'type': 'baseline',
                    'recommendation': 'Establish baseline metrics and continue monitoring competitor activity',
                    'priority': 'medium'
                }]

            recommendations = []
            
            # Analyze engagement gaps
            engagement_gaps = self._identify_engagement_gaps(our_content, competitor_content)
            if engagement_gaps:
                recommendations.append({
                    'type': 'engagement',
                    'recommendation': f'Focus on improving engagement in: {", ".join(engagement_gaps)}',
                    'priority': 'high'
                })
            
            # Analyze content opportunities
            content_gaps = self._identify_content_gaps(our_content, competitor_content)
            if content_gaps:
                recommendations.append({
                    'type': 'content',
                    'recommendation': 'Explore untapped content opportunities',
                    'details': content_gaps,
                    'priority': 'medium'
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating strategy recommendations: {e}")
            return []

    def _extract_topics(self, content_df: pd.DataFrame) -> List[str]:
        """Extract main topics from content"""
        try:
            # Simple topic extraction based on common words
            if 'text' not in content_df.columns:
                return []
                
            text_content = ' '.join(content_df['text'].fillna('').astype(str))
            words = text_content.lower().split()
            # Remove common words and get unique topics
            common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
            topics = [w for w in words if w not in common_words and len(w) > 3]
            return list(set(topics))
        except Exception as e:
            logger.error(f"Error extracting topics: {e}")

    def _calculate_engagement_rate(self, content_df: pd.DataFrame) -> float:
        """Calculate overall engagement rate"""
        try:
            if content_df.empty:
                return 0.0
            
            engagement_metrics = ['score', 'num_comments']
            available_metrics = [m for m in engagement_metrics if m in content_df.columns]
            
            if not available_metrics:
                return 0.0
            
            total_engagement = content_df[available_metrics].sum().sum()
            return total_engagement / len(content_df) if len(content_df) > 0 else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating engagement rate: {e}")
            return 0.0

    def _calculate_comparative_metrics(self, our_content: pd.DataFrame, competitor_content: pd.DataFrame) -> Dict:
        """Calculate comparative engagement metrics"""
        try:
            our_metrics = {
                'engagement_rate': self._calculate_engagement_rate(our_content),
                'avg_score': our_content['score'].mean() if 'score' in our_content.columns else 0.0,
                'avg_comments': our_content['num_comments'].mean() if 'num_comments' in our_content.columns else 0.0
            }
            
            competitor_metrics = {
                'engagement_rate': self._calculate_engagement_rate(competitor_content),
                'avg_score': competitor_content['score'].mean() if 'score' in competitor_content.columns else 0.0,
                'avg_comments': competitor_content['num_comments'].mean() if 'num_comments' in competitor_content.columns else 0.0
            }
            
            return {
                'our_metrics': our_metrics,
                'competitor_metrics': competitor_metrics,
                'relative_performance': {
                    metric: (our_metrics[metric] / competitor_metrics[metric] if competitor_metrics[metric] != 0 else 1.0)
                    for metric in our_metrics.keys()
                }
            }
        except Exception as e:
            logger.error(f"Error calculating comparative metrics: {e}")
            return {}

    def _identify_top_content(self, content_df: pd.DataFrame) -> List[Dict]:
        """Identify top performing content"""
        try:
            if content_df.empty:
                return []
            
            # Calculate engagement score
            content_df['engagement_score'] = (
                content_df['score'].fillna(0) + 
                (content_df['num_comments'].fillna(0) * 2)  # Weight comments more heavily
            )
            
            # Get top 5 posts
            top_posts = content_df.nlargest(5, 'engagement_score')
            
            return [{
                'id': row['id'],
                'text': row['text'] if 'text' in row else '',
                'score': row['score'] if 'score' in row else 0,
                'num_comments': row['num_comments'] if 'num_comments' in row else 0,
                'engagement_score': row['engagement_score']
            } for _, row in top_posts.iterrows()]
            
        except Exception as e:
            logger.error(f"Error identifying top content: {e}")
            return []

class CompetitiveAnalyzer(BaseAnalyzer):
    """Analyzer for competitive metrics and benchmarking"""

    def __init__(self):
        """Initialize competitive analyzer"""
        super().__init__()
        self.logger = logging.getLogger(__name__)

    def analyze_share_of_voice(self, brand_data: Dict, competitor_data: List[Dict]) -> Dict:
        """
        Analyze share of voice across social platforms
        
        Args:
            brand_data: Dict containing brand metrics
            competitor_data: List of competitor metrics
            
        Returns:
            Dict containing SOV analysis
        """
        try:
            sov_metrics = {
                'overall_sov': self._calculate_overall_sov(brand_data, competitor_data),
                'platform_sov': self._calculate_platform_sov(brand_data, competitor_data),
                'sentiment_analysis': self._analyze_sentiment_distribution(brand_data, competitor_data),
                'topic_share': self._analyze_topic_distribution(brand_data, competitor_data),
                'trend_analysis': self._analyze_sov_trends(brand_data, competitor_data)
            }
            return sov_metrics
        except Exception as e:
            self.logger.error(f"Error analyzing share of voice: {str(e)}")
            return {}

    def analyze_benchmarks(self, brand_metrics: Dict, industry_data: Dict) -> Dict:
        """
        Analyze performance benchmarks against industry standards
        
        Args:
            brand_metrics: Dict containing brand performance metrics
            industry_data: Dict containing industry benchmarks
            
        Returns:
            Dict containing benchmark analysis
        """
        try:
            benchmark_metrics = {
                'performance_benchmarks': self._calculate_performance_benchmarks(brand_metrics, industry_data),
                'growth_comparison': self._analyze_growth_rates(brand_metrics, industry_data),
                'engagement_benchmarks': self._calculate_engagement_benchmarks(brand_metrics, industry_data),
                'content_effectiveness': self._analyze_content_effectiveness(brand_metrics, industry_data),
                'audience_quality': self._analyze_audience_quality(brand_metrics, industry_data)
            }
            return benchmark_metrics
        except Exception as e:
            self.logger.error(f"Error analyzing benchmarks: {str(e)}")
            return {}

    def analyze_trends(self, platform_data: Dict) -> Dict:
        """
        Analyze industry and platform trends
        
        Args:
            platform_data: Dict containing platform trend data
            
        Returns:
            Dict containing trend analysis
        """
        try:
            trend_metrics = {
                'trending_topics': self._analyze_trending_topics(platform_data),
                'trend_velocity': self._calculate_trend_velocity(platform_data),
                'trend_relevance': self._analyze_trend_relevance(platform_data),
                'opportunity_score': self._calculate_opportunity_score(platform_data),
                'trend_forecasting': self._forecast_trend_evolution(platform_data)
            }
            return trend_metrics
        except Exception as e:
            self.logger.error(f"Error analyzing trends: {str(e)}")
            return {}

    def _calculate_overall_sov(self, brand_data: Dict, competitor_data: List[Dict]) -> Dict:
        """Calculate overall share of voice metrics"""
        try:
            # Aggregate mentions and engagement
            brand_mentions = sum(brand_data.get('mentions', {}).values())
            brand_engagement = sum(brand_data.get('engagement', {}).values())
            
            total_mentions = brand_mentions
            total_engagement = brand_engagement
            competitor_metrics = []
            
            for competitor in competitor_data:
                comp_mentions = sum(competitor.get('mentions', {}).values())
                comp_engagement = sum(competitor.get('engagement', {}).values())
                total_mentions += comp_mentions
                total_engagement += comp_engagement
                
                competitor_metrics.append({
                    'name': competitor.get('name', 'Unknown'),
                    'mention_share': comp_mentions / total_mentions if total_mentions > 0 else 0,
                    'engagement_share': comp_engagement / total_engagement if total_engagement > 0 else 0
                })
            
            return {
                'brand_sov': {
                    'mention_share': brand_mentions / total_mentions if total_mentions > 0 else 0,
                    'engagement_share': brand_engagement / total_engagement if total_engagement > 0 else 0
                },
                'competitor_sov': competitor_metrics,
                'total_market_volume': {
                    'mentions': total_mentions,
                    'engagement': total_engagement
                }
            }
        except Exception as e:
            self.logger.error(f"Error calculating overall SOV: {str(e)}")
            return {}

    def _analyze_trending_topics(self, platform_data: Dict) -> Dict:
        """Analyze trending topics and their characteristics"""
        try:
            topics = platform_data.get('trending_topics', [])
            if not topics:
                return {}
            
            # Analyze topic metrics
            topic_analysis = []
            for topic in topics:
                analysis = {
                    'topic': topic['name'],
                    'volume': topic.get('volume', 0),
                    'growth_rate': self._calculate_growth_rate(topic.get('history', [])),
                    'sentiment': self._analyze_topic_sentiment(topic.get('sentiment', {})),
                    'demographic_reach': self._analyze_demographic_reach(topic.get('demographics', {})),
                    'related_topics': self._find_related_topics(topic, topics)
                }
                topic_analysis.append(analysis)
            
            # Sort by volume and growth rate
            sorted_topics = sorted(
                topic_analysis,
                key=lambda x: (x['volume'], x['growth_rate']),
                reverse=True
            )
            
            return {
                'top_trends': sorted_topics[:10],
                'trend_categories': self._categorize_trends(sorted_topics),
                'trend_correlations': self._analyze_trend_correlations(sorted_topics),
                'emerging_trends': self._identify_emerging_trends(sorted_topics)
            }
        except Exception as e:
            self.logger.error(f"Error analyzing trending topics: {str(e)}")
            return {}

    def _calculate_trend_velocity(self, platform_data: Dict) -> Dict:
        """Calculate velocity and acceleration of trends"""
        try:
            trend_history = platform_data.get('trend_history', [])
            if not trend_history:
                return {}
            
            # Convert to pandas DataFrame for time series analysis
            df = pd.DataFrame(trend_history)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df.set_index('timestamp', inplace=True)
            
            # Calculate velocity (rate of change)
            df['velocity'] = df['volume'].diff() / df.index.to_series().diff().dt.total_seconds()
            
            # Calculate acceleration (change in velocity)
            df['acceleration'] = df['velocity'].diff() / df.index.to_series().diff().dt.total_seconds()
            
            return {
                'current_velocity': float(df['velocity'].iloc[-1]),
                'average_velocity': float(df['velocity'].mean()),
                'acceleration': float(df['acceleration'].iloc[-1]),
                'velocity_trend': self._analyze_velocity_trend(df),
                'momentum_score': self._calculate_momentum_score(df)
            }
        except Exception as e:
            self.logger.error(f"Error calculating trend velocity: {str(e)}")
            return {}

    def _forecast_trend_evolution(self, platform_data: Dict) -> Dict:
        """Forecast trend evolution using historical data"""
        try:
            trend_history = platform_data.get('trend_history', [])
            if not trend_history:
                return {}
            
            # Prepare time series data
            df = pd.DataFrame(trend_history)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df.set_index('timestamp', inplace=True)
            
            # Calculate trend components
            trend_components = {
                'seasonal_pattern': self._identify_seasonal_pattern(df),
                'growth_trajectory': self._calculate_growth_trajectory(df),
                'cycle_length': self._estimate_cycle_length(df),
                'stability_score': self._calculate_stability_score(df)
            }
            
            # Generate forecast
            forecast = {
                'short_term': self._generate_short_term_forecast(df),
                'long_term': self._generate_long_term_forecast(df),
                'confidence_intervals': self._calculate_forecast_confidence(df),
                'influencing_factors': self._identify_influencing_factors(df)
            }
            
            return {
                'trend_components': trend_components,
                'forecast': forecast,
                'reliability_score': self._calculate_forecast_reliability(df)
            }
        except Exception as e:
            self.logger.error(f"Error forecasting trend evolution: {str(e)}")
            return {}
