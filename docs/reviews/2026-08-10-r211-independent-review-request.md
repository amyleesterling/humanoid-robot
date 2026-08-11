# R211 independent review request

**PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Independently review `HR-V0-RUNTIME-OBS-CARRIER-P0.5` and its relationship to the observation interface, Pi carrier, compute harness and integrated Electrical V3 candidate. Do not treat ERC/DRC success or this project-owned audit as design approval.

1. Confirm the exact `SN74LVC1G07DBVR` orderable identity, DBV pin mapping, land dimensions, mask/paste treatment, open-drain behavior, Ioff/partial-power claims, decoupling, routing and unused-pin treatment against current TI documentation.
2. Confirm exact Panasonic `ERJ6ENF1002V`, `ERJ6ENF3902V` and retained bias-resistor identities. Reproduce HIGH, LOW, short-current and aggregate 3V3 calculations across resistance tolerance, TCR, aging, supply tolerance, device leakage, cable leakage/capacitance and temperature.
3. Obtain authoritative Raspberry Pi 5/RP1 input thresholds, leakage, capacitance, clamp-current, injection-current and unpowered-pin limits, plus allowable 3V3 header loading, or obtain a written application disposition from Raspberry Pi. Do not infer these values from another Broadcom device or generic 3.3 V CMOS rules.
4. Define and witness STANDBY, start-up, shutdown, rail-ramp, brownout, recovery, open-circuit, stuck-low, short-to-ground, short-to-3V3, cross-channel and back-power tests on representative hardware. Confirm that no diagnostic-channel fault creates motion authority or defeats the independent safety architecture.
5. Perform independent schematic and PCB review, DFM, assembly-process review, first-article inspection, continuity/isolation testing, signal-integrity/timing measurement, thermal measurement, EMC review and fault injection before any release decision.
6. Confirm the exact integration revision and prohibit P0.3 and P0.4 from supplier upload, quotation, order or fabrication.

Every diagnostic channel has zero functional-safety credit. This request does not authorize procurement, fabrication, assembly, connection, powered testing, motion or energization.
