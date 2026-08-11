# R233 validation record

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

- Date: 2026-08-11
- Artifact: `HR-V0-PNOZ-KWD-APP-P0.2`
- Native ECAD candidate reviewed: `V3-P1.20-WATCHDOG-INTERLOCK-CANDIDATE`
- Current electrical product remains: `Project Button Electrical V3-P1.15-CARRIER-CANDIDATE`

## Source and calculation results

- Controlled Pilz Operating Manual `21396-EN-23` SHA-256: `4B6E4768CEFAEDAF54F006347D32A8A04964B59A16F3616D8AC43698D3626BB4`.
- Current Pilz product/manual record rechecked 2026-08-11; manufacturer portal identifies manual date/revision 2026-06-22 / 21396-EN-23.
- Current Phoenix Contact item 2967060 product record/data-maintenance date 2026-04-01 rechecked 2026-08-11.
- All 31 selected P1.20 terminal/path rows match the connector schedule exactly.
- Twelve source/derived electrical screens pass the focused checker.
- Derived paper margins recalculate to 4.8 times voltage, 5.0 times steady current, 75 times input-inrush current and 10 times DC13-to-input-inrush current.
- The 30 ms mixed timing sum is correctly classified `NOT AN ACCEPTANCE BOUND` because it combines a typical relay-release value with a maximum Pilz dropout value and omits downstream physical response.
- Ten fault cases are controlled; four remain `HAZARDOUS / OPEN` and every case retains zero safety credit.
- Nine closure holds and ten qualified-review questions remain open/selection required.
- Sol R12 B-005 is `PARTIALLY_ADDRESSED_OPEN`; qualified closure is `NO` and work authority is `NO`.

## Repository and software validation

- Focused R233 checker: **PASS**.
- Standard repository checker sweep with the controlled CadQuery-capable runtime: **176 / 176 PASS**.
- Native KiCad/pcbnew checker sweep with KiCad 10.0.5 bundled Python: **18 / 18 PASS**.
- Supervisor firmware source tests: **67 / 67 PASS**.
- Watchdog reference-model and compiled-C differential tests: **11 / 11 PASS**.
- Final staged deterministic release manifest: **PASS with 4,617 controlled package files**.

The first standard sweep used an interpreter without repository CadQuery access and was non-authoritative. The authoritative elevated read-only sweep used the controlled local CadQuery runtime and passed 176/176. Two stale legacy state assertions were synchronized to the R233 fail-closed release-state string before the passing sweep.

## Interactive-guide validation boundary

The focused checker confirms the complete warning, 16 px minimum body/functional text, 14 px table text, responsive metric grid, locally scrolling wide tables, all twelve electrical screens, all ten fault cases and the zero-safety-credit/B-005 boundary.

An attempted in-app-browser review of the local `file:` artifact was blocked by the browser URL security policy. No alternate-browser workaround was attempted. Therefore R233 records **static structural/legibility QA only; visual desktop/mobile browser QA is not executed**. This does not affect the engineering calculations, but it remains an explicit presentation-review hold before deployment.

## Boundary

R233 closes only the paper contact/load compatibility question. It does not establish relay life, guaranteed response, common-cause control, protected routing, received identity, installed resistance, restart behavior, fault response, stopping time/distance, achieved PL/SIL/Category, qualified validation or work authority. P1.20 remains unaccepted and P1.15 remains current.
