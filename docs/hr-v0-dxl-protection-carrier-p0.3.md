# HR-V0 DXL protection carrier P0.3 and PCBA DFM inquiry P0.1

> **PRELIMINARY - NOT APPROVED FOR SUPPLIER UPLOAD, QUOTATION, PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, MOTION, OR ENERGIZATION**

- Carrier identifier: `HR-V0-DXL-PROT-CARRIER-P0.3`
- DFM identifier: `HR-V0-DXL-PROT-DFM-P0.1`
- Review round: R159
- Date: 2026-08-09
- Preferred inquiry route: MacroFab capability screen only; provider not selected
- Provider contacts/uploads/quotes/orders: 0
- Physical articles/tests/qualified approvals: 0

## Result

R159 advances the R158 current-limiter evaluation carrier toward a provider-reviewable PCBA package without authorizing any external action. The RPW0010A copper, mask and paste geometry corrected in R158 is unchanged. Two manufacturing-control gaps are corrected:

1. P0.2's native KiCad soldermask-dam rule permitted 0.05 mm even though the screened provider publishes 0.10 mm as its minimum. P0.3 enforces 0.10 mm for the native mask-dam rule and 0.10 mm for minimum/default copper clearance.
2. P0.2 had no board registration features. P0.3 adds three non-collinear board-only global fiducials at `(10,10)`, `(90,10)` and `(10,50)` mm. Each has 1.0 mm exposed copper and a 2.0 mm mask opening and is excluded from BOM/position output.

P0.3 remains an evaluation carrier. It does not solve TPS25946 reverse current, regeneration energy, system protection coordination or any safety function.

## Current provider capability screen

MacroFab's official live capability page, accessed 2026-08-09, is used only to test whether a written DFM inquiry is plausible. It publishes support for 2-36 layers, 1.6 mm standard thickness, QFN/TQFN pitch down to 0.3 mm, mixed SMD/PTH assembly, 0.0762 mm trace/spacing/annular-ring minimums, 0.1524 mm paste aperture/clearance minimums, a 0.10 mm soldermask-dam minimum, AOI, QFN X-ray and first-article images.

The internal screen passes broad dimensional capability but does not select MacroFab or establish process acceptance. The RPW mask dam is exactly at the published minimum, compound L-shaped paste apertures require written stencil disposition, and the following remain `SELECTION REQUIRED`: laminate, stackup, copper weight, surface finish, paste/flux/alloy, stencil thickness, workmanship class and exact inspection deliverables.

## Controlled inquiry package

- 24 provider-capability rows, including all at-limit and selection-required items.
- 24 blocking DFM questions, all `NOT SENT`, unanswered and open.
- 23 proposed submission files bound to repository paths, byte counts and SHA-256 hashes; every row says `NOT UPLOADED` and upload authorization `NO`.
- 18 blank first-article checks covering serialization, stackup, component traceability, placement, RPW SPI/AOI/X-ray, PTH soldering, cleanliness, continuity, isolation, deviations and independent disposition.
- Exact denial state for provider selection/contact, upload, quotation, purchase, fabrication, assembly, connection, energization and functional-safety credit.

The proposed files are a controlled inquiry set, not a supplier upload archive. A provider may not silently modify mask, paste, footprint, drill, outline, BOM or placement data; every proposed change must be returned for project disposition.

## Native validation

- Five native KiCad sheets: ERC 0 errors / 0 warnings.
- PCB: DRC 0 violations / 0 unconnected pads / 0 footprint errors within the modeled rules.
- 100 x 60 x 1.6 mm nominal board, four copper layers, 20 BOM placements, four board-only mounting holes and three board-only fiducials.
- 69 routed track segments, 22 vias, 0.18 mm minimum routed track, 0.30 mm minimum via drill and 0.15 mm minimum via annular ring.
- A canonical P0.2/P0.3 fingerprint proves parity across tracks, vias, all non-fiducial pads/nets, Edge.Cuts, zones, layer count and thickness; the only excluded intentional changes are native design rules, three fiducials and revision/status metadata.
- Exact release-source, DFM-copy, file-hash, denial-state and gate-state checks are native-machine verified.

Native checks and a provider capability page do not establish fabrication yield, assembly quality, electrical/thermal performance, physical suitability or permission for work.

## Controlled artifacts

- Native source: `electrical/kicad/hr-v0-dxl-protection-carrier-p0.3/`
- Manufacturing-data source: `electrical/manufacturing/hr-v0-dxl-protection-carrier-dfm-p0.1/`
- Circuit-parity record: `electrical/manufacturing/hr-v0-dxl-protection-carrier-dfm-p0.1/p0.2-p0.3-circuit-parity.json`
- Interactive guide and synchronized package: `release/hr-v0/dxl-protection-carrier-p0.3/`
- Generator: `tools/generate_hr_v0_dxl_protection_carrier_p03.py`
- Native checker: `tools/check_hr_v0_dxl_protection_carrier_p03.py`

R159 advances the carrier's internal DFM readiness only. Provider response, selected process, qualified review, first-article evidence and every physical-work authorization remain open.
