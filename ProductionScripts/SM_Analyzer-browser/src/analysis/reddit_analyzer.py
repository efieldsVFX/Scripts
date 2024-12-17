"""
Reddit Analytics Module
Focused on essential metrics for content decisions
"""

from typing import Dict, List
import logging
from datetime import datetime
from collections import defaultdict
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

class RedditAudienceAnalyzer:
    """Simplified analyzer focusing on key audience insights"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def process_insights(self, posts: List[Dict], related_data: Dict = None) -> Dict:
        """Process Reddit posts to extract actionable insights specific to r/HarmonyKorrine"""
        try:
            if not posts:
                return {}

            analysis = {
                'content_insights': self._analyze_content_performance(posts),
                'edglrd_content': self._analyze_edglrd_content(posts),
                'community_interests': self._analyze_community_interests(related_data),
                'posting_patterns': self._analyze_posting_patterns(posts)
            }

            return analysis
        except Exception as e:
            self.logger.error(f"Error processing insights: {str(e)}")
            return {}

    def _analyze_content_performance(self, posts: List[Dict]) -> Dict:
        """Analyze what content performs best"""
        try:
            performance = {
                'top_posts': [],
                'topics': defaultdict(int),
                'avg_engagement': 0
            }

            total_engagement = 0
            for post in posts:
                # Calculate engagement (score + comments)
                engagement = post.get('score', 0) + post.get('num_comments', 0)
                total_engagement += engagement

                # Track top performing posts
                if engagement > 10:  # Only track posts with decent engagement
                    performance['top_posts'].append({
                        'title': post.get('title'),
                        'engagement': engagement,
                        'url': post.get('url'),
                        'created_utc': post.get('created_utc')
                    })

                # Extract topics from title
                words = post.get('title', '').lower().split()
                for word in words:
                    if len(word) > 4:  # Skip short words
                        performance['topics'][word] += 1

            # Sort top posts by engagement
            performance['top_posts'].sort(key=lambda x: x['engagement'], reverse=True)
            performance['top_posts'] = performance['top_posts'][:5]  # Keep only top 5

            # Calculate average engagement
            if posts:
                performance['avg_engagement'] = total_engagement / len(posts)

            # Get top topics
            performance['topics'] = dict(sorted(
                performance['topics'].items(),
                key=lambda x: x[1],
                reverse=True
            )[:10])  # Keep only top 10 topics

            return performance
        except Exception as e:
            self.logger.error(f"Error analyzing content performance: {str(e)}")
            return {}

    def _analyze_edglrd_content(self, posts: List[Dict]) -> Dict:
        """Analyze EDGLRD-related content performance"""
        edglrd_posts = [
            post for post in posts 
            if 'EDGLRD' in post.get('title', '').upper() or 'EDGLRD' in post.get('selftext', '').upper()
        ]
        
        return {
            'total_posts': len(edglrd_posts),
            'avg_score': sum(post.get('score', 0) for post in edglrd_posts) / len(edglrd_posts) if edglrd_posts else 0,
            'top_posts': sorted(edglrd_posts, key=lambda x: x.get('score', 0), reverse=True)[:5],
            'monthly_distribution': self._get_monthly_distribution(edglrd_posts)
        }

    def _analyze_community_interests(self, related_data: Dict) -> Dict:
        """Analyze community interests based on related subreddits"""
        if not related_data:
            return {}
            
        return {
            'top_related_subreddits': dict(list(related_data.get('related_subreddits', {}).items())[:10]),
            'interest_categories': self._categorize_interests(related_data.get('related_subreddits', {})),
            'cross_posting_patterns': self._analyze_cross_posting(related_data.get('user_posts', []))
        }

    def _analyze_posting_patterns(self, posts: List[Dict]) -> Dict:
        """Analyze posting patterns in the community"""
        patterns = {
            'post_types': defaultdict(int),
            'flair_distribution': defaultdict(int),
            'weekly_activity': defaultdict(int)
        }
        
        for post in posts:
            # Analyze post types
            patterns['post_types']['text' if post.get('is_self') else 'link'] += 1
            
            # Track flair usage
            if post.get('link_flair_text'):
                patterns['flair_distribution'][post['link_flair_text']] += 1
            
            # Track weekly activity
            timestamp = datetime.fromtimestamp(post['created_utc'])
            patterns['weekly_activity'][timestamp.strftime('%A')] += 1
            
        return patterns

    def _categorize_interests(self, related_subs: Dict) -> Dict:
        """Categorize related subreddits into interest categories"""
        categories = defaultdict(int)
        
        # Define category keywords
        category_mapping = {
            'Film & Cinema': ['movie', 'film', 'cinema', 'director'],
            'Art & Culture': ['art', 'culture', 'photography', 'music'],
            'Entertainment': ['tv', 'shows', 'entertainment', 'media'],
            'Discussion': ['discussion', 'talk', 'debate', 'ask'],
        }
        
        for sub, count in related_subs.items():
            sub_lower = sub.lower()
            categorized = False
            for category, keywords in category_mapping.items():
                if any(keyword in sub_lower for keyword in keywords):
                    categories[category] += count
                    categorized = True
                    break
            if not categorized:
                categories['Other'] += count
                
        return dict(categories)

    def _get_monthly_distribution(self, posts: List[Dict]) -> Dict:
        """Get monthly distribution of posts"""
        distribution = defaultdict(int)
        
        for post in posts:
            timestamp = datetime.fromtimestamp(post['created_utc'])
            distribution[timestamp.strftime('%Y-%m')] += 1
            
        return dict(distribution)

    def _analyze_cross_posting(self, user_posts: List[Dict]) -> Dict:
        """Analyze cross-posting patterns"""
        patterns = defaultdict(int)
        
        for post in user_posts:
            # Track cross-posting
            if post.get('crosspost_parent'):
                patterns['cross_posts'] += 1
                
        return dict(patterns)


class RedditMLAnalyzer:
    """ML-powered Reddit content analyzer"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.nlp = spacy.load('en_core_web_sm')
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.clustering = KMeans(n_clusters=5, random_state=42)
        
    def analyze_subreddit_trends(self, analytics_data: Dict) -> Dict:
        """Analyze subreddit trends using ML techniques"""
        try:
            insights = {
                'content_clusters': self._analyze_content_clusters(analytics_data),
                'engagement_predictions': self._predict_engagement(analytics_data),
                'topic_trends': self._analyze_topic_trends(analytics_data),
                'growth_opportunities': self._identify_growth_opportunities(analytics_data),
                'content_recommendations': self._generate_content_recommendations(analytics_data)
            }
            return insights
        except Exception as e:
            self.logger.error(f"Error in ML analysis: {str(e)}")
            return {}
    
    def _analyze_content_clusters(self, analytics_data: Dict) -> Dict:
        """Cluster similar content to identify successful patterns"""
        try:
            # Prepare text data for clustering
            texts = [f"{post['title']} {post['selftext']}" for post in analytics_data['top_posts']]
            if not texts:
                return {}
                
            # Transform texts to TF-IDF features
            features = self.vectorizer.fit_transform(texts)
            
            # Perform clustering
            clusters = self.clustering.fit_predict(features)
            
            # Analyze clusters
            cluster_insights = defaultdict(list)
            for idx, cluster in enumerate(clusters):
                post = analytics_data['top_posts'][idx]
                cluster_insights[f'cluster_{cluster}'].append({
                    'title': post['title'],
                    'score': post['score'],
                    'engagement': post['score'] + post['num_comments']
                })
            
            # Calculate cluster performance
            cluster_performance = {}
            for cluster, posts in cluster_insights.items():
                avg_engagement = sum(p['engagement'] for p in posts) / len(posts)
                cluster_performance[cluster] = {
                    'avg_engagement': avg_engagement,
                    'top_posts': sorted(posts, key=lambda x: x['engagement'], reverse=True)[:3],
                    'size': len(posts)
                }
                
            return cluster_performance
        except Exception as e:
            self.logger.error(f"Error in content clustering: {str(e)}")
            return {}
    
    def _predict_engagement(self, analytics_data: Dict) -> Dict:
        """Predict potential engagement for different content types"""
        try:
            engagement_patterns = defaultdict(list)
            
            # Analyze engagement patterns by content type
            for post in analytics_data['top_posts']:
                content_type = self._get_content_type(post)
                time_of_day = datetime.fromtimestamp(post['created_utc']).hour
                engagement = post['score'] + post['num_comments']
                
                engagement_patterns[content_type].append({
                    'time_of_day': time_of_day,
                    'engagement': engagement
                })
            
            # Calculate optimal posting times and expected engagement
            predictions = {}
            for content_type, patterns in engagement_patterns.items():
                by_hour = defaultdict(list)
                for p in patterns:
                    by_hour[p['time_of_day']].append(p['engagement'])
                
                best_hours = {
                    hour: sum(engagements)/len(engagements)
                    for hour, engagements in by_hour.items()
                }
                
                predictions[content_type] = {
                    'best_hours': dict(sorted(best_hours.items(), 
                                            key=lambda x: x[1], 
                                            reverse=True)[:3]),
                    'avg_engagement': sum(p['engagement'] for p in patterns) / len(patterns)
                }
            
            return predictions
        except Exception as e:
            self.logger.error(f"Error in engagement prediction: {str(e)}")
            return {}
    
    def _analyze_topic_trends(self, analytics_data: Dict) -> Dict:
        """Analyze trending topics and their performance"""
        try:
            # Extract topics using NLP
            topics = defaultdict(list)
            for post in analytics_data['top_posts']:
                doc = self.nlp(f"{post['title']} {post['selftext']}")
                
                # Extract named entities and noun phrases
                entities = [ent.text.lower() for ent in doc.ents]
                noun_phrases = [chunk.text.lower() for chunk in doc.noun_chunks]
                
                engagement = post['score'] + post['num_comments']
                
                # Track performance of topics
                for topic in set(entities + noun_phrases):
                    if len(topic.split()) > 1:  # Only multi-word topics
                        topics[topic].append(engagement)
            
            # Calculate topic performance
            topic_performance = {}
            for topic, engagements in topics.items():
                if len(engagements) >= 3:  # Only topics with sufficient data
                    topic_performance[topic] = {
                        'frequency': len(engagements),
                        'avg_engagement': sum(engagements) / len(engagements),
                        'trend': self._calculate_trend(engagements)
                    }
            
            return dict(sorted(topic_performance.items(), 
                             key=lambda x: x[1]['avg_engagement'], 
                             reverse=True)[:20])
        except Exception as e:
            self.logger.error(f"Error in topic analysis: {str(e)}")
            return {}
    
    def _identify_growth_opportunities(self, analytics_data: Dict) -> Dict:
        """Identify potential growth opportunities"""
        try:
            opportunities = {
                'underutilized_content_types': self._find_underutilized_content(),
                'emerging_topics': self._find_emerging_topics(analytics_data),
                'engagement_gaps': self._find_engagement_gaps(analytics_data),
                'content_suggestions': self._generate_content_suggestions(analytics_data)
            }
            return opportunities
        except Exception as e:
            self.logger.error(f"Error identifying growth opportunities: {str(e)}")
            return {}
    
    def _generate_content_recommendations(self, analytics_data: Dict) -> List[Dict]:
        """Generate content recommendations based on historical performance"""
        try:
            # Analyze successful content patterns
            successful_patterns = self._analyze_successful_patterns(analytics_data)
            
            # Generate recommendations
            recommendations = []
            for pattern in successful_patterns:
                recommendations.append({
                    'content_type': pattern['type'],
                    'suggested_topics': pattern['topics'],
                    'best_posting_time': pattern['optimal_time'],
                    'expected_engagement': pattern['expected_engagement'],
                    'reasoning': pattern['success_factors']
                })
            
            return recommendations
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {str(e)}")
            return []
    
    def _get_content_type(self, post: Dict) -> str:
        """Determine content type from post data"""
        if post.get('is_video'):
            return 'video'
        elif post.get('url', '').endswith(('.jpg', '.png', '.gif')):
            return 'image'
        elif post.get('is_self'):
            return 'text'
        return 'link'
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from a series of values"""
        if len(values) < 2:
            return 'stable'
        
        slope = (values[-1] - values[0]) / len(values)
        if slope > 0.1:
            return 'rising'
        elif slope < -0.1:
            return 'falling'
        return 'stable'
