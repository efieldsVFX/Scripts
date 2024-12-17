"""
Topic Modeler
Handles topic modeling using various methods (LDA, NMF, BERTopic).
"""

from typing import List, Dict, Union, Optional, Tuple
import pandas as pd
import numpy as np
from gensim import corpora, models
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation, NMF
import pyLDAvis
import pyLDAvis.gensim_models
from bertopic import BERTopic
from utils import logger, MODEL_CONFIG

class TopicModeler:
    def __init__(self, 
                 method: str = 'lda',
                 num_topics: int = 5,
                 random_state: int = 42):
        """
        Initialize topic modeler with specified method
        
        Args:
            method (str): Topic modeling method ('lda', 'nmf', or 'bertopic')
            num_topics (int): Number of topics to extract
            random_state (int): Random state for reproducibility
        """
        self.method = method.lower()
        self.num_topics = num_topics
        self.random_state = random_state
        self.model = None
        self.dictionary = None
        self.corpus = None
        self.vectorizer = None
        
        logger.info(f"Topic modeler initialized using {method}")

    def fit(self, texts: List[str]) -> None:
        """
        Fit topic model to texts
        
        Args:
            texts (List[str]): List of preprocessed texts
        """
        try:
            if self.method == 'lda':
                self._fit_lda(texts)
            elif self.method == 'nmf':
                self._fit_nmf(texts)
            elif self.method == 'bertopic':
                self._fit_bertopic(texts)
            else:
                raise ValueError(f"Unsupported method: {self.method}")
                
            logger.info(f"Topic model fitted successfully")
            
        except Exception as e:
            logger.error(f"Error fitting topic model: {str(e)}")
            raise

    def transform(self, texts: List[str]) -> np.ndarray:
        """
        Transform texts to topic distributions
        
        Args:
            texts (List[str]): List of preprocessed texts
            
        Returns:
            np.ndarray: Topic distributions for input texts
        """
        try:
            if self.method == 'lda':
                return self._transform_lda(texts)
            elif self.method == 'nmf':
                return self._transform_nmf(texts)
            elif self.method == 'bertopic':
                return self._transform_bertopic(texts)
                
        except Exception as e:
            logger.error(f"Error transforming texts: {str(e)}")
            raise

    def get_topics(self, num_words: int = 10) -> Dict[int, List[Tuple[str, float]]]:
        """
        Get top words for each topic
        
        Args:
            num_words (int): Number of words to return per topic
            
        Returns:
            Dict: Topics with their top words and weights
        """
        try:
            if self.method == 'lda':
                return self._get_lda_topics(num_words)
            elif self.method == 'nmf':
                return self._get_nmf_topics(num_words)
            elif self.method == 'bertopic':
                return self._get_bertopic_topics(num_words)
                
        except Exception as e:
            logger.error(f"Error getting topics: {str(e)}")
            raise

    def visualize_topics(self, output_path: Optional[str] = None):
        """
        Generate topic visualization
        
        Args:
            output_path (str, optional): Path to save visualization
        """
        try:
            if self.method == 'lda':
                vis_data = pyLDAvis.gensim_models.prepare(
                    self.model, self.corpus, self.dictionary
                )
                if output_path:
                    pyLDAvis.save_html(vis_data, output_path)
                return vis_data
                
            elif self.method == 'bertopic':
                return self.model.visualize_topics()
                
        except Exception as e:
            logger.error(f"Error visualizing topics: {str(e)}")
            raise

    def _fit_lda(self, texts: List[str]) -> None:
        """Fit LDA model"""
        # Create dictionary and corpus
        tokenized_texts = [text.split() for text in texts]
        self.dictionary = corpora.Dictionary(tokenized_texts)
        self.corpus = [self.dictionary.doc2bow(text) for text in tokenized_texts]
        
        # Train LDA model
        self.model = models.LdaModel(
            corpus=self.corpus,
            id2word=self.dictionary,
            num_topics=self.num_topics,
            random_state=self.random_state,
            update_every=1,
            chunksize=100,
            passes=10,
            alpha='auto',
            per_word_topics=True
        )

    def _fit_nmf(self, texts: List[str]) -> None:
        """Fit NMF model"""
        # Create TF-IDF matrix
        self.vectorizer = TfidfVectorizer(max_features=5000)
        tfidf_matrix = self.vectorizer.fit_transform(texts)
        
        # Train NMF model
        self.model = NMF(
            n_components=self.num_topics,
            random_state=self.random_state
        )
        self.model.fit(tfidf_matrix)

    def _fit_bertopic(self, texts: List[str]) -> None:
        """Fit BERTopic model"""
        self.model = BERTopic(
            n_topics=self.num_topics,
            random_state=self.random_state
        )
        self.model.fit(texts)

    def _transform_lda(self, texts: List[str]) -> np.ndarray:
        """Transform texts using LDA"""
        corpus = [self.dictionary.doc2bow(text.split()) for text in texts]
        return np.array([[topic[1] for topic in self.model.get_document_topics(doc)] 
                        for doc in corpus])

    def _transform_nmf(self, texts: List[str]) -> np.ndarray:
        """Transform texts using NMF"""
        tfidf_matrix = self.vectorizer.transform(texts)
        return self.model.transform(tfidf_matrix)

    def _transform_bertopic(self, texts: List[str]) -> np.ndarray:
        """Transform texts using BERTopic"""
        topics, probs = self.model.transform(texts)
        return probs

    def _get_lda_topics(self, num_words: int) -> Dict[int, List[Tuple[str, float]]]:
        """Get LDA topics"""
        return {i: self.model.show_topic(i, num_words) for i in range(self.num_topics)}

    def _get_nmf_topics(self, num_words: int) -> Dict[int, List[Tuple[str, float]]]:
        """Get NMF topics"""
        feature_names = self.vectorizer.get_feature_names_out()
        topics = {}
        for topic_idx, topic in enumerate(self.model.components_):
            top_words = [(feature_names[i], topic[i]) 
                        for i in topic.argsort()[:-num_words-1:-1]]
            topics[topic_idx] = top_words
        return topics

    def _get_bertopic_topics(self, num_words: int) -> Dict[int, List[Tuple[str, float]]]:
        """Get BERTopic topics"""
        topics = {}
        for topic_id in range(self.num_topics):
            topic_words = self.model.get_topic(topic_id)[:num_words]
            topics[topic_id] = topic_words
        return topics 