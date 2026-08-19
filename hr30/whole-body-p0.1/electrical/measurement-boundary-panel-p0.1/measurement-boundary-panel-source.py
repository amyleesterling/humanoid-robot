#!/usr/bin/env python3
"""Generate HR-30 eight-channel measurement boundary panel P0.1.

The panel is passive test equipment, not a safety device.  Eight independent
two-wire paths remain mutually floating.  A separate 3-AA timing slate has no
electrical connection to any robot or analog-channel net.
"""

from __future__ import annotations

import csv
import hashlib
import html
import importlib.util
import json
import math
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import pcbnew


ROOT = Path(__file__).resolve().parents[1]
WHOLE = ROOT / "hr30" / "whole-body-p0.1"
OUT = WHOLE / "electrical" / "measurement-boundary-panel-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / "electrical" / "measurement-boundary-panel-p0.1"
INSTRUMENTS = WHOLE / "first-energization-instrumentation-p0.1"
PROJECT = "hr30-measurement-boundary-panel-p0.1"
IDENTIFIER = "HR30-MEASUREMENT-BOUNDARY-PANEL-P0.1"
DATE = "2026-08-18"
WARNING = "PRELIMINARY - UNBUILT MEASUREMENT FIXTURE - ZERO SAFETY CREDIT - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, WALKING OR ENERGIZATION"
AUTHORITY = "NO PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED-TEST, MOTION, WALKING OR ENERGIZATION AUTHORITY"
KICAD = Path(r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe")
CAD_PYTHON = ROOT.parent / ".venvs" / "hr-v0-cad" / "Scripts" / "python.exe"
FP_ROOT = Path(r"C:\Program Files\KiCad\10.0\share\kicad\footprints")

PHOENIX_HEADER = "Connector_Phoenix_MSTB:PhoenixContact_MSTBA_2,5_2-G-5,08_1x02_P5.08mm_Horizontal"
PHOENIX_PAGE = "https://www.phoenixcontact.com/en-us/products/pcb-header-mstba-25-2-g-508-1757242"
PHOENIX_PLUG = "https://www.phoenixcontact.com/en-us/products/pcb-connector-mstb-25-2-st-508-1757019"
VISHAY_TNPW = "https://www.vishay.com/docs/31006/tnpw.pdf"
NI_9229 = "https://download.ni.com/support/manuals/374184c_02.pdf"
NI_9924 = "https://www.ni.com/en/shop/hardware/connectors/model-ni-9924"
KEYSTONE_2464 = "https://www.keyelco.com/product.cfm/product_id/1029"
OMRON_B3F = "https://components.omron.com/sites/default/files/datasheet_pdf/A070-E1.pdf"
KINGBRIGHT_LED = "https://www.kingbrightusa.com/product.asp?catalog_name=LED&product_id=WP7113QBC%2FD"
HAMMOND_RZ = "https://www.hammfg.com/electronics/small-case/plastic/rz"

CHANNELS = [
    (1, "CH-AI-01", "ACT_MAIN_SOURCE_12V", "INS-02/AI0"),
    (2, "CH-AI-02", "ACT_MAIN_SAFE_12V", "INS-02/AI1"),
    (3, "CH-AI-03", "TTL_SELECTED_SAFE_9V", "INS-02/AI2"),
    (4, "CH-AI-04", "CTRL_SAFE_5V", "INS-02/AI3"),
    (5, "CH-AI-05", "ESTOP_CH_A_24V", "INS-03/AI0"),
    (6, "CH-AI-06", "WATCHDOG_PERMIT_24V", "INS-03/AI1"),
    (7, "CH-AI-07", "K1_DIAGNOSTIC_24V", "INS-03/AI2"),
    (8, "CH-AI-08", "K2_DIAGNOSTIC_24V", "INS-03/AI3"),
]


@dataclass(frozen=True)
class Part:
    ref: str
    value: str
    manufacturer: str
    mpn: str
    footprint: str
    pins: dict[str, str]
    x: float
    y: float
    rotation: float = 0.0
    section: str = "ANALOG"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"empty register: {path.name}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def analog_parts() -> list[Part]:
    items: list[Part] = []
    for index, _, signal, _ in CHANNELS:
        y = 10.0 + (index - 1) * 13.5
        base = f"CH{index}"
        items += [
            Part(f"J{index}I", f"{signal} floating input", "Phoenix Contact", "1757242", PHOENIX_HEADER,
                 {"1":f"{base}_HI_IN","2":f"{base}_LO_IN"}, 12, y, 90),
            Part(f"R{index}A", "5.10 kOhm 0.1% series", "Vishay", "ORDER CODE SELECTION REQUIRED", "Resistor_SMD:R_1206_3216Metric", {"1":f"{base}_HI_IN","2":f"{base}_HI_MID"}, 55, y),
            Part(f"R{index}B", "5.10 kOhm 0.1% series", "Vishay", "ORDER CODE SELECTION REQUIRED", "Resistor_SMD:R_1206_3216Metric", {"1":f"{base}_HI_MID","2":f"{base}_HI_OUT"}, 110, y),
            Part(f"R{index}C", "5.10 kOhm 0.1% series", "Vishay", "ORDER CODE SELECTION REQUIRED", "Resistor_SMD:R_1206_3216Metric", {"1":f"{base}_LO_IN","2":f"{base}_LO_MID"}, 55, y - 5.08),
            Part(f"R{index}D", "5.10 kOhm 0.1% series", "Vishay", "ORDER CODE SELECTION REQUIRED", "Resistor_SMD:R_1206_3216Metric", {"1":f"{base}_LO_MID","2":f"{base}_LO_OUT"}, 110, y - 5.08),
            Part(f"J{index}O", f"to {signal} DAQ input", "Phoenix Contact", "1757242", PHOENIX_HEADER,
                 {"1":f"{base}_HI_OUT","2":f"{base}_LO_OUT"}, 184, y, 90),
        ]
    return items


def slate_parts() -> list[Part]:
    return [
        Part("JBT1", "3-AA battery holder input", "Phoenix Contact", "1757242", PHOENIX_HEADER, {"1":"SLATE_BAT_POS","2":"SLATE_BAT_RET"}, 12, 124, 90, "SLATE"),
        Part("SW1", "momentary sync", "Omron", "B3F-1000", "Button_Switch_THT:SW_TH_Tactile_Omron_B3F-100x", {"1":"SLATE_BAT_POS","2":"SLATE_ACTIVE"}, 42, 119, 0, "SLATE"),
        Part("D1", "blue visible sync LED", "Kingbright", "WP7113QBC/D", "LED_THT:LED_D5.0mm_Clear", {"1":"SLATE_LED_RET","2":"SLATE_ACTIVE"}, 72, 122, 0, "SLATE"),
        Part("RSL1", "330 Ohm LED series", "Vishay", "ORDER CODE SELECTION REQUIRED", "Resistor_SMD:R_1206_3216Metric", {"1":"SLATE_LED_RET","2":"SLATE_BAT_RET"}, 90, 128, 0, "SLATE"),
        Part("RSL2", "1.00 kOhm DIO series", "Vishay", "ORDER CODE SELECTION REQUIRED", "Resistor_SMD:R_1206_3216Metric", {"1":"SLATE_ACTIVE","2":"SLATE_OUT"}, 122, 118, 0, "SLATE"),
        Part("RSL3", "100 kOhm output pulldown", "Vishay", "ORDER CODE SELECTION REQUIRED", "Resistor_SMD:R_1206_3216Metric", {"1":"SLATE_OUT","2":"SLATE_BAT_RET"}, 150, 128, 0, "SLATE"),
        Part("JTTL", "to NI-9924 / NI-9401 DIO0", "Phoenix Contact", "1757242", PHOENIX_HEADER, {"1":"SLATE_OUT","2":"SLATE_BAT_RET"}, 184, 124, 90, "SLATE"),
    ]


def load_model():
    path = ROOT / "tools" / "generate_hr_v0_electrical_v3.py"
    spec = importlib.util.spec_from_file_location("hr30_measurement_model", path)
    if not spec or not spec.loader: raise RuntimeError("cannot load schematic model")
    model = importlib.util.module_from_spec(spec); sys.modules[spec.name] = model; spec.loader.exec_module(model)
    model.OUT = OUT; model.PROJECT = PROJECT; model.REV = "P0.1"; model.DATE = DATE; model.WARNING = WARNING
    model.PROJECT_TITLE = "PROJECT BUTTON HR-30 MEASUREMENT BOUNDARY"
    model.PROJECT_SUBTITLE = "Eight floating current-limited differential lanes plus an independent battery sync slate; zero safety credit."
    return model


def schematic_component(model, part: Part, position: tuple[float, float]):
    pin_names = {"1":"HI / +" if part.section == "ANALOG" else "CONTACT 1", "2":"LO / -" if part.section == "ANALOG" else "CONTACT 2"}
    pins = [model.pn(part.ref, number, pin_names.get(number, number), net, "left" if number == "1" else "right") for number, net in part.pins.items()]
    source = PHOENIX_PAGE if part.ref.startswith("J") else VISHAY_TNPW if part.ref.startswith("R") else OMRON_B3F if part.ref == "SW1" else KINGBRIGHT_LED
    return model.Component(part.ref, part.value, pins, "CANDIDATE - PHYSICAL VALIDATION OPEN", "TEST EQUIPMENT ONLY; ZERO SAFETY CREDIT", source, "Electrical value/footprint encoded; passive order codes and as-built validation remain open.", position=position, width=58, footprint=part.footprint)


def write_schematic(items: list[Part]) -> None:
    model = load_model(); sheets = []
    analog = [p for p in items if p.section == "ANALOG"]
    for sheet_index, channel_range in enumerate(((1,2,3,4),(5,6,7,8)), 1):
        sheet = model.Sheet(sheet_index, f"0{sheet_index}_channels_{channel_range[0]}_{channel_range[-1]}.kicad_sch", f"Floating differential channels {channel_range[0]}-{channel_range[-1]}", "Every lead has two series resistors; channels share no nets or reference.")
        selected = [p for p in analog if int(''.join(ch for ch in p.ref if ch.isdigit()) or 0) in channel_range]
        positions = {}
        for row, ch in enumerate(channel_range):
            refs = [f"J{ch}I",f"R{ch}A",f"R{ch}B",f"J{ch}O",f"R{ch}C",f"R{ch}D"]
            coords = [(55,48+row*70),(140,38+row*70),(225,38+row*70),(365,48+row*70),(140,66+row*70),(225,66+row*70)]
            positions.update(dict(zip(refs,coords)))
        sheet.components = [schematic_component(model,p,positions[p.ref]) for p in selected]
        sheet.notes = [
            "No channel conductor is connected to another channel, chassis, PE, USB ground or slate return.",
            "Two 5.10 kOhm 0.1% series resistors per lead provide current limitation; they are not fuses or safety components.",
            "The 1 MOhm nominal NI-9229 differential input produces a nominal 1.0204 scale correction; calibrate every assembled channel.", WARNING,
        ]
        sheets.append(sheet)
    slate = model.Sheet(3, "03_battery_sync_slate.kicad_sch", "Independent camera/DAQ synchronization slate", "Three-AA source drives one visible LED and one current-limited TTL output; no robot connection.")
    slate_items = [p for p in items if p.section == "SLATE"]
    slate_pos = {"JBT1":(52,70),"SW1":(125,70),"D1":(205,52),"RSL1":(275,52),"RSL2":(205,100),"RSL3":(275,126),"JTTL":(360,100)}
    slate.components = [schematic_component(model,p,slate_pos[p.ref]) for p in slate_items]
    slate.notes = [
        "Only 3 x AA NiMH or alkaline cells may be considered; measured open-circuit pack voltage must remain below the NI-9401 5.25 V normal-input maximum.",
        "JTTL connects only through an exact, reviewed cable to NI-9924/NI-9401 DIO0. Direct robot 24 V connection is prohibited.",
        "The LED and TTL event are energized by the same momentary contact for visual/electrical time correlation.", WARNING,
    ]
    sheets.append(slate)
    net_counts: dict[str,int] = {}
    for sheet in sheets:
        for component in sheet.components:
            for pin in component.pins: net_counts[pin.net] = net_counts.get(pin.net, 0) + 1
    wires = model.build_wire_numbers(sheets, net_counts); root_uuid = model.uid("root-hr30-measurement-boundary-p0.1")
    project = {"board":{},"boards":[],"cvpcb":{},"erc":{},"libraries":{},"meta":{"filename":f"{PROJECT}.kicad_pro","version":1},"net_settings":{"classes":[{"name":"Default","priority":2147483647,"clearance":0.20,"track_width":0.25,"via_diameter":0.70,"via_drill":0.35}],"meta":{"version":3}},"pcbnew":{},"schematic":{},"text_variables":{"PROJECT_STATUS":WARNING}}
    (OUT/f"{PROJECT}.kicad_pro").write_text(json.dumps(project,indent=2)+"\n",encoding="utf-8")
    components = [c for s in sheets for c in s.components]
    symbols = [model.lib_symbol(c).replace(f'(symbol "PBV3:{c.ref}"',f'(symbol "{c.ref}"',1) for c in components]
    (OUT/f"{PROJECT}.kicad_sym").write_text('(kicad_symbol_lib\n  (version 20251024) (generator "kicad_symbol_editor") (generator_version "10.0")\n  '+"\n".join(symbols)+'\n)\n',encoding="utf-8")
    (OUT/"sym-lib-table").write_text(f'(sym_lib_table\n  (version 7)\n  (lib (name "PBV3")(type "KiCad")(uri "${{KIPRJMOD}}/{PROJECT}.kicad_sym")(options "")(descr "HR-30 measurement-boundary symbols"))\n)\n',encoding="utf-8")
    (OUT/f"{PROJECT}.kicad_sch").write_text(model.root_schematic(root_uuid,sheets),encoding="utf-8")
    for sheet in sheets: (OUT/sheet.filename).write_text(model.child_schematic(root_uuid,sheet,net_counts,wires),encoding="utf-8")


def footprint(identifier: str):
    library, name = identifier.split(":",1); fp = pcbnew.FootprintLoad(str(FP_ROOT/f"{library}.pretty"),name)
    if fp is None: raise RuntimeError(f"cannot load footprint {identifier}")
    return fp


def pad_positions(fp, number: str) -> list[tuple[float,float]]:
    out=[]
    for pad in fp.Pads():
        if pad.GetNumber() == number:
            p=pad.GetPosition(); out.append((pcbnew.ToMM(p.x),pcbnew.ToMM(p.y)))
    if not out: raise RuntimeError(f"no pad {fp.GetReference()}.{number}")
    return out


def add_track(board, net, points, width=.30, layer=pcbnew.F_Cu):
    for a,b in zip(points,points[1:]):
        t=pcbnew.PCB_TRACK(board); t.SetStart(pcbnew.VECTOR2I_MM(*a)); t.SetEnd(pcbnew.VECTOR2I_MM(*b)); t.SetLayer(layer); t.SetWidth(pcbnew.FromMM(width)); t.SetNet(net); board.Add(t)


def add_via(board, net, point):
    via=pcbnew.PCB_VIA(board); via.SetPosition(pcbnew.VECTOR2I_MM(*point)); via.SetWidth(pcbnew.FromMM(.80)); via.SetDrill(pcbnew.FromMM(.40)); via.SetLayerPair(pcbnew.F_Cu,pcbnew.B_Cu); via.SetNet(net); board.Add(via)


def add_text(board, value, x, y, size=.75, layer=pcbnew.F_SilkS):
    t=pcbnew.PCB_TEXT(board); t.SetText(value); t.SetPosition(pcbnew.VECTOR2I_MM(x,y)); t.SetLayer(layer); t.SetTextSize(pcbnew.VECTOR2I_MM(size,size)); t.SetTextThickness(pcbnew.FromMM(max(.15,size*.14))); board.Add(t)


def write_board(items: list[Part]) -> dict[str,object]:
    board=pcbnew.BOARD(); board.SetCopperLayerCount(2); settings=board.GetDesignSettings(); settings.SetBoardThickness(pcbnew.FromMM(1.6)); settings.m_MinClearance=pcbnew.FromMM(.20); settings.m_TrackMinWidth=pcbnew.FromMM(.20); settings.m_HoleClearance=pcbnew.FromMM(.25); settings.m_HoleToHoleMin=pcbnew.FromMM(.30); settings.m_ViasMinSize=pcbnew.FromMM(.70); settings.m_MinThroughDrill=pcbnew.FromMM(.35); settings.m_ViasMinAnnularWidth=pcbnew.FromMM(.15); settings.m_NetSettings.GetDefaultNetclass().SetClearance(pcbnew.FromMM(.20))
    names=sorted({net for p in items for net in p.pins.values()}); nets={}
    for name in names: net=pcbnew.NETINFO_ITEM(board,name); board.Add(net); nets[name]=net
    fps={}
    for part in items:
        fp=footprint(part.footprint); fp.SetReference(part.ref); fp.SetValue(part.mpn); fp.SetPosition(pcbnew.VECTOR2I_MM(part.x,part.y)); fp.SetOrientationDegrees(part.rotation); fp.Reference().SetVisible(False); fp.Value().SetVisible(False)
        for pad in fp.Pads():
            net=part.pins.get(pad.GetNumber());
            if net: pad.SetNet(nets[net])
        board.Add(fp); fps[part.ref]=fp
    for index,point in enumerate(((5,5),(205,5),(5,129),(205,129)),1):
        hole=footprint("MountingHole:MountingHole_3.2mm_M3"); hole.SetReference(f"H{index}"); hole.SetValue("M3 ENCLOSURE STANDOFF"); hole.SetPosition(pcbnew.VECTOR2I_MM(*point)); hole.SetBoardOnly(True); hole.SetExcludedFromBOM(True); hole.SetExcludedFromPosFiles(True); hole.Reference().SetVisible(False); hole.Value().SetVisible(False); board.Add(hole)
    corners=((0,0),(210,0),(210,134),(0,134))
    for a,b in zip(corners,(*corners[1:],corners[0])):
        edge=pcbnew.PCB_SHAPE(board); edge.SetShape(pcbnew.SHAPE_T_SEGMENT); edge.SetStart(pcbnew.VECTOR2I_MM(*a)); edge.SetEnd(pcbnew.VECTOR2I_MM(*b)); edge.SetLayer(pcbnew.Edge_Cuts); edge.SetWidth(pcbnew.FromMM(.20)); board.Add(edge)
    # Every analog net connects only the two pads that actually share it.
    for index,_,signal,_ in CHANNELS:
        for net_name in (f"CH{index}_HI_IN",f"CH{index}_HI_MID",f"CH{index}_HI_OUT",f"CH{index}_LO_IN",f"CH{index}_LO_MID",f"CH{index}_LO_OUT"):
            endpoints=[]
            for part in items:
                for pin,name in part.pins.items():
                    if name==net_name: endpoints.append(pad_positions(fps[part.ref],pin)[0])
            if len(endpoints)!=2: raise RuntimeError(f"{net_name} expected two endpoints, got {len(endpoints)}")
            add_track(board,nets[net_name],endpoints,.34)
        add_text(board,f"CH{index}",29,8.1+(index-1)*13.5,.80)
    # Slate routing is confined below the isolation line and has no analog nets.
    p=lambda r,n: pad_positions(fps[r],n)[0]
    for q in pad_positions(fps["SW1"],"1")[1:]: add_track(board,nets["SLATE_BAT_POS"],[p("SW1","1"),q],.35)
    for q in pad_positions(fps["SW1"],"2")[1:]: add_track(board,nets["SLATE_ACTIVE"],[p("SW1","2"),q],.35)
    add_track(board,nets["SLATE_BAT_POS"],[p("JBT1","1"),(28,116),p("SW1","1")],.35)
    add_track(board,nets["SLATE_ACTIVE"],[p("SW1","2"),(61,115),(80,115),(80,122),p("D1","2")],.35)
    add_track(board,nets["SLATE_ACTIVE"],[(61,115),(114,115),p("RSL2","1")],.35)
    add_track(board,nets["SLATE_LED_RET"],[p("D1","1"),(72,125),(82,125),p("RSL1","1")],.35)
    add_track(board,nets["SLATE_OUT"],[p("RSL2","2"),(138,118),p("RSL3","1")],.35)
    add_track(board,nets["SLATE_OUT"],[(138,118),(180,116),p("JTTL","1")],.35)
    via_r1=(p("RSL1","2")[0],131.0); via_r3=(p("RSL3","2")[0],131.0)
    add_track(board,nets["SLATE_BAT_RET"],[p("RSL1","2"),via_r1],.35); add_via(board,nets["SLATE_BAT_RET"],via_r1)
    add_track(board,nets["SLATE_BAT_RET"],[p("RSL3","2"),via_r3],.35); add_via(board,nets["SLATE_BAT_RET"],via_r3)
    return_bus=[p("JBT1","2"),(28,132),via_r1,via_r3,(170,132),(170,p("JTTL","2")[1]),p("JTTL","2")]
    add_track(board,nets["SLATE_BAT_RET"],return_bus,.40,pcbnew.B_Cu)
    # Clear physical demarcation between floating analog lanes and slate.
    line=pcbnew.PCB_SHAPE(board); line.SetShape(pcbnew.SHAPE_T_SEGMENT); line.SetStart(pcbnew.VECTOR2I_MM(24,111)); line.SetEnd(pcbnew.VECTOR2I_MM(186,111)); line.SetLayer(pcbnew.F_SilkS); line.SetWidth(pcbnew.FromMM(.50)); board.Add(line)
    add_text(board,"EIGHT MUTUALLY FLOATING DIFFERENTIAL CHANNELS",105,2.2,1.05)
    add_text(board,"BATTERY SYNC SLATE - NO ROBOT CONNECTION",105,132.3,.90)
    board_dir=OUT/"board"; board_dir.mkdir(parents=True,exist_ok=True); path=board_dir/f"{PROJECT}.kicad_pcb"; pcbnew.SaveBoard(str(path),board)
    return {"path":path,"component_count":len(items),"named_net_count":len(names),"board_mm":[210,134,1.6],"analog_channel_count":8}


def run_cli(args, allowed=(0,)):
    cp=subprocess.run([str(KICAD),*map(str,args)],cwd=OUT,text=True,capture_output=True)
    if cp.returncode not in allowed: raise RuntimeError(f"KiCad failed {cp.returncode}: {' '.join(map(str,args))}\n{cp.stdout}\n{cp.stderr}")
    return cp


def validate_export(info):
    validation=OUT/"validation"; output=OUT/"output"; validation.mkdir(exist_ok=True); output.mkdir(exist_ok=True)
    erc=validation/f"{PROJECT}-erc.rpt"; cp=run_cli(["sch","erc","--exit-code-violations","--output",erc,OUT/f"{PROJECT}.kicad_sch"],(0,5))
    if cp.returncode: raise RuntimeError(erc.read_text(encoding="utf-8"))
    run_cli(["sch","export","svg","--output",output,OUT/f"{PROJECT}.kicad_sch"])
    drc=validation/f"{PROJECT}-drc.rpt"; cp=run_cli(["pcb","drc","--severity-all","--exit-code-violations","--output",drc,info["path"]],(0,5))
    if cp.returncode: raise RuntimeError(drc.read_text(encoding="utf-8"))
    run_cli(["pcb","export","svg","--mode-single","--output",output/f"{PROJECT}-front.svg","--layers","F.Cu,F.Silkscreen,F.Mask,Edge.Cuts","--fit-page-to-board","--exclude-drawing-sheet",info["path"]])
    run_cli(["pcb","export","svg","--mode-single","--output",output/f"{PROJECT}-back.svg","--layers","B.Cu,B.Silkscreen,B.Mask,Edge.Cuts","--mirror","--fit-page-to-board","--exclude-drawing-sheet",info["path"]])
    fab=OUT/"fabrication-candidate-not-released"; gerber=fab/"gerber"; drill=fab/"drill"; gerber.mkdir(parents=True,exist_ok=True); drill.mkdir(parents=True,exist_ok=True)
    run_cli(["pcb","export","gerbers","--output",gerber,"--layers","F.Cu,B.Cu,F.Mask,B.Mask,F.Silkscreen,B.Silkscreen,Edge.Cuts","--precision","6","--check-zones",info["path"]])
    run_cli(["pcb","export","drill","--output",drill,"--format","excellon","--excellon-units","mm","--generate-map","--map-format","svg","--generate-report","--report-path",drill/f"{PROJECT}-drill-report.rpt",info["path"]])
    run_cli(["pcb","export","ipcd356","--output",fab/f"{PROJECT}.d356",info["path"]])
    run_cli(["pcb","export","pos","--output",fab/f"{PROJECT}-positions.csv","--side","both","--format","csv","--units","mm",info["path"]])
    run_cli(["pcb","export","stats","--output",fab/f"{PROJECT}-board-stats.json","--format","json","--units","mm",info["path"]])
    (fab/"README.txt").write_text(WARNING+"\nManufacturing outputs are candidates only and are not released for order.\n",encoding="utf-8")
    for svg in OUT.rglob("*.svg"): svg.write_text("\n".join(line.rstrip() for line in svg.read_text(encoding="utf-8").splitlines())+"\n",encoding="utf-8")
    return {"erc_errors":0,"erc_warnings":0,"drc_violations":0,"unconnected_items":0}


def channel_calculations() -> list[dict[str,object]]:
    values=[12.0,24.0,60.0]
    rows=[]
    for voltage in values:
        for fault,resistors in (("NOMINAL FOUR RESISTORS",4),("ONE RESISTOR SHORT",3)):
            loop=resistors*5100.0; current=voltage/loop; power=current*current*5100.0
            rows.append({"applied_differential_v":voltage,"case":fault,"remaining_series_resistors":resistors,"loop_resistance_ohm":loop,"short_current_ma":round(current*1000,6),"power_per_remaining_resistor_mw":round(power*1000,6),"capacity_claim":"NONE; ENGINEERING CALCULATION ONLY","warning":WARNING})
    return rows


def publish(items, info, checks):
    channels=[]; contacts=[]
    for index,channel,signal,daq in CHANNELS:
        channels.append({"channel":channel,"signal":signal,"panel_input":f"J{index}I.1 HI / J{index}I.2 LO","panel_output":f"J{index}O.1 HI / J{index}O.2 LO","daq_endpoint":daq,"series_resistance_each_lead_ohm":10200,"nominal_ni_input_ohm":1000000,"nominal_output_over_input":round(1000000/(1000000+20400),9),"nominal_scale_correction":1.0204,"shared_reference":"NONE","calibration":"REQUIRED PER ASSEMBLED CHANNEL","warning":WARNING})
        for side,ref in (("INPUT",f"J{index}I"),("OUTPUT",f"J{index}O")):
            for pin,polarity in ((1,"HI/+"),(2,"LO/-")):
                contacts.append({"channel":channel,"connector":ref,"side":side,"contact":pin,"polarity":polarity,"signal":signal,"header":"Phoenix 1757242","mating_plug":"Phoenix 1757019","installed_harness_endpoint":"SELECTION REQUIRED","warning":WARNING})
    contacts += [
        {"channel":"CH-DIO-01","connector":"JBT1","side":"SLATE BATTERY","contact":1,"polarity":"+","signal":"SLATE_BAT_POS","header":"Phoenix 1757242","mating_plug":"Phoenix 1757019","installed_harness_endpoint":"Keystone 2464 leads; harness/termination selection required","warning":WARNING},
        {"channel":"CH-DIO-01","connector":"JBT1","side":"SLATE BATTERY","contact":2,"polarity":"-","signal":"SLATE_BAT_RET","header":"Phoenix 1757242","mating_plug":"Phoenix 1757019","installed_harness_endpoint":"Keystone 2464 leads; harness/termination selection required","warning":WARNING},
        {"channel":"CH-DIO-01","connector":"JTTL","side":"SLATE OUTPUT","contact":1,"polarity":"TTL EVENT","signal":"SLATE_OUT","header":"Phoenix 1757242","mating_plug":"Phoenix 1757019","installed_harness_endpoint":"NI-9924 DIO0 exact terminal/cable selection required","warning":WARNING},
        {"channel":"CH-DIO-01","connector":"JTTL","side":"SLATE OUTPUT","contact":2,"polarity":"SLATE RETURN","signal":"SLATE_BAT_RET","header":"Phoenix 1757242","mating_plug":"Phoenix 1757019","installed_harness_endpoint":"NI-9924 COM exact terminal/cable selection required","warning":WARNING},
    ]
    write_csv(OUT/"channel-register.csv",channels); write_csv(OUT/"connector-contact-map.csv",contacts); write_csv(OUT/"current-limit-calculation.csv",channel_calculations())
    nets=[]
    for name in sorted({net for p in items for net in p.pins.values()}):
        refs=[f"{p.ref}.{pin}" for p in items for pin,net in p.pins.items() if net==name]
        nets.append({"net":name,"terminals":"; ".join(refs),"domain":"SLATE - INDEPENDENT BATTERY" if name.startswith("SLATE") else name.split("_")[0]+" - FLOATING ANALOG","cross_channel_connection":"NO","robot_power_capability":"NONE; PASSIVE MEASUREMENT PATH" if not name.startswith("SLATE") else "NONE; NO ROBOT CONNECTION","warning":WARNING})
    write_csv(OUT/"net-register.csv",nets)
    bom=[]
    for p in items:
        state="EXACT CANDIDATE" if p.mpn not in ("ORDER CODE SELECTION REQUIRED",) else "FAMILY/VALUE/FOOTPRINT DEFINED; ORDER CODE SELECTION REQUIRED"
        bom.append({"reference":p.ref,"item":p.value,"manufacturer":p.manufacturer,"candidate_order_code":p.mpn,"quantity":1,"footprint":p.footprint,"selection_state":state,"procurement_released":"NO","warning":WARNING})
    bom += [
        {"reference":"P1-P18","item":"2-position mating screw plug","manufacturer":"Phoenix Contact","candidate_order_code":"1757019","quantity":18,"footprint":"CABLE ITEM","selection_state":"EXACT CANDIDATE; WIRE/FERRULE PROCESS OPEN","procurement_released":"NO","warning":WARNING},
        {"reference":"BT1","item":"3-AA through-hole holder used off-board","manufacturer":"Keystone Electronics","candidate_order_code":"2464","quantity":1,"footprint":"OFF-BOARD","selection_state":"EXACT CANDIDATE; CELL CHEMISTRY/HARNESS OPEN","procurement_released":"NO","warning":WARNING},
        {"reference":"TB1","item":"NI-9924 front-mount screw terminal","manufacturer":"NI","candidate_order_code":"781922-01","quantity":1,"footprint":"OFF-BOARD","selection_state":"EXACT CANDIDATE; DIO CONTACT MAP/LEAD OPEN","procurement_released":"NO","warning":WARNING},
        {"reference":"ENC1","item":"222 x 146 x 55 mm polycarbonate enclosure clear lid","manufacturer":"Hammond","candidate_order_code":"RZ0218C","quantity":1,"footprint":"OFF-BOARD","selection_state":"EXACT CANDIDATE; CUTOUT/DFM/RECEIVING OPEN","procurement_released":"NO","warning":WARNING},
        {"reference":"PCB1","item":"210 x 134 x 1.6 mm two-layer FR-4 PCB","manufacturer":"SELECTION REQUIRED","candidate_order_code":"SELECTION REQUIRED","quantity":1,"footprint":"NATIVE BOARD","selection_state":"NATIVE DESIGN PRESENT; FABRICATOR/FINISH/DFM OPEN","procurement_released":"NO","warning":WARNING},
    ]
    write_csv(OUT/"candidate-bom.csv",bom)
    sources=[
        ("MB-S01","Phoenix Contact","MSTBA 2,5/2-G-5,08 product record 1757242",PHOENIX_PAGE,"live official product record; accessed 2026-08-18","2 poles; 5.08 mm pitch; 12 A nominal; 320 V; exact PCB-header footprint candidate"),
        ("MB-S02","Phoenix Contact","MSTB 2,5/2-ST-5,08 product record 1757019",PHOENIX_PLUG,"live official product record; accessed 2026-08-18","matching 2-position screw plug; 0.2-2.5 mm2 / AWG24-12"),
        ("MB-S03","Vishay","TNPW precision thin-film resistor datasheet 31006",VISHAY_TNPW,"revision 18-Feb-2025; accessed 2026-08-18","1206: 0.25 W, 200 V, 10 ohm-2 Mohm; 0.1% and 25 ppm/K available; exact order codes remain selection required"),
        ("MB-S04","NI","NI-9229 datasheet 374184C-02",NI_9229,"official datasheet; accessed 2026-08-18","4 differential simultaneous channels; +/-60 V nominal; 1 Mohm differential input; +/-100 V overvoltage; wiring and torque"),
        ("MB-S05","NI","NI-9924 product record",NI_9924,"live official product page; accessed 2026-08-18","781922-01; 25-pin female D-sub to screw-terminal block; 60 VDC/30 Vrms"),
        ("MB-S06","Keystone Electronics","3 AA cell holder product record",KEYSTONE_2464,"live official product page; accessed 2026-08-18","part 2464; 3 AA cells in series; polypropylene; through-hole holder"),
        ("MB-S07","Omron","B3F tactile switch datasheet A070-E1",OMRON_B3F,"official datasheet; accessed 2026-08-18","B3F-1000 in production; SPST momentary; 1-50 mA at 3-24 VDC; 1M operations minimum"),
        ("MB-S08","Kingbright","WP7113QBC/D product record",KINGBRIGHT_LED,"live official product page; accessed 2026-08-18","5 mm blue InGaN LED; 465 nm; intensity specified at 20 mA"),
        ("MB-S09","Hammond Manufacturing","RZ enclosure series record",HAMMOND_RZ,"live official product page; accessed 2026-08-18","RZ0218C; 222 x 146 x 55 mm; clear lid; 213.87 x 137.87 mm maximum PCB; designed to meet IP65"),
    ]
    write_csv(OUT/"primary-source-register.csv",[{"source_id":a,"manufacturer":b,"document":c,"url":d,"revision_or_access_date":e,"verified_scope":f,"system_suitability":"PHYSICAL VALIDATION OPEN","warning":WARNING} for a,b,c,d,e,f in sources])
    tests=[
        ("MB-T01","Mutual isolation","With all external connectors removed, every channel contact is >10 Mohm from every other channel, slate, enclosure and PE."),
        ("MB-T02","Per-channel continuity","Each HI and LO path matches the released contact map; no cross-polarity or cross-channel continuity."),
        ("MB-T03","Resistance","Each lead measures 10.2 kohm within assembled tolerance; individual resistor values recorded."),
        ("MB-T04","Calibration","Apply traceable points across each intended range and store fitted gain/offset/uncertainty."),
        ("MB-T05","Output short current","Use a current-limited source and verify the assembled short-current model without exceeding component ratings."),
        ("MB-T06","Single-resistor fault","Fault analysis/review confirms one shorted series resistor does not create an unacceptable loading path."),
        ("MB-T07","Slate voltage","Approved battery chemistry installed; measured open-circuit output remains below 5.25 V."),
        ("MB-T08","Slate timing","LED onset and NI DIO edge offset/uncertainty measured over repeated presses and video frame rates."),
        ("MB-T09","No robot-to-slate connection","Continuity inspection proves slate nets connect only to BT1, SW1, D1, RSL1-RSL3 and JTTL."),
        ("MB-T10","Enclosure/strain relief","Received enclosure, PCB supports, guarded terminals, labels, cable clamps and lid clearances inspected."),
    ]
    write_csv(OUT/"inspection-and-calibration-register.csv",[{"test_id":a,"test":b,"acceptance":c,"result":"NOT EXECUTED","evidence":"REQUIRED","authority":AUTHORITY,"warning":WARNING} for a,b,c in tests])
    holds=[
        ("MB-H01","precision resistor order codes","qualified selection of exact 5.10k 0.1%, 330 ohm, 1k and 100k TNPW candidates plus traceable lot receiving"),
        ("MB-H02","analog input harness endpoints","exact robot/PDU diagnostic terminal locations, connectors, wire, ferrules, strain relief and no-bypass review"),
        ("MB-H03","DAQ output harness","exact NI-9976 contact/wire schedule, cable length, ferrules, shielding/routing and strain relief"),
        ("MB-H04","sync output harness","exact NI-9924 DIO0/COM contact map, cable, voltage check and review"),
        ("MB-H05","slate cell chemistry","exact cells/chemistry, measured maximum pack voltage and replacement control"),
        ("MB-H06","independent ECAD review","qualified schematic/layout/footprint/clearance/source review"),
        ("MB-H07","fabrication/receiving/assembly","DFM, fabricated PCB, enclosure machining, workmanship and received-part inspection"),
        ("MB-H08","calibration/uncertainty","all ten tests executed; per-channel correction/uncertainty and timing offset frozen"),
        ("MB-H09","stage limits/procedure","qualified voltage/current/temperature/time abort limits and signed procedure"),
        ("MB-H10","FER-G11 physical closure","installed protected points, in-date instruments, dry rehearsal and qualified signoff"),
    ]
    write_csv(OUT/"open-holds.csv",[{"hold_id":a,"unresolved_item":b,"closure_evidence":c,"state":"OPEN","authority":AUTHORITY,"warning":WARNING} for a,b,c in holds])
    # Explicitly update the earlier 12 connection obligations without pretending installation.
    probe_rows=list(csv.DictReader((INSTRUMENTS/"probe-connection-register.csv").open(encoding="utf-8",newline="")))
    for row in probe_rows:
        if row["channel"].startswith("CH-AI-"):
            n=int(row["channel"].split("-")[-1]); row["method"] = f"route through passive measurement panel J{n}I -> J{n}O; exact field and NI harnesses remain open"; row["connector_pinout_released"]="PANEL CONTACTS RELEASED; FIELD/DAQ ENDS OPEN"; row["probe_protection_released"]="CURRENT-LIMITING DESIGN PRESENT; NOT PHYSICALLY VALIDATED"; row["installed"]="NO"
        elif row["channel"]=="CH-DIO-01":
            row["method"]="independent battery sync slate JTTL -> NI-9924 DIO0/COM; direct robot 24 V remains prohibited"; row["connector_pinout_released"]="PANEL CONTACTS RELEASED; NI CONTACTS OPEN"; row["probe_protection_released"]="BATTERY-ONLY 1K SERIES DESIGN PRESENT; NOT PHYSICALLY VALIDATED"; row["installed"]="NO"
    write_csv(OUT/"instrumentation-connection-disposition.csv",probe_rows)
    info = dict(info); info["path"] = Path(info["path"]).relative_to(OUT).as_posix()
    status={"identifier":IDENTIFIER,"date":DATE,"warning":WARNING,**info,**checks,"native_kicad_sheet_count":4,"floating_differential_channel_count":8,"series_resistor_count":32,"analog_shared_net_count":0,"sync_slate_independent_battery":True,"sync_slate_robot_connection_present":False,"nominal_24v_output_short_current_ma":round(24/20400*1000,6),"one_resistor_short_24v_current_ma":round(24/15300*1000,6),"nominal_scale_correction":1.0204,"enclosure_candidate":"Hammond RZ0218C","exact_panel_contact_map_present":True,"field_harness_released":False,"daq_harness_released":False,"fabricated":False,"assembled":False,"calibrated":False,"installed":False,"fer_g11_closed":False,"functional_safety_credit":False,"procurement_authority":False,"fabrication_authority":False,"assembly_authority":False,"connection_authority":False,"powered_test_authority":False,"motion_authority":False,"walking_authority":False,"energization_authority":False}
    (OUT/"panel-status.json").write_text(json.dumps(status,indent=2)+"\n",encoding="utf-8")
    binding={"identifier":IDENTIFIER,"warning":WARNING,"instrumentation_package":"hr30/whole-body-p0.1/first-energization-instrumentation-p0.1","instrumentation_status_sha256":sha(INSTRUMENTS/"instrumentation-status.json"),"instrumentation_probe_register_sha256":sha(INSTRUMENTS/"probe-connection-register.csv"),"fer_gate_register":"hr30/whole-body-p0.1/first-energization-readiness-p0.1/energization-gate-register.csv","fer_gate_register_sha256":sha(WHOLE/"first-energization-readiness-p0.1"/"energization-gate-register.csv"),"scope":"FER-G11 PHYSICAL-INTERFACE DESIGN EVIDENCE ONLY; INSTALLATION/CALIBRATION/QUALIFICATION OPEN"}
    (OUT/"source-binding.json").write_text(json.dumps(binding,indent=2)+"\n",encoding="utf-8")
    (OUT/"README.md").write_text(f"""# HR-30 measurement boundary panel P0.1

**{WARNING}**

This package contains a four-sheet native KiCad project and routed 210 x 134 mm PCB for eight mutually floating differential measurement lanes. Each lead passes through two 5.10 kOhm precision-series resistors before an NI-9229 channel. No analog channel shares a reference, return, chassis or slate net. The independent three-AA synchronization slate drives one visible blue LED and a 1 kOhm-series TTL output for camera/DAQ correlation; it has no robot electrical connection.

The panel contact map is exact, but field-side and NI-side harnesses are not released. The board/enclosure are unbuilt, calibration and timing-correlation tests are unexecuted, resistor order codes and battery chemistry remain selections, and FER-G11 remains open. ERC/DRC prove encoded connectivity only. This is test-equipment design evidence with zero functional-safety credit and no work authority.
""",encoding="utf-8")
    make_html()


def table_html(filename,title):
    rows=list(csv.DictReader((OUT/filename).open(encoding="utf-8",newline=""))); fields=list(rows[0]); head=''.join(f'<th>{html.escape(f.replace("_"," ").title())}</th>' for f in fields); body=''.join('<tr>'+''.join(f'<td>{html.escape(str(r[f]))}</td>' for f in fields)+'</tr>' for r in rows)
    return f'<section><h2>{html.escape(title)}</h2><div class="table-wrap"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div></section>'


def make_html():
    tables=''.join([table_html("channel-register.csv","Eight floating measurement lanes"),table_html("connector-contact-map.csv","Exact panel contact map"),table_html("current-limit-calculation.csv","Current-limit calculations"),table_html("inspection-and-calibration-register.csv","Physical inspection and calibration plan"),table_html("open-holds.csv","What remains open")])
    (OUT/"index.html").write_text(f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 measurement boundary panel</title><script type="module" src="../../vendor/model-viewer.min.js"></script><style>:root{{--sky:#9ddcff;--blue:#082d67;--mid:#145ca8;--gold:#ffc83d;--ink:#0b1d35;--paper:#f7fbff;--hold:#fff0b8;--line:#85bee4}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.55 system-ui,sans-serif}}header{{padding:clamp(28px,6vw,72px);background:linear-gradient(135deg,var(--blue),var(--mid));color:white}}header h1{{font-size:clamp(36px,6vw,68px);line-height:1.03;margin:.25em 0}}main{{max-width:1500px;margin:auto;padding:clamp(18px,4vw,52px)}}.warning{{background:var(--gold);color:#221800;padding:16px;border:3px solid #6e4d00;font-weight:900}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:18px}}.card{{background:white;border:2px solid var(--blue);border-radius:16px;padding:20px;box-shadow:6px 6px 0 var(--sky)}}.hold{{background:var(--hold)}}.metric{{font-size:clamp(30px,4vw,52px);font-weight:900;color:var(--blue)}}model-viewer{{width:100%;height:min(70vh,700px);min-height:480px;background:linear-gradient(#dff4ff,#fff);border:3px solid var(--blue);border-radius:18px}}section{{margin:46px 0}}h2{{font-size:clamp(26px,3vw,40px);color:var(--blue)}}.viewer{{overflow:auto;background:white;border:2px solid var(--line);border-radius:14px}}object{{display:block;width:100%;min-width:900px;min-height:540px}}.table-wrap{{overflow:auto;border:2px solid var(--blue);border-radius:12px;background:white}}table{{border-collapse:collapse;width:max-content;min-width:100%}}th,td{{padding:12px 14px;border-bottom:1px solid #a8c4e4;vertical-align:top;max-width:470px;white-space:normal}}th{{position:sticky;top:0;background:var(--blue);color:white;font-size:14px;text-align:left}}td{{font-size:16px}}a{{color:#064e9d;font-weight:800}}@media(max-width:650px){{model-viewer{{min-height:420px}}th,td{{min-width:180px}}}}</style></head><body><header><div class="warning">{html.escape(WARNING)}</div><p>HR-30 / FER-G11 / physical measurement boundary</p><h1>Eight voltages. Eight floating paths. No mystery clips.</h1><p>A routed passive board defines every panel contact and keeps the camera/DAQ sync pulse on its own batteries. Field harnesses, calibration and qualified limits remain open.</p></header><main><section class="grid"><article class="card"><div class="metric">8 × 2</div><h2>floating conductors</h2><p>No common reference joins the differential lanes.</p></article><article class="card"><div class="metric">1.18 mA</div><h2>24 V short screen</h2><p>Nominal output-short current through four 5.10 kOhm resistors.</p></article><article class="card"><div class="metric">1.0204</div><h2>nominal correction</h2><p>Required scale correction against the NI-9229 nominal 1 MOhm input.</p></article><article class="card hold"><div class="metric">0</div><h2>authorized connections</h2><p>The board is unbuilt and FER-G11 remains open.</p></article></section><section><h2>Enclosed panel candidate</h2><model-viewer src="HR30_measurement_boundary_panel_candidate.glb" camera-controls shadow-intensity="1" exposure="1.05"></model-viewer><p><a href="HR30_measurement_boundary_panel_candidate.step">Download STEP</a>. The CAD is an interface envelope; received RZ0269C geometry controls.</p></section><section><h2>Routed native board</h2><div class="viewer"><object data="output/{PROJECT}-front.svg" type="image/svg+xml" aria-label="Front copper and silkscreen for the measurement boundary panel"></object></div></section><section class="grid"><article class="card"><h2>Analog boundary</h2><p>Two resistors in each lead. No fuse or safety claim. Each assembled path must be calibrated and checked against field loading.</p></article><article class="card"><h2>Sync boundary</h2><p>The button lights a visible LED and issues a battery-only TTL event through 1 kOhm. Direct 24 V is prohibited.</p></article><article class="card hold"><h2>Still blocked</h2><p>Exact field/DAQ harnesses, cells, passive order codes, DFM, fabrication, calibration, timing uncertainty and qualified stage limits.</p></article></section>{tables}<section><h2>Engineering files</h2><p><a href="{PROJECT}.kicad_pro">KiCad project</a> · <a href="board/{PROJECT}.kicad_pcb">PCB</a> · <a href="validation/{PROJECT}-erc.rpt">ERC</a> · <a href="validation/{PROJECT}-drc.rpt">DRC</a> · <a href="candidate-bom.csv">BOM</a> · <a href="primary-source-register.csv">sources</a></p></section></main></body></html>''',encoding="utf-8")
    page = OUT / "index.html"
    page.write_text(page.read_text(encoding="utf-8").replace("RZ0269C", "RZ0218C"), encoding="utf-8")


def integrate():
    status_path=WHOLE/"package-status.json"; status=json.loads(status_path.read_text(encoding="utf-8")); status.update({"measurement_boundary_panel_present":True,"measurement_boundary_panel_native_kicad":True,"measurement_boundary_panel_floating_channels":8,"measurement_boundary_panel_contact_map_present":True,"measurement_boundary_panel_field_harness_released":False,"measurement_boundary_panel_daq_harness_released":False,"measurement_boundary_panel_calibrated":False,"measurement_boundary_panel_safety_credit":False,"fer_g11_closed":False}); status_path.write_text(json.dumps(status,indent=2)+"\n",encoding="utf-8")
    start,end="<!-- HR30-MEASUREMENT-BOUNDARY-P01-START -->","<!-- HR30-MEASUREMENT-BOUNDARY-P01-END -->"
    readme=WHOLE/"README.md"; text=readme.read_text(encoding="utf-8")
    if start in text and end in text: text=text.split(start,1)[0]+text.split(end,1)[1]
    block=f'''{start}\n## Physical measurement boundary\n\nThe [interactive measurement-boundary guide](electrical/measurement-boundary-panel-p0.1/index.html) adds a routed **210 x 134 mm native KiCad board** with eight mutually floating, current-limited differential lanes and an independent battery-powered camera/DAQ sync slate. The panel contact map is exact. Field/DAQ harnesses, resistor order codes, battery chemistry, DFM, fabrication, calibration, timing uncertainty and qualified limits remain open, so FER-G11 and every work authority remain false.\n{end}\n'''; readme.write_text(text.rstrip()+"\n\n"+block,encoding="utf-8")
    page=WHOLE/"index.html"; text=page.read_text(encoding="utf-8")
    if start in text and end in text: text=text.split(start,1)[0]+text.split(end,1)[1]
    section=f'''{start}<section id="measurement-boundary"><h2>The instrument bench now has a real floating measurement boundary</h2><div class="grid"><article class="card pass"><div class="metric">8 × 2</div><p>current-limited conductors with no shared analog reference.</p></article><article class="card pass"><h3>Battery-only sync</h3><p>One button produces the camera LED and NI timing edge without touching robot power.</p></article><article class="card hold"><h3>FER-G11 stays open</h3><p>Harnesses, fabrication, calibration, uncertainty and qualified limits remain physical gates.</p></article></div><p><a href="electrical/measurement-boundary-panel-p0.1/index.html">Open the interactive measurement-boundary guide</a>.</p></section>{end}'''; text=text.replace("</main>",section+"</main>",1); page.write_text(text,encoding="utf-8")


def manifest_release():
    shutil.copy2(Path(__file__),OUT/"measurement-boundary-panel-source.py"); shutil.copy2(ROOT/"tools"/"generate_hr30_measurement_boundary_panel_cad_p01.py",OUT/"measurement-boundary-panel-cad-source.py")
    shutil.copy2(ROOT/"tools"/"check_hr30_measurement_boundary_panel_p01.py",OUT/"measurement-boundary-panel-checker.py")
    files=[p for p in OUT.rglob("*") if p.is_file() and p.name!="file-manifest.csv"]
    write_csv(OUT/"file-manifest.csv",[{"path":p.relative_to(OUT).as_posix(),"bytes":p.stat().st_size,"sha256":sha(p),"warning":WARNING} for p in sorted(files)])
    if RELEASE.exists(): shutil.rmtree(RELEASE)
    shutil.copytree(OUT,RELEASE)
    code="import sys;sys.path.insert(0,'tools');import generate_hr30_system_package_p01 as s;s.refresh_manifest_and_release()"
    if subprocess.run([str(CAD_PYTHON),"-c",code],cwd=ROOT,check=False).returncode: raise RuntimeError("whole-body refresh failed")


def main() -> int:
    if OUT.exists(): shutil.rmtree(OUT)
    OUT.mkdir(parents=True); items=analog_parts()+slate_parts(); print("measurement boundary: schematic",flush=True); write_schematic(items); print("measurement boundary: PCB",flush=True); info=write_board(items); print("measurement boundary: native validation",flush=True); checks=validate_export(info); print("measurement boundary: CAD",flush=True)
    if subprocess.run([str(CAD_PYTHON),str(ROOT/"tools"/"generate_hr30_measurement_boundary_panel_cad_p01.py")],cwd=ROOT,check=False).returncode: raise RuntimeError("panel CAD generation failed")
    print("measurement boundary: publish/integrate",flush=True); publish(items,info,checks); integrate(); manifest_release(); print(json.dumps({"identifier":IDENTIFIER,"channels":8,"components":len(items),"erc":[0,0],"drc":0,"fer_g11_closed":False,"authorities":0},indent=2)); return 0


if __name__=="__main__": raise SystemExit(main())
