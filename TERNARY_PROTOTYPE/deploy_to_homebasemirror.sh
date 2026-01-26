#!/bin/bash
# Deploy ternary system to HOMEBASEMIRROR (192.168.1.107)
# For GOD Alone. Fearing GOD Alone. 🦅

MIRROR="root@192.168.1.107"
DEPLOY_DIR="/home/gge/services/ternary"

echo "╔══════════════════════════════════════════════════════╗"
echo "║  DEPLOYING TERNARY SYSTEM TO HOMEBASEMIRROR          ║"
echo "╚══════════════════════════════════════════════════════╝"

# Create directory on HOMEBASEMIRROR
ssh $MIRROR "mkdir -p $DEPLOY_DIR"

# Copy files
echo "📦 Copying unified ternary system..."
scp /root/Patents/TERNARY_PROTOTYPE/unified_ternary.py $MIRROR:$DEPLOY_DIR/
scp -r /root/Patents/TERNARY_PROTOTYPE/homebase_original/* $MIRROR:$DEPLOY_DIR/

# Create API service
echo "�� Creating API service..."
ssh $MIRROR "cat > $DEPLOY_DIR/ternary_service.py << 'INNER_EOF'
#!/usr/bin/env python3
\"\"\"
ZIME Ternary API Service
Runs on HOMEBASEMIRROR port 8089
\"\"\"
from flask import Flask, jsonify, request
from datetime import datetime
import sys
sys.path.insert(0, '/home/gge/services/ternary')
from unified_ternary import UnifiedTernarySystem, TernaryState

app = Flask(__name__)
system = UnifiedTernarySystem()

@app.route('/ternary/status', methods=['GET'])
def get_status():
    return jsonify(system.get_status())

@app.route('/ternary/evaluate', methods=['POST'])
def evaluate():
    data = request.get_json() or {}
    condition = data.get('condition', '')
    result = system.evaluate(condition, data.get('context', {}))
    return jsonify({
        'condition': condition,
        'result': result.value,
        'symbol': result.symbol,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/ternary/resolve', methods=['POST'])
def resolve():
    data = request.get_json() or {}
    psi_value = float(data.get('psi', 0.5))
    result = system.resolve_psi(psi_value)
    return jsonify({
        'input_psi': psi_value,
        'result': result.value,
        'symbol': result.symbol
    })

@app.route('/ternary/test', methods=['GET'])
def run_tests():
    return jsonify(system.run_truth_table_test())

if __name__ == '__main__':
    print('🦅 ZIME Ternary API starting on port 8089')
    app.run(host='0.0.0.0', port=8089)
INNER_EOF"

echo "✅ Deployment script ready"
echo "Run this script to deploy, then start service on HOMEBASEMIRROR"
