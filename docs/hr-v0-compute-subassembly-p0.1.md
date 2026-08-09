# HR-V0 compute subassembly candidate P0.1

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TEST, OR ENERGIZATION.**

Identifier: `HR-V0-COMPUTE-SUBASM-P0.1`

Date: 2026-08-08

Parent selection: `HR-V0-COMPUTE-SEL-P0.1`

Electrical baseline: `Project Button Electrical V3-P1.14`

## Controlled decision

R120 advances the compute stack from two exact product identities to a bounded subassembly candidate:

- `PI1`: Raspberry Pi 5, 8 GB, unit only, `SC1112` remains an exact candidate on hold.
- `PSU3`: Raspberry Pi 27 W USB-C Power Supply, US Type A, black, `SC1158` remains an exact candidate on hold.
- `COOL1`: Raspberry Pi Active Cooler for Raspberry Pi 5, manufacturer-configurator stock code `SC1148`, becomes an exact candidate on hold.
- `STORE1`: Raspberry Pi SD Card, 64 GB, unprogrammed becomes the preferred product/capacity branch, but the exact manufacturer order code is **SELECTION REQUIRED** because Raspberry Pi's current public product brief, PIP record and configured US page do not expose an unambiguous order code.
- `IMAGE1`: Raspberry Pi OS Lite 64-bit, release 2026-06-18, Debian 13 Trixie, kernel 6.18, official SHA-256 `acff736ca7945e3b305f07cda4abdb870910e12634991da69783611756e381b3` becomes a pinned digital candidate. It has not been downloaded, written, booted, hardened or accepted.

No product is authorized for purchase. No image is authorized for deployment to a machine. Exact identity is not application approval.

## Mechanical and cooling boundary

The current Raspberry Pi 5 drawing gives an approximate 85 mm x 56 mm board envelope and explicitly says its dimensions are reference-only, subject to tolerance and unsuitable as production data. The Active Cooler brief gives an approximate 63.50 mm x 42.50 mm x 13.70 mm envelope and the same reference-only warning. Therefore R120 does **not** issue mounting-hole coordinates, standoff lengths, tray holes or enclosure cut-outs.

The Active Cooler is a permanent clip-on accessory with pre-applied thermal pads and two spring-loaded push pins. It connects to the Pi 5 `FAN` header, receives 5 V from that header, and uses PWM plus tachometer. The manufacturer recommends that it not be removed after installation. The cooler current is not published in the controlled sources, so PSU margin, installed current and thermal acceptance remain open.

`COOL1` is treated as an internal `PI1` accessory boundary. Electrical V3-P1.14 external connectivity is unchanged. This does not hide its load: `CPSI-008` and `CPSI-009` explicitly require measured fan and complete-compute current before application acceptance.

The compute stack and its heartbeat retain **zero functional-safety credit**.

## Storage and image boundary

The official 64 GB card branch is preferred because it is A2, C10/U3/V30 and has Raspberry Pi 5 SDR104 performance published by the manufacturer. Those catalog figures are not endurance, power-loss robustness or project acceptance evidence. Exact order code, programmed/unprogrammed identity, supplier trace, retention and received markings remain open.

The OS record freezes the public image URL and Raspberry Pi-published SHA-256 only. The project still requires:

1. controlled download and independent local hash verification;
2. write/read-back verification on the selected received card;
3. an exact package, service and kernel configuration manifest;
4. secrets provisioned outside the repository;
5. fail-closed startup behavior and inactive motion outputs until the released state machine is ready;
6. power-loss, corruption, recovery and update/rollback tests; and
7. signed configuration and controls review.

The official resilient-filesystem whitepaper supports treating abrupt power loss and SD-card write behavior as engineering risks. It does not prove that this Project Button image is resilient.

## Installation boundary

R121 supersedes this installation snapshot with `HR-V0-CP-P0.6` / `HR-V0-COMPUTE-INSTALL-P0.1`. `BOM-058` now has an exact held enlarged enclosure/backplate branch and `BOM-080` through `BOM-082` add exact held case/base/strap candidates. `BOM-059` and `BOM-070` remain **SELECTION REQUIRED**, and every standoff, fastener, cable entry, USB cable, production hole, installed fit, retention test, fan clearance, service access, grounding/EMC and thermal result remains open. Reference drawings provide catalog-envelope evidence only; received hardware must be measured and accepted before any fabrication release.

## Sol R12 disposition

Sol's supplied summary is the already-controlled R12 review, not a new review round. R120 improves the evidence chain for one architecture-only subsystem. It does not close Sol's build-readiness verdict, any functional-safety, stopping, mass/inertia, walking, power-loss or physical-verification blocker.

## Controlled artifacts

- `electrical/vendor/raspberry-pi/compute-r120/source-manifest-p0.1.csv`
- `bom/hr-v0-compute-subassembly-p0.1.csv`
- `electrical/interfaces/hr-v0-compute-subassembly-p0.1.csv`
- `software/images/hr-v0-rpi-os-lite-p0.1.json`
- `tests/forms/hr-v0-compute-subassembly-receiving-template-p0.1.csv`
- `tests/forms/hr-v0-compute-image-build-template-p0.1.csv`
- `release/hr-v0/compute-subassembly-p0.1/index.html`
- `tools/check_hr_v0_compute_subassembly_p01.py`

Passing repository checks proves only controlled consistency. It does not authorize purchase, assembly, wiring, imaging, powered testing, motion or energization.
