# R172 validation record

R172 issues `HR-V0-RPI-OS-SBOM-P0.1` as a controlled publisher-SBOM and exact DPKG comparison lock. It does not promote, install or authorize an operating-system image.

- The controlled compressed publisher SBOM is 5,336,108 bytes and has SHA-256 `7a82f353f58d925543ed196e56b551342138551132fcb59111917df64c683959`.
- The decompressed SPDX 2.3 document contains 4,743 package records and 632 unique DPKG name/version identities.
- The normalized DPKG lock has SHA-256 `8146766fb15bc3a5cbceaed00ef53cc5aa0af2d9a085762df6a34a23f9174e02`.
- Fifteen critical package rows are controlled as comparison candidates. Presence is not target evidence or application approval.
- Exact DPKG identities named `python3-serial` and `dynamixel-sdk` are absent from the publisher SBOM. No broader absence claim is made.
- All 12 target-verification rows remain `NOT_AUTHORIZED / NOT_EXECUTED`.
- `EG-002`, `EG-017` and `EG-022` remain partial.

## Browser validation

The interactive guide was inspected at 1280 x 720 and 390 x 844.

- body and button text: 16 px;
- technical text: 14 px;
- no horizontal overflow;
- filter results: Everything 4, Exact identity 1, Runtime inputs 2, Open evidence 1;
- no console warnings or errors; and
- the desktop and mobile header, warning, summary cards and controls remain legible and reflow without clipping.

## Repository validation

- General repository checks: **101/101 passed**.
- Native KiCad-dependent checks under KiCad 10.0: **13/13 passed**.
- CadQuery geometry checks: **14/14 passed**.
- Pre-manifest total: **128/128 passed**.
- The staged release-manifest check brings the controlled total to **129 checks**.

These checks prove controlled-source integrity, normalization reproducibility, parser compatibility, digital invariants and reference-model behavior only. The disk image was not downloaded; no target media was written or read back; and no target was booted, installed, connected or HIL-tested. No GPIO or serial backend was selected. No connection, motion, functional-safety or energization authority exists.
