# HR-30 native body architecture P0.1

**PRELIMINARY - CONFIGURATION AND PACKAGING CAD ONLY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, POWERED TESTING, MOTION, OR ENERGIZATION**

This is the first repository-native full-body CAD for Project Button. It freezes the `HR-PROD-030` neutral-pose datums, all 25 candidate axes, the 762 mm overall height, shell envelopes, load-frame envelopes and first component-bay reservations.

It is intentionally an architecture model, not a buildable machine. The STEP contains candidate physical envelopes plus visible module-family geometry for every axis: output shafts, standard catalogue bearing candidates, removable four-hole interface carriers, exact SHA-bound manufacturer actuator bodies, cable corridors and reduction reservations. Ten dimensioned module families cover all 25 axes, including dedicated 2.5:1 knee and ankle-pitch candidates and a shared intersecting-axis shoulder gimbal rather than overlapping generic servo blocks. Three controlled ROBOTIS source files and 25 explicit orthonormal transforms replace anonymous actuator boxes while leaving every frame, horn, fastener, cable exit, tolerance and received fit unresolved. The web GLB deliberately substitutes dimension-matched low-complexity actuator bodies for the detailed B-Reps; the exact geometry remains in both STEP assemblies and the source/transform registers. The second STEP and GLB add joint-axis and component-reservation references. The package also assigns a provisional actuator/transmission route to every axis and records explicit REUSE / ADAPT / REJECT decisions for the SHA-bound Asimov 1 source rig. Bearing dimensions, masses and catalogue ratings are now recorded from current primary manufacturer pages, but bearing application, life, suffix, fits, retention and received identity remain open. Exact fasteners, stops, encoders, actuator interfaces, wall construction, tolerances, harnesses, power hardware, mass properties, collision proof and physical validation remain open.

The revised straight arm chain is 360 mm from shoulder axis to nominal contact datum, and the bilateral fingertip span is 900 mm. Both preferred targets are met in nominal CAD. Tolerance-based swept-envelope, received-geometry and physical reach validation remain open.

## Whole-body systems completion

P0.1 now also includes floating-base 25-DOF URDF and MJCF models, a historical 9.63 kg allocation baseline now superseded by the reconciled planning inertials, power/thermal/compute/network/cost budgets, a whole-robot candidate BOM, two-hand functional requirements, staged standing/walking development, a modular build/electrification plan, and the OpenAI-to-deterministic-controller action boundary. These artifacts make the architecture coherent and simulatable; none converts the open selections or physical validation into work authority.

## Modular fabrication architecture

P0.1 now includes an editable CAD assembly that converts the visual body envelopes into a candidate central frame, paired windowed limb plates, foot carriers, hollow split torso/pelvis/head shells, removable body panels, both seventeen-part custom gripper mechanisms, and twelve segregated harness corridors. Separate neck data and actuator-power branches prevent the head actuators from borrowing the data-only corridor. The current product-envelope correction uses a 2.5 mm nominal shoulder-bridge wall, a 6 mm windowed waist bridge, 3 mm leg side plates/ties and foot carriers, and 0.8 mm thermoformed-polycarbonate or PA12 body/limb panels while retaining every joint datum and outer module interface. Local bosses, ribs, buckling, gait loads, forming/SLS qualification and impact stiffness remain open. The CAD density screen is 1.465 kg for fixed/mechanism parts and 0.279 kg for removable covers. These numbers feed the downstream mass reconciliation but remain geometry/material-assumption screens; they do not establish as-built whole-robot mass or strength. No drawing, tolerance, material, fastener, harness, structural, DFM, or work release follows.
## Whole-body mass reconciliation

The 9.63 kg allocation is no longer presented as the current dynamics mass. A reproducible reconciliation now combines 98 fabrication-CAD parts, 25 published actuator masses, 142 joint-hardware candidate parts (including catalogue bearing masses), 156 located screw candidates, 10 catalogue belt candidates and 64 located equipment/harness/contact items. The active tether-first dynamics model is 9.990 kg with neutral COM Z=0.348 m and 0.010 kg planning margin to the 10 kg hard limit. The separate onboard-envelope model is 11.455 kg and includes 1.357 kg for the rejected direct-source pack envelope, cassette and unselected protection allowance. It exceeds the product hard limit and is packaging evidence, not an installed energy configuration. Exact protection, received masses and physical properties remain open.
## Installed equipment layout

The former empty torso, pelvis, head and foot reservations now contain 64 located equipment, harness, contact, sole and installation-hardware candidates with explicit mounting planes, service directions, connector boundaries and dynamic-link placement. Their provisional as-installed planning mass is 3.722 kg. Eight bus-specific 124 x 45 mm walking-power board instances are now visibly installed in the pelvis, torso and both thighs; no board input serves more than one actuator bus or regulator output. The rear-torso model retains the former Grepow/Tattu pack envelope so the superseded packaging assumption remains visible, but that direct 4S source is rejected. Tether-first is the primary development configuration; Bioenno BLF-1209WS remains an onboard-later evaluation candidate requiring a new cassette. Battery current delivery, containment, retention, connector, charger, thermal and abuse evidence remain open.

## Located joint fastener candidates

The whole-body joint carriers now contain 156 explicit M3/M4/M5 socket-head geometry candidates across 39 plates. Every screw axis is generated from the same joint datum and carrier pattern as the body CAD. The 0.554 kg generic-steel screen is included in mass reconciliation, but exact products, threads, tapped members, torque, preload, locking, access and physical proof remain open.

## Individual manufacturing-candidate files

