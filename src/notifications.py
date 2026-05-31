"""Email notifications for price drops"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging

logger = logging.getLogger(__name__)


class EmailNotifier:
    """Send email notifications for price alerts"""
    
    def __init__(self, smtp_server=None, smtp_port=None, sender_email=None, sender_password=None):
        self.smtp_server = smtp_server or os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = smtp_port or int(os.getenv('SMTP_PORT', 587))
        self.sender_email = sender_email or os.getenv('SENDER_EMAIL')
        self.sender_password = sender_password or os.getenv('SENDER_PASSWORD')
    
    def send_alert(self, recipient_email, product_name, target_price, current_price, site_name):
        """Send price drop alert email"""
        try:
            subject = f"🔔 Price Alert: {product_name}"
            
            savings = target_price - current_price
            savings_percent = (savings / target_price) * 100
            
            body = f"""
            <html>
                <body style="font-family: Arial, sans-serif;">
                    <h2>Price Drop Alert!</h2>
                    <p>Great news! The price of <strong>{product_name}</strong> has dropped below your target price.</p>
                    
                    <table style="border-collapse: collapse; margin: 20px 0;">
                        <tr style="background: #f0f0f0;">
                            <td style="padding: 10px; border: 1px solid #ddd;"><strong>Product</strong></td>
                            <td style="padding: 10px; border: 1px solid #ddd;">{product_name}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border: 1px solid #ddd;"><strong>Site</strong></td>
                            <td style="padding: 10px; border: 1px solid #ddd;">{site_name}</td>
                        </tr>
                        <tr style="background: #f0f0f0;">
                            <td style="padding: 10px; border: 1px solid #ddd;"><strong>Target Price</strong></td>
                            <td style="padding: 10px; border: 1px solid #ddd;">${target_price:.2f}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border: 1px solid #ddd;"><strong>Current Price</strong></td>
                            <td style="padding: 10px; border: 1px solid #ddd; color: green; font-weight: bold;">${current_price:.2f}</td>
                        </tr>
                        <tr style="background: #e8f5e9;">
                            <td style="padding: 10px; border: 1px solid #ddd;"><strong>You Save</strong></td>
                            <td style="padding: 10px; border: 1px solid #ddd; color: green; font-weight: bold;">${savings:.2f} ({savings_percent:.1f}%)</td>
                        </tr>
                    </table>
                    
                    <p>Don't miss out! Check the product now.</p>
                    <p style="color: #666; font-size: 12px;">This is an automated message from Price Scraper.</p>
                </body>
            </html>
            """
            
            self._send_email(recipient_email, subject, body)
            logger.info(f"Alert email sent to {recipient_email}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to send alert email: {e}")
            return False
    
    def send_daily_summary(self, recipient_email, price_changes):
        """Send daily price summary email"""
        try:
            subject = "📊 Daily Price Summary"
            
            rows = ""
            for change in price_changes:
                direction = "📈" if change['is_increase'] else "📉"
                rows += f"""
                <tr>
                    <td style="padding: 10px; border: 1px solid #ddd;">{change['product']}</td>
                    <td style="padding: 10px; border: 1px solid #ddd;">${change['previous']:.2f}</td>
                    <td style="padding: 10px; border: 1px solid #ddd;">${change['current']:.2f}</td>
                    <td style="padding: 10px; border: 1px solid #ddd;">{direction} {change['change_percent']}%</td>
                </tr>
                """
            
            body = f"""
            <html>
                <body style="font-family: Arial, sans-serif;">
                    <h2>Daily Price Summary</h2>
                    <p>Here's a summary of price changes today:</p>
                    
                    <table style="border-collapse: collapse; width: 100%;">
                        <tr style="background: #4CAF50; color: white;">
                            <th style="padding: 10px; border: 1px solid #ddd;">Product</th>
                            <th style="padding: 10px; border: 1px solid #ddd;">Previous</th>
                            <th style="padding: 10px; border: 1px solid #ddd;">Current</th>
                            <th style="padding: 10px; border: 1px solid #ddd;">Change</th>
                        </tr>
                        {rows}
                    </table>
                    
                    <p style="color: #666; font-size: 12px; margin-top: 20px;">This is an automated message from Price Scraper.</p>
                </body>
            </html>
            """
            
            self._send_email(recipient_email, subject, body)
            logger.info(f"Summary email sent to {recipient_email}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to send summary email: {e}")
            return False
    
    def _send_email(self, recipient_email, subject, body):
        """Send email via SMTP"""
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = self.sender_email
        message["To"] = recipient_email
        
        part = MIMEText(body, "html")
        message.attach(part)
        
        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.sendmail(self.sender_email, recipient_email, message.as_string())
