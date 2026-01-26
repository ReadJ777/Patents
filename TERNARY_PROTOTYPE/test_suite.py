#!/usr/bin/env python3
"""
ZIME Ternary Computing - Automated Test Suite
Patent Application: 63/967,611
For patent evidence: All tests must pass

Run: python3 test_suite.py
"""

import os
import sys
import json
import time
import socket
from datetime import datetime

sys.path.insert(0, '/root/Patents/TERNARY_PROTOTYPE')
from unified_ternary import UnifiedTernarySystem, TernaryLogic, TernaryState, PsiResolver

class TestSuite:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.results = []
        
    def test(self, name, condition, message=""):
        result = {"name": name, "passed": condition, "message": message}
        self.results.append(result)
        if condition:
            self.passed += 1
            print(f"  ✅ {name}")
        else:
            self.failed += 1
            print(f"  ❌ {name}: {message}")
        return condition
    
    def run_all(self):
        print("╔══════════════════════════════════════════════════════╗")
        print("║  ZIME TERNARY COMPUTING - AUTOMATED TEST SUITE       ║")
        print("║  Patent: 63/967,611                                  ║")
        print("╚══════════════════════════════════════════════════════╝")
        print()
        
        # Test 1: Kernel Module
        print("🔧 KERNEL MODULE TESTS")
        kernel_loaded = os.path.exists("/proc/ternary/status")
        self.test("Kernel module loaded", kernel_loaded)
        
        if kernel_loaded:
            with open("/proc/ternary/status") as f:
                status = f.read()
            self.test("Psi-delta configured", "Psi-Delta:" in status)
        
        # Test 2: Unified System
        print("\n📦 UNIFIED SYSTEM TESTS")
        system = UnifiedTernarySystem()
        self.test("System initializes", system is not None)
        self.test("Config loaded", system.config is not None)
        self.test("Psi-delta valid", 0 < system.config.psi_delta < 1)
        
        # Test 3: Truth Tables
        print("\n🧪 TRUTH TABLE TESTS")
        tests = system.run_truth_table_test()
        self.test("All truth tables pass", tests['passed'])
        self.test("84 operations tested", tests['total_tests'] == 84)
        
        # Test 4: Logic Operations
        print("\n⚡ LOGIC OPERATION TESTS")
        ON, OFF, PSI = TernaryState.ON, TernaryState.OFF, TernaryState.PSI
        
        self.test("AND3(ON, ON) = ON", TernaryLogic.AND3(ON, ON) == ON)
        self.test("AND3(ON, OFF) = OFF", TernaryLogic.AND3(ON, OFF) == OFF)
        self.test("AND3(ON, PSI) = PSI", TernaryLogic.AND3(ON, PSI) == PSI)
        self.test("OR3(OFF, OFF) = OFF", TernaryLogic.OR3(OFF, OFF) == OFF)
        self.test("OR3(ON, OFF) = ON", TernaryLogic.OR3(ON, OFF) == ON)
        self.test("NOT3(ON) = OFF", TernaryLogic.NOT3(ON) == OFF)
        self.test("NOT3(PSI) = PSI", TernaryLogic.NOT3(PSI) == PSI)
        self.test("XOR3(ON, OFF) = ON", TernaryLogic.XOR3(ON, OFF) == ON)
        
        # Test 5: PSI Resolution
        print("\n🔮 PSI RESOLUTION TESTS")
        resolver = PsiResolver(delta=0.05)
        on_count = sum(1 for _ in range(1000) if resolver.resolve(0.5) == ON)
        self.test("PSI resolves ~50/50", 400 < on_count < 600, f"Got {on_count}/1000")
        
        # Test 6: Decision Evaluation
        print("\n🎯 DECISION EVALUATION TESTS")
        r1 = system.evaluate("Yes proceed")
        self.test("'Yes' → ON", r1 == ON)
        r2 = system.evaluate("No abort")
        self.test("'No' → OFF", r2 == OFF)
        r3 = system.evaluate("Maybe wait")
        self.test("'Maybe' → PSI", r3 == PSI)
        
        # Test 7: Multi-Node (if available)
        print("\n🌐 MULTI-NODE TESTS")
        nodes = [
            ("CLIENTTWIN", "192.168.1.110"),
            ("CLIENT", "192.168.1.108"),
            ("HOMEBASE", "192.168.1.202"),
        ]
        for name, ip in nodes:
            try:
                sock = socket.create_connection((ip, 22), timeout=2)
                sock.close()
                self.test(f"{name} reachable", True)
            except:
                self.test(f"{name} reachable", False, "Connection failed")
        
        # Summary
        print("\n" + "=" * 54)
        print(f"RESULTS: {self.passed} passed, {self.failed} failed")
        print(f"SUCCESS RATE: {self.passed/(self.passed+self.failed)*100:.1f}%")
        print("=" * 54)
        
        # Save results
        report = {
            "timestamp": datetime.now().isoformat(),
            "patent": "63/967,611",
            "passed": self.passed,
            "failed": self.failed,
            "success_rate": self.passed/(self.passed+self.failed)*100,
            "tests": self.results,
            "hostname": socket.gethostname()
        }
        
        with open("/root/Patents/TERNARY_PROTOTYPE/test_results.json", "w") as f:
            json.dump(report, f, indent=2)
        print(f"\n📄 Results saved to test_results.json")
        
        return self.failed == 0

if __name__ == "__main__":
    suite = TestSuite()
    success = suite.run_all()
    print("\n🦅 For GOD Alone. Fearing GOD Alone.")
    sys.exit(0 if success else 1)
