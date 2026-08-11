#!/usr/bin/env python3
"""Generate R211/P0.5 power-state-corrected observation carrier.

P0.5 replaces the hard-enabled push-pull SN74LVC1G125 stage with the
open-drain SN74LVC1G07.  Each channel gains an exact 10 kohm pull-up ahead
of the retained 39 kohm GPIO fault limiter.  The candidate remains an
ordinary diagnostic with no work or safety authority.
"""

from __future__ import annotations

import csv
import hashlib
import html
import importlib.util
import json
import math
import sys
from collections import Counter
from pathlib import Path

import pcbnew


ROOT = Path(__file__).resolve().parents[1]
P03_TOOL = ROOT / "tools/generate_hr_v0_runtime_observation_carrier_p03.py"
ECAD = ROOT / "electrical/kicad/hr-v0-runtime-observation-carrier-p0.5"
WEB = ROOT / "release/hr-v0/runtime-observation-carrier-p0.5"
DOC = ROOT / "docs/hr-v0-runtime-observation-carrier-p0.5.md"
PROJECT = "hr-v0-runtime-observation-carrier-p0.5"
IDENTIFIER = "HR-V0-RUNTIME-OBS-CARRIER-P0.5"
REV = "R211 / P0.5 / PCB-P0.4"
DATE = "2026-08-10"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
BUFFER_MPN = "Texas Instruments SN74LVC1G07DBVR"
RPU_VALUE = "10.0 kohm 1% 0.125 W 0805"
RPU_MPN = "Panasonic ERJ6ENF1002V"
CHANNELS = [(1, "SR1", "UOBS1", "4", "3"), (2, "SRA1", "UOBS1", "5", "4"), (3, "K1", "UOBS2", "4", "5"), (4, "K2", "UOBS2", "5", "6")]


def load_p03():
    spec = importlib.util.spec_from_file_location("obs_p03_for_p05", P03_TOOL)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {P03_TOOL}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def exact_dbv_land(p03, legacy) -> pcbnew.FOOTPRINT:
    fp = pcbnew.FOOTPRINT(None)
    fp.SetFPID(pcbnew.LIB_ID(p03.LIB_NAME, p03.BUFFER_FOOTPRINT))
    fp.SetValue(p03.BUFFER_FOOTPRINT)
    for number, x, y in (("1", -1.30, -0.95), ("2", -1.30, 0.0), ("3", -1.30, 0.95), ("4", 1.30, 0.95), ("5", 1.30, -0.95)):
        legacy.add_smd_pad(fp, number, x, y, 1.10, 0.60, 0.07)
    legacy.add_outline(fp, -1.75, -1.45, 1.75, 1.45)
    fp.Reference().SetVisible(False)
    fp.Value().SetVisible(False)
    return fp


