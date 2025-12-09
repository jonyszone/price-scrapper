"""Generic parser implementation"""

import logging
import re
from typing import List, Optional
from bs4 import BeautifulSoup
from src.parsers.base import BaseParser
from src.models import Product, SiteConfig

logger = logging.getLogger(__name__)


class GenericParser(BaseParser):
    """Generic parser that uses CSS selectors from configuration"""

    def parse(self, site_config: SiteConfig) -> List[Product]:
        """
        Parse products from a site using configured selectors
        
        Args:
            site_config: Site configuration
            
        Returns:
            List of Product objects
        """
        try:
            soup = self.fetch_page(site_config.url)
            product = self.extract_product_data(soup, site_config)
            return [product] if product else []
        except Exception as e:
            logger.error(f"Error parsing {site_config.name}: {e}")
            return []

    def extract_product_data(self, element: BeautifulSoup, site_config: SiteConfig) -> Optional[Product]:
        """
        Extract product data using selectors
        
        Args:
            element: BeautifulSoup element (page or product card)
            site_config: Site configuration with selectors
            
        Returns:
            Product object or None if extraction fails
        """
        selectors = site_config.selectors
        
        if not selectors:
            logger.error(f"No selectors configured for {site_config.name}")
            return None

        # Helper to get text from selector
        def get_text(selector: str) -> Optional[str]:
            if not selector:
                return None
            el = element.select_one(selector)
            return el.get_text(strip=True) if el else None

        # Extract basic data
        # Note: Name/Title selector isn't in the example yaml, assuming 'title' or 'name' might be added
        # For now, using site name if title selector missing, or failing gracefully
        name = get_text(selectors.get('title')) or get_text(selectors.get('name')) or site_config.name
        
        # Extract price
        price_text = get_text(selectors.get('price'))
        if not price_text:
            logger.warning(f"Could not find price for {site_config.name}")
            return None

        # Clean price string
        price_val = self._clean_price(price_text)
        
        # Extract original price
        original_price_val = 0.0
        original_price_text = get_text(selectors.get('original_price'))
        if original_price_text:
            original_price_val = self._clean_price(original_price_text)
        
        # Extract availability
        availability = get_text(selectors.get('availability'))
        if availability:
            # Normalize to snake_case format expected by API (in_stock, out_of_stock, limited)
            availability = availability.lower().strip().replace(' ', '_')
        else:
            # Check if availability selector is for a button (e.g., "Add to cart" button)
            # If button exists, assume in_stock
            avail_selector = selectors.get('availability')
            if avail_selector and 'button' in avail_selector.lower():
                button_el = element.select_one(avail_selector)
                if button_el:
                    availability = 'in_stock'
        
        # Extract image
        image_url = None
        if selectors.get('image'):
            img_el = element.select_one(selectors['image'])
            if img_el:
                image_url = img_el.get('src')

        return Product(
            name=name,
            price=price_val,
            original_price=original_price_val,
            url=site_config.url,
            site=site_config.name,
            product_id=site_config.product_id,
            location_id=site_config.location_id,
            availability=availability,
            image_url=image_url
        )

    def _clean_price(self, price_str: str) -> float:
        """Clean price string and convert to float"""
        # Remove currency symbols and non-numeric chars except decimal point
        # This is a simple regex, might need adjustment for specific currencies
        clean_str = re.sub(r'[^\d.]', '', price_str)
        try:
            return float(clean_str)
        except ValueError:
            logger.warning(f"Failed to parse price: {price_str}")
            return 0.0
