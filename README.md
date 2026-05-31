# Price Scraper - Enterprise Edition

A production-ready Python web scraper with anti-blocking, browser automation, database persistence, and real-time monitoring.

## 🚀 Features

### Core Scraping
- ✅ **Intelligent Scraping** - Auto-detects best method (requests vs browser)
- ✅ **Anti-Blocking** - Proxy rotation, user-agent rotation, request delays
- ✅ **Browser Automation** - Selenium-based scraping for JavaScript-heavy sites
- ✅ **Modular Parsers** - Easy to add custom site parsers

### Data Management
- ✅ **Database Support** - SQLite/PostgreSQL with SQLAlchemy ORM
- ✅ **Price History** - Track all price changes over time
- ✅ **Data Export** - CSV export functionality

### Monitoring & Alerts
- ✅ **Price Alerts** - Automatic notifications when prices drop
- ✅ **Web Dashboard** - Real-time monitoring interface
- ✅ **Email Notifications** - HTML-formatted price drop alerts
- ✅ **Price Statistics** - Min/max/average price analysis

### Performance
- ✅ **Caching** - TTL-based in-memory cache
- ✅ **Rate Limiting** - Configurable request throttling
- ✅ **Request Throttling** - Avoid overwhelming servers

### Management
- ✅ **CLI Tool** - 9 commands for complete control
- ✅ **Configuration** - YAML-based site configuration
- ✅ **Logging** - Comprehensive logging system

## 📋 Project Structure

```
price-scraper/
├── config/
│   └── sites.yaml                 # Site configurations
├── src/
│   ├── __init__.py
│   ├── models.py                  # Data models
│   ├── utils.py                   # Utility functions
│   ├── api_client.py              # API client
│   ├── scraper.py                 # Main scraper
│   ├── database.py                # Database models & operations
│   ├── alerts.py                  # Price alerts & comparison
│   ├── dashboard.py               # Web dashboard (Flask)
│   ├── cache.py                   # Caching & rate limiting
│   ├── notifications.py           # Email notifications
│   ├── anti_blocking.py           # Anti-blocking mechanisms
│   ├── browser_scraper.py         # Browser-based scraping
│   ├── intelligent_scraper.py     # Smart scraper selection
│   ├── cli.py                     # CLI tool
│   └── parsers/
│       ├── __init__.py
│       ├── base.py                # Base parser
│       ├── generic.py             # Generic parser
│       └── browser.py             # Browser parser
├── logs/                          # Log files
├── .env                           # Environment variables
├── .env.example                   # Example env
├── requirements.txt               # Dependencies
├── main.py                        # Entry point
├── README.md                      # This file
└── ANTI_BLOCKING_GUIDE.md        # Anti-blocking guide
```

## 🔧 Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your settings
```

### 3. Configure Sites
Edit `config/sites.yaml`:
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
```

## 📖 Usage

### Command Line Interface

```bash
# Create price alert
python -m src.cli create-alert --site amazon.com --product laptop --price 800

# List all alerts
python -m src.cli list-alerts

# Get price statistics
python -m src.cli stats --site amazon.com --product laptop --days 30

# Check alerts and trigger notifications
python -m src.cli check-alerts

# Start web dashboard
python -m src.cli dashboard --port 5000

# Export data to CSV
python -m src.cli export-data

# Show system status
python -m src.cli status

# Send test email
python -m src.cli send-test-email --email user@example.com

# Delete alert
python -m src.cli delete-alert --alert-id 1
```

### Python API

```python
from src.intelligent_scraper import IntelligentScraper
from src.database import Database
from src.alerts import AlertManager

# Scrape with auto-detection
scraper = IntelligentScraper(use_proxies=True, proxy_list=['proxy1', 'proxy2'])
html = scraper.scrape('https://amazon.com/product')

# Manage alerts
db = Database()
alert_manager = AlertManager(db)
alert = alert_manager.create_alert('amazon.com', 'laptop', 800)

# Check for triggered alerts
triggered = alert_manager.check_alerts()
```

## 🛡️ Anti-Blocking Features

### Proxy Rotation
```python
from src.anti_blocking import ProxyRotator

rotator = ProxyRotator(['http://proxy1:8080', 'http://proxy2:8080'])
proxy = rotator.get_proxy_dict()
```

### User-Agent Rotation
```python
from src.anti_blocking import UserAgentRotator

ua_rotator = UserAgentRotator()
headers = {'User-Agent': ua_rotator.get_random_user_agent()}
```

