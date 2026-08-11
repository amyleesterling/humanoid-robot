# HR-V0 P1.21 nominal DCR and voltage-drop screen P0.1

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Identifier: `HR-V0-P121-DCR-DROP-P0.1`

Review round: R244

Date: 2026-08-11

## Outcome

R244 adds a reproducible manufacturer-nominal resistance input for the held Belden/Alpha Wire 3057 conductor and calculates four deliberately limited path screens. The current official Alpha Wire product record publishes **4.4 ohm/1000 ft at 20 C nominal**, which converts to **0.014435695538 ohm/m**.

The calculations use R242 planning centerlines and published typical/derived load inputs. They are **one-way, centerline, 20 C, conductor-only planning values**. They are not complete circuit voltage-drop results and are not accepted design limits.

| Path | Nominal conductor resistance | Nominal conductor-only drop |
|---|---:|---:|
| C-01, 1.37025 m, 2.5 W / 24 V derived steady load | 0.019780512 ohm | 0.002060470 V |
| C-02, 1.30025 m, 18 mA typical coil current | 0.018770013 ohm | 0.000337860 V |
| C-03+C-06+C-07, 1.50425 m, 2.5 W / 24 V derived steady load | 0.021714895 ohm | 0.002261968 V |
| C-04, 1.27425 m, 18 mA typical coil current | 0.018394685 ohm | 0.000331104 V |

For the two Pilz supply paths, the nominal conductor-only screen also records 0.009890256 V and 0.010857448 V at the published 0.5 A / 5 ms inrush. C-05 remains uncalculated because the complete feedback burden is not defined.

## What the arithmetic excludes

- the return conductor and complete circuit topology;
- actual cut lengths, bend arcs, terminal entry and service allowance;
- received-lot resistance and its measurement uncertainty;
- resistance change with conductor temperature;
- source tolerance, source droop and protective-device impedance;
- terminal, ferrule, relay-contact and connector resistance;
- maximum KWD coil current across voltage and temperature;
- the KWD2:21 feedback burden;
- a qualified minimum-voltage or maximum-drop acceptance criterion;
- branch-protection coordination, thermal validation and physical test results.

`R242-H03` is therefore only **partially addressed and remains open**.

## Exact driver-bit disposition

Current primary documentation does not support an exact purchase-ready driver bit without inference.

- Pilz manual `21396-EN-23` gives the 750104 tightening torque and strip length but no drive form, blade geometry, access envelope or approved tool order code. The Pilz bit remains `SELECTION REQUIRED`.
- Phoenix item `2967060` gives an M3 screw and 0.6 to 0.8 N m torque but no drive form or bit pairing. Phoenix `1212568` (slotted 0.6 x 3.5 x 50 mm, E6.3) is the strongest held candidate; `1212569` is the 70 mm alternative. Neither is selected until Phoenix confirms the exact 2967060 + 1212224 combination and required reach.

Both interfaces still require unpowered fit/access checks on received terminals, current torque-tool calibration and witnessed installation evidence.

## Controlled artifacts

- Engineering evidence: `electrical/routing/hr-v0-p121-dcr-drop-p0.1/`
- Interactive guide: `release/hr-v0/p121-dcr-drop-p0.1/index.html`
- Configuration reconciliation: `HR-V0-CONFIG-REC-P0.8`
- Reproduction: `tools/generate_hr_v0_p121_dcr_drop_p01.py`
- Validation: `tools/check_hr_v0_p121_dcr_drop_p01.py`

P1.15 remains the current electrical candidate. P1.21 and R244 remain unaccepted. No protection, temperature, wiring, work or safety gate closes.
