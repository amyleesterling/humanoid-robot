"""Generate the HR-V0 hard-stop-region clearance and interface-acquisition package.

This package extends the nominal P0.7 collision evidence only into the three
regions needed to evaluate J1 minimum, J1 maximum and J2 minimum stop concepts.
It deliberately does not invent an axial stack, attachment feature, bumper or
released stop datum from nominal vendor CAD.
"""

from __future__ import annotations

import json
import math
import shutil
from pathlib import Path

import cadquery as cq

import generate_hr_v0_arm_architecture as arm


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "cad" / "hr-v0" / "generated" / "stop-region-clearance-p0.1"
REVISION = "HR-V0-STOP-REGION-P0.1"
PARENT_ARM_REVISION = "HR-V0-ARM-ARCH-P0.7"
WARNING = "PRELIMINARY - NOMINAL CAD EVIDENCE ONLY - NO STOP OR MOTION RELEASE"
INCREMENT_DEG = 0.5
REQUIRED_CLEARANCE_MM = 0.75


def values(start: float, stop: float) -> list[float]:
    count = int(round((stop - start) / INCREMENT_DEG))
    return [round(start + index * INCREMENT_DEG, 6) for index in range(count + 1)]


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    arm.write_csv(path, rows)


def build_shapes() -> tuple[dict[str, cq.Shape], dict[str, cq.Shape], dict[str, cq.Shape]]:
    xm540 = arm.import_step("XMHD-540.N101.I101.STP")
    h101 = arm.import_step("FR13-H101K.stp")
    s102 = arm.import_step("FR13-S102K.stp")
    h104 = arm.import_step("FR12-H104K.stp")
    joint_body = arm.actuator_to_joint_frame(xm540)

    fixed = {
        "COLUMN": arm.column_envelope(),
        "SHOULDER_SUPPORT": arm.shoulder_support_plate(),
        "J1_BODY": arm.rotate_x(joint_body, 90.0),
        "J1_S102": arm.rotate_x(s102, 90.0),
    }
    upper = {
        "J1_H101": h101,
        "UPPER_PROX_ADAPTER": arm.adapter(32.0),
        "UPPER_MEMBER": arm.beam(32.0 + arm.PLATE_T, arm.UPPER_BEAM_L),
        "UPPER_DIST_ADAPTER": arm.j2_positive_catch_adapter(32.0 + arm.PLATE_T + arm.UPPER_BEAM_L),
        "J2_BODY": arm.rotate_x(joint_body, 90.0).translate((0.0, arm.J2_Y, 0.0)),
        "J2_S102": arm.rotate_x(s102, 90.0).translate((0.0, arm.J2_Y, 0.0)),
    }
    fore_y = arm.J2_Y + 32.0
    moving = {
        "J2_H101": h101.translate((0.0, arm.J2_Y, 0.0)),
        "FORE_PROX_ADAPTER": arm.j2_positive_striker_adapter(fore_y),
        "FORE_MEMBER": arm.beam(fore_y + arm.PLATE_T, arm.FOREARM_BEAM_L),
        "FORE_DIST_H104_ADAPTER": arm.gripper_adapter(fore_y + arm.PLATE_T + arm.FOREARM_BEAM_L),
        "G1_H104": arm.rotate_x(h104, 180.0).translate((0.0, arm.G1_Y, 0.0)),
    }
    return fixed, upper, moving


