# HR-V0 DXL carrier integration P0.1

> **PRELIMINARY - NOT APPROVED FOR SUPPLIER UPLOAD, QUOTATION, PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, MOTION, OR ENERGIZATION**

Identifier: `HR-V0-DXL-CARRIER-INTEGRATION-P0.1`

Electrical candidate: `V3-P1.15-CARRIER-CANDIDATE`

DXL-star candidate: `DXL-STAR-P0.2-CARRIER-CANDIDATE`

Carrier source: `HR-V0-DXL-PROT-CARRIER-P0.3`

Date: 2026-08-09

## Correction

The P1.14/P0.1 sources used `J1_VDD`, `J2_VDD`, and `J3_VDD` on both sides of the proposed current-limiter carriers. That naming did not encode the limiter boundary and could not support an unambiguous point-to-point harness.

The separate R161 candidates introduce three explicit four-terminal carrier blocks:

- `F1.2 J1_FUSED_PRELIMIT -> LIM1.JIN1:1 -> LIM1.JOUT1:1 J1_LIMITED_VDD`;
- `F2.2 J2_FUSED_PRELIMIT -> LIM2.JIN1:1 -> LIM2.JOUT1:1 J2_LIMITED_VDD`;
- `F3.2 J3_FUSED_PRELIMIT -> LIM3.JIN1:1 -> LIM3.JOUT1:1 J3_LIMITED_VDD`.

Each `JIN1:2/JOUT1:2` return remains `ACT_0V_PE_BONDED`. The P0.2 DXL-star candidate uses only the `*_LIMITED_VDD` rails at `JP1/JP2/JP3` and `JA1/JA2/JA3`. `JC1:2` remains intentionally omitted from copper.

The current P1.14/P0.1 baseline is preserved. R161 is a review candidate, not a released baseline.

## Physical integration screen

The nominal P0.6 backplate reserve `BP-026` is screened at `x=54..377.8 mm`, `y=533.4..675.8 mm`. Three nominal 100 x 60 mm P0.3 carriers analytically fit without overlap at:

| Ref | Lower-left x | Lower-left y |
|---|---:|---:|
| LIM1 | 54.0 mm | 538.0 mm |
| LIM2 | 164.0 mm | 538.0 mm |
| LIM3 | 54.0 mm | 608.0 mm |

The carrier holes are screened from the native P0.3 board at `(5,5)`, `(95,5)`, `(5,55)`, and `(95,55)` mm relative to each board origin. These coordinates do not release drilling. Received dimensions, standoffs, connector sweep, cover depth, airflow, service access, coating/bonding disposition, tolerances and qualified layout review remain absent.

Six geometric route lower-bound screens are recorded, but every cut length remains `SELECTION REQUIRED`. Surrogate centers omit exact terminal locations, duct entries, bend radii, service loops, strain relief, termination allowances and received tolerances.

## Evidence and limitations

- Electrical candidate: 13 native sheets, KiCad 10.0.5 ERC 0 errors / 0 warnings.
- DXL-star candidate: native ERC 0/0, DRC 0 violations, 0 unconnected pads.
- Native parity: P0.2 routed copper, footprints, pads, zones and outline are identical to P0.1 after the explicit net-name map.
- Integration records: 15 net transitions, three placements, twelve mounting-hole screens, six held route screens, twelve unresolved selections and 24 open acceptance rows.
- [Interactive review guide](../release/hr-v0/dxl-carrier-integration-p0.1/index.html)
- [Independent review request](reviews/2026-08-09-r161-independent-review-request.md)

ERC/DRC establish encoded connectivity and layout-rule consistency only. No carrier or star board has been built, and no continuity, polarity, isolation, current-limit, reverse-energy, fault, thermal, waveform, EMC or functional-safety test has been executed.
