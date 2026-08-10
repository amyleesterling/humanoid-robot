# HR-V0 DXL protection-carrier harness P0.1

> **PRELIMINARY - NOT APPROVED FOR SUPPLIER UPLOAD, QUOTATION, PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, MOTION, OR ENERGIZATION**

Identifier: `HR-V0-DXL-PROT-CARRIER-HARNESS-P0.1`

Round: R160

Date: 2026-08-09

## Result

R160 turns the P0.3 carrier's generic “mating harness held” note into a controlled two-harness interface:

- `HAR-CIN` connects an unresolved protected source/fuse termination to carrier `JIN1`.
- `HAR-COUT` connects carrier `JOUT1` to one selected DXL-star `JP1`, `JP2`, or `JP3` input.

The carrier and DXL-star mating candidates are JST `VHR-2N` housings with `SVH-21T-P1.1` contacts. The conductor candidate is Belden 9918, 18 AWG 16x30 tinned copper: `9918 002100` red for positive and `9918 010100` black for return. JST's current catalog places that contact and nominal 2.0 mm wire OD inside the published AWG 22-to-18 and 1.7-to-3.0 mm envelope.

That comparison is not an installed current rating or application approval.

## Deliberate holds

No strip length, crimp height, pull force, hand-tool identity, source-side termination, cut length, strain relief, installed ampacity, thermal limit, voltage-drop limit or fault-clearing acceptance was inferred. Nine explicit selections and eighteen blank acceptance rows remain open. The existing pre-carrier `J1_VDD/J2_VDD/J3_VDD` naming also requires an Electrical V3/DXL-star revision before a carrier may be inserted without net-name ambiguity.

The [interactive guide](../release/hr-v0/dxl-protection-carrier-harness-p0.1/index.html) exposes the interface map, exact candidate BOM, cut/crimp schedule, process traveler, unresolved selections and blank acceptance matrix. Every cut/crimp row says `DO NOT CUT OR CRIMP`.

## Review accounting

The Sol summary supplied again at this stage is the existing R12 independent verdict (`18 BLOCKER / 30 MAJOR / 8 MINOR`) and is not counted as a new independent review. R160 is a project-owned response to its missing-buildable-electrical and fabrication-evidence findings. It closes no physical, qualified-review, functional-safety or work-authorization gate.
