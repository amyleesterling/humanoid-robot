# HR-V0 control-panel physical-definition candidate P0.4

**PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, OR ENERGIZATION**

Document ID: `HR-V0-CP-P0.4`

Date: 2026-08-07

Electrical input: `Project Button Electrical V3-P1.8`

Supersedes: `HR-V0-CP-P0.3` as the current layout candidate; P0.1 through P0.3 remain configuration history.

## Decision and defect correction

P0.1 reserve is physically insufficient. It reserved only `270 x 43 mm` for `JC1`, `FSR1`, `FSR2`, `F0`, `F1`, `F2`, `F3`, and `SD1`. The proposed Blue Sea Systems `5025` alone has a published `84.20 x 124.31 mm` body, and Phoenix Contact `PT 4-HESI (5X20)` item `3211861` has a published `55.9 mm` height before rail, end-cover, conductor-bend, or service allowance. Nothing may be squeezed into the P0.1 strip.

P0.4 retains P0.3's corrected enclosure candidate, Hammond `PJ242010RT`, and white steel inner panel `18P2117`. Hammond publishes an enclosure outside size of `610 x 508 x 257 mm` and an inner-panel size of `21 x 17 in` (`533.4 x 431.8 mm`). The enlarged nominal panel allows distinct planning envelopes for the branch fuse block, two safety-output fuse holders, the inline main-fuse holder, and a still-visible unresolved inlet/fuse-link reserve.

P0.4 retains the exact Phoenix Contact `D-ST 4`, item `3030420`, end-cover candidate for the FSR holder group and freezes Littelfuse `75920-01` as the exact `SD1` catalog candidate. The switch remains outside the released backplate geometry. `sidewall-placement.csv` records a right-side enclosure-wall option only because it can keep the actuator-current path stationary while the knob remains accessible; all cutout, rear-envelope, conductor-route, guard, legend, padlock, and application fields remain held.

This is a planar fit and accessory-identity correction, not a build release. Internal usable depth, latch/hinge geometry, cover ribs, installed cable bends, heat, duct fill, wall/bench support, rating after modification, and received fit remain open.

## Newly controlled protection hardware

- `FSR1` and `FSR2` propose two non-LED Phoenix Contact `PT 4-HESI (5X20)` item `3211861` DIN fuse-terminal holders and one `D-ST 4` item `3030420` end cover for the open side of the group. The official product records support 5 x 20 mm fuse accommodation, 6.3 A holder maximum, push-in connection, 24-10 AWG converted range, 6.2 mm holder width, and a 2.2 x 55.9 x 29 mm end-cover envelope. These are component limits, not a selected fuse or conductor.
- `F1` through `F3` retain Blue Sea Systems `5025`, now with an explicit 100 x 130 mm planning/service envelope around the published 84.20 x 124.31 mm body. Three of its six circuits are proposed; unused-circuit treatment, ring terminals, conductor bends, cover sweep, mounting, protection coordination, and thermal proof remain open.
- `F0` retains Littelfuse `FHAC0002SXJ`, now with an explicit service envelope. Its 30 A holder maximum is not a fuse value. Holder retention, 12-to-16 AWG transition, splice/termination, strain relief, temperature, and clearing evidence remain open.
- Every ampere-specific fuse link for `F0` through `F3`, `FSR1`, and `FSR2` remains **SELECTION REQUIRED**. The end-cover order code is frozen only as a candidate; received compatibility, side orientation, installed group width, touch inspection, and qualified application review remain mandatory.
- `SD1` proposes active Littelfuse order code `75920-01`: SPST, yellow knob, On/Off markings, two identical 3/8-24 studs, through-panel mounting, and an OFF-position padlock feature. Littelfuse permits high-side use. The current datasheet's published current-cycle figures depend on 4/0 cable and are not a Project Button conductor, fault-duty, or load-break rating. The source/load stud assignment, conductor/lug stack, rear touch protection, installed geometry, load-break procedure, zero-energy verification, human factors, and qualified Boston application review remain open. `SD1` is not the E-stop and receives no functional-safety credit.

Pilz operating manual `21396-EN-23` gives maximum external-contact protection limits for order `750104`; those maxima do not select the project fuse. The proposed 24 V source, contactor coils, installed conductors, prospective fault behavior, ambient/grouping, time-current curve, and qualified application review must still be coordinated.

## Controlled artifacts

- `electrical/panel/hr-v0-control-panel-p0.4/panel-bom.csv`: 25 current candidate/selection rows.
- `backplate-layout.csv`: 20 nominal planning rectangles, origin at the inner panel's top-left, x right and y down.
- `door-layout.csv`: five provisional operator/legend locations on the catalog cover-width basis.
- `sidewall-placement.csv`: one fail-closed `SD1` placement option; no coordinate or cutout.
- `terminal-allocation.csv`: proposed `XT1-01` through `XT1-06`; no bridges.
- `cable-entry-schedule.csv`: six functional zones; no hole or gland release.
- `stationary-wire-schedule.csv`: 66 V3 wire-number endpoints with every physical conductor field held `SELECTION REQUIRED`.
- `thermal-space-screen.csv`: twelve bounded screens, including the P0.1 fit defect and P0.4 protection allocations.
- `panel-layout.svg`: readable visual review drawing; CSV coordinates remain authoritative.
- `tests/forms/hr-v0-control-panel-receiving-assembly-template.csv`: twenty-two unexecuted records.
- `tests/forms/hr-v0-h1-receiving-template.csv`: fourteen unexecuted H1 records.
- `tools/check_hr_v0_control_panel.py`: fail-closed source, geometry, warning, evidence, and V3 endpoint checks.

