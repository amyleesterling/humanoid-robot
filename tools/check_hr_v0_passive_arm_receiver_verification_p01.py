"""Check the R128 second-method passive-receiver verification package."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "cad" / "hr-v0" / "generated" / "passive-arm-receiver-verification-p0.1"
SUMMARY = OUT / "verification-summary.json"
ANALYTIC = OUT / "analytic-envelope-verification.csv"
FIT = OUT / "receiver-guard-fit-verification.csv"
ARITHMETIC = OUT / "arithmetic-rederivation.csv"
METHODS = OUT / "method-register.csv"
GUIDE = ROOT / "release" / "hr-v0" / "passive-arm-receiver-verification-p0.1" / "index.html"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def close(actual: float, expected: float, tolerance: float = 1e-6) -> bool:
    return abs(actual - expected) <= tolerance


def main() -> int:
    for path in (SUMMARY, ANALYTIC, FIT, ARITHMETIC, METHODS, GUIDE):
        assert path.exists() and path.stat().st_size > 0, path

    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    assert summary["identifier"] == "HR-V0-PASSIVE-ARM-RECEIVER-VERIFY-P0.1"
    assert "NOT APPROVED FOR FABRICATION, MOTION OR ENERGIZATION" in summary["warning"]
    analytic = summary["analytic_envelope"]
    comparison = summary["r127_comparison"]
    fit = summary["receiver_guard_fit"]
    arithmetic = summary["arithmetic"]

    assert close(analytic["minimum_z_mm"], 384.14261888640146, 1e-9)
    assert analytic["controlling_minimum"]["component"] == "H104_FRAME"
    assert analytic["controlling_minimum"]["family"] == "fore"
    assert close(analytic["controlling_minimum"]["q1_deg"], -20.0, 1e-9)
    assert close(analytic["controlling_minimum"]["q2_deg"], 15.0, 1e-9)
    assert close(comparison["sampled_minimum_z_mm"], analytic["minimum_z_mm"], 1e-9)
    assert close(comparison["released_conservative_minimum_z_mm"], 383.10647837214253, 1e-9)
    assert close(comparison["released_conservative_clearance_mm"], 63.10647837214253, 1e-9)
    assert comparison["analytic_minus_released_bound_mm"] > 1.036
    assert "retained" in comparison["disposition"].lower()

    assert fit["step_bounds_mm"] == {
        "xmin": -90.0,
        "xmax": 90.0,
        "ymin": -430.0,
        "ymax": 430.0,
        "zmin": 20.0,
        "zmax": 320.0,
    }
    assert close(fit["x_margin_each_side_mm"], 110.0)
    assert close(fit["y_margin_each_side_mm"], 20.0)
    assert close(fit["bottom_margin_mm"], 20.0)
    assert close(fit["top_margin_mm"], 630.0)

    assert close(arithmetic["ma30_total_j"], 10.507589099568353, 1e-12)
    assert close(arithmetic["stroke_mm"], 8.128, 1e-12)
    assert close(arithmetic["minimum_impact_speed_m_s"], 0.67056, 1e-12)
    assert close(arithmetic["maximum_impact_speed_m_s"], 4.45008, 1e-12)
    assert close(arithmetic["rail_moment_n_mm"], 210000.0, 1e-9)
    assert close(arithmetic["rail_stress_mpa"], 92.59871684635227, 1e-9)
    assert close(arithmetic["rail_deflection_mm"], 3.951236974285569, 1e-9)

    analytic_rows = rows(ANALYTIC)
    assert len(analytic_rows) == 11
    assert {row["family"] for row in analytic_rows} == {"upper", "fore"}
    h104 = next(row for row in analytic_rows if row["component"] == "H104_FRAME")
    assert close(float(h104["minimum_z_mm"]), analytic["minimum_z_mm"], 1e-9)
    assert all("complete gripper/cables/tolerances excluded" in row["boundary"] for row in analytic_rows)

    fit_rows = rows(FIT)
    assert len(fit_rows) == 5
    assert all(row["result"] != "" for row in fit_rows)
    assert all("PHYSICAL" not in row["result"] for row in fit_rows)

    arithmetic_rows = rows(ARITHMETIC)
    assert len(arithmetic_rows) == 11
    assert any("application approval open" in row["boundary"] for row in arithmetic_rows)

    method_rows = rows(METHODS)
    assert len(method_rows) == 3
    assert {row["method_id"] for row in method_rows} == {
        "R128-METHOD-001",
        "R128-METHOD-002",
        "R128-METHOD-003",
    }
    assert all("INTERNAL CORROBORATION" in row["status"] for row in method_rows)

    html = GUIDE.read_text(encoding="utf-8")
    for required in (
        "The receiver clearance now has a second mathematical proof.",
        "384.143 mm",
        "63.106 mm",
        "20.0 mm",
        "type=\"range\"",
        "font:17px/1.55",
        "NOT APPROVED FOR FABRICATION, MOTION OR ENERGIZATION",
        "EG-008",
    ):
        if required == "EG-008":
            assert "zero fabrication, motion, energization or functional-safety approval" in html
        else:
            assert required in html

    assert summary["verification_state"].startswith("INTERNAL SECOND-METHOD CORROBORATION COMPLETE")
    assert summary["gate_state"] == "EG-008 AND EG-009 REMAIN PARTIAL"

    print("HR-V0 passive receiver R128 second-method verification check passed")
    print("Analytic known-AABB minimum Z 384.142618886 mm; retained R127 clearance 63.106478372 mm")
    print("Nominal receiver/guard margins X 110 mm, Y 20 mm; all physical and qualified holds remain open")
    print("PRELIMINARY - NOT APPROVED FOR FABRICATION, MOTION OR ENERGIZATION")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
