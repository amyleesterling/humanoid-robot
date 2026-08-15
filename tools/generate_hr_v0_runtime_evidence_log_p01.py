#!/usr/bin/env python3
"""Generate HR-V0 runtime evidence-log contract P0.1.

This creates source/test evidence controls only. It sends nothing, executes no
physical test, and authorizes no installation, connection, motion, or energy.
"""

from __future__ import annotations

import csv
import hashlib
import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IDENTIFIER = "HR-V0-EVID-LOG-P0.1"
ROUND = "R236"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
TARGETS = (
    ROOT / "controls/hr-v0-runtime-evidence-log-p0.1",
    ROOT / "release/hr-v0/runtime-evidence-log-p0.1",
)


CHANNELS = [
    ("LOG-CH-001", "SESSION_START", "once per exclusive session", "complete context identities and hashes; context SHA-256", "context is complete and hash-valid"),
    ("LOG-CH-002", "RUNTIME_START_REQUEST", "on start request", "state; heartbeat; torque request; bus torque; trajectory; fault", "written before hardware access"),
    ("LOG-CH-003", "RUNTIME_STARTED", "after torque-off bus setup", "complete runtime status", "runtime reports started only after setup"),
    ("LOG-CH-004", "CYCLE_BEGIN", "every runtime cycle", "complete runtime status", "period selected at no more than 10 ms"),
    ("LOG-CH-005", "FEEDBACK_SAMPLE", "every runtime cycle that reaches hardware read", "joint positions and eleven hardware/health observations", "no missing or nonfinite released field"),
    ("LOG-CH-006", "COMMAND_RECEIVED", "every received command", "session; sequence; source/deadline times; config/model hashes; mode; samples; endpoints", "complete before acceptance decision"),
    ("LOG-CH-007", "COMMAND_DECISION", "every received command", "trajectory; sequence; accepted; state; fault", "one decision per received command"),
    ("LOG-CH-008", "COMMAND_SAMPLE", "every actuator sample write", "index; due time; commanded/measured positions; terminal-reassert flag", "write evidence is configuration bound"),
    ("LOG-CH-009", "SUPERVISOR_EVENT", "every in-memory supervisor event", "source event; source state; detail; source monotonic time", "no source event omitted or reordered"),
    ("LOG-CH-010", "CYCLE_OUTPUT", "every completed or fault-shortened cycle", "complete runtime status", "paired with cycle start under accepted loss policy"),
    ("LOG-CH-011", "RUNTIME_SHUTDOWN_REQUEST", "on shutdown request", "complete runtime status", "record attempt cannot prevent cleanup"),
    ("LOG-CH-012", "RUNTIME_STOPPED", "after heartbeat/bus/resources cleanup", "complete runtime status", "started false and torque false"),
    ("LOG-CH-013", "RUNTIME_FAIL_CLOSED", "best effort after runtime failure", "complete runtime status and latched fault", "failure to log never skips heartbeat/torque removal"),
    ("LOG-CH-014", "SESSION_END", "clean close only", "closed_cleanly true", "absence means truncated/abrupt end; never inferred clean"),
]

CLOCK_BUDGET = [
    ("CLK-001", "runtime cycle period", "CTRL-004", "<= 10 ms", "SELECTION REQUIRED", "target scheduler trace", "OPEN"),
    ("CLK-002", "monotonic clock implementation", "logging source contract", "nondecreasing integer milliseconds", "SELECTION REQUIRED", "target clock identity and API record", "OPEN"),
    ("CLK-003", "monotonic clock resolution", "TEST-LOG-001", "SELECTION REQUIRED", "SELECTION REQUIRED", "calibrated timestamp analyzer comparison", "OPEN"),
    ("CLK-004", "monotonic drift over test duration", "TEST-LOG-001", "SELECTION REQUIRED", "SELECTION REQUIRED", "traceable reference comparison", "OPEN"),
    ("CLK-005", "cycle timestamp jitter", "TEST-LOG-001", "SELECTION REQUIRED", "SELECTION REQUIRED", "target distribution and worst-case trace", "OPEN"),
    ("CLK-006", "UTC source and synchronization method", "Sol M-022", "SELECTION REQUIRED", "SELECTION REQUIRED", "target configuration and network-isolation disposition", "OPEN"),
    ("CLK-007", "UTC offset uncertainty", "Sol M-022", "SELECTION REQUIRED", "SELECTION REQUIRED", "calibrated UTC comparison", "OPEN"),
    ("CLK-008", "cross-instrument synchronization", "fault reconstruction", "SELECTION REQUIRED", "SELECTION REQUIRED", "shared event injection and measured offsets", "OPEN"),
    ("CLK-009", "logging write latency", "runtime deadline protection", "SELECTION REQUIRED", "SELECTION REQUIRED", "worst-case storage/load measurement", "OPEN"),
    ("CLK-010", "timestamp wrap/regression behavior", "fail-closed runtime", "no regression accepted", "source-enforced; target evidence required", "fault injection and long-run test", "OPEN"),
]

