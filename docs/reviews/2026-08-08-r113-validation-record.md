# R113 validation record

Status: **PRELIMINARY - CONFIGURATION CORRECTION ONLY; NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, MOTION, OR ENERGIZATION**

## Scope

R113 issues `HR-V0-GRIP-SEL-P0.1`. It reconciles `SYS-002`, `GRIP-002` and HR-SYS-001 revision 0.1 section 2 without changing any requirement. The current 40-70 mm each-principal-dimension object envelope is retained and no gripper is selected.

## Reproduced facts

- Pololu item 3551 publishes a 32 mm internal opening; 40 - 32 = 8 mm nominal shortfall before pads, tolerances and uncertainty.
- ROBOTIS publishes a 20-75 mm gripper stroke, but the installed padded usable opening remains unverified and receives compatibility-screen credit only.
- The controlled ServoCity product, assembly, specification and STEP records do not publish a usable-opening value; it receives no numerical compliance credit.
- The R111 25-30 mm object is a proposal, not a released baseline.
- All three candidate states are `NOT SELECTED` or conditional-study-only.

## Automated and presentation checks

The dedicated checker passed. Installed Google Chrome rendered the guide at `1440 x 1000` and `390 x 844` with zero page-width overflow, `16 px` body/control text and `14 px` metadata. The two requirement-branch controls changed `aria-pressed` state and explanatory content at both viewports. Desktop and mobile screenshots were visually inspected: the warning remained prominent, cards reflowed from three columns to one, and no clipping or unreadable text was found. Complete repository-suite and deterministic-manifest results are recorded below after final regeneration.

All **66 unique checker programs passed**, including the controlled CadQuery and KiCad-runtime checks. The deterministic release manifest contains **1,535 package files**. The final clean-commit manifest reproduction is recorded by the commit-bound validation step.

The intentional command `tools/check_energization_gates.py --through-stage E2 --require-ready` returned the expected exit code `2`: all 21 gates applicable through E2 remain `PARTIAL`, zero are closed, and all 30 total gates remain unresolved. The package correctly refuses an energization-readiness claim.

## Gate result

R113 closes only the preference/configuration ambiguity. It closes zero requirements, risks, physical tests, qualified reviews, fabrication gates, motion gates or energization gates. HR-V0 remains not build-ready and energization remains prohibited.
