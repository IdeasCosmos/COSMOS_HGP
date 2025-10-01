"""
COSMOS MVP Core Module
핵심 엔진 및 시스템 컴포넌트
"""

try:
    from .engine import UnifiedCosmosEngine
except ImportError:
    UnifiedCosmosEngine = None

try:
    from .velocity import VelocityManager, Layer
except ImportError:
    VelocityManager = None
    Layer = None

try:
    from .annotation import AnnotationSystem
except ImportError:
    AnnotationSystem = None

try:
    from .healing import SelfHealingSystem
except ImportError:
    SelfHealingSystem = None

__all__ = [
    'UnifiedCosmosEngine',
    'VelocityManager', 
    'Layer',
    'AnnotationSystem',
    'SelfHealingSystem'
]
