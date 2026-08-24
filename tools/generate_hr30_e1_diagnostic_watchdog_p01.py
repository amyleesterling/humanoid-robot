#!/usr/bin/env python3
"""Generate the HR-30 E1 diagnostic-watchdog adapter P0.1.

This is an ordinary, non-safety watchdog observation board for the controls-
only E1 fixture.  It hard-ties the controller permit input low, observes the
motion heartbeat, and exposes watchdog outputs only at local test pads.  It
cannot switch or enable actuator power and grants no work authority.
"""

from __future__ import annotations

import csv
import hashlib
import html
import importlib.util
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import pcbnew


ROOT = Path(__file__).resolve().parents[1]
WHOLE = ROOT / "hr30" / "whole-body-p0.1"
OUT = WHOLE / "electrical" / "e1-diagnostic-watchdog-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / "electrical" / "e1-diagnostic-watchdog-p0.1"
PROJECT = "hr30-e1-diagnostic-watchdog-p0.1"
IDENTIFIER = "HR30-E1-DIAGNOSTIC-WATCHDOG-P0.1"
DATE = "2026-08-18"
WARNING = "PRELIMINARY - DIAGNOSTIC ONLY - ZERO SAFETY CREDIT - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION OR ENERGIZATION"
AUTHORITY = "NO PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED-TEST, MOTION OR ENERGIZATION AUTHORITY"
KICAD = Path(r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe")
CAD_PYTHON = ROOT.parent / ".venvs" / "hr-v0-cad" / "Scripts" / "python.exe"
FP_ROOT = Path(r"C:\Program Files\KiCad\10.0\share\kicad\footprints")

TI_DATA = "https://www.ti.com/lit/ds/symlink/tps3431.pdf"
TI_PART = "https://www.ti.com/product/TPS3431/part-details/TPS3431SDRBR"
JST_GH = "https://www.jst-mfg.com/product/pdf/eng/eGH.pdf"
BELDEN_1852 = "https://www.belden.com/products/cable/electronic-wire-cable/lead-wire-hook-up-wire/1852"


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


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def load_model():
    path = ROOT / "tools" / "generate_hr_v0_electrical_v3.py"
    spec = importlib.util.spec_from_file_location("hr30_e1_wd_model", path)
    if not spec or not spec.loader:
        raise RuntimeError("cannot load schematic model")
    model = importlib.util.module_from_spec(spec); sys.modules[spec.name] = model; spec.loader.exec_module(model)
    model.OUT = OUT; model.PROJECT = PROJECT; model.REV = "P0.1"; model.DATE = DATE; model.WARNING = WARNING
    model.PROJECT_TITLE = "PROJECT BUTTON HR-30 E1 DIAGNOSTIC WATCHDOG"
    model.PROJECT_SUBTITLE = "TPS3431 heartbeat observation; permit forced low; local outputs only; zero safety credit."
    return model


def parts() -> list[Part]:
    return [
        Part("J1", "controller JIO1 fixture cable", "JST", "BM08B-GHS-TBT", "Connector_JST:JST_GH_BM08B-GHS-TBT_1x08-1MP_P1.25mm_Vertical",
             {"1":"CTRL_GND","2":"CTRL_3V3","3":"CTRL_GND","4":"INTENTIONALLY_NOT_CONNECTED_J1_4","5":"MOTION_WD_HEARTBEAT","6":"INTENTIONALLY_NOT_CONNECTED_J1_6","7":"INTENTIONALLY_NOT_CONNECTED_J1_7","8":"INTENTIONALLY_NOT_CONNECTED_J1_8"}, 5.0, 12.5, 90.0),
        Part("U1", "standard programmable watchdog", "Texas Instruments", "TPS3431SDRBR", "Package_SON:VSON-8-1EP_3x3mm_P0.65mm_EP1.65x2.4mm",
             {"1":"CTRL_3V3","2":"INTENTIONALLY_NOT_CONNECTED_U1_2","3":"CTRL_3V3","4":"CTRL_GND","5":"CTRL_3V3","6":"WD_INPUT","7":"WD_OUTPUT_N","8":"WD_ENOUT","9":"CTRL_GND"}, 22.0, 12.5),
        Part("R1", "1 kOhm heartbeat series", "SELECTION REQUIRED", "SELECTION REQUIRED", "Resistor_SMD:R_0603_1608Metric", {"1":"MOTION_WD_HEARTBEAT","2":"WD_INPUT"}, 28.0, 12.825, 180.0),
        Part("R2", "100 kOhm WDI pulldown", "SELECTION REQUIRED", "SELECTION REQUIRED", "Resistor_SMD:R_0603_1608Metric", {"1":"WD_INPUT","2":"CTRL_GND"}, 28.0, 15.5),
        Part("R5", "100 kOhm WDO pullup", "SELECTION REQUIRED", "SELECTION REQUIRED", "Resistor_SMD:R_0603_1608Metric", {"1":"CTRL_3V3","2":"WD_OUTPUT_N"}, 28.0, 10.5, 180.0),
        Part("R6", "100 kOhm ENOUT pullup", "SELECTION REQUIRED", "SELECTION REQUIRED", "Resistor_SMD:R_0603_1608Metric", {"1":"CTRL_3V3","2":"WD_ENOUT"}, 28.0, 7.5, 180.0),
        Part("C1", "100 nF VDD bypass", "SELECTION REQUIRED", "SELECTION REQUIRED", "Capacitor_SMD:C_0603_1608Metric", {"1":"CTRL_3V3","2":"CTRL_GND"}, 18.0, 8.0),
        Part("TP1", "heartbeat test pad", "PROJECT PAD", "N/A", "TestPoint:TestPoint_Pad_D1.0mm", {"1":"WD_INPUT"}, 25.0, 18.0),
        Part("TP2", "watchdog fault active-low test pad", "PROJECT PAD", "N/A", "TestPoint:TestPoint_Pad_D1.0mm", {"1":"WD_OUTPUT_N"}, 33.0, 10.5),
        Part("TP3", "watchdog enable-output test pad", "PROJECT PAD", "N/A", "TestPoint:TestPoint_Pad_D1.0mm", {"1":"WD_ENOUT"}, 32.0, 5.5),
        Part("TP4", "3V3 test pad", "PROJECT PAD", "N/A", "TestPoint:TestPoint_Pad_D1.0mm", {"1":"CTRL_3V3"}, 34.0, 7.0),
        Part("TP5", "ground test pad", "PROJECT PAD", "N/A", "TestPoint:TestPoint_Pad_D1.0mm", {"1":"CTRL_GND"}, 34.0, 18.0),
    ]


def schematic_component(model, part: Part):
    names = {
        "U1": {"1":"VDD","2":"CWD / NC = 1.6 s nominal","3":"EN","4":"GND","5":"SET1","6":"WDI","7":"WDO active low","8":"ENOUT","9":"EXPOSED PAD / GND"},
        "J1": {"1":"CTRL_GND","2":"CTRL_3V3","3":"PERMIT HARD-LOW","4":"EMPTY","5":"HEARTBEAT","6":"EMPTY","7":"EMPTY","8":"EMPTY"},
    }.get(part.ref, {})
    pins = [model.pn(part.ref, number, names.get(number, number), net, "left" if index % 2 == 0 else "right") for index, (number, net) in enumerate(part.pins.items())]
    positions = {
        "J1": (72, 62), "U1": (208, 62),
        "R1": (332, 48), "R2": (332, 82), "R5": (332, 150), "R6": (332, 184),
        "C1": (208, 218), "TP1": (66, 262), "TP2": (142, 262),
        "TP3": (218, 262), "TP4": (294, 262), "TP5": (370, 262),
    }
    x, y = positions[part.ref]
    return model.Component(part.ref, part.value, pins, "CANDIDATE - PHYSICAL VALIDATION OPEN", "DIAGNOSTIC ONLY; ZERO SAFETY CREDIT", TI_DATA if part.ref == "U1" else JST_GH if part.ref == "J1" else "PROJECT DESIGN", "Exact U1/J1 candidates; passive order codes remain selection required.", position=(x,y), width=84 if part.ref in ("J1","U1") else 52, footprint=part.footprint)


def write_schematic(items: list[Part]) -> None:
    model = load_model(); components = [schematic_component(model, part) for part in items]
    sheet = model.Sheet(1, "01_watchdog_adapter.kicad_sch", "E1 diagnostic heartbeat watchdog", "Permit is physically forced low; WDO and ENOUT remain local test signals; CWD open selects the 1.6 s nominal preset.")
    sheet.components = components
    sheet.notes = [
        "J1.3 hard-ties motion-controller SAFETY_PERMIT_HARDWIRED to CTRL_GND for the E1 fixture.",
        "J1.4, J1.6, J1.7 and J1.8 are physically empty cable contacts and explicit board no-connects.",
        "TPS3431 WDO and ENOUT terminate only at local pullups/test pads; neither can command motion or actuator power.",
        "CWD is deliberately open. TI specifies 1360/1600/1840 ms minimum/typical/maximum with SET1 high.", WARNING,
    ]
    net_counts: dict[str,int] = {}
    for component in components:
        for pin in component.pins: net_counts[pin.net] = net_counts.get(pin.net,0)+1
    wires = model.build_wire_numbers([sheet], net_counts); root_uuid = model.uid("root-hr30-e1-watchdog-p0.1")
    project = {"board":{},"boards":[],"cvpcb":{},"erc":{},"libraries":{},"meta":{"filename":f"{PROJECT}.kicad_pro","version":1},"net_settings":{"classes":[{"name":"Default","priority":2147483647,"clearance":0.15,"track_width":0.20,"via_diameter":0.60,"via_drill":0.30}],"meta":{"version":3}},"pcbnew":{},"schematic":{},"text_variables":{"PROJECT_STATUS":WARNING}}
    (OUT/f"{PROJECT}.kicad_pro").write_text(json.dumps(project,indent=2)+"\n",encoding="utf-8")
    symbols = [model.lib_symbol(c).replace(f'(symbol "PBV3:{c.ref}"',f'(symbol "{c.ref}"',1) for c in components]
    (OUT/f"{PROJECT}.kicad_sym").write_text('(kicad_symbol_lib\n  (version 20251024) (generator "kicad_symbol_editor") (generator_version "10.0")\n  '+"\n".join(symbols)+'\n)\n',encoding="utf-8")
    (OUT/"sym-lib-table").write_text(f'(sym_lib_table\n  (version 7)\n  (lib (name "PBV3")(type "KiCad")(uri "${{KIPRJMOD}}/{PROJECT}.kicad_sym")(options "")(descr "HR-30 E1 diagnostic watchdog symbols"))\n)\n',encoding="utf-8")
    (OUT/f"{PROJECT}.kicad_sch").write_text(model.root_schematic(root_uuid,[sheet]),encoding="utf-8")
    (OUT/sheet.filename).write_text(model.child_schematic(root_uuid,sheet,net_counts,wires),encoding="utf-8")


def footprint(identifier: str):
    library,name = identifier.split(":",1); item = pcbnew.FootprintLoad(str(FP_ROOT/f"{library}.pretty"),name)
    if item is None: raise RuntimeError(f"cannot load {identifier}")
    return item


def pad_xy(fp, number: str) -> tuple[float,float]:
    pads=[p for p in fp.Pads() if p.GetNumber()==number]
    if len(pads)!=1: raise RuntimeError(f"expected one pad {fp.GetReference()}.{number}")
    q=pads[0].GetPosition(); return pcbnew.ToMM(q.x),pcbnew.ToMM(q.y)


def track(board,net,points,width=0.20,layer=pcbnew.F_Cu):
    for a,b in zip(points,points[1:]):
        t=pcbnew.PCB_TRACK(board); t.SetStart(pcbnew.VECTOR2I_MM(*a)); t.SetEnd(pcbnew.VECTOR2I_MM(*b)); t.SetLayer(layer); t.SetWidth(pcbnew.FromMM(width)); t.SetNet(net); board.Add(t)


def via(board,net,point):
    v=pcbnew.PCB_VIA(board); v.SetPosition(pcbnew.VECTOR2I_MM(*point)); v.SetWidth(pcbnew.FromMM(.60)); v.SetDrill(pcbnew.FromMM(.30)); v.SetLayerPair(pcbnew.F_Cu,pcbnew.B_Cu); v.SetNet(net); board.Add(v)


def text(board,value,x,y,size=.75):
    t=pcbnew.PCB_TEXT(board); t.SetText(value); t.SetPosition(pcbnew.VECTOR2I_MM(x,y)); t.SetLayer(pcbnew.F_SilkS); t.SetTextSize(pcbnew.VECTOR2I_MM(size,size)); t.SetTextThickness(pcbnew.FromMM(.15)); board.Add(t)


def write_board(items: list[Part]) -> dict[str,object]:
    board=pcbnew.BOARD(); board.SetCopperLayerCount(2); s=board.GetDesignSettings(); s.SetBoardThickness(pcbnew.FromMM(1.6)); s.m_MinClearance=pcbnew.FromMM(.15); s.m_TrackMinWidth=pcbnew.FromMM(.18); s.m_HoleClearance=pcbnew.FromMM(.20); s.m_HoleToHoleMin=pcbnew.FromMM(.25); s.m_ViasMinSize=pcbnew.FromMM(.55); s.m_MinThroughDrill=pcbnew.FromMM(.25); s.m_ViasMinAnnularWidth=pcbnew.FromMM(.12); s.m_NetSettings.GetDefaultNetclass().SetClearance(pcbnew.FromMM(.15))
    names=("CTRL_GND","CTRL_3V3","MOTION_WD_HEARTBEAT","WD_INPUT","WD_OUTPUT_N","WD_ENOUT")
    nets={}
    for name in names: n=pcbnew.NETINFO_ITEM(board,name); board.Add(n); nets[name]=n
    fps={}
    for part in items:
        fp=footprint(part.footprint); fp.SetReference(part.ref); fp.SetValue(part.mpn); fp.SetPosition(pcbnew.VECTOR2I_MM(part.x,part.y)); fp.SetOrientationDegrees(part.rotation); fp.Reference().SetVisible(False); fp.Value().SetVisible(False)
        for pad in fp.Pads():
            name=part.pins.get(pad.GetNumber(),"")
            if name in nets: pad.SetNet(nets[name])
        board.Add(fp); fps[part.ref]=fp
    for i,point in enumerate(((12,22),(37,22)),1):
        h=footprint("MountingHole:MountingHole_2.7mm_M2.5"); h.SetReference(f"H{i}"); h.SetValue("M2.5 FIXTURE HOLE"); h.SetPosition(pcbnew.VECTOR2I_MM(*point)); h.SetBoardOnly(True); h.SetExcludedFromBOM(True); h.SetExcludedFromPosFiles(True); h.Reference().SetVisible(False); h.Value().SetVisible(False); board.Add(h)
    corners=((0,0),(40,0),(40,25),(0,25))
    for a,b in zip(corners,(*corners[1:],corners[0])):
        e=pcbnew.PCB_SHAPE(board); e.SetShape(pcbnew.SHAPE_T_SEGMENT); e.SetStart(pcbnew.VECTOR2I_MM(*a)); e.SetEnd(pcbnew.VECTOR2I_MM(*b)); e.SetLayer(pcbnew.Edge_Cuts); e.SetWidth(pcbnew.FromMM(.20)); board.Add(e)
    p=lambda r,n: pad_xy(fps[r],n)
    # Heartbeat path runs around the lower perimeter; watchdog-local signals
    # stay in short, separated component-side corridors.
    track(board,nets["MOTION_WD_HEARTBEAT"],[p("J1","5"),(9.0,11.875),(9.0,4.5),(36.0,4.5),(36.0,12.825),p("R1","1")])
    track(board,nets["WD_INPUT"],[p("U1","6"),(25.0,12.825),p("R1","2"),(27.175,15.5),p("R2","1"),(27.175,18.0),p("TP1","1")])
    track(board,nets["WD_OUTPUT_N"],[p("U1","7"),(25.0,12.175),(25.0,10.5),p("R5","2"),(27.175,9.2),(33.0,9.2),p("TP2","1")])
    track(board,nets["WD_ENOUT"],[p("U1","8"),(24.2,11.525),(24.2,7.5),p("R6","2"),(27.175,6.0),(31.0,6.0),p("TP3","1")])
    # Back-plane 3V3 zone; every front-only SMD supply pad receives a short via fanout.
    supply_vias = {
        ("J1","2"):(8.2,15.625), ("U1","1"):(19.2,11.525),
        ("U1","3"):(19.2,12.825), ("U1","5"):(24.8,14.8),
        ("R5","1"):(30.0,10.5), ("R6","1"):(30.0,7.5),
        ("C1","1"):(16.0,8.0), ("TP4","1"):(35.2,7.0),
    }
    for (ref,num),v in supply_vias.items():
        q=p(ref,num); track(board,nets["CTRL_3V3"],[q,v]); via(board,nets["CTRL_3V3"],v)
    for layer,name,margin in ((pcbnew.F_Cu,"CTRL_GND",.5),(pcbnew.B_Cu,"CTRL_3V3",.7)):
        z=pcbnew.ZONE(board); z.SetLayer(layer); z.SetNet(nets[name]); z.SetLocalClearance(pcbnew.FromMM(.18)); z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL); o=z.Outline(); o.NewOutline()
        for q in ((margin,margin),(40-margin,margin),(40-margin,25-margin),(margin,25-margin)): o.Append(pcbnew.VECTOR2I_MM(*q))
        board.Add(z)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    text(board,"E1 WD P0.1",20,23.3,.80); text(board,"DIAGNOSTIC ONLY",20,2.0,.80); text(board,"PERMIT LOW",7.5,20.8,.80)
    directory=OUT/"board"; directory.mkdir(parents=True,exist_ok=True); path=directory/f"{PROJECT}.kicad_pcb"; pcbnew.SaveBoard(str(path),board)
    return {"path":path,"named_nets":len(names),"components":len(items),"vias":8}


