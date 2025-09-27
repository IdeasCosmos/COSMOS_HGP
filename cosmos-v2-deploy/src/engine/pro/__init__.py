# COSMOS-HGP Pro Engine
# Commercial Version (Proprietary License)

"""
Professional execution engine for COSMOS-HGP Commercial version.

Features:
- All Core features
- Parallel execution support
- Distributed processing
- Advanced dashboard with WebSocket
- ML-based prediction
- Advanced rule management
- SLA monitoring
- Security & RBAC
- Enterprise support
"""

# Pro features are available only with commercial license
# This module requires COSMOS-HGP Pro license

try:
    from .parallel_exec import ParallelExecutor
    from .distributed import DistributedProcessor
    from .advanced_dashboard import AdvancedDashboard
    from .ml_predictor import MLPredictor
    from .rule_manager import RuleManager
    from .sla_monitor import SLAMonitor
    from .security import RBACManager
    
    PRO_FEATURES_AVAILABLE = True
    
    __all__ = [
        "ParallelExecutor",
        "DistributedProcessor", 
        "AdvancedDashboard",
        "MLPredictor",
        "RuleManager",
        "SLAMonitor",
        "RBACManager"
    ]
    
except ImportError as e:
    PRO_FEATURES_AVAILABLE = False
    print("COSMOS-HGP Pro features not available. Commercial license required.")
    print(f"Import error: {e}")
    
    __all__ = []

__version__ = "1.0.0-pro"
__license__ = "Commercial"
