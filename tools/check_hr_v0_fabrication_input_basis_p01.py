from __future__ import annotations

import csv
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "release" / "hr-v0" / "fabrication-input-basis-p0.1"
WARNING = "PRELIMINARY - NOT APPROVED FOR QUOTATION FABRICATION MOTION OR ENERGIZATION"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"HR-V0-FAB-INPUT-P0.1 check failed: {message}")


def close(actual: float, expected: float, tolerance: float = 1e-9) -> bool:
    return math.isclose(actual, expected, rel_tol=0.0, abs_tol=tolerance)


def main() -> None:
    required = {
        "input-reconciliation.csv",
        "kinematic-screens.csv",
        "source-register.csv",
        "package-status.json",
        "index.html",
    }
    require({p.name for p in PKG.iterdir()} == required, "package membership changed")

    requirements = {r["id"]: r for r in rows(ROOT / "requirements" / "requirements.csv")}
    require("no more than 100 g" in requirements["SYS-002"]["statement"], "SYS-002 payload changed")
    require("40 mm and 70 mm" in requirements["SYS-002"]["statement"], "SYS-002 dimensions changed")
    require("0.15 m/s" in requirements["SYS-004"]["statement"], "SYS-004 TCP limit changed")
    require("30 deg/s" in requirements["SYS-004"]["statement"], "SYS-004 joint cap changed")
    require("10 deg/s" in requirements["SYS-005"]["statement"], "SYS-005 setup limit changed")

    atomic = {r["child_id"]: r for r in rows(ROOT / "requirements" / "atomic-p0.2" / "atomic-requirements.csv")}
    expected_atomic = {
        "SYS-002-A02": "shall not exceed 100 g",
        "SYS-004-A01": "shall not exceed 0.15 m/s",
        "SYS-004-A03": "at or below 30 deg/s",
        "SYS-005-A02": "shall not exceed 10 deg/s",
    }
    for child_id, phrase in expected_atomic.items():
        require(phrase in atomic[child_id]["child_statement"], f"{child_id} changed")

    inputs = rows(PKG / "input-reconciliation.csv")
    require([r["input_id"] for r in inputs] == [f"FAB-IN-{i:03d}" for i in range(1, 11)], "input IDs changed")
    counts = {
        "reconciled": sum(r["state"] == "CONTROLLED DRAFT - INDEPENDENT ACCEPTANCE REQUIRED" for r in inputs),
        "partial": sum(r["state"] == "PARTIAL" for r in inputs),
        "open": sum(r["state"] in {"OPEN", "SELECTION REQUIRED"} for r in inputs),
        "unauthorized": sum(r["state"] == "NOT AUTHORIZED" for r in inputs),
    }
    require(counts == {"reconciled": 1, "partial": 2, "open": 6, "unauthorized": 1}, f"input states changed: {counts}")
    require(all(r["warning"] == WARNING for r in inputs), "input warning changed")

    screens = {r["screen_id"]: r for r in rows(PKG / "kinematic-screens.csv")}
    expected = {
        "FIB-CALC-001": 0.100 * 9.80665 * 0.950,
        "FIB-CALC-002": 0.5 * 0.100 * 0.15**2,
        "FIB-CALC-003": 0.360 * math.radians(30.0),
        "FIB-CALC-004": math.degrees(0.15 / 0.360),
        "FIB-CALC-005": 0.360 * math.radians(10.0),
    }
    require(set(screens) == set(expected), "screen IDs changed")
    for screen_id, value in expected.items():
        require(close(float(screens[screen_id]["result"]), value), f"{screen_id} result mismatch")
        require(screens[screen_id]["warning"] == WARNING, f"{screen_id} warning changed")
    require(float(screens["FIB-CALC-003"]["result"]) > 0.15, "30 deg/s conflict disappeared")

    status = json.loads((PKG / "package-status.json").read_text(encoding="utf-8"))
    require(status["identifier"] == "HR-V0-FAB-INPUT-P0.1", "identifier changed")
    require(status["round"] == "R173", "round changed")
    require(status["gate_effect"] == "EG-006_AND_EG-007_REMAIN_PARTIAL", "gate effect changed")
    require(status["warning"] == WARNING, "status warning changed")

    html = (PKG / "index.html").read_text(encoding="utf-8")
    require(
        "font:16px" in html
        and "font-size:14px" in html
        and "font-size:16px;font-weight:700" in html,
        "legibility floors changed",
    )
    require(
        "PRELIMINARY - NOT APPROVED FOR QUOTATION, FABRICATION, MOTION, OR ENERGIZATION" in html,
        "visible warning changed",
    )

    print("HR-V0 fabrication input basis P0.1 check passed: 10 inputs; 1 reconciled; 2 partial; 6 open; 1 unauthorized; 5 calculations")
    print("EG-006 and EG-007 remain PARTIAL; no quotation, fabrication, motion or energization authority")
    print(WARNING)


if __name__ == "__main__":
    main()
