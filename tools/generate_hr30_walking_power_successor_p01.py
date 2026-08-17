#!/usr/bin/env python3
"""Generate the HR-30 bidirectional walking-power successor candidate.

This package replaces the single reverse-blocking branch concept for walking
development with two oppositely oriented TPS259482L eFuses per axis branch.
One device protects each current direction.  It deliberately does not release
the contactor-open energy sink, thresholds, PCB, or any powered-work authority.
"""

from __future__ import annotations

import csv
import hashlib
import html
import importlib.util
import json
import shutil
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WHOLE = ROOT / "hr30" / "whole-body-p0.1"
OUT = WHOLE / "electrical" / "walking-power-successor-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / "electrical" / OUT.name
PROJECT = "hr30-walking-power-successor-p0.1"
IDENTIFIER = "HR30-WALKING-POWER-SUCCESSOR-P0.1"
DATE = "2026-08-17"
WARNING = (
    "PRELIMINARY - WALKING-POWER ARCHITECTURE CANDIDATE ONLY - NOT APPROVED "
    "FOR PROCUREMENT, FABRICATION, CONNECTION, POWERED TESTING, MOTION OR ENERGIZATION"
)
WHOLE_WARNING = (
    "PRELIMINARY - CONFIGURATION AND PACKAGING CAD ONLY - NOT APPROVED FOR PROCUREMENT, "
    "FABRICATION, ASSEMBLY, POWERED TESTING, MOTION, OR ENERGIZATION"
)
AUTHORITY = "NO PROCUREMENT, FABRICATION, CONNECTION, POWERED-TEST, MOTION OR ENERGIZATION AUTHORITY"
KICAD = Path(r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe")

TI_DS = "https://www.ti.com/lit/ds/symlink/tps25948.pdf"
TI_PRODUCT = "https://www.ti.com/product/TPS25948/part-details/TPS259482LYWPR"
TI_BIDIR = "https://www.ti.com/lit/an/slva948/slva948.pdf"
TI_E2E = "https://e2e.ti.com/support/power-management-group/power-management/f/power-management-forum/1547179/tps25948-forward-and-reverse-power-mux-application"
JST_VH = "https://www.jst-mfg.com/product/pdf/eng/eVH.pdf"
JST_GH = "https://www.jst-mfg.com/product/pdf/eng/eGH.pdf"


@dataclass
class Part:
    ref: str
    value: str
    pins: dict[str, str]
    footprint: str
    evidence: str
    source: str


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise RuntimeError(f"refusing empty CSV: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def controlled(row: dict[str, object]) -> dict[str, object]:
    return {**row, "execution_state": "NOT EXECUTED", "authority": AUTHORITY, "warning": WARNING}


def axis_allocations() -> list[dict[str, object]]:
    source = read_csv(WHOLE / "actuator-bus-axis-binding.csv")
    caps = {r["axis_id"]: r for r in read_csv(WHOLE / "harness/current-policy-binding-p0.1/axis-power-policy-binding.csv")}
    groups = [
        ("WPS-LLEG", [r for r in source if r["bus_id"] == "RS-LLEG"]),
        ("WPS-RLEG", [r for r in source if r["bus_id"] == "RS-RLEG"]),
        ("WPS-ARMS", [r for r in source if r["bus_id"] in {"RS-LARM", "RS-RARM"}]),
        ("WPS-DISTAL", [r for r in source if r["bus_id"] in {"TTL-LDIST", "TTL-RDIST", "TTL-HEAD"}]),
        ("WPS-CORE", [r for r in source if r["bus_id"] == "RS-WAIST"]),
    ]
    rows: list[dict[str, object]] = []
    for board, members in groups:
        for channel in range(1, 7):
            axis = members[channel - 1] if channel <= len(members) else None
            if not axis:
                rows.append(controlled({
                    "board_instance": board, "channel": channel, "axis_id": "DNP SPARE", "bus_id": "DNP",
                    "actuator_family": "DNP", "candidate_internal_cap_a": "DNP",
                    "forward_device": "DNP", "reverse_device": "DNP", "population_state": "DNP",
                }))
                continue
            cap_row = caps[axis["axis_id"]]
            cap = float(cap_row["candidate_internal_limit_a"])
            rows.append(controlled({
                "board_instance": board, "channel": channel, "axis_id": axis["axis_id"],
                "bus_id": axis["bus_id"], "actuator_family": axis["actuator_family"],
                "candidate_internal_cap_a": f"{cap:.6f}",
                "forward_device": "TPS259482LYWPR IN=BUS OUT=MID",
                "reverse_device": "TPS259482LYWPR IN=AXIS OUT=MID",
                "population_state": "POPULATE AS PAIRED BIDIRECTIONAL CANDIDATE",
            }))
    return rows


def source_bindings() -> list[dict[str, object]]:
    items = [
        ("WPS-B01", "25-axis ownership", WHOLE / "actuator-bus-axis-binding.csv"),
        ("WPS-B02", "axis current-policy candidates", WHOLE / "harness/current-policy-binding-p0.1/axis-power-policy-binding.csv"),
        ("WPS-B03", "eight-bus current boundary", WHOLE / "harness/current-policy-binding-p0.1/bus-power-boundary.csv"),
        ("WPS-B04", "five-feed power boundary", WHOLE / "electrical/tether-power-core-p0.1/five-pdu-feed-register.csv"),
        ("WPS-B05", "commissioning PDU allocation", WHOLE / "electrical/actuator-branch-pdu-p0.1/board-instance-channel-allocation.csv"),
        ("WPS-B06", "protection/conductor holds", WHOLE / "electrical/protection-conductor-architecture-p0.1/open-holds.csv"),
    ]
    return [controlled({
        "binding_id": item_id, "role": role, "path": path.relative_to(ROOT).as_posix(),
        "sha256": sha(path), "bytes": path.stat().st_size,
    }) for item_id, role, path in items]


def primary_sources() -> list[dict[str, object]]:
    data = [
        ("WPS-S01", "Texas Instruments", "TPS25948xx datasheet", "SLVSGT9D Rev D; April 2026", TI_DS,
         "3.5-23 V; 12.2 mOhm typical; 20 mOhm maximum across temperature; 1-9 A ILIM; RCBCTRL permits bidirectional steady-state flow; reverse-direction OCP is not provided by one device"),
        ("WPS-S02", "Texas Instruments", "TPS259482LYWPR active orderable page", "active official product page; accessed 2026-08-17", TI_PRODUCT,
         "exact latch-off, adjustable fast-trip, RCBCTRL orderable candidate; 12-ball YWP PowerWCSP"),
        ("WPS-S03", "Texas Instruments", "Bidirectional control through back-to-back eFuses", "SLVA948; December 2017", TI_BIDIR,
         "two oppositely oriented eFuses provide symmetric forward/reverse current limiting and off-state blocking; application uses TPS2595 and requires HR-30 validation with TPS25948"),
        ("WPS-S04", "Texas Instruments", "TPS25948 reverse-mode OCP response", "TI E2E manufacturer response; accessed 2026-08-17", TI_E2E,
         "manufacturer engineer states OCP is only IN-to-OUT; this prevents using one TPS25948 as a protected regenerative branch"),
        ("WPS-S05", "JST", "VH connector catalogue", "revision not stated; accessed 2026-08-17", JST_VH,
         "candidate PDU power interface family only; exact contact, conductor, derating and retention remain open"),
        ("WPS-S06", "JST", "GH connector catalogue", "revision not stated; accessed 2026-08-17", JST_GH,
         "candidate branch control/monitor connector family only"),
    ]
    return [controlled({"source_id": i, "manufacturer": m, "document": d, "revision_or_date": rev, "url": url, "verified_use": use}) for i, m, d, rev, url, use in data]


def architecture_options() -> list[dict[str, object]]:
    data = [
        ("WPS-O01", "existing TPS259474L single-device branch", "RETAIN FOR RESTRAINED COMMISSIONING ONLY", "forward protection but true reverse blocking prevents shared-bus regeneration"),
        ("WPS-O02", "single TPS259482L with RCBCTRL low", "REJECT AS SOLE WALKING BRANCH", "permits reverse flow but manufacturer states overcurrent protection works only IN-to-OUT"),
        ("WPS-O03", "two oppositely oriented TPS259482L devices", "SELECTED P0.1 WALKING-BRANCH CANDIDATE", "one device protects motoring current and the other protects regenerative current; both block while off or faulted"),
        ("WPS-O04", "bidirectional fuse plus monitor and power switch", "ADAPTATION FALLBACK", "physically credible but exact fuse curve, switch fault behavior and monitoring architecture remain unselected"),
        ("WPS-O05", "one local clamp per actuator", "REJECT AS PRIMARY", "twenty-five sinks add heat and do not close contactor-open shared-bus energy without measured branch data"),
        ("WPS-O06", "five-feed active brake/dump", "REQUIRED COMPANION ARCHITECTURE", "absorbs downstream energy after upstream contactors open; exact chopper, resistor, thresholds and energy ratings remain selection required"),
    ]
    return [controlled({"option_id": i, "architecture": a, "disposition": d, "basis": b}) for i, a, d, b in data]


def energy_states() -> list[dict[str, object]]:
    data = [
        ("WPS-E0", "OFF / UNPOWERED", "both EN low; RCB active by device behavior", "both directions blocked", "stored-energy verification required"),
        ("WPS-E1", "CONTROLLED START", "RCB active until steady state; paired enable sequence candidate", "bus to axis ramp only", "startup sequence and dVdt interaction test required"),
        ("WPS-E2", "MOTORING", "both enabled; both RCBCTRL low", "BUS -> forward eFuse -> MID -> reverse-oriented eFuse -> AXIS", "forward device provides IN-to-OUT OCP"),
        ("WPS-E3", "REGENERATION", "both enabled; both RCBCTRL low", "AXIS -> reverse eFuse -> MID -> forward-oriented eFuse -> BUS", "reverse-oriented device provides IN-to-OUT OCP"),
        ("WPS-E4", "FORWARD OVERCURRENT", "forward device limits then can thermally latch off", "branch isolated after fault", "threshold, timer and SOA test required"),
        ("WPS-E5", "REVERSE OVERCURRENT", "reverse-oriented device limits then can thermally latch off", "branch isolated after fault", "regenerative fault test required"),
        ("WPS-E6", "CONTACTORS OPEN / COAST", "upstream source removed; paired branch remains conductive for bounded discharge window", "AXIS -> downstream PDU bus -> five-feed brake/dump", "brake/dump and branch-control timing are not selected"),
        ("WPS-E7", "BRANCH DISABLED", "either device disabled/faulted; RCB always active in disabled/fault state", "both directions blocked by paired path", "verify no downstream backfeed and discharge"),
    ]
    return [controlled({"state_id": i, "state": state, "command_or_condition": command, "energy_path": path, "protection_or_hold": hold}) for i, state, command, path, hold in data]


def loss_rows(allocations: list[dict[str, object]]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    axis_rows: list[dict[str, object]] = []
    by_board: defaultdict[str, dict[str, float]] = defaultdict(lambda: {"typ": 0.0, "max": 0.0, "cap": 0.0, "count": 0.0})
    for row in allocations:
        if row["axis_id"] == "DNP SPARE":
            continue
        cap = float(row["candidate_internal_cap_a"])
        typ = cap * cap * 0.0244
        max_loss = cap * cap * 0.0400
        accuracy = "DATASHEET MAXIMUM ACCURACY NOT SPECIFIED BELOW 3 A"
        device_min = "PASS" if cap >= 1.0 else "FAIL - 0.700 A CAP BELOW 1 A DEVICE MINIMUM"
        axis_rows.append(controlled({
            "axis_id": row["axis_id"], "board_instance": row["board_instance"], "candidate_internal_cap_a": f"{cap:.6f}",
            "pair_ron_typ_ohm": "0.0244", "pair_ron_hot_max_ohm": "0.0400",
            "pair_loss_at_cap_typ_w": f"{typ:.6f}", "pair_loss_at_cap_hot_max_w": f"{max_loss:.6f}",
            "device_1_to_9a_range_screen": device_min, "current_limit_accuracy_boundary": accuracy,
            "normal_rms_loss": "SELECTION REQUIRED - CAP LOSS IS NOT NORMAL DUTY",
        }))
        b = by_board[str(row["board_instance"])]
        b["typ"] += typ; b["max"] += max_loss; b["cap"] += cap; b["count"] += 1
    board_rows = [controlled({
        "board_instance": board, "populated_axis_count": int(values["count"]),
        "arithmetic_cap_sum_a": f"{values['cap']:.6f}",
        "simultaneous_pair_loss_typ_w": f"{values['typ']:.6f}",
        "simultaneous_pair_loss_hot_max_w": f"{values['max']:.6f}",
        "thermal_credit": "NONE - REQUIRES PCB, COPPER, AIRFLOW, ENCLOSURE AND MEASURED DUTY",
    }) for board, values in sorted(by_board.items())]
    return axis_rows, board_rows


def brake_boundaries() -> list[dict[str, object]]:
    data = [
        ("WPS-D01", "FB1 / WPS-LLEG", "one downstream active chopper + resistor bank", "SELECTION REQUIRED", "measured left-leg regenerative energy/current and contactor-open trace"),
        ("WPS-D02", "FB2 / WPS-RLEG", "one downstream active chopper + resistor bank", "SELECTION REQUIRED", "measured right-leg regenerative energy/current and contactor-open trace"),
        ("WPS-D03", "FB3 / WPS-ARMS", "one downstream active chopper + resistor bank", "SELECTION REQUIRED", "measured bilateral-arm regenerative energy/current"),
        ("WPS-D04", "FB4 / WPS-DISTAL", "one downstream active chopper + resistor bank", "SELECTION REQUIRED", "measured head/wrist/gripper regenerative energy/current"),
        ("WPS-D05", "FB5 / WPS-CORE", "one downstream active chopper + resistor bank", "SELECTION REQUIRED", "measured waist regenerative energy/current"),
    ]
    return [controlled({"dump_id": i, "feed": feed, "candidate_role": role, "exact_components_and_threshold": state, "closure_input": evidence}) for i, feed, role, state, evidence in data]


def open_holds() -> list[dict[str, object]]:
    data = [
        ("WPS-H01", "TPS259482L paired use is extrapolated from TI's TPS2595 two-eFuse application note", "obtain TI application review and validate the exact TPS259482L pair across all states"),
        ("WPS-H02", "current-limit setpoints, resistors and ITIMER values are not selected", "measured inrush/RMS/peak/fault/regeneration plus received-device threshold and SOA tests"),
        ("WPS-H03", "six XC330 caps are 0.700 A, below the TPS25948 1 A minimum limit", "select a branch threshold of at least 1 A and prove conductor/connector/fault protection; internal actuator cap remains separate"),
        ("WPS-H04", "datasheet maximum current-limit accuracy is stated only above 3 A while every HR-30 candidate cap is below 3 A", "received-lot calibration over temperature; do not treat calculated ILIM as released"),
        ("WPS-H05", "five contactor-open brake/dump circuits have no selected devices, thresholds or energy ratings", "measure return energy/current/voltage and size the identical-as-built choppers and resistor banks"),
        ("WPS-H06", "source absorption and reverse-energy behavior are not characterized", "manufacturer-approved application basis and bench characterization of RSP path, contactors and downstream bus"),
        ("WPS-H07", "paired startup, disable and fault timing are unvalidated", "instrument EN, RCBCTRL, IN/MID/OUT, SPLYGD and ILM in both directions under fault"),
        ("WPS-H08", "native schematic is not a routed PCB", "complete exact YWP footprint, placement, copper/thermal design, DFM, ERC/DRC and physical board tests"),
        ("WPS-H09", "connector, conductor, fuse and five-feed coordination remain open", "close protection/conductor architecture inputs with exact parts and hot/fault evidence"),
        ("WPS-H10", "dynamic walking demand and regenerative events are unmeasured", "restrained instrumented trajectories, loss/temperature/overvoltage traces and repeatable fault tests"),
        ("WPS-H11", "functional safety allocation and stopping performance are not validated", "qualified review of identical hardware/software plus measured stopping and fault response"),
        ("WPS-H12", "no procurement, fabrication, connection, powered-test, motion or energization authority exists", "separate signed release after every applicable hold closes"),
    ]
    return [controlled({"hold_id": i, "unresolved_item": item, "closure_evidence": evidence, "state": "OPEN"}) for i, item, evidence in data]


def parts() -> list[Part]:
    result = [
        Part("J1", "12 V CONTROLLED INPUT", {"1": "PDU_0V", "2": "PDU_12V_IN"},
             "TerminalBlock_MetzConnect:TerminalBlock_MetzConnect_Type703_RT10N02HGLU_1x02_P9.52mm_Horizontal",
             "existing five-feed input boundary; exact terminal and production footprint remain under predecessor holds", JST_VH),
        Part("JBRK", "EXTERNAL FEED BRAKE/DUMP INTERFACE", {"1": "PDU_0V", "2": "PDU_12V_IN", "3": "DUMP_DIAG"},
             "Connector_JST:JST_VH_B3P-VH_1x03_P3.96mm_Vertical",
             "physical three-contact architecture interface only; current rating and exact chopper remain selection required", JST_VH),
    ]
    # Deliberately unassigned in the native schematic.  A dimension-near KiCad
    # DSBGA footprint is not an acceptable substitute for TI YWP0012A.
    fp = ""
    for channel in range(1, 7):
        c = str(channel)
        bus, axis, mid, gnd = "PDU_12V_IN", f"BRANCH_{c}_12V", f"CH{c}_MID", "PDU_0V"
        en, rcb = f"CH{c}_EN", f"CH{c}_RCBCTRL"
        f_ilm, r_ilm = f"CH{c}_ILM_F", f"CH{c}_ILM_R"
        f_pg, r_pg = f"CH{c}_PG_F", f"CH{c}_PG_R"
        dvf, dvr = f"CH{c}_DVDT_F", f"CH{c}_DVDT_R"
        itf, itr = f"CH{c}_ITIMER_F", f"CH{c}_ITIMER_R"
        evidence = "TPS259482LYWPR candidate; native footprint deliberately blank until exact TI YWP0012A land pattern is generated and DFM-accepted"
        source = TI_DS
        result.extend([
            Part(f"U{c}F", "TPS259482L FORWARD OCP", {"1": en, "2": f"CH{c}_OV_F", "3": f_pg, "4": rcb, "5": bus, "6": mid, "7": dvf, "8": gnd, "9": f_ilm, "10": itf, "11": mid, "12": bus}, fp, evidence, source),
            Part(f"U{c}R", "TPS259482L REVERSE OCP", {"1": en, "2": f"CH{c}_OV_R", "3": r_pg, "4": rcb, "5": axis, "6": mid, "7": dvr, "8": gnd, "9": r_ilm, "10": itr, "11": mid, "12": axis}, fp, evidence, source),
            Part(f"J{c}O", f"CHANNEL {c} AXIS OUTPUT", {"1": gnd, "2": axis}, "Connector_JST:JST_VH_B2P-VH_1x02_P3.96mm_Vertical", "candidate local power pair", JST_VH),
            Part(f"J{c}C", f"CHANNEL {c} CONTROL/MONITOR", {"1": gnd, "2": en, "3": f_pg, "4": r_pg, "5": f_ilm, "6": r_ilm, "7": rcb}, "Connector_JST:JST_GH_BM07B-GHS-TBT_1x07-1MP_P1.25mm_Vertical", "ordinary diagnostics/control only; zero safety credit", JST_GH),
            Part(f"R{c}E", "100k EN pulldown", {"1": en, "2": gnd}, "Resistor_SMD:R_0603_1608Metric", "candidate fail-low bias; exact control circuit remains open", source),
            Part(f"R{c}B", "10k RCBCTRL pulldown", {"1": rcb, "2": gnd}, "Resistor_SMD:R_0603_1608Metric", "pull low enables bidirectional steady-state flow; disabled/fault state remains blocking by device behavior", source),
            Part(f"R{c}F", "RILM FORWARD - SELECTION REQUIRED", {"1": f_ilm, "2": gnd}, "Resistor_SMD:R_0603_1608Metric", "no value released; ILIM range and accuracy boundaries apply", source),
            Part(f"R{c}R", "RILM REVERSE - SELECTION REQUIRED", {"1": r_ilm, "2": gnd}, "Resistor_SMD:R_0603_1608Metric", "independent reverse-current limit remains selection required", source),
            Part(f"C{c}F", "DVDT FORWARD - SELECTION REQUIRED", {"1": dvf, "2": gnd}, "Capacitor_SMD:C_0603_1608Metric", "startup slew interaction requires test", source),
            Part(f"C{c}R", "DVDT REVERSE - SELECTION REQUIRED", {"1": dvr, "2": gnd}, "Capacitor_SMD:C_0603_1608Metric", "startup slew interaction requires test", source),
            Part(f"C{c}I", "INPUT BYPASS - SELECTION REQUIRED", {"1": bus, "2": gnd}, "Capacitor_SMD:C_0805_2012Metric", "value/voltage/bias/placement open", source),
            Part(f"C{c}O", "AXIS BYPASS - SELECTION REQUIRED", {"1": axis, "2": gnd}, "Capacitor_SMD:C_0805_2012Metric", "value/voltage/bias/regeneration pulse open", source),
        ])
    return result


def load_model():
    path = ROOT / "tools/generate_hr_v0_electrical_v3.py"
    spec = importlib.util.spec_from_file_location("hr30_wps_model", path)
    if not spec or not spec.loader:
        raise RuntimeError("cannot load schematic writer")
    model = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = model
    spec.loader.exec_module(model)
    model.OUT = OUT; model.PROJECT = PROJECT; model.REV = "P0.1"; model.DATE = DATE; model.WARNING = WARNING
    model.PROJECT_TITLE = "PROJECT BUTTON HR-30 BIDIRECTIONAL WALKING-POWER SUCCESSOR"
    model.PROJECT_SUBTITLE = "Paired eFuse branch candidate; brake/dump, thresholds, PCB and all powered work remain open."
    return model


def write_schematic(items: list[Part]) -> None:
    model = load_model()
    components = []
    for item in items:
        pins = [model.pn(item.ref, number, number, net, "left" if index % 2 == 0 else "right") for index, (number, net) in enumerate(item.pins.items())]
        components.append(model.Component(item.ref, item.value, pins, "PRELIMINARY CANDIDATE / SELECTIONS OPEN", item.evidence, item.source, item.evidence, position=(50, 50), width=88, footprint=item.footprint))
    by_ref = {component.ref: component for component in components}
    sheets = []
    overview = model.Sheet(1, "01_system_boundaries.kicad_sch", "Five-feed and six-channel board boundaries", "One board pattern is instantiated five times; 25 channels populated and five DNP.")
    overview.components = [by_ref["J1"], by_ref["JBRK"]] + [by_ref[f"J{i}O"] for i in range(1, 7)] + [by_ref[f"J{i}C"] for i in range(1, 7)]
    for index, component in enumerate(overview.components):
        component.position = (52 + (index % 3) * 145, 46 + (index // 3) * 57); component.width = 84
    overview.notes = ["JBRK is a real downstream interface obligation, not a released resistor/chopper selection.", "Each axis output is an individual power pair; data harnesses remain data-only.", WARNING]
    sheets.append(overview)
    for channel in range(1, 7):
        c = str(channel)
        refs = [f"U{c}F", f"U{c}R", f"R{c}E", f"R{c}B", f"R{c}F", f"R{c}R", f"C{c}F", f"C{c}R", f"C{c}I", f"C{c}O"]
        sheet = model.Sheet(channel + 1, f"{channel + 1:02d}_paired_channel_{channel}.kicad_sch", f"Paired bidirectional branch {channel}", "One TPS259482L faces each current direction; exact setpoints and PCB remain open.")
        sheet.components = [by_ref[ref] for ref in refs]
        for index, component in enumerate(sheet.components):
            component.position = (54 + (index % 3) * 145, 45 + (index // 3) * 67); component.width = 88
        sheet.notes = ["Motoring: UxF provides IN-to-OUT overcurrent protection.", "Regeneration: UxR provides IN-to-OUT overcurrent protection.", "A single TPS25948 is insufficient because reverse-direction OCP is not provided.", "Five downstream brake/dump circuits are still required for contactor-open energy.", WARNING]
        sheets.append(sheet)
    net_counts = Counter(pin.net for component in components for pin in component.pins)
    wires = model.build_wire_numbers(sheets, net_counts)
    root_uuid = model.uid("root-hr30-walking-power-successor-p0.1")
    project = {"board": {}, "boards": [], "cvpcb": {}, "erc": {}, "libraries": {}, "meta": {"filename": f"{PROJECT}.kicad_pro", "version": 1}, "net_settings": {"classes": [{"name": "Default", "priority": 2147483647, "clearance": 0.2, "track_width": 0.25, "via_diameter": 0.8, "via_drill": 0.4}], "meta": {"version": 3}}, "pcbnew": {}, "schematic": {}, "text_variables": {"PROJECT_STATUS": WARNING}}
    (OUT / f"{PROJECT}.kicad_pro").write_text(json.dumps(project, indent=2) + "\n", encoding="utf-8")
    symbols = [model.lib_symbol(component).replace(f'(symbol "PBV3:{component.ref}"', f'(symbol "{component.ref}"', 1) for component in components]
    (OUT / f"{PROJECT}.kicad_sym").write_text('(kicad_symbol_lib\n  (version 20251024) (generator "kicad_symbol_editor") (generator_version "10.0")\n  ' + "\n".join(symbols) + "\n)\n", encoding="utf-8")
    (OUT / "sym-lib-table").write_text(f'(sym_lib_table\n  (version 7)\n  (lib (name "PBV3")(type "KiCad")(uri "${{KIPRJMOD}}/{PROJECT}.kicad_sym")(options "")(descr "HR-30 walking-power successor symbols"))\n)\n', encoding="utf-8")
    (OUT / "fp-lib-table").write_text('(fp_lib_table\n  (version 7)\n)\n', encoding="utf-8")
    (OUT / f"{PROJECT}.kicad_sch").write_text(model.root_schematic(root_uuid, sheets), encoding="utf-8")
    for sheet in sheets:
        (OUT / sheet.filename).write_text(model.child_schematic(root_uuid, sheet, net_counts, wires), encoding="utf-8")


def validate_kicad() -> dict[str, object]:
    validation = OUT / "validation"; output = OUT / "output"
    validation.mkdir(); output.mkdir()
    erc = subprocess.run([str(KICAD), "sch", "erc", "--exit-code-violations", "--output", str(validation / f"{PROJECT}-erc.rpt"), str(OUT / f"{PROJECT}.kicad_sch")], cwd=OUT, text=True, capture_output=True)
    if erc.returncode != 0:
        raise RuntimeError(f"KiCad ERC failed ({erc.returncode})\n{erc.stdout}\n{erc.stderr}")
    export = subprocess.run([str(KICAD), "sch", "export", "svg", "--output", str(output), str(OUT / f"{PROJECT}.kicad_sch")], cwd=OUT, text=True, capture_output=True)
    if export.returncode != 0:
        raise RuntimeError(f"KiCad SVG export failed\n{export.stdout}\n{export.stderr}")
    for svg in output.glob("*.svg"):
        svg.write_text("\n".join(line.rstrip() for line in svg.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")
    (OUT / f"{PROJECT}.kicad_prl").unlink(missing_ok=True)
    return {"kicad_version": "10.0.5", "native_sheet_count_including_root": 8, "erc_errors": 0, "erc_warnings": 0, "exported_svg_count": len(list(output.glob("*.svg")))}


def branch_svg() -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1500" height="820" viewBox="0 0 1500 820" role="img" aria-labelledby="title desc"><title id="title">Paired HR-30 bidirectional actuator branch</title><desc id="desc">Two oppositely oriented TPS259482L eFuses connect the PDU bus to one actuator. The forward device protects motoring current; the reverse-oriented device protects regenerative current. A five-feed brake dump remains required.</desc><defs><marker id="a" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#0b5b9b"/></marker><marker id="r" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#a03921"/></marker></defs><style>text{{font:600 19px system-ui;fill:#102a43}}.h{{font-size:34px;font-weight:900}}.s{{font-size:16px}}.box{{fill:#fff;stroke:#0b5b9b;stroke-width:4}}.gold{{fill:#fff0ad;stroke:#8a6200;stroke-width:4}}.hold{{fill:#ffe4df;stroke:#a03921;stroke-width:4}}.f{{stroke:#0b5b9b;stroke-width:8;fill:none;marker-end:url(#a)}}.r{{stroke:#a03921;stroke-width:8;fill:none;marker-end:url(#r)}}.wire{{stroke:#183c5d;stroke-width:7}}</style><rect width="1500" height="820" fill="#eef8ff"/><text class="h" x="55" y="60">HR-30 walking branch: protected in both directions</text><text x="55" y="102">A single bidirectional TPS25948 path is not enough: its OCP acts only from IN to OUT.</text><rect class="gold" x="55" y="180" width="230" height="120" rx="18"/><text x="92" y="232">PDU 12 V bus</text><text class="s" x="92" y="266">five feed instances</text><path class="wire" d="M285 240H390"/><rect class="box" x="390" y="160" width="300" height="160" rx="20"/><text class="h" x="432" y="218">UxF</text><text x="432" y="256">TPS259482L</text><text class="s" x="432" y="288">IN=BUS · OUT=MID</text><path class="wire" d="M690 240H810"/><text x="732" y="222">MID</text><rect class="box" x="810" y="160" width="300" height="160" rx="20"/><text class="h" x="852" y="218">UxR</text><text x="852" y="256">TPS259482L</text><text class="s" x="852" y="288">IN=AXIS · OUT=MID</text><path class="wire" d="M1110 240H1215"/><rect class="gold" x="1215" y="180" width="230" height="120" rx="18"/><text x="1252" y="232">DYNAMIXEL</text><text class="s" x="1252" y="266">one local power pair</text><path class="f" d="M230 390H1260"/><text x="575" y="370">MOTORING: BUS → AXIS · UxF provides forward OCP</text><path class="r" d="M1260 500H230"/><text x="555" y="545">REGENERATION: AXIS → BUS · UxR provides forward OCP</text><rect class="hold" x="55" y="620" width="1390" height="130" rx="20"/><text class="h" x="92" y="671">Still required before walking</text><text x="92" y="715">Five downstream brake/dump circuits, measured energy, exact thresholds, routed PCB, thermal proof and contactor-open timing.</text><text class="s" x="55" y="795">{WARNING}</text></svg>'''


def page(status: dict[str, object], allocations: list[dict[str, object]], board_losses: list[dict[str, object]], holds: list[dict[str, object]]) -> str:
    alloc_html = "".join(f'<tr><td>{r["board_instance"]}</td><td>{r["channel"]}</td><td>{r["axis_id"]}</td><td>{r["actuator_family"]}</td><td>{r["candidate_internal_cap_a"]}</td></tr>' for r in allocations)
    loss_html = "".join(f'<tr><td>{r["board_instance"]}</td><td>{r["populated_axis_count"]}</td><td>{r["arithmetic_cap_sum_a"]}</td><td>{r["simultaneous_pair_loss_typ_w"]}</td><td>{r["simultaneous_pair_loss_hot_max_w"]}</td></tr>' for r in board_losses)
    hold_html = "".join(f'<li><b>{r["hold_id"]}</b> {html.escape(str(r["unresolved_item"]))}</li>' for r in holds)
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 walking-power successor</title><style>:root{{--deep:#071f3b;--blue:#0b5b9b;--sky:#d6f1ff;--gold:#f4bd21;--paper:#f6fbff;--ink:#122c45;--red:#9d3520;--line:#82c5e6}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.55 system-ui,Segoe UI,sans-serif}}header,main,footer{{padding:clamp(24px,5vw,64px) max(18px,calc((100vw - 1280px)/2))}}header,footer{{background:linear-gradient(135deg,var(--deep),var(--blue));color:white}}h1{{font-size:clamp(38px,6vw,72px);line-height:1.03;max-width:18ch}}h2{{font-size:clamp(28px,4vw,44px)}}h3{{font-size:22px}}.warning{{background:var(--gold);color:#17243a;border:3px solid #7b5600;padding:16px;font-weight:900}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:18px}}article,.panel,li{{background:white;border:2px solid var(--line);border-radius:16px;padding:19px}}.metric{{font-size:clamp(34px,5vw,55px);font-weight:900;color:var(--blue)}}.hold{{border-color:#bf6a56;background:#fff2ef}}.hold .metric,.bad{{color:var(--red)}}.scroll{{overflow:auto;border:2px solid var(--line);border-radius:16px;background:white}}object{{display:block;width:100%;min-width:900px}}table{{border-collapse:collapse;width:100%;min-width:900px}}th,td{{padding:14px;text-align:left;border-bottom:1px solid var(--line);font-size:16px}}th{{background:var(--sky)}}a{{color:#075b9b;font-weight:800}}li{{margin:12px 0}}code{{font-size:16px}}@media(max-width:560px){{body{{font-size:16px}}}}</style></head><body><header><div class="warning">{html.escape(WARNING)}</div><p>HR-30 whole-body P0.1</p><h1>The walking branch now has a real return path.</h1><p>Every populated actuator branch uses a candidate pair of oppositely oriented eFuses: one protects motoring current and one protects regenerative current.</p></header><main><section class="grid"><article><div class="metric">25</div><p>whole-body axes bound to paired branch slots</p></article><article><div class="metric">50</div><p>candidate populated TPS259482L devices</p></article><article><div class="metric">ERC 0/0</div><p>eight native KiCad sheets including root</p></article><article class="hold"><div class="metric">5 open</div><p>feed-level brake/dump circuits still require measured sizing</p></article></section><section><h2>Why two devices are required</h2><div class="scroll"><object data="bidirectional-branch-schematic.svg" type="image/svg+xml" aria-label="Paired bidirectional eFuse architecture"></object></div><p>TI documents that TPS25948 can pass bidirectional steady-state current when RCBCTRL is low, but its overcurrent protection acts only from IN to OUT. The selected P0.1 candidate therefore places one device in each direction. This is an engineering inference from TI's bidirectional two-eFuse application architecture and still requires TI application review and physical validation.</p></section><section><h2>Native KiCad is included</h2><div class="panel"><p><a href="{PROJECT}.kicad_pro">Open the native KiCad project</a> · <a href="output/{PROJECT}.svg">root schematic export</a> · <a href="validation/{PROJECT}-erc.rpt">complete ERC report</a>.</p><p>The project contains one boundary sheet and six fully populated paired-channel sheets. It is a connected schematic candidate, not a routed or fabrication-released PCB.</p></div></section><section><h2>Five board instances and 25 axes</h2><div class="scroll"><table><thead><tr><th>Board</th><th>Channel</th><th>Axis</th><th>Actuator</th><th>Internal cap A</th></tr></thead><tbody>{alloc_html}</tbody></table></div></section><section><h2>Pair conduction-loss screen</h2><p>These values use the axis cap as if simultaneous and therefore bound silicon conduction loss only. They are not measured walking duty or a thermal release.</p><div class="scroll"><table><thead><tr><th>Board</th><th>Axes</th><th>Cap sum A</th><th>Pair loss typ W</th><th>Pair loss hot-max W</th></tr></thead><tbody>{loss_html}</tbody></table></div><p><a href="axis-pair-loss-screen.csv">Open all 25 axis calculations</a> · <a href="board-pair-loss-screen.csv">five-board summary</a>.</p></section><section class="panel"><h2>The honest remaining blocker</h2><p>When K1/K2 open, the source is gone but the robot can still return mechanical energy. The paired branches allow that energy onto each downstream feed, but each of the five feeds still needs a measured, independently powered brake/dump circuit. No resistor, chopper, voltage threshold or energy rating is released.</p><p><a href="feed-brake-dump-boundary.csv">Open the five-feed brake/dump obligations</a> · <a href="energy-flow-state-register.csv">eight power states</a> · <a href="architecture-option-register.csv">architecture decisions</a>.</p><h2>Open holds</h2><ul>{hold_html}</ul></section></main><footer>{html.escape(WARNING)}</footer></body></html>'''


def integrate_root(status: dict[str, object]) -> None:
    status_path = WHOLE / "package-status.json"
    root_status = json.loads(status_path.read_text(encoding="utf-8"))
    root_status.update({
        "walking_power_successor_package_present": True,
        "walking_power_successor_native_sheet_count": status["native_schematic_sheet_count"],
        "walking_power_successor_axis_count": status["allocated_axis_count"],
        "walking_power_successor_paired_device_count": status["populated_efuse_count"],
        "walking_power_bidirectional_branch_architecture_defined": True,
        "walking_power_bidirectional_overcurrent_architecture_defined": True,
        "walking_power_reverse_energy_path_to_downstream_feed_defined": True,
        "walking_power_feed_brake_dump_selected": False,
        "walking_power_pcb_routed": False,
        "walking_power_thermal_validated": False,
        "walking_power_architecture_complete": False,
        "walking_power_connection_authority": False,
        "walking_power_motion_authority": False,
        "walking_power_energization_authority": False,
    })
    status_path.write_text(json.dumps(root_status, indent=2) + "\n", encoding="utf-8")
    readme = WHOLE / "README.md"; text = readme.read_text(encoding="utf-8")
    start, end = "<!-- HR30-WALKING-POWER-P01-README-START -->", "<!-- HR30-WALKING-POWER-P01-README-END -->"
    if start in text and end in text:
        text = text.split(start, 1)[0] + text.split(end, 1)[1]
    block = f'''{start}\n## Bidirectional walking-power successor\n\nThe [interactive walking-power guide](electrical/walking-power-successor-p0.1/index.html) replaces the single reverse-blocking branch for walking development with a native eight-sheet KiCad candidate containing two oppositely oriented TPS259482L devices per branch. One device protects motoring current and the other protects regenerative current. All 25 axes are allocated across five six-channel board instances; five positions remain DNP. The architecture returns energy to the downstream feed, but five contactor-open brake/dump circuits, exact current thresholds, PCB layout, thermal proof and every powered-work authority remain open.\n{end}\n'''
    marker = "<!-- HR30-PROTECTION-CONDUCTOR-P01-README-START -->"
    text = text.replace(marker, block + marker) if marker in text else text.rstrip() + "\n\n" + block
    readme.write_text(text, encoding="utf-8", newline="\n")
    index = WHOLE / "index.html"; text = index.read_text(encoding="utf-8")
    start, end = "<!-- HR30-WALKING-POWER-P01-START -->", "<!-- HR30-WALKING-POWER-P01-END -->"
    if start in text and end in text:
        text = text.split(start, 1)[0] + text.split(end, 1)[1]
    section = f'''{start}<section id="walking-power-successor"><h2>Walking power now has a protected return path</h2><div class="grid"><article class="card pass"><div class="metric">25</div><p>axis-bound paired bidirectional branches.</p></article><article class="card pass"><div class="metric">50</div><p>candidate populated TPS259482L devices: one overcurrent direction each.</p></article><article class="card pass"><h3>ERC 0 / 0</h3><p>Eight native KiCad sheets including the root.</p></article><article class="card hold"><div class="metric">5 open</div><p>contactor-open brake/dump circuits still require measured sizing.</p></article></div><p><a href="electrical/walking-power-successor-p0.1/index.html">Open the interactive walking-power successor</a>. The return path is defined; PCB, thermal, dump-energy and powered-motion authority remain open.</p></section>{end}'''
    marker = "<!-- HR30-PROTECTION-CONDUCTOR-P01-START -->"
    text = text.replace(marker, section + marker) if marker in text else text.replace("</main>", section + "</main>", 1)
    index.write_text(text, encoding="utf-8", newline="\n")


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    allocations = axis_allocations()
    axis_losses, board_losses = loss_rows(allocations)
    holds = open_holds()
    items = parts()
    write_schematic(items)
    validation = validate_kicad()
    write_csv(OUT / "source-binding.csv", source_bindings())
    write_csv(OUT / "primary-source-register.csv", primary_sources())
    write_csv(OUT / "architecture-option-register.csv", architecture_options())
    write_csv(OUT / "energy-flow-state-register.csv", energy_states())
    write_csv(OUT / "axis-branch-allocation.csv", allocations)
    write_csv(OUT / "component-pin-register.csv", [controlled({
        "reference": item.ref, "pin": pin, "net": net, "footprint": item.footprint,
        "source": item.source, "evidence": item.evidence,
    }) for item in items for pin, net in item.pins.items()])
    write_csv(OUT / "axis-pair-loss-screen.csv", axis_losses)
    write_csv(OUT / "board-pair-loss-screen.csv", board_losses)
    write_csv(OUT / "feed-brake-dump-boundary.csv", brake_boundaries())
    write_csv(OUT / "open-holds.csv", holds)
    status = {
        "identifier": IDENTIFIER, "date": DATE, "warning": WARNING,
        "native_schematic_sheet_count": 8, "kicad_erc_errors": 0, "kicad_erc_warnings": 0,
        "board_pattern_count": 1, "board_instance_count": 5, "channels_per_board": 6,
        "allocated_axis_count": 25, "dnp_spare_count": 5, "candidate_device": "TPS259482LYWPR",
        "populated_efuse_count": 50, "dnp_efuse_count": 10,
        "branch_topology_selected_as_p01_candidate": True,
        "single_device_bidirectional_branch_rejected": True,
        "bidirectional_power_flow_defined": True,
        "bidirectional_overcurrent_architecture_defined": True,
        "off_state_bidirectional_blocking_defined": True,
        "reverse_energy_path_to_downstream_feed_defined": True,
        "feed_brake_dump_obligation_count": 5,
        "feed_brake_dump_selected": False, "exact_current_thresholds_selected": False,
        "tps25948_pair_manufacturer_application_accepted": False,
        "exact_ywp_footprint_released": False, "pcb_layout_present": False,
        "thermal_validated": False, "walking_power_architecture_complete": False,
        "functional_safety_credit": False, "procurement_authority": False, "fabrication_authority": False,
        "connection_authority": False, "powered_test_authority": False, "motion_authority": False,
        "energization_authority": False, "validation": validation,
    }
    (OUT / "walking-power-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    (OUT / "bidirectional-branch-schematic.svg").write_text(branch_svg(), encoding="utf-8", newline="\n")
    (OUT / "index.html").write_text(page(status, allocations, board_losses, holds), encoding="utf-8", newline="\n")
    (OUT / "README.md").write_text(f"# HR-30 walking-power successor P0.1\n\n**{WARNING}**\n\nThis package provides the native KiCad and web artifacts for a paired TPS259482L bidirectional actuator-branch candidate. One eFuse protects each current direction across every populated axis. Five downstream contactor-open brake/dump circuits, exact settings, a routed PCB, thermal evidence and all powered-work authority remain open.\n", encoding="utf-8", newline="\n")
    manifest_rows = []
    for path in sorted(p for p in OUT.rglob("*") if p.is_file() and p.name != "file-manifest.csv"):
        manifest_rows.append({"path": path.relative_to(OUT).as_posix(), "sha256": sha(path), "bytes": path.stat().st_size, "warning": WARNING})
    write_csv(OUT / "file-manifest.csv", manifest_rows)
    if RELEASE.exists():
        shutil.rmtree(RELEASE)
    RELEASE.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(OUT, RELEASE)
    integrate_root(status)
    sys.path.insert(0, str(ROOT / "tools"))
    import generate_hr30_system_package_p01 as system_package
    system_package.refresh_manifest_and_release()
    print(f"generated {OUT.relative_to(ROOT)}: 25 axes, 50 populated eFuses, ERC 0/0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
