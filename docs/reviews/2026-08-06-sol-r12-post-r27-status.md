# Sol R12 Status Reconciliation after R27

> **PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**

This is a status update against the existing independent Sol R12 review. It is not a new independent review and is not counted as another Sol round.

## Material change

- Electrical V3 advanced from `V3-P0.5` to `V3-P0.6`.
- `S0` no longer uses four anonymous `TBD-*` terminals. Its two manufacturer NC contact positions are represented as project-unique `R-1/R-2` and `L-1/L-2` designators, with `TOP`-up bottom-view orientation explicit.
- The right NC pair is project channel 1 and the left NC pair is project channel 2. Received-device orientation, markings, continuity and positive-opening behavior remain open.
- RESET and ARM terminal numbers were deliberately not inferred. IDEC's current transition notice says old and redesigned HW assemblies may be shipped under unchanged complete-switch order codes and internal BOM part numbers changed.
- The receiving form now records separate expected and observed channel pairs instead of a single ambiguous two-terminal field.
- All native KiCad sources, schedules, netlist, PDF/SVG exports, ERC report and source manifest were regenerated from the same generator revision.

## Reproduced status

- Electrical checker: PASS
- KiCad 10.0.5 ERC: 0 errors / 0 warnings
- 11 native pages, 55 component blocks, 241 terminals
- 62 named connected plus 25 deliberate unconnected nets
- 216 unique wire labels
- 43 unresolved component/interface rows
- 60 `TBD-*` terminal designations, down from 64
- E2 release-gate status: 0 closed, 14 partial and 7 open; this pass closed no gate

## Sol findings not closed

This pass does not close the missing buildable-machine, functional-safety, stopping-time, contactor-duty, protection, conductor, grounding, enclosure, battery, real-time control, physical-test, or qualified-review blockers. No executed requirement verification exists merely because ECAD parses and ERC is clean. The package remains not ready for fabrication or energization.

Primary implementation record: `docs/hr-v0-electrical-terminal-closure-r27.md`.
