# R108 validation record - gripper acquisition correction

Status: **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, MOTION, OR ENERGIZATION**

R108 verifies the current official ROBOTIS scope for FR12-G101GM and HN12-I101 and reconciles it against the enumerated HR-V0 mechanism. FR12-G101GM is rejected as a sole mechanism source; RM-X52 remains proposed and unreleased. No source drawing for FR12-G101GM, FR12-E170GM or FR12-E171GM was acquired from the linked official frame drawing index.

The fail-closed checker verifies three acquisition dispositions, five access-dated primary-source records, the twenty-row RM-X52 mechanism register, the release warning and legible web-guide font floors.

## Visual verification

The responsive web guide was rendered in headless Microsoft Edge at 1440 x 1000 and 390 x 844 CSS-pixel viewports. Both views had document scroll width equal to client width, so no page-level horizontal overflow was present. The computed minimum functional font was 12 px. Screenshot inspection found the warning, decision, three acquisition dispositions, fail-closed path and open-hold panel readable and unclipped at both widths. The temporary screenshots and QA script were removed after inspection.

## Repository verification

The complete repository suite passed:

- 60 checker programs: 54 workspace-Python, three CadQuery and three KiCad 10.0.5 runtime checks;
- 47 executable firmware unit tests inside the firmware checker; no target flash or HIL was performed;
- 359 hash-controlled generated CAD artifacts and 16 vendor references;
- 81 requirements, 40 risks, 109 procedures and 56 release/walking-document procedure references;
- BOM closure at 78 groups, 17 evaluation candidates, 25 exact holds and 28 selection-required groups; and
- all 30 energization gates unresolved: zero closed, 22 partial and eight open.

The staged `HR-V0-RC-P0.1` manifest passed with 1,441 package files. The intentional E2 `--require-ready` check returned exit code 2 with all 21 applicable E0-E2 gates partial; this is the required fail-closed result. A clean post-commit manifest check remains required.

No item was ordered, no supplier was contacted, no file or physical article was received, and no gripper hold or authorization gate closed.