CALIBRATION = [
    ("CAL-001", "target monotonic clock", "time", "implementation identity/resolution/drift"),
    ("CAL-002", "UTC reference", "time", "source/offset/uncertainty"),
    ("CAL-003", "timestamp or logic analyzer", "time", "sample rate/timebase/trigger uncertainty"),
    ("CAL-004", "oscilloscope", "time/voltage", "timebase, probe and channel skew"),
    ("CAL-005", "DMM", "voltage/resistance", "range and uncertainty"),
    ("CAL-006", "current probe/logger", "current/time", "zero, bandwidth and uncertainty"),
    ("CAL-007", "temperature instruments", "temperature/time", "sensor identity, placement and uncertainty"),
    ("CAL-008", "joint angle reference", "angle/time", "datum, resolution and uncertainty"),
    ("CAL-009", "linear position reference", "distance/time", "datum, resolution and uncertainty"),
    ("CAL-010", "force/load instrumentation", "force/time", "range, overload and uncertainty"),
    ("CAL-011", "video synchronization witness", "time/image", "frame rate, trigger and timestamp uncertainty"),
    ("CAL-012", "storage health/free-space monitor", "bytes/time", "method and threshold verification"),
]

TESTS = [
    ("LOG-T001", "context completeness", "attempt start with each identity/hash absent or mismatched", "runtime/log construction refuses before hardware access"),
    ("LOG-T002", "sequence and chain", "produce a bounded session then independently verify every record", "strict sequence, context and SHA-256 chain pass"),
    ("LOG-T003", "tamper detection", "modify each field class in copied logs", "every modified record is rejected"),
    ("LOG-T004", "truncation detection", "remove bytes, records and SESSION_END", "corruption rejected; clean-close claim false when footer absent"),
    ("LOG-T005", "clock regression", "inject decreasing monotonic timestamps", "write rejected and runtime fails closed"),
    ("LOG-T006", "UTC characterization", "compare every record UTC time with calibrated reference", "selected offset/uncertainty limit passes"),
    ("LOG-T007", "100 Hz completeness", "run selected worst-load case at released period", "every required cycle channel is present at 100 Hz or faster"),
    ("LOG-T008", "command completeness", "inject accepted and rejected commands", "received/decision/sample records contain all released fields"),
    ("LOG-T009", "feedback completeness", "exercise each available and unavailable observation", "positions and all health observations retain type and unknown state"),
    ("LOG-T010", "supervisor-event parity", "compare in-memory event stream with JSONL records", "count, order, timestamps, states and details match"),
    ("LOG-T011", "write failure", "inject open/write/flush/fsync failure before and during motion", "no start on open failure; active failure removes heartbeat and torque"),
    ("LOG-T012", "storage exhaustion", "cross selected size/free-space limits", "new motion inhibited or controlled fail-closed response occurs per released policy"),
    ("LOG-T013", "abrupt power loss", "remove compute power at each write phase", "prior records verify or truncation is explicit; restart cannot append old session"),
    ("LOG-T014", "calibration mismatch", "alter calibration ID/hash and expiration state", "preflight refuses and no hardware backend imports"),
    ("LOG-T015", "configuration replay", "replay log with one CAD/ECAD/BOM/firmware/procedure hash changed", "independent acceptance rejects the session"),
]

