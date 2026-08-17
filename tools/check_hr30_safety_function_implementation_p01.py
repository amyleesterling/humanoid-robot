"""Fail-closed checks for HR-30 safety-function implementation P0.1."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WHOLE = ROOT / "hr30" / "whole-body-p0.1"
OUT = WHOLE / "safety-function-implementation-p0.1"
REL = ROOT / "release" / "hr30" / "whole-body-p0.1" / OUT.name
GEN = ROOT / "tools" / "generate_hr30_safety_function_implementation_p01.py"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    implementation = rows("safety-function-implementation-matrix.csv")
    exact = rows("exact-circuit-interface-map.csv")
    holds = rows("open-implementation-holds.csv")
    status = json.loads((OUT / "implementation-status.json").read_text(encoding="utf-8"))
    assert len(implementation) == 12 and {r["function_id"] for r in implementation} == {f"SFR-{i:02d}" for i in range(1, 13)}
    assert all(r["achieved_pl_claimed"] == "NO" and r["validation_state"] == "NOT VALIDATED" for r in implementation)
    assert sum("ECAD CONNECTED" in r["implementation_state"] for r in implementation) == 3
    assert any(r["function_id"] == "SFR-05" and "HARNESS BLOCKER" in r["implementation_state"] and "ROBOTIS daisy cables carry VDD" in r["independence_or_safe_state"] for r in implementation)
    assert any(r["function_id"] == "SFR-07" and "NO SAFETY CREDIT" in r["implementation_state"] for r in implementation)
    assert any(r["function_id"] == "SFR-11" and "MOTION PROHIBITED" in r["implementation_state"] for r in implementation)
    assert len(exact) == 12 and {r["function_id"] for r in exact} == {"SFR-01", "SFR-02", "SFR-03"}
    assert any(r["reference"] == "K1" and r["terminal_or_pin"] == "21-22" and r["net_path"] == "RESET_EDM to EDM_K1_OUT" for r in exact)
    assert any(r["reference"] == "K2" and r["terminal_or_pin"] == "21-22" and r["net_path"] == "EDM_K1_OUT to RESET_EDM" for r in exact)
    assert any(r["reference"] == "SR1/K1" and "13-14 / A1-A2" in r["terminal_or_pin"] for r in exact)
    assert any(r["reference"] == "SR1/K2" and "23-24 / A1-A2" in r["terminal_or_pin"] for r in exact)
    assert len(holds) == 10 and all(r["state"] == "OPEN" for r in holds)
    assert status["safety_function_count"] == 12 and status["connected_unvalidated_function_count"] == 3
    for key in ("functional_safety_validated", "achieved_pl_calculated", "qualified_review_complete", "connection_authority", "powered_test_authority", "motion_authority", "energization_authority"):
        assert status[key] is False
    for binding in rows("source-binding.csv"):
        path = ROOT / binding["path"]
        assert path.is_file() and sha(path) == binding["sha256"]
    assert (OUT / "safety-function-implementation-source.py").read_bytes() == GEN.read_bytes()
    for row in rows("file-manifest.csv"):
        path = OUT / row["path"]
        assert path.stat().st_size == int(row["bytes"]) and sha(path) == row["sha256"]
    source = sorted(p.relative_to(OUT).as_posix() for p in OUT.rglob("*") if p.is_file())
    release = sorted(p.relative_to(REL).as_posix() for p in REL.rglob("*") if p.is_file())
    assert source == release and all(sha(OUT / p) == sha(REL / p) for p in source)
    page = (OUT / "index.html").read_text(encoding="utf-8")
    assert "font:17px" in page and "font-size:16px" in page and "What is implemented, exactly?" in page
    root = json.loads((WHOLE / "package-status.json").read_text(encoding="utf-8"))
    assert root["safety_function_implementation_map_present"] is True and root["safety_function_implementation_validated"] is False
    assert "HR30-SFI-P01-START" in (WHOLE / "README.md").read_text(encoding="utf-8")
    assert "safety-function-implementation" in (WHOLE / "index.html").read_text(encoding="utf-8")
    print("PASS: all 12 HR-30 safety functions have an exact implementation disposition; three have connected unvalidated circuitry, and no achieved PL or work authority is claimed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
