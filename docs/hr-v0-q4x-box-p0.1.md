# HR-V0 Q4X temporary interface-box candidate P0.1

> **PRELIMINARY - BENCH R&D CANDIDATE ONLY - NOT APPROVED FOR PROCUREMENT, FABRICATION, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Artifact: **HR-V0-Q4X-BOX-P0.1**

Round: **R184**

Date: **2026-08-10**

## Outcome

R184 converts the R183 Q4X protection/termination placeholder into a connected, native KiCad candidate with exact branch protection, terminals, ferrules, crimp tool, fiberglass enclosure, fiberglass panel, DIN rail, glands, lock nuts and cable designation. It remains a review candidate, not a build or connection release.

The temporary Q4X system remains a separately powered 24 V instrumentation domain. It has no intentional connection to robot safety 24 V/0 V, PE, contactor, watchdog, reset, actuator or DYNAMIXEL circuits and receives zero safety credit.

## Protection conclusion

The exact candidate is Phoenix Contact `PTCB E1 24DC/0.1A NO`, item `1464484`. The Q4X catalog upper-bound screen at 24.0 V is 28.125 mA; adding the PTCB's typical 5 mA closed-circuit current gives 33.125 mA before inrush. The resulting 3.019 ratio to 0.1 A is only a nominal steady-state screen. It is not an inrush margin or safety factor.

Phoenix publishes typical active limiting of 1.2 times nominal, not a guaranteed hard fault-current ceiling. R184 therefore does not claim a 0.12 A maximum. The Keithley channel's 1.5 A catalog maximum is below the PTCB's 300 A short-circuit switching capacity, so the manufacturer's catalog condition for an upstream backup fuse is not triggered. No fuse value is released, and source-current setting, overload, short, backfeed and abnormal-condition tests remain mandatory.

## Ground and shield rule

The nonconductive enclosure and inner panel contain an isolated metal DIN rail. No PE conductor enters this candidate box. The Banner cordset drain lands only on `XQ1.6`, an ordinary insulated terminal labeled `SHIELD PARK - NO PE/0V CONNECTION`; there is no bridge or shield clamp. Q4X pin 5 analog ground is not project-bonded to pin 3 DC common. These are proposals pending Boston site and qualified electrical review, not generalized grounding rules.

## Native electrical source

- root plus two connected child sheets: `electrical/kicad/hr-v0-q4x-box-p0.1/`;
- sheet 01: source cable, return distribution and exact 0.1 A protection;
- sheet 02: exact sensor pins, remote-input park, analog pair, drain park and unresolved isolated test fixture;
- KiCad ERC and exported SVGs: `electrical/kicad/hr-v0-q4x-box-p0.1/validation/` and `output/`; and
- synchronized BOM, net, connector and wire schedules in the same directory.

## Still blocking physical work

All fourteen `QBH-*` holds remain open. The most immediate are the exact source-cable procurement form and length, dimensioned gland-hole/rail coordinates, received identities, current-limit setting, terminal/crimp trials, unpowered isolation, closed-box thermal behavior, exact guarded analog test fixture, Boston site/jurisdiction review and separate work authorization.

R184 changes neither the robot electrical baseline nor Sol R12's verdict. `EG-025` remains open, `EG-026` remains partial, and no Sol blocker closes.

## Primary sources

The complete current-source register is `test-equipment/hr-v0/q4x-box-p0.1/source-register.csv`. Manufacturer component ratings do not transfer automatically to the completed drilled and wired assembly.
