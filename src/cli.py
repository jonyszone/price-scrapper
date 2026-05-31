"""CLI tool for price scraper management"""

import click
import os
from src.database import Database
from src.alerts import AlertManager, PriceComparator
from src.dashboard import Dashboard
from src.notifications import EmailNotifier
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@click.group()
def cli():
    """Price Scraper CLI Tool"""
    pass


@cli.command()
@click.option('--site', prompt='Site name', help='Website name')
@click.option('--product', prompt='Product name', help='Product name')
@click.option('--price', prompt='Target price', type=float, help='Target price for alert')
def create_alert(site, product, price):
    """Create a price alert"""
    db = Database()
    alert_manager = AlertManager(db)
    alert = alert_manager.create_alert(site, product, price)
    click.echo(f"✓ Alert created (ID: {alert.id}) for {product} at ${price}")


@cli.command()
def list_alerts():
    """List all active alerts"""
    db = Database()
    alerts = db.get_active_alerts()
    
    if not alerts:
        click.echo("No active alerts")
        return
    
    click.echo("\n📋 Active Alerts:")
    click.echo("-" * 80)
    for alert in alerts:
        latest = db.get_latest_price(alert.site_name, alert.product_name)
        current_price = latest.price if latest else "N/A"
        status = "🔔 Triggered" if alert.triggered_at else "⏳ Waiting"
        click.echo(f"ID: {alert.id} | {alert.product_name} | Target: ${alert.target_price} | Current: ${current_price} | {status}")


@cli.command()
@click.option('--alert-id', prompt='Alert ID', type=int, help='Alert ID to delete')
def delete_alert(alert_id):
    """Delete an alert"""
    db = Database()
    session = db.Session()
    try:
        from src.database import PriceAlert
        alert = session.query(PriceAlert).filter(PriceAlert.id == alert_id).first()
        if alert:
            session.delete(alert)
            session.commit()
            click.echo(f"✓ Alert {alert_id} deleted")
        else:
            click.echo(f"✗ Alert {alert_id} not found")
    finally:
        session.close()


@cli.command()
@click.option('--site', prompt='Site name', help='Website name')
@click.option('--product', prompt='Product name', help='Product name')
@click.option('--days', default=30, help='Number of days to analyze')
def stats(site, product, days):
    """Get price statistics"""
    db = Database()
    comparator = PriceComparator(db)
    
    lowest = comparator.get_lowest_price(site, product, days)
    highest = comparator.get_highest_price(site, product, days)
    average = comparator.get_average_price(site, product, days)
    change = comparator.get_price_change(site, product)
    
    click.echo(f"\n📊 Price Statistics for {product} ({days} days):")
    click.echo("-" * 50)
    click.echo(f"Lowest:  ${lowest}" if lowest else "Lowest:  N/A")
    click.echo(f"Highest: ${highest}" if highest else "Highest: N/A")
    click.echo(f"Average: ${average}" if average else "Average: N/A")
    
    if change:
        direction = "📈" if change['is_increase'] else "📉"
        click.echo(f"Change:  {direction} {change['change_percent']}% (${change['previous']} → ${change['current']})")


@cli.command()
@click.option('--email', prompt='Recipient email', help='Email address')
def send_test_email(email):
    """Send test email"""
    try:
        notifier = EmailNotifier()
        notifier.send_alert(
            email,
            "Test Product",
            100.00,
            79.99,
            "Test Site"
        )
        click.echo(f"✓ Test email sent to {email}")
    except Exception as e:
        click.echo(f"✗ Failed to send email: {e}")


@cli.command()
@click.option('--port', default=5000, help='Dashboard port')
def dashboard(port):
    """Start web dashboard"""
    db = Database()
    dash = Dashboard(db, port=port)
    click.echo(f"🚀 Starting dashboard on http://localhost:{port}")
    dash.run()


@cli.command()
def check_alerts():
    """Check all alerts and trigger notifications"""
    db = Database()
    alert_manager = AlertManager(db)
    triggered = alert_manager.check_alerts()
    
    if triggered:
        click.echo(f"\n🔔 {len(triggered)} alert(s) triggered:")
        for alert in triggered:
            click.echo(f"  • {alert['product']}: ${alert['current_price']} (save ${alert['savings']})")
    else:
        click.echo("No alerts triggered")


@cli.command()
def export_data():
    """Export price history to CSV"""
    import csv
    from datetime import datetime
    
    db = Database()
    session = db.Session()
    try:
        from src.database import PriceHistory
        
        filename = f"price_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Site', 'Product', 'Price', 'Currency', 'Date', 'Available'])
            
            for record in session.query(PriceHistory).all():
                writer.writerow([
                    record.site_name,
                    record.product_name,
                    record.price,
                    record.currency,
                    record.scraped_at,
                    record.is_available
                ])
        
        click.echo(f"✓ Data exported to {filename}")
    finally:
        session.close()


@cli.command()
def status():
    """Show system status"""
    db = Database()
    session = db.Session()
    try:
        from src.database import PriceHistory, PriceAlert
        
        total_prices = session.query(PriceHistory).count()
        total_alerts = session.query(PriceAlert).count()
        active_alerts = session.query(PriceAlert).filter(PriceAlert.is_active == True).count()
        
        click.echo("\n📊 System Status:")
        click.echo("-" * 50)
        click.echo(f"Total Price Records: {total_prices}")
        click.echo(f"Total Alerts: {total_alerts}")
        click.echo(f"Active Alerts: {active_alerts}")
    finally:
        session.close()


if __name__ == '__main__':
    cli()
