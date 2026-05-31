"""Web dashboard for price monitoring"""

from flask import Flask, render_template_string, jsonify, request
from src.database import Database
from src.alerts import AlertManager, PriceComparator
import logging

logger = logging.getLogger(__name__)


class Dashboard:
    """Web dashboard for monitoring prices"""
    
    def __init__(self, db: Database, port=5000):
        self.app = Flask(__name__)
        self.db = db
        self.alert_manager = AlertManager(db)
        self.comparator = PriceComparator(db)
        self.port = port
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def index():
            return self._render_dashboard()
        
        @self.app.route('/api/prices')
        def get_prices():
            """Get all latest prices"""
            session = self.db.Session()
            try:
                from src.database import PriceHistory
                from sqlalchemy import func
                
                latest_prices = session.query(
                    PriceHistory.site_name,
                    PriceHistory.product_name,
                    func.max(PriceHistory.scraped_at).label('latest_date')
                ).group_by(PriceHistory.site_name, PriceHistory.product_name).all()
                
                prices = []
                for site, product, date in latest_prices:
                    latest = self.db.get_latest_price(site, product)
                    if latest:
                        prices.append({
                            'site': site,
                            'product': product,
                            'price': latest.price,
                            'currency': latest.currency,
                            'date': latest.scraped_at.isoformat(),
                            'available': latest.is_available
                        })
                
                return jsonify(prices)
            finally:
                session.close()
        
        @self.app.route('/api/alerts')
        def get_alerts():
            """Get all active alerts"""
            alerts = self.db.get_active_alerts()
            return jsonify([{
                'id': a.id,
                'product': a.product_name,
                'target_price': a.target_price,
                'site': a.site_name,
                'active': a.is_active,
                'triggered': a.triggered_at is not None
            } for a in alerts])
        
        @self.app.route('/api/alerts', methods=['POST'])
        def create_alert():
            """Create new alert"""
            data = request.json
            alert = self.alert_manager.create_alert(
                data['site_name'],
                data['product_name'],
                data['target_price']
            )
            return jsonify({'id': alert.id, 'status': 'created'}), 201
        
        @self.app.route('/api/stats/<site>/<product>')
        def get_stats(site, product):
            """Get price statistics"""
            return jsonify({
                'lowest_30d': self.comparator.get_lowest_price(site, product, 30),
                'highest_30d': self.comparator.get_highest_price(site, product, 30),
                'average_30d': self.comparator.get_average_price(site, product, 30),
                'change': self.comparator.get_price_change(site, product)
            })
    
    def _render_dashboard(self):
        """Render HTML dashboard"""
        html = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Price Scraper Dashboard</title>
            <style>
                body { font-family: Arial; margin: 20px; background: #f5f5f5; }
                .container { max-width: 1200px; margin: 0 auto; }
                h1 { color: #333; }
                .card { background: white; padding: 20px; margin: 10px 0; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
                table { width: 100%; border-collapse: collapse; }
                th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
                th { background: #4CAF50; color: white; }
                .price { font-weight: bold; color: #2196F3; }
                .up { color: red; }
                .down { color: green; }
                button { background: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
                button:hover { background: #45a049; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📊 Price Scraper Dashboard</h1>
                
                <div class="card">
                    <h2>Latest Prices</h2>
                    <table id="pricesTable">
                        <thead>
                            <tr>
                                <th>Site</th>
                                <th>Product</th>
                                <th>Price</th>
                                <th>Status</th>
                                <th>Last Updated</th>
                            </tr>
                        </thead>
                        <tbody></tbody>
                    </table>
                </div>
                
                <div class="card">
                    <h2>Active Alerts</h2>
                    <table id="alertsTable">
                        <thead>
                            <tr>
                                <th>Product</th>
                                <th>Target Price</th>
                                <th>Site</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody></tbody>
                    </table>
                </div>
            </div>
            
            <script>
                async function loadPrices() {
                    const res = await fetch('/api/prices');
                    const prices = await res.json();
                    const tbody = document.querySelector('#pricesTable tbody');
                    tbody.innerHTML = prices.map(p => `
                        <tr>
                            <td>${p.site}</td>
                            <td>${p.product}</td>
                            <td class="price">${p.currency} ${p.price}</td>
                            <td>${p.available ? '✓ Available' : '✗ Out of Stock'}</td>
                            <td>${new Date(p.date).toLocaleString()}</td>
                        </tr>
                    `).join('');
                }
                
                async function loadAlerts() {
                    const res = await fetch('/api/alerts');
                    const alerts = await res.json();
                    const tbody = document.querySelector('#alertsTable tbody');
                    tbody.innerHTML = alerts.map(a => `
                        <tr>
                            <td>${a.product}</td>
                            <td>$${a.target_price}</td>
                            <td>${a.site}</td>
                            <td>${a.triggered ? '🔔 Triggered' : '⏳ Waiting'}</td>
                        </tr>
                    `).join('');
                }
                
                loadPrices();
                loadAlerts();
                setInterval(loadPrices, 30000);
                setInterval(loadAlerts, 30000);
            </script>
        </body>
        </html>
        '''
        return render_template_string(html)
    
    def run(self):
        """Start dashboard server"""
        logger.info(f"Starting dashboard on http://localhost:{self.port}")
        self.app.run(host='0.0.0.0', port=self.port, debug=False)
