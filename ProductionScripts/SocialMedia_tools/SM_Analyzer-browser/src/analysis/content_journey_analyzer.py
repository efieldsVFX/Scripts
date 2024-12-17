"""
Content Journey Analysis Module
Tracks content consumption patterns and creative impact
"""

from typing import Dict, List, Optional
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict

class ContentJourneyAnalyzer:
    def __init__(self):
        self.content_types = ['Story', 'Reel', 'Post', 'Video']
        self.journey_data = defaultdict(list)
        
    def track_content_sequence(self, data: pd.DataFrame) -> Dict:
        """
        Track the sequence of content consumed by users
        
        Args:
            data: DataFrame with columns ['user_id', 'content_id', 'content_type', 'timestamp']
            
        Returns:
            Dict containing journey patterns
        """
        data = data.sort_values(['user_id', 'timestamp'])
        
        # Track transitions between content types
        transitions = defaultdict(int)
        for user_id, group in data.groupby('user_id'):
            content_sequence = group['content_type'].tolist()
            for i in range(len(content_sequence) - 1):
                transition = (content_sequence[i], content_sequence[i + 1])
                transitions[transition] += 1
        
        journey_metrics = {
            'common_paths': dict(transitions),
            'entry_points': data.groupby('user_id')['content_type'].first().value_counts().to_dict(),
            'exit_points': data.groupby('user_id')['content_type'].last().value_counts().to_dict(),
            'avg_journey_length': data.groupby('user_id').size().mean()
        }
        
        return journey_metrics
        
    def analyze_creative_impact(self, data: pd.DataFrame) -> Dict:
        """
        Analyze visual and textual elements driving performance
        
        Args:
            data: DataFrame with columns ['content_id', 'visual_elements', 'text_elements', 'engagement_metrics']
            
        Returns:
            Dict containing creative performance metrics
        """
        # Analyze impact of different creative elements
        visual_impact = data.groupby('visual_elements')['engagement_metrics'].mean().to_dict()
        text_impact = data.groupby('text_elements')['engagement_metrics'].mean().to_dict()
        
        # Calculate element combinations performance
        data['element_combo'] = data['visual_elements'] + ' + ' + data['text_elements']
        combo_impact = data.groupby('element_combo')['engagement_metrics'].mean().nlargest(5).to_dict()
        
        creative_metrics = {
            'visual_element_performance': visual_impact,
            'text_element_performance': text_impact,
            'top_element_combinations': combo_impact,
            'overall_engagement_correlation': self._calculate_element_correlation(data)
        }
        
        return creative_metrics
        
    def _calculate_element_correlation(self, data: pd.DataFrame) -> Dict:
        """Calculate correlation between creative elements and engagement"""
        # Convert categorical elements to dummy variables
        visual_dummies = pd.get_dummies(data['visual_elements'], prefix='visual')
        text_dummies = pd.get_dummies(data['text_elements'], prefix='text')
        
        # Combine with engagement metrics
        correlation_data = pd.concat([visual_dummies, text_dummies, data['engagement_metrics']], axis=1)
        correlations = correlation_data.corr()['engagement_metrics'].sort_values(ascending=False).to_dict()
        
        return correlations
        
    def get_content_insights(self, data: pd.DataFrame) -> Dict:
        """
        Generate comprehensive content insights
        
        Args:
            data: DataFrame containing all content data
            
        Returns:
            Dict containing overall content metrics
        """
        journey_metrics = self.track_content_sequence(data)
        creative_metrics = self.analyze_creative_impact(data)
        
        return {
            'content_journey': journey_metrics,
            'creative_impact': creative_metrics
        }
