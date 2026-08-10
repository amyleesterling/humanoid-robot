# HR-V0 DC service-disconnect candidate P0.2

> **PRELIMINARY - EXACT CATALOG CANDIDATE ONLY - NOT APPROVED FOR PROCUREMENT, FABRICATION, WIRING, LOCKOUT USE, OR ENERGIZATION**

Date: 2026-08-07

Document ID: `HR-V0-SD-P0.2`

Applies to: Electrical `V3-P1.12`, reference `SD1`, positive path `ACT_12V_FUSED -> SD1 -> K1_P1_IN`

Supersedes: `HR-V0-SD-P0.1` as the current application screen. P0.1 remains configuration history.

## Decision

Littelfuse `75920-01` is frozen as the exact `SD1` **catalog candidate on hold**. It is an active SPST through-panel master disconnect with On/Off markings, a yellow knob, two identical 3/8-24 studs, and an OFF-position padlock provision. Littelfuse states that the series may be used on the high side, matching the existing positive-only schematic without interrupting the shared actuator/DC return.

This decision freezes an order code and topology, not an installed application. Conductor and lug selection, source/load stud designation, source fault envelope, operating and regenerative current, make/break duty, panel location, rear touch protection, enclosure effects, padlock access, zero-energy verification, legend, human factors, received inspection, and qualified Boston/Massachusetts review remain open. The terminals remain `TBD-IN` and `TBD-OUT` because current manufacturer documents do not designate one identical stud as source and the other as load.

`SD1` is a manual service-isolation candidate. It is not the emergency stop, receives no functional-safety credit, and may not bypass `K1`, `K2`, their monitored reset/ARM sequence, or any qualified energy-control procedure. A component-level lockout feature does not establish Project Button compliance with OSHA, NFPA 70, NFPA 79, ISO 12100, ISO 13849, IEC 62061, or any local code.

## Current manufacturer facts for the frozen candidate

The current 75920 Series datasheet, Rev `091825` (2025), identifies `75920-01` as a 70 V DC master disconnect with On/Off markings, yellow knob, SPST circuitry, through-hole mounting, 3/8-24 terminals, a 3/4-16 mounting stem, and mounting holes of nominal diameter 20.62 mm and 7.92 mm. It lists a -40 to +85 °C operating range, IPX8, high-side or low-side use, and a built-in lock-out/tag-out feature.

The datasheet's high continuous and cycle ratings depend on 105 mm² (4/0) or twin 4/0 cable. Those published figures do not authorize a smaller Project Button conductor, prove the exact lug/stud thermal stack, establish prospective-fault withstand, or define permissible loaded switching for the robot.

The exact `75920-01` drawing shows the mounting pattern and overall family envelope. The related installation instruction `IF-165`, Rev `010320-C` (2020), requires the supplied bezel, specifies a panel-thickness range of 0.81-11.43 mm, 70-90 in-lb terminal-nut torque, and a padlock arrangement in which the bezel and knob holes align in the OFF position. The older instruction states a 6-36 V range while the current datasheet states 70 V maximum. Project Button operates nominally at 12 V, within both documents, but the revision difference must remain in receiving control and the current document set supplied with the received part must govern.

The exact drawing and instruction are inputs only. No cutout is released until the received switch, enclosure wall thickness, ribs/latches, rear stud envelope, cable bends, terminal cover, padlock access, and tool clearances are measured together.

## Candidate comparison and rejection record

| Candidate | Primary-source result | Project disposition |
|---|---|---|
| Blue Sea Systems `6004200` | Single-circuit locking-key marine switch. Published 300 A rating depends on 4/0 AWG cable. Instructions say to turn loads off before OFF and not to switch OFF while an engine is running. A removable key is not the same evidence as an OFF-position personal padlock route. | **Not selected.** Retained as R63 screening history only. Fault/load-break, conductor, lockout, placement, and jurisdiction evidence did not close. |
| ABB `OTDCP25SA11M`, order `1SCA125127R1001` | IP65 enclosed 2-pole DC switch-disconnector; 25 A DC-21B at 660 V DC; red/yellow handle; official `OTDCP_11_` diagram switches negative through 1-2 and positive through 3-4. Enclosure is nominally 95 x 150 x 95 mm with M20 entries. | **Not selected for this topology.** The official two-pole diagram conflicts with the present shared/bonded-return architecture. Use of one pole was not inferred. It also does not fit the current 127.8 x 140 mm reserve and would require a new placement/topology review. |
| Littelfuse `75920-01` | Active SPST device; manufacturer permits high-side use; exact order code, 3/8-24 studs, mounting pattern, panel-thickness range, torque, and OFF-position padlock provision are documented. | **Exact catalog candidate on hold.** It matches the positive-only topology, but no application, conductor, cutout, lockout procedure, or energization release exists. |

## Provisional physical integration rule

`electrical/panel/hr-v0-control-panel-p0.4/sidewall-placement.csv` records a right enclosure side-wall option. It is a preference only: keeping the high-current conductors on a stationary surface avoids a flexible door-current loom and leaves the knob externally accessible. The location has no coordinate, cutout, or wiring release. Door, backplate, and other side-wall options remain subject to received geometry and qualified review.