def configure(p03) -> None:
    p03.ECAD = ECAD; p03.WEB = WEB; p03.DOC = DOC; p03.PROJECT = PROJECT
    p03.IDENTIFIER = IDENTIFIER; p03.REV = REV; p03.DATE = DATE
    p03.LIB_NAME = "PB_RUNTIME_OBS_P05"; p03.LIB_DIR = ECAD / "PB_RUNTIME_OBS_P05.pretty"
    p03.BUFFER_MPN = BUFFER_MPN
    p03.RGP_VALUE = "39.0 kohm 1% 0.125 W 0805"; p03.RGP_MPN = "Panasonic ERJ6ENF3902V"
    retained = [row for row in p03.NEW_SOURCES if row[0] not in {"OBS3-SRC-016", "OBS3-SRC-017", "OBS3-SRC-020"}]
    p03.NEW_SOURCES = retained + [
        ("OBS5-SRC-016", "Texas Instruments", "SN74LVC1G07 datasheet", "SCES296AG Rev AG", "2025-10; package addendum 2026-07-15; rechecked 2026-08-10", "https://www.ti.com/lit/ds/symlink/sn74lvc1g07.pdf", "Open-drain truth table, DBV pins, Ioff, DC limits, timing and active orderable record"),
        ("OBS5-SRC-017", "Texas Instruments", "SN74LVC1G07 product record", "ACTIVE catalog product", "rechecked 2026-08-10", "https://www.ti.com/product/SN74LVC1G07", "Exact active open-drain buffer family; procurement and application approval remain open"),
        ("OBS5-SRC-020", "Panasonic Industry", "ERJ6ENF3902V product record", "39.0 kohm 1% 0805; TCR +/-100 ppm/K", "rechecked 2026-08-10", "https://industrial.panasonic.com/ww/products/pt/general-purpose-chip-resistors/models/ERJ6ENF3902V", "Exact GPIO series candidate"),
        ("OBS5-SRC-022", "Texas Instruments", "DBV0005A package drawing and board-layout example", "4214839/K", "2024-08; rechecked 2026-08-10", "https://www.ti.com/lit/ds/symlink/sn74lvc1g07.pdf", "Five 1.10 x 0.60 mm lands, 0.95 mm pitch, 1.90 mm row span and 2.60 mm row-center spacing"),
        ("OBS5-SRC-023", "Panasonic Industry", "ERJ6ENF1002V product record", "10.0 kohm 1% 0805; TCR +/-100 ppm/K", "rechecked 2026-08-10", "https://industrial.panasonic.com/ww/products/pt/general-purpose-chip-resistors/models/ERJ6ENF1002V", "Exact open-drain pull-up candidate"),
        ("OBS5-SRC-024", "Raspberry Pi Ltd", "RP1 Peripherals", "current public RP1 register reference", "rechecked 2026-08-10", "https://datasheets.raspberrypi.com/rp1/rp1-peripherals.pdf", "Bank0 defaults to 3.3 V selection; pad drive settings are 2/4/8/12 mA; no VIH/VIL/leakage/clamp limits published"),
        ("OBS5-SRC-025", "Raspberry Pi Ltd", "Raspberry Pi HAT+ Specification", "release 2024-12-05", "rechecked 2026-08-10", "https://datasheets.raspberrypi.com/hat/hat_plus_specification.pdf", "40-pin 3V3/5V power-state boundary and STANDBY compatibility requirement; P0.5 is not claimed as a HAT+"),
    ]
    p03.HOLDS = [
        ("OBS5-HOLD-001", "R202 inherited field application", "Close every P0.2 Y32, H1, K1/K2 wetting, EMC, grounding and thermal hold against received parts"),
        ("OBS5-HOLD-002", "Pi 3V3 envelope", "Obtain Raspberry Pi application acceptance for the 7.612 mA screen and measure startup, steady, brownout, STANDBY and shutdown rail behavior"),
        ("OBS5-HOLD-003", "Pi GPIO DC interface", "Obtain authoritative RP1 VIH, VIL, leakage, capacitance, clamp and unpowered-pin limits or configuration-specific Raspberry Pi acceptance"),
        ("OBS5-HOLD-004", "open-drain application", "Qualified electrical review of SN74LVC1G07DBVR, the 10k/39k/330k network, Ioff, transition rate, delta-ICC, faults and thermal screens"),
        ("OBS5-HOLD-005", "PCB DFM", "Selected fabricator accepts TI 4214839/K DBV-5 and Panasonic 0805 lands, four-layer stack, spacing, mask, legend, holes, zones and board drawing"),
        ("OBS5-HOLD-006", "assembly process", "Selected assembler accepts stencil, paste, solder alloy/profile, cleaning, AOI, rework and first-article controls"),
        ("OBS5-HOLD-007", "harness timing and EMC", "Measure installed conductor capacitance, rise/fall time, crosstalk, actuator-current interference, routing and separation"),
        ("OBS5-HOLD-008", "partial power and back-power", "Execute OFF, 5V-only STANDBY, ramp, active, brownout, shutdown, field-only, open, short-to-return, short-to-3V3 and cross-short cases"),
        ("OBS5-HOLD-009", "received identity", "Inspect exact UOBS1/UOBS2/UBUF1-UBUF4/resistor/capacitor/terminal identities, markings, orientation and damage"),
        ("OBS5-HOLD-010", "unpowered board inspection", "Inspect dimensions, holes, lands, isolation corridor, continuity, shorts, residue and no unintended field/compute bond"),
        ("OBS5-HOLD-011", "powered isolated fixture", "Execute voltage, current, truth-table, rail, thermal and timing tests only under a separately authorized isolated fixture procedure"),
        ("OBS5-HOLD-012", "software fail-closed behavior", "Prove every unknown or invalid observation inhibits ordinary heartbeat/motion authority and cannot create a restart"),
        ("OBS5-HOLD-013", "safety boundary", "Qualified reviewer confirms the entire observation path remains ordinary diagnostic circuitry with zero safety credit"),
        ("OBS5-HOLD-014", "work authority", "Separate written authorization is required before procurement, fabrication, assembly, connection or powered testing"),
    ]
    p03.LOADS = [
        ("OBS5-LOAD-001", "PI_3V3_CANDIDATE", "two ISO1212 logic sides", "2 x 1.9 mA maximum ICC1", "3.800 mA", "TI ISO1212 bound", "SCREEN ONLY"),
        ("OBS5-LOAD-002", "PI_3V3_CANDIDATE", "four SN74LVC1G07 static supplies", "4 x 10 uA maximum ICC", "0.040 mA", "does not include delta-ICC", "SCREEN ONLY"),
        ("OBS5-LOAD-003", "PI_3V3_CANDIDATE", "four LVC inputs near VCC-0.6", "4 x 0.5 mA maximum delta-ICC row", "2.000 mA", "conservative simultaneous-high screen", "SELECTION/MEASUREMENT REQUIRED"),
        ("OBS5-LOAD-004", "PI_3V3_CANDIDATE", "four 47k input pulldown paths", "4 x 3.6 V/(1.47015k+46.0647k)", "0.303 mA", "tolerance and TCR included", "SCREEN ONLY"),
        ("OBS5-LOAD-005", "PI_3V3_CANDIDATE", "four 10k pull-ups with outputs low", "4 x 3.6 V/9.801k", "1.469 mA", "tolerance and TCR included", "SCREEN ONLY"),
        ("OBS5-LOAD-006", "PI_3V3_CANDIDATE", "combined steady worst-case screen", "3.800 + 0.040 + 2.000 + 0.303 + 1.469", "7.612 mA", "not Pi 5 source approval; switching current absent", "SELECTION REQUIRED"),
    ]
    p03.make_sot23_5 = lambda legacy: exact_dbv_land(p03, legacy)


