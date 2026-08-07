"""Generate the HR-V0 P0.2 mechanical release-coordination artifacts.

This generator is intentionally standard-library only.  It does not replace the
CadQuery R0.1 native geometry; it binds that geometry, the cut schedule, the
assembly datum chain, and every unresolved physical interface into one readable
general-arrangement artifact.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CAD = ROOT / "cad" / "hr-v0"
OUT = CAD / "generated" / "assembly"
REVISION = "HR-V0-MECH-P0.2"
WARNING = "PRELIMINARY—NOT RELEASED FOR FABRICATION OR ENERGIZATION"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def canonical_text_sha256(path: Path) -> str:
    """Hash controlled text independent of Git's LF/CRLF checkout policy."""
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest().upper()


def write_datums() -> list[dict[str, str]]:
    # A0 is the base/bench-plan origin.  The kinematic chain is shown in the
    # neutral horizontal study pose; angles and physical stop locations remain
    # separate controlled studies.
    rows = [
        {"datum_id": "A0", "description": "bench plane and base plan origin", "x_mm": "0", "y_mm": "0", "z_mm": "0", "status": "candidate datum"},
        {"datum_id": "C0", "description": "column extrusion centerline at bench plane", "x_mm": "-210", "y_mm": "0", "z_mm": "0", "status": "candidate datum"},
        {"datum_id": "J1", "description": "shoulder rotation axis", "x_mm": "-166", "y_mm": "0", "z_mm": "500", "status": "candidate datum; assembled inspection required"},
        {"datum_id": "J2", "description": "elbow rotation axis in neutral study pose", "x_mm": "-6", "y_mm": "0", "z_mm": "500", "status": "derived from J1 plus 160 mm"},
        {"datum_id": "G1", "description": "gripper-frame mounting datum in neutral study pose", "x_mm": "154", "y_mm": "0", "z_mm": "500", "status": "derived from J2 plus 160 mm"},
        {"datum_id": "OMAX", "description": "maximum permitted object-center reach datum in neutral study pose", "x_mm": "194", "y_mm": "0", "z_mm": "500", "status": "360 mm upper limit from J1; not a commanded pose"},
    ]
    with (OUT / "assembly-datums.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys(), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return rows


def write_svg() -> None:
    # Front-view transform: world X/Z in millimetres to drawing coordinates.
    sx = 0.65
    ox = 560.0
    bench_y = 780.0

    def x(world: float) -> float:
        return ox + world * sx

    def y(world_z: float) -> float:
        return bench_y - world_z * sx

    j1x, j2x, g1x, omaxx = (-166.0, -6.0, 154.0, 194.0)
    colx = -210.0
    guard_left = x(j1x - 450.0)
    guard_right = x(j1x + 450.0)
    guard_top = y(950.0)
    dim_y = y(500.0) - 78.0

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="1100" viewBox="0 0 1400 1100" role="img" aria-labelledby="title desc">
  <title id="title">Project Button HR-V0 mechanical general arrangement P0.2</title>
  <desc id="desc">Dimensioned preliminary bench demonstrator datum chain, base, arm, guard reservation, plan view, configuration legend, and unresolved release holds.</desc>
  <style>
    text {{ font-family: system-ui, sans-serif; font-size: 16px; fill: #082554; }}
    .title {{ font-size: 30px; font-weight: 750; }}
    .subtitle {{ font-size: 18px; font-weight: 650; }}
    .warning {{ font-size: 18px; font-weight: 750; fill: #8a4b00; }}
    .small {{ font-size: 14px; }}
    .structure {{ fill: #d9efff; stroke: #082554; stroke-width: 4; }}
    .custom {{ fill: #ffd059; stroke: #082554; stroke-width: 3; }}
    .actuator {{ fill: #2185d0; stroke: #082554; stroke-width: 3; }}
    .hold {{ fill: #fff3cf; stroke: #b17700; stroke-width: 2; }}
    .guard {{ fill: #d9efff; fill-opacity: 0.12; stroke: #2185d0; stroke-width: 3; stroke-dasharray: 10 8; }}
    .axis {{ fill: white; stroke: #082554; stroke-width: 3; }}
    .datum {{ stroke: #082554; stroke-width: 2; stroke-dasharray: 5 5; }}
    .dim {{ stroke: #b17700; stroke-width: 2; marker-start: url(#arrow); marker-end: url(#arrow); }}
    .ext {{ stroke: #b17700; stroke-width: 1.5; }}
    .callout {{ fill: white; stroke: #082554; stroke-width: 2; }}
  </style>
  <defs>
    <marker id="arrow" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#b17700"/></marker>
  </defs>
  <text id="release-warning-top" x="36" y="38" class="warning">{WARNING}</text>
  <text x="36" y="78" class="title">HR-V0 mechanical general arrangement</text>
  <text x="36" y="108" class="subtitle">{REVISION} · neutral datum study · dimensions in millimetres · do not scale</text>

  <text x="36" y="150" class="subtitle">FRONT ELEVATION · A0 BENCH PLANE</text>
  <rect x="{guard_left:.1f}" y="{guard_top:.1f}" width="{guard_right-guard_left:.1f}" height="{bench_y-guard_top:.1f}" class="guard"/>
  <text x="{guard_left+16:.1f}" y="{guard_top+26:.1f}" class="small">900 W x 950 H INTERNAL SPACE RESERVATION — NOT A SAFETY DISTANCE</text>
  <line x1="100" y1="{bench_y:.1f}" x2="790" y2="{bench_y:.1f}" class="datum"/>
  <text x="105" y="{bench_y+24:.1f}" class="small">A0 BENCH PLANE</text>
  <rect x="{x(-250):.1f}" y="{y(40):.1f}" width="{500*sx:.1f}" height="{40*sx:.1f}" class="structure"/>
  <rect x="{x(colx-20):.1f}" y="{y(520):.1f}" width="{40*sx:.1f}" height="{500*sx:.1f}" class="structure"/>
  <rect x="{x(colx+5):.1f}" y="{y(555):.1f}" width="{90*sx:.1f}" height="{110*sx:.1f}" class="custom"/>
  <circle cx="{x(j1x):.1f}" cy="{y(500):.1f}" r="18" class="actuator"/>
  <rect x="{x(j1x):.1f}" y="{y(522):.1f}" width="{160*sx:.1f}" height="{44*sx:.1f}" rx="14" class="custom"/>
  <circle cx="{x(j2x):.1f}" cy="{y(500):.1f}" r="18" class="actuator"/>
  <rect x="{x(j2x):.1f}" y="{y(522):.1f}" width="{160*sx:.1f}" height="{44*sx:.1f}" rx="14" class="custom"/>
  <circle cx="{x(g1x):.1f}" cy="{y(500):.1f}" r="15" class="actuator"/>
  <rect x="{x(g1x):.1f}" y="{y(535):.1f}" width="{40*sx:.1f}" height="{70*sx:.1f}" rx="8" class="hold"/>
  <line x1="{x(omaxx):.1f}" y1="{y(540):.1f}" x2="{x(omaxx):.1f}" y2="{y(460):.1f}" class="datum"/>

  <circle cx="{x(j1x):.1f}" cy="{y(500):.1f}" r="6" class="axis"/><text x="{x(j1x)-18:.1f}" y="{y(500)+38:.1f}" class="subtitle">J1</text>
  <circle cx="{x(j2x):.1f}" cy="{y(500):.1f}" r="6" class="axis"/><text x="{x(j2x)-18:.1f}" y="{y(500)+38:.1f}" class="subtitle">J2</text>
  <circle cx="{x(g1x):.1f}" cy="{y(500):.1f}" r="6" class="axis"/><text x="{x(g1x)-18:.1f}" y="{y(500)+38:.1f}" class="subtitle">G1</text>
  <text x="{x(omaxx)+8:.1f}" y="{y(540):.1f}" class="small">OMAX</text>

  <line x1="{x(j1x):.1f}" y1="{dim_y:.1f}" x2="{x(j2x):.1f}" y2="{dim_y:.1f}" class="dim"/>
  <line x1="{x(j2x):.1f}" y1="{dim_y:.1f}" x2="{x(g1x):.1f}" y2="{dim_y:.1f}" class="dim"/>
  <line x1="{x(j1x):.1f}" y1="{dim_y-42:.1f}" x2="{x(omaxx):.1f}" y2="{dim_y-42:.1f}" class="dim"/>
  <text x="{(x(j1x)+x(j2x))/2-34:.1f}" y="{dim_y-9:.1f}" class="subtitle">160 ±0.5</text>
  <text x="{(x(j2x)+x(g1x))/2-34:.1f}" y="{dim_y-9:.1f}" class="subtitle">160 ±0.5</text>
  <text x="{(x(j1x)+x(omaxx))/2-62:.1f}" y="{dim_y-51:.1f}" class="subtitle">REACH ≤ 360</text>
  <line x1="{x(-278):.1f}" y1="{y(0):.1f}" x2="{x(-278):.1f}" y2="{y(500):.1f}" class="dim"/>
  <text x="{x(-298):.1f}" y="{y(250):.1f}" transform="rotate(-90 {x(-298):.1f} {y(250):.1f})" class="subtitle">J1 AXIS HEIGHT 500 ±2</text>
  <line x1="{x(-250):.1f}" y1="{bench_y+58:.1f}" x2="{x(250):.1f}" y2="{bench_y+58:.1f}" class="dim"/>
  <text x="{x(0)-62:.1f}" y="{bench_y+50:.1f}" class="subtitle">BASE 500</text>

  <text x="850" y="150" class="subtitle">PLAN VIEW · BASE / GUARD RESERVATION</text>
  <rect x="865" y="185" width="378" height="168" class="guard"/>
  <rect x="949" y="202" width="210" height="134" class="structure"/>
  <rect x="964" y="202" width="17" height="134" class="structure"/>
  <circle cx="983" cy="269" r="8" class="axis"/>
  <text x="1000" y="264" class="small">C0 column X=-210</text>
  <text x="1000" y="286" class="small">J1 offset +44 from C0</text>
  <text x="875" y="380" class="small">Guard reservation: 900 W x 400 D. Base: 500 x 320.</text>

  <text x="850" y="430" class="subtitle">CONFIGURATION LEGEND</text>
  <rect x="850" y="450" width="24" height="24" class="structure"/><text x="888" y="469">selected profile / candidate cut length</text>
  <rect x="850" y="486" width="24" height="24" class="custom"/><text x="888" y="505">custom RFQ geometry; FAI and fit holds remain</text>
  <rect x="850" y="522" width="24" height="24" class="actuator"/><text x="888" y="541">evaluation actuator / received identity required</text>
  <rect x="850" y="558" width="24" height="24" class="hold"/><text x="888" y="577">design or selection hold</text>

  <rect x="830" y="620" width="525" height="334" rx="12" class="hold"/>
  <text x="850" y="654" class="subtitle">FABRICATION / ASSEMBLY HOLDS</text>
  <text x="850" y="690">1. Execute MV0-FC01 / FC02 / FC03 on received frames.</text>
  <text x="850" y="720">2. Freeze hole size/position, fastener stacks, torque and retention.</text>
  <text x="850" y="750">3. Proof six 40-4334 / twenty-four 75-3422 frame-joint candidates.</text>
  <text x="850" y="780">4. Survey the Boston build bench and engineer its anchors.</text>
  <text x="850" y="810">5. Design and proof backed-up hard stops, guard and catch.</text>
  <text x="850" y="840">6. Close measured mass/COM/inertia and rerun load calculations.</text>
  <text x="850" y="870">7. Complete FAI and unpowered assembly inspection.</text>
  <text x="850" y="910" class="warning">NO STRUCTURAL CUTTING ORDER OR POWERED MOTION IS RELEASED.</text>

  <rect x="36" y="900" width="745" height="132" rx="10" class="callout"/>
  <text x="56" y="932" class="subtitle">DATUM CHAIN</text>
  <text x="56" y="962">A0 base center → C0 column X=-210 → J1 X=-166 / Z=500</text>
  <text x="56" y="992">J2 = J1 +160 in neutral pose → G1 = J2 +160 → OMAX ≤ J1 +360</text>
  <text x="56" y="1018" class="small">Only the neutral pose is depicted. Joint limits, sweep, stopping travel and physical stops are controlled separately.</text>
  <text id="release-warning-bottom" x="36" y="1074" class="warning">{REVISION} · {WARNING}</text>
</svg>'''
    (OUT / "HR-V0_general-arrangement.svg").write_text(svg, encoding="utf-8", newline="\n")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    data_path = CAD / "mechanical-release-data.csv"
    interface_path = CAD / "mechanical-interface-control.csv"
    components_path = CAD / "mechanical-assembly-components.csv"
    extrusion_path = ROOT / "bom" / "hr-v0-extrusion-cut-schedule.csv"
    frame_joint_path = ROOT / "bom" / "hr-v0-frame-joint-schedule.csv"
    data = read_csv(data_path)
    interfaces = read_csv(interface_path)
    components = read_csv(components_path)
    extrusions = read_csv(extrusion_path)
    frame_joints = read_csv(frame_joint_path)
    datums = write_datums()
    write_svg()
    summary = {
        "revision": REVISION,
        "warning": WARNING,
        "source_hashes": {
            path.relative_to(ROOT).as_posix(): canonical_text_sha256(path)
            for path in (data_path, interface_path, components_path, extrusion_path, frame_joint_path)
        },
        "counts": {
            "controlled_parameters": len(data),
            "interfaces": len(interfaces),
            "assembly_components": len(components),
            "extrusion_cut_rows": len(extrusions),
            "frame_joint_rows": len(frame_joints),
            "datums": len(datums),
        },
        "parameter_status_counts": dict(sorted(Counter(row["status"] for row in data).items())),
        "interface_status_counts": dict(sorted(Counter(row["current_status"] for row in interfaces).items())),
        "release_state": "coordination_candidate_not_released",
    }
    (OUT / "mechanical-release-summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(
        f"Generated {REVISION}: {len(data)} parameters, {len(interfaces)} interfaces, "
        f"{len(components)} component groups, {len(frame_joints)} frame joints, {len(datums)} datums"
    )
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
