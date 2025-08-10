"""
Treblle SDK for Django - API Intelligence Platform

A production-ready middleware for comprehensive API monitoring and observability.
"""

__version__ = "2.0.3"
__author__ = "Treblle"
__email__ = "support@treblle.com"
__url__ = "https://treblle.com"

# Import middleware for easy access
from .middleware import TreblleMiddleware

__all__ = ['TreblleMiddleware', '__version__']