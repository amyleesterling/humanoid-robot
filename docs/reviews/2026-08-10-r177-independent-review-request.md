# R177 independent review request — low-loading isolated event acquisition

> **PRELIMINARY — NOT APPROVED FOR PROCUREMENT, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION.**

Independently review `HR-V0-DYN-EVENT-AIN-P0.1` against Sol R12, R174-R176, TI `SBASA34B` / `SBAU330C`, the current LabJack T7 documentation and Project Button Electrical V3-P1.15-CARRIER-CANDIDATE.

Verify:

1. The decision to retain R176 as historical/not preferred because its approximately 2.25 mA typical input load is not accepted.
2. AMC3330EVM J2.1/J2.2/J2.3, J3.1/J3.2/J3.3 and J1.1/J1.2 mappings.
3. Every T7 AIN even-positive/adjacent-odd-negative pair and DB37 pin.
4. The EVM's ±1 V input boundary, high-impedance data and TI's warning that the board is not certified for high-voltage operation.
5. That no direct 24 V-class input, divider value, protection part, connector, logic supply or field harness has been released.
6. The eight-address stream model and explicit sequential—not simultaneous—sampling limitation.
7. That every field node still requires an accepted normal/reverse/transient envelope, maximum permissible added load and tap-present/tap-absent proof.
8. Native KiCad parse/ERC/net/connector/BOM/export consistency and visual legibility across all five child sheets.
9. That the DAQ, EVMs, host and stored traces receive zero safety-function credit.
10. That `EG-025` remains open and `EG-026` partial, with no procurement, connection, physical evidence or work authorization.

Report exact source revision/date and exact artifact/sheet/terminal/net for every finding. Do not assign approval, PLr/SIL, fabrication readiness or permission to energize.
