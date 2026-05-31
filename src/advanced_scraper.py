"""Advanced scraper with human-like behavior"""

from src.human_browser import HumanBrowser
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)


class AdvancedHumanScraper:
    """Scrape like a real human - with observation, interaction, and screenshots"""
    
    def __init__(self, screenshot_dir='screenshots'):
        self.browser = HumanBrowser(headless=False, screenshot_dir=screenshot_dir)
        self.screenshot_dir = screenshot_dir
    
    def scrape_amazon_product(self, search_term):
        """Scrape Amazon like a human would"""
        logger.info(f"Starting human-like Amazon scrape for: {search_term}")
        
        # Visit Amazon
        self.browser.visit_page('https://www.amazon.com')
        
        # Search like a human
        self.browser.search_and_observe('#twotabsearchtextbox', search_term)
        
        # Get page info
        info = self.browser.get_page_info()
        logger.info(f"Page info: {info}")
        
        # Extract prices
        prices = self.browser.get_all_prices()
        logger.info(f"Found prices: {prices}")
        
        # Get HTML
        html = self.browser.driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract products
        products = []
        for item in soup.find_all('div', {'data-component-type': 's-search-result'}):
            try:
                title = item.find('h2', {'class': 's-size-mini'}).text.strip()
                price_elem = item.find('span', {'class': 'a-price-whole'})
                price = price_elem.text.strip() if price_elem else 'N/A'
                
                products.append({
                    'title': title,
                    'price': price,
                    'source': 'amazon'
                })
            except:
                pass
        
        logger.info(f"Extracted {len(products)} products")
        return products
    
    def scrape_ebay_product(self, search_term):
        """Scrape eBay like a human would"""
        logger.info(f"Starting human-like eBay scrape for: {search_term}")
        
        # Visit eBay
        self.browser.visit_page('https://www.ebay.com')
        
        # Search
        self.browser.search_and_observe('#gh-ac', search_term)
        
        # Random browsing to appear human
        self.browser.random_browsing(duration_seconds=10)
        
        # Extract data
        html = self.browser.driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        products = []
        for item in soup.find_all('div', {'class': 's-item'}):
            try:
                title = item.find('h2', {'class': 's-item__title'}).text.strip()
                price_elem = item.find('span', {'class': 's-item__price'})
                price = price_elem.text.strip() if price_elem else 'N/A'
                
                products.append({
                    'title': title,
                    'price': price,
                    'source': 'ebay'
                })
            except:
                pass
        
        logger.info(f"Extracted {len(products)} products")
        return products
    
    def scrape_with_interaction(self, url, interactions):
        """Scrape with custom interactions"""
        logger.info(f"Scraping {url} with interactions")
        
        self.browser.visit_page(url)
        
        # Perform interactions
        for interaction in interactions:
            action = interaction.get('action')
            selector = interaction.get('selector')
            value = interaction.get('value')
            
            if action == 'click':
                self.browser.click_element(selector)
            elif action == 'type':
                self.browser.type_text(selector, value)
            elif action == 'hover':
                self.browser.hover_element(selector)
            elif action == 'scroll':
                direction = value or 'down'
                self.browser.human_scroll(direction, amount=2)
            
            logger.info(f"Performed: {action} on {selector}")
        
        # Take final screenshot
        self.browser._take_screenshot("final_state.png")
        
        return self.browser.driver.page_source
    
    def compare_prices(self, search_term):
        """Compare prices across multiple sites like a human would"""
        logger.info(f"Comparing prices for: {search_term}")
        
        results = {
            'search_term': search_term,
            'amazon': [],
            'ebay': [],
            'timestamp': str(__import__('datetime').datetime.now())
        }
        
        try:
            results['amazon'] = self.scrape_amazon_product(search_term)
        except Exception as e:
            logger.error(f"Amazon scrape failed: {e}")
        
        try:
            results['ebay'] = self.scrape_ebay_product(search_term)
        except Exception as e:
            logger.error(f"eBay scrape failed: {e}")
        
        return results
    
    def get_screenshots(self):
        """Get list of all screenshots taken"""
        from pathlib import Path
        screenshot_path = Path(self.screenshot_dir)
        screenshots = list(screenshot_path.glob('*.png'))
        return sorted(screenshots)
    
    def close(self):
        """Close browser"""
        self.browser.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class HumanScraperFactory:
    """Factory for creating human-like scrapers"""
    
    @staticmethod
    def create_amazon_scraper():
        """Create Amazon scraper"""
        return AdvancedHumanScraper(screenshot_dir='screenshots/amazon')
    
    @staticmethod
    def create_ebay_scraper():
        """Create eBay scraper"""
        return AdvancedHumanScraper(screenshot_dir='screenshots/ebay')
    
    @staticmethod
    def create_comparison_scraper():
        """Create price comparison scraper"""
        return AdvancedHumanScraper(screenshot_dir='screenshots/comparison')
