from utils.paths import setup_analysis_folders
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                              QLabel, QLineEdit, QPushButton, QSpinBox, 
                              QTextEdit, QProgressBar, QTabWidget, QTableWidget,
                              QTableWidgetItem, QMessageBox, QScrollArea, QGridLayout)
from PySide6.QtCore import Qt, Signal, Slot, QThread
from PySide6.QtGui import QFont, QIcon, QPixmap
import pandas as pd
from pathlib import Path
from collectors.reddit_collector import RedditCollector
from analysis.combined import ContentAnalyzer
import logging
import json
import os
import matplotlib.pyplot as plt
import seaborn as sns

logger = logging.getLogger(__name__)

class RedditAnalyzerWorker(QThread):
    progress = Signal(str)
    finished = Signal(dict)
    error = Signal(str)
    
    def __init__(self, subreddit, keywords, limit):
        super().__init__()
        self.subreddits = subreddit if isinstance(subreddit, list) else [subreddit]
        self.keywords = keywords
        self.limit = limit
        self._cancel_requested = False
        
    def cancel(self):
        self._cancel_requested = True
        
    def run(self):
        try:
            if self._cancel_requested:
                self.progress.emit("Analysis cancelled")
                return
                
            # Setup output directories
            output_dir = setup_analysis_folders(self.subreddits)
            self.progress.emit(f"Created output directory at {output_dir}")
            
            if self._cancel_requested:
                self.progress.emit("Analysis cancelled")
                return
                
            # Data collection
            reddit = RedditCollector()
            all_posts = []
            
            # Collect posts from all subreddits
            for subreddit in self.subreddits:
                if self._cancel_requested:
                    self.progress.emit("Analysis cancelled")
                    return
                    
                self.progress.emit(f"Collecting posts from r/{subreddit}...")
                subreddit_posts = reddit.collect_subreddit_posts(subreddit, limit=self.limit)
                if not subreddit_posts.empty:
                    all_posts.append(subreddit_posts)
            
            if self._cancel_requested:  # Add check after subreddit collection
                self.progress.emit("Analysis cancelled")
                return
                
            # Search for keywords within specified subreddits if both are provided
            if self.keywords and self.subreddits:
                for term in self.keywords:
                    if self._cancel_requested:
                        self.progress.emit("Analysis cancelled")
                        return
                    self.progress.emit(f"Searching for '{term}' in specified subreddits...")
                    search_posts = reddit.search_reddit_posts(term, subreddits=self.subreddits, limit=self.limit)
                    if not search_posts.empty:
                        all_posts.append(search_posts)
            else:
                # Search all of Reddit if no specific subreddits are provided
                for term in self.keywords:
                    if self._cancel_requested:
                        self.progress.emit("Analysis cancelled")
                        return
                    self.progress.emit(f"Searching for '{term}' across all of Reddit...")
                    search_posts = reddit.search_reddit_posts(term, limit=self.limit)
                    if not search_posts.empty:
                        all_posts.append(search_posts)
            
            if self._cancel_requested:  # Add check after keyword search
                self.progress.emit("Analysis cancelled")
                return
                
            if all_posts:
                # Save and analyze combined data
                combined_posts = pd.concat(all_posts, ignore_index=True).drop_duplicates(subset=['id'])
                raw_data_path = output_dir / 'data' / 'reddit_posts.csv'
                combined_posts.to_csv(raw_data_path, index=False)
                
                # Analyze combined data
                analyzer = ContentAnalyzer(raw_data_path, raw_data_path)
                analyzer.set_cancellation_callback(lambda: self._cancel_requested)
                combined_results = analyzer.perform_analysis(
                    progress_callback=lambda p, s: self.progress.emit(s),
                    output_dir=output_dir
                )
                
                # Analyze individual subreddits
                subreddit_results = {}
                for subreddit in self.subreddits:
                    subreddit_posts = combined_posts[combined_posts['subreddit'].str.lower() == subreddit.lower()]
                    if not subreddit_posts.empty:
                        # Save subreddit data
                        subreddit_path = output_dir / subreddit / 'data' / 'reddit_posts.csv'
                        subreddit_posts.to_csv(subreddit_path, index=False)
                        
                        # Analyze subreddit data
                        subreddit_analyzer = ContentAnalyzer(subreddit_path, subreddit_path)
                        subreddit_analyzer.set_cancellation_callback(lambda: self._cancel_requested)
                        subreddit_results[subreddit] = subreddit_analyzer.perform_analysis(
                            progress_callback=lambda p, s: self.progress.emit(f"[r/{subreddit}] {s}"),
                            output_dir=output_dir / subreddit
                        )
                
                # Emit completion with all results
                self.finished.emit({
                    'posts': len(combined_posts),
                    'analysis': combined_results,
                    'subreddit_analysis': subreddit_results,
                    'output_dir': str(output_dir.resolve())
                })
        except Exception as e:
            self.error.emit(str(e))

