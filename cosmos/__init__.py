"""
COSMOS-HGP Free Version
Hierarchical Gradient Propagation System
"""

__version__ = "1.0.0"
__author__ = "장재혁 (IdeasCosmos)"
__email__ = "sjpupro@gmail.com"

from .engine import BasicEngine
from .api_client import CosmosAPI
from .exceptions import ProFeatureError

__all__ = [
    'BasicEngine',
    'CosmosAPI',
    'ProFeatureError'
]
