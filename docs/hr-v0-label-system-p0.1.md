# HR-V0 panel identification system P0.1

**PRELIMINARY - NOT APPROVED FOR PROCUREMENT, PRINTING, INSTALLATION, WIRING, OR ENERGIZATION**

Identifier: `HR-V0-LABEL-P0.1`

Review round: R169

Date: 2026-08-09

## Result

R169 corrects a physically misleading marker definition and freezes a reviewable panel-identification candidate:

- XT1 uses six short terminal markers, `01` through `06`, on Phoenix Contact `UCT-TM 5` item `0828734` stock. The old strings such as `XT1-03 / SR1 STATUS` do not fit the manufacturer-published `4.6 x 10.5 mm` text field and are superseded.
- A separate adhesive device marker identifies the group as `XT1`; the complete position-to-net mapping stays in the terminal schedule and ECAD, where it remains readable.
- Thirty panel/source device-reference labels and four operator legends use exact-candidate Phoenix Contact `US-EMLP (17.5X15)` item `0830839` stock. The configured 34 markers fit on one 45-marker card, but the manufacturer-published ten-card minimum order is not a purchase authorization.
- Four large status/configuration legends use exact-candidate Phoenix Contact `US-EMLP (60X30)` item `0828805` stock, exactly filling one four-marker card. Its ten-card minimum order is likewise not a purchase authorization.
- Terminal text, device references and legend wording are now configuration controlled. Printer or marking service, ribbon/cartridge, artwork file, font, placement, substrate preparation, adhesion, wire-marker system, code-required hazard labels, physical inspection and qualified acceptance remain open.

`BOM-062` advances from an undifferentiated selection-required group to an `exact_candidate_hold` for these three material stocks and the controlled printed-text schedule. That state does not release complete machine labeling: wire markers and jurisdiction-required labels remain `SELECTION REQUIRED`.

## Controlled files

- `electrical/panel/hr-v0-label-system-p0.1/terminal-marker-schedule.csv`
- `electrical/panel/hr-v0-label-system-p0.1/device-marker-schedule.csv`
- `electrical/panel/hr-v0-label-system-p0.1/large-legend-schedule.csv`
- `electrical/panel/hr-v0-label-system-p0.1/source-register.csv`
- `electrical/panel/hr-v0-label-system-p0.1/open-holds.csv`
- `electrical/panel/hr-v0-label-system-p0.1/package-status.json`
- `release/hr-v0/label-system-p0.1/index.html`
- `tools/check_hr_v0_label_system_p01.py`

## Primary-source boundary

Phoenix Contact currently publishes:

- [UCT-TM 5, item 0828734](https://www.phoenixcontact.com/en-us/products/terminal-marking-uct-tm-5-0828734): white 5.2 mm-pitch latching terminal markers, 72 per sheet, with a `4.6 x 10.5 mm` text field.
- [US-EMLP (17.5X15), item 0830839](https://www.phoenixcontact.com/en-us/products/device-marking-us-emlp-175x15-0830839): white adhesive PVC device markers, 45 per card, with a `17.5 x 15 mm` field.
- [US-EMLP (60X30), item 0828805](https://www.phoenixcontact.com/en-us/products/device-marking-us-emlp-60x30-0828805): white adhesive PVC device markers, four per card, with a `60 x 30 mm` field.

Those manufacturer facts establish catalog identity and physical label fields only. They do not approve the Project Button text, typography, warnings, adhesion, environment, human factors, installed position or regulatory sufficiency.

## Release boundary

All twelve holds remain open. Passing the checker proves only digital schedule consistency. It does not prove that a printed label fits, remains legible, adheres, survives cleaning, communicates safely, matches installed wiring or satisfies Boston/US marking obligations.

`EG-003` and `EG-015` remain partial. No gate closes.

**PRELIMINARY - NOT APPROVED FOR PROCUREMENT, PRINTING, INSTALLATION, WIRING, OR ENERGIZATION.**
