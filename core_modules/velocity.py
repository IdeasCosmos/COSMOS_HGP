# cosmos_velocity.py - Core velocity policy and layer management
"""
COSMOS-HGP Velocity Policy Management System
Implements the cosmic escape velocity metaphor for cascade control
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional, Any
import numpy as np
import math
import logging
from datetime import datetime

# Configure logging for production use
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Layer(Enum):
    """Seven cosmic spheres with increasing escape velocity thresholds"""
    L1_QUANTUM = (1, "Quantum", 0.12)    # Subatomic fluctuations
    L2_ATOMIC = (2, "Atomic", 0.20)      # Atomic interactions
    L3_MOLECULAR = (3, "Molecular", 0.26) # Molecular bonds
    L4_COMPOUND = (4, "Compound", 0.30)   # Compound structures
    L5_ORGANIC = (5, "Organic", 0.33)     # Organic systems
    L6_ECOSYSTEM = (6, "Ecosystem", 0.35) # Ecosystem dynamics
    L7_COSMOS = (7, "Cosmos", 0.38)       # Cosmic harmony
    
    def __init__(self, level: int, name: str, threshold: float):
        self.level = level
        self.display_name = name
        self.threshold = threshold
    
    @classmethod
    def from_level(cls, level: int) -> 'Layer':
        """Get layer by numeric level"""
        for layer in cls:
            if layer.level == level:
                return layer
        raise ValueError(f"No layer found for level {level}")

@dataclass
class VelocityProfile:
    """Profile configuration for different operational modes"""
    name: str
    thresholds: Dict[Layer, float]
    cumulative_cap: float
    description: str
    
    @classmethod
    def standard(cls) -> 'VelocityProfile':
        """Standard balanced profile"""
        return cls(
            name="standard",
            thresholds={layer: layer.threshold for layer in Layer},
            cumulative_cap=0.50,
            description="Balanced approach for normal operations"
        )
    
    @classmethod
    def conservative(cls) -> 'VelocityProfile':
        """Conservative profile with lower thresholds"""
        return cls(
            name="conservative",
            thresholds={layer: layer.threshold * 0.8 for layer in Layer},
            cumulative_cap=0.45,
            description="Higher safety margins for critical operations"
        )
    
    @classmethod
    def aggressive(cls) -> 'VelocityProfile':
        """Aggressive profile with higher thresholds"""
        return cls(
            name="aggressive",
            thresholds={layer: min(layer.threshold * 1.2, 0.5) for layer in Layer},
            cumulative_cap=0.60,
            description="More permissive for development/testing"
        )

class VelocityPolicyManager:
    """
    Manages escape velocity thresholds across layers.
    Supports dynamic profile switching for different operational modes.
    """
    
    def __init__(self, profile: str = "standard"):
        """Initialize with specified profile"""
        self.profiles = {
            "standard": VelocityProfile.standard(),
            "conservative": VelocityProfile.conservative(),
            "aggressive": VelocityProfile.aggressive()
        }
        self.current_profile = self.profiles.get(profile, VelocityProfile.standard())
        self.breach_history = []  # Track breaches for analysis
        logger.info(f"Initialized VelocityPolicyManager with {profile} profile")
    
    def set_profile(self, profile_name: str) -> None:
        """Switch to a different velocity profile"""
        if profile_name not in self.profiles:
            raise ValueError(f"Unknown profile: {profile_name}")
        
        old_profile = self.current_profile.name
        self.current_profile = self.profiles[profile_name]
        logger.info(f"Switched velocity profile from {old_profile} to {profile_name}")
    
    def get_threshold(self, layer: Layer) -> float:
        """Get current threshold for a specific layer"""
        return self.current_profile.thresholds.get(layer, layer.threshold)
    
    def check_velocity_breach(self, layer: Layer, velocity: float) -> Tuple[bool, float]:
        """
        Check if velocity breaches the threshold for a given layer
        Returns: (is_breached, threshold_value)
        """
        # Handle edge cases
        if not isinstance(velocity, (int, float)):
            logger.error(f"Invalid velocity type: {type(velocity)}")
            return False, 0.0
        
        if math.isnan(velocity) or math.isinf(velocity):
            logger.warning(f"NaN or Inf velocity detected at {layer.display_name}")
            return True, 0.0  # Treat as breach for safety
        
        threshold = self.get_threshold(layer)
        is_breached = velocity > threshold
        
        if is_breached:
            breach_info = {
                "timestamp": datetime.now().isoformat(),
                "layer": layer.display_name,
                "velocity": velocity,
                "threshold": threshold,
                "excess": velocity - threshold
            }
            self.breach_history.append(breach_info)
            logger.warning(f"Velocity breach at {layer.display_name}: {velocity:.3f} > {threshold:.3f}")
        
        return is_breached, threshold
    
    def calculate_cumulative(self, velocity_list: List[float]) -> float:
        """
        Calculate cumulative impact using the cosmic formula:
        V_cumulative = 1 - ∏(1 - v_k) for all k impacts
        Capped at profile's cumulative_cap
        """
        if not velocity_list:
            return 0.0
        
        # Filter out invalid values
        valid_velocities = []
        for v in velocity_list:
            if isinstance(v, (int, float)) and not math.isnan(v) and not math.isinf(v):
                # Clamp individual velocities to [0, 1]
                valid_velocities.append(max(0.0, min(1.0, v)))
            else:
                logger.warning(f"Skipping invalid velocity in cumulative calculation: {v}")
        
        if not valid_velocities:
            return 0.0
        
        # Calculate cumulative using the product formula
        # V_cumulative = 1 - ∏(1 - v_k)
        product = 1.0
        for v in valid_velocities:
            product *= (1.0 - v)
        
        cumulative = 1.0 - product
        
        # Apply cap from current profile
        capped_cumulative = min(cumulative, self.current_profile.cumulative_cap)
        
        if cumulative > self.current_profile.cumulative_cap:
            logger.info(f"Cumulative velocity capped: {cumulative:.3f} → {capped_cumulative:.3f}")
        
        return capped_cumulative
    
    def calculate_impact(self, before: np.ndarray, after: np.ndarray) -> float:
        """
        Calculate impact between state transitions using the specified formula:
        impact = 0.5 * (change_rate) + 0.5 * |scale_factor - 1.0|
        """
        # Ensure numpy arrays
        before = np.asarray(before, dtype=np.float64)
        after = np.asarray(after, dtype=np.float64)
        
        # Handle edge cases
        before_norm = np.linalg.norm(before)
        after_norm = np.linalg.norm(after)
        
        if before_norm < 1e-12:  # Near-zero input
            if after_norm < 1e-12:
                return 0.0  # No change from zero to zero
            else:
                return 0.5  # Maximum impact for creation from nothing
        
        # Calculate change rate
        change_rate = np.linalg.norm(after - before) / before_norm
        
        # Calculate scale factor with numerical stability
        scale_factor = np.tanh(after_norm / before_norm)
        
        # Combine into final impact
        impact = 0.5 * change_rate + 0.5 * abs(scale_factor - 1.0)
        
        # Ensure impact is in valid range [0, 1]
        impact = max(0.0, min(1.0, impact))
        
        return impact
    
    def get_layer_transition_probability(self, from_layer: Layer, to_layer: Layer) -> float:
        """
        Get probability of impact propagating between layers
        Based on the transition matrix in specifications
        """
        # Only allow propagation to the next layer
        if to_layer.level != from_layer.level + 1:
            return 0.0
        
        # Transition probabilities decrease as we go up
        transition_probs = {
            1: 0.8,  # L1 → L2
            2: 0.7,  # L2 → L3
            3: 0.6,  # L3 → L4
            4: 0.5,  # L4 → L5
            5: 0.4,  # L5 → L6
            6: 0.3,  # L6 → L7
            7: 0.0,  # L7 is terminal
        }
        
        return transition_probs.get(from_layer.level, 0.0)
    
    def calculate_cascade_probability(self, impact: float, lambda_param: float = 2.0, 
                                     alpha: float = 2.5) -> float:
        """
        Calculate cascade probability using the mathematical model:
        P(cascade|impact) = 1 - exp(-λ * impact^α)
        """
        if impact <= 0:
            return 0.0
        
        probability = 1 - math.exp(-lambda_param * (impact ** alpha))
        return max(0.0, min(1.0, probability))  # Clamp to [0, 1]
    
    def get_breach_statistics(self) -> Dict[str, Any]:
        """Get statistics about velocity breaches"""
        if not self.breach_history:
            return {
                "total_breaches": 0,
                "breaches_by_layer": {},
                "average_excess": 0.0,
                "max_velocity": 0.0
            }
        
        breaches_by_layer = {}
        total_excess = 0.0
        max_velocity = 0.0
        
        for breach in self.breach_history:
            layer = breach["layer"]
            breaches_by_layer[layer] = breaches_by_layer.get(layer, 0) + 1
            total_excess += breach["excess"]
            max_velocity = max(max_velocity, breach["velocity"])
        
        return {
            "total_breaches": len(self.breach_history),
            "breaches_by_layer": breaches_by_layer,
            "average_excess": total_excess / len(self.breach_history),
            "max_velocity": max_velocity,
            "recent_breaches": self.breach_history[-10:]  # Last 10 breaches
        }
    
    def reset_breach_history(self) -> None:
        """Clear breach history"""
        self.breach_history = []
        logger.info("Breach history cleared")

class AdaptiveThresholdManager:
    """
    Learn optimal thresholds from execution history
    Uses exponential moving average of successful executions
    """
    
    def __init__(self, alpha: float = 0.1):
        """
        Initialize adaptive threshold manager
        alpha: Learning rate for exponential moving average
        """
        self.alpha = alpha
        self.threshold_history = {layer: [] for layer in Layer}
        self.current_thresholds = {layer: layer.threshold for layer in Layer}
        logger.info(f"Initialized AdaptiveThresholdManager with α={alpha}")
    
    def update_threshold(self, layer: Layer, impact_history: List[float], 
                        target_block_rate: float = 0.05) -> float:
        """
        Update threshold for a layer based on impact history
        Aims to block exactly target_block_rate of impacts
        """
        if not impact_history:
            return self.current_thresholds[layer]
        
        # Store history
        self.threshold_history[layer].extend(impact_history)
        
        # Use only recent history (last 1000 samples)
        recent_history = self.threshold_history[layer][-1000:]
        
        if len(recent_history) < 20:  # Need minimum samples
            return self.current_thresholds[layer]
        
        # Calculate optimal threshold (95th percentile by default)
        sorted_impacts = np.sort(recent_history)
        percentile_idx = int(len(sorted_impacts) * (1 - target_block_rate))
        optimal_threshold = sorted_impacts[percentile_idx] * 1.1  # 10% safety margin
        
        # Apply exponential moving average
        old_threshold = self.current_thresholds[layer]
        new_threshold = (1 - self.alpha) * old_threshold + self.alpha * optimal_threshold
        
        # Ensure threshold stays within reasonable bounds
        min_threshold = layer.threshold * 0.5
        max_threshold = layer.threshold * 1.5
        new_threshold = max(min_threshold, min(max_threshold, new_threshold))
        
        self.current_thresholds[layer] = new_threshold
        
        logger.info(f"Updated {layer.display_name} threshold: {old_threshold:.3f} → {new_threshold:.3f}")
        
        return new_threshold
    
    def get_threshold(self, layer: Layer) -> float:
        """Get current adaptive threshold for a layer"""
        return self.current_thresholds.get(layer, layer.threshold)
    
    def get_learning_statistics(self) -> Dict[str, Any]:
        """Get statistics about threshold learning"""
        stats = {}
        for layer in Layer:
            history = self.threshold_history[layer]
            if history:
                stats[layer.display_name] = {
                    "samples": len(history),
                    "current_threshold": self.current_thresholds[layer],
                    "default_threshold": layer.threshold,
                    "mean_impact": np.mean(history),
                    "std_impact": np.std(history),
                    "adaptation_ratio": self.current_thresholds[layer] / layer.threshold
                }
        return stats