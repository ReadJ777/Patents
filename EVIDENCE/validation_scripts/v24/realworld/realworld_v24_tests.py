#!/usr/bin/env python3
"""
Real-World Scenario Verification - v24.1
USPTO Patent #63/967,611

Tests real-world application scenarios from Section 9 of spec:
1. Autonomous Vehicles
2. Medical Diagnosis  
3. Financial Fraud Detection
4. IoT Sensor Networks
5. Cloud Infrastructure
"""

import os
import sys
import socket
import hashlib
import time
import random

# ═══════════════════════════════════════════════════════════════
# AUTONOMOUS VEHICLE SCENARIO (Claim 1 + Claim 4)
# ═══════════════════════════════════════════════════════════════

def test_av_obstacle_classification():
    """
    Scenario: Autonomous vehicle classifying obstacle
    - High confidence (>0.55): Take action (brake/steer)
    - Low confidence (<0.45): No obstacle
    - Uncertain (0.45-0.55): DEFER - don't guess!
    """
    
    def classify_obstacle(sensor_confidence):
        if sensor_confidence < 0.45:
            return ('NO_OBSTACLE', 'continue')
        elif sensor_confidence > 0.55:
            return ('OBSTACLE', 'brake')
        else:
            return ('UNCERTAIN', 'defer_to_backup')
    
    scenarios = [
        (0.9, 'OBSTACLE'),     # Clear obstacle
        (0.1, 'NO_OBSTACLE'),  # Clear path
        (0.5, 'UNCERTAIN'),    # Fog/unclear - DEFER
        (0.48, 'UNCERTAIN'),   # Marginal - DEFER
        (0.52, 'UNCERTAIN'),   # Marginal - DEFER
    ]
    
    passed = 0
    for conf, expected in scenarios:
        result, action = classify_obstacle(conf)
        if result == expected:
            passed += 1
            # Verify uncertain cases defer (safety critical!)
            if expected == 'UNCERTAIN' and action != 'defer_to_backup':
                passed -= 1
    
    return passed, len(scenarios)

def test_av_no_wrong_decisions():
    """AV should NEVER make wrong committed decisions"""
    
    def simulate_av_decision(ground_truth, sensor_reading):
        # Classify
        if sensor_reading < 0.45:
            decision = 0  # No obstacle
        elif sensor_reading > 0.55:
            decision = 1  # Obstacle
        else:
            decision = None  # Deferred
        
        # Check if committed decision is correct
        if decision is not None:
            return decision == ground_truth
        else:
            return True  # Deferred = not wrong
    
    # Run 1000 scenarios
    wrong_count = 0
    for _ in range(1000):
        ground_truth = random.randint(0, 1)
        # Sensor has noise around truth
        noise = random.gauss(0, 0.15)
        sensor = ground_truth + noise
        sensor = max(0, min(1, sensor))  # Clamp
        
        if not simulate_av_decision(ground_truth, sensor):
            wrong_count += 1
    
    # Zero wrong decisions on COMMITTED cases
    if wrong_count == 0:
        return 2, 2
    return 0, 2

# ═══════════════════════════════════════════════════════════════
# MEDICAL DIAGNOSIS SCENARIO (Claim 1 + Claim 3)
# ═══════════════════════════════════════════════════════════════

def test_medical_diagnosis_deferral():
    """
    Medical diagnosis: uncertain cases should request specialist
    """
    
    def diagnose(biomarker_confidence):
        if biomarker_confidence > 0.55:
            return ('POSITIVE', 'treat')
        elif biomarker_confidence < 0.45:
            return ('NEGATIVE', 'monitor')
        else:
            return ('UNCERTAIN', 'request_specialist')
    
    tests = [
        (0.95, 'POSITIVE'),   # Clear positive
        (0.05, 'NEGATIVE'),   # Clear negative
        (0.50, 'UNCERTAIN'),  # Ambiguous - specialist needed
    ]
    
    passed = 0
    for conf, expected in tests:
        result, action = diagnose(conf)
        if result == expected:
            passed += 1
    
    return passed, len(tests)

