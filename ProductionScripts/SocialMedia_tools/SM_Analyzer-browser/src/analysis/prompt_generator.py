from typing import Dict, List
import pandas as pd
from textblob import TextBlob

class PromptGenerator:
    def __init__(self):
        self.style_mappings = {
            'high_engagement': ['masterpiece', 'award winning', 'trending', 'viral'],
            'emotional': ['dramatic', 'powerful', 'emotional', 'intense'],
            'technical': ['highly detailed', 'ultra realistic', 'professional', '8k'],
            'artistic': ['artistic', 'stylized', 'creative', 'innovative']
        }
        
    def generate_prompts(self, analysis_data: Dict) -> List[Dict]:
        """Generate Stable Diffusion prompts based on social media analysis"""
        prompts = []
        
        # Extract key performance indicators
        top_content = self._analyze_top_content(analysis_data)
        sentiment_data = self._analyze_sentiment_patterns(analysis_data)
        visual_elements = self._extract_visual_elements(analysis_data)
        
        # Generate base prompts
        for content_type, metrics in top_content.items():
            prompt = {
                'base_prompt': self._construct_base_prompt(
                    content_type, 
                    metrics, 
                    sentiment_data,
                    visual_elements
                ),
                'negative_prompt': self._construct_negative_prompt(metrics),
                'performance_metrics': metrics,
                'recommended_settings': self._get_recommended_settings(metrics)
            }
            prompts.append(prompt)
            
        return prompts

    def _analyze_top_content(self, analysis_data: Dict) -> Dict:
        """Analyze top performing content patterns"""
        content_patterns = {}
        
        for platform, data in analysis_data.items():
            if 'top_performing_posts' in data:
                for post in data['top_performing_posts']:
                    content_type = self._classify_content(post)
                    engagement = post.get('engagement_score', 0)
                    
                    if content_type not in content_patterns:
                        content_patterns[content_type] = {
                            'engagement': 0,
                            'common_elements': [],
                            'color_patterns': [],
                            'composition_types': []
                        }
                    
                    content_patterns[content_type]['engagement'] += engagement
                    
        return content_patterns

    def _construct_base_prompt(self, content_type: str, metrics: Dict, 
                             sentiment: Dict, visuals: Dict) -> str:
        """Construct the main prompt based on analysis"""
        prompt_elements = []
        
        # Add technical quality terms
        prompt_elements.extend([
            "masterpiece",
            "highly detailed",
            "professional photography"
        ])
        
        # Add style elements based on performance
        if metrics['engagement'] > 0.8:  # High engagement threshold
            prompt_elements.extend(self.style_mappings['high_engagement'])
        
        # Add emotional elements based on sentiment
        if sentiment.get('positive_ratio', 0) > 0.7:
            prompt_elements.extend(self.style_mappings['emotional'])
            
        # Add visual elements
        if visuals:
            prompt_elements.extend([
                f"prominent {color} tones" for color in visuals.get('colors', [])[:2]
            ])
            
        return ", ".join(prompt_elements)

    def _construct_negative_prompt(self, metrics: Dict) -> str:
        """Construct negative prompt based on low-performing elements"""
        negative_elements = [
            "low quality",
            "blurry",
            "watermark",
            "text",
            "oversaturated"
        ]
        
        # Add specific negative elements based on metrics
        if metrics.get('low_performing_elements'):
            negative_elements.extend(metrics['low_performing_elements'])
            
        return ", ".join(negative_elements)

    def _get_recommended_settings(self, metrics: Dict) -> Dict:
        """Get recommended Stable Diffusion settings based on content type"""
        return {
            'CFG': 12 if metrics['engagement'] > 0.8 else 8,
            'steps': 50,
            'sampler': 'k_euler_a',
            'size': '512x512'
        }
