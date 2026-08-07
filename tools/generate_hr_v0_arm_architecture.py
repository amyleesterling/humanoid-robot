"""Generate the integrated exact-coordinate HR-V0 arm candidate for R67.

The exported geometry is a feasibility/configuration candidate.  It is not a
fabrication release.  Purchased 80/20 stock remains a conservative 20 x 40 mm
collision envelope, while the manufacturer-published end-tap coordinates,
ROBOTIS frame hole patterns, candidate countersunk fastener envelope and
vendor-coordinate actuator rotation are modeled explicitly.  Tolerances,
qualified acceptance, physical fit and proof requirements remain open.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
import shutil
from pathlib import Path

import cadquery as cq
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.gp import gp_Trsf


ROOT = Path(__file__).resolve().parents[1]
VENDOR = ROOT / "cad" / "vendor" / "robotis"
VENDOR_8020 = ROOT / "cad" / "vendor" / "8020"
OUT = ROOT / "cad" / "hr-v0" / "generated" / "arm-architecture-p0.6"
REVISION = "HR-V0-ARM-ARCH-P0.6"
WARNING = "PRELIMINARY - CANDIDATE GEOMETRY ONLY - NOT RELEASED FOR FABRICATION OR ENERGIZATION"

PLATE_T = 9.525
PLATE_MIN_T = 9.0
PLATE_MAX_T = 10.0
UPPER_BEAM_L = 100.0
FOREARM_BEAM_L = 50.0
J2_Y = round(32.0 + PLATE_T + UPPER_BEAM_L + PLATE_T + 51.5, 4)
G1_Y = round(J2_Y + 32.0 + PLATE_T + FOREARM_BEAM_L + PLATE_T + 28.0, 4)
FRAME_HOLE_D = 2.70
END_HOLE_D = 5.50
END_CSK_D = 11.40
END_CSK_D_NOM = 11.30
END_CSK_D_MIN = 9.43
END_CSK_DEPTH = 3.10
END_TAP_SPACING = 20.0
M5_SCREW_LENGTH = 20.0
M2_5_SCREW_LENGTH = 20.0
H101_LINK_FACE_T = 2.0
H101_LINK_FACE_MAX_T = 2.2
M2_5_NUT_T = 3.60
M2_5_NUT_MIN_T = 3.30
MATERIAL_PROJECT_MIN_YIELD_MPA = 240.0
FASTENER_A2_70_MIN_TENSILE_MPA = 700.0
PROOF_MULTIPLIER = 3.0
ACTUATOR_AXIAL_OFFSET_X = 1.75
COLLISION_INCREMENT_DEG = 0.5
CONTINUOUS_ANALYSIS_J2_MAX_DEG = 120.0
PROVISIONAL_J2_SOFT_LIMIT_DEG = 115.0
CANDIDATE_J2_POSITIVE_HARD_STOP_DEG = 118.0
CANDIDATE_CONTACT_GUARD_DEG = 1.0
CONTINUOUS_CERTIFIED_CLEARANCE_MM = 0.75
CONTINUOUS_NUMERIC_TOLERANCE_MM = 1e-6
CONTINUOUS_MIN_CELL_DEG = 1e-5
SUPPORT_PLATE_H = 80.0
SUPPORT_M8_SPACING = 60.0
SUPPORT_M8_HOLE_D = 8.50
J1_S102_FACE_Y = -51.5
COLUMN_FACE_Y = J1_S102_FACE_Y - PLATE_T
COLUMN_CENTER_Y = COLUMN_FACE_Y - 20.0
COLUMN_TOP_Z = 40.0
COLUMN_LENGTH = 500.0
J1_A0_X = -210.0
J1_A0_Y = round(-COLUMN_CENTER_Y, 4)
J1_A0_Z = 500.0
H104_SELECTED_AXES_LOCAL_XZ = ((-11.0, -8.0), (11.0, -8.0), (-12.0, 6.0), (12.0, 6.0))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def canonicalize_step(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = re.sub(
        r"(FILE_NAME\('Open CASCADE Shape Model',)'[^']*'",
        r"\1'1980-01-01T00:00:00'",
        text,
        count=1,
    )
    path.write_text("\n".join(line.rstrip() for line in text.splitlines()) + "\n", encoding="utf-8", newline="\n")


def import_step(name: str) -> cq.Shape:
    return cq.importers.importStep(str(VENDOR / name)).val()


def rotate_x(shape: cq.Shape, angle_deg: float, origin_y: float = 0.0) -> cq.Shape:
    return shape.rotate((0.0, origin_y, 0.0), (1.0, origin_y, 0.0), angle_deg)


def actuator_to_joint_frame(shape: cq.Shape) -> cq.Shape:
    """Map ROBOTIS actuator STEP coordinates into the FR13 joint frame.

    The proper rotation is fixed by two independent registrations:
    local actuator +Z (output axis) maps to joint -X, and the two bottom
    mounting axes at local (x=+/-13.5, y=-41.5) map exactly to the S102 axes
    at joint (y=+/-13.5, z=41.5).  The X translation only places the axial
    display envelope; received horn/idler stack measurement remains open.
    """
    transform = gp_Trsf()
    transform.SetValues(
        0.0, 0.0, -1.0, ACTUATOR_AXIAL_OFFSET_X,
        1.0, 0.0, 0.0, 0.0,
        0.0, -1.0, 0.0, 0.0,
    )
    return cq.Shape.cast(BRepBuilderAPI_Transform(shape.wrapped, transform, True).Shape())


def adapter(y0: float) -> cq.Shape:
    solid = cq.Solid.makeBox(48.0, PLATE_T, 40.0, cq.Vector(-24.0, y0, -20.0))
    # ROBOTIS's assembly precedent uses the rectangular +/-16 x +/-8 pattern,
    # not the PCD22 horn pattern incorrectly used in P0.1.
    for x in (-16.0, 16.0):
        for z in (-8.0, 8.0):
            hole = cq.Solid.makeCylinder(FRAME_HOLE_D / 2.0, PLATE_T, cq.Vector(x, y0, z), cq.Vector(0, 1, 0))
            solid = solid.cut(hole)
    # The purchased profile's published 4.19 mm cores lie on the 40 mm axis,
    # 20 mm apart.  A 90-degree countersink keeps the M5 candidate flush under
    # the ROBOTIS frame.  R56 increases the adapter from 4.7625 mm to nominal
    # 9.525 mm and sets a 9.0 mm finished minimum. R57 uses the maximum
    # controlled countersink envelope for the exact A2-70 Torx candidate;
    # material certification, inspection and physical proof remain gates.
    for z in (-10.0, 10.0):
        hole = cq.Solid.makeCylinder(END_HOLE_D / 2.0, PLATE_T, cq.Vector(0, y0, z), cq.Vector(0, 1, 0))
        solid = solid.cut(hole)
        countersink = cq.Solid.makeCone(
            END_CSK_D / 2.0,
            END_HOLE_D / 2.0,
            END_CSK_DEPTH,
            cq.Vector(0, y0, z),
            cq.Vector(0, 1, 0),
        )
        solid = solid.cut(countersink)
    return solid


def gripper_adapter(y0: float) -> cq.Shape:
    """Adapter using four exact FR12-H104K broad-face through-hole axes.

    The selected axes are read from the controlled manufacturer STEP.  After
    the H104 frame is rotated 180 degrees about X, local Z changes sign in the
    project frame.  The two M5 member-end holes retain the existing pattern.
    """

    solid = cq.Solid.makeBox(48.0, PLATE_T, 40.0, cq.Vector(-24.0, y0, -20.0))
    for x, local_z in H104_SELECTED_AXES_LOCAL_XZ:
        project_z = -local_z
        hole = cq.Solid.makeCylinder(
            FRAME_HOLE_D / 2.0, PLATE_T, cq.Vector(x, y0, project_z), cq.Vector(0, 1, 0)
        )
        solid = solid.cut(hole)
    for z in (-10.0, 10.0):
        hole = cq.Solid.makeCylinder(
            END_HOLE_D / 2.0, PLATE_T, cq.Vector(0, y0, z), cq.Vector(0, 1, 0)
        )
        solid = solid.cut(hole)
        countersink = cq.Solid.makeCone(
            END_CSK_D / 2.0,
            END_HOLE_D / 2.0,
            END_CSK_DEPTH,
            cq.Vector(0, y0, z),
            cq.Vector(0, 1, 0),
        )
        solid = solid.cut(countersink)
    return solid


def shoulder_support_plate() -> cq.Shape:
    """Side-slot plate joining the 40-4040 column to the rolled J1 S102."""

    solid = cq.Solid.makeBox(
        48.0,
        PLATE_T,
        SUPPORT_PLATE_H,
        cq.Vector(-24.0, COLUMN_FACE_Y, -SUPPORT_PLATE_H / 2.0),
    )
    for x in (-16.0, 16.0):
        for z in (-8.0, 8.0):
            hole = cq.Solid.makeCylinder(
                FRAME_HOLE_D / 2.0,
                PLATE_T,
                cq.Vector(x, COLUMN_FACE_Y, z),
                cq.Vector(0, 1, 0),
            )
            solid = solid.cut(hole)
    for z in (-SUPPORT_M8_SPACING / 2.0, SUPPORT_M8_SPACING / 2.0):
        hole = cq.Solid.makeCylinder(
            SUPPORT_M8_HOLE_D / 2.0,
            PLATE_T,
            cq.Vector(0, COLUMN_FACE_Y, z),
            cq.Vector(0, 1, 0),
        )
        solid = solid.cut(hole)
    return solid


def column_envelope() -> cq.Shape:
    return cq.Solid.makeBox(
        40.0,
        40.0,
        COLUMN_LENGTH,
        cq.Vector(-20.0, COLUMN_CENTER_Y - 20.0, COLUMN_TOP_Z - COLUMN_LENGTH),
    )


def cylindrical_axes(
    shape: cq.Shape,
    *,
    radius: float,
    axis: str,
) -> set[tuple[float, float]]:
    """Return unique transverse coordinates for exact cylindrical STEP faces."""

    result: set[tuple[float, float]] = set()
    for face in shape.Faces():
        if face.geomType() != "CYLINDER":
            continue
        cylinder = face._geomAdaptor().Cylinder()
        if not math.isclose(cylinder.Radius(), radius, abs_tol=1e-6):
            continue
        direction = cylinder.Axis().Direction()
        location = cylinder.Axis().Location()
        if axis == "Y" and abs(direction.Y()) > 0.999999:
            result.add((round(location.X(), 3), round(location.Z(), 3)))
        elif axis == "Z" and abs(direction.Z()) > 0.999999:
            result.add((round(location.X(), 3), round(location.Y(), 3)))
    return result


def beam(y0: float, length: float) -> cq.Shape:
    # The purchased section remains a conservative envelope.  The 40 mm axis is
    # vertical so the two end taps at z=+/-10 provide a torque-resisting couple
    # about the X joint axis; P0.1's horizontal orientation did not.
    return cq.Solid.makeBox(20.0, length, 40.0, cq.Vector(-10.0, y0, -20.0))


def matrix_x(angle_deg: float, tx: float, ty: float, tz: float) -> list[list[float]]:
    c = round(math.cos(math.radians(angle_deg)), 12)
    s = round(math.sin(math.radians(angle_deg)), 12)
    return [[1.0, 0.0, 0.0, tx], [0.0, c, -s, ty], [0.0, s, c, tz], [0.0, 0.0, 0.0, 1.0]]


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_adapter_dxf(path: Path) -> None:
    """Write a minimal ASCII DXF with separate finished-feature layers."""
    lines: list[str] = [
        "0", "SECTION", "2", "HEADER", "9", "$ACADVER", "1", "AC1009", "0", "ENDSEC",
        "0", "SECTION", "2", "ENTITIES",
    ]

    def line(x1: float, y1: float, x2: float, y2: float, layer: str) -> None:
        lines.extend(["0", "LINE", "8", layer, "10", str(x1), "20", str(y1), "30", "0", "11", str(x2), "21", str(y2), "31", "0"])

    def circle(x: float, y: float, radius: float, layer: str) -> None:
        lines.extend(["0", "CIRCLE", "8", layer, "10", str(x), "20", str(y), "30", "0", "40", str(radius)])

    for x1, z1, x2, z2 in ((-24, -20, 24, -20), (24, -20, 24, 20), (24, 20, -24, 20), (-24, 20, -24, -20)):
        line(x1, z1, x2, z2, "FINISHED_PROFILE")
    for x in (-16.0, 16.0):
        for z in (-8.0, 8.0):
            circle(x, z, FRAME_HOLE_D / 2.0, "M2_5_CLEARANCE")
    for z in (-10.0, 10.0):
        circle(0.0, z, END_HOLE_D / 2.0, "M5_CLEARANCE")
        circle(0.0, z, END_CSK_D_NOM / 2.0, "M5_COUNTERSINK_NOMINAL")
    lines.extend(["0", "ENDSEC", "0", "EOF"])
    path.write_text("\n".join(lines) + "\n", encoding="ascii", newline="\n")


def write_custom_plate_dxf(
    path: Path,
    *,
    width: float,
    height: float,
    small_holes: tuple[tuple[float, float], ...],
    large_holes: tuple[tuple[float, float], ...],
    countersunk_large: bool,
) -> None:
    lines: list[str] = [
        "0", "SECTION", "2", "HEADER", "9", "$ACADVER", "1", "AC1009", "0", "ENDSEC",
        "0", "SECTION", "2", "ENTITIES",
    ]

    def line(x1: float, y1: float, x2: float, y2: float, layer: str) -> None:
        lines.extend(["0", "LINE", "8", layer, "10", str(x1), "20", str(y1), "30", "0", "11", str(x2), "21", str(y2), "31", "0"])

    def circle(x: float, y: float, radius: float, layer: str) -> None:
        lines.extend(["0", "CIRCLE", "8", layer, "10", str(x), "20", str(y), "30", "0", "40", str(radius)])

    half_w = width / 2.0
    half_h = height / 2.0
    for x1, z1, x2, z2 in (
        (-half_w, -half_h, half_w, -half_h),
        (half_w, -half_h, half_w, half_h),
        (half_w, half_h, -half_w, half_h),
        (-half_w, half_h, -half_w, -half_h),
    ):
        line(x1, z1, x2, z2, "FINISHED_PROFILE")
    for x, z in small_holes:
        circle(x, z, FRAME_HOLE_D / 2.0, "M2_5_CLEARANCE")
    large_diameter = END_HOLE_D if countersunk_large else SUPPORT_M8_HOLE_D
    for x, z in large_holes:
        circle(x, z, large_diameter / 2.0, "M5_CLEARANCE" if countersunk_large else "M8_CLEARANCE")
        if countersunk_large:
            circle(x, z, END_CSK_D_NOM / 2.0, "M5_COUNTERSINK_NOMINAL")
    lines.extend(["0", "ENDSEC", "0", "EOF"])
    path.write_text("\n".join(lines) + "\n", encoding="ascii", newline="\n")


def write_interface_plate_drawing(
    path: Path,
    *,
    title: str,
    part_id: str,
    envelope: str,
    small_pattern: str,
    large_pattern: str,
    source_note: str,
    use_note: str,
) -> None:
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="950" viewBox="0 0 1600 950">
<style>text{{font-family:Arial,sans-serif;fill:#082b4c;font-size:18px}}.title{{font-size:34px;font-weight:700}}.head{{font-size:24px;font-weight:700}}.warn{{font-size:20px;font-weight:700;fill:#8a3b00}}.box{{fill:#f7fbff;stroke:#0b4f8a;stroke-width:3}}.note{{fill:#fff9e8;stroke:#d59600;stroke-width:3}}</style>
<rect width="1600" height="950" fill="#ffffff"/>
<text x="45" y="60" class="title">{title}</text>
<text x="45" y="100" class="warn">{part_id} / {REVISION} - {WARNING}</text>
<rect x="55" y="155" width="1490" height="290" rx="14" class="box"/>
<text x="90" y="205" class="head">Controlled candidate geometry</text>
<text x="90" y="250">Finished envelope: {envelope}; 6061-T651 plate from held OnlineMetals 1249 stock.</text>
<text x="90" y="292">Frame pattern: {small_pattern}</text>
<text x="90" y="334">Structural/member pattern: {large_pattern}</text>
<text x="90" y="376">All hole coordinates are basic to the part center; coordinate tolerance +/-0.05 mm.</text>
<text x="90" y="418">Hole diameters, thickness, flatness, parallelism, edge break and FAI controls are in the CSV schedule.</text>
<rect x="55" y="485" width="1490" height="300" rx="14" class="note"/>
<text x="90" y="540" class="head">Source and installation boundary</text>
<text x="90" y="585">{source_note}</text>
<text x="90" y="630">{use_note}</text>
<text x="90" y="675">Received-part fit, exact stack, installation torque, locking, tool access and proof remain required.</text>
<text x="90" y="720">Supplier DFM and one separately authorized first article precede any use on an assembly.</text>
<text x="90" y="765" class="warn">DO NOT FABRICATE, ASSEMBLE, CONNECT, OR ENERGIZE FROM THIS DRAWING ALONE.</text>
<text x="55" y="870">Units: mm | Projection: plate face X-Z | Date: 2026-08-07</text>
</svg>'''
    path.write_text(svg, encoding="utf-8", newline="\n")


def write_adapter_drawing(path: Path) -> None:
    sx = lambda value: 390 + value * 10
    sz = lambda value: 500 - value * 10
    holes = []
    for x in (-16.0, 16.0):
        for z in (-8.0, 8.0):
            holes.append(f'<circle cx="{sx(x)}" cy="{sz(z)}" r="13.5" class="hole"/><line x1="{sx(x)-18}" y1="{sz(z)}" x2="{sx(x)+18}" y2="{sz(z)}" class="center"/><line x1="{sx(x)}" y1="{sz(z)-18}" x2="{sx(x)}" y2="{sz(z)+18}" class="center"/>')
    for z in (-10.0, 10.0):
        holes.append(f'<circle cx="{sx(0)}" cy="{sz(z)}" r="27.5" class="hole"/><circle cx="{sx(0)}" cy="{sz(z)}" r="56.5" class="csk"/><line x1="{sx(0)-65}" y1="{sz(z)}" x2="{sx(0)+65}" y2="{sz(z)}" class="center"/>')
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1100" viewBox="0 0 1600 1100">
<style>text{{font-family:Arial,sans-serif;fill:#082b4c;font-size:18px}}.title{{font-size:34px;font-weight:700}}.head{{font-size:23px;font-weight:700}}.warn{{font-size:20px;font-weight:700;fill:#8a3b00}}.part{{fill:#d9f1ff;stroke:#0b4f8a;stroke-width:4}}.hole{{fill:#fff;stroke:#0b4f8a;stroke-width:3}}.csk{{fill:none;stroke:#d59600;stroke-width:3}}.center{{stroke:#657b8a;stroke-width:1.5;stroke-dasharray:8 5}}.dim{{stroke:#082b4c;stroke-width:2}}.box{{fill:#fff9e8;stroke:#d59600;stroke-width:3}}</style>
<rect width="1600" height="1100" fill="#f7fbff"/>
<text x="40" y="55" class="title">MV0-C01 arm adapter — controlled candidate drawing</text>
<text x="40" y="90" class="warn">{REVISION} — {WARNING}</text>
<rect x="150" y="300" width="480" height="400" class="part"/>
{''.join(holes)}
<line x1="150" y1="245" x2="630" y2="245" class="dim"/><line x1="150" y1="230" x2="150" y2="270" class="dim"/><line x1="630" y1="230" x2="630" y2="270" class="dim"/><text x="345" y="225" class="head">48.00 ±0.10</text>
<line x1="95" y1="300" x2="95" y2="700" class="dim"/><line x1="80" y1="300" x2="120" y2="300" class="dim"/><line x1="80" y1="700" x2="120" y2="700" class="dim"/><text x="35" y="520" class="head" transform="rotate(-90 35 520)">40.00 ±0.10</text>
<text x="175" y="755">4× Ø2.70 +0.10/−0.00 at X=±16.00, Z=±8.00; center coordinates ±0.05</text>
<text x="175" y="790">2× Ø5.50 +0.10/−0.00 at X=0, Z=±10.00; center coordinates ±0.05</text>
<text x="175" y="825">2× countersink Ø11.30 +0.10/−0.00, 90° included nominal; received screw functional gauge controls</text>
<rect x="760" y="150" width="790" height="780" rx="12" class="box"/>
<text x="800" y="205" class="head">Material and process</text>
<text x="800" y="245">6061‑T651 plate, ASTM B209 / AMS 4027, OnlineMetals part 1249 candidate.</text>
<text x="800" y="280">One 8×8×3/8 in sheet, one heat lot, MTR required. CNC mill/drill only.</text>
<text x="800" y="315">Finished thickness 9.00–10.00 mm; opposite broad faces parallel within 0.10 mm.</text>
<text x="800" y="350">Flatness ≤0.15 mm over the finished part. Bare as-machined; remove all burrs.</text>
<text x="800" y="385">Break sharp edges 0.20–0.50 mm. No anodize, plating, or unapproved substitution.</text>
<text x="800" y="440" class="head">Functional acceptance</text>
<text x="800" y="480">Use received Accu SHKL-M5-20-A2-R360 as the countersink functional gauge.</text>
<text x="800" y="515">Head proud ≤0.05 mm; recess ≤0.25 mm. Residual thickness below cone ≥5.80 mm.</text>
<text x="800" y="550">Inspect all dimensions; record actual hole coordinates, thickness, flatness, and mass.</text>
<text x="800" y="585">Dry-fit only with received ROBOTIS frames and 20-2040 article before load proof.</text>
<text x="800" y="640" class="head">Release boundary</text>
<text x="800" y="680">Drawing is suitable for supplier DFM/quotation only after program authorization.</text>
<text x="800" y="715">No production quantity. One separately authorized first article maximum.</text>
<text x="800" y="750">Torque, final locking validation, cable clearance, proof load, FAI, and qualified</text>
<text x="800" y="785">mechanical disposition remain required before assembly or actuator connection.</text>
<text x="800" y="850" class="warn">DO NOT FABRICATE OR ENERGIZE FROM THIS DRAWING ALONE.</text>
<text x="800" y="890">Units: mm • Projection: adapter face X–Z • Revision: {REVISION}</text>
</svg>'''
    path.write_text(svg, encoding="utf-8", newline="\n")


def positive_intersection(a: cq.Shape, b: cq.Shape) -> float:
    try:
        return max(0.0, a.intersect(b).Volume())
    except Exception:
        return float("inf")


def boxes_overlap(a: cq.Shape, b: cq.Shape, tolerance: float = 1e-6) -> bool:
    aa = a.BoundingBox()
    bb = b.BoundingBox()
    return not (
        aa.xmax < bb.xmin - tolerance or bb.xmax < aa.xmin - tolerance
        or aa.ymax < bb.ymin - tolerance or bb.ymax < aa.ymin - tolerance
        or aa.zmax < bb.zmin - tolerance or bb.zmax < aa.zmin - tolerance
    )


def bbox_tuple(shape: cq.Shape) -> tuple[float, float, float, float, float, float]:
    box = shape.BoundingBox()
    return box.xmin, box.xmax, box.ymin, box.ymax, box.zmin, box.zmax


def rotate_bbox_x(
    bounds: tuple[float, float, float, float, float, float],
    angle_deg: float,
) -> tuple[float, float, float, float, float, float]:
    xmin, xmax, ymin, ymax, zmin, zmax = bounds
    c = math.cos(math.radians(angle_deg))
    s = math.sin(math.radians(angle_deg))
    yz = [(c * y - s * z, s * y + c * z) for y in (ymin, ymax) for z in (zmin, zmax)]
    return xmin, xmax, min(item[0] for item in yz), max(item[0] for item in yz), min(item[1] for item in yz), max(item[1] for item in yz)


def bbox_values_overlap(
    a: tuple[float, float, float, float, float, float],
    b: tuple[float, float, float, float, float, float],
    tolerance: float = 1e-6,
) -> bool:
    return not (
        a[1] < b[0] - tolerance
        or b[1] < a[0] - tolerance
        or a[3] < b[2] - tolerance
        or b[3] < a[2] - tolerance
        or a[5] < b[4] - tolerance
        or b[5] < a[4] - tolerance
    )


def bbox_distance_values(
    a: tuple[float, float, float, float, float, float],
    b: tuple[float, float, float, float, float, float],
) -> float:
    """Euclidean lower bound between two axis-aligned bounding boxes."""

    dx = max(a[0] - b[1], b[0] - a[1], 0.0)
    dy = max(a[2] - b[3], b[2] - a[3], 0.0)
    dz = max(a[4] - b[5], b[4] - a[5], 0.0)
    return math.sqrt(dx * dx + dy * dy + dz * dz)


def bbox_radius_about_x(shape: cq.Shape, origin_y: float = 0.0, origin_z: float = 0.0) -> float:
    """Conservative maximum Y-Z radius using the shape's enclosing AABB."""

    bounds = bbox_tuple(shape)
    return max(
        math.hypot(y - origin_y, z - origin_z)
        for y in (bounds[2], bounds[3])
        for z in (bounds[4], bounds[5])
    )


