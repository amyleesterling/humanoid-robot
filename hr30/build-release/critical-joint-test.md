# Button critical-joint decision package

Date: 2026-09-25. Source: `174691255409336a7e25ba1505217859c98c3f80`.

**Review brief and planning budget only. No purchasing, fabrication, wiring, energization or motion approval.**

## Decision and place in the whole robot

Determine whether the proposed XM430-W350-R / LD-25 ankle-pitch module can support its reviewed motion duty with acceptable temperature, tracking, backlash, mechanical behavior and fault response. An acceptable result advances to a complete-leg test; it does not qualify the hips, balance, walking, falls, or child interaction. A failed result triggers a bounded actuator/reduction/load-demand trade before bulk procurement. It must not trigger another unbounded arm-only project.

The first candidate is the right ankle because it has the highest peak-to-current-endpoint fraction among the 12 leg axes in the **pinned ideal-fixture** demand table. Left ankle is nearly identical. Hip roll has a greater absolute torque demand, and LIGHT4's hip structure/material remains a separate serious risk. This selection criterion is not an overall safety ranking.

## Exact candidate boundary

| Item | Candidate definition |
| --- | --- |
| Robot axis / bus | `R_ANKLE_PITCH` / `RS-RLEG` |
| Motor | ROBOTIS XM430-W350-R, SKU `902-0118-000`, RS-485; no TTL substitution |
| Drive | `LD-25`, 2.5:1, 16:40 teeth |
| Motor pulley | `GPA16GT5090-A-P8` |
| Output pulley | `GPA40GT5090-A-P12` |
| Belt | `GBN250EV5GT-090` |
| Horn / adapter | `HN12-N101` / `MA-HN12-P8`; not the knee's HN13/10 mm interface |
| Existing design inputs | [Allocation](../whole-body-p0.1/leg-drivetrain-p0.1/axis-drivetrain-allocation.csv), [LD-25 STEP](../whole-body-p0.1/leg-drivetrain-p0.1/LD-25/LD-25_candidate.step), [adapter guide](../whole-body-p0.1/leg-drivetrain-adapters-p0.1/index.html) |
| Torque source | [Active LIGHT4 demand table](../whole-body-p0.1/active-light4-p0.1/whole-body-axis-demand.csv) |

These names bind the proposed interface, not an approved manufacturing bill. Exact shaft/carrier drawings, bearings, fits, retention, materials, fastener products/preloads, tooth geometry/capacity, belt tension, guards and received-part compatibility still require review. Retain the real module's load path and interfaces in the article; a bare motor result cannot qualify the belt joint.

For initial motor characterization, use the manufacturer's existing communication interface with an independently reviewed bench power/stop arrangement. There is no need to fabricate all custom whole-robot PCBs just to characterize one motor. The U2D2/hub are test equipment only; this does not replace or qualify the robot's power and safety architecture.

## Numerical question, not a test command

The source table reports 6.433361747 Nm peak, 5.644891650 Nm RMS and 7.571049 Nm linear current endpoint for this joint. The allocation assumes 2.5:1 and 0.85 transmission efficiency. ROBOTIS's product page lists 0.82 Nm as an estimated continuous motor value using a 20%-of-stall heuristic. Thus:

```
heuristic joint torque = 0.82 * 2.5 * 0.85 = 1.7425 Nm
model RMS / heuristic = 5.644891650 / 1.7425 = 3.239536...
```

Neither the heuristic nor the ratio is an acceptance criterion. RMS output torque is not a measured motor thermal load. Losses, speed, cooling, reversible power flow, internal control and waveform duration matter. The fixture supplies artificial base constraint forces; these values cannot be promoted to free-walking loads. Do not command peak torque continuously or extend the short simulated sequence indefinitely.

The baseline lock binds the full inverse-dynamics trace and joint trajectory by hash, but this sprint did **not** extract, inspect or authorize their complete time-domain test waveform. That is an explicit pre-test deliverable, not a blank to be silently filled by an operator.

## Pre-test deliverable from the integration partner

Provide one reviewed packet covering the actual fixture and the actual unit under test. Name the responsible mechanical, electrical and test reviewers; no reviewer is currently assigned.

The packet must contain the dated article BOM and drawings, received-unit identification, assembly/inspection method, torque and speed demand versus time, signs/coordinate conventions, repeat/rest schedule, loading method, rated fixture reaction/load limits, measurement-chain calibration and uncertainty, wiring/protection/grounding/regen scheme, and numeric warning/abort/acceptance limits. Separate normal stopping from loss of torque/support. The published motor maximum temperature is not a safe-touch limit or an automatic test release.

Record every numeric limit with its source, reviewer and applicable stage. Unset limits mean that stage cannot execute. The test should be restrained and guarded, with no child access and no human applying the test load by hand. Do not use unqualified whole-body fit-check prints as load-bearing test hardware.

## Finite execution sequence after separate approval

**Identity and inert inspection.** Confirm exact RS-485 SKU and firmware, received dimensions, horn/shaft/bearing arrangement, fastener retention, cable routes, guard fit and fixture restraint. Record as-built article mass and photographs. Independently verify calibration and sign conventions while disconnected. Reject substitutions until reviewed.

**Motor-only characterization.** Begin with the reviewed low-energy/no-load condition, then characterize only within the approved stage envelope. Log actual output torque and position independently of the motor's internal estimates, along with speed, current, voltage, internal reported temperature and relevant external temperatures. This stage may reject the motor before spending on a complete custom joint. It cannot qualify that joint.

