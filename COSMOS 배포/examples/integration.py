#!/usr/bin/env python3
"""
COSMOS System Integration Example
Demonstrates how to integrate COSMOS with external systems and monitoring tools.
"""

import requests
import json
import time
import threading
import logging
from datetime import datetime
from typing import Dict, List, Any, Callable
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class COSMOSMonitor:
    """Monitor for COSMOS system with alerting capabilities"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.alert_callbacks = []
        self.monitoring = False
        self.monitor_thread = None
        
        # Thresholds for alerting
        self.thresholds = {
            "p95_latency": 100.0,  # ms
            "block_events": 50,    # per minute
            "error_rate": 0.1,     # 10%
            "memory_usage": 0.8    # 80%
        }
    
    def add_alert_callback(self, callback: Callable[[str, Dict], None]):
        """Add an alert callback function"""
        self.alert_callbacks.append(callback)
    
    def check_health(self) -> Dict[str, Any]:
        """Check system health"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        try:
            response = self.session.get(f"{self.base_url}/metrics/live", timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to get metrics: {e}")
            return {}
    
    def get_event_stats(self) -> Dict[str, Any]:
        """Get event statistics"""
        try:
            response = self.session.get(f"{self.base_url}/events/stats", timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to get event stats: {e}")
            return {}
    
    def check_thresholds(self, metrics: Dict[str, Any], stats: Dict[str, Any]) -> List[str]:
        """Check if any thresholds are exceeded"""
        alerts = []
        
        # Check P95 latency
        p95_latency = metrics.get("p95_ms", 0)
        if p95_latency > self.thresholds["p95_latency"]:
            alerts.append(f"High P95 latency: {p95_latency}ms (threshold: {self.thresholds['p95_latency']}ms)")
        
        # Check block events
        blocks = metrics.get("blocks", 0)
        if blocks > self.thresholds["block_events"]:
            alerts.append(f"High block events: {blocks} (threshold: {self.thresholds['block_events']})")
        
        # Check error rate
        if "by_kind" in stats:
            total_events = stats.get("total_events", 0)
            error_events = stats["by_kind"].get("error", 0)
            if total_events > 0:
                error_rate = error_events / total_events
                if error_rate > self.thresholds["error_rate"]:
                    alerts.append(f"High error rate: {error_rate:.2%} (threshold: {self.thresholds['error_rate']:.2%})")
        
        return alerts
    
    def trigger_alerts(self, alerts: List[str], metrics: Dict[str, Any]):
        """Trigger alert callbacks"""
        for alert in alerts:
            logger.warning(f"ALERT: {alert}")
            for callback in self.alert_callbacks:
                try:
                    callback(alert, metrics)
                except Exception as e:
                    logger.error(f"Alert callback failed: {e}")
    
    def monitor_loop(self):
        """Main monitoring loop"""
        logger.info("Starting COSMOS monitoring...")
        
        while self.monitoring:
            try:
                # Get current metrics and stats
                metrics = self.get_metrics()
                stats = self.get_event_stats()
                
                # Check thresholds
                alerts = self.check_thresholds(metrics, stats)
                
                # Trigger alerts if any
                if alerts:
                    self.trigger_alerts(alerts, metrics)
                else:
                    logger.info("System healthy - no alerts")
                
                # Log current status
                logger.info(f"Metrics: P95={metrics.get('p95_ms', 0)}ms, "
                          f"Blocks={metrics.get('blocks', 0)}, "
                          f"Total Events={metrics.get('total_events', 0)}")
                
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
            
            # Wait before next check
            time.sleep(30)  # Check every 30 seconds
    
    def start_monitoring(self):
        """Start monitoring in background thread"""
        if self.monitoring:
            logger.warning("Monitoring already started")
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("Monitoring started")
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("Monitoring stopped")

class EmailNotifier:
    """Email notification system"""
    
    def __init__(self, smtp_server: str, smtp_port: int, username: str, password: str, to_email: str):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.to_email = to_email
    
    def send_alert(self, alert: str, metrics: Dict[str, Any]):
        """Send email alert"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.username
            msg['To'] = self.to_email
            msg['Subject'] = f"COSMOS Alert: {alert}"
            
            body = f"""
COSMOS System Alert

Alert: {alert}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Current Metrics:
- P95 Latency: {metrics.get('p95_ms', 0)}ms
- Block Events: {metrics.get('blocks', 0)}
- Cap Events: {metrics.get('caps', 0)}
- Running Groups: {metrics.get('running_groups', 0)}
- Total Events: {metrics.get('total_events', 0)}

Please check the COSMOS dashboard for more details.
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            text = msg.as_string()
            server.sendmail(self.username, self.to_email, text)
            server.quit()
            
            logger.info(f"Email alert sent: {alert}")
            
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")

class SlackNotifier:
    """Slack notification system"""
    
    def __init__(self, webhook_url: str, channel: str = "#alerts"):
        self.webhook_url = webhook_url
        self.channel = channel
    
    def send_alert(self, alert: str, metrics: Dict[str, Any]):
        """Send Slack alert"""
        try:
            payload = {
                "channel": self.channel,
                "username": "COSMOS Monitor",
                "icon_emoji": ":warning:",
                "text": f"🚨 COSMOS Alert: {alert}",
                "attachments": [
                    {
                        "color": "danger",
                        "fields": [
                            {"title": "P95 Latency", "value": f"{metrics.get('p95_ms', 0)}ms", "short": True},
                            {"title": "Block Events", "value": str(metrics.get('blocks', 0)), "short": True},
                            {"title": "Total Events", "value": str(metrics.get('total_events', 0)), "short": True},
                            {"title": "Time", "value": datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "short": True}
                        ]
                    }
                ]
            }
            
            response = requests.post(self.webhook_url, json=payload)
            response.raise_for_status()
            
            logger.info(f"Slack alert sent: {alert}")
            
        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}")

def file_logger(alert: str, metrics: Dict[str, Any]):
    """Simple file logger for alerts"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"{timestamp} - ALERT: {alert} - Metrics: {metrics}\n"
    
    with open("cosmos_alerts.log", "a") as f:
        f.write(log_entry)
    
    logger.info(f"Alert logged to file: {alert}")

def main():
    """Main integration example"""
    print("🔗 COSMOS System Integration Example")
    print("=" * 40)
    
    # Initialize monitor
    monitor = COSMOSMonitor()
    
    # Add alert callbacks
    monitor.add_alert_callback(file_logger)
    
    # Example: Add email notifier (uncomment and configure)
    # email_notifier = EmailNotifier(
    #     smtp_server="smtp.gmail.com",
    #     smtp_port=587,
    #     username="your-email@gmail.com",
    #     password="your-password",
    #     to_email="admin@yourcompany.com"
    # )
    # monitor.add_alert_callback(email_notifier.send_alert)
    
    # Example: Add Slack notifier (uncomment and configure)
    # slack_notifier = SlackNotifier(
    #     webhook_url="https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK",
    #     channel="#alerts"
    # )
    # monitor.add_alert_callback(slack_notifier.send_alert)
    
    # Check if server is running
    health = monitor.check_health()
    if health.get("status") != "healthy":
        print("❌ COSMOS server is not running. Please start it first:")
        print("   python main_viz.py")
        return
    
    print("✅ COSMOS server is running")
    
    # Start monitoring
    print("\n🔍 Starting monitoring...")
    monitor.start_monitoring()
    
    try:
        print("Monitoring active. Press Ctrl+C to stop...")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping monitoring...")
        monitor.stop_monitoring()
    
    print("🎉 Integration example completed!")
    print("\n📁 Generated files:")
    print("  - cosmos_alerts.log (alert log)")
    print("\n💡 Next steps:")
    print("  - Configure email/Slack notifications")
    print("  - Adjust alert thresholds")
    print("  - Integrate with your monitoring stack")

if __name__ == "__main__":
    main()
