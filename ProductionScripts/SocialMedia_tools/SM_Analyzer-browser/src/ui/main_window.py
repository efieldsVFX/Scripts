import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from utils import (
    setup_analysis_folders,
    ComplianceManager,
    BrandAlignmentManager,
    InitializationError,
    DataCollectionError,
    AnalysisCancelled
)

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QSpinBox, QTextEdit, QProgressBar, QTabWidget, QTableWidget,
    QTableWidgetItem, QMessageBox, QScrollArea, QGridLayout, QComboBox, 
    QStackedWidget, QGroupBox, QFormLayout, QFileDialog
)
from PySide6.QtCore import Qt, Signal, Slot, QThread, QSize
from PySide6.QtGui import QFont, QIcon, QPixmap
import pandas as pd
from pathlib import Path
from collectors.reddit_collector import RedditCollector
from collectors.twitter_collector import TwitterCollector
from collectors.instagram_collector import InstagramCollector
from collectors.tiktok_collector import TikTokCollector
from collectors.youtube_collector import YouTubeCollector
from analysis.content_analyzer import ContentAnalyzer
from analysis.prompt_generator import PromptGenerator
from analysis.brand_identity_analyzer import BrandIdentityAnalyzer
from analysis.competitive_analyzer import CompetitiveAnalyzer
import logging
import json
import os
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)

class AnalysisWorker(QThread):
    progress = Signal(int)
    error = Signal(str)
    finished = Signal(dict)
    status = Signal(str)

    def __init__(self, collectors, params, compliance_manager, brand_manager):
        super().__init__()
        self.collectors = collectors
        self.params = params
        self.compliance_manager = compliance_manager
        self.brand_manager = brand_manager
        self._cancel_requested = False
        
        try:
            self.output_dir = Path('output/temp')
            self.output_dir.mkdir(parents=True, exist_ok=True)
            
            self.posts_file = self.output_dir / 'temp_posts.csv'
            self.comments_file = self.output_dir / 'temp_comments.csv'
            
            posts_df = pd.DataFrame(columns=[
                'text', 'title', 'created_utc', 'id', 'author', 
                'score', 'num_comments', 'url'
            ])
            comments_df = pd.DataFrame(columns=[
                'body', 'created_utc', 'id', 'author', 
                'score', 'parent_id'
            ])
            
            posts_df.to_csv(self.posts_file, index=False)
            comments_df.to_csv(self.comments_file, index=False)
            
            self.analyzer = ContentAnalyzer(
                posts_file=str(self.posts_file),
                comments_file=str(self.comments_file)
            )
            self.brand_analyzer = BrandIdentityAnalyzer(
                brand_manager.get_brand_values(),
                brand_manager.get_target_audience()
            )
            self.competitive_analyzer = CompetitiveAnalyzer()
            
        except Exception as e:
            logger.error(f"Failed to initialize analyzers: {e}")
            self.cleanup_temp_files()
            raise InitializationError(f"Failed to initialize analysis components: {str(e)}")

    def cleanup_temp_files(self):
        """Clean up temporary files and directories"""
        try:
            if hasattr(self, 'posts_file') and self.posts_file.exists():
                self.posts_file.unlink()
            if hasattr(self, 'comments_file') and self.comments_file.exists():
                self.comments_file.unlink()
            if hasattr(self, 'output_dir') and self.output_dir.exists():
                # Only remove directory if it's empty
                if not any(self.output_dir.iterdir()):
                    self.output_dir.rmdir()
        except Exception as e:
            logger.error(f"Failed to cleanup temporary files: {e}")

    def cancel(self):
        self._cancel_requested = True
        
    def run(self):
        try:
            results = {}
            total_platforms = len([p for p, c in self.collectors.items() if c])
            processed = 0
            
            for platform, collector in self.collectors.items():
                if self._cancel_requested:
                    raise AnalysisCancelled("Analysis cancelled by user")
                    
                if collector and self.params.get(platform):
                    self.status.emit(f"Analyzing {platform}...")
                    
                    try:
                        # Validate data collection parameters
                        if not self.compliance_manager.validate_data_collection(
                            platform, 
                            self.params[platform].keys()
                        ):
                            logger.warning(f"Skipping {platform} due to compliance validation failure")
                            continue
                        
                        # Collect and process data with progress updates
                        platform_data = self._collect_platform_data(platform, collector)
                        
                        if platform_data.empty:
                            logger.warning(f"No data collected for {platform}")
                            continue
                            
                        # Perform analysis
                        results[platform] = self._analyze_platform_data(
                            platform, platform_data)
                        
                        processed += 1
                        self.progress.emit(int(processed / total_platforms * 100))
                        
                    except Exception as e:
                        logger.error(f"Error analyzing {platform}: {e}")
                        results[platform] = {"error": str(e)}

            self.finished.emit(results)
            
        except AnalysisCancelled as e:
            self.error.emit(str(e))
        except Exception as e:
            logger.error(f"Analysis failed: {e}", exc_info=True)
            self.error.emit(f"Analysis failed: {str(e)}")

    def _collect_platform_data(self, platform: str, collector) -> pd.DataFrame:
        """Collect and preprocess platform data"""
        try:
            platform_data = collector.collect_data(**self.params[platform])
            
            # Save data to temporary files
            if not platform_data.empty:
                # Split data into posts and comments if applicable
                if 'type' in platform_data.columns:
                    posts = platform_data[platform_data['type'] == 'post']
                    comments = platform_data[platform_data['type'] == 'comment']
                    
                    if not posts.empty:
                        posts.to_csv(self.posts_file, index=False)
                    if not comments.empty:
                        comments.to_csv(self.comments_file, index=False)
                else:
                    # If no type column, assume all are posts
                    platform_data.to_csv(self.posts_file, index=False)
                    pd.DataFrame().to_csv(self.comments_file, index=False)
            
            return self.compliance_manager.anonymize_data(platform_data)
        except Exception as e:
            logger.error(f"Data collection failed for {platform}: {e}")
            raise DataCollectionError(f"Failed to collect {platform} data: {str(e)}")

    def _analyze_platform_data(self, platform: str, data: pd.DataFrame) -> Dict:
        """Perform comprehensive platform analysis"""
        return {
            'content_analysis': self.analyzer.analyze_content(
                data,
                self.brand_manager.get_platform_guidelines(platform)
            ),
            'brand_alignment': self.brand_analyzer.analyze_content_alignment(data),
            'competitive_analysis': self.competitive_analyzer.analyze_market_position(
                data,
                self.collect_competitor_data(platform)
            ),
            'recommendations': self.brand_analyzer.generate_content_recommendations({
                'platform': platform,
                'data': data
            })
        }

    def __del__(self):
        """Cleanup temporary files on object destruction"""
        self.cleanup_temp_files()

    def collect_competitor_data(self, platform: str) -> pd.DataFrame:
        """Collect competitor data for comparative analysis"""
        try:
            # Get competitor handles/names from brand manager
            competitor_data = pd.DataFrame()
            platform_guidelines = self.brand_manager.get_platform_guidelines(platform)
            competitors = platform_guidelines.get('competitors', [])
            
            if not competitors:
                logger.info(f"No competitors defined for {platform}")
                return competitor_data
            
            # Collect data for each competitor
            for competitor in competitors:
                try:
                    competitor_params = {
                        'username': competitor,
                        'limit': self.params[platform].get('limit', 100),
                        'timeframe': self.params[platform].get('timeframe', '30d')
                    }
                    
                    if platform in self.collectors:
                        comp_data = self.collectors[platform].collect_data(**competitor_params)
                        if not comp_data.empty:
                            comp_data['competitor'] = competitor
                            competitor_data = pd.concat([competitor_data, comp_data])
                            
                except Exception as e:
                    logger.warning(f"Failed to collect data for competitor {competitor}: {e}")
                    continue
                
            return self.compliance_manager.anonymize_data(competitor_data)
            
        except Exception as e:
            logger.error(f"Error collecting competitor data for {platform}: {e}")
            return pd.DataFrame()

