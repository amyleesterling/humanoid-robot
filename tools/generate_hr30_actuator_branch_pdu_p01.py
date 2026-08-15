#!/usr/bin/env python3
"""Generate the HR-30 six-channel actuator branch-PDU candidate.

The same editable board is instantiated five times.  Twenty-five channels are
allocated to the whole-body axes and five channels are assembly-DNP spares.
This is a restrained commissioning architecture, not the walking power stage:
TPS259474L blocks reverse current and therefore requires separate regeneration
and clamp closure before any standing or walking work.
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
from collections import Counter
from pathlib import Path

import pcbnew

import generate_hr30_actuator_interface_carriers_p01 as carrier


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "hr30" / "whole-body-p0.1"
OUT = PACKAGE / "electrical" / "actuator-branch-pdu-p0.1"
PROJECT = "hr30-actuator-branch-pdu-p0.1"
IDENTIFIER = "HR30-ACTUATOR-BRANCH-PDU-P0.1"
DATE = "2026-08-15"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION OR ENERGIZATION"
WHOLE_WARNING = "PRELIMINARY - CONFIGURATION AND PACKAGING CAD ONLY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, POWERED TESTING, MOTION, OR ENERGIZATION"
KICAD = Path(r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe")
FP_ROOT = Path(r"C:\Program Files\KiCad\10.0\share\kicad\footprints")
RPW_SOURCE = ROOT / "electrical/kicad/hr-v0-dxl-protection-carrier-p0.3/ProjectButton_RPW.pretty/TI_RPW0010A_HotRodQFN_2x2mm_P0.45mm_TI4225183A_P02.kicad_mod"
RPW_NAME = "TI_RPW0010A_HotRodQFN_2x2mm_P0.45mm_TI4225183A_P02"

TI_DS = "https://www.ti.com/lit/ds/symlink/tps25947.pdf"
TI_PRODUCT = "https://www.ti.com/product/TPS25947"
JST_VH = "https://www.jst-mfg.com/product/pdf/eng/eVH.pdf"
JST_GH = "https://www.jst-mfg.com/product/pdf/eng/eGH.pdf"
PHOENIX = "https://www.phoenixcontact.com/en-us/products/pcb-terminal-block-mkds-5-2-95-1714971"
ROBOTIS = "https://docs.robotis.com/docs/dxl/model_reference/"

Part = carrier.Part


def write_csv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def add(parts: list[Part], *args, **kwargs) -> Part:
    part = Part(*args, **kwargs); parts.append(part); return part


def channel_parts(channel: int, x: float) -> list[Part]:
    c = str(channel)
    vin, vout, gnd = "PDU_12V_IN", f"BRANCH_{c}_12V", "PDU_0V"
    en, ov, pgth, pg, ilm, dvdt = (f"CH{c}_{name}" for name in ("EN", "OV", "PGTH", "PG", "ILM", "DVDT"))
    common = {"board": "PDU"}
    parts: list[Part] = []
    add(parts, "PDU", f"U20{c}", "TPS259474LRPWR circuit-breaker latch-off eFuse", "TPS259474LRPWR", "Texas Instruments", f"ProjectButton_RPW:{RPW_NAME}",
        {"1": en, "2": ov, "3": pg, "4": pgth, "5": vin, "6": vout, "7": dvdt, "8": gnd, "9": ilm, "10": ""}, x, 20.5,
        source=TI_DS, evidence="SLVSFC9C Rev C May 2026; adjustable OVLO; circuit breaker; latch-off; PG/PGTH; reverse blocking")
    add(parts, "PDU", f"J10{c}", f"CHANNEL {c} OUTPUT", "B2P-VH", "JST", "Connector_JST:JST_VH_B2P-VH_1x02_P3.96mm_Vertical",
        {"1": gnd, "2": vout}, x, 3.8, source=JST_VH, evidence="JST VH catalog; B2P-VH header; VHR-2N housing; contact and conductor selection remains controlled")
    specs = (
        (f"R{c}01", "470k 1% UVLO top", "RC0603FR-07470KL", vin, en, x-4.4, 29.0),
        (f"R{c}02", "27.4k 1% UVLO/OVLO middle", "RC0603FR-0727K4L", en, ov, x, 29.0),
        (f"R{c}03", "40.2k 1% OVLO bottom", "RC0603FR-0740K2L", ov, gnd, x+4.4, 29.0),
        (f"R{c}04", "47k 1% PGTH top", "RC0603FR-0747KL", vout, pgth, x-3.0, 25.3),
        (f"R{c}05", "5.76k 1% PGTH bottom", "RC0603FR-075K76L", pgth, gnd, x+3.0, 25.3),
        (f"R{c}06", "ASSEMBLY VARIANT RILM", "1.24k / 1.47k / 3.83k", ilm, gnd, x-3.0, 15.7),
    )
    for ref, value, mpn, n1, n2, px, py in specs:
        add(parts, "PDU", ref, value, mpn, "Yageo candidate", "Resistor_SMD:R_0603_1608Metric", {"1": n1, "2": n2}, px, py, source=TI_DS, evidence="candidate calculation; tolerance and physical threshold test required")
    for ref, value, mpn, n1, n2, px, py in (
        (f"C{c}01", "1uF 25V X7R input", "SELECTION REQUIRED", vin, gnd, x-4.5, 11.5),
        (f"C{c}02", "2x1uF 25V X7R output equivalent", "SELECTION REQUIRED", vout, gnd, x+4.5, 11.5),
        (f"C{c}03", "3.3nF dVdt", "SELECTION REQUIRED", dvdt, gnd, x+3.0, 15.7),
    ):
        add(parts, "PDU", ref, value, mpn, "SELECTION REQUIRED", "Capacitor_SMD:C_0603_1608Metric", {"1": n1, "2": n2}, px, py, source=TI_DS, evidence="TI application equation; voltage bias, tolerance and transient validation open")
    add(parts, "PDU", f"D{c}01", "LOCAL BRANCH CLAMP - DNP", "SELECTION REQUIRED", "SELECTION REQUIRED", "Diode_SMD:D_SMA",
        {"1": gnd, "2": vout}, x, 8.0, fitted=False, source=TI_DS, evidence="placeholder only; pulse energy, clamp voltage and regeneration architecture unresolved")
    return parts


def circuit_parts() -> list[Part]:
    parts: list[Part] = []
    add(parts, "PDU", "J1", "12 V CONTROLLED INPUT", "MKDS 5/2-9.5 1714971", "Phoenix Contact", "TerminalBlock_MetzConnect:TerminalBlock_MetzConnect_Type703_RT10N02HGLU_1x02_P9.52mm_Horizontal",
        {"1": "PDU_0V", "2": "PDU_12V_IN"}, 8.5, 36.0, source=PHOENIX, evidence="Phoenix 1714971 electrical candidate; temporary library outline has exact 9.52 mm pitch but body/holes require vendor-footprint verification")
    ctrl = {"1": "PDU_0V", "2": "PDU_0V"}
    for i in range(1, 7): ctrl[str(i+2)] = f"CH{i}_EN"
    for i in range(1, 7): ctrl[str(i+8)] = f"CH{i}_PG"
    add(parts, "PDU", "J2", "6x DISABLE_OD + 6x PG", "BM14B-GHS-TBT", "JST", "Connector_JST:JST_GH_BM14B-GHS-TBT_1x14-1MP_P1.25mm_Vertical",
        ctrl, 42.0, 36.0, source=JST_GH, evidence="logic/diagnostic only; open-drain disable is not a safety function")
    for channel, x in enumerate((8.0, 21.2, 34.4, 47.6, 60.8, 74.0), 1):
        parts.extend(channel_parts(channel, x))
    return parts


def load_fp(identifier: str):
    library, name = identifier.split(":", 1)
    if library == "ProjectButton_RPW":
        fp = pcbnew.FootprintLoad(str(OUT / "ProjectButton_RPW.pretty"), name)
    else:
        fp = pcbnew.FootprintLoad(str(FP_ROOT / f"{library}.pretty"), name)
    if fp is None: raise RuntimeError(f"cannot load footprint {identifier}")
    return fp


def write_board(parts: list[Part]) -> dict[str, object]:
    board = pcbnew.BOARD(); board.SetCopperLayerCount(6)
    settings = board.GetDesignSettings(); settings.SetBoardThickness(pcbnew.FromMM(1.6))
    settings.m_MinClearance = pcbnew.FromMM(0.10); settings.m_TrackMinWidth = pcbnew.FromMM(0.15)
    settings.m_HoleClearance = pcbnew.FromMM(0.10); settings.m_SolderMaskMinWidth = pcbnew.FromMM(0.10)
    settings.m_HoleToHoleMin = pcbnew.FromMM(0.25); settings.m_ViasMinSize = pcbnew.FromMM(0.35)
    settings.m_MinThroughDrill = pcbnew.FromMM(0.15); settings.m_ViasMinAnnularWidth = pcbnew.FromMM(0.10)
    settings.m_NetSettings.GetDefaultNetclass().SetClearance(pcbnew.FromMM(0.10))
    net_names = sorted({net for p in parts for net in p.pins.values() if net}); nets = {}
    for name in net_names:
        net = pcbnew.NETINFO_ITEM(board, name); board.Add(net); nets[name] = net
    for p in parts:
        fp = load_fp(p.footprint); fp.SetReference(p.ref); fp.SetValue(p.value)
        fp.SetPosition(pcbnew.VECTOR2I_MM(p.x, p.y)); fp.SetOrientationDegrees(p.rotation)
        fp.Reference().SetVisible(False); fp.Value().SetVisible(False); fp.SetDNP(not p.fitted)
        for pad in fp.Pads():
            if p.pins.get(pad.GetNumber()): pad.SetNet(nets[p.pins[pad.GetNumber()]])
        board.Add(fp)
        if p.ref.startswith(("R", "C", "D")): fp.Flip(fp.GetPosition(), False)
    for index, (x, y) in enumerate(((3.0,3.0),(79.0,3.0),(3.0,39.0),(79.0,39.0)), 1):
        hole = carrier.lib_fp("MountingHole:MountingHole_2.7mm_M2.5"); hole.SetReference(f"MH{index}"); hole.SetValue("M2.5 BOARD-ONLY")
        hole.SetPosition(pcbnew.VECTOR2I_MM(x,y)); hole.SetBoardOnly(True); hole.SetExcludedFromBOM(True); hole.SetExcludedFromPosFiles(True); board.Add(hole)
    for a,b in zip(((0,0),(82,0),(82,42),(0,42)),((82,0),(82,42),(0,42),(0,0))):
        edge=pcbnew.PCB_SHAPE(board); edge.SetShape(pcbnew.SHAPE_T_SEGMENT); edge.SetStart(pcbnew.VECTOR2I_MM(*a)); edge.SetEnd(pcbnew.VECTOR2I_MM(*b)); edge.SetLayer(pcbnew.Edge_Cuts); edge.SetWidth(pcbnew.FromMM(.2)); board.Add(edge)
    # P0.1 freezes the exact placed physical topology but deliberately does not
    # invent a high-current route before stackup/current/thermal inputs close.
    # The native PCB therefore carries a visible ratsnest and a fail-closed DRC
    # report; the complete electrical connectivity is in the native schematic.
    routing = {"vias": 0, "routing_complete": False, "routing_method": "PLACEMENT ONLY - HIGH-CURRENT ROUTING HELD OPEN"}
    carrier.add_text(board, "HR-30 6CH BRANCH PDU P0.1", 23, 1.7, .75, pcbnew.B_SilkS)
    carrier.add_text(board, "COMMISSIONING ONLY - REGEN / THERMAL OPEN", 18, 40.2, .7, pcbnew.B_SilkS)
    board_path = OUT / f"{PROJECT}.kicad_pcb"; pcbnew.SaveBoard(str(board_path), board)
    carrier.apply_stackup(board_path)
    return {"path": board_path, "nets": len(net_names), "parts": len(parts), "routing": routing}


def load_model():
    path = ROOT / "tools/generate_hr_v0_electrical_v3.py"
    spec = importlib.util.spec_from_file_location("hr30_pdu_model", path)
    if not spec or not spec.loader: raise RuntimeError("cannot load schematic model")
    model = importlib.util.module_from_spec(spec); sys.modules[spec.name] = model; spec.loader.exec_module(model)
    model.OUT=OUT; model.PROJECT=PROJECT; model.REV="P0.1"; model.DATE=DATE; model.WARNING=WARNING
    model.PROJECT_TITLE="PROJECT BUTTON HR-30 SIX-CHANNEL ACTUATOR BRANCH PDU"
    model.PROJECT_SUBTITLE="Five board instances allocate 25 protected commissioning branches; reverse-energy architecture remains open."
    return model


def write_schematic(parts: list[Part]) -> None:
    model=load_model(); items=[]
    for p in parts:
        pins=[model.pn(p.ref,n,n,net,"left" if i%2==0 else "right") for i,(n,net) in enumerate(p.pins.items()) if net]
        items.append(model.Component(p.ref,p.value,pins,"EXACT CANDIDATE / APPLICATION VALIDATION OPEN",p.evidence,p.source,p.evidence,position=(50,50),width=75,footprint=p.footprint))
    by_ref={i.ref:i for i in items}; sheets=[]
    overview=model.Sheet(1,"01_pdu_boundaries.kicad_sch","PDU input, logic and six branch outputs","Five identical board assemblies provide 30 positions; only 25 are populated by the allocation register.")
    overview.components=[by_ref["J1"],by_ref["J2"]]+[by_ref[f"J10{i}"] for i in range(1,7)]
    for i,item in enumerate(overview.components): item.position=(55+(i%3)*145,50+(i//3)*65); item.width=80
    overview.notes=["J2 DISABLE_OD/PG is ordinary control and diagnostics only; it has zero safety credit.","Branch outputs are local power pairs; actuator data-only harnesses never carry VDD between axes.",WARNING]; sheets.append(overview)
    for c in range(1,7):
        refs=[f"U20{c}"]+[f"R{c}0{i}" for i in range(1,7)]+[f"C{c}0{i}" for i in range(1,4)]+[f"D{c}01"]
        sheet=model.Sheet(c+1,f"{c+1:02d}_channel_{c}.kicad_sch",f"Branch channel {c}","TPS259474L latch-off circuit-breaker commissioning channel")
        sheet.components=[by_ref[r] for r in refs]
        for i,item in enumerate(sheet.components): item.position=(55+(i%3)*145,48+(i//3)*60); item.width=80
        sheet.notes=["ITIMER is deliberately open for fastest circuit-breaker response.","RILM is an assembly variant bound to an axis; never substitute without regenerating the allocation.","Reverse blocking makes this a commissioning circuit only until regeneration/clamp evidence closes.",WARNING]; sheets.append(sheet)
    net_counts=Counter(pin.net for item in items for pin in item.pins); wires=model.build_wire_numbers(sheets,net_counts); root_uuid=model.uid("root-hr30-actuator-branch-pdu-p0.1")
    project={"board":{},"boards":[],"cvpcb":{},"erc":{},"libraries":{},"meta":{"filename":f"{PROJECT}.kicad_pro","version":1},"net_settings":{"classes":[{"name":"Default","priority":2147483647,"clearance":0.1,"track_width":0.18,"via_diameter":0.45,"via_drill":0.2}],"meta":{"version":3}},"pcbnew":{},"schematic":{},"text_variables":{"PROJECT_STATUS":WARNING}}
    (OUT/f"{PROJECT}.kicad_pro").write_text(json.dumps(project,indent=2)+"\n",encoding="utf-8")
    symbols=[model.lib_symbol(i).replace(f'(symbol "PBV3:{i.ref}"',f'(symbol "{i.ref}"',1) for i in items]
    (OUT/f"{PROJECT}.kicad_sym").write_text('(kicad_symbol_lib\n  (version 20251024) (generator "kicad_symbol_editor") (generator_version "10.0")\n  '+"\n".join(symbols)+"\n)\n",encoding="utf-8")
    (OUT/"sym-lib-table").write_text(f'(sym_lib_table\n  (version 7)\n  (lib (name "PBV3")(type "KiCad")(uri "${{KIPRJMOD}}/{PROJECT}.kicad_sym")(options "")(descr "HR-30 branch PDU symbols"))\n)\n',encoding="utf-8")
    (OUT/"fp-lib-table").write_text('(fp_lib_table\n  (version 7)\n  (lib (name "ProjectButton_RPW")(type "KiCad")(uri "${KIPRJMOD}/ProjectButton_RPW.pretty")(options "")(descr "TI RPW package from controlled project source"))\n)\n',encoding="utf-8")
    (OUT/f"{PROJECT}.kicad_sch").write_text(model.root_schematic(root_uuid,sheets),encoding="utf-8")
    for sheet in sheets: (OUT/sheet.filename).write_text(model.child_schematic(root_uuid,sheet,net_counts,wires),encoding="utf-8")


def run_cli(args: list[object], allowed=(0,)) -> subprocess.CompletedProcess[str]:
    done=subprocess.run([str(KICAD),*map(str,args)],cwd=OUT,text=True,capture_output=True)
    if done.returncode not in allowed: raise RuntimeError(f"KiCad CLI failed {done.returncode}: {' '.join(map(str,args))}\n{done.stdout}\n{done.stderr}")
    return done


def validate_export(board: dict[str, object]) -> dict[str, object]:
    val=OUT/"validation"; output=OUT/"output"; val.mkdir(exist_ok=True); output.mkdir(exist_ok=True)
    erc=run_cli(["sch","erc","--exit-code-violations","--output",val/f"{PROJECT}-erc.rpt",OUT/f"{PROJECT}.kicad_sch"],allowed=(0,5))
    run_cli(["sch","export","svg","--output",output,OUT/f"{PROJECT}.kicad_sch"])
    drc=run_cli(["pcb","drc","--severity-all","--exit-code-violations","--output",val/f"{PROJECT}-drc.rpt",board["path"]],allowed=(0,5))
    if erc.returncode: raise RuntimeError("PDU schematic must reach ERC 0/0 before publication")
    for suffix,layers,extra in (("front","F.Cu,F.Silkscreen,F.Mask,Edge.Cuts",[]),("back","B.Cu,B.Silkscreen,B.Mask,Edge.Cuts",["--mirror"])):
        run_cli(["pcb","export","svg","--mode-single","--output",output/f"{PROJECT}-{suffix}.svg","--layers",layers,"--fit-page-to-board","--exclude-drawing-sheet",*extra,board["path"]])
    for layer in ("In1.Cu","In2.Cu","In3.Cu","In4.Cu"):
        run_cli(["pcb","export","svg","--mode-single","--output",output/f"{PROJECT}-{layer.lower().replace('.','-')}.svg","--layers",f"{layer},Edge.Cuts","--fit-page-to-board","--exclude-drawing-sheet",board["path"]])
    for svg in output.rglob("*.svg"): svg.write_text("\n".join(line.rstrip() for line in svg.read_text(encoding="utf-8").splitlines())+"\n",encoding="utf-8")
    (OUT/f"{PROJECT}.kicad_prl").unlink(missing_ok=True)
    report=(val/f"{PROJECT}-drc.rpt").read_text(encoding="utf-8",errors="replace")
    return {"erc_errors":0,"erc_warnings":0,"drc_return_code":drc.returncode,"pcb_layout_state":"PLACED / UNROUTED - DRC NOT ACCEPTED","drc_report_line_count":len(report.splitlines())}


def allocations() -> list[dict[str, object]]:
    axes=list(csv.DictReader((PACKAGE/"actuator-bus-axis-binding.csv").open(encoding="utf-8")))
    groups=[("PDU-LLEG",[a for a in axes if a["bus_id"]=="RS-LLEG"]),("PDU-RLEG",[a for a in axes if a["bus_id"]=="RS-RLEG"]),("PDU-ARMS",[a for a in axes if a["bus_id"] in {"RS-LARM","RS-RARM"}]),("PDU-DISTAL",[a for a in axes if a["bus_id"] in {"TTL-LDIST","TTL-RDIST","TTL-HEAD"}]),("PDU-CORE",[a for a in axes if a["bus_id"]=="RS-WAIST"])]
    rows=[]
    for board_id,members in groups:
        for channel in range(1,7):
            axis=members[channel-1] if channel<=len(members) else None
            family=axis["actuator_family"] if axis else "DNP"
            variant={"XH540":("1.24k","2.689 A nominal; 2.420-2.958 A at stated +/-10% accuracy"),"XM540":("1.24k","2.689 A nominal; 2.420-2.958 A at stated +/-10% accuracy"),"XM430":("1.47k","2.268 A nominal; 2.041-2.495 A at stated +/-10% accuracy"),"XC330":("3.83k","0.871 A nominal; TI does not specify +/-10% below 1 A")}.get(family,("DNP","DNP"))
            rows.append({"board_instance":board_id,"channel":channel,"axis_id":axis["axis_id"] if axis else "DNP SPARE","bus_id":axis["bus_id"] if axis else "DNP","actuator_family":family,"r_ilm_variant":variant[0],"candidate_threshold":variant[1],"population_state":"POPULATE FOR CONTROLLED COMMISSIONING" if axis else "DNP - NO COMPONENT POPULATION","walking_state":"DISABLED - REGENERATION / CONNECTOR / THERMAL / DYNAMIC EVIDENCE OPEN","warning":WARNING})
    return rows


def publish(parts: list[Part], board: dict[str, object], validation: dict[str, object]) -> None:
    alloc=allocations(); write_csv(OUT/"board-instance-channel-allocation.csv",list(alloc[0]),alloc)
    comp=[{"reference":p.ref,"manufacturer":p.manufacturer,"manufacturer_part_number":p.mpn,"value":p.value,"footprint":p.footprint,"fitted_on_bare_six_channel_pattern":"YES" if p.fitted else "NO / DNP","source":p.source,"evidence":p.evidence,"status":"CANDIDATE / PHYSICAL VALIDATION OPEN","warning":WARNING} for p in parts]
    write_csv(OUT/"component-register.csv",list(comp[0]),comp)
    terms=[{"reference":p.ref,"pad":pin,"net":net,"warning":WARNING} for p in parts for pin,net in p.pins.items() if net]
    write_csv(OUT/"terminal-register.csv",list(terms[0]),terms)
    sources=[("TI-TPS25947","Texas Instruments","TPS25947 datasheet","SLVSFC9C Rev C; revised May 2026",TI_DS,"pinout, order code, circuit-breaker/latch-off behavior, equations and layout"),("TI-PRODUCT","Texas Instruments","TPS25947 product page","active; accessed 2026-08-15",TI_PRODUCT,"2.7-23 V, 0.5-6 A, +/-10% ILIM above 1 A, reverse blocking"),("JST-VH","JST","VH connector catalog","live catalog accessed 2026-08-15",JST_VH,"B2P-VH header, VHR-2N housing, SVH contact families"),("JST-GH","JST","GH connector catalog","live catalog accessed 2026-08-15",JST_GH,"BM14B-GHS-TBT logic header candidate"),("PHOENIX-MKDS5","Phoenix Contact","MKDS 5/2-9.5 product page","order 1714971; accessed 2026-08-15",PHOENIX,"32 A input terminal candidate; exact vendor footprint still open"),("ROBOTIS-DXL","ROBOTIS","DYNAMIXEL model reference","live official docs accessed 2026-08-15",ROBOTIS,"actuator families, voltage and published momentary stall endpoints")]
    write_csv(OUT/"primary-source-register.csv",["source_id","manufacturer","document","revision_or_date","url","verified_use"],[{"source_id":a,"manufacturer":b,"document":c,"revision_or_date":d,"url":e,"verified_use":f} for a,b,c,d,e,f in sources])
    consequences=[]
    loads={r["axis_id"]:r for r in csv.DictReader((PACKAGE/"joint-load-screen.csv").open(encoding="utf-8"))}
    endpoint={"XH540":4.9,"XM540":4.4,"XM430":2.3,"XC330":0.88}
    nominal={"XH540":2.6887,"XM540":2.6887,"XM430":2.267,"XC330":0.8705}
    for row in alloc:
        if row["axis_id"]=="DNP SPARE": continue
        load=loads[row["axis_id"]]; fam=row["actuator_family"]
        scaled=float(load["effective_published_stall_endpoint_nm"])*nominal[fam]/endpoint[fam]
        required_text=load["development_endpoint_screen_nm"]
        required=float(required_text) if required_text not in {"SELECTION REQUIRED","N/A",""} else 0.0
        consequences.append({"axis_id":row["axis_id"],"actuator_family":fam,"candidate_nominal_branch_limit_a":f"{nominal[fam]:.4f}","published_12v_stall_current_a":f"{endpoint[fam]:.2f}","current_scaled_momentary_endpoint_nm":f"{scaled:.4f}","static_development_screen_nm":f"{required:.4f}","nominal_static_ratio":f"{scaled/required:.3f}" if required else "N/A","disposition":"STATIC SCREEN ONLY - NOT CONTINUOUS OR DYNAMIC CAPABILITY; WALKING DISABLED","warning":WARNING})
    write_csv(OUT/"current-limit-torque-consequence-register.csv",list(consequences[0]),consequences)
    holds=[
        ("PDU-H01","Exact current threshold at received hardware, resistor tolerance and temperature","measure every populated channel; XC330 is below TI's stated +/-10% range"),("PDU-H02","JST EH 3 A actuator boundary","derive RMS/fault/ambient/bundling/duty/inrush and connector temperature; never use 4.4/4.9 A stall as continuous"),("PDU-H03","Regeneration and reverse energy","TPS259474L blocks reverse current; select and validate a bidirectional walking architecture or measured local clamp/dump path"),("PDU-H04","PCB high-current and thermal layout","independent copper/via/stackup/temperature analysis and physical thermal test"),("PDU-H05","Input and output connector footprint/contact/wire set","vendor drawing, mating hardware, crimp tooling, retention and received inspection"),("PDU-H06","Safety boundary","eFuses and J2 controls have zero functional-safety credit; redundant upstream interruption remains separate"),("PDU-H07","Dynamic torque closure","accepted trajectories, current/torque curves, thermal duty, inertia, disturbance, contact and fall-restraint evidence"),("PDU-H08","Fabrication and commissioning release","independent electrical/layout review, DFM, FAI, unpowered inspection and separately signed test procedure")]
    write_csv(OUT/"open-holds.csv",["hold_id","unresolved_item","closure_evidence","state","warning"],[{"hold_id":a,"unresolved_item":b,"closure_evidence":c,"state":"OPEN - BLOCKS PROCUREMENT/FABRICATION/CONNECTION/POWERED TEST/MOTION/ENERGIZATION","warning":WARNING} for a,b,c in holds])
    status={"identifier":IDENTIFIER,"date":DATE,"warning":WARNING,"native_schematic_sheet_count":8,"board_pattern_count":1,"board_instance_count":5,"channels_per_board":6,"allocated_axis_channels":25,"dnp_spare_channels":5,"component_records":len(parts),"terminal_records":len(terms),"placement_complete":True,"routing_complete":False,"drc_accepted":False,"validation":validation,"commissioning_current_limit_architecture_present":True,"walking_power_architecture_complete":False,"reverse_energy_architecture_complete":False,"connector_current_compatibility_validated":False,"thermal_validated":False,"functional_safety_credit":False,"procurement_authority":False,"fabrication_authority":False,"connection_authority":False,"powered_test_authority":False,"motion_authority":False,"energization_authority":False}
    (OUT/"pdu-status.json").write_text(json.dumps(status,indent=2)+"\n",encoding="utf-8")
    rows="".join(f"<tr><td>{r['board_instance']}</td><td>{r['channel']}</td><td>{r['axis_id']}</td><td>{r['actuator_family']}</td><td>{r['r_ilm_variant']}</td><td>{r['population_state']}</td></tr>" for r in alloc)
    (OUT/"index.html").write_text(f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 branch PDU</title><style>:root{{--navy:#082f58;--blue:#12669f;--sky:#c8ecff;--gold:#f2b928;--paper:#f7fcff}}*{{box-sizing:border-box}}body{{margin:0;color:var(--navy);font:clamp(16px,1.15vw,19px)/1.55 system-ui,sans-serif;background:var(--paper)}}header{{padding:clamp(1.5rem,5vw,4rem);background:linear-gradient(135deg,var(--sky),white);border-bottom:7px solid var(--gold)}}header>div,main{{max-width:1240px;margin:auto}}h1{{font-size:clamp(2.3rem,6vw,5rem);line-height:1.02;max-width:16ch}}h2{{font-size:clamp(1.6rem,3vw,2.8rem)}}main{{padding:2rem clamp(1rem,4vw,3rem) 5rem}}.warning,.hold{{border:3px solid #ad7500;background:#fff0b8;border-radius:14px;padding:1rem;font-weight:800}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,230px),1fr));gap:1rem;margin:2rem 0}}article,.panel{{background:white;border:2px solid var(--blue);border-radius:16px;padding:1.1rem}}article b{{display:block;font-size:clamp(2rem,4vw,3.5rem)}}.board,.table-wrap{{overflow:auto;border:2px solid #83bddb;background:white}}object{{display:block;width:100%;min-width:760px;min-height:430px}}table{{border-collapse:collapse;width:100%;min-width:920px}}th,td{{padding:.8rem;text-align:left;vertical-align:top;border-bottom:1px solid #bdd0dc}}th{{background:var(--navy);color:white}}a{{color:#075d98;font-weight:800}}@media(max-width:650px){{main{{padding:1.2rem .8rem 4rem}}}}</style></head><body><header><div><p class="warning">{html.escape(WARNING)}</p><h1>Every actuator now has a physical branch slot.</h1><p>One editable six-channel KiCad board, five assembly instances, 25 allocated axes and five visibly unpopulated spares.</p></div></header><main><section class="grid"><article><b>25</b>allocated actuator branches</article><article><b>5</b>identical PDU boards</article><article><b>ERC 0/0</b>eight native schematic sheets</article><article><b>Placed PCB</b>high-current routing and DRC acceptance remain open</article></section><div class="hold"><h2>This is not the walking power stage</h2><p>TPS259474L blocks reverse current. It is retained only for restrained, low-energy commissioning. Standing and walking remain disabled until regenerative energy, connector temperature, dynamic torque and upstream interruption are physically validated.</p></div><h2>Native placement candidate</h2><div class="board"><object data="output/{PROJECT}-front.svg" type="image/svg+xml" aria-label="HR-30 six-channel branch PDU placement candidate"></object></div><p>The visible ratsnest is intentional: no high-current copper is released before the stackup/current/thermal inputs close. <a href="{PROJECT}.kicad_pro">Open the KiCad project</a> · <a href="{PROJECT}.kicad_pcb">Open the native PCB</a> · <a href="validation/{PROJECT}-erc.rpt">ERC report</a> · <a href="validation/{PROJECT}-drc.rpt">complete fail-closed DRC report</a></p><h2>Five-board population map</h2><div class="table-wrap"><table><thead><tr><th>Board</th><th>Channel</th><th>Axis</th><th>Family</th><th>RILM</th><th>Population</th></tr></thead><tbody>{rows}</tbody></table></div><h2>Controlled engineering records</h2><div class="panel"><p><a href="board-instance-channel-allocation.csv">channel allocation</a> · <a href="current-limit-torque-consequence-register.csv">torque consequences</a> · <a href="component-register.csv">component register</a> · <a href="terminal-register.csv">terminal register</a> · <a href="primary-source-register.csv">primary sources</a> · <a href="open-holds.csv">open holds</a></p></div></main></body></html>''',encoding="utf-8")
    (OUT/"README.md").write_text(f"# HR-30 actuator branch PDU P0.1\n\n**{WARNING}**\n\nThis package provides one editable six-channel native KiCad schematic and placed PCB candidate. Five assembly instances allocate 25 whole-body actuator branches and retain five DNP spares. Schematic ERC is 0/0. High-current routing and DRC acceptance deliberately remain open until stackup, current and thermal inputs close. It is a restrained commissioning architecture only; reverse energy, connector closure, dynamic torque and all work authority remain open.\n",encoding="utf-8")
    files=[p for p in OUT.rglob("*") if p.is_file() and p.name!="file-manifest.csv"]
    write_csv(OUT/"file-manifest.csv",["path","bytes","sha256","warning"],[{"path":p.relative_to(OUT).as_posix(),"bytes":p.stat().st_size,"sha256":sha(p),"warning":WARNING} for p in sorted(files)])


def update_package() -> None:
    status_path=PACKAGE/"package-status.json"; status=json.loads(status_path.read_text(encoding="utf-8")); status.update({"actuator_branch_pdu_native_schematic_present":True,"actuator_branch_pdu_schematic_sheet_count":8,"actuator_branch_pdu_board_pattern_count":1,"actuator_branch_pdu_board_instance_count":5,"actuator_branch_pdu_allocated_channel_count":25,"actuator_branch_pdu_dnp_spare_count":5,"actuator_branch_pdu_erc_errors":0,"actuator_branch_pdu_erc_warnings":0,"actuator_branch_pdu_placement_complete":True,"actuator_branch_pdu_routing_complete":False,"actuator_branch_pdu_drc_accepted":False,"actuator_branch_pdu_walking_power_architecture_complete":False,"actuator_branch_pdu_energization_authority":False}); status_path.write_text(json.dumps(status,indent=2)+"\n",encoding="utf-8")
    readme=PACKAGE/"README.md"; text=readme.read_text(encoding="utf-8"); start,end="<!-- HR30-PDU-P01-START -->","<!-- HR30-PDU-P01-END -->"
    if start in text and end in text: text=text.split(start,1)[0]+text.split(end,1)[1]
    section=f"\n{start}\n## Twenty-five physical actuator branch slots\n\nFive instances of one editable six-channel native KiCad PDU candidate allocate all 25 axes and retain five assembly-DNP spares. The eight-sheet schematic validates at ERC 0/0; the native PCB freezes placement while high-current routing and DRC acceptance remain openly held. Each populated channel uses a TPS259474L circuit-breaker/latch-off eFuse with an axis-bound RILM variant, individual output pair, open-drain disable input and power-good output. This is a restrained commissioning architecture only: the device blocks reverse current, so regeneration/clamp, connector temperature, dynamic torque, copper/thermal validation and every powered-work authority remain open. Open `electrical/actuator-branch-pdu-p0.1/index.html`.\n{end}\n"
    readme.write_text(text.rstrip()+section,encoding="utf-8")
    page=PACKAGE/"index.html"; text=page.read_text(encoding="utf-8")
    if start in text and end in text: text=text.split(start,1)[0]+text.split(end,1)[1]
    web=f'''{start}<section id="actuator-branch-pdu"><h2>Every actuator now has a physical protected branch slot</h2><div class="grid"><article class="card pass"><div class="metric">25</div><p>axis-bound commissioning branches across five board instances.</p></article><article class="card pass"><div class="metric">5</div><p>assembly-DNP spare channels remain visibly unpopulated.</p></article><article class="card pass"><h3>ERC 0 / 0</h3><p>Eight editable, connected native schematic sheets.</p></article><article class="card hold"><h3>PCB routing open</h3><p>High-current copper, DRC acceptance, regeneration and thermal proof remain open.</p></article></div><div class="viewer"><object data="electrical/actuator-branch-pdu-p0.1/output/{PROJECT}-front.svg" type="image/svg+xml" aria-label="Six-channel HR-30 actuator branch PDU placement candidate"></object><p><a href="electrical/actuator-branch-pdu-p0.1/index.html">Open the interactive PDU guide</a> · <a href="electrical/actuator-branch-pdu-p0.1/board-instance-channel-allocation.csv">25-axis allocation</a> · <a href="electrical/actuator-branch-pdu-p0.1/{PROJECT}.kicad_pro">native KiCad project</a>.</p></div></section>{end}'''
    marker="<!-- HR30-CARRIERS-P01-END -->"
    if marker not in text: raise RuntimeError("carrier marker missing")
    page.write_text(text.replace(marker,marker+web),encoding="utf-8")
    files=[p for p in PACKAGE.rglob("*") if p.is_file() and p!=PACKAGE/"file-manifest.csv"]
    write_csv(PACKAGE/"file-manifest.csv",["path","bytes","sha256","warning"],[{"path":p.relative_to(PACKAGE).as_posix(),"bytes":p.stat().st_size,"sha256":sha(p),"warning":WHOLE_WARNING} for p in sorted(files)])
    release=ROOT/"release/hr30/whole-body-p0.1"
    release_pdu=release/"electrical/actuator-branch-pdu-p0.1"
    if release_pdu.exists(): shutil.rmtree(release_pdu)
    for path in PACKAGE.rglob("*"):
        if path.is_file():
            target=release/path.relative_to(PACKAGE); target.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(path,target)


def main() -> None:
    if OUT.exists(): shutil.rmtree(OUT)
    OUT.mkdir(parents=True); pretty=OUT/"ProjectButton_RPW.pretty"; pretty.mkdir(); shutil.copy2(RPW_SOURCE,pretty/RPW_SOURCE.name)
    parts=circuit_parts(); write_schematic(parts); board=write_board(parts); validation=validate_export(board); publish(parts,board,validation); update_package()
    print(json.dumps({"parts":len(parts),"nets":board["nets"],"vias":board["routing"]["vias"],"validation":validation},indent=2))


if __name__ == "__main__": main()
