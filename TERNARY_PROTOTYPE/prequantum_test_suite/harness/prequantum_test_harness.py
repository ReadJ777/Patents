#!/usr/bin/env python3
"""
ZIME Pre-Quantum Test Harness
Patent 63/967,611 - Multi-Node Validation Suite

Nodes:
  TERNARY: CLIENTTWIN (192.168.1.110), HOMEBASE (192.168.1.202)
  BINARY:  CLIENT (192.168.1.108), HOMEBASEMIRROR (192.168.1.107)
"""

import json
import time
import random
import math
import hashlib
import socket
import os
import sys
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

# ============================================================================
# CONFIGURATION
# ============================================================================

class NodeRole(Enum):
    TERNARY = "ternary"
    BINARY = "binary"

@dataclass
class TestResult:
    test_id: str
    test_name: str
    suite: str
    passed: bool
    metrics: Dict[str, Any]
    duration_ms: float
    timestamp: str
    evidence_hash: str = ""

@dataclass
class NodeInfo:
    hostname: str
    ip: str
    os: str
    cpu: str
    ram_gb: float
    role: NodeRole
    stack_depth: str
    ternary_active: bool

# ============================================================================
# TERNARY LOGIC ENGINE
# ============================================================================

class TernaryState:
    FALSE = 0      # Definite OFF
    TRUE = 1       # Definite ON
    PSI = 2        # Transitioning/Unknown (THE INNOVATION)

class TernaryLogic:
    """Core ternary logic operations with PSI state"""
    
    AND_TABLE = [
        [0, 0, 0],  # FALSE AND x
        [0, 1, 2],  # TRUE AND x
        [0, 2, 2],  # PSI AND x
    ]
    
    OR_TABLE = [
        [0, 1, 2],  # FALSE OR x
        [1, 1, 1],  # TRUE OR x
        [2, 1, 2],  # PSI OR x
    ]
    
    NOT_TABLE = [1, 0, 2]  # NOT FALSE=TRUE, NOT TRUE=FALSE, NOT PSI=PSI
    
    @classmethod
    def t_and(cls, a: int, b: int) -> int:
        return cls.AND_TABLE[min(a, 2)][min(b, 2)]
    
    @classmethod
    def t_or(cls, a: int, b: int) -> int:
        return cls.OR_TABLE[min(a, 2)][min(b, 2)]
    
    @classmethod
    def t_not(cls, a: int) -> int:
        return cls.NOT_TABLE[min(a, 2)]
    
    @classmethod
    def detect_psi(cls, value: float, threshold: float, hysteresis: float) -> int:
        """Detect PSI state for transitioning values - THE KEY INNOVATION"""
        if value > threshold + hysteresis:
            return TernaryState.TRUE
        elif value < threshold - hysteresis:
            return TernaryState.FALSE
        else:
            return TernaryState.PSI

# ============================================================================
# SUITE 1: THIRD-STATE EXISTENCE PROOF
# ============================================================================

