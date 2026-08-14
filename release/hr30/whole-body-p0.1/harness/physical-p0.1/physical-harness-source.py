"""Generate the HR-30 whole-body physical-harness P0.1 candidate.

This package translates the existing logical ECAD, eight actuator data buses, 25
joint axes, installed equipment and reserved body corridors into one explicit
physical-harness architecture.  It deliberately does not select conductor
sizes, protection ratings, assembled cables or unverified connector contacts.
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
WB = ROOT / "hr30" / "whole-body-p0.1"
OUT = WB / "harness" / "physical-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / "harness" / "physical-p0.1"
IDENTIFIER = "HR30-WHOLE-BODY-PHYSICAL-HARNESS-P0.1"
WARNING = (
    "PRELIMINARY - PHYSICAL HARNESS ARCHITECTURE ONLY - NOT APPROVED FOR "
    "PROCUREMENT, FABRICATION, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
)
AUTHORITY = "NO PROCUREMENT, FABRICATION, CONNECTION, POWERED TEST, MOTION OR ENERGIZATION AUTHORITY"
OPEN = "SELECTION REQUIRED"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"refusing empty controlled register: {path.name}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def xyz(text: str) -> tuple[float, float, float]:
    return tuple(float(v.strip()) for v in text.strip("() ").split(","))  # type: ignore[return-value]


def fxyz(p: tuple[float, float, float]) -> str:
    return f"({p[0]:.3f},{p[1]:.3f},{p[2]:.3f})"


def dist(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    return math.sqrt(sum((a[i] - b[i]) ** 2 for i in range(3)))


def axis_module(axis: str) -> str:
    side = axis[:1]
    if axis.startswith("HEAD_"):
        return "HN-NH01"
    if axis == "WAIST_YAW":
        return "HN-P01"
    if "GRIPPER" in axis:
        return f"HN-G0{1 if side == 'L' else 2}"
    if any(k in axis for k in ("SHOULDER", "ELBOW", "WRIST")):
        return f"HN-A0{1 if side == 'L' else 2}"
    if any(k in axis for k in ("ANKLE",)):
        return f"HN-F0{1 if side == 'L' else 2}"
    return f"HN-L0{1 if side == 'L' else 2}"


def trunk_for(axis: str, service: str) -> str:
    suffix = "POWER" if service == "POWER" else "DATA"
    if axis.startswith("HEAD_"):
        return f"HN01_HEAD_{'POWER_BRANCH' if service == 'POWER' else 'BRANCH'}"
    if axis == "WAIST_YAW":
        return f"HN01_TORSO_{'POWER' if service == 'POWER' else 'DATA'}_SPINE"
    side = axis[0]
    limb = "ARM" if any(k in axis for k in ("SHOULDER", "ELBOW", "WRIST", "GRIPPER")) else "LEG"
    return f"HN01_{side}_{limb}_{suffix}"


def equipment_route(module: str, role: str) -> tuple[str, str]:
    if module in {"H01", "N01"}:
        return "HN01_HEAD_POWER_BRANCH", "HN01_HEAD_BRANCH"
    if module in {"A01", "G01"}:
        return "HN01_L_ARM_POWER", "HN01_L_ARM_DATA"
    if module in {"A02", "G02"}:
        return "HN01_R_ARM_POWER", "HN01_R_ARM_DATA"
    if module in {"L01", "F01"}:
        return "HN01_L_LEG_POWER", "HN01_L_LEG_DATA"
    if module in {"L02", "F02"}:
        return "HN01_R_LEG_POWER", "HN01_R_LEG_DATA"
    return "HN01_TORSO_POWER_SPINE", "HN01_TORSO_DATA_SPINE"


def build() -> dict[str, int | float]:
    OUT.mkdir(parents=True, exist_ok=True)
    axes = read_csv(WB / "joint-axis-schedule.csv")
    bindings = read_csv(WB / "actuator-bus-axis-binding.csv")
    trunks = read_csv(WB / "harness-route-register.csv")
    equipment = read_csv(WB / "installed-equipment-register.csv")
    terminals = read_csv(WB / "electrical/kicad/hr30-whole-body-electrical-p0.1/connector-schedule.csv")
    buses = read_csv(WB / "harness/bus-harness-assembly-register.csv")
    assemblies = read_csv(WB / "harness/harness-assembly-register.csv")
    terminations = read_csv(WB / "harness/bus-termination-register.csv")
    if (len(axes), len(bindings), len(buses), len(assemblies)) != (25, 25, 8, 14):
        raise SystemExit("controlled whole-body harness source count drift")

    by_axis = {r["axis_id"]: r for r in axes}
    binding_by_axis = {r["axis_id"]: r for r in bindings}

    source_paths = [
        WB / "joint-axis-schedule.csv", WB / "actuator-bus-axis-binding.csv",
        WB / "harness-route-register.csv", WB / "installed-equipment-register.csv",
        WB / "electrical/kicad/hr30-whole-body-electrical-p0.1/connector-schedule.csv",
        WB / "harness/bus-harness-assembly-register.csv", WB / "harness/harness-assembly-register.csv",
        WB / "harness/bus-termination-register.csv", Path(__file__),
    ]
    write_csv(OUT / "source-register.csv", [{
        "source": p.relative_to(ROOT).as_posix(), "sha256": sha256(p),
        "use": "configuration-bound input", "warning": WARNING,
    } for p in source_paths])

    assembly_rows = []
    for row in assemblies:
        assembly_rows.append({
            **row,
            "entry_datum": "DEFINED BY ROUTE-POINT REGISTER; MODULE INTERFACE DATUM VALIDATION OPEN",
            "exit_datum": "DEFINED BY ROUTE-POINT REGISTER; MODULE INTERFACE DATUM VALIDATION OPEN",
            "drawing_state": "P0.1 PHYSICAL ROUTE ALLOCATION PRESENT - CUT LENGTH/CONNECTORS/RETENTION OPEN",
            "authority": AUTHORITY,
        })
    write_csv(OUT / "harness-assembly-register.csv", assembly_rows)

    route_rows: list[dict] = []
    point_rows: list[dict] = []
    for route in trunks:
        a, b = xyz(route["start_xyz_mm"]), xyz(route["end_xyz_mm"])
        route_rows.append({
            "segment_id": route["route_id"], "segment_kind": "FIXED BODY CORRIDOR",
            "assembly_id": "HN-C01" if "TORSO" in route["route_id"] else "HN-P01",
            "service": route["service_class"], "from_point": route["route_id"] + "-P01",
            "to_point": route["route_id"] + "-P02", "planning_length_mm": f"{dist(a,b):.3f}",
            "minimum_bend_radius_mm": route["minimum_dynamic_bend_radius_mm"],
            "corridor_diameter_mm": route["corridor_diameter_mm"],
            "separation_rule": route["separation_rule"], "selection_state": "CORRIDOR RESERVED; PHYSICAL CABLE OPEN",
            "authority": AUTHORITY,
        })
        for n, p in ((1, a), (2, b)):
            point_rows.append({
                "point_id": f"{route['route_id']}-P0{n}", "segment_id": route["route_id"],
                "sequence": n, "x_mm": f"{p[0]:.3f}", "y_mm": f"{p[1]:.3f}", "z_mm": f"{p[2]:.3f}",
                "datum_basis": "WHOLE-BODY RESERVED CORRIDOR CENTERLINE", "tolerance": OPEN,
            })

    axis_rows: list[dict] = []
    loop_rows: list[dict] = []
    power_rows: list[dict] = []
    link_rows: list[dict] = []
    connector_rows: list[dict] = []
    contact_rows: list[dict] = []
    core_rows: list[dict] = []
    retention_rows: list[dict] = []
    derating_rows: list[dict] = []
    stall = {"XH540": 4.9, "XM540": 4.4, "XM430": 2.3, "XC330": 0.88}
    for binding in bindings:
        axis = binding["axis_id"]
        a = by_axis[axis]
        center = (float(a["x_mm"]), float(a["y_mm"]), float(a["z_mm"]))
        family, bus = binding["actuator_family"], binding["bus_id"]
        pseg, dseg = f"LOOP-{axis}-PWR", f"LOOP-{axis}-DATA"
        module = axis_module(axis)
        for service, seg, xoff, y0, y1 in (("ACTUATOR POWER", pseg, 5.0, -14.0, 14.0), ("DATA", dseg, -5.0, -10.0, 10.0)):
            p1 = (center[0] + xoff, center[1] + y0, center[2])
            p2 = (center[0] + xoff, center[1] + y1, center[2])
            route_rows.append({
                "segment_id": seg, "segment_kind": "MOVING JOINT LOOP", "assembly_id": module,
                "service": service, "from_point": seg + "-P01", "to_point": seg + "-P02",
                "planning_length_mm": f"{dist(p1,p2):.3f}", "minimum_bend_radius_mm": OPEN,
                "corridor_diameter_mm": OPEN,
                "separation_rule": "POWER/DATA LOCAL LOOPS OFFSET 10 mm IN X; VERIFY THROUGH FULL JOINT RANGE",
                "selection_state": "GEOMETRY CANDIDATE - SWEEP/CUT LENGTH/FLEX LIFE/CLAMP TEST OPEN", "authority": AUTHORITY,
            })
            for n, p in ((1, p1), (2, p2)):
                point_rows.append({
                    "point_id": f"{seg}-P0{n}", "segment_id": seg, "sequence": n,
                    "x_mm": f"{p[0]:.3f}", "y_mm": f"{p[1]:.3f}", "z_mm": f"{p[2]:.3f}",
                    "datum_basis": f"OFFSET FROM {axis} CANDIDATE AXIS DATUM", "tolerance": OPEN,
                })
        axis_rows.append({
            "axis_id": axis, "module_assembly": module, "bus_id": bus,
            "segment_position": binding["segment_position_provisional"], "actuator_family": family,
            "axis_xyz_mm": fxyz(center), "axis_direction": f"({a['direction_x']},{a['direction_y']},{a['direction_z']})",
            "power_trunk": trunk_for(axis, "POWER"), "power_loop": pseg,
            "data_trunk": trunk_for(axis, "DATA"), "data_loop": dseg,
            "physical_range_sweep": "NOT EXECUTED", "authority": AUTHORITY,
        })
        loop_rows.append({
            "axis_id": axis, "power_loop": pseg, "data_loop": dseg,
            "joint_axis_xyz_mm": fxyz(center), "joint_axis_direction": f"({a['direction_x']},{a['direction_y']},{a['direction_z']})",
            "commanded_range": a["provisional_commanded_range"], "minimum_bend_radius": OPEN,
            "slack_length": OPEN, "clamp_locations": OPEN, "flex_cycle_requirement": OPEN,
            "collision_and_pinch_sweep": "NOT EXECUTED", "state": "OBLIGATION GEOMETRY PRESENT - PHYSICAL RELEASE OPEN",
        })
        amps = stall[family]
        power_rows.append({
            "drop_id": f"PWR-{axis}", "axis_id": axis, "bus_branch": bus,
            "branch_net": f"{axis}_VDD", "return_net": f"{bus}_RET",
            "protection_topology": "ONE DISTINCT PROTECTION / TELEMETRY BOUNDARY PER ACTUATOR; VALUE AND DEVICE SELECTION OPEN",
            "candidate_12v_stall_endpoint_a": f"{amps:.2f}",
            "endpoint_boundary": "DATASHEET MOMENTARY STALL ENDPOINT; NOT DEMAND/RATING",
            "conductor_size": OPEN, "connector_limit": OPEN, "branch_protection": OPEN,
            "fault_current_length_ambient_bundling_inrush_duty_jurisdiction": "ALL REQUIRED",
            "authority": AUTHORITY,
        })
        link_rows.append({
            "link_id": f"LINK-{axis}", "bus_id": bus, "axis_id": axis,
            "ordinal": binding["segment_position_provisional"], "protocol": binding["protocol"],
            "controller_boundary": binding["controller_side_connector_and_pin_mapping"],
            "actuator_boundary": binding["connector_pin_mapping"],
            "vdd_isolation_rule": "STANDARD DYNAMIXEL CABLE VDD CONTACT MUST NOT PARALLEL A DIFFERENT PROTECTED BRANCH",
            "custom_breakout_or_depinning": OPEN, "continuity_no_backfeed_test": "NOT EXECUTED", "authority": AUTHORITY,
        })
        conn_id = f"J-ACT-{axis}"
        connector_rows.append({
            "connector_id": conn_id, "location": axis, "function": "COMBINED ACTUATOR POWER AND DATA",
            "candidate_housing": binding["actuator_side_housing"], "mating_part": OPEN,
            "contact_order_code": binding["actuator_side_crimp_terminal"], "contact_count": binding["actuator_connector_contacts"],
            "keying_retention_strain_relief": OPEN, "source": binding["official_interface_source"],
            "source_date": binding["official_interface_accessed_date"], "selection_state": "DEVICE INTERFACE VERIFIED; HARNESS ASSEMBLY OPEN",
        })
        pins = [("1", "GND", "POWER RETURN"), ("2", "VDD", "ACTUATOR POWER")]
        if binding["protocol"].startswith("RS-485"):
            pins += [("3", "DATA+", "DATA"), ("4", "DATA-", "DATA")]
        else:
            pins += [("3", "DATA", "DATA")]
        for pin, net, service in pins:
            physical_net = f"{axis}_VDD" if net == "VDD" else (f"{bus}_RET" if net == "GND" else f"{bus}_{net}")
            source_contact = f"PBR-{axis}/{net}" if net == "VDD" else f"BRK-{bus}/{net}"
            contact_rows.append({
                "connector_id": conn_id, "contact": pin, "axis_id": axis, "signal": net,
                "bus_net": physical_net, "service": service,
                "wire_core": f"CORE-{axis}-{net.replace('+','P').replace('-','N')}",
                "physical_pin_state": "VERIFIED AT ACTUATOR INTERFACE", "end_to_end_test": "NOT EXECUTED",
            })
            core_rows.append({
                "core_id": f"CORE-{axis}-{net.replace('+','P').replace('-','N')}", "axis_id": axis,
                "from_connector_contact": source_contact, "to_connector_contact": f"{conn_id}/{pin}",
                "net": physical_net, "service": service, "route": pseg if service.startswith("POWER") or service == "ACTUATOR POWER" else dseg,
                "conductor_cross_section": OPEN, "insulation_temperature_flex": OPEN,
                "shield_or_twist": OPEN, "cut_length_and_slack": OPEN, "authority": AUTHORITY,
            })
        retention_rows.append({
            "retention_id": f"RET-{axis}", "axis_id": axis, "power_loop": pseg, "data_loop": dseg,
            "fixed_side_clamp": OPEN, "moving_side_clamp": OPEN, "connector_load_isolation": "REQUIRED",
            "minimum_pull_test": OPEN, "abrasion_guard": OPEN, "inspection_access": OPEN, "validation": "NOT EXECUTED",
        })
        derating_rows.append({
            "circuit": f"PWR-{axis}", "bus_branch": bus, "endpoint_current_a": f"{amps:.2f}",
            "normal_rms_current_a": OPEN, "fault_current_a": OPEN, "length_mm": OPEN,
            "ambient_c": OPEN, "bundle_count": OPEN, "duty_cycle": OPEN, "inrush": OPEN,
            "connector_limit_a": OPEN, "conductor_selection": OPEN, "calculation_state": "BLOCKED BY REQUIRED INPUTS",
        })

    write_csv(OUT / "route-segment-register.csv", route_rows)
    write_csv(OUT / "route-point-register.csv", point_rows)
    write_csv(OUT / "axis-harness-binding.csv", axis_rows)
    write_csv(OUT / "service-loop-register.csv", loop_rows)
    write_csv(OUT / "actuator-power-drop-register.csv", power_rows)
    write_csv(OUT / "bus-physical-link-register.csv", link_rows)
    write_csv(OUT / "connector-instance-register.csv", connector_rows)
    write_csv(OUT / "connector-contact-map.csv", contact_rows)
    write_csv(OUT / "cable-core-register.csv", core_rows)
    write_csv(OUT / "retention-strain-relief-register.csv", retention_rows)
    write_csv(OUT / "current-derating-register.csv", derating_rows)

    termination_rows = []
    for row in terminations:
        termination_rows.append({
            **row, "controller_connector": next(b["controller_interface"] for b in buses if b["bus_id"] == row["bus_id"]),
            "far_end_axis": max((b for b in bindings if b["bus_id"] == row["bus_id"]), key=lambda x: int(x["segment_position_provisional"]))["axis_id"],
            "physical_validation": "NOT EXECUTED", "authority": AUTHORITY,
        })
    write_csv(OUT / "bus-termination-register.csv", termination_rows)

    equipment_rows = []
    for eq in equipment:
        pwr, data = equipment_route(eq["module"], eq["role"])
        equipment_rows.append({
            "item_id": eq["item_id"], "module": eq["module"], "role": eq["role"], "candidate": eq["candidate"],
            "center_xyz_mm": f"({eq['center_x_mm']},{eq['center_y_mm']},{eq['center_z_mm']})",
            "power_route": pwr, "data_route": data, "connector_boundary": eq["connector_boundary"],
            "physical_connector": OPEN, "contact_map": OPEN, "retention": OPEN,
            "continuity_function_test": "NOT EXECUTED", "authority": AUTHORITY,
        })
    write_csv(OUT / "equipment-interface-register.csv", equipment_rows)

    logical_rows = []
    for t in terminals:
        net = t.get("net_name", t.get("net", ""))
        logical_rows.append({
            **t, "physical_binding_state": "LOGICAL TERMINAL RETAINED; PHYSICAL CONTACT SELECTION REQUIRED",
            "route_classification": "ACTUATOR BUS" if any(b["bus_id"] in net for b in buses) else "AUXILIARY / SAFETY / ENERGY / COMPUTE",
            "physical_connector": OPEN, "physical_contact": OPEN, "cable_core": OPEN,
            "inspection_state": "NOT EXECUTED", "authority": AUTHORITY,
        })
    write_csv(OUT / "logical-terminal-binding.csv", logical_rows)

    shield_rows = [{
        "bus_id": b["bus_id"], "protocol": b["protocol"], "candidate_shield_scope": OPEN,
        "controller_end_bond": OPEN, "far_end_bond": OPEN, "frame_bond": OPEN,
        "drain_wire_route": OPEN, "ground_loop_review": "NOT EXECUTED", "emc_test": "NOT EXECUTED",
    } for b in buses]
    write_csv(OUT / "shield-bond-register.csv", shield_rows)

    inspections = [
        ("INSP-01", "document/configuration", "all connector IDs, contacts, wire numbers and revision match as-built", "100%", "before fabrication release"),
        ("INSP-02", "continuity", "point-to-point continuity against connector-contact map", "100%", "before any connection"),
        ("INSP-03", "isolation", "no unintended VDD continuity between any of the 25 separately protected actuator feeds", "100%", "before actuator connection"),
        ("INSP-04", "polarity", "VDD/return polarity and data pair identity", "100%", "before actuator connection"),
        ("INSP-05", "shield/bond", "bond endpoints and insulation from unintended frame points", "100%", "before EMC testing"),
        ("INSP-06", "retention", "connector retention and strain-relief pull", OPEN, "before motion"),
        ("INSP-07", "joint sweep", "full commanded-range clearance, bend radius and pinch inspection", "25 axes", "unpowered before motion"),
        ("INSP-08", "current injection", "current-limited branch voltage-drop/thermal check", OPEN, "guarded bench only after approved test plan"),
        ("INSP-09", "communications", "termination/waveform/reflection/error-rate test", "8 buses", "guarded bench only after approved test plan"),
        ("INSP-10", "post-cycle", "abrasion, conductor damage, retention and continuity after flex-cycle target", OPEN, "before walking development"),
    ]
    write_csv(OUT / "inspection-test-register.csv", [{
        "test_id": i, "test_class": c, "method": m, "sample_or_limit": s, "gate": g,
        "procedure": OPEN, "result": "NOT EXECUTED", "authority": AUTHORITY,
    } for i, c, m, s, g in inspections])

    unresolved = [
        ("HSEL-01", "all power conductors", "cross-section/insulation/flex construction", "fault current, RMS/peak duty, length, ambient, bundling, voltage-drop, jurisdiction"),
        ("HSEL-02", "25 actuator power feeds", "individual fuse/current limiter, distribution and disconnect implementation", "prospective fault current, inrush, coordination, DC interrupt rating, connector/conductor limits"),
        ("HSEL-03", "25 actuator drops", "custom data-only/power-injection breakout construction", "controlled drawing, crimp process, no-backfeed continuity and fault-injection evidence"),
        ("HSEL-04", "all moving joints", "dynamic cable family, slack and minimum bend radius", "joint sweep, cycle target, torsion, temperature, abrasion and supplier flex data"),
        ("HSEL-05", "eight data buses", "termination/bias/baud/shielding", "measured topology, cable impedance/length, transceiver limits, waveform and EMC tests"),
        ("HSEL-06", "equipment interfaces", "mating connectors/contacts/keying", "manufacturer pinout/revision, voltage/current, retention, service access and procurement availability"),
        ("HSEL-07", "retention", "clamps, grommets, strain relief and abrasion protection", "full geometry, pull load, serviceability, material/fire/environment evidence"),
        ("HSEL-08", "battery/safety/charge", "physical harness implementation", "qualified electrical review, protection study, PE/0V decision, service disconnect and interlock validation"),
        ("HSEL-09", "jurisdiction", "applicable wiring/fire/product requirements", "Boston build/use venue, equipment classification and qualified review"),
        ("HSEL-10", "all harnesses", "manufacturing and inspection process", "drawing release, tooling, crimp validation, pull test, labeling, traceability and as-built record"),
    ]
    write_csv(OUT / "unresolved-harness-selections.csv", [{
        "selection_id": i, "scope": s, "selection": sel, "evidence_needed": e,
        "state": OPEN, "authority": AUTHORITY,
    } for i, s, sel, e in unresolved])

    stats = {
        "fixed_route_segments": len(trunks), "moving_joint_route_segments": 50,
        "total_route_segments": len(route_rows), "route_points": len(point_rows),
        "axes": len(axis_rows), "buses": len(buses), "harness_assemblies": len(assembly_rows),
        "equipment_items": len(equipment_rows), "logical_terminals": len(logical_rows),
        "actuator_connector_contacts": len(contact_rows), "cable_cores": len(core_rows),
        "candidate_12v_stall_endpoint_sum_a": round(sum(float(r["candidate_12v_stall_endpoint_a"]) for r in power_rows), 2),
    }
    write_visuals(route_rows, point_rows, axis_rows, buses, stats)
    status = {
        "identifier": IDENTIFIER, "warning": WARNING, "scope": "complete HR-30 P0.1 physical harness architecture",
        **stats, "topology": "25 separately protected actuator feeds / 8 data-only multidrop buses / data-only controller boundaries",
        "route_geometry_candidate_present": True, "every_axis_has_power_and_data_loop": True,
        "every_equipment_item_bound": True, "every_logical_terminal_retained": True,
        "standard_dynamixel_cable_direct_use_approved": False, "assembled_cables_selected": False,
        "conductor_sizing_released": False, "protection_released": False, "connector_set_released": False,
        "harness_validated": False, "procurement_authority": False, "fabrication_authority": False,
        "connection_authority": False, "powered_test_authority": False, "motion_authority": False,
        "energization_authority": False,
    }
    (OUT / "physical-harness-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    readme = f"""# HR-30 whole-body physical harness P0.1

