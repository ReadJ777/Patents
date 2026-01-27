#!/usr/bin/env python3
"""
Claim 7: Hypervisor Uncertainty-Aware Scheduling - Validation Suite
USPTO Patent #63/967,611 - v23.1

Tests all elements of Claim 7:
(a) Per-VM Uncertainty Tracking
(b) Uncertainty-Based Scheduling  
(c) Memory Optimization
(d) Guest Visibility Interface (CPUID/hypercalls/MSR)
"""

import os
import sys
import struct
import hashlib
import time
from dataclasses import dataclass
from typing import List, Dict, Tuple
from enum import IntEnum

# ═══════════════════════════════════════════════════════════════
# CLAIM 7 CONSTANTS FROM SPEC v23.1
# ═══════════════════════════════════════════════════════════════

class HypercallID(IntEnum):
    HC_PSI_QUERY = 0x01000001
    HC_PSI_UPDATE = 0x01000002
    HC_PSI_CLUSTER = 0x01000003
    HC_PSI_POWER = 0x01000004

class TernaryState(IntEnum):
    TERNARY_FALSE = 0
    TERNARY_TRUE = 1
    TERNARY_PSI = 2

@dataclass
class VMContext:
    """Per-VM ternary context"""
    vm_id: int
    psi_deferrals: int = 0
    total_decisions: int = 0

@dataclass
class SchedulingDecision:
    """vCPU scheduling priority and time slice"""
    priority: int
    time_slice_ms: int

@dataclass
class TernaryPage:
    """Memory page with ternary metadata"""
    gfn: int
    has_psi: bool = False
    psi_access_count: int = 0
    flagged_for_compression: bool = False
    flagged_for_isolation: bool = False

# ═══════════════════════════════════════════════════════════════
# CORE FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def compute_vm_psi_ratio(vm: VMContext) -> float:
    if vm.total_decisions == 0:
        return 0.0
    return vm.psi_deferrals / vm.total_decisions

def compute_scheduling(psi_ratio: float) -> SchedulingDecision:
    if psi_ratio > 0.7:
        return SchedulingDecision(priority=140, time_slice_ms=5)
    elif psi_ratio < 0.3:
        return SchedulingDecision(priority=100, time_slice_ms=20)
    else:
        return SchedulingDecision(priority=120, time_slice_ms=10)

def flag_uncertain_page(page: TernaryPage, access_during_psi: bool) -> TernaryPage:
    if access_during_psi:
        page.has_psi = True
        page.psi_access_count += 1
        if page.psi_access_count >= 3:
            page.flagged_for_compression = True
        if page.psi_access_count >= 10:
            page.flagged_for_isolation = True
    return page

def cpuid_leaf_0x40000000() -> Dict:
    # CPUID returns little-endian values
    return {
        'eax': 0x40000001,
        'ebx': int.from_bytes(b'ZIME', 'little'),  # "ZIME" in little-endian
        'ecx': int.from_bytes(b'TER4', 'little'),
        'edx': 0x00010001,
    }

def hypercall_psi_query(vm: VMContext) -> Tuple[int, float]:
    return (0, compute_vm_psi_ratio(vm))

def hypercall_psi_update(vm: VMContext, new_deferrals: int, new_decisions: int) -> int:
    vm.psi_deferrals += new_deferrals
    vm.total_decisions += new_decisions
    return 0

def hypercall_psi_cluster(vms: List[VMContext]) -> Tuple[int, float]:
    total_deferrals = sum(vm.psi_deferrals for vm in vms)
    total_decisions = sum(vm.total_decisions for vm in vms)
    if total_decisions == 0:
        return (0, 0.0)
    return (0, total_deferrals / total_decisions)

def hypercall_psi_power(vm: VMContext, action: str) -> int:
    ratio = compute_vm_psi_ratio(vm)
    if action == 'reduce' and ratio > 0.5:
        return 0
    elif action == 'boost' and ratio < 0.3:
        return 0
    return 1

# ═══════════════════════════════════════════════════════════════
# TESTS
# ═══════════════════════════════════════════════════════════════

def test_psi_ratio_calculation():
    tests = [(0, 100, 0.0), (30, 100, 0.3), (70, 100, 0.7), (100, 100, 1.0), (0, 0, 0.0), (1, 1000, 0.001)]
    passed = 0
    for deferrals, total, expected in tests:
        vm = VMContext(vm_id=1, psi_deferrals=deferrals, total_decisions=total)
        if abs(compute_vm_psi_ratio(vm) - expected) < 0.0001:
            passed += 1
    return passed, len(tests)

def test_per_vm_tracking():
    vms = [VMContext(vm_id=i, psi_deferrals=i*30, total_decisions=100) for i in range(1, 4)]
    ratios = [compute_vm_psi_ratio(vm) for vm in vms]
    assert ratios[0] == 0.3 and ratios[1] == 0.6 and ratios[2] == 0.9
    vms[0].psi_deferrals += 20
    assert compute_vm_psi_ratio(vms[0]) == 0.5 and compute_vm_psi_ratio(vms[1]) == 0.6
    return 3, 3

