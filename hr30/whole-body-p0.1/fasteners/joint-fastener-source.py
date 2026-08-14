"""Generate located joint-carrier fastener candidates for the HR-30 whole body.

This converts every existing four-hole joint-module carrier into explicit,
editable screw geometry.  The metric sizes, lengths, material density and
engagement are P0.1 planning candidates only: no torque, preload, tapped-side
material, locking method, strength, fatigue, procurement or work authority is
released by this package.
"""

from __future__ import annotations

import csv
import hashlib
import html
import json
import shutil
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

import cadquery as cq

import generate_hr30_body_architecture_p01 as body


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "hr30" / "whole-body-p0.1"
OUT = PACKAGE / "fasteners"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / "fasteners"
IDENTIFIER = "HR30-JOINT-FASTENER-CANDIDATES-P0.1"
WARNING = body.WARNING
STEEL_DENSITY_KG_M3 = 7850.0


FASTENER_FAMILIES = {
    "M3": {"nominal_d_mm": 3.0, "head_d_mm": 5.5, "head_h_mm": 3.0, "length_mm": 10.0, "hole_max_mm": 3.5},
    "M4": {"nominal_d_mm": 4.0, "head_d_mm": 7.0, "head_h_mm": 4.0, "length_mm": 12.0, "hole_max_mm": 4.6},
    "M5": {"nominal_d_mm": 5.0, "head_d_mm": 8.5, "head_h_mm": 5.0, "length_mm": 16.0, "hole_max_mm": 5.6},
}


