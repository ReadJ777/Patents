"""
Ternary State API for Admin Dashboard
Integrated with admin.paparazzime.cloud
"""
from flask import Blueprint, jsonify, request
from datetime import datetime
from ternary_state_system import (
    TernaryState,
    get_manager,
    get_alert_system
)

ternary_bp = Blueprint('ternary', __name__, url_prefix='/api/ternary')

# Initialize systems
manager = get_manager()
alerts = get_alert_system(psi_threshold=5, time_window=60)

@ternary_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get ternary state statistics"""
    stats = manager.get_statistics()
    return jsonify({
        'success': True,
        'data': stats,
        'timestamp': datetime.now().isoformat()
    })

@ternary_bp.route('/alerts', methods=['GET'])
def get_alerts():
    """Get alert information"""
    alert_stats = alerts.get_alert_statistics()
    recent_alerts = [
        {
            'timestamp': a.timestamp.isoformat(),
            'severity': a.severity,
            'message': a.message,
            'category': a.category,
            'psi_count': a.psi_count,
            'pattern': a.pattern
        }
        for a in alerts.alert_history[-10:]
    ]
    
    return jsonify({
        'success': True,
        'data': {
            'statistics': alert_stats,
            'recent_alerts': recent_alerts
        },
        'timestamp': datetime.now().isoformat()
    })

@ternary_bp.route('/record', methods=['POST'])
def record_state():
    """Record a new state"""
    data = request.get_json()
    state_value = data.get('state', '1')
    category = data.get('category', 'general')
    
    try:
        state = TernaryState(state_value)
        manager.record_state(state, category)
        alerts.record_state(state, category)
        
        return jsonify({
            'success': True,
            'message': f'State {state.value} {state.symbol} recorded',
            'timestamp': datetime.now().isoformat()
        })
    except ValueError:
        return jsonify({
            'success': False,
            'error': 'Invalid state value. Use 0, 1, or Ψ'
        }), 400

@ternary_bp.route('/dashboard', methods=['GET'])
def get_dashboard_data():
    """Get complete dashboard data"""
    stats = manager.get_statistics()
    alert_stats = alerts.get_alert_statistics()
    recent_alerts = [
        {
            'timestamp': a.timestamp.isoformat(),
            'severity': a.severity,
            'message': a.message,
            'psi_count': a.psi_count
        }
        for a in alerts.alert_history[-5:]
    ]
    
    return jsonify({
        'success': True,
        'data': {
            'stats': stats,
            'alerts': {
                'statistics': alert_stats,
                'recent': recent_alerts
            },
            'system_info': {
                'version': '2.0.0',
                'features': ['ternary_logic', 'psi_detection', 'alerts'],
                'motto': 'For GOD Alone. Fearing GOD Alone.'
            }
        },
        'timestamp': datetime.now().isoformat()
    })

# Auto-initialize with some data
def initialize_ternary_system():
    """Initialize system with baseline data"""
    manager.record_state(TernaryState.ON, "system")
    manager.record_state(TernaryState.ON, "security")
    print("🦅 Ternary API initialized - For GOD Alone. Fearing GOD Alone.")

initialize_ternary_system()
