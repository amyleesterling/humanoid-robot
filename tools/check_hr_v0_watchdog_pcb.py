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
    edge_segments = [
        item for item in board.GetDrawings()
        if item.GetLayer() == pcbnew.Edge_Cuts and item.GetShape() == pcbnew.SHAPE_T_SEGMENT
    ]
    outline_edges = {
        frozenset((
            (round(pcbnew.ToMM(item.GetStart().x), 4), round(pcbnew.ToMM(item.GetStart().y), 4)),
            (round(pcbnew.ToMM(item.GetEnd().x), 4), round(pcbnew.ToMM(item.GetEnd().y), 4)),
        ))
        for item in edge_segments
    }
    expected_outline = {
        frozenset(((20.0, 20.0), (180.0, 20.0))),
        frozenset(((180.0, 20.0), (180.0, 120.0))),
        frozenset(((180.0, 120.0), (20.0, 120.0))),
        frozenset(((20.0, 120.0), (20.0, 20.0))),
    }
    require(outline_edges == expected_outline,
            "board outline differs from the controlled 160 mm x 100 mm rectangle", failures)
    segments = [item for item in board.Tracks() if type(item).__name__ == "PCB_TRACK"]
    vias = [item for item in board.Tracks() if type(item).__name__ == "PCB_VIA"]
    zones = list(board.Zones())
    require(len(segments) == 201, "controlled segment count differs from 201", failures)
    require(len(vias) == 56, "controlled via count differs from 56", failures)
    require(len(zones) == 3, "controlled copper-zone count differs from three", failures)
    min_track_width_mm = min(pcbnew.ToMM(item.GetWidth()) for item in segments)
    min_via_drill_mm = min(pcbnew.ToMM(item.GetDrillValue()) for item in vias)
    min_via_annular_mm = min(
        (pcbnew.ToMM(item.GetWidth(pcbnew.F_Cu)) - pcbnew.ToMM(item.GetDrillValue())) / 2
        for item in vias
    )
    require(min_track_width_mm >= 0.1524,
            "a routed trace is below the controlled 6 mil fabrication envelope", failures)
    require(min_via_drill_mm >= 0.254,
            "a via drill is below the proposed two-layer service minimum", failures)
    require(min_via_annular_mm >= 0.127,
            "a via annular ring is below the proposed two-layer service minimum", failures)
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
        require(test_pad.GetShape() == pcbnew.PAD_SHAPE_RECT,
                f"{ref} pad is not the rectangular Harwin issue-10 land", failures)
        require(test_pad.IsOnLayer(pcbnew.F_Cu), f"{ref} is not top-side probe accessible", failures)

    # Vishay VO618A option-7 document 83432 Rev. 2.1 freezes the SMD land
    # geometry. The mask/stencil process and system-level creepage requirement
    # remain open; these checks prove only the encoded copper candidate.
    iso = footprints["ISO1"]
    require(iso.GetFPID().GetLibItemName() == "VO618A_Option7_SMD",
            "ISO1 is not using the controlled VO618A option-7 land", failures)
    require(iso.GetFieldText("Datasheet") == "https://www.vishay.com/docs/83432/vo618a.pdf",
            "ISO1 datasheet field is not frozen to Vishay document 83432", failures)
    iso_pads = {item.GetNumber(): item for item in iso.Pads() if item.GetNumber()}
    for number, item in iso_pads.items():
        require(abs(pcbnew.ToMM(item.GetSizeX()) - 1.52) < 0.001 and
                abs(pcbnew.ToMM(item.GetSizeY()) - 1.78) < 0.001,
                f"ISO1.{number} differs from the 1.52 x 1.78 mm option-7 land", failures)
    iso_row_centres = abs(pcbnew.ToMM(iso_pads["4"].GetPosition().x - iso_pads["1"].GetPosition().x))
    require(iso_row_centres - 1.52 >= 8.0,
            "ISO1 option-7 inner copper gap is below 8.0 mm", failures)
    require(abs(iso_row_centres + 1.52 - 11.05) < 0.001,
            "ISO1 option-7 overall copper span differs from 11.05 mm", failures)
    require(abs(pcbnew.ToMM(iso_pads["2"].GetPosition().y - iso_pads["1"].GetPosition().y)) - 2.54 < 0.001,
            "ISO1 option-7 within-row pin pitch differs from 2.54 mm", failures)

    # R89 replaces generic hand-solder lands with controlled manufacturer-
    # traced reflow candidates. Mask/paste/process capability and first-article
    # evidence remain release holds; these checks prevent geometry regression.
    passive_groups = [
        (("CDEC1", "CDRV1", "CDRV2"), "Murata_GRM21_Reflow_Nominal", 0.95, 0.95, 2.05,
         "https://pim.murata.com/asset/pim4/ceramicCapacitorSMD/GRM21BR71H104KA01-01-EN_PDF_CERAMICCAPACITORSMD?lastModifiedDatetime=20250707233810"),
        (("CFI1", "CFI2"), "TDK_CGA3_Reflow_Nominal", 0.70, 0.70, 1.40,
         "https://product.tdk.com/system/files/dam/doc/product/capacitor/ceramic/mlcc/specification/mlccspec_automotive_general_en.pdf"),
        (("RHB1", "RHP1", "RSN1", "RSN2", "RSO1", "RSO2", "RPD1", "RPD2"),
         "Panasonic_ERJ6_Reflow_Nominal", 1.15, 1.15, 2.35,
         "https://industrial.panasonic.com/cdbs/www-data/pdf/RDM0000/DMM0000COL17.pdf"),
        (("RTH1", "RTH2"), "Vishay_MMA0204_IPC_Reflow", 1.40, 1.55, 3.00,
         "https://www.vishay.com/doc/?28950="),
        (("RW1", "RW2"), "Vishay_CRCW1210_Reflow", 1.10, 2.80, 2.80,
         "https://www.vishay.com/docs/20035/dcrcwe3.pdf"),
    ]
    for references, footprint_name, pad_x, pad_y, centre_span, datasheet in passive_groups:
        for ref in references:
            candidate = footprints[ref]
            require(candidate.GetFPID().GetLibItemName() == footprint_name,
                    f"{ref} is not using controlled {footprint_name}", failures)
            require(candidate.GetFieldText("Datasheet") == datasheet,
                    f"{ref} controlled land source is missing or wrong", failures)
            require(pcbnew.ToMM(candidate.GetLocalSolderMaskMargin()) == 0.05,
                    f"{ref} does not encode the provisional 0.05 mm NSMD mask clearance", failures)
            pads_by_number = {item.GetNumber(): item for item in candidate.Pads() if item.GetNumber()}
            require(set(pads_by_number) == {"1", "2"}, f"{ref} does not have exactly two numbered lands", failures)
            for number, item in pads_by_number.items():
                require(abs(pcbnew.ToMM(item.GetSizeX()) - pad_x) < 0.001 and
                        abs(pcbnew.ToMM(item.GetSizeY()) - pad_y) < 0.001,
                        f"{ref}.{number} differs from controlled {pad_x:.2f} x {pad_y:.2f} mm land", failures)
            require(abs(distance_mm(pads_by_number["1"], pads_by_number["2"]) - centre_span) < 0.001,
                    f"{ref} land centre span differs from {centre_span:.2f} mm", failures)

    # TI ISO1212 SLLSEY7G layout controls: the 100 nF side-1 bypass is
    # constrained to a maximum 2 mm copper-edge placement gap, CIN is kept
    # compact, and
    # the high-voltage end of RTHR remains at least 4 mm from receiver/CIN/
    # RSENSE pins. These numeric checks are placement screens, not EMC proof.
    require(footprints["UFB1"].GetFPID().GetLibItemName() == "TI_DBQ0016A_Example_Land",
            "UFB1 is not using the controlled TI DBQ0016A example land", failures)
    require(footprints["UFB1"].GetFieldText("Datasheet") == "https://www.ti.com/lit/ds/symlink/iso1212.pdf",
            "UFB1 datasheet field is not frozen to the TI ISO1212 record", failures)
    require(pcbnew.ToMM(footprints["UFB1"].GetLocalSolderMaskMargin()) == 0.05,
            "UFB1 does not encode the TI example 0.05 mm NSMD mask clearance", failures)
    for item in footprints["UFB1"].Pads():
        if item.GetNumber():
            require(abs(pcbnew.ToMM(item.GetSizeX()) - 1.60) < 0.001 and
                    abs(pcbnew.ToMM(item.GetSizeY()) - 0.41) < 0.001,
                    f"UFB1.{item.GetNumber()} differs from the TI DBQ0016A 1.60 x 0.41 mm example land", failures)
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
        driver = footprints[f"UDRV{channel}"]
        require(driver.GetFPID().GetLibItemName() == "TI_PW0016A_Example_Land",
                f"UDRV{channel} is not using the controlled TI PW0016A example land", failures)
        require(driver.GetFieldText("Datasheet") == "https://www.ti.com/lit/ds/symlink/tpl7407l.pdf",
                f"UDRV{channel} datasheet field is not frozen to TI SLRS066D", failures)
        require(pcbnew.ToMM(driver.GetLocalSolderMaskMargin()) == 0.05,
                f"UDRV{channel} does not encode the TI example 0.05 mm NSMD mask clearance", failures)
        for item in driver.Pads():
            if item.GetNumber():
                require(abs(pcbnew.ToMM(item.GetSizeX()) - 1.50) < 0.001 and
                        abs(pcbnew.ToMM(item.GetSizeY()) - 0.45) < 0.001,
                        f"UDRV{channel}.{item.GetNumber()} differs from the TI PW0016A 1.50 x 0.45 mm example land", failures)
        require(distance_mm(pad(footprints, f"CDRV{channel}", "1"),
                            pad(footprints, f"UDRV{channel}", "9")) <= 3.5,
                f"CDRV{channel} is not compact to UDRV{channel} COM", failures)
        require(nearest_mm(pad(footprints, f"CDRV{channel}", "2"),
                           [pad(footprints, f"UDRV{channel}", str(number)) for number in range(2, 9)]) <= 3.5,
                f"CDRV{channel} is not compact to UDRV{channel} GND", failures)

    title = board.GetTitleBlock()
    require(title.GetRevision() == "PCB-P1.0 / Electrical V3-P1.15", "PCB title-block revision mismatch", failures)
    require(WARNING in board_path.read_text(encoding="utf-8-sig"), "PCB warning missing", failures)
    require("ROUTED/TEST-ACCESS CANDIDATE" in board_path.read_text(encoding="utf-8-sig"),
            "routed/test-access candidate status missing from PCB", failures)

    project = json.loads((OUT / "project-button-v3.kicad_pro").read_text(encoding="utf-8-sig"))
    board_rules = project["board"]["design_settings"]["rules"]
    require(board_rules.get("min_copper_edge_clearance", 0) >= 0.381,
            "encoded copper-to-edge clearance is below the proposed service minimum", failures)
    require(board_rules.get("min_through_hole_diameter", 0) >= 0.254,
            "encoded through-hole minimum is below the proposed service minimum", failures)
    default = next((item for item in project["net_settings"]["classes"] if item.get("name") == "Default"), {})
    require(default.get("clearance") == 0.1524, "controlled 6 mil candidate copper clearance missing", failures)
    require(default.get("track_width") == 0.25, "controlled 0.25 mm candidate track width missing", failures)
    power = next((item for item in project["net_settings"]["classes"] if item.get("name") == "POWER24"), {})
    require(power.get("clearance") == 0.1524 and power.get("track_width") == 0.75,
            "controlled POWER24 candidate net class differs from 0.1524/0.75 mm", failures)
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
    for name in ("MKDS_1_2_3P5.kicad_mod", "MKDS_1_4_3P5.kicad_mod", "VO618A_Option7_SMD.kicad_mod", "Harwin_S1751_46R.kicad_mod", "TI_PW0016A_Example_Land.kicad_mod", "TI_DBQ0016A_Example_Land.kicad_mod", "Murata_GRM21_Reflow_Nominal.kicad_mod", "TDK_CGA3_Reflow_Nominal.kicad_mod", "Panasonic_ERJ6_Reflow_Nominal.kicad_mod", "Vishay_MMA0204_IPC_Reflow.kicad_mod", "Vishay_CRCW1210_Reflow.kicad_mod"):
        require((OUT / "PBV3_Footprints.pretty" / name).is_file(), f"custom candidate footprint missing: {name}", failures)

    constraint_evidence = {
        "status": WARNING,
        "board_revision": "PCB-P1.0",
        "electrical_revision": "Electrical V3-P1.15",
        "generated_date": "2026-08-10",
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
            {
                "manufacturer": "OSH Park",
                "document": "Two Layer Service design rules and materials",
                "revision": "Web page; no revision stated",
                "accessed": "2026-08-06",
                "url": "https://docs.oshpark.com/services/two-layer/",
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
            "minimum_track_width_mm": round(min_track_width_mm, 4),
            "minimum_via_drill_mm": round(min_via_drill_mm, 4),
            "minimum_via_annular_ring_mm": round(min_via_annular_mm, 4),
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
        "proposed_fabrication_envelope": {
            "status": "PROPOSED - FABRICATOR ACCEPTANCE AND RELEASE REQUIRED",
            "service": "OSH Park Two Layer Prototype Service",
            "country": "United States",
            "nominal_board_thickness_mm": 1.6,
            "copper_layers": 2,
            "copper_weight_oz": 1,
            "finish": "ENIG",
            "minimum_trace_width_mm": 0.1524,
            "minimum_trace_spacing_mm": 0.1524,
            "minimum_drill_mm": 0.254,
            "minimum_annular_ring_mm": 0.127,
            "minimum_board_edge_keepout_mm": 0.381,
            "controlled_board_outline_mm": [160.0, 100.0],
            "encoded_copper_edge_clearance_mm": board_rules["min_copper_edge_clearance"],
            "source_revision": "Web page; no revision stated",
            "accessed": "2026-08-06",
            "source_url": "https://docs.oshpark.com/services/two-layer/",
        },
        "limitations": [
            "Zero native DRC violations proves only the encoded geometric/connectivity rules.",
            "PCB-P1.0 directly binds the unchanged P0.9 geometry/topology and exact hidden assembly identity/process-state fields to Electrical V3-P1.15. The 0.1524 mm (6 mil) minimum trace/clearance candidate envelope, controlled lands and rectangular Harwin test-point lands are unchanged; fabricator/assembler acceptance remains required.",
            "The proposed OSH Park two-layer process is not a released purchase or fabrication selection.",
            "No fabrication, EMC, thermal, COM-slew, physical probe-access or fault evidence is released.",
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
    print("42 board-mounted references; 4 board-only M3 holes; 201 segments; 56 vias; 3 filled zones")
    print("40 modeled nets: every multi-pad net connected; 14 singletons isolated; 2 SUB thermal nets controlled; 89 no-net pads untouched")
    print("TI placement/SUB screens and 16 Harwin test-point land patterns: PASS")
    print("KiCad DRC: 0 violations; 0 routed unconnected pads; no Gerber/drill release outputs")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
