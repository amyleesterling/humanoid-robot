from __future__ import annotations

import json
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path


SUPERVISOR_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SUPERVISOR_ROOT))

from project_button_supervisor.evidence_log import (  # noqa: E402
    EvidenceContext,
    EvidenceLogError,
    HashChainedJsonlSink,
    REQUIRED_HASHES,
    REQUIRED_IDENTITIES,
    verify_log,
)


def context() -> EvidenceContext:
    return EvidenceContext(
        session_id="SESSION-TEST",
        identities={key: f"TEST-{key}" for key in REQUIRED_IDENTITIES},
        hashes={key: "a" * 64 for key in REQUIRED_HASHES},
    )


def fixed_utc() -> datetime:
    return datetime(2026, 8, 11, 12, 0, 0, tzinfo=timezone.utc)


class EvidenceLogTests(unittest.TestCase):
    def test_round_trip_verifies_closed_hash_chain(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "session.jsonl"
            sink = HashChainedJsonlSink(path, context(), 100, fixed_utc)
            sink.record(110, "CYCLE_OUTPUT", {"state": "SAFE_DISABLED", "positions": {"J1": 0.0}})
            sink.close(120)
            result = verify_log(path)
        self.assertEqual(result.record_count, 3)
        self.assertEqual((result.first_monotonic_ms, result.last_monotonic_ms), (100, 120))
        self.assertTrue(result.closed_cleanly)

    def test_open_log_is_valid_but_not_cleanly_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "session.jsonl"
            sink = HashChainedJsonlSink(path, context(), 100, fixed_utc)
            sink.record(110, "CYCLE_OUTPUT", {"state": "SAFE_DISABLED"})
            sink._handle.close()  # emulate abrupt power loss without inventing a clean footer
            result = verify_log(path)
        self.assertFalse(result.closed_cleanly)

    def test_tamper_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "session.jsonl"
            sink = HashChainedJsonlSink(path, context(), 100, fixed_utc)
            sink.close(120)
            records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
            records[0]["payload"]["context"]["session_id"] = "TAMPERED"
            path.write_text("\n".join(json.dumps(record) for record in records) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(EvidenceLogError, "hash mismatch"):
                verify_log(path)

    def test_monotonic_regression_is_rejected_before_write(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            sink = HashChainedJsonlSink(Path(directory) / "session.jsonl", context(), 100, fixed_utc)
            with self.assertRaisesRegex(EvidenceLogError, "regressed"):
                sink.record(99, "CYCLE_OUTPUT", {})
            sink.close(100)

    def test_existing_session_file_is_never_appended(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "session.jsonl"
            path.write_text("existing", encoding="utf-8")
            with self.assertRaisesRegex(EvidenceLogError, "exclusive"):
                HashChainedJsonlSink(path, context(), 100, fixed_utc)

    def test_unresolved_context_is_rejected(self) -> None:
        identities = {key: f"TEST-{key}" for key in REQUIRED_IDENTITIES}
        identities["calibration_set_id"] = "SELECTION REQUIRED"
        invalid = EvidenceContext("SESSION-TEST", identities, {key: "a" * 64 for key in REQUIRED_HASHES})
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(EvidenceLogError, "unresolved"):
                HashChainedJsonlSink(Path(directory) / "session.jsonl", invalid, 100, fixed_utc)

    def test_nonfinite_payload_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            sink = HashChainedJsonlSink(Path(directory) / "session.jsonl", context(), 100, fixed_utc)
            with self.assertRaisesRegex(EvidenceLogError, "canonical JSON"):
                sink.record(110, "CYCLE_OUTPUT", {"value": float("nan")})
            sink.close(110)


if __name__ == "__main__":
    unittest.main()
