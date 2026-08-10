#!/usr/bin/env python3
"""Build the R185 review-only Q4X panel and catalog-envelope proxy STEP."""

from pathlib import Path
import re

import cadquery as cq


OUT = Path(__file__).resolve().parent

# Manufacturer geometry: Hammond 14F0907 official drawing/STEP.
PANEL_X = 174.498
PANEL_Y = 222.250
PANEL_T = 3.175
HOLE_D = 6.350
HOLE_X = 158.750
HOLE_Y = 209.550

# Candidate geometry: centered Phoenix 1207650 rail cut and catalog-width proxies.
RAIL_L = 150.000
RAIL_W = 35.000
RAIL_H = 7.500
GROUP_WIDTHS = [9.5, 6.2, 5.2, 2.2, 26.0, 2.2, 9.5]
GROUP_HEIGHTS = [54.6, 105.8, 72.2, 72.2, 48.6, 48.6, 54.6]


panel = cq.Workplane("XY").box(PANEL_X, PANEL_Y, PANEL_T)
for x in (-HOLE_X / 2, HOLE_X / 2):
    for y in (-HOLE_Y / 2, HOLE_Y / 2):
        panel = panel.faces(">Z").workplane().pushPoints([(x, y)]).hole(HOLE_D)

# The rail is a planning envelope, not a profile-faithful manufacturing model.
rail = cq.Workplane("XY").box(RAIL_L, RAIL_W, RAIL_H).translate((0, 0, PANEL_T / 2 + RAIL_H / 2))

blocks = []
x0 = -sum(GROUP_WIDTHS) / 2
for width, height in zip(GROUP_WIDTHS, GROUP_HEIGHTS):
    block = cq.Workplane("XY").box(width, height, 36.8).translate((x0 + width / 2, 0, PANEL_T / 2 + RAIL_H + 18.4))
    blocks.append(block)
    x0 += width

assembly = cq.Assembly(name="HR-V0-Q4X-BOX-LAYOUT-P0.1")
assembly.add(panel, name="PANEL1_14F0907_PROXY", color=cq.Color(0.74, 0.91, 1.0))
assembly.add(rail, name="DR1_150MM_ENVELOPE", color=cq.Color(0.55, 0.60, 0.65))
for index, block in enumerate(blocks, start=1):
    assembly.add(block, name=f"CATALOG_ENVELOPE_{index:02d}", color=cq.Color(0.96, 0.75, 0.15))

step_path = OUT / "hr-v0-q4x-box-layout-p0.1.step"
assembly.save(str(step_path), exportType="STEP")
# Open Cascade writes harmless trailing spaces into STEP records. Normalize the
# generated text so repository whitespace checks remain meaningful and quiet.
step_path.write_bytes(re.sub(rb"[ \t]+(?=\r?\n)", b"", step_path.read_bytes()))
cq.exporters.export(panel, str(OUT / "14F0907-review-proxy.stl"), tolerance=0.02, angularTolerance=0.1)

(OUT / "README.md").write_text(
    "# HR-V0 Q4X box layout P0.1 CAD\n\n"
    "PRELIMINARY - REVIEW PROXY ONLY - NOT APPROVED FOR FABRICATION OR DRILLING.\n\n"
    "`build.py` creates a panel solid from Hammond catalog geometry plus a rectangular rail and component-envelope review assembly. "
    "The rail is not a profile-faithful part and the component blocks are not supplier CAD. The STEP/STL are collision and review proxies, not fabrication outputs. "
    "No rail fastener or gland hole is modeled because those coordinates remain SELECTION REQUIRED.\n",
    encoding="utf-8",
)
