"""Generate the fail-closed HR-V0-MECH-P0.3 coordination artifacts."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CAD = ROOT / "cad" / "hr-v0"
OUT = CAD / "generated" / "assembly"
REVISION = "HR-V0-MECH-P0.3"
WARNING = "PRELIMINARY - NO BUILDABLE ARM GEOMETRY - NOT RELEASED FOR FABRICATION OR ENERGIZATION"


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
        {"datum_id": "J1", "description": "shoulder rotation axis", "x_mm": "", "y_mm": "", "z_mm": "", "status": "SELECTION REQUIRED - P0.2 transform superseded"},
        {"datum_id": "J2", "description": "elbow rotation axis", "x_mm": "", "y_mm": "", "z_mm": "", "status": "SELECTION REQUIRED - P0.2 transform superseded"},
        {"datum_id": "G1", "description": "gripper-frame datum", "x_mm": "", "y_mm": "", "z_mm": "", "status": "SELECTION REQUIRED - P0.2 transform superseded"},
        {"datum_id": "OMAX", "description": "maximum object-center reach datum", "x_mm": "", "y_mm": "", "z_mm": "", "status": "SELECTION REQUIRED - depends on replacement arm"},
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
<text x="40" y="150" class="sub">Base/frame candidate retained</text>
<rect x="80" y="545" width="500" height="40" class="structure"/>
<rect x="80" y="505" width="40" height="40" class="structure"/><rect x="540" y="505" width="40" height="40" class="structure"/>
<rect x="100" y="45" width="40" height="500" class="structure"/>
<line x1="330" y1="600" x2="330" y2="625" class="datum"/><text x="300" y="653">A0</text>
<line x1="120" y1="45" x2="120" y2="585" class="datum"/><text x="82" y="685">C0 X=-210 candidate</text>
<text x="80" y="730">Five exact candidate extrusion cuts and six frame joints remain on physical-fit/proof hold.</text>
<text x="80" y="764">Bench anchors remain SELECTION REQUIRED for one surveyed Boston bench.</text>
<rect x="680" y="150" width="670" height="600" rx="18" class="hold"/>
<text x="720" y="205" class="sub">ARM ARCHITECTURE HOLD</text>
<text x="720" y="255" class="warn">J1, J2, G1 AND OMAX COORDINATES WITHDRAWN</text>
<text x="720" y="305">Exact manufacturer STEP geometry shows:</text>
<text x="750" y="350">1. H101 is a moving output U-frame.</text>
<text x="750" y="390">2. S102 is a bottom body frame in a different plane.</text>
<text x="750" y="430">3. MV0-001 and MV0-003 do not define the required 3D transforms.</text>
<text x="750" y="470">4. The former 44 / 160 / 160 mm chain is superseded.</text>
<text x="720" y="535">Replacement must close MECH-005 / AUDIT-MECH-012:</text>
<text x="750" y="580">exact transforms and parallel-axis proof</text>
<text x="750" y="620">collision, tool access, fasteners and cable space</text>
<text x="750" y="660">load path, tolerances, drawings, FAI and qualified review</text>
<text x="720" y="710" class="warn">NO ARM PART MAY BE QUOTED OR FABRICATED.</text>
<rect x="40" y="820" width="1310" height="120" rx="14" class="hold"/>
<text x="70" y="865">Interactive exact-source evidence: generated/vendor-interfaces/XM540-H101-S102-same-origin.step</text>
<text x="70" y="903">Readable orientation evidence: generated/vendor-interfaces/XM540-frame-orientation.svg</text>
<text x="40" y="975" class="warn">{REVISION} - {WARNING}</text>
</svg>'''
    (OUT / "HR-V0_general-arrangement.svg").write_text(svg, encoding="utf-8", newline="\n")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    paths = [
        CAD / "mechanical-release-data.csv", CAD / "mechanical-interface-control.csv", CAD / "mechanical-assembly-components.csv",
        ROOT / "bom" / "hr-v0-extrusion-cut-schedule.csv", ROOT / "bom" / "hr-v0-frame-joint-schedule.csv",
        CAD / "frame-joint-placement-p0.2.csv", CAD / "generated" / "vendor-interfaces" / "same-origin-bounds.csv",
    ]
    data, interfaces, components, extrusions, frame_joints, placements, vendor_rows = [read_csv(path) for path in paths]
    datums = write_datums(); write_svg()
    summary = {
        "revision": REVISION, "warning": WARNING,
        "source_hashes": {path.relative_to(ROOT).as_posix(): canonical_text_sha256(path) for path in paths},
        "counts": {"controlled_parameters": len(data), "interfaces": len(interfaces), "assembly_components": len(components), "extrusion_cut_rows": len(extrusions), "frame_joint_rows": len(frame_joints), "frame_joint_placements": len(placements), "vendor_interface_sources": len(vendor_rows), "datums": len(datums)},
        "parameter_status_counts": dict(sorted(Counter(row["status"] for row in data).items())),
        "interface_status_counts": dict(sorted(Counter(row["current_status"] for row in interfaces).items())),
        "release_state": "base_coordination_only_arm_architecture_withdrawn",
        "superseded": ["HR-V0-MECH-P0.2 arm datum chain", "MV0-001", "MV0-002", "MV0-003", "HR-V0-FAB-RFI-P0.1"],
    }
    (OUT / "mechanical-release-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"Generated {REVISION}: base coordination retained; J1/J2/G1/OMAX blanked; arm architecture withdrawn")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
