# Independent review request - HR-V0 watchdog PCB fabrication candidate P0.1

**PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**

Review configuration: Electrical V3-P1.13 / PCB-P0.5 / `HR-V0-WD-FAB-P0.1` / `HR-V0-WD-TRAVELER-P0.1`.

This is a review of a CAM candidate and physical-evidence route, not a request
to upload, quote, order, fabricate, assemble or energize anything.

## Review questions

1. Reproduce the package from the generator and verify every manifest hash.
2. Re-run KiCad DRC and both new checkers; report tool/version compatibility problems.
3. Compare every board reference, pad, net, connector pin and test point with Electrical V3-P1.13.
4. Review all 42 component footprints against current primary manufacturer land patterns, including package variant, orientation, paste, mask, hole, courtyard and assembly access.
5. Inspect all nine Gerber layers, PTH/NPTH drill files, outline, job file, placement and IPC-D-356 in an independent viewer. Identify clipping, repair, ambiguity, stray geometry or unreadable legends.
6. Check the 6 mil/6 mil, 0.30 mm design drill, 0.15 mm design annular ring, 160 x 100 mm outline and proposed two-layer process against the selected supplier's current written capability.
7. Decide whether the documented KiCad 9.x direct-processing statement creates any additional KiCad 10.0.5 submission risk. Do not assume native-file compatibility.
8. Audit exact order codes, lifecycle, availability, substitutions, polarity and traceability for the 42-reference BOM.
9. Challenge trace/protection/source-foldback/connector/conductor coordination; all missing fault-current and time-current inputs must remain selection required.
10. Review test-point access, SWD fixture isolation/no-back-power, dummy-load fixtures, current-limited source, measurement categories and stop conditions.
11. Review every CAM, receiving/assembly, bring-up and inspection row for missing operations, premature numerical assumptions or unsafe sequencing.
12. Confirm the safety relay, contactors, external control source, supervisor, actuator source and all motion hardware stay disconnected through board-level bring-up.
13. Confirm E2-HOLD-008 remains open until physical and qualified evidence exists.
14. Return BLOCKER/MAJOR/MINOR findings with exact file, layer, reference, pad/net or traveler row and primary-source evidence.

Passing DRC, CAM generation or repository checkers proves only deterministic
modeled consistency. It does not approve fabrication, assembly, functional
safety or energization.
