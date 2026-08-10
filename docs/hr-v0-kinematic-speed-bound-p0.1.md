# HR-V0 conservative kinematic speed bound P0.1

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Artifact: `HR-V0-KIN-P0.1`

Configuration: `HR-V0-SUP-P0.3` / `HR-V0-FRAME-CONV-P0.1` / `HR-V0-MECH-P0.6`

Review/control round: R197

## Correction

The supervisor required a kinematic-model hash but no repository implementation could calculate the configured TCP-speed constraint. R197 adds a conservative planar rate bound for the current parallel J1/J2 +X axes and binds it to the controlled frame and mechanical revisions.

The current nominal transform register gives J1-to-J2 as 202.550 mm and J1-to-H104 as 331.600 mm. The candidate therefore derives J2-to-H104 as 129.050 mm. Complete H104-to-tool reach remains `SELECTION REQUIRED` because the gripper/TCP selection, tolerance and received geometry are unresolved.

For joint rates in radians per second, the source evaluates:

`v_bound = |w_J1| (L_J1J2 + L_J2H104 + L_H104TCP) + |w_J2| (L_J2H104 + L_H104TCP)`

This uses the triangle inequality. It never subtracts one joint contribution from another, so favorable joint-angle or rate cancellation cannot reduce the bound. Gripper opening rate does not translate the H104 tool point and is handled separately by the gripper speed limit.

## Fail-closed binding

The repository configuration cannot construct the validator. Construction requires all of the following:

- exact artifact, model-type, frame and mechanical identifiers;
- exact current 202.550 mm and 129.050 mm link inputs;
- a finite nonnegative selected H104-to-tool reach;
- release state `ACCEPTED-FOR-GUARDED-HIL`;
- an exact SHA-256 acceptance-evidence hash; and
- an exact SHA-256 model hash matching the canonical configuration block.

`Supervisor.from_json()` obtains the validator from the same configuration object. The committed `SELECTION REQUIRED` values therefore cause constructor refusal before motion authority exists.

## Executable evidence

Nine kinematic tests cover repository refusal, exact model hashing, zero rate, the triangle bound, rate-sign symmetry, gripper-rate separation, exact axis sets, nonfinite values and hash substitution. Existing supervisor tests now use an internally consistent accepted fixture rather than an arbitrary placeholder validator hash.

## Remaining evidence

The source does not establish the actual TCP, tolerance, deflection, calibration, backlash, controller timing, as-built geometry or physical speed. The 0.150 m/s setting remains a candidate, not an accepted safe speed. Complete gripper/tool selection, metrology, model-to-measurement comparison, guarded HIL, stopping evidence, independent controls review and qualified mechanical/functional-safety disposition remain open. The ordinary supervisor receives zero functional-safety credit. No finding, requirement or energization gate closes.
