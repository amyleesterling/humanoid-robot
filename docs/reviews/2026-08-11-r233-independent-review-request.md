# R233 P1.20 PNOZ/KWD independent review request

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Please review `HR-V0-PNOZ-KWD-APP-P0.2` against the unaccepted P1.20 native KiCad source, Pilz Operating Manual 21396-EN-23, the current Phoenix Contact 2967060 product record and Sol R12 B-005. Review accuracy and completeness; do not infer approval to build or energize.

## Requested checks

1. Confirm all 31 recorded terminal/net rows against every relevant native P1.20 sheet.
2. Confirm the exact proposed 750104 selector position and whether its dual-channel short-detection plus monitored falling-edge behavior is compatible with the proposed two-stage SR1/SRA1 architecture.
3. Confirm that 24 V/50 mA and 0.2 A for 100 ms are the applicable Pilz input/start/feedback load data for order 750104.
4. Confirm that Phoenix item 2967060 has a 5 V/10 mA minimum switching load, 15 A for 300 ms inrush envelope and no force-guided/safety-relay claim.
5. Recalculate the 4.8, 5.0, 75 and 10 paper margins and challenge whether any comparison is inapplicable.
6. Review all ten fault cases, including dual weld/bypass, shared controller/driver command, common-route damage, start/feedback cross-short and coil-driver/suppression faults.
7. Confirm that heartbeat restoration without a fresh monitored ARM event cannot re-energize SRA1, K1 or K2 or command motion.
8. Define required protected routing, cable-resistance allocation, conductor/terminal selection, environmental limits, inspection and test evidence.
9. Define the common-cause/dependent-failure analysis and functional-safety evidence necessary to close B-005.
10. State whether B-005 is correctly classified `PARTIALLY_ADDRESSED_OPEN`, and list every prerequisite before P1.20 could be promoted.

Do not assign safety credit to KWD1/KWD2, accept typical timing as a worst-case bound, mark P1.20 current, or authorize procurement, fabrication, assembly, connection, powered test, motion or energization.
