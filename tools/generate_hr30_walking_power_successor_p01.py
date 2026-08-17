#!/usr/bin/env python3
"""Generate the HR-30 bidirectional walking-power successor candidate.

This package replaces the single reverse-blocking branch concept for walking
development with two oppositely oriented TPS259482L eFuses per axis branch.
One device protects each current direction.  It produces an exact-land-pattern
routed PCB candidate but deliberately does not release the contactor-open
energy sink, thresholds, production stackup, DFM, or powered-work authority.
"""

from __future__ import annotations

import csv
import hashlib
import html
import heapq
import importlib.util
import json
import shutil
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

import pcbnew

import generate_hr30_actuator_interface_carriers_p01 as carrier


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
FP_ROOT = Path(r"C:\Program Files\KiCad\10.0\share\kicad\footprints")
BOARD_W = 150.0
BOARD_H = 68.0
YWP_LIBRARY = "ProjectButton_WPS"
YWP_NAME = "TI_YWP0012A_PowerWCSP_2.441x1.728mm"
YWP_FOOTPRINT = f"{YWP_LIBRARY}:{YWP_NAME}"

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
    x: float = 0.0
    y: float = 0.0
    rotation: float = 0.0


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


def write_ywp_footprint_library() -> Path:
    """Write the exact TI YWP0012A example land pattern from 4228640/A.

    The eight control lands are 0.20 mm square at x=+/-1.06 mm and
    y=+/-0.675/+/-0.225 mm.  The four power lands are 0.50 x 0.25 mm at
    x=+/-0.476 mm and y=+/-0.45 mm.  The footprint is an engineering
    candidate tied to TI's April-2026 Rev-D data sheet; board-fabricator DFM
    and assembly-process acceptance remain explicit open holds.
    """
    library = OUT / f"{YWP_LIBRARY}.pretty"
    library.mkdir(parents=True, exist_ok=True)
    path = library / f"{YWP_NAME}.kicad_mod"
    small = {
        "1": (-1.060, 0.675), "2": (-1.060, 0.225),
        "3": (-1.060, -0.225), "4": (-1.060, -0.675),
        "7": (1.060, -0.675), "8": (1.060, -0.225),
        "9": (1.060, 0.225), "10": (1.060, 0.675),
    }
    power = {
        "5": (-0.476, -0.450), "6": (0.476, -0.450),
        "11": (0.476, 0.450), "12": (-0.476, 0.450),
    }
    pads = []
    for number, (x, y) in small.items():
        pads.append(
            f'  (pad "{number}" smd roundrect (at {x:.3f} {y:.3f}) '
            '(size 0.20 0.20) (layers "F.Cu" "F.Paste" "F.Mask") '
            '(roundrect_rratio 0.25))'
        )
    for number, (x, y) in power.items():
        pads.append(
            f'  (pad "{number}" smd roundrect (at {x:.3f} {y:.3f}) '
            '(size 0.50 0.25) (layers "F.Cu" "F.Paste" "F.Mask") '
            '(roundrect_rratio 0.20))'
        )
    text = f'''(footprint "{YWP_NAME}"
  (version 20260206)
  (generator "pcbnew")
  (generator_version "10.0")
  (layer "F.Cu")
  (descr "TI YWP0012A PowerWCSP exact example land pattern; TI drawing 4228640/A 04/2022 in TPS25948 Rev D April 2026")
  (tags "TI YWP0012A PowerWCSP TPS25948")
  (property "Reference" "REF**" (at 0 -2.15 0) (layer "F.SilkS")
    (effects (font (size 0.80 0.80) (thickness 0.12))))
  (property "Value" "{YWP_NAME}" (at 0 2.15 0) (layer "F.Fab")
    (effects (font (size 0.80 0.80) (thickness 0.12))))
  (solder_mask_margin 0.05)
  (attr smd)
  (fp_rect (start -1.2205 -0.864) (end 1.2205 0.864)
    (stroke (width 0.08) (type solid)) (fill none) (layer "F.Fab"))
  (fp_line (start -1.36 -1.02) (end 1.36 -1.02)
    (stroke (width 0.10) (type solid)) (layer "F.SilkS"))
  (fp_line (start 1.36 -1.02) (end 1.36 1.02)
    (stroke (width 0.10) (type solid)) (layer "F.SilkS"))
  (fp_line (start 1.36 1.02) (end -1.36 1.02)
    (stroke (width 0.10) (type solid)) (layer "F.SilkS"))
  (fp_line (start -1.36 1.02) (end -1.36 -0.55)
    (stroke (width 0.10) (type solid)) (layer "F.SilkS"))
  (fp_poly (pts (xy -1.36 -1.02) (xy -1.82 -1.02) (xy -1.36 -1.48))
    (stroke (width 0.10) (type solid)) (fill solid) (layer "F.SilkS"))
  (fp_rect (start -1.55 -1.20) (end 1.55 1.20)
    (stroke (width 0.05) (type default)) (fill none) (layer "F.CrtYd"))
{chr(10).join(pads)}
)\n'''
    path.write_text(text, encoding="utf-8", newline="\n")
    return path


def load_fp(identifier: str):
    library, name = identifier.split(":", 1)
    root = OUT / f"{library}.pretty" if library == YWP_LIBRARY else FP_ROOT / f"{library}.pretty"
    footprint = pcbnew.FootprintLoad(str(root), name)
    if footprint is None:
        raise RuntimeError(f"cannot load footprint {identifier}")
    return footprint


def add_via(board: pcbnew.BOARD, net: pcbnew.NETINFO_ITEM, point: tuple[float, float]) -> None:
    via = pcbnew.PCB_VIA(board)
    via.SetPosition(pcbnew.VECTOR2I_MM(*point))
    via.SetWidth(pcbnew.FromMM(0.45))
    via.SetDrill(pcbnew.FromMM(0.20))
    via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    via.SetNet(net)
    via.SetFrontTentingMode(True)
    via.SetBackTentingMode(True)
    board.Add(via)


