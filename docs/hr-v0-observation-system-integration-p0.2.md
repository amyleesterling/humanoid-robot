# HR-V0 observation-system integration and configuration reconciliation R212 / P0.2

**PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

R212 corrects a configuration mismatch left after R211. The standalone observation carrier had advanced to `HR-V0-RUNTIME-OBS-CARRIER-P0.5`, but the only complete system-view derivative and release metadata still named the superseded P0.2 receiver.

`V3-P1.17-OBSERVATION-P0.5-CANDIDATE` retains P1.15 as the direct watchdog/core source. Its checker reconstructs both generators and proves that all 79 P1.15 component definitions, pins, nets, status fields and evidence fields are unchanged. The only new system references are OBS1 and PIOBS1. Their selected terminal/net maps match the current native P0.5 and Pi-carrier schedules exactly.

`observation-subassembly-binding.csv` records the current P0.5 and Pi-carrier source-manifest hashes, connector-schedule hashes and the generated P1.17 connector-schedule hash. Native KiCad parses the root plus thirteen child sheets and ERC reports 0 errors / 0 warnings.

`HR-V0-CONFIG-REC-P0.2` retains the P1.15 direct core and adds the P1.17 system view, P0.5 receiver, Pi carrier and field/compute harness candidates. It supersedes P1.16, observation P0.2-P0.4 and configuration P0.1 for current review. It does not add missing observation assemblies or harnesses to the 91-group hierarchical BOM; that omission is an explicit open hold rather than an implied selection.

Affected gates EG-002, EG-003, EG-004, EG-010, EG-012, EG-014 and EG-015 remain partial. Fifteen configuration holds and twelve acceptance rows remain open. No physical result, qualified approval or work authority is created.
