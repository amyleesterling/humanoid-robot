#!/usr/bin/env python3
"""Generate the HR-30 distributed actuator-power harness successor.

This is a physical architecture candidate.  It replaces the impossible bundle
of 25 individual jacketed power cables with local protected distribution nodes,
multi-core limb trunks, and one two-core branch at each actuator.  It does not
release protection values, cable cutting, fabrication, connection, or power.
"""

from __future__ import annotations

import csv
import hashlib
import html
import json
import math
import shutil
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WHOLE = ROOT / "hr30" / "whole-body-p0.1"
POLICY = WHOLE / "harness" / "current-policy-binding-p0.1" / "axis-power-policy-binding.csv"
ROUTES = WHOLE / "harness" / "physical-p0.1" / "route-segment-register.csv"
ROUTE_GUIDES = WHOLE / "harness" / "power-route-guides-p0.1" / "route-centerline-register.csv"
OUT = WHOLE / "harness" / "distributed-power-harness-successor-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / "harness" / OUT.name
RELEASE_WHOLE = ROOT / "release" / "hr30" / "whole-body-p0.1"
IDENTIFIER = "HR30-DISTRIBUTED-POWER-HARNESS-SUCCESSOR-P0.1"
DATE = "2026-08-18"
WARNING = "PRELIMINARY - DISTRIBUTED ACTUATOR-POWER HARNESS CANDIDATE - NOT APPROVED FOR PROCUREMENT, FABRICATION, CONNECTION, POWERED TESTING, MOTION OR ENERGIZATION"
AUTHORITY = "NO PROCUREMENT, FABRICATION, CONNECTION, POWERED-TEST, MOTION OR ENERGIZATION AUTHORITY"
WHOLE_WARNING = "PRELIMINARY - CONFIGURATION AND PACKAGING CAD ONLY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, POWERED TESTING, MOTION, OR ENERGIZATION"
HARNESS_WARNING = "PRELIMINARY - NOT APPROVED FOR CONNECTION, FABRICATION, MOTION OR ENERGIZATION"
MARKER = "HR30-DISTRIBUTED-POWER-HARNESS-P01"


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
    """Replace one generated section, or insert it before </main>/at EOF."""
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
    """Update or append exact changed files without rewriting unrelated evidence."""
    existing = read_csv(manifest_path)
    by_path = {row["path"]: row for row in existing}
    for target in changed:
        relative = target.relative_to(base).as_posix()
        by_path[relative] = {
            "path": relative,
            "bytes": str(target.stat().st_size),
            "sha256": sha(target),
            "warning": warning,
        }
    ordered = [by_path[row["path"]] for row in existing]
    known = {row["path"] for row in existing}
    ordered.extend(by_path[key] for key in sorted(set(by_path) - known))
    write_csv(manifest_path, ordered)


