# COSMOS-HGP Core Engine
# Open Source Version (Apache 2.0 License)

"""
Core execution engine for COSMOS-HGP Open Source version.

Features:
- Hierarchical execution
- Local blocking
- Cumulative capping
- Timeline generation
- Deterministic replay
- REST API
- Basic dashboard
- Logging
"""

from .hier_exec import HierarchicalExecutor
from .impact import ImpactCalculator
from .cap import CumulativeCapper
from .filters import InequalityFilter

__version__ = "1.0.0"
__license__ = "Apache 2.0"

__all__ = [
    "HierarchicalExecutor",
    "ImpactCalculator", 
    "CumulativeCapper",
    "InequalityFilter"
]
