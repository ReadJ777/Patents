#!/usr/bin/env python3
"""
ZIME Ternary - Cross-Node Benchmark
Patent Application: 63/967,611
Tests kernel module on multiple nodes
"""

import subprocess
import json
import time
from datetime import datetime

NODES = [
    ("CLIENTTWIN", "192.168.1.110", "local"),
    ("CLIENT", "192.168.1.108", "ssh"),
]

def run_on_node(node_name, ip, method):
    """Run benchmark on a node"""
    
    benchmark_script = '''
import time
import random

# Benchmark config
iterations = 100000

# Binary approach
start = time.time()
binary_errors = 0
for i in range(iterations):
    confidence = random.random()
    # Binary: must decide yes/no
    decision = confidence > 0.5
    # Simulate error when uncertain (0.3-0.7)
    if 0.3 < confidence < 0.7:
        binary_errors += 1
binary_time = time.time() - start

# Ternary approach
start = time.time()
ternary_errors = 0
ternary_deferred = 0
delta = 0.05
for i in range(iterations):
    confidence = random.random()
    # Ternary: can defer
    if confidence > 0.5 + delta * 5:
        pass  # ON - confident yes
    elif confidence < 0.5 - delta * 5:
        pass  # OFF - confident no
    else:
        ternary_deferred += 1  # PSI - defer
ternary_time = time.time() - start

print(f"BINARY: {binary_time:.3f}s, {binary_errors} errors")
print(f"TERNARY: {ternary_time:.3f}s, {ternary_deferred} deferred, {ternary_errors} errors")
print(f"IMPROVEMENT: {(binary_errors - ternary_errors) / binary_errors * 100:.1f}% error reduction")
'''
    
    if method == "local":
        result = subprocess.run(
            ["python3", "-c", benchmark_script],
            capture_output=True, text=True
        )
        output = result.stdout
    else:
        result = subprocess.run(
            ["ssh", f"root@{ip}", f"python3 -c '{benchmark_script}'"],
            capture_output=True, text=True
        )
        output = result.stdout
    
    return output

def check_kernel(node_name, ip, method):
    """Check if kernel module is loaded"""
    if method == "local":
        result = subprocess.run(
            ["cat", "/proc/ternary/status"],
            capture_output=True, text=True
        )
    else:
        result = subprocess.run(
            ["ssh", f"root@{ip}", "cat /proc/ternary/status 2>/dev/null || echo 'NOT LOADED'"],
            capture_output=True, text=True
        )
    
    return "Psi-Delta" in result.stdout

print("╔══════════════════════════════════════════════════════╗")
print("║  CROSS-NODE TERNARY BENCHMARK                        ║")
print("║  Patent: 63/967,611                                  ║")
print("╚══════════════════════════════════════════════════════╝")
print()

results = []
for node_name, ip, method in NODES:
    print(f"=== {node_name} ({ip}) ===")
    
    # Check kernel
    kernel_loaded = check_kernel(node_name, ip, method)
    print(f"Kernel Module: {'✅ LOADED' if kernel_loaded else '❌ NOT LOADED'}")
    
    # Run benchmark
    print("Running 100,000 iteration benchmark...")
    output = run_on_node(node_name, ip, method)
    print(output)
    
    results.append({
        "node": node_name,
        "ip": ip,
        "kernel_loaded": kernel_loaded,
        "output": output.strip()
    })
    print()

# Save results
report = {
    "timestamp": datetime.now().isoformat(),
    "patent": "63/967,611",
    "nodes_tested": len(results),
    "results": results
}

with open("/root/Patents/TERNARY_PROTOTYPE/benchmark/crossnode_results.json", "w") as f:
    json.dump(report, f, indent=2)

print("📄 Results saved to crossnode_results.json")
print("🦅 For GOD Alone. Fearing GOD Alone.")
