#!/usr/bin/env python3
"""Generate the physical E1 controller-to-carrier logic harness candidate.

This module is called by generate_hr30_e1_controls_fixture_p01.py after the
native fixture has been generated.  It adds two placed, pin-for-pin harnesses
and an integrated fixture-with-harness assembly.  It never grants authority to
fabricate, connect, power, or move hardware.
"""

from __future__ import annotations

import csv
import hashlib
import html
import json
import math
import shutil
from datetime import datetime, timezone
from pathlib import Path

import cadquery as cq


ROOT = Path(__file__).resolve().parents[1]
BODY = ROOT / "hr30" / "whole-body-p0.1"
OUT = BODY / "electrical" / "e1-controls-only-fixture-p0.1"
IDENTIFIER = "HR30-E1-LOGIC-HARNESS-P0.1"
WARNING = (
    "PRELIMINARY - UNBUILT E1 LOGIC HARNESS CANDIDATE - NOT APPROVED FOR "
    "CONNECTION, POWERED TESTING, MOTION, WALKING, OR ENERGIZATION"
)
AUTHORITY = "NO CONNECTION, POWERED-TEST, MOTION, WALKING OR ENERGIZATION AUTHORITY"

MCU_TERMINALS = BODY / "electrical/motion-controller-p0.1/terminal-register.csv"
CARRIER_TERMINALS = BODY / "electrical/carriers-p0.1/carrier-terminal-register.csv"
BASE_FIXTURE_STEP = OUT / "HR30_E1_controls_only_fixture_candidate.step"

WIRE = {
    "CTRL_GND": ("Belden", "1852 BK005", "BLACK", (0.04, 0.05, 0.06)),
    "CTRL_5V": ("Belden", "1852 RD005", "RED", (0.78, 0.06, 0.05)),
    "CTRL_3V3": ("Belden", "1852 YL005", "YELLOW", (0.95, 0.68, 0.05)),
    "TX": ("Belden", "1852 BL005", "BLUE", (0.05, 0.33, 0.78)),
    "RX": ("Belden", "1852 WH005", "WHITE", (0.92, 0.92, 0.92)),
    "DIR": ("Belden", "1852 OR005", "ORANGE", (0.96, 0.34, 0.04)),
}

