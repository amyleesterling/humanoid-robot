# R245 validation record

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

R245 products: `HR-V0-MECH-BOM-BIND-P0.3`, `HR-V0-FW-MECH-SRC-BIND-P0.1`, and `HR-V0-CONFIG-REC-P0.9`.

Generation and dedicated checking reproduce five one-each custom parts, fifteen unchanged STEP/DXF/drawing identities, the current integrated P0.8 architecture on every binding row, eight source-manifest hash matches, two matching fail-closed firmware bindings, and a deliberately absent physical/HIL acceptance hash.

The dedicated checker also runs the supervisor unit-test suite and verifies that a stale source-manifest hash fails selection closure.

## Executed results

- Standard repository checker sweep: **188/188 PASS**.
- Native KiCad 10.0 checker sweep: **18/18 PASS**.
- Release-candidate manifest: **5,155 package files PASS** while the working candidate remains uncommitted.
- Desktop browser QA at 1280 x 720: all three R245 guides load with the exact warning visible, no page-level horizontal overflow and zero captured console warnings/errors. The mechanical and firmware tables stay in local overflow containers. Minimum observed leaf text is 14 px for technical code labels; body/functional text is 16 px or larger.
- Narrow-layout browser execution: **NOT COMPLETED**. The in-app browser's advertised 390 x 844 viewport override returned successfully but retained a measured 1280 x 720 viewport; the alternate Chrome surface was unavailable. Static CSS review confirms responsive `clamp()` typography, body copy at 16 px or larger, and local `.table { overflow:auto }` containment, but this is not recorded as an executed mobile visual pass.

These checks establish source/configuration integrity and desktop legibility only. They do not establish machinist-ready drawings, physical acceptance, functional safety or permission to energize.
