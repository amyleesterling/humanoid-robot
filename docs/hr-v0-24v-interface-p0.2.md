# HR-V0 24 V source interface P0.2

**PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**

Identifier: `HR-V0-24V-IF-P0.2`

Date: 2026-08-08

Electrical dependency: Project Button Electrical `V3-P1.11`

Supersedes: `HR-V0-24V-IF-P0.1` for the current candidate only

## Outcome

R81 removes the unsupported Mean Well barrel-to-locking conversion from the current candidate. The proposed chain is now:

`PSU2 GlobTek WR9QI1660YL4NKITR6B with factory YL4/C40337 locking cord -> J24 Kycon KPJX-PM-4S -> F24 SELECTION REQUIRED -> SAFETY_24V`

GlobTek's exact Rev B specification covers the source and its output cord as one ordered product. It identifies a 24 V, 1.66 A, 40 W Class II wall adapter with floating output, a 1200 mm UL 1185 16 AWG 1C-plus-shield cord, an overmolded male four-pin locking connector, and the following output assignment:

| Point | Function | Candidate net |
|---|---|---|
| `PSU2:YL4-1` / `J24:1` | +24 V | `SAFETY_24V_RAW` |
| `PSU2:YL4-2` / `J24:2` | N/C | no net / no connection |
| `PSU2:YL4-3` / `J24:3` | 0 V / shield return | `SAFETY_0V` |
| `PSU2:YL4-4` / `J24:4` | N/C | no net / no connection |
| `F24:IN` | source +24 V | `SAFETY_24V_RAW` |
| `F24:OUT` | protected +24 V | `SAFETY_24V` |

Pins 2 and 4 may not be repurposed. GlobTek identifies YL4 as the KPPX-4P connector type, and Kycon recommends the KPJX-PM-4S jack for KPPX plugs. The exact GlobTek source drawing still permits a four-pin locking connector "or equal," so received plug identity, keyed fit, plug-view/jack-view reconciliation, continuity and polarity remain mandatory.

This removes the earlier source/accessory compatibility blocker. It does not release procurement, panel cutting, PCB or harness fabrication, wiring, protection, or energization.

## Preliminary continuous-load screen

| Load | Evidence basis | Screened power | Screened current at 24 V | Limitation |
|---|---|---:|---:|---|
| `K1/K2` | Schneider published 5.4 W DC coil consumption, two coils | 10.800 W | 0.450 A | pickup transient, tolerance, duty and received behavior open |
| `SR1/SRA1` | Pilz published 2.5 W power consumption, two devices | 5.000 W | 0.208 A | startup/input tolerance and installed configuration open |
| `KWD1/KWD2` | Phoenix Contact 18 mA typical, two devices | 0.864 W | 0.036 A | typical value is not a guaranteed maximum |
| `H1` | IDEC HW-family 24 V LED-lamp screen | 0.360 W | 0.015 A | exact complete-assembly mapping and received consumption open |
| `WDPCB1/DC1` | conservative project continuous design reserve | 10.000 W | 0.417 A | this is not a manufacturer rating; actual startup, steady, brownout, fault and thermal behavior must be measured |
| **Total** |  | **27.024 W** | **1.126 A** | screening result only |

At GlobTek's full-load ambient envelope through 40 C, the nameplate headroom is 12.976 W. At the published 50 C / 80% limit, the derated source capacity is 32 W and the screened headroom is 4.976 W. Neither number closes simultaneous pickup, wiring loss, source tolerance, startup, brownout, current-limit interaction, recovery, abnormal-condition or enclosure-temperature behavior.

GlobTek specifies an auto-recovering output current limit from 110% to 160% of rated current. That range does not select or coordinate `F24`; it reinforces the need for measured source behavior and time-current coordination.

## Remaining blockers

- receive and identify the exact source, Q-NA blade and supplied locking plug;
- prove blade retention and site/outlet suitability;
- prove exact plug-to-KPJX-PM-4S fit, keyed orientation, continuity and polarity;
- execute simultaneous pickup, steady-state, brownout, source-foldback/recovery and abnormal-condition tests;
- select `F24` only after source behavior, load inrush, conductor/connector limits, cable length, ambient, bundling, time-current curves and Boston jurisdictional review are accepted;
- release the PCB or harness, terminals, insulation, support, panel entry, mounting, retention, strain relief and touch protection;
- execute voltage-drop, contact-temperature, retention, pullout and fault tests at the accepted worst case; and
- obtain qualified electrical review and controlled stage-specific work authorization.

## Controlled files

The machine-readable package is `electrical/interfaces/hr-v0-24v-interface-p0.2/`:

- `interface-bom.csv`
- `pin-allocation.csv`
- `load-budget.csv`
- `compatibility-holds.csv`
- `source-register.csv`
- `interface-summary.json`
- `HR-V0_24v-interface-guide.html`

Generate with `python tools/generate_hr_v0_24v_interface.py` and check with `python tools/check_hr_v0_24v_interface.py`.

## Primary evidence

- GlobTek, `WR9QI1660YL4NKITR6B`, specification Rev B, current generated copy and product page rechecked 2026-08-08: https://spec.globtek.info/spec/?id=01t0c000008jfZg
- GlobTek, exact product page, rechecked 2026-08-08: https://www.globtek.com/_0/WR9QI1660YL4NKITR6B/o
- Kycon, `KPJX-PM` catalog index `0126`, 2026-01: https://www.kycon.com/Catalog_PDF/KPJX-PM.pdf
- Kycon, `KPJX-PM-4S` drawing Rev C2, 2026-01-08: https://www.kycon.com/Pub_Eng_Draw/KPJX-PM-4S.pdf
- Schneider Electric, TeSys Deca catalog `MKTED210011EN`, 2026: https://download.schneider-electric.com/files?p_Doc_Ref=MKTED210011EN
- Pilz, PNOZ s4 product/manual record `21396-EN-23`, 2026: https://www.pilz.com/en-INT/eshop/product/750104
- Phoenix Contact, item `2967060`, data-maintenance date 2026-04-01: https://www.phoenixcontact.com/en-us/products/relay-module-plc-rsc-24dc21-21-2967060
- IDEC, HW Series screw-terminal catalog, updated 2026-07-23: https://us.idec.com/idec-us/en/USD/medias/HWSeries-us.pdf
- TRACO POWER, TSR 1 Series datasheet, 2024-02-07: https://www.tracopower.com/tsr1-datasheet

No result in this document approves procurement, fabrication, wiring, connection, energization, motion, human exposure or child-adjacent use.