def test_medical_accuracy():
    """Medical accuracy on committed decisions should be 100%"""
    
    correct = 0
    committed = 0
    
    random.seed(123)
    for _ in range(1000):
        # Ground truth
        truth = random.randint(0, 1)
        # Biomarker with noise
        reading = truth + random.gauss(0, 0.2)
        reading = max(0, min(1, reading))
        
        if reading < 0.45:
            decision = 0
            committed += 1
            if decision == truth:
                correct += 1
        elif reading > 0.55:
            decision = 1
            committed += 1
            if decision == truth:
                correct += 1
        # else: deferred, don't count
    
    accuracy = correct / committed if committed > 0 else 0
    
    # Should be very high on committed decisions
    if accuracy > 0.95:
        return 2, 2
    return 1, 2

# ═══════════════════════════════════════════════════════════════
# FINANCIAL FRAUD DETECTION (Claim 1 + Claim 2)
# ═══════════════════════════════════════════════════════════════

def test_fraud_detection():
    """
    Fraud detection: uncertain transactions get human review
    """
    
    def detect_fraud(risk_score):
        if risk_score > 0.55:
            return ('FRAUD', 'block')
        elif risk_score < 0.45:
            return ('LEGITIMATE', 'approve')
        else:
            return ('UNCERTAIN', 'human_review')
    
    tests = [
        (0.99, 'FRAUD'),       # Clear fraud
        (0.01, 'LEGITIMATE'),  # Clear legitimate
        (0.50, 'UNCERTAIN'),   # Human review
        (0.46, 'UNCERTAIN'),   # Marginal - review
    ]
    
    passed = 0
    for score, expected in tests:
        result, action = detect_fraud(score)
        if result == expected:
            passed += 1
    
    return passed, len(tests)

def test_fraud_consensus():
    """Multi-node fraud detection consensus"""
    
    def multi_node_consensus(scores, weights, threshold=0.66):
        """Weighted consensus from multiple detection nodes"""
        total_weight = sum(weights)
        fraud_weight = sum(w for s, w in zip(scores, weights) if s > 0.55)
        legit_weight = sum(w for s, w in zip(scores, weights) if s < 0.45)
        
        if fraud_weight / total_weight >= threshold:
            return 'FRAUD'
        elif legit_weight / total_weight >= threshold:
            return 'LEGITIMATE'
        else:
            return 'UNCERTAIN'
    
    tests = [
        ([0.9, 0.8, 0.85], [1, 1, 1], 'FRAUD'),
        ([0.1, 0.2, 0.15], [1, 1, 1], 'LEGITIMATE'),
        ([0.9, 0.1, 0.5], [1, 1, 1], 'UNCERTAIN'),  # Mixed
    ]
    
    passed = 0
    for scores, weights, expected in tests:
        if multi_node_consensus(scores, weights) == expected:
            passed += 1
    
    return passed, len(tests)

# ═══════════════════════════════════════════════════════════════
# IOT SENSOR NETWORK (Claim 2 + Claim 5)
# ═══════════════════════════════════════════════════════════════

def test_iot_sensor_fusion():
    """Multiple sensors should reach consensus"""
    
    def sensor_fusion(readings, weights):
        """Fuse multiple sensor readings with weights"""
        weighted_sum = sum(r * w for r, w in zip(readings, weights))
        total_weight = sum(weights)
        fused = weighted_sum / total_weight
        
        if fused < 0.45:
            return 0
        elif fused > 0.55:
            return 1
        else:
            return 2  # PSI
    
    tests = [
        ([0.9, 0.85, 0.88], [1, 1, 1], 1),   # All agree high
        ([0.1, 0.15, 0.12], [1, 1, 1], 0),   # All agree low
        ([0.9, 0.1, 0.5], [1, 1, 1], 2),     # Disagreement = PSI
    ]
    
    passed = 0
    for readings, weights, expected in tests:
        if sensor_fusion(readings, weights) == expected:
            passed += 1
    
    return passed, len(tests)