def build_schematic(p03, legacy, base) -> None:
    model = base.load_model(); pn, Component, Sheet = model.pn, model.Component, model.Sheet
    jfield = Component("JFIELD1", "Phoenix Contact MKDS 1/6-3,5 item 1751280", [pn("JFIELD1", "1", "SR1 STATUS", "SR1_STATUS", "right"), pn("JFIELD1", "2", "SRA1 STATUS", "SRA1_STATUS", "right"), pn("JFIELD1", "3", "K1 STATUS", "K1_STATUS", "right"), pn("JFIELD1", "4", "K2 STATUS", "K2_STATUS", "right"), pn("JFIELD1", "5", "FIELD RETURN", "SAFETY_0V", "right"), pn("JFIELD1", "6", "N/C", "INTENTIONALLY_UNUSED_JFIELD1_6", "right")], "EXACT PCB TERMINAL CANDIDATE - PHYSICAL HOLD", "R202 numbering retained; no harness or connection release.", position=(76, 92), width=74, footprint=f"{p03.LIB_NAME}:Phoenix_MKDS_1_6_3P5_1751280")
    jlogic = Component("JLOGIC1", "Phoenix Contact MKDS 1/6-3,5 item 1751280", [pn("JLOGIC1", "1", "PI 3V3 CANDIDATE", "PI_3V3_CANDIDATE", "left"), pn("JLOGIC1", "2", "COMPUTE RETURN", "COMPUTE_0V", "left"), pn("JLOGIC1", "3", "OBS SR1", "OBS_SR1_PI", "left"), pn("JLOGIC1", "4", "OBS SRA1", "OBS_SRA1_PI", "left"), pn("JLOGIC1", "5", "OBS K1", "OBS_K1_PI", "left"), pn("JLOGIC1", "6", "OBS K2", "OBS_K2_PI", "left")], "EXACT PCB TERMINAL CANDIDATE - PI/HARNESS/PHYSICAL HOLD", "Open-drain outputs; Pi DC acceptance remains open.", position=(300, 92), width=74, footprint=f"{p03.LIB_NAME}:Phoenix_MKDS_1_6_3P5_1751280")
    s1 = Sheet(1, "01_boundaries.kicad_sch", "Field and compute boundaries", "R202 connector numbering retained; power-state-corrected outputs on page 4.", compact=True); s1.components = [jfield, jlogic]; s1.notes = ["SAFETY_0V and COMPUTE_0V remain distinct.", "All observations are ordinary diagnostics with zero safety credit."]
    u1 = base.iso1212(model, "UOBS1", "SR1", "SRA1", "OBS_SR1_RAW", "OBS_SRA1_RAW", (210, 136))
    s2 = Sheet(2, "02_sr1_sra1_inputs.kicad_sch", "SR1 and SRA1 Type-3 inputs", "Inherited field network; received H1/Y32 evidence remains held.", compact=True); s2.components = base.channel_parts(model, 1, "SR1_STATUS", "SR1", 62, False) + [u1] + base.channel_parts(model, 2, "SRA1_STATUS", "SRA1", 360, True)
    u2 = base.iso1212(model, "UOBS2", "K1", "K2", "OBS_K1_RAW", "OBS_K2_RAW", (210, 136))
    s3 = Sheet(3, "03_k1_k2_inputs.kicad_sch", "K1 and K2 diagnostic auxiliary inputs", "Inherited field network; contact evidence remains held.", compact=True); s3.components = base.channel_parts(model, 3, "K1_STATUS", "K1", 62, True) + [u2] + base.channel_parts(model, 4, "K2_STATUS", "K2", 360, True)
    outputs, buffers = [], []
    for index, name, _uref, _upin, _jpin in CHANNELS:
        x = 42 + (index - 1) * 108
        outputs.extend([
            base.resistor(model, f"RSO{index}", p03.RSO_VALUE, p03.RSO_MPN, f"OBS_{name}_RAW", f"OBS_{name}_BUF_IN", (x, 56), "ISO OUTPUT FAULT LIMIT"),
            base.resistor(model, f"RPD{index}", p03.RIN_VALUE, p03.RIN_MPN, f"OBS_{name}_BUF_IN", "COMPUTE_0V", (x, 104), "BUFFER INPUT FAIL-LOW"),
            base.resistor(model, f"RPU{index}", RPU_VALUE, RPU_MPN, f"OBS_{name}_BUF_OUT", "PI_3V3_CANDIDATE", (x, 170), "OPEN-DRAIN PULL-UP"),
            base.resistor(model, f"RGP{index}", p03.RGP_VALUE, p03.RGP_MPN, f"OBS_{name}_BUF_OUT", f"OBS_{name}_PI", (x, 212), "GPIO PATH FAULT LIMIT"),
            base.resistor(model, f"RPO{index}", p03.RPO_VALUE, p03.RPO_MPN, f"OBS_{name}_PI", "COMPUTE_0V", (x, 254), "CARRIER-SIDE FAIL-LOW"),
        ])
        ref = f"UBUF{index}"
        buffers.append(Component(ref, BUFFER_MPN, [pn(ref, "1", "N/C", f"INTENTIONALLY_UNUSED_{ref}_1", "left"), pn(ref, "2", f"A {name}", f"OBS_{name}_BUF_IN", "left"), pn(ref, "3", "GND", "COMPUTE_0V", "left"), pn(ref, "4", f"Y OPEN DRAIN {name}", f"OBS_{name}_BUF_OUT", "right"), pn(ref, "5", "VCC", "PI_3V3_CANDIDATE", "right")], "EXACT OPEN-DRAIN CANDIDATE - APPLICATION/PCB/PHYSICAL HOLD", "No OE pin; Ioff supports partial power down. Zero safety credit.", "https://www.ti.com/lit/ds/symlink/sn74lvc1g07.pdf", "SCES296AG Rev AG; rechecked 2026-08-10", position=(x, 136), width=86, footprint=f"{p03.LIB_NAME}:{p03.BUFFER_FOOTPRINT}"))
    cdec = [Component(f"CDEC{index}", "100 nF 50 V X7R; Murata GRM21BR71H104KA01L", [pn(f"CDEC{index}", "1", "VCC", "PI_3V3_CANDIDATE", "left"), pn(f"CDEC{index}", "2", "GND", "COMPUTE_0V", "right")], "EXACT DECOUPLING CANDIDATE - PLACEMENT/PHYSICAL HOLD", f"Local bypass for {purpose}; physical evidence remains open.", position=(70 + index * 70, 294), width=64, footprint=f"{p03.LIB_NAME}:Murata_GRM21_Reflow_Nominal") for index, purpose in ((1, "UOBS1"), (2, "UOBS2"), (3, "UBUF1"), (4, "UBUF2"), (5, "UBUF3"), (6, "UBUF4"))]
    s4 = Sheet(4, "04_compute_outputs.kicad_sch", "Open-drain fail-low compute outputs", "No OE sequencing path; Pi acceptance remains open.", compact=True); s4.components = [*outputs, *buffers, *cdec]; s4.notes = ["RPU=10k is ahead of the retained 39k GPIO limiter; RPO=330k remains carrier-side bias.", "P0.5 removes positive drive into the Pi pin; physical power-state proof remains held."]
    sheets = [s1, s2, s3, s4]; items = [c for s in sheets for c in s.components]; counts = Counter(pin.net for c in items for pin in c.pins); wire_numbers = model.build_wire_numbers(sheets, counts)
    ECAD.mkdir(parents=True, exist_ok=True)
    for stale in ECAD.glob("*.kicad_sch"): stale.unlink()
    project_data = {"board": {}, "boards": [], "cvpcb": {}, "erc": {}, "libraries": {}, "meta": {"filename": f"{PROJECT}.kicad_pro", "version": 1}, "net_settings": {"classes": [], "meta": {"version": 3}}, "pcbnew": {}, "schematic": {}, "text_variables": {"PROJECT_STATUS": WARNING, "REVISION": REV}}
    (ECAD / f"{PROJECT}.kicad_pro").write_text(json.dumps(project_data, indent=2) + "\n", encoding="utf-8")
    symbols = [model.lib_symbol(c).replace(f'(symbol "PBV3:{c.ref}"', f'(symbol "{c.ref}"', 1) for c in items]
    (ECAD / f"{PROJECT}.kicad_sym").write_text('(kicad_symbol_lib\n  (version 20251024) (generator "kicad_symbol_editor") (generator_version "10.0")\n  ' + "\n".join(symbols) + "\n)\n", encoding="utf-8")
    (ECAD / "sym-lib-table").write_text(f'(sym_lib_table\n  (version 7)\n  (lib (name "PBV3")(type "KiCad")(uri "${{KIPRJMOD}}/{PROJECT}.kicad_sym")(options "")(descr "R211 open-drain observation symbols"))\n)\n', encoding="utf-8")
    root_uuid = model.uid("root-hr-v0-runtime-observation-carrier-p05")
    (ECAD / f"{PROJECT}.kicad_sch").write_text(model.root_schematic(root_uuid, sheets), encoding="utf-8")
    for sheet in sheets: (ECAD / sheet.filename).write_text(model.child_schematic(root_uuid, sheet, counts, wire_numbers), encoding="utf-8")
    p03.write_csv(ECAD / "connector-schedule.csv", ["sheet", "reference", "terminal", "function", "net", "state"], [(s.filename, c.ref, p.number, p.name, p.net, c.status) for s in sheets for c in s.components for p in c.pins])
    p03.write_csv(ECAD / "bom.csv", ["reference", "value", "quantity", "state"], [(c.ref, c.value, str(c.quantity), c.status) for c in items if c.quantity])
    p03.write_csv(ECAD / "net-schedule.csv", ["net", "node_count", "nodes"], [(net, str(count), " | ".join(f"{s.filename}:{c.ref}:{p.number}" for s in sheets for c in s.components for p in c.pins if p.net == net)) for net, count in sorted(counts.items())])
    p03.write_csv(ECAD / "load-budget.csv", ["load_id", "net", "architecture", "basis", "result", "limit", "state"], p03.LOADS)
    p03.write_csv(ECAD / "selection-holds.csv", ["hold_id", "scope", "evidence_required"], p03.HOLDS)
    p03.write_csv(ECAD / "source-register.csv", ["source_id", "manufacturer", "document", "revision", "date", "official_url", "use_and_limit"], legacy.SOURCES)


