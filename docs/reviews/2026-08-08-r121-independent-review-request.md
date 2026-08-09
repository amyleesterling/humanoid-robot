# R121 independent review request

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TEST, OR ENERGIZATION.**

Review target: `HR-V0-CP-P0.6` / `HR-V0-COMPUTE-INSTALL-P0.1` against Electrical `V3-P1.14`.

This requests an accuracy and completeness review, not approval to buy, drill, assemble, wire, power or energize anything.

## Review scope

1. Verify from current primary manufacturer records the identities and stated facts for Hammond `PJ302410RT` / `18P2721`, Waveshare `PI5-CASE-D` SKU `26087`, ROBOTIS U2D2 `902-0132-000`, HellermannTyton `GTM500C2` article `130-95000`, and `GT.50X80C2` article `854-44353`.
2. Challenge the decision to supersede P0.5 with the larger enclosure/backplate pair, including overall size, mass/support, service access, door controls and appropriateness for a guarded Boston makerspace prototype.
3. Recalculate all 26 two-dimensional envelope boundaries and check the WD2 segregation claim, compute-column spacing and lower reserve.
4. Determine whether the Waveshare case really supports Raspberry Pi `SC1112` plus official Active Cooler `SC1148` with the supplied hardware, without inferring screw/standoff details from unlabeled images.
5. Challenge use of GTM/Grip Tie products for rigid U2D2 retention. Define the missing compression, slip, vibration, abrasion, pull, connector-load and repeated-service acceptance evidence; do not invent acceptance values.
6. Verify that the current U2D2 Type-C change is represented correctly and that `BOM-070` remains open for host connector, length, shield/conductor construction and OD.
7. Review metal-case/steel-panel/DIN-rail bonding, compute-return/actuator-return coupling, shields, PE/DC 0 V treatment and no-damage measurement requirements against the current grounding package.
8. Review depth, port access, cable bends, entry fittings, duct fill, separation, blocked-fan behavior, simultaneous losses and closed-enclosure temperature-rise evidence.
9. Compare BOM, closure register, panel BOM, layout CSV, thermal/space screen, receiving template, SVG, web guide, current handoff and release metadata for consistency.
10. State separately whether the package is ready for qualified mechanical, electrical, enclosure-system, EMC and functional-safety review. Do not state that it is ready for fabrication or energization without executed evidence and separate authorization.

Report `BLOCKER` / `MAJOR` / `MINOR` findings with the exact file, row/reference, manufacturer source revision/date, risk, proposed correction and evidence needed to close it. Preserve every preliminary warning and mark every unsupported pin, rating, fastener, cable, hole or acceptance value `SELECTION REQUIRED`.

## Controlled files

- `docs/hr-v0-control-panel-p0.6.md`
- `electrical/panel/hr-v0-control-panel-p0.6/`
- `bom/bom.csv`
- `bom/hr-v0-bom-closure.csv`
- `tests/forms/hr-v0-compute-installation-receiving-template-p0.1.csv`
- `release/hr-v0/compute-installation-p0.1/index.html`
- `tools/check_hr_v0_compute_installation_p01.py`

Reproduction:

```powershell
python tools/generate_hr_v0_bom_closure.py
python tools/check_hr_v0_compute_installation_p01.py
python tools/check_energization_gates.py --through-stage E2 --require-ready
```

The readiness command is expected to exit `2` while all E0-E2 gates remain partial.
