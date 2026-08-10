# HR-V0 DXL injection allocation binding P0.1

**PRELIMINARY - NOT APPROVED FOR SUPPLIER UPLOAD, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, MOTION, OR ENERGIZATION**

Identifier: `HR-V0-DXL-INJECT-BIND-P0.1`

Round: R152

## Configuration correction

Legacy `BOM-035` described three separate VDD-isolating injection modules. That allocation contradicts the current controlled electrical design:

- Electrical V3-P1.14 contains exactly one `INJ1` central DXL-star block;
- native DXL-STAR-P0.1 contains exactly one board with three isolated positive rails, one common data net and one common return;
- `BOM-051` is the held parent PCB identity for that board; and
- all eighteen Electrical V3 INJ1 terminals reconcile exactly to the eighteen native board terminals.

R152 therefore reclassifies `BOM-035` as an integrated function under `BOM-051`, with parent-controlled quantity one and no separate purchase. It does not add or remove any electrical path.

## Unchanged release boundary

Twelve residual hold groups remain open. They preserve the R151 board fabrication/assembly holds plus connector/header/contact receiving evidence; harness construction; branch protection; exact conductors and terminations; the JST EH 3 A versus XM540 4.4 A stall-current conflict; DXL waveform/EMC; no-backfeed and power sequencing; grounding/shielding; thermal/fault validation; qualified review; and separate work authorization.

System BOM closure becomes 17 evaluation candidates, 40 exact candidates on hold, three grouped-component holds, 19 selection-required groups, four exclusions and two integrated items. This is configuration cleanup only. `EG-003`, `EG-004` and `EG-015` remain partial.

## Controlled evidence

- [Interactive allocation guide](../release/hr-v0/dxl-injection-binding-p0.1/index.html)
- `release/hr-v0/dxl-injection-binding-p0.1/bom-allocation-binding.csv`
- `release/hr-v0/dxl-injection-binding-p0.1/allocation-parity.csv`
- `release/hr-v0/dxl-injection-binding-p0.1/residual-holds.csv`
- `tools/generate_hr_v0_dxl_injection_binding.py`
- `tools/check_hr_v0_dxl_injection_binding_p01.py`

No supplier contact, upload, quotation, purchase, fabrication, assembly, physical article, connection, motion, energization or safety credit is created.