Every one of the 98 physical frame, removable-cover, and gripper-mechanism candidates now has its own native STEP and SVG drawing-view export in `manufacturing-files/`. Planar 2.5D candidates also expose largest-face DXF profiles; removable printed covers expose STL meshes. Material/cut, process-route, inspection-characteristic and file-provenance registers keep the parts connected to the authoritative fabrication source. These are design-refinement and supplier-discussion files, not released drawings or fabrication authority; exact materials, tolerances/GD&T, threads/inserts, print settings, DFM, FAI, structural proof and physical validation remain open.

## Serviceable joint-family CAD

Ten native reusable joint-family assemblies cover every one of the 25 axes. Each family exposes a hollow output shaft, aligned catalogue-bearing candidates, removable truss carriers, axial retainers, carrier screws, an output-encoder carrier, exact SHA-bound actuator packaging geometry, and the appropriate direct coupler, belt reduction, shoulder gimbal, or symmetric hand rack/pinion candidate. Native STEP and interactive GLB exports plus stack, part, fit/retention, and assembly registers live in `joint-family-cad/`. They are whole-body refinement artifacts, not manufacturing or work releases; exact fits, materials, products, capacity and physical proof remain open.

## Separable module CAD

The fabrication and integration-reference geometry is now exported as 12 real body modules plus an exploded whole-body STEP and interactive GLB. Each module export is derived from the same fabrication, body/joint/hand and installed-equipment sources as the integrated robot rather than from placeholder blocks. Explosion offsets are presentation transforms only. These are P0.1 separation and refinement artifacts, not released manufacturing drawings or assembly authority.

## Whole-body interface atlas

The web-first interface atlas now consolidates the actual 12 build modules, all 25 owned axes, union-envelope dimensions, current mass allocation, candidate joint mount patterns, service panels, harness corridors, adjacent-module interfaces and staged assembly dependencies. It is generated from the authoritative CAD registers and links directly to the integrated STEP/GLB. It is a P0.1 interface-control candidate; released part drawings, GD&T, material/process selections, fasteners, DFM, FAI and physical validation remain open.

## Whole-body joint-load architecture

All 25 axes now have a reproducible static load screen tied to the current URDF mass tree, the 100 g handoff payload and explicit single-support COM-offset cases. All shoulder axes and both elbows use 82 g XM430 candidates; the shoulders use 1.5:1 reductions, the wrists use XC330 candidates, the ankles use reduced XM430 candidates, and the knees use 2.5:1 reductions. Published stall values remain momentary endpoints only; continuous torque, belt capacity, thermal behavior, dynamic gait loads and physical correlation are open.

<!-- HR30-FULL-SCALE-FIT-CHECK-P01-README-START -->
## Full-scale unpowered fit-check kit

The [full-scale fit-check guide](full-scale-fit-check-p0.1/index.html) provides one source-bound, bed-normalized STL for every one of the **98 physical CAD parts** across all twelve body modules, plus twelve module ZIP bundles and candidate generic 220 x 220 x 250 mm plate layouts. Every file is 1:1, placed at Z=0 with a 5 mm X/Y margin, and retains a recorded rigid transform back to its native STEP source. Zero parts have been printed or accepted; no G-code or slicer profile is released. Printed articles may not carry robot, standing, walking, fall, powered-test or impact loads.
<!-- HR30-FULL-SCALE-FIT-CHECK-P01-README-END -->
<!-- HR30-CARRIERS-P01-START -->
## Physical actuator-interface carriers

The eight whole-body actuator buses now have **86 sourced circuit parts** across two routed native 82 × 42 mm KiCad PCB candidates. Carrier A contains four complete ISOW1432 isolated RS-485 application networks; Carrier B contains one more plus three SN74LVC1T45 TTL networks. KiCad verifies the carrier schematic at ERC 0/0 and both boards at DRC 0/0 with zero unconnected pads. Five all-copper rule areas protect the isolator moats, and the native sources bind the JLC06161H-3313 nominal 1.6 mm candidate stackup. Layer-by-layer SVGs and machine-readable DFM/fabrication candidates are published for inspection, but no output is released for ordering, assembly, connection or energization. Open `electrical/carriers-p0.1/index.html` for the routed layer guide.
<!-- HR30-CARRIERS-P01-END -->

<!-- HR30-MOTION-CONTROLLER-P01-START -->
## Deterministic motion-controller board

A routed **82 × 42 mm six-layer STM32H743ZIT6 controller candidate** now binds all eight UART groups, both carrier headers, controller power conversion, MCU supply/reset/boot/VCAP, SWD, deterministic status I/O and a structured-action SPI boundary. The corrected internal connector order is 1=GND, 2=5 V, 3=3.3 V, matching both routed carriers; PE7/PE8/PE9 are corrected to LQFP144 pins 58/59/60. Native checks are **ERC 0/0, DRC 0 and zero unconnected items**. Application review, HIL, physical verification and qualified review remain open. This is not a fabrication release or a safety controller.
<!-- HR30-MOTION-CONTROLLER-P01-END -->
<!-- HR30-PDU-P01-START -->
## Twenty-five routed actuator branch slots

Five distributed instances of one editable six-channel native KiCad PDU candidate allocate all 25 axes and retain five assembly-DNP spares. The eight-sheet schematic validates at ERC 0/0; the 124 x 45 mm ten-layer PCB validates at DRC 0/0 with zero unconnected pads. Each populated channel uses a TPS259474L circuit-breaker/latch-off eFuse with an axis-bound RILM variant, individual output pair, open-drain disable input and power-good output. This is a restrained commissioning architecture only: the device blocks reverse current, so production stackup, regeneration/clamp, connector temperature, dynamic torque, copper/thermal validation and every powered-work authority remain open. Open `electrical/actuator-branch-pdu-p0.1/index.html`.
<!-- HR30-PDU-P01-END -->

<!-- HR30-TETHER-POWER-START -->
## Physical tether power core

