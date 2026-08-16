"""Generate the HR-30 P0.1 whole-body mass reconciliation.

This is a planning model, not an as-built mass property.  It combines the
material-density screens for the fabrication CAD and joint-module CAD with
current official actuator masses.  Interpenetrating candidate parts are not
deducted, and unselected equipment remains outside the identified subtotal.
"""

from __future__ import annotations

import csv
import json
import re
import shutil
from collections import Counter, defaultdict
from pathlib import Path

import generate_hr30_body_architecture_p01 as body
import generate_hr30_joint_fasteners_p01 as joint_fasteners
import generate_hr30_installed_equipment_p01 as equipment
import generate_hr30_fabrication_architecture_p01 as fabrication
import generate_hr30_system_package_p01 as system


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "hr30" / "whole-body-p0.1"
IDENTIFIER = "HR-30-MASS-RECONCILIATION-P0.1"
WARNING = body.WARNING
ACCESSED = "2026-08-14"
BASELINE_COMMIT = "dfb9a7d"
PRODUCT_MASS_TARGET_KG = 8.0
PRODUCT_MASS_HARD_LIMIT_KG = 10.0
ONBOARD_ENERGY_ENVELOPE_IDS = {
    "EQ-T01-BATTERY-PACK",
    "EQ-T01-BATTERY-CASSETTE",
    "EQ-T01-BATTERY-PROTECTION",
}
BASELINE_MASS = {
    "fabrication": 3.605845154,
    "actuators": 3.391,
    "joint_hardware": 6.327138769,
    "identified": 13.323983923,
    "dynamics": 16.675074212,
}

