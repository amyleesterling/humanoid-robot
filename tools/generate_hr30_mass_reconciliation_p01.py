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
import generate_hr30_installed_equipment_p01 as equipment
import generate_hr30_fabrication_architecture_p01 as fabrication
import generate_hr30_system_package_p01 as system


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "hr30" / "whole-body-p0.1"
IDENTIFIER = "HR-30-MASS-RECONCILIATION-P0.1"
WARNING = body.WARNING
ACCESSED = "2026-08-14"
BASELINE_COMMIT = "dfb9a7d"
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
    if axis_id.startswith("HEAD_") or "GRIPPER" in axis_id:
        name = "ROBOTIS XC330-T288-T"
        mass = ACTUATOR_SOURCES[name]["mass_kg"]
        return name, mass, mass, mass, "candidate family; exact suffix/rail/interface selection remains open"
    if any(token in axis_id for token in ("HIP_", "KNEE_", "ANKLE_")):
        name = "ROBOTIS XH540-W270-R"
        mass = ACTUATOR_SOURCES[name]["mass_kg"]
        return name, mass, mass, mass, "evaluation candidate; continuous-duty and walking suitability unproved"
    if "WRIST_ROTATION" in axis_id:
        name = "ROBOTIS XM430-W350-R"
        mass = ACTUATOR_SOURCES[name]["mass_kg"]
        return name, mass, mass, mass, "candidate; exact suffix/interface selection remains open"
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

    body_components, _, _, _ = body.build()
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
        # Apply a visible 8% integration contingency instead; this covers small
        # adhesives, labels, local brackets and selection drift, but is not
        # physical closure or a substitute for received masses.
        contingency = planning * 0.08
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
            "integration_contingency_kg": f"{contingency:.9f}",
            "reconciled_dynamics_mass_kg": f"{dynamic_mass:.9f}",
            "reconciled_com_x_m": f"{center[0]:.9f}",
            "reconciled_com_y_m": f"{center[1]:.9f}",
            "reconciled_com_z_m": f"{center[2]:.9f}",
            "identified_item_count": len(members),
            "status": "EXPLICIT ITEMS PLUS 8% INTEGRATION CONTINGENCY; HISTORICAL ALLOCATION RETAINED FOR COMPARISON ONLY",
            "warning": WARNING,
        })
        dynamics_rows.append({**base, "mass": dynamic_mass, "center": center})

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
        "installed_equipment_item_count": sum(1 for r in items if r["category"] == "INSTALLED EQUIPMENT / HARNESS PLANNING MASS"),
        "minimum_identified_candidate_mass_kg": round(min_total, 9),
        "planning_identified_candidate_mass_kg": round(planning_total, 9),
        "maximum_identified_candidate_mass_kg": round(max_total, 9),
        "fabrication_cad_density_screen_kg": round(category_totals["FABRICATION CAD DENSITY SCREEN"], 9),
        "actuator_published_mass_planning_kg": round(category_totals["MANUFACTURER PUBLISHED ACTUATOR MASS"], 9),
        "joint_hardware_gross_density_screen_kg": round(category_totals["JOINT HARDWARE CAD DENSITY SCREEN"], 9),
        "installed_equipment_harness_planning_mass_kg": round(category_totals["INSTALLED EQUIPMENT / HARNESS PLANNING MASS"], 9),
        "prior_allocation_mass_kg": round(sum(r["mass"] for r in system.link_rows()), 9),
        "reconciled_dynamics_planning_mass_kg": round(dynamic_total, 9),
        "reconciled_dynamics_neutral_com_m": [round(v, 9) for v in com],
        "program_maximum_mass_kg": 10.0,
        "planning_margin_to_program_maximum_kg": round(10.0 - dynamic_total, 9),
        "program_mass_target_status": "EXCEEDED" if dynamic_total > 10.0 else "NOT YET EXCEEDED BUT UNMODELED MASS REMAINS",
        "unmodeled_or_unselected": [
            "onboard battery, BMS and charger are not installed in the tether-first configuration",
            "exact selected controller, power, protection, sensor, audio, cooling and networking hardware",
            "received harness, connector, strain-relief, fastener, insert, sole, pad and restraint masses",
            "manufacturing features and mass changes after overlap removal, DFM and structural redesign",
        ],
        "model_limit": "Gross candidate-volume and located-equipment planning screen with no overlap deduction; dynamics use explicit per-link items plus 8% integration contingency. Not an as-built or released mass property.",
        "authority": {"procurement": False, "fabrication": False, "powered_test": False, "motion": False, "energization": False},
        "warning": WARNING,
    }
    return link_rows, dynamics_rows, summary


