# HR-V0 runtime observation interface R201 / P0.1

**PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

This correction turns the four positive diagnostic states identified in R200 into a connected native KiCad evaluation candidate. It does not select Raspberry Pi GPIO pins, release a PCB or harness, add any safety function, or authorize a connection.

## Architecture

Two exact TI `ISO1212DBQ` candidates receive `SR1_STATUS`, `SRA1_STATUS`, `K1_STATUS`, and `K2_STATUS`. Every channel uses the exact controlled Type-3 network: Vishay `MMA02040C1001FB300` 1.00 kohm RTHR, Panasonic `ERJ6ENF5620V` 562 ohm RSENSE, and TDK `CGA3E2X7R1H103K080AA` 10 nF CIN. SRA1, K1, and K2 also use Vishay `CRCW12102K70FKEA` 2.70 kohm shunts. SR1 does not, because its Y32 output already drives H1.

Field FGND connects only to `SAFETY_0V`; logic GND1 connects only to `COMPUTE_0V`. This preserves a proposed isolated boundary in the schematic, but gives no system insulation or functional-safety credit. SUB pins remain intentionally unconnected and require their own floating copper under TI layout guidance.

## Calculation results

- ISO1212 Type-3 current is screened at 2.05 to 2.75 mA per active channel.
- SRA1/K1/K2 total status current is 10.41 to 12.18 mA with resistor and rail tolerance. Each 2.70 kohm shunt dissipates at most 0.238 W, 47.6% of its 0.5 W 70 C rating before enclosure derating.
- At Schneider's 17 V signalling minimum, the K1/K2 screen is 8.28 mA, above the 5 mA minimum. Installed voltage and physical contact performance remain open.
- Pilz Y32 residual current of 0.1 mA produces no more than 0.27 V across the nominal 2.70 kohm shunt, below the 8.7 V maximum-low threshold screen.
- SR1's catalog current screen is 7 mA H1 plus 2.75 mA receiver = 9.75 mA, leaving 10.25 mA to Pilz's 20 mA limit. This is not closure: the exact received H1 maximum current is unknown, and a 5 V Y32 drop on the 22.8 V rail can leave only 17.8 V for a 24 V light whose published voltage range begins at 21.6 V.
- Two ISO1212 logic sides plus four 10 kohm pulldowns screen at no more than 5.0 mA from 3.3 V. Raspberry Pi source capacity, GPIO thresholds, exact pins, boot pulls, cable and back-power behavior remain selection and HIL items.

## EMC and fault boundary

TI SLLSEY7G Table 8-1 reports the 562 ohm / 1 kohm / 10 nF Type-3 network at +/-1 kV line-to-PE and line-to-line, +/-500 V line-to-FGND surge, +/-6 kV IEC ESD and +/-4 kV EFT under TI's test arrangement. Those component-level application results are not a Project Button enclosure or cable qualification. TI also requires the high-voltage side of RTHR at least 4 mm from device/CIN/RSENSE pins and local 100 nF VCC1 bypassing.

All ten holds in `selection-holds.csv` remain open. The interface is diagnostic only; no output may command, restore, latch or preserve motion. ERC 0/0 proves only the encoded graph and annotations.

The controlled manufacturer document identities, revisions/dates, locators and application boundaries are recorded in `electrical/kicad/hr-v0-runtime-observation-interface-p0.1/source-register.csv`, including separate current Phoenix Contact records for items 1751264 and 1751248. Catalog ratings are not installed-system acceptance.
