#!/usr/bin/env python3
"""Generate the physical E1 J1 logic-power cable candidate.

The cable is a two-conductor, 1000 mm cut-length candidate from the controller
J1 VH connector to two 4 mm bench-supply plugs.  Geometry is project-owned and
dimensioned from public manufacturer drawings; it is not redistributed vendor
CAD.  This package never grants fabrication, connection, or power authority.
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
OUT = BODY / "electrical/e1-controls-only-fixture-p0.1"
LOGIC = BODY / "electrical/logic-power-kit-p0.1"
IDENTIFIER = "HR30-E1-J1-LOGIC-POWER-CABLE-P0.1"
WARNING = (
    "PRELIMINARY - UNBUILT J1 LOGIC-POWER CABLE CANDIDATE - NOT APPROVED FOR "
    "CONNECTION, POWERED TESTING, MOTION, WALKING, OR ENERGIZATION"
)
AUTHORITY = "NO CONNECTION, POWERED-TEST, MOTION, WALKING OR ENERGIZATION AUTHORITY"

BASE_INTEGRATED_STEP = OUT / "HR30_E1_controls_fixture_with_logic_harness_candidate.step"
WIRE_OD_MM = 1.575
CUT_LENGTH_MM = 1000.0
J1_PANEL_X_MM = -128.2
J1_PANEL_Y_MM = 0.0
J1_MATED_CENTER_Z_MM = 25.0


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


def path_length(points: list[tuple[float, float, float]]) -> float:
    return sum(math.dist(a, b) for a, b in zip(points, points[1:]))


def segment(a: tuple[float, float, float], b: tuple[float, float, float], radius: float) -> cq.Shape:
    direction = cq.Vector(b[0] - a[0], b[1] - a[1], b[2] - a[2])
    if direction.Length <= 1e-9:
        raise RuntimeError("zero-length power-cable segment")
    return cq.Solid.makeCylinder(radius, direction.Length, cq.Vector(*a), direction.normalized())


def physical_wire(points: list[tuple[float, float, float]], radius: float) -> cq.Shape:
    shapes: list[cq.Shape] = [segment(a, b, radius) for a, b in zip(points, points[1:])]
    shapes.extend(cq.Solid.makeSphere(radius, cq.Vector(*point)) for point in points[1:-1])
    return cq.Compound.makeCompound(shapes)


def cylinder_x(x: float, y: float, z: float, radius: float, length: float, direction: int = 1) -> cq.Shape:
    return cq.Solid.makeCylinder(radius, length, cq.Vector(x, y, z), cq.Vector(direction, 0, 0))


def j1_housing(center: tuple[float, float, float]) -> cq.Shape:
    # Project-owned envelope based on JST VH public catalog dimensions for
    # VHR-2N (7.86 x 10.5 x 10.6 mm).  It is deliberately not manufacturer CAD.
    return cq.Workplane("XY").box(10.5, 7.86, 10.6).translate(center).val()


def banana_plug(tip: tuple[float, float, float]) -> cq.Compound:
    # Project-owned envelope from Pomona D5934 dimensions.  The conductor-side
    # body is shown as 19.05 mm long and the mating pin as a 4 mm cylinder.
    x, y, z = tip
    metal = cylinder_x(x - 17.0, y, z, 2.0, 17.0, 1)
    body = cylinder_x(x - 36.05, y, z, 4.0, 19.05, 1)
    return cq.Compound.makeCompound([metal, body])


def integrated_route(y_offset: float) -> list[tuple[float, float, float]]:
    # A physical stowed service-loop candidate with a mathematically exact
    # 1000 mm centerline.  The final segment is solved from the preceding sum.
    y0 = J1_PANEL_Y_MM + y_offset
    base = [
        (J1_PANEL_X_MM, y0, J1_MATED_CENTER_Z_MM),
        (-150.0, y0, J1_MATED_CENTER_Z_MM),
        (-150.0, 100.0 + y_offset, J1_MATED_CENTER_Z_MM),
        (-320.0, 100.0 + y_offset, J1_MATED_CENTER_Z_MM),
        (-320.0, 50.0 + y_offset, J1_MATED_CENTER_Z_MM),
        (-150.0, 50.0 + y_offset, J1_MATED_CENTER_Z_MM),
        (-150.0, -50.0 + y_offset, J1_MATED_CENTER_Z_MM),
        (-320.0, -50.0 + y_offset, J1_MATED_CENTER_Z_MM),
        (-320.0, -100.0 + y_offset, J1_MATED_CENTER_Z_MM),
    ]
    remainder = CUT_LENGTH_MM - path_length(base)
    if remainder <= 0:
        raise RuntimeError("service-loop path exceeds cut length")
    base.append((-320.0 - remainder, -100.0 + y_offset, J1_MATED_CENTER_Z_MM))
    if abs(path_length(base) - CUT_LENGTH_MM) > 1e-6:
        raise RuntimeError("service-loop length solution failed")
    return base


def write_cad() -> dict:
    red = (0.78, 0.05, 0.04)
    black = (0.035, 0.045, 0.06)
    housing_color = (0.94, 0.94, 0.90)
    radius = WIRE_OD_MM / 2

    # Straight manufacturing view: exact 1000 mm wire centerlines.
    manufacturing = cq.Assembly(name="HR30_E1_J1_LOGIC_POWER_CABLE_P01_NOT_RELEASED")
    mfg_shapes: list[cq.Shape] = []
    housing = j1_housing((0.0, 0.0, 0.0))
    manufacturing.add(housing, name="JST_VHR_2N_PROJECT_ENVELOPE", color=cq.Color(*housing_color, 0.75))
    mfg_shapes.append(housing)
    for name, y, color in (("J1_2_AUX_5V_SAFE", 1.98, red), ("J1_1_CTRL_GND", -1.98, black)):
        wire = physical_wire([(5.25, y, 0.0), (1005.25, y, 0.0)], radius)
        plug = banana_plug((1041.30, y, 0.0))
        manufacturing.add(wire, name=f"WIRE_{name}_1000MM", color=cq.Color(*color, 1))
        manufacturing.add(plug, name=f"POMONA_5934_{name}_PROJECT_ENVELOPE", color=cq.Color(*color, 1))
        mfg_shapes.extend([wire, plug])
    mfg_compound = cq.Compound.makeCompound(mfg_shapes)
    step = OUT / "HR30_E1_J1_logic_power_cable_candidate.step"
    cq.exporters.export(mfg_compound, str(step))
    clean_step(step)
    manufacturing.save(str(OUT / "HR30_E1_J1_logic_power_cable_candidate.glb"), tolerance=0.12, angularTolerance=0.10)

    # Integrated view: the same 1000 mm centerline stowed beside the panel.
    routed = cq.Assembly(name="HR30_E1_COMPLETE_LOGIC_WIRING_P01_NOT_RELEASED")
    routed_shapes: list[cq.Shape] = []
    placed_housing = j1_housing((J1_PANEL_X_MM, J1_PANEL_Y_MM, J1_MATED_CENTER_Z_MM))
    routed.add(placed_housing, name="J1_VHR_2N_PROJECT_ENVELOPE", color=cq.Color(*housing_color, 0.75))
    routed_shapes.append(placed_housing)
    route_lengths = {}
    for name, y, color in (("J1_2_AUX_5V_SAFE", 1.98, red), ("J1_1_CTRL_GND", -1.98, black)):
        points = integrated_route(y)
        wire = physical_wire(points, radius)
        end = points[-1]
        plug = banana_plug((end[0] - 36.05, end[1], end[2]))
        routed.add(wire, name=f"ROUTED_{name}", color=cq.Color(*color, 1))
        routed.add(plug, name=f"SOURCE_PLUG_{name}", color=cq.Color(*color, 1))
        routed_shapes.extend([wire, plug])
        route_lengths[name] = path_length(points)
    routed_compound = cq.Compound.makeCompound(routed_shapes)
    routed_step = OUT / "HR30_E1_J1_logic_power_cable_placed_candidate.step"
    cq.exporters.export(routed_compound, str(routed_step))
    clean_step(routed_step)
    routed.save(str(OUT / "HR30_E1_J1_logic_power_cable_placed_candidate.glb"), tolerance=0.14, angularTolerance=0.11)

    fixture = cq.importers.importStep(str(BASE_INTEGRATED_STEP)).val()
    complete = cq.Compound.makeCompound([fixture, routed_compound])
    complete_step = OUT / "HR30_E1_controls_fixture_complete_logic_wiring_candidate.step"
    cq.exporters.export(complete, str(complete_step))
    clean_step(complete_step)
    complete_assembly = cq.Assembly(name="HR30_E1_COMPLETE_LOGIC_WIRING_P01_NOT_RELEASED")
    complete_assembly.add(fixture, name="E1_FIXTURE_AND_CARRIER_HARNESSES", color=cq.Color(0.62, 0.68, 0.72, 0.86))
    complete_assembly.add(routed_compound, name="J1_LOGIC_POWER_CABLE", color=cq.Color(0.10, 0.42, 0.82, 1))
    complete_assembly.save(
        str(OUT / "HR30_E1_controls_fixture_complete_logic_wiring_candidate.glb"),
        tolerance=0.16,
        angularTolerance=0.12,
    )
    bounds = complete.BoundingBox()
    return {
        "manufacturing_centerline_mm_each": CUT_LENGTH_MM,
        "placed_centerline_mm": route_lengths,
        "complete_extent_mm": [round(bounds.xlen, 6), round(bounds.ylen, 6), round(bounds.zlen, 6)],
    }


def write_registers(geometry: dict) -> None:
    write_csv(OUT / "j1-power-cable-assembly-register.csv", [{
        "assembly_id": "E1-J1-PWR-01", "from": "SIGLENT SPD3303X CH1 +/-",
        "to": "MOTION_CONTROLLER:J1", "conductor_count": 2,
        "wire_cut_length_mm_each": "1000.000", "wire_od_mm_nominal": f"{WIRE_OD_MM:.3f}",
        "controller_housing": "JST VHR-2N", "controller_contacts": "2 x JST SVH-21T-P1.1",
        "source_connectors": "Pomona 5934-2 RED; 5934-0 BLACK",
        "cad_basis": "PROJECT-OWNED DIMENSIONAL ENVELOPES; NOT MANUFACTURER CAD",
        "built": "NO", "authority": AUTHORITY, "warning": WARNING,
    }])
    write_csv(OUT / "j1-power-cable-contact-map.csv", [
        {"map_id": "J1P-C01", "source_terminal": "SPD3303X CH1 +", "source_connector": "Pomona 5934-2", "wire": "Alpha Wire 3051 RD005", "color": "RED", "destination": "J1.2", "net": "AUX_5V_SAFE", "polarity": "POSITIVE", "cut_length_mm": "1000.000", "continuity": "NOT EXECUTED", "isolation": "NOT EXECUTED", "authority": AUTHORITY, "warning": WARNING},
        {"map_id": "J1P-C02", "source_terminal": "SPD3303X CH1 -", "source_connector": "Pomona 5934-0", "wire": "Alpha Wire 3051 BK005", "color": "BLACK", "destination": "J1.1", "net": "CTRL_GND", "polarity": "RETURN", "cut_length_mm": "1000.000", "continuity": "NOT EXECUTED", "isolation": "NOT EXECUTED", "authority": AUTHORITY, "warning": WARNING},
    ])
    write_csv(OUT / "j1-power-cable-route-register.csv", [
        {"route_id": "J1P-R01", "conductor": "J1.2 AUX_5V_SAFE", "native_j1_panel_xyz_mm": f"{J1_PANEL_X_MM:.3f},{J1_PANEL_Y_MM + 1.98:.3f},{J1_MATED_CENTER_Z_MM:.3f}", "cad_centerline_mm": f"{geometry['placed_centerline_mm']['J1_2_AUX_5V_SAFE']:.3f}", "minimum_static_bend_radius_mm": "15.750 CANDIDATE (10 x NOMINAL OD)", "retention": "SELECTION REQUIRED", "route_validation": "NOT EXECUTED", "authority": AUTHORITY, "warning": WARNING},
        {"route_id": "J1P-R02", "conductor": "J1.1 CTRL_GND", "native_j1_panel_xyz_mm": f"{J1_PANEL_X_MM:.3f},{J1_PANEL_Y_MM - 1.98:.3f},{J1_MATED_CENTER_Z_MM:.3f}", "cad_centerline_mm": f"{geometry['placed_centerline_mm']['J1_1_CTRL_GND']:.3f}", "minimum_static_bend_radius_mm": "15.750 CANDIDATE (10 x NOMINAL OD)", "retention": "SELECTION REQUIRED", "route_validation": "NOT EXECUTED", "authority": AUTHORITY, "warning": WARNING},
    ])
    write_csv(OUT / "j1-power-cable-bom.csv", [
        {"item": "J1P-01", "quantity": 1, "manufacturer": "JST", "order_code": "VHR-2N", "description": "2-position VH receptacle housing", "selection": "EXACT CANDIDATE; RECEIVED FIT OPEN", "procurement_released": "NO", "warning": WARNING},
        {"item": "J1P-02", "quantity": 8, "manufacturer": "JST", "order_code": "SVH-21T-P1.1", "description": "two installed contacts plus six process specimens", "selection": "MACHINE CRIMP PROCESS CANDIDATE; NO HAND CRIMP RELEASED", "procurement_released": "NO", "warning": WARNING},
        {"item": "J1P-03", "quantity": 1, "manufacturer": "Alpha Wire", "order_code": "3051 RD005", "description": "22 AWG red hook-up wire; 1000 mm cut", "selection": "EXACT CANDIDATE", "procurement_released": "NO", "warning": WARNING},
        {"item": "J1P-04", "quantity": 1, "manufacturer": "Alpha Wire", "order_code": "3051 BK005", "description": "22 AWG black hook-up wire; 1000 mm cut", "selection": "EXACT CANDIDATE", "procurement_released": "NO", "warning": WARNING},
        {"item": "J1P-05", "quantity": 1, "manufacturer": "Pomona Electronics", "order_code": "5934-2", "description": "red 4 mm solderless set-screw plug", "selection": "EXACT CANDIDATE; SET-SCREW PROCESS OPEN", "procurement_released": "NO", "warning": WARNING},
        {"item": "J1P-06", "quantity": 1, "manufacturer": "Pomona Electronics", "order_code": "5934-0", "description": "black 4 mm solderless set-screw plug", "selection": "EXACT CANDIDATE; SET-SCREW PROCESS OPEN", "procurement_released": "NO", "warning": WARNING},
        {"item": "J1P-07", "quantity": 1, "manufacturer": "Alpha Wire", "order_code": "FIT-KIT-221BK", "description": "black 2:1 heat-shrink kit containing FIT-221-1/4", "selection": "EXACT MATERIAL CANDIDATE; CUT LENGTH/PROCESS OPEN", "procurement_released": "NO", "warning": WARNING},
        {"item": "J1P-08", "quantity": 4, "manufacturer": "Brady", "order_code": "M21-11-427", "description": "0.75 x 0.5 in B-427 self-laminating wire labels", "selection": "EXACT MATERIAL CANDIDATE; PRINT/PLACEMENT/RETENTION OPEN", "procurement_released": "NO", "warning": WARNING},
        {"item": "J1P-09", "quantity": 1, "manufacturer": "JST", "order_code": "AP-K2N + MKS-L + APLMK SVH21-11", "description": "manufacturer-listed machine/applicator path", "selection": "CONTRACT-HARNESS PROCESS CANDIDATE; NO HAND TOOL RELEASED", "procurement_released": "NO", "warning": WARNING},
    ])
    write_csv(OUT / "j1-power-cable-process-traveler.csv", [
        {"step": "J1P-A01", "operation": "receive and inspect exact parts", "acceptance": "order code/lot/CoC, wire OD, housing/contact/plug identity recorded", "record": "NOT EXECUTED", "stop_rule": "QUARANTINE ANY MISMATCH", "authority": AUTHORITY, "warning": WARNING},
        {"step": "J1P-A02", "operation": "make six crimp-process specimens", "acceptance": "supplier-controlled machine setup; crimp cross-section and pull evidence accepted", "record": "NOT EXECUTED", "stop_rule": "NO HARNESS CRIMP UNTIL PROCESS ACCEPTED", "authority": AUTHORITY, "warning": WARNING},
        {"step": "J1P-A03", "operation": "cut two Alpha 3051 wires", "acceptance": "1000 mm each before termination; no insulation damage", "record": "NOT EXECUTED", "stop_rule": "SCRAP DAMAGED OR OUT-OF-TOLERANCE WIRE", "authority": AUTHORITY, "warning": WARNING},
        {"step": "J1P-A04", "operation": "apply exact candidate heat shrink and labels", "acceptance": "red J1.2/+5V and black J1.1/0V remain legible at both ends; shrink process released", "record": "NOT EXECUTED", "stop_rule": "STOP ON AMBIGUOUS POLARITY OR HEAT DAMAGE", "authority": AUTHORITY, "warning": WARNING},
        {"step": "J1P-A05", "operation": "machine-crimp JST contacts and insert by map", "acceptance": "J1.1 black return; J1.2 red positive; locking lances retained", "record": "NOT EXECUTED", "stop_rule": "NO SOLDER REPAIR; QUARANTINE DEFECT", "authority": AUTHORITY, "warning": WARNING},
        {"step": "J1P-A06", "operation": "assemble Pomona set-screw plugs", "acceptance": "strip length and set-screw torque released; no exposed strand; red/black identity retained", "record": "NOT EXECUTED", "stop_rule": "NO INVENTED TORQUE OR STRIP LENGTH", "authority": AUTHORITY, "warning": WARNING},
        {"step": "J1P-A07", "operation": "de-energized continuity/isolation/polarity test", "acceptance": "CH1+ to J1.2 only; CH1- to J1.1 only; no cross-short; values meet released limits", "record": "NOT EXECUTED", "stop_rule": "QUARANTINE ANY WRONG OR INTERMITTENT PATH", "authority": AUTHORITY, "warning": WARNING},
        {"step": "J1P-A08", "operation": "pull/retention and received-fit inspection", "acceptance": "contacts, plugs, labels, sleeving and J1 mate remain secure; route has no pinch/chafe", "record": "NOT EXECUTED", "stop_rule": "NO FORCE-FIT OR FIELD REWORK", "authority": AUTHORITY, "warning": WARNING},
        {"step": "J1P-A09", "operation": "independent as-built inspection", "acceptance": "serialized cable matches CAD/map/BOM and all records", "record": "NOT EXECUTED", "stop_rule": "TRAVELER DOES NOT GRANT CONNECTION OR POWER AUTHORITY", "authority": AUTHORITY, "warning": WARNING},
    ])
    write_csv(OUT / "j1-power-cable-primary-source-register.csv", [
        {"source_id": "J1P-S01", "manufacturer": "JST", "document": "VH product page and eVH catalog", "revision_date": "official live page/catalog accessed 2026-08-18; visible revision not stated", "url": "https://www.jst-mfg.com/product/index.php?lang=2&series=262", "verified": "VHR-2N/SVH-21T-P1.1 identity, pitch, wire/contact range and housing dimensions; no application current released", "warning": WARNING},
        {"source_id": "J1P-S02", "manufacturer": "Alpha Wire", "document": "3051 product specification", "revision_date": "official live PDF accessed 2026-08-18; revision not stated", "url": "https://www.alphawire.com/disteAPI/SpecPDF/DownloadProductSpecPdf?productPartNumber=3051", "verified": "22 AWG 7/30 tinned copper; 1.575 +/-0.051 mm OD; -40 to 105 C; 10 x diameter bend-radius guidance", "warning": WARNING},
        {"source_id": "J1P-S03", "manufacturer": "Pomona Electronics", "document": "5934 drawing D5934_101", "revision_date": "Rev 101; 2007-10-01; accessed 2026-08-18", "url": "https://www.pomonaelectronics.com/sites/default/files/d5934_101.pdf", "verified": "5934-0 black/5934-2 red; solderless internal set screw; AWG18-22; 4 mm plug interface", "warning": WARNING},
        {"source_id": "J1P-S04", "manufacturer": "Alpha Wire", "document": "FIT-KIT-221BK product specification", "revision_date": "official live PDF accessed 2026-08-18; revision not stated", "url": "https://www.alphawire.com/disteAPI/SpecPDF/DownloadProductSpecPdf?productPartNumber=FIT-KIT-221BK", "verified": "kit contains black FIT-221-1/4; 2:1 cross-linked polyolefin; 6.35 mm supplied / 3.175 mm recovered ID", "warning": WARNING},
        {"source_id": "J1P-S05", "manufacturer": "Brady", "document": "M21-11-427 product page", "revision_date": "official live page accessed 2026-08-18; revision not stated", "url": "https://www.bradyid.com/wire-cable-labels/self-laminating-vinyl-wrap-around-labels-ribbon-pre-sized-for-m210-m211-printers-cps-4293071?part-number=m21-11-427", "verified": "0.75 x 0.5 in B-427 self-laminating label; wire diameter range 0.06-0.199 in", "warning": WARNING},
    ])
    write_csv(OUT / "j1-power-cable-source-binding.csv", [
        {"role": "J1 power cable generator", "path": Path(__file__).relative_to(ROOT).as_posix(), "sha256": sha(Path(__file__)), "state": "BOUND", "warning": WARNING},
        {"role": "logic-power connector map", "path": (LOGIC / "connector-contact-map.csv").relative_to(ROOT).as_posix(), "sha256": sha(LOGIC / "connector-contact-map.csv"), "state": "BOUND", "warning": WARNING},
        {"role": "motion controller PCB", "path": (BODY / "electrical/motion-controller-p0.1/board/hr30-motion-controller-p0.1.kicad_pcb").relative_to(ROOT).as_posix(), "sha256": sha(BODY / "electrical/motion-controller-p0.1/board/hr30-motion-controller-p0.1.kicad_pcb"), "state": "BOUND", "warning": WARNING},
        {"role": "E1 fixture with carrier harnesses", "path": BASE_INTEGRATED_STEP.relative_to(ROOT).as_posix(), "sha256": sha(BASE_INTEGRATED_STEP), "state": "BOUND", "warning": WARNING},
    ])
    write_csv(OUT / "j1-power-cable-open-holds.csv", [
        {"hold_id": "J1P-H01", "unresolved": "cable is unbuilt and all received parts are uninspected", "closure": "received-order/lot/CoC and dimensional inspection", "state": "OPEN", "authority": AUTHORITY, "warning": WARNING},
        {"hold_id": "J1P-H02", "unresolved": "JST crimp process is unqualified; no hand crimp released", "closure": "controlled supplier machine setup, cross-section and pull data", "state": "OPEN", "authority": AUTHORITY, "warning": WARNING},
        {"hold_id": "J1P-H03", "unresolved": "Pomona strip length and set-screw torque are unreleased", "closure": "manufacturer/supplier assembly process and retention evidence", "state": "OPEN", "authority": AUTHORITY, "warning": WARNING},
        {"hold_id": "J1P-H04", "unresolved": "heat-shrink cut lengths/process and label content/placement are unvalidated", "closure": "released drawing/process plus legibility and retention inspection", "state": "OPEN", "authority": AUTHORITY, "warning": WARNING},
        {"hold_id": "J1P-H05", "unresolved": "current/thermal derating and fault protection are open", "closure": "received-load, inrush, conductor/contact/plug limits and fault analysis", "state": "OPEN", "authority": AUTHORITY, "warning": WARNING},
        {"hold_id": "J1P-H06", "unresolved": "continuity, isolation, polarity, pull, fit and route tests are unexecuted", "closure": "completed traveler and calibrated measurement records", "state": "OPEN", "authority": AUTHORITY, "warning": WARNING},
        {"hold_id": "J1P-H07", "unresolved": "voltage/current/OCP setpoints and DC-reference plan remain unreleased", "closure": "qualified electrical review of received controller/supply/instruments", "state": "OPEN", "authority": AUTHORITY, "warning": WARNING},
        {"hold_id": "J1P-H08", "unresolved": "connection and powered-test authority are absent", "closure": "separate signed release for exact serialized configuration", "state": "OPEN", "authority": AUTHORITY, "warning": WARNING},
    ])
    status = {
        "identifier": IDENTIFIER, "warning": WARNING,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "cable_assembly_count": 1, "conductor_count": 2,
        "wire_cut_length_mm_each": CUT_LENGTH_MM,
        "native_j1_reference": "J1 B2P-VH-B",
        "native_j1_panel_xyz_mm": [J1_PANEL_X_MM, J1_PANEL_Y_MM, J1_MATED_CENTER_Z_MM],
        "project_owned_dimensional_envelopes_only": True,
        "manufacturer_cad_redistributed": False,
        "exact_candidate_housing_contacts_wire_plugs_selected": True,
        "exact_candidate_sleeve_and_label_material_selected": True,
        "cable_built": False, "crimp_process_qualified": False,
        "set_screw_process_released": False, "received_fit_validated": False,
        "continuity_isolation_polarity_executed": False,
        "current_thermal_derating_validated": False,
        "supply_limits_released": False, "dc_reference_approved": False,
        "connection_authority": False, "powered_test_authority": False,
        "motion_authority": False, "walking_authority": False,
        "energization_authority": False,
    }
    (OUT / "j1-power-cable-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n")


def write_svg() -> None:
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="700" viewBox="0 0 1400 700" role="img" aria-labelledby="title desc"><title id="title">HR-30 E1 J1 logic-power cable assembly map</title><desc id="desc">Two 1000 mm Alpha Wire conductors connect red and black Pomona plugs to controller J1 contacts 2 and 1.</desc><style>text{{font:600 18px system-ui;fill:#102b46}}.title{{font-size:36px;font-weight:900}}.sub{{font-size:22px;font-weight:800}}.small{{font-size:16px}}.box{{fill:#fff;stroke:#0b4f91;stroke-width:4}}.warn{{fill:#fff0b5;stroke:#8d241f;stroke-width:4}}.red{{stroke:#b32025;stroke-width:10;fill:none}}.black{{stroke:#17243a;stroke-width:10;fill:none}}</style><rect width="1400" height="700" fill="#eef8fe"/><text class="title" x="55" y="58">HR-30 E1 J1 logic-power cable candidate</text><rect class="warn" x="55" y="85" width="1290" height="65" rx="14"/><text x="80" y="125">UNBUILT / UNPOWERED - VERIFY POLARITY DE-ENERGIZED - NO CONNECTION OR POWER AUTHORITY</text><rect class="box" x="70" y="230" width="245" height="230" rx="18"/><text class="sub" x="105" y="280">Bench supply</text><text x="105" y="325">SPD3303X CH1 +</text><text x="105" y="400">SPD3303X CH1 -</text><path class="red" d="M315 320 H930"/><path class="black" d="M315 395 H930"/><text class="small" x="410" y="300">5934-2 / 3051 RD005 / 1000 mm / RED</text><text class="small" x="410" y="430">5934-0 / 3051 BK005 / 1000 mm / BLACK</text><rect class="box" x="930" y="235" width="360" height="220" rx="18"/><text class="sub" x="965" y="280">Controller J1 / VHR-2N</text><text x="965" y="325">J1.2 AUX_5V_SAFE (red)</text><text x="965" y="400">J1.1 CTRL_GND (black)</text><text class="small" x="70" y="535">Project-owned dimensional connector/plug envelopes; not manufacturer CAD.</text><text class="small" x="70" y="570">FIT-KIT-221BK sleeve and M21-11-427 labels are exact material candidates; process remains open.</text><text class="small" x="70" y="635">{html.escape(WARNING)}</text></svg>'''
    (OUT / "j1-power-cable-assembly-map.svg").write_text(svg, encoding="utf-8", newline="\n")


def write_docs() -> None:
    readme = """## J1 logic-power cable candidate

