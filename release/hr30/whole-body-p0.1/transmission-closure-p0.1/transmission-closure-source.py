"""Close the HR-30 P0.1 transmission packaging placeholders with real candidates.

This successor package maps every one of the 39 pulley/coupler placeholders in
the base body architecture to an existing detailed successor or to new
editable geometry.  It installs four catalogue-defined 16:24 shoulder drives
and nine project-owned direct-output clamp adapters into the complete robot.
It is a coherent design candidate, not a procurement, fabrication, capacity,
motion, safety, or energization release.
"""

from __future__ import annotations

import csv
import hashlib
import html
import json
import math
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

import cadquery as cq


ROOT = Path(__file__).resolve().parents[1]
WHOLE = ROOT / "hr30" / "whole-body-p0.1"
OUT = WHOLE / "transmission-closure-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / "transmission-closure-p0.1"
IDENTIFIER = "HR30-TRANSMISSION-CLOSURE-P0.1"
WARNING = "PRELIMINARY - WHOLE-BODY TRANSMISSION GEOMETRY CANDIDATE ONLY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, POWERED TESTING, MOTION, OR ENERGIZATION"

sys.path.insert(0, str(ROOT / "tools"))
import generate_hr30_body_architecture_p01 as body  # noqa: E402
import generate_hr30_installed_leg_drivetrains_p01 as installed_legs  # noqa: E402
import generate_hr30_leg_drivetrain_p01 as drives  # noqa: E402
import generate_hr30_leg_drivetrain_adapters_p01 as leg_adapters  # noqa: E402
import generate_hr30_system_package_p01 as system  # noqa: E402


@dataclass(frozen=True)
class DirectAdapter:
    adapter_id: str
    axes: tuple[str, ...]
    actuator_interface: str
    shaft_diameter_mm: float
    nominal_span_mm: float
    flange_od_mm: float
    bolt_count: int
    bolt_pcd_mm: float
    clearance_diameter_mm: float
    center_access_diameter_mm: float
    source_record: str


DIRECT_ADAPTERS = (
    DirectAdapter("DA-XC330-S6-L36", ("HEAD_PAN", "HEAD_TILT", "L_WRIST_ROTATION", "R_WRIST_ROTATION"), "XC330 OUTPUT WHEEL PCD12", 6.0, 36.0, 20.0, 4, 12.0, 2.2, 4.5, "ROBOTIS XL/XC-330 drawing dated 2020-05-28"),
    DirectAdapter("DA-HN12-S10-L51", ("L_ELBOW_PITCH", "R_ELBOW_PITCH"), "HN12-N101", 10.0, 51.0, 20.0, 8, 16.0, 2.4, 8.2, "ROBOTIS HN12-N101 drawing dated 2019-05-22"),
    DirectAdapter("DA-HN13-S17-L43", ("WAIST_YAW",), "HN13-N101", 17.0, 43.0, 30.0, 8, 22.0, 2.9, 10.2, "ROBOTIS HN13-N101 drawing dated 2019-05-22"),
    DirectAdapter("DA-HN13-S12-L61", ("L_HIP_YAW", "R_HIP_YAW"), "HN13-N101", 12.0, 61.0, 27.0, 8, 22.0, 2.9, 10.2, "ROBOTIS HN13-N101 drawing dated 2019-05-22"),
)

SHOULDER_AXES = (
    "L_SHOULDER_PITCH", "L_SHOULDER_ROLL", "R_SHOULDER_PITCH", "R_SHOULDER_ROLL"
)
DIRECT_AXES = tuple(axis for spec in DIRECT_ADAPTERS for axis in spec.axes)
SHOULDER_DRIVE = drives.Drive(
    "SD-15S", "JMF-03-SHOULDER-GIMBAL", 16, 24, 37, 10.0,
    "GPA16GT5090-A-P10", "GPA24GT5090-A-P10", "GBN185EV5GT-090",
    "XM430 all shoulder axes", "HN12-N101 all shoulder axes", SHOULDER_AXES,
)
SHOULDER_CENTER_MM = drives.solve_center(SHOULDER_DRIVE)


