"""Generate the exact-coordinate HR-V0 arm architecture candidate for R54.

The exported geometry is a feasibility/configuration candidate.  It is not a
fabrication release: the 80/20 section is represented by its conservative
20 x 40 mm envelope and all fastener, tolerance and proof requirements remain
open.
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


ROOT = Path(__file__).resolve().parents[1]
VENDOR = ROOT / "cad" / "vendor" / "robotis"
OUT = ROOT / "cad" / "hr-v0" / "generated" / "arm-architecture-p0.1"
REVISION = "HR-V0-ARM-ARCH-P0.1"
WARNING = "PRELIMINARY - CANDIDATE GEOMETRY ONLY - NOT RELEASED FOR FABRICATION OR ENERGIZATION"

J2_Y = 191.5
G1_Y = 309.5
PLATE_T = 4.0
UPPER_BEAM_L = 100.0
FOREARM_BEAM_L = 50.0
PCD_D = 22.0
PCD_HOLE_D = 2.70
END_HOLE_D = 5.50


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


def adapter(y0: float) -> cq.Shape:
    solid = cq.Solid.makeBox(48.0, PLATE_T, 36.0, cq.Vector(-24.0, y0, -18.0))
    for index in range(8):
        angle = math.radians(index * 45.0)
        x = (PCD_D / 2.0) * math.cos(angle)
        z = (PCD_D / 2.0) * math.sin(angle)
        hole = cq.Solid.makeCylinder(PCD_HOLE_D / 2.0, PLATE_T, cq.Vector(x, y0, z), cq.Vector(0, 1, 0))
        solid = solid.cut(hole)
    for x in (-10.0, 10.0):
        hole = cq.Solid.makeCylinder(END_HOLE_D / 2.0, PLATE_T, cq.Vector(x, y0, 0), cq.Vector(0, 1, 0))
        solid = solid.cut(hole)
    return solid


def beam(y0: float, length: float) -> cq.Shape:
    # Conservative collision envelope.  The real 20-2040 slot/core geometry is
    # deliberately not invented; it must come from received stock or controlled
    # manufacturer CAD before a fabrication release.
    return cq.Solid.makeBox(40.0, length, 20.0, cq.Vector(-20.0, y0, -10.0))


def matrix_x(angle_deg: float, tx: float, ty: float, tz: float) -> list[list[float]]:
    c = round(math.cos(math.radians(angle_deg)), 12)
    s = round(math.sin(math.radians(angle_deg)), 12)
    return [[1.0, 0.0, 0.0, tx], [0.0, c, -s, ty], [0.0, s, c, tz], [0.0, 0.0, 0.0, 1.0]]


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def positive_intersection(a: cq.Shape, b: cq.Shape) -> float:
    try:
        return max(0.0, a.intersect(b).Volume())
    except Exception:
        return float("inf")


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    xm540 = import_step("XMHD-540.N101.I101.STP")
    h101 = import_step("FR13-H101K.stp")
    s102 = import_step("FR13-S102K.stp")
    h104 = import_step("FR12-H104K.stp")

    # Reference pose: J1 and J2 axes are parallel +X.  The J2 body is rolled
    # +90 degrees about X to make the S102 outside face oppose the H101 face.
    # The J2 output reference offset is -90 degrees, returning the output H101
    # and straight forearm to the project +Y direction.
    j1_body = xm540
    j1_h101 = h101
    upper_p = adapter(32.0)
    upper_b = beam(36.0, UPPER_BEAM_L)
    upper_d = adapter(136.0)
    j2_body = rotate_x(xm540, 90.0).translate((0.0, J2_Y, 0.0))
    j2_s102 = rotate_x(s102, 90.0).translate((0.0, J2_Y, 0.0))
    j2_h101 = h101.translate((0.0, J2_Y, 0.0))
    fore_p = adapter(223.5)
    fore_b = beam(227.5, FOREARM_BEAM_L)
    fore_d = adapter(277.5)
    gripper_frame = rotate_x(h104, 180.0).translate((0.0, G1_Y, 0.0))

    components = {
        "J1_XM540": j1_body,
        "J1_H101": j1_h101,
        "UL_PROX_ADAPTER": upper_p,
        "UL_20-2040_ENVELOPE": upper_b,
        "UL_DIST_ADAPTER": upper_d,
        "J2_XM540_RX90": j2_body,
        "J2_S102_RX90": j2_s102,
        "J2_H101_OUTPUT_REFERENCE": j2_h101,
        "FA_PROX_ADAPTER": fore_p,
        "FA_20-2040_50MM_ENVELOPE": fore_b,
        "FA_DIST_ADAPTER": fore_d,
        "G1_H104_RX180": gripper_frame,
    }

    assembly = cq.Assembly(name="HR_V0_ARM_ARCHITECTURE_CANDIDATE_NOT_RELEASED")
    colors = {
        "J1_XM540": cq.Color(0.05, 0.25, 0.50),
        "J2_XM540_RX90": cq.Color(0.05, 0.25, 0.50),
        "J1_H101": cq.Color(0.95, 0.70, 0.10),
        "J2_H101_OUTPUT_REFERENCE": cq.Color(0.95, 0.70, 0.10),
        "J2_S102_RX90": cq.Color(0.40, 0.78, 0.96),
        "G1_H104_RX180": cq.Color(0.40, 0.78, 0.96),
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
        "MV0-C01_pcd22_to_20-2040_adapter": adapter(0.0),
        "MV0-C02_20-2040_100mm_collision_envelope": beam(0.0, UPPER_BEAM_L),
        "MV0-C03_20-2040_50mm_collision_envelope": beam(0.0, FOREARM_BEAM_L),
    }.items():
        part_path = part_dir / f"{name}.step"
        cq.exporters.export(solid, str(part_path))
        canonicalize_step(part_path)

    transform_rows = [
        {"item": "J1 body", "parent": "WORLD", "tx_mm": 0, "ty_mm": 0, "tz_mm": 0, "rx_deg": 0, "matrix_4x4_row_major": json.dumps(matrix_x(0, 0, 0, 0)), "status": "candidate datum"},
        {"item": "J1 H101 output reference", "parent": "J1 output", "tx_mm": 0, "ty_mm": 0, "tz_mm": 0, "rx_deg": 0, "matrix_4x4_row_major": json.dumps(matrix_x(0, 0, 0, 0)), "status": "exact vendor geometry; fastener stack open"},
        {"item": "J2 body and S102", "parent": "WORLD", "tx_mm": 0, "ty_mm": J2_Y, "tz_mm": 0, "rx_deg": 90, "matrix_4x4_row_major": json.dumps(matrix_x(90, 0, J2_Y, 0)), "status": "architecture candidate"},
        {"item": "J2 H101 straight-reference pose", "parent": "WORLD", "tx_mm": 0, "ty_mm": J2_Y, "tz_mm": 0, "rx_deg": 0, "matrix_4x4_row_major": json.dumps(matrix_x(0, 0, J2_Y, 0)), "status": "requires -90 deg output offset relative J2 body"},
        {"item": "G1 H104 frame", "parent": "WORLD", "tx_mm": 0, "ty_mm": G1_Y, "tz_mm": 0, "rx_deg": 180, "matrix_4x4_row_major": json.dumps(matrix_x(180, 0, G1_Y, 0)), "status": "candidate frame only; gripper transform open"},
    ]
    write_csv(OUT / "transform-schedule.csv", transform_rows)

    interface_rows = [
        {"interface": "A01", "from": "J1 H101 outside broad face", "to": "upper proximal adapter", "plane_world": "Y=32.0 mm", "pattern": "8 x dia 2.5 manufacturer thru on PCD22; candidate adapter dia 2.70", "fasteners": "SELECTION REQUIRED", "status": "geometrically_registered_not_released"},
        {"interface": "A02", "from": "upper proximal adapter", "to": "20-2040 end", "plane_world": "Y=36.0 mm", "pattern": "candidate two-hole M5 end-tap route at X=+/-10 mm; exact controlled profile CAD/received inspection required", "fasteners": "SELECTION REQUIRED", "status": "envelope_candidate_only"},
        {"interface": "A03", "from": "20-2040 end", "to": "upper distal adapter", "plane_world": "Y=136.0 mm", "pattern": "candidate two-hole M5 end-tap route at X=+/-10 mm; exact controlled profile CAD/received inspection required", "fasteners": "SELECTION REQUIRED", "status": "envelope_candidate_only"},
        {"interface": "A04", "from": "upper distal adapter", "to": "J2 S102 outside broad face", "plane_world": "Y=140.0 mm", "pattern": "8 x dia 2.5 manufacturer thru on PCD22; candidate adapter dia 2.70", "fasteners": "SELECTION REQUIRED", "status": "geometrically_registered_not_released"},
        {"interface": "A05", "from": "J2 H101 outside broad face", "to": "forearm proximal adapter", "plane_world": "Y=223.5 mm at straight reference", "pattern": "8 x dia 2.5 manufacturer thru on PCD22; candidate adapter dia 2.70", "fasteners": "SELECTION REQUIRED", "status": "geometrically_registered_not_released"},
        {"interface": "A06", "from": "forearm beam", "to": "forearm adapters", "plane_world": "Y=227.5 and 277.5 mm at straight reference", "pattern": "candidate two-hole M5 end-tap route; exact controlled profile CAD/received inspection required", "fasteners": "SELECTION REQUIRED", "status": "envelope_candidate_only"},
        {"interface": "A07", "from": "forearm distal adapter", "to": "H104 outside broad face", "plane_world": "Y=281.5 mm at straight reference", "pattern": "manufacturer broad-face pattern; final subset and adapter holes SELECTION REQUIRED", "fasteners": "SELECTION REQUIRED", "status": "transform_candidate_pattern_open"},
    ]
    write_csv(OUT / "interface-schedule.csv", interface_rows)

    fixed_upper = [j1_body, j1_h101, upper_p, upper_b, upper_d, j2_body, j2_s102]
    moving_zero = [j2_h101, fore_p, fore_b, fore_d, gripper_frame]
    sweep_rows: list[dict[str, object]] = []
    worst = 0.0
    for q_deg in range(15, 126, 5):
        moving = [rotate_x(item, q_deg, J2_Y) for item in moving_zero]
        volume = sum(positive_intersection(a, b) for a in fixed_upper for b in moving)
        worst = max(worst, volume)
        sweep_rows.append({"j2_internal_deg": q_deg, "sampled_pairwise_intersection_mm3": f"{volume:.6f}", "result": "PASS" if volume <= 1e-5 else "COLLISION", "scope": "self-collision screen only; cables, tools, guards, stops and unsampled poses excluded"})
    write_csv(OUT / "collision-sweep.csv", sweep_rows)

    mass_per_m_kg = 0.0428 * 0.45359237 / 0.0254
    upper_beam_mass_g = mass_per_m_kg * (UPPER_BEAM_L / 1000.0) * 1000.0
    forearm_beam_mass_g = mass_per_m_kg * (FOREARM_BEAM_L / 1000.0) * 1000.0
    gross_plate_mass_g = 48.0 * 36.0 * PLATE_T / 1000.0 * 2.70
    removed_volume = 8 * math.pi * (PCD_HOLE_D / 2) ** 2 * PLATE_T + 2 * math.pi * (END_HOLE_D / 2) ** 2 * PLATE_T
    plate_mass_g = gross_plate_mass_g - removed_volume / 1000.0 * 2.70
    upper_link_mass_g = upper_beam_mass_g + 2 * plate_mass_g
    forearm_link_mass_g = forearm_beam_mass_g + 2 * plate_mass_g
    gravity = 9.80665
    shoulder_nm = gravity * (0.12 * 0.086 + 0.20 * 0.1915 + 0.12 * 0.2505 + 0.21 * 0.3095 + 0.10 * 0.360)
    elbow_nm = gravity * (0.12 * 0.059 + 0.21 * 0.118 + 0.10 * 0.1685)
    summary = {
        "revision": REVISION,
        "warning": WARNING,
        "disposition": "exact-coordinate architecture candidate; no part or fastener released",
        "vendor_source_sha256": {name: sha256(VENDOR / name) for name in ("XMHD-540.N101.I101.STP", "FR13-H101K.stp", "FR13-S102K.stp", "FR12-H104K.stp")},
        "candidate_geometry_mm": {
            "j1_to_j2_axis": J2_Y,
            "j2_to_g1_frame_origin": G1_Y - J2_Y,
            "j1_to_g1_frame_origin": G1_Y,
            "adapter_thickness": PLATE_T,
            "upper_beam_envelope": [40.0, UPPER_BEAM_L, 20.0],
            "forearm_beam_envelope": [40.0, FOREARM_BEAM_L, 20.0],
            "reserved_g1_to_object_center_max": 360.0 - G1_Y,
            "pcd_diameter": PCD_D,
        },
        "axis_parallelism_math": {"j1_direction": [1, 0, 0], "j2_direction": [1, 0, 0], "dot_product": 1.0, "angular_difference_deg": 0.0},
        "reference_output_offset_deg": -90.0,
        "collision_screen": {"sampled_j2_range_deg": [15, 125], "increment_deg": 5, "maximum_positive_intersection_mm3": round(worst, 6), "scope": "self-collision only"},
        "mass_and_load_screen": {
            "20_2040_mass_basis_kg_per_m": round(mass_per_m_kg, 6),
            "one_100mm_upper_beam_mass_g": round(upper_beam_mass_g, 3),
            "one_50mm_forearm_beam_mass_g": round(forearm_beam_mass_g, 3),
            "one_adapter_candidate_mass_g": round(plate_mass_g, 3),
            "upper_beam_plus_two_adapters_mass_g": round(upper_link_mass_g, 3),
            "forearm_beam_plus_two_adapters_mass_g": round(forearm_link_mass_g, 3),
            "allocated_shoulder_gravity_nm": round(shoulder_nm, 3),
            "allocated_elbow_gravity_nm": round(elbow_nm, 3),
            "screening_multiplier": 2.25,
            "shoulder_screen_nm": round(shoulder_nm * 2.25, 3),
            "elbow_screen_nm": round(elbow_nm * 2.25, 3),
            "status": "screen only; received masses, COM, inertia, continuous torque and thermal proof required",
        },
        "open_release_items": [
            "controlled exact 20-2040 cross-section and end-tap coordinates",
            "adapter material, thickness, tolerances and manufacturing process",
            "all M2.5 and M5 fastener order codes, grades, lengths, engagement, torque and retention",
            "tool access, cable routing, connector sweep and strain relief",
            "full continuous joint-space collision analysis including base, guard, stops and gripper",
            "stress, joint-slip, thread, fatigue, impact and proof analyses",
            "received-part fit, first-article inspection and qualified mechanical approval",
        ],
    }
    (OUT / "architecture-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8", newline="\n")

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1500" height="920" viewBox="0 0 1500 920">
<style>text{{font-family:Arial,sans-serif;fill:#082b4c;font-size:18px}}.title{{font-size:34px;font-weight:700}}.sub{{font-size:23px;font-weight:700}}.warn{{font-size:20px;font-weight:700;fill:#8a3b00}}.axis{{stroke:#0b4f8a;stroke-width:4}}.part{{fill:#66c7f4;stroke:#0b4f8a;stroke-width:3}}.frame{{fill:#f3b61f;stroke:#8a5a00;stroke-width:3}}.note{{fill:#fff4cd;stroke:#f3b61f;stroke-width:3}}</style>
<rect width="1500" height="920" fill="#f7fbff"/>
<text x="40" y="55" class="title">HR-V0 exact-coordinate arm architecture candidate</text>
<text x="40" y="92" class="warn">{REVISION} - {WARNING}</text>
<text x="40" y="145" class="sub">Straight reference pose, side elevation (Y horizontal, Z vertical)</text>
<line x1="150" y1="370" x2="1330" y2="370" stroke="#b7cad9" stroke-width="2"/>
<circle cx="190" cy="370" r="18" fill="#0b4f8a"/><text x="155" y="420">J1 Y=0</text>
<rect x="220" y="330" width="54" height="80" class="frame"/>
<rect x="274" y="350" width="400" height="40" class="part"/><text x="365" y="340">100 mm 20-2040 envelope + two 4 mm adapters</text>
<circle cx="714" cy="370" r="18" fill="#0b4f8a"/><text x="655" y="420">J2 Y=191.5</text>
<rect x="744" y="330" width="54" height="80" class="frame"/>
<rect x="798" y="350" width="250" height="40" class="part"/><text x="840" y="340">50 mm forearm member</text>
<rect x="1048" y="330" width="54" height="80" class="frame"/><text x="1000" y="440">G1 Y=309.5</text>
<line x1="190" y1="480" x2="714" y2="480" class="axis"/><text x="350" y="512">J1-J2 = 191.5 mm candidate</text>
<line x1="714" y1="550" x2="1102" y2="550" class="axis"/><text x="800" y="582">J2-G1 = 118.0 mm candidate</text>
<rect x="70" y="640" width="1360" height="210" rx="14" class="note"/>
<text x="100" y="690" class="sub">What this fixes</text>
<text x="100" y="730">The J2 body and S102 are deliberately rolled +90 deg; the output reference is offset -90 deg.</text>
<text x="100" y="766">This preserves parallel +X J1/J2 axes and places opposing broad faces at Y=32 and Y=140 mm.</text>
<text x="100" y="802">G1 leaves 50.5 mm to the 360 mm object-center ceiling. The beams are conservative envelopes, not invented profile CAD.</text>
<text x="100" y="838" class="warn">Fasteners, tolerances, cables, complete sweep, proof and qualified review remain open. Do not fabricate.</text>
</svg>'''
    (OUT / "HR-V0_arm_architecture_candidate.svg").write_text(svg, encoding="utf-8", newline="\n")

    print(f"Generated {REVISION}: J1-J2 {J2_Y:.1f} mm; J2-G1 {G1_Y-J2_Y:.1f} mm; collision max {worst:.6f} mm3")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
