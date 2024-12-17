"""
Combined analysis module - redirects to content_analyzer
"""
from .content_analyzer import ContentAnalyzer

# Re-export ContentAnalyzer
__all__ = ['ContentAnalyzer']
