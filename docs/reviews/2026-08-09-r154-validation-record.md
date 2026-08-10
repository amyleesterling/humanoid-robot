# R154 validation record - DXL branch-current envelope

> **PRELIMINARY - NOT APPROVED FOR SUPPLIER UPLOAD, QUOTATION, PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, MOTION, OR ENERGIZATION**

Date: 2026-08-09
Identifier: `HR-V0-DXL-CURRENT-ENV-P0.1`
Round: R154

## Controlled result

- The existing XM540 raw current-limit candidate of 800 is recorded as a 2.152 A nominal internal screen using the published 2.69 mA/unit scale. The 0.848 A arithmetic distance to the JST EH 3 A published condition is not treated as tolerance, transient margin, thermal proof, connector approval or an external branch-current limit.
- The gripper raw current-limit candidate of 300 is recorded as a 0.807 A nominal internal screen. No physical branch-current result is inferred from that register value.
- The actuator configuration now requires an exact accepted `HR-V0-DXL-CURRENT-ENV-P0.1` evidence identifier and SHA-256 digest before release selections can close.
- During every motion telemetry sample, the transport re-reads Current Limit and Goal Current. Any read failure or exact-value drift causes best-effort torque-off, clears the active trajectory and propagates a fault.
- ATOF fuse-only connector overload control is rejected because its time-current behavior does not create an instantaneous 3 A connector-current ceiling.
- The present internal-limit, continuous-readback and branch-fuse path remains a guarded qualification candidate only. Hardware current limiting and changed connector/actuator architecture remain explicit alternatives.
- Eleven staged measurement records and fourteen acceptance groups remain blank. Fourteen residual holds preserve external current limiting, fuse and conductor selection, waveform capture, regeneration/no-backfeed, voltage drop, thermal rise, clearing behavior, received-HIL evidence, qualified review and all work authority.

## Automated validation

- 37 direct supervisor unit tests passed.
- The firmware source validator reported 48 executable unit tests and passed source, configuration, manifest and separation checks.
- 101 standard repository checkers passed using the controlled HR-V0 CAD Python environment.
- 7 native KiCad checkers passed using KiCad 10.0 Python.
- The R154 checker verifies package membership and hashes, source traceability, derived arithmetic, fail-closed evidence binding, runtime current-register invariants, fuse-only rejection, blank physical forms, fourteen open holds and all false work-authority flags.
- The release-manifest checker is executed after the final staged manifest is generated and is recorded in the commit handoff.

## Web visual QA

The interactive guide was inspected at 1280 x 720 and 390 x 844. Both views retained 14 px minimum functional text, four status cards, fourteen visible holds and no page-level horizontal overflow. Both technical tables intentionally gain local horizontal scrolling at 390 px. The released-external-limit card says `NONE`, preserving the distinction between an absent release and a released 0 A value.

## Disposition

The zero-check result validates repository structure, arithmetic, configuration binding and simulated fault handling only. It does not prove actual branch current, current-limit tolerance, connector suitability, conductor or crimp capability, fuse coordination, regeneration behavior, no-backfeed behavior, voltage drop, thermal performance, enclosure conditions, physical separation, stopping performance, functional safety or received-hardware behavior.

R154 is a project-owned correction and validation pass, not an independent review or approval. Sol's resupplied engineering summary remains R12 and is not double-counted. The package remains **PRELIMINARY - NOT APPROVED FOR FABRICATION, ASSEMBLY, CONNECTION, MOTION, OR ENERGIZATION**.
