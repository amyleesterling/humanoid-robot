# HR-V0 E2 evidence parity contract P0.2

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Date: 2026-08-11

Identifier: `HR-V0-E2-EVIDENCE-P0.2`

Hardware slice: `HR-V0-E2-HW-P0.4`

Sequence: `HR-V0-E2-SEQ-P0.1`
Configuration: `HR-V0-CONFIG-REC-P0.3`

## Correction

The historical unpowered-configuration P0.1 template named obsolete Electrical V3-P1.8 and HR-V0-MECH-P0.6 defaults. Its sample row also placed `HR-V0-RC-P0.1` in the `file_manifest_sha256` column instead of `release_candidate_id`. It must not be used for a future run.

P0.2 supersedes that future-use form and the P0.1 authorization form. It does not rewrite either historical file. The corrected configuration form separately records the core P1.15 ECAD, P1.17 observation system view, PCB-P1.0 manufacturing identity, complete P0.8 arm, current manufacturing-review chain and P0.3 configuration reconciliation.

## One combined E2 result

The hardware safety-logic form and software-authority form are now a mandatory one-to-one evidence pair for all twenty `E2-SL-*` cases. A hardware trace is insufficient without the synchronized controller evidence, and a software log is insufficient without the synchronized physical trace.

Every case requires:

- the actuator source physically absent and every actuator branch disconnected and covered;
- the expected hardware relay/coil/mirror/auxiliary state;
- active trajectory `NONE`;
- torque-enable request `FALSE`;
- stale replay `REJECTED`; and
- synchronized raw trace, controller log, article/configuration identity and independent disposition.

In `E2-SL-005` and `E2-SL-019`, the K1/K2 coil path may be permissive only inside the disconnected-load E2 boundary. `ON` does not mean actuator power or motion authority. The actuator source remains physically absent, no trajectory exists, no torque request exists and stale command replay must be rejected.

## Controlled inputs

`form-sha256-register.csv` hash-binds seven inputs. `configuration-identity-register.csv` controls eight exact configuration identities. `case-pairing-register.csv` binds the twenty hardware cases to the twenty software cases. `open-holds.csv` preserves seven blocking evidence groups.

EG-018 through EG-022 remain `partial`. The records are blank, the reviewers are unselected, the site and test limits are unresolved, and no physical run has occurred. Repository checks establish schema, identity, hashing and fail-closed consistency only.

## Sol review intake

The reviewer-reported baseline remains 18 BLOCKER, 30 MAJOR and 8 MINOR findings; 62/62 requirements draft; 106 unresolved electrical selections; and zero executed, approved verification results. R216 closes only this repository-owned E2 evidence-definition defect. It does not close any physical, functional-safety, stopping-time, grounding, contactor, battery, continuous-duty, walking or qualified-review finding.

**CURRENT DISPOSITION: NOT EXECUTED; NOT AUTHORIZED; NOT APPROVED FOR ENERGIZATION.**
