# R236 independent review request

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Please independently review `HR-V0-EVID-LOG-P0.1` against Sol M-022, `CTRL-004`, `CTRL-005`, `CFG-001`, `CFG-002` and the current fail-closed runtime.

Check at minimum:

1. Whether the six required identities and eight hashes are sufficient to bind a log to one test configuration without circular or mutable evidence.
2. Whether exclusive per-session creation, strict sequence, monotonic time, context hash, previous-record hash and record hash are correctly implemented and independently verifiable.
3. Whether command receipt, decision, commanded sample, measured feedback, supervisor events and complete output state are captured without relying on later reconstruction.
4. Whether any evidence-open/write/flush/fsync/close failure can skip heartbeat removal, torque-off or resource cleanup.
5. Whether a 1..10 ms selected runtime period is a correct necessary source bound for 100 Hz evidence while remaining insufficient until target scheduling/WCET is measured.
6. Whether clean close and abrupt/truncated close are distinguishable without inventing recovered records.
7. Whether the clock budget identifies every target monotonic, UTC, jitter, drift, latency and cross-instrument uncertainty input needed for acceptance.
8. Whether the calibration and session-acceptance templates are blank and cannot be mistaken for executed evidence.
9. Whether the committed host configuration remains fail-closed before backend import with all logging selections unresolved.
10. Whether Sol M-022 and `EG-002/017/020/021/022` correctly remain open/partial with zero safety credit and no test or energization authority.

Return BLOCKER / MAJOR / MINOR findings with exact file and line/record, failure scenario, evidence basis and proposed correction. Do not treat passing source tests as target timing, calibration, HIL, functional-safety or energization approval.
