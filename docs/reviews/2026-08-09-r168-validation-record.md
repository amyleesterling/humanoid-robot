# R168 validation record

R168 issues `HR-V0-XT1-P0.1` and reconciles system `BOM-039` to the exact catalog/position evidence already present in the panel and E2 packages.

- Six terminal positions: five gray Phoenix Contact 3209510 and one blue 3209523.
- One direct 3030417 end cover.
- Zero bridges or jumpers.
- Two installed 3022218 restraints remain procured under shared `BOM-085`; no duplicate quantity is introduced.
- Unmarked 0828734 stock and every printed-label decision remain under `BOM-062`; no duplicate or false label closure is introduced.
- Twelve open holds and all procurement/assembly/wiring/energization/safety-credit flags remain false.

Validation must include `python tools/check_hr_v0_xt1_terminal_group_p01.py` and the full repository regression. Passing proves digital configuration consistency only; it does not prove received parts, conductor/termination selection, ratings coordination, installed wiring, point-to-point inspection or qualified review.

`EG-003` and `EG-015` remain partial. No gate closes.

## Executed validation

- Full repository regression: **125/125 checkers passed** — 97 standard, 13 native KiCad and 14 CadQuery geometry checks, plus the release-manifest checker.
- Controlled release manifest: **2,801 package files**.
- Energization-gate posture: **0 closed / 22 partial / 8 open**; all 30 gates remain unresolved.
- Interactive-guide desktop check at **1280 × 720**: six cards present, 16 px body and button text, 14 px technical tags, no horizontal overflow and the preliminary warning visible.
- Interactive-guide mobile check at **390 × 844**: six cards present, the same minimum text sizes, no horizontal overflow and the preliminary warning visible.
- Filter behavior: `Safety power` shows exactly XT1-02 and XT1-01; `Status signals` shows exactly XT1-03 through XT1-06; `All six` restores all positions.
- Browser console: **0 errors**.

These are configuration, parsing, geometry and presentation results only. They do not supply missing physical evidence or authorize procurement, assembly, wiring, fabrication, motion or energization.
