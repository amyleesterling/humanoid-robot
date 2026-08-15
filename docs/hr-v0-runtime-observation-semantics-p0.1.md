# HR-V0 runtime observation semantics P0.1

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Artifact: `HR-V0-RUNTIME-OBS-P0.1`

Review/control round: R200

## Correction

R199 incorrectly described nine runtime booleans as nine physical GPIO observations. R200 separates four positive panel status candidates from five unavailable health providers and one software-derived bus result. Unknown values are represented as `None`; the supervisor does not coerce them to healthy. Unknown control power holds `POWER_OFF`. Any other unknown required health observation holds `SAFE_DISABLED`. Heartbeat and torque authority remain false.

The four proposed GPIO semantics are `SR1_STATUS`, `SRA1_STATUS`, `K1_STATUS` and `K2_STATUS`. The unused SR1/SRA1 41-42 NC contacts are not inverted into a positive ready claim: an open conductor could otherwise resemble an energized relay. They remain diagnostic contacts with zero functional-safety credit.

## Exact source trace

- SR1 ready candidate: `SR1:Y32 -> SR1_STATUS -> H1 and XT1-03` on `02_estop_eligibility.kicad_sch` and `09_compute_and_control_terminals.kicad_sch`.
- SRA1 armed candidate: `SRA1:Y32 -> SRA1_STATUS -> XT1-04` on `03_arm_watchdog_eligibility.kicad_sch` and sheet 09.
- K1 feedback candidate: `SAFETY_24V -> K1:13/14 -> K1_STATUS -> XT1-05` on `04_contactor_edm.kicad_sch` and sheet 09.
- K2 feedback candidate: `SAFETY_24V -> K2:13/14 -> K2_STATUS -> XT1-06` on sheet 04 and sheet 09.

These traces prove only the current source topology. They do not release a receiver, connector, GPIO, cable or load.

## Loading blockers

Pilz manual 21396-EN-23 identifies Y32 as a non-safety semiconductor status output, high when the safety contacts are closed, with 24 V output, 20 mA maximum current, 0.1 mA residual current and up to 5 V internal drop. The existing SR1 Y32 also drives H1. A TI ISO1212 Type 2 candidate is approximately a 6 mA-class load with 200 ohm `RSENSE`, so it cannot be added until the exact received H1 current plus worst-case receiver current is proven below the Pilz limit across tolerances and faults.

Schneider's LC1D25BD sheet gives 5 mA minimum switching current and 17 V minimum switching voltage for the built-in auxiliary contacts. Any K1/K2 receiver must satisfy those minima under worst-case rail, receiver, wiring and contact conditions.

TI ISO1212 Rev G is an evaluation candidate only. A future design must select exact passives and surge protection, respect its 2.25-5.5 V controller supply, provide the required decoupling, and complete thermal, surge, grounding and isolation review. Raspberry Pi GPIO is 3.3 V logic; exact Pi 5 RP1 line thresholds and pin allocation remain selection-required.

## Software evidence

- `HardwareSnapshot` now represents unselected health observations as `bool | None`.
- Heartbeat permission requires known-good control power, E-stop health, EDM health, bus health and no compute undervoltage.
- The libgpiod backend reads only the four positive status candidates and deliberately returns `None` for control power, E-stop, watchdog, EDM and compute undervoltage.
- Three added supervisor tests prove unknown control power, health and watchdog observations inhibit motion; updated backend tests prove the four-channel mapping.

This is source-model evidence, not target or physical evidence. The committed preflight remains non-ready and the package cannot import or open hardware.

## Primary documents

- Pilz PNOZ s4 operating manual 21396-EN-23, dated 2026-06-22, accessed 2026-08-10: <https://www.pilz.com/download/open/OM_PNOZ_s4_21396-EN-23.pdf>
- TI ISO1212 datasheet SLLSEY7G, Rev G, revised 2025-02, accessed 2026-08-10: <https://www.ti.com/lit/ds/symlink/iso1212.pdf>
- Schneider LC1D25BD product data sheet, current official publication accessed 2026-08-10: <https://iportal.se.com/Contents/docs/SQD-LC1D25BD.PDF>
- Raspberry Pi GPIO documentation, accessed 2026-08-10: <https://www.raspberrypi.com/documentation/computers/raspberry-pi.html>

No requirement, Sol finding, energization gate, functional-safety claim or work authorization closes.
