"""Generate the HR-30 Boston fabrication execution route.

This package turns the existing 1:1 fit-check and controlled manufacturing
files into sendable, non-powered fabrication handoffs.  It does not release
structural parts or authorize procurement, fabrication, assembly, motion, or
energization.
"""

from __future__ import annotations

import csv
import hashlib
import html
import json
import shutil
import struct
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WB = ROOT / "hr30" / "whole-body-p0.1"
FIT = WB / "full-scale-fit-check-p0.1"
SOURCING = WB / "fabrication-sourcing-p0.1"
OUT = WB / "boston-fabrication-route-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / OUT.name
WARNING = (
    "PRELIMINARY - UNPOWERED NONSTRUCTURAL FIT-CHECK / RFQ ROUTE ONLY - "
    "NOT APPROVED FOR PROCUREMENT, STRUCTURAL FABRICATION, ASSEMBLY, "
    "POWERED TESTING, MOTION, OR ENERGIZATION"
)
ACCESSED = "2026-08-17"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise RuntimeError(f"refusing empty CSV: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def read_binary_stl(path: Path) -> list[tuple[tuple[float, float, float], tuple[tuple[float, float, float], ...], int]]:
    data = path.read_bytes()
    if len(data) < 84:
        raise RuntimeError(f"short STL: {path}")
    count = struct.unpack_from("<I", data, 80)[0]
    if len(data) != 84 + 50 * count:
        raise RuntimeError(f"non-binary or malformed STL: {path}")
    triangles = []
    for index in range(count):
        values = struct.unpack_from("<12fH", data, 84 + 50 * index)
        normal = tuple(values[0:3])
        vertices = (tuple(values[3:6]), tuple(values[6:9]), tuple(values[9:12]))
        triangles.append((normal, vertices, values[12]))
    return triangles


def triangle_bounds(triangles) -> tuple[float, float, float, float, float, float]:
    vertices = [vertex for _, tri, _ in triangles for vertex in tri]
    return (
        min(v[0] for v in vertices), max(v[0] for v in vertices),
        min(v[1] for v in vertices), max(v[1] for v in vertices),
        min(v[2] for v in vertices), max(v[2] for v in vertices),
    )


def write_binary_stl(path: Path, triangles) -> None:
    header = b"HR30 G01 NONSTRUCTURAL FIT CHECK - NO LOAD OR MOTION CREDIT"[:80].ljust(80, b" ")
    payload = bytearray(header)
    payload.extend(struct.pack("<I", len(triangles)))
    for normal, tri, attribute in triangles:
        payload.extend(struct.pack("<12fH", *(normal + tri[0] + tri[1] + tri[2] + (attribute,))))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)