HOLDS = [
    ("LOG-H001", "target monotonic clock identity/resolution", "target OS/kernel/hardware clock selection and measurement"),
    ("LOG-H002", "monotonic drift and jitter", "calibrated worst-load target trace"),
    ("LOG-H003", "UTC source and uncertainty", "approved isolated-network time policy and measured offset"),
    ("LOG-H004", "100 Hz runtime cycle", "selected <=10 ms period plus target scheduling/WCET evidence"),
    ("LOG-H005", "configuration identities and hashes", "accepted exact release, ECAD, CAD, BOM, firmware and manifest hashes"),
    ("LOG-H006", "calibration set", "serialized instruments, current calibration evidence and accepted uncertainty budget"),
    ("LOG-H007", "test procedure identity", "accepted configuration-specific procedure and SHA-256"),
    ("LOG-H008", "storage sizing and reserve", "measured record rate, duration, maximum file and minimum-free-space selection"),
    ("LOG-H009", "rotation and retention", "approved ownership, mode, rotation, export and retention policy"),
    ("LOG-H010", "abrupt-loss/corruption policy", "executed cut-power matrix and accepted recovery disposition"),
    ("LOG-H011", "content/rate verification", "executed LOG-T001 through LOG-T015 with raw artifacts"),
    ("LOG-H012", "cross-instrument synchronization", "shared-event trace and accepted offset uncertainty"),
    ("LOG-H013", "target integration/HIL", "installed image hashes and target HIL evidence"),
    ("LOG-H014", "qualified review", "signed controls, test and configuration review"),
    ("LOG-H015", "work authorization", "separate configuration-specific written authorization"),
]


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.rstrip() + "\n", encoding="utf-8", newline="\n")


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def schema() -> dict[str, object]:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "urn:project-button:hr-v0:evidence-log:p0.1",
        "title": IDENTIFIER,
        "type": "object",
        "additionalProperties": False,
        "required": ["schema_id", "sequence", "monotonic_ms", "wall_time_utc", "event", "context_sha256", "previous_sha256", "payload", "record_sha256"],
        "properties": {
            "schema_id": {"const": IDENTIFIER},
            "sequence": {"type": "integer", "minimum": 0},
            "monotonic_ms": {"type": "integer", "minimum": 0},
            "wall_time_utc": {"type": "string", "format": "date-time"},
            "event": {"type": "string", "pattern": "^[A-Z][A-Z0-9_]{2,63}$"},
            "context_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
            "previous_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
            "payload": {"type": "object"},
            "record_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
        },
        "verification_boundary": WARNING,
    }


def make_rows() -> dict[str, tuple[list[str], list[dict[str, object]]]]:
    return {
        "channel-register.csv": (["channel_id", "event", "cadence", "required_payload", "acceptance_rule", "status", "warning"], [
            dict(zip(["channel_id", "event", "cadence", "required_payload", "acceptance_rule"], row), status="SOURCE_IMPLEMENTED_TARGET_UNVERIFIED", warning=WARNING) for row in CHANNELS
        ]),
        "clock-budget.csv": (["clock_id", "quantity", "requirement_basis", "candidate_or_required_limit", "accepted_limit", "closure_evidence", "status", "warning"], [
            dict(zip(["clock_id", "quantity", "requirement_basis", "candidate_or_required_limit", "accepted_limit", "closure_evidence", "status"], row), warning=WARNING) for row in CLOCK_BUDGET
        ]),
        "calibration-register.csv": (["calibration_id", "instrument_or_source", "measurand", "required_record", "manufacturer", "model", "serial", "calibration_certificate", "calibration_due", "uncertainty", "status", "warning"], [
            {"calibration_id": row[0], "instrument_or_source": row[1], "measurand": row[2], "required_record": row[3], "manufacturer": "", "model": "", "serial": "", "calibration_certificate": "", "calibration_due": "", "uncertainty": "", "status": "SELECTION REQUIRED", "warning": WARNING} for row in CALIBRATION
        ]),
        "test-case-register.csv": (["test_id", "subject", "method", "acceptance", "state", "authorization", "actual_result", "evidence_hash", "warning"], [
            {"test_id": row[0], "subject": row[1], "method": row[2], "acceptance": row[3], "state": "NOT_EXECUTED", "authorization": "NOT_AUTHORIZED", "actual_result": "", "evidence_hash": "", "warning": WARNING} for row in TESTS
        ]),
        "open-holds.csv": (["hold_id", "topic", "evidence_required", "state", "owner_candidate", "warning"], [
            {"hold_id": row[0], "topic": row[1], "evidence_required": row[2], "state": "OPEN", "owner_candidate": "SELECTION REQUIRED", "warning": WARNING} for row in HOLDS
        ]),
        "session-acceptance-template.csv": (["session_id", "log_sha256", "record_count", "first_monotonic_ms", "last_monotonic_ms", "closed_cleanly", "context_sha256", "schema_pass", "chain_pass", "rate_pass", "content_pass", "calibration_pass", "configuration_pass", "reviewer", "review_date", "disposition", "warning"], [
            {"session_id": "", "log_sha256": "", "record_count": "", "first_monotonic_ms": "", "last_monotonic_ms": "", "closed_cleanly": "", "context_sha256": "", "schema_pass": "", "chain_pass": "", "rate_pass": "", "content_pass": "", "calibration_pass": "", "configuration_pass": "", "reviewer": "", "review_date": "", "disposition": "NOT_REVIEWED", "warning": WARNING}
        ]),
    }