ACTUATOR_SOURCES = {
    "ROBOTIS XH540-W270-R": {
        "mass_kg": 0.165,
        "url": "https://emanual.robotis.com/docs/en/dxl/x/xh540-w270/",
        "source_note": "Current official ROBOTIS e-Manual; live page has no published page revision/date.",
    },
    "ROBOTIS XM540-W270-R": {
        "mass_kg": 0.165,
        "url": "https://emanual.robotis.com/docs/en/dxl/x/xm540-w270/",
        "source_note": "Current official ROBOTIS e-Manual; live page has no published page revision/date.",
    },
    "ROBOTIS XM430-W350-R": {
        "mass_kg": 0.082,
        "url": "https://emanual.robotis.com/docs/en/dxl/x/xm430-w350/",
        "source_note": "Current official ROBOTIS e-Manual; live page has no published page revision/date.",
    },
    "ROBOTIS XC330-T288-T": {
        "mass_kg": 0.023,
        "url": "https://emanual.robotis.com/docs/en/dxl/x/xc330-t288/",
        "source_note": "Current official ROBOTIS e-Manual; live page has no published page revision/date.",
    },
}


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise RuntimeError(f"refusing empty CSV: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def axis_from_component(name: str) -> str:
    prefix = "JMOD_"
    suffix = "_ACTUATOR_VENDOR_CANDIDATE"
    if not name.startswith(prefix) or not name.endswith(suffix):
        raise ValueError(name)
    return name[len(prefix) : -len(suffix)]


def axis_link(axis_id: str) -> str:
    if axis_id == "WAIST_YAW":
        return "base_link"
    if axis_id == "HEAD_PAN":
        return "neck_pan_link"
    if axis_id == "HEAD_TILT":
        return "head"
    side = axis_id[0] if axis_id[:2] in ("L_", "R_") else None
    if not side:
        raise KeyError(axis_id)
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


def fabrication_link(module: str, name: str) -> str:
    fixed = {"T01": "torso", "P01": "base_link", "N01": "neck_pan_link", "H01": "head"}
    if module in fixed:
        return fixed[module]
    side = "L" if module.endswith("1") else "R"
    if module.startswith("A0"):
        if "UPPER_ARM" in name:
            return f"{side}_upper_arm"
        if "FOREARM" in name:
            return f"{side}_forearm"
    if module.startswith("G0"):
        return f"{side}_hand"
    if module.startswith("L0"):
        if "THIGH" in name:
            return f"{side}_thigh"
        if "SHIN" in name:
            return f"{side}_shin"
    if module.startswith("F0"):
        return f"{side}_foot"
    raise KeyError(f"unmapped fabrication part: {module}/{name}")


def actuator_choice(axis_id: str) -> tuple[str, float, float, float, str]:
    if axis_id.startswith("HEAD_") or "GRIPPER" in axis_id or "WRIST_ROTATION" in axis_id:
        name = "ROBOTIS XC330-T288-T"
        mass = ACTUATOR_SOURCES[name]["mass_kg"]
        return name, mass, mass, mass, "whole-body static-load candidate; exact suffix, duty, rail and interface remain open"
    if "ANKLE_" in axis_id:
        name = "ROBOTIS XM430-W350-R"
        mass = ACTUATOR_SOURCES[name]["mass_kg"]
        return name, mass, mass, mass, "reduced ankle candidate; continuous-duty, belt capacity, thermal and walking suitability unproved"
    if any(token in axis_id for token in ("HIP_", "KNEE_")):
        name = "ROBOTIS XH540-W270-R"
        mass = ACTUATOR_SOURCES[name]["mass_kg"]
        return name, mass, mass, mass, "evaluation candidate; continuous-duty and walking suitability unproved"
    if "SHOULDER_" in axis_id:
        name = "ROBOTIS XM430-W350-R"
        mass = ACTUATOR_SOURCES[name]["mass_kg"]
        return name, mass, mass, mass, "1.5:1 reduced whole-body shoulder candidate; continuous, dynamic and thermal proof remains open"
    if "ELBOW_PITCH" in axis_id:
        name = "ROBOTIS XM430-W350-R"
        mass = ACTUATOR_SOURCES[name]["mass_kg"]
        return name, mass, mass, mass, "whole-body P0.1 static-load candidate; continuous, dynamic and thermal proof remains open"
    name = "ROBOTIS XM540-W270-R"
    mass = ACTUATOR_SOURCES[name]["mass_kg"]
    return name, mass, mass, mass, "candidate; exact suffix/interface selection remains open"


def hardware_material(name: str) -> tuple[str, float]:
    if "OUTPUT_SHAFT" in name:
        return "7075-T6/T651 ALUMINUM HOLLOW SHAFT DENSITY SCREEN", 2810.0
    if any(token in name for token in ("BEARING_", "ACTUATOR_OUTPUT_COUPLER")):
        return "STEEL GEOMETRIC DENSITY SCREEN", 7850.0
    if any(token in name for token in ("INTERFACE_PLATE", "OUTPUT_PULLEY", "MOTOR_PULLEY", "SYMMETRIC_DRIVE_COUPLER")):
        return "ALUMINUM GEOMETRIC DENSITY SCREEN", 2700.0
    raise KeyError(name)


def add_item(rows: list[dict], *, item_id: str, category: str, component: str, link: str,
             candidate: str, density: float | str, volume: float | str,
             minimum: float, planning: float, maximum: float, center_mm,
             basis: str, state: str) -> None:
    rows.append({
        "item_id": item_id,
        "category": category,
        "source_component": component,
        "dynamic_link": link,
        "candidate_material_or_model": candidate,
        "density_screen_kg_m3": f"{density:.1f}" if isinstance(density, float) else density,
        "cad_volume_mm3": f"{volume:.6f}" if isinstance(volume, float) else volume,
        "minimum_candidate_mass_kg": f"{minimum:.9f}",
        "planning_candidate_mass_kg": f"{planning:.9f}",
        "maximum_candidate_mass_kg": f"{maximum:.9f}",
        "placement_x_m": f"{center_mm.x / 1000.0:.9f}",
        "placement_y_m": f"{center_mm.y / 1000.0:.9f}",
        "placement_z_m": f"{center_mm.z / 1000.0:.9f}",
        "basis_and_limit": basis,
        "selection_state": state,
        "warning": WARNING,
    })


def build_items() -> tuple[list[dict], list[dict]]:
    items: list[dict] = []
    source_rows = []
    for model, source in ACTUATOR_SOURCES.items():
        source_rows.append({
            "manufacturer": "ROBOTIS",
            "model": model,
            "published_mass_kg": f"{source['mass_kg']:.6f}",
            "official_url": source["url"],
            "document_revision_or_date": "NOT PUBLISHED ON LIVE PAGE",
            "accessed_date": ACCESSED,
            "verification_note": source["source_note"],
            "selection_state": "MASS VALUE VERIFIED; PROJECT APPLICATION/SELECTION REMAINS PRELIMINARY",
            "warning": WARNING,
        })

    fabrication_parts, _, _ = fabrication.build()
    for part in fabrication_parts:
        if part.density_kg_m3 <= 1.0:
            continue
        mass = fabrication.volume_mass_kg(part.shape, part.density_kg_m3)
        add_item(
            items, item_id=f"FAB-{part.name}", category="FABRICATION CAD DENSITY SCREEN",
            component=part.name, link=fabrication_link(part.module, part.name),
            candidate=part.material_candidate, density=float(part.density_kg_m3),
            volume=float(part.shape.Volume()), minimum=mass, planning=mass, maximum=mass,
            center_mm=part.shape.Center(),
            basis="candidate CAD volume times stated density; material, manufacturing and received mass unverified",
            state="GEOMETRIC MATERIAL SCREEN ONLY",
        )

    body_components, body_axes, _, _ = body.build()
    actuator_parts = [p for p in body_components if p.physical and p.name.endswith("_ACTUATOR_VENDOR_CANDIDATE")]
    if len(actuator_parts) != 25:
        raise RuntimeError(f"expected 25 actuator bodies, found {len(actuator_parts)}")
    for part in actuator_parts:
        axis_id = axis_from_component(part.name)
        candidate, minimum, planning, maximum, state = actuator_choice(axis_id)
        add_item(
            items, item_id=f"ACT-{axis_id}", category="MANUFACTURER PUBLISHED ACTUATOR MASS",
            component=part.name, link=axis_link(axis_id), candidate=candidate,
            density="N/A", volume=float(part.shape.Volume()), minimum=minimum, planning=planning, maximum=maximum,
            center_mm=part.shape.Center(),
            basis="official published product mass; placement uses SHA-bound packaging BRep geometric centroid, not a published actuator CG",
            state=state.upper(),
        )

    module_parts = [
        p for p in body_components
        if p.physical and p.name.startswith("JMOD_") and not p.name.endswith("_ACTUATOR_VENDOR_CANDIDATE")
    ]
    for part in module_parts:
        axis_id = part.name[len("JMOD_"):].split("_OUTPUT_SHAFT", 1)[0]
        if "_BEARING_" in axis_id:
            axis_id = axis_id.split("_BEARING_", 1)[0]
        elif "_INTERFACE_PLATE_" in axis_id:
            axis_id = axis_id.split("_INTERFACE_PLATE_", 1)[0]
        elif "_OUTPUT_PULLEY" in axis_id:
            axis_id = axis_id.split("_OUTPUT_PULLEY", 1)[0]
        elif "_MOTOR_PULLEY" in axis_id:
            axis_id = axis_id.split("_MOTOR_PULLEY", 1)[0]
        elif "_ACTUATOR_OUTPUT_COUPLER" in axis_id:
            axis_id = axis_id.split("_ACTUATOR_OUTPUT_COUPLER", 1)[0]
        elif "_SYMMETRIC_DRIVE_COUPLER" in axis_id:
            axis_id = axis_id.split("_SYMMETRIC_DRIVE_COUPLER", 1)[0]
        material, density = hardware_material(part.name)
        if "_BEARING_" in part.name:
            family_id = body.joint_module_family(axis_id)
            bearing = body.BEARING_CANDIDATES[body.JOINT_MODULE_FAMILIES[family_id]["bearing_id"]]
            material = f"{bearing['manufacturer']} {bearing['designation']} PUBLISHED MASS"
            density_value: float | str = "N/A"
            mass = bearing["mass_kg"]
            basis = (
                "current official manufacturer catalogue mass; CAD is only the principal-dimension envelope; "
                "load direction, life, suffix, lubrication, fits, retention and received identity unverified"
            )
            state = "CATALOGUE EVALUATION CANDIDATE; APPLICATION SELECTION REQUIRED"
        else:
            density_value = density
            mass = part.shape.Volume() * 1e-9 * density
            basis = "candidate envelope volume times generic density; exact component geometry, voids, fits and received mass unverified"
            state = "GROSS NO-OVERLAP-DEDUCTION SCREEN; NOT A SELECTED HARDWARE MASS"
        add_item(
            items, item_id=f"JHW-{part.name}", category="JOINT HARDWARE CAD DENSITY SCREEN",
            component=part.name, link=axis_link(axis_id), candidate=material,
            density=density_value, volume=float(part.shape.Volume()), minimum=mass, planning=mass, maximum=mass,
            center_mm=part.shape.Center(),
            basis=basis,
            state=state,
        )

    # Replace the formerly hidden screw allowance with the exact P0.1
    # fastener geometry located through every joint-carrier hole.  These remain
    # generic-density candidates, not selected products or preload evidence.
    for fastener in joint_fasteners.build(body_axes):
        mass = float(fastener.row["planning_mass_kg"])
        add_item(
            items, item_id=fastener.fastener_id, category="LOCATED JOINT FASTENER CAD DENSITY SCREEN",
            component=fastener.fastener_id, link=fastener.dynamic_link,
            candidate=f"{fastener.candidate_size} metric socket-head geometry candidate",
            density=joint_fasteners.STEEL_DENSITY_KG_M3, volume=float(fastener.shape.Volume()),
            minimum=mass * 0.90, planning=mass, maximum=mass * 1.15,
            center_mm=fastener.shape.Center(),
            basis=("located screw envelope through an actual joint-carrier hole; generic steel density; "
                   "exact product/property class/thread/tapped member/torque/preload/locking and received mass unverified"),
            state="LOCATED GEOMETRIC CANDIDATE; SELECTION AND JOINT VALIDATION REQUIRED",
        )

    # The ten reduced leg joints now carry explicit current-catalogue belt
    # mass.  Pulley mass remains the custom spoked CAD density screen above;
    # tooth capacity, tensioning, guards and pulley manufacture remain open.
    for axis in body_axes:
        axis_id = axis["axis_id"]
        family = body.JOINT_MODULE_FAMILIES[body.joint_module_family(axis_id)]
        if family["motor_offset"] <= 0:
            continue
        if "HIP_PITCH" in axis_id:
            belt, mass = "Gates 225-5MGT3-15 / product 9400-55278", 0.014
        elif any(token in axis_id for token in ("HIP_ROLL", "KNEE_PITCH", "ANKLE_PITCH", "ANKLE_ROLL")):
            belt, mass = "Gates 250-5MGT3-15 / product 9400-55245", 0.015
        else:
            continue
        add_item(
            items, item_id=f"BELT-{axis_id}", category="MANUFACTURER PUBLISHED TRANSMISSION MASS",
            component=f"JMOD_{axis_id}_BELT", link=axis_link(axis_id), candidate=belt,
            density="N/A", volume="N/A", minimum=mass, planning=mass, maximum=mass,
            center_mm=body.cq.Vector(float(axis["x_mm"]), float(axis["y_mm"]), float(axis["z_mm"])),
            basis="Gates 2025 catalogue published belt mass; custom pulley, capacity, alignment, tension, guard and received mass unverified",
            state="CATALOGUE BELT CANDIDATE; TRANSMISSION SELECTION REQUIRED",
        )

    installed_items = equipment.build()
    for part in installed_items:
        center = part.shape.Center()
        verified_mass = "9 g verified" in part.evidence_state or "0.123 kg" in part.evidence_state
        minimum = part.planning_mass_kg if verified_mass else part.planning_mass_kg * 0.80
        maximum = part.planning_mass_kg if verified_mass else part.planning_mass_kg * 1.25
        add_item(
            items, item_id=part.item_id, category="INSTALLED EQUIPMENT / HARNESS PLANNING MASS",
            component=part.item_id, link=part.dynamic_link, candidate=part.candidate,
            density="N/A", volume=float(part.shape.Volume()), minimum=minimum,
            planning=part.planning_mass_kg, maximum=maximum, center_mm=center,
            basis=(f"located installed-equipment candidate; {part.evidence_state}; mounting={part.mounting_plane}; "
                   f"service={part.service_direction}"),
            state="CANDIDATE / SELECTION REQUIRED; NO PROCUREMENT OR ENERGIZATION AUTHORITY",
        )
    return items, source_rows


def reconcile(items: list[dict]) -> tuple[list[dict], list[dict], dict]:
    baseline = {row["link"]: row for row in system.link_rows()}
    by_link: dict[str, list[dict]] = defaultdict(list)
    for item in items:
        by_link[item["dynamic_link"]].append(item)

    link_rows = []
    dynamics_rows = []
    for link, base in baseline.items():
        members = by_link.get(link, [])
        minimum = sum(float(r["minimum_candidate_mass_kg"]) for r in members)
        planning = sum(float(r["planning_candidate_mass_kg"]) for r in members)
        maximum = sum(float(r["maximum_candidate_mass_kg"]) for r in members)
        allocation = float(base["mass"])
        # The former allocations no longer mask or inflate the explicit model.
        # Preserve the pre-existing 8% non-fastener integration reserve while
        # converting its hidden screw allowance into explicit located hardware.
        # If a link's explicit screws consume that reserve, only the unused
        # residual remains; no fastener is double-counted.
        fastener_mass = sum(
            float(r["planning_candidate_mass_kg"])
            for r in members if r["category"] == "LOCATED JOINT FASTENER CAD DENSITY SCREEN"
        )
        non_fastener_planning = planning - fastener_mass
        contingency_before_fasteners = non_fastener_planning * 0.08
        contingency = max(0.0, contingency_before_fasteners - fastener_mass)
        dynamic_mass = planning + contingency
        residual = contingency
        weighted = [0.0, 0.0, 0.0]
        for row in members:
            mass = float(row["planning_candidate_mass_kg"])
            for i, key in enumerate(("placement_x_m", "placement_y_m", "placement_z_m")):
                weighted[i] += mass * float(row[key])
        for i in range(3):
            weighted[i] += residual * float(base["center"][i])
        center = tuple(weighted[i] / dynamic_mass for i in range(3)) if dynamic_mass else tuple(base["center"])
        delta = allocation - planning
        link_rows.append({
            "dynamic_link": link,
            "assembly_group": base["group"],
            "baseline_allocation_kg": f"{allocation:.9f}",
            "identified_minimum_candidate_kg": f"{minimum:.9f}",
            "identified_planning_candidate_kg": f"{planning:.9f}",
            "identified_maximum_candidate_kg": f"{maximum:.9f}",
            "allocation_minus_planning_kg": f"{delta:.9f}",
            "explicit_joint_fastener_candidate_kg": f"{fastener_mass:.9f}",
            "integration_contingency_before_fastener_allocation_kg": f"{contingency_before_fasteners:.9f}",
            "integration_contingency_kg": f"{contingency:.9f}",
            "reconciled_dynamics_mass_kg": f"{dynamic_mass:.9f}",
            "reconciled_com_x_m": f"{center[0]:.9f}",
            "reconciled_com_y_m": f"{center[1]:.9f}",
            "reconciled_com_z_m": f"{center[2]:.9f}",
            "identified_item_count": len(members),
            "status": "EXPLICIT ITEMS INCLUDING LOCATED FASTENERS PLUS RESIDUAL OF FORMER 8% INTEGRATION CONTINGENCY; NO FASTENER DOUBLE COUNT",
            "warning": WARNING,
        })
        dynamics_rows.append({
            **base,
            "mass": dynamic_mass,
            "center": center,
            # Mass reconciliation may move the planning inertial/COM within a
            # link, but it must never move that link's collision or visual
            # envelope.  Preserve the canonical body geometry independently.
            # Preserve the authoritative physical geometry datum independently
            # of the reconciled inertial COM.  Most links use the historical
            # center, while the shortened torso shell is intentionally offset
            # upward to maintain its hip-yaw service gap.
            "geometry_center": base.get("geometry_center", base["center"]),
        })

    category_totals = Counter()
    min_total = planning_total = max_total = 0.0
    for item in items:
        m0 = float(item["minimum_candidate_mass_kg"])
        mp = float(item["planning_candidate_mass_kg"])
        m1 = float(item["maximum_candidate_mass_kg"])
        category_totals[item["category"]] += mp
        min_total += m0
        planning_total += mp
        max_total += m1
    dynamic_total = sum(float(r["reconciled_dynamics_mass_kg"]) for r in link_rows)
    com = tuple(sum(r["mass"] * r["center"][i] for r in dynamics_rows) / dynamic_total for i in range(3))
    summary = {
        "identifier": IDENTIFIER,
        "item_count": len(items),
        "actuator_count": sum(1 for r in items if r["category"] == "MANUFACTURER PUBLISHED ACTUATOR MASS"),
        "fabrication_part_count": sum(1 for r in items if r["category"] == "FABRICATION CAD DENSITY SCREEN"),
        "joint_hardware_part_count": sum(1 for r in items if r["category"] == "JOINT HARDWARE CAD DENSITY SCREEN"),
        "located_joint_fastener_count": sum(1 for r in items if r["category"] == "LOCATED JOINT FASTENER CAD DENSITY SCREEN"),
        "transmission_belt_count": sum(1 for r in items if r["category"] == "MANUFACTURER PUBLISHED TRANSMISSION MASS"),
        "installed_equipment_item_count": sum(1 for r in items if r["category"] == "INSTALLED EQUIPMENT / HARNESS PLANNING MASS"),
        "minimum_identified_candidate_mass_kg": round(min_total, 9),
        "planning_identified_candidate_mass_kg": round(planning_total, 9),
        "maximum_identified_candidate_mass_kg": round(max_total, 9),
        "fabrication_cad_density_screen_kg": round(category_totals["FABRICATION CAD DENSITY SCREEN"], 9),
        "actuator_published_mass_planning_kg": round(category_totals["MANUFACTURER PUBLISHED ACTUATOR MASS"], 9),
        "joint_hardware_gross_density_screen_kg": round(category_totals["JOINT HARDWARE CAD DENSITY SCREEN"], 9),
        "located_joint_fastener_planning_mass_kg": round(category_totals["LOCATED JOINT FASTENER CAD DENSITY SCREEN"], 9),
        "transmission_belt_published_mass_kg": round(category_totals["MANUFACTURER PUBLISHED TRANSMISSION MASS"], 9),
        "installed_equipment_harness_planning_mass_kg": round(category_totals["INSTALLED EQUIPMENT / HARNESS PLANNING MASS"], 9),
        "prior_allocation_mass_kg": round(sum(r["mass"] for r in system.link_rows()), 9),
        "reconciled_dynamics_planning_mass_kg": round(dynamic_total, 9),
        "reconciled_dynamics_neutral_com_m": [round(v, 9) for v in com],
        "program_mass_target_kg": PRODUCT_MASS_TARGET_KG,
        "program_maximum_mass_kg": PRODUCT_MASS_HARD_LIMIT_KG,
        "planning_margin_to_product_target_kg": round(PRODUCT_MASS_TARGET_KG - dynamic_total, 9),
        "planning_margin_to_program_maximum_kg": round(PRODUCT_MASS_HARD_LIMIT_KG - dynamic_total, 9),
        "integration_contingency_before_fastener_allocation_kg": round(sum(float(r["integration_contingency_before_fastener_allocation_kg"]) for r in link_rows), 9),
        "remaining_integration_contingency_kg": round(sum(float(r["integration_contingency_kg"]) for r in link_rows), 9),
        "program_mass_target_status": "WITHIN 10 KG HARD LIMIT IN PLANNING MODEL; 8 KG TARGET AND PHYSICAL MASS CLOSURE OPEN" if dynamic_total <= PRODUCT_MASS_HARD_LIMIT_KG else "EXCEEDS 10 KG HARD LIMIT",
        "unmodeled_or_unselected": [
            "exact battery BMS/PCM, cell monitor, connector, service disconnect, precharge, containment, retention and offboard charger hardware",
            "exact selected controller, power, protection, sensor, audio, cooling and networking hardware",
            "received harness, connector, strain-relief, fastener/insert, sole, pad and restraint masses",
            "manufacturing features and mass changes after overlap removal, DFM and structural redesign",
        ],
        "model_limit": "Gross candidate-volume and located-equipment planning screen with no overlap deduction; dynamics include 156 explicit joint-fastener candidates plus the unused residual of the former 8% integration contingency. Not an as-built or released mass property.",
        "authority": {"procurement": False, "fabrication": False, "powered_test": False, "motion": False, "energization": False},
        "warning": WARNING,
    }
    return link_rows, dynamics_rows, summary


def write_mass_properties(dynamics_rows: list[dict], summary: dict, filename: str = "mass-properties-budget.csv") -> None:
    total_mass = sum(row["mass"] for row in dynamics_rows)
    com = tuple(sum(row["mass"] * row["center"][i] for row in dynamics_rows) / total_mass for i in range(3))
    out = []
    total_inertia = [0.0, 0.0, 0.0]
    for row in dynamics_rows:
        local = system.inertia_box(row["mass"], row["size"])
        dx, dy, dz = (row["center"][i] - com[i] for i in range(3))
        combined = (
            local[0] + row["mass"] * (dy * dy + dz * dz),
            local[1] + row["mass"] * (dx * dx + dz * dz),
            local[2] + row["mass"] * (dx * dx + dy * dy),
        )
        total_inertia = [total_inertia[i] + combined[i] for i in range(3)]
        out.append({
            "link": row["link"], "assembly_group": row["group"], "allocated_mass_kg": f"{row['mass']:.6f}",
            "neutral_com_x_m": f"{row['center'][0]:.6f}", "neutral_com_y_m": f"{row['center'][1]:.6f}", "neutral_com_z_m": f"{row['center'][2]:.6f}",
            "local_ixx_kg_m2": f"{local[0]:.9f}", "local_iyy_kg_m2": f"{local[1]:.9f}", "local_izz_kg_m2": f"{local[2]:.9f}",
            "status": "P0.1 RECONCILED PLANNING INERTIAL - BOX APPROXIMATION; PHYSICAL IDENTIFICATION OPEN",
        })
    out.append({
        "link": "TOTAL", "assembly_group": "whole robot", "allocated_mass_kg": f"{total_mass:.6f}",
        "neutral_com_x_m": f"{com[0]:.6f}", "neutral_com_y_m": f"{com[1]:.6f}", "neutral_com_z_m": f"{com[2]:.6f}",
        "local_ixx_kg_m2": f"{total_inertia[0]:.9f}", "local_iyy_kg_m2": f"{total_inertia[1]:.9f}", "local_izz_kg_m2": f"{total_inertia[2]:.9f}",
        "status": "P0.1 RECONCILED PLANNING MODEL - NOT AS-BUILT CAD/SCALE/IDENTIFICATION",
    })
    write_csv(OUT / filename, out)
    summary["reconciled_box_model_inertia_kg_m2"] = [round(v, 9) for v in total_inertia]


def write_configuration_register(summary: dict, tether_summary: dict) -> None:
    excluded_mass = sum(
        float(row["planning_candidate_mass_kg"])
        for row in csv.DictReader((OUT / "mass-item-reconciliation.csv").open(encoding="utf-8"))
        if row["item_id"] in ONBOARD_ENERGY_ENVELOPE_IDS
    )
    rows = [
        {
            "configuration_id": "HR30-TETHER-FIRST-P0.1",
            "program_role": "ACTIVE CONTROLLED DEVELOPMENT BASELINE",
            "included_energy_hardware": "rear tether inlet and robot distribution; no onboard pack/cassette/protection",
            "excluded_item_ids": " | ".join(sorted(ONBOARD_ENERGY_ENVELOPE_IDS)),
            "excluded_identified_mass_kg": f"{excluded_mass:.9f}",
            "planning_dynamics_mass_kg": f"{tether_summary['reconciled_dynamics_planning_mass_kg']:.9f}",
            "neutral_com_x_m": f"{tether_summary['reconciled_dynamics_neutral_com_m'][0]:.9f}",
            "neutral_com_y_m": f"{tether_summary['reconciled_dynamics_neutral_com_m'][1]:.9f}",
            "neutral_com_z_m": f"{tether_summary['reconciled_dynamics_neutral_com_m'][2]:.9f}",
            "margin_to_10kg_hard_limit_kg": f"{tether_summary['planning_margin_to_program_maximum_kg']:.9f}",
            "dynamics_artifacts": "hr30_tether.urdf | hr30_tether.xml | mass-properties-budget-tether.csv | link-mass-reconciliation-tether.csv",
            "selection_state": "ACTIVE P0.1 DEVELOPMENT CONFIGURATION; PHYSICAL MASS/COM/INERTIA AND TETHER DYNAMICS UNVALIDATED",
            "authority": "NO PROCUREMENT, FABRICATION, POWERED TEST, MOTION OR ENERGIZATION AUTHORITY",
        },
        {
            "configuration_id": "HR30-ONBOARD-ENVELOPE-P0.1",
            "program_role": "PACKAGING AND MASS ENVELOPE ONLY",
            "included_energy_hardware": "rejected Grepow/Tattu direct-source envelope plus candidate cassette and unselected protection allowance",
            "excluded_item_ids": "NONE",
            "excluded_identified_mass_kg": "0.000000000",
            "planning_dynamics_mass_kg": f"{summary['reconciled_dynamics_planning_mass_kg']:.9f}",
            "neutral_com_x_m": f"{summary['reconciled_dynamics_neutral_com_m'][0]:.9f}",
            "neutral_com_y_m": f"{summary['reconciled_dynamics_neutral_com_m'][1]:.9f}",
            "neutral_com_z_m": f"{summary['reconciled_dynamics_neutral_com_m'][2]:.9f}",
            "margin_to_10kg_hard_limit_kg": f"{summary['planning_margin_to_program_maximum_kg']:.9f}",
            "dynamics_artifacts": "hr30.urdf | hr30.xml | hr30_onboard_envelope.urdf | hr30_onboard_envelope.xml | mass-properties-budget.csv | link-mass-reconciliation.csv",
            "selection_state": "NOT AN ACTIVE POWER CONFIGURATION; DIRECT 4S SOURCE REJECTED; NEW ONBOARD ENERGY ARCHITECTURE REQUIRED",
            "authority": "NO PROCUREMENT, FABRICATION, POWERED TEST, MOTION OR ENERGIZATION AUTHORITY",
        },
    ]
    write_csv(OUT / "mass-configuration-register.csv", rows)
    summary.update({
        "active_development_configuration": "HR30-TETHER-FIRST-P0.1",
        "active_tether_dynamics_planning_mass_kg": tether_summary["reconciled_dynamics_planning_mass_kg"],
        "active_tether_neutral_com_m": tether_summary["reconciled_dynamics_neutral_com_m"],
        "active_tether_margin_to_program_maximum_kg": tether_summary["planning_margin_to_program_maximum_kg"],
        "excluded_onboard_envelope_identified_mass_kg": round(excluded_mass, 9),
        "onboard_envelope_configuration": "HR30-ONBOARD-ENVELOPE-P0.1",
        "onboard_envelope_dynamics_planning_mass_kg": summary["reconciled_dynamics_planning_mass_kg"],
        "onboard_envelope_neutral_com_m": summary["reconciled_dynamics_neutral_com_m"],
        "onboard_envelope_margin_to_program_maximum_kg": summary["planning_margin_to_program_maximum_kg"],
        "configuration_mass_separation_present": True,
    })


def write_allocation_register(dynamics_rows: list[dict], summary: dict) -> None:
    masses = {row["link"]: row["mass"] for row in dynamics_rows}
    head_neck = masses["head"] + masses["neck_pan_link"]
    torso = masses["torso"]
    pelvis = masses["base_link"]
    arms = sum(mass for link, mass in masses.items() if any(token in link for token in ("shoulder", "upper_arm", "forearm", "hand", "gripper")))
    legs = sum(mass for link, mass in masses.items() if any(token in link for token in ("hip_", "thigh", "shin", "ankle_", "foot")))
    total = sum(masses.values())

    def row(assembly: str, target: float, maximum: float, value: float) -> dict:
        return {
            "assembly": assembly, "target_kg": f"{target:.3f}", "maximum_kg": f"{maximum:.3f}",
            "cad_mass_kg": f"P0.1 RECONCILED PLANNING {value:.3f}",
            "status": "OVER MAXIMUM - REDESIGN/REALLOCATION REQUIRED" if value > maximum else "WITHIN MAXIMUM ONLY FOR CURRENT INCOMPLETE PLANNING MODEL",
        }

    rows = [
        row("head and neck", 0.55, 0.65, head_neck),
        row("chest compute and waist", 2.10, 2.40, torso),
        row("two arms and hands", 1.70, 1.95, arms),
        row("pelvis power and restraint structure", 1.60, 1.85, pelvis),
        row("two legs and feet", 4.70, 5.25, legs),
        {
            "assembly": "integration contingency within link totals", "target_kg": "0.000", "maximum_kg": "0.900",
            "cad_mass_kg": f"RESIDUAL {summary['remaining_integration_contingency_kg']:.3f} AFTER {summary['located_joint_fastener_planning_mass_kg']:.3f} KG EXPLICIT JOINT FASTENERS",
            "status": "FORMER 8% NON-FASTENER RESERVE NOW PARTLY ALLOCATED TO LOCATED SCREW CANDIDATES; RECEIVED MASSES REMAIN OPEN",
        },
        row("TOTAL", PRODUCT_MASS_TARGET_KG, PRODUCT_MASS_HARD_LIMIT_KG, total),
    ]
    write_csv(OUT / "mass-allocation-register.csv", rows)


def write_lightweight_register(summary: dict) -> None:
    rows = [
        {
            "decision_id": "HR30-LW-001", "affected_system": "torso frame",
            "baseline_candidate": "solid 18 x 18 mm rail envelopes",
            "lightweight_candidate": "18 x 18 x 2 mm hollow rail envelopes; outer interfaces retained",
            "mass_effect": "included in fabrication subtotal", "engineering_hold": "exact extrusion, local inserts, buckling, joint loads and received section open",
        },
        {
            "decision_id": "HR30-LW-002", "affected_system": "limbs, pelvis and feet",
            "baseline_candidate": "solid plate and link envelopes",
            "lightweight_candidate": "closed-perimeter windowed plates and longitudinally slotted paired arm links",
            "mass_effect": "included in fabrication subtotal", "engineering_hold": "stress concentration, fatigue, fasteners, edge finish, DFM and proof loads open",
        },
        {
            "decision_id": "HR30-LW-003", "affected_system": "covers",
            "baseline_candidate": "2.4-3.0 mm shells and panels",
            "lightweight_candidate": "1.2 mm body/limb panels with unchanged interfaces; detailed hand parts retained",
            "mass_effect": "included in fabrication subtotal", "engineering_hold": "material/process, ribs, vents, retention, impact, pinch edges and print qualification open",
        },
        {
            "decision_id": "HR30-LW-004", "affected_system": "joint shafts",
            "baseline_candidate": "solid steel density-screen shafts",
            "lightweight_candidate": "62%-diameter through-bored 7075-T6/T651 aluminum density-screen shafts",
            "mass_effect": "included in joint-hardware subtotal", "engineering_hold": "bearing seats, hardcoat/sleeves, wall stress, fatigue, fretting, retention and material selection open",
        },
        {
            "decision_id": "HR30-LW-005", "affected_system": "joint support",
            "baseline_candidate": "two external bearing carriers on every axis",
            "lightweight_candidate": "actuator internal support plus one external carrier on direct axes; two external carriers retained on remote/reduced outputs",
            "mass_effect": "22 redundant direct-axis carrier solids removed", "engineering_hold": "actuator internal-load allowance, moment path, bearing life, stiffness and received fit open",
        },
        {
            "decision_id": "HR30-LW-006", "affected_system": "carrier plates and pulleys",
            "baseline_candidate": "solid four-hole slabs and annular pulley discs",
            "lightweight_candidate": "closed carrier frames with cross webs and spoked rim/hub pulleys",
            "mass_effect": "included in joint-hardware subtotal", "engineering_hold": "web load path, belt tooth system, flange, balance, guard, DFM and proof testing open",
        },
        {
            "decision_id": "HR30-LW-007", "affected_system": "all external joint bearings",
            "baseline_candidate": "principal-dimension annulus treated as solid bearing steel",
            "lightweight_candidate": "seven standard NSK/SKF catalogue candidates; 6901 leg and 6803 waist candidates reduce distal hardware mass",
            "mass_effect": "published catalogue mass replaces gross annulus density screen", "engineering_hold": "load direction, life, suffix, lubrication, fits, retention and received identity open",
        },
        {
            "decision_id": "HR30-LW-008", "affected_system": "shoulder roll, wrists and ankles",
            "baseline_candidate": "165 g XM540 shoulder-pitch, 82 g XM430 shoulder-roll/elbows, 23 g XC330 wrists and 82 g XM430 ankles",
            "lightweight_candidate": "82 g XM430 shoulder-roll, 23 g XC330 wrists and 82 g XM430 ankles with 2.0:1/2.5:1 reductions",
            "mass_effect": "published actuator masses included in whole-body subtotal", "engineering_hold": "continuous duty, belt capacity, contact loads, thermal behavior and physical correlation open",
        },
        {
            "decision_id": "HR30-LW-009", "affected_system": "leg transmissions",
            "baseline_candidate": "belt-path reference volumes with no carried belt mass",
            "lightweight_candidate": "ten Gates 5MGT3 15 mm belt candidates carried at published catalogue mass",
            "mass_effect": f"adds {summary['transmission_belt_published_mass_kg']:.3f} kg of previously omitted transmission mass", "engineering_hold": "pulley capacity, custom manufacture, tension, alignment, guard, life and received mass open",
        },
        {
            "decision_id": "HR30-LW-TOTAL", "affected_system": "whole robot identified candidate",
            "baseline_candidate": f"commit {BASELINE_COMMIT}: {BASELINE_MASS['identified']:.6f} kg gross identified / {BASELINE_MASS['dynamics']:.6f} kg conservative dynamics",
            "lightweight_candidate": f"current: {summary['planning_identified_candidate_mass_kg']:.6f} kg gross identified / {summary['reconciled_dynamics_planning_mass_kg']:.6f} kg conservative dynamics",
            "mass_effect": f"gross identified reduction {BASELINE_MASS['identified'] - summary['planning_identified_candidate_mass_kg']:.6f} kg; dynamics reduction {BASELINE_MASS['dynamics'] - summary['reconciled_dynamics_planning_mass_kg']:.6f} kg",
            "engineering_hold": "active tether-first candidate must remain at or below the authoritative 10 kg hard limit; the 8 kg target, received mass closure and every physical validation remain open",
        },
    ]
    for row in rows:
        row["decision_state"] = "PRELIMINARY WHOLE-BODY LIGHTWEIGHT ARCHITECTURE CANDIDATE"
        row["authority"] = "NO PROCUREMENT, FABRICATION, POWERED TEST, MOTION OR ENERGIZATION AUTHORITY"
    write_csv(OUT / "lightweight-architecture-register.csv", rows)


def update_docs(summary: dict) -> None:
    report = f"""# HR-30 whole-body mass reconciliation P0.1

**{WARNING}**

The former 9.63 kg value was an allocation, not a physical mass model. This pass inventories {summary['fabrication_part_count']} materialized fabrication-CAD parts, {summary['actuator_count']} actuators, {summary['joint_hardware_part_count']} joint-hardware candidate solids, {summary['located_joint_fastener_count']} located joint-fastener candidates, {summary['transmission_belt_count']} catalogue belt candidates and {summary['installed_equipment_item_count']} located equipment/harness/contact items. The complete packaging inventory is **{summary['planning_identified_candidate_mass_kg']:.3f} kg** and includes the exact published 1.057 kg rejected-pack envelope plus cassette and protection allowances. Those three items total **{summary['excluded_onboard_envelope_identified_mass_kg']:.3f} kg** and are not installed in the active tether-first development configuration.

Relative to commit `{BASELINE_COMMIT}`, the lightweight topology reduces the gross identified candidate subtotal by **{BASELINE_MASS['identified'] - summary['planning_identified_candidate_mass_kg']:.3f} kg**. The body retains all 25 axes, complete limbs and hands while using hollow torso rails, windowed and slotted load-path plates, thinner service covers, hollow aluminum shaft screens, topology-lightened carrier frames and pulleys, and actuator-plus-one-external-bearing support on direct axes. Those changes are geometry candidates, not strength or bearing-life evidence.

The package now exposes two non-interchangeable dynamics configurations. `HR30-TETHER-FIRST-P0.1` is the active controlled-development baseline at **{summary['active_tether_dynamics_planning_mass_kg']:.3f} kg**, neutral COM **({summary['active_tether_neutral_com_m'][0]:.3f}, {summary['active_tether_neutral_com_m'][1]:.3f}, {summary['active_tether_neutral_com_m'][2]:.3f}) m**, and **{summary['active_tether_margin_to_program_maximum_kg']:.3f} kg** planning margin to the authoritative 10 kg hard limit. The 8 kg product target remains missed. `HR30-ONBOARD-ENVELOPE-P0.1` remains a packaging-only case at **{summary['onboard_envelope_dynamics_planning_mass_kg']:.3f} kg**, which exceeds the 10 kg hard limit by **{-summary['onboard_envelope_margin_to_program_maximum_kg']:.3f} kg**. Its direct 4S source is rejected and it is not an active power configuration. Both models retain the explicit per-link subtotal and residual integration contingency without double-counting the {summary['located_joint_fastener_planning_mass_kg']:.3f} kg of located screw candidates. Exact selections, received masses and dynamic walking proof remain open.

The actuator planning subtotal uses published masses from current official ROBOTIS e-Manual pages checked {ACCESSED}. Both elbows and both shoulder-roll axes use the 82 g XM430 candidate, both wrists use the 23 g XC330 candidate, and all four ankles use the 82 g XM430 candidate behind explicit reductions. The ten Gates belt candidates add {summary['transmission_belt_published_mass_kg']:.3f} kg at current published catalogue mass. None of this is continuous-duty, dynamic, belt-capacity, thermal or physical validation. CAD actuator placement is the geometric centroid of the SHA-bound manufacturer packaging body, not a published center of gravity.

Bearing masses now use seven standard catalogue candidates from current NSK/SKF primary pages rather than treating each principal-dimension annulus as solid steel. The 12 x 24 x 6 mm NSK 6901 is the leg output candidate and the 17 x 26 x 5 mm NSK 6803 is the waist candidate. Those catalogue masses improve the planning model but do not select a bearing application or prove load direction, life, suffix, lubrication, fit, retention or received identity.

Fabrication and joint-hardware values are volume-times-density screens; equipment values are located as-installed allowances, with current primary manufacturer evidence recorded where available. Candidate solids may interpenetrate and manufacturing redesign will change them; no overlap deduction is taken. The URDF and MJCF inertias remain box approximations for development simulation. Physical mass, COM and inertia identification, exact selections, structural closure, gait validation and qualified review remain mandatory.
"""
    (OUT / "mass-reconciliation.md").write_text(report, encoding="utf-8", newline="\n")

    readme = (OUT / "README.md").read_text(encoding="utf-8")
    readme = readme.replace(
        "The CAD density screen is 2.627 kg for frame parts and 0.979 kg for removable covers. These numbers are geometry/material-assumption screens only; the main 9.63 kg whole-robot allocation remains authoritative until exact parts and received masses close.",
        "The CAD density screen is 2.627 kg for frame parts and 0.979 kg for removable covers. These numbers are geometry/material-assumption screens only and are now carried into the whole-body mass reconciliation; exact parts and received masses remain open.",
    )
    readme = readme.replace(
        "a 9.63 kg allocation model with neutral COM/inertia",
        "a historical 9.63 kg allocation baseline now superseded by the reconciled planning inertials",
    )
    mass_section = f"""
## Whole-body mass reconciliation

The 9.63 kg allocation is no longer presented as the current dynamics mass. A reproducible reconciliation now combines {summary['fabrication_part_count']} fabrication-CAD parts, {summary['actuator_count']} published actuator masses, {summary['joint_hardware_part_count']} joint-hardware candidate parts (including catalogue bearing masses), {summary['located_joint_fastener_count']} located screw candidates, {summary['transmission_belt_count']} catalogue belt candidates and {summary['installed_equipment_item_count']} located equipment/harness/contact items. The active tether-first dynamics model is {summary['active_tether_dynamics_planning_mass_kg']:.3f} kg with neutral COM Z={summary['active_tether_neutral_com_m'][2]:.3f} m and {summary['active_tether_margin_to_program_maximum_kg']:.3f} kg planning margin to the 10 kg hard limit. The separate onboard-envelope model is {summary['onboard_envelope_dynamics_planning_mass_kg']:.3f} kg and includes {summary['excluded_onboard_envelope_identified_mass_kg']:.3f} kg for the rejected direct-source pack envelope, cassette and unselected protection allowance. It exceeds the product hard limit and is packaging evidence, not an installed energy configuration. Exact protection, received masses and physical properties remain open.
""".strip()
    readme, mass_count = re.subn(
        r"## Whole-body mass reconciliation\n.*?(?=\n## |\Z)",
        mass_section,
        readme,
        count=1,
        flags=re.S,
    )
    if mass_count == 0:
        marker = "\n## Whole-body joint-load architecture\n"
        if marker in readme:
            readme = readme.replace(marker, "\n" + mass_section + "\n" + marker, 1)
        else:
            readme = readme.rstrip() + "\n\n" + mass_section + "\n"
    (OUT / "README.md").write_text(readme.rstrip() + "\n", encoding="utf-8", newline="\n")

    walking_path = OUT / "walking-development-architecture.md"
    walking = walking_path.read_text(encoding="utf-8")
    old = "The neutral estimated mass is 9.63 kg with estimated COM Z=0.338 m; these are allocation-model values, not measured properties."
    new = f"The active tether-first planning dynamics mass is {summary['active_tether_dynamics_planning_mass_kg']:.3f} kg with neutral COM Z={summary['active_tether_neutral_com_m'][2]:.3f} m; these are candidate-volume and allocation values, not measured properties. The separate {summary['onboard_envelope_dynamics_planning_mass_kg']:.3f} kg onboard-envelope case retains rejected-pack packaging evidence and is not an active power configuration."
    if old in walking:
        walking = walking.replace(old, new)
    elif new in walking:
        pass
    else:
        walking, count = re.subn(
            r"The (?:(?:reconciled planning|onboard-energy planning|active tether-first planning) dynamics mass is [^.]+\.[0-9]{3} kg with neutral COM Z=[0-9.]+ m|neutral estimated mass is 9\.63 kg with estimated COM Z=[0-9.]+ m);[^\n]+",
            new,
            walking,
            count=1,
        )
        if count != 1:
            raise RuntimeError("walking mass statement drift")
    walking_path.write_text(walking, encoding="utf-8", newline="\n")

    web_path = OUT / "index.html"
    web = web_path.read_text(encoding="utf-8")
    web, link_count = re.subn(
        r'<a href="mass-properties-budget\.csv">.*?(?=<a href="power-energy-budget\.csv">)',
        '<a href="mass-properties-budget.csv">Onboard-envelope mass/COM/inertia</a> · <a href="mass-properties-budget-tether.csv">Tether-first mass/COM/inertia</a> · <a href="mass-configuration-register.csv">Mass configurations</a> · <a href="mass-reconciliation.md">Mass reconciliation</a> · <a href="mass-item-reconciliation.csv">Mass item register</a> · <a href="lightweight-architecture-register.csv">Lightweight decisions</a> · ',
        web,
        count=1,
    )
    if link_count != 1:
        raise RuntimeError("system artifact mass-link block drift")
    web, card_count = re.subn(
        r'<article class="card (?:hold|miss)"><h3>Mass and energy</h3><p>[\s\S]*?</p></article>',
        f'<article class="card hold"><h3>Mass and energy</h3><p>{summary["active_tether_dynamics_planning_mass_kg"]:.3f} kg active tether-first planning mass with {summary["active_tether_margin_to_program_maximum_kg"]:.3f} kg planning margin to the authoritative 10 kg hard limit; the 8 kg target remains missed. The separate {summary["onboard_envelope_dynamics_planning_mass_kg"]:.3f} kg onboard-envelope model exceeds the hard limit, retains a rejected pack envelope and is not an active power configuration. Physical mass, COM, inertia and energy selection remain open.</p></article>',
        web,
        count=1,
    )
    if card_count != 1:
        raise RuntimeError("system mass card drift")
    web, body_mass_count = re.subn(
        r'<article class="card (?:hold|miss)"><h3>(?:Mass is still unproven|Mass remains preliminary|10 kg target does not close|10 kg planning screen has no usable margin|Onboard design exceeds 10 kg maximum|P0.1 mass envelope closes only in the planning model|Mass configurations are now explicit)</h3><p>[\s\S]*?</p></article>',
        f'<article class="card hold"><h3>Mass configurations are now explicit</h3><p>The active tether-first model is {summary["active_tether_dynamics_planning_mass_kg"]:.3f} kg. The {summary["onboard_envelope_dynamics_planning_mass_kg"]:.3f} kg packaging case includes {summary["excluded_onboard_envelope_identified_mass_kg"]:.3f} kg for a rejected direct-source pack envelope, cassette and unselected protection allowance. Neither configuration is an as-built mass property.</p></article>',
        web,
        count=1,
    )
    if body_mass_count != 1:
        raise RuntimeError("body mass card drift")
    web_path.write_text(web, encoding="utf-8", newline="\n")

    # Keep the repository Pages entry synchronized with the authoritative
    # reconciliation instead of requiring a manual mass-card edit after every
    # whole-body geometry change.
    root_page_path = ROOT / "index.html"
    root_page = root_page_path.read_text(encoding="utf-8")
    root_page, root_mass_count = re.subn(
        r'<article class="card hold"><div class="metric">[0-9.]+ kg</div><p>(?:Whole-body planning-model mass|Active tether-first planning mass)[^<]*</p></article>',
        f'<article class="card hold"><div class="metric">{summary["active_tether_dynamics_planning_mass_kg"]:.3f} kg</div><p>Active tether-first planning mass, not measured. The separate onboard-envelope case is {summary["onboard_envelope_dynamics_planning_mass_kg"]:.3f} kg and still uses a rejected battery envelope.</p></article>',
        root_page,
        count=1,
    )
    if root_mass_count != 1:
        raise RuntimeError("repository Pages mass card drift")
    root_page_path.write_text(root_page, encoding="utf-8", newline="\n")

    status_path = OUT / "package-status.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    status.update({
        "estimated_mass_kg": summary["active_tether_dynamics_planning_mass_kg"],
        "estimated_neutral_com_m": summary["active_tether_neutral_com_m"],
        "estimated_neutral_com_z_m": summary["active_tether_neutral_com_m"][2],
        "mass_reconciliation_present": True,
        "whole_body_lightweight_architecture_present": True,
        "identified_candidate_mass_kg": summary["planning_identified_candidate_mass_kg"],
        "mass_margin_to_10kg_kg": summary["active_tether_margin_to_program_maximum_kg"],
        "mass_margin_to_p01_maximum_kg": summary["active_tether_margin_to_program_maximum_kg"],
        "module_interface_mass_reconciliation_kg": summary["active_tether_dynamics_planning_mass_kg"],
        "active_development_mass_configuration": summary["active_development_configuration"],
        "active_tether_development_mass_kg": summary["active_tether_dynamics_planning_mass_kg"],
        "active_tether_neutral_com_m": summary["active_tether_neutral_com_m"],
        "active_tether_mass_margin_to_p01_maximum_kg": summary["active_tether_margin_to_program_maximum_kg"],
        "onboard_energy_envelope_mass_kg": summary["onboard_envelope_dynamics_planning_mass_kg"],
        "onboard_energy_envelope_active": False,
        "mass_configuration_separation_present": True,
        "mass_budget_closed": summary["active_tether_dynamics_planning_mass_kg"] <= PRODUCT_MASS_HARD_LIMIT_KG,
        "mass_budget_basis": "ACTIVE TETHER-FIRST CONSERVATIVE PLANNING MODEL ONLY; 8 KG TARGET AND PHYSICAL MASS/COM/INERTIA VALIDATION OPEN",
        "mass_com_inertia_physically_validated": False,
    })
    status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")

    holds_path = OUT / "open-holds.csv"
    holds = list(csv.DictReader(holds_path.open(encoding="utf-8")))
    arm_mass = next(
        float(row["cad_mass_kg"].split()[-1])
        for row in csv.DictReader((OUT / "mass-allocation-register.csv").open(encoding="utf-8"))
        if row["assembly"] == "two arms and hands"
    )
    for row in holds:
        if row["hold_id"] == "HR30-P01-H02":
            row["unresolved_item"] = (
                f"The current bilateral arms-and-hands planning mass is {arm_mass:.3f} kg against the 1.950 kg assembly maximum. "
                "The former arm-mass blocker is closed at candidate-planning level only; received mass and arm structural/dynamic proof remain open under H09/H10."
            )
            row["state"] = "RESOLVED AT CANDIDATE-PLANNING LEVEL - PHYSICAL VALIDATION OPEN"
            row["release_effect"] = "NO LONGER A DESIGN-MASS BLOCKER; H09/H10 STILL BLOCK FABRICATION, MOTION AND ENERGIZATION"
        if row["hold_id"] == "HR30-P01-H09":
            row["unresolved_item"] = (
                f"The active tether-first planning model is {summary['active_tether_dynamics_planning_mass_kg']:.3f} kg, while the separate onboard-envelope case is {summary['onboard_envelope_dynamics_planning_mass_kg']:.3f} kg. "
                f"The {summary['excluded_onboard_envelope_identified_mass_kg']:.3f} kg difference is a rejected direct-source pack envelope, cassette and unselected protection allowance, not installed development hardware. Exact onboard energy architecture, overlap removal, received mass/COM and physical inertia identification remain open."
            )
    write_csv(holds_path, holds)


