"""
Content Analyzer
Combines sentiment analysis, topic modeling, and engagement metrics
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import logging
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import re

logger = logging.getLogger(__name__)

class ContentAnalyzer:
    def __init__(self, posts_file: str, comments_file: str):
        """Initialize analyzer with data files"""
        self.posts_df = pd.read_csv(posts_file)
        self.comments_df = pd.read_csv(comments_file)
        self.sia = SentimentIntensityAnalyzer()
        self.cancellation_callback = None
        
        # Convert timestamps
        self.posts_df['created_utc'] = pd.to_datetime(self.posts_df['created_utc'])
        
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
        """Analyze sentiment in posts and comments"""
        self.posts_df['sentiment'] = self.posts_df['text'].apply(
            lambda x: self.sia.polarity_scores(str(x))['compound']
        )
        
        return {
            'average_sentiment': self.posts_df['sentiment'].mean(),
            'sentiment_distribution': self.posts_df['sentiment'].value_counts(bins=5).to_dict()
        }
        
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
        return {
            'avg_score': self.posts_df['score'].mean(),
            'avg_comments': self.posts_df['num_comments'].mean(),
            'peak_hours': self.posts_df['created_utc'].dt.hour.value_counts().head(3).to_dict(),
            'top_subreddits': self.posts_df['subreddit'].value_counts().head(5).to_dict()
        }
        
    def _generate_recommendations(self):
        """Generate content recommendations"""
        high_engagement = self.posts_df[
            self.posts_df['score'] > self.posts_df['score'].median()
        ]
        
        return {
            'optimal_posting_time': high_engagement['created_utc'].dt.hour.mode().iloc[0],
            'successful_topics': self._analyze_topics()[:5],
            'engagement_correlation': self.posts_df['score'].corr(self.posts_df['sentiment'])
        }
        
    def _generate_visualizations(self):
        """Create visualization plots"""
        output_dir = Path('output/analysis')
        output_dir.mkdir(exist_ok=True)
        
        # Sentiment distribution
        plt.figure(figsize=(10, 6))
        sns.histplot(data=self.posts_df, x='sentiment', bins=20)
        plt.title('Content Sentiment Distribution')
        plt.savefig(output_dir / 'sentiment_distribution.png')
        plt.close()
        
        # Engagement over time
        plt.figure(figsize=(12, 6))
        self.posts_df.set_index('created_utc')['score'].resample('D').mean().plot()
        plt.title('Average Engagement Over Time')
        plt.savefig(output_dir / 'engagement_timeline.png')
        plt.close()
