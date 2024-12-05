"""
Sentiment Analyzer
Handles sentiment analysis using various methods (VADER, Transformers, TextBlob).
"""

from typing import List, Dict, Union, Optional
import pandas as pd
import numpy as np
from nltk.sentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
from transformers import pipeline
from src.utils import logger, MODEL_CONFIG
import logging

logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    def __init__(self, method: str = 'vader', model_name: str = 'distilbert-base-uncased-finetuned-sst-2-english'):
        """
        Initialize sentiment analyzer with specified method
        
        Args:
            method (str): Sentiment analysis method ('vader', 'textblob', or 'transformers')
            model_name (str): Transformer model name if using 'transformers' method
        """
        self.method = method.lower()
        self.model_name = model_name
        
        if self.method == 'vader':
            try:
                self.analyzer = SentimentIntensityAnalyzer()
            except Exception as e:
                logger.error(f"Error initializing VADER: {str(e)}")
                raise
        elif self.method == 'transformers':
            try:
                self.analyzer = pipeline("sentiment-analysis", model=model_name)
            except Exception as e:
                logger.error(f"Error initializing Transformer model: {str(e)}")
                raise
        elif self.method == 'textblob':
            self.analyzer = TextBlob
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        logger.info(f"Sentiment analyzer initialized using {method}")

    def analyze_text(self, text: Union[str, float, None]) -> Dict[str, Union[float, str]]:
        """
        Analyze sentiment of a single text
        
        Args:
            text: Input text (can be string, float, or None)
            
        Returns:
            Dict containing sentiment scores and classification
        """
        try:
            # Handle non-string inputs
            if not isinstance(text, str):
                if pd.isna(text):
                    text = ''
                else:
                    text = str(text)
            
            # Return neutral sentiment for empty text
            if not text.strip():
                return {
                    'compound': 0.0,
                    'positive': 0.0,
                    'negative': 0.0,
                    'neutral': 1.0,
                    'sentiment': 'neutral'
                }
            
            if self.method == 'vader':
                scores = self.analyzer.polarity_scores(text)
                sentiment = self._classify_vader_sentiment(scores['compound'])
                return {
                    'compound': scores['compound'],
                    'positive': scores['pos'],
                    'negative': scores['neg'],
                    'neutral': scores['neu'],
                    'sentiment': sentiment
                }
            
        except Exception as e:
            logger.error(f"Error analyzing text: {str(e)}")
            # Return neutral sentiment on error
            return {
                'compound': 0.0,
                'positive': 0.0,
                'negative': 0.0,
                'neutral': 1.0,
                'sentiment': 'neutral'
            }

    def analyze_dataframe(self, df: pd.DataFrame, text_column: str, prefix: str = '') -> pd.DataFrame:
        """
        Analyze sentiment for texts in a DataFrame
        """
        if text_column not in df.columns:
            raise ValueError(f"Column '{text_column}' not found in DataFrame")

        logger.info(f"Analyzing sentiment for column '{text_column}'")
        
        # Create a copy to avoid modifying the original
        df = df.copy()
        
        # Ensure text column contains strings
        df[text_column] = df[text_column].fillna('').astype(str)
        
        # Track analysis progress
        total_rows = len(df)
        results = []
        
        for idx, text in enumerate(df[text_column], 1):
            if idx % 100 == 0:
                logger.debug(f"Analyzed {idx}/{total_rows} texts")
            results.append(self.analyze_text(text))
        
        # Convert results to DataFrame columns
        if self.method == 'vader':
            df['sentiment_score'] = [r['compound'] for r in results]
            df['sentiment'] = [r['sentiment'] for r in results]
            df['sentiment_positive'] = [r['positive'] for r in results]
            df['sentiment_negative'] = [r['negative'] for r in results]
            df['sentiment_neutral'] = [r['neutral'] for r in results]
        
        logger.debug(f"Added sentiment columns: {[col for col in df.columns if 'sentiment' in col]}")
        logger.debug(f"Sample sentiment scores: {df['sentiment_score'].head()}")
        
        return df

    def get_aggregate_sentiment(self, texts: List[str]) -> Dict[str, Union[float, Dict]]:
        """
        Get aggregate sentiment statistics for a list of texts
        
        Args:
            texts (List[str]): List of input texts
            
        Returns:
            Dict: Aggregate sentiment statistics
        """
        sentiments = [self.analyze_text(text) for text in texts]
        
        if self.method == 'vader':
            compounds = [s['compound'] for s in sentiments]
            sentiment_counts = pd.Series([s['sentiment'] for s in sentiments]).value_counts()
            
            return {
                'mean_compound': np.mean(compounds),
                'std_compound': np.std(compounds),
                'sentiment_distribution': sentiment_counts.to_dict(),
                'dominant_sentiment': sentiment_counts.index[0]
            }
            
        elif self.method == 'transformers':
            scores = [s['score'] for s in sentiments]
            sentiment_counts = pd.Series([s['sentiment'] for s in sentiments]).value_counts()
            
            return {
                'mean_score': np.mean(scores),
                'std_score': np.std(scores),
                'sentiment_distribution': sentiment_counts.to_dict(),
                'dominant_sentiment': sentiment_counts.index[0]
            }
            
        elif self.method == 'textblob':
            polarities = [s['polarity'] for s in sentiments]
            subjectivities = [s['subjectivity'] for s in sentiments]
            sentiment_counts = pd.Series([s['sentiment'] for s in sentiments]).value_counts()
            
            return {
                'mean_polarity': np.mean(polarities),
                'std_polarity': np.std(polarities),
                'mean_subjectivity': np.mean(subjectivities),
                'std_subjectivity': np.std(subjectivities),
                'sentiment_distribution': sentiment_counts.to_dict(),
                'dominant_sentiment': sentiment_counts.index[0]
            }

    @staticmethod
    def _classify_vader_sentiment(compound_score: float) -> str:
        """Classify VADER compound score into sentiment category"""
        if compound_score >= 0.05:
            return 'positive'
        elif compound_score <= -0.05:
            return 'negative'
        else:
            return 'neutral'

    @staticmethod
    def _classify_textblob_sentiment(polarity: float) -> str:
        """Classify TextBlob polarity into sentiment category"""
        if polarity > 0:
            return 'positive'
        elif polarity < 0:
            return 'negative'
        else:
            return 'neutral' 