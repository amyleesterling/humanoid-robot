"""Generate the HR-30 P0.1 whole-body power/data harness architecture."""

from __future__ import annotations

import csv
import hashlib
import html
import json
import math
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "hr30" / "whole-body-p0.1"
OUT = PKG / "harness"
WARNING = "PRELIMINARY - NOT APPROVED FOR CONNECTION, FABRICATION, MOTION OR ENERGIZATION"
ACCESSED = "2026-08-14"

PINS = {
    "XH540": ("RS-485", "1=GND; 2=VDD; 3=DATA+; 4=DATA-", "JST EHR-04", "JST B4B-EH-A"),
    "XM540": ("RS-485", "1=GND; 2=VDD; 3=DATA+; 4=DATA-", "JST EHR-04", "JST B4B-EH-A"),
    "XM430": ("RS-485", "1=GND; 2=VDD; 3=DATA+; 4=DATA-", "JST EHR-04", "JST B4B-EH-A"),
    "XC330": ("TTL", "1=GND; 2=VDD; 3=DATA", "JST EHR-03", "JST B3B-EH-A"),
}
STALL_A = {"XH540": 4.9, "XM540": 4.4, "XM430": 2.3, "XC330": 0.88}
ROUTES = {
    "RS-LLEG": ("HN01_TORSO_POWER_SPINE | HN01_L_LEG_POWER", "HN01_TORSO_DATA_SPINE | HN01_L_LEG_DATA"),
    "RS-RLEG": ("HN01_TORSO_POWER_SPINE | HN01_R_LEG_POWER", "HN01_TORSO_DATA_SPINE | HN01_R_LEG_DATA"),
    "RS-LARM": ("HN01_TORSO_POWER_SPINE | HN01_L_ARM_POWER", "HN01_TORSO_DATA_SPINE | HN01_L_ARM_DATA"),
    "RS-RARM": ("HN01_TORSO_POWER_SPINE | HN01_R_ARM_POWER", "HN01_TORSO_DATA_SPINE | HN01_R_ARM_DATA"),
    "RS-WAIST": ("HN01_TORSO_POWER_SPINE", "HN01_TORSO_DATA_SPINE"),
    "TTL-LDIST": ("HN01_TORSO_POWER_SPINE | HN01_L_ARM_POWER", "HN01_TORSO_DATA_SPINE | HN01_L_ARM_DATA"),
    "TTL-RDIST": ("HN01_TORSO_POWER_SPINE | HN01_R_ARM_POWER", "HN01_TORSO_DATA_SPINE | HN01_R_ARM_DATA"),
    "TTL-HEAD": ("HN01_TORSO_POWER_SPINE | HN01_HEAD_POWER_BRANCH", "HN01_TORSO_DATA_SPINE | HN01_HEAD_BRANCH"),
}


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise SystemExit(f"refusing empty register: {path.name}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def point(text: str) -> tuple[float, float, float]:
    return tuple(float(v) for v in re.findall(r"[-+]?\d+(?:\.\d+)?", text))  # type: ignore[return-value]


def svg_map(route_rows: list[dict]) -> str:
    colors = {"ACTUATOR POWER": "#e3aa18", "DATA/LOW VOLTAGE": "#56bde9", "DATA/ENCODER": "#56bde9"}
    lines = []
    for row in route_rows:
        a, b = point(row["start_xyz_mm"]), point(row["end_xyz_mm"])
        x1, y1 = 350 + 1.9 * a[0], 735 - 0.92 * a[2]
        x2, y2 = 350 + 1.9 * b[0], 735 - 0.92 * b[2]
        color = colors[row["service_class"]]
        lines.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="7" stroke-linecap="round"><title>{html.escape(row["route_id"])} — {html.escape(row["service_class"])}</title></line>')
        lines.append(f'<circle cx="{x2:.1f}" cy="{y2:.1f}" r="5" fill="{color}"/>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 700 780" role="img" aria-labelledby="title desc">
<title id="title">HR-30 whole-body harness corridor map</title><desc id="desc">Front elevation showing six actuator-power and six data corridors through the complete humanoid.</desc>
<rect width="700" height="780" rx="28" fill="#061a36"/><g fill="#e8f6ff" stroke="#8ed8ff" stroke-width="3" opacity=".28">
<rect x="282" y="74" width="136" height="112" rx="45"/><rect x="258" y="190" width="184" height="178" rx="38"/><rect x="284" y="370" width="132" height="92" rx="28"/>
<rect x="112" y="214" width="116" height="54" rx="22"/><rect x="472" y="214" width="116" height="54" rx="22"/><rect x="84" y="268" width="72" height="245" rx="30"/><rect x="544" y="268" width="72" height="245" rx="30"/>
<rect x="270" y="454" width="56" height="242" rx="24"/><rect x="374" y="454" width="56" height="242" rx="24"/><rect x="226" y="687" width="112" height="43" rx="18"/><rect x="362" y="687" width="112" height="43" rx="18"/></g>
<g>{''.join(lines)}</g><g font-family="system-ui,sans-serif" font-size="18" fill="#fff"><text x="26" y="38" font-size="24" font-weight="700">12 located whole-body corridors</text><text x="26" y="66" fill="#9bdcff">blue = data / low voltage</text><text x="430" y="66" fill="#ffd25a">gold = actuator power</text></g></svg>'''


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    buses = read_csv(PKG / "actuator-bus-topology.csv")
    axes = read_csv(PKG / "actuator-bus-axis-binding.csv")
    routes = read_csv(PKG / "harness-route-register.csv")
    if len(buses) != 8 or len(axes) != 25 or len(routes) != 12:
        raise SystemExit("whole-body bus/axis/route inputs are incomplete")

    pin_rows = []
    sources = {
        "XH540": ("https://docs.robotis.com/docs/dxl/model_reference/x_series/xh_series/xh540-w270/", "ROBOTIS-GIT b0c64501f080d20088d044c65569f45279351ade; 2025-06-19"),
        "XM540": ("https://docs.robotis.com/docs/dxl/model_reference/x_series/xm_series/xm540-w270/", "ROBOTIS-GIT b0c64501f080d20088d044c65569f45279351ade; 2025-06-19"),
        "XM430": ("https://docs.robotis.com/docs/dxl/model_reference/x_series/xm_series/xm430-w350/", "ROBOTIS-GIT b0c64501f080d20088d044c65569f45279351ade; 2025-06-19"),
        "XC330": ("https://docs.robotis.com/docs/dxl/model_reference/x_series/xc_series/xc330-t288/", "ROBOTIS-GIT 91f72d1ddd3f86d94d74b35ab037f7ec8c8c4dbe; 2026-01-27"),
    }
    for family, (protocol, pins, housing, header) in PINS.items():
        url, revision = sources[family]
        pin_rows.append({"family": family, "protocol": protocol, "actuator_side_pin_mapping": pins, "cable_housing": housing, "actuator_pcb_header": header, "crimp_terminal": "JST SEH-001T-P0.6", "manufacturer_published_dynamixel_wire_gauge": "21 AWG", "official_source": url, "source_revision_or_date": revision, "accessed_date": ACCESSED, "closure_state": "VERIFIED AT ACTUATOR INTERFACE ONLY", "remaining_selection": "assembled cable, controller connector, application conductor sizing, retention, flex life and EMC"})
    write_csv(OUT / "actuator-side-pinout-register.csv", pin_rows)

    by_axis = {row["axis_id"]: row for row in axes}
    branch_rows, drop_rows, boundaries = [], [], []
    for bus in buses:
        bus_id = bus["bus_id"]
        axis_ids = [value.strip() for value in bus["axis_ids"].split("|")]
        endpoint = sum(STALL_A[by_axis[axis]["actuator_family"]] for axis in axis_ids)
        pwr, data = ROUTES[bus_id]
        branch_rows.append({"bus_id": bus_id, "protocol": bus["protocol"], "axis_count": len(axis_ids), "axis_ids": " | ".join(axis_ids), "power_corridor_chain": pwr, "data_corridor_chain": data, "candidate_12v_stall_endpoint_sum_a": f"{endpoint:.2f}", "endpoint_use_boundary": "MOMENTARY DATASHEET STALL SUM ONLY - NOT NORMAL DEMAND OR A PROTECTION/CONDUCTOR RATING", "power_topology": "ONE SEPARATELY PROTECTED SEGMENT BRANCH; LISTED AXES MAY SHARE ONLY THIS BRANCH VDD", "data_power_boundary": "CONTROLLER BOUNDARY MUST NOT JOIN VDD TO ANOTHER PROTECTED SEGMENT; EXACT BREAKOUT SELECTION REQUIRED", "controller_interface": "SELECTION REQUIRED", "termination_bias_level_shift": "SELECTION REQUIRED", "status": "ROUTED CANDIDATE - NOT RELEASED"})
        boundaries.append({"boundary_id": f"CB-{bus_id}", "boundary_type": "CONTROLLER / SEGMENT", "bus_id": bus_id, "axis_id": "N/A", "known_side": "LOGICAL DATA AND RETURN NETS", "known_pin_mapping": "SELECTION REQUIRED", "mating_part": "SELECTION REQUIRED", "validation": "NOT EXECUTED"})
        for order, axis in enumerate(axis_ids, 1):
            family = by_axis[axis]["actuator_family"]
            protocol, pins, housing, _ = PINS[family]
            drop_rows.append({"axis_id": axis, "bus_id": bus_id, "segment_order_provisional": order, "actuator_family": family, "protocol": protocol, "actuator_side_pin_mapping": pins, "actuator_side_housing": housing, "power_corridor_chain": pwr, "data_corridor_chain": data, "actuator_id": "SELECTION REQUIRED", "assembled_cable_order_code": "SELECTION REQUIRED", "planning_geometric_length_mm": "DERIVE FROM WHOLE-BODY ROUTE; SERVICE LOOP/CUT LENGTH SELECTION REQUIRED", "retention_flex_shielding": "SELECTION REQUIRED", "authority": "NO CONNECTION OR ENERGIZATION AUTHORITY"})
            boundaries.append({"boundary_id": f"AB-{axis}", "boundary_type": "HARNESS / ACTUATOR", "bus_id": bus_id, "axis_id": axis, "known_side": housing, "known_pin_mapping": pins, "mating_part": "JST SEH-001T-P0.6 CONTACT IN LISTED HOUSING; ASSEMBLED CABLE SELECTION REQUIRED", "validation": "NOT EXECUTED"})
    write_csv(OUT / "bus-harness-assembly-register.csv", branch_rows)
    write_csv(OUT / "actuator-drop-register.csv", drop_rows)
    write_csv(OUT / "connector-boundary-register.csv", boundaries)

    assembly_defs = [
        ("HN-E01", "energy/battery/charge", "T01 | external charger/tether"), ("HN-S01", "safety/permit", "T01 | external E-stop/reset"),
        ("HN-C01", "compute/interfaces", "T01"), ("HN-P01", "pelvis/waist", "P01"), ("HN-NH01", "head and articulated neck", "N01 | H01"),
        ("HN-A01", "left arm", "A01"), ("HN-G01", "left hand", "G01"), ("HN-A02", "right arm", "A02"), ("HN-G02", "right hand", "G02"),
        ("HN-L01", "left leg", "L01"), ("HN-F01", "left foot", "F01"), ("HN-L02", "right leg", "L02"), ("HN-F02", "right foot", "F02"),
        ("HN-X01", "external/service", "external restraint, charger, service and bench interfaces"),
    ]
    assembly_rows = [{"assembly_id": aid, "scope": scope, "modules_or_boundary": modules, "power_entry": "SELECTION REQUIRED", "data_entry": "SELECTION REQUIRED", "connector_instances": "SELECTION REQUIRED", "retention_and_service_access": "SELECTION REQUIRED", "drawing_state": "WHOLE-BODY ALLOCATION PRESENT - DETAILED HARNESS DRAWING OPEN", "authority": "NO FABRICATION OR CONNECTION AUTHORITY"} for aid, scope, modules in assembly_defs]
    write_csv(OUT / "harness-assembly-register.csv", assembly_rows)

    equipment = read_csv(PKG / "installed-equipment-register.csv")
    def equipment_assembly(row: dict) -> str:
        module = row["module"]
        if module == "T01": return "HN-E01" if any(word in row["role"].lower() for word in ("battery", "power", "disconnect", "contactor", "converter")) else "HN-C01"
        return {"P01":"HN-P01","N01":"HN-NH01","H01":"HN-NH01","A01":"HN-A01","G01":"HN-G01","A02":"HN-A02","G02":"HN-G02","L01":"HN-L01","F01":"HN-F01","L02":"HN-L02","F02":"HN-F02","HN01":"HN-X01"}.get(module, "HN-X01")
    equipment_rows = [{"item_id": row["item_id"], "module": row["module"], "harness_assembly": equipment_assembly(row), "role": row["role"], "candidate": row["candidate"], "declared_connector_boundary": row["connector_boundary"], "operating_power_w": row["operating_power_w"], "dynamic_link": row["dynamic_link"], "physical_connector_and_contacts": "SELECTION REQUIRED", "power_net_and_protection": "SELECTION REQUIRED", "data_net_and_interface": "SELECTION REQUIRED", "route_and_retention": "SELECTION REQUIRED", "completeness_state": "EQUIPMENT ACCOUNTED FOR - PHYSICAL HARNESS DEFINITION OPEN"} for row in equipment]
    write_csv(OUT / "equipment-interface-register.csv", equipment_rows)

    loop_rows = [{"loop_id": f"SL-{row['axis_id']}", "axis_id": row["axis_id"], "bus_id": row["bus_id"], "power_corridor_chain": row["power_corridor_chain"], "data_corridor_chain": row["data_corridor_chain"], "rotation_range_and_stackup": "DERIVE FROM WHOLE-BODY DOF LIMITS; TOLERANCE OPEN", "minimum_bend_radius": "SELECTION REQUIRED FROM CABLE", "loop_length_and_slack": "SELECTION REQUIRED", "clamp_points": "SELECTION REQUIRED", "cycle_life_test": "NOT EXECUTED", "state": "MOVING-LOOP OBLIGATION DEFINED"} for row in drop_rows]
    write_csv(OUT / "service-loop-register.csv", loop_rows)
    term_rows = [{"bus_id": row["bus_id"], "protocol": row["protocol"], "topology": "MULTIDROP DAISY / STUB CONTROL SELECTION REQUIRED", "controller_end_termination": "SELECTION REQUIRED", "far_end_termination": "SELECTION REQUIRED", "bias_network": "SELECTION REQUIRED", "reference_and_shield": "SELECTION REQUIRED", "baud_rate": "SELECTION REQUIRED", "waveform_emc_validation": "NOT EXECUTED"} for row in buses]
    write_csv(OUT / "bus-termination-register.csv", term_rows)

    connector_schedule = PKG / "electrical" / "kicad" / "hr30-whole-body-electrical-p0.1" / "connector-schedule.csv"
    terminal_rows = read_csv(connector_schedule)
    terminal_binding = [{"sheet": row["sheet"], "reference": row["reference"], "terminal": row["terminal"], "pin_name": row["pin_name"], "net": row["net"], "current_definition_state": row["status"], "physical_connector_instance": "ACTUATOR DEVICE INTERFACE VERIFIED" if row["reference"].startswith("AX_") else "SELECTION REQUIRED", "physical_contact": row["terminal"] if row["reference"].startswith("AX_") else "SELECTION REQUIRED", "wire_or_cable_core": "SELECTION REQUIRED", "route_segment": "BINDING REQUIRED", "validation": "NOT EXECUTED"} for row in terminal_rows]
    write_csv(OUT / "logical-terminal-binding.csv", terminal_binding)

    corridor_rows = []
    for row in routes:
        a, b = point(row["start_xyz_mm"]), point(row["end_xyz_mm"])
        length = math.dist(a, b)
        corridor_rows.append({"route_id": row["route_id"], "module": row["module"], "service_class": row["service_class"], "start_xyz_mm": row["start_xyz_mm"], "end_xyz_mm": row["end_xyz_mm"], "geometric_centerline_mm": f"{length:.1f}", "corridor_diameter_mm": row["corridor_diameter_mm"], "minimum_dynamic_bend_radius_mm": row["minimum_dynamic_bend_radius_mm"], "fill_budget": "SELECTION REQUIRED AFTER CABLE OD/COUNT", "service_loop_and_cut_length": "SELECTION REQUIRED", "moving_joint_flex_life": "SELECTION REQUIRED AND TEST REQUIRED", "state": "LOCATED CORRIDOR - CABLE NOT RELEASED"})
    write_csv(OUT / "corridor-fill-budget.csv", corridor_rows)

    source_rows = [{"source_id": family, "official_url": sources[family][0], "revision_or_date": sources[family][1], "accessed_date": ACCESSED, "verified": PINS[family][1] + "; " + PINS[family][2] + "; " + PINS[family][3] + "; JST SEH-001T-P0.6; 21 AWG published", "not_verified": "whole-robot harness application"} for family in PINS]
    source_rows += [
        {"source_id": "U2D2", "official_url": "https://docs.robotis.com/docs/parts/interface/u2d2/", "revision_or_date": "ROBOTIS-GIT 2c6cbdc3c85abd30451ec56126303395c69b2bf6; 2026-04-17", "accessed_date": ACCESSED, "verified": "no actuator power; max 6 Mbps; optional 120 ohm termination", "not_verified": "final eight-segment controller; REJECTED for that role"},
        {"source_id": "U2D2-PHB", "official_url": "https://docs.robotis.com/docs/parts/interface/u2d2_power_hub/", "revision_or_date": "ROBOTIS-GIT 700c2bfd2e8da9dc64c18ce4020f33feb454d8eb; 2025-02-05", "accessed_date": ACCESSED, "verified": "3.5-24 V; 10 A maximum aggregate", "not_verified": "whole-body power; REJECTED for summed actuator power"},
        {"source_id": "JST-EH", "official_url": "https://www.jst-mfg.com/product/pdf/eng/eEH.pdf", "revision_or_date": "CURRENT PDF; REVISION DATE NOT STATED", "accessed_date": ACCESSED, "verified": "EH series catalog interface data", "not_verified": "HR-30 application current/flex/derating"},
    ]
    write_csv(OUT / "harness-source-register.csv", source_rows)
    (OUT / "whole-body-harness-map.svg").write_text(svg_map(routes), encoding="utf-8", newline="\n")

    total_endpoint = sum(float(row["candidate_12v_stall_endpoint_sum_a"]) for row in branch_rows)
    status = {"identifier": "HR30-WHOLE-BODY-HARNESS-P0.1", "axis_drop_count": 25, "bus_branch_count": 8, "corridor_count": 12, "connector_boundary_count": 33, "harness_assembly_count": len(assembly_rows), "installed_equipment_binding_count": len(equipment_rows), "service_loop_obligation_count": len(loop_rows), "logical_terminal_binding_count": len(terminal_binding), "actuator_side_pinout_families_verified": 4, "candidate_12v_stall_endpoint_sum_a": total_endpoint, "u2d2_final_controller_role": "REJECT", "u2d2_power_hub_whole_body_role": "REJECT", "controller_side_connectors_selected": False, "assembled_cables_selected": False, "protection_selected": False, "conductor_sizing_released": False, "harness_validated": False, "connection_authority": False, "fabrication_authority": False, "powered_test_authority": False, "motion_authority": False, "energization_authority": False, "warning": WARNING}
    (OUT / "harness-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    (OUT / "README.md").write_text(f"""# HR-30 whole-body harness P0.1

**{WARNING}**

This package turns the 25-axis electrical allocation into eight explicit protected bus branches, 25 actuator drops, 33 connector boundaries, 14 controlled harness assemblies and 12 located full-body corridors. It also accounts for every installed equipment item and every current KiCad logical terminal so the missing physical definitions are visible rather than silently omitted. Current official ROBOTIS documentation closes the actuator-side pin order and listed JST parts only. Controller connectors, cable assemblies, conductor sizing, protection, termination, shielding, retention, flex life and physical validation remain **SELECTION REQUIRED**.

The 76.08 A figure is only the arithmetic sum of published 12 V momentary stall-current endpoints. It is not expected operating current and must not be used as a fuse, conductor, connector or source rating. A U2D2 Power Hub is limited to 10 A aggregate and is rejected for whole-body or leg power aggregation. U2D2 is retained only as a single-segment commissioning candidate, not the final eight-segment controller.

The controller boundary must not connect one protected segment's VDD to another. Standard ROBOTIS X3P/X4P cable families include VDD; exact breakout/cable construction and no-backfeed verification remain open.
""", encoding="utf-8", newline="\n")

    cards = "".join(f'<article><h3>{html.escape(row["bus_id"])}</h3><p>{row["axis_count"]} axes · {html.escape(row["protocol"])}</p><p><strong>Power:</strong> {html.escape(row["power_corridor_chain"])}</p><p><strong>Data:</strong> {html.escape(row["data_corridor_chain"])}</p><p><strong>Stall endpoint sum:</strong> {row["candidate_12v_stall_endpoint_sum_a"]} A</p></article>' for row in branch_rows)
    route_html = "".join(f'<tr><td>{html.escape(row["route_id"])}</td><td>{html.escape(row["service_class"])}</td><td>{row["geometric_centerline_mm"]}</td><td>{row["corridor_diameter_mm"]}</td><td>{row["minimum_dynamic_bend_radius_mm"]}</td></tr>' for row in corridor_rows)
    (OUT / "index.html").write_text(f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 whole-body harness P0.1</title><style>:root{{--ink:#061a36;--sky:#8ed8ff;--blue:#0a4b91;--gold:#f5bd2b;--paper:#f6fbff}}*{{box-sizing:border-box}}body{{margin:0;font:17px/1.55 system-ui,sans-serif;color:var(--ink);background:var(--paper)}}header,main{{max-width:1180px;margin:auto;padding:28px}}header{{background:var(--ink);color:white;max-width:none}}header>div{{max-width:1180px;margin:auto}}h1{{font-size:clamp(2rem,5vw,4.6rem);line-height:1;margin:.2em 0}}h2{{font-size:clamp(1.55rem,3vw,2.4rem)}}.warning{{border:3px solid var(--gold);padding:14px;font-weight:800}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:18px}}article{{background:white;border:2px solid var(--blue);border-radius:18px;padding:18px;box-shadow:6px 6px 0 var(--sky)}}img{{display:block;max-width:760px;width:100%;margin:auto}}.table{{overflow:auto;background:white;border:2px solid var(--blue);border-radius:16px}}table{{border-collapse:collapse;width:100%;min-width:780px}}th,td{{padding:12px;text-align:left;border-bottom:1px solid #b9d7ea}}th{{background:var(--blue);color:white}}a{{color:#075ca7;font-weight:700}}small{{font-size:14px}}</style></head><body><header><div><p class="warning">{WARNING}</p><h1>Power and data, through the whole robot.</h1><p>Eight protected segment candidates, 25 actuator drops, 33 connector boundaries, and 12 located corridors.</p></div></header><main><section><h2>One recognizable whole-body route map</h2><img src="whole-body-harness-map.svg" alt="Front view of HR-30 showing separate blue data and gold actuator-power corridors"></section><section><h2>Eight bus harness assemblies</h2><div class="grid">{cards}</div></section><section><h2>Corridor budget</h2><div class="table"><table><thead><tr><th>Route</th><th>Service</th><th>Centerline mm</th><th>Diameter mm</th><th>Minimum bend radius mm</th></tr></thead><tbody>{route_html}</tbody></table></div></section><section><h2>What is actually verified</h2><p>Current official ROBOTIS documentation defines the actuator-side pins and listed JST parts. It does not define HR-30's controller-side connectors, cable assemblies, protection, sizing, routing durability or EMC. Those remain selection and test work.</p><p><a href="actuator-side-pinout-register.csv">Pinout register</a> · <a href="bus-harness-assembly-register.csv">Bus assemblies</a> · <a href="actuator-drop-register.csv">25 drops</a> · <a href="connector-boundary-register.csv">33 boundaries</a> · <a href="corridor-fill-budget.csv">12 corridors</a> · <a href="harness-source-register.csv">Sources</a></p></section></main></body></html>''', encoding="utf-8", newline="\n")
    shutil.copy2(Path(__file__), OUT / "whole-body-harness-source.py")
    manifest_rows = []
    for path in sorted(OUT.iterdir()):
        if path.is_file() and path.name != "file-manifest.csv":
            manifest_rows.append({"path": path.name, "bytes": path.stat().st_size, "sha256": sha(path), "warning": WARNING})
    write_csv(OUT / "file-manifest.csv", manifest_rows)

    package_status = json.loads((PKG / "package-status.json").read_text(encoding="utf-8"))
    package_status.update({"whole_body_harness_package_present": True, "whole_body_harness_branch_count": 8, "whole_body_harness_axis_drop_count": 25, "whole_body_harness_corridor_count": 12, "whole_body_harness_assembly_count": len(assembly_rows), "whole_body_harness_equipment_binding_count": len(equipment_rows), "whole_body_harness_logical_terminal_binding_count": len(terminal_binding), "actuator_side_pinouts_reconciled": True, "whole_body_harness_validated": False})
    (PKG / "package-status.json").write_text(json.dumps(package_status, indent=2) + "\n", encoding="utf-8")
    root_page = PKG / "index.html"
    page = root_page.read_text(encoding="utf-8")
    start, end = "<!-- HR30-HARNESS-P01-START -->", "<!-- HR30-HARNESS-P01-END -->"
    if start in page and end in page:
        page = page.split(start, 1)[0] + page.split(end, 1)[1]
    marker = '<section id="native-electrical">'
    section = f'''{start}<section id="whole-body-harness"><h2>The power and data paths now reach every joint</h2><div class="grid"><article class="card pass"><h3>12 located corridors</h3><p>Six actuator-power and six data paths include separate moving-loop reservations through the neck, both arms and both legs.</p></article><article class="card pass"><h3>25 actuator drops</h3><p>Every whole-body axis is assigned to one of eight protected segment candidates and one explicit actuator connector boundary.</p></article><article class="card pass"><h3>Actuator-side pins verified</h3><p>Current official ROBOTIS documentation closes the device-side pin order and listed JST piece parts.</p></article><article class="card hold"><h3>Harness is not released</h3><p>Controller connectors, assembled cables, branch protection, conductor sizing, flex life, EMC and physical tests remain open.</p></article></div><div class="viewer"><object data="harness/whole-body-harness-map.svg" type="image/svg+xml" aria-label="Interactive HR-30 whole-body power and data corridor map"></object><p><a href="harness/index.html">Open the interactive harness guide</a>, or inspect the <a href="harness/bus-harness-assembly-register.csv">eight branch assemblies</a>, <a href="harness/actuator-drop-register.csv">25 drops</a>, and <a href="harness/connector-boundary-register.csv">33 connector boundaries</a>.</p></div></section>{end}'''
    if marker not in page:
        raise SystemExit("native electrical marker missing from whole-body guide")
    root_page.write_text(page.replace(marker, section + marker), encoding="utf-8", newline="\n")
    package_readme = PKG / "README.md"
    readme = package_readme.read_text(encoding="utf-8")
    readme_start, readme_end = "<!-- HR30-HARNESS-README-START -->", "<!-- HR30-HARNESS-README-END -->"
    if readme_start in readme and readme_end in readme:
        readme = readme.split(readme_start, 1)[0] + readme.split(readme_end, 1)[1]
    readme += f"\n{readme_start}\n## Whole-body harness\n\nEight protected bus-branch candidates now map all 25 actuator drops through 12 located power/data corridors, including separate head power and data paths. Current official ROBOTIS documentation closes actuator-side pins only; controller interfaces, cable assemblies, protection, sizing, retention, flex life, EMC and physical validation remain open. See [`harness/index.html`](harness/index.html).\n{readme_end}\n"
    package_readme.write_text(readme, encoding="utf-8", newline="\n")
    sys.path.insert(0, str(ROOT / "tools"))
    import generate_hr30_system_package_p01 as system
    system.refresh_manifest_and_release()
    print(json.dumps(status, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
