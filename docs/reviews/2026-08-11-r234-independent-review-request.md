# R234 P1.21 independent review request

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Please review `V3-P1.21-SRA1-SUPPLY-WATCHDOG-CANDIDATE` and `HR-V0-P121-SRA1-SUPPLY-WD-P0.1` against current P1.15, unaccepted P1.20, Sol R12 B-005, the Pilz PNOZ s4 750104 manual 21396-EN-23 and Phoenix Contact item 2967060 data.

1. Re-run KiCad 10 parse, export and ERC on all thirteen pages.
2. Confirm the exact seven-terminal P1.20-to-P1.21 delta and unchanged 333 terminal assignments.
3. Confirm SR1 supply and both E-stop input loops are independent of KWD1/KWD2.
4. Confirm KWD1/KWD2 series-gate only SRA1 A1 and cannot source a modeled SRA1 input/start return.
5. Challenge all fourteen fault cases, especially dual/common-cause, internal cross-pole, route bridge, brownout and E-stop-with-KWD-welded cases.
6. Verify heartbeat restoration cannot close SRA1 outputs without a later falling-edge monitored ARM.
7. Assess whether switching/power-cycling SRA1 A1 is permissible and what written manufacturer or qualified application evidence is required.
8. Verify the nine electrical screens without treating catalog envelopes as endurance or application approval.
9. Confirm DF-01 has zero safety credit and PG-01 assumes its failure.
10. State the exact evidence required before P1.21 could be promoted.

Do not mark P1.21 current, buildable, functionally safe or approved for procurement, fabrication, assembly, connection, powered testing, motion or energization.
