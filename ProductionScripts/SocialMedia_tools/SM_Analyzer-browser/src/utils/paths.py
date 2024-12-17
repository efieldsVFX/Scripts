from pathlib import Path
import os
from datetime import datetime

def get_desktop_path():
    """Get the user's desktop path"""
    return Path(os.path.expanduser("~/Desktop"))

def setup_analysis_folders(subreddits):
    """Create output folders for analysis results"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    desktop = get_desktop_path()
    base_dir = desktop / "RedditAnalysis"
    base_dir.mkdir(exist_ok=True)
    
    # Create a folder name from subreddits
    folder_name = '_'.join(subreddits) if subreddits else 'general'
    analysis_dir = base_dir / f"{folder_name}_{timestamp}"
    analysis_dir.mkdir(exist_ok=True)
    
    # Create common data and visualization directories
    data_dir = analysis_dir / 'data'
    vis_dir = analysis_dir / 'visualizations'
    data_dir.mkdir(exist_ok=True)
    vis_dir.mkdir(exist_ok=True)
    
    # Create subreddit-specific subdirectories if provided
    if subreddits:
        for subreddit in subreddits:
            subreddit_dir = analysis_dir / subreddit
            subreddit_dir.mkdir(exist_ok=True)
            (subreddit_dir / 'data').mkdir(exist_ok=True)
            (subreddit_dir / 'visualizations').mkdir(exist_ok=True)
    
    return analysis_dir 