"""Generate the fail-closed HR-V0-MECH-P0.6 integrated coordination artifacts."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CAD = ROOT / "cad" / "hr-v0"
OUT = CAD / "generated" / "assembly"
REVISION = "HR-V0-MECH-P0.6"
ARM_REVISION = "HR-V0-ARM-ARCH-P0.7"
STOP_REVISION = "HR-V0-HS-P0.3"
WARNING = "PRELIMINARY - INTEGRATED CANDIDATE ONLY - NOT RELEASED FOR FABRICATION OR ENERGIZATION"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def canonical_text_sha256(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest().upper()


def write_datums() -> list[dict[str, str]]:
    rows = [
        {"datum_id": "A0", "description": "bench plane and base-plan origin", "x_mm": "0", "y_mm": "0", "z_mm": "0", "status": "candidate base datum"},
        {"datum_id": "C0", "description": "candidate column centerline", "x_mm": "-210", "y_mm": "0", "z_mm": "0", "status": "candidate base datum"},
        {"datum_id": "J1", "description": "candidate shoulder rotation axis", "x_mm": "-210", "y_mm": "81.025", "z_mm": "500", "status": f"integrated candidate from {ARM_REVISION}; physical inspection and release open"},
        {"datum_id": "J2", "description": "candidate elbow rotation axis in straight reference", "x_mm": "-210", "y_mm": "283.575", "z_mm": "500", "status": f"integrated candidate from {ARM_REVISION}; physical inspection and release open"},
        {"datum_id": "G1", "description": "candidate H104 gripper-frame datum in straight reference", "x_mm": "-210", "y_mm": "412.625", "z_mm": "500", "status": f"integrated candidate from {ARM_REVISION}; received fit and release open"},
        {"datum_id": "OMAX", "description": "maximum object-center reach requirement boundary in straight reference", "x_mm": "-210", "y_mm": "441.025", "z_mm": "500", "status": "controlled 360 mm J1-relative limit; actual TCP must remain at or inside after received assembly"},
    ]
    with (OUT / "assembly-datums.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys(), lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)
    return rows


def write_svg() -> None:
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="1000" viewBox="0 0 1400 1000">
<style>text{{font-family:Arial,sans-serif;fill:#082b4c;font-size:18px}}.title{{font-size:36px;font-weight:700}}.sub{{font-size:23px;font-weight:700}}.small{{font-size:16px}}.warn{{font-size:20px;font-weight:700;fill:#8a3b00}}.structure{{fill:#66c7f4;stroke:#0b4f8a;stroke-width:3}}.hold{{fill:#fff4cd;stroke:#f3b61f;stroke-width:4}}.datum{{stroke:#0b4f8a;stroke-width:2;stroke-dasharray:8 6}}</style>
<rect width="1400" height="1000" fill="#f7fbff"/>
<text x="40" y="58" class="title">Project Button HR-V0 mechanical coordination</text>
<text x="40" y="98" class="warn">{REVISION} - {WARNING}</text>
<text x="40" y="150" class="sub">Integrated base, column and two-axis arm candidate</text>
<rect x="80" y="545" width="500" height="40" class="structure"/>
<rect x="80" y="505" width="40" height="40" class="structure"/><rect x="540" y="505" width="40" height="40" class="structure"/>
<rect x="100" y="185" width="40" height="360" class="structure"/>
<line x1="330" y1="600" x2="330" y2="625" class="datum"/><text x="300" y="653">A0</text>
<line x1="120" y1="185" x2="120" y2="585" class="datum"/><text x="82" y="685">C0 X=-210 candidate</text>
<text x="80" y="720">Five extrusion cuts and six frame joints remain on</text>
<text x="80" y="755">received-fit, torque, slip and proof hold.</text>
<text x="80" y="790">Bench anchors remain SELECTION REQUIRED for one surveyed Boston bench.</text>
<rect x="680" y="150" width="670" height="600" rx="18" class="hold"/>
<text x="720" y="205" class="sub">ARM RELEASE HOLD</text>
<text x="720" y="250" class="warn">A00-A07 SOURCE GEOMETRY CLOSED AS A CANDIDATE</text>
<text x="720" y="300">J1: (-210, 81.025, 500) mm from A0</text>
<text x="720" y="340">J1-J2: 202.550 mm; J2-G1: 129.050 mm</text>
<text x="720" y="380">J1/J2 axes parallel in the nominal native assembly</text>
<text x="720" y="430">Continuous nominal first contact: J2=121.6433 deg</text>
<text x="720" y="480">Candidate soft/stop datums: 115/118 deg; neither is released.</text>
<text x="720" y="535">Still required before quotation/fabrication:</text>
<text x="750" y="580">received material, fit, fastener and FAI evidence</text>
<text x="750" y="620">bumper selection, cables, guard and stop overtravel proof</text>
<text x="750" y="660">physical proof and qualified mechanical disposition</text>
<text x="720" y="710" class="warn">NO PART OR ASSEMBLY IS RELEASED.</text>
<rect x="40" y="820" width="1310" height="120" rx="14" class="hold"/>
<text x="70" y="865">Interactive candidate: generated/arm-architecture-p0.7/HR-V0_arm_architecture_candidate.glb</text>
<text x="70" y="903">Controlled STEP, drawings and stop evidence: generated/arm-architecture-p0.7/</text>
<text x="40" y="975" class="warn">{REVISION} - {WARNING}</text>
</svg>'''
    (OUT / "HR-V0_general-arrangement.svg").write_text(svg, encoding="utf-8", newline="\n")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    paths = [
        CAD / "mechanical-release-data.csv", CAD / "mechanical-interface-control.csv", CAD / "mechanical-assembly-components.csv",
        ROOT / "bom" / "hr-v0-extrusion-cut-schedule.csv", ROOT / "bom" / "hr-v0-frame-joint-schedule.csv",
        CAD / "frame-joint-placement-p0.2.csv", CAD / "generated" / "vendor-interfaces" / "same-origin-bounds.csv",
        CAD / "generated" / "arm-architecture-p0.7" / "architecture-summary.json",
        CAD / "generated" / "arm-architecture-p0.7" / "interface-schedule.csv",
        CAD / "generated" / "arm-architecture-p0.7" / "transform-schedule.csv",
        CAD / "generated" / "arm-architecture-p0.7" / "continuous-clearance-analysis.json",
        CAD / "generated" / "arm-architecture-p0.7" / "hard-stop-allocation.csv",
        CAD / "generated" / "arm-architecture-p0.7" / "j2-positive-stop-analysis.json",
        CAD / "generated" / "arm-architecture-p0.7" / "j2-positive-stop-controls.csv",
    ]
    data, interfaces, components, extrusions, frame_joints, placements, vendor_rows, arm_summary_rows, arm_interfaces, arm_transforms, continuous_analysis, stop_allocation, positive_stop, stop_controls = [read_csv(path) if path.suffix == ".csv" else json.loads(path.read_text(encoding="utf-8")) for path in paths]
    datums = write_datums(); write_svg()
    summary = {
        "revision": REVISION, "warning": WARNING,
        "source_hashes": {path.relative_to(ROOT).as_posix(): canonical_text_sha256(path) for path in paths},
        "arm_revision": ARM_REVISION,
        "stop_revision": STOP_REVISION,
        "counts": {"controlled_parameters": len(data), "interfaces": len(interfaces), "assembly_components": len(components), "extrusion_cut_rows": len(extrusions), "frame_joint_rows": len(frame_joints), "frame_joint_placements": len(placements), "vendor_interface_sources": len(vendor_rows), "datums": len(datums)},
        "parameter_status_counts": dict(sorted(Counter(row["status"] for row in data).items())),
        "interface_status_counts": dict(sorted(Counter(row["current_status"] for row in interfaces).items())),
        "release_state": "integrated_exact_coordinate_candidate_not_released_for_fabrication_or_energization",
        "integrated_interface_ids": [row["interface"] for row in arm_interfaces],
        "arm_transform_count": len(arm_transforms),
        "arm_sample_count": arm_summary_rows["collision_screen"]["sample_count"],
        "continuous_minimum_guaranteed_clearance_mm": continuous_analysis["minimum_guaranteed_clearance_mm"],
        "continuous_first_nominal_contact_j2_deg": continuous_analysis["continuous_first_contact_j2_deg_numeric"],
        "candidate_j2_soft_limit_deg": float(stop_allocation[0]["candidate_software_limit_deg"]),
        "candidate_j2_positive_hard_stop_datum_deg": float(stop_allocation[0]["candidate_backed_up_hard_stop_datum_deg"]),
        "candidate_j2_physical_uncertainty_budget_deg": float(stop_allocation[0]["candidate_physical_uncertainty_budget_deg"]),
        "candidate_j2_positive_stop_nominal_contact_deg": positive_stop["nominal_metal_contact_deg"],
        "candidate_j2_stop_control_count": len(stop_controls),
        "candidate_j2_bumper_selection_state": "SELECTION REQUIRED - NO ORDER CODE RELEASED",
        "superseded": ["HR-V0-MECH-P0.5", "HR-V0-MECH-P0.4", "HR-V0-MECH-P0.2 arm datum chain", "MV0-001", "MV0-002", "MV0-003", "HR-V0-ARM-ARCH-P0.6", "HR-V0-ARM-ARCH-P0.5", "HR-V0-ARM-ARCH-P0.4", "HR-V0-HS-P0.2", "HR-V0-FAB-RFI-P0.1"],
    }
    (OUT / "mechanical-release-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"Generated {REVISION}: integrated A00-A07 plus positive-stop CAD candidate; continuous nominal contact 121.643289 deg; candidate J2 soft/stop 115/118 deg; no fabrication or energization release")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