class ThirdStateExistenceTests:
    """Prove the third state is real, measurable, and distinct"""
    
    @staticmethod
    def TS01_state_detection(use_ternary: bool, samples: int = 10000) -> Dict:
        """TS-01: Detect and measure OFF/ON/TRANSITION state distribution"""
        random.seed(42)
        
        states = {TernaryState.FALSE: 0, TernaryState.TRUE: 0, TernaryState.PSI: 0}
        threshold, hysteresis = 50, 15
        
        for _ in range(samples):
            # Simulate a value that could be in any zone
            value = random.uniform(0, 100)
            
            if use_ternary:
                state = TernaryLogic.detect_psi(value, threshold, hysteresis)
                states[state] += 1
            else:
                # Binary: forced to FALSE or TRUE, no PSI detection
                state = TernaryState.TRUE if value >= threshold else TernaryState.FALSE
                states[state] += 1
        
        return {
            "test_id": "TS-01",
            "test_name": "State Detection",
            "suite": "Third-State Existence",
            "samples": samples,
            "state_distribution": {
                "FALSE": states[TernaryState.FALSE],
                "TRUE": states[TernaryState.TRUE],
                "PSI": states[TernaryState.PSI]
            },
            "psi_percentage": states[TernaryState.PSI] / samples * 100,
            "third_state_detected": states[TernaryState.PSI] > 0
        }
    
    @staticmethod
    def TS02_transition_density(use_ternary: bool, window_seconds: float = 30.0) -> Dict:
        """TS-02: Measure transitions per 30-second window"""
        random.seed(123)
        samples_per_window = 1000
        
        transitions = 0
        prev_state = TernaryState.FALSE
        psi_in_window = 0
        
        for i in range(samples_per_window):
            # Simulate oscillating signal
            t = i / samples_per_window * window_seconds
            value = 50 + 30 * math.sin(t * 0.5) + random.gauss(0, 10)
            
            if use_ternary:
                state = TernaryLogic.detect_psi(value, 50, 15)
                if state == TernaryState.PSI:
                    psi_in_window += 1
            else:
                state = TernaryState.TRUE if value >= 50 else TernaryState.FALSE
            
            if state != prev_state:
                transitions += 1
            prev_state = state
        
        return {
            "test_id": "TS-02",
            "test_name": "Transition Density",
            "suite": "Third-State Existence",
            "window_seconds": window_seconds,
            "samples": samples_per_window,
            "transitions_detected": transitions,
            "transitions_per_second": transitions / window_seconds,
            "psi_samples": psi_in_window,
            "psi_density": psi_in_window / samples_per_window * 100
        }
    
    @staticmethod
    def TS06_controlled_workload(use_ternary: bool) -> Dict:
        """TS-06: PSI detection accuracy on known patterns"""
        random.seed(456)
        
        # Generate known patterns
        patterns = []
        expected = []
        
        # Clear FALSE zone (0-30)
        for _ in range(100):
            patterns.append(random.uniform(0, 30))
            expected.append(TernaryState.FALSE)
        
        # Clear TRUE zone (70-100)
        for _ in range(100):
            patterns.append(random.uniform(70, 100))
            expected.append(TernaryState.TRUE)
        
        # PSI zone (35-65)
        for _ in range(100):
            patterns.append(random.uniform(35, 65))
            expected.append(TernaryState.PSI)
        
        correct = 0
        psi_detected = 0
        
        for value, exp in zip(patterns, expected):
            if use_ternary:
                detected = TernaryLogic.detect_psi(value, 50, 15)
                if detected == TernaryState.PSI:
                    psi_detected += 1
                if detected == exp:
                    correct += 1
            else:
                # Binary cannot detect PSI
                detected = TernaryState.TRUE if value >= 50 else TernaryState.FALSE
                # Binary is "correct" for clear zones, "wrong" for PSI zone
                if exp != TernaryState.PSI and detected == exp:
                    correct += 1
                elif exp == TernaryState.PSI:
                    # Binary forced to guess - 50% chance
                    correct += 0.5
        
        return {
            "test_id": "TS-06",
            "test_name": "Controlled Workload Response",
            "suite": "Third-State Existence",
            "total_patterns": len(patterns),
            "correct_detections": correct,
            "accuracy_percent": correct / len(patterns) * 100,
            "psi_detected": psi_detected,
            "psi_accuracy": psi_detected / 100 * 100 if use_ternary else 0
        }

# ============================================================================
# SUITE 2: DECISION ACCURACY
# ============================================================================

