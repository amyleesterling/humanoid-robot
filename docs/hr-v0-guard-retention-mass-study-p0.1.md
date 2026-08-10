# HR-V0 guard retention and mass study P0.1

**PRELIMINARY—EVALUATION STUDY ONLY. NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, MOTION, CONNECTION, OR ENERGIZATION.**

Date: 2026-08-07

Identifier: `HR-V0-GUARD-RET-P0.1`

Parent: `HR-V0-GUARD-P0.3`

Requirements: `SAFE-004`, `SAFE-010`, `SAFE-011`

Risks: `R-001`, `R-002`, `R-003`, `R-006`, `R-022`

## Correction

P0.3 identified 80/20 `20-2496` as a panel-retainer family candidate. Current primary documentation shows that it requires drill-through machining on the panel. Plaskolite's TUFFAK fabrication guide says through-fastening glazing should be used only when unavoidable, that the design must accommodate thermal movement, and that all sheet edges should be engaged in the frame.

`20-2496` is therefore excluded from the current retention baseline. It remains catalog-screening history, not a machine retainer candidate. The P0.3 panel dimensions are enclosure envelopes, not released finished cut dimensions or hole patterns.

## Exact evaluation branch

The exact nonselected evaluation branch is:

- Plaskolite TUFFAK GP clear, nominal 3 mm, for the eight outer panels only;
- 80/20 `12004` polypropylene reduction T-slot cover used as a continuous panel gasket on all four edges;
- the P0.3 nominal 6 mm receiver retained unchanged; and
- the P0.3 `20-2020` frame retained unchanged.

80/20 publishes `12004` as a 2 m 20-Series product that can be used as a panel gasket for 1–4 mm panels. The page publishes no retention load, impact capacity, installed compression or project allowable. Exact identity and thickness compatibility do not establish suitability.

The generated edge schedule contains 32 pieces totaling 20,980 mm. A deterministic stock-packing screen uses eleven 2 m lengths with 1,020 mm nominal offcut before saw kerf. This is not a purchase or cut list: received length, kerf, installation allowance and final panel dimensions remain open.

## Mass result

The current P0.3 profile-and-sheet subtotal is 30.799798 kg. The hybrid evaluation branch gives:

| Subset | Planning mass |
|---|---:|
| `20-2020` profile schedule | 5.213705 kg |
| Eight nominal 3 mm outer panels | 11.383920 kg |
| Five nominal 6 mm receiver pieces | 2.818253 kg |
| Known subtotal | 19.415878 kg |
| Reduction from P0.3 | 11.383920 kg |

This is a 36.96% reduction in the known subtotal. It excludes gasket, brackets, screws, T-nuts, anchors, receiver nests, cable entry and reinforcement. The density basis remains Plaskolite's typical value and is not released material evidence.

No thinner panel is selected. The branch cannot supersede P0.3 until the complete credible impact-energy/direction envelope, retention loads, frame and joint response, temperature range, physical tests and qualified disposition close.

R77 `HR-V0-GUARD-IMPACT-P0.1` now supplies the bounded arithmetic and hazard-to-test allocation input. It leaves powered-contact, detached-item and static-load values open, so this selection hold remains unchanged.

## Thermal and fit boundary

The Plaskolite guide gives a general expansion/contraction allowance of 1.52 mm per foot in both sheet directions. Applied only as a planning screen, that is approximately:

- 4.837 mm across a 970 mm dimension;
- 2.418 mm across a 485 mm dimension; and
- 2.194 mm across a 440 mm dimension.

These values are not final gaps. The exact temperature range, install temperature, slot geometry, gasket engagement/compression, panel tolerance and required retained edge depth are unresolved. Finished panel dimensions must not be released from the current envelope schedule.

## Evidence required before selection

1. Accepted maximum credible impact-energy and direction allocation covering the foam payload, gripper/tool, fasteners, cable whip and relevant runaway/detachment cases.
2. Exact manufacturer CAD or received metrology for `20-2020`, `12004` and sheet thickness/tolerance.
3. Accepted four-edge engagement, corner, service-removal and thermal-movement design.
4. Written 80/20 application guidance or a qualified calculation for gasket retention and frame load transfer.
5. Exact full-size or representative fixture and a released impact/push-out procedure using the production-equivalent panel, edge finish, gasket, frame, joint spacing and supports.
6. Recorded pre/post dimensions, residual engagement, fastener movement, cracking, tearing, permanent set and frame/joint damage.
7. Receiver deflection, rebound and drop-test closure with the 6 mm receiver branch.
8. Qualified mechanical and safety review of the frozen configuration and test evidence.

Passing an unpowered fit mock-up does not close impact containment. Passing one impact direction does not release untested directions or energies.

## Primary sources

- 80/20 `20-2496` product page, live page without formal revision, accessed 2026-08-07: https://8020.net/20-2496.html
- 80/20 `12004` product page, live page without formal revision, accessed 2026-08-07: https://8020.net/12004.html
- Plaskolite TUFFAK fabrication guide `FAB015`, current 68-page guide without printed revision, accessed 2026-08-07: https://plaskolite.com/docs/default-source/fab/fab015_tuf_en.pdf
- Plaskolite TUFFAK GP PDS004, code `122022`, accessed 2026-08-07: https://plaskolite.com/docs/default-source/pds/pds004_tuf_gp.pdf
- 80/20 `20-2020` product page, live page without formal revision, accessed 2026-08-07: https://8020.net/20-2020.html

The generated interactive guide and machine-readable schedules are under `cad/hr-v0/guard-retention-study-p0.1/`. They provide evaluation inputs only and create no authorization.
