"""Validate the HR-V0 watchdog PCB routed/test-access candidate.

Run this checker with KiCad's bundled Python. It independently proves source
consistency, placement membership, manufacturer-derived geometry screens,
routed pad connectivity, intentional singleton isolation, copper counts and
native KiCad DRC status. It does not release fabrication, assembly,
energization or safety credit.
"""

from __future__ import annotations

import importlib.util
import heapq
import json
import math
import re
import sys
from pathlib import Path

import pcbnew


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "electrical" / "kicad" / "project-button-v3"
WARNING = "PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION"
TESTPOINT_NETS = {
    "TP1": "SAFETY_24V", "TP2": "SAFETY_0V", "TP3": "WD_5V", "TP4": "WD_3V3",
    "TP5": "PI_HEARTBEAT", "TP6": "WD_HEARTBEAT", "TP7": "WD1_DRIVE", "TP8": "WD2_DRIVE",
    "TP9": "WD1_COIL_N", "TP10": "WD2_COIL_N", "TP11": "WD1_NC_24V", "TP12": "WD2_NC_24V",
    "TP13": "UFB_OUT1", "TP14": "UFB_OUT2", "TP15": "WD_SWDIO", "TP16": "WD_SWCLK",
}
FLOATING_SUB_NETS = {"INTENTIONALLY_UNUSED_UFB1_12", "INTENTIONALLY_UNUSED_UFB1_13"}


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