### Browser Scraping (Like MCP)
```python
from src.browser_scraper import BrowserScraper

with BrowserScraper(headless=True) as scraper:
    html = scraper.scrape('https://amazon.com', wait_selector='.product')
    prices = scraper.get_all_elements_text('.price')
```

### Intelligent Selection
```python
from src.intelligent_scraper import IntelligentScraper

# Automatically uses browser for Amazon, requests for others
scraper = IntelligentScraper()
html = scraper.scrape('https://amazon.com/product')
```

See [ANTI_BLOCKING_GUIDE.md](ANTI_BLOCKING_GUIDE.md) for detailed guide.

## 💾 Database

### Models

**PriceHistory** - Track all price changes
```python
db.add_price_history(
    site_name='amazon.com',
    product_name='laptop',
    product_url='https://...',
    price=999.99,
    currency='USD'
)
```

**PriceAlert** - Manage price alerts
```python
alert = db.create_alert('amazon.com', 'laptop', 800)
```

### Queries
```python
# Get price history
history = db.get_price_history('amazon.com', 'laptop', limit=100)

# Get latest price
latest = db.get_latest_price('amazon.com', 'laptop')

# Get active alerts
alerts = db.get_active_alerts()
```

## 📊 Web Dashboard

Start dashboard:
```bash
python -m src.cli dashboard --port 5000
```

Access at: `http://localhost:5000`

Features:
- Real-time price monitoring
- Active alerts display
- Price statistics
- Auto-refresh every 30 seconds

## 📧 Email Notifications

Configure SMTP in `.env`:
```
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
```

Send alerts:
```python
from src.notifications import EmailNotifier

notifier = EmailNotifier()
notifier.send_alert(
    'user@example.com',
    'laptop',
    target_price=800,
    current_price=699,
    site_name='amazon.com'
)
```

## ⚙️ Configuration

### Environment Variables
```bash
# Database
DATABASE_URL=sqlite:///price_scraper.db

# API
API_BASE_URL=https://api.example.com
API_KEY=your-api-key

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
SENDER_PASSWORD=your-password

# Proxies
PROXIES=http://proxy1:8080,http://proxy2:8080
```

## 🎯 Best Practices

1. **Always use delays** - Minimum 2-5 seconds between requests
2. **Rotate user agents** - Appear as different browsers
3. **Use proxies** - For high-volume scraping
4. **Respect robots.txt** - Check before scraping
5. **Use browser for JS** - When content is dynamically loaded
6. **Monitor rate limits** - Adjust delays if getting 429 errors
7. **Rotate IPs** - Use proxy rotation for blocking-prone sites

## 📈 Performance

| Method | Speed | Reliability | Resource |
|--------|-------|-------------|----------|
| Simple Requests | Fast | Low | Low |
| Requests + Rotation | Medium | Medium | Low |
| Browser | Slow | High | High |
| Browser + Proxy | Slow | Very High | High |

## 🔍 Troubleshooting

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

## 📚 Documentation

- [ANTI_BLOCKING_GUIDE.md](ANTI_BLOCKING_GUIDE.md) - Detailed anti-blocking guide
- [requirements.txt](requirements.txt) - All dependencies

## 🤝 Creating Custom Parsers

```python
from src.parsers.base import BaseParser
from src.models import Product

class MyCustomParser(BaseParser):
    def parse(self, url: str, site_name: str):
        soup = self.fetch_page(url)
        products = []
        for item in soup.find_all('.product'):
            products.append(self.extract_product_data(item))
        return products
    
    def extract_product_data(self, element):
        return Product(
            name=element.find('.title').text,
            price=float(element.find('.price').text.replace('$', '')),
            url=element.find('a')['href']
        )
```

Register in `main.py`:
```python
scraper.register_parser('my_site', MyCustomParser())
```

## 📝 License

MIT

## 🚀 Quick Start

```bash
# 1. Install
pip install -r requirements.txt

# 2. Configure
cp .env.example .env
# Edit .env

# 3. Create alert
python -m src.cli create-alert --site amazon.com --product laptop --price 800

# 4. Start dashboard
python -m src.cli dashboard

# 5. Check alerts
python -m src.cli check-alerts
```

---

**Status**: Production Ready ✅  
**Version**: 2.0 (Enterprise Edition)  
**Last Updated**: 2026-05-31