**{WARNING}**

This is the first complete physical translation of the HR-30 logical wiring architecture. It binds all **{stats['axes']} joints**, **{stats['buses']} actuator buses**, **{stats['equipment_items']} installed equipment items**, and **{stats['logical_terminals']} current ECAD logical terminals** to a controlled harness architecture.

It contains {stats['fixed_route_segments']} body corridors plus 50 explicit moving-joint power/data loops ({stats['total_route_segments']} route segments and {stats['route_points']} route points). Each actuator has a known device-side contact map, a branch-power relationship, a data-link boundary, a moving-loop obligation, retention obligation, derating inputs, and an inspection path.

The architecture now allocates one separately protected power feed to every actuator. A standard ROBOTIS X3P/X4P daisy cable carries VDD, so it cannot be used unchanged because it would parallel those 25 feeds. A custom/de-pinned data-only harness or power-injection breakout remains **SELECTION REQUIRED**.

The 76.08 A figure is only the sum of manufacturer 12 V momentary stall-current endpoints. It is not expected demand, a conductor rating, a fuse value, or permission to power the robot.

Open the [interactive physical harness guide](index.html). Start with `axis-harness-binding.csv`, `route-segment-register.csv`, `connector-contact-map.csv`, and `unresolved-harness-selections.csv`.

