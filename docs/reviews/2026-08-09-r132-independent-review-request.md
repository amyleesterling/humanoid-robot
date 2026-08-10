# R132 independent review request

Status: **PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**

Review `HR-V0-WD-PCBA-RFI-P0.1` against current PCB-P0.7, not immutable PCB-P0.5 or superseded PCB-P0.6.

Please independently:

1. Reproduce the 46-reference board membership and 38 SMD / four THT / four NPTH process split from native KiCad source.
2. Confirm that R89 corrected its 21 affected references and R132 changes only TP1-TP16 from rounded-rectangle to Harwin's rectangular 3.45 x 1.85 mm land without moving or resizing them.
3. Challenge every local mask/paste setting, the proposed SMD-then-THT sequence, Pico module treatment, ISO1 contamination boundary and mixed-alloy/process assumption.
4. Assess whether all four provider public-capability claims are accurate as of 2026-08-09 without treating marketing text as Project Button acceptance.
5. Determine whether the twenty requirements and twenty-four questions are sufficient for a reference-level DFM and first-article decision.
6. Audit the ten supplier-file holds, fourteen closure holds and twenty-four first-article rows for missing evidence or accidental authorization.
7. Identify the applicable bare-board, assembly, workmanship, cleanliness, insulation, traceability and test standards that a qualified reviewer must select for the Boston prototype context.
8. Report BLOCKER / MAJOR / MINOR findings with exact reference, pad/process, register row, source and proposed correction.

Run:

```powershell
& 'C:\Program Files\KiCad\10.0\bin\python.exe' tools/generate_hr_v0_watchdog_pcba_inquiry.py
& 'C:\Users\amyle\Documents\New project\.venvs\hr-v0-cad\Scripts\python.exe' tools/check_hr_v0_watchdog_pcba_inquiry.py
```

Do not approve fabrication, assembly or energization. A clean checker or DRC is not supplier acceptance, physical evidence, functional-safety validation or work authorization.