def run_cli(args,allowed=(0,)):
    cp=subprocess.run([str(KICAD),*map(str,args)],cwd=OUT,text=True,capture_output=True)
    if cp.returncode not in allowed: raise RuntimeError(f"KiCad failed {cp.returncode}: {' '.join(map(str,args))}\n{cp.stdout}\n{cp.stderr}")
    return cp


def validate_export(info):
    validation=OUT/"validation"; output=OUT/"output"; validation.mkdir(exist_ok=True); output.mkdir(exist_ok=True)
    erc=validation/f"{PROJECT}-erc.rpt"; cp=run_cli(["sch","erc","--exit-code-violations","--output",erc,OUT/f"{PROJECT}.kicad_sch"],(0,5))
    if cp.returncode: raise RuntimeError(erc.read_text(encoding="utf-8"))
    run_cli(["sch","export","svg","--output",output,OUT/f"{PROJECT}.kicad_sch"])
    board=info["path"]; drc=validation/f"{PROJECT}-drc.rpt"; cp=run_cli(["pcb","drc","--severity-all","--exit-code-violations","--output",drc,board],(0,5))
    if cp.returncode: raise RuntimeError(drc.read_text(encoding="utf-8"))
    run_cli(["pcb","export","svg","--mode-single","--output",output/f"{PROJECT}-front.svg","--layers","F.Cu,F.Silkscreen,F.Mask,Edge.Cuts","--fit-page-to-board","--exclude-drawing-sheet",board])
    run_cli(["pcb","export","svg","--mode-single","--output",output/f"{PROJECT}-back.svg","--layers","B.Cu,B.Silkscreen,B.Mask,Edge.Cuts","--mirror","--fit-page-to-board","--exclude-drawing-sheet",board])
    fab=OUT/"fabrication-candidate-not-released"; gerber=fab/"gerber"; drill=fab/"drill"; gerber.mkdir(parents=True,exist_ok=True); drill.mkdir(parents=True,exist_ok=True)
    run_cli(["pcb","export","gerbers","--output",gerber,"--layers","F.Cu,B.Cu,F.Mask,B.Mask,F.Silkscreen,B.Silkscreen,Edge.Cuts","--precision","6","--check-zones",board])
    run_cli(["pcb","export","drill","--output",drill,"--format","excellon","--excellon-units","mm","--generate-map","--map-format","svg","--generate-report","--report-path",drill/f"{PROJECT}-drill-report.rpt",board])
    run_cli(["pcb","export","ipcd356","--output",fab/f"{PROJECT}.d356",board]); run_cli(["pcb","export","pos","--output",fab/f"{PROJECT}-positions.csv","--side","both","--format","csv","--units","mm",board]); run_cli(["pcb","export","stats","--output",fab/f"{PROJECT}-board-stats.json","--format","json","--units","mm",board])
    (fab/"README.txt").write_text(WARNING+"\n\nManufacturing outputs are DFM candidates only and are not released for order.\n",encoding="utf-8")
    for svg in OUT.rglob("*.svg"): svg.write_text("\n".join(line.rstrip() for line in svg.read_text(encoding="utf-8").splitlines())+"\n",encoding="utf-8")
    return {"erc_errors":0,"erc_warnings":0,"drc_violations":0,"unconnected_items":0}


