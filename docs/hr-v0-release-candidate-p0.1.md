# HR-V0 release-candidate configuration P0.1

Status: **PRELIMINARY—NOT APPROVED FOR FABRICATION OR ENERGIZATION**

Candidate identifier: `HR-V0-RC-P0.1`

System baseline: `HR-30-SYS-R0.2`

## Purpose

This package makes the current HR-V0 review configuration reproducible. It does not convert proposed parts into selected parts, close physical evidence, or authorize a build. The exact Git commit containing `release/hr-v0/release-candidate.json` and its verified file manifest identifies the candidate reviewed at that commit.

The manifest covers every Git-tracked or non-ignored candidate file except the manifest itself. That exception prevents a recursive self-hash. The manifest includes its own metadata, generator, checker, engineering sources, generated candidates, BOMs, requirements, risks, procedures, primary/vendor references, review history and configuration files.

The manifest hashes Git's canonical staged blobs, not platform-dependent checkout bytes. Clean-worktree enforcement separately proves that the checkout corresponds to the committed candidate. Existing domain-specific line-ending rules remain unchanged so the release-control layer does not rewrite established CAD, ECAD, firmware or vendor evidence formats.

## Current product set

| Domain | Current candidate | Release boundary |
|---|---|---|
| Systems | `HR-30-SYS-R0.2` | integrated preliminary baseline |
| Electrical | `Project Button Electrical V3-P1.15-CARRIER-CANDIDATE` / `V3-P1.17-OBSERVATION-P0.5-CANDIDATE` / `DXL-STAR-P0.2-CARRIER-CANDIDATE` / `HR-V0-DXL-PROT-CARRIER-P0.3` / `HR-V0-DXL-PROT-CARRIER-HARNESS-P0.1` / `HR-V0-DXL-CARRIER-INTEGRATION-P0.1` / `HR-V0-DXL-CARRIER-MOUNT-IF-P0.1` / `HR-V0-CONFIG-REC-P0.3` | P1.15 remains the direct watchdog/core binding and P1.17 the current observation-integrated system view; native recorded ERC/DRC checks pass, but provider/process, physical terminals/ratings, harness terminations/lengths, received fit, Pi acceptance, fault/thermal/EMC tests, independent acceptance and qualified review remain open; no wiring, drilling, fabrication, connection, motion or energization release |
| Watchdog PCB | `PCB-P0.9` / `HR-V0-WD-IC-META-P0.1` / `HR-V0-WD-LAND-P0.1` / `HR-V0-WD-PCBA-RFI-P0.1` / `HR-V0-WD-PCBA-DATA-P0.2` / `HR-V0-WD-BOM-BIND-P0.1` / `HR-V0-WD-CAM-P0.2` / `HR-V0-E2-P115-PARITY-P0.1` | routed Harwin-shape-corrected candidate with all 42 exact identities in native KiCad fields plus exact BOM/placement/orientation data; current P1.15-bound quarantined CAM review outputs contain ten Gerber/job and five drill/map/report files, IPC-D-356, native DRC 0 and exact 42-reference internal parity; no supplier-normalized XYRS, provider/process acceptance, physical evidence, independent acceptance or work authorization; CAM P0.1 and PCB-P0.5 through P0.8 remain historical |
| Actuator star PCB | `DXL-STAR-P0.2-CARRIER-CANDIDATE` / `HR-V0-DXL-STAR-MFG-P0.2` | routed carrier-aware candidate with source-bound quarantined internal CAM, DRC 0 and exact placement/terminal parity; P0.1 CAM remains historical; provider/process, normalized XYRS, DFM, first article and physical qualification remain open |
| Mechanical | `HR-V0-MECH-P0.6` + `HR-V0-ARM-ARCH-P0.8-DWG-INTEGRATED-CANDIDATE` + inherited `HR-V0-ARM-ARCH-P0.7` analytical basis + `HR-V0-HS-P0.3` + `HR-V0-J2-STOP-P0.1` + `HR-V0-MECH-BOM-BIND-P0.2` | The complete arm imports the five exact current P0.8 custom-part STEP hashes at the controlled transforms and regenerates nominal collision/clearance/stop evidence; received MTR/fit, T-slot capacity, qualified analytical acceptance, torque/locking/reuse, remaining stops, physical stopping/tolerance closure, cables/guard, FAI, proof and qualified review remain open |
| Frame/sign convention | `HR-V0-FRAME-CONV-P0.1` | right-handed A0/J1/J2/G1 convention and engineering signs controlled; legacy guard layout quarantined; physical datum survey, raw direction/scale/zero, gripper registration, CFG-002 fault proof and HR-30 mirroring remain open |
| Arm fabrication | `HR-V0-FAB-RFI-P0.2-WITHDRAWN` | zero active supplier packets; replacement architecture required |
| Firmware | `HR-V0-FW-P0.4` / `HR-V0-SUP-P0.3` / `HR-V0-ACT-P0.3` / `HR-V0-WD-BUILD-P0.2` / `HR-V0-DXL-TRANSPORT-P0.3` / `HR-V0-DXL-CURRENT-ENV-P0.1` / `HR-V0-LIMITS-P0.2` | fail-closed source records P0.8 as required mechanical identity, P0.2 as manufacturing identity and P0.7 only as inherited kinematic basis; acceptance hashes, calibration/current/limit evidence, target SDK/install, received actuator configuration, flash, execution and HIL validation remain unresolved or absent |
| Functional safety | `HR-V0-FSA-P0.1` | allocation candidate; `DF-01` has zero safety credit; no PLr/SIL assigned |
| BOM / evaluation acquisition / receiving | `HR-V0-BOM-P0.1` / `EVALUATION-BATCH-A` / `HR-V0-EVAL-BATCH-A-ACQ-P0.1` / `HR-V0-EVAL-BATCH-A-RCV-P0.1` / `HR-V0-ACT-AC-CORD-P0.1` / `HR-V0-MECH-BOM-BIND-P0.2` / `DXL-STAR-P0.2-CARRIER-CANDIDATE` / `HR-V0-DXL-PROT-CARRIER-P0.3` / `HR-V0-DXL-PROT-CARRIER-HARNESS-P0.1` / `HR-V0-DXL-CARRIER-MOUNT-IF-P0.1` / `HR-V0-CONFIG-REC-P0.3` | 91 closure groups remain fail closed; the five custom parts are exact-identity bound but not provider-, DFM-, FAI- or receiving-approved; carrier PCBAs, harnesses and mounting hardware remain represented but not procurement-released; physical and qualified acceptance remain open |
| E2 commissioning | `HR-V0-E2-SEQ-P0.1` / `HR-V0-E2-HW-P0.4` / `HR-V0-E2-P115-PARITY-P0.1` | P1.15-bound 15-step control-only procedure and 23-row hardware slice; actuator source and complete actuator subset absent or unwired; twelve holds and five forms unexecuted; authorization `NOT AUTHORIZED` |
| Governance | `HR-V0-GOV-P0.3` / `HR-V0-REQ-ATOMIC-P0.2` | complete source-bound coverage of 81 requirements, 40 risks and 30 gates; 458 draft child candidates plus blank acceptance rows cover all 66 compound parents after 62 internal separations; independent atomicity/coverage acceptance, named people, qualifications, history, executed evidence, residual-risk decisions, signatures and approvals remain open |
| Assembly sequence | `HR-V0-BUILD-TRAVELER-P0.1` / `HR-V0-CONFIG-REC-P0.3` | integrated 14-phase / 85-step unpowered build-order candidate synchronized to P0.8/P0.2 with 21 through-E2 gates and 14 holds mapped; zero steps authorized/executed; BT-P13 connection and powered work prohibited |

