"""
Social Media Analytics Dashboard
Handles visualization of analytics data across all platforms
"""

from typing import Dict, List, Optional
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import logging

class AnalyticsDashboard:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.color_scheme = {
            'primary': '#1f77b4',
            'secondary': '#ff7f0e',
            'success': '#2ca02c',
            'danger': '#d62728'
        }
        
    def plot_audience_demographics(self, data: pd.DataFrame) -> go.Figure:
        """
        Create demographic visualization
        
        Args:
            data: DataFrame with demographic information
            
        Returns:
            Plotly figure object
        """
        try:
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Age Distribution', 'Gender Distribution', 
                              'Top Locations', 'Income Distribution')
            )
            
            # Age distribution
            fig.add_trace(
                go.Histogram(x=data['age'], name='Age',
                           marker_color=self.color_scheme['primary']),
                row=1, col=1
            )
            
            # Gender distribution
            gender_counts = data['gender'].value_counts()
            fig.add_trace(
                go.Pie(labels=gender_counts.index, values=gender_counts.values,
                      name='Gender'),
                row=1, col=2
            )
            
            # Location distribution
            location_counts = data['location'].value_counts().head(10)
            fig.add_trace(
                go.Bar(x=location_counts.index, y=location_counts.values,
                      name='Location', marker_color=self.color_scheme['secondary']),
                row=2, col=1
            )
            
            # Income distribution
            fig.add_trace(
                go.Box(y=data['income'], name='Income',
                      marker_color=self.color_scheme['primary']),
                row=2, col=2
            )
            
            fig.update_layout(height=800, title_text="Audience Demographics")
            return fig
            
        except Exception as e:
            self.logger.error(f"Error creating demographic visualization: {str(e)}")
            raise
            
    def plot_engagement_metrics(self, data: pd.DataFrame) -> go.Figure:
        """
        Create engagement visualization
        
        Args:
            data: DataFrame with engagement metrics
            
        Returns:
            Plotly figure object
        """
        try:
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Engagement Over Time', 'Engagement by Type',
                              'Sentiment Distribution', 'Peak Engagement Hours')
            )
            
            # Engagement over time
            fig.add_trace(
                go.Scatter(x=data['timestamp'], y=data['engagement_count'],
                          mode='lines', name='Engagement',
                          line=dict(color=self.color_scheme['primary'])),
                row=1, col=1
            )
            
            # Engagement by type
            engagement_types = data['engagement_type'].value_counts()
            fig.add_trace(
                go.Bar(x=engagement_types.index, y=engagement_types.values,
                      name='Engagement Types',
                      marker_color=self.color_scheme['secondary']),
                row=1, col=2
            )
            
            # Sentiment distribution
            sentiment_dist = data['sentiment'].value_counts()
            fig.add_trace(
                go.Pie(labels=sentiment_dist.index, values=sentiment_dist.values,
                      name='Sentiment'),
                row=2, col=1
            )
            
            # Peak hours
            hourly_engagement = data.groupby(data['timestamp'].dt.hour)['engagement_count'].mean()
            fig.add_trace(
                go.Bar(x=hourly_engagement.index, y=hourly_engagement.values,
                      name='Peak Hours',
                      marker_color=self.color_scheme['primary']),
                row=2, col=2
            )
            
            fig.update_layout(height=800, title_text="Engagement Metrics")
            return fig
            
        except Exception as e:
            self.logger.error(f"Error creating engagement visualization: {str(e)}")
            raise
            
    def plot_content_performance(self, data: pd.DataFrame) -> go.Figure:
        """
        Create content performance visualization
        
        Args:
            data: DataFrame with content performance metrics
            
        Returns:
            Plotly figure object
        """
        try:
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Content Type Performance', 'Engagement by Time',
                              'Top Performing Content', 'Content Journey')
            )
            
            # Content type performance
            type_performance = data.groupby('content_type')['engagement_count'].mean()
            fig.add_trace(
                go.Bar(x=type_performance.index, y=type_performance.values,
                      name='Content Types',
                      marker_color=self.color_scheme['primary']),
                row=1, col=1
            )
            
            # Engagement by time
            fig.add_trace(
                go.Scatter(x=data['timestamp'], y=data['engagement_count'],
                          mode='lines', name='Engagement',
                          line=dict(color=self.color_scheme['secondary'])),
                row=1, col=2
            )
            
            # Top performing content
            top_content = data.nlargest(10, 'engagement_count')
            fig.add_trace(
                go.Bar(x=top_content['content_id'], y=top_content['engagement_count'],
                      name='Top Content',
                      marker_color=self.color_scheme['success']),
                row=2, col=1
            )
            
            # Content journey
            journey_data = data.groupby('content_sequence')['user_count'].mean()
            fig.add_trace(
                go.Funnel(y=journey_data.index, x=journey_data.values,
                         name='Content Journey'),
                row=2, col=2
            )
            
            fig.update_layout(height=800, title_text="Content Performance")
            return fig
            
        except Exception as e:
            self.logger.error(f"Error creating content performance visualization: {str(e)}")
            raise
            
    def plot_platform_comparison(self, data: Dict[str, pd.DataFrame]) -> go.Figure:
        """
        Create cross-platform comparison visualization
        
        Args:
            data: Dict of DataFrames with platform-specific metrics
            
        Returns:
            Plotly figure object
        """
        try:
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Engagement by Platform', 'Growth Rate Comparison',
                              'Content Performance', 'Audience Size')
            )
            
            platforms = list(data.keys())
            colors = [self.color_scheme[color] for color in self.color_scheme.keys()]
            
            # Engagement by platform
            platform_engagement = {platform: df['engagement_count'].mean() 
                                for platform, df in data.items()}
            fig.add_trace(
                go.Bar(x=list(platform_engagement.keys()),
                      y=list(platform_engagement.values()),
                      name='Platform Engagement',
                      marker_color=colors[0]),
                row=1, col=1
            )
            
            # Growth rate comparison
            growth_rates = {platform: (df['follower_count'].iloc[-1] - 
                                     df['follower_count'].iloc[0]) / 
                                     df['follower_count'].iloc[0]
                          for platform, df in data.items()}
            fig.add_trace(
                go.Bar(x=list(growth_rates.keys()),
                      y=list(growth_rates.values()),
                      name='Growth Rate',
                      marker_color=colors[1]),
                row=1, col=2
            )
            
            # Content performance
            for i, (platform, df) in enumerate(data.items()):
                fig.add_trace(
                    go.Box(y=df['engagement_count'],
                          name=platform,
                          marker_color=colors[i % len(colors)]),
                    row=2, col=1
                )
            
            # Audience size
            audience_size = {platform: df['follower_count'].iloc[-1]
                           for platform, df in data.items()}
            fig.add_trace(
                go.Pie(labels=list(audience_size.keys()),
                      values=list(audience_size.values()),
                      name='Audience Size'),
                row=2, col=2
            )
            
            fig.update_layout(height=800, title_text="Platform Comparison")
            return fig
            
        except Exception as e:
            self.logger.error(f"Error creating platform comparison visualization: {str(e)}")
            raise
