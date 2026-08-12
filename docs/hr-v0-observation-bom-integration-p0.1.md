# HR-V0 observation BOM integration P0.1

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Document ID: **HR-V0-OBS-BOM-INTEGRATION-P0.1**  
Round: **R259**  
Date: **2026-08-12**

## Result

R259 integrates the observation electronics and their two harness assemblies into the hierarchical HR-V0 system BOM. The current BOM and closure register now contain **108 groups with exact row parity**. Ten new groups, `BOM-099` through `BOM-108`, bind:

- one `HR-V0-RUNTIME-OBS-CARRIER-P0.5` PCBA;
- one `HR-V0-PI-OBS-CARRIER-P0.1` PCBA;
- one five-conductor field-harness assembly;
- one six-conductor compute-harness assembly;
- two exact Phoenix Contact runtime terminal candidates;
- one exact Samtec Pi header candidate;
- one exact Phoenix Contact Pi terminal candidate;
- eleven exact Belden 22 AWG color/spool candidates; and
- one unresolved four-site mounting set for each carrier.

The [interactive integration guide](../release/hr-v0/observation-bom-integration-p0.1/index.html) exposes the source binding, assembly quantities, conductor candidates, mounting interfaces, holds and blank acceptance records without implying work authority.

## What this corrects

The native carrier sources and harness definitions existed, but the hierarchical system BOM did not carry them as complete assemblies. R259 removes that bookkeeping omission. `release/hr-v0/release-candidate.json` now identifies the current **108-group** BOM and `HR-V0-CONFIG-REC-P0.23` rather than the stale 98-group/P0.8 metadata.

## Remaining HOLD-15 evidence

This is a logical/configuration correction, not physical closure. HOLD-15 remains **DESIGN REQUIRED** because the package still lacks:

1. exact M3 and M2.5 standoffs, screws, stack heights, materials, thread engagement, torque and panel interfaces;
2. all eleven conductor cut lengths, installed routes, support, separation, preparations and labels;
3. fabrication provider, process, stackup, DFM and first-article evidence for both PCBAs;
4. received identity, fit, DCR, pull, continuity, isolation and functional results; and
5. qualified electrical, mechanical and functional-safety dispositions plus separate written stage authority.

No unresolved hardware, cut length, procurement quantity, rating or physical result was inferred.

## Configuration effect

`HR-V0-CONFIG-REC-P0.23` supersedes P0.22 as the configuration record only. It contains **42 current records, 35 supersession records, 28 BOM-integration records, 11 gate records, 144 open holds and 179 blank/unexecuted acceptance rows**.

Archived configuration records retain the recorded 64-character SHA-256 values for mutable live sources such as `bom/bom.csv` and `release/hr-v0/release-candidate.json`. Exact byte parity for those current live sources is owned by the P0.23 source-hash register and R259 checker. This prevents a legitimate successor revision from making a historical record pretend to describe current bytes.

R259 closes zero Sol R12 blockers and releases no procurement, fabrication, assembly, connection, powered-test, motion, functional-safety or energization authority.
