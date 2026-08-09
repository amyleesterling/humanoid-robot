# R117 validation record

Status: **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, TESTING, OR ENERGIZATION**

## Scope

R117 issues `HR-V0-K1K2-APP-P0.2`, a fail-closed evidence packet for the proposed K1/K2 Schneider LC1D25BD contactors. It does not select or approve the contactor application. Sol's resupplied verdict is reconciled as the existing R12 independent review and is not double-counted.

## Manufacturer-source control

Five current Schneider source identities are recorded. The current TeSys catalog `MKTED210011EN`, version 17.1 dated 2026-07-10, was retrieved as a 52,595,312-byte PDF with SHA-256 `ACE31998C5091FAAC5BD15C6BE1CC272E52501161B96D3184BDBBB64F9EA8293`. The LC1D25BD product sheet was retrieved as a 112,580-byte, seven-page PDF with SHA-256 `333EFD8170CDFADAAFBBA19CF07518E0C379380BC4BDA85D2A9355A4DB360D63`. The catalog and product sheet are identified and hash-controlled in the manifest but are not redistributed by the repository.

The official product sheet supports only the recorded product facts, including the 24 VDC coil, 5.4 W coil consumption at 20 degrees C, built-in bidirectional peak-limiting diode, one NO plus one NC auxiliary contact, mechanically linked/mirror NC contact, 5 mA at 17 V minimum signaling current, 28 ms time constant and documented opening/closing-time ranges. The source expressly leaves suitability determination to the application. No nominal product current is treated as a released electronic-load or regenerative breaking rating.

## Application and evidence controls

The controlled application register contains 33 inputs. Eighteen inputs required before the supplier query remain `NOT_MEASURED`, `OPEN` or `NOT_EXECUTED`. The characterization template contains twelve stages, all `NOT EXECUTED` and `NOT_AUTHORIZED`. The Schneider request is complete enough to expose the proposed six-pole/two-device series chain and the missing load envelope, but it remains unmistakably `UNSENT` and requires program-owner approval after the eighteen prerequisite inputs close.

The only arithmetic screens are `5.4 W / 24 V = 0.225 A` nominal coil current and `50 mA / 5 mA = 10` nominal feedback-current margin. Neither screen proves switching suitability, diagnostic coverage, safety integrity, conductor or protection sizing, stopping performance or physical behavior.

## Visual and interactive QA

Installed Google Chrome rendered the responsive guide at `1440 x 1000` and `390 x 844`. Both layouts had zero page-width overflow. Computed body/control text was 16 px, warning text 18 px, metadata 14 px and badges 12 px. Eight cards were visible in the unfiltered view; the Before supplier query filter showed exactly four cards. Desktop and mobile captures were visually inspected and were legible and unclipped.

The official LC1D25BD product sheet pages 1-3, including the application and technical-data page, were rendered and visually inspected for readable source extraction. Temporary source/render and browser-capture files were not retained as release artifacts.

## Repository and readiness validation

All **70 unique repository checker programs passed**, including the final deterministic-manifest check. Traceability resolves 81 requirements, 40 risks, 110 procedures and 57 release/walking-document procedure references. The deterministic release manifest contains **1,573 package files** before final clean-commit reproduction.

The intentional command `tools/check_energization_gates.py --through-stage E2 --require-ready` returned the expected exit code `2`. Zero gates applicable through E2 are closed. The package correctly refuses an energization-readiness claim.

Break and regenerative duty, contact voltage/current waveforms, capacitance, source response, fault current, protection, conductors, connector limits, ambient/bundling, mission profile, total stopping limits, supplier disposition, received-device evidence, physical tests, fault injection and qualified electrical/functional-safety review remain open. `EG-013` remains partial. No result authorizes ordering, wiring, fabrication, connection, testing, motion or energization.
