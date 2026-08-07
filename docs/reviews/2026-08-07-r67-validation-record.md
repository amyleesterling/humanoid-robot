# R67 validation record

> **PRELIMINARY—NOT APPROVED FOR FABRICATION OR ENERGIZATION.** Passing software checks do not establish physical suitability, safety integrity or permission to build.

Date: 2026-08-07

Candidate branch: `codex/review-ledger-handoff`

Products: `HR-V0-ARM-ARCH-P0.6`, `HR-V0-MECH-P0.5`, `HR-V0-HS-P0.2`

## Generated evidence

- 30 P0.6 arm artifacts generated from the controlled CadQuery environment;
- 40,001 sampled two-axis collision rows;
- 70 continuously certified non-intentional body pairs in 130 adaptive interval cells;
- minimum guaranteed nominal lower-bound clearance `0.765783 mm` against a `0.75 mm` required floor;
- exact critical-pair clearance at J2=120 degrees `0.962813 mm`;
- continuous numerical nominal contact J2=`121.643289 deg`; and
- candidate-only software/positive-stop/contact allocation `115/118/121.643289 deg`.

Two consecutive P0.6 generations produced byte-identical sets of all 30 artifacts before final static SVG layout correction. The final layout correction changes only fixed SVG text/positions in the same deterministic generator; independent reviewers are requested to repeat the complete byte comparison.

## Automated results

- arm architecture checker: PASS;
- integrated mechanical release checker: PASS;
- generated CAD/source-manifest checker: PASS, 162 generated artifacts and 11 vendor references;
- traceability: PASS, 81 requirements / 40 risks / 103 procedures / 56 release-and-walking references;
- BOM, frame-joint, fabrication-route, sourcing, manufacturing, electrical V3, control-panel, protection, service-disconnect, safety-allocation, E2 and firmware checkers: PASS within their stated preliminary boundaries;
- watchdog PCB: PASS, native DRC 0, no fabrication outputs;
- DXL-STAR PCB: PASS, native ERC/DRC 0/0, no fabrication outputs;
- release manifest: PASS, 664 package files after this record is included; and
- energization gates: 30 total, 0 closed / 22 partial / 8 open, NOT READY.

## Visual QA

The P0.6 arm SVG and P0.5 general-arrangement SVG were rendered in a browser. The first pass exposed a partially hidden column label, a stale R66 heading, and a general-arrangement note extending under the arm-hold panel. The generators were corrected, the artifacts regenerated, and both automated SVG checks passed. Body text remains 18 px; warning text is 20 px; titles are 34/36 px.

## Unclosed evidence

The validation does not close received material/FAI/fit, T-slot capacity, fastener installation, actual hard-stop design, measured stopping/backlash/compliance/tolerance/uncertainty, cable/guard/as-built clearance, mass/COM/inertia, continuous-duty/thermal behavior, protective electrical selections, functional-safety allocation or qualified signatures.

No fabrication, assembly, motion, connection or energization authorization exists.
