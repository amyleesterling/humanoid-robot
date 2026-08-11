# R224 independent electrical review request

**PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Review `HR-V0-ECAD-WEB-REVIEW-P0.1` against the actual P1.18 native KiCad source. Do not treat ERC 0/0 or a clean-looking SVG as electrical or functional-safety approval.

Please verify every one of the thirteen sheets for:

1. sheet identity, hierarchy, title, cross-reference and correspondence to the named native source;
2. every reference, terminal/pin label, net, contact state and two-ended P2P conductor mapping;
3. P1.15 versus P1.18 logic parity, confirming that only `XD24`, `XD0`, `XN1`, `XN2` and `XN3` topology nodes were added;
4. dual-channel E-stop, monitored RESET, distinct ARM, EDM, watchdog-gated SR1 supply and redundant actuator-power interruption behavior;
5. the requirement that RESET or E-stop release cannot command motion;
6. mains/source boundaries, PE/0 V rules, isolation assumptions, protection, current paths and fault consequences;
7. watchdog zero-safety-credit boundaries and single/common-cause faults;
8. all `TBD-*`, `SELECTION REQUIRED`, connector, fuse, conductor, termination and application holds;
9. any clipped, overlapping, ambiguous, misleading, excessively sparse or unreadable schematic presentation; and
10. parity among native source, ERC, netlist, BOM, connector schedule, net schedule, wire-number table, P2P schedule and web exports.

Return BLOCKER / MAJOR / MINOR findings with exact sheet, reference, terminal/net, source evidence and proposed correction. State separately whether P1.18 may advance to formal configuration consideration. Do not grant fabrication, connection, powered-test, motion or energization authority.
