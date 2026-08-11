# R225 validation record

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Date: 2026-08-11

Artifact: `HR-V0-WD-PERMIT-TOPOLOGY-P0.1`

## Source checks

- P1.18 native sheet 03, KiCad 10.0.5 netlist, wire-number table, ERC report and SRS P0.2 are SHA-256 bound;
- `WD_SUPPLY_INTERMEDIATE` contains exactly `KWD1:14` and `KWD2:11`;
- `SR1_A1_WD_GATED` contains exactly `KWD2:14` and `SR1:A1`;
- `SAFETY_24V` contains `KWD1:11`;
- neither KWD reference occurs on `SR1_S11`, `SR1_S12`, `SR1_S21` or `SR1_S22`;
- five relevant wire-number rows match the netlist endpoints;
- nine Boolean fault cases include single-weld and dual-weld/bypass states;
- both single-weld/heartbeat-absent screens remove the modeled permit; the dual-weld/bypass screen preserves it and remains hazardous;
- eight holds remain open, reviewer closure is not claimed and every physical/work authority flag is false.

## Pending final synchronization

- focused package checker: PASS;
- gate/release/configuration synchronization and dependent hash regeneration: PASS;
- desktop browser QA at 1280 x 720: PASS; 1280 CSS-pixel document width, no body overflow, 16 px minimum visible text and both 900 px tables contained without clipping;
- mobile browser QA at requested 390 x 844 (375 CSS-pixel document width): PASS; no body overflow, 16 px minimum visible text, single-column flow and both 900 px tables contained in explicit horizontal-scroll regions;
- pre-manifest standard checker sweep: 166 / 167 PASS; all nonmanifest checks passed and only the expected unstaged-manifest check failed;
- native KiCad Python checker sweep: 19 / 19 PASS;
- supervisor firmware tests: 67 / 67 PASS;
- watchdog firmware tests: 11 / 11 PASS;
- final staged standard-check sweep: 167 / 167 PASS;
- final release manifest: PASS with 4,321 controlled package files;
- independent electrical and functional-safety review: OPEN.

This proof covers source topology only. It does not prove contact behavior, routing, common-cause performance, response time, achieved risk reduction or permission for physical work.
