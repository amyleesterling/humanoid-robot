"""Install exact-candidate leg transmissions into the complete HR-30 body.

The base whole-body source already contains all 25 supported axes and joint
carriers.  This derived assembly removes the ten generic leg pulley/belt/motor
placeholders and installs the product-specific P0.1 pulleys, belts, shifted
manufacturer actuator geometry, exact horns, project motor adapters, shouldered
output shafts/capture washers and guard envelopes.  It is packaging CAD only:
material, fits, fasteners, capacity and physical proof remain open.
"""

from __future__ import annotations

import csv
import hashlib
import html
import json
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

import cadquery as cq
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.gp import gp_Trsf


ROOT = Path(__file__).resolve().parents[1]
WHOLE = ROOT / "hr30" / "whole-body-p0.1"
OUT = WHOLE / "leg-drivetrain-installation-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / "leg-drivetrain-installation-p0.1"
IDENTIFIER = "HR30-INSTALLED-LEG-DRIVETRAINS-P0.1"
WARNING = "PRELIMINARY - WHOLE-BODY PRODUCT PACKAGING CANDIDATE ONLY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, POWERED TESTING, MOTION, OR ENERGIZATION"

sys.path.insert(0, str(ROOT / "tools"))
import generate_hr30_body_architecture_p01 as body  # noqa: E402
import generate_hr30_leg_drivetrain_p01 as drives  # noqa: E402
import generate_hr30_leg_drivetrain_adapters_p01 as adapters  # noqa: E402
import generate_hr30_system_package_p01 as system  # noqa: E402


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