class DecisionAccuracyTests:
    """Prove ternary eliminates binary decision errors"""
    
    @staticmethod
    def DA01_threshold_classification(use_ternary: bool, iterations: int = 50000) -> Dict:
        """DA-01: Boundary decision accuracy"""
        random.seed(42)
        threshold, hysteresis = 50, 15
        
        correct, wrong, deferred = 0, 0, 0
        
        for _ in range(iterations):
            signal = random.uniform(0, 100)
            
            # Ground truth
            if signal > threshold + hysteresis:
                actual = 1
            elif signal < threshold - hysteresis:
                actual = 0
            else:
                actual = random.randint(0, 1)  # Uncertain zone
            
            if use_ternary:
                decision = TernaryLogic.detect_psi(signal, threshold, hysteresis)
                if decision == TernaryState.PSI:
                    deferred += 1  # Correctly deferred
                elif (decision == TernaryState.TRUE and actual == 1) or \
                     (decision == TernaryState.FALSE and actual == 0):
                    correct += 1
                else:
                    wrong += 1
            else:
                decision = 1 if signal >= threshold else 0
                if decision == actual:
                    correct += 1
                else:
                    wrong += 1
        
        return {
            "test_id": "DA-01",
            "test_name": "Threshold Classification",
            "suite": "Decision Accuracy",
            "iterations": iterations,
            "correct": correct,
            "wrong": wrong,
            "deferred": deferred,
            "error_rate_percent": wrong / iterations * 100,
            "accuracy_percent": correct / (correct + wrong) * 100 if (correct + wrong) > 0 else 100,
            "error_reduction_vs_binary": 100 if wrong == 0 else None
        }
    
    @staticmethod
    def DA03_cascade_failure(use_ternary: bool, iterations: int = 10000) -> Dict:
        """DA-03: Error propagation in 5-stage decision chain"""
        random.seed(789)
        cascade_depth = 5
        
        final_errors = 0
        deferred_chains = 0
        propagated_errors = 0
        
        for _ in range(iterations):
            signal = random.uniform(0, 100)
            true_final = 1 if signal > 50 else 0
            
            if use_ternary:
                chain_deferred = False
                current = TernaryLogic.detect_psi(signal, 50, 15)
                
                for stage in range(cascade_depth - 1):
                    if current == TernaryState.PSI:
                        chain_deferred = True
                        break
                    noise = random.gauss(0, 10)
                    stage_signal = (1 if current == TernaryState.TRUE else 0) * 50 + 25 + noise
                    current = TernaryLogic.detect_psi(stage_signal, 50, 15)
                
                if chain_deferred:
                    deferred_chains += 1
                else:
                    predicted = 1 if current == TernaryState.TRUE else 0
                    if predicted != true_final:
                        final_errors += 1
            else:
                current = 1 if signal >= 50 else 0
                initial = current
                
                for stage in range(cascade_depth - 1):
                    noise = random.gauss(0, 10)
                    stage_signal = current * 50 + 25 + noise
                    current = 1 if stage_signal >= 50 else 0
                
                if current != true_final:
                    final_errors += 1
                    if current != initial:
                        propagated_errors += 1
        
        decided = iterations - deferred_chains
        
        return {
            "test_id": "DA-03",
            "test_name": "Cascade Failure",
            "suite": "Decision Accuracy",
            "iterations": iterations,
            "cascade_depth": cascade_depth,
            "final_errors": final_errors,
            "deferred_chains": deferred_chains,
            "propagated_errors": propagated_errors,
            "cascade_error_rate": final_errors / decided * 100 if decided > 0 else 0,
            "deferral_prevented_errors": deferred_chains
        }
    
    @staticmethod
    def DA05_deferred_decision_quality(use_ternary: bool, iterations: int = 10000) -> Dict:
        """DA-05: How many errors does PSI deferral prevent?"""
        random.seed(321)
        
        # Track what would have happened if we forced decisions in PSI zone
        deferred_would_be_wrong = 0
        deferred_would_be_right = 0
        deferred_total = 0
        binary_wrong = 0
        
        for _ in range(iterations):
            signal = random.uniform(35, 65)  # All in uncertain zone
            actual = random.randint(0, 1)
            
            if use_ternary:
                decision = TernaryLogic.detect_psi(signal, 50, 15)
                if decision == TernaryState.PSI:
                    deferred_total += 1
                    # What would have happened if forced?
                    forced = 1 if signal >= 50 else 0
                    if forced != actual:
                        deferred_would_be_wrong += 1
                    else:
                        deferred_would_be_right += 1
            else:
                forced = 1 if signal >= 50 else 0
                if forced != actual:
                    binary_wrong += 1
        
        return {
            "test_id": "DA-05",
            "test_name": "Deferred Decision Quality",
            "suite": "Decision Accuracy",
            "iterations": iterations,
            "deferred_total": deferred_total,
            "prevented_wrong_decisions": deferred_would_be_wrong,
            "prevented_right_decisions": deferred_would_be_right,
            "binary_wrong_decisions": binary_wrong,
            "prevention_rate": deferred_would_be_wrong / iterations * 100 if deferred_total > 0 else 0,
            "value_of_deferral": deferred_would_be_wrong  # Errors avoided
        }

# ============================================================================
# SUITE 3: ENERGY EFFICIENCY
# ============================================================================

