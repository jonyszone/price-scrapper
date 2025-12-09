"""Main entry point for the price scraper"""

import os
from pathlib import Path
from dotenv import load_dotenv

from src.utils import setup_logging, load_yaml_config, get_env_variable
from src.models import SiteConfig
from src.scraper import Scraper
from src.api_client import APIClient
from src.parsers.base import BaseParser
from src.parsers.generic import GenericParser
from src.parsers.browser import BrowserParser


# Load environment variables
load_dotenv()


def main():
    """Main function"""
    # Setup logging
    logger = setup_logging(log_level=os.getenv('LOG_LEVEL', 'INFO'))
    logger.info("Starting price scraper")
    
    # Load site configurations
    config_path = Path(__file__).parent / 'config' / 'sites.yaml'
    config_data = load_yaml_config(str(config_path))
    
    # Parse site configurations
    site_configs = [
        SiteConfig(
            name=site['name'],
            url=site['url'],
            enabled=site.get('enabled', True),
            parser=site.get('parser', 'base'),
            product_id=site.get('product_id', 0),
            location_id=site.get('location_id', 0),
            selectors=site.get('selectors', {})
        )
        for site in config_data.get('sites', [])
    ]
    
    logger.info(f"Loaded {len(site_configs)} site configurations")
    
    # Initialize scraper
    scraper = Scraper()
    
    # Register parsers here
    scraper.register_parser('base', GenericParser())
    scraper.register_parser('generic', GenericParser())
    scraper.register_parser('browser', BrowserParser())
    # Example: scraper.register_parser('custom', YourCustomParser())
    if not scraper.parsers:
         logger.warning("No parsers registered. Defaulting 'base' to GenericParser.")
    
    # Initialize API client
    api_base_url = get_env_variable('API_BASE_URL')
    api_key = get_env_variable('API_KEY')
    api_client = APIClient(api_base_url, api_key)
    
    # Check API health
    if not api_client.health_check():
        logger.warning("API health check failed. Continuing anyway...")
    
    # Scrape all sites
    products = scraper.scrape_all(site_configs)
    
    # Send products to API
    if products:
        try:
            response = api_client.send_products(products)
            logger.info(f"API Response: {response}")
        except Exception as e:
            logger.error(f"Failed to send products to API: {e}")
    else:
        logger.info("No products scraped")
    
    logger.info("Price scraper finished")


if __name__ == '__main__':
    main()