def integrate_parent_guides() -> None:
    harness_readme = WHOLE / "harness" / "README.md"
    harness_index = WHOLE / "harness" / "index.html"
    body_readme = WHOLE / "README.md"
    body_index = WHOLE / "index.html"
    replace_marker(harness_readme, """## Distributed actuator-power successor

The [interactive distributed-power guide](distributed-power-harness-successor-p0.1/index.html) rejects the physically impossible one-jacketed-cable-per-axis bundle. Six local protected nodes feed exact Alpha Wire 12-, 4-, and 2-core candidate trunks with an explicit protected pair for every one of the 25 axes. All six trunk diameter screens fit, and all six now bind to the dimensioned tangent guides in the whole-body route CAD. Protection devices, breakout ECAD, guard and collision sweeps, thermal validation and every powered-work authority remain open.""")
    replace_marker(harness_index, """<section id="distributed-power-harness"><h2>The actuator-power trunks now fit their routed corridors</h2><div class="grid"><article><h3>25 protected pairs</h3><p>Every actuator retains a dedicated positive and return pair with explicit trunk cores and cavities.</p></article><article><h3>6 local nodes</h3><p>Protection moves to the pelvis, shoulder roots, waist bay and neck base.</p></article><article><h3>6 / 6 diameter screens</h3><p>The multi-core trunk candidate fits every circular corridor screen.</p></article><article><h3>6 / 6 routed bend screens</h3><p>Every trunk binds to two dimensioned tangent circular guides at the cable-specific planning radius.</p></article></div><p><a href="distributed-power-harness-successor-p0.1/index.html">Open the distributed-power harness guide.</a></p></section>""")
    replace_marker(body_readme, """## Distributed whole-body actuator power

The [distributed-power harness successor](harness/distributed-power-harness-successor-p0.1/index.html) replaces the rejected 25-jacket corridor bundle with six local protected distribution nodes and multi-core limb trunks. It binds a dedicated protected core pair to every axis and exact cable/terminal candidates. All six diameter screens and all six dimensioned route-guide radius screens pass; protection electronics, breakout ECAD, guards, full-pose collision sweeps and thermal tests remain open.""")
    replace_marker(body_index, """<section id="distributed-power-harness"><h2>A physically routed power architecture for all 25 axes</h2><div class="grid"><article class="card pass"><div class="metric">25</div><p>explicit protected conductor pairs</p></article><article class="card pass"><div class="metric">6 / 6</div><p>multi-core trunk diameter screens pass</p></article><article class="card"><div class="metric">6</div><p>local distribution nodes across the whole body</p></article><article class="card pass"><div class="metric">6 / 6</div><p>dimensioned tangent route-guide radius screens pass</p></article></div><p><a href="harness/distributed-power-harness-successor-p0.1/index.html">Open the interactive distributed-power harness guide.</a> Guarding, full-pose collision, thermal and physical validation remain open.</p></section>""")

    harness_manifest = WHOLE / "harness" / "file-manifest.csv"
    update_manifest_rows(harness_manifest, WHOLE / "harness", [harness_readme, harness_index], HARNESS_WARNING)
    package_files = sorted(p for p in OUT.iterdir() if p.is_file())
    update_manifest_rows(
        WHOLE / "file-manifest.csv",
        WHOLE,
        [body_readme, body_index, harness_readme, harness_index, harness_manifest, *package_files],
        WHOLE_WARNING,
    )

    RELEASE_WHOLE.mkdir(parents=True, exist_ok=True)
    for source in [body_readme, body_index, WHOLE / "file-manifest.csv"]:
        shutil.copy2(source, RELEASE_WHOLE / source.name)
    release_harness = RELEASE_WHOLE / "harness"
    release_harness.mkdir(parents=True, exist_ok=True)
    for source in [harness_readme, harness_index, harness_manifest]:
        shutil.copy2(source, release_harness / source.name)


def cable_specs() -> dict[str, dict[str, float | int | str]]:
    return {
        "861802": {"cores": 2, "awg": 18, "nominal_od_mm": 5.3340, "max_od_mm": 5.5880, "dcr_ohm_per_1000ft": 6.9, "dcr_ohm_per_km": 22.637795276, "bend_multiple": 8.0, "bend_radius_max_od_mm": 44.7040},
        "861804": {"cores": 4, "awg": 18, "nominal_od_mm": 6.0198, "max_od_mm": 6.2992, "dcr_ohm_per_1000ft": 6.9, "dcr_ohm_per_km": 22.637795276, "bend_multiple": 8.0, "bend_radius_max_od_mm": 50.3936},
        "861812": {"cores": 12, "awg": 18, "nominal_od_mm": 8.9408, "max_od_mm": 9.3472, "dcr_ohm_per_1000ft": 7.0, "dcr_ohm_per_km": 22.965879265, "bend_multiple": 8.0, "bend_radius_max_od_mm": 74.7776},
    }


