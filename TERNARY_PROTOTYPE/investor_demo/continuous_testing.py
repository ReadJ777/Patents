#!/usr/bin/env python3
"""
ZIME Ternary - Continuous Background Testing
Runs indefinitely, logging results and finding flaws
"""

import os
import sys
import time
import json
import random
from datetime import datetime
from collections import defaultdict

sys.path.insert(0, '/root/Patents/TERNARY_PROTOTYPE')
sys.path.insert(0, '/root/ZIME-Framework/brain')

LOG_FILE = "/root/Patents/TERNARY_PROTOTYPE/investor_demo/continuous_test.log"

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    with open(LOG_FILE, 'a') as f:
        f.write(line + "\n")

def run_continuous_tests():
    from zime_ternary import TernaryDecision, TernaryLogic, TernaryState
    
    log("=" * 60)
    log("ZIME TERNARY - CONTINUOUS BACKGROUND TESTING")
    log("Patent: 63/967,611")
    log("=" * 60)
    
    td = TernaryDecision()
    logic = TernaryLogic()
    states = [TernaryState.OFF, TernaryState.PSI, TernaryState.ON]
    
    stats = defaultdict(int)
    errors = []
    start_time = time.time()
    last_report = start_time
    
    cycle = 0
    while True:
        cycle += 1
        
        try:
            # Test batch of decisions
            for _ in range(10000):
                result = td.decide(random.random())
                stats['decisions'] += 1
                if result == 1:
                    stats['true'] += 1
                elif result == 0:
                    stats['false'] += 1
                else:
                    stats['psi'] += 1
            
            # Test logic operations
            for _ in range(10000):
                a, b = random.choice(states), random.choice(states)
                logic.AND3(a, b)
                logic.OR3(a, b)
                logic.XOR3(a, b)
                stats['logic'] += 3
            
            # Check kernel
            if os.path.exists('/proc/ternary/status'):
                stats['kernel_ok'] += 1
            else:
                stats['kernel_fail'] += 1
            
        except Exception as e:
            errors.append(str(e))
            stats['errors'] += 1
        
        # Report every 60 seconds
        now = time.time()
        if now - last_report >= 60:
            elapsed = now - start_time
            rate = stats['decisions'] / elapsed
            
            log(f"Cycle {cycle}: {stats['decisions']:,} decisions, "
                f"{stats['logic']:,} logic ops, {len(errors)} errors, "
                f"{rate:,.0f} decisions/sec")
            
            # Save stats
            with open("/root/Patents/TERNARY_PROTOTYPE/investor_demo/continuous_stats.json", 'w') as f:
                json.dump({
                    'cycle': cycle,
                    'elapsed_seconds': elapsed,
                    'stats': dict(stats),
                    'errors': errors[-10:],  # Last 10 errors
                    'rate': rate
                }, f, indent=2)
            
            last_report = now
        
        # Small sleep to prevent CPU hogging
        time.sleep(0.01)

if __name__ == "__main__":
    run_continuous_tests()
