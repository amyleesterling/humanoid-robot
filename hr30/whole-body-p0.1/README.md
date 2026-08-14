# HR-30 native body architecture P0.1

**PRELIMINARY - CONFIGURATION AND PACKAGING CAD ONLY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, POWERED TESTING, MOTION, OR ENERGIZATION**

This is the first repository-native full-body CAD for Project Button. It freezes the `HR-PROD-030` neutral-pose datums, all 25 candidate axes, the 762 mm overall height, shell envelopes, load-frame envelopes and first component-bay reservations.

It is intentionally an architecture model, not a buildable machine. The STEP contains candidate physical envelopes plus visible module-family geometry for every axis: output shafts, standard catalogue bearing candidates, removable four-hole interface carriers, exact SHA-bound manufacturer actuator bodies, cable corridors and reduction reservations. Ten dimensioned module families cover all 25 axes, including dedicated 2.0:1 knee and 2.5:1 ankle-pitch candidates and a shared intersecting-axis shoulder gimbal rather than overlapping generic servo blocks. Three controlled ROBOTIS source files and 25 explicit orthonormal transforms replace anonymous actuator boxes while leaving every frame, horn, fastener, cable exit, tolerance and received fit unresolved. The web GLB deliberately substitutes dimension-matched low-complexity actuator bodies for the detailed B-Reps; the exact geometry remains in both STEP assemblies and the source/transform registers. The second STEP and GLB add joint-axis and component-reservation references. The package also assigns a provisional actuator/transmission route to every axis and records explicit REUSE / ADAPT / REJECT decisions for the SHA-bound Asimov 1 source rig. Bearing dimensions, masses and catalogue ratings are now recorded from current primary manufacturer pages, but bearing application, life, suffix, fits, retention and received identity remain open. Exact fasteners, stops, encoders, actuator interfaces, wall construction, tolerances, harnesses, power hardware, mass properties, collision proof and physical validation remain open.

The straight arm-chain arithmetic is 370 mm reach and 950 mm span: both pass hard limits, but both miss the preferred 360/900 mm targets. This is recorded as an open design correction rather than hidden.

## Whole-body systems completion

P0.1 now also includes floating-base 25-DOF URDF and MJCF models, a historical 9.63 kg allocation baseline now superseded by the reconciled planning inertials, power/thermal/compute/network/cost budgets, a whole-robot candidate BOM, two-hand functional requirements, staged standing/walking development, a modular build/electrification plan, and the OpenAI-to-deterministic-controller action boundary. These artifacts make the architecture coherent and simulatable; none converts the open selections or physical validation into work authority.

## Modular fabrication architecture

P0.1 now includes a second editable CAD assembly that converts the visual body envelopes into a candidate central frame, paired windowed limb plates, foot carriers, hollow split torso/pelvis/head shells, removable limb and palm panels, and twelve segregated harness corridors. Separate neck data and actuator-power branches prevent the head actuators from borrowing the data-only corridor. The current mass candidate uses 1.5 mm limb/palm/foot panels and 1.6 mm torso/pelvis/head shells; ribs, print/process qualification and impact stiffness remain open. The CAD density screen is 1.526 kg for frame parts and 0.558 kg for removable covers. These numbers feed the downstream mass reconciliation but remain geometry/material-assumption screens; neither they nor the historical 9.63 kg allocation establish whole-robot mass closure. No drawing, tolerance, material, fastener, harness, structural, DFM, or work release follows.

## Whole-body mass reconciliation

The 9.63 kg allocation is no longer presented as the current dynamics mass. A reproducible reconciliation now combines 66 fabrication-CAD parts, 25 published actuator masses, 142 joint-hardware candidate parts (including catalogue bearing masses), 156 located screw candidates, 10 catalogue belt candidates and 54 located equipment/harness/contact items. The gross identified subtotal is 11.328 kg; the explicit per-link model plus 0.372 kg residual integration contingency is 11.701 kg with neutral COM Z=0.369 m. This includes the onboard pack/cassette/protection reservation and leaves 0.299 kg to the 12 kg P0.1 maximum. The 10 kg lightweight stretch objective remains open by 1.701 kg. Exact protection and received masses remain open.
## Individual manufacturing-candidate files

Every one of the 66 physical frame and removable-cover candidates now has its own native STEP and SVG drawing-view export in `manufacturing-files/`. Planar 2.5D candidates also expose largest-face DXF profiles; removable printed covers expose STL meshes. Material/cut, process-route, inspection-characteristic and file-provenance registers keep the parts connected to the authoritative fabrication source. These are design-refinement and supplier-discussion files, not released drawings or fabrication authority; exact materials, tolerances/GD&T, threads/inserts, print settings, DFM, FAI, structural proof and physical validation remain open.

