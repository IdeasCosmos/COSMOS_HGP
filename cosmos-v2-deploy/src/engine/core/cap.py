#!/usr/bin/env python3
"""
Cumulative Capping - Core Implementation
COSMOS-HGP Open Source Version
"""

class CumulativeCapper:
    """Calculate and manage cumulative velocity capping"""
    
    @staticmethod
    def update(current_cumulative: float, new_impact: float) -> float:
        """
        Update cumulative velocity using the formula:
        V = 1 - ∏(1 - v_k)
        
        where v_k is the impact of the k-th rule
        """
        # Ensure impact is in [0, 1] range
        new_impact = max(0.0, min(1.0, new_impact))
        
        # Update cumulative: V_new = 1 - (1 - V_old) * (1 - v_new)
        new_cumulative = 1.0 - (1.0 - current_cumulative) * (1.0 - new_impact)
        
        return new_cumulative
    
    @staticmethod
    def check_cap_reached(cumulative: float, cap: float) -> bool:
        """Check if cumulative velocity has reached the cap"""
        return cumulative >= cap
    
    @staticmethod
    def calculate_cap_ratio(cumulative: float, cap: float) -> float:
        """Calculate the ratio of cumulative to cap (0.0 to 1.0+)"""
        if cap <= 0:
            return 0.0
        return cumulative / cap
    
    @staticmethod
    def get_cap_status(cumulative: float, cap: float) -> str:
        """Get human-readable cap status"""
        ratio = CumulativeCapper.calculate_cap_ratio(cumulative, cap)
        
        if ratio >= 1.0:
            return "CAP_REACHED"
        elif ratio >= 0.8:
            return "APPROACHING_CAP"
        elif ratio >= 0.5:
            return "MODERATE"
        else:
            return "LOW"
