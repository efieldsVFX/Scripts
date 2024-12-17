"""
Network Manager Module
Handles network connectivity for both wired and wireless connections
"""

import os
import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional
import requests
from urllib.parse import urljoin
import re

logger = logging.getLogger(__name__)

class NetworkManager:
    def __init__(self, config_path: str = None):
        self.config_path = config_path or os.path.join(os.path.dirname(__file__), '../config/app_config.json')
        self.load_config()
        self.current_connection = None
        self.current_network = None
        self.session = requests.Session()
        
    def load_config(self):
        """Load network configuration from app_config.json"""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            self.config = config.get('network', {})
            logger.info("Network configuration loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load network configuration: {e}")
            self.config = {}
            
    def check_connection(self) -> bool:
        """Check if there is an active network connection"""
        try:
            # Try multiple reliable hosts
            test_urls = [
                'https://api.github.com',
                'https://www.google.com',
                'https://www.microsoft.com'
            ]
            
            for url in test_urls:
                try:
                    response = requests.get(url, timeout=5)
                    if response.status_code == 200:
                        return True
                except requests.RequestException:
                    continue
                    
            return False
            
        except Exception as e:
            logger.error(f"Error checking connection: {e}")
            return False
            
    def get_active_connection(self) -> Optional[str]:
        """Get the currently active connection type (wired/wireless)"""
        if self.current_connection:
            return self.current_connection
            
        # Check wired first
        if self._check_wired_connection():
            self.current_connection = 'wired'
            return 'wired'
            
        # Then check wireless
        if self._check_wireless_connection():
            self.current_connection = 'wireless'
            return 'wireless'
            
        return None
        
    def _check_wired_connection(self) -> bool:
        """Check if wired connection is available and active"""
        if not self.config.get('connections', {}).get('wired', {}).get('enabled', False):
            return False
            
        interface = self.config['connections']['wired']['interface']
        try:
            # Check if the network interface exists and is up
            return os.path.exists(f"/sys/class/net/{interface}")
        except Exception as e:
            logger.error(f"Error checking wired connection: {e}")
            return False
            
    def _check_wireless_connection(self) -> bool:
        """Check if wireless connection is available and active"""
        if not self.config.get('connections', {}).get('wireless', {}).get('enabled', False):
            return False
            
        interface = self.config['connections']['wireless']['interface']
        try:
            # Check if the wireless interface exists and is up
            return os.path.exists(f"/sys/class/net/{interface}")
        except Exception as e:
            logger.error(f"Error checking wireless connection: {e}")
            return False
            
    def connect(self, connection_type: str = None) -> bool:
        """
        Establish network connection
        
        Args:
            connection_type: 'wired' or 'wireless'. If None, try both in order.
        
        Returns:
            bool: True if connection established successfully
        """
        if connection_type and connection_type not in ['wired', 'wireless']:
            raise ValueError("connection_type must be 'wired' or 'wireless'")
            
        if connection_type:
            return self._connect_specific(connection_type)
            
        # Try wired first, then wireless
        if self._connect_specific('wired'):
            return True
        return self._connect_specific('wireless')
        
    def _connect_specific(self, connection_type: str) -> bool:
        """Establish specific type of connection with retry logic"""
        config = self.config['connections'][connection_type]
        if not config.get('enabled', False):
            logger.warning(f"{connection_type} connection is disabled in config")
            return False
            
        retry_config = config.get('retry_config', {})
        max_attempts = retry_config.get('max_attempts', 3)
        backoff_factor = retry_config.get('backoff_factor', 1.5)
        
        for attempt in range(max_attempts):
            try:
                if connection_type == 'wired':
                    success = self._establish_wired_connection()
                else:
                    success = self._establish_wireless_connection()
                    
                if success:
                    self.current_connection = connection_type
                    logger.info(f"Successfully established {connection_type} connection")
                    return True
                    
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed for {connection_type} connection: {e}")
                
            if attempt < max_attempts - 1:
                wait_time = backoff_factor ** attempt
                logger.info(f"Waiting {wait_time:.1f}s before next attempt...")
                time.sleep(wait_time)
                
        return False
        
    def _establish_wired_connection(self) -> bool:
        """Establish wired network connection"""
        config = self.config['connections']['wired']
        interface = config['interface']
        
        try:
            # Check if interface exists
            if not os.path.exists(f"/sys/class/net/{interface}"):
                logger.error(f"Wired interface {interface} not found")
                return False
                
            # If using DHCP, attempt to get IP address
            if config.get('dhcp', True):
                # In a real implementation, you would use platform-specific
                # commands to request DHCP address
                pass
                
            return self.check_connection()
            
        except Exception as e:
            logger.error(f"Error establishing wired connection: {e}")
            return False
            
    def _establish_wireless_connection(self) -> bool:
        """Establish wireless network connection"""
        config = self.config['connections']['wireless']
        interface = config['interface']
        
        try:
            # Check if interface exists
            if not os.path.exists(f"/sys/class/net/{interface}"):
                logger.error(f"Wireless interface {interface} not found")
                return False
            
            # Get available networks sorted by priority
            networks = sorted(
                config.get('networks', {}).items(),
                key=lambda x: x[1].get('priority', 999)
            )
            
            for network_name, network_config in networks:
                logger.info(f"Attempting to connect to {network_name}")
                
                if self._connect_to_network(network_name, network_config):
                    self.current_network = network_name
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error establishing wireless connection: {e}")
            return False
            
    def _connect_to_network(self, network_name: str, network_config: dict) -> bool:
        """Connect to a specific wireless network"""
        try:
            if network_config.get('authentication') != 'password':
                logger.error(f"Invalid authentication type for {network_name}")
                return False
                
            password = network_config.get('password')
            if not password:
                logger.error(f"Password not configured for {network_name}")
                return False
                
            # Create and apply Windows WiFi profile
            try:
                # Create XML profile for the network
                profile_content = f'''<?xml version="1.0"?>
                <WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
                    <name>{network_name}</name>
                    <SSIDConfig>
                        <SSID>
                            <name>{network_name}</name>
                        </SSID>
                    </SSIDConfig>
                    <connectionType>ESS</connectionType>
                    <connectionMode>auto</connectionMode>
                    <MSM>
                        <security>
                            <authEncryption>
                                <authentication>WPA2PSK</authentication>
                                <encryption>AES</encryption>
                                <useOneX>false</useOneX>
                            </authEncryption>
                            <sharedKey>
                                <keyType>passPhrase</keyType>
                                <protected>false</protected>
                                <keyMaterial>{password}</keyMaterial>
                            </sharedKey>
                        </security>
                    </MSM>
                </WLANProfile>'''
                
                # Save profile to temporary file
                profile_path = os.path.join(os.environ['TEMP'], f'{network_name.lower()}_wifi_profile.xml')
                with open(profile_path, 'w') as f:
                    f.write(profile_content)
                
                # Add profile and connect
                os.system(f'netsh wlan add profile filename="{profile_path}"')
                os.system(f'netsh wlan connect name="{network_name}"')
                
                # Clean up
                os.remove(profile_path)
                
                # Wait for connection to establish
                time.sleep(5)
                
                # Verify connection
                if self.check_connection():
                    logger.info(f"Successfully connected to {network_name}")
                    return True
                else:
                    logger.error(f"Failed to verify connection to {network_name}")
                    return False
                
            except Exception as e:
                logger.error(f"Failed to configure {network_name} network: {e}")
                return False
            
        except Exception as e:
            logger.error(f"Error connecting to {network_name}: {e}")
            return False
            
    def setup_proxy(self) -> bool:
        """Configure proxy settings if enabled"""
        proxy_config = self.config.get('proxy', {})
        if not proxy_config.get('enabled', False):
            return True
            
        try:
            proxy_host = proxy_config.get('host')
            proxy_port = proxy_config.get('port')
            
            if proxy_config.get('auth', {}).get('required', False):
                username = proxy_config['auth'].get('username')
                password = proxy_config['auth'].get('password')
                proxy_url = f"http://{username}:{password}@{proxy_host}:{proxy_port}"
            else:
                proxy_url = f"http://{proxy_host}:{proxy_port}"
                
            # Set environment variables for requests
            os.environ['HTTP_PROXY'] = proxy_url
            os.environ['HTTPS_PROXY'] = proxy_url
            
            logger.info("Proxy configuration applied successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error setting up proxy: {e}")
            return False
            
    def handle_connection_loss(self) -> bool:
        """
        Handle network connection loss with fallback logic
        
        Returns:
            bool: True if connection restored successfully
        """
        fallback_config = self.config.get('fallback', {})
        if not fallback_config.get('enabled', True):
            return False
            
        max_retries = fallback_config.get('max_retries', 5)
        retry_interval = fallback_config.get('retry_interval', 60)
        
        logger.warning("Network connection lost. Attempting to restore...")
        
        for attempt in range(max_retries):
            logger.info(f"Restoration attempt {attempt + 1}/{max_retries}")
            
            # Try to reconnect with current connection type first
            if self.current_connection:
                if self._connect_specific(self.current_connection):
                    return True
                    
            # If that fails, try the other connection type
            other_type = 'wireless' if self.current_connection == 'wired' else 'wired'
            if self._connect_specific(other_type):
                return True
                
            if attempt < max_retries - 1:
                logger.info(f"Waiting {retry_interval}s before next attempt...")
                time.sleep(retry_interval)
                
        logger.error("Failed to restore network connection after all attempts")
        return False
