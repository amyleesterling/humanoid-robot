"""Reconcile legacy joint-hardware envelopes to the HR-30 successor design.

This stage runs after transmission closure.  It makes the manufacturing
register agree with the installed whole-body design without granting any
procurement or fabrication authority.
"""

from __future__ import annotations

import csv
import hashlib
import html
import json
import shutil
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WHOLE = ROOT / "hr30" / "whole-body-p0.1"
JOINT = WHOLE / "joint-hardware-manufacturing-p0.1"
TRANSMISSION = WHOLE / "transmission-closure-p0.1"
OUT = WHOLE / "joint-hardware-successor-reconciliation-p0.1"
RELEASE_ROOT = ROOT / "release" / "hr30" / "whole-body-p0.1"
RELEASE = RELEASE_ROOT / OUT.name
IDENTIFIER = "HR30-JOINT-HARDWARE-SUCCESSOR-RECONCILIATION-P0.1"
WARNING = "PRELIMINARY - JOINT-HARDWARE SUCCESSOR CANDIDATES ONLY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, POWERED TESTING, MOTION, OR ENERGIZATION"
LEGACY_TYPES = {
    "MOTOR_PULLEY_ENVELOPE",
    "OUTPUT_PULLEY_ENVELOPE",
    "ACTUATOR_OUTPUT_COUPLER_PLACEHOLDER",
    "SYMMETRIC_DRIVE_COUPLER_PLACEHOLDER",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        raise RuntimeError(f"refusing empty CSV: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def candidate_class(row: dict[str, str]) -> str:
    if "PULLEY" in row["predecessor_part_type"]:
        return "CATALOGUE PRODUCT CANDIDATE"
    if "GRIPPER" in row["axis_id"]:
        return "EDITABLE DETAILED HAND MECHANISM"
    return "EDITABLE CUSTOM DIRECT ADAPTER"


def exact_successor(row: dict[str, str]) -> str:
    if "PULLEY" not in row["predecessor_part_type"]:
        return row["successor"]
    if "SHOULDER" in row["axis_id"]:
        return "GPA20GT5090-A-P10"
    kind = "MOTOR_PULLEY" if row["predecessor_part_type"] == "MOTOR_PULLEY_ENVELOPE" else "OUTPUT_PULLEY"
    expected = f"{row['axis_id']}_{kind}"
    installed = read_csv(WHOLE / "leg-drivetrain-installation-p0.1" / "installed-component-register.csv")
    matches = [item for item in installed if item["part_id"] == expected]
    if len(matches) != 1:
        raise RuntimeError(f"cannot resolve exact installed pulley candidate {expected}")
    return matches[0]["note"].split(";", 1)[0]


def source_artifacts(row: dict[str, str]) -> tuple[str, str, str]:
    cls = candidate_class(row)
    successor = row["successor"]
    if cls == "CATALOGUE PRODUCT CANDIDATE":
        if "SHOULDER" in row["axis_id"]:
            return (
                "transmission-closure-p0.1/shoulder-drive-register.csv",
                "PURCHASE CANDIDATE; DO NOT FABRICATE LEGACY ENVELOPE",
                "order code recorded; vendor tooth B-Rep and received identity not claimed",
            )
        return (
            "leg-drivetrain-p0.1/candidate-product-register.csv;leg-drivetrain-installation-p0.1/installed-component-register.csv",
            "PURCHASE CANDIDATE; DO NOT FABRICATE LEGACY ENVELOPE",
            "order code recorded; exact received product and application remain open",
        )
    if cls == "EDITABLE DETAILED HAND MECHANISM":
        return (
            "grippers-p0.1/parts/PINION.step;grippers-p0.1/parts/RACK_POSITIVE.step;grippers-p0.1/parts/RACK_NEGATIVE.step",
            "CUSTOM FABRICATION CANDIDATE AFTER DFM/FAI; DO NOT FABRICATE LEGACY COUPLER",
            "three editable STEP parts replace one abstract symmetric-drive envelope",
        )
    return (
        f"transmission-closure-p0.1/parts/{successor}.step;transmission-closure-p0.1/drawings/{successor}.svg",
        "CUSTOM MACHINING CANDIDATE AFTER DFM/FAI; DO NOT FABRICATE LEGACY COUPLER",
        "editable blind-bore split-clamp adapter; fits, material, fastener and proof open",
    )


def build_binding() -> list[dict[str, str]]:
    dispositions = read_csv(TRANSMISSION / "transmission-disposition-register.csv")
    if len(dispositions) != 39 or len({r["predecessor_part_id"] for r in dispositions}) != 39:
        raise RuntimeError("transmission disposition is not 39 unique predecessor rows")
    bindings: list[dict[str, str]] = []
    for row in dispositions:
        if row["predecessor_part_type"] not in LEGACY_TYPES:
            raise RuntimeError(f"unexpected predecessor type: {row['predecessor_part_type']}")
        cls = candidate_class(row)
        row = dict(row)
        row["successor"] = exact_successor(row)
        artifacts, route, note = source_artifacts(row)
        for rel in artifacts.split(";"):
            if not (WHOLE / rel).is_file():
                raise RuntimeError(f"missing successor evidence {rel}")
        bindings.append({
            "predecessor_part_id": row["predecessor_part_id"],
            "axis_id": row["axis_id"],
            "predecessor_part_type": row["predecessor_part_type"],
            "predecessor_authoritative": "NO",
            "predecessor_disposition": "SUPERSEDED - DO NOT FABRICATE",
            "successor": row["successor"],
            "successor_class": cls,
            "authoritative_source_artifacts": artifacts,
            "manufacturing_or_procurement_route": route,
            "successor_candidate_geometry_or_order_code_present": "YES",
            "successor_selected_for_procurement": "NO",
            "successor_released_for_fabrication": "NO",
            "remaining_evidence": row["remaining_validation"],
            "mapping_note": note,
            "authority": "NO PROCUREMENT, FABRICATION, ASSEMBLY, POWERED TEST, MOTION OR ENERGIZATION AUTHORITY",
            "warning": WARNING,
        })
    return sorted(bindings, key=lambda item: item["predecessor_part_id"])


def reconcile_joint_register(bindings: list[dict[str, str]]) -> None:
    by_id = {row["predecessor_part_id"]: row for row in bindings}
    rows = read_csv(JOINT / "joint-hardware-part-register.csv")
    found = 0
    for row in rows:
        binding = by_id.get(row["part_id"])
        if not binding:
            continue
        found += 1
        row["material_or_product_candidate"] = binding["successor"]
        if binding["successor_class"] == "CATALOGUE PRODUCT CANDIDATE":
            row["catalogue_candidate"] = binding["successor"].split(" / ")[0]
        row["route"] = binding["manufacturing_or_procurement_route"]
        row["disposition"] = "SUPERSEDED PREDECESSOR - SEE SUCCESSOR RECONCILIATION; DO NOT FABRICATE"
        row["release_state"] = "PREDECESSOR WITHHELD; SUCCESSOR CANDIDATE BOUND; SELECTION/VALIDATION/RELEASE OPEN"
    if found != 39:
        raise RuntimeError(f"expected to reconcile 39 joint rows; found {found}")
    write_csv(JOINT / "joint-hardware-part-register.csv", rows)

    features = read_csv(JOINT / "joint-hardware-feature-register.csv")
    touched: set[str] = set()
    for row in features:
        if row["part_id"] in by_id:
            touched.add(row["part_id"])
            row["candidate_requirement"] = f"legacy geometry superseded; use {by_id[row['part_id']]['successor']} and close listed validation evidence"
            row["state"] = "SUPERSEDED PREDECESSOR - SUCCESSOR CANDIDATE BOUND; RELEASE OPEN"
    if touched != set(by_id):
        raise RuntimeError("feature register does not cover all 39 predecessor items")
    write_csv(JOINT / "joint-hardware-feature-register.csv", features)

    status_path = JOINT / "joint-hardware-manufacturing-status.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    status.update({
        "redesign_required_count": 0,
        "predecessor_superseded_count": 39,
        "unmapped_predecessor_count": 0,
        "successor_candidate_binding_count": 39,
        "successor_validation_open_count": 39,
        "successor_procurement_selection_count": 0,
        "successor_fabrication_release_count": 0,
        "successor_reconciliation_identifier": IDENTIFIER,
    })
    status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")

    readme_path = JOINT / "README.md"
    readme = readme_path.read_text(encoding="utf-8")
    readme = readme.replace(
        "It intentionally withholds supplier files for 39 catalogue bearing envelopes and 39 incomplete pulley/coupler definitions.",
        "It intentionally withholds supplier files for 39 catalogue bearing envelopes. The 39 legacy pulley/coupler envelopes are superseded and bound through the successor reconciliation; none is a supplier-upload part, and all successor validation/release gates remain open.",
    )
    readme_path.write_text(readme, encoding="utf-8")

    page_path = JOINT / "index.html"
    page = page_path.read_text(encoding="utf-8")
    replacements = {
        "catalogue and incomplete geometry is stopped before supplier upload": "catalogue items and superseded predecessors are stopped before supplier upload",
        "pulley and coupler definitions blocked for redesign": "legacy pulley/coupler envelopes superseded; successor validation open",
        "It deliberately withholds supplier files for 28 toothless pulley envelopes, 11 coupling placeholders and 39 catalogue bearing envelopes.": "It withholds supplier files for 39 catalogue bearing envelopes and all 39 legacy pulley/coupler predecessors. The successor reconciliation binds each predecessor to a physical candidate without releasing it.",
        "REDESIGN REQUIRED - ACTUATOR/HORN/CLAMP INTERFACE ABSENT": "SUPERSEDED PREDECESSOR - SEE SUCCESSOR RECONCILIATION; DO NOT FABRICATE",
        "REDESIGN REQUIRED - SMOOTH ENVELOPE HAS NO TIMING TEETH OR FLANGES": "SUPERSEDED PREDECESSOR - SEE SUCCESSOR RECONCILIATION; DO NOT FABRICATE",
    }
    for old, new in replacements.items():
        page = page.replace(old, new)
    page_path.write_text(page, encoding="utf-8")