The installed switch requires a rear guard or terminal cover that prevents accidental contact and shorting at both studs and lug stacks while preserving inspection, torque-tool, and conductor-bend access. Exact protection is **SELECTION REQUIRED**.

The required external legend candidate is:

`ACTUATOR DC SERVICE DISCONNECT - LOCK OFF FOR SERVICE - NOT E-STOP`

That text is not released artwork. Its wording, visibility, durability, language, color treatment, and distinction from the red E-stop require qualified human-factors and electrical-safety review.

## Application questions that must be closed

1. What is the measured GST280A12-C6P prospective-fault/current-limit/foldback envelope at `SD1`, including lead impedance and abnormal conditions?
2. What are the simultaneous actuator operating, acceleration, stall, regenerative, and bus-rise envelopes at the switch?
3. Must normal OFF occur only after `K1` and `K2` are proven open? Is any loaded or faulted interruption required, and does Littelfuse support that exact duty?
4. What exact conductor, insulation, length, ambient, bundling, lug order code, crimp tool/die, stud stack, anti-rotation control, bend radius, torque verification, strain relief, and pull-test method are released?
5. Which identical stud is controlled as source and which as load, or may the application treat the main path as bidirectional? Written manufacturer evidence is required if direction matters.
6. What rear guard/touch-protection part and enclosure modifications preserve required clearances and completed-enclosure rating?
7. Does the selected placement permit full 90-degree travel, OFF-position padlocking, label visibility, zero-energy verification, service access, and safe conductor routing?
8. What exact personal-lock/tag procedure, authorized-person control, stored-energy discharge check, and zero-energy test point apply? Component literature is not the procedure.
9. Does a qualified Massachusetts electrical/safety reviewer accept the complete installed application and applicable jurisdictional basis?

## Required receiving and validation evidence

- received part identity, current documents, date/lot code, knob/bezel/accessory completeness, and damage inspection;
- measured mounting pattern, panel thickness, front/rear envelope, stud spacing, travel, padlock hole and enclosure collision record;
- unpowered continuity in ON/OFF, source/load-direction disposition, insulation and inadvertent-contact inspection;
- released lug/stud stack, calibrated 70-90 in-lb terminal torque, witness mark, pull test and retorque policy;
- measured millivolt drop and temperature rise over the released duty envelope;
- abnormal-operation and intended switching-duty test with current/voltage waveforms and post-test inspection;
- demonstrated OFF-position personal-lock route, zero-energy verification, labeling, accessibility and human-factors acceptance;
- synchronized KiCad source, BOM, wire schedule, panel drawing, assembly traveler and commissioning procedure;
- signed qualified electrical and safety application disposition.

The controlled blank execution record remains `tests/forms/hr-v0-service-disconnect-receiving-application-template.csv`. All 15 rows remain `NOT EXECUTED`.

## Primary manufacturer evidence

- Littelfuse `75920-01` active product page, accessed 2026-08-07: https://www.littelfuse.com/products/switches-connectors/dc-disconnect-switches/manual-battery-disconnect-switches/75920/75920-01
- Littelfuse 75920 Series datasheet, Rev `091825` (2025): https://www.littelfuse.com/assetdocs/littelfuse-switches-75920-battery-disconnect-switches-datasheet?assetguid=5c669382-b5bb-497d-9b4d-1d9a4d9a1a03
- Littelfuse `75920-01` 2D print, current download accessed 2026-08-07: https://www.littelfuse.com/assetdocs/75920-01-2d-prints?assetguid=d9da84d1-5639-411f-85b6-fc3616c5a09e
- Littelfuse instruction `IF-165`, Rev `010320-C` (2020): https://www.littelfuse.com/assetdocs/75920-instruction-sheet?assetguid=367c93ee-1e28-4303-8f22-0768ddb19df1
- Blue Sea Systems `6004200` product page, accessed 2026-08-07: https://www.bluesea.com/products/6004200/Single_Circuit_ON-OFF_with_Locking_Key_-_Black
- Blue Sea Systems `6004 / 6004200` instructions, accessed 2026-08-07: https://d2pyqm2yd3fw2i.cloudfront.net/files/resources/instructions/6004_web_version.pdf
- ABB DC switch catalog `1SCC301022C0201`, June 2024: https://library.e.abb.com/public/5f9bd9221fcc416e9b503c548177226b/1SCC301022C0201_DC_switches_%20OTDC_OTM_06_2024.pdf
- ABB instruction `1SCC340027M0002`, `34OTDCP16-32` Rev F, PDF dated 2024-12-30 and ABB library date 2025-04-22: https://search.abb.com/library/Download.aspx?Action=Launch&DocumentID=1SCC340027M0002&DocumentPartId=&LanguageCode=en

Manufacturer facts establish component characteristics only. They do not approve the Project Button application, establish system lockout compliance, or authorize fabrication, wiring, or energization.
