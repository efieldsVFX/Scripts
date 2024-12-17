"""
Server Module
Handles network access for both wired and wireless users
"""

import os
import sys

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

import json
import logging
from pathlib import Path
from flask import Flask, jsonify, request
from flask_cors import CORS
import socket
import netifaces
from src.utils.sample_data import get_cached_sample_data, generate_content_ideas

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app and CORS
app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"],
        "supports_credentials": True
    }
})

# Basic route for testing
@app.route('/')
def index():
    """Root endpoint"""
    return jsonify({
        'status': 'running',
        'server_ip': '192.168.1.67',
        'port': 5000
    })

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})

@app.route('/info')
def server_info():
    """Get server information"""
    return jsonify({
        'ips': get_local_ips(),
        'config': load_config()
    })

@app.route('/api/analytics/data')
def get_analytics_data():
    """Get analytics data for the dashboard"""
    try:
        # For now, return sample data
        data = get_cached_sample_data()
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error getting analytics data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/content/ideas', methods=['POST'])
def generate_ideas_endpoint():
    """Generate and store content ideas"""
    try:
        data = get_cached_sample_data()
        if not data:
            logger.error("Failed to get sample data")
            return jsonify({'error': 'Failed to get sample data'}), 500
        
        # Generate new ideas for each platform
        generated_ideas = {}
        for platform in ['Instagram', 'Twitter', 'TikTok', 'YouTube']:
            if platform in data:
                platform_data = data[platform]
                generated_ideas[platform] = generate_content_ideas(platform, platform_data)
        
        # Create data directory if it doesn't exist
        data_dir = os.path.join(project_root, 'data')
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        
        # Store ideas in a file
        ideas_path = os.path.join(data_dir, 'content_ideas.json')
        
        with open(ideas_path, 'w') as f:
            json.dump(generated_ideas, f, indent=2)
        
        logger.info(f"Successfully generated and stored content ideas at {ideas_path}")
        return jsonify(generated_ideas)
    except Exception as e:
        logger.error(f"Error generating content ideas: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/content/ideas', methods=['GET'])
def get_content_ideas():
    """Get stored content ideas"""
    try:
        ideas_path = os.path.join(project_root, 'data', 'content_ideas.json')
        if os.path.exists(ideas_path):
            with open(ideas_path, 'r') as f:
                return jsonify(json.load(f))
        return jsonify({})
    except Exception as e:
        logger.error(f"Error getting content ideas: {e}")
        return jsonify({'error': str(e)}), 500

def load_config():
    """Load server configuration"""
    config_path = os.path.join(os.path.dirname(__file__), 'config/app_config.json')
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return {}

def get_local_ips():
    """Get all local IP addresses"""
    ips = []
    try:
        # Get all network interfaces
        interfaces = netifaces.interfaces()
        
        for iface in interfaces:
            addrs = netifaces.ifaddresses(iface)
            # Get IPv4 addresses
            if netifaces.AF_INET in addrs:
                for addr in addrs[netifaces.AF_INET]:
                    ip = addr['addr']
                    # Include all IPs for debugging
                    ips.append(ip)
                    logger.info(f"Found IP address: {ip} on interface {iface}")
        
        return ips
    except Exception as e:
        logger.error(f"Error getting local IPs: {e}")
        return []

def get_wifi_ip():
    """Get IP address for WiFi networks (EDGLRD and EDGLRD_GUEST)"""
    ips = get_local_ips()
    # Return the first non-localhost IP as it's likely the WiFi IP
    for ip in ips:
        if not ip.startswith('127.'):
            logger.info(f"Using WiFi IP: {ip}")
            return ip
    return '0.0.0.0'  # Fallback to all interfaces if no specific IP found

def get_network_ip():
    """Get the network IP address"""
    try:
        # Get all network interfaces
        interfaces = netifaces.interfaces()
        for iface in interfaces:
            addrs = netifaces.ifaddresses(iface)
            if netifaces.AF_INET in addrs:
                for addr in addrs[netifaces.AF_INET]:
                    ip = addr['addr']
                    # Look for the main network IP (not VirtualBox)
                    if ip.startswith('192.168.1.') and ip != '192.168.1.56':
                        return ip
    except Exception as e:
        logger.error(f"Error getting network IP: {e}")
    return '0.0.0.0'

def setup_server():
    """Configure server settings"""
    config = load_config()
    return config

def main():
    """Main server function"""
    try:
        config = setup_server()
        port = config.get('port', 5000)
        
        # Bind to all interfaces to allow access from other computers
        host = '0.0.0.0'
        
        logger.info(f"Starting server on port {port}")
        logger.info("Server will be accessible at:")
        logger.info(f"- Network: http://192.168.1.185:5000")
        logger.info(f"- Local: http://localhost:5000")
        
        app.run(host=host, port=port, debug=True, threaded=True)
        
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
