"""Browser-based scraping using Selenium (like MCP servers)"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import logging
import time

logger = logging.getLogger(__name__)


class BrowserScraper:
    """Scrape using real browser (Selenium) to bypass anti-bot detection"""
    
    def __init__(self, headless=True, use_proxy=None):
        self.headless = headless
        self.use_proxy = use_proxy
        self.driver = None
    
    def _setup_driver(self):
        """Setup Chrome driver with anti-detection options"""
        options = Options()
        
        if self.headless:
            options.add_argument('--headless')
        
        # Anti-detection options
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        
        # Add proxy if provided
        if self.use_proxy:
            options.add_argument(f'--proxy-server={self.use_proxy}')
        
        # Random user agent
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
        ]
        import random
        options.add_argument(f'user-agent={random.choice(user_agents)}')
        
        self.driver = webdriver.Chrome(options=options)
        
        # Inject JavaScript to hide automation
        self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => false,
                });
            '''
        })
    
    def scrape(self, url, wait_selector=None, wait_time=10):
        """Scrape page using browser"""
        try:
            if not self.driver:
                self._setup_driver()
            
            logger.info(f"Loading {url}")
            self.driver.get(url)
            
            # Wait for element to load
            if wait_selector:
                WebDriverWait(self.driver, wait_time).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, wait_selector))
                )
                logger.debug(f"Element {wait_selector} loaded")
            else:
                time.sleep(3)  # Default wait
            
            # Scroll to load lazy content
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            return self.driver.page_source
        
        except Exception as e:
            logger.error(f"Failed to scrape {url}: {e}")
            return None
    
    def scrape_with_javascript(self, url, javascript_code, wait_time=10):
        """Scrape page and execute custom JavaScript"""
        try:
            if not self.driver:
                self._setup_driver()
            
            logger.info(f"Loading {url}")
            self.driver.get(url)
            time.sleep(wait_time)
            
            # Execute custom JavaScript
            result = self.driver.execute_script(javascript_code)
            logger.debug(f"JavaScript executed, result: {result}")
            
            return self.driver.page_source, result
        
        except Exception as e:
            logger.error(f"Failed to scrape {url}: {e}")
            return None, None
    
    def get_element_text(self, selector):
        """Get text from element"""
        try:
            element = self.driver.find_element(By.CSS_SELECTOR, selector)
            return element.text
        except Exception as e:
            logger.error(f"Failed to get element {selector}: {e}")
            return None
    
    def get_all_elements_text(self, selector):
        """Get text from all matching elements"""
        try:
            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
            return [el.text for el in elements]
        except Exception as e:
            logger.error(f"Failed to get elements {selector}: {e}")
            return []
    
    def click_element(self, selector):
        """Click element"""
        try:
            element = self.driver.find_element(By.CSS_SELECTOR, selector)
            element.click()
            logger.debug(f"Clicked {selector}")
            return True
        except Exception as e:
            logger.error(f"Failed to click {selector}: {e}")
            return False
    
    def scroll_to_bottom(self):
        """Scroll to bottom of page"""
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
    
    def close(self):
        """Close browser"""
        if self.driver:
            self.driver.quit()
            logger.info("Browser closed")
    
    def __enter__(self):
        self._setup_driver()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
