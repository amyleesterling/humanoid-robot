"""Generate the HR-V0 gripper source-control and integration-input package.

The package uses the exact official ROBOTIS OpenMANIPULATOR-X URDF and mesh
files frozen in cad/vendor/robotis/open-manipulator-9187eca.  Those files are
collision/kinematic references, not Project Button fabrication geometry and
not received-part measurements.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import shutil
import struct
import xml.etree.ElementTree as ET
from pathlib import Path

import cadquery as cq
from OCP.StlAPI import StlAPI_Reader
from OCP.TopoDS import TopoDS_Shape


ROOT = Path(__file__).resolve().parents[1]
VENDOR = ROOT / "cad" / "vendor" / "robotis" / "open-manipulator-9187eca"
OUT = ROOT / "cad" / "hr-v0" / "generated" / "gripper-integration-p0.2"
REVISION = "HR-V0-GRIP-P0.2"
SOURCE_COMMIT = "9187eca0920458be04d2399906388f55242f81f1"
WARNING = "PRELIMINARY - REFERENCE GEOMETRY ONLY - NOT RELEASED FOR FABRICATION, MOTION, OR ENERGIZATION"
EXPECTED_HASHES = {
    "gripper_left_palm.stl": "FB4DFABE68712BBBA34DEB9F8469F9187009C07579DCCD5401B82D08DE425267",
    "gripper_right_palm.stl": "A5BFC10A067C806A19062E2FCB58989623A09EDC0E9BBC4FD735A56D83F99752",
    "link5.stl": "75E7596295DD5F5CBC68D81B2C875058F28721F98D7402D2D431CCF2334B57A6",
    "open_manipulator_x.urdf": "784078C2A5BB16ACCD2CA4CBCF0D340403D6D343F047B433B503AEAE85EF17D3",
    "LICENSE": "C71D239DF91726FC519C6EB72D318EC65820627232B2F796219E87DCF35D0AB4",
}
RAW_BASE = f"https://raw.githubusercontent.com/ROBOTIS-GIT/open_manipulator/{SOURCE_COMMIT}"
SOURCE_URLS = {
    "gripper_left_palm.stl": f"{RAW_BASE}/open_manipulator_description/meshes/open_manipulator_x/gripper_left_palm.stl",
    "gripper_right_palm.stl": f"{RAW_BASE}/open_manipulator_description/meshes/open_manipulator_x/gripper_right_palm.stl",
    "link5.stl": f"{RAW_BASE}/open_manipulator_description/meshes/open_manipulator_x/link5.stl",
    "open_manipulator_x.urdf": f"{RAW_BASE}/open_manipulator_description/urdf/open_manipulator_x/open_manipulator_x.urdf",
    "LICENSE": f"{RAW_BASE}/LICENSE",
}
CONFIGURATIONS = (
    ("urdf_lower", -11.0),
    ("urdf_neutral", 0.0),
    ("urdf_upper", 20.0),
)
MASS_POINTS_G = (0.0, 25.0, 50.0, 57.242, 75.0, 100.0, 115.225, 125.0, 150.0)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def read_binary_stl_vertices(path: Path) -> list[tuple[float, float, float]]:
    data = path.read_bytes()
    if len(data) < 84:
        raise RuntimeError(f"STL too short: {path}")
    triangle_count = struct.unpack_from("<I", data, 80)[0]
    if len(data) != 84 + triangle_count * 50:
        raise RuntimeError(f"Expected binary STL layout: {path}")
    vertices: list[tuple[float, float, float]] = []
    for index in range(triangle_count):
        values = struct.unpack_from("<12fH", data, 84 + index * 50)
        vertices.extend((values[3:6], values[6:9], values[9:12]))
    return vertices


def convex_hull(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
    unique = sorted(set(points))
    if len(unique) <= 1:
        return unique

    def cross(origin: tuple[float, float], a: tuple[float, float], b: tuple[float, float]) -> float:
        return (a[0] - origin[0]) * (b[1] - origin[1]) - (a[1] - origin[1]) * (b[0] - origin[0])

    lower: list[tuple[float, float]] = []
    for point in unique:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], point) <= 0:
            lower.pop()
        lower.append(point)
    upper: list[tuple[float, float]] = []
    for point in reversed(unique):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], point) <= 0:
            upper.pop()
        upper.append(point)
    return lower[:-1] + upper[:-1]


def read_shape(path: Path) -> cq.Shape:
    shape = TopoDS_Shape()
    if not StlAPI_Reader().Read(shape, str(path)):
        raise RuntimeError(f"Unable to read STL: {path}")
    return cq.Shape(shape)


def parse_urdf() -> dict[str, object]:
    root = ET.parse(VENDOR / "open_manipulator_x.urdf").getroot()
    joints: dict[str, dict[str, object]] = {}
    for name in ("gripper_left_joint", "gripper_right_joint"):
        joint = root.find(f"./joint[@name='{name}']")
        if joint is None:
            raise RuntimeError(f"Missing {name}")
        origin = joint.find("origin")
        axis = joint.find("axis")
        limit = joint.find("limit")
        if origin is None or axis is None or limit is None:
            raise RuntimeError(f"Incomplete {name}")
        joints[name] = {
            "parent": joint.find("parent").attrib["link"],
            "child": joint.find("child").attrib["link"],
            "origin_mm": [1000.0 * float(value) for value in origin.attrib["xyz"].split()],
            "axis": [float(value) for value in axis.attrib["xyz"].split()],
            "lower_mm": 1000.0 * float(limit.attrib["lower"]),
            "upper_mm": 1000.0 * float(limit.attrib["upper"]),
        }
    return joints


def placed(shape: cq.Shape, joint: dict[str, object], q_mm: float) -> cq.Shape:
    origin = joint["origin_mm"]
    axis = joint["axis"]
    translation = tuple(float(origin[i]) + float(axis[i]) * q_mm for i in range(3))
    return shape.translate(translation)


def bounds(shape: cq.Shape) -> list[float]:
    box = shape.BoundingBox()
    return [box.xmin, box.ymin, box.zmin, box.xmax, box.ymax, box.zmax]


def points_string(points: list[tuple[float, float]], x_offset: float, y_offset: float, scale: float) -> str:
    return " ".join(f"{x_offset + x * scale:.2f},{y_offset - y * scale:.2f}" for x, y in points)


def svg_preview(hulls: dict[str, list[tuple[float, float]]], samples: list[dict[str, object]]) -> str:
    scale = 2.15
    panel_x = (55.0, 560.0, 1065.0)
    panel_y = 460.0
    panels: list[str] = []
    for index, ((label, q_mm), sample) in enumerate(zip(CONFIGURATIONS, samples)):
        x0 = panel_x[index]
        left = [(x + 81.7, y + 21.0 + q_mm) for x, y in hulls["left"]]
        right = [(x + 81.7, y - 21.0 - q_mm) for x, y in hulls["right"]]
        panels.append(
            f'''<g>
  <rect x="{x0}" y="210" width="460" height="390" rx="16" class="panel"/>
  <text x="{x0 + 22}" y="248" class="head">{label.replace('_', ' ')}</text>
  <text x="{x0 + 22}" y="278">joint displacement q = {q_mm:.1f} mm</text>
  <polygon points="{points_string(hulls['link5'], x0 + 85, panel_y, scale)}" class="carrier"/>
  <polygon points="{points_string(left, x0 + 85, panel_y, scale)}" class="palm"/>
  <polygon points="{points_string(right, x0 + 85, panel_y, scale)}" class="palm"/>
  <text x="{x0 + 22}" y="640">Closest palm-mesh distance: {float(sample['closest_mesh_distance_mm']):.3f} mm</text>
</g>'''
        )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="950" viewBox="0 0 1600 950">
<style>
  text {{ font-family: Arial, sans-serif; fill: #102a43; font-size: 18px; }}
  .title {{ font-size: 34px; font-weight: 700; }}
  .head {{ font-size: 23px; font-weight: 700; }}
  .warn {{ font-size: 20px; font-weight: 700; fill: #8a4b00; }}
  .panel {{ fill: #f8fbff; stroke: #123b68; stroke-width: 3; }}
  .carrier {{ fill: #9dd8f5; stroke: #123b68; stroke-width: 2.5; }}
  .palm {{ fill: #f4bd3e; stroke: #123b68; stroke-width: 2.5; }}
</style>
<rect width="1600" height="950" fill="#eef7fd"/>
<text x="55" y="62" class="title">HR-V0 official gripper reference geometry</text>
<text x="55" y="102" class="warn">{WARNING}</text>
<text x="55" y="142">ROBOTIS source commit {SOURCE_COMMIT[:12]} - top-view convex projections - dimensions in mm</text>
<text x="55" y="178">Blue: official link5 carrier mesh. Gold: official palm meshes positioned by the official URDF.</text>
{''.join(panels)}
<rect x="55" y="690" width="1460" height="190" rx="16" fill="#fff8e7" stroke="#8a4b00" stroke-width="3"/>
<text x="82" y="730" class="head">What this establishes - and what it does not</text>
<text x="82" y="770">The exact public meshes and URDF are revision-frozen and reproducible. The views show geometry-derived projection envelopes.</text>
<text x="82" y="808">Mesh distance is not certified jaw opening. The e-Manual 20-75 mm stroke still requires received-assembly reconciliation.</text>
<text x="82" y="846">No crank/rod/rail manufacturing CAD, H104 registration, guard, mass, force, fastener, cable, or physical test is released.</text>
<text x="55" y="925">Revision {REVISION}. No fabrication, motion, energization, or functional-safety approval.</text>
</svg>'''


def html_viewer(hulls: dict[str, list[tuple[float, float]]], samples: list[dict[str, object]]) -> str:
    scale = 4.0
    x_offset = 135.0
    y_offset = 320.0
    carrier = points_string(hulls["link5"], x_offset, y_offset, scale)
    left = points_string([(x + 81.7, y + 21.0) for x, y in hulls["left"]], x_offset, y_offset, scale)
    right = points_string([(x + 81.7, y - 21.0) for x, y in hulls["right"]], x_offset, y_offset, scale)
    sample_rows = "".join(
        f"<tr><td>{row['configuration']}</td><td>{row['joint_displacement_q_mm']}</td><td>{row['closest_mesh_distance_mm']}</td></tr>"
        for row in samples
    )
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>HR-V0 gripper reference geometry</title>
<style>
:root {{ --sky:#dff3ff; --blue:#123b68; --gold:#f4bd3e; --ink:#102a43; --warn:#8a4b00; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; font:16px/1.5 Arial,sans-serif; color:var(--ink); background:#f8fbff; }}
header,main {{ width:calc(100% - 32px); max-width:1120px; margin:auto; }}
header {{ padding:28px 0 18px; }}
h1 {{ margin:0 0 8px; font-size:clamp(30px,5vw,48px); line-height:1.1; }}
h2 {{ font-size:24px; }}
.warning {{ padding:14px 18px; border:3px solid var(--warn); border-radius:12px; background:#fff8e7; color:#613600; font-weight:700; font-size:18px; }}
.card {{ margin:20px 0; padding:22px; border:2px solid var(--blue); border-radius:16px; background:white; }}
label {{ display:block; font-size:18px; font-weight:700; }}
input[type=range] {{ width:100%; min-height:42px; }}
.readout {{ font-size:22px; font-weight:700; color:var(--blue); }}
svg {{ width:100%; height:auto; min-height:420px; border:1px solid #8aa8bf; background:var(--sky); }}
.carrier {{ fill:#9dd8f5; stroke:var(--blue); stroke-width:2.5; }}
.palm {{ fill:var(--gold); stroke:var(--blue); stroke-width:2.5; }}
table {{ width:100%; border-collapse:collapse; font-size:16px; }}
th,td {{ padding:10px; border:1px solid #7890a4; text-align:left; }}
th {{ background:var(--sky); }}
.meta {{ font-size:14px; }}
code {{ font-size:15px; overflow-wrap:anywhere; }}
@media (max-width:650px) {{ .card {{ padding:16px; }} svg {{ min-height:300px; }} th,td {{ padding:8px; }} }}
</style>
</head>
<body>
<header>
  <h1>HR-V0 gripper reference geometry</h1>
  <p class="warning">{WARNING}</p>
  <p>Exact ROBOTIS public mesh projections positioned by the official URDF. Blue is the fixed link5 carrier mesh; gold is the two moving palm meshes.</p>
</header>
<main>
  <section class="card">
    <label for="q">URDF joint displacement: <span class="readout" id="qValue">0.0 mm</span></label>
    <input id="q" type="range" min="-11" max="20" step="0.1" value="0">
    <svg viewBox="0 0 900 640" role="img" aria-label="Interactive top view of the official gripper reference meshes">
      <polygon points="{carrier}" class="carrier"/>
      <g id="leftPalm"><polygon points="{left}" class="palm"/></g>
      <g id="rightPalm"><polygon points="{right}" class="palm"/></g>
    </svg>
    <p>The slider applies the URDF prismatic axes only. It does not model compliance, rubber-pad compression, linkage error, backlash, guard clearance, cable motion, or manufacturing tolerance.</p>
  </section>
  <section class="card">
    <h2>Frozen sample checks</h2>
    <table><thead><tr><th>Configuration</th><th>q (mm)</th><th>Closest mesh distance (mm)</th></tr></thead><tbody>{sample_rows}</tbody></table>
    <p>Closest triangle-mesh distance is not certified jaw opening and is not the e-Manual stroke value. The received mechanism must be measured and reconciled before a usable opening is released.</p>
  </section>
  <section class="card">
    <h2>Source and release boundary</h2>
    <p>Official ROBOTIS OpenMANIPULATOR source commit: <code>{SOURCE_COMMIT}</code>. The repository files are collision/visualization references under the included upstream license; they are not Project Button manufacturing drawings.</p>
    <p>Still required: complete mechanism manufacturing definition or received metrology, H104-to-carrier registration, guard and receiver CAD, received mass/COM, exact fasteners and cable path, force/current tests, power-off containment, wear tests, and qualified review.</p>
    <p class="meta">Revision {REVISION}. No fabrication, motion, energization, or functional-safety approval.</p>
  </section>
</main>
<script>
const slider=document.getElementById('q');
const value=document.getElementById('qValue');
const left=document.getElementById('leftPalm');
const right=document.getElementById('rightPalm');
const pxPerMm={scale};
function update() {{ const q=Number(slider.value); value.textContent=q.toFixed(1)+' mm'; left.setAttribute('transform','translate(0,'+(-q*pxPerMm)+')'); right.setAttribute('transform','translate(0,'+(q*pxPerMm)+')'); }}
slider.addEventListener('input',update); update();
</script>
</body>
</html>'''


def main() -> int:
    for name, expected in EXPECTED_HASHES.items():
        path = VENDOR / name
        if not path.is_file() or sha256(path) != expected:
            raise RuntimeError(f"Vendor source integrity failure: {name}")
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    joints = parse_urdf()
    left_joint = joints["gripper_left_joint"]
    right_joint = joints["gripper_right_joint"]
    if left_joint["lower_mm"] != -11.0 or left_joint["upper_mm"] != 20.0:
        raise RuntimeError("Unexpected left gripper URDF limits")
    if right_joint["lower_mm"] != -11.0 or right_joint["upper_mm"] != 20.0:
        raise RuntimeError("Unexpected right gripper URDF limits")

    left_shape = read_shape(VENDOR / "gripper_left_palm.stl")
    right_shape = read_shape(VENDOR / "gripper_right_palm.stl")
    link5_shape = read_shape(VENDOR / "link5.stl")
    samples: list[dict[str, object]] = []
    for label, q_mm in CONFIGURATIONS:
        left = placed(left_shape, left_joint, q_mm)
        right = placed(right_shape, right_joint, q_mm)
        samples.append(
            {
                "configuration": label,
                "joint_displacement_q_mm": f"{q_mm:.3f}",
                "left_origin_x_mm": f"{float(left_joint['origin_mm'][0]):.3f}",
                "left_origin_y_at_q_mm": f"{float(left_joint['origin_mm'][1]) + q_mm:.3f}",
                "right_origin_x_mm": f"{float(right_joint['origin_mm'][0]):.3f}",
                "right_origin_y_at_q_mm": f"{float(right_joint['origin_mm'][1]) - q_mm:.3f}",
                "closest_mesh_distance_mm": f"{left.distance(right):.6f}",
                "left_bounds_mm": ";".join(f"{value:.6f}" for value in bounds(left)),
                "right_bounds_mm": ";".join(f"{value:.6f}" for value in bounds(right)),
                "interpretation": "OFFICIAL MESH/URDF REFERENCE ONLY - NOT CERTIFIED JAW OPENING",
            }
        )
    write_csv(OUT / "gripper-kinematic-samples.csv", samples)

    source_rows = [
        {
            "file": name,
            "upstream_commit": SOURCE_COMMIT,
            "retrieved_utc": "2026-08-07",
            "sha256": EXPECTED_HASHES[name],
            "source_url": SOURCE_URLS[name],
            "project_use": "OFFICIAL REFERENCE ONLY - NO FABRICATION OR MASS CREDIT",
        }
        for name in EXPECTED_HASHES
    ]
    write_csv(OUT / "gripper-source-integrity.csv", source_rows)

    mass_rows: list[dict[str, object]] = []
    for mass_g in MASS_POINTS_G:
        shoulder_delta = mass_g / 1000.0 * 9.80665 * 0.3316
        elbow_delta = mass_g / 1000.0 * 9.80665 * 0.12905
        mass_rows.append(
            {
                "parameterized_unresolved_gripper_mass_g": f"{mass_g:.3f}",
                "incremental_shoulder_gravity_Nm_at_331_6_mm": f"{shoulder_delta:.6f}",
                "incremental_elbow_gravity_Nm_at_129_05_mm": f"{elbow_delta:.6f}",
                "p0_7_total_if_only_this_unknown_remained_g": f"{692.758 + mass_g:.3f}",
                "p0_7_750_g_screen": "WITHIN" if 692.758 + mass_g <= 750.0 else "OVER",
                "r70_nonselected_total_if_only_this_unknown_remained_g": f"{634.775 + mass_g:.3f}",
                "r70_nonselected_750_g_screen": "WITHIN" if 634.775 + mass_g <= 750.0 else "OVER",
                "boundary": "PARAMETRIC ONLY; OTHER UNRESOLVED MOVING ITEMS ALSO CONSUME HEADROOM",
            }
        )
    write_csv(OUT / "gripper-mass-load-sensitivity.csv", mass_rows)

    holds = [
        {
            "hold_id": "GRH-001",
            "scope": "complete mechanism manufacturing definition",
            "current_evidence": "official link5 and palm STL collision/visual meshes",
            "missing_evidence": "native part CAD/drawings or received dimensional metrology for crank rods rails brackets pads bushes and interfaces",
            "effect": "no gripper fabrication or dimensional release",
            "status": "OPEN",
        },
        {
            "hold_id": "GRH-002",
            "scope": "H104-to-URDF carrier registration",
            "current_evidence": "separate H104 STEP and official link5-parent URDF frame",
            "missing_evidence": "controlled transform proven against received kit datums and fastener access",
            "effect": "no exact merged arm/gripper assembly or collision credit",
            "status": "OPEN",
        },
        {
            "hold_id": "GRH-003",
            "scope": "usable opening calibration",
            "current_evidence": "e-Manual 20-75 mm stroke plus URDF limits and mesh-distance samples",
            "missing_evidence": "received mechanism calibration across the project 20-70 mm object range with pads installed",
            "effect": "mesh distance is not released as jaw opening",
            "status": "OPEN",
        },
        {
            "hold_id": "GRH-004",
            "scope": "mass COM and inertia closure",
            "current_evidence": "82 g actuator catalog mass and parameterized load sensitivity",
            "missing_evidence": "weighed received components and assembled gripper plus measured local COM and cable share",
            "effect": "MASS-002 remains blocked",
            "status": "OPEN",
        },
        {
            "hold_id": "GRH-005",
            "scope": "guard and receiver",
            "current_evidence": "reference collision envelopes only",
            "missing_evidence": "released fixed guard receiver catch attachment access-probe clearance and retained-load CAD plus tests",
            "effect": "no guarded motion",
            "status": "OPEN",
        },
        {
            "hold_id": "GRH-006",
            "scope": "force current and power-off behavior",
            "current_evidence": "test method only",
            "missing_evidence": "calibrated force/current foam-compression retention drop and power-off containment records",
            "effect": "no grip-force setting or handoff capability claim",
            "status": "OPEN",
        },
        {
            "hold_id": "GRH-007",
            "scope": "fasteners cable and wear",
            "current_evidence": "kit content allocation",
            "missing_evidence": "exact fastener stack torque locking cable route strain relief flex-cycle and retention evidence",
            "effect": "no assembly or service release",
            "status": "OPEN",
        },
    ]
    write_csv(OUT / "gripper-integration-holds.csv", holds)

    hulls = {
        "left": convex_hull([(x, y) for x, y, _ in read_binary_stl_vertices(VENDOR / "gripper_left_palm.stl")]),
        "right": convex_hull([(x, y) for x, y, _ in read_binary_stl_vertices(VENDOR / "gripper_right_palm.stl")]),
        "link5": convex_hull([(x, y) for x, y, _ in read_binary_stl_vertices(VENDOR / "link5.stl")]),
    }
    (OUT / "HR-V0_gripper-reference-envelope.svg").write_text(svg_preview(hulls, samples), encoding="utf-8", newline="\n")
    (OUT / "HR-V0_gripper-reference-viewer.html").write_text(html_viewer(hulls, samples), encoding="utf-8", newline="\n")

    summary = {
        "revision": REVISION,
        "warning": WARNING,
        "upstream_commit": SOURCE_COMMIT,
        "source_file_count": len(EXPECTED_HASHES),
        "configuration_count": len(samples),
        "urdf_joints": joints,
        "link5_bounds_mm": bounds(link5_shape),
        "urdf_endpoint_closest_mesh_distance_mm": {
            row["configuration"]: float(row["closest_mesh_distance_mm"]) for row in samples
        },
        "published_stroke_mm": [20.0, 75.0],
        "project_object_range_mm": [20.0, 70.0],
        "controlled_p0_7_known_subtotal_g": 692.758,
        "controlled_p0_7_total_unresolved_headroom_g": 57.242,
        "r70_nonselected_known_subtotal_g": 634.775,
        "r70_nonselected_total_unresolved_headroom_g": 115.225,
        "mass_credit": "NONE - URDF inertial values and mesh volumes are not used as physical gripper mass",
        "integration_state": "SOURCE GEOMETRY CONTROLLED; COMPLETE BUILD DEFINITION AND PHYSICAL EVIDENCE OPEN",
    }
    (OUT / "gripper-geometry-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    (OUT / "README.md").write_text(
        f"# HR-V0 gripper integration input {REVISION}\n\n"
        f"{WARNING}\n\n"
        "This generated package freezes official ROBOTIS collision/visual meshes and URDF kinematics at an exact upstream commit, provides a responsive interactive top-view reference, and records mass/load sensitivity and fail-closed integration holds. It is not manufacturing CAD and takes no mass, fit, guard, force, motion, or safety credit.\n\n"
        "Regenerate with `C:\\Users\\amyle\\Documents\\New project\\.venvs\\hr-v0-cad\\Scripts\\python.exe tools/generate_hr_v0_gripper_integration.py`, then run `tools/check_hr_v0_gripper_integration.py` with the same interpreter.\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"Generated {REVISION}: exact official source frozen; seven integration holds remain open")
    print("PRELIMINARY - NOT APPROVED FOR FABRICATION, MOTION, OR ENERGIZATION")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
