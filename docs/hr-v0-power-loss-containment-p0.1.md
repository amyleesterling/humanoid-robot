# HR-V0 passive power-loss containment P0.1

**PRELIMINARY - NOT APPROVED FOR FABRICATION, MOTION OR ENERGIZATION**

Document ID: `HR-V0-POWERLOSS-P0.1`

Date: 2026-08-08

Gate: `EG-009` remains `partial`

## Decision

HR-V0 shall not depend on actuator holding torque, gearbox friction, software, `DF-01`, a controlled stop, cable tension or an operator to remain safe after drive-energy loss. The selected strategy is passive containment: a fixed inaccessible guard, a fixed receiver that supports the arm and gripper throughout their collapse envelope, a separate object catch, released bidirectional hard stops, and restart prevention.

This decision selects a protection strategy, not a receiver design. Exact receiver material, geometry, retention, energy factor, allowed travel, reaction force, rebound, final resting envelope and proof method remain `SELECTION REQUIRED`.

`HR-V0-COLLAPSE-ENV-P0.1` subsequently proves that the existing P0.3 floor tray is 114 mm below the controlled arm envelope. That tray is the object catch only and cannot satisfy the passive arm-receiver requirement.

## Conservative gravitational input

The current moving-mass ledger allocates exactly `750 g` across five unique buckets and records a maximum shoulder radius of `360 mm`. Without relying on the current joint limits or a particular collapse path, any point contained within that radius can change height by no more than the sphere diameter:

```text
vertical excursion bound = 2 × 0.360 m = 0.720 m
gravitational potential bound = 0.750 kg × 9.80665 m/s² × 0.720 m
                              = 5.295591 J
```

For the permitted `100 g` foam object alone, the same geometric bound is `0.706079 J`. An ideal point-mass free-fall screen over `0.720 m` is `3.758 m/s`; that value is not a predicted link speed, contact speed or receiver input.

The `5.295591 J` value is deliberately conservative with respect to pose geometry but incomplete as an impact case. It excludes:

- continued motor drive;
- electrical regeneration and rail-decay behavior;
- elastic energy;
- receiver compliance and damping;
- joint/link inertia distribution;
- detached hardware;
- cable loads;
- uncertainty and an accepted design/proof factor; and
- secondary contact and rebound.

It is therefore a configuration-allocation input only. It is not a guard rating, receiver rating, proof energy, allowable load or permission to fabricate.

## Required passive chain

1. Either actuator energy disappears or a torque-off condition occurs.
2. J1, J2 and the gripper are assumed able to move; no holding behavior is credited.
3. The fixed guard prevents access to the full collapse, pinch and rebound region.
4. The fixed arm receiver and separate object catch contain all moving items without control power.
5. The final resting state is stable, supported and inaccessible.
6. Restoring power cannot resume the interrupted trajectory. Recovery returns through physical `RESET`, a distinct later `ARM`, and a fresh validated trajectory.

`power-loss-strategy.csv` records this chain item by item. Continued-drive faults remain a separate `HR-V0-GUARD-IMPACT-P0.1` case and may not use the gravitational-only energy value.

## Physical evidence scaffold

The blank test form contains `72` cases:

- a `3 × 3` grid over J1 `-20/25/70 deg` and J2 `15/65/115 deg`;
- empty-open and maximum-foam-payload states; and
- E-stop demand, actuator-source loss, control-power loss and bus-watchdog torque-off causes.

Every row is `NOT EXECUTED` and `NOT AUTHORIZED`. The grid is a fixture/test scaffold, not proof of every pose. Closure additionally requires accepted continuous as-built collapse-envelope coverage, selected instrumentation, calibrated force/travel/video channels, exact energy-removal methods, a protected test sequence, deviation control and qualified witnesses.

The tests shall record rail decay, final joint positions, maximum point travel, receiver contact and travel, peak force, rebound, object escape, accessible hazards, cable/connector damage, structural/guard damage and restart behavior.

## Closure conditions

`EG-009` may close only after all of the following are accepted for one immutable configuration:

- complete as-built mass, center of mass and inertia;
- all four bidirectional J1/J2 physical boundaries and the gripper passive behavior;
- continuous collapse and rebound envelope inside the fixed guard;
- exact receiver/catch CAD, material, retention and load path;
- accepted gravitational, continued-drive, stored-energy, regeneration and detached-part cases;
- receiver force, travel, energy and rebound acceptance limits with uncertainty;
- guard access and final-rest/recovery assessment;
- execution and approval of the physical records; and
- qualified mechanical and safety review.

No physical evidence exists in this package. `EG-009` remains `partial`.

## Controlled artifacts

- `safety/hr-v0-power-loss-containment-p0.1/power-loss-energy-bound.csv`
- `safety/hr-v0-power-loss-containment-p0.1/power-loss-strategy.csv`
- `tests/forms/hr-v0-power-loss-containment-template-p0.1.csv`
- `release/hr-v0/power-loss-containment-p0.1/index.html`
- `tools/generate_hr_v0_power_loss_containment.py`
- `tools/check_hr_v0_power_loss_containment_p01.py`

The calculation inputs come from the project-controlled `bom/hr-v0-moving-mass-ledger.csv`. This package asserts no new manufacturer product behavior or rating.