def html_page() -> str:
    cards = "".join(f'<article data-kind="events"><h3>{html.escape(row[1])}</h3><p><b>{row[0]}</b> · {html.escape(row[2])}</p><p>{html.escape(row[3])}</p></article>' for row in CHANNELS)
    holds = "".join(f'<tr><td>{row[0]}</td><td>{html.escape(row[1])}</td><td>{html.escape(row[2])}</td><td>OPEN</td></tr>' for row in HOLDS)
    tests = "".join(f'<tr><td>{row[0]}</td><td>{html.escape(row[1])}</td><td>{html.escape(row[3])}</td><td>NOT EXECUTED</td></tr>' for row in TESTS)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{IDENTIFIER}</title><style>
:root{{--sky:#79cfff;--navy:#082a52;--blue:#075ea8;--gold:#f4bd28;--paper:#f7fbff;--ink:#10243b;--line:#b8d9ef}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.55 system-ui,sans-serif}}header{{background:linear-gradient(135deg,var(--navy),var(--blue));color:white;padding:clamp(24px,5vw,64px)}}main{{max-width:1200px;margin:auto;padding:24px}}h1{{font-size:clamp(32px,6vw,64px);line-height:1.05;margin:.2em 0}}h2{{font-size:clamp(24px,3vw,36px)}}.warning{{background:#fff4c7;color:#3c2b00;border:3px solid var(--gold);padding:16px;font-weight:800}}nav{{display:flex;gap:10px;flex-wrap:wrap;margin:22px 0}}button{{font:inherit;font-weight:750;padding:12px 16px;border:2px solid var(--navy);border-radius:999px;background:white;color:var(--navy);cursor:pointer}}button[aria-pressed=true]{{background:var(--gold)}}section{{display:none}}section.active{{display:block}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px}}article{{background:white;border:2px solid var(--line);border-radius:16px;padding:18px}}table{{width:100%;border-collapse:collapse;background:white}}th,td{{text-align:left;vertical-align:top;border:1px solid var(--line);padding:12px;min-width:130px}}th{{background:#dff2ff;color:var(--navy)}}.scroll{{overflow-x:auto;border-radius:14px}}.stat{{font-size:clamp(24px,4vw,40px);font-weight:850;color:var(--navy)}}code{{font-size:16px;background:#e8f5ff;padding:2px 6px;border-radius:4px}}@media(max-width:600px){{main{{padding:16px}}th,td{{min-width:150px}}}}
</style></head><body><header><p>{ROUND} · SOURCE/TEST CONTRACT</p><h1>Runtime evidence that can be audited</h1><p>Configuration-bound JSONL, monotonic sequence, per-record SHA-256 chain, explicit calibration and timing holds.</p></header><main>
<p class="warning">{WARNING}</p>
<nav aria-label="Guide sections"><button data-show="overview" aria-pressed="true">Overview</button><button data-show="events" aria-pressed="false">Events</button><button data-show="tests" aria-pressed="false">Tests</button><button data-show="holds" aria-pressed="false">Open holds</button></nav>
<section id="overview" class="active"><h2>What changed</h2><div class="grid"><article><div class="stat">14</div><p>required event classes</p></article><article><div class="stat">15</div><p>future test cases, all unexecuted</p></article><article><div class="stat">15</div><p>open acceptance holds</p></article></div><p>The runtime now requires an evidence sink. A log-open or write failure prevents start or forces the active runtime through its existing heartbeat-removal and torque-off path. This is ordinary diagnostic evidence with zero functional-safety credit.</p><p>The committed host configuration still exits preflight. Calibration, clock behavior, storage policy, exact hashes, target HIL and authorization remain unresolved.</p></section>
<section id="events"><h2>Required event stream</h2><div class="grid">{cards}</div></section>
<section id="tests"><h2>Future verification</h2><div class="scroll"><table><thead><tr><th>ID</th><th>Subject</th><th>Acceptance</th><th>State</th></tr></thead><tbody>{tests}</tbody></table></div></section>
<section id="holds"><h2>What still blocks evidence acceptance</h2><div class="scroll"><table><thead><tr><th>ID</th><th>Topic</th><th>Evidence required</th><th>State</th></tr></thead><tbody>{holds}</tbody></table></div></section>
<script>const buttons=[...document.querySelectorAll('button[data-show]')],sections=[...document.querySelectorAll('main section')];buttons.forEach(b=>b.addEventListener('click',()=>{{buttons.forEach(x=>x.setAttribute('aria-pressed',String(x===b)));sections.forEach(s=>s.classList.toggle('active',s.id===b.dataset.show));location.hash=b.dataset.show;}}));const wanted=location.hash.slice(1);if(wanted){{const b=buttons.find(x=>x.dataset.show===wanted);if(b)b.click();}}</script>
</main></body></html>"""


def manifest(directory: Path) -> None:
    entries = []
    for path in sorted(directory.iterdir()):
        if path.is_file() and path.name != "file-manifest.csv":
            entries.append({"file": path.name, "bytes": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    write_csv(directory / "file-manifest.csv", ["file", "bytes", "sha256"], entries)


def main() -> None:
    rows = make_rows()
    status = {
        "identifier": IDENTIFIER,
        "round": ROUND,
        "schema_id": IDENTIFIER,
        "source_implemented": True,
        "runtime_sink_required": True,
        "supervisor_unit_tests": 75,
        "event_classes": len(CHANNELS),
        "clock_budget_rows": len(CLOCK_BUDGET),
        "calibration_rows": len(CALIBRATION),
        "physical_tests": len(TESTS),
        "physical_tests_executed": 0,
        "open_holds": len(HOLDS),
        "sol_m022_disposition": "PARTIALLY_ADDRESSED_OPEN",
        "functional_safety_credit": "NONE",
        "work_authority": False,
        "warning": WARNING,
    }
    readme = f"""# {IDENTIFIER}

> **{WARNING}**

This package controls the source-side runtime evidence stream and the future target/calibration acceptance route. It does not contain an accepted calibration, target trace, physical result, qualified disposition, or test authority.

- {len(CHANNELS)} required event classes
- {len(CLOCK_BUDGET)} clock/uncertainty budget rows
- {len(CALIBRATION)} blank calibration records
- {len(TESTS)} future tests, all `NOT_EXECUTED`
- {len(HOLDS)} open holds
- Sol M-022 remains `PARTIALLY_ADDRESSED_OPEN`
"""
    for directory in TARGETS:
        directory.mkdir(parents=True, exist_ok=True)
        write_text(directory / "README.md", readme)
        write_text(directory / "index.html", html_page())
        write_text(directory / "package-status.json", json.dumps(status, indent=2))
        write_text(directory / "log-schema.json", json.dumps(schema(), indent=2))
        for name, (fields, data) in rows.items():
            write_csv(directory / name, fields, data)
        manifest(directory)
    print(f"Wrote {IDENTIFIER}: {len(CHANNELS)} events, {len(TESTS)} tests, {len(HOLDS)} holds")
    print(WARNING)


if __name__ == "__main__":
    main()
