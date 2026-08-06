# HR-30 Preliminary Load and Power Budget

**PRELIMINARY—NOT APPROVED FOR ENERGIZATION**

Status: feasibility and correction model only. It is not a procurement, fabrication, or walking release. Walking hardware shall not be selected from this document alone.

Revision note: the R11 correction pass records failed mass allocations, blocks direct-drive hip roll, and reopens the actuator rail, battery, and tether architecture. Controlled arithmetic and sources are in [R11 engineering calculations](r11-engineering-calculations.md).

## Mass budget and failed-closure warning

| Assembly | Target | Maximum | R11 disposition |
|---|---:|---:|---|
| Head and neck | 0.45 kg | 0.55 kg | not closed |
| Chest, compute, and waist | 1.20 kg | 1.35 kg | not closed |
| Two complete arms and hands | 1.30 kg | 1.50 kg | **current candidate set fails allocation** |
| Pelvis and restraint structure | 0.65 kg | 0.75 kg | not closed |
| Two legs and feet | 3.40 kg | 3.80 kg | **current concept fails independent screening** |
| Wiring, covers, fasteners, margin | 0.60 kg | 0.80 kg | not closed |
| HR-30W onboard energy storage | 0.40 kg development allowance | 1.25 kg | chemistry and architecture `SELECTION REQUIRED` |
| **Total** | **8.00 kg** | **10.00 kg** | **not demonstrated** |

The target column is an aggressive allocation, not an as-built property. The maximum column sums to the 10.0 kg absolute ceiling, but separate maxima cannot be consumed independently without closing the total.

The current arm candidate count is six 165 g XM540 units plus four 82 g XM430 units. The actuators alone total 1.318 kg. That is already 18 g above the 1.30 kg target and leaves only 182 g below the 1.50 kg maximum for every arm link, bearing, shaft, fastener, gripper, cable, and cover. The current arm architecture therefore fails the allocation; actuator adequacy does not establish arm feasibility.

Twelve 165 g XH540 leg actuators alone total 1.980 kg. An independent review then screened the two-leg assembly at approximately 4.5–4.9 kg after adding provisional reductions, bearings, structure, feet, and harness. Those added values are review assumptions, not released part selections or controlled CAD mass properties. They nevertheless show that the 3.40/3.80 kg allocation is not credible until a supplier-backed part ledger and CAD roll-up prove otherwise. No joint sizing or walking claim may use 8.0 kg as an as-built fact.

## Controlled mass and inertia ledger

Before any full-body CAD freeze, a controlled ledger shall contain one row for every part, cable, connector, fastener, cover, adhesive, lubricant, battery element, and restraint attachment:

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

Target, estimate, and measured values may never be collapsed into one column. The ledger shall roll up by link and assembly, publish whole-robot center of mass and inertia, and preserve the exact configuration used by simulation and controls.

A 15–20% unallocated design reserve has been proposed by independent review. Whether that reserve sits inside the 8.0 kg target and how it is released remain `SELECTION REQUIRED`. Gate G-20 cannot close on the current allocation table.

## Fall energy

At the 8 kg target and 0.41 m nominal center-of-mass height:

`E = m g h = 8 × 9.80665 × 0.41 = 32.2 J`

At the 10 kg/0.46 m hard limits, the corresponding energy is 45.1 J. These are configuration-screening values, not proof that either mass or center-of-mass height has been achieved. Full-height testing requires an independently reviewed restraint that prevents the head or limbs reaching the floor and is rated from the measured robot mass and credible dynamic arrest load. The earlier phrase “5× robot weight” is not, by itself, a restraint specification.

## Upper-body actuator loading

The V0 arm calculation remains the first physical test. HR-30 arms use similar reach but must meet a 0.75 kg-per-arm allocation. Shoulder gravity torque is expected in the 1.7–2.2 N·m range at full horizontal reach with the 100 g payload. Candidate stall torque is only a momentary ideal point; current, voltage at the actuator, duty cycle, temperature, structure, and the failed mass allocation govern acceptance.

Waist yaw sees little static gravity torque when vertical. Its sizing is governed by upper-body inertia, cable drag, and emergency stopping. HR-30A initially limits waist speed to 15 deg/s.

## Leg feasibility bounds

The corrected load screening uses both the 8 kg target and 10 kg ceiling and does not treat stall torque as continuous capability.

