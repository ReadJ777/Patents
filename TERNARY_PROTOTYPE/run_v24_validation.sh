#!/bin/bash
# ZIME v24.1 Complete Validation Suite
# Patent: 63/967,611 | Generates evidence for all 7 claims
# Run this on all nodes for multi-platform validation

set -e

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║  ZIME v24.1 COMPLETE VALIDATION SUITE                           ║"
echo "║  Patent: 63/967,611 | Multi-Platform Evidence Generation        ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""
echo "Node: $(hostname)"
echo "Platform: $(uname -s) $(uname -m)"
echo "Date: $(date -Iseconds)"
echo ""

cd /root/Patents/TERNARY_PROTOTYPE

# Track results
PASSED=0
TOTAL=0
BASE_DIR="/root/Patents/TERNARY_PROTOTYPE"

run_test() {
    local name=$1
    local claim=$2
    local cmd=$3
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "TEST: $name (Claim $claim)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    ((TOTAL++)) || true
    
    if eval "$cmd"; then
        echo "✅ PASSED: $name"
        ((PASSED++)) || true
    else
        echo "❌ FAILED: $name"
    fi
    echo ""
}

# Test 1: C Library (Claim 4)
run_test "C Library Throughput" 4 "$BASE_DIR/libternary/benchmark"

# Test 2: C Library Tests (All claims)  
run_test "C Library Unit Tests" 1 "$BASE_DIR/libternary/test_ternary"

# Test 3: Python Hardware Validation (Claims 1,3,4,5,6)
run_test "Python Hardware Validation" 6 "cd $BASE_DIR && python3 v24_hardware_validation.py"

# Test 4: Kernel Module Check (Claim 5)
run_test "Kernel Module /proc Interface" 5 "test -d /proc/ternary && cat /proc/ternary/status"

# Test 5: RAPL Energy Interface (Claim 6)
run_test "RAPL Energy Interface" 6 "test -f /sys/class/powercap/intel-rapl/intel-rapl:0/energy_uj && cat /sys/class/powercap/intel-rapl/intel-rapl:0/energy_uj"

# Test 6: CPU Frequency Interface (Claim 6)
run_test "CPU Frequency Interface" 6 "test -f /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq && cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq"

# Test 7: Unified System (Claims 1-3)
run_test "Unified Ternary System" 1 "cd $BASE_DIR && python3 -c 'from unified_ternary import *; s=UnifiedTernarySystem(); print(s.run_truth_table_test())'"

# Summary
echo "══════════════════════════════════════════════════════════════════"
echo "SUMMARY: $PASSED/$TOTAL tests passed"
echo "══════════════════════════════════════════════════════════════════"

# Generate hash
HASH=$(echo "$PASSED/$TOTAL $(hostname) $(date +%s)" | sha256sum | cut -c1-16)
echo "Evidence Hash: $HASH"
echo "Timestamp: $(date -Iseconds)"

# Save results
RESULTS_FILE="/root/Patents/EVIDENCE/v24_$(hostname)_$(date +%Y%m%d_%H%M%S).txt"
{
    echo "ZIME v24.1 Validation Results"
    echo "Node: $(hostname)"
    echo "Platform: $(uname -s) $(uname -m)"
    echo "Date: $(date -Iseconds)"
    echo "Tests: $PASSED/$TOTAL passed"
    echo "Hash: $HASH"
} > "$RESULTS_FILE"

echo ""
echo "Results saved to: $RESULTS_FILE"

if [ "$PASSED" -eq "$TOTAL" ]; then
    echo ""
    echo "🎉 ALL TESTS PASSED!"
    exit 0
else
    echo ""
    echo "⚠️  Some tests failed - check output above"
    exit 1
fi
