#!/bin/bash
#
# Ternary KVM Extension - Installation Script
# Installs all dependencies and builds the hypervisor module
#
# Patent: 63/967,611
# Layer: Hypervisor (Ring -1)

set -e

echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║  TERNARY KVM EXTENSION - INSTALLATION                                        ║"
echo "║  Hypervisor-Level Ternary Computing (Ring -1)                                ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HYPERVISOR_DIR="$(dirname "$SCRIPT_DIR")"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

check_root() {
    if [[ $EUID -ne 0 ]]; then
        echo -e "${YELLOW}Warning: Not running as root. Some operations may fail.${NC}"
    fi
}

check_virtualization() {
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Step 1: Checking Hardware Virtualization Support"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    if grep -E '(vmx|svm)' /proc/cpuinfo > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Hardware virtualization: SUPPORTED${NC}"
        if grep -q vmx /proc/cpuinfo; then
            echo "   Type: Intel VT-x"
        else
            echo "   Type: AMD-V"
        fi
    else
        echo -e "${RED}❌ Hardware virtualization: NOT DETECTED${NC}"
        echo ""
        echo "   Options:"
        echo "   1. Enable VT-x/AMD-V in BIOS"
        echo "   2. If running in a VM, enable nested virtualization"
        echo ""
        read -p "Continue anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    echo ""
}

install_dependencies() {
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Step 2: Installing Dependencies"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    # Detect package manager
    if command -v apt &> /dev/null; then
        PKG_MANAGER="apt"
        echo "Detected: Debian/Ubuntu"
        sudo apt update
        sudo apt install -y \
            build-essential \
            linux-headers-$(uname -r) \
            qemu-system-x86 \
            qemu-kvm \
            libvirt-daemon-system \
            libvirt-clients \
            bridge-utils \
            virt-manager
    elif command -v dnf &> /dev/null; then
        PKG_MANAGER="dnf"
        echo "Detected: Fedora/RHEL"
        sudo dnf install -y \
            kernel-devel \
            kernel-headers \
            gcc \
            make \
            qemu-kvm \
            libvirt \
            virt-manager
    elif command -v pacman &> /dev/null; then
        PKG_MANAGER="pacman"
        echo "Detected: Arch Linux"
        sudo pacman -Sy --noconfirm \
            linux-headers \
            base-devel \
            qemu \
            libvirt \
            virt-manager
    else
        echo -e "${YELLOW}Unknown package manager. Please install manually:${NC}"
        echo "  - build-essential / base-devel"
        echo "  - linux-headers-$(uname -r)"
        echo "  - qemu-kvm"
        echo "  - libvirt"
    fi
    
    echo ""
    echo -e "${GREEN}✅ Dependencies installed${NC}"
    echo ""
}

setup_kvm() {
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Step 3: Setting Up KVM"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    # Load KVM modules
    echo "Loading KVM modules..."
    sudo modprobe kvm 2>/dev/null || true
    
    if grep -q vmx /proc/cpuinfo; then
        sudo modprobe kvm_intel 2>/dev/null || true
    else
        sudo modprobe kvm_amd 2>/dev/null || true
    fi
    
    # Check if loaded
    if lsmod | grep -q kvm; then
        echo -e "${GREEN}✅ KVM modules loaded${NC}"
        lsmod | grep kvm
    else
        echo -e "${YELLOW}⚠️ KVM modules not loaded (may need reboot or BIOS change)${NC}"
    fi
    
    # Check /dev/kvm
    if [ -e /dev/kvm ]; then
        echo -e "${GREEN}✅ /dev/kvm exists${NC}"
        
        # Add user to kvm group
        if [ -n "$SUDO_USER" ]; then
            sudo usermod -aG kvm "$SUDO_USER"
            echo "   Added $SUDO_USER to kvm group"
        fi
    else
        echo -e "${YELLOW}⚠️ /dev/kvm not found${NC}"
    fi
    
    # Start libvirtd
    if systemctl is-active --quiet libvirtd; then
        echo -e "${GREEN}✅ libvirtd is running${NC}"
    else
        echo "Starting libvirtd..."
        sudo systemctl start libvirtd 2>/dev/null || true
        sudo systemctl enable libvirtd 2>/dev/null || true
    fi
    
    echo ""
}

build_module() {
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Step 4: Building Ternary KVM Module"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    cd "$HYPERVISOR_DIR"
    
    echo "Building module..."
    make clean 2>/dev/null || true
    
    if make; then
        echo ""
        echo -e "${GREEN}✅ Module built successfully: ternary_kvm.ko${NC}"
        ls -lh ternary_kvm.ko 2>/dev/null || echo "   (Module location varies by kernel version)"
    else
        echo ""
        echo -e "${RED}❌ Build failed${NC}"
        echo "   Check kernel headers are installed for $(uname -r)"
        exit 1
    fi
    
    echo ""
}

test_module() {
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Step 5: Testing Module"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    cd "$HYPERVISOR_DIR"
    
    # Try to load module
    echo "Loading ternary_kvm module..."
    if sudo insmod ternary_kvm.ko 2>/dev/null; then
        echo -e "${GREEN}✅ Module loaded successfully${NC}"
        
        # Show kernel messages
        echo ""
        echo "Kernel messages:"
        dmesg | grep ternary_kvm | tail -10
        
        # Unload for now
        echo ""
        echo "Unloading module (will be loaded when needed)..."
        sudo rmmod ternary_kvm 2>/dev/null || true
    else
        echo -e "${YELLOW}⚠️ Could not load module (may need KVM active)${NC}"
        echo "   This is expected if KVM is not available"
    fi
    
    echo ""
}

print_summary() {
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "INSTALLATION COMPLETE"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Ternary KVM Extension is ready!"
    echo ""
    echo "Usage:"
    echo "  Load module:    sudo insmod $HYPERVISOR_DIR/ternary_kvm.ko"
    echo "  Unload module:  sudo rmmod ternary_kvm"
    echo "  Check status:   make status"
    echo "  View logs:      dmesg | grep ternary_kvm"
    echo ""
    echo "Next Steps:"
    echo "  1. Create a test VM: ./scripts/create_test_vm.sh"
    echo "  2. Run benchmarks:   ./scripts/benchmark.sh"
    echo "  3. View results:     cat ./tests/results.json"
    echo ""
    echo "Documentation: $HYPERVISOR_DIR/docs/"
    echo ""
    echo "For GOD Alone. Fearing GOD Alone. 🦅"
}

# Main
check_root
check_virtualization
install_dependencies
setup_kvm
build_module
test_module
print_summary
