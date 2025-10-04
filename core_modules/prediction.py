"""
COSMOS-HGP Cascade Prediction System (PRO)
ML 기반 cascade 예측 차단
"""

import numpy as np
from typing import Dict, List, Any
from collections import deque
import logging

logger = logging.getLogger(__name__)

class CascadePredictor:
    """ML 기반 cascade 예측기"""
    
    def __init__(self, history_size: int = 10000):
        self.history = deque(maxlen=history_size)
        self.is_trained = False
    
    def extract_features(self, input_vector: np.ndarray) -> np.ndarray:
        """특징 추출"""
        return np.array([
            np.mean(input_vector),
            np.std(input_vector),
            np.max(input_vector),
            len(input_vector)
        ])
    
    def predict_cascade_probability(self, input_vector: np.ndarray) -> float:
        """Cascade 확률 예측 (0-1)"""
        features = self.extract_features(input_vector)
        max_val = features[2]
        
        if abs(max_val) > 1000:
            return 0.9  # 매우 높은 위험
        elif abs(max_val) > 100:
            return 0.6  # 중간 위험
        else:
            return 0.1  # 낮은 위험
    
    def should_block(self, input_vector: np.ndarray, threshold: float = 0.5) -> bool:
        """예측 차단 여부 결정"""
        probability = self.predict_cascade_probability(input_vector)
        return probability > threshold

