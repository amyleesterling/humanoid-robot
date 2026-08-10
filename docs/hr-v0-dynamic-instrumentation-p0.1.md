# HR-V0 dynamic instrumentation backbone P0.1

> **PRELIMINARY - INSTRUMENTATION EVALUATION CANDIDATE ONLY - NOT APPROVED FOR PROCUREMENT, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION.**

Identifier: `HR-V0-DYN-INST-P0.1`
Date: 2026-08-10

## Decision

This correction names a bounded acquisition backbone for eventual `HR-V0-DYN-CHAR-P0.1` and `HR-V0-DYN-TRACE-P0.1` work without claiming that the physical measurement chain is complete.

Four exact products are evaluation candidates:

- LabJack `T7` base-model DAQ;
- LabJack `CB37 Terminal Board`;
- LEM `HLSR 10-P/SP33` bidirectional current transducer; and
- Teledyne Vision Solutions `BFS-U3-04S2C-CS` high-speed global-shutter camera.

They are not a purchase release. The force, displacement, independent-angle, isolated 24 V event-input and sample-clock-witness chains remain `SELECTION REQUIRED`. The candidate current-transducer range remains unaccepted until the branch fault, peak, RMS and regeneration envelope is measured or otherwise bounded.

## What the backbone can support

The T7 provides fourteen analog inputs, seven differential pairs, twenty-three digital I/O lines and hardware-timed acquisition. Its stated total stream capacity is 100 ksamples/s; sample rate is shared across scan addresses. The project must freeze the actual scan list, ranges, rate, skew and filtering and measure the resulting timing behavior. A clean parse or manufacturer maximum is not an accepted timing budget.

The CB37 exposes the T7 DB37 connector at screw terminals. The remote DB37 cable, mounting, enclosure, strain relief and terminal schedule are still open.

The HLSR 10-P/SP33 is a PCB-mount component, not a finished instrument. Its current public datasheet gives 10 A nominal RMS, a -25 A to +25 A measuring range, 46 mV/A nominal sensitivity, a 3.3 V supply, an approximately 1.65 V reference, a plus/minus 1.15 V output difference across the measuring range, 2.5 microsecond 90 percent step delay and 450 kHz bandwidth. It requires a purpose-designed carrier, clean secondary supply, Uref/Uout acquisition, primary-path thermal and fault review, installed bidirectional calibration and inaccessible conducting parts.

The camera is a corroborating optical channel. The exact lens, working distance, field of view, scale, lighting, USB3 path, trigger wiring, rigid mount, dropped-frame check and trigger-to-exposure latency remain open. Video receives no primary timing credit before those checks close.

## Explicit rejection

The LabJack `LJTick-Divider` divide-by-5 variant is documented as a ground-referenced two-channel divider that can condition 24 V logic. It is not galvanic isolation. Project 24 V stop, coil and mirror signals therefore may not be connected to a T7 through this divider and called a completed primary event-measurement chain. An exact isolated input bank and reviewed schematic remain required. No DAQ or test computer receives safety-function credit or may be inserted so that its failure can command motion or defeat the protective circuit.

## Channel state

The controlled `channel-allocation.csv` maps all fifteen R78 channels. It deliberately leaves T7 address assignments open until the sensor/interface topology is selected. `interface-register.csv` records the manufacturer facts and the project-specific no-connect boundaries. `selection-holds.csv` contains fifteen fail-closed closure records. The receiving/calibration template contains no invented serial, calibration or reviewer evidence.

## Gate effect

`EG-025` and `EG-026` remain open and partial respectively. This package closes only the absence of named acquisition-backbone candidates. It supplies zero physical measurements, zero calibration evidence, zero qualified dispositions and zero work authorization. Sol R12's stopping, reset, physical-instrumentation and executed-evidence blockers remain open.
