# Project Button Configuration Management

Package baseline: **HR-30-SYS-R0.2**  
Baseline date: 2026-08-06  
Status: preliminary engineering baseline; not approved for fabrication, procurement, or energization

## Identifier hierarchy

- **HR-30-SYS-R0.2** identifies this integrated systems-specification package.
- Each controlled document retains its own document ID and revision. A document revision is not the package baseline.
- **Project Button Electrical V2.1** identifies the connected KiCad electrical package. Its revision is independent of the systems package.
- **Project Button Electrical V3-P0.1** identifies the historical R16 connected candidate retained in Git history.
- **Project Button Electrical V3-P0.2** identifies the historical R17 restart-chain correction candidate.
- **Project Button Electrical V3-P0.3** identifies the historical R18 voltage-boundary correction with opaque feedback-interface blocks.
- **Project Button Electrical V3-P1.4** identifies the current schematic correction candidate. It retains P1.1's pin-level feedback circuit and test access, P1.2's separate `DXL-STAR-P0.1` actuator-injection boundary and P1.3's current K1/K2 application record. P1.4 adds fail-closed received-lot terminal control for RESET and ARM without inventing the four unresolved terminal markings. The separate current watchdog-board candidate is **PCB-P0.5**, a DRC-clean routed/test-access candidate with separate floating 2 mm x 2 mm `SUB1`/`SUB2` thermal areas and a source-backed 0.1524 mm U.S. two-layer prototype-process envelope. Source-side contact construction, harness current sharing, protection/distribution, received measurements, supplier archive acceptance, physical test access, thermal/pulse/DC-bias/EMC evidence, COM-slew, brownout, HIL/fault evidence, received terminals, panel human factors and qualified review remain open. `V3-P1.4`, `PCB-P0.5`, and `DXL-STAR-P0.1` have not superseded V2.1 and are not released baselines.
- **HR-V0-FW-P0.1** identifies the preliminary watchdog/supervisor source candidate. It has executable source tests but no released binary or HIL evidence.
- **HR-V0-MECH-P0.3** identifies the current mechanical correction hold. R53 uses exact manufacturer-coordinate ROBOTIS STEP files under **HR-V0-ROBOTIS-IF-P0.1**, withdraws the P0.2 J1/J2/G1 chain and `MV0-001` through `MV0-003`, and replaces **HR-V0-FAB-RFI-P0.1** with **HR-V0-FAB-RFI-P0.2-WITHDRAWN** containing zero supplier ZIPs. R56 supersedes R55's thin-adapter candidate with **HR-V0-ARM-ARCH-P0.3**: corrected XM540/S102 registration, ROBOTIS rectangular link pattern, vertical 20-2040 members, a 9.525 mm nominal adapter, exact Westfield fastener candidates on hold, explicit fastener/tool/load screens and a 221-pose collision screen. It does not supersede the P0.3 hold. The first nominal modeled contact at 122 degrees makes the 120-degree ceiling provisional until continuous collision proof, hard-stop and stopping-overtravel margin close. The base cuts and **HR-V0-FRAME-P0.2** remain candidate coordination evidence. `MECH-005` / `AUDIT-MECH-012` and `MECH-006` / `INSPECT-MECH-013` still require certified adapter material and local analysis, received fastener stacks, torque/locking rules, cables, tolerances, FAI, physical proof and qualified disposition before any arm quotation or fabrication route can reactivate.
- **HR-V0-RC-P0.1** identifies the deterministic configuration candidate defined by `release/hr-v0/release-candidate.json` and `release/hr-v0/HR-V0-RC-P0.1-file-manifest.csv`. The exact Git commit containing a passing manifest is the candidate configuration identifier. This label freezes a reviewable file set only; it is not a fabrication, procurement, software, safety, or energization release.
- **HR-V0-BOM-P0.1** identifies the 71-group system-BOM closure register and sixteen-line Evaluation Batch A boundary. R56 records the selected S102 body-frame, 20-2040/end-tap architecture and three Westfield arm-interface fastener order codes as exact candidates on hold, not as evaluation-purchase lines. The grouped adapter and structural-fastener rows remain design-required because material certification, local analysis, complete hardware allocation, torque, locking, received fit and proof remain unresolved; no received candidate is application-released by purchase or receipt.
- Website releases are identified by their website Git commit and hosted version. A website release is a presentation of controlled artifacts, not an engineering revision.

The label **V2.2** is not a released engineering identifier and must not be used for this package.

## Controlled baseline summary

This baseline contains 75 draft requirements and 40 open risks. HR-V0 and HR-30 release specifications remain unbuilt and unvalidated. Individual files may advance only through a recorded change that updates their revision, linked requirements, evidence, and review disposition as applicable. `HR-V0-RC-P0.1` provides deterministic package membership and hashes; `EG-002` remains partial until the candidate is merged or otherwise immutably accepted and qualified reviewers sign the applicable stage. `HR-V0-BOM-P0.1` advances `EG-003` to partial but does not release a complete machine BOM. `HR-V0-MECH-P0.3` preserves base coordination while explicitly withdrawing the invalid arm chain; `EG-005` through `EG-008` remain partial pending replacement geometry, physical evidence and qualified review.

## Release rule

Neither a clean ERC result nor a website deployment constitutes design approval. The package remains **PRELIMINARY—NOT APPROVED FOR ENERGIZATION** until the applicable selections, calculations, physical tests, and qualified electrical and functional-safety reviews are complete.
