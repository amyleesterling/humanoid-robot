"""Generate the HR-30 P0.1 whole-body joint-load architecture screen.

This is a transparent static architecture screen across all 25 axes.  It does
not turn published stall torque into continuous capability and does not
authorize procurement, fabrication, powered testing, motion or energization.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
import shutil
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "hr30" / "whole-body-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1"
IDENTIFIER = "HR-30-JOINT-LOAD-ARCH-P0.1"
WARNING = "PRELIMINARY - CONFIGURATION AND PACKAGING CAD ONLY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, POWERED TESTING, MOTION, OR ENERGIZATION"
G = 9.80665
PAYLOAD_EACH_HAND_KG = 0.100
DEVELOPMENT_FACTOR = 1.50
REDUCED_DRIVE_EFFICIENCY = 0.85
NARROW_ENDPOINT_RATIO = 1.50

ACTUATORS = {
    "ROBOTIS XC330-T288-T": {"mass_kg": 0.023, "stall_nm_12v": 1.0, "stall_a_12v": 0.88, "rpm_12v": 71.0, "url": "https://emanual.robotis.com/docs/en/dxl/x/xc330-t288/"},
    "ROBOTIS XM430-W350-R": {"mass_kg": 0.082, "stall_nm_12v": 4.1, "stall_a_12v": 2.3, "rpm_12v": 46.0, "url": "https://emanual.robotis.com/docs/en/dxl/x/xm430-w350/"},
    "ROBOTIS XM540-W270-R": {"mass_kg": 0.165, "stall_nm_12v": 10.6, "stall_a_12v": 4.4, "rpm_12v": 30.0, "url": "https://emanual.robotis.com/docs/en/dxl/x/xm540-w270/"},
    "ROBOTIS XH540-W270-R": {"mass_kg": 0.165, "stall_nm_12v": 9.9, "stall_a_12v": 4.9, "rpm_12v": 39.0, "url": "https://emanual.robotis.com/docs/en/dxl/x/xh540-w270/"},
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def vec(text: str) -> tuple[float, float, float]:
    return tuple(float(v) for v in text.split())


def norm(v: tuple[float, float, float]) -> float:
    return math.sqrt(sum(x * x for x in v))


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise RuntimeError(f"refusing empty CSV {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def actuator_for(axis_id: str) -> tuple[str, float, float]:
    if axis_id.startswith("HEAD_") or "GRIPPER" in axis_id:
        return "ROBOTIS XC330-T288-T", 1.0, 1.0
    if "WRIST" in axis_id or "ELBOW" in axis_id:
        return "ROBOTIS XM430-W350-R", 1.0, 1.0
    if axis_id == "WAIST_YAW" or "SHOULDER" in axis_id:
        return "ROBOTIS XM540-W270-R", 1.0, 1.0
    if "HIP_ROLL" in axis_id or "ANKLE_ROLL" in axis_id:
        return "ROBOTIS XH540-W270-R", 2.0, REDUCED_DRIVE_EFFICIENCY
    if any(token in axis_id for token in ("HIP_PITCH", "KNEE_PITCH", "ANKLE_PITCH")):
        return "ROBOTIS XH540-W270-R", 1.5, REDUCED_DRIVE_EFFICIENCY
    return "ROBOTIS XH540-W270-R", 1.0, 1.0


def parse_model() -> tuple[dict, dict, dict]:
    robot = ET.parse(OUT / "hr30.urdf").getroot()
    links = {}
    for link in robot.findall("link"):
        links[link.get("name")] = {
            "mass": float(link.find("inertial/mass").get("value")),
            "com": vec(link.find("inertial/origin").get("xyz")),
        }
    joints = {}
    children = defaultdict(list)
    for joint in robot.findall("joint"):
        row = {
            "name": joint.get("name"),
            "parent": joint.find("parent").get("link"),
            "child": joint.find("child").get("link"),
            "origin": vec(joint.find("origin").get("xyz")),
            "axis": vec(joint.find("axis").get("xyz")),
        }
        joints[row["name"]] = row
        children[row["parent"]].append(row)
    return links, joints, children


def subtree_radii(child_link: str, links: dict, children: dict) -> tuple[list[tuple[str, float, float]], dict[str, float]]:
    masses = []
    link_origin_bounds = {}

    def walk(link: str, origin_bound: float) -> None:
        link_origin_bounds[link] = origin_bound
        masses.append((link, links[link]["mass"], origin_bound + norm(links[link]["com"])))
        for joint in children.get(link, []):
            walk(joint["child"], origin_bound + norm(joint["origin"]))

    walk(child_link, 0.0)
    return masses, link_origin_bounds


def support_case(axis_id: str, total_mass: float) -> tuple[float | None, str]:
    if "HIP_ROLL" in axis_id or "ANKLE_ROLL" in axis_id:
        return total_mass * G * 0.025, "single-support full planning mass at 25 mm lateral COM offset"
    if "HIP_PITCH" in axis_id or "ANKLE_PITCH" in axis_id:
        return total_mass * G * 0.035, "single-support full planning mass at 35 mm fore-aft COM offset"
    if "KNEE_PITCH" in axis_id:
        return total_mass * G * 0.060, "controlled crouch screen using full planning mass and 60 mm equivalent knee moment arm"
    return None, "not a support-axis load case"


def compute_rows() -> tuple[list[dict], dict]:
    links, joints, children = parse_model()
    total_mass = sum(link["mass"] for link in links.values())
    rows = []
    for axis_id, joint in joints.items():
        masses, origins = subtree_radii(joint["child"], links, children)
        chain_mass = sum(m for _, m, _ in masses)
        gravity_bound = G * sum(m * radius for _, m, radius in masses)
        payload_bound = 0.0
        payload_count = 0
        for gripper_link in ("L_gripper", "R_gripper"):
            if gripper_link in origins:
                payload_count += 1
                payload_bound += PAYLOAD_EACH_HAND_KG * G * (origins[gripper_link] + 0.075)
        gravity_with_payload = gravity_bound + payload_bound
        support_nm, support_basis = support_case(axis_id, total_mass)
        if axis_id.endswith("_YAW") or axis_id in ("HEAD_PAN",):
            static_nm = 0.0
            load_basis = "gravity produces no torque about the nominal vertical yaw axis; inertia, friction, cable and disturbance torque remain SELECTION REQUIRED"
        elif "GRIPPER" in axis_id:
            static_nm = None
            load_basis = "jaw force-to-motor torque depends on the unresolved rack/pinion or tendon geometry and compliance"
        else:
            static_nm = max(gravity_with_payload, support_nm or 0.0)
            load_basis = support_basis if support_nm is not None and support_nm >= gravity_with_payload else "posture-independent triangle-inequality gravity bound for current descendant masses plus 100 g hand payload where applicable"

        actuator_name, ratio, efficiency = actuator_for(axis_id)
        actuator = ACTUATORS[actuator_name]
        effective_endpoint = actuator["stall_nm_12v"] * ratio * efficiency
        development_nm = static_nm * DEVELOPMENT_FACTOR if static_nm is not None else None
        endpoint_ratio = effective_endpoint / development_nm if development_nm and development_nm > 0 else None
        if "ELBOW" in axis_id:
            disposition = "XM430 RETAINED AS WHOLE-BODY P0.1 CANDIDATE; CONTINUOUS/DYNAMIC/THERMAL/PHYSICAL PROOF OPEN"
        elif endpoint_ratio is not None and endpoint_ratio < NARROW_ENDPOINT_RATIO:
            disposition = "NARROW PUBLISHED-STALL-ENDPOINT SCREEN; NO DOWNSIZE; CONTINUOUS/DYNAMIC/THERMAL PROOF BLOCKING"
        else:
            disposition = "PACKAGING CANDIDATE RETAINED; STALL ENDPOINT IS NOT CONTINUOUS CAPABILITY"
        rows.append({
            "axis_id": axis_id,
            "parent_link": joint["parent"],
            "child_link": joint["child"],
            "descendant_mass_kg": f"{chain_mass:.6f}",
            "payload_count": payload_count,
            "gravity_chain_upper_bound_nm": f"{gravity_with_payload:.6f}",
            "support_case_nm": "N/A" if support_nm is None else f"{support_nm:.6f}",
            "governing_static_screen_nm": "SELECTION REQUIRED" if static_nm is None else f"{static_nm:.6f}",
            "development_factor": f"{DEVELOPMENT_FACTOR:.2f}",
            "development_endpoint_screen_nm": "SELECTION REQUIRED" if development_nm is None else f"{development_nm:.6f}",
            "candidate_actuator": actuator_name,
            "candidate_ratio": f"{ratio:.3f}",
            "assumed_transmission_efficiency": f"{efficiency:.3f}",
            "published_12v_stall_endpoint_nm": f"{actuator['stall_nm_12v']:.3f}",
            "effective_published_stall_endpoint_nm": f"{effective_endpoint:.6f}",
            "stall_endpoint_to_development_screen_ratio": "N/A" if endpoint_ratio is None else f"{endpoint_ratio:.3f}",
            "governing_basis": load_basis,
            "candidate_disposition": disposition,
            "unresolved_evidence": "accepted duty cycle and trajectory; continuous torque; current limit; N-T curve; winding/case temperature; reflected inertia; acceleration; contact/impact; regeneration; bearing/joint friction; cable torque; measured mass/COM; physical correlation",
            "authority": "NO PROCUREMENT, FABRICATION, POWERED TEST, MOTION OR ENERGIZATION AUTHORITY",
            "warning": WARNING,
        })
    rows.sort(key=lambda row: list(joints).index(row["axis_id"]))
    status = {
        "identifier": IDENTIFIER,
        "axis_count": len(rows),
        "planning_mass_kg": round(total_mass, 6),
        "payload_each_hand_kg": PAYLOAD_EACH_HAND_KG,
        "development_factor": DEVELOPMENT_FACTOR,
        "reduced_drive_efficiency_assumption": REDUCED_DRIVE_EFFICIENCY,
        "narrow_endpoint_ratio_threshold": NARROW_ENDPOINT_RATIO,
        "elbow_xm430_candidate_retained": True,
        "published_stall_endpoint_used_as_continuous_rating": False,
        "continuous_torque_validated": False,
        "dynamic_gait_loads_validated": False,
        "actuator_selection_released": False,
        "procurement_authority": False,
        "fabrication_authority": False,
        "powered_test_authority": False,
        "motion_authority": False,
        "energization_authority": False,
        "warning": WARNING,
    }
    return rows, status


def update_docs(rows: list[dict], status: dict) -> None:
    narrow = [row for row in rows if "NARROW" in row["candidate_disposition"]]
    report = f"""# HR-30 whole-body joint-load architecture P0.1