def chord_motion_bound(radius_mm: float, half_width_deg: float) -> float:
    """Maximum point displacement from an interval center under X rotation."""

    return 2.0 * radius_mm * math.sin(math.radians(abs(half_width_deg)) / 2.0)


def certify_continuous_1d(
    *,
    pair_id: str,
    fixed_shape: cq.Shape,
    moving_shape: cq.Shape,
    rotation_origin_y: float,
    q_lo: float,
    q_hi: float,
    coordinate: str,
) -> tuple[dict[str, object], list[dict[str, object]]]:
    """Certify a one-angle interval with exact/AABB distance and a chord bound."""

    radius = bbox_radius_about_x(moving_shape, rotation_origin_y)
    fixed_bounds = bbox_tuple(fixed_shape)
    pending = [(q_lo, q_hi, 0)]
    leaves: list[dict[str, object]] = []
    exact_calls = 0
    while pending:
        lo, hi, depth = pending.pop()
        mid = (lo + hi) / 2.0
        transformed = rotate_x(moving_shape, mid, rotation_origin_y)
        aabb_lower = bbox_distance_values(fixed_bounds, bbox_tuple(transformed))
        motion_bound = chord_motion_bound(radius, (hi - lo) / 2.0)
        center_distance = aabb_lower
        method = "AABB_LOWER_BOUND"
        if center_distance - motion_bound < CONTINUOUS_CERTIFIED_CLEARANCE_MM:
            center_distance = fixed_shape.distance(transformed)
            exact_calls += 1
            method = "EXACT_BREP_DISTANCE"
        guaranteed = center_distance - motion_bound
        if guaranteed + CONTINUOUS_NUMERIC_TOLERANCE_MM >= CONTINUOUS_CERTIFIED_CLEARANCE_MM:
            leaves.append(
                {
                    "pair_id": pair_id,
                    "coordinate": coordinate,
                    "q1_lo_deg": f"{lo:.9f}" if coordinate == "J1" else "",
                    "q1_hi_deg": f"{hi:.9f}" if coordinate == "J1" else "",
                    "q2_lo_deg": f"{lo:.9f}" if coordinate == "J2" else "",
                    "q2_hi_deg": f"{hi:.9f}" if coordinate == "J2" else "",
                    "center_distance_mm": f"{center_distance:.9f}",
                    "motion_bound_mm": f"{motion_bound:.9f}",
                    "guaranteed_clearance_mm": f"{guaranteed:.9f}",
                    "distance_method": method,
                    "subdivision_depth": depth,
                    "status": "CERTIFIED_NOMINAL_MODEL_SPACE",
                }
            )
            continue
        if hi - lo <= CONTINUOUS_MIN_CELL_DEG:
            raise RuntimeError(
                f"continuous proof failed for {pair_id} on {coordinate} in [{lo}, {hi}]: "
                f"guaranteed {guaranteed:.9f} mm"
            )
        split = mid
        pending.append((split, hi, depth + 1))
        pending.append((lo, split, depth + 1))
    minimum = min(float(row["guaranteed_clearance_mm"]) for row in leaves)
    summary = {
        "pair_id": pair_id,
        "coordinates": coordinate,
        "q1_range_deg": f"{q_lo:.6f}..{q_hi:.6f}" if coordinate == "J1" else "INVARIANT",
        "q2_range_deg": f"{q_lo:.6f}..{q_hi:.6f}" if coordinate == "J2" else "INVARIANT",
        "certified_leaf_cells": len(leaves),
        "exact_brep_distance_calls": exact_calls,
        "minimum_guaranteed_clearance_mm": f"{minimum:.9f}",
        "status": "CERTIFIED_NOMINAL_MODEL_SPACE",
    }
    return summary, leaves


