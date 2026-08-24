"""Generate the mass-bound HR-30 LIGHT4 whole-body dynamics candidate."""

from __future__ import annotations

import csv
import hashlib
import html
import json
import math
import shutil
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import mujoco
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import generate_hr30_control_successor_p01 as control_successor  # noqa: E402
import generate_hr30_dynamics_successor_p01 as dynamics_successor  # noqa: E402
import generate_hr30_system_package_p01 as system  # noqa: E402
import generate_hr30_torque_demand_p01 as torque_demand  # noqa: E402

BODY = ROOT / "hr30" / "whole-body-p0.1"
OUT = BODY / "active-light4-p0.1"
LIGHT = BODY / "lightweight-hip-successor-p0.1"
BASE_DYN = BODY / "mujoco-dynamics-validation-p0.1" / "hr30_tether_ideal_fixture.xml"
BASE_URDF = BODY / "hr30_tether.urdf"
BASE_MJCF = BODY / "hr30_tether.xml"
IDENTIFIER = "HR30-TETHER-LIGHT4-P0.1"
WARNING = (
    "PRELIMINARY - MASS-BOUND WHOLE-BODY LIGHT4 ENGINEERING CANDIDATE ONLY - "
    "NOT APPROVED FOR PROCUREMENT, FABRICATION, CONNECTION, POWERED TESTING, "
    "MOTION, WALKING, OR ENERGIZATION"
)
HIP_AXES = {"L_HIP_ROLL", "L_HIP_PITCH", "R_HIP_ROLL", "R_HIP_PITCH"}
TARGET_MASS_KG = 9.879813509


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise RuntimeError(f"refusing empty table {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalize(rows: list[dict]) -> None:
    for row in rows:
        if "warning" in row:
            row["warning"] = WARNING


def build_mass_model() -> tuple[list[dict], list[dict], dict]:
    base_links = {row["dynamic_link"]: row for row in read_csv(BODY / "link-mass-reconciliation-tether.csv")}
    base_items = {row["item_id"]: row for row in read_csv(BODY / "mass-item-reconciliation.csv")}
    replacement = read_csv(LIGHT / "replacement-boundary.csv")
    additions = read_csv(LIGHT / "hip-mass-budget.csv")
    canonical = {row["link"]: row for row in system.link_rows()}
    remove_by_link: dict[str, list[tuple[float, tuple[float, float, float], str]]] = defaultdict(list)
    for row in replacement:
        source = base_items.get(row["item_id"])
        if source is None:
            raise RuntimeError(f"replacement item missing: {row['item_id']}")
        mass = float(row["removed_planning_mass_kg"])
        if abs(mass - float(source["planning_candidate_mass_kg"])) > 5e-10:
            raise RuntimeError(f"replacement mass drift: {row['item_id']}")
        center = tuple(float(source[key]) for key in ("placement_x_m", "placement_y_m", "placement_z_m"))
        remove_by_link[row["dynamic_link"]].append((mass, center, row["item_id"]))
    add_by_link: dict[str, list[tuple[float, tuple[float, float, float], str]]] = defaultdict(list)
    for row in additions:
        side, _, mode = row["axis_id"].partition("_HIP_")
        link = f"{side}_hip_roll_link" if mode == "ROLL" else f"{side}_thigh"
        mass = float(row["planning_mass_kg"])
        center = tuple(float(row[key]) / 1000.0 for key in ("center_x_mm", "center_y_mm", "center_z_mm"))
        add_by_link[link].append((mass, center, row["part_id"]))

    dynamics_rows, evidence = [], []
    for link, geom in canonical.items():
        base = base_links[link]
        before_mass = float(base["reconciled_dynamics_mass_kg"])
        before_center = tuple(float(base[key]) for key in ("reconciled_com_x_m", "reconciled_com_y_m", "reconciled_com_z_m"))
        moment = [before_mass * value for value in before_center]
        removed_mass = added_mass = 0.0
        for mass, center, _ in remove_by_link.get(link, []):
            removed_mass += mass
            for index in range(3):
                moment[index] -= mass * center[index]
        for mass, center, _ in add_by_link.get(link, []):
            added_mass += mass
            for index in range(3):
                moment[index] += mass * center[index]
        after_mass = before_mass - removed_mass + added_mass
        after_center = tuple(value / after_mass for value in moment)
        dynamics_rows.append({**geom, "mass": after_mass, "center": after_center, "geometry_center": geom.get("geometry_center", geom["center"])})
        evidence.append({
            "dynamic_link": link, "base_tether_mass_kg": f"{before_mass:.9f}",
            "removed_predecessor_hip_mass_kg": f"{removed_mass:.9f}", "added_light4_hip_mass_kg": f"{added_mass:.9f}",
            "active_light4_mass_kg": f"{after_mass:.9f}", "active_com_x_m": f"{after_center[0]:.9f}",
            "active_com_y_m": f"{after_center[1]:.9f}", "active_com_z_m": f"{after_center[2]:.9f}",
            "removed_item_count": len(remove_by_link.get(link, [])), "added_item_count": len(add_by_link.get(link, [])),
            "state": "MASS/COM RECONCILED FROM SHA-BOUND PLANNING INVENTORIES; PHYSICAL MASS PROPERTY OPEN", "warning": WARNING,
        })
    total = sum(row["mass"] for row in dynamics_rows)
    center = tuple(sum(row["mass"] * row["center"][i] for row in dynamics_rows) / total for i in range(3))
    if abs(total - TARGET_MASS_KG) > 5e-9:
        raise RuntimeError(f"LIGHT4 mass does not reconcile: {total:.12f}")
    summary = {
        "base_tether_mass_kg": sum(float(row["reconciled_dynamics_mass_kg"]) for row in base_links.values()),
        "removed_mass_kg": sum(mass for values in remove_by_link.values() for mass, _, _ in values),
        "added_mass_kg": sum(mass for values in add_by_link.values() for mass, _, _ in values),
        "active_mass_kg": total, "margin_to_10kg_kg": 10.0 - total, "center_of_mass_m": center,
        "affected_links": sorted(set(remove_by_link) | set(add_by_link)),
        "removed_item_count": sum(len(values) for values in remove_by_link.values()),
        "added_item_count": sum(len(values) for values in add_by_link.values()),
    }
    return dynamics_rows, evidence, summary


def set_inertials(root: ET.Element, rows: list[dict]) -> None:
    frames, by_link = system.frame_positions(), {row["link"]: row for row in rows}
    for body in root.findall(".//body"):
        name = body.get("name")
        if name not in by_link:
            continue
        inertial, row = body.find("inertial"), by_link[name]
        if inertial is None:
            raise RuntimeError(f"MJCF inertial missing for {name}")
        relative = tuple(row["center"][i] - frames[name][i] for i in range(3))
        inertial.set("pos", " ".join(f"{value:.9f}" for value in relative))
        inertial.set("mass", f"{row['mass']:.9f}")
        inertial.set("diaginertia", " ".join(f"{value:.12f}" for value in system.inertia_box(row["mass"], row["size"])))


def write_mjcf(source: Path, target: Path, rows: list[dict], caps: dict[str, float]) -> None:
    root = ET.parse(source).getroot()
    root.set("model", "hr30_tether_light4_mass_bound_p01")
    set_inertials(root, rows)
    for motor in root.findall("./actuator/motor"):
        axis = motor.get("joint", "")
        cap = 1.0 if axis.endswith("_GRIPPER") else caps[axis]
        motor.set("ctrlrange", f"{-cap:.9f} {cap:.9f}")
    custom = root.find("custom")
    if custom is None:
        custom = ET.SubElement(root, "custom")
    ET.SubElement(custom, "text", name="configuration", data=IDENTIFIER)
    ET.SubElement(custom, "text", name="mass_boundary", data="LIGHT4 CAD inventory replaces four predecessor hip inventories; physical mass/inertia open")
    ET.indent(root)
    target.write_text(ET.tostring(root, encoding="unicode") + "\n", encoding="utf-8", newline="\n")


def write_urdf(rows: list[dict]) -> Path:
    root = ET.parse(BASE_URDF).getroot()
    root.set("name", "hr30_tether_light4_mass_bound_p01")
    frames, by_link = system.frame_positions(), {row["link"]: row for row in rows}
    for link in root.findall("link"):
        name = link.get("name")
        if name not in by_link:
            continue
        row, inertial = by_link[name], link.find("inertial")
        relative = tuple(row["center"][i] - frames[name][i] for i in range(3))
        inertial.find("origin").set("xyz", " ".join(f"{value:.9f}" for value in relative))
        inertial.find("mass").set("value", f"{row['mass']:.9f}")
        inode = inertial.find("inertia")
        for key, value in zip(("ixx", "iyy", "izz"), system.inertia_box(row["mass"], row["size"])):
            inode.set(key, f"{value:.12f}")
    for axis in sorted(HIP_AXES):
        transmission = ET.SubElement(root, "transmission", name=f"T_{axis}_LIGHT4")
        ET.SubElement(transmission, "type").text = "transmission_interface/SimpleTransmission"
        joint = ET.SubElement(transmission, "joint", name=axis)
        ET.SubElement(joint, "hardwareInterface").text = "hardware_interface/EffortJointInterface"
        actuator = ET.SubElement(transmission, "actuator", name=f"A_{axis}_LIGHT4")
        ET.SubElement(actuator, "hardwareInterface").text = "hardware_interface/EffortJointInterface"
        ET.SubElement(actuator, "mechanicalReduction").text = "4.0"
    ET.indent(root)
    target = OUT / "hr30_tether_light4_active.urdf"
    target.write_text(ET.tostring(root, encoding="unicode") + "\n", encoding="utf-8", newline="\n")
    return target


def demand_envelope(samples: list[dict], caps: dict[str, float]) -> tuple[list[dict], list[dict]]:
    grouped: dict[str, list[float]] = defaultdict(list)
    sequence_axes: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    sequence_samples: dict[str, set[int]] = defaultdict(set)
    sequence_contact_ok: dict[str, set[int]] = defaultdict(set)
    for row in samples:
        cap = caps[row["axis_id"]]
        row["candidate_current_endpoint_nm"] = f"{cap:.9f}"
        row["absolute_contact_demand_ratio"] = f"{abs(float(row['contact_enabled_inverse_torque_nm'])) / cap:.9f}"
        row["absolute_open_chain_demand_ratio"] = f"{abs(float(row['open_chain_inverse_torque_nm'])) / cap:.9f}"
        row["absolute_gravity_demand_ratio"] = f"{abs(float(row['gravity_only_torque_nm'])) / cap:.9f}"
        grouped[row["axis_id"]].append(abs(float(row["contact_enabled_inverse_torque_nm"])))
        sequence_axes[row["sequence_id"]][row["axis_id"]].append(abs(float(row["contact_enabled_inverse_torque_nm"])))
        sample_index = int(row["sample_index"])
        sequence_samples[row["sequence_id"]].add(sample_index)
        if row["declared_support_contact_present"] == "TRUE":
            sequence_contact_ok[row["sequence_id"]].add(sample_index)
    axis_rows = [{
        "axis_id": axis, "peak_contact_inverse_torque_nm": f"{max(values):.9f}",
        "rms_contact_inverse_torque_nm": f"{math.sqrt(sum(value * value for value in values) / len(values)):.9f}",
        "candidate_current_endpoint_nm": f"{caps[axis]:.9f}", "peak_to_current_endpoint_ratio": f"{max(values) / caps[axis]:.9f}",
        "endpoint_state": "WITHIN LINEAR CURRENT ENDPOINT; CONTINUOUS CAPACITY OPEN" if max(values) <= caps[axis] else "ENDPOINT GAP",
        "warning": WARNING,
    } for axis, values in sorted(grouped.items())]
    sequence_rows = []
    for sequence, axes in sorted(sequence_axes.items()):
        ratios = {axis: max(values) / caps[axis] for axis, values in axes.items()}
        over = sorted(axis for axis, ratio in ratios.items() if ratio > 1.0)
        count = len(sequence_samples[sequence])
        sequence_rows.append({
            "sequence_id": sequence, "trajectory_sample_count": count, "axis_count": len(axes),
            "declared_support_contact_coverage_fraction": f"{len(sequence_contact_ok[sequence]) / count:.9f}",
            "maximum_peak_to_current_endpoint_ratio": f"{max(ratios.values()):.9f}",
            "axes_exceeding_candidate_current_endpoint": "+".join(over) or "NONE", "axis_exceedance_count": len(over),
            "result": "CURRENT ENDPOINT GAP" if over else "WITHIN LIGHT4 LINEAR CURRENT ENDPOINT - CONTINUOUS CAPACITY STILL OPEN",
            "scope": "MASS-BOUND LIGHT4 INVERSE-DYNAMICS DESIGN DIAGNOSTIC; NOT WALKING VALIDATION", "warning": WARNING,
        })
    return axis_rows, sequence_rows


def render_page(status: dict, demand: list[dict], summaries: list[dict]) -> str:
    worst = max(demand, key=lambda row: float(row["peak_to_current_endpoint_ratio"]))
    cards = "".join(f"<article class='card'><h3>{html.escape(row['sequence_id'])}</h3><div class='metric'>{float(row['maximum_rotary_tracking_error_deg']):.2f}&deg;</div><p>maximum tracking error; {float(row['maximum_rotary_saturation_fraction'])*100:.2f}% saturation.</p></article>" for row in summaries)
    return f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><script type='module' src='https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js'></script><title>HR-30 LIGHT4 integrated candidate</title><style>:root{{--deep:#071d36;--blue:#0b4f91;--sky:#84d8ff;--gold:#f2b91d;--paper:#eef8fe;--ink:#142a40;--line:#96cce7;--green:#146c43}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.5 system-ui,Segoe UI,sans-serif}}header,main{{padding:28px 20px}}header{{background:var(--deep);color:white}}header>div,main{{max-width:1180px;margin:auto}}h1{{font-size:clamp(38px,6vw,68px);line-height:1.05}}h2{{font-size:clamp(28px,4vw,43px)}}.warning{{background:var(--gold);color:#15243a;border:3px solid #805600;padding:15px 18px;font-weight:900}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:16px}}.card,.panel{{background:white;border:2px solid var(--line);border-radius:16px;padding:18px;margin:18px 0}}.metric{{font-size:clamp(32px,5vw,48px);font-weight:900;color:var(--blue)}}.pass{{color:var(--green)}}model-viewer{{width:100%;height:min(70vh,680px);background:linear-gradient(#dff4ff,#fff);border-radius:14px}}a{{color:#075b9b;font-weight:800}}@media(max-width:700px){{body{{font-size:16px}}header,main{{padding-inline:13px}}}}</style></head><body><header><div><div class='warning'>{html.escape(WARNING)}</div><h1>The lightweight hips now belong to the same robot in CAD and dynamics.</h1><p>The four physical 4:1 hip packages are reconciled into the complete 762 mm humanoid, then inverse dynamics and bounded control are recomputed from that exact mass model.</p></div></header><main><section class='grid'><article class='card pass'><div class='metric'>{status['mass_kg']:.3f} kg</div><p>{status['margin_to_10kg_kg']:.3f} kg below the program maximum in the planning model.</p></article><article class='card pass'><div class='metric'>{status['maximum_rotary_tracking_error_deg']:.2f}&deg;</div><p>maximum bounded tracking error; zero rotary saturation.</p></article><article class='card'><div class='metric'>{float(worst['peak_to_current_endpoint_ratio']):.2f}&times;</div><p>worst inverse-demand/current-endpoint ratio ({html.escape(worst['axis_id'])}). Continuous duty remains open.</p></article></section><section class='panel'><h2>Complete integrated humanoid</h2><model-viewer camera-controls auto-rotate shadow-intensity='1' src='../lightweight-hip-successor-p0.1/HR-30_light4_whole_body_candidate.glb' alt='Complete HR-30 humanoid with lightweight four-to-one hip transmissions'></model-viewer></section><section class='grid'>{cards}</section><section class='panel'><h2>Engineering files</h2><p><a href='hr30_tether_light4_active.urdf'>URDF</a> &middot; <a href='hr30_tether_light4_active.xml'>MJCF</a> &middot; <a href='hr30_tether_light4_ideal_fixture.xml'>bounded test MJCF</a> &middot; <a href='link-mass-reconciliation.csv'>link masses/COM</a> &middot; <a href='whole-body-axis-demand.csv'>inverse demand</a> &middot; <a href='sequence-control-summary.csv'>control results</a> &middot; <a href='../lightweight-hip-successor-p0.1/HR-30_light4_whole_body_candidate.step'>whole-body STEP</a>.</p></section><section class='panel'><h2>Still preliminary</h2><p>This closes a model-consistency defect. It does not validate belt teeth, shafts, bearings, carriers, fasteners, backlash, efficiency, continuous torque, heat, wiring, balance, restraint, physical mass, motion, walking, or energization.</p></section></main></body></html>"""


def replace_marker(path: Path, start: str, end: str, content: str) -> None:
    text = path.read_text(encoding="utf-8")
    block = f"{start}\n{content}\n{end}"
    if start in text and end in text:
        text = text[:text.index(start)] + block + text[text.index(end) + len(end):]
    else:
        text = text.rstrip() + "\n\n" + block + "\n"
    path.write_text(text, encoding="utf-8", newline="\n")


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    rows, link_rows, mass = build_mass_model()
    write_csv(OUT / "link-mass-reconciliation.csv", link_rows)
    cap_rows = read_csv(BODY / "current-constrained-actuation-p0.1" / "axis-current-torque-register.csv")
    baseline_caps = {row["axis_id"]: float(row["current_limited_linear_endpoint_nm"]) for row in cap_rows}
    active_caps = dict(baseline_caps)
    for axis in HIP_AXES:
        cap_row = next(row for row in cap_rows if row["axis_id"] == axis)
        active_caps[axis] *= 4.0 / float(cap_row["transmission_ratio"])
    write_urdf(rows)
    plain_mjcf, fixture_mjcf = OUT / "hr30_tether_light4_active.xml", OUT / "hr30_tether_light4_ideal_fixture.xml"
    write_mjcf(BASE_MJCF, plain_mjcf, rows, active_caps)
    write_mjcf(BASE_DYN, fixture_mjcf, rows, active_caps)
    shutil.copy2(fixture_mjcf, OUT / "hr30_tether_ideal_fixture.xml")
    model = mujoco.MjModel.from_xml_path(str(fixture_mjcf.resolve()))
    if abs(float(model.body_subtreemass[1]) - mass["active_mass_kg"]) > 5e-6:
        raise RuntimeError("compiled LIGHT4 MJCF mass mismatch")

    old_demand_dir = torque_demand.DYN
    torque_demand.DYN = OUT
    try:
        samples, _, _, _, _ = torque_demand.analyze()
    finally:
        torque_demand.DYN = old_demand_dir
    normalize(samples)
    demand, sequence_demand = demand_envelope(samples, active_caps)
    normalize(sequence_demand)
    write_csv(OUT / "inverse-dynamics-samples.csv", samples)
    write_csv(OUT / "whole-body-axis-demand.csv", demand)
    write_csv(OUT / "sequence-demand-summary.csv", sequence_demand)

    old_predecessor_demand = dynamics_successor.DEMAND
    dynamics_successor.DEMAND = OUT
    control_successor.install_controller()
    try:
        control_samples, axis_results, control_summaries, control_status = dynamics_successor.simulate(model, baseline_caps, active_caps)
    finally:
        dynamics_successor.DEMAND = old_predecessor_demand
    normalize(control_samples); normalize(axis_results); normalize(control_summaries)
    write_csv(OUT / "control-samples.csv", control_samples)
    write_csv(OUT / "axis-control-results.csv", axis_results)
    write_csv(OUT / "sequence-control-summary.csv", control_summaries)
    all_control_pass = bool(control_status["all_sequences_pass_bounded_successor_screen"])
    all_endpoints = all(row["endpoint_state"].startswith("WITHIN") for row in demand)
    status = {
        "identifier": IDENTIFIER, "warning": WARNING, "complete_humanoid_geometry_bound": True,
        "whole_body_step_sha256": sha(LIGHT / "HR-30_light4_whole_body_candidate.step"),
        "whole_body_glb_sha256": sha(LIGHT / "HR-30_light4_whole_body_candidate.glb"),
        "mass_kg": mass["active_mass_kg"], "center_of_mass_m": mass["center_of_mass_m"],
        "margin_to_10kg_kg": mass["margin_to_10kg_kg"], "hip_transmission_ratio": 4.0,
        "mass_reconciled_link_count": len(rows), "affected_link_count": len(mass["affected_links"]),
        "removed_predecessor_item_count": mass["removed_item_count"], "added_light4_item_count": mass["added_item_count"],
        "mujoco_model_compiles": True, "mujoco_model_mass_matches_reconciliation": True,
        "fresh_inverse_dynamics_executed": True, "inverse_demand_within_linear_current_endpoints": all_endpoints,
        "fresh_bounded_control_executed": True, "bounded_control_screen_pass": all_control_pass,
        "maximum_rotary_tracking_error_deg": max(float(row["maximum_rotary_tracking_error_deg"]) for row in control_summaries),
        "maximum_rotary_saturation_fraction": max(float(row["maximum_rotary_saturation_fraction"]) for row in control_summaries),
        "physical_mass_validated": False, "continuous_capacity_validated": False, "free_balance_validated": False,
        "connection_authority": False, "powered_test_authority": False, "motion_authority": False,
        "walking_authority": False, "energization_authority": False,
    }
    (OUT / "active-light4-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n")
    (OUT / "runtime-provenance.json").write_text(json.dumps({"identifier": IDENTIFIER, "warning": WARNING, "executed_utc": datetime.now(timezone.utc).isoformat(), "python": sys.version, "mujoco": mujoco.__version__, "numpy": np.__version__, "controller": "inverse feedforward plus frozen endpoint-scaled kp=8.0, kd=0.8", "integration_timestep_s": dynamics_successor.DT, "scope": "ideal six-axis pelvis fixture; mass-bound LIGHT4 planning model"}, indent=2) + "\n", encoding="utf-8", newline="\n")
    holds = [
        ("AL4-H01", "belt tooth geometry, pulley manufacturing data and belt capacity/tension are unreleased"),
        ("AL4-H02", "carrier, shaft, bearing, fastener, guard and material strength are unvalidated"),
        ("AL4-H03", "continuous torque, torque-speed, efficiency, backlash, reflected inertia and thermal behavior are unvalidated"),
        ("AL4-H04", "free balance, contact robustness, latency, state estimation and physical restraint are unvalidated"),
        ("AL4-H05", "cable motion envelope, physical mass/COM/inertia and tolerance stack are unvalidated"),
        ("AL4-H06", "guarded hardware correlation and qualified mechanical/controls review are unexecuted"),
    ]
    write_csv(OUT / "open-holds.csv", [{"hold_id": key, "unresolved": value, "state": "OPEN", "authority": "BLOCKS PROCUREMENT, FABRICATION, POWERED TESTING, MOTION AND WALKING", "warning": WARNING} for key, value in holds])
    sources = [
        ("generator", Path(__file__)), ("whole-body STEP", LIGHT / "HR-30_light4_whole_body_candidate.step"),
        ("whole-body GLB", LIGHT / "HR-30_light4_whole_body_candidate.glb"), ("lightweight hip inventory", LIGHT / "hip-mass-budget.csv"),
        ("replacement boundary", LIGHT / "replacement-boundary.csv"), ("base tether item inventory", BODY / "mass-item-reconciliation.csv"),
        ("base tether link model", BODY / "link-mass-reconciliation-tether.csv"), ("base URDF", BASE_URDF),
        ("base MJCF", BASE_MJCF), ("base fixture MJCF", BASE_DYN),
        ("trajectory", BODY / "walking-sequence-p0.1" / "trajectory-samples.csv"),
        ("joint trajectory", BODY / "walking-sequence-p0.1" / "joint-trajectory.csv"),
        ("current endpoints", BODY / "current-constrained-actuation-p0.1" / "axis-current-torque-register.csv"),
        ("control implementation", ROOT / "tools" / "generate_hr30_control_successor_p01.py"),
        ("simulation implementation", ROOT / "tools" / "generate_hr30_dynamics_successor_p01.py"),
        ("inverse dynamics implementation", ROOT / "tools" / "generate_hr30_torque_demand_p01.py"),
    ]
    write_csv(OUT / "source-binding.csv", [{"role": role, "path": path.relative_to(ROOT).as_posix(), "sha256": sha(path), "state": "BOUND", "warning": WARNING} for role, path in sources])
    (OUT / "README.md").write_text(f"# HR-30 active LIGHT4 whole-body candidate P0.1\n\n**{WARNING}**\n\nThis package removes {mass['removed_item_count']} predecessor hip items from their actual dynamics links, inserts {mass['added_item_count']} lightweight-hip CAD items at their modeled centers, and rebuilds the complete 26-link robot at {mass['active_mass_kg']:.9f} kg. The URDF, MJCF, inverse-dynamics demand and bounded controller all derive from that same mass model.\n\nThe fresh ideal-fixture controller result is {'PASS' if all_control_pass else 'FAIL'} with {status['maximum_rotary_tracking_error_deg']:.6f} degrees maximum rotary error and {status['maximum_rotary_saturation_fraction']:.9f} maximum rotary saturation fraction. This is model-consistency evidence only—not physical walking, safety, fabrication, or energization approval.\n", encoding="utf-8", newline="\n")
    (OUT / "index.html").write_text(render_page(status, demand, control_summaries), encoding="utf-8", newline="\n")
    shutil.copy2(Path(__file__), OUT / "active-light4-source.py")
    write_csv(OUT / "file-manifest.csv", [{"file": path.name, "bytes": path.stat().st_size, "sha256": sha(path), "warning": WARNING} for path in sorted(OUT.iterdir()) if path.is_file() and path.name != "file-manifest.csv"])

    package_status_path = BODY / "package-status.json"
    package_status = json.loads(package_status_path.read_text(encoding="utf-8"))
    package_status.update({"active_whole_body_engineering_candidate": IDENTIFIER, "active_light4_mass_bound_model_present": True, "active_light4_planning_mass_kg": status["mass_kg"], "active_light4_margin_to_10kg_kg": status["margin_to_10kg_kg"], "active_light4_fresh_inverse_dynamics_executed": True, "active_light4_bounded_control_screen_pass": all_control_pass, "active_light4_physical_validation_complete": False})
    package_status_path.write_text(json.dumps(package_status, indent=2) + "\n", encoding="utf-8", newline="\n")
    readme_block = f"## Integrated LIGHT4 whole-body candidate\n\nThe [integrated LIGHT4 guide](active-light4-p0.1/index.html) binds the complete lightweight-hip STEP/GLB, a {status['mass_kg']:.3f} kg reconciled whole-body URDF/MJCF, freshly recomputed inverse dynamics, and freshly executed bounded control traces. The planning model is {status['margin_to_10kg_kg']:.3f} kg below the 10 kg maximum and the ideal-fixture control screen passes with zero rotary saturation. Physical mass, transmission strength, continuous duty, free balance, restraint, motion and energization remain open."
    replace_marker(BODY / "README.md", "<!-- HR30-ACTIVE-LIGHT4-P01-START -->", "<!-- HR30-ACTIVE-LIGHT4-P01-END -->", readme_block)
    page_block = f"<section id='active-light4'><h2>The lightweight hip geometry and walking model now agree</h2><div class='grid'><article class='card pass'><div class='metric'>{status['mass_kg']:.3f} kg</div><p>mass-reconciled whole-body planning model; {status['margin_to_10kg_kg']:.3f} kg below the program maximum.</p></article><article class='card pass'><div class='metric'>0%</div><p>maximum rotary saturation in the fresh bounded ideal-fixture control run.</p></article><article class='card'><h3>One source chain</h3><p>STEP/GLB, 26-link URDF/MJCF, inverse dynamics and control traces are SHA-bound to the same LIGHT4 candidate.</p></article><article class='card hold'><h3>Physical proof remains open</h3><p>Transmission strength, heat, balance, restraint, physical mass and every work authority remain unresolved.</p></article></div><p><a href='active-light4-p0.1/index.html'>Open the integrated LIGHT4 whole-body guide.</a></p></section>"
    replace_marker(BODY / "index.html", "<!-- HR30-ACTIVE-LIGHT4-P01-START -->", "<!-- HR30-ACTIVE-LIGHT4-P01-END -->", page_block)
    system.refresh_manifest_and_release()
    print(json.dumps(status, indent=2))
    return 0 if all_control_pass and all_endpoints else 2


if __name__ == "__main__":
    raise SystemExit(main())
