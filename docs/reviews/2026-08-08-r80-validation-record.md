# R80 validation record - 24 V source-interface correction

**PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**

Date: 2026-08-08

Round: R80

## Controlled outcome

- Electrical V3-P1.10 replaces the ambiguous system `JC1` block with standard KiCad references `J24` and `F24`.
- `J24` freezes exact held catalog/topology candidates: Mean Well `DC PLUG-P1J-R7B` and Kycon `KPJX-PM-4S`.
- `J24:1` and `J24:4` map to `SAFETY_24V_RAW`; `J24:2` and `J24:3` map to `SAFETY_0V`.
- `F24:IN` maps to `SAFETY_24V_RAW`; `F24:OUT` maps to `SAFETY_24V` while hardware and value remain `SELECTION REQUIRED`.
- The separate DXL-star board's `JC1` reference remains unchanged and unambiguous within that native project.
- `HR-V0-24V-IF-P0.1`, the P0.4 control-panel allocation and the E2 hardware slice are synchronized.

## Validation performed

- KiCad 10.0.5 parsed the root plus twelve child sheets.
- Native ERC: `0 errors / 0 warnings`.
- Native exports: thirteen A3 SVG pages plus thirteen-page PDF.
- Electrical checker: PASS for 77 component blocks, 297 modeled/netlist terminals, 64 named connected nets, 36 deliberate unconnected nets, 261 unique wire labels, 75 nonzero-quantity BOM records, 65 unresolved component/interface rows and 14 deliberate `TBD-*` terminals.
- 24 V interface checker: PASS for six BOM rows, eight pin records, eight compatibility/physical holds and five current primary-source records.
- E2 hardware checker: PASS for 23 configuration rows, six XT1 rows, three source rows and twelve blocking holds.
- Control-panel checker: PASS for 26 BOM rows, 20 backplate allocations, six XT1 positions and 66 bounded V3 wire endpoints.
- Browser QA: the interactive guide parsed with all expected headings, tables and warning text; at the available 1280 x 720 viewport, page scroll width equaled client width, the body font was 16 px, the minimum functional text was 14 px and no text fell below 14 px. The narrow-screen CSS retains horizontal scrolling inside the flow/table containers rather than shrinking text.
- KiCad sheet-01 visual QA: the first export exposed border clipping and then label crowding during intermediate layouts. The final two-column/four-row A3 export removes both defects; all source, connector, protection and DNP blocks, net labels, warnings, notes and title fields are visible without overlap.
- Repository validation: all 32 checkers passed using the controlled general, CadQuery and KiCad Python runtimes as applicable.
- Release manifest: 878 package files; clean-clone reproduction passed with a clean worktree and all five R80-critical checks. Remote-branch verification follows push.

## Limits

The current official Mean Well evidence found during R80 does not explicitly prove that `DC PLUG-P1J-R7B` is approved with `GST40A24-P1J`, nor does it close the conversion cable current/application envelope. No equal current sharing across paired R7B contacts is assumed. No `F24` hardware/value, PCB/harness, wire, panel hole, mounting, retention, touch protection, strain relief, received polarity, temperature-rise or abnormal-condition evidence is released.

ERC and repository checks prove modeled consistency only. They do not establish physical suitability, electrical safety, functional-safety performance, fabrication readiness or permission to energize. Gate status remains 0 closed / 22 partial / 8 open.
