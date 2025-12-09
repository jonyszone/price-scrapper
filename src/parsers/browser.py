"""Browser-based parser using Selenium for JavaScript-heavy websites"""

import logging
import time
from typing import List, Optional
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src.parsers.base import BaseParser
from src.models import Product, SiteConfig

logger = logging.getLogger(__name__)


class BrowserParser(BaseParser):
    """Browser-based parser using Selenium for sites that require JavaScript"""

    def __init__(self, timeout: int = 30, headless: bool = True):
        """
        Initialize browser parser
        
        Args:
            timeout: Request timeout in seconds
            headless: Run browser in headless mode
        """
        super().__init__(timeout)
        self.headless = headless
        self.driver = None

    def _init_driver(self):
        """Initialize Selenium WebDriver with undetected-chromedriver"""
        if self.driver is not None:
            return

        try:
            import os
            
            options = uc.ChromeOptions()
            
            if self.headless:
                options.add_argument('--headless=new')
            
            # Additional options
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--window-size=1920,1080')
            
            # Add proxy if enabled
            proxy_enabled = os.getenv('PROXY_ENABLED', 'false').lower() == 'true'
            if proxy_enabled:
                proxy_host = os.getenv('PROXY_HOST')
                proxy_port = os.getenv('PROXY_PORT')
                proxy_user = os.getenv('PROXY_USERNAME')
                proxy_pass = os.getenv('PROXY_PASSWORD')
                
                if proxy_host and proxy_port:
                    # Format: username:password@host:port
                    if proxy_user and proxy_pass:
                        proxy_string = f'{proxy_user}:{proxy_pass}@{proxy_host}:{proxy_port}'
                    else:
                        proxy_string = f'{proxy_host}:{proxy_port}'
                    
                    options.add_argument(f'--proxy-server=http://{proxy_string}')
                    logger.info(f"Using proxy: {proxy_host}:{proxy_port}")
            
            # Initialize undetected chromedriver
            # version_main=None will auto-detect, or specify like version_main=142
            self.driver = uc.Chrome(options=options, version_main=142)
            self.driver.set_page_load_timeout(self.timeout)
            
            logger.info("Undetected browser initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize browser: {e}")
            raise

    def fetch_page(self, url: str) -> BeautifulSoup:
        """
        Fetch and parse a web page using browser
        
        Args:
            url: URL to fetch
            
        Returns:
            BeautifulSoup object
        """
        self._init_driver()
        
        try:
            logger.info(f"Loading page with browser: {url}")
            self.driver.get(url)
            
            # Wait for page to load (wait for body element)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Additional wait for dynamic content
            time.sleep(2)
            
            # Save screenshot for debugging
            try:
                screenshot_path = f"debug_screenshot_{int(time.time())}.png"
                self.driver.save_screenshot(screenshot_path)
                logger.info(f"Screenshot saved to {screenshot_path}")
            except Exception as e:
                logger.warning(f"Could not save screenshot: {e}")
            
            # Get page source and parse with BeautifulSoup
            page_source = self.driver.page_source
            return BeautifulSoup(page_source, 'html.parser')
            
        except Exception as e:
            logger.error(f"Error fetching page with browser: {e}")
            raise

    def parse(self, site_config: SiteConfig) -> List[Product]:
        """
        Parse products from a site using browser
        
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
        finally:
            # Clean up browser
            self.cleanup()

    def extract_product_data(self, element: BeautifulSoup, site_config: SiteConfig) -> Optional[Product]:
        """
        Extract product data using selectors
        
        Args:
            element: BeautifulSoup element (page)
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

        # Extract title
        name = get_text(selectors.get('title')) or get_text(selectors.get('name')) or site_config.name
        
        # Extract price
        price_text = get_text(selectors.get('price'))
        if not price_text:
            logger.warning(f"Could not find price for {site_config.name}")
            return None

        price_val = self._clean_price(price_text)
        
        # Extract original price
        original_price_val = 0.0
        original_price_text = get_text(selectors.get('original_price'))
        if original_price_text:
            original_price_val = self._clean_price(original_price_text)
        
        # Extract availability
        availability = get_text(selectors.get('availability'))
        if availability:
            availability = availability.lower().strip().replace(' ', '_')
        else:
            # Check if availability selector is for a button
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
            url=site_config.url,
            site=site_config.name,
            product_id=site_config.product_id,
            location_id=site_config.location_id,
            original_price=original_price_val,
            availability=availability,
            image_url=image_url
        )

    def _clean_price(self, price_str: str) -> float:
        """Clean price string and convert to float"""
        import re
        clean_str = re.sub(r'[^\d.]', '', price_str)
        try:
            return float(clean_str)
        except ValueError:
            logger.warning(f"Failed to parse price: {price_str}")
            return 0.0

    def cleanup(self):
        """Clean up browser resources"""
        if self.driver:
            try:
                self.driver.quit()
                self.driver = None
                logger.info("Browser closed successfully")
            except Exception as e:
                logger.error(f"Error closing browser: {e}")

    def __del__(self):
        """Destructor to ensure browser is closed"""
        self.cleanup()
