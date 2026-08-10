# R184 independent review request

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION.**

Review exact artifact **HR-V0-Q4X-BOX-P0.1** at the supplied commit. Treat native KiCad and repository registers as authoritative; the web guide is presentation only. This is a temporary bench-instrumentation candidate with zero safety credit, not a robot safety circuit.

## Required checks

1. Open the root and both child sheets in KiCad 10; rerun ERC and compare the native netlist, connector schedule, wire-number table and BOM.
2. Verify every terminal on `PS1`, `CBLPS1`, `PTCB1`, `XQ1.1-XQ1.6`, `CBLQ4X1`, `Q4X1` and unresolved `TEST1`.
3. Check the exact current manufacturer evidence for Phoenix Contact `1464484`, `3209578`, `3209510`, `3030514`, `3030417`, `3022218`, `1207650`, `0828734`, `0828736`, `3203066`, `3201110` and `1212034`.
4. Check Hammond `PJ1084T` and `14F0907`, LAPP `53111000` and `53119000`, Alpha Wire `881802`, Banner `815158` and `97540`, and Keithley `2220-30-1` against current primary documentation.
5. Recalculate the 28.125 mA Q4X screen, 33.125 mA combined screen, 3.019 nominal ratio, both cable/gland fit screens and source/breaker switching-capacity comparison.
6. Confirm that Phoenix's typical `1.2 x IN` current limiting is not represented as a guaranteed 0.12 A fault ceiling.
7. Determine whether the catalog backup-fuse condition is correctly interpreted without inventing an upstream fuse value or replacing installed fault testing.
8. Review the exact source cable/ferrule/tool combination, including the Alpha `881802` conductor construction, Phoenix ferrule cross-section/AWG statements, CRIMPFOX die guidance, stripping, retention and inspection obligations.
9. Review the no-PE-entry, isolated-rail proposal for a Boston bench installation. Identify every code, listing, enclosure, abnormal-condition or completed-assembly issue that remains.
10. Confirm the Banner drain is parked only at `XQ1.6`, with no bridge, PE, rail, chassis or 0 V connection, and that Q4X pin 5 is not silently joined to pin 3.
11. Confirm PTCB remote terminals 13/14 and the Q4X remote input are physically unwired candidates, not logical-only no-connect assertions.
12. Review enclosure space, rail length, wire-bend space, covers, end brackets, markers and cable-gland placement. Exact drilling coordinates remain unreleased.
13. Review the unresolved `TEST1` analog lead fixture for touch protection, isolation, strain relief and alternate-ground paths.
14. Compare Markdown, all CSV/JSON records, native ECAD, SVGs, interactive guide, inspection form, gate supplement, generator and checker for exact consistency.
15. Confirm zero procurement, fabrication, connection, powered-test, motion, energization or safety authority is implied.

Classify every issue BLOCKER / MAJOR / MINOR and cite exact file, sheet, reference, terminal, net or row. Do not approve procurement, fabrication, connection, powered testing, motion, energization or functional safety.
