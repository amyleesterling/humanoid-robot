# HR-30B release specification — supported full body

Document ID: HR-REL-30B  
Revision: 0.1  
Status: future gate; detailed design not released

## Capability earned

A complete 25-axis maximum humanoid body is assembled for restrained integration and individual leg-joint qualification without claiming standing or walking.

## Included configuration

- The released HR-30A upper body plus two six-axis legs.
- Hip yaw, hip roll, hip pitch, knee pitch, ankle pitch, and ankle roll per leg.
- Engineered overhead restraint or rigid support frame that prevents floor impact and carries the robot whenever required.
- Leg joints unpowered or mechanically locked until individually qualified.

## Entry conditions

- HR-30A acceptance is approved.
- Full-body CAD, mass properties, collision envelope, harness motion envelope, and restraint attachment load path are released.
- The restraint analysis defines proof load, attachment hardware, travel, clearances, and inspection intervals.

## Acceptance criteria

- The complete restraint path is proof tested without the robot at no less than five times as-built robot weight and the approved analysis value.
- The assembled body remains within the 740–800 mm configuration envelope and 10.0 kg absolute mass ceiling.
- Every leg axis has signed load, thermal, current, power-loss, brake/lock, joint-limit, cable-clearance, and fault-injection evidence before it is enabled.
- Kinematics, joint polarity, sensor identity, bus segmentation, and physical/software configuration reconcile.
- The restraint or support frame prevents floor impact throughout the full released swept volume.

## Required evidence

Approved T9 records including TEST-RESTRAINT-001, AUDIT-LEG-001 for all twelve leg axes, full-body mass and dimension records, CAD interference review, and configuration audit.

## Boundary

HR-30B does not claim powered stance, weight transfer, dynamic gait, untethered operation, or operation around people.