def source_rows() -> list[dict[str, object]]:
    local = []
    for sid, path, role in [
        ("DPH-S01", POLICY, "25-axis current-cap and route-length binding"),
        ("DPH-S02", ROUTES, "whole-body corridor diameters and bend reservations"),
        ("DPH-S12", ROUTE_GUIDES, "dimensioned whole-body tangent route-guide geometry"),
    ]:
        local.append(common({"source_id": sid, "publisher": "Project Button", "document": role, "revision_or_date": "current P0.1 input", "official_url_or_path": path.relative_to(ROOT).as_posix(), "sha256": sha(path), "verified_scope": role}))
    official = [
        ("DPH-S03", "Alpha Wire", "861802 product page", "live official page; accessed 2026-08-18", "https://www.alphawire.com/products/cable/xtra-guard-performance-cable/xtra-guard-flex/861802", "2C 18 AWG; 0.210 +/- 0.010 in OD; 0.063 in core OD; 6.9 ohm/1000 ft nominal DCR at 20 C; 8xd bend; +5 to 105 C dynamic; 86000 family up to six million flex cycles"),
        ("DPH-S04", "Alpha Wire", "861804 product page", "live official page; accessed 2026-08-18", "https://www.alphawire.com/products/cable/xtra-guard-performance-cable/xtra-guard-flex/861804", "4C 18 AWG; 0.237 +/- 0.011 in OD; 6.9 ohm/1000 ft nominal DCR at 20 C; 8xd bend; +5 to 105 C dynamic"),
        ("DPH-S05", "Alpha Wire", "861812 customer specification", "live official PDF; accessed 2026-08-18; page revision not stated", "https://www.alphawire.com/disteAPI/SpecPDF/DownloadProductSpecPdf?productPartNumber=861812", "12C 18 AWG; 0.352 +/- 0.016 in OD; 0.063 in core OD; unshielded construction"),
        ("DPH-S06", "Alpha Wire", "Xtra-Guard Flex catalog", "current official catalog; accessed 2026-08-18", "https://www.alphawire.com/-/media/project/alphawire/alphawire/files/brochures/al_xgflexcatalog.pdf?rev=-1", "861812 12C 18 AWG continuous-flex family; nominal conductor DCR 7.0 ohm/1000 ft at 20 C; 8xd bend; +5 to 105 C dynamic"),
        ("DPH-S07", "Molex", "Micro-Fit 3.0 single-row product specification PS-43650", "revision N4; 2025-11-21", "https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/productspecificationpdf/436/43650/PS-43650-001.pdf", "18 AWG wire up to 1.85 mm insulation OD; 2-circuit wire-to-wire reference 7 A/contact at <=30 C rise; 12-circuit reference 6.5 A/contact; application derating required"),
        ("DPH-S08", "Molex", "43030 female-terminal series", "live official series page; accessed 2026-08-18", "https://www.molex.com/en-us/products/series-chart/43030", "430300038 tin-plated female terminal for 18 AWG and 1.85 mm maximum insulation OD"),
        ("DPH-S09", "Molex", "43031 male-terminal series", "live official series page; accessed 2026-08-18", "https://www.molex.com/en-us/products/series-chart/43031", "430310021 tin-plated male terminal for 18 AWG and 1.85 mm maximum insulation OD"),
        ("DPH-S10", "Molex", "43020 12-circuit panel plug", "live official product page; accessed 2026-08-18", "https://www.molex.com/en-us/products/part-detail/430201200", "430201200 is a 12-circuit dual-row polarized locking panel-mount plug"),
        ("DPH-S11", "Molex", "43025 receptacle sales drawing", "official sales drawing; accessed 2026-08-18", "https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/salesdrawingpdf/430/43025/430250200_sd.pdf", "43025-1200 is the mating 12-circuit receptacle housing for 43020 and uses 43030 female terminals"),
    ]
    local.extend(common({"source_id": sid, "publisher": pub, "document": doc, "revision_or_date": rev, "official_url_or_path": url, "sha256": "N/A - LIVE PRIMARY SOURCE", "verified_scope": scope}) for sid, pub, doc, rev, url, scope in official)
    return local


def cable_rows(specs: dict[str, dict[str, object]]) -> list[dict[str, object]]:
    use = {"861802": "one protected pair at a local actuator branch or waist feed", "861804": "two protected pairs in the head branch", "861812": "six protected pairs in each leg; five protected pairs plus two isolated spares in each arm"}
    return [common({
        "part_number": part, "service": use[part], "conductors": spec["cores"], "conductor_awg": spec["awg"],
        "core_od_nominal_mm": "1.6002", "cable_od_nominal_mm": f"{float(spec['nominal_od_mm']):.4f}", "cable_od_max_mm": f"{float(spec['max_od_mm']):.4f}",
        "nominal_dcr_20c_ohm_per_1000ft": spec["dcr_ohm_per_1000ft"], "nominal_dcr_20c_ohm_per_km": f"{float(spec['dcr_ohm_per_km']):.9f}",
        "dynamic_bend_multiple": spec["bend_multiple"], "planning_min_radius_using_max_od_mm": f"{float(spec['bend_radius_max_od_mm']):.4f}",
        "dynamic_temperature_c": "+5 to +105", "family_flex_life": "86000 family rated up to 6 million flex cycles; exact HR-30 motion spectrum not validated",
        "candidate_state": "GEOMETRIC/ELECTRICAL CANDIDATE - RECEIVED LOT, CRIMP, BUNDLE, MOTION AND TEMPERATURE VALIDATION OPEN",
    }) for part, spec in specs.items()]


def group_for_axis(axis: dict[str, str]) -> tuple[str, str, str]:
    bus = axis["bus_id"]
    if bus == "RS-LLEG": return "HN01_L_LEG_POWER", "DP-LLEG", "861812"
    if bus == "RS-RLEG": return "HN01_R_LEG_POWER", "DP-RLEG", "861812"
    if bus in {"RS-LARM", "TTL-LDIST"}: return "HN01_L_ARM_POWER", "DP-LARM", "861812"
    if bus in {"RS-RARM", "TTL-RDIST"}: return "HN01_R_ARM_POWER", "DP-RARM", "861812"
    if bus == "TTL-HEAD": return "HN01_HEAD_POWER_BRANCH", "DP-HEAD", "861804"
    if bus == "RS-WAIST": return "HN01_TORSO_POWER_SPINE", "DP-WAIST", "861802"
    raise RuntimeError(f"unmapped bus {bus}")


