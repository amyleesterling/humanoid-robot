# HR-V0 mechanical BOM binding P0.1

**PRELIMINARY - NOT APPROVED FOR QUOTATION, FABRICATION, ASSEMBLY, MOTION, OR ENERGIZATION**

Identifier: `HR-V0-MECH-BOM-BIND-P0.1`

Round: R148

Controlled architecture: `HR-V0-ARM-ARCH-P0.7`

## Correction

The live system BOM retained a superseded P0.5 custom-part description: three `MV0-C01` parts plus `MV0-C04` and `MV0-C05`. That set cannot represent the controlled P0.7 mechanism because it omits the J2 positive-stop parts `MV0-C06` and `MV0-C07`.

`BOM-027` now binds exactly one each:

- `MV0-C01` joint-to-20-2040 adapter;
- `MV0-C04` H104-to-20-2040 adapter;
- `MV0-C05` S102-to-40-4040 support;
- `MV0-C06` J2 positive moving striker; and
- `MV0-C07` J2 positive fixed catch.

The candidate total remains five. Each part is bound to the existing SHA-256-controlled STEP, DXF and readable SVG identity in `HR-V0-MECH-DFM-DATA-P0.1`. Candidate material remains 6061-T651 aluminum, 9.525 mm nominal and 9.00–10.00 mm finished. The screened process remains high-requirement 3-axis CNC subject to provider and qualified-review acceptance.

## Evidence and state

- [Interactive binding guide](../release/hr-v0/mechanical-bom-binding-p0.1/index.html)
- `bom/hr-v0-mechanical-custom-part-binding.csv`
- `release/hr-v0/mechanical-bom-binding-p0.1/package-status.json`
- `release/hr-v0/mechanical-dfm-data-p0.1/geometry-file-register.csv`
- `release/hr-v0/mechanical-dfm-data-p0.1/hold-register.csv`

The BOM closure class advances from `selection_required` to `exact_candidate_hold` because configuration identity and candidate quantity are now exact. This is not a machining release. All fifteen DFM holds remain open: qualified drawing review, architecture freeze, material/MTR, received interfaces, T-slot capacity, countersink/fastener stack, stop bumper and load, cable/guard envelope, mass properties, continuous actuator duty, physical acceptance, provider acceptance, commercial authority, and safety/energization.

No provider has been contacted. No geometry may be uploaded. Quotation, purchase, first article, fabrication, assembly, motion and energization remain unauthorized.