def write_csv(path: Path, records: list[dict]) -> None:
    if not records:
        raise RuntimeError(f"refusing empty CSV: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)


def axis_vector(record: dict) -> cq.Vector:
    return cq.Vector(float(record["direction_x"]), float(record["direction_y"]), float(record["direction_z"])).normalized()


def offset_vector(axis_id: str) -> cq.Vector:
    if "HIP_ROLL" in axis_id:
        return cq.Vector(0, 0, -1)
    if "ANKLE_ROLL" in axis_id:
        return cq.Vector(0, 0, 1)
    if "HIP_PITCH" in axis_id:
        return cq.Vector(0, 0, 1)
    if "KNEE_PITCH" in axis_id or "ANKLE_PITCH" in axis_id:
        return cq.Vector(0, 0, 1)
    raise RuntimeError(f"no reduced-drive offset rule for {axis_id}")


def axial_plane_offset(axis_id: str) -> float:
    # Put pitch-drive planes just outboard of the dual-bearing stacks; put
    # roll-drive planes behind the joint.  This avoids pretending that two
    # orthogonal 47-67 mm pulley envelopes occupy the same central volume.
    if "PITCH" in axis_id:
        return 45.0 if axis_id.startswith("L_") else -45.0
    if "ROLL" in axis_id:
        return -55.0
    raise RuntimeError(f"no external drive-plane rule for {axis_id}")


def map_local(shape: cq.Shape, origin: cq.Vector, local_y_world: cq.Vector, local_z_world: cq.Vector) -> cq.Shape:
    y_dir = local_y_world.normalized()
    z_dir = local_z_world.normalized()
    if abs(y_dir.dot(z_dir)) > 1e-9:
        raise RuntimeError("drive local axes are not orthogonal")
    x_dir = y_dir.cross(z_dir).normalized()
    transform = gp_Trsf()
    transform.SetValues(
        x_dir.x, y_dir.x, z_dir.x, origin.x,
        x_dir.y, y_dir.y, z_dir.y, origin.y,
        x_dir.z, y_dir.z, z_dir.z, origin.z,
    )
    return cq.Shape.cast(BRepBuilderAPI_Transform(shape.wrapped, transform, True).Shape())


def guard_local(drive: drives.Drive, center_mm: float) -> cq.Shape:
    max_flange = max(drives.PULLEY_FLANGE_OD_MM[drive.output_teeth], drives.PULLEY_FLANGE_OD_MM[drive.motor_teeth])
    width = max_flange + 12.0
    height = center_mm + max_flange / 2.0 + 10.0
    center_z = (center_mm + (drives.PULLEY_FLANGE_OD_MM[drive.motor_teeth] - drives.PULLEY_FLANGE_OD_MM[drive.output_teeth]) / 4.0) / 2.0
    outer = cq.Workplane("XY").box(width + 6.0, 14.0, height + 6.0).translate((0, 0, center_z)).val()
    inner = cq.Workplane("XY").box(width, 16.0, height).translate((0, 0, center_z)).val()
    return outer.cut(inner).clean()


def drive_for_axis(axis_id: str) -> drives.Drive:
    matches = [drive for drive in drives.DRIVES if axis_id in drive.axis_ids]
    if len(matches) != 1:
        raise RuntimeError(f"axis-to-drive mapping is not one-to-one: {axis_id}")
    return matches[0]


def build_installed() -> tuple[list[body.Component], list[InstalledPart], list[dict], list[dict]]:
    base_components, axes, _bindings, _vendor = body.build()
    axis_map = {record["axis_id"]: record for record in axes}
    reduced_axes = {axis for drive in drives.DRIVES for axis in drive.axis_ids}
    generic_suffixes = (
        "_OUTPUT_PULLEY", "_MOTOR_PULLEY", "_BELT_PATH_RESERVATION", "_ACTUATOR_VENDOR_CANDIDATE"
    )
    retained = [
        component for component in base_components
        if not any(component.name == f"JMOD_{axis_id}{suffix}" for axis_id in reduced_axes for suffix in generic_suffixes)
    ]
    if len(base_components) - len(retained) != len(reduced_axes) * len(generic_suffixes):
        raise RuntimeError("generic reduced-drive placeholder removal count drift")

    vendor_shapes = {
        source_id: cq.importers.importStep(str(source["path"])).val()
        for source_id, source in body.VENDOR_ACTUATOR_SOURCES.items()
    }
    parts: list[InstalledPart] = []
    installation: list[dict] = []
    per_axis_shapes: dict[str, list[cq.Shape]] = {}
    per_axis_parts: dict[str, list[InstalledPart]] = {}
    for axis_id in sorted(reduced_axes):
        axis = axis_map[axis_id]
        candidate = drive_for_axis(axis_id)
        center = cq.Vector(float(axis["x_mm"]), float(axis["y_mm"]), float(axis["z_mm"]))
        axis_dir = axis_vector(axis)
        drive_dir = offset_vector(axis_id)
        plane_offset = axial_plane_offset(axis_id)
        plane_center = center + axis_dir.multiply(plane_offset)
        solved_center = drives.solve_center(candidate)
        motor_center = plane_center + drive_dir.multiply(solved_center)
        outward_sign = 1.0 if plane_offset > 0 else -1.0
        outward_axis = axis_dir.multiply(outward_sign)

        local_output = drives.pulley_envelope(candidate.output_teeth, 12.0, 0.0)
        local_motor = drives.pulley_envelope(candidate.motor_teeth, candidate.motor_bore_mm, solved_center)
        local_belt = drives.belt_envelope(candidate, solved_center)
        local_guard = guard_local(candidate, solved_center)
        output = map_local(local_output, plane_center, axis_dir, drive_dir)
        motor = map_local(local_motor, plane_center, axis_dir, drive_dir)
        belt = map_local(local_belt, plane_center, axis_dir, drive_dir)
        guard = map_local(local_guard, plane_center, axis_dir, drive_dir)

        adapter_spec = adapters.motor_adapter_for_axis(axis_id, candidate)
        horn_spec = adapters.HORN_INTERFACES[adapter_spec.horn_key]
        stack_to_pulley_center = adapters.FLANGE_THICKNESS_MM + adapters.PULLEY_ENGAGEMENT_MM / 2.0
        horn_contact = motor_center - outward_axis.multiply(stack_to_pulley_center)
        motor_adapter = map_local(adapters.motor_adapter_shape(adapter_spec), horn_contact, outward_axis, drive_dir)
        horn = map_local(adapters.horn_shape_local(adapter_spec.horn_key), horn_contact, outward_axis, drive_dir)

        source_id = body.vendor_source_for_axis(axis_id)
        actuator_output = horn_contact - outward_axis.multiply(horn_spec.contact_y_mm + 0.4)
        actuator, _basis = body.vendor_actuator_to_axis(vendor_shapes[source_id], (actuator_output.x, actuator_output.y, actuator_output.z), (axis_dir.x, axis_dir.y, axis_dir.z))
        spec = body.JOINT_MODULE_FAMILIES[body.joint_module_family(axis_id)]
        actuator_visual = body.oriented_box((actuator_output.x, actuator_output.y, actuator_output.z), (axis_dir.x, axis_dir.y, axis_dir.z), spec["body_w"], spec["body_h"], spec["body_d"])
        local_output_shaft, local_output_cap = adapters.output_shaft_local(abs(plane_offset))
        output_shaft = map_local(local_output_shaft, plane_center, outward_axis, drive_dir)
        output_cap = map_local(local_output_cap, plane_center, outward_axis, drive_dir)

        axis_parts = [
            InstalledPart(axis_id, f"{axis_id}_OUTPUT_PULLEY", "catalog P-bore-plus-tap pulley envelope", output, output, (0.96, 0.55, 0.08, 1.0), f"{candidate.output_pulley_code}; received fit/set-screw/capacity validation open"),
            InstalledPart(axis_id, f"{axis_id}_MOTOR_PULLEY", "catalog P-bore-plus-tap pulley envelope", motor, motor, (0.98, 0.72, 0.12, 1.0), f"{candidate.motor_pulley_code}; received fit/set-screw/capacity validation open"),
            InstalledPart(axis_id, f"{axis_id}_BELT", "catalog belt routing envelope", belt, belt, (0.10, 0.13, 0.17, 1.0), f"{candidate.belt_code}; tension/capacity/life open"),
            InstalledPart(axis_id, f"{axis_id}_GUARD", "removable guard envelope", guard, guard, (0.40, 0.75, 0.94, 0.30), "transparent packaging envelope; split, vents, retention and access proof open"),
            InstalledPart(axis_id, f"{axis_id}_ACTUATOR", "shifted manufacturer actuator", actuator, actuator_visual, (0.10, 0.25, 0.44, 1.0), f"{source_id} exact STEP with simplified GLB body; project mount open"),
            InstalledPart(axis_id, f"{axis_id}_HORN", "exact manufacturer horn", horn, horn, (0.45, 0.50, 0.57, 1.0), f"{horn_spec.horn_id} exact STEP; thread/load/physical validation open"),
            InstalledPart(axis_id, f"{axis_id}_MOTOR_ADAPTER", "project horn-to-pulley adapter", motor_adapter, motor_adapter, (0.95, 0.62, 0.08, 1.0), f"{adapter_spec.adapter_id}; nominal CAD complete; material/fit/fasteners/capacity open"),
            InstalledPart(axis_id, f"{axis_id}_OUTPUT_SHAFT", "shouldered hollow output shaft", output_shaft, output_shaft, (0.76, 0.79, 0.83, 1.0), f"OS-P12-{abs(plane_offset):.0f}; nominal CAD complete; material/fit/capacity open"),
            InstalledPart(axis_id, f"{axis_id}_OUTPUT_CAP", "removable output capture washer", output_cap, output_cap, (0.95, 0.62, 0.08, 1.0), "20 mm OD capture washer; through-bolt/fastener selection and proof open"),
        ]
        parts.extend(axis_parts)
        per_axis_shapes[axis_id] = [part.shape for part in axis_parts]
        per_axis_parts[axis_id] = axis_parts
        installation.append({
            "axis_id": axis_id,
            "drive_id": candidate.drive_id,
            "joint_center_mm": f"({center.x:.3f}, {center.y:.3f}, {center.z:.3f})",
            "joint_axis_direction": f"({axis_dir.x:.0f}, {axis_dir.y:.0f}, {axis_dir.z:.0f})",
            "belt_centerline_direction": f"({drive_dir.x:.0f}, {drive_dir.y:.0f}, {drive_dir.z:.0f})",
            "external_drive_plane_offset_mm": f"{plane_offset:.3f}",
            "output_pulley_center_mm": f"({plane_center.x:.3f}, {plane_center.y:.3f}, {plane_center.z:.3f})",
            "motor_center_mm": f"({motor_center.x:.3f}, {motor_center.y:.3f}, {motor_center.z:.3f})",
            "solved_pitch_center_distance_mm": f"{solved_center:.9f}",
            "motor_pulley_code": candidate.motor_pulley_code,
            "output_pulley_code": candidate.output_pulley_code,
            "belt_code": candidate.belt_code,
            "actuator_source": source_id,
            "horn": horn_spec.horn_id,
            "motor_adapter": adapter_spec.adapter_id,
            "output_adapter": f"OS-P12-{abs(plane_offset):.0f}",
            "horn_contact_center_mm": f"({horn_contact.x:.3f}, {horn_contact.y:.3f}, {horn_contact.z:.3f})",
            "actuator_output_center_mm": f"({actuator_output.x:.3f}, {actuator_output.y:.3f}, {actuator_output.z:.3f})",
            "adapter_boundary": "NOMINAL SOLIDS INSTALLED; MATERIAL, FIT, TOLERANCE, FASTENER, RUNOUT, CAPACITY AND PHYSICAL PROOF OPEN",
            "warning": WARNING,
        })

    collisions: list[dict] = []
    axis_ids = sorted(per_axis_shapes)
    for index, first in enumerate(axis_ids):
        first_compound = cq.Compound.makeCompound(per_axis_shapes[first])
        for second in axis_ids[index + 1 :]:
            second_compound = cq.Compound.makeCompound(per_axis_shapes[second])
            common = first_compound.intersect(second_compound).Volume()
            distance = 0.0 if common > 1e-6 else first_compound.distance(second_compound)
            offenders = []
            if common > 1e-6:
                for first_part in per_axis_parts[first]:
                    for second_part in per_axis_parts[second]:
                        part_common = first_part.shape.intersect(second_part.shape).Volume()
                        if part_common > 1e-6:
                            offenders.append((part_common, first_part.part_id, second_part.part_id))
                offenders.sort(reverse=True)
            collisions.append({
                "first_axis": first,
                "second_axis": second,
                "common_volume_mm3": f"{common:.9f}",
                "minimum_nominal_distance_mm": f"{distance:.6f}",
                "state": "INTERFERENCE" if common > 1e-6 else "NO COMMON VOLUME",
                "overlapping_part_pairs": "; ".join(f"{a} x {b} = {volume:.6f} mm3" for volume, a, b in offenders) if offenders else "NONE",
                "scope": "RIGID PRODUCT/ACTUATOR/GUARD/SHAFT ENVELOPES; TOLERANCE, CABLES, DEFORMATION AND MOTION SWEEP EXCLUDED",
                "warning": WARNING,
            })
    return retained, parts, installation, collisions


def render_index() -> str:
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 installed leg drivetrains P0.1</title><script type="module" src="../vendor/model-viewer.min.js"></script><style>:root{{--deep:#081e38;--navy:#123b68;--pale:#eff9fe;--gold:#f2b91d;--line:#acd8ed;--ink:#152b43}}*{{box-sizing:border-box}}html,body{{max-width:100%;overflow-x:clip}}body{{margin:0;background:var(--pale);color:var(--ink);font:17px/1.55 system-ui,Segoe UI,sans-serif}}header,footer{{padding:32px max(20px,calc((100vw - 1200px)/2));background:var(--deep);color:white}}h1{{font-size:clamp(36px,6vw,66px);line-height:1.04}}h2{{font-size:clamp(28px,4vw,42px);color:var(--navy)}}.warning{{padding:16px;background:var(--gold);color:#17243a;border:3px solid #8a5b00;font-weight:900}}main{{max-width:1200px;margin:auto;padding:28px 20px 80px}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px}}.card,.viewer,.panel{{background:white;border:2px solid var(--line);border-radius:18px;padding:18px;overflow:hidden}}.metric{{font-size:34px;font-weight:900;color:var(--navy)}}model-viewer{{display:block;width:100%;height:clamp(560px,72vh,780px);background:radial-gradient(circle,#fff,var(--pale))}}a{{color:#075b9b;font-weight:800}}@media(max-width:560px){{body{{font-size:16px}}.grid{{grid-template-columns:1fr}}model-viewer{{height:520px}}}}</style></head><body><header><div class="warning">{html.escape(WARNING)}</div><h1>The exact candidate leg drives and adapters are installed on the complete robot.</h1><p>Ten generic ratio-only transmission placeholders are replaced by product-specific P-bore pulleys, belts, exact horns, shifted actuators, motor adapters, shouldered output shafts, capture washers and guard envelopes.</p></header><main><section><h2>Orbit the complete installation</h2><div class="viewer"><model-viewer src="HR-30_leg_drivetrains_installed_candidate.glb" alt="Complete preliminary HR-30 humanoid with ten product-specific leg drivetrains and physical adapters installed" camera-controls camera-orbit="28deg 76deg 100%" field-of-view="27deg" shadow-intensity="0.85" exposure="1.05"></model-viewer><p><a href="HR-30_leg_drivetrains_installed_candidate.step">Whole-body STEP</a> &middot; <a href="HR-30_installed_leg_drivetrains_only_candidate.step">drivetrains-only STEP</a> &middot; <a href="installed-drivetrain-register.csv">installation register</a>.</p></div></section><section><h2>Controlled installation boundary</h2><div class="grid"><article class="card"><div class="metric">10</div><p>reduced axes carry exact product candidates and nominal adapter solids.</p></article><article class="card"><div class="metric">3 + 2</div><p>motor-adapter and output-shaft families are reused bilaterally.</p></article><article class="card"><div class="metric">45 / 55 mm</div><p>pitch drives sit outboard; roll drives sit behind their bearing stacks.</p></article><article class="card"><div class="metric">0</div><p>nominal inter-drive common-volume pairs required for this package to pass.</p></article></div></section><section><h2>Still unresolved</h2><div class="panel"><p>The adapter solids close the nominal geometric gap, not the engineering release. Material, fits, tolerances, runout, fastener length/grade/locking/torque, pulley set-screw capacity, through-bolt retention, bearing-side load effects, guarding details, cable and cover sweep, tension, fatigue, mass/COM reconciliation, gait dynamics and physical validation remain open. The rigid-envelope screen grants no fabrication, motion or energization authority.</p></div></section></main><footer>Project Button &middot; HR-30 installed leg drivetrains P0.1 &middot; preliminary only</footer></body></html>'''


def integrate_root() -> None:
    status_path = WHOLE / "package-status.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    status.update({
        "installed_leg_drivetrain_whole_body_cad_present": True,
        "installed_leg_drivetrain_axis_count": 10,
        "installed_leg_drivetrain_pitch_plane_offset_mm": 45.0,
        "installed_leg_drivetrain_roll_plane_offset_mm": -55.0,
        "installed_leg_drivetrain_nominal_inter_axis_common_volume_count": 0,
        "installed_leg_drivetrain_motion_sweep_validated": False,
        "installed_leg_drivetrain_capacity_validated": False,
        "installed_leg_drivetrain_adapters_complete": True,
        "installed_leg_drivetrain_adapter_material_fit_fasteners_released": False,
        "installed_leg_drivetrain_adapter_physical_fit_validated": False,
        "fabrication_authority": False, "powered_test_authority": False,
        "motion_authority": False, "energization_authority": False,
    })
    status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")

    readme_path = WHOLE / "README.md"
    readme = readme_path.read_text(encoding="utf-8")
    start, end = "<!-- HR30-INSTALLED-LEG-DRIVES-P01-README-START -->", "<!-- HR30-INSTALLED-LEG-DRIVES-P01-README-END -->"
    if start in readme and end in readme:
        readme = readme.split(start, 1)[0] + readme.split(end, 1)[1]
    block = f'''{start}\n## Product-specific leg drives installed in the whole body\n\nThe [installed drivetrain guide](leg-drivetrain-installation-p0.1/index.html) replaces ten generic pulley/belt/motor placeholders in a derived complete humanoid assembly. Exact candidate P-bore pulleys, belts, HN12/HN13 horns, shifted manufacturer actuators, project motor adapters, shouldered output shafts, capture washers and guard envelopes occupy controlled external drive planes. All 45 inter-drive pairs have zero nominal common volume. Motion sweep, material, fits, tolerances, fasteners, cable/cover clearance, capacity and physical proof remain open.\n{end}\n'''
    marker = "<!-- HR30-ASSEMBLY-GUIDE-P01-START -->"
    if marker not in readme:
        raise RuntimeError("whole-body README integration marker missing")
    readme_path.write_text(readme.replace(marker, block + marker), encoding="utf-8", newline="\n")

    page_path = WHOLE / "index.html"
    page = page_path.read_text(encoding="utf-8")
    start, end = "<!-- HR30-INSTALLED-LEG-DRIVES-P01-START -->", "<!-- HR30-INSTALLED-LEG-DRIVES-P01-END -->"
    if start in page and end in page:
        page = page.split(start, 1)[0] + page.split(end, 1)[1]
    section = f'''{start}<section id="installed-leg-drives"><h2>The product-specific leg drives and adapters now occupy the complete humanoid</h2><div class="grid"><article class="card pass"><div class="metric">10 / 10</div><p>Reduced axes have exact candidate pulleys, belts, horns and nominal adapter solids.</p></article><article class="card pass"><div class="metric">45 pairs</div><p>Zero nominal inter-drive common-volume interference.</p></article><article class="card pass"><h3>External service planes</h3><p>Pitch drives sit outboard; roll drives sit behind their bearing stacks.</p></article><article class="card hold"><h3>Still preliminary</h3><p>Material, fits, fasteners, capacity, motion sweep, covers, cables, tolerances and physical proof remain open.</p></article></div><div class="viewer"><model-viewer src="leg-drivetrain-installation-p0.1/HR-30_leg_drivetrains_installed_candidate.glb" poster="front-elevation.svg" alt="Interactive complete HR-30 with ten product-specific leg drives and physical adapter solids installed" camera-controls camera-orbit="28deg 76deg 100%" field-of-view="27deg" shadow-intensity="0.85"></model-viewer><p><a href="leg-drivetrain-installation-p0.1/index.html">Open the installed-drive guide</a> · <a href="leg-drivetrain-installation-p0.1/installed-drivetrain-register.csv">installation register</a> · <a href="leg-drivetrain-installation-p0.1/inter-drive-clearance-register.csv">clearance screen</a>.</p></div></section>{end}'''
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
        "All twelve leg axes have static load screens. Ten belt-reduced axes now have exact MISUMI 5GT/EV5GT "
        "candidate geometry, exact HN12/HN13 horns, three motor-adapter variants and two shouldered output-shaft/capture "
        "variants installed on controlled external service planes in a complete-body CAD assembly; all 45 nominal "
        "inter-drive pairs have zero common volume. Material, fits, tolerances, runout, fastener details, bearing side "
        "loads, belt tension/capacity, motion and cable/cover sweeps, accepted trajectories, continuous torque, thermal "
        "limits, contact/impact, regeneration, fall restraint, gait correlation and physical proof remain open."
    )
    write_csv(holds_path, holds)


