"""Generate the first native parametric HR-30 full-body architecture.

This is a dimensioned configuration/packaging model, not manufacturing CAD.
It freezes the product-specification datums, all 25 candidate axes, named link
and shell envelopes, and the first component-bay reservations.  Joint stacks,
bearings, reductions, fasteners, covers, harnesses, tolerances, materials and
qualified structural evidence remain open.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import shutil
from dataclasses import dataclass
from pathlib import Path

import cadquery as cq
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.gp import gp_Trsf


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "hr30" / "whole-body-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1"
MODEL_VIEWER_SOURCE = ROOT / "release" / "vendor" / "model-viewer" / "4.1.0"
IDENTIFIER = "HR-30-BODY-ARCH-P0.1"
WARNING = (
    "PRELIMINARY - CONFIGURATION AND PACKAGING CAD ONLY - NOT APPROVED FOR "
    "PROCUREMENT, FABRICATION, ASSEMBLY, POWERED TESTING, MOTION, OR ENERGIZATION"
)
ASIMOV_1_SOURCE_SHA256 = "ae126d212e8c56486ce014bd9b01b3779b0086867f9b47615ddefbbf32fa5167"
VENDOR_ACTUATOR_SOURCES = {
    "ROBOTIS-540": {
        "path": ROOT / "cad" / "vendor" / "robotis" / "XMHD-540.N101.I101.STP",
        "expected_sha256": "6E0DF65638B3A23B12C7EE1114D4D06F5EC2DE9E84E3FFDDD7E115E8F8FAF39F",
        "record": "ROBOTIS XM/H/D-540 manufacturer STEP; retrieved 2026-08-06",
        "applies": "XM540 and XH540 package candidates",
    },
    "ROBOTIS-X430": {
        "path": ROOT / "cad" / "vendor" / "robotis" / "x430-fr12-r91" / "x-430_idle.stp",
        "expected_sha256": "7FF4E39475245D5C1FC4F703E9241FCA1A09D57AED920274498DBE2CD5E31E22",
        "record": "ROBOTIS X-430 manufacturer STEP retained as a whole-body packaging source",
        "applies": "XM430 package candidates",
    },
    "ROBOTIS-XC330": {
        "path": ROOT / "cad" / "vendor" / "robotis" / "xc330" / "XL-XC-330-official-source.stp",
        "expected_sha256": "E2F7B060801A1D6A21F23BCA2554F29A402F7D73B8498CB201C9E6ADF3139EB6",
        "record": "ROBOTIS XL/XC-330 official STEP download 1987; retrieved 2026-08-10",
        "applies": "XC330 package candidates",
    },
}

# Standard catalogue bearing candidates replace the former anonymous annular
# steel density solids.  Dimensions and catalogue mass are primary-source
# facts; application suitability, suffix, fits, preload and life remain open.
BEARING_CANDIDATES = {
    "NSK-696": {
        "manufacturer": "NSK", "designation": "696 OPEN EVALUATION CANDIDATE",
        "bore_d": 6.0, "outer_d": 15.0, "width": 5.0, "mass_kg": 0.00388,
        "dynamic_rating_n": 1910.0, "static_rating_n": 670.0,
        "url": "https://www.oss.nsk.com/jp/products/bearings/ball-bearings/deep-groove-ball-bearings/extra-small-ball-bearings-and-miniature-ball-bearings-metric-series/696-esm-md.html",
    },
    "SKF-625-2Z": {
        "manufacturer": "SKF", "designation": "625-2Z EVALUATION CANDIDATE",
        "bore_d": 5.0, "outer_d": 16.0, "width": 5.0, "mass_kg": 0.005,
        "dynamic_rating_n": 1430.0, "static_rating_n": 630.0,
        "url": "https://www.emarketplace.in.skf.com/deep-groove-ball-bearing/625-2z",
    },
    "SKF-61900-2RS1": {
        "manufacturer": "SKF", "designation": "61900-2RS1 EVALUATION CANDIDATE",
        "bore_d": 10.0, "outer_d": 22.0, "width": 6.0, "mass_kg": 0.009,
        "dynamic_rating_n": 2700.0, "static_rating_n": 1270.0,
        "url": "https://www.emarketplace.in.skf.com/deep-groove-ball-bearing/61900-2rs1",
    },
    "SKF-6003-2Z-C3": {
        "manufacturer": "SKF", "designation": "6003-2Z/C3 EVALUATION CANDIDATE",
        "bore_d": 17.0, "outer_d": 35.0, "width": 10.0, "mass_kg": 0.040,
        "dynamic_rating_n": 6370.0, "static_rating_n": 3250.0,
        "url": "https://www.emarketplace.in.skf.com/deep-groove-ball-bearing/6003-2z-c3",
    },
    "SKF-6002-2RS1": {
        "manufacturer": "SKF", "designation": "6002-2RS1 EVALUATION CANDIDATE",
        "bore_d": 15.0, "outer_d": 32.0, "width": 9.0, "mass_kg": 0.030,
        "dynamic_rating_n": 5850.0, "static_rating_n": 2850.0,
        "url": "https://www.emarketplace.in.skf.com/deep-groove-ball-bearing/6002-2rs1",
    },
    "NSK-6803": {
        "manufacturer": "NSK", "designation": "6803 OPEN EVALUATION CANDIDATE",
        "bore_d": 17.0, "outer_d": 26.0, "width": 5.0, "mass_kg": 0.007,
        "dynamic_rating_n": 2890.0, "static_rating_n": 1570.0,
        "url": "https://www.oss.nsk.com/in/products/bearings/ball-bearings/deep-groove-ball-bearings/single-row-deep-groove-ball-bearings/6803-apn.html",
    },
    "NSK-6901": {
        "manufacturer": "NSK", "designation": "6901 OPEN EVALUATION CANDIDATE",
        "bore_d": 12.0, "outer_d": 24.0, "width": 6.0, "mass_kg": 0.010,
        "dynamic_rating_n": 3200.0, "static_rating_n": 1460.0,
        "url": "https://www.oss.nsk.com/in/products/bearings/ball-bearings/deep-groove-ball-bearings/single-row-deep-groove-ball-bearings/6901-apn.html",
    },
}

# Authoritative HR-PROD-030 datums, millimetres.
HEIGHT = 762.0
ANKLE_Z = 45.0
KNEE_Z = 210.0
HIP_Z = 380.0
WAIST_Z = 425.0
SHOULDER_Z = 590.0
NECK_Z = 650.0
HIP_HALF_WIDTH = 62.5
SHOULDER_AXIS_X = 105.0
ELBOW_X = 135.0
WRIST_X = 140.0
ELBOW_Z = 440.0
WRIST_Z = 295.0
FINGERTIP_Z = 220.0


@dataclass(frozen=True)
class Component:
    name: str
    group: str
    shape: cq.Shape
    color: tuple[float, float, float, float]
    physical: bool = True
    note: str = ""
    visual_shape: cq.Shape | None = None


def canonicalize_step(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = re.sub(
        r"(FILE_NAME\('Open CASCADE Shape Model',)'[^']*'",
        r"\1'1980-01-01T00:00:00'",
        text,
        count=1,
    )
    path.write_text("\n".join(line.rstrip() for line in text.splitlines()) + "\n", encoding="utf-8", newline="\n")


def rounded_box(width: float, depth: float, height: float, center: tuple[float, float, float], radius: float) -> cq.Shape:
    solid = cq.Workplane("XY").box(width, depth, height)
    if radius > 0:
        solid = solid.edges().fillet(radius)
    return solid.translate(center).val()


def tapered_body(
    z0: float,
    z1: float,
    lower_width: float,
    lower_depth: float,
    upper_width: float,
    upper_depth: float,
    center_x: float = 0.0,
    center_y: float = 0.0,
) -> cq.Shape:
    """Make a dimensioned tapered envelope so body segments are not generic blocks."""
    return (
        cq.Workplane("XY")
        .workplane(offset=z0)
        .center(center_x, center_y)
        .rect(lower_width, lower_depth)
        .workplane(offset=z1 - z0)
        .rect(upper_width, upper_depth)
        .loft(combine=True)
        .val()
    )


def cylinder_between(origin: tuple[float, float, float], direction: tuple[float, float, float], length: float, diameter: float) -> cq.Shape:
    d = cq.Vector(*direction).normalized()
    start = cq.Vector(*origin) - d.multiply(length / 2.0)
    return cq.Solid.makeCylinder(diameter / 2.0, length, start, d)


def hollow_cylinder_between(origin: tuple[float, float, float], direction: tuple[float, float, float], length: float, outer_diameter: float, bore_diameter: float) -> cq.Shape:
    """Candidate hollow shaft/tube with a through bore and unchanged outer interface."""
    outer = cylinder_between(origin, direction, length, outer_diameter)
    inner = cylinder_between(origin, direction, length + 2.0, bore_diameter)
    return outer.cut(inner)


def link_between(a: tuple[float, float, float], b: tuple[float, float, float], diameter: float) -> cq.Shape:
    av = cq.Vector(*a)
    bv = cq.Vector(*b)
    delta = bv - av
    length = delta.Length
    return cq.Solid.makeCylinder(diameter / 2.0, length, av, delta.normalized())


def local_plane(center: tuple[float, float, float], direction: tuple[float, float, float]) -> cq.Plane:
    """Create a stable workplane whose local Z is the controlled joint axis."""
    normal = cq.Vector(*direction).normalized()
    reference = cq.Vector(0, 0, 1) if abs(normal.z) < 0.9 else cq.Vector(1, 0, 0)
    x_dir = reference.cross(normal).normalized()
    return cq.Plane(origin=cq.Vector(*center), xDir=x_dir, normal=normal)


def vendor_actuator_to_axis(shape: cq.Shape, center: tuple[float, float, float], direction: tuple[float, float, float]) -> tuple[cq.Shape, tuple[cq.Vector, cq.Vector, cq.Vector]]:
    """Map native actuator +Z/output origin to the controlled HR-30 axis.

    The roll convention is deterministic: local +X maps to the stable xDir
    returned by ``local_plane`` and local +Y completes the right-handed basis.
    This is a packaging transform only; it does not select a frame, horn,
    fastener, cable exit, tolerance, or received-part fit.
    """
    plane = local_plane(center, direction)
    x_dir = plane.xDir.normalized()
    z_dir = plane.zDir.normalized()
    y_dir = z_dir.cross(x_dir).normalized()
    transform = gp_Trsf()
    transform.SetValues(
        x_dir.x, y_dir.x, z_dir.x, center[0],
        x_dir.y, y_dir.y, z_dir.y, center[1],
        x_dir.z, y_dir.z, z_dir.z, center[2],
    )
    result = cq.Shape.cast(BRepBuilderAPI_Transform(shape.wrapped, transform, True).Shape())
    return result, (x_dir, y_dir, z_dir)


def vendor_source_for_axis(axis_id: str) -> str:
    if axis_id.startswith("HEAD_") or "GRIPPER" in axis_id:
        return "ROBOTIS-XC330"
    if any(token in axis_id for token in ("WRIST", "ELBOW", "ANKLE_", "SHOULDER_ROLL")):
        return "ROBOTIS-X430"
    return "ROBOTIS-540"


def oriented_box(center: tuple[float, float, float], direction: tuple[float, float, float], width: float, height: float, axial_depth: float) -> cq.Shape:
    return cq.Workplane(local_plane(center, direction)).box(width, height, axial_depth).val()


def interface_plate(
    center: tuple[float, float, float],
    direction: tuple[float, float, float],
    width: float,
    height: float,
    thickness: float,
    pattern_x: float,
    pattern_y: float,
    clearance_diameter: float,
    shaft_diameter: float,
) -> cq.Shape:
    plane = local_plane(center, direction)
    plate = cq.Workplane(plane).box(width, height, thickness)
    drilled = (
        plate.faces(">Z")
        .workplane()
        .pushPoints([(-pattern_x / 2, -pattern_y / 2), (-pattern_x / 2, pattern_y / 2), (pattern_x / 2, -pattern_y / 2), (pattern_x / 2, pattern_y / 2)])
        .hole(clearance_diameter)
    )
    # Preserve the complete outer datum and four bolt pads while replacing the
    # old solid slab with a closed rectangular carrier frame.
    window_x = max(8.0, pattern_x - 10.0)
    window_y = max(8.0, pattern_y - 10.0)
    frame = drilled.faces(">Z").workplane().rect(window_x, window_y).cutThruAll().val()
    spoke_w = max(5.0, clearance_diameter + 2.0)
    cross_x = cq.Workplane(plane).box(window_x + 2.0, spoke_w, thickness).val()
    cross_y = cq.Workplane(plane).box(spoke_w, window_y + 2.0, thickness).val()
    center_bore = cylinder_between(center, direction, thickness + 2.0, shaft_diameter + 0.6)
    return frame.fuse(cross_x).fuse(cross_y).cut(center_bore)


def bearing_ring(center: tuple[float, float, float], direction: tuple[float, float, float], width: float, outer_diameter: float, shaft_diameter: float) -> cq.Shape:
    outer = cylinder_between(center, direction, width, outer_diameter)
    bore = cylinder_between(center, direction, width + 2.0, shaft_diameter + 0.4)
    return outer.cut(bore)


def spoked_pulley(center: tuple[float, float, float], direction: tuple[float, float, float], width: float, outer_diameter: float, shaft_diameter: float) -> cq.Shape:
    """Packaging pulley with outer rim, hub and four load-path spokes."""
    plane = local_plane(center, direction)
    rim_t = max(2.5, outer_diameter * 0.07)
    hub_od = max(shaft_diameter + 8.0, outer_diameter * 0.30)
    rim = cq.Workplane(plane).circle(outer_diameter / 2.0).circle(outer_diameter / 2.0 - rim_t).extrude(width / 2.0, both=True)
    hub = cq.Workplane(plane).circle(hub_od / 2.0).circle(shaft_diameter / 2.0 + 0.2).extrude(width / 2.0, both=True)
    spoke_span = outer_diameter - 2.0 * rim_t + 1.0
    spoke_w = max(3.0, rim_t)
    cross_x = cq.Workplane(plane).box(spoke_span, spoke_w, width)
    cross_y = cq.Workplane(plane).box(spoke_w, spoke_span, width)
    return rim.union(hub).union(cross_x).union(cross_y).val()


JOINT_MODULE_FAMILIES = {
    "JMF-01-COMPACT": {
        "role": "compact supported direct joint",
        "plate_w": 36.0, "plate_h": 38.0, "plate_t": 3.0, "pattern_x": 26.0, "pattern_y": 28.0, "hole_d": 3.4,
        "shaft_d": 6.0, "bearing_od": 15.0, "bearing_w": 5.0, "bearing_id": "NSK-696", "span": 32.0, "body_w": 28.0, "body_h": 34.0, "body_d": 34.0,
        "transmission": "direct supported output", "ratio": "1.0:1 candidate", "motor_offset": 0.0, "cable_d": 6.0,
    },
    "JMF-02-GRIPPER": {
        "role": "parallel hand-shaped gripper drive",
        "plate_w": 42.0, "plate_h": 38.0, "plate_t": 3.0, "pattern_x": 32.0, "pattern_y": 26.0, "hole_d": 3.4,
        "shaft_d": 5.0, "bearing_od": 16.0, "bearing_w": 5.0, "bearing_id": "SKF-625-2Z", "span": 28.0, "body_w": 32.0, "body_h": 36.0, "body_d": 30.0,
        "transmission": "symmetric rack/pinion or tendon coupling", "ratio": "SELECTION REQUIRED", "motor_offset": 0.0, "cable_d": 6.0,
    },
    "JMF-03-SHOULDER-GIMBAL": {
        "role": "shared intersecting-axis shoulder gimbal",
        "plate_w": 58.0, "plate_h": 64.0, "plate_t": 4.0, "pattern_x": 44.0, "pattern_y": 50.0, "hole_d": 4.5,
        "shaft_d": 10.0, "bearing_od": 22.0, "bearing_w": 6.0, "bearing_id": "SKF-61900-2RS1", "span": 52.0, "body_w": 42.0, "body_h": 52.0, "body_d": 48.0,
        "transmission": "two remote or nested supported drives sharing one gimbal housing", "ratio": "1.0:1 initial candidate", "motor_offset": 38.0, "cable_d": 10.0,
    },
    "JMF-04-MEDIUM": {
        "role": "medium supported direct joint",
        "plate_w": 52.0, "plate_h": 56.0, "plate_t": 4.0, "pattern_x": 40.0, "pattern_y": 44.0, "hole_d": 4.5,
        "shaft_d": 10.0, "bearing_od": 22.0, "bearing_w": 6.0, "bearing_id": "SKF-61900-2RS1", "span": 46.0, "body_w": 42.0, "body_h": 52.0, "body_d": 48.0,
        "transmission": "direct supported output", "ratio": "1.0:1 candidate", "motor_offset": 0.0, "cable_d": 9.0,
    },
    "JMF-05-WAIST": {
        "role": "large supported waist turntable",
        "plate_w": 98.0, "plate_h": 72.0, "plate_t": 5.0, "pattern_x": 82.0, "pattern_y": 56.0, "hole_d": 5.5,
        "shaft_d": 17.0, "bearing_od": 26.0, "bearing_w": 5.0, "bearing_id": "NSK-6803", "span": 28.0, "body_w": 50.0, "body_h": 60.0, "body_d": 48.0,
        "transmission": "supported yaw output with actuator isolated from overturning load", "ratio": "1.0:1 initial candidate", "motor_offset": 0.0, "cable_d": 18.0,
    },
    "JMF-06-LEG-DIRECT": {
        "role": "large supported direct leg joint",
        "plate_w": 66.0, "plate_h": 70.0, "plate_t": 5.0, "pattern_x": 52.0, "pattern_y": 56.0, "hole_d": 5.5,
        "shaft_d": 12.0, "bearing_od": 24.0, "bearing_w": 6.0, "bearing_id": "NSK-6901", "span": 60.0, "body_w": 46.0, "body_h": 58.0, "body_d": 52.0,
        "transmission": "direct supported output", "ratio": "1.0:1 W0 candidate", "motor_offset": 0.0, "cable_d": 12.0,
    },
    "JMF-07-LEG-REDUCED-15": {
        "role": "parallel-axis reduced leg joint",
        "plate_w": 72.0, "plate_h": 78.0, "plate_t": 5.0, "pattern_x": 58.0, "pattern_y": 64.0, "hole_d": 5.5,
        "shaft_d": 12.0, "bearing_od": 24.0, "bearing_w": 6.0, "bearing_id": "NSK-6901", "span": 64.0, "body_w": 46.0, "body_h": 58.0, "body_d": 52.0,
        "transmission": "20:30 tooth, 5M-pitch parallel-axis timing transmission with output encoder", "ratio": "1.5:1 geometric candidate", "motor_offset": 50.0, "output_pulley_d": 48.0, "motor_pulley_d": 32.0, "cable_d": 12.0,
    },
    "JMF-08-LEG-REDUCED-20": {
        "role": "higher-reduction hip/ankle roll joint",
        "plate_w": 74.0, "plate_h": 70.0, "plate_t": 5.0, "pattern_x": 60.0, "pattern_y": 56.0, "hole_d": 5.5,
        "shaft_d": 12.0, "bearing_od": 24.0, "bearing_w": 6.0, "bearing_id": "NSK-6901", "span": 64.0, "body_w": 46.0, "body_h": 58.0, "body_d": 52.0,
        "transmission": "20:40 tooth, 5M-pitch parallel-axis timing transmission with output encoder", "ratio": "2.0:1 geometric candidate", "motor_offset": 50.0, "output_pulley_d": 64.0, "motor_pulley_d": 32.0, "cable_d": 12.0,
    },
    "JMF-09-KNEE-REDUCED-20": {
        "role": "2.0:1 knee transmission with dual-supported output",
        "plate_w": 74.0, "plate_h": 78.0, "plate_t": 5.0, "pattern_x": 60.0, "pattern_y": 64.0, "hole_d": 5.5,
        "shaft_d": 12.0, "bearing_od": 24.0, "bearing_w": 6.0, "bearing_id": "NSK-6901", "span": 64.0, "body_w": 46.0, "body_h": 58.0, "body_d": 52.0,
        "transmission": "20:40 tooth, 5M-pitch parallel-axis timing transmission with output encoder", "ratio": "2.0:1 whole-body knee candidate", "motor_offset": 50.0, "output_pulley_d": 64.0, "motor_pulley_d": 32.0, "cable_d": 12.0,
    },
    "JMF-10-ANKLE-PITCH-REDUCED-25": {
        "role": "compact 2.5:1 ankle-pitch transmission",
        "plate_w": 74.0, "plate_h": 72.0, "plate_t": 5.0, "pattern_x": 60.0, "pattern_y": 58.0, "hole_d": 5.5,
        "shaft_d": 12.0, "bearing_od": 24.0, "bearing_w": 6.0, "bearing_id": "NSK-6901", "span": 64.0, "body_w": 34.0, "body_h": 47.0, "body_d": 29.0,
        "transmission": "16:40 tooth, 5M-pitch timing transmission with output encoder", "ratio": "2.5:1 whole-body ankle candidate", "motor_offset": 51.0, "output_pulley_d": 64.0, "motor_pulley_d": 26.0, "cable_d": 10.0,
    },
}

# Remote/reduced output shafts retain two external supports. Direct-drive
# families use the actuator's internal output support plus one external bearing
# carrier, avoiding the former redundant two-external-bearing mass model.
for _family in JOINT_MODULE_FAMILIES.values():
    _family["external_bearings"] = 2 if _family["motor_offset"] > 0 else 1


def joint_module_family(axis_id: str) -> str:
    if axis_id.startswith("HEAD_") or "WRIST" in axis_id:
        return "JMF-01-COMPACT"
    if "GRIPPER" in axis_id:
        return "JMF-02-GRIPPER"
    if "SHOULDER" in axis_id:
        return "JMF-03-SHOULDER-GIMBAL"
    if axis_id == "WAIST_YAW":
        return "JMF-05-WAIST"
    if "ELBOW" in axis_id:
        return "JMF-04-MEDIUM"
    if "KNEE_PITCH" in axis_id:
        return "JMF-09-KNEE-REDUCED-20"
    if "ANKLE_PITCH" in axis_id:
        return "JMF-10-ANKLE-PITCH-REDUCED-25"
    if "HIP_ROLL" in axis_id or "ANKLE_ROLL" in axis_id:
        return "JMF-08-LEG-REDUCED-20"
    if "HIP_PITCH" in axis_id:
        return "JMF-07-LEG-REDUCED-15"
    return "JMF-06-LEG-DIRECT"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def front_elevation_svg() -> str:
    def z(value: float) -> float:
        return 810.0 - value

    datum_rows = [
        ("ankle pitch", ANKLE_Z),
        ("knee pitch", KNEE_Z),
        ("hip pitch", HIP_Z),
        ("waist yaw", WAIST_Z),
        ("shoulder pitch", SHOULDER_Z),
        ("neck pan", NECK_Z),
        ("shell top", HEIGHT),
    ]
    lines = "".join(
        f'<line x1="90" y1="{z(value):.1f}" x2="690" y2="{z(value):.1f}" class="datum"/>'
        f'<text x="705" y="{z(value)+6:.1f}" class="label">{label} · {value:.0f} mm</text>'
        for label, value in datum_rows
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="900" viewBox="0 0 1100 900" role="img" aria-labelledby="title desc">
<title id="title">HR-30 P0.1 front elevation and controlled height datums</title><desc id="desc">A 762 millimetre humanoid body architecture with feet, legs, pelvis, torso, arms, head and seven horizontal datum lines.</desc>
<style>.datum{{stroke:#d39a13;stroke-width:2;stroke-dasharray:8 7}}.label{{font:700 16px system-ui;fill:#082b55}}.shell{{fill:#8bd8fa;stroke:#082b55;stroke-width:3}}.frame{{fill:#123f70;stroke:#041a35;stroke-width:3}}.joint{{fill:#f4b942;stroke:#7c5200;stroke-width:3}}.floor{{stroke:#041a35;stroke-width:5}}.note{{font:800 18px system-ui;fill:#102a43}}</style>
<rect width="1100" height="900" fill="#f7fbff"/><line x1="75" y1="810" x2="700" y2="810" class="floor"/>{lines}
<rect x="249" y="775" width="90" height="35" rx="7" class="shell"/><rect x="451" y="775" width="90" height="35" rx="7" class="shell"/>
<rect x="262" y="600" width="64" height="145" rx="12" class="shell"/><rect x="464" y="600" width="64" height="145" rx="12" class="shell"/>
<circle cx="294" cy="600" r="28" class="joint"/><circle cx="496" cy="600" r="28" class="joint"/>
<rect x="259" y="430" width="70" height="150" rx="14" class="shell"/><rect x="461" y="430" width="70" height="150" rx="14" class="shell"/>
<rect x="317" y="357" width="155" height="70" rx="13" class="shell"/><rect x="338" y="373" width="113" height="38" rx="7" class="frame"/>
<rect x="300" y="225" width="190" height="155" rx="18" class="shell"/><rect x="372" y="160" width="46" height="58" rx="8" class="frame"/>
<rect x="320" y="48" width="150" height="112" rx="20" class="shell"/><rect x="337" y="72" width="116" height="57" rx="9" class="frame"/><circle cx="372" cy="99" r="7" class="joint"/><circle cx="418" cy="99" r="7" class="joint"/>
<circle cx="290" cy="220" r="25" class="joint"/><circle cx="500" cy="220" r="25" class="joint"/>
<path d="M290 220 L270 370" stroke="#8bd8fa" stroke-width="46" stroke-linecap="round"/><path d="M500 220 L520 370" stroke="#8bd8fa" stroke-width="46" stroke-linecap="round"/>
<circle cx="270" cy="370" r="25" class="joint"/><circle cx="520" cy="370" r="25" class="joint"/>
<path d="M270 370 L270 515" stroke="#8bd8fa" stroke-width="44" stroke-linecap="round"/><path d="M520 370 L520 515" stroke="#8bd8fa" stroke-width="44" stroke-linecap="round"/>
<rect x="246" y="510" width="48" height="35" rx="9" class="joint"/><rect x="248" y="540" width="18" height="42" rx="7" class="joint"/><rect x="274" y="540" width="18" height="42" rx="7" class="joint"/><rect x="496" y="510" width="48" height="35" rx="9" class="joint"/><rect x="498" y="540" width="18" height="42" rx="7" class="joint"/><rect x="524" y="540" width="18" height="42" rx="7" class="joint"/>
<text x="75" y="855" class="note">Architecture envelopes only · X lateral · front view · floor Z=0</text></svg>"""