def cable_svg() -> str:
    rows=[("1","BLACK","CTRL_GND","JIO1.1","J1.1"),("2","RED","CTRL_3V3","JIO1.2","J1.2"),("3","BLACK","PERMIT HARD-LOW","JIO1.3","J1.3"),("4","EMPTY","NO CONTACT","JIO1.4","J1.4"),("5","BLUE","HEARTBEAT","JIO1.5","J1.5"),("6","EMPTY","NO CONTACT","JIO1.6","J1.6"),("7","EMPTY","NO CONTACT","JIO1.7","J1.7"),("8","EMPTY","NO CONTACT","JIO1.8","J1.8")]
    colors={"BLACK":"#1f2937","RED":"#c62828","BLUE":"#0b63b6","EMPTY":"#a4aebb"}; lines=[]
    for i,(contact,color,signal,left,right) in enumerate(rows):
        y=150+i*54; dash=' stroke-dasharray="10 9"' if color=="EMPTY" else ""; lines.append(f'<line x1="290" y1="{y}" x2="970" y2="{y}" stroke="{colors[color]}" stroke-width="12"{dash}/><text x="310" y="{y-12}">{contact} {color} - {html.escape(signal)}</text><text x="72" y="{y+6}">{left}</text><text x="1000" y="{y+6}">{right}</text>')
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="1260" height="620" viewBox="0 0 1260 620"><style>text{{font:600 18px system-ui;fill:#12263a}}.h{{font-size:30px;font-weight:900}}.box{{fill:#fff;stroke:#0b4f91;stroke-width:4}}</style><rect width="1260" height="620" fill="#e7f7ff"/><text class="h" x="42" y="44">E1 watchdog fixture cable - 4 of 8 contacts populated</text><text x="42" y="76">Candidate finished length 250 +/- 10 mm. Contacts 4, 6, 7 and 8 are physically empty.</text><rect class="box" x="48" y="104" width="210" height="478" rx="18"/><rect class="box" x="990" y="104" width="220" height="478" rx="18"/>{"".join(lines)}<text x="42" y="610">{html.escape(WARNING)}</text></svg>'


def publish(items,info,checks):
    contacts=[]
    for n in range(1,9):
        state="POPULATED" if n in (1,2,3,5) else "PHYSICALLY EMPTY"
        signal={1:"CTRL_GND",2:"CTRL_3V3",3:"SAFETY_PERMIT_HARDWIRED -> CTRL_GND",4:"PRECHARGE_STATUS / NOT CARRIED",5:"MOTION_WD_HEARTBEAT",6:"PRECHARGE_REQUEST / NOT CARRIED",7:"MOTION_FAULT_DIAGNOSTIC / NOT CARRIED",8:"UNASSIGNED / NOT CARRIED"}[n]
        contacts.append({"contact":n,"controller_endpoint":f"JIO1.{n}","adapter_endpoint":f"J1.{n}","signal_or_disposition":signal,"cable_contact_state":state,"motion_enable_capability":"NONE; CONTACT 3 IS HARD-LOW" if n==3 else "NONE","warning":WARNING})
    write_csv(OUT/"connector-contact-map.csv",list(contacts[0]),contacts)
    circuit=[
        {"reference":p.ref,"item":p.value,"manufacturer":p.manufacturer,"manufacturer_part_number":p.mpn,"quantity":1,"selection_state":"EXACT CANDIDATE" if p.mpn not in ("SELECTION REQUIRED","N/A") else "VALUE/FOOTPRINT DEFINED; ORDER CODE SELECTION REQUIRED" if p.mpn=="SELECTION REQUIRED" else "PROJECT TEST PAD","footprint":p.footprint,"warning":WARNING} for p in items]
    circuit += [{"reference":"CBL1-H1/H2","item":"8-position cable housings","manufacturer":"JST","manufacturer_part_number":"GHR-08V-S","quantity":2,"selection_state":"EXACT CANDIDATE","footprint":"N/A","warning":WARNING},{"reference":"CBL1-C1/C8","item":"GH crimp contacts for four conductors","manufacturer":"JST","manufacturer_part_number":"SSHL-002T-P0.2","quantity":8,"selection_state":"EXACT CANDIDATE; CRIMP PROCESS OPEN","footprint":"N/A","warning":WARNING},{"reference":"CBL1-W1/W4","item":"28 AWG stranded fixture conductors","manufacturer":"Belden","manufacturer_part_number":"1852 BK005 / RD005 / BL005","quantity":4,"selection_state":"EXACT CANDIDATE; LENGTH/PROCESS OPEN","footprint":"N/A","warning":WARNING},{"reference":"PCB1","item":"40 x 25 x 1.6 mm two-layer FR-4 PCB","manufacturer":"SELECTION REQUIRED","manufacturer_part_number":"SELECTION REQUIRED","quantity":1,"selection_state":"NATIVE DESIGN PRESENT; FABRICATOR/FINISH/DFM OPEN","footprint":"N/A","warning":WARNING}]
    write_csv(OUT/"candidate-bom.csv",list(circuit[0]),circuit)
    sources=[
        {"source_id":"WD-S01","manufacturer":"Texas Instruments","document":"TPS3431 datasheet SNVSB66A","revision_date":"July 2018; revised October 2021; accessed 2026-08-18","url":TI_DATA,"verified":"DRB pinout; 1.8-6.5 V; falling-edge WDI; active-low open-drain WDO; 0.1 uF bypass; 1-100 kOhm output pullups; CWD open + SET1 high gives 1360/1600/1840 ms","warning":WARNING},
        {"source_id":"WD-S02","manufacturer":"Texas Instruments","document":"TPS3431SDRBR orderable record","revision_date":"live official product page; accessed 2026-08-18","url":TI_PART,"verified":"exact active orderable candidate TPS3431SDRBR, 3 x 3 mm DRB VSON-8","warning":WARNING},
        {"source_id":"WD-S03","manufacturer":"JST","document":"GH connector catalog","revision_date":"live official catalog; revision not stated; accessed 2026-08-18","url":JST_GH,"verified":"BM08B-GHS-TBT, GHR-08V-S, SSHL-002T-P0.2; 1.25 mm pitch; contact wire range","warning":WARNING},
        {"source_id":"WD-S04","manufacturer":"Belden","document":"1852 product record","revision_date":"Revision 0.119; 2026-06-30; accessed 2026-08-18","url":BELDEN_1852,"verified":"28 AWG stranded tinned copper, 0.89 mm nominal OD, candidate fixture wire family","warning":WARNING},
    ]
    write_csv(OUT/"primary-source-register.csv",list(sources[0]),sources)
    tests=[("WD-T01","Unpowered contact mapping","contacts 1,2,3,5 only; 4,6,7,8 physically empty"),("WD-T02","Permit hard-low","JIO1.3 to CTRL_GND <=0.5 ohm through fixture cable/adapter"),("WD-T03","No motion output","WDO_N and ENOUT have no continuity to JIO1 or actuator interfaces"),("WD-T04","Timeout limits","with approved current-limited 3.3 V only, WDO_N asserts after 1.36-1.84 s without WDI falling edge"),("WD-T05","Heartbeat acceptance","falling edges faster than 1.36 s keep WDO_N inactive"),("WD-T06","Heartbeat loss","removing heartbeat asserts WDO_N for 170-230 ms per TI reset delay"),("WD-T07","Power-cycle fail state","permit remains low throughout all fixture supply transitions"),("WD-T08","Isolation boundary","all actuator carriers, PDUs, field cables and actuators physically absent")]
    write_csv(OUT/"inspection-and-hil-register.csv",["test_id","test","acceptance","result","evidence","warning"],[{"test_id":a,"test":b,"acceptance":c,"result":"NOT EXECUTED","evidence":"REQUIRED","warning":WARNING} for a,b,c in tests])
    holds=[("WD-H01","passive exact order codes","qualified electrical selection for 1 kOhm, 100 kOhm and 100 nF parts"),("WD-H02","independent board review","signed schematic/layout/footprint review against sources"),("WD-H03","fabrication and receiving","fabricated board, received-part identity, dimensional and workmanship evidence"),("WD-H04","fixture cable build","controlled crimp process, contact retention, pull and continuity evidence"),("WD-H05","E1 current-limited supply","approved separately protected logic-only supply and grounding implementation"),("WD-H06","HIL execution","eight inspection/HIL rows executed with raw scope/DMM evidence"),("WD-H07","functional-safety boundary","qualified confirmation that this diagnostic circuit receives zero safety credit and is never used as an actuator permit")]
    write_csv(OUT/"open-holds.csv",["hold_id","unresolved_item","closure_evidence","state","authority","warning"],[{"hold_id":a,"unresolved_item":b,"closure_evidence":c,"state":"OPEN","authority":AUTHORITY,"warning":WARNING} for a,b,c in holds])
    (OUT/"fixture-cable.svg").write_text(cable_svg(),encoding="utf-8")
    fab=[p for p in (OUT/"fabrication-candidate-not-released").rglob("*") if p.is_file()]
    write_csv(OUT/"fabrication-candidate-register.csv",["path","bytes","sha256","release_state","warning"],[{"path":p.relative_to(OUT).as_posix(),"bytes":p.stat().st_size,"sha256":sha(p),"release_state":"CANDIDATE ONLY - NOT RELEASED FOR ORDER","warning":WARNING} for p in sorted(fab)])
    status={"identifier":IDENTIFIER,"date":DATE,"warning":WARNING,"native_kicad_schematic_sheet_count":2,"native_kicad_board":True,"board_dimensions_mm":[40,25,1.6],"copper_layers":2,"component_count":info["components"],"named_net_count":info["named_nets"],"via_count":info["vias"],**checks,"tps3431_exact_candidate_bound":True,"watchdog_timeout_ms":{"minimum":1360,"typical":1600,"maximum":1840},"jio1_populated_contacts":[1,2,3,5],"jio1_physically_empty_contacts":[4,6,7,8],"permit_hard_tied_low":True,"watchdog_outputs_local_only":True,"actuator_interfaces_present":False,"actuator_power_path_present":False,"diagnostic_only":True,"functional_safety_credit":False,"pcb_fabricated":False,"fixture_cable_built":False,"hil_executed":False,"procurement_authority":False,"fabrication_authority":False,"assembly_authority":False,"connection_authority":False,"powered_test_authority":False,"motion_authority":False,"energization_authority":False}
    (OUT/"watchdog-status.json").write_text(json.dumps(status,indent=2)+"\n",encoding="utf-8")
    (OUT/"README.md").write_text(f"# HR-30 E1 diagnostic watchdog P0.1\n\n**{WARNING}**\n\nThis package contains a native KiCad schematic and routed 40 x 25 mm two-layer diagnostic adapter using the exact TI TPS3431SDRBR candidate. It observes MOTION_WD_HEARTBEAT, forces the controller permit input low, and exposes WDO_N/ENOUT only at local test pads. JIO1 contacts 4, 6, 7 and 8 are physically absent from the fixture cable. It contains no actuator interface or actuator-power path.\n\nThe open CWD pin and high SET1 select TI's 1360/1600/1840 ms minimum/typical/maximum preset. Native ERC/DRC validate encoded connectivity only. The board/cable are unbuilt, HIL is unexecuted, the circuit receives zero functional-safety credit, and every work authority remains false.\n",encoding="utf-8")
    (OUT/"index.html").write_text(f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 E1 diagnostic watchdog</title><style>:root{{--deep:#071d36;--blue:#0b4f91;--sky:#dff4ff;--gold:#f2b91d;--paper:#f6fbff;--ink:#142a40;--line:#89c7e8}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.55 system-ui,Segoe UI,sans-serif}}header,main,footer{{padding:clamp(24px,5vw,64px) max(18px,calc((100vw - 1200px)/2))}}header,footer{{background:linear-gradient(135deg,var(--deep),var(--blue));color:#fff}}h1{{font-size:clamp(38px,6vw,68px);line-height:1.04}}h2{{font-size:clamp(28px,4vw,42px)}}.warning{{background:var(--gold);color:#17243a;border:3px solid #805600;padding:16px;font-weight:900}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:17px}}article,.panel{{background:#fff;border:2px solid var(--line);border-radius:16px;padding:19px;margin:18px 0}}.metric{{font-size:clamp(30px,4vw,46px);font-weight:900;color:var(--blue);white-space:nowrap}}.hold{{border-color:#c99200;background:#fff8db}}.viewer{{overflow:auto;border:2px solid var(--line);background:#fff}}object{{display:block;width:100%;min-width:760px;min-height:390px}}a{{color:#075b9b;font-weight:800}}li{{margin:.55rem 0}}@media(max-width:560px){{body{{font-size:16px}}}}</style></head><body><header><div class="warning">{html.escape(WARNING)}</div><h1>A real watchdog board, with no route to motion.</h1><p>The controls-only fixture can now observe heartbeat loss on a routed native board while its permit input remains physically grounded.</p></header><main><section class="grid"><article><div class="metric">40 x 25</div><p>millimetre two-layer board</p></article><article><div class="metric">1.36-1.84 s</div><p>TI specified preset timeout range</p></article><article><div class="metric">4 / 8</div><p>fixture cable contacts populated</p></article><article class="hold"><div class="metric">0</div><p>safety credit or authorized tests</p></article></section><section><h2>Routed board</h2><div class="viewer"><object data="output/{PROJECT}-front.svg" type="image/svg+xml" aria-label="Front copper and silkscreen of the E1 diagnostic watchdog board"></object></div></section><section><h2>Four-conductor fixture cable</h2><div class="viewer"><object data="fixture-cable.svg" type="image/svg+xml" aria-label="Eight-position cable with only contacts one, two, three and five populated"></object></div></section><section class="panel"><h2>Fail-closed signal boundary</h2><ul><li>Contact 3 grounds SAFETY_PERMIT_HARDWIRED.</li><li>Contact 5 carries MOTION_WD_HEARTBEAT through a 1 kOhm series resistor.</li><li>WDO_N and ENOUT terminate only at local pullups and test pads.</li><li>Contacts 4, 6, 7 and 8 are physically empty.</li><li>No actuator connector, PDU or power switching component exists on this board.</li></ul></section><section class="panel"><h2>Engineering source</h2><p><a href="{PROJECT}.kicad_pro">Native KiCad project</a> &middot; <a href="board/{PROJECT}.kicad_pcb">Native PCB</a> &middot; <a href="connector-contact-map.csv">contact map</a> &middot; <a href="candidate-bom.csv">BOM</a> &middot; <a href="inspection-and-hil-register.csv">HIL plan</a> &middot; <a href="validation/{PROJECT}-erc.rpt">ERC</a> &middot; <a href="validation/{PROJECT}-drc.rpt">DRC</a> &middot; <a href="open-holds.csv">open holds</a></p></section></main><footer>{html.escape(WARNING)}</footer></body></html>''',encoding="utf-8")


def integrate():
    status_path=WHOLE/"package-status.json"; status=json.loads(status_path.read_text(encoding="utf-8")); status.update({"e1_diagnostic_watchdog_native_board_present":True,"e1_diagnostic_watchdog_exact_tps3431_candidate":True,"e1_diagnostic_watchdog_permit_hard_low":True,"e1_diagnostic_watchdog_outputs_local_only":True,"e1_diagnostic_watchdog_erc_errors":0,"e1_diagnostic_watchdog_erc_warnings":0,"e1_diagnostic_watchdog_drc_violations":0,"e1_diagnostic_watchdog_fabricated":False,"e1_diagnostic_watchdog_hil_complete":False,"e1_diagnostic_watchdog_safety_credit":False}); status_path.write_text(json.dumps(status,indent=2)+"\n",encoding="utf-8")
    start,end="<!-- HR30-E1-WATCHDOG-P01-START -->","<!-- HR30-E1-WATCHDOG-P01-END -->"
    readme=WHOLE/"README.md"; text=readme.read_text(encoding="utf-8")
    if start in text and end in text: text=text.split(start,1)[0]+text.split(end,1)[1]
    block=f'''{start}\n## E1 diagnostic heartbeat watchdog\n\nThe [interactive diagnostic-watchdog guide](electrical/e1-diagnostic-watchdog-p0.1/index.html) contains a routed **40 x 25 mm native KiCad board** using the exact TPS3431SDRBR candidate. Its four-conductor fixture cable carries only ground, 3.3 V, a hard-low permit and heartbeat. Watchdog outputs remain local. The board/cable are unbuilt, HIL is unexecuted, and the circuit has zero functional-safety or work authority.\n{end}\n'''; readme.write_text(text.rstrip()+"\n\n"+block,encoding="utf-8")
    page=WHOLE/"index.html"; text=page.read_text(encoding="utf-8")
    if start in text and end in text: text=text.split(start,1)[0]+text.split(end,1)[1]
    section=f'''{start}<section id="e1-watchdog"><h2>The controls-only fixture now has a real diagnostic watchdog board</h2><div class="grid"><article class="card pass"><div class="metric">40 x 25</div><p>millimetre native KiCad board with exact TPS3431 candidate.</p></article><article class="card pass"><h3>Permit stays low</h3><p>The fixture hard-grounds the permit input and keeps both watchdog outputs local.</p></article><article class="card hold"><h3>Zero safety credit</h3><p>The board and cable are unbuilt and all HIL, physical validation and work authority remain open.</p></article></div><p><a href="electrical/e1-diagnostic-watchdog-p0.1/index.html">Open the interactive watchdog guide</a>.</p></section>{end}'''
    text=text.replace("</main>",section+"</main>",1); page.write_text(text,encoding="utf-8")


def manifest_release():
    shutil.copy2(Path(__file__),OUT/"watchdog-source.py")
    files=[p for p in OUT.rglob("*") if p.is_file() and p.name!="file-manifest.csv"]
    write_csv(OUT/"file-manifest.csv",["path","bytes","sha256","warning"],[{"path":p.relative_to(OUT).as_posix(),"bytes":p.stat().st_size,"sha256":sha(p),"warning":WARNING} for p in sorted(files)])
    if RELEASE.exists(): shutil.rmtree(RELEASE)
    shutil.copytree(OUT,RELEASE)
    code="import sys;sys.path.insert(0,'tools');import generate_hr30_system_package_p01 as s;s.refresh_manifest_and_release()"
    if subprocess.run([str(CAD_PYTHON),"-c",code],cwd=ROOT,check=False).returncode: raise RuntimeError("whole-body refresh failed")


def main() -> int:
    if OUT.exists(): shutil.rmtree(OUT)
    OUT.mkdir(parents=True); items=parts(); print("E1 watchdog: native schematic",flush=True); write_schematic(items); print("E1 watchdog: routed PCB",flush=True); info=write_board(items); print("E1 watchdog: native validation",flush=True); checks=validate_export(info); print("E1 watchdog: publish/integrate",flush=True); publish(items,info,checks); integrate(); manifest_release(); print(json.dumps({"identifier":IDENTIFIER,"board_mm":[40,25,1.6],"erc":[0,0],"drc":0,"safety_credit":False,"authorities":0},indent=2)); return 0


if __name__=="__main__": raise SystemExit(main())
