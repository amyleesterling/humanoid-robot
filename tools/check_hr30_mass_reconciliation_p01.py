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
        "link-mass-reconciliation-tether.csv", "mass-properties-budget-tether.csv",
        "mass-configuration-register.csv", "hr30_tether.urdf", "hr30_tether.xml",
        "hr30_onboard_envelope.urdf", "hr30_onboard_envelope.xml",
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
    require(len(items) == len({row["item_id"] for row in items}) == 489, "mass item identity/count drift")
    categories = Counter(row["category"] for row in items)
    require(categories == Counter({
        "JOINT HARDWARE CAD DENSITY SCREEN": 142,
        "LOCATED JOINT FASTENER CAD DENSITY SCREEN": 156,
        "FABRICATION CAD DENSITY SCREEN": 98,
        "MANUFACTURER PUBLISHED ACTUATOR MASS": 25,
        "MANUFACTURER PUBLISHED TRANSMISSION MASS": 10,
        "INSTALLED EQUIPMENT / HARNESS PLANNING MASS": 58,
    }), "mass category population drift")
    actuator_rows = [row for row in items if row["category"] == "MANUFACTURER PUBLISHED ACTUATOR MASS"]
    require(abs(sum(float(row["planning_candidate_mass_kg"]) for row in actuator_rows) - 2.609) < 1e-9, "actuator planning mass drift")
    elbows = [row for row in actuator_rows if "ELBOW" in row["item_id"]]
    require(len(elbows) == 2 and all(row["candidate_material_or_model"] == "ROBOTIS XM430-W350-R" for row in elbows), "whole-body elbow XM430 candidate mass not preserved")
    bearing_rows = [row for row in items if "_BEARING_" in row["source_component"]]
    require(len(bearing_rows) == 39 and abs(sum(float(row["planning_candidate_mass_kg"]) for row in bearing_rows) - 0.34252) < 1e-9, "catalogue bearing mass population drift")
    require(all("APPLICATION SELECTION REQUIRED" in row["selection_state"] and row["density_screen_kg_m3"] == "N/A" for row in bearing_rows), "bearing mass/application boundary missing")
    require(all(float(row["minimum_candidate_mass_kg"]) <= float(row["planning_candidate_mass_kg"]) <= float(row["maximum_candidate_mass_kg"]) for row in items), "mass bound ordering invalid")
    onboard_envelope_ids = {
        "EQ-T01-BATTERY-PACK", "EQ-T01-BATTERY-CASSETTE", "EQ-T01-BATTERY-PROTECTION",
    }
    envelope_items = [row for row in items if row["item_id"] in onboard_envelope_ids]
    require({row["item_id"] for row in envelope_items} == onboard_envelope_ids, "onboard envelope item set drift")
    excluded_envelope_mass = sum(float(row["planning_candidate_mass_kg"]) for row in envelope_items)
    require(abs(excluded_envelope_mass - 1.357) < 2e-9, "onboard envelope exclusion mass drift")
    require("REJECTED direct source" in next(row for row in envelope_items if row["item_id"] == "EQ-T01-BATTERY-PACK")["candidate_material_or_model"], "rejected direct-source pack boundary missing")
    fastener_rows = [row for row in items if row["category"] == "LOCATED JOINT FASTENER CAD DENSITY SCREEN"]
    require(len(fastener_rows) == 156 and abs(sum(float(row["planning_candidate_mass_kg"]) for row in fastener_rows) - 0.554224112) < 2e-9, "located fastener mass population drift")
    hand_fabrication_rows = [row for row in items if row["category"] == "FABRICATION CAD DENSITY SCREEN" and row["source_component"].startswith(("G01_", "G02_"))]
    require(len(hand_fabrication_rows) == 34, "both seventeen-part custom grippers are not represented in the mass model")

    summary = json.loads((SRC / "mass-reconciliation-summary.json").read_text(encoding="utf-8"))
    for category, key in (
        ("FABRICATION CAD DENSITY SCREEN", "fabrication_cad_density_screen_kg"),
        ("MANUFACTURER PUBLISHED ACTUATOR MASS", "actuator_published_mass_planning_kg"),
        ("JOINT HARDWARE CAD DENSITY SCREEN", "joint_hardware_gross_density_screen_kg"),
        ("LOCATED JOINT FASTENER CAD DENSITY SCREEN", "located_joint_fastener_planning_mass_kg"),
        ("MANUFACTURER PUBLISHED TRANSMISSION MASS", "transmission_belt_published_mass_kg"),
        ("INSTALLED EQUIPMENT / HARNESS PLANNING MASS", "installed_equipment_harness_planning_mass_kg"),
    ):
        actual = sum(float(row["planning_candidate_mass_kg"]) for row in items if row["category"] == category)
        require(abs(actual - float(summary[key])) < 2e-9, f"summary category mismatch {category}")
    identified = sum(float(row["planning_candidate_mass_kg"]) for row in items)
    require(abs(identified - float(summary["planning_identified_candidate_mass_kg"])) < 2e-9, "identified subtotal mismatch")
    require(11.45 < identified < 11.60, "installed-equipment/onboard-energy identified subtotal outside controlled P0.1 band")
    require(summary["located_joint_fastener_count"] == 156, "fastener count missing from mass summary")
    require(summary["program_mass_target_status"].startswith("WITHIN P0.1 MAXIMUM") and 0.0 < summary["planning_margin_to_program_maximum_kg"] < 0.15, "narrow 12 kg P0.1 planning margin not disclosed")
    require(-2.0 < summary["planning_margin_to_lightweight_stretch_kg"] < -1.8, "10 kg lightweight stretch miss not disclosed")
    require(not any(summary["authority"].values()), "mass package authority overclaim")
    require(summary["configuration_mass_separation_present"], "mass configuration separation missing")
    require(summary["active_development_configuration"] == "HR30-TETHER-FIRST-P0.1", "active mass configuration drift")
    require(abs(float(summary["excluded_onboard_envelope_identified_mass_kg"]) - excluded_envelope_mass) < 2e-9, "excluded envelope mass summary drift")
    require(abs(float(summary["onboard_envelope_dynamics_planning_mass_kg"]) - float(summary["reconciled_dynamics_planning_mass_kg"])) < 2e-9, "onboard envelope dynamics alias drift")
    require(10.3 < float(summary["active_tether_dynamics_planning_mass_kg"]) < 10.7, "active tether mass outside controlled P0.1 band")
    require(1.3 < float(summary["active_tether_margin_to_program_maximum_kg"]) < 1.7, "active tether margin outside controlled P0.1 band")

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
        fastener_link = float(row["explicit_joint_fastener_candidate_kg"])
        contingency_before = float(row["integration_contingency_before_fastener_allocation_kg"])
        contingency = float(row["integration_contingency_kg"])
        require(abs(contingency_before - (identified_link - fastener_link) * 0.08) < 2e-9, f"pre-fastener contingency mismatch {row['dynamic_link']}")
        require(abs(contingency - max(0.0, contingency_before - fastener_link)) < 2e-9, f"remaining contingency mismatch {row['dynamic_link']}")
        require(abs(reconciled - (identified_link + contingency)) < 2e-9, f"link planning rule mismatch {row['dynamic_link']}")
    reconciled_total = sum(float(row["reconciled_dynamics_mass_kg"]) for row in links)
    require(abs(reconciled_total - float(summary["reconciled_dynamics_planning_mass_kg"])) < 2e-9, "reconciled total mismatch")
    tether_links = rows("link-mass-reconciliation-tether.csv")
    require(len(tether_links) == 26 and len({row["dynamic_link"] for row in tether_links}) == 26, "tether link reconciliation population drift")
    tether_total = sum(float(row["reconciled_dynamics_mass_kg"]) for row in tether_links)
    require(abs(tether_total - float(summary["active_tether_dynamics_planning_mass_kg"])) < 2e-9, "tether dynamics total mismatch")
    require(float(next(row for row in tether_links if row["dynamic_link"] == "torso")["identified_planning_candidate_kg"]) < float(next(row for row in links if row["dynamic_link"] == "torso")["identified_planning_candidate_kg"]), "tether torso does not exclude onboard envelope")

    urdf = ET.parse(SRC / "hr30.urdf").getroot()
    urdf_mass = sum(float(node.find("inertial/mass").get("value")) for node in urdf.findall("link"))
    mjcf = ET.parse(SRC / "hr30.xml").getroot()
    mjcf_mass = sum(float(node.get("mass")) for node in mjcf.findall("./worldbody//inertial"))
    require(abs(urdf_mass - reconciled_total) < 5e-6, "URDF mass not reconciled")
    require(abs(mjcf_mass - reconciled_total) < 5e-6, "MJCF mass not reconciled")
    tether_urdf = ET.parse(SRC / "hr30_tether.urdf").getroot()
    tether_urdf_mass = sum(float(node.find("inertial/mass").get("value")) for node in tether_urdf.findall("link"))
    tether_mjcf = ET.parse(SRC / "hr30_tether.xml").getroot()
    tether_mjcf_mass = sum(float(node.get("mass")) for node in tether_mjcf.findall("./worldbody//inertial"))
    require(abs(tether_urdf_mass - tether_total) < 5e-6 and abs(tether_mjcf_mass - tether_total) < 5e-6, "tether dynamics artifacts not reconciled")
    require(sha(SRC / "hr30.urdf") == sha(SRC / "hr30_onboard_envelope.urdf") and sha(SRC / "hr30.xml") == sha(SRC / "hr30_onboard_envelope.xml"), "default/onboard-envelope artifact identity drift")
    configurations = {row["configuration_id"]: row for row in rows("mass-configuration-register.csv")}
    require(set(configurations) == {"HR30-TETHER-FIRST-P0.1", "HR30-ONBOARD-ENVELOPE-P0.1"}, "mass configuration register drift")
    require(configurations["HR30-TETHER-FIRST-P0.1"]["program_role"] == "ACTIVE CONTROLLED DEVELOPMENT BASELINE", "tether configuration role drift")
    require("REJECTED" in configurations["HR30-ONBOARD-ENVELOPE-P0.1"]["selection_state"], "onboard-envelope rejection boundary missing")
    require(all(row["authority"].startswith("NO PROCUREMENT") for row in configurations.values()), "mass configuration authority overclaim")
    budget = rows("mass-properties-budget.csv")[-1]
    require(budget["link"] == "TOTAL" and abs(float(budget["allocated_mass_kg"]) - reconciled_total) < 2e-6, "mass-properties total not reconciled")

    allocation = {row["assembly"]: row for row in rows("mass-allocation-register.csv")}
    require(abs(float(allocation["TOTAL"]["cad_mass_kg"].split()[-1]) - round(reconciled_total, 3)) < 0.001, "allocation register total does not match reconciliation")
    require("WITHIN MAXIMUM" in allocation["TOTAL"]["status"], "allocation register does not expose the provisional P0.1 mass-envelope status")
    require("RESIDUAL" in allocation["integration contingency within link totals"]["cad_mass_kg"] and "EXPLICIT JOINT FASTENERS" in allocation["integration contingency within link totals"]["cad_mass_kg"], "fastener allocation against contingency not explicit")

    status = json.loads((SRC / "package-status.json").read_text(encoding="utf-8"))
    require(status["mass_reconciliation_present"] and not status["mass_budget_closed"] and not status["mass_com_inertia_physically_validated"], "main package mass status overclaim")
    require(abs(float(status["estimated_mass_kg"]) - reconciled_total) < 2e-9, "main package mass drift")
    require(status["mass_configuration_separation_present"] and status["active_development_mass_configuration"] == "HR30-TETHER-FIRST-P0.1", "main package active mass configuration missing")
    require(abs(float(status["active_tether_development_mass_kg"]) - tether_total) < 2e-9 and not status["onboard_energy_envelope_active"], "main package tether/onboard mass state drift")
    require(not any(status[key] for key in ("procurement_authority", "fabrication_authority", "powered_test_authority", "motion_authority", "energization_authority")), "main package authority overclaim")
    page = (SRC / "index.html").read_text(encoding="utf-8")
    require("mass-reconciliation.md" in page and "mass-item-reconciliation.csv" in page and "mass-configuration-register.csv" in page and "mass-properties-budget-tether.csv" in page and "lightweight-architecture-register.csv" in page, "web guide mass reconciliation links missing")
    require(f"{tether_total:.3f} kg active tether-first" in page and f"{reconciled_total:.3f} kg onboard-envelope" in page, "web guide configuration masses missing")
    print(f"PASS: HR-30 mass reconciliation inventories 489 candidate items and separates the {tether_total:.3f} kg active tether-first dynamics model from the {reconciled_total:.3f} kg onboard-envelope planning case; exactly {excluded_envelope_mass:.3f} kg of rejected-pack/cassette/protection packaging evidence is excluded only from the active configuration; physical closure and all authority gates remain open")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
