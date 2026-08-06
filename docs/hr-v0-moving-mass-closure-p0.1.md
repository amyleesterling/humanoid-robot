# HR-V0 Moving-Mass Closure P0.1

**PRELIMINARY - MASS LEDGER AND SCREEN ONLY. NOT A FABRICATION OR ENERGIZATION RELEASE.**

Date: 2026-08-06

Requirement: `MASS-002`

Controlled ledger: `bom/hr-v0-moving-mass-ledger.csv`

Measurement record: `tests/forms/hr-v0-moving-mass-measurement-template.csv`

## Configuration boundary

The HR-V0 moving-assembly ceiling is 750 g, excluding the fixed J1 actuator, shoulder adapter, column, base and bench anchors. The moving configuration includes every item that rotates about J1: both link plates, J1/J2 moving frames and idlers, the J2 actuator/body-frame assembly, the gripper actuator and mechanism, all moving fasteners/stops/guides/connectors/cable shares, and the maximum 100 g payload.

No item may be omitted because it was supplied in a kit, modeled as a massless envelope, attached near a joint axis, or allocated to electrical rather than mechanical work. Each item appears exactly once in the ledger.

## Current reproducible subtotal

| Known item | Basis | Mass |
|---|---|---:|
| `MV0-001` upper-link plate | generated CAD volume at 2.70 g/cm3 | 109.2 g |
| J2 `XM540-W270-T` actuator | current ROBOTIS e-Manual | 165.0 g |
| `MV0-002` forearm plate | generated CAD volume at 2.70 g/cm3 | 109.2 g |
| gripper `XM430-W350-T` actuator | current ROBOTIS e-Manual | 82.0 g |
| maximum permitted payload | system requirement | 100.0 g |
| **Known subtotal** |  | **565.4 g** |
| **Unresolved headroom to 750 g** |  | **184.6 g** |

The known subtotal already consumes 75.4% of the ceiling. The remaining 184.6 g must cover two moving H101 frame/idler assemblies, one S102 frame, all frame/link/gripper fasteners and spacers, the complete gripper mechanism and pads, J2 moving stop hardware, cable guides, strain relief, connectors and every moving cable segment.

This is not a pass. The current 120 g upper-link and 120 g forearm allocation buckets each contain a 109.2 g plate, leaving only 10.8 g per bucket for their H101/frame/fastener/harness content. Those suballocations are not credible until measured; the system may need thinner/lighter link geometry or a controlled regrouping supported by the final torque, stiffness and impact calculations.

## Source status

The ROBOTIS XM540-W270 and XM430-W350 e-Manual pages were rechecked 2026-08-06 and report 165 g and 82 g respectively. Received-device mass still governs the measured ledger. Frame and kit-content pages do not provide controlled component masses, and material shall not be inferred from appearance or STEP volume.

CAD masses are estimates until stock alloy/temper, actual thickness, finish and measured first-article mass are recorded. The calculation must be rerun whenever hole geometry, material, gripper, cable route, stop part or fastener changes.

## Closure procedure

1. Freeze the exact configuration and repository commit.
2. Execute `INSPECT-MECH-005` for received frame-kit identity and contents.
3. Execute `INSPECT-MECH-007` using a calibrated scale and the controlled 13-row measurement form.
4. Record measured mass with uncertainty for every separate part, then repeat for each assembled moving subassembly as a cross-check.
5. Determine local center of mass and inertia using a released CAD or physical method; preserve raw measurements and coordinate transforms.
6. Reconcile component totals to assembly measurements within the released uncertainty. Investigate rather than distributing unexplained error.
7. Update the gravity, torque, stop-impact and receiver/drop calculations from the same immutable mass configuration.
8. Run `REVIEW-MASS-002`; pass only if the measured moving assembly including the 100 g test payload is no more than 750 g and every item is included once.
9. Obtain qualified mechanical review before torque/current limits or proof loads use the closed ledger.

No supplier estimate, CAD value or unused allocation is permission to substitute an unweighed component.
