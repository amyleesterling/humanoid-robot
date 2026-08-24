#!/usr/bin/env python3
"""Generate retained neutral-pose actuator-power envelopes for HR-30.

The six exact tangent centerlines are fixed-pose planning evidence only.  A
continuous cable and rigid guard cannot span a moving limb; the joint-local
articulated-power-harness package supersedes that topology.
"""

from __future__ import annotations

import csv
import hashlib
import html
import json
import math
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WHOLE = ROOT / "hr30" / "whole-body-p0.1"
INPUT = WHOLE / "harness" / "distributed-power-harness-successor-p0.1"
POINTS = WHOLE / "harness" / "physical-p0.1" / "route-point-register.csv"
ROUTES = WHOLE / "harness" / "physical-p0.1" / "route-segment-register.csv"
BODY_STEP = WHOLE / "HR-30_body_architecture_candidate.step"
OUT = WHOLE / "harness" / "power-route-guides-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / "harness" / OUT.name
RELEASE_WHOLE = ROOT / "release" / "hr30" / "whole-body-p0.1"
IDENTIFIER = "HR30-POWER-ROUTE-GUIDES-P0.1"
DATE = "2026-08-18"
WARNING = "PRELIMINARY - WHOLE-BODY POWER ROUTE-GUIDE CANDIDATE - NOT APPROVED FOR PROCUREMENT, FABRICATION, CONNECTION, POWERED TESTING, MOTION OR ENERGIZATION"
AUTHORITY = "NO PROCUREMENT, FABRICATION, CONNECTION, POWERED-TEST, MOTION OR ENERGIZATION AUTHORITY"
WHOLE_WARNING = "PRELIMINARY - CONFIGURATION AND PACKAGING CAD ONLY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, POWERED TESTING, MOTION, OR ENERGIZATION"
HARNESS_WARNING = "PRELIMINARY - NOT APPROVED FOR CONNECTION, FABRICATION, MOTION OR ENERGIZATION"
MARKER = "HR30-POWER-ROUTE-GUIDES-P01"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise RuntimeError(f"refusing empty CSV: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def common(row: dict[str, object]) -> dict[str, object]:
    return {**row, "authority": AUTHORITY, "warning": WARNING}


def replace_marker(path: Path, body: str) -> None:
    start = f"<!-- {MARKER}-START -->"
    end = f"<!-- {MARKER}-END -->"
    block = f"{start}\n{body.rstrip()}\n{end}"
    text = path.read_text(encoding="utf-8")
    if start in text and end in text:
        prefix, tail = text.split(start, 1)
        _, suffix = tail.split(end, 1)
        text = prefix.rstrip() + "\n\n" + block + suffix
    elif path.suffix.lower() == ".html" and "</main>" in text:
        text = text.replace("</main>", block + "\n</main>", 1)
    else:
        text = text.rstrip() + "\n\n" + block + "\n"
    path.write_text(text, encoding="utf-8", newline="\n")


def update_manifest_rows(manifest_path: Path, base: Path, changed: list[Path], warning: str) -> None:
    existing = read_csv(manifest_path)
    by_path = {row["path"]: row for row in existing}
    for target in changed:
        relative = target.relative_to(base).as_posix()
        by_path[relative] = {"path": relative, "bytes": str(target.stat().st_size), "sha256": sha(target), "warning": warning}
    ordered = [by_path[row["path"]] for row in existing]
    known = {row["path"] for row in existing}
    ordered.extend(by_path[key] for key in sorted(set(by_path) - known))
    write_csv(manifest_path, ordered)


def parse_xyz(row: dict[str, str]) -> tuple[float, float, float]:
    return float(row["x_mm"]), float(row["y_mm"]), float(row["z_mm"])


def v_sub(a: tuple[float, float, float], b: tuple[float, float, float]) -> tuple[float, float, float]:
    return tuple(a[i] - b[i] for i in range(3))


def v_add(a: tuple[float, float, float], b: tuple[float, float, float]) -> tuple[float, float, float]:
    return tuple(a[i] + b[i] for i in range(3))


def v_mul(a: tuple[float, float, float], scale: float) -> tuple[float, float, float]:
    return tuple(value * scale for value in a)


def dot(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    return sum(a[i] * b[i] for i in range(3))


def norm(a: tuple[float, float, float]) -> float:
    return math.sqrt(dot(a, a))


def unit(a: tuple[float, float, float]) -> tuple[float, float, float]:
    length = norm(a)
    if length <= 0:
        raise RuntimeError("zero vector")
    return tuple(value / length for value in a)


def cross(a: tuple[float, float, float], b: tuple[float, float, float]) -> tuple[float, float, float]:
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def route_geometry() -> tuple[list[dict[str, object]], dict[str, dict[str, object]]]:
    points = {row["point_id"]: parse_xyz(row) for row in read_csv(POINTS)}
    corridor_rows = {row["corridor"]: row for row in read_csv(INPUT / "corridor-architecture.csv")}
    selected = {
        row["segment_id"]: row
        for row in read_csv(ROUTES)
        if row["segment_id"] in corridor_rows
    }
    if set(selected) != set(corridor_rows):
        raise RuntimeError("six corridor bindings required")

    rows: list[dict[str, object]] = []
    geometry: dict[str, dict[str, object]] = {}
    for segment_id in sorted(selected):
        route = selected[segment_id]
        arch = corridor_rows[segment_id]
        p0 = points[route["from_point"]]
        p1 = points[route["to_point"]]
        chord = v_sub(p1, p0)
        chord_length = norm(chord)
        u = unit(chord)
        global_out = (0.0, 1.0, 0.0)
        n_raw = v_sub(global_out, v_mul(u, dot(global_out, u)))
        if norm(n_raw) < 1e-9:
            n_raw = (1.0, 0.0, 0.0)
        n = unit(n_raw)
        plane_normal = unit(cross(u, n))
        radius = float(arch["candidate_required_bend_radius_mm"])
        if chord_length <= 2.0 * radius:
            raise RuntimeError(f"{segment_id}: chord too short for two tangent R{radius} turns")
        straight = chord_length - 2.0 * radius
        route_length = straight + math.pi * radius
        max_od = float(arch["trunk_max_od_mm"])
        control = {
            "start": p0,
            "arc1_mid": v_add(v_add(p0, v_mul(u, radius * (1.0 - 1.0 / math.sqrt(2.0)))), v_mul(n, radius / math.sqrt(2.0))),
            "arc1_end": v_add(v_add(p0, v_mul(u, radius)), v_mul(n, radius)),
            "arc2_start": v_add(v_add(p0, v_mul(u, chord_length - radius)), v_mul(n, radius)),
            "arc2_mid": v_add(v_add(p0, v_mul(u, chord_length - radius + radius / math.sqrt(2.0))), v_mul(n, radius / math.sqrt(2.0))),
            "end": p1,
        }
        geometry[segment_id] = {
            "p0": p0, "p1": p1, "u": u, "n": n, "plane_normal": plane_normal,
            "radius": radius, "max_od": max_od, "control": control,
        }
        rows.append(common({
            "route_id": f"PRG-{segment_id}", "source_corridor": segment_id,
            "trunk_part": arch["successor_trunk"], "axis_count": arch["axis_count"],
            "start_xyz_mm": "{:.3f},{:.3f},{:.3f}".format(*p0),
            "end_xyz_mm": "{:.3f},{:.3f},{:.3f}".format(*p1),
            "outward_unit_vector": "{:.6f},{:.6f},{:.6f}".format(*n),
            "chord_length_mm": f"{chord_length:.3f}",
            "candidate_centerline_length_mm": f"{route_length:.3f}",
            "candidate_max_od_mm": f"{max_od:.4f}",
            "published_dynamic_bend_multiple": "8.0",
            "exact_guide_radius_mm": f"{radius:.4f}",
            "straight_external_spine_mm": f"{straight:.3f}",
            "turn_geometry": "two tangent 90-degree circular turns plus one straight external spine",
            "bend_screen": "PASS GEOMETRIC CENTERLINE RADIUS",
            "diameter_screen": arch["diameter_screen"],
            "route_class": "NEUTRAL-POSE ENVELOPE ONLY - NOT AN ARTICULATED LIMB ROUTE",
            "collision_state": "CONTINUOUS WHOLE-LIMB MOTION ROUTE REJECTED; ARTICULATED SUCCESSOR REQUIRED",
            "state": "DIMENSIONED FIXED-POSE CENTERLINE; NOT ELIGIBLE AS CUT LENGTH, MOVING CABLE OR RIGID GUARD",
        }))
    return rows, geometry


def clamp_rows(route_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for route in route_rows:
        for suffix, station, role in [
            ("A", "0", "fixed-side entry clamp before first circular guide"),
            ("B", "R", "tangent-exit clamp after first circular guide"),
            ("C", "L-R", "tangent-entry clamp before second circular guide"),
            ("D", "L", "fixed-side exit clamp after second circular guide"),
        ]:
            rows.append(common({
                "clamp_id": f"CL-{route['source_corridor']}-{suffix}",
                "route_id": route["route_id"], "station_basis": station, "role": role,
                "candidate_type": "two-piece radiused P-clamp or printed guide saddle; exact part/fasteners SELECTION REQUIRED",
                "minimum_edge_radius": ">= cable OD/2 at received maximum OD; verify manufacturer guidance",
                "retention_rule": "retain without crushing jacket; prevent connector load; service removal without cutting cable",
                "mount_interface": "SELECTION REQUIRED FROM MODULE CAD AND ASSEMBLY ACCESS REVIEW",
                "state": "LOCATED BY ROUTE PARAMETER; PART, PRELOAD, FASTENERS AND PULL TEST OPEN",
            }))
    return rows


def guard_rows(route_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [common({
        "guard_id": f"GD-{row['source_corridor']}", "route_id": row["route_id"],
        "guard_envelope": f"cable maximum OD {row['candidate_max_od_mm']} mm plus minimum 3 mm radial planning clearance",
        "material_candidate": "NONE FOR THIS CONTINUOUS PATH - rigid whole-limb shell rejected",
        "opening_rule": "rigid protection must terminate before every moving axis",
        "service_rule": "superseded by link-local rigid guards plus joint-local flexible bellows",
        "validation": "neutral geometry retained only as planning evidence; use articulated successor for motion architecture",
        "state": "REJECTED AS CONTINUOUS GUARD; ARTICULATED SUCCESSOR REQUIRED",
    }) for row in route_rows]


def source_rows() -> list[dict[str, object]]:
    local = [
        ("PRG-S01", INPUT / "corridor-architecture.csv", "successor trunk/corridor/bend binding"),
        ("PRG-S02", POINTS, "whole-body route endpoint coordinates"),
        ("PRG-S03", ROUTES, "whole-body corridor identifiers and service separation"),
        ("PRG-S04", BODY_STEP, "authoritative complete-body context used in the combined GLB"),
    ]
    rows = [common({
        "source_id": sid, "publisher": "Project Button", "document": scope,
        "revision_or_date": "current whole-body P0.1 input", "official_url_or_path": path.relative_to(ROOT).as_posix(),
        "sha256": sha(path), "verified_scope": scope,
    }) for sid, path, scope in local]
    rows.append(common({
        "source_id": "PRG-S05", "publisher": "Alpha Wire", "document": "Xtra-Guard Flex 86000 product family",
        "revision_or_date": "current official product pages/catalog; accessed 2026-08-18",
        "official_url_or_path": "https://www.alphawire.com/products/cable/xtra-guard-performance-cable/xtra-guard-flex",
        "sha256": "N/A - LIVE PRIMARY SOURCE",
        "verified_scope": "861802/861804/861812 candidate maximum diameters and published 8xd dynamic bend rule; application validation remains open",
    }))
    return rows


def hold_rows() -> list[dict[str, object]]:
    holds = [
        ("PRG-H00", "continuous whole-limb cable/rigid-guard topology", "REJECTED - use the articulated-power-harness package with joint-local tap boards and separate rigid/flexible guards"),
        ("PRG-H01", "full-body pose and collision envelope", "run exact neutral/crouch/weight-transfer/step/fall-restraint sweeps with guards and tether"),
        ("PRG-H02", "external-spine snag and human-contact risk", "rounded guard design plus qualified hazard review and physical mockup"),
        ("PRG-H03", "received cable OD and bend applicability", "supplier CoC/datasheet, received-lot OD, construction and written application disposition"),
        ("PRG-H04", "route cut lengths and service slack", "measure on assembled body through complete joint range; do not use centerline length as cut length"),
        ("PRG-H05", "clamp and guard hardware", "exact parts, materials, fasteners, access, retention, pull/chafe and impact tests"),
        ("PRG-H06", "dynamic flex and torsion life", "motion-spectrum cycling at min/max temperature with post-test electrical and jacket inspection"),
        ("PRG-H07", "connector/breakout loads", "breakout ECAD/mechanical design plus strain relief and connector qualification"),
        ("PRG-H08", "bundle thermal and current derating", "measured duty/current distribution and worst-case enclosed temperature-rise test"),
        ("PRG-H09", "walking and fall-clearance proof", "instrumented restrained walking development with guard-contact monitoring after unpowered sweeps"),
        ("PRG-H10", "qualified electrical/mechanical approval", "signed configuration review after all preceding evidence exists"),
    ]
    return [common({"hold_id": hid, "unresolved_item": item, "evidence_required": evidence, "state": "OPEN", "execution": "NOT EXECUTED"}) for hid, item, evidence in holds]


def make_path(cq, geom: dict[str, object]):
    p0 = geom["p0"]
    u = geom["u"]
    plane_normal = geom["plane_normal"]
    radius = float(geom["radius"])
    chord_length = norm(v_sub(geom["p1"], p0))
    plane = cq.Plane(origin=cq.Vector(*p0), xDir=cq.Vector(*u), normal=cq.Vector(*plane_normal))
    q = radius / math.sqrt(2.0)
    return (
        cq.Workplane(plane)
        .moveTo(0.0, 0.0)
        .threePointArc((radius - q, q), (radius, radius))
        .lineTo(chord_length - radius, radius)
        .threePointArc((chord_length - radius + q, q), (chord_length, 0.0))
        .wire()
    )


def export_cad(geometry: dict[str, dict[str, object]]) -> None:
    import cadquery as cq

    route_assembly = cq.Assembly(name="HR30_POWER_ROUTE_GUIDES_P01")
    combined = cq.Assembly(name="HR30_WHOLE_BODY_POWER_ROUTE_GUIDES_P01")
    body = cq.importers.importStep(str(BODY_STEP)).val()
    combined.add(body, name="HR30_BODY_ARCHITECTURE_REFERENCE", color=cq.Color(0.70, 0.78, 0.84, 0.38))
    palette = [cq.Color(0.95, 0.55, 0.02), cq.Color(0.02, 0.48, 0.82), cq.Color(0.95, 0.72, 0.04), cq.Color(0.08, 0.35, 0.66), cq.Color(0.98, 0.42, 0.05), cq.Color(0.15, 0.58, 0.88)]
    for index, (segment_id, geom) in enumerate(sorted(geometry.items())):
        path = make_path(cq, geom)
        start = geom["p0"]
        u = geom["u"]
        n = geom["n"]
        profile_normal = unit(cross(u, n))
        profile_plane = cq.Plane(origin=cq.Vector(*start), xDir=cq.Vector(*n), normal=cq.Vector(*u))
        cable = cq.Workplane(profile_plane).circle(float(geom["max_od"]) / 2.0).sweep(path, isFrenet=True).val()
        color = palette[index % len(palette)]
        route_assembly.add(cable, name=segment_id, color=color)
        combined.add(cable, name=segment_id, color=color)
        for label, point in [("ENTRY", geom["p0"]), ("EXIT", geom["p1"])]:
            marker = cq.Workplane("XY", origin=point).sphere(float(geom["max_od"]) * 0.75).val()
            route_assembly.add(marker, name=f"{segment_id}_{label}", color=cq.Color(0.95, 0.75, 0.05))
            combined.add(marker, name=f"{segment_id}_{label}", color=cq.Color(0.95, 0.75, 0.05))
    route_assembly.save(str(OUT / "HR-30_power_route_guides_candidate.step"))
    route_assembly.save(str(OUT / "HR-30_power_route_guides_candidate.glb"), tolerance=0.25, angularTolerance=0.18)
    # The combined model is a web inspection view, not a metrology mesh.  A
    # deliberately coarser tessellation keeps GitHub Pages responsive while
    # the exact routes remain available in the route-only STEP.
    combined.save(str(OUT / "HR-30_whole_body_power_routes_candidate.glb"), tolerance=0.55, angularTolerance=0.28)


def svg(route_rows: list[dict[str, object]]) -> str:
    y_positions = {"HN01_R_ARM_POWER": 250, "HN01_R_LEG_POWER": 410, "HN01_TORSO_POWER_SPINE": 570, "HN01_HEAD_POWER_BRANCH": 730, "HN01_L_LEG_POWER": 890, "HN01_L_ARM_POWER": 1050}
    cards = []
    for row in route_rows:
        y = y_positions[row["source_corridor"]]
        radius = float(row["exact_guide_radius_mm"])
        cards.append(f'''<g transform="translate(70 {y})"><rect width="1460" height="120" rx="18" fill="#fff" stroke="#82c4e6" stroke-width="3"/><text x="24" y="32" font-size="20" font-weight="800" fill="#071d36">{html.escape(str(row['source_corridor']))}</text><text x="24" y="64" font-size="16" fill="#24425f">{html.escape(str(row['trunk_part']))} · {row['axis_count']} axes · max OD {row['candidate_max_od_mm']} mm</text><path d="M 520 88 A {radius:.1f} {radius:.1f} 0 0 1 {520+radius:.1f} {88-radius:.1f} H {1260-radius:.1f} A {radius:.1f} {radius:.1f} 0 0 1 1260 88" fill="none" stroke="#f2b91d" stroke-width="12" stroke-linecap="round"/><text x="520" y="108" font-size="15" fill="#0b4f91">two tangent R{radius:.1f} guides · {row['candidate_centerline_length_mm']} mm centerline</text><rect x="1280" y="28" width="150" height="44" rx="22" fill="#dff5e8" stroke="#147348" stroke-width="2"/><text x="1355" y="56" text-anchor="middle" font-size="17" font-weight="800" fill="#0a5b38">RADIUS PASS</text></g>''')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1240" viewBox="0 0 1600 1240" role="img" aria-labelledby="title desc"><title id="title">HR-30 whole-body power route guides</title><desc id="desc">Six dimensioned external guarded trunk candidates with exact tangent bend radii.</desc><rect width="1600" height="1240" fill="#eef8ff"/><text x="70" y="72" font-size="44" font-weight="900" fill="#071d36">Six real routed trunks, not six straight placeholders.</text><text x="70" y="112" font-size="20" fill="#24425f">Each path preserves its P0.1 endpoints and adds two exact tangent circular guides sized at 8× maximum cable OD.</text><rect x="70" y="140" width="1460" height="72" rx="14" fill="#f2b91d" stroke="#805600" stroke-width="3"/><text x="96" y="184" font-size="19" font-weight="900" fill="#17243a">PRELIMINARY · EXTERNAL GUARDED-SPINE CANDIDATE · COLLISION, SNAG, MOTION, CLAMP, THERMAL AND PHYSICAL PROOF OPEN</text>{''.join(cards)}</svg>'''


def html_page(route_rows: list[dict[str, object]], holds: list[dict[str, object]]) -> str:
    table_rows = "".join(f"<tr><td>{html.escape(str(r['source_corridor']))}</td><td>{r['trunk_part']}</td><td>{r['axis_count']}</td><td>{r['candidate_max_od_mm']}</td><td>{r['exact_guide_radius_mm']}</td><td>{r['candidate_centerline_length_mm']}</td><td>{r['bend_screen']}</td></tr>" for r in route_rows)
    hold_cards = "".join(f"<article class=\"hold\"><h3>{html.escape(str(r['hold_id']))}</h3><p><strong>{html.escape(str(r['unresolved_item']))}</strong></p><p>{html.escape(str(r['evidence_required']))}</p></article>" for r in holds)
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 neutral power-route envelopes</title><script type="module" src="../../vendor/model-viewer.min.js"></script><style>:root{{--deep:#071d36;--blue:#0b4f91;--sky:#d9f2ff;--gold:#f2b91d;--paper:#f7fbff;--ink:#142a40;--line:#82c4e6;--red:#982520;--green:#147348}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.55 system-ui,Segoe UI,sans-serif}}header,main,footer{{padding:clamp(24px,5vw,64px) max(18px,calc((100vw - 1280px)/2))}}header,footer{{background:linear-gradient(135deg,var(--deep),var(--blue));color:white}}h1{{font-size:clamp(38px,6vw,70px);line-height:1.04;max-width:19ch}}h2{{font-size:clamp(28px,4vw,44px)}}h3{{font-size:22px}}.warning{{background:var(--gold);color:#17243a;border:3px solid #805600;padding:16px;font-weight:900}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:18px}}article,.panel{{background:white;border:2px solid var(--line);border-radius:16px;padding:19px}}.metric{{font-size:clamp(34px,5vw,54px);font-weight:900;color:var(--blue)}}.pass{{border-color:var(--green)}}.hold{{border-color:var(--red)}}model-viewer{{width:100%;height:min(72vh,760px);min-height:520px;background:linear-gradient(#d9f2ff,#f7fbff);border:2px solid var(--line);border-radius:16px}}.scroll{{overflow:auto;border:2px solid var(--line);border-radius:14px;background:white}}table{{border-collapse:collapse;width:100%;min-width:940px}}th,td{{padding:14px;text-align:left;vertical-align:top;border-bottom:1px solid var(--line);font-size:16px}}th{{background:var(--deep);color:white}}a{{color:#075b9b;font-weight:800}}small{{font-size:14px}}@media(max-width:560px){{body{{font-size:16px}}model-viewer{{min-height:430px}}}}</style></head><body><header><div class="warning">{WARNING}</div><p>HR-30 whole-body P0.1</p><h1>Useful neutral envelopes; rejected as moving-limb routes.</h1><p>These six exact tangent centerlines retain fixed-pose planning evidence. They are not cable cut lengths, and no continuous rigid guard may span a moving joint. The articulated-power-harness package is the current successor.</p></header><main><section class="grid"><article class="pass"><div class="metric">6 / 6</div><p>neutral centerline-radius calculations reproduce</p></article><article class="pass"><div class="metric">12</div><p>exact tangent quarter-circle guides retained</p></article><article class="hold"><div class="metric">0</div><p>routes eligible as articulated whole-limb cables</p></article><article class="hold"><div class="metric">0</div><p>rigid guards allowed to cross moving joints</p></article></section><section><h2>Inspect the retained fixed-pose geometry</h2><model-viewer src="HR-30_whole_body_power_routes_candidate.glb" alt="Interactive complete HR-30 with six retained neutral-pose actuator-power route envelopes" camera-controls camera-orbit="28deg 78deg 112%" field-of-view="28deg" shadow-intensity="0.85" exposure="1.05"></model-viewer><p><a href="HR-30_power_route_guides_candidate.step">Neutral-envelope STEP</a> · <a href="route-centerline-register.csv">Exact route register</a> · <a href="../articulated-power-harness-p0.1/index.html">current articulated successor</a></p></section><section><h2>The corrected boundary</h2><div class="panel hold"><p>A shoulder, elbow, wrist, hip, knee, ankle, neck or waist changes the relative pose of adjacent links. A continuous rigid shell spanning that axis would lock or collide with the joint. The successor uses rigid link-local channels that stop before the axis and flexible joint-local bellows around smaller flat-cable segments.</p></div></section><section><h2>Dimensioned neutral centerlines</h2><div class="scroll"><table><thead><tr><th>Corridor</th><th>Cable</th><th>Axes</th><th>Max OD mm</th><th>Guide R mm</th><th>Centerline mm</th><th>Screen</th></tr></thead><tbody>{table_rows}</tbody></table></div></section><section><h2>Open or rejected items</h2><div class="grid">{hold_cards}</div></section></main><footer>{WARNING}</footer></body></html>'''
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 whole-body power route guides</title><script type="module" src="../../vendor/model-viewer.min.js"></script><style>:root{{--deep:#071d36;--blue:#0b4f91;--sky:#d9f2ff;--gold:#f2b91d;--paper:#f7fbff;--ink:#142a40;--line:#82c4e6;--red:#982520;--green:#147348}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.55 system-ui,Segoe UI,sans-serif}}header,main,footer{{padding:clamp(24px,5vw,64px) max(18px,calc((100vw - 1280px)/2))}}header,footer{{background:linear-gradient(135deg,var(--deep),var(--blue));color:white}}h1{{font-size:clamp(38px,6vw,70px);line-height:1.04;max-width:18ch}}h2{{font-size:clamp(28px,4vw,44px)}}h3{{font-size:22px}}.warning{{background:var(--gold);color:#17243a;border:3px solid #805600;padding:16px;font-weight:900}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:18px}}article,.panel{{background:white;border:2px solid var(--line);border-radius:16px;padding:19px}}.metric{{font-size:clamp(34px,5vw,54px);font-weight:900;color:var(--blue)}}.pass{{border-color:var(--green)}}.hold{{border-color:var(--red)}}img{{max-width:100%;height:auto;border:2px solid var(--line);border-radius:16px}}model-viewer{{width:100%;height:min(72vh,760px);min-height:520px;background:linear-gradient(#d9f2ff,#f7fbff);border:2px solid var(--line);border-radius:16px}}.scroll{{overflow:auto;border:2px solid var(--line);border-radius:14px;background:white}}table{{border-collapse:collapse;width:100%;min-width:940px}}th,td{{padding:14px;text-align:left;vertical-align:top;border-bottom:1px solid var(--line);font-size:16px}}th{{background:var(--deep);color:white;position:sticky;top:0}}a{{color:#075b9b;font-weight:800}}small{{font-size:14px}}@media(max-width:560px){{body{{font-size:16px}}model-viewer{{min-height:430px}}}}</style></head><body><header><div class="warning">{WARNING}</div><p>HR-30 whole-body P0.1</p><h1>The power trunks now have real geometry.</h1><p>Six straight corridor placeholders have been replaced by editable tangent route centerlines. Each trunk leaves the body, follows a guarded external spine, and returns without violating the candidate cable's published 8× maximum-OD bend rule.</p></header><main><section class="grid"><article class="pass"><div class="metric">6 / 6</div><p>dimensioned centerline-radius screens pass</p></article><article class="pass"><div class="metric">12</div><p>exact tangent quarter-circle guides</p></article><article><div class="metric">24</div><p>parameter-located clamp obligations</p></article><article class="hold"><div class="metric">0</div><p>executed whole-body collision or walking sweeps</p></article></section><section><h2>Rotate the complete robot and inspect the routes</h2><model-viewer src="HR-30_whole_body_power_routes_candidate.glb" alt="Interactive complete HR-30 humanoid with six colored external actuator-power route candidates" camera-controls camera-orbit="28deg 78deg 112%" field-of-view="28deg" shadow-intensity="0.85" exposure="1.05"></model-viewer><p><a href="HR-30_power_route_guides_candidate.step">Editable route-guide STEP</a> · <a href="HR-30_power_route_guides_candidate.glb">Route-only GLB</a> · <a href="route-centerline-register.csv">Exact route register</a></p></section><section><h2>What changed</h2><img src="power-route-guides.svg" alt="Six HR-30 trunk route cards showing exact maximum cable diameters and bend radii"><div class="panel"><p>The paths use a shared construction: a 90-degree circular entry guide, a straight external spine, and a 90-degree circular exit guide. The arcs are tangent to the spine and use the cable-specific minimum planning radius. The centerline length is a CAD result—not a production cut length.</p></div></section><section><h2>Dimensioned centerlines</h2><div class="scroll"><table><thead><tr><th>Corridor</th><th>Cable</th><th>Axes</th><th>Max OD mm</th><th>Guide R mm</th><th>Centerline mm</th><th>Screen</th></tr></thead><tbody>{table_rows}</tbody></table></div></section><section><h2>The remaining work is physical, not cosmetic</h2><div class="grid">{hold_cards}</div></section><section><h2>Controlled artifacts</h2><div class="panel"><p><a href="route-centerline-register.csv">Centerlines</a> · <a href="clamp-obligation-register.csv">Clamps</a> · <a href="guard-envelope-register.csv">Guards</a> · <a href="open-holds.csv">Open holds</a> · <a href="primary-source-register.csv">Sources</a> · <a href="status.json">Status</a></p><small>No route is released for cutting, connection, motion or energization.</small></div></section></main><footer>{WARNING}</footer></body></html>'''


def integrate_parent_guides() -> None:
    harness_readme = WHOLE / "harness" / "README.md"
    harness_index = WHOLE / "harness" / "index.html"
    body_readme = WHOLE / "README.md"
    body_index = WHOLE / "index.html"
    replace_marker(harness_readme, """## Whole-body power route guides

The [interactive power-route guide](power-route-guides-p0.1/index.html) replaces all six straight actuator-power corridor placeholders with editable tangent 3D centerlines. Twelve exact circular turns satisfy the selected trunks' 8x maximum-OD planning rule. The routes are external guarded-spine candidates; guard CAD, clamps, cut lengths, pose/fall/walking collision sweeps, thermal/flex tests and every powered-work authority remain open.""")
    replace_marker(harness_index, """<section id="power-route-guides"><h2>The six actuator-power trunks now have actual 3D centerlines</h2><div class="grid"><article><h3>6 / 6 route screens</h3><p>Every trunk now has two tangent circular guides at the candidate cable's 8x maximum-OD radius.</p></article><article><h3>External guarded spines</h3><p>The routes are visible, dimensioned and serviceable instead of being hidden straight-line placeholders.</p></article><article><h3>24 clamp obligations</h3><p>Entry, tangent-exit, tangent-entry and final-exit restraints are parameter-located for every trunk.</p></article><article><h3>Physical proof remains open</h3><p>Guards, snag controls, full-pose collision, walking, thermal, flex-life and cut-length evidence are not executed.</p></article></div><p><a href="power-route-guides-p0.1/index.html">Open the interactive whole-body power-route guide.</a></p></section>""")
    replace_marker(body_readme, """## Routed whole-body power trunks

The [whole-body power-route guide](harness/power-route-guides-p0.1/index.html) adds actual 3D tangent centerlines to all six actuator-power trunks. The complete robot is visible with the six external guarded-spine candidates, and the editable route-only STEP preserves every source endpoint. Geometry passes the cable-radius screen; collision, guard, clamp, thermal, motion and physical validation remain open.""")
    replace_marker(body_index, """<section id="power-route-guides"><h2>The power harness is now visible on the complete humanoid</h2><div class="grid"><article class="card pass"><div class="metric">6 / 6</div><p>trunk centerline-radius screens pass</p></article><article class="card pass"><div class="metric">12</div><p>exact tangent circular guides</p></article><article class="card pass"><div class="metric">24</div><p>parameter-located clamp obligations</p></article><article class="card hold"><div class="metric">0</div><p>executed collision, walking or physical route tests</p></article></div><div class="viewer"><model-viewer src="harness/power-route-guides-p0.1/HR-30_whole_body_power_routes_candidate.glb" poster="front-elevation.svg" alt="Interactive complete HR-30 with six colored power-route candidates" camera-controls shadow-intensity="0.8" exposure="1.05"></model-viewer><p><a href="harness/power-route-guides-p0.1/index.html">Open the interactive route guide</a> · <a href="harness/power-route-guides-p0.1/HR-30_power_route_guides_candidate.step">route STEP</a> · <a href="harness/power-route-guides-p0.1/route-centerline-register.csv">dimensions</a>.</p></div></section>""")

    # Correct the presentation boundary with the same idempotent marker.
    replace_marker(harness_readme, """## Neutral whole-body power-route envelopes

The [neutral power-route guide](power-route-guides-p0.1/index.html) retains six editable tangent 3D centerlines as fixed-pose planning evidence. The continuous whole-limb cable/rigid-guard topology is rejected; use the articulated-power-harness successor for moving joints.""")
    replace_marker(harness_index, """<section id="power-route-guides"><h2>Six neutral route envelopes remain as controlled evidence</h2><div class="grid"><article><h3>6 / 6 neutral calculations</h3><p>The fixed-pose tangent-radius calculations reproduce.</p></article><article><h3>0 articulated routes</h3><p>No continuous whole-limb path is eligible to cross a moving joint.</p></article><article><h3>Rigid guards stop at joints</h3><p>The successor separates rigid link channels from flexible joint bellows.</p></article><article><h3>Historical geometry retained</h3><p>The STEP and GLB remain useful for endpoint traceability.</p></article></div><p><a href="power-route-guides-p0.1/index.html">Open the retained neutral-envelope guide.</a></p></section>""")
    replace_marker(body_readme, """## Retained neutral power-route envelopes

The [neutral-route guide](harness/power-route-guides-p0.1/index.html) retains the earlier tangent centerlines as controlled fixed-pose evidence. They are explicitly rejected as continuous moving-limb routes; the articulated-power-harness package is authoritative for joint-by-joint routing.""")
    replace_marker(body_index, """<section id="power-route-guides"><h2>The former whole-limb route is retained—and rejected for motion</h2><div class="grid"><article class="card pass"><div class="metric">6 / 6</div><p>neutral radius calculations reproduce</p></article><article class="card pass"><div class="metric">12</div><p>exact tangent guides retained</p></article><article class="card hold"><div class="metric">0</div><p>continuous paths eligible across moving joints</p></article><article class="card hold"><div class="metric">0</div><p>rigid guards allowed to span a joint</p></article></div><p><a href="harness/power-route-guides-p0.1/index.html">Open the retained neutral-envelope guide.</a> The articulated-power-harness section contains the current successor.</p></section>""")

    harness_manifest = WHOLE / "harness" / "file-manifest.csv"
    update_manifest_rows(harness_manifest, WHOLE / "harness", [harness_readme, harness_index], HARNESS_WARNING)
    package_files = sorted(p for p in OUT.iterdir() if p.is_file())
    update_manifest_rows(WHOLE / "file-manifest.csv", WHOLE, [body_readme, body_index, harness_readme, harness_index, harness_manifest, *package_files], WHOLE_WARNING)

    RELEASE_WHOLE.mkdir(parents=True, exist_ok=True)
    for source in [body_readme, body_index, WHOLE / "file-manifest.csv"]:
        shutil.copy2(source, RELEASE_WHOLE / source.name)
    release_harness = RELEASE_WHOLE / "harness"
    release_harness.mkdir(parents=True, exist_ok=True)
    for source in [harness_readme, harness_index, harness_manifest]:
        shutil.copy2(source, release_harness / source.name)


def manifest() -> None:
    rows = []
    for path in sorted(p for p in OUT.iterdir() if p.is_file() and p.name != "file-manifest.csv"):
        rows.append({"path": path.name, "bytes": path.stat().st_size, "sha256": sha(path), "warning": WARNING})
    write_csv(OUT / "file-manifest.csv", rows)


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    route_rows, geometry = route_geometry()
    clamps = clamp_rows(route_rows)
    guards = guard_rows(route_rows)
    holds = hold_rows()
    write_csv(OUT / "route-centerline-register.csv", route_rows)
    write_csv(OUT / "clamp-obligation-register.csv", clamps)
    write_csv(OUT / "guard-envelope-register.csv", guards)
    write_csv(OUT / "open-holds.csv", holds)
    write_csv(OUT / "primary-source-register.csv", source_rows())
    export_cad(geometry)
    (OUT / "power-route-guides.svg").write_text(svg(route_rows), encoding="utf-8", newline="\n")
    (OUT / "index.html").write_text(html_page(route_rows, holds), encoding="utf-8", newline="\n")
    (OUT / "README.md").write_text(f"# HR-30 neutral power-route envelopes P0.1\n\n{WARNING}\n\nThis package retains six fixed-pose tangent centerlines as planning evidence. It is rejected as a continuous articulated cable/rigid-guard topology; use ../articulated-power-harness-p0.1/.\n", encoding="utf-8", newline="\n")
    (OUT / "status.json").write_text(json.dumps({
        "identifier": IDENTIFIER, "date": DATE, "warning": WARNING,
        "route_count": len(route_rows), "exact_circular_turn_count": len(route_rows) * 2,
        "clamp_obligation_count": len(clamps), "geometric_radius_screens_pass": len(route_rows),
        "combined_whole_body_glb_complete": True, "editable_route_step_complete": True,
        "neutral_pose_geometry_only": True, "articulated_route_eligible_count": 0,
        "continuous_whole_limb_rigid_guard_rejected": True,
        "guard_solids_complete": False, "collision_sweeps_complete": False,
        "walking_clearance_complete": False, "physical_validation_complete": False,
        "fabrication_authority": False, "connection_authority": False,
        "powered_test_authority": False, "motion_authority": False, "energization_authority": False,
    }, indent=2) + "\n", encoding="utf-8", newline="\n")
    shutil.copy2(__file__, OUT / "power-route-guides-source.py")
    manifest()
    if RELEASE.exists():
        shutil.rmtree(RELEASE)
    RELEASE.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(OUT, RELEASE)
    integrate_parent_guides()


if __name__ == "__main__":
    main()
