/* Project-owned minimal reset path for STM32H743ZIT6 FIRST_POWER_NO_MOTION.
 * It disables interrupts, forces the defined GPIO/UART boundary inactive
 * before C runtime initialization, initializes data/BSS, then enters the
 * polling target loop.  It is not derived safety-certified startup code. */

.syntax unified
.cpu cortex-m7
.fpu softvfp
.thumb

.global g_hr30_vectors
.global Reset_Handler
.global Default_Handler
.extern _estack
.extern _sidata
.extern _sdata
.extern _edata
.extern _sbss
.extern _ebss
.extern hr30_target_early_safe
.extern hr30_target_main
.extern hr30_target_fault_hold

.section .isr_vector,"a",%progbits
.balign 1024
.type g_hr30_vectors, %object
g_hr30_vectors:
    .word _estack
    .word Reset_Handler
    .word Default_Handler /* NMI */
    .word Default_Handler /* HardFault */
    .word Default_Handler /* MemManage */
    .word Default_Handler /* BusFault */
    .word Default_Handler /* UsageFault */
    .word 0
    .word 0
    .word 0
    .word 0
    .word Default_Handler /* SVCall */
    .word Default_Handler /* DebugMon */
    .word 0
    .word Default_Handler /* PendSV */
    .word Default_Handler /* SysTick; polling profile never enables it */
    .rept 150
    .word Default_Handler
    .endr
.size g_hr30_vectors, . - g_hr30_vectors

.section .text.Reset_Handler,"ax",%progbits
.thumb_func
.type Reset_Handler, %function
Reset_Handler:
    cpsid i
    bl hr30_target_early_safe

    ldr r0, =_sidata
    ldr r1, =_sdata
    ldr r2, =_edata
1:
    cmp r1, r2
    bcs 2f
    ldr r3, [r0], #4
    str r3, [r1], #4
    b 1b
2:
    ldr r1, =_sbss
    ldr r2, =_ebss
    movs r3, #0
3:
    cmp r1, r2
    bcs 4f
    str r3, [r1], #4
    b 3b
4:
    ldr r0, =g_hr30_vectors
    ldr r1, =0xe000ed08
    str r0, [r1]
    dsb
    isb
    bl hr30_target_main
5:
    b 5b
.size Reset_Handler, . - Reset_Handler

.section .text.Default_Handler,"ax",%progbits
.thumb_func
.type Default_Handler, %function
Default_Handler:
    cpsid i
    bl hr30_target_fault_hold
6:
    b 6b
.size Default_Handler, . - Default_Handler

.section .note.GNU-stack,"",%progbits
