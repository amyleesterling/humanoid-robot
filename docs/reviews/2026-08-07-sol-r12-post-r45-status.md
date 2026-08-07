# Sol R12 status after R45 configuration-candidate correction

Status: **PROJECT-OWNED RECONCILIATION—NOT AN INDEPENDENT REVIEW OR APPROVAL**

Date: 2026-08-07

Baseline reviewed by Sol: the R12 pre-correction configuration

Current correction: R45 / `HR-V0-RC-P0.1`

## What R45 changes

R45 creates a deterministic, reviewable HR-V0 package boundary:

- records the current systems, electrical, PCB, mechanical, firmware and safety candidate identifiers in machine-readable release metadata;
- classifies Electrical V2.1 as historical and HR-30A/B/C/D/W as later-stage scope rather than silently mixing them into the HR-V0 candidate;
- hashes every non-ignored package file except the self-referential manifest itself;
- includes the metadata, generator and checker within the hashed file set;
- controls cross-platform text checkout so line-ending conversion cannot silently invalidate or rewrite the evidence set;
- detects changed, missing, extra, reordered, reclassified or corrupted package files; and
- provides a clean-clone mode that also requires a clean Git worktree.

## Sol finding disposition

| Finding | R45 status | Remaining evidence |
|---|---|---|
| `B-001` authoritative repository lacks native build sources | **Repository-source portion stale; build-release conclusion remains open** | The candidate includes native CAD, KiCad and firmware sources, but their unresolved selections and physical evidence still prevent fabrication or energization. |
| `B-002` electrical revision/configuration mismatch | **Package boundary materially advanced; release open** | Current V3-P1.4, PCB-P0.5 and DXL-STAR-P0.1 identifiers are frozen in one candidate; merge/acceptance, selection closure, physical evidence and qualified review remain required. |
| Configuration evidence chain stops before fabrication | **Unchanged in outcome** | A reproducible candidate is not a build release. No Gerber/drill release, cutting order, flashed controller, assembled machine or executed physical test is authorized. |

## Current verdict

- **HR-V0 fabrication readiness:** not ready.
- **HR-V0 energization readiness:** prohibited; no gate closes in R45.
- **Configuration-review readiness:** materially improved; `EG-002` remains partial pending immutable acceptance and signatures.
- **HR-30 walking:** unchanged and outside this release candidate.

R45 assigns no PLr/SIL, closes no physical verification, and issues no fabrication or energization permission.

**PRELIMINARY—NOT APPROVED FOR FABRICATION OR ENERGIZATION.**
