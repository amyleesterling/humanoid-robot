#!/usr/bin/env python3
"""Generate the HR-30 source-local diagnostic pickoff pod package P0.1.

Eight identical one-channel pods place two 100 kOhm series elements in each
measurement lead before the long cable to the floating measurement panel.
The pods are test equipment, not safety devices.  Device-specific source-tap
hardware remains open and no connection or energization authority follows.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import importlib.util
import json
import math
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WHOLE = ROOT / "hr30" / "whole-body-p0.1"
OUT = WHOLE / "electrical" / "diagnostic-pickoff-pods-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / "electrical" / OUT.name
PANEL = WHOLE / "electrical" / "measurement-boundary-panel-p0.1"
HARNESS = WHOLE / "first-energization-measurement-harness-p0.1"
TETHER = WHOLE / "electrical" / "tether-power-core-p0.1"
WHOLE_ECAD = WHOLE / "electrical" / "kicad" / "hr30-whole-body-electrical-p0.1"
PROJECT = "hr30-diagnostic-pickoff-pod-p0.1"
IDENTIFIER = "HR30-DIAGNOSTIC-PICKOFF-PODS-P0.1"
DATE = "2026-08-19"
WARNING = "PRELIMINARY - UNBUILT SOURCE-LOCAL DIAGNOSTIC PICKOFF PODS - ZERO SAFETY CREDIT - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, WALKING OR ENERGIZATION"
AUTHORITY = "NO PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED-TEST, MOTION, WALKING OR ENERGIZATION AUTHORITY"
KICAD = Path(r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe")
KICAD_PYTHON = Path(r"C:\Program Files\KiCad\10.0\bin\python.exe")
CAD_PYTHON = ROOT.parent / ".venvs" / "hr-v0-cad" / "Scripts" / "python.exe"
FP_ROOT = Path(r"C:\Program Files\KiCad\10.0\share\kicad\footprints")

PHOENIX_HEADER = "Connector_Phoenix_MSTB:PhoenixContact_MSTBA_2,5_2-G-5,08_1x02_P5.08mm_Horizontal"
PHOENIX_HEADER_URL = "https://www.phoenixcontact.com/en-us/products/pcb-header-mstba-25-2-g-508-1757242"
PHOENIX_PLUG_URL = "https://www.phoenixcontact.com/en-us/products/pcb-connector-mstb-25-2-st-508-1757019"
VISHAY_URL = "https://www.vishay.com/docs/28758/tnpw_e3.pdf"
HAMMOND_URL = "https://www.hammfg.com/pdf/1551kfl.pdf"
ALPHA_URL = "https://www.alphawire.com/products/cable/alpha-essentials/tray-cable/5610b2201"

R_PICKOFF_EACH_OHM = 100_000.0
R_PICKOFF_PER_LEAD_OHM = 2 * R_PICKOFF_EACH_OHM
R_PANEL_PER_LEAD_OHM = 10_200.0
R_NI_INPUT_OHM = 1_000_000.0
R_TOTAL_OHM = R_NI_INPUT_OHM + 2 * (R_PICKOFF_PER_LEAD_OHM + R_PANEL_PER_LEAD_OHM)
NOMINAL_RATIO = R_NI_INPUT_OHM / R_TOTAL_OHM
NOMINAL_CORRECTION = 1.0 / NOMINAL_RATIO

CHANNELS = [
    {"channel_id":"CH-AI-01","pod_id":"DP-01","signal":"ACT_MAIN_SOURCE_12V","planning_v":12.0,"hi_net":"RAW_12V_POS","lo_net":"RAW_0V","sheet":"01_external_source_panel.kicad_sch","hi_terminal":"PS1:+V","lo_terminal":"PS1:-V","location":"external source enclosure; adjacent to PS1 output terminals","tap_boundary":"PS1 terminal accessory / approved parallel-conductor method SELECTION REQUIRED"},
    {"channel_id":"CH-AI-02","pod_id":"DP-02","signal":"ACT_MAIN_SAFE_12V","planning_v":12.0,"hi_net":"TETHER_POS_SWITCHED","lo_net":"RAW_0V","sheet":"04_touch_safe_tether.kicad_sch","hi_terminal":"XT1A:P1","lo_terminal":"XT1A:P2","location":"pelvis rear tether inlet; adjacent to XT1A","tap_boundary":"dedicated sense breakout around high-current XT1A path SELECTION REQUIRED; no second conductor may be inferred at SBS contact"},
    {"channel_id":"CH-AI-03","pod_id":"DP-03","signal":"TTL_LDIST_SAFE_9V","planning_v":9.0,"hi_net":"TTL_LDIST_SAFE_9V","lo_net":"ACT_0V_CONTROLLED","sheet":"01_energy_precharge_conversion.kicad_sch","hi_terminal":"REG_TTL_L:LOG-OUT","lo_terminal":"REG_TTL_L:LOG-RET-OUT","location":"pelvis power tray; adjacent to left-distal regulator output","tap_boundary":"physical regulator output terminal/test connector SELECTION REQUIRED"},
    {"channel_id":"CH-AI-04","pod_id":"DP-04","signal":"CTRL_5V","planning_v":5.0,"hi_net":"CTRL_5V","lo_net":"CTRL_GND","sheet":"04_motion_controller_carrier_connectors.kicad_sch","hi_terminal":"REG1:LOG-5V","lo_terminal":"REG1:LOG-GND","location":"torso rear electronics tray; adjacent to motion-controller 5 V regulator","tap_boundary":"dedicated protected controller test connector is not present; board revision / tap implementation SELECTION REQUIRED"},
    {"channel_id":"CH-AI-05","pod_id":"DP-05","signal":"ESTOP_CH_A_24V","planning_v":24.0,"hi_net":"S12_CH1","lo_net":"SAFE_0V","sheet":"02_estop_reset_safety_relay.kicad_sch","hi_terminal":"SR1:S12","lo_terminal":"SR1:A2","location":"external safety enclosure; adjacent to SR1","tap_boundary":"Pilz terminal parallel-conductor/accessory acceptance and safety-input loading review REQUIRED"},
    {"channel_id":"CH-AI-06","pod_id":"DP-06","signal":"HARDWIRED_PERMIT_24V","planning_v":24.0,"hi_net":"HARDWIRED_PERMIT","lo_net":"SAFE_0V","sheet":"02_estop_reset_safety_relay.kicad_sch","hi_terminal":"SR1:34","lo_terminal":"SR1:A2","location":"external safety enclosure; adjacent to SR1","tap_boundary":"Pilz terminal parallel-conductor/accessory acceptance and no-bypass fault review REQUIRED"},
    {"channel_id":"CH-AI-07","pod_id":"DP-07","signal":"K1_COIL_24V","planning_v":24.0,"hi_net":"K1_COIL_POS","lo_net":"SAFE_0V","sheet":"03_redundant_dc_interruption.kicad_sch","hi_terminal":"K1:A1","lo_terminal":"K1:A2","location":"external contactor enclosure; adjacent to K1 coil terminals","tap_boundary":"Schneider coil-terminal accessory / approved parallel-conductor method SELECTION REQUIRED"},
    {"channel_id":"CH-AI-08","pod_id":"DP-08","signal":"K2_COIL_24V","planning_v":24.0,"hi_net":"K2_COIL_POS","lo_net":"SAFE_0V","sheet":"03_redundant_dc_interruption.kicad_sch","hi_terminal":"K2:A1","lo_terminal":"K2:A2","location":"external contactor enclosure; adjacent to K2 coil terminals","tap_boundary":"Schneider coil-terminal accessory / approved parallel-conductor method SELECTION REQUIRED"},
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"empty register: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def run(command: list[str], cwd: Path = ROOT, allowed: tuple[int, ...] = (0,)) -> subprocess.CompletedProcess[str]:
    cp = subprocess.run(command, cwd=cwd, text=True, capture_output=True)
    if cp.returncode not in allowed:
        raise RuntimeError(f"command failed {cp.returncode}: {' '.join(command)}\n{cp.stdout}\n{cp.stderr}")
    return cp


def load_model():
    path = ROOT / "tools" / "generate_hr_v0_electrical_v3.py"
    spec = importlib.util.spec_from_file_location("hr30_pickoff_model", path)
    if not spec or not spec.loader:
        raise RuntimeError("cannot load schematic model")
    model = importlib.util.module_from_spec(spec); sys.modules[spec.name] = model; spec.loader.exec_module(model)
    model.OUT = OUT; model.PROJECT = PROJECT; model.REV = "P0.1"; model.DATE = DATE; model.WARNING = WARNING
    model.PROJECT_TITLE = "PROJECT BUTTON HR-30 DIAGNOSTIC PICKOFF POD"
    model.PROJECT_SUBTITLE = "One floating source-local measurement lane; two 100 kOhm series elements in each lead; zero safety credit."
    return model


def write_schematic() -> None:
    model = load_model()
    parts = [
        ("JIN", "source-local input", "Phoenix Contact 1757242", {"1":"SRC_HI","2":"SRC_LO"}, (55,90), PHOENIX_HEADER),
        ("RHA", "100 kOhm 0.1%", "Vishay TNPW1206100KBEEA", {"1":"SRC_HI","2":"HI_MID"}, (145,70), "Resistor_SMD:R_1206_3216Metric"),
        ("RHB", "100 kOhm 0.1%", "Vishay TNPW1206100KBEEA", {"1":"HI_MID","2":"OUT_HI"}, (235,70), "Resistor_SMD:R_1206_3216Metric"),
        ("RLA", "100 kOhm 0.1%", "Vishay TNPW1206100KBEEA", {"1":"SRC_LO","2":"LO_MID"}, (145,120), "Resistor_SMD:R_1206_3216Metric"),
        ("RLB", "100 kOhm 0.1%", "Vishay TNPW1206100KBEEA", {"1":"LO_MID","2":"OUT_LO"}, (235,120), "Resistor_SMD:R_1206_3216Metric"),
        ("JOUT", "current-limited output to measurement panel", "Phoenix Contact 1757242", {"1":"OUT_HI","2":"OUT_LO"}, (335,90), PHOENIX_HEADER),
    ]
    sheet = model.Sheet(1, "01_source_local_pickoff.kicad_sch", "Source-local floating diagnostic pickoff", "Eight separately labeled assemblies use this same one-channel circuit.")
    components = []
    for ref, value, mpn, pins, position, footprint in parts:
        source = PHOENIX_HEADER_URL if ref.startswith("J") else VISHAY_URL
        pns = [model.pn(ref, number, "HI / +" if number == "1" else "LO / -", net, "left" if number == "1" else "right") for number, net in pins.items()]
        components.append(model.Component(ref, value, pns, "EXACT COMPONENT CANDIDATE; APPLICATION OPEN", "TEST EQUIPMENT ONLY; ZERO SAFETY CREDIT", source, f"{mpn}; receiving and application validation open", position=position, width=62, footprint=footprint))
    sheet.components = components
    sheet.notes = [
        "Install one pod per measured node within a guarded enclosure and within 100 mm maximum conductor path of the approved source tap.",
        "Each lead has two physically separate 100 kOhm resistors before JOUT. A single resistor short still leaves 100 kOhm in that lead.",
        "The short lead between the source terminal and first resistor remains an uncontrolled fault boundary until the exact device tap, routing and retention are approved.",
        "No pod conductor is joined to another channel, chassis, PE, USB ground or synchronization slate.", WARNING,
    ]
    sheets = [sheet]
    net_counts: dict[str, int] = {}
    for component in components:
        for pin in component.pins:
            net_counts[pin.net] = net_counts.get(pin.net, 0) + 1
    wires = model.build_wire_numbers(sheets, net_counts)
    root_uuid = model.uid("root-hr30-diagnostic-pickoff-pod-p0.1")
    project = {"board":{},"boards":[],"cvpcb":{},"erc":{},"libraries":{},"meta":{"filename":f"{PROJECT}.kicad_pro","version":1},"net_settings":{"classes":[],"meta":{"version":3}},"pcbnew":{},"schematic":{},"text_variables":{"PROJECT_STATUS":WARNING}}
    (OUT / f"{PROJECT}.kicad_pro").write_text(json.dumps(project, indent=2) + "\n", encoding="utf-8")
    symbols = [model.lib_symbol(c).replace(f'(symbol "PBV3:{c.ref}"', f'(symbol "{c.ref}"', 1) for c in components]
    (OUT / f"{PROJECT}.kicad_sym").write_text('(kicad_symbol_lib\n  (version 20251024) (generator "kicad_symbol_editor") (generator_version "10.0")\n  ' + "\n".join(symbols) + '\n)\n', encoding="utf-8")
    (OUT / "sym-lib-table").write_text(f'(sym_lib_table\n  (version 7)\n  (lib (name "PBV3")(type "KiCad")(uri "${{KIPRJMOD}}/{PROJECT}.kicad_sym")(options "")(descr "HR-30 diagnostic-pickoff symbols"))\n)\n', encoding="utf-8")
    (OUT / f"{PROJECT}.kicad_sch").write_text(model.root_schematic(root_uuid, sheets), encoding="utf-8")
    (OUT / sheet.filename).write_text(model.child_schematic(root_uuid, sheet, net_counts, wires), encoding="utf-8")


def pcb_mode() -> int:
    import pcbnew
    def footprint(identifier: str):
        library, name = identifier.split(":", 1)
        fp = pcbnew.FootprintLoad(str(FP_ROOT / f"{library}.pretty"), name)
        if fp is None: raise RuntimeError(f"cannot load footprint {identifier}")
        return fp
    def pads(fp, number: str):
        return [p for p in fp.Pads() if p.GetNumber() == number]
    def xy(pad):
        p = pad.GetPosition(); return pcbnew.ToMM(p.x), pcbnew.ToMM(p.y)
    def track(board, net, a, b, width=.30):
        item = pcbnew.PCB_TRACK(board); item.SetStart(pcbnew.VECTOR2I_MM(*a)); item.SetEnd(pcbnew.VECTOR2I_MM(*b)); item.SetLayer(pcbnew.F_Cu); item.SetWidth(pcbnew.FromMM(width)); item.SetNet(net); board.Add(item)
    board = pcbnew.BOARD(); board.SetCopperLayerCount(2)
    settings = board.GetDesignSettings(); settings.SetBoardThickness(pcbnew.FromMM(1.6)); settings.m_MinClearance = pcbnew.FromMM(.20); settings.m_TrackMinWidth = pcbnew.FromMM(.20); settings.m_HoleClearance = pcbnew.FromMM(.25); settings.m_HoleToHoleMin = pcbnew.FromMM(.30); settings.m_NetSettings.GetDefaultNetclass().SetClearance(pcbnew.FromMM(.20))
    names = ["SRC_HI","SRC_LO","HI_MID","LO_MID","OUT_HI","OUT_LO"]
    nets = {}
    for name in names:
        net = pcbnew.NETINFO_ITEM(board, name); board.Add(net); nets[name] = net
    placements = [
        ("JIN", PHOENIX_HEADER, 15.0, 17.0, 90, {"1":"SRC_HI","2":"SRC_LO"}),
        ("RHA", "Resistor_SMD:R_1206_3216Metric", 29.0, 22.08, 0, {"1":"SRC_HI","2":"HI_MID"}),
        ("RHB", "Resistor_SMD:R_1206_3216Metric", 45.0, 22.08, 0, {"1":"HI_MID","2":"OUT_HI"}),
        ("RLA", "Resistor_SMD:R_1206_3216Metric", 29.0, 11.92, 0, {"1":"SRC_LO","2":"LO_MID"}),
        ("RLB", "Resistor_SMD:R_1206_3216Metric", 45.0, 11.92, 0, {"1":"LO_MID","2":"OUT_LO"}),
        ("JOUT", PHOENIX_HEADER, 55.0, 17.0, 90, {"1":"OUT_HI","2":"OUT_LO"}),
    ]
    fps = {}
    for ref, lib, x, y, angle, pinmap in placements:
        fp = footprint(lib); fp.SetReference(ref); fp.SetValue("TNPW1206100KBEEA" if ref.startswith("R") else "1757242"); fp.SetPosition(pcbnew.VECTOR2I_MM(x, y)); fp.SetOrientationDegrees(angle); fp.Reference().SetVisible(False); fp.Value().SetVisible(False)
        for number, name in pinmap.items():
            for pad in pads(fp, number): pad.SetNet(nets[name])
        board.Add(fp); fps[ref] = fp
    for index, (x, y) in enumerate(((5.25,5.53),(68.75,5.53),(5.25,28.47),(68.75,28.47)), 1):
        hole = footprint("MountingHole:MountingHole_3.5mm"); hole.SetReference(f"H{index}"); hole.SetValue("HAMMOND 1551KFL STANDOFF CANDIDATE"); hole.SetPosition(pcbnew.VECTOR2I_MM(x,y)); hole.SetBoardOnly(True); hole.SetExcludedFromBOM(True); hole.SetExcludedFromPosFiles(True); hole.Reference().SetVisible(False); hole.Value().SetVisible(False); board.Add(hole)
    corners = ((0,0),(74,0),(74,34),(0,34))
    for a, b in zip(corners, (*corners[1:], corners[0])):
        edge = pcbnew.PCB_SHAPE(board); edge.SetShape(pcbnew.SHAPE_T_SEGMENT); edge.SetStart(pcbnew.VECTOR2I_MM(*a)); edge.SetEnd(pcbnew.VECTOR2I_MM(*b)); edge.SetLayer(pcbnew.Edge_Cuts); edge.SetWidth(pcbnew.FromMM(.20)); board.Add(edge)
    by_net: dict[str, list[tuple[float,float]]] = {name: [] for name in names}
    for ref, _, _, _, _, pinmap in placements:
        for number, name in pinmap.items(): by_net[name].append(xy(pads(fps[ref], number)[0]))
    for name, endpoints in by_net.items():
        if len(endpoints) != 2: raise RuntimeError(f"{name} endpoint count {len(endpoints)}")
        track(board, nets[name], endpoints[0], endpoints[1], .34)
    for value, x, y, size in (("SOURCE",15.0,32.0,.9),("LIMITED OUT",55.0,32.0,.9),("2 x 100K / LEAD",37.0,2.0,.9),("NO SAFETY CREDIT",37.0,17.0,.9)):
        text = pcbnew.PCB_TEXT(board); text.SetText(value); text.SetPosition(pcbnew.VECTOR2I_MM(x,y)); text.SetLayer(pcbnew.F_SilkS); text.SetTextSize(pcbnew.VECTOR2I_MM(size,size)); text.SetTextThickness(pcbnew.FromMM(.15)); board.Add(text)
    board_dir = OUT / "board"; board_dir.mkdir(parents=True, exist_ok=True)
    pcbnew.SaveBoard(str(board_dir / f"{PROJECT}.kicad_pcb"), board)
    print("generated one-channel source-local pickoff board")
    return 0


def source_rows() -> list[dict[str, object]]:
    return [{**row, "source_tail_max_mm":100, "source_tail_state":"EXACT LENGTH/TERMINATION NOT RELEASED", "pod_input":"JIN.1 HI / JIN.2 LO", "pod_output":"JOUT.1 HI / JOUT.2 LO", "panel_input":f"J{index}I.1 HI / J{index}I.2 LO", "connection_released":"NO", "warning":WARNING} for index, row in enumerate(CHANNELS, 1)]


def pod_rows() -> list[dict[str, object]]:
    return [{"pod_id":r["pod_id"],"channel_id":r["channel_id"],"signal":r["signal"],"pcb":f"{PROJECT}.kicad_pcb","pcb_mm":"74 x 34 x 1.6","enclosure":"Hammond 1551KFLBK; 80 x 40 x 20 mm box; flanged lid","location":r["location"],"source_tail_max_mm":100,"output_cable_finished_mm":3000,"physical_state":"UNBUILT; INSTALLATION/FAI OPEN","authority":AUTHORITY,"warning":WARNING} for r in CHANNELS]


def contact_rows() -> list[dict[str, object]]:
    rows = []
    for index, channel in enumerate(CHANNELS, 1):
        for connector, side, contact, polarity, net, endpoint in [
            ("JIN","SOURCE INPUT",1,"HI/+",channel["hi_net"],channel["hi_terminal"]),
            ("JIN","SOURCE INPUT",2,"LO/-",channel["lo_net"],channel["lo_terminal"]),
            ("JOUT","LIMITED OUTPUT",1,"HI/+",f"DP{index:02d}_LIMITED_HI",f"measurement panel J{index}I.1"),
            ("JOUT","LIMITED OUTPUT",2,"LO/-",f"DP{index:02d}_LIMITED_LO",f"measurement panel J{index}I.2"),
        ]:
            rows.append({"pod_id":channel["pod_id"],"channel_id":channel["channel_id"],"connector":connector,"side":side,"contact":contact,"polarity":polarity,"net":net,"external_endpoint":endpoint,"header":"Phoenix 1757242","mating_plug":"Phoenix 1757019","termination":"22 AWG ferrule 3203066 at pod; source end SELECTION REQUIRED" if side == "SOURCE INPUT" else "22 AWG ferrule 3203066 both ends","connection_released":"NO","warning":WARNING})
    return rows


def resistor_rows() -> list[dict[str, object]]:
    rows = []
    for channel in CHANNELS:
        for ref, lead, ordinal in (("RHA","HI",1),("RHB","HI",2),("RLA","LO",1),("RLB","LO",2)):
            rows.append({"pod_id":channel["pod_id"],"channel_id":channel["channel_id"],"reference":ref,"lead":lead,"series_ordinal":ordinal,"manufacturer":"Vishay","order_code":"TNPW1206100KBEEA","resistance_ohm":100000,"tolerance_percent":0.1,"tcr_ppm_per_k":25,"operating_voltage_rating_v":200,"rated_dissipation_p70_w":0.52,"planning_24v_max_dissipation_each_w":f"{(24.0/R_TOTAL_OHM)**2*R_PICKOFF_EACH_OHM:.9f}","state":"EXACT CANDIDATE; RECEIVED LOT/ASSEMBLY OPEN","warning":WARNING})
    return rows


def cable_rows() -> list[dict[str, object]]:
    rows = []
    for index, channel in enumerate(CHANNELS, 1):
        rows.append({"cable_id":f"DP-TAIL-{index:02d}","channel_id":channel["channel_id"],"from":f"{channel['hi_terminal']} / {channel['lo_terminal']}","to":f"{channel['pod_id']} JIN.1 / JIN.2","cable":"Alpha Wire 5610B2201; one shielded 22 AWG pair","finished_length_mm":"INSTALL TO <=100 MM SOURCE-TO-FIRST-RESISTOR PATH","cut_length_mm":"SELECTION REQUIRED AFTER SOURCE-TAP DESIGN","connector_from":"SELECTION REQUIRED","connector_to":"Phoenix 1757019","shield":"cut back and individually insulated both ends","state":"SOURCE TERMINATION/LENGTH OPEN","warning":WARNING})
        rows.append({"cable_id":f"DP-PANEL-{index:02d}","channel_id":channel["channel_id"],"from":f"{channel['pod_id']} JOUT.1 / JOUT.2","to":f"measurement panel J{index}I.1 / J{index}I.2","cable":"Alpha Wire 5610B2201; one shielded 22 AWG pair","finished_length_mm":3000,"cut_length_mm":3100,"connector_from":"Phoenix 1757019","connector_to":"Phoenix 1757019 allocated by measurement-panel BOM","shield":"cut back and individually insulated both ends","state":"EXACT CANDIDATE; ROUTE/BUILD/NOISE VALIDATION OPEN","warning":WARNING})
    return rows


def scale_rows() -> list[dict[str, object]]:
    rows = []
    for channel in CHANNELS:
        v = channel["planning_v"]
        rows.append({"channel_id":channel["channel_id"],"signal":channel["signal"],"planning_source_v_not_limit":f"{v:.3f}","pickoff_series_each_lead_ohm":f"{R_PICKOFF_PER_LEAD_OHM:.0f}","panel_series_each_lead_ohm":f"{R_PANEL_PER_LEAD_OHM:.0f}","nominal_ni_differential_input_ohm":f"{R_NI_INPUT_OHM:.0f}","nominal_ni_over_source_ratio":f"{NOMINAL_RATIO:.9f}","nominal_scale_correction":f"{NOMINAL_CORRECTION:.6f}","planning_ni_reading_v":f"{v*NOMINAL_RATIO:.6f}","planning_source_loading_ua":f"{v/R_TOTAL_OHM*1e6:.6f}","calibration":"REQUIRED WITH COMPLETE AS-BUILT CHAIN","qualified_limit":"NO","warning":WARNING})
    return rows


def fault_rows() -> list[dict[str, object]]:
    tests = [
        ("DP-F01","JOUT HI-to-LO short at 24 V planning screen",f"limited by 400 kOhm source-local series path; {24/400000*1e6:.3f} uA ideal","PAPER SCREEN ONLY; PASS/FAIL NOT RELEASED"),
        ("DP-F02","one JOUT lead shorted to opposite source reference at 24 V",f"limited by 200 kOhm intact lead; {24/200000*1e6:.3f} uA ideal","PAPER SCREEN ONLY; PASS/FAIL NOT RELEASED"),
        ("DP-F03","one of two same-lead resistors short",f"remaining 100 kOhm limits ideal 24 V current to {24/100000*1e6:.3f} uA","SINGLE-FAULT INTENT; COMPONENT/PCB COMMON-CAUSE REVIEW OPEN"),
        ("DP-F04","one series resistor open","channel becomes invalid/high impedance; acquisition must flag implausible or missing signal","DETECTION/PROCEDURE OPEN"),
        ("DP-F05","both same-lead resistors short","dual/common-cause fault removes source-local limiting on that lead","UNCONTROLLED; QUALIFIED FAULT REVIEW REQUIRED"),
        ("DP-F06","source tail shorts before first resistor","fault is upstream of pod protection and may stress the measured circuit","BLOCKER: exact <=100 mm guarded route, tap accessory, retention and source protection review"),
        ("DP-F07","pod input/output reversed","long cable would be upstream of limiting resistors","BLOCKER: keyed labels, point-to-point inspection and connector-orientation control"),
        ("DP-F08","cross-channel cable short","each affected conductor remains behind its own two-resistor path if pods are correctly installed","PHYSICAL SEPARATION/BUILD TEST OPEN"),
        ("DP-F09","safety-circuit measurement loading",f"nominal 24 V source loading {24/R_TOTAL_OHM*1e6:.3f} uA through complete chain","PILZ APPLICATION/DIAGNOSTIC EFFECT AND QUALIFIED REVIEW OPEN"),
        ("DP-F10","pod enclosure or cable damage","ABS enclosure is not a safety-rated guard; exposed conductors or swapped cables possible","GUARDED CABINET LOCATION/STRAIN RELIEF/INSPECTION OPEN"),
    ]
    return [{"fault_id":a,"fault":b,"calculated_or_intended_response":c,"disposition":d,"safety_credit":"NONE","authority":AUTHORITY,"warning":WARNING} for a,b,c,d in tests]


def bom_rows() -> list[dict[str, object]]:
    return [
        {"item":"one-channel diagnostic pickoff PCB","manufacturer":"SELECTION REQUIRED","order_code":"SELECTION REQUIRED","quantity":8,"basis":"74 x 34 x 1.6 mm two-layer native KiCad candidate","selection_state":"FABRICATOR/STACKUP/FINISH/DFM OPEN","procurement_released":"NO","warning":WARNING},
        {"item":"100 kOhm 0.1% 25 ppm/K 1206 resistor","manufacturer":"Vishay","order_code":"TNPW1206100KBEEA","quantity":32,"basis":"four per pod; two in series per lead","selection_state":"EXACT CANDIDATE; RECEIVED LOT OPEN","procurement_released":"NO","warning":WARNING},
        {"item":"2-position 5.08 mm horizontal PCB header","manufacturer":"Phoenix Contact","order_code":"1757242","quantity":16,"basis":"JIN/JOUT on eight pods","selection_state":"EXACT CANDIDATE","procurement_released":"NO","warning":WARNING},
        {"item":"2-position 5.08 mm screw plug","manufacturer":"Phoenix Contact","order_code":"1757019","quantity":16,"basis":"source-tail pod end and pod-to-panel output end; panel-input plugs allocated separately","selection_state":"EXACT CANDIDATE; TERMINATION PROCESS OPEN","procurement_released":"NO","warning":WARNING},
        {"item":"flanged ABS enclosure 80 x 40 x 20 mm","manufacturer":"Hammond Manufacturing","order_code":"1551KFLBK","quantity":8,"basis":"one enclosure per source-local pod","selection_state":"EXACT ENVELOPE CANDIDATE; CUTOUT/FAI/ENVIRONMENT OPEN","procurement_released":"NO","warning":WARNING},
        {"item":"#2 x 3/16 PCB mounting screws","manufacturer":"Hammond Manufacturing","order_code":"1551ATS100","quantity":1,"basis":"one 100-piece pack; four screws per pod","selection_state":"EXACT ACCESSORY CANDIDATE; FAI/TORQUE OPEN","procurement_released":"NO","warning":WARNING},
        {"item":"one-pair shielded 22 AWG cable","manufacturer":"Alpha Wire","order_code":"5610B2201","quantity":"25 m minimum for eight 3.1 m cuts plus source tails","basis":"pod-to-panel and short source-tail candidates","selection_state":"EXACT CABLE FAMILY; ROUTE/BUILD/NOISE OPEN","procurement_released":"NO","warning":WARNING},
        {"item":"0.34 mm2 / 22 AWG 8 mm ferrule","manufacturer":"Phoenix Contact","order_code":"3203066","quantity":48,"basis":"32 pod-to-panel conductor ends plus 16 source-tail pod ends","selection_state":"EXACT CANDIDATE; CRIMP PROCESS OPEN","procurement_released":"NO","warning":WARNING},
        {"item":"source-device terminal tap/accessory","manufacturer":"SELECTION REQUIRED","order_code":"SELECTION REQUIRED","quantity":16,"basis":"HI and LO source boundary for eight pods","selection_state":"BLOCKING SELECTION; DEVICE-SPECIFIC","procurement_released":"NO","warning":WARNING},
    ]


def primary_sources() -> list[dict[str, object]]:
    return [
        {"source_id":"DP-S01","manufacturer":"Vishay","document":"TNPW e3 high stability thin film flat chip resistors","revision_or_date":"Revision 10-Apr-2026; Document 28758; accessed 2026-08-19","url":VISHAY_URL,"verified_scope":"TNPW1206 1 Ohm-2 MOhm; 0.52 W P70; 200 V operating; ordering grammar for TNPW1206100KBEEA","warning":WARNING},
        {"source_id":"DP-S02","manufacturer":"Phoenix Contact","document":"MSTBA 2,5/2-G-5,08 PCB header 1757242","revision_or_date":"live official page; accessed 2026-08-19; page revision not stated","url":PHOENIX_HEADER_URL,"verified_scope":"exact header identity and mating family","warning":WARNING},
        {"source_id":"DP-S03","manufacturer":"Phoenix Contact","document":"MSTB 2,5/2-ST-5,08 PCB connector 1757019","revision_or_date":"live official page; accessed 2026-08-19; page revision not stated","url":PHOENIX_PLUG_URL,"verified_scope":"24-12 AWG; flexible conductor with ferrule 0.25-2.5 mm2; 7 mm strip; 0.5-0.6 N m; do not mate under load","warning":WARNING},
        {"source_id":"DP-S04","manufacturer":"Hammond Manufacturing","document":"1551KFL enclosure drawing","revision_or_date":"REV 31.08.2023; accessed 2026-08-19","url":HAMMOND_URL,"verified_scope":"1551KFLBK identity; 80 x 40 x 20 mm box; maximum PCB 74 x 34 mm; 63.50 x 22.94 mm standoff spacing; 1551ATS100 accessory","warning":WARNING},
        {"source_id":"DP-S05","manufacturer":"Alpha Wire","document":"5610B2201 official product record","revision_or_date":"live official record; accessed 2026-08-19; page revision not stated","url":ALPHA_URL,"verified_scope":"one shielded 22 AWG twisted pair; 105 C; 300 Vrms; bend radius 10x cable diameter","warning":WARNING},
        {"source_id":"DP-S06","manufacturer":"NI","document":"NI-9229 datasheet","revision_or_date":"374184C-02; accessed 2026-08-19","url":"https://download.ni.com/support/manuals/374184c_02.pdf","verified_scope":"nominal 1 MOhm differential input and +/-60 V range used only for paper scaling; as-built calibration required","warning":WARNING},
    ]


def inspection_rows() -> list[dict[str, object]]:
    tests = [
        ("DP-T01","Incoming identity","Record PCB revision, resistor lot/marking, connectors, enclosure, cable and ferrules against exact candidates."),
        ("DP-T02","Resistor measurement","Measure all 32 resistors before assembly and record each value; reject mismatch or mixed reels."),
        ("DP-T03","PCB inspection","AOI/visual and dimensional FAI; verify each lead contains two separate series footprints and no copper bypass."),
        ("DP-T04","Enclosure FAI","Verify board/standoffs, cutout clearance, lid closure, labels, strain relief and no exposed conductive parts."),
        ("DP-T05","Unpowered resistance","For each pod, measure JIN.1-JOUT.1 and JIN.2-JOUT.2; each must equal two series resistors within defined measurement uncertainty."),
        ("DP-T06","Isolation","Every pod lane remains open to enclosure, other pods, shield/drain, PE and synchronization slate at the approved test threshold."),
        ("DP-T07","Source-tail control","Qualified reviewer verifies exact source accessory, <=100 mm source-to-first-resistor path, abrasion protection, restraint and no protection/safety bypass."),
        ("DP-T08","Cable point-to-point","Verify DP-01..08 JOUT polarity to measurement-panel J1I..J8I; reversed input/output or channel identity is rejectable."),
        ("DP-T09","Low-voltage transfer","With source hardware absent, inject traceable low voltage and verify end-to-end ratio/polarity at the NI terminals."),
        ("DP-T10","Nominal transfer/calibration","Calibrate each complete pod+cables+panel+NI channel at relevant voltages; retain gain, offset, noise and crosstalk evidence."),
        ("DP-T11","Fault injection","Guarded test of output shorts, one resistor open/short simulation and cross-channel faults; compare measured current and detection to approved limits."),
        ("DP-T12","Qualified disposition","Electrical and functional-safety reviewers accept source loading, terminal taps, fault behavior and stage-specific use before any connection."),
    ]
    return [{"test_id":a,"test":b,"acceptance":c,"result":"NOT EXECUTED","evidence":"REQUIRED","authority":AUTHORITY,"warning":WARNING} for a,b,c in tests]


def hold_rows() -> list[dict[str, object]]:
    holds = [
        ("DP-H01","device-specific source terminal taps","written manufacturer/application acceptance or engineered breakout for PS1, XT1A, both regulators, SR1 and K1/K2; exact conductors/ferrules/lugs/torques"),
        ("DP-H02","source-tail physical route","as-installed <=100 mm source-to-first-resistor path, guarding, segregation, abrasion protection and strain relief for all eight pods"),
        ("DP-H03","safety-circuit loading and fault review","Pilz/Schneider application review plus qualified analysis showing no masking, reset, permit or contactor-command effect"),
        ("DP-H04","PCB and enclosure DFM/FAI","fabricator stackup/finish, resistor spacing, Hammond standoff fit, connector cutouts, retention, labels and cabinet environmental suitability"),
        ("DP-H05","assembled pod and cable verification","all DP-T01 through DP-T11 results with calibrated equipment and retained evidence"),
        ("DP-H06","end-to-end calibration/uncertainty","complete source simulator + pod + 3 m cable + measurement panel + NI chain calibration and timing/noise/crosstalk uncertainty"),
        ("DP-H07","independent qualified review","electrical and functional-safety acceptance of exact as-built revision and stage-specific connection procedure"),
        ("DP-H08","FER-G11 closure","installed protected pickoffs, current calibration, dry rehearsal, signed stage limits and complete records"),
    ]
    return [{"hold_id":a,"item":b,"closure_evidence":c,"state":"OPEN","authority":AUTHORITY,"warning":WARNING} for a,b,c in holds]


def write_cad() -> None:
    import cadquery as cq
    from cadquery.occ_impl.exporters.assembly import exportAssembly, exportGLTF
    assembly = cq.Assembly(name="HR30_DIAGNOSTIC_PICKOFF_PODS")
    for index, channel in enumerate(CHANNELS):
        x = (index % 2) * 110.0; y = (index // 2) * 55.0
        base = cq.Workplane("XY").box(80,40,18).translate((x,y,9))
        lid = cq.Workplane("XY").box(96.3,40,2).translate((x,y,19))
        board = cq.Workplane("XY").box(74,34,1.6).translate((x,y,4.8))
        connector_a = cq.Workplane("XY").box(9,12,8).translate((x-22,y,8))
        connector_b = cq.Workplane("XY").box(9,12,8).translate((x+22,y,8))
        resistors = cq.Workplane("XY").box(3.2,1.6,0.8).translate((x-8,y-5.08,6.0))
        for rx, ry in ((8,-5.08),(-8,5.08),(8,5.08)):
            resistors = resistors.union(cq.Workplane("XY").box(3.2,1.6,0.8).translate((x+rx,y+ry,6.0)))
        assembly.add(base, name=f"{channel['pod_id']}_ENCLOSURE", color=cq.Color(0.05,0.12,0.25,0.35))
        assembly.add(lid, name=f"{channel['pod_id']}_FLANGED_LID", color=cq.Color(0.05,0.12,0.25,0.45))
        assembly.add(board, name=f"{channel['pod_id']}_PCB", color=cq.Color(0.05,0.45,0.22))
        assembly.add(connector_a, name=f"{channel['pod_id']}_JIN", color=cq.Color(0.18,0.55,0.25))
        assembly.add(connector_b, name=f"{channel['pod_id']}_JOUT", color=cq.Color(0.18,0.55,0.25))
        assembly.add(resistors, name=f"{channel['pod_id']}_RESISTORS", color=cq.Color(0.12,0.12,0.12))
    if not exportAssembly(assembly, str(OUT / "HR30_eight_source_local_pickoff_pods_candidate.step")):
        raise RuntimeError("STEP assembly export failed")
    if not exportGLTF(assembly, str(OUT / "HR30_eight_source_local_pickoff_pods_candidate.glb"), binary=True):
        raise RuntimeError("GLB assembly export failed")


def make_svg() -> None:
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="850" viewBox="0 0 1600 850">','<rect width="1600" height="850" fill="#f7fbff"/>','<style>text{font-family:system-ui,Segoe UI,sans-serif;fill:#0b1d35}.h{font-size:34px;font-weight:900}.t{font-size:17px;font-weight:800}.s{font-size:13px}.box{fill:#fff;stroke:#082d67;stroke-width:3}.pod{fill:#e4f6ff;stroke:#145ca8;stroke-width:3}.wire{stroke:#145ca8;stroke-width:4}.r{fill:#ffc83d;stroke:#6e4d00;stroke-width:2}.warn{fill:#ffc83d;stroke:#6e4d00;stroke-width:3}</style>','<text class="h" x="50" y="52">Eight source-local diagnostic pickoff pods</text>','<rect class="warn" x="50" y="72" width="1500" height="50" rx="8"/><text class="t" x="70" y="104">UNBUILT — SOURCE TAPS OPEN — ZERO SAFETY CREDIT — NO CONNECTION OR ENERGIZATION AUTHORITY</text>']
    for index, channel in enumerate(CHANNELS):
        y = 160 + index*78
        parts += [f'<rect class="box" x="50" y="{y-25}" width="315" height="58" rx="12"/><text class="t" x="68" y="{y}">{channel["pod_id"]} · {channel["signal"]}</text><text class="s" x="68" y="{y+22}">{channel["hi_terminal"]} / {channel["lo_terminal"]}</text>',f'<line class="wire" x1="365" y1="{y-8}" x2="475" y2="{y-8}"/><line class="wire" x1="365" y1="{y+12}" x2="475" y2="{y+12}"/>',f'<rect class="pod" x="475" y="{y-32}" width="520" height="66" rx="13"/><text class="t" x="495" y="{y-8}">{channel["pod_id"]} · 74 × 34 mm PCB</text>',f'<rect class="r" x="730" y="{y-22}" width="65" height="18"/><rect class="r" x="805" y="{y-22}" width="65" height="18"/><rect class="r" x="730" y="{y+8}" width="65" height="18"/><rect class="r" x="805" y="{y+8}" width="65" height="18"/><text class="s" x="735" y="{y-8}">100 kΩ</text><text class="s" x="810" y="{y-8}">100 kΩ</text><text class="s" x="735" y="{y+22}">100 kΩ</text><text class="s" x="810" y="{y+22}">100 kΩ</text><text class="s" x="890" y="{y+7}">1551KFLBK</text>',f'<line class="wire" x1="995" y1="{y-8}" x2="1210" y2="{y-8}"/><line class="wire" x1="995" y1="{y+12}" x2="1210" y2="{y+12}"/><rect class="box" x="1210" y="{y-25}" width="330" height="58" rx="12"/><text class="t" x="1230" y="{y}">3.0 m to panel J{index+1}I</text><text class="s" x="1230" y="{y+22}">separate floating 22 AWG pair</text>']
    parts += ['</svg>']
    (OUT / "source-local-pickoff-architecture.svg").write_text("\n".join(parts) + "\n", encoding="utf-8")


def table_html(filename: str, title: str) -> str:
    with (OUT / filename).open(encoding="utf-8", newline="") as handle: rows = list(csv.DictReader(handle))
    fields = list(rows[0]); head = "".join(f"<th>{html.escape(x.replace('_',' ').title())}</th>" for x in fields)
    body = "".join("<tr>" + "".join(f"<td>{html.escape(row[x])}</td>" for x in fields) + "</tr>" for row in rows)
    return f'<section><h2>{html.escape(title)}</h2><div class="table"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div></section>'


def make_html() -> None:
    tables = "".join([table_html("source-node-register.csv","Eight exact source nodes"),table_html("end-to-end-scale-register.csv","End-to-end loading and scale"),table_html("fault-boundary-register.csv","Fault boundary"),table_html("candidate-bom.csv","Candidate BOM"),table_html("inspection-test-register.csv","Build and test traveler"),table_html("open-holds.csv","Open before connection")])
    (OUT / "index.html").write_text(f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 diagnostic pickoff pods</title><script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/4.1.0/model-viewer.min.js"></script><style>:root{{--sky:#9ddcff;--blue:#082d67;--mid:#145ca8;--gold:#ffc83d;--ink:#0b1d35;--paper:#f7fbff;--line:#85bee4}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.55 system-ui,Segoe UI,sans-serif}}header{{padding:clamp(28px,6vw,72px);background:linear-gradient(135deg,var(--blue),var(--mid));color:#fff}}h1{{font-size:clamp(38px,6vw,70px);line-height:1.03}}main{{max-width:1500px;margin:auto;padding:clamp(18px,4vw,52px)}}.warning{{background:var(--gold);color:#221800;padding:16px;border:3px solid #6e4d00;font-weight:900}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:18px}}article{{background:#fff;border:2px solid var(--blue);border-radius:16px;padding:20px;box-shadow:6px 6px 0 var(--sky)}}.hold{{background:#fff3c8}}.metric{{font-size:clamp(32px,4vw,54px);font-weight:900;color:var(--blue)}}section{{margin:44px 0}}h2{{font-size:clamp(28px,3vw,42px);color:var(--blue)}}.diagram,.table,.viewer{{overflow:auto;background:#fff;border:2px solid var(--blue);border-radius:14px}}object{{display:block;width:100%;min-width:1100px;min-height:700px}}model-viewer{{width:100%;height:560px;background:radial-gradient(circle,#fff,#e4f6ff)}}table{{border-collapse:collapse;width:max-content;min-width:100%}}th,td{{padding:12px 14px;border-bottom:1px solid #a8c4e4;vertical-align:top;max-width:520px}}th{{position:sticky;top:0;background:var(--blue);color:#fff;font-size:14px;text-align:left}}td{{font-size:16px}}a{{color:#064e9d;font-weight:800}}@media(max-width:650px){{body{{font-size:16px}}th,td{{min-width:180px}}}}</style></head><body><header><div class="warning">{html.escape(WARNING)}</div><p>HR-30 / FER-G11 / robot-side measurement boundary</p><h1>The long measurement cables now begin behind source-local resistance.</h1><p>Eight one-channel pods keep every measured pair floating and place two 100 kΩ elements in each lead before the three-metre panel cable.</p></header><main><section class="grid"><article><div class="metric">8</div><h2>source-local pods</h2><p>One pod per exact HR-30 node avoids a shared remote box and its long unprotected tap conductors.</p></article><article><div class="metric">2 + 2</div><h2>resistors per pair</h2><p>Two separate 100 kΩ elements in HI and two in LO retain 100 kΩ after one resistor-short fault.</p></article><article><div class="metric">1.4204</div><h2>nominal correction</h2><p>Composite paper scale includes pod, measurement panel and nominal NI input. Every real channel still requires calibration.</p></article><article class="hold"><div class="metric">0</div><h2>authorized taps</h2><p>Device-specific terminal accessories and the short upstream tail remain blocking physical selections.</p></article></section><section><h2>Complete source-to-panel architecture</h2><div class="diagram"><object data="source-local-pickoff-architecture.svg" type="image/svg+xml" aria-label="Eight independent source-local measurement pods"></object></div></section><section><h2>Eight-pod packaging candidate</h2><div class="viewer"><model-viewer src="HR30_eight_source_local_pickoff_pods_candidate.glb" camera-controls auto-rotate shadow-intensity="1" alt="Eight source-local diagnostic pickoff pods"></model-viewer></div></section><section class="grid"><article><h2>What this fixes</h2><p>No three-metre cable is directly attached to a robot power or safety node. Each long conductor begins after two source-local resistors.</p></article><article><h2>What it cannot fix</h2><p>The short conductor from each source terminal to JIN is upstream of the resistors. Exact terminal hardware, route and retention must be accepted before connection.</p></article><article class="hold"><h2>No safety function</h2><p>The pods are diagnostic test equipment. They do not perform emergency stopping, power interruption or fault-tolerant monitoring.</p></article></section>{tables}<section><h2>Engineering files</h2><p><a href="{PROJECT}.kicad_pro">KiCad project</a> · <a href="board/{PROJECT}.kicad_pcb">KiCad PCB</a> · <a href="HR30_eight_source_local_pickoff_pods_candidate.step">STEP</a> · <a href="source-node-register.csv">source nodes</a> · <a href="connector-contact-map.csv">contacts</a> · <a href="source-to-panel-cable-register.csv">cables</a> · <a href="primary-source-register.csv">sources</a></p></section></main></body></html>''', encoding="utf-8")


def integrate() -> None:
    status_path = WHOLE / "package-status.json"; status = json.loads(status_path.read_text(encoding="utf-8"))
    status.update({"diagnostic_pickoff_pods_candidate_present":True,"diagnostic_pickoff_pod_count":8,"diagnostic_pickoff_series_elements_per_lead":2,"diagnostic_pickoff_long_cables_current_limited":True,"diagnostic_pickoff_source_terminal_taps_released":False,"diagnostic_pickoff_pods_built":False,"measurement_harness_robot_pickoffs_released":False,"fer_g11_closed":False,"connection_authority":False,"energization_authority":False})
    status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    start, end = "<!-- HR30-DIAGNOSTIC-PICKOFF-PODS-P01-START -->", "<!-- HR30-DIAGNOSTIC-PICKOFF-PODS-P01-END -->"
    readme = WHOLE / "README.md"; text = readme.read_text(encoding="utf-8")
    if start in text and end in text: text = text.split(start,1)[0] + text.split(end,1)[1]
    block = f'''{start}\n## Source-local diagnostic pickoff pods\n\nThe [interactive diagnostic-pickoff guide](electrical/{OUT.name}/index.html) defines **eight separate one-channel pods**, one per measured HR-30 node. Two 100 kOhm Vishay elements in each lead precede every long source-to-panel cable, with exact pod connectors, enclosure candidate, board source, contact map, paper fault screens and composite 1.4204 scale correction. Device-specific source-terminal accessories, the <=100 mm upstream tails, build/FAI/calibration and qualified no-bypass review remain open; no connection or energization authority follows.\n{end}\n'''
    readme.write_text(text.rstrip() + "\n\n" + block, encoding="utf-8")
    page = WHOLE / "index.html"; text = page.read_text(encoding="utf-8")
    if start in text and end in text: text = text.split(start,1)[0] + text.split(end,1)[1]
    section = f'''{start}<section id="diagnostic-pickoff-pods"><h2>Every measurement cable now starts behind a source-local pod</h2><div class="grid"><article class="card pass"><div class="metric">8</div><p>separate one-channel pods bind the eight exact whole-body measurement nodes.</p></article><article class="card pass"><h3>2 x 100 kΩ per lead</h3><p>A single resistor-short fault still leaves 100 kΩ before the long cable.</p></article><article class="card hold"><h3>Source taps remain open</h3><p>Device-specific terminal hardware and the short upstream tails still block connection and FER-G11.</p></article></div><p><a href="electrical/{OUT.name}/index.html">Open the interactive source-local pickoff guide</a>.</p></section>{end}'''
    page.write_text(text.replace("</main>", section + "</main>", 1), encoding="utf-8")


def write_package() -> None:
    if OUT.exists(): shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    write_schematic()
    run([str(KICAD_PYTHON), str(Path(__file__).resolve()), "--pcb"])
    validation = OUT / "validation"; validation.mkdir()
    run([str(KICAD), "sch", "erc", "--exit-code-violations", "--output", str(validation / f"{PROJECT}-erc.rpt"), str(OUT / f"{PROJECT}.kicad_sch")])
    run([str(KICAD), "pcb", "drc", "--exit-code-violations", "--output", str(validation / f"{PROJECT}-drc.rpt"), str(OUT / "board" / f"{PROJECT}.kicad_pcb")])
    output = OUT / "output"; output.mkdir()
    run([str(KICAD), "sch", "export", "svg", "--output", str(output), str(OUT / f"{PROJECT}.kicad_sch")])
    write_csv(OUT / "source-node-register.csv", source_rows())
    write_csv(OUT / "pod-assembly-register.csv", pod_rows())
    write_csv(OUT / "connector-contact-map.csv", contact_rows())
    write_csv(OUT / "resistor-register.csv", resistor_rows())
    write_csv(OUT / "source-to-panel-cable-register.csv", cable_rows())
    write_csv(OUT / "end-to-end-scale-register.csv", scale_rows())
    write_csv(OUT / "fault-boundary-register.csv", fault_rows())
    write_csv(OUT / "candidate-bom.csv", bom_rows())
    write_csv(OUT / "primary-source-register.csv", primary_sources())
    write_csv(OUT / "inspection-test-register.csv", inspection_rows())
    write_csv(OUT / "open-holds.csv", hold_rows())
    binding = {"identifier":IDENTIFIER,"date":DATE,"warning":WARNING,"measurement_harness_channels_sha256":sha(HARNESS / "channel-endpoint-register.csv"),"measurement_panel_channels_sha256":sha(PANEL / "channel-register.csv"),"tether_power_net_schedule_sha256":sha(TETHER / "net-schedule.csv"),"whole_body_net_schedule_sha256":sha(WHOLE_ECAD / "net-schedule.csv"),"scope":"SOURCE-LOCAL POD, DOWNSTREAM CABLE AND PAPER FAULT/SCALING CANDIDATE; DEVICE TERMINAL TAPS/BUILD/TEST/REVIEW OPEN"}
    (OUT / "source-binding.json").write_text(json.dumps(binding, indent=2) + "\n", encoding="utf-8")
    status = {"identifier":IDENTIFIER,"date":DATE,"warning":WARNING,"pod_count":8,"channel_count":8,"one_pod_per_channel":True,"series_resistors_per_lead":2,"series_resistance_per_lead_ohm":200000,"long_cable_upstream_of_resistors":False,"source_terminal_taps_selected":False,"source_tails_validated":False,"native_kicad_sheet_count":2,"erc_errors":0,"erc_warnings":0,"drc_violations":0,"pcb_built":False,"pods_built":False,"inspection_executed":False,"calibration_executed":False,"independent_qualified_review":False,"fer_g11_closed":False,"functional_safety_credit":False,"procurement_authority":False,"fabrication_authority":False,"assembly_authority":False,"connection_authority":False,"powered_test_authority":False,"motion_authority":False,"walking_authority":False,"energization_authority":False}
    (OUT / "pod-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    (OUT / "README.md").write_text(f'''# HR-30 source-local diagnostic pickoff pods P0.1\n\n**{WARNING}**\n\nEight identical one-channel pods place two 100 kOhm Vishay TNPW1206 resistors in each HI and LO lead before any three-metre cable reaches the floating measurement panel. Each exact HR-30 signal gets its own 74 x 34 mm native KiCad board in a Hammond 1551KFLBK envelope candidate. No signal reference, shield, enclosure or channel is shared.\n\nThe complete nominal chain is 200 kOhm per pod lead, 10.2 kOhm per measurement-panel lead and the nominal 1 MOhm NI-9229 differential input. Its paper ratio is {NOMINAL_RATIO:.9f} and scale correction is {NOMINAL_CORRECTION:.6f}; this is not calibration evidence. The source terminal to first resistor remains upstream of protection. Exact device-specific tap accessories, <=100 mm guarded tails, loading/fault review, PCB/enclosure FAI, build, calibration and FER-G11 remain open.\n''', encoding="utf-8")
    write_cad(); make_svg(); make_html()
    shutil.copy2(Path(__file__), OUT / "diagnostic-pickoff-source.py")
    shutil.copy2(ROOT / "tools" / "check_hr30_diagnostic_pickoff_pods_p01.py", OUT / "diagnostic-pickoff-checker.py")
    files = [p for p in OUT.rglob("*") if p.is_file() and p.name != "file-manifest.csv"]
    write_csv(OUT / "file-manifest.csv", [{"path":p.relative_to(OUT).as_posix(),"bytes":p.stat().st_size,"sha256":sha(p),"warning":WARNING} for p in sorted(files)])
    if RELEASE.exists(): shutil.rmtree(RELEASE)
    shutil.copytree(OUT, RELEASE)
    integrate()
    code = "import sys;sys.path.insert(0,'tools');import generate_hr30_system_package_p01 as s;s.refresh_manifest_and_release()"
    run([str(CAD_PYTHON), "-c", code])
    print(json.dumps({"identifier":IDENTIFIER,"pods":8,"channels":8,"erc":"0/0","drc":0,"scale_correction":round(NOMINAL_CORRECTION,6),"source_taps_released":False,"authorities":0}, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--pcb", action="store_true"); args = parser.parse_args()
    if args.pcb: return pcb_mode()
    write_package(); return 0


if __name__ == "__main__":
    raise SystemExit(main())
