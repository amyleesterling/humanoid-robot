# R122 validation record

**Package:** `HR-V0-U2D2-USB-P0.1` / synchronized `HR-V0-CP-P0.6`

**Status:** **PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**

## Controlled result

- StarTech.com `USB2AC50CM` is the exact `BOM-070` candidate on hold; it is not purchase-, installation-, connection- or application-released.
- System BOM regeneration: 82 groups; 17 evaluation candidates; 33 exact-candidate holds; three grouped-component holds; 24 selection-required groups; four exclusions; one integrated item.
- P0.6 panel BOM: 34 rows including `PAN-034`.
- R122 interface package: four current primary-source rows, 14 interface controls, four trade rows, 18 blank receiving rows and 16 blank test rows.
- Every receiving/test result field is blank. Every row is `NOT_EXECUTED` and `NOT_AUTHORIZED`.
- EG-003, EG-010, EG-015, EG-016 and EG-017 remain `partial`.

## Automated validation

- All 74 non-manifest `tools/check_*.py` checkers passed using the controlled CadQuery/Python environment, with the three KiCad/PCB checkers run under KiCad 10.0.5 Python.
- `tools/check_hr_v0_u2d2_usb_cable_p01.py` passed: exact identity, source, interface, trade, receiving/test, panel, BOM, gate, metadata and guide assertions stayed synchronized.
- `tools/check_hr_v0_compute_installation_p01.py` passed after synchronization to 34 panel-BOM rows.
- The intentional readiness invocation `tools/check_energization_gates.py --through-stage E2 --require-ready` returned exit 2: 21/21 gates through E2 remain partial; zero are closed.
- Responsive Chromium QA passed at 1440 x 1000 and 390 x 844: no body overflow, minimum visible text 12 CSS px, technical diagram/table overflow remained within explicit horizontal scrollers, and the interactive evidence filters returned the expected two electrical cards.
- Desktop and mobile rendered pages were visually inspected. The numbered closure route, warning hierarchy, readable labels and deliberate technical scrolling were confirmed.

## Evidence that remains absent

No cable or U2D2 lot was received. No Pi/case port fit, cable length/OD measurement, minimum-bend disposition, GTM3/GT3 installation, pull/slip/abrasion/vibration, closed-cover, local-temperature, continuity/shield, enumeration, waveform/jitter/error, common-mode, no-backfeed/power-sequencing, transient, EMC, HIL or qualified-review result exists.

The DYNAMIXEL-side TTL cable, cable entry/gland, PE/DC0V/shield implementation and actuator-current separation proof remain unresolved. USB connection/reconnection/reset has no motion authority, but that behavior has not yet been physically validated.

R122 closes no energization gate and does not change Sol R12's overall verdict: HR-V0 is not ready to build or energize, and HR-30W walking remains physically plausible but unproved.

## Configuration closure

The deterministic release manifest is regenerated only after all R122 files are staged, then checked again from the clean committed tree. The final manifest count and commit hash are recorded by Git and the manifest checker, not inferred as design approval.

**PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**
