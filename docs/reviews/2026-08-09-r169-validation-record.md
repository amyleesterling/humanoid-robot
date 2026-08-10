# R169 validation record

R169 issues `HR-V0-LABEL-P0.1` and corrects the XT1 marker text to fit the selected manufacturer field.

- Six XT1 position markers are exactly `01` through `06` on `0828734` stock.
- Thirty device-reference and four short operator-legend markers are allocated to one configured `0830839` card.
- Four large legends exactly fill one configured `0828805` card.
- Twelve physical/application holds remain open.
- Wire markers, printing process, artwork approval, adhesion, durability, installed inspection and regulatory marking remain unresolved.

Validation must include `python tools/check_hr_v0_label_system_p01.py` and the full applicable repository regression. Browser QA must exercise all four guide filters at desktop and mobile widths. Passing proves digital consistency and presentation only.

`EG-003` and `EG-015` remain partial. No work authority or gate closes.

## Executed validation

- General repository checks: **98/98 passed**.
- Native KiCad-dependent checks under KiCad 10.0: **13/13 passed**.
- CadQuery geometry checks: **14/14 passed**.
- Pre-manifest total: **125/125 passed**. The release-manifest check is executed after staging and brings the controlled total to 126 checks.
- Browser QA at 1280 x 720 and 390 x 844 confirmed 16 px body and button text, 14 px technical labels, no horizontal overflow, the preliminary warning, and zero console warnings/errors.
- Filter behavior: Everything = 4 visible cards; XT1 markers = 1; Device references = 1; Door legends = 2.
- Browser QA found and corrected an invalid `font` shorthand that had caused 13.33 px filter-button text despite a nominal 16 px declaration.

These results verify source consistency, parser compatibility, generated geometry invariants and guide behavior only. They are not fabrication evidence, installed inspection, electrical test evidence or functional-safety validation.
