# HR-V0 Electrical Selection Closure R26

> **PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**

Date: 2026-08-06  
Configuration: Electrical `V3-P0.5`

## Purpose

This bounded correction responds to Sol R12's unresolved electrical-interface and human-factors findings. It closes only facts established by current primary manufacturer evidence. It does not claim that received devices, panel layout, physical terminals, protection, conductors, enclosure, functional safety, or restart behavior have been validated.

## Exact identities frozen

| Reference | Frozen identity | Primary evidence | Still open |
|---|---|---|---|
| `S1` RESET | IDEC `HW1B-M1F10-B`, black, flush, momentary, 1NO, screw terminal | IDEC US product page; `HW Series Catalog_Screw`, dated 2026-07-23; checked 2026-08-06 | received marking, bottom-view terminal numbering, continuity, panel position, explicit legend, spacing, guarding, and human-factors review |
| `S2` ARM | IDEC `HW1B-M1F10-G`, green, flush, momentary, 1NO, screw terminal | IDEC US product page; `HW Series Catalog_Screw`, dated 2026-07-23; checked 2026-08-06 | same received/panel evidence; ARM actuation/release after every dropout must be physically tested |
| `PSU3` regional model | `Raspberry Pi 27W USB-C Power Supply US`, Type-A plug | Raspberry Pi product brief `RP-008245-DS-1`, published October 2023; portal update 2025-10-06; checked 2026-08-06 | exact family SKU and color because the official portal lists twelve SKUs without a region/color mapping; cable retention, receptacle/site review, and received test |

## Explicit non-closures

- The IDEC product pages establish configuration and color, not the project-specific physical terminal-number mapping. The schematic therefore retains `TBD-*` terminals until a received bottom-view record and continuity test are signed.
- Color difference is only one cue. `RESET` and `ARM` still need explicit legends, reviewed spacing/guarding, and an accepted panel layout.
- The Raspberry Pi source remains independent compute power with no safety authority. Freezing the US regional model does not resolve cable retention or the exact SKU.
- Fuse/holder values, conductor gauges, connector families, DC service disconnect, 24 V locking interface, watchdog converter/driver/interface, terminal blocks, enclosure, and frame/shield treatment remain `SELECTION REQUIRED` or `DESIGN REQUIRED`.
- No R26 change closes an energization gate. Physical restart, contactor, fault-injection, stopping, grounding, and qualified-review evidence remain absent.

## Evidence route

Execute `tests/forms/hr-v0-control-device-receiving-template.csv` only after the exact devices are received. Record markings, bottom-view photographs, contact identification by continuity, mechanical return, explicit legends, panel clearances, and reviewer disposition. A completed receiving record is necessary but not sufficient for fabrication or energization release.

## Sources

- IDEC `HW1B-M1F10-B`: https://www.idec.com/en-us/switches-indicator-lights/switches-pushbuttons/pushbuttons-pilot-lights/hw-22mm-heavy-duty/hw1b-m1f10-b
- IDEC `HW1B-M1F10-G`: https://www.idec.com/en-us/switches-indicator-lights/switches-pushbuttons/pushbuttons-pilot-lights/hw-22mm-heavy-duty/hw1b-m1f10-g
- Raspberry Pi Product Information Portal: https://pip-assets.raspberrypi.com/categories/898-raspberry-pi-27w-usb-c-power-supply
- Raspberry Pi product brief `RP-008245-DS-1`: https://pip-assets.raspberrypi.com/categories/898-raspberry-pi-27w-usb-c-power-supply/documents/RP-008245-DS-1-27w-usb-c-power-supply-product-brief.pdf

No part of this record authorizes ordering, wiring, fabrication, or energization.