The P0.1 robot no longer contains an abstract high-current interruption module. RSP-500-12, PNOZ s4 750104 and two independent LC1D40ABD series contactors are located in an external 1418N4C6 panel candidate. Each contactor's three main poles are wired in series and the built-in 21-22 mirror-certified NC auxiliary participates in EDM. This corrects a candidate/interface mismatch but does not establish a Category, PL or SIL. The robot carries an SBS75G inlet and one main plus eight covered MIDI-holder positions: five individual RS walking-power-board inputs and three dedicated S18V20F9 regulator inputs. Each regulator output remains exclusive to its own TTL walking-power board. The seven-sheet native KiCad package validates at ERC 0/0 for connectivity and annotation only. All nine fuse values, final conductors, grounding, thermal behavior, stopping behavior and every work authority remain open. See `electrical/tether-power-core-p0.1/index.html`.
<!-- HR30-TETHER-POWER-END -->

## Whole-body energy and safety spine P0.1

The [interactive energy and safety guide](energy-safety-spine-p0.1/index.html) defines the tether-first whole-robot power path and a separate later onboard LiFePO4 evaluation path. The direct 14.8 V nominal 4S LiPo architecture is rejected because its nominal voltage equals the XH/XM published maximum. Three regulated 9 V TTL branches replace the unregulated 12 V assumption for the XC330 axes, and all 25 actuators now have distinct unresolved protection/telemetry boundaries.

The native KiCad topology correction is synchronized, but exact physical energy/safety terminals remain unselected. The 179 W operating and 727 W short-peak budgets are not source or wiring ratings. Protection, conductor sizing, fault current, stopping time, PE/0 V and functional-safety validation remain open. Reset can never command motion.





<!-- HR30-LEG-DRIVETRAIN-P01-README-START -->
## Reduced-leg drivetrain product geometry

The [leg-drivetrain package](leg-drivetrain-p0.1/index.html) assigns every one of the ten belt-reduced leg axes to four editable 5GT/EV5GT modules. The knees now use a distinct 16:40, 2.5:1 XH540 module with a 10 mm horn-adapter stub; the ankles retain the separate 8 mm version. MISUMI 16/20/30/40-tooth P-bore-plus-tap pulley candidates, 225/250/255 mm by 9 mm belt candidates, solved 49.359/49.965/51.456 mm pitch centers and ROBOTIS horn-family boundaries replace the former ratio-only placeholders. Capacity, material, fits, tolerances, fasteners, tensioning, guarding and physical proof remain open.
<!-- HR30-LEG-DRIVETRAIN-P01-README-END -->

<!-- HR30-LEG-ADAPTERS-P01-README-START -->
## Dimensioned leg-drive adapters

The [leg-drive adapter guide](leg-drivetrain-adapters-p0.1/index.html) adds three editable horn-to-pulley adapters and two shouldered output-shaft/capture families. Exact HN12/HN13 STEP geometry and reference-drawing patterns control the motor interface; all ten reduced axes have an adapter allocation. Nominal geometry is complete, while material, tolerances, fits, fastener details, capacity and physical proof remain open.
<!-- HR30-LEG-ADAPTERS-P01-README-END -->

<!-- HR30-HIP4-P01-README-START -->
## Bilateral 4:1 compound hip transmissions

The [hip-transmission package](hip-transmission-p0.1/index.html) installs physical two-stage 16:32 EV5GT drives on all four hip pitch/roll axes in a derived complete-body STEP/GLB. Each module includes two belts, four pulleys, a supported intermediate shaft, two carrier plates with explicit motor-tension slots, the exact actuator/horn boundary, output retention and a removable guard. Capacity and motion validation remain open.
<!-- HR30-HIP4-P01-README-END -->
<!-- HR30-INSTALLED-LEG-DRIVES-P01-README-START -->
## Product-specific leg drives installed in the whole body

The [installed drivetrain guide](leg-drivetrain-installation-p0.1/index.html) replaces ten generic pulley/belt/motor placeholders in a derived complete humanoid assembly. Exact candidate P-bore pulleys, belts, HN12/HN13 horns, shifted manufacturer actuators, project motor adapters, shouldered output shafts, capture washers and guard envelopes occupy controlled external drive planes. All 45 inter-drive pairs have zero nominal common volume. Motion sweep, material, fits, tolerances, fasteners, cable/cover clearance, capacity and physical proof remain open.
<!-- HR30-INSTALLED-LEG-DRIVES-P01-README-END -->

## Whole-body fabrication sourcing P0.1

The [interactive fabrication sourcing guide](fabrication-sourcing-p0.1/index.html) binds all 98 physical candidates to controlled upload files, exact SHA-256 values, five nonempty quote batches, seven Boston/online routes and ten mandatory written DFM questions. The public-stock screen prevents silent thickness substitution: only 0 of 45 planar candidates match the reviewed nominal stock values within 0.02 mm.

This is a route to quotation, not authority to buy or make parts. Materials, tolerances/GD&T, inspection, DFM disposition, structural capacity, FAI and physical proof remain open.

## Actual-axis joint-hardware manufacturing P0.1

The [joint-hardware manufacturing guide](joint-hardware-manufacturing-p0.1/index.html) classifies all 142 non-actuator hardware items on the 25 actual axes. It adds 64 local-coordinate shaft/carrier STEP and SVG files plus 39 carrier DXFs, while correctly withholding supplier files for 39 catalogue bearing envelopes and 39 toothless pulley/coupler placeholders.

This corrects the manufacturing-universe boundary: the 98 body/frame/hand parts were never the complete robot. Joint fits, shoulders, retention, toothed pulley products, actuator adapters, materials, tolerances, DFM, FAI and structural proof remain open.

<!-- HR30-TRANSMISSION-CLOSURE-P01-README-START -->
## Whole-body transmission closure

