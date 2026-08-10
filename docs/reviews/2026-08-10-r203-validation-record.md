# R203 validation record

**PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

## Scope

R203 issues `HR-V0-RUNTIME-OBS-PINMAP-P0.1`, a source-level Raspberry Pi 5 GPIO allocation candidate for the four diagnostic-only observation outputs already defined at `JLOGIC1`. It does not select a Pi-side connector or harness, resolve the target Linux gpiochip path, authorize a connection, or give the ordinary watchdog/observation path any functional-safety credit.

The committed candidate maps `OBS_SR1_PI`, `OBS_SRA1_PI`, `OBS_K1_PI` and `OBS_K2_PI` to GPIO22/GPIO23/GPIO24/GPIO25 at physical pins 15/16/18/22. Existing ordinary heartbeat output remains GPIO17 at physical pin 11. Compute return is physical pin 20 for `JLOGIC1` and physical pin 6 for the existing heartbeat path. `PI_3V3_CANDIDATE` is associated with physical pin 17 only as an interface candidate; back-power, sequencing and source acceptance remain open.

## Source verification

- The package contains eight allocation rows, eight conflict-audit rows, six harness-interface rows, eight open holds and four primary-source records.
- Raspberry Pi official documentation and RP1 data were rechecked on 2026-08-10. The RP1 PDF records build date 2023-11-07 and build version `b9b6f74-clean`.
- The conflict audit explicitly blocks `enable_jtag_gpio=1`, records alternate functions including DPI exposure, and requires target `gpioinfo`/pin-control readback rather than inferring a device path.
- The host deployment config binds the four source candidates as active-high inputs but retains `gpio_chip_path: SELECTION REQUIRED` and refuses startup through the preflight boundary.
- No Pi-side connector, contact, cable, wire gauge, shield termination, enclosure routing or harness order code is selected.

## Regression

- The first complete controlled-environment sweep passed 144/145 source checkers. The sole expected failure was the deterministic release manifest rejecting the nine new unstaged R203 files; no engineering failure was suppressed.
- Supervisor and watchdog source tests: 78/78 passed. Target flash and HIL remain not performed.
- Host tests: 16/16 passed. Preflight remains deliberately non-ready at exit 78 with 36 explicit holds, comprising 16 open plus two partial closure-register rows.
- Native KiCad `pcbnew` checker sweep under KiCad 10.0.5 Python: 14/14 passed, including the R202 observation carrier.
- The energization-gate checker returned documented non-ready exit 2: 0/21 gates closed and 21/21 partial through E2.
- The deterministic release manifest contains 3,488 staged package files and passes its dedicated checker. It freezes source/configuration content only and does not imply acceptance.
- After staging the deliberate R203 package and regenerating the manifest, the complete controlled-environment sweep passed 145/145 source checkers at the exact staged candidate.

## Remaining evidence

All eight R203 selection holds remain open. In particular, target OS/kernel/libgpiod identity, gpiochip path, boot overlays, runtime line report, Pi header mate, cable assembly, EMC/grounding review, back-power behavior, physical continuity, polarity, dropout, startup, shutdown and HIL evidence are absent. R203 closes no Sol R12 finding, requirement, energization gate, fabrication gate, connection authority, powered-test authority or functional-safety credit.
