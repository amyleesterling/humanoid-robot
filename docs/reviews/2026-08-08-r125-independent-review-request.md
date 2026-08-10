# Independent review request - HR-V0 passive power-loss containment P0.1

Please review `HR-V0-POWERLOSS-P0.1` as a conservative strategy/allocation package, not a receiver design or motion release.

Status: **PRELIMINARY - NOT APPROVED FOR FABRICATION, MOTION OR ENERGIZATION**

## Reproduce

```powershell
& 'C:\Users\amyle\Documents\New project\.venvs\hr-v0-cad\Scripts\python.exe' tools/check_hr_v0_power_loss_containment_p01.py
```

## Review questions

1. Does summing unique ledger allocation buckets reproduce exactly `0.750 kg`?
2. Does the controlled ledger reproduce a `0.360 m` maximum shoulder radius?
3. Is `2r = 0.720 m` a valid configuration-independent upper bound on vertical point excursion for the controlled radius sphere?
4. Does `m g 2r` reproduce `5.295591 J` with `g = 9.80665 m/s²`?
5. Are the exclusions sufficiently explicit to prevent treating this result as an impact rating or receiver proof energy?
6. Is zero credit assigned consistently to actuator hold, friction, software, `DF-01`, controlled stop, cable tension and operator action?
7. Does the selected passive chain cover shoulder, elbow, gripper, object, final rest and restart without claiming that the current guard/receiver implements it?
8. Are the 72 blank cases useful, and what continuous analysis or additional pose/cause cases are required?
9. Do the receiver design holds capture energy factor, travel, reaction, rebound, load path, access, uncertainty, recovery and physical proof?
10. Does `EG-009` correctly remain `partial`?

Provide BLOCKER / MAJOR / MINOR findings with exact file, row, equation, gate and evidence references. State separately whether the package is ready for qualified mechanical review, physical power-loss testing, fabrication, motion or energization. Do not infer approval from passing checks.

## Controlled artifacts

- `docs/hr-v0-power-loss-containment-p0.1.md`
- `safety/hr-v0-power-loss-containment-p0.1/power-loss-energy-bound.csv`
- `safety/hr-v0-power-loss-containment-p0.1/power-loss-strategy.csv`
- `tests/forms/hr-v0-power-loss-containment-template-p0.1.csv`
- `release/hr-v0/power-loss-containment-p0.1/index.html`
- `tools/generate_hr_v0_power_loss_containment.py`
- `tools/check_hr_v0_power_loss_containment_p01.py`
- `bom/hr-v0-moving-mass-ledger.csv`