def build_rows(specs: dict[str, dict[str, object]]) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    axes = read_csv(POLICY)
    route_map = {r["segment_id"]: r for r in read_csv(ROUTES) if r["segment_kind"] == "FIXED BODY CORRIDOR"}
    guide_map = {r["source_corridor"]: r for r in read_csv(ROUTE_GUIDES)}
    if len(axes) != 25:
        raise RuntimeError("25 axes required")
    if len(guide_map) != 6 or not set(guide_map).issubset(route_map):
        raise RuntimeError("six power route-guide identities must map to physical corridors")
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    axis_rows: list[dict[str, object]] = []
    drop_rows: list[dict[str, object]] = []
    pair_counter: dict[str, int] = defaultdict(int)
    core_colors = {1:"BLACK", 2:"RED", 3:"WHITE", 4:"GREEN", 5:"ORANGE", 6:"BLUE", 7:"BROWN", 8:"YELLOW", 9:"VIOLET", 10:"SLATE", 11:"PINK", 12:"TAN"}
    copper_alpha = 0.00393
    for axis in axes:
        corridor, node, trunk = group_for_axis(axis)
        grouped[corridor].append(axis)
        pair_counter[corridor] += 1
        pair_index = pair_counter[corridor]
        return_core = pair_index * 2 - 1
        vdd_core = pair_index * 2
        cap = float(axis["candidate_internal_limit_a"])
        rt_m = float(axis["round_trip_planning_length_mm"]) / 1000.0
        dcr20 = float(specs[trunk]["dcr_ohm_per_km"]) / 1000.0
        r20 = dcr20 * rt_m
        r80 = r20 * (1.0 + copper_alpha * 60.0)
        axis_rows.append(common({
            "axis_id": axis["axis_id"], "bus_id": axis["bus_id"], "distribution_node": node, "corridor": corridor, "trunk_part": trunk,
            "core_pair": f"PAIR {pair_index}: core/cavity {return_core} {core_colors[return_core]}=RETURN; core/cavity {vdd_core} {core_colors[vdd_core]}=VDD", "local_branch_part": "Alpha Wire 861802",
            "candidate_current_cap_a": f"{cap:.6f}", "published_stall_endpoint_a": axis["published_stall_endpoint_a"], "stall_is_normal_demand": "NO",
            "one_way_planning_length_mm": axis["one_way_planning_length_mm"], "round_trip_planning_length_mm": axis["round_trip_planning_length_mm"],
            "nominal_cable_only_loop_r20_ohm": f"{r20:.8f}", "nominal_cable_only_loop_r80_ohm": f"{r80:.8f}",
            "cap_drop_20c_v": f"{cap*r20:.8f}", "cap_drop_80c_v": f"{cap*r80:.8f}", "cap_loss_80c_w": f"{cap*cap*r80:.8f}",
            "calculation_boundary": "NOMINAL ALPHA DCR AND EXISTING STRAIGHT-LINE PLANNING LENGTH ONLY; CONNECTORS, PIGTAIL, BREAKOUT, REGENERATION, DUTY AND SERVICE-LOOP LENGTH EXCLUDED",
            "branch_protection": "LOCAL ELECTRONIC BRANCH CHANNEL - VALUES/COMPONENTS SELECTION REQUIRED",
            "state": "CANDIDATE CORE ALLOCATION; NOT CUT OR CONNECTED",
        }))
        drop_rows.append(common({
            "axis_id": axis["axis_id"], "distribution_node": node, "incoming_trunk": trunk, "breakout_interface": "12-circuit Micro-Fit for 861812; 4-circuit Micro-Fit for 861804; 2-circuit Micro-Fit for 861802",
            "candidate_terminal_female": "430300038", "candidate_terminal_male": "430310021", "local_pair": "861802 2C 18 AWG",
            "actuator_pigtail": "Alpha Wire 3051 22 AWG to JST EH; restrained and non-flexing",
            "polarity": f"incoming cavity {return_core} {core_colors[return_core]}=RETURN; cavity {vdd_core} {core_colors[vdd_core]}=VDD; local 861802 BLACK=RETURN/RED=VDD", "serviceability": "connectorized breakout board; no jacket mid-span splice",
            "state": "PHYSICAL SUCCESSOR CONCEPT - PCB, HOUSING SIZE, CLAMP AND ACTUATOR-END LENGTH OPEN",
        }))
    corridor_rows: list[dict[str, object]] = []
    node_rows: list[dict[str, object]] = []
    for corridor, member_axes in sorted(grouped.items()):
        route = route_map[corridor]
        _, node, trunk = group_for_axis(member_axes[0])
        spec = specs[trunk]
        count = len(member_axes)
        old_fill = count * (float(specs["861802"]["max_od_mm"]) / float(route["corridor_diameter_mm"])) ** 2
        if count == 1:
            old_packing = float(specs["861802"]["max_od_mm"]) <= float(route["corridor_diameter_mm"])
            packing_basis = "single circular cable diameter"
        elif count == 2:
            old_packing = 2.0 * float(specs["861802"]["max_od_mm"]) <= float(route["corridor_diameter_mm"])
            packing_basis = "exact two-equal-circle minimum enclosing diameter = 2d"
        else:
            old_packing = old_fill <= 1.0
            packing_basis = "area lower bound only; area > 1 proves impossible"
        new_fill = (float(spec["max_od_mm"]) / float(route["corridor_diameter_mm"])) ** 2
        bend_reserved = float(route["minimum_bend_radius_mm"])
        bend_required = float(spec["bend_radius_max_od_mm"])
        guide = guide_map[corridor]
        guide_radius = float(guide["exact_guide_radius_mm"])
        if guide["trunk_part"] != trunk or int(guide["axis_count"]) != count:
            raise RuntimeError(f"route-guide allocation drift: {corridor}")
        corridor_rows.append(common({
            "corridor": corridor, "axis_count": count, "protected_core_count": count*2, "old_individual_861802_bundle_fill_ratio": f"{old_fill:.6f}",
            "old_bundle_geometric_result": "FAIL" if not old_packing else "PASS LOWER-BOUND SCREEN ONLY", "old_bundle_packing_basis": packing_basis, "successor_trunk": trunk, "trunk_core_count": spec["cores"],
            "spare_cores": int(spec["cores"]) - count*2, "corridor_diameter_mm": route["corridor_diameter_mm"], "trunk_max_od_mm": f"{float(spec['max_od_mm']):.4f}",
            "trunk_area_fill_ratio": f"{new_fill:.6f}", "diameter_screen": "PASS GEOMETRIC AREA" if float(spec["max_od_mm"]) < float(route["corridor_diameter_mm"]) else "FAIL",
            "legacy_straight_reservation_radius_mm": f"{bend_reserved:.4f}", "candidate_required_bend_radius_mm": f"{bend_required:.4f}",
            "integrated_route_guide_radius_mm": f"{guide_radius:.4f}", "integrated_route_geometry": guide["turn_geometry"],
            "route_guide_id": guide["route_id"], "route_guide_centerline_length_mm": guide["candidate_centerline_length_mm"],
            "bend_screen": "PASS ROUTE-GUIDE GEOMETRY" if guide_radius >= bend_required else "FAIL - ROUTE TURN/GUIDE GEOMETRY MUST CHANGE",
            "installation_clearance": "OPEN - AREA/DIAMETER SCREEN IS NOT A PULL, CLAMP, CHAFE OR TOLERANCE RELEASE",
        }))
        node_rows.append(common({
            "node_id": node, "location": {"DP-LLEG":"left pelvis/hip root", "DP-RLEG":"right pelvis/hip root", "DP-LARM":"left shoulder root", "DP-RARM":"right shoulder root", "DP-HEAD":"torso/neck base", "DP-WAIST":"pelvis waist bay"}[node],
            "channel_count": count, "axes": "; ".join(a["axis_id"] for a in member_axes), "upstream_feed": "ACTUATOR RAIL AFTER REDUNDANT INTERRUPTION; LOCAL FEED CONDUCTOR/CONNECTOR/PROTECTION SELECTION REQUIRED",
            "per_axis_output": "one separately protected positive and return pair", "fault_isolation": "one channel fault must not backfeed another channel; exact eFuse/fuse architecture open",
            "telemetry": "per-channel current/fault status candidate; interface selection required", "mechanical_envelope": "SELECTION REQUIRED IN MODULE CAD",
            "state": "DISTRIBUTED NODE REQUIRED BY PHYSICAL PACKING; SCHEMATIC/PCB NOT YET RELEASED",
        }))
    return axis_rows, corridor_rows, node_rows, drop_rows


