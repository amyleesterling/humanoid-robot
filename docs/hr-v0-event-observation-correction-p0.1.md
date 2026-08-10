# HR-V0 event-observation independence correction P0.1

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION.**

Document ID: **HR-V0-EVENT-OBS-CORR-P0.1**

Round: **R180**

Date: **2026-08-10**

Electrical configuration: **Project Button Electrical V3-P1.15-CARRIER-CANDIDATE**

## Correction

R174-R179 incorrectly allowed two conductors in one series external-device-monitoring path to be interpreted as two independent contactor mirror-state channels. They are not independent:

`SRA1 feedback source -> K1:21-22 NC mirror -> EDM_K1_OUT -> K2:21-22 NC mirror -> SRA1_START_RETURN -> SRA1:S34`

When the chain is closed, the same series current flows through `EDM_K1_OUT` and `SRA1_START_RETURN`. A current observation at both locations cannot identify which contact changed. R180 therefore supersedes only that semantic interpretation; the historical artifacts remain intact and the R178 no-connect disposition still controls.

The corrected observation model uses:

- one common EDM-chain current witness at `SRA1_START_RETURN` (`W3007`, `SRA1:S34`), with `EDM_K1_OUT` allowed only as an alternative location;
- separate `K1_STATUS` and `K2_STATUS` NO auxiliary diagnostic-voltage channels for individual corroboration;
- both contactor-coil current channels;
- the initiating event, control-source voltage and independent motion witness on the same accepted timebase.

The NO auxiliary channels receive **zero safety credit** and do not replace the NC mechanically linked mirror-contact EDM chain.

## Eight-channel acquisition candidate

Tektronix `MSO58B` is an exact eight-input host **evaluation candidate**. Four `TCP0030A` probes and three `TIVP02` isolated-voltage probes, each with its included `TIVPMX10X` tip, are exact probe evaluation candidates for one simultaneous run. The eighth input is reserved for an independent motion witness, which remains `SELECTION REQUIRED`.

The exact MSO58B bandwidth, record-length, OS/storage, calibration and order configuration remain `SELECTION REQUIRED`. Simultaneous probe-power compatibility also remains open. The current 5 Series B specification identifies an 80 W total probe-power limit split into two 40 W four-channel groups; R180 does not infer that the proposed seven-probe population fits those limits.

### STOP run

| Channel | Signal | Candidate | Interpretation boundary |
|---|---|---|---|
| CH1 | `SR1_S12` stop-event current | `TCP0030A` | event witness only after thresholds/uncertainty close |
| CH2 | `K1_A1` coil current | `TCP0030A` | command current, not contact position |
| CH3 | `K2_A1` coil current | `TCP0030A` | command current, not contact position |
| CH4 | common `SRA1_START_RETURN` EDM current | `TCP0030A` | series-chain state, not individual contact identity |
| CH5 | `K1_STATUS` diagnostic voltage | `TIVP02/TIVPMX10X` | blocked pending exact load/protection; zero safety credit |
| CH6 | `K2_STATUS` diagnostic voltage | `TIVP02/TIVPMX10X` | blocked pending exact load/protection; zero safety credit |
| CH7 | `SAFETY_24V` relative to `SAFETY_0V` | `TIVP02/TIVPMX10X` | exact isolated test points remain `SELECTION REQUIRED` |
| CH8 | independent motion | `SELECTION REQUIRED` | only this channel can support stopping/no-motion evidence |

### RESET/ARM run

CH1 and CH2 become `SR1_START_RETURN` RESET current and `ARM_AFTER_S2` current. CH3-CH8 retain both coil currents, both individual diagnostic auxiliaries, source voltage and independent motion. This permits a simultaneous check that releasing/resetting the E-stop alone does not produce contactor-coil command current or motion. Exact acceptance limits remain unresolved; no run has executed.

## Diagnostic auxiliary circuit is not released

P1.15 feeds K1:13 and K2:13 from `SAFETY_24V` and exposes `K1_STATUS` at `XT1-05` and `K2_STATUS` at `XT1-06`, but each output presently ends at the terminal and has no defined receiver/load/return. A non-contact current probe would therefore observe no useful status current. A voltage interpretation requires an exact protected diagnostic load and return to `SAFETY_0V`.

Schneider's controlled application evidence identifies 5 mA at 17 V as the minimum signaling-current condition for the LC1D25BD auxiliary contact. R180 does **not** select a resistor value or part number from that number. Closure requires:

1. exact load, protection, conductor and return paths from `XT1-05`/`XT1-06` to `SAFETY_0V`, while preserving the controlled `SAFETY_24V` feeds to K1:13/K2:13;
2. minimum-current proof over rail minimum, tolerance, temperature and wiring resistance;
3. maximum voltage/current/power/temperature and transient proof;
4. open, short, wrong-value, cross-channel and source-loss fault analysis;
5. valid/invalid threshold and disagreement logic;
6. proof that the diagnostic circuit cannot create automatic restart or mask an EDM fault; and
7. qualified electrical and functional-safety acceptance.

No diagnostic load, resistor network, test lead or probe connection is approved.

## Sol R12 reconciliation

The supplied Sol analysis is the same independent R12 review and is not counted again. R180 directly addresses one evidence-chain defect revealed while working the R12 stopping-time and physical-instrumentation blockers. It does not change Sol's overall verdict:

- HR-V0 build readiness remains **NOT READY**;
- HR-V0 energization remains **PROHIBITED**;
- no physical stopping, reset-without-motion or fault-injection evidence exists;
- functional-safety allocation and qualified validation remain open; and
- HR-30 walking remains a later feasibility program, not a released build.

## Gate effect

- `EG-025` remains **open**.
- `EG-026` remains **partial**.
- zero diagnostic loads and zero physical connections are released;
- zero physical tests have executed;
- the MSO58B, probes and all test instrumentation receive **zero safety credit**; and
- no procurement, fabrication, connection, powered test, motion or energization is authorized.
