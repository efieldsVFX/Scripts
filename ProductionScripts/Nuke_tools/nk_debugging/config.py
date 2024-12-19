import yaml
from pathlib import Path
from typing import Dict, Any
from .exceptions import ConfigError
from .logger import logger
from .constants import CONFIG_PATH

class Config:
    """Configuration manager for the debugging tool."""
    
    def __init__(self, config_path: Path = CONFIG_PATH):
        self.config_path = config_path
        self.settings: Dict[str, Any] = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            if not self.config_path.exists():
                logger.warning(f"Config file not found at {self.config_path}")
                return self._create_default_config()

            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            raise ConfigError(f"Configuration load failed: {e}") from e

    def _create_default_config(self) -> Dict[str, Any]:
        """Create and save default configuration."""
        default_config = {
            'thread_limit': 4,
            'log_retention_days': 30,
            'max_log_files': 100,
            'default_allocator': 'malloc',
            'ui': {
                'window_size': (800, 600),
                'font_size': 10,
                'show_tooltips': True
            }
        }

        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            yaml.dump(default_config, f)

        return default_config

    def save(self):
        """Save current configuration to file."""
        try:
            with open(self.config_path, 'w') as f:
                yaml.dump(self.settings, f)
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            raise ConfigError(f"Configuration save failed: {e}") from e 