def connector_rows() -> list[dict[str, object]]:
    return [common(r) for r in [
        {"interface_id":"DPH-C01","service":"18 AWG female crimp","part_number":"430300038","wire":"18 AWG; 1.60-1.85 mm preferred insulation range in Molex hand-tool specification","current_basis":"family reference only; end-use thermal test required","state":"EXACT TERMINAL CANDIDATE"},
        {"interface_id":"DPH-C02","service":"18 AWG male crimp","part_number":"430310021","wire":"18 AWG; 1.60-1.85 mm preferred insulation range in Molex hand-tool specification","current_basis":"family reference only; end-use thermal test required","state":"EXACT TERMINAL CANDIDATE"},
        {"interface_id":"DPH-C03","service":"12-core trunk receptacle","part_number":"430251200","wire":"12 x 18 AWG using 430300038","current_basis":"12-circuit wire-to-wire reference 6.5 A/contact; all circuits powered; application dependent","state":"EXACT HOUSING CANDIDATE; RECEIVED FIT OPEN"},
        {"interface_id":"DPH-C04","service":"12-core panel plug","part_number":"430201200","wire":"12 x 18 AWG using 430310021","current_basis":"12-circuit wire-to-wire reference 6.5 A/contact; all circuits powered; application dependent","state":"EXACT HOUSING CANDIDATE; RECEIVED FIT OPEN"},
        {"interface_id":"DPH-C05","service":"2-core local branch pair","part_number":"430250200 + 430200200","wire":"2 x 18 AWG with 430300038/430310021","current_basis":"2-circuit wire-to-wire reference 7 A/contact; HR-30 cap <=2.499010 A; end-use test still required","state":"EXACT HOUSING/TERMINAL CANDIDATE"},
    ]]


