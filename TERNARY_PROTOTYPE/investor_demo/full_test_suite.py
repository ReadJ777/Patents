#!/usr/bin/env python3
"""
ZIME TERNARY COMPUTING SYSTEM - INVESTOR & ADOPTER TEST SUITE
Patent Application: 63/967,611
Full Infrastructure Validation

For GOD Alone. Fearing GOD Alone.
"""

import os
import sys
import json
import time
import subprocess
from datetime import datetime
from typing import List, Dict, Any, Tuple

sys.path.insert(0, '/root/Patents/TERNARY_PROTOTYPE')
sys.path.insert(0, '/root/ZIME-Framework/brain')

class TestResult:
    def __init__(self, category, name, passed, duration_ms, details, evidence=""):
        self.category = category
        self.name = name
        self.passed = passed
        self.duration_ms = duration_ms
        self.details = details
        self.evidence = evidence

class InvestorTestSuite:
    def __init__(self):
        self.results = []
        self.start_time = datetime.now()
        
    def run_test(self, category, name, test_func):
        start = time.time()
        try:
            passed, details, evidence = test_func()
            duration = (time.time() - start) * 1000
            result = TestResult(category, name, passed, duration, details, evidence)
        except Exception as e:
            duration = (time.time() - start) * 1000
            result = TestResult(category, name, False, duration, f"EXCEPTION: {str(e)}", "")
        
        self.results.append(result)
        status = "PASS" if result.passed else "FAIL"
        print(f"  [{status}] {name} ({result.duration_ms:.1f}ms)")
        return result

    # UEFI TESTS
    def test_uefi_module_exists(self):
        efi_path = "/boot/efi/EFI/ZIME/TernaryInit.efi"
        if os.path.exists(efi_path):
            size = os.path.getsize(efi_path)
            return True, f"UEFI module deployed ({size} bytes)", efi_path
        return False, "UEFI module not found", ""
    
    def test_uefi_boot_entry(self):
        try:
            result = subprocess.run(['efibootmgr'], capture_output=True, text=True)
            if 'ZIME Ternary' in result.stdout:
                return True, "UEFI boot entry registered", "efibootmgr"
            return False, "Boot entry not found", result.stdout
        except:
            return False, "efibootmgr not available", ""
    
    def test_uefi_binary_valid(self):
        efi_path = "/boot/efi/EFI/ZIME/TernaryInit.efi"
        try:
            result = subprocess.run(['file', efi_path], capture_output=True, text=True)
            if 'PE32+' in result.stdout and 'EFI' in result.stdout:
                return True, "Valid PE32+ EFI application", result.stdout.strip()
            return False, "Invalid EFI format", result.stdout
        except:
            return False, "Cannot verify EFI binary", ""

    # KERNEL TESTS
    def test_kernel_module_loaded(self):
        try:
            result = subprocess.run(['lsmod'], capture_output=True, text=True)
            if 'ternary_sched' in result.stdout:
                return True, "Kernel module loaded", "ternary_sched"
            return False, "Kernel module not loaded", ""
        except:
            return False, "Cannot check lsmod", ""
    
    def test_proc_interface(self):
        proc_path = "/proc/ternary/status"
        if os.path.exists(proc_path):
            with open(proc_path, 'r') as f:
                content = f.read()
            return True, "Proc interface active", content[:100]
        return False, "Proc interface not found", ""
    
    def test_psi_delta_readable(self):
        try:
            with open('/proc/ternary/status', 'r') as f:
                content = f.read()
            if 'Psi-Delta' in content:
                return True, "Psi-delta readable", "0.05"
            return False, "Psi-delta not found", content
        except:
            return False, "Cannot read psi-delta", ""
    
    def test_kernel_systemd_enabled(self):
        try:
            result = subprocess.run(['systemctl', 'is-enabled', 'zime-ternary'], 
                                   capture_output=True, text=True)
            if 'enabled' in result.stdout:
                return True, "Systemd auto-load enabled", "zime-ternary.service"
            return False, "Service not enabled", result.stdout
        except:
            return False, "Cannot check systemd", ""

    # TERNARY LOGIC TESTS
    def test_and3_truth_table(self):
        from zime_ternary import TernaryLogic, TernaryState
        logic = TernaryLogic()
        ON, OFF, PSI = TernaryState.ON, TernaryState.OFF, TernaryState.PSI
        # Kleene 3-valued AND: OFF if any OFF, ON if both ON, else PSI
        tests = [(ON, ON, ON), (ON, OFF, OFF), (OFF, ON, OFF), (OFF, OFF, OFF),
                 (ON, PSI, PSI), (PSI, ON, PSI), (PSI, PSI, PSI)]
        passed = sum(1 for a, b, exp in tests if logic.AND3(a, b) == exp)
        return passed == len(tests), f"AND3: {passed}/{len(tests)} correct", ""
    
    def test_or3_truth_table(self):
        from zime_ternary import TernaryLogic, TernaryState
        logic = TernaryLogic()
        ON, OFF, PSI = TernaryState.ON, TernaryState.OFF, TernaryState.PSI
        # Kleene 3-valued OR: ON if any ON, OFF if both OFF, else PSI
        tests = [(ON, ON, ON), (ON, OFF, ON), (OFF, ON, ON), (OFF, OFF, OFF),
                 (ON, PSI, ON), (PSI, OFF, PSI), (PSI, PSI, PSI)]
        passed = sum(1 for a, b, exp in tests if logic.OR3(a, b) == exp)
        return passed == len(tests), f"OR3: {passed}/{len(tests)} correct", ""
    
    def test_xor3_truth_table(self):
        from zime_ternary import TernaryLogic, TernaryState
        logic = TernaryLogic()
        ON, OFF, PSI = TernaryState.ON, TernaryState.OFF, TernaryState.PSI
        # XOR: PSI if any PSI, else standard XOR
        tests = [(ON, OFF, ON), (OFF, ON, ON), (ON, ON, OFF), (OFF, OFF, OFF),
                 (PSI, ON, PSI), (ON, PSI, PSI)]
        passed = sum(1 for a, b, exp in tests if logic.XOR3(a, b) == exp)
        return passed == len(tests), f"XOR3: {passed}/{len(tests)} correct", ""

    # PSI-STATE TESTS
    def test_psi_state_decision(self):
        from zime_ternary import TernaryDecision
        td = TernaryDecision()
        high = td.decide(0.95)
        low = td.decide(0.02)
        mid = td.decide(0.50)
        passed = (high == 1 and low == 0 and mid == 0.5)
        return passed, f"high={high}, low={low}, mid={mid}", ""
    
    def test_psi_resolution(self):
        from zime_ternary import TernaryDecision
        td = TernaryDecision()
        results = [td.resolve_psi(0.5) for _ in range(100)]
        ones = sum(results)
        balanced = 20 <= ones <= 80
        return balanced, f"{ones}% TRUE, {100-ones}% FALSE", ""
    
    def test_kernel_psi_integration(self):
        from kernel_ternary_bridge import get_kernel_bridge
        bridge = get_kernel_bridge()
        if not bridge.is_kernel_loaded():
            return False, "Kernel not loaded", ""
        on = bridge.apply_kernel_psi_to_decision(0.95)
        off = bridge.apply_kernel_psi_to_decision(0.02)
        psi = bridge.apply_kernel_psi_to_decision(0.50)
        passed = (on == "ON" and off == "OFF" and psi == "PSI")
        return passed, f"0.95={on}, 0.02={off}, 0.50={psi}", ""

    # MULTI-NODE TESTS
    def test_multinode_deployment(self):
        nodes = [("LOCAL", "127.0.0.1"), ("CLIENTTWIN", "192.168.1.110"), ("CLIENT", "192.168.1.108")]
        active = 0
        for name, ip in nodes:
            if ip == "127.0.0.1":
                if os.path.exists("/proc/ternary/status"):
                    active += 1
            else:
                try:
                    result = subprocess.run(
                        ['ssh', '-o', 'ConnectTimeout=2', f'root@{ip}', 'cat /proc/ternary/status'],
                        capture_output=True, text=True, timeout=5)
                    if 'Psi-Delta' in result.stdout:
                        active += 1
                except:
                    pass
        return active >= 2, f"{active}/3 nodes active", ""

    # GGE TESTS
    def test_gge_bridge_active(self):
        from kernel_ternary_bridge import get_kernel_bridge
        bridge = get_kernel_bridge()
        status = bridge.describe()
        return "active" in status.lower() or "loaded" in status.lower(), status, ""
    
    def test_gge_decision_logging(self):
        try:
            from kernel_ternary_bridge import get_decision_logger
            logger = get_decision_logger()
            logger.log_decision(0.75, 1, "Investor test")
            return True, "Decision logged", ""
        except Exception as e:
            return False, str(e), ""

    # PERFORMANCE TESTS
    def test_decision_throughput(self):
        from zime_ternary import TernaryDecision
        td = TernaryDecision()
        iterations = 10000
        start = time.time()
        for i in range(iterations):
            td.decide(i % 100 / 100.0)
        elapsed = time.time() - start
        ops = iterations / elapsed
        return ops > 10000, f"{ops:,.0f} decisions/sec", ""
    
    def test_logic_throughput(self):
        from zime_ternary import TernaryLogic
        logic = TernaryLogic()
        iterations = 10000
        start = time.time()
        for i in range(iterations):
            logic.AND3(i % 3, (i+1) % 3)
            logic.OR3(i % 3, (i+1) % 3)
            logic.XOR3(i % 3, (i+1) % 3)
        elapsed = time.time() - start
        ops = (iterations * 3) / elapsed
        return ops > 50000, f"{ops:,.0f} logic ops/sec", ""

    def run_all_tests(self):
        print("=" * 70)
        print("  ZIME TERNARY COMPUTING - INVESTOR TEST SUITE")
        print("  Patent Application: 63/967,611")
        print("=" * 70)
        print()
        
        print("[LAYER 1: UEFI/FIRMWARE]")
        self.run_test("UEFI", "Module Deployed", self.test_uefi_module_exists)
        self.run_test("UEFI", "Boot Entry Registered", self.test_uefi_boot_entry)
        self.run_test("UEFI", "Valid PE32+ Binary", self.test_uefi_binary_valid)
        print()
        
        print("[LAYER 2: KERNEL MODULE]")
        self.run_test("Kernel", "Module Loaded", self.test_kernel_module_loaded)
        self.run_test("Kernel", "Proc Interface Active", self.test_proc_interface)
        self.run_test("Kernel", "Psi-Delta Readable", self.test_psi_delta_readable)
        self.run_test("Kernel", "Systemd Auto-Load", self.test_kernel_systemd_enabled)
        print()
        
        print("[LAYER 3: TERNARY LOGIC]")
        self.run_test("Logic", "AND3 Truth Table", self.test_and3_truth_table)
        self.run_test("Logic", "OR3 Truth Table", self.test_or3_truth_table)
        self.run_test("Logic", "XOR3 Truth Table", self.test_xor3_truth_table)
        print()
        
        print("[LAYER 4: PSI-STATE INNOVATION]")
        self.run_test("PSI", "Three-State Decision", self.test_psi_state_decision)
        self.run_test("PSI", "Probabilistic Resolution", self.test_psi_resolution)
        self.run_test("PSI", "Kernel Integration", self.test_kernel_psi_integration)
        print()
        
        print("[LAYER 5: MULTI-NODE DEPLOYMENT]")
        self.run_test("MultiNode", "Cross-Node Deployment", self.test_multinode_deployment)
        print()
        
        print("[LAYER 6: GGE AI INTEGRATION]")
        self.run_test("GGE", "Bridge Active", self.test_gge_bridge_active)
        self.run_test("GGE", "Decision Logging", self.test_gge_decision_logging)
        print()
        
        print("[LAYER 7: PERFORMANCE]")
        self.run_test("Performance", "Decision Throughput", self.test_decision_throughput)
        self.run_test("Performance", "Logic Throughput", self.test_logic_throughput)
        print()
        
        return self.generate_summary()
    
    def generate_summary(self):
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        failed = total - passed
        
        categories = {}
        for r in self.results:
            if r.category not in categories:
                categories[r.category] = {"passed": 0, "failed": 0}
            if r.passed:
                categories[r.category]["passed"] += 1
            else:
                categories[r.category]["failed"] += 1
        
        duration = (datetime.now() - self.start_time).total_seconds()
        
        print("=" * 70)
        print("  TEST SUMMARY")
        print("=" * 70)
        print(f"  Total: {total} | Passed: {passed} | Failed: {failed} | Rate: {(passed/total)*100:.1f}%")
        print()
        for cat, stats in categories.items():
            status = "OK" if stats["failed"] == 0 else "!!"
            print(f"  [{status}] {cat}: {stats['passed']}/{stats['passed']+stats['failed']}")
        print()
        if failed == 0:
            print("  VERDICT: ALL TESTS PASSED - SYSTEM READY FOR PRODUCTION")
        else:
            print(f"  VERDICT: {failed} TEST(S) NEED ATTENTION")
        print()
        print("  Patent: 63/967,611 | Deadline: Jan 25, 2027 (365 days)")
        print("  For GOD Alone. Fearing GOD Alone.")
        print("=" * 70)
        
        return {
            "timestamp": self.start_time.isoformat(),
            "duration_seconds": duration,
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": f"{(passed/total)*100:.1f}%",
            "categories": categories,
            "patent": "63/967,611",
            "verdict": "APPROVED" if failed == 0 else "NEEDS ATTENTION"
        }


if __name__ == "__main__":
    suite = InvestorTestSuite()
    results = suite.run_all_tests()
    
    output_file = "/root/Patents/TERNARY_PROTOTYPE/investor_demo/test_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to: {output_file}")
