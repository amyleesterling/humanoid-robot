# Independent review request - HR-V0 receiver guide interface R130

Review `HR-V0-RECEIVER-GUIDE-IF-P0.1` as an unreleased interface-correction candidate, not as a fabrication package, safety validation or energization approval.

Status: **PRELIMINARY - NOT APPROVED FOR FABRICATION, MOTION OR ENERGIZATION**

## Reproduce

```powershell
& 'C:\Users\amyle\Documents\New project\.venvs\hr-v0-cad\Scripts\python.exe' tools/generate_hr_v0_receiver_guide_interface.py
& 'C:\Users\amyle\Documents\New project\.venvs\hr-v0-cad\Scripts\python.exe' tools/check_hr_v0_receiver_guide_interface_p01.py
```

## Review questions

1. Does the package correctly interpret the current official igus `TWA-01-20` K2 mounting pattern as `53 x 40 mm`, four M6 threads, without inferring thread depth or screw selection?
2. Is the proof that the R129 `FAB-REC-003` 20 x 50 mm tab cannot cover that pattern correct in both orientations?
3. Are the official product, drawing, CAD-viewer, catalog and vertical-system records cited with sufficient provenance, and is the absence of received STEP/CAD stated honestly?
4. Is the candidate right-angle orientation geometrically coherent with the controlled receiver coordinate frame and the 73 x 80 mm vertical face?
5. Are all 24 K2 and platen candidate centers reproduced correctly, with diameters and final machining explicitly held?
6. Is the 30 mm symmetric rail end spacing shown only as arithmetic derived from a 120 mm candidate length and 60 mm pitch, without presenting a configured order code?
7. Are the bracket mass and four-bracket-plus-platen subtotal arithmetically correct, with fasteners, pads, shock moving parts and effective moving mass excluded?
8. Does the package adequately expose the unresolved fixed/floating carriage arrangement, alignment and overconstraint risk?
9. Do all holes, threads, fasteners, allowables, loads, application acceptance and proof requirements remain fail-closed?
10. Do `EG-008` and `EG-009` correctly remain partial, with no physical result or fabrication/energization authorization implied?

Provide BLOCKER / MAJOR / MINOR findings with exact artifact, row, coordinate, feature, source, calculation, assumption and gate references. Identify every item still preventing final holes, machining, assembly, proof or energization. Do not infer hardware, order codes, settings, allowables, approvals or work authorization.
