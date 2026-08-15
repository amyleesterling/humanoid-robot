# HR-V0 P1.21 consolidated native-KiCad review candidate P0.1

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Identifier: `HR-V0-P121-CONSOLIDATED-REVIEW-P0.1`  
Review round: R238  
Date: 2026-08-11

## Result

No new electrical revision is needed merely to combine the prior layout and watchdog work. `V3-P1.21-SRA1-SUPPLY-WATCHDOG-CANDIDATE` is already generated through this source lineage:

`P1.18 panel topology -> P1.19 visual correction -> P1.20 intermediate watchdog experiment -> P1.21 SRA1-supply watchdog correction`

P1.21 therefore already contains the readable P1.19 page geometry and the explicit `XD24`, `XD0`, `XN1`, `XN2`, and `XN3` panel nodes. It is the preferred **review candidate**, not the current or accepted configuration. `V3-P1.15-CARRIER-CANDIDATE` remains current.

## Machine-checked boundary

- 13 native KiCad sheets: root plus twelve children.
- 84 component identities, 106 named nets, 340 modeled terminal rows, 301 wire-number rows and 63 unresolved-selection rows.
- Six keyed terminal/pin-role changes between P1.19 and P1.21. They move the ordinary two-contact series supply gate from `SR1:A1` to downstream `SRA1:A1`.
- Five dense sheets retain the P1.19 A2 layout; the ordinary child sheets retain A3.
- KiCad ERC remains 0 errors and 0 warnings. This checks connectivity and annotation only.
- The interactive review surface exposes all thirteen current P1.21 SVG exports and the exact six-terminal delta.

## Sol analysis disposition

The analysis pasted on 2026-08-11 repeats the same R12 independent review package already controlled and dispositioned by R231. It is not counted as a new independent review round. Its core verdict remains correct: HR-V0 is achievable but not build-ready; energization remains prohibited; HR-30W walking is plausible but unproved; and none of the 18 blockers has qualified closure.

R238 improves only configuration clarity. It does not close missing CAD, selections, manufacturer application evidence, physical tests, stopping evidence, guard evidence, PLr/SIL allocation or qualified review.

## Open holds

Eleven holds remain open, including fresh visual review of logic-changed pages 2 and 3, independent every-sheet review, Pilz/Phoenix application disposition, protected routing, received-component verification, no-load restart/brownout traces, fault injection, stopping/guard evidence, PLr/SIL allocation, qualified review and formal promotion/work authorization.

## Review surfaces

- [Interactive P1.21 consolidated review](../release/hr-v0/p121-consolidated-review-p0.1/index.html)
- [Lineage register](../release/hr-v0/p121-consolidated-review-p0.1/lineage-register.csv)
- [Thirteen-sheet review register](../release/hr-v0/p121-consolidated-review-p0.1/sheet-review-register.csv)
- [Exact P1.19-to-P1.21 terminal delta](../release/hr-v0/p121-consolidated-review-p0.1/terminal-delta.csv)
- [Open holds](../release/hr-v0/p121-consolidated-review-p0.1/open-holds.csv)

This package is suitable for independent and qualified review. It is not a fabrication, connection, powered-test, motion or energization release.
