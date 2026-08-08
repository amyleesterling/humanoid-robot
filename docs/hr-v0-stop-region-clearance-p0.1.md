# HR-V0 hard-stop region clearance and interface acquisition P0.1

Document ID: **HR-V0-STOP-REGION-P0.1**
Date: 2026-08-08
Parent arm: `HR-V0-ARM-ARCH-P0.7`
Requirements: `SAFE-007`, `MECH-005`, `MECH-006`
Status: **PRELIMINARY - NOMINAL CAD EVIDENCE ONLY - NOT APPROVED FOR QUOTATION, FABRICATION, MOTION, OR ENERGIZATION**

## Result

The current P0.7 rigid-body geometry was evaluated in the three regions needed before J1-minimum, J1-maximum and J2-minimum physical stops can be designed:

- J1 `-25..-20 deg` with J2 `10..120 deg`;
- J1 `70..75 deg` with J2 `10..120 deg`; and
- J2 `10..15 deg` with J1 `-20..70 deg`.

The deterministic package contains `6,411` unique 0.5-degree boundary poses. Every sampled pose has zero positive-volume non-intentional intersection. It also contains `131` continuous pair-region certificates and `133` accepted leaf cells. The conservative nominal lower bound is `5.743912 mm`, above the package's `0.75 mm` nominal model-space floor.

This closes one question only: the historic `-25/+75 deg` J1 and `+10 deg` J2 study regions are not already occupied by the current nominal P0.7 rigid bodies. It does **not** select those numbers as stop datums, establish room for a stop part, or release a motion envelope.

## Why a physical stop is not frozen yet

The current source does not establish the received horn/idler axial stack, usable side-plate volume, approved fixed and moving attachment features, longer/shared fastener stack, installed cable/connector/strain-relief sweep, guard sweep, accepted contact radius, bumper, impact load case or manufacturing route. A coaxial cam, side-sector plate or integral three-dimensional adapter extension would depend on those inputs.

Inventing any of them from a nominal envelope could create a stop that:

- loads the actuator case, connector, cable or cosmetic cover;
- uses an unapproved hole, thread or shared fastener;
- collides with the received frame, cable, tool or guard;
- contacts at the wrong angle after the actual axial stack and backlash are measured; or
- cannot carry drive-persistence, impact, prying or fatigue loads.

The package therefore leaves all three potentially acceptable topologies `CANDIDATE ROUTE - NOT SELECTED` and explicitly rejects the actuator case/cable/guard as a stop and software-only limiting without independent metal backup.

## Required physical acquisition

`stop-interface-measurement-register.csv` defines `HSI-001..020`. All rows are `OPEN` and `NOT EXECUTED`. The register requires:

1. exact received XM540/H101/S102 identities;
2. J1/J2 fixed and moving axial face locations;
3. both-side swept-volume scans across the candidate regions;
4. manufacturer-supported and physically measured attachment features;
5. external mechanical angle-datum, repeatability and unpowered-backlash evidence; encoder calibration remains later separately authorized powered work;
6. installed cable, connector, strain-relief and guard sweeps;
7. accepted load path, effective/reflected inertia and stop contact radius;
8. exact bumper/retention evidence; and
9. supplier DFM, material certification and first-article capability.

No blank field may be inferred. Numerical acceptance and uncertainty values remain `SELECTION REQUIRED` until a qualified mechanical reviewer accepts the measurement method and load basis.

## Controlled artifacts

- `cad/hr-v0/generated/stop-region-clearance-p0.1/stop-region-clearance-analysis.json`
- `cad/hr-v0/generated/stop-region-clearance-p0.1/stop-region-clearance-samples.csv`
- `cad/hr-v0/generated/stop-region-clearance-p0.1/stop-region-continuous-summary.csv`
- `cad/hr-v0/generated/stop-region-clearance-p0.1/stop-region-continuous-cells.csv`
- `cad/hr-v0/generated/stop-region-clearance-p0.1/stop-interface-measurement-register.csv`
- `cad/hr-v0/generated/stop-region-clearance-p0.1/stop-topology-decision-register.csv`
- `cad/hr-v0/generated/stop-region-clearance-p0.1/HR-V0_stop-region-acquisition.svg`
- `cad/hr-v0/generated/stop-region-clearance-p0.1/HR-V0_stop-region-guide.html`
- `tools/generate_hr_v0_stop_region_clearance.py`
- `tools/check_hr_v0_stop_region_clearance.py`

## Next controlled release step

After `HSI-001..020` are executed against one immutable received configuration, select one topology and issue integrated native CAD, part drawings, attachment and fastener definition, tolerance stack, bumper selection, structural/impact/fatigue analysis, cable/guard sweep, FAI plan and guarded single-axis validation procedure. The selected stop must then be physically measured and tested for contact angle, coast, drive persistence, stopping overtravel, backlash, compliance, impact, rebound and post-test condition before any motion credit is requested.

This package authorizes none of those actions. It does not close `EG-005`, `EG-006`, `EG-007`, `EG-026` or `EG-028`.
