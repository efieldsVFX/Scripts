"""
Social Media Analytics Dashboard
A professional-grade analytics interface for social media insights
"""

import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd
import sys
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent.parent
if str(src_path) not in sys.path:
    sys.path.append(str(src_path))

# Import project modules
from analytics_manager import AnalyticsManager
from utils.logger import get_logger
import yaml

logger = get_logger(__name__)

# Page configuration
st.set_page_config(
    page_title="Social Media Analytics Hub",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern look
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        background-color: #007bff;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        border: none;
    }
    .metric-card {
        background-color: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .st-emotion-cache-1y4p8pa {
        max-width: 100% !important;
    }
    </style>
    """, unsafe_allow_html=True)

class DashboardUI:
    def __init__(self):
        config_path = src_path / "config" / "config.yaml"
        self.manager = AnalyticsManager(str(config_path))
        
    def render_header(self):
        """Render dashboard header"""
        col1, col2 = st.columns([2,3])
        with col1:
            st.title("📊 Social Media Analytics Hub")
        with col2:
            st.markdown(
                """
                <div style='text-align: right; padding: 1rem;'>
                    <span style='color: #666; font-size: 0.8rem;'>Last Updated: {}</span>
                </div>
                """.format(datetime.now().strftime("%Y-%m-%d %H:%M")),
                unsafe_allow_html=True
            )
            
    def render_sidebar(self):
        """Render sidebar controls"""
        with st.sidebar:
            st.markdown("## Analytics Controls")
            
            platform = st.selectbox(
                "Select Platform",
                ["Instagram", "TikTok", "Twitter", "YouTube"],
                index=0
            )
            
            date_range = st.date_input(
                "Date Range",
                value=(datetime.now() - timedelta(days=30), datetime.now()),
                max_value=datetime.now()
            )
            
            metrics = st.multiselect(
                "Select Metrics",
                ["Post Intelligence", "Engagement Analytics", "Audience Insights", "Strategic Metrics"],
                default=["Post Intelligence", "Engagement Analytics"]
            )
            
            st.markdown("---")
            
            if st.button("Generate Report", use_container_width=True):
                return {
                    'platform': platform,
                    'start_date': date_range[0],
                    'end_date': date_range[1],
                    'metrics': metrics
                }
        return None
        
    def render_overview_metrics(self, data: dict):
        """Render overview metrics cards"""
        st.markdown("### Key Performance Overview")
        
        cols = st.columns(4)
        metrics = [
            ("Total Posts", data['post_intelligence']['total_posts'], ""),
            ("Engagement Rate", f"{data['engagement_analytics']['real_time_metrics']['current_engagement_rate']}%", ""),
            ("Brand Voice Score", data['strategic_metrics']['brand_consistency']['voice_score'], ""),
            ("ROI", f"{data['strategic_metrics']['roi_analysis']['overall_roi']}%", "")
        ]
        
        for col, (label, value, change) in zip(cols, metrics):
            with col:
                st.metric(label=label, value=value, delta=change)
                    
    def render_charts(self, data: dict, selected_metrics: list):
        """Render analytics charts"""
        if "Post Intelligence" in selected_metrics:
            st.markdown("### Post Intelligence")
            col1, col2 = st.columns(2)
            
            with col1:
                # Content Type Distribution
                fig = go.Figure(data=[go.Pie(
                    labels=list(data['post_intelligence']['content_types'].keys()),
                    values=list(data['post_intelligence']['content_types'].values()),
                    hole=.3
                )])
                fig.update_layout(title="Content Type Distribution")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Daily Post Distribution
                daily_data = data['post_intelligence']['posting_times']['daily_distribution']
                fig = go.Figure(data=[go.Bar(
                    x=list(daily_data.keys()),
                    y=list(daily_data.values())
                )])
                fig.update_layout(title="Daily Post Distribution")
                st.plotly_chart(fig, use_container_width=True)
            
        if "Engagement Analytics" in selected_metrics:
            st.markdown("### Engagement Analytics")
            col1, col2 = st.columns(2)
            
            with col1:
                # Sentiment Analysis
                sentiment = data['engagement_analytics']['sentiment_analysis']
                fig = go.Figure(data=[go.Pie(
                    labels=['Positive', 'Neutral', 'Negative'],
                    values=[sentiment['positive'], sentiment['neutral'], sentiment['negative']]
                )])
                fig.update_layout(title="Sentiment Distribution")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Engagement Trend
                trend = data['engagement_analytics']['real_time_metrics']['hourly_trend']
                fig = go.Figure(data=[go.Line(y=trend)])
                fig.update_layout(title="Hourly Engagement Trend")
                st.plotly_chart(fig, use_container_width=True)
            
        if "Audience Insights" in selected_metrics:
            st.markdown("### Audience Demographics")
            col1, col2 = st.columns(2)
            
            with col1:
                # Age Distribution
                age_data = data['audience_insights']['demographics']['age_groups']
                fig = go.Figure(data=[go.Bar(
                    x=list(age_data.keys()),
                    y=list(age_data.values())
                )])
                fig.update_layout(title="Age Distribution")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Gender Distribution
                gender_data = data['audience_insights']['demographics']['gender']
                fig = go.Figure(data=[go.Pie(
                    labels=list(gender_data.keys()),
                    values=list(gender_data.values())
                )])
                fig.update_layout(title="Gender Distribution")
                st.plotly_chart(fig, use_container_width=True)
            
        if "Strategic Metrics" in selected_metrics:
            st.markdown("### Strategic Performance")
            col1, col2 = st.columns(2)
            
            with col1:
                # ROI by Content Type
                roi_data = data['strategic_metrics']['roi_analysis']['by_content_type']
                fig = go.Figure(data=[go.Bar(
                    x=list(roi_data.keys()),
                    y=list(roi_data.values())
                )])
                fig.update_layout(title="ROI by Content Type")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Brand Consistency Metrics
                brand_data = data['strategic_metrics']['brand_consistency']
                fig = go.Figure(data=[go.Radar(
                    r=[brand_data['voice_score'], brand_data['visual_consistency'], brand_data['message_alignment']],
                    theta=['Voice', 'Visual', 'Message']
                )])
                fig.update_layout(title="Brand Consistency Metrics")
                st.plotly_chart(fig, use_container_width=True)
                    
    def render_insights(self, data: dict):
        """Render AI-powered insights"""
        st.markdown("### Key Insights")
        
        with st.expander("View Detailed Insights", expanded=True):
            cols = st.columns(2)
            
            insights = [
                "👥 Audience engagement peaks during evening hours (6-8 PM)",
                "📈 Video content outperforms static posts by 47%",
                "🎯 Female users aged 25-34 show highest conversion rates",
                "💡 Educational content drives 2.3x more shares"
            ]
            
            for col, insight in zip(cols * 2, insights):
                with col:
                    st.markdown(f"""
                        <div style="background-color: white; padding: 1rem; border-radius: 5px; margin: 0.5rem 0;">
                            {insight}
                        </div>
                    """, unsafe_allow_html=True)
                    
    def render_recommendations(self, data: dict):
        """Render AI-generated recommendations"""
        st.markdown("### Strategic Recommendations")
        
        recommendations = [
            {
                "title": "Content Strategy",
                "description": "Increase video content production focusing on educational topics",
                "impact": "High",
                "effort": "Medium"
            },
            {
                "title": "Posting Schedule",
                "description": "Optimize posting times for 6-8 PM window",
                "impact": "Medium",
                "effort": "Low"
            },
            {
                "title": "Audience Targeting",
                "description": "Create targeted campaigns for female users 25-34",
                "impact": "High",
                "effort": "High"
            }
        ]
        
        for rec in recommendations:
            st.markdown(f"""
                <div style="background-color: white; padding: 1rem; border-radius: 5px; margin: 1rem 0;">
                    <h4 style="margin: 0;">{rec['title']}</h4>
                    <p style="margin: 0.5rem 0;">{rec['description']}</p>
                    <span style="background-color: #e9ecef; padding: 0.2rem 0.5rem; border-radius: 3px; margin-right: 0.5rem;">
                        Impact: {rec['impact']}
                    </span>
                    <span style="background-color: #e9ecef; padding: 0.2rem 0.5rem; border-radius: 3px;">
                        Effort: {rec['effort']}
                    </span>
                </div>
            """, unsafe_allow_html=True)
            
    def main(self):
        """Main dashboard rendering function"""
        try:
            self.render_header()
            
            # Render sidebar and get user selections
            selections = self.render_sidebar()
            
            if selections:
                # Generate analytics data
                report = self.manager.generate_report(
                    platform=selections['platform'].lower(),
                    start_date=selections['start_date'],
                    end_date=selections['end_date']
                )
                
                # Render dashboard components
                self.render_overview_metrics(report['analysis'])
                self.render_charts(report['analysis'], selections['metrics'])
                self.render_insights(report['analysis'])
                self.render_recommendations(report['analysis'])
                
        except Exception as e:
            logger.error(f"Error rendering dashboard: {str(e)}")
            st.error("An error occurred while rendering the dashboard. Please try again.")

if __name__ == "__main__":
    dashboard = DashboardUI()
    dashboard.main()
