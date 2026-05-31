# Anti-Blocking & Browser Scraping Guide

## Problem: IP Blocking

Websites block scrapers by:
1. **IP Detection** - Same IP making too many requests
2. **User-Agent Detection** - Recognizing bot patterns
3. **JavaScript Rendering** - Content loaded dynamically
4. **Rate Limiting** - Too many requests per second

## Solutions Implemented

### 1. **Anti-Blocking Mechanisms** (`anti_blocking.py`)

#### Proxy Rotation
```python
from src.anti_blocking import ProxyRotator

rotator = ProxyRotator(['http://proxy1:8080', 'http://proxy2:8080'])
proxy = rotator.get_proxy_dict()
```

#### User-Agent Rotation
```python
from src.anti_blocking import UserAgentRotator

ua_rotator = UserAgentRotator()
headers = {'User-Agent': ua_rotator.get_random_user_agent()}
```

#### Request Delays
```python
from src.anti_blocking import RequestDelayer

delayer = RequestDelayer(min_delay=2, max_delay=8)
delayer.wait()  # Random delay between 2-8 seconds
```

#### Complete Strategy
```python
from src.anti_blocking import IPRotationStrategy

strategy = IPRotationStrategy()
strategy.add_proxies(['proxy1', 'proxy2', 'proxy3'])
config = strategy.get_request_config()  # Get headers + proxies
strategy.apply_delay()
```

### 2. **Browser-Based Scraping** (`browser_scraper.py`)

Like MCP servers, uses real browser (Selenium) to:
- Execute JavaScript
- Bypass anti-bot detection
- Handle dynamic content
- Appear as real user

```python
from src.browser_scraper import BrowserScraper

# Simple usage
with BrowserScraper(headless=True) as scraper:
    html = scraper.scrape('https://example.com', wait_selector='.product')
    prices = scraper.get_all_elements_text('.price')
```

#### Advanced Features
```python
# With proxy
scraper = BrowserScraper(use_proxy='http://proxy:8080')

# Execute custom JavaScript
html, result = scraper.scrape_with_javascript(
    'https://example.com',
    'return document.querySelectorAll(".price").map(el => el.textContent)'
)

# Interact with page
scraper.click_element('.load-more-button')
scraper.scroll_to_bottom()
```

### 3. **Intelligent Scraper** (`intelligent_scraper.py`)

Automatically chooses best method:

```python
from src.intelligent_scraper import IntelligentScraper

scraper = IntelligentScraper(use_proxies=True, proxy_list=['proxy1', 'proxy2'])

# Automatically uses browser for Amazon, requests for others
html = scraper.scrape('https://amazon.com/product')

# With fallback
html = scraper.scrape_with_fallback('https://example.com')
```

#### Scraper Factory
```python
from src.intelligent_scraper import ScraperFactory

# Get recommended scraper type
scraper_type = ScraperFactory.get_scraper_type('https://amazon.com')
# Returns: 'browser'

scraper = ScraperFactory.create_scraper('https://example.com')
```

## Configuration

### Environment Variables
```bash
# Proxies (comma-separated)
PROXIES=http://proxy1:8080,http://proxy2:8080

# Browser settings
HEADLESS=true
USE_PROXY=http://proxy:8080

# Request settings
MIN_DELAY=2
MAX_DELAY=8
```

### Sites Requiring Browser
- amazon.com
- ebay.com
- alibaba.com
- etsy.com
- shopify stores
- JavaScript-heavy sites

### Sites Prone to Blocking
- amazon.com
- ebay.com
- linkedin.com
- instagram.com
- facebook.com

## Best Practices

1. **Always use delays** - Minimum 2-5 seconds between requests
2. **Rotate user agents** - Appear as different browsers
3. **Use proxies** - For high-volume scraping
4. **Respect robots.txt** - Check before scraping
5. **Use browser for JS** - When content is dynamically loaded
6. **Monitor rate limits** - Adjust delays if getting 429 errors
7. **Rotate IPs** - Use proxy rotation for blocking-prone sites

## Performance Comparison

| Method | Speed | Reliability | Resource Usage |
|--------|-------|-------------|-----------------|
| Simple Requests | Fast | Low (blocks easily) | Low |
| Requests + Rotation | Medium | Medium | Low |
| Browser | Slow | High | High |
| Browser + Proxy | Slow | Very High | High |

## Example: Scraping Amazon

```python
from src.intelligent_scraper import IntelligentScraper

scraper = IntelligentScraper(
    use_proxies=True,
    proxy_list=['proxy1:8080', 'proxy2:8080']
)

# Automatically uses browser + proxy rotation
html = scraper.scrape('https://amazon.com/s?k=laptop')

# Extract prices
from bs4 import BeautifulSoup
soup = BeautifulSoup(html, 'html.parser')
prices = [p.text for p in soup.find_all('span', class_='a-price-whole')]
```

## Troubleshooting

### Getting 403 Forbidden
- Add delays between requests
- Rotate user agents
- Use proxies
- Switch to browser scraping

### Getting 429 Too Many Requests
- Increase delays
- Use more proxies
- Reduce concurrent requests

### JavaScript not loading
- Use browser scraper
- Increase wait time
- Check wait_selector

### Browser crashes
- Reduce number of concurrent browsers
- Increase memory
- Use headless mode

## CLI Usage

```bash
# Create alert with browser scraping
python -m src.cli create-alert --site amazon.com --product laptop --price 800

# Check scraper type
python -m src.cli scraper-type https://amazon.com

# Test proxy
python -m src.cli test-proxy http://proxy:8080
```

---

**Note**: Always respect website terms of service and robots.txt. Use responsibly!
