# R171 validation record

R171 issues `HR-V0-HOST-DEPLOY-P0.1` as a disabled, fail-closed source/deployment candidate.

- Six proposed overlay files are controlled and every installation row remains `NOT_AUTHORIZED`.
- The committed configuration produces 23 preflight holds and exits 78.
- Six unit tests prove committed-HOLD refusal, no child-process spawn, malformed/configuration-file failure, absent-target failure, no hardware-backend imports, disabled preset and no restart.
- Eighteen closure holds remain open.
- All 21 target execution rows remain `NOT_AUTHORIZED / NOT_EXECUTED`.
- `EG-003`, `EG-017` and `EG-021` remain partial.

## Browser validation

The interactive guide was inspected at 1280 x 720 and 390 x 844.

- body and button text: 16 px;
- technical labels: 14 px;
- no horizontal overflow;
- filter results: Everything 4, Startup path 1, Open evidence 2, Safety boundary 1;
- no console warnings or errors; and
- the mobile header, warning, summary cards and controls remain comfortably legible.

## Repository validation

- General repository checks: **100/100 passed**.
- Native KiCad-dependent checks under KiCad 10.0: **13/13 passed**.
- CadQuery geometry checks: **14/14 passed**.
- Pre-manifest total: **127/127 passed**.
- The staged release-manifest check brings the controlled total to **128 checks**.

These checks prove file integrity, parser compatibility, digital invariants and reference-model behavior only. No target image was built, written, booted, installed or HIL-tested. No GPIO or serial backend was selected. No connection, motion, functional-safety or energization authority exists.
