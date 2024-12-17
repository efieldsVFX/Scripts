from typing import Dict, List
import pandas as pd
from textblob import TextBlob
import numpy as np
import logging
import re

logger = logging.getLogger(__name__)

class BrandIdentityAnalyzer:
    def __init__(self, brand_values: Dict[str, float], target_audience: List[str]):
        self.brand_values = brand_values
        self.target_audience = target_audience
        
    def analyze_content_alignment(self, content_df: pd.DataFrame) -> Dict:
        """Analyze how well content aligns with brand values and audience"""
        alignment_metrics = {
            'brand_value_alignment': self._calculate_value_alignment(content_df),
            'audience_engagement': self._analyze_audience_engagement(content_df),
            'tone_consistency': self._analyze_tone_consistency(content_df),
            'trending_relevance': self._calculate_trend_alignment(content_df)
        }
        
        return alignment_metrics
    
    def generate_content_recommendations(self, analysis_results: Dict) -> List[Dict]:
        """Generate content recommendations that align with brand identity"""
        recommendations = []
        
        # Identify successful content patterns that align with brand values
        successful_patterns = self._extract_successful_patterns(analysis_results)
        
        # Generate recommendations for each platform
        for platform, patterns in successful_patterns.items():
            platform_recs = {
                'platform': platform,
                'content_types': self._filter_brand_aligned_content(patterns['content_types']),
                'tone_suggestions': self._generate_tone_suggestions(patterns['sentiment']),
                'optimal_posting_times': patterns['timing'],
                'recommended_hashtags': self._filter_relevant_hashtags(patterns['hashtags']),
                'engagement_strategies': self._generate_engagement_strategies(patterns)
            }
            recommendations.append(platform_recs)
            
        return recommendations

    def _calculate_value_alignment(self, content_df: pd.DataFrame) -> float:
        """Calculate how well content aligns with brand values"""
        try:
            # Combine all text content for analysis
            text_content = ' '.join(content_df['text'].fillna('').astype(str))
            
            # Calculate alignment scores for each brand value
            alignment_scores = []
            for value, importance in self.brand_values.items():
                value_score = self._calculate_single_value_alignment(text_content, value)
                alignment_scores.append(value_score * importance)
            
            return sum(alignment_scores) / len(alignment_scores) if alignment_scores else 0.0
            
        except Exception as e:
            logger.error(f"Error in value alignment calculation: {e}")
            return 0.0

    def _calculate_single_value_alignment(self, text: str, value: str) -> float:
        """Calculate alignment with a specific brand value"""
        try:
            # Value-specific keywords
            value_words = {
                'innovation': ['new', 'innovative', 'cutting-edge', 'advanced'],
                'reliability': ['reliable', 'consistent', 'stable', 'trusted'],
                'sustainability': ['sustainable', 'green', 'eco-friendly', 'environmental'],
                'quality': ['quality', 'premium', 'excellent', 'superior'],
                'customer_focus': ['customer', 'service', 'support', 'satisfaction']
            }
            
            relevant_words = value_words.get(value.lower(), [value.lower()])
            text = text.lower()
            
            # Word presence score
            word_matches = sum(1 for word in relevant_words if word in text)
            word_score = min(word_matches / len(relevant_words), 1.0)
            
            # Sentiment score
            sentiment_score = (TextBlob(text).sentiment.polarity + 1) / 2
            
            # Combined score
            return 0.7 * word_score + 0.3 * sentiment_score
            
        except Exception as e:
            logger.error(f"Error in single value alignment calculation: {e}")
            return 0.0

    def _analyze_audience_engagement(self, content_df: pd.DataFrame) -> Dict:
        """Analyze audience engagement metrics"""
        try:
            return {
                'engagement_rate': content_df['engagement'].mean() if 'engagement' in content_df else 0.0,
                'audience_reach': len(content_df),
                'interaction_quality': self._calculate_interaction_quality(content_df)
            }
        except Exception as e:
            logger.error(f"Error analyzing audience engagement: {e}")
            return {}

    def _analyze_tone_consistency(self, content_df: pd.DataFrame) -> Dict:
        """Analyze consistency of content tone"""
        try:
            sentiments = [TextBlob(str(text)).sentiment.polarity 
                         for text in content_df['text'].fillna('')]
            return {
                'average_sentiment': sum(sentiments) / len(sentiments) if sentiments else 0.0,
                'sentiment_variance': np.var(sentiments) if sentiments else 0.0
            }
        except Exception as e:
            logger.error(f"Error analyzing tone consistency: {e}")
            return {}

    def _calculate_trend_alignment(self, content_df: pd.DataFrame) -> float:
        """Calculate how well content aligns with current trends"""
        try:
            # Placeholder for trend alignment calculation
            return 0.5  # Default middle value
        except Exception as e:
            logger.error(f"Error calculating trend alignment: {e}")
            return 0.0

    def _calculate_interaction_quality(self, content_df: pd.DataFrame) -> float:
        """Calculate the quality of interactions based on engagement metrics"""
        try:
            # Calculate interaction quality based on available metrics
            quality_metrics = {
                'score_weight': 0.4,
                'comment_weight': 0.6
            }
            
            # Calculate average score
            avg_score = content_df['score'].mean() if 'score' in content_df else 0.0
            
            # Calculate average comments (if available)
            avg_comments = content_df['num_comments'].mean() if 'num_comments' in content_df else 0.0
            
            # Normalize scores (assuming typical Reddit metrics)
            normalized_score = min(avg_score / 100, 1.0)
            normalized_comments = min(avg_comments / 50, 1.0)
            
            # Calculate weighted quality score
            quality_score = (
                normalized_score * quality_metrics['score_weight'] +
                normalized_comments * quality_metrics['comment_weight']
            )
            
            return quality_score
            
        except Exception as e:
            logger.error(f"Error calculating interaction quality: {e}")
            return 0.0

    def _extract_successful_patterns(self, analysis_results: Dict) -> Dict:
        """Extract patterns from successful content"""
        try:
            platform = analysis_results.get('platform', '')
            content_data = analysis_results.get('data', pd.DataFrame())
            
            if content_data.empty:
                return {
                    platform: {
                        'content_types': [],
                        'sentiment': {'positive': 0, 'neutral': 0, 'negative': 0},
                        'timing': [],
                        'hashtags': []
                    }
                }
            
            # Get top performing content
            top_content = content_data.nlargest(10, 'score') if 'score' in content_data.columns else content_data.head(10)
            
            # Extract patterns
            patterns = {
                platform: {
                    'content_types': self._identify_content_types(top_content),
                    'sentiment': self._analyze_sentiment_distribution(top_content),
                    'timing': self._extract_posting_times(top_content),
                    'hashtags': self._extract_hashtags(top_content)
                }
            }
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error extracting successful patterns: {e}")
            return {}

    def _identify_content_types(self, content_df: pd.DataFrame) -> List[str]:
        """Identify types of content that perform well"""
        try:
            content_types = []
            if 'text' in content_df.columns:
                # Updated regex patterns to avoid warning
                has_links = content_df['text'].str.contains(r'https?://\S+', case=False)
                has_images = content_df['text'].str.contains(r'[^\s]+\.(jpg|jpeg|png|gif)\b', case=False, regex=True)
                
                if has_links.any():
                    content_types.append('link_posts')
                if has_images.any():
                    content_types.append('image_posts')
                if not (has_links.any() or has_images.any()):
                    content_types.append('text_posts')
                    
            return content_types
            
        except Exception as e:
            logger.error(f"Error identifying content types: {e}")
            return []

    def _analyze_sentiment_distribution(self, content_df: pd.DataFrame) -> Dict:
        """Analyze sentiment distribution in successful content"""
        try:
            sentiments = {'positive': 0, 'neutral': 0, 'negative': 0}
            
            if 'text' in content_df.columns:
                for text in content_df['text'].fillna(''):
                    sentiment = TextBlob(str(text)).sentiment.polarity
                    if sentiment > 0.1:
                        sentiments['positive'] += 1
                    elif sentiment < -0.1:
                        sentiments['negative'] += 1
                    else:
                        sentiments['neutral'] += 1
                        
            total = sum(sentiments.values()) or 1  # Avoid division by zero
            return {k: v/total for k, v in sentiments.items()}
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment distribution: {e}")
            return {'positive': 0, 'neutral': 1, 'negative': 0}

    def _extract_posting_times(self, content_df: pd.DataFrame) -> List[str]:
        """Extract optimal posting times"""
        try:
            if 'created_utc' not in content_df.columns:
                return []
                
            # Convert UTC timestamps to datetime
            times = pd.to_datetime(content_df['created_utc'], unit='s')
            
            # Get hour distribution of successful posts
            hour_counts = times.dt.hour.value_counts()
            
            # Return top 3 posting hours
            return [f"{hour:02d}:00" for hour in hour_counts.head(3).index]
            
        except Exception as e:
            logger.error(f"Error extracting posting times: {e}")
            return []

    def _extract_hashtags(self, content_df: pd.DataFrame) -> List[str]:
        """Extract commonly used hashtags"""
        try:
            hashtags = []
            if 'text' in content_df.columns:
                for text in content_df['text'].fillna(''):
                    # Extract hashtags using regex
                    found_tags = re.findall(r'#(\w+)', str(text))
                    hashtags.extend(found_tags)
                    
            # Return top 5 most common hashtags
            from collections import Counter
            return [tag for tag, _ in Counter(hashtags).most_common(5)]
            
        except Exception as e:
            logger.error(f"Error extracting hashtags: {e}")
            return []

    def _filter_brand_aligned_content(self, content_types: List[str]) -> List[str]:
        """Filter content types that align with brand values"""
        try:
            # Simple filtering based on brand values
            aligned_types = []
            for content_type in content_types:
                # Add logic to filter based on brand values
                aligned_types.append(content_type)
            return aligned_types
        except Exception as e:
            logger.error(f"Error filtering brand aligned content: {e}")
            return []

    def _generate_tone_suggestions(self, sentiment_distribution: Dict) -> List[str]:
        """Generate tone suggestions based on successful content"""
        try:
            suggestions = []
            if sentiment_distribution['positive'] > 0.6:
                suggestions.append("Maintain positive, upbeat tone")
            elif sentiment_distribution['neutral'] > 0.6:
                suggestions.append("Focus on informative, balanced content")
            return suggestions
        except Exception as e:
            logger.error(f"Error generating tone suggestions: {e}")
            return []

    def _generate_engagement_strategies(self, patterns: Dict) -> List[str]:
        """Generate engagement strategies based on content patterns"""
        try:
            strategies = []
            
            # Add timing-based strategies
            if patterns.get('timing'):
                strategies.append(f"Post during peak engagement hours: {', '.join(patterns['timing'])}")
            
            # Add content type strategies
            if patterns.get('content_types'):
                strategies.append(f"Focus on {', '.join(patterns['content_types'])} content")
            
            # Add sentiment-based strategies
            sentiment = patterns.get('sentiment', {})
            if sentiment.get('positive', 0) > 0.4:
                strategies.append("Maintain positive tone in content")
            elif sentiment.get('neutral', 0) > 0.4:
                strategies.append("Use balanced, informative tone")
            
            # Add hashtag strategies
            if patterns.get('hashtags'):
                strategies.append(f"Include relevant hashtags: {', '.join(patterns['hashtags'][:3])}")
            
            return strategies
            
        except Exception as e:
            logger.error(f"Error generating engagement strategies: {e}")
            return []

    def _filter_relevant_hashtags(self, hashtags: List[str]) -> List[str]:
        """Filter hashtags based on brand relevance and values"""
        try:
            if not hashtags:
                return []

            # Create a set of relevant keywords based on brand values
            relevant_keywords = set()
            value_keywords = {
                'innovation': {'new', 'tech', 'innovation', 'future'},
                'reliability': {'reliable', 'trusted', 'quality'},
                'sustainability': {'sustainable', 'green', 'eco', 'environment'},
                'quality': {'premium', 'quality', 'best'},
                'customer_focus': {'customer', 'service', 'support'}
            }
            
            # Add all value-related keywords to the relevant set
            for value in self.brand_values:
                if value.lower() in value_keywords:
                    relevant_keywords.update(value_keywords[value.lower()])
            
            # Filter hashtags based on relevance
            filtered_hashtags = []
            for hashtag in hashtags:
                # Check if hashtag contains any relevant keywords
                hashtag_lower = hashtag.lower()
                if any(keyword in hashtag_lower for keyword in relevant_keywords):
                    filtered_hashtags.append(hashtag)
                # Include hashtags that match target audience
                elif any(audience_term.lower() in hashtag_lower 
                        for audience_term in self.target_audience):
                    filtered_hashtags.append(hashtag)
            
            # Return filtered hashtags, or original list if all were filtered out
            return filtered_hashtags if filtered_hashtags else hashtags[:3]
            
        except Exception as e:
            logger.error(f"Error filtering relevant hashtags: {e}")
            return hashtags[:3]  # Return top 3 original hashtags if filtering fails