def routed_path_mm(board, start_pad, end_pad) -> float:
    """Return the shortest explicit track/via path between two pad centres."""
    graph = {}

    def connect(a, b, distance):
        graph.setdefault(a, []).append((b, distance))
        graph.setdefault(b, []).append((a, distance))

    for item in board.Tracks():
        if type(item).__name__ == "PCB_TRACK":
            start = (item.GetStart().x, item.GetStart().y, item.GetLayer())
            end = (item.GetEnd().x, item.GetEnd().y, item.GetLayer())
            connect(start, end, math.hypot(
                pcbnew.ToMM(item.GetEnd().x - item.GetStart().x),
                pcbnew.ToMM(item.GetEnd().y - item.GetStart().y),
            ))
        elif type(item).__name__ == "PCB_VIA":
            point_f = (item.GetPosition().x, item.GetPosition().y, pcbnew.F_Cu)
            point_b = (item.GetPosition().x, item.GetPosition().y, pcbnew.B_Cu)
            connect(point_f, point_b, 0.0)
    start = (start_pad.GetPosition().x, start_pad.GetPosition().y, pcbnew.F_Cu)
    end = (end_pad.GetPosition().x, end_pad.GetPosition().y, pcbnew.F_Cu)
    queue = [(0.0, start)]
    best = {start: 0.0}
    while queue:
        distance, node = heapq.heappop(queue)
        if node == end:
            return distance
        if distance != best.get(node):
            continue
        for neighbor, increment in graph.get(node, []):
            candidate = distance + increment
            if candidate < best.get(neighbor, math.inf):
                best[neighbor] = candidate
                heapq.heappush(queue, (candidate, neighbor))
    return math.inf


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
    segments = [item for item in board.Tracks() if type(item).__name__ == "PCB_TRACK"]
    vias = [item for item in board.Tracks() if type(item).__name__ == "PCB_VIA"]
    zones = list(board.Zones())
    require(len(segments) == 200, "controlled segment count differs from 200", failures)
    require(len(vias) == 56, "controlled via count differs from 56", failures)
    require(len(zones) == 3, "controlled copper-zone count differs from three", failures)
    zones_by_net = {zone.GetNetname(): zone for zone in zones}
    require(set(zones_by_net) == {"SAFETY_0V"} | FLOATING_SUB_NETS,
            "zone nets differ from SAFETY_0V plus the two isolated SUB nets", failures)
    for net_name, zone in zones_by_net.items():
        require(zone.IsOnLayer(pcbnew.B_Cu), f"{net_name} zone is not on B.Cu", failures)
        require(zone.IsFilled() and zone.HasFilledPolysForLayer(pcbnew.B_Cu),
                f"{net_name} zone does not contain a saved B.Cu fill", failures)
        if net_name in FLOATING_SUB_NETS:
            bounds = zone.Outline().BBox()
            require(abs(pcbnew.ToMM(bounds.GetWidth()) - 2.0) < 0.001 and
                    abs(pcbnew.ToMM(bounds.GetHeight()) - 2.0) < 0.001,
                    f"{net_name} thermal plane is not exactly 2 mm x 2 mm", failures)

    # Independently rebuild KiCad connectivity. Every modeled net with more
    # than one pad must form one connected pad set. Every modeled singleton
    # and every footprint pad without a net must remain free of route copper.
    connectivity = board.GetConnectivity()
    connectivity.Build(board)
    require(connectivity.GetUnconnectedCount(False) == 0,
            "KiCad connectivity engine reports an open routed connection", failures)
    modeled_by_net = {}
    for ref, comp in expected.items():
        for pin in comp.pins:
            modeled_by_net.setdefault(pin.net, []).append(pad(footprints, ref, pin.number))
    singleton_records = []
    floating_sub_records = []
    for net_name, net_pads in modeled_by_net.items():
        expected_ids = {item.m_Uuid.AsString() for item in net_pads}
        if len(net_pads) > 1:
            for item in net_pads:
                connected_ids = {
                    connected.m_Uuid.AsString()
                    for connected in connectivity.GetConnectedItems(item)
                    if isinstance(connected, pcbnew.PAD)
                }
                require(connected_ids == expected_ids,
                        f"routed pad set is incomplete or contaminated at {net_name}", failures)
        elif net_name in FLOATING_SUB_NETS:
            item = net_pads[0]
            connected = list(connectivity.GetConnectedItems(item))
            connected_pads = {
                connected.m_Uuid.AsString()
                for connected in connected
                if isinstance(connected, pcbnew.PAD)
            }
            require(connected_pads == expected_ids,
                    f"floating SUB net {net_name} reaches another pad", failures)
            net_segments = [track for track in segments if track.GetNetname() == net_name]
            net_vias = [via for via in vias if via.GetNetname() == net_name]
            require(bool(net_segments) and bool(net_vias) and net_name in zones_by_net,
                    f"floating SUB net {net_name} lacks controlled trace/via/plane copper", failures)
            floating_sub_records.append({
                "net": net_name,
                "reference": item.GetParentFootprint().GetReference(),
                "pad": item.GetNumber(),
                "segments": len(net_segments),
                "vias": len(net_vias),
            })
        else:
            item = net_pads[0]
            connected = list(connectivity.GetConnectedItems(item))
            require(len(connected) == 1 and connected[0].m_Uuid == item.m_Uuid,
                    f"intentional singleton {net_name} touches route copper", failures)
            singleton_records.append({
                "net": net_name,
                "reference": item.GetParentFootprint().GetReference(),
                "pad": item.GetNumber(),
            })
    require(len(singleton_records) == 14, "controlled isolated singleton-pad count differs from 14", failures)
    require(len(floating_sub_records) == 2, "controlled floating-SUB count differs from two", failures)
    no_net_pads = [
        item
        for footprint in board.GetFootprints()
        for item in footprint.Pads()
        if not item.GetNetname()
    ]
    require(len(no_net_pads) == 89, "controlled no-net pad count differs from 89", failures)
    for item in no_net_pads:
        require(len(list(connectivity.GetConnectedItems(item))) == 0,
                f"no-net pad touches copper at {item.GetParentFootprint().GetReference()}.{item.GetNumber()}", failures)

    # Harwin drawing S1751-XXR issue 10 freezes the SMT land pattern. These
    # checks prove encoded footprint and net identity; physical probe access
    # still requires assembled-board inspection.
    for ref, net_name in TESTPOINT_NETS.items():
        footprint = footprints[ref]
        require(footprint.GetFPID().GetLibItemName() == "Harwin_S1751_46R",
                f"{ref} does not use the frozen Harwin S1751-46R footprint", failures)
        test_pad = pad(footprints, ref, "1")
        require(test_pad.GetNetname() == net_name, f"{ref} net differs from {net_name}", failures)
        require(abs(pcbnew.ToMM(test_pad.GetSizeX()) - 3.45) < 0.001 and
                abs(pcbnew.ToMM(test_pad.GetSizeY()) - 1.85) < 0.001,
                f"{ref} pad differs from the 3.45 mm x 1.85 mm Harwin land pattern", failures)
        require(test_pad.IsOnLayer(pcbnew.F_Cu), f"{ref} is not top-side probe accessible", failures)

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
    require(title.GetRevision() == "PCB-P0.4 / Electrical V3-P1.1", "PCB title-block revision mismatch", failures)
    require(WARNING in board_path.read_text(encoding="utf-8-sig"), "PCB warning missing", failures)
    require("ROUTED/TEST-ACCESS CANDIDATE" in board_path.read_text(encoding="utf-8-sig"),
            "routed/test-access candidate status missing from PCB", failures)

    project = json.loads((OUT / "project-button-v3.kicad_pro").read_text(encoding="utf-8-sig"))
    default = next((item for item in project["net_settings"]["classes"] if item.get("name") == "Default"), {})
    require(default.get("clearance") == 0.15, "controlled 0.15 mm candidate copper clearance missing", failures)
    require(default.get("track_width") == 0.25, "controlled 0.25 mm candidate track width missing", failures)
    power = next((item for item in project["net_settings"]["classes"] if item.get("name") == "POWER24"), {})
    require(power.get("clearance") == 0.15 and power.get("track_width") == 0.75,
            "controlled POWER24 candidate net class differs from 0.15/0.75 mm", failures)
    require(project["net_settings"].get("netclass_assignments") == {
        "SAFETY_24V": "POWER24", "WD1_COIL_N": "POWER24", "WD2_COIL_N": "POWER24"
    }, "POWER24 net assignments differ from the controlled three nets", failures)

    drc = (OUT / "validation" / "project-button-v3-pcb-test-access-drc.rpt").read_text(encoding="utf-8-sig")
    require("Found 0 DRC violations" in drc, "routed/test-access DRC has violations", failures)
    unconnected = re.search(r"Found (\d+) unconnected pads", drc)
    require(unconnected is not None and int(unconnected.group(1)) == 0,
            "native DRC routed-unconnected count differs from zero", failures)
    log = (OUT / "validation" / "project-button-v3-pcb-test-access-cli.log").read_text(encoding="utf-8-sig")
    require(log.count("exit=0") == 3, "PCB DRC/top-render/bottom-render commands did not all exit 0", failures)
    for side in ("top", "bottom"):
        render = OUT / "output" / f"project-button-v3-pcb-test-access-{side}.png"
        require(render.is_file() and render.stat().st_size > 20_000,
                f"PCB {side} render missing or unexpectedly small", failures)
    fabrication_outputs = [
        path for path in OUT.rglob("*")
        if path.is_file() and path.suffix.lower() in {".gbr", ".ger", ".drl", ".xln", ".gbrjob"}
    ]
    require(not fabrication_outputs, "Gerber/drill fabrication outputs exist despite the open release gate", failures)
    for name in ("MKDS_1_2_3P5.kicad_mod", "MKDS_1_4_3P5.kicad_mod", "VO618A_Option7_SMD.kicad_mod", "Harwin_S1751_46R.kicad_mod"):
        require((OUT / "PBV3_Footprints.pretty" / name).is_file(), f"custom candidate footprint missing: {name}", failures)

    constraint_evidence = {
        "status": WARNING,
        "board_revision": "PCB-P0.4",
        "electrical_revision": "Electrical V3-P1.1",
        "generated_date": "2026-08-06",
        "manufacturer_sources": [
            {
                "manufacturer": "Texas Instruments",
                "document": "ISO121x datasheet SLLSEY7G",
                "revision": "G, revised February 2025",
                "accessed": "2026-08-06",
                "url": "https://www.ti.com/lit/ds/symlink/iso1212.pdf",
            },
            {
                "manufacturer": "Texas Instruments",
                "document": "TPL7407L datasheet SLRS066D",
                "revision": "D, revised March 2016",
                "accessed": "2026-08-06",
                "url": "https://www.ti.com/lit/ds/symlink/tpl7407l.pdf",
            },
            {
                "manufacturer": "Harwin",
                "document": "S1751-XXR technical drawing DRG 02202",
                "revision": "Issue 10, 2023-02-15",
                "accessed": "2026-08-06",
                "url": "https://content.harwin.com/asset/e4e6a5e1-de35-4a2b-8b49-ff06562cba9d/DRG-02202-Technical-Drawing-Datasheet-S1751R-pdf.pdf",
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
        "measured_explicit_route_paths_mm": {
            "CDEC1_VCC_to_UFB1_VCC2": round(routed_path_mm(
                board, pad(footprints, "CDEC1", "1"), pad(footprints, "UFB1", "2")), 4),
            "CDEC1_VCC_to_UFB1_VCC3": round(routed_path_mm(
                board, pad(footprints, "CDEC1", "1"), pad(footprints, "UFB1", "3")), 4),
            "CDRV1_to_UDRV1_COM": round(routed_path_mm(
                board, pad(footprints, "CDRV1", "1"), pad(footprints, "UDRV1", "9")), 4),
            "CDRV1_GND_to_UDRV1_GND8": round(routed_path_mm(
                board, pad(footprints, "CDRV1", "2"), pad(footprints, "UDRV1", "8")), 4),
            "CDRV2_to_UDRV2_COM": round(routed_path_mm(
                board, pad(footprints, "CDRV2", "1"), pad(footprints, "UDRV2", "9")), 4),
            "CDRV2_GND_to_UDRV2_GND8": round(routed_path_mm(
                board, pad(footprints, "CDRV2", "2"), pad(footprints, "UDRV2", "8")), 4),
        },
        "routing_state": {
            "segments": len(segments),
            "vias": len(vias),
            "zones": len(zones),
            "native_unconnected_pads": 0,
            "intentional_singleton_pads": singleton_records,
            "floating_sub_copper": floating_sub_records,
            "test_points": TESTPOINT_NETS,
            "no_net_pads": len(no_net_pads),
            "track_widths_mm": sorted({round(pcbnew.ToMM(item.GetWidth()), 4) for item in segments}),
            "route_lengths_mm": {
                net_name: round(sum(
                    math.hypot(
                        pcbnew.ToMM(item.GetEnd().x - item.GetStart().x),
                        pcbnew.ToMM(item.GetEnd().y - item.GetStart().y),
                    )
                    for item in segments if item.GetNetname() == net_name
                ), 4)
                for net_name in sorted({item.GetNetname() for item in segments})
            },
        },
        "limitations": [
            "Zero native DRC violations proves only the encoded geometric/connectivity rules.",
            "The 0.10 mm fine-pitch breakouts require fabricator capability selection and review.",
            "No stack-up, fabrication, EMC, thermal, COM-slew, physical probe-access or fault evidence is released.",
            "UFB1 field and logic returns share SAFETY_0V; no galvanic-isolation or safety credit is claimed.",
        ],
    }
    evidence_path = OUT / "validation" / "project-button-v3-pcb-test-access-evidence.json"
    evidence_path.write_text(json.dumps(constraint_evidence, indent=2) + "\n", encoding="utf-8")
    model.manifest()

    if failures:
        print("HR-V0 watchdog PCB routed/test-access validation: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("HR-V0 watchdog PCB routed/test-access validation: PASS")
    print("42 board-mounted references; 4 board-only M3 holes; 200 segments; 56 vias; 3 filled zones")
    print("40 modeled nets: every multi-pad net connected; 14 singletons isolated; 2 SUB thermal nets controlled; 89 no-net pads untouched")
    print("TI placement/SUB screens and 16 Harwin test-point land patterns: PASS")
    print("KiCad DRC: 0 violations; 0 routed unconnected pads; no Gerber/drill release outputs")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
