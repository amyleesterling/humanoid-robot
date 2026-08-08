# HR-V0 watchdog PCB build-and-test traveler P0.1

> **PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**

- Identifier: `HR-V0-WD-TRAVELER-P0.1`
- CAM candidate: `HR-V0-WD-FAB-P0.1`
- PCB: `PCB-P0.5`
- Electrical compatibility: `Project Button Electrical V3-P1.13`
- Date: 2026-08-08

## Purpose

This traveler turns the watchdog-board portion of Sol's “drawings, exact
parts, test fixtures and fault injection” finding into an executable evidence
route. It does not authorize any physical action. Every operation starts
`NOT_EXECUTED`; numerical limits remain `SELECTION REQUIRED` until derived,
reviewed and signed for the exact instruments, article and source.

The watchdog board has **zero safety credit**. Passing board tests cannot
establish a PL, SIL, Category, safety function, permission to fabricate, or
permission to energize Project Button.

## Hard boundaries

- No supplier upload or order until all applicable CAM-review rows pass and a
  separately named fabrication authority signs the exact commit/package.
- No assembly until received bare-board and part identities pass.
- No board power until the pre-power inspection is signed by a qualified
  electrical reviewer.
- The first board source is an isolated, current-limited laboratory source;
  its voltage, current limit, stop limits, wiring, grounding and instrument
  ratings must be selected and approved before use.
- The safety relay, contactors, external 24 V source, Raspberry Pi supervisor,
  actuator source, U2D2, actuators and all motion hardware remain disconnected.
- Only approved dummy loads may replace relay coils during board bring-up.
- Any changed file, received substitution, rework, unexpected reading,
  instrument expiry or configuration mismatch stops the traveler and revokes
  the run authorization.

## Phase gates

| Gate | Required evidence | Decision authority | Default |
|---|---|---|---|
| WD-TG-01 source freeze | commit, package manifest, regenerated checker PASS | configuration manager + independent reviewer | OPEN |
| WD-TG-02 CAM review | completed `hr-v0-watchdog-pcb-cam-review-template.csv`, layer screenshots, supplier response | qualified electrical reviewer + fabrication authority | OPEN |
| WD-TG-03 fabrication order | exact job/order record and separately signed authorization | program owner + fabrication authority | PROHIBITED |
| WD-TG-04 bare-board receipt | supplier certificates, visual/dimensional/electrical evidence | quality reviewer | OPEN |
| WD-TG-05 assembly release | exact part receiving, process plan, orientation review | assembly lead + independent reviewer | PROHIBITED |
| WD-TG-06 pre-power release | completed receiving/assembly form and accepted resistance/isolation limits | qualified electrical reviewer | PROHIBITED |
| WD-TG-07 disconnected-load bring-up | signed instruments, limits, fixtures, exclusion and stop-work briefing | test director + electrical reviewer + witness | PROHIBITED |
| WD-TG-08 board validation | raw HIL/fault/brownout/thermal/EMC data and independent disposition | qualified electrical + functional-safety reviewers | OPEN |
| WD-TG-09 E2 integration eligibility | E2-HOLD-008 closure evidence referenced without closing other E2 holds | E2 authorization roles | OPEN |

## Controlled records

1. `release/hr-v0/watchdog-pcb-fabrication-candidate-p0.1/` — CAM review candidate.
2. `tests/forms/hr-v0-watchdog-pcb-cam-review-template.csv` — 24 independent CAM and authorization checks.
3. `tests/forms/hr-v0-watchdog-pcb-receiving-assembly-template.csv` — 18 receiving and assembly operations.
4. `tests/forms/hr-v0-watchdog-pcb-current-limited-bringup-template.csv` — 16 staged bring-up operations.
5. `tests/forms/hr-v0-watchdog-pcb-inspection-template.csv` — board performance inspection summary.
6. `tests/forms/hr-v0-watchdog-drive-test-template.csv` and `hr-v0-watchdog-fault-injection-template.csv` — waveform and fault evidence.

Do not overwrite templates with results. Copy them into a dated article folder,
record the accepted commit and board serial, preserve raw instrument exports,
photographs and calibration certificates, and hash the complete evidence set.

## E2 disposition

This traveler advances `E2-HOLD-008` from “no fabrication package” to “CAM
review candidate and unexecuted physical route exist.” It does **not** close
that hold. Supplier acceptance, order authorization, bare-board test,
assembly, HIL, fault, brownout, thermal, EMC and qualified dispositions all
remain missing.

All other E2 holds remain unchanged. In particular, no selected protection,
approved conductors, fabricated enclosure, accepted firmware, calibrated test
setup, four-role run authorization, or physical proof of actuator-source
absence exists.
