"""
Configuration loader for EDGLRD Social Media Analyzer
"""

import os
import json
import yaml
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'))

def load_config() -> Dict[str, Any]:
    """
    Load configuration from JSON and YAML files, with environment variable overrides
    """
    config = {}
    
    # Load JSON config
    json_path = os.path.join(os.path.dirname(__file__), 'app_config.json')
    if os.path.exists(json_path):
        with open(json_path, 'r') as f:
            config.update(json.load(f))
    
    # Load YAML config
    yaml_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
    if os.path.exists(yaml_path):
        with open(yaml_path, 'r') as f:
            yaml_config = yaml.safe_load(f)
            if yaml_config:
                config.update(yaml_config)
    
    # Override with environment variables for API credentials
    api_auth = config.get('api_auth', {})
    
    # Reddit credentials
    reddit_auth = api_auth.get('reddit', {})
    reddit_auth.update({
        'client_id': os.getenv('REDDIT_CLIENT_ID', reddit_auth.get('client_id')),
        'client_secret': os.getenv('REDDIT_CLIENT_SECRET', reddit_auth.get('client_secret')),
        'user_agent': os.getenv('REDDIT_USER_AGENT', reddit_auth.get('user_agent', 'SocialMediaAnalyzer/0.1')),
        'username': os.getenv('REDDIT_USERNAME', reddit_auth.get('username')),
        'password': os.getenv('REDDIT_PASSWORD', reddit_auth.get('password'))
    })
    api_auth['reddit'] = reddit_auth
    
    # Update config with API auth
    config['api_auth'] = api_auth
    
    return config
