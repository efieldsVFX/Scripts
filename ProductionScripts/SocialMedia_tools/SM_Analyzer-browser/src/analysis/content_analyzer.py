"""
Content Analyzer
Combines sentiment analysis, topic modeling, and engagement metrics
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import logging
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import re
from typing import Dict, List
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
import requests

logger = logging.getLogger(__name__)

class ContentAnalyzer:
    def __init__(self, posts_file: str = None, comments_file: str = None):
        """Initialize analyzer with optional data files"""
        self.cancellation_callback = None
        self.posts_df = None
        self.comments_df = None
        
        # Load data if files are provided
        if posts_file:
            self.posts_df = pd.read_csv(posts_file)
            self.posts_df['created_utc'] = pd.to_datetime(self.posts_df['created_utc'])
        if comments_file:
            self.comments_df = pd.read_csv(comments_file)
            
    def set_cancellation_callback(self, callback):
        """Set a callback function to check for cancellation requests"""
        self.cancellation_callback = callback
    
    def should_cancel(self):
        """Check if analysis should be cancelled"""
        return self.cancellation_callback and self.cancellation_callback()
    
    def analyze(self):
        """Run complete analysis"""
        if self.should_cancel():
            return None
            
        results = {
            'sentiment': self._analyze_sentiment(),
            'topics': self._analyze_topics(),
            'engagement': self._analyze_engagement(),
            'recommendations': self._generate_recommendations()
        }
        
        if not self.should_cancel():
            self._generate_visualizations()
        return results
        
    def _analyze_sentiment(self):
        """Analyze sentiment of posts and comments"""
        from .sentiment_analyzer import SentimentAnalyzer
        
        analyzer = SentimentAnalyzer(method='spacy')
        sentiment_results = {
            'overall_sentiment': 'neutral',
            'sentiment_scores': {
                'positive': 0,
                'negative': 0,
                'neutral': 0
            }
        }
        
        if self.posts_df is not None:
            texts = self.posts_df['title'].fillna('') + ' ' + self.posts_df['text'].fillna('')
            sentiment_results = analyzer.get_aggregate_sentiment(texts)
            
        return sentiment_results
        
    def _analyze_topics(self):
        """Extract trending topics"""
        def clean_text(text):
            if isinstance(text, str):
                text = re.sub(r'http\S+|www\S+|https\S+', '', text)
                text = re.sub(r'[^\w\s]', '', text)
                return text.lower()
            return ''
            
        # Combine title and text
        all_text = ' '.join(
            self.posts_df['title'].fillna('').apply(clean_text) + ' ' + 
            self.posts_df['text'].fillna('').apply(clean_text)
        )
        
        words = word_tokenize(all_text)
        stop_words = set(stopwords.words('english'))
        words = [w for w in words if w not in stop_words and len(w) > 3]
        
        return Counter(words).most_common(10)
        
    def _analyze_engagement(self):
        """Analyze engagement patterns"""
        if self.posts_df is None:
            return {}
            
        engagement_metrics = {
            'total_posts': len(self.posts_df),
            'avg_score': self.posts_df['score'].mean(),
            'max_score': self.posts_df['score'].max(),
            'engagement_by_hour': self.posts_df.groupby(
                self.posts_df['created_utc'].dt.hour
            )['score'].mean().to_dict()
        }
        
        return engagement_metrics
        
    def _generate_recommendations(self):
        """Generate content recommendations"""
        recommendations = []
        
        if self.posts_df is not None:
            # Time-based recommendations
            peak_hours = pd.Series(
                self._analyze_engagement()['engagement_by_hour']
            ).nlargest(3)
            
            recommendations.append({
                'type': 'timing',
                'message': f'Best posting times: {", ".join(str(h) for h in peak_hours.index)}:00',
                'confidence': 0.8
            })
            
            # Topic recommendations
            top_topics = self._analyze_topics()
            if top_topics:
                recommendations.append({
                    'type': 'topics',
                    'message': f'Top performing topics: {", ".join(t[0] for t in top_topics[:3])}',
                    'confidence': 0.7
                })
                
        return recommendations
        
    def _generate_visualizations(self):
        """Generate analysis visualizations"""
        if self.posts_df is None:
            return
            
        # Create output directory
        output_dir = Path('output/visualizations')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Engagement over time
        plt.figure(figsize=(12, 6))
        sns.scatterplot(
            data=self.posts_df,
            x='created_utc',
            y='score',
            alpha=0.6
        )
        plt.title('Engagement Over Time')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(output_dir / 'engagement_time.png')
        plt.close()
        
        # Engagement by hour
        engagement_by_hour = self.posts_df.groupby(
            self.posts_df['created_utc'].dt.hour
        )['score'].mean()
        
        plt.figure(figsize=(12, 6))
        engagement_by_hour.plot(kind='bar')
        plt.title('Average Engagement by Hour')
        plt.xlabel('Hour of Day')
        plt.ylabel('Average Score')
        plt.tight_layout()
        plt.savefig(output_dir / 'engagement_hour.png')
        plt.close()
        
    def analyze_content(self, content_df: pd.DataFrame, platform: str = None) -> Dict:
        """Analyze content from DataFrame input"""
        try:
            # Store the input DataFrame
            self.posts_df = content_df
            
            # Ensure datetime conversion for created_utc
            if 'created_utc' in self.posts_df.columns:
                self.posts_df['created_utc'] = pd.to_datetime(self.posts_df['created_utc'])
            
            # Run analysis
            analysis_results = {
                'basic_metrics': {
                    'total_posts': len(content_df),
                    'total_engagement': content_df['score'].sum() if 'score' in content_df.columns else 0,
                    'avg_engagement': content_df['score'].mean() if 'score' in content_df.columns else 0,
                },
                'sentiment': self._analyze_sentiment(),
                'topics': self._analyze_topics(),
                'engagement': self._analyze_engagement(),
                'recommendations': self._generate_recommendations()
            }
            
            # Generate visualizations if not cancelled
            if not self.should_cancel():
                self._generate_visualizations()
                
            return analysis_results
            
        except Exception as e:
            logger.error(f"Error in content analysis: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'metrics': {}
            }

class BaseContentAnalyzer:
    """Base class for analyzing social media content with advanced metrics"""
    
    def __init__(self, platform: str):
        """Initialize content analyzer"""
        self.platform = platform
        self.logger = logging.getLogger(__name__)
    
    def analyze_content_journey(self, content_data: Dict) -> Dict:
        """
        Analyze content performance journey over time
        
        Args:
            content_data: Dict containing content metrics over time
            
        Returns:
            Dict containing journey analysis metrics
        """
        try:
            journey_metrics = {
                'engagement_curve': self._calculate_engagement_curve(content_data),
                'peak_performance': max(content_data.get('engagement_history', [])),
                'time_to_peak': self._calculate_time_to_peak(content_data),
                'decay_rate': self._calculate_decay_rate(content_data)
            }
            return journey_metrics
        except Exception as e:
            self.logger.error(f"Error analyzing content journey: {str(e)}")
            return {}
    
    def analyze_creative_impact(self, content_url: str, performance_data: Dict) -> Dict:
        """
        Analyze creative elements and their impact on performance
        
        Args:
            content_url: URL to the content media
            performance_data: Dict containing performance metrics
            
        Returns:
            Dict containing creative impact analysis
        """
        try:
            impact_metrics = {
                'visual_elements': self._analyze_visual_elements(content_url),
                'performance_correlation': self._correlate_elements_performance(
                    performance_data
                )
            }
            return impact_metrics
        except Exception as e:
            self.logger.error(f"Error analyzing creative impact: {str(e)}")
            return {}
    
    def predict_content_metrics(self, content_data: Dict) -> Dict:
        """
        Generate predictive metrics for content performance
        
        Args:
            content_data: Dict containing historical content data
            
        Returns:
            Dict containing predicted metrics
        """
        try:
            predictions = {
                'virality_score': self._predict_virality(content_data),
                'decay_curve': self._predict_decay_curve(content_data),
                'lifetime_value': self._calculate_predicted_lifetime_value(content_data),
                'trend_alignment': self._analyze_trend_alignment(content_data),
                'growth_potential': self._estimate_growth_potential(content_data)
            }
            return predictions
        except Exception as e:
            self.logger.error(f"Error predicting content metrics: {str(e)}")
            return {}
    
    def _calculate_engagement_curve(self, content_data: Dict) -> List[float]:
        """Calculate engagement curve over time"""
        try:
            engagement_history = content_data.get('engagement_history', [])
            if not engagement_history:
                return []
            
            # Normalize engagement values
            scaler = StandardScaler()
            normalized = scaler.fit_transform([[x] for x in engagement_history])
            return normalized.flatten().tolist()
        except Exception as e:
            self.logger.error(f"Error calculating engagement curve: {str(e)}")
            return []
    
    def _analyze_visual_elements(self, content_url: str) -> Dict:
        """Analyze visual elements"""
        try:
            response = requests.get(content_url)
            response.raise_for_status()
            
            # Basic image analysis
            return {
                'has_image': True,
                'size': len(response.content),
                'format': response.headers.get('content-type', '')
            }
        except Exception as e:
            self.logger.error(f"Error analyzing visual elements: {str(e)}")
            return {'has_image': False}
    
    def _predict_virality(self, content_data: Dict) -> float:
        """Predict content virality using machine learning"""
        try:
            engagement_history = content_data.get('engagement_history', [])
            if len(engagement_history) < 2:
                return 0.0
            
            # Use Isolation Forest to detect potential viral content
            clf = IsolationForest(contamination=0.1, random_state=42)
            scores = clf.fit_predict([[x] for x in engagement_history])
            
            # Convert isolation scores to virality probability
            virality_score = (scores == -1).mean()  # Proportion of anomalous points
            return float(virality_score)
        except Exception as e:
            self.logger.error(f"Error predicting virality: {str(e)}")
            return 0.0
    
    def _calculate_predicted_lifetime_value(self, content_data: Dict) -> float:
        """Calculate predicted lifetime value (PLV) of content"""
        try:
            engagement_history = content_data.get('engagement_history', [])
            if not engagement_history:
                return 0.0
            
            # Simple exponential decay model
            current_value = engagement_history[-1]
            decay_rate = self._calculate_decay_rate(content_data)
            time_horizon = 30  # Days
            
            plv = current_value * (1 - decay_rate) ** time_horizon
            return max(0.0, float(plv))
        except Exception as e:
            self.logger.error(f"Error calculating PLV: {str(e)}")
            return 0.0
    
    def _calculate_decay_rate(self, content_data: Dict) -> float:
        """Calculate engagement decay rate"""
        try:
            engagement_history = content_data.get('engagement_history', [])
            if len(engagement_history) < 2:
                return 0.0
            
            # Calculate average decay between consecutive points
            decays = [
                (engagement_history[i] - engagement_history[i+1]) / engagement_history[i]
                for i in range(len(engagement_history)-1)
                if engagement_history[i] > 0
            ]
            
            return float(np.mean(decays)) if decays else 0.0
        except Exception as e:
            self.logger.error(f"Error calculating decay rate: {str(e)}")
            return 0.0
    
    def _calculate_time_to_peak(self, content_data: Dict) -> int:
        """Calculate time to peak engagement"""
        try:
            engagement_history = content_data.get('engagement_history', [])
            if not engagement_history:
                return 0
            
            peak_index = np.argmax(engagement_history)
            return int(peak_index)
        except Exception as e:
            self.logger.error(f"Error calculating time to peak: {str(e)}")
            return 0
    
    def _analyze_trend_alignment(self, content_data: Dict) -> float:
        """Analyze alignment with current trends"""
        try:
            trend_keywords = content_data.get('trend_keywords', [])
            content_keywords = content_data.get('content_keywords', [])
            
            if not trend_keywords or not content_keywords:
                return 0.0
            
            # Calculate keyword overlap
            overlap = len(set(trend_keywords) & set(content_keywords))
            alignment_score = overlap / len(trend_keywords)
            
            return float(alignment_score)
        except Exception as e:
            self.logger.error(f"Error analyzing trend alignment: {str(e)}")
            return 0.0
    
    def _estimate_growth_potential(self, content_data: Dict) -> float:
        """Estimate potential for future growth"""
        try:
            virality = self._predict_virality(content_data)
            trend_alignment = self._analyze_trend_alignment(content_data)
            current_engagement = content_data.get('current_engagement', 0)
            
            # Combine factors into growth potential score
            growth_potential = (
                0.4 * virality +
                0.3 * trend_alignment +
                0.3 * min(1.0, current_engagement / 1000)
            )
            
            return float(growth_potential)
        except Exception as e:
            self.logger.error(f"Error estimating growth potential: {str(e)}")
            return 0.0
    
    def _predict_decay_curve(self, content_data: Dict) -> List[float]:
        """Predict future engagement decay"""
        try:
            current_engagement = content_data.get('current_engagement', 0)
            decay_rate = self._calculate_decay_rate(content_data)
            
            # Project decay curve for next 30 points
            decay_curve = [
                current_engagement * (1 - decay_rate) ** i
                for i in range(30)
            ]
            
            return decay_curve
        except Exception as e:
            self.logger.error(f"Error predicting decay curve: {str(e)}")
            return []
    
    def _correlate_elements_performance(self, performance_data: Dict) -> Dict:
        """Correlate creative elements with performance metrics"""
        try:
            elements = performance_data.get('creative_elements', {})
            metrics = performance_data.get('performance_metrics', {})
            
            correlations = {}
            for element, presence in elements.items():
                if presence and metrics:
                    correlation = np.corrcoef(
                        [float(presence)],
                        [float(m) for m in metrics.values()]
                    )[0, 1]
                    correlations[element] = float(correlation)
            
            return correlations
        except Exception as e:
            self.logger.error(f"Error correlating elements: {str(e)}")
            return {}
