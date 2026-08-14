# HR-30 native body architecture P0.1

**PRELIMINARY - CONFIGURATION AND PACKAGING CAD ONLY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, POWERED TESTING, MOTION, OR ENERGIZATION**

This is the first repository-native full-body CAD for Project Button. It freezes the `HR-PROD-030` neutral-pose datums, all 25 candidate axes, the 762 mm overall height, shell envelopes, load-frame envelopes and first component-bay reservations.

It is intentionally an architecture model, not a buildable machine. The STEP contains candidate physical envelopes plus visible module-family geometry for every axis: output shafts, standard catalogue bearing candidates, removable four-hole interface carriers, exact SHA-bound manufacturer actuator bodies, cable corridors and reduction reservations. Ten dimensioned module families cover all 25 axes, including dedicated 2.0:1 knee and 2.5:1 ankle-pitch candidates and a shared intersecting-axis shoulder gimbal rather than overlapping generic servo blocks. Three controlled ROBOTIS source files and 25 explicit orthonormal transforms replace anonymous actuator boxes while leaving every frame, horn, fastener, cable exit, tolerance and received fit unresolved. The web GLB deliberately substitutes dimension-matched low-complexity actuator bodies for the detailed B-Reps; the exact geometry remains in both STEP assemblies and the source/transform registers. The second STEP and GLB add joint-axis and component-reservation references. The package also assigns a provisional actuator/transmission route to every axis and records explicit REUSE / ADAPT / REJECT decisions for the SHA-bound Asimov 1 source rig. Bearing dimensions, masses and catalogue ratings are now recorded from current primary manufacturer pages, but bearing application, life, suffix, fits, retention and received identity remain open. Exact fasteners, stops, encoders, actuator interfaces, wall construction, tolerances, harnesses, power hardware, mass properties, collision proof and physical validation remain open.

The straight arm-chain arithmetic is 370 mm reach and 950 mm span: both pass hard limits, but both miss the preferred 360/900 mm targets. This is recorded as an open design correction rather than hidden.

## Whole-body systems completion

P0.1 now also includes floating-base 25-DOF URDF and MJCF models, a historical 9.63 kg allocation baseline now superseded by the reconciled planning inertials, power/thermal/compute/network/cost budgets, a whole-robot candidate BOM, two-hand functional requirements, staged standing/walking development, a modular build/electrification plan, and the OpenAI-to-deterministic-controller action boundary. These artifacts make the architecture coherent and simulatable; none converts the open selections or physical validation into work authority.

## Modular fabrication architecture

P0.1 now includes a second editable CAD assembly that converts the visual body envelopes into a candidate central frame, paired windowed limb plates, foot carriers, hollow split torso/pelvis/head shells, removable limb and palm panels, and eleven segregated harness corridors. The current mass candidate uses 1.5 mm limb/palm/foot panels and 1.6 mm torso/pelvis/head shells; ribs, print/process qualification and impact stiffness remain open. The CAD density screen is 1.526 kg for frame parts and 0.558 kg for removable covers. These numbers feed the downstream mass reconciliation but remain geometry/material-assumption screens; neither they nor the historical 9.63 kg allocation establish whole-robot mass closure. No drawing, tolerance, material, fastener, harness, structural, DFM, or work release follows.

## Installed equipment layout

The former empty torso, pelvis, head and foot reservations now contain 56 located equipment, harness, contact, sole and installation-hardware candidates with explicit mounting planes, service directions, connector boundaries and dynamic-link placement. Their provisional as-installed planning mass is 3.380 kg. The primary whole-body candidate now includes the exact published envelope and mass of a Grepow/Tattu TAA12K4S30EC5 4S 12 Ah pack in a removable rear-torso cassette, plus a distinct protection/telemetry reservation because the pack page does not state an integrated BMS/PCM. The tether inlet remains for controlled development. Battery protection, current delivery, containment, retention, connector, charger, thermal and abuse evidence remain open.

## Whole-body mass reconciliation

The 9.63 kg allocation is no longer presented as the current dynamics mass. A reproducible reconciliation now combines 66 fabrication-CAD parts, 25 published actuator masses, 142 joint-hardware candidate parts (including catalogue bearing masses), 10 catalogue belt candidates and 56 located equipment/harness/contact items. The gross identified subtotal is 10.609 kg; the explicit per-link model plus 8% integration contingency is 11.458 kg with neutral COM Z=0.371 m. This includes the onboard pack/cassette/protection reservation and leaves 0.542 kg to the 12 kg P0.1 maximum. The 10 kg lightweight stretch objective remains open by 1.458 kg. Exact protection and received masses remain open.


## Whole-body joint-load architecture

All 25 axes now have a reproducible static load screen tied to the current URDF mass tree, the 100 g handoff payload and explicit single-support COM-offset cases. The elbows and shoulder-roll axes use 82 g XM430 candidates; the wrists use XC330 candidates; the ankles use reduced XM430 candidates; and the knees reserve 2.0:1 reductions. Published stall values remain momentary endpoints only; continuous torque, belt capacity, thermal behavior, dynamic gait loads and physical correlation are open.