def sample_schedule() -> list[tuple[float, float, str]]:
    scheduled: dict[tuple[float, float], str] = {}
    for q2 in values(10.0, 15.0):
        for q1 in values(-25.0, 75.0):
            scheduled[(q1, q2)] = "J2_MIN_REGION"
    for q2 in values(15.5, 120.0):
        for q1 in values(-25.0, -20.5):
            scheduled[(q1, q2)] = "J1_MIN_REGION"
        for q1 in values(70.5, 75.0):
            scheduled[(q1, q2)] = "J1_MAX_REGION"
    return [(q1, q2, scheduled[(q1, q2)]) for q1, q2 in sorted(scheduled, key=lambda item: (item[1], item[0]))]


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    fixed, upper_zero, moving_zero = build_shapes()
    intentional_j1 = {("J1_BODY", "J1_H101"), ("J1_S102", "J1_H101")}
    intentional_j2 = {("J2_BODY", "J2_H101"), ("J2_S102", "J2_H101")}
    intentional_stop = {("UPPER_DIST_ADAPTER", "FORE_PROX_ADAPTER")}

    schedule = sample_schedule()
    q1_values = sorted({item[0] for item in schedule})
    q2_values = sorted({item[1] for item in schedule})
    fixed_bounds = {name: arm.bbox_tuple(shape) for name, shape in fixed.items()}

    base_upper: dict[float, tuple[float, int, list[str]]] = {}
    for q1 in q1_values:
        transformed = {name: arm.rotate_x(shape, q1) for name, shape in upper_zero.items()}
        volume = 0.0
        tested = 0
        hits: list[str] = []
        for fixed_name, fixed_shape in fixed.items():
            for upper_name, upper_shape in transformed.items():
                if (fixed_name, upper_name) in intentional_j1:
                    continue
                if arm.boxes_overlap(fixed_shape, upper_shape):
                    tested += 1
                    intersection = arm.positive_intersection(fixed_shape, upper_shape)
                    volume += intersection
                    if intersection > 1e-5:
                        hits.append(f"{fixed_name}:{upper_name}={intersection:.6f}")
        base_upper[q1] = volume, tested, hits

    upper_fore: dict[float, tuple[float, int, list[str], dict[str, cq.Shape], dict[str, tuple[float, ...]]]] = {}
    for q2 in q2_values:
        transformed = {name: arm.rotate_x(shape, q2, arm.J2_Y) for name, shape in moving_zero.items()}
        volume = 0.0
        tested = 0
        hits: list[str] = []
        for upper_name, upper_shape in upper_zero.items():
            for moving_name, moving_shape in transformed.items():
                if (upper_name, moving_name) in intentional_j2 | intentional_stop:
                    continue
                if arm.boxes_overlap(upper_shape, moving_shape):
                    tested += 1
                    intersection = arm.positive_intersection(upper_shape, moving_shape)
                    volume += intersection
                    if intersection > 1e-5:
                        hits.append(f"{upper_name}:{moving_name}={intersection:.6f}")
        upper_fore[q2] = volume, tested, hits, transformed, {
            name: arm.bbox_tuple(shape) for name, shape in transformed.items()
        }

    sample_rows: list[dict[str, object]] = []
    maximum_intersection = 0.0
    for q1, q2, region in schedule:
        base_volume, base_tested, base_hits = base_upper[q1]
        relative_volume, relative_tested, relative_hits, fore_relative, fore_bounds = upper_fore[q2]
        volume = base_volume + relative_volume
        tested = base_tested + relative_tested
        hits = list(base_hits) + list(relative_hits)
        for fixed_name, fixed_shape in fixed.items():
            for moving_name, relative_shape in fore_relative.items():
                rotated_bounds = arm.rotate_bbox_x(fore_bounds[moving_name], q1)
                if not arm.bbox_values_overlap(fixed_bounds[fixed_name], rotated_bounds):
                    continue
                tested += 1
                transformed = arm.rotate_x(relative_shape, q1)
                intersection = arm.positive_intersection(fixed_shape, transformed)
                volume += intersection
                if intersection > 1e-5:
                    hits.append(f"{fixed_name}:{moving_name}={intersection:.6f}")
        maximum_intersection = max(maximum_intersection, volume)
        sample_rows.append(
            {
                "region": region,
                "j1_deg": f"{q1:.1f}",
                "j2_internal_deg": f"{q2:.1f}",
                "broadphase_pairs_requiring_boolean": tested,
                "colliding_pairs": ";".join(hits),
                "sampled_pairwise_intersection_mm3": f"{volume:.6f}",
                "result": "PASS_NOMINAL" if volume <= 1e-5 else "COLLISION",
                "scope": "P0.7 nominal rigid bodies only; intentional frame and C06/C07 positive-stop interfaces excluded; cables, guards, tolerances, compliance, deformation and proposed stop hardware excluded",
            }
        )
    write_csv(OUT / "stop-region-clearance-samples.csv", sample_rows)

    summary_rows: list[dict[str, object]] = []
    cell_rows: list[dict[str, object]] = []

    def record_1d(region: str, prefix: str, q_lo: float, q_hi: float) -> None:
        for fixed_name, fixed_shape in fixed.items():
            for upper_name, upper_shape in upper_zero.items():
                if (fixed_name, upper_name) in intentional_j1:
                    continue
                summary, cells = arm.certify_continuous_1d(
                    pair_id=f"{region}:{prefix}:{fixed_name}:{upper_name}",
                    fixed_shape=fixed_shape,
                    moving_shape=upper_shape,
                    rotation_origin_y=0.0,
                    q_lo=q_lo,
                    q_hi=q_hi,
                    coordinate="J1",
                )
                summary_rows.append(summary)
                cell_rows.extend(cells)

    record_1d("J1_MIN_REGION", "BASE_UPPER", -25.0, -20.0)
    record_1d("J1_MAX_REGION", "BASE_UPPER", 70.0, 75.0)

    for upper_name, upper_shape in upper_zero.items():
        for moving_name, moving_shape in moving_zero.items():
            if (upper_name, moving_name) in intentional_j2 | intentional_stop:
                continue
            summary, cells = arm.certify_continuous_1d(
                pair_id=f"J2_MIN_REGION:UPPER_FORE:{upper_name}:{moving_name}",
                fixed_shape=upper_shape,
                moving_shape=moving_shape,
                rotation_origin_y=arm.J2_Y,
                q_lo=10.0,
                q_hi=15.0,
                coordinate="J2",
            )
            summary_rows.append(summary)
            cell_rows.extend(cells)

    regions_2d = (
        ("J1_MIN_REGION", -25.0, -20.0, 10.0, 120.0),
        ("J1_MAX_REGION", 70.0, 75.0, 10.0, 120.0),
        ("J2_MIN_REGION", -20.0, 70.0, 10.0, 15.0),
    )
    for region, q1_lo, q1_hi, q2_lo, q2_hi in regions_2d:
        for fixed_name, fixed_shape in fixed.items():
            for moving_name, moving_shape in moving_zero.items():
                summary, cells = arm.certify_continuous_2d(
                    pair_id=f"{region}:BASE_FORE:{fixed_name}:{moving_name}",
                    fixed_shape=fixed_shape,
                    moving_shape=moving_shape,
                    q1_lo=q1_lo,
                    q1_hi=q1_hi,
                    q2_lo=q2_lo,
                    q2_hi=q2_hi,
                )
                summary_rows.append(summary)
                cell_rows.extend(cells)

    write_csv(OUT / "stop-region-continuous-summary.csv", summary_rows)
    write_csv(OUT / "stop-region-continuous-cells.csv", cell_rows)
    minimum_guaranteed = min(float(row["minimum_guaranteed_clearance_mm"]) for row in summary_rows)

    measurements = [
        ("HSI-001", "CONFIG", "received XM540 identity and serial for J1/J2", "supplier label plus receiving photographs", "exact received article must match controlled source"),
        ("HSI-002", "CONFIG", "received H101 and S102 identities for J1/J2", "labels, kit trace and receiving photographs", "no visual substitution"),
        ("HSI-003", "AXIAL", "J1 assembled H101/C01 outer X faces relative to joint axis", "CMM or calibrated height/depth method", "SELECTION REQUIRED"),
        ("HSI-004", "AXIAL", "J1 assembled S102/C05 outer X faces relative to joint axis", "CMM or calibrated height/depth method", "SELECTION REQUIRED"),
        ("HSI-005", "AXIAL", "J2 assembled H101/C06 outer X faces relative to joint axis", "CMM or calibrated height/depth method", "SELECTION REQUIRED"),
        ("HSI-006", "AXIAL", "J2 assembled S102/C07 outer X faces relative to joint axis", "CMM or calibrated height/depth method", "SELECTION REQUIRED"),
        ("HSI-007", "ENVELOPE", "available side-plate volume on both X sides of J1", "3D scan or CMM point cloud across -25..75 deg", "include screws, tools, connectors and service access"),
        ("HSI-008", "ENVELOPE", "available side-plate volume on both X sides of J2", "3D scan or CMM point cloud across 10..118 deg", "include screws, tools, connectors and service access"),
        ("HSI-009", "ATTACHMENT", "approved fixed-structure attachment features near J1", "manufacturer drawing plus received feature metrology", "do not infer unused holes or threads"),
        ("HSI-010", "ATTACHMENT", "approved moving-link attachment features near J1", "manufacturer drawing plus received stack metrology", "longer/shared fasteners require separate release"),
        ("HSI-011", "ATTACHMENT", "approved fixed-structure attachment features near J2", "manufacturer drawing plus received feature metrology", "do not infer unused holes or threads"),
        ("HSI-012", "ATTACHMENT", "approved moving-link attachment features near J2", "manufacturer drawing plus received stack metrology", "longer/shared fasteners require separate release"),
        ("HSI-013", "MOTION", "external mechanical angle datum, repeatability and unpowered backlash at J1", "calibrated external angle reference, repeated bidirectional hand-positioned series", "encoder calibration requires a later separately authorized powered stage; SELECTION REQUIRED acceptance and uncertainty"),
        ("HSI-014", "MOTION", "external mechanical angle datum, repeatability and unpowered backlash at J2", "calibrated external angle reference, repeated bidirectional hand-positioned series", "encoder calibration requires a later separately authorized powered stage; SELECTION REQUIRED acceptance and uncertainty"),
        ("HSI-015", "CABLE_GUARD", "received cable, connector and strain-relief swept volume", "configured harness plus scan/inspection at boundary poses", "cables may not become stops"),
        ("HSI-016", "CABLE_GUARD", "received guard and access-clearance swept volume", "configured guard inspection at boundary poses", "nominal CAD does not establish safety distance"),
        ("HSI-017", "LOAD", "accepted stop contact radius and load path", "qualified structural model tied to received geometry", "include prying, unequal sharing, parent structure and fasteners"),
        ("HSI-018", "LOAD", "effective and reflected inertia for every released case", "instrumented dynamic characterization", "include payload, current, speed, voltage, temperature and fault cases"),
        ("HSI-019", "BUMPER", "exact bumper and retention selection", "current manufacturer force-stroke, energy, temperature, aging and life evidence", "SELECTION REQUIRED; metal backup remains mandatory"),
        ("HSI-020", "MANUFACTURING", "supplier DFM and inspection capability for selected stop topology", "written DFM, material certification and FAI plan", "no quotation or fabrication release in this package"),
    ]
    measurement_rows = [
        {
            "measurement_id": item[0],
            "category": item[1],
            "required_input": item[2],
            "evidence_method": item[3],
            "acceptance_or_boundary": item[4],
            "value": "NOT EXECUTED",
            "instrument_or_source": "SELECTION REQUIRED",
            "uncertainty_or_revision": "SELECTION REQUIRED",
            "status": "OPEN",
            "warning": WARNING,
        }
        for item in measurements
    ]
    write_csv(OUT / "stop-interface-measurement-register.csv", measurement_rows)

    topology_rows = [
        {"topology_id": "HST-001", "concept": "coaxial cam or sector ring", "potential_advantage": "direct angle definition and compact tangential contact", "blocking_evidence": "HSI-003..006 axial stack; HSI-009..012 approved attachment; HSI-015..020 cable, load, bumper and manufacturing closure", "disposition": "CANDIDATE ROUTE - NOT SELECTED"},
        {"topology_id": "HST-002", "concept": "external side-plate sector and moving striker", "potential_advantage": "keeps contact outside actuator case and can use replaceable metal/bumper elements", "blocking_evidence": "HSI-007..012 side volume and attachment; HSI-015..020 cable, load, bumper and manufacturing closure", "disposition": "CANDIDATE ROUTE - NOT SELECTED"},
        {"topology_id": "HST-003", "concept": "integral three-dimensional C01/C05 and C06/C07 stop extensions", "potential_advantage": "direct load path through current custom adapters", "blocking_evidence": "requires new non-planar parts, exact received clearance, qualified parent-part analysis and supplier DFM", "disposition": "CANDIDATE ROUTE - NOT SELECTED"},
        {"topology_id": "HST-004", "concept": "actuator case, connector, cable, guard or cosmetic cover as stop", "potential_advantage": "none accepted", "blocking_evidence": "prohibited load path under SAFE-007 and MECH-006", "disposition": "REJECTED"},
        {"topology_id": "HST-005", "concept": "software limit without independent metal backup", "potential_advantage": "none accepted", "blocking_evidence": "does not satisfy independent physical restraint requirement", "disposition": "REJECTED"},
    ]
    write_csv(OUT / "stop-topology-decision-register.csv", topology_rows)

    analysis = {
        "revision": REVISION,
        "parent_arm_revision": PARENT_ARM_REVISION,
        "warning": WARNING,
        "sample_increment_deg": INCREMENT_DEG,
        "sample_count": len(sample_rows),
        "sample_regions": {
            "j1_min": {"j1_deg": [-25.0, -20.5], "j2_deg": [15.5, 120.0]},
            "j1_max": {"j1_deg": [70.5, 75.0], "j2_deg": [15.5, 120.0]},
            "j2_min": {"j1_deg": [-25.0, 75.0], "j2_deg": [10.0, 15.0]},
        },
        "maximum_sampled_intersection_mm3": round(maximum_intersection, 6),
        "continuous_certificate_count": len(summary_rows),
        "continuous_leaf_cell_count": len(cell_rows),
        "minimum_guaranteed_clearance_mm": round(minimum_guaranteed, 6),
        "required_guaranteed_clearance_mm": REQUIRED_CLEARANCE_MM,
        "measurement_inputs_open": len(measurement_rows),
        "stop_topology_selected": False,
        "interpretation": "The historical -25/+75 deg J1 and +10 deg J2 boundary regions are nominally free of non-intentional P0.7 rigid-body contact. This does not select those datums or prove room for stop hardware, cables, guards, tolerances, deformation, backlash, stopping travel or an as-built article.",
        "status": "NOMINAL REGION FEASIBILITY ONLY - PHYSICAL INTERFACE ACQUISITION AND QUALIFIED STOP DESIGN REQUIRED",
    }
    (OUT / "stop-region-clearance-analysis.json").write_text(
        json.dumps(analysis, indent=2) + "\n", encoding="utf-8", newline="\n"
    )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1050" viewBox="0 0 1600 1050">
