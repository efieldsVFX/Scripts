"""
EDGLRD Social Media Analytics Dashboard
A user-friendly interface for social media analytics
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import requests
from typing import Dict, List, Optional
from streamlit_extras.metric_cards import style_metric_cards
from dotenv import load_dotenv
import os
import asyncio
import socket
from textblob import TextBlob
import time
from plotly.subplots import make_subplots
import random
import logging

# Initialize logger
logger = logging.getLogger(__name__)

def plot_engagement_patterns(engagement_data):
    """
    Create a visualization for engagement patterns
    Args:
        engagement_data (dict): Dictionary containing hourly and daily engagement patterns
    Returns:
        plotly.graph_objs.Figure: A figure containing the engagement patterns visualization
    """
    # Create subplots
    fig = make_subplots(rows=1, cols=2, subplot_titles=('Hourly Engagement', 'Daily Engagement'))

    # Add hourly engagement bar chart
    hourly_data = engagement_data['hourly']
    fig.add_trace(
        go.Bar(
            x=list(hourly_data.keys()),
            y=list(hourly_data.values()),
            name='Hourly',
            marker_color='rgb(55, 83, 109)'
        ),
        row=1, col=1
    )

    # Add daily engagement bar chart
    daily_data = engagement_data['daily']
    fig.add_trace(
        go.Bar(
            x=list(daily_data.keys()),
            y=list(daily_data.values()),
            name='Daily',
            marker_color='rgb(26, 118, 255)'
        ),
        row=1, col=2
    )

    # Update layout
    fig.update_layout(
        showlegend=False,
        height=400,
        title_text="Engagement Patterns",
        title_x=0.5,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    # Update y-axes to show percentages
    fig.update_yaxes(title_text="Percentage (%)", range=[0, 100])

    # Update x-axes
    fig.update_xaxes(title_text="Time of Day", row=1, col=1)
    fig.update_xaxes(title_text="Day Type", row=1, col=2)

    return fig

class SentimentAnalyzer:
    """Analyzes sentiment of text using various methods"""
    
    def __init__(self, method='textblob'):
        self.method = method
    
    def analyze_text(self, text: str) -> float:
        """Analyze sentiment of a single text"""
        if not text or not isinstance(text, str):
            return 0.0
            
        if self.method == 'textblob':
            blob = TextBlob(text)
            return blob.sentiment.polarity
        return 0.0
    
    def analyze_dataframe(self, df: pd.DataFrame, text_column: str) -> pd.DataFrame:
        """Analyze sentiment for all texts in a dataframe"""
        df = df.copy()
        df['score'] = df[text_column].apply(self.analyze_text)
        df['sentiment'] = df['score'].apply(self._score_to_label)
        return df
    
    def _score_to_label(self, score: float) -> str:
        """Convert sentiment score to label"""
        if score > 0.1:
            return 'positive'
        elif score < -0.1:
            return 'negative'
        return 'neutral'

class EngagementAnalyzer:
    """Analyzes engagement metrics for social media content"""
    
    def get_engagement_summary(self, df: pd.DataFrame) -> Dict:
        """Get summary of engagement metrics"""
        if df.empty:
            return {
                'total_interactions': 0,
                'avg_score': 0,
                'engagement_rate': 0,
                'contextual_engagement': {
                    'overall_rate': 0,
                    'by_sentiment': {'positive': 0, 'neutral': 0, 'negative': 0}
                },
                'engagement_velocity': {
                    'hourly': {'00-06': 0, '06-12': 0, '12-18': 0, '18-24': 0},
                    'daily': {'weekday': 0, 'weekend': 0}
                }
            }
            
        total_interactions = len(df)
        avg_score = df['score'].mean() if 'score' in df.columns else 0
        engagement_rate = (df['score'] > 0).mean() if 'score' in df.columns else 0
        
        # Calculate engagement by sentiment
        sentiment_engagement = {}
        if 'sentiment' in df.columns:
            for sentiment in ['positive', 'neutral', 'negative']:
                sentiment_subset = df[df['sentiment'] == sentiment]
                sentiment_engagement[sentiment] = len(sentiment_subset) / len(df) if len(df) > 0 else 0
        else:
            sentiment_engagement = {'positive': 0, 'neutral': 0, 'negative': 0}
        
        # Calculate engagement velocity
        engagement_velocity = {
            'hourly': {'00-06': 0, '06-12': 0, '12-18': 0, '18-24': 0},
            'daily': {'weekday': 0, 'weekend': 0}
        }
        
        if 'timestamp' in df.columns:
            # Hourly patterns
            df['hour'] = df['timestamp'].dt.hour
            for start, end in [(0,6), (6,12), (12,18), (18,24)]:
                mask = (df['hour'] >= start) & (df['hour'] < end)
                key = f"{start:02d}-{end:02d}"
                engagement_velocity['hourly'][key] = len(df[mask]) / len(df) if len(df) > 0 else 0
            
            # Daily patterns
            df['is_weekend'] = df['timestamp'].dt.dayofweek >= 5
            weekend_posts = df[df['is_weekend']]
            weekday_posts = df[~df['is_weekend']]
            engagement_velocity['daily'] = {
                'weekend': len(weekend_posts) / len(df) if len(df) > 0 else 0,
                'weekday': len(weekday_posts) / len(df) if len(df) > 0 else 0
            }
        
        return {
            'total_interactions': total_interactions,
            'avg_score': avg_score,
            'engagement_rate': engagement_rate,
            'contextual_engagement': {
                'overall_rate': engagement_rate,
                'by_sentiment': sentiment_engagement
            },
            'engagement_velocity': engagement_velocity
        }

# Add project root directory to Python path
import sys
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

from src.ui.content_ideas_section import (
    display_content_ideas_section,
    display_content_performance_insights,
    display_idea_generation_controls
)
from src.analytics_manager import AnalyticsManager
from src.utils.test_data_generator import TestDataGenerator
from src.collectors.reddit_collector import RedditCollector
from src.config.config import load_config
from src.api.api_manager import APIManager
from src.social_media_collector import SocialMediaCollector

# Load environment variables
dotenv_path = os.path.join(root_dir, '.env')
load_dotenv(dotenv_path)

# Configure Streamlit page
st.set_page_config(
    page_title="EDGLRD Analytics",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items=None,
    page_icon="📊",
)

# Initialize managers and collectors
analytics_manager = AnalyticsManager()
test_data_generator = TestDataGenerator()
api_manager = APIManager()

async def collect_reddit_data():
    """Collect sample Reddit data for demonstration"""
    try:
        # Sample data structure
        data = {
            'total_posts': 850,
            'edglrd_mentions': 125,
            'avg_score': 5.2,
            'engagement_patterns': {
                'hourly': {'morning': 30, 'afternoon': 45, 'evening': 25},
                'daily': {'weekday': 75, 'weekend': 25}
            },
            'top_posts': [
                {
                    'text': 'Just got my EDGLRD merch and it\'s amazing! 🔥',
                    'score': 245,
                    'sentiment': 'positive',
                    'author': 'reddit_user1',
                    'created_utc': time.time() - 3600
                },
                {
                    'text': 'The new EDGLRD collection is fire',
                    'score': 189,
                    'sentiment': 'positive',
                    'author': 'reddit_user2',
                    'created_utc': time.time() - 7200
                },
                {
                    'text': 'EDGLRD quality never disappoints',
                    'score': 156,
                    'sentiment': 'positive',
                    'author': 'reddit_user3',
                    'created_utc': time.time() - 10800
                },
                {
                    'text': 'Waiting for restock of the black hoodie',
                    'score': 134,
                    'sentiment': 'neutral',
                    'author': 'reddit_user4',
                    'created_utc': time.time() - 14400
                },
                {
                    'text': 'Anyone else loving the new designs?',
                    'score': 122,
                    'sentiment': 'positive',
                    'author': 'reddit_user5',
                    'created_utc': time.time() - 18000
                }
            ],
            'comments': pd.DataFrame({
                'text': [
                    'Love the new EDGLRD drop!',
                    'When is the next release?',
                    'The quality is amazing',
                    'Shipping was super fast',
                    'Need more colors!'
                ],
                'score': [45, 32, 28, 25, 20],
                'sentiment': ['positive', 'neutral', 'positive', 'positive', 'neutral'],
                'author': ['user1', 'user2', 'user3', 'user4', 'user5'],
                'created_utc': [
                    time.time() - 3600,
                    time.time() - 7200,
                    time.time() - 10800,
                    time.time() - 14400,
                    time.time() - 18000
                ]
            })
        }
        return data
    except Exception as e:
        st.error(f"Error collecting Reddit data: {str(e)}")
        return None

# Initialize collectors
@st.cache_resource
def init_collectors():
    """Initialize data collectors"""
    collectors = {
        'reddit': RedditCollector(),
        'social_media': SocialMediaCollector()
    }
    return collectors

collectors = init_collectors()

# Initialize session state
if 'reddit_collector' not in st.session_state:
    try:
        reddit_collector = RedditCollector()
        st.session_state.reddit_collector = reddit_collector
        st.session_state.reddit_data = None
        st.session_state.reddit_initialized = True
    except Exception as e:
        st.error(f"Error initializing Reddit collector: {str(e)}")
        st.session_state.reddit_collector = None
        st.session_state.reddit_initialized = False

# Initialize theme in session state
if 'theme' not in st.session_state:
    st.session_state.theme = "Light"  # Default theme

# Initialize session state for content ideas and platform selection
if 'content_ideas' not in st.session_state:
    st.session_state.content_ideas = {}
if 'selected_platform' not in st.session_state:
    st.session_state.selected_platform = "All Platforms"
if 'regenerate_ideas' not in st.session_state:
    st.session_state.regenerate_ideas = False

def get_server_url():
    """Get the server URL based on how the dashboard is being accessed"""
    urls_to_try = [
        "http://localhost:5000",  # Local development
        "http://127.0.0.1:5000",  # Alternative localhost
        "http://0.0.0.0:5000"     # All network interfaces
    ]
    
    for url in urls_to_try:
        try:
            response = requests.get(f"{url}/health", timeout=1)
            if response.status_code == 200:
                st.success(f"Connected to server at {url}")
                return url
        except Exception:
            continue
    
    st.error("Could not connect to server. Make sure the server is running.")
    return "http://localhost:5000"  # Default to localhost

# Use the dynamic server URL
SERVER_URL = get_server_url()

# Display server connection status
try:
    response = requests.get(f"{SERVER_URL}/health")
    if response.status_code == 200:
        st.success(f"Connected to server at {SERVER_URL}")
    else:
        st.error(f"Server error: Status code {response.status_code}")
except Exception as e:
    st.error(f"Could not connect to server at {SERVER_URL}. Make sure the server is running on the WiFi computer (192.168.1.185).")

def generate_and_store_ideas():
    """Generate new content ideas and store them"""
    try:
        response = requests.post(f"{SERVER_URL}/api/content/ideas")
        
        if response.status_code == 200:
            st.session_state.content_ideas = response.json()
            return True
        else:
            st.error("Failed to generate ideas. Please try again.")
            return False
    except Exception as e:
        st.error("Error connecting to the server. Please try again later.")
        return False

def load_stored_ideas():
    """Load previously stored content ideas"""
    try:
        response = requests.get(f"{SERVER_URL}/api/content/ideas")
        if response.status_code == 200:
            st.session_state.content_ideas = response.json()
    except Exception as e:
        st.error(f"Error loading ideas: {str(e)}")

# Sidebar
with st.sidebar:
    st.title("📊 Analytics Controls")
    
    # Platform selector
    available_platforms = ["All Platforms", "Instagram", "Twitter", "Reddit", "TikTok", "YouTube"]
    st.session_state.selected_platform = st.selectbox(
        "Select Platform",
        available_platforms,
        index=available_platforms.index(st.session_state.get('selected_platform', 'All Platforms'))
    )

    # Theme selector
    st.session_state.theme = st.selectbox(
        "Choose Theme",
        options=["Light", "Dark"],
        index=0 if st.session_state.theme == "Light" else 1
    )
    
    st.divider()
    
    # Add generate ideas button
    if st.button("🎨 Generate Content Ideas"):
        with st.spinner("Generating fresh content ideas..."):
            if generate_and_store_ideas():
                st.success("New content ideas generated!")
            else:
                st.error("Failed to generate new ideas")

    # Add social media controls
    st.subheader("Social Media Analysis")
    query = st.text_input("Search Query/Username", "")
    days_back = st.slider("Days to Analyze", 1, 30, 7)
    
    if st.button("Fetch Social Media Data"):
        with st.spinner("Collecting data from social media platforms..."):
            try:
                # Collect data from all platforms
                social_data = asyncio.run(
                    collectors['social_media'].collect_all_platforms(
                        query=query,
                        username=query,
                        days_back=days_back
                    )
                )
                
                # Generate summary
                summary = collectors['social_media'].generate_summary(social_data)
                
                # Store in session state
                st.session_state.social_data = social_data
                st.session_state.social_summary = summary
                
                st.success("Data collected successfully!")
            except Exception as e:
                st.error(f"Error collecting data: {str(e)}")

# Main dashboard layout
st.title("EDGLRD Social Media Analytics")

# Create main tabs
main_tabs = st.tabs(["📊 Performance", "💡 Content Ideas", "👥 Audience Insights", "📱 Social Media Analysis"])

# Initialize data
with st.spinner('Loading analytics data...'):
    try:
        # Initialize analytics data dictionary
        analytics_data = {}
        
        # Get real or sample data based on API availability
        def get_platform_data(platform: str) -> Dict:
            """Get real or sample data based on API availability"""
            try:
                # Try to get real data from APIs
                data = api_manager.get_platform_data(platform)
                if 'error' not in data:
                    return data
                    
                # Fallback to sample data if API fails
                print(f"Using sample data for {platform} due to API error: {data['error']}")
                return get_sample_data()[platform]
            except Exception as e:
                print(f"Error getting data for {platform}: {str(e)}")
                return get_sample_data()[platform]

        # Get sample data for all platforms
        sample_data = {
            'Instagram': {
                'metrics': {
                    'followers': 15000,
                    'engagement_rate': 3.2,
                    'posts': 450,
                    'likes': 25000,
                    'comments': 1200
                },
                'growth_trends': {
                    'dates': [str(datetime.now() - timedelta(days=x)) for x in range(30, 0, -1)],
                    'followers': [random.randint(14000, 15000) for _ in range(30)],
                    'engagement': [random.uniform(2.8, 3.5) for _ in range(30)]
                },
                'engagement_patterns': {
                    'hourly': {str(i): random.uniform(1, 5) for i in range(24)},
                    'daily': {'Weekday': 3.8, 'Weekend': 4.2}
                },
                'top_posts': [
                    {'type': 'image', 'likes': 2500, 'comments': 150, 'engagement_rate': 4.5},
                    {'type': 'video', 'likes': 3000, 'comments': 200, 'engagement_rate': 5.2},
                    {'type': 'carousel', 'likes': 2800, 'comments': 180, 'engagement_rate': 4.8}
                ],
                'optimal_times': {
                    'weekday': ['09:00', '12:00', '17:00'],
                    'weekend': ['11:00', '15:00', '20:00']
                }
            },
            'Twitter': {
                'metrics': {
                    'followers': 8500,
                    'engagement_rate': 3.2,
                    'posts': 1200
                },
                'engagement_patterns': {
                    'hourly': {'morning': 30, 'afternoon': 40, 'evening': 30},
                    'daily': {'weekday': 70, 'weekend': 30}
                }
            },
            'TikTok': {
                'metrics': {
                    'followers': 25000,
                    'engagement_rate': 7.5,
                    'posts': 200
                },
                'engagement_patterns': {
                    'hourly': {'morning': 25, 'afternoon': 35, 'evening': 40},
                    'daily': {'weekday': 60, 'weekend': 40}
                }
            },
            'YouTube': {
                'metrics': {
                    'followers': 5000,
                    'engagement_rate': 6.1,
                    'posts': 85
                },
                'engagement_patterns': {
                    'hourly': {'morning': 20, 'afternoon': 30, 'evening': 50},
                    'daily': {'weekday': 55, 'weekend': 45}
                }
            },
            'Reddit': {
                'metrics': {
                    'followers': 12000,
                    'engagement_rate': 5.5,
                    'posts': 800
                },
                'engagement_patterns': {
                    'hourly': {'morning': 30, 'afternoon': 35, 'evening': 35},
                    'daily': {'weekday': 60, 'weekend': 40}
                }
            }
        }
        
        # Merge sample data with Reddit data
        analytics_data.update(sample_data)
        
        # If no platform is selected, default to the first available one
        if not st.session_state.get('selected_platform') and analytics_data:
            st.session_state.selected_platform = list(analytics_data.keys())[0]
            
        if st.session_state.selected_platform in analytics_data:
            platform_data = analytics_data[st.session_state.selected_platform]
            
            # Display Analytics Section
            st.header(f"{st.session_state.selected_platform} Analytics")
            
            # Display platform metrics
            if st.session_state.selected_platform == "All Platforms":
                # Calculate aggregated metrics across all platforms
                total_followers = sum(platform_data['metrics']['followers'] for platform_data in analytics_data.values())
                avg_engagement_rate = sum(platform_data['metrics']['engagement_rate'] for platform_data in analytics_data.values()) / len(analytics_data)
                total_posts = sum(platform_data['metrics']['posts'] for platform_data in analytics_data.values())
                
                # Display aggregated metrics
                metrics_cols = st.columns(4)
                with metrics_cols[0]:
                    st.metric("Total Followers", total_followers)
                with metrics_cols[1]:
                    st.metric("Avg Engagement Rate", f"{avg_engagement_rate:.1f}%")
                with metrics_cols[2]:
                    st.metric("Total Posts", total_posts)
                with metrics_cols[3]:
                    st.metric("Active Platforms", len(analytics_data))
            elif st.session_state.selected_platform in analytics_data:
                platform_data = analytics_data[st.session_state.selected_platform]
                
                # Display platform metrics
                metrics_cols = st.columns(4)
                with metrics_cols[0]:
                    st.metric("Followers", platform_data['metrics']['followers'])
                with metrics_cols[1]:
                    st.metric("Engagement Rate", f"{platform_data['metrics']['engagement_rate']}%")
                with metrics_cols[2]:
                    st.metric("Total Posts", platform_data['metrics']['posts'])
                with metrics_cols[3]:
                    st.metric("Platform", st.session_state.selected_platform)
            
            # Display engagement patterns for other platforms
            st.subheader("Engagement Patterns")
            fig = plot_engagement_patterns(platform_data['engagement_patterns'])
            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f'Error loading analytics data: {str(e)}')
        st.stop()

# Function definitions
def analyze_comments(comments_data: pd.DataFrame) -> Dict:
    """
    Analyze comments using machine learning and sentiment analysis
    
    Args:
        comments_data: DataFrame containing comment data
        
    Returns:
        Dict containing analysis results
    """
    # Initialize analyzers
    sentiment_analyzer = SentimentAnalyzer(method='textblob')
    engagement_analyzer = EngagementAnalyzer()
    
    # Analyze sentiment
    comments_with_sentiment = sentiment_analyzer.analyze_dataframe(comments_data, 'text')
    
    # Convert created_utc to datetime if it exists
    if 'created_utc' in comments_with_sentiment.columns:
        comments_with_sentiment['timestamp'] = pd.to_datetime(comments_with_sentiment['created_utc'], unit='s')
    else:
        comments_with_sentiment['timestamp'] = pd.Timestamp.now()  # Default timestamp
    
    # Get engagement metrics
    engagement_metrics = engagement_analyzer.get_engagement_summary(comments_with_sentiment)
    
    # Calculate aggregate statistics
    sentiment_stats = {
        'overall_sentiment': comments_with_sentiment['sentiment'].value_counts().to_dict(),
        'avg_sentiment_score': comments_with_sentiment['score'].mean()
    }
    
    # Add time-based sentiment trends if we have timestamps
    if 'timestamp' in comments_with_sentiment.columns:
        # Group by day and calculate mean sentiment
        daily_sentiment = comments_with_sentiment.groupby(comments_with_sentiment['timestamp'].dt.date)['score'].mean()
        sentiment_stats['sentiment_trends'] = daily_sentiment.to_dict()
    else:
        sentiment_stats['sentiment_trends'] = {}
    
    # Identify key topics and patterns
    topic_patterns = {
        'common_topics': analyze_topics(comments_with_sentiment['text']),
        'engagement_by_topic': analyze_topic_engagement(comments_with_sentiment)
    }
    
    return {
        'sentiment_analysis': sentiment_stats,
        'engagement_metrics': engagement_metrics,
        'topic_analysis': topic_patterns
    }

def display_comment_analysis(comments_data: pd.DataFrame):
    """Display comment analysis results in the dashboard"""
    if comments_data.empty:
        st.warning("No comment data available for analysis")
        return
        
    # Perform analysis
    analysis_results = analyze_comments(comments_data)
    
    # Display sentiment overview
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Overall Sentiment",
            f"{analysis_results['sentiment_analysis']['avg_sentiment_score']:.2f}",
            "Based on comment analysis"
        )
        
    with col2:
        sentiment_dist = analysis_results['sentiment_analysis']['overall_sentiment']
        total_comments = sum(sentiment_dist.values()) if sentiment_dist else 1
        positive_rate = sentiment_dist.get('positive', 0) / total_comments if total_comments > 0 else 0
        st.metric(
            "Positive Comments",
            f"{positive_rate:.1%}"
        )
        
    with col3:
        engagement = analysis_results['engagement_metrics']['contextual_engagement']
        st.metric(
            "Engagement Rate",
            f"{engagement['overall_rate']:.1%}"
        )
    
    # Display detailed analysis
    tabs = st.tabs(["Sentiment Analysis", "Topic Insights", "Engagement Patterns"])
    
    with tabs[0]:
        st.subheader("Sentiment Analysis")
        fig = plot_sentiment_trends(analysis_results['sentiment_analysis']['sentiment_trends'])
        st.plotly_chart(fig, use_container_width=True)
        
    with tabs[1]:
        st.subheader("Key Topics")
        topics = analysis_results['topic_analysis']['common_topics']
        for topic, score in topics.items():
            st.progress(score, text=topic)
            
    with tabs[2]:
        st.subheader("Engagement Patterns")
        patterns = analysis_results['engagement_metrics']['engagement_velocity']
        fig = plot_engagement_patterns(patterns)
        st.plotly_chart(fig, use_container_width=True)

def analyze_topics(texts: pd.Series) -> Dict[str, float]:
    """Extract and score key topics from texts"""
    # Implement topic extraction (placeholder for now)
    return {'Topic 1': 0.8, 'Topic 2': 0.6, 'Topic 3': 0.4}

def analyze_topic_engagement(df: pd.DataFrame) -> Dict[str, float]:
    """Analyze engagement levels for different topics"""
    # Implement topic engagement analysis (placeholder for now)
    return {'Topic 1': 0.75, 'Topic 2': 0.45, 'Topic 3': 0.3}

def plot_sentiment_trends(trends: Dict) -> go.Figure:
    """Create visualization for sentiment trends"""
    fig = go.Figure()
    dates = list(trends.keys())
    scores = list(trends.values())
    
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=scores,
            mode='lines+markers',
            name='Sentiment Score',
            line=dict(color='#1f77b4')
        )
    )
    
    fig.update_layout(
        title='Sentiment Trends Over Time',
        xaxis_title='Date',
        yaxis_title='Sentiment Score',
        hovermode='x'
    )
    
    return fig

def display_audience_insights(platform_data: Dict):
    """Display comprehensive audience insights including demographics, active times, interests, and growth"""
    st.subheader("👥 Audience Insights")
    
    # Create tabs for different insight categories
    demo_tab, timing_tab, interests_tab, growth_tab = st.tabs([
        "Demographics", "Active Times", "Interests & Interactions", "Growth Metrics"
    ])
    
    with demo_tab:
        col1, col2 = st.columns(2)
        with col1:
            # Age Distribution
            demographics_data = platform_data.get('demographics', {
                'age_distribution': {
                    'Age Group': ['18-24', '25-34', '35-44', '45-54', '55+'],
                    'Percentage': [30, 35, 20, 10, 5]
                }
            })
            
            age_df = pd.DataFrame(demographics_data['age_distribution'])
            fig_age = px.pie(age_df, values='Percentage', names='Age Group',
                         title='Audience Age Distribution',
                         color_discrete_sequence=px.colors.qualitative.Set3)
            st.plotly_chart(fig_age, use_container_width=True)
        
        with col2:
            # Gender Distribution
            gender_data = platform_data.get('demographics', {
                'gender_distribution': {
                    'Gender': ['Female', 'Male', 'Other'],
                    'Percentage': [48, 47, 5]
                }
            })
            gender_df = pd.DataFrame(gender_data['gender_distribution'])
            fig_gender = px.pie(gender_df, values='Percentage', names='Gender',
                            title='Gender Distribution',
                            color_discrete_sequence=px.colors.qualitative.Set3)
            st.plotly_chart(fig_gender, use_container_width=True)
    
    with timing_tab:
        col1, col2 = st.columns(2)
        with col1:
            # Daily Active Times
            active_times = platform_data.get('active_times', {
                'daily': {
                    'Hour': list(range(24)),
                    'Activity': [random.randint(50, 100) for _ in range(24)]
                }
            })
            daily_df = pd.DataFrame(active_times['daily'])
            fig_daily = px.line(daily_df, x='Hour', y='Activity',
                            title='Daily Activity Pattern',
                            labels={'Activity': 'Engagement Level'})
            st.plotly_chart(fig_daily, use_container_width=True)
        
        with col2:
            # Weekly Active Times
            weekly_data = platform_data.get('active_times', {
                'weekly': {
                    'Day': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                    'Activity': [random.randint(60, 100) for _ in range(7)]
                }
            })
            weekly_df = pd.DataFrame(weekly_data['weekly'])
            fig_weekly = px.bar(weekly_df, x='Day', y='Activity',
                             title='Weekly Activity Pattern',
                             labels={'Activity': 'Engagement Level'})
            st.plotly_chart(fig_weekly, use_container_width=True)
    
    with interests_tab:
        col1, col2 = st.columns(2)
        with col1:
            # Top Interests
            interests_data = platform_data.get('interests', {
                'categories': ['Technology', 'Entertainment', 'Sports', 'Fashion', 'Food'],
                'scores': [85, 72, 68, 55, 45]
            })
            interests_df = pd.DataFrame({
                'Category': interests_data['categories'],
                'Score': interests_data['scores']
            })
            fig_interests = px.bar(interests_df, x='Category', y='Score',
                                title='Audience Interests',
                                color='Score',
                                color_continuous_scale='Viridis')
            st.plotly_chart(fig_interests, use_container_width=True)
        
        with col2:
            # Age Group Interactions
            interactions_data = platform_data.get('age_interactions', {
                'age_groups': ['18-24', '25-34', '35-44', '45-54', '55+'],
                'engagement_rate': [8.5, 7.2, 6.8, 5.5, 4.5]
            })
            interactions_df = pd.DataFrame({
                'Age Group': interactions_data['age_groups'],
                'Engagement Rate': interactions_data['engagement_rate']
            })
            fig_interactions = px.bar(interactions_df, x='Age Group', y='Engagement Rate',
                                   title='Engagement Rate by Age Group',
                                   color='Engagement Rate',
                                   color_continuous_scale='Viridis')
            st.plotly_chart(fig_interactions, use_container_width=True)
    
    with growth_tab:
        # Follower Growth Trend
        growth_data = platform_data.get('follower_growth', {
            'dates': pd.date_range(end=pd.Timestamp.now(), periods=30).strftime('%Y-%m-%d').tolist(),
            'followers': [random.randint(1000, 1500) + i * 50 for i in range(30)]
        })
        growth_df = pd.DataFrame({
            'Date': growth_data['dates'],
            'Followers': growth_data['followers']
        })
        fig_growth = px.line(growth_df, x='Date', y='Followers',
                          title='Follower Growth Trend',
                          labels={'Followers': 'Total Followers'})
        fig_growth.update_xaxes(tickangle=45)
        st.plotly_chart(fig_growth, use_container_width=True)
        
        # Growth Statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            growth_rate = ((growth_df['Followers'].iloc[-1] - growth_df['Followers'].iloc[0]) / 
                         growth_df['Followers'].iloc[0] * 100)
            st.metric("30-Day Growth Rate", f"{growth_rate:.1f}%")
        with col2:
            avg_daily_growth = (growth_df['Followers'].diff().mean())
            st.metric("Avg. Daily New Followers", f"{int(avg_daily_growth)}")
        with col3:
            total_followers = growth_df['Followers'].iloc[-1]
            st.metric("Total Followers", f"{total_followers:,}")

def display_video_metrics(platform_data: Dict):
    """Display comprehensive video metrics including behavioral patterns, recurring views, and engagement loyalty"""
    st.header("📊 Video Performance Metrics")
    
    if not platform_data:
        st.warning("No video data available for analysis")
        return
        
    # Get video metrics data
    behavioral_patterns = platform_data.get('behavioral_patterns', {})
    recurring_views = platform_data.get('recurring_views', {})
    engagement_loyalty = platform_data.get('engagement_loyalty', {})
    
    # Create tabs for different metric categories
    metric_tabs = st.tabs(["Behavioral Patterns", "Recurring Views", "Engagement Loyalty"])
    
    # Behavioral Patterns Tab
    with metric_tabs[0]:
        st.subheader("👥 Viewer Behavioral Patterns")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # View patterns
            view_patterns = behavioral_patterns.get('view_patterns', {})
            if view_patterns:
                # Video length preference
                length_pref = view_patterns.get('video_length_preference', {})
                fig_length = px.pie(
                    values=list(length_pref.values()),
                    names=list(length_pref.keys()),
                    title="Views by Video Length"
                )
                st.plotly_chart(fig_length, use_container_width=True)
        
        with col2:
            # Peak viewing hours
            peak_hours = view_patterns.get('peak_hours', {})
            if peak_hours:
                fig_hours = px.bar(
                    x=list(peak_hours.keys()),
                    y=list(peak_hours.values()),
                    title="Peak Viewing Hours",
                    labels={'x': 'Hour of Day', 'y': 'Views'}
                )
                st.plotly_chart(fig_hours, use_container_width=True)
        
        # Engagement patterns
        engagement_patterns = behavioral_patterns.get('engagement_patterns', {})
        if engagement_patterns:
            st.subheader("Engagement Distribution")
            engagement_dist = engagement_patterns.get('engagement_rate_distribution', [])
            fig_engagement = px.histogram(
                engagement_dist,
                title="Engagement Rate Distribution",
                labels={'value': 'Engagement Rate (%)', 'count': 'Number of Videos'}
            )
            st.plotly_chart(fig_engagement, use_container_width=True)
    
    # Recurring Views Tab
    with metric_tabs[1]:
        st.subheader("🔄 Recurring Views Analysis")
        
        # Overall metrics
        total_views = recurring_views.get('total_views', 0)
        recurring_view_count = recurring_views.get('recurring_views', 0)
        recurring_percentage = recurring_views.get('recurring_percentage', 0)
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Views", f"{total_views:,}")
        col2.metric("Recurring Views", f"{recurring_view_count:,}")
        col3.metric("Recurring Percentage", f"{recurring_percentage:.1f}%")
        
        # Video-specific recurring views
        videos = recurring_views.get('videos', [])
        if videos:
            st.subheader("Recurring Views by Video")
            video_df = pd.DataFrame(videos)
            fig_videos = px.bar(
                video_df,
                x='title',
                y=['views', 'estimated_recurring'],
                title="Views Distribution",
                barmode='group',
                labels={'value': 'Count', 'variable': 'Type'}
            )
            st.plotly_chart(fig_videos, use_container_width=True)
    
    # Engagement Loyalty Tab
    with metric_tabs[2]:
        st.subheader("❤️ Engagement Loyalty Metrics")
        
        # Overall loyalty metrics
        overall_loyalty = engagement_loyalty.get('overall_loyalty', 0)
        engagement_consistency = engagement_loyalty.get('engagement_consistency', 0)
        
        col1, col2 = st.columns(2)
        col1.metric("Overall Loyalty Score", f"{overall_loyalty:.1f}")
        col2.metric("Engagement Consistency", f"{engagement_consistency:.1f}%")
        
        # Video-specific loyalty metrics
        videos = engagement_loyalty.get('videos', [])
        if videos:
            st.subheader("Engagement Loyalty by Video")
            video_df = pd.DataFrame(videos)
            fig_loyalty = px.scatter(
                video_df,
                x='views',
                y='engagement_rate',
                title="Views vs Engagement Rate",
                labels={'views': 'Views', 'engagement_rate': 'Engagement Rate (%)'}
            )
            st.plotly_chart(fig_loyalty, use_container_width=True)

# Main dashboard content
with main_tabs[0]:
    # Display the performance hub
    def display_performance_hub(data: Dict):
        """Display the overall social media performance hub with investor-focused metrics"""
        
        st.header("📊 Performance Overview", anchor=False)
        
        # KPI Metrics Row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_audience = data.get('subscriber_count', 0)
            growth_rate = data.get('growth_rate', 0)
            st.metric(
                "Total Audience",
                f"{total_audience:,}",
                f"{growth_rate:.1f}%",
                help="Total subscriber count across platforms"
            )
        
        with col2:
            engagement_metrics = data.get('engagement_metrics', {})
            engagement_rate = engagement_metrics.get('engagement_rate', 0)
            prev_engagement = data.get('previous_engagement_rate', 0)
            st.metric(
                "Engagement Rate",
                f"{engagement_rate:.1f}%",
                f"{engagement_rate - prev_engagement:.1f}%",
                help="Average engagement rate across all content"
            )
        
        with col3:
            conversion_metrics = data.get('conversion_metrics', {})
            conversion_rate = conversion_metrics.get('conversion_rate', 0)
            prev_conversion = conversion_metrics.get('previous_conversion_rate', 0)
            st.metric(
                "Conversion Rate",
                f"{conversion_rate:.1f}%",
                f"{conversion_rate - prev_conversion:.1f}%",
                help="Estimated conversion rate from engagement to action"
            )
        
        with col4:
            content_performance = data.get('content_performance', {})
            viral_posts = len(content_performance.get('viral_posts', []))
            prev_viral = content_performance.get('previous_viral_posts', 0)
            st.metric(
                "Viral Content",
                viral_posts,
                f"+{viral_posts - prev_viral}",
                help="Number of posts achieving viral status"
            )
        
        # Platform Performance
        st.subheader("📱 Platform Performance")
        
        # Extract platform-specific metrics
        platforms = ['Instagram', 'Twitter', 'TikTok', 'YouTube', 'Reddit']
        platform_metrics = []
        
        for platform in platforms:
            if platform in data and isinstance(data[platform], dict):
                metrics = data[platform].get('metrics', {})
                platform_metrics.append({
                    'Platform': platform,
                    'Followers': metrics.get('followers', 0),
                    'Engagement Rate': metrics.get('engagement_rate', 0),
                    'Revenue': metrics.get('revenue', 0)
                })
        
        if platform_metrics:
            # Create DataFrame for platform metrics
            df_platforms = pd.DataFrame(platform_metrics)
            
            # Create subplots for platform metrics
            fig = go.Figure()
            
            # Add followers bar
            fig.add_trace(go.Bar(
                name='Followers',
                x=df_platforms['Platform'],
                y=df_platforms['Followers'],
                text=df_platforms['Followers'].apply(lambda x: f'{x:,}'),
                textposition='auto',
                yaxis='y1',
                marker_color='#4CAF50'
            ))
            
            # Add engagement rate line
            fig.add_trace(go.Scatter(
                name='Engagement Rate',
                x=df_platforms['Platform'],
                y=df_platforms['Engagement Rate'],
                text=df_platforms['Engagement Rate'].apply(lambda x: f'{x:.1f}%'),
                mode='lines+markers+text',
                textposition='top center',
                yaxis='y2',
                line=dict(color='#2196F3', width=3),
                marker=dict(size=10)
            ))
            
            # Add revenue bar
            fig.add_trace(go.Bar(
                name='Revenue',
                x=df_platforms['Platform'],
                y=df_platforms['Revenue'],
                text=df_platforms['Revenue'].apply(lambda x: f'${x:,}'),
                textposition='auto',
                yaxis='y3',
                marker_color='#FFC107'
            ))
            
            # Update layout with multiple y-axes
            fig.update_layout(
                title='Platform Performance Comparison',
                template='plotly_white',
                showlegend=True,
                hovermode='x unified',
                barmode='group',
                plot_bgcolor='white',
                yaxis=dict(
                    title='Followers',
                    titlefont=dict(color='#4CAF50'),
                    tickfont=dict(color='#4CAF50'),
                    showgrid=True,
                    gridcolor='rgba(0,0,0,0.1)'
                ),
                yaxis2=dict(
                    title='Engagement Rate (%)',
                    titlefont=dict(color='#2196F3'),
                    tickfont=dict(color='#2196F3'),
                    anchor='free',
                    overlaying='y',
                    side='right',
                    position=1,
                    showgrid=False
                ),
                yaxis3=dict(
                    title='Revenue ($)',
                    titlefont=dict(color='#FFC107'),
                    tickfont=dict(color='#FFC107'),
                    anchor='free',
                    overlaying='y',
                    side='right',
                    position=0.85,
                    showgrid=False
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Growth Trends
        st.subheader("📈 Growth Trends")
        
        # Create growth trend chart
        if 'historical_metrics' in data:
            df = pd.DataFrame(data['historical_metrics'])
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            fig = px.line(df, x='timestamp', y=['subscriber_count', 'active_users'],
                         title='Audience Growth Over Time',
                         labels={'subscriber_count': 'Total Subscribers', 
                                'active_users': 'Active Users',
                                'timestamp': 'Date'},
                         template='plotly_white')
            fig.update_layout(
                legend_title_text='Metric',
                hovermode='x unified',
                plot_bgcolor='white'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Engagement Analysis
        st.subheader("🎯 Engagement Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Best performing content
            st.write("🏆 Top Performing Content")
            viral_posts = data.get('content_performance', {}).get('viral_posts', [])
            if viral_posts:
                for post in viral_posts[:3]:  # Show top 3
                    st.markdown(f"""
                        **{post['title']}**  
                        💬 {post['comments']:,} comments | ⬆️ {post['score']:,} engagements
                    """)
        
        with col2:
            # Best posting times
            st.write("⏰ Optimal Posting Times")
            best_times = data.get('content_performance', {}).get('best_posting_times', {})
            if best_times:
                times_df = pd.DataFrame(list(best_times.items()), columns=['Hour', 'Engagement'])
                times_df['Hour'] = pd.to_datetime(times_df['Hour'].apply(lambda x: f"2024-01-01 {x}:00")).dt.strftime('%I %p')
                fig = px.bar(times_df.nlargest(5, 'Engagement'), 
                            x='Hour', y='Engagement',
                            title='Best Times to Post',
                            template='plotly_white')
                st.plotly_chart(fig, use_container_width=True)

    display_performance_hub(analytics_data)
    
    # Display video metrics for video platforms
    if st.session_state.selected_platform in ['youtube', 'tiktok']:
        platform_data = analytics_data[st.session_state.selected_platform]
        display_video_metrics(platform_data)

with main_tabs[1]:
    # Content Ideas Section
    st.header("💡 Content Ideas Generator")
    
    # Add custom CSS for better styling
    st.markdown("""
        <style>
        .idea-card {
            background-color: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin: 1rem 0;
        }
        .idea-header {
            font-size: 1.2rem;
            font-weight: bold;
            margin-bottom: 1rem;
            color: #1f1f1f;
        }
        .idea-tag {
            display: inline-block;
            padding: 0.3rem 0.8rem;
            background-color: #f0f2f6;
            border-radius: 15px;
            margin: 0.2rem;
            font-size: 0.9rem;
        }
        .idea-section {
            background-color: #f8f9fa;
            padding: 1rem;
            border-radius: 5px;
            margin: 0.5rem 0;
        }
        .metric-card {
            background-color: #f8f9fa;
            padding: 1rem;
            border-radius: 5px;
            margin-bottom: 0.5rem;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Display content ideas
    if st.session_state.content_ideas:
        # Create tabs for different platforms
        platforms = list(st.session_state.content_ideas.keys())
        if platforms:
            tabs = st.tabs(platforms)
            
            for tab, platform in zip(tabs, platforms):
                with tab:
                    ideas = st.session_state.content_ideas[platform]
                    
                    for i, idea in enumerate(ideas, 1):
                        # Create a card for each idea
                        st.markdown(f"""
                            <div class="idea-card">
                                <div class="idea-header">
                                    💡 Content Idea #{i}
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        # Create two columns for content layout
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            # Display content type as a tag
                            if idea.get('content_type'):
                                st.markdown(f"""
                                    <div class="idea-tag">
                                        {idea['content_type']}
                                    </div>
                                """, unsafe_allow_html=True)
                            
                            # Display theme in a section
                            if idea.get('theme'):
                                st.markdown("""
                                    <div class="idea-section">
                                        <strong>Theme:</strong><br/>
                                        {theme}
                                    </div>
                                """.format(theme=idea['theme']), unsafe_allow_html=True)
                            
                            # Display description
                            if idea.get('description'):
                                st.markdown("""
                                    <div class="idea-section">
                                        <strong>Description:</strong><br/>
                                        {description}
                                    </div>
                                """.format(description=idea['description']), unsafe_allow_html=True)
                            
                            # Display key elements as tags
                            if idea.get('suggested_elements'):
                                st.markdown("<strong>Key Elements:</strong>", unsafe_allow_html=True)
                                elements_html = "".join([
                                    f'<div class="idea-tag">• {element}</div>'
                                    for element in idea['suggested_elements']
                                ])
                                st.markdown(elements_html, unsafe_allow_html=True)
                        
                        with col2:
                            # Display metrics in a clean card
                            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                            
                            if idea.get('best_posting_time'):
                                st.metric(
                                    "Best Time to Post",
                                    f"{idea['best_posting_time']:02d}:00"
                                )
                            
                            if idea.get('estimated_engagement'):
                                st.metric(
                                    "Estimated Engagement",
                                    f"{idea['estimated_engagement']:.1f}"
                                )
                            
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                            # Display hashtags as tags
                            if idea.get('hashtags'):
                                st.markdown("<strong>Suggested Hashtags:</strong>", unsafe_allow_html=True)
                                hashtags_html = "".join([
                                    f'<div class="idea-tag">#{tag}</div>'
                                    for tag in idea['hashtags']
                                ])
                                st.markdown(hashtags_html, unsafe_allow_html=True)
                        
                        # Add spacing between cards
                        st.markdown("<br/>", unsafe_allow_html=True)
    else:
        st.info("No content ideas generated yet. Click the 'Generate Content Ideas' button in the sidebar to get started!")
    
    # Display content performance insights if available
    if st.session_state.selected_platform == "All Platforms":
        # Combine engagement patterns from all platforms
        combined_patterns = {}
        for platform in analytics_data:
            platform_patterns = analytics_data[platform].get('engagement_patterns', {})
            for key, value in platform_patterns.items():
                if key not in combined_patterns:
                    combined_patterns[key] = value
                else:
                    # If the value is a dict, merge them
                    if isinstance(value, dict):
                        combined_patterns[key].update(value)
                    # If it's a list, extend it
                    elif isinstance(value, list):
                        combined_patterns[key].extend(value)
                    # Otherwise, take the average
                    else:
                        combined_patterns[key] = (combined_patterns[key] + value) / 2
        if combined_patterns:
            display_content_performance_insights(combined_patterns)
        else:
            st.info("No content performance data available across platforms")
    elif st.session_state.selected_platform in analytics_data:
        platform_data = analytics_data[st.session_state.selected_platform]
        display_content_performance_insights(platform_data.get('engagement_patterns', {}))
    else:
        st.info("No content performance data available for the selected platform")
    
    # Display comment analysis section
    st.markdown("---")
    if st.session_state.selected_platform == "All Platforms":
        # Show aggregated comment analysis for all platforms
        all_comments = []
        for platform in analytics_data:
            if 'comments_data' in analytics_data[platform]:
                all_comments.append(analytics_data[platform]['comments_data'])
        if all_comments:
            combined_comments = pd.concat(all_comments, ignore_index=True)
            display_comment_analysis(combined_comments)
        else:
            st.info("No comment data available across platforms")
    elif 'comments_data' in analytics_data[st.session_state.selected_platform]:
        display_comment_analysis(analytics_data[st.session_state.selected_platform]['comments_data'])
    else:
        st.info("No comment data available for the selected platform")

with main_tabs[2]:
    if st.session_state.selected_platform == "All Platforms":
        st.header("Combined Audience Insights")
        # Show combined insights from all platforms
        combined_data = {
            'metrics': {
                'followers': sum(platform_data['metrics']['followers'] for platform_data in analytics_data.values()),
                'engagement_rate': sum(platform_data['metrics']['engagement_rate'] for platform_data in analytics_data.values()) / len(analytics_data),
                'posts': sum(platform_data['metrics']['posts'] for platform_data in analytics_data.values())
            },
            'engagement_patterns': {}
        }
        
        # Combine engagement patterns
        for platform_data in analytics_data.values():
            patterns = platform_data.get('engagement_patterns', {})
            for key, value in patterns.items():
                if key not in combined_data['engagement_patterns']:
                    combined_data['engagement_patterns'][key] = value
                else:
                    if isinstance(value, dict):
                        for subkey, subvalue in value.items():
                            if subkey in combined_data['engagement_patterns'][key]:
                                combined_data['engagement_patterns'][key][subkey] = (combined_data['engagement_patterns'][key][subkey] + subvalue) / 2
                            else:
                                combined_data['engagement_patterns'][key][subkey] = subvalue
                    else:
                        combined_data['engagement_patterns'][key] = (combined_data['engagement_patterns'][key] + value) / 2
        
        display_audience_insights(combined_data)
    elif st.session_state.selected_platform in analytics_data:
        platform_data = analytics_data[st.session_state.selected_platform]
        display_audience_insights(platform_data)
    else:
        st.info("No audience insights available for the selected platform")

with main_tabs[3]:
    st.header("📱 Social Media Analytics Dashboard")
    
    if 'social_data' in st.session_state and 'social_summary' in st.session_state:
        # Platform Selection
        platform = st.selectbox(
            "Select Platform",
            ["All Platforms", "Instagram", "Twitter", "TikTok"]
        )
        
        # Date Range
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date")
        with col2:
            end_date = st.date_input("End Date")
        
        # Overview Metrics
        st.subheader("📈 Overview")
        overview_cols = st.columns(4)
        
        with overview_cols[0]:
            st.metric(
                "Total Reach",
                format_number(st.session_state.social_summary.get('total_reach', 0)),
                help="Total number of unique users who saw your content"
            )
        with overview_cols[1]:
            st.metric(
                "Engagement Rate",
                f"{st.session_state.social_summary.get('engagement_rate', 0):.2f}%",
                help="Average engagement rate across all content"
            )
        with overview_cols[2]:
            st.metric(
                "Brand Sentiment",
                f"{st.session_state.social_summary.get('positive_sentiment', 0):.1f}%",
                help="Percentage of positive sentiment mentions"
            )
        with overview_cols[3]:
            st.metric(
                "Response Rate",
                f"{st.session_state.social_summary.get('response_rate', 0):.1f}%",
                help="Percentage of comments/mentions responded to"
            )
        
        # Display platform-specific metrics
        if platform != "All Platforms":
            platform_data = st.session_state.social_data.get(platform.lower(), {})
            if platform_data:
                display_social_media_metrics(platform_data)
        else:
            # Combined metrics across platforms
            combined_data = {}
            for p, data in st.session_state.social_data.items():
                for key, value in data.items():
                    if key not in combined_data:
                        combined_data[key] = value
                    else:
                        # Combine metrics appropriately based on type
                        if isinstance(value, (int, float)):
                            combined_data[key] += value
                        elif isinstance(value, list):
                            combined_data[key].extend(value)
                        elif isinstance(value, dict):
                            combined_data[key].update(value)
            
            display_social_media_metrics(combined_data)
        
        # Recommendations
        st.subheader("💡 Strategic Recommendations")
        recommendations = generate_recommendations(st.session_state.social_summary)
        for i, rec in enumerate(recommendations, 1):
            st.markdown(f"{i}. {rec}")
    else:
        st.info("Use the sidebar controls to fetch social media data")

def format_number(num):
    """Format large numbers for display"""
    if num >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num/1_000:.1f}K"
    return str(num)

def generate_recommendations(summary: Dict) -> List[str]:
    """Generate strategic recommendations based on analytics"""
    recommendations = []
    
    # Engagement recommendations
    if summary.get('engagement_rate', 0) < 0.03:
        recommendations.append("Increase engagement by posting more interactive content (polls, questions, contests)")
    
    # Content timing
    best_times = summary.get('best_posting_times', [])
    if best_times:
        recommendations.append(f"Schedule posts during peak engagement times: {', '.join(best_times)}")
    
    # Content type optimization
    top_content = summary.get('top_performing_content_types', [])
    if top_content:
        recommendations.append(f"Focus on creating more {', '.join(top_content)} content")
    
    # Hashtag strategy
    if summary.get('hashtag_performance'):
        top_hashtags = summary['hashtag_performance'][:3]
        recommendations.append(f"Utilize high-performing hashtags: {', '.join(top_hashtags)}")
    
    # Audience growth
    if summary.get('audience_growth_rate', 0) < 0.05:
        recommendations.append("Implement audience growth strategies: collaborations, contests, and targeted ads")
    
    # Sentiment improvement
    if summary.get('negative_sentiment_rate', 0) > 0.2:
        recommendations.append("Address negative sentiment by improving response time and customer service")
    
    return recommendations

def display_social_media_metrics(platform_data: Dict):
    """Display comprehensive social media KPIs and metrics"""
    
    # Engagement Overview
    st.subheader("📊 Engagement Overview")
    metrics_cols = st.columns(4)
    
    with metrics_cols[0]:
        st.metric(
            "Total Engagement Rate",
            f"{(platform_data.get('engagement_rate', 0) * 100):.2f}%",
            help="(Likes + Comments + Shares) / Total Followers"
        )
    with metrics_cols[1]:
        st.metric(
            "Avg Response Time",
            f"{platform_data.get('avg_response_time', 0):.1f}h",
            help="Average time to respond to comments/mentions"
        )
    with metrics_cols[2]:
        st.metric(
            "Audience Growth",
            f"{platform_data.get('audience_growth_rate', 0):.1f}%",
            help="Follower growth rate over the selected period"
        )
    with metrics_cols[3]:
        st.metric(
            "Brand Sentiment",
            f"{platform_data.get('positive_sentiment_rate', 0):.1f}%",
            help="Percentage of positive sentiment mentions"
        )

    # Content Performance
    st.subheader("📈 Content Performance")
    perf_cols = st.columns(2)
    
    with perf_cols[0]:
        # Best Performing Content
        st.markdown("### 🏆 Top Performing Content")
        top_posts = pd.DataFrame(platform_data.get('top_posts', []))
        if not top_posts.empty:
            st.dataframe(
                top_posts[['content_type', 'engagement_rate', 'impressions', 'reach']],
                hide_index=True
            )
    
    with perf_cols[1]:
        # Content Type Performance
        st.markdown("### 📱 Content Type Analysis")
        content_performance = pd.DataFrame(platform_data.get('content_type_performance', []))
        if not content_performance.empty:
            fig = px.bar(
                content_performance,
                x='content_type',
                y='engagement_rate',
                title='Engagement by Content Type'
            )
            st.plotly_chart(fig, use_container_width=True)

    # Audience Insights
    st.subheader("👥 Audience Insights")
    audience_cols = st.columns(2)
    
    with audience_cols[0]:
        # Demographics
        st.markdown("### 📊 Demographics")
        demo_data = pd.DataFrame(platform_data.get('demographics', []))
        if not demo_data.empty:
            fig = px.pie(demo_data, values='percentage', names='category', title='Audience Demographics')
            st.plotly_chart(fig, use_container_width=True)
    
    with audience_cols[1]:
        # Active Times
        st.markdown("### ⏰ Best Times to Post")
        active_times = pd.DataFrame(platform_data.get('active_times', []))
        if not active_times.empty:
            fig = px.line(
                active_times,
                x='hour',
                y='engagement',
                title='Hourly Engagement Pattern'
            )
            st.plotly_chart(fig, use_container_width=True)

    # Hashtag Performance
    st.subheader("🏷️ Hashtag Analysis")
    hashtag_cols = st.columns(2)
    
    with hashtag_cols[0]:
        # Top Hashtags
        st.markdown("### 🔝 Top Performing Hashtags")
        hashtags = pd.DataFrame(platform_data.get('hashtag_performance', []))
        if not hashtags.empty:
            st.dataframe(
                hashtags[['hashtag', 'reach', 'engagement_rate']],
                hide_index=True
            )
    
    with hashtag_cols[1]:
        # Hashtag Reach
        st.markdown("### 📢 Hashtag Reach")
        if not hashtags.empty:
            fig = px.bar(
                hashtags,
                x='hashtag',
                y='reach',
                title='Reach by Hashtag'
            )
            st.plotly_chart(fig, use_container_width=True)

    # Competitor Analysis
    st.subheader("🔍 Competitor Analysis")
    comp_cols = st.columns(2)
    
    with comp_cols[0]:
        # Competitor Metrics
        st.markdown("### 📊 Competitor Comparison")
        comp_data = pd.DataFrame(platform_data.get('competitor_metrics', []))
        if not comp_data.empty:
            st.dataframe(
                comp_data[['competitor', 'followers', 'engagement_rate', 'content_frequency']],
                hide_index=True
            )
    
    with comp_cols[1]:
        # Share of Voice
        st.markdown("### 📢 Share of Voice")
        if not comp_data.empty:
            fig = px.pie(
                comp_data,
                values='mentions',
                names='competitor',
                title='Share of Voice in Industry'
            )
            st.plotly_chart(fig, use_container_width=True)

    # Campaign Performance
    st.subheader("🎯 Campaign Performance")
    campaign_data = pd.DataFrame(platform_data.get('campaign_performance', []))
    if not campaign_data.empty:
        st.dataframe(
            campaign_data[[
                'campaign_name',
                'start_date',
                'end_date',
                'reach',
                'engagement_rate',
                'conversion_rate',
                'roi'
            ]],
            hide_index=True
        )

    # Content Calendar
    st.subheader("📅 Content Calendar")
    calendar_data = pd.DataFrame(platform_data.get('content_calendar', []))
    if not calendar_data.empty:
        st.dataframe(
            calendar_data[[
                'date',
                'content_type',
                'status',
                'target_audience',
                'expected_reach'
            ]],
            hide_index=True
        )

# Apply theme
if st.session_state.theme == "Dark":
    st.markdown("""
        <style>
        /* Dark theme styles */
        .stApp {
            background-color: #0E1117;
            color: #FAFAFA;
        }
        
        /* Metric styles */
        [data-testid="stMetric"] {
            background-color: #262730 !important;
            border: 1px solid #303030 !important;
            border-radius: 0.5rem !important;
            padding: 1rem !important;
            color: #FAFAFA !important;
        }
        
        [data-testid="stMetricLabel"] {
            color: #FAFAFA !important;
        }
        
        [data-testid="stMetricValue"] {
            color: #FAFAFA !important;
        }
        
        [data-testid="stMetricDelta"] {
            color: #0CBA6F !important;
        }
        
        [data-testid="stMetricDelta"] svg {
            fill: #0CBA6F !important;
        }

        /* Tab styles */
        button[data-baseweb="tab"] {
            color: #FAFAFA !important;
        }
        
        button[data-baseweb="tab"][aria-selected="true"] {
            color: #00D4FF !important;
            border-color: #00D4FF !important;
        }
        
        [data-testid="stTabContent"] {
            color: #FAFAFA !important;
        }

        /* Header styles */
        .main-header {
            color: #FAFAFA;
        }
        
        .platform-badge {
            background-color: #1E1E1E;
            border: 1px solid #303030;
            color: #00D4FF;
            padding: 0.5rem 1rem;
            border-radius: 0.5rem;
            font-size: 1.2rem;
            font-weight: 500;
        }

        /* Additional metric container styles */
        div[data-testid="metric-container"] {
            background-color: #262730 !important;
            border: 1px solid #303030 !important;
            border-radius: 0.5rem !important;
            padding: 1rem !important;
        }
        
        div[data-testid="metric-container"] > div {
            color: #FAFAFA !important;
        }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
        /* Light theme styles */
        .stApp {
            background-color: #FFFFFF;
            color: #31333F;
        }
        
        /* Metric styles */
        [data-testid="stMetric"] {
            background-color: #F8F9FA !important;
            border: 1px solid #E0E0E0 !important;
            border-radius: 0.5rem !important;
            padding: 1rem !important;
            color: #31333F !important;
        }
        
        [data-testid="stMetricLabel"] {
            color: #31333F !important;
        }
        
        [data-testid="stMetricValue"] {
            color: #31333F !important;
        }
        
        [data-testid="stMetricDelta"] {
            color: #0CBA6F !important;
        }
        
        [data-testid="stMetricDelta"] svg {
            fill: #0CBA6F !important;
        }

        /* Tab styles */
        button[data-baseweb="tab"] {
            color: #31333F !important;
        }
        
        button[data-baseweb="tab"][aria-selected="true"] {
            color: #0068C9 !important;
            border-color: #0068C9 !important;
        }
        
        [data-testid="stTabContent"] {
            color: #31333F !important;
        }

        /* Header styles */
        .main-header {
            color: #31333F;
        }
        
        .platform-badge {
            background-color: #F8F9FA;
            border: 1px solid #E0E0E0;
            color: #0068C9;
            padding: 0.5rem 1rem;
            border-radius: 0.5rem;
            font-size: 1.2rem;
            font-weight: 500;
        }

        /* Additional metric container styles */
        div[data-testid="metric-container"] {
            background-color: #F8F9FA !important;
            border: 1px solid #E0E0E0 !important;
            border-radius: 0.5rem !important;
            padding: 1rem !important;
        }
        
        div[data-testid="metric-container"] > div {
            color: #31333F !important;
        }
        </style>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(
    f"""
    <div style='text-align: center'>
        <p>EDGLRD Social Media Analytics Dashboard | Updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
    </div>
    """,
    unsafe_allow_html=True
)

if __name__ == "__main__":
    # The Streamlit CLI will handle running the app
    pass
