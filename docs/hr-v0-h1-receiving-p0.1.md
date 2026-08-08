# HR-V0 H1 pilot-light receiving and characterization P0.1

**PRELIMINARY - NOT APPROVED FOR PROCUREMENT, PANEL WIRING, OR ROBOT ENERGIZATION**

Document ID: `HR-V0-H1-RCV-P0.1`

Date: 2026-08-07

Electrical input: introduced by `Project Button Electrical V3-P1.5`; retained by current `Project Button Electrical V3-P1.10`

Candidate: IDEC `HW1P-1FQD-A-24V`

Evidence form: `tests/forms/hr-v0-h1-receiving-template.csv`

## Purpose

This procedure closes the gap between a current catalog identity and the physical H1 installed in the HR-V0 panel. The official IDEC USA page identifies an amber, round-flush, black-plastic-bezel pilot light with screw terminals and 24 VAC/DC illumination. It does not by itself prove the received terminal markings, orientation, internal circuit, current, brightness, legend interpretation, mounting fit, or installed behavior.

`TBD-HA` and `TBD-HB` are project placeholders only. They are not IDEC terminal markings and must not appear on a released wire instruction after received evidence identifies the actual connection points.

## Safety and authorization boundary

Receiving steps H1-001 through H1-007 are unpowered. H1-008 through H1-011 require a separately approved component-test setup, a current-limited isolated laboratory source selected by the responsible electrical reviewer, guarded terminals, an accessible source disconnect, calibrated voltage/current instruments, and a written test authorization. This procedure does not choose a current limit, fuse, test-lead rating, or source because the necessary application and facility inputs are not yet controlled.

No H1 test authorizes control-panel, actuator-source, or robot energization. H1 must remain outside any claimed safety function and has no motion authority.

H1 must never be described as "safe" or "armed".

## Unpowered receiving sequence

1. Quarantine the item under its receiving record; do not install it in a drilled panel.
2. Record supplier, purchase record, manufacturer, complete order code, package label, lot/date markings and quantity.
3. Photograph the unopened label, front operator, bezel/color, side views, complete rear, every molded or printed terminal mark, and included instructions with a scale and record ID visible.
4. Compare the received item to the current official product page and the exact catalog revision retained in the project evidence. Record every difference; do not resolve a discrepancy by assumption.
5. Measure the received front/operator diameter, panel interface, rear-body width/height/depth and maximum terminal envelope using calibrated tools. Record measurement uncertainty.
6. Transcribe terminal markings exactly as molded/printed, including orientation datum. A second reviewer compares the transcription to the photographs.
7. Obtain an identifiable manufacturer circuit/terminal diagram for the received construction or record `NOT AVAILABLE`. Do not infer polarity, bridge rectification, LED topology, suppression or internal resistance from the 24 VAC/DC rating.

## Authorized component characterization

The responsible electrical reviewer must write the source current limit, test-lead protection, voltage ramp, dwell, ambient range and acceptance bounds into the approved test record before power is applied.

8. With the lamp disconnected, independently verify source polarity, current limit, disconnect function and instrument calibration status.
9. Test the received lamp at the approved 24 VDC condition in each lead orientation. Record terminal-to-source mapping, steady current, inrush capture method/result, light output observation, case temperature and anomalies. The second orientation is a test of the received device, not permission to call either physical terminal positive or negative.
10. If 24 VAC operation is relevant to the final application, it requires a separate source, protection and authorization record; it is not needed for the current DC architecture and must not be improvised.
11. Repeat the approved DC condition at the defined minimum/maximum control-rail bounds and ambient conditions. Record current and visibility. No rail bounds are released by this document.

## Human-factors and functional checks

12. Present the proposed legend **RESET STAGE READY - DIAGNOSTIC ONLY / NO MOTION AUTHORITY** in the actual operator context. Verify that reviewers do not interpret the amber lamp as “safe,” “armed,” “motion enabled,” or permission to enter the guarded space.
13. In the later disconnected-load HIL test, verify H1 follows only `SR1_STATUS`; it must not illuminate from K1/K2 status, software command, stale compute state, or a short to another status net.
14. Record qualified electrical and human-factors dispositions. Only then may a controlled V3 revision replace `TBD-HA/TBD-HB` with received terminal identities and issue an installed-wire instruction.

## Acceptance boundary

The receiving record is acceptable only when every field is complete, photographs and raw instrument files are attached by immutable reference, discrepancies are closed, and the named reviewers sign. Passing this component procedure closes only H1 identity/terminal/application evidence. It does not close protection, conductor, enclosure, functional-safety, E2, fabrication, or energization gates.

## Primary source

IDEC USA, `HW1P-1FQD-A-24V` current product page, rechecked 2026-08-07; page identifies amber color, round flush operator, black plastic bezel, screw-terminal construction and 24 VAC/DC illumination. The page lists `HW Series Catalog_Screw` dated 2026-07-23. See the exact URL in the V3 and panel BOM records.
