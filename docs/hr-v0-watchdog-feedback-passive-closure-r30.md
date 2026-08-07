# HR-V0 watchdog-feedback passive closure — R30

> **PRELIMINARY — NOT APPROVED FOR FABRICATION OR ENERGIZATION**

Configuration: Electrical `V3-P0.9`

Date: 2026-08-06

## Scope

R30 replaces the value-only passive records on the `ISO1212DBQ` watchdog-feedback sheet with exact proposed manufacturer order codes. This removes procurement ambiguity for the candidate circuit. It does not release a PCB, close physical derating, assign safety credit, or authorize procurement, fabrication, or energization.

## Frozen candidates

| References | Proposed exact order code | Manufacturer facts used | Preliminary screen | Evidence still required |
|---|---|---|---|---|
| `RTH1`, `RTH2` | Vishay `MMA02040C1001FB300` | 1.00 kΩ, ±1%, MELF; `MMA0204` power-operation rating 0.4 W at 70 °C; 200 V maximum operating voltage | 2.75 mA produces 7.56 mW | Released footprint and land pattern; PCB temperature; pulse/surge/EFT/ESD envelope; enclosure derating; received resistance |
| `RSN1`, `RSN2` | Panasonic `ERJ6ENF5620V` | 562 Ω, ±1%, 0805, 0.125 W | 2.75 mA produces 4.25 mW, 3.4% of nominal rating | PCB temperature; tolerance/fault analysis; received resistance; powered threshold/current evidence |
| `CFI1`, `CFI2` | TDK `CGA3E2X7R1H103K080AA` | Production; 10 nF ±10%, 50 VDC, X7R, 0603, −55 to 125 °C, AEC-Q200 | Rated voltage exceeds the 24.6 V screened rail maximum | Effective capacitance under DC bias, tolerance and temperature; received measurement; EMC placement and test |
| `RW1`, `RW2` | Vishay `CRCW12102K70FKEA` | 2.70 kΩ, ±1%, 1210; 0.5 W at 70 °C; 200 V maximum operating voltage | Worst screened steady loss 0.226 W, 45.2% of nominal rating | Board/enclosure temperature; power derating; pulse and open/short behavior; received resistance and thermal image |
| `CDEC1` | Murata `GRM21BR71H104KA01L` | 100 nF, 50 V, X7R, 0805 | Same controlled candidate already used for local driver bypass | Placement within 2 mm of `UFB1`; PCB land pattern; received capacitance; power-sequence evidence |
| `RSO1`, `RSO2` | Panasonic `ERJ6ENF1001V` | 1.00 kΩ, ±1%, 0805, 0.125 W | 3.3 V contention screen: 10.9 mW, 8.7% of nominal rating | Output/GPIO fault injection, target thresholds, received resistance and PCB review |
| `RPD1`, `RPD2` | Panasonic `ERJ6ENF1002V` | 10.0 kΩ, ±1%, 0805, 0.125 W | 3.3 V produces 1.09 mW | Brownout/high-impedance behavior, target HIL, received resistance and PCB review |

These percentages compare simple steady-state screens with manufacturer nominal power ratings. They are not an allowable-temperature-rise calculation and do not include mounting, ambient, enclosure, neighboring heat, pulse energy, fault energy, aging, or production variation.

## Circuit constraints retained

- `RSN1/2` remain between `SENSE` and `IN`, not from `IN` to field ground.
- `CFI1/2` remain from `SENSE` to `SAFETY_0V` and must be located at `UFB1`.
- `RW1/2` remain in parallel with each field-input path to meet the proposed Phoenix relay contact wetting-current screen.
- `CDEC1` must be located within 2 mm of the `UFB1` logic-supply pins.
- Logic and field grounds remain tied to `SAFETY_0V`; no galvanic-isolation or PL/SIL credit is claimed.
- A welded watchdog contact remains a known limitation; freezing passive parts does not make the ordinary watchdog a validated safety function.

## Controlled verification

Execute `INSPECT-ELEC-006` using `tests/forms/hr-v0-watchdog-feedback-passive-receiving-template.csv` before any powered feedback-board test. Attach manufacturer-marking/packaging photographs, traceable resistance and capacitance measurements, PCB land-pattern and placement evidence, and the approved thermal/pulse/bias/fault analysis. Powered threshold, brownout and fault-injection work remains part of the later disconnected-load PCB/HIL program.

## Primary manufacturer evidence

- Texas Instruments, *ISO121x Isolated 24-V to 60-V Digital Input Receivers*, `SLLSEY7G`, revised February 2025: https://www.ti.com/lit/ds/symlink/iso1211.pdf
- Vishay Beyschlag, *MMU 0102, MMA 0204, MMB 0207 Thin Film MELF Resistors*, document `28963`, revision 2026-06-02: https://www.vishay.com/docs/28963/mmu0102_mma0204_mmb0207.pdf
- Vishay, *D/CRCW e3 Standard Thick Film Chip Resistors*, document `20035`, revision 2026-04-14: https://www.vishay.com/docs/20035/dcrcwe3.pdf
- Panasonic Industry, `ERJ6ENF5620V`, `ERJ6ENF1001V`, and `ERJ6ENF1002V` current product pages, accessed 2026-08-06: https://industrial.panasonic.com/ww/products/pt/general-purpose-chip-resistors/models/ERJ6ENF5620V, https://industrial.panasonic.com/ww/products/pt/general-purpose-chip-resistors/models/ERJ6ENF1001V, and https://industrial.panasonic.com/ww/products/pt/general-purpose-chip-resistors/models/ERJ6ENF1002V
- TDK, `CGA3E2X7R1H103K080AA` current production product page, accessed 2026-08-06: https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=CGA3E2X7R1H103K080AA
- Murata, `GRM21BR71H104KA01L` official specification asset, updated 2025 and accessed 2026-08-06: https://pim.murata.com/asset/pim4/ceramicCapacitorSMD/GRM21BR71H104KA01-01-EN_PDF_CERAMICCAPACITORSMD?lastModifiedDatetime=20250707233810

R30 closes exact passive identity only. PCB, received hardware, derating, EMC, fault injection, HIL, FMEA, qualified electrical review and qualified functional-safety validation remain open.
