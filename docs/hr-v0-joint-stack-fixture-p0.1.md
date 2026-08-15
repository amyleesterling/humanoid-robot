# HR-V0 zero-energy joint-stack fixture candidate P0.1

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

> **SUPERSEDED BY R253 / `HR-V0-JOINT-STACK-FIXTURE-P0.2`.** The six coplanar contacts in this record have constraint-matrix rank 3 and are prohibited for fixture fabrication or session use.

## Decision

R252 advances, but does not close, R251 hold `R251-H07` and joint-stack hold points `JSM-HP-004` and `JSM-HP-005`. It binds exact controlled ROBOTIS source geometry to a review-only six-contact fixture envelope and a fail-closed temporary-stack instruction. The package is not a manufacturing drawing, not a released fixture, and not authority to install hardware or begin a shop session.

## Source-bound geometry screen

The candidate assembly imports the controlled native STEP files for the XM540, FR13-H101K, and FR13-S102K. The S102 is transformed into the same nominal joint frame used by the integrated arm model. Six 2 mm-radius review envelopes are tangent to the transformed S102 outer face at nominal `Y=-51.500 mm`. Every contact envelope has at least `6.750 mm` nominal distance from the imported XM540 solid.

Those numbers are a deterministic nominal-CAD screen only. They do not account for received-part variation, coating, bracket deformation, contact compression, assembly tolerance, measurement uncertainty, or load. Contact material and maximum force remain `SELECTION REQUIRED`.

## Temporary-stack boundary

The twelve-step instruction requires all of the following before any threaded assembly:

- a verified zero-energy work area with no U2D2, actuator cable, or source-capable item present;
- received-article identity, inventory, loose-part dimensions, thread-depth, and screw-length evidence;
- a signed, configuration-bound selection of screw allocation, spacer placement, temporary torque, tooling, locking prohibition, and reuse/disposition;
- fixture first-article inspection and a physical proof that only the selected S102 face contacts engage;
- secondary restraint that prevents tip or escape without becoming a rotation stop;
- independent witness, accepted pose list, calibrated instruments, complete raw records, teardown inspection, and re-quarantine.

Every operation is `NOT EXECUTED`. A failed or missing prerequisite produces `STOP`, `NO ASSEMBLY`, `REMOVE FIXTURE`, or `QUARANTINE/NCR`; it never produces permission to improvise.

## Controlled artifacts

- [Interactive fixture guide](../release/hr-v0/joint-stack-fixture-p0.1/index.html)
- [Fixture source package](../test-fixtures/hr-v0/joint-stack-fixture-p0.1/)
- [Configuration reconciliation P0.16](../release/hr-v0/configuration-reconciliation-p0.16/index.html)
- [Independent review request](reviews/2026-08-11-r252-independent-review-request.md)

The package contains exact source hashes, STEP and GLB review assemblies, six contact records, six keepout rules, twelve selection records, twelve open holds, twelve unexecuted operations, and ten unexecuted acceptance criteria.

## Evidence still required

Closure requires received parts; selected fixture material, process, contact material, force, restraint, fasteners, tolerances, and datum scheme; a qualified mechanical/metrology review; fixture manufacture and dimensional first-article inspection; physical fit and keepout evidence; an accepted uncertainty budget; a signed temporary hardware/torque/reuse instruction; a separate written authorization for the exact zero-energy session; executed records; teardown inspection; and qualified disposition.

R252 closes no Sol blocker and grants no procurement, fabrication, assembly, test, motion, safety, or energization credit.
