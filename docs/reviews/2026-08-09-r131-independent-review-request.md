# Independent review request - HR-V0 watchdog PCB mounting interface R131

Review `HR-V0-WD-MOUNT-IF-P0.1` as a current-source reconciliation and mounting-interface closure candidate, not as a fabrication package, safety validation or energization approval.

Status: **PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**

## Reproduce

```powershell
& 'C:\Program Files\KiCad\10.0\bin\kicad-cli.exe' pcb drc --exit-code-violations -o electrical/kicad/project-button-v3/validation/project-button-v3-r131-audit-drc.rpt electrical/kicad/project-button-v3/project-button-v3.kicad_pcb
& 'C:\Users\amyle\Documents\New project\.venvs\hr-v0-cad\Scripts\python.exe' tools/generate_hr_v0_watchdog_pcb_mounting_interface.py
& 'C:\Users\amyle\Documents\New project\.venvs\hr-v0-cad\Scripts\python.exe' tools/check_hr_v0_watchdog_pcb_mounting_interface_p01.py
```

## Review questions

1. Does the immutable P0.5 source actually contain the `+/-4.4 mm`, `2.00 x 1.60 mm` ISO1 lands described by the independent finding?
2. Does current P0.6 actually contain `+/-4.765 mm`, `1.52 x 1.78 mm` lands and the official Vishay URL?
3. Are the derived P0.5 `6.800 / 10.800 mm` and P0.6 `8.010 / 11.050 mm` inner-gap/overall-span values correct?
4. Is it configuration-correct to apply the original fabrication blocker to P0.5 while recognizing that P0.6 already supersedes it?
5. Does native KiCad 10.0.5 DRC reproduce zero violations, unconnected pads and footprint errors, without being overstated as physical evidence?
6. Are the four board-relative and candidate panel coordinates reproduced correctly from the controlled P0.6 board and panel envelope?
7. Are the Harwin `R30-1611000`, `R30-1611300` and `R30-1611500` identities and published properties supported by current primary records?
8. Is the `1.824574 mm` nominal hex-body-to-board-edge screen correct and sufficiently bounded against screw-head, washer, tolerance and load uncertainty?
9. Does the package correctly keep standoff height, every fastener, drilling, torque, insulation/bonding and assembly process unselected?
10. Do all twelve holds and eight blank receiving rows prevent accidental fabrication or energization credit?

Provide BLOCKER / MAJOR / MINOR findings with exact file, reference, coordinate, feature, source, calculation, assumption and gate references. Do not infer screws, washers, torque, order codes, process settings, standards disposition or work authorization.
