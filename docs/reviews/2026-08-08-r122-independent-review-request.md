# R122 independent review request

**Package:** `HR-V0-U2D2-USB-P0.1` / `HR-V0-CP-P0.6`

**Status:** **PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**

Please review R122 for engineering accuracy and completeness, not presentation polish and not permission to energize.

## Questions

1. Verify every StarTech.com `USB2AC50CM` attribute against the current official product page/datasheet, including exact Product ID, connector types, 0.5 m length, USB 2.0/480 Mbps, straight style, 3.5 mm OD, 22/30 AWG, jacket, shielding and 0 to 35 degrees C range. Identify any unsupported inference.
2. Verify that the U2D2 connector-revision statement, 6 Mbps maximum, no-actuator-power statement and reference-voltage grounding warning match the current ROBOTIS e-Manual and remain received-lot holds.
3. Check that the exact cable is physically plausible between the received Pi 5 / PI5-CASE-D and U2D2 positions without treating the unpublished minimum bend radius, connector overhang, port access or GTM3/GT3 retention as proven.
4. Review continuity, shield/common-mode, no-backfeed/power-sequencing, enumeration, waveform/jitter/error, disconnect/recovery, transient-susceptibility, EMC and local thermal test completeness.
5. Confirm that USB connect/reconnect/reset cannot create or preserve motion authority and that recovery still requires the allocated inspection/reset/ARM/fresh-command sequence.
6. Confirm that the DYNAMIXEL-side TTL harness, cable entry, PE/DC0V/shield implementation and all powered work remain unresolved and that no functional-safety credit is implied.
7. Cross-check `BOM-070`, the closure register, `PAN-034`, `BP-025`, `CE-05`, `CIH-010`, `TS-015`, receiving/test forms, energization gates, release metadata, website guide and checker for consistency.
8. Inspect the guide at desktop and narrow mobile widths for clipped content, unreadable text below 12 CSS px or misleading state presentation.

## Return format

- BLOCKER / MAJOR / MINOR findings with exact artifact, row/identifier and proposed correction.
- Every unsupported fact or missing source revision/date.
- Every missing physical/electrical/controls/EMC test input.
- A clear statement of whether the package is ready for qualified electrical/EMC/controls review. Do not mark it ready for fabrication, connection or energization.

**PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**
