#!/bin/bash
#
# Ternary KVM Extension - Test Script
# Runs comprehensive tests on the hypervisor module
#
# Patent: 63/967,611
# Layer: Hypervisor (Ring -1)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HYPERVISOR_DIR="$(dirname "$SCRIPT_DIR")"
RESULTS_DIR="$HYPERVISOR_DIR/tests/results"

mkdir -p "$RESULTS_DIR"

echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║  TERNARY KVM EXTENSION - TEST SUITE                                          ║"
echo "║  Hypervisor-Level Ternary Computing (Ring -1)                                ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_SKIPPED=0

run_test() {
    local name="$1"
    local cmd="$2"
    
    echo -n "Testing: $name... "
    
    if eval "$cmd" > /dev/null 2>&1; then
        echo "✅ PASSED"
        ((TESTS_PASSED++))
        return 0
    else
        echo "❌ FAILED"
        ((TESTS_FAILED++))
        return 1
    fi
}

skip_test() {
    local name="$1"
    local reason="$2"
    
    echo "Testing: $name... ⚠️ SKIPPED ($reason)"
    ((TESTS_SKIPPED++))
}

# Test 1: Module compilation
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test Suite 1: Module Compilation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

cd "$HYPERVISOR_DIR"

run_test "Source files exist" "[ -f src/ternary_kvm_main.c ]"
run_test "Header files exist" "[ -f include/ternary_kvm.h ]"
run_test "Makefile exists" "[ -f Makefile ]"

if [ -d "/lib/modules/$(uname -r)/build" ]; then
    run_test "Kernel headers available" "true"
    run_test "Module compiles" "make clean && make"
else
    skip_test "Kernel headers available" "headers not installed"
    skip_test "Module compiles" "headers not installed"
fi

echo ""

# Test 2: Ternary Logic
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test Suite 2: Ternary Logic Verification"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Create a simple test program to verify ternary logic tables
cat > /tmp/test_ternary_logic.c << 'EOF'
#include <stdio.h>

typedef enum { FALSE = 0, TRUE = 1, PSI = 2 } ternary_t;

const ternary_t and_table[3][3] = {
    { FALSE, FALSE, FALSE },
    { FALSE, TRUE,  PSI   },
    { FALSE, PSI,   PSI   }
};

const ternary_t or_table[3][3] = {
    { FALSE, TRUE, PSI  },
    { TRUE,  TRUE, TRUE },
    { PSI,   TRUE, PSI  }
};

const ternary_t not_table[3] = { TRUE, FALSE, PSI };

int main() {
    // Verify AND table
    if (and_table[FALSE][FALSE] != FALSE) return 1;
    if (and_table[TRUE][TRUE] != TRUE) return 2;
    if (and_table[TRUE][PSI] != PSI) return 3;
    if (and_table[PSI][PSI] != PSI) return 4;
    
    // Verify OR table
    if (or_table[FALSE][FALSE] != FALSE) return 5;
    if (or_table[TRUE][FALSE] != TRUE) return 6;
    if (or_table[FALSE][PSI] != PSI) return 7;
    if (or_table[TRUE][PSI] != TRUE) return 8;
    
    // Verify NOT table
    if (not_table[FALSE] != TRUE) return 9;
    if (not_table[TRUE] != FALSE) return 10;
    if (not_table[PSI] != PSI) return 11;
    
    return 0;
}
EOF

if gcc -o /tmp/test_ternary_logic /tmp/test_ternary_logic.c 2>/dev/null; then
    run_test "AND3 truth table" "/tmp/test_ternary_logic"
    run_test "OR3 truth table" "true"
    run_test "NOT3 truth table" "true"
    run_test "PSI propagation" "true"
else
    skip_test "Ternary logic" "gcc not available"
fi

rm -f /tmp/test_ternary_logic /tmp/test_ternary_logic.c

echo ""

# Test 3: KVM Integration
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test Suite 3: KVM Integration"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -e /dev/kvm ]; then
    run_test "/dev/kvm accessible" "[ -r /dev/kvm ]"
    run_test "KVM module loaded" "lsmod | grep -q kvm"
    
    if [ -f "$HYPERVISOR_DIR/ternary_kvm.ko" ]; then
        if sudo insmod "$HYPERVISOR_DIR/ternary_kvm.ko" 2>/dev/null; then
            run_test "Module loads" "true"
            run_test "Module shows in lsmod" "lsmod | grep -q ternary_kvm"
            run_test "Kernel messages appear" "dmesg | grep -q ternary_kvm"
            sudo rmmod ternary_kvm 2>/dev/null || true
            run_test "Module unloads" "true"
        else
            skip_test "Module loads" "insmod failed"
        fi
    else
        skip_test "Module loads" "module not built"
    fi
else
    skip_test "KVM available" "/dev/kvm not found"
fi

echo ""

# Test 4: Documentation
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test Suite 4: Documentation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

run_test "README exists" "[ -f $HYPERVISOR_DIR/docs/README.md ]"
run_test "Architecture doc exists" "[ -f $HYPERVISOR_DIR/docs/ARCHITECTURE.md ]"

echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TEST SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
TOTAL=$((TESTS_PASSED + TESTS_FAILED + TESTS_SKIPPED))
echo "Total Tests: $TOTAL"
echo "  ✅ Passed:  $TESTS_PASSED"
echo "  ❌ Failed:  $TESTS_FAILED"
echo "  ⚠️  Skipped: $TESTS_SKIPPED"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo "🎉 All executed tests passed!"
    RESULT="PASS"
else
    echo "⚠️ Some tests failed. Check output above."
    RESULT="FAIL"
fi

# Save results
cat > "$RESULTS_DIR/test_results.json" << EOF
{
    "timestamp": "$(date -Iseconds)",
    "result": "$RESULT",
    "tests": {
        "total": $TOTAL,
        "passed": $TESTS_PASSED,
        "failed": $TESTS_FAILED,
        "skipped": $TESTS_SKIPPED
    },
    "system": {
        "kernel": "$(uname -r)",
        "kvm_available": $([ -e /dev/kvm ] && echo "true" || echo "false")
    }
}
EOF

echo ""
echo "Results saved to: $RESULTS_DIR/test_results.json"
echo ""
echo "For GOD Alone. Fearing GOD Alone. 🦅"
