# HR-V0 DXL protection carrier P0.2

> **PRELIMINARY - NOT APPROVED FOR SUPPLIER UPLOAD, QUOTATION, PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, MOTION, OR ENERGIZATION**

> **SUPERSEDED FOR CURRENT NATIVE/MANUFACTURING REVIEW:** R159/P0.3 retains this revision's RPW copper/mask/paste geometry but corrects the native soldermask-dam rule and adds board fiducials plus a controlled DFM inquiry. P0.2 remains historical review evidence and is not a supplier release.

- Identifier: `HR-V0-DXL-PROT-CARRIER-P0.2`
- Review round: R158
- Date: 2026-08-09
- Robot baseline changed: no
- Tests executed: 0
- Qualified approvals: 0

## Result

R158 independently re-read the RPW0010A package and example board/stencil land patterns in the Texas Instruments TPS25946 datasheet `SLVSGA8B`, revision B, April 2022, package drawing `4225183/A` dated 08/2019. That audit found eight explicit P0.1 transcription failures. P0.1 is therefore superseded and prohibited for supplier use.

P0.2 retains the R156 circuit only as an evaluation carrier and corrects the custom footprint to the drawing-derived 0.45 mm side-pad pitch, 0.30 x 2.40 mm central copper, compound L-shaped corner copper, 0.05 mm solder-mask-expansion candidate and separate reduced stencil apertures. The official source file accessed on 2026-08-09 had SHA-256 `AC74BA4AE2470ECD4E8657B2E964DEC5CE0643A8D4466476BA3486E980CED490`.

## Exact encoded geometry

| Feature | P0.2 encoding |
|---|---:|
| Side pads 2/3/8/9 | 0.60 x 0.25 mm at 0.45 mm pitch |
| Central copper pads 5/6 | 0.30 x 2.40 mm |
| Corner horizontal copper | 0.60 x 0.30 mm |
| Corner vertical copper | 0.25 x 0.65 mm |
| Central paste, each copper pad | two 0.28 x 1.06 mm apertures |
| Corner horizontal paste | 0.60 x 0.275 mm |
| Corner vertical paste | 0.225 x 0.63 mm |
| Mask expansion candidate | 0.05 mm around copper |

The footprint is encoded as 14 copper/mask pad primitives plus 16 paste-only aperture primitives. Compound corner primitives share the electrical pad number. The mask value is a review candidate subject to selected-fabricator capability and tolerance review.

## Verification performed

- Five native KiCad sheets parse under KiCad 10.0.5.
- ERC: 0 errors / 0 warnings.
- DRC: 0 violations / 0 unconnected pads / 0 footprint errors within the modeled rule set.
- Native `pcbnew` checker: exact 14-copper / 16-paste primitive parity passed.
- Ten-row source-to-P0.1-to-P0.2 comparison register records eight explicit P0.1 failures and their P0.2 corrections.
- Package manifest, warnings and all denial flags are machine checked.

These checks establish repository consistency and internal drawing transcription only. They do not establish solderability, fabrication capability, assembly yield, thermal behavior, electrical suitability or permission for physical work.

## Holds that remain decisive

`R158-H01` is only partial. A reviewer independent of the author must recheck the land pattern; the selected fabricator and assembler/stencil provider must accept the mask, paste, copper and process assumptions; and the first article requires AOI plus X-ray. Fifteen other holds remain open, including stackup, thermal performance, forward-current calibration, reverse current, clamp pulse energy, source/contactor/fuse coordination, connector/harness current, capacitance/derating, grounding, variants, inspection, HIL/fault tests, qualified review and explicit authorization.

## Controlled package

- Native source: `electrical/kicad/hr-v0-dxl-protection-carrier-p0.2/`
- Interactive guide and synchronized review outputs: `release/hr-v0/dxl-protection-carrier-p0.2/`
- Exact comparison: `release/hr-v0/dxl-protection-carrier-p0.2/rpw-land-pattern-parity.csv`
- Generator: `tools/generate_hr_v0_dxl_protection_carrier_p02.py`
- Native checker: `tools/check_hr_v0_dxl_protection_carrier_p02.py`

P0.2 does not alter Electrical V3-P1.14, select a supplier, release a BOM, authorize a quotation/order, or make HR-V0 build-ready or energization-ready.
