# R160 validation record

> **PRELIMINARY - NOT APPROVED FOR SUPPLIER UPLOAD, QUOTATION, PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, MOTION, OR ENERGIZATION**

Date: 2026-08-09

Package: `HR-V0-DXL-PROT-CARRIER-HARNESS-P0.1`

## Configuration checked

- P0.3 carrier `JIN1/JOUT1` terminal schedule and BOM
- DXL-STAR-P0.1 `JP1/JP2/JP3` connector schedule
- Electrical V3 branch interface schedule
- JST VH catalog/product/handling records and Belden 9918 revision 0.515 product record

## Deterministic result

`tools/check_hr_v0_dxl_protection_carrier_harness_p01.py` passes:

- two harness identities;
- eight interface rows;
- exact candidate `VHR-2N`, `SVH-21T-P1.1`, `9918 002100`, and `9918 010100` identities;
- carrier pin 1 positive / pin 2 return parity;
- DXL-star `JP1/JP2/JP3` parity;
- four held cut/crimp rows;
- ten unexecuted process steps;
- eighteen open, unsigned acceptance rows;
- nine `SELECTION REQUIRED` records;
- mirrored engineering/release files and deterministic manifests;
- all authorization and safety-credit flags false.

Repository regression with the existing CadQuery-enabled validation environment passed 104/104 pre-R160 non-`pcbnew` checkers plus the new R160 checker. Before staging, the release-manifest checker separately and correctly rejected the new untracked files. After the exact R160 scope was added to the index, the release manifest was regenerated for 2,499 controlled package files and the complete sweep was rerun.

Final staged result: release manifest PASS at 2,499 files; standard checker sweep PASS at 105/105. No native PCB source changed in R160, so the prior R159 KiCad 10.0.5 ERC/DRC and 10/10 native-checker record remains the controlling native-ECAD result and is not represented as a newly executed native sweep.

Rendered desktop guide QA passed at 1280 px: title and warning were visible without clipping, document width was 1265 px inside a 1280 px viewport, body/warning text computed to 16 px and metadata to 14 px. All six linked CSV artifacts are present and hash-bound. No mobile screenshot is claimed in this record.

No harness exists. No cut, strip, crimp, pull, continuity, polarity, isolation, retention, voltage-drop, thermal or fault test was executed.
