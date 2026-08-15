# R245 independent review request

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Independently review `HR-V0-MECH-BOM-BIND-P0.3`, `HR-V0-FW-MECH-SRC-BIND-P0.1` and `HR-V0-CONFIG-REC-P0.9` for accuracy and completeness. This request is not an approval request for fabrication or energization.

Please verify:

1. all five custom-part rows name `HR-V0-ARM-ARCH-P0.8-DWG-INTEGRATED-CANDIDATE` and retain the fifteen exact P0.2 artifact identities;
2. no historical P0.1/P0.2 artifact was overwritten;
3. all eight source-manifest hashes reproduce from repository files;
4. both firmware configurations bind the same identifier and manifest SHA-256;
5. an altered architecture, manufacturing revision or manifest hash fails closed;
6. source identity cannot substitute for the separate physical/HIL acceptance hash;
7. the remaining shop-document, DFM/FAI, physical and qualified-review holds are complete; and
8. no file grants procurement, fabrication, assembly, connection, powered-test, motion, energization or functional-safety authority.

Also assess the proposed next mechanical package: five successor shop drawings, formal datum/GD&T disposition, controlled title blocks/general notes, exact RFQ payload and a part-specific unpowered assembly instruction.