The [transmission closure guide](transmission-closure-p0.1/index.html) maps all 39 smooth-pulley or generic-coupler predecessor placeholders to concrete successors. Twenty leg pulleys were already superseded by installed MISUMI candidates, two gripper couplers by the detailed rack-and-pinion hands, eight shoulder pulley positions now use a 16:24 5GT / 185 mm belt candidate, and nine direct axes now use four editable flanged blind-bore split-clamp adapter families. The successor whole-body STEP/GLB also corrects the wrist vendor geometry to XC330. Material, fits, retention, capacity, DFM, FAI and physical proof remain open.
<!-- HR30-TRANSMISSION-CLOSURE-P01-README-END -->


















<!-- HR30-TRANSITION-BRACKETS-P01-README-START -->
## Actuator fixed-transition bracket CAD

The [interactive transition-bracket guide](harness/actuator-transition-brackets-p0.1/index.html) places one dimensioned three-solid service cassette at every one of the 25 actuator feeds. Editable part STEP, the standard assembly STEP/GLB, the recognizable whole-body placement STEP/GLB and all coordinates are included.

The central connector opening is a **project-owned clearance proxy**, not a released Molex cutout. A printable nine-window diagnostic coupon, print traveler and blank inspection record are included so a received connector can be checked before all 25 brackets are revised. Official-drawing reconciliation, received-part fit, production material/process selection, cable clamp qualification, body attachment, tolerance-aware collision and physical testing remain open.
<!-- HR30-TRANSITION-BRACKETS-P01-README-END -->

<!-- HR30-ACTUATOR-CABLE-COUPON-P01-README-START -->
## Actuator cable coupon and route measurement

The [interactive coupon guide](harness/actuator-cable-coupon-p0.1/index.html) defines the complete moving **CF130 -> Molex 430250200/430300001 -> panel 430200200/430310001 -> restrained Alpha 3051 -> JST EH** transition coupon. Eleven specimen families cover both crimp systems, the panel mount, strain isolation, electrical/thermal behavior and flex. The dimensioned bracket candidate and all **25 nominal placements** are configuration-bound. Direct CF130-to-JST crimping is rejected. No production cut length, bracket release, crimp setting or physical-work authority is granted.
<!-- HR30-ACTUATOR-CABLE-COUPON-P01-README-END -->





<!-- HR30-ACTUATOR-CABLE-KIT-P01-README-START -->
## Actuator cable kit

The [interactive actuator cable-kit guide](harness/actuator-cable-kit-p0.1/index.html) assigns all **25 axis feeds** their candidate current caps and planning lengths, binds JST **EHR-3/EHR-4 + SEH-001T-P0.6** candidate order-code families, and defines **159 connector-cavity records**. The dimensioned transition-bracket candidate and all **25 nominal module placements** are configuration-bound. All **8 actuator buses** now bind to the proposed `PDU_COMMON_RET` single-point reference architecture: each actuator uses its dedicated branch return, while the 17 inter-actuator links leave both GND and VDD empty to prevent a parallel motor-return path. Five RS-485 carrier channels are isolated; three TTL channels are not. The retained rejected-CF9 predecessor calculation has a largest 20 C planning drop of **0.091 V**; it is not an ampacity, logic-margin or thermal release. Every bus-reference test and physical validation gate remains open.
<!-- HR30-ACTUATOR-CABLE-KIT-P01-README-END -->
<!-- HR30-INTERAXIS-DATA-ADAPTER-P01-README-START -->
## Inter-axis data adapters

The [interactive 17-link adaptation guide](harness/interaxis-data-adapter-p0.1/index.html) binds **14 RS-485 X4P** and **3 TTL X3P** inter-actuator links to exact ROBOTIS cable-family SKUs. Each candidate removes both factory power conductors completely, leaves upstream cavities 1/2 empty, retains factory data contacts, and inserts the destination actuator's dedicated protected branch-power contacts into its combined input housing. Zero adapters have been modified, inspected, routed or communication-tested; the eight carrier-to-first-actuator harnesses remain a separate open boundary.
<!-- HR30-INTERAXIS-DATA-ADAPTER-P01-README-END -->
<!-- HR30-FIRST-ENERGIZATION-P01-README-START -->
## First-energization readiness

The [interactive first-energization guide](first-energization-readiness-p0.1/index.html) joins the existing whole-body CAD, native ECAD, harness, safety architecture and one-axis bench station into **12 objective release gates**, **8 staged power states**, a 26-item inspection traveler and 12 fault-injection cases. All physical execution and signoff fields remain open. This makes the path auditable; it does **not** authorize connection, powered testing, motion or energization.
<!-- HR30-FIRST-ENERGIZATION-P01-README-END -->
<!-- HR30-HARNESS-CURRENT-BINDING-P01-README-START -->
## Harness/current-policy reconciliation

The [harness/current-policy guide](harness/current-policy-binding-p0.1/index.html) binds all 25 individual actuator power pairs to the candidate Current Limit register values and their geometry-derived planning lengths. It separates the **71.88 A** arithmetic sum of published momentary stall endpoints from the **46.678 A** arithmetic sum of candidate internal limits. Neither number is normal RMS demand, a conductor rating, a fuse value, or permission to connect power. Conductors, protection, voltage drop, temperature rise, duty, regeneration, received connectors and physical test evidence remain open.
<!-- HR30-HARNESS-CURRENT-BINDING-P01-README-END -->
<!-- HR30-CURRENT-CONSTRAINED-P01-README-START -->
## Current-constrained whole-body actuation