No cable cut length, conductor size, protection value, complete connector set, retention hardware, shielding decision, or powered validation is released by this package.
"""
    (OUT / "README.md").write_text(readme, encoding="utf-8")
    return stats


def write_visuals(routes: list[dict], points: list[dict], axes: list[dict], buses: list[dict], stats: dict) -> None:
    pmap = {p["point_id"]: p for p in points}
    def project(p: dict) -> tuple[float, float]:
        return 390 + float(p["x_mm"]) * 1.72, 720 - float(p["z_mm"]) * 0.86
    lines = []
    for r in routes:
        a, b = pmap[r["from_point"]], pmap[r["to_point"]]
        x1,y1 = project(a); x2,y2 = project(b)
        cls = "power" if "POWER" in r["service"] else "data"
        lines.append(f'<line class="route {cls}" data-kind="{r["segment_kind"]}" x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}"><title>{html.escape(r["segment_id"])} · {html.escape(r["service"])}</title></line>')
    dots = []
    for a in axes:
        x,y,z = xyz(a["axis_xyz_mm"]); sx,sy = 390+x*1.72, 720-z*0.86
        dots.append(f'<circle class="joint" cx="{sx:.1f}" cy="{sy:.1f}" r="4"><title>{html.escape(a["axis_id"])} · {html.escape(a["bus_id"])}</title></circle>')
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 780 760" role="img" aria-labelledby="title desc"><title id="title">HR-30 physical harness front map</title><desc id="desc">Complete preliminary routing map with fixed body corridors, joint loops and all 25 actuator axes.</desc><style>text{{font-family:Arial,sans-serif;fill:#0d2d57}}.body{{fill:#d8f1ff;stroke:#123f73;stroke-width:3}}.route{{stroke-width:5;fill:none;stroke-linecap:round;opacity:.86}}.power{{stroke:#f4b400}}.data{{stroke:#179de3}}.joint{{fill:#fff;stroke:#123f73;stroke-width:2}}.label{{font-size:16px;font-weight:700}}</style><rect width="780" height="760" rx="24" fill="#f8fcff"/><g class="body"><rect x="310" y="210" width="160" height="190" rx="24"/><rect x="332" y="68" width="116" height="112" rx="40"/><rect x="350" y="180" width="80" height="35" rx="12"/><rect x="260" y="240" width="48" height="260" rx="22"/><rect x="472" y="240" width="48" height="260" rx="22"/><rect x="320" y="400" width="140" height="75" rx="24"/><rect x="320" y="472" width="58" height="240" rx="22"/><rect x="402" y="472" width="58" height="240" rx="22"/></g><g>{''.join(lines)}</g><g>{''.join(dots)}</g><text class="label" x="24" y="34">Gold: actuator power · Sky blue: data/low voltage · White dots: 25 joints</text><text x="24" y="58" font-size="14">Geometry candidate only; bend radius, slack, clamps, cable OD and joint sweeps remain open.</text></svg>'''
    (OUT / "whole-body-physical-harness.svg").write_text(svg, encoding="utf-8")

    bus_cards = "".join(f'<button class="bus" data-bus="{html.escape(b["bus_id"])}"><strong>{html.escape(b["bus_id"])}</strong><span>{html.escape(b["protocol"])} · {html.escape(b["axis_count"])} axes</span><span>{html.escape(b["candidate_12v_stall_endpoint_sum_a"])} A endpoint sum</span></button>' for b in buses)
    axis_cards = "".join(f'<tr data-bus="{html.escape(a["bus_id"])}"><td>{html.escape(a["axis_id"])}</td><td>{html.escape(a["bus_id"])}</td><td>{html.escape(a["actuator_family"])}</td><td>{html.escape(a["axis_xyz_mm"])}</td><td>{html.escape(a["power_loop"])}<br>{html.escape(a["data_loop"])}</td></tr>' for a in axes)
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 physical harness P0.1</title><style>:root{{--navy:#0d2d57;--blue:#179de3;--sky:#d8f1ff;--gold:#f4b400;--paper:#f8fcff}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--navy);font:16px/1.5 system-ui,sans-serif}}header{{background:linear-gradient(135deg,var(--navy),#185d9d);color:white;padding:32px max(24px,calc((100% - 1180px)/2))}}h1{{font-size:clamp(32px,5vw,60px);line-height:1.05;margin:.2em 0}}.warning{{background:var(--gold);color:#1b2840;padding:14px 18px;font-weight:800;border-radius:12px}}main{{max-width:1180px;margin:auto;padding:28px 20px 70px}}h2{{font-size:clamp(25px,3vw,38px);margin-top:46px}}.stats,.buses{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:14px}}.stat,.bus,.panel{{background:white;border:2px solid #9bd5f5;border-radius:16px;padding:18px;box-shadow:0 6px 18px #0d2d5712}}.stat strong{{display:block;font-size:28px}}.bus{{font:inherit;color:inherit;text-align:left;cursor:pointer}}.bus strong,.bus span{{display:block}}.bus.active{{border-color:var(--gold);box-shadow:0 0 0 3px #f4b40055}}.map{{width:100%;max-height:760px}}.tablewrap{{overflow:auto;border:2px solid #9bd5f5;border-radius:16px;background:white}}table{{border-collapse:collapse;width:100%;min-width:900px}}th,td{{padding:13px 14px;border-bottom:1px solid #cfeafa;text-align:left;vertical-align:top}}th{{position:sticky;top:0;background:var(--navy);color:white;font-size:14px}}td{{font-size:14px}}a{{color:#075f9f;font-weight:700}}.open{{border-left:8px solid var(--gold)}}@media(max-width:600px){{header{{padding:24px 18px}}main{{padding:20px 14px}}}}</style></head><body><header><div class="warning">{html.escape(WARNING)}</div><p>HR-30 · Whole-body P0.1</p><h1>Physical harness guide</h1><p>Every body corridor, actuator feed, data bus, joint loop and current ECAD terminal is accounted for—without pretending unresolved cable and protection choices are finished.</p></header><main><section class="stats"><div class="stat"><strong>{stats['axes']}</strong>separate actuator feeds</div><div class="stat"><strong>{stats['total_route_segments']}</strong>route segments</div><div class="stat"><strong>{stats['logical_terminals']}</strong>logical terminals</div><div class="stat"><strong>{stats['candidate_12v_stall_endpoint_sum_a']}</strong>A endpoint sum, not demand</div></section><h2>Whole-body route map</h2><div class="panel"><img class="map" src="whole-body-physical-harness.svg" alt="Front map of the HR-30 physical harness routes and joint loops"></div><h2>Eight data buses</h2><p>Select a data bus to filter the joint table; select it again to show all.</p><div class="buses">{bus_cards}</div><h2>All 25 protected-feed candidates</h2><div class="tablewrap"><table><thead><tr><th>Axis</th><th>Data bus</th><th>Actuator</th><th>Joint datum (mm)</th><th>Moving loops</th></tr></thead><tbody>{axis_cards}</tbody></table></div><h2>Critical power boundary</h2><div class="panel open"><p>Each actuator now has its own protection/telemetry boundary and VDD net. Standard ROBOTIS X3P/X4P cables include VDD, so a custom data-only/power-injection breakout or controlled depinning method is required to keep the 25 feeds isolated.</p><p>The 76.08 A figure is the arithmetic sum of momentary 12 V stall-current endpoints—not a normal-load forecast, fuse rating, cable rating, or permission to energize.</p></div><h2>Build registers</h2><div class="panel"><p><a href="route-segment-register.csv">route segments</a> · <a href="route-point-register.csv">route points</a> · <a href="axis-harness-binding.csv">axis bindings</a> · <a href="connector-contact-map.csv">actuator contacts</a> · <a href="cable-core-register.csv">cable cores</a> · <a href="equipment-interface-register.csv">equipment interfaces</a> · <a href="logical-terminal-binding.csv">logical terminals</a> · <a href="current-derating-register.csv">derating inputs</a> · <a href="inspection-test-register.csv">inspection/tests</a> · <a href="unresolved-harness-selections.csv">open selections</a></p></div></main><script>const buttons=[...document.querySelectorAll('.bus')],rows=[...document.querySelectorAll('tbody tr')];buttons.forEach(b=>b.addEventListener('click',()=>{{const on=!b.classList.contains('active');buttons.forEach(x=>x.classList.remove('active'));b.classList.toggle('active',on);rows.forEach(r=>r.hidden=on&&r.dataset.bus!==b.dataset.bus)}}));</script></body></html>'''
    (OUT / "index.html").write_text(page, encoding="utf-8")


def manifest_and_release() -> None:
    manifest = OUT / "file-manifest.csv"
    if manifest.exists(): manifest.unlink()
    rows = [{"path": p.relative_to(OUT).as_posix(), "bytes": p.stat().st_size, "sha256": sha256(p), "warning": WARNING} for p in sorted(OUT.rglob("*")) if p.is_file()]
    write_csv(manifest, rows)
    if RELEASE.exists(): shutil.rmtree(RELEASE)
    shutil.copytree(OUT, RELEASE)


def integrate_whole_body_package(stats: dict) -> None:
    readme_path = WB / "README.md"
    readme = readme_path.read_text(encoding="utf-8")
    marker = "## Physical whole-body harness P0.1"
    block = f"""

