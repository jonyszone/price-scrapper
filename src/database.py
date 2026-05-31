"""Database models and operations for price history"""

from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

Base = declarative_base()


class PriceHistory(Base):
    """Model for storing price history"""
    __tablename__ = 'price_history'
    
    id = Column(Integer, primary_key=True)
    site_name = Column(String(100), nullable=False)
    product_name = Column(String(255), nullable=False)
    product_url = Column(String(500), nullable=False)
    price = Column(Float, nullable=False)
    currency = Column(String(10), default='USD')
    scraped_at = Column(DateTime, default=datetime.utcnow)
    is_available = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<PriceHistory({self.site_name}, {self.product_name}, ${self.price})>"


class PriceAlert(Base):
    """Model for price alerts"""
    __tablename__ = 'price_alerts'
    
    id = Column(Integer, primary_key=True)
    site_name = Column(String(100), nullable=False)
    product_name = Column(String(255), nullable=False)
    target_price = Column(Float, nullable=False)
    current_price = Column(Float)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    triggered_at = Column(DateTime)
    
    def __repr__(self):
        return f"<PriceAlert({self.product_name}, target=${self.target_price})>"


class Database:
    """Database manager"""
    
    def __init__(self, db_url=None):
        if db_url is None:
            db_url = os.getenv('DATABASE_URL', 'sqlite:///price_scraper.db')
        
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
    
    def add_price_history(self, site_name, product_name, product_url, price, currency='USD', is_available=True):
        """Add price history record"""
        session = self.Session()
        try:
            history = PriceHistory(
                site_name=site_name,
                product_name=product_name,
                product_url=product_url,
                price=price,
                currency=currency,
                is_available=is_available
            )
            session.add(history)
            session.commit()
            return history
        finally:
            session.close()
    
    def get_price_history(self, site_name, product_name, limit=100):
        """Get price history for a product"""
        session = self.Session()
        try:
            return session.query(PriceHistory).filter(
                PriceHistory.site_name == site_name,
                PriceHistory.product_name == product_name
            ).order_by(PriceHistory.scraped_at.desc()).limit(limit).all()
        finally:
            session.close()
    
    def get_latest_price(self, site_name, product_name):
        """Get latest price for a product"""
        session = self.Session()
        try:
            return session.query(PriceHistory).filter(
                PriceHistory.site_name == site_name,
                PriceHistory.product_name == product_name
            ).order_by(PriceHistory.scraped_at.desc()).first()
        finally:
            session.close()
    
    def create_alert(self, site_name, product_name, target_price):
        """Create price alert"""
        session = self.Session()
        try:
            alert = PriceAlert(
                site_name=site_name,
                product_name=product_name,
                target_price=target_price
            )
            session.add(alert)
            session.commit()
            return alert
        finally:
            session.close()
    
    def get_active_alerts(self):
        """Get all active alerts"""
        session = self.Session()
        try:
            return session.query(PriceAlert).filter(PriceAlert.is_active == True).all()
        finally:
            session.close()
    
    def trigger_alert(self, alert_id):
        """Mark alert as triggered"""
        session = self.Session()
        try:
            alert = session.query(PriceAlert).filter(PriceAlert.id == alert_id).first()
            if alert:
                alert.triggered_at = datetime.utcnow()
                session.commit()
            return alert
        finally:
            session.close()
