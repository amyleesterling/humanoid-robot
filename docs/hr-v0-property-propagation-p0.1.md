# HR-V0 accepted-property propagation and stale-analysis control P0.1

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Identifier: `HR-V0-PROP-PROPAGATION-P0.1`

Round: R249

State: fail-closed propagation contract; no accepted property bundle

## Correction

R248 defines how physical mass, center of mass and inertia will be measured. R249 controls what must happen next. It prevents historical planning screens from being silently reused after an as-built configuration exists and defines one canonical, hash-bound input bundle for every downstream mechanical, stopping, containment, duty and control analysis.

The current incomplete gravity envelope, stop-load sensitivity, impact-energy, power-loss, stopping-time, actuator-duty and firmware-limit artifacts remain useful historical or planning evidence. They are not accepted release inputs.

## Fail-closed compiler

`tools/compile_hr_v0_accepted_properties_p01.py` requires exactly six configuration/axis rows:

- `CFG-MP-01/J2`;
- `CFG-MP-02/J1`;
- `CFG-MP-03/J1` and `CFG-MP-03/J2`; and
- `CFG-MP-04/J1` and `CFG-MP-04/J2`.

Every row must be `EXECUTED` and `ACCEPTED`, carry positive mass and inertia, nonnegative COM radius and expanded uncertainties, exact configuration/evidence SHA-256 identities, an approver and an acceptance-record URI. Axis rows for one configuration must share the same configuration hash. The current blank template returns exit code 78.

A successful future compile establishes only accepted physical-property identity. It deliberately keeps procurement, fabrication, assembly, connection, powered testing, motion, energization and safety credit false. Each downstream analysis still requires its own method, additional inputs, uncertainty, independent check and qualified acceptance.

## Controlled propagation

Twelve consumers are enumerated:

1. J1 gravity/static torque;
2. J2 gravity/static torque;
3. J1 acceleration torque;
4. J2 acceleration torque;
5. rotational stopping energy;
6. hard-stop load and energy;
7. guard/catch impact;
8. power-loss collapse/receiver behavior;
9. joint, fastener, plate and anchor structure;
10. continuous/cyclic actuator duty;
11. firmware pose/rate/acceleration limits; and
12. the qualified motion-test matrix.

The rebuild order starts with the accepted bundle and coordinate-frame reconciliation, then regenerates gravity, dynamic, duty, stopping, contact, structure and containment evidence before firmware limits or physical motion testing can be accepted.

## Boundary

No physical property has been accepted. No downstream analysis has been regenerated. Twelve package holds and ten acceptances remain open. Sol B-010, B-011 and B-013 remain open; affected energization and motion gates remain partial.
