# R170 validation record

R170 issues `HR-V0-COMPUTE-STORAGE-P0.2` and advances `BOM-064` from an unidentified product branch to one exact candidate on hold.

- `SDCIT2/64GBSP` is copied from Kingston's current official industrial microSD datasheet.
- The package separates published family features from 64 GB capacity-specific evidence.
- It does not assign the family's maximum TBW statement to the selected 64 GB part.
- Raspberry Pi capacity and host-interface facts are treated as plausibility evidence only.
- Twelve receiving, application, software, physical-test and review holds remain open.
- No imaging, booting or powered evidence is recorded.

Validation must include `python tools/check_hr_v0_compute_storage_p02.py` and the full applicable repository regression. Browser QA must exercise all four filters at desktop and mobile widths. Passing proves digital consistency and presentation only.

`EG-002`, `EG-003`, `EG-005`, `EG-010`, `EG-017`, `EG-021`, `EG-022` and `EG-027` remain unresolved. No work authority or gate closes.

## Executed validation

- General repository checks: **99/99 passed**.
- Native KiCad-dependent checks under KiCad 10.0: **13/13 passed**.
- CadQuery geometry checks: **14/14 passed**.
- Pre-manifest total: **126/126 passed**. The staged release-manifest check is executed after staging and brings the controlled total to 127 checks.
- Browser QA at 1280 x 720 and 390 x 844 confirmed 16 px body and button text, 14 px technical labels, no horizontal overflow, the preliminary warning and zero console warnings/errors.
- Filter behavior: Everything = 4 visible cards; Published evidence = 2; Physical tests = 1; Safety boundaries = 1.

These results verify source consistency, parser compatibility, generated geometry invariants and guide behavior only. They are not received-media, boot, endurance, power-loss, electrical-test or functional-safety evidence.