The native motion-controller J1 boundary now has a physical cable assembly candidate: two 1000 mm Alpha Wire 3051 conductors, a JST VHR-2N housing with SVH-21T-P1.1 contacts, red/black Pomona 5934 source plugs, FIT-KIT-221BK sleeving and Brady M21-11-427 labels. J1.2 is red `AUX_5V_SAFE`; J1.1 is black `CTRL_GND`. The connector and plug shapes are project-owned dimensional envelopes from public drawings, not redistributed manufacturer CAD.

Manufacturing and placed STEP/GLB files, a native-J1 route, contact map, BOM and nine-step traveler are included. Crimping, set-screw assembly, sleeving, labels, received fit, derating, tests, supply limits, grounding and every authority remain open. No hand crimp is released.
"""
    replace_marker(OUT / "README.md", "<!-- HR30-E1-J1-POWER-CABLE-P01-START -->", "<!-- HR30-E1-J1-POWER-CABLE-P01-END -->", readme)
    table = "".join(
        f"<tr><td>{html.escape(row['map_id'])}</td><td>{html.escape(row['source_terminal'])}</td><td>{html.escape(row['wire'])}</td><td>{html.escape(row['destination'])}</td><td>{html.escape(row['net'])}</td><td>{html.escape(row['cut_length_mm'])}</td></tr>"
        for row in rows(OUT / "j1-power-cable-contact-map.csv")
    )
    section = f'''<section id="e1-j1-power-cable"><h2>J1 now has a physical two-wire power-cable candidate</h2><div class="grid"><article><div class="metric">2</div><p>polarity-bound 22 AWG conductors</p></article><article><div class="metric">1,000 mm</div><p>cut length for each conductor</p></article><article><div class="metric">J1.2 / J1.1</div><p>native controller contacts</p></article><article class="hold"><div class="metric">0</div><p>built, connected, or powered cables</p></article></div><model-viewer src="HR30_E1_controls_fixture_complete_logic_wiring_candidate.glb" camera-controls shadow-intensity="0.8" exposure="1.05" alt="Interactive HR-30 E1 controls fixture with controller-to-carrier harnesses and the two-conductor J1 logic-power cable candidate"></model-viewer><p><a href="HR30_E1_controls_fixture_complete_logic_wiring_candidate.step">complete fixture STEP</a> &middot; <a href="HR30_E1_J1_logic_power_cable_candidate.step">manufacturing cable STEP</a> &middot; <a href="j1-power-cable-assembly-map.svg">assembly map</a></p><div class="scroll"><table><thead><tr><th>Map</th><th>Supply</th><th>Wire</th><th>J1 contact</th><th>Net</th><th>Cut length</th></tr></thead><tbody>{table}</tbody></table></div><div class="panel hold"><h3>Construction is still blocked</h3><p>The CAD fixes identity, polarity, cut length and the native J1 location. It does not release the JST crimp, Pomona set-screw torque, sleeve/label process, current/thermal limits, continuity/isolation/pull tests, voltage/current/OCP settings, grounding, connection, or power.</p><p><a href="j1-power-cable-process-traveler.csv">process traveler</a> &middot; <a href="j1-power-cable-open-holds.csv">open holds</a> &middot; <a href="j1-power-cable-primary-source-register.csv">primary sources</a></p></div></section>'''
    index = OUT / "index.html"
    text = index.read_text(encoding="utf-8")
    start, end = "<!-- HR30-E1-J1-POWER-CABLE-P01-START -->", "<!-- HR30-E1-J1-POWER-CABLE-P01-END -->"
    if start in text and end in text:
        before, tail = text.split(start, 1)
        _, after = tail.split(end, 1)
        text = before.rstrip() + after.lstrip()
    if "</main>" not in text:
        raise RuntimeError("E1 guide lost its main element")
    text = text.replace("</main>", f"{start}\n{section}\n{end}\n</main>", 1)
    index.write_text(text, encoding="utf-8", newline="\n")


def update_status_and_root() -> None:
    boundary_path = OUT / "connector-boundary-register.csv"
    data = rows(boundary_path)
    for row in data:
        if row["boundary"] == "J1":
            row["e1_state"] = "PHYSICAL TWO-WIRE CANDIDATE DEFINED; UNBUILT / UNCONNECTED / UNPOWERED"
            row["selection"] = "VHR-2N / SVH-21T-P1.1 / ALPHA 3051 / POMONA 5934; PROCESS AND TESTS OPEN"
    write_csv(boundary_path, data)
    holds_path = OUT / "open-holds.csv"
    holds = rows(holds_path)
    for row in holds:
        if row["hold_id"] == "E1-H04":
            row["unresolved"] = "the defined J1 cable and both pin-for-pin logic harness candidates remain unbuilt/uninspected"
            row["closure"] = "released supplier assembly processes plus continuity, isolation, polarity, pull/retention, labels and received-fit records"
    write_csv(holds_path, holds)
    status_path = OUT / "e1-fixture-status.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    status.update({
        "j1_logic_power_cable_candidate_present": True,
        "j1_logic_power_conductor_count": 2,
        "j1_logic_power_wire_cut_length_mm_each": CUT_LENGTH_MM,
        "j1_logic_power_cable_built": False,
        "j1_logic_power_cable_validated": False,
    })
    status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n")
    root_status_path = BODY / "package-status.json"
    root_status = json.loads(root_status_path.read_text(encoding="utf-8"))
    root_status.update({
        "e1_j1_logic_power_cable_candidate_present": True,
        "e1_j1_logic_power_conductor_count": 2,
        "e1_j1_logic_power_wire_cut_length_mm_each": CUT_LENGTH_MM,
        "e1_j1_logic_power_cable_built": False,
        "e1_j1_logic_power_cable_validated": False,
    })
    root_status_path.write_text(json.dumps(root_status, indent=2) + "\n", encoding="utf-8", newline="\n")
    root_readme = """## E1 J1 logic-power cable