def render_page(bindings: list[dict[str, str]]) -> str:
    table_rows = "".join(
        "<tr>" + "".join(f"<td>{html.escape(row[key])}</td>" for key in (
            "axis_id", "predecessor_part_id", "successor", "successor_class",
            "manufacturing_or_procurement_route", "remaining_evidence",
        )) + "</tr>" for row in bindings
    )
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 joint-hardware successor reconciliation</title><style>
body{{margin:0;background:#eef8ff;color:#08254f;font:17px/1.55 system-ui,sans-serif}}header,main{{max-width:1320px;margin:auto;padding:28px}}header{{background:#8ed8ff;border-bottom:5px solid #f2b705}}h1{{font-size:clamp(2rem,5vw,4rem);line-height:1.05;margin:.3em 0}}h2{{font-size:clamp(1.5rem,3vw,2.4rem)}}.warning{{background:#08254f;color:white;padding:16px;font-size:16px;font-weight:700}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px}}.card{{background:white;border:2px solid #135da8;border-radius:14px;padding:18px;box-shadow:5px 5px 0 #f2b705}}.metric{{font-size:2.3rem;font-weight:800}}.tablewrap{{overflow:auto;background:white;border:2px solid #135da8;border-radius:12px}}table{{border-collapse:collapse;width:100%;min-width:1100px;font-size:16px}}th,td{{padding:12px;text-align:left;vertical-align:top;border-bottom:1px solid #9bc9e8}}th{{background:#08254f;color:white;position:sticky;top:0}}a{{color:#064f9c;font-weight:700}}code{{font-size:14px}}@media(max-width:700px){{header,main{{padding:18px}}}}
</style></head><body><div class="warning">{html.escape(WARNING)}</div><header><p>HR-30 · Whole-body P0.1</p><h1>One manufacturing truth for every transmission interface.</h1><p>The old smooth pulleys and generic couplers are retained only as historical packaging evidence. Every one now points to a physical successor candidate.</p></header><main><section class="grid"><article class="card"><div class="metric">39 / 39</div><p>legacy predecessor items mapped and superseded</p></article><article class="card"><div class="metric">28</div><p>pulley positions bound to catalogue product candidates</p></article><article class="card"><div class="metric">9 + 2</div><p>direct-adapter axes plus detailed hand mechanisms</p></article><article class="card"><div class="metric">0</div><p>procurement selections or fabrication releases</p></article></section><h2>Authoritative crosswalk</h2><p><a href="successor-manufacturing-binding.csv">Download the complete CSV</a> · <a href="reconciliation-status.json">Status and authority boundary</a></p><div class="tablewrap"><table><thead><tr><th>Axis</th><th>Superseded predecessor</th><th>Successor</th><th>Class</th><th>Route</th><th>Evidence still required</th></tr></thead><tbody>{table_rows}</tbody></table></div><h2>What this closes—and what it does not</h2><p>This closes the configuration contradiction: no legacy pulley/coupler envelope is an authoritative manufacturing part, and none remains unmapped. It does not select a supplier item, release a custom part, validate load or life, approve a fit, or authorize physical work.</p></main></body></html>'''


def replace_marked(path: Path, marker: str, content: str, anchor: str) -> None:
    text = path.read_text(encoding="utf-8")
    start = f"<!-- {marker}-START -->"
    end = f"<!-- {marker}-END -->"
    block = f"{start}{content}{end}"
    if start in text:
        before, rest = text.split(start, 1)
        _, after = rest.split(end, 1)
        text = before + block + after
    else:
        if anchor not in text:
            raise RuntimeError(f"anchor not found in {path}: {anchor}")
        text = text.replace(anchor, anchor + block, 1)
    path.write_text(text, encoding="utf-8")


def integrate(bindings: list[dict[str, str]]) -> None:
    status_path = WHOLE / "package-status.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    status.update({
        "joint_hardware_redesign_required_count": 0,
        "joint_hardware_predecessor_superseded_count": 39,
        "joint_hardware_unmapped_predecessor_count": 0,
        "joint_hardware_successor_candidate_binding_count": 39,
        "joint_hardware_successor_validation_open_count": 39,
        "joint_hardware_successor_procurement_selection_count": 0,
        "joint_hardware_successor_fabrication_release_count": 0,
        "joint_hardware_successor_reconciliation_present": True,
    })
    status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")

    holds = read_csv(WHOLE / "open-holds.csv")
    updates = {
        "HR30-P01-H01": "All 39 base-architecture pulley/coupler placeholders are superseded and have named successor artifacts: 28 catalogue pulley positions, nine direct-adapter axes and two detailed rack-and-pinion hands. Zero predecessors remain authoritative or unmapped. The 39 catalogue bearing envelopes and 156 carrier screws remain candidates. Product receipt, material, fit, tolerance, retention, load/life, DFM, FAI and physical proof remain open for all 39 successors and associated hardware.",
        "HR30-P01-H06": "The manufacturing universe separates 98 body/frame/hand candidates, 142 actual-axis joint-hardware items and a 39-row successor crosswalk. The body set has controlled STEP/SVG files, 45 DXFs, 24 cover STLs and five nonempty pre-RFQ batches. The 39 legacy pulley/coupler envelopes are withheld and superseded, not incomplete parts. Sixty-four shaft/carrier refinement solids and 39 carrier DXFs remain candidates; exact materials, tolerances, threads, DFM, FAI, structural proof and qualified review remain open.",
        "HR30-P01-H10": "Whole-body, module and actual-axis geometry includes twelve module-specific fabrication/integration STEP pairs, individual candidate files for all 98 physical fabrication parts, and 64 real current joint shaft/carrier solids. All 39 legacy pulley/coupler envelopes have bound successors and are marked DO NOT FABRICATE. No successor is selected for procurement or released for fabrication; drawings, fits, materials/processes, exact hardware, DFM, FAI, proof, physical test and qualified review remain open.",
    }
    for row in holds:
        if row["hold_id"] in updates:
            row["unresolved_item"] = updates[row["hold_id"]]
    write_csv(WHOLE / "open-holds.csv", holds)

    readme = WHOLE / "README.md"
    text = readme.read_text(encoding="utf-8")
    heading = "## Joint-hardware successor reconciliation"
    section = (
        f"\n{heading}\n\nThe [successor reconciliation guide](joint-hardware-successor-reconciliation-p0.1/index.html) "
        "establishes one manufacturing truth for the 39 legacy pulley/coupler envelopes. All are superseded and mapped to 28 catalogue pulley positions, nine direct-adapter axes or two detailed hand mechanisms. Zero legacy envelopes remain authoritative or unmapped, but all successor selection, release and physical validation gates remain open.\n"
    )
    if heading in text:
        before, rest = text.split(heading, 1)
        next_heading = rest.find("\n## ")
        text = before + section.lstrip("\n") + (rest[next_heading:] if next_heading >= 0 else "")
    else:
        text += section
    readme.write_text(text, encoding="utf-8")

    web_section = '''<section id="joint-hardware-successors"><h2>Legacy transmission envelopes now point to real successors</h2><div class="grid"><article class="card pass"><div class="metric">39 / 39</div><p>old pulley/coupler records are mapped and superseded.</p></article><article class="card pass"><div class="metric">28 + 9 + 2</div><p>catalogue pulley positions, direct-adapter axes and detailed hands.</p></article><article class="card"><div class="metric">0</div><p>unmapped or still-authoritative predecessors.</p></article><article class="card hold"><h3>Release remains open</h3><p>No successor is selected for procurement or released for fabrication.</p></article></div><p><a href="joint-hardware-successor-reconciliation-p0.1/index.html">Open the successor crosswalk</a> · <a href="joint-hardware-successor-reconciliation-p0.1/successor-manufacturing-binding.csv">39-row binding register</a>.</p></section>'''
    anchor = "<!-- HR30-TRANSMISSION-CLOSURE-P01-END -->"
    replace_marked(WHOLE / "index.html", "HR30-JOINT-SUCCESSOR-RECONCILIATION-P01", web_section, anchor)
    root_page = ROOT / "index.html"
    root_text = root_page.read_text(encoding="utf-8")
    link = '          <li><a href="hr30/whole-body-p0.1/joint-hardware-successor-reconciliation-p0.1/index.html">Joint-hardware successor manufacturing crosswalk</a></li>\n'
    if link not in root_text:
        root_anchor = '          <li><a href="hr30/whole-body-p0.1/transmission-closure-p0.1/index.html">Whole-body transmission closure and successor assembly</a></li>\n'
        if root_anchor not in root_text:
            raise RuntimeError("top-level site transmission link anchor missing")
        root_text = root_text.replace(root_anchor, root_anchor + link, 1)
        root_page.write_text(root_text, encoding="utf-8")


def write_manifest(package: Path) -> None:
    rows = []
    for path in sorted(p for p in package.rglob("*") if p.is_file() and p.name != "file-manifest.csv"):
        rows.append({"path": path.relative_to(package).as_posix(), "bytes": str(path.stat().st_size), "sha256": sha(path), "warning": WARNING})
    write_csv(package / "file-manifest.csv", rows)


def refresh_joint_manifest_and_release() -> None:
    base_warning = json.loads((JOINT / "joint-hardware-manufacturing-status.json").read_text(encoding="utf-8"))["warning"]
    rows = []
    for path in sorted(p for p in JOINT.rglob("*") if p.is_file() and p.name != "file-manifest.csv"):
        rows.append({"path": path.relative_to(JOINT).as_posix(), "bytes": str(path.stat().st_size), "sha256": sha(path), "warning": base_warning})
    write_csv(JOINT / "file-manifest.csv", rows)
    target = RELEASE_ROOT / JOINT.name
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(JOINT, target)


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    bindings = build_binding()
    reconcile_joint_register(bindings)
    counts = Counter(row["successor_class"] for row in bindings)
    write_csv(OUT / "successor-manufacturing-binding.csv", bindings)
    write_csv(OUT / "successor-class-summary.csv", [
        {"successor_class": key, "predecessor_positions": str(value), "selected_for_procurement": "0", "released_for_fabrication": "0", "warning": WARNING}
        for key, value in sorted(counts.items())
    ])
    source_paths = [
        TRANSMISSION / "transmission-disposition-register.csv",
        TRANSMISSION / "direct-adapter-part-register.csv",
        TRANSMISSION / "shoulder-drive-register.csv",
        WHOLE / "leg-drivetrain-p0.1" / "candidate-product-register.csv",
        WHOLE / "grippers-p0.1" / "gripper-part-register.csv",
        JOINT / "joint-hardware-part-register.csv",
    ]
    (OUT / "source-binding.json").write_text(json.dumps({
        "identifier": IDENTIFIER,
        "generator": Path(__file__).relative_to(ROOT).as_posix(),
        "generator_sha256": sha(Path(__file__)),
        "sources": [{"path": path.relative_to(ROOT).as_posix(), "sha256": sha(path)} for path in source_paths],
        "warning": WARNING,
    }, indent=2) + "\n", encoding="utf-8")
    (OUT / "reconciliation-status.json").write_text(json.dumps({
        "identifier": IDENTIFIER,
        "predecessor_count": 39,
        "predecessor_authoritative_count": 0,
        "predecessor_superseded_count": 39,
        "unmapped_predecessor_count": 0,
        "successor_candidate_binding_count": 39,
        "catalogue_product_candidate_positions": counts["CATALOGUE PRODUCT CANDIDATE"],
        "editable_custom_direct_adapter_axes": counts["EDITABLE CUSTOM DIRECT ADAPTER"],
        "editable_detailed_hand_mechanisms": counts["EDITABLE DETAILED HAND MECHANISM"],
        "successor_validation_open_count": 39,
        "procurement_selection_count": 0,
        "fabrication_release_count": 0,
        "complete_joint_hardware_manufacturing_definition": False,
        "procurement_authority": False,
        "fabrication_authority": False,
        "assembly_authority": False,
        "powered_test_authority": False,
        "motion_authority": False,
        "energization_authority": False,
        "warning": WARNING,
    }, indent=2) + "\n", encoding="utf-8")
    (OUT / "README.md").write_text(f"# HR-30 joint-hardware successor reconciliation P0.1\n\n{WARNING}\n\nThis package binds all 39 legacy pulley/coupler envelopes to physical successor candidates. The old shapes are not manufacturing parts. No successor is selected or released. See `successor-manufacturing-binding.csv`.\n", encoding="utf-8")
    (OUT / "index.html").write_text(render_page(bindings), encoding="utf-8")
    integrate(bindings)
    refresh_joint_manifest_and_release()
    write_manifest(OUT)
    if RELEASE.exists():
        shutil.rmtree(RELEASE)
    shutil.copytree(OUT, RELEASE)
    import generate_hr30_system_package_p01 as system
    system.refresh_manifest_and_release()
    print("PASS: 39 legacy joint-hardware envelopes superseded and bound to 28 catalogue pulley positions, 9 direct-adapter axes and 2 detailed hands; all release authority false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
