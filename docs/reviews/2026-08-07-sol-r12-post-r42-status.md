# Sol R12 Findings Rechecked against R42

> **PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**

Date: 2026-08-07

System baseline: `HR-30-SYS-R0.2`

Correction baseline: Electrical `V3-P1.4`

This is a project-owned status reconciliation, not a new independent review. Sol R12 remains the independent assessment of the pre-correction `ee276af...` baseline: 18 BLOCKER, 30 MAJOR and 8 MINOR findings; 62 of 62 then-audited requirements draft; 106 unresolved Electrical V2.1 selections; and no executed, approved verification evidence. The newly supplied summary is the same R12 review and is not double-counted.

## R42 correction

R42 narrows the RESET/ARM physical-terminal evidence defect without closing it:

- rechecked current IDEC US pages for `HW1B-M1F10-B` and `HW1B-M1F10-G`, which retain the complete black RESET and green ARM momentary 1NO screw-terminal identities;
- recorded IDEC's 2026-07-14 notice that the HW transition began 2026-06-15, prior or redesigned assemblies may ship under unchanged complete order codes, and internal BOM component codes changed;
- recorded that the live `HW1B-M1F10-G` product-page BOM returned `No BOM products found` on 2026-08-07;
- refused to transfer a legacy, push-in or visually inferred terminal number onto the current screw-terminal assemblies;
- retained `S1:TBD-R1/TBD-R2` and `S2:TBD-A1/TBD-A2` in the connected source;
- added a received-lot form covering photographs, declared orientation, design classification, molded markings, released/pressed resistance, meter checks, retaining hardware, harness mapping and independent review;
- added an exact IDEC/distributor query for lot-specific construction, contact block, terminal drawing, mounting hardware and termination requirements; and
- issued synchronized Electrical `V3-P1.4` native source, schedules, BOM, netlist, ERC, PDF and SVG artifacts; and
- fixed LF normalization and deterministic V3 generation for `electrical/kicad/**/*.kicad_pro` after clean clones exposed DXL-star and V3 source-manifest failures caused only by CRLF conversion.

## What remains open

- Neither S1 nor S2 has been purchased, received, inspected, continuity-tested or panel-tested.
- The internal contact-block identities, underside orientation and manufacturer terminal marks remain unresolved for the delivered lot.
- Panel spacing, guarding, retention, legend legibility and human-factors acceptance remain unexecuted.
- No physical trace proves RESET alone cannot energize contactors or that every safety dropout requires RESET release followed by distinct ARM press/release.
- No qualified electrical or functional-safety reviewer has accepted the device, terminal map, monitored-start behavior or fault evidence.
- Through E2 the gate result remains 0 closed, 15 partial and 6 open. `EG-011` remains partial.
- Sol's remaining mechanical, CAD, mass/inertia, continuous-torque, safe-power-loss, protection, grounding, battery, bus, real-time, restraint, fabrication, physical-test and walking blockers remain open.

## Disposition

Sol's central verdict is unchanged: HR-V0 is not ready for fabrication or energization, and HR-30W walking is not demonstrated. R42 replaces an ambiguous switch-terminal placeholder with a controlled received-lot closure route. It releases no terminal identity and grants no permission to procure, fabricate, wire or energize.