## Serviceable joint-family CAD

Ten native reusable joint-family assemblies cover every one of the 25 axes. Each family exposes a hollow output shaft, aligned catalogue-bearing candidates, removable truss carriers, axial retainers, carrier screws, an output-encoder carrier, exact SHA-bound actuator packaging geometry, and the appropriate direct coupler, belt reduction, shoulder gimbal, or symmetric hand rack/pinion candidate. Native STEP and interactive GLB exports plus stack, part, fit/retention, and assembly registers live in `joint-family-cad/`. They are whole-body refinement artifacts, not manufacturing or work releases; exact fits, materials, products, capacity and physical proof remain open.

## Located joint fastener candidates

The whole-body joint carriers now contain 156 explicit M3/M4/M5 socket-head geometry candidates across 39 plates. Every screw axis is generated from the same joint datum and carrier pattern as the body CAD. The 0.554 kg generic-steel screen is included in mass reconciliation, but exact products, threads, tapped members, torque, preload, locking, access and physical proof remain open.

## Separable module CAD

The fabrication and integration-reference geometry is now exported as 12 real body modules plus an exploded whole-body STEP and interactive GLB. Each module export is derived from the same fabrication, body/joint/hand and installed-equipment sources as the integrated robot rather than from placeholder blocks. Explosion offsets are presentation transforms only. These are P0.1 separation and refinement artifacts, not released manufacturing drawings or assembly authority.

## Whole-body interface atlas

The web-first interface atlas now consolidates the actual 12 build modules, all 25 owned axes, union-envelope dimensions, current mass allocation, candidate joint mount patterns, service panels, harness corridors, adjacent-module interfaces and staged assembly dependencies. It is generated from the authoritative CAD registers and links directly to the integrated STEP/GLB. It is a P0.1 interface-control candidate; released part drawings, GD&T, material/process selections, fasteners, DFM, FAI and physical validation remain open.

## Whole-body joint-load architecture

All 25 axes now have a reproducible static load screen tied to the current URDF mass tree, the 100 g handoff payload and explicit single-support COM-offset cases. The elbows and shoulder-roll axes use 82 g XM430 candidates; the wrists use XC330 candidates; the ankles use reduced XM430 candidates; and the knees reserve 2.0:1 reductions. Published stall values remain momentary endpoints only; continuous torque, belt capacity, thermal behavior, dynamic gait loads and physical correlation are open.

## Installed equipment layout

The former empty torso, pelvis, head and foot reservations now contain 54 located equipment, harness, contact, sole and installation-hardware candidates with explicit mounting planes, service directions, connector boundaries and dynamic-link placement. Their provisional as-installed planning mass is 3.442 kg. The primary whole-body candidate now includes the exact published envelope and mass of a Grepow/Tattu TAA12K4S30EC5 4S 12 Ah pack in a removable rear-torso cassette, plus a distinct protection/telemetry reservation because the pack page does not state an integrated BMS/PCM. The tether inlet remains for controlled development. Battery protection, current delivery, containment, retention, connector, charger, thermal and abuse evidence remain open.







<!-- HR30-HARNESS-README-START -->
## Whole-body harness

Eight protected bus-branch candidates now map all 25 actuator drops through 12 located power/data corridors, including separate head power and data paths. Primary sources close the actuator pins, eight STM32 channel pins, five RS-485 and three TTL interface-device pinouts, and exact data-only field connector candidates. Assembled cables, branch protection, sizing, retention, flex life, termination, EMC and physical validation remain open. See [`harness/index.html`](harness/index.html).
<!-- HR30-HARNESS-README-END -->
<!-- HR30-CARRIERS-P01-START -->
## Physical actuator-interface carriers

The eight whole-body actuator buses now have **86 sourced circuit parts** across two native 82 × 42 mm KiCad PCB placement candidates. Carrier A contains four complete ISOW1432 isolated RS-485 application networks; Carrier B contains one more plus three SN74LVC1T45 TTL networks. The carrier schematic hierarchy passes KiCad ERC with 0 errors and 0 warnings. Both board placements have zero non-connectivity DRC violations. Copper is deliberately unrouted: KiCad reports 140 Carrier A and 89 Carrier B unconnected pads. The rejected automatic route is not retained, and no Gerber or drill package is published. Open `electrical/carriers-p0.1/index.html` for the front/back board guide.
<!-- HR30-CARRIERS-P01-END -->
