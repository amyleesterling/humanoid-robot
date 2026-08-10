# HR-V0 K1/K2 Contactor Application Evidence P0.1

Current superseding closure packet: `HR-V0-K1K2-APP-P0.2` in `docs/hr-v0-contactor-application-p0.2.md`. P0.1 remains the historical R41 evidence record.

> **PRELIMINARY—NOT APPROVED FOR FABRICATION OR ENERGIZATION**

Date: 2026-08-07

System baseline: `HR-30-SYS-R0.2`

Electrical candidate: `V3-P1.3`

Gate: `EG-013` remains **partial**

## Controlled candidate and topology

`K1` and `K2` remain proposed Schneider Electric `LC1D25BD` contactors. They are two physically distinct final elements with 24 VDC coils. Electrical `V3-P1.3` represents all three main poles of each contactor in series:

`ACT_12V_FUSED -> SD1 -> K1 1L1-2T1 -> 3L2-4T2 -> 5L3-6T3 -> K2 1L1-2T1 -> 3L2-4T2 -> 5L3-6T3 -> ACT_12V_BUS`

The external jumpers are therefore `K1 2T1->3L2`, `K1 4T2->5L3`, `K1 6T3->K2 1L1`, `K2 2T1->3L2`, and `K2 4T2->5L3`. This topology is a connected candidate, not permission to wire or energize it.

The integrated normally-closed auxiliary of each device is represented at `21-22` in the SRA1 external-device-monitoring return. The integrated normally-open auxiliary is represented at `13-14` as a diagnostic only. Manufacturer evidence supports the contact relationship, but received-device identity, terminal mapping, continuity, forced-fault behavior, and the complete safety function still require physical validation and qualified functional-safety review.

## Current primary manufacturer evidence

| Source | Revision/date recorded | Evidence used | What it does not establish |
|---|---|---|---|
| Schneider `LC1D25BD` product data sheet `SQD-LC1D25BD.PDF` | dated 2017-09-13; rechecked 2026-08-07 | 24 VDC BD coil; 5.4 W sealed/inrush coil screen at 20 °C; 16–24 ms opening time; integrated 1NO+1NC auxiliary; NC mirror contact to IEC 60947-4-1; 1NO+1NC mechanically linked to IEC 60947-5-1; built-in bidirectional peak-limiting diode | application-specific DC operational current, source/fuse coordination, low-current arc extinction, regenerated energy, loaded stopping time, or received behavior |
| Schneider TeSys catalog 2026, document `MKTED210011EN`, pages A5/120–A5/123 | catalog 2026; downloaded/rechecked 2026-08-07; SHA-256 `ACE31998C5091FAAC5BD15C6BE1CC272E52501161B96D3184BDBBB64F9EA8293` | at the published 24 V row, the `LC1D25` column shows 32 A with one, two, or three poles in series; selection tables distinguish DC-1 (`L/R <= 1 ms`) from DC-2 through DC-5 (`L/R <= 15 ms`) and require voltage, utilization category/time constant, current, and durability | a released 12 V regenerative electronic-load application or a fuse/conductor rating |
| Schneider FAQ `FA126437` | modified 2026-05-12; rechecked 2026-08-07 | LC1D09 through LC1D150 include mirror and mechanically linked contacts; Schneider recommends the base-device NC auxiliary for monitoring main contacts | achieved PL/SIL, diagnostic coverage, correct received wiring, or application suitability |

Primary links:

- <https://www.se.com/us/en/product/LC1D25BD/iec-contactor-tesys-deca-nonreversing-25a-15hp-at-480vac-up-to-100ka-sccr-3-phase-3-no-24vdc-coil-open-style/>
- <https://iportal.se.com/Contents/docs/SQD-LC1D25BD.PDF>
- <https://download.schneider-electric.com/files?filename=Catalog&p_Doc_Ref=MKTED210011EN>
- <https://www.se.com/us/en/faqs/FA126437/>

