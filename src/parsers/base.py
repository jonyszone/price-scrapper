"""Base parser class"""

from abc import ABC, abstractmethod
from typing import List
import requests
from bs4 import BeautifulSoup
from src.models import Product, SiteConfig


class BaseParser(ABC):
    """Base parser class for all site-specific parsers"""
    
    def __init__(self, timeout: int = 30):
        """
        Initialize parser
        
        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def fetch_page(self, url: str) -> BeautifulSoup:
        """
        Fetch and parse a web page
        
        Args:
            url: URL to fetch
            
        Returns:
            BeautifulSoup object
        """
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()
        return BeautifulSoup(response.content, 'html.parser')
    
    @abstractmethod
    def parse(self, site_config: SiteConfig) -> List[Product]:
        """
        Parse products from a site
        
        Args:
            url: URL to scrape
            site_name: Name of the site
            
        Returns:
            List of Product objects
        """
        pass
    
    @abstractmethod
    def extract_product_data(self, element, site_config: SiteConfig) -> Product:
        """
        Extract product data from a page element
        
        Args:
            element: BeautifulSoup element containing product data
            
        Returns:
            Product object
        """
        pass
