# R246 validation record

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

R246 products: `HR-V0-P121-STATIC-VOLTAGE-BUDGET-P0.1` and `HR-V0-CONFIG-REC-P0.10`.

## Deterministic result

The dedicated checker reproduces eight P1.21 terminal-addressed control loops, four primary load-family operating envelopes, six raw source-connector headroom screens, eighteen series elements, eight uncalculated transient cases, eighteen missing inputs, ten unsent manufacturer questions, ten open holds and seven unexecuted package acceptances.

It independently compares fourteen critical `(reference, terminal, net)` tuples against the actual P1.21 connector schedule. It rejects the 12 V Mean Well actuator source from the 24 V control budget, accepts no installed margin, and confirms that P1.15 remains current while P1.21 remains unaccepted.

## Executed results

- Dedicated R246 checker: **PASS**.
- Standard repository checker sweep: **189/189 PASS**.
- Native KiCad 10.0 checker sweep: **18/18 PASS**.
- Release-candidate manifest: **5,210 package files generated before this validation record; final manifest regenerated after adding this record**.
- Desktop browser QA at 1280 x 720: both R246 guides load with the exact warning visible, body text at 16 px, minimum technical leaf text at 14 px, no page-level horizontal overflow, and table content contained in local scrolling regions. The voltage-budget guide exposes ten tables and 97 body rows; the configuration guide exposes five tables and 156 body rows.
- Visual inspection: the voltage-budget landing surface has legible sky-blue/dark-blue/golden-yellow presentation, an immediately visible warning and explicit `PARTIAL / NOT ACCEPTED` status.
- Narrow/mobile browser execution: **NOT COMPLETED**. Responsive CSS uses a 16 px body floor, 14 px table text and local table overflow, but static inspection is not recorded as an executed mobile visual pass.

## Initial integration failure and correction

The first standard sweep failed 9/189 because R246 initially rewrote the central hash-bound gate and release-candidate files. That invalidated older frozen evidence packages. The integration was corrected: the central files were restored byte-for-byte, and R246 is carried as an additive gate-evidence supplement plus P0.10 reconciliation until a deliberate coordinated central-baseline reissue. The corrected sweep passes 189/189.

These checks establish arithmetic, source/configuration integrity, native-ECAD continuity and desktop legibility only. They do not establish a complete installed circuit, source dynamics, protection coordination, received hardware behavior, functional safety, build readiness or permission to energize.
