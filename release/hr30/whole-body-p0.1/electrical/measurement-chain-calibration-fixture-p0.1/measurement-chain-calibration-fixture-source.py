#!/usr/bin/env python3
"""Generate the HR-30 off-robot measurement-chain calibration fixture P0.1.

The fixture drives exactly one disconnected diagnostic-pod -> 3 m cable ->
measurement-panel -> NI-9229 lane at a time.  It is test equipment only and
never connects to an HR-30 source node or safety circuit during calibration.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WHOLE = ROOT / "hr30" / "whole-body-p0.1"
OUT = WHOLE / "electrical" / "measurement-chain-calibration-fixture-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / "electrical" / OUT.name
PODS = WHOLE / "electrical" / "diagnostic-pickoff-pods-p0.1"
PANEL = WHOLE / "electrical" / "measurement-boundary-panel-p0.1"
HARNESS = WHOLE / "first-energization-measurement-harness-p0.1"
INSTR = WHOLE / "first-energization-instrumentation-p0.1"
PROJECT = "hr30-measurement-chain-calibration-fixture-p0.1"
IDENTIFIER = "HR30-MEASUREMENT-CHAIN-CALIBRATION-FIXTURE-P0.1"
DATE = "2026-08-19"
WARNING = "PRELIMINARY - UNBUILT OFF-ROBOT MEASUREMENT CALIBRATION FIXTURE - ZERO SAFETY CREDIT - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION TO THE ROBOT, POWERED ROBOT TESTING, MOTION, WALKING OR ENERGIZATION"
AUTHORITY = "NO PROCUREMENT, FABRICATION, ASSEMBLY, ROBOT CONNECTION, POWERED-ROBOT-TEST, MOTION, WALKING OR ENERGIZATION AUTHORITY"
KICAD = Path(r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe")
KICAD_PYTHON = Path(r"C:\Program Files\KiCad\10.0\bin\python.exe")
CAD_PYTHON = ROOT.parent / ".venvs" / "hr-v0-cad" / "Scripts" / "python.exe"
FP_ROOT = Path(r"C:\Program Files\KiCad\10.0\share\kicad\footprints")

PHOENIX_FP = "Connector_Phoenix_MSTB:PhoenixContact_MSTBA_2,5_2-G-5,08_1x02_P5.08mm_Horizontal"
PHOENIX_HEADER_URL = "https://www.phoenixcontact.com/en-us/products/pcb-header-mstba-25-2-g-508-1757242"
PHOENIX_PLUG_URL = "https://www.phoenixcontact.com/en-us/products/pcb-connector-mstb-25-2-st-508-1757019"
KEYSIGHT_URL = "https://www.keysight.com/us/en/assets/7018-05629/data-sheets/5992-2124.pdf"
FLUKE_URL = "https://www.fluke.com/en-us/product/electrical-testing/digital-multimeters/87v-max"
FLUKE_TL930_URL = "https://www.fluke.com/en-us/product/accessories/adapters/fluke-tl930"
POMONA_73099_URL = "https://www.pomonaelectronics.com/sites/default/files/d73099_101.pdf"
HAMMOND_URL = "https://www.hammfg.com/electronics/small-case/plastic/1591"
NI9229_URL = "https://www.ni.com/docs/en-US/bundle/ni-9229-specs/page/specs.html"

CHANNELS = [
    ("CH-AI-01", "ACT_MAIN_SOURCE_12V", 12.0),
    ("CH-AI-02", "ACT_MAIN_SAFE_12V", 12.0),
    ("CH-AI-03", "TTL_LDIST_SAFE_9V", 9.0),
    ("CH-AI-04", "CTRL_5V", 5.0),
    ("CH-AI-05", "ESTOP_CH_A_24V", 24.0),
    ("CH-AI-06", "HARDWIRED_PERMIT_24V", 24.0),
    ("CH-AI-07", "K1_COIL_24V", 24.0),
    ("CH-AI-08", "K2_COIL_24V", 24.0),
]
POINTS = (0.0, 1.0, 2.5, 5.0, 9.0, 12.0, 18.0, 24.0, 0.0)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"empty register: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def run(command: list[str], cwd: Path = ROOT) -> subprocess.CompletedProcess[str]:
    cp = subprocess.run(command, cwd=cwd, text=True, capture_output=True)
    if cp.returncode:
        raise RuntimeError(f"command failed {cp.returncode}: {' '.join(command)}\n{cp.stdout}\n{cp.stderr}")
    return cp


def load_model():
    path = ROOT / "tools" / "generate_hr_v0_electrical_v3.py"
    spec = importlib.util.spec_from_file_location("hr30_cal_fixture_model", path)
    if not spec or not spec.loader:
        raise RuntimeError("cannot load schematic model")
    model = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = model
    spec.loader.exec_module(model)
    model.OUT = OUT
    model.PROJECT = PROJECT
    model.REV = "P0.1"
    model.DATE = DATE
    model.WARNING = WARNING
    model.PROJECT_TITLE = "PROJECT BUTTON HR-30 OFF-ROBOT MEASUREMENT CALIBRATION FIXTURE"
    model.PROJECT_SUBTITLE = "Sequential floating-lane source breakout; one disconnected chain at a time; zero safety credit."
    return model


def write_schematic() -> None:
    model = load_model()
    definitions = [
        ("JPS", "isolated source input", "Phoenix Contact 1757242", (62, 95)),
        ("JDUT", "output to disconnected diagnostic pod", "Phoenix Contact 1757242", (318, 95)),
    ]
    components = []
    for ref, value, mpn, position in definitions:
        pins = [
            model.pn(ref, "1", "HI / +", "CAL_HI", "left"),
            model.pn(ref, "2", "LO / -", "CAL_LO", "right"),
        ]
        components.append(model.Component(ref, value, pins, "EXACT COMPONENT CANDIDATE; APPLICATION OPEN", "OFF-ROBOT TEST EQUIPMENT ONLY", PHOENIX_HEADER_URL, mpn, position=position, width=72, footprint=PHOENIX_FP))
    components += [
        model.Component("JHI", "red 4 mm DMM safety jack", [model.pn("JHI", "1", "CAL HI", "CAL_HI", "left")], "EXACT COMPONENT CANDIDATE; PCB/ENCLOSURE FAI OPEN", "OFF-ROBOT TEST EQUIPMENT ONLY", POMONA_73099_URL, "73099-2", position=(177, 48), width=66, footprint="HR30_CAL:POMONA_73099"),
        model.Component("JLO", "black 4 mm DMM safety jack", [model.pn("JLO", "1", "CAL LO", "CAL_LO", "right")], "EXACT COMPONENT CANDIDATE; PCB/ENCLOSURE FAI OPEN", "OFF-ROBOT TEST EQUIPMENT ONLY", POMONA_73099_URL, "73099-0", position=(203, 48), width=66, footprint="HR30_CAL:POMONA_73099"),
    ]
    sheet = model.Sheet(1, "01_passive_source_breakout.kicad_sch", "Passive one-channel calibration source breakout", "JPS, JHI/JLO and JDUT are one floating pair; no PE/chassis/USB connection is present.")
    sheet.components = components
    sheet.notes = [
        "Use exactly one disconnected measurement chain at a time: pod, 3 m cable, one panel lane, one NI-9229 channel.",
        "Keysight output remains OFF during every connection change. Candidate ceiling is 24.0 V and candidate current limit is 10 mA; qualified procedure approval remains open.",
        "Fluke 87V MAX CAL measures the actual JPS voltage through JHI/JLO using the exact TL930 patch-cord candidate. Supply readback alone is not the reference value.",
        "No fixture contact may be attached to the robot, safety relay, contactor, actuator bus, PE, chassis or synchronization slate.",
        WARNING,
    ]
    sheets = [sheet]
    net_counts = {"CAL_HI": 3, "CAL_LO": 3}
    wires = model.build_wire_numbers(sheets, net_counts)
    root_uuid = model.uid("root-hr30-measurement-chain-calibration-fixture-p0.1")
    project = {"board": {}, "boards": [], "cvpcb": {}, "erc": {}, "libraries": {}, "meta": {"filename": f"{PROJECT}.kicad_pro", "version": 1}, "net_settings": {"classes": [], "meta": {"version": 3}}, "pcbnew": {}, "schematic": {}, "text_variables": {"PROJECT_STATUS": WARNING}}
    (OUT / f"{PROJECT}.kicad_pro").write_text(json.dumps(project, indent=2) + "\n", encoding="utf-8")
    symbols = [model.lib_symbol(c).replace(f'(symbol "PBV3:{c.ref}"', f'(symbol "{c.ref}"', 1) for c in components]
    (OUT / f"{PROJECT}.kicad_sym").write_text('(kicad_symbol_lib\n  (version 20251024) (generator "kicad_symbol_editor") (generator_version "10.0")\n  ' + "\n".join(symbols) + '\n)\n', encoding="utf-8")
    (OUT / "sym-lib-table").write_text(f'(sym_lib_table\n  (version 7)\n  (lib (name "PBV3")(type "KiCad")(uri "${{KIPRJMOD}}/{PROJECT}.kicad_sym")(options "")(descr "HR-30 calibration fixture symbols"))\n)\n', encoding="utf-8")
    (OUT / f"{PROJECT}.kicad_sch").write_text(model.root_schematic(root_uuid, sheets), encoding="utf-8")
    (OUT / sheet.filename).write_text(model.child_schematic(root_uuid, sheet, net_counts, wires), encoding="utf-8")


def pcb_mode() -> int:
    import pcbnew

    def footprint(identifier: str):
        library, name = identifier.split(":", 1)
        fp = pcbnew.FootprintLoad(str(FP_ROOT / f"{library}.pretty"), name)
        if fp is None:
            raise RuntimeError(f"cannot load footprint {identifier}")
        return fp

    def pads(fp, number: str):
        return [p for p in fp.Pads() if p.GetNumber() == number]

    def track(board, net, a, b, width=.50, layer=None):
        item = pcbnew.PCB_TRACK(board)
        item.SetStart(pcbnew.VECTOR2I_MM(*a)); item.SetEnd(pcbnew.VECTOR2I_MM(*b))
        item.SetLayer(pcbnew.F_Cu if layer is None else layer); item.SetWidth(pcbnew.FromMM(width)); item.SetNet(net); board.Add(item)

    def pomona_73099_footprint():
        """Manufacturer-drawing footprint, D2134437 rev.101.

        Four 1.3 mm holes are on a 10.16 mm square.  The 2.2 mm centre
        contact is 3.8 mm from the left column and 2.2 mm below the top row.
        All five metal PCB tails belong to the one-pole jack and deliberately
        use the same pad number/net.  Received-part FAI remains mandatory.
        """
        fp = pcbnew.FOOTPRINT(None); fp.SetFPID(pcbnew.LIB_ID("HR30_CAL", "POMONA_73099")); fp.SetValue("POMONA_73099")
        fp.Reference().SetVisible(False); fp.Value().SetVisible(False)
        layers = pcbnew.LSET.AllCuMask(); layers.AddLayer(pcbnew.F_Mask); layers.AddLayer(pcbnew.B_Mask)
        for px, py, drill in ((-5.08,-5.08,1.30),(5.08,-5.08,1.30),(-5.08,5.08,1.30),(5.08,5.08,1.30),(-1.28,-2.88,2.20)):
            pad = pcbnew.PAD(fp); pad.SetNumber("1"); pad.SetAttribute(pcbnew.PAD_ATTRIB_PTH); pad.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
            pad.SetSize(pcbnew.VECTOR2I_MM(drill + 1.0, drill + 1.0)); pad.SetDrillSize(pcbnew.VECTOR2I_MM(drill, drill)); pad.SetFPRelativePosition(pcbnew.VECTOR2I_MM(px, py)); pad.SetLayerSet(layers); fp.Add(pad)
        for start, end in (((-6,-7.5),(6,-7.5)),((6,-7.5),(6,7.5)),((6,7.5),(-6,7.5)),((-6,7.5),(-6,-7.5))):
            line=pcbnew.PCB_SHAPE(fp); line.SetShape(pcbnew.SHAPE_T_SEGMENT); line.SetStart(pcbnew.VECTOR2I_MM(*start)); line.SetEnd(pcbnew.VECTOR2I_MM(*end)); line.SetLayer(pcbnew.F_Fab); line.SetWidth(pcbnew.FromMM(.15)); fp.Add(line)
        return fp

    lib = OUT / "HR30_CAL.pretty"; lib.mkdir(parents=True, exist_ok=True)
    pcbnew.PCB_IO_KICAD_SEXPR().FootprintSave(str(lib), pomona_73099_footprint())
    (OUT / "fp-lib-table").write_text('(fp_lib_table\n  (version 7)\n  (lib (name "HR30_CAL")(type "KiCad")(uri "${KIPRJMOD}/HR30_CAL.pretty")(options "")(descr "Pomona 73099 candidate from D2134437 rev.101"))\n)\n', encoding="utf-8")

    def pomona_73099(ref: str, value: str, x: float, y: float, net):
        fp = pomona_73099_footprint(); fp.SetFPID(pcbnew.LIB_ID("", "POMONA_73099")); fp.SetReference(ref); fp.SetValue(value); fp.SetPosition(pcbnew.VECTOR2I_MM(x, y))
        for pad in fp.Pads(): pad.SetNet(net)
        board.Add(fp)
        placed = list(fp.Pads())
        centre = max(placed, key=lambda p: p.GetDrillSize().x)
        c = centre.GetPosition(); centre_xy = (pcbnew.ToMM(c.x), pcbnew.ToMM(c.y))
        layer = pcbnew.F_Cu if net.GetNetname() == "CAL_HI" else pcbnew.B_Cu
        for pad in placed:
            if pad is centre: continue
            p = pad.GetPosition(); track(board, net, centre_xy, (pcbnew.ToMM(p.x), pcbnew.ToMM(p.y)), layer=layer)
        return fp

    board = pcbnew.BOARD(); board.SetCopperLayerCount(2)
    settings = board.GetDesignSettings(); settings.SetBoardThickness(pcbnew.FromMM(1.6)); settings.m_MinClearance = pcbnew.FromMM(.25); settings.m_TrackMinWidth = pcbnew.FromMM(.25); settings.m_HoleClearance = pcbnew.FromMM(.25); settings.m_HoleToHoleMin = pcbnew.FromMM(.30); settings.m_NetSettings.GetDefaultNetclass().SetClearance(pcbnew.FromMM(.25))
    nets = {}
    for name in ("CAL_HI", "CAL_LO"):
        net = pcbnew.NETINFO_ITEM(board, name); board.Add(net); nets[name] = net
    placements = [("JPS", 16.0, 40.0, 90), ("JDUT", 88.0, 40.0, 90)]
    fps = {}
    for ref, x, y, angle in placements:
        fp = footprint(PHOENIX_FP); fp.SetReference(ref); fp.SetValue("1757242"); fp.SetPosition(pcbnew.VECTOR2I_MM(x, y)); fp.SetOrientationDegrees(angle); fp.Reference().SetVisible(False); fp.Value().SetVisible(False)
        for number, net_name in (("1", "CAL_HI"), ("2", "CAL_LO")):
            for pad in pads(fp, number): pad.SetNet(nets[net_name])
        board.Add(fp); fps[ref] = fp
    fps["JHI"] = pomona_73099("JHI", "73099-2 RED", 43.0, 64.0, nets["CAL_HI"])
    fps["JLO"] = pomona_73099("JLO", "73099-0 BLACK", 61.0, 64.0, nets["CAL_LO"])
    for index, (x, y) in enumerate(((5,5),(99,5),(5,71),(99,71)), 1):
        hole = footprint("MountingHole:MountingHole_3.5mm"); hole.SetReference(f"H{index}"); hole.SetValue("ENCLOSURE STANDOFF FAI REQUIRED"); hole.SetPosition(pcbnew.VECTOR2I_MM(x,y)); hole.SetBoardOnly(True); hole.SetExcludedFromBOM(True); hole.SetExcludedFromPosFiles(True); hole.Reference().SetVisible(False); hole.Value().SetVisible(False); board.Add(hole)
    corners = ((0,0),(104,0),(104,76),(0,76))
    for a, b in zip(corners, (*corners[1:], corners[0])):
        edge = pcbnew.PCB_SHAPE(board); edge.SetShape(pcbnew.SHAPE_T_SEGMENT); edge.SetStart(pcbnew.VECTOR2I_MM(*a)); edge.SetEnd(pcbnew.VECTOR2I_MM(*b)); edge.SetLayer(pcbnew.Edge_Cuts); edge.SetWidth(pcbnew.FromMM(.20)); board.Add(edge)
    def pos(ref, pin):
        p = pads(fps[ref], pin)[0].GetPosition(); return pcbnew.ToMM(p.x), pcbnew.ToMM(p.y)
    for pin, net_name, ybus in (("1", "CAL_HI", 48.0), ("2", "CAL_LO", 32.0)):
        a, c = pos("JPS", pin), pos("JDUT", pin)
        b = pos("JHI" if net_name == "CAL_HI" else "JLO", "1")
        layer = pcbnew.F_Cu if net_name == "CAL_HI" else pcbnew.B_Cu
        track(board, nets[net_name], a, (30,ybus), layer=layer); track(board, nets[net_name], (30,ybus), (74,ybus), layer=layer); track(board, nets[net_name], (74,ybus), c, layer=layer); track(board, nets[net_name], b, (b[0],ybus), layer=layer)
    for value, x, y, size in (("ISOLATED SOURCE",16,73,1.0),("RED HI     DMM     BLACK LO",52,51,1.0),("ONE DISCONNECTED CHAIN",80,7,1.0),("NEVER CONNECT TO ROBOT",52,16,1.15)):
        label = pcbnew.PCB_TEXT(board); label.SetText(value); label.SetPosition(pcbnew.VECTOR2I_MM(x,y)); label.SetLayer(pcbnew.F_SilkS); label.SetTextSize(pcbnew.VECTOR2I_MM(size,size)); label.SetTextThickness(pcbnew.FromMM(.17)); board.Add(label)
    board_dir = OUT / "board"; board_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(OUT / "fp-lib-table", board_dir / "fp-lib-table")
    shutil.copytree(OUT / "HR30_CAL.pretty", board_dir / "HR30_CAL.pretty", dirs_exist_ok=True)
    pcbnew.SaveBoard(str(board_dir / f"{PROJECT}.kicad_pcb"), board)
    print("generated passive one-channel calibration fixture PCB")
    return 0


def port_rows() -> list[dict[str, object]]:
    rows = []
    for ref, role, external in (("JPS", "ISOLATED SOURCE INPUT", "Keysight E36313A output 2 or 3"), ("JDUT", "DISCONNECTED CHAIN OUTPUT", "selected diagnostic pod JIN")):
        for contact, polarity, net in ((1, "HI/+", "CAL_HI"), (2, "LO/-", "CAL_LO")):
            rows.append({"connector":ref,"role":role,"contact":contact,"polarity":polarity,"net":net,"header":"Phoenix Contact 1757242","mating_plug":"Phoenix Contact 1757019","external_endpoint":external,"parallel_contacts_on_board":3,"robot_connection_permitted":"NO","warning":WARNING})
    for ref, polarity, net, jack, endpoint in (("JHI","HI/+","CAL_HI","Pomona 73099-2 red","Fluke V/ohm input through red TL930 lead"),("JLO","LO/-","CAL_LO","Pomona 73099-0 black","Fluke COM input through black TL930 lead")):
        rows.append({"connector":ref,"role":"REFERENCE DMM SAFETY JACK","contact":1,"polarity":polarity,"net":net,"header":jack,"mating_plug":"Fluke TL930 4 mm patch cord","external_endpoint":endpoint,"parallel_contacts_on_board":3,"robot_connection_permitted":"NO","warning":WARNING})
    return rows


def channel_rows() -> list[dict[str, object]]:
    return [{"sequence":i,"channel_id":cid,"signal":signal,"planning_full_scale_v_not_limit":v,"pod":f"DP-{i:02d}","pod_input":"JIN.1/JIN.2","pod_output":"JOUT.1/JOUT.2","panel_input":f"J{i}I.1/J{i}I.2","panel_output":f"J{i}O.1/J{i}O.2","ni_module":"NI-9229-A" if i <= 4 else "NI-9229-B","ni_channel":f"AI{(i-1)%4}","simultaneous_fixture_channels":1,"robot_disconnected_required":"YES","state":"NOT EXECUTED","warning":WARNING} for i,(cid,signal,v) in enumerate(CHANNELS,1)]


def point_rows() -> list[dict[str, object]]:
    rows = []
    for index, (cid, signal, planning_v) in enumerate(CHANNELS, 1):
        for ordinal, requested in enumerate(POINTS, 1):
            rows.append({"channel_id":cid,"signal":signal,"point_ordinal":ordinal,"requested_source_v":f"{requested:.3f}","within_channel_planning_range":"YES" if requested <= planning_v else "EXTENDED BENCH CHARACTERIZATION ONLY","repeat_count":3,"source_current_limit_candidate_ma":10,"reference_value":"MEASURE WITH IN-DATE FLUKE 87V MAX CAL","ni_raw_value":"NOT EXECUTED","fit_use":"YES" if ordinal not in (1,9) else "ZERO/HYSTERESIS CHECK","performance_acceptance_limit":"QUALIFIED SELECTION REQUIRED","state":"NOT EXECUTED","warning":WARNING})
    return rows


def procedure_rows() -> list[dict[str, object]]:
    steps = [
        ("CF-P01","prove robot separation","Photograph all eight pod JIN source tails disconnected from robot and cap them; continuity proves no fixture-to-robot path.","STOP if any robot, safety, actuator, PE or chassis connection exists"),
        ("CF-P02","record equipment identity","Record source, DMM, cDAQ, both NI-9229 serials, firmware/software, calibration certificates and expiry.","STOP for expired/missing calibration or failed self-test"),
        ("CF-P03","inspect passive fixture","Continuity CAL_HI JPS-JHI-JDUT and CAL_LO JPS-JLO-JDUT; >10 Mohm between HI/LO and enclosure/PE with all external leads removed.","STOP on map, insulation or damage discrepancy"),
        ("CF-P04","set isolated source","Output OFF; select one E36313A output 2 or 3; candidate 10 mA current limit; verify no earth-reference strap or series/parallel coupling.","Qualified setup approval remains required"),
        ("CF-P05","connect reference meter","Connect red/black TL930 leads from JHI/JLO to the Fluke V/ohm and COM inputs; verify both current jacks empty and polarity correct.","STOP if either meter current input is used"),
        ("CF-P06","connect one chain","Connect JDUT only to selected pod JIN; connect that pod through its 3 m cable, panel lane and measurement harness to one NI-9229 channel.","All seven other lanes remain disconnected from fixture"),
        ("CF-P07","zero check","Command 0 V, turn output ON, record DMM and NI samples; then output OFF.","No numerical acceptance until qualified limits are released"),
        ("CF-P08","ascending points","For each scheduled nonzero point: output OFF, set value, verify 10 mA limit, output ON, settle, record DMM and NI; output OFF before change.","Never exceed 24.0 V candidate ceiling"),
        ("CF-P09","descending zero","Return to 0 V and record end zero for offset/hysteresis evidence.","Retain raw time series, not summaries only"),
        ("CF-P10","polarity characterization","With output OFF, use a separately labeled crossed JDUT cable; apply 1 V then the channel planning voltage and record negative response.","Characterization only; fault-detection limit open"),
        ("CF-P11","open-lead characterization","With output OFF, use separately labeled HI-open and LO-open cables; apply 1 V and planning voltage; characterize the actual invalid/open signature.","Do not assume an open input reads zero"),
        ("CF-P12","isolation/noise","At 0 V and planning voltage capture at least 10 s raw data while all other fixture inputs remain disconnected.","Noise/crosstalk limits open"),
        ("CF-P13","repeat","Perform three complete repeats per point and retain environmental temperature and elapsed time.","Missing repeat leaves channel uncalibrated"),
        ("CF-P14","fit and uncertainty","Fit source voltage = gain * NI voltage + offset per channel; retain residuals and uncertainty contributors.","Nominal 1.4204 factor is comparison only"),
        ("CF-P15","close out","Output OFF, disconnect source, cap all leads, archive raw data and signed traveler.","This does not authorize robot connection or energization"),
    ]
    return [{"step_id":a,"action":b,"method":c,"stop_or_boundary":d,"execution_state":"NOT EXECUTED","authority":AUTHORITY,"warning":WARNING} for a,b,c,d in steps]


def fault_rows() -> list[dict[str, object]]:
    cases = [
        ("CF-F01","normal polarity","standard straight-through JDUT cable","positive slope and recorded residuals; numeric limit open"),
        ("CF-F02","reversed polarity","dedicated red-tagged crossed JDUT cable","negative response must be recognizable; threshold open"),
        ("CF-F03","HI lead open","dedicated orange-tagged one-conductor cable","characterize actual invalid/open signature; do not infer zero"),
        ("CF-F04","LO lead open","dedicated orange-tagged one-conductor cable","characterize actual invalid/open signature; do not infer zero"),
        ("CF-F05","JDUT HI-LO short","dedicated black shorting plug; source output OFF during installation","E36313A enters current limiting at candidate 10 mA; qualified test approval open"),
        ("CF-F06","wrong panel lane","connect selected pod output to a nonmatching panel lane during unpowered continuity only","channel map discrepancy must be found before voltage application"),
        ("CF-F07","adjacent NI lane observation","one driven lane; seven source inputs disconnected","record crosstalk/noise; acceptance limit open"),
        ("CF-F08","source removed mid-record","turn E36313A output OFF without changing wiring","capture decay/open behavior; detection-time limit open"),
    ]
    return [{"fault_id":a,"condition":b,"controlled_adapter_or_action":c,"required_observation":d,"robot_connection":"PROHIBITED","execution_state":"NOT EXECUTED","safety_credit":"NONE","warning":WARNING} for a,b,c,d in cases]


def data_rows() -> list[dict[str, object]]:
    fields = [
        ("run_id","string","unique immutable acquisition run"),("timestamp_utc","ISO-8601","common acquisition timestamp"),("channel_id","enum CH-AI-01..08","exact lane identity"),("repeat","integer 1..3","repeat identity"),("requested_source_v","V","programmed value; not reference"),("reference_dmm_v","V","Fluke measured source value"),("ni_raw_v","V","unscaled NI-9229 reading"),("source_current_a","A","Keysight readback; support evidence only"),("fixture_temp_c","degC","ambient near fixture"),("gain_v_per_v","ratio","fitted source/NI slope"),("offset_v","V","fitted source intercept"),("residual_v","V","reference minus fitted source"),("expanded_uncertainty_v","V","method/coverage factor must be stated"),("equipment_serials","string","source/DMM/cDAQ/module identities"),("calibration_due_dates","string","traceability boundary"),("raw_file_sha256","hex","immutable raw evidence binding"),("operator","string","executor identity"),("reviewer","string","qualified disposition identity"),
    ]
    return [{"field":a,"type_or_unit":b,"purpose":c,"required":"YES","value":"NOT EXECUTED","warning":WARNING} for a,b,c in fields]


def bom_rows() -> list[dict[str, object]]:
    return [
        {"item":"passive calibration breakout PCB","manufacturer":"SELECTION REQUIRED","order_code":"SELECTION REQUIRED","quantity":1,"basis":"104 x 76 x 1.6 mm two-layer native KiCad design","state":"FABRICATOR/STACKUP/FINISH/DFM OPEN","procurement_released":"NO","warning":WARNING},
        {"item":"2-position 5.08 mm horizontal PCB header","manufacturer":"Phoenix Contact","order_code":"1757242","quantity":2,"basis":"JPS and JDUT","state":"EXACT CANDIDATE","procurement_released":"NO","warning":WARNING},
        {"item":"2-position 5.08 mm screw plug","manufacturer":"Phoenix Contact","order_code":"1757019","quantity":7,"basis":"source pair, normal, reverse, HI-open, LO-open and controlled short adapter","state":"EXACT CONNECTOR; CABLE TERMINATIONS DEFINED IN SEPARATE CABLE-KIT PACKAGE","procurement_released":"NO","warning":WARNING},
        {"item":"right-angle PCB 4 mm safety jack, red","manufacturer":"Pomona Electronics","order_code":"73099-2","quantity":1,"basis":"JHI direct DMM monitor","state":"EXACT CANDIDATE; MANUFACTURER DRAWING D2134437 REV.101; RECEIVED FAI OPEN","procurement_released":"NO","warning":WARNING},
        {"item":"right-angle PCB 4 mm safety jack, black","manufacturer":"Pomona Electronics","order_code":"73099-0","quantity":1,"basis":"JLO direct DMM monitor","state":"EXACT CANDIDATE; MANUFACTURER DRAWING D2134437 REV.101; RECEIVED FAI OPEN","procurement_released":"NO","warning":WARNING},
        {"item":"61 cm red/black 4 mm patch-cord pair","manufacturer":"Fluke","order_code":"TL930 / part 1616671","quantity":1,"basis":"fixture JHI/JLO to 87V MAX V/ohm and COM inputs","state":"EXACT CANDIDATE; 30 V RMS/60 V DC, 8 A; RECEIPT/LEAD INSPECTION OPEN","procurement_released":"NO","warning":WARNING},
        {"item":"flanged-lid ABS enclosure 121 x 94 x 34 mm","manufacturer":"Hammond Manufacturing","order_code":"1591GFLBK","quantity":1,"basis":"fixture housing candidate","state":"EXACT ENVELOPE CANDIDATE; PCB SUPPORT/CUTOUT/FAI OPEN","procurement_released":"NO","warning":WARNING},
        {"item":"triple-output programmable DC supply","manufacturer":"Keysight","order_code":"E36313A","quantity":1,"basis":"output 2 or 3; 0-25 V / 0-2 A; low-current range available","state":"BORROW CANDIDATE; RECEIPT/CALIBRATION/ISOLATION CHECK OPEN","procurement_released":"NO","warning":WARNING},
        {"item":"traceably calibrated DMM","manufacturer":"Fluke","order_code":"5206068 (87V MAX CAL)","quantity":1,"basis":"independent source-voltage reference","state":"EXACT CANDIDATE; CERTIFICATE/DUE DATE/LEAD INSPECTION OPEN","procurement_released":"NO","warning":WARNING},
        {"item":"source and fault-injection cable set","manufacturer":"PROJECT ASSEMBLY","order_code":"HR30-MCF-CK-P0.1","quantity":1,"basis":"normal, reverse, HI-open, LO-open, short and source leads; keyed labels required","state":"DEFINED IN SEPARATE CABLE-KIT PACKAGE; UNBUILT","procurement_released":"NO","warning":WARNING},
    ]


def source_rows() -> list[dict[str, object]]:
    return [
        {"source_id":"CF-S01","manufacturer":"Keysight","document":"E36300 Series data sheet 5992-2124EN","revision_or_date":"live official PDF accessed 2026-08-19; document revision not stated in extracted title","url":KEYSIGHT_URL,"verified":"E36313A outputs 2/3 are 0-25 V, 0-2 A; remote sensing and 20 mA low-current measurement range documented","open_boundary":"received serial/calibration, exact output isolation/configuration and 10 mA behavior","warning":WARNING},
        {"source_id":"CF-S02","manufacturer":"Fluke","document":"87V MAX product page","revision_or_date":"live official page accessed 2026-08-19; page revision not stated","url":FLUKE_URL,"verified":"87V MAX CAL part 5206068 includes traceable certificate with data","open_boundary":"received certificate, due date, applicable voltage uncertainty and lead condition","warning":WARNING},
        {"source_id":"CF-S03","manufacturer":"Phoenix Contact","document":"MSTBA 2,5/2-G-5,08 product page","revision_or_date":"live official page accessed 2026-08-19; page revision not stated","url":PHOENIX_HEADER_URL,"verified":"1757242 two-position 5.08 mm PCB header family","open_boundary":"received lot/PCB process/application FAI","warning":WARNING},
        {"source_id":"CF-S04","manufacturer":"Phoenix Contact","document":"MSTB 2,5/2-ST-5,08 product page","revision_or_date":"live official page accessed 2026-08-19; page revision not stated","url":PHOENIX_PLUG_URL,"verified":"1757019 mating screw plug family","open_boundary":"wire range, strip/ferrule method and retention for exact cable","warning":WARNING},
        {"source_id":"CF-S05","manufacturer":"Hammond Manufacturing","document":"1591 series product page and current family drawing","revision_or_date":"live official page accessed 2026-08-19","url":HAMMOND_URL,"verified":"1591GFLBK nominal 121 x 94 x 34 mm flanged-lid ABS enclosure family","open_boundary":"internal PCB supports, connector cutouts and received FAI","warning":WARNING},
        {"source_id":"CF-S06","manufacturer":"National Instruments","document":"NI-9229 specifications","revision_or_date":"live official documentation accessed 2026-08-19; revision not stated on page","url":NI9229_URL,"verified":"four simultaneously sampled differential channels and published input characteristics","open_boundary":"received module identity/calibration and complete-chain uncertainty","warning":WARNING},
        {"source_id":"CF-S07","manufacturer":"Pomona Electronics","document":"Model 73099 technical data sheet D2134437 rev.101","revision_or_date":"rev.101; copyright 2019; live official PDF accessed 2026-08-19","url":POMONA_73099_URL,"verified":"red 73099-2 and black 73099-0 right-angle PCB safety jacks; official drill pattern; CAT III 1000 V/CAT IV 600 V, 24 A","open_boundary":"received-part pin/commoning check, PCB/enclosure FAI and application review","warning":WARNING},
        {"source_id":"CF-S08","manufacturer":"Fluke","document":"TL930 product page","revision_or_date":"live official page accessed 2026-08-19; page revision not stated","url":FLUKE_TL930_URL,"verified":"part 1616671; red/black pair; 61 cm; multi-stacking 4 mm plugs; 30 V RMS/60 V DC, 8 A","open_boundary":"received lead inspection and exact 87V MAX input fit","warning":WARNING},
    ]


def hold_rows() -> list[dict[str, object]]:
    holds = [
        ("CF-H01","fixture PCB/enclosure DFM and FAI","fabricator stackup/finish, Hammond internal fit, supports, connector cutouts, labels and strain relief"),
        ("CF-H02","exact cable construction","wire, plugs, terminations, polarity, labels, continuity, retention and short/open adapter controls"),
        ("CF-H03","received calibrated instruments","serials, firmware, self-test, certificates, due dates and exact configuration"),
        ("CF-H04","qualified calibration procedure and limits","approved point set/current limit/settling/sample duration/fit/residual/noise/crosstalk/uncertainty criteria"),
        ("CF-H05","fixture build and inspection","all passive continuity, insulation, enclosure, connector and labeling tests executed"),
        ("CF-H06","eight complete-chain calibration executions","three repeats per point plus polarity/open/noise characterization and immutable raw data"),
        ("CF-H07","independent metrology/electrical review","accepted uncertainty budget, fit method, traceability and channel dispositions"),
        ("CF-H08","robot-side source-tap package","separate device-specific terminal hardware, loading/fault review and installed source-tail evidence"),
        ("CF-H09","FER-G11 closure","signed whole-session instruments, numeric abort limits, dry rehearsal and qualified stage authorization"),
    ]
    return [{"hold_id":a,"item":b,"closure_evidence":c,"state":"OPEN","authority":AUTHORITY,"warning":WARNING} for a,b,c in holds]


def inspection_rows() -> list[dict[str, object]]:
    tests = [
        ("CF-T01","board continuity","JPS.1/JHI.1/JDUT.1 common; JPS.2/JLO.1/JDUT.2 common; no cross pair"),
        ("CF-T02","mutual isolation",">10 Mohm between CAL_HI, CAL_LO, enclosure and PE with all external cables removed; limit requires qualified confirmation"),
        ("CF-T03","connector polarity","all six external contacts and every labeled cable match connector/contact map; JHI red and JLO black"),
        ("CF-T04","enclosure/strain relief","received board supports, clearances, lid, cutouts, guards, labels and clamps inspected"),
        ("CF-T05","robot separation","fixture has no continuity to robot, safety, actuator, PE, chassis or sync slate"),
        ("CF-T06","source current limit","candidate 10 mA behavior verified into dedicated shorting plug without exceeding received ratings"),
        ("CF-T07","reference agreement","source readback and traceable DMM comparison recorded; acceptance limit qualified before execution"),
        ("CF-T08","all channel calibration","72 scheduled points x 3 repeats complete with raw files"),
        ("CF-T09","fault adapter behavior","reverse, HI-open, LO-open, short, wrong-lane continuity and source-off cases executed"),
        ("CF-T10","uncertainty/review","per-channel fit, residuals, repeatability, temperature, instrument uncertainty and reviewer disposition complete"),
    ]
    return [{"test_id":a,"test":b,"acceptance_or_required_evidence":c,"result":"NOT EXECUTED","evidence":"REQUIRED","authority":AUTHORITY,"warning":WARNING} for a,b,c in tests]


def write_cad() -> None:
    import cadquery as cq
    from cadquery.occ_impl.exporters.assembly import exportAssembly, exportGLTF
    assembly = cq.Assembly(name="HR30_MEASUREMENT_CHAIN_CALIBRATION_FIXTURE")
    enclosure = cq.Workplane("XY").box(121,94,34).translate((0,0,17))
    lid = cq.Workplane("XY").box(137,94,2).translate((0,0,35))
    board = cq.Workplane("XY").box(104,76,1.6).translate((0,0,8))
    assembly.add(enclosure, name="HAMMOND_1591GFLBK_ENVELOPE", color=cq.Color(0.05,0.13,0.28,0.35))
    assembly.add(lid, name="FLANGED_LID", color=cq.Color(0.05,0.13,0.28,0.45))
    assembly.add(board, name="PASSIVE_BREAKOUT_PCB", color=cq.Color(0.05,0.45,0.22))
    for name, x, y, angle in (("JPS",-36,0,0),("JDUT",36,0,0)):
        connector = cq.Workplane("XY").box(12,10,9).translate((x,y,13))
        assembly.add(connector, name=name, color=cq.Color(0.16,0.55,0.30))
    for name, x, color in (("JHI_RED",-9,cq.Color(0.85,0.05,0.05)),("JLO_BLACK",9,cq.Color(0.04,0.04,0.04))):
        jack = cq.Workplane("XY").box(12,33,14.9).translate((x,30,16))
        assembly.add(jack, name=name, color=color)
    if not exportAssembly(assembly, str(OUT / "HR30_measurement_chain_calibration_fixture_candidate.step")):
        raise RuntimeError("STEP export failed")
    if not exportGLTF(assembly, str(OUT / "HR30_measurement_chain_calibration_fixture_candidate.glb"), binary=True):
        raise RuntimeError("GLB export failed")


def make_svg() -> None:
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="760" viewBox="0 0 1600 760"><rect width="1600" height="760" fill="#f7fbff"/><style>text{{font-family:system-ui,Segoe UI,sans-serif;fill:#0b1d35}}.h{{font-size:36px;font-weight:900}}.t{{font-size:18px;font-weight:800}}.s{{font-size:14px}}.box{{fill:#fff;stroke:#082d67;stroke-width:3}}.fixture{{fill:#e4f6ff;stroke:#145ca8;stroke-width:4}}.wire{{stroke:#145ca8;stroke-width:5;fill:none}}.ref{{stroke:#d39b00;stroke-width:5;fill:none}}.warn{{fill:#ffc83d;stroke:#6e4d00;stroke-width:3}}</style><text class="h" x="48" y="56">Off-robot calibration of one complete floating measurement lane</text><rect class="warn" x="48" y="78" width="1504" height="58" rx="10"/><text class="t" x="72" y="113">UNBUILT - ROBOT CONNECTION PROHIBITED - NUMERIC ACCEPTANCE LIMITS OPEN - ZERO SAFETY CREDIT</text><rect class="box" x="55" y="270" width="245" height="150" rx="16"/><text class="t" x="80" y="312">Keysight E36313A</text><text class="s" x="80" y="345">Output 2 or 3 / isolated check</text><text class="s" x="80" y="375">0-24 V points / 10 mA candidate</text><rect class="fixture" x="365" y="235" width="320" height="220" rx="18"/><text class="t" x="392" y="280">Passive calibration fixture</text><text class="s" x="392" y="315">JPS source - JHI/JLO DMM - JDUT out</text><text class="s" x="392" y="345">104 x 76 mm routed PCB</text><text class="s" x="392" y="375">Pomona safety jacks / 1591GFLBK</text><path class="wire" d="M300 330 H365"/><rect class="box" x="390" y="520" width="270" height="120" rx="16"/><text class="t" x="420" y="560">Fluke 87V MAX CAL</text><text class="s" x="420" y="590">TL930 red/black patch pair</text><path class="ref" d="M525 520 V455"/><rect class="box" x="755" y="270" width="205" height="150" rx="16"/><text class="t" x="785" y="312">One DP pod</text><text class="s" x="785" y="345">2 x 100 kOhm / lead</text><text class="s" x="785" y="375">source tail disconnected</text><path class="wire" d="M685 330 H755"/><rect class="box" x="1025" y="270" width="205" height="150" rx="16"/><text class="t" x="1055" y="312">3 m cable + panel</text><text class="s" x="1055" y="345">one floating lane</text><text class="s" x="1055" y="375">10.2 kOhm / lead</text><path class="wire" d="M960 330 H1025"/><rect class="box" x="1295" y="270" width="250" height="150" rx="16"/><text class="t" x="1325" y="312">NI-9229 channel</text><text class="s" x="1325" y="345">raw differential samples</text><text class="s" x="1325" y="375">gain/offset/uncertainty fit</text><path class="wire" d="M1230 330 H1295"/><text class="t" x="55" y="700">Repeat sequentially for CH-AI-01 through CH-AI-08. Seven fixture inputs remain disconnected at every run.</text></svg>'''
    (OUT / "off-robot-calibration-architecture.svg").write_text(svg + "\n", encoding="utf-8")


def table_html(filename: str, title: str) -> str:
    with (OUT / filename).open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    fields = list(rows[0]); head = "".join(f"<th>{html.escape(x.replace('_',' ').title())}</th>" for x in fields)
    body = "".join("<tr>" + "".join(f"<td>{html.escape(row[x])}</td>" for x in fields) + "</tr>" for row in rows)
    return f'<section><h2>{html.escape(title)}</h2><div class="table"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div></section>'


def make_html() -> None:
    tables = "".join([
        table_html("calibration-channel-register.csv","Eight sequential channel builds"),
        table_html("calibration-point-register.csv","Calibration point schedule"),
        table_html("procedure-register.csv","Controlled off-robot procedure"),
        table_html("fault-injection-register.csv","Safe bench fault characterization"),
        table_html("candidate-bom.csv","Candidate BOM"),
        table_html("open-holds.csv","Open before any execution or robot connection"),
    ])
    (OUT / "index.html").write_text(f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 measurement-chain calibration fixture</title><script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/4.1.0/model-viewer.min.js"></script><style>:root{{--sky:#9ddcff;--blue:#082d67;--mid:#145ca8;--gold:#ffc83d;--ink:#0b1d35;--paper:#f7fbff}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.55 system-ui,Segoe UI,sans-serif}}header{{padding:clamp(28px,6vw,72px);background:linear-gradient(135deg,var(--blue),var(--mid));color:white}}h1{{font-size:clamp(38px,6vw,70px);line-height:1.03;max-width:1100px}}main{{max-width:1500px;margin:auto;padding:clamp(18px,4vw,52px)}}.warning{{background:var(--gold);color:#221800;padding:16px;border:3px solid #6e4d00;font-weight:900}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:18px}}article{{background:white;border:2px solid var(--blue);border-radius:16px;padding:20px;box-shadow:6px 6px 0 var(--sky)}}.hold{{background:#fff3c8}}.metric{{font-size:clamp(32px,4vw,54px);font-weight:900;color:var(--blue)}}section{{margin:44px 0}}h2{{font-size:clamp(28px,3vw,42px);color:var(--blue)}}.diagram,.table,.viewer{{overflow:auto;background:white;border:2px solid var(--blue);border-radius:14px}}object{{display:block;width:100%;min-width:1100px;min-height:540px}}model-viewer{{width:100%;height:540px;background:radial-gradient(circle,#fff,#e4f6ff)}}.pcb{{display:block;width:min(100%,1100px);margin:auto;background:white}}table{{border-collapse:collapse;width:max-content;min-width:100%}}th,td{{padding:12px 14px;border-bottom:1px solid #a8c4e4;vertical-align:top;max-width:520px}}th{{position:sticky;top:0;background:var(--blue);color:white;font-size:14px;text-align:left}}td{{font-size:16px}}a{{color:#064e9d;font-weight:800}}@media(max-width:650px){{body{{font-size:16px}}th,td{{min-width:180px}}}}</style></head><body><header><div class="warning">{html.escape(WARNING)}</div><p>HR-30 / FER-G11 / pre-connection metrology</p><h1>Calibrate the entire voltage-measurement chain without touching the robot.</h1><p>A passive three-port fixture drives one floating pod, cable, panel lane and NI input at a time while an independent calibrated meter records the real source voltage.</p></header><main><section class="grid"><article><div class="metric">1</div><h2>lane at a time</h2><p>No channel returns are joined. Seven source inputs remain disconnected during every run.</p></article><article><div class="metric">72 x 3</div><h2>scheduled samples</h2><p>Nine points on eight lanes, each repeated three times, preserve zero-return and hysteresis evidence.</p></article><article><div class="metric">0-24 V</div><h2>source envelope</h2><p>The exact candidate source covers the whole planned signal range. A 10 mA setting is provisional until reviewed and verified.</p></article><article class="hold"><div class="metric">0</div><h2>robot connections</h2><p>This fixture is for disconnected chains only. Source taps, numeric limits, build and qualified review remain open.</p></article></section><section><h2>Physical test architecture</h2><div class="diagram"><object data="off-robot-calibration-architecture.svg" type="image/svg+xml" aria-label="Off-robot measurement calibration architecture"></object></div></section><section><h2>Native routed PCB</h2><div class="diagram"><img class="pcb" src="output/{PROJECT}-top.png" alt="Top render of the passive three-port calibration fixture PCB"></div></section><section><h2>Fixture packaging candidate</h2><div class="viewer"><model-viewer src="HR30_measurement_chain_calibration_fixture_candidate.glb" camera-controls auto-rotate shadow-intensity="1" alt="HR-30 passive measurement calibration fixture"></model-viewer></div></section><section class="grid"><article><h2>What becomes measurable</h2><p>Per-channel gain, offset, residuals, polarity, open-lead signature, noise, crosstalk and repeatability across the assembled pod-to-NI chain.</p></article><article><h2>What remains outside this fixture</h2><p>Robot source-terminal loading, safety-circuit behavior, the short upstream source tails, real switching transients and all motion or stop-time measurements.</p></article><article class="hold"><h2>No paper pass</h2><p>The fixture and every cable are unbuilt. The schedule defines evidence; it does not manufacture calibration results.</p></article></section>{tables}<section><h2>Engineering files</h2><p><a href="{PROJECT}.kicad_pro">KiCad project</a> · <a href="board/{PROJECT}.kicad_pcb">routed PCB</a> · <a href="HR30_measurement_chain_calibration_fixture_candidate.step">STEP</a> · <a href="calibration-point-register.csv">point schedule</a> · <a href="data-schema-register.csv">data schema</a> · <a href="primary-source-register.csv">manufacturer sources</a></p></section></main></body></html>''', encoding="utf-8")


def integrate() -> None:
    status_path = WHOLE / "package-status.json"; status = json.loads(status_path.read_text(encoding="utf-8"))
    status.update({"measurement_chain_calibration_fixture_candidate_present":True,"measurement_chain_calibration_fixture_native_kicad":True,"measurement_chain_calibration_fixture_off_robot_only":True,"measurement_chain_calibration_fixture_built":False,"measurement_chain_calibration_executed":False,"measurement_chain_calibration_accepted":False,"measurement_boundary_panel_calibrated":False,"measurement_harness_calibrated":False,"fer_g11_closed":False,"connection_authority":False,"energization_authority":False})
    status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    start, end = "<!-- HR30-MEASUREMENT-CAL-FIXTURE-P01-START -->", "<!-- HR30-MEASUREMENT-CAL-FIXTURE-P01-END -->"
    readme = WHOLE / "README.md"; text = readme.read_text(encoding="utf-8")
    if start in text and end in text:
        text = text.split(start,1)[0] + text.split(end,1)[1]
    block = f'''{start}\n## Off-robot measurement-chain calibration fixture\n\nThe [interactive calibration-fixture guide](electrical/{OUT.name}/index.html) adds a routed **104 x 76 mm native KiCad passive breakout** and a 121 x 94 x 34 mm enclosure candidate. It sequentially drives one disconnected diagnostic pod, three-metre cable, panel lane and NI-9229 input while an in-date Fluke 87V MAX CAL records the actual Keysight E36313A source voltage. The 72-point, three-repeat schedule covers gain, offset, polarity, open-lead behavior, noise and crosstalk without connecting to the robot. Hardware build, instrument receipt/calibration, numeric acceptance limits, execution, uncertainty review, source taps and FER-G11 remain open.\n{end}\n'''
    readme.write_text(text.rstrip() + "\n\n" + block, encoding="utf-8")
    page = WHOLE / "index.html"; text = page.read_text(encoding="utf-8")
    if start in text and end in text:
        text = text.split(start,1)[0] + text.split(end,1)[1]
    section = f'''{start}<section id="measurement-calibration-fixture"><h2>The entire measurement chain can now be calibrated off-robot</h2><div class="grid"><article class="card pass"><div class="metric">72 x 3</div><p>scheduled calibration observations cover all eight floating voltage lanes.</p></article><article class="card pass"><h3>One lane at a time</h3><p>The passive fixture never joins channel returns and never connects to the robot.</p></article><article class="card hold"><h3>Execution remains open</h3><p>Build, calibrated received equipment, numeric limits, uncertainty review and FER-G11 are not complete.</p></article></div><p><a href="electrical/{OUT.name}/index.html">Open the interactive off-robot calibration guide</a>.</p></section>{end}'''
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
    # KiCad's SVG writer leaves cosmetic end-of-line spaces.  Normalize the
    # checked-in web exports without changing their rendered content.
    for svg in output.glob("*.svg"):
        svg.write_text("\n".join(line.rstrip() for line in svg.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")
    run([str(KICAD), "pcb", "render", "--output", str(output / f"{PROJECT}-top.png"), "--width", "1600", "--height", "1000", "--side", "top", "--background", "opaque", str(OUT / "board" / f"{PROJECT}.kicad_pcb")])
    write_csv(OUT / "fixture-port-register.csv", port_rows())
    write_csv(OUT / "calibration-channel-register.csv", channel_rows())
    write_csv(OUT / "calibration-point-register.csv", point_rows())
    write_csv(OUT / "procedure-register.csv", procedure_rows())
    write_csv(OUT / "fault-injection-register.csv", fault_rows())
    write_csv(OUT / "data-schema-register.csv", data_rows())
    write_csv(OUT / "candidate-bom.csv", bom_rows())
    write_csv(OUT / "primary-source-register.csv", source_rows())
    write_csv(OUT / "inspection-test-register.csv", inspection_rows())
    write_csv(OUT / "open-holds.csv", hold_rows())
    binding = {"identifier":IDENTIFIER,"date":DATE,"warning":WARNING,"diagnostic_pod_channels_sha256":sha(PODS / "source-node-register.csv"),"diagnostic_pod_scale_sha256":sha(PODS / "end-to-end-scale-register.csv"),"measurement_panel_channels_sha256":sha(PANEL / "channel-register.csv"),"measurement_harness_endpoints_sha256":sha(HARNESS / "channel-endpoint-register.csv"),"instrument_register_sha256":sha(INSTR / "instrument-register.csv"),"scope":"OFF-ROBOT ONE-CHANNEL-AT-A-TIME CALIBRATION FIXTURE; NO ROBOT OR SAFETY-CIRCUIT CONNECTION"}
    (OUT / "source-binding.json").write_text(json.dumps(binding, indent=2) + "\n", encoding="utf-8")
    status = {"identifier":IDENTIFIER,"date":DATE,"warning":WARNING,"channel_count":8,"simultaneous_fixture_channels":1,"scheduled_points":72,"repeats_per_point":3,"native_kicad_sheet_count":2,"erc_errors":0,"erc_warnings":0,"drc_violations":0,"robot_connection_permitted":False,"fixture_built":False,"fixture_inspection_executed":False,"instrument_calibration_verified":False,"calibration_executed":False,"uncertainty_accepted":False,"numeric_acceptance_limits_released":False,"fer_g11_closed":False,"functional_safety_credit":False,"procurement_authority":False,"fabrication_authority":False,"assembly_authority":False,"connection_authority":False,"powered_robot_test_authority":False,"motion_authority":False,"walking_authority":False,"energization_authority":False}
    (OUT / "calibration-fixture-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    (OUT / "README.md").write_text(f'''# HR-30 measurement-chain calibration fixture P0.1\n\n**{WARNING}**\n\nThis package defines a passive one-channel source breakout for calibrating the complete disconnected diagnostic chain: one source-local pod, its three-metre cable, one measurement-panel lane, its harness and one NI-9229 input. A Keysight E36313A candidate provides 0-24 V points with a provisional 10 mA current limit. A Fluke 87V MAX CAL candidate independently measures the actual source through exact Pomona 73099-2/73099-0 PCB safety-jack and Fluke TL930 patch-cord candidates.\n\nThe fixture has no PE, chassis, USB, robot or safety-circuit connection. Exactly one lane is driven at a time. The point schedule, fault-characterization adapters, data schema, routed PCB and physical enclosure model are design artifacts only. Build, received-part FAI, calibration, numeric acceptance limits, uncertainty review, source-terminal taps, FER-G11 and every robot work authority remain open.\n''', encoding="utf-8")
    write_cad(); make_svg(); make_html()
    shutil.copy2(Path(__file__), OUT / "measurement-chain-calibration-fixture-source.py")
    shutil.copy2(ROOT / "tools" / "check_hr30_measurement_chain_calibration_fixture_p01.py", OUT / "measurement-chain-calibration-fixture-checker.py")
    files = [p for p in OUT.rglob("*") if p.is_file() and p.name != "file-manifest.csv"]
    write_csv(OUT / "file-manifest.csv", [{"path":p.relative_to(OUT).as_posix(),"bytes":p.stat().st_size,"sha256":sha(p),"warning":WARNING} for p in sorted(files)])
    if RELEASE.exists(): shutil.rmtree(RELEASE)
    shutil.copytree(OUT, RELEASE)
    integrate()
    code = "import sys;sys.path.insert(0,'tools');import generate_hr30_system_package_p01 as s;s.refresh_manifest_and_release()"
    run([str(CAD_PYTHON), "-c", code])
    print(json.dumps({"identifier":IDENTIFIER,"channels":8,"points":72,"repeats":3,"erc":"0/0","drc":0,"robot_connection":False,"fer_g11":False,"authorities":0}, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--pcb", action="store_true"); args = parser.parse_args()
    if args.pcb: return pcb_mode()
    write_package(); return 0


if __name__ == "__main__":
    raise SystemExit(main())
