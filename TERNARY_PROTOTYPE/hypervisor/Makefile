# Makefile for Ternary KVM Extension
# Builds kernel module for hypervisor-level ternary computing

obj-m += ternary_kvm.o
ternary_kvm-objs := src/ternary_kvm_main.o

# Kernel build directory
KDIR := /lib/modules/$(shell uname -r)/build
PWD := $(shell pwd)

# Compiler flags
ccflags-y := -I$(PWD)/include -DDEBUG

# Default target
all:
	@echo "Building Ternary KVM Extension..."
	$(MAKE) -C $(KDIR) M=$(PWD) modules
	@echo "Build complete: ternary_kvm.ko"

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	$(MAKE) -C $(KDIR) M=$(PWD) clean
	rm -f Module.markers Module.symvers modules.order
	@echo "Clean complete"

# Install module
install: all
	@echo "Installing ternary_kvm module..."
	sudo $(MAKE) -C $(KDIR) M=$(PWD) modules_install
	sudo depmod -a
	@echo "Module installed. Load with: sudo modprobe ternary_kvm"

# Load module
load:
	@echo "Loading ternary_kvm module..."
	sudo insmod ternary_kvm.ko
	@echo "Module loaded. Check dmesg for output."

# Unload module
unload:
	@echo "Unloading ternary_kvm module..."
	sudo rmmod ternary_kvm 2>/dev/null || true
	@echo "Module unloaded."

# Check module status
status:
	@echo "Ternary KVM Module Status:"
	@lsmod | grep ternary_kvm || echo "Module not loaded"
	@echo ""
	@echo "Kernel messages:"
	@dmesg | grep ternary_kvm | tail -20

# Help
help:
	@echo "Ternary KVM Extension Makefile"
	@echo ""
	@echo "Targets:"
	@echo "  all      - Build the module (default)"
	@echo "  clean    - Remove build artifacts"
	@echo "  install  - Install module to system"
	@echo "  load     - Load module into kernel"
	@echo "  unload   - Unload module from kernel"
	@echo "  status   - Check module status and logs"
	@echo "  help     - Show this help message"

.PHONY: all clean install load unload status help