{marker}

The [interactive physical harness guide](harness/physical-p0.1/index.html) translates the logical ECAD into {stats['total_route_segments']} route segments: 12 reserved body corridors and two moving-loop candidates at every one of the 25 joint axes. It retains all {stats['logical_terminals']} current logical terminals and binds every installed equipment item without inventing unresolved conductor sizes, fuse values, connectors, or cable order codes.

This is routing and interface architecture, not a released cable set. All 25 actuator feeds have distinct protection boundaries, but no protection value or implementation is released. Custom data-only/power-injection breakouts, cable sizing, retention, flex-life, EMC, and physical validation remain selection required.
"""
    if marker in readme:
        start = readme.index(marker)
        end = readme.find("\n## ", start + len(marker))
        readme = readme[:start].rstrip() + "\n\n" + block.strip() + ("\n\n" + readme[end + 1:] if end >= 0 else "\n")
    else:
        readme = readme.rstrip() + "\n\n" + block.strip() + "\n"
    readme_path.write_text(readme, encoding="utf-8")

    index_path = WB / "index.html"
    page = index_path.read_text(encoding="utf-8")
    harness_link = '<a href="harness/physical-p0.1/index.html">Interactive physical harness</a>'
    if harness_link not in page:
        needle = '<a href="harness-route-register.csv">Harness routes</a>'
        if needle not in page:
            raise SystemExit("whole-body web integration anchor missing")
        page = page.replace(needle, needle + " · " + harness_link, 1)
        index_path.write_text(page, encoding="utf-8")

    status_path = WB / "package-status.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    status.update({
        "physical_harness_package_present": True,
        "physical_harness_route_segments": stats["total_route_segments"],
        "physical_harness_route_points": stats["route_points"],
        "physical_harness_axes_bound": stats["axes"],
        "physical_harness_logical_terminals_retained": stats["logical_terminals"],
        "physical_harness_selected": False,
        "physical_harness_validated": False,
    })
    status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    stats = build()
    shutil.copy2(Path(__file__), OUT / "physical-harness-source.py")
    manifest_and_release()
    integrate_whole_body_package(stats)
    import generate_hr30_system_package_p01 as system_package
    system_package.refresh_manifest_and_release()
    print(json.dumps({"identifier": IDENTIFIER, **stats}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
