"""Generate exact-source ROBOTIS interface-orientation evidence for R53."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path

import cadquery as cq


ROOT = Path(__file__).resolve().parents[1]
VENDOR = ROOT / "cad" / "vendor" / "robotis"
OUT = ROOT / "cad" / "hr-v0" / "generated" / "vendor-interfaces"
REVISION = "HR-V0-ROBOTIS-IF-P0.1"
WARNING = "PRELIMINARY - ORIENTATION EVIDENCE ONLY - NO BUILDABLE ARM GEOMETRY"

SOURCES = (
    ("XMHD-540.N101.I101.STP", "XM540 actuator", "body and output-axis reference"),
    ("FR13-H101K.stp", "FR13-H101K", "moving hinge/output frame"),
    ("FR13-S101K.stp", "FR13-S101K", "side/body frame candidate; architecture not selected"),
    ("FR13-S102K.stp", "FR13-S102K", "bottom/body frame; P0.2 flat-plate use withdrawn"),
    ("FR12-H104K.stp", "FR12-H104K", "gripper-side frame candidate; architecture not released"),
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def shape(path: Path) -> cq.Shape:
    return cq.importers.importStep(str(path)).val()


def fmt(value: float) -> str:
    return f"{value:.6f}".rstrip("0").rstrip(".")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    loaded = {filename: shape(VENDOR / filename) for filename, _, _ in SOURCES}
    rows: list[dict[str, str]] = []
    for filename, component, role in SOURCES:
        bb = loaded[filename].BoundingBox()
        rows.append(
            {
                "component": component,
                "source": f"cad/vendor/robotis/{filename}",
                "sha256": sha256(VENDOR / filename),
                "xmin_mm": fmt(bb.xmin), "xmax_mm": fmt(bb.xmax),
                "ymin_mm": fmt(bb.ymin), "ymax_mm": fmt(bb.ymax),
                "zmin_mm": fmt(bb.zmin), "zmax_mm": fmt(bb.zmax),
                "same_origin_role": role,
                "release_disposition": "REFERENCE_ONLY" if filename != "FR13-S102K.stp" else "P0.2_APPLICATION_WITHDRAWN",
            }
        )
    csv_path = OUT / "same-origin-bounds.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys(), lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)

    trio = (loaded["XMHD-540.N101.I101.STP"], loaded["FR13-H101K.stp"], loaded["FR13-S102K.stp"])
    compound = cq.Compound.makeCompound(list(trio))
    step_path = OUT / "XM540-H101-S102-same-origin.step"
    cq.exporters.export(compound, str(step_path))
    # CadQuery/OCC emits harmless trailing spaces in STEP records. Canonicalize
    # them so repository whitespace checks and cross-checkout hashes are stable.
    step_text = step_path.read_text(encoding="utf-8")
    step_text = re.sub(
        r"(FILE_NAME\('Open CASCADE Shape Model',)'[^']*'",
        r"\1'1980-01-01T00:00:00'",
        step_text,
        count=1,
    )
    step_path.write_text("\n".join(line.rstrip() for line in step_text.splitlines()) + "\n", encoding="utf-8", newline="\n")

    names = ("XM540 actuator", "H101 moving output frame", "S102 bottom body frame")
    colors = ("#0b4f8a", "#f3b61f", "#66c7f4")
    def rect(bb: cq.BoundBox, plane: str, x0: float, y0: float, scale: float, color: str, name: str) -> str:
        if plane == "xz":
            a0, a1, b0, b1 = bb.xmin, bb.xmax, bb.zmin, bb.zmax
        else:
            a0, a1, b0, b1 = bb.ymin, bb.ymax, bb.zmin, bb.zmax
        return (f'<rect x="{x0+(a0+50)*scale:.1f}" y="{y0+(60-b1)*scale:.1f}" '
                f'width="{(a1-a0)*scale:.1f}" height="{(b1-b0)*scale:.1f}" '
                f'fill="{color}" fill-opacity="0.36" stroke="{color}" stroke-width="3"/>'
                f'<text x="{x0+(a0+50)*scale:.1f}" y="{y0+(60-b1)*scale-8:.1f}" class="label">{name}</text>')
    boxes = [item.BoundingBox() for item in trio]
    svg_parts = [rect(bb, "xz", 40, 160, 4.0, color, name) for bb, color, name in zip(boxes, colors, names)]
    svg_parts += [rect(bb, "yz", 700, 160, 4.0, color, name) for bb, color, name in zip(boxes, colors, names)]
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="920" viewBox="0 0 1400 920">
<style>text{{font-family:Arial,sans-serif;fill:#082b4c;font-size:18px}}.title{{font-size:34px;font-weight:700}}.sub{{font-size:22px;font-weight:700}}.label{{font-size:16px;font-weight:700}}.warn{{font-size:20px;font-weight:700;fill:#8a3b00}}</style>
<rect width="1400" height="920" fill="#f7fbff"/>
<text x="40" y="55" class="title">XM540 frame interfaces in manufacturer STEP coordinates</text>
<text x="40" y="92" class="warn">{WARNING}</text>
<text x="40" y="135" class="sub">X-Z projection</text><text x="700" y="135" class="sub">Y-Z projection</text>
{''.join(svg_parts)}
<rect x="40" y="650" width="1320" height="220" rx="14" fill="#fff4cd" stroke="#f3b61f" stroke-width="3"/>
<text x="70" y="700" class="sub">R53 disposition</text>
<text x="70" y="740">The exact files share an assembly origin, but H101 is a moving U-frame and S102 is a bottom body frame.</text>
<text x="70" y="777">Their link interfaces are not the single coplanar plate assumed by MV0-001 and MV0-003.</text>
<text x="70" y="814">P0.2 arm geometry and all supplier packets are withdrawn. Bounds shown here are evidence—not mounting surfaces.</text>
<text x="70" y="851" class="warn">Replacement requires exact transforms, parallel-axis proof, collision/tool access and a qualified load-path review.</text>
</svg>'''
    (OUT / "XM540-frame-orientation.svg").write_text(svg, encoding="utf-8", newline="\n")

    intersections = {}
    trio_keys = ("actuator_h101", "actuator_s102", "h101_s102")
    for key, left, right in zip(trio_keys, (trio[0], trio[0], trio[1]), (trio[1], trio[2], trio[2])):
        intersections[key] = fmt(left.intersect(right).Volume())
    summary = {
        "revision": REVISION,
        "warning": WARNING,
        "coordinate_basis": "manufacturer STEP files imported without transforms",
        "source_count": len(SOURCES),
        "pairwise_intersection_volume_mm3": intersections,
        "engineering_disposition": "P0.2 flat-link and shoulder-adapter geometry withdrawn; replacement architecture selection required",
    }
    (OUT / "interface-orientation-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"Generated {REVISION}: {len(rows)} exact-source bounds and same-origin STEP/SVG evidence")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
