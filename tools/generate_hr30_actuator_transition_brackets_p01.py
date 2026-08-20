#!/usr/bin/env python3
"""Generate the 25-axis HR-30 fixed-transition bracket candidate package.

The geometry is a project-owned service-cassette candidate around the selected
CF130 -> Micro-Fit -> Alpha 3051 electrical transition.  The connector window
is deliberately a clearance proxy, not a released Molex panel cutout.
"""

from __future__ import annotations

import csv
import hashlib
import html
import json
import math
import shutil
from pathlib import Path

import cadquery as cq


ROOT = Path(__file__).resolve().parents[1]
WB = ROOT / "hr30" / "whole-body-p0.1"
PHYSICAL = WB / "harness" / "physical-p0.1"
OUT = WB / "harness" / "actuator-transition-brackets-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / "harness" / OUT.name
IDENTIFIER = "HR30-ACTUATOR-TRANSITION-BRACKETS-P0.1"
DATE = "2026-08-18"
WARNING = "PRELIMINARY - DIMENSIONED TRANSITION-BRACKET CANDIDATE - CONNECTOR FIT AND MANUFACTURING CUTOUT NOT RELEASED - NOT APPROVED FOR PROCUREMENT, FABRICATION, CONNECTION, POWERED TESTING, MOTION OR ENERGIZATION"
AUTHORITY = "NO PROCUREMENT, FABRICATION, CONNECTION, POWERED-TEST, MOTION OR ENERGIZATION AUTHORITY"