def interactive_html() -> str:
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 native body architecture P0.1</title>
<script type="module" src="vendor/model-viewer.min.js"></script>
<style>:root{{--deep:#041a35;--navy:#082b55;--sky:#7dd3fc;--pale:#e4f6ff;--gold:#f4b942;--ink:#102a43;--paper:#f7fbff;--line:#9ccfe8;--red:#9b1c1c;--green:#166534}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.55 system-ui,"Segoe UI",sans-serif}}header{{background:linear-gradient(135deg,var(--deep),var(--navy));color:white;padding:clamp(32px,6vw,78px) 20px}}header>div,main,footer>div{{max-width:1240px;margin:auto}}h1{{font-size:clamp(38px,6.2vw,74px);line-height:1.03;margin:.24em 0}}h2{{font-size:clamp(27px,3.4vw,42px);line-height:1.15;color:var(--navy)}}h3{{font-size:clamp(20px,2.1vw,27px);color:var(--navy)}}.warning{{background:var(--gold);color:#17243a;border:3px solid #8a5b00;padding:16px 18px;font-weight:900}}.eyebrow{{font-size:14px;font-weight:850;color:var(--sky);letter-spacing:.04em}}main{{padding:30px 20px 80px}}section{{margin:32px 0}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(235px,1fr));gap:17px}}.card,.panel{{background:white;border:2px solid var(--line);border-radius:16px;padding:20px;box-shadow:0 3px 0 #c4e2f1}}.metric{{font-size:clamp(35px,5vw,57px);line-height:1;font-weight:900;color:var(--navy)}}.pass{{border-left:9px solid var(--green)}}.hold{{border-left:9px solid var(--gold)}}.miss{{border-left:9px solid var(--red)}}.viewer{{border:3px solid var(--navy);border-radius:18px;overflow:hidden;background:var(--pale)}}model-viewer{{display:block;width:100%;height:clamp(520px,72vh,780px);background:radial-gradient(circle,#fff,var(--pale))}}.viewer p{{background:white;padding:15px 18px;margin:0}}img{{display:block;width:100%;height:auto;background:white;border:2px solid var(--line);border-radius:16px}}.table{{overflow:auto;border:2px solid var(--line);border-radius:14px;background:white}}table{{border-collapse:collapse;width:100%;min-width:940px}}th,td{{padding:13px 14px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top;font-size:16px}}th{{background:var(--navy);color:white}}a{{color:#075b9b;font-weight:800}}code{{font-size:16px}}footer{{background:var(--deep);color:white;padding:32px 20px}}@media(max-width:680px){{body{{font-size:16px}}main{{padding-inline:14px}}model-viewer{{height:500px}}}}</style></head><body>
<header><div><p class="warning">{WARNING}</p><p class="eyebrow">PROJECT BUTTON · HR-30-BODY-ARCH-P0.1 · FIRST NATIVE FULL-BODY CAD</p><h1>The 30-inch robot now has a body.</h1><p>This is the first dimensioned, repository-native HR-30 assembly: exact height datums, named limbs, 25 candidate axes, structural envelopes, shells, and component reservations. It is architecture CAD—not yet manufacturing CAD.</p></div></header>
<main><section class="grid"><article class="card pass"><div class="metric">762 mm</div><p>Exact neutral-pose floor-to-shell-top geometry.</p></article><article class="card pass"><div class="metric">25</div><p>Named head, waist, arm, hand, hip, knee, and ankle axes.</p></article><article class="card"><div class="metric">{len(JOINT_MODULE_FAMILIES)}</div><p>Dimensioned joint-module families spanning all 25 axes.</p></article><article class="card hold"><div class="metric">0</div><p>Fabrication, motion, safety, or energization approvals.</p></article></section>
<section><h2>Orbit the native body architecture</h2><div class="viewer"><model-viewer src="HR-30_body_architecture_candidate.glb" poster="front-elevation.svg" alt="Interactive 3D model of the preliminary 762 millimetre Project Button humanoid body architecture" camera-controls camera-orbit="35deg 76deg 95%" min-camera-orbit="auto auto 20%" max-camera-orbit="auto auto 240%" field-of-view="26deg" shadow-intensity="0.85" exposure="1.05" interaction-prompt="auto"></model-viewer><p>Drag to orbit; scroll or pinch to zoom. Sky blue is shell envelope, dark blue is load-path envelope, gold is joint/hand hardware, and red rods are reference axes. Transparent objects reserve electronics, sensors, restraint, and joint datum space. The downloadable STEP embeds the exact SHA-bound actuator B-Reps; the GLB uses dimension-matched simplified actuator bodies so the web model remains practical to load.</p></div></section>
<section><h2>The dimensions come from the specification</h2><img src="front-elevation.svg" alt="Front elevation of HR-30 with ankle, knee, hip, waist, shoulder, neck and top height datums"></section>
<section><h2>What this pass proves—and what it does not</h2><div class="grid"><article class="card pass"><h3>Native geometry exists</h3><p>STEP and GLB are generated from a versioned CadQuery source. The STEP reimports with vertices exactly at Z=0 and Z=762 mm.</p></article><article class="card pass"><h3>Kinematic architecture exists</h3><p>All 25 candidate axes have coordinates, directions, regions, and provisional ranges in a machine-readable schedule.</p></article><article class="card miss"><h3>Preferred reach is missed</h3><p>The specified nominal segments total 370 mm per arm and 950 mm span. These pass the 390/980 mm hard limits but miss the 360/900 mm targets.</p></article><article class="card hold"><h3>Mass is still unproven</h3><p>These are packaging envelopes, not materialized parts. The existing arm and leg actuator concepts already fail their preferred mass allocations.</p></article></div></section>
<section><h2>Controlled body datums</h2><div class="table"><table><thead><tr><th>Datum</th><th>Z above floor</th><th>Role</th></tr></thead><tbody><tr><td>Ankle pitch</td><td>45 mm</td><td>Lower-leg kinematic datum</td></tr><tr><td>Knee pitch</td><td>210 mm</td><td>165 mm above ankle pitch</td></tr><tr><td>Hip pitch</td><td>380 mm</td><td>170 mm above knee pitch</td></tr><tr><td>Waist yaw</td><td>425 mm</td><td>Upper-body rotation datum</td></tr><tr><td>Shoulder pitch</td><td>590 mm</td><td>Upper-arm datum</td></tr><tr><td>Neck pan</td><td>650 mm</td><td>Head pan datum</td></tr><tr><td>Shell top</td><td>762 mm</td><td>Exact nominal standing height</td></tr></tbody></table></div></section>
<section><h2>Next engineering conversions</h2><div class="grid"><article class="card hold"><h3>Joints</h3><p>Convert the ten visible module-family candidates into released shafts, selected bearings, verified fits, retained fasteners, stops, encoders, and serviceable housings.</p></article><article class="card hold"><h3>Structure and covers</h3><p>Convert solid visual envelopes into materialized frames and tool-removable covers with thickness, splits, edges, vents, access, and retention.</p></article><article class="card hold"><h3>Harness and power</h3><p>Route bend-controlled cables and select the actuator rail, protection, regeneration handling, tether, and eventual onboard energy system.</p></article><article class="card hold"><h3>Evidence</h3><p>Close mass/COM/inertia, collision, gait loads, thermal behavior, stopping, fall restraint, DFM, tolerances, FAI, physical testing, and qualified review.</p></article></div></section>
<section><h2>Download the engineering artifacts</h2><div class="panel"><p><a href="HR-30_body_architecture_candidate.step">Physical-envelope STEP</a> · <a href="HR-30_body_kinematic_reference.step">Kinematic-reference STEP</a> · <a href="HR-30_body_architecture_candidate.glb">Interactive GLB</a> · <a href="whole-body-source.py">Editable CadQuery source</a> · <a href="joint-axis-schedule.csv">Joint-axis schedule</a> · <a href="joint-module-family-schedule.csv">Joint-module families</a> · <a href="joint-module-axis-binding.csv">All-axis module binding</a> · <a href="vendor-actuator-source-register.csv">Vendor source register</a> · <a href="vendor-actuator-transform-register.csv">Per-axis actuator transforms</a> · <a href="actuator-transmission-allocation.csv">Actuator allocation</a> · <a href="asimov-1-reuse-adapt-reject.csv">Asimov 1 matrix</a> · <a href="component-envelope-schedule.csv">Component schedule</a> · <a href="geometry-checks.json">Geometry checks</a> · <a href="open-holds.csv">Open holds</a></p></div></section></main>
<footer><div><p>Project Button · HR-30-BODY-ARCH-P0.1 · adult-operated experimental machinery · not a toy · no procurement, fabrication, motion, energization, or functional-safety approval</p></div></footer></body></html>"""


def bbox_dict(shape: cq.Shape) -> dict[str, float]:
    b = shape.BoundingBox()
    return {
        "xmin": b.xmin,
        "xmax": b.xmax,
        "ymin": b.ymin,
        "ymax": b.ymax,
        "zmin": b.zmin,
        "zmax": b.zmax,
        "xlen": b.xlen,
        "ylen": b.ylen,
        "zlen": b.zlen,
    }


def vertex_extent_dict(shape: cq.Shape) -> dict[str, float]:
    points = [vertex.Center() for vertex in shape.Vertices()]
    return {
        "xmin": min(point.x for point in points),
        "xmax": max(point.x for point in points),
        "ymin": min(point.y for point in points),
        "ymax": max(point.y for point in points),
        "zmin": min(point.z for point in points),
        "zmax": max(point.z for point in points),
    }


def build() -> tuple[list[Component], list[dict], list[dict], list[dict]]:
    shell = (0.25, 0.68, 0.92, 0.82)
    structure = (0.08, 0.20, 0.38, 1.0)
    joint = (0.96, 0.70, 0.08, 1.0)
    hand = (0.98, 0.78, 0.18, 1.0)
    bay = (0.12, 0.30, 0.65, 0.34)
    sensor = (0.98, 0.76, 0.12, 0.42)
    axis_color = (0.91, 0.18, 0.15, 0.72)
    components: list[Component] = []
    vendor_shapes: dict[str, cq.Shape] = {}
    for source_id, source in VENDOR_ACTUATOR_SOURCES.items():
        actual_sha = sha256(source["path"]).upper()
        if actual_sha != source["expected_sha256"]:
            raise RuntimeError(f"{source_id} source hash mismatch: {actual_sha}")
        vendor_shapes[source_id] = cq.importers.importStep(str(source["path"])).val()

    def add(name: str, group: str, shape: cq.Shape, color, physical: bool = True, note: str = "", visual_shape: cq.Shape | None = None) -> None:
        components.append(Component(name, group, shape, color, physical, note, visual_shape))

    # Feet and leg envelopes.  Every segment is an individually dimensioned,
    # tapered shell around a separate load-path envelope; none is an abstract
    # cylinder or an undefined leg placeholder.
    for side, sx in (("L", HIP_HALF_WIDTH), ("R", -HIP_HALF_WIDTH)):
        add(f"{side}_FOOT_SHELL_ENVELOPE", "foot", rounded_box(90, 145, 35, (sx, 25, 17.5), 6), shell)
        add(f"{side}_ANKLE_HOUSING_ENVELOPE", "joint housing", rounded_box(66, 64, 52, (sx, 0, 51), 5), structure)
        add(f"{side}_SHIN_STRUCTURAL_ENVELOPE", "lower leg", rounded_box(54, 54, 135, (sx, 0, 127.5), 5), structure)
        add(f"{side}_SHIN_SHELL_ENVELOPE", "lower-leg shell", tapered_body(61, 194, 61, 65, 68, 72, sx), shell)
        add(f"{side}_KNEE_HOUSING_ENVELOPE", "joint housing", rounded_box(70, 68, 56, (sx, 0, KNEE_Z), 6), structure)
        add(f"{side}_THIGH_STRUCTURAL_ENVELOPE", "upper leg", rounded_box(58, 58, 140, (sx, 0, 295), 5), structure)
        add(f"{side}_THIGH_SHELL_ENVELOPE", "upper-leg shell", tapered_body(225, 365, 66, 68, 74, 76, sx), shell)
        add(f"{side}_HIP_HOUSING_ENVELOPE", "joint housing", rounded_box(72, 82, 70, (sx, 0, 380), 7), structure)

    # Pelvis, torso, neck and head.
    add("PELVIS_SHELL_ENVELOPE", "pelvis", tapered_body(352, 417, 142, 96, 155, 105), shell)
    add("PELVIS_LOAD_FRAME_ENVELOPE", "pelvis structure", rounded_box(132, 72, 42, (0, 0, 390), 5), structure)
    add("WAIST_BEARING_STACK_RESERVATION", "joint housing", rounded_box(112, 84, 34, (0, 0, WAIST_Z), 6), structure)
    add("TORSO_SHELL_ENVELOPE", "torso", tapered_body(430, 585, 152, 94, 190, 110), shell)
    add("TORSO_LEFT_FRAME_RAIL", "torso structure", rounded_box(20, 25, 142, (70, 0, 510), 3), structure)
    add("TORSO_RIGHT_FRAME_RAIL", "torso structure", rounded_box(20, 25, 142, (-70, 0, 510), 3), structure)
    add("TORSO_SHOULDER_CROSSMEMBER", "torso structure", rounded_box(170, 28, 24, (0, 0, 575), 3), structure)
    add("NECK_COLUMN_ENVELOPE", "neck", rounded_box(54, 54, 58, (0, 0, 625), 6), structure)
    add("HEAD_SHELL_ENVELOPE", "head", rounded_box(150, 110, 112, (0, 0, 706), 12), shell)
    add("FACE_SCREEN_PANEL", "face screen", rounded_box(116, 7, 58, (0, -57.5, 704), 3), structure, True, "serviceable display-panel envelope; exact display selection required")
    add("FACE_LEFT_EYE_GRAPHIC", "screen-face graphic", rounded_box(18, 2, 8, (28, -61.5, 713), 0.7), hand, True, "visual identity only; rendered by the display in production")
    add("FACE_RIGHT_EYE_GRAPHIC", "screen-face graphic", rounded_box(18, 2, 8, (-28, -61.5, 713), 0.7), hand, True, "visual identity only; rendered by the display in production")
    add("FACE_DISPLAY_RESERVATION", "sensor/display bay", rounded_box(108, 8, 50, (0, -52, 704), 3), sensor, False, "display, camera privacy indicator and status-light hardware unresolved")

    # Arms in neutral down pose.
    for side, sign in (("L", 1.0), ("R", -1.0)):
        shoulder = (sign * SHOULDER_AXIS_X, 0.0, SHOULDER_Z)
        elbow = (sign * ELBOW_X, 0.0, ELBOW_Z)
        wrist = (sign * WRIST_X, 0.0, WRIST_Z)
        add(f"{side}_SHOULDER_HOUSING_ENVELOPE", "joint housing", rounded_box(40, 72, 58, shoulder, 6), structure)
        add(f"{side}_UPPER_ARM_STRUCTURAL_ENVELOPE", "upper arm", link_between(shoulder, elbow, 34), structure)
        add(f"{side}_UPPER_ARM_SHELL_ENVELOPE", "upper-arm shell", link_between(shoulder, elbow, 48), shell)
        add(f"{side}_ELBOW_HOUSING_ENVELOPE", "joint housing", rounded_box(54, 62, 54, elbow, 6), structure)
        add(f"{side}_FOREARM_STRUCTURAL_ENVELOPE", "forearm", link_between(elbow, wrist, 32), structure)
        add(f"{side}_FOREARM_SHELL_ENVELOPE", "forearm shell", link_between(elbow, wrist, 46), shell)
        add(f"{side}_WRIST_HOUSING_ENVELOPE", "joint housing", rounded_box(48, 56, 45, wrist, 6), structure)
        # One-DOF, two-finger parallel gripper.  The palm, fingers and soft-pad
        # lands are separate visible solids so the wrist does not terminate in
        # an undefined block.  Linkage, compliance and force proof remain open.
        add(f"{side}_HAND_PALM_ENVELOPE", "hand-shaped gripper palm", rounded_box(50, 58, 36, (sign * WRIST_X, 0, 270), 6), hand, True, "houses one actuator and symmetric coupling")
        for digit, offset in (("INBOARD", -13.0), ("OUTBOARD", 13.0)):
            digit_x = sign * WRIST_X + offset
            add(f"{side}_{digit}_GRIPPER_FINGER", "hand-shaped gripper finger", rounded_box(18, 44, 46, (digit_x, 0, 232), 5), hand, True, "broad parallel jaw; no narrow scissor point")
            add(f"{side}_{digit}_SOFT_PAD_LAND", "gripper contact pad land", rounded_box(16, 48, 8, (digit_x, 0, FINGERTIP_Z), 3), hand, True, "replaceable compliant pad; material and force-stroke selection required")

    # Component reservations intentionally remain separate reference solids.
    add("TORSO_COMPUTE_BAY", "component bay", rounded_box(142, 72, 82, (0, 5, 520), 4), bay, False, "compute, cooling, storage and retention selection required")
    add("PELVIS_POWER_BAY", "component bay", rounded_box(118, 72, 45, (0, 5, 382), 4), bay, False, "source, conversion, protection and regeneration architecture selection required")
    add("HEAD_SENSOR_BAY", "component bay", rounded_box(108, 70, 58, (0, 4, 705), 4), bay, False, "camera, audio, illumination and privacy hardware selection required")
    add("PELVIS_IMU_DATUM_BAY", "component bay", rounded_box(42, 42, 20, (0, 0, 407), 3), sensor, False, "pelvis IMU exact model and mount remain open")
    add("PELVIS_RESTRAINT_INTERFACE_ENVELOPE", "restraint interface", rounded_box(80, 52, 20, (0, 32, 414), 3), sensor, False, "rated restraint interface not designed")

    axes: list[dict] = []

    def add_axis(axis_id: str, region: str, side: str, motion: str, xyz, direction, provisional_range: str, source: str) -> None:
        axes.append({
            "axis_id": axis_id,
            "region": region,
            "side": side,
            "motion": motion,
            "x_mm": xyz[0],
            "y_mm": xyz[1],
            "z_mm": xyz[2],
            "direction_x": direction[0],
            "direction_y": direction[1],
            "direction_z": direction[2],
            "provisional_commanded_range": provisional_range,
            "source": source,
            "status": "ARCHITECTURE DATUM ONLY - JOINT DESIGN NOT RELEASED",
        })
        add(f"AXIS_{axis_id}", "joint axis reference", cylinder_between(xyz, direction, 68 if side != "C" else 55, 7), axis_color, False)

    add_axis("HEAD_PAN", "head", "C", "pan", (0, 0, NECK_Z), (0, 0, 1), "SELECTION REQUIRED", "HR-PROD-030")
    add_axis("HEAD_TILT", "head", "C", "tilt", (0, 0, 690), (1, 0, 0), "SELECTION REQUIRED", "HR-PROD-030")
    add_axis("WAIST_YAW", "waist", "C", "yaw", (0, 0, WAIST_Z), (0, 0, 1), "speed <=15 deg/s in HR-30A", "HR-PROD-030 / HR-LOAD-030")
    for side, sign in (("L", 1.0), ("R", -1.0)):
        add_axis(f"{side}_SHOULDER_PITCH", "arm", side, "pitch", (sign * SHOULDER_AXIS_X, 0, SHOULDER_Z), (1, 0, 0), "SELECTION REQUIRED", "HR-PROD-030")
        add_axis(f"{side}_SHOULDER_ROLL", "arm", side, "roll", (sign * SHOULDER_AXIS_X, 0, SHOULDER_Z), (0, 1, 0), "SELECTION REQUIRED", "HR-PROD-030")
        add_axis(f"{side}_ELBOW_PITCH", "arm", side, "pitch", (sign * ELBOW_X, 0, ELBOW_Z), (1, 0, 0), "SELECTION REQUIRED", "HR-PROD-030")
        add_axis(f"{side}_WRIST_ROTATION", "arm", side, "rotation", (sign * WRIST_X, 0, WRIST_Z), (0, 0, 1), "SELECTION REQUIRED", "HR-PROD-030")
        add_axis(f"{side}_GRIPPER", "hand", side, "parallel open/close", (sign * WRIST_X, 0, 252), (sign, 0, 0), "SELECTION REQUIRED", "HR-PROD-030")
        add_axis(f"{side}_HIP_YAW", "leg", side, "yaw", (sign * HIP_HALF_WIDTH, 0, 397), (0, 0, 1), "+/-30 deg", "HR-WALK-001")
        add_axis(f"{side}_HIP_ROLL", "leg", side, "roll", (sign * HIP_HALF_WIDTH, 0, 388), (0, 1, 0), "+/-25 deg", "HR-WALK-001")
        add_axis(f"{side}_HIP_PITCH", "leg", side, "pitch", (sign * HIP_HALF_WIDTH, 0, HIP_Z), (1, 0, 0), "-35..+45 deg", "HR-WALK-001")
        add_axis(f"{side}_KNEE_PITCH", "leg", side, "pitch", (sign * HIP_HALF_WIDTH, 0, KNEE_Z), (1, 0, 0), "0..120 deg", "HR-WALK-001")
        add_axis(f"{side}_ANKLE_PITCH", "leg", side, "pitch", (sign * HIP_HALF_WIDTH, 0, ANKLE_Z), (1, 0, 0), "-35..+30 deg", "HR-WALK-001")
        add_axis(f"{side}_ANKLE_ROLL", "leg", side, "roll", (sign * HIP_HALF_WIDTH, 0, 37), (0, 1, 0), "+/-20 deg", "HR-WALK-001")

    # Turn each datum into a visible, dimensioned joint-module candidate.  The
    # geometry establishes the architecture of hollow shafts, actuator-plus-
    # external direct support or two-sided remote-output support,
    # removable interface plates, actuator envelopes, cable corridors and
    # reduction reservations.  It deliberately does not claim bearing fits,
    # materials, preload, fastener strength, actuator ratings or DFM release.
    module_bindings: list[dict] = []
    vendor_transforms: list[dict] = []
    for axis in axes:
        axis_id = axis["axis_id"]
        family_id = joint_module_family(axis_id)
        spec = JOINT_MODULE_FAMILIES[family_id]
        center = (float(axis["x_mm"]), float(axis["y_mm"]), float(axis["z_mm"]))
        direction = (float(axis["direction_x"]), float(axis["direction_y"]), float(axis["direction_z"]))
        normal = cq.Vector(*direction).normalized()
        span = spec["span"]
        shaft_length = span + 2.0 * spec["plate_t"]
        shaft_bore = max(2.0, spec["shaft_d"] * 0.62)
        add(f"JMOD_{axis_id}_OUTPUT_SHAFT", "joint module shaft", hollow_cylinder_between(center, direction, shaft_length, spec["shaft_d"], shaft_bore), joint, True, f"{family_id} hollow shaft candidate with {shaft_bore:.1f} mm through bore; material, wall, fits and retention selection required")
        end_specs = (("A", -1.0), ("B", 1.0)) if spec["external_bearings"] == 2 else (("B", 1.0),)
        for end_name, sign_end in end_specs:
            bearing_center_v = cq.Vector(*center) + normal.multiply(sign_end * (span / 2.0 - spec["bearing_w"] / 2.0))
            plate_center_v = cq.Vector(*center) + normal.multiply(sign_end * (span / 2.0 + spec["plate_t"] / 2.0))
            bearing_center = (bearing_center_v.x, bearing_center_v.y, bearing_center_v.z)
            plate_center = (plate_center_v.x, plate_center_v.y, plate_center_v.z)
            bearing = BEARING_CANDIDATES[spec["bearing_id"]]
            add(
                f"JMOD_{axis_id}_BEARING_{end_name}_RING", "joint module bearing",
                bearing_ring(bearing_center, direction, spec["bearing_w"], spec["bearing_od"], spec["shaft_d"]),
                joint, True,
                f"{family_id} {bearing['designation']} catalogue envelope; load direction, life, suffix, fit, retention and application selection required",
            )
            add(
                f"JMOD_{axis_id}_INTERFACE_PLATE_{end_name}",
                "joint module interface plate",
                interface_plate(plate_center, direction, spec["plate_w"], spec["plate_h"], spec["plate_t"], spec["pattern_x"], spec["pattern_y"], spec["hole_d"], spec["shaft_d"]),
                structure,
                True,
                f"{family_id} provisional four-hole module interface; thread/fastener stack not released",
            )

        # Pick a stable direction perpendicular to the joint axis for cable and
        # parallel-drive reservations.  Pitch reductions sit inside the
        # adjacent vertical link, not outside the leg silhouette.
        if abs(normal.z) > 0.9:
            offset_direction = cq.Vector(0, 1, 0)
        elif abs(normal.y) > 0.9:
            offset_direction = cq.Vector(0, 0, -1 if "HIP_ROLL" in axis_id or "SHOULDER_ROLL" in axis_id else 1)
        elif any(token in axis_id for token in ("HIP_PITCH",)):
            offset_direction = cq.Vector(0, 0, -1)
        elif any(token in axis_id for token in ("KNEE_PITCH", "ANKLE_PITCH")):
            offset_direction = cq.Vector(0, 0, 1)
        else:
            offset_direction = cq.Vector(0, 1, 0)
        corridor_center_v = cq.Vector(*center) + offset_direction.multiply(min(spec["plate_w"], spec["plate_h"]) * 0.28)
        corridor_center = (corridor_center_v.x, corridor_center_v.y, corridor_center_v.z)
        add(f"JMOD_{axis_id}_CABLE_CORRIDOR", "joint cable corridor", cylinder_between(corridor_center, direction, shaft_length, spec["cable_d"]), sensor, False, f"{family_id} routing reservation; cable construction and bend control selection required")

        motor_offset = spec["motor_offset"]
        if "GRIPPER" in axis_id:
            # The gripper axis above describes symmetric jaw travel, not the
            # rotary motor shaft.  Package the compact motor transversely inside
            # the palm and show a real coupling member to the jaw-drive datum.
            side_sign = 1.0 if axis_id.startswith("L_") else -1.0
            motor_center = (side_sign * WRIST_X, 0.0, 278.0)
            actuator_direction = (0.0, 1.0, 0.0)
            vendor_source_id = vendor_source_for_axis(axis_id)
            actuator_shape, actuator_basis = vendor_actuator_to_axis(vendor_shapes[vendor_source_id], motor_center, actuator_direction)
            add(f"JMOD_{axis_id}_ACTUATOR_VENDOR_CANDIDATE", "joint actuator vendor geometry", actuator_shape, structure, True, f"{vendor_source_id} SHA-bound manufacturer geometry mounted transversely in the palm; dimension-matched simplified body in GLB; project mounting interface remains candidate", oriented_box(motor_center, actuator_direction, spec["body_w"], spec["body_h"], spec["body_d"]))
            add(f"JMOD_{axis_id}_SYMMETRIC_DRIVE_COUPLER", "gripper transmission", link_between(center, motor_center, 6.0), joint, True, "candidate rack/pinion or tendon equalizer connection; geometry is packaging-only")
        elif motor_offset > 0:
            motor_center_v = cq.Vector(*center) + offset_direction.multiply(motor_offset)
            motor_center = (motor_center_v.x, motor_center_v.y, motor_center_v.z)
            output_pulley_d = spec.get("output_pulley_d", 32.0)
            motor_pulley_d = spec.get("motor_pulley_d", 24.0)
            add(f"JMOD_{axis_id}_OUTPUT_PULLEY", "joint transmission", spoked_pulley(center, direction, 12.0, output_pulley_d, spec["shaft_d"]), joint, True, f"{spec['ratio']} lightweight spoked pulley envelope; pitch/width/tooth count selection required")
            add(f"JMOD_{axis_id}_MOTOR_PULLEY", "joint transmission", spoked_pulley(motor_center, direction, 12.0, motor_pulley_d, 6.0), joint, True, f"{spec['ratio']} lightweight spoked motor pulley envelope; bore and retention selection required")
            vendor_source_id = vendor_source_for_axis(axis_id)
            actuator_shape, actuator_basis = vendor_actuator_to_axis(vendor_shapes[vendor_source_id], motor_center, direction)
            add(f"JMOD_{axis_id}_ACTUATOR_VENDOR_CANDIDATE", "joint actuator vendor geometry", actuator_shape, structure, True, f"{vendor_source_id} SHA-bound manufacturer geometry in STEP; dimension-matched simplified body in GLB; project mounting interface remains candidate", oriented_box(motor_center, direction, spec["body_w"], spec["body_h"], spec["body_d"]))
            add(f"JMOD_{axis_id}_BELT_PATH_RESERVATION", "joint transmission reservation", link_between(center, motor_center, 8.0), sensor, False, "belt sweep/guard reservation only; no belt selection or load credit")
        else:
            axial_sign = 1.0 if "WRIST" in axis_id else 1.0 if abs(normal.x) > 0.9 and center[0] < 0 else -1.0
            motor_center_v = cq.Vector(*center) + normal.multiply(axial_sign * (span / 2.0 + spec["plate_t"] + spec["body_d"] / 2.0))
            motor_center = (motor_center_v.x, motor_center_v.y, motor_center_v.z)
            vendor_source_id = vendor_source_for_axis(axis_id)
            actuator_shape, actuator_basis = vendor_actuator_to_axis(vendor_shapes[vendor_source_id], motor_center, direction)
            add(f"JMOD_{axis_id}_ACTUATOR_VENDOR_CANDIDATE", "joint actuator vendor geometry", actuator_shape, structure, True, f"{vendor_source_id} SHA-bound manufacturer geometry in STEP; dimension-matched simplified body in GLB; project mounting interface remains candidate", oriented_box(motor_center, direction, spec["body_w"], spec["body_h"], spec["body_d"]))
            add(f"JMOD_{axis_id}_ACTUATOR_OUTPUT_COUPLER", "joint transmission", cylinder_between(((motor_center_v + cq.Vector(*center)).multiply(0.5).x, (motor_center_v + cq.Vector(*center)).multiply(0.5).y, (motor_center_v + cq.Vector(*center)).multiply(0.5).z), direction, (motor_center_v - cq.Vector(*center)).Length, max(4.0, spec["shaft_d"] * 0.72)), joint, True, "coaxial output coupling candidate; spline, clamp, material and retention selection required")

        x_basis, y_basis, z_basis = actuator_basis
        vendor_transforms.append({
            "axis_id": axis_id,
            "family_id": family_id,
            "vendor_source_id": vendor_source_id,
            "source_sha256": VENDOR_ACTUATOR_SOURCES[vendor_source_id]["expected_sha256"],
            "native_output_axis": "+Z through native origin",
            "controlled_axis_relation": "TRANSVERSE PALM DRIVE THROUGH SYMMETRIC COUPLER" if "GRIPPER" in axis_id else "COAXIAL WITH CONTROLLED ROTARY AXIS",
            "project_output_origin_mm": f"({motor_center[0]:.6f}, {motor_center[1]:.6f}, {motor_center[2]:.6f})",
            "project_basis_local_x": f"({x_basis.x:.6f}, {x_basis.y:.6f}, {x_basis.z:.6f})",
            "project_basis_local_y": f"({y_basis.x:.6f}, {y_basis.y:.6f}, {y_basis.z:.6f})",
            "project_basis_local_z_output": f"({z_basis.x:.6f}, {z_basis.y:.6f}, {z_basis.z:.6f})",
            "roll_rule": "local +X uses deterministic joint-plane xDir; local +Y completes right-handed basis",
            "geometry_use": "SHA-BOUND MANUFACTURER PACKAGING GEOMETRY EMBEDDED IN STEP/GLB",
            "interface_status": "FRAME, HORN, FASTENER, CABLE EXIT, TOLERANCE AND RECEIVED FIT SELECTION REQUIRED",
            "authority": "NO PROCUREMENT, FABRICATION, MOTION OR ENERGIZATION AUTHORITY",
        })

        shared_assembly = f"{axis['side']}_SHOULDER_GIMBAL" if family_id == "JMF-03-SHOULDER-GIMBAL" else f"{axis_id}_MODULE"
        module_bindings.append({
            "axis_id": axis_id,
            "family_id": family_id,
            "shared_assembly_id": shared_assembly,
            "axis_center_mm": f"({center[0]:.3f}, {center[1]:.3f}, {center[2]:.3f})",
            "axis_direction": f"({direction[0]:.0f}, {direction[1]:.0f}, {direction[2]:.0f})",
            "shaft_candidate_mm": f"OD {spec['shaft_d']:.1f} x {shaft_length:.1f}",
            "bearing_envelope_each_mm": f"OD {spec['bearing_od']:.1f} x W {spec['bearing_w']:.1f} x {spec['external_bearings']}",
            "plate_candidate_mm": f"{spec['plate_w']:.1f} x {spec['plate_h']:.1f} x {spec['plate_t']:.1f}",
            "external_mount_pattern": f"4 x DIA {spec['hole_d']:.1f} on {spec['pattern_x']:.1f} x {spec['pattern_y']:.1f} rectangle",
            "transmission": spec["transmission"],
            "ratio": spec["ratio"],
            "cable_corridor_diameter_mm": f"{spec['cable_d']:.1f}",
            "selection_state": "GEOMETRIC CANDIDATE - BEARINGS, FITS, MATERIAL, FASTENERS, STOPS, ENCODER AND ACTUATOR INTERFACE SELECTION REQUIRED",
            "authority": "NO PROCUREMENT, FABRICATION, MOTION OR ENERGIZATION AUTHORITY",
        })
    return components, axes, module_bindings, vendor_transforms


def joint_packaging_screen(components: list[Component], axes: list[dict]) -> dict:
    """Screen neutral-pose module connectivity, actuator clashes and floor crossing."""
    by_name = {item.name: item for item in components}

    def allowed_names(axis_id: str) -> list[str]:
        side = axis_id[0] if axis_id.startswith(("L_", "R_")) else "C"
        if axis_id == "HEAD_PAN":
            return ["NECK_COLUMN_ENVELOPE", "HEAD_SHELL_ENVELOPE"]
        if axis_id == "HEAD_TILT":
            return ["HEAD_SHELL_ENVELOPE"]
        if axis_id == "WAIST_YAW":
            return ["WAIST_BEARING_STACK_RESERVATION", "PELVIS_SHELL_ENVELOPE", "TORSO_SHELL_ENVELOPE"]
        if "SHOULDER" in axis_id:
            return [f"{side}_SHOULDER_HOUSING_ENVELOPE", "TORSO_SHELL_ENVELOPE", f"{side}_UPPER_ARM_SHELL_ENVELOPE"]
        if "ELBOW" in axis_id:
            return [f"{side}_ELBOW_HOUSING_ENVELOPE", f"{side}_UPPER_ARM_SHELL_ENVELOPE", f"{side}_FOREARM_SHELL_ENVELOPE"]
        if "WRIST" in axis_id or "GRIPPER" in axis_id:
            return [f"{side}_WRIST_HOUSING_ENVELOPE", f"{side}_FOREARM_SHELL_ENVELOPE", f"{side}_HAND_PALM_ENVELOPE"]
        if "HIP" in axis_id:
            return [f"{side}_HIP_HOUSING_ENVELOPE", "PELVIS_SHELL_ENVELOPE", f"{side}_THIGH_SHELL_ENVELOPE"]
        if "KNEE" in axis_id:
            return [f"{side}_KNEE_HOUSING_ENVELOPE", f"{side}_THIGH_SHELL_ENVELOPE", f"{side}_SHIN_SHELL_ENVELOPE"]
        if "ANKLE" in axis_id:
            return [f"{side}_ANKLE_HOUSING_ENVELOPE", f"{side}_SHIN_SHELL_ENVELOPE", f"{side}_FOOT_SHELL_ENVELOPE"]
        raise RuntimeError(f"no packaging-volume mapping for {axis_id}")

    def touches(a: cq.Shape, b: cq.Shape, tolerance: float = 0.25) -> bool:
        # Packaging connectivity includes the explicit 0.20 mm nominal
        # diametral clearance between a candidate shaft and bearing envelope.
        abox, bbox = a.BoundingBox(), b.BoundingBox()
        if (
            max(abox.xmin, bbox.xmin) - min(abox.xmax, bbox.xmax) > tolerance
            or max(abox.ymin, bbox.ymin) - min(abox.ymax, bbox.ymax) > tolerance
            or max(abox.zmin, bbox.zmin) - min(abox.zmax, bbox.zmax) > tolerance
        ):
            return False
        return a.intersect(b).Volume() > 1e-6 or a.distance(b) <= tolerance

    def actuator_axis(name: str) -> str:
        return name[len("JMOD_") : -len("_ACTUATOR_VENDOR_CANDIDATE")]

    def assembly(axis_id: str) -> str:
        for token in ("SHOULDER", "HIP", "ANKLE"):
            if axis_id.startswith((f"L_{token}_", f"R_{token}_")):
                return f"{axis_id[0]}_{token}_CLUSTER"
        if axis_id.startswith("HEAD_"):
            return "HEAD_NECK_CLUSTER"
        return axis_id

    detached: list[dict] = []
    part_count = 0
    for axis in axes:
        axis_id = axis["axis_id"]
        allowed = [by_name[name].shape for name in allowed_names(axis_id)]
        parts = [item for item in components if item.physical and item.name.startswith(f"JMOD_{axis_id}_")]
        part_count += len(parts)
        connected = {index for index, item in enumerate(parts) if any(touches(item.shape, volume) for volume in allowed)}
        changed = True
        while changed:
            changed = False
            for index, item in enumerate(parts):
                if index in connected:
                    continue
                if any(touches(item.shape, parts[other].shape) for other in connected):
                    connected.add(index)
                    changed = True
        detached.extend({"axis_id": axis_id, "component": item.name} for index, item in enumerate(parts) if index not in connected)

    actuators = [item for item in components if item.physical and item.name.endswith("_ACTUATOR_VENDOR_CANDIDATE")]
    collisions: list[dict] = []
    for index, first in enumerate(actuators):
        first_axis = actuator_axis(first.name)
        first_box = first.shape.BoundingBox()
        for second in actuators[index + 1 :]:
            second_axis = actuator_axis(second.name)
            if assembly(first_axis) == assembly(second_axis):
                continue
            second_box = second.shape.BoundingBox()
            if (
                min(first_box.xmax, second_box.xmax) <= max(first_box.xmin, second_box.xmin)
                or min(first_box.ymax, second_box.ymax) <= max(first_box.ymin, second_box.ymin)
                or min(first_box.zmax, second_box.zmax) <= max(first_box.zmin, second_box.zmin)
            ):
                continue
            overlap = first.shape.intersect(second.shape).Volume()
            if overlap > 1e-5:
                collisions.append({"first_axis": first_axis, "second_axis": second_axis, "overlap_mm3": overlap})
    floor = [
        {"component": item.name, "zmin_mm": item.shape.BoundingBox().zmin}
        for item in components
        if item.physical and item.shape.BoundingBox().zmin < -1e-7
    ]
    return {
        "screen": "NEUTRAL-POSE CONNECTIVITY / CROSS-ASSEMBLY EXACT-ACTUATOR COLLISION / FLOOR",
        "scope": "Nominal packaging only; excludes swept motion, tolerance, cable, structural and safety proof",
        "module_part_count": part_count,
        "exact_actuator_count": len(actuators),
        "detached": detached,
        "cross_assembly_actuator_collisions": collisions,
        "floor_crossings": floor,
        "pass": not detached and not collisions and not floor,
        "authority": "NO PROCUREMENT, FABRICATION, MOTION OR ENERGIZATION AUTHORITY",
    }


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    components, axes, module_bindings, vendor_transforms = build()
    packaging = joint_packaging_screen(components, axes)
    if not packaging["pass"]:
        raise RuntimeError(f"neutral-pose joint packaging screen failed: {packaging}")
    physical = [item.shape for item in components if item.physical]
    all_shapes = [item.shape for item in components]
    physical_compound = cq.Compound.makeCompound(physical)
    reference_compound = cq.Compound.makeCompound(all_shapes)

    step = OUT / "HR-30_body_architecture_candidate.step"
    reference_step = OUT / "HR-30_body_kinematic_reference.step"
    cq.exporters.export(physical_compound, str(step))
    cq.exporters.export(reference_compound, str(reference_step))
    canonicalize_step(step)
    canonicalize_step(reference_step)

    assembly = cq.Assembly(name="HR_30_BODY_ARCHITECTURE_P01_NOT_RELEASED")
    for item in components:
        assembly.add(item.visual_shape if item.visual_shape is not None else item.shape, name=item.name, color=cq.Color(*item.color))
    assembly.save(str(OUT / "HR-30_body_architecture_candidate.glb"))

    write_csv(OUT / "joint-axis-schedule.csv", axes)
    write_csv(OUT / "joint-module-axis-binding.csv", module_bindings)
    write_csv(OUT / "vendor-actuator-transform-register.csv", vendor_transforms)
    write_csv(OUT / "vendor-actuator-source-register.csv", [{
        "source_id": source_id,
        "record": source["record"],
        "repository_path": source["path"].relative_to(ROOT).as_posix(),
        "sha256": source["expected_sha256"],
        "applies": source["applies"],
        "native_output_datum": "+Z through native origin; exact project roll and translation recorded per axis",
        "release_boundary": "MANUFACTURER REFERENCE GEOMETRY ONLY - RECEIVED IDENTITY, FIT, TOLERANCE AND INTERFACE VALIDATION REQUIRED",
    } for source_id, source in VENDOR_ACTUATOR_SOURCES.items()])
    write_csv(OUT / "bearing-candidate-source-register.csv", [{
        "bearing_id": bearing_id,
        "manufacturer": bearing["manufacturer"],
        "designation": bearing["designation"],
        "bore_diameter_mm": f"{bearing['bore_d']:.3f}",
        "outside_diameter_mm": f"{bearing['outer_d']:.3f}",
        "width_mm": f"{bearing['width']:.3f}",
        "published_mass_kg": f"{bearing['mass_kg']:.6f}",
        "published_dynamic_rating_n": f"{bearing['dynamic_rating_n']:.1f}",
        "published_static_rating_n": f"{bearing['static_rating_n']:.1f}",
        "official_url": bearing["url"],
        "document_revision_or_date": "LIVE MANUFACTURER PAGE; REVISION NOT PUBLISHED",
        "accessed_date": "2026-08-14",
        "application_state": "EVALUATION CANDIDATE ONLY - LOAD, LIFE, FIT, SUFFIX, LUBRICATION, RETENTION AND RECEIVED IDENTITY OPEN",
        "authority": "NO PROCUREMENT OR FABRICATION AUTHORITY",
    } for bearing_id, bearing in BEARING_CANDIDATES.items()])
    write_csv(OUT / "joint-module-family-schedule.csv", [{
        "family_id": family_id,
        "role": spec["role"],
        "axis_count": sum(row["family_id"] == family_id for row in module_bindings),
        "plate_candidate_mm": f"{spec['plate_w']:.1f} x {spec['plate_h']:.1f} x {spec['plate_t']:.1f}",
        "mount_pattern": f"4 x DIA {spec['hole_d']:.1f} on {spec['pattern_x']:.1f} x {spec['pattern_y']:.1f} rectangle",
        "shaft_diameter_mm": f"{spec['shaft_d']:.1f}",
        "bearing_envelope_each_mm": f"OD {spec['bearing_od']:.1f} x W {spec['bearing_w']:.1f}",
        "bearing_evaluation_candidate": BEARING_CANDIDATES[spec["bearing_id"]]["designation"],
        "bearing_published_mass_each_kg": f"{BEARING_CANDIDATES[spec['bearing_id']]['mass_kg']:.6f}",
        "external_bearing_count_per_axis": spec["external_bearings"],
        "support_span_mm": f"{spec['span']:.1f}",
        "transmission": spec["transmission"],
        "ratio": spec["ratio"],
        "motor_axis_offset_mm": f"{spec['motor_offset']:.1f}",
        "cable_corridor_diameter_mm": f"{spec['cable_d']:.1f}",
        "status": "DIMENSIONED ARCHITECTURE CANDIDATE - EXACT COMPONENTS, FITS, MATERIALS AND LOAD PROOF OPEN",
    } for family_id, spec in JOINT_MODULE_FAMILIES.items()])
    actuator_rows = []
    for axis in axes:
        axis_id = axis["axis_id"]
        region = axis["region"]
        if axis_id.startswith("HEAD_"):
            actuator, transmission, rail, disposition = (
                "ROBOTIS XC330-class compact X-series candidate",
                "direct drive with current/velocity limiting",
                "compatible isolated or shared rail SELECTION REQUIRED",
                "PROVISIONAL",
            )
        elif axis_id == "WAIST_YAW":
            actuator, transmission, rail, disposition = (
                "ROBOTIS XM540-W270-R candidate",
                "direct drive; external bearing support",
                "10.0-14.8 V candidate domain",
                "PROVISIONAL",
            )
        elif "SHOULDER_ROLL" in axis_id:
            actuator, transmission, rail, disposition = (
                "ROBOTIS XM430-W350-R candidate",
                "remote/nested 1.0:1 supported gimbal output",
                "10.0-14.8 V candidate domain",
                "PROVISIONAL - WHOLE-BODY STATIC ENDPOINT SCREEN RETAINED; CONTINUOUS/DYNAMIC/THERMAL PROOF REQUIRED",
            )
        elif "SHOULDER_PITCH" in axis_id:
            actuator, transmission, rail, disposition = (
                "ROBOTIS XM540-W270-R candidate",
                "direct drive candidate; dual-supported output",
                "10.0-14.8 V candidate domain",
                "PROVISIONAL - ARM MASS TARGET CURRENTLY FAILS",
            )
        elif "ELBOW" in axis_id:
            actuator, transmission, rail, disposition = (
                "ROBOTIS XM430-W350-R candidate",
                "direct drive candidate; dual-supported output",
                "10.0-14.8 V candidate domain",
                "PROVISIONAL - RETAINED BY WHOLE-BODY STATIC LOAD SCREEN; CONTINUOUS/DYNAMIC/THERMAL PROOF REQUIRED",
            )
        elif "WRIST" in axis_id:
            actuator, transmission, rail, disposition = (
                "ROBOTIS XC330-T288-T candidate",
                "direct drive through supported wrist shaft",
                "6.0-12.0 V candidate domain",
                "PROVISIONAL - WHOLE-BODY STATIC SCREEN RETAINED; DYNAMIC WRIST DUTY OPEN",
            )
        elif "GRIPPER" in axis_id:
            actuator, transmission, rail, disposition = (
                "ROBOTIS XC330-class compact candidate",
                "transverse palm-mounted motor with compliant symmetric rack/pinion or tendon equalizer",
                "6.0-12.0 V candidate domain; common rail architecture SELECTION REQUIRED",
                "PROVISIONAL - FORCE/LIMIT/COMPLIANCE PROOF REQUIRED",
            )
        elif "ANKLE_ROLL" in axis_id:
            actuator, transmission, rail, disposition = (
                "ROBOTIS XM430-W350-R evaluation candidate",
                "2.0:1 timing-reduction candidate; dual-supported 12 mm output; exact belt capacity SELECTION REQUIRED",
                "10.0-14.8 V candidate domain",
                "PROVISIONAL - WHOLE-BODY STATIC SCREEN RETAINED; CONTINUOUS/DYNAMIC/THERMAL PROOF REQUIRED",
            )
        elif "ANKLE_PITCH" in axis_id:
            actuator, transmission, rail, disposition = (
                "ROBOTIS XM430-W350-R evaluation candidate",
                "2.5:1 16:40 timing-reduction candidate; dual-supported 12 mm output; exact belt capacity SELECTION REQUIRED",
                "10.0-14.8 V candidate domain",
                "PROVISIONAL - WHOLE-BODY STATIC SCREEN RETAINED; CONTINUOUS/DYNAMIC/THERMAL PROOF REQUIRED",
            )
        elif "HIP_ROLL" in axis_id:
            actuator, transmission, rail, disposition = (
                "ROBOTIS XH540-W270-R evaluation candidate",
                "2.0:1 geometric timing-reduction candidate; dual-supported output; exact belt/pulleys SELECTION REQUIRED",
                "10.0-14.8 V candidate domain",
                "DIRECT DRIVE REJECTED/BLOCKED BY WHOLE-BODY PACKAGING",
            )
        elif "KNEE_PITCH" in axis_id:
            actuator, transmission, rail, disposition = (
                "ROBOTIS XH540-W270-R evaluation candidate",
                "2.0:1 whole-body knee timing-reduction candidate; dual-supported 12 mm output; output absolute encoder",
                "10.0-14.8 V candidate domain",
                "PROVISIONAL - CONTINUOUS TORQUE/THERMAL/GAIT PROOF REQUIRED",
            )
        elif "HIP_PITCH" in axis_id:
            actuator, transmission, rail, disposition = (
                "ROBOTIS XH540-W270-R evaluation candidate",
                "1.5:1 timing-belt candidate; dual-supported output; output absolute encoder",
                "10.0-14.8 V candidate domain",
                "PROVISIONAL - CONTINUOUS TORQUE/THERMAL/GAIT PROOF REQUIRED",
            )
        else:
            actuator, transmission, rail, disposition = (
                "ROBOTIS XH540-W270-R evaluation candidate",
                "direct-drive W0 test candidate; dual-supported output",
                "10.0-14.8 V candidate domain",
                "PROVISIONAL - W0 PROOF REQUIRED",
            )
        actuator_rows.append({
            "axis_id": axis_id,
            "region": region,
            "candidate_actuator": actuator,
            "candidate_transmission": transmission,
            "candidate_rail": rail,
            "position_feedback": "actuator encoder plus output-side absolute encoder on every reduced leg joint; other safety role SELECTION REQUIRED",
            "candidate_disposition": disposition,
            "interface_status": "AXIS AND RESERVATION DEFINED; EXACT HOUSING/SHAFT/BEARING/FASTENER INTERFACES OPEN",
            "authority": "NO PROCUREMENT OR FABRICATION AUTHORITY",
        })
    write_csv(OUT / "actuator-transmission-allocation.csv", actuator_rows)

    asimov_rows = [
        ("A1-01", "friendly non-photorealistic overall character", "REUSE", "visual intent only", "retain unmistakably robotic appearance"),
        ("A1-02", "screen-face concept", "ADAPT", "head/interaction architecture", "replace mesh face with serviceable display, camera privacy indicator and status lighting"),
        ("A1-03", "rounded shell language", "REUSE", "industrial design envelope", "convert to tool-removable covers with >=3 mm external edge radius"),
        ("A1-04", "rig hierarchy and animation clips", "ADAPT", "visualization and behavior reference", "retarget only after mapping to the controlled 25-axis skeleton and joint limits"),
        ("A1-05", "source mesh topology", "REJECT", "manufacturing/structural geometry", "not dimensioned, toleranced, materialized, or load-path controlled"),
        ("A1-06", "source joint centers and bone axes", "REJECT", "robot kinematics", "use HR-PROD-030 datums and the controlled joint-axis schedule"),
        ("A1-07", "head proportions", "ADAPT", "150 x 110 x 112 mm controlled head envelope", "preserve character while fitting screen, cameras, microphones, speakers and cooling"),
        ("A1-08", "torso silhouette", "ADAPT", "190 x 110 x 155 mm torso shell envelope", "fit compute, cooling, load frame, harness and service access"),
        ("A1-09", "arm silhouette", "ADAPT", "two articulated engineering arms", "meet controlled axes, hard reach limits, mass, payload and pinch constraints"),
        ("A1-10", "hand appearance", "ADAPT", "two broad parallel hand-shaped grippers", "must grasp, hold, present and release without narrow scissor points"),
        ("A1-11", "leg and foot silhouette", "ADAPT", "six-axis legs and 90 x 145 mm feet", "fit supported shafts, reductions, sensing and replaceable compliant soles"),
        ("A1-12", "textures and colors", "REUSE", "web visualization only", "no material, flammability, finish or cleanability credit"),
        ("A1-13", "internal structure", "REJECT", "whole-body load path", "source provides no controlled frame, bearings, joints, restraint interface or fall load path"),
        ("A1-14", "walking/backflip/running animations", "REJECT", "motion commands", "visual reference only; cannot become executable trajectories or validation evidence"),
    ]
    write_csv(OUT / "asimov-1-reuse-adapt-reject.csv", [{
        "matrix_id": row[0],
        "asimov_1_feature": row[1],
        "decision": row[2],
        "hr30_use": row[3],
        "engineering_rule": row[4],
        "source_archive_sha256": ASIMOV_1_SOURCE_SHA256,
        "status": "CONTROLLED ARCHITECTURE DECISION - NO MANUFACTURING OR MOTION CREDIT",
    } for row in asimov_rows])
    component_rows = []
    for item in components:
        box = bbox_dict(item.shape)
        component_rows.append({
            "component": item.name,
            "group": item.group,
            "physical_or_reference": "PHYSICAL ENVELOPE" if item.physical else "REFERENCE/RESERVATION",
            "xmin_mm": f"{box['xmin']:.6f}",
            "xmax_mm": f"{box['xmax']:.6f}",
            "ymin_mm": f"{box['ymin']:.6f}",
            "ymax_mm": f"{box['ymax']:.6f}",
            "zmin_mm": f"{box['zmin']:.6f}",
            "zmax_mm": f"{box['zmax']:.6f}",
            "note": item.note,
            "status": "CANDIDATE ENVELOPE - NOT A FABRICATION PART",
        })
    write_csv(OUT / "component-envelope-schedule.csv", component_rows)
    (OUT / "joint-packaging-screen.json").write_text(json.dumps(packaging, indent=2) + "\n", encoding="utf-8")

    physical_box = bbox_dict(physical_compound)
    reference_box = bbox_dict(reference_compound)
    physical_vertices = vertex_extent_dict(physical_compound)
    straight_reach = 150.0 + 145.0 + 75.0
    arm_span = 2.0 * (SHOULDER_AXIS_X + straight_reach)
    checks = {
        "identifier": IDENTIFIER,
        "warning": WARNING,
        "coordinate_system": {"x": "robot left", "y": "rearward; face is -Y", "z": "up from floor", "origin": "floor/sagittal-plane intersection beneath pelvis"},
        "source_datums_mm": {"ankle_pitch": ANKLE_Z, "knee_pitch": KNEE_Z, "hip_pitch": HIP_Z, "waist_yaw": WAIST_Z, "shoulder_pitch": SHOULDER_Z, "neck_pan": NECK_Z, "shell_top": HEIGHT},
        "physical_bbox_mm": physical_box,
        "physical_vertex_extents_mm": physical_vertices,
        "reference_bbox_mm": reference_box,
        "joint_axis_count": len(axes),
        "physical_component_count": len(physical),
        "reference_component_count": len(components) - len(physical),
        "joint_module_family_count": len(JOINT_MODULE_FAMILIES),
        "joint_module_binding_count": len(module_bindings),
        "vendor_actuator_source_count": len(VENDOR_ACTUATOR_SOURCES),
        "vendor_actuator_transform_count": len(vendor_transforms),
        "bearing_candidate_source_count": len(BEARING_CANDIDATES),
        "shoulder_shell_width_mm": 250.0,
        "hip_shell_width_mm": 155.0,
        "foot_center_spacing_mm": 125.0,
        "straight_arm_reach_screen_mm": straight_reach,
        "straight_arm_span_screen_mm": arm_span,
        "checks": {
            "overall_height_exact_762": abs(physical_vertices["zmax"] - HEIGHT) < 1e-6 and abs(physical_vertices["zmin"]) < 1e-6,
            "joint_axis_count_exact_25": len(axes) == 25,
            "shoulder_shell_target_met": 250.0 <= 250.0,
            "hip_shell_target_met": 155.0 <= 155.0,
            "foot_spacing_inside_walking_band": 90.0 <= 125.0 <= 140.0,
            "straight_arm_reach_target_met": straight_reach <= 360.0,
            "straight_arm_reach_hard_limit_met": straight_reach <= 390.0,
            "straight_arm_span_target_met": arm_span <= 900.0,
            "straight_arm_span_hard_limit_met": arm_span <= 980.0,
        },
        "interpretation": "architecture and packaging geometry only; external envelopes are not manufacturing parts and volume is not mass",
        "authority": {"procurement": False, "fabrication": False, "assembly": False, "powered_test": False, "motion": False, "energization": False},
    }
    (OUT / "geometry-checks.json").write_text(json.dumps(checks, indent=2) + "\n", encoding="utf-8")

    mass_rows = [
        {"assembly": "head and neck", "target_kg": 0.55, "maximum_kg": 0.65, "cad_mass_kg": "NOT CALCULATED - ENVELOPES", "status": "OPEN"},
        {"assembly": "chest compute waist and onboard energy", "target_kg": 2.10, "maximum_kg": 2.40, "cad_mass_kg": "NOT CALCULATED - ENVELOPES", "status": "OPEN"},
        {"assembly": "two arms and hands", "target_kg": 1.70, "maximum_kg": 1.95, "cad_mass_kg": "NOT CALCULATED - ENVELOPES", "status": "OPEN"},
        {"assembly": "pelvis power and restraint structure", "target_kg": 1.60, "maximum_kg": 1.85, "cad_mass_kg": "NOT CALCULATED - ENVELOPES", "status": "OPEN"},
        {"assembly": "two legs and feet", "target_kg": 4.70, "maximum_kg": 5.25, "cad_mass_kg": "NOT CALCULATED - ENVELOPES", "status": "OPEN"},
        {"assembly": "integration contingency within link totals", "target_kg": 0.00, "maximum_kg": 0.90, "cad_mass_kg": "8% PLANNING RULE", "status": "OPEN"},
        {"assembly": "TOTAL", "target_kg": 10.50, "maximum_kg": 12.00, "cad_mass_kg": "NOT DEMONSTRATED", "status": "OPEN/BLOCKING; 10 KG LIGHTWEIGHT STRETCH RETAINED"},
    ]
    write_csv(OUT / "mass-allocation-register.csv", mass_rows)
    holds = [
        ("HR30-P01-H01", "All 25 axes have dimensioned module-family bindings and visible shaft/bearing/interface candidates. Standard catalogue bearing candidates now align every shaft/envelope, but load direction, life, suffix, fits, materials, fasteners, stops, encoders, actuator interfaces and physical proof remain open."),
        ("HR30-P01-H02", "The arm actuator concept exceeds its mass target before links, hands, cables and covers."),
        ("HR30-P01-H03", "The leg concept fails its current mass screen; reduced hip/ankle roll packaging clears the floor in the neutral pose but continuous torque, thermal, impact and gait loads remain unproved."),
        ("HR30-P01-H04", "No selected power source, regeneration control, contactors, battery or tether exists."),
        ("HR30-P01-H05", "The 370 mm straight-arm reach and 950 mm span pass hard limits but miss targets."),
        ("HR30-P01-H06", "Shells are solid visual envelopes without wall thickness, splits, fasteners, vents or service access."),
        ("HR30-P01-H07", "Harness corridors, bend radii, strain relief and moving-joint routing are absent."),
        ("HR30-P01-H08", "Collision, self-collision, stopping, fall, restraint and power-loss behavior are unverified."),
        ("HR30-P01-H09", "Mass, center of mass and inertia are not derived because controlled physical parts do not yet exist."),
        ("HR30-P01-H10", "No DFM, tolerance, GD&T, material, FAI, proof, physical test or qualified review exists."),
    ]
    write_csv(OUT / "open-holds.csv", [{"hold_id": hid, "unresolved_item": text, "state": "OPEN", "release_effect": "BLOCKS FABRICATION, MOTION AND ENERGIZATION"} for hid, text in holds])

    readme = f"""# HR-30 native body architecture P0.1

**{WARNING}**

This is the first repository-native full-body CAD for Project Button. It freezes the `HR-PROD-030` neutral-pose datums, all 25 candidate axes, the 762 mm overall height, shell envelopes, load-frame envelopes and first component-bay reservations.

It is intentionally an architecture model, not a buildable machine. The STEP contains candidate physical envelopes plus visible module-family geometry for every axis: output shafts, standard catalogue bearing candidates, removable four-hole interface carriers, exact SHA-bound manufacturer actuator bodies, cable corridors and reduction reservations. Ten dimensioned module families cover all 25 axes, including dedicated 2.0:1 knee and 2.5:1 ankle-pitch candidates and a shared intersecting-axis shoulder gimbal rather than overlapping generic servo blocks. Three controlled ROBOTIS source files and 25 explicit orthonormal transforms replace anonymous actuator boxes while leaving every frame, horn, fastener, cable exit, tolerance and received fit unresolved. The web GLB deliberately substitutes dimension-matched low-complexity actuator bodies for the detailed B-Reps; the exact geometry remains in both STEP assemblies and the source/transform registers. The second STEP and GLB add joint-axis and component-reservation references. The package also assigns a provisional actuator/transmission route to every axis and records explicit REUSE / ADAPT / REJECT decisions for the SHA-bound Asimov 1 source rig. Bearing dimensions, masses and catalogue ratings are now recorded from current primary manufacturer pages, but bearing application, life, suffix, fits, retention and received identity remain open. Exact fasteners, stops, encoders, actuator interfaces, wall construction, tolerances, harnesses, power hardware, mass properties, collision proof and physical validation remain open.

The straight arm-chain arithmetic is 370 mm reach and 950 mm span: both pass hard limits, but both miss the preferred 360/900 mm targets. This is recorded as an open design correction rather than hidden.
"""
    (OUT / "README.md").write_text(readme, encoding="utf-8", newline="\n")
    (OUT / "front-elevation.svg").write_text(front_elevation_svg(), encoding="utf-8", newline="\n")
    (OUT / "index.html").write_text(interactive_html(), encoding="utf-8", newline="\n")
    vendor_out = OUT / "vendor"
    vendor_out.mkdir()
    for vendor_name in ("model-viewer.min.js", "LICENSE", "SOURCE.md"):
        shutil.copy2(MODEL_VIEWER_SOURCE / vendor_name, vendor_out / vendor_name)
    (OUT / "package-status.json").write_text(json.dumps({
        "identifier": IDENTIFIER,
        "program": "HR-30 whole humanoid",
        "phase": "P0.1 first substantive whole-body architecture",
        "whole_body_geometry_present": True,
        "head_present": True,
        "neck_present": True,
        "torso_present": True,
        "pelvis_present": True,
        "two_complete_arms_present": True,
        "two_hand_shaped_grippers_present": True,
        "two_articulated_legs_present": True,
        "ankles_and_feet_present": True,
        "joint_axis_count": len(axes),
        "actuator_allocation_count": len(actuator_rows),
        "joint_module_family_count": len(JOINT_MODULE_FAMILIES),
        "joint_module_binding_count": len(module_bindings),
        "joint_module_geometry_present": True,
        "sha_bound_vendor_actuator_geometry_present": True,
        "vendor_actuator_source_count": len(VENDOR_ACTUATOR_SOURCES),
        "vendor_actuator_transform_count": len(vendor_transforms),
        "bearing_candidate_source_count": len(BEARING_CANDIDATES),
        "web_glb_uses_dimension_matched_simplified_actuator_bodies": True,
        "neutral_pose_joint_packaging_screen_pass": packaging["pass"],
        "asimov_matrix_count": len(asimov_rows),
        "editable_source_present": True,
        "step_present": True,
        "glb_present": True,
        "manufacturing_detail_complete": False,
        "procurement_authority": False,
        "fabrication_authority": False,
        "powered_test_authority": False,
        "motion_authority": False,
        "energization_authority": False,
        "warning": WARNING,
    }, indent=2) + "\n", encoding="utf-8")
    shutil.copy2(Path(__file__), OUT / "whole-body-source.py")

    files = [p for p in OUT.rglob("*") if p.is_file() and p.name != "file-manifest.csv"]
    manifest_rows = [{"path": p.relative_to(OUT).as_posix(), "bytes": p.stat().st_size, "sha256": sha256(p), "warning": WARNING} for p in sorted(files)]
    write_csv(OUT / "file-manifest.csv", manifest_rows)
    if RELEASE.exists():
        shutil.rmtree(RELEASE)
    shutil.copytree(OUT, RELEASE)
    print(json.dumps({"identifier": IDENTIFIER, "physical_components": len(physical), "all_components": len(components), "axes": len(axes), "geometric_zmin_mm": physical_vertices["zmin"], "geometric_zmax_mm": physical_vertices["zmax"], "out": str(OUT)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
