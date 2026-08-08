"""Generate the separately identified HR-V0 X430 elbow P0.8 candidate.

This is a configuration-comparison artifact, not a fabrication or motion
release.  It registers official ROBOTIS STEP geometry, documents the assembly
datum transform, and produces nominal model-space evidence while leaving
received fit, tolerances, cables, guards, continuous torque, stopping and
qualified acceptance open.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import shutil
import sys
from pathlib import Path

import cadquery as cq
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.gp import gp_Trsf


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import generate_hr_v0_arm_architecture as base  # noqa: E402


REVISION = "HR-V0-ARM-ARCH-P0.8-X430-CANDIDATE"
WARNING = (
    "PRELIMINARY - COMPARISON CANDIDATE ONLY - NOT APPROVED FOR QUOTATION, "
    "PROCUREMENT, FABRICATION, ASSEMBLY, MOTION, CONNECTION, OR ENERGIZATION"
)
OUT = ROOT / "cad" / "hr-v0" / "generated" / "elbow-architecture-p0.8"
VENDOR = ROOT / "cad" / "vendor" / "robotis" / "x430-fr12-r91"
VENDOR_COMMON = ROOT / "cad" / "vendor" / "robotis"

PLATE_T = 9.525
FRAME_HOLE_D = 2.70
END_HOLE_D = 5.50
UPPER_BEAM_L = 100.0
FOREARM_BEAM_L = 50.0
J1_H101_FACE = 32.0
J2_H101_FACE = 28.0
S102_LOCAL_Z_SHIFT = 21.0
S102_FIXED_FACE = 40.5
J2_Y = J1_H101_FACE + PLATE_T + UPPER_BEAM_L + PLATE_T + S102_FIXED_FACE
G1_LOCAL_Y = J2_H101_FACE + PLATE_T + FOREARM_BEAM_L + PLATE_T + 28.0
G1_Y = J2_Y + G1_LOCAL_Y
OBJECT_CENTER_Y = G1_Y + 28.4
SOFT_LIMIT_DEG = 115.0
HARD_STOP_DEG = 118.0
STOP_FIXED_WING_Z = 15.0
STOP_MOVING_WING_Z = 19.9167
SAMPLE_INCREMENT_DEG = 0.5


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty CSV: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def x430_to_joint_frame(shape: cq.Shape) -> cq.Shape:
    """Map X430 local +Z output to joint -X without moving the joint origin."""

    transform = gp_Trsf()
    transform.SetValues(
        0.0, 0.0, -1.0, 2.35,
        1.0, 0.0, 0.0, 0.0,
        0.0, -1.0, 0.0, 0.0,
    )
    return cq.Shape.cast(BRepBuilderAPI_Transform(shape.wrapped, transform, True).Shape())


def cut_adapter_features(shape: cq.Shape, y0: float) -> cq.Shape:
    for x in (-12.0, 12.0):
        for z in (-6.0, 6.0):
            shape = shape.cut(
                cq.Solid.makeCylinder(
                    FRAME_HOLE_D / 2.0,
                    PLATE_T,
                    cq.Vector(x, y0, z),
                    cq.Vector(0.0, 1.0, 0.0),
                )
            )
    for z in (-10.0, 10.0):
        shape = shape.cut(
            cq.Solid.makeCylinder(
                END_HOLE_D / 2.0,
                PLATE_T,
                cq.Vector(0.0, y0, z),
                cq.Vector(0.0, 1.0, 0.0),
            )
        )
        shape = shape.cut(
            cq.Solid.makeCone(
                base.END_CSK_D / 2.0,
                END_HOLE_D / 2.0,
                base.END_CSK_DEPTH,
                cq.Vector(0.0, y0, z),
                cq.Vector(0.0, 1.0, 0.0),
            )
        )
    return shape


def stop_adapter(y0: float, wing_z: float) -> cq.Shape:
    """Plate plus two external integral stop wings; no bumper is credited."""

    shape = cq.Solid.makeBox(48.0, PLATE_T, 40.0, cq.Vector(-24.0, y0, -20.0))
    shape = shape.fuse(cq.Solid.makeBox(17.0, PLATE_T, 6.0, cq.Vector(24.0, y0, wing_z)))
    shape = shape.fuse(cq.Solid.makeBox(17.0, PLATE_T, 6.0, cq.Vector(-41.0, y0, wing_z)))
    return cut_adapter_features(shape, y0)


def first_contact(fixed: cq.Shape, moving: cq.Shape, lo: float, hi: float) -> float:
    for _ in range(44):
        mid = (lo + hi) / 2.0
        volume = fixed.intersect(base.rotate_x(moving, mid)).Volume()
        if volume > 1e-9:
            hi = mid
        else:
            lo = mid
    return hi


def exact_axes(shape: cq.Shape, axis: str, radius: float) -> set[tuple[float, float]]:
    result: set[tuple[float, float]] = set()
    for face in shape.Faces():
        if face.geomType() != "CYLINDER":
            continue
        cylinder = face._geomAdaptor().Cylinder()
        if not math.isclose(cylinder.Radius(), radius, abs_tol=1e-6):
            continue
        direction = cylinder.Axis().Direction()
        location = cylinder.Axis().Location()
        if axis == "X" and abs(direction.X()) > 0.999999:
            result.add((round(location.Y(), 3), round(location.Z(), 3)))
        elif axis == "Y" and abs(direction.Y()) > 0.999999:
            result.add((round(location.X(), 3), round(location.Z(), 3)))
        elif axis == "Z" and abs(direction.Z()) > 0.999999:
            result.add((round(location.X(), 3), round(location.Y(), 3)))
    return result


def drawing_svg(path: Path, part_id: str, wing_z: float, role: str) -> None:
    path.write_text(
        f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="760" viewBox="0 0 1200 760">
<style>text{{font-family:Arial,sans-serif;fill:#102a43;font-size:20px}}.h{{font-size:34px;font-weight:700;fill:#082b55}}.w{{font-weight:700;fill:#9b1c1c}}.d{{stroke:#082b55;stroke-width:3;fill:#e4f6ff}}.c{{stroke:#f4b942;stroke-width:3;fill:none}}.x{{stroke:#9b1c1c;stroke-width:2}}</style>
<rect width="1200" height="760" fill="#f7fbff"/><text x="45" y="60" class="h">{part_id} · X430 elbow {role}</text>
<text x="45" y="100" class="w">{WARNING}</text>
<rect x="330" y="210" width="480" height="300" class="d"/><rect x="160" y="{360-wing_z*6:.1f}" width="170" height="60" class="d"/><rect x="810" y="{360-wing_z*6:.1f}" width="170" height="60" class="d"/>
<circle cx="480" cy="320" r="14" class="c"/><circle cx="720" cy="320" r="14" class="c"/><circle cx="480" cy="440" r="14" class="c"/><circle cx="720" cy="440" r="14" class="c"/>
<circle cx="600" cy="300" r="28" class="c"/><circle cx="600" cy="460" r="28" class="c"/>
<line x1="600" y1="180" x2="600" y2="540" class="x"/><line x1="130" y1="380" x2="1010" y2="380" class="x"/>
<text x="45" y="590">Envelope: base 48 × 40 × 9.525 mm; two 17 × 6 mm integral wings; wing Z={wing_z:.4f} mm.</text>
<text x="45" y="625">Frame axes: X=±12, Z=±6, Ø2.70. Member axes: X=0, Z=±10, Ø5.50 with candidate countersinks.</text>
<text x="45" y="660">Coordinates are nominal model-space controls only. Material, tolerance, edge treatment, bumper, FAI and proof remain open.</text>
<text x="45" y="705" class="w">DO NOT QUOTE OR FABRICATE FROM THIS REVIEW DRAWING.</text></svg>''',
        encoding="utf-8",
        newline="\n",
    )


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "parts").mkdir(parents=True)

    x430_raw = cq.importers.importStep(str(VENDOR / "x-430_idle.stp")).val()
    h101 = cq.importers.importStep(str(VENDOR / "fr12_h101.stp")).val()
    s102_raw = cq.importers.importStep(str(VENDOR / "fr12_s102.stp")).val()
    h104 = cq.importers.importStep(str(VENDOR_COMMON / "FR12-H104K.stp")).val()

    x430_mounts = {(-11.0, -32.0), (11.0, -32.0)}
    s102_mounts = {(-11.0, 11.0), (11.0, 11.0)}
    h101_link_axes = {(-12.0, -6.0), (-12.0, 6.0), (12.0, -6.0), (12.0, 6.0)}
    if not x430_mounts <= exact_axes(x430_raw, "Z", 1.25):
        raise RuntimeError("controlled X430 STEP lost selected rear case axes")
    if not s102_mounts <= exact_axes(s102_raw, "X", 1.3):
        raise RuntimeError("controlled FR12-S102 STEP lost selected side axes")
    if not h101_link_axes <= exact_axes(h101, "Y", 1.3):
        raise RuntimeError("controlled FR12-H101 STEP lost selected link axes")

    x430 = base.rotate_x(x430_to_joint_frame(x430_raw), 90.0)
    s102 = base.rotate_x(s102_raw.translate((0.0, 0.0, S102_LOCAL_Z_SHIFT)), 90.0)
    fixed_catch = stop_adapter(-S102_FIXED_FACE - PLATE_T, STOP_FIXED_WING_Z)
    upper_beam = base.beam(-S102_FIXED_FACE - PLATE_T - UPPER_BEAM_L, UPPER_BEAM_L)
    moving_striker = stop_adapter(J2_H101_FACE, STOP_MOVING_WING_Z)
    forearm_beam = base.beam(J2_H101_FACE + PLATE_T, FOREARM_BEAM_L)
    distal = base.gripper_adapter(J2_H101_FACE + PLATE_T + FOREARM_BEAM_L)
    gripper_frame = base.rotate_x(h104, 180.0).translate((0.0, G1_LOCAL_Y, 0.0))

    fixed = {
        "J2_X430_RX90": x430,
        "J2_FR12_S102_RX90": s102,
        "P08_CATCH": fixed_catch,
        "UPPER_20-2040_ENVELOPE": upper_beam,
    }
    moving = {
        "J2_FR12_H101": h101,
        "P08_STRIKER": moving_striker,
        "FOREARM_20-2040_ENVELOPE": forearm_beam,
        "P08_H104_ADAPTER": distal,
        "G1_FR12_H104_RX180": gripper_frame,
    }
    intentional = {
        ("J2_X430_RX90", "J2_FR12_H101"),
        ("J2_FR12_S102_RX90", "J2_FR12_H101"),
        ("P08_CATCH", "P08_STRIKER"),
    }

    components = {**fixed, **moving}
    assembly = cq.Assembly(name="HR_V0_X430_ELBOW_P08_CANDIDATE_NOT_RELEASED")
    for name, shape in components.items():
        color = cq.Color(0.10, 0.32, 0.58)
        if "FR12" in name:
            color = cq.Color(0.96, 0.70, 0.12)
        if "CATCH" in name:
            color = cq.Color(0.72, 0.16, 0.12)
        if "STRIKER" in name:
            color = cq.Color(0.95, 0.42, 0.10)
        assembly.add(shape, name=name, color=color)
    step_path = OUT / "HR-V0_X430_elbow_P0.8_candidate.step"
    cq.exporters.export(cq.Compound.makeCompound(list(components.values())), str(step_path))
    base.canonicalize_step(step_path)
    assembly.save(str(OUT / "HR-V0_X430_elbow_P0.8_candidate.glb"))

    for name, shape in {
        "P08-C01_X430_fixed-catch-adapter": fixed_catch.translate((0.0, S102_FIXED_FACE + PLATE_T, 0.0)),
        "P08-C02_X430_moving-striker-adapter": moving_striker.translate((0.0, -J2_H101_FACE, 0.0)),
    }.items():
        part = OUT / "parts" / f"{name}.step"
        cq.exporters.export(shape, str(part))
        base.canonicalize_step(part)
    drawing_svg(OUT / "P08-C01_fixed-catch-review-drawing.svg", "P08-C01", STOP_FIXED_WING_Z, "fixed catch")
    drawing_svg(OUT / "P08-C02_moving-striker-review-drawing.svg", "P08-C02", STOP_MOVING_WING_Z, "moving striker")

    contact_deg = first_contact(fixed_catch, moving_striker, 116.0, 120.0)
    if abs(contact_deg - HARD_STOP_DEG) > 0.01:
        raise RuntimeError(f"nominal stop contact {contact_deg:.6f} deg misses 118 deg target")

    collision_rows: list[dict[str, object]] = []
    first_nonintentional: float | None = None
    maximum_before_soft = 0.0
    maximum_before_stop = 0.0
    for index in range(int(round((125.0 - 15.0) / SAMPLE_INCREMENT_DEG)) + 1):
        angle = 15.0 + index * SAMPLE_INCREMENT_DEG
        transformed = {name: base.rotate_x(shape, angle) for name, shape in moving.items()}
        volume = 0.0
        pairs: list[str] = []
        for fixed_name, fixed_shape in fixed.items():
            for moving_name, moving_shape in transformed.items():
                if (fixed_name, moving_name) in intentional:
                    continue
                if base.boxes_overlap(fixed_shape, moving_shape):
                    pair_volume = base.positive_intersection(fixed_shape, moving_shape)
                    volume += pair_volume
                    if pair_volume > 1e-5:
                        pairs.append(f"{fixed_name}:{moving_name}={pair_volume:.6f}")
        stop_volume = fixed_catch.intersect(transformed["P08_STRIKER"]).Volume()
        if volume > 1e-5 and first_nonintentional is None:
            first_nonintentional = angle
        if angle <= SOFT_LIMIT_DEG:
            maximum_before_soft = max(maximum_before_soft, volume)
        if angle <= HARD_STOP_DEG:
            maximum_before_stop = max(maximum_before_stop, volume)
        collision_rows.append(
            {
                "j2_deg": f"{angle:.1f}",
                "nonintentional_intersection_mm3": f"{volume:.9f}",
                "nonintentional_pairs": ";".join(pairs),
                "stop_pair_intersection_mm3": f"{stop_volume:.9f}",
                "classification": "SOFT_LIMIT" if angle == SOFT_LIMIT_DEG else ("STOP_TARGET" if angle == HARD_STOP_DEG else "SAMPLED_POSE"),
                "status": "NOMINAL RIGID BODY SAMPLE ONLY - CONTINUOUS/TOLERANCE/CABLE/GUARD/PHYSICAL PROOF OPEN",
            }
        )
    write_csv(OUT / "collision-sweep.csv", collision_rows)

    stop_rows = []
    for index in range(61):
        angle = SOFT_LIMIT_DEG + index * 0.05
        moved = base.rotate_x(moving_striker, angle)
        stop_rows.append(
            {
                "j2_deg": f"{angle:.2f}",
                "metal_clearance_mm": f"{fixed_catch.distance(moved):.9f}",
                "metal_intersection_mm3": f"{fixed_catch.intersect(moved).Volume():.9f}",
                "classification": "SOFT_LIMIT" if index == 0 else ("TARGET" if index == 60 else "APPROACH"),
                "status": "NOMINAL CAD ONLY - BUMPER/TOLERANCE/STOPPING/LOAD/PHYSICAL VALIDATION OPEN",
            }
        )
    write_csv(OUT / "hard-stop-sweep.csv", stop_rows)

    feature_rows = [
        {
            "feature_id": "P08-FEAT-001",
            "source": "cad/vendor/robotis/x430-fr12-r91/x-430_idle.stp",
            "sha256": sha256(VENDOR / "x-430_idle.stp"),
            "selected_axes": "local Z at X=+/-11,Y=-32; diameter 2.5 cylindrical subset",
            "registration": "matrix maps to joint X axes at Y=+/-11,Z=32 before package roll",
            "status": "EXACT STEP AXES; RECEIVED FIT/IDENTITY/FAI OPEN",
        },
        {
            "feature_id": "P08-FEAT-002",
            "source": "cad/vendor/robotis/x430-fr12-r91/fr12_s102.stp",
            "sha256": sha256(VENDOR / "fr12_s102.stp"),
            "selected_axes": "local X at Y=+/-11,Z=11; diameter 2.6",
            "registration": "translate local Z +21 -> Z=32; exact match to X430 rear axes before package roll",
            "status": "EXACT STEP AXES; DRAWING REFERENCE ONLY; RECEIVED FIT/FAI OPEN",
        },
        {
            "feature_id": "P08-FEAT-003",
            "source": "cad/vendor/robotis/x430-fr12-r91/fr12_h101.stp",
            "sha256": sha256(VENDOR / "fr12_h101.stp"),
            "selected_axes": "local Y at X=+/-12,Z=+/-6; diameter 2.6",
            "registration": "P08-C02 adapter holes diameter 2.70 at exact axes; face offset 28 mm",
            "status": "EXACT STEP AXES; DRAWING REFERENCE ONLY; RECEIVED FIT/FAI OPEN",
        },
    ]
    write_csv(OUT / "interface-feature-evidence.csv", feature_rows)

    transform_rows = [
        {
            "item": "X430 actuator",
            "parent": "J2",
            "transform": "raw +Z output -> joint -X; axial Tx=2.35 mm; then package Rx=90 deg",
            "registration_evidence": "rear case local Z axes X=+/-11,Y=-32 map to FR12-S102 side axes after +21 mm frame shift",
            "status": "EXACT MODEL REGISTRATION; RECEIVED HORN/IDLER STACK MEASUREMENT OPEN",
        },
        {
            "item": "FR12-S102 fixed frame",
            "parent": "J2",
            "transform": "local Tz=+21 mm; then package Rx=90 deg",
            "registration_evidence": "local side axes Z=11 become joint-registration Z=32; outside face becomes Y=-40.5 mm",
            "status": "EXACT STEP REGISTRATION; RECEIVED FIT OPEN",
        },
        {
            "item": "FR12-H101 moving frame",
            "parent": "J2 moving",
            "transform": "identity at straight reference; rotates about joint +X",
            "registration_evidence": "outside link face at Y=28 mm and exact X=+/-12,Z=+/-6 axes",
            "status": "EXACT STEP REGISTRATION; RECEIVED FIT OPEN",
        },
    ]
    write_csv(OUT / "transform-schedule.csv", transform_rows)

    interface_rows = [
        {
            "interface": "P08-A01",
            "from": "upper 20-2040 envelope",
            "to": "P08-C01 fixed catch / FR12-S102",
            "coordinates": "beam M5 axes X=0,Z=+/-10; frame axes X=+/-12,Z=+/-6; fixed face J2 Y=-40.5",
            "fastener_state": "SELECTION REQUIRED; existing P0.7 candidates are not inherited without stack proof",
            "status": "NOMINAL GEOMETRY REGISTERED; STRUCTURAL/FAI/PROOF OPEN",
        },
        {
            "interface": "P08-A02",
            "from": "FR12-H101 moving face",
            "to": "P08-C02 striker / forearm 20-2040",
            "coordinates": "frame axes X=+/-12,Z=+/-6; beam M5 axes X=0,Z=+/-10; moving face J2 Y=28",
            "fastener_state": "SELECTION REQUIRED; received screw/nut stack and access proof required",
            "status": "NOMINAL GEOMETRY REGISTERED; STRUCTURAL/FAI/PROOF OPEN",
        },
        {
            "interface": "P08-HS-J2",
            "from": "P08-C02 twin integral wings",
            "to": "P08-C01 twin integral wings",
            "coordinates": f"nominal first positive volume at {contact_deg:.6f} deg; soft limit {SOFT_LIMIT_DEG:.1f} deg",
            "fastener_state": "integral aluminum profiles; bumper material/retention SELECTION REQUIRED",
            "status": "CAD CANDIDATE ONLY; TOLERANCE/LOAD/STOPPING/REBOUND/PHYSICAL PROOF OPEN",
        },
    ]
    write_csv(OUT / "interface-schedule.csv", interface_rows)

    density_g_mm3 = 2.70 / 1000.0
    catch_mass = fixed_catch.Volume() * density_g_mm3
    striker_mass = moving_striker.Volume() * density_g_mm3
    p07_known = 692.758
    p08_known = p07_known - 165.0 - 66.870 - 70.265 + 82.0 + catch_mass + striker_mass
    headroom = 750.0 - p08_known
    beam_mass_per_m_kg = 0.0428 * 0.45359237 / 0.0254
    fore_beam_mass = beam_mass_per_m_kg * (FOREARM_BEAM_L / 1000.0) * 1000.0
    distal_mass = distal.Volume() * density_g_mm3
    fore_mass = striker_mass + fore_beam_mass + distal_mass
    fore_com = (
        striker_mass * (J2_H101_FACE + PLATE_T / 2.0)
        + fore_beam_mass * (J2_H101_FACE + PLATE_T + FOREARM_BEAM_L / 2.0)
        + distal_mass * (J2_H101_FACE + PLATE_T + FOREARM_BEAM_L + PLATE_T / 2.0)
    ) / fore_mass
    gravity = 9.80665
    elbow_gravity = gravity * (
        fore_mass / 1000.0 * fore_com / 1000.0
        + 0.21 * G1_LOCAL_Y / 1000.0
        + 0.10 * (OBJECT_CENTER_Y - J2_Y) / 1000.0
    )
    elbow_screen = elbow_gravity * 2.25
    endpoint_ratio = 4.1 / elbow_screen
    mass_rows = [
        {
            "configuration": "P0.7 controlled unreleased",
            "j2_actuator": "XM540-W270-T",
            "j1_to_j2_mm": "202.550",
            "j2_to_g1_mm": "129.050",
            "candidate_object_center_mm": "360.000",
            "incomplete_known_mass_g": "692.758",
            "headroom_to_750_g": "57.242",
            "elbow_screen_nm": "1.158",
            "12v_stall_endpoint_ratio": "9.154",
            "status": "CONTROLLED BUT UNRELEASED; INCOMPLETE MASS AND PHYSICAL EVIDENCE",
        },
        {
            "configuration": "P0.8 X430 exact-coordinate candidate",
            "j2_actuator": "XM430-W350-T",
            "j1_to_j2_mm": f"{J2_Y:.3f}",
            "j2_to_g1_mm": f"{G1_LOCAL_Y:.3f}",
            "candidate_object_center_mm": f"{OBJECT_CENTER_Y:.3f}",
            "incomplete_known_mass_g": f"{p08_known:.3f}",
            "headroom_to_750_g": f"{headroom:.3f}",
            "elbow_screen_nm": f"{elbow_screen:.3f}",
            "12v_stall_endpoint_ratio": f"{endpoint_ratio:.3f}",
            "status": "COMPARISON CANDIDATE; FRAME/FASTENER/CABLE/GRIPPER/BUMPER MASS AND CONTINUOUS TORQUE OPEN",
        },
    ]
    write_csv(OUT / "mass-load-comparison.csv", mass_rows)

    source_holds = list(csv.DictReader((ROOT / "release" / "hr-v0" / "elbow-actuator-trade-p0.1" / "architecture-holds.csv").open(encoding="utf-8")))
    for row in source_holds:
        if row["hold_id"] in {"ELBH-002", "ELBH-007", "ELBH-008"}:
            row["state"] = "PARTIAL"
            row["release_effect"] += "; P0.8 nominal CAD evidence exists but physical closure is absent"
    write_csv(OUT / "architecture-holds.csv", source_holds)

    summary = {
        "revision": REVISION,
        "warning": WARNING,
        "configuration_disposition": "P0.8 comparison candidate only; P0.7 remains controlled and XM430 is not selected",
        "geometry_mm": {
            "j1_to_j2_axis": round(J2_Y, 3),
            "j2_to_g1_frame_origin": round(G1_LOCAL_Y, 3),
            "candidate_object_center_from_j1": round(OBJECT_CENTER_Y, 3),
            "fr12_s102_local_z_registration_shift": S102_LOCAL_Z_SHIFT,
            "fr12_s102_fixed_face_offset": S102_FIXED_FACE,
            "fr12_h101_moving_face_offset": J2_H101_FACE,
        },
        "assembly_model_overlap_review_mm3": {
            "x430_with_fr12_s102": round(x430.intersect(s102).Volume(), 6),
            "x430_with_fr12_h101_straight_reference": round(x430.intersect(h101).Volume(), 6),
            "fr12_s102_with_fr12_h101_straight_reference": round(s102.intersect(h101).Volume(), 6),
            "status": "intentional assembly-interface candidate overlaps; independent transform audit and received fit required",
        },
        "stop": {
            "soft_limit_deg": SOFT_LIMIT_DEG,
            "nominal_first_contact_deg": round(contact_deg, 6),
            "maximum_nonintentional_intersection_through_soft_limit_mm3": round(maximum_before_soft, 9),
            "maximum_nonintentional_intersection_through_stop_mm3": round(maximum_before_stop, 9),
            "first_sampled_nonintentional_collision_deg": first_nonintentional,
            "status": "nominal rigid-body sampled evidence only; continuous/tolerance/cable/guard/stopping/physical proof open",
        },
        "mass_and_load": {
            "fixed_catch_cad_mass_g": round(catch_mass, 3),
            "moving_striker_cad_mass_g": round(striker_mass, 3),
            "incomplete_known_mass_g": round(p08_known, 3),
            "provisional_headroom_to_750_g": round(headroom, 3),
            "elbow_gravity_nm": round(elbow_gravity, 3),
            "elbow_2_25_screen_nm": round(elbow_screen, 3),
            "xm430_12v_stall_endpoint_ratio_only": round(endpoint_ratio, 3),
            "status": "incomplete screen; not continuous capacity, safety factor, thermal proof, or mass closure",
        },
        "source_sha256": {
            "x-430_idle.stp": sha256(VENDOR / "x-430_idle.stp"),
            "fr12_h101.stp": sha256(VENDOR / "fr12_h101.stp"),
            "fr12_s102.stp": sha256(VENDOR / "fr12_s102.stp"),
            "FR12-H104K.stp": sha256(VENDOR_COMMON / "FR12-H104K.stp"),
        },
        "release_flags": {
            "supersedes_p0_7": False,
            "xm430_selected": False,
            "quotation_authorized": False,
            "procurement_authorized": False,
            "fabrication_authorized": False,
            "assembly_authorized": False,
            "motion_authorized": False,
            "connection_authorized": False,
            "energization_authorized": False,
        },
    }
    (OUT / "architecture-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8", newline="\n")
    (OUT / "package-status.json").write_text(
        json.dumps(
            {
                "revision": REVISION,
                "state": "COMPARISON_CANDIDATE_NOT_SELECTED",
                "warning": WARNING,
                "open_hold_count": sum(row["state"] == "OPEN" for row in source_holds),
                "partial_hold_count": sum(row["state"] == "PARTIAL" for row in source_holds),
                "release_flags": summary["release_flags"],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
