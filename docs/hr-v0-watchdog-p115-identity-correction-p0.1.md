# HR-V0 watchdog P1.15 native-identity correction P0.1

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Identifier: `HR-V0-WD-P115-ID-P0.1`

Correction round: R195
Date: 2026-08-10

## Correction

The current watchdog PCB is now `PCB-P1.0 / Electrical V3-P1.15`. This removes the live configuration exception in which PCB-P0.9 retained an Electrical V3-P1.14 native title while the active system and CAM review were P1.15-bound through a separate parity record.

PCB-P1.0 is a configuration-identity correction only. The controlled P0.8 structural snapshot and P0.7 assembly baseline prove:

- geometry and topology unchanged;
- copper, tracks, vias, zones and nets unchanged;
- all 42 populated placements and four NPTH features unchanged;
- all 294 hidden native assembly fields unchanged; and
- all 16 Harwin test-point land patterns unchanged.

The historical `HR-V0-E2-P115-PARITY-P0.1` record remains audit evidence, but the current board, assembly package, CAM review, BOM binding and E2 slice no longer depend on that exception.

## Synchronized current artifacts

- `electrical/kicad/project-button-v3/project-button-v3.kicad_pcb`
- `electrical/manufacturing/hr-v0-watchdog-pcba-assembly-data-p0.2/`
- `release/hr-v0/watchdog-pcb-cam-p0.2/`
- `bom/hr-v0-watchdog-pcb-binding.csv`
- `release/hr-v0/watchdog-pcb-bom-binding-p0.1/`
- `electrical/e2/hr-v0-e2-hardware-p0.4/`
- `release/hr-v0/e2-hardware-p0.4/`
- `release/hr-v0/release-candidate.json`

## What remains open

All twelve assembly-data holds, all eighteen CAM/manufacturing holds and all twelve E2 hardware holds remain open. Supplier-normalized XYRS, accepted fabrication/assembly process, stackup and materials, protection selections, physical article, bare-board test, assembled-board inspection, HIL, fault injection, EMC, thermal evidence, functional-safety allocation, qualified review and separate work authorizations remain absent.

ERC/DRC and deterministic parity evidence establish only encoded configuration consistency. They do not establish manufacturability, physical correctness, safety performance or permission to perform work. EG-002 and EG-004 remain partial.

**PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**
