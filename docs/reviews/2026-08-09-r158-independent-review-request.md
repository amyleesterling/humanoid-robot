# R158 independent review request

> **PRELIMINARY - NOT APPROVED FOR SUPPLIER UPLOAD, QUOTATION, PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, MOTION, OR ENERGIZATION**

Please independently review `HR-V0-DXL-PROT-CARRIER-P0.2` against the official Texas Instruments TPS25946 datasheet `SLVSGA8B` revision B, package drawing `4225183/A`, and the current electrical evaluation boundary.

Check at minimum:

1. every copper, mask and paste primitive, dimension, pitch, center and pad number against TI pages 45-47;
2. the use of compound same-number corner copper and paste-only stencil apertures in native KiCad;
3. whether the 0.05 mm mask expansion is accurately labeled as a candidate requiring fabricator tolerance acceptance;
4. the board instance, footprint library, fabrication outputs, parity CSV and checker for exact synchronization;
5. whether P0.1 is unmistakably superseded and prohibited for supplier use;
6. whether the selected assembler/stencil process needs a different paste treatment, home-plate adjustment, mask rule or via/thermal constraint;
7. whether AOI plus X-ray and a first-article acceptance plan are sufficient or need additional cross-section/pull/rework evidence;
8. whether any artifact implies supplier release, fabrication, assembly, connection, energization, safety credit or physical validation.

Report BLOCKER / MAJOR / MINOR findings with the exact artifact, primitive/pad and proposed correction. Do not approve physical work or energization.
