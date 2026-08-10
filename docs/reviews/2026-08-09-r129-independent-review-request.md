# Independent review request - HR-V0 passive receiver R129 detail

Review `HR-V0-PASSIVE-ARM-RECEIVER-DETAIL-P0.2` as an unreleased mechanical and passive-containment candidate, not as a fabrication package, safety validation or energization approval.

Status: **PRELIMINARY - NOT APPROVED FOR FABRICATION, MOTION OR ENERGIZATION**

## Reproduce

```powershell
& 'C:\Users\amyle\Documents\New project\.venvs\hr-v0-cad\Scripts\python.exe' tools/generate_hr_v0_passive_arm_receiver_detail.py
& 'C:\Users\amyle\Documents\New project\.venvs\hr-v0-cad\Scripts\python.exe' tools/check_hr_v0_passive_arm_receiver_detail_p02.py
```

## Review questions

1. Are all manufacturer names and exact candidate identities supported by the cited current primary sources?
2. Has the package avoided inferring the configured `TS-01-20` rail order code, mounting-hole pattern, connector or fastener detail, tolerance, rating or application approval?
3. Are vendor-part shapes presented honestly as planning envelopes rather than received manufacturer CAD?
4. Are the three fabricated STEP/DXF files demonstrably hole-free blanks rather than machinable final parts?
5. Are the nominal `9.625 mm` backup gap and `1.497 mm` post-stroke residual arithmetically correct, and is the unresolved tolerance/deformation boundary sufficiently explicit?
6. Does the 80/20 bracket and suggested-hardware count follow the primary product page without implying a receiver-specific joint allowable?
7. Are the platen, guide, shock, catch, bracket, rail, post, brace, base/guard and anchor load paths complete enough to expose every unresolved interface?
8. Are the X/Y/Z receiver bounds and nominal guard margins consistent with the controlled R127/R128 geometry?
9. Do the contact-layer cut plan, retention hold and missing dynamic material behavior prevent accidental energy-absorption credit?
10. Do all twelve holds remain fail-closed, with the original 28 R127 physical records unexecuted and `EG-008/009` partial?

Provide BLOCKER / MAJOR / MINOR findings with exact artifact, row, feature, source, calculation, assumption and gate references. Identify every item that would still prevent final holes, fabrication, assembly, physical test or energization. Do not infer hardware, settings, allowables, approvals or work authorization.
