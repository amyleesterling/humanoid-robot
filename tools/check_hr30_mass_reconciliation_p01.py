"""Fail-closed checks for HR-30 P0.1 whole-body mass reconciliation."""

from __future__ import annotations

import csv
import hashlib
import json
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "hr30" / "whole-body-p0.1"
REL = ROOT / "release" / "hr30" / "whole-body-p0.1"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(name: str) -> list[dict]:
    return list(csv.DictReader((SRC / name).open(encoding="utf-8")))


def main() -> int:
    required = {
        "actuator-mass-source-register.csv", "mass-item-reconciliation.csv",
        "link-mass-reconciliation.csv", "mass-reconciliation-summary.json",
        "mass-reconciliation.md", "mass-reconciliation-source.py", "lightweight-architecture-register.csv",
    }
    for name in required:
        require((SRC / name).is_file(), f"missing {name}")
        require((REL / name).is_file() and sha(SRC / name) == sha(REL / name), f"source/release mismatch {name}")
    require(sha(SRC / "mass-reconciliation-source.py") == sha(ROOT / "tools" / "generate_hr30_mass_reconciliation_p01.py"), "generator snapshot drift")

    source = {row["model"]: row for row in rows("actuator-mass-source-register.csv")}
    expected = {
        "ROBOTIS XH540-W270-R": 0.165,
        "ROBOTIS XM540-W270-R": 0.165,
        "ROBOTIS XM430-W350-R": 0.082,
        "ROBOTIS XC330-T288-T": 0.023,
    }
    require(set(source) == set(expected), "actuator source set drift")
    for model, mass in expected.items():
        row = source[model]
        require(abs(float(row["published_mass_kg"]) - mass) < 1e-12, f"published mass drift {model}")
        require(row["official_url"].startswith("https://emanual.robotis.com/"), f"nonofficial source {model}")
        require(row["accessed_date"] == "2026-08-14" and row["document_revision_or_date"] == "NOT PUBLISHED ON LIVE PAGE", f"source date/revision disclosure drift {model}")

    items = rows("mass-item-reconciliation.csv")
    require(len(items) == len({row["item_id"] for row in items}) == 296, "mass item identity/count drift")
    categories = Counter(row["category"] for row in items)
    require(categories == Counter({
        "JOINT HARDWARE CAD DENSITY SCREEN": 142,
        "FABRICATION CAD DENSITY SCREEN": 66,
        "MANUFACTURER PUBLISHED ACTUATOR MASS": 25,
        "MANUFACTURER PUBLISHED TRANSMISSION MASS": 10,
        "INSTALLED EQUIPMENT / HARNESS PLANNING MASS": 53,
    }), "mass category population drift")
    actuator_rows = [row for row in items if row["category"] == "MANUFACTURER PUBLISHED ACTUATOR MASS"]
    require(abs(sum(float(row["planning_candidate_mass_kg"]) for row in actuator_rows) - 2.609) < 1e-9, "actuator planning mass drift")
    elbows = [row for row in actuator_rows if "ELBOW" in row["item_id"]]
    require(len(elbows) == 2 and all(row["candidate_material_or_model"] == "ROBOTIS XM430-W350-R" for row in elbows), "whole-body elbow XM430 candidate mass not preserved")
    bearing_rows = [row for row in items if "_BEARING_" in row["source_component"]]
    require(len(bearing_rows) == 39 and abs(sum(float(row["planning_candidate_mass_kg"]) for row in bearing_rows) - 0.34252) < 1e-9, "catalogue bearing mass population drift")
    require(all("APPLICATION SELECTION REQUIRED" in row["selection_state"] and row["density_screen_kg_m3"] == "N/A" for row in bearing_rows), "bearing mass/application boundary missing")
    require(all(float(row["minimum_candidate_mass_kg"]) <= float(row["planning_candidate_mass_kg"]) <= float(row["maximum_candidate_mass_kg"]) for row in items), "mass bound ordering invalid")

    summary = json.loads((SRC / "mass-reconciliation-summary.json").read_text(encoding="utf-8"))
    for category, key in (
        ("FABRICATION CAD DENSITY SCREEN", "fabrication_cad_density_screen_kg"),
        ("MANUFACTURER PUBLISHED ACTUATOR MASS", "actuator_published_mass_planning_kg"),
        ("JOINT HARDWARE CAD DENSITY SCREEN", "joint_hardware_gross_density_screen_kg"),
        ("MANUFACTURER PUBLISHED TRANSMISSION MASS", "transmission_belt_published_mass_kg"),
        ("INSTALLED EQUIPMENT / HARNESS PLANNING MASS", "installed_equipment_harness_planning_mass_kg"),
    ):
        actual = sum(float(row["planning_candidate_mass_kg"]) for row in items if row["category"] == category)
        require(abs(actual - float(summary[key])) < 2e-9, f"summary category mismatch {category}")
    identified = sum(float(row["planning_candidate_mass_kg"]) for row in items)
    require(abs(identified - float(summary["planning_identified_candidate_mass_kg"])) < 2e-9, "identified subtotal mismatch")
    require(9.2 < identified < 9.3, "tether-first identified subtotal outside controlled P0.1 band")
    require(summary["program_mass_target_status"] == "NOT YET EXCEEDED BUT UNMODELED MASS REMAINS" and 0 < summary["planning_margin_to_program_maximum_kg"] < 0.01, "narrow 10 kg planning margin not disclosed")
    require(not any(summary["authority"].values()), "mass package authority overclaim")

    decisions = rows("lightweight-architecture-register.csv")
    require(len(decisions) == 10 and {row["decision_id"] for row in decisions} >= {"HR30-LW-001", "HR30-LW-004", "HR30-LW-005", "HR30-LW-007", "HR30-LW-008", "HR30-LW-009", "HR30-LW-TOTAL"}, "lightweight architecture decision set incomplete")
    total_decision = next(row for row in decisions if row["decision_id"] == "HR30-LW-TOTAL")
    require("dfb9a7d" in total_decision["baseline_candidate"] and "gross identified reduction" in total_decision["mass_effect"], "lightweight baseline/delta traceability missing")
    require(all(row["authority"].startswith("NO PROCUREMENT") for row in decisions), "lightweight decision authority overclaim")

    links = rows("link-mass-reconciliation.csv")
    require(len(links) == 26 and len({row["dynamic_link"] for row in links}) == 26, "link reconciliation population drift")
    for row in links:
        baseline = float(row["baseline_allocation_kg"])
        identified_link = float(row["identified_planning_candidate_kg"])
        reconciled = float(row["reconciled_dynamics_mass_kg"])
        contingency = float(row["integration_contingency_kg"])
        require(abs(contingency - identified_link * 0.08) < 2e-9, f"integration contingency mismatch {row['dynamic_link']}")
        require(abs(reconciled - (identified_link + contingency)) < 2e-9, f"link planning rule mismatch {row['dynamic_link']}")
    reconciled_total = sum(float(row["reconciled_dynamics_mass_kg"]) for row in links)
    require(abs(reconciled_total - float(summary["reconciled_dynamics_planning_mass_kg"])) < 2e-9, "reconciled total mismatch")

    urdf = ET.parse(SRC / "hr30.urdf").getroot()
    urdf_mass = sum(float(node.find("inertial/mass").get("value")) for node in urdf.findall("link"))
    mjcf = ET.parse(SRC / "hr30.xml").getroot()
    mjcf_mass = sum(float(node.get("mass")) for node in mjcf.findall("./worldbody//inertial"))
    require(abs(urdf_mass - reconciled_total) < 5e-6, "URDF mass not reconciled")
    require(abs(mjcf_mass - reconciled_total) < 5e-6, "MJCF mass not reconciled")
    budget = rows("mass-properties-budget.csv")[-1]
    require(budget["link"] == "TOTAL" and abs(float(budget["allocated_mass_kg"]) - reconciled_total) < 2e-6, "mass-properties total not reconciled")

    allocation = {row["assembly"]: row for row in rows("mass-allocation-register.csv")}
    require(abs(float(allocation["TOTAL"]["cad_mass_kg"].split()[-1]) - round(reconciled_total, 3)) < 0.001, "allocation register total does not match reconciliation")
    require("INCOMPLETE PLANNING MODEL" in allocation["TOTAL"]["status"], "allocation register does not expose narrow/incomplete mass screen")
    require("8% OF EXPLICIT" in allocation["integration contingency within link totals"]["cad_mass_kg"], "integration contingency not explicit")

    status = json.loads((SRC / "package-status.json").read_text(encoding="utf-8"))
    require(status["mass_reconciliation_present"] and not status["mass_budget_closed"] and not status["mass_com_inertia_physically_validated"], "main package mass status overclaim")
    require(abs(float(status["estimated_mass_kg"]) - reconciled_total) < 2e-9, "main package mass drift")
    require(not any(status[key] for key in ("procurement_authority", "fabrication_authority", "powered_test_authority", "motion_authority", "energization_authority")), "main package authority overclaim")
    page = (SRC / "index.html").read_text(encoding="utf-8")
    require("mass-reconciliation.md" in page and "mass-item-reconciliation.csv" in page and "lightweight-architecture-register.csv" in page and f"{reconciled_total:.3f} kg tether-first planning" in page, "web guide mass reconciliation missing")
    require("onboard energy" in page.lower(), "web guide hides onboard-energy boundary")
    print(f"PASS: HR-30 mass reconciliation inventories 296 candidate items including 53 located equipment/harness items, 10 published belt masses, 2.609 kg published actuator mass and 39 catalogue bearing candidates, {identified:.3f} kg tether-first identified mass and {reconciled_total:.3f} kg dynamics mass with only {summary['planning_margin_to_program_maximum_kg']:.3f} kg nominal margin; mass closure and all physical/authority gates remain open")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