def zip_add_bytes(archive: zipfile.ZipFile, name: str, data: bytes) -> None:
    info = zipfile.ZipInfo(name, date_time=(2026, 8, 17, 12, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    archive.writestr(info, data)


def build_gripper_plate(parts: list[dict[str, str]]) -> tuple[list[dict], dict]:
    placements = {
        "G01_PALM_TOP_BRIDGE": (4.0, 4.0),
        "G01_PALM_BOTTOM_BRIDGE": (53.0, 4.0),
        "G01_PALM_FRONT_PLATE": (102.0, 4.0),
        "G01_PALM_REAR_PLATE": (4.0, 57.0),
        "G01_FINGER_POSITIVE": (43.0, 57.0),
        "G01_FINGER_NEGATIVE": (82.0, 57.0),
        "G01_RACK_POSITIVE": (4.0, 112.0),
        "G01_RACK_NEGATIVE": (40.0, 112.0),
        "G01_PINION": (76.0, 112.0),
    }
    by_id = {row["part_id"]: row for row in parts}
    if set(placements) - set(by_id):
        raise RuntimeError("G01 fit-check source set incomplete")
    combined = []
    rows = []
    for sequence, (part_id, (target_x, target_y)) in enumerate(placements.items(), start=1):
        row = by_id[part_id]
        source = FIT / row["stl_path"]
        triangles = read_binary_stl(source)
        xmin, xmax, ymin, ymax, zmin, zmax = triangle_bounds(triangles)
        dx, dy, dz = target_x - xmin, target_y - ymin, -zmin
        translated = []
        for normal, tri, attribute in triangles:
            translated.append((normal, tuple((v[0] + dx, v[1] + dy, v[2] + dz) for v in tri), attribute))
        combined.extend(translated)
        rows.append({
            "sequence": sequence,
            "part_id": part_id,
            "role": row["role"],
            "source_stl": row["stl_path"],
            "source_sha256": row["stl_sha256"],
            "placed_min_x_mm": f"{target_x:.3f}",
            "placed_min_y_mm": f"{target_y:.3f}",
            "placed_width_mm": f"{xmax - xmin:.3f}",
            "placed_depth_mm": f"{ymax - ymin:.3f}",
            "placed_height_mm": f"{zmax - zmin:.3f}",
            "scale": "1:1 MILLIMETRES - DO NOT SCALE",
            "structural_credit": "NONE",
            "warning": WARNING,
        })
    output = OUT / "bpl-submission" / "HR30_G01_gripper_fit_plate_nonstructural.stl"
    write_binary_stl(output, combined)
    bounds = triangle_bounds(combined)
    summary = {
        "part_count": len(rows),
        "triangle_count": len(combined),
        "bbox_x_mm": bounds[1] - bounds[0],
        "bbox_y_mm": bounds[3] - bounds[2],
        "bbox_z_mm": bounds[5] - bounds[4],
        "stl_path": output.relative_to(OUT).as_posix(),
        "stl_sha256": sha256(output),
    }
    if summary["bbox_x_mm"] > 140 or summary["bbox_y_mm"] > 140 or summary["bbox_z_mm"] > 140:
        raise RuntimeError(f"BPL conservative envelope exceeded: {summary}")
    return rows, summary


def layout_svg(rows: list[dict], summary: dict) -> None:
    scale = 4.5
    canvas_x = 1040
    canvas_y = 700
    rectangles = []
    legend = []
    colors = ["#62c7ee", "#f2b91d", "#8fd3ff", "#ffd86a", "#5aa7df", "#e8b748", "#9ad9ee", "#f7cc51", "#79bce3"]
    for index, row in enumerate(rows):
        x = float(row["placed_min_x_mm"]) * scale + 34
        y = float(row["placed_min_y_mm"]) * scale + 72
        width = float(row["placed_width_mm"]) * scale
        height = float(row["placed_depth_mm"]) * scale
        rectangles.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{width:.1f}" height="{height:.1f}" rx="5" fill="{colors[index]}" stroke="#071d36" stroke-width="2"/>'
            f'<text x="{x + 7:.1f}" y="{y + 20:.1f}" font-size="16" font-weight="800" fill="#071d36">{index + 1}</text>'
        )
        legend.append(f'<text x="705" y="{90 + index * 43}" font-size="16" fill="#142a40"><tspan font-weight="800">{index + 1}.</tspan> {html.escape(row["part_id"])}</text>')
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_x}" height="{canvas_y}" viewBox="0 0 {canvas_x} {canvas_y}">
<rect width="100%" height="100%" fill="#f6fbff"/>
<text x="34" y="38" font-family="system-ui,sans-serif" font-size="25" font-weight="900" fill="#071d36">HR-30 left-gripper nonstructural fit plate</text>
<rect x="34" y="72" width="630" height="630" fill="#fff" stroke="#0b4f91" stroke-width="3"/>
<text x="46" y="684" font-family="system-ui,sans-serif" font-size="15" fill="#142a40">140 mm conservative planning square; actual STL {summary['bbox_x_mm']:.1f} x {summary['bbox_y_mm']:.1f} x {summary['bbox_z_mm']:.1f} mm</text>
<g font-family="system-ui,sans-serif">{''.join(rectangles)}{''.join(legend)}</g>
<rect x="692" y="500" width="320" height="145" rx="12" fill="#f2b91d" stroke="#805600" stroke-width="3"/>
<text x="712" y="535" font-family="system-ui,sans-serif" font-size="17" font-weight="900" fill="#17243a">UNPOWERED FIT ARTICLE ONLY</text>
<text x="712" y="568" font-family="system-ui,sans-serif" font-size="15" fill="#17243a">No load, grasp, motion, or safety credit.</text>
<text x="712" y="596" font-family="system-ui,sans-serif" font-size="15" fill="#17243a">Slicer time/support preflight required.</text>
<text x="712" y="624" font-family="system-ui,sans-serif" font-size="15" fill="#17243a">Do not scale the submitted STL.</text>
</svg>'''
    (OUT / "bpl-submission" / "plate-layout.svg").write_text(svg + "\n", encoding="utf-8")


def build_full_fit_zip(parts: list[dict[str, str]]) -> dict:
    output = OUT / "makerspace-submission" / "HR30_complete_98_part_nonstructural_fit_check.zip"
    output.parent.mkdir(parents=True, exist_ok=True)
    included = []
    with zipfile.ZipFile(output, "w") as archive:
        readme = f"""# HR-30 complete 1:1 nonstructural fit-check bundle

{WARNING}

This bundle contains 98 bed-normalized binary STL files plus the controlled
plate, print-setting, assembly-traveler and inspection registers.  Every part
is 1:1 millimetres.  Do not scale.  No G-code or slicer profile is released;
the receiving facility must perform printer/material/support/time preflight.
"""
        zip_add_bytes(archive, "README.md", readme.encode("utf-8"))
        included.append("README.md")
        for row in sorted(parts, key=lambda item: item["part_id"]):
            source = FIT / row["stl_path"]
            name = f"stl/{row['module']}/{row['part_id']}.stl"
            zip_add_bytes(archive, name, source.read_bytes())
            included.append(name)
        for name in [
            "fit-check-part-register.csv",
            "fit-check-print-settings.csv",
            "print-build-plate-register.csv",
            "fit-check-assembly-traveler.csv",
            "fit-check-inspection-register.csv",
        ]:
            zip_add_bytes(archive, f"registers/{name}", (FIT / name).read_bytes())
            included.append(f"registers/{name}")
    return {
        "path": output.relative_to(OUT).as_posix(),
        "sha256": sha256(output),
        "bytes": output.stat().st_size,
        "stl_count": 98,
        "member_count": len(included),
    }


def build() -> dict:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    parts = read_csv(FIT / "fit-check-part-register.csv")
    if len(parts) != 98 or any(row["built_quantity"] != "0" for row in parts):
        raise RuntimeError("controlled 98-part unbuilt fit-check baseline required")

    sources = [
        {"source_id": "BFR-S01", "organization": "Boston Public Library", "scope": "current 3D-print availability and locations", "url": "https://www.bpl.org/faq/printing-copying-and-scanning/", "revision_or_date": "LIVE OFFICIAL PAGE; REVISION/DATE NOT STATED", "accessed_date": ACCESSED},
        {"source_id": "BFR-S02", "organization": "Boston Public Library", "scope": "KBLIC MakerBot Sketch limits and submission rules", "url": "https://www.bpl.org/about-the-bpl/official-policies/kirstein-business-library-innovation-center-3d-printing-guidelines/", "revision_or_date": "LIVE OFFICIAL POLICY PAGE; REVISION/DATE NOT STATED", "accessed_date": ACCESSED},
        {"source_id": "BFR-S03", "organization": "Artisans Asylum", "scope": "current Boston shop list, access paths and contact", "url": "https://www.artisansasylum.com/home", "revision_or_date": "LIVE OFFICIAL PAGE; REVISION/DATE NOT STATED", "accessed_date": ACCESSED},
        {"source_id": "BFR-S04", "organization": "Artisans Asylum", "scope": "machine-shop equipment and training state", "url": "https://wiki.artisansasylum.com/wiki/Category:Machine_Shop", "revision_or_date": "LIVE ORGANIZATION WIKI; REVISION/DATE NOT STATED", "accessed_date": ACCESSED},
        {"source_id": "BFR-S05", "organization": "Artisans Asylum", "scope": "private instruction for machining, fabrication, 3D printing and KiCad", "url": "https://www.artisansasylum.com/private-lessons", "revision_or_date": "LIVE OFFICIAL PAGE; REVISION/DATE NOT STATED", "accessed_date": ACCESSED},
        {"source_id": "BFR-S06", "organization": "Boston Makers", "scope": "local FDM/digital fabrication capability", "url": "https://www.bostonmakers.org/the-space/", "revision_or_date": "LIVE OFFICIAL PAGE; REVISION/DATE NOT STATED", "accessed_date": ACCESSED},
        {"source_id": "BFR-S07", "organization": "Mill Forge Makerspace", "scope": "south-of-Boston welding, metal, CNC and additive capability", "url": "https://millforge.org/", "revision_or_date": "LIVE OFFICIAL PAGE; REVISION/DATE NOT STATED", "accessed_date": ACCESSED},
        {"source_id": "BFR-S08", "organization": "Armstrong Machining", "scope": "Beverly prototype CNC and welding/finishing", "url": "https://www.armstrongmachining.com/", "revision_or_date": "LIVE OFFICIAL PAGE; REVISION/DATE NOT STATED", "accessed_date": ACCESSED},
        {"source_id": "BFR-S09", "organization": "True Position Machine", "scope": "prototype metal/plastic CNC and DFM from STEP/IGES/PDF", "url": "https://tpmcnc.com/rapid-prototyping-services/", "revision_or_date": "LIVE OFFICIAL PAGE; REVISION/DATE NOT STATED", "accessed_date": ACCESSED},
        {"source_id": "BFR-S10", "organization": "Borg Design", "scope": "Hudson prototype machining, additive and DFM", "url": "https://www.borgdesign.com/", "revision_or_date": "LIVE OFFICIAL PAGE; REVISION/DATE NOT STATED", "accessed_date": ACCESSED},
        {"source_id": "BFR-S11", "organization": "Tucker Engineering", "scope": "Peabody CNC machining, deburring, assembly and finishing", "url": "https://www.tuckereng.com/", "revision_or_date": "LIVE OFFICIAL PAGE; REVISION/DATE NOT STATED", "accessed_date": ACCESSED},
    ]
    write_csv(OUT / "primary-source-register.csv", sources)

    facilities = [
        {"route_id": "BFR-R01", "facility": "Boston Public Library / KBLIC", "location": "700 Boylston St, Boston", "verified_capability": "MakerBot Sketch; PLA; STL intake; 146 x 146 x 146 mm maximum; 0.10-0.40 mm resolution; tuned 0.20 mm", "access_boundary": "one build/month/person; <=7 hours; advance submission", "current_state": "TEMPORARILY UNAVAILABLE ON CURRENT KBLIC PAGE", "project_role": "one small nonstructural fit plate only after availability and slicer-time confirmation", "contact_or_entry": "BPL 3D Print Request / KBLIC", "cost_state": "NOT STATED / CONFIRM", "decision": "HOLD UNTIL SERVICE AVAILABLE", "source_ids": "BFR-S01;BFR-S02", "warning": WARNING},
        {"route_id": "BFR-R02", "facility": "Artisans Asylum", "location": "96 Holton Street, Allston, MA 02134", "verified_capability": "digital fabrication/3D printing; machine shop; metal shop; CNC plasma; electronics/robotics; ShopBot", "access_boundary": "class/day pass/membership; machine access requires applicable training/tool test", "current_state": "OPEN; EXACT MACHINE AVAILABILITY REQUIRES CONFIRMATION", "project_role": "PRIMARY LOCAL CANDIDATE for 98-part fit check, metal DFM, fixture and electronics support", "contact_or_entry": "front-desk@artisansasylum.com / 617-800-9010", "cost_state": "CLASS/DAY-PASS/MEMBERSHIP OR PRIVATE LESSON - CURRENT PRICE CONFIRMATION REQUIRED", "decision": "CONTACT / TOUR / CAPABILITY REVIEW", "source_ids": "BFR-S03;BFR-S04;BFR-S05", "warning": WARNING},
        {"route_id": "BFR-R03", "facility": "Boston Makers", "location": "105 S. Huntington Ave, Boston", "verified_capability": "LulzBot 3 and Powerspec Ultra 3D printers; laser/electronics/wood tools", "access_boundary": "membership/training; exact printer state and build envelope not published on reviewed page", "current_state": "OPEN - CONFIRM", "project_role": "SECONDARY SMALL-PRINT / ELECTRONICS WORKSPACE; NOT A VERIFIED METAL-CNC ROUTE", "contact_or_entry": "contact@bostonmakers.org / book tour", "cost_state": "MEMBERSHIP REQUIRED / CONFIRM", "decision": "CAPABILITY INQUIRY", "source_ids": "BFR-S06", "warning": WARNING},
        {"route_id": "BFR-R04", "facility": "Mill Forge Makerspace", "location": "south of Boston; exact visit route on official site", "verified_capability": "welding, metal work, FDM/resin printing, CNC laser and routers", "access_boundary": "membership/tour/training; exact metal-CNC machine/process not verified", "current_state": "OPEN - CONFIRM", "project_role": "SECONDARY MAKER / WELDING / FABRICATION CANDIDATE", "contact_or_entry": "official site tour/contact", "cost_state": "MEMBERSHIP REQUIRED / CONFIRM", "decision": "CAPABILITY INQUIRY", "source_ids": "BFR-S07", "warning": WARNING},
        {"route_id": "BFR-R05", "facility": "Armstrong Machining", "location": "Beverly, MA", "verified_capability": "prototype/low-volume CNC milling/turning; aluminum/steel/plastics; welding; finishing", "access_boundary": "commercial quotation and written DFM", "current_state": "NO CONTACT / NO QUOTE", "project_role": "LOCAL COMMERCIAL METAL RFQ CANDIDATE", "contact_or_entry": "official quote/contact page; 978-232-9466", "cost_state": "QUOTE REQUIRED", "decision": "RFQ/DFM ONLY", "source_ids": "BFR-S08", "warning": WARNING},
        {"route_id": "BFR-R06", "facility": "True Position Machine", "location": "Hampstead, NH", "verified_capability": "prototype CNC in metal/plastic; design assistance; STEP/IGES/PDF intake", "access_boundary": "commercial quotation and written DFM", "current_state": "NO CONTACT / NO QUOTE", "project_role": "REGIONAL COMMERCIAL PROTOTYPE RFQ CANDIDATE", "contact_or_entry": "official quote/contact page; 603-785-2205", "cost_state": "QUOTE REQUIRED", "decision": "RFQ/DFM ONLY", "source_ids": "BFR-S09", "warning": WARNING},
        {"route_id": "BFR-R07", "facility": "Borg Design", "location": "Hudson, MA", "verified_capability": "4/5-axis CNC; prototype machining; additive; SolidWorks/DFM", "access_boundary": "commercial quotation and written DFM", "current_state": "NO CONTACT / NO QUOTE", "project_role": "REGIONAL COMMERCIAL PRECISION/COMPLEX-PART RFQ CANDIDATE", "contact_or_entry": "official request-a-quote page", "cost_state": "QUOTE REQUIRED", "decision": "RFQ/DFM ONLY", "source_ids": "BFR-S10", "warning": WARNING},
        {"route_id": "BFR-R08", "facility": "Tucker Engineering", "location": "Peabody, MA", "verified_capability": "3/4-axis milling; turning; deburring; assembly; finishing", "access_boundary": "commercial quotation and written DFM", "current_state": "NO CONTACT / NO QUOTE", "project_role": "LOCAL COMMERCIAL MACHINED-PART / THERMAL RFQ CANDIDATE", "contact_or_entry": "info@tuckereng.com / 978-532-5900", "cost_state": "QUOTE REQUIRED", "decision": "RFQ/DFM ONLY", "source_ids": "BFR-S11", "warning": WARNING},
    ]
    write_csv(OUT / "facility-capability-register.csv", facilities)

    screen = []
    for row in parts:
        dimensions = [float(row[f"oriented_bbox_{axis}_mm"]) for axis in "xyz"]
        within = max(dimensions) <= 140.0
        screen.append({
            "part_id": row["part_id"], "module": row["module"], "role": row["role"],
            "oriented_bbox_x_mm": row["oriented_bbox_x_mm"], "oriented_bbox_y_mm": row["oriented_bbox_y_mm"], "oriented_bbox_z_mm": row["oriented_bbox_z_mm"],
            "within_project_140mm_conservative_envelope": "YES" if within else "NO",
            "bpl_7_hour_limit_verified": "NO - SLICER PREFLIGHT REQUIRED",
            "bpl_service_available": "NO - CURRENT PAGE SAYS TEMPORARILY UNAVAILABLE",
            "submission_authority": "NONE", "warning": WARNING,
        })
    write_csv(OUT / "bpl-envelope-screen.csv", screen)

    plate_rows, plate_summary = build_gripper_plate(parts)
    write_csv(OUT / "bpl-submission" / "plate-part-register.csv", plate_rows)
    layout_svg(plate_rows, plate_summary)
    submission = f"""# BPL submission candidate: HR-30 G01 gripper fit plate

{WARNING}

This is one 1:1 millimetre STL containing nine separated left-gripper parts.
Actual bounds: {plate_summary['bbox_x_mm']:.3f} x {plate_summary['bbox_y_mm']:.3f} x {plate_summary['bbox_z_mm']:.3f} mm.

- Do not scale.
- Intended material: library-standard PLA, color irrelevant.
- Development layer-height candidate: 0.20 mm.
- This is an unpowered dimensional/mechanism fit article with no load credit.
- Library staff must confirm service availability and slice time <=7 hours before accepting it.
- Support, adhesion and printer-specific settings remain the operator's decision; record them with the returned part.

The KBLIC page reviewed on {ACCESSED} says 3D printing is temporarily unavailable.
Do not submit until BPL confirms service has resumed.
"""
    (OUT / "bpl-submission" / "SUBMISSION.md").write_text(submission, encoding="utf-8")
    full_zip = build_full_fit_zip(parts)

    quote_batches = read_csv(SOURCING / "quote-batch-register.csv")
    rfq_rows = []
    for batch in quote_batches:
        rfq_rows.append({
            "batch_id": batch["quote_batch_id"],
            "batch_scope": batch["scope"],
            "part_count": batch["part_count"],
            "controlled_source_register": "hr30/whole-body-p0.1/fabrication-sourcing-p0.1/quote-batch-register.csv",
            "candidate_routes": "BFR-R05;BFR-R06;BFR-R07;BFR-R08" if "metal" in batch["scope"].lower() or "machin" in batch["scope"].lower() else "BFR-R02;BFR-R03;BFR-R04",
            "execution_state": "NO CONTACT / NO QUOTE",
            "material_tolerance_release": "OPEN",
            "authority": "RFQ/DFM CONVERSATION ONLY",
            "warning": WARNING,
        })
    write_csv(OUT / "commercial-rfq-routing.csv", rfq_rows)

    actions = [
        {"action_id": "BFR-A01", "sequence": 1, "action": "Confirm BPL 3D-print service has resumed; do not submit while current page says temporarily unavailable", "input": "BFR-R01 / current official page", "completion_evidence": "dated written availability response", "state": "OPEN", "authority": "INQUIRY ONLY", "warning": WARNING},
        {"action_id": "BFR-A02", "sequence": 2, "action": "Ask BPL to preflight the controlled G01 plate at 100% scale and reject if estimated time exceeds 7 hours", "input": plate_summary["stl_path"] + " SHA-256 " + plate_summary["stl_sha256"], "completion_evidence": "slicer screenshot/profile/time plus accepted request", "state": "OPEN", "authority": "UNPOWERED FIT ARTICLE ONLY", "warning": WARNING},
        {"action_id": "BFR-A03", "sequence": 3, "action": "Tour/contact Artisans Asylum and confirm FDM capacity for the complete 98-part bundle plus training/access requirements", "input": full_zip["path"] + " SHA-256 " + full_zip["sha256"], "completion_evidence": "dated capability response, printer/envelope/material/profile and cost", "state": "OPEN", "authority": "CAPABILITY INQUIRY ONLY", "warning": WARNING},
        {"action_id": "BFR-A04", "sequence": 4, "action": "Review the controlled five-batch metal RFQ package with Artisans machine shop or one commercial candidate", "input": "commercial-rfq-routing.csv and fabrication-sourcing-p0.1", "completion_evidence": "written DFM response with process/material/tolerance/inspection assumptions", "state": "OPEN", "authority": "RFQ/DFM ONLY", "warning": WARNING},
        {"action_id": "BFR-A05", "sequence": 5, "action": "Print, label and inspect the G01 plate before authorizing any further fit-check batch", "input": "plate-part-register.csv plus parent inspection register", "completion_evidence": "nine identified parts; photos; dimensions; fit/issue record; no powered use", "state": "OPEN", "authority": "UNPOWERED INSPECTION ONLY", "warning": WARNING},
    ]
    write_csv(OUT / "execution-action-register.csv", actions)

    holds = [
        {"hold_id": "BFR-H01", "unresolved": "BPL service currently unavailable", "evidence_required": "dated confirmation that service resumed", "state": "OPEN", "warning": WARNING},
        {"hold_id": "BFR-H02", "unresolved": "G01 plate print time/support/adhesion not sliced on the receiving printer", "evidence_required": "operator slicer preview/profile and <=7-hour result", "state": "OPEN", "warning": WARNING},
        {"hold_id": "BFR-H03", "unresolved": "makerspace access, training, exact machines and costs unconfirmed", "evidence_required": "facility responses/tour and operator qualification", "state": "OPEN", "warning": WARNING},
        {"hold_id": "BFR-H04", "unresolved": "commercial shops not contacted and no quotes/DFM received", "evidence_required": "written quote and DFM dispositions bound to exact file hashes", "state": "OPEN", "warning": WARNING},
        {"hold_id": "BFR-H05", "unresolved": "materials, tolerances/GD&T, structural allowables and inspection not released", "evidence_required": "qualified design release, drawings, material/inspection requirements and physical validation", "state": "OPEN", "warning": WARNING},
        {"hold_id": "BFR-H06", "unresolved": "zero fit-check or production parts built or inspected", "evidence_required": "as-built records and completed inspection travelers", "state": "OPEN", "warning": WARNING},
    ]
    write_csv(OUT / "open-holds.csv", holds)

    status = {
        "identifier": "HR30-BOSTON-FABRICATION-ROUTE-P0.1",
        "warning": WARNING,
        "location": "Boston, Massachusetts, USA",
        "primary_source_count": len(sources),
        "facility_route_count": len(facilities),
        "controlled_fit_check_part_count": len(parts),
        "bpl_conservative_envelope_part_count": sum(row["within_project_140mm_conservative_envelope"] == "YES" for row in screen),
        "bpl_gripper_plate_part_count": plate_summary["part_count"],
        "bpl_gripper_plate_triangle_count": plate_summary["triangle_count"],
        "bpl_gripper_plate_bbox_mm": [round(plate_summary[key], 6) for key in ["bbox_x_mm", "bbox_y_mm", "bbox_z_mm"]],
        "bpl_gripper_plate_sha256": plate_summary["stl_sha256"],
        "complete_fit_check_zip_stl_count": full_zip["stl_count"],
        "complete_fit_check_zip_sha256": full_zip["sha256"],
        "bpl_service_currently_available": False,
        "bpl_print_time_verified": False,
        "makerspace_capability_confirmed": False,
        "supplier_contact_executed": False,
        "quotes_received": False,
        "fit_check_parts_built": 0,
        "fit_check_parts_inspected": 0,
        "materials_selected": False,
        "structural_fabrication_released": False,
        "procurement_authority": False,
        "fabrication_authority": False,
        "assembly_authority": False,
        "powered_test_authority": False,
        "motion_authority": False,
        "energization_authority": False,
    }
    (OUT / "route-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    (OUT / "README.md").write_text(
        f"# HR-30 Boston fabrication route P0.1\n\n{WARNING}\n\n"
        "This package contains one BPL-envelope gripper fit plate, a complete 98-STL makerspace bundle, "
        "current Boston-area facility research, and controlled commercial RFQ routing. BPL is currently unavailable; "
        "no facility has been contacted and no quote, material, structural part or work authority is released.\n",
        encoding="utf-8",
    )
    shutil.copy2(Path(__file__), OUT / "boston-fabrication-route-source.py")
    write_web(status, plate_summary, full_zip, facilities, actions)
    integrate(status)
    manifest_and_release()
    return status


def write_web(status: dict, plate: dict, bundle: dict, facilities: list[dict], actions: list[dict]) -> None:
    facility_rows = "".join(
        f"<tr><td>{html.escape(row['facility'])}</td><td>{html.escape(row['verified_capability'])}</td><td>{html.escape(row['current_state'])}</td><td>{html.escape(row['project_role'])}</td><td>{html.escape(row['cost_state'])}</td></tr>"
        for row in facilities
    )
    action_rows = "".join(
        f"<tr><td>{row['sequence']}</td><td>{html.escape(row['action'])}</td><td>{html.escape(row['completion_evidence'])}</td><td>{html.escape(row['state'])}</td></tr>"
        for row in actions
    )
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 Boston fabrication route</title><style>
:root{{--deep:#071d36;--blue:#0b4f91;--sky:#d9f2ff;--gold:#f2b91d;--paper:#f6fbff;--ink:#142a40;--line:#91cbe7}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.55 system-ui,Segoe UI,sans-serif}}header,main,footer{{padding:clamp(24px,5vw,64px) max(18px,calc((100vw - 1280px)/2))}}header,footer{{background:linear-gradient(135deg,var(--deep),var(--blue));color:#fff}}h1{{font-size:clamp(38px,6vw,68px);line-height:1.05}}h2{{font-size:clamp(28px,4vw,42px)}}h3{{font-size:22px}}.warning{{background:var(--gold);color:#17243a;border:3px solid #805600;padding:16px;font-weight:900}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:16px}}article,.panel{{background:#fff;border:2px solid var(--line);border-radius:16px;padding:19px}}.metric{{font-size:clamp(30px,5vw,48px);font-weight:900;color:var(--blue)}}.hold{{border-color:#d39a00;background:#fff9df}}.scroll{{overflow:auto;border:2px solid var(--line);border-radius:14px;background:#fff}}table{{border-collapse:collapse;width:100%;min-width:1080px}}th,td{{padding:14px;text-align:left;vertical-align:top;border-bottom:1px solid var(--line);font-size:16px}}th{{background:var(--deep);color:#fff;position:sticky;top:0}}a{{color:#075b9b;font-weight:800}}img{{display:block;max-width:100%;height:auto;border:2px solid var(--line);border-radius:14px;background:#fff}}code{{font-size:15px}}@media(max-width:560px){{body{{font-size:16px}}}}
</style></head><body><header><div class="warning">{html.escape(WARNING)}</div><p>Boston, Massachusetts · current-source review {ACCESSED}</p><h1>The robot now has somewhere real to become physical.</h1><p>One library-sized gripper plate, one complete 98-part makerspace bundle, and eight verified local/regional facility routes connect the existing CAD to an unpowered first fit check.</p></header><main>
<section class="grid"><article><div class="metric">9 parts</div><p>one 1:1 left-gripper fit plate, {plate['bbox_x_mm']:.1f} × {plate['bbox_y_mm']:.1f} × {plate['bbox_z_mm']:.1f} mm.</p></article><article><div class="metric">98 STLs</div><p>complete body fit-check bundle with travelers and inspection records.</p></article><article><div class="metric">8 routes</div><p>library, community-shop and commercial candidates.</p></article><article class="hold"><div class="metric">0 built</div><p>no physical or structural credit yet.</p></article></section>
<section><h2>First object: the left hand</h2><div class="panel"><p>The first submission is a nine-part, nonstructural left-gripper mechanism plate. It tests the visible hand architecture before consuming a whole-body print queue. It is 100% scale and contains no G-code.</p><img src="bpl-submission/plate-layout.svg" alt="Layout of nine HR-30 left gripper fit parts"><p><a href="bpl-submission/HR30_G01_gripper_fit_plate_nonstructural.stl">Download the controlled STL</a> · <a href="bpl-submission/SUBMISSION.md">Read the submission note</a> · SHA-256 <code>{plate['stl_sha256']}</code></p><div class="warning">BPL's current KBLIC page says 3D printing is temporarily unavailable. Confirm service has resumed and the sliced job is at most seven hours before submission.</div></div></section>
<section><h2>Complete makerspace handoff</h2><div class="panel"><p><a href="{bundle['path']}">Download the 98-part fit-check ZIP</a> ({bundle['bytes']/1_000_000:.1f} MB). It contains all bed-normalized STLs, print settings, 22 build-plate records, the 54-step assembly traveler and 392 inspection records. It deliberately contains no G-code.</p><p>SHA-256 <code>{bundle['sha256']}</code></p></div></section>
<section><h2>Where each job can go</h2><div class="scroll"><table><thead><tr><th>Facility</th><th>Verified capability</th><th>Current state</th><th>Project role</th><th>Cost</th></tr></thead><tbody>{facility_rows}</tbody></table></div></section>
<section><h2>Execution sequence</h2><div class="scroll"><table><thead><tr><th>#</th><th>Action</th><th>Completion evidence</th><th>State</th></tr></thead><tbody>{action_rows}</tbody></table></div></section>
<section><h2>Controlled records</h2><div class="panel"><p><a href="facility-capability-register.csv">Facility capabilities</a> · <a href="primary-source-register.csv">Primary sources</a> · <a href="bpl-envelope-screen.csv">98-part library envelope screen</a> · <a href="commercial-rfq-routing.csv">Commercial RFQ routing</a> · <a href="open-holds.csv">Open evidence</a>.</p></div></section>
</main><footer>{html.escape(WARNING)}</footer></body></html>'''
    (OUT / "index.html").write_text(page + "\n", encoding="utf-8")


