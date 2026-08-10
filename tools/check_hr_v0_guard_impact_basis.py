from __future__ import annotations

import csv
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "cad" / "hr-v0" / "guard-impact-basis-p0.1"


def read_csv(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def require(errors: list[str], condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def main() -> None:
    errors: list[str] = []
    expected = {
        "HR-V0_guard-impact-basis.html",
        "guard-impact-summary.json",
        "impact-direction-matrix.csv",
        "impact-energy-cases.csv",
        "impact-input-register.csv",
        "impact-source-register.csv",
        "impact-test-controls.csv",
    }
    require(errors, OUT.is_dir(), "impact output directory missing")
    if OUT.is_dir():
        require(errors, {p.name for p in OUT.iterdir() if p.is_file()} == expected, "impact artifact membership changed")

    summary = json.loads((OUT / "guard-impact-summary.json").read_text(encoding="utf-8"))
    require(errors, summary.get("revision") == "HR-V0-GUARD-IMPACT-P0.1", "wrong impact revision")
    require(errors, "NOT APPROVED" in summary.get("status", ""), "warning lost")
    expected_values = {
        "payload_translation_j": 0.001125,
        "moving_mass_translation_j": 0.008438,
        "payload_drop_j": 0.931632,
        "payload_drop_plus_translation_j": 0.932757,
        "single_axis_catalog_endpoint_screen_j": 0.479663,
        "combined_axis_catalog_endpoint_screen_j": 0.990987,
        "raw_800_work_per_degree_per_xm540_j": 0.090408,
        "stall_endpoint_work_per_degree_per_xm540_j": 0.185005,
    }
    for key, expected_value in expected_values.items():
        require(errors, math.isclose(float(summary.get(key, -1)), expected_value, abs_tol=0.000001), f"{key} changed")
    require(errors, summary.get("selection_state") == "NO PANEL, RETENTION SYSTEM, TEST ENERGY, OR IMPACT RATING SELECTED", "selection hold changed")

    inputs = read_csv("impact-input-register.csv")
    require(errors, len(inputs) == 15, "expected 15 impact inputs")
    unresolved_inputs = [row for row in inputs if row["value"] == "SELECTION REQUIRED"]
    require(errors, len(unresolved_inputs) == 5, "expected five unresolved impact inputs")

    cases = read_csv("impact-energy-cases.csv")
    require(errors, len(cases) == 11, "expected 11 energy cases")
    require(errors, sum(row["calculated_energy_j"] == "SELECTION REQUIRED" for row in cases) == 3, "expected three blocking open energy cases")
    require(errors, all("RATING" not in row["state"] or "NOT A GUARD RATING" in row["state"] for row in cases), "an energy case appears to claim a rating")
    require(errors, all("INCOMPLETE" in row["state"] for row in cases if row["case_id"] in {"GIE-005", "GIE-006"}), "catalog endpoint screens must remain incomplete")

    directions = read_csv("impact-direction-matrix.csv")
    require(errors, len(directions) == 6 and all(row["state"] == "OPEN" for row in directions), "direction matrix must remain six open rows")
    controls = read_csv("impact-test-controls.csv")
    require(errors, len(controls) == 12, "expected 12 impact controls")
    require(errors, all(row["state"] not in {"PASS", "CLOSED", "RELEASED"} for row in controls), "impact control improperly closed")

    sources = read_csv("impact-source-register.csv")
    require(errors, len(sources) == 6, "expected six source rows")
    require(errors, all("2026-08-07" in row["revision_or_date"] for row in sources), "source date control failed")
    require(errors, sources[0]["url"].startswith("https://emanual.robotis.com/"), "XM540 source is not official")
    require(errors, sources[1]["url"].startswith("https://emanual.robotis.com/"), "XM430 source is not official")

    html = (OUT / "HR-V0_guard-impact-basis.html").read_text(encoding="utf-8")
    for token in ("font:16px", "Five hazards", "0.932757 J", "0.990987 J", "SELECTION REQUIRED", "NOT APPROVED", "not a panel rating"):
        require(errors, token in html, f"interactive guide missing {token!r}")

    if errors:
        raise SystemExit("\n".join(f"ERROR: {error}" for error in errors))
    print("HR-V0 guard impact basis check passed: 15 inputs, 11 energy cases, 6 directions, 12 open controls")
    print("Payload-only combined screen: 0.932757 J; combined-axis catalog endpoint screen: 0.990987 J")
    print("PRELIMINARY - NO PANEL SELECTION, FABRICATION, MOTION, OR ENERGIZATION RELEASE")


if __name__ == "__main__":
    main()
