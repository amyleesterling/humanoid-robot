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
from collections import defaultdict
from pathlib import Path

import cadquery as cq


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


def normalize_step_text(path: Path) -> None:
    """Remove exporter-only trailing spaces while preserving STEP content."""
    lines = path.read_text(encoding="utf-8").splitlines()
    path.write_text("\n".join(line.rstrip() for line in lines) + "\n", encoding="utf-8", newline="\n")


def xyz(text: str) -> tuple[float, float, float]:
    return tuple(float(v.strip()) for v in text.strip("() ").split(","))  # type: ignore[return-value]


def fxyz(p: tuple[float, float, float]) -> str:
    return f"({p[0]:.3f},{p[1]:.3f},{p[2]:.3f})"


def dist(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    return math.sqrt(sum((a[i] - b[i]) ** 2 for i in range(3)))


def body_box(
    width: float,
    depth: float,
    height: float,
    x: float,
    y: float,
    z0: float,
) -> cq.Shape:
    """Create a lightweight whole-body context envelope from a bottom datum."""
    return cq.Workplane("XY").box(width, depth, height).translate((x, y, z0 + height / 2)).val()


def rod_between(
    start: tuple[float, float, float],
    end: tuple[float, float, float],
    radius: float,
) -> cq.Shape:
    vector = tuple(end[i] - start[i] for i in range(3))
    length = math.sqrt(sum(value * value for value in vector))
    if length <= 0:
        raise ValueError(f"zero-length route from {start} to {end}")
    direction = cq.Vector(*(value / length for value in vector))
    return cq.Solid.makeCylinder(radius, length, cq.Vector(*start), direction)


def write_route_cad(routes: list[dict], points: list[dict]) -> int:
    """Export all 62 registered centerlines in a recognizable 762 mm body.

    The route rods are visualization/reference geometry.  Their display
    diameter is deliberately not a cable OD, bundle diameter, clearance, or
    bend-radius release.
    """
    pmap = {
        row["point_id"]: (float(row["x_mm"]), float(row["y_mm"]), float(row["z_mm"]))
        for row in points
    }
    assembly = cq.Assembly(name="HR30_WHOLE_BODY_HARNESS_CENTERLINES_P0_1")
    body_color = cq.Color(0.33, 0.68, 0.88, 0.22)
    dark_color = cq.Color(0.04, 0.19, 0.36, 0.30)
    gold = cq.Color(0.95, 0.64, 0.02, 1.0)
    sky = cq.Color(0.05, 0.61, 0.90, 1.0)

    # Lightweight context only: exact physical body geometry remains in the
    # authoritative whole-body STEP/GLB.  These envelopes make the route
    # assembly immediately recognizable without duplicating the 90 MB model.
    context = (
        ("BODY-LEFT-FOOT", body_box(105, 170, 35, 62.5, 18, 0), body_color),
        ("BODY-RIGHT-FOOT", body_box(105, 170, 35, -62.5, 18, 0), body_color),
        ("BODY-LEFT-LEG", body_box(55, 72, 375, 62.5, 0, 35), body_color),
        ("BODY-RIGHT-LEG", body_box(55, 72, 375, -62.5, 0, 35), body_color),
        ("BODY-PELVIS", body_box(180, 100, 80, 0, 0, 410), dark_color),
        ("BODY-TORSO", body_box(210, 108, 170, 0, 0, 490), dark_color),
        ("BODY-HEAD", body_box(142, 112, 102, 0, 0, 660), body_color),
        ("BODY-LEFT-ARM", body_box(62, 70, 295, 135, 0, 295), body_color),
        ("BODY-RIGHT-ARM", body_box(62, 70, 295, -135, 0, 295), body_color),
        ("BODY-LEFT-HAND", body_box(54, 58, 70, 140, 0, 225), body_color),
        ("BODY-RIGHT-HAND", body_box(54, 58, 70, -140, 0, 225), body_color),
    )
    for name, shape, color in context:
        assembly.add(shape, name=name, color=color)

    cad_rows = []
    for route in routes:
        start = pmap[route["from_point"]]
        end = pmap[route["to_point"]]
        power = "POWER" in route["service"]
        radius = 1.5 if power else 1.0
        shape = rod_between(start, end, radius)
        solid_name = "ROUTE-" + route["segment_id"]
        assembly.add(shape, name=solid_name, color=gold if power else sky)
        cad_rows.append({
            "segment_id": route["segment_id"],
            "solid_name": solid_name,
            "segment_kind": route["segment_kind"],
            "service": route["service"],
            "from_xyz_mm": fxyz(start),
            "to_xyz_mm": fxyz(end),
            "registered_planning_length_mm": route["planning_length_mm"],
            "cad_centerline_length_mm": f"{dist(start, end):.3f}",
            "display_rod_diameter_mm": f"{2 * radius:.1f}",
            "display_color": "GOLD" if power else "SKY BLUE",
            "geometry_interpretation": "REFERENCE CENTERLINE ROD ONLY - NOT CABLE OD, BUNDLE SIZE, CLEARANCE OR BEND-RADIUS RELEASE",
            "authority": AUTHORITY,
        })
    write_csv(OUT / "route-cad-register.csv", cad_rows)
    step_path = OUT / "HR30_whole_body_harness_centerlines_candidate.step"
    assembly.save(str(step_path))
    normalize_step_text(step_path)
    assembly.save(str(OUT / "HR30_whole_body_harness_centerlines_candidate.glb"))
    return len(cad_rows)


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
    actuator_pinouts = read_csv(WB / "harness/actuator-side-pinout-register.csv")
    harness_sources = read_csv(WB / "harness/harness-source-register.csv")
    current_limits = read_csv(WB / "current-constrained-actuation-p0.1/axis-current-torque-register.csv")
    bus_current_budgets = read_csv(WB / "current-constrained-actuation-p0.1/bus-current-budget.csv")
    pdu_allocations = read_csv(WB / "electrical/actuator-branch-pdu-p0.1/board-instance-channel-allocation.csv")
    if (len(axes), len(bindings), len(buses), len(assemblies), len(actuator_pinouts), len(current_limits), len(bus_current_budgets)) != (25, 25, 8, 14, 4, 25, 8):
        raise SystemExit("controlled whole-body harness source count drift")

    by_axis = {r["axis_id"]: r for r in axes}
    binding_by_axis = {r["axis_id"]: r for r in bindings}
    bus_bindings: dict[str, list[dict[str, str]]] = defaultdict(list)
    for binding in bindings:
        bus_bindings[binding["bus_id"]].append(binding)
    for values in bus_bindings.values():
        values.sort(key=lambda row: int(row["segment_position_provisional"]))
    predecessor: dict[str, str | None] = {}
    successor: dict[str, str | None] = {}
    for values in bus_bindings.values():
        for index, binding in enumerate(values):
            predecessor[binding["axis_id"]] = values[index - 1]["axis_id"] if index else None
            successor[binding["axis_id"]] = values[index + 1]["axis_id"] if index + 1 < len(values) else None
    trunk_by_id = {row["route_id"]: row for row in trunks}
    pdu_by_axis = {row["axis_id"]: row for row in pdu_allocations if row["axis_id"] != "DNP SPARE"}
    equipment_by_id = {row["item_id"]: row for row in equipment}
    if len(pdu_by_axis) != 25 or any(f"EQ-{row['board_instance']}" not in equipment_by_id for row in pdu_allocations):
        raise SystemExit("five-board PDU allocation is not installed in the whole-body equipment model")

    source_paths = [
        WB / "joint-axis-schedule.csv", WB / "actuator-bus-axis-binding.csv",
        WB / "harness-route-register.csv", WB / "installed-equipment-register.csv",
        WB / "electrical/actuator-branch-pdu-p0.1/board-instance-channel-allocation.csv",
        WB / "electrical/kicad/hr30-whole-body-electrical-p0.1/connector-schedule.csv",
        WB / "harness/bus-harness-assembly-register.csv", WB / "harness/harness-assembly-register.csv",
        WB / "harness/bus-termination-register.csv", WB / "harness/actuator-side-pinout-register.csv",
        WB / "harness/harness-source-register.csv",
        WB / "current-constrained-actuation-p0.1/axis-current-torque-register.csv",
        WB / "current-constrained-actuation-p0.1/bus-current-budget.csv", Path(__file__),
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
    chain_rows: list[dict] = []
    power_pair_rows: list[dict] = []
    data_link_rows: list[dict] = []
    retention_rows: list[dict] = []
    derating_rows: list[dict] = []
    # Every connector physically present on the five routed PDU assemblies is
    # instantiated here.  Board-side parts are selected by the native KiCad
    # source; cable-side mating contacts, crimp process and retention remain
    # explicit selections.
    for board_id in sorted({row["board_instance"] for row in pdu_allocations}):
        input_id = f"J-{board_id}-IN"
        connector_rows.append({
            "connector_id": input_id, "location": board_id, "function": "CONTROLLED 12 V BOARD INPUT",
            "candidate_housing": "Phoenix Contact MKDS 5/2-9.5 board header 1714971", "mating_part": OPEN,
            "contact_order_code": OPEN, "contact_count": 2, "keying_retention_strain_relief": OPEN,
            "source": "https://www.phoenixcontact.com/en-us/products/pcb-terminal-block-mkds-5-2-95-1714971",
            "source_date": "accessed 2026-08-15", "selection_state": "BOARD HEADER PRESENT; FIELD MATING HARDWARE/CONDUCTOR/RETENTION OPEN",
        })
        for pin, signal in (("1", "PDU_0V"), ("2", "PDU_12V_IN")):
            contact_rows.append({
                "connector_id": input_id, "contact": pin, "axis_id": "BOARD INPUT", "signal": signal,
                "bus_net": signal, "service": "ACTUATOR POWER TRUNK", "wire_core": OPEN,
                "physical_pin_state": "BOARD CONTACT DEFINED; FIELD TERMINATION OPEN", "end_to_end_test": "NOT EXECUTED",
            })
    for allocation in pdu_allocations:
        board_id, channel, axis = allocation["board_instance"], allocation["channel"], allocation["axis_id"]
        output_id, control_id = f"J-{board_id}-OUT-{channel}", f"J-{board_id}-CTL-{channel}"
        connector_rows.extend(({
            "connector_id": output_id, "location": board_id, "function": f"CHANNEL {channel} ACTUATOR OUTPUT",
            "candidate_housing": "JST B2P-VH board header", "mating_part": "JST VHR-2N; contact/conductor selection open",
            "contact_order_code": OPEN, "contact_count": 2, "keying_retention_strain_relief": OPEN,
            "source": "https://www.jst-mfg.com/product/pdf/eng/eVH.pdf", "source_date": "accessed 2026-08-15",
            "selection_state": "BOARD HEADER PRESENT; DNP CHANNEL HAS NO FIELD HARNESS" if axis == "DNP SPARE" else "BOARD HEADER PRESENT; FIELD ASSEMBLY VALIDATION OPEN",
        }, {
            "connector_id": control_id, "location": board_id, "function": f"CHANNEL {channel} DISABLE/POWER-GOOD CONTROL",
            "candidate_housing": "JST BM03B-GHS-TBT board header", "mating_part": "JST GHR-03V-S; contact/conductor selection open",
            "contact_order_code": OPEN, "contact_count": 3, "keying_retention_strain_relief": OPEN,
            "source": "https://www.jst-mfg.com/product/pdf/eng/eGH.pdf", "source_date": "accessed 2026-08-15",
            "selection_state": "BOARD HEADER PRESENT; DNP CHANNEL CONTROL UNPOPULATED" if axis == "DNP SPARE" else "BOARD HEADER PRESENT; CONTROL HARNESS VALIDATION OPEN",
        }))
        output_signals = (("1", "PDU_0V"), ("2", f"BRANCH_{channel}_12V"))
        for pin, signal in output_signals:
            contact_rows.append({
                "connector_id": output_id, "contact": pin, "axis_id": axis, "signal": signal,
                "bus_net": "NO NET - DNP SPARE" if axis == "DNP SPARE" else (f"{pdu_by_axis[axis]['bus_id']}_RET" if pin == "1" else f"{axis}_VDD"),
                "service": "DNP" if axis == "DNP SPARE" else ("POWER RETURN" if pin == "1" else "ACTUATOR POWER"),
                "wire_core": "NONE - DNP" if axis == "DNP SPARE" else f"CORE-{axis}-{'GND' if pin == '1' else 'VDD'}",
                "physical_pin_state": "DNP - NO FIELD HARNESS" if axis == "DNP SPARE" else "BOARD CONTACT DEFINED; FIELD ASSEMBLY OPEN",
                "end_to_end_test": "NOT EXECUTED",
            })
        for pin, signal in (("1", "PDU_0V"), ("2", f"CH{channel}_EN"), ("3", f"CH{channel}_PG")):
            contact_rows.append({
                "connector_id": control_id, "contact": pin, "axis_id": axis, "signal": signal,
                "bus_net": "NO NET - DNP SPARE" if axis == "DNP SPARE" else f"{board_id}_{signal}",
                "service": "DNP" if axis == "DNP SPARE" else "CONTROL/DIAGNOSTIC - ZERO SAFETY CREDIT",
                "wire_core": "NONE - DNP" if axis == "DNP SPARE" else OPEN,
                "physical_pin_state": "DNP - NO FIELD HARNESS" if axis == "DNP SPARE" else "BOARD CONTACT DEFINED; FIELD ASSEMBLY OPEN",
                "end_to_end_test": "NOT EXECUTED",
            })
    stall = {"XH540": 4.9, "XM540": 4.4, "XM430": 2.3, "XC330": 0.88}
    for binding in bindings:
        axis = binding["axis_id"]
        a = by_axis[axis]
        center = (float(a["x_mm"]), float(a["y_mm"]), float(a["z_mm"]))
        family, bus = binding["actuator_family"], binding["bus_id"]
        allocation = pdu_by_axis[axis]
        board_id, channel = allocation["board_instance"], allocation["channel"]
        board_eq = equipment_by_id[f"EQ-{board_id}"]
        board_center = (float(board_eq["center_x_mm"]), float(board_eq["center_y_mm"]), float(board_eq["center_z_mm"]))
        pdu_output = f"J-{board_id}-OUT-{channel}"
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
            "protection_topology": f"{board_id} CHANNEL {channel}; TPS259474L COMMISSIONING CANDIDATE; RILM VARIANT {allocation['r_ilm_variant']}; PHYSICAL VALIDATION OPEN",
            "candidate_12v_stall_endpoint_a": f"{amps:.2f}",
            "endpoint_boundary": "DATASHEET MOMENTARY STALL ENDPOINT; NOT DEMAND/RATING",
            "conductor_size": OPEN, "connector_limit": OPEN, "branch_protection": OPEN,
            "fault_current_length_ambient_bundling_inrush_duty_jurisdiction": "ALL REQUIRED",
            "authority": AUTHORITY,
        })
        previous_axis = predecessor[axis]
        next_axis = successor[axis]
        protocol_is_rs = binding["protocol"].startswith("RS-485")
        data_signals = ["DATA+", "DATA-"] if protocol_is_rs else ["DATA"]
        upstream_endpoint = f"CB-{bus}" if previous_axis is None else f"J-OUT-{previous_axis}"
        outgoing_endpoint = f"J-OUT-{axis}" if next_axis is not None else "NO OUTGOING CABLE - FAR END"
        incoming_pin_map = "1=INDIVIDUAL RETURN; 2=INDIVIDUAL VDD; 3=DATA+; 4=DATA-" if protocol_is_rs else "1=INDIVIDUAL RETURN; 2=INDIVIDUAL VDD; 3=DATA"
        outgoing_pin_map = "1=EMPTY; 2=EMPTY; 3=DATA+; 4=DATA-" if protocol_is_rs else "1=EMPTY; 2=EMPTY; 3=DATA"
        power_one_way_mm = dist(board_center, center) + 28.0
        if previous_axis is None:
            data_route = trunk_by_id[trunk_for(axis, "DATA")]
            data_start = xyz(data_route["start_xyz_mm"])
        else:
            previous = by_axis[previous_axis]
            data_start = (float(previous["x_mm"]), float(previous["y_mm"]), float(previous["z_mm"]))
        data_link_mm = dist(data_start, center) + 20.0
        link_rows.append({
            "link_id": f"LINK-{axis}", "bus_id": bus, "axis_id": axis,
            "ordinal": binding["segment_position_provisional"], "protocol": binding["protocol"],
            "from_endpoint": upstream_endpoint, "to_endpoint": f"J-ACT-{axis}",
            "next_endpoint": outgoing_endpoint,
            "data_conductors": " | ".join(data_signals),
            "reference_path": "INDIVIDUAL PBR RETURN PAIR TO ACTUATOR PIN 1; NO GND CONDUCTOR IN INTER-ACTUATOR DATA LINK",
            "controller_boundary": binding["controller_side_connector_and_pin_mapping"],
            "actuator_boundary": binding["connector_pin_mapping"],
            "vdd_isolation_rule": "STANDARD DYNAMIXEL CABLE VDD CONTACT MUST NOT PARALLEL A DIFFERENT PROTECTED BRANCH",
            "custom_breakout_or_depinning": "CONTROLLED SPLIT-HARNESS CANDIDATE: INPUT HOUSING COMBINES INDIVIDUAL POWER PAIR WITH DATA; OUTGOING HOUSING HAS GND/VDD CAVITIES EMPTY",
            "continuity_no_backfeed_test": "NOT EXECUTED", "authority": AUTHORITY,
        })
        chain_rows.append({
            "bus_id": bus, "ordinal": binding["segment_position_provisional"], "axis_id": axis,
            "upstream_data_endpoint": upstream_endpoint, "input_connector": f"J-ACT-{axis}",
            "input_pin_map": incoming_pin_map, "individual_power_pair": f"PAIR-{axis}",
            "outgoing_connector": outgoing_endpoint, "outgoing_pin_map": outgoing_pin_map if next_axis is not None else "NO OUTGOING HARNESS CONNECTOR",
            "successor_axis": next_axis or "FAR END", "termination_state": "SELECTION REQUIRED AT FAR END" if next_axis is None else "NOT AT THIS NODE",
            "topology_state": "SERIAL DATA TRUNK / INDIVIDUAL TWO-WIRE POWER PAIR; NO STAR DATA STUBS", "authority": AUTHORITY,
        })
        power_pair_rows.append({
            "pair_id": f"PAIR-{axis}", "axis_id": axis, "bus_id": bus,
            "positive_net": f"{axis}_VDD", "return_net": f"{bus}_RET",
            "source_boundary": pdu_output, "destination_connector": f"J-ACT-{axis}",
            "destination_contacts": "1=RETURN; 2=VDD", "one_way_planning_length_mm": f"{power_one_way_mm:.3f}",
            "round_trip_planning_length_mm": f"{2 * power_one_way_mm:.3f}",
            "length_basis": "POWER-CORRIDOR START TO AXIS DATUM PLUS 28 mm LOCAL LOOP; CUT LENGTH/SLACK NOT RELEASED",
            "conductor_selection": OPEN, "authority": AUTHORITY,
        })
        data_link_rows.append({
            "link_id": f"DATA-{axis}", "bus_id": bus, "ordinal": binding["segment_position_provisional"],
            "from_endpoint": upstream_endpoint, "to_endpoint": f"J-ACT-{axis}",
            "conductors": " | ".join(data_signals), "conductor_count": len(data_signals),
            "reference_rule": "ACTUATOR REFERENCE PROVIDED BY INDIVIDUAL POWER-PAIR RETURN; CONTROLLER REFERENCE STAR-TIE/FAULT REVIEW OPEN",
            "planning_length_mm": f"{data_link_mm:.3f}",
            "length_basis": "CONTROLLER-CORRIDOR START OR PREDECESSOR AXIS DATUM TO CURRENT AXIS PLUS 20 mm LOCAL LOOP",
            "twist_impedance_shield": OPEN, "authority": AUTHORITY,
        })
        conn_id = f"J-ACT-{axis}"
        connector_rows.append({
            "connector_id": conn_id, "location": axis, "function": "COMBINED ACTUATOR POWER AND DATA",
            "candidate_housing": binding["actuator_side_housing"], "mating_part": OPEN,
            "contact_order_code": binding["actuator_side_crimp_terminal"], "contact_count": binding["actuator_connector_contacts"],
            "keying_retention_strain_relief": OPEN, "source": binding["official_interface_source"],
            "source_date": binding["official_interface_accessed_date"], "selection_state": "DEVICE INTERFACE VERIFIED; SPLIT-HARNESS CANDIDATE DEFINED; ASSEMBLY VALIDATION OPEN",
        })
        pins = [("1", "GND", "POWER RETURN"), ("2", "VDD", "ACTUATOR POWER")]
        if binding["protocol"].startswith("RS-485"):
            pins += [("3", "DATA+", "DATA"), ("4", "DATA-", "DATA")]
        else:
            pins += [("3", "DATA", "DATA")]
        for pin, net, service in pins:
            physical_net = f"{axis}_VDD" if net == "VDD" else (f"{bus}_RET" if net == "GND" else f"{bus}_{net}")
            if net in {"VDD", "GND"}:
                source_contact = f"{pdu_output}/{'2' if net == 'VDD' else '1'}"
            else:
                source_contact = f"{upstream_endpoint}/{net}"
            contact_rows.append({
                "connector_id": conn_id, "contact": pin, "axis_id": axis, "signal": net,
                "bus_net": physical_net, "service": service,
                "wire_core": f"CORE-{axis}-{net.replace('+','P').replace('-','N')}",
                "physical_pin_state": "VERIFIED AT ACTUATOR INTERFACE", "end_to_end_test": "NOT EXECUTED",
            })
            core_rows.append({
                "core_id": f"CORE-{axis}-{net.replace('+','P').replace('-','N')}", "axis_id": axis,
                "from_connector_contact": source_contact, "to_connector_contact": f"{conn_id}/{pin}",
                "net": physical_net, "service": service, "route": pseg if service in {"POWER RETURN", "ACTUATOR POWER"} else dseg,
                "conductor_cross_section": OPEN, "insulation_temperature_flex": OPEN,
                "shield_or_twist": OPEN,
                "cut_length_and_slack": f"PLANNING {power_one_way_mm:.3f} mm ONE-WAY; CUT LENGTH/SLACK OPEN" if service in {"POWER RETURN", "ACTUATOR POWER"} else f"PLANNING {data_link_mm:.3f} mm; CUT LENGTH/SLACK OPEN",
                "authority": AUTHORITY,
            })
        if next_axis is not None:
            out_id = f"J-OUT-{axis}"
            connector_rows.append({
                "connector_id": out_id, "location": axis, "function": "DATA-ONLY OUTGOING LINK TO " + next_axis,
                "candidate_housing": binding["actuator_side_housing"], "mating_part": "SECOND ACTUATOR PORT",
                "contact_order_code": binding["actuator_side_crimp_terminal"], "contact_count": binding["actuator_connector_contacts"],
                "keying_retention_strain_relief": OPEN, "source": binding["official_interface_source"],
                "source_date": binding["official_interface_accessed_date"], "selection_state": "PIN 1 AND PIN 2 INTENTIONALLY UNPOPULATED; DATA CONTACTS ONLY; VALIDATION OPEN",
            })
            output_pins = [("1", "EMPTY-GND"), ("2", "EMPTY-VDD")]
            output_pins += [("3", "DATA+"), ("4", "DATA-")] if protocol_is_rs else [("3", "DATA")]
            for pin, signal in output_pins:
                is_empty = signal.startswith("EMPTY")
                core_signal = signal.replace("+", "P").replace("-", "N")
                contact_rows.append({
                    "connector_id": out_id, "contact": pin, "axis_id": axis, "signal": signal,
                    "bus_net": "NO NET - CAVITY EMPTY" if is_empty else f"{bus}_{signal}",
                    "service": "INTENTIONALLY UNPOPULATED" if is_empty else "DATA",
                    "wire_core": "NONE - CAVITY EMPTY" if is_empty else f"CORE-{next_axis}-{core_signal}",
                    "physical_pin_state": "MUST REMAIN EMPTY; NO CONTACT" if is_empty else "DEVICE INTERFACE PIN VERIFIED; DATA-ONLY CONTACT CANDIDATE",
                    "end_to_end_test": "NOT EXECUTED",
                })
        retention_rows.append({
            "retention_id": f"RET-{axis}", "axis_id": axis, "power_loop": pseg, "data_loop": dseg,
            "fixed_side_clamp": OPEN, "moving_side_clamp": OPEN, "connector_load_isolation": "REQUIRED",
            "minimum_pull_test": OPEN, "abrasion_guard": OPEN, "inspection_access": OPEN, "validation": "NOT EXECUTED",
        })
        derating_rows.append({
            "circuit": f"PWR-{axis}", "bus_branch": bus, "endpoint_current_a": f"{amps:.2f}",
            "normal_rms_current_a": OPEN, "fault_current_a": OPEN, "length_mm": f"{power_one_way_mm:.3f}",
            "round_trip_planning_length_mm": f"{2 * power_one_way_mm:.3f}",
            "length_basis": "GEOMETRY-DERIVED PLANNING LENGTH ONLY; CUT LENGTH AND SLACK OPEN",
            "ambient_c": OPEN, "bundle_count": OPEN, "duty_cycle": OPEN, "inrush": OPEN,
            "connector_limit_a": "JST EH CATALOG 3 A BOUNDARY; ACTUATOR ENDPOINT CONFLICT OPEN",
            "conductor_selection": OPEN, "calculation_state": "PARTIAL - LENGTH PRESENT; RMS/FAULT/AMBIENT/BUNDLING/DUTY/INRUSH STILL REQUIRED",
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
    write_csv(OUT / "actuator-chain-contact-map.csv", chain_rows)
    write_csv(OUT / "individual-power-pair-register.csv", power_pair_rows)
    write_csv(OUT / "serial-data-link-register.csv", data_link_rows)
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
        is_pdu = eq["item_id"].startswith("EQ-PDU-")
        equipment_rows.append({
            "item_id": eq["item_id"], "module": eq["module"], "role": eq["role"], "candidate": eq["candidate"],
            "center_xyz_mm": f"({eq['center_x_mm']},{eq['center_y_mm']},{eq['center_z_mm']})",
            "power_route": pwr, "data_route": data, "connector_boundary": eq["connector_boundary"],
            "physical_connector": "NATIVE J1/J10x/J20x BOARD HEADERS PRESENT; FIELD MATING ASSEMBLIES OPEN" if is_pdu else OPEN,
            "contact_map": "BOUND TO CONNECTOR-INSTANCE-REGISTER AND CONNECTOR-CONTACT-MAP" if is_pdu else OPEN,
            "retention": OPEN,
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
        ("HSEL-03", "25 actuator drops", "controlled split-harness candidate: individual VDD/return pair into each input housing; serial data-only outgoing housing with GND/VDD cavities empty", "candidate contact drawings now present; crimp process, cavity inspection, no-backfeed continuity and fault-injection evidence still required"),
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
        "state": "CANDIDATE DEFINED / VALIDATION REQUIRED" if i == "HSEL-03" else OPEN, "authority": AUTHORITY,
    } for i, s, sel, e in unresolved])

    source_by_id = {row["source_id"]: row for row in harness_sources}
    current_by_axis = {row["axis_id"]: row for row in current_limits}
    interface_rows = []
    for row in actuator_pinouts:
        family = row["family"]
        used_axes = sorted(binding["axis_id"] for binding in bindings if binding["actuator_family"] == family)
        interface_rows.append({
            "actuator_family": family,
            "axis_count": len(used_axes),
            "axes": "; ".join(used_axes),
            "protocol": row["protocol"],
            "device_pin_mapping": row["actuator_side_pin_mapping"],
            "robotis_housing_name": row["cable_housing"],
            "robotis_pcb_header": row["actuator_pcb_header"],
            "robotis_crimp_terminal": row["crimp_terminal"],
            "robotis_published_wire_gauge": row["manufacturer_published_dynamixel_wire_gauge"],
            "official_source": row["official_source"],
            "source_revision_or_date": row["source_revision_or_date"],
            "accessed_date": row["accessed_date"],
            "verified_boundary": "DEVICE PINOUT / ROBOTIS-LISTED CONNECTOR FAMILY ONLY",
            "unverified_boundary": row["remaining_selection"],
            "authority": AUTHORITY,
        })
    write_csv(OUT / "actuator-interface-verification-register.csv", interface_rows)

    cable_rows = [
        ("ROBOT CABLE-X4P 180 MM", "903-0244-000", "180", "JST", "JST", "1 GND; 2 VDD; 3 DATA+; 4 DATA-", "https://www.robotis.us/robot-cable-x4p-180mm-10pcs/"),
        ("ROBOT CABLE-X4P 240 MM", "903-0245-000", "240", "JST", "JST", "1 GND; 2 VDD; 3 DATA+; 4 DATA-", "https://www.robotis.us/robot-cable-x4p-240mm-10pcs/"),
        ("ROBOT CABLE-X4P CONVERTIBLE 180 MM", "903-0246-000", "180", "MOLEX", "JST", "1 GND; 2 VDD; 3 DATA+; 4 DATA-", "https://www.robotis.us/robot-cable-x4p-180mm-convertible-10pcs/"),
        ("ROBOT CABLE-X3P 180 MM", "903-0249-000", "180", "JST", "JST", "1 GND; 2 VDD; 3 DATA", "https://www.robotis.us/robot-cable-x3p-180mm-10pcs/"),
        ("ROBOT CABLE-X3P CONVERTIBLE 180 MM", "903-0251-000", "180", "MOLEX", "JST", "1 GND; 2 VDD; 3 DATA", "https://www.robotis.us/robot-cable-x3p-180mm-convertible-10pcs/"),
    ]
    write_csv(OUT / "robotis-cable-family-register.csv", [{
        "cable_family": name, "official_order_code": code, "nominal_length_mm": length,
        "end_a": end_a, "end_b": end_b, "published_populated_contacts": contacts,
        "hr30_whole_body_role": "REJECT FOR INTER-ACTUATOR DATA-ONLY LINKS",
        "reason": "PUBLISHED ASSEMBLY POPULATES GND/VDD; IT WOULD PARALLEL SEPARATELY PROTECTED ACTUATOR POWER PATHS",
        "permitted_candidate_use": "ONE-ACTUATOR CURRENT-LIMITED COMMISSIONING ONLY AFTER RECEIVED-CABLE CONTINUITY CHECK",
        "official_source": source, "source_revision_or_date": "LIVE OFFICIAL PRODUCT PAGE; REVISION DATE NOT STATED",
        "accessed_date": "2026-08-16", "selection_state": "CATALOG FAMILY VERIFIED; FINAL HR-30 CABLE REJECTED",
        "authority": AUTHORITY,
    } for name, code, length, end_a, end_b, contacts, source in cable_rows])

    leg_cap = {row["bus_id"]: float(row["simultaneous_candidate_cap_a"]) for row in bus_current_budgets}
    discrepancy_rows = [
        {
            "finding_id": "DXL-IF-001", "interface": "JST EH CONDUCTOR RANGE",
            "manufacturer_a_evidence": "ROBOTIS LISTS 21 AWG FOR DYNAMIXEL X-SERIES CABLES",
            "manufacturer_b_evidence": "JST EH CATALOG RATES 3 A AT AWG 22 AND LISTS AWG 32 TO 22; SEH-001T-P0.6 LISTS AWG 30 TO 22 (0.05 TO 0.33 MM2)",
            "disposition": "CONFLICT OPEN - DO NOT RELEASE 21 AWG OR SUBSTITUTE A CONTACT",
            "closure_evidence": "WRITTEN JST/ROBOTIS APPLICATION APPROVAL OR EXACT RECEIVED ASSEMBLY IDENTIFICATION; CRIMP CROSS-SECTION/PULL/THERMAL/FLEX TEST",
            "source_a": source_by_id["JST-EH"]["official_url"], "source_b": source_by_id["XH540"]["official_url"], "authority": AUTHORITY,
        },
        {
            "finding_id": "DXL-IF-002", "interface": "JST EH HOUSING ORDER-CODE TEXT",
            "manufacturer_a_evidence": "ROBOTIS DOCUMENTATION LISTS EHR-03 / EHR-04",
            "manufacturer_b_evidence": "JST EH CATALOG TABLE LISTS EHR-3 / EHR-4",
            "disposition": "NOMENCLATURE CONFLICT OPEN - DO NOT INFER THE PROCUREMENT ORDER CODE",
            "closure_evidence": "WRITTEN SUPPLIER QUOTE/CONFIRMATION AND RECEIVED-HOUSING MARKING/DIMENSION INSPECTION",
            "source_a": source_by_id["JST-EH"]["official_url"], "source_b": source_by_id["XH540"]["official_url"], "authority": AUTHORITY,
        },
        {
            "finding_id": "DXL-IF-003", "interface": "ACTUATOR ENDPOINT CURRENT / JST EH CONTACT",
            "manufacturer_a_evidence": "XH540 12 V MOMENTARY STALL ENDPOINT 4.9 A",
            "manufacturer_b_evidence": "JST EH CATALOG CURRENT RATING 3 A AT AWG 22",
            "disposition": "CURRENT-LIMITED DEVELOPMENT CANDIDATE ONLY; NO STALL-CURRENT HARNESS CLAIM",
            "closure_evidence": "EXTERNAL BRANCH CURRENT LIMIT/FAULT CLEARING PLUS RECEIVED-CONTACT VOLTAGE-DROP AND TEMPERATURE TEST AT ACCEPTED DUTY",
            "source_a": source_by_id["XH540"]["official_url"], "source_b": source_by_id["JST-EH"]["official_url"], "authority": AUTHORITY,
        },
        {
            "finding_id": "DXL-IF-004", "interface": "U2D2 POWER HUB AGGREGATE POWER",
            "manufacturer_a_evidence": "U2D2 POWER HUB MAXIMUM CURRENT 10.0 A",
            "manufacturer_b_evidence": f"EACH LEG INTERNAL CURRENT-LIMIT CANDIDATE SUM IS {leg_cap['RS-LLEG']:.6f} A; EACH LEG STALL-ENDPOINT SUM IS 24.20 A",
            "disposition": "REJECT FOR WHOLE-BODY OR LEG POWER AGGREGATION",
            "closure_evidence": "NONE FOR THIS ROLE; USE THE 25-BRANCH PDU ARCHITECTURE AFTER ITS OWN VALIDATION",
            "source_a": source_by_id["U2D2-PHB"]["official_url"], "source_b": "current-constrained-actuation-p0.1/bus-current-budget.csv", "authority": AUTHORITY,
        },
        {
            "finding_id": "DXL-IF-005", "interface": "U2D2 WHOLE-BODY DATA CONTROL",
            "manufacturer_a_evidence": "ONE USB CONVERTER WITH TTL AND RS-485 PORTS; NO EIGHT-ISOLATED-SEGMENT CLAIM",
            "manufacturer_b_evidence": "HR-30 REQUIRES FIVE RS-485 AND THREE TTL SEGMENTS",
            "disposition": "REJECT FOR FINAL WHOLE-BODY CONTROLLER; RETAIN AS ONE-SEGMENT COMMISSIONING TOOL CANDIDATE",
            "closure_evidence": "RECEIVED USB REVISION INSPECTION; SINGLE-SEGMENT DATA/TERMINATION/REFERENCE TEST ONLY",
            "source_a": source_by_id["U2D2"]["official_url"], "source_b": "actuator-bus-axis-binding.csv", "authority": AUTHORITY,
        },
    ]
    write_csv(OUT / "manufacturer-interface-discrepancy-register.csv", discrepancy_rows)

    route_cad_solid_count = write_route_cad(route_rows, point_rows)
    stats = {
        "fixed_route_segments": len(trunks), "moving_joint_route_segments": 50,
        "total_route_segments": len(route_rows), "route_points": len(point_rows),
        "route_cad_solid_count": route_cad_solid_count,
        "axes": len(axis_rows), "buses": len(buses), "harness_assemblies": len(assembly_rows),
        "equipment_items": len(equipment_rows), "logical_terminals": len(logical_rows),
        "actuator_connector_instances": len(connector_rows), "actuator_connector_contacts": len(contact_rows),
        "cable_cores": len(core_rows), "serial_data_links": len(data_link_rows),
        "individual_power_pairs": len(power_pair_rows), "data_only_outgoing_connectors": sum(1 for r in chain_rows if r["successor_axis"] != "FAR END"),
        "actuator_interface_verification_records": len(interface_rows),
        "robotis_commercial_cable_families_reviewed": len(cable_rows),
        "manufacturer_interface_discrepancies_open": len(discrepancy_rows),
        "candidate_12v_stall_endpoint_sum_a": round(sum(float(r["candidate_12v_stall_endpoint_a"]) for r in power_rows), 2),
    }
    write_visuals(route_rows, point_rows, axis_rows, buses, stats, chain_rows)
    status = {
        "identifier": IDENTIFIER, "warning": WARNING, "scope": "complete HR-30 P0.1 physical harness architecture",
        **stats, "topology": "25 individual positive/return power pairs / 8 serial data-only trunks / GND and VDD cavities empty in every inter-actuator outgoing connector",
        "split_harness_candidate_defined": True,
        "data_star_topology_rejected": True,
        "serial_data_predecessor_successor_chain_complete": True,
        "inter_actuator_ground_or_vdd_pass_through_present": False,
        "route_geometry_candidate_present": True, "whole_body_route_step_present": True,
        "whole_body_route_glb_present": True, "route_cad_is_cable_size_release": False,
        "every_axis_has_power_and_data_loop": True,
        "every_equipment_item_bound": True, "every_logical_terminal_retained": True,
        "standard_dynamixel_cable_direct_use_approved": False, "assembled_cables_selected": False,
        "u2d2_final_whole_body_controller_approved": False,
        "u2d2_power_hub_whole_body_or_leg_power_approved": False,
        "robotis_jst_wire_gauge_conflict_closed": False,
        "robotis_jst_housing_order_code_conflict_closed": False,
        "conductor_sizing_released": False, "protection_released": False, "connector_set_released": False,
        "harness_validated": False, "procurement_authority": False, "fabrication_authority": False,
        "connection_authority": False, "powered_test_authority": False, "motion_authority": False,
        "energization_authority": False,
    }
    (OUT / "physical-harness-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    readme = f"""# HR-30 whole-body physical harness P0.1

**{WARNING}**

This is the first complete physical translation of the HR-30 logical wiring architecture. It binds all **{stats['axes']} joints**, **{stats['buses']} actuator buses**, **{stats['equipment_items']} installed equipment items**, and **{stats['logical_terminals']} current ECAD logical terminals** to a controlled harness architecture.

It contains {stats['fixed_route_segments']} body corridors plus 50 explicit moving-joint power/data loops ({stats['total_route_segments']} route segments and {stats['route_points']} route points). All {stats['route_cad_solid_count']} registered routes are also exported as named editable STEP solids and as one interactive GLB in a recognizable 762 mm body context. Those rods are route centerlines—not selected cable diameters, bundle clearances, or bend-radius releases. Each actuator has a known device-side contact map, a branch-power relationship, a data-link boundary, a moving-loop obligation, retention obligation, derating inputs, and an inspection path.

The architecture now defines one two-conductor power pair per actuator and a serial data chain for each bus. Every actuator input housing receives its own return, VDD, and data contacts. Every inter-actuator outgoing housing populates only the data contacts: GND and VDD cavities remain empty, so no power current is daisy-chained through a preceding actuator connector. This controlled split-harness is the P0.1 construction candidate; crimp tooling, conductor selection, cavity inspection, no-backfeed tests, and fault injection remain required before release.

The {stats['candidate_12v_stall_endpoint_sum_a']:.2f} A figure is only the sum of manufacturer 12 V momentary stall-current endpoints for the current 25-axis allocation. It is not expected demand, a conductor rating, a fuse value, or permission to power the robot.

Manufacturer-interface review is now configuration-bound. ROBOTIS publishes the actuator pinouts, but its 21 AWG cable statement conflicts with JST's EH catalog limit of AWG 22 for `SEH-001T-P0.6`, and ROBOTIS's `EHR-03` / `EHR-04` names differ from JST's `EHR-3` / `EHR-4` catalog table. These are not silently normalized: both remain open procurement blockers in `manufacturer-interface-discrepancy-register.csv`. U2D2 is retained only as a single-segment commissioning candidate, and the 10 A U2D2 Power Hub is rejected for whole-body or leg power aggregation.

Open the [interactive physical harness guide](index.html). Start with the whole-body route model, `route-cad-register.csv`, `axis-harness-binding.csv`, `route-segment-register.csv`, `connector-contact-map.csv`, and `unresolved-harness-selections.csv`.

No cable cut length, conductor size, protection value, complete connector set, retention hardware, shielding decision, or powered validation is released by this package.
"""
    (OUT / "README.md").write_text(readme, encoding="utf-8")
    return stats


def write_visuals(routes: list[dict], points: list[dict], axes: list[dict], buses: list[dict], stats: dict, chains: list[dict]) -> None:
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

    diagram_dir = OUT / "bus-diagrams"
    if diagram_dir.exists():
        shutil.rmtree(diagram_dir)
    diagram_dir.mkdir()
    diagram_cards = []
    for bus in buses:
        bus_id = bus["bus_id"]
        rows = sorted((row for row in chains if row["bus_id"] == bus_id), key=lambda row: int(row["ordinal"]))
        width = 280 + 220 * len(rows)
        nodes = []
        arrows = []
        controller = '<rect x="24" y="92" width="180" height="128" rx="16" class="controller"/><text x="40" y="122" class="title">CONTROLLER</text><text x="40" y="150">Data-only JST GH</text><text x="40" y="176">No actuator VDD</text><text x="40" y="202">Reference star tie open</text>'
        previous_x = 204
        for index, row in enumerate(rows):
            x = 250 + index * 220
            nodes.append(
                f'<rect x="{x}" y="70" width="184" height="172" rx="16" class="node"/>'
                f'<text x="{x+16}" y="101" class="title">{html.escape(row["axis_id"])}</text>'
                f'<text x="{x+16}" y="129">Input: power pair + data</text>'
                f'<text x="{x+16}" y="157">Pin 1 return / Pin 2 VDD</text>'
                f'<text x="{x+16}" y="185">Outgoing: data only</text>'
                f'<text x="{x+16}" y="213">Outgoing pins 1/2 EMPTY</text>'
            )
            arrows.append(f'<line x1="{previous_x}" y1="150" x2="{x}" y2="150" class="data" marker-end="url(#arrow)"/>')
            arrows.append(f'<line x1="{x+92}" y1="278" x2="{x+92}" y2="242" class="power" marker-end="url(#arrowGold)"/><text x="{x+16}" y="302">Individual VDD + return pair</text>')
            previous_x = x + 184
        far_x = 250 + len(rows) * 220
        arrows.append(f'<line x1="{previous_x}" y1="150" x2="{far_x}" y2="150" class="data"/><text x="{far_x-2}" y="142" text-anchor="end">FAR END / termination open</text>')
        drawing = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} 330" role="img" aria-labelledby="title desc"><title id="title">{html.escape(bus_id)} serial data and individual power harness</title><desc id="desc">Serial data chain through each actuator with separate VDD and return pair at each actuator. Outgoing ground and VDD cavities remain empty.</desc><defs><marker id="arrow" markerWidth="9" markerHeight="9" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#179de3"/></marker><marker id="arrowGold" markerWidth="9" markerHeight="9" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#d99a00"/></marker></defs><style>text{{font:16px Arial,sans-serif;fill:#0d2d57}}.title{{font-weight:700;font-size:17px}}.controller{{fill:#d8f1ff;stroke:#123f73;stroke-width:3}}.node{{fill:white;stroke:#123f73;stroke-width:3}}.data{{stroke:#179de3;stroke-width:5}}.power{{stroke:#d99a00;stroke-width:5}}</style><rect width="100%" height="100%" fill="#f8fcff"/><text x="24" y="36" class="title">{html.escape(bus_id)} / {html.escape(bus["protocol"])} / {len(rows)} axes</text>{controller}{''.join(arrows)}{''.join(nodes)}</svg>'''
        slug = bus_id.lower()
        (diagram_dir / f"{slug}.svg").write_text(drawing, encoding="utf-8")
        diagram_cards.append(f'<article class="diagram"><h3>{html.escape(bus_id)}</h3><div class="diagram-scroll"><img src="bus-diagrams/{slug}.svg" alt="{html.escape(bus_id)} serial data chain and individual power-pair drawing"></div></article>')

    bus_cards = "".join(f'<button class="bus" data-bus="{html.escape(b["bus_id"])}"><strong>{html.escape(b["bus_id"])}</strong><span>{html.escape(b["protocol"])} · {html.escape(b["axis_count"])} axes</span><span>{html.escape(b["candidate_12v_stall_endpoint_sum_a"])} A endpoint sum</span></button>' for b in buses)
    axis_cards = "".join(f'<tr data-bus="{html.escape(a["bus_id"])}"><td>{html.escape(a["axis_id"])}</td><td>{html.escape(a["bus_id"])}</td><td>{html.escape(a["actuator_family"])}</td><td>{html.escape(a["axis_xyz_mm"])}</td><td>{html.escape(a["power_loop"])}<br>{html.escape(a["data_loop"])}</td></tr>' for a in axes)
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 physical harness P0.1</title><style>:root{{--navy:#0d2d57;--blue:#179de3;--sky:#d8f1ff;--gold:#f4b400;--paper:#f8fcff}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--navy);font:16px/1.5 system-ui,sans-serif}}header{{background:linear-gradient(135deg,var(--navy),#185d9d);color:white;padding:32px max(24px,calc((100% - 1180px)/2))}}h1{{font-size:clamp(32px,5vw,60px);line-height:1.05;margin:.2em 0}}.warning{{background:var(--gold);color:#1b2840;padding:14px 18px;font-weight:800;border-radius:12px}}main{{max-width:1180px;margin:auto;padding:28px 20px 70px}}h2{{font-size:clamp(25px,3vw,38px);margin-top:46px}}.stats,.buses{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:14px}}.stat,.bus,.panel{{background:white;border:2px solid #9bd5f5;border-radius:16px;padding:18px;box-shadow:0 6px 18px #0d2d5712}}.stat strong{{display:block;font-size:28px}}.bus{{font:inherit;color:inherit;text-align:left;cursor:pointer}}.bus strong,.bus span{{display:block}}.bus.active{{border-color:var(--gold);box-shadow:0 0 0 3px #f4b40055}}.map{{width:100%;max-height:760px}}.tablewrap{{overflow:auto;border:2px solid #9bd5f5;border-radius:16px;background:white}}table{{border-collapse:collapse;width:100%;min-width:900px}}th,td{{padding:13px 14px;border-bottom:1px solid #cfeafa;text-align:left;vertical-align:top}}th{{position:sticky;top:0;background:var(--navy);color:white;font-size:14px}}td{{font-size:14px}}a{{color:#075f9f;font-weight:700}}.open{{border-left:8px solid var(--gold)}}@media(max-width:600px){{header{{padding:24px 18px}}main{{padding:20px 14px}}}}</style></head><body><header><div class="warning">{html.escape(WARNING)}</div><p>HR-30 · Whole-body P0.1</p><h1>Physical harness guide</h1><p>Every body corridor, actuator feed, data bus, joint loop and current ECAD terminal is accounted for—without pretending unresolved cable and protection choices are finished.</p></header><main><section class="stats"><div class="stat"><strong>{stats['axes']}</strong>separate actuator feeds</div><div class="stat"><strong>{stats['total_route_segments']}</strong>route segments</div><div class="stat"><strong>{stats['logical_terminals']}</strong>logical terminals</div><div class="stat"><strong>{stats['candidate_12v_stall_endpoint_sum_a']}</strong>A endpoint sum, not demand</div></section><h2>Whole-body route map</h2><div class="panel"><img class="map" src="whole-body-physical-harness.svg" alt="Front map of the HR-30 physical harness routes and joint loops"></div><h2>Eight data buses</h2><p>Select a data bus to filter the joint table; select it again to show all.</p><div class="buses">{bus_cards}</div><h2>All 25 protected-feed candidates</h2><div class="tablewrap"><table><thead><tr><th>Axis</th><th>Data bus</th><th>Actuator</th><th>Joint datum (mm)</th><th>Moving loops</th></tr></thead><tbody>{axis_cards}</tbody></table></div><h2>Critical power boundary</h2><div class="panel open"><p>Each actuator now has its own protection/telemetry boundary and VDD net. Standard ROBOTIS X3P/X4P cables include VDD, so a custom data-only/power-injection breakout or controlled depinning method is required to keep the 25 feeds isolated.</p><p>The {stats['candidate_12v_stall_endpoint_sum_a']:.2f} A figure is the arithmetic sum of momentary 12 V stall-current endpoints—not a normal-load forecast, fuse rating, cable rating, or permission to energize.</p></div><h2>Manufacturer interface reality check</h2><div class="panel open"><p><strong>Pinouts are verified; the cable assembly is not.</strong> ROBOTIS lists 21 AWG DYNAMIXEL wire, while JST's EH catalog limits the listed SEH-001T-P0.6 contact to AWG 22. ROBOTIS also writes EHR-03/EHR-04 while JST's own catalog table writes EHR-3/EHR-4. Neither discrepancy is silently normalized.</p><p>U2D2 remains a one-segment commissioning candidate only. It is not the final eight-segment controller. The 10 A U2D2 Power Hub is rejected for whole-body and leg power aggregation.</p><p><a href="actuator-interface-verification-register.csv">verified device interfaces</a> · <a href="robotis-cable-family-register.csv">commercial cable review</a> · <a href="manufacturer-interface-discrepancy-register.csv">open manufacturer discrepancies</a></p></div><h2>Build registers</h2><div class="panel"><p><a href="route-segment-register.csv">route segments</a> · <a href="route-point-register.csv">route points</a> · <a href="axis-harness-binding.csv">axis bindings</a> · <a href="connector-contact-map.csv">actuator contacts</a> · <a href="cable-core-register.csv">cable cores</a> · <a href="equipment-interface-register.csv">equipment interfaces</a> · <a href="logical-terminal-binding.csv">logical terminals</a> · <a href="current-derating-register.csv">derating inputs</a> · <a href="inspection-test-register.csv">inspection/tests</a> · <a href="unresolved-harness-selections.csv">open selections</a></p></div></main><script>const buttons=[...document.querySelectorAll('.bus')],rows=[...document.querySelectorAll('tbody tr')];buttons.forEach(b=>b.addEventListener('click',()=>{{const on=!b.classList.contains('active');buttons.forEach(x=>x.classList.remove('active'));b.classList.toggle('active',on);rows.forEach(r=>r.hidden=on&&r.dataset.bus!==b.dataset.bus)}}));</script></body></html>'''
    page = page.replace(
        "<title>HR-30 physical harness P0.1</title><style>",
        '<title>HR-30 physical harness P0.1</title><script type="module" src="../../vendor/model-viewer.min.js"></script><style>',
        1,
    )
    page = page.replace(
        ".map{width:100%;max-height:760px}",
        "model-viewer{display:block;width:100%;height:clamp(500px,70vh,760px);background:radial-gradient(circle,#fff,#d8f1ff)}.map{width:100%;max-height:760px}",
        1,
    )
    route_viewer = '''<h2>Orbit all 62 routes in the complete body</h2><div class="panel"><model-viewer src="HR30_whole_body_harness_centerlines_candidate.glb" camera-controls camera-orbit="32deg 76deg 105%" field-of-view="27deg" shadow-intensity="0.8" exposure="1.05" alt="Interactive recognizable 762 millimetre HR-30 whole body with all 62 registered harness centerlines"></model-viewer><p>Gold rods are actuator-power centerlines; sky-blue rods are data/low-voltage centerlines. The translucent body is lightweight positional context. Rod diameter is illustrative and does not release cable OD, bundle clearance, or bend radius.</p><p><a href="HR30_whole_body_harness_centerlines_candidate.step">Download editable route STEP</a> · <a href="route-cad-register.csv">Inspect the 62-solid CAD register</a></p></div>'''
    page = page.replace("<h2>Whole-body route map</h2>", route_viewer + "<h2>Whole-body route map</h2>", 1)
    page = page.replace(
        '<a href="route-point-register.csv">route points</a> ·',
        '<a href="route-point-register.csv">route points</a> · <a href="route-cad-register.csv">route CAD</a> ·',
        1,
    )
    (OUT / "index.html").write_text(page, encoding="utf-8")
    page_path = OUT / "index.html"
    page = page_path.read_text(encoding="utf-8")
    page = page.replace(
        ".open{border-left:8px solid var(--gold)}",
        ".open{border-left:8px solid var(--gold)}.diagram{background:white;border:2px solid #9bd5f5;border-radius:16px;padding:18px;margin:18px 0}.diagram-scroll{overflow:auto}.diagram img{display:block;max-width:none;height:330px}",
    )
    page = page.replace(
        '</div><h2>All 25 protected-feed candidates</h2>',
        '</div><h2>Eight serial data-chain assembly drawings</h2><p>Each actuator receives an individual VDD/return pair. Inter-actuator outgoing connectors carry data only; GND and VDD cavities stay empty.</p>' + "".join(diagram_cards) + '<h2>All 25 protected-feed candidates</h2>',
        1,
    )
    page = page.replace(
        "Each actuator now has its own protection/telemetry boundary and VDD net. Standard ROBOTIS X3P/X4P cables include VDD, so a custom data-only/power-injection breakout or controlled depinning method is required to keep the 25 feeds isolated.",
        "Each actuator now has its own positive/return power pair. The P0.1 split-harness candidate combines that pair with incoming data at the actuator input housing, while the outgoing housing populates data contacts only. GND and VDD cavities remain empty so power is not daisy-chained through preceding actuator connectors.",
    )
    page = page.replace(
        '<a href="connector-contact-map.csv">actuator contacts</a> · <a href="cable-core-register.csv">cable cores</a>',
        '<a href="actuator-chain-contact-map.csv">actuator chain map</a> · <a href="individual-power-pair-register.csv">individual power pairs</a> · <a href="serial-data-link-register.csv">serial data links</a> · <a href="connector-contact-map.csv">all connector cavities</a> · <a href="cable-core-register.csv">cable cores</a>',
    )
    page_path.write_text(page, encoding="utf-8")


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

The [interactive physical harness guide](harness/physical-p0.1/index.html) translates the logical ECAD into {stats['total_route_segments']} route segments: 12 reserved body corridors and two moving-loop candidates at every one of the 25 joint axes. It retains all {stats['logical_terminals']} current logical terminals and binds every installed equipment item without inventing unresolved conductor sizes or protection values.

All {stats['route_cad_solid_count']} route centerlines now exist as named editable STEP solids and one interactive GLB in a recognizable 762 mm body context. The display rods are centerline references only; they do not release cable OD, bundle clearance, bend radius, cut length, or retention.

The P0.1 split-harness candidate uses 25 individual positive/return power pairs and eight serial data chains. Incoming actuator housings combine the individual pair with data; outgoing inter-actuator housings populate data contacts only and leave GND/VDD cavities empty. The eight bus assembly drawings and 25 contact maps are construction candidates, not a released cable set. Protection, conductor sizing, crimp process qualification, retention, flex-life, EMC, and physical validation remain open.

Four actuator-family interfaces are now source-verified, five commercial ROBOTIS cable families are dispositioned, and five manufacturer-interface discrepancies remain explicitly open. In particular, the ROBOTIS 21 AWG statement conflicts with JST's AWG 22 contact limit, the documented housing order-code text differs, U2D2 is not the eight-segment controller, and the 10 A Power Hub is rejected for whole-body or leg power.
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
        "physical_harness_route_cad_solids": stats["route_cad_solid_count"],
        "physical_harness_route_step_present": True,
        "physical_harness_route_glb_present": True,
        "physical_harness_axes_bound": stats["axes"],
        "physical_harness_logical_terminals_retained": stats["logical_terminals"],
        "whole_body_harness_equipment_binding_count": stats["equipment_items"],
        "physical_harness_connector_instance_count": stats["actuator_connector_instances"],
        "physical_harness_connector_contact_count": stats["actuator_connector_contacts"],
        "physical_harness_split_harness_candidate_defined": True,
        "physical_harness_serial_data_link_count": stats["serial_data_links"],
        "physical_harness_individual_power_pair_count": stats["individual_power_pairs"],
        "physical_harness_actuator_interface_verification_count": stats["actuator_interface_verification_records"],
        "physical_harness_commercial_cable_family_review_count": stats["robotis_commercial_cable_families_reviewed"],
        "physical_harness_manufacturer_discrepancy_count": stats["manufacturer_interface_discrepancies_open"],
        "physical_harness_u2d2_final_controller_approved": False,
        "physical_harness_u2d2_power_hub_aggregate_power_approved": False,
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
