# Price Scraper

A Python-based web scraper for collecting product prices from various e-commerce sites.

## Project Structure

```
price-scraper/
├── config/
│   └── sites.yaml          # Site configurations
├── src/
│   ├── __init__.py
│   ├── models.py           # Data models
│   ├── utils.py            # Utility functions
│   ├── api_client.py       # API client for sending data
│   ├── scraper.py          # Main scraper logic
│   └── parsers/
│       ├── __init__.py
│       └── base.py         # Base parser class
├── logs/                   # Log files (auto-created)
├── data/                   # Optional data exports
├── .env                    # Environment variables
├── .env.example            # Example environment variables
├── requirements.txt        # Python dependencies
├── main.py                 # Entry point
└── README.md              # This file
```

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment variables:**
   - Copy `.env.example` to `.env`
   - Update the values in `.env` with your API credentials

3. **Configure sites:**
   - Edit `config/sites.yaml` to add the sites you want to scrape
   - Implement site-specific parsers in `src/parsers/`

## Usage

Run the scraper:
```bash
python main.py
```

## Creating Custom Parsers

To scrape a specific site, create a custom parser by extending `BaseParser`:

```python
from src.parsers.base import BaseParser
from src.models import Product

class MyCustomParser(BaseParser):
    def parse(self, url: str, site_name: str) -> List[Product]:
        soup = self.fetch_page(url)
        # Implement your parsing logic
        products = []
        # Extract products from soup
        return products
    
    def extract_product_data(self, element) -> Product:
        # Extract product data from element
        return Product(...)
```

Then register it in `main.py`:
```python
scraper.register_parser('my_site', MyCustomParser())
```

## Features

- ✅ Modular parser architecture
- ✅ YAML-based site configuration
- ✅ API client for data submission
- ✅ Logging support
- ✅ Environment-based configuration
- ✅ Extensible design

## Requirements

- Python 3.7+
- See `requirements.txt` for package dependencies

## License

MIT
