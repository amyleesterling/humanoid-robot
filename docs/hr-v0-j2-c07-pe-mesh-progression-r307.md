# HR-V0 J2 C07 mesh progression through R307

**PRELIMINARY—NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

This handoff extends the controlled R286-R302 chain through R307. It is numerical-method evidence only. It does not select P0.13, prove structural capacity, close R279-C02 or R278-H02, or authorize physical work.

## Current outcome

- R300 remains the preferred numerical baseline: 1,244,636 Tet10 elements, global minimum SICN 0.203978, zero cells below 0.20, every monitored zone passing, and three failed Q8 samples in two elements.
- R303 executed the exact R302 two-face refinement once. It retained the frozen linear gates but reduced the global minimum to 0.116866 and produced ten failed samples in one element. The route is rejected.
- R304 localized all ten failures to the same negative-X rail-transition cylinder identified before R303.
- R305 found nearly coincident curved surface-edge midsides in the remaining element and restored R300 as the next-method baseline.
- R306 attempted one constrained `HighOrder` optimization on the retained discrete R300 mesh. The process produced no result and was stopped after CPU and memory counters remained unchanged for at least 60 seconds. The temporary decompressed copy was removed; R300 remains intact.
- R307 freezes one new candidate: regenerate the exact R300 linear mesh while OCC geometry is live, require exact R300 reproduction, curve to Tet10, optimize C07-MATRIX once, and restore every linear corner. It has not executed.

## R307 acceptance boundary

The single execution must satisfy all of the following without tuning:

- exact R300 linear element tags, connectivity, SICN values, zone codes, and coordinates;
- bijective linear-to-Tet10 corner mapping and restoration within 1e-12 mm;
- unchanged element connectivity and orientation;
- zero wrong/nonpositive or normalized-floor failures at Q4, Q6, and Q8;
- complete exact exterior-facet mapping;
- maximum Q8 B-Rep deviation no greater than 0.005 mm;
- every face within 0.25% area error;
- loaded-area error no greater than 0.25%;
- load location and moment drift no greater than 0.1%.

A pass would advance only a bounded CAD-resident curving method. Full-reference-domain Jacobian positivity, independent numerical acceptance, structural fields, sections, exact-zone statistics, singularity trends, L0-L3/L4 convergence, H02, contact/joint/dynamic/material/physical evidence, capacity, and every work authority remain separate and open.
