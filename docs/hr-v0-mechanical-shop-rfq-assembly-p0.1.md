# HR-V0 mechanical shop, RFQ and unpowered assembly candidate P0.1

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Identifier: `HR-V0-MECH-SHOP-RFQ-ASSY-P0.1`

Round: R247

Status: **REVIEW/RFQ PREPARATION ONLY**

## Result

R247 converts the five current P0.3-bound custom parts into a controlled successor shop-drawing and provider-review package without changing their nominal geometry. Each P0.2 SVG now prints the current integrated architecture identifier, the complete preliminary warning, a drawing number, revision, units, scale, source binding, geometry-change declaration and an explicit false fabrication-authority field.

The package also provides:

- a hash-bound 15-artifact RFQ payload containing five P0.2 shop drawings, five current finished-profile DXFs and five current STEP files;
- fourteen unsent provider capability and DFM questions;
- a 21-step zero-energy assembly sequence covering interfaces A00 through A07 and the J2 positive hard-stop pair;
- nine joint-verification records;
- twelve unresolved tool and consumable selections;
- an eight-step nonconformance workflow;
- twelve open holds; and
- ten unexecuted acceptance rows.

No provider has been selected or contacted. No file transmission, quotation, procurement, fabrication, assembly or physical inspection is authorized.

## Geometry and configuration boundary

The five successor drawings retain the exact geometry fingerprints of their P0.1 predecessors. The fifteen STEP/DXF identities remain the exact hashes in `HR-V0-MECH-BOM-BIND-P0.3`, and the current mechanical architecture remains `HR-V0-ARM-ARCH-P0.8-DWG-INTEGRATED-CANDIDATE`.

The P0.2 drawing change is administrative and control-layer only. It corrects the stale printed architecture identifier and warning, adds a controlled title block and identifies the absence of a released formal datum reference frame and feature-control frames. It does not change a hole, edge, thickness, profile or nominal part position.

`HR-V0-CONFIG-REC-P0.11` carries the result as a supporting candidate. P1.15 remains the current electrical design and P1.21 remains unaccepted. The system BOM remains 98 groups.

## Why fabrication remains blocked

The existing `ICF-01` least-squares registration method is retained for inspection planning, but it is not represented as an ASME Y14.5 datum reference frame. Formal datum and GD&T disposition remains `SELECTION REQUIRED` for every part and requires a qualified mechanical reviewer.

The following evidence is also absent:

1. an authorized provider capability response and complete DFM disposition;
2. released material/process specifications and received certificates;
3. exact fastener stack, torque, locking, reuse and tool selections;
4. calibrated first-article inspection of all five physical parts;
5. separate authorization and execution of the zero-energy assembly traveler;
6. unpowered full-chain fit and hard-stop evidence;
7. structural, slip, pullout, prying, fatigue and proof evidence;
8. received mass, center-of-mass and inertia reconciliation; and
9. signed, configuration-bound qualified release.

## Web review

- [Interactive mechanical shop/RFQ/assembly guide](../release/hr-v0/mechanical-shop-rfq-assembly-p0.1/index.html)
- [Configuration reconciliation P0.11](../release/hr-v0/configuration-reconciliation-p0.11/index.html)

These artifacts prepare a qualified review and a future authorized capability inquiry. They are not a fabrication package or work instruction.
