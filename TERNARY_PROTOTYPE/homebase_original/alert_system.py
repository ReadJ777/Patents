"""Ternary Alert System with Ψ Spike Detection"""
import logging
from typing import List
from datetime import datetime, timedelta
from collections import deque
from dataclasses import dataclass
from .ternary_state import TernaryState

logger = logging.getLogger(__name__)

@dataclass
class Alert:
    timestamp: datetime
    severity: str
    message: str
    category: str
    psi_count: int
    pattern: str = "▔▁▔▁▔▁▔▁"

class TernaryAlertSystem:
    PSI_ALERT_PATTERN = "▔▁▔▁▔▁▔▁"
    
    def __init__(self, psi_threshold: int = 5, time_window: int = 60):
        self.psi_threshold = psi_threshold
        self.time_window = time_window
        self.state_history = deque(maxlen=1000)
        self.alert_history: List[Alert] = []
        self.alerts_triggered = 0
        self.psi_spikes_detected = 0
        logger.info(f"🦅 TernaryAlertSystem initialized - Ψ threshold={psi_threshold}")
    
    def record_state(self, state: TernaryState, category: str = "general"):
        """Record a state occurrence"""
        self.state_history.append((datetime.now(), state, category))
        if state == TernaryState.PSI:
            self._check_psi_spike()
    
    def _check_psi_spike(self):
        """Detect if Ψ states exceed threshold"""
        now = datetime.now()
        window_start = now - timedelta(seconds=self.time_window)
        psi_count = sum(1 for ts, state, _ in self.state_history 
                       if state == TernaryState.PSI and ts >= window_start)
        
        if psi_count >= self.psi_threshold:
            self._trigger_psi_alert(psi_count)
    
    def _trigger_psi_alert(self, psi_count: int):
        """Trigger Ψ spike alert"""
        self.psi_spikes_detected += 1
        severity = 'CRITICAL' if psi_count >= self.psi_threshold * 3 else \
                  'HIGH' if psi_count >= self.psi_threshold * 2 else \
                  'MEDIUM' if psi_count >= self.psi_threshold * 1.5 else 'LOW'
        
        alert = Alert(
            timestamp=datetime.now(),
            severity=severity,
            message=f"System uncertainty detected: {psi_count} Ψ states in {self.time_window}s",
            category="uncertainty_spike",
            psi_count=psi_count
        )
        self.alert_history.append(alert)
        self.alerts_triggered += 1
        logger.warning(f"⚠️ ALERT: {alert.message}")
    
    def get_alert_statistics(self):
        """Get alert statistics"""
        return {
            'total_alerts': self.alerts_triggered,
            'psi_spikes': self.psi_spikes_detected,
            'threshold': self.psi_threshold,
            'window': self.time_window,
            'recent_alerts': len(self.alert_history)
        }

_alert_system = None
def get_alert_system(psi_threshold: int = 5, time_window: int = 60):
    global _alert_system
    if _alert_system is None:
        _alert_system = TernaryAlertSystem(psi_threshold, time_window)
    return _alert_system

def console_alert_handler(alert: Alert):
    print(f"\n{'='*60}\n⚠️ TERNARY ALERT - {alert.severity}\n{'='*60}")
    print(f"Time: {alert.timestamp}\nMessage: {alert.message}\nPattern: {alert.pattern}\n{'='*60}\n")
