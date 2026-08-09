# R116 independent review request

Status: **PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**

Review `HR-V0-PNOZ-CONF-P0.1` and the synchronized Electrical V3-P1.13 narrative for source accuracy, exact terminal/net conformance, restart behavior and fail-closed disposition. This is not a request to approve wiring, fabrication, functional safety or energization.

## Review artifacts

- `electrical/vendor/pilz/pnoz-s4-750104-r116/source-manifest-p0.1.csv`
- `electrical/vendor/pilz/pnoz-s4-750104-r116/PNOZ_s4_21396-EN-23.pdf`
- `safety/hr-v0-pnoz-path-conformance-p0.1.csv`
- `docs/hr-v0-pnoz-path-conformance-p0.1.md`
- `docs/electrical.md`
- `docs/hr-v0-electrical-v3-candidate.md`
- `electrical/kicad/project-button-v3/net-schedule.csv`
- `release/hr-v0/pnoz-path-conformance-p0.1/index.html`
- `tools/check_hr_v0_pnoz_path_conformance_p01.py`

## Questions

1. Does the controlled PDF exactly match Pilz manual edition `21396-EN-23`, and are the recorded dates clearly distinguished?
2. Do SR1 S11/S12 and S21/S22 contain only the two direct S0 NC channels, with no KWD contact in either return?
3. Does SR1 use the manual's S12-to-S34 monitored-start pattern for physical RESET?
4. Do SR1 13-14 and 23-24 separately gate SRA1 S11-S12 and S21-S22?
5. Does SRA1 use physical ARM and both K1/K2 21-22 NC mirror contacts from S12 to S34?
6. Are SRA1 13-14 and 23-24 separately routed through still-unselected FSR1/FSR2 protection to K1/K2 coils?
7. Can E-stop release, heartbeat restoration, controller reboot, a held RESET or stale command energize either contactor in the encoded topology?
8. Are the KWD switched-A1 application, physical protected routing, selector proof, protection, contactor application, total response and qualified PLr/category validation kept open?
9. Is every diagnostic output and the entire heartbeat path assigned zero functional-safety credit?
10. Could any clean checker or source match be mistaken for received-device, physical, functional-safety or energization approval?

Return BLOCKER / MAJOR / MINOR findings with exact sheet, component, terminal, net, CSV row and source-page references. State separately whether the package is ready for qualified electrical/functional-safety review and whether any wiring, fabrication or energization is authorized.
