"""Validate the HR-V0 watchdog PCB constrained-placement candidate.

Run this checker with KiCad's bundled Python.  It proves source consistency,
placement membership, manufacturer-derived geometry rules and the explicitly
unrouted state only. It does not release routing, fabrication, assembly,
energization or safety credit.
"""

from __future__ import annotations

import importlib.util
import json
import math
import re
import sys
from pathlib import Path

import pcbnew


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "electrical" / "kicad" / "project-button-v3"
WARNING = "PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION"


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def load_model():
    path = ROOT / "tools" / "generate_hr_v0_electrical_v3.py"
    spec = importlib.util.spec_from_file_location("pbv3_check_model", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load electrical model")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def pad(footprints, reference: str, number: str):
    matches = [item for item in footprints[reference].Pads() if item.GetNumber() == number]
    if len(matches) != 1:
        raise RuntimeError(f"expected one pad {reference}.{number}, found {len(matches)}")
    return matches[0]


def distance_mm(a, b) -> float:
    pa = a.GetPosition()
    pb = b.GetPosition()
    return math.hypot(pcbnew.ToMM(pa.x - pb.x), pcbnew.ToMM(pa.y - pb.y))


def nearest_mm(item, candidates) -> float:
    return min(distance_mm(item, candidate) for candidate in candidates)


def edge_distance_mm(a, b) -> float:
    """Shortest distance between axis-aligned pad copper bounding boxes."""
    aa = a.GetBoundingBox()
    bb = b.GetBoundingBox()
    dx = max(0, max(aa.GetLeft(), bb.GetLeft()) - min(aa.GetRight(), bb.GetRight()))
    dy = max(0, max(aa.GetTop(), bb.GetTop()) - min(aa.GetBottom(), bb.GetBottom()))
    return math.hypot(pcbnew.ToMM(dx), pcbnew.ToMM(dy))


def nearest_edge_mm(item, candidates) -> float:
    return min(edge_distance_mm(item, candidate) for candidate in candidates)


def main() -> int:
    failures: list[str] = []
    model = load_model()
    expected = {
        comp.ref: comp
        for sheet in model.sheets()
        for comp in sheet.components
        if comp.watchdog_pcb
    }
    board_path = OUT / "project-button-v3.kicad_pcb"
    require(board_path.is_file(), "native PCB source missing", failures)
    if not board_path.is_file():
        return 1
    board = pcbnew.LoadBoard(str(board_path))
    footprints = {footprint.GetReference(): footprint for footprint in board.GetFootprints()}
    board_only = {f"MH{index}" for index in range(1, 5)}
    require(set(footprints) == set(expected) | board_only,
            "PCB footprint membership differs from controlled board subset plus four board-only holes", failures)
    for ref, comp in expected.items():
        footprint = footprints.get(ref)
        if footprint is None:
            continue
        actual = {pad.GetNumber(): pad.GetNetname() for pad in footprint.Pads() if pad.GetNetname()}
        wanted = {pin.number: pin.net for pin in comp.pins}
        require(actual == wanted, f"PCB pad/net mapping differs at {ref}", failures)
    require(board.GetCopperLayerCount() == 2, "candidate is no longer a controlled two-layer board", failures)
    require(len(list(board.Tracks())) == 0, "placement candidate unexpectedly contains tracks or vias", failures)
    require(len(list(board.Zones())) == 0, "placement candidate unexpectedly contains copper zones", failures)

    # TI ISO1212 SLLSEY7G layout controls: the 100 nF side-1 bypass is
    # constrained to a maximum 2 mm copper-edge placement gap, CIN is kept
    # compact, and
    # the high-voltage end of RTHR remains at least 4 mm from receiver/CIN/
    # RSENSE pins. These numeric checks are placement screens, not EMC proof.
    require(footprints["UFB1"].GetFPID().GetLibItemName() == "SSOP-16_3.9x4.9mm_P0.635mm",
            "UFB1 is not using the DBQ body/pitch candidate footprint", failures)
    require(nearest_edge_mm(pad(footprints, "CDEC1", "1"),
                            [pad(footprints, "UFB1", "2"), pad(footprints, "UFB1", "3")]) <= 2.0,
            "CDEC1 VCC pad exceeds the 2 mm UFB1 VCC placement screen", failures)
    require(nearest_edge_mm(pad(footprints, "CDEC1", "2"),
                            [pad(footprints, "UFB1", "1"), pad(footprints, "UFB1", "8")]) <= 2.0,
            "CDEC1 GND pad exceeds the 2 mm UFB1 GND placement screen", failures)
    for channel, sense_pin in (("1", "16"), ("2", "11")):
        require(distance_mm(pad(footprints, f"CFI{channel}", "1"),
                            pad(footprints, "UFB1", sense_pin)) <= 3.5,
                f"CFI{channel} is not compact to UFB1 SENSE{channel}", failures)
        require(nearest_mm(pad(footprints, f"RSN{channel}", "1"),
                           [pad(footprints, "UFB1", sense_pin)]) <= 7.0,
                f"RSN{channel} is not in the controlled field-side cluster", failures)
        high_voltage_pad = pad(footprints, f"RTH{channel}", "1")
        protected_pads = list(footprints["UFB1"].Pads()) + list(footprints[f"CFI{channel}"].Pads()) + list(footprints[f"RSN{channel}"].Pads())
        require(nearest_edge_mm(high_voltage_pad, protected_pads) >= 4.0,
                f"RTH{channel} high-voltage pad violates TI's 4 mm placement screen", failures)

    ufb_x = pcbnew.ToMM(footprints["UFB1"].GetPosition().x)
    for ref in ("CFI1", "RSN1", "RTH1", "RW1", "CFI2", "RSN2", "RTH2", "RW2", "JWF1"):
        require(pcbnew.ToMM(footprints[ref].GetPosition().x) > ufb_x,
                f"{ref} is not on the controlled field-input side of UFB1", failures)
    for ref in ("CDEC1", "RSO1", "RPD1", "RSO2", "RPD2", "WDCTRL1"):
        require(pcbnew.ToMM(footprints[ref].GetPosition().x) < ufb_x,
                f"{ref} is not on the controlled logic side of UFB1", failures)

    # TPL7407L SLRS066D requires COM transient control and wide output/return
    # copper. The local capacitor loop is screened here; slew rate, trace width,
    # fault current and thermal evidence remain physical routing/test gates.
    for channel in ("1", "2"):
        require(distance_mm(pad(footprints, f"CDRV{channel}", "1"),
                            pad(footprints, f"UDRV{channel}", "9")) <= 3.5,
                f"CDRV{channel} is not compact to UDRV{channel} COM", failures)
        require(nearest_mm(pad(footprints, f"CDRV{channel}", "2"),
                           [pad(footprints, f"UDRV{channel}", str(number)) for number in range(2, 9)]) <= 3.5,
                f"CDRV{channel} is not compact to UDRV{channel} GND", failures)

    title = board.GetTitleBlock()
    require(title.GetRevision() == "PCB-P0.2 / Electrical V3-P1.0", "PCB title-block revision mismatch", failures)
    require(WARNING in board_path.read_text(encoding="utf-8-sig"), "PCB warning missing", failures)
    require("UNROUTED" in board_path.read_text(encoding="utf-8-sig"), "unrouted status missing from PCB", failures)

    project = json.loads((OUT / "project-button-v3.kicad_pro").read_text(encoding="utf-8-sig"))
    default = next((item for item in project["net_settings"]["classes"] if item.get("name") == "Default"), {})
    require(default.get("clearance") == 0.15, "controlled 0.15 mm candidate copper clearance missing", failures)
    require(default.get("track_width") == 0.25, "controlled 0.25 mm candidate track width missing", failures)

    drc = (OUT / "validation" / "project-button-v3-pcb-placement-drc.rpt").read_text(encoding="utf-8-sig")
    require("Found 0 DRC violations" in drc, "placement DRC has non-unrouted violations", failures)
    unconnected = re.search(r"Found (\d+) unconnected pads", drc)
    require(unconnected is not None and int(unconnected.group(1)) == 68,
            "controlled unrouted-pad count differs from 68", failures)
    log = (OUT / "validation" / "project-button-v3-pcb-placement-cli.log").read_text(encoding="utf-8-sig")
    require(log.count("exit=0") == 2, "PCB DRC/render command did not both exit 0", failures)
    render = OUT / "output" / "project-button-v3-pcb-placement-top.png"
    require(render.is_file() and render.stat().st_size > 30_000, "PCB top render missing or unexpectedly small", failures)
    for name in ("MKDS_1_2_3P5.kicad_mod", "MKDS_1_4_3P5.kicad_mod", "VO618A_Option7_SMD.kicad_mod"):
        require((OUT / "PBV3_Footprints.pretty" / name).is_file(), f"custom candidate footprint missing: {name}", failures)

    constraint_evidence = {
        "status": WARNING,
        "board_revision": "PCB-P0.2",
        "electrical_revision": "Electrical V3-P1.0",
        "generated_date": "2026-08-06",
        "manufacturer_sources": [
            {
                "manufacturer": "Texas Instruments",
                "document": "ISO121x datasheet SLLSEY7G",
                "revision": "G, revised February 2025",
                "accessed": "2026-08-06",
                "url": "https://www.ti.com/lit/ds/symlink/iso1211.pdf",
            },
            {
                "manufacturer": "Texas Instruments",
                "document": "TPL7407L datasheet SLRS066D",
                "revision": "D, revised March 2016",
                "accessed": "2026-08-06",
                "url": "https://www.ti.com/lit/ds/symlink/tpl7407l.pdf",
            },
        ],
        "measured_placement_screens_mm": {
            "CDEC1_VCC_to_UFB1_VCC_edge_max": round(nearest_edge_mm(
                pad(footprints, "CDEC1", "1"),
                [pad(footprints, "UFB1", "2"), pad(footprints, "UFB1", "3")]), 4),
            "CDEC1_GND_to_UFB1_GND_edge_max": round(nearest_edge_mm(
                pad(footprints, "CDEC1", "2"),
                [pad(footprints, "UFB1", "1"), pad(footprints, "UFB1", "8")]), 4),
            "CFI1_to_UFB1_SENSE1_centres": round(distance_mm(
                pad(footprints, "CFI1", "1"), pad(footprints, "UFB1", "16")), 4),
            "CFI2_to_UFB1_SENSE2_centres": round(distance_mm(
                pad(footprints, "CFI2", "1"), pad(footprints, "UFB1", "11")), 4),
            "RTH1_high_voltage_to_protected_copper_min": round(nearest_edge_mm(
                pad(footprints, "RTH1", "1"),
                list(footprints["UFB1"].Pads()) + list(footprints["CFI1"].Pads()) + list(footprints["RSN1"].Pads())), 4),
            "RTH2_high_voltage_to_protected_copper_min": round(nearest_edge_mm(
                pad(footprints, "RTH2", "1"),
                list(footprints["UFB1"].Pads()) + list(footprints["CFI2"].Pads()) + list(footprints["RSN2"].Pads())), 4),
            "CDRV1_to_UDRV1_COM_centres": round(distance_mm(
                pad(footprints, "CDRV1", "1"), pad(footprints, "UDRV1", "9")), 4),
            "CDRV2_to_UDRV2_COM_centres": round(distance_mm(
                pad(footprints, "CDRV2", "1"), pad(footprints, "UDRV2", "9")), 4),
        },
        "routing_state": {"tracks": len(list(board.Tracks())), "zones": len(list(board.Zones())), "unconnected_pads": 68},
        "limitations": [
            "Placement screens are not routed-copper path measurements.",
            "No trace-width, stack-up, fabrication, EMC, thermal, COM-slew or fault evidence is released.",
            "UFB1 field and logic returns share SAFETY_0V; no galvanic-isolation or safety credit is claimed.",
        ],
    }
    evidence_path = OUT / "validation" / "project-button-v3-pcb-placement-constraints.json"
    evidence_path.write_text(json.dumps(constraint_evidence, indent=2) + "\n", encoding="utf-8")
    model.manifest()

    if failures:
        print("HR-V0 watchdog PCB placement validation: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("HR-V0 watchdog PCB constrained-placement validation: PASS")
    print("26 board-mounted references; 4 board-only M3 holes; 0 routed tracks; 0 zones")
    print("TI placement screens: CDEC <=2 mm; CIN compact; RTH high side >=4 mm; field/control zoning PASS")
    print("KiCad DRC: 0 non-unrouted violations; 68 unconnected pads are the controlled open routing gate")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
