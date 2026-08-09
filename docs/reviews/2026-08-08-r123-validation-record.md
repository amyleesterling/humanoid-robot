# R123 validation record

**Package:** `HR-V0-PANEL-RD-P0.1` / synchronized `HR-V0-CP-P0.6`

**Status:** **PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**

## Defect and controlled correction

- The former P0.6 branch contained one 500 mm perforated rail against DR1-DR4 planning segments totaling 642.6 mm; it was materially insufficient.
- Phoenix Contact's current record for the former perforated candidate states a greater-than-100-mm minimum, conflicting with the 65 mm DR3 and 100 mm DR4 planning segments.
- R123 replaces that branch with two exact held Phoenix Contact `1207648` 500 mm unperforated rails. Every planning segment exceeds the current greater-than-20-mm unperforated minimum.
- One exact held `3240189` 2000 mm duct covers the 1655.4 mm WD1-WD3 planning total before kerf.
- Six exact held `3022218` brackets are allocated only to DR1/DR2/DR3. DR4 remains `SELECTION REQUIRED` because the 90.5 mm case envelope and 100 mm rail do not establish room for two 9.5 mm brackets.

## Controlled state

- System BOM: 85 groups; 17 evaluation candidates; 36 exact-candidate holds; three grouped-component holds; 24 selection-required groups; four exclusions; one integrated item.
- P0.6 panel BOM remains 34 rows with corrected `PAN-006`, `PAN-008` and `PAN-009` identities/quantities.
- R123 package: seven planning cut rows, twelve holds, three primary-source rows, eighteen blank receiving rows and sixteen blank installation rows.
- Every result/evidence field is blank. Every physical-work row is `NOT_EXECUTED` and `NOT_AUTHORIZED`.
- `BOM-059`, final lengths/tolerances, kerf, tool/process, hole patterns, fasteners/torque, DR4 end retention, bonding/coating treatment, physical proof and qualified review remain unresolved.

## Automated validation

- All 75 non-manifest `tools/check_*.py` checkers passed using the controlled CadQuery/Python environment, with the three KiCad/PCB checkers run under KiCad 10.0.5 Python.
- `tools/check_hr_v0_panel_rail_duct_p01.py` passed all BOM, panel, stock-arithmetic, minimum-length, DR4-boundary, source, form, gate, metadata and guide assertions.
- Existing compute-installation and BOM closure checkers passed after R123 synchronization.
- The readiness invocation `tools/check_energization_gates.py --through-stage E2 --require-ready` returns exit 2: all 21 applicable gates remain partial and zero are closed.
- Responsive Chromium QA passed at 1440 x 1000 and 390 x 844: no body overflow, minimum visible text 12 CSS px, deliberate stock/table scrollers contained overflow, and the Fabrication filter returned exactly its two cards.
- Desktop and mobile renders were visually inspected. Stock bars, warning hierarchy, DR4 hold, filter state and 1-5 closure sequence remained readable.

## Configuration closure

The all-file manifest is regenerated only after all R123 files are staged and is checked again from the clean committed tree. Its exact file count and commit hash are configuration evidence, not fabrication or energization approval.

R123 does not change Sol R12's overall verdict: HR-V0 remains not ready to build or energize, and HR-30W remains physically plausible but unproved.

**PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**
