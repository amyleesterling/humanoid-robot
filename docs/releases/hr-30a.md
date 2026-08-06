# HR-30A release specification — active upper body

Document ID: HR-REL-30A  
Revision: 0.1  
Program baseline: HR-30-SYS-R0.2  
Status: design baseline; detailed design not released

## Capability earned

A stationary 762 mm humanoid upper body performs guarded two-arm research motions from a bolted pelvic pedestal.

## Included configuration

- Thirteen active axes: head pan/tilt, waist yaw, two shoulder pitch/roll pairs, two elbow pitch axes, two wrist rotation axes, and two grippers.
- Bolted steel pedestal at the pelvis datum; lower-body appearance shells are non-load-bearing.
- External extra-low-voltage tethered actuator power with no onboard battery.
- Visible ready, setup, fault, and actuator-power-off states plus a hardware-driven camera privacy indicator.

## Entry conditions

- HR-V0 acceptance records are approved or every reused subsystem has equivalent evidence.
- The pedestal, pelvis interface, swept envelope, electrical distribution, and safety disconnect have approved designs and test procedures.
- Every actuator group has single-joint current, thermal, and fault limits.

## Acceptance criteria

- CAD, actuator IDs, software configuration, and physical inventory reconcile to exactly 13 active axes.
- Neutral height is 762 mm nominal and remains within 740–800 mm; tethered mass is at most 10.0 kg with an 8.0 kg target.
- Pedestal and primary structure pass proof testing; undefined lower-body axes remain mechanically locked.
- Tether polarity, strain relief, branch protection, and external actuator-energy isolation pass inspection and fault tests.
- Two-arm thermal/current budgets, visible states, privacy indication, joint limits, and guarded motion tests pass.

## Required evidence

Approved T7/T8 records including INSPECT-PROD-001 through INSPECT-PROD-003, INSPECT-PROD-002, TEST-MASS-001, TEST-ELEC-030, TEST-UI-001, TEST-PRIV-001, and configuration reconciliation.

## Boundary

HR-30A does not authorize powered legs, free standing, walking, onboard batteries, human contact, or operation around children.