def replace_marked(text: str, start: str, end: str, block: str) -> str:
    if start in text:
        left = text.index(start)
        right = text.index(end, left) + len(end)
        return text[:left] + block + text[right:]
    return text.rstrip() + "\n\n" + block + "\n"


def integrate(status: dict) -> None:
    readme_path = WB / "README.md"
    readme = readme_path.read_text(encoding="utf-8")
    start = "<!-- HR30-BOSTON-FABRICATION-ROUTE-P01-START -->"
    end = "<!-- HR30-BOSTON-FABRICATION-ROUTE-P01-END -->"
    block = f'''{start}
## Boston fabrication execution route P0.1

The [interactive Boston fabrication route](boston-fabrication-route-p0.1/index.html) packages a nine-part, 1:1 left-gripper fit plate and the complete 98-STL body fit check for real facilities. Eight current official facility routes are recorded. Boston Public Library printing is currently unavailable; no facility contact, quote, material selection, structural fabrication, or work authority is claimed.
{end}'''
    readme_path.write_text(replace_marked(readme, start, end, block), encoding="utf-8")

    index_path = WB / "index.html"
    page = index_path.read_text(encoding="utf-8")
    start = "<!-- HR30-BOSTON-FABRICATION-ROUTE-P01-START -->"
    end = "<!-- HR30-BOSTON-FABRICATION-ROUTE-P01-END -->"
    section = f'''{start}<section id="boston-fabrication"><h2>The first physical handoff is ready</h2><div class="grid"><article class="card pass"><div class="metric">9 parts</div><p>one BPL-envelope left-gripper fit plate at 1:1 scale.</p></article><article class="card pass"><div class="metric">98 STLs</div><p>one complete makerspace fit-check bundle with assembly and inspection travelers.</p></article><article class="card pass"><div class="metric">8 routes</div><p>current Boston-area maker and commercial candidates.</p></article><article class="card hold"><div class="metric">0 built</div><p>BPL is temporarily unavailable; no quote or physical result exists.</p></article></div><p><a href="boston-fabrication-route-p0.1/index.html">Open the Boston fabrication execution guide</a>.</p></section>{end}'''
    if start in page:
        page = replace_marked(page, start, end, section)
    else:
        anchor = "<!-- HR30-FABRICATION-SOURCING-P01-END -->"
        if anchor not in page:
            raise RuntimeError("fabrication sourcing section anchor missing")
        page = page.replace(anchor, anchor + section, 1)
    index_path.write_text(page, encoding="utf-8")

    root_path = ROOT / "index.html"
    root_page = root_path.read_text(encoding="utf-8")
    link = '<li><a href="hr30/whole-body-p0.1/boston-fabrication-route-p0.1/index.html">Boston fabrication execution route</a></li>'
    if link not in root_page:
        anchor = '<li><a href="hr30/whole-body-p0.1/fabrication-sourcing-p0.1/index.html">Fabrication sourcing and RFQ guide</a></li>'
        if anchor not in root_page:
            raise RuntimeError("root fabrication sourcing link missing")
        root_page = root_page.replace(anchor, anchor + link, 1)
        root_path.write_text(root_page, encoding="utf-8")

    status_path = WB / "package-status.json"
    package_status = json.loads(status_path.read_text(encoding="utf-8"))
    package_status.update({
        "boston_fabrication_route_present": True,
        "boston_fabrication_facility_route_count": status["facility_route_count"],
        "boston_bpl_gripper_plate_part_count": status["bpl_gripper_plate_part_count"],
        "boston_complete_fit_check_zip_stl_count": status["complete_fit_check_zip_stl_count"],
        "boston_bpl_service_currently_available": False,
        "boston_fabrication_supplier_contact_executed": False,
        "boston_fit_check_parts_built": 0,
        "boston_fabrication_authority": False,
    })
    status_path.write_text(json.dumps(package_status, indent=2) + "\n", encoding="utf-8")


def manifest_and_release() -> None:
    manifest = OUT / "file-manifest.csv"
    if manifest.exists():
        manifest.unlink()
    rows = [
        {"path": path.relative_to(OUT).as_posix(), "bytes": path.stat().st_size, "sha256": sha256(path), "warning": WARNING}
        for path in sorted(OUT.rglob("*")) if path.is_file()
    ]
    write_csv(manifest, rows)
    if RELEASE.exists():
        shutil.rmtree(RELEASE)
    shutil.copytree(OUT, RELEASE)
    import generate_hr30_system_package_p01 as system
    system.refresh_manifest_and_release()


def main() -> int:
    status = build()
    print(json.dumps(status, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
