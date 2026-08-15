#!/usr/bin/env python3
"""Generate R209 buffered runtime-observation carrier candidate.

This derivative preserves the R202 field-input copper and replaces the direct
ISO1212-to-harness outputs with a bounded two-stage interface.  It generates
native KiCad source and review evidence only; it grants no work authority.
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
from collections import Counter
from pathlib import Path

import pcbnew


ROOT = Path(__file__).resolve().parents[1]
LEGACY = ROOT / "electrical/kicad/hr-v0-runtime-observation-carrier-p0.2"
ECAD = ROOT / "electrical/kicad/hr-v0-runtime-observation-carrier-p0.3"
WEB = ROOT / "release/hr-v0/runtime-observation-carrier-p0.3"
DOC = ROOT / "docs/hr-v0-runtime-observation-carrier-p0.3.md"
PROJECT = "hr-v0-runtime-observation-carrier-p0.3"
IDENTIFIER = "HR-V0-RUNTIME-OBS-CARRIER-P0.3"
REV = "R209 / P0.3 / PCB-P0.2"
DATE = "2026-08-10"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
KICAD = Path(r"C:\Program Files\KiCad\10.0\bin")
LIB_NAME = "PB_RUNTIME_OBS_P03"
LIB_DIR = ECAD / f"{LIB_NAME}.pretty"

RSO_VALUE = "1.50 kohm 1% 0.125 W 0805"
RSO_MPN = "Panasonic ERJ6ENF1501V"
RIN_VALUE = "47.0 kohm 1% 0.125 W 0805"
RIN_MPN = "Panasonic ERJ6ENF4702V"
RGP_VALUE = "36.5 kohm 1% 0.125 W 0805"
RGP_MPN = "Panasonic ERJ6ENF3652V"
RPO_VALUE = "330 kohm 1% 0.125 W 0805"
RPO_MPN = "Panasonic ERJ6ENF3303V"
BUFFER_MPN = "Texas Instruments SN74LVC1G125DBVR"
BUFFER_FOOTPRINT = "TI_DBV0005A_SOT23_5"

CHANNELS = [
    (1, "SR1", "UOBS1", "4", "3"),
    (2, "SRA1", "UOBS1", "5", "4"),
    (3, "K1", "UOBS2", "4", "5"),
    (4, "K2", "UOBS2", "5", "6"),
]

NEW_SOURCES = [
    ("OBS3-SRC-016", "Texas Instruments", "SN74LVC1G125 datasheet", "SCES223T Rev T", "2014-10; rechecked 2026-08-10", "https://www.ti.com/lit/ds/symlink/sn74lvc1g125.pdf", "SN74LVC1G125 electrical limits and DBV pinout: 1.65-5.5 V operation; 2.0/0.8 V input thresholds at 2.7-3.6 V; 100 uA output-level rows; Ioff; ICC and delta-ICC rows"),
    ("OBS3-SRC-017", "Texas Instruments", "SN74LVC1G125 product and package record", "active production DBV-5; package addendum 2026-04-08", "rechecked 2026-08-10", "https://www.ti.com/product/SN74LVC1G125/part-details/SN74LVC1G125DBVR", "Exact active orderable candidate; DBV0005A package drawing controls candidate land geometry; procurement and application approval remain open"),
    ("OBS3-SRC-018", "Panasonic Industry", "ERJ6ENF1501V product record", "1.50 kohm 1% 0805", "rechecked 2026-08-10", "https://industrial.panasonic.com/ww/products/pt/general-purpose-chip-resistors/models/ERJ6ENF1501V", "Exact ISO-output series candidate"),
    ("OBS3-SRC-019", "Panasonic Industry", "ERJ6ENF4702V product record", "47.0 kohm 1% 0805", "rechecked 2026-08-10", "https://industrial.panasonic.com/ww/products/pt/general-purpose-chip-resistors/models/ERJ6ENF4702V", "Exact buffer-input fail-low candidate"),
    ("OBS3-SRC-020", "Panasonic Industry", "ERJ6ENF3652V product record", "36.5 kohm 1% 0805", "rechecked 2026-08-10", "https://industrial.panasonic.com/ww/products/pt/general-purpose-chip-resistors/models/ERJ6ENF3652V", "Exact GPIO-path series candidate"),
    ("OBS3-SRC-021", "Panasonic Industry", "ERJ6ENF3303V model record", "330 kohm 1% 0805", "rechecked 2026-08-10", "https://industrial.panasonic.com/ww/products/pt/general-purpose-chip-resistors/models/ERJ6ENF3303V", "Exact cable-side fail-low candidate"),
]

HOLDS = [
    ("OBS3-HOLD-001", "R202 inherited field application", "Close every P0.2 Y32, H1, K1/K2 wetting, EMC, grounding and thermal hold against received parts"),
    ("OBS3-HOLD-002", "Pi 3V3 envelope", "Obtain authoritative Pi 5 external-load and rail-tolerance limits; then measure startup, steady, brownout and shutdown rail behavior"),
    ("OBS3-HOLD-003", "Pi GPIO DC interface", "Obtain authoritative RP1 VIH, VIL, leakage, capacitance, clamp and unpowered-pin limits or an application-specific Raspberry Pi acceptance"),
    ("OBS3-HOLD-004", "buffer application", "Qualified electrical review of the four exact SN74LVC1G125DBVR supply, OE grounding, transition-rate, delta-ICC, fault-current, output-divider and thermal screens"),
    ("OBS3-HOLD-005", "PCB DFM", "Selected fabricator accepts the updated DBV-5/0805 lands, four-layer stack, spacing, mask, legend, holes, zones and board drawing"),
    ("OBS3-HOLD-006", "assembly process", "Selected assembler accepts stencil, paste, solder alloy/profile, cleaning, AOI, rework and first-article controls"),
    ("OBS3-HOLD-007", "harness timing and EMC", "Measure installed conductor capacitance, rise/fall time, crosstalk, actuator-current interference, routing and separation"),
    ("OBS3-HOLD-008", "partial power and back-power", "Execute OFF, ramp, active, brownout, shutdown, field-only, open, short-to-return, short-to-3V3 and cross-short cases"),
    ("OBS3-HOLD-009", "received identity", "Inspect exact UOBS1/UOBS2/UBUF1-UBUF4/resistor/capacitor/terminal identities, markings, orientation and damage"),
    ("OBS3-HOLD-010", "unpowered board inspection", "Inspect dimensions, holes, lands, isolation corridor, continuity, shorts, residue and no unintended field/compute bond"),
    ("OBS3-HOLD-011", "powered isolated fixture", "Execute voltage, current, truth-table, rail, thermal and timing tests only under a separately authorized isolated fixture procedure"),
    ("OBS3-HOLD-012", "software fail-closed behavior", "Prove every unknown or invalid observation inhibits ordinary heartbeat/motion authority and cannot create a restart"),
    ("OBS3-HOLD-013", "safety boundary", "Qualified reviewer confirms the entire observation path remains ordinary diagnostic circuitry with zero safety credit"),
    ("OBS3-HOLD-014", "work authority", "Separate written authorization is required before procurement, fabrication, assembly, connection or powered testing"),
]

LOADS = [
    ("OBS3-LOAD-001", "PI_3V3_CANDIDATE", "two ISO1212 logic sides", "2 x 1.9 mA maximum ICC1", "3.800 mA", "TI ISO1212 bound", "SCREEN ONLY"),
    ("OBS3-LOAD-002", "PI_3V3_CANDIDATE", "four SN74LVC1G125 static supplies", "4 x 10 uA maximum ICC", "0.040 mA", "does not include delta-ICC", "SCREEN ONLY"),
    ("OBS3-LOAD-003", "PI_3V3_CANDIDATE", "four LVC inputs near VCC-0.6", "4 x 0.5 mA maximum delta-ICC row", "2.000 mA", "conservative simultaneous-high screen; installed transition behavior remains open", "SELECTION/MEASUREMENT REQUIRED"),
    ("OBS3-LOAD-004", "PI_3V3_CANDIDATE", "four 47k input pulldown paths", "4 x 3.6 V/(1.485k+46.53k)", "0.300 mA", "maximum-resistor-current screen", "SCREEN ONLY"),
    ("OBS3-LOAD-005", "PI_3V3_CANDIDATE", "four 330k output pulldown paths", "4 x 3.6 V/(36.135k+326.7k)", "0.040 mA", "maximum-resistor-current screen", "SCREEN ONLY"),
    ("OBS3-LOAD-006", "PI_3V3_CANDIDATE", "combined steady worst-case screen", "3.800 + 0.040 + 2.000 + 0.300 + 0.040", "6.180 mA", "not Pi 5 source approval; switching current absent", "SELECTION REQUIRED"),
]


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def write_csv(path: Path, header: list[str], rows: list[tuple[str, ...]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle); writer.writerow([*header, "warning"])
        for row in rows: writer.writerow([*row, WARNING])


def prepare_modules():
    legacy = load_module(ROOT / "tools/generate_hr_v0_runtime_observation_carrier_p02.py", "obs_p02_for_p03")
    legacy.ECAD = ECAD; legacy.WEB = WEB; legacy.DOC = DOC; legacy.PROJECT = PROJECT
    legacy.IDENTIFIER = IDENTIFIER; legacy.REV = REV; legacy.DATE = DATE
    legacy.LIB_NAME = LIB_NAME; legacy.LIB_DIR = LIB_DIR
    legacy.SOURCES = [*legacy.SOURCES, *NEW_SOURCES]
    legacy.HOLDS = HOLDS
    base = legacy.load_base()
    base.ECAD = ECAD; base.WEB = WEB; base.DOC = DOC; base.PROJECT = PROJECT
    base.IDENTIFIER = IDENTIFIER; base.REV = REV; base.DATE = DATE
    base.SOURCES = legacy.SOURCES; base.HOLDS = HOLDS; base.LOADS = LOADS
    base.FOOTPRINTS.update({
        RSO_MPN: f"{LIB_NAME}:Panasonic_ERJ6_Reflow_Nominal",
        RIN_MPN: f"{LIB_NAME}:Panasonic_ERJ6_Reflow_Nominal",
        RGP_MPN: f"{LIB_NAME}:Panasonic_ERJ6_Reflow_Nominal",
        RPO_MPN: f"{LIB_NAME}:Panasonic_ERJ6_Reflow_Nominal",
        "SN74LVC1G125DBVR": f"{LIB_NAME}:{BUFFER_FOOTPRINT}",
    })
    return legacy, base


def build_schematic(legacy, base) -> None:
    model = base.load_model(); pn, Component, Sheet = model.pn, model.Component, model.Sheet
    jfield = Component("JFIELD1", "Phoenix Contact MKDS 1/6-3,5 item 1751280", [
        pn("JFIELD1", "1", "SR1 STATUS", "SR1_STATUS", "right"), pn("JFIELD1", "2", "SRA1 STATUS", "SRA1_STATUS", "right"),
        pn("JFIELD1", "3", "K1 STATUS", "K1_STATUS", "right"), pn("JFIELD1", "4", "K2 STATUS", "K2_STATUS", "right"),
        pn("JFIELD1", "5", "FIELD RETURN", "SAFETY_0V", "right"), pn("JFIELD1", "6", "N/C", "INTENTIONALLY_UNUSED_JFIELD1_6", "right"),
    ], "EXACT PCB TERMINAL CANDIDATE - PHYSICAL HOLD", "R202 position numbering retained; no harness or connection release.", position=(76, 92), width=74, footprint=f"{LIB_NAME}:Phoenix_MKDS_1_6_3P5_1751280")
    jlogic = Component("JLOGIC1", "Phoenix Contact MKDS 1/6-3,5 item 1751280", [
        pn("JLOGIC1", "1", "PI 3V3 CANDIDATE", "PI_3V3_CANDIDATE", "left"), pn("JLOGIC1", "2", "COMPUTE RETURN", "COMPUTE_0V", "left"),
        pn("JLOGIC1", "3", "OBS SR1", "OBS_SR1_PI", "left"), pn("JLOGIC1", "4", "OBS SRA1", "OBS_SRA1_PI", "left"),
        pn("JLOGIC1", "5", "OBS K1", "OBS_K1_PI", "left"), pn("JLOGIC1", "6", "OBS K2", "OBS_K2_PI", "left"),
    ], "EXACT PCB TERMINAL CANDIDATE - PI/HARNESS/PHYSICAL HOLD", "Four outputs now follow the buffered and separately limited path. Pi DC acceptance remains open.", position=(300, 92), width=74, footprint=f"{LIB_NAME}:Phoenix_MKDS_1_6_3P5_1751280")
    s1 = Sheet(1, "01_boundaries.kicad_sch", "Field and compute boundaries", "R202 connector numbering retained; buffered compute outputs on page 4.", compact=True)
    s1.components = [jfield, jlogic]; s1.notes = ["SAFETY_0V and COMPUTE_0V remain distinct.", "All observations are ordinary diagnostics with zero safety credit."]

    u1 = base.iso1212(model, "UOBS1", "SR1", "SRA1", "OBS_SR1_RAW", "OBS_SRA1_RAW", (210, 136))
    s2 = Sheet(2, "02_sr1_sra1_inputs.kicad_sch", "SR1 and SRA1 Type-3 inputs", "Inherited field network; received H1/Y32 evidence remains held.", compact=True)
    s2.components = base.channel_parts(model, 1, "SR1_STATUS", "SR1", 62, False) + [u1] + base.channel_parts(model, 2, "SRA1_STATUS", "SRA1", 360, True)
    s2.notes = ["Field-side component identities and nets are retained from P0.2.", "No field-input physical evidence is closed by this derivative."]
    u2 = base.iso1212(model, "UOBS2", "K1", "K2", "OBS_K1_RAW", "OBS_K2_RAW", (210, 136))
    s3 = Sheet(3, "03_k1_k2_inputs.kicad_sch", "K1 and K2 diagnostic auxiliary inputs", "Inherited field network; contact evidence remains held.", compact=True)
    s3.components = base.channel_parts(model, 3, "K1_STATUS", "K1", 62, True) + [u2] + base.channel_parts(model, 4, "K2_STATUS", "K2", 360, True)
    s3.notes = ["Field-side component identities and nets are retained from P0.2.", "No contact application or safety credit is added."]

    outputs = []
    buffers = []
    for index, name, _uref, _upin, _jpin in CHANNELS:
        x = 46 + (index - 1) * 106
        outputs.extend([
            base.resistor(model, f"RSO{index}", RSO_VALUE, RSO_MPN, f"OBS_{name}_RAW", f"OBS_{name}_BUF_IN", (x, 60), "ISO OUTPUT FAULT LIMIT"),
            base.resistor(model, f"RPD{index}", RIN_VALUE, RIN_MPN, f"OBS_{name}_BUF_IN", "COMPUTE_0V", (x, 112), "BUFFER INPUT FAIL-LOW"),
            base.resistor(model, f"RGP{index}", RGP_VALUE, RGP_MPN, f"OBS_{name}_BUF_OUT", f"OBS_{name}_PI", (x, 180), "GPIO PATH FAULT LIMIT"),
            base.resistor(model, f"RPO{index}", RPO_VALUE, RPO_MPN, f"OBS_{name}_PI", "COMPUTE_0V", (x, 232), "CABLE-SIDE FAIL-LOW"),
        ])
        ref = f"UBUF{index}"
        buffers.append(Component(ref, BUFFER_MPN, [
            pn(ref, "1", "OE ACTIVE LOW", "COMPUTE_0V", "left"),
            pn(ref, "2", f"A {name}", f"OBS_{name}_BUF_IN", "left"),
            pn(ref, "3", "GND", "COMPUTE_0V", "left"),
            pn(ref, "4", f"Y {name}", f"OBS_{name}_BUF_OUT", "right"),
            pn(ref, "5", "VCC", "PI_3V3_CANDIDATE", "right"),
        ], "EXACT BUFFER CANDIDATE - APPLICATION/PCB/PHYSICAL HOLD", "OE is hard-grounded. This ordinary diagnostic buffer has zero safety credit.", "https://www.ti.com/lit/ds/symlink/sn74lvc1g125.pdf", "SCES223T Rev T; rechecked 2026-08-10", position=(x, 142), width=82, footprint=f"{LIB_NAME}:{BUFFER_FOOTPRINT}"))
    cdec = []
    for index, purpose in ((1, "UOBS1"), (2, "UOBS2"), (3, "UBUF1"), (4, "UBUF2"), (5, "UBUF3"), (6, "UBUF4")):
        cdec.append(Component(f"CDEC{index}", "100 nF 50 V X7R; Murata GRM21BR71H104KA01L", [pn(f"CDEC{index}", "1", "VCC", "PI_3V3_CANDIDATE", "left"), pn(f"CDEC{index}", "2", "GND", "COMPUTE_0V", "right")], "EXACT DECOUPLING CANDIDATE - PLACEMENT/PHYSICAL HOLD", f"Local bypass for {purpose}; physical placement and received evidence remain open.", position=(70 + index * 70, 282), width=64, footprint=f"{LIB_NAME}:Murata_GRM21_Reflow_Nominal"))
    s4 = Sheet(4, "04_compute_outputs.kicad_sch", "Buffered fail-low compute outputs", "ISO and GPIO fault limits are separated; Pi acceptance remains open.", compact=True)
    s4.components = [*outputs, *buffers, *cdec]
    s4.notes = ["RSO=1.50k and RPD=47k bound the ISO-to-buffer side; RGP=36.5k and RPO=330k bound the harness side.", "The selected analytical supply envelope is 3.0-3.6 V; the actual Pi 5 rail and GPIO limits remain held."]

    sheets = [s1, s2, s3, s4]; items = [c for s in sheets for c in s.components]
    counts = Counter(pin.net for component in items for pin in component.pins); wire_numbers = model.build_wire_numbers(sheets, counts)
    ECAD.mkdir(parents=True, exist_ok=True)
    for stale in ECAD.glob("*.kicad_sch"): stale.unlink()
    project_data = {"board": {}, "boards": [], "cvpcb": {}, "erc": {}, "libraries": {}, "meta": {"filename": f"{PROJECT}.kicad_pro", "version": 1}, "net_settings": {"classes": [], "meta": {"version": 3}}, "pcbnew": {}, "schematic": {}, "text_variables": {"PROJECT_STATUS": WARNING, "REVISION": REV}}
    (ECAD / f"{PROJECT}.kicad_pro").write_text(json.dumps(project_data, indent=2) + "\n", encoding="utf-8")
    symbols = [model.lib_symbol(component).replace(f'(symbol "PBV3:{component.ref}"', f'(symbol "{component.ref}"', 1) for component in items]
    (ECAD / f"{PROJECT}.kicad_sym").write_text('(kicad_symbol_lib\n  (version 20251024) (generator "kicad_symbol_editor") (generator_version "10.0")\n  ' + "\n".join(symbols) + "\n)\n", encoding="utf-8")
    (ECAD / "sym-lib-table").write_text(f'(sym_lib_table\n  (version 7)\n  (lib (name "PBV3")(type "KiCad")(uri "${{KIPRJMOD}}/{PROJECT}.kicad_sym")(options "")(descr "R209 buffered runtime observation symbols"))\n)\n', encoding="utf-8")
    root_uuid = model.uid("root-hr-v0-runtime-observation-carrier-p03")
    (ECAD / f"{PROJECT}.kicad_sch").write_text(model.root_schematic(root_uuid, sheets), encoding="utf-8")
    for sheet in sheets: (ECAD / sheet.filename).write_text(model.child_schematic(root_uuid, sheet, counts, wire_numbers), encoding="utf-8")
    write_csv(ECAD / "connector-schedule.csv", ["sheet", "reference", "terminal", "function", "net", "state"], [(s.filename, c.ref, p.number, p.name, p.net, c.status) for s in sheets for c in s.components for p in c.pins])
    write_csv(ECAD / "bom.csv", ["reference", "value", "quantity", "state"], [(c.ref, c.value, str(c.quantity), c.status) for c in items if c.quantity])
    write_csv(ECAD / "net-schedule.csv", ["net", "node_count", "nodes"], [(net, str(count), " | ".join(f"{s.filename}:{c.ref}:{p.number}" for s in sheets for c in s.components for p in c.pins if p.net == net)) for net, count in sorted(counts.items())])
    write_csv(ECAD / "load-budget.csv", ["load_id", "net", "architecture", "basis", "result", "limit", "state"], LOADS)
    write_csv(ECAD / "selection-holds.csv", ["hold_id", "scope", "evidence_required"], HOLDS)
    write_csv(ECAD / "source-register.csv", ["source_id", "manufacturer", "document", "revision", "date", "official_url", "use_and_limit"], legacy.SOURCES)


def make_sot23_5(legacy) -> pcbnew.FOOTPRINT:
    fp = pcbnew.FOOTPRINT(None); fp.SetFPID(pcbnew.LIB_ID(LIB_NAME, BUFFER_FOOTPRINT)); fp.SetValue(BUFFER_FOOTPRINT)
    # Candidate geometry is source-controlled to TI DBV0005A; DFM acceptance remains held.
    for number, x, y in (("1", -1.10, -0.95), ("2", -1.10, 0.0), ("3", -1.10, 0.95), ("4", 1.10, 0.95), ("5", 1.10, -0.95)):
        legacy.add_smd_pad(fp, number, x, y, 1.20, 0.70, 0.10)
    legacy.add_outline(fp, -1.70, -1.45, 1.70, 1.45)
    fp.Reference().SetVisible(False); fp.Value().SetVisible(False)
    return fp


def prepare_library(legacy) -> None:
    LIB_DIR.mkdir(parents=True, exist_ok=True)
    for stale in LIB_DIR.glob("*.kicad_mod"): stale.unlink()
    for source in (LEGACY / "PB_RUNTIME_OBS.pretty").glob("*.kicad_mod"):
        shutil.copyfile(source, LIB_DIR / source.name)
    pcbnew.PCB_IO_KICAD_SEXPR().FootprintSave(str(LIB_DIR), make_sot23_5(legacy))
    (ECAD / "fp-lib-table").write_text(f'(fp_lib_table\n  (version 7)\n  (lib (name "{LIB_NAME}")(type "KiCad")(uri "${{KIPRJMOD}}/{LIB_NAME}.pretty")(options "")(descr "R209 buffered observation footprints"))\n)\n', encoding="utf-8")


def build_board(legacy) -> dict[str, object]:
    prepare_library(legacy)
    board = pcbnew.LoadBoard(str(LEGACY / "hr-v0-runtime-observation-carrier-p0.2.kicad_pcb"))
    footprints = {fp.GetReference(): fp for fp in board.GetFootprints()}
    nets = {str(name): net for name, net in board.GetNetsByName().items()}
    inherited_track_nets = {item.m_Uuid.AsString(): item.GetNetname() for item in board.GetTracks()}
    affected = {f"OBS_{name}_{suffix}" for _i, name, *_rest in CHANNELS for suffix in ("RAW", "BUF_IN", "BUF_OUT", "PI")}
    for item in list(board.GetTracks()):
        pos = item.GetPosition(); x = pcbnew.ToMM(pos.x); y = pcbnew.ToMM(pos.y)
        obsolete_compute_stub = item.GetNetname() == "COMPUTE_0V" and 85.0 <= x <= 88.5 and 30.0 <= y <= 61.0
        if item.GetNetname() in affected or obsolete_compute_stub: board.Delete(item)
    for _i, name, *_rest in CHANNELS:
        for suffix in ("BUF_IN", "BUF_OUT"):
            net_name = f"OBS_{name}_{suffix}"
            if net_name not in nets:
                net = pcbnew.NETINFO_ITEM(board, net_name); board.Add(net); nets[net_name] = net
    nets = {str(name): net for name, net in board.GetNetsByName().items()}
    placements = {}
    for index, _name, *_rest in CHANNELS:
        lane = 66.0 - 8.0 * index
        placements.update({
            f"RSO{index}": (71.5, lane, 0.0),
            f"RPD{index}": (76.0, lane + 2.6, 90.0),
            f"UBUF{index}": (83.0, lane, 0.0),
            f"CDEC{index + 2}": (87.0, lane - 2.6, 0.0),
            f"RGP{index}": (92.0, lane + 0.95, 0.0),
            f"RPO{index}": (98.0, lane + 3.2, 90.0),
        })
    for index, name, _uref, _upin, _jpin in CHANNELS:
        rso, rpd = footprints[f"RSO{index}"], footprints[f"RPD{index}"]
        for fp, key in ((rso, f"RSO{index}"), (rpd, f"RPD{index}")):
            x, y, angle = placements[key]; fp.SetPosition(pcbnew.VECTOR2I_MM(x, y)); fp.SetOrientationDegrees(angle)
        rso.SetValue(f"{RSO_VALUE}; {RSO_MPN}"); rpd.SetValue(f"{RIN_VALUE}; {RIN_MPN}")
        for pad in rso.Pads(): pad.SetNet(nets[f"OBS_{name}_RAW" if pad.GetNumber() == "1" else f"OBS_{name}_BUF_IN"])
        for pad in rpd.Pads(): pad.SetNet(nets[f"OBS_{name}_BUF_IN" if pad.GetNumber() == "1" else "COMPUTE_0V"])
    additions = {f"UBUF{i}": BUFFER_FOOTPRINT for i in range(1, 5)}
    additions.update({f"CDEC{i + 2}": "Murata_GRM21_Reflow_Nominal" for i in range(1, 5)})
    additions.update({f"RGP{i}": "Panasonic_ERJ6_Reflow_Nominal" for i in range(1, 5)})
    additions.update({f"RPO{i}": "Panasonic_ERJ6_Reflow_Nominal" for i in range(1, 5)})
    for ref, footprint_name in additions.items():
        fp = pcbnew.FootprintLoad(str(LIB_DIR), footprint_name); fp.SetReference(ref)
        x, y, angle = placements[ref]; fp.SetPosition(pcbnew.VECTOR2I_MM(x, y)); fp.SetOrientationDegrees(angle)
        if ref.startswith("UBUF"):
            index = int(ref[4:]); name = CHANNELS[index - 1][1]
            fp.SetValue(BUFFER_MPN)
            pin_nets = {"1":"COMPUTE_0V","2":f"OBS_{name}_BUF_IN","3":"COMPUTE_0V","4":f"OBS_{name}_BUF_OUT","5":"PI_3V3_CANDIDATE"}
        elif ref.startswith("CDEC"):
            fp.SetValue("100 nF 50 V X7R; Murata GRM21BR71H104KA01L"); pin_nets = {"1":"PI_3V3_CANDIDATE","2":"COMPUTE_0V"}
        else:
            index = int(ref[-1]); name = CHANNELS[index - 1][1]
            if ref.startswith("RGP"):
                fp.SetValue(f"{RGP_VALUE}; {RGP_MPN}"); pin_nets = {"1":f"OBS_{name}_BUF_OUT","2":f"OBS_{name}_PI"}
            else:
                fp.SetValue(f"{RPO_VALUE}; {RPO_MPN}"); pin_nets = {"1":f"OBS_{name}_PI","2":"COMPUTE_0V"}
        for pad in fp.Pads(): pad.SetNet(nets[pin_nets[pad.GetNumber()]])
        board.Add(fp); footprints[ref] = fp

    for drawing in board.GetDrawings():
        if isinstance(drawing, pcbnew.PCB_TEXT):
            text = drawing.GetText().replace("PCB-P0.1", "PCB-P0.2")
            drawing.SetText(text)
    legacy.add_board_text(board, "4X BUFFERED OUTPUTS - SN74LVC1G125DBVR", 72.0, 12.5, 0.85)

    def pad(ref: str, number: str) -> tuple[float, float]:
        match = [item for item in footprints[ref].Pads() if item.GetNumber() == number]
        if len(match) != 1: raise RuntimeError(f"pad lookup {ref}.{number}")
        pos = match[0].GetPosition(); return pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y)

    for index, name, uref, upin, jpin in CHANNELS:
        raw, bin_net, bout, pi_net = f"OBS_{name}_RAW", f"OBS_{name}_BUF_IN", f"OBS_{name}_BUF_OUT", f"OBS_{name}_PI"
        raw_u, rso1 = pad(uref, upin), pad(f"RSO{index}", "1")
        va = (64.0 + 0.5 * (index % 2), raw_u[1])
        bus_y = {1: 58.0, 2: 51.5, 3: 42.0, 4: 36.5}[index]
        elbow, vb = (65.5, bus_y), (70.0, bus_y)
        legacy.add_track(board, nets[raw], [raw_u, va], pcbnew.F_Cu); legacy.add_via(board, nets[raw], va, 0.60, 0.30)
        legacy.add_track(board, nets[raw], [va, (65.5, raw_u[1]), elbow, vb], pcbnew.B_Cu); legacy.add_via(board, nets[raw], vb, 0.60, 0.30)
        legacy.add_track(board, nets[raw], [vb, rso1], pcbnew.F_Cu)
        rso2, rpd1, ubin = pad(f"RSO{index}", "2"), pad(f"RPD{index}", "1"), pad(f"UBUF{index}", "2")
        branch = (74.5, rso2[1]); legacy.add_track(board, nets[bin_net], [rso2, branch, ubin], pcbnew.F_Cu)
        legacy.add_track(board, nets[bin_net], [branch, (branch[0], rpd1[1]), rpd1], pcbnew.F_Cu)
        ubout, rgp1 = pad(f"UBUF{index}", "4"), pad(f"RGP{index}", "1")
        legacy.add_track(board, nets[bout], [ubout, rgp1], pcbnew.F_Cu)
        rgp2, rpo1, target = pad(f"RGP{index}", "2"), pad(f"RPO{index}", "1"), pad("JLOGIC1", jpin)
        pbranch, pvia, tvia = (96.0, rgp2[1]), (103.0 + 0.4 * index, rgp2[1]), (109.0, target[1])
        legacy.add_track(board, nets[pi_net], [rgp2, pbranch, pvia], pcbnew.F_Cu); legacy.add_track(board, nets[pi_net], [pbranch, (pbranch[0], rpo1[1]), rpo1], pcbnew.F_Cu)
        legacy.add_via(board, nets[pi_net], pvia); legacy.add_track(board, nets[pi_net], [pvia, tvia], pcbnew.B_Cu); legacy.add_via(board, nets[pi_net], tvia)
        legacy.add_track(board, nets[pi_net], [tvia, target], pcbnew.F_Cu)

    ground_nodes = [(f"RPD{i}", "2") for i in range(1,5)] + [(f"RPO{i}", "2") for i in range(1,5)] + [(f"CDEC{i + 2}", "2") for i in range(1,5)] + [(f"UBUF{i}", pin) for i in range(1,5) for pin in ("1","3")]
    for index, (ref, number) in enumerate(ground_nodes):
        point = pad(ref, number); offset = (-1.3 if ref.startswith("UBUF") else 0.8, (index % 3 - 1) * 0.20)
        via = (point[0] + offset[0], point[1] + offset[1]); legacy.add_track(board, nets["COMPUTE_0V"], [point, via], pcbnew.F_Cu, 0.30); legacy.add_via(board, nets["COMPUTE_0V"], via)
    for index in range(1,5):
        ubuf, cdec = pad(f"UBUF{index}", "5"), pad(f"CDEC{index + 2}", "1")
        via = (cdec[0] - 0.8, cdec[1]); legacy.add_track(board, nets["PI_3V3_CANDIDATE"], [ubuf, cdec, via], pcbnew.F_Cu, 0.30); legacy.add_via(board, nets["PI_3V3_CANDIDATE"], via)
    # pcbnew may renumber nets when new NETINFO_ITEM objects are added; restore every
    # retained inherited copper item to its captured net before filling zones.
    for item in board.GetTracks():
        inherited_name = inherited_track_nets.get(item.m_Uuid.AsString())
        if inherited_name and inherited_name not in affected:
            item.SetNet(nets[inherited_name])
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    board_path = ECAD / f"{PROJECT}.kicad_pcb"; pcbnew.SaveBoard(str(board_path), board)
    placement_rows = []
    for fp in sorted(board.GetFootprints(), key=lambda item: item.GetReference()):
        pos = fp.GetPosition(); placement_rows.append((fp.GetReference(), fp.GetFPID().GetLibItemName(), f"{pcbnew.ToMM(pos.x):.3f}", f"{pcbnew.ToMM(pos.y):.3f}", f"{fp.GetOrientationDegrees():.3f}", "TOP", "CANDIDATE - NOT RELEASED"))
    write_csv(ECAD / "pcb-placement.csv", ["reference", "footprint", "x_mm", "y_mm", "rotation_deg", "side", "state"], placement_rows)
    tracks = list(board.GetTracks())
    return {"footprints": len(placement_rows), "mounted_components": len(placement_rows)-4, "mounting_holes": 4, "board_width_mm": 120.0, "board_height_mm": 90.0, "copper_layers": 4, "field_compute_corridor_mm": 5.6, "track_segments": sum(isinstance(item, pcbnew.PCB_TRACK) and not isinstance(item, pcbnew.PCB_VIA) for item in tracks), "vias": sum(isinstance(item, pcbnew.PCB_VIA) for item in tracks), "zones": len(list(board.Zones())), "fabrication_authorized": False, "connection_authorized": False, "powered_testing_authorized": False, "motion_authorized": False, "energization_authorized": False, "safety_credit": False}


def run_native(summary: dict[str, object]) -> None:
    validation, output = ECAD / "validation", ECAD / "output"; validation.mkdir(exist_ok=True); output.mkdir(exist_ok=True)
    for stale in list(output.glob("*.svg")) + list(output.glob("*.pdf")): stale.unlink()
    root, board = ECAD / f"{PROJECT}.kicad_sch", ECAD / f"{PROJECT}.kicad_pcb"
    commands = [
        [str(KICAD / "kicad-cli.exe"), "sch", "erc", "--exit-code-violations", "--output", str(validation / f"{PROJECT}-erc.rpt"), str(root)],
        [str(KICAD / "kicad-cli.exe"), "sch", "export", "netlist", "--output", str(validation / f"{PROJECT}.net"), str(root)],
        [str(KICAD / "kicad-cli.exe"), "sch", "export", "svg", "--output", str(output), str(root)],
        [str(KICAD / "kicad-cli.exe"), "pcb", "drc", "--exit-code-violations", "--output", str(validation / f"{PROJECT}-drc.rpt"), str(board)],
        [str(KICAD / "kicad-cli.exe"), "pcb", "export", "stats", "--output", str(validation / f"{PROJECT}-stats.txt"), str(board)],
        [str(KICAD / "kicad-cli.exe"), "pcb", "export", "svg", "--mode-single", "--layers", "F.Cu,F.Silkscreen,Edge.Cuts", "--fit-page-to-board", "--exclude-drawing-sheet", "--output", str(output / "runtime-observation-carrier-top.svg"), str(board)],
    ]
    logs = []
    for command in commands:
        result = subprocess.run(command, text=True, capture_output=True); logs.append("$ " + subprocess.list2cmdline(command) + "\n" + result.stdout + result.stderr + f"\nexit={result.returncode}\n")
        if result.returncode:
            (validation / "kicad-cli.log").write_text("\n".join(logs), encoding="utf-8"); raise SystemExit(result.returncode)
    (validation / "kicad-cli.log").write_text("\n".join(logs), encoding="utf-8")
    children = sorted(path for path in output.glob("*.svg") if path.name not in (f"{PROJECT}.svg", "runtime-observation-carrier-top.svg"))
    for index, source in enumerate(children, 1): source.replace(output / f"runtime-observation-{index}.svg")
    for svg in output.glob("*.svg"):
        text = svg.read_text(encoding="utf-8").replace("#C83434", "#0B4F8A").replace("#F2EDA1", "#9A6500").replace("#D0D2CD", "#082B55")
        svg.write_text("\n".join(line.rstrip() for line in text.splitlines()) + "\n", encoding="utf-8")
    (validation / "pcb-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    (ECAD / f"{PROJECT}.kicad_prl").unlink(missing_ok=True)


def write_docs_web(summary: dict[str, object]) -> None:
    calculations = [
        ("ISO short to return at 3.6 V", "3.6 V / 1.485 kohm", "2.424 mA", "below ISO1212 +/-3 mA recommended output current"),
        ("buffer input HIGH at 3.0 V", "(3.0-0.4) x 46.53/(46.53+1.515)", "2.518 V", "0.518 V above SN74LVC1G125 VIH=2.0 V"),
        ("buffer input LOW", "ISO1212 VOL maximum", "<=0.400 V", ">=0.400 V below SN74LVC1G125 VIL=0.8 V"),
        ("GPIO hard short", "3.6 V / 36.135 kohm", "99.63 uA", "inside SN74LVC1G125 100 uA output-level test row"),
        ("GPIO source HIGH floor at 3.0 V", "(3.0-0.3) x 326.7/(326.7+36.865)", "2.426 V", "Pi 5/RP1 VIH still not published; margin not closed"),
        ("steady 3V3 load screen", "ISO + ICC + delta-ICC + pull paths", "6.180 mA", "not Pi 5 source approval; switching current absent"),
    ]
    DOC.write_text(f'''# HR-V0 buffered runtime-observation carrier {REV}\n\n**{WARNING}**\n\nR209 supersedes the P0.2 direct ISO1212-to-harness output candidate with a buffered P0.3 native KiCad derivative. The four field channels, both isolation barriers, connector numbering, board outline, mounting datums and field-side copper remain controlled. Each ISO output now reaches its own `SN74LVC1G125DBVR` input through 1.50 kohm and is biased low by 47.0 kohm. Each buffer output reaches the existing JLOGIC1 signal through 36.5 kohm and is biased low by 330 kohm.\n\nThe component-level calculation is constrained to a proposed 3.0-3.6 V interface envelope. It bounds the R208 ISO hard-short defect at 2.424 mA and creates a 0.518 V minimum input-HIGH screen against TI's 2.0 V threshold. The downstream 36.5 kohm resistor limits a 3.6 V hard short to 99.63 uA. This is a design correction, not physical or Raspberry Pi acceptance. Pi 5 header-source limits, RP1 GPIO thresholds/leakage/clamps, installed capacitance/timing, back-power, EMC, thermal and fault-injection evidence remain open.\n\nEach active-low OE pin is hard-connected to `COMPUTE_0V`; software cannot enable or bypass the buffers. Observations remain ordinary diagnostics with zero functional-safety credit. Unknown, invalid or unavailable observations must inhibit ordinary heartbeat/motion authority, and reset or power restoration cannot command motion. All {len(HOLDS)} holds and all physical acceptance evidence remain open.\n''', encoding="utf-8")
    calc_rows = "".join(f"<tr><td>{html.escape(a)}</td><td>{html.escape(b)}</td><td>{html.escape(c)}</td><td>{html.escape(d)}</td></tr>" for a,b,c,d in calculations)
    hold_rows = "".join(f"<tr><td>{html.escape(a)}</td><td>{html.escape(b)}</td><td>{html.escape(c)}</td></tr>" for a,b,c in HOLDS)
    source_rows = "".join(f"<tr><td>{html.escape(a)}</td><td>{html.escape(b)}</td><td>{html.escape(c)}</td><td>{html.escape(d)}</td></tr>" for a,b,c,d,*_ in NEW_SOURCES)
    WEB.mkdir(parents=True, exist_ok=True)
    WEB.joinpath("index.html").write_text(f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>R209 buffered observation carrier</title><style>:root{{--sky:#dff3ff;--blue:#082b55;--gold:#f5bd21;--paper:#f8fbfd;--line:#8db8d9}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--blue);font:clamp(16px,1.2vw,19px)/1.55 system-ui,sans-serif}}header,main{{max-width:1180px;margin:auto;padding:28px}}header{{background:var(--sky);border-bottom:5px solid var(--gold)}}h1{{font-size:clamp(32px,5vw,62px);line-height:1.05;margin:.2em 0}}h2{{font-size:clamp(24px,3vw,36px)}}.warning,.hold{{padding:18px;background:#fff4c2;border:3px solid #9c6800;font-weight:800}}.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:16px}}.card{{padding:20px;background:white;border:2px solid var(--line);border-radius:14px}}.card b{{font-size:30px;display:block}}.scroll{{overflow:auto;border:2px solid var(--line);border-radius:12px;background:white}}table{{width:100%;border-collapse:collapse;min-width:900px}}th,td{{padding:13px;text-align:left;vertical-align:top;border-bottom:1px solid #b8d2e5;font-size:14px}}th{{background:var(--blue);color:white}}img,object{{display:block;width:100%;height:auto;min-height:420px;background:white;border:2px solid var(--line);border-radius:14px}}button{{font:inherit;padding:10px 14px;border:2px solid var(--blue);border-radius:8px;background:white;color:var(--blue);font-weight:700}}button[aria-pressed="true"]{{background:var(--gold)}}@media(max-width:520px){{header,main{{padding:18px}}th,td{{font-size:14px}}}}</style></head><body><header><p>Project Button - R209 controlled engineering guide</p><h1>The ISO output no longer drives the cable directly.</h1><p class="warning">{WARNING}</p></header><main><div class="cards"><div class="card"><b>2.424 mA</b>maximum ISO-side short screen</div><div class="card"><b>99.63 uA</b>maximum GPIO-side short screen</div><div class="card"><b>24.180 mA</b>steady 3V3 load screen, not Pi approval</div><div class="card"><b>0</b>physical acceptance results</div></div><h2>Choose the view</h2><p><button data-view="schematic" aria-pressed="true">Buffered schematic</button> <button data-view="board" aria-pressed="false">Routed board</button></p><object id="drawing" data="../../../electrical/kicad/hr-v0-runtime-observation-carrier-p0.3/output/runtime-observation-4.svg" type="image/svg+xml">Open native schematic export.</object><h2>Fault and margin screens</h2><div class="scroll"><table><thead><tr><th>Case</th><th>Calculation</th><th>Result</th><th>Disposition</th></tr></thead><tbody>{calc_rows}</tbody></table></div><p class="hold">Pi 5/RP1 DC limits, rail acceptance, installed timing, physical tests and qualified review remain open. This correction does not authorize a build or connection.</p><h2>Primary-source additions</h2><div class="scroll"><table><thead><tr><th>ID</th><th>Manufacturer</th><th>Document</th><th>Revision</th></tr></thead><tbody>{source_rows}</tbody></table></div><h2>{len(HOLDS)} open holds</h2><div class="scroll"><table><thead><tr><th>ID</th><th>Scope</th><th>Evidence required</th></tr></thead><tbody>{hold_rows}</tbody></table></div></main><script>const drawing=document.querySelector('#drawing');const urls={{schematic:'../../../electrical/kicad/hr-v0-runtime-observation-carrier-p0.3/output/runtime-observation-4.svg',board:'../../../electrical/kicad/hr-v0-runtime-observation-carrier-p0.3/output/runtime-observation-carrier-top.svg'}};document.querySelectorAll('button[data-view]').forEach(button=>button.addEventListener('click',()=>{{document.querySelectorAll('button[data-view]').forEach(item=>item.setAttribute('aria-pressed',String(item===button)));drawing.data=urls[button.dataset.view]}}));</script></body></html>''', encoding="utf-8")
    guide = WEB / "index.html"
    guide.write_text(guide.read_text(encoding="utf-8").replace("24.180 mA", "6.180 mA"), encoding="utf-8")


def manifest() -> None:
    target = ECAD / "SOURCE-MANIFEST.csv"; result = []
    for path in sorted(ECAD.rglob("*")):
        if path.is_file() and path != target: result.append((path.relative_to(ECAD).as_posix(), hashlib.sha256(path.read_bytes()).hexdigest().upper()))
    with target.open("w", newline="", encoding="utf-8") as handle: writer = csv.writer(handle); writer.writerow(["file", "sha256"]); writer.writerows(result)


def main() -> int:
    legacy, base = prepare_modules(); build_schematic(legacy, base); summary = build_board(legacy); run_native(summary); write_docs_web(summary); manifest()
    print(f"Generated {IDENTIFIER}: 5 native sheets / {summary['footprints']} footprints / {summary['track_segments']} tracks / {summary['vias']} vias")
    print(f"R208 direct-output blocker corrected in candidate; {len(HOLDS)} holds remain; no work or safety authority")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
