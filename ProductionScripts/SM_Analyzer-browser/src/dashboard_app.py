"""
Social Media Analytics Dashboard Application
Interactive web dashboard for visualizing social media analytics
"""

import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta

from analytics_manager import AnalyticsManager
from visualization.dashboard import AnalyticsDashboard

# Initialize analytics manager and dashboard
analytics_manager = AnalyticsManager()
dashboard = AnalyticsDashboard()

# Initialize Dash app with a modern theme
app = dash.Dash(__name__, 
                external_stylesheets=[dbc.themes.FLATLY],
                title="EDGLRD Social Media Analytics")

# Create the layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("EDGLRD Social Media Analytics", className="text-center mb-4"),
            html.Hr()
        ])
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Platform Selection"),
                dbc.CardBody([
                    dcc.Dropdown(
                        id='platform-dropdown',
                        options=[
                            {'label': 'Instagram', 'value': 'instagram'},
                            {'label': 'TikTok', 'value': 'tiktok'},
                            {'label': 'Twitter', 'value': 'twitter'},
                            {'label': 'YouTube', 'value': 'youtube'}
                        ],
                        value='instagram',
                        clearable=False
                    )
                ])
            ], className="mb-4")
        ])
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Audience Demographics"),
                dbc.CardBody([
                    dcc.Graph(id='demographics-graph')
                ])
            ])
        ], width=6),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Engagement Metrics"),
                dbc.CardBody([
                    dcc.Graph(id='engagement-graph')
                ])
            ])
        ], width=6)
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Content Performance"),
                dbc.CardBody([
                    dcc.Graph(id='content-performance-graph')
                ])
            ])
        ])
    ])
], fluid=True)

# Callbacks for updating graphs
@app.callback(
    Output('demographics-graph', 'figure'),
    Input('platform-dropdown', 'value')
)
def update_demographics(platform):
    # Create sample data for now
    data = pd.DataFrame({
        'age': [25, 30, 35, 40, 28, 32],
        'gender': ['M', 'F', 'M', 'F', 'M', 'F'],
        'location': ['US', 'UK', 'CA', 'US', 'UK', 'CA'],
        'income': ['50k', '75k', '100k', '60k', '80k', '90k']
    })
    return dashboard.plot_audience_demographics(data)

@app.callback(
    Output('engagement-graph', 'figure'),
    Input('platform-dropdown', 'value')
)
def update_engagement(platform):
    # Sample engagement data
    dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
    data = pd.DataFrame({
        'date': dates,
        'likes': [100 + i * 10 for i in range(30)],
        'comments': [50 + i * 5 for i in range(30)],
        'shares': [20 + i * 2 for i in range(30)]
    })
    
    fig = px.line(data, x='date', y=['likes', 'comments', 'shares'],
                  title='Engagement Over Time')
    return fig

@app.callback(
    Output('content-performance-graph', 'figure'),
    Input('platform-dropdown', 'value')
)
def update_content_performance(platform):
    # Sample content performance data
    data = pd.DataFrame({
        'content_type': ['Photo', 'Video', 'Story', 'Reel', 'Live'],
        'engagement_rate': [4.5, 6.2, 3.8, 7.1, 5.5],
        'reach': [1000, 2000, 800, 2500, 1500]
    })
    
    fig = px.scatter(data, x='engagement_rate', y='reach',
                    size='engagement_rate', text='content_type',
                    title='Content Performance by Type')
    return fig

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050, debug=True)
