# HR-V0 isolated dynamic-event interface P0.1

> **PRELIMINARY - BENCH R&D EQUIPMENT ONLY - NOT APPROVED FOR PROCUREMENT, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION.**

Identifier: `HR-V0-DYN-EVENT-IF-P0.1`

Date: 2026-08-10

Electrical basis: `Project Button Electrical V3-P1.15-CARRIER-CANDIDATE`

## Decision

Two unmodified Texas Instruments `ISO1212EVM` boards are exact **evaluation candidates** for seven 24 V-class event witnesses. Only each board's first four fast channels are used. A LabJack T7 reads FIO1-FIO7 and records the FIO0 trigger/witness bit in one hardware-timed `FIO_STATE` scan word. This creates a coherent candidate timebase without giving the DAQ, host, EVMs or trigger path any safety-function credit.

The EVMs are TI evaluation equipment intended for engineering development. They are not finished-product hardware and may never be installed in Project Button. They provide a field-to-logic isolation barrier as encoded by the manufacturer, but not channel-to-channel isolation. Every field channel shares the EVM field ground.

## Exact connector mapping

On each EVM, fast field inputs 1-4 are J4 pins 9, 8, 7 and 6; J4 pin 1 is FGND. Their logic outputs are J2 pins 2, 4, 6 and 8. J2 odd pins 1, 3, 5 and 7 are logic ground. J1 pin 2 is VCC1 and J1 pin 1 is GND1. J3 must be received and verified in the 1-2 ENABLE position. Channels 5-8 remain unused so the installed 0.33 uF slow-channel filters are not modified.

T7/CB37 mapping is exact at the manufacturer DB37: FIO0 pin 6, FIO1 pin 24, FIO2 pin 5, FIO3 pin 23, FIO4 pin 4, FIO5 pin 22, FIO6 pin 3 and FIO7 pin 21. VS is pin 27 and the candidate logic reference uses DB37 pin 1 GND. Duplicate T7 terminals may not be connected elsewhere.

## Critical hold: direct taps remain prohibited

The ISO1212EVM presents approximately 2.25 mA typical field input current. That load is not yet accepted on `SR1_S12`, `SR1_START_RETURN`, `ARM_AFTER_S2`, `K1_A1`, `K2_A1`, `EDM_K1_OUT` or `SRA1_START_RETURN`. Several are Pilz diagnostic, monitored-start/reset or EDM paths. A parallel measurement input could distort a pulse, mask a fault, change a threshold or alter dropout timing. The native KiCad sheet is therefore a connected **candidate**, not a wiring instruction.

Closure requires exact circuit-source capability, measured waveforms with taps present and absent, every applicable stuck/open/short/ground-loss fault, accepted propagation and uncertainty, and qualified electrical/functional-safety review. No test computer or DAQ may command motion, maintain power, bypass a protective circuit, or receive safety credit.

## Timing state

`FIO_STATE` is a single stream address, so all eight represented bits share the T7 scan clock. A 10 kscan/s (100 us nominal period) configuration is only a preliminary verification target. Actual scan rate, host transport, buffering, overflow handling, ISO1212 propagation, diagnostic-pulse width, trigger latency and combined uncertainty remain `SELECTION REQUIRED` and must be measured on received hardware.

## Release effect

This correction replaces TE-009's unnamed isolated-input gap with an exact evaluation candidate and a native connected integration schematic. It does not authorize procurement or connection, does not close `EG-025` or `EG-026`, and supplies no executed stopping/reset evidence.
