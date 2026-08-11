# HR-V0 runtime evidence log P0.1

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Identifier: `HR-V0-EVID-LOG-P0.1`

Round: R236

## Outcome

R236 addresses the source-side portion of Sol M-022 without treating source tests as physical timing or calibration evidence. The runtime now requires a configuration-bound evidence sink. A log-open failure occurs before hardware access; an in-cycle write failure enters the existing fail-closed cleanup path that attempts heartbeat removal and bus torque-off independently of the logger.

The JSONL record contract provides:

- an exclusive file per boot/session rather than ambiguous append;
- strict monotonically nondecreasing timestamps and sequence numbers;
- a complete configuration context with six identities and eight SHA-256 bindings;
- a context hash inherited by every record;
- a per-record SHA-256 chain and explicit clean-session footer;
- command receipt/decision/sample, feedback, supervisor-event and complete cycle-output records;
- rejection of unresolved configuration, timestamp regression, nonfinite JSON, tampering and an existing session filename.

The host preflight now refuses a runtime cycle period above 10 ms, which is the source-side prerequisite for the existing 100 Hz `CTRL-004` requirement. The committed configuration still exits 78 with 49 holds because timing, clock, calibration, storage, exact hashes, target HIL, review and work authorization are unresolved.

## Controlled package

- Interactive guide: `release/hr-v0/runtime-evidence-log-p0.1/index.html`
- Log record schema: `release/hr-v0/runtime-evidence-log-p0.1/log-schema.json`
- Fourteen event classes: `release/hr-v0/runtime-evidence-log-p0.1/channel-register.csv`
- Ten clock-budget rows: `release/hr-v0/runtime-evidence-log-p0.1/clock-budget.csv`
- Twelve blank calibration records: `release/hr-v0/runtime-evidence-log-p0.1/calibration-register.csv`
- Fifteen unexecuted tests: `release/hr-v0/runtime-evidence-log-p0.1/test-case-register.csv`
- Fifteen open holds: `release/hr-v0/runtime-evidence-log-p0.1/open-holds.csv`
- Blank session acceptance: `release/hr-v0/runtime-evidence-log-p0.1/session-acceptance-template.csv`

## Evidence boundary

The passing source tests demonstrate serialization, chaining, rejection behavior and model-level fail-closed integration. They do not establish target clock resolution/drift, UTC accuracy, scheduler jitter, cross-instrument synchronization, filesystem durability, log retention, storage-exhaustion behavior, abrupt-loss recovery, calibration validity or physical/HIL performance.

Sol M-022 remains `PARTIALLY_ADDRESSED_OPEN`. `EG-002`, `EG-017`, `EG-020`, `EG-021` and `EG-022` remain partial. The logger and supervisor receive zero functional-safety credit.
