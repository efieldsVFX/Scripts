from src.collectors.reddit_collector import RedditCollector
from src.config import load_config
import json
from datetime import datetime

def print_section(title: str, data: dict):
    """Helper function to print formatted sections"""
    print(f"\n{'='*20} {title} {'='*20}")
    print(json.dumps(data, indent=2))

def main():
    # Initialize collector
    config = load_config()
    collector = RedditCollector(config['reddit'])
    
    # 1. Get subscriber metrics
    subscriber_metrics = collector.get_subscriber_metrics()
    print_section("Subscriber Metrics", subscriber_metrics)
    
    # 2. Analyze content preferences and trends
    content_analysis = collector.analyze_content_preferences(timeframe='month')
    print_section("Content Analysis", content_analysis)
    
    # 3. Get audience insights
    audience_insights = collector.analyze_audience_insights(sample_size=100)
    print_section("Audience Insights", audience_insights)
    
    # 4. Predict performance for a sample post
    sample_post = {
        'type': 'text',
        'title': 'New EDGLRD Collection Announcement',
        'content': 'Excited to share our latest sustainable fashion collection...',
        'planned_time': datetime.now()
    }
    performance_prediction = collector.predict_post_performance(sample_post)
    print_section("Post Performance Prediction", performance_prediction)
    
    # 5. Get detailed subreddit stats
    subreddit_stats = collector.get_subreddit_stats()
    print_section("Detailed Subreddit Statistics", subreddit_stats)
    
    # Generate summary report
    print("\n📊 EDGLRD Reddit Analytics Summary 📊")
    print(f"Total Subscribers: {subscriber_metrics.get('total_subscribers', 'N/A')}")
    print(f"Active Users: {subscriber_metrics.get('active_users', 'N/A')}")
    print(f"Most Active Hours: {list(audience_insights.get('active_hours', {}).keys())[:3]}")
    print(f"Top Content Type: {next(iter(content_analysis.get('post_types', {})), 'N/A')}")
    print(f"Recommended Posting Time: {performance_prediction.get('best_posting_time', 'N/A')}")
    
    # Print actionable insights
    print("\n🎯 Actionable Insights:")
    print("1. Best Time to Post:", performance_prediction.get('best_posting_time', 'N/A'))
    print("2. Content Recommendations:")
    for rec in performance_prediction.get('content_recommendations', []):
        print(f"   - {rec}")
    print(f"3. Most Active Subreddit Overlap: {list(audience_insights.get('common_subreddits', {}).keys())[:3]}")

if __name__ == "__main__":
    main()
