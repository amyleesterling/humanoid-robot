# HR-30 Preliminary Load and Power Budget

Status: feasibility model only. Walking hardware shall not be selected from this document alone.

## Mass budget

| Assembly | Target | Maximum |
|---|---:|---:|
| Head and neck | 0.45 kg | 0.55 kg |
| Chest, compute, and waist | 1.20 kg | 1.35 kg |
| Two complete arms and hands | 1.30 kg | 1.50 kg |
| Pelvis and restraint structure | 0.65 kg | 0.75 kg |
| Two legs and feet | 3.40 kg | 3.80 kg |
| Wiring, covers, fasteners, margin | 0.60 kg | 0.80 kg |
| HR-30W onboard energy storage | 0.40 kg development allowance | 1.25 kg |
| **Total** | **8.00 kg** | **10.00 kg** |

The target column is an aggressive 8.0 kg walking budget, not an entitlement for every subsystem to consume its maximum. The maximum column sums to the 10.0 kg absolute ceiling. Twelve XH540-class leg actuators alone are approximately 1.98 kg before reductions, bearings, links, feet, sensors, and wiring, making leg mass the controlling CAD budget. HR-30A excludes onboard batteries; HR-30W requires the energy-storage allocation.

## Controlled mass and inertia ledger

The table above is allocation only. It is not mass closure. Before any full-body CAD freeze, a controlled ledger shall contain one row for every part, cable, connector, fastener, cover, adhesive, lubricant, battery element, and restraint attachment, with these fields:

| Required field | Meaning |
|---|---|
| configuration and revision | exact assembly and source revision |
| quantity and material | controlled BOM identity, not appearance |
| target mass | allocation before detailed design |
| current estimate | supplier value or CAD mass property with source |
| measured mass | calibrated-scale result when hardware exists |
| local center of mass | coordinates in the controlled robot datum system |
| inertia tensor | CAD or measured value and coordinate frame |
| evidence maturity | target, supplier, CAD, or measured |
| owner and approver | accountable engineering roles |

Target, estimate, and measured values may never be collapsed into one column. The model shall roll up by link and assembly, publish whole-robot center of mass and inertia, and preserve the exact configuration used by simulation and controls.

A 15 to 20 percent unallocated design-reserve policy has been proposed by independent review, but whether that reserve sits inside the 8.0 kg target and how it is released remain `SELECTION REQUIRED`. Until gate G-20 closes, the current table does not demonstrate mass closure and no actuator sizing may treat the 8.0 kg target as an as-built fact.

## Fall energy

At the 8 kg target and 0.41 m nominal center-of-mass height, gravitational potential energy is approximately:

`E = m g h = 8 × 9.80665 × 0.41 = 32.2 J`

At the 10 kg/0.46 m hard limits it is 45.1 J. This is sufficient to cause injury and equipment damage. Consequently, full-height testing requires a restraint that prevents the head or limbs reaching the floor and that is designed for at least 5× robot weight plus dynamic effects established by review.

## Upper-body actuator loading

The V0 arm calculation remains the governing first test. HR-30 arms use similar reach but must meet a 0.75 kg-per-arm mass allocation. Shoulder gravity torque is expected in the 1.7–2.2 N·m range at full horizontal reach with the 100 g payload. The candidate XM540-class shoulder has adequate stall-torque ratio on paper, but continuous current and temperature determine acceptance.

Waist yaw sees little static gravity torque when vertical; its sizing is governed by accelerating the upper-body inertia, cable drag, and emergency stopping. HR-30A initially limits waist speed to 15 deg/s.

## Leg feasibility bounds

During controlled single support, an 8 kg system with the center of mass held 40 mm from the ankle center produces about 3.14 N·m static ankle torque. A 2× dynamic factor and 1.5× uncertainty factor produce a 9.42 N·m screening value. A 150 mm offset would produce 11.8 N·m static torque and represents a fall-capture condition, not a sustainable gait pose.

The candidate XH540-W270-R publishes 11.7 N·m stall torque at 14.8 V. A 1.5:1 external reduction yields 17.6 N·m theoretical joint stall torque before losses, but continuous capability is not established by that number. The walking release requires measured continuous/cyclic performance at the actual duty cycle and an 8 kg-or-lower as-built mass.

The original 35.3 N·m fall-capture screening case remains relevant to structural proof and restraint design, but it is not the normal actuator operating point.

## Power architecture by phase

| Phase | Actuator rail | Design approach |
|---|---|---|
| HR-V0 | 12 V, 20 A protected maximum | one arm; existing two-contactor chain |
| HR-30A | 12 V, provisional 50 A source ceiling | separately fused left arm, right arm, head/waist groups; master safety disconnect sized for verified DC duty |
| HR-30B | 14.0–14.8 V leg test supply | supported joint-by-joint testing only |
| HR-30C/D | external current-limited 14.0–14.8 V tether | separately protected left leg, right leg, and upper-body domains |
| HR-30W | onboard 4-series protected battery | capacity and chemistry selected from measured gait profile |

Summed stall current is not a permissible operating point. Software budgets simultaneous motion, each joint has a characterized current limit, and hardware protection is sized for credible faults. HR-30A supply, contactors, connectors, and cable gauge must be reselected; V0 parts are not silently scaled up.
