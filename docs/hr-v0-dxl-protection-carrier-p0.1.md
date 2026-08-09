# HR-V0 DXL protection carrier P0.1

> **PRELIMINARY - NOT APPROVED FOR SUPPLIER UPLOAD, QUOTATION, PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, MOTION, OR ENERGIZATION**

- Identifier: `HR-V0-DXL-PROT-CARRIER-P0.1`
- Review round: R156
- Date: 2026-08-09

## Result

R156 converts the retained R155 `TPS259461LRPWR` circuit into a native single-channel four-layer carrier candidate that can support controlled physical measurements. The package proposes three separately serialized evaluation articles: two J1/J2 variants using `RC0603FR-071K65L` and one G1 variant using `RC0603FR-073K32L`.

The carrier uses exact candidate identities for the TI active device, four threshold resistors, dVdt capacitor, input/output capacitors, output Schottky, JST headers and Keystone test points. The input has 0.1 uF plus 1 uF candidates; the output has two parallel 1 uF candidates to provide nominal margin above TI's 1 uF guidance. Nominal margin is not effective-capacitance proof.

## Native engineering source

- Five native KiCad sheets: root, core, threshold dividers, bypass/transients and measurements.
- One routed 100 x 60 mm four-copper-layer PCB candidate.
- One custom `RPW0010A` footprint derived from TI's official package/land drawing.
- Twenty physical BOM placements plus four board-only M3 holes.
- KiCad 10.0.5 ERC: 0 errors / 0 warnings.
- KiCad 10.0.5 DRC: 0 violations / 0 unconnected pads.
- Review CAM outputs for all four copper layers, drill, position and statistics.

The custom footprint remains a drawing interpretation. DRC does not substitute for independent land-pattern audit, paste/mask decision, assembler DFM, first-article inspection or X-ray.

## Decisive limitations

TPS25946 limits forward current only. Reverse current remains unbounded while the device is ON, so this carrier does not solve regenerative-energy control by itself. The external Pololu 3771 shunt candidate remains outside the carrier and requires separate pulse-energy, thermal, source, contactor and simultaneous-axis validation.

The package contains ten blank tests and sixteen open hold groups. It does not change Electrical V3-P1.14, the system BOM, fuse values, connector/harness releases, functional-safety allocation or work authority. No physical test has been executed.

## Controlled package

- Native source: `electrical/kicad/hr-v0-dxl-protection-carrier/`
- Interactive guide and synchronized source/CAM review set: `release/hr-v0/dxl-protection-carrier-p0.1/`
- Generator: `tools/generate_hr_v0_dxl_protection_carrier_p01.py`
- Checker: `tools/check_hr_v0_dxl_protection_carrier_p01.py`

This is the physical-evidence route Sol found missing. It does not make HR-V0 build-ready or energization-ready.
