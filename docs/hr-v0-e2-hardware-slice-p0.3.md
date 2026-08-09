# HR-V0 E2 control-only hardware slice P0.3

**PRELIMINARY - CONFIGURATION CANDIDATE ONLY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**

Date: 2026-08-09

Identifier: `HR-V0-E2-HW-P0.3`

Electrical input: `Project Button Electrical V3-P1.14`, watchdog board `PCB-P0.9`, assembly data `HR-V0-WD-PCBA-DATA-P0.2`

Sequence input: `HR-V0-E2-SEQ-P0.1`

Supersedes: `HR-V0-E2-HW-P0.2` for the current candidate only

## Result

P0.3 synchronizes the fail-closed E2 control-only boundary to the current electrical and watchdog-PCBA configuration. It retains 23 installed-candidate, physically-absent/disconnected, DNP or selection-required states; six exact XT1 position-to-net candidates; three source-domain states; and twelve blocking holds.

Only the accepted 24 V safety/control source and 5.1 V compute source may eventually be considered at E2. The 12 V actuator source, its AC and DC connections, branch protection, U2D2 power path and every actuator plug must be physically absent or disconnected, covered, labeled and proven dead. K1 and K2 may be installed only for coil and auxiliary/mirror-contact testing; their load poles remain unsourced and unwired.

The new watchdog-PCBA metadata and assembly-data packages improve configuration traceability. They do not select the assembly process, authorize board manufacture or close any physical evidence hold.

This is configuration control, not a build, wiring or energization release.

## Controlled artifacts

- `electrical/e2/hr-v0-e2-hardware-p0.3/e2-configuration-slice.csv`
- `electrical/e2/hr-v0-e2-hardware-p0.3/e2-terminal-register.csv`
- `electrical/e2/hr-v0-e2-hardware-p0.3/e2-source-register.csv`
- `electrical/e2/hr-v0-e2-hardware-p0.3/e2-blocking-holds.csv`
- `electrical/e2/hr-v0-e2-hardware-p0.3/e2-hardware-summary.json`
- `electrical/e2/hr-v0-e2-hardware-p0.3/HR-V0_e2-hardware-guide.html`
- `tools/generate_hr_v0_e2_hardware_slice.py`
- `tools/check_hr_v0_e2_hardware_slice.py`

The HTML guide is a responsive review surface with a 16 px body-text floor. CSV and JSON remain the controlled comparison inputs.

## Open release boundary

All twelve hardware holds remain open: site, receiving, RESET/ARM/H1 mapping, source-cord/J24 application and physical evidence, `F24` and FSR1/FSR2 protection/link selections, conductors/terminations, enclosure fabrication, watchdog PCB manufacture, firmware/HIL, test equipment/limits, four-role authorization and physical proof that the actuator domain is absent.

Nothing in this package approves procurement, quotation, drilling, cutting, PCB fabrication, assembly, wiring, connection, energization, motion, human exposure or child-adjacent operation.

**CURRENT VERDICT: NOT BUILT; NOT EXECUTED; NOT AUTHORIZED FOR ENERGIZATION.**
