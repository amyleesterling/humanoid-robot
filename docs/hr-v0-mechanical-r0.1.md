# HR-V0 Mechanical R0.1 Preliminary Baseline

**PRELIMINARY—NOT RELEASED FOR FABRICATION OR ENERGIZATION**

Date: 2026-08-06  
Native source: `cad/hr-v0/src/hr_v0_cad.py`  
Reproducible screens: `cad/hr-v0/src/mechanical_checks.py`

## Design decision

HR-V0 is a light-duty, adult-operated bench demonstrator. It does not need high payload or speed. The mechanism is therefore frozen at 100 g of soft payload, two 160 mm planar links, and deliberately limited motion. Strength is not used as a reason to omit proof: low mass, low speed, rounded tooling, current/force limiting, guarding, and redundant power interruption are the protective strategy.

The first structural architecture uses:

- flat 4.75 mm nominal 6061-T6 upper and forearm link plates;
- ROBOTIS FR13-H101K output frames and FR13-S102K actuator-body frames, using the manufacturer's dual-sided support geometry;
- 80/20 40-4040 40 mm square T-slot extrusion for a bolted base and 500 mm column;
- 80/20 40-series catalog gussets; and
- flat 6.35 mm nominal 6061-T6 adapter and bench-anchor plates.

No welding or custom bent 6061 part is required. The base must be physically secured to a surveyed bench; the free-standing assembly model is not an operating configuration.

## Custom part mass closure

| Part | CAD mass at 2.70 g/cm³ | Allocation consequence |
|---|---:|---|
| MV0-001 upper link | 109.2 g | Fits the old 120 g plate-only intent, but leaves insufficient room for frame/fasteners. Allocation must be regrouped. |
| MV0-002 forearm | 109.2 g | Same issue. |
| MV0-003 shoulder adapter | 167.2 g | Fixed, not part of moving mass. |
| MV0-004 anchor plate | 126.9 g each | Fixed; two required. |

The controlled 13-row ledger in `bom/hr-v0-moving-mass-ledger.csv` currently supports a 565.4 g known subtotal and leaves 184.6 g unresolved under the 750 g ceiling. That headroom must still contain every moving frame, fastener, spacer, stop part, cable guide, connector, moving harness segment, and the complete gripper mechanism. See `docs/hr-v0-moving-mass-closure-p0.1.md`. This is not mass closure; all received items require measured mass, local center of mass, and inertia evidence for the exact configuration before torque is re-released.

## Preliminary structural screens

The controlled structural proof moment is `3.83 N·m × 3.0 = 11.49 N·m`. For a 44 × 4.75 mm link cross-section, conservatively subtracting two 2.70 mm holes from the section depth gives:

- net-section second moment: 22,765 mm⁴;
- net-section bending stress: 9.74 MPa;
- ratio against the 240 MPa screening yield input: 24.6;
- gross-section cantilever deflection at equivalent proof load: 0.042 mm;
- conservative load per fastener if only two PCD22 fasteners carry the moment: 522 N; and
- candidate M2.5 plate-bearing stress: 44.0 MPa.

Using the manufacturer-published 80/20 40-4040 inertia of 13.787 cm⁴ and an aluminum modulus of 69 GPa, the 500 mm column screen under the same pure proof moment gives 0.151 mm end displacement. Across a 420 mm anchor couple, the minimum static reaction is only 27.4 N per side. These low nominal numbers show the flat-plate/T-slot concept is plausible; they do not resolve fastener preload, fatigue, frame allowables, shock, bench pull-out, or proof testing.

## Release blockers

1. `MV0-FC01`/`INSPECT-MECH-003` now control the PCD22 check, and `MV0-FC02`/`INSPECT-MECH-004` control the selected S102 32 x 16 tapped rectangle. Execute both against received parts. Candidate 2.70 mm clearance holes remain unreleased until physical fit, gauge/thread criteria, process capability, and acceptance tolerances are recorded and reviewed.
2. R21 corrected the invalid assumption that both ends of both links use PCD22. `MV0-001` now distinguishes H101 output and S102 body-frame interfaces; `MV0-003` uses the selected S102 pattern; `MV0-002` has no released gripper holes. See `docs/hr-v0-joint-interface-fasteners-p0.1.md`.
3. Receive and identify every kit component under `INSPECT-MECH-005`, then select exact M2.5/M8 fasteners, engagement, torque, locking and inspection marks. The expected kit inventory does not prove screw grade, allocation, preload or structural capacity.
4. The P0.1 hard-stop study defines the J1/J2 convention, four candidate 5-degree-offset datums, 50 mm contact-radius study, allocated-mass energy cases and validation route. Release the actual backed-up bumper/catch, brackets, fasteners, tolerance stack and guarded impact evidence before motion.
5. Release the gripper mechanism, compliant pads, detachment retention and force/current characterization.
6. Add cable paths, bend-radius checks, strain relief and swept-volume collision evidence.
7. Design the fixed polycarbonate guard and receiver fixture from the measured stop trajectory.
8. Survey the actual bench substrate and select anchor hardware using pull-out/shear and edge-distance evidence.
9. Correlate CAD masses and geometry with the first article, then obtain qualified mechanical review.

The generated DXF/STEP files are suitable for comparable quotations only. They are not suitable for an approved cutting order.
