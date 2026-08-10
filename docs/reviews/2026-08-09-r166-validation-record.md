# R166 validation record

Status: **PRELIMINARY - NOT APPROVED FOR SUPPLIER UPLOAD, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, MOTION, OR ENERGIZATION**

`HR-V0-WD-CAM-P0.2` was generated with KiCad 10.0.5 from PCB-P0.9 and bound to the P1.15 native source manifest plus `HR-V0-E2-P115-PARITY-P0.1`.

Native DRC records zero violations, zero unconnected pads, and zero footprint errors. The package contains ten Gerber/job files, five drill/map/report files, nineteen registered CAM outputs, 42 exact internal placement-parity rows, eighteen open holds, and zero supplier/work authorizations.

The synchronized repository contains 123 controlled checkers and a 2,779-file release manifest. The first full pass exposed three expected dependent-package BOM hash changes; the current-envelope, DXL-harness-allocation, and mechanical-BOM-binding packages were regenerated from the current BOM. A later pass exposed the expected CAM-register-to-BOM-binding hash cascade after drill-map whitespace normalization; that binding was regenerated. The final repository-wide regression completed with **123/123 checkers passing**, and the staged release-manifest checker passes after this record is re-hashed.

The interactive guide was inspected in the in-app browser at 1,280 x 720 and rendered through headless Chrome at its effective 500 px narrow-window minimum. Body text is 16 px, technical/helper text is 14 px, all eighteen holds and the preliminary warning are present, and no mojibake was detected. The first constrained render prompted explicit `max-width: 480px` reflow rules and overflow guards in the source generator; the regenerated 500 px render has no visible clipping. The 390 px CSS boundary is source-checked but was not directly rendered because this Windows Chrome instance enforces a wider minimum content viewport.

The energization register remains fail-closed: 0 gates closed, 22 partial, and 8 open. Passing digital, CAM, source-integrity, and presentation checks do not establish manufacturability or close any physical, supplier, test, functional-safety, or authorization gate.
