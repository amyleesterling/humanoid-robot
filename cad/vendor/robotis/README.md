# ROBOTIS manufacturer reference CAD

These files were retrieved from the current ROBOTIS product documentation on 2026-08-06. They remain manufacturer reference artifacts and are not Project Button fabrication drawings. File hashes and source URLs are recorded in `vendor-manifest.csv`.

The checked files establish the actuator envelope and the FR13-H101K, FR13-S101K, FR13-S102K, and FR12-H104K frame interfaces used by the HR-V0 concept. The OpenMANIPULATOR-X assembly manual supplies controlled gripper-assembly context. The project must still physically fit-check purchased parts before cutting production metal.

R71 also freezes the official OpenMANIPULATOR repository's `link5`, left-palm and right-palm STL files plus the URDF at exact upstream commit `9187eca0920458be04d2399906388f55242f81f1`. The imported `LICENSE` is retained beside those sources. These are collision/visualization and kinematic references only. They are not native part-level manufacturing CAD, do not establish the H104-to-URDF transform on the received kit, and receive no physical mass credit. In particular, the URDF's one-gram palm inertia records are treated as simulation placeholders, not measurements.

For the distal gripper interface, the project selects a compact four-hole subset on a 24 x 12 mm rectangle from the received FR12-H104K STEP geometry and checks it with `MV0-FC03`. The drawing is dated Aug-31-17 and states `FOR REFERENCE ONLY`; physical seating, fastener access, exact hardware, tolerance and structural proof therefore remain mandatory.

R115 controls the current official XC430-W240 e-Manual download chain for the complete FR12-H104K DWG/PDF/STEP reference set. The current PDF and STEP are byte-identical to the files already held here; the added DWG has an `AC1015` signature. This provenance correction does not define the H104-to-OpenMANIPULATOR carrier transform, complete gripper mechanism, manufacturing tolerances or physical acceptance evidence.

## Documentation defect recorded during retrieval

The current ROBOTIS XM540-W270-T e-Manual labels download number 696 as the FR13-S101K STEP file, but that endpoint delivered a DWG. The manufacturer endpoint numbered 698 delivered the S101 STEP file stored here. The mismatch is not corrected or inferred silently; the actual resolved URL and hash are retained in the manifest.

Project Button does not extend or reinterpret the upstream license. Retain the imported license, source URLs, exact commit and manufacturer notices. If repository redistribution is challenged, remove the binaries and use the manifest to retrieve controlled local copies.

**PRELIMINARY—NOT RELEASED FOR FABRICATION OR ENERGIZATION.**
