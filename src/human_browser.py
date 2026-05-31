"""Human-like browsing behavior simulation"""

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import time
import random
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class HumanBrowser:
    """Simulate real human browsing behavior"""
    
    def __init__(self, headless=False, screenshot_dir='screenshots'):
        self.driver = None
        self.headless = headless
        self.screenshot_dir = Path(screenshot_dir)
        self.screenshot_dir.mkdir(exist_ok=True)
        self.screenshot_count = 0
    
    def _setup_driver(self):
        """Setup Chrome driver with human-like options"""
        from selenium.webdriver.chrome.options import Options
        
        options = Options()
        if self.headless:
            options.add_argument('--headless')
        
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--window-size=1920,1080')
        
        self.driver = webdriver.Chrome(options=options)
        
        # Hide automation
        self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': 'Object.defineProperty(navigator, "webdriver", {get: () => false})'
        })
    
    def _random_delay(self, min_sec=0.5, max_sec=3):
        """Random human-like delay"""
        delay = random.uniform(min_sec, max_sec)
        time.sleep(delay)
    
    def _human_mouse_move(self, element):
        """Move mouse to element like a human (not instant)"""
        actions = ActionChains(self.driver)
        
        # Get element position
        location = element.location
        size = element.size
        
        # Random point within element
        x = location['x'] + random.randint(0, size['width'])
        y = location['y'] + random.randint(0, size['height'])
        
        # Move mouse gradually (like human)
        actions.move_by_offset(x, y)
        actions.perform()
        
        self._random_delay(0.2, 0.8)
    
    def _human_scroll(self, direction='down', amount=3):
        """Scroll like a human (not instant)"""
        for i in range(amount):
            if direction == 'down':
                self.driver.execute_script("window.scrollBy(0, 300);")
            else:
                self.driver.execute_script("window.scrollBy(0, -300);")
            
            self._random_delay(0.5, 1.5)
    
    def _take_screenshot(self, name=None):
        """Take screenshot for observation"""
        self.screenshot_count += 1
        filename = name or f"screenshot_{self.screenshot_count:03d}.png"
        filepath = self.screenshot_dir / filename
        
        self.driver.save_screenshot(str(filepath))
        logger.info(f"Screenshot saved: {filepath}")
        return filepath
    
    def _observe_page(self):
        """Observe page like a human would"""
        # Take initial screenshot
        self._take_screenshot("initial_view.png")
        
        # Scroll and observe
        self._human_scroll('down', amount=2)
        self._take_screenshot("after_scroll_down.png")
        
        # Scroll back up
        self._human_scroll('up', amount=1)
        self._take_screenshot("after_scroll_up.png")
    
    def visit_page(self, url):
        """Visit page like a human"""
        if not self.driver:
            self._setup_driver()
        
        logger.info(f"Visiting {url}")
        self.driver.get(url)
        
        # Random wait for page load
        self._random_delay(2, 4)
        
        # Observe page
        self._observe_page()
        
        return self.driver.page_source
    
    def click_element(self, selector, human_like=True):
        """Click element like a human"""
        from selenium.webdriver.common.by import By
        
        element = self.driver.find_element(By.CSS_SELECTOR, selector)
        
        if human_like:
            self._human_mouse_move(element)
        
        element.click()
        self._random_delay(1, 2)
        logger.info(f"Clicked: {selector}")
    
    def type_text(self, selector, text, human_like=True):
        """Type text like a human (with delays between keys)"""
        from selenium.webdriver.common.by import By
        
        element = self.driver.find_element(By.CSS_SELECTOR, selector)
        
        if human_like:
            self._human_mouse_move(element)
        
        element.click()
        self._random_delay(0.5, 1)
        
        # Type with human-like delays
        for char in text:
            element.send_keys(char)
            self._random_delay(0.05, 0.15)  # Delay between keystrokes
        
        logger.info(f"Typed: {text}")
    
    def search_and_observe(self, search_box_selector, search_term):
        """Search and observe results like a human"""
        self.type_text(search_box_selector, search_term)
        self._random_delay(1, 2)
        
        # Press Enter
        from selenium.webdriver.common.by import By
        element = self.driver.find_element(By.CSS_SELECTOR, search_box_selector)
        element.send_keys(Keys.RETURN)
        
        # Wait for results
        self._random_delay(3, 5)
        
        # Observe results
        self._take_screenshot("search_results.png")
        self._human_scroll('down', amount=3)
        self._take_screenshot("search_results_scrolled.png")
    
    def hover_element(self, selector):
        """Hover over element like a human"""
        from selenium.webdriver.common.by import By
        
        element = self.driver.find_element(By.CSS_SELECTOR, selector)
        actions = ActionChains(self.driver)
        actions.move_to_element(element)
        actions.perform()
        
        self._random_delay(0.5, 1.5)
        logger.info(f"Hovered: {selector}")
    
    def get_page_info(self):
        """Get page information like a human observer would"""
        info = {
            'title': self.driver.title,
            'url': self.driver.current_url,
            'page_height': self.driver.execute_script("return document.body.scrollHeight"),
            'viewport_height': self.driver.execute_script("return window.innerHeight"),
        }
        return info
    
    def extract_visible_text(self):
        """Extract visible text from page"""
        text = self.driver.execute_script("""
            return document.body.innerText;
        """)
        return text
    
    def get_all_links(self):
        """Get all links on page"""
        links = self.driver.execute_script("""
            return Array.from(document.querySelectorAll('a'))
                .map(a => ({text: a.innerText, href: a.href}))
                .filter(a => a.text.trim().length > 0);
        """)
        return links
    
    def get_all_prices(self):
        """Extract prices from page"""
        prices = self.driver.execute_script("""
            return Array.from(document.querySelectorAll('*'))
                .map(el => el.innerText)
                .filter(text => /\$\d+/.test(text))
                .slice(0, 10);
        """)
        return prices
    
    def random_browsing(self, duration_seconds=30):
        """Random browsing behavior for specified duration"""
        start_time = time.time()
        
        while time.time() - start_time < duration_seconds:
            # Random action
            action = random.choice(['scroll', 'hover', 'click', 'wait'])
            
            if action == 'scroll':
                direction = random.choice(['down', 'up'])
                self._human_scroll(direction, amount=1)
                logger.info(f"Random scroll: {direction}")
            
            elif action == 'hover':
                # Hover over random element
                try:
                    elements = self.driver.find_elements("tag name", "a")
                    if elements:
                        random.choice(elements)
                        self._random_delay(0.5, 1)
                except:
                    pass
            
            elif action == 'wait':
                self._random_delay(2, 5)
                logger.info("Random wait")
            
            self._random_delay(1, 3)
    
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
