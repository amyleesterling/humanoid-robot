# HR-V0 corrected dynamic-trace analysis P0.2

> **PRELIMINARY - ANALYSIS CANDIDATE ONLY - QUALIFIED DISPOSITION REQUIRED - NOT APPROVED FOR CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION.**

Identifier: **HR-V0-DYN-TRACE-P0.2**

Round: **R181**

Date: **2026-08-10**

## Decision

`HR-V0-DYN-TRACE-P0.1` is superseded for current use. Its DTA-003 rule treated two mirror channels as independent and its single trace schema combined STOP and RESET evidence that cannot fit the R180 eight-input simultaneous acquisition plan.

P0.2 creates two separate physical-run contracts:

1. one eight-channel disconnected-load E2 `STOP` trace; and
2. one eight-channel `RESET_ARM` trace.

No cross-run simultaneity is claimed. Both physical configuration templates reject execution while their numeric limits remain `SELECTION REQUIRED`.

## Corrected contact-state semantics

During the active state, the K1/K2 coils and their individual NO auxiliary diagnostics are asserted while the two NC mirror contacts hold the series EDM chain open. After a STOP demand:

- K1 coil current falls;
- K2 coil current falls;
- K1 NO auxiliary diagnostic voltage falls;
- K2 NO auxiliary diagnostic voltage falls; and
- the one common NC-mirror EDM chain closes, producing a rising common-chain observation.

The two NO auxiliaries are diagnostic corroboration only and receive **zero safety-function credit**. They do not replace the common NC-mirror EDM chain. `EDM_K1_OUT` and `SRA1_START_RETURN` remain locations in that same series chain and are never counted as two independent contact states.

## STOP trace: eight simultaneous physical channels

| Channel role | P0.2 field | Interpretation |
|---|---|---|
| stop-event witness | `stop_event_state` | one controlled rising STOP edge |
| K1 coil current | `k1_coil_state` | falling command-current state |
| K2 coil current | `k2_coil_state` | falling command-current state |
| common series EDM current | `common_edm_chain_state` | rising chain-closed state after both NC mirrors return |
| K1 NO auxiliary voltage | `k1_aux_status_state` | falling diagnostic state; zero safety credit |
| K2 NO auxiliary voltage | `k2_aux_status_state` | falling diagnostic state; zero safety credit |
| control-source voltage | `source_voltage_V` | must remain valid throughout the observation window |
| independent motion | `external_angle_deg` | must remain within the accepted E2 no-motion noise band |

The actuator source is physically absent and K1/K2 load poles are unsourced and unwired. The analyzer computes event/contact transition times, verifies that the control supply remains valid, and rejects measured motion. It fails if the common EDM chain does not close, either coil/auxiliary transition is absent or duplicated, any transition exceeds its accepted limit, the control source becomes invalid, or motion exceeds the accepted noise band.

This E2 trace cannot prove powered-motion stopping time, residual travel, actuator-source removal or hard-stop clearance. Those require a later separately authorized and separately instrumented test architecture.

## RESET/ARM trace: eight simultaneous physical channels

| Channel role | P0.2 field | Interpretation |
|---|---|---|
| monitored RESET witness | `reset_event_state` | one controlled rising RESET edge |
| separate ARM witness | `arm_event_state` | exactly one later edge after the selected interval |
| K1 coil current | `k1_coil_state` | must remain false before ARM |
| K2 coil current | `k2_coil_state` | must remain false before ARM |
| K1 NO auxiliary voltage | `k1_aux_status_state` | must remain false before ARM; diagnostic only |
| K2 NO auxiliary voltage | `k2_aux_status_state` | must remain false before ARM; diagnostic only |
| control-source voltage | `source_voltage_V` | must remain valid so no-motion is not explained by brownout |
| independent motion | `external_angle_deg` | must remain within the accepted noise band before ARM |

This directly evaluates the requirement that releasing/resetting the E-stop cannot command contactor energization or motion. It does not prove the requirement until the exact interfaces, thresholds, physical run matrix, repeated results and qualified disposition are accepted.

## Synthetic code-path validation

Six generated traces exercise the analyzer:

- nominal STOP: computed `PASS`, disposition `HOLD`;
- missing common-EDM closure: `FAIL`, `REJECT`;
- dropped-scan/sample-index defect: `FAIL`, `REJECT`;
- measured motion in disconnected-load E2: `FAIL`, `REJECT`;
- nominal RESET then distinct ARM: computed `PASS`, disposition `HOLD`; and
- coil/auxiliary/motion activity before ARM: `FAIL`, `REJECT`.

The nominal E2 STOP fixture reports K1/K2 coil drops at 5/6 ms, K1/K2 diagnostic auxiliary openings at 10/11 ms and common EDM closure at 12 ms after the synthetic event, with zero angle change and a valid 24 V control source. The nominal RESET fixture has a 0.070 s reset-to-ARM interval and zero synthetic angle change. These values validate code paths only; they are not proposed physical acceptance limits.

## Still required

- exact `MSO58B` configuration and simultaneous probe-power proof;
- exact independent motion witness, calibration, mount and angle conversion;
- exact protected K1/K2 diagnostic loads and thresholds;
- accepted event/current/source thresholds, hysteresis and dwell;
- accepted sample interval, trace length, trigger, deskew, filter and timing uncertainty;
- qualified E2 contact-transition timing allocation and no-motion/source-valid limits;
- a separate later powered-motion acquisition architecture and qualified stopping-time/travel/clearance allocation;
- complete load/pose/fault/repetition matrix and disconnected-load E2 authorization;
- immutable raw traces, configuration, video and calibration evidence; and
- named competent and independent reviewers with signed configuration-specific dispositions.

## Gate effect

- `EG-025` remains **open**.
- `EG-026` remains **partial**.
- zero physical runs and zero released numeric thresholds exist;
- P0.1 remains historical and is not valid for current physical evidence;
- all acquisition equipment and diagnostic channels receive **zero safety credit**; and
- no procurement, fabrication, connection, powered test, motion or energization is authorized.