def generate_into_package() -> dict:
    items, sources = build_items()
    link_rows, dynamics_rows, summary = reconcile(items)
    tether_items = [row for row in items if row["item_id"] not in ONBOARD_ENERGY_ENVELOPE_IDS]
    tether_link_rows, tether_dynamics_rows, tether_summary = reconcile(tether_items)
    write_csv(OUT / "actuator-mass-source-register.csv", sources)
    write_csv(OUT / "mass-item-reconciliation.csv", items)
    write_csv(OUT / "link-mass-reconciliation.csv", link_rows)
    write_csv(OUT / "link-mass-reconciliation-tether.csv", tether_link_rows)
    write_lightweight_register(summary)
    write_mass_properties(dynamics_rows, summary)
    write_mass_properties(tether_dynamics_rows, tether_summary, "mass-properties-budget-tether.csv")
    write_configuration_register(summary, tether_summary)
    write_allocation_register(tether_dynamics_rows, tether_summary)

    # Preserve the historical default dynamics artifacts as the complete
    # onboard-envelope planning case, while adding an explicit active
    # tether-first model.  This avoids silently dropping packaging evidence or
    # pretending the rejected direct-4S source is installed in the development
    # robot.
    system.write_urdf(dynamics_rows, system.joint_rows())
    system.write_mjcf(dynamics_rows, system.joint_rows())
    shutil.copy2(OUT / "hr30.urdf", OUT / "hr30_onboard_envelope.urdf")
    shutil.copy2(OUT / "hr30.xml", OUT / "hr30_onboard_envelope.xml")
    system.write_urdf(tether_dynamics_rows, system.joint_rows())
    system.write_mjcf(tether_dynamics_rows, system.joint_rows())
    shutil.copy2(OUT / "hr30.urdf", OUT / "hr30_tether.urdf")
    shutil.copy2(OUT / "hr30.xml", OUT / "hr30_tether.xml")
    shutil.copy2(OUT / "hr30_onboard_envelope.urdf", OUT / "hr30.urdf")
    shutil.copy2(OUT / "hr30_onboard_envelope.xml", OUT / "hr30.xml")
    update_docs(summary)
    (OUT / "mass-reconciliation-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    shutil.copy2(Path(__file__), OUT / "mass-reconciliation-source.py")
    return summary


def main() -> int:
    summary = generate_into_package()
    system.refresh_manifest_and_release()
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