def certify_continuous_2d(
    *,
    pair_id: str,
    fixed_shape: cq.Shape,
    moving_shape: cq.Shape,
    q1_lo: float,
    q1_hi: float,
    q2_lo: float,
    q2_hi: float,
) -> tuple[dict[str, object], list[dict[str, object]]]:
    """Certify a two-angle interval with additive rigid-motion chord bounds."""

    radius_j2 = bbox_radius_about_x(moving_shape, J2_Y)
    radius_j1 = J2_Y + radius_j2
    fixed_bounds = bbox_tuple(fixed_shape)
    pending = [(q1_lo, q1_hi, q2_lo, q2_hi, 0)]
    leaves: list[dict[str, object]] = []
    exact_calls = 0
    while pending:
        lo1, hi1, lo2, hi2, depth = pending.pop()
        mid1 = (lo1 + hi1) / 2.0
        mid2 = (lo2 + hi2) / 2.0
        transformed = rotate_x(rotate_x(moving_shape, mid2, J2_Y), mid1)
        aabb_lower = bbox_distance_values(fixed_bounds, bbox_tuple(transformed))
        bound1 = chord_motion_bound(radius_j1, (hi1 - lo1) / 2.0)
        bound2 = chord_motion_bound(radius_j2, (hi2 - lo2) / 2.0)
        motion_bound = bound1 + bound2
        center_distance = aabb_lower
        method = "AABB_LOWER_BOUND"
        if center_distance - motion_bound < CONTINUOUS_CERTIFIED_CLEARANCE_MM:
            center_distance = fixed_shape.distance(transformed)
            exact_calls += 1
            method = "EXACT_BREP_DISTANCE"
        guaranteed = center_distance - motion_bound
        if guaranteed + CONTINUOUS_NUMERIC_TOLERANCE_MM >= CONTINUOUS_CERTIFIED_CLEARANCE_MM:
            leaves.append(
                {
                    "pair_id": pair_id,
                    "coordinate": "J1+J2",
                    "q1_lo_deg": f"{lo1:.9f}",
                    "q1_hi_deg": f"{hi1:.9f}",
                    "q2_lo_deg": f"{lo2:.9f}",
                    "q2_hi_deg": f"{hi2:.9f}",
                    "center_distance_mm": f"{center_distance:.9f}",
                    "motion_bound_mm": f"{motion_bound:.9f}",
                    "guaranteed_clearance_mm": f"{guaranteed:.9f}",
                    "distance_method": method,
                    "subdivision_depth": depth,
                    "status": "CERTIFIED_NOMINAL_MODEL_SPACE",
                }
            )
            continue
        if max(hi1 - lo1, hi2 - lo2) <= CONTINUOUS_MIN_CELL_DEG:
            raise RuntimeError(
                f"continuous proof failed for {pair_id} in [{lo1}, {hi1}] x [{lo2}, {hi2}]: "
                f"guaranteed {guaranteed:.9f} mm"
            )
        # Split the angular coordinate with the larger current motion bound.
        if bound1 >= bound2:
            split = mid1
            pending.append((split, hi1, lo2, hi2, depth + 1))
            pending.append((lo1, split, lo2, hi2, depth + 1))
        else:
            split = mid2
            pending.append((lo1, hi1, split, hi2, depth + 1))
            pending.append((lo1, hi1, lo2, split, depth + 1))
    minimum = min(float(row["guaranteed_clearance_mm"]) for row in leaves)
    summary = {
        "pair_id": pair_id,
        "coordinates": "J1+J2",
        "q1_range_deg": f"{q1_lo:.6f}..{q1_hi:.6f}",
        "q2_range_deg": f"{q2_lo:.6f}..{q2_hi:.6f}",
        "certified_leaf_cells": len(leaves),
        "exact_brep_distance_calls": exact_calls,
        "minimum_guaranteed_clearance_mm": f"{minimum:.9f}",
        "status": "CERTIFIED_NOMINAL_MODEL_SPACE",
    }
    return summary, leaves


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    xm540 = import_step("XMHD-540.N101.I101.STP")
    h101 = import_step("FR13-H101K.stp")
    s102 = import_step("FR13-S102K.stp")
    h104 = import_step("FR12-H104K.stp")

    h104_axes = cylindrical_axes(h104, radius=1.25, axis="Y")
    s102_axes = cylindrical_axes(s102, radius=1.25, axis="Z")
    expected_h104_axes = set(H104_SELECTED_AXES_LOCAL_XZ)
    expected_s102_axes = {(-16.0, -8.0), (-16.0, 8.0), (16.0, -8.0), (16.0, 8.0)}
    if not expected_h104_axes <= h104_axes:
        raise RuntimeError(f"controlled H104 STEP lost selected axes: {sorted(expected_h104_axes - h104_axes)}")
    if not expected_s102_axes <= s102_axes:
        raise RuntimeError(f"controlled S102 STEP lost selected axes: {sorted(expected_s102_axes - s102_axes)}")
    feature_rows = [
        {
            "feature_id": "FEAT-H104-001",
            "source": "cad/vendor/robotis/FR12-H104K.stp",
            "source_sha256": sha256(VENDOR / "FR12-H104K.stp"),
            "official_drawing_date": "2017-08-31",
            "axis_direction": "local Y",
            "diameter_mm": "2.5",
            "selected_axes": ";".join(f"X={x:g},Z={z:g}" for x, z in H104_SELECTED_AXES_LOCAL_XZ),
            "verification": "exact cylinder-axis subset present in controlled STEP",
            "release_boundary": "received frame fit and FAI required",
        },
        {
            "feature_id": "FEAT-S102-001",
            "source": "cad/vendor/robotis/FR13-S102K.stp",
            "source_sha256": sha256(VENDOR / "FR13-S102K.stp"),
            "official_drawing_date": "2026-01-07",
            "axis_direction": "local Z before project Rx90",
            "diameter_mm": "2.5",
            "selected_axes": ";".join(f"X={x:g},Y={y:g}" for x, y in sorted(expected_s102_axes)),
            "verification": "exact cylinder-axis subset present in controlled STEP",
            "release_boundary": "received frame fit and FAI required",
        },
    ]
    write_csv(OUT / "interface-feature-evidence.csv", feature_rows)

    # Reference pose: J1 and J2 axes are parallel +X.  The raw actuator STEP
    # output axis is local Z and must first be mapped into the joint frame.  The
    # J2 fixed package is then rolled +90 degrees about X so the S102 broad face
    # opposes the upper-link distal adapter.  A -90 degree output reference
    # returns H101 and the straight forearm to project +Y.
    joint_body = actuator_to_joint_frame(xm540)
    # Both fixed S102 frames are rolled +90 degrees. Their outside broad faces
    # become vertical mounting planes. The H101 output references remain in the
    # straight project pose through an explicit -90 degree output offset.
    j1_body = rotate_x(joint_body, 90.0)
    j1_s102 = rotate_x(s102, 90.0)
    j1_h101 = h101
    support_plate = shoulder_support_plate()
    column = column_envelope()
    upper_p = adapter(32.0)
    upper_b = beam(32.0 + PLATE_T, UPPER_BEAM_L)
    upper_d = adapter(32.0 + PLATE_T + UPPER_BEAM_L)
    j2_body = rotate_x(joint_body, 90.0).translate((0.0, J2_Y, 0.0))
    j2_s102 = rotate_x(s102, 90.0).translate((0.0, J2_Y, 0.0))
    j2_h101 = h101.translate((0.0, J2_Y, 0.0))
    fore_p_y = J2_Y + 32.0
    fore_p = adapter(fore_p_y)
    fore_b = beam(fore_p_y + PLATE_T, FOREARM_BEAM_L)
    fore_d = gripper_adapter(fore_p_y + PLATE_T + FOREARM_BEAM_L)
    gripper_frame = rotate_x(h104, 180.0).translate((0.0, G1_Y, 0.0))

    components = {
        "COLUMN_40-4040_ENVELOPE": column,
        "MV0-C05_SHOULDER_SUPPORT": support_plate,
        "J1_XM540": j1_body,
        "J1_S102_RX90": j1_s102,
        "J1_H101": j1_h101,
        "UL_PROX_ADAPTER": upper_p,
        "UL_20-2040_VERTICAL_ENVELOPE": upper_b,
        "UL_DIST_ADAPTER": upper_d,
        "J2_XM540_RX90": j2_body,
        "J2_S102_RX90": j2_s102,
        "J2_H101_OUTPUT_REFERENCE": j2_h101,
        "FA_PROX_ADAPTER": fore_p,
        "FA_20-2040_VERTICAL_50MM_ENVELOPE": fore_b,
        "FA_DIST_H104_ADAPTER": fore_d,
        "G1_H104_RX180": gripper_frame,
    }

    assembly = cq.Assembly(name="HR_V0_ARM_ARCHITECTURE_CANDIDATE_NOT_RELEASED")
    colors = {
        "J1_XM540": cq.Color(0.05, 0.25, 0.50),
        "J2_XM540_RX90": cq.Color(0.05, 0.25, 0.50),
        "J1_H101": cq.Color(0.95, 0.70, 0.10),
        "J2_H101_OUTPUT_REFERENCE": cq.Color(0.95, 0.70, 0.10),
        "J2_S102_RX90": cq.Color(0.40, 0.78, 0.96),
        "J1_S102_RX90": cq.Color(0.40, 0.78, 0.96),
        "G1_H104_RX180": cq.Color(0.40, 0.78, 0.96),
        "MV0-C05_SHOULDER_SUPPORT": cq.Color(0.82, 0.84, 0.86),
        "COLUMN_40-4040_ENVELOPE": cq.Color(0.46, 0.50, 0.54),
    }
    for name, solid in components.items():
        assembly.add(solid, name=name, color=colors.get(name, cq.Color(0.65, 0.69, 0.73)))
    step_path = OUT / "HR-V0_arm_architecture_candidate.step"
    # Assembly STEP presentation records are emitted in nondeterministic map
    # order by OCC.  The controlled STEP is therefore an ordered geometry
    # compound; the GLB carries the component names and review colors.
    cq.exporters.export(cq.Compound.makeCompound(list(components.values())), str(step_path))
    canonicalize_step(step_path)
    assembly.save(str(OUT / "HR-V0_arm_architecture_candidate.glb"))

    # Native candidate custom parts.  These define topology for review but are
    # expressly excluded from quotation/fabrication until tolerances, material,
    # fasteners, access and proof are released.
    part_dir = OUT / "parts"
    part_dir.mkdir()
    for name, solid in {
        "MV0-C01_rect32x16_to_20-2040_countersunk_adapter": adapter(0.0),
        "MV0-C02_20-2040_100mm_vertical_collision_envelope": beam(0.0, UPPER_BEAM_L),
        "MV0-C03_20-2040_50mm_vertical_collision_envelope": beam(0.0, FOREARM_BEAM_L),
        "MV0-C04_H104_to_20-2040_countersunk_adapter": gripper_adapter(0.0),
        "MV0-C05_S102_to_40-4040_side_slot_support": shoulder_support_plate(),
    }.items():
        part_path = part_dir / f"{name}.step"
        cq.exporters.export(solid, str(part_path))
        canonicalize_step(part_path)
    write_adapter_dxf(part_dir / "MV0-C01_adapter-finished-profile.dxf")
    write_custom_plate_dxf(
        part_dir / "MV0-C04_gripper-adapter-finished-profile.dxf",
        width=48.0,
        height=40.0,
        small_holes=tuple((x, -local_z) for x, local_z in H104_SELECTED_AXES_LOCAL_XZ),
        large_holes=((0.0, -10.0), (0.0, 10.0)),
        countersunk_large=True,
    )
    write_custom_plate_dxf(
        part_dir / "MV0-C05_shoulder-support-finished-profile.dxf",
        width=48.0,
        height=SUPPORT_PLATE_H,
        small_holes=((-16.0, -8.0), (-16.0, 8.0), (16.0, -8.0), (16.0, 8.0)),
        large_holes=((0.0, -30.0), (0.0, 30.0)),
        countersunk_large=False,
    )
    write_adapter_drawing(OUT / "MV0-C01_adapter-candidate-drawing.svg")
    write_interface_plate_drawing(
        OUT / "MV0-C04_gripper-adapter-candidate-drawing.svg",
        title="MV0-C04 H104-to-20-2040 gripper adapter candidate",
        part_id="MV0-C04",
        envelope="48.00 x 40.00 x 9.525 nominal",
        small_pattern="4 x diameter 2.70 at project X/Z (-11,+8), (+11,+8), (-12,-6), (+12,-6)",
        large_pattern="2 x diameter 5.50 with 11.30-11.40 countersink at X=0, Z=+/-10",
        source_note="The four H104 axes are exact cylindrical axes extracted from controlled FR12-H104K STEP; drawing dated Aug-31-17.",
        use_note="The selected subset avoids the two M5 countersinks nominally and is verified against the transformed H104 STEP.",
    )
    write_interface_plate_drawing(
        OUT / "MV0-C05_shoulder-support-candidate-drawing.svg",
        title="MV0-C05 S102-to-40-4040 side-slot support candidate",
        part_id="MV0-C05",
        envelope="48.00 x 80.00 x 9.525 nominal",
        small_pattern="4 x diameter 2.70 at X=+/-16, Z=+/-8 for the rolled S102 broad-face pattern",
        large_pattern="2 x diameter 8.50 at X=0, Z=+/-30 for the 40-4040 front T-slot",
        source_note="S102 pattern is checked against controlled FR13-S102K STEP/drawing dated 2026-01-07; column is 80/20 40-4040.",
        use_note="17-8520 plus 13035 are exact mounting-hardware candidates only; T-slot pullout, torque and proof remain open.",
    )

    actuator_matrix = [[0.0, 0.0, -1.0, ACTUATOR_AXIAL_OFFSET_X], [1.0, 0.0, 0.0, 0.0], [0.0, -1.0, 0.0, 0.0], [0.0, 0.0, 0.0, 1.0]]
    transform_rows = [
        {"item": "40-4040 column envelope", "parent": "J1_LOCAL", "tx_mm": 0, "ty_mm": COLUMN_CENTER_Y, "tz_mm": COLUMN_TOP_Z - COLUMN_LENGTH, "rx_deg": 0, "matrix_4x4_row_major": json.dumps(matrix_x(0, 0, COLUMN_CENTER_Y, COLUMN_TOP_Z - COLUMN_LENGTH)), "status": "conservative purchased-profile envelope; received cross-section and support proof open"},
        {"item": "MV0-C05 shoulder support", "parent": "J1_LOCAL", "tx_mm": 0, "ty_mm": COLUMN_FACE_Y, "tz_mm": -SUPPORT_PLATE_H / 2.0, "rx_deg": 0, "matrix_4x4_row_major": json.dumps(matrix_x(0, 0, COLUMN_FACE_Y, -SUPPORT_PLATE_H / 2.0)), "status": "exact candidate geometry; T-slot stack torque pullout and proof open"},
        {"item": "J1 XM540 body and S102", "parent": "J1_LOCAL", "tx_mm": 0, "ty_mm": 0, "tz_mm": 0, "rx_deg": 90, "matrix_4x4_row_major": json.dumps(matrix_x(90, 0, 0, 0)), "status": "package roll exact; internal XM540 uses the recorded actuator axis-map"},
        {"item": "J1 H101 straight-reference pose", "parent": "J1_LOCAL", "tx_mm": 0, "ty_mm": 0, "tz_mm": 0, "rx_deg": 0, "matrix_4x4_row_major": json.dumps(matrix_x(0, 0, 0, 0)), "status": "requires -90 deg output offset relative J1 body"},
        {"item": "J2 joint package and S102", "parent": "WORLD", "tx_mm": 0, "ty_mm": J2_Y, "tz_mm": 0, "rx_deg": 90, "matrix_4x4_row_major": json.dumps(matrix_x(90, 0, J2_Y, 0)), "status": "package roll exact; internal XM540 uses the recorded actuator axis-map"},
        {"item": "J2 H101 straight-reference pose", "parent": "WORLD", "tx_mm": 0, "ty_mm": J2_Y, "tz_mm": 0, "rx_deg": 0, "matrix_4x4_row_major": json.dumps(matrix_x(0, 0, J2_Y, 0)), "status": "requires -90 deg output offset relative J2 body"},
        {"item": "G1 H104 frame", "parent": "WORLD", "tx_mm": 0, "ty_mm": G1_Y, "tz_mm": 0, "rx_deg": 180, "matrix_4x4_row_major": json.dumps(matrix_x(180, 0, G1_Y, 0)), "status": "four exact broad-face axes registered to MV0-C04; received fit and gripper kit assembly remain open"},
        {"item": "J1 local frame", "parent": "A0_BASE_CENTER", "tx_mm": J1_A0_X, "ty_mm": J1_A0_Y, "tz_mm": J1_A0_Z, "rx_deg": 0, "matrix_4x4_row_major": json.dumps(matrix_x(0, J1_A0_X, J1_A0_Y, J1_A0_Z)), "status": "candidate full-assembly placement; base/column receipt and inspection open"},
    ]
    write_csv(OUT / "transform-schedule.csv", transform_rows)

    interface_rows = [
        {"interface": "A00", "from": "40-4040 column front T-slot", "to": "MV0-C05 shoulder support and rolled J1 S102", "plane_world": f"J1-local Y={COLUMN_FACE_Y:.4f} to {J1_S102_FACE_Y:.4f} mm", "pattern": "2 x dia 8.50 at X=0 Z=+/-30 to T-slot; 4 x dia 2.70 at X=+/-16 Z=+/-8 to S102", "fasteners": "80/20 17-8520 + 13035 and MISUMI SCB2.5-20 + ACCU HNN-M2.5-A2 EXACT CANDIDATE HOLD; torque/received stack SELECTION REQUIRED", "status": "exact_coordinate_candidate_static_screen_only"},
        {"interface": "A01", "from": "J1 H101 outside broad face", "to": "upper proximal adapter", "plane_world": "Y=32.0000 mm", "pattern": "4 x manufacturer dia 2.5 thru at X=+/-16 Z=+/-8; adapter dia 2.70", "fasteners": "MISUMI SCB2.5-20 + ACCU HNN-M2.5-A2 EXACT CANDIDATE HOLD; torque/received stack SELECTION REQUIRED", "status": "rectangular_pattern_registered_static_proof_only"},
        {"interface": "A02", "from": "upper proximal adapter", "to": "20-2040 end", "plane_world": f"Y={32.0 + PLATE_T:.4f} mm", "pattern": "2 x M5x0.8 end taps at X=0 Z=+/-10; controlled flush countersinks", "fasteners": "ACCU SHKL-M5-20-A2-R360 EXACT CANDIDATE HOLD; torque/received seating SELECTION REQUIRED", "status": "manufacturer_coordinates_registered_static_proof_only"},
        {"interface": "A03", "from": "20-2040 end", "to": "upper distal adapter", "plane_world": f"Y={32.0 + PLATE_T + UPPER_BEAM_L:.4f} mm", "pattern": "2 x M5x0.8 end taps at X=0 Z=+/-10; controlled flush countersinks", "fasteners": "ACCU SHKL-M5-20-A2-R360 EXACT CANDIDATE HOLD; torque/received seating SELECTION REQUIRED", "status": "manufacturer_coordinates_registered_static_proof_only"},
        {"interface": "A04", "from": "upper distal adapter", "to": "J2 S102 outside broad face", "plane_world": f"Y={J2_Y - 51.5:.4f} mm", "pattern": "4 x manufacturer dia 2.5 thru at X=+/-16 Z=+/-8; adapter dia 2.70", "fasteners": "MISUMI SCB2.5-20 + ACCU HNN-M2.5-A2 EXACT CANDIDATE HOLD; torque/received stack SELECTION REQUIRED", "status": "rectangular_pattern_registered_static_proof_only"},
        {"interface": "A05", "from": "J2 H101 outside broad face", "to": "forearm proximal adapter", "plane_world": f"Y={fore_p_y:.4f} mm at straight reference", "pattern": "4 x manufacturer dia 2.5 thru at X=+/-16 Z=+/-8; adapter dia 2.70", "fasteners": "MISUMI SCB2.5-20 + ACCU HNN-M2.5-A2 EXACT CANDIDATE HOLD; torque/received stack SELECTION REQUIRED", "status": "rectangular_pattern_registered_static_proof_only"},
        {"interface": "A06", "from": "forearm beam", "to": "forearm adapters", "plane_world": f"Y={fore_p_y + PLATE_T:.4f} and {fore_p_y + PLATE_T + FOREARM_BEAM_L:.4f} mm at straight reference", "pattern": "2 x M5x0.8 end taps at X=0 Z=+/-10; controlled flush countersinks", "fasteners": "ACCU SHKL-M5-20-A2-R360 EXACT CANDIDATE HOLD; torque/received seating SELECTION REQUIRED", "status": "manufacturer_coordinates_registered_static_proof_only"},
        {"interface": "A07", "from": "MV0-C04 forearm distal adapter", "to": "H104 outside broad face", "plane_world": f"Y={fore_p_y + 2 * PLATE_T + FOREARM_BEAM_L:.4f} mm at straight reference", "pattern": "4 x exact H104 dia 2.5 axes; project X/Z (-11,+8),(+11,+8),(-12,-6),(+12,-6); adapter dia 2.70", "fasteners": "MISUMI SCB2.5-20 + ACCU HNN-M2.5-A2 EXACT CANDIDATE HOLD; torque/received stack SELECTION REQUIRED", "status": "exact_step_axis_subset_registered_static_proof_only"},
    ]
    write_csv(OUT / "interface-schedule.csv", interface_rows)

    fixed_base = {
        "COLUMN": column,
        "SHOULDER_SUPPORT": support_plate,
        "J1_BODY": j1_body,
        "J1_S102": j1_s102,
    }
    upper_zero = {
        "J1_H101": j1_h101,
        "UPPER_PROX_ADAPTER": upper_p,
        "UPPER_MEMBER": upper_b,
        "UPPER_DIST_ADAPTER": upper_d,
        "J2_BODY": j2_body,
        "J2_S102": j2_s102,
    }
    moving_zero = {
        "J2_H101": j2_h101,
        "FORE_PROX_ADAPTER": fore_p,
        "FORE_MEMBER": fore_b,
        "FORE_DIST_H104_ADAPTER": fore_d,
        "G1_H104": gripper_frame,
    }
    intentional_j1_pairs = {("J1_BODY", "J1_H101"), ("J1_S102", "J1_H101")}
    intentional_j2_pairs = {("J2_BODY", "J2_H101"), ("J2_S102", "J2_H101")}
    sweep_rows: list[dict[str, object]] = []
    worst = 0.0
    q1_values = [-20.0 + sample * COLLISION_INCREMENT_DEG for sample in range(int(round(90.0 / COLLISION_INCREMENT_DEG)) + 1)]
    q2_values = [15.0 + sample * COLLISION_INCREMENT_DEG for sample in range(int(round(110.0 / COLLISION_INCREMENT_DEG)) + 1)]
    fixed_bounds = {name: bbox_tuple(shape) for name, shape in fixed_base.items()}

    # Base-versus-upper collisions depend only on J1. Compute those exact
    # booleans once per J1 pose rather than once for every J1/J2 combination.
    base_upper_by_q1: dict[float, tuple[float, int, list[str]]] = {}
    for q1_deg in q1_values:
        upper = {name: rotate_x(item, q1_deg) for name, item in upper_zero.items()}
        volume = 0.0
        tested = 0
        pairs: list[str] = []
        for fixed_name, fixed_shape in fixed_base.items():
            for upper_name, upper_shape in upper.items():
                if (fixed_name, upper_name) in intentional_j1_pairs:
                    continue
                if boxes_overlap(fixed_shape, upper_shape):
                    tested += 1
                    pair_volume = positive_intersection(fixed_shape, upper_shape)
                    volume += pair_volume
                    if pair_volume > 1e-5:
                        pairs.append(f"{fixed_name}:{upper_name}={pair_volume:.6f}")
        base_upper_by_q1[q1_deg] = (volume, tested, pairs)

    # Upper-versus-forearm collisions depend only on the internal J2 angle;
    # a common J1 rotation cannot change their relative intersection.
    upper_fore_by_q2: dict[float, tuple[float, int, list[str]]] = {}
    for q2_deg in q2_values:
        fore_relative = {name: rotate_x(item, q2_deg, J2_Y) for name, item in moving_zero.items()}
        volume = 0.0
        tested = 0
        pairs: list[str] = []
        for upper_name, upper_shape in upper_zero.items():
            for fore_name, fore_shape in fore_relative.items():
                if (upper_name, fore_name) in intentional_j2_pairs:
                    continue
                if boxes_overlap(upper_shape, fore_shape):
                    tested += 1
                    pair_volume = positive_intersection(upper_shape, fore_shape)
                    volume += pair_volume
                    if pair_volume > 1e-5:
                        pairs.append(f"{upper_name}:{fore_name}={pair_volume:.6f}")
        upper_fore_by_q2[q2_deg] = (volume, tested, pairs)

    # The remaining base-versus-forearm pairs receive a conservative rotated
    # AABB screen. Exact transformed solids and booleans are created only when
    # those enclosing boxes overlap, so this stage cannot skip a real contact.
    for q2_deg in q2_values:
        relative_volume, relative_tested, relative_pairs = upper_fore_by_q2[q2_deg]
        fore_relative = {name: rotate_x(item, q2_deg, J2_Y) for name, item in moving_zero.items()}
        fore_bounds = {name: bbox_tuple(shape) for name, shape in fore_relative.items()}
        for q1_deg in q1_values:
            base_volume, base_tested, base_pairs = base_upper_by_q1[q1_deg]
            volume = base_volume + relative_volume
            tested_pairs = base_tested + relative_tested
            colliding_pairs = list(base_pairs) + list(relative_pairs)
            for fixed_name, fixed_shape in fixed_base.items():
                for fore_name, relative_shape in fore_relative.items():
                    rotated_bounds = rotate_bbox_x(fore_bounds[fore_name], q1_deg)
                    if not bbox_values_overlap(fixed_bounds[fixed_name], rotated_bounds):
                        continue
                    tested_pairs += 1
                    transformed = rotate_x(relative_shape, q1_deg)
                    pair_volume = positive_intersection(fixed_shape, transformed)
                    volume += pair_volume
                    if pair_volume > 1e-5:
                        colliding_pairs.append(f"{fixed_name}:{fore_name}={pair_volume:.6f}")

            worst = max(worst, volume)
            if q2_deg <= PROVISIONAL_J2_SOFT_LIMIT_DEG:
                result = "PASS" if volume <= 1e-5 else "COLLISION_WITHIN_PROVISIONAL_LIMIT"
            else:
                result = "COLLISION" if volume > 1e-5 else "OUTSIDE_PROVISIONAL_LIMIT"
            sweep_rows.append(
                {
                    "j1_deg": f"{q1_deg:.1f}",
                    "j2_internal_deg": f"{q2_deg:.1f}",
                    "broadphase_pairs_requiring_boolean": tested_pairs,
                    "colliding_pairs": ";".join(colliding_pairs),
                    "sampled_pairwise_intersection_mm3": f"{volume:.6f}",
                    "result": result,
                    "scope": "0.5-deg two-joint sampled collision screen; conservative rotated-AABB broadphase; exact booleans for every overlapping box; intentional J1/J2 frame interfaces excluded; cables, guards, stops and between-sample proof excluded",
                }
            )
    write_csv(OUT / "collision-sweep.csv", sweep_rows)
    collision_rows = [row for row in sweep_rows if row["result"] in ("COLLISION", "COLLISION_WITHIN_PROVISIONAL_LIMIT")]
    first_nominal_collision_deg = min((float(row["j2_internal_deg"]) for row in collision_rows), default=None)
    max_intersection_within_limit = max(
        float(row["sampled_pairwise_intersection_mm3"])
        for row in sweep_rows
        if float(row["j2_internal_deg"]) <= PROVISIONAL_J2_SOFT_LIMIT_DEG
    )

    # Continuous nominal model-space clearance certificate.  At each adaptive
    # cell center, an AABB lower bound or exact B-Rep distance is reduced by a
    # rigorous chord-displacement bound for every permitted angular deviation
    # inside that cell.  A leaf is accepted only when the remainder is at least
    # 0.75 mm.  This closes only between-sample CAD separation; manufacturing
    # tolerance, cables, guards, compliance and stopping travel remain open.
    continuous_summary_rows: list[dict[str, object]] = []
    continuous_cell_rows: list[dict[str, object]] = []
    for fixed_name, fixed_shape in fixed_base.items():
        for upper_name, upper_shape in upper_zero.items():
            if (fixed_name, upper_name) in intentional_j1_pairs:
                continue
            summary_row, cell_rows = certify_continuous_1d(
                pair_id=f"BASE_UPPER:{fixed_name}:{upper_name}",
                fixed_shape=fixed_shape,
                moving_shape=upper_shape,
                rotation_origin_y=0.0,
                q_lo=-20.0,
                q_hi=70.0,
                coordinate="J1",
            )
            continuous_summary_rows.append(summary_row)
            continuous_cell_rows.extend(cell_rows)
    for upper_name, upper_shape in upper_zero.items():
        for fore_name, fore_shape in moving_zero.items():
            if (upper_name, fore_name) in intentional_j2_pairs:
                continue
            summary_row, cell_rows = certify_continuous_1d(
                pair_id=f"UPPER_FORE:{upper_name}:{fore_name}",
                fixed_shape=upper_shape,
                moving_shape=fore_shape,
                rotation_origin_y=J2_Y,
                q_lo=15.0,
                q_hi=CONTINUOUS_ANALYSIS_J2_MAX_DEG,
                coordinate="J2",
            )
            continuous_summary_rows.append(summary_row)
            continuous_cell_rows.extend(cell_rows)
    for fixed_name, fixed_shape in fixed_base.items():
        for fore_name, fore_shape in moving_zero.items():
            summary_row, cell_rows = certify_continuous_2d(
                pair_id=f"BASE_FORE:{fixed_name}:{fore_name}",
                fixed_shape=fixed_shape,
                moving_shape=fore_shape,
                q1_lo=-20.0,
                q1_hi=70.0,
                q2_lo=15.0,
                q2_hi=CONTINUOUS_ANALYSIS_J2_MAX_DEG,
            )
            continuous_summary_rows.append(summary_row)
            continuous_cell_rows.extend(cell_rows)
    write_csv(OUT / "continuous-clearance-summary.csv", continuous_summary_rows)
    write_csv(OUT / "continuous-clearance-cells.csv", continuous_cell_rows)
    continuous_minimum_guaranteed_mm = min(
        float(row["minimum_guaranteed_clearance_mm"])
        for row in continuous_summary_rows
    )

    critical_fixed = upper_zero["J2_BODY"]
    critical_moving = moving_zero["FORE_PROX_ADAPTER"]
    continuous_contact_lo = CONTINUOUS_ANALYSIS_J2_MAX_DEG
    continuous_contact_hi = first_nominal_collision_deg or 125.0
    for _ in range(60):
        midpoint = (continuous_contact_lo + continuous_contact_hi) / 2.0
        clearance = critical_fixed.distance(rotate_x(critical_moving, midpoint, J2_Y))
        if clearance > 1e-7:
            continuous_contact_lo = midpoint
        else:
            continuous_contact_hi = midpoint
    continuous_first_contact_deg = continuous_contact_hi
    clearance_at_analysis_max_mm = critical_fixed.distance(
        rotate_x(critical_moving, CONTINUOUS_ANALYSIS_J2_MAX_DEG, J2_Y)
    )
    clearance_at_soft_limit_mm = critical_fixed.distance(
        rotate_x(critical_moving, PROVISIONAL_J2_SOFT_LIMIT_DEG, J2_Y)
    )
    soft_to_stop_deg = CANDIDATE_J2_POSITIVE_HARD_STOP_DEG - PROVISIONAL_J2_SOFT_LIMIT_DEG
    stop_to_contact_deg = continuous_first_contact_deg - CANDIDATE_J2_POSITIVE_HARD_STOP_DEG
    candidate_physical_budget_deg = stop_to_contact_deg - CANDIDATE_CONTACT_GUARD_DEG
    continuous_analysis = {
        "revision": REVISION,
        "method": "adaptive interval cover; center AABB lower bound or exact B-Rep distance minus additive rigid-body chord-displacement bounds",
        "included_pair_groups": ["fixed base versus upper", "upper versus forearm", "fixed base versus forearm"],
        "intentional_interfaces_excluded": sorted(
            [f"{left}:{right}" for left, right in intentional_j1_pairs | intentional_j2_pairs]
        ),
        "joint_domain_deg": {"j1": [-20.0, 70.0], "j2": [15.0, CONTINUOUS_ANALYSIS_J2_MAX_DEG]},
        "required_certified_clearance_mm": CONTINUOUS_CERTIFIED_CLEARANCE_MM,
        "minimum_guaranteed_clearance_mm": round(continuous_minimum_guaranteed_mm, 6),
        "pair_count": len(continuous_summary_rows),
        "certified_leaf_cell_count": len(continuous_cell_rows),
        "exact_brep_distance_call_count": sum(int(row["exact_brep_distance_calls"]) for row in continuous_summary_rows),
        "critical_pair": "UPPER_FORE:J2_BODY:FORE_PROX_ADAPTER",
        "critical_pair_exact_clearance_at_j2_120_mm": round(clearance_at_analysis_max_mm, 6),
        "critical_pair_exact_clearance_at_candidate_soft_limit_mm": round(clearance_at_soft_limit_mm, 6),
        "continuous_first_contact_j2_deg_numeric": round(continuous_first_contact_deg, 6),
        "continuous_first_contact_threshold_mm": 1e-7,
        "release_boundary": "nominal model-space separation only; tolerances, deformation, cables, guards, stops, stopping travel and physical proof excluded",
        "status": "CERTIFIED_NOMINAL_MODEL_SPACE_NOT_A_PHYSICAL_OR_MOTION_RELEASE",
    }
    (OUT / "continuous-clearance-analysis.json").write_text(
        json.dumps(continuous_analysis, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    hard_stop_allocation_rows = [
        {
            "joint": "J2_POSITIVE",
            "candidate_software_limit_deg": f"{PROVISIONAL_J2_SOFT_LIMIT_DEG:.6f}",
            "candidate_backed_up_hard_stop_datum_deg": f"{CANDIDATE_J2_POSITIVE_HARD_STOP_DEG:.6f}",
            "continuous_nominal_first_contact_deg": f"{continuous_first_contact_deg:.6f}",
            "soft_limit_to_stop_allowance_deg": f"{soft_to_stop_deg:.6f}",
            "stop_to_nominal_contact_deg": f"{stop_to_contact_deg:.6f}",
            "reserved_nominal_collision_guard_deg": f"{CANDIDATE_CONTACT_GUARD_DEG:.6f}",
            "candidate_physical_uncertainty_budget_deg": f"{candidate_physical_budget_deg:.6f}",
            "required_physical_evidence": "measured stopping overtravel + backlash + compliance + tolerance + measurement uncertainty must fit both the 3 deg soft-to-stop allowance and the 2.643289 deg residual nominal-contact budget",
            "status": "CANDIDATE ALLOCATION ONLY - PHYSICAL STOP DESIGN AND VALIDATION REQUIRED",
            "warning": WARNING,
        }
    ]
    write_csv(OUT / "hard-stop-allocation.csv", hard_stop_allocation_rows)

    mass_per_m_kg = 0.0428 * 0.45359237 / 0.0254
    upper_beam_mass_g = mass_per_m_kg * (UPPER_BEAM_L / 1000.0) * 1000.0
    forearm_beam_mass_g = mass_per_m_kg * (FOREARM_BEAM_L / 1000.0) * 1000.0
    plate_mass_g = adapter(0.0).Volume() / 1000.0 * 2.70
    gripper_plate_mass_g = gripper_adapter(0.0).Volume() / 1000.0 * 2.70
    support_plate_mass_g = shoulder_support_plate().Volume() / 1000.0 * 2.70
    upper_link_mass_g = upper_beam_mass_g + 2 * plate_mass_g
    forearm_link_mass_g = forearm_beam_mass_g + plate_mass_g + gripper_plate_mass_g
    gravity = 9.80665
    upper_com_y = (32.0 + (J2_Y - 51.5)) / 2.0
    fore_com_y = J2_Y + 32.0 + PLATE_T + FOREARM_BEAM_L / 2.0
    shoulder_nm = gravity * (0.12 * upper_com_y / 1000.0 + 0.20 * J2_Y / 1000.0 + 0.12 * fore_com_y / 1000.0 + 0.21 * G1_Y / 1000.0 + 0.10 * 0.360)
    elbow_nm = gravity * (0.12 * (fore_com_y - J2_Y) / 1000.0 + 0.21 * (G1_Y - J2_Y) / 1000.0 + 0.10 * (360.0 - J2_Y) / 1000.0)
    shoulder_screen_nm = shoulder_nm * 2.25

    frame_to_end_center_mm = math.hypot(16.0, 2.0)
    feature_clearance_mm = frame_to_end_center_mm - END_CSK_D / 2.0 - FRAME_HOLE_D / 2.0
    m5_engagement_mm = M5_SCREW_LENGTH - PLATE_T
    m5_min_engagement_mm = M5_SCREW_LENGTH - PLATE_MAX_T
    m2_5_nominal_protrusion_mm = M2_5_SCREW_LENGTH - H101_LINK_FACE_T - PLATE_T - M2_5_NUT_T
    m2_5_screen_min_protrusion_mm = M2_5_SCREW_LENGTH - H101_LINK_FACE_MAX_T - PLATE_MAX_T - M2_5_NUT_T
    m5_couple_force_n = shoulder_screen_nm * 1000.0 / END_TAP_SPACING
    proof_moment_nm = shoulder_screen_nm * PROOF_MULTIPLIER
    proof_m5_couple_force_n = proof_moment_nm * 1000.0 / END_TAP_SPACING
    proof_m2_5_row_force_n = proof_moment_nm * 1000.0 / 16.0
    proof_m2_5_each_force_n = proof_m2_5_row_force_n / 2.0
    aluminum_shear_yield_mpa = 0.577 * 172.37
    thread_shear_area_mm2 = math.pi * 4.19 * m5_engagement_mm * 0.5
    thread_shear_capacity_n = thread_shear_area_mm2 * aluminum_shear_yield_mpa
    beam_bending_stress_mpa = shoulder_screen_nm * 1000.0 * 20.0 / (4.5357 * 10000.0)
    adapter_min_residual_mm = PLATE_MIN_T - END_CSK_DEPTH
    adapter_required_punching_shear_mpa = m5_couple_force_n / (math.pi * END_HOLE_D * adapter_min_residual_mm)
    adapter_head_annulus_mm2 = math.pi / 4.0 * (END_CSK_D_MIN ** 2 - END_HOLE_D ** 2)
    adapter_head_average_pressure_mpa = m5_couple_force_n / adapter_head_annulus_mm2
    proof_adapter_punching_shear_mpa = proof_m5_couple_force_n / (math.pi * END_HOLE_D * adapter_min_residual_mm)
    proof_adapter_head_average_pressure_mpa = proof_m5_couple_force_n / adapter_head_annulus_mm2
    proof_m2_5_bearing_mpa = proof_m2_5_each_force_n / (2.5 * PLATE_MIN_T)
    m2_5_edge_ligament_mm = 24.0 - 16.0 - FRAME_HOLE_D / 2.0
    proof_m2_5_edge_tearout_mpa = proof_m2_5_each_force_n / (2.0 * PLATE_MIN_T * m2_5_edge_ligament_mm)
    proof_adapter_net_section_mpa = proof_m2_5_row_force_n / ((48.0 - 2.0 * FRAME_HOLE_D) * PLATE_MIN_T)
    support_m8_couple_force_n = proof_moment_nm * 1000.0 / SUPPORT_M8_SPACING
    support_m8_bearing_mpa = support_m8_couple_force_n / (SUPPORT_M8_HOLE_D * PLATE_MIN_T)
    support_net_section_mpa = support_m8_couple_force_n / ((48.0 - SUPPORT_M8_HOLE_D) * PLATE_MIN_T)
    column_bending_stress_mpa = proof_moment_nm * 1000.0 * 20.0 / (13.787 * 10000.0)
    support_head_to_s102_clearance_mm = 30.0 - 16.5 - 12.87 / 2.0
    h104_to_nearest_countersink_clearance_mm = min(
        math.hypot(x, project_z - m5_z) - FRAME_HOLE_D / 2.0 - END_CSK_D / 2.0
        for x, local_z in H104_SELECTED_AXES_LOCAL_XZ
        for project_z in (-local_z,)
        for m5_z in (-10.0, 10.0)
    )
    project_fastener_shear_screen_mpa = 0.30 * FASTENER_A2_70_MIN_TENSILE_MPA
    m5_thread_root_screen_area_mm2 = math.pi * 4.0 ** 2 / 4.0
    m2_5_thread_root_screen_area_mm2 = math.pi * 2.0 ** 2 / 4.0
    m5_fastener_shear_screen_capacity_n = project_fastener_shear_screen_mpa * m5_thread_root_screen_area_mm2
    m2_5_fastener_shear_screen_capacity_n = project_fastener_shear_screen_mpa * m2_5_thread_root_screen_area_mm2
    kaiser_typical_yield_mpa = 276.0
    kaiser_typical_shear_yield_mpa = 0.577 * kaiser_typical_yield_mpa

    fastener_rows = [
        {"fastener_id": "FAST-C01", "interfaces": "A02;A03;A06", "candidate_order_code": "SHKL-M5-20-A2-R360", "description": "M5 x 20 countersunk Torx screw; A2-70 stainless; pre-applied AccuLock 360", "quantity_candidate": 8, "controlled_dimensions": "L=20 mm; head dia=9.43..11.20 mm; countersunk length=3.10 mm; T25; M5x0.8; 90 deg +2/-0", "modeled_engagement_mm": f"{m5_engagement_mm:.4f} nominal; {m5_min_engagement_mm:.4f} screen minimum", "status": "EXACT CANDIDATE HOLD", "remaining_evidence": "received identity, full-thread condition, torque development, flush seating, cure/storage, single-install project rule and proof"},
        {"fastener_id": "FAST-C02", "interfaces": "A00;A01;A04;A05;A07", "candidate_order_code": "SCB2.5-20", "description": "MISUMI M2.5 x 20 ISO 4762 socket head cap screw; A2-70 stainless", "quantity_candidate": 20, "controlled_dimensions": "L=20 mm; head dia max=4.5 mm; head height max=2.5 mm; 2 mm socket; M2.5x0.45; fully threaded", "modeled_engagement_mm": f"{m2_5_nominal_protrusion_mm:.4f} nominal protrusion beyond 3.6 mm nut; {m2_5_screen_min_protrusion_mm:.4f} geometric screen minimum", "status": "EXACT CANDIDATE HOLD", "remaining_evidence": "received identity, frame/plate/nut stack, screw-length tolerance, protrusion, torque, wrench access and proof"},
        {"fastener_id": "FAST-C03", "interfaces": "A00;A01;A04;A05;A07", "candidate_order_code": "HNN-M2.5-A2", "description": "Accu M2.5 DIN 985 nylon-insert locking nut; A2 stainless", "quantity_candidate": 20, "controlled_dimensions": "M2.5x0.45; overall thickness 3.30..3.60 mm; 5 mm across flats; nylon insert", "modeled_engagement_mm": f"paired with SCB2.5-20; {m2_5_screen_min_protrusion_mm:.4f} geometric minimum beyond nut", "status": "EXACT CANDIDATE HOLD", "remaining_evidence": "received identity/dimensions, prevailing torque, installation torque, single-use project rule, temperature envelope and proof"},
        {"fastener_id": "FAST-C04", "interfaces": "purchased member ends", "candidate_order_code": "20-7047", "description": "80/20 two-hole M5x0.8 end-tap service for 20-2040", "quantity_candidate": 4, "controlled_dimensions": "two taps; 22.23 mm published depth; 4.19 mm cores at 20 mm spacing", "modeled_engagement_mm": f"{m5_engagement_mm:.4f} nominal; {m5_min_engagement_mm:.4f} screen minimum", "status": "EXACT SERVICE CANDIDATE HOLD", "remaining_evidence": "written supplier confirmation, received thread gauge/depth inspection and proof joint"},
        {"fastener_id": "FAST-C05", "interfaces": "A00 column T-slot", "candidate_order_code": "17-8520", "description": "80/20 M8 x 20 fully threaded stainless SHCS", "quantity_candidate": 2, "controlled_dimensions": "L=20 mm; head diameter 12.87 mm; head height 7.82 mm; 6 mm hex; M8x1.25", "modeled_engagement_mm": f"{20.0 - PLATE_T:.4f} mm nominal beyond plate before T-nut projection/stack", "status": "EXACT CANDIDATE HOLD", "remaining_evidence": "received identity, T-nut engagement, washer decision, installation torque, anti-galling, head clearance and proof"},
        {"fastener_id": "FAST-C06", "interfaces": "A00 column T-slot", "candidate_order_code": "13035", "description": "80/20 M8 self-aligning roll-in T-nut with ball spring; 304 stainless; 40-series compatible", "quantity_candidate": 2, "controlled_dimensions": "22.00 x 13.50 mm body; M8x1.25; 7.80 mm height plus 0.80 mm projection", "modeled_engagement_mm": "SELECTION REQUIRED from received nut/screw/plate/slot stack", "status": "EXACT CANDIDATE HOLD", "remaining_evidence": "received identity and fit, full thread engagement, slot condition, torque, pullout/slip/prying proof and qualified acceptance"},
    ]
    write_csv(OUT / "fastener-candidate-schedule.csv", fastener_rows)

    access_rows = [
        {"check": "TA-01", "features": "M5 countersink to nearest M2.5 clearance hole", "result_mm": f"{feature_clearance_mm:.4f}", "criterion": ">= 1.0 mm nominal feature clearance", "result": "PASS NOMINAL", "release_effect": "does not release tolerance or machining process"},
        {"check": "TA-02", "features": "two M5 countersunk heads", "result_mm": f"{END_TAP_SPACING - END_CSK_D:.4f}", "criterion": ">= 1.0 mm nominal head-envelope clearance", "result": "PASS NOMINAL", "release_effect": "heads install before frame; service requires frame removal"},
        {"check": "TA-03", "features": "M2.5 clearance-hole edge at X=+/-16", "result_mm": f"{24.0 - 16.0 - FRAME_HOLE_D / 2.0:.4f}", "criterion": ">= 2d preliminary edge screen", "result": "PASS NOMINAL", "release_effect": "HNN-M2.5-A2 fits nominally; physical 5 mm tool proof remains required"},
        {"check": "TA-04", "features": "M5 countersink edge at Z=+/-10", "result_mm": f"{20.0 - 10.0 - END_CSK_D / 2.0:.4f}", "criterion": ">= 2.0 mm nominal edge clearance", "result": "PASS NOMINAL", "release_effect": "pull-through and fatigue proof remain open"},
        {"check": "TA-05", "features": "material remaining below maximum M5 countersink at finished minimum thickness", "result_mm": f"{adapter_min_residual_mm:.4f}", "criterion": ">= 5.0 mm project geometry screen; structural acceptance still requires proof", "result": "PASS NOMINAL / PROOF OPEN", "release_effect": "physical countersink inspection material certificate local analysis and proof remain required"},
        {"check": "TA-06", "features": "SCB2.5-20 protrusion beyond maximum-thickness HNN-M2.5-A2 stack", "result_mm": f"{m2_5_screen_min_protrusion_mm:.4f}", "criterion": ">= 1.35 mm (3 x 0.45 mm pitch) geometric screen before screw-length tolerance", "result": "PASS NOMINAL / RECEIVED STACK OPEN", "release_effect": "received screw length frame/plate/nut stack and tool proof remain required"},
        {"check": "TA-07", "features": "MV0-C04 selected H104 holes to nearest M5 countersink envelope", "result_mm": f"{h104_to_nearest_countersink_clearance_mm:.4f}", "criterion": ">= 1.0 mm nominal feature clearance", "result": "PASS NOMINAL / RECEIVED FRAME FIT OPEN", "release_effect": "exact STEP axes are controlled; manufacturing tolerance and received H104 fit remain required"},
        {"check": "TA-08", "features": "MV0-C05 M8 head envelope to rolled S102 projected height", "result_mm": f"{support_head_to_s102_clearance_mm:.4f}", "criterion": ">= 3.0 mm nominal wrench/head clearance outside S102 envelope", "result": "PASS NOMINAL / TOOL PROOF OPEN", "release_effect": "received head, frame envelope, wrench access and cable clearance remain required"},
    ]
    write_csv(OUT / "tool-access-screen.csv", access_rows)

    load_rows = [
        {"screen": "LS-01", "item": "M5 end-tap bolt couple", "input": f"{shoulder_screen_nm:.4f} N m / {END_TAP_SPACING:.1f} mm", "result": f"{m5_couple_force_n:.2f} N", "basis": "no clamp-friction credit; already includes 2.25 screening multiplier", "status": "STATIC SCREEN PASS; PROOF OPEN"},
        {"screen": "LS-02", "item": "6063-T6 internal-thread shear", "input": f"4.19 mm core; {m5_engagement_mm:.4f} mm engagement; 0.5 circumference; 0.577 x 172.37 MPa", "result": f"{thread_shear_capacity_n:.1f} N capacity / {thread_shear_capacity_n / m5_couple_force_n:.1f} ratio", "basis": "conservative project inference from published yield; ignores preload, fatigue and countersink pull-through", "status": "STATIC SCREEN PASS; PHYSICAL PROOF OPEN"},
        {"screen": "LS-03", "item": "20-2040 strong-axis bending stress", "input": f"M={shoulder_screen_nm:.4f} N m; c=20 mm; I=4.5357 cm^4", "result": f"{beam_bending_stress_mpa:.4f} MPa / 172.37 MPa published yield", "basis": "purchased-section global bending only", "status": "STATIC SCREEN PASS; JOINT/DEFLECTION/FATIGUE OPEN"},
        {"screen": "LS-04", "item": "adapter countersink punching-shear demand", "input": f"{m5_couple_force_n:.2f} N / (pi x {END_HOLE_D:.2f} mm x {adapter_min_residual_mm:.3f} mm)", "result": f"{adapter_required_punching_shear_mpa:.4f} MPa demand; {kaiser_typical_shear_yield_mpa / adapter_required_punching_shear_mpa:.1f} ratio to Kaiser typical T651 shear-yield inference", "basis": "9.0 mm finished minimum and 3.1 mm max countersink; comparison uses typical 276 MPa yield from Kaiser Rev 05/06, not a minimum allowable", "status": "INDICATIVE STATIC SCREEN PASS; CERTIFICATE/PROOF OPEN"},
        {"screen": "LS-05", "item": "adapter countersunk-head annular average pressure", "input": f"{m5_couple_force_n:.2f} N / annulus({END_CSK_D_MIN:.2f} mm head min, {END_HOLE_D:.2f} mm hole)", "result": f"{adapter_head_average_pressure_mpa:.4f} MPa average pressure; {kaiser_typical_yield_mpa / adapter_head_average_pressure_mpa:.1f} ratio to Kaiser typical T651 yield", "basis": "average-pressure screen only; does not resolve conical contact, prying, local bending, preload, fatigue or impact", "status": "INDICATIVE STATIC SCREEN PASS; FEA/PROOF OPEN"},
    ]
    write_csv(OUT / "joint-load-screen.csv", load_rows)

    adapter_control_rows = [
        {"control_id": "ADP-001", "feature": "finished outside width X", "nominal_mm": "48.00", "tolerance_or_limit": "+/-0.10", "inspection": "calibrated caliper or CMM; record actual", "status": "CANDIDATE CONTROL; FAI REQUIRED"},
        {"control_id": "ADP-002", "feature": "finished outside height Z", "nominal_mm": "40.00", "tolerance_or_limit": "+/-0.10", "inspection": "calibrated caliper or CMM; record actual", "status": "CANDIDATE CONTROL; FAI REQUIRED"},
        {"control_id": "ADP-003", "feature": "finished thickness Y", "nominal_mm": "9.525", "tolerance_or_limit": "9.00 minimum / 10.00 maximum", "inspection": "micrometer at four corners and center", "status": "CANDIDATE CONTROL; FAI REQUIRED"},
        {"control_id": "ADP-004", "feature": "four M2.5 clearance holes", "nominal_mm": "diameter 2.70 at X +/-16.00 Z +/-8.00", "tolerance_or_limit": "diameter +0.10/-0.00; each center coordinate +/-0.05", "inspection": "pin gauges plus CMM or optical comparator", "status": "CANDIDATE CONTROL; FAI REQUIRED; RECEIVED FRAME FIT REQUIRED"},
        {"control_id": "ADP-005", "feature": "two M5 clearance holes", "nominal_mm": "diameter 5.50 at X 0 Z +/-10.00", "tolerance_or_limit": "diameter +0.10/-0.00; each center coordinate +/-0.05", "inspection": "pin gauges plus CMM or optical comparator", "status": "CANDIDATE CONTROL; FAI REQUIRED; RECEIVED END-TAP FIT REQUIRED"},
        {"control_id": "ADP-006", "feature": "two M5 countersinks", "nominal_mm": "diameter 11.30; 90 degree included nominal", "tolerance_or_limit": "diameter +0.10/-0.00; received head proud <=0.05 and recess <=0.25", "inspection": "CMM/optical plus received SHKL-M5-20-A2-R360 functional gauge", "status": "CANDIDATE CONTROL; FAI REQUIRED"},
        {"control_id": "ADP-007", "feature": "residual below countersink", "nominal_mm": "not applicable", "tolerance_or_limit": ">=5.80", "inspection": "derive from measured thickness and countersink depth; retain raw data", "status": "CANDIDATE CONTROL; FAI REQUIRED"},
        {"control_id": "ADP-008", "feature": "broad-face flatness", "nominal_mm": "not applicable", "tolerance_or_limit": "<=0.15 over finished part", "inspection": "surface plate and indicator or CMM", "status": "CANDIDATE CONTROL; FAI REQUIRED"},
        {"control_id": "ADP-009", "feature": "opposite broad-face parallelism", "nominal_mm": "not applicable", "tolerance_or_limit": "<=0.10", "inspection": "micrometer map or CMM", "status": "CANDIDATE CONTROL; FAI REQUIRED"},
        {"control_id": "ADP-010", "feature": "edges and finish", "nominal_mm": "bare as-machined", "tolerance_or_limit": "break 0.20 to 0.50; no burrs; no coating", "inspection": "visual and edge-break gauge", "status": "CANDIDATE CONTROL; FAI REQUIRED"},
    ]
    write_csv(OUT / "adapter-drawing-controls.csv", adapter_control_rows)

    adapter_analysis_rows = [
        {"screen_id": "ADP-LC-01", "item": "proof-screen moment", "demand": f"{proof_moment_nm:.4f} N m", "capacity_or_limit": "3.0 x R57 2.25 gravity screen", "ratio": "1.0000 applied", "result": "PROJECT PROOF LOAD CANDIDATE; QUALIFIED ACCEPTANCE OPEN"},
        {"screen_id": "ADP-LC-02", "item": "M5 thread-root shear", "demand": f"{proof_m5_couple_force_n:.2f} N per screw", "capacity_or_limit": f"{m5_fastener_shear_screen_capacity_n:.1f} N from 4.0 mm project root and 0.30 x 700 MPa", "ratio": f"{m5_fastener_shear_screen_capacity_n / proof_m5_couple_force_n:.2f}", "result": "ANALYTICAL SCREEN PASS; NOT AN ALLOWABLE"},
        {"screen_id": "ADP-LC-03", "item": "M2.5 thread-root shear", "demand": f"{proof_m2_5_each_force_n:.2f} N per screw", "capacity_or_limit": f"{m2_5_fastener_shear_screen_capacity_n:.1f} N from 2.0 mm project root and 0.30 x 700 MPa", "ratio": f"{m2_5_fastener_shear_screen_capacity_n / proof_m2_5_each_force_n:.2f}", "result": "ANALYTICAL SCREEN PASS; NOT AN ALLOWABLE"},
        {"screen_id": "ADP-LC-04", "item": "adapter punching shear below M5 countersink", "demand": f"{proof_adapter_punching_shear_mpa:.4f} MPa", "capacity_or_limit": f"{0.5 * MATERIAL_PROJECT_MIN_YIELD_MPA:.1f} MPa project screen from required 240 MPa MTR yield", "ratio": f"{0.5 * MATERIAL_PROJECT_MIN_YIELD_MPA / proof_adapter_punching_shear_mpa:.2f}", "result": "ANALYTICAL SCREEN PASS; MTR/FAI/PROOF OPEN"},
        {"screen_id": "ADP-LC-05", "item": "average annular pressure under M5 head", "demand": f"{proof_adapter_head_average_pressure_mpa:.4f} MPa", "capacity_or_limit": f"{MATERIAL_PROJECT_MIN_YIELD_MPA:.1f} MPa required MTR yield", "ratio": f"{MATERIAL_PROJECT_MIN_YIELD_MPA / proof_adapter_head_average_pressure_mpa:.2f}", "result": "ANALYTICAL SCREEN PASS; CONICAL CONTACT/PROOF OPEN"},
        {"screen_id": "ADP-LC-06", "item": "M2.5 hole bearing", "demand": f"{proof_m2_5_bearing_mpa:.4f} MPa", "capacity_or_limit": f"{MATERIAL_PROJECT_MIN_YIELD_MPA:.1f} MPa required MTR yield", "ratio": f"{MATERIAL_PROJECT_MIN_YIELD_MPA / proof_m2_5_bearing_mpa:.2f}", "result": "ANALYTICAL SCREEN PASS; PHYSICAL PROOF OPEN"},
        {"screen_id": "ADP-LC-07", "item": "M2.5 edge tear-out average shear", "demand": f"{proof_m2_5_edge_tearout_mpa:.4f} MPa", "capacity_or_limit": f"{0.5 * MATERIAL_PROJECT_MIN_YIELD_MPA:.1f} MPa project screen from required 240 MPa MTR yield", "ratio": f"{0.5 * MATERIAL_PROJECT_MIN_YIELD_MPA / proof_m2_5_edge_tearout_mpa:.2f}", "result": "ANALYTICAL SCREEN PASS; PHYSICAL PROOF OPEN"},
        {"screen_id": "ADP-LC-08", "item": "adapter net-section average stress", "demand": f"{proof_adapter_net_section_mpa:.4f} MPa", "capacity_or_limit": f"{MATERIAL_PROJECT_MIN_YIELD_MPA:.1f} MPa required MTR yield", "ratio": f"{MATERIAL_PROJECT_MIN_YIELD_MPA / proof_adapter_net_section_mpa:.2f}", "result": "ANALYTICAL SCREEN PASS; PHYSICAL PROOF OPEN"},
        {"screen_id": "ADP-LC-09", "item": "20-2040 M5 internal-thread shear", "demand": f"{proof_m5_couple_force_n:.2f} N", "capacity_or_limit": f"{thread_shear_capacity_n:.1f} N R56 conservative inferred capacity", "ratio": f"{thread_shear_capacity_n / proof_m5_couple_force_n:.2f}", "result": "ANALYTICAL SCREEN PASS; RECEIVED THREAD/PROOF OPEN"},
        {"screen_id": "ADP-LC-10", "item": "20-2040 strong-axis bending", "demand": f"{beam_bending_stress_mpa * PROOF_MULTIPLIER:.4f} MPa", "capacity_or_limit": "172.37 MPa published profile yield", "ratio": f"{172.37 / (beam_bending_stress_mpa * PROOF_MULTIPLIER):.2f}", "result": "ANALYTICAL SCREEN PASS; JOINT/DEFLECTION/FATIGUE OPEN"},
    ]
    write_csv(OUT / "adapter-proof-analysis.csv", adapter_analysis_rows)
    new_interface_control_rows = [
        {"control_id": "C04-001", "part_id": "MV0-C04", "feature": "finished envelope", "nominal_mm": "48.00 x 40.00 x 9.525", "tolerance_or_limit": "width/height +/-0.10; thickness 9.00 to 10.00", "inspection": "CMM/caliper plus five-point micrometer map", "status": "CANDIDATE CONTROL; FAI REQUIRED"},
        {"control_id": "C04-002", "part_id": "MV0-C04", "feature": "four H104 clearance holes", "nominal_mm": "diameter 2.70 at X/Z (-11,+8),(+11,+8),(-12,-6),(+12,-6)", "tolerance_or_limit": "diameter +0.10/-0.00; coordinates +/-0.05", "inspection": "pin gauges plus CMM; dry fit received H104", "status": "EXACT STEP-AXIS CANDIDATE; FAI/FIT REQUIRED"},
        {"control_id": "C04-003", "part_id": "MV0-C04", "feature": "two M5 clearance/countersink holes", "nominal_mm": "diameter 5.50 and countersink 11.30 at X=0 Z=+/-10", "tolerance_or_limit": "hole +0.10/-0.00; countersink +0.10/-0.00; 90 deg nominal", "inspection": "pin/CMM/optical plus received M5 functional gauge", "status": "CANDIDATE CONTROL; FAI REQUIRED"},
        {"control_id": "C04-004", "part_id": "MV0-C04", "feature": "broad faces and finish", "nominal_mm": "bare as-machined", "tolerance_or_limit": "flatness <=0.15; parallelism <=0.10; edge break 0.20 to 0.50; burr-free", "inspection": "surface plate/CMM and visual", "status": "CANDIDATE CONTROL; FAI REQUIRED"},
        {"control_id": "C04-005", "part_id": "MV0-C04", "feature": "received H104 registration", "nominal_mm": "all four selected axes accept received frame without forced alignment", "tolerance_or_limit": "no filing, slotting, bending or substitution", "inspection": "documented dry fit with fasteners loose; preserve photos and deviations", "status": "PHYSICAL FIT REQUIRED"},
        {"control_id": "C05-001", "part_id": "MV0-C05", "feature": "finished envelope", "nominal_mm": "48.00 x 80.00 x 9.525", "tolerance_or_limit": "width/height +/-0.10; thickness 9.00 to 10.00", "inspection": "CMM/caliper plus five-point micrometer map", "status": "CANDIDATE CONTROL; FAI REQUIRED"},
        {"control_id": "C05-002", "part_id": "MV0-C05", "feature": "four S102 clearance holes", "nominal_mm": "diameter 2.70 at X=+/-16 Z=+/-8", "tolerance_or_limit": "diameter +0.10/-0.00; coordinates +/-0.05", "inspection": "pin gauges plus CMM; dry fit received S102", "status": "EXACT STEP-AXIS CANDIDATE; FAI/FIT REQUIRED"},
        {"control_id": "C05-003", "part_id": "MV0-C05", "feature": "two column-slot clearance holes", "nominal_mm": "diameter 8.50 at X=0 Z=+/-30", "tolerance_or_limit": "diameter +0.10/-0.00; coordinates +/-0.05", "inspection": "pin gauges plus CMM; dry fit received 17-8520/13035/40-4040", "status": "CANDIDATE CONTROL; FAI/FIT REQUIRED"},
        {"control_id": "C05-004", "part_id": "MV0-C05", "feature": "broad faces and finish", "nominal_mm": "bare as-machined", "tolerance_or_limit": "flatness <=0.15; parallelism <=0.10; edge break 0.20 to 0.50; burr-free", "inspection": "surface plate/CMM and visual", "status": "CANDIDATE CONTROL; FAI REQUIRED"},
        {"control_id": "C05-005", "part_id": "MV0-C05", "feature": "column/S102 dry-fit alignment", "nominal_mm": "plate seats on column face and rolled S102 face without forced alignment", "tolerance_or_limit": "no filing, slotting, bending or substitution", "inspection": "documented dry fit with fasteners loose; preserve photos and deviations", "status": "PHYSICAL FIT REQUIRED"},
    ]
    write_csv(OUT / "new-interface-drawing-controls.csv", new_interface_control_rows)

    support_analysis_rows = [
        {"screen_id": "SUP-LC-01", "item": "proof-screen moment", "demand": f"{proof_moment_nm:.4f} N m", "capacity_or_limit": "same 3.0 x R57 2.25-gravity shoulder screen", "ratio": "1.0000 applied", "result": "PROJECT PROOF LOAD CANDIDATE; QUALIFIED ACCEPTANCE OPEN"},
        {"screen_id": "SUP-LC-02", "item": "M8 vertical couple", "demand": f"{support_m8_couple_force_n:.2f} N at 60.0 mm spacing", "capacity_or_limit": "T-slot pullout/slip capacity not published for this application", "ratio": "SELECTION REQUIRED", "result": "PHYSICAL PROOF AND QUALIFIED ANALYSIS REQUIRED"},
        {"screen_id": "SUP-LC-03", "item": "MV0-C05 M8-hole average bearing", "demand": f"{support_m8_bearing_mpa:.4f} MPa", "capacity_or_limit": f"{MATERIAL_PROJECT_MIN_YIELD_MPA:.1f} MPa required MTR yield", "ratio": f"{MATERIAL_PROJECT_MIN_YIELD_MPA / support_m8_bearing_mpa:.2f}", "result": "ANALYTICAL SCREEN PASS; PRYING/PRELOAD/PROOF OPEN"},
        {"screen_id": "SUP-LC-04", "item": "MV0-C05 net-section average stress", "demand": f"{support_net_section_mpa:.4f} MPa", "capacity_or_limit": f"{MATERIAL_PROJECT_MIN_YIELD_MPA:.1f} MPa required MTR yield", "ratio": f"{MATERIAL_PROJECT_MIN_YIELD_MPA / support_net_section_mpa:.2f}", "result": "ANALYTICAL SCREEN PASS; LOCAL BENDING/FATIGUE/PROOF OPEN"},
        {"screen_id": "SUP-LC-05", "item": "40-4040 column global bending", "demand": f"{column_bending_stress_mpa:.4f} MPa", "capacity_or_limit": "172.37 MPa live-page published yield", "ratio": f"{172.37 / column_bending_stress_mpa:.2f}", "result": "GLOBAL SCREEN PASS; T-SLOT/JOINT/DEFLECTION/PROOF OPEN"},
        {"screen_id": "SUP-LC-06", "item": "S102/MV0-C05 M2.5 row", "demand": f"{proof_m2_5_each_force_n:.2f} N per screw at 16 mm row spacing", "capacity_or_limit": "shares existing adapter M2.5 analytical screen", "ratio": f"{m2_5_fastener_shear_screen_capacity_n / proof_m2_5_each_force_n:.2f}", "result": "ANALYTICAL SCREEN PASS; RECEIVED STACK/PROOF OPEN"},
    ]
    write_csv(OUT / "column-support-analysis.csv", support_analysis_rows)
    summary = {
        "revision": REVISION,
        "warning": WARNING,
        "disposition": "integrated exact-coordinate arm/column candidate with closed source geometry at A00 through A07; material, received fit, physical proof, hard-stop, cable, guard and qualified release gates remain open; no part or assembly released",
        "vendor_source_sha256": {name: sha256(VENDOR / name) for name in ("XMHD-540.N101.I101.STP", "FR13-H101K.stp", "FR13-S102K.stp", "FR12-H104K.stp")},
        "vendor_8020_source_sha256": {name: sha256(VENDOR_8020 / name) for name in ("20-2040-endview.svg", "20-2040-dimensions.jpg", "20-2040-30mm.EPRT")},
        "candidate_geometry_mm": {
            "j1_to_j2_axis": round(J2_Y, 4),
            "j2_to_g1_frame_origin": round(G1_Y - J2_Y, 4),
            "j1_to_g1_frame_origin": round(G1_Y, 4),
            "adapter_thickness": PLATE_T,
            "adapter_finished_thickness_range": [PLATE_MIN_T, PLATE_MAX_T],
            "adapter_envelope": [48.0, PLATE_T, 40.0],
            "gripper_adapter_envelope": [48.0, PLATE_T, 40.0],
            "shoulder_support_envelope": [48.0, PLATE_T, SUPPORT_PLATE_H],
            "upper_beam_envelope": [20.0, UPPER_BEAM_L, 40.0],
            "forearm_beam_envelope": [20.0, FOREARM_BEAM_L, 40.0],
            "reserved_g1_to_object_center_max": round(360.0 - G1_Y, 4),
            "robotis_rectangular_pattern": {"x_centers": [-16.0, 16.0], "z_centers": [-8.0, 8.0], "hole_diameter": FRAME_HOLE_D},
            "profile_end_tap_centers": {"x": 0.0, "z_centers": [-10.0, 10.0], "core_diameter": 4.19},
            "m5_countersink": {"finished_diameter_range": [END_CSK_D_NOM, END_CSK_D], "modeled_maximum_diameter": END_CSK_D, "maximum_depth_screen": END_CSK_DEPTH, "included_angle_deg_nominal": 90.0},
            "h104_selected_local_axes_xz": [list(axis) for axis in H104_SELECTED_AXES_LOCAL_XZ],
            "support_m8_axes_xz": [[0.0, -30.0], [0.0, 30.0]],
            "column_center_local_y": COLUMN_CENTER_Y,
            "j1_a0_transform_mm": [J1_A0_X, J1_A0_Y, J1_A0_Z],
        },
        "actuator_axis_registration": {
            "matrix_3x3": [[0, 0, -1], [1, 0, 0], [0, -1, 0]],
            "raw_output_axis": [0, 0, 1],
            "joint_output_axis": [-1, 0, 0],
            "raw_bottom_mount_axes": [[13.5, -41.5], [-13.5, -41.5]],
            "registered_s102_axes_yz": [[13.5, 41.5], [-13.5, 41.5]],
            "axial_translation_x_mm": ACTUATOR_AXIAL_OFFSET_X,
            "axial_translation_status": "candidate display placement; received horn/idler stack measurement required",
        },
        "axis_parallelism_math": {"j1_direction": [1, 0, 0], "j2_direction": [1, 0, 0], "dot_product": 1.0, "angular_difference_deg": 0.0},
        "reference_output_offset_deg": -90.0,
        "collision_screen": {"sampled_j1_range_deg": [-20, 70], "sampled_j2_range_deg": [15, 125], "increment_deg": COLLISION_INCREMENT_DEG, "sample_count": len(sweep_rows), "provisional_soft_limit_deg": PROVISIONAL_J2_SOFT_LIMIT_DEG, "candidate_positive_hard_stop_datum_deg": CANDIDATE_J2_POSITIVE_HARD_STOP_DEG, "continuous_analysis_j2_max_deg": CONTINUOUS_ANALYSIS_J2_MAX_DEG, "continuous_minimum_guaranteed_clearance_mm": round(continuous_minimum_guaranteed_mm, 6), "continuous_first_nominal_contact_j2_deg": round(continuous_first_contact_deg, 6), "candidate_soft_to_stop_allowance_deg": round(soft_to_stop_deg, 6), "candidate_stop_to_contact_margin_deg": round(stop_to_contact_deg, 6), "reserved_nominal_collision_guard_deg": CANDIDATE_CONTACT_GUARD_DEG, "candidate_physical_uncertainty_budget_deg": round(candidate_physical_budget_deg, 6), "first_sampled_positive_volume_collision_j2_deg": first_nominal_collision_deg, "maximum_positive_intersection_mm3_full_requested_range": round(worst, 6), "maximum_positive_intersection_mm3_within_provisional_limit": round(max_intersection_within_limit, 6), "scope": "continuous adaptive nominal model-space separation certificate covers all 70 non-intentional body pairs through J2=120 deg; sampled exact-boolean sweep continues through J2=125 deg; cables, guards, tolerances, deformation, physical stops, stopping travel and qualified acceptance remain open"},
        "mass_and_load_screen": {
            "20_2040_mass_basis_kg_per_m": round(mass_per_m_kg, 6),
            "one_100mm_upper_beam_mass_g": round(upper_beam_mass_g, 3),
            "one_50mm_forearm_beam_mass_g": round(forearm_beam_mass_g, 3),
            "one_adapter_candidate_mass_g": round(plate_mass_g, 3),
            "gripper_adapter_candidate_mass_g": round(gripper_plate_mass_g, 3),
            "shoulder_support_candidate_mass_g": round(support_plate_mass_g, 3),
            "upper_beam_plus_two_adapters_mass_g": round(upper_link_mass_g, 3),
            "forearm_beam_plus_two_adapters_mass_g": round(forearm_link_mass_g, 3),
            "allocated_shoulder_gravity_nm": round(shoulder_nm, 3),
            "allocated_elbow_gravity_nm": round(elbow_nm, 3),
            "screening_multiplier": 2.25,
            "shoulder_screen_nm": round(shoulder_screen_nm, 3),
            "elbow_screen_nm": round(elbow_nm * 2.25, 3),
            "status": "screen only; received masses, COM, inertia, continuous torque and thermal proof required",
        },
        "nominal_joint_screens": {
            "nearest_m5_countersink_to_m2_5_hole_clearance_mm": round(feature_clearance_mm, 4),
            "m5_thread_engagement_mm": round(m5_engagement_mm, 4),
            "m5_min_thread_engagement_screen_mm": round(m5_min_engagement_mm, 4),
            "m2_5_nominal_protrusion_mm": round(m2_5_nominal_protrusion_mm, 4),
            "m2_5_geometric_min_protrusion_screen_mm": round(m2_5_screen_min_protrusion_mm, 4),
            "m5_couple_force_n": round(m5_couple_force_n, 2),
            "inferred_internal_thread_shear_capacity_n": round(thread_shear_capacity_n, 1),
            "20_2040_strong_axis_bending_stress_mpa": round(beam_bending_stress_mpa, 4),
            "adapter_min_residual_below_countersink_mm": round(adapter_min_residual_mm, 4),
            "adapter_punching_shear_demand_mpa": round(adapter_required_punching_shear_mpa, 4),
            "adapter_head_annular_average_pressure_mpa": round(adapter_head_average_pressure_mpa, 4),
            "proof_screen_multiplier_on_2_25_gravity_case": PROOF_MULTIPLIER,
            "proof_screen_moment_nm": round(proof_moment_nm, 4),
            "proof_m5_couple_force_n": round(proof_m5_couple_force_n, 2),
            "proof_m2_5_each_force_n": round(proof_m2_5_each_force_n, 2),
            "proof_adapter_punching_shear_mpa": round(proof_adapter_punching_shear_mpa, 4),
            "proof_adapter_head_annular_average_pressure_mpa": round(proof_adapter_head_average_pressure_mpa, 4),
            "proof_m2_5_bearing_mpa": round(proof_m2_5_bearing_mpa, 4),
            "project_mtr_minimum_yield_mpa": MATERIAL_PROJECT_MIN_YIELD_MPA,
            "status": "analytical screening only; typical material properties are not allowables; controlled tolerances exist but no fatigue, preload, prying, local bending, physical proof or qualified-acceptance credit is taken",
        },
        "candidate_primary_sources": {
            "adapter_material_typical_properties": "Kaiser Aluminum Sheet Coil & Plate Alloy 6061, Rev. 05/06; typical T6/T651 yield 276 MPa; not a minimum allowable",
            "adapter_raw_stock": "OnlineMetals part 1249, 3/8 inch 6061-T651 plate, ASTM B209 / AMS 4027, MTR available; live product page accessed 2026-08-07",
            "m5_countersunk_screw": "Accu SHKL-M5-20-A2-R360, A2-70, AccuLock 360; live U.S. product page accessed 2026-08-07",
            "m2_5_socket_screw": "MISUMI SCB2.5-20, A2-70, fully threaded; live U.S. configurator accessed 2026-08-07",
            "m2_5_locknut": "Accu HNN-M2.5-A2, DIN 985 nylon-insert locking nut; live U.S. product page revision/stock record dated 2026-07-14 and accessed 2026-08-07",
            "column_profile": "80/20 40-4040, 40 x 40 mm 6063-T6 four-open-slot profile; live product page accessed 2026-08-07",
            "column_screw": "80/20 17-8520, M8 x 20 fully threaded stainless SHCS; live product page accessed 2026-08-07",
            "column_t_nut": "80/20 13035, M8 self-aligning roll-in T-nut with ball spring, 304 stainless and 40-series compatible; live product page accessed 2026-08-07",
            "column_mount_precedent": "80/20 40006-BP live product page pairs 17-8520 and 13035 for T-slot mounting; application proof remains project-specific",
            "h104_frame": "ROBOTIS FR12-H104K controlled STEP and Aug-31-17 drawing; selected exact axes recorded in interface-feature-evidence.csv",
            "s102_frame": "ROBOTIS FR13-S102K controlled STEP and 2026-01-07 drawing; selected exact axes recorded in interface-feature-evidence.csv",
        },
        "open_release_items": [
            "supplier confirmation and received inspection for 20-2040 two-hole M5 end-tap service",
            "separately authorized OnlineMetals 1249 receipt with one heat lot, MTR review against the project 240 MPa minimum-yield acceptance and stock inspection",
            "qualified supplier DFM acceptance of the P0.5 adapter/support controls and one separately authorized first article per custom geometry",
            "received SCB2.5-20/HNN-M2.5-A2 stack, screw-length tolerance, prevailing/installation torque, single-use rule, wrench envelope and proof",
            "received SHKL-M5-20-A2-R360 identity, full-thread condition, seating, torque/cure/storage method, single-install rule and physical proof",
            "received horn/idler axial stack and complete actuator/frame assembly fit",
            "received MV0-C04/H104 and MV0-C05/S102/40-4040 fit with complete exact fastener stacks",
            "17-8520/13035 engagement, anti-galling, installation torque, T-slot pullout/slip/prying and column-support proof",
            "tool access, cable routing, connector sweep and strain relief",
            "guard, cable, tolerance, deformation and as-built collision proof beyond the continuous nominal body certificate",
            "physical J2 hard-stop design plus measured stopping overtravel, backlash, compliance, tolerance and uncertainty closure against the candidate allocation",
            "qualified acceptance of the R66 analytical equivalent or requested local FEA plus joint-slip, preload, fatigue, impact and physical proof",
            "received-part fit, first-article inspection and qualified mechanical approval",
        ],
    }
    (OUT / "architecture-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8", newline="\n")

    first_collision_label = f"{first_nominal_collision_deg:.1f} deg" if first_nominal_collision_deg is not None else "none in sampled range"
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1500" height="920" viewBox="0 0 1500 920">
<style>text{{font-family:Arial,sans-serif;fill:#082b4c;font-size:18px}}.title{{font-size:34px;font-weight:700}}.sub{{font-size:23px;font-weight:700}}.warn{{font-size:20px;font-weight:700;fill:#8a3b00}}.axis{{stroke:#0b4f8a;stroke-width:4}}.part{{fill:#66c7f4;stroke:#0b4f8a;stroke-width:3}}.frame{{fill:#f3b61f;stroke:#8a5a00;stroke-width:3}}.note{{fill:#fff4cd;stroke:#f3b61f;stroke-width:3}}</style>
<rect width="1500" height="920" fill="#f7fbff"/>
<text x="40" y="55" class="title">HR-V0 fabrication-defined exact-coordinate arm candidate</text>
<text x="40" y="92" class="warn">{REVISION} - {WARNING}</text>
<text x="40" y="145" class="sub">Straight reference pose, side elevation (Y horizontal, Z vertical)</text>
<line x1="150" y1="370" x2="1330" y2="370" stroke="#b7cad9" stroke-width="2"/>
<rect x="95" y="220" width="60" height="400" fill="#737d85" stroke="#263746" stroke-width="3"/><text x="70" y="650">40-4040 column</text>
<rect x="155" y="315" width="28" height="110" fill="#d4d8dc" stroke="#263746" stroke-width="3"/><text x="115" y="205">MV0-C05 support</text>
<circle cx="190" cy="370" r="18" fill="#0b4f8a"/><text x="155" y="420">J1 Y=0</text>
<rect x="220" y="330" width="54" height="80" class="frame"/>
<rect x="274" y="330" width="400" height="80" class="part"/><text x="300" y="315">100 mm 20-2040 vertical envelope + two 9.525 mm adapters</text>
<circle cx="714" cy="370" r="18" fill="#0b4f8a"/><text x="635" y="440">J2 Y={J2_Y:.4f}</text>
<rect x="744" y="330" width="54" height="80" class="frame"/>
<rect x="798" y="330" width="250" height="80" class="part"/><text x="840" y="315">50 mm vertical forearm member</text>
<rect x="1048" y="330" width="54" height="80" class="frame"/><text x="980" y="440">G1 Y={G1_Y:.4f}</text>
<line x1="190" y1="480" x2="714" y2="480" class="axis"/><text x="350" y="512">J1-J2 = {J2_Y:.4f} mm candidate</text>
<line x1="714" y1="550" x2="1102" y2="550" class="axis"/><text x="800" y="582">J2-G1 = {G1_Y-J2_Y:.4f} mm candidate</text>
<rect x="70" y="670" width="1360" height="220" rx="14" class="note"/>
<text x="100" y="720" class="sub">R67 continuous-clearance and J2-allocation correction</text>
<text x="100" y="760">A00 closes candidate column/J1 geometry; A07 closes the exact H104 STEP-axis subset with MV0-C04.</text>
<text x="100" y="796">17-8520/13035 and all prior fasteners remain held. No installation torque or T-slot capacity is released.</text>
<text x="100" y="832">Continuous nominal clearance certified to J2=120 deg; contact {continuous_first_contact_deg:.4f} deg. Candidate soft/stop: {PROVISIONAL_J2_SOFT_LIMIT_DEG:.0f}/{CANDIDATE_J2_POSITIVE_HARD_STOP_DEG:.0f} deg.</text>
<text x="100" y="868" class="warn">Physical stops, stopping travel, tolerances, cables, guards, MTR/FAI and qualified acceptance remain open. Do not fabricate.</text>
</svg>'''
    (OUT / "HR-V0_arm_architecture_candidate.svg").write_text(svg, encoding="utf-8", newline="\n")

    print(f"Generated {REVISION}: J1-J2 {J2_Y:.4f} mm; J2-G1 {G1_Y-J2_Y:.4f} mm; continuous contact {continuous_first_contact_deg:.6f} deg; candidate J2 soft/stop {PROVISIONAL_J2_SOFT_LIMIT_DEG:.1f}/{CANDIDATE_J2_POSITIVE_HARD_STOP_DEG:.1f} deg")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
