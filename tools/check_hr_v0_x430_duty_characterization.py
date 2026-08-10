from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release" / "hr-v0" / "x430-duty-characterization-p0.1"


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> None:
    errors: list[str] = []
    required = [
        "source-register.csv", "current-torque-sensitivity.csv", "instrument-channel-register.csv",
        "fixture-control-register.csv", "duty-test-sequence.csv", "acceptance-equation-register.csv",
        "raw-data-schema.csv", "open-hold-register.csv", "package-status.json", "index.html",
    ]
    errors.extend(f"missing {name}" for name in required if not (OUT / name).exists())
    form = ROOT / "tests" / "forms" / "hr-v0-x430-duty-characterization-template.csv"
    if not form.exists():
        errors.append("missing blank execution form")
    if errors:
        raise SystemExit("\n".join(errors))

    sources = rows("source-register.csv")
    if len(sources) != 4 or sources[0]["revision_or_date"] != "live page; no formal document revision shown; accessed 2026-08-08":
        errors.append("source register changed")
    for row in sources[1:]:
        path = ROOT / row["locator"]
        if not path.exists() or sha256(path) != row["sha256"]:
            errors.append(f"source binding changed: {row['source_id']}")

    sensitivity = rows("current-torque-sensitivity.csv")
    if len(sensitivity) != 7:
        errors.append("sensitivity row count changed")
    for row in sensitivity:
        raw = float(row["raw_current_units"])
        amps = raw * 0.00269
        torque = amps * 4.1 / 2.3
        if not math.isclose(float(row["nominal_internal_current_a"]), amps, abs_tol=1e-6):
            errors.append("current-unit arithmetic mismatch")
        if not math.isclose(float(row["ideal_stall_line_torque_nm"]), torque, abs_tol=1e-6):
            errors.append("stall-line arithmetic mismatch")
        if "NOT A COMMAND" not in row["authority"]:
            errors.append("sensitivity authority boundary missing")

    channels = rows("instrument-channel-register.csv")
    if len(channels) != 15 or channels[0]["quantity"] != "external actuator-branch current":
        errors.append("instrument channel set changed")
    if "Supplemental" not in channels[10]["evidence_role"] or "Supplemental" not in channels[12]["evidence_role"]:
        errors.append("DYNAMIXEL telemetry promoted above supplemental evidence")

    fixtures = rows("fixture-control-register.csv")
    if len(fixtures) != 12 or any(row["state"] != "OPEN" for row in fixtures):
        errors.append("fixture control promoted or count changed")

    stages = rows("duty-test-sequence.csv")
    if len(stages) != 12 or sum(row["state"] == "BLOCKED" for row in stages) != 7:
        errors.append("test sequence count/state changed")
    for row in stages:
        if "POWERED" in row["energy_state"] and row["state"] != "BLOCKED":
            errors.append(f"powered stage promoted: {row['stage_id']}")

    equations = rows("acceptance-equation-register.csv")
    if len(equations) != 10 or any(row["acceptance_limit"] != "SELECTION REQUIRED" for row in equations):
        errors.append("acceptance limit invented or count changed")

    holds = rows("open-hold-register.csv")
    if len(holds) != 12 or any(row["state"] != "OPEN" for row in holds):
        errors.append("hold register promoted or count changed")

    with form.open(newline="", encoding="utf-8") as handle:
        form_rows = list(csv.DictReader(handle))
    numeric = ["current_limit_raw", "pwm_limit_raw", "velocity_limit_raw", "acceleration_limit_raw", "ambient_c", "external_current_rms_a", "external_current_peak_a", "terminal_voltage_min_v", "torque_mean_nm", "torque_peak_nm", "case_temp_max_c", "connector_temp_max_c", "cable_temp_max_c"]
    if len(form_rows) != 12 or any(row["execution_state"] != "NOT EXECUTED" for row in form_rows):
        errors.append("execution template promoted or count changed")
    if any(row[field] for row in form_rows for field in numeric):
        errors.append("execution template contains numeric result or limit")

    status = json.loads((OUT / "package-status.json").read_text(encoding="utf-8"))
    false_keys = ["powered_stages_authorized", "test_fixture_buildable", "current_limit_released", "duty_profile_released", "thermal_limits_released", "continuous_torque_verified", "x430_selected", "p1_1_selected", "motion_released", "connection_released", "energization_released", "load_open_08_closed"]
    if status.get("identifier") != "HR-V0-X430-DUTY-P0.1" or any(status.get(key) is not False for key in false_keys):
        errors.append("fail-closed package status changed")

    guide = (OUT / "index.html").read_text(encoding="utf-8")
    for phrase in ("NOT APPROVED FOR POWERED TEST", "NOT A COMMAND OR CONTINUOUS RATING", "font-size:13px", "th,td{padding:12px", "DYNAMIXEL telemetry is supplemental"):
        if phrase not in guide:
            errors.append(f"guide boundary/style missing: {phrase}")

    if errors:
        raise SystemExit("HR-V0 X430 duty characterization check FAILED:\n- " + "\n- ".join(errors))
    print("HR-V0 X430 duty characterization check: PASS")
    print("15 channels; 12 fixture controls open; 12 stages; all 7 powered stages blocked")
    print("12 blank result rows; no current, duty, thermal or acceptance limit released")


if __name__ == "__main__":
    main()