Electrical V2.1 remains preserved as a reviewed historical baseline. It does not override V3's HR-V0 correction intent. HR-30A/B/C/D/W remain later program stages and are not released by this HR-V0 candidate.

## Generate and verify

From the repository root with Python 3, first stage every deliberate candidate change except the generated manifest. Generation fails if any non-ignored package file remains untracked. Then run:

```powershell
python tools/generate_hr_v0_release_manifest.py
git add release/hr-v0/HR-V0-RC-P0.1-file-manifest.csv
python tools/check_hr_v0_release_manifest.py
```

After committing all candidate files, a clean clone must pass:

```powershell
python tools/check_hr_v0_release_manifest.py --require-clean
```

Any content change, added package file, deleted package file, role change, size change, or hash change invalidates the manifest until it is deliberately regenerated and reviewed.

## Why EG-002 remains partial

The deterministic file set closes the earlier ambiguity about which artifacts travel together. It cannot itself prove acceptance. `EG-002` remains partial until:

1. the candidate commit is merged or otherwise immutably accepted by the configuration manager;
2. the exact remote commit is recorded in the controlled release record;
3. a clean clone reproduces the manifest and every applicable domain checker;
4. deviations and unresolved selections are dispositioned; and
5. accountable engineering and qualified safety reviewers sign the applicable release stage.

This configuration candidate does not close any fabrication or energization gate.
