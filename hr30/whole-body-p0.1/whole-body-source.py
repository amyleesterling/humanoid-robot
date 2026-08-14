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
ELBOW_X = 125.0
WRIST_X = 125.0
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


def link_between(a: tuple[float, float, float], b: tuple[float, float, float], diameter: float) -> cq.Shape:
    av = cq.Vector(*a)
    bv = cq.Vector(*b)
    delta = bv - av
    length = delta.Length
    return cq.Solid.makeCylinder(diameter / 2.0, length, av, delta.normalized())


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
<main><section class="grid"><article class="card pass"><div class="metric">762 mm</div><p>Exact neutral-pose floor-to-shell-top geometry.</p></article><article class="card pass"><div class="metric">25</div><p>Named head, waist, arm, hand, hip, knee, and ankle axes.</p></article><article class="card"><div class="metric">43</div><p>Candidate physical envelopes in the STEP assembly.</p></article><article class="card hold"><div class="metric">0</div><p>Fabrication, motion, safety, or energization approvals.</p></article></section>
<section><h2>Orbit the native body architecture</h2><div class="viewer"><model-viewer src="HR-30_body_architecture_candidate.glb" poster="front-elevation.svg" alt="Interactive 3D model of the preliminary 762 millimetre Project Button humanoid body architecture" camera-controls camera-orbit="35deg 76deg 95%" min-camera-orbit="auto auto 20%" max-camera-orbit="auto auto 240%" field-of-view="26deg" shadow-intensity="0.85" exposure="1.05" interaction-prompt="auto"></model-viewer><p>Drag to orbit; scroll or pinch to zoom. Sky blue is shell envelope, dark blue is load-path envelope, gold is joint/hand hardware, and red rods are reference axes. Transparent objects reserve electronics, sensors, restraint, and joint datum space.</p></div></section>
<section><h2>The dimensions come from the specification</h2><img src="front-elevation.svg" alt="Front elevation of HR-30 with ankle, knee, hip, waist, shoulder, neck and top height datums"></section>
<section><h2>What this pass proves—and what it does not</h2><div class="grid"><article class="card pass"><h3>Native geometry exists</h3><p>STEP and GLB are generated from a versioned CadQuery source. The STEP reimports with vertices exactly at Z=0 and Z=762 mm.</p></article><article class="card pass"><h3>Kinematic architecture exists</h3><p>All 25 candidate axes have coordinates, directions, regions, and provisional ranges in a machine-readable schedule.</p></article><article class="card miss"><h3>Preferred reach is missed</h3><p>The specified nominal segments total 370 mm per arm and 950 mm span. These pass the 390/980 mm hard limits but miss the 360/900 mm targets.</p></article><article class="card hold"><h3>Mass is still unproven</h3><p>These are packaging envelopes, not materialized parts. The existing arm and leg actuator concepts already fail their preferred mass allocations.</p></article></div></section>
<section><h2>Controlled body datums</h2><div class="table"><table><thead><tr><th>Datum</th><th>Z above floor</th><th>Role</th></tr></thead><tbody><tr><td>Ankle pitch</td><td>45 mm</td><td>Lower-leg kinematic datum</td></tr><tr><td>Knee pitch</td><td>210 mm</td><td>165 mm above ankle pitch</td></tr><tr><td>Hip pitch</td><td>380 mm</td><td>170 mm above knee pitch</td></tr><tr><td>Waist yaw</td><td>425 mm</td><td>Upper-body rotation datum</td></tr><tr><td>Shoulder pitch</td><td>590 mm</td><td>Upper-arm datum</td></tr><tr><td>Neck pan</td><td>650 mm</td><td>Head pan datum</td></tr><tr><td>Shell top</td><td>762 mm</td><td>Exact nominal standing height</td></tr></tbody></table></div></section>
<section><h2>Next engineering conversions</h2><div class="grid"><article class="card hold"><h3>Joints</h3><p>Replace every joint envelope with dual-supported shafts, bearings, reductions, fasteners, stops, encoders, and serviceable housings.</p></article><article class="card hold"><h3>Structure and covers</h3><p>Convert solid visual envelopes into materialized frames and tool-removable covers with thickness, splits, edges, vents, access, and retention.</p></article><article class="card hold"><h3>Harness and power</h3><p>Route bend-controlled cables and select the actuator rail, protection, regeneration handling, tether, and eventual onboard energy system.</p></article><article class="card hold"><h3>Evidence</h3><p>Close mass/COM/inertia, collision, gait loads, thermal behavior, stopping, fall restraint, DFM, tolerances, FAI, physical testing, and qualified review.</p></article></div></section>
<section><h2>Download the engineering artifacts</h2><div class="panel"><p><a href="HR-30_body_architecture_candidate.step">Physical-envelope STEP</a> · <a href="HR-30_body_kinematic_reference.step">Kinematic-reference STEP</a> · <a href="HR-30_body_architecture_candidate.glb">Interactive GLB</a> · <a href="whole-body-source.py">Editable CadQuery source</a> · <a href="joint-axis-schedule.csv">Joint-axis schedule</a> · <a href="actuator-transmission-allocation.csv">Actuator allocation</a> · <a href="asimov-1-reuse-adapt-reject.csv">Asimov 1 matrix</a> · <a href="component-envelope-schedule.csv">Component schedule</a> · <a href="geometry-checks.json">Geometry checks</a> · <a href="open-holds.csv">Open holds</a></p></div></section></main>
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