class MainWindow(QMainWindow):
    def create_topics_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Create table for trending topics
        self.topics_table = QTableWidget()
        self.topics_table.setColumnCount(2)
        self.topics_table.setHorizontalHeaderLabels(["Topic", "Frequency"])
        self.topics_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.topics_table)
        
        return tab

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Reddit Content Analyzer")
        self.setMinimumSize(1024, 768)  # Larger default size
        
        # Apply modern dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: #e0e0e0;
            }
            
            QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 13px;
            }
            
            QTabWidget::pane {
                border: none;
                background: #333333;
                border-radius: 8px;
            }
            
            QTabBar::tab {
                background: #404040;
                color: #b0b0b0;
                padding: 12px 20px;
                border: none;
                margin-right: 4px;
                border-radius: 6px 6px 0 0;
            }
            
            QTabBar::tab:selected {
                background: #333333;
                color: #ffffff;
            }
            
            QTabBar::tab:hover:!selected {
                background: #454545;
                color: #ffffff;
            }
            
            QLineEdit, QSpinBox {
                padding: 10px;
                background: #404040;
                border: 2px solid #505050;
                border-radius: 6px;
                color: #ffffff;
                selection-background-color: #264f78;
            }
            
            QLineEdit:focus, QSpinBox:focus {
                border: 2px solid #0078d4;
                background: #454545;
            }
            
            QLabel {
                color: #e0e0e0;
                font-size: 13px;
            }
            
            QPushButton {
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: 500;
                background: #404040;
                border: 1px solid #505050;
                color: #e0e0e0;
            }
            
            QPushButton:hover {
                background: #454545;
                border: 1px solid #606060;
            }
            
            QPushButton#analyze_btn {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #2ecc71,
                    stop: 0.4 #29b765,
                    stop: 0.5 #27ae60,
                    stop: 1.0 #219a52
                );
                border: 1px solid #27ae60;
                color: white;
            }
            
            QPushButton#analyze_btn:hover {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #3ed882,
                    stop: 0.4 #2ecc71,
                    stop: 0.5 #29b765,
                    stop: 1.0 #27ae60
                );
                border: 1px solid #2ecc71;
            }
            
            QPushButton#cancel_button {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #e74c3c,
                    stop: 0.4 #e43725,
                    stop: 0.5 #c0392b,
                    stop: 1.0 #a93323
                );
                border: 1px solid #c0392b;
                color: white;
            }
            
            QPushButton#cancel_button:disabled {
                background: #383838;
                border: 1px solid #404040;
                color: #707070;
            }
            
            QPushButton:disabled {
                background: #383838;
                border: 1px solid #404040;
                color: #707070;
            }
            
            QProgressBar {
                border: none;
                background: #404040;
                border-radius: 4px;
                height: 8px;
                text-align: center;
            }
            
            QProgressBar::chunk {
                border-radius: 4px;
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2196F3,
                    stop:0.4 #42A5F5,
                    stop:0.8 #64B5F6,
                    stop:1 #2196F3
                );
            }
            
            QTableWidget {
                background: #333333;
                border: 1px solid #404040;
                border-radius: 6px;
                gridline-color: #404040;
            }
            
            QTableWidget::item {
                padding: 8px;
                color: #e0e0e0;
            }
            
            QTableWidget::item:selected {
                background: #264f78;
                color: #ffffff;
            }
            
            QHeaderView::section {
                background: #404040;
                color: #e0e0e0;
                padding: 10px;
                border: none;
                border-right: 1px solid #505050;
                border-bottom: 1px solid #505050;
            }
            
            QScrollBar:vertical {
                background: #333333;
                width: 14px;
                border-radius: 7px;
            }
            
            QScrollBar::handle:vertical {
                background: #505050;
                min-height: 30px;
                border-radius: 7px;
            }
            
            QScrollBar::handle:vertical:hover {
                background: #606060;
            }
            
            QTextEdit {
                background: #333333;
                border: 1px solid #404040;
                border-radius: 6px;
                color: #e0e0e0;
                padding: 8px;
                selection-background-color: #264f78;
            }
        """)
        
        # Set window icon
        icon_path = str(Path(__file__).parent.parent / 'assets' / 'logo.png')
        self.setWindowIcon(QIcon(icon_path))
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create tabs with better organization
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Collection tab
        collection_tab = self.create_collection_tab()
        self.tabs.addTab(collection_tab, "Data Collection")
        
        # Results tabs
        self.metrics_tab = self.create_metrics_tab()
        self.tabs.addTab(self.metrics_tab, "Engagement Metrics")
        
        self.sentiment_tab = self.create_sentiment_tab()
        self.tabs.addTab(self.sentiment_tab, "Sentiment Analysis")
        
        self.topics_tab = self.create_topics_tab()
        self.tabs.addTab(self.topics_tab, "Trending Topics")
        
        self.visualizations_tab = self.create_visualizations_tab()
        self.tabs.addTab(self.visualizations_tab, "Visualizations")
        
        self.worker = None
        self._is_analysis_running = False
        self._cancel_requested = False

        self.load_saved_state()

    def create_collection_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)
        
        # Input fields group
        input_group = QWidget()
        input_group.setStyleSheet("""
            QWidget {
                background: #333333;
                border: 1px solid #404040;
                border-radius: 6px;
            }
            QLabel {
                background: transparent;
                border: none;
                color: #e0e0e0;
            }
            QLineEdit, QSpinBox {
                background: #404040;
                color: #e0e0e0;
                border: 2px solid #505050;
            }
        """)
        
        input_layout = QVBoxLayout(input_group)
        input_layout.setContentsMargins(24, 24, 24, 24)
        input_layout.setSpacing(16)
        
        # Subreddit input
        subreddit_layout = QHBoxLayout()
        subreddit_label = QLabel("Subreddit:")
        self.subreddit_input = QLineEdit()
        self.subreddit_input.setPlaceholderText("Enter subreddit names (comma-separated)")
        self.subreddit_input.setToolTip("Enter one or more subreddit names, separated by commas (e.g., 'python, programming, learnpython')")
        subreddit_layout.addWidget(subreddit_label)
        subreddit_layout.addWidget(self.subreddit_input)
        input_layout.addLayout(subreddit_layout)
        
        # Keywords input
        keywords_layout = QHBoxLayout()
        keywords_label = QLabel("Keywords:")
        self.keywords_input = QLineEdit()
        self.keywords_input.setPlaceholderText("Enter search terms (comma-separated)")
        self.keywords_input.setToolTip("Enter search terms to find posts. If subreddits are specified, searches will be limited to those subreddits.")
        keywords_layout.addWidget(keywords_label)
        keywords_layout.addWidget(self.keywords_input)
        input_layout.addLayout(keywords_layout)
        
        # Limit input
        limit_layout = QHBoxLayout()
        limit_label = QLabel("Post limit:")
        self.limit_input = QSpinBox()
        self.limit_input.setRange(1, 10000)
        self.limit_input.setValue(1000)
        limit_layout.addWidget(limit_label)
        limit_layout.addWidget(self.limit_input)
        input_layout.addLayout(limit_layout)
        
        layout.addWidget(input_group)
        
        # Progress bar and status
        self.progress_bar = QProgressBar()
        self.status_label = QLabel("Ready")
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.status_label)
        
        # Button layout for Analyze and Cancel buttons
        button_layout = QHBoxLayout()
        
        # Analyze button
        self.analyze_btn = QPushButton("Start Analysis")
        self.analyze_btn.setObjectName("analyze_btn")  # Important for styling
        self.analyze_btn.clicked.connect(self.start_analysis)
        self.analyze_btn.setCursor(Qt.PointingHandCursor)
        button_layout.addWidget(self.analyze_btn)
        
        # Cancel button
        self.cancel_button = QPushButton("Cancel Analysis")
        self.cancel_button.setEnabled(False)
        self.cancel_button.setObjectName("cancel_button")
        self.cancel_button.clicked.connect(self.cancel_current_operations)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        # Results view
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        layout.addWidget(self.results_text)
        
        # Update layout spacing
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        input_layout.setContentsMargins(15, 15, 15, 15)
        input_layout.setSpacing(10)
        
        return tab

    def create_metrics_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)
        
        # Create table for metrics
        self.metrics_table = QTableWidget()
        self.metrics_table.setColumnCount(2)
        self.metrics_table.setHorizontalHeaderLabels(["Metric", "Value"])
        self.metrics_table.horizontalHeader().setStretchLastSection(True)
        
        # Set table properties for better readability
        self.metrics_table.setAlternatingRowColors(True)
        self.metrics_table.verticalHeader().setVisible(False)
        self.metrics_table.setShowGrid(True)
        self.metrics_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #404040;
                border: none;
            }
            QTableWidget::item {
                padding: 10px;
            }
        """)
        
        layout.addWidget(self.metrics_table)
        return tab

    def create_sentiment_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Create areas for sentiment visualization
        self.sentiment_plot_label = QLabel()
        layout.addWidget(self.sentiment_plot_label)
        
        # Add sentiment metrics table
        self.sentiment_table = QTableWidget()
        self.sentiment_table.setColumnCount(2)
        self.sentiment_table.setHorizontalHeaderLabels(["Metric", "Value"])
        layout.addWidget(self.sentiment_table)
        
        return tab

    def create_visualizations_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Create labels for both plots
        self.sentiment_dist_label = QLabel("Sentiment Distribution")
        self.engagement_plot_label = QLabel("Engagement Over Time")
        
        scroll_layout.addWidget(self.sentiment_dist_label)
        scroll_layout.addSpacing(20)
        scroll_layout.addWidget(self.engagement_plot_label)
        
        # Set up scroll area
        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)
        
        return tab

    def update_metrics_display(self, metrics):
        """Update the metrics table with engagement metrics"""
        self.metrics_table.setRowCount(0)
        if not metrics:
            return
        
        # Format engagement metrics for display
        formatted_metrics = {
            'Average Post Score': f"{metrics.get('avg_post_score', 0):.1f}",
            'Average Comments': f"{metrics.get('avg_comments', 0):.1f}",
            'Total Posts': metrics.get('total_posts', 0),
            'Total Comments': metrics.get('total_comments', 0),
            'Unique Authors': metrics.get('unique_authors', 0),
            'Peak Posting Hour': metrics.get('peak_posting_hours', 0)
        }
        
        # Add top subreddits if available
        if 'top_subreddits' in metrics:
            for subreddit, count in metrics['top_subreddits'].items():
                formatted_metrics[f'Top Subreddit: r/{subreddit}'] = count
        
        # Add to table
        for key, value in formatted_metrics.items():
            row = self.metrics_table.rowCount()
            self.metrics_table.insertRow(row)
            self.metrics_table.setItem(row, 0, QTableWidgetItem(key))
            self.metrics_table.setItem(row, 1, QTableWidgetItem(str(value)))
        
        # Adjust column widths
        self.metrics_table.resizeColumnsToContents()
        self.metrics_table.horizontalHeader().setStretchLastSection(True)

    def update_visualizations(self, output_dir):
        """Update visualization displays with both combined and subreddit-specific data"""
        output_dir = Path(output_dir)
        
        # Create scrollable widget for visualizations
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        content_layout = QVBoxLayout(content)
        
        # Add combined analysis section
        combined_section = self.create_analysis_section(
            output_dir / 'data' / 'reddit_posts.csv',
            output_dir / 'visualizations',
            "Combined Analysis"
        )
        content_layout.addWidget(combined_section)
        
        # Add subreddit-specific sections
        for subreddit in self.worker.subreddits:
            subreddit_path = output_dir / subreddit
            if subreddit_path.exists():
                subreddit_section = self.create_analysis_section(
                    subreddit_path / 'data' / 'reddit_posts.csv',
                    subreddit_path / 'visualizations',
                    f"r/{subreddit}"
                )
                content_layout.addWidget(subreddit_section)
        
        scroll.setWidget(content)
        
        # Replace existing visualization tab content
        for i in range(self.tabs.count()):
            if self.tabs.tabText(i) == "Visualizations":
                vis_tab = QWidget()
                vis_layout = QVBoxLayout(vis_tab)
                vis_layout.addWidget(scroll)
                self.tabs.removeTab(i)
                self.tabs.insertTab(i, vis_tab, "Visualizations")
                break

    def create_analysis_section(self, data_path, vis_path, title):
        """Create a section containing both metrics and visualizations"""
        section = QWidget()
        layout = QVBoxLayout(section)
        
        # Add title
        title_label = QLabel(title)
        title_label.setFont(QFont('Arial', 14, QFont.Bold))
        layout.addWidget(title_label)
        
        # Add metrics if data file exists
        if data_path.exists():
            df = pd.read_csv(data_path)
            metrics_group = QWidget()
            metrics_layout = QGridLayout(metrics_group)
            
            # Add key metrics
            metrics = {
                'Total Posts': len(df),
                'Average Score': f"{df['score'].mean():.1f}",
                'Total Comments': df['num_comments'].sum(),
                'Average Comments': f"{df['num_comments'].mean():.1f}"
            }
            
            for i, (key, value) in enumerate(metrics.items()):
                metrics_layout.addWidget(QLabel(f"{key}:"), i // 2, (i % 2) * 2)
                metrics_layout.addWidget(QLabel(str(value)), i // 2, (i % 2) * 2 + 1)
            
            layout.addWidget(metrics_group)
        
        # Add separator
        layout.addWidget(QLabel(""))
        
        # Add visualizations
        if vis_path.exists():
            for img_file in vis_path.glob('*.png'):
                img_label = QLabel()
                pixmap = QPixmap(str(img_file))
                scaled_pixmap = pixmap.scaled(800, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                img_label.setPixmap(scaled_pixmap)
                img_label.setAlignment(Qt.AlignCenter)
                layout.addWidget(img_label)
        
        return section

    def update_sentiment_display(self, sentiment_data):
        """Update the sentiment table with sentiment analysis results"""
        self.sentiment_table.setRowCount(0)
        if not sentiment_data:
            return
        
        # Format sentiment metrics for display
        formatted_metrics = {
            'Average Post Sentiment': f"{sentiment_data.get('avg_post_sentiment', 0):.3f}",
            'Average Comment Sentiment': f"{sentiment_data.get('avg_comment_sentiment', 0):.3f}",
            'Total Analyzed Posts': sentiment_data.get('total_analyzed_posts', 0),
            'Total Analyzed Comments': sentiment_data.get('total_analyzed_comments', 0)
        }
        
        for key, value in formatted_metrics.items():
            row = self.sentiment_table.rowCount()
            self.sentiment_table.insertRow(row)
            self.sentiment_table.setItem(row, 0, QTableWidgetItem(key))
            self.sentiment_table.setItem(row, 1, QTableWidgetItem(str(value)))
        
        # Adjust column widths
        self.sentiment_table.resizeColumnsToContents()
        self.sentiment_table.horizontalHeader().setStretchLastSection(True)

    def update_topics_display(self, topics_data):
        """Update the topics table with trending topics data"""
        self.topics_table.setRowCount(0)
        if not topics_data or not isinstance(topics_data, list):
            return
        
        # Sort topics by frequency in descending order
        sorted_topics = sorted(topics_data, key=lambda x: x[1], reverse=True)
        
        for topic, frequency in sorted_topics:
            row = self.topics_table.rowCount()
            self.topics_table.insertRow(row)
            self.topics_table.setItem(row, 0, QTableWidgetItem(str(topic)))
            self.topics_table.setItem(row, 1, QTableWidgetItem(str(frequency)))
        
        # Adjust column widths
        self.topics_table.resizeColumnsToContents()
        self.topics_table.horizontalHeader().setStretchLastSection(True)

    def start_analysis(self):
        """Start the Reddit analysis process"""
        if self._is_analysis_running:
            return
            
        # Get input values and handle multiple subreddits
        subreddits = [s.strip() for s in self.subreddit_input.text().split(',') if s.strip()]
        keywords = [k.strip() for k in self.keywords_input.text().split(',') if k.strip()]
        limit = self.limit_input.value()
        
        # Validate inputs
        if not subreddits and not keywords:
            QMessageBox.warning(
                self,
                "Input Error",
                "Please enter either a subreddit or at least one keyword."
            )
            return
            
        # Update UI state
        self._is_analysis_running = True
        self._cancel_requested = False
        self.analyze_btn.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self.progress_bar.setRange(0, 100)  # Changed from 0 to have determinate progress
        self.progress_bar.setValue(0)
        self.status_label.setText("Starting analysis...")
        self.results_text.clear()
        
        # Create and start worker thread
        self.worker = RedditAnalyzerWorker(subreddits, keywords, limit)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.analysis_complete)
        self.worker.error.connect(self.handle_error)
        self.worker.start()

    def cancel_current_operations(self):
        """Cancel any running analysis operations."""
        if self.worker and self._is_analysis_running:
            self._cancel_requested = True
            self.worker.cancel()
            self.status_label.setText("Cancelling...")
            self.cancel_button.setEnabled(False)
            
            # Immediately reset UI state
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(0)
            self.analyze_btn.setEnabled(True)
            self._is_analysis_running = False
            
            # Force worker to quit if it's not responding
            if self.worker.isRunning():
                self.worker.quit()
                self.worker.wait()
            self.worker = None
        
    @Slot(str)
    def update_progress(self, message):
        """Update the progress display with the given message"""
        self.status_label.setText(message)
        
        # Format subreddit names in the message for better readability
        if "Collecting posts from" in message:
            subreddit = message.split("r/")[1].strip("...")
            message = f"Collecting posts from r/{subreddit}"
        
        self.results_text.append(message)
        
        # Update progress bar to show activity
        current_value = self.progress_bar.value()
        new_value = (current_value + 1) % 100
        self.progress_bar.setValue(new_value)
        
    @Slot(dict)
    def analysis_complete(self, results):
        """Handle completion of the analysis"""
        self._is_analysis_running = False
        self.analyze_btn.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.progress_bar.setValue(100)
        
        if not self._cancel_requested:
            self.status_label.setText("Analysis complete!")
            
            # Update results display
            summary = (f"Analysis completed successfully!\n"
                      f"Processed {results['posts']} posts\n"
                      f"Results saved to: {results['output_dir']}")
            self.results_text.append(summary)
            
            # Update all tabs with results
            if 'analysis' in results:
                analysis = results['analysis']
                
                # Update engagement metrics
                if 'engagement' in analysis:
                    self.update_metrics_display(analysis['engagement'])
                
                # Update sentiment analysis
                if 'sentiment' in analysis:
                    self.update_sentiment_display(analysis['sentiment'])
                
                # Update trending topics
                # Extract topics from recommendations if available
                if 'recommendations' in analysis and 'successful_topics' in analysis['recommendations']:
                    self.update_topics_display(analysis['recommendations']['successful_topics'])
                
                # Update visualizations
                if 'output_dir' in results:
                    self.update_visualizations(results['output_dir'])
        
        self._cancel_requested = False
        self.worker = None
        
    @Slot(str)
    def handle_error(self, error_message):
        """Handle errors during analysis"""
        self._is_analysis_running = False
        self.analyze_btn.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.status_label.setText("Error occurred!")
        
        QMessageBox.critical(
            self,
            "Analysis Error",
            f"An error occurred during analysis:\n{error_message}"
        )
        
        self.worker = None

    def save_current_state(self):
        """Save the current state of inputs when application closes"""
        try:
            state = {
                'subreddits': self.subreddit_input.text(),
                'keywords': self.keywords_input.text(),
                'limit': self.limit_input.value()
            }
            
            # Create config directory if it doesn't exist
            config_dir = Path.home() / '.reddit_analyzer'
            config_dir.mkdir(exist_ok=True)
            
            # Save state to JSON file
            with open(config_dir / 'last_session.json', 'w') as f:
                json.dump(state, f)
                
        except Exception as e:
            logger.error(f"Failed to save application state: {e}")

    def load_saved_state(self):
        """Load the previously saved state"""
        try:
            config_file = Path.home() / '.reddit_analyzer' / 'last_session.json'
            if config_file.exists():
                with open(config_file) as f:
                    state = json.load(f)
                    
                self.subreddit_input.setText(state.get('subreddits', ''))
                self.keywords_input.setText(state.get('keywords', ''))
                self.limit_input.setValue(state.get('limit', 1000))
        except Exception as e:
            logger.error(f"Failed to load saved state: {e}")