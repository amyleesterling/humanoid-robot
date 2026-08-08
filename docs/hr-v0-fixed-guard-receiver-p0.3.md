# HR-V0 fixed guard and receiver catalog-candidate package P0.3

**PRELIMINARY—DESIGN CANDIDATE ONLY. NOT APPROVED FOR PROCUREMENT, FABRICATION, MOTION, CONNECTION, OR ENERGIZATION.**

Date: 2026-08-07

Identifier: `HR-V0-GUARD-P0.3`

> **R76 retention correction:** `HR-V0-GUARD-RET-P0.1` excludes `20-2496` from the current retention baseline and confirms that the panel schedule below contains enclosure envelopes, not released finished cut dimensions or hole patterns. P0.3 remains the current frame/space basis.

> **R77 impact-allocation input:** `HR-V0-GUARD-IMPACT-P0.1` separates payload, moving-link, continued-drive, detached-hardware and static-access cases. It does not release a proof energy, panel thickness or retention system.

Supersedes: `HR-V0-GUARD-P0.2` for current guard guidance

Mechanical basis: `HR-V0-MECH-P0.6` / `HR-V0-ARM-ARCH-P0.7`

Requirements: `SAFE-004`, `SAFE-010`, `SAFE-011`, `MECH-001`

Physical protective measure: `PG-01`; no SRP/CS, PL, SIL or functional-safety credit

## Result

P0.3 retains the P0.2 400 × 900 × 950 mm internal clear-space candidate and replaces four generic product placeholders with current manufacturer catalog candidates. It also adds the five receiver pieces omitted from the earlier panel schedule, a twenty-joint schedule, and an incomplete guard mass screen.

The package remains intentionally unreleased. The exact catalog identity of a component does not prove its application, joint capacity, panel retention, impact behavior, anchoring, access prevention or suitability for this machine.

## Exact catalog candidates on hold

| Candidate | Quantity | Primary-source fact | Unresolved application evidence |
|---|---:|---|---|
| 80/20 `20-2020`, custom lengths | 16 pieces | 20 × 20 mm 20 Series, 6063-T6 aluminum, clear anodized, four open T-slots; manufacturer describes machine-guard use | written configuration, received identity/length/squareness, frame analysis, anchors and proof |
| 80/20 `14201` | 20 | 20 Series dual-support inside corner bracket; no machining required | joint orientation, access, loads, allowable, torque, fit, slip and proof |
| 80/20 `75-3581` | 40 | manufacturer-suggested two-per-`14201` M5 × 8 BHSCS/T-nut assemblies | received identity, torque, locking, reuse, witness marking and joint proof |
| Plaskolite TUFFAK GP clear, nominal 6 mm | 13 sheet envelopes; finished sizes not released | transparent UV-stabilized polycarbonate; PDS lists machine guards among applications | supplier SKU/stock, thickness tolerance, finished sizes, design values, flame disposition, edge treatment, retention, impact and proof |

The earlier 80/20 `20-2496` family screen is not an active retention candidate. Current documentation says it requires drill-through panel machining, while Plaskolite says through-fastening glazing should be used only when unavoidable and reviewed for thermal movement. See `HR-V0-GUARD-RET-P0.1` for the exact nonselected `12004` / nominal 3 mm continuous-gasket evaluation branch. Retention loads, final sheet dimensions, temperature fit, impact proof and qualified selection remain open.

## Profile-cut, sheet-envelope and joint definition

The generated package contains:

- six `20-2020` posts at 970 mm;
- four width rails at 900 mm;
- six depth rails at 400 mm;
- twenty rail-to-post joints using one proposed `14201` and two proposed `75-3581` assemblies per joint;
- eight outer transparent panel envelopes; and
- five receiver-piece envelopes, for thirteen sheet envelopes total.

All profile lengths are custom-length candidates without end machining. Saw allowance, cut tolerance, deburring, packaging damage limits and received inspection remain open. The sheet values are envelope dimensions only. No finished panel dimension or panel hole is released.

## Mass screen

80/20 publishes `0.0247 lb/in` for `20-2020`. The 11,820 mm schedule therefore gives a catalog-estimated profile mass of `5.213705 kg`.

Plaskolite PDS004 gives a typical specific gravity of `1.2`. Applying 1200 kg/m³ to the generated nominal 6 mm sheet volumes gives:

| Subset | Candidate mass |
|---|---:|
| Eight outer panels | 22.767840 kg |
| Five receiver pieces | 2.818253 kg |
| Profile plus sheet subtotal | 30.799798 kg |

This subtotal is incomplete. It excludes brackets, screws, T-nuts, panel retainers, anchors, cable-entry parts, receiver nests and any reinforcement. PDS004 expressly says its typical properties are not specification values, so the calculation is a planning screen rather than released mass evidence. Received thickness and mass must replace it.

The fixed guard mass is outside the moving-arm mass target, but it creates material handling, bench capacity, stability and anchoring loads. Those loads must be closed before assembly or installation.

## Primary documentation

- 80/20 `20-2020` product page, live page without a formal document revision, accessed 2026-08-07: https://8020.net/20-2020.html
- 80/20 `14201` product page, live page without a formal document revision, accessed 2026-08-07: https://8020.net/14201.html
- 80/20 `20-2496` product page, live page without a formal document revision, accessed 2026-08-07: https://8020.net/20-2496.html
- Plaskolite PDS004 TUFFAK GP Polycarbonate Sheet, code `122022`, accessed 2026-08-07: https://plaskolite.com/docs/default-source/pds/pds004_tuf_gp.pdf
- OSHA 29 CFR 1910.212, current electronic regulation accessed 2026-08-07: https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.212
- ISO 14120:2015 Edition 2 metadata, accessed 2026-08-07: https://www.iso.org/standard/59545.html

The 80/20 page displays the modulus string as `68.947.6 N / Sq mm`, which is malformed. P0.3 does not repair, reinterpret or use that value. Structural calculations require an unambiguous manufacturer value or accepted material evidence.

## Release holds

All twelve `GH-*` holds remain open. In addition to product receiving and structural work, closure requires the complete gripper/payload/cable swept-and-stopping envelope, selected access probe and clearance, panel-retention design, exact anchors, cable entry, impact and detached-part analysis, drop and guard tests, Boston site survey, and signed qualified reviews.

`HR-V0-GUARD-P0.3` supplies no purchase, quote acceptance, cutting, drilling, assembly, installation, motion, connection, energization or functional-safety approval.
