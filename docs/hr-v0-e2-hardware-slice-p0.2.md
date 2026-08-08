# HR-V0 E2 control-only hardware slice P0.2

**PRELIMINARY - CONFIGURATION CANDIDATE ONLY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**

Date: 2026-08-08

Identifier: `HR-V0-E2-HW-P0.2`

Electrical input: `Project Button Electrical V3-P1.11`

Sequence input: `HR-V0-E2-SEQ-P0.1`

Supersedes: `HR-V0-E2-HW-P0.1` for the current candidate only

## Result

P0.2 retains the fail-closed E2 control-only boundary and replaces the unsupported 24 V barrel-conversion chain with the exact GlobTek `WR9QI1660YL4NKITR6B` factory YL4/C40337 locking-cord candidate. It records 23 installed-candidate, physically-absent/disconnected, DNP or selection-required states; six exact XT1 position-to-net candidates; three source-domain states; and twelve blocking holds.

Only the accepted 24 V safety/control source and 5.1 V compute source may eventually be considered at E2. The 12 V actuator source, its AC and DC connections, branch protection, U2D2 power path and every actuator plug must be physically absent or disconnected, covered, labeled and proven dead. K1 and K2 may be installed only for coil and auxiliary/mirror-contact testing; their load poles remain unsourced and unwired.

This is configuration control, not a build, wiring or energization release.

## 24 V source boundary

The exact candidate chain is:

`PSU2 GlobTek WR9QI1660YL4NKITR6B with factory YL4/C40337 cord -> J24 Kycon KPJX-PM-4S -> F24 SELECTION REQUIRED -> control-only loads`

The source is a 24 V, 1.66 A, 40 W Class II wall adapter with floating output. The exact Rev B drawing assigns pin 1 to +24 V, pin 3 to return/shield, and pins 2/4 to N/C. Received source, Q-NA blade and supplied plug identity, blade retention, plug/jack fit, pin view, continuity and polarity remain mandatory because GlobTek permits a four-pin locking connector "or equal."

The preliminary continuous-load screen is 27.024 W / 1.126 A, including a conservative 10 W project reserve for `WDPCB1/DC1`. That leaves 12.976 W of nameplate headroom through 40 C and 4.976 W at the source's published 50 C / 80% derating point. These are screening values only. Simultaneous pickup, tolerance, wiring loss, startup, brownout, current-limit/foldback, recovery and abnormal-condition evidence remain unexecuted.

See `docs/hr-v0-24v-interface-p0.2.md` and `electrical/interfaces/hr-v0-24v-interface-p0.2/`.

## XT1 exact position candidate

| Position | Net | Catalog candidate |
|---|---|---|
| XT1-01 | `SAFETY_24V` | Phoenix PT 2,5 gray item `3209510` |
| XT1-02 | `SAFETY_0V` | Phoenix PT 2,5 BU blue item `3209523` |
| XT1-03 | `SR1_STATUS` | Phoenix PT 2,5 gray item `3209510` |
| XT1-04 | `SRA1_STATUS` | Phoenix PT 2,5 gray item `3209510` |
| XT1-05 | `K1_STATUS` | Phoenix PT 2,5 gray item `3209510` |
| XT1-06 | `K2_STATUS` | Phoenix PT 2,5 gray item `3209510` |

The candidate group also records D-ST 2,5 end cover `3030417`, two CLIPFIX 35 end brackets `3022218`, and UCT-TM 5 marker sheet `0828734`. Conductor order codes, ferrule/direct-wire method, protection, current/temperature coordination, received compatibility, strip length, installed retention, marking and point-to-point proof remain unresolved.

## Controlled artifacts

- `electrical/e2/hr-v0-e2-hardware-p0.2/e2-configuration-slice.csv`
- `electrical/e2/hr-v0-e2-hardware-p0.2/e2-terminal-register.csv`
- `electrical/e2/hr-v0-e2-hardware-p0.2/e2-source-register.csv`
- `electrical/e2/hr-v0-e2-hardware-p0.2/e2-blocking-holds.csv`
- `electrical/e2/hr-v0-e2-hardware-p0.2/e2-hardware-summary.json`
- `electrical/e2/hr-v0-e2-hardware-p0.2/HR-V0_e2-hardware-guide.html`
- `tools/generate_hr_v0_e2_hardware_slice.py`
- `tools/check_hr_v0_e2_hardware_slice.py`

The HTML guide is a responsive review surface with a 16 px body-text floor. CSV and JSON remain the controlled comparison inputs.

## Open release boundary

All twelve hardware holds remain open: site, receiving, RESET/ARM/H1 mapping, source-cord/J24 application and physical evidence, `F24` and FSR1/FSR2 protection/link selections, conductors/terminations, enclosure fabrication, watchdog PCB manufacture, firmware/HIL, test equipment/limits, four-role authorization and physical proof that the actuator domain is absent.

Nothing in this package approves procurement, quotation, drilling, cutting, PCB fabrication, assembly, wiring, connection, energization, motion, human exposure or child-adjacent operation.

**CURRENT VERDICT: NOT BUILT; NOT EXECUTED; NOT AUTHORIZED FOR ENERGIZATION.**
