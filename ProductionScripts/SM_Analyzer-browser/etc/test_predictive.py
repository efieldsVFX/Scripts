import sys
import os
import pandas as pd
from datetime import datetime, timedelta
import pytest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.analysis.predictive_analyzer import PredictiveAnalyzer

def generate_test_data():
    # Generate sample data for testing
    dates = pd.date_range(start='2024-01-01', end='2024-12-10', freq='D')
    
    # Instagram data
    instagram_data = pd.DataFrame({
        'date': dates,
        'followers': range(1000, 1000 + len(dates)),
        'followers_delta': [5] * len(dates),
        'likes': [100] * len(dates),
        'comments': [20] * len(dates),
        'shares': [10] * len(dates),
        'saves': [5] * len(dates),
        'post_id': [f'post_{i}' for i in range(len(dates))],
        'post_type': ['image'] * len(dates)
    })
    
    # TikTok data with different growth pattern
    tiktok_data = pd.DataFrame({
        'date': dates,
        'followers': range(2000, 2000 + len(dates) * 2, 2),
        'followers_delta': [10] * len(dates),
        'likes': [200] * len(dates),
        'comments': [40] * len(dates),
        'shares': [30] * len(dates),
        'saves': [15] * len(dates),
        'post_id': [f'tiktok_{i}' for i in range(len(dates))],
        'post_type': ['video'] * len(dates)
    })
    
    return {
        'engagement': pd.concat([instagram_data, tiktok_data], ignore_index=True),
        'content': pd.concat([instagram_data, tiktok_data], ignore_index=True)
    }

def test_predictive_insights():
    # Initialize analyzer
    analyzer = PredictiveAnalyzer()
    
    # Generate test data
    analysis_data = generate_test_data()
    
    # Run analysis
    predictive_results = analyzer.get_predictive_insights(analysis_data)
    
    # Verify structure
    assert isinstance(predictive_results, dict), "Predictive results should be a dictionary"
    assert 'virality' in predictive_results, "Should contain virality metrics"
    assert 'follower_decay' in predictive_results, "Should contain follower decay metrics"
    assert 'lifetime_value' in predictive_results, "Should contain lifetime value metrics"
    assert 'trends' in predictive_results, "Should contain trend metrics"
    
    # Print results for inspection
    print("\nPredictive Analysis Results:")
    for metric, value in predictive_results.items():
        print(f"\n{metric.upper()}:")
        print(value)

if __name__ == "__main__":
    test_predictive_insights()
