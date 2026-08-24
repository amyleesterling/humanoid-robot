"""Fail-closed validation for the integrated HR-30 LIGHT4 candidate."""

from __future__ import annotations

import csv
import hashlib
import json
import xml.etree.ElementTree as ET
from pathlib import Path

import mujoco

ROOT = Path(__file__).resolve().parents[1]
BODY = ROOT / "hr30" / "whole-body-p0.1"
PKG = BODY / "active-light4-p0.1"
REL = ROOT / "release" / "hr30" / "whole-body-p0.1" / PKG.name
TARGET = 9.879813509


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def main() -> int:
    status = json.loads((PKG / "active-light4-status.json").read_text(encoding="utf-8"))
    required_true = (
        "complete_humanoid_geometry_bound", "mujoco_model_compiles",
        "mujoco_model_mass_matches_reconciliation", "fresh_inverse_dynamics_executed",
        "inverse_demand_within_linear_current_endpoints", "fresh_bounded_control_executed",
        "bounded_control_screen_pass",
    )
    if not all(status.get(key) is True for key in required_true):
        fail("required model/simulation gate is not true")
    if abs(float(status["mass_kg"]) - TARGET) > 5e-9 or float(status["margin_to_10kg_kg"]) <= 0:
        fail("mass reconciliation drift")
    for key, value in status.items():
        if key.endswith("authority") and value is not False:
            fail(f"authority escaped fail-closed boundary: {key}")
    if status.get("physical_mass_validated") or status.get("continuous_capacity_validated") or status.get("free_balance_validated"):
        fail("physical validation overclaim")

    manifest = rows(PKG / "file-manifest.csv")
    actual = sorted(path.name for path in PKG.iterdir() if path.is_file() and path.name != "file-manifest.csv")
    if sorted(row["file"] for row in manifest) != actual:
        fail("package manifest file set mismatch")
    for row in manifest:
        path = PKG / row["file"]
        if sha(path) != row["sha256"] or path.stat().st_size != int(row["bytes"]):
            fail(f"manifest mismatch: {path.name}")
    source_rows = rows(PKG / "source-binding.csv")
    if len(source_rows) < 16:
        fail("source binding incomplete")
    for row in source_rows:
        path = ROOT / row["path"]
        if not path.is_file() or sha(path) != row["sha256"]:
            fail(f"source binding mismatch: {row['role']}")

    urdf = ET.parse(PKG / "hr30_tether_light4_active.urdf").getroot()
    urdf_mass = sum(float(node.get("value")) for node in urdf.findall("./link/inertial/mass"))
    reductions = {node.text for node in urdf.findall("./transmission/actuator/mechanicalReduction")}
    if abs(urdf_mass - TARGET) > 5e-6 or reductions != {"4.0"} or len(urdf.findall("./transmission")) != 4:
        fail("URDF mass or hip reductions mismatch")
    model = mujoco.MjModel.from_xml_path(str((PKG / "hr30_tether_light4_ideal_fixture.xml").resolve()))
    if abs(float(model.body_subtreemass[1]) - TARGET) > 5e-6 or model.nu != 25 or model.nmocap != 1:
        fail("compiled MJCF topology/mass mismatch")
    link_rows = rows(PKG / "link-mass-reconciliation.csv")
    if len(link_rows) != 26 or sum(int(row["removed_item_count"]) for row in link_rows) != 68 or sum(int(row["added_item_count"]) for row in link_rows) != 52:
        fail("link/item reconciliation mismatch")
    demands = rows(PKG / "whole-body-axis-demand.csv")
    if len(demands) != 23 or any(not row["endpoint_state"].startswith("WITHIN") for row in demands):
        fail("inverse-demand endpoint screen mismatch")
    sequence_demand = rows(PKG / "sequence-demand-summary.csv")
    if len(sequence_demand) != 2 or any(row["axes_exceeding_candidate_current_endpoint"] != "NONE" or not row["result"].startswith("WITHIN LIGHT4") for row in sequence_demand):
        fail("sequence demand summary does not use LIGHT4 endpoints")
    sequence = rows(PKG / "sequence-control-summary.csv")
    if len(sequence) != 2 or any(not row["result"].startswith("PASS") for row in sequence):
        fail("bounded control sequences do not pass")
    axes = rows(PKG / "axis-control-results.csv")
    if len(axes) != 50 or any(row["screen_state"].startswith("FAIL") for row in axes):
        fail("axis control screen mismatch")

    if not REL.is_dir():
        fail("release mirror missing")
    source_files = sorted(path.relative_to(PKG).as_posix() for path in PKG.rglob("*") if path.is_file())
    release_files = sorted(path.relative_to(REL).as_posix() for path in REL.rglob("*") if path.is_file())
    if source_files != release_files:
        fail("release mirror file set mismatch")
    for name in source_files:
        if sha(PKG / name) != sha(REL / name):
            fail(f"release mirror mismatch: {name}")
    package = json.loads((BODY / "package-status.json").read_text(encoding="utf-8"))
    if package.get("active_whole_body_engineering_candidate") != "HR30-TETHER-LIGHT4-P0.1":
        fail("root package did not promote integrated candidate")
    print("PASS: LIGHT4 CAD, mass model, URDF/MJCF, fresh inverse dynamics and bounded control are synchronized; all physical/work authorities remain false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
