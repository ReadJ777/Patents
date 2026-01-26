#!/usr/bin/env python3
"""
ZIME Ternary GPU Computing - Pure Python Demo
Patent Application: 63/967,611 (GPU Expansion)
Copyright (c) 2026 JaKaiser Smith
For GOD Alone. Fearing GOD Alone.
"""

import random
import math

# Trit encoding
TRIT_ZERO = 0b00
TRIT_NEG = 0b01
TRIT_POS = 0b10
TRIT_PSI = 0b11

TRIT_NAMES = {
    TRIT_ZERO: "0",
    TRIT_NEG: "-1",
    TRIT_POS: "+1",
    TRIT_PSI: "Ψ"
}

class TernaryTensor:
    """Ternary tensor with Ψ-state support"""
    
    def __init__(self, shape):
        self.shape = shape
        self.size = 1
        for s in shape:
            self.size *= s
        
        # Storage: list of (trit_value, psi_probability)
        self.data = [(TRIT_ZERO, 0.5) for _ in range(self.size)]
    
    @classmethod
    def from_floats(cls, values, threshold=0.5, psi_zone=0.2):
        """Convert float values to ternary with Ψ for uncertain"""
        flat = values if isinstance(values, list) else [values]
        tt = cls((len(flat),))
        
        for i, val in enumerate(flat):
            if val > threshold:
                tt.data[i] = (TRIT_POS, 1.0)
            elif val < -threshold:
                tt.data[i] = (TRIT_NEG, 0.0)
            elif abs(val) < psi_zone:
                tt.data[i] = (TRIT_ZERO, 0.5)
            else:
                # Uncertain zone → Ψ state
                prob = (val + threshold) / (2 * threshold)
                tt.data[i] = (TRIT_PSI, prob)
        
        return tt
    
    def to_floats(self):
        """Convert to float values"""
        result = []
        for trit, prob in self.data:
            if trit == TRIT_POS:
                result.append(1.0)
            elif trit == TRIT_NEG:
                result.append(-1.0)
            elif trit == TRIT_PSI:
                result.append(prob)  # Show probability
            else:
                result.append(0.0)
        return result
    
    def count_psi(self):
        """Count Ψ states"""
        return sum(1 for t, _ in self.data if t == TRIT_PSI)
    
    def resolve_psi(self):
        """Resolve all Ψ states probabilistically"""
        for i, (trit, prob) in enumerate(self.data):
            if trit == TRIT_PSI:
                resolved = TRIT_POS if random.random() < prob else TRIT_NEG
                self.data[i] = (resolved, prob)
        return self
    
    def __str__(self):
        return "[" + ", ".join(TRIT_NAMES[t] for t, _ in self.data) + "]"


def ternary_matmul(A, B):
    """Ternary matrix multiplication"""
    # A is m x k, B is k x n
    m, k1 = len(A), len(A[0])
    k2, n = len(B), len(B[0])
    assert k1 == k2, "Dimension mismatch"
    
    C = [[0 for _ in range(n)] for _ in range(m)]
    
    for i in range(m):
        for j in range(n):
            total = 0
            for k in range(k1):
                a_trit, _ = A[i][k]
                b_trit, _ = B[k][j]
                
                # Ternary multiply
                a_val = {TRIT_POS: 1, TRIT_NEG: -1, TRIT_ZERO: 0, TRIT_PSI: 0}[a_trit]
                b_val = {TRIT_POS: 1, TRIT_NEG: -1, TRIT_ZERO: 0, TRIT_PSI: 0}[b_trit]
                total += a_val * b_val
            
            C[i][j] = total
    
    return C


def demo():
    print()
    print("╔══════════════════════════════════════════════════════╗")
    print("║  ZIME TERNARY GPU COMPUTING - Demo                   ║")
    print("║  Patent Application: 63/967,611                      ║")
    print("║  For GOD Alone. Fearing GOD Alone.                   ║")
    print("╚══════════════════════════════════════════════════════╝")
    print()
    
    # Test 1: Basic ternary conversion
    print("=== Test 1: Float to Ternary Conversion ===")
    values = [0.8, -0.7, 0.05, 0.3, -0.3, 0.0]
    print(f"Input floats: {values}")
    
    tt = TernaryTensor.from_floats(values, threshold=0.5, psi_zone=0.1)
    print(f"Ternary:      {tt}")
    print(f"Ψ count:      {tt.count_psi()}")
    print()
    
    # Test 2: Psi resolution
    print("=== Test 2: Ψ-State Resolution ===")
    print(f"Before: {tt}")
    tt.resolve_psi()
    print(f"After:  {tt}")
    print()
    
    # Test 3: Ternary matrix multiply
    print("=== Test 3: Ternary Matrix Multiplication ===")
    
    # 2x3 matrix
    A = [
        [(TRIT_POS, 1.0), (TRIT_NEG, 0.0), (TRIT_ZERO, 0.5)],
        [(TRIT_ZERO, 0.5), (TRIT_POS, 1.0), (TRIT_NEG, 0.0)]
    ]
    
    # 3x2 matrix
    B = [
        [(TRIT_POS, 1.0), (TRIT_ZERO, 0.5)],
        [(TRIT_NEG, 0.0), (TRIT_POS, 1.0)],
        [(TRIT_POS, 1.0), (TRIT_NEG, 0.0)]
    ]
    
    print("A (2x3):")
    for row in A:
        print("  [" + ", ".join(TRIT_NAMES[t] for t, _ in row) + "]")
    
    print("B (3x2):")
    for row in B:
        print("  [" + ", ".join(TRIT_NAMES[t] for t, _ in row) + "]")
    
    C = ternary_matmul(A, B)
    print("C = A × B (2x2):")
    for row in C:
        print(f"  {row}")
    print()
    
    # Test 4: Memory savings
    print("=== Test 4: Memory Comparison ===")
    n = 1000000  # 1M weights
    float32_size = n * 4  # 4 bytes per float
    ternary_size = (n * 2 + 7) // 8  # 2 bits per trit
    
    print(f"Weights: {n:,}")
    print(f"Float32: {float32_size:,} bytes ({float32_size/1024/1024:.2f} MB)")
    print(f"Ternary: {ternary_size:,} bytes ({ternary_size/1024/1024:.2f} MB)")
    print(f"Savings: {float32_size/ternary_size:.1f}x smaller!")
    print()
    
    # Test 5: Uncertainty demo
    print("=== Test 5: Uncertainty-Aware Inference ===")
    
    # Simulate a classifier with uncertainty
    confidence_scores = [0.9, 0.7, 0.3, 0.1]  # High to low confidence
    
    for conf in confidence_scores:
        # Convert to ternary: high confidence → ±1, low → Ψ
        if conf > 0.7:
            decision = "ACCEPT (+1)"
            state = "certain"
        elif conf < 0.3:
            decision = "REJECT (-1)"
            state = "certain"
        else:
            decision = "DEFER (Ψ)"
            state = "uncertain"
        
        print(f"  Confidence {conf:.1f} → {decision} [{state}]")
    
    print()
    print("╔══════════════════════════════════════════════════════╗")
    print("║  ✅ GPU Ternary Computing Demo Complete!             ║")
    print("║  For GOD Alone. Fearing GOD Alone. 🦅                ║")
    print("╚══════════════════════════════════════════════════════╝")


if __name__ == "__main__":
    demo()
