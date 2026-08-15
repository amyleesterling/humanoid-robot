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
import heapq
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
        {"1": en, "2": ov, "3": pg, "4": pgth, "5": vin, "6": vout, "7": dvdt, "8": gnd, "9": ilm, "10": ""}, x, 37.0,
        source=TI_DS, evidence="SLVSFC9C Rev C May 2026; adjustable OVLO; circuit breaker; latch-off; PG/PGTH; reverse blocking")
    add(parts, "PDU", f"J10{c}", f"CHANNEL {c} OUTPUT", "B2P-VH", "JST", "Connector_JST:JST_VH_B2P-VH_1x02_P3.96mm_Vertical",
        {"1": gnd, "2": vout}, x, 6.0, source=JST_VH, evidence="JST VH catalog; B2P-VH header; VHR-2N housing; contact and conductor selection remains controlled")
    add(parts, "PDU", f"J20{c}", f"CHANNEL {c} CONTROL", "BM03B-GHS-TBT", "JST", "Connector_JST:JST_GH_BM03B-GHS-TBT_1x03-1MP_P1.25mm_Vertical",
        {"1": gnd, "2": en, "3": pg}, x, 70.0, source=JST_GH, evidence="per-channel GND / open-drain DISABLE / PG service boundary; zero safety credit")
    specs = (
        (f"R{c}01", "470k 1% UVLO top", "RC0603FR-07470KL", vin, en, x-5.0, 49.0),
        (f"R{c}02", "27.4k 1% UVLO/OVLO middle", "RC0603FR-0727K4L", en, ov, x, 49.0),
        (f"R{c}03", "40.2k 1% OVLO bottom", "RC0603FR-0740K2L", ov, gnd, x+5.0, 49.0),
        (f"R{c}04", "47k 1% PGTH top", "RC0603FR-0747KL", vout, pgth, x-3.5, 43.5),
        (f"R{c}05", "5.76k 1% PGTH bottom", "RC0603FR-075K76L", pgth, gnd, x+3.5, 43.5),
        (f"R{c}06", "ASSEMBLY VARIANT RILM", "1.24k / 1.47k / 3.83k", ilm, gnd, x-3.5, 30.5),
    )
    for ref, value, mpn, n1, n2, px, py in specs:
        add(parts, "PDU", ref, value, mpn, "Yageo candidate", "Resistor_SMD:R_0603_1608Metric", {"1": n1, "2": n2}, px, py, source=TI_DS, evidence="candidate calculation; tolerance and physical threshold test required")
    for ref, value, mpn, n1, n2, px, py in (
        (f"C{c}01", "1uF 25V X7R input", "SELECTION REQUIRED", vin, gnd, x-5.0, 24.0),
        (f"C{c}02", "2x1uF 25V X7R output equivalent", "SELECTION REQUIRED", vout, gnd, x+5.0, 24.0),
        (f"C{c}03", "3.3nF dVdt", "SELECTION REQUIRED", dvdt, gnd, x+3.5, 30.5),
    ):
        add(parts, "PDU", ref, value, mpn, "SELECTION REQUIRED", "Capacitor_SMD:C_0603_1608Metric", {"1": n1, "2": n2}, px, py, source=TI_DS, evidence="TI application equation; voltage bias, tolerance and transient validation open")
    add(parts, "PDU", f"D{c}01", "LOCAL BRANCH CLAMP - DNP", "SELECTION REQUIRED", "SELECTION REQUIRED", "Diode_SMD:D_SMA",
        {"1": gnd, "2": vout}, x, 14.0, fitted=False, source=TI_DS, evidence="placeholder only; pulse energy, clamp voltage and regeneration architecture unresolved")
    return parts


def circuit_parts() -> list[Part]:
    parts: list[Part] = []
    add(parts, "PDU", "J1", "12 V CONTROLLED INPUT", "MKDS 5/2-9.5 1714971", "Phoenix Contact", "TerminalBlock_MetzConnect:TerminalBlock_MetzConnect_Type703_RT10N02HGLU_1x02_P9.52mm_Horizontal",
        {"1": "PDU_0V", "2": "PDU_12V_IN"}, 140.0, 58.0, 90.0, source=PHOENIX, evidence="Phoenix 1714971 electrical candidate; temporary library outline has exact 9.52 mm pitch but body/holes require vendor-footprint verification")
    for channel, x in enumerate((16.0, 36.0, 56.0, 76.0, 96.0, 116.0), 1):
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


