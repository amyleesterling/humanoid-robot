# Sol R12 Findings Rechecked After R89

Status: **PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**
Date: 2026-08-08

The Sol analysis resupplied on 2026-08-08 is the already-controlled R12 review, not a new independent round. Its exact totals and baseline match the archived dossier: 18 BLOCKER, 30 MAJOR, 8 MINOR, 62 draft requirements, 106 unresolved Electrical V2.1 selections and zero approved executed verification evidence. Sol did not review R13-R89.

Sol's headline verdict remains current: HR-V0 is not yet a buildable or energizable machine, and HR-30W walking remains physically plausible but unproved.

## Material R89 change

R89 independently re-audited the watchdog board's physical packages and found source errors that clean DRC could not detect:

- `ISO1` had a 6.8 mm inner copper gap against the 8.0 mm option-7 requirement.
- `UDRV1`, `UDRV2` and `UFB1` used generic alternate lands instead of the current TI example patterns.
- fifteen of seventeen audited passive references matched neither the cited manufacturers' published land envelopes; `RTH1/RTH2` matched a wave pattern while the candidate required a defined assembly process.

`PCB-P0.6` corrects the optocoupler, TI IC and all seventeen passive lands, records a proposed mixed reflow/manual-THT sequence and retains zero DRC violations. The immutable R88 PCB-P0.5 CAM package is superseded for current review, and no PCB-P0.6 CAM package has been issued.

## What R89 does not close

- assembler acceptance, stencil, mask, paste, reflow, hand-solder, cleaning, AOI, rework or first-article evidence;
- system-level creepage/clearance and functional-safety allocation;
- Phoenix support/torque/service geometry, DC1 land/drill rationale, Pico process proof, Harwin probe access or M3 hardware/load selection;
- physical PCB, harness, enclosure, EMC, thermal, fault-injection or HIL evidence;
- any fabrication, assembly, connection, motion or energization gate.

R89 is a project-owned correction pass. It does not reduce or close Sol's original 56 findings and does not constitute independent approval.
