# HR-V0 P1.20 PNOZ/KWD application dossier P0.2

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Identifier: `HR-V0-PNOZ-KWD-APP-P0.2`

Round: R233

Date: 2026-08-11

## Decision

The P1.20 contact application passes a limited manufacturer-data screen. The proposed Pilz PNOZ s4 750104 input/start/feedback circuits are specified at 24 VDC and 50 mA. The proposed Phoenix Contact 2967060 ordinary relay contacts have a published minimum switching load of 5 V at 10 mA and published switching envelopes above the Pilz input load. Derived paper margins are 4.8 times voltage, 5.0 times steady current and 75 times the maximum stated Pilz input-inrush current.

This result means only that the proposed contact/load pairing is not rejected by the checked catalog limits. It does **not** establish reliable life in the installed environment, maximum response time, diagnostic coverage, functional-safety performance, achieved PL/SIL/Category, or permission to procure, fabricate, connect, test or energize.

The Phoenix relay is not treated as force-guided or safety-rated. `KWD1` and `KWD2` receive zero safety credit.

## Exact P1.20 signal paths

Channel 1:

`SRA1:S11 -> SR1:13-14 -> KWD1:11-14 -> SRA1:S12`

Channel 2:

`SRA1:S21 -> SR1:23-24 -> KWD2:11-14 -> SRA1:S22`

Monitored ARM/EDM return:

`SRA1:S12 -> S2:TBD-A1/TBD-A2 -> K1:21-22 -> K2:21-22 -> SRA1:S34`

The package machine-checks every selected terminal and net against the P1.20 connector schedule. Direct dual-channel E-stop paths remain separate from the ordinary heartbeat interlocks. Heartbeat restoration must not create a fresh monitored ARM event or a motion command.

## Manufacturer-source findings

Pilz Operating Manual `21396-EN-23` supplies the following application boundaries for order 750104:

- 24 VDC, 50 mA input/start/feedback circuits;
- maximum input-circuit inrush of 0.2 A for 100 ms;
- 30 ohm maximum overall cable resistance in the proposed dual-channel short-detection mode;
- monitored falling-edge start requires the input to close and then open, with a 250 ms waiting period and at least 100 ms falling-edge start pulse;
- E-stop delay-on-de-energization is 10 ms typical and 20 ms maximum;
- start/feedback-loop cross-shorts are not detected and require protected or separate installation;
- 24 V supply must be SELV/PELV with protective separation; and
- the device is for at least an IP54 control cabinet and qualified-personnel application.

Phoenix Contact current product data for item 2967060 supplies:

- 24 VDC coil, two AgNi changeover contacts;
- 5 V at 10 mA minimum switching load;
- 15 A for 300 ms maximum inrush envelope;
- 2 A at 24 V DC13 and 6 A limiting continuous current; and
- 8 ms pickup and 10 ms release as typical—not guaranteed maximum—times.

The mixed 30 ms timing sum of Phoenix typical release plus Pilz maximum input dropout is explicitly **not an acceptance bound**. Maximum KWD release/bounce, SRA1 response, contactor drop, actuator-rail decay, torque decay and mechanical stopping response remain unknown.

## Sol B-005 disposition

`PARTIALLY_ADDRESSED_OPEN`

P1.20 addresses the reviewed single-weld source-topology defect: either single KWD weld is defeated by the other SRA1 input channel opening in the modeled circuit. R233 adds a favorable paper contact/load screen.

B-005 does not have qualified closure. Both contacts welded or bypassed, a shared controller/driver stuck on, and common-route bypass remain hazardous. The design lacks accepted common-cause/dependent-failure analysis, protected physical routing, received and installed measurements, fault injection, stopping traces, functional-safety allocation and qualified validation.

## Required configuration and validation evidence

Before P1.20 could be considered for promotion, a qualified reviewer must confirm the exact PNOZ selector position and series-contact application. The proposed selector is the short-detection plus monitored falling-edge mode; it must be set with power removed, sealed and independently inspected. The project must then provide:

- received 750104 and 2967060 identity and terminal mapping;
- exact conductor route, separation, resistance allocation and installed measurement;
- measured S11/S21 voltage, current, inrush, contact drop and bounce;
- common-cause analysis covering MCU, clock, supply, PCB, driver, connector, harness and environment;
- restart-prevention and PNOZ fault-recovery traces;
- authorized single- and dual-fault injection with SRA1, K1/K2, rail, torque and stopping traces;
- PLr/SIL/Category allocation and the corresponding qualified validation; and
- formal configuration promotion plus separate work authority.

P1.15 remains current. P1.18, P1.19 and P1.20 remain unaccepted. No work authority exists.

## Controlled artifacts

- `safety/hr-v0-pnoz-kwd-application-p0.2/`
- `release/hr-v0/pnoz-kwd-application-p0.2/`
- `requirements/hr-v0-gate-evidence-supplement-r233.csv`
- `tools/generate_hr_v0_pnoz_kwd_application_p02.py`
- `tools/check_hr_v0_pnoz_kwd_application_p02.py`
