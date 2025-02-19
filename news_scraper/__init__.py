"""News scraper module for fetching and processing financial news."""

from .scraper import NewsScraperClient
from .config import ScraperConfig

__all__ = ['NewsScraperClient', 'ScraperConfig']