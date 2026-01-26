"""
Ternary State System for ThinkTank Admin Dashboard
Integrated with admin.paparazzime.cloud
"""
from .ternary_state import TernaryState, CREED, MOTTO
from .ternary_manager import TernaryStateManager, get_manager
from .alert_system import TernaryAlertSystem, get_alert_system, console_alert_handler

__all__ = [
    "TernaryState",
    "TernaryStateManager", 
    "TernaryAlertSystem",
    "get_manager",
    "get_alert_system",
    "console_alert_handler",
    "CREED",
    "MOTTO"
]
__version__ = "2.0.0"
