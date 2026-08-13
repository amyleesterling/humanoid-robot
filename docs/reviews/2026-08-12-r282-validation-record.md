# R282 validation draft

> **PRELIMINARY - PROTOCOL CORRECTION AND NUMERICAL METHOD EVIDENCE ONLY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Generated and checker-verified project-owned evidence: C06 curved mapping 18,351/18,351 edges and zero wrong-orientation quadrature Jacobians; C07 mapping 26,209/26,209 edges and **18 wrong-orientation quadrature Jacobians (fail)**; coarse direct/CG solution difference 7.382440e-13, energy difference 1.086597e-12, displacement difference 6.631311e-13; analytic affine-patch DOF errors 1.664105e-16 direct and 1.316926e-13 CG. Independent review, exact-zone implementation, raw convergence execution, H02 and all work authority remain open.

Browser DOM QA passed. At 1440 x 900, body text is 17 px, minimum functional text is 16 px, there is no root overflow, and all seven table wrappers fit. At 390 x 844 (375 px client width), body/minimum text is 16 px, there is no root overflow, and all seven tables scroll internally. The warning, H02-open statement and `What R281 got wrong` section are visible.

Final repository validation passed on 2026-08-12:

- Native KiCad validation: **18/18 checks passed**; no ECAD source changed in R282.
- HR-V0 standard checker sweep: **227/227 checks passed**.
- R282 dedicated checker: passed with C07 curved geometry, H02, capacity, and every work-authority gate held open.
- Master release inventory regenerated: **7,674 package files**.
- Exact checkout-byte reproducibility for the four historical R281 CRLF artifacts is frozen in `.gitattributes`; their Git-normalized semantic content was not altered.
- Staged diff whitespace validation: passed.

These are configuration, consistency, and numerical-method checks. They do not establish structural capacity, functional safety, fabrication readiness, motion readiness, or permission to energize.
