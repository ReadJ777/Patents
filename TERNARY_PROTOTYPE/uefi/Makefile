ARCH = x86_64
TARGET = TernaryInit.efi

EFIINC = /usr/include/efi
EFIINC_ARCH = /usr/include/efi/$(ARCH)
EFILIB = /usr/lib
EFI_CRT = /usr/lib/crt0-efi-$(ARCH).o
LDSCRIPT = /usr/lib/elf_$(ARCH)_efi.lds

CC = gcc
LD = ld
OBJCOPY = objcopy

CFLAGS = -I$(EFIINC) -I$(EFIINC_ARCH) -fno-stack-protector -fpic -fshort-wchar -mno-red-zone -Wall -DEFI_FUNCTION_WRAPPER
LDFLAGS = -nostdlib -znocombreloc -T $(LDSCRIPT) -shared -Bsymbolic -L $(EFILIB) $(EFI_CRT)

all: $(TARGET)

TernaryInit.o: TernaryInit_gnuefi.c
	$(CC) $(CFLAGS) -c -o $@ $<

TernaryInit.so: TernaryInit.o
	$(LD) $(LDFLAGS) $< -o $@ -lefi -lgnuefi

$(TARGET): TernaryInit.so
	$(OBJCOPY) -j .text -j .sdata -j .data -j .dynamic -j .dynsym -j .rel -j .rela -j .reloc --target=efi-app-$(ARCH) $< $@

clean:
	rm -f *.o *.so *.efi
