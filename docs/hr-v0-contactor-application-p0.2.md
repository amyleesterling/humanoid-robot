# HR-V0 K1/K2 contactor application closure P0.2

Status: **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, TESTING, OR ENERGIZATION**

Document ID: **HR-V0-K1K2-APP-P0.2**

Date: 2026-08-08

System baseline: `HR-30-SYS-R0.2`

Electrical candidate: `Project Button Electrical V3-P1.13`

Gate: `EG-013` remains **partial**

## Outcome

P0.2 turns the earlier narrative closure list into three controlled artifacts: a 33-row application-input register, a twelve-stage unexecuted characterization template, and an exact but **UNSENT** Schneider application request. It selects no contactor application, protection, conductor, fixture, limit or test authorization.

The proposed hardware identity remains two Schneider Electric `LC1D25BD` devices with 24 VDC `BD` coils. Each device's three power poles are represented in series, and K1 and K2 are then series-connected. The exact V3-P1.13 net model and terminal sequence are unchanged.

## Current manufacturer-source correction

The current controlled catalog copy is Schneider `MKTED210011EN`, version 17.1, July 2026, 52,595,312 bytes, SHA-256 `ACE31998C5091FAAC5BD15C6BE1CC272E52501161B96D3184BDBBB64F9EA8293`. Schneider's current official download record identifies the July 2026 catalog. The vendor PDF is not committed because its legal page prohibits redistribution; the exact hash, size, URL, document identity and engineering use are controlled instead.

The official `SQD-LC1D25BD.PDF` retrieved on 2026-08-08 is 112,580 bytes, SHA-256 `333EFD8170CDFADAAFBBA19CF07518E0C379380BC4BDA85D2A9355A4DB360D63`, with creation/modification metadata dated 2017-09-13. It explicitly states that the documentation is not a substitute for determining suitability for a specific application.

The product sheet supports only bounded candidate facts used here:

- 24 VDC coil; 5.4 W at 20 C, giving a nominal arithmetic screen of `5.4 / 24 = 0.225 A` per coil;
- opening time `16..24 ms` and closing time `53.55..72.45 ms` as component data;
- built-in bidirectional peak-limiting diode suppression;
- integral 1NO+1NC contacts, with the NC identified as a mirror contact and the pair mechanically linked;
- minimum signalling current 5 mA and voltage 17 V; and
- environmental, terminal and dimensional catalog values that still require received/application verification.

The Pilz PNOZ s4 manual lists 50 mA for the start/feedback circuit. The nominal arithmetic comparison is `50 mA / 5 mA = 10`. This is a useful compatibility screen for the K1/K2 NC mirror contacts in the SRA1 start/EDM loop, but it is not proof of actual loop voltage/current, contact reliability, diagnostic coverage or functional-safety performance. Physical measurement and qualified review remain mandatory.

## Why the power-contact application remains open

The actuator path is an electronic load with unknown capacitance, time constant, switching current, reverse/regenerative current and voltage transient at contact opening. The `11.1 A` value is only a sum of three published momentary actuator stall endpoints. It is not a measured contact current, normal duty, break duty or prospective fault current.

Schneider's DC tables distinguish utilization categories and load time constants. The catalog's lower-current critical-current warning is material because the present endpoint screen is below the 32 A / 24 V LC1D25 table row. Neither the `25 A` marketing shorthand nor the 32 A catalog row releases a 12 V electronic/regenerative application.

## Measurement and supplier-response sequence

1. Complete received/unpowered identity and terminal verification.
2. Execute coil-only and disconnected-main-pole timing checks under a separately authorized current-limited 24 V fixture.
3. Freeze the actual 12 V source, harness, capacitance, protection, actuator settings and representative operating envelope.
4. Measure every KAI-016 through KAI-024 quantity using synchronized external voltage/current/contact/position evidence.
5. Freeze durability, cycles/hour, ambient, enclosure, conductor and stopping-time requirements.
6. Obtain program-owner approval to send the prepared Schneider query with the completed evidence attached.
7. Archive Schneider's identifiable written response and reconcile it against the exact measured configuration.
8. Only after the response and qualified review, select or reject the contactor application and protection approach.
9. If selected, execute guarded repeated loaded interruption, failed-closed equivalent, rail-decay, residual-travel and stopping-time evidence under a separate approved work authorization.

Every powered row in `tests/forms/hr-v0-contactor-interruption-characterization-template-p0.1.csv` is `NOT EXECUTED` and `NOT_AUTHORIZED`. The template is not a test instruction until exact fixture, instruments, limits, risk controls, responsible people and authorization are accepted.

## Primary sources

- Schneider Electric, *TeSys Catalog 2026*, `MKTED210011EN`, version 17.1, July 2026: https://www.se.com/us/en/download/document/MKTED210011EN/
- Schneider Electric, *LC1D25BD Product Data Sheet*, `SQD-LC1D25BD.PDF`, dated 2017-09-13: https://iportal2.schneider-electric.com/Contents/docs/SQD-LC1D25BD.PDF
- Schneider Electric, DC-load guidance `FAQ000273244`, modified 2026-05-02: https://www.se.com/uk/en/faqs/FAQ000273244/
- Schneider Electric, mirror-contact guidance `FA126437`, modified 2026-05-12: https://www.se.com/us/en/faqs/FA126437/
- Pilz, *PNOZ s4 Operating Manual*, `21396-EN-23`: https://www.pilz.com/download/open/OM_PNOZ_s4_21396-EN-23.pdf

`EG-013` remains partial. No row in this package authorizes purchase, wiring, protection selection, fabrication, test execution, motion or energization.
