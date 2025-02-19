"""Configuration settings for the news scraper module."""

from dataclasses import dataclass
from typing import List, Optional

@dataclass
class ScraperConfig:
    """Configuration for news scraping settings."""
    base_url: str
    api_key: Optional[str] = None
    max_articles_per_request: int = 100
    default_keywords: List[str] = None
    cache_duration_minutes: int = 60
    request_timeout_seconds: int = 30
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        if not self.base_url:
            raise ValueError("base_url must be provided")
        
        if self.default_keywords is None:
            self.default_keywords = []
            
        if self.max_articles_per_request < 1:
            raise ValueError("max_articles_per_request must be positive")
            
        if self.cache_duration_minutes < 0:
            raise ValueError("cache_duration_minutes cannot be negative")
            
        if self.request_timeout_seconds < 1:
            raise ValueError("request_timeout_seconds must be positive")