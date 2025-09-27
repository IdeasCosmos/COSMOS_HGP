#!/usr/bin/env python3
"""
Impact Calculator - Core Implementation
COSMOS-HGP Open Source Version
"""

import numpy as np
from typing import Any

class ImpactCalculator:
    """Calculate impact between before and after states"""
    
    @staticmethod
    def calculate(before: Any, after: Any, epsilon: float = 1e-12) -> float:
        """
        Calculate impact using the formula:
        impact = 0.5 * change_rate + 0.5 * scale_factor
        
        where:
        - change_rate = ||after - before|| / (||before|| + epsilon)
        - scale_factor = |tanh(||after|| / (||before|| + epsilon)) - 1|
        """
        try:
            # Convert to numpy arrays
            before_arr = np.array(before, dtype=float)
            after_arr = np.array(after, dtype=float)
            
            # Handle shape mismatch
            if before_arr.shape != after_arr.shape:
                return 0.5  # Default impact for shape mismatch
            
            # Calculate norms
            before_norm = np.linalg.norm(before_arr)
            after_norm = np.linalg.norm(after_arr)
            
            # Handle zero norm case
            if before_norm < epsilon:
                return 0.5 if after_norm > epsilon else 0.0
            
            # Calculate change rate
            change_rate = np.linalg.norm(after_arr - before_arr) / (before_norm + epsilon)
            
            # Calculate scale factor
            scale_ratio = after_norm / (before_norm + epsilon)
            scale_factor = abs(np.tanh(scale_ratio) - 1.0)
            
            # Combine into final impact
            impact = 0.5 * change_rate + 0.5 * scale_factor
            
            # Clamp to [0, 1] range
            return max(0.0, min(1.0, impact))
            
        except Exception:
            # Return default impact for any calculation errors
            return 0.1
    
    @staticmethod
    def normalize_input(data: Any) -> np.ndarray:
        """Normalize input data to handle edge cases"""
        try:
            if isinstance(data, (list, tuple)):
                data = np.array(data, dtype=float)
            elif not isinstance(data, np.ndarray):
                data = np.array([data], dtype=float)
            
            # Handle NaN and Inf values
            data = np.nan_to_num(data, nan=0.0, posinf=1e6, neginf=-1e6)
            
            return data
            
        except Exception:
            return np.array([0.0])
