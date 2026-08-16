"""Generate exact-candidate HR-30 reduced-leg drivetrain modules.

This package replaces ratio-only 5 mm-pitch belt concepts with purchasable
pulley/belt candidates, solved pitch-center geometry, editable CAD envelopes,
and all-ten-axis allocation.  It remains preliminary: torque capacity,
tension, horn adapters, fits, fatigue, guarding and physical proof stay open.
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
PACKAGE = ROOT / "hr30" / "whole-body-p0.1"
OUT = PACKAGE / "leg-drivetrain-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / "leg-drivetrain-p0.1"
IDENTIFIER = "HR30-REDUCED-LEG-DRIVETRAIN-P0.1"
WARNING = "PRELIMINARY - PRODUCT/GEOMETRY CANDIDATE ONLY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, POWERED TESTING, MOTION, OR ENERGIZATION"
PITCH_MM = 5.0
BELT_WIDTH_MM = 9.0
BELT_BODY_THICKNESS_MM = 3.8

sys.path.insert(0, str(ROOT / "tools"))
import generate_hr30_body_architecture_p01 as body  # noqa: E402
import generate_hr30_system_package_p01 as system  # noqa: E402


@dataclass(frozen=True)
class Drive:
    drive_id: str
    family_id: str
    motor_teeth: int
    output_teeth: int
    belt_teeth: int
    motor_bore_mm: float
    motor_pulley_code: str
    output_pulley_code: str
    belt_code: str
    actuator_family: str
    horn_code: str
    axis_ids: tuple[str, ...]


DRIVES = (
    Drive("LD-15", "JMF-07-LEG-REDUCED-15", 20, 30, 45, 10.0, "GPA20GT5090-A-P10", "GPA30GT5090-A-P12", "GBN225EV5GT-090", "XH540", "HN13-N101 / SKU 903-0276-000", ("L_HIP_PITCH", "R_HIP_PITCH")),
    Drive("LD-20", "JMF-08-LEG-REDUCED-20", 20, 40, 51, 10.0, "GPA20GT5090-A-P10", "GPA40GT5090-A-P12", "GBN255EV5GT-090", "XH540 or XM430 by axis", "HN13-N101 / SKU 903-0276-000 or HN12-N101 / SKU 903-0238-000", ("L_HIP_ROLL", "R_HIP_ROLL", "L_ANKLE_ROLL", "R_ANKLE_ROLL")),
    Drive("LD-25K", "JMF-09-KNEE-REDUCED-25", 16, 40, 50, 10.0, "GPA16GT5090-A-P10", "GPA40GT5090-A-P12", "GBN250EV5GT-090", "XH540", "HN13-N101 / SKU 903-0276-000", ("L_KNEE_PITCH", "R_KNEE_PITCH")),
    Drive("LD-25", "JMF-10-ANKLE-PITCH-REDUCED-25", 16, 40, 50, 8.0, "GPA16GT5090-A-P8", "GPA40GT5090-A-P12", "GBN250EV5GT-090", "XM430", "HN12-N101 / SKU 903-0238-000", ("L_ANKLE_PITCH", "R_ANKLE_PITCH")),
)

PULLEY_OD_MM = {16: 24.32, 20: 30.69, 24: 37.06, 30: 46.61, 40: 62.52}
PULLEY_FLANGE_OD_MM = {16: 29.0, 20: 35.0, 24: 42.0, 30: 51.0, 40: 67.0}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise RuntimeError(f"refusing empty CSV: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def pitch_diameter(teeth: int) -> float:
    return teeth * PITCH_MM / math.pi


def belt_length(center_mm: float, motor_teeth: int, output_teeth: int) -> float:
    d = pitch_diameter(motor_teeth)
    D = pitch_diameter(output_teeth)
    return 2.0 * center_mm + math.pi * (D + d) / 2.0 + (D - d) ** 2 / (4.0 * center_mm)


def solve_center(drive: Drive) -> float:
    target = drive.belt_teeth * PITCH_MM
    low = abs(pitch_diameter(drive.output_teeth) - pitch_diameter(drive.motor_teeth)) / 2.0 + 0.01
    high = 150.0
    for _ in range(100):
        middle = (low + high) / 2.0
        if belt_length(middle, drive.motor_teeth, drive.output_teeth) < target:
            low = middle
        else:
            high = middle
    center = (low + high) / 2.0
    if abs(belt_length(center, drive.motor_teeth, drive.output_teeth) - target) > 1e-8:
        raise RuntimeError(f"belt-center solve failed: {drive.drive_id}")
    return center


def cylinder(center_z: float, width: float, diameter: float) -> cq.Shape:
    return body.cylinder_between((0.0, 0.0, center_z), (0.0, 1.0, 0.0), width, diameter)


def pulley_envelope(teeth: int, bore_mm: float, center_z: float) -> cq.Shape:
    od = PULLEY_OD_MM[teeth]
    flange_od = PULLEY_FLANGE_OD_MM[teeth]
    tooth_width = 10.3
    hub_width = 22.0
    hub_diameter = max(bore_mm + 8.0, min(od - 2.0, bore_mm + 16.0))
    toothed = cylinder(center_z, tooth_width, od)
    hub = body.cylinder_between((0.0, tooth_width / 2.0, center_z), (0, 1, 0), hub_width - tooth_width, hub_diameter)
    flanges = cylinder(center_z, 0.8, flange_od).translate((0, -(tooth_width / 2.0 + 0.4), 0)).fuse(
        cylinder(center_z, 0.8, flange_od).translate((0, tooth_width / 2.0 + 0.4, 0))
    )
    bore = cylinder(center_z, hub_width + 2.0, bore_mm)
    return toothed.fuse(hub).fuse(flanges).cut(bore).clean()


def belt_envelope(drive: Drive, center_mm: float) -> cq.Shape:
    """Product-specific routing envelope; teeth remain represented by vendor OD."""
    r1 = pitch_diameter(drive.output_teeth) / 2.0
    r2 = pitch_diameter(drive.motor_teeth) / 2.0
    half_t = BELT_BODY_THICKNESS_MM / 2.0
    outer1 = cylinder(0.0, BELT_WIDTH_MM, 2.0 * (r1 + half_t))
    inner1 = cylinder(0.0, BELT_WIDTH_MM + 1.0, 2.0 * max(0.1, r1 - half_t))
    outer2 = cylinder(center_mm, BELT_WIDTH_MM, 2.0 * (r2 + half_t))
    inner2 = cylinder(center_mm, BELT_WIDTH_MM + 1.0, 2.0 * max(0.1, r2 - half_t))
    rings = outer1.cut(inner1).fuse(outer2.cut(inner2))

    nz = (r1 - r2) / center_mm
    nx_abs = math.sqrt(max(0.0, 1.0 - nz * nz))
    runs = []
    for sign in (-1.0, 1.0):
        nx = sign * nx_abs
        p1 = (nx * r1, nz * r1)
        p2 = (nx * r2, center_mm + nz * r2)
        vx, vz = p2[0] - p1[0], p2[1] - p1[1]
        length = math.hypot(vx, vz)
        px, pz = -vz / length * half_t, vx / length * half_t
        polygon = [(p1[0] + px, p1[1] + pz), (p2[0] + px, p2[1] + pz), (p2[0] - px, p2[1] - pz), (p1[0] - px, p1[1] - pz)]
        runs.append(cq.Workplane("XZ").polyline(polygon).close().extrude(BELT_WIDTH_MM / 2.0, both=True).val())
    return rings.fuse(runs[0]).fuse(runs[1]).clean()


def build_drive(drive: Drive) -> tuple[cq.Assembly, cq.Shape, dict]:
    center = solve_center(drive)
    motor = pulley_envelope(drive.motor_teeth, drive.motor_bore_mm, center)
    output = pulley_envelope(drive.output_teeth, 12.0, 0.0)
    belt = belt_envelope(drive, center)
    plate_width = max(PULLEY_FLANGE_OD_MM[drive.output_teeth], PULLEY_FLANGE_OD_MM[drive.motor_teeth]) + 12.0
    plate_height = center + max(PULLEY_FLANGE_OD_MM[drive.output_teeth], PULLEY_FLANGE_OD_MM[drive.motor_teeth]) / 2.0 + 10.0
    plate_center_z = (center + (PULLEY_FLANGE_OD_MM[drive.motor_teeth] - PULLEY_FLANGE_OD_MM[drive.output_teeth]) / 4.0) / 2.0
    plate = cq.Workplane("XY").box(plate_width, 5.0, plate_height).translate((0, -10.0, plate_center_z)).val()
    plate = plate.cut(cylinder(0.0, 8.0, 12.5).translate((0, -10.0, 0))).cut(cylinder(center, 8.0, drive.motor_bore_mm + 4.0).translate((0, -10.0, 0))).clean()
    guard_outer = cq.Workplane("XY").box(plate_width + 6.0, 14.0, plate_height + 6.0).translate((0, 3.0, plate_center_z)).val()
    guard_inner = cq.Workplane("XY").box(plate_width, 16.0, plate_height).translate((0, 3.0, plate_center_z)).val()
    guard = guard_outer.cut(guard_inner).clean()
    compound = cq.Compound.makeCompound([plate, output, motor, belt, guard])
    assembly = cq.Assembly(name=f"{drive.drive_id}_P01_NOT_RELEASED")
    assembly.add(plate, name="SLOTTED_CARRIER_PLATE", color=cq.Color(0.06, 0.22, 0.40, 1.0))
    assembly.add(output, name="MISUMI_OUTPUT_PULLEY_ENVELOPE", color=cq.Color(0.95, 0.55, 0.08, 1.0))
    assembly.add(motor, name="MISUMI_MOTOR_PULLEY_ENVELOPE", color=cq.Color(0.95, 0.70, 0.10, 1.0))
    assembly.add(belt, name="MISUMI_EV5GT_BELT_ROUTING_ENVELOPE", color=cq.Color(0.12, 0.15, 0.18, 1.0))
    assembly.add(guard, name="REMOVABLE_GUARD_ENVELOPE", color=cq.Color(0.40, 0.75, 0.94, 0.35))
    values = {
        "drive_id": drive.drive_id, "family_id": drive.family_id,
        "ratio": f"{drive.output_teeth / drive.motor_teeth:.6f}",
        "motor_teeth": drive.motor_teeth, "output_teeth": drive.output_teeth,
        "motor_pitch_diameter_mm": f"{pitch_diameter(drive.motor_teeth):.6f}",
        "output_pitch_diameter_mm": f"{pitch_diameter(drive.output_teeth):.6f}",
        "motor_catalog_od_mm": f"{PULLEY_OD_MM[drive.motor_teeth]:.6f}",
        "output_catalog_od_mm": f"{PULLEY_OD_MM[drive.output_teeth]:.6f}",
        "belt_teeth": drive.belt_teeth, "belt_pitch_length_mm": f"{drive.belt_teeth * PITCH_MM:.6f}",
        "solved_nominal_center_distance_mm": f"{center:.9f}",
        "recalculated_pitch_length_mm": f"{belt_length(center, drive.motor_teeth, drive.output_teeth):.9f}",
        "length_closure_error_mm": f"{abs(belt_length(center, drive.motor_teeth, drive.output_teeth) - drive.belt_teeth * PITCH_MM):.12f}",
        "candidate_center_adjustment_slot_mm": "+/-1.5 DEVELOPMENT CANDIDATE - TENSION CALCULATION OPEN",
        "cad_scope": "PRODUCT-SPECIFIC PULLEY/BELT EXTERNAL AND ROUTING ENVELOPES; VENDOR TOOTH B-REP NOT CLAIMED",
        "warning": WARNING,
    }
    return assembly, compound, values


def export_step(shape: cq.Shape, path: Path) -> None:
    cq.exporters.export(shape, str(path))
    body.canonicalize_step(path)


def diagram_svg(drive: Drive, values: dict) -> str:
    C = float(values["solved_nominal_center_distance_mm"])
    scale = 4.3
    z0 = 250.0
    x0 = 260.0
    r_out = pitch_diameter(drive.output_teeth) / 2.0 * scale
    r_motor = pitch_diameter(drive.motor_teeth) / 2.0 * scale
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="720" height="520" viewBox="0 0 720 520"><style>text{{font-family:system-ui,Segoe UI,sans-serif;fill:#132b46;font-size:16px}}.h{{font-size:26px;font-weight:800}}.n{{font-size:18px;font-weight:700}}.dim{{stroke:#075b9b;stroke-width:2;fill:none}}.belt{{stroke:#1d2733;stroke-width:12;fill:none}}.p{{fill:#f2b91d;stroke:#8a5b00;stroke-width:3}}</style><rect width="720" height="520" fill="#eff9fe"/><text x="28" y="42" class="h">{html.escape(drive.drive_id)} · {drive.motor_teeth}:{drive.output_teeth} · {drive.belt_teeth * 5} mm EV5GT</text><line x1="{x0}" y1="{z0}" x2="{x0}" y2="{z0-C*scale}" class="belt"/><circle cx="{x0}" cy="{z0}" r="{r_out}" class="p"/><circle cx="{x0}" cy="{z0-C*scale}" r="{r_motor}" class="p"/><line x1="{x0+120}" y1="{z0}" x2="{x0+120}" y2="{z0-C*scale}" class="dim"/><text x="{x0+138}" y="{z0-C*scale/2}" class="n">C = {C:.3f} mm</text><text x="28" y="420">Motor: {html.escape(drive.motor_pulley_code)}</text><text x="28" y="450">Output: {html.escape(drive.output_pulley_code)}</text><text x="28" y="480">Belt: {html.escape(drive.belt_code)} · 9 mm width</text></svg>'''


def render_index(values: list[dict]) -> str:
    cards = "".join(f'''<article><h3>{row['drive_id']} · {row['motor_teeth']}:{row['output_teeth']}</h3><p><strong>{row['ratio']}:1</strong> · {row['belt_pitch_length_mm']} mm belt · {row['solved_nominal_center_distance_mm']} mm centers.</p><p><a href="{row['drive_id']}/{row['drive_id']}_candidate.step">STEP</a> · <a href="{row['drive_id']}/{row['drive_id']}_candidate.glb">GLB</a> · <a href="{row['drive_id']}/{row['drive_id']}_layout.svg">layout</a></p></article>''' for row in values)
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 leg drivetrains P0.1</title><script type="module" src="../vendor/model-viewer.min.js"></script><style>:root{{--deep:#081e38;--navy:#123b68;--pale:#eff9fe;--gold:#f2b91d;--line:#afd5e8;--ink:#152b43}}*{{box-sizing:border-box}}html,body{{max-width:100%;overflow-x:clip}}body{{margin:0;background:var(--pale);color:var(--ink);font:17px/1.55 system-ui,Segoe UI,sans-serif}}header{{padding:34px max(20px,calc((100vw - 1200px)/2));background:var(--deep);color:white}}h1{{font-size:clamp(36px,6vw,66px);line-height:1.04}}h2{{font-size:clamp(28px,4vw,42px);color:var(--navy)}}h3{{font-size:22px;color:var(--navy)}}.warning{{padding:16px;background:var(--gold);color:#17243a;border:3px solid #8a5b00;font-weight:900}}main{{max-width:1200px;margin:auto;padding:28px 20px 80px}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:16px}}article,.viewer,.panel{{background:white;border:2px solid var(--line);border-radius:18px;padding:18px;overflow:hidden}}model-viewer{{display:block;width:100%;height:clamp(520px,70vh,760px);background:radial-gradient(circle,#fff,var(--pale))}}a{{color:#075b9b;font-weight:800}}footer{{padding:28px max(20px,calc((100vw - 1200px)/2));background:var(--deep);color:white}}@media(max-width:560px){{body{{font-size:16px}}.grid{{grid-template-columns:1fr}}}}</style></head><body><header><div class="warning">{WARNING}</div><h1>Ten reduced leg axes now point to four physical belt modules.</h1><p>Purchasable MISUMI P-bore-plus-tap pulley and belt candidates replace ratio-only transmission placeholders. The knees now use their own 16:40, 2.5:1 XH540 module so the static screen can fit below the connector-current boundary.</p></header><main><section><h2>Orbit the four-module lineup</h2><div class="viewer"><model-viewer src="HR-30_leg_drivetrain_lineup_candidate.glb" alt="Interactive lineup of four preliminary HR-30 leg belt drivetrains" camera-controls camera-orbit="140deg 70deg 110%" field-of-view="30deg" shadow-intensity="0.8"></model-viewer><p><a href="HR-30_leg_drivetrain_lineup_candidate.step">Lineup STEP</a> · <a href="axis-drivetrain-allocation.csv">ten-axis allocation</a> · <a href="candidate-product-register.csv">candidate products</a> · <a href="belt-center-geometry.csv">belt geometry</a>.</p></div></section><section><h2>Four reusable modules</h2><div class="grid">{cards}</div></section><section><h2>What this closes—and what it does not</h2><div class="panel"><p>The ratio, tooth counts, product families, nominal widths, belt lengths and center distances are coherent candidates. Nominal horn/stub/shaft adapter geometry now exists separately. The knee change is an architecture correction, not continuous-torque proof. No torque-capacity, tooth-load, belt-tension, fit, fastener, guarding, alignment, thermal, fatigue or physical validation credit follows. Product availability and written quotations must be reconfirmed before procurement.</p></div></section></main><footer>Project Button · HR-30 reduced leg drivetrain P0.1 · no procurement, fabrication, powered-test, motion or energization authority</footer></body></html>'''


def integrate_root() -> None:
    status_path = PACKAGE / "package-status.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    status.update({
        "reduced_leg_drivetrain_package_present": True,
        "reduced_leg_drivetrain_module_count": 4,
        "reduced_leg_drivetrain_axis_count": 10,
        "reduced_leg_drivetrain_candidate_products_defined": True,
        "reduced_leg_drivetrain_capacity_validated": False,
        "reduced_leg_drivetrain_horn_adapters_complete": True,
        "procurement_authority": False, "fabrication_authority": False,
        "powered_test_authority": False, "motion_authority": False, "energization_authority": False,
    })
    status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")

    readme_path = PACKAGE / "README.md"
    readme = readme_path.read_text(encoding="utf-8")
    start, end = "<!-- HR30-LEG-DRIVETRAIN-P01-README-START -->", "<!-- HR30-LEG-DRIVETRAIN-P01-README-END -->"
    if start in readme and end in readme:
        readme = readme.split(start, 1)[0] + readme.split(end, 1)[1]
    block = f'''{start}\n## Reduced-leg drivetrain product geometry\n\nThe [leg-drivetrain package](leg-drivetrain-p0.1/index.html) assigns every one of the ten belt-reduced leg axes to four editable 5GT/EV5GT modules. The knees now use a distinct 16:40, 2.5:1 XH540 module with a 10 mm horn-adapter stub; the ankles retain the separate 8 mm version. MISUMI 16/20/30/40-tooth P-bore-plus-tap pulley candidates, 225/250/255 mm by 9 mm belt candidates, solved 49.359/49.965/51.456 mm pitch centers and ROBOTIS horn-family boundaries replace the former ratio-only placeholders. Capacity, material, fits, tolerances, fasteners, tensioning, guarding and physical proof remain open.\n{end}\n'''
    marker = "<!-- HR30-ASSEMBLY-GUIDE-P01-START -->"
    readme_path.write_text(readme.replace(marker, block + marker), encoding="utf-8", newline="\n")

    page_path = PACKAGE / "index.html"
    page = page_path.read_text(encoding="utf-8")
    start, end = "<!-- HR30-LEG-DRIVETRAIN-P01-START -->", "<!-- HR30-LEG-DRIVETRAIN-P01-END -->"
    if start in page and end in page:
        page = page.split(start, 1)[0] + page.split(end, 1)[1]
    section = f'''{start}<section id="leg-drivetrains"><h2>The ten reduced leg axes now use four concrete belt-module candidates</h2><div class="grid"><article class="card pass"><div class="metric">10 axes</div><p>Hip pitch/roll, knee pitch and ankle pitch/roll are allocated bilaterally.</p></article><article class="card pass"><div class="metric">4 modules</div><p>A dedicated 2.5:1 knee module replaces the previous 2:1 knee drive; exact tooth counts, belt lengths and solved centers are encoded.</p></article><article class="card pass"><h3>Purchasable families</h3><p>MISUMI P-bore-plus-tap pulleys and EV5GT belts plus ROBOTIS X540/X430 horn families are named.</p></article><article class="card hold"><h3>Capacity remains open</h3><p>Material, fits, fasteners, tension, tooth loads, guards, fatigue and physical proof are unresolved.</p></article></div><p><a href="leg-drivetrain-p0.1/index.html">Open the leg-drivetrain guide</a> · <a href="leg-drivetrain-p0.1/axis-drivetrain-allocation.csv">axis allocation</a> · <a href="leg-drivetrain-p0.1/belt-center-geometry.csv">center geometry</a>.</p></section>{end}'''
    page_path.write_text(page.replace(marker, section + marker), encoding="utf-8", newline="\n")

    holds_path = PACKAGE / "open-holds.csv"
    with holds_path.open(encoding="utf-8", newline="") as handle:
        holds = list(csv.DictReader(handle))
    for hold in holds:
        if hold["hold_id"] == "HR30-P01-H03":
            hold["unresolved_item"] = (
                "All twelve leg axes have explicit single-support static load screens. The ten belt-reduced "
                "hip/knee/ankle axes now map to four exact MISUMI 5GT/EV5GT product candidates with solved "
                "nominal pitch centers and ROBOTIS horn-family boundaries. Exact horn-to-pulley adapters, "
                "shaft/hub retention, belt tension and capacity, accepted trajectories, continuous torque, "
                "thermal limits, inertia, contact/impact, regeneration, fall restraint, gait correlation and "
                "physical proof remain open."
            )
            break
    else:
        raise RuntimeError("controlled leg hold HR30-P01-H03 missing")
    write_csv(holds_path, holds)

    bom_path = PACKAGE / "whole-robot-candidate-bom.csv"
    with bom_path.open(encoding="utf-8", newline="") as handle:
        bom = list(csv.DictReader(handle))
    for item in bom:
        if item["item_id"] == "HR30-BOM-019":
            item["manufacturer"] = "MISUMI / project-custom adapters"
            item["candidate"] = (
                "GPA16/20/30/40GT5090 configured pulley candidates with GBN225/250/255EV5GT-090 "
                "belt candidates; exact per-axis codes in leg-drivetrain-p0.1; horn adapters, capacity, "
                "tension, guarding and retention open"
            )
            item["quantity"] = "10"
            break
    else:
        raise RuntimeError("controlled leg-reduction BOM item HR30-BOM-019 missing")
    write_csv(bom_path, bom)


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    values = []
    lineup = cq.Assembly(name="HR30_LEG_DRIVETRAIN_LINEUP_P01_NOT_RELEASED")
    lineup_shapes = []
    for index, drive in enumerate(DRIVES):
        directory = OUT / drive.drive_id
        directory.mkdir()
        assembly, compound, row = build_drive(drive)
        values.append(row)
        step = directory / f"{drive.drive_id}_candidate.step"
        glb = directory / f"{drive.drive_id}_candidate.glb"
        export_step(compound, step)
        assembly.save(str(glb), tolerance=0.12, angularTolerance=0.12)
        (directory / f"{drive.drive_id}_layout.svg").write_text(diagram_svg(drive, row), encoding="utf-8", newline="\n")
        x_shift = (index - (len(DRIVES) - 1) / 2.0) * 105.0
        shifted = compound.translate((x_shift, 0.0, 0.0))
        lineup_shapes.append(shifted)
        lineup.add(
            assembly,
            name=drive.drive_id,
            loc=cq.Location(cq.Vector(x_shift, 0.0, 0.0)),
        )
    export_step(cq.Compound.makeCompound(lineup_shapes), OUT / "HR-30_leg_drivetrain_lineup_candidate.step")
    lineup.save(str(OUT / "HR-30_leg_drivetrain_lineup_candidate.glb"), tolerance=0.16, angularTolerance=0.14)
    write_csv(OUT / "belt-center-geometry.csv", values)

    product_rows = []
    product_definitions = {}
    for drive in DRIVES:
        product_definitions[drive.motor_pulley_code] = ("MISUMI", "5GT clear-anodized aluminum pulley candidate", 1)
        product_definitions[drive.output_pulley_code] = ("MISUMI", "5GT clear-anodized aluminum pulley candidate", 1)
        product_definitions[drive.belt_code] = ("MISUMI", "EV5GT high-modulus rubber timing belt candidate", 1)
    for index, (code, (manufacturer, description, _)) in enumerate(sorted(product_definitions.items()), 1):
        quantity = sum(len(drive.axis_ids) for drive in DRIVES if code in {drive.motor_pulley_code, drive.output_pulley_code, drive.belt_code})
        product_rows.append({"product_id": f"LDP-{index:02d}", "manufacturer": manufacturer, "candidate_order_code": code, "description": description, "whole_robot_quantity": quantity, "selection_state": "EXACT CONFIGURABLE CANDIDATE - WRITTEN QUOTE/RECEIPT/LOAD VALIDATION REQUIRED", "authority": "NO PROCUREMENT AUTHORITY", "warning": WARNING})
    write_csv(OUT / "candidate-product-register.csv", product_rows)

    axis_rows = []
    for drive in DRIVES:
        for axis in drive.axis_ids:
            horn = "HN12-N101 / SKU 903-0238-000" if ("ANKLE" in axis) else "HN13-N101 / SKU 903-0276-000"
            adapter = "MA-HN12-P8" if "ANKLE_PITCH" in axis else ("MA-HN12-P10" if "ANKLE_ROLL" in axis else "MA-HN13-P10")
            axis_rows.append({"axis_id": axis, "drive_id": drive.drive_id, "ratio": f"{drive.output_teeth / drive.motor_teeth:.3f}:1", "motor_pulley": drive.motor_pulley_code, "output_pulley": drive.output_pulley_code, "belt": drive.belt_code, "actuator_horn_family": horn, "horn_to_pulley_adapter": f"{adapter} - NOMINAL CAD COMPLETE; MATERIAL/FIT/FASTENERS/PROOF OPEN", "release_state": "PRODUCT/GEOMETRY CANDIDATE - CAPACITY AND PHYSICAL VALIDATION OPEN", "warning": WARNING})
    write_csv(OUT / "axis-drivetrain-allocation.csv", axis_rows)

    sources = [
        {"source_id": "LDS-01", "source": "MISUMI High Torque Timing Pulleys - 5GT Type", "url": "https://uk.misumi-ec.com/pdf/fa/p1_1117.pdf", "revision_or_date": "current official catalog page available 2026-08-14; document revision not stated", "accessed_date": "2026-08-14", "use": "pulley order-code construction, tooth counts, bores, pitch/outside/flange dimensions and 9 mm width", "warning": WARNING},
        {"source_id": "LDS-02", "source": "MISUMI Super High Torque Timing Belts EV5GT", "url": "https://us.misumi-ec.com/pdf/fa/2019/2019_US_1432.pdf", "revision_or_date": "current official catalog PDF available 2026-08-14; document revision/date not stated", "accessed_date": "2026-08-14", "use": "225/250/255 mm EV5GT belt lengths, tooth counts, 9 mm width and compatibility boundary", "warning": WARNING},
        {"source_id": "LDS-03", "source": "ROBOTIS HN13-N101 Set", "url": "https://www.robotis.us/hn13-n101-set/", "revision_or_date": "live official product page; revision/date not stated", "accessed_date": "2026-08-14", "use": "XH/XM540 standard-horn family and SKU 903-0276-000", "warning": WARNING},
        {"source_id": "LDS-04", "source": "ROBOTIS HN12-N101 Set", "url": "https://www.robotis.us/hn12-n101-set/", "revision_or_date": "live official product page; revision/date not stated", "accessed_date": "2026-08-14", "use": "XH/XM430 standard-horn family and SKU 903-0238-000", "warning": WARNING},
        {"source_id": "LDS-05", "source": "Project-owned open-belt pitch-length equation", "url": "belt-center-geometry.csv and leg-drivetrain-source.py", "revision_or_date": "repository-bound at generation", "accessed_date": "2026-08-14", "use": "solve nominal pitch-center distance; capacity/tension not inferred", "warning": WARNING},
    ]
    write_csv(OUT / "transmission-source-register.csv", sources)
    status = {"identifier": IDENTIFIER, "module_count": 4, "axis_count": len(axis_rows), "candidate_product_count": len(product_rows), "native_step_module_count": 4, "native_glb_module_count": 4, "lineup_step_present": True, "lineup_glb_present": True, "knee_ratio": 2.5, "knee_current_boundary_correction_present": True, "belt_pitch_length_closure_error_mm_max": max(float(row["length_closure_error_mm"]) for row in values), "exact_candidate_product_allocation_present": True, "vendor_tooth_brep_present": False, "horn_adapter_nominal_cad_complete": True, "horn_adapter_material_fit_fasteners_released": False, "capacity_validated": False, "tension_validated": False, "physical_validation_complete": False, "procurement_authority": False, "fabrication_authority": False, "assembly_authority": False, "powered_test_authority": False, "motion_authority": False, "energization_authority": False, "warning": WARNING}
    (OUT / "leg-drivetrain-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    (OUT / "index.html").write_text(render_index(values), encoding="utf-8", newline="\n")
    (OUT / "README.md").write_text(f"# HR-30 reduced-leg drivetrain P0.1\n\n**{WARNING}**\n\nFour product-specific 5GT/EV5GT modules cover all ten reduced leg axes. The dedicated LD-25K knee module uses 16:40 teeth, a 250 mm belt and a 10 mm XH540 horn-adapter interface. Native CAD represents catalog external/routing envelopes and exact solved pitch centers. P-bore-plus-tap retention and separate dimensioned adapter geometry are selected, while vendor tooth B-Reps, material, fits, fasteners, capacity and work authority remain open.\n", encoding="utf-8", newline="\n")
    shutil.copy2(Path(__file__), OUT / "leg-drivetrain-source.py")
    files = sorted(path for path in OUT.rglob("*") if path.is_file() and path.name != "file-manifest.csv")
    write_csv(OUT / "file-manifest.csv", [{"path": path.relative_to(OUT).as_posix(), "bytes": path.stat().st_size, "sha256": sha256(path), "warning": WARNING} for path in files])
    integrate_root()
    system.refresh_manifest_and_release()
    print(json.dumps(status, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