## Layout boundary

Every P0.4 rectangle fits inside the nominal `431.8 x 533.4 mm` panel boundary. The bottom allocation is:

| Reference | Planning envelope | Current state |
|---|---:|---|
| `F1/F2/F3 BLOCK` | `100 x 130 mm` | exact 5025 candidate; no fuse values or mounting release |
| `FSR1/FSR2 HOLDERS + END COVER` | `25 x 75 mm` | two exact 3211861 holders plus one exact 3030420 end-cover candidate; fuse links/grouping open |
| `F0 HOLDER` | `30 x 130 mm` | exact FHAC0002SXJ candidate; retention/splice open |
| `JC1/F0-F3 LINKS/FSR1-FSR2 LINKS` | `127.8 x 140 mm` | selection reserve; adequacy unproved |

`SD1` is not assigned to that rectangle. Its provisional right-side-wall option has no released coordinate or hole. A door location is deliberately not preferred at this stage because it would introduce a flexible high-current door loom; this is a routing judgment, not a prohibition or a completed installation decision.

The rectangles do not prove noninterference in depth, cover operation, terminal/tool access, conductor bend radius, segregation, or thermal behavior. Received components and their manufacturer instructions must be measured before a later layout revision can release holes.

No backplate, enclosure, DIN-rail, duct, or door hole coordinate is released. No drilling is allowed from either CSV or SVG.

## Wiring, grounding, and enclosure limits

The 66 V3 wire-number endpoints remain synchronized. Conductor part number, gauge, color/insulation, measured length, end termination, route, bundling, strain relief, door-flex construction, and pull-test evidence remain `SELECTION REQUIRED`.

The fiberglass enclosure does not remove the need to bond the steel inner panel, DIN rails, applicable device metalwork, frame, and shields according to a qualified fault-path design. A project-added DC 0 V/PE star point remains prohibited. P0.4 adds no such bond and makes no completed-enclosure Type/IP claim.

H1 remains IDEC `HW1P-1FQD-A-24V`, labeled **RESET STAGE READY - DIAGNOSTIC ONLY / NO MOTION AUTHORITY**. Its `TBD-HA`/`TBD-HB` physical terminals remain unverified and it receives zero functional-safety credit.

## Closure sequence

1. Select and coordinate all six fuse links, `JC1`, conductors, terminations, glands, and bonding hardware; receive and verify the candidate end cover and exact `SD1`.
2. Receive and inspect enclosure, panel, protection hardware, operators, relays, contactors, terminals, rails, ducts, and boards.
3. Replace catalog envelopes with received dimensions, service sweeps, cable bends, and a three-dimensional depth model.
4. Complete fault-current, time-current, voltage-drop, duct-fill, heat, grounding/bonding, and enclosure-rating reviews.
5. Obtain qualified electrical, mechanical-layout, functional-safety, enclosure-system, and human-factors dispositions.
6. Issue later controlled drill/cut/wire drawings and travelers only after those reviews.
7. Fabricate only under separate written authorization, then execute 100 percent unpowered inspection and the staged commissioning gates.

## Primary manufacturer evidence

- Hammond `PJ242010RT` product page and current PJRT catalog: https://www.hammfg.com/part/PJ242010RT
- Hammond `18P2117` product page and drawing: https://www.hammfg.com/part/18P2117
- Phoenix Contact `PT 4-HESI (5X20)` item `3211861`, generated product PDF dated 2026-07-06: https://www.phoenixcontact.com/en-us/products/fuse-terminal-block-pt-4-hesi-5x20-3211861
- Phoenix Contact `D-ST 4` end cover, item `3030420`, official product page rechecked 2026-08-07: https://www.phoenixcontact.com/en-us/products/end-cover-d-st-4-3030420
- Blue Sea Systems `5025` current product page and dimensioned drawing: https://www.bluesea.com/products/5025
- Littelfuse `FHAC0002SXJ` datasheet `062923-B`: https://www.littelfuse.com/assetdocs/littelfuse-fuse-holder-ato-fhac-datasheet.pdf?assetguid=272e0b1a-a576-4173-8740-c1eb469efd79
- Littelfuse `75920-01` active product page, accessed 2026-08-07: https://www.littelfuse.com/products/switches-connectors/dc-disconnect-switches/manual-battery-disconnect-switches/75920/75920-01
- Littelfuse 75920 Series datasheet, Rev `091825` (2025): https://www.littelfuse.com/assetdocs/littelfuse-switches-75920-battery-disconnect-switches-datasheet?assetguid=5c669382-b5bb-497d-9b4d-1d9a4d9a1a03
- Littelfuse `75920-01` 2D print, current download accessed 2026-08-07: https://www.littelfuse.com/assetdocs/75920-01-2d-prints?assetguid=d9da84d1-5639-411f-85b6-fc3616c5a09e
- Littelfuse installation instruction `IF-165`, Rev `010320-C` (2020): https://www.littelfuse.com/assetdocs/75920-instruction-sheet?assetguid=367c93ee-1e28-4303-8f22-0768ddb19df1
- Pilz PNOZ s4 operating manual `21396-EN-23`: https://www.pilz.com/download/open/OM_PNOZ_s4_21396-EN-23.pdf

Manufacturer facts establish candidate identities and limits only. They do not approve this application or authorize energization.
