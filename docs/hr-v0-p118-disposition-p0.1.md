# HR-V0 P1.18 configuration-disposition dossier P0.1

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

- Identifier: `HR-V0-P118-DISPOSITION-P0.1`
- Review round: R229
- Date: 2026-08-11

## Outcome

R229 supplies a configuration-bound disposition dossier for the unaccepted `V3-P1.18-PANEL-TOPOLOGY-CANDIDATE`. It proves a bounded modeled delta from current P1.15; it does not accept or promote P1.18.

The project-owned comparison found no uncontrolled connectivity delta:

- all 77 P1.15 BOM rows are preserved without modification;
- exactly five catalog-candidate terminal devices are added: `XD24`, `XD0`, `XN1`, `XN2` and `XN3`;
- all 308 P1.15 terminal/net records are preserved without modification;
- exactly 32 terminal rows are added on the five new devices;
- all 106 named nets are preserved;
- 101 nets retain identical membership;
- five nets gain only the controlled node terminals, with no removed original connection;
- all 269 P1.15 semantic wire-table rows remain present, with 32 node-terminal rows added; and
- all 63 unresolved-selection records remain identical when keyed by sheet/reference.

This evidence is necessary for configuration disposition, but it is not sufficient for qualified electrical or functional-safety acceptance.

## Native-sheet boundary

Thirteen P1.15/P1.18 native sheets are SHA-256 bound. After normalizing only the revision identity, date, warning text and KiCad project-instance name, child sheets 04 through 12 are identical. Sheets 01 through 03 contain the five controlled topology-node additions. The root sheet changes revision/index narrative but carries no components or wires.

The comparison does not hide native-source differences: both original hashes are retained. Normalization is used only to classify administrative changes and is independently reproducible in the generator/checker chain.

## Logic invariants

The dossier traces eight logic boundaries to the exact connector/net evidence and prior source-bound reviews:

1. both direct E-stop channels;
2. RESET as eligibility only, with no motion command;
3. distinct ARM and EDM behavior;
4. two ordinary series watchdog contacts with zero safety credit and the dual/common-cause hazard retained;
5. K1/K2 coil, EDM and load-pole topology;
6. the E2 grounding/return boundary;
7. exclusion of the actuator domain from E2; and
8. 55 explicit two-ended conductors with no modeled hidden splice.

The project result is only `PRESERVED IN MODEL`. Physical fault behavior, stopping performance, PLr/SIL allocation and qualified acceptance remain open.

## Decision boundary

P1.15 remains the current electrical configuration. P1.18 remains unaccepted until all of the following receive controlled dispositions:

- independent page-by-page electrical review;
- qualified functional-safety review;
- exact node loading, protection, covers, markers, partitions, rail retention and access;
- exact conductors, dynamic door loom, routes, lengths, service loops and separation;
- termination process, DCR, voltage drop, ampacity, fill, thermal and fault coordination;
- received and installed identity/continuity/polarity/isolation/torque/pull/thermal/fault evidence; and
- formal immutable promotion by the named configuration authority.

`EG-002`, `EG-004` and `EG-020` remain partial. The decision matrix intentionally leaves every independent-review field blank.

## Controlled artifacts

- Engineering dossier: `electrical/reviews/hr-v0-p118-disposition-p0.1/`
- Interactive review guide: `release/hr-v0/p118-disposition-p0.1/index.html`
- Gate supplement: `requirements/hr-v0-gate-evidence-supplement-r229.csv`
- Generator: `tools/generate_hr_v0_p118_disposition_p01.py`
- Checker: `tools/check_hr_v0_p118_disposition_p01.py`

This dossier cannot authorize procurement, fabrication, assembly, wiring, connection, powered testing, motion or energization.
