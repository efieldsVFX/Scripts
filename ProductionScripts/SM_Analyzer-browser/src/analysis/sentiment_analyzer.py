"""
Sentiment Analyzer
Handles sentiment analysis using spaCy and TextBlob.
"""

from typing import List, Dict, Union, Optional
import pandas as pd
import numpy as np
from textblob import TextBlob
import spacy
from src.utils import logger
import logging

logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    def __init__(self, method: str = 'spacy'):
        """
        Initialize sentiment analyzer with specified method
        
        Args:
            method (str): Sentiment analysis method ('spacy' or 'textblob')
        """
        self.method = method.lower()
        
        if self.method == 'spacy':
            try:
                self.nlp = spacy.load('en_core_web_sm')
            except Exception as e:
                logger.error(f"Error initializing spaCy: {str(e)}")
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
                    'score': 0.0,
                    'positive': 0.0,
                    'negative': 0.0,
                    'neutral': 1.0,
                    'sentiment': 'neutral'
                }
            
            if self.method == 'spacy':
                doc = self.nlp(text)
                # Calculate sentiment using spaCy's token polarity
                sentiments = [token.sentiment for token in doc if token.sentiment != 0]
                if not sentiments:
                    score = 0.0
                else:
                    score = np.mean(sentiments)
                
                # Normalize score to [-1, 1] range
                score = max(min(score, 1.0), -1.0)
                
                # Calculate component scores
                pos_score = max(0, score)
                neg_score = abs(min(0, score))
                neu_score = 1.0 - (pos_score + neg_score)
                
                sentiment = self._classify_sentiment(score)
                
                return {
                    'score': score,
                    'positive': pos_score,
                    'negative': neg_score,
                    'neutral': neu_score,
                    'sentiment': sentiment
                }
            
            elif self.method == 'textblob':
                blob = TextBlob(text)
                polarity = blob.sentiment.polarity
                
                # Calculate component scores
                pos_score = max(0, polarity)
                neg_score = abs(min(0, polarity))
                neu_score = 1.0 - (pos_score + neg_score)
                
                sentiment = self._classify_sentiment(polarity)
                
                return {
                    'score': polarity,
                    'positive': pos_score,
                    'negative': neg_score,
                    'neutral': neu_score,
                    'sentiment': sentiment
                }
            
        except Exception as e:
            logger.error(f"Error analyzing text: {str(e)}")
            # Return neutral sentiment on error
            return {
                'score': 0.0,
                'positive': 0.0,
                'negative': 0.0,
                'neutral': 1.0,
                'sentiment': 'neutral'
            }

    def analyze_dataframe(self, df: pd.DataFrame, text_column: str) -> pd.DataFrame:
        """
        Analyze sentiment for texts in a DataFrame
        
        Args:
            df: Input DataFrame
            text_column: Name of column containing text to analyze
            
        Returns:
            DataFrame with added sentiment columns
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
        df['sentiment_score'] = [r['score'] for r in results]
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
        scores = [s['score'] for s in sentiments]
        sentiment_counts = pd.Series([s['sentiment'] for s in sentiments]).value_counts()
        
        return {
            'mean_score': np.mean(scores),
            'std_score': np.std(scores),
            'sentiment_distribution': sentiment_counts.to_dict(),
            'dominant_sentiment': sentiment_counts.index[0]
        }

    @staticmethod
    def _classify_sentiment(score: float) -> str:
        """Classify sentiment score into category"""
        if score >= 0.05:
            return 'positive'
        elif score <= -0.05:
            return 'negative'
        else:
            return 'neutral'