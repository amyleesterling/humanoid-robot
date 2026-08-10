# Sol R12 finding status after R68

> **PRELIMINARY—NOT APPROVED FOR FABRICATION OR ENERGIZATION.** This is a project-owned disposition, not an independent approval.

Independent review being dispositioned: Sol R12, including the resupplied summary reporting 18 BLOCKERS, 30 MAJOR findings, 8 MINOR findings, 62/62 draft requirements, 106 unresolved electrical selections, and zero executed approved verification records. The resupplied summary is the same R12 review and is not counted again.

Current correction round: R68

## Correction

R68 fixes a configuration mismatch introduced by the mechanical correction sequence: `HR-V0-ARM-ARCH-P0.6` allocated a 115° J2 software ceiling, while the active supervisor JSON still allowed 125°. `HR-V0-FW-P0.3`, `HR-V0-SUP-P0.2`, `HR-V0-ACT-P0.2`, and `HR-V0-DXL-TRANSPORT-P0.2` now bind command validation and engineering-to-raw conversion to the exact current mechanical identifiers and the 15°–115° J2 envelope.

Stale 120° limits, stale mechanical revisions, missing acceptance evidence, and commands above 115° are rejected in executable tests. The committed candidate deliberately records its mechanical limit as not released, so it remains unable to open the actuator transport or request motion.

## R12 disposition

This narrows the control-configuration portion of Sol’s motion-limit and evidence-chain findings. It does not close the need for physical hard-stop CAD, measured total stopping time/overtravel, calibration, backlash/compliance/tolerance/uncertainty, cable/guard clearance, received hardware, HIL, qualified functional-safety allocation, or any other R12 blocker. Sol’s overall verdict remains accurate: HR-V0 is not build-ready and energization remains prohibited under the current package.

No fabrication, connection, flashing, motion, or energization gate closed.