def add_via(board: pcbnew.BOARD, net: pcbnew.NETINFO_ITEM, point: tuple[float, float], diameter: float=.35, drill: float=.15) -> None:
    via=pcbnew.PCB_VIA(board); via.SetPosition(pcbnew.VECTOR2I_MM(*point)); via.SetWidth(pcbnew.FromMM(diameter)); via.SetDrill(pcbnew.FromMM(drill)); via.SetLayerPair(pcbnew.F_Cu,pcbnew.B_Cu); via.SetNet(net)
    via.SetFrontTentingMode(True); via.SetBackTentingMode(True); board.Add(via)


def route_board(board: pcbnew.BOARD, nets: dict[str, pcbnew.NETINFO_ITEM]) -> dict[str, object]:
    """Route every non-ground net on a dedicated family layer.

    This is deliberately a small, deterministic maze router rather than an
    interactive or unconstrained autorouter.  Each signal family owns one
    internal layer; the shared input and six independent outputs own two more.
    Foreign through-vias and through-hole pads are treated as all-layer
    obstacles.  The resulting ten-layer topology is a manufacturable routing
    candidate, while copper weight, thermal rise and production stackup remain
    explicit selections rather than implied approvals.
    """
    layer_for={"PDU_12V_IN":pcbnew.In1_Cu}
    for c in range(1,7):
        layer_for.update({
            f"BRANCH_{c}_12V":pcbnew.In2_Cu,
            f"CH{c}_EN":pcbnew.In3_Cu,
            f"CH{c}_PG":pcbnew.In4_Cu,
            f"CH{c}_OV":pcbnew.In5_Cu,
            f"CH{c}_PGTH":pcbnew.In6_Cu,
            f"CH{c}_DVDT":pcbnew.In7_Cu,
            f"CH{c}_ILM":pcbnew.In8_Cu,
        })

    pad_records=[]; pads_by_net={name:[] for name in nets}; via_points=[]
    for fp in board.GetFootprints():
        center=fp.GetPosition(); cx,cy=pcbnew.ToMM(center.x),pcbnew.ToMM(center.y)
        # HotRod QFN pins contain more than one copper primitive per logical
        # pad number.  Route only the farthest primitive; the primitives are
        # already joined inside the footprint.
        selected={}
        for pad in fp.Pads():
            name=pad.GetNetname(); number=pad.GetNumber()
            if not name: continue
            pos=pad.GetPosition(); px,py=pcbnew.ToMM(pos.x),pcbnew.ToMM(pos.y)
            key=(number,name)
            if key not in selected or (px-cx)**2+(py-cy)**2 > selected[key][0]:
                selected[key]=((px-cx)**2+(py-cy)**2,pad)
        for _,pad in selected.values():
            name=pad.GetNetname(); pos=pad.GetPosition(); px,py=pcbnew.ToMM(pos.x),pcbnew.ToMM(pos.y)
            bbox=pad.GetBoundingBox(); bounds=(pcbnew.ToMM(bbox.GetX()),pcbnew.ToMM(bbox.GetY()),pcbnew.ToMM(bbox.GetRight()),pcbnew.ToMM(bbox.GetBottom()))
            pad_records.append({"net":name,"ref":fp.GetReference(),"pad":pad.GetNumber(),"point":(px,py),"bounds":bounds,"th":pad.IsOnLayer(pcbnew.F_Cu) and pad.IsOnLayer(pcbnew.B_Cu)})

    def clear_of_pads(point, net_name, margin=.28):
        x,y=point
        for record in pad_records:
            if record["net"]==net_name: continue
            l,t,r,b=record["bounds"]
            if l-margin <= x <= r+margin and t-margin <= y <= b+margin: return False
        return True

    access={name:[] for name in nets}; fanouts=0; via_count=0
    for record in pad_records:
        name=record["net"]; px,py=record["point"]
        if record["th"]:
            access[name].append((px,py)); continue
        fp=next(item for item in board.GetFootprints() if item.GetReference()==record["ref"])
        center=fp.GetPosition(); cx,cy=pcbnew.ToMM(center.x),pcbnew.ToMM(center.y)
        if str(record["ref"]).startswith("J20"):
            ux,uy=0.0,-1.0
        elif str(record["ref"]).startswith("U20") and str(record["pad"]) in {"5","6"}:
            # Drive the two high-current center pads away from the four
            # fine-pitch control pads on their package sides.  VIN exits north
            # and VOUT south before reaching their dedicated internal layers.
            ux,uy=(0.0,1.0) if str(record["pad"])=="5" else (0.0,-1.0)
        else:
            dx,dy=px-cx,py-cy
            if abs(dx)+abs(dy)<.001: ux,uy=0.0,-1.0
            else:
                mag=(dx*dx+dy*dy)**.5; ux,uy=dx/mag,dy/mag
        base=1.70 if str(record["ref"]).startswith("U20") else 1.05
        accepted=None
        for step in range(18):
            distance=base+.20*step
            candidate=(round((px+ux*distance)*4)/4,round((py+uy*distance)*4)/4)
            if not (1.0<candidate[0]<149.0 and 1.0<candidate[1]<77.0): continue
            if not clear_of_pads(candidate,name): continue
            if any((candidate[0]-x)**2+(candidate[1]-y)**2 < .55**2 for x,y,_ in via_points): continue
            accepted=candidate; break
        if accepted is None: raise RuntimeError(f"no escape for {record['ref']}.{record['pad']} [{name}]")
        fanout_width=.10 if str(record["ref"]).startswith("U20") else .15
        carrier.add_track(board,nets[name],(px,py),accepted,pcbnew.F_Cu,fanout_width); fanouts+=1
        add_via(board,nets[name],accepted,.45,.20); via_count+=1; via_points.append((*accepted,name))
        access[name].append(accepted)

    # Ground needs no signal route: every SMD ground pad has a tented through
    # via into filled front/back planes, and all through-hole returns touch the
    # planes directly.
    route_names=[name for name,points in access.items() if name!="PDU_0V" and len(points)>1]
    grid=.25; x0=y0=1.0; nx=int((149.0-x0)/grid)+1; ny=int((77.0-y0)/grid)+1
    mounting=((4.0,4.0),(146.0,4.0),(4.0,74.0),(146.0,74.0))
    foreign_vias=[(x,y,name) for x,y,name in via_points]

    def point(cell): return (x0+cell[0]*grid,y0+cell[1]*grid)
    def cell_for(p): return (round((p[0]-x0)/grid),round((p[1]-y0)/grid))
    def segment_distance(p,a,b):
        px,py=p; ax,ay=a; bx,by=b; dx,dy=bx-ax,by-ay
        if dx==dy==0: return ((px-ax)**2+(py-ay)**2)**.5
        q=max(0,min(1,((px-ax)*dx+(py-ay)*dy)/(dx*dx+dy*dy)))
        return ((px-(ax+q*dx))**2+(py-(ay+q*dy))**2)**.5

    occupied={layer:{} for layer in set(layer_for.values())}
    def available(cell,name,width):
        ix,iy=cell
        if not (0<=ix<nx and 0<=iy<ny): return False
        x,y=point(cell); radius=.225+width/2+.10
        if not (1.0+width/2<=x<=149.0-width/2 and 1.0+width/2<=y<=77.0-width/2): return False
        if any((x-hx)**2+(y-hy)**2 < (1.55+width/2)**2 for hx,hy in mounting): return False
        if any(other!=name and (x-vx)**2+(y-vy)**2 < radius**2 for vx,vy,other in foreign_vias): return False
        for record in pad_records:
            if record["net"]==name or not record["th"]: continue
            l,t,r,b=record["bounds"]
            if l-.10-width/2<=x<=r+.10+width/2 and t-.10-width/2<=y<=b+.10+width/2: return False
        return occupied[layer_for[name]].get(cell) in (None,name)

    def path_to_tree(start,tree,name,width):
        if start in tree: return [start]
        frontier=[(0,0,start)]; parent={start:None}; cost={start:0}; serial=1
        xs=[c[0] for c in tree]; ys=[c[1] for c in tree]
        def h(c): return max(min(xs)-c[0],0,c[0]-max(xs))+max(min(ys)-c[1],0,c[1]-max(ys))
        while frontier:
            _,_,cell=heapq.heappop(frontier)
            if cell in tree:
                out=[cell]
                while parent[out[-1]] is not None: out.append(parent[out[-1]])
                out.reverse(); return out
            for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
                nxt=(cell[0]+dx,cell[1]+dy)
                if not available(nxt,name,width): continue
                new=cost[cell]+1
                if new>=cost.get(nxt,10**12): continue
                cost[nxt]=new; parent[nxt]=cell
                heapq.heappush(frontier,(new+h(nxt),serial,nxt)); serial+=1
        raise RuntimeError(f"no deterministic route for {name} from {point(start)}")

    segments=0
    for name in sorted(route_names,key=lambda n:(0 if n=="PDU_12V_IN" else 1 if n.startswith("BRANCH") else 2,n)):
        width=1.00 if name=="PDU_12V_IN" else .80 if name.startswith("BRANCH") else .15
        layer=layer_for[name]; endpoints=[cell_for(p) for p in access[name]]
        root=endpoints[0]
        if not available(root,name,width): raise RuntimeError(f"blocked root for {name}")
        tree={root}; occupied[layer][root]=name
        carrier.add_track(board,nets[name],access[name][0],point(root),layer,width); segments+=1
        for exact,target in zip(access[name][1:],endpoints[1:]):
            if not available(target,name,width):
                candidates=[(dx*dx+dy*dy,(target[0]+dx,target[1]+dy)) for dx in range(-8,9) for dy in range(-8,9)]
                target=next(cell for _,cell in sorted(candidates) if available(cell,name,width))
            path=path_to_tree(target,tree,name,width)
            carrier.add_track(board,nets[name],exact,point(path[0]),layer,width); segments+=1
            # Collapse collinear grid edges into physical segments.
            run_start=path[0]; direction=None
            for index in range(1,len(path)+1):
                new_direction=None if index==len(path) else (path[index][0]-path[index-1][0],path[index][1]-path[index-1][1])
                if direction is None: direction=new_direction
                if index==len(path) or new_direction!=direction:
                    carrier.add_track(board,nets[name],point(run_start),point(path[index-1]),layer,width); segments+=1
                    run_start=path[index-1]; direction=new_direction
            for cell in path: occupied[layer][cell]=name; tree.add(cell)
    return {"vias":via_count,"fanouts":fanouts,"segments":segments,"routing_complete":True,"routing_method":"ten-layer deterministic family-separated obstacle-aware route","routing_grid_mm":grid}


