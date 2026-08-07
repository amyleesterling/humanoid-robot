# Actuator and Harness Interface Constraints

**PRELIMINARY—NOT APPROVED FOR FABRICATION OR ENERGIZATION**

## DYNAMIXEL power and data boundary

ROBOTIS identifies standard X-series connector pin 2 as `VDD`; it is not documented as an externally driven sense-only input. This applies to the standard TTL and RS-485 connector definitions. Therefore, independently protected actuator branches shall not be joined through ordinary full-pin daisy-chain or interface cables.

The released harness must use a reviewed power-isolating topology that preserves the required data and reference conductors while preventing any branch or interface supply from backfeeding another. Before connection to actuators, every manufactured harness requires pin-to-pin continuity, insulation, polarity, branch-isolation, and powered no-backfeed tests. `VDD_SENSE` is prohibited as a pin-2 label unless ROBOTIS provides applicable written evidence for the exact interface.

Electrical V3-P1.4 implements the proposed topology as one central `DXL-STAR-P0.1` board. `JC1` carries only GND on pin 1 and DATA on pin 3; its pin 2 has no net or copper and both mating cable cavities must be empty. `JP1`-`JP3` accept three separately protected positive branches plus common return. `JA1`-`JA3` each carry common GND/data and only their respective positive branch. See `docs/hr-v0-dxl-star-injection-p0.1.md` and the native project at `electrical/kicad/hr-v0-dxl-star/`. The board is routed and ERC/DRC-clean, but it is not released: cable construction, EH current conflict, protection, thermal, signal-integrity, no-backfeed, fabrication and received evidence remain open.

`HR-V0-ACT-P0.1` proposes raw internal-current limits of 800 for J1/J2 and 300 for the gripper solely for guarded characterization. The XM540 value corresponds nominally to 2.152 A using ROBOTIS's approximate 2.69 mA/raw scale. It does not prove that external branch supply current remains below the JST EH 3 A series rating. The received harness also needs resolution of ROBOTIS's stated 21 AWG DYNAMIXEL wire against JST's published AWG 22 maximum for the EH contact family. See `docs/hr-v0-actuator-current-envelope-p0.1.md`.

## U2D2 and Power Hub

U2D2 is a communications interface, not the robot’s summed-current distribution element. The official U2D2 Power Hub documentation states 3.5–24.0 V and 10.0 A maximum and says to use only one power input. It is restricted to development configurations whose measured total current remains within the documented limit and whose custom harness prevents parallel branch power. The full robot requires separately protected distribution selected from measured load and fault-current evidence.

## Connector release requirements

Exact connector housing and contact manufacturer part numbers, mating face and cable-end views, pin numbering, conductor gauge/insulation, crimp tooling, pull force, current/temperature derating, mating cycles, keying, strain relief, shielding, and service labeling remain `SELECTION REQUIRED`. A family photo or approximate connector-current statement is not a released pinout or rating.

## Emergency-stop interface

The IDEC XW family supports candidate dual-NC direct-opening configurations, but `S0` and `SH0` remain `SELECTION REQUIRED`. Freeze the complete order code, contact blocks, operator reset action, terminal numbering, and bottom-view orientation from current official documentation before replacing any `TBD-*` identifier. Verify the received device and both positively opening NC channels before panel wiring.

Primary sources were checked 2026-08-05 through 2026-08-07: [ROBOTIS X-series connector definitions](https://emanual.robotis.com/docs/en/dxl/x/), [U2D2](https://emanual.robotis.com/docs/en/parts/interface/u2d2/), [U2D2 Power Hub](https://emanual.robotis.com/docs/en/parts/interface/u2d2_power_hub/), [JST EH](https://www.jst-mfg.com/product/index.php?lang=2&series=58), [JST VH](https://www.jst-mfg.com/product/pdf/eng/eVH.pdf), and the [IDEC XW candidate family page](https://www.idec.com/en-us/switches-indicator-lights/switches-pushbuttons/emergency-stop-switches/xw-22mm-estop/xw1e-bv402m-r). Live pages without a displayed document revision are access-dated and must be rechecked at release.