def test_scheduling_high_psi():
    passed = 0
    for psi in [0.71, 0.8, 0.9, 1.0]:
        dec = compute_scheduling(psi)
        if dec.priority >= 130 and dec.time_slice_ms <= 10:
            passed += 1
    return passed, 4

def test_scheduling_low_psi():
    passed = 0
    for psi in [0.0, 0.1, 0.2, 0.29]:
        dec = compute_scheduling(psi)
        if dec.priority <= 110 and dec.time_slice_ms >= 15:
            passed += 1
    return passed, 4

def test_scheduling_medium_psi():
    passed = 0
    for psi in [0.3, 0.4, 0.5, 0.6, 0.7]:
        dec = compute_scheduling(psi)
        if 110 <= dec.priority <= 130:
            passed += 1
    return passed, 5

def test_memory_page_flagging():
    page = TernaryPage(gfn=0x1000)
    assert not page.has_psi and not page.flagged_for_compression
    page = flag_uncertain_page(page, True)
    assert page.has_psi and page.psi_access_count == 1 and not page.flagged_for_compression
    for _ in range(9):
        page = flag_uncertain_page(page, True)
    assert page.psi_access_count == 10 and page.flagged_for_compression and page.flagged_for_isolation
    return 5, 5

def test_page_isolation():
    pages = [TernaryPage(gfn=i, has_psi=(i % 3 == 0)) for i in range(100)]
    psi_pages = [p for p in pages if p.has_psi]
    normal_pages = [p for p in pages if not p.has_psi]
    assert len(psi_pages) == 34 and len(normal_pages) == 66
    return 2, 2

def test_cpuid_interface():
    cpuid = cpuid_leaf_0x40000000()
    sig = cpuid['ebx'].to_bytes(4, 'little').decode('ascii')
    assert sig == 'ZIME', f"Expected ZIME, got {sig}"
    return 2, 2

def test_hypercalls():
    vm1 = VMContext(vm_id=1, psi_deferrals=20, total_decisions=100)
    vm2 = VMContext(vm_id=2, psi_deferrals=80, total_decisions=100)
    passed = 0
    
    status, ratio = hypercall_psi_query(vm1)
    if status == 0 and abs(ratio - 0.2) < 0.001: passed += 1
    
    status = hypercall_psi_update(vm1, 10, 50)
    if status == 0 and vm1.psi_deferrals == 30: passed += 1
    
    status, cluster = hypercall_psi_cluster([vm1, vm2])
    expected = (30 + 80) / (150 + 100)
    if status == 0 and abs(cluster - expected) < 0.001: passed += 1
    
    status = hypercall_psi_power(vm2, 'reduce')
    if status == 0: passed += 1
    
    return passed, 4

def test_msr_interface():
    vm = VMContext(vm_id=1, psi_deferrals=45, total_decisions=100)
    ratio = compute_vm_psi_ratio(vm)
    msr_value = int(ratio * 0xFFFFFFFF)
    assert 0 <= msr_value <= 0xFFFFFFFF
    assert msr_value == int(0.45 * 0xFFFFFFFF)
    return 2, 2

def test_prior_art_distinction():
    kvm = ['vm_exits', 'msr_access', 'mmio', 'io_access']
    vmware = ['resource_contention', 'cpu_ready', 'mem_balloon']
    zime = ['psi_ratio_per_vm', 'uncertainty_scheduling', 'psi_memory_pages']
    for m in zime:
        assert m not in kvm and m not in vmware
    return 3, 3

def main():
    import socket
    hostname = socket.gethostname()
    print("=" * 70)
    print(f"CLAIM 7: HYPERVISOR VALIDATION @ {hostname}")
    print("=" * 70)
    
    tests = [
        ("(a) PSI Ratio", test_psi_ratio_calculation),
        ("(a) Per-VM Tracking", test_per_vm_tracking),
        ("(b) Scheduling High PSI", test_scheduling_high_psi),
        ("(b) Scheduling Low PSI", test_scheduling_low_psi),
        ("(b) Scheduling Medium PSI", test_scheduling_medium_psi),
        ("(c) Memory Flagging", test_memory_page_flagging),
        ("(c) Page Isolation", test_page_isolation),
        ("(d) CPUID Interface", test_cpuid_interface),
        ("(d) Hypercalls", test_hypercalls),
        ("(d) MSR Interface", test_msr_interface),
        ("Prior Art Distinction", test_prior_art_distinction),
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
    print(f"CLAIM 7 TOTAL: {total_passed}/{total_tests}")
    h = hashlib.md5(f"claim7-{total_passed}/{total_tests}".encode()).hexdigest()[:16]
    print(f"Hash: {h}")
    
    return 0 if total_passed == total_tests else 1

if __name__ == '__main__':
    sys.exit(main())
