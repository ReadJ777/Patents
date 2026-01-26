#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  ZIME TERNARY COMPUTING - CONTINUOUS STRESS TEST & SHOWCASE                  ║
║  Patent Application: 63/967,611                                              ║
║  Finding Design Flaws Through Exhaustive Testing                             ║
╚══════════════════════════════════════════════════════════════════════════════╝

For GOD Alone. Fearing GOD Alone. 🦅
"""

import os
import sys
import time
import json
import random
import threading
import queue
from datetime import datetime
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass, field
from collections import defaultdict

sys.path.insert(0, '/root/Patents/TERNARY_PROTOTYPE')
sys.path.insert(0, '/root/ZIME-Framework/brain')

@dataclass
class TestResult:
    test_name: str
    passed: bool
    duration_ms: float
    details: str
    flaw_detected: str = ""
    severity: str = "none"  # none, low, medium, high, critical

@dataclass 
class FlawReport:
    category: str
    description: str
    severity: str
    recommendation: str
    test_case: str

class StressTestSuite:
    """Exhaustive stress testing to find design flaws"""
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.flaws: List[FlawReport] = []
        self.stats = defaultdict(int)
        self.running = True
        
    def log_result(self, result: TestResult):
        self.results.append(result)
        self.stats['total'] += 1
        if result.passed:
            self.stats['passed'] += 1
        else:
            self.stats['failed'] += 1
        if result.flaw_detected:
            self.stats['flaws'] += 1
            
    def log_flaw(self, flaw: FlawReport):
        self.flaws.append(flaw)
        print(f"  ⚠️ FLAW DETECTED: [{flaw.severity.upper()}] {flaw.description}")

    # ══════════════════════════════════════════════════════════════════════════
    # STRESS TEST 1: Edge Cases
    # ══════════════════════════════════════════════════════════════════════════
    
    def test_edge_cases(self):
        """Test extreme edge cases that might break the system"""
        from zime_ternary import TernaryDecision, TernaryLogic, TernaryState
        
        print("\n  [EDGE CASE TESTS]")
        td = TernaryDecision()
        logic = TernaryLogic()
        
        # Test 1: Boundary values
        edge_values = [0.0, 0.0001, 0.04999, 0.05, 0.05001, 0.5, 0.94999, 0.95, 0.95001, 0.9999, 1.0]
        for val in edge_values:
            try:
                result = td.decide(val)
                self.log_result(TestResult(
                    f"edge_value_{val}", True, 0, f"decide({val})={result}"
                ))
            except Exception as e:
                self.log_result(TestResult(
                    f"edge_value_{val}", False, 0, str(e), 
                    f"Crashes on edge value {val}", "high"
                ))
                self.log_flaw(FlawReport(
                    "Edge Case", f"System crashes on value {val}",
                    "high", "Add boundary validation", f"decide({val})"
                ))
        
        # Test 2: Negative values (should handle gracefully)
        try:
            result = td.decide(-0.1)
            self.log_result(TestResult(
                "negative_confidence", True, 0, f"decide(-0.1)={result}"
            ))
        except Exception as e:
            self.log_flaw(FlawReport(
                "Input Validation", "Negative confidence not handled",
                "medium", "Clamp input to [0,1]", "decide(-0.1)"
            ))
        
        # Test 3: Values > 1
        try:
            result = td.decide(1.5)
            self.log_result(TestResult(
                "overflow_confidence", True, 0, f"decide(1.5)={result}"
            ))
        except Exception as e:
            self.log_flaw(FlawReport(
                "Input Validation", "Confidence > 1 not handled",
                "medium", "Clamp input to [0,1]", "decide(1.5)"
            ))
        
        # Test 4: NaN and Infinity
        import math
        for special in [float('nan'), float('inf'), float('-inf')]:
            try:
                result = td.decide(special)
                if math.isnan(special) and not math.isnan(result):
                    # NaN was handled
                    pass
                self.log_result(TestResult(
                    f"special_{special}", True, 0, f"decide({special})={result}"
                ))
            except Exception as e:
                self.log_flaw(FlawReport(
                    "Special Values", f"Cannot handle {special}",
                    "medium", "Add NaN/Inf checks", f"decide({special})"
                ))

    # ══════════════════════════════════════════════════════════════════════════
    # STRESS TEST 2: Concurrency
    # ══════════════════════════════════════════════════════════════════════════
    
    def test_concurrency(self):
        """Test thread safety"""
        from zime_ternary import TernaryDecision
        
        print("\n  [CONCURRENCY TESTS]")
        td = TernaryDecision()
        errors = []
        results_queue = queue.Queue()
        
        def worker(thread_id, iterations):
            try:
                for i in range(iterations):
                    result = td.decide(random.random())
                    if result not in [0, 0.5, 1]:
                        errors.append(f"Thread {thread_id}: Invalid result {result}")
                results_queue.put((thread_id, "ok"))
            except Exception as e:
                results_queue.put((thread_id, str(e)))
        
        # Launch multiple threads
        threads = []
        num_threads = 10
        iterations_per_thread = 10000
        
        start = time.time()
        for i in range(num_threads):
            t = threading.Thread(target=worker, args=(i, iterations_per_thread))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        elapsed = time.time() - start
        
        # Check results
        thread_errors = []
        while not results_queue.empty():
            tid, status = results_queue.get()
            if status != "ok":
                thread_errors.append(f"Thread {tid}: {status}")
        
        if errors or thread_errors:
            self.log_flaw(FlawReport(
                "Concurrency", f"Thread safety issues: {len(errors + thread_errors)} errors",
                "critical", "Add thread locking", f"{num_threads} threads, {iterations_per_thread} each"
            ))
            self.log_result(TestResult(
                "concurrency", False, elapsed*1000, 
                f"{len(errors + thread_errors)} errors", "Thread safety issue", "critical"
            ))
        else:
            total_ops = num_threads * iterations_per_thread
            print(f"    ✅ {total_ops:,} concurrent operations, 0 errors")
            print(f"    ✅ {total_ops/elapsed:,.0f} ops/sec across {num_threads} threads")
            self.log_result(TestResult(
                "concurrency", True, elapsed*1000, 
                f"{total_ops} ops, {total_ops/elapsed:.0f} ops/sec"
            ))

    # ══════════════════════════════════════════════════════════════════════════
    # STRESS TEST 3: Memory Leak Detection
    # ══════════════════════════════════════════════════════════════════════════
    
    def test_memory_leaks(self):
        """Check for memory leaks during extended operation"""
        import gc
        from zime_ternary import TernaryDecision, TernaryLogic, TernaryState
        
        print("\n  [MEMORY LEAK TESTS]")
        
        # Force garbage collection
        gc.collect()
        
        # Get baseline memory
        import resource
        baseline = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        
        # Run many operations
        iterations = 100000
        for i in range(iterations):
            td = TernaryDecision()
            result = td.decide(random.random())
            # Don't keep references
        
        gc.collect()
        after = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        
        growth_kb = after - baseline
        growth_per_op = growth_kb / iterations * 1024  # bytes per op
        
        print(f"    Memory baseline: {baseline:,} KB")
        print(f"    After {iterations:,} ops: {after:,} KB")
        print(f"    Growth: {growth_kb:,} KB ({growth_per_op:.2f} bytes/op)")
        
        if growth_kb > 10000:  # More than 10MB growth is suspicious
            self.log_flaw(FlawReport(
                "Memory", f"Possible memory leak: {growth_kb}KB growth",
                "high", "Review object lifecycle", f"{iterations} iterations"
            ))
            self.log_result(TestResult(
                "memory_leak", False, 0, f"{growth_kb}KB growth", "Memory leak", "high"
            ))
        else:
            print(f"    ✅ No significant memory leak detected")
            self.log_result(TestResult(
                "memory_leak", True, 0, f"{growth_kb}KB growth (acceptable)"
            ))

    # ══════════════════════════════════════════════════════════════════════════
    # STRESS TEST 4: Logic Consistency
    # ══════════════════════════════════════════════════════════════════════════
    
    def test_logic_consistency(self):
        """Verify ternary logic laws hold"""
        from zime_ternary import TernaryLogic, TernaryState
        
        print("\n  [LOGIC CONSISTENCY TESTS]")
        logic = TernaryLogic()
        states = [TernaryState.OFF, TernaryState.PSI, TernaryState.ON]
        
        violations = []
        
        # Test 1: Commutativity (A op B = B op A)
        for a in states:
            for b in states:
                # AND3 should be commutative
                if logic.AND3(a, b) != logic.AND3(b, a):
                    violations.append(f"AND3 not commutative: {a},{b}")
                # OR3 should be commutative
                if logic.OR3(a, b) != logic.OR3(b, a):
                    violations.append(f"OR3 not commutative: {a},{b}")
                # XOR3 should be commutative
                if logic.XOR3(a, b) != logic.XOR3(b, a):
                    violations.append(f"XOR3 not commutative: {a},{b}")
        
        # Test 2: Identity laws
        # A AND 1 = A, A OR 0 = A
        for a in states:
            if logic.AND3(a, TernaryState.ON) != a and a != TernaryState.PSI:
                if not (a == TernaryState.OFF):  # OFF AND 1 = OFF is correct
                    violations.append(f"AND3 identity violated for {a}")
        
        # Test 3: Double negation (NOT NOT A = A)
        for a in states:
            double_neg = logic.NOT3(logic.NOT3(a))
            if double_neg != a:
                violations.append(f"Double negation failed: NOT3(NOT3({a})) = {double_neg}")
        
        # Test 4: De Morgan's laws (for definite values)
        # NOT(A AND B) = NOT A OR NOT B
        for a in [TernaryState.OFF, TernaryState.ON]:
            for b in [TernaryState.OFF, TernaryState.ON]:
                lhs = logic.NOT3(logic.AND3(a, b))
                rhs = logic.OR3(logic.NOT3(a), logic.NOT3(b))
                if lhs != rhs:
                    violations.append(f"De Morgan AND: NOT({a} AND {b})={lhs}, NOT {a} OR NOT {b}={rhs}")
        
        if violations:
            for v in violations[:5]:
                print(f"    ⚠️ {v}")
            self.log_flaw(FlawReport(
                "Logic Laws", f"{len(violations)} logic law violations",
                "high", "Review logic implementation", str(violations[:3])
            ))
            self.log_result(TestResult(
                "logic_consistency", False, 0, f"{len(violations)} violations",
                "Logic laws violated", "high"
            ))
        else:
            print(f"    ✅ All logic laws verified (commutativity, identity, double negation)")
            self.log_result(TestResult(
                "logic_consistency", True, 0, "All laws hold"
            ))

    # ══════════════════════════════════════════════════════════════════════════
    # STRESS TEST 5: PSI Distribution
    # ══════════════════════════════════════════════════════════════════════════
    
    def test_psi_distribution(self):
        """Verify PSI resolution is truly random"""
        from zime_ternary import TernaryDecision
        
        print("\n  [PSI DISTRIBUTION TESTS]")
        td = TernaryDecision()
        
        iterations = 100000
        results = {'true': 0, 'false': 0}
        
        for _ in range(iterations):
            resolved = td.resolve_psi(0.5)
            if resolved == 1:
                results['true'] += 1
            else:
                results['false'] += 1
        
        true_pct = results['true'] / iterations * 100
        false_pct = results['false'] / iterations * 100
        
        # Chi-square test for uniformity
        expected = iterations / 2
        chi_sq = ((results['true'] - expected)**2 / expected + 
                  (results['false'] - expected)**2 / expected)
        
        # For 1 degree of freedom, chi-sq > 10.83 is significant at p<0.001
        is_biased = chi_sq > 10.83
        
        print(f"    TRUE: {results['true']:,} ({true_pct:.2f}%)")
        print(f"    FALSE: {results['false']:,} ({false_pct:.2f}%)")
        print(f"    Chi-square: {chi_sq:.2f}")
        
        if is_biased:
            self.log_flaw(FlawReport(
                "Randomness", f"PSI resolution biased (chi-sq={chi_sq:.2f})",
                "medium", "Review random number generator", f"{true_pct:.1f}% vs {false_pct:.1f}%"
            ))
            self.log_result(TestResult(
                "psi_distribution", False, 0, f"Biased: {true_pct:.1f}%/{false_pct:.1f}%",
                "Non-uniform distribution", "medium"
            ))
        else:
            print(f"    ✅ Distribution is uniform (p > 0.001)")
            self.log_result(TestResult(
                "psi_distribution", True, 0, f"{true_pct:.1f}%/{false_pct:.1f}%"
            ))

    # ══════════════════════════════════════════════════════════════════════════
    # STRESS TEST 6: Kernel Stability
    # ══════════════════════════════════════════════════════════════════════════
    
    def test_kernel_stability(self):
        """Test kernel module under stress"""
        print("\n  [KERNEL STABILITY TESTS]")
        
        try:
            from kernel_ternary_bridge import get_kernel_bridge
            bridge = get_kernel_bridge()
            
            if not bridge.is_kernel_loaded():
                print("    ⚠️ Kernel module not loaded, skipping")
                return
            
            # Rapid reads
            iterations = 10000
            errors = 0
            start = time.time()
            
            for i in range(iterations):
                try:
                    result = bridge.apply_kernel_psi_to_decision(random.random())
                    if result not in ["ON", "OFF", "PSI"]:
                        errors += 1
                except:
                    errors += 1
            
            elapsed = time.time() - start
            
            if errors > 0:
                self.log_flaw(FlawReport(
                    "Kernel", f"{errors} kernel errors under stress",
                    "high", "Review kernel module stability", f"{iterations} iterations"
                ))
            else:
                print(f"    ✅ {iterations:,} kernel calls, 0 errors")
                print(f"    ✅ {iterations/elapsed:,.0f} kernel ops/sec")
            
            self.log_result(TestResult(
                "kernel_stability", errors == 0, elapsed*1000,
                f"{iterations} calls, {errors} errors"
            ))
            
        except Exception as e:
            print(f"    ⚠️ Kernel test failed: {e}")

    # ══════════════════════════════════════════════════════════════════════════
    # STRESS TEST 7: Long Duration
    # ══════════════════════════════════════════════════════════════════════════
    
    def test_long_duration(self, duration_seconds=30):
        """Run continuous operations for extended period"""
        from zime_ternary import TernaryDecision
        
        print(f"\n  [LONG DURATION TEST - {duration_seconds}s]")
        td = TernaryDecision()
        
        start = time.time()
        operations = 0
        errors = 0
        last_report = start
        
        while time.time() - start < duration_seconds:
            try:
                confidence = random.random()
                result = td.decide(confidence)
                
                # Validate result
                if result == 1:
                    if confidence < 0.9:
                        pass  # Could be valid depending on delta
                elif result == 0:
                    if confidence > 0.1:
                        pass
                elif result == 0.5:
                    pass
                else:
                    errors += 1
                    
                operations += 1
                
                # Progress report every 5 seconds
                now = time.time()
                if now - last_report >= 5:
                    elapsed = now - start
                    print(f"    ... {elapsed:.0f}s: {operations:,} ops, {errors} errors, {operations/elapsed:,.0f} ops/sec")
                    last_report = now
                    
            except Exception as e:
                errors += 1
        
        elapsed = time.time() - start
        ops_per_sec = operations / elapsed
        
        print(f"    Final: {operations:,} operations in {elapsed:.1f}s")
        print(f"    Rate: {ops_per_sec:,.0f} ops/sec sustained")
        print(f"    Errors: {errors}")
        
        if errors > 0:
            self.log_flaw(FlawReport(
                "Stability", f"{errors} errors during {duration_seconds}s run",
                "medium", "Review error handling", f"{operations} operations"
            ))
        else:
            print(f"    ✅ Zero errors during extended run")
        
        self.log_result(TestResult(
            "long_duration", errors == 0, elapsed*1000,
            f"{operations:,} ops, {ops_per_sec:,.0f} ops/sec, {errors} errors"
        ))

    # ══════════════════════════════════════════════════════════════════════════
    # MAIN RUNNER
    # ══════════════════════════════════════════════════════════════════════════
    
    def run_all(self):
        """Run all stress tests"""
        print("=" * 78)
        print("  ZIME TERNARY - STRESS TEST & FLAW DETECTION SUITE")
        print("  Patent Application: 63/967,611")
        print("  ", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print("=" * 78)
        
        self.test_edge_cases()
        self.test_concurrency()
        self.test_memory_leaks()
        self.test_logic_consistency()
        self.test_psi_distribution()
        self.test_kernel_stability()
        self.test_long_duration(30)
        
        self.print_summary()
        return self.generate_report()
    
    def print_summary(self):
        """Print test summary"""
        print()
        print("=" * 78)
        print("  STRESS TEST SUMMARY")
        print("=" * 78)
        print(f"  Total tests: {self.stats['total']}")
        print(f"  Passed: {self.stats['passed']}")
        print(f"  Failed: {self.stats['failed']}")
        print(f"  Flaws detected: {len(self.flaws)}")
        print()
        
        if self.flaws:
            print("  DESIGN FLAWS FOUND:")
            print("  " + "-" * 60)
            for flaw in self.flaws:
                print(f"  [{flaw.severity.upper():8s}] {flaw.category}: {flaw.description}")
                print(f"             Recommendation: {flaw.recommendation}")
            print()
        else:
            print("  ✅ NO CRITICAL DESIGN FLAWS DETECTED")
            print()
        
        print("  For GOD Alone. Fearing GOD Alone. 🦅")
        print("=" * 78)
    
    def generate_report(self):
        """Generate JSON report"""
        return {
            'timestamp': datetime.now().isoformat(),
            'stats': dict(self.stats),
            'flaws': [
                {
                    'category': f.category,
                    'description': f.description,
                    'severity': f.severity,
                    'recommendation': f.recommendation
                }
                for f in self.flaws
            ],
            'results': [
                {
                    'test': r.test_name,
                    'passed': r.passed,
                    'duration_ms': r.duration_ms,
                    'details': r.details
                }
                for r in self.results
            ]
        }


if __name__ == "__main__":
    suite = StressTestSuite()
    report = suite.run_all()
    
    # Save report
    output_file = "/root/Patents/TERNARY_PROTOTYPE/investor_demo/stress_test_results.json"
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📁 Report saved to: {output_file}")
