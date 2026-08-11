# R237 validation record

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Configuration: `HR-V0-LOT-A-SRC-P0.1`

Date: 2026-08-11

R237 validation is repository/source validation only. The focused checker proves internal arithmetic, mirror equality, fail-closed states, source-record completeness, manifest integrity and presence of the exact `-T`/`-R` contradiction. It cannot prove seller inventory, shipment identity, authenticity, received fit, cost, tax, delivery, assembly suitability or physical performance.

## Executed repository validation

- Focused `HR-V0-LOT-A-SRC-P0.1` checker: **PASS** — six units, $1,182.22 visible subtotal, thirteen facts, four open anomalies, eight unsent questions, ten open decision gates and twelve unexecuted receiving rows.
- Standard repository checker sweep: **180/180 PASS** using the controlled Python/CadQuery validation environment.
- Native KiCad `pcbnew` checker sweep: **18/18 PASS**. R237 changes no ECAD source; this confirms the existing native-board evidence remains reproducible.
- Release manifest: **4,802 package files** before the final validation-record refresh; the manifest is regenerated and clean-tree checked in the release commit.
- Interactive guide QA at 1280 × 720: three item cards, four anomaly rows, eight supplier-question rows and two horizontally scrollable table containers rendered; body width did not overflow; minimum visible text was 14 CSS px for a short item badge and 16 CSS px or greater for functional copy; filtering `torque` returned exactly one row and reset restored eight. The header and filtered table were visually inspected. Responsive rules were checked statically; an actual narrow viewport was not executed.

No supplier question was sent, no cart or quote was created, no purchase was authorized, and no article was ordered, received, assembled, connected or powered.
