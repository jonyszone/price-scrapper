"""Main scraper module"""

import logging
from typing import List
from src.models import Product, SiteConfig
from src.parsers.base import BaseParser


logger = logging.getLogger(__name__)


class Scraper:
    """Main scraper class"""
    
    def __init__(self):
        """Initialize scraper"""
        self.parsers = {}
    
    def register_parser(self, name: str, parser: BaseParser):
        """
        Register a parser for a specific site
        
        Args:
            name: Parser name
            parser: Parser instance
        """
        self.parsers[name] = parser
        logger.info(f"Registered parser: {name}")
    
    def scrape_site(self, site_config: SiteConfig) -> List[Product]:
        """
        Scrape a single site
        
        Args:
            site_config: Site configuration
            
        Returns:
            List of scraped products
        """
        if not site_config.enabled:
            logger.info(f"Site {site_config.name} is disabled, skipping")
            return []
        
        parser_name = site_config.parser
        if parser_name not in self.parsers:
            logger.error(f"Parser {parser_name} not found for site {site_config.name}")
            return []
        
        parser = self.parsers[parser_name]
        
        try:
            logger.info(f"Scraping site: {site_config.name}")
            products = parser.parse(site_config)
            logger.info(f"Scraped {len(products)} products from {site_config.name}")
            return products
        except Exception as e:
            logger.error(f"Error scraping {site_config.name}: {e}")
            return []
    
    def scrape_all(self, site_configs: List[SiteConfig]) -> List[Product]:
        """
        Scrape all configured sites
        
        Args:
            site_configs: List of site configurations
            
        Returns:
            List of all scraped products
        """
        all_products = []
        
        for config in site_configs:
            products = self.scrape_site(config)
            all_products.extend(products)
        
        logger.info(f"Total products scraped: {len(all_products)}")
        return all_products
