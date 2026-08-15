# R224 validation record

**PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Date: 2026-08-11

Artifact: `HR-V0-ECAD-WEB-REVIEW-P0.1`

## Digital checks

- thirteen native KiCad sheets are mapped one-to-one to thirteen native KiCad SVG exports;
- every native sheet and SVG is SHA-256 bound;
- all SVGs retain the common A3 `419.9890 x 297.0022 mm` geometry and `0 0 419.9890 297.0022` view box;
- the controlled ERC report remains 0 errors and 0 warnings;
- the KiCad CLI log records one PDF and thirteen SVG plots, but the web viewer links only to SVG;
- four source artifacts, eight open holds and four authority rows are controlled;
- the dedicated generator/checker pass;
- P1.15 remains current, P1.18 remains unaccepted, and every physical/work authority remains false.

## Browser QA

- desktop viewer shell inspected at 1440 x 900 and 1440 x 1200 requested viewports;
- body-level horizontal overflow absent and minimum computed interface text is 14 CSS px;
- all thirteen sheet controls and native SVG loads are represented in the DOM;
- navigation, stable sheet hashes, direct SVG link and focus mode function;
- the first five exports received an internal visual sampling screen;
- focus mode was added after the initial browser screen showed avoidable navigation-column compression;
- mobile viewer shell inspected at a requested 390 x 844 viewport (375 CSS-pixel content width): no body-level horizontal overflow, 14 CSS-pixel minimum interface text, all thirteen controls present and the 1587 x 1123 native SVG loaded;
- full page-by-page electrical visual review remains **NOT EXECUTED** and is not inferred from browser loading or ERC.

## Repository validation

- pre-manifest standard checker sweep: 162 / 166 PASS; three dependent hash registers correctly detected the R224 gate/release changes and were regenerated, leaving only the expected unstaged-manifest failure;
- regenerated governance, functional-safety review-route and build-traveler checks: PASS;
- native KiCad Python checker sweep: 19 / 19 PASS;
- supervisor firmware tests: 67 / 67 PASS;
- watchdog firmware tests: 11 / 11 PASS;
- final staged standard-check sweep: 166 / 166 PASS;
- final release manifest: PASS with 4,295 controlled package files;
- independent electrical/parity review: OPEN;
- qualified electrical and functional-safety review: OPEN.

These checks prove source/export identity and web-review usability only. They do not prove the correctness, suitability or safety of the circuit and do not authorize physical work.