**{WARNING}**

This artifact covers all **{len(rows)} axes** in the current floating-base URDF. It provides a reproducible static architecture screen for deciding which actuator packages should remain in P0.1; it is not an actuator release or gait simulation.

For each non-yaw rotary axis, the generator sums the current descendant link masses using a posture-independent triangle-inequality radius bound. A 100 g object is added at each downstream hand. Leg support axes also receive a deliberately explicit single-support screen based on the full {status['planning_mass_kg']:.3f} kg planning model: 25 mm lateral COM offset, 35 mm fore-aft COM offset, or a 60 mm equivalent knee moment arm. The governing static value is multiplied by {DEVELOPMENT_FACTOR:.2f} only as an architecture endpoint screen.

The comparison column uses current official ROBOTIS **12 V stall torque**, transmission ratio and an {REDUCED_DRIVE_EFFICIENCY:.2f} efficiency assumption for reduced axes. ROBOTIS explicitly warns that stall torque is momentary and differs from continuous and real-world output. Consequently no row claims continuous capability. Accepted trajectories, current limits, duty cycle, N-T curves, temperature, inertia, contact, stopping and physical correlation remain mandatory.

The two elbows now retain the 82 g XM430 candidate already represented by the exact X-430 body in CAD. This removes the former XM430/XM540 ambiguity without reusing the archived HR-V0 elbow analysis. It remains a P0.1 candidate pending whole-body duty and physical testing.