@dataclass(frozen=True)
class InstalledPart:
    axis_id: str
    part_id: str
    kind: str
    shape: cq.Shape
    visual_shape: cq.Shape
    color: tuple[float, float, float, float]
    note: str


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise RuntimeError(f"refusing empty CSV: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def parse_vector(text: str) -> cq.Vector:
    return cq.Vector(*[float(value.strip()) for value in text.strip("() ").split(",")])


def axis_vector(record: dict) -> cq.Vector:
    return cq.Vector(float(record["direction_x"]), float(record["direction_y"]), float(record["direction_z"])).normalized()


def direct_spec_for_axis(axis_id: str) -> DirectAdapter:
    matches = [spec for spec in DIRECT_ADAPTERS if axis_id in spec.axes]
    if len(matches) != 1:
        raise RuntimeError(f"direct adapter allocation drift for {axis_id}")
    return matches[0]


def direct_adapter_local(spec: DirectAdapter, span_mm: float | None = None) -> cq.Shape:
    """A flange-ended blind-bore split-clamp torque tube, local axis +Y."""
    length = spec.nominal_span_mm if span_mm is None else span_mm
    flange_t = 4.0
    clamp_engagement = min(18.0, max(13.0, length * 0.38))
    tube_od = max(spec.shaft_diameter_mm + 8.0, 14.0)
    body_shape = body.cylinder_between((0, length / 2.0, 0), (0, 1, 0), length, tube_od)
    flange = body.cylinder_between((0, flange_t / 2.0, 0), (0, 1, 0), flange_t, spec.flange_od_mm)
    shape = body_shape.fuse(flange)

    # Blind output-shaft socket: the uncut motor end leaves a positive torque
    # path from the flange into the tube.  The diametral allowance is a design
    # placeholder and carries no fit or tolerance release.
    bore = body.cylinder_between(
        (0, length - clamp_engagement / 2.0 + 0.25, 0), (0, 1, 0),
        clamp_engagement + 0.5, spec.shaft_diameter_mm + 0.20,
    )
    shape = shape.cut(bore)
    access = body.cylinder_between((0, flange_t / 2.0, 0), (0, 1, 0), flange_t + 1.0, spec.center_access_diameter_mm)
    shape = shape.cut(access)
    for index in range(spec.bolt_count):
        angle = math.radians(index * 360.0 / spec.bolt_count)
        x = spec.bolt_pcd_mm / 2.0 * math.cos(angle)
        z = spec.bolt_pcd_mm / 2.0 * math.sin(angle)
        shape = shape.cut(body.cylinder_between((x, flange_t / 2.0, z), (0, 1, 0), flange_t + 1.0, spec.clearance_diameter_mm))

    # Explicit clamp slit and two-lug pinch-bolt access.  Exact bolt, thread,
    # torque and fatigue disposition remain selection required.
    lug_y = length - clamp_engagement / 2.0
    lug_z = tube_od / 2.0 + 2.5
    lug = cq.Workplane("XY").box(tube_od + 5.0, clamp_engagement * 0.72, 5.0).translate((0, lug_y, lug_z)).val()
    shape = shape.fuse(lug)
    slit = cq.Workplane("XY").box(1.2, clamp_engagement + 1.0, tube_od / 2.0 + 6.0).translate((0, lug_y, tube_od / 4.0 + 3.0)).val()
    shape = shape.cut(slit)
    pinch = body.cylinder_between((0, lug_y, lug_z), (1, 0, 0), tube_od + 8.0, 3.4)
    return shape.cut(pinch).clean()


def shoulder_offset(axis_id: str) -> cq.Vector:
    if "PITCH" in axis_id:
        return cq.Vector(0, 1, 0)
    if "ROLL" in axis_id:
        return cq.Vector(0, 0, -1)
    raise RuntimeError(axis_id)


def shoulder_horn_key(axis_id: str) -> str:
    return "HN12"


def shoulder_adapter_spec(axis_id: str):
    target = "MA-HN12-P10"
    return next(item for item in leg_adapters.MOTOR_ADAPTERS if item.adapter_id == target)


def perpendicular(direction: cq.Vector) -> cq.Vector:
    trial = cq.Vector(0, 0, 1) if abs(direction.z) < 0.8 else cq.Vector(1, 0, 0)
    return (trial - direction.multiply(direction.dot(trial))).normalized()


def build_successor() -> tuple[list[body.Component], list[InstalledPart], list[dict], list[dict]]:
    retained, leg_parts, _leg_installation, _leg_collisions = installed_legs.build_installed()
    _base, axes, _bindings, vendor_transforms = body.build()
    axis_map = {record["axis_id"]: record for record in axes}
    transform_map = {record["axis_id"]: record for record in vendor_transforms}

    remove_names = {f"JMOD_{axis}_ACTUATOR_OUTPUT_COUPLER" for axis in DIRECT_AXES}
    for axis in SHOULDER_AXES:
        remove_names.update({
            f"JMOD_{axis}_OUTPUT_PULLEY", f"JMOD_{axis}_MOTOR_PULLEY",
            f"JMOD_{axis}_BELT_PATH_RESERVATION", f"JMOD_{axis}_ACTUATOR_VENDOR_CANDIDATE",
        })
    retained = [component for component in retained if component.name not in remove_names]
    if len(remove_names) != 25:
        raise RuntimeError("expected 9 direct plus 16 shoulder placeholder components")

    parts: list[InstalledPart] = list(leg_parts)
    direct_rows: list[dict] = []
    shoulder_rows: list[dict] = []
    vendor_shapes = {key: cq.importers.importStep(str(value["path"])).val() for key, value in body.VENDOR_ACTUATOR_SOURCES.items()}

    for axis_id in DIRECT_AXES:
        axis = axis_map[axis_id]
        center = cq.Vector(float(axis["x_mm"]), float(axis["y_mm"]), float(axis["z_mm"]))
        motor = parse_vector(transform_map[axis_id]["project_output_origin_mm"])
        travel = center - motor
        length = travel.Length
        spec = direct_spec_for_axis(axis_id)
        if abs(length - spec.nominal_span_mm) > 1e-6:
            raise RuntimeError(f"direct adapter span drift {axis_id}: {length} vs {spec.nominal_span_mm}")
        local = direct_adapter_local(spec, length)
        world = installed_legs.map_local(local, motor, travel.normalized(), perpendicular(travel.normalized()))
        parts.append(InstalledPart(axis_id, f"{axis_id}_{spec.adapter_id}", "flanged blind-bore split-clamp direct adapter", world, world, (0.95, 0.62, 0.08, 1.0), f"{spec.actuator_interface} to supported {spec.shaft_diameter_mm:.0f} mm shaft; nominal geometry only"))
        direct_rows.append({
            "axis_id": axis_id, "adapter_id": spec.adapter_id, "actuator_interface": spec.actuator_interface,
            "motor_output_origin_mm": f"({motor.x:.3f}, {motor.y:.3f}, {motor.z:.3f})",
            "supported_joint_axis_mm": f"({center.x:.3f}, {center.y:.3f}, {center.z:.3f})",
            "installed_span_mm": f"{length:.3f}", "shaft_socket_diameter_mm": f"{spec.shaft_diameter_mm + 0.20:.3f}",
            "flange_bolt_pattern": f"{spec.bolt_count} x DIA {spec.clearance_diameter_mm:.1f} on PCD {spec.bolt_pcd_mm:.1f}",
            "interface_source": spec.source_record,
            "geometry_state": "EDITABLE STEP + BLIND SOCKET + SPLIT + PINCH-BOLT ACCESS COMPLETE",
            "release_boundary": "MATERIAL, FIT, TOLERANCE, FASTENER, CLAMP TORQUE, RUNOUT, CAPACITY, DFM, FAI AND PHYSICAL PROOF OPEN",
            "warning": WARNING,
        })

    for axis_id in SHOULDER_AXES:
        axis = axis_map[axis_id]
        center = cq.Vector(float(axis["x_mm"]), float(axis["y_mm"]), float(axis["z_mm"]))
        axis_dir = axis_vector(axis)
        drive_dir = shoulder_offset(axis_id)
        motor_center = center + drive_dir.multiply(SHOULDER_CENTER_MM)
        outward_sign = 1.0 if axis_id.startswith("L_") else -1.0
        outward_axis = axis_dir.multiply(outward_sign)

        local_output = drives.pulley_envelope(24, 10.0, 0.0)
        local_motor = drives.pulley_envelope(16, 10.0, SHOULDER_CENTER_MM)
        local_belt = drives.belt_envelope(SHOULDER_DRIVE, SHOULDER_CENTER_MM)
        output = installed_legs.map_local(local_output, center, axis_dir, drive_dir)
        motor_pulley = installed_legs.map_local(local_motor, center, axis_dir, drive_dir)
        belt = installed_legs.map_local(local_belt, center, axis_dir, drive_dir)

        adapter_spec = shoulder_adapter_spec(axis_id)
        horn_spec = leg_adapters.HORN_INTERFACES[shoulder_horn_key(axis_id)]
        stack_to_pulley_center = leg_adapters.FLANGE_THICKNESS_MM + leg_adapters.PULLEY_ENGAGEMENT_MM / 2.0
        horn_contact = motor_center - outward_axis.multiply(stack_to_pulley_center)
        motor_adapter = installed_legs.map_local(leg_adapters.motor_adapter_shape(adapter_spec), horn_contact, outward_axis, drive_dir)
        horn = installed_legs.map_local(leg_adapters.horn_shape_local(adapter_spec.horn_key), horn_contact, outward_axis, drive_dir)
        source_id = body.vendor_source_for_axis(axis_id)
        actuator_output = horn_contact - outward_axis.multiply(horn_spec.contact_y_mm + 0.4)
        actuator, _basis = body.vendor_actuator_to_axis(vendor_shapes[source_id], (actuator_output.x, actuator_output.y, actuator_output.z), (axis_dir.x, axis_dir.y, axis_dir.z))
        family = body.JOINT_MODULE_FAMILIES["JMF-03-SHOULDER-GIMBAL"]
        actuator_visual = body.oriented_box((actuator_output.x, actuator_output.y, actuator_output.z), (axis_dir.x, axis_dir.y, axis_dir.z), family["body_w"], family["body_h"], family["body_d"])

        axis_parts = (
            InstalledPart(axis_id, f"{axis_id}_OUTPUT_PULLEY", "catalogue 24-tooth 5GT P-bore pulley envelope", output, output, (0.96, 0.55, 0.08, 1.0), "GPA24GT5090-A-P10; vendor tooth B-Rep not claimed"),
            InstalledPart(axis_id, f"{axis_id}_MOTOR_PULLEY", "catalogue 16-tooth 5GT P-bore pulley envelope", motor_pulley, motor_pulley, (0.98, 0.72, 0.12, 1.0), "GPA16GT5090-A-P10; vendor tooth B-Rep not claimed"),
            InstalledPart(axis_id, f"{axis_id}_BELT", "catalogue 37-tooth EV5GT belt routing envelope", belt, belt, (0.10, 0.13, 0.17, 1.0), "GBN185EV5GT-090; 185 mm pitch length"),
            InstalledPart(axis_id, f"{axis_id}_HORN", "exact manufacturer horn", horn, horn, (0.45, 0.50, 0.57, 1.0), f"{horn_spec.horn_id} exact STEP"),
            InstalledPart(axis_id, f"{axis_id}_MOTOR_ADAPTER", "project horn-to-pulley adapter", motor_adapter, motor_adapter, (0.95, 0.62, 0.08, 1.0), adapter_spec.adapter_id),
            InstalledPart(axis_id, f"{axis_id}_ACTUATOR", "shifted manufacturer actuator", actuator, actuator_visual, (0.10, 0.25, 0.44, 1.0), source_id),
        )
        parts.extend(axis_parts)
        shoulder_rows.append({
            "axis_id": axis_id, "drive_id": "SD-15S", "actuator": "XM430-W350-R",
            "actuator_source": source_id, "horn": horn_spec.horn_id, "motor_adapter": adapter_spec.adapter_id,
            "motor_pulley": "GPA16GT5090-A-P10", "output_pulley": "GPA24GT5090-A-P10", "belt": "GBN185EV5GT-090",
            "teeth_ratio": "16:24 / 1.5:1", "pitch_mm": "5.0", "belt_width_mm": "9.0", "belt_teeth": "37",
            "solved_pitch_center_distance_mm": f"{SHOULDER_CENTER_MM:.6f}", "pitch_length_check_mm": f"{drives.belt_length(SHOULDER_CENTER_MM, 16, 24):.6f}",
            "geometry_state": "CATALOGUE PRODUCT ENVELOPES + EXACT HORN + EDITABLE ADAPTER INSTALLED",
            "release_boundary": "WRITTEN QUOTE, RECEIPT, FIT, RETENTION, TENSION, LOAD/LIFE, GUARD, CABLE SWEEP AND PHYSICAL PROOF OPEN",
            "warning": WARNING,
        })
    return retained, parts, direct_rows, shoulder_rows


def disposition_rows() -> list[dict]:
    source = list(csv.DictReader((WHOLE / "joint-hardware-manufacturing-p0.1" / "joint-hardware-part-register.csv").open(encoding="utf-8", newline="")))
    targets = [row for row in source if "PULLEY" in row["part_type"] or "COUPLER" in row["part_type"]]
    if len(targets) != 39:
        raise RuntimeError(f"expected 39 predecessor placeholders, got {len(targets)}")
    leg_alloc = {row["axis_id"]: row for row in csv.DictReader((WHOLE / "leg-drivetrain-adapters-p0.1" / "axis-adapter-allocation.csv").open(encoding="utf-8", newline=""))}
    rows = []
    for row in targets:
        axis_id = row["axis_id"]
        part_type = row["part_type"]
        if "GRIPPER" in axis_id:
            successor = "detailed-grippers-p0.1 PINION + RACK_POSITIVE + RACK_NEGATIVE"
            state = "SUPERSEDED BY EDITABLE MODULE-0.5 INVOLUTE PINION/RACK HAND MECHANISM"
        elif axis_id in leg_alloc and "PULLEY" in part_type:
            successor = leg_alloc[axis_id]["motor_pulley" if "MOTOR" in part_type else "output_pulley"]
            state = "SUPERSEDED BY INSTALLED MISUMI CATALOGUE PRODUCT CANDIDATE"
        elif axis_id in SHOULDER_AXES and "PULLEY" in part_type:
            successor = "GPA16/GPA24GT5090-A-P10 / SD-15S installed shoulder drive"
            state = "SUPERSEDED BY INSTALLED MISUMI CATALOGUE PRODUCT CANDIDATE"
        elif axis_id in DIRECT_AXES and "COUPLER" in part_type:
            successor = direct_spec_for_axis(axis_id).adapter_id
            state = "SUPERSEDED BY EDITABLE FLANGED BLIND-BORE SPLIT-CLAMP ADAPTER"
        else:
            raise RuntimeError(f"unmapped predecessor {row['part_id']}")
        rows.append({
            "predecessor_part_id": row["part_id"], "axis_id": axis_id, "predecessor_part_type": part_type,
            "predecessor_state": row["disposition"], "successor": successor, "successor_state": state,
            "placeholder_geometry_remaining_authoritative": "NO", "successor_selected_for_procurement": "NO",
            "remaining_validation": "PRODUCT RECEIPT OR MATERIAL/FIT/TOLERANCE/CAPACITY/DFM/FAI/PHYSICAL PROOF AS APPLICABLE",
            "warning": WARNING,
        })
    return rows


def drawing_svg(spec: DirectAdapter) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="720" viewBox="0 0 1000 720"><style>.t{{font:800 34px system-ui;fill:#fff}}.h{{font:800 22px system-ui;fill:#123b68}}.b{{font:16px system-ui;fill:#152b43}}.s{{stroke:#075b9b;stroke-width:3;fill:none}}.p{{fill:#f2b91d;stroke:#8a5b00;stroke-width:3}}</style><rect width="1000" height="720" fill="#eff9fe"/><rect width="1000" height="104" fill="#081e38"/><text x="34" y="55" class="t">{html.escape(spec.adapter_id)}</text><text x="34" y="86" class="t" style="font-size:17px">PRELIMINARY - NOT RELEASED FOR MACHINING</text><text x="44" y="152" class="h">Controlled nominal geometry</text><text x="44" y="190" class="b">Interface: {html.escape(spec.actuator_interface)}</text><text x="44" y="224" class="b">Span: {spec.nominal_span_mm:.1f} mm; shaft socket: {spec.shaft_diameter_mm + 0.20:.2f} mm</text><text x="44" y="258" class="b">Flange: OD {spec.flange_od_mm:.1f}; {spec.bolt_count} × DIA {spec.clearance_diameter_mm:.1f} on PCD {spec.bolt_pcd_mm:.1f}</text><text x="44" y="292" class="b">Blind socket, split and transverse pinch-bolt access are modeled.</text><rect x="520" y="180" width="330" height="120" rx="24" class="p"/><circle cx="850" cy="240" r="92" class="p"/><circle cx="850" cy="240" r="25" fill="#eff9fe" stroke="#075b9b" stroke-width="3"/><line x1="520" y1="350" x2="850" y2="350" class="s"/><text x="600" y="386" class="h">local +Y torque tube</text><text x="44" y="640" class="b">Material, fits, tolerances, thread, fasteners, clamp torque, runout, capacity, DFM, FAI and physical proof remain open.</text></svg>'''


def render_index() -> str:
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 transmission closure P0.1</title><script type="module" src="../vendor/model-viewer.min.js"></script><style>:root{{--deep:#081e38;--navy:#123b68;--pale:#eff9fe;--gold:#f2b91d;--line:#acd8ed;--ink:#152b43}}*{{box-sizing:border-box}}html,body{{max-width:100%;overflow-x:clip}}body{{margin:0;background:var(--pale);color:var(--ink);font:17px/1.55 system-ui,Segoe UI,sans-serif}}header,footer{{padding:32px max(20px,calc((100vw - 1200px)/2));background:var(--deep);color:white}}h1{{font-size:clamp(36px,6vw,66px);line-height:1.04}}h2{{font-size:clamp(28px,4vw,42px);color:var(--navy)}}h3{{font-size:22px;color:var(--navy)}}.warning{{padding:16px;background:var(--gold);color:#17243a;border:3px solid #8a5b00;font-weight:900}}main{{max-width:1200px;margin:auto;padding:28px 20px 80px}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px}}.card,.viewer,.panel{{background:white;border:2px solid var(--line);border-radius:18px;padding:18px;overflow:hidden}}.metric{{font-size:36px;font-weight:900;color:var(--navy)}}model-viewer{{display:block;width:100%;height:clamp(560px,72vh,780px);background:radial-gradient(circle,#fff,var(--pale))}}.table-wrap{{overflow:auto;border:2px solid var(--line);border-radius:14px}}table{{border-collapse:collapse;min-width:900px;width:100%}}th,td{{padding:14px;text-align:left;vertical-align:top;border-bottom:1px solid var(--line);font-size:14px}}th{{background:var(--navy);color:white}}a{{color:#075b9b;font-weight:800}}@media(max-width:560px){{body{{font-size:16px}}.grid{{grid-template-columns:1fr}}model-viewer{{height:520px}}}}</style></head><body><header><div class="warning">{html.escape(WARNING)}</div><h1>Every transmission placeholder now has a named successor.</h1><p>The complete robot carries product-specific leg and shoulder drives, detailed rack-and-pinion hands, and nine editable direct-output clamp adapters. The geometry is tangible; engineering release evidence remains deliberately open.</p></header><main><section><h2>Orbit the successor assembly</h2><div class="viewer"><model-viewer src="HR-30_transmissions_installed_candidate.glb" alt="Complete 762 millimetre HR-30 humanoid with installed leg and shoulder belt drives and direct-output adapters" camera-controls camera-orbit="28deg 76deg 100%" field-of-view="27deg" shadow-intensity="0.85" exposure="1.05"></model-viewer><p><a href="HR-30_transmissions_installed_candidate.step">Whole-body STEP</a> · <a href="HR-30_transmission_hardware_only_candidate.step">transmission-only STEP</a> · <a href="transmission-disposition-register.csv">all 39 dispositions</a>.</p></div></section><section><h2>What changed</h2><div class="grid"><article class="card"><div class="metric">39 / 39</div><p>predecessor pulley/coupler placeholders mapped to concrete successors.</p></article><article class="card"><div class="metric">4</div><p>shoulder axes use 16:24 5GT catalogue candidates with 185 mm belts.</p></article><article class="card"><div class="metric">9</div><p>direct joints have four editable blind-bore split-clamp adapter families.</p></article><article class="card"><div class="metric">0</div><p>procurement, fabrication, powered-test, motion, or energization approvals.</p></article></div></section><section><h2>The shoulders are no longer ratio-only sketches</h2><div class="panel"><p>Each shoulder axis uses a <strong>GPA16GT5090-A-P10</strong> motor pulley, a <strong>GPA24GT5090-A-P10</strong> supported-output pulley, and one <strong>GBN185EV5GT-090</strong> 37-tooth belt candidate. The 16:24 pair gives 1.5:1 reduction and a solved 42.0177 mm nominal pitch center. All four motors use the exact XM430/HN12 packaging source.</p></div></section><section><h2>Direct adapters</h2><div class="table-wrap"><table><thead><tr><th>Family</th><th>Axes</th><th>Motor interface</th><th>Supported output</th></tr></thead><tbody>{''.join(f'<tr><td>{s.adapter_id}</td><td>{", ".join(s.axes)}</td><td>{s.actuator_interface}</td><td>{s.shaft_diameter_mm:.0f} mm blind socket; split/pinch access</td></tr>' for s in DIRECT_ADAPTERS)}</tbody></table></div></section><section><h2>Still required before making parts</h2><div class="panel"><p>Written product quotes and received-part registration; shaft and bearing fits; material and heat treatment; tolerance, runout, clamp and fastener calculations; belt tension and life; motor/horn retention; interference and motion sweeps; guards; DFM; first-article inspection; load, thermal, endurance and fault testing; and qualified mechanical review. This package removes placeholder geometry, not those obligations.</p></div></section></main><footer>Project Button · HR-30 transmission closure P0.1 · preliminary only</footer></body></html>'''


def integrate_root() -> None:
    status_path = WHOLE / "package-status.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    status.update({
        "transmission_closure_package_present": True,
        "transmission_predecessor_placeholder_count": 39,
        "transmission_predecessor_placeholder_successor_mapping_complete": True,
        "shoulder_catalogue_drive_axis_count": 4,
        "direct_output_adapter_axis_count": 9,
        "direct_output_adapter_family_count": 4,
        "wrist_vendor_geometry_reconciled_to_xc330": True,
        "transmission_successor_whole_body_step_present": True,
        "transmission_successor_whole_body_glb_present": True,
        "transmission_material_fit_capacity_validated": False,
        "procurement_authority": False, "fabrication_authority": False, "assembly_authority": False,
        "powered_test_authority": False, "motion_authority": False, "energization_authority": False,
    })
    status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")

    readme_path = WHOLE / "README.md"
    text = readme_path.read_text(encoding="utf-8")
    start, end = "<!-- HR30-TRANSMISSION-CLOSURE-P01-README-START -->", "<!-- HR30-TRANSMISSION-CLOSURE-P01-README-END -->"
    if start in text and end in text:
        text = text.split(start, 1)[0] + text.split(end, 1)[1]
    marker = "<!-- HR30-ASSEMBLY-GUIDE-P01-START -->"
    block = f'''{start}\n## Whole-body transmission closure\n\nThe [transmission closure guide](transmission-closure-p0.1/index.html) maps all 39 smooth-pulley or generic-coupler predecessor placeholders to concrete successors. Twenty leg pulleys were already superseded by installed MISUMI candidates, two gripper couplers by the detailed rack-and-pinion hands, eight shoulder pulley positions now use a 16:24 5GT / 185 mm belt candidate, and nine direct axes now use four editable flanged blind-bore split-clamp adapter families. The successor whole-body STEP/GLB also corrects the wrist vendor geometry to XC330. Material, fits, retention, capacity, DFM, FAI and physical proof remain open.\n{end}\n'''
    if marker in text:
        text = text.replace(marker, block + marker)
    else:
        text = text.rstrip() + "\n\n" + block
    readme_path.write_text(text, encoding="utf-8", newline="\n")

    page_path = WHOLE / "index.html"
    page = page_path.read_text(encoding="utf-8")
    start, end = "<!-- HR30-TRANSMISSION-CLOSURE-P01-START -->", "<!-- HR30-TRANSMISSION-CLOSURE-P01-END -->"
    if start in page and end in page:
        page = page.split(start, 1)[0] + page.split(end, 1)[1]
    section = f'''{start}<section id="transmission-closure"><h2>The transmission placeholders now have physical successors</h2><div class="grid"><article class="card pass"><div class="metric">39 / 39</div><p>predecessor pulley and coupler placeholders are dispositioned.</p></article><article class="card pass"><div class="metric">4 + 9</div><p>shoulder belt drives and direct-output adapter axes are installed.</p></article><article class="card pass"><h3>Whole robot</h3><p>A successor STEP and interactive GLB carry the transmission hardware on the complete humanoid.</p></article><article class="card hold"><h3>Not released</h3><p>Products, fits, retention, capacity, DFM, FAI and physical tests remain open.</p></article></div><p><a href="transmission-closure-p0.1/index.html">Open the transmission guide</a> · <a href="transmission-closure-p0.1/transmission-disposition-register.csv">39-item disposition register</a>.</p></section>{end}'''
    marker = "<!-- HR30-ASSEMBLY-GUIDE-P01-START -->"
    if marker in page:
        page = page.replace(marker, section + marker)
    elif "</main>" in page:
        page = page.replace("</main>", section + "</main>")
    else:
        raise RuntimeError("whole-body page insertion boundary missing")
    page_path.write_text(page, encoding="utf-8", newline="\n")

    holds_path = WHOLE / "open-holds.csv"
    with holds_path.open(encoding="utf-8", newline="") as handle:
        holds = list(csv.DictReader(handle))
    hold = next(row for row in holds if row["hold_id"] == "HR30-P01-H01")
    hold["unresolved_item"] = (
        "All 39 base-architecture pulley/coupler placeholders now have named successor artifacts: 20 installed leg pulley candidates, "
        "2 detailed rack-and-pinion hands, 8 installed shoulder pulley candidates and 9 editable direct-output clamp adapters. "
        "This eliminates authoritative placeholder geometry but does not release material, shaft/bearing fits, shoulders/grooves, "
        "clamp/fastener retention, exact received products, DFM, FAI, load/life, endurance or physical proof. The 39 catalogue bearing "
        "envelopes and 156 carrier screws remain candidate hardware with application, torque, locking and capacity open."
    )
    write_csv(holds_path, holds)


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    (OUT / "parts").mkdir()
    (OUT / "drawings").mkdir()

    retained, parts, direct_rows, shoulder_rows = build_successor()
    disposition = disposition_rows()
    write_csv(OUT / "transmission-disposition-register.csv", disposition)
    write_csv(OUT / "direct-adapter-axis-register.csv", direct_rows)
    write_csv(OUT / "shoulder-drive-register.csv", shoulder_rows)
    write_csv(OUT / "direct-adapter-part-register.csv", [{
        "adapter_id": spec.adapter_id, "whole_robot_quantity": len(spec.axes), "axes": ";".join(spec.axes),
        "actuator_interface": spec.actuator_interface, "nominal_span_mm": f"{spec.nominal_span_mm:.3f}",
        "shaft_socket_diameter_mm": f"{spec.shaft_diameter_mm + 0.20:.3f}", "flange_od_mm": f"{spec.flange_od_mm:.3f}",
        "flange_pattern": f"{spec.bolt_count} x DIA {spec.clearance_diameter_mm:.1f} on PCD {spec.bolt_pcd_mm:.1f}",
        "manufacturing_route": "TURN + MILL BOLT FIELD + SAW/MILL SPLIT + DRILL/THREAD PINCH LUG CANDIDATE",
        "material": "SELECTION REQUIRED", "nominal_geometry_complete": "YES", "fabrication_released": "NO", "warning": WARNING,
    } for spec in DIRECT_ADAPTERS])
    write_csv(OUT / "source-register.csv", [
        {"source_id": "TC-S01", "record": "ROBOTIS HN12-N101 official STEP/PDF", "revision_date": "drawing 2019-05-22; local SHA-bound sources", "locator": "cad/vendor/robotis/hn12-n101-r103/", "use": "eight-hole PCD16 horn interface", "warning": WARNING},
        {"source_id": "TC-S02", "record": "ROBOTIS HN13-N101 official STEP/PDF", "revision_date": "drawing 2019-05-22; local SHA-bound sources", "locator": "cad/vendor/robotis/hn13-n101-r143/", "use": "eight-hole PCD22 horn interface", "warning": WARNING},
        {"source_id": "TC-S03", "record": "ROBOTIS XL/XC-330 official reference drawing", "revision_date": "drawing 2020-05-28; retrieved 2026-08-10", "locator": "cad/vendor/robotis/xc330/XL-XC-330-official-drawing.pdf", "use": "four output holes on PCD12; drawing marked FOR REFERENCE ONLY", "warning": WARNING},
        {"source_id": "TC-S04", "record": "MISUMI High Torque Timing Pulleys 5GT Type", "revision_date": "official catalogue PDF accessed 2026-08-16; page carries no controlled revision field", "locator": "https://us.c.misumi-ec.com/book/usa_2019_msm_fa/pdf/1410.pdf", "use": "GPA16GT5090-A-P10 and GPA24GT5090-A-P10; 16/24 teeth; 5 mm pitch; 9 mm belt; OD 24.32/37.06; P10 bore + tap permitted", "warning": WARNING},
        {"source_id": "TC-S05", "record": "MISUMI EV5GT belt catalogue", "revision_date": "official catalogue PDF accessed 2026-08-15; page carries no controlled revision field", "locator": "https://us.misumi-ec.com/pdf/fa/2019/2019_US_1432.pdf", "use": "GBN185EV5GT-090; 37 teeth; 185 mm pitch length; 9 mm width", "warning": WARNING},
        {"source_id": "TC-S06", "record": "transmission closure generator", "revision_date": "generated 2026-08-15", "locator": "tools/generate_hr30_transmission_closure_p01.py", "use": "editable direct adapters, installed shoulder drives and 39-item disposition", "warning": WARNING},
    ])

    for spec in DIRECT_ADAPTERS:
        shape = direct_adapter_local(spec)
        step = OUT / "parts" / f"{spec.adapter_id}.step"
        cq.exporters.export(shape, str(step))
        body.canonicalize_step(step)
        (OUT / "drawings" / f"{spec.adapter_id}.svg").write_text(drawing_svg(spec), encoding="utf-8", newline="\n")

    hardware = cq.Compound.makeCompound([part.shape for part in parts if part.axis_id in set(DIRECT_AXES) | set(SHOULDER_AXES)])
    whole = cq.Compound.makeCompound([component.shape for component in retained if component.physical] + [part.shape for part in parts])
    cq.exporters.export(hardware, str(OUT / "HR-30_transmission_hardware_only_candidate.step"))
    cq.exporters.export(whole, str(OUT / "HR-30_transmissions_installed_candidate.step"))
    body.canonicalize_step(OUT / "HR-30_transmission_hardware_only_candidate.step")
    body.canonicalize_step(OUT / "HR-30_transmissions_installed_candidate.step")

    hardware_assy = cq.Assembly(name="HR30_TRANSMISSION_HARDWARE_P01_NOT_RELEASED")
    whole_assy = cq.Assembly(name="HR30_WHOLE_BODY_TRANSMISSIONS_P01_NOT_RELEASED")
    for component in retained:
        whole_assy.add(component.visual_shape if component.visual_shape is not None else component.shape, name=component.name, color=cq.Color(*component.color))
    for part in parts:
        whole_assy.add(part.visual_shape, name=part.part_id, color=cq.Color(*part.color))
        if part.axis_id in set(DIRECT_AXES) | set(SHOULDER_AXES):
            hardware_assy.add(part.visual_shape, name=part.part_id, color=cq.Color(*part.color))
    hardware_assy.save(str(OUT / "HR-30_transmission_hardware_only_candidate.glb"), tolerance=0.15, angularTolerance=0.14)
    whole_assy.save(str(OUT / "HR-30_transmissions_installed_candidate.glb"), tolerance=0.19, angularTolerance=0.17)

    status = {
        "identifier": IDENTIFIER, "predecessor_placeholder_count": 39, "predecessor_successor_mapping_count": len(disposition),
        "predecessor_successor_mapping_complete": len(disposition) == 39, "shoulder_drive_axis_count": len(shoulder_rows),
        "direct_adapter_axis_count": len(direct_rows), "direct_adapter_family_count": len(DIRECT_ADAPTERS),
        "whole_body_step_present": True, "whole_body_glb_present": True, "editable_source_present": True,
        "wrist_vendor_geometry_reconciled_to_xc330": True, "catalogue_tooth_brep_claimed": False,
        "material_fit_fasteners_capacity_validated": False, "physical_validation_complete": False,
        "procurement_authority": False, "fabrication_authority": False, "assembly_authority": False,
        "powered_test_authority": False, "motion_authority": False, "energization_authority": False, "warning": WARNING,
    }
    (OUT / "transmission-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    (OUT / "README.md").write_text(f"# HR-30 transmission closure P0.1\n\n**{WARNING}**\n\nAll 39 smooth-pulley or generic-coupler predecessor placeholders have concrete successor mappings. The package installs four catalogue-defined 16:24 shoulder drives and nine editable direct-output clamp adapters into the complete 762 mm humanoid while preserving the installed reduced-leg drivetrains. It grants no work authority.\n", encoding="utf-8", newline="\n")
    (OUT / "index.html").write_text(render_index(), encoding="utf-8", newline="\n")
    shutil.copy2(Path(__file__), OUT / "transmission-closure-source.py")
    files = sorted(path for path in OUT.rglob("*") if path.is_file() and path.name != "file-manifest.csv")
    write_csv(OUT / "file-manifest.csv", [{"path": path.relative_to(OUT).as_posix(), "bytes": path.stat().st_size, "sha256": sha(path), "warning": WARNING} for path in files])
    integrate_root()
    system.refresh_manifest_and_release()
    print(json.dumps(status, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
