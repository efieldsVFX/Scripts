"""
EDGLRD Social Media Analyzer API
FastAPI application for social media analytics with integrated dashboard
"""

import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime
import pandas as pd

from .analytics_manager import AnalyticsManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="EDGLRD Social Media Analyzer",
    description="Enterprise-grade social media analytics platform",
    version="1.0.0"
)

# Initialize Analytics Manager
analytics_manager = AnalyticsManager()

# FastAPI routes
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "EDGLRD Social Media Analyzer API",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/platforms")
async def get_platforms():
    """Get list of configured social media platforms"""
    return {
        "platforms": list(analytics_manager.collectors.keys())
    }

@app.get("/analytics/{platform}")
async def get_platform_analytics(
    platform: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Get analytics for a specific platform"""
    try:
        if platform not in analytics_manager.collectors:
            raise HTTPException(status_code=404, detail=f"Platform {platform} not found")
        
        # Convert dates if provided
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None
        
        # Collect data
        collector = analytics_manager.collectors[platform]
        data = collector.collect_data(start_date=start, end_date=end)
        
        # Analyze data
        analysis = {
            "audience": analytics_manager.audience_analyzer.analyze(data),
            "engagement": analytics_manager.engagement_analyzer.analyze(data),
            "content": analytics_manager.content_analyzer.analyze(data),
            "predictions": analytics_manager.predictive_analyzer.analyze(data)
        }
        
        return {
            "platform": platform,
            "timeframe": {
                "start": start_date,
                "end": end_date
            },
            "analysis": analysis
        }
    
    except Exception as e:
        logger.error(f"Error processing analytics for {platform}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    import socket
    import netifaces

    # Get local IP addresses
    def get_local_ips():
        ips = []
        interfaces = netifaces.interfaces()
        for interface in interfaces:
            addrs = netifaces.ifaddresses(interface)
            if netifaces.AF_INET in addrs:
                for addr in addrs[netifaces.AF_INET]:
                    ip = addr['addr']
                    if not ip.startswith('127.'):
                        ips.append(ip)
        return ips

    # Display access information
    local_ips = get_local_ips()
    logger.info("Starting SM Analyzer Server")
    logger.info("Server can be accessed at:")
    for ip in local_ips:
        logger.info(f"  http://{ip}:8000")
    
    # Configure CORS to allow access from any origin
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Run the server
    uvicorn.run(app, host="0.0.0.0", port=8000)
