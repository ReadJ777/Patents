/*
 * Ternary KVM Extension - Header File
 * 
 * Extends KVM with ternary logic support (Ring -1)
 * Provides transparent ternary computing for all guest VMs
 * 
 * Patent: 63/967,611 - ZIME Ternary Computing System
 * Date: 2026-01-26
 * Layer: Hypervisor (Ring -1)
 */

#ifndef TERNARY_KVM_H
#define TERNARY_KVM_H

#include <linux/kvm_host.h>
#include <linux/kvm.h>
#include <linux/types.h>

/* Ternary logic states */
typedef enum {
    TERNARY_FALSE = 0,
    TERNARY_TRUE = 1,
    TERNARY_PSI = 2      /* Deferred/Unknown state */
} ternary_state_t;

/* Ternary value with metadata */
struct ternary_value {
    ternary_state_t state;
    u64 timestamp;       /* When value was set */
    u32 defer_count;     /* How many times deferred */
    u32 confidence;      /* Confidence level (0-100) */
};

/* Ternary memory page descriptor */
struct ternary_page {
    gfn_t gfn;                      /* Guest frame number */
    struct ternary_value *values;   /* Ternary values for page */
    u32 ternary_count;              /* Number of ternary values */
    bool has_psi;                   /* Page contains PSI states */
    struct list_head list;          /* List linkage */
};

/* Per-VM ternary context */
struct ternary_vm_context {
    struct kvm *kvm;
    struct list_head ternary_pages; /* List of ternary pages */
    spinlock_t lock;
    
    /* Statistics */
    u64 ternary_ops;
    u64 psi_deferrals;
    u64 memory_intercepts;
    u64 cpu_intercepts;
    u64 io_intercepts;
};

/* Per-vCPU ternary state */
struct ternary_vcpu_context {
    struct kvm_vcpu *vcpu;
    struct ternary_value registers[16]; /* x86 GPRs in ternary */
    u32 psi_pending;                     /* PSI operations pending */
    bool ternary_mode;                   /* vCPU in ternary mode */
};

/* Ternary operation types */
enum ternary_op {
    TOP_AND3,
    TOP_OR3,
    TOP_NOT3,
    TOP_XOR3,
    TOP_NAND3,
    TOP_NOR3,
    TOP_ADD3,
    TOP_SUB3,
    TOP_MUL3
};

/* Ternary operation result */
struct ternary_result {
    struct ternary_value result;
    bool needs_defer;       /* Operation should be deferred */
    u64 defer_until;        /* Timestamp to retry */
};

/* Function prototypes */

/* Initialization */
int ternary_kvm_init(void);
void ternary_kvm_exit(void);

/* VM context management */
int ternary_vm_init(struct kvm *kvm);
void ternary_vm_destroy(struct kvm *kvm);

/* vCPU context management */
int ternary_vcpu_init(struct kvm_vcpu *vcpu);
void ternary_vcpu_destroy(struct kvm_vcpu *vcpu);

/* VM exit handlers */
int ternary_handle_exit(struct kvm_vcpu *vcpu);
int ternary_handle_mmio(struct kvm_vcpu *vcpu, gpa_t gpa, bool is_write);
int ternary_handle_pio(struct kvm_vcpu *vcpu, u16 port, bool is_write);

/* Memory operations */
int ternary_gfn_to_page(struct kvm *kvm, gfn_t gfn, struct ternary_page **page);
int ternary_map_memory(struct kvm *kvm, gpa_t gpa, u64 size);
void ternary_unmap_memory(struct kvm *kvm, gpa_t gpa, u64 size);

/* Ternary logic operations */
struct ternary_result ternary_execute_op(enum ternary_op op,
                                         struct ternary_value *a,
                                         struct ternary_value *b);

/* PSI state management */
bool ternary_should_defer(struct ternary_value *val);
int ternary_resolve_psi(struct kvm_vcpu *vcpu, struct ternary_value *val);
void ternary_defer_operation(struct kvm_vcpu *vcpu, u64 defer_until);

/* Statistics and debugging */
void ternary_dump_stats(struct kvm *kvm);
void ternary_dump_vcpu_state(struct kvm_vcpu *vcpu);

/* Utility functions */
static inline bool is_ternary_psi(const struct ternary_value *val)
{
    return val->state == TERNARY_PSI;
}

static inline bool is_ternary_true(const struct ternary_value *val)
{
    return val->state == TERNARY_TRUE;
}

static inline bool is_ternary_false(const struct ternary_value *val)
{
    return val->state == TERNARY_FALSE;
}

/* Ternary logic tables (3x3 matrices) */
extern const ternary_state_t ternary_and_table[3][3];
extern const ternary_state_t ternary_or_table[3][3];
extern const ternary_state_t ternary_not_table[3];

#endif /* TERNARY_KVM_H */