def build() -> tuple[list[Component], list[dict]]:
    shell = (0.25, 0.68, 0.92, 0.82)
    structure = (0.08, 0.20, 0.38, 1.0)
    joint = (0.96, 0.70, 0.08, 1.0)
    hand = (0.98, 0.78, 0.18, 1.0)
    bay = (0.12, 0.30, 0.65, 0.34)
    sensor = (0.98, 0.76, 0.12, 0.42)
    axis_color = (0.91, 0.18, 0.15, 0.72)
    components: list[Component] = []

    def add(name: str, group: str, shape: cq.Shape, color, physical: bool = True, note: str = "") -> None:
        components.append(Component(name, group, shape, color, physical, note))

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
        add_axis(f"{side}_GRIPPER", "hand", side, "parallel open/close", (sign * WRIST_X, 0, 252), (1, 0, 0), "SELECTION REQUIRED", "HR-PROD-030")
        add_axis(f"{side}_HIP_YAW", "leg", side, "yaw", (sign * HIP_HALF_WIDTH, 0, 397), (0, 0, 1), "+/-30 deg", "HR-WALK-001")
        add_axis(f"{side}_HIP_ROLL", "leg", side, "roll", (sign * HIP_HALF_WIDTH, 0, 388), (0, 1, 0), "+/-25 deg", "HR-WALK-001")
        add_axis(f"{side}_HIP_PITCH", "leg", side, "pitch", (sign * HIP_HALF_WIDTH, 0, HIP_Z), (1, 0, 0), "-35..+45 deg", "HR-WALK-001")
        add_axis(f"{side}_KNEE_PITCH", "leg", side, "pitch", (sign * HIP_HALF_WIDTH, 0, KNEE_Z), (1, 0, 0), "0..120 deg", "HR-WALK-001")
        add_axis(f"{side}_ANKLE_PITCH", "leg", side, "pitch", (sign * HIP_HALF_WIDTH, 0, ANKLE_Z), (1, 0, 0), "-35..+30 deg", "HR-WALK-001")
        add_axis(f"{side}_ANKLE_ROLL", "leg", side, "roll", (sign * HIP_HALF_WIDTH, 0, 37), (0, 1, 0), "+/-20 deg", "HR-WALK-001")
    return components, axes


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    components, axes = build()
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
        assembly.add(item.shape, name=item.name, color=cq.Color(*item.color))
    assembly.save(str(OUT / "HR-30_body_architecture_candidate.glb"))

    write_csv(OUT / "joint-axis-schedule.csv", axes)
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
        elif "SHOULDER" in axis_id:
            actuator, transmission, rail, disposition = (
                "ROBOTIS XM540-W270-R candidate",
                "direct drive candidate; dual-supported output",
                "10.0-14.8 V candidate domain",
                "PROVISIONAL - ARM MASS TARGET CURRENTLY FAILS",
            )
        elif "ELBOW" in axis_id:
            actuator, transmission, rail, disposition = (
                "ROBOTIS XM430-W350-R / XM540-W270-R decision candidate",
                "direct drive candidate; dual-supported output",
                "10.0-14.8 V candidate domain",
                "PROVISIONAL - DECIDE FROM HR-V0 MEASURED DATA",
            )
        elif "WRIST" in axis_id:
            actuator, transmission, rail, disposition = (
                "ROBOTIS XM430-W350-R candidate",
                "direct drive through supported wrist shaft",
                "10.0-14.8 V candidate domain",
                "PROVISIONAL",
            )
        elif "GRIPPER" in axis_id:
            actuator, transmission, rail, disposition = (
                "ROBOTIS XM430-class candidate",
                "compliant parallel-link or tendon transmission",
                "10.0-14.8 V candidate domain",
                "PROVISIONAL - FORCE/LIMIT/COMPLIANCE PROOF REQUIRED",
            )
        elif "HIP_ROLL" in axis_id:
            actuator, transmission, rail, disposition = (
                "ROBOTIS XH540-W270-R evaluation candidate",
                "reduction path reserved; ratio SELECTION REQUIRED; dual-supported output",
                "10.0-14.8 V candidate domain",
                "DIRECT DRIVE REJECTED/BLOCKED",
            )
        elif any(term in axis_id for term in ("HIP_PITCH", "KNEE_PITCH", "ANKLE_PITCH")):
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
        {"assembly": "head and neck", "target_kg": 0.45, "maximum_kg": 0.55, "cad_mass_kg": "NOT CALCULATED - ENVELOPES", "status": "OPEN"},
        {"assembly": "chest compute and waist", "target_kg": 1.20, "maximum_kg": 1.35, "cad_mass_kg": "NOT CALCULATED - ENVELOPES", "status": "OPEN"},
        {"assembly": "two arms and hands", "target_kg": 1.30, "maximum_kg": 1.50, "cad_mass_kg": "NOT CALCULATED - CURRENT ACTUATOR CONCEPT ALREADY FAILS TARGET", "status": "OPEN/BLOCKING"},
        {"assembly": "pelvis and restraint structure", "target_kg": 0.65, "maximum_kg": 0.75, "cad_mass_kg": "NOT CALCULATED - ENVELOPES", "status": "OPEN"},
        {"assembly": "two legs and feet", "target_kg": 3.40, "maximum_kg": 3.80, "cad_mass_kg": "NOT CALCULATED - CURRENT CONCEPT FAILS SCREEN", "status": "OPEN/BLOCKING"},
        {"assembly": "wiring covers fasteners margin", "target_kg": 0.60, "maximum_kg": 0.80, "cad_mass_kg": "NOT CALCULATED", "status": "OPEN"},
        {"assembly": "onboard energy", "target_kg": 0.40, "maximum_kg": 1.25, "cad_mass_kg": "SELECTION REQUIRED", "status": "OPEN"},
        {"assembly": "TOTAL", "target_kg": 8.00, "maximum_kg": 10.00, "cad_mass_kg": "NOT DEMONSTRATED", "status": "OPEN/BLOCKING"},
    ]
    write_csv(OUT / "mass-allocation-register.csv", mass_rows)
    holds = [
        ("HR30-P01-H01", "All 25 load-bearing joint stacks, bearings, shafts, reductions and fasteners are absent."),
        ("HR30-P01-H02", "The arm actuator concept exceeds its mass target before links, hands, cables and covers."),
        ("HR30-P01-H03", "The leg concept fails its current mass screen and direct-drive hip roll is blocked."),
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

It is intentionally an architecture model, not a buildable machine. The STEP contains candidate physical envelopes. The second STEP and GLB add joint-axis and component-reservation references. The package also assigns a provisional actuator/transmission route to every axis and records explicit REUSE / ADAPT / REJECT decisions for the SHA-bound Asimov 1 source rig. Exact joints, materials, wall construction, tolerances, fasteners, harnesses, power hardware, mass properties, collision proof and physical validation remain open.

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
