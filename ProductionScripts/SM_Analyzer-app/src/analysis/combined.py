"""
Content Analysis Module
"""

import pandas as pd
import numpy as np
from textblob import TextBlob
from collections import Counter
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from .sentiment_analyzer import SentimentAnalyzer
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import re
import logging
import os
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class ContentAnalyzer:
    def __init__(self, posts_file, comments_file):
        """Initialize analyzer with data files"""
        # Load data
        self.posts_df = pd.read_csv(posts_file)
        self.comments_df = pd.read_csv(comments_file)
        self.sentiment_analyzer = SentimentAnalyzer(method='vader')
        
        # Verify and prepare required columns
        required_columns = {
            'posts': ['text', 'title', 'created_utc'],
            'comments': ['body', 'created_utc']
        }
        
        # Check posts columns
        for col in required_columns['posts']:
            if col not in self.posts_df.columns:
                logger.error(f"Required column '{col}' not found in posts DataFrame")
                raise ValueError(f"Missing required column '{col}' in posts data")
        
        # Check comments columns
        if self.comments_df.empty:
            logger.warning("Comments DataFrame is empty")
            self.comments_df['body'] = ''
            self.comments_df['created_utc'] = pd.NaT
        else:
            for col in required_columns['comments']:
                if col not in self.comments_df.columns:
                    logger.warning(f"Required column '{col}' not found in comments DataFrame")
                    self.comments_df[col] = ''
        
        # Clean and prepare text columns
        self.posts_df['text'] = self.posts_df['text'].fillna('').astype(str)
        self.posts_df['title'] = self.posts_df['title'].fillna('').astype(str)
        self.comments_df['body'] = self.comments_df['body'].fillna('').astype(str)
        
        # Convert timestamps
        self.posts_df['created_utc'] = pd.to_datetime(self.posts_df['created_utc'])
        self.comments_df['created_utc'] = pd.to_datetime(self.comments_df['created_utc'])
        
        self.cancellation_callback = None
    
    def set_cancellation_callback(self, callback):
        """Set a callback function to check for cancellation requests"""
        self.cancellation_callback = callback
    
    def should_cancel(self):
        """Check if analysis should be cancelled"""
        return self.cancellation_callback and self.cancellation_callback()
    
    def perform_analysis(self, progress_callback=None, output_dir=None):
        """Perform full analysis and save results"""
        try:
            if progress_callback:
                progress_callback(0, "Starting analysis...")
            
            # Perform analysis steps
            sentiment_results = self.analyze_sentiment()
            if progress_callback:
                progress_callback(30, "Sentiment analysis complete...")
            
            engagement_results = self._analyze_engagement()
            if progress_callback:
                progress_callback(60, "Engagement analysis complete...")
            
            recommendations = self._generate_recommendations()
            if progress_callback:
                progress_callback(90, "Generating recommendations...")
            
            # Combine results
            analysis_results = {
                'sentiment': sentiment_results,
                'engagement': engagement_results,
                'recommendations': recommendations
            }
            
            # Save results if output directory provided
            if output_dir:
                output_path = Path(output_dir) / 'analysis_results.json'
                with open(output_path, 'w') as f:
                    json.dump(analysis_results, f, indent=4)
                
                # Generate visualizations
                self.plot_insights(str(output_dir / 'visualizations'))
            
            if progress_callback:
                progress_callback(100, "Analysis complete!")
            
            return analysis_results
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            raise
    
    def analyze_sentiment(self):
        """Analyze sentiment for posts and comments"""
        # Analyze posts sentiment
        self.posts_df = self.sentiment_analyzer.analyze_dataframe(self.posts_df, 'text')
        
        # Analyze comments sentiment if available
        if not self.comments_df.empty and 'body' in self.comments_df.columns:
            self.comments_df = self.sentiment_analyzer.analyze_dataframe(self.comments_df, 'body')
            avg_comment_sentiment = self.comments_df['sentiment_score'].mean()
        else:
            logger.warning("No comment data available for sentiment analysis")
            avg_comment_sentiment = None
        
        return {
            'avg_post_sentiment': self.posts_df['sentiment_score'].mean(),
            'avg_comment_sentiment': avg_comment_sentiment,
            'total_analyzed_posts': len(self.posts_df),
            'total_analyzed_comments': len(self.comments_df) if not self.comments_df.empty else 0
        }
    
    def clean_text(self, text):
        if isinstance(text, str):
            # Remove URLs
            text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
            # Remove special characters and numbers
            text = re.sub(r'[^\w\s]', '', text)
            # Convert to lowercase
            text = text.lower()
            return text
        return ''
    
    def identify_trending_topics(self, n_topics=10):
        # Combine all text
        all_text = ' '.join(
            self.posts_df['text'].fillna('').astype(str) + ' ' + 
            self.posts_df['title'].fillna('').astype(str)
        )
        
        # Clean and tokenize
        words = word_tokenize(self.clean_text(all_text))
        stop_words = set(stopwords.words('english'))
        words = [w for w in words if w not in stop_words and len(w) > 3]
        
        # Get most common topics
        return Counter(words).most_common(n_topics)
    
    def _analyze_engagement(self):
        """Analyze engagement patterns"""
        return {
            'avg_post_score': float(self.posts_df['score'].mean()),
            'avg_comments': float(self.posts_df['num_comments'].mean()),
            'total_posts': int(len(self.posts_df)),
            'total_comments': int(len(self.comments_df)),
            'unique_authors': int(len(self.posts_df['author'].unique())),
            'peak_posting_hours': int(self.posts_df['created_utc'].dt.hour.mode().iloc[0]),
            'top_subreddits': {k: int(v) for k, v in self.posts_df['subreddit'].value_counts().head(5).to_dict().items()} if 'subreddit' in self.posts_df.columns else {}
        }
    
    def _generate_recommendations(self):
        """Generate content recommendations"""
        try:
            high_engagement_posts = self.posts_df[
                self.posts_df['score'] > self.posts_df['score'].median()
            ]
            
            if 'sentiment_score' not in self.posts_df.columns:
                logger.warning("No sentiment_score found. Running sentiment analysis...")
                self.analyze_sentiment()
            
            topics = self.identify_trending_topics(5)
            return {
                'optimal_posting_time': int(high_engagement_posts['created_utc'].dt.hour.mode().iloc[0]),
                'successful_topics': [(str(topic), int(count)) for topic, count in topics],
                'sentiment_correlation': float(self.posts_df['score'].corr(self.posts_df['sentiment_score']))
            }
            
        except Exception as e:
            logger.error(f"Error generating content suggestions: {str(e)}")
            return {
                'optimal_posting_time': None,
                'successful_topics': [],
                'sentiment_correlation': None
            }
    
    def plot_insights(self, output_dir='output'):
        """Create visualizations"""
        try:
            # Ensure output directory exists
            os.makedirs(output_dir, exist_ok=True)
            
            # Sentiment distribution - adjusted size
            plt.figure(figsize=(8, 5), dpi=80)
            sns.histplot(data=self.posts_df, x='sentiment_score')
            plt.title('Sentiment Distribution in Posts', fontsize=10)
            plt.xlabel('Sentiment Score', fontsize=9)
            plt.ylabel('Count', fontsize=9)
            plt.xticks(fontsize=8)
            plt.yticks(fontsize=8)
            plt.tight_layout()
            plt.savefig(f'{output_dir}/sentiment_distribution.png', bbox_inches='tight')
            plt.close()
            
            # Engagement over time - adjusted size
            plt.figure(figsize=(8, 5), dpi=80)
            self.posts_df.set_index('created_utc')['score'].resample('D').mean().plot()
            plt.title('Average Engagement Over Time', fontsize=10)
            plt.xlabel('Date', fontsize=9)
            plt.ylabel('Average Score', fontsize=9)
            plt.xticks(fontsize=8, rotation=45)
            plt.yticks(fontsize=8)
            plt.tight_layout()
            plt.savefig(f'{output_dir}/engagement_over_time.png', bbox_inches='tight')
            plt.close()
            
        except Exception as e:
            logger.error(f"Error creating visualizations: {str(e)}")
            raise

    def verify_sentiment_analysis(self):
        """Verify that sentiment analysis has been performed"""
        sentiment_columns = [col for col in self.posts_df.columns if 'sentiment' in col]
        if not sentiment_columns:
            logger.warning("No sentiment columns found. Running sentiment analysis...")
            self.analyze_sentiment()
        return True
