# HR-V0 runtime observation carrier R202 / P0.2 / PCB-P0.1

**PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

R202 supersedes R201's compound 4+2 terminal candidate with exact six-position Phoenix Contact `MKDS 1/6-3,5`, item `1751280`, for both field and compute boundaries. It adds a native routed four-layer 120 x 90 mm PCB candidate while retaining the R201 receiver calculations and diagnostic-only boundary.

The PCB has 29 mounted component footprints plus four board-only M3 holes, separate `SAFETY_0V` and `COMPUTE_0V` zones on In1.Cu, a compute-side `PI_3V3_CANDIDATE` zone on In2.Cu, a 5.6 mm field/compute zone corridor and four isolated floating SUB lands. No signal trace crosses the field/compute corridor; only the two ISO1212 packages span the functional domain boundary.

Native ERC and DRC both report zero violations in the encoded candidate. That proves neither application safety nor manufacturability. Phoenix's 1.1 mm drill is manufacturer data; the 2.10 mm copper land is inherited project-controlled geometry and requires fabricator acceptance. Four layers, stackup, laminate, copper, solder mask, stencil, assembly process, mounting, enclosure and first article remain open.

The schematic still does not select Raspberry Pi GPIOs. The two six-position screw terminals terminate project-defined board positions only; exact wire, ferrules, labels, 5 mm strip length, 0.22-0.25 Nm torque application, strain relief and service routing require a released harness. No output may command, restore or preserve motion. All fourteen holds remain open and zero functional-safety credit is claimed.