The [current-constrained actuation guide](current-constrained-actuation-p0.1/index.html) binds all 25 axes to candidate Current Limit register values and an eight-bus simultaneous-cap budget. XH/XM540 axes use raw 929 (2.499 A), XM430 axes raw 743 (1.999 A), and XC330 axes raw 700 (0.700 A). A dedicated 2.5:1 knee drive replaces the former 2:1 architecture because the old knee required about 3.07 A to reach its static development screen. All numeric torque comparisons remain linear published-stall endpoint screens, not continuous capability. External current, branch protection, temperature, dynamics and physical validation remain open.
<!-- HR30-CURRENT-CONSTRAINED-P01-README-END -->

## Physical whole-body harness P0.1

The [interactive physical harness guide](harness/physical-p0.1/index.html) translates the logical ECAD into 62 route segments: 12 reserved body corridors and two moving-loop candidates at every one of the 25 joint axes. It retains all 667 current logical terminals and binds every installed equipment item without inventing unresolved conductor sizes or protection values.

All 62 route centerlines now exist as named editable STEP solids and one interactive GLB in a recognizable 762 mm body context. The display rods are centerline references only; they do not release cable OD, bundle clearance, bend radius, cut length, or retention.

The P0.1 split-harness candidate uses 25 individual positive/return power pairs and eight serial data chains. Incoming actuator housings combine the individual pair with data; outgoing inter-actuator housings populate data contacts only and leave GND/VDD cavities empty. The eight bus assembly drawings and 25 contact maps are construction candidates, not a released cable set. Protection, conductor sizing, crimp process qualification, retention, flex-life, EMC, and physical validation remain open.

Four actuator-family interfaces are now source-verified, five commercial ROBOTIS cable families are dispositioned, and five manufacturer-interface discrepancies remain explicitly open. In particular, the ROBOTIS 21 AWG statement conflicts with JST's AWG 22 contact limit, the documented housing order-code text differs, U2D2 is not the eight-segment controller, and the 10 A Power Hub is rejected for whole-body or leg power.

<!-- HR30-HEAD-HMI-HARNESS-P01-README-START -->
## Physical head HMI harness

The [interactive head HMI harness guide](harness/head-hmi-harness-p0.1/index.html) replaces generic connector notes with **8 located equipment records** and **11 routed physical links**. Both cameras now correctly use Pi 5 22-way to Camera Module 3 15-pin Standard-Mini cable candidates; the former 200 mm assumption is replaced by a 300 mm route candidate. The face display is remote rather than GPIO-stacked, and a current ReSpeaker Flex linear array/core plus two speaker candidates and a specific 5 V fan define the audio/cooling path. Exact cables, privacy controls, protection, physical fit and tests remain open.
<!-- HR30-HEAD-HMI-HARNESS-P01-README-END -->
<!-- HR30-GRIPPERS-P01-README-START -->
## Detailed bilateral hand mechanisms

The [detailed gripper package](grippers-p0.1/index.html) contains two editable 18-part symmetric rack-and-pinion assemblies. Each now uses a project-owned 20-degree, module-0.5 involute pinion and matching racks with a 0.08 mm nominal total tangential-backlash candidate. The OPEN assembly rotates its pinion 148.969 degrees for the 13 mm rack displacement. CAD-derived states provide an 8–34 mm pad gap over 26 mm total coupled stroke. Manufactured profile tolerance, fits, materials, exact actuator-horn adapter, calibration, sensing, pinch proof, endurance, DFM/FAI and physical validation remain open.
<!-- HR30-GRIPPERS-P01-README-END -->

<!-- HR30-ASSEMBLY-GUIDE-P01-START -->
## Whole-robot assembly traveler

The [interactive assembly guide](assembly-guide-p0.1/index.html) binds all 12 physical modules, 98 fabrication candidates including both detailed hand mechanisms, 25 axes, 156 located joint fasteners, 64 installed equipment items and 14 harness assemblies into a dependency-ordered unpowered traveler. It does not release materials, tolerances, hardware, torque, assembly, powered work, motion or energization.
<!-- HR30-ASSEMBLY-GUIDE-P01-END -->









## Joint-hardware successor reconciliation

The [successor reconciliation guide](joint-hardware-successor-reconciliation-p0.1/index.html) establishes one manufacturing truth for the 39 legacy pulley/coupler envelopes. All are superseded and mapped to 28 catalogue pulley positions, nine direct-adapter axes or two detailed hand mechanisms. Zero legacy envelopes remain authoritative or unmapped, but all successor selection, release and physical validation gates remain open.

<!-- HR30-AXIS-COMMISSION-START -->
## One-axis first-power station

The whole-body package now includes a removable, source-limited commissioning station rather than relying on the unreleased walking-power tree for first inspection. It uses a safety-listed Keysight E36313A candidate, ROBOTIS U2D2/Power Hub, exact X3P/X4P cable families, a native four-child-sheet KiCad design, printable tray/cover files and a 25-axis work order. Candidate first power is one mechanically restrained, whole-body-disconnected actuator at 11.0 V / 0.25 A with read-only telemetry and Torque Enable required to read zero. Qualified review, received-hardware inspection, calibration, restraint and separately signed connection/energization authority remain open. See `electrical/axis-commissioning-station-p0.1/index.html`.
<!-- HR30-AXIS-COMMISSION-END -->

<!-- BENCH-HARNESS-P01 START -->
## Commissioning bench harness

The one-axis station now includes an assembly-controlled two-wire source harness with exact manufacturer-assembled Mueller source leads, Mini-Fit polarity, sacrificial tin-dipped-tip removal, exact candidate crimp/measurement/pull/cut/strip tools, a controlled 25 +/-6 mm/min destructive-pull method, inspection traveler and as-built record. Receipt, calibration, lead/tool compatibility, physical fabrication, qualified review and every connection/powered-test/motion/energization authority remain open.
<!-- BENCH-HARNESS-P01 END -->

<!-- NO-MOTION-P01 START -->
## Guarded actuator inspection