def add_ground_zones(board: pcbnew.BOARD, net: pcbnew.NETINFO_ITEM) -> None:
    for layer in (pcbnew.F_Cu,pcbnew.B_Cu):
        zone=pcbnew.ZONE(board); zone.SetLayer(layer); zone.SetNet(net); zone.SetLocalClearance(pcbnew.FromMM(.20)); zone.SetMinThickness(pcbnew.FromMM(.254)); zone.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
        polygon=zone.Outline(); polygon.NewOutline()
        for point in ((.8,.8),(149.2,.8),(149.2,77.2),(.8,77.2)): polygon.Append(pcbnew.VECTOR2I_MM(*point))
        board.Add(zone)


def write_board(parts: list[Part]) -> dict[str, object]:
    board = pcbnew.BOARD(); board.SetCopperLayerCount(10)
    settings = board.GetDesignSettings(); settings.SetBoardThickness(pcbnew.FromMM(1.6))
    settings.m_MinClearance = pcbnew.FromMM(0.10); settings.m_TrackMinWidth = pcbnew.FromMM(0.10)
    settings.m_HoleClearance = pcbnew.FromMM(0.10); settings.m_SolderMaskMinWidth = pcbnew.FromMM(0.00)
    settings.m_HoleToHoleMin = pcbnew.FromMM(0.25); settings.m_ViasMinSize = pcbnew.FromMM(0.45)
    settings.m_MinThroughDrill = pcbnew.FromMM(0.20); settings.m_ViasMinAnnularWidth = pcbnew.FromMM(0.10)
    settings.m_NetSettings.GetDefaultNetclass().SetClearance(pcbnew.FromMM(0.10))
    net_names = sorted({net for p in parts for net in p.pins.values() if net}); nets = {}
    for name in net_names:
        net = pcbnew.NETINFO_ITEM(board, name); board.Add(net); nets[name] = net
    for p in parts:
        fp = load_fp(p.footprint); fp.SetReference(p.ref); fp.SetValue(p.value)
        fp.SetPosition(pcbnew.VECTOR2I_MM(p.x, p.y)); fp.SetOrientationDegrees(p.rotation)
        fp.Reference().SetVisible(False); fp.Value().SetVisible(False); fp.SetDNP(not p.fitted)
        if p.ref.startswith("U20"):
            # Preserve a real mask web around the 0.45 mm-pitch HotRod pads.
            # This is a controlled solder-mask-defined candidate and still
            # requires board-fabricator DFM acceptance before release.
            for pad in fp.Pads():
                if pad.GetNumber(): pad.SetLocalSolderMaskMargin(pcbnew.FromMM(-0.025))
        for pad in fp.Pads():
            if p.pins.get(pad.GetNumber()): pad.SetNet(nets[p.pins[pad.GetNumber()]])
        board.Add(fp)
    for index, (x, y) in enumerate(((4.0,4.0),(146.0,4.0),(4.0,74.0),(146.0,74.0)), 1):
        hole = carrier.lib_fp("MountingHole:MountingHole_2.7mm_M2.5"); hole.SetReference(f"MH{index}"); hole.SetValue("M2.5 BOARD-ONLY")
        hole.SetPosition(pcbnew.VECTOR2I_MM(x,y)); hole.SetBoardOnly(True); hole.SetExcludedFromBOM(True); hole.SetExcludedFromPosFiles(True); hole.Reference().SetVisible(False); hole.Value().SetVisible(False); board.Add(hole)
    for a,b in zip(((0,0),(150,0),(150,78),(0,78)),((150,0),(150,78),(0,78),(0,0))):
        edge=pcbnew.PCB_SHAPE(board); edge.SetShape(pcbnew.SHAPE_T_SEGMENT); edge.SetStart(pcbnew.VECTOR2I_MM(*a)); edge.SetEnd(pcbnew.VECTOR2I_MM(*b)); edge.SetLayer(pcbnew.Edge_Cuts); edge.SetWidth(pcbnew.FromMM(.2)); board.Add(edge)
    routing = route_board(board,nets)
    add_ground_zones(board,nets["PDU_0V"]); pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    carrier.add_text(board, "HR-30 6CH BRANCH PDU P0.1", 42, 2.0, .90, pcbnew.B_SilkS)
    carrier.add_text(board, "COMMISSIONING ONLY - REGEN / THERMAL OPEN", 39, 76.0, .82, pcbnew.B_SilkS)
    board_path = OUT / f"{PROJECT}.kicad_pcb"; pcbnew.SaveBoard(str(board_path), board)
    # A production ten-layer buildup is intentionally not inferred from the
    # earlier six-layer carrier candidate.  Exact foil weights, dielectric
    # construction and finished thickness remain STACKUP SELECTION REQUIRED.
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
    overview.components=[by_ref["J1"]]+[by_ref[f"J20{i}"] for i in range(1,7)]+[by_ref[f"J10{i}"] for i in range(1,7)]
    for i,item in enumerate(overview.components): item.position=(55+(i%3)*145,50+(i//3)*65); item.width=80
    overview.notes=["Each J20x GND/DISABLE_OD/PG boundary is ordinary control and diagnostics only; it has zero safety credit.","Branch outputs are local power pairs; actuator data-only harnesses never carry VDD between axes.",WARNING]; sheets.append(overview)
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
    if drc.returncode: raise RuntimeError("PDU PCB must reach DRC 0/0 before routed-candidate publication")
    for suffix,layers,extra in (("front","F.Cu,F.Silkscreen,F.Mask,Edge.Cuts",[]),("back","B.Cu,B.Silkscreen,B.Mask,Edge.Cuts",["--mirror"])):
        run_cli(["pcb","export","svg","--mode-single","--output",output/f"{PROJECT}-{suffix}.svg","--layers",layers,"--fit-page-to-board","--exclude-drawing-sheet",*extra,board["path"]])
    for layer in tuple(f"In{i}.Cu" for i in range(1,9)):
        run_cli(["pcb","export","svg","--mode-single","--output",output/f"{PROJECT}-{layer.lower().replace('.','-')}.svg","--layers",f"{layer},Edge.Cuts","--fit-page-to-board","--exclude-drawing-sheet",board["path"]])
    for svg in output.rglob("*.svg"): svg.write_text("\n".join(line.rstrip() for line in svg.read_text(encoding="utf-8").splitlines())+"\n",encoding="utf-8")
    (OUT/f"{PROJECT}.kicad_prl").unlink(missing_ok=True)
    report=(val/f"{PROJECT}-drc.rpt").read_text(encoding="utf-8",errors="replace")
    return {"erc_errors":0,"erc_warnings":0,"drc_return_code":0,"drc_violations":0,"unconnected_pads":0,"pcb_layout_state":"ROUTED CANDIDATE - DRC 0/0 - PHYSICAL VALIDATION OPEN","drc_report_line_count":len(report.splitlines())}


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
    status={"identifier":IDENTIFIER,"date":DATE,"warning":WARNING,"native_schematic_sheet_count":8,"board_pattern_count":1,"board_instance_count":5,"channels_per_board":6,"allocated_axis_channels":25,"dnp_spare_channels":5,"component_records":len(parts),"terminal_records":len(terms),"board_width_mm":150.0,"board_height_mm":78.0,"copper_layer_count":10,"placement_complete":True,"routing_complete":True,"drc_accepted":True,"routing":board["routing"],"production_stackup_selected":False,"validation":validation,"commissioning_current_limit_architecture_present":True,"walking_power_architecture_complete":False,"reverse_energy_architecture_complete":False,"connector_current_compatibility_validated":False,"thermal_validated":False,"functional_safety_credit":False,"procurement_authority":False,"fabrication_authority":False,"connection_authority":False,"powered_test_authority":False,"motion_authority":False,"energization_authority":False}
    (OUT/"pdu-status.json").write_text(json.dumps(status,indent=2)+"\n",encoding="utf-8")
    rows="".join(f"<tr><td>{r['board_instance']}</td><td>{r['channel']}</td><td>{r['axis_id']}</td><td>{r['actuator_family']}</td><td>{r['r_ilm_variant']}</td><td>{r['population_state']}</td></tr>" for r in alloc)
    layers="".join(f'<article><h3>Internal copper {i}</h3><div class="board"><object data="output/{PROJECT}-in{i}-cu.svg" type="image/svg+xml" aria-label="HR-30 PDU internal copper layer {i}"></object></div></article>' for i in range(1,9))
    (OUT/"index.html").write_text(f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 branch PDU</title><style>:root{{--navy:#082f58;--blue:#12669f;--sky:#c8ecff;--gold:#f2b928;--paper:#f7fcff}}*{{box-sizing:border-box}}body{{margin:0;color:var(--navy);font:clamp(16px,1.15vw,19px)/1.55 system-ui,sans-serif;background:var(--paper)}}header{{padding:clamp(1.5rem,5vw,4rem);background:linear-gradient(135deg,var(--sky),white);border-bottom:7px solid var(--gold)}}header>div,main{{max-width:1240px;margin:auto}}h1{{font-size:clamp(2.3rem,6vw,5rem);line-height:1.02;max-width:16ch}}h2{{font-size:clamp(1.6rem,3vw,2.8rem)}}main{{padding:2rem clamp(1rem,4vw,3rem) 5rem}}.warning,.hold{{border:3px solid #ad7500;background:#fff0b8;border-radius:14px;padding:1rem;font-weight:800}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,230px),1fr));gap:1rem;margin:2rem 0}}article,.panel{{background:white;border:2px solid var(--blue);border-radius:16px;padding:1.1rem}}article b{{display:block;font-size:clamp(2rem,4vw,3.5rem)}}.board,.table-wrap{{overflow:auto;border:2px solid #83bddb;background:white}}object{{display:block;width:100%;min-width:760px;min-height:430px}}table{{border-collapse:collapse;width:100%;min-width:920px}}th,td{{padding:.8rem;text-align:left;vertical-align:top;border-bottom:1px solid #bdd0dc}}th{{background:var(--navy);color:white}}a{{color:#075d98;font-weight:800}}@media(max-width:650px){{main{{padding:1.2rem .8rem 4rem}}}}</style></head><body><header><div><p class="warning">{html.escape(WARNING)}</p><h1>Every actuator now has a physical branch slot.</h1><p>One editable six-channel KiCad board, five assembly instances, 25 allocated axes and five visibly unpopulated spares.</p></div></header><main><section class="grid"><article><b>25</b>allocated actuator branches</article><article><b>5</b>identical PDU boards</article><article><b>ERC 0/0</b>eight native schematic sheets</article><article><b>Placed PCB</b>high-current routing and DRC acceptance remain open</article></section><div class="hold"><h2>This is not the walking power stage</h2><p>TPS259474L blocks reverse current. It is retained only for restrained, low-energy commissioning. Standing and walking remain disabled until regenerative energy, connector temperature, dynamic torque and upstream interruption are physically validated.</p></div><h2>Native placement candidate</h2><div class="board"><object data="output/{PROJECT}-front.svg" type="image/svg+xml" aria-label="HR-30 six-channel branch PDU placement candidate"></object></div><p>The visible ratsnest is intentional: no high-current copper is released before the stackup/current/thermal inputs close. <a href="{PROJECT}.kicad_pro">Open the KiCad project</a> · <a href="{PROJECT}.kicad_pcb">Open the native PCB</a> · <a href="validation/{PROJECT}-erc.rpt">ERC report</a> · <a href="validation/{PROJECT}-drc.rpt">complete fail-closed DRC report</a></p><h2>Five-board population map</h2><div class="table-wrap"><table><thead><tr><th>Board</th><th>Channel</th><th>Axis</th><th>Family</th><th>RILM</th><th>Population</th></tr></thead><tbody>{rows}</tbody></table></div><h2>Controlled engineering records</h2><div class="panel"><p><a href="board-instance-channel-allocation.csv">channel allocation</a> · <a href="current-limit-torque-consequence-register.csv">torque consequences</a> · <a href="component-register.csv">component register</a> · <a href="terminal-register.csv">terminal register</a> · <a href="primary-source-register.csv">primary sources</a> · <a href="open-holds.csv">open holds</a></p></div></main></body></html>''',encoding="utf-8")
    guide_path=OUT/"index.html"; guide=guide_path.read_text(encoding="utf-8")
    guide=guide.replace("Every actuator now has a physical branch slot.","Every actuator now has a routed branch slot.")
    guide=guide.replace("<b>Placed PCB</b>high-current routing and DRC acceptance remain open","<b>DRC 0/0</b>routed 150 × 78 mm candidate; zero unconnected pads")
    guide=guide.replace("Native placement candidate","Native routed candidate").replace("placement candidate","routed candidate")
    guide=guide.replace("The visible ratsnest is intentional: no high-current copper is released before the stackup/current/thermal inputs close.","The ten-layer route is complete and KiCad reports DRC 0/0 with zero unconnected pads. This verifies connectivity and geometric rule compliance only; production stackup, copper weight, thermal rise and DFM remain open.")
    guide=guide.replace("complete fail-closed DRC report","DRC 0/0 report")
    guide=guide.replace("<h2>Five-board population map</h2>",f"<h2>Inspect all eight internal copper layers</h2>{layers}<h2>Five-board population map</h2>")
    guide_path.write_text(guide,encoding="utf-8")
    (OUT/"README.md").write_text(f"# HR-30 actuator branch PDU P0.1\n\n**{WARNING}**\n\nThis package provides one editable six-channel native KiCad schematic and routed 150 x 78 mm ten-layer PCB candidate. Five assembly instances allocate 25 whole-body actuator branches and retain five DNP spares. KiCad verifies schematic ERC 0/0, PCB DRC 0/0 and zero unconnected pads. The route separates shared input, individual outputs and six control-net families; exact production stackup, copper weight, DFM, thermal rise and physical tests remain open. It is a restrained commissioning architecture only; reverse energy, connector closure, dynamic torque and all work authority remain open.\n",encoding="utf-8")
    files=[p for p in OUT.rglob("*") if p.is_file() and p.name!="file-manifest.csv"]
    write_csv(OUT/"file-manifest.csv",["path","bytes","sha256","warning"],[{"path":p.relative_to(OUT).as_posix(),"bytes":p.stat().st_size,"sha256":sha(p),"warning":WARNING} for p in sorted(files)])


def update_package() -> None:
    status_path=PACKAGE/"package-status.json"; status=json.loads(status_path.read_text(encoding="utf-8")); status.update({"actuator_branch_pdu_native_schematic_present":True,"actuator_branch_pdu_schematic_sheet_count":8,"actuator_branch_pdu_board_pattern_count":1,"actuator_branch_pdu_board_instance_count":5,"actuator_branch_pdu_allocated_channel_count":25,"actuator_branch_pdu_dnp_spare_count":5,"actuator_branch_pdu_erc_errors":0,"actuator_branch_pdu_erc_warnings":0,"actuator_branch_pdu_placement_complete":True,"actuator_branch_pdu_routing_complete":True,"actuator_branch_pdu_drc_accepted":True,"actuator_branch_pdu_drc_violations":0,"actuator_branch_pdu_unconnected_pads":0,"actuator_branch_pdu_production_stackup_selected":False,"actuator_branch_pdu_walking_power_architecture_complete":False,"actuator_branch_pdu_energization_authority":False}); status_path.write_text(json.dumps(status,indent=2)+"\n",encoding="utf-8")
    readme=PACKAGE/"README.md"; text=readme.read_text(encoding="utf-8"); start,end="<!-- HR30-PDU-P01-START -->","<!-- HR30-PDU-P01-END -->"
    if start in text and end in text: text=text.split(start,1)[0]+text.split(end,1)[1]
    section=f"\n{start}\n## Twenty-five routed actuator branch slots\n\nFive instances of one editable six-channel native KiCad PDU candidate allocate all 25 axes and retain five assembly-DNP spares. The eight-sheet schematic validates at ERC 0/0; the 150 x 78 mm ten-layer PCB validates at DRC 0/0 with zero unconnected pads. Each populated channel uses a TPS259474L circuit-breaker/latch-off eFuse with an axis-bound RILM variant, individual output pair, open-drain disable input and power-good output. This is a restrained commissioning architecture only: the device blocks reverse current, so production stackup, regeneration/clamp, connector temperature, dynamic torque, copper/thermal validation and every powered-work authority remain open. Open `electrical/actuator-branch-pdu-p0.1/index.html`.\n{end}\n"
    readme.write_text(text.rstrip()+section,encoding="utf-8")
    page=PACKAGE/"index.html"; text=page.read_text(encoding="utf-8")
    if start in text and end in text: text=text.split(start,1)[0]+text.split(end,1)[1]
    web=f'''{start}<section id="actuator-branch-pdu"><h2>Every actuator now has a routed protected branch slot</h2><div class="grid"><article class="card pass"><div class="metric">25</div><p>axis-bound commissioning branches across five board instances.</p></article><article class="card pass"><div class="metric">5</div><p>assembly-DNP spare channels remain visibly unpopulated.</p></article><article class="card pass"><h3>ERC 0 / 0</h3><p>Eight editable, connected native schematic sheets.</p></article><article class="card pass"><h3>DRC 0 / 0</h3><p>Routed 150 × 78 mm candidate with zero unconnected pads. Stackup and thermal proof remain open.</p></article></div><div class="viewer"><object data="electrical/actuator-branch-pdu-p0.1/output/{PROJECT}-front.svg" type="image/svg+xml" aria-label="Six-channel HR-30 actuator branch PDU routed candidate"></object><p><a href="electrical/actuator-branch-pdu-p0.1/index.html">Open the interactive PDU guide</a> · <a href="electrical/actuator-branch-pdu-p0.1/board-instance-channel-allocation.csv">25-axis allocation</a> · <a href="electrical/actuator-branch-pdu-p0.1/{PROJECT}.kicad_pro">native KiCad project</a>.</p></div></section>{end}'''
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
