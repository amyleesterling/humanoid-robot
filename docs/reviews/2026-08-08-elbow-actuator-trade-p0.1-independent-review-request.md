# Independent review request — HR-V0 elbow actuator trade P0.1

> **PRELIMINARY — NOT APPROVED FOR QUOTATION, PROCUREMENT, FABRICATION, ASSEMBLY, MOTION, CONNECTION, OR ENERGIZATION.**

Please perform an independent mechanical/electrical/controls review of `HR-V0-ELBOW-TRADE-P0.1`. This is an architecture hold and planning sensitivity, not a request to approve XM430 or energization.

## Controlled inputs

- `docs/hr-v0-elbow-actuator-trade-p0.1.md`
- `docs/hr-v0-moving-mass-closure-p0.1.md`
- `bom/hr-v0-moving-mass-ledger.csv`
- `cad/hr-v0/generated/arm-architecture-p0.7/architecture-summary.json`
- `release/hr-v0/elbow-actuator-trade-p0.1/`
- `cad/vendor/robotis/x430-fr12-r91/`
- `docs/hr-v0-actuator-current-envelope-p0.1.md`
- `docs/hr-v0-boston-fabrication-decision-p0.2.md`

## Questions requiring explicit disposition

1. Recompute the P0.7 692.758 g incomplete subtotal, 57.242 g headroom, 83.000 g actuator delta, and all four trade rows without trusting the project summary.
2. Confirm that every omitted moving frame, fastener, spacer, bumper, gripper-mechanism, guard, connector and cable item remains visible and that no STEP volume is credited as physical mass.
3. Confirm that the 140.242 g and 198.225 g values are correctly labeled same-axis planning sensitivities, not mass passes or selectable configurations.
4. Check the official ROBOTIS XM430/XM540 mass, 12 V stall-current/torque, no-load speed, stall-versus-continuous warning, connector information and source-file links against the current primary pages; record access date and any visible revision.
5. Independently challenge whether the 1.158 N·m J2 and approximately 4.170 N·m J1 screens remain useful after a geometry change. Do not turn a stall-endpoint ratio into continuous torque or safety margin.
6. Check the three-actuator 11.1 A to 9.0 A catalog-current sensitivity and the limited statement about the JST EH 3 A headline rating. Confirm that conductor/contact construction, derating, transient, thermal, protection and measurement evidence stays open.
7. Parse and inspect the five acquired manufacturer files; verify hashes, identities, geometry units, drawing content, datums, tolerances, frame compatibility and whether the X430 idler assembly is the correct exact model for the proposed TTL actuator.
8. Determine whether FR12-H101K/FR12-S102K/H104 and the proposed link/stop topology can be integrated without an unsupported load path, interference, inaccessible fasteners or cable/guard failure.
9. Challenge all twelve architecture holds and identify any missing dependency invalidated by a P0.8 branch.
10. Confirm that P0.7 remains controlled, XM430 is not selected, and the R90 supplier route is held rather than silently superseded.
11. State the minimum analytical and physical evidence required before actuator selection, custom-metal quoting, procurement, fabrication, connection, motion and energization as separate decisions.
12. Report findings as BLOCKER / MAJOR / MINOR with exact file, row, part, interface, calculation or requirement references and primary-source links.

## Reproduction

```powershell
& 'C:\Users\amyle\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' tools/check_hr_v0_elbow_actuator_trade.py
& 'C:\Users\amyle\Documents\New project\.venvs\hr-v0-cad\Scripts\python.exe' -c "import cadquery as cq; from pathlib import Path; [print(p.name, len(cq.importers.importStep(str(p)).vals())) for p in Path('cad/vendor/robotis/x430-fr12-r91').glob('*.stp')]"
```

Do not mark the robot approved for fabrication or energization. A clean checker proves file identity and bounded arithmetic only.