**Complete LD-25 module.** Preserve the proposed actual shaft, bearings, carriers, adapter and belt. Check bidirectional efficiency, backlash, deflection and retention, then execute the approved representative waveform with its approved rest/repetition schedule. Log thermal evolution until the specified observation criterion or earlier abort. Compare measured output to the source trajectory and document model discrepancies. No extrapolation from one brief run to unlimited duty.

**Reviewed fault/stop tests.** Within the independently released fault-test envelope, verify communication loss/stale-command response, reset without automatic motion, local stop, loss of electrical power, regeneration handling and restrained mechanical response. Internal servo protection or the hub's switch does not establish functional safety. Do not inject faults until the fixture safely contains the consequences.

**Decision.** The reviewers issue RETAIN FOR COMPLETE-LEG TEST, REVISE, or INCONCLUSIVE with linked raw evidence. RETAIN requires all predeclared criteria to pass with stated uncertainty and an inspection after testing. REVISE identifies the smallest justified change and its mass/power/control impact. INCONCLUSIVE cannot be treated as a pass. None grants whole-body walking or safety validation.

## Evidence to return

Keep raw synchronized channels, calibration records, source hashes, instrument/sample identifiers, numeric approved limits, operator/reviewer identity, actual test duration and abort log. Required physical channels include independent output torque and angle, actuator telemetry, source voltage/current, ambient/case temperatures, and event markers; exact rates and timing uncertainty are approved before execution. Provide before/after backlash and inspection measurements, not just a video of motion.

Measured efficiency, torque-speed/duty behavior, delay and play feed the same LIGHT4 model. The next complete-leg stage uses those bounds. Do not create a competing robot revision without an explicit change decision.

## Cost and sourcing

[Machine-readable planning budget](first-tranche-budget.json); totals are reproduced by the checker.

| Cost class | USD | Basis |
| --- | ---: | --- |
| One XM430-W350-R | 333.39 | Displayed ROBOTIS catalog price |
| U2D2 | 36.92 | Displayed ROBOTIS catalog price |
| U2D2 Power Hub Board Set | 21.85 | Displayed ROBOTIS catalog price |
| Specialist review / load-profile preparation | 1,000–2,500 | Internal allowance, not quote |
| Restrained bench fixture / guard | 400–1,200 | Internal allowance, not quote |
| Complete drive mechanical parts | 200–500 | Internal allowance, not quote |
| Calibrated lab equipment access | 350–1,000 | Borrow/rent/contract assumption; not equipment purchase |
| Test execution / analysis | 800–2,000 | Internal allowance, not quote |
| Test wiring / protection / stop / regen | 150–400 | Internal allowance, not quote |
| One bounded rebuild reserve | 250–600 | Internal allowance; not automatic spare purchase |
| **Planning total** | **3,542.16–8,592.16** | **Before tax/shipping; not a purchasing approval** |

The apparent precision is arithmetic, not price certainty. Describe this externally as roughly $3.5k–$8.6k. Actual fixtures, available laboratory equipment and contractor scope can materially change it. Do not place an order against this range.

Product-page retrieval on 2026-09-25 exposed unresolved inconsistencies: the actuator title/SKU says -R while its package table says -T; the U2D2 page advertises USB-C but lists a Micro USB cable. The pages include Sold out and Add to cart language. No availability, reserved stock or lead time is established.

## Unsent, non-binding inquiry text

To ROBOTIS / an authorized distributor: Please confirm one XM430-W350-R, SKU 902-0118-000, RS-485 rather than TTL, its supplied horn/cables, availability, lead time and non-binding price. Please resolve the -R/-T package-table discrepancy. For U2D2 902-0132-000, confirm USB connector/hardware revision and included cable; also quote hub set 902-0145-001. Can you provide measured continuous-duty/thermal and torque-speed information, cooling/test conditions, allowed shaft/belt loads and regenerative-power guidance for the proposed ankle application? The public 0.82 Nm value is labeled an estimate, and we are not treating it as a qualified duty rating. No order or binding commitment is requested.

To an integration/test provider: Please quote an independent design/load review and a guarded one-axis motor-then-joint characterization, using the linked candidate interfaces. Separate review, article manufacture, instrumentation access/calibration, test execution/analysis and one optional rebuild. Identify supplied versus owner-supplied equipment and all missing design inputs. Return drawings, limits, raw measurements and a signed retain/revise/inconclusive disposition. No fabrication or powered work may begin without separate approval.

No inquiry has been sent and no supplier quote has been received in this sprint.

## Primary sources

- Existing repository files linked above and SHA-256 bindings in [baseline.lock.json](baseline.lock.json).
- [ROBOTIS XM430-W350-R product page](https://robotis.us/products/dynamixel-xm430-w350-r): exact candidate, displayed price, estimated-torque disclosure and unresolved package-table mismatch.
- [ROBOTIS XM430 manual](https://emanual.robotis.com/docs/en/dxl/x/xm430-w350/): operating/control and performance boundaries; stall is not continuous capacity.
- [ROBOTIS U2D2](https://robotis.us/products/u2d2) and [hub](https://robotis.us/products/u2d2-power-hub-board-set): displayed prices and interface definitions, not functional-safety qualifications.
