# HR-V0 actuator-source AC cord candidate P0.1

**PRELIMINARY - NOT APPROVED FOR FABRICATION, CONNECTION, MOTION, OR ENERGIZATION**

Identifier: `HR-V0-ACT-AC-CORD-P0.1`

Date: 2026-08-09

Round: R147

## Selection result

R147 advances system `BOM-063` from `selection_required` to `exact_candidate_hold` for one Eaton Tripp Lite series `P006-006` cord. The current official Eaton record identifies:

- NEMA 5-15P to IEC-320-C13;
- 10 A, 125 VAC;
- 18 AWG, three conductors;
- SJT black PVC, VW-1, 7.8 mm catalog OD;
- 6 ft / 1.83 m length;
- -20 to 60 C catalog operating range; and
- UL Listed and cUL Listed status.

The MEAN WELL `GST280A-SPEC` document dated 2026-04-03 identifies the held `GST280A12-C6P` source as Class I with an IEC320-C14 inlet, 3 A typical input at 115 VAC and 95 A cold-start inrush at 115 VAC. It also states that output `-V` is connected to AC protective earth and that final-equipment compliance must be reconfirmed.

The nominal screen is `3 A / 10 A = 0.300`. It is not a cord-ampacity, branch-protection, inrush, temperature, PE, EMC or code-compliance release because the source current is typical and the site/received configuration does not exist.

## Why the exact candidate remains held

Twelve holds remain open: exact Boston premises and branch survey; applicable code/makerspace policy review; separate purchase authority; received cord identity; received source/inlet identity; unpowered mapping and PE/isolation tests; trip-free route; bend/retention; 95 A inrush reconciliation; thermal/abnormal plan; substitution control; and qualified installed-configuration acceptance.

No extension cord or alternate cable is approved by this record. No conductor-to-contact mapping is inferred from connector appearance. Any later unpowered continuity work must use a qualified method and record the received markings, instrument/calibration identity, raw result and independent review.

## Controlled artifacts

- `electrical/ac-input/hr-v0-actuator-ac-cord-p0.1/source-register.csv`
- `electrical/ac-input/hr-v0-actuator-ac-cord-p0.1/interface-control.csv`
- `electrical/ac-input/hr-v0-actuator-ac-cord-p0.1/selection-holds.csv`
- `electrical/ac-input/hr-v0-actuator-ac-cord-p0.1/package-status.json`
- `tests/forms/hr-v0-actuator-ac-cord-receiving-template-p0.1.csv`
- `tests/forms/hr-v0-actuator-ac-cord-site-fit-template-p0.1.csv`
- `release/hr-v0/actuator-ac-cord-p0.1/index.html`
- `tools/generate_hr_v0_actuator_ac_cord.py`
- `tools/check_hr_v0_actuator_ac_cord_p01.py`

## Gate effect

`EG-001`, `EG-003`, `EG-016`, and `EG-019` remain **partial**. The catalog identity is more exact, but the site, received hardware, PE implementation, inrush/branch behavior and qualified acceptance are absent. No other gate changes.
