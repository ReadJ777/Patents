/*
 * Ternary KVM Extension - Memory Virtualization
 * 
 * Implements ternary-aware Extended Page Table (EPT) handling
 * Transparently tracks PSI state across guest memory
 * 
 * Patent: 63/967,611
 * Layer: Hypervisor (Ring -1)
 */

#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/slab.h>
#include <linux/hashtable.h>
#include "../include/ternary_kvm.h"

/* Hash table for ternary page tracking */
#define TERNARY_PAGE_HASH_BITS 10
static DEFINE_HASHTABLE(ternary_page_ht, TERNARY_PAGE_HASH_BITS);
static DEFINE_SPINLOCK(page_ht_lock);

/* Statistics */
static atomic64_t pages_tracked = ATOMIC64_INIT(0);
static atomic64_t psi_pages = ATOMIC64_INIT(0);
static atomic64_t memory_intercepts = ATOMIC64_INIT(0);

/*
 * Allocate a ternary page descriptor
 */
static struct ternary_page *alloc_ternary_page(gfn_t gfn)
{
    struct ternary_page *page;
    
    page = kzalloc(sizeof(*page), GFP_KERNEL);
    if (!page)
        return NULL;
    
    page->gfn = gfn;
    page->values = kzalloc(PAGE_SIZE / sizeof(u64) * sizeof(struct ternary_value),
                           GFP_KERNEL);
    if (!page->values) {
        kfree(page);
        return NULL;
    }
    
    INIT_LIST_HEAD(&page->list);
    atomic64_inc(&pages_tracked);
    
    return page;
}

/*
 * Free a ternary page descriptor
 */
static void free_ternary_page(struct ternary_page *page)
{
    if (!page)
        return;
    
    kfree(page->values);
    kfree(page);
    atomic64_dec(&pages_tracked);
}

/*
 * Get or create ternary page for a guest frame number
 */
int ternary_gfn_to_page(struct kvm *kvm, gfn_t gfn, struct ternary_page **result)
{
    struct ternary_page *page;
    u32 hash = hash_32(gfn, TERNARY_PAGE_HASH_BITS);
    
    spin_lock(&page_ht_lock);
    
    /* Search for existing page */
    hash_for_each_possible(ternary_page_ht, page, list, hash) {
        if (page->gfn == gfn) {
            *result = page;
            spin_unlock(&page_ht_lock);
            return 0;
        }
    }
    
    /* Allocate new page */
    page = alloc_ternary_page(gfn);
    if (!page) {
        spin_unlock(&page_ht_lock);
        return -ENOMEM;
    }
    
    hash_add(ternary_page_ht, &page->list, hash);
    *result = page;
    
    spin_unlock(&page_ht_lock);
    
    pr_debug("ternary_kvm: Tracking new page GFN %llx\n", (u64)gfn);
    return 0;
}
EXPORT_SYMBOL_GPL(ternary_gfn_to_page);

/*
 * Map guest memory range for ternary tracking
 */
int ternary_map_memory(struct kvm *kvm, gpa_t gpa, u64 size)
{
    gfn_t start_gfn = gpa >> PAGE_SHIFT;
    gfn_t end_gfn = (gpa + size - 1) >> PAGE_SHIFT;
    gfn_t gfn;
    struct ternary_page *page;
    int ret;
    
    pr_info("ternary_kvm: Mapping ternary memory GPA %llx size %llu\n", 
            (u64)gpa, size);
    
    for (gfn = start_gfn; gfn <= end_gfn; gfn++) {
        ret = ternary_gfn_to_page(kvm, gfn, &page);
        if (ret)
            return ret;
    }
    
    return 0;
}
EXPORT_SYMBOL_GPL(ternary_map_memory);

/*
 * Unmap guest memory range from ternary tracking
 */
void ternary_unmap_memory(struct kvm *kvm, gpa_t gpa, u64 size)
{
    gfn_t start_gfn = gpa >> PAGE_SHIFT;
    gfn_t end_gfn = (gpa + size - 1) >> PAGE_SHIFT;
    gfn_t gfn;
    struct ternary_page *page;
    struct hlist_node *tmp;
    u32 hash;
    
    pr_info("ternary_kvm: Unmapping ternary memory GPA %llx size %llu\n",
            (u64)gpa, size);
    
    spin_lock(&page_ht_lock);
    
    for (gfn = start_gfn; gfn <= end_gfn; gfn++) {
        hash = hash_32(gfn, TERNARY_PAGE_HASH_BITS);
        hash_for_each_possible_safe(ternary_page_ht, page, tmp, list, hash) {
            if (page->gfn == gfn) {
                hash_del(&page->list);
                free_ternary_page(page);
                break;
            }
        }
    }
    
    spin_unlock(&page_ht_lock);
}
EXPORT_SYMBOL_GPL(ternary_unmap_memory);

