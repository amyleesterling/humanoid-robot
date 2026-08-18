# HR-30 E1 controls-only fixture P0.1

**PRELIMINARY - UNBUILT CONTROLS-ONLY FIXTURE CANDIDATE - NOT APPROVED FOR CONNECTION, POWERED TESTING, MOTION, WALKING, OR ENERGIZATION**

This is the missing physical artifact for the whole-body electrification plan's E1 stage. The 360 x 240 mm bench fixture carries the native motion-controller, carrier A, carrier B and SWD-adapter board candidates. Fourteen native mounting-hole axes are retained. Each carrier is enclosed by a screw-retained cover with no external opening; its controller cable enters through the panel from below. All eight actuator-data field ports are inaccessible, and the fixture contains no actuator-power connector, PDU, conductor or actuator.

The fixture is an editable/generated CAD candidate, not a built or approved test station. The native PCB STEP exports disclose missing connector models, exact hardware/material selections remain open, and the logic wiring has not been built or inspected. No hardware may be connected or powered from this package.

<!-- HR30-E1-LOGIC-HARNESS-P01-START -->
## Pin-for-pin E1 logic harness candidates

The fixture now includes two physical controller-to-carrier harness candidates rather than an undefined 15-circuit note. E1-HA-A populates all 15 positions; E1-HA-B populates positions 1-12 and deliberately leaves 13-15 empty at both ends. The package contains 27 individually modeled wires, four GHR-15V-S housing envelopes, exact straight-through net maps, 320/310 mm cut-length candidates, construction records, STEP/GLB exports and an integrated fixture-with-harness assembly.

Belden 1852 28 AWG stranded tinned-copper wire is the exact wire candidate because its published 0.89 mm nominal insulation diameter is inside JST's 0.76-1.0 mm SSHL-002T-P0.2 range. No hand crimp is released; the only manufacturer-listed route recorded here is the JST machine/applicator path, to be executed by a controlled harness supplier after process qualification. The harnesses remain unbuilt and cannot be connected or powered.

<!-- HR30-E1-LOGIC-HARNESS-P01-END -->

<!-- HR30-E1-J1-POWER-CABLE-P01-START -->
## J1 logic-power cable candidate

The native motion-controller J1 boundary now has a physical cable assembly candidate: two 1000 mm Alpha Wire 3051 conductors, a JST VHR-2N housing with SVH-21T-P1.1 contacts, red/black Pomona 5934 source plugs, FIT-KIT-221BK sleeving and Brady M21-11-427 labels. J1.2 is red `AUX_5V_SAFE`; J1.1 is black `CTRL_GND`. The connector and plug shapes are project-owned dimensional envelopes from public drawings, not redistributed manufacturer CAD.

Manufacturing and placed STEP/GLB files, a native-J1 route, contact map, BOM and nine-step traveler are included. Crimping, set-screw assembly, sleeving, labels, received fit, derating, tests, supply limits, grounding and every authority remain open. No hand crimp is released.

<!-- HR30-E1-J1-POWER-CABLE-P01-END -->
