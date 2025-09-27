#!/usr/bin/env python3
"""
Inequality Filter - Core Implementation
COSMOS-HGP Open Source Version
"""

class InequalityFilter:
    """Single inequality filter for local blocking"""
    
    def __init__(self, threshold: float = 0.30):
        self.threshold = threshold
    
    def should_block(self, impact: float) -> bool:
        """Check if impact exceeds threshold (should block)"""
        return impact >= self.threshold
    
    def get_block_reason(self, impact: float) -> str:
        """Get human-readable block reason"""
        if impact >= self.threshold:
            return f"impact={impact:.3f} >= threshold={self.threshold:.3f}"
        else:
            return f"impact={impact:.3f} < threshold={self.threshold:.3f} (allowed)"
    
    def get_impact_ratio(self, impact: float) -> float:
        """Get ratio of impact to threshold"""
        if self.threshold <= 0:
            return 0.0
        return impact / self.threshold
    
    def update_threshold(self, new_threshold: float):
        """Update the threshold value"""
        self.threshold = new_threshold
    
    def get_threshold(self) -> float:
        """Get current threshold value"""
        return self.threshold
