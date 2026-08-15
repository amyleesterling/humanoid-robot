# HR-V0 U2D2-to-JC1 controller harness P0.1

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

`HR-V0-U2D2-JC1-HARNESS-P0.1` converts the previously design-required `BOM-061` interface into an exact but unreleased two-conductor candidate.

## Exact candidate definition

- U2D2 cavity 1 `GND` to JC1 cavity 1 `CTRL_GND`: Belden `3051 BK005`, black, 22 AWG.
- U2D2 cavity 2 `VDD` to JC1 cavity 2 `NO_NET_NO_COPPER`: **no contact and no conductor at either end**.
- U2D2 cavity 3 `DATA` to JC1 cavity 3 `DXL_DATA`: Belden `3051 WH005`, white, 22 AWG.
- Two JST `EHR-3` housings and four `SEH-001T-P0.6` contacts, already allocated by BOM-054/055.
- One `500 +/- 5 mm` finished-length candidate, measured unloaded along the harness centerline between the rear wire-exit planes of the two housings.
- A project-owned `25 +/- 5 mm` pair-lay candidate and the Belden-published `15 mm` stationary minimum bend radius.
- JST `YRS-260` is the exact held hand-tool candidate for the selected strip-form contact. It is manufacturing equipment, not a robot BOM item.

The current planning-point Manhattan distance is `325.05 mm`; the 500 mm candidate leaves `174.95 mm` for route and service-loop accommodation. Those coordinates are component-envelope and carrier-placement candidates, not received connector datums. The arithmetic does not release a route or raw wire cut.

## What remains unresolved

The raw cut length remains `SELECTION REQUIRED`. The package requires current official JST processing limits, received-lot identity, calibrated tooling, accepted crimp coupons, conductor and insulation crimp-height evidence, pull evidence, received-route fit, strain relief, continuity, isolation, pin-2 omission, no-backfeed, waveform and error-rate results. Every process and test row remains `NOT EXECUTED`.

This harness carries no summed actuator power. U2D2 actuator VDD is intentionally absent. That physical omission must be verified on every article; a drawing statement is not acceptance evidence.

## Controlled package

- [Interactive guide](../release/hr-v0/u2d2-jc1-harness-p0.1/index.html)
- [Pin map](../release/hr-v0/u2d2-jc1-harness-p0.1/interface-pinmap.csv)
- [Harness BOM](../release/hr-v0/u2d2-jc1-harness-p0.1/harness-bom.csv)
- [Build definition](../release/hr-v0/u2d2-jc1-harness-p0.1/conductor-and-build-register.csv)
- [Process and inspection plan](../release/hr-v0/u2d2-jc1-harness-p0.1/process-and-inspection-plan.csv)
- [Continuity/isolation matrix](../release/hr-v0/u2d2-jc1-harness-p0.1/continuity-isolation-matrix.csv)
- [Open holds](../release/hr-v0/u2d2-jc1-harness-p0.1/open-holds.csv)

This round also corrects canonical BOM-closure drift: BOM-107 and BOM-108 now agree across the system BOM, closure register and configuration integration map as `exact_candidate_hold`.
