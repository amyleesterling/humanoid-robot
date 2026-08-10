# R183 independent review request

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION.**

Review exact artifact **HR-V0-Q4X-IF-P0.1** at the supplied commit. Treat the native repository as authoritative and the web guide as presentation only.

## Required checks

1. Verify the exact identities and current official sources for `Q4XFULAF110-Q8/97540`, `BC-M12F5-22-2-SF/815158`, `SMBQ4XFA/91512`, `2220-30-1`, `TIVP02` and `TIVPMX10X`.
2. Reconcile Banner's product-page/manual discrepancy for the bracket bolt length without inference.
3. Check every proposed Q4X pin/color/function, the remote-input parking boundary, analog pair and shield hold.
4. Confirm the temporary Q4X domain has no proposed connection to robot `SAFETY_24V`, `SAFETY_0V`, PE/chassis, E-stop, reset, watchdog, contactor, actuator or DXL circuits.
5. Determine whether the `2220-30-1` isolation and control architecture is correctly represented and identify any missing mains, output-floating, current-limit or protection evidence.
6. Check that 24.0 V is labeled only as a candidate and that the current limit, protection, terminals, conductors and enclosure remain `SELECTION REQUIRED`.
7. Review the exact cordset for received continuity, shield, bend, retention, strain relief and route obligations.
8. Review the bracket/support/target geometry and confirm no target has been silently selected.
9. Review the proposed calibration campaign, response/averaging alternatives, warm-up requirement, uncertainty chain and prohibition on using a catalog value as the no-motion limit.
10. Confirm every physical result, connection, safety credit and work authority remains absent.
11. Compare the Markdown document, all CSV registers/forms, JSON status, interactive guide, gate supplement, generator and checker for exact consistency.
12. Classify every issue as BLOCKER / MAJOR / MINOR with exact file and row/field references.

## Explicit questions

- Is any wire, terminal, shield, protection or supply setting phrased as released rather than a review candidate?
- Does any boundary permit common-mode, backfeed or PE coupling that the package fails to control?
- Is `SMBQ4XFA` an appropriate bracket candidate while its included-bolt discrepancy remains held?
- Is the screened-but-not-selected target disposition appropriately conservative?
- Does the calibration plan contain enough evidence to support a later qualified no-motion limit without claiming one now?

Do not approve procurement, fabrication, connection, powered testing, motion, energization or functional safety.
