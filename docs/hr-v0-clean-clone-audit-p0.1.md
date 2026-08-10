# HR-V0 clean-clone reproducibility audit P0.1

> **PRELIMINARY - CONFIGURATION EVIDENCE ONLY - NOT APPROVED FOR PROCUREMENT, FABRICATION, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Artifact: `HR-V0-CLEAN-CLONE-AUDIT-P0.1`

Round: R189

Date: 2026-08-10

## Result

A fresh Windows clone of source commit `221035ed307f4e3501abad82cf7afa42f6e7cc36` passed all **145/145** repository checker programs and remained clean after execution. The run comprised 132 non-`pcbnew` checks and 13 KiCad `pcbnew` checks. The release-manifest checker also passed with `--require-clean` over 3,206 controlled package files.

The test environment deliberately retained machine-level `core.autocrlf=true`. This demonstrates that the repository checkout contract, rather than the operator's global Git setting, controls the working bytes required by the current hash-bound package.

## Defects found and corrected

The first clean clone of the R188 candidate passed only 112/145 checks. Hash-bound working bytes depended on the originating machine's newline conversion. A blanket LF rule was then tested and rejected after it reduced the result to 99/145.

The accepted correction adds a generated exact checkout contract: LF is the repository default, 989 historically CRLF-controlled paths receive explicit CRLF checkout rules, and five deliberately mixed-EOL artifacts are preserved as opaque bytes. That correction reached 144/145. The final failure exposed six synthetic dynamic-trace result records containing Amy's absolute local repository path. The analyzer now emits repository-relative trace and configuration identifiers, and all six results were regenerated.

The complete failure history is retained in `configuration/hr-v0-clean-clone-audit-p0.1/failure-disposition.csv`; the machine-readable audit is `configuration/hr-v0-clean-clone-audit-p0.1/audit-summary.json`.

## Interpretation boundary

This result proves only that the encoded repository package reproduces in the recorded software environment. It does not prove that any requirement is correct, any part fits, any circuit is safe, any firmware works on target hardware, or any machine may be fabricated or energized. `EG-002` remains **PARTIAL** pending merge or other immutable acceptance, named configuration authority, qualified review, and formal acceptance of the controlled baseline.

Sol's resupplied 18 BLOCKER / 30 MAJOR / 8 MINOR summary is the already-recorded independent review R12. R189 closes none of those physical, functional-safety, fabrication, or energization blockers.
