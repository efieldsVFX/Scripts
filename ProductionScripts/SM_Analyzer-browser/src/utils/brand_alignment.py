"""
Brand Alignment Manager
Handles content validation and guideline generation based on brand values
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import logging
from textblob import TextBlob
from datetime import datetime

logger = logging.getLogger(__name__)

class BrandAlignmentManager:
    def __init__(self, brand_values: Dict[str, float], content_guidelines: Dict):
        self.brand_values = brand_values
        self.content_guidelines = content_guidelines
        
    def get_brand_values(self) -> Dict[str, float]:
        """Get current brand values"""
        return self.brand_values
        
    def get_target_audience(self) -> List[str]:
        """Get target audience from content guidelines"""
        return self.content_guidelines.get('target_audience', [])
    
    def get_platform_guidelines(self, platform: str) -> Dict:
        """Get platform-specific content guidelines for a given platform
        
        Args:
            platform: The social media platform to get guidelines for (e.g., 'reddit', 'twitter')
            
        Returns:
            Dict containing the platform-specific guidelines
        """
        platform_guidelines = self.content_guidelines.get('platform_guidelines', {})
        return platform_guidelines.get(platform, {})
    
    def validate_content(self, content: Dict) -> Dict:
        """Validate content against brand guidelines"""
        alignment_score = self._calculate_alignment(content)
        return {
            'aligned': alignment_score >= 0.7,
            'score': alignment_score,
            'improvements': self._suggest_improvements(content)
        }
    
    def _calculate_alignment(self, content: Dict) -> float:
        """Calculate content alignment with brand values"""
        try:
            text = content.get('text', '')
            sentiment = TextBlob(text).sentiment.polarity
            
            # Calculate alignment based on brand values
            alignment_scores = []
            for value, importance in self.brand_values.items():
                value_score = self._calculate_value_alignment(text, value)
                alignment_scores.append(value_score * importance)
                
            return np.mean(alignment_scores) if alignment_scores else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating alignment: {e}")
            return 0.0
    
    def _calculate_value_alignment(self, text: str, value: str) -> float:
        """Calculate alignment with specific brand value
        
        Args:
            text: The content text to analyze
            value: The brand value to check alignment against
            
        Returns:
            float: Alignment score between 0 and 1
        """
        try:
            # Create a TextBlob for sentiment analysis
            blob = TextBlob(text.lower())
            
            # Basic value alignment calculation based on word presence and sentiment
            value_words = {
                'innovation': ['new', 'innovative', 'cutting-edge', 'advanced'],
                'reliability': ['reliable', 'consistent', 'stable', 'trusted'],
                'sustainability': ['sustainable', 'green', 'eco-friendly', 'environmental'],
                'quality': ['quality', 'premium', 'excellent', 'superior'],
                'customer_focus': ['customer', 'service', 'support', 'satisfaction']
            }
            
            # Get relevant words for the value
            relevant_words = value_words.get(value.lower(), [value.lower()])
            
            # Check word presence
            word_matches = sum(1 for word in relevant_words if word in text.lower())
            word_score = min(word_matches / len(relevant_words), 1.0)
            
            # Combine with sentiment
            sentiment_score = (blob.sentiment.polarity + 1) / 2  # Normalize to 0-1
            
            # Weighted combination
            return 0.7 * word_score + 0.3 * sentiment_score
            
        except Exception as e:
            logger.error(f"Error in value alignment calculation: {e}")
            return 0.0
    
    def _suggest_improvements(self, content: Dict) -> List[str]:
        """Generate improvement suggestions for content"""
        suggestions = []
        alignment = self._calculate_alignment(content)
        
        if alignment < 0.7:
            suggestions.append("Consider adjusting tone to better match brand voice")
        if alignment < 0.5:
            suggestions.append("Content may need significant revision to align with brand values")
            
        return suggestions
