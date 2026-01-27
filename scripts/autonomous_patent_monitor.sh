#!/bin/bash
# 🦅 GoodGirlEagle's Autonomous Patent Monitor - ROBUST
LOG_DIR="/root/Patents/EVIDENCE/autonomous_tests"
mkdir -p "$LOG_DIR"
exec >> "$LOG_DIR/monitor.log" 2>&1

echo "========================================"
echo "🦅 Monitor Started: $(date)"
echo "========================================"

ITERATION=1
while true; do
    echo ""
    echo "🦅 ITER $ITERATION - $(date '+%Y-%m-%d %H:%M:%S')"
    
    RESULT=$(timeout 30 ssh -o ConnectTimeout=10 root@192.168.1.108 'python3 -c "
import random, json, time
r = {\"ts\": time.strftime(\"%H:%M\"), \"psi\": round(sum(1 for _ in range(10000) if 0.35<random.gauss(0.5,0.3)<0.65)/100,1)}
print(json.dumps(r))
"' 2>/dev/null || echo '{"error": "timeout"}')
    
    echo "$RESULT" > "$LOG_DIR/test_$(date +%Y%m%d_%H%M).json"
    echo "Result: $RESULT"
    
    cd /root/Patents
    git pull origin master 2>/dev/null
    git add .
    git commit -m "🦅 GGE $(date '+%m-%d %H:%M')" 2>/dev/null && git push origin master 2>/dev/null && echo "✅ Pushed"
    
    ITERATION=$((ITERATION + 1))
    sleep 1800
done
