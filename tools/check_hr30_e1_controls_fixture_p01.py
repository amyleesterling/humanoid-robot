#!/usr/bin/env python3
"""Fail-closed checker for the HR-30 E1 controls-only fixture P0.1."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import cadquery as cq


ROOT = Path(__file__).resolve().parents[1]
BODY = ROOT / "hr30" / "whole-body-p0.1"
OUT = BODY / "electrical/e1-controls-only-fixture-p0.1"
REL = ROOT / "release/hr30/whole-body-p0.1/electrical/e1-controls-only-fixture-p0.1"
WARNING = (
    "PRELIMINARY - UNBUILT CONTROLS-ONLY FIXTURE CANDIDATE - NOT APPROVED "
    "FOR CONNECTION, POWERED TESTING, MOTION, WALKING, OR ENERGIZATION"
)
EXPECTED_BUSES = {
    "RS-LLEG", "RS-RLEG", "RS-LARM", "RS-RARM",
    "RS-WAIST", "TTL-LDIST", "TTL-RDIST", "TTL-HEAD",
}


def need(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    required = {
        "README.md", "index.html", "e1-fixture-status.json",
        "HR30_E1_controls_only_fixture_candidate.step",
        "HR30_E1_controls_only_fixture_candidate.glb",
        "HR30_E1_base_panel_candidate.step", "HR30_E1_base_panel_candidate.dxf",
        "HR30_E1_carrier_field_port_cover_candidate.step",
        "HR30_E1_carrier_field_port_cover_candidate.stl",
        "mcu-native-pcb.step", "carrier_a-native-pcb.step",
        "carrier_b-native-pcb.step", "swd-native-pcb.step",
        "kicad-board-export.log", "pcb-placement-register.csv",
        "mount-hole-register.csv", "field-port-exclusion-register.csv",
        "e1-configuration-register.csv", "connector-boundary-register.csv",
        "candidate-bom.csv", "assembly-sequence.csv", "source-binding.csv",
        "open-holds.csv", "e1-controls-fixture-source.py", "file-manifest.csv",
    }
    source_files = {path.name for path in OUT.iterdir() if path.is_file()}
    release_files = {path.name for path in REL.iterdir() if path.is_file()}
    need(source_files == required, f"source file set drift: {sorted(source_files ^ required)}")
    need(release_files == required, f"release file set drift: {sorted(release_files ^ required)}")
    for name in required:
        need(sha(OUT / name) == sha(REL / name), f"source/release mismatch {name}")
    need(
        sha(OUT / "e1-controls-fixture-source.py")
        == sha(ROOT / "tools/generate_hr30_e1_controls_fixture_p01.py"),
        "generator snapshot drift",
    )

    bindings = rows(OUT / "source-binding.csv")
    need(len(bindings) == 9 and len({row["role"] for row in bindings}) == 9, "source binding count drift")
    for row in bindings:
        path = ROOT / row["path"]
        need(path.is_file() and sha(path) == row["sha256"] and row["state"] == "BOUND", f"source binding mismatch {row['role']}")

    boards = rows(OUT / "pcb-placement-register.csv")
    need(len(boards) == 4 and {row["board_id"] for row in boards} == {"MCU", "CARRIER_A", "CARRIER_B", "SWD"}, "board population drift")
    need(sum(int(row["mount_hole_count"]) for row in boards) == 14, "board mount-hole aggregate drift")
    for row in boards:
        source = ROOT / row["native_pcb"]
        need(source.is_file() and sha(source) == row["native_pcb_sha256"], f"native PCB hash drift {row['board_id']}")
        need((OUT / row["exported_step"]).is_file(), f"missing board STEP {row['board_id']}")

    holes = rows(OUT / "mount-hole-register.csv")
    need(len(holes) == 14 and len({row["hole_id"] for row in holes}) == 14, "mount-hole register drift")
    need(len({(row["panel_x_mm"], row["panel_y_mm"]) for row in holes}) == 14, "duplicate panel hole axes")
    need(all(float(row["native_hole_diameter_mm"]) == 2.7 and float(row["panel_clearance_diameter_mm"]) == 3.0 for row in holes), "mount-hole diameter drift")

    ports = rows(OUT / "field-port-exclusion-register.csv")
    need(len(ports) == 8 and {row["whole_body_bus"] for row in ports} == EXPECTED_BUSES, "field-port coverage drift")
    need(len({row["port_id"] for row in ports}) == 8, "duplicate field-port identity")
    need(all(row["power_contact_present"] == "NO - DATA-ONLY INTERFACE" for row in ports), "power contact introduced at field port")
    need(all("NO EXTERNAL OPENING" in row["e1_physical_state"] for row in ports), "field port not physically enclosed")

    stages = rows(OUT / "e1-configuration-register.csv")
    need([row["stage"] for row in stages] == ["E1-A", "E1-B", "E1-C"], "E1 stage sequence drift")
    need(all(row["execution"] == "NOT EXECUTED" for row in stages), "unexecuted fixture presented as executed")
    boundaries = rows(OUT / "connector-boundary-register.csv")
    need({row["boundary"] for row in boundaries} == {"J1", "JDBG1", "JMCU_A", "JMCU_B", "FIELD_PORTS", "ACTUATOR_POWER"}, "connector boundary drift")
    actuator_power = next(row for row in boundaries if row["boundary"] == "ACTUATOR_POWER")
    need(actuator_power["allowed_on_fixture"] == "NONE" and "NO CONNECTOR" in actuator_power["e1_state"], "actuator-power exclusion weakened")

    status = json.loads((OUT / "e1-fixture-status.json").read_text(encoding="utf-8"))
    need(status["native_board_count"] == 4 and status["native_board_step_export_count"] == 4, "status board count drift")
    need(status["native_mount_hole_count"] == 14 and status["sealed_carrier_cover_count"] == 2, "status geometry count drift")
    need(status["actuator_field_port_count"] == 8 and status["actuator_field_ports_physically_covered_in_cad"], "status port coverage drift")
    need(not any(status[key] for key in (
        "actuator_power_connectors_present", "actuator_power_conductors_present",
        "actuator_pdu_present", "actuator_present", "fixture_built", "native_pcbs_built",
        "received_fit_validated", "wiring_built_or_inspected", "firmware_flashed",
        "hil_executed", "connection_authority", "powered_test_authority",
        "motion_authority", "walking_authority", "energization_authority",
    )), "fixture status overclaim or actuator-power path introduced")

    assembly = cq.importers.importStep(str(OUT / "HR30_E1_controls_only_fixture_candidate.step")).val()
    bounds = assembly.BoundingBox()
    need(abs(bounds.xlen - 360.009328) < 0.02 and abs(bounds.ylen - 240.009328) < 0.02, "assembly footprint drift")
    need(54.9 < bounds.zlen < 55.2, "assembly height drift")
    base = cq.importers.importStep(str(OUT / "HR30_E1_base_panel_candidate.step")).val()
    base_bounds = base.BoundingBox()
    need(abs(base_bounds.xlen - 360.0) < 0.02 and abs(base_bounds.ylen - 240.0) < 0.02 and abs(base_bounds.zlen - 6.0) < 0.02, "base panel dimensions drift")
    need((OUT / "HR30_E1_controls_only_fixture_candidate.glb").stat().st_size > 500_000, "GLB is implausibly small")

    holds = rows(OUT / "open-holds.csv")
    need(len(holds) == 8 and all(row["state"] == "OPEN" for row in holds), "E1 open-hold drift")
    log = (OUT / "kicad-board-export.log").read_text(encoding="utf-8")
    need(log.count("exit=0") == 4, "KiCad board export count/result drift")
    need("Could not add 3D model" in log, "missing-model disclosure unexpectedly absent")

    page = (OUT / "index.html").read_text(encoding="utf-8")
    need("font:17px" in page and "font-size:16px" in page and "font-size:14px" in page, "E1 guide violates legibility floor")
    need("<model-viewer" in page and "HR30_E1_controls_only_fixture_candidate.glb" in page, "interactive model missing")
    need("This guide cannot authorize connection or power" in page, "authority boundary missing from guide")
    root_readme = (BODY / "README.md").read_text(encoding="utf-8")
    root_page = (BODY / "index.html").read_text(encoding="utf-8")
    need(root_readme.count("HR30-E1-CONTROLS-FIXTURE-P01-START") == 1, "root README marker drift")
    need(root_page.count("HR30-E1-CONTROLS-FIXTURE-P01-START") == 1, "root page marker drift")
    package_status = json.loads((BODY / "package-status.json").read_text(encoding="utf-8"))
    need(package_status["e1_controls_only_fixture_present"] and package_status["e1_native_pcb_count"] == 4, "root E1 status absent")
    need(package_status["e1_actuator_power_component_count"] == 0, "root status introduces actuator power")
    need(not package_status["e1_fixture_built"] and not package_status["e1_connection_authority"] and not package_status["e1_powered_test_authority"], "root E1 authority overclaim")

    manifest = rows(OUT / "file-manifest.csv")
    need(len(manifest) == len(required) - 1 and len({row["file"] for row in manifest}) == len(manifest), "package manifest population drift")
    for row in manifest:
        path = OUT / row["file"]
        need(path.is_file() and int(row["bytes"]) == path.stat().st_size and row["sha256"] == sha(path), f"manifest mismatch {row['file']}")
        need(row["warning"] == WARNING, f"manifest warning drift {row['file']}")

    print("PASS: HR-30 E1 fixture uses 4 native PCBs / 14 exact mount axes, encloses all 8 data field ports, contains zero actuator-power hardware, and keeps every physical/authority gate false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
