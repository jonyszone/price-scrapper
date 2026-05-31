"""Price comparison and alert system"""

from datetime import datetime, timedelta
from src.database import Database
import logging

logger = logging.getLogger(__name__)


class PriceComparator:
    """Compare prices and detect changes"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def get_price_change(self, site_name, product_name):
        """Get price change percentage"""
        history = self.db.get_price_history(site_name, product_name, limit=2)
        
        if len(history) < 2:
            return None
        
        current = history[0].price
        previous = history[1].price
        
        if previous == 0:
            return None
        
        change_percent = ((current - previous) / previous) * 100
        return {
            'current': current,
            'previous': previous,
            'change_percent': round(change_percent, 2),
            'is_increase': change_percent > 0
        }
    
    def get_lowest_price(self, site_name, product_name, days=30):
        """Get lowest price in last N days"""
        session = self.db.Session()
        try:
            from src.database import PriceHistory
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            result = session.query(PriceHistory).filter(
                PriceHistory.site_name == site_name,
                PriceHistory.product_name == product_name,
                PriceHistory.scraped_at >= cutoff_date
            ).order_by(PriceHistory.price).first()
            
            return result.price if result else None
        finally:
            session.close()
    
    def get_highest_price(self, site_name, product_name, days=30):
        """Get highest price in last N days"""
        session = self.db.Session()
        try:
            from src.database import PriceHistory
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            result = session.query(PriceHistory).filter(
                PriceHistory.site_name == site_name,
                PriceHistory.product_name == product_name,
                PriceHistory.scraped_at >= cutoff_date
            ).order_by(PriceHistory.price.desc()).first()
            
            return result.price if result else None
        finally:
            session.close()
    
    def get_average_price(self, site_name, product_name, days=30):
        """Get average price in last N days"""
        session = self.db.Session()
        try:
            from src.database import PriceHistory
            from sqlalchemy import func
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            result = session.query(func.avg(PriceHistory.price)).filter(
                PriceHistory.site_name == site_name,
                PriceHistory.product_name == product_name,
                PriceHistory.scraped_at >= cutoff_date
            ).scalar()
            
            return round(result, 2) if result else None
        finally:
            session.close()


class AlertManager:
    """Manage price alerts"""
    
    def __init__(self, db: Database):
        self.db = db
        self.comparator = PriceComparator(db)
    
    def check_alerts(self):
        """Check all active alerts and trigger if needed"""
        alerts = self.db.get_active_alerts()
        triggered = []
        
        for alert in alerts:
            latest = self.db.get_latest_price(alert.site_name, alert.product_name)
            
            if latest and latest.price <= alert.target_price:
                self.db.trigger_alert(alert.id)
                triggered.append({
                    'alert_id': alert.id,
                    'product': alert.product_name,
                    'target_price': alert.target_price,
                    'current_price': latest.price,
                    'savings': round(alert.target_price - latest.price, 2)
                })
                logger.info(f"Alert triggered: {alert.product_name} at ${latest.price}")
        
        return triggered
    
    def create_alert(self, site_name, product_name, target_price):
        """Create new price alert"""
        alert = self.db.create_alert(site_name, product_name, target_price)
        logger.info(f"Alert created: {product_name} at ${target_price}")
        return alert
    
    def get_alert_status(self, alert_id):
        """Get alert status"""
        session = self.db.Session()
        try:
            from src.database import PriceAlert
            alert = session.query(PriceAlert).filter(PriceAlert.id == alert_id).first()
            
            if not alert:
                return None
            
            latest = self.db.get_latest_price(alert.site_name, alert.product_name)
            
            return {
                'id': alert.id,
                'product': alert.product_name,
                'target_price': alert.target_price,
                'current_price': latest.price if latest else None,
                'is_active': alert.is_active,
                'triggered': alert.triggered_at is not None,
                'triggered_at': alert.triggered_at
            }
        finally:
            session.close()