def hold_rows() -> list[dict[str, object]]:
    data = [
        ("DPH-H01", "six distributed protection nodes lack selected eFuse/fuse components and PCB schematics", "select devices from measured fault, inrush, regeneration and clearing evidence; create connected ECAD"),
        ("DPH-H02", "upstream feed conductors/connectors to each distributed node are not sized", "fault-current, simultaneous-duty, voltage-drop, connector and thermal tests"),
        ("DPH-H03", "arm trunk 861812 has only 0.6528 mm diametral corridor clearance at maximum published OD", "tolerance stack, pull/assembly method, chafe liner, clamp and full-motion physical fit test"),
        ("DPH-H04", "all six route-guide radius screens pass, but guard, snag and full-pose collision clearance remain unexecuted", "complete exact guarded-route CAD and neutral/crouch/weight-transfer/step/fall-restraint collision sweeps before any fabrication release"),
        ("DPH-H05", "local 861802 branch loops and joint crossings have no accepted 3D sweep or cut length", "joint-by-joint routed CAD, full-limit sweep, clamp locations and flex-cycle test"),
        ("DPH-H06", "861812 12-core intermediate breakouts are not schematic- or PCB-defined", "keyed cavity map, breakout PCB, creepage/clearance, copper, protection boundary, mounting and service access"),
        ("DPH-H07", "published conductor DCR values are nominal, not maximum, and bundle temperature is unvalidated", "received-lot four-wire resistance plus representative bundle temperature-rise test at measured duty and fault clearing"),
        ("DPH-H08", "Micro-Fit reference ratings do not release the HR-30 connector application", "production-tool crimp sections/pull tests, connector temperature rise, vibration, retention and mating-cycle plan"),
        ("DPH-H09", "Alpha 3051-to-JST EH actuator pigtail remains the 22 AWG endpoint bottleneck", "exact pigtail length, crimp process, JST application derating and connector temperature-rise validation"),
        ("DPH-H10", "no exact supplier quotation, received lot, certificate, or availability has been accepted", "written quotation and incoming inspection tied to exact order codes and source revisions"),
        ("DPH-H11", "protective-earth, shield and reference bonding remain outside this power-cable package", "qualified electrical integration disposition with the authoritative ECAD"),
        ("DPH-H12", "no physical build or powered evidence exists", "staged unpowered fit, continuity/hipot as applicable, guarded low-energy commissioning, fault injection and qualified review"),
    ]
    return [common({"hold_id": i, "unresolved": issue, "evidence_required": evidence, "state": "OPEN"}) for i, issue, evidence in data]


def svg(corridors: list[dict[str, object]]) -> str:
    cards = "".join(f'<g transform="translate({80 + (i%3)*500},{270 + (i//3)*245})"><rect class="card" width="440" height="190" rx="18"/><text class="name" x="24" y="42">{html.escape(str(r["distribution_node"] if "distribution_node" in r else r["corridor"]))}</text><text x="24" y="78">{html.escape(str(r["corridor"]))}</text><text x="24" y="112">{r["successor_trunk"]}: {r["protected_core_count"]}/{r["trunk_core_count"]} protected cores</text><text x="24" y="146">OD {r["trunk_max_od_mm"]} / corridor {r["corridor_diameter_mm"]} mm</text><text class="small" x="24" y="174">bend: {html.escape(str(r["bend_screen"]))}</text></g>' for i, r in enumerate(corridors))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1040" viewBox="0 0 1600 1040" role="img" aria-labelledby="t d"><title id="t">HR-30 distributed actuator power harness</title><desc id="d">Six local protected distribution nodes feed multi-core limb trunks and local two-core actuator branches.</desc><style>text{{font:18px system-ui;fill:#122a42}}.title{{font-size:40px;font-weight:900}}.sub{{font-size:22px}}.name{{font-size:24px;font-weight:900;fill:#0b4f91}}.small{{font-size:16px}}.card{{fill:#fff;stroke:#0b4f91;stroke-width:3}}.rail{{stroke:#f2b91d;stroke-width:12}}.warn{{fill:#fff0b5;stroke:#805600;stroke-width:3}}</style><rect width="1600" height="1040" fill="#eef8ff"/><rect x="40" y="28" width="1520" height="90" rx="16" class="warn"/><text class="title" x="75" y="82">Distributed HR-30 actuator-power successor</text><text class="sub" x="75" y="145">Redundant upstream interruption</text><path class="rail" d="M80 185 H1520"/><text class="sub" x="600" y="220">six local protected nodes</text>{cards}<text class="small" x="55" y="1010">{html.escape(WARNING)}</text></svg>'''


