# Independent review request - HR-V0 collapse envelope P0.1

Please review `HR-V0-COLLAPSE-ENV-P0.1` as a continuous known-geometry screen and receiver-role correction, not a completed guard or receiver design.

Status: **PRELIMINARY - NOT APPROVED FOR FABRICATION, MOTION OR ENERGIZATION**

## Reproduce

```powershell
& 'C:\Users\amyle\Documents\New project\.venvs\hr-v0-cad\Scripts\python.exe' tools/generate_hr_v0_collapse_envelope.py
& 'C:\Users\amyle\Documents\New project\.venvs\hr-v0-cad\Scripts\python.exe' tools/check_hr_v0_collapse_envelope_p01.py
```

## Review questions

1. Are all controlled P0.7 known moving B-Reps assigned to the correct J1-only or J1-plus-J2 group?
2. Does the AABB-corner Y-Z radius continuously contain each rigid shape under X-axis rotation?
3. Is the J1-to-J2 distance plus J2-local radius a valid conservative continuous bound under arbitrary two-axis rotation?
4. Do independent calculations reproduce `338.740914 mm`, X `-42..+42 mm`, and the controlling `360 mm` ledger radius?
5. Do the controlled inputs fit the current 450 mm radial, 400 mm depth and 950 mm height reservations with the reported margins?
6. Is the 90 mm residual properly treated as unallocated rather than safety/stopping/cable clearance?
7. Does `26 mm` tray top versus `140 mm` arm-envelope bottom reproduce the `114 mm` separation?
8. Is reclassifying the current floor tray as object-catch-only technically correct?
9. What exact passive arm-receiver or stop-supported-rest architecture should proceed to design?
10. Do the exclusions and eighteen-row metrology scaffold capture the remaining proof boundary?

Provide BLOCKER / MAJOR / MINOR findings with exact component, equation, CSV row, geometry, gate and evidence references. State separately whether the package is ready for receiver design, fabrication, physical power-loss testing, motion or energization. Passing calculations are not approval.