The `25 A` in the product name is not used as an HR-V0 DC rating. The current catalog’s 32 A / 24 V entry is recorded only as manufacturer application evidence under its stated conditions.

## HR-V0 screening boundary

The proposed actuator source is 12 V, 21 A. The controlled actuator screen is `4.4 + 4.4 + 2.3 = 11.1 A`, using published momentary stall endpoints; it is neither a continuous operating requirement nor a measured break current. HR-V0 contains electronic motor drives, bus capacitance, inductance, and possible regeneration, so it is not assumed to be a DC-1 resistive load.

The catalog explicitly warns that operation below its tabulated currents can produce durability below the IEC 60947-4-1 definition because of critical current, and directs the application to Schneider technical support. Because 11.1 A is below the published 32 A row, the catalog table alone cannot release `LC1D25BD` for HR-V0. The 12 V bus is also not silently treated as an independently published 12 V rating.

The 5.4 W coil value gives only `5.4 W / 24 V = 0.225 A` nominal arithmetic per coil. The two-coil screen is 0.45 A. It does not establish pickup current, transient current, protection, wire size, rail behavior, or stopping time. The published 16–24 ms device opening time is a component datum, not a measured robot stopping time.

## Evidence required before selection can close

1. Freeze and measure the worst-case current through K1/K2 at every commanded and fault interruption, including regeneration and simultaneous joint motion.
2. Capture bus voltage, source response, downstream capacitance, equivalent transient or `L/R`, current direction, and decay during opening.
3. Determine the applicable DC utilization category or obtain written Schneider application guidance for the actual electronic/regenerative load.
4. Obtain Schneider written guidance for `LC1D25BD` at the measured 12 V/current envelope with all three poles in series, explicitly addressing the catalog’s lower-current/critical-current warning and the required operations/life.
5. Freeze prospective fault current, source current limiting, F0/F1/F2/F3 protection, interrupting capacity, conductor/terminal ratings, ambient, enclosure, bundling, and jurisdictional basis.
6. Freeze the required mechanical/electrical endurance and maximum operating cycles per hour.
7. Receive and inspect both contactors; verify order code, coil polarity/suppression, main and auxiliary terminals, mirror behavior, and contact continuity against controlled records.
8. On a guarded, independently de-energizable fixture, execute repeated worst-case loaded interruptions, welded-contact fault injection, coil dropout, bus rail decay, residual motion, and total stopping-time tests.
9. Obtain qualified electrical and functional-safety review of the complete function and evidence. No PL/SIL credit is assigned by this document.

## Manufacturer application query record

The support request shall include, rather than omit or guess:

- candidate `LC1D25BD`, 24 VDC BD coil, two devices in series;
- exact three-pole series wiring and terminal sequence shown above;
- measured normal, peak, break, reverse/regenerative, and fault currents;
- measured bus voltage/transient, capacitance, equivalent `L/R`, and source current-limit behavior;
- exact upstream/downstream protective devices and prospective fault current;
- required interruption count, cycles/hour, life, ambient, enclosure, wiring, and installation orientation;
- whether the device must interrupt after loss of both coil commands and the maximum permitted opening/stopping time; and
- a request for an identifiable written Schneider disposition tied to the submitted envelope and current catalog revision.

Until those inputs and the written response exist, the request record shall say `SELECTION REQUIRED` rather than implying manufacturer approval.

## Disposition

Manufacturer evidence now supports the proposed terminal/contact relationship, built-in coil suppression, timing datum, and the existence of a three-poles-in-series DC selection table. It also exposes a material lower-current/critical-current issue for the present HR-V0 screen. `K1` and `K2` therefore remain:

`PROPOSED - CATALOG DC ENVELOPE FOUND; CRITICAL-CURRENT AND APPLICATION CONFIRMATION REQUIRED; TEST REQUIRED`

`EG-013` remains partial. No fuse, conductor, contactor application, safety integrity, fabrication, or energization release is issued.
