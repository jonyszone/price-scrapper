"""Intelligent scraper that chooses best method based on site"""

import requests
from src.anti_blocking import IPRotationStrategy
from src.browser_scraper import BrowserScraper
import logging

logger = logging.getLogger(__name__)


class IntelligentScraper:
    """Smart scraper that detects blocking and switches methods"""
    
    # Sites that require browser
    BROWSER_REQUIRED_SITES = [
        'amazon.com',
        'ebay.com',
        'alibaba.com',
        'etsy.com',
        'shopify',
        'javascript-heavy-sites'
    ]
    
    # Sites that block easily
    BLOCKING_PRONE_SITES = [
        'amazon.com',
        'ebay.com',
        'linkedin.com',
        'instagram.com',
        'facebook.com'
    ]
    
    def __init__(self, use_proxies=False, proxy_list=None):
        self.ip_strategy = IPRotationStrategy()
        if proxy_list:
            self.ip_strategy.add_proxies(proxy_list)
        self.use_proxies = use_proxies
        self.browser = None
    
    def _should_use_browser(self, url):
        """Determine if browser is needed"""
        for site in self.BROWSER_REQUIRED_SITES:
            if site in url:
                logger.info(f"Browser required for {site}")
                return True
        return False
    
    def _should_rotate_ip(self, url):
        """Determine if IP rotation is needed"""
        for site in self.BLOCKING_PRONE_SITES:
            if site in url:
                logger.info(f"IP rotation recommended for {site}")
                return True
        return False
    
    def scrape(self, url, selector=None, use_browser=None):
        """Intelligently scrape URL"""
        
        # Determine method
        if use_browser is None:
            use_browser = self._should_use_browser(url)
        
        if use_browser:
            return self._scrape_with_browser(url, selector)
        else:
            return self._scrape_with_requests(url)
    
    def _scrape_with_requests(self, url):
        """Scrape using requests with anti-blocking"""
        try:
            self.ip_strategy.apply_delay()
            
            config = self.ip_strategy.get_request_config()
            logger.info(f"Scraping {url} with requests")
            
            response = requests.get(url, **config)
            response.raise_for_status()
            
            logger.info(f"Successfully scraped {url}")
            return response.text
        
        except requests.exceptions.RequestException as e:
            logger.warning(f"Requests failed for {url}: {e}. Trying browser...")
            return self._scrape_with_browser(url)
    
    def _scrape_with_browser(self, url, selector=None):
        """Scrape using browser"""
        try:
            proxy = None
            if self._should_rotate_ip(url):
                proxy = self.ip_strategy.proxy_rotator.get_next_proxy()
            
            if not self.browser:
                self.browser = BrowserScraper(headless=True, use_proxy=proxy)
            
            logger.info(f"Scraping {url} with browser")
            html = self.browser.scrape(url, wait_selector=selector)
            
            if html:
                logger.info(f"Successfully scraped {url} with browser")
                return html
            else:
                logger.error(f"Browser scraping failed for {url}")
                return None
        
        except Exception as e:
            logger.error(f"Browser scraping error: {e}")
            return None
    
    def scrape_with_fallback(self, url, selector=None):
        """Scrape with automatic fallback"""
        logger.info(f"Attempting to scrape {url}")
        
        # Try requests first
        html = self._scrape_with_requests(url)
        
        if html and len(html) > 100:
            return html
        
        # Fallback to browser
        logger.warning(f"Requests returned insufficient data, using browser")
        html = self._scrape_with_browser(url, selector)
        
        return html
    
    def close(self):
        """Close browser if open"""
        if self.browser:
            self.browser.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class ScraperFactory:
    """Factory for creating appropriate scraper"""
    
    @staticmethod
    def create_scraper(url, use_proxies=False, proxy_list=None):
        """Create appropriate scraper for URL"""
        return IntelligentScraper(use_proxies, proxy_list)
    
    @staticmethod
    def get_scraper_type(url):
        """Get recommended scraper type"""
        scraper = IntelligentScraper()
        if scraper._should_use_browser(url):
            return 'browser'
        elif scraper._should_rotate_ip(url):
            return 'requests_with_rotation'
        else:
            return 'simple_requests'
