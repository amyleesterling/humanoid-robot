# Independent review request - HR-V0 passive arm receiver P0.1

Review `HR-V0-PASSIVE-ARM-RECEIVER-P0.1` as a preliminary geometry and sizing candidate, not a released receiver or accepted shock-absorber application.

Status: **PRELIMINARY - NOT APPROVED FOR FABRICATION, MOTION OR ENERGIZATION**

## Reproduce

```powershell
& 'C:\Users\amyle\Documents\New project\.venvs\hr-v0-cad\Scripts\python.exe' tools/generate_hr_v0_passive_arm_receiver.py
& 'C:\Users\amyle\Documents\New project\.venvs\hr-v0-cad\Scripts\python.exe' tools/check_hr_v0_passive_arm_receiver_p01.py
```

## Review questions

1. Does the conservative AABB-corner method and radial half-cell deduction continuously bound the known commanded geometry?
2. Do independent calculations reproduce `383.106478 mm` minimum Z and `63.106478 mm` nominal residual?
3. Does the `180 x 800 mm` platen cover the controlled known X/Y region without conflicting with the fixed guard?
4. Is three-unit MA30M arithmetic correctly converted and carefully separated from application approval?
5. Are effective mass, impact velocity, parallel sharing, side load, adjustment, temperature and failure-mode holds complete?
6. Is the 2,000 N rail calculation arithmetically correct, and is it clearly prevented from becoming an allowable or proof-load claim?
7. What exact platen, guide, compliant-contact, bracket, post and anchor selections are needed before fabrication?
8. Does the candidate create new pinch, rebound, access, maintenance or single-shock-failure hazards?
9. What physical test progression and uncertainty are required before any gravitational power-loss test?
10. Do `EG-008` and `EG-009` correctly remain partial?

Provide BLOCKER / MAJOR / MINOR findings with exact artifact, row, equation, geometry, component and gate references. Use current primary manufacturer documents and record revision/date. Do not infer a shock setting, peak force, structural allowable, proof multiplier, guide, contact material, joint, fastener or work authorization. Passing arithmetic is not approval.
