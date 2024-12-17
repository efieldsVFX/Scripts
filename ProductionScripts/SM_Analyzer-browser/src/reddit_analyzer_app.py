import sys
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow
import logging
import signal
from collectors.reddit_collector import RedditCollector
import json
from pathlib import Path
from typing import Dict

logger = logging.getLogger(__name__)

def handle_exception(exc_type, exc_value, exc_traceback):
    """Global exception handler"""
    if issubclass(exc_type, KeyboardInterrupt):
        # Handle keyboard interrupt differently
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    # You might want to show a dialog to the user here
    sys.__excepthook__(exc_type, exc_value, exc_traceback)

def setup_signal_handlers(window):
    """Setup signal handlers for graceful shutdown"""
    signal_handler.window = window
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

def setup_logging():
    """Configure application logging"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "app.log"),
            logging.StreamHandler()
        ]
    )
    
    # Set third-party loggers to WARNING
    logging.getLogger("praw").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

def load_config() -> Dict:
    """Load application configuration"""
    try:
        with open("config/app_config.json") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        return {}

def signal_handler(signum, frame):
    # Log the termination signal
    logging.info(f"Received signal {signum}. Initiating graceful shutdown...")
    # Get the main window instance and trigger data saving
    if hasattr(signal_handler, 'window') and signal_handler.window:
        # Add cancellation before saving state
        signal_handler.window.cancel_current_operations()
        signal_handler.window.save_current_state()
    # Exit the application
    QApplication.quit()

def main():
    """Main application entry point"""
    try:
        # Set up exception handling
        sys.excepthook = handle_exception
        
        # Set up logging
        setup_logging()
        logger.info("Starting Reddit Analyzer App")
        
        # Load configuration
        config = load_config()
        logger.info("Configuration loaded successfully")
        
        # Initialize Reddit collector
        reddit_collector = RedditCollector(config['api_auth']['reddit'])
        
        # Get EDGLRD subreddit stats
        subreddit_stats = reddit_collector.get_subreddit_stats()
        logger.info(f"EDGLRD Subreddit Stats: {subreddit_stats}")
        
        # Get top posts from last month
        top_posts = reddit_collector.get_top_posts(time_filter='month', limit=10)
        logger.info(f"Retrieved {len(top_posts)} top posts from r/EDGLRD")
        
        # Initialize Qt application
        app = QApplication(sys.argv)
        
        # Create and show main window
        window = MainWindow(reddit_collector)
        window.show()
        
        # Set up signal handlers
        setup_signal_handlers(window)
        
        return app.exec()
        
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())