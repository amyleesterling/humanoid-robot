# R176 independent review request — isolated dynamic-event interface

> **PRELIMINARY — REVIEW INPUT ONLY — NOT APPROVED FOR PROCUREMENT, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION.**

Please review `HR-V0-DYN-EVENT-IF-P0.1` for accuracy and completeness. This is an evaluation-instrument interface, not a robot subassembly or safety function.

## Controlled review set

- `docs/hr-v0-dynamic-event-interface-p0.1.md`
- `test-equipment/hr-v0/dynamic-event-interface-p0.1/`
- `electrical/kicad/hr-v0-dynamic-event-interface-p0.1/`
- `tests/forms/hr-v0-dynamic-event-interface-receiving-template-p0.1.csv`
- `release/hr-v0/dynamic-event-interface-p0.1/`
- `requirements/hr-v0-gate-evidence-supplement-r176.csv`
- `tools/generate_hr_v0_dynamic_event_interface_p01.py`
- `tools/check_hr_v0_dynamic_event_interface_p01.py`

## Review questions

1. Verify every ISO1212EVM J4/J2/J1/J3 terminal against TI `SLLU254A`, including that only unmodified fast channels 1–4 are used.
2. Verify every T7 DB37/FIO mapping, `FIO_STATE` stream claim, logic-level boundary and duplicate-terminal constraint against current LabJack primary documentation.
3. Challenge the assumption that approximately 2.25 mA typical may be placed in parallel with `SR1_S12`, `SR1_START_RETURN`, `ARM_AFTER_S2`, `K1_A1`, `K2_A1`, `EDM_K1_OUT` and `SRA1_START_RETURN`.
4. Determine what exact Pilz/Schneider application evidence and physical tests are required to prove no diagnostic-pulse distortion, false state, cross-fault masking, EDM defeat, coil-dropout change or common-cause degradation.
5. Challenge the shared field-FGND topology, test-point adapters, segregation, shielding, ground-loss faults and the proposed T7 VS power route.
6. Verify that FIO0 as a streamed trigger/witness bit plus FIO1–FIO7 as event bits can support a defensible common-clock trace. Challenge the preliminary 10 kscan/s target and identify every propagation, sampling, buffer, transport, trigger and analysis uncertainty term.
7. Verify that no test equipment can command motion, sustain power, bypass a protective circuit, or receive safety-function credit.
8. Inspect all native KiCad sheets and exports for pin/net parity, clipping, unreadable text, misleading wiring or hidden assumptions. Re-run KiCad ERC; explain why ERC 0/0 does not validate the application.
9. Identify any safer or more suitable exact evaluation route supported by current primary manufacturer evidence.

Return prioritized `BLOCKER / MAJOR / MINOR` findings with exact file, sheet, reference, terminal, net and source revision/date. Do not approve connection, powered testing, motion or energization.