def _point_equal(a, b, tolerance=5):
    return abs(a.x - b.x) <= tolerance and abs(a.y - b.y) <= tolerance


def correct_board(p03, legacy, original_build_board) -> dict[str, object]:
    summary = original_build_board(legacy)
    board_path = ECAD / f"{PROJECT}.kicad_pcb"; board = pcbnew.LoadBoard(str(board_path))
    footprints = {fp.GetReference(): fp for fp in board.GetFootprints()}; nets = {str(name): net for name, net in board.GetNetsByName().items()}
    for index, name, *_ in CHANNELS:
        net_name = f"INTENTIONALLY_UNUSED_UBUF{index}_1"
        if net_name not in nets:
            net = pcbnew.NETINFO_ITEM(board, net_name); board.Add(net); nets[net_name] = net
        pad1 = next(p for p in footprints[f"UBUF{index}"].Pads() if p.GetNumber() == "1"); pad_pos = pad1.GetPosition()
        endpoint = None
        for item in list(board.GetTracks()):
            if isinstance(item, pcbnew.PCB_TRACK) and not isinstance(item, pcbnew.PCB_VIA) and item.GetNetname() == "COMPUTE_0V" and (_point_equal(item.GetStart(), pad_pos) or _point_equal(item.GetEnd(), pad_pos)):
                endpoint = item.GetEnd() if _point_equal(item.GetStart(), pad_pos) else item.GetStart(); board.Delete(item)
        if endpoint is not None:
            for item in list(board.GetTracks()):
                if isinstance(item, pcbnew.PCB_VIA) and item.GetNetname() == "COMPUTE_0V" and _point_equal(item.GetPosition(), endpoint): board.Delete(item)
        pad1.SetNet(nets[net_name]); footprints[f"UBUF{index}"].SetValue(BUFFER_MPN)
    for index, name, *_ in CHANNELS:
        lane = 66.0 - 8.0 * index; ref = f"RPU{index}"
        fp = pcbnew.FootprintLoad(str(p03.LIB_DIR), "Panasonic_ERJ6_Reflow_Nominal"); fp.SetReference(ref); fp.SetValue(f"{RPU_VALUE}; {RPU_MPN}"); fp.SetPosition(pcbnew.VECTOR2I_MM(102.0, lane - 0.8)); fp.SetOrientationDegrees(0)
        for pad in fp.Pads(): pad.SetNet(nets[f"OBS_{name}_BUF_OUT" if pad.GetNumber() == "1" else "PI_3V3_CANDIDATE"])
        board.Add(fp); footprints[ref] = fp
        def pxy(reference, number):
            pos = next(p for p in footprints[reference].Pads() if p.GetNumber() == number).GetPosition(); return pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y)
        rpu1, rpu2, rgp1 = pxy(ref, "1"), pxy(ref, "2"), pxy(f"RGP{index}", "1")
        via_a, via_b = (rpu1[0], rpu1[1] - 1.15), (rgp1[0] - 0.85, rpu1[1] - 1.15)
        legacy.add_track(board, nets[f"OBS_{name}_BUF_OUT"], [rpu1, via_a], pcbnew.F_Cu); legacy.add_via(board, nets[f"OBS_{name}_BUF_OUT"], via_a)
        legacy.add_track(board, nets[f"OBS_{name}_BUF_OUT"], [via_a, via_b], pcbnew.B_Cu); legacy.add_via(board, nets[f"OBS_{name}_BUF_OUT"], via_b)
        legacy.add_track(board, nets[f"OBS_{name}_BUF_OUT"], [via_b, rgp1], pcbnew.F_Cu)
        via = (rpu2[0], rpu2[1] - 1.15); legacy.add_track(board, nets["PI_3V3_CANDIDATE"], [rpu2, via], pcbnew.F_Cu, 0.30); legacy.add_via(board, nets["PI_3V3_CANDIDATE"], via)
    for drawing in board.GetDrawings():
        if isinstance(drawing, pcbnew.PCB_TEXT): drawing.SetText(drawing.GetText().replace("SN74LVC1G125DBVR", "SN74LVC1G07DBVR").replace("PCB-P0.2", "PCB-P0.4"))
    pcbnew.ZONE_FILLER(board).Fill(board.Zones()); pcbnew.SaveBoard(str(board_path), board)
    rows = []
    for fp in sorted(board.GetFootprints(), key=lambda item: item.GetReference()):
        pos = fp.GetPosition(); rows.append((fp.GetReference(), fp.GetFPID().GetLibItemName(), f"{pcbnew.ToMM(pos.x):.3f}", f"{pcbnew.ToMM(pos.y):.3f}", f"{fp.GetOrientationDegrees():.3f}", "TOP", "CANDIDATE - NOT RELEASED"))
    p03.write_csv(ECAD / "pcb-placement.csv", ["reference", "footprint", "x_mm", "y_mm", "rotation_deg", "side", "state"], rows)
    tracks = list(board.GetTracks()); summary.update({"footprints": len(rows), "mounted_components": len(rows)-4, "track_segments": sum(isinstance(x, pcbnew.PCB_TRACK) and not isinstance(x, pcbnew.PCB_VIA) for x in tracks), "vias": sum(isinstance(x, pcbnew.PCB_VIA) for x in tracks), "zones": len(list(board.Zones()))})
    return summary


