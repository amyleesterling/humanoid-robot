"""Generate the R160 P0.3 carrier harness interface-control package."""

from __future__ import annotations

import csv
import hashlib
import html
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENG = ROOT / "electrical" / "harness" / "hr-v0-dxl-protection-carrier-harness-p0.1"
OUT = ROOT / "release" / "hr-v0" / "dxl-protection-carrier-harness-p0.1"
IDENTIFIER = "HR-V0-DXL-PROT-CARRIER-HARNESS-P0.1"
WARNING = (
    "PRELIMINARY - NOT APPROVED FOR SUPPLIER UPLOAD, QUOTATION, PROCUREMENT, "
    "FABRICATION, ASSEMBLY, CONNECTION, MOTION, OR ENERGIZATION"
)
SOURCES = {
    "electrical/kicad/hr-v0-dxl-protection-carrier-p0.3/terminal-schedule.csv": ROOT / "electrical" / "kicad" / "hr-v0-dxl-protection-carrier-p0.3" / "terminal-schedule.csv",
    "electrical/kicad/hr-v0-dxl-protection-carrier-p0.3/bom.csv": ROOT / "electrical" / "kicad" / "hr-v0-dxl-protection-carrier-p0.3" / "bom.csv",
    "electrical/kicad/hr-v0-dxl-star/connector-schedule.csv": ROOT / "electrical" / "kicad" / "hr-v0-dxl-star" / "connector-schedule.csv",
    "electrical/kicad/project-button-v3/connector-schedule.csv": ROOT / "electrical" / "kicad" / "project-button-v3" / "connector-schedule.csv",
}


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(value)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def reset_dir(path: Path, expected_parent: Path, expected_name: str) -> None:
    if path.exists():
        resolved = path.resolve()
        if resolved.parent != expected_parent.resolve() or resolved.name != expected_name:
            raise RuntimeError(f"refusing to replace unexpected path: {resolved}")
        shutil.rmtree(resolved)
    path.mkdir(parents=True)


