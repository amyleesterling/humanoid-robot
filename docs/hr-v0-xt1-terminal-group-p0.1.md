# HR-V0 XT1 control-terminal group P0.1

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, ASSEMBLY, WIRING, OR ENERGIZATION.**

Identifier: `HR-V0-XT1-P0.1`

Review round: R168

## Configuration correction

The panel and E2 packages already freeze six XT1 position-to-net candidates and exact Phoenix Contact catalog bodies, but system `BOM-039` still described the complete group as `SELECTION REQUIRED`. R168 reconciles that mismatch.

The exact held group is:

- five Phoenix Contact `3209510` gray PT 2.5 feed-through terminal blocks;
- one Phoenix Contact `3209523` blue PT 2.5 BU feed-through terminal block;
- one Phoenix Contact `3030417` D-ST 2.5 gray end cover; and
- zero bridges or jumpers.

Two `3022218` CLIPFIX 35 brackets physically restrain XT1, but their procurement quantity is already controlled within the six-bracket panel stock group `BOM-085`. They are not duplicated in BOM-039. Unmarked `0828734` marker stock is referenced by the panel package, while printed labels and their process remain under `BOM-062`; it is likewise not duplicated in BOM-039.

## Exact position map

| Position | Catalog body | Net | Bridge |
|---|---|---|---|
| XT1-01 | 3209510 gray | SAFETY_24V | NO BRIDGE |
| XT1-02 | 3209523 blue | SAFETY_0V | NO BRIDGE |
| XT1-03 | 3209510 gray | SR1_STATUS | NO BRIDGE |
| XT1-04 | 3209510 gray | SRA1_STATUS | NO BRIDGE |
| XT1-05 | 3209510 gray | K1_STATUS | NO BRIDGE |
| XT1-06 | 3209510 gray | K2_STATUS | NO BRIDGE |

This mapping is configuration evidence, not a wiring release.

## Manufacturer data boundary

Phoenix Contact publishes the PT 2.5 family as push-in, 5.2 mm wide, with 8 to 10 mm strip length and manufacturer nominal 800 V / 24 A data. Those values describe the component under the manufacturer's conditions. They do not select Project Button conductor size, allowable circuit current, protection, ambient/bundling derating, connector coordination, temperature rise or jurisdictional compliance.

## Holds that remain open

The exact wire and insulation MPN, conductor size/color, cable length, fault/load current, voltage drop, bundling, ambient, direct-wire/ferrule method, ferrule/tool/die, strip-process control, grounding disposition, status-interface proof, printed markers, received identity, end-cover orientation, rail retention, point-to-point inspection and qualified review remain unresolved. `open-holds.csv` retains twelve explicit holds and every authorization is false.

`XT1-02 = SAFETY_0V` does not create a DC 0 V/PE bond. The separate grounding/bonding package remains controlling.

## Controlled artifacts

- `electrical/panel/hr-v0-xt1-terminal-group-p0.1/terminal-position-register.csv`
- `electrical/panel/hr-v0-xt1-terminal-group-p0.1/accessory-allocation.csv`
- `electrical/panel/hr-v0-xt1-terminal-group-p0.1/source-register.csv`
- `electrical/panel/hr-v0-xt1-terminal-group-p0.1/open-holds.csv`
- `electrical/panel/hr-v0-xt1-terminal-group-p0.1/package-status.json`
- `requirements/hr-v0-gate-evidence-supplement-r168.csv`
- `release/hr-v0/xt1-terminal-group-p0.1/index.html`
- `tools/check_hr_v0_xt1_terminal_group_p01.py`

`EG-003` and `EG-015` remain partial. No purchase, assembly, wiring, connection, test, motion, energization or safety credit is authorized.

**PRELIMINARY - NOT APPROVED FOR PROCUREMENT, ASSEMBLY, WIRING, OR ENERGIZATION.**
