#!/usr/bin/env python3
"""
ZIME v23.0 Complete Test Suite
Patent #63/967,611
"""
import os, sys, time, random, hashlib, socket
from datetime import datetime

class TernaryV23:
    BINARY_0, PSI, BINARY_1 = 0, 1, 2
    
    def __init__(self, threshold=0.5, delta=0.05, alpha=0.1, timeout_ms=1000):
        self.threshold, self.delta, self.alpha = threshold, delta, alpha
        self.timeout_ms, self.safe_default = timeout_ms, self.BINARY_0
        self.prev_confidence, self.timeout_count = 0.5, 0
        self.deferral_queue = []
    
    def normalize(self, raw):
        return min(1.0, max(0.0, raw / 0xFFFFFFFF))
    
    def ewma(self, x, prev, alpha):
        return alpha * x + (1 - alpha) * prev
    
    def apply_penalty(self, conf, density):
        penalty = max(0, (density - 0.5) * 2)
        return conf * (1 - penalty) + 0.5 * penalty
    
    def classify_direct(self, c):
        if c < self.threshold - self.delta: return 0
        elif c > self.threshold + self.delta: return 2
        else: return 1
    
    def classify(self, raw, transition_count=0, use_ewma=True):
        n = self.normalize(raw) if isinstance(raw, int) else raw
        s = self.ewma(n, self.prev_confidence, self.alpha) if use_ewma else n
        if use_ewma: self.prev_confidence = s
        c = self.apply_penalty(s, min(1.0, transition_count / 100.0))
        return (0 if c < self.threshold - self.delta else 2 if c > self.threshold + self.delta else 1), c
    
    def defer(self, raw):
        self.deferral_queue.append((time.time() * 1000, raw))
    
    def resolve_deferred(self):
        now = time.time() * 1000
        results, remaining = [], []
        for start, raw in self.deferral_queue:
            if now - start > self.timeout_ms:
                self.timeout_count += 1
                results.append((raw, self.safe_default, 'TIMEOUT'))
            else:
                remaining.append((start, raw))
        self.deferral_queue = remaining
        return results


def run_tests():
    passed = failed = 0
    hostname = socket.gethostname()
    
    def test(name, ok):
        nonlocal passed, failed
        print(f"  {'✓' if ok else '✗'} {name}")
        if ok: passed += 1
        else: failed += 1
    
    print(f"\n{'═'*60}")
    print(f" V23.0 COMPLETE TEST SUITE - {hostname}")
    print(f"{'═'*60}")
    
    # 1. Normalization
    print(f"\n[1] NORMALIZATION")
    c = TernaryV23()
    test("normalize(0) = 0.0", c.normalize(0) == 0.0)
    test("normalize(MAX) = 1.0", c.normalize(0xFFFFFFFF) == 1.0)
    
    # 2. EWMA
    print(f"\n[2] EWMA SMOOTHING")
    test("ewma(1.0, 0.0, 0.1) = 0.1", abs(c.ewma(1.0, 0.0, 0.1) - 0.1) < 0.001)
    test("ewma(0.0, 1.0, 0.1) = 0.9", abs(c.ewma(0.0, 1.0, 0.1) - 0.9) < 0.001)
    
    # 3. Density penalty
    print(f"\n[3] DENSITY PENALTY")
    test("density=0 → no penalty", abs(c.apply_penalty(0.8, 0) - 0.8) < 0.001)
    test("density=1 → full penalty", abs(c.apply_penalty(0.8, 1.0) - 0.5) < 0.001)
    
    # 4. Direct classifier
    print(f"\n[4] DIRECT CLASSIFIER (v22 compatible)")
    c = TernaryV23(threshold=0.5, delta=0.10)
    test("0.1 → BINARY_0", c.classify_direct(0.1) == 0)
    test("0.5 → PSI", c.classify_direct(0.5) == 1)
    test("0.9 → BINARY_1", c.classify_direct(0.9) == 2)
    
    # 5. EWMA classifier
    print(f"\n[5] EWMA CLASSIFIER (v23 new)")
    c = TernaryV23(threshold=0.5, delta=0.10)
    c.prev_confidence = 0.5
    state, conf = c.classify(0.1, use_ewma=True)
    test(f"EWMA smooths 0.1→{conf:.2f}", 0.3 < conf < 0.5)
    
    # 6. Deferral timeout
    print(f"\n[6] DEFERRAL TIMEOUT")
    c = TernaryV23(timeout_ms=1)
    c.deferral_queue = [(0, 0.5), (0, 0.6)]  # Already timed out
    time.sleep(0.01)
    results = c.resolve_deferred()
    test("Timeout returns SAFE_DEFAULT", len(results) == 2 and all(r[1] == 0 for r in results))
    test("timeout_count = 2", c.timeout_count == 2)
    
    # 7. v22 backward compatibility
    print(f"\n[7] v22 BACKWARD COMPATIBILITY")
    c = TernaryV23(threshold=0.5, delta=0.05)
    results = [c.classify_direct(i/100) for i in range(101)]
    h = hashlib.md5(str(results).encode()).hexdigest()
    test(f"v22 hash: {h[:16]}...", h == "ba29e28bfecb5d2fe5ba18a0ec073d83")
    
    # 8. /proc interface
    print(f"\n[8] /PROC INTERFACE")
    for p in ['/proc/ternary', '/var/run/ternary', '/tmp/ternary']:
        if os.path.isdir(p):
            test(f"Interface at {p}", True)
            break
    else:
        test("Interface exists", False)
    
    # Summary
    total = passed + failed
    print(f"\n{'═'*60}")
    print(f" V23.0 RESULTS: {passed}/{total} passed ({100*passed//total}%)")
    print(f"{'═'*60}")
    if failed == 0:
        print(" ✅ V23.0 FULLY VALIDATED")
    print(f"{'═'*60}\n")
    
    return failed == 0

if __name__ == '__main__':
    sys.exit(0 if run_tests() else 1)
