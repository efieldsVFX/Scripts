"""
Test script for Social Media Analytics implementations
"""

import sys
import os
from datetime import datetime
import pandas as pd
from typing import Dict, List

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from collectors.reddit_collector import RedditCollector
from collectors.twitter_collector import TwitterCollector
from collectors.youtube_collector import YouTubeCollector
from collectors.instagram_collector import InstagramCollector
from analysis.reddit_analyzer import RedditAudienceAnalyzer
from analysis.twitter_analyzer import TwitterAudienceAnalyzer
from analysis.youtube_analyzer import YouTubeAudienceAnalyzer
from analysis.instagram_analyzer import InstagramAudienceAnalyzer

def test_reddit_analytics():
    """Test Reddit analytics implementation"""
    print("\n=== Testing Reddit Analytics ===")
    
    try:
        # Initialize collector and analyzer
        collector = RedditCollector()
        analyzer = RedditAudienceAnalyzer()
        
        # Test subreddit insights collection
        print("\nCollecting insights from r/Python...")
        insights = collector.collect_audience_insights("Python")
        
        if not insights:
            print("[FAIL] Failed to collect Reddit insights")
            return
            
        print("[PASS] Successfully collected Reddit insights")
        print(f"- Community data collected: {bool(insights.get('community_data'))}")
        print(f"- Engagement data collected: {bool(insights.get('engagement_data'))}")
        print(f"- Content data collected: {bool(insights.get('content_data'))}")
        print(f"- Behavior data collected: {bool(insights.get('behavior_data'))}")
        print(f"- Topic data collected: {bool(insights.get('topic_data'))}")
        
        # Test insights analysis
        print("\nAnalyzing Reddit insights...")
        analysis = analyzer.process_insights(insights)
        
        if not analysis:
            print("[FAIL] Failed to analyze Reddit insights")
            return
            
        print("[PASS] Successfully analyzed Reddit insights")
        print(f"- Community metrics analyzed: {bool(analysis.get('community_metrics'))}")
        print(f"- Engagement analyzed: {bool(analysis.get('engagement'))}")
        print(f"- Content performance analyzed: {bool(analysis.get('content_performance'))}")
        print(f"- Audience behavior analyzed: {bool(analysis.get('audience_behavior'))}")
        print(f"- Topic analysis completed: {bool(analysis.get('topic_analysis'))}")
        
        # Test content collection
        print("\nTesting content collection...")
        posts_df = collector.collect_subreddit_posts("Python", limit=10)
        
        if posts_df.empty:
            print("[FAIL] Failed to collect Reddit posts")
            return
            
        print("[PASS] Successfully collected Reddit posts")
        print(f"- Number of posts collected: {len(posts_df)}")
        
    except Exception as e:
        print(f"[FAIL] Error during Reddit analytics testing: {str(e)}")

def test_twitter_analytics():
    """Test Twitter analytics implementation"""
    print("\n=== Testing Twitter Analytics ===")
    
    try:
        # Test initialization without API keys
        collector = TwitterCollector({})
        analyzer = TwitterAudienceAnalyzer()
        
        print("[PASS] Successfully initialized Twitter components")
        print("Note: Full testing requires Twitter API keys")
        
    except Exception as e:
        print(f"[FAIL] Error during Twitter analytics testing: {str(e)}")

def test_youtube_analytics():
    """Test YouTube analytics implementation"""
    print("\n=== Testing YouTube Analytics ===")
    
    try:
        # Test initialization without API key
        collector = YouTubeCollector({})
        analyzer = YouTubeAudienceAnalyzer()
        
        print("[PASS] Successfully initialized YouTube components")
        print("Note: Full testing requires YouTube API key")
        
    except Exception as e:
        print(f"[FAIL] Error during YouTube analytics testing: {str(e)}")

def test_instagram_analytics():
    """Test Instagram analytics implementation"""
    print("\n=== Testing Instagram Analytics ===")
    
    try:
        # Test initialization without API keys
        collector = InstagramCollector({})
        analyzer = InstagramAudienceAnalyzer()
        
        print("[PASS] Successfully initialized Instagram components")
        print("Note: Full testing requires Instagram API keys")
        
    except Exception as e:
        print(f"[FAIL] Error during Instagram analytics testing: {str(e)}")

def main():
    """Run all analytics tests"""
    print("Starting Social Media Analytics Tests...")
    print("=" * 50)
    
    # Test Reddit implementation
    test_reddit_analytics()
    
    # Test Twitter implementation
    test_twitter_analytics()
    
    # Test YouTube implementation
    test_youtube_analytics()
    
    # Test Instagram implementation
    test_instagram_analytics()
    
    print("\nTests completed!")

if __name__ == "__main__":
    main()
