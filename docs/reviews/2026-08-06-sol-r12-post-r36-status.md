# Sol R12 findings rechecked against R36

> **PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**

Date: 2026-08-06

This is a project-owned reconciliation, not a new independent Sol review. Sol's R12 totals remain **18 BLOCKER, 30 MAJOR and 8 MINOR** against the historical configuration.

## R36 correction

R36 adds a controlled protection and conductor-coordination input package for `F0`, `F1`, `F2`, `F3`, `FSR1`, and `FSR2`. It proposes exact holder/distribution hardware and an exact fuse family without selecting any ampere rating:

- Littelfuse `FHAC0002SXJ` for the F0 holder;
- Blue Sea Systems `5025` for the F1-F3 branch block;
- Littelfuse `ATOF` for the F0-F3 fuse family;
- FSR1/FSR2 device and holder family still `SELECTION REQUIRED`.

The six-row register contains 78 explicit open measurement/selection cells and zero released fuse ampere ratings. Three controlled procedures and one unexecuted form define analysis, receiving inspection, thermal/voltage/current characterization, and guarded clearing proof. R36 also corrects the shared KiCad-project regeneration path so schematic refreshes preserve PCB net classes/design settings and board-render evidence. A schematic regeneration followed directly by the PCB checker now passes without an intervening board repair. The native V3 source, schedules and exports were regenerated; ERC remains 0/0 and the exact-net and PCB checkers pass.

## Material finding retained

The current primary-source comparison exposes, rather than hides, a branch-connector conflict: ROBOTIS publishes XM540-W270-T at a 4.4 A stall endpoint at 12 V and identifies the JST EH connector family, while JST publishes 3 A AC/DC at AWG 22 for EH. ROBOTIS also states 21 AWG for DYNAMIXEL wire. This is not evidence that 4.4 A is an allowed continuous connector current and does not support selecting a fuse above the connector basis.

The two XM540 branches therefore remain blocked pending written application evidence or a qualified disposition, exact received-harness identity, released current limit/duty, stabilized thermal evidence and fault-clearing proof. The XM430 branch remains open for the same installed-harness evidence even though its 2.3 A stall endpoint is below the JST series screen.

## What R36 narrows

- Sol M-012 is narrowed because the exact missing protection inputs, candidate hardware boundary, execution records and non-release rule are now machine-controlled.
- Sol M-013 remains narrowed by the existing exclusion of U2D2 VDD and is reinforced by the 10.0 A Power Hub versus 11.1 A summed-stall screen.
- Energization gate `EG-014` moves from `open` to `partial`; through E2 the register now reports 0 closed, 15 partial and 6 open gates.

## What remains open

- All six fuse/protection ampere ratings and both coil-protection device families.
- Source prospective fault/current-limit behavior, cable lengths, conductor and terminal order codes, installed connector limits, ambient, bundling, duty, peak duration, regeneration, voltage drop, temperature and clearing-time evidence.
- The F0 12 AWG holder-pigtail to six-contact 16 AWG JA1 transition and all downstream terminal/splice details.
- Physical receipt, assembly, inspection, thermal/fault execution and qualified electrical/safety review.
- Every other physical-build, functional-safety, mechanical and control blocker retained in R35.

## Disposition

Sol's central verdict remains correct. R36 makes protection coordination executable and auditably unresolved; it does not make the machine buildable or energizable. No fabrication, wiring, procurement, functional-safety or energization approval is issued.
