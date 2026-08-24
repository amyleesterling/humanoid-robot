#!/usr/bin/env python3
"""Generate the HR-30 E1 controls-only physical fixture candidate.

The fixture carries the native motion-controller, two interface carriers and
SWD adapter while physically omitting every actuator-power component.  Closed
carrier covers and under-panel logic-cable passages make all eight field ports
inaccessible during E1.  It is an unbuilt candidate and grants no authority to
connect or energize hardware.
"""

from __future__ import annotations

import csv
import hashlib
import html
import json
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import cadquery as cq

import generate_hr30_system_package_p01 as system


ROOT = Path(__file__).resolve().parents[1]
BODY = ROOT / "hr30" / "whole-body-p0.1"
OUT = BODY / "electrical" / "e1-controls-only-fixture-p0.1"
KICAD = Path(r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe")
IDENTIFIER = "HR30-E1-CONTROLS-ONLY-FIXTURE-P0.1"
WARNING = (
    "PRELIMINARY - UNBUILT CONTROLS-ONLY FIXTURE CANDIDATE - NOT APPROVED "
    "FOR CONNECTION, POWERED TESTING, MOTION, WALKING, OR ENERGIZATION"
)
AUTHORITY = "NO CONNECTION, POWERED-TEST, MOTION, WALKING OR ENERGIZATION AUTHORITY"

BOARD_SOURCES = {
    "MCU": BODY / "electrical/motion-controller-p0.1/board/hr30-motion-controller-p0.1.kicad_pcb",
    "CARRIER_A": BODY / "electrical/carriers-p0.1/carrier-a/hr30-carrier-a-p0.1.kicad_pcb",
    "CARRIER_B": BODY / "electrical/carriers-p0.1/carrier-b/hr30-carrier-b-p0.1.kicad_pcb",
    "SWD": BODY / "electrical/swd-adapter-p0.1/board/hr30-swd-adapter-p0.1.kicad_pcb",
    "WATCHDOG": BODY / "electrical/e1-diagnostic-watchdog-p0.1/board/hr30-e1-diagnostic-watchdog-p0.1.kicad_pcb",
}

PLACEMENTS = {
    "MCU": (-92.0, -42.0),
    "CARRIER_A": (44.0, -48.0),
    "CARRIER_B": (44.0, 48.0),
    "SWD": (-122.0, 58.0),
    "WATCHDOG": (-75.0, 60.0),
}

HOLES = {
    "MCU": [(3.5, -3.5), (2.0, -39.5), (80.0, -39.5), (78.5, -3.5)],
    "CARRIER_A": [(3.5, -3.5), (3.5, -38.5), (78.5, -38.5), (78.5, -3.5)],
    "CARRIER_B": [(3.5, -3.5), (3.5, -38.5), (78.5, -38.5), (78.5, -3.5)],
    "SWD": [(2.5, -2.5), (29.5, -17.5)],
    "WATCHDOG": [(12.0, -22.0), (37.0, -22.0)],
}

SIZE = {
    "MCU": (82.0, 42.0),
    "CARRIER_A": (82.0, 42.0),
    "CARRIER_B": (82.0, 42.0),
    "SWD": (32.0, 20.0),
    "WATCHDOG": (40.0, 25.0),
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise RuntimeError(f"refusing empty table {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def clean_step(path: Path) -> None:
    path.write_bytes(re.sub(rb"[ \t]+(?=\r?\n)", b"", path.read_bytes()))


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


def export_boards() -> dict[str, Path]:
    exported: dict[str, Path] = {}
    log: list[str] = []
    for key, source in BOARD_SOURCES.items():
        target = OUT / f"{key.lower()}-native-pcb.step"
        command = [
            str(KICAD), "pcb", "export", "step", "--force", "--subst-models",
            "--output", str(target), str(source),
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        log.append(
            "$ " + subprocess.list2cmdline(command) + "\n" + result.stdout + result.stderr
            + f"\nexit={result.returncode}\n"
        )
        if result.returncode or not target.is_file():
            raise RuntimeError(f"KiCad STEP export failed for {key}")
        clean_step(target)
        exported[key] = target
    (OUT / "kicad-board-export.log").write_text("\n".join(log), encoding="utf-8", newline="\n")
    return exported


def centered(shape: cq.Shape, key: str, bottom_z: float = 14.0) -> cq.Shape:
    width, depth = SIZE[key]
    cx, cy = PLACEMENTS[key]
    bounds = shape.BoundingBox()
    return shape.translate((cx - width / 2.0, cy + depth / 2.0, bottom_z - bounds.zmin))


def local_to_panel(key: str, x: float, y: float) -> tuple[float, float]:
    width, depth = SIZE[key]
    cx, cy = PLACEMENTS[key]
    return cx - width / 2.0 + x, cy + depth / 2.0 + y


def carrier_cover(cx: float, cy: float) -> cq.Shape:
    # Fully closed, transparent cover. The controller cable enters through the
    # base plate directly below JCA1/JCB1; no external field-port opening exists.
    outer = cq.Workplane("XY").box(98, 58, 28).translate((cx, cy, 20)).val()
    inner = cq.Workplane("XY").box(92, 52, 25).translate((cx, cy, 18.5)).val()
    shell = outer.cut(inner)
    flange_outer = cq.Workplane("XY").box(110, 70, 3).translate((cx, cy, 4.5)).val()
    flange_inner = cq.Workplane("XY").box(92, 52, 4).translate((cx, cy, 4.5)).val()
    cover = shell.fuse(flange_outer.cut(flange_inner))
    for x, y in cover_fastener_points(cx, cy):
        cover = cover.cut(cq.Workplane("XY").cylinder(5, 1.7).translate((x, y, 2)).val())
    return cover


def cover_fastener_points(cx: float, cy: float) -> list[tuple[float, float]]:
    return [(cx + dx, cy + dy) for dx in (-52.0, 52.0) for dy in (-32.0, 32.0)]


def write_cad(exported: dict[str, Path]) -> dict:
    panel = cq.Workplane("XY").box(360, 240, 6).edges("|Z").fillet(8)
    for x in (-165, 165):
        for y in (-105, 105):
            panel = panel.cut(cq.Workplane("XY").cylinder(10, 2.75).translate((x, y, -5)))

    for key in ("CARRIER_A", "CARRIER_B"):
        for x, y in cover_fastener_points(*PLACEMENTS[key]):
            panel = panel.cut(cq.Workplane("XY").cylinder(10, 1.7).translate((x, y, -5)))

    # Exact PCB mounting-hole axes are taken from the native board sources.
    for key, points in HOLES.items():
        for x, y in points:
            px, py = local_to_panel(key, x, y)
            panel = panel.cut(cq.Workplane("XY").cylinder(10, 1.5).translate((px, py, -5)))

    # JCA1/JCB1 are at native board (41,38), which maps to STEP Y=-38.
    # Logic cables pass below the panel so the carrier covers have no openings.
    for key in ("CARRIER_A", "CARRIER_B"):
        sx, sy = local_to_panel(key, 41.0, -38.0)
        panel = panel.cut(cq.Workplane("XY").box(24, 9, 10).translate((sx, sy, 0)))
    for local_x in (17.0, 65.0):
        sx, sy = local_to_panel("MCU", local_x, -38.0)
        panel = panel.cut(cq.Workplane("XY").box(18, 9, 10).translate((sx, sy, 0)))
    panel_shape = panel.val()

    standoffs: list[cq.Shape] = []
    hardware_parts: list[cq.Shape] = []
    hardware_assembly = cq.Assembly(name="HR30_E1_FIXTURE_HARDWARE_P01_NOT_RELEASED")
    for key, points in HOLES.items():
        for x, y in points:
            px, py = local_to_panel(key, x, y)
            pedestal = cq.Workplane("XY").circle(3.0).circle(1.4).extrude(3).translate((px, py, 3)).val()
            threaded_spacer = (
                cq.Workplane("XY").polygon(6, 5.773503).circle(1.05).extrude(8)
                .translate((px, py, 6)).val()
            )
            standoff = cq.Compound.makeCompound([pedestal, threaded_spacer])
            standoffs.append(standoff)
            top_shank = cq.Workplane("XY").circle(1.25).extrude(6).translate((px, py, 9.6)).val()
            top_head = cq.Workplane("XY").circle(2.5).extrude(2.1).translate((px, py, 15.6)).val()
            bottom_shank = cq.Workplane("XY").circle(1.25).extrude(12).translate((px, py, -3)).val()
            bottom_head = cq.Workplane("XY").circle(2.25).extrude(1.6).translate((px, py, -4.6)).val()
            fastener = cq.Compound.makeCompound([top_shank, top_head, bottom_shank, bottom_head])
            hardware_parts.extend([standoff, fastener])
            hardware_assembly.add(standoff, name=f"{key}_M2P5_PEDESTAL_AND_STANDOFF_{len(standoffs):02d}", color=cq.Color(0.88, 0.70, 0.20, 1))
            hardware_assembly.add(fastener, name=f"{key}_M2P5_TOP_BOTTOM_SCREWS_{len(standoffs):02d}", color=cq.Color(0.94, 0.94, 0.86, 1))

    covers = {
        "CARRIER_A": carrier_cover(*PLACEMENTS["CARRIER_A"]),
        "CARRIER_B": carrier_cover(*PLACEMENTS["CARRIER_B"]),
    }
    # Open-top under-panel guard.  The later logic-harness generator places
    # two separate fixed routes inside this protected volume at different Z
    # levels.  The guard is deliberately a tray, not a solid box occupying the
    # cable volume.
    guard_parts = [
        cq.Workplane("XY").box(245, 150, 2).translate((-15, 0, -18)).val(),
        cq.Workplane("XY").box(245, 2, 14).translate((-15, -74, -10)).val(),
        cq.Workplane("XY").box(245, 2, 14).translate((-15, 74, -10)).val(),
        cq.Workplane("XY").box(2, 146, 14).translate((-136.5, 0, -10)).val(),
        cq.Workplane("XY").box(2, 146, 14).translate((106.5, 0, -10)).val(),
    ]
    underside_raceway = cq.Compound.makeCompound(guard_parts)
    feet: list[cq.Shape] = []
    foot_fasteners: list[cq.Shape] = []
    for x in (-165, 165):
        for y in (-105, 105):
            riser = cq.Workplane("XY").circle(11.15).circle(2.75).extrude(7.9).translate((x, y, -10.9))
            riser = riser.cut(cq.Workplane("XY").circle(4.75).extrude(4.8).translate((x, y, -10.9)))
            bumper = cq.Workplane("XY").circle(11.15).extrude(10.1).translate((x, y, -21)).val()
            foot = cq.Compound.makeCompound([riser.val(), bumper])
            feet.append(foot)
            screw_head = cq.Workplane("XY").circle(4.5).extrude(4.5).translate((x, y, -10.9)).val()
            screw_shank = cq.Workplane("XY").circle(2.5).extrude(16).translate((x, y, -6.4)).val()
            nut = cq.Workplane("XY").polygon(6, 9.237604).circle(2.5).extrude(4.2).translate((x, y, 3)).val()
            foot_fastener = cq.Compound.makeCompound([screw_head, screw_shank, nut])
            foot_fasteners.append(foot_fastener)
            hardware_parts.extend([foot, foot_fastener])
            hardware_assembly.add(foot, name=f"FOOT_RISER_AND_SJ5309_{len(feet):02d}", color=cq.Color(0.12, 0.17, 0.23, 0.92))
            hardware_assembly.add(foot_fastener, name=f"FOOT_M5_SCREW_AND_NUT_{len(feet):02d}", color=cq.Color(0.92, 0.92, 0.84, 1))

    cover_fasteners: list[cq.Shape] = []
    for key in ("CARRIER_A", "CARRIER_B"):
        for x, y in cover_fastener_points(*PLACEMENTS[key]):
            shank = cq.Workplane("XY").circle(1.5).extrude(12).translate((x, y, -6)).val()
            head = cq.Workplane("XY").circle(2.8).extrude(2.4).translate((x, y, 6)).val()
            nut = cq.Workplane("XY").polygon(6, 6.350853).circle(1.5).extrude(2.4).translate((x, y, -5.4)).val()
            fastener = cq.Compound.makeCompound([shank, head, nut])
            cover_fasteners.append(fastener)
            hardware_parts.append(fastener)
            hardware_assembly.add(fastener, name=f"{key}_COVER_M3_FASTENER_{len(cover_fasteners):02d}", color=cq.Color(0.94, 0.94, 0.86, 1))

    boards = {
        key: centered(cq.importers.importStep(str(path)).val(), key)
        for key, path in exported.items()
    }
    assembly = cq.Assembly(name="HR30_E1_CONTROLS_ONLY_FIXTURE_P01_NOT_RELEASED")
    assembly.add(panel_shape, name="E1_BASE_PANEL_360x240x6", color=cq.Color(0.72, 0.76, 0.80, 1))
    assembly.add(underside_raceway, name="UNDER_PANEL_LOGIC_CABLE_GUARD", color=cq.Color(0.05, 0.22, 0.42, 0.32))
    for index, foot in enumerate(feet, 1):
        assembly.add(foot, name=f"BENCH_FOOT_{index}", color=cq.Color(0.08, 0.10, 0.12, 1))
    for index, fastener in enumerate(foot_fasteners, 1):
        assembly.add(fastener, name=f"BENCH_FOOT_M5_FASTENER_{index}", color=cq.Color(0.92, 0.92, 0.84, 1))
    for index, standoff in enumerate(standoffs, 1):
        assembly.add(standoff, name=f"M2P5_STANDOFF_{index:02d}", color=cq.Color(0.85, 0.65, 0.18, 1))
    for index, fastener in enumerate(hardware_parts[1::2][:len(standoffs)], 1):
        assembly.add(fastener, name=f"M2P5_STANDOFF_FASTENER_SET_{index:02d}", color=cq.Color(0.94, 0.94, 0.86, 1))
    board_colors = {
        "MCU": cq.Color(0.05, 0.35, 0.18, 1),
        "CARRIER_A": cq.Color(0.05, 0.42, 0.22, 1),
        "CARRIER_B": cq.Color(0.05, 0.42, 0.22, 1),
        "SWD": cq.Color(0.05, 0.35, 0.18, 1),
        "WATCHDOG": cq.Color(0.10, 0.30, 0.58, 1),
    }
    for key, board in boards.items():
        assembly.add(board, name=f"NATIVE_{key}_PCB", color=board_colors[key])
    for key, cover in covers.items():
        assembly.add(cover, name=f"SEALED_{key}_FIELD_PORT_COVER", color=cq.Color(0.52, 0.82, 1.0, 0.34))
    for index, fastener in enumerate(cover_fasteners, 1):
        assembly.add(fastener, name=f"CARRIER_COVER_FASTENER_{index:02d}", color=cq.Color(0.94, 0.94, 0.86, 1))

    parts = [panel_shape, underside_raceway, *feet, *foot_fasteners, *hardware_parts[1:2 * len(standoffs):2], *standoffs, *boards.values(), *covers.values(), *cover_fasteners]
    combined = cq.Compound.makeCompound(parts)
    combined_path = OUT / "HR30_E1_controls_only_fixture_candidate.step"
    cq.exporters.export(combined, str(combined_path))
    clean_step(combined_path)
    assembly.save(str(OUT / "HR30_E1_controls_only_fixture_candidate.glb"), tolerance=0.18, angularTolerance=0.14)
    hardware_compound = cq.Compound.makeCompound(hardware_parts)
    hardware_path = OUT / "HR30_E1_fixture_hardware_candidate.step"
    cq.exporters.export(hardware_compound, str(hardware_path))
    clean_step(hardware_path)
    hardware_assembly.save(str(OUT / "HR30_E1_fixture_hardware_candidate.glb"), tolerance=0.12, angularTolerance=0.10)
    base_path = OUT / "HR30_E1_base_panel_candidate.step"
    cq.exporters.export(panel_shape, str(base_path))
    clean_step(base_path)
    cq.exporters.exportDXF(cq.Workplane("XY").add(panel_shape).faces(">Z"), str(OUT / "HR30_E1_base_panel_candidate.dxf"))
    cover_path = OUT / "HR30_E1_carrier_field_port_cover_candidate.step"
    cq.exporters.export(covers["CARRIER_A"].translate((-PLACEMENTS["CARRIER_A"][0], -PLACEMENTS["CARRIER_A"][1], 0)), str(cover_path))
    clean_step(cover_path)
    cq.exporters.export(
        covers["CARRIER_A"].translate((-PLACEMENTS["CARRIER_A"][0], -PLACEMENTS["CARRIER_A"][1], 0)),
        str(OUT / "HR30_E1_carrier_field_port_cover_candidate.stl"), tolerance=0.10,
    )
    bounds = combined.BoundingBox()
    return {
        "assembly_extent_mm": [round(bounds.xlen, 6), round(bounds.ylen, 6), round(bounds.zlen, 6)],
        "panel_mm": [360.0, 240.0, 6.0],
        "standoff_count": len(standoffs),
        "sealed_carrier_cover_count": len(covers),
        "cover_fastener_count": len(cover_fasteners),
        "bench_foot_count": len(feet),
        "actuator_field_port_count": 8,
    }


def board_rows(exported: dict[str, Path]) -> list[dict]:
    rows: list[dict] = []
    for key in ("MCU", "CARRIER_A", "CARRIER_B", "SWD", "WATCHDOG"):
        width, depth = SIZE[key]
        rows.append({
            "board_id": key,
            "native_pcb": BOARD_SOURCES[key].relative_to(ROOT).as_posix(),
            "native_pcb_sha256": sha(BOARD_SOURCES[key]),
            "exported_step": exported[key].name,
            "board_width_mm": f"{width:.3f}",
            "board_depth_mm": f"{depth:.3f}",
            "center_x_mm": f"{PLACEMENTS[key][0]:.3f}",
            "center_y_mm": f"{PLACEMENTS[key][1]:.3f}",
            "mount_hole_count": len(HOLES[key]),
            "mount_hole_diameter_mm": "2.700 NATIVE / 3.000 PANEL CLEARANCE",
            "state": "NATIVE PCB IDENTITY BOUND; PHYSICAL BOARD UNBUILT",
            "warning": WARNING,
        })
    return rows


def write_registers(exported: dict[str, Path], geometry: dict) -> None:
    write_csv(OUT / "pcb-placement-register.csv", board_rows(exported))
    hole_rows = []
    for key, points in HOLES.items():
        for index, (x, y) in enumerate(points, 1):
            px, py = local_to_panel(key, x, y)
            hole_rows.append({
                "hole_id": f"{key}-H{index}", "board_id": key,
                "native_x_mm": f"{x:.3f}", "native_step_y_mm": f"{y:.3f}",
                "panel_x_mm": f"{px:.3f}", "panel_y_mm": f"{py:.3f}",
                "native_hole_diameter_mm": "2.700", "panel_clearance_diameter_mm": "3.000",
                "fastener": "M2.5 CANDIDATE - LENGTH/MATERIAL/TORQUE SELECTION REQUIRED",
                "state": "CAD AXIS DEFINED; FIT UNVALIDATED", "warning": WARNING,
            })
    write_csv(OUT / "mount-hole-register.csv", hole_rows)

    write_csv(OUT / "field-port-exclusion-register.csv", [
        {
            "port_id": f"{carrier}-CH{channel}", "carrier": carrier,
            "whole_body_bus": bus, "power_contact_present": "NO - DATA-ONLY INTERFACE",
            "e1_physical_state": "ENCLOSED BY SCREW-RETAINED COVER; NO EXTERNAL OPENING",
            "verification": "COVER PRESENCE/FASTENER WITNESS AND ZERO FIELD CABLES - NOT EXECUTED",
            "authority": AUTHORITY, "warning": WARNING,
        }
        for carrier, buses in (
            ("CARRIER_A", ["RS-LLEG", "RS-RLEG", "RS-LARM", "RS-RARM"]),
            ("CARRIER_B", ["RS-WAIST", "TTL-LDIST", "TTL-RDIST", "TTL-HEAD"]),
        ) for channel, bus in enumerate(buses, 1)
    ])

    write_csv(OUT / "e1-configuration-register.csv", [
        {"stage": "E1-A", "installed": "MCU + SWD adapter", "physically_absent": "both carriers; every PDU; every actuator cable; every actuator", "permitted_intent": "logic input inspection and no-motion target flash after separate approval", "execution": "NOT EXECUTED", "authority": AUTHORITY, "warning": WARNING},
        {"stage": "E1-B", "installed": "MCU + both carriers + sealed covers + under-panel logic cables", "physically_absent": "all eight field cables; every PDU; every actuator power source; every actuator", "permitted_intent": "logic boot and UART-direction inactive-state measurement after separate approval", "execution": "NOT EXECUTED", "authority": AUTHORITY, "warning": WARNING},
        {"stage": "E1-C", "installed": "E1-B plus selected diagnostic watchdog in separately released adapter", "physically_absent": "all actuator interfaces remain inaccessible and unpowered", "permitted_intent": "watchdog/fault-state HIL after design and separate approval", "execution": "NOT EXECUTED", "authority": AUTHORITY, "warning": WARNING},
    ])

    write_csv(OUT / "connector-boundary-register.csv", [
        {"boundary": "J1", "endpoint": "motion-controller logic input", "allowed_on_fixture": "5 V LOGIC CANDIDATE THROUGH LOGIC-POWER-KIT ONLY", "e1_state": "UNCONNECTED / UNPOWERED", "selection": "JST VHR-2N / SVH-21T-P1.1 CANDIDATE; ASSEMBLY OPEN", "warning": WARNING},
        {"boundary": "JDBG1", "endpoint": "motion-controller SWD", "allowed_on_fixture": "STDC14 ADAPTER PATH CANDIDATE", "e1_state": "UNCONNECTED", "selection": "EXISTING SWD ADAPTER CANDIDATE; CABLE/PROBE OPEN", "warning": WARNING},
        {"boundary": "JIO1_WATCHDOG", "endpoint": "motion-controller diagnostic watchdog fixture cable", "allowed_on_fixture": "CONTACTS 1,2,3,5 ONLY; CONTACT 3 HARD-LOW; OUTPUTS LOCAL", "e1_state": "UNBUILT / UNCONNECTED / UNPOWERED", "selection": "TPS3431SDRBR ADAPTER + GHR-08V-S FOUR-CONDUCTOR CABLE CANDIDATE; ZERO SAFETY CREDIT", "warning": WARNING},
        {"boundary": "JMCU_A", "endpoint": "carrier A logic-only link", "allowed_on_fixture": "UNDER-PANEL PREWIRED LOGIC CABLE ONLY", "e1_state": "UNBUILT", "selection": "15-CIRCUIT JST GH HARNESS SELECTION/CRIMP VALIDATION OPEN", "warning": WARNING},
        {"boundary": "JMCU_B", "endpoint": "carrier B logic-only link", "allowed_on_fixture": "UNDER-PANEL PREWIRED LOGIC CABLE ONLY", "e1_state": "UNBUILT", "selection": "15-CIRCUIT JST GH HARNESS SELECTION/CRIMP VALIDATION OPEN", "warning": WARNING},
        {"boundary": "FIELD_PORTS", "endpoint": "eight actuator-data outputs", "allowed_on_fixture": "NONE", "e1_state": "BLOCKED BY TWO CLOSED COVERS", "selection": "COVER MATERIAL/FASTENERS/RECEIVED CLEARANCE OPEN", "warning": WARNING},
        {"boundary": "ACTUATOR_POWER", "endpoint": "all actuator VDD conductors and protection hardware", "allowed_on_fixture": "NONE", "e1_state": "NO CONNECTOR, CONDUCTOR, PDU OR SOURCE PRESENT", "selection": "NOT APPLICABLE TO E1", "warning": WARNING},
    ])

    write_csv(OUT / "candidate-bom.csv", [
        {"item": "E1-01", "quantity": 1, "part": "360 x 240 x 6 mm base panel", "candidate": "CLEAR POLYCARBONATE OR ALUMINUM - SELECTION REQUIRED", "fabrication": "CNC / WATERJET; DXF PROVIDED", "release": "NO", "warning": WARNING},
        {"item": "E1-02", "quantity": 2, "part": "carrier field-port cover", "candidate": "3 mm CLEAR POLYCARBONATE CANDIDATE", "fabrication": "PRINT/MACHINE/THERMOFORM PROCESS SELECTION REQUIRED", "release": "NO", "warning": WARNING},
        {"item": "E1-03", "quantity": 16, "part": "M2.5 x 8 mm standoff", "candidate": "MATERIAL/ORDER CODE SELECTION REQUIRED", "fabrication": "PURCHASE", "release": "NO", "warning": WARNING},
        {"item": "E1-04", "quantity": 32, "part": "M2.5 board/standoff fastener", "candidate": "LENGTH/HEAD/MATERIAL/TORQUE SELECTION REQUIRED", "fabrication": "PURCHASE", "release": "NO", "warning": WARNING},
        {"item": "E1-05", "quantity": 4, "part": "20 mm bench foot", "candidate": "NONSLIP MATERIAL/ORDER CODE SELECTION REQUIRED", "fabrication": "PURCHASE", "release": "NO", "warning": WARNING},
        {"item": "E1-06", "quantity": 1, "part": "under-panel logic cable cover", "candidate": "INSULATING MATERIAL SELECTION REQUIRED", "fabrication": "MACHINE/PRINT", "release": "NO", "warning": WARNING},
        {"item": "E1-07", "quantity": 1, "part": "native HR-30 motion controller", "candidate": "CURRENT P0.1 PCB CANDIDATE", "fabrication": "UNBUILT / PCB RELEASE OPEN", "release": "NO", "warning": WARNING},
        {"item": "E1-08", "quantity": 2, "part": "native HR-30 interface carriers", "candidate": "CURRENT CARRIER A/B P0.1 PCB CANDIDATES", "fabrication": "UNBUILT / PCB RELEASE OPEN", "release": "NO", "warning": WARNING},
        {"item": "E1-09", "quantity": 1, "part": "native HR-30 SWD adapter", "candidate": "CURRENT P0.1 PCB CANDIDATE", "fabrication": "UNBUILT / PCB RELEASE OPEN", "release": "NO", "warning": WARNING},
        {"item": "E1-10", "quantity": 1, "part": "native HR-30 E1 diagnostic watchdog", "candidate": "TPS3431 P0.1 PCB CANDIDATE; ZERO SAFETY CREDIT", "fabrication": "UNBUILT / PCB RELEASE OPEN", "release": "NO", "warning": WARNING},
    ])

    write_csv(OUT / "assembly-sequence.csv", [
        {"step": 1, "operation": "machine base and covers; deburr and clean", "mandatory_check": "dimensions, edge condition, insulation/material identity", "result": "NOT EXECUTED", "authority": AUTHORITY, "warning": WARNING},
        {"step": 2, "operation": "fit feet, standoffs and empty panel hardware", "mandatory_check": "flatness, retention, no conductive debris", "result": "NOT EXECUTED", "authority": AUTHORITY, "warning": WARNING},
        {"step": 3, "operation": "fit unpowered MCU, SWD adapter and diagnostic-watchdog adapter", "mandatory_check": "native hole alignment and received-board clearance; permit remains hard-low", "result": "NOT EXECUTED", "authority": AUTHORITY, "warning": WARNING},
        {"step": 4, "operation": "fit unpowered carriers and under-panel logic harnesses", "mandatory_check": "point-to-point/short/retention inspection; no field cables", "result": "NOT EXECUTED", "authority": AUTHORITY, "warning": WARNING},
        {"step": 5, "operation": "install both closed carrier covers", "mandatory_check": "all eight field ports physically inaccessible; witness fasteners", "result": "NOT EXECUTED", "authority": AUTHORITY, "warning": WARNING},
        {"step": 6, "operation": "independent E1 configuration inspection", "mandatory_check": "zero actuator-power hardware and zero actuator/data field cables present", "result": "NOT EXECUTED", "authority": AUTHORITY, "warning": WARNING},
    ])

    source_paths = [
        ("generator", Path(__file__)),
        *[(f"native {key} PCB", path) for key, path in BOARD_SOURCES.items()],
        ("logic-power kit status", BODY / "electrical/logic-power-kit-p0.1/logic-power-status.json"),
        ("no-motion firmware status", BODY / "firmware/hr30-motion-controller-p0.1/firmware-status.json"),
        ("no-motion target binary", BODY / "firmware/hr30-motion-controller-p0.1/output/stm32h743-p0.1/hr30-motion-controller-stm32h743.bin"),
        ("SWD bring-up status", BODY / "firmware/stm32-target-bringup-p0.1/bringup-status.json"),
    ]
    write_csv(OUT / "source-binding.csv", [
        {"role": role, "path": path.relative_to(ROOT).as_posix(), "sha256": sha(path), "state": "BOUND", "warning": WARNING}
        for role, path in source_paths
    ])

    write_csv(OUT / "open-holds.csv", [
        {"hold_id": "E1-H01", "unresolved": "all five native PCBs remain unbuilt/uninspected candidates", "closure": "fabrication release, received inspection, assembly records and independent electrical review", "state": "OPEN", "authority": AUTHORITY, "warning": WARNING},
        {"hold_id": "E1-H02", "unresolved": "carrier STEP exports report missing 3D models for controller-side JST GH connectors", "closure": "received connector envelope or authoritative model; cover/slot clearance inspection", "state": "OPEN", "authority": AUTHORITY, "warning": WARNING},
        {"hold_id": "E1-H03", "unresolved": "panel, covers, standoffs, feet and fasteners are not selected or built", "closure": "exact material/order codes, DFM, fabrication and dimensional inspection", "state": "OPEN", "authority": AUTHORITY, "warning": WARNING},
        {"hold_id": "E1-H04", "unresolved": "J1 and both 15-circuit logic harnesses are unbuilt", "closure": "released wire/contact/tooling/process plus continuity, isolation, pull and retention records", "state": "OPEN", "authority": AUTHORITY, "warning": WARNING},
        {"hold_id": "E1-H05", "unresolved": "logic supply setpoint/current/OCP and DC-reference plan remain unreleased", "closure": "received-load/inrush/fault measurements and qualified electrical disposition", "state": "OPEN", "authority": AUTHORITY, "warning": WARNING},
        {"hold_id": "E1-H06", "unresolved": "no-motion binary is compiled but unflashed; HIL is unexecuted", "closure": "approved flash, boot, IO, fault-injection and torque-disabled measurements", "state": "OPEN", "authority": AUTHORITY, "warning": WARNING},
        {"hold_id": "E1-H07", "unresolved": "diagnostic watchdog circuit/adapter candidate is selected but board and four-conductor cable are unbuilt and HIL is unexecuted", "closure": "independent review, controlled fabrication/cable assembly, received inspection, hard-low permit confirmation and eight-row HIL evidence", "state": "OPEN", "authority": AUTHORITY, "warning": WARNING},
        {"hold_id": "E1-H08", "unresolved": "fixture has no qualified connection or powered-test authorization", "closure": "named qualified reviewers accept exact as-built fixture and sign a separate stage-specific authorization", "state": "OPEN", "authority": AUTHORITY, "warning": WARNING},
    ])

    status = {
        "identifier": IDENTIFIER, "warning": WARNING,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "native_board_count": 5, "native_board_step_export_count": len(exported),
        "panel_dimensions_mm": geometry["panel_mm"],
        "assembly_extent_mm": geometry["assembly_extent_mm"],
        "native_mount_hole_count": geometry["standoff_count"],
        "sealed_carrier_cover_count": geometry["sealed_carrier_cover_count"],
        "actuator_field_port_count": 8, "actuator_field_ports_physically_covered_in_cad": True,
        "actuator_power_connectors_present": False, "actuator_power_conductors_present": False,
        "actuator_pdu_present": False, "actuator_present": False,
        "fixture_built": False, "native_pcbs_built": False,
        "received_fit_validated": False, "wiring_built_or_inspected": False,
        "firmware_flashed": False, "hil_executed": False,
        "connection_authority": False, "powered_test_authority": False,
        "motion_authority": False, "walking_authority": False,
        "energization_authority": False,
    }
    (OUT / "e1-fixture-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n")


def write_docs() -> None:
    (OUT / "README.md").write_text(f"""# HR-30 E1 controls-only fixture P0.1

**{WARNING}**

This is the missing physical artifact for the whole-body electrification plan's E1 stage. The 360 x 240 mm bench fixture carries the native motion-controller, carrier A, carrier B, SWD-adapter and diagnostic-watchdog board candidates. Sixteen native mounting-hole axes are retained. The watchdog's permit contact is hard-low and its outputs remain local. Each carrier is enclosed by a screw-retained cover with no external opening; its controller cable enters through the panel from below. All eight actuator-data field ports are inaccessible, and the fixture contains no actuator-power connector, PDU, conductor or actuator.

The fixture is an editable/generated CAD candidate, not a built or approved test station. The native PCB STEP exports disclose missing connector models, exact hardware/material selections remain open, and the logic wiring has not been built or inspected. No hardware may be connected or powered from this package.
""", encoding="utf-8", newline="\n")

    stages = "".join(
        f"<tr><td>{html.escape(row['stage'])}</td><td>{html.escape(row['installed'])}</td><td>{html.escape(row['physically_absent'])}</td><td>{html.escape(row['execution'])}</td></tr>"
        for row in list(csv.DictReader((OUT / "e1-configuration-register.csv").open(encoding="utf-8", newline="")))
    )
    ports = "".join(
        f"<tr><td>{html.escape(row['port_id'])}</td><td>{html.escape(row['whole_body_bus'])}</td><td>{html.escape(row['e1_physical_state'])}</td></tr>"
        for row in list(csv.DictReader((OUT / "field-port-exclusion-register.csv").open(encoding="utf-8", newline="")))
    )
    (OUT / "index.html").write_text(f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 E1 controls-only fixture</title><script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/4.1.0/model-viewer.min.js"></script><style>:root{{--deep:#071d36;--blue:#0b4f91;--sky:#dff4ff;--gold:#f2b91d;--paper:#eef8fe;--ink:#142a40;--line:#86c7e7;--red:#8d241f}}*{{box-sizing:border-box}}html,body{{max-width:100%;overflow-x:clip}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.5 system-ui,Segoe UI,sans-serif}}header,main,footer{{padding:clamp(24px,5vw,62px) max(18px,calc((100vw - 1180px)/2))}}header,footer{{background:linear-gradient(135deg,var(--deep),var(--blue));color:white}}h1{{font-size:clamp(38px,6vw,68px);line-height:1.04;max-width:18ch}}h2{{font-size:clamp(28px,4vw,44px)}}.warning{{background:var(--gold);color:#17243a;border:3px solid #805600;padding:16px;font-weight:900}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:18px}}article,.panel{{background:white;border:2px solid var(--line);border-radius:16px;padding:19px;margin:18px 0}}.metric{{font-size:clamp(34px,5vw,54px);font-weight:900;color:var(--blue)}}.hold{{border-color:#c85b4d}}model-viewer{{width:100%;height:min(70vh,650px);background:linear-gradient(#dff4ff,#fff);border:2px solid var(--line);border-radius:16px}}.scroll{{overflow:auto}}table{{border-collapse:collapse;width:100%;min-width:780px}}th,td{{font-size:16px;line-height:1.45;text-align:left;vertical-align:top;padding:13px;border-bottom:1px solid var(--line)}}th{{background:var(--deep);color:white}}a{{color:#075b9b;font-weight:800}}small{{font-size:14px}}@media(max-width:600px){{body{{font-size:16px}}model-viewer{{height:480px}}}}</style></head><body><header><div class="warning">{html.escape(WARNING)}</div><p>Project Button &middot; whole-body E1 artifact</p><h1>Power the controls without creating an actuator path.</h1><p>The complete humanoid now has a physical controls-only fixture candidate, not merely an E1 paragraph.</p></header><main><section class="grid"><article><div class="metric">5</div><p>native PCB candidates on exact mounting axes</p></article><article><div class="metric">8 / 8</div><p>actuator-data field ports enclosed</p></article><article><div class="metric">0</div><p>actuator-power connectors, conductors, PDUs or actuators</p></article><article class="hold"><div class="metric">0</div><p>built fixtures or authorized powered tests</p></article></section><section><h2>Inspect the actual fixture geometry</h2><model-viewer src="HR30_E1_controls_only_fixture_candidate.glb" camera-controls shadow-intensity="0.8" exposure="1.05" alt="Interactive HR-30 E1 controls-only fixture with motion controller, two enclosed interface carriers, SWD adapter and local diagnostic watchdog"></model-viewer><p><a href="HR30_E1_controls_only_fixture_candidate.step">assembly STEP</a> &middot; <a href="HR30_E1_base_panel_candidate.dxf">base DXF</a> &middot; <a href="HR30_E1_carrier_field_port_cover_candidate.stl">cover STL</a></p></section><section class="panel"><h2>Three controlled configurations</h2><div class="scroll"><table><thead><tr><th>Stage</th><th>Installed</th><th>Physically absent</th><th>Execution</th></tr></thead><tbody>{stages}</tbody></table></div></section><section class="panel"><h2>All eight field ports remain inaccessible</h2><div class="scroll"><table><thead><tr><th>Port</th><th>Bus</th><th>Physical state</th></tr></thead><tbody>{ports}</tbody></table></div></section><section class="panel"><h2>Fail-closed boundary</h2><p>The watchdog board shown in CAD grounds the permit contact and keeps WDO/ENOUT local, but the board and cable are unbuilt and receive zero safety credit. Native board fabrication, received connector clearance, panel hardware, logic cables, supply limits, grounding, firmware flashing, HIL and independent approval remain open. This guide cannot authorize connection or power.</p><p><a href="../e1-diagnostic-watchdog-p0.1/index.html">watchdog guide</a> &middot; <a href="open-holds.csv">open holds</a> &middot; <a href="pcb-placement-register.csv">PCB placements</a> &middot; <a href="mount-hole-register.csv">mount axes</a> &middot; <a href="connector-boundary-register.csv">connector boundaries</a> &middot; <a href="candidate-bom.csv">candidate BOM</a></p></section></main><footer>{html.escape(WARNING)}</footer></body></html>""", encoding="utf-8", newline="\n")


def manifest() -> None:
    rows = []
    for path in sorted(OUT.iterdir(), key=lambda item: item.name):
        if path.is_file() and path.name != "file-manifest.csv":
            rows.append({"file": path.name, "bytes": path.stat().st_size, "sha256": sha(path), "warning": WARNING})
    write_csv(OUT / "file-manifest.csv", rows)


def publish_root() -> None:
    readme_block = """## E1 controls-only physical fixture

The [E1 controls-only fixture](electrical/e1-controls-only-fixture-p0.1/index.html) turns the electrification plan's E1 stage into an actual 360 x 240 mm CAD assembly. It mounts the native motion controller, both four-channel carriers, SWD adapter and local diagnostic-watchdog board on their real PCB hole axes, encloses all eight actuator-data field ports, and contains no actuator-power connector, conductor, PDU or actuator. The watchdog permit is hard-low and both outputs stay local. The fixture and boards remain unbuilt; wiring, supply limits, received clearances, firmware/HIL and independent authorization remain open."""
    html_block = """<section id="e1-controls-fixture"><h2>E1 now has a physical controls-only fixture</h2><div class="grid"><article class="card pass"><div class="metric">5</div><p>native PCB candidates on exact hole axes</p></article><article class="card pass"><div class="metric">8 / 8</div><p>actuator-data field ports enclosed in CAD</p></article><article class="card pass"><div class="metric">0</div><p>actuator-power components present</p></article><article class="card hold"><div class="metric">0</div><p>built or powered fixtures</p></article></div><p><a href="electrical/e1-controls-only-fixture-p0.1/index.html">Open the interactive E1 fixture guide</a>. The watchdog receives zero safety credit, and no connection or powered-test authority follows.</p></section>"""
    replace_marker(BODY / "README.md", "<!-- HR30-E1-CONTROLS-FIXTURE-P01-START -->", "<!-- HR30-E1-CONTROLS-FIXTURE-P01-END -->", readme_block)
    replace_marker(BODY / "index.html", "<!-- HR30-E1-CONTROLS-FIXTURE-P01-START -->", "<!-- HR30-E1-CONTROLS-FIXTURE-P01-END -->", html_block)
    status_path = BODY / "package-status.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    status.update({
        "e1_controls_only_fixture_present": True,
        "e1_native_pcb_count": 5,
        "e1_native_mount_hole_count": 16,
        "e1_actuator_field_port_cover_count": 8,
        "e1_actuator_power_component_count": 0,
        "e1_fixture_built": False,
        "e1_connection_authority": False,
        "e1_powered_test_authority": False,
    })
    status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    for path in OUT.iterdir():
        if path.is_file():
            path.unlink()
    exported = export_boards()
    geometry = write_cad(exported)
    write_registers(exported, geometry)
    write_docs()
    import generate_hr30_e1_logic_harness_p01 as logic_harness
    logic_harness.generate_into_fixture()
    import generate_hr30_e1_logic_power_cable_p01 as logic_power_cable
    logic_power_cable.generate_into_fixture()
    import generate_hr30_e1_fixture_hardware_p01 as fixture_hardware
    fixture_hardware.generate_into_fixture()
    shutil.copy2(__file__, OUT / "e1-controls-fixture-source.py")
    manifest()
    publish_root()
    system.refresh_manifest_and_release()
    print(json.dumps(json.loads((OUT / "e1-fixture-status.json").read_text(encoding="utf-8")), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
