"""Ternary State Manager"""
import logging
from typing import Dict
from datetime import datetime
from collections import defaultdict
from .ternary_state import TernaryState

logger = logging.getLogger(__name__)

class TernaryStateManager:
    def __init__(self):
        self.state_count = {'0': 0, '1': 0, 'Ψ': 0}
        self.category_states = defaultdict(lambda: {'0': 0, '1': 0, 'Ψ': 0})
        self.start_time = datetime.now()
        logger.info("🦅 TernaryStateManager initialized")
    
    def record_state(self, state: TernaryState, category: str = "general"):
        """Record a state occurrence"""
        self.state_count[state.value] += 1
        self.category_states[category][state.value] += 1
    
    def get_statistics(self) -> Dict:
        """Get overall statistics"""
        total = sum(self.state_count.values())
        if total == 0:
            return {'total': 0, 'states': self.state_count}
        
        return {
            'total': total,
            'success_rate': (self.state_count['1'] / total) * 100,
            'failure_rate': (self.state_count['0'] / total) * 100,
            'uncertain_rate': (self.state_count['Ψ'] / total) * 100,
            'states': self.state_count,
            'uptime': str(datetime.now() - self.start_time),
            'categories': dict(self.category_states)
        }

_manager = None
def get_manager():
    global _manager
    if _manager is None:
        _manager = TernaryStateManager()
    return _manager
