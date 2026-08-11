# R218 independent review request

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION.**

Review identifier: `HR-V0-SRS-P0.2`
Review scope: safety-requirements completeness and candidate-limit validity only

Please review the package against the current repository and controlled primary sources. Do not infer a PLr, SIL, category, achieved performance or approval.

## Questions

1. Is the adult-only, fixed-guarded, bench-restrained HR-V0 boundary complete for the intended staged commissioning lifecycle?
2. Is the J2-positive first-motion candidate of 200 ms total response and 2.000 degrees residual travel at no more than 10.000 degrees/s internally coherent, and are its limitations sufficiently explicit?
3. Does the 1.000-degree nominal reserve need a larger design margin before tolerance/backlash/compliance/uncertainty closure?
4. Is automatic motion correctly prohibited until a separately accepted 66.667 ms / 2.000-degree bound or a different released envelope exists?
5. Are `SF-01`, `SF-03`, `DF-01` and `PG-01` classified and bounded without assigning unjustified safety credit?
6. Does the validation matrix cover E-stop channel order, redundant final-element faults, restart/reset misuse, feedback discrepancy, recovery and ordinary-diagnostic failure?
7. Does the common-cause register cover the credible shared electrical, mechanical, software, environmental and maintenance faults?
8. What additional information is required before a qualified ISO 12100 risk determination and ISO 13849-1:2023 or IEC 62061 allocation can be executed?
9. Identify every statement that could be misread as achieved performance, functional-safety approval or permission for physical work.

Please return findings as `BLOCKER`, `MAJOR` or `MINOR`, with exact artifact/row references, primary-source support, required correction and closure evidence.