- Ankle screening at a 40 mm center-of-mass offset is 3.14 N·m static at 8 kg and 3.92 N·m at 10 kg. Applying the existing 2× dynamic and 1.5× uncertainty factors gives 9.42 N·m and 11.77 N·m respectively.
- Hip-roll screening at a 62.5 mm lateral moment arm is 4.90 N·m static at 8 kg and 6.13 N·m at 10 kg. Applying a 2× dynamic factor gives 9.81 N·m and 12.26 N·m before any separate uncertainty factor.
- The XH540-W270 publishes ideal stall torque of 9.9 N·m at 12.0 V and 11.7 N·m at 14.8 V. Direct-drive hip roll has essentially no ideal margin at the 8 kg dynamic screen and does not meet the 10 kg screen even at 14.8 V. It is therefore **blocked**, not a baseline.
- The proposed 1.5:1 pitch-axis reduction yields 17.55 N·m ideal zero-speed joint stall at 14.8 V before efficiency loss. This is not a continuous or cyclic rating.

W0 shall evaluate hip yaw, hip roll, hip pitch, knee pitch, ankle pitch, and ankle roll through standing, weight transfer, single support, stepping, kneeling, rising, commanded stop, and credible disturbance cases. Closure requires measured cyclic torque/speed/temperature at the actual loaded rail voltage, verified reductions and losses, output-side load paths, measured mass properties, and gait trajectories. The original 35.3 N·m fall-capture case remains relevant to structure and restraint, not to a sustainable gait operating point.

## Power architecture by phase

| Phase | Actuator energy source | R11 design boundary |
|---|---|---|
| HR-V0 | 12 V bench supply candidate | existing two-contactor concept; protection and coordination unresolved |
| HR-30A | source and rail `SELECTION REQUIRED` | separately protected left arm, right arm, and head/waist domains; verified DC interruption required |
| HR-30B | supported joint-test source `SELECTION REQUIRED` | source must remain within actuator input limits under steady and transient conditions |
| HR-30C/D | managed development tether architecture `SELECTION REQUIRED` | compare low-voltage feed with higher-voltage tether plus on-robot conversion |
| HR-30W | chemistry, series count, converter, rail, and capacity `SELECTION REQUIRED` | select only after measured gait load and transient profiles |

The XH540-W270 input range is 10.0–14.8 V and its recommended voltage is 12 V. A nominal 4-series lithium-ion or LiPo pack reaches 16.8 V when full and therefore cannot directly feed this actuator rail. A nominal 4-series LiFePO4 pack may reach about 14.6 V, but loaded end-of-discharge voltage can reduce torque and speed. These examples are compatibility screens, not a chemistry selection. Any regulated architecture must close converter mass, efficiency, heat rejection, transient response, fault behavior, and regeneration handling.

Summed stall current is not an operating point or a released source current. Software motion budgets do not replace hardware fault protection. Every source, fuse, conductor, connector, contactor, precharge element, and service disconnect remains sized from controlled duty, inrush, fault-current, environment, and installation evidence.

## HR-V0 Mean Well coordination boundary

The current Mean Well LRS-350-12 manufacturer specification lists 12 V, 29 A, and 348 W. It lists overload protection at 110–140% of rated output power with hiccup-mode automatic recovery, a separate 150% peak-load allowance for up to one second, and 60 A typical cold-start input inrush at both 115 and 230 VAC. It does not publish the inrush pulse duration/T50, I²t, a quantified short-circuit time-current curve, or an LRS-350-specific external branch-protection selection.

Consequently, QF1 and the downstream F0/F1–F3 protection values remain `SELECTION REQUIRED`. Coordination must include measured or manufacturer-supplied source current-limiting behavior, prospective fault current, conductor and connector limits, cable length, ambient, bundling, duty cycle, inrush, interrupting rating, and jurisdiction. The LRS-350 output is not documented as an energy sink; a regeneration/clamp architecture and controlled-stop behavior under bus rise remain unresolved.

## Development tether boundary

The earlier tether-drop example assumed, only for screening, an 8 AWG conductor resistance of 2.1 mΩ/m, a 3–5 m one-way tether, and 80 A. The resulting 6–10 m loop is 12.6–21 mΩ, producing about 1.01–1.68 V drop. None of those values is a released conductor, length, connector, or current selection.

The tether design shall compare low-voltage high-current distribution with a higher-voltage tether and on-robot conversion. Electrical closure requires maximum/continuous current, source regulation, allowed actuator-terminal voltage, conductor temperature, connector/contact ratings, fuse coordination, transient drop, regeneration, PE/shield strategy, and jurisdiction. Mechanical closure requires mass per metre, bend stiffness, overhead support, drag force/moment across the workspace, strain relief, snag prevention, and fall-arrest separation.

All unresolved values remain `SELECTION REQUIRED`. This document does not authorize fabrication or energization.
