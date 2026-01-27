#include <linux/module.h>
#include <linux/export-internal.h>
#include <linux/compiler.h>

MODULE_INFO(name, KBUILD_MODNAME);

__visible struct module __this_module
__section(".gnu.linkonce.this_module") = {
	.name = KBUILD_MODNAME,
	.init = init_module,
#ifdef CONFIG_MODULE_UNLOAD
	.exit = cleanup_module,
#endif
	.arch = MODULE_ARCH_INIT,
};

KSYMTAB_FUNC(ternary_enter_psi_state, "", "");
KSYMTAB_FUNC(ternary_evaluate_thread, "", "");
KSYMTAB_FUNC(ternary_adjust_psi, "", "");

SYMBOL_CRC(ternary_enter_psi_state, 0x7938e74d, "");
SYMBOL_CRC(ternary_evaluate_thread, 0x7938e74d, "");
SYMBOL_CRC(ternary_adjust_psi, 0x60d52757, "");

static const struct modversion_info ____versions[]
__used __section("__versions") = {
	{ 0xfed1e3bc, "kmalloc_caches" },
	{ 0x70db3fe4, "__kmalloc_cache_noprof" },
	{ 0xe8213e80, "_printk" },
	{ 0x224a53e7, "get_random_bytes" },
	{ 0xd272d446, "__stack_chk_fail" },
	{ 0x0576ccac, "proc_mkdir" },
	{ 0x82c6f73b, "proc_create" },
	{ 0x003b23f9, "single_open" },
	{ 0xf2c4f3f1, "seq_printf" },
	{ 0x90a48d82, "__ubsan_handle_out_of_bounds" },
	{ 0x33c78c8a, "remove_proc_entry" },
	{ 0xcb8b6ec6, "kfree" },
	{ 0xbd4e501f, "seq_read" },
	{ 0xfc8fa4ce, "seq_lseek" },
	{ 0xcb077514, "single_release" },
	{ 0xd272d446, "__fentry__" },
	{ 0xe1e1f979, "_raw_spin_lock_irqsave" },
	{ 0x81a1a811, "_raw_spin_unlock_irqrestore" },
	{ 0xd272d446, "__x86_return_thunk" },
	{ 0xbd03ed67, "random_kmalloc_seed" },
	{ 0xba157484, "module_layout" },
};

static const u32 ____version_ext_crcs[]
__used __section("__version_ext_crcs") = {
	0xfed1e3bc,
	0x70db3fe4,
	0xe8213e80,
	0x224a53e7,
	0xd272d446,
	0x0576ccac,
	0x82c6f73b,
	0x003b23f9,
	0xf2c4f3f1,
	0x90a48d82,
	0x33c78c8a,
	0xcb8b6ec6,
	0xbd4e501f,
	0xfc8fa4ce,
	0xcb077514,
	0xd272d446,
	0xe1e1f979,
	0x81a1a811,
	0xd272d446,
	0xbd03ed67,
	0xba157484,
};
static const char ____version_ext_names[]
__used __section("__version_ext_names") =
	"kmalloc_caches\0"
	"__kmalloc_cache_noprof\0"
	"_printk\0"
	"get_random_bytes\0"
	"__stack_chk_fail\0"
	"proc_mkdir\0"
	"proc_create\0"
	"single_open\0"
	"seq_printf\0"
	"__ubsan_handle_out_of_bounds\0"
	"remove_proc_entry\0"
	"kfree\0"
	"seq_read\0"
	"seq_lseek\0"
	"single_release\0"
	"__fentry__\0"
	"_raw_spin_lock_irqsave\0"
	"_raw_spin_unlock_irqrestore\0"
	"__x86_return_thunk\0"
	"random_kmalloc_seed\0"
	"module_layout\0"
;

MODULE_INFO(depends, "");


MODULE_INFO(srcversion, "F639956912654F7F1F9FC08");
