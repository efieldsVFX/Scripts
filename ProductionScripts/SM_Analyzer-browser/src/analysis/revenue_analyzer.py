"""
Revenue metrics analyzer for social media analytics
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from .base_analyzer import BaseAnalyzer

class RevenueAnalyzer(BaseAnalyzer):
    """Analyzer for revenue and monetization metrics"""

    def __init__(self):
        """Initialize revenue analyzer"""
        super().__init__()
        self.logger = logging.getLogger(__name__)

    def analyze_shopping_revenue(self, shopping_data: Dict) -> Dict:
        """
        Analyze revenue from shoppable posts
        
        Args:
            shopping_data: Dict containing shopping metrics
            
        Returns:
            Dict containing shopping revenue analysis
        """
        try:
            shopping_metrics = {
                'sales_metrics': self._analyze_sales_performance(shopping_data),
                'product_metrics': self._analyze_product_performance(shopping_data),
                'conversion_metrics': self._analyze_conversion_funnel(shopping_data),
                'customer_metrics': self._analyze_customer_behavior(shopping_data),
                'trend_analysis': self._analyze_sales_trends(shopping_data)
            }
            return shopping_metrics
        except Exception as e:
            self.logger.error(f"Error analyzing shopping revenue: {str(e)}")
            return {}

    def analyze_ad_revenue(self, ad_data: Dict) -> Dict:
        """
        Analyze revenue from advertising
        
        Args:
            ad_data: Dict containing advertising metrics
            
        Returns:
            Dict containing ad revenue analysis
        """
        try:
            ad_metrics = {
                'revenue_metrics': self._analyze_revenue_performance(ad_data),
                'platform_breakdown': self._analyze_platform_revenue(ad_data),
                'format_performance': self._analyze_ad_formats(ad_data),
                'optimization_metrics': self._analyze_optimization_metrics(ad_data),
                'roi_analysis': self._calculate_advertising_roi(ad_data)
            }
            return ad_metrics
        except Exception as e:
            self.logger.error(f"Error analyzing ad revenue: {str(e)}")
            return {}

    def analyze_link_performance(self, link_data: Dict) -> Dict:
        """
        Analyze link click-through performance and revenue impact
        
        Args:
            link_data: Dict containing link metrics
            
        Returns:
            Dict containing link performance analysis
        """
        try:
            link_metrics = {
                'ctr_metrics': self._analyze_click_through_rates(link_data),
                'conversion_impact': self._analyze_link_conversions(link_data),
                'revenue_attribution': self._analyze_revenue_attribution(link_data),
                'channel_performance': self._analyze_channel_effectiveness(link_data),
                'optimization_insights': self._generate_link_insights(link_data)
            }
            return link_metrics
        except Exception as e:
            self.logger.error(f"Error analyzing link performance: {str(e)}")
            return {}

    def _analyze_sales_performance(self, shopping_data: Dict) -> Dict:
        """Analyze sales performance metrics"""
        try:
            sales = shopping_data.get('sales', [])
            if not sales:
                return {}
            
            # Convert to DataFrame for analysis
            df = pd.DataFrame(sales)
            
            # Calculate key metrics
            total_revenue = df['revenue'].sum()
            average_order_value = df['revenue'].mean()
            
            return {
                'total_revenue': float(total_revenue),
                'average_order_value': float(average_order_value),
                'revenue_by_platform': self._calculate_platform_revenue(df),
                'sales_growth': self._calculate_sales_growth(df),
                'top_performing_products': self._identify_top_products(df)
            }
        except Exception as e:
            self.logger.error(f"Error analyzing sales performance: {str(e)}")
            return {}

    def _analyze_revenue_performance(self, ad_data: Dict) -> Dict:
        """Analyze advertising revenue performance"""
        try:
            campaigns = ad_data.get('campaigns', [])
            if not campaigns:
                return {}
            
            # Calculate revenue metrics
            total_spend = sum(camp.get('spend', 0) for camp in campaigns)
            total_revenue = sum(camp.get('revenue', 0) for camp in campaigns)
            
            campaign_metrics = []
            for campaign in campaigns:
                metrics = {
                    'campaign_id': campaign.get('id'),
                    'spend': campaign.get('spend', 0),
                    'revenue': campaign.get('revenue', 0),
                    'roas': campaign.get('revenue', 0) / campaign.get('spend', 1) if campaign.get('spend', 0) > 0 else 0,
                    'conversion_rate': self._calculate_conversion_rate(campaign)
                }
                campaign_metrics.append(metrics)
            
            return {
                'total_metrics': {
                    'spend': total_spend,
                    'revenue': total_revenue,
                    'roas': total_revenue / total_spend if total_spend > 0 else 0
                },
                'campaign_performance': campaign_metrics,
                'platform_breakdown': self._analyze_platform_breakdown(campaigns),
                'trend_analysis': self._analyze_revenue_trends(campaigns)
            }
        except Exception as e:
            self.logger.error(f"Error analyzing revenue performance: {str(e)}")
            return {}

    def _analyze_click_through_rates(self, link_data: Dict) -> Dict:
        """Analyze click-through rates and patterns"""
        try:
            links = link_data.get('links', [])
            if not links:
                return {}
            
            link_metrics = []
            for link in links:
                impressions = link.get('impressions', 0)
                clicks = link.get('clicks', 0)
                
                metrics = {
                    'link_id': link.get('id'),
                    'ctr': clicks / impressions if impressions > 0 else 0,
                    'bounce_rate': self._calculate_bounce_rate(link),
                    'conversion_rate': self._calculate_link_conversion_rate(link),
                    'revenue_per_click': self._calculate_revenue_per_click(link)
                }
                link_metrics.append(metrics)
            
            return {
                'overall_ctr': self._calculate_overall_ctr(links),
                'link_performance': link_metrics,
                'platform_comparison': self._compare_platform_performance(links),
                'content_type_analysis': self._analyze_content_type_performance(links),
                'temporal_patterns': self._analyze_temporal_patterns(links)
            }
        except Exception as e:
            self.logger.error(f"Error analyzing click-through rates: {str(e)}")
            return {}

    def _analyze_revenue_attribution(self, link_data: Dict) -> Dict:
        """Analyze revenue attribution across channels"""
        try:
            attributions = link_data.get('attributions', [])
            if not attributions:
                return {}
            
            # Create DataFrame for attribution analysis
            df = pd.DataFrame(attributions)
            
            # Calculate attribution metrics
            channel_attribution = df.groupby('channel').agg({
                'revenue': 'sum',
                'conversions': 'sum',
                'assists': 'sum'
            }).reset_index()
            
            # Calculate contribution metrics
            total_revenue = df['revenue'].sum()
            channel_attribution['revenue_share'] = channel_attribution['revenue'] / total_revenue
            
            return {
                'channel_attribution': channel_attribution.to_dict('records'),
                'attribution_model_comparison': self._compare_attribution_models(df),
                'customer_journey_analysis': self._analyze_customer_journeys(df),
                'touchpoint_value': self._calculate_touchpoint_value(df),
                'cross_channel_impact': self._analyze_cross_channel_effects(df)
            }
        except Exception as e:
            self.logger.error(f"Error analyzing revenue attribution: {str(e)}")
            return {}
