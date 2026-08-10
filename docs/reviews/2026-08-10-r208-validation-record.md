# R208 validation record

**PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

R208 issues `HR-V0-OBSERVATION-COMPUTE-POWER-BOUNDARY-P0.1` without releasing or superseding R202, R203, R204, R207 or Electrical P1.16.

The dedicated checker source-matches the exact power/signal topology, Raspberry Pi pin allocation, six-wire harness, two ISO1212 devices, four 1.00 kohm series candidates and four 10.0 kohm pulldowns. It preserves the Pi 5 header-load and RP1 DC-characteristic gaps, all false-authority flags, twelve open holds and fourteen unexecuted acceptance rows.

The source audit identifies a new blocker: a nominal 3.3 V hard short through the current 1.00 kohm output-series candidate screens at 3.300 mA, or 3.333 mA at -1% resistor tolerance, while TI specifies +/-3 mA recommended output current at 3.3 V. The current RSO selection and resulting Pi input margin are not released.

## Repository validation

Validation was executed against the synchronized staged package on 2026-08-10:

- dedicated R208 checker: PASS;
- standard HR-V0 checker sweep: 150/150 PASS;
- native `pcbnew` checker sweep under KiCad 10.0: 15/15 PASS;
- supervisor unit tests: 67/67 PASS;
- watchdog unit tests: 11/11 PASS;
- host-deployment unit tests: 16/16 PASS, with the committed configuration remaining `ready:false` and `motion_authority:NONE`;
- energization-gate audit: 0 closed, 23 partial and 7 open; `--require-ready` returned exit 2 as required for an unreleased package;
- interactive web guide at 1280 x 900 and 390 x 844: warning and blocker visible, minimum measured functional text 14 CSS px, no body-level horizontal overflow, SVG rendered, and the `FIELD_ONLY` selector state updated the displayed field-power evidence and retained authority `NONE`.

Passing source, regression and presentation checks cannot close any physical, application-review, qualified-review or authorization evidence. No test in this record connected or energized hardware.
