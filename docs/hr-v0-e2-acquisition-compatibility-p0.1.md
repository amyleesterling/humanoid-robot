# HR-V0 E2 acquisition compatibility P0.1

> **PRELIMINARY - EVALUATION CANDIDATE ONLY - NOT APPROVED FOR PROCUREMENT, FABRICATION, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION.**

Identifier: **HR-V0-E2-ACQ-COMPAT-P0.1**

Round: **R182**

Date: **2026-08-10**

## Decision

R182 closes the R180 paper calculation for an eight-channel `MSO58B` acquisition population and names an exact independent displacement-witness candidate for guarded disconnected-load E2.

The candidate population is:

- four Tektronix `TCP0030A` current probes; and
- four Tektronix `TIVP02` isolated-voltage probes, each using the included `TIVPMX10X` tip.

Tektronix publishes maximum probe-power values of 8.4 W for `TCP0030/A` and 9.5 W for `TIVP02/05/1`. The current MSO58B performance-verification record publishes eight TekVPI interfaces, 80 W total probe power and two 40 W banks covering channels 1-4 and 5-8.

A balanced two-current-plus-two-voltage-probe population in each bank gives:

`2 × 8.4 W + 2 × 9.5 W = 35.8 W per bank`

`4 × 8.4 W + 4 × 9.5 W = 71.6 W total`

The documented margins are 4.2 W per bank and 8.4 W total. This is an arithmetic compatibility result, not a received-equipment, firmware, calibration, self-test or powered compatibility result. The exact MSO58B order configuration remains `SELECTION REQUIRED`.

## Correct channel balance

R180's sequential CH1-CH8 listing would place four current probes in channels 1-4 and four voltage probes in channels 5-8. That arrangement would use 33.6 W in the first bank and 38.0 W in the second, both inside the published bank limits, but R182 intentionally balances two current and two voltage probes in each bank to preserve equal documented margins.

The logical channel mapping is therefore reordered without changing any R180 signal semantics:

| Channel | Bank | Probe | STOP role | RESET/ARM role |
|---|---|---|---|---|
| CH1 | 1-4 | TCP0030A | `SR1_S12` STOP-event current | `SR1_START_RETURN` RESET-event current |
| CH2 | 1-4 | TCP0030A | K1 coil current | `ARM_AFTER_S2` ARM-event current |
| CH3 | 1-4 | TIVP02 | K1 NO auxiliary diagnostic voltage | same |
| CH4 | 1-4 | TIVP02 | K2 NO auxiliary diagnostic voltage | same |
| CH5 | 5-8 | TCP0030A | K2 coil current | K1 coil current |
| CH6 | 5-8 | TCP0030A | one common series-EDM-chain current | K2 coil current |
| CH7 | 5-8 | TIVP02 | control-source voltage | same |
| CH8 | 5-8 | TIVP02 | independent Q4X no-motion witness | same |

STOP and RESET/ARM remain two separate physical runs. No cross-run simultaneity is claimed. The analyzer field mapping must be configured per run and independently checked before any authorized acquisition.

## Exact independent displacement candidate

Banner Engineering `Q4XFULAF110-Q8`, part number `97540`, is the exact E2 evaluation candidate. Current manufacturer records identify:

- flush-mount Class 1 visible-red laser;
- 35 mm to 110 mm sensing range;
- 0 V to 10 V analog output;
- 12 Vdc to 30 Vdc supply;
- less than 675 mW consumption excluding load;
- integral five-pin M12 male quick disconnect;
- 0.5 ms minimum response time;
- less than 0.15 mm analog resolution across the 35-110 mm range; and
- 2.5 kohm minimum load resistance for the voltage-output model.

The manufacturer wiring definition assigns pin 1/brown to supply, pin 2/white to remote input, pin 3/blue to supply return, pin 4/black to analog output and pin 5/gray to analog ground, with the shield shown separately. The proposed CH8 observation is differential across pin 4 and pin 5 using `TIVP02/TIVPMX10X`.

Tektronix publishes the `TIVPMX10X` input as 10 Mohm in parallel with 2.8 pF, a ±50 V differential range and an 18.3 ns propagation delay for the two-metre TIVP02 system. The 10 Mohm loading exceeds Banner's 2.5 kohm minimum-load requirement on paper. Physical loading, lead arrangement, EMI susceptibility, deskew and uncertainty remain unverified.

## Interpretation boundary

The Q4X candidate may provide an independent displacement witness for **absence of motion** in guarded disconnected-load E2. It is not selected for, and R182 does not claim:

- absolute joint-angle measurement;
- powered stopping time or residual travel;
- guard-clearance reconciliation;
- all-pose or all-axis visibility;
- redundant or safety-rated position feedback; or
- any safety-function credit.

The final no-motion limit cannot be copied from the catalog. It must be derived from the received sensor, selected target, exact operating distance, reflectance, alignment, fixture stiffness, temperature, response/averaging configuration, calibration and complete uncertainty budget. The manufacturer performance curves are conditional; no single repeatability number is released.

## Physical connection remains prohibited

Fifteen closure holds remain `SELECTION REQUIRED`, including:

1. exact host configuration, firmware, serial and calibration;
2. all eight received probe identities and balanced installed-probe power check;
3. current-probe jaw fit, conductor identity, polarity and noninterference;
4. protected K1/K2 diagnostic loads and returns;
5. protected control-source test points;
6. exact Q4X cordset and continuity evidence;
7. isolated instrumentation supply, protection, grounding and no-backfeed evidence;
8. sensor mount and target geometry;
9. locked sensor configuration;
10. accepted no-motion threshold and uncertainty;
11. scope timing, trigger, range, deskew and filtering configuration;
12. connection schedule and qualified pre-test review;
13. authorized guarded E2 execution and immutable raw evidence;
14. a separate powered-motion stopping architecture; and
15. qualified electrical and functional-safety disposition.

Two manufacturer inquiries are drafted but **not sent**. No provider contact is authorized by this package.

## Sol R12 reconciliation

The supplied 18-BLOCKER / 30-MAJOR / 8-MINOR Sol summary describes the same independent R12 baseline review already controlled in this repository and is not counted as a new review round. R182 advances only one narrow prerequisite: compatible paper population and exact E2 displacement-witness candidate. It does not change Sol's overall verdict:

- HR-V0 build readiness remains **NOT READY**;
- HR-V0 energization remains **PROHIBITED**;
- HR-30W remains physically plausible but unproven; and
- the mechanical definition, physical wiring, safety allocation, stopping evidence, mass/inertia closure, continuous drivetrain capability and qualified validation remain open.

## Gate effect

- `EG-025` remains **open**.
- `EG-026` remains **partial**.
- zero physical compatibility runs and zero field connections exist;
- no acquisition equipment, sensor, auxiliary diagnostic or analysis receives safety credit; and
- no procurement, fabrication, connection, powered testing, motion or energization is authorized.