The whole-body commissioning path now includes exact-envelope, horn-free output guards for all four candidate actuator models and a single-ID Protocol 2.0 inspector with no device-write API. Physical fit, fixture retention, software approval and all connection/powered-test/motion/energization authority remain open.
<!-- NO-MOTION-P01 END -->

<!-- HR30-NO-MOTION-FW-P01-README-START -->
## Deterministic no-motion firmware

The [HR-30 no-motion firmware guide](firmware/hr30-motion-controller-p0.1/index.html) binds all 25 axes and eight buses to a compiled `FIRST_POWER_NO_MOTION` state machine. Every torque-enable, bus-transmit, precharge and action-ready output remains zero; all motion requests are rejected and STOP is a no-op. Two clean host builds and two clean freestanding STM32H743 builds are byte-identical, and the compiled core/MMIO vector suites pass. The target is unflashed; HIL, physical timing, reset-state proof and qualified approval remain open, so this creates no powered-work or motion authority.
<!-- HR30-NO-MOTION-FW-P01-README-END -->

<!-- HR30-SWD-ADAPTER-P01-START -->
## Native SWD programming adapter

The [interactive SWD adapter guide](electrical/swd-adapter-p0.1/index.html) contains a routed **32 x 20 mm two-layer native KiCad adapter** from STLINK-V3MINIE STDC14 to controller JDBG1, plus the exact Samtec alignment-pin footprint, candidate manufacturing files, complete 14-contact disposition, five-contact service-cable drawing and inspection traveller. Native checks are ERC 0/0 and DRC 0. The board and cable remain unbuilt and all physical validation and work authority remain open.
<!-- HR30-SWD-ADAPTER-P01-END -->




<!-- HR30-WALKING-POWER-P01-README-START -->
## Bidirectional walking-power successor

The [interactive walking-power guide](electrical/walking-power-successor-p0.1/index.html) replaces the single reverse-blocking branch for walking development with a native eight-sheet KiCad candidate containing two oppositely oriented TPS259482L devices per branch. One device protects motoring current and the other protects regenerative current. All 25 axes are allocated across eight electrically separate six-channel board instances, one per authoritative actuator bus; 23 positions remain DNP. The package now carries the exact TI YWP0012A example land pattern and a routed 150 x 68 mm ten-layer board candidate with ERC 0/0, DRC 0/0 and zero unconnected pads. Eight contactor-open brake/dump circuits, exact current thresholds, production stackup, DFM, thermal proof and every powered-work authority remain open.
<!-- HR30-WALKING-POWER-P01-README-END -->
<!-- HR30-PROTECTION-CONDUCTOR-P01-README-START -->
## Staged protection and conductor architecture

The [interactive protection/conductor guide](electrical/protection-conductor-architecture-p0.1/index.html) binds the isolated 5 V logic-only path and the 12 V whole-body path into one staged hierarchy. The eight candidate axis-cap sums total 46.67779 A, above the 41.7 A source endpoint; the separate published stall endpoints total 71.88 A. These are constraints, not demand predictions or protection ratings. All fuse values, hot ampacity, regeneration handling and physical evidence remain open.
<!-- HR30-PROTECTION-CONDUCTOR-P01-README-END -->
<!-- HR30-GROUNDING-REFERENCE-P01-README-START -->
## Whole-robot grounding and DC-reference architecture

The [interactive grounding guide](electrical/grounding-reference-architecture-p0.1/index.html) consolidates facility PE, the external panel, the SBS75G first-mate tether contact, every conductive robot module, DC return, control ground, shields and grounded test equipment into one candidate topology. It proposes one removable BR1 DC-return/PE bond at RB0 and **10 controlled bond records**. Conductor hardware, limits, measurements, jurisdiction and qualified approval remain open; it grants no work authority.
<!-- HR30-GROUNDING-REFERENCE-P01-README-END -->

<!-- HR30-PROTECTIVE-BONDING-P01-README-START -->
## Physical protective-bonding implementation

The [interactive protective-bonding guide](electrical/protective-bonding-implementation-p0.1/index.html) binds the PE/reference architecture to **9 hardware records**, **13 whole-robot bond zones**, **14 articulated-joint bypass obligations**, a 16-step installation traveler and a blank 12-test inspection plan. Hammond enclosure studs, Phoenix Contact UT 10-PE, Anderson 1340G1 and an Alpha Wire 6 AWG fixed-panel family are candidate interfaces only. Fault sizing, moving-joint cable, installation, measurements, AHJ disposition and qualified release remain open.
<!-- HR30-PROTECTIVE-BONDING-P01-README-END -->

<!-- HR30-LOGIC-POWER-KIT-P01-README-START -->
## Logic-only controller power kit

The [interactive logic-power guide](electrical/logic-power-kit-p0.1/index.html) selects a SIGLENT SPD3303X, the exact two-contact JST boundary, red/black Alpha Wire conductors and Pomona banana plugs. The cable is unbuilt; voltage/current/OCP limits, DC-reference approval and every physical test remain open. It grants no connection or powered-work authority.
<!-- HR30-LOGIC-POWER-KIT-P01-README-END -->
<!-- HR30-STM32-BRINGUP-P01-README-START -->
## STM32 no-actuator bring-up

The [interactive target bring-up guide](firmware/stm32-target-bringup-p0.1/index.html) binds the reproducible STM32H743 image to the controller's exact five-contact SWD boundary and the [native routed SWD adapter candidate](electrical/swd-adapter-p0.1/index.html), plus ten release gates, twelve measurements and six fault injections. The target remains unflashed; the adapter board and cable remain unbuilt; all physical results and work authority remain open.
<!-- HR30-STM32-BRINGUP-P01-README-END -->

