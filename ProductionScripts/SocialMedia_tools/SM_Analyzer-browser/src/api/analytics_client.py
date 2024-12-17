"""
Analytics Client
Handles competitive analysis and revenue tracking across platforms
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import requests
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    RunReportRequest,
    DateRange,
    Metric,
    Dimension
)
from ..config.api_config import APIConfig

class AnalyticsClient:
    def __init__(self):
        """Initialize analytics clients"""
        config = APIConfig.get_analytics_config()
        if not APIConfig.validate_credentials(config):
            raise ValueError("Invalid Analytics API credentials")
            
        self.ga_property_id = config['ga_property_id']
        self.ga_client = BetaAnalyticsDataClient()
        self.brandwatch_token = config.get('brandwatch_token')
        self.brandwatch_url = "https://api.brandwatch.com/v3"
        
    def get_share_of_voice(self, keywords: List[str], start_date: str, end_date: str) -> Dict:
        """Get share of voice metrics using social listening APIs"""
        try:
            headers = {
                'Authorization': f'Bearer {self.brandwatch_token}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'query': ' OR '.join(keywords),
                'startDate': start_date,
                'endDate': end_date,
                'metrics': ['mentions', 'reach', 'sentiment']
            }
            
            response = requests.post(
                f"{self.brandwatch_url}/analytics/mentions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            print(f"Error fetching share of voice: {str(e)}")
            return {}
            
    def get_industry_benchmarks(self, industry: str, metrics: List[str]) -> Dict:
        """Get industry benchmarking data"""
        try:
            headers = {
                'Authorization': f'Bearer {self.brandwatch_token}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'industry': industry,
                'metrics': metrics
            }
            
            response = requests.post(
                f"{self.brandwatch_url}/benchmarks",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            print(f"Error fetching industry benchmarks: {str(e)}")
            return {}
            
    def get_url_performance(self, start_date: str, end_date: str) -> Dict:
        """Get URL click-through rates from Google Analytics"""
        try:
            request = RunReportRequest(
                property=f"properties/{self.ga_property_id}",
                date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
                metrics=[
                    Metric(name="clicks"),
                    Metric(name="impressions"),
                    Metric(name="CTR")
                ],
                dimensions=[Dimension(name="pageTitle"), Dimension(name="fullPageUrl")]
            )
            
            response = self.ga_client.run_report(request)
            
            results = []
            for row in response.rows:
                results.append({
                    'title': row.dimension_values[0].value,
                    'url': row.dimension_values[1].value,
                    'clicks': row.metric_values[0].value,
                    'impressions': row.metric_values[1].value,
                    'ctr': row.metric_values[2].value
                })
                
            return {'urls': results}
        except Exception as e:
            print(f"Error fetching URL performance: {str(e)}")
            return {}
