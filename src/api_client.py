"""API client for sending scraped data"""

import logging
from typing import List, Dict, Any
import requests
from src.models import Product


logger = logging.getLogger(__name__)


class APIClient:
    """Client for interacting with the backend API"""
    
    def __init__(self, base_url: str, api_key: str):
        """
        Initialize API client
        
        Args:
            base_url: Base URL of the API
            api_key: API key for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'X-API-Key': api_key,
            'Content-Type': 'application/json'
        })
    
    def send_products(self, products: List[Product]) -> Dict[str, Any]:
        """
        Send scraped products to the API
        
        Args:
            products: List of Product objects
            
        Returns:
            API response as dictionary
        """
        try:
            data = [
                {
                    'product_id': p.product_id,
                    'location_id': p.location_id,
                    'price': p.price,
                    'original_price': p.original_price,
                    'currency': p.currency,
                    'availability': p.availability,
                    'url': p.url,
                    'scraped_at': p.timestamp.isoformat(),
                    # Optional fields if API accepts them, otherwise remove
                    # 'image_url': p.image_url, 
                }
                for p in products
            ]
            
            response = self.session.post(
                f'{self.base_url}/api/v1/scraper/price/bulk',
                json={
                    'prices': data,
                    # Workaround for API bug: validation uses in_array:in_stock...
                    # so we must provide these keys
                    'in_stock': ['in_stock'],
                    'out_of_stock': ['out_of_stock'],
                    'limited': ['limited']
                }
            )
            response.raise_for_status()
            
            logger.info(f"Successfully sent {len(products)} products to API")
            return response.json()
            
        except requests.exceptions.RequestException as e:
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"API Error details: {e.response.text}")
            logger.error(f"Failed to send products to API: {e}")
            raise
    
    def health_check(self) -> bool:
        """Check API health"""
        try:
            response = self.session.get(f'{self.base_url}/api/health')
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
