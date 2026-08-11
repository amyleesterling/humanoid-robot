# HR-V0 K1/K2 contactor application P0.3

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Document ID: **HR-V0-K1K2-APP-P0.3**  
Date: 2026-08-11  
System baseline: `HR-30-SYS-R0.2`  
Current electrical source: `Project Button Electrical V3-P1.15-CARRIER-CANDIDATE`  
Unaccepted electrical candidate: `V3-P1.18-PANEL-TOPOLOGY-CANDIDATE`  
Gate: `EG-013` remains **partial**

## Decision

R226 closes one configuration-management defect in P0.2: its controlled application envelope referred to older P1.13 source, while later current and proposed ECAD existed. Direct machine comparison now proves that all sixteen `04_contactor_edm.kicad_sch` terminal/net rows and all sixteen `05_actuator_interruption.kicad_sch` terminal/net rows are byte-for-byte equal as CSV records between current P1.15 and unaccepted P1.18.

This establishes configuration continuity for the K1/K2 application question. It does **not** approve `LC1D25BD` for this DC load, promote P1.18, select a fuse, authorize a supplier request, or replace physical and qualified review.

## Exact modeled topology

The actuator-power path is represented as:

`ACT_12V_RAW -> F0 -> ACT_12V_FUSED -> SD1 -> K1 1L1-2T1 -> 3L2-4T2 -> 5L3-6T3 -> K2 1L1-2T1 -> 3L2-4T2 -> 5L3-6T3 -> ACT_12V_BUS`

`KP1` and `KP2` on sheet 05 are contact cross-references for the same physical `K1` and `K2` devices represented on sheet 04; they are not extra BOM devices. K1 and K2 each retain a 24 VDC coil, integral 21-22 NC mirror-contact candidate in the series EDM return, and a separate 13-14 NO diagnostic contact with zero safety credit.

The checker verifies the internal contact-jumper nets exactly in both netlists:

- `K1_P1_IN`: `SD1:TBD-OUT`, `KP1:1L1`;
- `K1_J12`: `KP1:2T1`, `KP1:3L2`;
- `K1_J23`: `KP1:4T2`, `KP1:5L3`;
- `K1_OUT`: `KP1:6T3`, `KP2:1L1`;
- `K2_J12`: `KP2:2T1`, `KP2:3L2`;
- `K2_J23`: `KP2:4T2`, `KP2:5L3`;
- `EDM_K1_OUT`: `K1:22`, `K2:21`;
- `K1_A1`: `FSR1:2`, `K1:A1`; and
- `K2_A1`: `FSR2:2`, `K2:A1`.

`F0` and both `SD1` physical terminals remain unresolved. The modeled series chain is therefore ECAD topology evidence, not a build release.

## Current primary-source disposition

Schneider's official TeSys catalog record remains `MKTED210011EN`, version 17.1, dated 2026-07-10. Schneider's official DC-load FAQ directs designers to the catalog's DC-1 through DC-5 utilization tables and coordination guidance. The official `LC1D25BD` product sheet is dated 2017-09-13 and identifies the 24 VDC coil, 16 to 24 ms published opening interval, integral mechanically linked 1NO+1NC contacts, 21-22 NC mirror contact, and 5 mA at 17 V minimum signaling values. All three official records were rechecked on 2026-08-11.

The product sheet also states that it is not a substitute for determining suitability for a particular application. Its AC-1/AC-3 headline ratings, 300 VDC insulation/operational-voltage field, 40 A thermal current, opening interval, or B10d entries do not prove 12 V electronic/capacitive/regenerative breaking performance. The catalog's three-pole DC tables and critical-current warning are screening evidence only.

Primary records:

- Schneider Electric, *TeSys Catalog 2026*, `MKTED210011EN`, version 17.1, 2026-07-10: https://www.se.com/us/en/download/document/MKTED210011EN/
- Schneider Electric, *LC1D25BD Product Data Sheet*, dated 2017-09-13: https://iportal.se.com/Contents/docs/SQD-LC1D25BD.PDF
- Schneider Electric, DC-load guidance `FAQ000273244`, modified 2026-05-02: https://www.se.com/uk/en/faqs/FAQ000273244/

## What remains unresolved

The eleven open holds cover:

1. formal P1.18 disposition;
2. received K1/K2 identity and terminal/contact verification;
3. measured normal, peak, opening and reverse-current/voltage/capacitance/time-constant envelope;
4. source current limiting, regeneration response and prospective fault current;
5. selected protection and coordination;
6. exact conductors, jumpers, terminations, lengths and routes;
7. ambient, enclosure, mounting, cycles/hour, life and maintenance requirements;
8. an identifiable written Schneider application disposition;
9. guarded loaded interruption, weld-equivalent and endurance evidence;
10. a qualified numerical stopping requirement and executed validation; and
11. signed configuration-specific electrical and functional-safety review.

The R117 Schneider request remains `UNSENT`. Eighteen prerequisite application inputs remain open or unmeasured. No vendor contact occurred in R226.

## Machine-readable and web evidence

- `electrical/reviews/hr-v0-contactor-application-p0.3/`
- `release/hr-v0/contactor-application-p0.3/index.html`
- `requirements/hr-v0-gate-evidence-supplement-r226.csv`
- `tools/generate_hr_v0_contactor_application_p03.py`
- `tools/check_hr_v0_contactor_application_p03.py`

P0.3 corrects the source binding. `EG-013` remains partial. No procurement, fabrication, assembly, connection, powered testing, motion, functional-safety approval, or energization authority exists.
