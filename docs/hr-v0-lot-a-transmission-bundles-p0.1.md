# HR-V0 Lot A recipient transmission bundles P0.1

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Document ID: **HR-V0-LOT-A-TX-BUNDLE-P0.1**

Date: 2026-08-12
Parent: `HR-V0-LOT-A-INQUIRY-P0.3`

## Result

R258 creates five deterministic, recipient-isolated ZIP archives from the exact R257 inquiry package. Each archive has a route-specific message, fail-closed control JSON, blank response sheets and a SHA-256 payload manifest. The three metrology archives also contain the 14 exact R257 scope attachments.

The [interactive bundle guide](../release/hr-v0/lot-a-transmission-bundles-p0.1/index.html) exposes each archive size, complete SHA-256 digest, open decision gates and blank transmission-event records.

## Isolation correction

R257 retained separate ROBOTIS response sheets but referenced one shared message. R258 corrects that ambiguity:

- `R257-RT-01` receives only sales/order questions `R257-RQ-01..08`;
- `R257-RT-02` receives only technical questions `R257-RQ-09..12`;
- each metrology candidate receives only its own 33 questions, five method rows and 18 characteristic rows; and
- the checker rejects any occurrence of another route identifier in a bundle's textual payload.

No ROBOTIS archive contains metrology STEP files or bid sheets. No metrology archive contains another provider's route identifier or response surface.

## Deterministic archive contract

The generator sorts all member paths, fixes ZIP timestamps to 1980-01-01 00:00:00, fixes regular-file permissions, uses UTF-8 names and creates an internal payload manifest. The checker rebuilds all five archives byte-for-byte, verifies archive SHA-256 values, CRCs, member counts, timestamps, route identity and fail-closed authority states.

## External-transmission boundary

The archives are internal review candidates. They are **NOT AUTHORIZED** and **NOT SENT**. Eleven open gates require:

1. archive reproduction and hash verification;
2. same-day recipient-route confirmation;
3. selected sender and monitored reply identity;
4. signed route/content/no-leakage review;
5. malware/content scanning;
6. exact one-time transmission authorization;
7. immutable transmission and receipt records;
8. response ingestion without inferred acceptance;
9. current-version verification immediately before send; and
10. accepted redistribution authority for the three vendor STEP files.

That final gate is essential: possessing vendor CAD in the repository does not by itself prove permission to redistribute it externally.

## Configuration effect

`HR-V0-CONFIG-REC-P0.22` supersedes P0.21 as the configuration record only. It contains 41 current records, 34 supersession records, 136 open holds and 169 blank/unexecuted acceptance rows.

R258 closes zero Sol R12 blockers and releases no contact, procurement, fabrication, assembly, connection, powered-test, motion, functional-safety or energization authority.
