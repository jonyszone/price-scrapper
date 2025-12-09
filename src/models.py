"""Data models for the price scraper"""

from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Product:
    """Product data model"""
    name: str
    price: float
    url: str
    site: str
    product_id: int
    location_id: int
    original_price: float = 0.0
    currency: str = "USD"
    timestamp: datetime = None
    image_url: Optional[str] = None
    availability: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class SiteConfig:
    """Site configuration model"""
    name: str
    url: str
    enabled: bool
    parser: str
    product_id: int = 0
    location_id: int = 0
    selectors: Dict[str, str] = field(default_factory=dict)