The E1 fixture now includes the physical two-conductor J1 cable candidate alongside the controller-to-carrier harnesses. Two 1000 mm Alpha Wire 3051 conductors are bound to native contacts J1.2 `AUX_5V_SAFE` (red) and J1.1 `CTRL_GND` (black), with exact JST, Pomona, Alpha FIT and Brady material candidates. The editable STEP/GLB assembly uses project-owned dimensional connector envelopes and shows the cable at the actual J1 placement. Every assembly process, test, supply limit, grounding decision and authority remains open.
"""
    replace_marker(BODY / "README.md", "<!-- HR30-E1-J1-POWER-CABLE-P01-START -->", "<!-- HR30-E1-J1-POWER-CABLE-P01-END -->", root_readme)


def generate_into_fixture() -> dict:
    if not BASE_INTEGRATED_STEP.is_file():
        raise RuntimeError("E1 fixture with logic harnesses must be generated first")
    logic_map = rows(LOGIC / "connector-contact-map.csv")
    if {(row["destination_contact"], row["net"]) for row in logic_map} != {
        ("J1.2", "AUX_5V_SAFE"), ("J1.1", "CTRL_GND")
    }:
        raise RuntimeError("logic-power contact map drift")
    geometry = write_cad()
    write_registers(geometry)
    write_svg()
    write_docs()
    update_status_and_root()
    shutil.copy2(__file__, OUT / "e1-j1-power-cable-source.py")
    return geometry


def main() -> int:
    result = generate_into_fixture()
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