# Coordinates are in the fixture's panel frame and are derived from the exact
# native PCB footprint coordinates and the E1 placement register.  The cable
# leaves each top-entry header, turns through an adjacent base opening, and is
# routed below the panel.  The paths are candidates; received fit remains open.
HARNESS = {
    "E1-HA-A": {
        "mcu_ref": "JCA1",
        "carrier_ref": "JCA1",
        "board": "A",
        "positions": 15,
        "populated": 15,
        "cut_length_mm": 320.0,
        "center_path": [
            (-116.0, -59.0, 20.0), (-116.0, -69.0, 20.0),
            (-116.0, -69.0, -7.0), (85.0, -75.0, -7.0),
            (85.0, -75.0, 20.0), (85.0, -65.0, 20.0),
        ],
    },
    "E1-HA-B": {
        "mcu_ref": "JCB1",
        "carrier_ref": "JCB1",
        "board": "B",
        "positions": 15,
        "populated": 12,
        "cut_length_mm": 310.0,
        "center_path": [
            (-68.0, -59.0, 20.0), (-68.0, -69.0, 20.0),
            (-68.0, -69.0, -13.0), (85.0, 21.0, -13.0),
            (85.0, 21.0, 20.0), (85.0, 31.0, 20.0),
        ],
    },
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, data: list[dict]) -> None:
    if not data:
        raise RuntimeError(f"refusing empty table {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(data[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(data)


def clean_step(path: Path) -> None:
    data = path.read_bytes()
    path.write_bytes(data.replace(b" \r\n", b"\r\n").replace(b" \n", b"\n"))


def replace_marker(path: Path, start: str, end: str, content: str) -> None:
    text = path.read_text(encoding="utf-8")
    block = f"{start}\n{content}\n{end}"
    if start in text and end in text:
        before, tail = text.split(start, 1)
        _, after = tail.split(end, 1)
        text = before + block + after
    else:
        text = text.rstrip() + "\n\n" + block + "\n"
    path.write_text(text, encoding="utf-8", newline="\n")


def terminal_map() -> dict[str, list[dict]]:
    mcu = rows(MCU_TERMINALS)
    carrier = rows(CARRIER_TERMINALS)
    result: dict[str, list[dict]] = {}
    for harness_id, spec in HARNESS.items():
        mcu_map = {
            int(row["pad"]): row["net"]
            for row in mcu if row["reference"] == spec["mcu_ref"]
        }
        carrier_map = {
            int(row["pad"]): row["net"]
            for row in carrier
            if row["board"] == spec["board"] and row["reference"] == spec["carrier_ref"]
        }
        expected_mcu = set(range(1, spec["populated"] + 1))
        if set(mcu_map) != expected_mcu:
            raise RuntimeError(f"{harness_id} MCU contact map drift")
        expected_carrier = set(range(1, spec["populated"] + 1))
        if set(carrier_map) != expected_carrier:
            raise RuntimeError(f"{harness_id} carrier contact map drift")
        mapped: list[dict] = []
        for position in range(1, 16):
            mcu_net = mcu_map.get(position, "EMPTY")
            carrier_net = carrier_map.get(position, "EMPTY")
            if mcu_net != carrier_net:
                raise RuntimeError(f"{harness_id}.{position} net mismatch")
            mapped.append({"position": position, "net": carrier_net})
        result[harness_id] = mapped
    return result


def wire_role(net: str) -> str:
    if net in ("CTRL_GND", "CTRL_5V", "CTRL_3V3"):
        return net
    if net.endswith("_TX"):
        return "TX"
    if net.endswith("_RX"):
        return "RX"
    if net.endswith("_DIR"):
        return "DIR"
    raise RuntimeError(f"unclassified logic net {net}")


def path_length(points: list[tuple[float, float, float]]) -> float:
    return sum(math.dist(a, b) for a, b in zip(points, points[1:]))


def segment(a: tuple[float, float, float], b: tuple[float, float, float], radius: float) -> cq.Shape:
    direction = cq.Vector(b[0] - a[0], b[1] - a[1], b[2] - a[2])
    length = direction.Length
    if length <= 1e-9:
        raise RuntimeError("zero-length harness segment")
    return cq.Solid.makeCylinder(radius, length, cq.Vector(*a), direction.normalized())


def physical_wire(points: list[tuple[float, float, float]], radius: float = 0.445) -> cq.Shape:
    solids: list[cq.Shape] = []
    for a, b in zip(points, points[1:]):
        solids.append(segment(a, b, radius))
    for point in points[1:-1]:
        solids.append(cq.Solid.makeSphere(radius, cq.Vector(*point)))
    return cq.Compound.makeCompound(solids)


def housing(center: tuple[float, float, float]) -> cq.Shape:
    # Project-owned clearance envelope based on the official GH catalog's
    # 15-position housing dimensions.  It is not a manufacturer CAD model.
    return cq.Workplane("XY").box(20.0, 6.7, 4.25).translate(center).val()


def write_cad(mapping: dict[str, list[dict]]) -> dict:
    harness_parts: list[cq.Shape] = []
    assembly = cq.Assembly(name="HR30_E1_LOGIC_HARNESSES_P01_NOT_RELEASED")
    wire_count = 0
    for harness_id, spec in HARNESS.items():
        start = spec["center_path"][0]
        finish = spec["center_path"][-1]
        for position_row in mapping[harness_id]:
            position = position_row["position"]
            net = position_row["net"]
            if net == "EMPTY":
                continue
            # The 15 positions form a 1.25 mm pitch row at each connector.
            x_offset = (position - 8) * 1.25
            points = [(x + x_offset, y, z) for x, y, z in spec["center_path"]]
            shape = physical_wire(points)
            role = wire_role(net)
            color = WIRE[role][3]
            assembly.add(shape, name=f"{harness_id}_WIRE_{position:02d}_{net}", color=cq.Color(*color, 1))
            harness_parts.append(shape)
            wire_count += 1
        for endpoint, point in (("MCU", start), ("CARRIER", finish)):
            shell = housing(point)
            assembly.add(shell, name=f"{harness_id}_{endpoint}_GHR15_ENVELOPE", color=cq.Color(0.92, 0.92, 0.90, 0.72))
            harness_parts.append(shell)

    compound = cq.Compound.makeCompound(harness_parts)
    step_path = OUT / "HR30_E1_logic_harness_candidate.step"
    cq.exporters.export(compound, str(step_path))
    clean_step(step_path)
    assembly.save(str(OUT / "HR30_E1_logic_harness_candidate.glb"), tolerance=0.12, angularTolerance=0.10)

    fixture = cq.importers.importStep(str(BASE_FIXTURE_STEP)).val()
    integrated = cq.Compound.makeCompound([fixture, compound])
    integrated_path = OUT / "HR30_E1_controls_fixture_with_logic_harness_candidate.step"
    cq.exporters.export(integrated, str(integrated_path))
    clean_step(integrated_path)
    integrated_assembly = cq.Assembly(name="HR30_E1_FIXTURE_WITH_LOGIC_HARNESSES_P01_NOT_RELEASED")
    integrated_assembly.add(fixture, name="E1_BASE_FIXTURE", color=cq.Color(0.62, 0.68, 0.72, 0.84))
    integrated_assembly.add(compound, name="E1_LOGIC_HARNESS_ASSEMBLIES", color=cq.Color(0.12, 0.42, 0.82, 1))
    integrated_assembly.save(
        str(OUT / "HR30_E1_controls_fixture_with_logic_harness_candidate.glb"),
        tolerance=0.16,
        angularTolerance=0.12,
    )
    bounds = integrated.BoundingBox()
    return {
        "physical_wire_count": wire_count,
        "housing_envelope_count": 4,
        "integrated_extent_mm": [round(bounds.xlen, 6), round(bounds.ylen, 6), round(bounds.zlen, 6)],
    }


def write_registers(mapping: dict[str, list[dict]], geometry: dict) -> None:
    assembly_rows = []
    contact_rows = []
    connector_rows = []
    for harness_id, spec in HARNESS.items():
        route_length = path_length(spec["center_path"])
        assembly_rows.append({
            "harness_id": harness_id,
            "from_connector": f"MCU:{spec['mcu_ref']}",
            "to_connector": f"CARRIER_{spec['board']}:{spec['carrier_ref']}",
            "housing_positions_each_end": 15,
            "populated_conductors": spec["populated"],
            "empty_positions": "NONE" if spec["populated"] == 15 else "13;14;15",
            "cad_centerline_length_mm": f"{route_length:.3f}",
            "candidate_cut_length_mm": f"{spec['cut_length_mm']:.3f}",
            "candidate_service_allowance_mm": f"{spec['cut_length_mm'] - route_length:.3f}",
            "routing": "TOP-ENTRY HEADER TO ADJACENT BASE SLOT; BELOW-PANEL FIXED ROUTE; TOP-ENTRY HEADER",
            "built": "NO",
            "authority": AUTHORITY,
            "warning": WARNING,
        })
        for endpoint in ("MCU", f"CARRIER_{spec['board']}"):
            connector_rows.append({
                "connector_id": f"{harness_id}-{endpoint}",
                "endpoint": endpoint,
                "mating_header": "JST BM15B-GHS-TBT",
                "housing_candidate": "JST GHR-15V-S",
                "contact_candidate": "JST SSHL-002T-P0.2",
                "contact_quantity": spec["populated"],
                "keying": "NATIVE GH POLARIZATION; POSITION 1 MARK MUST BE WITNESSED",
                "received_mating_fit": "NOT EXECUTED",
                "authority": AUTHORITY,
                "warning": WARNING,
            })
        for item in mapping[harness_id]:
            position = item["position"]
            net = item["net"]
            populated = net != "EMPTY"
            role = wire_role(net) if populated else "EMPTY"
            wire = WIRE.get(role)
            contact_rows.append({
                "map_id": f"{harness_id}-{position:02d}",
                "harness_id": harness_id,
                "position": position,
                "mcu_contact": f"{spec['mcu_ref']}.{position}",
                "carrier_contact": f"{spec['carrier_ref']}.{position}" if populated else "EMPTY CAVITY",
                "net": net,
                "population": "POPULATED BOTH ENDS" if populated else "EMPTY BOTH ENDS - NO CONTACT/WIRE",
                "wire_candidate": f"{wire[0]} {wire[1]}" if wire else "NONE",
                "wire_color": wire[2] if wire else "NONE",
                "end_labels": f"{harness_id}-P{position:02d} BOTH ENDS" if populated else "EMPTY-CAVITY WITNESS",
                "cut_length_mm": f"{spec['cut_length_mm']:.3f}" if populated else "NONE",
                "continuity": "NOT EXECUTED",
                "short_to_adjacent": "NOT EXECUTED",
                "retention": "NOT EXECUTED",
                "authority": AUTHORITY,
                "warning": WARNING,
            })
    write_csv(OUT / "logic-harness-assembly-register.csv", assembly_rows)
    write_csv(OUT / "logic-harness-connector-instance-register.csv", connector_rows)
    write_csv(OUT / "logic-harness-contact-map.csv", contact_rows)

    write_csv(OUT / "logic-harness-bom.csv", [
        {"item": "LH-01", "quantity": 4, "manufacturer": "JST", "order_code": "GHR-15V-S", "description": "15-position GH receptacle housing", "selection": "EXACT CANDIDATE; RECEIVED FIT OPEN", "procurement_released": "NO", "warning": WARNING},
        {"item": "LH-02", "quantity": 60, "manufacturer": "JST", "order_code": "SSHL-002T-P0.2", "description": "GH crimp contact; 54 installed plus 6 process specimens", "selection": "EXACT CANDIDATE; MACHINE CRIMP/QUALIFICATION OPEN", "procurement_released": "NO", "warning": WARNING},
        {"item": "LH-03", "quantity": 1, "manufacturer": "Belden", "order_code": "1852 BK005", "description": "28 AWG stranded tinned-copper black wire; 0.89 mm nominal OD", "selection": "EXACT CANDIDATE", "procurement_released": "NO", "warning": WARNING},
        {"item": "LH-04", "quantity": 1, "manufacturer": "Belden", "order_code": "1852 RD005", "description": "28 AWG stranded tinned-copper red wire; 0.89 mm nominal OD", "selection": "EXACT CANDIDATE", "procurement_released": "NO", "warning": WARNING},
        {"item": "LH-05", "quantity": 1, "manufacturer": "Belden", "order_code": "1852 YL005", "description": "28 AWG stranded tinned-copper yellow wire; 0.89 mm nominal OD", "selection": "EXACT CANDIDATE", "procurement_released": "NO", "warning": WARNING},
        {"item": "LH-06", "quantity": 1, "manufacturer": "Belden", "order_code": "1852 BL005", "description": "28 AWG stranded tinned-copper blue wire; 0.89 mm nominal OD", "selection": "EXACT CANDIDATE", "procurement_released": "NO", "warning": WARNING},
        {"item": "LH-07", "quantity": 1, "manufacturer": "Belden", "order_code": "1852 WH005", "description": "28 AWG stranded tinned-copper white wire; 0.89 mm nominal OD", "selection": "EXACT CANDIDATE", "procurement_released": "NO", "warning": WARNING},
        {"item": "LH-08", "quantity": 1, "manufacturer": "Belden", "order_code": "1852 OR005", "description": "28 AWG stranded tinned-copper orange wire; 0.89 mm nominal OD", "selection": "EXACT CANDIDATE", "procurement_released": "NO", "warning": WARNING},
        {"item": "LH-09", "quantity": 54, "manufacturer": "SELECTION REQUIRED", "order_code": "SELECTION REQUIRED", "description": "two-end durable wire-identification sleeves", "selection": "MATERIAL/PRINT/RETENTION OPEN", "procurement_released": "NO", "warning": WARNING},
        {"item": "LH-10", "quantity": 1, "manufacturer": "JST", "order_code": "AP-K2N + MKS-L-10-3 + APLMK SSHL002-02", "description": "manufacturer-listed machine/application tooling path", "selection": "CONTRACT-HARNESS PROCESS CANDIDATE; NO HAND TOOL RELEASED", "procurement_released": "NO", "warning": WARNING},
    ])

    write_csv(OUT / "logic-harness-process-traveler.csv", [
        {"step": "LH-A01", "operation": "verify exact source hashes and print contact map", "acceptance": "maps reproduce 15 A conductors and 12 B conductors; B positions 13-15 empty", "record": "NOT EXECUTED", "stop_rule": "STOP ON ANY MAP OR SOURCE DRIFT", "authority": AUTHORITY, "warning": WARNING},
        {"step": "LH-A02", "operation": "receive housings, contacts and Belden wire", "acceptance": "order code/lot/CoC inspection; conductor 28 AWG; insulation OD recorded within JST 0.76-1.0 mm range", "record": "NOT EXECUTED", "stop_rule": "QUARANTINE MISMATCH", "authority": AUTHORITY, "warning": WARNING},
        {"step": "LH-A03", "operation": "make six crimp-process specimens before harness work", "acceptance": "supplier-controlled machine setup; crimp cross-sections and pull data reviewed against released process specification", "record": "NOT EXECUTED", "stop_rule": "NO HARNESS CRIMP UNTIL PROCESS ACCEPTED", "authority": AUTHORITY, "warning": WARNING},
        {"step": "LH-A04", "operation": "cut and label 15 A wires and 12 B wires", "acceptance": "A 320 mm; B 310 mm; label at both ends; no nicks or thermal damage", "record": "NOT EXECUTED", "stop_rule": "SCRAP DAMAGED OR AMBIGUOUS WIRE", "authority": AUTHORITY, "warning": WARNING},
        {"step": "LH-A05", "operation": "machine-crimp both ends and inspect every crimp", "acceptance": "54 installed contacts; conductor/insulation wings correct; bellmouth/brush/locking lance per released vendor/JST process", "record": "NOT EXECUTED", "stop_rule": "NO REWORK BY SOLDERING; QUARANTINE DEFECT", "authority": AUTHORITY, "warning": WARNING},
        {"step": "LH-A06", "operation": "insert contacts by controlled map", "acceptance": "position-1 orientation witnessed; A positions 1-15 populated; B positions 1-12 populated and 13-15 visibly empty", "record": "NOT EXECUTED", "stop_rule": "EXTRACTED CONTACT NOT REUSED", "authority": AUTHORITY, "warning": WARNING},
        {"step": "LH-A07", "operation": "perform 100 percent de-energized continuity and isolation", "acceptance": "each end-to-end path matches net map; every nonmatching pair and empty B cavity is open", "record": "NOT EXECUTED", "stop_rule": "QUARANTINE ANY WRONG/INTERMITTENT PATH", "authority": AUTHORITY, "warning": WARNING},
        {"step": "LH-A08", "operation": "perform contact retention and label inspection", "acceptance": "each contact latched; labels legible at both ends; no housing damage", "record": "NOT EXECUTED", "stop_rule": "QUARANTINE ANY RETENTION OR ID FAILURE", "authority": AUTHORITY, "warning": WARNING},
        {"step": "LH-A09", "operation": "fit to unpowered received boards and fixture", "acceptance": "top-entry mating, adjacent slot routing, bend radius at least 10 mm, covers close, no pinch/chafe", "record": "NOT EXECUTED", "stop_rule": "NO FORCE-FIT OR FIELD-PORT ACCESS", "authority": AUTHORITY, "warning": WARNING},
        {"step": "LH-A10", "operation": "independent as-built inspection", "acceptance": "serialised harnesses match frozen maps and test records", "record": "NOT EXECUTED", "stop_rule": "NO CONNECTION/POWER AUTHORITY FROM THIS TRAVELER", "authority": AUTHORITY, "warning": WARNING},
    ])

    write_csv(OUT / "logic-harness-primary-source-register.csv", [
        {"source_id": "LH-S01", "manufacturer": "JST", "document": "GH connector product page/catalog", "revision_date": "live official page/catalog; accessed 2026-08-18", "url": "https://www.jst-mfg.com/product/index.php?lang=2&series=105", "verified": "GHR-15V-S; SSHL-002T-P0.2; 1 A at AWG26; contact range AWG30-26 / 0.05-0.13 mm2 / insulation OD 0.76-1.0 mm", "warning": WARNING},
        {"source_id": "LH-S02", "manufacturer": "JST", "document": "GH connector catalog", "revision_date": "current PDF accessed 2026-08-18; visible revision/date not stated", "url": "https://order.jst-mfg.com/InternetShop/app/pdf_show?kbn=1&key=GH.pdf", "verified": "15-position housing dimensions; AP-K2N/MKS-L-10-3/APLMK SSHL002-02 listed machine tooling", "warning": WARNING},
        {"source_id": "LH-S03", "manufacturer": "Belden", "document": "1852 product record", "revision_date": "Revision 0.119; 2026-06-30; accessed 2026-08-18", "url": "https://www.belden.com/products/cable/electronic-wire-cable/lead-wire-hook-up-wire/1852", "verified": "28 AWG 7x36 tinned copper; 0.89 mm nominal OD; exact 100 ft color order codes", "warning": WARNING},
    ])

    write_csv(OUT / "logic-harness-open-holds.csv", [
        {"hold_id": "LH-H01", "unresolved": "harnesses are unbuilt and all records are NOT EXECUTED", "closure": "serialised as-built traveler, photos, continuity/isolation and retention records", "state": "OPEN", "authority": AUTHORITY, "warning": WARNING},
        {"hold_id": "LH-H02", "unresolved": "no manual crimp tool is released; machine/contract-harness process is unqualified", "closure": "supplier process specification, exact machine setup, crimp-height/cross-section and pull acceptance with six specimens", "state": "OPEN", "authority": AUTHORITY, "warning": WARNING},
        {"hold_id": "LH-H03", "unresolved": "JST headline current is stated at AWG26, not the selected AWG28 wire", "closure": "measured rail currents/inrush, thermal test and qualified derating disposition before any power", "state": "OPEN", "authority": AUTHORITY, "warning": WARNING},
        {"hold_id": "LH-H04", "unresolved": "top-entry plug, adjacent slot and cover clearances are CAD candidates", "closure": "received-board/connector fit, bend, chafe, pinch and cover-closure inspection", "state": "OPEN", "authority": AUTHORITY, "warning": WARNING},
        {"hold_id": "LH-H05", "unresolved": "wire identification sleeve material and print process are unselected", "closure": "exact label material/order code plus abrasion/heat/legibility retention evidence", "state": "OPEN", "authority": AUTHORITY, "warning": WARNING},
        {"hold_id": "LH-H06", "unresolved": "logic harness package has no connection or powered-test authorization", "closure": "qualified review of exact boards, harnesses, supply/reference plan and separate stage authorization", "state": "OPEN", "authority": AUTHORITY, "warning": WARNING},
    ])

    source_bindings = [
        ("logic harness generator", Path(__file__)),
        ("motion controller terminal map", MCU_TERMINALS),
        ("carrier terminal map", CARRIER_TERMINALS),
        ("base E1 fixture STEP", BASE_FIXTURE_STEP),
    ]
    write_csv(OUT / "logic-harness-source-binding.csv", [
        {"role": role, "path": path.relative_to(ROOT).as_posix(), "sha256": sha(path), "state": "BOUND", "warning": WARNING}
        for role, path in source_bindings
    ])

    status = {
        "identifier": IDENTIFIER,
        "warning": WARNING,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "harness_assembly_count": 2,
        "connector_housing_count": 4,
        "connector_position_count": 60,
        "populated_conductor_count": 27,
        "installed_contact_count": 54,
        "empty_cavity_count": 6,
        "physical_wire_cad_count": geometry["physical_wire_count"],
        "native_pin_maps_match": True,
        "manufacturer_wire_contact_dimensional_candidate_match": True,
        "harness_built": False,
        "crimp_process_qualified": False,
        "received_fit_validated": False,
        "continuity_isolation_executed": False,
        "current_derating_validated": False,
        "connection_authority": False,
        "powered_test_authority": False,
        "motion_authority": False,
        "walking_authority": False,
        "energization_authority": False,
    }
    (OUT / "logic-harness-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n")


def write_svg(mapping: dict[str, list[dict]]) -> None:
    rows_svg = []
    y = 170
    for harness_id in ("E1-HA-A", "E1-HA-B"):
        rows_svg.append(f'<text class="h2" x="70" y="{y}">{harness_id}: straight-through numbered contacts</text>')
        y += 38
        for item in mapping[harness_id]:
            state = item["net"] if item["net"] != "EMPTY" else "EMPTY BOTH ENDS"
            rows_svg.append(f'<text x="95" y="{y}">P{item["position"]:02d}</text><line x1="170" y1="{y-6}" x2="760" y2="{y-6}"/><text x="790" y="{y}">{html.escape(state)}</text>')
            y += 29
        y += 35
    height = y + 90
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1500" height="{height}" viewBox="0 0 1500 {height}" role="img" aria-labelledby="title desc"><title id="title">HR-30 E1 logic harness construction map</title><desc id="desc">Two straight-through 15-position JST GH harnesses; carrier B positions 13 through 15 are empty.</desc><style>text{{font:600 18px system-ui;fill:#102b46}}.title{{font-size:38px;font-weight:900}}.h2{{font-size:25px;font-weight:900;fill:#0b4f91}}line{{stroke:#28a9df;stroke-width:5}}.warn{{fill:#fff0b5;stroke:#8d241f;stroke-width:4}}</style><rect width="1500" height="{height}" fill="#eef8fe"/><text class="title" x="55" y="58">HR-30 E1 controller-to-carrier logic harnesses</text><rect class="warn" x="55" y="82" width="1390" height="55"/><text x="75" y="118">UNBUILT CANDIDATES - VERIFY EVERY POSITION DE-ENERGIZED - NO CONNECTION OR POWER AUTHORITY</text>{''.join(rows_svg)}<text x="55" y="{height-35}">{html.escape(WARNING)}</text></svg>'''
    (OUT / "logic-harness-assembly-map.svg").write_text(svg, encoding="utf-8", newline="\n")


def write_docs(mapping: dict[str, list[dict]]) -> None:
    readme_section = f"""## Pin-for-pin E1 logic harness candidates

The fixture now includes two physical controller-to-carrier harness candidates rather than an undefined 15-circuit note. E1-HA-A populates all 15 positions; E1-HA-B populates positions 1-12 and deliberately leaves 13-15 empty at both ends. The package contains 27 individually modeled wires, four GHR-15V-S housing envelopes, exact straight-through net maps, 320/310 mm cut-length candidates, construction records, STEP/GLB exports and an integrated fixture-with-harness assembly.

Belden 1852 28 AWG stranded tinned-copper wire is the exact wire candidate because its published 0.89 mm nominal insulation diameter is inside JST's 0.76-1.0 mm SSHL-002T-P0.2 range. No hand crimp is released; the only manufacturer-listed route recorded here is the JST machine/applicator path, to be executed by a controlled harness supplier after process qualification. The harnesses remain unbuilt and cannot be connected or powered.
"""
    replace_marker(OUT / "README.md", "<!-- HR30-E1-LOGIC-HARNESS-P01-START -->", "<!-- HR30-E1-LOGIC-HARNESS-P01-END -->", readme_section)

    contact_rows = rows(OUT / "logic-harness-contact-map.csv")
    table = "".join(
        f"<tr><td>{html.escape(row['map_id'])}</td><td>{html.escape(row['net'])}</td><td>{html.escape(row['population'])}</td><td>{html.escape(row['wire_candidate'])}</td><td>{html.escape(row['cut_length_mm'])}</td></tr>"
        for row in contact_rows
    )
    section = f'''<section id="e1-logic-harness"><h2>The two logic links now exist as physical harness candidates</h2><div class="grid"><article><div class="metric">27</div><p>individually modeled, pin-bound conductors</p></article><article><div class="metric">54</div><p>candidate crimp contacts across four housings</p></article><article><div class="metric">6</div><p>carrier-B cavities deliberately empty</p></article><article class="hold"><div class="metric">0</div><p>built, inspected, or authorized harnesses</p></article></div><model-viewer src="HR30_E1_controls_fixture_with_logic_harness_candidate.glb" camera-controls shadow-intensity="0.8" exposure="1.05" alt="Interactive HR-30 E1 controls fixture with two pin-for-pin logic harness candidates"></model-viewer><p><a href="HR30_E1_controls_fixture_with_logic_harness_candidate.step">integrated fixture STEP</a> · <a href="HR30_E1_logic_harness_candidate.step">harness-only STEP</a> · <a href="logic-harness-assembly-map.svg">assembly map</a></p><div class="scroll"><table><thead><tr><th>Map</th><th>Net</th><th>Population</th><th>Wire</th><th>Cut length</th></tr></thead><tbody>{table}</tbody></table></div><div class="panel hold"><h3>What still blocks construction and connection</h3><p>The exact contact/wire dimensions are compatible candidates, but the crimp process, received connector fit, current derating, labels, continuity, isolation and retention have not been executed. There is no released hand crimp. These files do not authorize fabrication, connection, or power.</p><p><a href="logic-harness-process-traveler.csv">process traveler</a> · <a href="logic-harness-open-holds.csv">open holds</a> · <a href="logic-harness-primary-source-register.csv">primary sources</a></p></div></section>'''
    section = section.replace("\ufffd", "&middot;").replace("Â·", "&middot;")
    index_path = OUT / "index.html"
    index_text = index_path.read_text(encoding="utf-8")
    start = "<!-- HR30-E1-LOGIC-HARNESS-P01-START -->"
    end = "<!-- HR30-E1-LOGIC-HARNESS-P01-END -->"
    if start in index_text and end in index_text:
        before, tail = index_text.split(start, 1)
        _, after = tail.split(end, 1)
        index_text = before.rstrip() + after.lstrip()
    block = f"{start}\n{section}\n{end}\n"
    if "</main>" not in index_text:
        raise RuntimeError("E1 guide lost its main element")
    index_text = index_text.replace("</main>", block + "</main>", 1)
    index_path.write_text(index_text, encoding="utf-8", newline="\n")


def update_fixture_records() -> None:
    boundary_path = OUT / "connector-boundary-register.csv"
    data = rows(boundary_path)
    for row in data:
        if row["boundary"] == "JMCU_A":
            row["e1_state"] = "PIN-FOR-PIN CONSTRUCTION CANDIDATE DEFINED; UNBUILT"
            row["selection"] = "GHR-15V-S / SSHL-002T-P0.2 / BELDEN 1852; 15 OF 15 POPULATED"
        elif row["boundary"] == "JMCU_B":
            row["e1_state"] = "PIN-FOR-PIN CONSTRUCTION CANDIDATE DEFINED; UNBUILT"
            row["selection"] = "GHR-15V-S / SSHL-002T-P0.2 / BELDEN 1852; 12 OF 15 POPULATED; 13-15 EMPTY"
    write_csv(boundary_path, data)

    hold_path = OUT / "open-holds.csv"
    holds = rows(hold_path)
    for row in holds:
        if row["hold_id"] == "E1-H04":
            row["unresolved"] = "J1 and both now-defined pin-for-pin logic harness candidates remain unbuilt/uninspected"
            row["closure"] = "released supplier crimp process plus continuity, isolation, pull/retention, label and received-fit records"
    write_csv(hold_path, holds)

    status_path = OUT / "e1-fixture-status.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    status.update({
        "logic_harness_candidate_present": True,
        "logic_harness_assembly_count": 2,
        "logic_harness_populated_conductor_count": 27,
        "logic_harness_installed_contact_count": 54,
        "logic_harness_empty_cavity_count": 6,
        "wiring_built_or_inspected": False,
    })
    status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n")

    root_status_path = BODY / "package-status.json"
    root_status = json.loads(root_status_path.read_text(encoding="utf-8"))
    root_status.update({
        "e1_logic_harness_candidate_present": True,
        "e1_logic_harness_assembly_count": 2,
        "e1_logic_harness_populated_conductor_count": 27,
        "e1_logic_harness_installed_contact_count": 54,
        "e1_logic_harness_built": False,
        "e1_logic_harness_validated": False,
    })
    root_status_path.write_text(json.dumps(root_status, indent=2) + "\n", encoding="utf-8", newline="\n")

    root_section = """## E1 pin-for-pin logic harnesses

The E1 controls fixture now includes two placed controller-to-carrier harness candidates with 27 individually modeled conductors and four 15-position JST GH housing envelopes. Carrier A populates all 15 contacts. Carrier B populates contacts 1-12 and leaves 13-15 empty at both ends, matching the native ECAD instead of inventing three wires. Exact straight-through net maps, 320/310 mm cut-length candidates, STEP/GLB exports and a controlled construction traveler are included. The crimp process, received fit, current derating and every physical test remain open; no connection or powered-test authority follows.
"""
    replace_marker(BODY / "README.md", "<!-- HR30-E1-LOGIC-HARNESS-P01-START -->", "<!-- HR30-E1-LOGIC-HARNESS-P01-END -->", root_section)


def generate_into_fixture() -> dict:
    if not BASE_FIXTURE_STEP.is_file():
        raise RuntimeError("base E1 fixture must be generated first")
    mapping = terminal_map()
    geometry = write_cad(mapping)
    write_registers(mapping, geometry)
    write_svg(mapping)
    write_docs(mapping)
    update_fixture_records()
    shutil.copy2(__file__, OUT / "e1-logic-harness-source.py")
    return geometry


def main() -> int:
    result = generate_into_fixture()
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
