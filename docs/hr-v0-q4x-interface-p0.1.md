# HR-V0 Q4X E2 witness interface P0.1

> **PRELIMINARY - EVALUATION CANDIDATE ONLY - NOT APPROVED FOR PROCUREMENT, FABRICATION, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION.**

Identifier: **HR-V0-Q4X-IF-P0.1**

Round: **R183**

Date: **2026-08-10**

## Decision

R183 converts the R182 Q4X displacement-witness concept into a pin-level **review candidate**, not a released connection design. The exact candidate chain is:

- Banner `Q4XFULAF110-Q8`, part `97540`;
- Banner `BC-M12F5-22-2-SF`, part `815158`, 2 m shielded five-conductor M12-female-to-flying-lead cordset;
- Banner `SMBQ4XFA`, part `91512`, Q4X pan/tilt bracket;
- Keithley `2220-30-1`, isolated channel 1 only, as the temporary instrumentation source; and
- Tektronix `TIVP02` with `TIVPMX10X` as the R182 isolated analog observation candidate.

The protection device, terminal enclosure, conductor terminations, current limit, target and final support geometry remain **SELECTION REQUIRED**. No equipment is authorized for purchase or connection.

## Non-negotiable domain boundary

The temporary Q4X instrumentation domain is separate from the robot safety and actuator domains. It must not borrow `SAFETY_24V` or `SAFETY_0V`, and it must not connect to:

- E-stop, reset, watchdog or contactor circuits;
- actuator-source positive or return;
- DXL power, data or returns; or
- protective earth or chassis unless a later qualified review explicitly selects and documents a point.

One `2220-30-1` channel is proposed because the current manufacturer record identifies independent, isolated, independently controlled outputs. This is an instrumentation convenience only. The supply, cordset, Q4X and TIVP chain receive **zero safety-function credit**. An accepted unpowered isolation/no-backfeed test remains mandatory before any future connection disposition.

## Pin-level candidate schedule

All rows below are unreleased.

| Function | Candidate route | Remaining decision |
|---|---|---|
| supply positive | `2220-30-1 CH1 +` -> protection/termination -> cord brown -> Q4X pin 1 | protection part/rating, terminals, enclosure, conductor handling and current limit |
| supply return | `2220-30-1 CH1 -` -> termination -> cord blue -> Q4X pin 3 | termination and accepted isolation evidence |
| remote input | cord white -> Q4X pin 2 -> separately insulated identified parking terminal | terminal/enclosure and locked inactive configuration; no external drive |
| analog output | cord black -> Q4X pin 4 -> `TIVPMX10X` positive | received continuity, permitted lead arrangement, range and calibration |
| analog ground | cord gray -> Q4X pin 5 -> `TIVPMX10X` negative | received continuity and domain isolation |
| shield/drain | cord shield -> labeled isolated shield terminal | termination end/location and any chassis/PE treatment; no tie may be inferred |
| remote sense | `2220-30-1` remote-sense terminals | no-connection/local-sense candidate pending received-setup verification |
| unused outputs | `2220-30-1` channel 2 and all other outputs | disabled and unconnected |

The 24.0 Vdc source setting is a controlled **candidate**, not a released setting. The exact current limit is `SELECTION REQUIRED`. Branch protection is not a safety function and cannot be selected until available fault current, conductor/terminal limits, interruption capability, inrush, site and jurisdiction inputs exist.

## Cordset and bracket dispositions

Current Banner data supports the exact `BC-M12F5-22-2-SF` cordset candidate as 2 m, shielded, five-conductor 22 AWG black PVC, with a straight five-pin M12 female connector and flying leads. Received continuity, bend/retention, route, strain relief and shield termination are not proven.

`SMBQ4XFA` is the exact pan/tilt bracket candidate. Banner's current product page and the Q4X Rev J manual disagree on the included 3/8-16 bolt length: the product page says 2 in while the manual shows 2.25 in. No correction is inferred. Exact included hardware requires **MANUFACTURER CLARIFICATION**, and the 12 mm rod, base, attachment, rigidity, tolerance, clearance and retention remain `SELECTION REQUIRED`.

Banner `BRT-Q4X-60X50` / part `95777` was screened but is **not selected** for the analog displacement witness. Its product record describes a clear-object reference target and also reports `Laser Compatible: No`. Exact target material, finish, geometry, reflectance and mounting require application confirmation and received-sensor trials.

## Controlled calibration campaign

No no-motion threshold is released. Catalog resolution, repeatability or response time cannot substitute for received-system calibration. The future campaign must, under separate authorization:

1. receive and identify the sensor, cable, bracket, supply and probe;
2. prove unpowered cable continuity and absence of unintended shorts;
3. prove isolation from robot returns, PE/chassis and other supply channels using an accepted method;
4. inspect an exact rigid target fixture across full allowed travel, occlusion and cross-axis conditions;
5. freeze and independently check the complete supply, Q4X and scope configuration;
6. apply the manufacturer's 10 minute warm-up before optimum-performance calibration;
7. collect repeated static records across selected distances, power cycles and connector re-seats;
8. repeat over accepted ambient, target-orientation and alignment-offset bounds;
9. calculate voltage-to-displacement mapping, repeatability, drift, noise and complete uncertainty; and
10. select the no-motion threshold only through qualified electrical and functional-safety review reconciled to the R181 E2 timing contract.

Two controlled sensor configurations may be screened after authorization: a timing-priority 0.3 ms base response with averaging 1, and a repeatability-priority 0.3 ms base response with averaging 16. The manufacturer manual gives 0.5 ms and 4 ms worst-case response times respectively. Neither is selected. Teach endpoints, slope, output mapping, remote-input behavior and loss-of-signal behavior also remain unresolved.

## Primary-source control

| Manufacturer | Controlled source | Revision/date | Controlled use |
|---|---|---|---|
| Banner | Q4X analog laser manual | `185624 Rev J`, 2026-03-27 | pins, colors, power, output, range, response/averaging, warm-up, bracket family |
| Banner | `Q4XFULAF110-Q8` product record | live page checked 2026-08-10 | exact sensor identity |
| Banner | `BC-M12F5-22-2-SF` product record | live page checked 2026-08-10 | exact cordset candidate |
| Banner | `SMBQ4XFA` product record | live page checked 2026-08-10 | exact bracket candidate and source discrepancy |
| Banner | `BRT-Q4X-60X50` product record | live page checked 2026-08-10 | screened target; not selected |
| Keithley/Tektronix | Series 2200 product page | live page checked 2026-08-10 | current exact supply model and channel architecture |
| Keithley/Tektronix | Series 2200 specifications | `2220S-905-01 Rev B`, December 2013 | independent isolated 0-30 V / 0-1.5 A channel ratings, accuracy and noise |

Machine-readable URLs and controlled uses are in `source-register.csv`.

## Sol R12 reconciliation

The supplied 18-BLOCKER / 30-MAJOR / 8-MINOR summary remains the same independent Sol R12 review and is not counted again. R183 addresses only a small part of the instrumentation evidence chain. It does not supply buildable mechanical drawings, released wiring, functional-safety allocation, stopping evidence, physical calibration, mass/inertia closure, continuous-duty actuator evidence or a qualified approval.

## Gate effect

- `EG-025` remains **open**;
- `EG-026` remains **partial**;
- fourteen closure holds remain open;
- physical calibration and E2 run counts remain zero;
- released connection and protection counts remain zero;
- robot-baseline change count remains zero; and
- no procurement, fabrication, connection, powered testing, motion or energization is authorized.