def write_docs_web(p03, summary) -> None:
    rmin = lambda nominal: nominal * .99 * .99; rmax = lambda nominal: nominal * 1.01 * 1.01
    high = 3.0 * rmin(330000) / (rmax(10000) + rmax(39000) + rmin(330000)); low = .4 * rmin(330000) / (rmax(39000) + rmin(330000)); pullup_short = 3.6 / rmin(10000) * 1000
    calculations = [("ISO-side short", "3.6 V / (1.5k x .99 x .99)", "2.449 mA", "component screen only"), ("buffer-input HIGH", "2.6 V through 1.5k/47k extremes", "2.516 V", "above TI VIH=2.0 V"), ("open-drain HIGH at Pi node", "3.0 V through 10k/39k/330k extremes", f"{high:.3f} V", "RP1 VIH remains unpublished"), ("open-drain LOW at Pi node", "0.4 V through 39k/330k extremes", f"{low:.3f} V", "RP1 VIL remains unpublished"), ("pull-up hard short", "3.6 V / (10k x .99 x .99)", f"{pullup_short:.3f} mA", "bounded source-side fault"), ("steady 3V3 load screen", "ISO + ICC + delta-ICC + input bias + four pull-ups low", "7.612 mA", "not Pi 5 approval")]
    DOC.write_text(f"""# HR-V0 power-state-corrected runtime-observation carrier {REV}\n\n**{WARNING}**\n\nR211 supersedes P0.4 for current review. P0.4 hard-grounded the active-low OE pins of four `SN74LVC1G125DBVR` devices even though TI recommends a VCC pull-up when high impedance is required through power transitions. P0.5 removes that OE state entirely by using exact active `SN74LVC1G07DBVR` open-drain buffers. Each output has an exact Panasonic `ERJ6ENF1002V` 10.0 kohm pull-up to the same proposed Pi 3V3 rail, followed by the retained 39.0 kohm GPIO fault limiter and 330 kohm carrier-side fail-low bias.\n\nTI specifies the G07 for partial-power-down using Ioff and defines its DBV pin 1 as no-connect. When the carrier 3V3 supply is absent, the G07 output is high impedance and the pull-up source is absent with it; P0.5 therefore removes the prior positive push-pull source into the Pi pin. This is a topology improvement, not proof of Raspberry Pi compatibility.\n\nThe current official RP1 public reference defines 3.3 V bank selection and 2/4/8/12 mA drive settings but does not publish Pi 5/RP1 VIH, VIL, leakage, capacitance, clamp or unpowered-pin limits. The current HAT+ specification also requires tolerance of STANDBY with 5 V present and 3.3 V absent. Those limits and the 7.612 mA header-load screen require Raspberry Pi application acceptance and physical power-state testing. All fourteen holds remain open. Every channel remains an ordinary diagnostic with zero functional-safety credit.\n\nNo procurement, fabrication, assembly, connection, powered test, motion or energization is authorized.\n""", encoding="utf-8")
    rows = "".join(f"<tr><td>{html.escape(a)}</td><td>{html.escape(b)}</td><td>{html.escape(c)}</td><td>{html.escape(d)}</td></tr>" for a,b,c,d in calculations); holds = "".join(f"<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>" for a,b,c in p03.HOLDS)
    WEB.mkdir(parents=True, exist_ok=True)
    WEB.joinpath("index.html").write_text(f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>R211 open-drain observation carrier</title><style>:root{{--sky:#dff3ff;--blue:#082b55;--gold:#f5bd21;--paper:#f8fbfd;--line:#8db8d9}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--blue);font:clamp(16px,1.2vw,19px)/1.55 system-ui,sans-serif}}header,main{{max-width:1180px;margin:auto;padding:28px}}header{{background:var(--sky);border-bottom:5px solid var(--gold)}}h1{{font-size:clamp(32px,5vw,62px);line-height:1.05;margin:.2em 0}}h2{{font-size:clamp(24px,3vw,36px)}}.warning,.hold{{padding:18px;background:#fff4c2;border:3px solid #9c6800;font-weight:800}}.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px}}.card{{padding:20px;background:white;border:2px solid var(--line);border-radius:14px}}.card b{{font-size:30px;display:block}}.scroll{{overflow:auto;border:2px solid var(--line);border-radius:12px;background:white}}table{{width:100%;border-collapse:collapse;min-width:900px}}th,td{{padding:13px;text-align:left;vertical-align:top;border-bottom:1px solid #b8d2e5;font-size:14px}}th{{background:var(--blue);color:white}}object{{display:block;width:100%;height:auto;min-height:420px;background:white;border:2px solid var(--line);border-radius:14px}}button{{font:inherit;padding:10px 14px;border:2px solid var(--blue);border-radius:8px;background:white;color:var(--blue);font-weight:700}}button[aria-pressed="true"]{{background:var(--gold)}}@media(max-width:520px){{header,main{{padding:18px}}th,td{{font-size:14px}}}}</style></head><body><header><p>Project Button - R211 controlled engineering guide</p><h1>Open-drain outputs remove the OE sequencing defect.</h1><p class="warning">{WARNING}</p></header><main><div class="cards"><div class="card"><b>2.598 V</b>analytical HIGH floor</div><div class="card"><b>0.356 V</b>analytical LOW ceiling</div><div class="card"><b>0.367 mA</b>pull-up short screen</div><div class="card"><b>0</b>physical acceptance results</div></div><h2>Choose the view</h2><p><button data-view="schematic" aria-pressed="true">Open-drain schematic</button> <button data-view="board" aria-pressed="false">Routed board</button></p><object id="drawing" data="../../../electrical/kicad/hr-v0-runtime-observation-carrier-p0.5/output/runtime-observation-4.svg" type="image/svg+xml">Open native schematic export.</object><h2>Fault and margin screens</h2><div class="scroll"><table><thead><tr><th>Case</th><th>Calculation</th><th>Result</th><th>Disposition</th></tr></thead><tbody>{rows}</tbody></table></div><p class="hold">Pi 5/RP1 DC limits, STANDBY behavior, rail acceptance, installed timing, physical tests and qualified review remain open.</p><h2>Fourteen open holds</h2><div class="scroll"><table><thead><tr><th>ID</th><th>Scope</th><th>Evidence required</th></tr></thead><tbody>{holds}</tbody></table></div></main><script>const d=document.querySelector('#drawing');const u={{schematic:'../../../electrical/kicad/hr-v0-runtime-observation-carrier-p0.5/output/runtime-observation-4.svg',board:'../../../electrical/kicad/hr-v0-runtime-observation-carrier-p0.5/output/runtime-observation-carrier-top.svg'}};document.querySelectorAll('button[data-view]').forEach(b=>b.addEventListener('click',()=>{{document.querySelectorAll('button[data-view]').forEach(x=>x.setAttribute('aria-pressed',String(x===b)));d.data=u[b.dataset.view]}}));</script></body></html>''', encoding="utf-8")


def manifest() -> None:
    target = ECAD / "SOURCE-MANIFEST.csv"; result = []
    for path in sorted(ECAD.rglob("*")):
        if path.is_file() and path != target: result.append((path.relative_to(ECAD).as_posix(), hashlib.sha256(path.read_bytes()).hexdigest().upper()))
    with target.open("w", newline="", encoding="utf-8") as handle: writer = csv.writer(handle); writer.writerow(["file", "sha256"]); writer.writerows(result)


def main() -> int:
    p03 = load_p03(); configure(p03); legacy, base = p03.prepare_modules(); base.FOOTPRINTS[BUFFER_MPN] = f"{p03.LIB_NAME}:{p03.BUFFER_FOOTPRINT}"; base.FOOTPRINTS[RPU_MPN] = f"{p03.LIB_NAME}:Panasonic_ERJ6_Reflow_Nominal"
    build_schematic(p03, legacy, base)
    original = p03.build_board; summary = correct_board(p03, legacy, original)
    p03.run_native(summary); write_docs_web(p03, summary); manifest()
    print(f"Generated {IDENTIFIER}: 5 native sheets / {summary['footprints']} footprints / {summary['track_segments']} tracks / {summary['vias']} vias")
    print("P0.4 OE sequencing and positive-drive paths removed in candidate; fourteen holds remain")
    print(WARNING); return 0


if __name__ == "__main__":
    raise SystemExit(main())
