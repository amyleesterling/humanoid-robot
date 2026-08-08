from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "test-fixtures" / "hr-v0" / "dynamic-characterization-p0.1"


def read_csv(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def require(errors: list[str], condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def main() -> None:
    errors: list[str] = []
    expected = {
        "HR-V0_dynamic-characterization-guide.html",
        "daq-candidate-screen.csv",
        "dynamic-characterization-summary.json",
        "dynamic-source-register.csv",
        "dynamic-test-sequence.csv",
        "fixture-interface-controls.csv",
        "measurement-channel-register.csv",
        "raw-data-schema.csv",
        "timing-evidence-register.csv",
    }
    require(errors, OUT.is_dir(), "dynamic-characterization output directory missing")
    if OUT.is_dir():
        require(errors, {p.name for p in OUT.iterdir() if p.is_file()} == expected, "dynamic-characterization artifact membership changed")

    summary = json.loads((OUT / "dynamic-characterization-summary.json").read_text(encoding="utf-8"))
    require(errors, summary.get("revision") == "HR-V0-DYN-CHAR-P0.1", "wrong revision")
    require(errors, "NOT APPROVED" in summary.get("status", ""), "preliminary warning lost")
    require(errors, summary.get("channel_count") == 15, "expected 15 channels")
    require(errors, summary.get("test_stage_count") == 12, "expected 12 stages")
    require(errors, summary.get("timing_evidence_count") == 8, "expected eight timing evidence rows")
    require(errors, summary.get("raw_field_count") == 35, "expected 35 raw fields")
    require(errors, summary.get("authorized_powered_stage_count") == 0, "a powered stage appears authorized")
    require(errors, "not selected" in summary.get("daq_candidate", "").lower(), "DAQ candidate was improperly selected")

    channels = read_csv("measurement-channel-register.csv")
    require(errors, len(channels) == 15, "channel count changed")
    dxl = [row for row in channels if row["channel_id"] == "DCH-013"]
    require(errors, len(dxl) == 1, "DYNAMIXEL supplemental channel missing")
    if dxl:
        require(errors, dxl[0]["primary_or_supplemental"] == "SUPPLEMENTAL ONLY", "DYNAMIXEL telemetry gained primary credit")
        require(errors, dxl[0]["timing_credit"].startswith("NO primary"), "DYNAMIXEL telemetry gained timing credit")
    for required in {"DCH-002", "DCH-004", "DCH-005", "DCH-006", "DCH-007", "DCH-012", "DCH-015"}:
        require(errors, any(row["channel_id"] == required for row in channels), f"required channel {required} missing")

    daq = read_csv("daq-candidate-screen.csv")
    require(errors, len(daq) == 6, "DAQ candidate screen count changed")
    require(errors, all("SELECT" not in row["project_disposition"] or "not selected" in row["project_disposition"].lower() or "SELECTION REQUIRED" in row["project_disposition"] or "NO PREFERENCE" in row["project_disposition"] for row in daq), "DAQ row appears released")
    require(errors, any("12.5" in row["verified_capability"] for row in daq), "official eight-address screen missing")

    fixture = read_csv("fixture-interface-controls.csv")
    require(errors, len(fixture) == 12, "fixture control count changed")
    require(errors, all(row["state"] not in {"PASS", "CLOSED", "RELEASED", "AUTHORIZED"} for row in fixture), "fixture control improperly closed")
    require(errors, any("secondary restraint" in row["control"] for row in fixture), "secondary restraint control missing")
    require(errors, any("guard" in row["control"] and "shall not carry" in row["control"] for row in fixture), "guard load-path separation missing")

    stages = read_csv("dynamic-test-sequence.csv")
    require(errors, len(stages) == 12, "test sequence count changed")
    powered = [row for row in stages if row["stage_id"] in {"DYN-06", "DYN-07", "DYN-08", "DYN-09", "DYN-10", "DYN-11"}]
    require(errors, len(powered) == 6 and all(row["execution_state"] == "NOT AUTHORIZED" for row in powered), "powered stage authorization hold changed")
    require(errors, stages[6]["authorization_gate"].startswith("EG-019"), "source open-circuit stage gate changed")

    timing = read_csv("timing-evidence-register.csv")
    require(errors, len(timing) == 8 and all(row["state"] == "OPEN" for row in timing), "timing evidence must remain eight open rows")
    require(errors, timing[-1]["acceptance_value"].startswith("SELECTION REQUIRED"), "combined timing uncertainty improperly released")

    raw = read_csv("raw-data-schema.csv")
    require(errors, len(raw) == 35, "raw schema count changed")
    required_fields = {"run_id", "configuration_commit", "daq_time_s", "source_current_A", "external_angle_deg", "reaction_force_N", "dropped_scan_count", "calibration_bundle_hash", "run_disposition"}
    require(errors, required_fields.issubset({row["field_name"] for row in raw}), "raw schema lost required evidence fields")

    sources = read_csv("dynamic-source-register.csv")
    require(errors, len(sources) == 7, "source register count changed")
    require(errors, all("2026-08-07" in row["revision_or_date"] for row in sources), "source access date missing")
    require(errors, sources[0]["url"].startswith("https://emanual.robotis.com/"), "ROBOTIS source not official")
    require(errors, all(row["url"].startswith("https://support.labjack.com/") for row in sources[2:6]), "LabJack source not official")

    html = (OUT / "HR-V0_dynamic-characterization-guide.html").read_text(encoding="utf-8")
    for token in ("font:16px", "Measure the real joint", "SUPPLEMENTAL ONLY", "12.5 kscans/s", "SELECTION REQUIRED", "NOT APPROVED", "No powered test"):
        require(errors, token in html, f"interactive guide missing {token!r}")

    form = ROOT / "tests" / "forms" / "hr-v0-dynamic-characterization-template.csv"
    require(errors, form.is_file(), "dynamic-characterization execution template missing")
    if form.is_file():
        with form.open(encoding="utf-8", newline="") as handle:
            form_rows = list(csv.DictReader(handle))
        require(errors, len(form_rows) == 12, "execution template must contain 12 stage rows")
        require(errors, all(row["record_id"] == "NOT-EXECUTED" for row in form_rows), "execution template contains executed evidence")

    if errors:
        raise SystemExit("\n".join(f"ERROR: {error}" for error in errors))
    print("HR-V0 dynamic-characterization check passed: 15 channels, 12 stages, 8 open timing records, 35 raw fields")
    print("DYNAMIXEL telemetry remains supplemental; six powered stages remain NOT AUTHORIZED")
    print("PRELIMINARY - NO POWERED TESTING, MOTION, CONNECTION, OR ENERGIZATION RELEASE")


if __name__ == "__main__":
    main()
