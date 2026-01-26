"""ZIME Ternary Computing System - Patent 63/967,611"""
from .unified_ternary import UnifiedTernarySystem, TernaryState, TernaryLogic, PsiResolver, KernelInterface
from .ternary_decision import TernaryDecision

# Aliases for convenience
TernarySystem = UnifiedTernarySystem
PSI = TernaryState.PSI

__version__ = "1.0.0"
__patent__ = "63/967,611"
__all__ = ['TernarySystem', 'UnifiedTernarySystem', 'TernaryState', 'TernaryLogic', 
           'PsiResolver', 'KernelInterface', 'TernaryDecision', 'PSI']
