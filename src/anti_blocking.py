"""Anti-blocking mechanisms for web scraping"""

import random
import time
from typing import List
import logging

logger = logging.getLogger(__name__)


class ProxyRotator:
    """Rotate through proxies to avoid IP blocking"""
    
    def __init__(self, proxies: List[str] = None):
        self.proxies = proxies or []
        self.current_index = 0
    
    def add_proxy(self, proxy: str):
        """Add proxy to rotation"""
        self.proxies.append(proxy)
    
    def get_next_proxy(self):
        """Get next proxy in rotation"""
        if not self.proxies:
            return None
        
        proxy = self.proxies[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.proxies)
        return proxy
    
    def get_proxy_dict(self):
        """Get proxy dict for requests"""
        proxy = self.get_next_proxy()
        if proxy:
            return {'http': proxy, 'https': proxy}
        return None


class UserAgentRotator:
    """Rotate user agents to appear as different browsers"""
    
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
        'Mozilla/5.0 (X11; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59',
    ]
    
    def __init__(self):
        self.current_index = 0
    
    def get_random_user_agent(self):
        """Get random user agent"""
        return random.choice(self.USER_AGENTS)
    
    def get_next_user_agent(self):
        """Get next user agent in rotation"""
        ua = self.USER_AGENTS[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.USER_AGENTS)
        return ua


class RequestHeaders:
    """Generate realistic request headers"""
    
    @staticmethod
    def get_headers(user_agent=None):
        """Get realistic headers"""
        ua_rotator = UserAgentRotator()
        return {
            'User-Agent': user_agent or ua_rotator.get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
            'Referer': 'https://www.google.com/',
        }


class RequestDelayer:
    """Add intelligent delays between requests"""
    
    def __init__(self, min_delay=1, max_delay=5):
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.last_request_time = 0
    
    def wait(self):
        """Wait before next request"""
        delay = random.uniform(self.min_delay, self.max_delay)
        logger.debug(f"Waiting {delay:.2f}s before next request")
        time.sleep(delay)
        self.last_request_time = time.time()
    
    def wait_between_domains(self, domain1, domain2):
        """Wait longer between different domains"""
        if domain1 != domain2:
            delay = random.uniform(self.max_delay, self.max_delay * 2)
            logger.debug(f"Waiting {delay:.2f}s between domains")
            time.sleep(delay)


class IPRotationStrategy:
    """Strategy for rotating IPs"""
    
    def __init__(self):
        self.proxy_rotator = ProxyRotator()
        self.ua_rotator = UserAgentRotator()
        self.delayer = RequestDelayer(min_delay=2, max_delay=8)
    
    def add_proxies(self, proxies: List[str]):
        """Add proxies"""
        for proxy in proxies:
            self.proxy_rotator.add_proxy(proxy)
    
    def get_request_config(self):
        """Get complete request configuration"""
        return {
            'proxies': self.proxy_rotator.get_proxy_dict(),
            'headers': RequestHeaders.get_headers(self.ua_rotator.get_next_user_agent()),
            'timeout': 10
        }
    
    def apply_delay(self):
        """Apply delay before request"""
        self.delayer.wait()
