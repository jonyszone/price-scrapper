# Quick Start Guide

## 5-Minute Setup

### Step 1: Install
```bash
pip install -r requirements.txt
```

### Step 2: Configure
```bash
cp .env.example .env
# Edit .env with your settings
```

### Step 3: Create Alert
```bash
python -m src.cli create-alert --site amazon.com --product laptop --price 800
```

### Step 4: Start Dashboard
```bash
python -m src.cli dashboard --port 5000
```

### Step 5: Check Alerts
```bash
python -m src.cli check-alerts
```

Visit `http://localhost:5000` to see your dashboard!

---

## Common Tasks

### Create Price Alert
```bash
python -m src.cli create-alert \
  --site amazon.com \
  --product "MacBook Pro" \
  --price 1200
```

### View All Alerts
```bash
python -m src.cli list-alerts
```

### Get Price Statistics
```bash
python -m src.cli stats \
  --site amazon.com \
  --product "MacBook Pro" \
  --days 30
```

### Export Data
```bash
python -m src.cli export-data
# Creates: price_history_YYYYMMDD_HHMMSS.csv
```

### Delete Alert
```bash
python -m src.cli delete-alert --alert-id 1
```

### Check System Status
```bash
python -m src.cli status
```

---

## Python API Usage

### Basic Scraping
```python
from src.intelligent_scraper import IntelligentScraper

scraper = IntelligentScraper()
html = scraper.scrape('https://amazon.com/s?k=laptop')
print(html[:500])
```

### Create Alert
```python
from src.database import Database
from src.alerts import AlertManager

db = Database()
alert_manager = AlertManager(db)
alert = alert_manager.create_alert('amazon.com', 'laptop', 800)
print(f"Alert created: {alert.id}")
```

### Check Alerts
```python
triggered = alert_manager.check_alerts()
for alert in triggered:
    print(f"Price dropped: {alert['product']} - ${alert['current_price']}")
```

### Get Statistics
```python
from src.alerts import PriceComparator

comparator = PriceComparator(db)
lowest = comparator.get_lowest_price('amazon.com', 'laptop', days=30)
highest = comparator.get_highest_price('amazon.com', 'laptop', days=30)
average = comparator.get_average_price('amazon.com', 'laptop', days=30)

print(f"Lowest: ${lowest}")
print(f"Highest: ${highest}")
print(f"Average: ${average}")
```

### Browser Scraping
```python
from src.browser_scraper import BrowserScraper

with BrowserScraper(headless=True) as scraper:
    html = scraper.scrape('https://amazon.com/s?k=laptop', wait_selector='.s-result-item')
    prices = scraper.get_all_elements_text('.a-price-whole')
    print(prices)
```

### Send Email Alert
```python
from src.notifications import EmailNotifier

notifier = EmailNotifier()
notifier.send_alert(
    'user@example.com',
    'MacBook Pro',
    target_price=1200,
    current_price=999,
    site_name='amazon.com'
)
```

---

## Configuration Examples

### .env File
```bash
# Database
DATABASE_URL=sqlite:///price_scraper.db

# Logging
LOG_LEVEL=INFO

# Scraping
MIN_DELAY=2
MAX_DELAY=8
HEADLESS=true

# Email
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password

# Proxies (optional)
PROXIES=http://proxy1:8080,http://proxy2:8080
```

### sites.yaml
```yaml
sites:
  - name: "Amazon"
    url: "https://amazon.com/s?k=laptop"
    enabled: true
    parser: "browser"
    selectors:
      product: ".s-result-item"
      price: ".a-price-whole"
      title: "h2 a span"
  
  - name: "eBay"
    url: "https://www.ebay.com/sch/i.html?_nkw=laptop"
    enabled: true
    parser: "browser"
    selectors:
      product: ".s-item"
      price: ".s-item__price"
      title: ".s-item__title"
```

---

## Troubleshooting

### Issue: Getting 403 Forbidden
**Solution:**
```python
# Use browser scraping
scraper = IntelligentScraper(use_proxies=True)
html = scraper.scrape('https://amazon.com/product')
```

### Issue: Getting 429 Too Many Requests
**Solution:**
```bash
# Increase delays in .env
MIN_DELAY=5
MAX_DELAY=15
```

### Issue: JavaScript not loading
**Solution:**
```python
# Use browser scraper with wait selector
with BrowserScraper() as scraper:
    html = scraper.scrape(url, wait_selector='.product')
```

### Issue: Email not sending
**Solution:**
```bash
# Check SMTP settings in .env
# For Gmail, use app-specific password
# Enable "Less secure app access" if needed
```

---

## Next Steps

1. **Read Full Documentation** - See [README.md](README.md)
2. **Learn Anti-Blocking** - See [ANTI_BLOCKING_GUIDE.md](ANTI_BLOCKING_GUIDE.md)
3. **Explore Features** - See [FEATURES.md](FEATURES.md)
4. **Create Custom Parser** - Extend `BaseParser` for your site
5. **Set Up Notifications** - Configure email alerts

---

## Support

For issues or questions:
1. Check the documentation files
2. Review the CLI help: `python -m src.cli --help`
3. Check logs in `logs/` directory
4. Enable DEBUG logging: `LOG_LEVEL=DEBUG`

---

**Ready to start?** Run: `python -m src.cli dashboard --port 5000`
