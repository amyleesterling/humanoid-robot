# R69 validation record — HR-V0 J2 positive-stop candidate

> **PRELIMINARY—NOT APPROVED FOR QUOTATION, FABRICATION, ASSEMBLY, MOTION, OR ENERGIZATION.**

Date: 2026-08-07

Products: `HR-V0-ARM-ARCH-P0.7`, `HR-V0-MECH-P0.6`, `HR-V0-HS-P0.3`, `HR-V0-J2-STOP-P0.1`, `HR-V0-FW-P0.4`, `HR-V0-SUP-P0.3`, `HR-V0-ACT-P0.3`, `HR-V0-DXL-TRANSPORT-P0.3`, `HR-V0-LIMITS-P0.2`

## Result

- Controlled CadQuery generation completed without geometry exception.
- Arm checker passed with 43 generated artifacts: 31 top-level and 12 part files.
- The 40,001-pose body sweep retains zero positive intersection through J2=115° and first sampled body collision at 122°.
- The adaptive certificate covers 69 non-intentional pairs through J2=120°; minimum lower bound is 0.765783 mm.
- C06/C07 are the sole intentional stop pair and are separately analyzed.
- Nominal metal contact is 117.999985°, metal gap at 115° is 1.072358 mm, and body clearance at metal contact is 2.114900 mm.
- The unselected maximum 0.75 mm bumper envelope retains 0.322358 mm nominal gap at 115° and first contacts at 115.861085°.
- Five geometric sensitivity cases, three non-allowable load screens, and six stop controls were generated.
- Replacing two plain adapters with C06/C07 raised the current known/CAD-estimated moving subtotal to 692.758 g and reduced unresolved headroom to 57.242 g; both link allocation buckets are exceeded. Mass closure remains a blocker.
- Mechanical-release generation/checking passed.
- Firmware source validation passed with 47 executable unit tests after synchronizing all binding identifiers. The committed acceptance hash remains `SELECTION REQUIRED`, so the serial port remains inhibited.

## Boundary

No physical article, material certificate, first article, bumper, fastener installation, contact/stopping measurement, proof load, cable/guard sweep, target, HIL, qualified review or signed work authorization exists. The stop load screen omits reflected rotor inertia, impact amplification, unequal rail sharing, prying, local contact, fatigue and life. No artifact is a fabrication or motion release.