def status_payload(installation: list[dict], installed: list[InstalledPart], collisions: list[dict], interference_count: int) -> dict:
    return {
        "identifier": IDENTIFIER,
        "installed_axis_count": len(installation),
        "installed_component_count": len(installed),
        "pitch_drive_plane_offset_mm": 45.0,
        "roll_drive_plane_offset_mm": -55.0,
        "inter_axis_pair_count": len(collisions),
        "inter_axis_common_volume_count": interference_count,
        "nominal_rigid_envelope_inter_axis_screen_pass": interference_count == 0,
        "complete_humanoid_present": True,
        "whole_body_step_present": interference_count == 0,
        "whole_body_glb_present": interference_count == 0,
        "generic_reduced_drive_placeholders_removed": True,
        "exact_candidate_product_envelopes_installed": True,
        "motion_sweep_validated": False,
        "tolerance_validated": False,
        "cable_and_cover_clearance_validated": False,
        "horn_and_hub_adapter_nominal_geometry_complete": True,
        "horn_and_hub_adapter_material_fit_fasteners_released": False,
        "capacity_validated": False,
        "mass_com_reconciled": False,
        "physical_validation_complete": False,
        "procurement_authority": False,
        "fabrication_authority": False,
        "assembly_authority": False,
        "powered_test_authority": False,
        "motion_authority": False,
        "energization_authority": False,
        "warning": WARNING,
    }


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    retained, installed, installation, collisions = build_installed()
    interference_count = sum(float(row["common_volume_mm3"]) > 1e-6 for row in collisions)

    write_csv(OUT / "installed-drivetrain-register.csv", installation)
    write_csv(OUT / "inter-drive-clearance-register.csv", collisions)
    write_csv(OUT / "installed-component-register.csv", [{
        "axis_id": part.axis_id,
        "part_id": part.part_id,
        "kind": part.kind,
        "volume_mm3": f"{part.shape.Volume():.6f}",
        "bbox_x_mm": f"{part.shape.BoundingBox().xlen:.6f}",
        "bbox_y_mm": f"{part.shape.BoundingBox().ylen:.6f}",
        "bbox_z_mm": f"{part.shape.BoundingBox().zlen:.6f}",
        "note": part.note,
        "warning": WARNING,
    } for part in installed])

    status = status_payload(installation, installed, collisions, interference_count)
    (OUT / "installation-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    if interference_count:
        print(json.dumps(status, indent=2))
        return 2

    drivetrain_compound = cq.Compound.makeCompound([part.shape for part in installed])
    whole_compound = cq.Compound.makeCompound([component.shape for component in retained if component.physical] + [part.shape for part in installed])
    cq.exporters.export(drivetrain_compound, str(OUT / "HR-30_installed_leg_drivetrains_only_candidate.step"))
    cq.exporters.export(whole_compound, str(OUT / "HR-30_leg_drivetrains_installed_candidate.step"))
    body.canonicalize_step(OUT / "HR-30_installed_leg_drivetrains_only_candidate.step")
    body.canonicalize_step(OUT / "HR-30_leg_drivetrains_installed_candidate.step")

    drive_assembly = cq.Assembly(name="HR30_INSTALLED_LEG_DRIVES_P01_NOT_RELEASED")
    whole_assembly = cq.Assembly(name="HR30_WHOLE_BODY_WITH_INSTALLED_LEG_DRIVES_P01_NOT_RELEASED")
    for component in retained:
        whole_assembly.add(component.visual_shape if component.visual_shape is not None else component.shape, name=component.name, color=cq.Color(*component.color))
    for part in installed:
        drive_assembly.add(part.visual_shape, name=part.part_id, color=cq.Color(*part.color))
        whole_assembly.add(part.visual_shape, name=part.part_id, color=cq.Color(*part.color))
    drive_assembly.save(str(OUT / "HR-30_installed_leg_drivetrains_only_candidate.glb"), tolerance=0.16, angularTolerance=0.14)
    whole_assembly.save(str(OUT / "HR-30_leg_drivetrains_installed_candidate.glb"), tolerance=0.18, angularTolerance=0.16)

    (OUT / "installation-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    (OUT / "index.html").write_text(render_index(), encoding="utf-8", newline="\n")
    (OUT / "README.md").write_text(f"# HR-30 installed leg drivetrains P0.1\n\n**{WARNING}**\n\nA complete-body derived assembly replaces the ten generic reduced-leg pulley, belt and actuator placeholders with exact candidate product envelopes, exact horns, nominal motor adapters, shouldered output shafts and capture washers on external service planes. This is packaging CAD, not a released structure or capacity result.\n", encoding="utf-8", newline="\n")
    shutil.copy2(Path(__file__), OUT / "installed-leg-drivetrains-source.py")
    write_csv(OUT / "source-binding.csv", [
        {"source": "tools/generate_hr30_body_architecture_p01.py", "sha256": sha(ROOT / "tools" / "generate_hr30_body_architecture_p01.py"), "role": "complete 25-axis body and supported joint carriers", "warning": WARNING},
        {"source": "tools/generate_hr30_leg_drivetrain_p01.py", "sha256": sha(ROOT / "tools" / "generate_hr30_leg_drivetrain_p01.py"), "role": "exact candidate pulley/belt geometry and solved centers", "warning": WARNING},
        {"source": "tools/generate_hr30_leg_drivetrain_adapters_p01.py", "sha256": sha(ROOT / "tools" / "generate_hr30_leg_drivetrain_adapters_p01.py"), "role": "exact horn bindings plus editable motor adapter and output shaft/capture geometry", "warning": WARNING},
        {"source": "tools/generate_hr30_installed_leg_drivetrains_p01.py", "sha256": sha(Path(__file__)), "role": "installation transforms, external planes and derived assemblies", "warning": WARNING},
    ])
    files = sorted(path for path in OUT.rglob("*") if path.is_file() and path.name != "file-manifest.csv")
    write_csv(OUT / "file-manifest.csv", [{"path": path.relative_to(OUT).as_posix(), "bytes": path.stat().st_size, "sha256": sha(path), "warning": WARNING} for path in files])

    integrate_root()
    system.refresh_manifest_and_release()
    print(json.dumps(status, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
