# R175 independent review request

Review `HR-V0-DYN-INST-P0.1` as an instrumentation evaluation candidate, not a procurement, connection, test or energization release.

1. Confirm the LabJack T7/CB37 facts and challenge whether the proposed channel count, ranges and shared 100 ksamples/s capacity can support the final scan list after sensor interfaces are selected.
2. Confirm that no 24 V source is authorized for direct connection to T7 DIO and that the ground-referenced LJTick-Divider is correctly rejected as a completed isolated stop-event interface.
3. Review the LEM HLSR 10-P/SP33 range, transfer, primary thermal/fault path and secondary supply/reference requirements. Identify every carrier schematic/layout requirement before it could become a selected instrument.
4. Challenge the BFS-U3-04S2C-CS choice, including optics, working distance, trigger polarity, trigger-to-exposure latency, frame integrity, scale calibration and containment mounting.
5. Confirm force, displacement, independent angle, isolated 24 V events, source voltage and sample-clock witness remain `SELECTION REQUIRED`.
6. Confirm the DAQ/test computer receives zero safety-function credit and cannot be inserted so its failure commands motion or defeats a protective function.
7. Challenge all fifteen channel mappings, eight interface boundaries and fifteen closure holds for missing overload, calibration, uncertainty, grounding, EMC, connector, enclosure or fault-injection requirements.
8. Confirm `EG-025` remains open and `EG-026` remains partial, with no physical evidence or work authorization.

Return `BLOCKER / MAJOR / MINOR` findings with exact file, item, channel, interface and hold identifiers. Do not infer a rating, order code, pinout, range acceptance, safety credit, physical result or permission to procure, connect, test, move or energize.
