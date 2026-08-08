# HR-V0 gripper electrical/control interface P0.1

Status: **PRELIMINARY - ORDINARY CONTROL ONLY - NOT APPROVED FOR PROCUREMENT, FABRICATION, CONNECTION, MOTION, OR ENERGIZATION**

Identifier: `HR-V0-GRIP-ELEC-P0.1`
Date: 2026-08-08

## Architecture candidate

R112 adds a native two-sheet KiCad 10.0.5 project at `electrical/kicad/hr-v0-gripper-interface/`. It encodes seven logical blocks and the proposed protected gripper branch:

1. `POST_K1_K2_24V` enters through a connector/interface that remains `SELECTION REQUIRED`.
2. `FGRIP1` is branch protection with no released rating, value or MPN.
3. Pololu D24V22F6 item 2859 is the preferred 6 V regulator evaluation candidate. Its EN input has no external connection. Its open-drain PG output is pulled up to the Maestro 5 V logical rail through a held 10 kOhm implementation candidate.
4. Pololu Micro Maestro 6 item 1350 is the preferred ordinary controller evaluation candidate. Logic/control comes from Raspberry Pi USB; the servo rail comes from the separate regulated 6 V branch.
5. CH0 is the candidate PWM output, CH1 the green FS90-FB analog feedback input and CH2 the regulator power-good input.
6. Pololu item 3551 remains a preferred evaluation gripper only, not a selected configuration item.

The KiCad component terminals are explicitly logical functional identifiers, not physical connector pin numbers or pad positions. Connector, cable, carrier, termination and pad mapping remain `SELECTION REQUIRED`.

## Nonmoving restart behavior

The candidate requires the Maestro internal script to remain empty, run-on-startup disabled, CH0 set to `Off` on startup or error, and CH1/CH2 configured as inputs. E-stop release or manual reset may restore the downstream branch, but it shall not issue PWM. CH0 must remain Off until RESET + ARM state is validated and the supervisor issues a deliberate fresh command.

A nonzero serial timeout is required, but its exact value remains `SELECTION REQUIRED` pending the accepted total stopping-time budget. PWM endpoints, speed, acceleration, feedback correlation, USB disconnect behavior, host port/cable, received controller identity, firmware/configuration hash and HIL/fault results also remain open. No approximate endpoint is released.

The Maestro, regulator PG and feedback channel receive **zero functional-safety credit**. The physical power-removal boundary remains the dual actuator contactors, and the complete safety function still requires the safety-requirements specification, PLr/SIL allocation, common-cause analysis, stopping-time acceptance and qualified validation.

## Verification

- KiCad 10.0.5 parsed the root and child sheet.
- ERC reports `0 errors / 0 warnings`.
- The native netlist contains `POST_K1_K2_24V`, `GRIP_24V_PROTECTED`, `GRIP_6V`, `GRIP_PWM`, `GRIP_FB` and `GRIP_PG_SENSE`.
- Five manufacturer PDF/STEP payloads are controlled by byte count and SHA-256.
- The Micro Maestro STEP parses as three solids; the D24V22Fx STEP parses as one solid. Those shapes are nominal reference geometry only.

ERC verifies encoded connectivity and annotation. It does not verify physical pin order, application ratings, protection coordination, thermal/noise/EMC behavior, no-backfeed, cable voltage drop, received hardware, settings or fault response.

## Primary manufacturer records

- [Pololu Micro Maestro 6 item 1350](https://www.pololu.com/product/1350/), current product record checked 2026-08-08.
- [Maestro Servo Controller User's Guide](https://www.pololu.com/docs/pdf/0J40/maestro.pdf), copyright 2001-2022, no printed revision, 102 pages.
- [Micro Maestro dimension drawing](https://www.pololu.com/file/0J1172/micro-maestro-6-channel-usb-servo-controller-dimensions.pdf), dated 10 July 2017.
- [Pololu D24V22F6 item 2859](https://www.pololu.com/product/2859), current product record checked 2026-08-08.
- [D24V22Fx dimension drawing](https://www.pololu.com/file/0J1031/d24v22fx-step-down-voltage-regulator-dimension-diagram.pdf), dated 12 November 2015.
- [Pololu FS90-FB item 3436](https://www.pololu.com/product/3436), current product record checked 2026-08-08.

The responsive interactive guide is `release/hr-v0/gripper-interface-p0.1/index.html`. It is the primary human-readable diagram; the KiCad PDF/SVG files are diagnostic exports from the native source.
