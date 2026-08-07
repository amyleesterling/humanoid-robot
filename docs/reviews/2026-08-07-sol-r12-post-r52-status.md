# Sol R12 status after R52 packet-portability correction

**Date:** 2026-08-07

**Independent reviewed baseline:** Sol R12

**Current project response:** R52 / corrected `HR-V0-FAB-RFI-P0.1`

**Status:** **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY OR ENERGIZATION**

Clean-clone validation found that R51's ZIP timestamps and member ordering were deterministic, but CAD text payload bytes still depended on the Windows checkout's CRLF/LF state. The committed R51 packet hashes therefore failed source-equality checks in a fresh clone.

R52 normalizes controlled text payloads (`CSV`, `DXF`, `MD`, `STEP`, `SVG`, and `TXT`) to LF before internal hashing and ZIP storage. Binary payloads remain byte-for-byte. The checker independently applies the same explicit canonical representation, verifies packet/source equivalence, and rejects unsafe paths, permissions, timestamps, compression, duplicate membership and PDFs. Release CSV files are pinned to LF in `.gitattributes` so regenerating the outer packet index also leaves a clean Windows checkout.

R52 regenerates all three packet hashes and must prove two conditions in a clean clone:

1. the committed packets pass internal/source/index verification before regeneration; and
2. regeneration produces no Git diff and leaves the clean-clone worktree clean.

This correction changes packet identity only; it does not close any Sol finding or energization gate. Supplier responses, site survey, finished tolerances, exact anchors, first articles, FAI, physical proof and qualified review remain absent.
