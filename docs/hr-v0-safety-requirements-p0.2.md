# HR-V0 safety-requirements candidate P0.2

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION.**

Identifier: `HR-V0-SRS-P0.2`
Control round: R218
Control date: 2026-08-11

## Decision

This package turns the existing HR-V0 safety-function framework into measurable candidate requirements for the first guarded single-joint motion phase. It does **not** assign a required Performance Level, claim a category, claim a SIL, validate a safety function or authorize physical work.

The applicable machine boundary remains:

- adult-only engineering prototype;
- fixed, tool-removable guard and passive receiver;
- rigid bench restraint;
- no child or bystander access to the hazard zone;
- no automatic motion on this evidence; and
- ordinary heartbeat diagnostic `DF-01` receives zero safety credit.

The machine-readable package is `release/hr-v0/safety-requirements-p0.2/`.

## Candidate first-motion limit

The current J2-positive controlled geometry has a 115.000-degree software boundary and a nominal 118.000-degree positive metal stop. R218 allocates, for qualified review, no more than 2.000 degrees of residual travel at setup speed while retaining a nominal 1.000-degree geometric reserve before tolerance, backlash, compliance and uncertainty deductions.

At the existing setup-speed ceiling:

```text
candidate speed = 10.000 deg/s
candidate residual travel = 2.000 deg
candidate total response = 2.000 / 10.000 = 0.200 s = 200 ms
```

This is a **candidate design and acceptance limit**, not measured performance. It applies only to guarded E4 J2-positive setup motion after every earlier phase gate is accepted.

Keeping the same 2.000-degree envelope at the existing 30.000-degree/s automatic joint ceiling would require:

```text
2.000 / 30.000 = 0.066667 s = 66.667 ms
```

Automatic motion remains prohibited on this evidence. The project shall not assume that the proposed contactors, rail, actuator and mechanism can meet 66.667 ms.

## Component timing screen

The controlled Pilz PNOZ s4 `21396-EN-23` manual lists a maximum 20 ms delay-on de-energisation with E-stop for order code `750104`. It also lists a maximum 70 ms switch-on delay for falling-edge monitored start. The controlled Schneider record lists 24 ms as the upper end of the published `LC1D25BD` opening-time component range.

A deliberately conservative sequential arithmetic screen is therefore:

```text
20 ms safety-relay de-energisation maximum
+24 ms contactor opening component maximum
=44 ms component-only screen
```

At 10 degrees/s, 44 ms corresponds to 0.440 degrees. The remaining unproven allocation inside the R218 candidate is 156 ms and 1.560 degrees. That allocation must cover actual channel behavior, coil/output behavior, contact opening, rail decay, regenerated energy, actuator torque decay, mechanical coast, measurement uncertainty and statistical variation.

At 30 degrees/s, the same arithmetic consumes 1.320 degrees and leaves only 22.667 ms / 0.680 degrees for every unmeasured term. This is another reason automatic motion is not released.

Component numbers are not complete-function performance. Neither contactor DC application suitability nor loaded interruption is accepted.

## Credited candidates and non-credited measures

| ID | R218 boundary | Current credit |
|---|---|---|
| `SF-01` | dual-channel emergency-stop actuator-energy removal through two series final elements | candidate only; PLr/SIL and validation open |
| `SF-03` | prevention of unexpected restart with monitored RESET, later distinct ARM, EDM and fresh trajectory | candidate only; PLr/SIL and validation open |
| `DF-01` | ordinary Raspberry Pi/RP2040 heartbeat diagnostic | zero safety credit; failure assumed |
| `PG-01` | fixed guard, passive receiver and bench restraint | physical measure; no SRP/CS label and no credit before physical release |

The qualified reviewer must determine whether this boundary is sufficient, whether another safety function is required, and whether the proposed component architecture can achieve the selected integrity and timing targets.

## Required validation

The controlled matrix contains sixteen unexecuted scenarios. It includes:

- both E-stop channel orders;
- either K1 or K2 deliberately prevented from opening;
- E-stop release without reset;
- RESET held during release;
- valid RESET without later ARM;
- ARM held or presented early;
- ARM without a fresh trajectory;
- heartbeat restoration;
- Raspberry Pi and watchdog reboot;
- K1/K2 mirror-contact discrepancies;
- 24 V brownout and recovery; and
- `DF-01` stuck valid while the physical containment case is assessed.

Test repetitions, measurement thresholds other than the controlled timing/travel candidates, uncertainty method and statistical acceptance remain for the qualified validation plan. Every row remains `NOT EXECUTED`.

## Qualified allocation remains open

`qualified-allocation-inputs.csv` deliberately leaves severity, exposure frequency/duration, avoidance, PLr/SIL, category/architecture, reliability data, diagnostic coverage, CCF scoring, reviewer competence, independence and signature as `SELECTION REQUIRED` or `NOT EXECUTED`.

The package identifies twelve common-cause topics but accepts no fault exclusion or safety credit. Shared supplies, enclosure/contamination, channel cable, RESET/ARM wiring, coil control, power-path bypass, EDM, suppression, rail regeneration, stale software commands, mechanical containment and maintenance bypass all remain open.

## Primary-source boundary

- ISO 12100:2010, Edition 1, published 2010-11, current official page rechecked 2026-08-11: <https://www.iso.org/standard/51528.html>
- ISO 13849-1:2023, Edition 4, published 2023-04, current official page rechecked 2026-08-11: <https://www.iso.org/standard/73481.html>
- ISO 13849-2:2012, Edition 2, published 2012-10, current official page rechecked 2026-08-11: <https://www.iso.org/standard/53640.html>
- ISO 13850:2015, Edition 3, published 2015-11, current official page rechecked 2026-08-11: <https://www.iso.org/standard/59970.html>
- Pilz PNOZ s4 operating manual `21396-EN-23`, controlled local PDF created 2026-06-17 and official product file dated 2026-06-22: <https://www.pilz.com/download/open/OM_PNOZ_s4_21396-EN-23.pdf>
- Schneider Electric `LC1D25BD` product data sheet, dated 2017-09-13 and live source rechecked 2026-08-11: <https://iportal.se.com/Contents/docs/SQD-LC1D25BD.PDF>

Official abstracts establish scope and revision. The responsible organization must obtain and control the complete applicable standards. Manufacturer component data does not approve the Project Button application.

## Release consequence

R218 improves the safety-requirements evidence from undefined total-response limits to one explicit, fail-closed first-motion candidate and one explicitly prohibited automatic-motion case. `EG-012`, `EG-021`, `EG-022` and `EG-026` remain partial. Physical hardware, exact rail threshold, loaded timing, guard/stop proof, PLr/SIL allocation and signed validation are still required.