<!-- HR30-SRS-P01-README-START -->
## Whole-body safety requirements P0.1

The [interactive safety-requirements guide](safety-requirements-p0.1/index.html) converts the existing whole-robot stop topology, first-power firmware and restraint boundary into 24 open hazards, 12 safety/control functions, a candidate PLr allocation, 8 explicit stopping-time intervals and 20 validation cases. Achieved PL/PFHd, common-cause evidence, numerical stopping limits, physical results and qualified approval remain open. It is a reviewable SRS candidate, not permission to connect, power or move the robot.
<!-- HR30-SRS-P01-README-END -->

<!-- HR30-SFI-P01-START -->
## Safety-function implementation map

The [interactive implementation map](safety-function-implementation-p0.1/index.html) binds all 12 SRS functions to current terminals and nets or marks them absent. Only SFR-01 through SFR-03 have connected candidate circuitry, and none is validated.
<!-- HR30-SFI-P01-END -->

<!-- HR30-BOSTON-FABRICATION-ROUTE-P01-START -->
## Boston fabrication execution route P0.1

The [interactive Boston fabrication route](boston-fabrication-route-p0.1/index.html) packages a nine-part, 1:1 left-gripper fit plate and the complete 98-STL body fit check for real facilities. Eight current official facility routes are recorded. Boston Public Library printing is currently unavailable; no facility contact, quote, material selection, structural fabrication, or work authority is claimed.
<!-- HR30-BOSTON-FABRICATION-ROUTE-P01-END -->

<!-- HR30-FIRST-BUILD-CART-P01-START -->
## First physical-build cart P0.1

The [interactive first-build cart](first-build-cart-p0.1/index.html) converts the existing fit-check, cable-coupon and one-actuator commissioning packages into a deliberately small first tranche: one clearance coupon and eleven-part manually operable G01 fit article, eight sample/quote requests, borrowed or contracted specialist tooling, and two reusable ROBOTIS bench candidates totaling USD 58.77 before tax and shipping. No order, vendor contact, print, physical test, connection or energization is claimed.
<!-- HR30-FIRST-BUILD-CART-P01-END -->

<!-- HR30-FIRST-FIT-ARTICLE-P01-START -->
## First manual G01 fit article P0.1

The [interactive first-fit-article guide](first-fit-article-p0.1/index.html) packages one manually operable, unpowered G01 development fixture: eleven printable parts, open/closed STEP and GLB states, one 220 mm combined plate candidate, a clearance coupon, assembly hardware candidates, and a twelve-step physical traveler. Zero parts are built. The fixture is intentionally derived and may not receive production, actuator, structural, grasp, powered-test, motion, or energization credit.
<!-- HR30-FIRST-FIT-ARTICLE-P01-END -->

<!-- HR30-WALKING-SEQUENCE-P01-START -->
## Timed whole-body walking sequence P0.1

The [interactive walking-sequence guide](walking-sequence-p0.1/index.html) binds the active 9.990 kg tether-first URDF/MJCF to two bilateral 50 Hz minimum-jerk step candidates. Each trajectory ends with both feet nominally flat and one foot advanced 40 mm; all 25 joint positions, velocities and accelerations are exported. The data is simulator-only and carries no hardware motion or walking authority.
<!-- HR30-WALKING-SEQUENCE-P01-END -->

<!-- HR30-MUJOCO-DYNAMICS-P01-START -->
## Executed MuJoCo dynamics checkpoint

The [MuJoCo dynamics guide](mujoco-dynamics-validation-p0.1/index.html) records two complete ideal-fixture simulations of the bilateral 40 mm sequences. The corrected 9.990 kg model now compiles with positive inertia on every moving body and explicit foot/floor contacts. The fixture is numerical test equipment, not evidence of free balance, a physical fall restraint or walking authority.
<!-- HR30-MUJOCO-DYNAMICS-P01-END -->

<!-- HR30-TORQUE-DEMAND-P01-START -->
## Whole-body inverse-dynamics demand

The [interactive torque-demand guide](torque-demand-p0.1/index.html) evaluates all 23 rotary axes over both bilateral 50 Hz sequences with contact-enabled, open-chain and gravity-only inverse dynamics. It records the actual endpoint gap and produces sizing directions without releasing a transmission or claiming continuous capacity.
<!-- HR30-TORQUE-DEMAND-P01-END -->

<!-- HR30-DYNAMICS-SUCCESSOR-P01-START -->
## Hip-reduction dynamics successor

The [dynamics successor guide](dynamics-successor-p0.1/index.html) executes the unchanged bilateral gait with a preregistered 4:1 hip pitch/roll scenario and inverse-dynamics feedforward. The bounded numerical screen fails: the four revised hip axes clear, but unchanged knee and ankle saturation remains excessive. The configuration is retained as rejection evidence. It does not approve fabrication, motion or walking.
<!-- HR30-DYNAMICS-SUCCESSOR-P01-END -->

<!-- HR30-CONTROL-SUCCESSOR-P01-START -->
## Whole-body control successor

The [interactive control-successor guide](control-successor-p0.1/index.html) reruns the complete 25-axis, 9.990 kg tether model with the installed 4:1 hip candidate and unchanged gait, contacts, current ceilings and inverse feedforward. The frozen 8.0/0.8 feedback candidate clears both bounded sequences with no rotary saturation and less than one degree maximum rotary error. This corrects the earlier controller-generated knee/ankle saturation without adding distal hardware. Robustness, free balance, continuous capacity and every physical authority remain open.
<!-- HR30-CONTROL-SUCCESSOR-P01-END -->

<!-- HR30-LIGHTWEIGHT-HIP-P01-START -->
## Lightweight 4:1 hip successor