def main() -> None:
    for source in SOURCES.values():
        if not source.is_file():
            raise FileNotFoundError(source)
    reset_dir(ENG, ROOT / "electrical" / "harness", ENG.name)
    reset_dir(OUT, ROOT / "release" / "hr-v0", OUT.name)

    source_rows = [
        {"source_id": "CHS-001", "manufacturer": "JST", "document": "VH connector English catalog eVH.pdf", "revision_or_date": "current catalog asset; accessed 2026-08-09", "url": "https://www.jst-mfg.com/product/pdf/eng/eVH.pdf", "controlled_fact": "B2P-VH mates within the VH family; VHR-2N housing; SVH-21T-P1.1 supports AWG 22 to 18 / 0.33 to 0.83 mm2 and 1.7 to 3.0 mm insulation OD; AP-K2N/MKS-L/APLMK SVH21-11 catalog tooling chain", "not_proved": "strip length, crimp height, pull-force acceptance, hand-tool identity, application derating, assembled thermal suitability or project approval", "warning": WARNING},
        {"source_id": "CHS-002", "manufacturer": "JST", "document": "VH connector live product profile", "revision_or_date": "live page; accessed 2026-08-09", "url": "https://www.jst-mfg.com/product/index.php?lang=2&series=262", "controlled_fact": "3.96 mm VH series; secure lock; VHR-2N and SVH-21T-P1.1 listed; 7 A statement applies to AWG 18 with shrouded header conditions", "not_proved": "Project Button current rating, pulse allowance, bundling/ambient derating, mating retention under robot motion or approval to connect", "warning": WARNING},
        {"source_id": "CHS-003", "manufacturer": "JST", "document": "Handling Precautions for Terminals and Connectors", "revision_or_date": "official English asset; accessed 2026-08-09", "url": "https://www.jst-mfg.com/product/pdf/eng/handling_e.pdf", "controlled_fact": "use within ratings; validate equipment suitability; connector is not a structural member; use controlled harness processing", "not_proved": "application acceptance or safety function", "warning": WARNING},
        {"source_id": "CHS-004", "manufacturer": "Belden", "document": "9918 live product record", "revision_or_date": "revision 0.515 dated 2026-02-20; accessed 2026-08-09", "url": "https://www.belden.com/products/cable/electronic-wire-cable/lead-wire-hook-up-wire/9918", "controlled_fact": "18 AWG 16x30 tinned-copper PVC wire; nominal OD 2.0 mm; 9918 002100 red and 9918 010100 black are active 100 ft item identities", "not_proved": "installed ampacity, voltage drop, flex life, abrasion, route, bundling, fault clearing or connector thermal suitability", "warning": WARNING},
    ]

    bom_rows = [
        {"item_id": "CHB-001", "manufacturer": "JST", "manufacturer_part_number": "VHR-2N", "description": "2-circuit VH mating housing", "quantity_per_single_channel_evaluation_set": "3", "status": "EXACT CANDIDATE; RECEIVING AND APPLICATION HOLD", "evidence": "CHS-001/CHS-002", "warning": WARNING},
        {"item_id": "CHB-002", "manufacturer": "JST", "manufacturer_part_number": "SVH-21T-P1.1", "description": "tin-plated crimp contact for AWG 22 to 18", "quantity_per_single_channel_evaluation_set": "6 plus process scrap SELECTION REQUIRED", "status": "EXACT CANDIDATE; CRIMP PROCESS HOLD", "evidence": "CHS-001", "warning": WARNING},
        {"item_id": "CHB-003", "manufacturer": "Belden", "manufacturer_part_number": "9918 002100", "description": "18 AWG 16x30 red PVC hook-up wire, 100 ft", "quantity_per_single_channel_evaluation_set": "CUT LENGTH SELECTION REQUIRED", "status": "EXACT CANDIDATE; ROUTE/THERMAL HOLD", "evidence": "CHS-004", "warning": WARNING},
        {"item_id": "CHB-004", "manufacturer": "Belden", "manufacturer_part_number": "9918 010100", "description": "18 AWG 16x30 black PVC hook-up wire, 100 ft", "quantity_per_single_channel_evaluation_set": "CUT LENGTH SELECTION REQUIRED", "status": "EXACT CANDIDATE; ROUTE/THERMAL HOLD", "evidence": "CHS-004", "warning": WARNING},
        {"item_id": "CHB-005", "manufacturer": "JST", "manufacturer_part_number": "AP-K2N + MKS-L + APLMK SVH21-11", "description": "catalog crimping-machine/applicator chain for SVH-21T-P1.1", "quantity_per_single_channel_evaluation_set": "PROCESS EQUIPMENT - NOT A RELEASED PURCHASE", "status": "OFFICIAL MACHINE CHAIN; PROVIDER/PROCESS SELECTION REQUIRED", "evidence": "CHS-001", "warning": WARNING},
        {"item_id": "CHB-006", "manufacturer": "SELECTION REQUIRED", "manufacturer_part_number": "SELECTION REQUIRED", "description": "fuse-holder/source-side termination for HAR-CIN end A", "quantity_per_single_channel_evaluation_set": "1 interface", "status": "SELECTION REQUIRED", "evidence": "F1/F2/F3 exact holder and terminal remain unresolved", "warning": WARNING},
        {"item_id": "CHB-007", "manufacturer": "SELECTION REQUIRED", "manufacturer_part_number": "SELECTION REQUIRED", "description": "labels, strain relief, abrasion protection and tie-down hardware", "quantity_per_single_channel_evaluation_set": "SELECTION REQUIRED", "status": "SELECTION REQUIRED", "evidence": "physical route and enclosure placement required", "warning": WARNING},
    ]

    interface_rows = [
        {"harness_id": "HAR-CIN", "end": "A", "mate_or_reference": "F1/F2/F3 protected output / exact holder terminal", "cavity_or_terminal": "SELECTION REQUIRED", "project_signal": "BRANCH_FUSED_IN", "population": "SELECTION REQUIRED", "conductor": "Belden 9918 002100 red", "acceptance": "far-end identity and polarity must be frozen before any assembly", "warning": WARNING},
        {"harness_id": "HAR-CIN", "end": "B", "mate_or_reference": "carrier JIN1 / JST B2P-VH", "cavity_or_terminal": "1", "project_signal": "BRANCH_FUSED_IN", "population": "VHR-2N + SVH-21T-P1.1", "conductor": "Belden 9918 002100 red", "acceptance": "continuity only to protected source positive", "warning": WARNING},
        {"harness_id": "HAR-CIN", "end": "A", "mate_or_reference": "return distribution / exact terminal", "cavity_or_terminal": "SELECTION REQUIRED", "project_signal": "ACT_0V_PE_BONDED", "population": "SELECTION REQUIRED", "conductor": "Belden 9918 010100 black", "acceptance": "far-end identity and single-bond architecture must be accepted", "warning": WARNING},
        {"harness_id": "HAR-CIN", "end": "B", "mate_or_reference": "carrier JIN1 / JST B2P-VH", "cavity_or_terminal": "2", "project_signal": "ACT_0V_PE_BONDED", "population": "VHR-2N + SVH-21T-P1.1", "conductor": "Belden 9918 010100 black", "acceptance": "continuity only to accepted common return", "warning": WARNING},
        {"harness_id": "HAR-COUT", "end": "A", "mate_or_reference": "carrier JOUT1 / JST B2P-VH", "cavity_or_terminal": "1", "project_signal": "BRANCH_LIMITED_OUT", "population": "VHR-2N + SVH-21T-P1.1", "conductor": "Belden 9918 002100 red", "acceptance": "continuity only to DXL-star selected JPx pin 1", "warning": WARNING},
        {"harness_id": "HAR-COUT", "end": "B", "mate_or_reference": "DXL-STAR JP1/JP2/JP3 / JST B2P-VH", "cavity_or_terminal": "1", "project_signal": "Jx_VDD AFTER CARRIER", "population": "VHR-2N + SVH-21T-P1.1", "conductor": "Belden 9918 002100 red", "acceptance": "axis/net relabeling required; never connect to an unmodified pre-carrier Jx_VDD definition", "warning": WARNING},
        {"harness_id": "HAR-COUT", "end": "A", "mate_or_reference": "carrier JOUT1 / JST B2P-VH", "cavity_or_terminal": "2", "project_signal": "ACT_0V_PE_BONDED", "population": "VHR-2N + SVH-21T-P1.1", "conductor": "Belden 9918 010100 black", "acceptance": "continuity only to selected JPx pin 2", "warning": WARNING},
        {"harness_id": "HAR-COUT", "end": "B", "mate_or_reference": "DXL-STAR JP1/JP2/JP3 / JST B2P-VH", "cavity_or_terminal": "2", "project_signal": "ACT_0V_PE_BONDED", "population": "VHR-2N + SVH-21T-P1.1", "conductor": "Belden 9918 010100 black", "acceptance": "continuity only to accepted common return", "warning": WARNING},
    ]

    cut_rows = []
    for harness, ends in (("HAR-CIN", "source termination to JIN1"), ("HAR-COUT", "JOUT1 to selected DXL-STAR JPx")):
        for circuit, color, mpn, signal in (("P", "RED", "9918 002100", "POSITIVE RAIL"), ("R", "BLACK", "9918 010100", "RETURN")):
            cut_rows.append({"wire_id": f"{harness}-{circuit}", "harness_id": harness, "route": ends, "signal": signal, "wire_mpn": mpn, "color": color, "cut_length_mm": "SELECTION REQUIRED", "strip_length_end_a_mm": "SELECTION REQUIRED", "strip_length_end_b_mm": "SELECTION REQUIRED", "end_a_termination": "SELECTION REQUIRED" if harness == "HAR-CIN" else "VHR-2N / SVH-21T-P1.1", "end_b_termination": "VHR-2N / SVH-21T-P1.1", "label_text": f"{harness}-{circuit}", "status": "DO NOT CUT OR CRIMP", "warning": WARNING})

    process_rows = [
        {"step_id": "CHP-001", "operation": "route survey", "controlled_requirement": "measure installed path with carrier, DXL-star, fuse holder, service loop, bend radius, tie-down and guard installed", "numeric_acceptance": "SELECTION REQUIRED", "state": "NOT EXECUTED", "evidence_uri": "", "warning": WARNING},
        {"step_id": "CHP-002", "operation": "wire receipt", "controlled_requirement": "verify MPN, color, 18 AWG 16x30 construction and nominal OD against manufacturer record", "numeric_acceptance": "received lot evidence required", "state": "NOT EXECUTED", "evidence_uri": "", "warning": WARNING},
        {"step_id": "CHP-003", "operation": "strip", "controlled_requirement": "use contact-specific controlled strip length; no nicked/cut strands or insulation damage", "numeric_acceptance": "SELECTION REQUIRED - JST application specification/provider instruction needed", "state": "NOT EXECUTED", "evidence_uri": "", "warning": WARNING},
        {"step_id": "CHP-004", "operation": "crimp", "controlled_requirement": "use validated SVH-21T-P1.1 process; no generic plier or unverified hand tool", "numeric_acceptance": "crimp height/width and insulation support SELECTION REQUIRED", "state": "NOT EXECUTED", "evidence_uri": "", "warning": WARNING},
        {"step_id": "CHP-005", "operation": "crimp inspection", "controlled_requirement": "record conductor brush, bellmouth, cutoff tab, wire barrel, insulation support and contact damage photos", "numeric_acceptance": "SELECTION REQUIRED", "state": "NOT EXECUTED", "evidence_uri": "", "warning": WARNING},
        {"step_id": "CHP-006", "operation": "pull test", "controlled_requirement": "test process coupons separately; do not damage production articles", "numeric_acceptance": "SELECTION REQUIRED - wire/contact/process standard and sampling plan", "state": "NOT EXECUTED", "evidence_uri": "", "warning": WARNING},
        {"step_id": "CHP-007", "operation": "housing insertion", "controlled_requirement": "insert positive into cavity 1 and return into cavity 2; verify lance engagement and secure lock", "numeric_acceptance": "full seating and retention; quantitative retention SELECTION REQUIRED", "state": "NOT EXECUTED", "evidence_uri": "", "warning": WARNING},
        {"step_id": "CHP-008", "operation": "continuity/polarity", "controlled_requirement": "100 percent pin-by-pin test before mating to any board; independent second-person polarity check", "numeric_acceptance": "meter/isolation thresholds SELECTION REQUIRED", "state": "NOT EXECUTED", "evidence_uri": "", "warning": WARNING},
        {"step_id": "CHP-009", "operation": "retention and route", "controlled_requirement": "no connector carries cable weight; strain relief and bend/service loop survive guarded handling", "numeric_acceptance": "SELECTION REQUIRED", "state": "NOT EXECUTED", "evidence_uri": "", "warning": WARNING},
        {"step_id": "CHP-010", "operation": "limited-energy thermal qualification", "controlled_requirement": "measure both contacts and conductors at accepted duty, ambient and bundling after protection/source coordination", "numeric_acceptance": "SELECTION REQUIRED; no powered execution authorized", "state": "NOT EXECUTED", "evidence_uri": "", "warning": WARNING},
    ]

    acceptance_subjects = [
        "carrier and DXL-star received connector identity", "source/fuse far-end terminal identity", "single DC 0 V/PE bond disposition",
        "installed route and exact cut lengths", "wire lot and construction", "contact and housing lot identity", "controlled strip specification",
        "controlled crimp equipment and settings", "crimp cross-section/visual acceptance", "process-coupon pull acceptance", "100 percent continuity",
        "100 percent polarity", "unintended-pair isolation", "mating/retention/strain relief", "voltage drop and thermal stabilization",
        "fault-clearing and reverse-energy behavior", "qualified electrical/manufacturing review", "separate written work authorization",
    ]
    acceptance_rows = [{"acceptance_id": f"CHA-{i:03d}", "subject": subject, "required_evidence": "executed configuration-specific record with raw data and traceable article IDs", "execution_state": "NOT EXECUTED", "result": "OPEN", "evidence_uri": "", "approver": "", "approval_date": "", "warning": WARNING} for i, subject in enumerate(acceptance_subjects, 1)]

    unresolved_rows = [
        {"selection_id": "CHU-001", "topic": "HAR-CIN source-side termination", "evidence_to_close": "exact fuse holder/source terminal, approved contact/lug/ferrule, wire range, torque/tool and finger-safe enclosure route", "state": "SELECTION REQUIRED", "warning": WARNING},
        {"selection_id": "CHU-002", "topic": "carrier placement", "evidence_to_close": "controlled mounting location, orientation, clearance, thermal airflow, tie-downs and service access", "state": "SELECTION REQUIRED", "warning": WARNING},
        {"selection_id": "CHU-003", "topic": "cut lengths", "evidence_to_close": "measured route for HAR-CIN and HAR-COUT including service loop and bend limits", "state": "SELECTION REQUIRED", "warning": WARNING},
        {"selection_id": "CHU-004", "topic": "strip length and crimp geometry", "evidence_to_close": "current JST application specification or qualified harness-provider process for SVH-21T-P1.1 with Belden 9918", "state": "SELECTION REQUIRED", "warning": WARNING},
        {"selection_id": "CHU-005", "topic": "manual/prototype crimp tool", "evidence_to_close": "manufacturer-approved exact tool or qualified provider process; catalog machine chain alone is not a prototype hand-tool release", "state": "SELECTION REQUIRED", "warning": WARNING},
        {"selection_id": "CHU-006", "topic": "pull test and sampling", "evidence_to_close": "applicable workmanship standard, contact/wire minimum, coupon quantity and calibrated tester", "state": "SELECTION REQUIRED", "warning": WARNING},
        {"selection_id": "CHU-007", "topic": "labels and strain relief", "evidence_to_close": "exact materials, compatibility, placement, abrasion, heat and retention tests", "state": "SELECTION REQUIRED", "warning": WARNING},
        {"selection_id": "CHU-008", "topic": "installed electrical limits", "evidence_to_close": "fault current, fuse, source foldback, length, ambient, bundling, connector, inrush, regeneration, duty and jurisdiction evidence", "state": "SELECTION REQUIRED", "warning": WARNING},
        {"selection_id": "CHU-009", "topic": "post-carrier net naming", "evidence_to_close": "Electrical V3 and DXL-star revision that distinguishes BRANCH_LIMITED_OUT from the pre-carrier J1/J2/J3_VDD names", "state": "SELECTION REQUIRED", "warning": WARNING},
    ]

    for name, rows in (("primary-source-register.csv", source_rows), ("harness-bom.csv", bom_rows), ("interface-control.csv", interface_rows), ("cut-crimp-schedule.csv", cut_rows), ("manufacturing-process.csv", process_rows), ("acceptance-matrix.csv", acceptance_rows), ("unresolved-selections.csv", unresolved_rows)):
        write_csv(ENG / name, rows)
        write_csv(OUT / name, rows)

    status = {
        "identifier": IDENTIFIER, "round": "R160", "date": "2026-08-09",
        "harnesses": 2, "interface_rows": len(interface_rows), "exact_candidate_bom_rows": 5,
        "selection_required_bom_rows": 2, "acceptance_rows": len(acceptance_rows), "open_acceptance_rows": len(acceptance_rows),
        "unresolved_selections": len(unresolved_rows), "source_hashes": {key: sha256(path) for key, path in SOURCES.items()},
        "carrier_side_connector_identity_closed_as_candidate": True, "output_both_ends_connector_identity_closed_as_candidate": True,
        "input_source_side_termination_selected": False, "cut_lengths_selected": False, "crimp_process_released": False,
        "harness_buildable": False, "harness_fabricated": False, "physical_test_executed": False,
        "qualified_review_complete": False, "supplier_contacted": False, "procurement_authorized": False,
        "fabrication_authorized": False, "assembly_authorized": False, "connection_authorized": False,
        "motion_authorized": False, "energization_authorized": False, "safety_credit": False, "warning": WARNING,
    }
    for directory in (ENG, OUT):
        write_text(directory / "package-status.json", json.dumps(status, indent=2) + "\n")
        write_text(directory / "README.md", f"# {IDENTIFIER}\n\n> **{WARNING}**\n\nR160 freezes the carrier-side JST VH mating family and an exact 18 AWG wire candidate, and defines the two-harness interface from the protected branch through the P0.3 carrier to one DXL-star input. It deliberately leaves route-dependent lengths, the source-side termination, crimp dimensions/tooling acceptance, installed electrical limits and every physical result open. Do not cut, crimp, assemble or connect from this package.\n")

    hold_html = "".join(f"<li><strong>{r['selection_id']}</strong><span>{html.escape(r['topic'])}</span><p>{html.escape(r['evidence_to_close'])}</p></li>" for r in unresolved_rows)
    iface_html = "".join(f"<tr><td>{r['harness_id']}</td><td>{r['end']}</td><td>{html.escape(r['mate_or_reference'])}</td><td>{r['cavity_or_terminal']}</td><td>{html.escape(r['project_signal'])}</td><td>{html.escape(r['conductor'])}</td></tr>" for r in interface_rows)
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{IDENTIFIER}</title><style>:root{{--sky:#b9e8ff;--navy:#082f58;--blue:#12669f;--gold:#f2b928;--paper:#f7fcff;--hold:#fff0b8}}*{{box-sizing:border-box}}body{{margin:0;color:var(--navy);font:clamp(16px,1.15vw,19px)/1.5 Arial,sans-serif;background:white}}header{{padding:clamp(1.5rem,5vw,4rem);background:linear-gradient(135deg,var(--sky),#effaff);border-bottom:7px solid var(--gold)}}h1{{font-size:clamp(2.2rem,5vw,4.6rem);line-height:1.04;max-width:20ch;margin:.25rem 0 1rem}}h2{{font-size:clamp(1.55rem,3vw,2.5rem)}}main{{max-width:1380px;margin:auto;padding:2rem clamp(1rem,4vw,3.5rem)}}.warning{{background:var(--hold);border:3px solid #ad7500;border-radius:.8rem;padding:1rem;font-weight:800}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,230px),1fr));gap:1rem;margin:2rem 0}}article{{border:3px solid var(--blue);border-radius:1rem;padding:1.1rem;background:var(--paper)}}article b{{display:block;font-size:clamp(2rem,4vw,3.5rem)}}.boundary{{border-left:7px solid var(--gold);padding-left:1rem;margin:2rem 0}}.table-wrap{{overflow:auto;border:2px solid #93b8ce;border-radius:.7rem}}table{{border-collapse:collapse;width:100%;min-width:1000px}}th,td{{padding:.8rem;text-align:left;vertical-align:top;border-bottom:1px solid #bdd0dc}}th{{background:var(--navy);color:white}}code,.meta,li span{{font-size:14px}}li{{margin:.9rem 0}}li strong{{display:block}}li p{{margin:.25rem 0}}a{{color:#075a96}}</style></head><body><header><div class="meta">{IDENTIFIER} · R160 · 2026-08-09</div><h1>The plugs are known. The route is not.</h1><div class="warning">{WARNING}. Do not cut, crimp, mate or power from this candidate.</div></header><main><p>The P0.3 carrier uses JST B2P-VH headers with project pin 1 positive and pin 2 return. This package freezes exact mating-family and wire candidates without inventing the missing installation measurements.</p><section class="grid"><article><b>2</b>controlled harness identities</article><article><b>8</b>pin/interface rows</article><article><b>9</b>unresolved selections</article><article><b>0</b>executed acceptance rows</article></section><div class="boundary"><h2>Candidate construction</h2><p>Carrier and DXL-star mates: JST VHR-2N housings with SVH-21T-P1.1 contacts. Conductors: Belden 9918, 18 AWG 16x30, red item 9918 002100 and black item 9918 010100. These identities fit the published wire and insulation-diameter envelope; installed current and thermal approval remain open.</p></div><h2>Interface map</h2><div class="table-wrap"><table><thead><tr><th>Harness</th><th>End</th><th>Mate</th><th>Cavity</th><th>Signal</th><th>Conductor</th></tr></thead><tbody>{iface_html}</tbody></table></div><div class="boundary"><h2>What blocks an actual harness</h2><ol>{hold_html}</ol></div><p><a href="interface-control.csv">interface control</a> · <a href="harness-bom.csv">BOM</a> · <a href="cut-crimp-schedule.csv">cut/crimp schedule</a> · <a href="manufacturing-process.csv">process traveler</a> · <a href="acceptance-matrix.csv">acceptance matrix</a> · <a href="unresolved-selections.csv">open selections</a></p></main></body></html>'''
    write_text(OUT / "index.html", page)

    for directory in (ENG, OUT):
        files = sorted(path for path in directory.rglob("*") if path.is_file() and path.name != "file-manifest.csv")
        rows = [{"path": path.relative_to(directory).as_posix(), "bytes": path.stat().st_size, "sha256": sha256(path)} for path in files]
        write_csv(directory / "file-manifest.csv", rows)

    print(f"{IDENTIFIER}: 2 harnesses / 8 interface rows / 9 unresolved selections / 18 acceptance rows OPEN")
    print(WARNING)


if __name__ == "__main__":
    main()
