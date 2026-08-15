"""Generate the HR-30 leg-drive horn adapters and output shaft interfaces.

The motor adapters are five-axis-machinable one-piece flange/stub parts that
bolt to exact ROBOTIS HN12/HN13 horn patterns and enter MISUMI P-bore pulley
candidates.  The output parts are two length variants of a hollow 12 mm shaft
with an integral pulley shoulder and a separate axial capture washer.  These
are coherent P0.1 geometry candidates, not released drawings: material, fits,
set-screw torque, fastener grade/locking, belt capacity and physical proof are
still open.
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
OUT = WHOLE / "leg-drivetrain-adapters-p0.1"
IDENTIFIER = "HR30-LEG-DRIVETRAIN-ADAPTERS-P0.1"
WARNING = "PRELIMINARY - DIMENSIONED ADAPTER GEOMETRY CANDIDATE ONLY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, POWERED TESTING, MOTION, OR ENERGIZATION"

sys.path.insert(0, str(ROOT / "tools"))
import generate_hr30_body_architecture_p01 as body  # noqa: E402
import generate_hr30_leg_drivetrain_p01 as drives  # noqa: E402
import generate_hr30_system_package_p01 as system  # noqa: E402


@dataclass(frozen=True)
class HornInterface:
    horn_id: str
    source_step: Path
    source_pdf: Path
    expected_step_sha256: str
    expected_pdf_sha256: str
    contact_y_mm: float
    horn_od_mm: float
    bolt_count: int
    bolt_pcd_mm: float
    horn_thread: str
    adapter_clearance_mm: float
    countersink_od_mm: float
    boss_clearance_mm: float
    boss_clearance_depth_mm: float
    flange_od_mm: float
    included_center_fastener: str
    included_frame_fastener: str
    official_product_url: str
    drawing_record: str


HORN_INTERFACES = {
    "HN12": HornInterface(
        "HN12-N101",
        ROOT / "cad/vendor/robotis/hn12-n101-r103/HN12-N101-official.step",
        ROOT / "cad/vendor/robotis/hn12-n101-r103/HN12-N101-official.pdf",
        "6DE6851B85132EC496F24A177729ECA5CE43416707652E79183BFA51E7F978FD",
        "0D6C309F8A45D81FFAABDB45982B7DE0B6E7F74742CAE850CFF4E938B86A81FA",
        2.0, 19.5, 8, 16.0, "M2 x 0.4 TAP THRU", 2.4, 4.0, 8.2, 2.3, 20.0,
        "M2.5 x 6 supplied with horn", "M2 x 3 supplied with horn",
        "https://www.robotis.us/hn12-n101-set/", "ROBOTIS download record 1735; drawing dated 2019-05-22",
    ),
    "HN13": HornInterface(
        "HN13-N101",
        ROOT / "cad/vendor/robotis/hn13-n101-r143/HN13-N101-official.step",
        ROOT / "cad/vendor/robotis/hn13-n101-r143/HN13-N101-official.pdf",
        "F3308807BC92C17E13F0785353B59D117DE8CEF96D3F7638D1388A92B46ABC6F",
        "761A049309BCE2242AB295332A488D024C0A68B5AF8560C892F016DB3BA93F44",
        2.6, 26.0, 8, 22.0, "M2.5 x 0.45 TAP THRU", 2.9, 5.2, 10.2, 2.4, 27.0,
        "M3 x 8 supplied with horn", "M2.5 x 4 supplied with horn",
        "https://robotis.us/hn13-n101-set/", "ROBOTIS download record 1737; drawing dated 2019-05-22",
    ),
}


@dataclass(frozen=True)
class MotorAdapter:
    adapter_id: str
    horn_key: str
    pulley_bore_mm: float
    pulley_candidate: str
    whole_robot_quantity: int


MOTOR_ADAPTERS = (
    MotorAdapter("MA-HN13-P10", "HN13", 10.0, "GPA16/20GT5090-A-P10", 6),
    MotorAdapter("MA-HN12-P10", "HN12", 10.0, "GPA20GT5090-A-P10", 2),
    MotorAdapter("MA-HN12-P8", "HN12", 8.0, "GPA16GT5090-A-P8", 2),
)

OUTPUT_ADAPTERS = (
    {"adapter_id": "OS-P12-45", "offset_mm": 45.0, "quantity": 8, "pulley_candidate": "GPA30/40GT5090-A-P12"},
    {"adapter_id": "OS-P12-55", "offset_mm": 55.0, "quantity": 2, "pulley_candidate": "GPA40GT5090-A-P12"},
)

FLANGE_THICKNESS_MM = 4.0
PULLEY_ENGAGEMENT_MM = 14.5
OUTPUT_SHAFT_OD_MM = 12.0
OUTPUT_SHAFT_BORE_MM = 7.4
OUTPUT_SHOULDER_OD_MM = 20.0
OUTPUT_SHOULDER_THICKNESS_MM = 3.0
OUTPUT_CAP_OD_MM = 20.0
OUTPUT_CAP_THICKNESS_MM = 2.0


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path: Path, records: list[dict]) -> None:
    if not records:
        raise RuntimeError(f"refusing empty CSV: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)


def validate_vendor_sources() -> None:
    for horn in HORN_INTERFACES.values():
        for path, expected in ((horn.source_step, horn.expected_step_sha256), (horn.source_pdf, horn.expected_pdf_sha256)):
            identity_sha = body.vendor_identity_sha256(path) if path.suffix.lower() in {".stp", ".step"} else sha(path)
            if not path.is_file() or identity_sha.upper() != expected:
                raise RuntimeError(f"vendor source identity mismatch: {path}")


def radial_hole(center_radius: float, angle_deg: float, diameter: float, length: float, center_y: float) -> cq.Shape:
    angle = math.radians(angle_deg)
    return body.cylinder_between(
        (center_radius * math.cos(angle), center_y, center_radius * math.sin(angle)),
        (0, 1, 0), length, diameter,
    )


def motor_adapter_shape(spec: MotorAdapter) -> cq.Shape:
    horn = HORN_INTERFACES[spec.horn_key]
    flange = body.cylinder_between((0, FLANGE_THICKNESS_MM / 2.0, 0), (0, 1, 0), FLANGE_THICKNESS_MM, horn.flange_od_mm)
    pocket = body.cylinder_between(
        (0, horn.boss_clearance_depth_mm / 2.0 - 0.05, 0), (0, 1, 0),
        horn.boss_clearance_depth_mm + 0.2, horn.boss_clearance_mm,
    )
    shape = flange.cut(pocket)
    pcd_radius = horn.bolt_pcd_mm / 2.0
    for index in range(horn.bolt_count):
        angle = index * 360.0 / horn.bolt_count
        shape = shape.cut(radial_hole(pcd_radius, angle, horn.adapter_clearance_mm, FLANGE_THICKNESS_MM + 1.0, FLANGE_THICKNESS_MM / 2.0))
        a = math.radians(angle)
        countersink = cq.Solid.makeCone(
            horn.countersink_od_mm / 2.0,
            horn.adapter_clearance_mm / 2.0,
            1.2,
            cq.Vector(pcd_radius * math.cos(a), FLANGE_THICKNESS_MM + 0.01, pcd_radius * math.sin(a)),
            cq.Vector(0, -1, 0),
        )
        shape = shape.cut(countersink)
    stub = body.cylinder_between(
        (0, FLANGE_THICKNESS_MM + PULLEY_ENGAGEMENT_MM / 2.0, 0),
        (0, 1, 0), PULLEY_ENGAGEMENT_MM, spec.pulley_bore_mm,
    )
    shape = shape.fuse(stub)
    thread_drill = 2.5 if spec.pulley_bore_mm == 8.0 else 3.3
    blind_depth = 8.0 if spec.pulley_bore_mm == 8.0 else 10.0
    blind = body.cylinder_between(
        (0, FLANGE_THICKNESS_MM + PULLEY_ENGAGEMENT_MM - blind_depth / 2.0 + 0.1, 0),
        (0, 1, 0), blind_depth + 0.2, thread_drill,
    )
    return shape.cut(blind).clean()


def horn_shape_local(horn_key: str) -> cq.Shape:
    horn = HORN_INTERFACES[horn_key]
    return cq.importers.importStep(str(horn.source_step)).val().translate((0, -horn.contact_y_mm, 0))


def output_shaft_local(offset_mm: float) -> tuple[cq.Shape, cq.Shape]:
    """Return a +Y-outward shaft and removable axial capture washer."""
    inside_y = -offset_mm - 8.0
    outside_y = PULLEY_ENGAGEMENT_MM + 3.5
    length = outside_y - inside_y
    shaft = body.hollow_cylinder_between(
        (0, (inside_y + outside_y) / 2.0, 0), (0, 1, 0),
        length, OUTPUT_SHAFT_OD_MM, OUTPUT_SHAFT_BORE_MM,
    )
    shoulder_y = -PULLEY_ENGAGEMENT_MM / 2.0 - OUTPUT_SHOULDER_THICKNESS_MM / 2.0
    shoulder = body.hollow_cylinder_between(
        (0, shoulder_y, 0), (0, 1, 0), OUTPUT_SHOULDER_THICKNESS_MM,
        OUTPUT_SHOULDER_OD_MM, OUTPUT_SHAFT_BORE_MM,
    )
    cap_y = PULLEY_ENGAGEMENT_MM / 2.0 + OUTPUT_CAP_THICKNESS_MM / 2.0
    cap = body.hollow_cylinder_between(
        (0, cap_y, 0), (0, 1, 0), OUTPUT_CAP_THICKNESS_MM,
        OUTPUT_CAP_OD_MM, OUTPUT_SHAFT_BORE_MM,
    )
    return shaft.fuse(shoulder).clean(), cap.clean()


def motor_adapter_for_axis(axis_id: str, drive: drives.Drive) -> MotorAdapter:
    if "ANKLE" not in axis_id:
        target = "MA-HN13-P10"
    elif abs(drive.motor_bore_mm - 8.0) < 1e-9:
        target = "MA-HN12-P8"
    else:
        target = "MA-HN12-P10"
    return next(item for item in MOTOR_ADAPTERS if item.adapter_id == target)


def drawing_svg(part_id: str, title: str, lines: list[str]) -> str:
    rows = "".join(f'<text x="48" y="{180 + i * 34}" class="body">{html.escape(line)}</text>' for i, line in enumerate(lines))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="620" viewBox="0 0 900 620"><style>.title{{font:800 34px system-ui,Segoe UI,sans-serif;fill:#fff}}.sub{{font:700 18px system-ui,Segoe UI,sans-serif;fill:#123b68}}.body{{font:16px system-ui,Segoe UI,sans-serif;fill:#152b43}}.warn{{font:800 16px system-ui,Segoe UI,sans-serif;fill:#17243a}}.line{{stroke:#075b9b;stroke-width:3;fill:none}}.part{{fill:#f2b91d;stroke:#8a5b00;stroke-width:3}}</style><rect width="900" height="620" fill="#eff9fe"/><rect width="900" height="100" fill="#081e38"/><text x="36" y="55" class="title">{html.escape(title)}</text><text x="36" y="84" class="title" style="font-size:18px">{html.escape(part_id)} - P0.1 candidate</text><rect x="46" y="122" width="280" height="38" rx="8" fill="#f2b91d"/><text x="60" y="147" class="warn">NOT RELEASED FOR MACHINING</text>{rows}<circle cx="690" cy="292" r="108" class="part"/><circle cx="690" cy="292" r="42" fill="#eff9fe" stroke="#075b9b" stroke-width="3"/><line x1="570" y1="430" x2="810" y2="430" class="line"/><text x="615" y="462" class="sub">interface view</text><text x="48" y="584" class="body">All dimensions in mm. Material, fits, tolerances, fastener grade/locking, torque and capacity remain SELECTION REQUIRED.</text></svg>'''


def render_index() -> str:
    cards = "".join(
        f'''<article class="card"><h3>{item.adapter_id}</h3><p>{item.horn_key} horn to {item.pulley_candidate}; {item.whole_robot_quantity} required.</p><p><a href="parts/{item.adapter_id}.step">STEP</a> &middot; <a href="drawings/{item.adapter_id}.svg">drawing</a></p></article>'''
        for item in MOTOR_ADAPTERS
    ) + "".join(
        f'''<article class="card"><h3>{item['adapter_id']}</h3><p>12 mm output shaft/shoulder/cap for {item['offset_mm']:.0f} mm service-plane offset; {item['quantity']} required.</p><p><a href="parts/{item['adapter_id']}.step">STEP</a> &middot; <a href="drawings/{item['adapter_id']}.svg">drawing</a></p></article>'''
        for item in OUTPUT_ADAPTERS
    )
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 leg-drive adapters P0.1</title><script type="module" src="../vendor/model-viewer.min.js"></script><style>:root{{--deep:#081e38;--navy:#123b68;--pale:#eff9fe;--gold:#f2b91d;--line:#acd8ed;--ink:#152b43}}*{{box-sizing:border-box}}html,body{{max-width:100%;overflow-x:clip}}body{{margin:0;background:var(--pale);color:var(--ink);font:17px/1.55 system-ui,Segoe UI,sans-serif}}header,footer{{padding:32px max(20px,calc((100vw - 1200px)/2));background:var(--deep);color:white}}h1{{font-size:clamp(36px,6vw,66px);line-height:1.04}}h2{{font-size:clamp(28px,4vw,42px);color:var(--navy)}}h3{{font-size:22px;color:var(--navy)}}.warning{{padding:16px;background:var(--gold);color:#17243a;border:3px solid #8a5b00;font-weight:900}}main{{max-width:1200px;margin:auto;padding:28px 20px 80px}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:16px}}.card,.viewer,.panel{{background:white;border:2px solid var(--line);border-radius:18px;padding:18px;overflow:hidden}}model-viewer{{display:block;width:100%;height:clamp(520px,70vh,760px);background:radial-gradient(circle,#fff,var(--pale))}}a{{color:#075b9b;font-weight:800}}@media(max-width:560px){{body{{font-size:16px}}.grid{{grid-template-columns:1fr}}model-viewer{{height:500px}}}}</style></head><body><header><div class="warning">{html.escape(WARNING)}</div><h1>The ten reduced leg drives now have physical adapter hardware.</h1><p>Three motor-adapter families join exact HN12/HN13 horn patterns to P-bore pulley candidates. Two hollow output-shaft families provide shoulders and removable axial capture.</p></header><main><section><h2>Orbit the adapter lineup</h2><div class="viewer"><model-viewer src="HR-30_leg_drivetrain_adapter_lineup_candidate.glb" alt="Five preliminary HR-30 leg-drive adapter families with exact ROBOTIS horns" camera-controls camera-orbit="135deg 70deg 115%" field-of-view="30deg" shadow-intensity="0.85"></model-viewer><p><a href="HR-30_leg_drivetrain_adapter_lineup_candidate.step">Lineup STEP</a> &middot; <a href="adapter-part-register.csv">part register</a> &middot; <a href="interface-definition-register.csv">interfaces</a> &middot; <a href="axis-adapter-allocation.csv">all ten axes</a>.</p></div></section><section><h2>Five reusable machined-part families</h2><div class="grid">{cards}</div></section><section><h2>What is now concrete</h2><div class="panel"><p>The horn bolt circles, center-boss clearances, flange/stub geometry, nominal pulley bores, output-shaft shoulders, capture washers and per-axis allocation are editable source CAD. The selected MISUMI pulley suffix changes from H round bore to P round-bore-plus-tap so the catalogue supplies radial retention screws. The P0.1 model still withholds material, fit, runout, set-screw torque, bolt length/grade/locking, thread engagement, belt capacity, fatigue and physical-fit credit.</p></div></section></main><footer>Project Button &middot; HR-30 leg-drive adapters P0.1 &middot; no procurement, fabrication, powered-test, motion or energization authority</footer></body></html>'''


def integrate_root() -> None:
    status_path = WHOLE / "package-status.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    status.update({
        "leg_drivetrain_adapter_package_present": True,
        "leg_drivetrain_motor_adapter_family_count": 3,
        "leg_drivetrain_output_adapter_family_count": 2,
        "leg_drivetrain_adapter_axis_allocation_complete": True,
        "leg_drivetrain_adapter_editable_cad_present": True,
        "leg_drivetrain_adapter_nominal_geometry_complete": True,
        "leg_drivetrain_adapter_fit_and_tolerance_released": False,
        "leg_drivetrain_adapter_capacity_validated": False,
        "leg_drivetrain_adapter_physical_fit_validated": False,
        "reduced_leg_drivetrain_horn_adapters_complete": True,
        "procurement_authority": False, "fabrication_authority": False,
        "assembly_authority": False, "powered_test_authority": False,
        "motion_authority": False, "energization_authority": False,
    })
    status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")

    readme_path = WHOLE / "README.md"
    readme = readme_path.read_text(encoding="utf-8")
    start, end = "<!-- HR30-LEG-ADAPTERS-P01-README-START -->", "<!-- HR30-LEG-ADAPTERS-P01-README-END -->"
    if start in readme and end in readme:
        readme = readme.split(start, 1)[0] + readme.split(end, 1)[1]
    marker = "<!-- HR30-ASSEMBLY-GUIDE-P01-START -->"
    block = f'''{start}\n## Dimensioned leg-drive adapters\n\nThe [leg-drive adapter guide](leg-drivetrain-adapters-p0.1/index.html) adds three editable horn-to-pulley adapters and two shouldered output-shaft/capture families. Exact HN12/HN13 STEP geometry and reference-drawing patterns control the motor interface; all ten reduced axes have an adapter allocation. Nominal geometry is complete, while material, tolerances, fits, fastener details, capacity and physical proof remain open.\n{end}\n'''
    if marker not in readme:
        raise RuntimeError("whole-body README integration marker missing")
    readme_path.write_text(readme.replace(marker, block + marker), encoding="utf-8", newline="\n")

    page_path = WHOLE / "index.html"
    page = page_path.read_text(encoding="utf-8")
    start, end = "<!-- HR30-LEG-ADAPTERS-P01-START -->", "<!-- HR30-LEG-ADAPTERS-P01-END -->"
    if start in page and end in page:
        page = page.split(start, 1)[0] + page.split(end, 1)[1]
    section = f'''{start}<section id="leg-drive-adapters"><h2>The reduced leg drives now have real adapter parts</h2><div class="grid"><article class="card pass"><div class="metric">3 + 2</div><p>Motor-flange and output-shaft adapter families.</p></article><article class="card pass"><div class="metric">10 / 10</div><p>Reduced leg axes have a complete nominal allocation.</p></article><article class="card pass"><h3>Manufacturer-bound</h3><p>Exact HN12/HN13 CAD and published bolt circles control the motor interface.</p></article><article class="card hold"><h3>Not released</h3><p>Fits, material, tolerances, fasteners, capacity and physical inspection remain open.</p></article></div><p><a href="leg-drivetrain-adapters-p0.1/index.html">Open the adapter guide</a> &middot; <a href="leg-drivetrain-adapters-p0.1/adapter-part-register.csv">part register</a> &middot; <a href="leg-drivetrain-adapters-p0.1/axis-adapter-allocation.csv">axis allocation</a>.</p></section>{end}'''
    if marker not in page:
        raise RuntimeError("whole-body page integration marker missing")
    page_path.write_text(page.replace(marker, section + marker), encoding="utf-8", newline="\n")

    holds_path = WHOLE / "open-holds.csv"
    with holds_path.open(encoding="utf-8", newline="") as handle:
        holds = list(csv.DictReader(handle))
    target = next((row for row in holds if row["hold_id"] == "HR30-P01-H03"), None)
    if target is None:
        raise RuntimeError("controlled leg hold missing")
    target["unresolved_item"] = (
        "All twelve leg axes have static load screens. Ten belt-reduced axes have MISUMI 5GT/EV5GT candidate geometry, "
        "three dimensioned HN12/HN13-to-P-bore motor-adapter variants, two shouldered output-shaft/capture variants and a "
        "complete per-axis allocation. Material, fits, tolerances, runout, fastener grade/length/locking/torque, bearing side "
        "loads, belt tension/capacity, motion and cable/cover sweeps, continuous torque, thermal limits, fatigue and physical "
        "fit/proof remain open."
    )
    write_csv(holds_path, holds)

    bom_path = WHOLE / "whole-robot-candidate-bom.csv"
    with bom_path.open(encoding="utf-8", newline="") as handle:
        bom = list(csv.DictReader(handle))
    item = next((row for row in bom if row["item_id"] == "HR30-BOM-019"), None)
    if item is None:
        raise RuntimeError("controlled leg reduction BOM row missing")
    item["candidate"] = (
        "MISUMI GPA16/20/30/40GT5090-A-P8/P10/P12 pulley candidates with GBN225/250/255EV5GT-090 belts; "
        "three project-custom horn adapters and two shouldered output-shaft/capture variants in leg-drivetrain-adapters-p0.1; "
        "material, fit, tolerance, fasteners, capacity and physical proof open"
    )
    write_csv(bom_path, bom)


def main() -> int:
    validate_vendor_sources()
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "parts").mkdir(parents=True)
    (OUT / "drawings").mkdir()

    assembly = cq.Assembly(name="HR30_LEG_DRIVETRAIN_ADAPTERS_P01_NOT_RELEASED")
    lineup_shapes: list[cq.Shape] = []
    part_rows: list[dict] = []
    interface_rows: list[dict] = []
    x_cursor = -100.0
    for spec in MOTOR_ADAPTERS:
        horn = HORN_INTERFACES[spec.horn_key]
        adapter = motor_adapter_shape(spec)
        vendor_horn = horn_shape_local(spec.horn_key)
        export_shape = cq.Compound.makeCompound([vendor_horn, adapter])
        cq.exporters.export(export_shape, str(OUT / "parts" / f"{spec.adapter_id}.step"))
        body.canonicalize_step(OUT / "parts" / f"{spec.adapter_id}.step")
        assembly.add(vendor_horn.translate((x_cursor, 0, 0)), name=f"{spec.adapter_id}_EXACT_{horn.horn_id}", color=cq.Color(0.45, 0.50, 0.57, 1.0))
        assembly.add(adapter.translate((x_cursor, 0, 0)), name=f"{spec.adapter_id}_PROJECT_ADAPTER", color=cq.Color(0.95, 0.62, 0.08, 1.0))
        lineup_shapes.extend([vendor_horn.translate((x_cursor, 0, 0)), adapter.translate((x_cursor, 0, 0))])
        x_cursor += 48.0
        part_rows.append({
            "part_id": spec.adapter_id, "kind": "MOTOR HORN-TO-PULLEY ADAPTER", "quantity": spec.whole_robot_quantity,
            "horn_interface": horn.horn_id, "pulley_interface": spec.pulley_candidate,
            "material": "SELECTION REQUIRED", "manufacturing_route": "TURN + 3-AXIS/5-AXIS MILL CANDIDATE",
            "volume_mm3": f"{adapter.Volume():.6f}", "mass_kg": "SELECTION REQUIRED",
            "nominal_geometry_complete": True, "fit_tolerance_released": False, "capacity_validated": False, "warning": WARNING,
        })
        interface_rows.extend([
            {"part_id": spec.adapter_id, "interface_id": "IF-HORN", "feature": f"{horn.bolt_count} clearance/countersink holes on PCD {horn.bolt_pcd_mm:.1f}; pocket {horn.boss_clearance_mm:.1f} x {horn.boss_clearance_depth_mm:.1f}", "mating_item": horn.horn_id, "nominal_definition": "COMPLETE", "tolerance_fit": "SELECTION REQUIRED", "validation": "PHYSICAL FIT AND TORQUE PROOF OPEN", "warning": WARNING},
            {"part_id": spec.adapter_id, "interface_id": "IF-PULLEY", "feature": f"{spec.pulley_bore_mm:.1f} OD x {PULLEY_ENGAGEMENT_MM:.1f} engagement stub; blind end-retainer tap-drill modeled", "mating_item": spec.pulley_candidate, "nominal_definition": "COMPLETE", "tolerance_fit": "SELECTION REQUIRED", "validation": "RUNOUT/SET-SCREW/AXIAL CAPTURE PROOF OPEN", "warning": WARNING},
        ])
        (OUT / "drawings" / f"{spec.adapter_id}.svg").write_text(drawing_svg(spec.adapter_id, f"{horn.horn_id} to {spec.pulley_candidate}", [
            f"Flange OD {horn.flange_od_mm:.1f}; thickness {FLANGE_THICKNESS_MM:.1f}",
            f"{horn.bolt_count} holes on PCD {horn.bolt_pcd_mm:.1f}; horn thread {horn.horn_thread}",
            f"Boss-clearance pocket diameter {horn.boss_clearance_mm:.1f}; depth {horn.boss_clearance_depth_mm:.1f}",
            f"Pulley stub diameter {spec.pulley_bore_mm:.1f}; engagement {PULLEY_ENGAGEMENT_MM:.1f}",
            f"Pulley candidate {spec.pulley_candidate}; P-bore radial set screws supplied by catalog",
        ]), encoding="utf-8", newline="\n")

    for item in OUTPUT_ADAPTERS:
        shaft, cap = output_shaft_local(item["offset_mm"])
        compound = cq.Compound.makeCompound([shaft, cap])
        cq.exporters.export(compound, str(OUT / "parts" / f"{item['adapter_id']}.step"))
        body.canonicalize_step(OUT / "parts" / f"{item['adapter_id']}.step")
        assembly.add(shaft.translate((x_cursor, 0, 0)), name=f"{item['adapter_id']}_SHOULDERED_SHAFT", color=cq.Color(0.10, 0.25, 0.44, 1.0))
        assembly.add(cap.translate((x_cursor, 0, 0)), name=f"{item['adapter_id']}_CAPTURE_WASHER", color=cq.Color(0.95, 0.62, 0.08, 1.0))
        lineup_shapes.extend([shaft.translate((x_cursor, 0, 0)), cap.translate((x_cursor, 0, 0))])
        x_cursor += 48.0
        part_rows.append({
            "part_id": item["adapter_id"], "kind": "OUTPUT SHOULDERED SHAFT + CAPTURE WASHER", "quantity": item["quantity"],
            "horn_interface": "N/A", "pulley_interface": item["pulley_candidate"],
            "material": "SELECTION REQUIRED", "manufacturing_route": "TURNING + CROSS/AXIAL FEATURES CANDIDATE",
            "volume_mm3": f"{compound.Volume():.6f}", "mass_kg": "SELECTION REQUIRED",
            "nominal_geometry_complete": True, "fit_tolerance_released": False, "capacity_validated": False, "warning": WARNING,
        })
        interface_rows.append({
            "part_id": item["adapter_id"], "interface_id": "IF-OUTPUT-PULLEY", "feature": f"12.0 OD hollow shaft; 7.4 bore; 20.0 OD x 3.0 shoulder; 20.0 OD x 2.0 capture washer", "mating_item": item["pulley_candidate"], "nominal_definition": "COMPLETE", "tolerance_fit": "SELECTION REQUIRED", "validation": "BEARING/THROUGH-BOLT/SET-SCREW/CAPACITY PROOF OPEN", "warning": WARNING,
        })
        (OUT / "drawings" / f"{item['adapter_id']}.svg").write_text(drawing_svg(item["adapter_id"], f"{item['offset_mm']:.0f} mm service-plane output shaft", [
            f"Nominal shaft OD {OUTPUT_SHAFT_OD_MM:.1f}; through bore {OUTPUT_SHAFT_BORE_MM:.1f}",
            f"Joint-to-pulley service-plane offset {item['offset_mm']:.1f}",
            f"Pulley shoulder OD {OUTPUT_SHOULDER_OD_MM:.1f}; thickness {OUTPUT_SHOULDER_THICKNESS_MM:.1f}",
            f"Capture washer OD {OUTPUT_CAP_OD_MM:.1f}; thickness {OUTPUT_CAP_THICKNESS_MM:.1f}",
            f"Pulley candidate {item['pulley_candidate']}",
        ]), encoding="utf-8", newline="\n")

    axis_rows = []
    for drive in drives.DRIVES:
        for axis_id in drive.axis_ids:
            motor = motor_adapter_for_axis(axis_id, drive)
            offset = 55.0 if "ROLL" in axis_id else 45.0
            output = next(item for item in OUTPUT_ADAPTERS if item["offset_mm"] == offset)
            axis_rows.append({
                "axis_id": axis_id, "drive_id": drive.drive_id, "motor_adapter": motor.adapter_id,
                "horn": HORN_INTERFACES[motor.horn_key].horn_id, "motor_pulley": motor.pulley_candidate,
                "output_adapter": output["adapter_id"], "output_pulley": drive.output_pulley_code.replace("-H12", "-P12"),
                "nominal_allocation_complete": True, "fit_capacity_physical_validation": "OPEN", "warning": WARNING,
            })
    if len(axis_rows) != 10:
        raise RuntimeError("adapter allocation must cover ten reduced axes")

    lineup = cq.Compound.makeCompound(lineup_shapes)
    cq.exporters.export(lineup, str(OUT / "HR-30_leg_drivetrain_adapter_lineup_candidate.step"))
    body.canonicalize_step(OUT / "HR-30_leg_drivetrain_adapter_lineup_candidate.step")
    assembly.save(str(OUT / "HR-30_leg_drivetrain_adapter_lineup_candidate.glb"), tolerance=0.10, angularTolerance=0.10)
    write_csv(OUT / "adapter-part-register.csv", part_rows)
    write_csv(OUT / "interface-definition-register.csv", interface_rows)
    write_csv(OUT / "axis-adapter-allocation.csv", axis_rows)
    write_csv(OUT / "fastener-selection-register.csv", [
        {"fastener_id": "AF-HN12", "location": "HN12 adapter flange", "candidate": "8 x countersunk M2 screw per adapter", "quantity_whole_robot": 32, "length_grade_locking_torque": "SELECTION REQUIRED", "source_boundary": HORN_INTERFACES["HN12"].horn_thread, "authority": "NO PROCUREMENT/FABRICATION AUTHORITY", "warning": WARNING},
        {"fastener_id": "AF-HN13", "location": "HN13 adapter flange", "candidate": "8 x countersunk M2.5 screw per adapter", "quantity_whole_robot": 48, "length_grade_locking_torque": "SELECTION REQUIRED", "source_boundary": HORN_INTERFACES["HN13"].horn_thread, "authority": "NO PROCUREMENT/FABRICATION AUTHORITY", "warning": WARNING},
        {"fastener_id": "AF-MOTOR-CAP", "location": "motor pulley axial capture", "candidate": "retaining screw + washer sized to blind end thread", "quantity_whole_robot": 10, "length_grade_locking_torque": "SELECTION REQUIRED", "source_boundary": "M3 tap-drill on 8 mm stub; M4 tap-drill on 10 mm stub", "authority": "NO PROCUREMENT/FABRICATION AUTHORITY", "warning": WARNING},
        {"fastener_id": "AF-OUTPUT-CAP", "location": "output pulley axial capture", "candidate": "through-bolt and washer system through 7.4 mm bore", "quantity_whole_robot": 10, "length_grade_locking_torque": "SELECTION REQUIRED", "source_boundary": "joint carrier and bearing stack release required", "authority": "NO PROCUREMENT/FABRICATION AUTHORITY", "warning": WARNING},
    ])
    write_csv(OUT / "source-binding.csv", [
        {"source_id": "ADS-01", "source": "ROBOTIS HN12-N101 official STEP", "path_or_url": HORN_INTERFACES["HN12"].source_step.relative_to(ROOT).as_posix(), "sha256": body.vendor_identity_sha256(HORN_INTERFACES["HN12"].source_step), "revision_date": HORN_INTERFACES["HN12"].drawing_record, "use": "exact HN12 solid and reference pattern", "warning": WARNING},
        {"source_id": "ADS-02", "source": "ROBOTIS HN13-N101 official STEP", "path_or_url": HORN_INTERFACES["HN13"].source_step.relative_to(ROOT).as_posix(), "sha256": body.vendor_identity_sha256(HORN_INTERFACES["HN13"].source_step), "revision_date": HORN_INTERFACES["HN13"].drawing_record, "use": "exact HN13 solid and reference pattern", "warning": WARNING},
        {"source_id": "ADS-03", "source": "MISUMI High Torque Timing Pulleys 5GT", "path_or_url": "https://uk.misumi-ec.com/pdf/fa/p1_1117.pdf", "sha256": "0799620CEB55DB471F4C4A16CB70751119B0478F970D0F47C301215E4C25CCBF", "revision_date": "official catalog PDF metadata 2012-09-04; accessed 2026-08-15", "use": "P round-bore-plus-tap option, 9 mm belt-width family and nominal bore availability", "warning": WARNING},
        {"source_id": "ADS-04", "source": "adapter generator", "path_or_url": Path(__file__).relative_to(ROOT).as_posix(), "sha256": sha(Path(__file__)), "revision_date": "generated 2026-08-15", "use": "editable flange/stub/shaft/cap source CAD", "warning": WARNING},
    ])
    status = {
        "identifier": IDENTIFIER, "motor_adapter_family_count": 3, "output_adapter_family_count": 2,
        "whole_robot_reduced_axis_count": 10, "axis_allocation_complete": True,
        "exact_vendor_horn_step_bound": True, "nominal_adapter_geometry_complete": True,
        "editable_source_cad_present": True, "step_exports_present": True, "glb_export_present": True,
        "misumi_p_bore_retention_topology_selected": True,
        "material_selected": False, "fits_and_tolerances_released": False, "fasteners_released": False,
        "capacity_validated": False, "physical_fit_validated": False,
        "procurement_authority": False, "fabrication_authority": False, "assembly_authority": False,
        "powered_test_authority": False, "motion_authority": False, "energization_authority": False,
        "warning": WARNING,
    }
    (OUT / "adapter-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    (OUT / "index.html").write_text(render_index(), encoding="utf-8", newline="\n")
    (OUT / "README.md").write_text(f"# HR-30 leg-drive adapters P0.1\n\n**{WARNING}**\n\nFive reusable machined-part families give all ten reduced leg axes a concrete nominal horn, pulley and output-shaft interface. The package is editable geometry, not a manufacturing release.\n", encoding="utf-8", newline="\n")
    shutil.copy2(Path(__file__), OUT / "leg-drivetrain-adapters-source.py")
    files = sorted(path for path in OUT.rglob("*") if path.is_file() and path.name != "file-manifest.csv")
    write_csv(OUT / "file-manifest.csv", [{"path": path.relative_to(OUT).as_posix(), "bytes": path.stat().st_size, "sha256": sha(path), "warning": WARNING} for path in files])

    integrate_root()
    system.refresh_manifest_and_release()
    print(json.dumps(status, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
