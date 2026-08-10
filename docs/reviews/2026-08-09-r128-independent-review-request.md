# Independent review request - HR-V0 passive receiver R128 verification

Review `HR-V0-PASSIVE-ARM-RECEIVER-VERIFY-P0.1` as an internal second-method verification of R127, not as an independent approval or released receiver.

Status: **PRELIMINARY - NOT APPROVED FOR FABRICATION, MOTION OR ENERGIZATION**

## Reproduce

```powershell
& 'C:\Users\amyle\Documents\New project\.venvs\hr-v0-cad\Scripts\python.exe' tools/generate_hr_v0_passive_arm_receiver_verification.py
& 'C:\Users\amyle\Documents\New project\.venvs\hr-v0-cad\Scripts\python.exe' tools/check_hr_v0_passive_arm_receiver_verification_p01.py
```

## Review questions

1. Is the closed-form two-axis Z expression correct for every P0.7 forearm AABB corner?
2. Does excluding interior stationary points follow from the current J1 `-20..70 deg` interval?
3. Do the four rectangle-boundary extrema prove the global `384.142618886 mm` minimum inside the stated AABB-corner model?
4. Is retaining R127's lower `383.106478372 mm` conservative bound appropriate?
5. Does re-importing the serialized STEP correctly establish nominal X/Y/Z bounds and the limiting `20 mm` guard margin?
6. Are STEP compound/object handling and volume/bounds interpretation sound?
7. Do Decimal re-derivations reproduce the ACE conversions and rail equations without upgrading catalog data to application approval?
8. Are all omitted gripper, object, cable, tolerance, deformation, load-sharing, peak-force, guide, joint, stop and physical-test inputs explicit?
9. Do `EG-008` and `EG-009` correctly remain partial?

Provide BLOCKER / MAJOR / MINOR findings with exact artifact, row, formula, assumption and gate references. Separately identify any flaw that invalidates R127's retained conservative result. Do not infer hardware, settings, allowables or work authorization.
