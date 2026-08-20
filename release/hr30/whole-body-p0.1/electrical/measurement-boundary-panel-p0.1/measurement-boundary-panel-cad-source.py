#!/usr/bin/env python3
"""Generate project CAD for the HR-30 measurement boundary panel P0.1."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import cadquery as cq


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "hr30" / "whole-body-p0.1" / "electrical" / "measurement-boundary-panel-p0.1"
WARNING = "PRELIMINARY - UNBUILT MEASUREMENT FIXTURE - ZERO SAFETY CREDIT - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, WALKING OR ENERGIZATION"


def box(center: tuple[float, float, float], size: tuple[float, float, float]) -> cq.Workplane:
    x, y, z = center
    return cq.Workplane("XY").box(*size).translate((x, y, z))


def clean_step(path: Path) -> None:
    text = path.read_text(encoding="utf-8", errors="replace")
    text = text.replace("FILE_NAME('Open CASCADE Shape Model'", "FILE_NAME('HR30_MEASUREMENT_BOUNDARY_PANEL_P0.1'")
    path.write_text(text, encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    # Project geometry follows the Hammond RZ0218C external envelope and its
    # published 213.87 x 137.87 mm maximum PCB window. Received parts control.
    base_outer = box((0, 0, 22.5), (222, 146, 45))
    base_inner = box((0, 0, 28), (212, 136, 38))
    base = base_outer.cut(base_inner)
    lid_frame = box((0, 0, 50), (222, 146, 10)).cut(box((0, 0, 50), (212, 136, 12)))
    lid_clear = box((0, 0, 55.5), (212, 136, 3))
    pcb = box((0, 0, 12.8), (210, 134, 1.6))
    analog_bar = box((-15, -12, 15.6), (150, 102, 4))
    slate_bar = box((74, 0, 15.6), (38, 120, 4))
    input_blocks = [box((-98, -47 + i * 13.5, 22), (10, 9, 14)) for i in range(8)]
    output_blocks = [box((98, -47 + i * 13.5, 22), (10, 9, 14)) for i in range(8)]
    slate_led = cq.Workplane("XY").circle(3).extrude(12).translate((73, -24, 16))
    slate_button = box((73, 0, 20), (10, 10, 12))
    battery = box((0, 0, 38), (58, 50, 18))
    parts = {
        "HAMMOND_RZ0269C_BASE_ENVELOPE": base,
        "CLEAR_LID_FRAME": lid_frame,
        "CLEAR_LID": lid_clear,
        "PCB_186X106": pcb,
        "EIGHT_FLOATING_CHANNELS": analog_bar,
        "BATTERY_SYNC_SLATE_ISLAND": slate_bar,
        "SYNC_LED": slate_led,
        "SYNC_BUTTON": slate_button,
        "KEYSTONE_2464_3AA_ENVELOPE": battery,
    }
    for i, shape in enumerate(input_blocks, 1): parts[f"CH{i}_INPUT_HEADER"] = shape
    for i, shape in enumerate(output_blocks, 1): parts[f"CH{i}_OUTPUT_HEADER"] = shape
    compound = cq.Compound.makeCompound([shape.val() for shape in parts.values()])
    step = OUT / "HR30_measurement_boundary_panel_candidate.step"
    cq.exporters.export(compound, str(step)); clean_step(step)
    assembly = cq.Assembly(name="HR30_MEASUREMENT_BOUNDARY_PANEL_P0.1_NOT_RELEASED")
    palette = [cq.Color(.03,.18,.40,1), cq.Color(.20,.58,.88,1), cq.Color(.98,.72,.08,1), cq.Color(.20,.24,.29,1)]
    for index, (name, shape) in enumerate(parts.items()):
        color = cq.Color(.55,.82,.96,.28) if name == "CLEAR_LID" else palette[index % len(palette)]
        assembly.add(shape, name=name, color=color)
    assembly.save(str(OUT / "HR30_measurement_boundary_panel_candidate.glb"), tolerance=.4, angularTolerance=.15)
    rows = []
    for name, shape in parts.items():
        bb = shape.val().BoundingBox()
        rows.append({
            "item": name, "xmin_mm": round(bb.xmin, 3), "xmax_mm": round(bb.xmax, 3),
            "ymin_mm": round(bb.ymin, 3), "ymax_mm": round(bb.ymax, 3),
            "zmin_mm": round(bb.zmin, 3), "zmax_mm": round(bb.zmax, 3),
            "geometry_status": "PROJECT INTERFACE ENVELOPE; RECEIVED PART CONTROLS",
            "warning": WARNING,
        })
    write_csv(OUT / "cad-item-register.csv", rows)
    (OUT / "cad-status.json").write_text(json.dumps({
        "identifier": "HR30-MEASUREMENT-BOUNDARY-PANEL-CAD-P0.1",
        "warning": WARNING,
        "enclosure_candidate": "Hammond RZ0218C",
        "enclosure_external_mm": [222, 146, 55],
        "published_max_pcb_mm": [213.87, 137.87],
        "project_pcb_mm": [210, 134, 1.6],
        "modeled_item_count": len(parts),
        "received_part_dimensional_validation": False,
        "fabrication_authority": False,
        "connection_authority": False,
        "energization_authority": False,
    }, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"items": len(parts), "step": step.name, "glb": True, "authority": 0}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