def write_mass_properties(dynamics_rows: list[dict], summary: dict) -> None:
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
    write_csv(OUT / "mass-properties-budget.csv", out)
    summary["reconciled_box_model_inertia_kg_m2"] = [round(v, 9) for v in total_inertia]


def write_allocation_register(dynamics_rows: list[dict]) -> None:
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
        row("head and neck", 0.45, 0.55, head_neck),
        row("chest compute and waist", 1.20, 1.35, torso),
        row("two arms and hands", 1.30, 1.50, arms),
        row("pelvis power and restraint structure", 1.40, 1.75, pelvis),
        row("two legs and feet", 3.40, 3.80, legs),
        {
            "assembly": "integration contingency within link totals", "target_kg": "0.000", "maximum_kg": "0.800",
            "cad_mass_kg": "8% OF EXPLICIT LINK SUBTOTALS",
            "status": "MODELED CONTINGENCY - RECEIVED MASSES AND ONBOARD-ENERGY CONFIGURATION OPEN",
        },
        row("TOTAL", 8.00, 10.00, total),
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
            "lightweight_candidate": "1.8 mm limb/palm/foot panels and 2.0 mm central/head shells",
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
            "lightweight_candidate": "five standard NSK/SKF catalogue candidates with published mass and matching shaft/envelope dimensions",
            "mass_effect": "published catalogue mass replaces gross annulus density screen", "engineering_hold": "load direction, life, suffix, lubrication, fits, retention and received identity open",
        },
        {
            "decision_id": "HR30-LW-TOTAL", "affected_system": "whole robot identified candidate",
            "baseline_candidate": f"commit {BASELINE_COMMIT}: {BASELINE_MASS['identified']:.6f} kg gross identified / {BASELINE_MASS['dynamics']:.6f} kg conservative dynamics",
            "lightweight_candidate": f"current: {summary['planning_identified_candidate_mass_kg']:.6f} kg gross identified / {summary['reconciled_dynamics_planning_mass_kg']:.6f} kg conservative dynamics",
            "mass_effect": f"gross identified reduction {BASELINE_MASS['identified'] - summary['planning_identified_candidate_mass_kg']:.6f} kg; dynamics reduction {BASELINE_MASS['dynamics'] - summary['reconciled_dynamics_planning_mass_kg']:.6f} kg",
            "engineering_hold": "10 kg tethered ceiling remains failed by conservative dynamics; equipment closure and every physical validation remain open",
        },
    ]
    for row in rows:
        row["decision_state"] = "PRELIMINARY WHOLE-BODY LIGHTWEIGHT ARCHITECTURE CANDIDATE"
        row["authority"] = "NO PROCUREMENT, FABRICATION, POWERED TEST, MOTION OR ENERGIZATION AUTHORITY"
    write_csv(OUT / "lightweight-architecture-register.csv", rows)


