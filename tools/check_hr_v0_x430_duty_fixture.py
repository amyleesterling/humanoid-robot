from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "test-fixtures" / "hr-v0" / "x430-duty-fixture-p0.1"
WEB = ROOT / "release" / "hr-v0" / "x430-duty-fixture-p0.1"
VENDOR = ROOT / "cad" / "vendor" / "robotis" / "x430-fr12-r91"


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> None:
    errors: list[str] = []
    required = [
        "HR-V0_X430_duty_fixture_P0.1_review.step",
        "HR-V0_X430_duty_fixture_P0.1_review.glb",
        "dimensioned-topology-review.svg",
        "geometry-control.csv",
        "topology-trade.csv",
        "load-path-screen.csv",
        "interface-register.csv",
        "instrument-candidate-register.csv",
        "open-hold-register.csv",
        "source-register.csv",
        "package-status.json",
    ]
    errors.extend(f"missing {name}" for name in required if not (OUT / name).exists())
    if not (WEB / "index.html").exists():
        errors.append("missing interactive guide")
    form = ROOT / "tests" / "forms" / "hr-v0-x430-duty-fixture-inspection-template.csv"
    if not form.exists():
        errors.append("missing blank fixture inspection form")
    if errors:
        raise SystemExit("\n".join(errors))

    geometry = rows("geometry-control.csv")
    if len(geometry) != 8 or geometry[4]["value_mm"] != "4 axes on BCD 31.75, both ends":
        errors.append("geometry controls changed")
    if any("CANDIDATE" not in row["release_state"] and "OPEN" not in row["release_state"] and "REQUIRED" not in row["release_state"] for row in geometry):
        errors.append("geometry authority boundary missing")

    trade = rows("topology-trade.csv")
    if len(trade) != 4 or trade[0]["disposition"] != "PREFERRED EVALUATION CANDIDATE - NOT SELECTED":
        errors.append("topology disposition changed")
    if trade[2]["disposition"] != "REJECT AS PRIMARY TORQUE EVIDENCE" or trade[3]["disposition"] != "PROHIBITED TEST METHOD":
        errors.append("rejected test methods changed")

    screens = rows("load-path-screen.csv")
    if len(screens) != 5:
        errors.append("load-path screen count changed")
    expected = [11 / 4.1, 16.5 / 4.1, 11 / 1.087329823, 11.1, 3 / 2.3]
    actual = [float(row["result"].split("=")[1].split()[0]) for row in screens]
    if any(not math.isclose(a, b, abs_tol=1e-6) for a, b in zip(actual, expected)):
        errors.append("load-path arithmetic changed")
    if any("ONLY" not in row["authority"] and "OPEN" not in row["authority"] and "NOT A" not in row["authority"] for row in screens):
        errors.append("screen authority boundary missing")

    interfaces = rows("interface-register.csv")
    if len(interfaces) != 12 or any(row["state"] != "OPEN" for row in interfaces):
        errors.append("interface register promoted or count changed")

    instruments = rows("instrument-candidate-register.csv")
    if len(instruments) != 6 or any("SELECTED" not in row["state"] and row["state"] != "SELECTION REQUIRED" for row in instruments):
        errors.append("instrument candidate boundary changed")

    holds = rows("open-hold-register.csv")
    if len(holds) != 14 or any(row["state"] != "OPEN" for row in holds):
        errors.append("fixture holds promoted or count changed")

    sources = rows("source-register.csv")
    if len(sources) != 8 or sources[1]["revision_or_date"] != "drawing revision F; live record accessed 2026-08-08":
        errors.append("source register changed")

    status = json.loads((OUT / "package-status.json").read_text(encoding="utf-8"))
    if status.get("identifier") != "HR-V0-X430-FIXTURE-P0.1" or status.get("open_hold_count") != 14:
        errors.append("package identity/state changed")
    if any(value is not False for value in status.get("release_flags", {}).values()):
        errors.append("fixture release flag promoted")
    for name, expected_hash in status.get("source_sha256", {}).items():
        if sha256(VENDOR / name) != expected_hash:
            errors.append(f"controlled ROBOTIS source changed: {name}")

    with form.open(newline="", encoding="utf-8") as handle:
        form_rows = list(csv.DictReader(handle))
    if len(form_rows) != 14 or any(row["execution_state"] != "NOT EXECUTED" for row in form_rows):
        errors.append("fixture inspection form promoted or count changed")
    result_fields = ("result", "instrument_id", "evidence_locator", "reviewer", "review_date")
    if any(row[field] for row in form_rows for field in result_fields):
        errors.append("blank fixture form contains result evidence")

    guide = (WEB / "index.html").read_text(encoding="utf-8")
    for phrase in (
        "still not a fixture release",
        "not selected hardware",
        "Datum markers are not holes",
        "font-size:13px",
        "th,td{text-align:left;vertical-align:top;padding:13px",
        "Fourteen holds prevent build or use",
    ):
        if phrase not in guide:
            errors.append(f"guide boundary/style missing: {phrase}")
    svg = (OUT / "dimensioned-topology-review.svg").read_text(encoding="utf-8")
    if "font-size:18px" not in svg or "Fabrication dimensions: SELECTION REQUIRED" not in svg:
        errors.append("drawing readability/release boundary changed")

    if errors:
        raise SystemExit("HR-V0 X430 duty fixture check FAILED:\n- " + "\n- ".join(errors))
    print("HR-V0 X430 duty fixture check: PASS")
    print("8 geometry controls; 4 topology options; 12 interfaces; 14 open holds")
    print("all fixture, powered-test, motion, connection and energization flags remain false")


if __name__ == "__main__":
    main()