/*
 * Handle MMIO exit with ternary logic
 */
int ternary_handle_mmio(struct kvm_vcpu *vcpu, gpa_t gpa, bool is_write)
{
    struct ternary_page *page;
    gfn_t gfn = gpa >> PAGE_SHIFT;
    u64 offset = gpa & ~PAGE_MASK;
    int slot = offset / sizeof(u64);
    int ret;
    
    atomic64_inc(&memory_intercepts);
    
    /* Get or create ternary page */
    ret = ternary_gfn_to_page(vcpu->kvm, gfn, &page);
    if (ret)
        return ret;
    
    if (is_write) {
        /* On write, mark value as TRUE (known) */
        page->values[slot].state = TERNARY_TRUE;
        page->values[slot].timestamp = ktime_get_ns();
        page->values[slot].confidence = 100;
        page->ternary_count++;
    } else {
        /* On read, check if value is PSI (unknown) */
        if (is_ternary_psi(&page->values[slot])) {
            /* Defer the read - return PSI to guest */
            pr_debug("ternary_kvm: MMIO read of PSI value at GPA %llx\n",
                     (u64)gpa);
            page->values[slot].defer_count++;
            atomic64_inc(&psi_pages);
            return -EAGAIN; /* Signal caller to defer */
        }
    }
    
    return 0;
}
EXPORT_SYMBOL_GPL(ternary_handle_mmio);

/*
 * Handle Port I/O with ternary logic
 */
int ternary_handle_pio(struct kvm_vcpu *vcpu, u16 port, bool is_write)
{
    /* Track I/O operations with ternary state */
    /* For I/O, PSI can mean "device busy, try later" */
    
    pr_debug("ternary_kvm: PIO %s port %x\n", 
             is_write ? "write" : "read", port);
    
    /* Check device state - if uncertain, return PSI */
    /* This is where we'd integrate with device emulation */
    
    return 0;
}
EXPORT_SYMBOL_GPL(ternary_handle_pio);

/*
 * Set a memory location to PSI state
 */
int ternary_set_psi(struct kvm *kvm, gpa_t gpa)
{
    struct ternary_page *page;
    gfn_t gfn = gpa >> PAGE_SHIFT;
    u64 offset = gpa & ~PAGE_MASK;
    int slot = offset / sizeof(u64);
    int ret;
    
    ret = ternary_gfn_to_page(kvm, gfn, &page);
    if (ret)
        return ret;
    
    page->values[slot].state = TERNARY_PSI;
    page->values[slot].timestamp = ktime_get_ns();
    page->values[slot].confidence = 0;
    page->has_psi = true;
    
    atomic64_inc(&psi_pages);
    
    return 0;
}
EXPORT_SYMBOL_GPL(ternary_set_psi);

/*
 * Resolve a PSI memory location
 */
int ternary_resolve_memory_psi(struct kvm *kvm, gpa_t gpa, ternary_state_t final_state)
{
    struct ternary_page *page;
    gfn_t gfn = gpa >> PAGE_SHIFT;
    u64 offset = gpa & ~PAGE_MASK;
    int slot = offset / sizeof(u64);
    int ret;
    
    ret = ternary_gfn_to_page(kvm, gfn, &page);
    if (ret)
        return ret;
    
    if (!is_ternary_psi(&page->values[slot]))
        return 0; /* Already resolved */
    
    page->values[slot].state = final_state;
    page->values[slot].timestamp = ktime_get_ns();
    page->values[slot].confidence = 100;
    
    /* Check if page still has any PSI values */
    page->has_psi = false;
    for (slot = 0; slot < PAGE_SIZE / sizeof(u64); slot++) {
        if (is_ternary_psi(&page->values[slot])) {
            page->has_psi = true;
            break;
        }
    }
    
    return 0;
}
EXPORT_SYMBOL_GPL(ternary_resolve_memory_psi);

/*
 * Get memory statistics
 */
void ternary_memory_stats(u64 *tracked, u64 *psi, u64 *intercepts)
{
    *tracked = atomic64_read(&pages_tracked);
    *psi = atomic64_read(&psi_pages);
    *intercepts = atomic64_read(&memory_intercepts);
}
EXPORT_SYMBOL_GPL(ternary_memory_stats);
