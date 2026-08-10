# HR-V0 P1.15 watchdog/E2 parity P0.1

Status: **PRELIMINARY - DIGITAL CONFIGURATION PARITY ONLY - NOT APPROVED FOR FABRICATION, CONNECTION, TEST, MOTION, OR ENERGIZATION**

Identifier: `HR-V0-E2-P115-PARITY-P0.1`

## Result

The P1.14 and P1.15 native netlists and synchronized schedules show:

- 69 shared component references outside the declared actuator change subset are exactly unchanged;
- all 263 terminals on those references retain identical sheet, terminal, pin-name, scheduled net, status and native net membership;
- 28 explicit E2 references, including S0, RESET, ARM, SR1/SRA1, K1/K2, KWD1/KWD2, watchdog controller/driver/feedback references, control sources, XT1 and watchdog debug test points, retain exact parity;
- the complete component change boundary is seven changed actuator references (`F1`-`F3`, `INJ1`, `J1`-`J3`) plus three added P0.3 carrier interfaces (`LIM1`-`LIM3`);
- native ERC remains 0 errors and 0 warnings for both P1.14 and P1.15.

This closes the internal digital compatibility question only. The changed actuator subset remains physically absent or unwired for E2. Digital parity does not prove received hardware, physical wiring, ratings, separation, protection, workmanship, firmware behavior, functional safety, or authorization to connect power.

## Remaining evidence

Twelve holds and eight independent acceptance rows remain open. They include independent parity acceptance, supplier/process and first-article evidence, lot-specific operator mappings, protection coordination, conductor and enclosure definition, physical actuator exclusion, HIL/fault testing, accepted instruments and limits, and four-role E2 authorization.

Interactive guide: `release/hr-v0/e2-p115-parity-p0.1/index.html`.
