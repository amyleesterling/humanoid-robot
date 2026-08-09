# HR-V0 Pi-to-U2D2 USB cable candidate P0.1

**Identifier:** `HR-V0-U2D2-USB-P0.1`

**Status:** **PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**

**Configuration:** R122 candidate correction against `HR-V0-CP-P0.6`

## Decision

`BOM-070` advances from `SELECTION REQUIRED` to an **exact candidate hold** for StarTech.com `USB2AC50CM`. This is a catalog-selection closure only. It does not authorize purchase, installation, connection, powered testing, motion or energization and earns zero functional-safety credit.

The current official StarTech datasheet identifies `USB2AC50CM` as a 0.5 m straight USB-A-to-USB-C cable supporting USB 2.0 at 480 Mbps. It publishes a 3.5 mm cable OD, 22/30 AWG construction, PVC jacket, aluminum-mylar foil with braid shielding, and a 0 to 35 degrees C operating range. The datasheet has no formal revision/date visible and says specifications may change, so received identity and physical evidence control acceptance.

## Why this candidate

- 0.5 m limits excess cable in the P0.6 segregated compute column.
- Straight ends avoid assuming an unmeasured right-angle orientation at the received Pi case or U2D2.
- Published OD and shield/conductor construction allow a real retention and routing test to be specified.
- The 480 Mbps catalog data-rate capability is above ROBOTIS' published 6 Mbps U2D2 maximum, but that is only an analytical compatibility screen. Enumeration, waveform, jitter, error, common-mode and HIL evidence remain required.

The ROBOTIS U2D2 e-Manual says the USB port changed from Micro-B to Type-C from August 2025 and that U2D2 does not supply DYNAMIXEL power. It also warns that improper reference-voltage grounding can damage U2D2. The received `902-0132-000` lot must therefore be inspected; neither connector revision nor grounding behavior is inferred.

## Controlled physical route

The cable remains in the `BP-025` / `GTM3` / `GT3` planning envelope in `HR-V0-CP-P0.6`. That envelope is not a released bend, hole or fastening pattern. StarTech publishes no minimum bend radius for this cable. A qualified reviewer must set a bend acceptance rule from received evidence, then approve pull, slip, abrasion, connector-load, vibration, service-cycle, depth and closed-cover tests.

The installed cable location must remain within its published 0 to 35 degrees C operating range under worst simultaneous panel duty and site ambient. Raspberry Pi's broader board temperature range does not override the cable's narrower published limit.

## Electrical and control holds

Before this link can be accepted:

1. Receive and inspect the exact cable, U2D2 connector revision, Raspberry Pi/case port access and retention parts.
2. Prove unpowered continuity, shield construction, route separation, connector fit and no mechanical damage.
3. Under a separately authorized E1 procedure with actuator power physically absent, prove enumeration, connection sequencing, no unexpected backfeed, common-mode behavior, signal waveform/jitter/error performance, disconnect timeout and brownout recovery.
4. Demonstrate that USB release, reconnect or reset cannot create or preserve motion authority. Recovery must remain fail-closed and require the allocated inspection/reset/ARM/fresh-command sequence.
5. Obtain qualified electrical, EMC, controls and commissioning dispositions against the exact received configuration.

The DYNAMIXEL-side TTL harness remains `SELECTION REQUIRED`. This decision does not release `CE-05`, any cable entry, gland, shield termination, DC 0 V/PE connection or actuator-current route.

## Controlled artifacts

- `electrical/vendor/startech/usb2ac50cm-r122/source-manifest-p0.1.csv`
- `electrical/interfaces/hr-v0-u2d2-usb-cable-p0.1.csv`
- `electrical/interfaces/hr-v0-u2d2-usb-cable-trade-p0.1.csv`
- `tests/forms/hr-v0-u2d2-usb-cable-receiving-template-p0.1.csv`
- `tests/forms/hr-v0-u2d2-usb-cable-test-template-p0.1.csv`
- `release/hr-v0/u2d2-usb-cable-p0.1/index.html`
- `tools/check_hr_v0_u2d2_usb_cable_p01.py`

## Primary sources

- StarTech.com, [USB2AC50CM product page](https://www.startech.com/en-us/cables/usb2ac50cm), current page, no formal revision stated, rechecked 2026-08-08.
- StarTech.com, [USB2AC50CM official datasheet](https://media.startech.com/cms/pdfs/usb2ac50cm_datasheet.pdf), current generated datasheet, no formal revision/date stated, rechecked 2026-08-08.
- ROBOTIS, [U2D2 e-Manual](https://emanual.robotis.com/docs/en/parts/interface/u2d2/), current page, no formal revision stated, rechecked 2026-08-08.
- Raspberry Pi, [Raspberry Pi 5 product brief](https://pip.raspberrypi.com/documents/RP-008348-DS-raspberry-pi-5-product-brief.pdf), `RP-008348-DS`, published April 2026, rechecked 2026-08-08.

**PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**
