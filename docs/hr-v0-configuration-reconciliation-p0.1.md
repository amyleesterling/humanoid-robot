# HR-V0 carrier-integrated configuration reconciliation P0.1

Status: **PRELIMINARY—NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, MOTION, OR ENERGIZATION**

Identifier: `HR-V0-CONFIG-REC-P0.1`

Review synchronization: R163-R166

Date: 2026-08-09

## Decision

The current electrical integration candidate is one coherent chain:

1. `Project Button Electrical V3-P1.15-CARRIER-CANDIDATE`;
2. `DXL-STAR-P0.2-CARRIER-CANDIDATE`;
3. three `HR-V0-DXL-PROT-CARRIER-P0.3` limiter-carrier PCBAs;
4. three input and three output harnesses defined by `HR-V0-DXL-PROT-CARRIER-HARNESS-P0.1`;
5. `HR-V0-DXL-CARRIER-INTEGRATION-P0.1`;
6. `HR-V0-DXL-CARRIER-MOUNT-IF-P0.1`; and
7. `HR-V0-E2-P115-PARITY-P0.1` and P1.15-bound `HR-V0-E2-HW-P0.4`; and
8. the 91-group `HR-V0-BOM-P0.1` closure register.

This corrects configuration metadata that still identified P1.14 and DXL-STAR-P0.1 after the carrier-aware candidates were created. It freezes a review relationship; it does not certify that the parts are manufacturable, fitted, wired, protected, or safe to power.

## Supersession boundary

- Electrical V3-P1.14 remains a historical parity source. R165 proves the unchanged PCB-P0.9 watchdog and E2 subset at exact P1.15 digital parity.
- DXL-STAR-P0.1 remains historical evidence.
- `HR-V0-DXL-STAR-MFG-P0.1` is P0.1 CAM and **must not** be used to fabricate P0.2.
- Current P0.2 internal CAM review exists through `HR-V0-DXL-STAR-MFG-P0.2`; supplier/process acceptance, normalized XYRS, DFM and first article remain open.
- The former PCB-P0.9/E2 P0.3 P1.14 compatibility hold is digitally resolved by `HR-V0-E2-P115-PARITY-P0.1` and current E2 P0.4. Independent acceptance, a supplier-normalized watchdog manufacturing package, received physical configuration, tests and authorization remain open.

## BOM reconciliation

The generated closure now contains 91 unique groups: 17 evaluation candidates, 43 exact-candidate holds, 3 grouped-component holds, 21 selection-required groups, 4 exclusions, and 3 integrated/no-separate-purchase groups.

R163 adds:

- `BOM-087`: three P0.3 limiter-carrier PCBAs;
- `BOM-088`: three carrier input harnesses;
- `BOM-089`: three carrier output harnesses;
- `BOM-090`: twelve held Essentra standoff candidates; and
- `BOM-091`: twenty-four held Essentra screw candidates.

The P0.2 star CAM is internal review evidence only. The star board and carrier PCBAs have no selected provider/process or accepted first article. Harness source/star terminations and exact cut lengths remain selection required. Mounting coordinates are center candidates only and do not authorize drilling.

## Gate effect

`EG-002`, `EG-003`, `EG-004`, `EG-014`, and `EG-015` remain `partial`. R163-R166 improve traceability, digital parity, and current watchdog CAM binding but supply no received article, physical fit, wiring, thermal/fault/EMC result, supplier/process acceptance, functional-safety validation, independent acceptance, or qualified authorization.

The machine-readable package is in `configuration/hr-v0-config-reconciliation-p0.1/`; the human-readable guide is in `release/hr-v0/configuration-reconciliation-p0.1/`.