@dataclass(frozen=True)
class Fastener:
    fastener_id: str
    axis_id: str
    module_id: str
    dynamic_link: str
    family_id: str
    carrier_end: str
    hole_index: int
    candidate_size: str
    shape: cq.Shape
    row: dict


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise RuntimeError(f"refusing empty CSV {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def module_for_axis(axis_id: str) -> str:
    if axis_id.startswith("HEAD_"):
        return "N01"
    if axis_id == "WAIST_YAW":
        return "P01"
    if axis_id.startswith("L_SHOULDER") or axis_id.startswith("L_ELBOW") or axis_id.startswith("L_WRIST"):
        return "A01"
    if axis_id.startswith("R_SHOULDER") or axis_id.startswith("R_ELBOW") or axis_id.startswith("R_WRIST"):
        return "A02"
    if axis_id == "L_GRIPPER":
        return "G01"
    if axis_id == "R_GRIPPER":
        return "G02"
    if axis_id.startswith("L_"):
        return "L01"
    if axis_id.startswith("R_"):
        return "L02"
    raise KeyError(axis_id)


def dynamic_link_for_axis(axis_id: str) -> str:
    if axis_id == "WAIST_YAW":
        return "base_link"
    if axis_id == "HEAD_PAN":
        return "neck_pan_link"
    if axis_id == "HEAD_TILT":
        return "head"
    side = axis_id[0]
    if "SHOULDER_PITCH" in axis_id:
        return f"{side}_shoulder_pitch_link"
    if "SHOULDER_ROLL" in axis_id or "ELBOW_PITCH" in axis_id:
        return f"{side}_upper_arm"
    if "WRIST_ROTATION" in axis_id:
        return f"{side}_forearm"
    if "GRIPPER" in axis_id:
        return f"{side}_hand"
    if any(token in axis_id for token in ("HIP_YAW", "HIP_ROLL", "HIP_PITCH", "KNEE_PITCH")):
        return f"{side}_thigh"
    if any(token in axis_id for token in ("ANKLE_PITCH", "ANKLE_ROLL")):
        return f"{side}_shin"
    raise KeyError(axis_id)


def size_for_hole(hole_d_mm: float) -> tuple[str, dict]:
    for name, spec in FASTENER_FAMILIES.items():
        if hole_d_mm <= spec["hole_max_mm"]:
            return name, spec
    raise RuntimeError(f"no candidate screw for {hole_d_mm} mm carrier hole")


def screw_shape(
    hole_center: cq.Vector,
    outward: cq.Vector,
    plate_t_mm: float,
    spec: dict,
) -> cq.Shape:
    """Socket-head envelope with shank passing from the outer carrier face inward."""
    outside_face = hole_center + outward.multiply(plate_t_mm / 2.0)
    inward = outward.multiply(-1.0)
    shank_center = outside_face + inward.multiply(spec["length_mm"] / 2.0)
    head_center = outside_face + outward.multiply(spec["head_h_mm"] / 2.0)
    shank = body.cylinder_between(
        (shank_center.x, shank_center.y, shank_center.z),
        (inward.x, inward.y, inward.z),
        spec["length_mm"],
        spec["nominal_d_mm"],
    )
    head = body.cylinder_between(
        (head_center.x, head_center.y, head_center.z),
        (outward.x, outward.y, outward.z),
        spec["head_h_mm"],
        spec["head_d_mm"],
    )
    return shank.fuse(head)


def build(axes: list[dict] | None = None) -> list[Fastener]:
    if axes is None:
        _components, axes, _bindings, _transforms = body.build()
    fasteners: list[Fastener] = []
    for axis in axes:
        axis_id = axis["axis_id"]
        family_id = body.joint_module_family(axis_id)
        family = body.JOINT_MODULE_FAMILIES[family_id]
        center = cq.Vector(float(axis["x_mm"]), float(axis["y_mm"]), float(axis["z_mm"]))
        normal = cq.Vector(float(axis["direction_x"]), float(axis["direction_y"]), float(axis["direction_z"])).normalized()
        plane = body.local_plane((center.x, center.y, center.z), (normal.x, normal.y, normal.z))
        candidate_size, screw_spec = size_for_hole(float(family["hole_d"]))
        ends = (("A", -1.0), ("B", 1.0)) if family["external_bearings"] == 2 else (("B", 1.0),)
        for end_name, sign_end in ends:
            outward = normal.multiply(sign_end)
            plate_center = center + outward.multiply(family["span"] / 2.0 + family["plate_t"] / 2.0)
            carrier = body.interface_plate(
                (plate_center.x, plate_center.y, plate_center.z),
                (normal.x, normal.y, normal.z),
                family["plate_w"], family["plate_h"], family["plate_t"],
                family["pattern_x"], family["pattern_y"], family["hole_d"], family["shaft_d"],
            )
            # Read the four real clearance-cylinder centers back from the exact
            # carrier B-Rep.  This avoids assuming CadQuery's face-workplane
            # in-plane orientation and binds the screws to the manufactured
            # hole geometry rather than merely repeating nominal coordinates.
            cylindrical_centers = [face.Center() for face in carrier.Faces() if face.geomType() == "CYLINDER"]
            unique_centers: dict[tuple[float, float, float], cq.Vector] = {}
            for candidate in cylindrical_centers:
                unique_centers[(round(candidate.x, 6), round(candidate.y, 6), round(candidate.z, 6))] = candidate
            hole_centers = sorted(
                unique_centers.values(),
                key=lambda candidate: (candidate - plate_center).Length,
                reverse=True,
            )[:4]
            if len(hole_centers) != 4 or min((candidate - plate_center).Length for candidate in hole_centers) < 5.0:
                raise RuntimeError(f"could not recover four physical carrier holes for {axis_id} {end_name}")
            hole_centers.sort(key=lambda candidate: (
                round((candidate - plate_center).dot(plane.xDir), 6),
                round((candidate - plate_center).dot(plane.yDir), 6),
            ))
            for hole_index, hole_center in enumerate(hole_centers, 1):
                shape = screw_shape(hole_center, outward, family["plate_t"], screw_spec)
                fastener_id = f"JF-{axis_id}-{end_name}-{hole_index}"
                volume_mm3 = float(shape.Volume())
                mass_kg = volume_mm3 * 1e-9 * STEEL_DENSITY_KG_M3
                clearance = float(family["hole_d"]) - screw_spec["nominal_d_mm"]
                engagement = screw_spec["length_mm"] - float(family["plate_t"])
                row = {
                    "fastener_id": fastener_id,
                    "axis_id": axis_id,
                    "module_id": module_for_axis(axis_id),
                    "dynamic_link": dynamic_link_for_axis(axis_id),
                    "joint_module_family": family_id,
                    "carrier_end": end_name,
                    "hole_index": hole_index,
                    "candidate_size": candidate_size,
                    "candidate_form": "METRIC SOCKET-HEAD CAP-SCREW GEOMETRY CANDIDATE",
                    "nominal_diameter_mm": f"{screw_spec['nominal_d_mm']:.3f}",
                    "carrier_clearance_hole_diameter_mm": f"{family['hole_d']:.3f}",
                    "diametral_clearance_mm": f"{clearance:.3f}",
                    "candidate_length_under_head_mm": f"{screw_spec['length_mm']:.3f}",
                    "carrier_plate_thickness_mm": f"{family['plate_t']:.3f}",
                    "provisional_thread_engagement_mm": f"{engagement:.3f}",
                    "head_diameter_mm": f"{screw_spec['head_d_mm']:.3f}",
                    "head_height_mm": f"{screw_spec['head_h_mm']:.3f}",
                    "hole_center_xyz_mm": f"({hole_center.x:.6f}, {hole_center.y:.6f}, {hole_center.z:.6f})",
                    "outward_access_direction": f"({outward.x:.0f}, {outward.y:.0f}, {outward.z:.0f})",
                    "cad_volume_mm3": f"{volume_mm3:.6f}",
                    "generic_steel_density_screen_kg_m3": f"{STEEL_DENSITY_KG_M3:.1f}",
                    "planning_mass_kg": f"{mass_kg:.9f}",
                    "retention_boundary": "TAPPED COMPANION / INSERT AND LOCKING METHOD SELECTION REQUIRED; NO TORQUE OR PRELOAD CREDIT",
                    "release_state": "LOCATED P0.1 HARDWARE CANDIDATE - EXACT FASTENER, MATERIAL, THREAD, TORQUE, PRELOAD, LOCKING, ACCESS AND PROOF OPEN",
                    "warning": WARNING,
                }
                fasteners.append(Fastener(fastener_id, axis_id, row["module_id"], row["dynamic_link"], family_id, end_name, hole_index, candidate_size, shape, row))
    return fasteners


def render_index(summary: dict) -> str:
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 joint fastener candidates P0.1</title><script type="module" src="../vendor/model-viewer.min.js"></script><style>
:root{{--deep:#0b203a;--navy:#132f55;--sky:#77c9f2;--gold:#f2b91d;--pale:#eef8fd;--line:#b8d7e8;--ink:#17243a}}*{{box-sizing:border-box}}body{{margin:0;background:var(--pale);color:var(--ink);font:17px/1.55 system-ui,-apple-system,Segoe UI,sans-serif}}header{{background:var(--deep);color:white;padding:36px max(20px,calc((100vw - 1200px)/2))}}main{{max-width:1200px;margin:auto;padding:28px 20px 80px}}h1{{font-size:clamp(36px,5vw,64px);line-height:1.04;margin:.35em 0}}h2{{font-size:clamp(27px,3vw,40px);color:var(--navy)}}.warning{{background:var(--gold);color:var(--ink);border:3px solid #8a5b00;padding:16px 18px;font-weight:900}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px}}.card,.viewer,.panel{{background:white;border:2px solid var(--line);border-radius:16px;padding:18px;overflow:hidden}}.metric{{font-size:36px;font-weight:900;color:var(--navy)}}model-viewer{{display:block;width:100%;height:660px;background:radial-gradient(circle,#fff,var(--pale))}}a{{color:#075b9b;font-weight:800}}footer{{background:var(--deep);color:white;padding:28px max(20px,calc((100vw - 1200px)/2))}}@media(max-width:600px){{model-viewer{{height:520px}}}}
</style></head><body><header><div class="warning">{WARNING}</div><h1>The whole robot now has located joint fasteners.</h1><p>Every screw passes through an actual four-hole joint-carrier opening. This is a geometric and mass-planning candidate, not a released fastener specification.</p></header><main><section><h2>Whole-body hardware population</h2><div class="grid"><article class="card"><div class="metric">{summary['fastener_count']}</div><p>located screw candidates across all 25 axes</p></article><article class="card"><div class="metric">{summary['carrier_plate_count']}</div><p>carrier plates, each with four occupied holes</p></article><article class="card"><div class="metric">{summary['planning_mass_kg']:.3f} kg</div><p>generic-steel CAD density screen</p></article><article class="card"><div class="metric">M3 / M4 / M5</div><p>candidate nominal sizes derived from the existing carrier clearances</p></article></div></section><section><h2>Fastened whole-body view</h2><div class="viewer"><model-viewer src="HR-30_fastened_whole_body_candidate.glb" poster="../front-elevation.svg" alt="Interactive complete HR-30 body with located joint fastener candidates" camera-controls shadow-intensity="0.8" exposure="1.05"></model-viewer><p><a href="HR-30_joint_fastener_candidates.step">Fastener STEP</a> · <a href="joint-fastener-register.csv">Per-fastener register</a> · <a href="joint-fastener-family-summary.csv">Family summary</a> · <a href="joint-fastener-source.py">Editable source</a></p></div></section><section><h2>What remains open</h2><div class="panel"><p>The tapped companion material, inserts, exact product and property class, washers, locking method, installation torque, preload, joint separation/slip/prying, fatigue, access tooling, reuse policy, witness marks and physical proof remain unresolved. No procurement, fabrication, assembly, powered-test, motion, or energization authority follows.</p></div></section></main><footer>Project Button · HR-30 joint fasteners P0.1 · preliminary candidate only</footer></body></html>'''


def update_package(summary: dict) -> None:
    status_path = PACKAGE / "package-status.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    status.update({
        "joint_fastener_candidate_geometry_present": True,
        "joint_fastener_candidate_count": summary["fastener_count"],
        "joint_fastener_carrier_plate_count": summary["carrier_plate_count"],
        "joint_fastener_candidate_mass_kg": summary["planning_mass_kg"],
        "joint_fastener_hole_alignment_screen_complete": True,
        "joint_fastener_selected": False,
        "joint_fastener_preload_validated": False,
    })
    status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")

    holds_path = PACKAGE / "open-holds.csv"
    holds = list(csv.DictReader(holds_path.open(encoding="utf-8")))
    for row in holds:
        if row["hold_id"] == "HR30-P01-H01":
            row["unresolved_item"] = (
                f"All 25 axes now have dimensioned module bindings and {summary['fastener_count']} located M3/M4/M5 screw candidates occupying all {summary['carrier_plate_count']} four-hole carriers. "
                "Exact products/property classes, tapped-side material/inserts, torque, preload, locking, access, joint separation/slip/prying, fatigue, continuous/dynamic duty and physical proof remain open."
            )
    write_csv(holds_path, holds)

    readme_path = PACKAGE / "README.md"
    readme = readme_path.read_text(encoding="utf-8")
    marker = "\n## Separable module CAD\n"
    addition = (
        "\n## Located joint fastener candidates\n\n"
        f"The whole-body joint carriers now contain {summary['fastener_count']} explicit M3/M4/M5 socket-head geometry candidates across {summary['carrier_plate_count']} plates. Every screw axis is generated from the same joint datum and carrier pattern as the body CAD. The {summary['planning_mass_kg']:.3f} kg generic-steel screen is included in mass reconciliation, but exact products, threads, tapped members, torque, preload, locking, access and physical proof remain open.\n"
    )
    if "## Located joint fastener candidates" not in readme:
        if marker not in readme:
            raise RuntimeError("README insertion marker missing")
        readme = readme.replace(marker, addition + marker)
    readme_path.write_text(readme, encoding="utf-8", newline="\n")

    page_path = PACKAGE / "index.html"
    page = page_path.read_text(encoding="utf-8")
    start, end = "<!-- HR30-JOINT-FASTENERS-P01-START -->", "<!-- HR30-JOINT-FASTENERS-P01-END -->"
    if start in page and end in page:
        page = page.split(start, 1)[0] + page.split(end, 1)[1]
    marker = '<section id="module-cad">'
    section = f'''{start}<section id="joint-fasteners"><h2>Every joint carrier now has located fasteners</h2><div class="grid"><article class="card pass"><div class="metric">{summary['fastener_count']}</div><p>M3/M4/M5 screw candidates occupy every carrier hole.</p></article><article class="card pass"><div class="metric">{summary['carrier_plate_count']}</div><p>four-hole carrier plates are populated across all 25 axes.</p></article><article class="card hold"><div class="metric">{summary['planning_mass_kg']:.3f} kg</div><p>generic-steel planning screen; received hardware mass remains open.</p></article><article class="card hold"><h3>No joint release</h3><p>Torque, preload, locking, tapped-side material, access, strength and fatigue remain unresolved.</p></article></div><div class="viewer"><model-viewer src="fasteners/HR-30_fastened_whole_body_candidate.glb" poster="front-elevation.svg" alt="Interactive complete HR-30 body with located joint fastener candidates" camera-controls shadow-intensity="0.8" exposure="1.05"></model-viewer><p><a href="fasteners/index.html">Open the fastener guide</a> · <a href="fasteners/HR-30_joint_fastener_candidates.step">Fastener STEP</a> · <a href="fasteners/joint-fastener-register.csv">Per-fastener register</a>.</p></div></section>{end}'''
    if marker not in page:
        raise RuntimeError("main page fastener insertion marker missing")
    page_path.write_text(page.replace(marker, section + marker), encoding="utf-8", newline="\n")


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    components, axes, _bindings, _transforms = body.build()
    fasteners = build(axes)
    rows = [item.row for item in fasteners]
    counts = Counter(item.candidate_size for item in fasteners)
    plate_count = len({(item.axis_id, item.carrier_end) for item in fasteners})
    total_mass = sum(float(item.row["planning_mass_kg"]) for item in fasteners)
    summary = {
        "identifier": IDENTIFIER,
        "axis_count": len({item.axis_id for item in fasteners}),
        "carrier_plate_count": plate_count,
        "fastener_count": len(fasteners),
        "m3_count": counts["M3"], "m4_count": counts["M4"], "m5_count": counts["M5"],
        "planning_mass_kg": round(total_mass, 9),
        "steel_density_screen_kg_m3": STEEL_DENSITY_KG_M3,
        "all_carrier_holes_occupied": len(fasteners) == plate_count * 4,
        "fasteners_selected": False,
        "torque_preload_locking_validated": False,
        "procurement_authority": False, "fabrication_authority": False,
        "assembly_authority": False, "powered_test_authority": False,
        "motion_authority": False, "energization_authority": False,
        "warning": WARNING,
    }
    if summary["axis_count"] != 25 or plate_count != 39 or len(fasteners) != 156 or counts != Counter({"M5": 92, "M4": 40, "M3": 24}):
        raise RuntimeError(f"whole-body fastener population drift: {summary}")
    if any(float(row["diametral_clearance_mm"]) <= 0 for row in rows):
        raise RuntimeError("fastener shank does not clear carrier hole")

    fastener_assembly = cq.Assembly(name="HR30_JOINT_FASTENERS_P01_NOT_RELEASED")
    for item in fasteners:
        fastener_assembly.add(item.shape, name=item.fastener_id, color=cq.Color(0.18, 0.21, 0.25, 1.0))
    fastener_step = OUT / "HR-30_joint_fastener_candidates.step"
    fastener_assembly.save(str(fastener_step))

    complete = cq.Assembly(name="HR30_FASTENED_WHOLE_BODY_P01_NOT_RELEASED")
    for component in components:
        if component.physical:
            complete.add(component.visual_shape or component.shape, name=component.name, color=cq.Color(*component.color))
    for item in fasteners:
        complete.add(item.shape, name=item.fastener_id, color=cq.Color(0.08, 0.10, 0.13, 1.0))
    complete.save(str(OUT / "HR-30_fastened_whole_body_candidate.glb"), tolerance=0.50, angularTolerance=0.25)

    write_csv(OUT / "joint-fastener-register.csv", rows)
    family_rows = []
    for size, spec in FASTENER_FAMILIES.items():
        subset = [item for item in fasteners if item.candidate_size == size]
        family_rows.append({
            "candidate_size": size, "quantity": len(subset),
            "nominal_diameter_mm": spec["nominal_d_mm"], "candidate_length_under_head_mm": spec["length_mm"],
            "head_diameter_mm": spec["head_d_mm"], "head_height_mm": spec["head_h_mm"],
            "carrier_hole_diameters_mm": "; ".join(sorted({item.row["carrier_clearance_hole_diameter_mm"] for item in subset})),
            "planning_mass_kg": f"{sum(float(item.row['planning_mass_kg']) for item in subset):.9f}",
            "selection_boundary": "GEOMETRY/DENSITY CANDIDATE ONLY; EXACT PRODUCT, PROPERTY CLASS, THREAD, TORQUE, PRELOAD AND LOCKING REQUIRED",
            "warning": WARNING,
        })
    write_csv(OUT / "joint-fastener-family-summary.csv", family_rows)
    (OUT / "joint-fastener-status.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    (OUT / "index.html").write_text(render_index(summary), encoding="utf-8", newline="\n")
    (OUT / "README.md").write_text(
        f"# HR-30 joint fastener candidates P0.1\n\n**{WARNING}**\n\nThis package places {len(fasteners)} editable screw envelopes through every actual joint-carrier hole. Exact products, property classes, tapped members/inserts, torque, preload, locking, access, strength, fatigue and physical proof remain open.\n",
        encoding="utf-8", newline="\n",
    )
    shutil.copy2(Path(__file__), OUT / "joint-fastener-source.py")
    update_package(summary)
    sys.path.insert(0, str(ROOT / "tools"))
    import generate_hr30_system_package_p01 as system
    system.refresh_manifest_and_release()
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