{len(narrow)} axes have less than {NARROW_ENDPOINT_RATIO:.2f} ratio between the effective published stall endpoint and the factored development screen. They are explicitly marked narrow and may not be downsized. Yaw and gripper axes retain separate unresolved inertia/mechanism requirements rather than receiving invented torque values.

Primary manufacturer pages were accessed 2026-08-14 and expose no page revision/date. Exact values are recorded in `actuator-endpoint-source-register.csv`.
"""
    (OUT / "joint-load-architecture.md").write_text(report, encoding="utf-8", newline="\n")

    readme_path = OUT / "README.md"
    readme = readme_path.read_text(encoding="utf-8")
    marker = "\n## Whole-body joint-load architecture\n"
    if marker in readme:
        readme = readme.split(marker, 1)[0].rstrip() + "\n"
    readme += f"""

## Whole-body joint-load architecture

All 25 axes now have a reproducible static load screen tied to the current URDF mass tree, the 100 g handoff payload and explicit single-support COM-offset cases. Both elbows use the 82 g XM430 P0.1 candidate. Published stall values remain momentary endpoints only; continuous torque, thermal behavior, dynamic gait loads and physical correlation are open.
"""
    readme_path.write_text(readme.rstrip() + "\n", encoding="utf-8", newline="\n")

    holds_path = OUT / "open-holds.csv"
    holds = list(csv.DictReader(holds_path.open(encoding="utf-8")))
    for row in holds:
        if row["hold_id"] == "HR30-P01-H01":
            row["unresolved_item"] = "All 25 axes now have dimensioned module bindings, standard catalogue bearing candidates and a whole-body static load screen. Continuous/dynamic actuator duty, bearing life/load direction, fits, materials, fasteners, stops, encoders, actuator interfaces and physical proof remain open."
        elif row["hold_id"] == "HR30-P01-H03":
            row["unresolved_item"] = "All twelve leg axes now have explicit single-support static load screens. The current XH540/reduction candidates remain provisional because accepted trajectories, continuous torque, thermal limits, inertia, contact/impact, regeneration, fall restraint and gait correlation remain unproved."
    write_csv(holds_path, holds)

    status_path = OUT / "package-status.json"
    package_status = json.loads(status_path.read_text(encoding="utf-8"))
    package_status.update({
        "whole_body_joint_load_architecture_present": True,
        "joint_load_axis_count": len(rows),
        "elbow_xm430_candidate_retained": True,
        "continuous_actuator_capability_validated": False,
        "dynamic_joint_loads_validated": False,
    })
    status_path.write_text(json.dumps(package_status, indent=2) + "\n", encoding="utf-8")

    page_path = OUT / "index.html"
    page = page_path.read_text(encoding="utf-8")
    section = f'''<section id="joint-loads"><h2>Every axis now has a load screen</h2><div class="grid"><article class="card pass"><div class="metric">25 / 25</div><p>Axes tied to the current URDF mass tree and actuator/transmission allocation.</p></article><article class="card"><h3>Elbows</h3><p>The 82 g XM430 candidate is now used on both sides; continuous-duty proof remains open.</p></article><article class="card hold"><h3>Legs</h3><p>Single-support COM-offset and knee-moment screens exist, but dynamic gait, contact and thermal validation do not.</p></article><article class="card miss"><h3>Stall is not continuous</h3><p>Published stall torque is shown only as a momentary endpoint. It grants no motion authority.</p></article></div><div class="panel"><p><a href="joint-load-architecture.md">Read the load model</a> · <a href="joint-load-screen.csv">All 25 axis results</a> · <a href="actuator-endpoint-source-register.csv">Primary actuator sources</a></p></div></section>'''
    page = re.sub(r'<section id="joint-loads">[\s\S]*?</section>', section, page, count=1) if 'id="joint-loads"' in page else page.replace("</main>", section + "</main>")
    page_path.write_text(page, encoding="utf-8", newline="\n")


def refresh_manifest_release() -> None:
    manifest = OUT / "file-manifest.csv"
    if manifest.exists():
        manifest.unlink()
    files = [path for path in OUT.rglob("*") if path.is_file()]
    write_csv(manifest, [{"path": path.relative_to(OUT).as_posix(), "bytes": path.stat().st_size, "sha256": sha(path), "warning": WARNING} for path in sorted(files)])
    if RELEASE.exists():
        shutil.rmtree(RELEASE)
    shutil.copytree(OUT, RELEASE)


def main() -> int:
    rows, status = compute_rows()
    write_csv(OUT / "joint-load-screen.csv", rows)
    write_csv(OUT / "actuator-endpoint-source-register.csv", [{
        "manufacturer": "ROBOTIS", "model": model,
        "published_mass_kg": f"{data['mass_kg']:.6f}",
        "published_12v_stall_torque_nm": f"{data['stall_nm_12v']:.3f}",
        "published_12v_stall_current_a": f"{data['stall_a_12v']:.3f}",
        "published_12v_no_load_speed_rpm": f"{data['rpm_12v']:.1f}",
        "official_url": data["url"], "document_revision_or_date": "LIVE PAGE; REVISION/DATE NOT PUBLISHED",
        "accessed_date": "2026-08-14",
        "manufacturer_caveat": "STALL TORQUE IS MOMENTARY AND DIFFERS FROM CONTINUOUS AND EXPECTED REAL-WORLD OUTPUT",
        "project_use": "ENDPOINT COMPARISON ONLY; NO CONTINUOUS-TORQUE OR MOTION CREDIT",
        "warning": WARNING,
    } for model, data in ACTUATORS.items()])
    (OUT / "joint-load-architecture-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    update_docs(rows, status)
    shutil.copy2(Path(__file__), OUT / "joint-load-architecture-source.py")
    refresh_manifest_release()
    print(json.dumps(status, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
