"""
Content Ideas Section for Streamlit Dashboard
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List
import pandas as pd
from collections import defaultdict

def display_content_ideas_section(platform_data: Dict, selected_platform: str):
    """Display content ideas section in the dashboard"""
    st.markdown("## 💡 Content Ideas")
    
    # Get content ideas for selected platform
    if selected_platform == "All Platforms":
        ideas = platform_data.get('content_ideas', {})
        if not ideas:
            st.info("No content ideas available yet. Generate more content to get personalized suggestions!")
            return
            
        # Create tabs for each platform
        platform_tabs = st.tabs(list(ideas.keys()) or ["No Data"])
        for tab, platform in zip(platform_tabs, ideas.keys()):
            with tab:
                display_platform_ideas(ideas[platform], platform)
    else:
        platform_ideas = platform_data.get('content_ideas', {}).get(selected_platform, [])
        display_platform_ideas(platform_ideas, selected_platform)

def display_platform_ideas(ideas: List[Dict], platform: str):
    """Display ideas for a specific platform"""
    if not ideas:
        st.info(f"No content ideas available for {platform} yet. Generate more content to get personalized suggestions!")
        return
        
    # Display ideas in a modern card layout
    for i, idea in enumerate(ideas, 1):
        with st.container():
            # Create a card-like container with custom styling
            st.markdown("""
                <style>
                .idea-card {
                    background-color: #ffffff;
                    border-radius: 10px;
                    padding: 20px;
                    margin: 10px 0;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                .idea-header {
                    color: #1f1f1f;
                    font-size: 1.2em;
                    font-weight: bold;
                    margin-bottom: 15px;
                }
                .idea-section {
                    margin: 10px 0;
                    padding: 10px;
                    background-color: #f8f9fa;
                    border-radius: 5px;
                }
                .tag {
                    display: inline-block;
                    padding: 5px 10px;
                    margin: 0 5px 5px 0;
                    background-color: #e9ecef;
                    border-radius: 15px;
                    font-size: 0.9em;
                }
                </style>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
                <div class="idea-card">
                    <div class="idea-header">
                        💡 Content Idea #{i}
                    </div>
                """, unsafe_allow_html=True)
            
            # Create two columns for content layout
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Title and Type
                if idea.get('title'):
                    st.markdown(f"**{idea['title']}**")
                if idea.get('content_type'):
                    st.markdown(f"""
                        <div class="tag">
                            {idea['content_type']}
                        </div>
                    """, unsafe_allow_html=True)
                
                # Theme
                if idea.get('theme'):
                    st.markdown("""
                        <div class="idea-section">
                            <strong>Theme:</strong><br/>
                            {theme}
                        </div>
                    """.format(theme=idea['theme']), unsafe_allow_html=True)
                
                # Description
                if idea.get('description'):
                    st.markdown("""
                        <div class="idea-section">
                            <strong>Description:</strong><br/>
                            {description}
                        </div>
                    """.format(description=idea['description']), unsafe_allow_html=True)
                
                # Key Elements
                if idea.get('suggested_elements'):
                    st.markdown("<strong>Key Elements:</strong>", unsafe_allow_html=True)
                    for element in idea['suggested_elements']:
                        st.markdown(f"""
                            <div class="tag">
                                • {element}
                            </div>
                        """, unsafe_allow_html=True)
            
            with col2:
                # Metrics in a clean layout
                st.markdown('<div class="idea-section">', unsafe_allow_html=True)
                
                # Best Time to Post
                if idea.get('optimal_posting_time') is not None:
                    st.metric(
                        "Best Time to Post",
                        f"{idea['optimal_posting_time']:02d}:00"
                    )
                
                # Impact Score
                if idea.get('predicted_impact') is not None:
                    st.metric(
                        "Impact Score",
                        f"{idea['predicted_impact']:.2f}"
                    )
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Hashtags
                if idea.get('hashtags'):
                    st.markdown("<strong>Suggested Hashtags:</strong>", unsafe_allow_html=True)
                    hashtags_html = "".join([
                        f'<div class="tag">#{tag}</div>'
                        for tag in idea['hashtags']
                    ])
                    st.markdown(hashtags_html, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Add some spacing between cards
            st.markdown("<br/>", unsafe_allow_html=True)

def display_content_performance_insights(performance_data: Dict):
    """Display insights about content performance"""
    st.markdown("### 📈 Content Performance Insights")
    
    # Create tabs for different insight types
    insight_tabs = st.tabs([
        "Best Performing Elements",
        "Optimal Timing",
        "Content Themes"
    ])
    
    with insight_tabs[0]:
        if 'element_performance' in performance_data:
            fig = px.bar(
                pd.DataFrame({
                    'Element': performance_data['element_performance'].keys(),
                    'Score': performance_data['element_performance'].values()
                }),
                x='Element',
                y='Score',
                title='Performance by Content Element'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with insight_tabs[1]:
        if 'peak_times' in performance_data:
            fig = px.line(
                pd.DataFrame({
                    'Hour': [time[0] for time in performance_data['peak_times']],
                    'Engagement': [score[1] for score in performance_data['peak_times']]
                }),
                x='Hour',
                y='Engagement',
                title='Engagement by Hour'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with insight_tabs[2]:
        if 'content_themes' in performance_data:
            fig = px.pie(
                pd.DataFrame({
                    'Theme': performance_data['content_themes'].keys(),
                    'Score': performance_data['content_themes'].values()
                }),
                names='Theme',
                values='Score',
                title='Top Performing Content Themes'
            )
            st.plotly_chart(fig, use_container_width=True)

def display_idea_generation_controls():
    """Display controls for idea generation"""
    with st.sidebar:
        st.markdown("### 💡 Content Ideas")
        
        # Platform selection (if needed)
        target_platform = st.selectbox(
            "Generate Ideas for Platform",
            ["All Platforms", "Instagram", "Twitter", "TikTok", "YouTube"]
        )
        
        # Content type filter
        content_types = st.multiselect(
            "Content Types",
            ["Image", "Video", "Story", "Reel", "Text", "Carousel"],
            default=["Image", "Video", "Story"]
        )
        
        # Number of ideas
        num_ideas = st.slider(
            "Number of Ideas",
            min_value=1,
            max_value=10,
            value=5
        )
        
        # Generate button
        if st.button("Generate Fresh Ideas"):
            st.session_state.regenerate_ideas = True
            
        return {
            'target_platform': target_platform,
            'content_types': content_types,
            'num_ideas': num_ideas
        }
