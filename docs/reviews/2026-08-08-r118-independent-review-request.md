# R118 independent review request

Status: **PRELIMINARY - NOT APPROVED FOR WIRING, FABRICATION, TESTING, OR ENERGIZATION**

Review `HR-V0-GND-BOND-P0.1` for source accuracy, domain separation, protective-bonding completeness, measurement safety, Boston applicability boundaries and native-ECAD closure requirements. This is not a request to select a bond, shield termination or test.

## Review artifacts

- `electrical/vendor/grounding-r118/source-manifest-p0.1.csv`
- `electrical/grounding/hr-v0-grounding-node-register-p0.1.csv`
- `electrical/grounding/hr-v0-grounding-selection-matrix-p0.1.csv`
- `tests/forms/hr-v0-grounding-bonding-survey-template-p0.1.csv`
- `docs/hr-v0-grounding-bonding-closure-p0.1.md`
- `release/hr-v0/grounding-bonding-p0.1/index.html`

## Questions

1. Does the current Mean Well source support only the internal `-V`/AC-FG relationship represented by `ACT_0V_PE_BONDED`?
2. Is retaining `SP1` as DNP correct until a different qualified topology is released?
3. Does the GlobTek record support calling pin 3 output return/shield while prohibiting a PE inference?
4. Are `SAFETY_0V`, `COMPUTE_0V`, `ROBOT_FRAME`, cable shields, steel backplate, DIN rails, actuator cases, USB shells and guard frame kept distinct?
5. Are the fifteen node records and twelve holds complete enough to prevent accidental parallel paths and missing fault paths?
6. Are all eighteen surveys safely bounded as unexecuted and unauthorized, with no instruction to megger installed electronics?
7. Does the Boston section distinguish current code/permit routes from a configuration-specific legal determination?
8. What exact topology, hardware, numeric limits and native-ECAD changes would be required before `EG-016` could close?

Return BLOCKER / MAJOR / MINOR findings with exact file, row, physical object, net, terminal, source clause and gate. State separately whether the packet is ready for an unpowered measurement-method review, ready for physical survey, ready for wiring review, and whether any physical work is authorized.
