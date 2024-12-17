# SM_Analyzer: Social Media Analytics for VFX Pipeline

A powerful social media analytics tool designed for VFX pipeline integration, enabling studios to analyze and optimize their social media presence through data-driven insights.

**Author**: Eric Fields (efieldsvfx@gmail.com)

![SM_Analyzer Dashboard](docs/images/dashboard.png)

## 🚀 Key Features

- **Multi-Platform Analysis**: Seamlessly collect and analyze data from multiple social media platforms:
  - Twitter
  - Instagram
  - Reddit
  - TikTok

- **Advanced Analytics Engine**:
  - Sentiment Analysis using VADER, Transformers, or TextBlob
  - Topic Modeling with LDA, NMF, or BERTopic
  - Engagement Metrics Tracking
  - Content Performance Analytics

- **Pipeline Integration**:
  - Easy integration with existing VFX pipelines
  - Automated data collection and analysis
  - Real-time monitoring capabilities
  - Export data in pipeline-friendly formats

- **Visualization Suite**:
  - Interactive sentiment distribution plots
  - Engagement timeline analysis
  - Topic visualization
  - Custom report generation

## 🛠 Technical Stack

- **Backend**: Python 3.8+
- **UI Framework**: PySide6
- **Data Processing**: pandas, numpy
- **ML/AI**: 
  - NLTK
  - Transformers (Hugging Face)
  - BERTopic
- **Visualization**: 
  - matplotlib
  - seaborn
  - pyLDAvis

## 🔧 Installation

```bash
# Clone the repository
git clone https://github.com/yourstudio/sm-analyzer.git

# Install dependencies
pip install -r requirements.txt

# Run the application
python src/reddit_analyzer_app.py
```

## 🎮 Usage Example

```python
from src.collectors import RedditCollector
from src.analysis import ContentAnalyzer

# Initialize collectors
collector = RedditCollector()

# Collect data
posts_data = collector.collect_posts("unreal_engine", max_results=1000)

# Initialize analyzer
analyzer = ContentAnalyzer(posts_data, comments_data)

# Run analysis
results = analyzer.perform_analysis()

# Generate visualizations
analyzer.plot_insights("output/visualizations")
```

## 🔄 Pipeline Integration

The SM_Analyzer is designed to seamlessly integrate with your VFX pipeline:

1. **Data Collection**:
   ```python
   # Automated data collection job
   collector.collect_user_posts(limit=100)
   ```

2. **Analysis**:
   ```python
   # Run sentiment analysis
   analyzer.analyze_sentiment()
   
   # Generate content recommendations
   recommendations = analyzer._generate_recommendations()
   ```

3. **Visualization**:
   ```python
   # Generate pipeline-ready visualizations
   analyzer._generate_visualizations()
   ```

## 📊 Features for VFX Studios

- **Content Performance Tracking**: Monitor how your VFX breakdowns and showreels perform across platforms
- **Audience Engagement Analysis**: Understand what content resonates with your target audience
- **Optimal Posting Times**: AI-driven recommendations for best posting times
- **Trending Topics**: Stay updated with industry trends and discussions
- **Sentiment Analysis**: Gauge audience reception to your VFX work
- **Automated Reporting**: Generate comprehensive reports for stakeholders

## 🔐 Security

- Environment-based configuration
- Secure API key management
- Rate limiting protection
- Data encryption support

## 📞 Support

For support, please contact:
- Author: Eric Fields
- Email: efieldsvfx@gmail.com
- Portfolio: [efields.vfx](https://efields.vfx)

## 📝 License

Copyright (c) 2024 Eric Fields. All rights reserved.

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.
