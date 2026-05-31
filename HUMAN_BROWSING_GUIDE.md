# Human-Like Browsing Guide

## Overview

The price scraper now includes **human-like browsing behavior** that mimics real user interactions:

- 🖱️ **Mouse movements** - Gradual, natural mouse movement
- ⌨️ **Typing delays** - Realistic keystroke timing
- 📜 **Human scrolling** - Gradual scrolling with pauses
- 📸 **Screenshots** - Observe page state at each step
- 🔍 **Page observation** - Analyze visible content
- 🎲 **Random behavior** - Unpredictable actions to avoid detection

## Features

### 1. Human Mouse Movement
```python
from src.human_browser import HumanBrowser

browser = HumanBrowser()
element = browser.driver.find_element("css selector", ".product")
browser._human_mouse_move(element)  # Gradual movement
```

### 2. Human Typing
```python
# Types with realistic delays between keystrokes
browser.type_text('#search-box', 'laptop', human_like=True)
```

### 3. Human Scrolling
```python
# Scroll down gradually
browser._human_scroll('down', amount=3)

# Scroll up
browser._human_scroll('up', amount=2)
```

### 4. Screenshots & Observation
```python
# Take screenshots at each step
browser._take_screenshot("initial_view.png")
browser._human_scroll('down', amount=2)
browser._take_screenshot("after_scroll.png")

# Observe page automatically
browser._observe_page()  # Takes multiple screenshots
```

### 5. Page Analysis
```python
# Get page information
info = browser.get_page_info()
# Returns: title, url, page_height, viewport_height

# Extract visible text
text = browser.extract_visible_text()

# Get all links
links = browser.get_all_links()

# Extract prices
prices = browser.get_all_prices()
```

### 6. Random Browsing
```python
# Simulate random human browsing for 30 seconds
browser.random_browsing(duration_seconds=30)
```

## Usage Examples

### Example 1: Search Amazon Like a Human
```python
from src.human_browser import HumanBrowser

with HumanBrowser(headless=False) as browser:
    # Visit Amazon
    browser.visit_page('https://www.amazon.com')
    
    # Search like a human
    browser.search_and_observe('#twotabsearchtextbox', 'laptop')
    
    # Observe results
    browser._human_scroll('down', amount=3)
    browser._take_screenshot("results.png")
    
    # Extract prices
    prices = browser.get_all_prices()
    print(prices)
```

### Example 2: Compare Prices Across Sites
```python
from src.advanced_scraper import AdvancedHumanScraper

scraper = AdvancedHumanScraper()
results = scraper.compare_prices('MacBook Pro')

print(f"Amazon: {results['amazon']}")
print(f"eBay: {results['ebay']}")

# Get all screenshots
screenshots = scraper.get_screenshots()
print(f"Screenshots: {screenshots}")

scraper.close()
```

### Example 3: Custom Interactions
```python
from src.advanced_scraper import AdvancedHumanScraper

scraper = AdvancedHumanScraper()

interactions = [
    {'action': 'click', 'selector': '.filter-button'},
    {'action': 'type', 'selector': '#price-input', 'value': '500'},
    {'action': 'click', 'selector': '.apply-filter'},
    {'action': 'scroll', 'value': 'down'},
]

html = scraper.scrape_with_interaction('https://example.com', interactions)
scraper.close()
```

### Example 4: Scrape with Screenshots
```python
from src.human_browser import HumanBrowser

with HumanBrowser(headless=False, screenshot_dir='my_screenshots') as browser:
    # Visit page
    browser.visit_page('https://amazon.com/s?k=laptop')
    
    # Interact
    browser.click_element('.filter-option')
    browser._take_screenshot("after_filter.png")
    
    # Scroll and observe
    browser._human_scroll('down', amount=5)
    browser._take_screenshot("scrolled_view.png")
    
    # Get page info
    info = browser.get_page_info()
    print(f"Page height: {info['page_height']}")
```

## How It Works

### Mouse Movement
- Calculates random point within element
- Moves mouse gradually (not instant)
- Adds human-like delays

### Typing
- Types each character individually
- Random delay between keystrokes (50-150ms)
- Appears like real typing

### Scrolling
- Scrolls in increments (300px per step)
- Pauses between scrolls (500-1500ms)
- Can scroll up or down

### Screenshots
- Saves PNG files to specified directory
- Numbered sequentially
- Useful for debugging and observation

### Random Browsing
- Randomly scrolls, hovers, clicks
- Adds unpredictable delays
- Simulates real user behavior

## Configuration

### Screenshot Directory
```python
browser = HumanBrowser(screenshot_dir='my_screenshots')
```

### Headless Mode
```python
# Show browser window
browser = HumanBrowser(headless=False)

# Hide browser window
browser = HumanBrowser(headless=True)
```

### Delay Ranges
```python
# Customize delays
browser._random_delay(min_sec=1, max_sec=5)
```

## Advanced Features

### Extract Structured Data
```python
# Get all links with text and href
links = browser.get_all_links()
# Returns: [{'text': 'Product', 'href': 'https://...'}, ...]

# Get all prices
prices = browser.get_all_prices()
# Returns: ['$99.99', '$199.99', ...]

# Get visible text
text = browser.extract_visible_text()
```

### Hover & Interact
```python
# Hover over element
browser.hover_element('.product-card')

# Click element
browser.click_element('.add-to-cart')

# Type in input
browser.type_text('#search', 'laptop')
```

### Page Information
```python
info = browser.get_page_info()
print(info)
# {
#   'title': 'Amazon.com',
#   'url': 'https://amazon.com/...',
#   'page_height': 5000,
#   'viewport_height': 1080
# }
```

## Anti-Detection Features

The HumanBrowser includes:
- ✅ Hides automation signals
- ✅ Realistic user agent
- ✅ Natural mouse movement
- ✅ Human typing delays
- ✅ Random browsing patterns
- ✅ Screenshot observation
- ✅ Realistic page interactions

## Performance Tips

1. **Use headless=True for speed** - Faster execution
2. **Use headless=False for debugging** - See what's happening
3. **Adjust delays** - Longer delays = more human-like but slower
4. **Take screenshots strategically** - Only when needed
5. **Use random_browsing sparingly** - Can be slow

## Troubleshooting

### Issue: Browser crashes
**Solution:** Reduce concurrent browsers, increase memory

### Issue: Screenshots not saving
**Solution:** Check directory permissions, ensure directory exists

### Issue: Slow performance
**Solution:** Reduce delays, use headless mode, limit screenshots

### Issue: Detection still happening
**Solution:** Increase delays, use more random behavior, add proxies

## CLI Integration

```bash
# Scrape with human behavior
python -m src.cli scrape-human --url https://amazon.com --search "laptop"

# Compare prices with human behavior
python -m src.cli compare-prices-human --term "MacBook Pro"
```

## Best Practices

1. **Always use delays** - Minimum 2-5 seconds between actions
2. **Take screenshots** - For debugging and verification
3. **Observe pages** - Use get_page_info() to understand structure
4. **Random behavior** - Use random_browsing() occasionally
5. **Respect robots.txt** - Check before scraping
6. **Use proxies** - For high-volume scraping
7. **Monitor detection** - Watch for 403/429 errors

## Performance Comparison

| Method | Speed | Detection Risk | Resource |
|--------|-------|-----------------|----------|
| Fast Requests | Very Fast | Very High | Low |
| Browser (instant) | Fast | High | High |
| Browser (human) | Slow | Very Low | High |
| Browser + Proxy | Very Slow | Minimal | Very High |

---

**Note**: Human-like browsing is slower but much more effective at avoiding detection!
