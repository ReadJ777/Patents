#!/bin/bash
#==============================================================================
# ZIME TERNARY - DEPLOYMENT VERIFICATION
#==============================================================================

echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║  ZIME TERNARY - INFRASTRUCTURE VERIFICATION                                 ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"

NODES=("localhost" "192.168.1.110" "192.168.1.108")
NODE_NAMES=("LOCAL" "CLIENTTWIN" "CLIENT")

echo ""
echo "┌──────────────┬──────┬───────────┬────────────┬─────────┬──────────┬─────────┐"
echo "│ System       │ UEFI │ EFI File  │ Boot Entry │ Kernel  │ /proc    │ Python  │"
echo "├──────────────┼──────┼───────────┼────────────┼─────────┼──────────┼─────────┤"

for i in ${!NODES[@]}; do
    ip=${NODES[$i]}
    name=${NODE_NAMES[$i]}
    
    if [ "$ip" = "localhost" ]; then
        uefi=$([ -d /sys/firmware/efi ] && echo "✅" || echo "❌")
        efi=$([ -f /boot/efi/EFI/ZIME/TernaryInit.efi ] && echo "✅" || echo "❌")
        boot=$(efibootmgr 2>/dev/null | grep -q "ZIME" && echo "✅" || echo "❌")
        kern=$(lsmod | grep -q ternary && echo "✅" || echo "❌")
        proc=$([ -f /proc/ternary/status ] && echo "✅" || echo "❌")
        pyth=$(python3 -c 'import sys; sys.path.insert(0, "/root/Patents/TERNARY_PROTOTYPE"); from zime_ternary import TernaryState' 2>/dev/null && echo "✅" || echo "❌")
    else
        result=$(ssh -o ConnectTimeout=3 root@$ip "
            uefi=\$([ -d /sys/firmware/efi ] && echo '✅' || echo '❌')
            efi=\$([ -f /boot/efi/EFI/ZIME/TernaryInit.efi ] && echo '✅' || echo '❌')
            boot=\$(efibootmgr 2>/dev/null | grep -q 'ZIME' && echo '✅' || echo '❌')
            kern=\$(lsmod | grep -q ternary && echo '✅' || echo '❌')
            proc=\$([ -f /proc/ternary/status ] && echo '✅' || echo '❌')
            pyth=\$(python3 -c 'import sys; sys.path.insert(0, \"/root/Patents/TERNARY_PROTOTYPE\"; from zime_ternary import TernaryState' 2>/dev/null && echo '✅' || echo '❌')
            echo \"\$uefi|\$efi|\$boot|\$kern|\$proc|\$pyth\"
        " 2>/dev/null) || result="❌|❌|❌|❌|❌|❌"
        
        uefi=$(echo $result | cut -d'|' -f1)
        efi=$(echo $result | cut -d'|' -f2)
        boot=$(echo $result | cut -d'|' -f3)
        kern=$(echo $result | cut -d'|' -f4)
        proc=$(echo $result | cut -d'|' -f5)
        pyth=$(echo $result | cut -d'|' -f6)
    fi
    
    printf "│ %-12s │ %-4s │ %-9s │ %-10s │ %-7s │ %-8s │ %-7s │\n" \
        "$name" "$uefi" "$efi" "$boot" "$kern" "$proc" "$pyth"
done

echo "└──────────────┴──────┴───────────┴────────────┴─────────┴──────────┴─────────┘"