# Project-owned P0.1 envelope.  These values do not claim to reproduce the
# manufacturer housing or its production panel opening.
PLATE_W = 34.0
PLATE_H = 28.0
PLATE_T = 3.0
PROXY_W = 14.0
PROXY_H = 9.5
MOUNT_PITCH = 26.0
MOUNT_D = 3.2
SHELF_W = 18.0
SHELF_L = 13.0
SHELF_T = 4.0
CAP_W = 18.0
CAP_L = 10.0
CAP_H = 6.0
CAP_HOLE_PITCH = 12.0
CAP_HOLE_D = 2.7
CABLE_PROXY_D = 4.8
ENVELOPE = (34.0, 31.0, 28.0)
COUPON_W = 96.0
COUPON_H = 78.0
COUPON_T = 3.0
COUPON_X_PITCH = 28.0
COUPON_Z_PITCH = 22.0
COUPON_WIDTHS = (13.5, 14.0, 14.5)
COUPON_HEIGHTS = (9.0, 9.5, 10.0)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise RuntimeError(f"refusing empty controlled register: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalize_step(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    path.write_text("\n".join(line.rstrip() for line in text.splitlines()) + "\n", encoding="utf-8", newline="\n")


def box(width: float, depth: float, height: float, x: float, y: float, z: float) -> cq.Shape:
    return cq.Workplane("XY").box(width, depth, height).translate((x, y, z)).val()


def y_hole(x: float, z: float, diameter: float, y0: float = -4.0, length: float = 8.0) -> cq.Shape:
    return cq.Solid.makeCylinder(diameter / 2, length, cq.Vector(x, y0, z), cq.Vector(0, 1, 0))


def standard_parts() -> tuple[cq.Shape, cq.Shape]:
    plate = box(PLATE_W, PLATE_T, PLATE_H, 0, 0, 0)
    plate = plate.cut(box(PROXY_W, 8.0, PROXY_H, 0, 0, 1.0))
    for x in (-MOUNT_PITCH / 2, MOUNT_PITCH / 2):
        plate = plate.cut(y_hole(x, 0, MOUNT_D))

    # One integral shelf on each side of the panel.  A cap bolts to each shelf
    # and restrains cable jacket; the connector contacts carry no joint load.
    for y in (-(PLATE_T + SHELF_L) / 2, (PLATE_T + SHELF_L) / 2):
        shelf = box(SHELF_W, SHELF_L, SHELF_T, 0, y, -PLATE_H / 2 + SHELF_T / 2)
        for x in (-CAP_HOLE_PITCH / 2, CAP_HOLE_PITCH / 2):
            shelf = shelf.cut(y_hole(x, -PLATE_H / 2 + SHELF_T / 2, CAP_HOLE_D, y - SHELF_L / 2 - 1, SHELF_L + 2))
        plate = plate.fuse(shelf)

    cap = box(CAP_W, CAP_L, CAP_H, 0, 0, 0)
    cable = cq.Solid.makeCylinder(CABLE_PROXY_D / 2, CAP_L + 2, cq.Vector(0, -CAP_L / 2 - 1, -CAP_H / 2), cq.Vector(0, 1, 0))
    cap = cap.cut(cable)
    for x in (-CAP_HOLE_PITCH / 2, CAP_HOLE_PITCH / 2):
        cap = cap.cut(y_hole(x, 0, CAP_HOLE_D, -CAP_L / 2 - 1, CAP_L + 2))
    return plate, cap


def fit_coupon() -> cq.Shape:
    """Nine-window diagnostic coupon around the project proxy.

    This deliberately does not encode or claim a Molex production cutout.
    It measures received-housing clearance against a controlled matrix while
    the revision-controlled manufacturer cutout remains unresolved.
    """
    coupon = box(COUPON_W, COUPON_T, COUPON_H, 0, 0, 0)
    for col, width in enumerate(COUPON_WIDTHS):
        x = (col - 1) * COUPON_X_PITCH
        for row, height in enumerate(COUPON_HEIGHTS):
            z = (1 - row) * COUPON_Z_PITCH
            coupon = coupon.cut(box(width, COUPON_T + 4.0, height, x, 0, z))
    return coupon


def coupon_matrix_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for col, width in enumerate(COUPON_WIDTHS):
        x = (col - 1) * COUPON_X_PITCH
        for row, height in enumerate(COUPON_HEIGHTS):
            z = (1 - row) * COUPON_Z_PITCH
            rows.append({
                "coupon_opening_id": f"ATB-COUPON-W{width:.1f}-H{height:.1f}",
                "column": col + 1, "row": row + 1,
                "center_x_mm": f"{x:.3f}", "center_z_mm": f"{z:.3f}",
                "nominal_width_mm": f"{width:.3f}", "nominal_height_mm": f"{height:.3f}",
                "plate_thickness_mm": f"{COUPON_T:.3f}",
                "purpose": "RECEIVED-HOUSING GROSS-CLEARANCE DIAGNOSTIC ONLY",
                "production_cutout_authority": "NONE - OFFICIAL DRAWING RECONCILIATION STILL REQUIRED",
                "warning": WARNING,
            })
    return rows


def coupon_process_rows() -> list[dict[str, object]]:
    steps = [
        ("ATB-CP01", "material receipt", "Prusament PETG V0 Natural 1 kg candidate; record spool ID, lot/NFC data and dry history", "Material substitution requires a new coupon record"),
        ("ATB-CP02", "drying", "If storage history is not dry, dry 6 h at 55 C per current Prusa guidance", "Record actual time and temperature"),
        ("ATB-CP03", "slicing", "Flat on textured or satin sheet; 0.4 mm nozzle; 0.20 mm layers; 4 perimeters; 5 top/bottom layers; 30% rectilinear infill; 100% scale; no supports", "Project diagnostic settings; store slicer/project file and profile version"),
        ("ATB-CP04", "printing", "Prusament PETG V0 profile; manufacturer range 230 +/- 10 C nozzle and 80 +/- 10 C bed", "Record printer, firmware, nozzle, profile and actual temperatures"),
        ("ATB-CP05", "conditioning", "Cool on the sheet; remove without heat-forming; condition 24 h at room ambient", "Record ambient temperature/humidity and elapsed time"),
        ("ATB-CP06", "dimensional inspection", "Measure coupon thickness and all nine openings at two width and two height locations", "Caliper/resolution ID and raw readings required; do not average away taper"),
        ("ATB-CP07", "received-part fit", "Inspect received Molex 430200200 lot; try each opening from intended side without force, trimming or heating", "Record housing/lot, first go, latch/ear access, retention and damage"),
        ("ATB-CP08", "disposition", "Compare measured coupon and received housing to revision-controlled Molex drawing before changing production CAD", "Coupon alone cannot release a production cutout"),
    ]
    return [{"step_id": i, "operation": op, "controlled_instruction": instruction, "record_required": record, "execution_state": "NOT EXECUTED", "authority": AUTHORITY, "warning": WARNING} for i, op, instruction, record in steps]


def coupon_inspection_rows(matrix: list[dict[str, object]]) -> list[dict[str, object]]:
    return [{
        "coupon_opening_id": row["coupon_opening_id"],
        "nominal_width_mm": row["nominal_width_mm"], "nominal_height_mm": row["nominal_height_mm"],
        "measured_width_top_mm": "NOT EXECUTED", "measured_width_bottom_mm": "NOT EXECUTED",
        "measured_height_left_mm": "NOT EXECUTED", "measured_height_right_mm": "NOT EXECUTED",
        "received_connector_lot": "NOT RECEIVED", "gross_clearance_result": "NOT EXECUTED",
        "latch_and_ear_access_result": "NOT EXECUTED", "retention_result": "NOT EXECUTED",
        "damage_or_witness_mark": "NOT EXECUTED", "disposition": "OPEN - NO FIT CLAIM",
        "authority": AUTHORITY, "warning": WARNING,
    } for row in matrix]


def module_for(axis: str) -> tuple[str, float]:
    if axis.startswith("HEAD_"):
        return "HEAD/NECK", -56.0
    if axis == "WAIST_YAW":
        return "PELVIS/WAIST", -50.0
    if "GRIPPER" in axis or "WRIST" in axis:
        return ("LEFT HAND/FOREARM" if axis.startswith("L_") else "RIGHT HAND/FOREARM"), -35.0
    if any(key in axis for key in ("SHOULDER", "ELBOW")):
        return ("LEFT ARM" if axis.startswith("L_") else "RIGHT ARM"), -35.0
    if "ANKLE" in axis:
        return ("LEFT LOWER LEG/FOOT" if axis.startswith("L_") else "RIGHT LOWER LEG/FOOT"), -36.0
    return ("LEFT LEG" if axis.startswith("L_") else "RIGHT LEG"), -36.0


def placement_xyz(axis: str, source: tuple[float, float, float]) -> tuple[float, float, float]:
    x, _y, z = source
    _module, rear_y = module_for(axis)
    overrides = {
        "L_HIP_YAW": (62.5, rear_y, 416.0), "L_HIP_ROLL": (62.5, rear_y, 385.0), "L_HIP_PITCH": (62.5, rear_y, 354.0),
        "R_HIP_YAW": (-62.5, rear_y, 416.0), "R_HIP_ROLL": (-62.5, rear_y, 385.0), "R_HIP_PITCH": (-62.5, rear_y, 354.0),
        "L_ANKLE_PITCH": (62.5, rear_y, 61.0), "L_ANKLE_ROLL": (62.5, rear_y, 28.0),
        "R_ANKLE_PITCH": (-62.5, rear_y, 61.0), "R_ANKLE_ROLL": (-62.5, rear_y, 28.0),
        "L_SHOULDER_PITCH": (110.0, rear_y, 610.0), "L_SHOULDER_ROLL": (110.0, rear_y, 577.0),
        "R_SHOULDER_PITCH": (-110.0, rear_y, 610.0), "R_SHOULDER_ROLL": (-110.0, rear_y, 577.0),
        "HEAD_PAN": (0.0, rear_y, 650.0), "HEAD_TILT": (0.0, rear_y, 690.0),
        "WAIST_YAW": (0.0, rear_y, 425.0),
    }
    return overrides.get(axis, (x - 5.0 if axis.startswith("L_") else x - 5.0, rear_y, z))


def placement_rows(transitions: list[dict[str, str]], points: list[dict[str, str]]) -> list[dict[str, object]]:
    point_map = {r["point_id"]: (float(r["x_mm"]), float(r["y_mm"]), float(r["z_mm"])) for r in points}
    rows: list[dict[str, object]] = []
    for transition in transitions:
        axis = transition["axis_id"]
        point_id = transition["power_loop"] + "-P01"
        source = point_map[point_id]
        candidate = placement_xyz(axis, source)
        module, rear_y = module_for(axis)
        rows.append({
            "placement_id": "ATB-" + axis,
            "axis_id": axis,
            "transition_id": transition["transition_id"],
            "module_region": module,
            "source_fixed_route_point": point_id,
            "source_x_mm": f"{source[0]:.3f}", "source_y_mm": f"{source[1]:.3f}", "source_z_mm": f"{source[2]:.3f}",
            "candidate_x_mm": f"{candidate[0]:.3f}", "candidate_y_mm": f"{candidate[1]:.3f}", "candidate_z_mm": f"{candidate[2]:.3f}",
            "offset_from_source_mm": f"{math.dist(source, candidate):.3f}",
            "panel_normal": "+Y/-Y; CONNECTOR AXIS ALONG Y",
            "nominal_rear_mount_plane_y_mm": f"{rear_y:.3f}",
            "candidate_envelope_xyz_mm": "34.0 x 31.0 x 28.0",
            "duplicate_resolution": "VERTICAL SERVICE-CASSETTE STAGGER" if "SHOULDER" in axis else "N/A",
            "placement_state": "DIMENSIONED NOMINAL CANDIDATE - TOLERANCE/SWEEP/RECEIVED FIT OPEN",
            "authority": AUTHORITY, "warning": WARNING,
        })
    return rows


def aabb_gap(a: dict[str, object], b: dict[str, object]) -> float:
    centers_a = [float(a[f"candidate_{k}_mm"]) for k in ("x", "y", "z")]
    centers_b = [float(b[f"candidate_{k}_mm"]) for k in ("x", "y", "z")]
    return math.sqrt(sum(max(0.0, abs(centers_a[i] - centers_b[i]) - ENVELOPE[i]) ** 2 for i in range(3)))


def spacing_rows(placements: list[dict[str, object]]) -> list[dict[str, object]]:
    rows = []
    for a in placements:
        candidates = [(aabb_gap(a, b), b) for b in placements if b is not a]
        gap, b = min(candidates, key=lambda item: item[0])
        rows.append({
            "placement_id": a["placement_id"], "nearest_placement_id": b["placement_id"],
            "nominal_aabb_clearance_mm": f"{gap:.3f}",
            "nominal_envelope_overlap": "NO" if gap > 0 else "YES",
            "screen_scope": "STANDARD 34 x 31 x 28 mm CASSETTE ENVELOPES IN NEUTRAL NOMINAL PLACEMENT ONLY",
            "unresolved": "BODY/COVER/CABLE/JOINED-HARDWARE TOLERANCE AND MOVING-SWEEP COLLISION NOT EVALUATED",
            "authority": AUTHORITY, "warning": WARNING,
        })
    return rows


def export_cad(placements: list[dict[str, object]]) -> None:
    base, cap = standard_parts()
    coupon = fit_coupon()
    cq.exporters.export(base, str(OUT / "ATB-BASE-P0.1.step"))
    cq.exporters.export(cap, str(OUT / "ATB-CLAMP-CAP-P0.1.step"))
    normalize_step(OUT / "ATB-BASE-P0.1.step")
    normalize_step(OUT / "ATB-CLAMP-CAP-P0.1.step")
    cq.exporters.export(coupon, str(OUT / "ATB-CONNECTOR-FIT-COUPON-P0.1.step"))
    normalize_step(OUT / "ATB-CONNECTOR-FIT-COUPON-P0.1.step")
    coupon_assembly = cq.Assembly(name="ATB_CONNECTOR_FIT_COUPON_P0_1")
    coupon_assembly.add(coupon, name="NINE-WINDOW-DIAGNOSTIC-COUPON", color=cq.Color(0.95, 0.68, 0.06))
    coupon_assembly.save(str(OUT / "ATB-CONNECTOR-FIT-COUPON-P0.1.glb"))

    unit = cq.Assembly(name="ATB_STANDARD_ASSEMBLY_P0_1")
    unit.add(base, name="ATB-BASE", color=cq.Color(0.95, 0.68, 0.06))
    cap_z = -PLATE_H / 2 + SHELF_T + CAP_H / 2
    unit.add(cap.translate((0, -9.5, cap_z)), name="ATB-CAP-DYNAMIC", color=cq.Color(0.08, 0.28, 0.52))
    unit.add(cap.translate((0, 9.5, cap_z)), name="ATB-CAP-PIGTAIL", color=cq.Color(0.08, 0.28, 0.52))
    unit.save(str(OUT / "ATB-STANDARD-ASSEMBLY-P0.1.step"))
    normalize_step(OUT / "ATB-STANDARD-ASSEMBLY-P0.1.step")
    unit.save(str(OUT / "ATB-STANDARD-ASSEMBLY-P0.1.glb"))

    whole = cq.Assembly(name="HR30_WHOLE_BODY_25_TRANSITION_BRACKETS_P0_1")
    sky, dark, gold, navy = cq.Color(0.33, 0.68, 0.88, 0.22), cq.Color(0.04, 0.19, 0.36, 0.28), cq.Color(0.95, 0.68, 0.06), cq.Color(0.06, 0.22, 0.42)
    context = [
        ("LEFT-FOOT", box(105,170,35,62.5,18,17.5), sky), ("RIGHT-FOOT", box(105,170,35,-62.5,18,17.5), sky),
        ("LEFT-LEG", box(55,72,375,62.5,0,222.5), sky), ("RIGHT-LEG", box(55,72,375,-62.5,0,222.5), sky),
        ("PELVIS", box(180,100,80,0,0,450), dark), ("TORSO", box(210,108,170,0,0,575), dark),
        ("HEAD", box(142,112,102,0,0,711), sky),
        ("LEFT-ARM", box(62,70,295,135,0,442.5), sky), ("RIGHT-ARM", box(62,70,295,-135,0,442.5), sky),
        ("LEFT-HAND", box(54,58,70,140,0,260), sky), ("RIGHT-HAND", box(54,58,70,-140,0,260), sky),
    ]
    for name, shape, color in context:
        whole.add(shape, name="BODY-" + name, color=color)
    for row in placements:
        p = (float(row["candidate_x_mm"]), float(row["candidate_y_mm"]), float(row["candidate_z_mm"]))
        whole.add(base.translate(p), name=str(row["placement_id"]) + "-BASE", color=gold)
        whole.add(cap.translate((p[0], p[1] - 9.5, p[2] + cap_z)), name=str(row["placement_id"]) + "-DYN-CAP", color=navy)
        whole.add(cap.translate((p[0], p[1] + 9.5, p[2] + cap_z)), name=str(row["placement_id"]) + "-PIG-CAP", color=navy)
    whole.save(str(OUT / "HR30_25_axis_transition_brackets_candidate.step"))
    normalize_step(OUT / "HR30_25_axis_transition_brackets_candidate.step")
    whole.save(str(OUT / "HR30_25_axis_transition_brackets_candidate.glb"))


def write_drawings() -> None:
    base_svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 820 540" role="img"><style>text{{font:16px Arial,sans-serif;fill:#0b315c}}.title{{font-size:28px;font-weight:700}}.part{{fill:#d9f2ff;stroke:#0b315c;stroke-width:4}}.proxy{{fill:#fff3c4;stroke:#9b6800;stroke-width:3;stroke-dasharray:10 7}}.dim{{stroke:#0b4f91;stroke-width:2;fill:none}}.note{{font-size:14px}}</style><rect width="820" height="540" fill="#f8fcff"/><text x="34" y="48" class="title">ATB-BASE-P0.1 front reference</text><rect x="220" y="90" width="340" height="280" rx="14" class="part"/><rect x="330" y="187" width="140" height="95" rx="8" class="proxy"/><circle cx="255" cy="230" r="16" fill="white" stroke="#0b315c" stroke-width="4"/><circle cx="525" cy="230" r="16" fill="white" stroke="#0b315c" stroke-width="4"/><path d="M220 410h340M220 397v26M560 397v26" class="dim"/><text x="350" y="438">34.0 mm</text><path d="M180 90v280M167 90h26M167 370h26" class="dim"/><text x="95" y="235">28.0 mm</text><text x="331" y="178">14.0 x 9.5 mm clearance proxy</text><text x="228" y="465">M3 candidate module holes: 26.0 mm pitch; 3.2 mm clearance</text><text x="34" y="500" class="note">PROJECT-OWNED GEOMETRY. NOT A MOLEX PANEL-CUTOUT OR CONNECTOR-FIT RELEASE.</text><text x="34" y="526" class="note">{html.escape(WARNING)}</text></svg>'''
    cap_svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 820 420" role="img"><style>text{{font:16px Arial,sans-serif;fill:#0b315c}}.title{{font-size:28px;font-weight:700}}.part{{fill:#f2b91d;stroke:#0b315c;stroke-width:4}}.dim{{stroke:#0b4f91;stroke-width:2}}</style><rect width="820" height="420" fill="#f8fcff"/><text x="34" y="48" class="title">ATB-CLAMP-CAP-P0.1 reference</text><rect x="230" y="105" width="360" height="120" rx="18" class="part"/><path d="M350 225a60 60 0 0 1 120 0" fill="#f8fcff" stroke="#0b315c" stroke-width="4"/><circle cx="290" cy="165" r="14" fill="white" stroke="#0b315c" stroke-width="4"/><circle cx="530" cy="165" r="14" fill="white" stroke="#0b315c" stroke-width="4"/><text x="245" y="270">18 x 10 x 6 mm; 2 x 2.7 mm holes at 12 mm pitch</text><text x="245" y="302">4.8 mm cable-jacket proxy; clamp force and insert selection open</text><text x="34" y="368">{html.escape(WARNING)}</text></svg>'''
    (OUT / "ATB-BASE-P0.1.svg").write_text(base_svg, encoding="utf-8", newline="\n")
    (OUT / "ATB-CLAMP-CAP-P0.1.svg").write_text(cap_svg, encoding="utf-8", newline="\n")
    cells = []
    for col, width in enumerate(COUPON_WIDTHS):
        x = 220 + col * 190
        for row, height in enumerate(COUPON_HEIGHTS):
            y = 120 + row * 125
            cells.append(f'<rect x="{x - width * 4:.1f}" y="{y - height * 4:.1f}" width="{width * 8:.1f}" height="{height * 8:.1f}" class="opening"/><text x="{x - 58}" y="{y + 63}" class="label">{width:.1f} x {height:.1f} mm</text>')
    coupon_svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 820 580" role="img"><style>text{{font:18px Arial,sans-serif;fill:#0b315c}}.title{{font-size:28px;font-weight:700}}.plate{{fill:#d9f2ff;stroke:#0b315c;stroke-width:4}}.opening{{fill:white;stroke:#9b6800;stroke-width:3}}.label{{font-size:18px;font-weight:700}}.note{{font-size:18px}}</style><rect width="820" height="580" fill="#f8fcff"/><text x="34" y="46" class="title">ATB connector-fit diagnostic coupon P0.1</text><rect x="100" y="68" width="620" height="420" rx="14" class="plate"/>{''.join(cells)}<text x="34" y="522" class="note">Nine rectangular gross-clearance tests only.</text><text x="34" y="548" class="note">PRELIMINARY DIAGNOSTIC COUPON — NOT A PRODUCTION CUTOUT</text><text x="34" y="574" class="note">OR A FABRICATION / CONNECTOR-FIT RELEASE.</text></svg>'''
    (OUT / "ATB-CONNECTOR-FIT-COUPON-P0.1.svg").write_text(coupon_svg, encoding="utf-8", newline="\n")


def source_rows() -> list[dict[str, object]]:
    local = [
        ("ATB-S01", PHYSICAL / "actuator-power-transition-register.csv", "25-axis electrical transition architecture"),
        ("ATB-S02", PHYSICAL / "route-point-register.csv", "fixed-side route-point coordinates"),
        ("ATB-S03", WB / "joint-axis-schedule.csv", "25-axis whole-body identity and datum schedule"),
    ]
    rows = [{"source_id": i, "publisher": "Project Button", "document": role, "revision_or_date": "current P0.1 generated input", "official_url_or_path": p.relative_to(ROOT).as_posix(), "sha256": sha(p), "verified_scope": role, "warning": WARNING} for i, p, role in local]
    official = [
        ("ATB-S04", "Molex", "Micro-Fit 3.0 43020 series chart", "live official page; accessed 2026-08-18", "https://www.molex.com/en-us/products/series-chart/43020", "430200200 is a 2-circuit dual-row plug housing with panel-mount ears; exact fit/cutout not transcribed"),
        ("ATB-S05", "Molex", "430200200 official sales drawing", "current official PDF link; accessed 2026-08-18; revision/date not extracted", "https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/salesdrawingpdf/430/43020/430200200_sd.pdf", "authoritative fit evidence required before bracket cutout release"),
        ("ATB-S06", "Molex", "Micro-Fit product specification PS-43045", "revision R; 2025-11-14", "https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/productspecificationpdf/430/43045/PS-43045-001.pdf", "connector-system family and application limits; bracket retention not released"),
        ("ATB-S07", "Molex", "Micro-Fit application specification 430450001-AS", "revision A1; approved 2025-11-21", "https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/applicationspecificationspdf/430/43045/430450001-AS-000.pdf", "crimp/application guidance; received-part fit and strain relief remain open"),
        ("ATB-S08", "Prusa Polymers", "Prusament PETG V0 material page", "live official page; accessed 2026-08-18", "https://prusament.com/materials/prusament-petg-v0/", "diagnostic coupon material candidate; 230 +/- 10 C nozzle, 80 +/- 10 C bed, drying guidance; no production-bracket or fire-safety credit"),
        ("ATB-S09", "Prusa Research", "Prusament PETG V0 Natural 1 kg (NFC)", "live official product page; accessed 2026-08-18; IDF 17666 / IDS 3514", "https://www.prusa3d.com/product/prusament-petg-v0-natural-1kg/", "purchasable diagnostic-coupon material candidate; UL claim applies only under the manufacturer's stated printer/profile conditions and is not credited here"),
    ]
    rows.extend({"source_id": i, "publisher": p, "document": d, "revision_or_date": rev, "official_url_or_path": url, "sha256": "N/A - LIVE PRIMARY SOURCE", "verified_scope": scope, "warning": WARNING} for i, p, d, rev, url, scope in official)
    return rows


def render(placements: list[dict[str, object]], spacing: list[dict[str, object]]) -> str:
    options = "".join(f'<option value="{html.escape(str(r["axis_id"]))}">{html.escape(str(r["axis_id"]))}</option>' for r in placements)
    rows = "".join(f'<tr data-axis="{html.escape(str(r["axis_id"]))}"><td>{html.escape(str(r["axis_id"]))}</td><td>{html.escape(str(r["module_region"]))}</td><td>{r["candidate_x_mm"]}, {r["candidate_y_mm"]}, {r["candidate_z_mm"]}</td><td>{html.escape(str(r["source_fixed_route_point"]))}</td></tr>' for r in placements)
    min_gap = min(float(r["nominal_aabb_clearance_mm"]) for r in spacing)
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 transition brackets P0.1</title><script type="module" src="../../vendor/model-viewer.min.js"></script><style>:root{{--deep:#071d36;--blue:#0b4f91;--sky:#d9f2ff;--gold:#f2b91d;--paper:#f7fbff;--ink:#142a40;--line:#82c4e6;--red:#982520}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.55 system-ui,Segoe UI,sans-serif}}header,main,footer{{padding:clamp(24px,5vw,64px) max(18px,calc((100vw - 1200px)/2))}}header,footer{{background:linear-gradient(135deg,var(--deep),var(--blue));color:white}}h1{{font-size:clamp(38px,6vw,68px);line-height:1.05;max-width:18ch}}h2{{font-size:clamp(27px,4vw,42px)}}.warning{{background:var(--gold);color:#17243a;border:3px solid #805600;padding:16px;font-weight:900}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(235px,1fr));gap:18px}}article,.panel{{background:white;border:2px solid var(--line);border-radius:16px;padding:19px}}.metric{{font-size:clamp(34px,5vw,54px);font-weight:900;color:var(--blue)}}model-viewer{{display:block;width:100%;height:clamp(520px,72vh,780px);background:radial-gradient(circle,#fff,var(--sky))}}select{{font:inherit;min-height:46px;padding:9px 12px;border:2px solid var(--blue);border-radius:9px}}.tablewrap{{overflow:auto;border:2px solid var(--line);border-radius:14px}}table{{border-collapse:collapse;width:100%;min-width:780px;background:white}}th,td{{padding:13px 14px;border-bottom:1px solid #cfeafa;text-align:left}}th{{background:var(--deep);color:white;font-size:14px}}td{{font-size:14px}}a{{color:#075b9b;font-weight:800}}.open{{border-left:8px solid var(--gold)}}small{{font-size:14px}}img{{max-width:100%;height:auto}}@media(max-width:560px){{body{{font-size:16px}}header,main,footer{{padding-left:16px;padding-right:16px}}}}</style></head><body><header><div class="warning">{html.escape(WARNING)}</div><p>HR-30 whole-body P0.1</p><h1>One fixed transition for every moving actuator feed.</h1><p>The robot now has a dimensioned service-cassette candidate at all 25 axes and a printable nine-window connector-fit coupon. The connector cutout remains unresolved until primary drawing reconciliation and received-part testing are complete.</p></header><main><section class="grid"><article><div class="metric">25</div><p>named whole-body placements</p></article><article><div class="metric">9</div><p>diagnostic coupon openings</p></article><article><div class="metric">{min_gap:.1f}</div><p>mm minimum nominal cassette-envelope clearance</p></article><article><div class="metric">0</div><p>received-part fit checks</p></article></section><h2>Orbit the complete robot</h2><div class="panel"><model-viewer src="HR30_25_axis_transition_brackets_candidate.glb" camera-controls camera-orbit="32deg 76deg 105%" field-of-view="27deg" shadow-intensity="0.8" exposure="1.05" alt="Interactive 762 millimetre humanoid with 25 gold and dark-blue fixed transition bracket cassettes"></model-viewer><p>Gold plates and blue clamp caps are the 25 transition candidates. Translucent body solids are positional context, not replacement production body CAD.</p><p><a href="HR30_25_axis_transition_brackets_candidate.step">Download whole-body placement STEP</a> · <a href="ATB-STANDARD-ASSEMBLY-P0.1.step">Download editable standard cassette STEP</a></p></div><h2>What is dimensioned</h2><div class="grid"><article><img src="ATB-BASE-P0.1.svg" alt="Dimensioned front reference for the transition bracket base"><p>34 × 28 × 3 mm panel plate, 26 mm M3 candidate module-hole pitch, integral two-sided clamp shelves.</p></article><article><img src="ATB-CLAMP-CAP-P0.1.svg" alt="Dimensioned reference for the removable clamp cap"><p>Two removable caps prevent cable jacket load from reaching Micro-Fit or JST contacts.</p></article></div><h2>Print the connector-fit coupon first</h2><div class="grid"><article><img src="ATB-CONNECTOR-FIT-COUPON-P0.1.svg" alt="Nine-window diagnostic connector fit coupon"><p>The 96 × 78 × 3 mm coupon spans 13.5–14.5 mm widths and 9.0–10.0 mm heights. It is designed to cheaply measure gross clearance against a received housing before changing 25 brackets.</p></article><article class="open"><p><strong>Diagnostic only.</strong> The rectangular matrix does not reproduce panel ears, latch access or retention geometry. A coupon result cannot release the production cutout.</p><p><a href="ATB-CONNECTOR-FIT-COUPON-P0.1.step">Download coupon STEP</a> · <a href="coupon-process-traveler.csv">Open the print/test traveler</a> · <a href="coupon-inspection-register.csv">Open the blank inspection record</a></p><p>Fit-check material candidate: Prusament PETG V0 Natural, IDF 17666 / IDS 3514. This package takes no UL or production-material credit.</p></article></div><h2>Connector-fit boundary</h2><div class="panel open"><p><strong>The 14 × 9.5 mm opening is a project-owned clearance proxy, not a Molex production cutout.</strong> The current official part identity is source-bound, but the manufacturing cutout has not been reliably extracted. Before fabrication release, reconcile the revision-controlled drawing and independently check its dimensions, then test a received connector. Production material, inserts, fasteners, clamp force, cable OD, tolerance, guard clearance and joint sweeps also remain open.</p></div><h2>All 25 placements</h2><label for="axis">Filter by axis</label> <select id="axis"><option value="">Show every axis</option>{options}</select><div class="tablewrap"><table><thead><tr><th>Axis</th><th>Module region</th><th>Candidate XYZ (mm)</th><th>Source route point</th></tr></thead><tbody>{rows}</tbody></table></div><h2>Controlled files</h2><div class="panel"><p><a href="placement-register.csv">25 placements</a> · <a href="coupon-opening-matrix.csv">coupon matrix</a> · <a href="part-register.csv">parts</a> · <a href="interface-register.csv">interfaces</a> · <a href="spacing-screen.csv">nominal spacing</a> · <a href="open-holds.csv">open holds</a> · <a href="source-register.csv">sources</a></p><p><small>{html.escape(AUTHORITY)}</small></p></div></main><footer>{html.escape(WARNING)}</footer><script>const s=document.querySelector('#axis'),trs=[...document.querySelectorAll('tbody tr')];s.addEventListener('change',()=>trs.forEach(r=>r.hidden=!!s.value&&r.dataset.axis!==s.value));</script></body></html>'''


def integrate_root() -> None:
    status_path = WB / "package-status.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    status.update({
        "actuator_transition_bracket_package_present": True,
        "actuator_transition_bracket_placement_count": 25,
        "actuator_transition_bracket_cad_present": True,
        "actuator_transition_bracket_diagnostic_fit_coupon_present": True,
        "actuator_transition_bracket_coupon_opening_count": 9,
        "actuator_transition_bracket_coupon_physical_test_executed": False,
        "actuator_transition_bracket_received_fit_verified": False,
        "actuator_transition_bracket_manufacturing_cutout_released": False,
        "actuator_transition_bracket_fabrication_released": False,
        "connection_authority": False, "powered_test_authority": False,
        "motion_authority": False, "energization_authority": False,
    })
    status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n")

    readme_path = WB / "README.md"
    text = readme_path.read_text(encoding="utf-8")
    start, end = "<!-- HR30-TRANSITION-BRACKETS-P01-README-START -->", "<!-- HR30-TRANSITION-BRACKETS-P01-README-END -->"
    if start in text and end in text:
        text = text.split(start, 1)[0] + text.split(end, 1)[1]
    block = f'''{start}\n## Actuator fixed-transition bracket CAD\n\nThe [interactive transition-bracket guide](harness/actuator-transition-brackets-p0.1/index.html) places one dimensioned three-solid service cassette at every one of the 25 actuator feeds. Editable part STEP, the standard assembly STEP/GLB, the recognizable whole-body placement STEP/GLB and all coordinates are included.\n\nThe central connector opening is a **project-owned clearance proxy**, not a released Molex cutout. A printable nine-window diagnostic coupon, print traveler and blank inspection record are included so a received connector can be checked before all 25 brackets are revised. Official-drawing reconciliation, received-part fit, production material/process selection, cable clamp qualification, body attachment, tolerance-aware collision and physical testing remain open.\n{end}\n'''
    anchor = "<!-- HR30-FIRST-ENERGIZATION-P01-README-START -->"
    if anchor in text:
        text = text.replace(anchor, block + anchor, 1)
    else:
        # A clean release generates the bracket package before the readiness
        # package.  Append now; readiness will add its own controlled block
        # later without becoming a prerequisite for physical CAD.
        text = text.rstrip() + "\n\n" + block
    readme_path.write_text(text, encoding="utf-8", newline="\n")

    page_path = WB / "index.html"
    text = page_path.read_text(encoding="utf-8")
    start, end = "<!-- HR30-TRANSITION-BRACKETS-P01-START -->", "<!-- HR30-TRANSITION-BRACKETS-P01-END -->"
    if start in text and end in text:
        text = text.split(start, 1)[0] + text.split(end, 1)[1]
    section = f'''{start}<section id="transition-brackets"><h2>The 25 moving power feeds now have physical fixed-transition CAD</h2><div class="grid"><article class="card"><div class="metric">25</div><p>dimensioned nominal placements</p></article><article class="card"><div class="metric">9</div><p>printable fit-coupon openings</p></article><article class="card hold"><div class="metric">0</div><p>received connector fit checks</p></article></div><p><a href="harness/actuator-transition-brackets-p0.1/index.html">Open the interactive bracket, coupon and whole-body placement guide</a>. The diagnostic coupon now provides a controlled first physical fit test; connector cutout, production material, clamp, attachment, tolerance and validation remain open.</p></section>{end}'''
    anchor = "<!-- HR30-FIRST-ENERGIZATION-P01-START -->"
    if anchor in text:
        text = text.replace(anchor, section + anchor, 1)
    elif "</main>" in text:
        text = text.replace("</main>", section + "</main>", 1)
    else:
        raise RuntimeError("whole-body page main element missing")
    page_path.write_text(text, encoding="utf-8", newline="\n")


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    transitions = read_csv(PHYSICAL / "actuator-power-transition-register.csv")
    points = read_csv(PHYSICAL / "route-point-register.csv")
    if len(transitions) != 25:
        raise RuntimeError("25 actuator power transitions required")
    placements = placement_rows(transitions, points)
    spacing = spacing_rows(placements)
    coupon_matrix = coupon_matrix_rows()
    if any(r["nominal_envelope_overlap"] != "NO" for r in spacing):
        bad = [r["placement_id"] for r in spacing if r["nominal_envelope_overlap"] != "NO"]
        raise RuntimeError(f"nominal cassette overlap: {bad}")

    parts = [
        {"part_id":"ATB-BASE-P0.1","description":"panel plate with project-owned clearance proxy and two integral clamp shelves","quantity_per_axis":1,"candidate_material":"PA12 MJF OR MACHINED/PRINTED POLYMER - SELECTION REQUIRED","dimensions_mm":"34 W x 31 overall Y envelope x 28 H; 3 mm panel; 14 x 9.5 proxy window","editable_step":"ATB-BASE-P0.1.step","release_state":"DIMENSIONED CANDIDATE - NOT FABRICATION RELEASED","authority":AUTHORITY,"warning":WARNING},
        {"part_id":"ATB-CLAMP-CAP-P0.1","description":"removable cable-jacket clamp cap; one dynamic and one pigtail side","quantity_per_axis":2,"candidate_material":"PA12 MJF OR MACHINED/PRINTED POLYMER - SELECTION REQUIRED","dimensions_mm":"18 W x 10 L x 6 H; 4.8 cable proxy; 2.7 holes at 12 pitch","editable_step":"ATB-CLAMP-CAP-P0.1.step","release_state":"DIMENSIONED CANDIDATE - CLAMP FORCE/INSERTS OPEN","authority":AUTHORITY,"warning":WARNING},
        {"part_id":"ATB-CONNECTOR-FIT-COUPON-P0.1","description":"nine-window received-housing gross-clearance diagnostic coupon","quantity_per_axis":0,"candidate_material":"PRUSAMENT PETG V0 NATURAL 1 KG (IDF 17666 / IDS 3514) - DIAGNOSTIC COUPON ONLY","dimensions_mm":"96 W x 78 H x 3 T; 3 x 3 openings from 13.5-14.5 W and 9.0-10.0 H","editable_step":"ATB-CONNECTOR-FIT-COUPON-P0.1.step","release_state":"PRINTABLE DIAGNOSTIC CANDIDATE - NOT A PRODUCTION CUTOUT OR BRACKET MATERIAL RELEASE","authority":AUTHORITY,"warning":WARNING},
    ]
    interfaces = [
        {"interface_id":"ATB-I01","interface":"module attachment","candidate_definition":"2 x M3 clearance holes, 26 mm horizontal pitch","verified_state":"PROJECT CANDIDATE ONLY","unresolved":"module insert/fastener/thread engagement/preload/tolerance/load path","authority":AUTHORITY,"warning":WARNING},
        {"interface_id":"ATB-I02","interface":"Molex 430200200 panel connector","candidate_definition":"14 x 9.5 mm central clearance proxy with panel space retained","verified_state":"NOT FIT VERIFIED; NOT A MOLEX CUTOUT","unresolved":"official drawing dimension extraction, revision, ear geometry, latch access, received fit coupon","authority":AUTHORITY,"warning":WARNING},
        {"interface_id":"ATB-I03","interface":"CF130 moving cable strain relief","candidate_definition":"dynamic-side shelf and removable cap around 4.8 mm jacket proxy","verified_state":"NOT CLAMP VERIFIED","unresolved":"exact cable OD, bend entry, clamp pressure, retention, flex life and jacket damage","authority":AUTHORITY,"warning":WARNING},
        {"interface_id":"ATB-I04","interface":"Alpha Wire 3051 pigtail strain relief","candidate_definition":"fixed-side shelf and removable cap; two conductors treated as restrained bundle","verified_state":"NOT CLAMP VERIFIED","unresolved":"bundle sleeving/OD, pigtail length, JST service loop, retention and thermal test","authority":AUTHORITY,"warning":WARNING},
        {"interface_id":"ATB-I05","interface":"received Molex 430200200 diagnostic fit coupon","candidate_definition":"nine rectangular openings: 13.5/14.0/14.5 mm width crossed with 9.0/9.5/10.0 mm height in a 3 mm plate","verified_state":"CAD/PROTOCOL PRESENT; PHYSICAL TEST NOT EXECUTED","unresolved":"official panel-ear/latch/retention cutout, printed dimensions, received lot and fit results","authority":AUTHORITY,"warning":WARNING},
    ]
    holds = [
        {"hold_id":"ATB-H01","unresolved":"official 430200200 manufacturing cutout and retention geometry not extracted/reconciled","evidence_required":"revision-controlled official drawing review plus independent dimensional check","state":"OPEN","authority":AUTHORITY,"warning":WARNING},
        {"hold_id":"ATB-H02","unresolved":"diagnostic coupon CAD/traveler exist but zero coupons or received Micro-Fit connectors have been inspected","evidence_required":"execute coupon traveler, inspect printed openings and received connector lot, record gross clearance/latch/ear/retention results","state":"OPEN","authority":AUTHORITY,"warning":WARNING},
        {"hold_id":"ATB-H03","unresolved":"diagnostic coupon material candidate is defined; production bracket material, process, inserts and fasteners remain unselected","evidence_required":"DFM, material lot, insert/fastener selection, torque/preload and environmental review","state":"OPEN","authority":AUTHORITY,"warning":WARNING},
        {"hold_id":"ATB-H04","unresolved":"CF130 and Alpha 3051 clamp geometry and force unverified","evidence_required":"received cable/bundle dimensions, pull, flex, torsion, temperature and jacket-damage tests","state":"OPEN","authority":AUTHORITY,"warning":WARNING},
        {"hold_id":"ATB-H05","unresolved":"25 nominal placements not reconciled to production body covers/hardware","evidence_required":"joined production CAD with tolerance-aware guard, fastener, cable and service-access collision sweep","state":"OPEN","authority":AUTHORITY,"warning":WARNING},
        {"hold_id":"ATB-H06","unresolved":"no bracket or whole-body hardware fabricated or inspected","evidence_required":"FAI, as-built coordinates, connector/cable assembly inspection and qualified review","state":"OPEN","authority":AUTHORITY,"warning":WARNING},
    ]
    write_csv(OUT / "part-register.csv", parts)
    write_csv(OUT / "interface-register.csv", interfaces)
    write_csv(OUT / "placement-register.csv", placements)
    write_csv(OUT / "spacing-screen.csv", spacing)
    write_csv(OUT / "coupon-opening-matrix.csv", coupon_matrix)
    write_csv(OUT / "coupon-process-traveler.csv", coupon_process_rows())
    write_csv(OUT / "coupon-inspection-register.csv", coupon_inspection_rows(coupon_matrix))
    write_csv(OUT / "source-register.csv", source_rows())
    write_csv(OUT / "open-holds.csv", holds)
    export_cad(placements)
    write_drawings()
    status = {
        "identifier": IDENTIFIER, "warning": WARNING, "generated_date": DATE,
        "standard_base_part_count": 1, "standard_clamp_cap_part_count": 1,
        "placement_count": len(placements), "installed_solid_count": len(placements) * 3,
        "whole_body_step_present": True, "whole_body_glb_present": True,
        "editable_standard_part_step_present": True, "bracket_candidate_dimensioned": True,
        "placement_candidate_defined": True, "nominal_envelope_overlap_count": 0,
        "diagnostic_fit_coupon_present": True, "diagnostic_fit_coupon_opening_count": len(coupon_matrix),
        "diagnostic_fit_coupon_material_candidate_defined": True,
        "diagnostic_fit_coupon_process_traveler_present": True,
        "diagnostic_fit_coupon_physical_test_executed": False,
        "connector_fit_released": False, "manufacturing_cutout_released": False,
        "received_part_fit_verified": False, "material_selected": False,
        "clamp_validated": False, "tolerance_aware_collision_validated": False,
        "fabrication_released": False, "procurement_authority": False,
        "fabrication_authority": False, "connection_authority": False,
        "powered_test_authority": False, "motion_authority": False,
        "energization_authority": False,
    }
    (OUT / "bracket-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n")
    (OUT / "README.md").write_text(f"# HR-30 actuator transition brackets P0.1\n\n**{WARNING}**\n\nThis package supplies real editable part CAD and all 25 nominal placements. It now also includes a printable nine-window connector-fit coupon, a controlled print/test traveler and an unexecuted inspection record. The connector window remains a project-owned clearance proxy, not a released Molex cutout. Open `index.html` for the interactive guide.\n", encoding="utf-8", newline="\n")
    (OUT / "index.html").write_text(render(placements, spacing), encoding="utf-8", newline="\n")
    shutil.copy2(Path(__file__), OUT / "actuator-transition-brackets-source.py")
    manifest = [{"path": p.relative_to(OUT).as_posix(), "bytes": p.stat().st_size, "sha256": sha(p), "warning": WARNING} for p in sorted(OUT.rglob("*")) if p.is_file() and p.name != "file-manifest.csv"]
    write_csv(OUT / "file-manifest.csv", manifest)
    if RELEASE.exists():
        shutil.rmtree(RELEASE)
    shutil.copytree(OUT, RELEASE)
    integrate_root()
    import generate_hr30_system_package_p01 as system_package
    system_package.refresh_manifest_and_release()
    print(json.dumps(status, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
