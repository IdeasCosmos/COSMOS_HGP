#!/usr/bin/env python3
"""
COSMOS Custom Analysis Example
Demonstrates advanced analysis techniques and custom visualization.
"""

import requests
import json
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import pandas as pd

class COSMOSAnalyzer:
    """Advanced analyzer for COSMOS data"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def get_all_events(self) -> List[Dict[str, Any]]:
        """Get all events from the system"""
        all_events = []
        after = 0
        limit = 200
        
        while True:
            try:
                response = self.session.get(
                    f"{self.base_url}/events",
                    params={"limit": limit, "after": after}
                )
                response.raise_for_status()
                data = response.json()
                events = data.get("events", [])
                
                if not events:
                    break
                
                all_events.extend(events)
                after = data.get("next", after + len(events))
                
                if len(events) < limit:
                    break
                    
            except requests.RequestException as e:
                print(f"Error fetching events: {e}")
                break
        
        return all_events
    
    def analyze_temporal_patterns(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze temporal patterns in events"""
        if not events:
            return {}
        
        # Convert timestamps to datetime
        timestamps = []
        for event in events:
            ts = event.get("ts", 0)
            if ts > 0:
                timestamps.append(datetime.fromtimestamp(ts / 1000))
        
        if not timestamps:
            return {}
        
        timestamps.sort()
        
        # Calculate time intervals
        intervals = []
        for i in range(1, len(timestamps)):
            interval = (timestamps[i] - timestamps[i-1]).total_seconds()
            intervals.append(interval)
        
        analysis = {
            "total_events": len(events),
            "time_span": (timestamps[-1] - timestamps[0]).total_seconds(),
            "avg_interval": np.mean(intervals) if intervals else 0,
            "median_interval": np.median(intervals) if intervals else 0,
            "min_interval": np.min(intervals) if intervals else 0,
            "max_interval": np.max(intervals) if intervals else 0,
            "events_per_second": len(events) / ((timestamps[-1] - timestamps[0]).total_seconds()) if len(timestamps) > 1 else 0
        }
        
        return analysis
    
    def analyze_layer_correlation(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze correlation between layers and event types"""
        if not events:
            return {}
        
        # Create correlation matrix
        layer_kind_matrix = {}
        
        for event in events:
            layer = event.get("layer", 0)
            kind = event.get("kind", "unknown")
            
            if layer not in layer_kind_matrix:
                layer_kind_matrix[layer] = {}
            
            layer_kind_matrix[layer][kind] = layer_kind_matrix[layer].get(kind, 0) + 1
        
        # Calculate correlations
        correlations = {}
        for layer, kinds in layer_kind_matrix.items():
            total_events = sum(kinds.values())
            correlations[layer] = {
                "total_events": total_events,
                "kind_distribution": kinds,
                "most_common_kind": max(kinds.items(), key=lambda x: x[1])[0] if kinds else None
            }
        
        return correlations
    
    def analyze_impact_distribution(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze impact value distribution"""
        if not events:
            return {}
        
        impacts = [event.get("impact", 0) for event in events if event.get("impact") is not None]
        
        if not impacts:
            return {}
        
        analysis = {
            "count": len(impacts),
            "mean": np.mean(impacts),
            "median": np.median(impacts),
            "std": np.std(impacts),
            "min": np.min(impacts),
            "max": np.max(impacts),
            "q25": np.percentile(impacts, 25),
            "q75": np.percentile(impacts, 75),
            "high_impact_events": len([i for i in impacts if i > 0.7]),
            "low_impact_events": len([i for i in impacts if i < 0.3])
        }
        
        return analysis
    
    def create_custom_visualization(self, events: List[Dict[str, Any]], output_path: str = "custom_analysis.png"):
        """Create custom visualization"""
        if not events:
            print("No events to visualize")
            return
        
        # Prepare data
        layers = [event.get("layer", 0) for event in events]
        impacts = [event.get("impact", 0) for event in events if event.get("impact") is not None]
        kinds = [event.get("kind", "unknown") for event in events]
        
        # Create figure with subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('COSMOS Custom Analysis', fontsize=16)
        
        # 1. Layer distribution
        layer_counts = {}
        for layer in layers:
            layer_counts[layer] = layer_counts.get(layer, 0) + 1
        
        ax1.bar(layer_counts.keys(), layer_counts.values())
        ax1.set_title('Event Distribution by Layer')
        ax1.set_xlabel('Layer')
        ax1.set_ylabel('Event Count')
        
        # 2. Impact distribution
        if impacts:
            ax2.hist(impacts, bins=20, alpha=0.7, edgecolor='black')
            ax2.set_title('Impact Value Distribution')
            ax2.set_xlabel('Impact Value')
            ax2.set_ylabel('Frequency')
        
        # 3. Event type distribution
        kind_counts = {}
        for kind in kinds:
            kind_counts[kind] = kind_counts.get(kind, 0) + 1
        
        ax3.pie(kind_counts.values(), labels=kind_counts.keys(), autopct='%1.1f%%')
        ax3.set_title('Event Type Distribution')
        
        # 4. Layer vs Impact scatter
        layer_impact_data = [(event.get("layer", 0), event.get("impact", 0)) 
                           for event in events if event.get("impact") is not None]
        
        if layer_impact_data:
            layers_scatter, impacts_scatter = zip(*layer_impact_data)
            ax4.scatter(layers_scatter, impacts_scatter, alpha=0.6)
            ax4.set_title('Layer vs Impact Correlation')
            ax4.set_xlabel('Layer')
            ax4.set_ylabel('Impact Value')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Custom visualization saved to {output_path}")

def main():
    """Main analysis function"""
    print("🔬 COSMOS Custom Analysis Example")
    print("=" * 40)
    
    # Initialize analyzer
    analyzer = COSMOSAnalyzer()
    
    # Check server status
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code != 200:
            print("❌ Server is not running. Please start the server first:")
            print("   python main_viz.py")
            return
    except requests.RequestException:
        print("❌ Server is not running. Please start the server first:")
        print("   python main_viz.py")
        return
    
    print("✅ Server is running")
    
    # Get all events
    print("\n📊 Fetching all events...")
    events = analyzer.get_all_events()
    print(f"  Found {len(events)} events")
    
    if not events:
        print("  No events found. Generate some test data first:")
        print("  python generate_test_data.py")
        return
    
    # Analyze temporal patterns
    print("\n⏰ Analyzing temporal patterns...")
    temporal_analysis = analyzer.analyze_temporal_patterns(events)
    if temporal_analysis:
        print(f"  Time span: {temporal_analysis['time_span']:.2f} seconds")
        print(f"  Events per second: {temporal_analysis['events_per_second']:.2f}")
        print(f"  Average interval: {temporal_analysis['avg_interval']:.2f} seconds")
    
    # Analyze layer correlation
    print("\n🔗 Analyzing layer correlations...")
    layer_analysis = analyzer.analyze_layer_correlation(events)
    for layer, data in layer_analysis.items():
        print(f"  L{layer}: {data['total_events']} events, most common: {data['most_common_kind']}")
    
    # Analyze impact distribution
    print("\n📈 Analyzing impact distribution...")
    impact_analysis = analyzer.analyze_impact_distribution(events)
    if impact_analysis:
        print(f"  Mean impact: {impact_analysis['mean']:.3f}")
        print(f"  High impact events (>0.7): {impact_analysis['high_impact_events']}")
        print(f"  Low impact events (<0.3): {impact_analysis['low_impact_events']}")
    
    # Create custom visualization
    print("\n🎨 Creating custom visualization...")
    analyzer.create_custom_visualization(events, "custom_analysis.png")
    
    print("\n🎉 Analysis completed!")
    print("\n📁 Generated files:")
    print("  - custom_analysis.png (custom visualization)")
    print("\n💡 Next steps:")
    print("  - View the custom visualization")
    print("  - Modify the analysis parameters")
    print("  - Integrate with your own data sources")

if __name__ == "__main__":
    main()