def page(axis: list[dict[str, object]], corridors: list[dict[str, object]], nodes: list[dict[str, object]], holds: list[dict[str, object]]) -> str:
    corridor_table = "".join(f"<tr><td><strong>{html.escape(str(r['corridor']))}</strong></td><td>{r['axis_count']}</td><td>{r['old_individual_861802_bundle_fill_ratio']}</td><td>{r['successor_trunk']}</td><td>{r['trunk_area_fill_ratio']}</td><td>{html.escape(str(r['bend_screen']))}</td></tr>" for r in corridors)
    node_cards = "".join(f"<article><h3>{html.escape(str(r['node_id']))}</h3><p><strong>{r['channel_count']} protected channels</strong></p><p>{html.escape(str(r['location']))}</p><p>{html.escape(str(r['axes']))}</p></article>" for r in nodes)
    holds_html = "".join(f"<li><strong>{h['hold_id']}</strong> — {html.escape(str(h['unresolved']))}</li>" for h in holds)
    max_drop = max(float(r["cap_drop_80c_v"]) for r in axis)
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 distributed power harness</title><style>:root{{--deep:#071d36;--blue:#0b4f91;--sky:#d9f2ff;--gold:#f2b91d;--paper:#f7fbff;--ink:#142a40;--line:#82c4e6;--red:#982520}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.55 system-ui,Segoe UI,sans-serif}}header,main,footer{{padding:clamp(24px,5vw,64px) max(18px,calc((100vw - 1280px)/2))}}header,footer{{background:linear-gradient(135deg,var(--deep),var(--blue));color:white}}h1{{font-size:clamp(38px,6vw,70px);line-height:1.04;max-width:19ch}}h2{{font-size:clamp(28px,4vw,44px)}}h3{{font-size:22px}}.warning{{background:var(--gold);color:#17243a;border:3px solid #805600;padding:16px;font-weight:900}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:18px}}article,.panel{{background:white;border:2px solid var(--line);border-radius:16px;padding:20px}}.metric{{font-size:clamp(34px,5vw,54px);font-weight:900;color:var(--blue)}}.hold{{border-color:var(--red)}}.scroll{{overflow:auto;border:2px solid var(--line);border-radius:14px;background:white}}table{{border-collapse:collapse;width:100%;min-width:980px}}th,td{{padding:14px;text-align:left;vertical-align:top;border-bottom:1px solid var(--line);font-size:16px}}th{{background:var(--deep);color:white;position:sticky;top:0}}img{{max-width:100%;height:auto;border:2px solid var(--line);border-radius:16px}}a{{color:#075b9b;font-weight:800}}li{{margin:.55rem 0}}small{{font-size:14px}}@media(max-width:560px){{body{{font-size:16px}}}}</style></head><body><header><div class="warning">{html.escape(WARNING)}</div><p>HR-30 whole-body P0.1</p><h1>The power harness now fits the limb corridors on paper.</h1><p>The previous concept bundled one jacketed cable per actuator. That physically fails five of six power corridors. This successor keeps individual protection but moves it to six local nodes and uses multi-core trunks.</p></header><main><section class="grid"><article><div class="metric">25</div><p>separately protected actuator pairs retained</p></article><article><div class="metric">6</div><p>local distribution nodes</p></article><article><div class="metric">3</div><p>exact Alpha cable families</p></article><article class="hold"><div class="metric">0</div><p>released protection values or powered permissions</p></article></section><section><h2>Why the architecture changed</h2><div class="panel"><p>Using Alpha 861802 for every axis would exceed the geometric cross-sectional area of both leg, both arm, and head corridors. One multi-core trunk per corridor fits the diameter screen while preserving a dedicated protected pair for every axis.</p><p>The cable-only nominal comparison produces a worst bounded 80°C drop of <strong>{max_drop:.4f} V</strong> at the current candidate caps and existing straight-line planning lengths. That is not a thermal rating or final voltage-drop result.</p></div></section><section><h2>Whole-body topology</h2><img src="distributed-power-harness.svg" alt="Six local actuator power distribution nodes feeding multi-core trunks"></section><section><h2>Local protection nodes</h2><div class="grid">{node_cards}</div></section><section><h2>Corridor screens</h2><div class="scroll"><table><thead><tr><th>Corridor</th><th>Axes</th><th>Old individual-cable fill ratio</th><th>Successor trunk</th><th>Trunk fill ratio</th><th>Bend screen</th></tr></thead><tbody>{corridor_table}</tbody></table></div><p><small>A fill ratio below 1 only proves the circular-area/diameter screen. It does not prove pullability, clearance, chafe, clamping, or tolerance.</small></p></section><section><h2>Still open before fabrication</h2><div class="panel hold"><ul>{holds_html}</ul></div></section><section><h2>Engineering records</h2><div class="panel"><p><a href="cable-family-register.csv">Cable families</a> · <a href="corridor-architecture.csv">Corridor architecture</a> · <a href="distribution-node-register.csv">Distribution nodes</a> · <a href="axis-core-allocation.csv">25 axis allocations</a> · <a href="actuator-breakout-register.csv">Breakouts</a> · <a href="connector-contact-register.csv">Connector contacts</a> · <a href="primary-source-register.csv">Primary sources</a> · <a href="open-holds.csv">Open holds</a></p></div></section></main><footer>{html.escape(WARNING)}</footer></body></html>'''


def manifest(out: Path) -> None:
    rows = []
    for path in sorted(p for p in out.iterdir() if p.is_file() and p.name != "file-manifest.csv"):
        rows.append({"file": path.name, "bytes": path.stat().st_size, "sha256": sha(path), "warning": WARNING})
    write_csv(out / "file-manifest.csv", rows)


def main() -> None:
    if OUT.exists(): shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    specs = cable_specs()
    axis, corridors, nodes, breakouts = build_rows(specs)
    connectors = connector_rows()
    holds = hold_rows()
    write_csv(OUT / "primary-source-register.csv", source_rows())
    write_csv(OUT / "cable-family-register.csv", cable_rows(specs))
    write_csv(OUT / "axis-core-allocation.csv", axis)
    write_csv(OUT / "corridor-architecture.csv", corridors)
    write_csv(OUT / "distribution-node-register.csv", nodes)
    write_csv(OUT / "actuator-breakout-register.csv", breakouts)
    write_csv(OUT / "connector-contact-register.csv", connectors)
    write_csv(OUT / "open-holds.csv", holds)
    (OUT / "distributed-power-harness.svg").write_text(svg(corridors), encoding="utf-8", newline="\n")
    (OUT / "index.html").write_text(page(axis, corridors, nodes, holds), encoding="utf-8", newline="\n")
    (OUT / "README.md").write_text(f"# HR-30 distributed power harness successor P0.1\n\n{WARNING}\n\nThis package replaces the physically impossible one-jacketed-cable-per-axis corridor bundle with six local protected distribution nodes, multi-core limb trunks, and local two-core actuator branches. It is a coherent physical/electrical candidate, not a fabrication or energization release.\n", encoding="utf-8", newline="\n")
    status = {
        "identifier": IDENTIFIER, "date": DATE, "warning": WARNING, "axis_count": len(axis), "distribution_node_count": len(nodes),
        "corridor_count": len(corridors), "old_individual_cable_corridor_failures": sum(r["old_bundle_geometric_result"] == "FAIL" for r in corridors),
        "successor_diameter_screens_pass": sum(r["diameter_screen"] == "PASS GEOMETRIC AREA" for r in corridors),
        "successor_bend_screens_pass": sum(r["bend_screen"] == "PASS ROUTE-GUIDE GEOMETRY" for r in corridors),
        "route_guide_geometry_integrated": True,
        "exact_cable_order_codes_bound": True, "exact_18awg_microfit_terminal_order_codes_bound": True,
        "protection_components_selected": False, "breakout_ecad_complete": False, "route_sweeps_complete": False, "thermal_validated": False,
        "fabrication_authority": False, "connection_authority": False, "powered_test_authority": False, "motion_authority": False, "energization_authority": False,
    }
    (OUT / "status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n")
    shutil.copy2(Path(__file__), OUT / "distributed-power-harness-source.py")
    manifest(OUT)
    if RELEASE.exists(): shutil.rmtree(RELEASE)
    RELEASE.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(OUT, RELEASE)
    integrate_parent_guides()
    print(json.dumps(status, indent=2))


if __name__ == "__main__":
    main()
