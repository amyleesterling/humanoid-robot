# Sol R12 findings rechecked against R30

Status: **project-owned reconciliation, not a new independent review**

Date: 2026-08-06

Sol's 18 BLOCKER / 30 MAJOR / 8 MINOR R12 verdict remains the controlled independent baseline. The analysis resupplied on 2026-08-06 is the same R12 review and is not counted twice.

R30 advances only the connected electrical correction candidate from `V3-P0.8` to `V3-P0.9`:

- freezes Vishay `MMA02040C1001FB300` for both `RTHR` positions;
- freezes Panasonic `ERJ6ENF5620V` for both `RSENSE` positions;
- freezes TDK `CGA3E2X7R1H103K080AA` for both field-input filter positions while retaining DC-bias validation;
- freezes Vishay `CRCW12102K70FKEA` for both 2.70 kilohm contact-wetting loads;
- freezes Murata `GRM21BR71H104KA01L` for logic decoupling;
- freezes Panasonic `ERJ6ENF1001V` and `ERJ6ENF1002V` for the GPIO series and default-low networks;
- adds exact-value checker assertions, `INSPECT-ELEC-006`, and an unexecuted received-part/PCB/derating record.

Simple steady-state screens show 7.56 mW in each threshold resistor, 4.25 mW in each current-set resistor, 0.226 W in each wetting resistor, 10.9 mW for the worst 3.3 V output-series contention screen, and 1.09 mW in each pulldown. These screens do not include PCB/enclosure temperature, pulse/fault energy, capacitor DC bias, EMC, contamination, manufacturing variation, or physical layout.

The regenerated candidate remains 11 pages, 59 component blocks, 274 terminals, 63 named connected plus 37 deliberate unconnected nets, 237 wire labels, 47 unresolved component/interface evidence rows, and 46 `TBD-*` terminals. Exact order codes do not remove a row when physical verification is still required.

R30 narrows Sol's anonymous/passive-selection finding. It does not close the corresponding build or energization blocker because no released PCB, received passive measurements, footprint/placement evidence, thermal/pulse/DC-bias/EMC validation, target fault injection, HIL trace, FMEA, PLr/SIL allocation, qualified review, or physical safety validation exists.

No energization gate closed. HR-V0 remains not ready to build and prohibited from energization.