class MainWindow(QMainWindow):
    def __init__(self, config=None):
        super().__init__()
        self.config = config or {}
        self.setup_managers()
        self.setup_ui()
        self.apply_theme()
        self.setup_connections()
        
        self.current_analysis = None
        self.results = {}

    def setup_managers(self):
        self.compliance_manager = ComplianceManager()
        self.brand_manager = BrandAlignmentManager(
            self.load_brand_values(),
            self.load_content_guidelines()
        )
        
        self.collectors = {
            'reddit': RedditCollector(),
            'twitter': None,  # Future implementation
            'instagram': None,  # Future implementation
            'tiktok': None,  # Future implementation
            'youtube': None  # Future implementation
        }

    def setup_ui(self):
        """Setup the main UI structure"""
        self.setWindowTitle("Social Media Content Analyzer")
        self.setMinimumSize(800, 600)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create stacked widget for different screens
        self.main_stack = QStackedWidget()
        layout.addWidget(self.main_stack)
        
        # Add screens
        self.main_stack.addWidget(self.create_platform_selector())
        self.main_stack.addWidget(self.create_analysis_form())
        self.main_stack.addWidget(self.create_progress_screen())
        self.main_stack.addWidget(self.create_results_screen())
        
        # Create status bar
        self.status_bar = self.statusBar()
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.hide()
        self.status_bar.addPermanentWidget(self.progress_bar)

    def create_platform_selector(self):
        """Create platform selection screen"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Header
        header = QLabel("Select Platforms to Analyze")
        header.setAlignment(Qt.AlignCenter)
        header.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(header)
        
        # Platform buttons grid
        grid = QGridLayout()
        self.platform_buttons = {}
        
        platforms = {
            'Reddit': {'icon': 'assets/icons/reddit.png', 'enabled': True},
            'Twitter': {'icon': 'assets/icons/twitter.png', 'enabled': False},
            'Instagram': {'icon': 'assets/icons/instagram.png', 'enabled': False},
            'TikTok': {'icon': 'assets/icons/tiktok.png', 'enabled': False},
            'YouTube': {'icon': 'assets/icons/youtube.png', 'enabled': False}
        }
        
        for i, (platform, info) in enumerate(platforms.items()):
            container = QGroupBox()
            container_layout = QVBoxLayout(container)
            
            # Create button with icon if available
            btn = QPushButton(platform)
            if os.path.exists(info['icon']):
                btn.setIcon(QIcon(info['icon']))
            btn.setCheckable(True)
            btn.setEnabled(info['enabled'])
            btn.setMinimumSize(120, 80)
            
            self.platform_buttons[platform] = btn
            container_layout.addWidget(btn)
            
            # Add to grid, 3 buttons per row
            grid.addWidget(container, i // 3, i % 3)
        
        layout.addLayout(grid)
        
        # Continue button
        continue_btn = QPushButton("Continue →")
        continue_btn.clicked.connect(self.show_analysis_form)
        layout.addWidget(continue_btn, alignment=Qt.AlignRight)
        
        layout.addStretch()
        return widget

    def create_analysis_form(self):
        """Create analysis input form"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # Reddit-specific inputs
        self.subreddit_input = QLineEdit()
        self.post_limit = QSpinBox()
        self.post_limit.setRange(10, 1000)
        self.post_limit.setValue(100)
        
        self.time_filter = QComboBox()
        self.time_filter.addItems(['day', 'week', 'month', 'year', 'all'])
        
        layout.addRow("Subreddit:", self.subreddit_input)
        layout.addRow("Post Limit:", self.post_limit)
        layout.addRow("Time Filter:", self.time_filter)
        
        # Control buttons
        button_layout = QHBoxLayout()
        back_btn = QPushButton("Back")
        analyze_btn = QPushButton("Start Analysis")
        
        back_btn.clicked.connect(lambda: self.main_stack.setCurrentIndex(0))
        analyze_btn.clicked.connect(self.start_analysis)
        
        button_layout.addWidget(back_btn)
        button_layout.addWidget(analyze_btn)
        layout.addRow(button_layout)
        
        return widget

    def create_progress_screen(self):
        """Create analysis progress screen"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Status label
        self.progress_label = QLabel("Preparing analysis...")
        self.progress_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.progress_label)
        
        # Progress bar
        progress_bar = QProgressBar()
        progress_bar.setMinimum(0)
        progress_bar.setMaximum(100)
        layout.addWidget(progress_bar)
        
        # Cancel button
        cancel_btn = QPushButton("Cancel Analysis")
        cancel_btn.clicked.connect(self.cancel_analysis)
        layout.addWidget(cancel_btn, alignment=Qt.AlignCenter)
        
        layout.addStretch()
        return widget

    def create_results_screen(self):
        """Create modern, user-friendly results display with clear data organization"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Create tabs with modern styling
        self.results_tabs = QTabWidget()
        self.results_tabs.setDocumentMode(True)
        
        # Overview tab with dashboard layout
        overview_tab = self.create_overview_tab()
        metrics_tab = self.create_metrics_tab()
        insights_tab = self.create_insights_tab()
        recommendations_tab = self.create_recommendations_tab()
        
        # Add tabs with icons for better UX
        self.results_tabs.addTab(overview_tab, "Overview")
        self.results_tabs.addTab(metrics_tab, "Metrics")
        self.results_tabs.addTab(insights_tab, "Insights") 
        self.results_tabs.addTab(recommendations_tab, "Recommendations")
        
        # Control buttons with modern styling
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setSpacing(10)
        
        export_btn = QPushButton("Export Results")
        export_btn.setProperty("class", "primary-button")
        export_btn.setMinimumWidth(150)
        
        new_analysis_btn = QPushButton("New Analysis")
        new_analysis_btn.setMinimumWidth(150)
        
        button_layout.addStretch()
        button_layout.addWidget(export_btn)
        button_layout.addWidget(new_analysis_btn)
        
        layout.addWidget(self.results_tabs)
        layout.addWidget(button_container)
        
        return widget

    def create_overview_tab(self):
        """Create overview dashboard with key metrics and visualizations"""
        tab = QWidget()
        layout = QGridLayout(tab)
        layout.setSpacing(20)
        
        # Summary card
        summary_card = QGroupBox("Analysis Summary")
        summary_layout = QVBoxLayout(summary_card)
        self.summary_label = QLabel()
        self.summary_label.setWordWrap(True)
        self.summary_label.setStyleSheet("""
            font-size: 14px;
            line-height: 1.6;
            padding: 10px;
        """)
        summary_layout.addWidget(self.summary_label)
        
        # Stats card with grid layout
        stats_card = QGroupBox("Key Statistics")
        stats_layout = QGridLayout(stats_card)
        self.stats_widgets = {}
        
        stats = ["Engagement Rate", "Sentiment Score", "Post Frequency", "Peak Activity"]
        for i, stat in enumerate(stats):
            label = QLabel(stat)
            value = QLabel("--")
            value.setStyleSheet("font-size: 18px; font-weight: bold;")
            stats_layout.addWidget(label, i // 2, (i % 2) * 2)
            stats_layout.addWidget(value, i // 2, (i % 2) * 2 + 1)
            self.stats_widgets[stat] = value
        
        layout.addWidget(summary_card, 0, 0, 1, 2)
        layout.addWidget(stats_card, 1, 0, 1, 2)
        
        return tab

    def create_metrics_tab(self):
        """Create detailed metrics view with charts and tables"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Metrics Summary Section
        summary_group = QGroupBox("Metrics Summary")
        summary_layout = QVBoxLayout(summary_group)
        
        self.metrics_summary = QTextEdit()
        self.metrics_summary.setReadOnly(True)
        self.metrics_summary.setStyleSheet("""
            QTextEdit {
                background-color: #2b2b2b;
                color: #ffffff;
                border-radius: 8px;
                padding: 15px;
                font-size: 14px;
                line-height: 1.6;
            }
        """)
        summary_layout.addWidget(self.metrics_summary)
        
        # Metrics filter controls
        filter_container = QWidget()
        filter_layout = QHBoxLayout(filter_container)
        filter_layout.setSpacing(10)
        
        self.time_range_combo = QComboBox()
        self.time_range_combo.addItems([
            "Last 7 days",
            "Last 30 days",
            "Last 90 days",
            "All time"
        ])
        
        self.metric_type_combo = QComboBox()
        self.metric_type_combo.addItems([
            "All Metrics",
            "Engagement",
            "Reach",
            "Growth",
            "Sentiment"
        ])
        
        filter_layout.addWidget(QLabel("Time Range:"))
        filter_layout.addWidget(self.time_range_combo)
        filter_layout.addWidget(QLabel("Metric Type:"))
        filter_layout.addWidget(self.metric_type_combo)
        filter_layout.addStretch()
        
        # Detailed metrics table
        self.metrics_table = QTableWidget()
        self.metrics_table.setStyleSheet("""
            QTableWidget {
                background-color: #2b2b2b;
                color: #ffffff;
                border-radius: 8px;
                gridline-color: #3d3d3d;
            }
            QHeaderView::section {
                background-color: #363636;
                color: #ffffff;
                padding: 8px;
                border: none;
                border-bottom: 1px solid #3d3d3d;
            }
            QTableWidget::item {
                padding: 8px;
            }
        """)
        
        # Export button
        export_btn = QPushButton("Export Metrics")
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a90e2;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
        """)
        export_btn.clicked.connect(self.export_metrics)
        
        # Add all components to main layout
        layout.addWidget(summary_group)
        layout.addWidget(filter_container)
        layout.addWidget(self.metrics_table)
        layout.addWidget(export_btn, alignment=Qt.AlignRight)
        
        # Connect filter signals
        self.time_range_combo.currentTextChanged.connect(self.filter_metrics)
        self.metric_type_combo.currentTextChanged.connect(self.filter_metrics)
        
        return tab

    def filter_metrics(self):
        """Filter metrics based on selected time range and metric type"""
        time_range = self.time_range_combo.currentText()
        metric_type = self.metric_type_combo.currentText()
        # Implementation will be added when we have the actual filtering logic
        pass

    def export_metrics(self):
        """Export metrics data to file"""
        try:
            file_name, _ = QFileDialog.getSaveFileName(
                self,
                "Export Metrics",
                "",
                "CSV Files (*.csv);;All Files (*)"
            )
            if file_name:
                # Implementation will be added for actual export logic
                QMessageBox.information(
                    self,
                    "Export Success",
                    "Metrics exported successfully!"
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Error",
                f"Failed to export metrics: {str(e)}"
            )

    def create_insights_tab(self):
        """Create insights tab with detailed analysis results"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Scrollable container for insights
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Container widget for insights content
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(20)
        
        # Insights header
        header = QLabel("Content Analysis Insights")
        header.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #2c3e50;
            padding-bottom: 10px;
        """)
        content_layout.addWidget(header)
        
        # Main insights display
        self.insights_label = QLabel()
        self.insights_label.setWordWrap(True)
        self.insights_label.setTextFormat(Qt.RichText)
        self.insights_label.setStyleSheet("""
            QLabel {
                background-color: #2b2b2b;
                border-radius: 8px;
                padding: 15px;
                line-height: 1.6;
                font-size: 14px;
            }
        """)
        content_layout.addWidget(self.insights_label)
        
        # Filter controls
        filter_container = QWidget()
        filter_layout = QHBoxLayout(filter_container)
        filter_layout.setSpacing(10)
        
        self.insight_type_combo = QComboBox()
        self.insight_type_combo.addItems([
            "All Insights",
            "Sentiment Analysis",
            "Topic Analysis",
            "Engagement Patterns",
            "Content Performance"
        ])
        self.insight_type_combo.currentTextChanged.connect(self.filter_insights)
        
        self.time_range_combo = QComboBox()
        self.time_range_combo.addItems([
            "All Time",
            "Last 7 Days",
            "Last 30 Days",
            "Last 90 Days"
        ])
        self.time_range_combo.currentTextChanged.connect(self.filter_insights)
        
        filter_layout.addWidget(QLabel("Insight Type:"))
        filter_layout.addWidget(self.insight_type_combo)
        filter_layout.addWidget(QLabel("Time Range:"))
        filter_layout.addWidget(self.time_range_combo)
        filter_layout.addStretch()
        
        content_layout.addWidget(filter_container)
        
        # Set the content widget as the scroll area's widget
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        return tab

    def filter_insights(self):
        """Filter insights based on selected criteria"""
        insight_type = self.insight_type_combo.currentText()
        time_range = self.time_range_combo.currentText()
        
        # Update insights display based on filters
        # This will be implemented when we have the actual data filtering logic
        pass

    def start_analysis(self):
        """Start the analysis process"""
        # Validate inputs
        subreddit = self.subreddit_input.text().strip()
        if not subreddit:
            QMessageBox.warning(self, "Missing Input", "Please enter a subreddit name.")
            return
            
        # Prepare analysis parameters
        analysis_params = {
            'reddit': {
                'subreddit': subreddit,
                'limit': self.post_limit.value(),
                'time_filter': self.time_filter.currentText()
            }
        }
        
        # Create and configure worker thread
        self.worker = AnalysisWorker(
            self.collectors,
            analysis_params,
            self.compliance_manager,
            self.brand_manager
        )
        
        # Connect signals
        self.worker.progress.connect(self.update_progress)
        self.worker.status.connect(self.update_status)
        self.worker.error.connect(self.handle_error)
        self.worker.finished.connect(self.handle_analysis_complete)
        
        # Switch to progress screen and start analysis
        self.main_stack.setCurrentIndex(2)
        self.progress_bar.show()
        self.worker.start()

    def update_progress(self, value):
        """Update progress bar during analysis"""
        self.progress_bar.setValue(value)
        self.progress_label.setText(f"Analyzing... {value}%")

    def handle_error(self, error_message):
        """Handle analysis errors"""
        QMessageBox.critical(
            self,
            "Analysis Error",
            f"An error occurred during analysis:\n{error_message}"
        )
        self.main_stack.setCurrentIndex(2)  # Back to analysis screen

    def handle_analysis_complete(self, results):
        """Handle analysis completion"""
        self.results = results
        self.main_stack.setCurrentIndex(3)  # Show results screen

    def load_brand_values(self) -> Dict[str, float]:
        """Load brand values from configuration file"""
        try:
            config_path = Path("config/brand_values.json")
            if config_path.exists():
                with open(config_path, 'r') as f:
                    return json.load(f)
            else:
                # Return default values if config doesn't exist
                return {
                    "professionalism": 0.8,
                    "innovation": 0.7,
                    "reliability": 0.9,
                    "engagement": 0.8
                }
        except Exception as e:
            logger.warning(f"Failed to load brand values: {e}")
            return {}

    def load_content_guidelines(self) -> Dict:
        """Load content guidelines from configuration file"""
        try:
            config_path = Path("config/content_guidelines.json")
            if config_path.exists():
                with open(config_path, 'r') as f:
                    return json.load(f)
            else:
                # Return default guidelines if config doesn't exist
                return {
                    "tone": "professional",
                    "visual_style": "modern",
                    "messaging": "informative"
                }
        except Exception as e:
            logger.warning(f"Failed to load content guidelines: {e}")
            return {}

    def apply_theme(self):
        """Apply production-grade dark theme styling following modern UI/UX standards"""
        self.setStyleSheet("""
            /* Base Theme Colors */
            * {
                outline: none;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen-Sans, Ubuntu, Cantarell, "Helvetica Neue", sans-serif;
            }
            
            QMainWindow, QDialog {
                background-color: #18191c;
            }
            
            /* Typography */
            QLabel {
                color: #dcddde;
                font-size: 13px;
            }
            
            QLabel[heading="true"] {
                font-size: 24px;
                font-weight: 500;
                color: #ffffff;
            }
            
            QLabel[subheading="true"] {
                font-size: 16px;
                font-weight: 500;
                color: #dcddde;
            }
            
            /* Buttons */
            QPushButton {
                padding: 8px 16px;
                border-radius: 4px;
                border: none;
                background-color: #2f3136;
                color: #dcddde;
                font-size: 13px;
                font-weight: 500;
                min-width: 100px;
                min-height: 32px;
            }
            
            QPushButton:hover {
                background-color: #36393f;
            }
            
            QPushButton:pressed {
                background-color: #202225;
            }
            
            QPushButton:disabled {
                background-color: #202225;
                color: #72767d;
            }
            
            QPushButton#primary_button {
                background-color: #5865f2;
                color: white;
            }
            
            QPushButton#primary_button:hover {
                background-color: #4752c4;
            }
            
            QPushButton#primary_button:pressed {
                background-color: #3c45a5;
            }
            
            QPushButton#primary_button:disabled {
                background-color: #3c45a5;
                opacity: 0.5;
            }
            
            QPushButton#destructive_button {
                background-color: #ed4245;
                color: white;
            }
            
            /* Form Elements */
            QLineEdit, QTextEdit, QComboBox, QSpinBox {
                padding: 8px 12px;
                border: 2px solid #202225;
                border-radius: 4px;
                background-color: #2f3136;
                color: #dcddde;
                font-size: 13px;
                selection-background-color: #5865f2;
                selection-color: white;
            }
            
            QLineEdit:hover, QTextEdit:hover, QComboBox:hover, QSpinBox:hover {
                border-color: #36393f;
            }
            
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus {
                border-color: #5865f2;
                background-color: #36393f;
            }
            
            QLineEdit:disabled, QTextEdit:disabled, QComboBox:disabled, QSpinBox:disabled {
                background-color: #202225;
                color: #72767d;
                border-color: #202225;
            }
            
            /* Dropdown/Combo Box */
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            
            QComboBox::down-arrow {
                image: url(resources/icons/chevron-down.svg);
                width: 12px;
                height: 12px;
            }
            
            QComboBox QAbstractItemView {
                background-color: #2f3136;
                border: 1px solid #202225;
                border-radius: 4px;
                selection-background-color: #5865f2;
                selection-color: white;
            }
            
            /* Tabs */
            QTabWidget::pane {
                border: 1px solid #202225;
                border-radius: 4px;
                background-color: #2f3136;
                top: -1px;
            }
            
            QTabBar::tab {
                padding: 8px 16px;
                margin-right: 4px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                background-color: #202225;
                color: #72767d;
                font-size: 13px;
            }
            
            QTabBar::tab:selected {
                background-color: #2f3136;
                color: #ffffff;
            }
            
            QTabBar::tab:hover:!selected {
                background-color: #36393f;
                color: #dcddde;
            }
            
            /* Scrollbars */
            QScrollBar:vertical {
                background-color: #2f3136;
                width: 8px;
                margin: 0;
            }
            
            QScrollBar::handle:vertical {
                background: #202225;
                min-height: 24px;
                border-radius: 4px;
            }
            
            QScrollBar::handle:vertical:hover {
                background: #36393f;
            }
            
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical,
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: none;
                border: none;
            }
            
            /* Tables */
            QTableWidget {
                background-color: #2f3136;
                color: #dcddde;
                gridline-color: #202225;
                border: 1px solid #202225;
                border-radius: 4px;
            }
            
            QTableWidget::item {
                padding: 8px;
            }
            
            QTableWidget::item:selected {
                background-color: #5865f2;
                color: white;
            }
            
            QHeaderView::section {
                background-color: #202225;
                color: #dcddde;
                padding: 8px;
                border: none;
                border-right: 1px solid #2f3136;
                font-weight: 500;
            }
            
            /* Progress Bar */
            QProgressBar {
                border: none;
                border-radius: 4px;
                background-color: #202225;
                text-align: center;
                color: white;
                font-size: 12px;
                min-height: 8px;
            }
            
            QProgressBar::chunk {
                background-color: #5865f2;
                border-radius: 4px;
            }
            
            /* Group Box */
            QGroupBox {
                border: 1px solid #202225;
                border-radius: 4px;
                margin-top: 16px;
                padding-top: 16px;
                color: #dcddde;
                font-weight: 500;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 4px;
            }
            
            /* Tooltips */
            QToolTip {
                background-color: #18191c;
                color: #dcddde;
                border: 1px solid #202225;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 12px;
            }
        """)

    def show_analysis_screen(self):
        """Show the analysis screen with selected platforms"""
        # Get selected platforms
        selected_platforms = [
            platform for platform, btn in self.platform_buttons.items()
            if btn.isChecked()
        ]
        
        if not selected_platforms:
            QMessageBox.warning(
                self,
                "No Platform Selected",
                "Please select at least one platform to analyze."
            )
            return
        
        # Update header with selected platforms
        platform_list = ", ".join(selected_platforms)
        self.analysis_header.setText(f"<h2>Configure Analysis for: {platform_list}</h2>")
        self.analysis_header.setTextFormat(Qt.RichText)
        self.analysis_header.setAlignment(Qt.AlignCenter)
        
        # Show appropriate platform input form
        if 'Reddit' in selected_platforms:
            self.platform_inputs.setCurrentIndex(0)  # Reddit form
        elif 'Twitter' in selected_platforms:
            self.platform_inputs.setCurrentIndex(1)  # Twitter form
        # Add other platform conditions as needed
        
        # Switch to analysis screen
        self.main_stack.setCurrentIndex(2)

    def start_analysis(self):
        """Start the analysis process with selected parameters"""
        # Collect parameters for each platform
        analysis_params = {}
        
        # Get Reddit parameters if selected
        if self.platform_buttons['Reddit'].isChecked():
            subreddit = self.subreddit_input.text().strip()
            if not subreddit:
                QMessageBox.warning(
                    self,
                    "Missing Input",
                    "Please enter a subreddit name."
                )
                return
            
            analysis_params['reddit'] = {
                'subreddit': subreddit,
                'limit': self.post_limit.value(),
                'time_filter': self.time_filter.currentText()
            }
        
        # Create and start worker thread
        self.worker = AnalysisWorker(self.collectors, analysis_params, self.compliance_manager, self.brand_manager)
        self.worker.progress.connect(self.update_progress)
        self.worker.error.connect(self.handle_error)
        self.worker.finished.connect(self.show_results)
        
        # Show progress screen
        self.progress_bar.setValue(0)
        self.progress_label.setText("Starting analysis...")
        self.main_stack.setCurrentIndex(3)  # Results screen with progress bar
        
        # Start analysis
        self.worker.start()

    def update_progress(self, value):
        """Update progress bar during analysis"""
        self.progress_bar.setValue(value)
        self.progress_label.setText(f"Analyzing... {value}%")

    def handle_error(self, error_message):
        """Handle analysis errors"""
        QMessageBox.critical(
            self,
            "Analysis Error",
            f"An error occurred during analysis:\n{error_message}"
        )
        self.main_stack.setCurrentIndex(2)  # Back to analysis screen

    def show_results(self, results):
        """Display analysis results"""
        self.progress_label.setText("Analysis complete!")
        self.display_results(results)

    def reset_analysis(self):
        """Reset the application to start a new analysis"""
        # Clear any existing results
        self.clear_results()
        
        # Reset platform selections
        for btn in self.platform_buttons.values():
            btn.setChecked(False)
        
        # Reset form inputs
        self.subreddit_input.clear()
        self.post_limit.setValue(100)
        self.time_filter.setCurrentIndex(0)
        
        # Reset progress indicators
        self.progress_bar.setValue(0)
        self.progress_label.setText("")
        
        # Show platform selector screen
        self.main_stack.setCurrentIndex(1)

    def clear_results(self):
        """Clear all analysis results"""
        # Clear results containers
        if hasattr(self, 'results_tabs'):
            self.results_tabs.clear()
        
        # Reset any visualizations
        for widget in self.findChildren(QWidget):
            if isinstance(widget, (QTableWidget, QTextEdit)):
                widget.clear()

    def cancel_current_operations(self):
        """Cancel any ongoing analysis operations"""
        if hasattr(self, 'worker') and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
            self.handle_error("Analysis cancelled by user")

    def save_current_state(self):
        """Save the current application state"""
        state = {
            'selected_platforms': [
                platform for platform, btn in self.platform_buttons.items()
                if btn.isChecked()
            ],
            'reddit_params': {
                'subreddit': self.subreddit_input.text(),
                'limit': self.post_limit.value(),
                'time_filter': self.time_filter.currentText()
            } if hasattr(self, 'subreddit_input') else None
        }
        
        try:
            with open('app_state.json', 'w') as f:
                json.dump(state, f)
        except Exception as e:
            logger.error(f"Failed to save application state: {e}")

    def load_brand_values(self) -> Dict:
        """Load brand values from configuration"""
        try:
            with open('config/brand_values.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}  # Return empty dict if config doesn't exist

    def load_content_guidelines(self) -> Dict:
        """Load content guidelines from configuration"""
        try:
            with open('config/content_guidelines.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}  # Return empty dict if config doesn't exist

    def export_results(self):
        """Export analysis results to files"""
        try:
            # Get selected subreddits
            subreddits = []
            if hasattr(self, 'subreddit_input'):
                subreddits = [self.subreddit_input.text().strip()]
            
            # Create output folders
            output_dir = setup_analysis_folders(subreddits)
            
            # Export data tables
            if hasattr(self, 'results_tabs'):
                for i in range(self.results_tabs.count()):
                    tab = self.results_tabs.widget(i)
                    tab_name = self.results_tabs.tabText(i)
                    
                    # Export tables
                    for table in tab.findChildren(QTableWidget):
                        if table.rowCount() > 0:
                            df = self._table_to_dataframe(table)
                            csv_path = output_dir / 'data' / f'{tab_name}_{table.objectName()}.csv'
                            df.to_csv(csv_path, index=False)
                    
                    # Export text content
                    for text_edit in tab.findChildren(QTextEdit):
                        if text_edit.toPlainText():
                            txt_path = output_dir / 'data' / f'{tab_name}_{text_edit.objectName()}.txt'
                            with open(txt_path, 'w', encoding='utf-8') as f:
                                f.write(text_edit.toPlainText())
            
            # Show success message
            QMessageBox.information(
                self,
                "Export Complete",
                f"Results exported successfully to:\n{output_dir}"
            )
            
        except Exception as e:
            logger.error(f"Failed to export results: {e}")
            QMessageBox.critical(
                self,
                "Export Error",
                f"Failed to export results:\n{str(e)}"
            )

    def _table_to_dataframe(self, table: QTableWidget) -> pd.DataFrame:
        """Convert QTableWidget to pandas DataFrame"""
        # Get headers
        headers = []
        for j in range(table.columnCount()):
            headers.append(table.horizontalHeaderItem(j).text())
        
        # Get data
        data = []
        for i in range(table.rowCount()):
            row = []
            for j in range(table.columnCount()):
                item = table.item(i, j)
                row.append(item.text() if item else '')
            data.append(row)
        
        return pd.DataFrame(data, columns=headers)

    def display_results(self, results: dict):
        """Display analysis results with improved formatting"""
        self.main_stack.setCurrentIndex(3)
        
        # Format metrics summary with modern styling
        metrics_html = "<div style='line-height: 1.6;'>"
        for platform, data in results.items():
            if 'content_analysis' in data:
                metrics = data['content_analysis'].get('metrics', {})
                metrics_html += f"""
                    <div style='margin-bottom: 20px;'>
                        <h3 style='color: #ffffff; margin-bottom: 10px;'>{platform}</h3>
                        <div style='display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px;'>
                """
                
                for metric, value in metrics.items():
                    metrics_html += f"""
                        <div style='background: #36393f; padding: 15px; border-radius: 8px;'>
                            <div style='color: #72767d; font-size: 12px;'>{metric}</div>
                            <div style='color: #ffffff; font-size: 18px; font-weight: 500;'>{value}</div>
                        </div>
                    """
                metrics_html += "</div></div>"
        metrics_html += "</div>"
        self.metrics_summary.setText(metrics_html)
        
        # Format insights with modern styling
        insights_html = "<div style='line-height: 1.6;'>"
        for platform, data in results.items():
            if 'content_analysis' in data:
                insights_html += f"""
                    <div style='margin-bottom: 20px;'>
                        <h3 style='color: #ffffff; margin-bottom: 10px;'>{platform}</h3>
                        <div style='background: #36393f; padding: 15px; border-radius: 8px;'>
                """
                
                if 'brand_alignment' in data:
                    score = data['brand_alignment'].get('overall_score', 0)
                    insights_html += f"""
                        <div style='margin-bottom: 10px;'>
                            <span style='color: #72767d;'>Brand Alignment Score:</span>
                            <span style='color: #ffffff; font-weight: 500;'> {score:.1%}</span>
                        </div>
                    """
                
                insights_html += f"""
                        <div style='color: #dcddde;'>
                            Analyzed {len(data['content_analysis'])} posts/comments
                        </div>
                    </div>
                    </div>
                """
        insights_html += "</div>"
        self.insights_label.setText(insights_html)
        
        # Format recommendations with modern styling
        recommendations_html = "<div style='line-height: 1.6;'>"
        for platform, data in results.items():
            if 'recommendations' in data:
                recommendations_html += f"""
                    <div style='margin-bottom: 20px;'>
                        <h3 style='color: #ffffff; margin-bottom: 10px;'>{platform} Recommendations</h3>
                        <ul style='margin: 0; padding-left: 20px;'>
                """
                
                for rec in data['recommendations']:
                    recommendations_html += f"""
                        <li style='color: #dcddde; margin-bottom: 8px;'>{rec}</li>
                    """
                recommendations_html += "</ul></div>"
        recommendations_html += "</div>"
        self.recommendations_list.setHtml(recommendations_html)

    def collect_competitor_data(self, platform: str) -> dict:
        """Collect competitor data for comparative analysis"""
        try:
            # Load competitor configuration
            with open('config/competitors.json', 'r') as f:
                competitors = json.load(f)
            
            competitor_data = {}
            if platform in competitors:
                for competitor in competitors[platform]:
                    # Use the appropriate collector to gather competitor data
                    if platform == 'reddit':
                        collector = RedditCollector()
                        competitor_data[competitor] = collector.collect_data(
                            subreddit=competitor,
                            limit=100,  # Reasonable default
                            time_filter='month'
                        )
                    # Add other platforms as needed
            
            return competitor_data
            
        except Exception as e:
            logger.error(f"Failed to collect competitor data: {e}")
            return {}

    def get_brand_values(self) -> Dict[str, float]:
        """Get brand values with default fallbacks"""
        defaults = {
            "authenticity": 0.8,
            "innovation": 0.7,
            "customer_focus": 0.9,
            "quality": 0.85
        }
        
        try:
            with open('config/brand_values.json', 'r') as f:
                values = json.load(f)
                # Merge with defaults, preferring configured values
                return {**defaults, **values}
        except Exception as e:
            logger.warning(f"Using default brand values: {e}")
            return defaults

    def get_target_audience(self) -> Dict[str, any]:
        """Get target audience configuration"""
        defaults = {
            "age_range": [25, 45],
            "interests": ["technology", "business", "innovation"],
            "engagement_level": "high",
            "platform_preferences": {
                "reddit": 0.8,
                "twitter": 0.7,
                "linkedin": 0.9
            }
        }
        
        try:
            with open('config/target_audience.json', 'r') as f:
                config = json.load(f)
                return {**defaults, **config}
        except Exception as e:
            logger.warning(f"Using default target audience: {e}")
            return defaults

    def closeEvent(self, event):
        """Handle application closure"""
        try:
            # Cancel any running operations
            self.cancel_current_operations()
            
            # Save current state
            self.save_current_state()
            
            # Accept the close event
            event.accept()
            
        except Exception as e:
            logger.error(f"Error during application closure: {e}")
            event.accept()  # Close anyway to prevent hanging

    def setup_connections(self):
        """Setup signal/slot connections"""
        # Add any additional connections here
        pass

    def cancel_analysis(self):
        """Cancel ongoing analysis"""
        if hasattr(self, 'worker') and self.worker.isRunning():
            self.worker.cancel()
            self.progress_label.setText("Cancelling analysis...")

    def start_new_analysis(self):
        """Reset UI for new analysis"""
        self.main_stack.setCurrentIndex(0)
        self.progress_bar.hide()
        self.progress_bar.setValue(0)
        self.subreddit_input.clear()
        self.post_limit.setValue(100)
        self.time_filter.setCurrentIndex(0)

    def update_status(self, status: str):
        """Update status message"""
        self.progress_label.setText(status)

    def export_results(self):
        """Export analysis results"""
        try:
            # Create export directory
            timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
            output_dir = Path(f'output/analysis_{timestamp}')
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Export raw data
            data_dir = output_dir / 'data'
            data_dir.mkdir(exist_ok=True)
            
            # Save results as JSON
            with open(output_dir / 'analysis_results.json', 'w') as f:
                json.dump(self.results, f, indent=2)
            
            # Export visualizations if any
            if hasattr(self, 'results_tabs'):
                self._export_tab_contents(output_dir)
            
            QMessageBox.information(
                self,
                "Export Complete",
                f"Results exported successfully to:\n{output_dir}"
            )
            
        except Exception as e:
            logger.error(f"Failed to export results: {e}")
            QMessageBox.critical(
                self,
                "Export Error",
                f"Failed to export results:\n{str(e)}"
            )

    def _export_tab_contents(self, output_dir: Path):
        """Export contents of all result tabs"""
        for i in range(self.results_tabs.count()):
            tab = self.results_tabs.widget(i)
            tab_name = self.results_tabs.tabText(i)
            
            # Export tables
            for table in tab.findChildren(QTableWidget):
                if table.rowCount() > 0:
                    df = self._table_to_dataframe(table)
                    df.to_csv(output_dir / 'data' / f'{tab_name}_{table.objectName()}.csv', 
                             index=False)
            
            # Export text content
            for text_edit in tab.findChildren(QTextEdit):
                if text_edit.toPlainText():
                    with open(output_dir / 'data' / f'{tab_name}_{text_edit.objectName()}.txt', 
                             'w', encoding='utf-8') as f:
                        f.write(text_edit.toPlainText())

    def show_analysis_form(self):
        """Show the analysis form for selected platforms"""
        selected = [p for p, btn in self.platform_buttons.items() if btn.isChecked()]
        if not selected:
            QMessageBox.warning(self, "No Selection", "Please select at least one platform.")
            return
        self.main_stack.setCurrentIndex(1)

    def create_recommendations_tab(self):
        """Create recommendations tab with actionable insights"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Scrollable container
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Container widget
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(20)
        
        # Header
        header = QLabel("Content Strategy Recommendations")
        header.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #2c3e50;
            padding-bottom: 10px;
        """)
        content_layout.addWidget(header)
        
        # Recommendations list
        self.recommendations_list = QTextEdit()
        self.recommendations_list.setReadOnly(True)
        self.recommendations_list.setStyleSheet("""
            QTextEdit {
                background-color: #2b2b2b;
                border-radius: 8px;
                padding: 15px;
                color: #ffffff;
                line-height: 1.6;
                font-size: 14px;
            }
        """)
        content_layout.addWidget(self.recommendations_list)
        
        # Priority filter
        filter_container = QWidget()
        filter_layout = QHBoxLayout(filter_container)
        filter_layout.setSpacing(10)
        
        priority_combo = QComboBox()
        priority_combo.addItems([
            "All Priorities",
            "High Priority",
            "Medium Priority",
            "Low Priority"
        ])
        priority_combo.currentTextChanged.connect(self.filter_recommendations)
        
        category_combo = QComboBox()
        category_combo.addItems([
            "All Categories",
            "Content Strategy",
            "Engagement",
            "Brand Alignment",
            "Platform Specific"
        ])
        category_combo.currentTextChanged.connect(self.filter_recommendations)
        
        filter_layout.addWidget(QLabel("Priority:"))
        filter_layout.addWidget(priority_combo)
        filter_layout.addWidget(QLabel("Category:"))
        filter_layout.addWidget(category_combo)
        filter_layout.addStretch()
        
        content_layout.addWidget(filter_container)
        
        # Export button
        export_btn = QPushButton("Export Recommendations")
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a90e2;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
        """)
        export_btn.clicked.connect(self.export_recommendations)
        content_layout.addWidget(export_btn, alignment=Qt.AlignRight)
        
        # Set the content widget as the scroll area's widget
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        return tab

    def filter_recommendations(self):
        """Filter recommendations based on priority and category"""
        # This will be implemented when we have the actual filtering logic
        pass

    def export_recommendations(self):
        """Export recommendations to a file"""
        # This will be implemented when we have the actual export logic
        pass