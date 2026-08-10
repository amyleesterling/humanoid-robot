# HR-V0 gripper CAD acquisition and datum-closure plan

Document ID: **HR-V0-GRIP-CAD-ACQ-P0.1**
Date: 2026-08-07
Parent: `HR-V0-GRIP-P0.2`
Requirements: `GRIP-002`, `MECH-005`, `MASS-002`
Verification: `AUDIT-GRIP-002`
Status: **PRELIMINARY - NOT APPROVED FOR FABRICATION, MOTION, OR ENERGIZATION**

Current acquisition correction: `HR-V0-GRIP-ACQ-P0.2` records the exact FR12-G101GM/HN12-I101 orderable scope and rejects that frame set as a sole substitute for the complete mechanism. The publisher-file and received-metrology routes below remain open.

## Decision

The current official ROBOTIS repository supplies useful `link5` and palm collision/visual meshes plus URDF kinematics. Those files do not define the complete gripper mechanism, the H104-to-carrier installation transform, fastener stacks, physical mass, tolerances, or a manufacturing release.

ROBOTIS's current OpenMANIPULATOR-X assembly page identifies the mechanism parts and links both an Onshape route and Thingiverse design 3069574. On 2026-08-07 the ROBOTIS endpoint `https://www.robotis.com/service/download.php?no=690` redirected to an error page. The official Thingiverse publisher page exposed metadata naming the printable mechanism files, but a controlled file set was not acquired. No missing dimension, transform, rating, revision, or file identity is inferred from that metadata.

`GRH-001` and `GRH-002` remain open. Project Button permits only the following two closure routes.

## Route A - controlled publisher files

1. Obtain the current direct ROBOTIS Onshape document/version URL or downloadable source package through the ROBOTIS Download Center or support channel.
2. Preserve every file without format conversion. Record publisher, source URL, filename, document/version identity, publication or file date, license, units, coordinate convention, and SHA-256 in `tests/forms/hr-v0-gripper-cad-acquisition-template.csv`.
3. Prefer a native assembly and native STEP or Parasolid parts. An STL may be retained as a labeled reference but cannot, by itself, establish threads, tolerances, material, fasteners, assembly mates, or release status.
4. Rebuild the complete mechanism from the frozen files. Independently correlate all assembly datums, component count, travel, fastener access, moving envelope, and the H104 installation interface.
5. Keep any publisher manufacturing-release claim verbatim and separately reviewed. Open-source availability is not equivalent to a fabrication release for Project Button.

## Route B - controlled received-part metrology

1. Receive and quarantine one exact RM-X52 kit under `INSPECT-GRIP-001` and the existing gripper receiving record. Preserve order label, lot or serial identity, contents, photographs, and measured component masses.
2. Establish physical datum frames GDM-A through GDM-G using `tests/forms/hr-v0-gripper-datum-metrology-template.csv`. Record the method, calibrated instrument, uncertainty, temperature, raw data, and independent reviewer.
3. Capture H104 and carrier mounting planes, hole patterns and axes; linkage pivot and rail geometry; installed-pad openings; service/cable envelope; complete mass and local center of mass. Do not backfill nominal values from a visual mesh.
4. Build native project CAD from the measured data, clearly labeling it `REVERSE-ENGINEERED FROM RECEIVED ARTICLE`. Preserve the raw scan/measurement evidence and quantify model-to-article residuals.
5. A qualified mechanical reviewer must accept the transform, tolerance basis, fastener stack, collision/guard model, load path, and intended manufacturing process before any supplier packet is generated.

Neither route may close usable opening, force/current, power-off retention, guarding, wear, drop, mass, or motion tests merely by producing CAD.

## Required H104-to-carrier datum closure

`cad/hr-v0/gripper-datum-control-p0.1.csv` deliberately leaves all six rigid-transform quantities and every acceptance tolerance as `SELECTION REQUIRED`. The closure record must include:

- translation X/Y/Z and rotation X/Y/Z between controlled datum frames;
- mounting-plane, hole/thread, actuator-axis, and fastener-access evidence;
- units, coordinate convention, handedness, and transform order;
- uncertainty or source tolerances and model-to-article residuals;
- an exact configuration and repository commit; and
- independent mechanical disposition.

Until that record passes, the reference gripper must not be merged into P0.7 for collision, reach, mass, fabrication, or safety credit.

## Prepared ROBOTIS support query - not sent

Subject: OpenMANIPULATOR-X / RM-X52 current gripper CAD and interface datum request

> Please provide the current direct Onshape document/version link or downloadable native files for the OpenMANIPULATOR-X gripper mechanism associated with RM-X52, including PALM GRIPPER, LINK ROD, FLANGE BUSH, CRANK ARM, RAIL BLOCK, RAIL BRACKET LEFT/RIGHT, link5/carrier, and the complete assembly. STEP or Parasolid plus the native assembly is preferred. Please identify file revision/date, units, coordinate convention, license, current product applicability, and whether Thingiverse design 3069574 is the current published set. If available, please also provide the H104-to-link5/carrier datum definition, exact fastener stack, material, and component/assembly mass data.

This text is a draft only. No email, support ticket, or supplier request has been sent by Codex.

## Source record

The controlled availability register is `cad/hr-v0/gripper-source-availability-p0.1.csv`. Primary sources recorded there are the [ROBOTIS assembly page](https://emanual.robotis.com/docs/en/platform/openmanipulator_x/assembly/), [ROBOTIS OpenMANIPULATOR-X product page](https://www.robotis.us/openmanipulator-x/), [ROBOTIS Support](https://www.robotis.us/Support), [official ROBOTIS GitHub repository](https://github.com/ROBOTIS-GIT/open_manipulator), and [ROBOTIS-published Thingiverse design](https://www.thingiverse.com/thing:3069574).

## Release boundary

This package closes only the ambiguity about how missing geometry may be obtained and controlled. It does not close any gripper integration hold, authorize a purchase or supplier contact, establish a physical datum, or make HR-V0 buildable. Every numerical datum and acceptance limit remains `SELECTION REQUIRED` until supported by controlled evidence and qualified review.