The [interactive lightweight hip guide](lightweight-hip-successor-p0.1/index.html) replaces each heavy two-stage compound hip drive with one physically modeled 15:60 EV5GT stage. Four complete single-stage packages are installed in the recognizable 762 mm humanoid, with STEP, GLB, URDF and the passing bounded-control MJCF. The mass screen now uses the complete superseded hip package boundary. Exact pulley teeth, composite material, capacity, structural proof, physical mass and every work authority remain open.
<!-- HR30-LIGHTWEIGHT-HIP-P01-END -->

<!-- HR30-DUTY-CURRENT-P01-START -->
## Harness duty-current evidence

The [whole-body harness duty-current guide](harness/duty-current-envelope-p0.1/index.html) supplies the previously missing bounded per-axis and per-bus torque-producing current envelopes from the executed control successor. It is calculation evidence only; final normal demand, wire construction, protection, thermal validation and every powered-work authority remain open.
<!-- HR30-DUTY-CURRENT-P01-END -->

<!-- HR30-DUTY-THERMAL-P01-START -->
## Whole-body harness duty/thermal screen

The [route-specific harness duty/thermal guide](harness/duty-thermal-screen-p0.1/index.html) connects both frozen walking traces to all 25 physical power-pair lengths, eight buses and six reserved power corridors. The derived loss cases define physical test obligations; they do not release conductors, contacts, protection or energization.
<!-- HR30-DUTY-THERMAL-P01-END -->

<!-- HR30-DISTRIBUTED-POWER-HARNESS-P01-START -->
## Distributed whole-body actuator power

The [distributed-power harness successor](harness/distributed-power-harness-successor-p0.1/index.html) replaces the rejected 25-jacket corridor bundle with six local protected distribution nodes and multi-core limb trunks. It binds a dedicated protected core pair to every axis and exact cable/terminal candidates. All six diameter screens pass; five bend reservations, the protection electronics, breakout ECAD, routed motion sweeps and thermal tests remain open.
<!-- HR30-DISTRIBUTED-POWER-HARNESS-P01-END -->

<!-- HR30-POWER-ROUTE-GUIDES-P01-START -->
## Routed whole-body power trunks

The [whole-body power-route guide](harness/power-route-guides-p0.1/index.html) adds actual 3D tangent centerlines to all six actuator-power trunks. The complete robot is visible with the six external guarded-spine candidates, and the editable route-only STEP preserves every source endpoint. Geometry passes the cable-radius screen; collision, guard, clamp, thermal, motion and physical validation remain open.
<!-- HR30-POWER-ROUTE-GUIDES-P01-END -->

<!-- HR30-E1-CONTROLS-FIXTURE-P01-START -->
## E1 controls-only physical fixture

The [E1 controls-only fixture](electrical/e1-controls-only-fixture-p0.1/index.html) turns the electrification plan's E1 stage into an actual 360 x 240 mm CAD assembly. It mounts the native motion controller, both four-channel carriers and SWD adapter on their real PCB hole axes, encloses all eight actuator-data field ports, and contains no actuator-power connector, conductor, PDU or actuator. The fixture and boards remain unbuilt; wiring, supply limits, received clearances, firmware/HIL and independent authorization remain open.
<!-- HR30-E1-CONTROLS-FIXTURE-P01-END -->

<!-- HR30-E1-LOGIC-HARNESS-P01-START -->
## E1 pin-for-pin logic harnesses

The E1 controls fixture now includes two placed controller-to-carrier harness candidates with 27 individually modeled conductors and four 15-position JST GH housing envelopes. Carrier A populates all 15 contacts. Carrier B populates contacts 1-12 and leaves 13-15 empty at both ends, matching the native ECAD instead of inventing three wires. Exact straight-through net maps, 320/310 mm cut-length candidates, STEP/GLB exports and a controlled construction traveler are included. The crimp process, received fit, current derating and every physical test remain open; no connection or powered-test authority follows.

<!-- HR30-E1-LOGIC-HARNESS-P01-END -->

<!-- HR30-E1-J1-POWER-CABLE-P01-START -->
## E1 J1 logic-power cable

The E1 fixture now includes the physical two-conductor J1 cable candidate alongside the controller-to-carrier harnesses. Two 1000 mm Alpha Wire 3051 conductors are bound to native contacts J1.2 `AUX_5V_SAFE` (red) and J1.1 `CTRL_GND` (black), with exact JST, Pomona, Alpha FIT and Brady material candidates. The editable STEP/GLB assembly uses project-owned dimensional connector envelopes and shows the cable at the actual J1 placement. Every assembly process, test, supply limit, grounding decision and authority remains open.

<!-- HR30-E1-J1-POWER-CABLE-P01-END -->

<!-- HR30-E1-FIXTURE-HARDWARE-P01-START -->
## E1 fixture hardware and fabrication

The controls-only fixture now has [interactive hardware CAD and readable fabrication drawings](electrical/e1-controls-only-fixture-p0.1/index.html#e1-fixture-hardware). Its 14 PCB stacks, eight cover fasteners and four full-height foot stacks are dimensioned and bound to exact candidate hardware. The covers now have real flanges and mounting holes. Fabrication, received fit, torque, adhesive/load testing, FAI and qualified acceptance remain open.
<!-- HR30-E1-FIXTURE-HARDWARE-P01-END -->

<!-- HR30-HARNESS-README-START -->
## Whole-body harness

Eight protected bus-branch candidates now map all 25 actuator drops through 12 located power/data corridors, including separate head power and data paths. Primary sources close the actuator pins, eight STM32 channel pins, five RS-485 and three TTL interface-device pinouts, and exact data-only field connector candidates. Assembled cables, branch protection, sizing, retention, flex life, termination, EMC and physical validation remain open. See [`harness/index.html`](harness/index.html).
<!-- HR30-HARNESS-README-END -->