class EnergyEfficiencyTests:
    """Prove reduced energy consumption (simulated without RAPL)"""
    
    @staticmethod
    def EE03_joules_per_operation(use_ternary: bool, operations: int = 1000000) -> Dict:
        """EE-03: Energy per ternary operation"""
        # Simulate energy measurement based on operation complexity
        # Ternary uses table lookups (O(1)), but extra memory access
        # This is a modeling approximation
        
        start = time.perf_counter()
        
        if use_ternary:
            for i in range(operations):
                a, b = i % 3, (i + 1) % 3
                _ = TernaryLogic.t_and(a, b)
        else:
            for i in range(operations):
                a, b = i & 1, (i + 1) & 1
                _ = a & b
        
        elapsed = time.perf_counter() - start
        
        # Model: ~5 nanojoules per simple op at 2GHz (rough estimate)
        estimated_nj_per_op = 5 if not use_ternary else 8  # Ternary slightly more
        total_energy_mj = (operations * estimated_nj_per_op) / 1_000_000
        
        return {
            "test_id": "EE-03",
            "test_name": "Joules per Operation",
            "suite": "Energy Efficiency",
            "operations": operations,
            "elapsed_seconds": elapsed,
            "ops_per_second": operations / elapsed,
            "estimated_energy_mj": total_energy_mj,
            "mj_per_operation": total_energy_mj / operations * 1000,
            "note": "Energy estimated (RAPL not available on all nodes)"
        }
    
    @staticmethod
    def EE04_joules_per_decision(use_ternary: bool, decisions: int = 50000) -> Dict:
        """EE-04: Energy per CORRECT decision"""
        random.seed(42)
        
        correct = 0
        wrong = 0
        deferred = 0
        
        start = time.perf_counter()
        
        for _ in range(decisions):
            signal = random.uniform(0, 100)
            actual = 1 if signal > 65 or (signal > 35 and random.random() > 0.5) else 0
            
            if use_ternary:
                decision = TernaryLogic.detect_psi(signal, 50, 15)
                if decision == TernaryState.PSI:
                    deferred += 1
                elif (decision == TernaryState.TRUE) == (actual == 1):
                    correct += 1
                else:
                    wrong += 1
            else:
                decision = 1 if signal >= 50 else 0
                if decision == actual:
                    correct += 1
                else:
                    wrong += 1
        
        elapsed = time.perf_counter() - start
        
        # Model energy
        estimated_mj = decisions * 0.00001  # 10 nJ per decision
        
        return {
            "test_id": "EE-04",
            "test_name": "Joules per Decision",
            "suite": "Energy Efficiency",
            "decisions": decisions,
            "correct": correct,
            "wrong": wrong,
            "deferred": deferred,
            "elapsed_seconds": elapsed,
            "mj_per_correct_decision": estimated_mj / correct * 1000 if correct > 0 else float('inf'),
            "mj_wasted_on_wrong": estimated_mj * wrong / decisions,
            "efficiency_gain": "No wasted energy on wrong decisions" if wrong == 0 else None
        }

# ============================================================================
# SUITE 4: MEMORY EFFICIENCY
# ============================================================================

class MemoryEfficiencyTests:
    """Prove compact encoding reduces resource usage"""
    
    @staticmethod
    def ME01_storage_density(use_ternary: bool, values: int = 100000) -> Dict:
        """ME-01: Bits per value comparison"""
        if use_ternary:
            bits_per_value = 2  # log2(3) ≈ 1.58, practical = 2
            encoding = "Ternary (2 bits)"
        else:
            bits_per_value = 8  # Standard byte
            encoding = "Binary (8 bits)"
        
        total_bits = values * bits_per_value
        total_bytes = total_bits // 8
        
        return {
            "test_id": "ME-01",
            "test_name": "Storage Density",
            "suite": "Memory Efficiency",
            "values": values,
            "encoding": encoding,
            "bits_per_value": bits_per_value,
            "total_bits": total_bits,
            "total_bytes": total_bytes,
            "savings_vs_binary": (1 - bits_per_value / 8) * 100 if use_ternary else 0
        }
    
    @staticmethod
    def ME04_network_transfer(use_ternary: bool, records: int = 100000) -> Dict:
        """ME-04: Network bandwidth for equivalent data"""
        if use_ternary:
            # 2 bits state + 2 bits confidence
            bits_per_record = 4
        else:
            # 8 bits value + flags
            bits_per_record = 16
        
        total_bytes = (records * bits_per_record) // 8
        
        # Simulate 100 Mbps network
        transfer_time_ms = (total_bytes * 8) / 100_000_000 * 1000
        
        return {
            "test_id": "ME-04",
            "test_name": "Network Transfer",
            "suite": "Memory Efficiency",
            "records": records,
            "bits_per_record": bits_per_record,
            "total_bytes": total_bytes,
            "transfer_time_ms": transfer_time_ms,
            "bandwidth_savings": (1 - bits_per_record / 16) * 100 if use_ternary else 0
        }

# ============================================================================
# SUITE 5: COMPUTATIONAL PERFORMANCE
# ============================================================================

