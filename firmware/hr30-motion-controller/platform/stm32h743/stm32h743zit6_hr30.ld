ENTRY(Reset_Handler)

MEMORY
{
    FLASH (rx)   : ORIGIN = 0x08000000, LENGTH = 2048K
    DTCMRAM (rwx): ORIGIN = 0x20000000, LENGTH = 128K
}

_estack = ORIGIN(DTCMRAM) + LENGTH(DTCMRAM);

SECTIONS
{
    .isr_vector ORIGIN(FLASH) : ALIGN(1024)
    {
        KEEP(*(.isr_vector))
    } > FLASH

    .text : ALIGN(4)
    {
        *(.text*)
        *(.rodata*)
        KEEP(*(.init))
        KEEP(*(.fini))
        . = ALIGN(4);
    } > FLASH

    .ARM.exidx : ALIGN(4)
    {
        *(.ARM.exidx*)
        *(.gnu.linkonce.armexidx.*)
    } > FLASH

    . = ALIGN(4);
    _sidata = LOADADDR(.data);
    .data : ALIGN(4)
    {
        _sdata = .;
        *(.data*)
        . = ALIGN(4);
        _edata = .;
    } > DTCMRAM AT > FLASH

    .bss (NOLOAD) : ALIGN(4)
    {
        _sbss = .;
        *(.bss*)
        *(COMMON)
        . = ALIGN(4);
        _ebss = .;
    } > DTCMRAM

    /DISCARD/ :
    {
        *(.comment)
        *(.note*)
        *(.eh_frame*)
    }
}

ASSERT(SIZEOF(.isr_vector) == 664, "HR-30 vector table must contain 166 words")
ASSERT((_edata - _sdata) + (_ebss - _sbss) < LENGTH(DTCMRAM) - 4096,
       "HR-30 target leaves less than 4096 bytes of DTCM stack headroom")
ASSERT(SIZEOF(.text) + SIZEOF(.isr_vector) < LENGTH(FLASH),
       "HR-30 target exceeds STM32H743ZI flash")