<style>text{{font-family:Arial,sans-serif;fill:#082b4c;font-size:18px}}.title{{font-size:36px;font-weight:700}}.head{{font-size:24px;font-weight:700}}.warn{{font-size:20px;font-weight:700;fill:#8a3b00}}.card{{fill:#f7fbff;stroke:#0b4f8a;stroke-width:3}}.hold{{fill:#fff5d8;stroke:#d59600;stroke-width:3}}.axis{{stroke:#0b4f8a;stroke-width:7}}.arc{{fill:none;stroke:#66c7f4;stroke-width:18;stroke-linecap:round}}.stop{{stroke:#f3b61f;stroke-width:8}}</style>
<rect width="1600" height="1050" fill="#ffffff"/>
<text x="60" y="70" class="title">HR-V0 hard-stop region evidence and acquisition boundary</text>
<text x="60" y="112" class="warn">{REVISION} / {WARNING}</text>
<rect x="55" y="155" width="720" height="390" rx="16" class="card"/>
<text x="90" y="205" class="head">What the nominal CAD now establishes</text>
<circle cx="335" cy="365" r="18" fill="#0b4f8a"/>
<path d="M 495 290 A 180 180 0 0 0 480 445" class="arc"/>
<line x1="335" y1="365" x2="480" y2="297" class="axis"/>
<line x1="335" y1="365" x2="382" y2="532" class="axis"/>
<line x1="467" y1="285" x2="500" y2="309" class="stop"/>
<line x1="365" y1="529" x2="400" y2="519" class="stop"/>
<text x="95" y="505">J1 candidate regions screened continuously: -25..-20 deg and 70..75 deg</text>
<text x="95" y="535">J2 candidate region screened continuously: 10..15 deg</text>
<rect x="825" y="155" width="720" height="390" rx="16" class="hold"/>
<text x="860" y="205" class="head">What remains physically unknown</text>
<text x="860" y="255">• received horn/idler and frame axial stack</text>
<text x="860" y="295">• approved fixed and moving attachment features</text>
<text x="860" y="335">• side-plate, tool, cable and guard swept volumes</text>
<text x="860" y="375">• stop material, bumper, retention and contact radius</text>
<text x="860" y="415">• stopping travel, backlash, compliance and uncertainty</text>
<text x="860" y="455">• impact, fatigue, prying, fastener and parent-load proof</text>
<text x="860" y="505" class="warn">No topology or stop angle is released.</text>
<rect x="55" y="585" width="1490" height="390" rx="16" class="card"/>
<text x="90" y="640" class="head">Fail-closed next action</text>
<text x="90" y="690">1. Receive and identify the exact J1/J2 actuator, H101, S102 and current custom-adapter articles.</text>
<text x="90" y="735">2. Execute HSI-001..020 with calibrated instruments; preserve raw scans, uncertainty and photographs.</text>
<text x="90" y="780">3. Select one topology only after attachment and swept-volume evidence is complete.</text>
<text x="90" y="825">4. Generate integrated stop CAD, drawings, tolerance/load analysis and a guarded single-axis test article.</text>
<text x="90" y="870">5. Measure contact, coast, stopping overtravel, impact and post-test condition before requesting motion credit.</text>
<text x="90" y="925" class="warn">Do not order, fabricate, connect, move or energize from this diagram.</text>
</svg>'''
    (OUT / "HR-V0_stop-region-acquisition.svg").write_text(svg, encoding="utf-8", newline="\n")

    html = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-V0 hard-stop region guide</title><style>
:root{{--sky:#66c7f4;--navy:#082b4c;--blue:#0b4f8a;--gold:#f3b61f;--paper:#f7fbff;--hold:#fff5d8}}*{{box-sizing:border-box}}body{{margin:0;font:clamp(16px,1.2vw,19px)/1.55 Arial,sans-serif;color:var(--navy);background:#fff}}header{{padding:2rem clamp(1rem,5vw,5rem);background:linear-gradient(135deg,var(--sky),#dff5ff);border-bottom:6px solid var(--gold)}}h1{{font-size:clamp(2rem,4vw,4rem);line-height:1.05;margin:.25rem 0 1rem}}h2{{font-size:clamp(1.45rem,2.4vw,2.2rem)}}.warning{{font-weight:700;color:#713300;background:var(--hold);border:3px solid var(--gold);padding:1rem;border-radius:.8rem}}main{{max-width:1280px;margin:auto;padding:2rem clamp(1rem,4vw,3rem)}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,330px),1fr));gap:1.25rem}}.card{{border:3px solid var(--blue);border-radius:1rem;padding:1.25rem;background:var(--paper)}}button{{font:inherit;font-weight:700;color:var(--navy);background:#fff;border:3px solid var(--blue);border-radius:.7rem;padding:.75rem 1rem;margin:.25rem;cursor:pointer}}button[aria-pressed="true"]{{background:var(--gold)}}table{{width:100%;border-collapse:collapse;display:block;overflow:auto}}th,td{{text-align:left;vertical-align:top;padding:.8rem;border-bottom:1px solid #9db7ca;min-width:150px}}th{{background:var(--navy);color:#fff;position:sticky;top:0}}.meta{{font-size:14px}}img{{width:100%;height:auto;border:2px solid #9db7ca}}[hidden]{{display:none!important}}</style></head><body>
<header><div class="meta">{REVISION} · parent {PARENT_ARM_REVISION}</div><h1>Hard-stop region evidence</h1><div class="warning">{WARNING}. This guide does not define a fabricable stop or permit motion.</div></header>
<main><div class="grid"><section class="card"><h2>Result</h2><p>The three historic boundary regions are free of nominal P0.7 rigid-body contact in the new sampled and continuous checks.</p><p><strong>That is geometric feasibility, not a released stop datum.</strong></p></section><section class="card"><h2>Evidence scale</h2><p>{len(sample_rows):,} sampled boundary poses<br>{len(summary_rows)} continuous pair-region certificates<br>{len(measurement_rows)} physical inputs still open</p></section><section class="card"><h2>Why no stop part yet</h2><p>The current source does not establish the as-built axial stack, approved attachment features, cable/guard sweeps, or load/bumper basis. Drawing a cam before those measurements would invent interfaces.</p></section></div>
<h2>Readable boundary map</h2><img src="HR-V0_stop-region-acquisition.svg" alt="Hard-stop region evidence and acquisition boundary">
<h2>Explore the remaining inputs</h2><div><button data-filter="ALL" aria-pressed="true">All</button><button data-filter="AXIAL">Axial stack</button><button data-filter="ATTACHMENT">Attachment</button><button data-filter="CABLE_GUARD">Cable &amp; guard</button><button data-filter="LOAD">Loads</button></div>
<table><thead><tr><th>ID</th><th>Category</th><th>Required input</th><th>Evidence method</th><th>Boundary</th></tr></thead><tbody>{''.join(f'<tr data-category="{row[1]}"><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td></tr>' for row in measurements)}</tbody></table>
</main><script>const buttons=[...document.querySelectorAll('button[data-filter]')],rows=[...document.querySelectorAll('tbody tr')];buttons.forEach(button=>button.addEventListener('click',()=>{{buttons.forEach(item=>item.setAttribute('aria-pressed','false'));button.setAttribute('aria-pressed','true');const value=button.dataset.filter;rows.forEach(row=>row.hidden=value!=='ALL'&&row.dataset.category!==value)}}));</script></body></html>'''
    (OUT / "HR-V0_stop-region-guide.html").write_text(html, encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
