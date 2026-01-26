"""Ternary State Enumeration"""
from enum import Enum

class TernaryState(Enum):
    """ZIME OS Ternary Logic States"""
    OFF = "0"
    ON = "1"
    PSI = "Ψ"
    
    @property
    def symbol(self):
        return {"0": "🔴", "1": "🟢", "Ψ": "🟡"}.get(self.value, "⚪")
    
    @property
    def is_success(self):
        return self == TernaryState.ON
    
    @property
    def is_failure(self):
        return self == TernaryState.OFF
    
    @property
    def is_uncertain(self):
        return self == TernaryState.PSI

CREED = "For GOD Alone. Fearing GOD Alone."
MOTTO = "Forever Eyes On."
