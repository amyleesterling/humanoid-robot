# Project Button electrical V2.1

> **PRELIMINARY - NOT APPROVED FOR ENERGIZATION**

This is the connected V2.1 correction pass. V1 remains preserved in the sibling `project-button` directory. The authoritative specification remains `C:\Users\amyle\Documents\New project\humanoid-robot`.

Generated artifacts:

- `project-button-v2.kicad_pro` and `project-button-v2.kicad_sch`
- 14 connected child sheets
- `bom.csv`
- `connector-schedule.csv`
- `netlist-schedule.csv`
- `wire-number-table.csv`
- `unresolved-selections.csv`
- `engineering-inputs-required.csv`
- `primary-source-register.csv`
- `requirements-trace.csv`

Regenerate with:

`node scripts/generate-electrical-v2.mjs`

The custom V2.1 block symbols intentionally represent reviewed functional interfaces. Manufacturer-verified terminal numbers are used only where recorded. Pins marked `TBD-*` are logical placeholders and are not buildable connector pin assignments. Pin electrical types remain passive until qualified manufacturer symbols and selected parts replace the placeholders, so ERC is a connectivity check and cannot establish electrical or functional safety. The clean ERC result does not prove physical pinouts, ratings, safety performance, or permission to energize; unresolved device pins remain passive functional interfaces.

**PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION.**
