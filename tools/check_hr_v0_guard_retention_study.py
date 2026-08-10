from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "cad" / "hr-v0" / "guard-retention-study-p0.1"
WARNING = "PRELIMINARY - EVALUATION STUDY ONLY"


def read_csv(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def fail(errors: list[str], condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def main() -> None:
    errors: list[str] = []
    expected = {
        "guard-mass-options.csv",
        "guard-gasket-edge-schedule.csv",
        "guard-gasket-stock-plan.csv",
        "guard-thermal-movement-screen.csv",
        "guard-retention-decisions.csv",
        "guard-retention-controls.csv",
        "guard-retention-source-register.csv",
        "guard-retention-summary.json",
        "HR-V0_guard-retention-study.html",
    }
    actual = {path.name for path in OUT.iterdir() if path.is_file()} if OUT.is_dir() else set()
    fail(errors, actual == expected, f"artifact membership differs: {sorted(actual ^ expected)}")

    summary = json.loads((OUT / "guard-retention-summary.json").read_text(encoding="utf-8"))
    fail(errors, summary.get("revision") == "HR-V0-GUARD-RET-P0.1", "wrong revision")
    fail(errors, WARNING in summary.get("status", ""), "summary warning missing")
    fail(errors, abs(float(summary.get("current_known_subtotal_kg", 0)) - 30.799798) < 0.000002, "P0.3 mass changed")
    fail(errors, abs(float(summary.get("preferred_evaluation_known_subtotal_kg", 0)) - 19.415878) < 0.000002, "hybrid mass mismatch")
    fail(errors, abs(float(summary.get("preferred_evaluation_reduction_kg", 0)) - 11.383920) < 0.000002, "hybrid reduction mismatch")
    fail(errors, summary.get("gasket_stock_quantity_screen") == 11, "gasket stock quantity mismatch")
    fail(errors, summary.get("gasket_used_length_mm") == 20980, "gasket used length mismatch")
    fail(errors, summary.get("gasket_offcut_before_kerf_mm") == 1020, "gasket offcut mismatch")

    mass = read_csv("guard-mass-options.csv")
    fail(errors, len(mass) == 4, "expected four mass branches")
    by_id = {row["option_id"]: row for row in mass}
    fail(errors, set(by_id) == {"GMASS-BASE-6", "GMASS-ALL-4P5", "GMASS-ALL-3", "GMASS-HYBRID-3-6"}, "mass branch IDs differ")
    fail(errors, "NOT SELECTED" in by_id["GMASS-HYBRID-3-6"]["state"], "hybrid branch must remain nonselected")

    edges = read_csv("guard-gasket-edge-schedule.csv")
    fail(errors, len(edges) == 3, "expected three gasket edge groups")
    fail(errors, sum(int(row["quantity"]) for row in edges) == 32, "expected 32 gasket pieces")
    fail(errors, sum(int(row["used_length_mm"]) for row in edges) == 20980, "edge schedule length mismatch")

    stocks = read_csv("guard-gasket-stock-plan.csv")
    fail(errors, len(stocks) == 11, "expected eleven gasket stock lengths")
    fail(errors, sum(int(row["used_mm"]) for row in stocks) == 20980, "stock used length mismatch")
    fail(errors, sum(int(row["offcut_mm"]) for row in stocks) == 1020, "stock offcut mismatch")
    fail(errors, all("KERF" in row["state"] for row in stocks), "stock rows must retain saw-kerf hold")

    thermal = read_csv("guard-thermal-movement-screen.csv")
    expected_thermal = {"970": 4.837, "485": 2.418, "440": 2.194}
    fail(errors, len(thermal) == 3, "expected three thermal screens")
    for row in thermal:
        fail(errors, abs(float(row["plaskolite_guideline_mm"]) - expected_thermal[row["dimension_mm"]]) < 0.002, f"thermal screen mismatch for {row['dimension_mm']}")
        fail(errors, "GUIDELINE" in row["state"], "thermal result must remain a guideline")

    decisions = read_csv("guard-retention-decisions.csv")
    fail(errors, len(decisions) == 3, "expected three retention decisions")
    disposition = {row["candidate_id"]: row["disposition"] for row in decisions}
    fail(errors, disposition.get("GRET-001") == "EXCLUDED FROM CURRENT RETENTION BASELINE", "20-2496 must be excluded")
    fail(errors, disposition.get("GRET-002") == "EXACT EVALUATION CANDIDATE; NOT SELECTED", "12004 branch state changed")
    fail(errors, disposition.get("GRET-003") == "DESIGN REQUIRED", "6 mm continuous route must remain open")

    controls = read_csv("guard-retention-controls.csv")
    fail(errors, len(controls) == 8, "expected eight retention controls")
    fail(errors, all(row["state"] not in {"CLOSED", "PASS", "RELEASED"} for row in controls), "retention control improperly closed")
    sources = read_csv("guard-retention-source-register.csv")
    fail(errors, len(sources) == 5, "expected five primary-source rows")
    fail(errors, all(row["url"].startswith("https://") and "accessed 2026-08-07" in row["revision_or_date"] for row in sources), "source URL/date control failed")

    html = (OUT / "HR-V0_guard-retention-study.html").read_text(encoding="utf-8")
    for token in ("font:16px", "19.416 kg", "20-2496", "12004", "NOT APPROVED", "no safety or fabrication release"):
        fail(errors, token in html, f"interactive guide missing {token!r}")

    if errors:
        raise SystemExit("\n".join(f"ERROR: {error}" for error in errors))
    print("HR-V0 guard retention/mass study check passed: 4 mass branches, 32 gasket pieces, 11 stock lengths, 3 decisions, 8 open controls")
    print("Preferred evaluation branch: 19.415878 kg known subtotal; 11.383920 kg reduction; NOT SELECTED")
    print("PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, MOTION, OR ENERGIZATION")


if __name__ == "__main__":
    main()
