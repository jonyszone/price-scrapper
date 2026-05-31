"""Caching and rate limiting for price scraper"""

import time
import hashlib
from datetime import datetime, timedelta
from functools import wraps
import logging

logger = logging.getLogger(__name__)


class Cache:
    """Simple in-memory cache with TTL"""
    
    def __init__(self, ttl_seconds=3600):
        self.cache = {}
        self.ttl = ttl_seconds
    
    def _get_key(self, *args, **kwargs):
        """Generate cache key from arguments"""
        key_str = str(args) + str(sorted(kwargs.items()))
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, *args, **kwargs):
        """Get value from cache"""
        key = self._get_key(*args, **kwargs)
        
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                logger.debug(f"Cache hit: {key}")
                return value
            else:
                del self.cache[key]
        
        return None
    
    def set(self, value, *args, **kwargs):
        """Set value in cache"""
        key = self._get_key(*args, **kwargs)
        self.cache[key] = (value, time.time())
        logger.debug(f"Cache set: {key}")
    
    def clear(self):
        """Clear all cache"""
        self.cache.clear()
    
    def cached(self, ttl=None):
        """Decorator for caching function results"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                cached_value = self.get(*args, **kwargs)
                if cached_value is not None:
                    return cached_value
                
                result = func(*args, **kwargs)
                self.set(result, *args, **kwargs)
                return result
            return wrapper
        return decorator


class RateLimiter:
    """Rate limiter for API calls"""
    
    def __init__(self, max_requests=10, window_seconds=60):
        self.max_requests = max_requests
        self.window = window_seconds
        self.requests = {}
    
    def is_allowed(self, identifier):
        """Check if request is allowed"""
        now = time.time()
        
        if identifier not in self.requests:
            self.requests[identifier] = []
        
        # Remove old requests outside window
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if now - req_time < self.window
        ]
        
        if len(self.requests[identifier]) < self.max_requests:
            self.requests[identifier].append(now)
            return True
        
        return False
    
    def get_wait_time(self, identifier):
        """Get seconds to wait before next request"""
        if identifier not in self.requests or not self.requests[identifier]:
            return 0
        
        oldest_request = min(self.requests[identifier])
        wait_time = self.window - (time.time() - oldest_request)
        return max(0, wait_time)
    
    def limit(self, identifier_func=None):
        """Decorator for rate limiting"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                identifier = identifier_func(*args, **kwargs) if identifier_func else 'default'
                
                if not self.is_allowed(identifier):
                    wait_time = self.get_wait_time(identifier)
                    logger.warning(f"Rate limit exceeded for {identifier}. Wait {wait_time:.1f}s")
                    time.sleep(wait_time)
                
                return func(*args, **kwargs)
            return wrapper
        return decorator


class RequestThrottler:
    """Throttle requests to avoid overwhelming servers"""
    
    def __init__(self, min_delay_seconds=1):
        self.min_delay = min_delay_seconds
        self.last_request_time = {}
    
    def throttle(self, identifier='default'):
        """Throttle requests"""
        now = time.time()
        
        if identifier in self.last_request_time:
            elapsed = now - self.last_request_time[identifier]
            if elapsed < self.min_delay:
                sleep_time = self.min_delay - elapsed
                logger.debug(f"Throttling {identifier} for {sleep_time:.2f}s")
                time.sleep(sleep_time)
        
        self.last_request_time[identifier] = time.time()
    
    def throttle_decorator(self, identifier_func=None):
        """Decorator for throttling"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                identifier = identifier_func(*args, **kwargs) if identifier_func else 'default'
                self.throttle(identifier)
                return func(*args, **kwargs)
            return wrapper
        return decorator


# Global instances
cache = Cache(ttl_seconds=3600)
rate_limiter = RateLimiter(max_requests=30, window_seconds=60)
throttler = RequestThrottler(min_delay_seconds=1)
