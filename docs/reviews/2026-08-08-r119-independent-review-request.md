# R119 independent review request

Status: **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, CONNECTION, OR ENERGIZATION**

Review `HR-V0-COMPUTE-SEL-P0.1` and Electrical V3-P1.14 for exact-identity accuracy, source provenance, BOM/ECAD consistency and completeness of the retained application holds. This is not a request to approve purchase or energization.

## Review artifacts

- `electrical/vendor/raspberry-pi/compute-r119/source-manifest-p0.1.csv`
- `bom/hr-v0-compute-selection-p0.1.csv`
- `electrical/interfaces/hr-v0-compute-power-selection-p0.1.csv`
- `tests/forms/hr-v0-compute-receiving-template-p0.1.csv`
- `docs/hr-v0-compute-selection-p0.1.md`
- `electrical/kicad/project-button-v3/`
- `release/hr-v0/compute-selection-p0.1/index.html`

## Questions

1. Does Raspberry Pi's current configured 8GB unit-only/United States output support `SC1112` without inference from PIP list order?
2. Does its current US Type-A/black/United States supply output support `SC1158`?
3. Are product-brief facts kept separate from dynamic SKU-mapping evidence?
4. Do BOM-001/BOM-002, PI1/PSU3, release metadata and the receiving form describe the same candidates?
5. Are cooling, storage/image, USB-C and heartbeat harness retention, site, PD/load/brownout/thermal, grounding/EMC, runtime, physical and qualified-review evidence sufficiently fail-closed?
6. Is it correct that V3-P1.14 changes no net, terminal or safety topology from P1.13?
7. Do `EG-003` and `EG-010` correctly remain partial?

Return BLOCKER / MAJOR / MINOR findings with exact file, row, reference, source and gate. State separately whether the identities are accurate, whether the two lines are ready for a separately authorized evaluation purchase, and whether anything is ready for connection or energization.