def axis_allocations() -> list[dict[str, object]]:
    source = read_csv(WHOLE / "actuator-bus-axis-binding.csv")
    caps = {r["axis_id"]: r for r in read_csv(WHOLE / "harness/current-policy-binding-p0.1/axis-power-policy-binding.csv")}
    feed_map = {
        "RS-LLEG": ("WPS-RS-LLEG", "ACT_MAIN_SAFE_12V", "ACT_0V_CONTROLLED", "12 V nominal candidate"),
        "RS-RLEG": ("WPS-RS-RLEG", "ACT_MAIN_SAFE_12V", "ACT_0V_CONTROLLED", "12 V nominal candidate"),
        "RS-LARM": ("WPS-RS-LARM", "ACT_MAIN_SAFE_12V", "ACT_0V_CONTROLLED", "12 V nominal candidate"),
        "RS-RARM": ("WPS-RS-RARM", "ACT_MAIN_SAFE_12V", "ACT_0V_CONTROLLED", "12 V nominal candidate"),
        "RS-WAIST": ("WPS-RS-WAIST", "ACT_MAIN_SAFE_12V", "ACT_0V_CONTROLLED", "12 V nominal candidate"),
        "TTL-LDIST": ("WPS-TTL-LDIST", "TTL_LDIST_SAFE_9V", "ACT_0V_CONTROLLED", "9 V regulated candidate"),
        "TTL-RDIST": ("WPS-TTL-RDIST", "TTL_RDIST_SAFE_9V", "ACT_0V_CONTROLLED", "9 V regulated candidate"),
        "TTL-HEAD": ("WPS-TTL-HEAD", "TTL_HEAD_SAFE_9V", "ACT_0V_CONTROLLED", "9 V regulated candidate"),
    }
    rows: list[dict[str, object]] = []
    for bus_id in ("RS-LLEG", "RS-RLEG", "RS-LARM", "RS-RARM", "RS-WAIST", "TTL-LDIST", "TTL-RDIST", "TTL-HEAD"):
        board, positive_net, return_net, nominal_voltage = feed_map[bus_id]
        members = [r for r in source if r["bus_id"] == bus_id]
        for channel in range(1, 7):
            axis = members[channel - 1] if channel <= len(members) else None
            if not axis:
                rows.append(controlled({
                    "board_instance": board, "channel": channel, "axis_id": "DNP SPARE", "bus_id": bus_id,
                    "feed_positive_net": positive_net, "feed_return_net": return_net,
                    "nominal_feed_voltage": nominal_voltage,
                    "actuator_family": "DNP", "candidate_internal_cap_a": "DNP",
                    "forward_device": "DNP", "reverse_device": "DNP", "population_state": "DNP",
                }))
                continue
            cap_row = caps[axis["axis_id"]]
            cap = float(cap_row["candidate_internal_limit_a"])
            rows.append(controlled({
                "board_instance": board, "channel": channel, "axis_id": axis["axis_id"],
                "bus_id": axis["bus_id"], "actuator_family": axis["actuator_family"],
                "feed_positive_net": positive_net, "feed_return_net": return_net,
                "nominal_feed_voltage": nominal_voltage,
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
        ("WPS-B04", "eight-bus physical topology", WHOLE / "actuator-bus-topology.csv"),
        ("WPS-B05", "whole-body physical feed-net schedule", WHOLE / "electrical/kicad/hr30-whole-body-electrical-p0.1/connector-schedule.csv"),
        ("WPS-B06", "eight protected source-feed boundary", WHOLE / "electrical/tether-power-core-p0.1/eight-bus-feed-register.csv"),
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
        ("WPS-O06", "five shared-input board instances", "REJECTED AFTER WHOLE-BODY RECONCILIATION", "would short RS-LARM to RS-RARM and would short the three independently regulated 9 V TTL outputs"),
        ("WPS-O07", "eight one-bus board instances with eight feed sinks", "SELECTED P0.1 WHOLE-BODY TOPOLOGY", "preserves all five RS-485 power domains and three regulated TTL power domains without cross-connecting feeds"),
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
        ("WPS-E6", "CONTACTORS OPEN / COAST", "upstream source removed; paired branch remains conductive for bounded discharge window", "AXIS -> its one authoritative bus feed -> one of eight brake/dump boundaries", "brake/dump and branch-control timing are not selected"),
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
        ("WPS-D01", "RS-LLEG / ACT_MAIN_SAFE_12V", "one downstream active chopper + resistor bank", "SELECTION REQUIRED", "measured left-leg regenerative energy/current and contactor-open trace"),
        ("WPS-D02", "RS-RLEG / ACT_MAIN_SAFE_12V", "one downstream active chopper + resistor bank", "SELECTION REQUIRED", "measured right-leg regenerative energy/current and contactor-open trace"),
        ("WPS-D03", "RS-LARM / ACT_MAIN_SAFE_12V", "one downstream active chopper + resistor bank", "SELECTION REQUIRED", "measured left-arm regenerative energy/current"),
        ("WPS-D04", "RS-RARM / ACT_MAIN_SAFE_12V", "one downstream active chopper + resistor bank", "SELECTION REQUIRED", "measured right-arm regenerative energy/current"),
        ("WPS-D05", "RS-WAIST / ACT_MAIN_SAFE_12V", "one downstream active chopper + resistor bank", "SELECTION REQUIRED", "measured waist regenerative energy/current"),
        ("WPS-D06", "TTL-LDIST / TTL_LDIST_SAFE_9V", "one downstream active chopper + resistor bank", "SELECTION REQUIRED", "measured left wrist/gripper return energy and 9 V regulator reverse-energy behavior"),
        ("WPS-D07", "TTL-RDIST / TTL_RDIST_SAFE_9V", "one downstream active chopper + resistor bank", "SELECTION REQUIRED", "measured right wrist/gripper return energy and 9 V regulator reverse-energy behavior"),
        ("WPS-D08", "TTL-HEAD / TTL_HEAD_SAFE_9V", "one downstream active chopper + resistor bank", "SELECTION REQUIRED", "measured head return energy and 9 V regulator reverse-energy behavior"),
    ]
    return [controlled({"dump_id": i, "feed": feed, "candidate_role": role, "exact_components_and_threshold": state, "closure_input": evidence}) for i, feed, role, state, evidence in data]


def open_holds() -> list[dict[str, object]]:
    data = [
        ("WPS-H01", "TPS259482L paired use is extrapolated from TI's TPS2595 two-eFuse application note", "obtain TI application review and validate the exact TPS259482L pair across all states"),
        ("WPS-H02", "current-limit setpoints, resistors and ITIMER values are not selected", "measured inrush/RMS/peak/fault/regeneration plus received-device threshold and SOA tests"),
        ("WPS-H03", "six XC330 caps are 0.700 A, below the TPS25948 1 A minimum limit", "select a branch threshold of at least 1 A and prove conductor/connector/fault protection; internal actuator cap remains separate"),
        ("WPS-H04", "datasheet maximum current-limit accuracy is stated only above 3 A while every HR-30 candidate cap is below 3 A", "received-lot calibration over temperature; do not treat calculated ILIM as released"),
        ("WPS-H05", "eight bus-domain brake/dump circuits have no selected devices, thresholds or energy ratings", "measure return energy/current/voltage per bus and size the identical-as-built choppers and resistor banks"),
        ("WPS-H06", "source absorption and reverse-energy behavior are not characterized", "manufacturer-approved application basis and bench characterization of RSP path, contactors and downstream bus"),
        ("WPS-H07", "paired startup, disable and fault timing are unvalidated", "instrument EN, RCBCTRL, IN/MID/OUT, SPLYGD and ILM in both directions under fault"),
        ("WPS-H08", "routed exact-land-pattern PCB candidate lacks production stackup and assembly validation", "fabricator DFM of YWP0012A, exact copper/laminate selection, fabrication outputs, FAI, X-ray inspection, thermal rise and physical board tests"),
        ("WPS-H09", "connector, conductor, fuse and eight-feed coordination remain open", "close protection/conductor architecture inputs with exact parts and hot/fault evidence"),
        ("WPS-H10", "dynamic walking demand and regenerative events are unmeasured", "restrained instrumented trajectories, loss/temperature/overvoltage traces and repeatable fault tests"),
        ("WPS-H11", "functional safety allocation and stopping performance are not validated", "qualified review of identical hardware/software plus measured stopping and fault response"),
        ("WPS-H12", "no procurement, fabrication, connection, powered-test, motion or energization authority exists", "separate signed release after every applicable hold closes"),
    ]
    return [controlled({"hold_id": i, "unresolved_item": item, "closure_evidence": evidence, "state": "OPEN"}) for i, item, evidence in data]


def parts() -> list[Part]:
    result = [
        Part("J1", "CONTROLLED BUS-FEED INPUT", {"1": "FEED_0V", "2": "FEED_VPOS"},
             "TerminalBlock_MetzConnect:TerminalBlock_MetzConnect_Type703_RT10N02HGLU_1x02_P9.52mm_Horizontal",
             "one isolated board input per authoritative bus; exact terminal and production footprint remain under predecessor holds", JST_VH,
             x=8.0, y=34.0, rotation=90.0),
        Part("JBRK", "EXTERNAL FEED BRAKE/DUMP INTERFACE", {"1": "FEED_0V", "2": "FEED_VPOS", "3": "DUMP_DIAG"},
             "Connector_JST:JST_VH_B3P-VH_1x03_P3.96mm_Vertical",
             "physical three-contact architecture interface only; current rating and exact chopper remain selection required", JST_VH,
             x=142.0, y=34.0, rotation=90.0),
    ]
    fp = YWP_FOOTPRINT
    channel_x = (27.0, 46.0, 65.0, 84.0, 103.0, 122.0)
    for channel in range(1, 7):
        c = str(channel)
        x = channel_x[channel - 1]
        bus, axis, mid, gnd = "FEED_VPOS", f"BRANCH_{c}_VPOS", f"CH{c}_MID", "FEED_0V"
        en, rcb = f"CH{c}_EN", f"CH{c}_RCBCTRL"
        f_ilm, r_ilm = f"CH{c}_ILM_F", f"CH{c}_ILM_R"
        f_pg, r_pg = f"CH{c}_PG_F", f"CH{c}_PG_R"
        dvf, dvr = f"CH{c}_DVDT_F", f"CH{c}_DVDT_R"
        itf, itr = f"CH{c}_ITIMER_F", f"CH{c}_ITIMER_R"
        evidence = "TPS259482LYWPR candidate on exact TI YWP0012A example land pattern 4228640/A; PCB fabrication/assembly DFM remains open"
        source = TI_DS
        result.extend([
            Part(f"U{c}F", "TPS259482L FORWARD OCP", {"1": en, "2": f"CH{c}_OV_F", "3": f_pg, "4": rcb, "5": bus, "6": mid, "7": dvf, "8": gnd, "9": f_ilm, "10": itf, "11": mid, "12": bus}, fp, evidence, source, x=x-3.0, y=29.0),
            Part(f"U{c}R", "TPS259482L REVERSE OCP", {"1": en, "2": f"CH{c}_OV_R", "3": r_pg, "4": rcb, "5": axis, "6": mid, "7": dvr, "8": gnd, "9": r_ilm, "10": itr, "11": mid, "12": axis}, fp, evidence, source, x=x+3.0, y=29.0, rotation=180.0),
            Part(f"J{c}O", f"CHANNEL {c} AXIS OUTPUT", {"1": gnd, "2": axis}, "Connector_JST:JST_VH_B2P-VH_1x02_P3.96mm_Vertical", "candidate local power pair", JST_VH, x=x, y=59.0),
            Part(f"J{c}C", f"CHANNEL {c} CONTROL/MONITOR", {"1": gnd, "2": en, "3": f_pg, "4": r_pg, "5": f_ilm, "6": r_ilm, "7": rcb}, "Connector_JST:JST_GH_BM07B-GHS-TBT_1x07-1MP_P1.25mm_Vertical", "ordinary diagnostics/control only; zero safety credit", JST_GH, x=x, y=8.0),
            Part(f"R{c}E", "100k EN pulldown", {"1": en, "2": gnd}, "Resistor_SMD:R_0603_1608Metric", "candidate fail-low bias; exact control circuit remains open", source, x=x-6.0, y=18.0),
            Part(f"R{c}B", "10k RCBCTRL pulldown", {"1": rcb, "2": gnd}, "Resistor_SMD:R_0603_1608Metric", "pull low enables bidirectional steady-state flow; disabled/fault state remains blocking by device behavior", source, x=x-4.0, y=18.0),
            Part(f"R{c}F", "RILM FORWARD - SELECTION REQUIRED", {"1": f_ilm, "2": gnd}, "Resistor_SMD:R_0603_1608Metric", "no value released; ILIM range and accuracy boundaries apply", source, x=x-2.0, y=18.0),
            Part(f"R{c}R", "RILM REVERSE - SELECTION REQUIRED", {"1": r_ilm, "2": gnd}, "Resistor_SMD:R_0603_1608Metric", "independent reverse-current limit remains selection required", source, x=x, y=18.0),
            Part(f"R{c}OF", "0R OVLO FORWARD PULLDOWN CANDIDATE", {"1": f"CH{c}_OV_F", "2": gnd}, "Resistor_SMD:R_0603_1608Metric", "prevents prohibited floating OVLO state; upstream feed overvoltage and final population remain open", source, x=x+2.0, y=18.0),
            Part(f"R{c}OR", "0R OVLO REVERSE PULLDOWN CANDIDATE", {"1": f"CH{c}_OV_R", "2": gnd}, "Resistor_SMD:R_0603_1608Metric", "prevents prohibited floating OVLO state; upstream feed overvoltage and final population remain open", source, x=x+4.0, y=18.0),
            Part(f"C{c}F", "DVDT FORWARD - SELECTION REQUIRED", {"1": dvf, "2": gnd}, "Capacitor_SMD:C_0603_1608Metric", "startup slew interaction requires test", source, x=x+6.0, y=18.0),
            Part(f"C{c}R", "DVDT REVERSE - SELECTION REQUIRED", {"1": dvr, "2": gnd}, "Capacitor_SMD:C_0603_1608Metric", "startup slew interaction requires test", source, x=x-5.0, y=42.0),
            Part(f"C{c}I", "INPUT BYPASS - SELECTION REQUIRED", {"1": bus, "2": gnd}, "Capacitor_SMD:C_0805_2012Metric", "value/voltage/bias/placement open", source, x=x-1.8, y=42.0),
            Part(f"C{c}O", "AXIS BYPASS - SELECTION REQUIRED", {"1": axis, "2": gnd}, "Capacitor_SMD:C_0805_2012Metric", "value/voltage/bias/regeneration pulse open", source, x=x+1.8, y=42.0),
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
    overview = model.Sheet(1, "01_system_boundaries.kicad_sch", "Eight isolated bus feeds and six-channel board pattern", "One board pattern is instantiated once per authoritative actuator bus; 25 channels populated and 23 DNP.")
    overview.components = [by_ref["J1"], by_ref["JBRK"]] + [by_ref[f"J{i}O"] for i in range(1, 7)] + [by_ref[f"J{i}C"] for i in range(1, 7)]
    for index, component in enumerate(overview.components):
        component.position = (52 + (index % 3) * 145, 46 + (index // 3) * 57); component.width = 84
    overview.notes = ["Each of eight board instances receives exactly one authoritative bus feed; no left/right or 9 V domains are tied together.", "JBRK is a real downstream interface obligation, not a released resistor/chopper selection.", "Each axis output is an individual power pair; data harnesses remain data-only.", WARNING]
    sheets.append(overview)
    for channel in range(1, 7):
        c = str(channel)
        refs = [f"U{c}F", f"U{c}R", f"R{c}E", f"R{c}B", f"R{c}F", f"R{c}R", f"R{c}OF", f"R{c}OR", f"C{c}F", f"C{c}R", f"C{c}I", f"C{c}O"]
        sheet = model.Sheet(channel + 1, f"{channel + 1:02d}_paired_channel_{channel}.kicad_sch", f"Paired bidirectional branch {channel}", "One TPS259482L faces each current direction; exact setpoints and PCB remain open.")
        sheet.components = [by_ref[ref] for ref in refs]
        for index, component in enumerate(sheet.components):
            component.position = (54 + (index % 3) * 145, 45 + (index // 3) * 67); component.width = 88
        sheet.notes = ["Motoring: UxF provides IN-to-OUT overcurrent protection.", "Regeneration: UxR provides IN-to-OUT overcurrent protection.", "A single TPS25948 is insufficient because reverse-direction OCP is not provided.", "Eight isolated bus-domain brake/dump circuits are still required for contactor-open energy.", WARNING]
        sheets.append(sheet)
    net_counts = Counter(pin.net for component in components for pin in component.pins)
    wires = model.build_wire_numbers(sheets, net_counts)
    root_uuid = model.uid("root-hr30-walking-power-successor-p0.1")
    project = {"board": {}, "boards": [], "cvpcb": {}, "erc": {}, "libraries": {}, "meta": {"filename": f"{PROJECT}.kicad_pro", "version": 1}, "net_settings": {"classes": [{"name": "Default", "priority": 2147483647, "clearance": 0.2, "track_width": 0.25, "via_diameter": 0.8, "via_drill": 0.4}], "meta": {"version": 3}}, "pcbnew": {}, "schematic": {}, "text_variables": {"PROJECT_STATUS": WARNING}}
    (OUT / f"{PROJECT}.kicad_pro").write_text(json.dumps(project, indent=2) + "\n", encoding="utf-8")
    symbols = [model.lib_symbol(component).replace(f'(symbol "PBV3:{component.ref}"', f'(symbol "{component.ref}"', 1) for component in components]
    (OUT / f"{PROJECT}.kicad_sym").write_text('(kicad_symbol_lib\n  (version 20251024) (generator "kicad_symbol_editor") (generator_version "10.0")\n  ' + "\n".join(symbols) + "\n)\n", encoding="utf-8")
    (OUT / "sym-lib-table").write_text(f'(sym_lib_table\n  (version 7)\n  (lib (name "PBV3")(type "KiCad")(uri "${{KIPRJMOD}}/{PROJECT}.kicad_sym")(options "")(descr "HR-30 walking-power successor symbols"))\n)\n', encoding="utf-8")
    (OUT / "fp-lib-table").write_text(
        f'(fp_lib_table\n  (version 7)\n  (lib (name "{YWP_LIBRARY}")(type "KiCad")(uri "${{KIPRJMOD}}/{YWP_LIBRARY}.pretty")(options "")(descr "Exact TI YWP0012A land pattern"))\n)\n',
        encoding="utf-8",
    )
    (OUT / f"{PROJECT}.kicad_sch").write_text(model.root_schematic(root_uuid, sheets), encoding="utf-8")
    for sheet in sheets:
        (OUT / sheet.filename).write_text(model.child_schematic(root_uuid, sheet, net_counts, wires), encoding="utf-8")


def route_board(board: pcbnew.BOARD, nets: dict[str, pcbnew.NETINFO_ITEM]) -> dict[str, object]:
    """Deterministically route the six-channel pattern on ten copper layers."""
    layer_for: dict[str, int] = {}
    for name in nets:
        if name == "FEED_VPOS":
            layer_for[name] = pcbnew.In1_Cu
        elif name.startswith("BRANCH_"):
            layer_for[name] = pcbnew.In2_Cu
        elif name.endswith("_MID"):
            layer_for[name] = pcbnew.In3_Cu
        elif "_EN" in name or "_OV_" in name:
            layer_for[name] = pcbnew.In4_Cu
        elif "_PG_" in name:
            layer_for[name] = pcbnew.In5_Cu
        elif "_RCBCTRL" in name:
            layer_for[name] = pcbnew.In6_Cu
        elif "_ILM_" in name:
            layer_for[name] = pcbnew.In7_Cu
        else:
            layer_for[name] = pcbnew.In8_Cu

    pad_records: list[dict[str, object]] = []
    via_points: list[tuple[float, float, str]] = []
    footprints = {fp.GetReference(): fp for fp in board.GetFootprints()}
    for fp in footprints.values():
        for pad in fp.Pads():
            name = pad.GetNetname()
            if not name:
                continue
            pos = pad.GetPosition()
            box = pad.GetBoundingBox()
            pad_records.append({
                "net": name,
                "ref": fp.GetReference(),
                "pad": pad.GetNumber(),
                "point": (pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y)),
                "bounds": (pcbnew.ToMM(box.GetX()), pcbnew.ToMM(box.GetY()), pcbnew.ToMM(box.GetRight()), pcbnew.ToMM(box.GetBottom())),
                "through": pad.IsOnLayer(pcbnew.F_Cu) and pad.IsOnLayer(pcbnew.B_Cu),
            })
    pad_net_counts = Counter(str(record["net"]) for record in pad_records)

    def clear_of_pads(point: tuple[float, float], own_net: str, margin: float = 0.20) -> bool:
        x, y = point
        for record in pad_records:
            if record["net"] == own_net:
                continue
            left, top, right, bottom = record["bounds"]
            if left - margin <= x <= right + margin and top - margin <= y <= bottom + margin:
                return False
        return True

    access = {name: [] for name in nets}
    fanouts = 0
    for record in pad_records:
        name = str(record["net"])
        px, py = record["point"]
        if record["through"]:
            access[name].append((px, py))
            continue
        if pad_net_counts[name] == 1:
            # Intentionally exposed selection-required IC controls remain
            # copper pads without a purposeless dangling via.
            access[name].append((px, py))
            continue
        fp = footprints[str(record["ref"])]
        center = fp.GetPosition()
        cx, cy = pcbnew.ToMM(center.x), pcbnew.ToMM(center.y)
        dx, dy = px - cx, py - cy
        magnitude = max((dx * dx + dy * dy) ** 0.5, 1e-9)
        ux, uy = dx / magnitude, dy / magnitude
        if str(record["ref"]).startswith("U") and str(record["pad"]) in {"5", "6", "11", "12"}:
            # Move the four wide power lands vertically away from the control
            # lands before the through-via transition.
            ux, uy = (0.0, -1.0) if dy < 0 else (0.0, 1.0)
        elif str(record["ref"]).startswith("J") and str(record["ref"]).endswith("C"):
            # The seven-pin control connector escapes toward the board centre;
            # horizontal radial fanout would cross adjacent pads.
            ux, uy = (0.0, 1.0)
        base = 1.45 if str(record["ref"]).startswith("U") else 1.00
        candidate = None
        # Dense rows of bias/monitor parts do not always have a clear escape
        # along the pad's radial vector.  Search deterministic alternate escape
        # directions before declaring the placement unroutable.
        directions = [(ux, uy), (0.0, 1.0), (0.0, -1.0), (1.0, 0.0), (-1.0, 0.0),
                      (0.70710678, 0.70710678), (-0.70710678, 0.70710678),
                      (0.70710678, -0.70710678), (-0.70710678, -0.70710678)]
        for ex, ey in directions:
            for step in range(22):
                distance = base + 0.20 * step
                trial = (round((px + ex * distance) * 4) / 4, round((py + ey * distance) * 4) / 4)
                if not (1.0 < trial[0] < BOARD_W - 1.0 and 1.0 < trial[1] < BOARD_H - 1.0):
                    continue
                if not clear_of_pads(trial, name):
                    continue
                if any((trial[0] - x) ** 2 + (trial[1] - y) ** 2 < 0.58 ** 2 for x, y, _ in via_points):
                    continue
                candidate = trial
                break
            if candidate is not None:
                break
        if candidate is None:
            raise RuntimeError(f"no fanout escape for {record['ref']}.{record['pad']} {name}")
        carrier.add_track(board, nets[name], (px, py), candidate, pcbnew.F_Cu, 0.10 if str(record["ref"]).startswith("U") else 0.15)
        add_via(board, nets[name], candidate)
        via_points.append((candidate[0], candidate[1], name))
        access[name].append(candidate)
        fanouts += 1

    # FEED_VPOS is a dedicated internal plane; FEED_0V uses the outer pours.
    # Point-to-point routing is therefore limited to branch/control families.
    route_names = [name for name, points in access.items() if name not in {"FEED_0V", "FEED_VPOS"} and len(points) > 1]
    grid = 0.50
    origin = 1.0
    nx = int((BOARD_W - 2.0) / grid) + 1
    ny = int((BOARD_H - 2.0) / grid) + 1
    mounting = ((3.5, 3.5), (BOARD_W - 3.5, 3.5), (3.5, BOARD_H - 3.5), (BOARD_W - 3.5, BOARD_H - 3.5))
    occupied = {layer: {} for layer in set(layer_for.values())}

    def point(cell: tuple[int, int]) -> tuple[float, float]:
        return origin + cell[0] * grid, origin + cell[1] * grid

    def cell_for(position: tuple[float, float]) -> tuple[int, int]:
        return round((position[0] - origin) / grid), round((position[1] - origin) / grid)

    def available(cell: tuple[int, int], name: str, width: float) -> bool:
        ix, iy = cell
        if not (0 <= ix < nx and 0 <= iy < ny):
            return False
        x, y = point(cell)
        radius = 0.225 + width / 2 + 0.10
        if any((x - hx) ** 2 + (y - hy) ** 2 < (1.55 + width / 2) ** 2 for hx, hy in mounting):
            return False
        if any(other != name and (x - vx) ** 2 + (y - vy) ** 2 < radius ** 2 for vx, vy, other in via_points):
            return False
        for record in pad_records:
            if record["net"] == name or not record["through"]:
                continue
            left, top, right, bottom = record["bounds"]
            if left - 0.10 - width / 2 <= x <= right + 0.10 + width / 2 and top - 0.10 - width / 2 <= y <= bottom + 0.10 + width / 2:
                return False
        return occupied[layer_for[name]].get(cell) in (None, name)

    def path_to_tree(start: tuple[int, int], tree: set[tuple[int, int]], name: str, width: float) -> list[tuple[int, int]]:
        if start in tree:
            return [start]
        xs = [cell[0] for cell in tree]
        ys = [cell[1] for cell in tree]
        heuristic = lambda cell: max(min(xs) - cell[0], 0, cell[0] - max(xs)) + max(min(ys) - cell[1], 0, cell[1] - max(ys))
        frontier = [(0, 0, start)]
        parents = {start: None}
        costs = {start: 0}
        serial = 1
        while frontier:
            _, _, cell = heapq.heappop(frontier)
            if cell in tree:
                result = [cell]
                while parents[result[-1]] is not None:
                    result.append(parents[result[-1]])
                result.reverse()
                return result
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nxt = (cell[0] + dx, cell[1] + dy)
                if not available(nxt, name, width):
                    continue
                new_cost = costs[cell] + 1
                if new_cost >= costs.get(nxt, 10 ** 12):
                    continue
                costs[nxt] = new_cost
                parents[nxt] = cell
                heapq.heappush(frontier, (new_cost + heuristic(nxt), serial, nxt))
                serial += 1
        raise RuntimeError(f"no deterministic route for {name}")

    segments = 0
    priority = lambda name: (0 if name == "FEED_VPOS" else 1 if name.startswith("BRANCH_") else 2 if name.endswith("_MID") else 3, name)
    for name in sorted(route_names, key=priority):
        width = 1.00 if name == "FEED_VPOS" else 0.80 if name.startswith("BRANCH_") or name.endswith("_MID") else 0.15
        layer = layer_for[name]
        endpoints = [cell_for(position) for position in access[name]]
        root = endpoints[0]
        if not available(root, name, width):
            raise RuntimeError(f"blocked route root for {name}")
        tree = {root}
        occupied[layer][root] = name
        carrier.add_track(board, nets[name], access[name][0], point(root), layer, width)
        segments += 1
        for exact, target in zip(access[name][1:], endpoints[1:]):
            if not available(target, name, width):
                candidates = sorted((dx * dx + dy * dy, (target[0] + dx, target[1] + dy)) for dx in range(-10, 11) for dy in range(-10, 11))
                target = next((cell for _, cell in candidates if available(cell, name, width)), None)
                if target is None:
                    raise RuntimeError(f"no clear target for {name}")
            route = path_to_tree(target, tree, name, width)
            carrier.add_track(board, nets[name], exact, point(route[0]), layer, width)
            segments += 1
            start = route[0]
            direction = None
            for index in range(1, len(route) + 1):
                next_direction = None if index == len(route) else (route[index][0] - route[index - 1][0], route[index][1] - route[index - 1][1])
                if direction is None:
                    direction = next_direction
                if index == len(route) or next_direction != direction:
                    carrier.add_track(board, nets[name], point(start), point(route[index - 1]), layer, width)
                    segments += 1
                    start = route[index - 1]
                    direction = next_direction
            for cell in route:
                occupied[layer][cell] = name
                tree.add(cell)
    return {
        "via_count": len(via_points), "fanout_count": fanouts, "track_segment_count": segments,
        "routing_complete": True, "routing_grid_mm": grid,
        "routing_method": "ten-layer deterministic family-separated routing with exact YWP fanout",
    }


def add_plane_zones(board: pcbnew.BOARD, ground: pcbnew.NETINFO_ITEM, feed: pcbnew.NETINFO_ITEM) -> None:
    for layer, net in ((pcbnew.F_Cu, ground), (pcbnew.B_Cu, ground), (pcbnew.In1_Cu, feed)):
        zone = pcbnew.ZONE(board)
        zone.SetLayer(layer)
        zone.SetNet(net)
        zone.SetLocalClearance(pcbnew.FromMM(0.20))
        zone.SetMinThickness(pcbnew.FromMM(0.254))
        zone.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
        polygon = zone.Outline()
        polygon.NewOutline()
        for x, y in ((0.8, 0.8), (BOARD_W - 0.8, 0.8), (BOARD_W - 0.8, BOARD_H - 0.8), (0.8, BOARD_H - 0.8)):
            polygon.Append(pcbnew.VECTOR2I_MM(x, y))
        board.Add(zone)


def write_board(items: list[Part]) -> dict[str, object]:
    board = pcbnew.BOARD()
    board.SetCopperLayerCount(10)
    settings = board.GetDesignSettings()
    settings.SetBoardThickness(pcbnew.FromMM(1.6))
    settings.m_MinClearance = pcbnew.FromMM(0.10)
    settings.m_TrackMinWidth = pcbnew.FromMM(0.10)
    settings.m_HoleClearance = pcbnew.FromMM(0.10)
    settings.m_HoleToHoleMin = pcbnew.FromMM(0.25)
    settings.m_ViasMinSize = pcbnew.FromMM(0.45)
    settings.m_MinThroughDrill = pcbnew.FromMM(0.20)
    settings.m_ViasMinAnnularWidth = pcbnew.FromMM(0.10)
    settings.m_SolderMaskMinWidth = pcbnew.FromMM(0.00)
    settings.m_NetSettings.GetDefaultNetclass().SetClearance(pcbnew.FromMM(0.10))
    net_names = sorted({net for item in items for net in item.pins.values() if net})
    nets: dict[str, pcbnew.NETINFO_ITEM] = {}
    for name in net_names:
        net = pcbnew.NETINFO_ITEM(board, name)
        board.Add(net)
        nets[name] = net
    for item in items:
        footprint = load_fp(item.footprint)
        footprint.SetReference(item.ref)
        footprint.SetValue(item.value)
        footprint.SetPosition(pcbnew.VECTOR2I_MM(item.x, item.y))
        footprint.SetOrientationDegrees(item.rotation + (90.0 if item.ref.startswith(("R", "C")) else 0.0))
        footprint.Reference().SetVisible(False)
        footprint.Value().SetVisible(False)
        for pad in footprint.Pads():
            if item.ref.startswith("U"):
                # TI specifies the copper land geometry; the final mask process
                # is fabricator-dependent and remains in the DFM hold.
                pad.SetLocalSolderMaskMargin(pcbnew.FromMM(-0.025))
            net_name = item.pins.get(pad.GetNumber())
            if net_name:
                pad.SetNet(nets[net_name])
        board.Add(footprint)
    for index, (x, y) in enumerate(((3.5, 3.5), (BOARD_W - 3.5, 3.5), (3.5, BOARD_H - 3.5), (BOARD_W - 3.5, BOARD_H - 3.5)), 1):
        hole = carrier.lib_fp("MountingHole:MountingHole_2.7mm_M2.5")
        hole.SetReference(f"MH{index}")
        hole.SetValue("M2.5 BOARD-ONLY")
        hole.SetPosition(pcbnew.VECTOR2I_MM(x, y))
        hole.SetBoardOnly(True)
        hole.SetExcludedFromBOM(True)
        hole.SetExcludedFromPosFiles(True)
        hole.Reference().SetVisible(False)
        hole.Value().SetVisible(False)
        board.Add(hole)
    corners = ((0, 0), (BOARD_W, 0), (BOARD_W, BOARD_H), (0, BOARD_H))
    for start, end in zip(corners, corners[1:] + corners[:1]):
        edge = pcbnew.PCB_SHAPE(board)
        edge.SetShape(pcbnew.SHAPE_T_SEGMENT)
        edge.SetStart(pcbnew.VECTOR2I_MM(*start))
        edge.SetEnd(pcbnew.VECTOR2I_MM(*end))
        edge.SetLayer(pcbnew.Edge_Cuts)
        edge.SetWidth(pcbnew.FromMM(0.20))
        board.Add(edge)
    routing = route_board(board, nets)
    add_plane_zones(board, nets["FEED_0V"], nets["FEED_VPOS"])
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    carrier.add_text(board, "HR-30 6CH BIDIRECTIONAL WALKING POWER P0.1", 36, 1.5, 0.82, pcbnew.B_SilkS)
    carrier.add_text(board, "PRELIMINARY - NO POWER AUTHORITY", 48, BOARD_H - 1.4, 0.82, pcbnew.B_SilkS)
    path = OUT / f"{PROJECT}.kicad_pcb"
    pcbnew.SaveBoard(str(path), board)
    return {"path": path, "net_count": len(net_names), "part_count": len(items), "routing": routing}


def validate_kicad(board: dict[str, object]) -> dict[str, object]:
    validation = OUT / "validation"; output = OUT / "output"
    validation.mkdir(); output.mkdir()
    erc = subprocess.run([str(KICAD), "sch", "erc", "--exit-code-violations", "--output", str(validation / f"{PROJECT}-erc.rpt"), str(OUT / f"{PROJECT}.kicad_sch")], cwd=OUT, text=True, capture_output=True)
    if erc.returncode != 0:
        raise RuntimeError(f"KiCad ERC failed ({erc.returncode})\n{erc.stdout}\n{erc.stderr}")
    export = subprocess.run([str(KICAD), "sch", "export", "svg", "--output", str(output), str(OUT / f"{PROJECT}.kicad_sch")], cwd=OUT, text=True, capture_output=True)
    if export.returncode != 0:
        raise RuntimeError(f"KiCad SVG export failed\n{export.stdout}\n{export.stderr}")
    drc = subprocess.run([str(KICAD), "pcb", "drc", "--severity-all", "--exit-code-violations", "--output", str(validation / f"{PROJECT}-drc.rpt"), str(board["path"])], cwd=OUT, text=True, capture_output=True)
    if drc.returncode != 0:
        raise RuntimeError(f"KiCad DRC failed ({drc.returncode})\n{drc.stdout}\n{drc.stderr}")
    for suffix, layers, extra in (
        ("front", "F.Cu,F.Silkscreen,F.Mask,Edge.Cuts", []),
        ("back", "B.Cu,B.Silkscreen,B.Mask,Edge.Cuts", ["--mirror"]),
    ):
        rendered = subprocess.run([str(KICAD), "pcb", "export", "svg", "--mode-single", "--output", str(output / f"{PROJECT}-{suffix}.svg"), "--layers", layers, "--fit-page-to-board", "--exclude-drawing-sheet", *extra, str(board["path"])], cwd=OUT, text=True, capture_output=True)
        if rendered.returncode != 0:
            raise RuntimeError(f"KiCad PCB SVG export failed: {suffix}\n{rendered.stdout}\n{rendered.stderr}")
    for layer in tuple(f"In{i}.Cu" for i in range(1, 9)):
        target = output / f"{PROJECT}-{layer.lower().replace('.', '-')}.svg"
        rendered = subprocess.run([str(KICAD), "pcb", "export", "svg", "--mode-single", "--output", str(target), "--layers", f"{layer},Edge.Cuts", "--fit-page-to-board", "--exclude-drawing-sheet", str(board["path"])], cwd=OUT, text=True, capture_output=True)
        if rendered.returncode != 0:
            raise RuntimeError(f"KiCad internal-layer export failed: {layer}\n{rendered.stdout}\n{rendered.stderr}")
    for svg in output.glob("*.svg"):
        svg.write_text("\n".join(line.rstrip() for line in svg.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")
    (OUT / f"{PROJECT}.kicad_prl").unlink(missing_ok=True)
    drc_text = (validation / f"{PROJECT}-drc.rpt").read_text(encoding="utf-8", errors="replace")
    return {
        "kicad_version": "10.0.5", "native_sheet_count_including_root": 8,
        "erc_errors": 0, "erc_warnings": 0, "drc_errors": 0, "drc_warnings": 0,
        "unconnected_pads": 0, "exported_svg_count": len(list(output.glob("*.svg"))),
        "drc_report_line_count": len(drc_text.splitlines()),
        "pcb_layout_state": "ROUTED CANDIDATE - DRC 0/0 - PHYSICAL/THERMAL/DFM VALIDATION OPEN",
    }


def _legacy_branch_svg() -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1500" height="820" viewBox="0 0 1500 820" role="img" aria-labelledby="title desc"><title id="title">Paired HR-30 bidirectional actuator branch</title><desc id="desc">Two oppositely oriented TPS259482L eFuses connect the PDU bus to one actuator. The forward device protects motoring current; the reverse-oriented device protects regenerative current. A five-feed brake dump remains required.</desc><defs><marker id="a" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#0b5b9b"/></marker><marker id="r" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#a03921"/></marker></defs><style>text{{font:600 19px system-ui;fill:#102a43}}.h{{font-size:34px;font-weight:900}}.s{{font-size:16px}}.box{{fill:#fff;stroke:#0b5b9b;stroke-width:4}}.gold{{fill:#fff0ad;stroke:#8a6200;stroke-width:4}}.hold{{fill:#ffe4df;stroke:#a03921;stroke-width:4}}.f{{stroke:#0b5b9b;stroke-width:8;fill:none;marker-end:url(#a)}}.r{{stroke:#a03921;stroke-width:8;fill:none;marker-end:url(#r)}}.wire{{stroke:#183c5d;stroke-width:7}}</style><rect width="1500" height="820" fill="#eef8ff"/><text class="h" x="55" y="60">HR-30 walking branch: protected in both directions</text><text x="55" y="102">A single bidirectional TPS25948 path is not enough: its OCP acts only from IN to OUT.</text><rect class="gold" x="55" y="180" width="230" height="120" rx="18"/><text x="92" y="232">PDU 12 V bus</text><text class="s" x="92" y="266">five feed instances</text><path class="wire" d="M285 240H390"/><rect class="box" x="390" y="160" width="300" height="160" rx="20"/><text class="h" x="432" y="218">UxF</text><text x="432" y="256">TPS259482L</text><text class="s" x="432" y="288">IN=BUS · OUT=MID</text><path class="wire" d="M690 240H810"/><text x="732" y="222">MID</text><rect class="box" x="810" y="160" width="300" height="160" rx="20"/><text class="h" x="852" y="218">UxR</text><text x="852" y="256">TPS259482L</text><text class="s" x="852" y="288">IN=AXIS · OUT=MID</text><path class="wire" d="M1110 240H1215"/><rect class="gold" x="1215" y="180" width="230" height="120" rx="18"/><text x="1252" y="232">DYNAMIXEL</text><text class="s" x="1252" y="266">one local power pair</text><path class="f" d="M230 390H1260"/><text x="575" y="370">MOTORING: BUS → AXIS · UxF provides forward OCP</text><path class="r" d="M1260 500H230"/><text x="555" y="545">REGENERATION: AXIS → BUS · UxR provides forward OCP</text><rect class="hold" x="55" y="620" width="1390" height="130" rx="20"/><text class="h" x="92" y="671">Still required before walking</text><text x="92" y="715">Five downstream brake/dump circuits, measured energy, exact thresholds, routed PCB, thermal proof and contactor-open timing.</text><text class="s" x="55" y="795">{WARNING}</text></svg>'''


def branch_svg() -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1500" height="820" viewBox="0 0 1500 820" role="img" aria-labelledby="title desc"><title id="title">Paired HR-30 bidirectional actuator branch</title><desc id="desc">Two oppositely oriented TPS259482L eFuses connect one electrically isolated actuator-bus feed to one actuator. The forward device protects motoring current; the reverse-oriented device protects regenerative current. Eight bus-domain brake dumps remain required.</desc><defs><marker id="a" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#0b5b9b"/></marker><marker id="r" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#a03921"/></marker></defs><style>text{{font:600 19px system-ui;fill:#102a43}}.h{{font-size:34px;font-weight:900}}.s{{font-size:16px}}.box{{fill:#fff;stroke:#0b5b9b;stroke-width:4}}.gold{{fill:#fff0ad;stroke:#8a6200;stroke-width:4}}.hold{{fill:#ffe4df;stroke:#a03921;stroke-width:4}}.f{{stroke:#0b5b9b;stroke-width:8;fill:none;marker-end:url(#a)}}.r{{stroke:#a03921;stroke-width:8;fill:none;marker-end:url(#r)}}.wire{{stroke:#183c5d;stroke-width:7}}</style><rect width="1500" height="820" fill="#eef8ff"/><text class="h" x="55" y="60">HR-30 walking branch: protected in both directions</text><text x="55" y="102">A single bidirectional TPS25948 path is not enough: its OCP acts only from IN to OUT.</text><rect class="gold" x="55" y="180" width="230" height="120" rx="18"/><text x="92" y="232">One bus feed</text><text class="s" x="92" y="266">one of 8 isolated domains</text><path class="wire" d="M285 240H390"/><rect class="box" x="390" y="160" width="300" height="160" rx="20"/><text class="h" x="432" y="218">UxF</text><text x="432" y="256">TPS259482L</text><text class="s" x="432" y="288">IN=BUS / OUT=MID</text><path class="wire" d="M690 240H810"/><text x="732" y="222">MID</text><rect class="box" x="810" y="160" width="300" height="160" rx="20"/><text class="h" x="852" y="218">UxR</text><text x="852" y="256">TPS259482L</text><text class="s" x="852" y="288">IN=AXIS / OUT=MID</text><path class="wire" d="M1110 240H1215"/><rect class="gold" x="1215" y="180" width="230" height="120" rx="18"/><text x="1252" y="232">DYNAMIXEL</text><text class="s" x="1252" y="266">one local power pair</text><path class="f" d="M230 390H1260"/><text x="575" y="370">MOTORING: BUS to AXIS / UxF provides forward OCP</text><path class="r" d="M1260 500H230"/><text x="555" y="545">REGENERATION: AXIS to BUS / UxR provides forward OCP</text><rect class="hold" x="55" y="620" width="1390" height="130" rx="20"/><text class="h" x="92" y="671">Still required before walking</text><text x="92" y="715">Eight bus-domain brake/dump circuits, measured energy, exact thresholds, routed PCB, thermal proof and contactor-open timing.</text><text class="s" x="55" y="795">{WARNING}</text></svg>'''


def _legacy_page(status: dict[str, object], allocations: list[dict[str, object]], board_losses: list[dict[str, object]], holds: list[dict[str, object]]) -> str:
    alloc_html = "".join(f'<tr><td>{r["board_instance"]}</td><td>{r["channel"]}</td><td>{r["axis_id"]}</td><td>{r["actuator_family"]}</td><td>{r["candidate_internal_cap_a"]}</td></tr>' for r in allocations)
    loss_html = "".join(f'<tr><td>{r["board_instance"]}</td><td>{r["populated_axis_count"]}</td><td>{r["arithmetic_cap_sum_a"]}</td><td>{r["simultaneous_pair_loss_typ_w"]}</td><td>{r["simultaneous_pair_loss_hot_max_w"]}</td></tr>' for r in board_losses)
    hold_html = "".join(f'<li><b>{r["hold_id"]}</b> {html.escape(str(r["unresolved_item"]))}</li>' for r in holds)
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 walking-power successor</title><style>:root{{--deep:#071f3b;--blue:#0b5b9b;--sky:#d6f1ff;--gold:#f4bd21;--paper:#f6fbff;--ink:#122c45;--red:#9d3520;--line:#82c5e6}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.55 system-ui,Segoe UI,sans-serif}}header,main,footer{{padding:clamp(24px,5vw,64px) max(18px,calc((100vw - 1280px)/2))}}header,footer{{background:linear-gradient(135deg,var(--deep),var(--blue));color:white}}h1{{font-size:clamp(38px,6vw,72px);line-height:1.03;max-width:18ch}}h2{{font-size:clamp(28px,4vw,44px)}}h3{{font-size:22px}}.warning{{background:var(--gold);color:#17243a;border:3px solid #7b5600;padding:16px;font-weight:900}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:18px}}article,.panel,li{{background:white;border:2px solid var(--line);border-radius:16px;padding:19px}}.metric{{font-size:clamp(34px,5vw,55px);font-weight:900;color:var(--blue)}}.hold{{border-color:#bf6a56;background:#fff2ef}}.hold .metric,.bad{{color:var(--red)}}.scroll{{overflow:auto;border:2px solid var(--line);border-radius:16px;background:white}}object{{display:block;width:100%;min-width:900px}}table{{border-collapse:collapse;width:100%;min-width:900px}}th,td{{padding:14px;text-align:left;border-bottom:1px solid var(--line);font-size:16px}}th{{background:var(--sky)}}a{{color:#075b9b;font-weight:800}}li{{margin:12px 0}}code{{font-size:16px}}@media(max-width:560px){{body{{font-size:16px}}}}</style></head><body><header><div class="warning">{html.escape(WARNING)}</div><p>HR-30 whole-body P0.1</p><h1>The walking branch now has a real return path.</h1><p>Every populated actuator branch uses a candidate pair of oppositely oriented eFuses: one protects motoring current and one protects regenerative current.</p></header><main><section class="grid"><article><div class="metric">25</div><p>whole-body axes bound to paired branch slots</p></article><article><div class="metric">50</div><p>candidate populated TPS259482L devices</p></article><article><div class="metric">ERC 0/0</div><p>eight native KiCad sheets including root</p></article><article class="hold"><div class="metric">5 open</div><p>feed-level brake/dump circuits still require measured sizing</p></article></section><section><h2>Why two devices are required</h2><div class="scroll"><object data="bidirectional-branch-schematic.svg" type="image/svg+xml" aria-label="Paired bidirectional eFuse architecture"></object></div><p>TI documents that TPS25948 can pass bidirectional steady-state current when RCBCTRL is low, but its overcurrent protection acts only from IN to OUT. The selected P0.1 candidate therefore places one device in each direction. This is an engineering inference from TI's bidirectional two-eFuse application architecture and still requires TI application review and physical validation.</p></section><section><h2>Native KiCad is included</h2><div class="panel"><p><a href="{PROJECT}.kicad_pro">Open the native KiCad project</a> · <a href="output/{PROJECT}.svg">root schematic export</a> · <a href="validation/{PROJECT}-erc.rpt">complete ERC report</a>.</p><p>The project contains one boundary sheet and six fully populated paired-channel sheets. It is a connected schematic candidate, not a routed or fabrication-released PCB.</p></div></section><section><h2>Five board instances and 25 axes</h2><div class="scroll"><table><thead><tr><th>Board</th><th>Channel</th><th>Axis</th><th>Actuator</th><th>Internal cap A</th></tr></thead><tbody>{alloc_html}</tbody></table></div></section><section><h2>Pair conduction-loss screen</h2><p>These values use the axis cap as if simultaneous and therefore bound silicon conduction loss only. They are not measured walking duty or a thermal release.</p><div class="scroll"><table><thead><tr><th>Board</th><th>Axes</th><th>Cap sum A</th><th>Pair loss typ W</th><th>Pair loss hot-max W</th></tr></thead><tbody>{loss_html}</tbody></table></div><p><a href="axis-pair-loss-screen.csv">Open all 25 axis calculations</a> · <a href="board-pair-loss-screen.csv">five-board summary</a>.</p></section><section class="panel"><h2>The honest remaining blocker</h2><p>When K1/K2 open, the source is gone but the robot can still return mechanical energy. The paired branches allow that energy onto each downstream feed, but each of the five feeds still needs a measured, independently powered brake/dump circuit. No resistor, chopper, voltage threshold or energy rating is released.</p><p><a href="feed-brake-dump-boundary.csv">Open the five-feed brake/dump obligations</a> · <a href="energy-flow-state-register.csv">eight power states</a> · <a href="architecture-option-register.csv">architecture decisions</a>.</p><h2>Open holds</h2><ul>{hold_html}</ul></section></main><footer>{html.escape(WARNING)}</footer></body></html>'''


def page(status: dict[str, object], allocations: list[dict[str, object]], board_losses: list[dict[str, object]], holds: list[dict[str, object]]) -> str:
    alloc_html = "".join(
        f'<tr><td>{r["board_instance"]}</td><td>{r["bus_id"]}</td><td>{r["channel"]}</td><td>{r["axis_id"]}</td><td>{r["feed_positive_net"]}</td><td>{r["nominal_feed_voltage"]}</td><td>{r["candidate_internal_cap_a"]}</td></tr>'
        for r in allocations
    )
    loss_html = "".join(
        f'<tr><td>{r["board_instance"]}</td><td>{r["populated_axis_count"]}</td><td>{r["arithmetic_cap_sum_a"]}</td><td>{r["simultaneous_pair_loss_typ_w"]}</td><td>{r["simultaneous_pair_loss_hot_max_w"]}</td></tr>'
        for r in board_losses
    )
    hold_html = "".join(f'<li><b>{r["hold_id"]}</b> {html.escape(str(r["unresolved_item"]))}</li>' for r in holds)
    rendered = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 walking-power successor</title><style>:root{{--deep:#071f3b;--blue:#0b5b9b;--sky:#d6f1ff;--gold:#f4bd21;--paper:#f6fbff;--ink:#122c45;--red:#9d3520;--line:#82c5e6}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.55 system-ui,Segoe UI,sans-serif}}header,main,footer{{padding:clamp(24px,5vw,64px) max(18px,calc((100vw - 1280px)/2))}}header,footer{{background:linear-gradient(135deg,var(--deep),var(--blue));color:white}}h1{{font-size:clamp(38px,6vw,72px);line-height:1.03;max-width:18ch}}h2{{font-size:clamp(28px,4vw,44px)}}h3{{font-size:22px}}.warning{{background:var(--gold);color:#17243a;border:3px solid #7b5600;padding:16px;font-weight:900}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:18px}}article,.panel,li{{background:white;border:2px solid var(--line);border-radius:16px;padding:19px}}.metric{{font-size:clamp(34px,5vw,55px);font-weight:900;color:var(--blue)}}.hold{{border-color:#bf6a56;background:#fff2ef}}.hold .metric,.bad{{color:var(--red)}}.scroll{{overflow:auto;border:2px solid var(--line);border-radius:16px;background:white}}object{{display:block;width:100%;min-width:900px}}table{{border-collapse:collapse;width:100%;min-width:1100px}}th,td{{padding:14px;text-align:left;border-bottom:1px solid var(--line);font-size:16px}}th{{background:var(--sky)}}a{{color:#075b9b;font-weight:800}}li{{margin:12px 0}}code{{font-size:16px}}@media(max-width:560px){{body{{font-size:16px}}}}</style></head><body><header><div class="warning">{html.escape(WARNING)}</div><p>HR-30 whole-body P0.1</p><h1>Eight feeds. No hidden cross-connections.</h1><p>Every actuator bus now owns one electrically separate board input and one regenerative sink boundary. Five 12 V RS domains and three regulated 9 V TTL domains remain isolated.</p></header><main><section class="grid"><article><div class="metric">25</div><p>whole-body axes bound to paired branch slots</p></article><article><div class="metric">50</div><p>candidate populated TPS259482L devices</p></article><article><div class="metric">8</div><p>one-bus board instances and independent feed domains</p></article><article class="hold"><div class="metric">8 open</div><p>feed-level brake/dump circuits still require measured sizing</p></article></section><section><h2>Why two devices are required</h2><div class="scroll"><object data="bidirectional-branch-schematic.svg" type="image/svg+xml" aria-label="Paired bidirectional eFuse architecture"></object></div><p>TI documents that TPS25948 can pass bidirectional steady-state current when RCBCTRL is low, but its overcurrent protection acts only from IN to OUT. The selected P0.1 candidate therefore places one device in each direction. This remains an engineering inference requiring TI application review and physical validation.</p></section><section><h2>Why the topology changed</h2><div class="panel"><p>The earlier five-instance grouping was rejected during whole-body reconciliation. A shared-input arm board would tie RS-LARM to RS-RARM. A shared-input distal board would tie TTL-LDIST, TTL-RDIST and TTL-HEAD together downstream of three independent 9 V regulators.</p><p>The corrected package instantiates one six-channel pattern for each of the eight authoritative buses. Empty positions are DNP and do not create another feed.</p></div></section><section><h2>Native KiCad and routed board</h2><div class="panel"><p><a href="{PROJECT}.kicad_pro">Open the native KiCad project</a> | <a href="{PROJECT}.kicad_pcb">open the routed PCB</a> | <a href="output/{PROJECT}-front.svg">front copper view</a> | <a href="validation/{PROJECT}-erc.rpt">ERC report</a> | <a href="validation/{PROJECT}-drc.rpt">DRC report</a>.</p><p>The project contains one boundary sheet, six channel-template sheets, the exact TI YWP0012A example land pattern and a routed {BOARD_W:.0f} x {BOARD_H:.0f} mm ten-layer candidate. ERC and DRC are 0/0 with zero unconnected pads. Production stackup, fabricator DFM, assembly yield, thermal rise and physical tests remain open.</p></div></section><section><h2>Eight board instances and 25 axes</h2><div class="scroll"><table><thead><tr><th>Board</th><th>Bus</th><th>Channel</th><th>Axis</th><th>Feed net</th><th>Nominal feed</th><th>Internal cap A</th></tr></thead><tbody>{alloc_html}</tbody></table></div></section><section><h2>Pair conduction-loss screen</h2><p>These values use the axis cap as if simultaneous and therefore bound silicon conduction loss only. They are not measured walking duty or a thermal release.</p><div class="scroll"><table><thead><tr><th>Board</th><th>Axes</th><th>Cap sum A</th><th>Pair loss typ W</th><th>Pair loss hot-max W</th></tr></thead><tbody>{loss_html}</tbody></table></div><p><a href="axis-pair-loss-screen.csv">Open all 25 axis calculations</a> | <a href="board-pair-loss-screen.csv">eight-board summary</a>.</p></section><section class="panel"><h2>The honest remaining blocker</h2><p>Each authoritative feed still needs its own measured, independently powered brake/dump circuit. No resistor, chopper, voltage threshold or energy rating is released.</p><p><a href="feed-brake-dump-boundary.csv">Open the eight feed obligations</a> | <a href="energy-flow-state-register.csv">eight power states</a> | <a href="architecture-option-register.csv">architecture decisions</a>.</p><h2>Open holds</h2><ul>{hold_html}</ul></section></main><footer>{html.escape(WARNING)}</footer></body></html>'''
    return rendered


def integrate_root(status: dict[str, object]) -> None:
    status_path = WHOLE / "package-status.json"
    root_status = json.loads(status_path.read_text(encoding="utf-8"))
    root_status.update({
        "walking_power_successor_package_present": True,
        "walking_power_successor_native_sheet_count": status["native_schematic_sheet_count"],
        "walking_power_successor_axis_count": status["allocated_axis_count"],
        "walking_power_successor_paired_device_count": status["populated_efuse_count"],
        "walking_power_bus_count": status["authoritative_bus_count"],
        "walking_power_board_instance_count": status["board_instance_count"],
        "walking_power_one_bus_per_board_instance": True,
        "walking_power_multi_bus_input_short_present": False,
        "walking_power_bidirectional_branch_architecture_defined": True,
        "walking_power_bidirectional_overcurrent_architecture_defined": True,
        "walking_power_reverse_energy_path_to_downstream_feed_defined": True,
        "walking_power_feed_brake_dump_selected": False,
        "walking_power_exact_ywp_land_pattern_present": True,
        "walking_power_pcb_routed": True,
        "walking_power_pcb_drc_accepted": True,
        "walking_power_pcb_unconnected_pads": 0,
        "walking_power_production_stackup_selected": False,
        "walking_power_thermal_validated": False,
        "walking_power_architecture_complete": False,
        "walking_power_connection_authority": False,
        "walking_power_motion_authority": False,
        "walking_power_energization_authority": False,
    })
    status_path.write_text(json.dumps(root_status, indent=2) + "\n", encoding="utf-8")
    readme = WHOLE / "README.md"; text = readme.read_text(encoding="utf-8")
    start, end = "<!-- HR30-WALKING-POWER-P01-README-START -->", "<!-- HR30-WALKING-POWER-P01-README-END -->"
    while start in text and end in text:
        text = text.split(start, 1)[0] + text.split(end, 1)[1]
    block = f'''{start}\n## Bidirectional walking-power successor\n\nThe [interactive walking-power guide](electrical/walking-power-successor-p0.1/index.html) replaces the single reverse-blocking branch for walking development with a native eight-sheet KiCad candidate containing two oppositely oriented TPS259482L devices per branch. One device protects motoring current and the other protects regenerative current. All 25 axes are allocated across eight electrically separate six-channel board instances, one per authoritative actuator bus; 23 positions remain DNP. The package now carries the exact TI YWP0012A example land pattern and a routed {BOARD_W:.0f} x {BOARD_H:.0f} mm ten-layer board candidate with ERC 0/0, DRC 0/0 and zero unconnected pads. Eight contactor-open brake/dump circuits, exact current thresholds, production stackup, DFM, thermal proof and every powered-work authority remain open.\n{end}\n'''
    marker = "<!-- HR30-PROTECTION-CONDUCTOR-P01-README-START -->"
    text = text.replace(marker, block + marker, 1) if marker in text else text.rstrip() + "\n\n" + block
    readme.write_text(text, encoding="utf-8", newline="\n")
    index = WHOLE / "index.html"; text = index.read_text(encoding="utf-8")
    start, end = "<!-- HR30-WALKING-POWER-P01-START -->", "<!-- HR30-WALKING-POWER-P01-END -->"
    while start in text and end in text:
        text = text.split(start, 1)[0] + text.split(end, 1)[1]
    section = f'''{start}<section id="walking-power-successor"><h2>Walking power now preserves all eight feed domains</h2><div class="grid"><article class="card pass"><div class="metric">25</div><p>axis-bound paired bidirectional branches.</p></article><article class="card pass"><div class="metric">8</div><p>electrically separate one-bus board instances.</p></article><article class="card pass"><h3>ERC / DRC 0 / 0</h3><p>Exact YWP land pattern and routed ten-layer board candidate.</p></article><article class="card hold"><div class="metric">8 open</div><p>bus-domain brake/dump circuits still require measured sizing.</p></article></div><p><a href="electrical/walking-power-successor-p0.1/index.html">Open the interactive walking-power successor</a>. The earlier five-board shared-input grouping is rejected; production stackup, DFM, thermal, dump-energy and powered-motion authority remain open.</p></section>{end}'''
    marker = "<!-- HR30-PROTECTION-CONDUCTOR-P01-START -->"
    text = text.replace(marker, section + marker, 1) if marker in text else text.replace("</main>", section + "</main>", 1)
    index.write_text(text, encoding="utf-8", newline="\n")


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    write_ywp_footprint_library()
    allocations = axis_allocations()
    axis_losses, board_losses = loss_rows(allocations)
    holds = open_holds()
    items = parts()
    write_schematic(items)
    board = write_board(items)
    validation = validate_kicad(board)
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
        "board_pattern_count": 1, "board_instance_count": 8, "channels_per_board": 6,
        "authoritative_bus_count": 8, "one_bus_per_board_instance": True,
        "multi_bus_input_short_present": False,
        "allocated_axis_count": 25, "dnp_spare_count": 23, "candidate_device": "TPS259482LYWPR",
        "populated_efuse_count": 50, "dnp_efuse_count": 46,
        "branch_topology_selected_as_p01_candidate": True,
        "single_device_bidirectional_branch_rejected": True,
        "bidirectional_power_flow_defined": True,
        "bidirectional_overcurrent_architecture_defined": True,
        "off_state_bidirectional_blocking_defined": True,
        "reverse_energy_path_to_downstream_feed_defined": True,
        "feed_brake_dump_obligation_count": 8,
        "feed_brake_dump_selected": False, "exact_current_thresholds_selected": False,
        "tps25948_pair_manufacturer_application_accepted": False,
        "exact_ywp_land_pattern_present": True,
        "exact_ywp_footprint_released": False,
        "pcb_layout_present": True,
        "pcb_routing_complete": True,
        "pcb_drc_accepted": True,
        "pcb_unconnected_pads": 0,
        "board_width_mm": BOARD_W,
        "board_height_mm": BOARD_H,
        "copper_layer_count": 10,
        "routing": board["routing"],
        "production_stackup_selected": False,
        "thermal_validated": False, "walking_power_architecture_complete": False,
        "functional_safety_credit": False, "procurement_authority": False, "fabrication_authority": False,
        "connection_authority": False, "powered_test_authority": False, "motion_authority": False,
        "energization_authority": False, "validation": validation,
    }
    (OUT / "walking-power-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    (OUT / "bidirectional-branch-schematic.svg").write_text(branch_svg(), encoding="utf-8", newline="\n")
    (OUT / "index.html").write_text(page(status, allocations, board_losses, holds), encoding="utf-8", newline="\n")
    (OUT / "README.md").write_text(f"# HR-30 walking-power successor P0.1\n\n**{WARNING}**\n\nThis package provides the native KiCad and web artifacts for a paired TPS259482L bidirectional actuator-branch candidate. One eFuse protects each current direction across every populated axis. The corrected topology uses eight electrically separate one-bus board instances and explicitly rejects the earlier five-board grouping that would have cross-connected independent feeds. The package now contains the exact TI YWP0012A example land pattern and a routed {BOARD_W:.0f} x {BOARD_H:.0f} mm ten-layer board candidate with ERC 0/0, DRC 0/0 and zero unconnected pads. Eight downstream contactor-open brake/dump circuits, exact settings, production stackup, DFM, thermal evidence and all powered-work authority remain open.\n", encoding="utf-8", newline="\n")
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
    print(f"generated {OUT.relative_to(ROOT)}: 25 axes, 50 populated eFuses, exact YWP, routed PCB, ERC/DRC 0/0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
