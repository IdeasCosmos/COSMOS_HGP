#!/usr/bin/env python3
"""
COSMOS Basic Usage Example
Demonstrates basic API interactions with the COSMOS visualization system.
"""

import requests
import json
import time
from typing import Dict, List, Any

class COSMOSClient:
    """Basic client for interacting with COSMOS API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get real-time system metrics"""
        try:
            response = self.session.get(f"{self.base_url}/metrics/live")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error getting metrics: {e}")
            return {}
    
    def get_events(self, limit: int = 50, after: int = 0) -> Dict[str, Any]:
        """Get events with pagination"""
        try:
            response = self.session.get(
                f"{self.base_url}/events",
                params={"limit": limit, "after": after}
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error getting events: {e}")
            return {"events": [], "next": 0, "total": 0}
    
    def get_event_stats(self) -> Dict[str, Any]:
        """Get event statistics"""
        try:
            response = self.session.get(f"{self.base_url}/events/stats")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error getting event stats: {e}")
            return {}
    
    def get_visualization_files(self) -> List[Dict[str, Any]]:
        """Get list of available visualization files"""
        try:
            response = self.session.get(f"{self.base_url}/viz")
            response.raise_for_status()
            return response.json().get("files", [])
        except requests.RequestException as e:
            print(f"Error getting visualization files: {e}")
            return []
    
    def generate_visualizations(self) -> bool:
        """Trigger visualization generation"""
        try:
            response = self.session.post(f"{self.base_url}/generate")
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            print(f"Error generating visualizations: {e}")
            return False

def main():
    """Main example function"""
    print("🌌 COSMOS Basic Usage Example")
    print("=" * 40)
    
    # Initialize client
    client = COSMOSClient()
    
    # Check if server is running
    print("🔍 Checking server status...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print("❌ Server is not responding properly")
            return
    except requests.RequestException:
        print("❌ Server is not running. Please start the server first:")
        print("   python main_viz.py")
        return
    
    # Get real-time metrics
    print("\n📊 Getting real-time metrics...")
    metrics = client.get_metrics()
    if metrics:
        print(f"  P95 Latency: {metrics.get('p95_ms', 0)}ms")
        print(f"  Block Events: {metrics.get('blocks', 0)}")
        print(f"  Cap Events: {metrics.get('caps', 0)}")
        print(f"  Running Groups: {metrics.get('running_groups', 0)}")
        print(f"  Total Events: {metrics.get('total_events', 0)}")
    
    # Get recent events
    print("\n📋 Getting recent events...")
    events_data = client.get_events(limit=10)
    events = events_data.get("events", [])
    print(f"  Found {len(events)} recent events")
    
    if events:
        print("  Sample events:")
        for i, event in enumerate(events[:3]):
            print(f"    {i+1}. {event.get('kind', 'unknown')} - Layer {event.get('layer', 0)} - Impact {event.get('impact', 0)}")
    
    # Get event statistics
    print("\n📈 Getting event statistics...")
    stats = client.get_event_stats()
    if stats and "by_kind" in stats:
        print("  Event distribution:")
        for kind, count in stats["by_kind"].items():
            print(f"    {kind}: {count}")
    
    if stats and "by_layer" in stats:
        print("  Layer distribution:")
        for layer, count in stats["by_layer"].items():
            print(f"    L{layer}: {count}")
    
    # Get visualization files
    print("\n🖼️ Getting visualization files...")
    viz_files = client.get_visualization_files()
    print(f"  Found {len(viz_files)} visualization files")
    
    for file_info in viz_files[:5]:  # Show first 5 files
        print(f"    {file_info['name']} ({file_info['size']} bytes)")
    
    # Generate new visualizations
    print("\n🔄 Generating new visualizations...")
    if client.generate_visualizations():
        print("  ✅ Visualizations generated successfully")
    else:
        print("  ❌ Failed to generate visualizations")
    
    print("\n🎉 Example completed!")
    print("\n💡 Next steps:")
    print("  - Open http://localhost:8000 for the dashboard")
    print("  - Check the examples/ folder for more advanced usage")
    print("  - Read the API documentation at http://localhost:8000/docs")

if __name__ == "__main__":
    main()
