# HR-V0 Boston/US custom-metal route P0.3

> **PRELIMINARY - NOT APPROVED FOR QUOTATION, FABRICATION, ASSEMBLY, MOTION, OR ENERGIZATION.**

Identifier: `HR-V0-BOSTON-FAB-ROUTE-P0.3`

Review round: R167
Date: 2026-08-09

## Result

The five controlled custom parts remain technically plausible conventional CNC work, but no provider is qualified and no external action is authorized. This refresh corrects the local route ranking and makes the missing low-load design inputs explicit.

- **Kontrast4D, Salem MA** has the strongest published Boston-area capability evidence: multi-axis CNC, numerical tolerance bands, CMM equipment and FAI availability. It has not confirmed Project Button's exact `6061-T651`, 9.525 mm stock, full drawing set, C07 surface map or every operation.
- **Protolabs** is the strongest published exact-material online route because its official aluminum page lists `6061-T651`; C06/C07 high-requirement controls still need manual acceptance.
- **Xometry** remains an online alternate; its network, exact supplier, T651 stock and tight-control acceptance remain unknown.
- **Fictiv** and **SendCutSend** do not close the controlled T651 requirement on their published pages. SendCutSend remains excluded as a finished-part route.

No statement here is a supplier selection, purchase recommendation, quote request or fabrication release.

## Controlled part requirements

All five parts require bare as-machined `6061-T651`, nominal 9.525 mm stock, finished thickness 9.00 to 10.00 mm, flatness no more than 0.15 mm, parallelism no more than 0.10 mm and the controlled edge break. C01/C04 use the controlled 11.30 +0.10/-0.00 mm countersink; C05 carries the relative interface datum chain; C06 carries twin rail datums at +/-0.025 mm; C07 carries the 1.00 +/-0.05 mm step and rail coplanarity no more than 0.03 mm.

These are project requirements from the controlled geometry package, not claims that a provider has accepted them.

## Why “not strong” is not a numerical requirement

The user intent is a light-duty demonstrator. It is recorded that way, but it cannot replace a maximum payload, motion profile, duty cycle, restraint/fall load cases or safety factors. Those inputs govern part stress, the C05 T-slot joint, C06/C07 stop impact and first-article acceptance. `open-design-inputs.csv` keeps all ten inputs fail-closed until measured or accepted evidence exists.

## Next controlled sequence

1. Qualified mechanical review accepts the numerical load cases and drawing controls.
2. Configuration authority issues a separate capability-only inquiry to one local and one online candidate. No geometry upload or portal order may occur automatically.
3. The provider confirms exact material/MTR, every controlled feature, inspection instruments, CMM report and surface-map format in writing.
4. A separate one-piece-per-geometry first-article authorization is issued.
5. Received articles remain quarantined until the controlled FAI and physical joint/fit tests pass.

## Artifacts

- `release/hr-v0/boston-fabrication-route-p0.3/route-comparison.csv`
- `release/hr-v0/boston-fabrication-route-p0.3/source-register.csv`
- `release/hr-v0/boston-fabrication-route-p0.3/open-design-inputs.csv`
- `release/hr-v0/boston-fabrication-route-p0.3/package-status.json`
- `release/hr-v0/boston-fabrication-route-p0.3/index.html`
- `tools/check_hr_v0_boston_fabrication_route_p03.py`

The prior P0.2 route is retained as historical evidence. P0.3 supersedes its provider ranking but does not relax any geometry, material, inspection or authorization hold.

**PRELIMINARY - NOT APPROVED FOR QUOTATION, FABRICATION, ASSEMBLY, MOTION, OR ENERGIZATION.**