def update_docs(summary: dict) -> None:
    report = f"""# HR-30 whole-body mass reconciliation P0.1

**{WARNING}**

The former 9.63 kg value was an allocation, not a physical mass model. This pass inventories {summary['fabrication_part_count']} materialized fabrication-CAD parts, {summary['actuator_count']} actuators, {summary['joint_hardware_part_count']} joint-hardware candidate solids and {summary['installed_equipment_item_count']} located equipment/harness/contact items. The tether-first gross identified planning subtotal is **{summary['planning_identified_candidate_mass_kg']:.3f} kg** before the 8% integration contingency and without an onboard battery/BMS/charger.

Relative to commit `{BASELINE_COMMIT}`, the lightweight topology reduces the gross identified candidate subtotal by **{BASELINE_MASS['identified'] - summary['planning_identified_candidate_mass_kg']:.3f} kg**. The body retains all 25 axes, complete limbs and hands while using hollow torso rails, windowed and slotted load-path plates, thinner service covers, hollow aluminum shaft screens, topology-lightened carrier frames and pulleys, and actuator-plus-one-external-bearing support on direct axes. Those changes are geometry candidates, not strength or bearing-life evidence.

The dynamics model now uses the explicit per-link subtotal plus a visible 8% integration contingency instead of carrying stale historical allocations. This produces a tethered provisional dynamics mass of **{summary['reconciled_dynamics_planning_mass_kg']:.3f} kg** and neutral COM **({summary['reconciled_dynamics_neutral_com_m'][0]:.3f}, {summary['reconciled_dynamics_neutral_com_m'][1]:.3f}, {summary['reconciled_dynamics_neutral_com_m'][2]:.3f}) m**. The resulting margin to the 10 kg program maximum is **{summary['planning_margin_to_program_maximum_kg']:.3f} kg**. Exact selections, received masses and the separate onboard-energy configuration remain open.

The actuator planning subtotal uses published masses from current official ROBOTIS e-Manual pages checked {ACCESSED}. Both elbows now use the already-modelled 82 g XM430 candidate because the whole-body static-load screen retains it with margin to the published 12 V stall endpoint. This is not continuous-duty, dynamic, thermal or physical validation. CAD actuator placement is the geometric centroid of the SHA-bound manufacturer packaging body, not a published center of gravity.

Bearing masses now use five standard catalogue candidates from current NSK/SKF primary pages rather than treating each principal-dimension annulus as solid steel. Those catalogue masses improve the planning model but do not select a bearing application or prove load direction, life, suffix, lubrication, fit, retention or received identity.

Fabrication and joint-hardware values are volume-times-density screens; equipment values are located as-installed allowances, with current primary manufacturer evidence recorded where available. Candidate solids may interpenetrate and manufacturing redesign will change them; no overlap deduction is taken. The URDF and MJCF inertias remain box approximations for development simulation. Physical mass, COM and inertia identification, exact selections, structural closure, gait validation and qualified review remain mandatory.
"""
    (OUT / "mass-reconciliation.md").write_text(report, encoding="utf-8", newline="\n")

    readme = (OUT / "README.md").read_text(encoding="utf-8").split("\n\n## Whole-body mass reconciliation", 1)[0].rstrip()
    readme = readme.replace(
        "The CAD density screen is 2.627 kg for frame parts and 0.979 kg for removable covers. These numbers are geometry/material-assumption screens only; the main 9.63 kg whole-robot allocation remains authoritative until exact parts and received masses close.",
        "The CAD density screen is 2.627 kg for frame parts and 0.979 kg for removable covers. These numbers are geometry/material-assumption screens only and are now carried into the whole-body mass reconciliation; exact parts and received masses remain open.",
    )
    readme = readme.replace(
        "a 9.63 kg allocation model with neutral COM/inertia",
        "a historical 9.63 kg allocation baseline now superseded by the reconciled planning inertials",
    )
    readme += f"""

## Whole-body mass reconciliation

The 9.63 kg allocation is no longer presented as the current dynamics mass. A reproducible reconciliation now combines {summary['fabrication_part_count']} fabrication-CAD parts, {summary['actuator_count']} published actuator masses, {summary['joint_hardware_part_count']} joint-hardware candidate parts (including catalogue bearing masses) and {summary['installed_equipment_item_count']} located equipment/harness/contact items. The tether-first gross identified subtotal is {summary['planning_identified_candidate_mass_kg']:.3f} kg; the explicit per-link model plus 8% integration contingency is {summary['reconciled_dynamics_planning_mass_kg']:.3f} kg with neutral COM Z={summary['reconciled_dynamics_neutral_com_m'][2]:.3f} m. The onboard battery/BMS/charger is not installed, and exact selections/received masses remain open.
"""
    (OUT / "README.md").write_text(readme.rstrip() + "\n", encoding="utf-8", newline="\n")

    walking_path = OUT / "walking-development-architecture.md"
    walking = walking_path.read_text(encoding="utf-8")
    old = "The neutral estimated mass is 9.63 kg with estimated COM Z=0.338 m; these are allocation-model values, not measured properties."
    new = f"The reconciled planning dynamics mass is {summary['reconciled_dynamics_planning_mass_kg']:.3f} kg with neutral COM Z={summary['reconciled_dynamics_neutral_com_m'][2]:.3f} m; these are candidate-volume and allocation values, not measured properties, and major equipment mass remains open."
    if old in walking:
        walking = walking.replace(old, new)
    else:
        walking, count = re.subn(
            r"The reconciled planning dynamics mass is [^.]+\.[0-9]{3} kg with neutral COM Z=[0-9.]+ m;[^\n]+",
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
        r'<a href="mass-properties-budget\.csv">Mass/COM/inertia</a>.*?(?=<a href="power-energy-budget\.csv">)',
        '<a href="mass-properties-budget.csv">Mass/COM/inertia</a> · <a href="mass-reconciliation.md">Mass reconciliation</a> · <a href="mass-item-reconciliation.csv">Mass item register</a> · <a href="lightweight-architecture-register.csv">Lightweight decisions</a> · ',
        web,
        count=1,
    )
    if link_count != 1:
        raise RuntimeError("system artifact mass-link block drift")
    web, card_count = re.subn(
        r'<article class="card hold"><h3>Mass and energy</h3><p>[\s\S]*?</p></article>',
        f'<article class="card hold"><h3>Mass and energy</h3><p>{summary["reconciled_dynamics_planning_mass_kg"]:.3f} kg tether-first planning dynamics mass, {summary["reconciled_dynamics_neutral_com_m"][2]:.3f} m neutral COM height, 197 W operating power budget and 135 W heat-rejection budget. Located equipment is included; onboard energy, received masses and physical closure remain open.</p></article>',
        web,
        count=1,
    )
    if card_count != 1:
        raise RuntimeError("system mass card drift")
    web, body_mass_count = re.subn(
        r'<article class="card (?:hold|miss)"><h3>(?:Mass is still unproven|10 kg target does not close)</h3><p>[\s\S]*?</p></article>',
        f'<article class="card miss"><h3>10 kg target does not close</h3><p>The tether-first explicit model is {summary["planning_identified_candidate_mass_kg"]:.3f} kg before contingency and {summary["reconciled_dynamics_planning_mass_kg"]:.3f} kg with 8% integration contingency. An onboard battery is not included.</p></article>',
        web,
        count=1,
    )
    if body_mass_count != 1:
        raise RuntimeError("body mass card drift")
    web_path.write_text(web, encoding="utf-8", newline="\n")

    status_path = OUT / "package-status.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    status.update({
        "estimated_mass_kg": summary["reconciled_dynamics_planning_mass_kg"],
        "estimated_neutral_com_m": summary["reconciled_dynamics_neutral_com_m"],
        "estimated_neutral_com_z_m": summary["reconciled_dynamics_neutral_com_m"][2],
        "mass_reconciliation_present": True,
        "whole_body_lightweight_architecture_present": True,
        "identified_candidate_mass_kg": summary["planning_identified_candidate_mass_kg"],
        "mass_margin_to_10kg_kg": summary["planning_margin_to_program_maximum_kg"],
        "mass_budget_closed": False,
        "mass_com_inertia_physically_validated": False,
    })
    status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")

    holds_path = OUT / "open-holds.csv"
    holds = list(csv.DictReader(holds_path.open(encoding="utf-8")))
    for row in holds:
        if row["hold_id"] == "HR30-P01-H09":
            row["unresolved_item"] = (
                f"A gross candidate-volume reconciliation now gives {summary['reconciled_dynamics_planning_mass_kg']:.3f} kg and provisional COM, "
                "with located tether-first equipment plus integration contingency, but overlap removal, exact selections, onboard energy, received mass/COM and physical inertia identification remain open."
            )
    write_csv(holds_path, holds)


def generate_into_package() -> dict:
    items, sources = build_items()
    link_rows, dynamics_rows, summary = reconcile(items)
    write_csv(OUT / "actuator-mass-source-register.csv", sources)
    write_csv(OUT / "mass-item-reconciliation.csv", items)
    write_csv(OUT / "link-mass-reconciliation.csv", link_rows)
    write_lightweight_register(summary)
    write_mass_properties(dynamics_rows, summary)
    write_allocation_register(dynamics_rows)
    system.write_urdf(dynamics_rows, system.joint_rows())
    system.write_mjcf(dynamics_rows, system.joint_rows())
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