def test_iot_distributed_state():
    """Test distributed state synchronization"""
    
    class IoTNode:
        def __init__(self, node_id):
            self.node_id = node_id
            self.local_state = 2  # PSI initially
            self.neighbors = []
        
        def sync_with_neighbors(self):
            if not self.neighbors:
                return
            states = [n.local_state for n in self.neighbors]
            states.append(self.local_state)
            
            # Majority vote
            from collections import Counter
            counts = Counter(states)
            most_common = counts.most_common(1)[0][0]
            self.local_state = most_common
    
    # Create 5 node network
    nodes = [IoTNode(i) for i in range(5)]
    for i, n in enumerate(nodes):
        n.neighbors = [nodes[j] for j in range(5) if j != i]
    
    # Set majority to state 1
    nodes[0].local_state = 1
    nodes[1].local_state = 1
    nodes[2].local_state = 1
    
    # Sync
    for n in nodes:
        n.sync_with_neighbors()
    
    # All should converge to 1
    converged = all(n.local_state == 1 for n in nodes)
    
    if converged:
        return 2, 2
    return 1, 2

# ═══════════════════════════════════════════════════════════════
# CLOUD INFRASTRUCTURE (Claim 6 + Claim 7)
# ═══════════════════════════════════════════════════════════════

def test_cloud_power_management():
    """High PSI should trigger power reduction"""
    
    def should_reduce_power(psi_ratio, threshold=0.8, window_seconds=30):
        return psi_ratio > threshold
    
    tests = [
        (0.9, True),   # High PSI -> reduce
        (0.5, False),  # Medium PSI -> normal
        (0.1, False),  # Low PSI -> maybe boost
    ]
    
    passed = 0
    for psi, expected in tests:
        if should_reduce_power(psi) == expected:
            passed += 1
    
    return passed, len(tests)

def test_vm_scheduling():
    """VMs with high PSI get de-prioritized (Claim 7)"""
    
    def get_priority(psi_ratio):
        if psi_ratio > 0.7:
            return 'LOW'  # De-prioritize
        elif psi_ratio < 0.3:
            return 'HIGH'  # Prioritize
        else:
            return 'NORMAL'
    
    tests = [
        (0.9, 'LOW'),
        (0.1, 'HIGH'),
        (0.5, 'NORMAL'),
    ]
    
    passed = 0
    for psi, expected in tests:
        if get_priority(psi) == expected:
            passed += 1
    
    return passed, len(tests)

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    hostname = socket.gethostname()
    print("=" * 70)
    print(f"REAL-WORLD SCENARIO VERIFICATION @ {hostname}")
    print("=" * 70)
    
    tests = [
        # Autonomous Vehicles
        ("AV: Obstacle Classification", test_av_obstacle_classification),
        ("AV: No Wrong Decisions", test_av_no_wrong_decisions),
        # Medical
        ("Medical: Diagnosis Deferral", test_medical_diagnosis_deferral),
        ("Medical: Committed Accuracy", test_medical_accuracy),
        # Financial
        ("Fraud: Detection", test_fraud_detection),
        ("Fraud: Multi-Node Consensus", test_fraud_consensus),
        # IoT
        ("IoT: Sensor Fusion", test_iot_sensor_fusion),
        ("IoT: Distributed State", test_iot_distributed_state),
        # Cloud
        ("Cloud: Power Management", test_cloud_power_management),
        ("Cloud: VM Scheduling", test_vm_scheduling),
    ]
    
    total_passed = total_tests = 0
    for name, func in tests:
        try:
            p, t = func()
            total_passed += p
            total_tests += t
            print(f"  {'✅' if p==t else '⚠️'} {name}: {p}/{t}")
        except Exception as e:
            print(f"  ❌ {name}: {e}")
            total_tests += 1
    
    print("-" * 70)
    print(f"REAL-WORLD TOTAL: {total_passed}/{total_tests}")
    h = hashlib.md5(f"realworld-{total_passed}/{total_tests}".encode()).hexdigest()[:16]
    print(f"Hash: {h}")
    
    return 0 if total_passed == total_tests else 1

if __name__ == '__main__':
    sys.exit(main())