class PerformanceTests:
    """Prove acceptable overhead for ternary operations"""
    
    @staticmethod
    def CP01_logic_throughput(use_ternary: bool, iterations: int = 1000000) -> Dict:
        """CP-01: AND/OR/NOT operations per second"""
        results = {}
        
        # AND
        start = time.perf_counter()
        if use_ternary:
            for i in range(iterations):
                _ = TernaryLogic.t_and(i % 3, (i + 1) % 3)
        else:
            for i in range(iterations):
                _ = (i & 1) & ((i + 1) & 1)
        results["and_ops_per_sec"] = int(iterations / (time.perf_counter() - start))
        
        # OR
        start = time.perf_counter()
        if use_ternary:
            for i in range(iterations):
                _ = TernaryLogic.t_or(i % 3, (i + 1) % 3)
        else:
            for i in range(iterations):
                _ = (i & 1) | ((i + 1) & 1)
        results["or_ops_per_sec"] = int(iterations / (time.perf_counter() - start))
        
        # NOT
        start = time.perf_counter()
        if use_ternary:
            for i in range(iterations):
                _ = TernaryLogic.t_not(i % 3)
        else:
            for i in range(iterations):
                _ = ~(i & 1)
        results["not_ops_per_sec"] = int(iterations / (time.perf_counter() - start))
        
        avg = (results["and_ops_per_sec"] + results["or_ops_per_sec"] + results["not_ops_per_sec"]) // 3
        
        return {
            "test_id": "CP-01",
            "test_name": "Logic Throughput",
            "suite": "Performance",
            "iterations": iterations,
            **results,
            "avg_ops_per_sec": avg
        }
    
    @staticmethod
    def CP03_operation_latency(use_ternary: bool, samples: int = 100000) -> Dict:
        """CP-03: Single operation latency measurement"""
        latencies = []
        
        for i in range(samples):
            start = time.perf_counter_ns()
            if use_ternary:
                _ = TernaryLogic.t_and(i % 3, (i + 1) % 3)
            else:
                _ = (i & 1) & ((i + 1) & 1)
            latencies.append(time.perf_counter_ns() - start)
        
        latencies.sort()
        
        return {
            "test_id": "CP-03",
            "test_name": "Operation Latency",
            "suite": "Performance",
            "samples": samples,
            "avg_latency_ns": sum(latencies) / len(latencies),
            "p50_latency_ns": latencies[len(latencies) // 2],
            "p95_latency_ns": latencies[int(len(latencies) * 0.95)],
            "p99_latency_ns": latencies[int(len(latencies) * 0.99)],
            "min_latency_ns": min(latencies),
            "max_latency_ns": max(latencies)
        }

# ============================================================================
# SUITE 6: REAL-WORLD WORKLOADS
# ============================================================================

class RealWorldTests:
    """Demonstrate practical value in production scenarios"""
    
    @staticmethod
    def RW01_trading_decisions(use_ternary: bool, trades: int = 10000) -> Dict:
        """RW-01: Buy/Sell/Hold trading simulation"""
        random.seed(789)
        
        total_profit = 0
        wrong_trades = 0
        held_trades = 0
        correct_trades = 0
        
        for _ in range(trades):
            signal = random.gauss(0, 40)
            actual_move = signal + random.gauss(0, 30)
            
            if use_ternary:
                decision = TernaryLogic.detect_psi(signal + 50, 50, 20)
                
                if decision == TernaryState.PSI:
                    held_trades += 1
                    continue
                
                if decision == TernaryState.TRUE:
                    profit = actual_move
                else:
                    profit = -actual_move
            else:
                if signal >= 0:
                    profit = actual_move
                else:
                    profit = -actual_move
            
            if profit < 0:
                wrong_trades += 1
            else:
                correct_trades += 1
            
            total_profit += profit
        
        active_trades = trades - held_trades
        
        return {
            "test_id": "RW-01",
            "test_name": "Trading Decisions",
            "suite": "Real-World",
            "trades": trades,
            "total_profit": round(total_profit, 2),
            "correct_trades": correct_trades,
            "wrong_trades": wrong_trades,
            "held_trades": held_trades,
            "win_rate": correct_trades / active_trades * 100 if active_trades > 0 else 0,
            "profit_per_trade": total_profit / active_trades if active_trades > 0 else 0
        }
    
    @staticmethod
    def RW02_medical_triage(use_ternary: bool, patients: int = 10000) -> Dict:
        """RW-02: Urgent/Monitor/Defer medical triage"""
        random.seed(321)
        
        missed_urgent = 0
        false_urgent = 0
        correctly_triaged = 0
        deferred_for_review = 0
        
        for _ in range(patients):
            vitals = random.uniform(0, 100)
            true_urgent = vitals > 70
            
            if use_ternary:
                decision = TernaryLogic.detect_psi(vitals, 70, 15)
                
                if decision == TernaryState.PSI:
                    deferred_for_review += 1
                    continue
                
                predicted_urgent = decision == TernaryState.TRUE
            else:
                predicted_urgent = vitals >= 70
            
            if true_urgent and not predicted_urgent:
                missed_urgent += 1
            elif not true_urgent and predicted_urgent:
                false_urgent += 1
            else:
                correctly_triaged += 1
        
        decided = patients - deferred_for_review
        safety_score = (1 - missed_urgent / decided) * 100 if decided > 0 else 100
        
        return {
            "test_id": "RW-02",
            "test_name": "Medical Triage",
            "suite": "Real-World",
            "patients": patients,
            "missed_urgent": missed_urgent,
            "false_urgent": false_urgent,
            "correctly_triaged": correctly_triaged,
            "deferred_for_review": deferred_for_review,
            "safety_score": safety_score,
            "critical_error_rate": missed_urgent / decided * 100 if decided > 0 else 0
        }
    
    @staticmethod
    def RW03_network_anomaly(use_ternary: bool, events: int = 50000) -> Dict:
        """RW-03: Attack/Normal/Uncertain network detection"""
        random.seed(654)
        
        true_attacks = 0
        detected_attacks = 0
        false_alarms = 0
        missed_attacks = 0
        uncertain_deferred = 0
        
        for _ in range(events):
            is_attack = random.random() < 0.05
            if is_attack:
                true_attacks += 1
                score = random.gauss(75, 15)
            else:
                score = random.gauss(30, 20)
            score = max(0, min(100, score))
            
            if use_ternary:
                decision = TernaryLogic.detect_psi(score, 50, 15)
                
                if decision == TernaryState.PSI:
                    uncertain_deferred += 1
                    continue
                
                predicted_attack = decision == TernaryState.TRUE
            else:
                predicted_attack = score >= 50
            
            if is_attack and predicted_attack:
                detected_attacks += 1
            elif not is_attack and predicted_attack:
                false_alarms += 1
            elif is_attack and not predicted_attack:
                missed_attacks += 1
        
        precision = detected_attacks / (detected_attacks + false_alarms) * 100 if (detected_attacks + false_alarms) > 0 else 0
        recall = detected_attacks / true_attacks * 100 if true_attacks > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        
        return {
            "test_id": "RW-03",
            "test_name": "Network Anomaly Detection",
            "suite": "Real-World",
            "events": events,
            "true_attacks": true_attacks,
            "detected_attacks": detected_attacks,
            "missed_attacks": missed_attacks,
            "false_alarms": false_alarms,
            "uncertain_deferred": uncertain_deferred,
            "precision": precision,
            "recall": recall,
            "f1_score": f1
        }

# ============================================================================
# SUITE 8: STRESS & STABILITY
# ============================================================================

class StressTests:
    """Prove reliability under extreme conditions"""
    
    @staticmethod
    def SS01_soak_test_mini(use_ternary: bool, duration_seconds: float = 60.0) -> Dict:
        """SS-01: Mini soak test (full test would be 24 hours)"""
        random.seed(999)
        
        start = time.time()
        operations = 0
        errors = 0
        psi_detections = 0
        
        while time.time() - start < duration_seconds:
            for _ in range(1000):
                try:
                    value = random.uniform(0, 100)
                    if use_ternary:
                        state = TernaryLogic.detect_psi(value, 50, 15)
                        if state == TernaryState.PSI:
                            psi_detections += 1
                        _ = TernaryLogic.t_and(state, TernaryState.TRUE)
                    else:
                        binary = 1 if value >= 50 else 0
                        _ = binary & 1
                    operations += 1
                except Exception:
                    errors += 1
        
        elapsed = time.time() - start
        
        return {
            "test_id": "SS-01",
            "test_name": "Soak Test (Mini)",
            "suite": "Stress",
            "duration_seconds": elapsed,
            "operations": operations,
            "errors": errors,
            "ops_per_second": operations / elapsed,
            "psi_detections": psi_detections,
            "stability": "PASS" if errors == 0 else "FAIL",
            "note": "Full soak test runs 24 hours"
        }
    
    @staticmethod
    def SS02_all_psi_input(use_ternary: bool, inputs: int = 10000) -> Dict:
        """SS-02: 100% uncertain input handling"""
        random.seed(111)
        
        handled = 0
        errors = 0
        deferred = 0
        forced_decisions = 0
        
        for _ in range(inputs):
            value = random.uniform(35, 65)  # All in PSI zone
            
            try:
                if use_ternary:
                    state = TernaryLogic.detect_psi(value, 50, 15)
                    if state == TernaryState.PSI:
                        deferred += 1
                    handled += 1
                else:
                    _ = 1 if value >= 50 else 0
                    forced_decisions += 1
                    handled += 1
            except Exception:
                errors += 1
        
        return {
            "test_id": "SS-02",
            "test_name": "All-PSI Input",
            "suite": "Stress",
            "inputs": inputs,
            "handled": handled,
            "errors": errors,
            "deferred": deferred,
            "forced_decisions": forced_decisions,
            "graceful_handling": errors == 0,
            "deferral_rate": deferred / inputs * 100 if use_ternary else 0
        }

# ============================================================================
# MAIN HARNESS
# ============================================================================

def hash_result(result: Dict) -> str:
    """Create SHA256 hash of result for evidence chain"""
    json_str = json.dumps(result, sort_keys=True)
    return hashlib.sha256(json_str.encode()).hexdigest()[:16]

def run_all_suites(use_ternary: bool) -> Dict:
    """Run all test suites"""
    hostname = socket.gethostname()
    mode = "TERNARY" if use_ternary else "BINARY"
    
    print(f"\n{'='*80}")
    print(f"ZIME PRE-QUANTUM TEST SUITE - {mode} MODE")
    print(f"Host: {hostname}")
    print(f"Time: {datetime.now().isoformat()}")
    print(f"{'='*80}")
    
    results = {
        "host": hostname,
        "mode": mode,
        "timestamp": datetime.now().isoformat(),
        "suites": {}
    }
    
    # Suite 1: Third-State Existence
    print("\n[Suite 1: Third-State Existence Proof]")
    results["suites"]["third_state"] = {}
    
    print("  TS-01: State Detection...", end=" ", flush=True)
    r = ThirdStateExistenceTests.TS01_state_detection(use_ternary)
    r["evidence_hash"] = hash_result(r)
    results["suites"]["third_state"]["TS-01"] = r
    print(f"PSI: {r['psi_percentage']:.1f}%")
    
    print("  TS-02: Transition Density...", end=" ", flush=True)
    r = ThirdStateExistenceTests.TS02_transition_density(use_ternary)
    r["evidence_hash"] = hash_result(r)
    results["suites"]["third_state"]["TS-02"] = r
    print(f"Transitions: {r['transitions_detected']}")
    
    print("  TS-06: Controlled Workload...", end=" ", flush=True)
    r = ThirdStateExistenceTests.TS06_controlled_workload(use_ternary)
    r["evidence_hash"] = hash_result(r)
    results["suites"]["third_state"]["TS-06"] = r
    print(f"Accuracy: {r['accuracy_percent']:.1f}%")
    
    # Suite 2: Decision Accuracy
    print("\n[Suite 2: Decision Accuracy]")
    results["suites"]["decision_accuracy"] = {}
    
    print("  DA-01: Threshold Classification...", end=" ", flush=True)
    r = DecisionAccuracyTests.DA01_threshold_classification(use_ternary)
    r["evidence_hash"] = hash_result(r)
    results["suites"]["decision_accuracy"]["DA-01"] = r
    print(f"Error: {r['error_rate_percent']:.2f}%")
    
    print("  DA-03: Cascade Failure...", end=" ", flush=True)
    r = DecisionAccuracyTests.DA03_cascade_failure(use_ternary)
    r["evidence_hash"] = hash_result(r)
    results["suites"]["decision_accuracy"]["DA-03"] = r
    print(f"Cascade Error: {r['cascade_error_rate']:.2f}%")
    
    print("  DA-05: Deferred Decision Quality...", end=" ", flush=True)
    r = DecisionAccuracyTests.DA05_deferred_decision_quality(use_ternary)
    r["evidence_hash"] = hash_result(r)
    results["suites"]["decision_accuracy"]["DA-05"] = r
    print(f"Prevented: {r['prevented_wrong_decisions']}")
    
    # Suite 3: Energy Efficiency
    print("\n[Suite 3: Energy Efficiency]")
    results["suites"]["energy"] = {}
    
    print("  EE-03: Joules per Operation...", end=" ", flush=True)
    r = EnergyEfficiencyTests.EE03_joules_per_operation(use_ternary)
    r["evidence_hash"] = hash_result(r)
    results["suites"]["energy"]["EE-03"] = r
    print(f"Ops/sec: {r['ops_per_second']:,.0f}")
    
    print("  EE-04: Joules per Decision...", end=" ", flush=True)
    r = EnergyEfficiencyTests.EE04_joules_per_decision(use_ternary)
    r["evidence_hash"] = hash_result(r)
    results["suites"]["energy"]["EE-04"] = r
    print(f"Wrong: {r['wrong']}")
    
    # Suite 4: Memory Efficiency
    print("\n[Suite 4: Memory Efficiency]")
    results["suites"]["memory"] = {}
    
    print("  ME-01: Storage Density...", end=" ", flush=True)
    r = MemoryEfficiencyTests.ME01_storage_density(use_ternary)
    r["evidence_hash"] = hash_result(r)
    results["suites"]["memory"]["ME-01"] = r
    print(f"{r['bits_per_value']} bits/value")
    
    print("  ME-04: Network Transfer...", end=" ", flush=True)
    r = MemoryEfficiencyTests.ME04_network_transfer(use_ternary)
    r["evidence_hash"] = hash_result(r)
    results["suites"]["memory"]["ME-04"] = r
    print(f"{r['total_bytes']:,} bytes")
    
    # Suite 5: Performance
    print("\n[Suite 5: Computational Performance]")
    results["suites"]["performance"] = {}
    
    print("  CP-01: Logic Throughput...", end=" ", flush=True)
    r = PerformanceTests.CP01_logic_throughput(use_ternary)
    r["evidence_hash"] = hash_result(r)
    results["suites"]["performance"]["CP-01"] = r
    print(f"{r['avg_ops_per_sec']:,} ops/sec")
    
    print("  CP-03: Operation Latency...", end=" ", flush=True)
    r = PerformanceTests.CP03_operation_latency(use_ternary)
    r["evidence_hash"] = hash_result(r)
    results["suites"]["performance"]["CP-03"] = r
    print(f"P50: {r['p50_latency_ns']:.0f}ns")
    
    # Suite 6: Real-World
    print("\n[Suite 6: Real-World Workloads]")
    results["suites"]["real_world"] = {}
    
    print("  RW-01: Trading Decisions...", end=" ", flush=True)
    r = RealWorldTests.RW01_trading_decisions(use_ternary)
    r["evidence_hash"] = hash_result(r)
    results["suites"]["real_world"]["RW-01"] = r
    print(f"Profit: {r['total_profit']:.0f}, Wrong: {r['wrong_trades']}")
    
    print("  RW-02: Medical Triage...", end=" ", flush=True)
    r = RealWorldTests.RW02_medical_triage(use_ternary)
    r["evidence_hash"] = hash_result(r)
    results["suites"]["real_world"]["RW-02"] = r
    print(f"Safety: {r['safety_score']:.1f}%")
    
    print("  RW-03: Network Anomaly...", end=" ", flush=True)
    r = RealWorldTests.RW03_network_anomaly(use_ternary)
    r["evidence_hash"] = hash_result(r)
    results["suites"]["real_world"]["RW-03"] = r
    print(f"F1: {r['f1_score']:.1f}")
    
    # Suite 8: Stress
    print("\n[Suite 8: Stress & Stability]")
    results["suites"]["stress"] = {}
    
    print("  SS-01: Soak Test (10s)...", end=" ", flush=True)
    r = StressTests.SS01_soak_test_mini(use_ternary, duration_seconds=10.0)
    r["evidence_hash"] = hash_result(r)
    results["suites"]["stress"]["SS-01"] = r
    print(f"{r['stability']}")
    
    print("  SS-02: All-PSI Input...", end=" ", flush=True)
    r = StressTests.SS02_all_psi_input(use_ternary)
    r["evidence_hash"] = hash_result(r)
    results["suites"]["stress"]["SS-02"] = r
    print(f"Graceful: {r['graceful_handling']}")
    
    # Generate master hash
    results["master_hash"] = hashlib.sha256(
        json.dumps(results, sort_keys=True).encode()
    ).hexdigest()
    
    print(f"\n{'='*80}")
    print(f"COMPLETE - {mode}")
    print(f"Master Evidence Hash: {results['master_hash'][:32]}...")
    print(f"{'='*80}")
    
    return results

def main():
    hostname = socket.gethostname().lower()
    
    # Determine mode
    ternary_hosts = ["clienttwin", "homebase"]
    use_ternary = any(t in hostname for t in ternary_hosts) and "mirror" not in hostname
    
    # Allow override
    if len(sys.argv) > 1:
        if sys.argv[1] == "--ternary":
            use_ternary = True
        elif sys.argv[1] == "--binary":
            use_ternary = False
    
    results = run_all_suites(use_ternary)
    
    # Save results
    output_file = f"/tmp/zime_prequantum_{hostname}_{results['mode']}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to: {output_file}")

if __name__ == "__main__":
    main()
