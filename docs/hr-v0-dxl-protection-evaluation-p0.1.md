# HR-V0 DXL branch-protection evaluation P0.1

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, MOTION, OR ENERGIZATION**

- Identifier: `HR-V0-DXL-PROT-EVAL-P0.1`
- Review round: R155
- Date: 2026-08-09

## Result

R155 turns R154's external-current-control option into a connected native KiCad evaluation candidate without selecting it for the robot. Three `TPS259461LRPWR` latch-off eFuse candidates sit between the separately fused branch inputs and the existing DXL-star inputs. Pololu item 3771 is modeled across the post-K2 actuator bus only as a short-pulse regenerative-clamp candidate.

The current Electrical V3-P1.14 robot baseline, system BOM, firmware external-current hold and all work-authority flags remain unchanged.

## Decisive limitation

TI specifies TPS25946 overcurrent protection from IN to OUT only. While enabled, reverse current can flow from OUT to IN without that current limit. The eFuse therefore cannot by itself bound actuator regeneration. TPS25947's always-active true reverse blocking was rejected for this path because returned energy would be isolated on the actuator side unless a separately validated local sink and overvoltage design existed.

Pololu item 3771 has a fixed 13.2 V setpoint with ±3% tolerance and a 1.50 ohm, 15 W relative-average resistance. The manufacturer describes occasional motor-regeneration pulses and warns that continuous voltage above the setpoint can destroy the product quickly. It is not a continuous dump load or safety function.

## Candidate arithmetic

- J1/J2 1.65 kohm ILM screen: 1.782178 to 2.222222 A after the application-level ±1% resistance corner screen.
- G1 3.32 kohm ILM screen: 0.841584 to 1.161616 A after the same screen.
- Derived UVLO rising screen: 9.664856 to 10.349515 V.
- Derived OVLO rising screen: 13.513315 to 14.490473 V.
- Pololu setpoint screen: 12.804 to 13.596 V.
- Conservative source-high plus full published ripple screen: 12.720 V, leaving only 0.084 V to the lowest shunt setpoint. Received nuisance-clamp evidence is mandatory.
- `13.2 V / 1.50 ohm = 8.8 A` and `13.2² / 1.50 ohm = 116.16 W` are arithmetic demonstrations of the pulse-only boundary, not manufacturer ratings for permitted current, time or energy.

## Controlled package

- Native KiCad: `electrical/kicad/hr-v0-dxl-protection-eval/`
- Interactive guide and evidence templates: `release/hr-v0/dxl-protection-evaluation-p0.1/`
- Generator: `tools/generate_hr_v0_dxl_protection_evaluation.py`
- Checker: `tools/check_hr_v0_dxl_protection_evaluation_p01.py`

KiCad 10.0.5 parses all five native sheets and reports ERC 0 errors / 0 warnings. That result covers encoded connectivity and annotation only. Fourteen physical test rows remain `NOT EXECUTED / NOT AUTHORIZED`; eighteen acceptance groups remain open.

## Required closure before selection

The exact passive order codes and derating, RPW PCB land/paste/assembly process, copper and thermal design, harness/contact/conductor/crimp definition, forward and reverse current waveforms, shunt pulse energy and cooling, source interaction, K1/K2 opening behavior, simultaneous-axis regeneration, fuses and fault coordination, DXL integrity, received HIL, qualified multidisciplinary review and separate written work authorization must all be accepted. No PCB, purchase, fabrication, assembly, connection, motion or energization is released.
