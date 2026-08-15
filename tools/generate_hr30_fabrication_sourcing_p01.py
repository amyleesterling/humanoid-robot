"""Generate the HR-30 whole-body fabrication sourcing and RFQ package.

This package binds every existing manufacturing-candidate part to a practical
Boston-area or online quoting route.  It is an RFQ/DFM conversation package,
not a released drawing set and not authority to order or fabricate parts.
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
WB = ROOT / "hr30" / "whole-body-p0.1"
MFG = WB / "manufacturing-files"
OUT = WB / "fabrication-sourcing-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / "fabrication-sourcing-p0.1"
IDENTIFIER = "HR30-WHOLE-BODY-FABRICATION-SOURCING-P0.1"
WARNING = (
    "PRELIMINARY - RFQ AND DFM CONVERSATION PACKAGE ONLY - NOT APPROVED FOR "
    "PROCUREMENT, FABRICATION, ASSEMBLY, POWERED TESTING, MOTION, OR ENERGIZATION"
)
AUTHORITY = "NO PROCUREMENT, FABRICATION, ASSEMBLY, POWERED TEST, MOTION OR ENERGIZATION AUTHORITY"
ACCESS_DATE = "2026-08-15"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise RuntimeError(f"refusing empty controlled register: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dimensions(text: str) -> list[float]:
    return [float(value.strip()) for value in text.removesuffix(" mm").split(" x ")]


def route_for(row: dict[str, str]) -> tuple[str, str, str]:
    material = row["material_candidate"].upper()
    role = row["role"].lower()
    if row["stl_path"]:
        return (
            "FIT-PRINT",
            "LOCAL ADDITIVE FIT ARTICLE",
            "The Hive / Artisans Asylum / qualified print provider; final polymer and process remain unselected",
        )
    if row["dxf_path"]:
        return (
            "FLAT-PROFILE",
            "FLAT-CUT OR 2.5D CNC PREQUOTE",
            "SendCutSend stock screen plus Xometry/qualified CNC fallback; exact thickness substitution prohibited",
        )
    if "ROD" in material:
        return (
            "PRECISION-ROD",
            "TURN/GRIND OR CATALOGUE-ROD PREQUOTE",
            "Qualified machine shop; hardness, straightness, finish and end features require drawing release",
        )
    if any(token in material for token in ("POM", "ACETAL", "PA-CF")) or "pad" in role:
        return (
            "CNC-POLYMER",
            "CNC POLYMER / ELASTOMER COUPON PREQUOTE",
            "Xometry/Protolabs or qualified local shop; exact resin, conditioning and lot evidence open",
        )
    return (
        "CNC-METAL",
        "3-AXIS CNC / CUT-DRILL PREQUOTE",
        "Xometry/Protolabs or qualified local machine shop; exact stock, temper and inspection open",
    )


def batch_for(row: dict[str, str], route_id: str) -> str:
    material = row["material_candidate"].upper()
    if route_id == "FIT-PRINT":
        return "QB-05-COVERS-FIT-PRINT"
    if route_id == "FLAT-PROFILE" and "6061" in material:
        return "QB-01-STRUCTURAL-FLAT-6061"
    if route_id == "FLAT-PROFILE":
        return "QB-02-GRIPPER-POLYMER"
    if route_id == "CNC-METAL":
        return "QB-03-CNC-ALUMINUM"
    if route_id == "CNC-POLYMER":
        return "QB-02-GRIPPER-POLYMER"
    return "QB-06-PRECISION-RODS"


def source_rows() -> list[dict]:
    return [
        {
            "source_id": "SRC-SCS-MATERIALS",
            "provider": "SendCutSend",
            "official_url": "https://sendcutsend.com/materials/",
            "verified_claim": "6061-T6 flat stock is listed in twelve thicknesses from 1.02 to 19.05 mm; Delrin, neoprene and other flat materials are also listed; laser, waterjet and CNC processes are offered",
            "document_revision_or_date": "LIVE OFFICIAL PAGE; REVISION NOT STATED",
            "accessed": ACCESS_DATE,
            "use_boundary": "PREQUOTE STOCK/PROCESS SCREEN ONLY; NO AUTOMATIC THICKNESS SUBSTITUTION OR ORDER RELEASE",
        },
        {
            "source_id": "SRC-SCS-6061",
            "provider": "SendCutSend",
            "official_url": "https://sendcutsend.com/materials/6061-aluminum/",
            "verified_claim": "6061-T6 stock sizes and optional deburring, countersinking, tapping, hardware and finishing services are published",
            "document_revision_or_date": "LIVE OFFICIAL PAGE; REVISION NOT STATED",
            "accessed": ACCESS_DATE,
            "use_boundary": "STOCK AVAILABILITY EVIDENCE; STRUCTURAL ALLOWABLES, CERTIFICATION AND PART ACCEPTANCE REMAIN OPEN",
        },
        {
            "source_id": "SRC-XOM-CNC",
            "provider": "Xometry US",
            "official_url": "https://www.xometry.com/capabilities/cnc-machining-service/cnc-milling-service/",
            "verified_claim": "CNC milling lists Aluminum 6061-T6 and custom material review paths",
            "document_revision_or_date": "LIVE OFFICIAL PAGE; REVISION NOT STATED",
            "accessed": ACCESS_DATE,
            "use_boundary": "CNC RFQ CANDIDATE; SUPPLIER/LOT/PROCESS ACCEPTANCE IS NOT INFERRED",
        },
        {
            "source_id": "SRC-XOM-STANDARDS",
            "provider": "Xometry US",
            "official_url": "https://www.xometry.com/manufacturing-standards/",
            "verified_claim": "Published default CNC tolerance and edge-break practices exist, while quote-specific requirements may supersede them",
            "document_revision_or_date": "LIVE OFFICIAL PAGE; REVISION NOT STATED",
            "accessed": ACCESS_DATE,
            "use_boundary": "REFERENCE ONLY; HR-30 TOLERANCES/GD&T MUST BE RELEASED PART BY PART",
        },
        {
            "source_id": "SRC-PROTO-QUALITY",
            "provider": "Protolabs",
            "official_url": "https://www.protolabs.com/media/y3gd35lg/pl_procurement_guide.pdf",
            "verified_claim": "Official procurement guide identifies CNC machining and optional inspection-report paths",
            "document_revision_or_date": "2025 PUBLICATION; PAGE REVISION NOT STATED",
            "accessed": ACCESS_DATE,
            "use_boundary": "BACKUP CNC/INSPECTION RFQ ROUTE; EXACT CAPABILITY MUST BE CONFIRMED IN WRITTEN QUOTE",
        },
        {
            "source_id": "SRC-AA-HOME",
            "provider": "Artisans Asylum",
            "official_url": "https://www.artisansasylum.com/home",
            "verified_claim": "Boston campus lists machine, metal, CNC plasma, electronics/robotics, finishing and digital-fabrication shops",
            "document_revision_or_date": "LIVE OFFICIAL PAGE; REVISION NOT STATED",
            "accessed": ACCESS_DATE,
            "use_boundary": "LOCAL DFM, FIXTURE AND FIT-ARTICLE PATH; MEMBERSHIP/TRAINING AND TOOL-SPECIFIC CAPABILITY CONFIRMATION REQUIRED",
        },
        {
            "source_id": "SRC-AA-TRAINING",
            "provider": "Artisans Asylum",
            "official_url": "https://www.artisansasylum.com/tool-testing-safety-training",
            "verified_claim": "Official page requires tool testing and distinguishes testing from instruction",
            "document_revision_or_date": "LIVE OFFICIAL PAGE; REVISION NOT STATED",
            "accessed": ACCESS_DATE,
            "use_boundary": "NO UNSUPERVISED TOOL USE IS ASSUMED",
        },
        {
            "source_id": "SRC-FABVILLE",
            "provider": "FabVille",
            "official_url": "https://fabville.org/",
            "verified_claim": "Somerville community fabrication lab publishes free open-shop access and staff support; current calendar posts a summer closure until the school year",
            "document_revision_or_date": "LIVE OFFICIAL SITE/CALENDAR; REVISION NOT STATED",
            "accessed": ACCESS_DATE,
            "use_boundary": "PROTOTYPE/DFM PATH ONLY; CONFIRM REOPENING, EXACT MACHINE, MATERIAL AND STAFF APPROVAL BEFORE VISIT",
        },
        {
            "source_id": "SRC-HIVE",
            "provider": "Cambridge Public Library - The Hive",
            "official_url": "https://www.cambridgema.gov/departments/cambridgepubliclibrary/locations/mainlibrary/thehive",
            "verified_claim": "The Hive publishes free fabrication access for Minuteman cardholders after required safety/equipment training",
            "document_revision_or_date": "LIVE OFFICIAL PAGE; REVISION NOT STATED",
            "accessed": ACCESS_DATE,
            "use_boundary": "NONSTRUCTURAL FIT-ARTICLE/LEARNING PATH ONLY; EXACT EQUIPMENT AND MATERIAL RULES MUST BE CONFIRMED",
        },
        {
            "source_id": "SRC-BPL-PRINT",
            "provider": "Boston Public Library",
            "official_url": "https://www.bpl.org/faq/technology/",
            "verified_claim": "BPL lists MakerBot access at selected branches; exact location rules apply",
            "document_revision_or_date": "LIVE OFFICIAL PAGE; REVISION NOT STATED",
            "accessed": ACCESS_DATE,
            "use_boundary": "SMALL NONSTRUCTURAL PRINT/FIT COUPONS ONLY; NOT A METAL OR PRODUCTION ROUTE",
        },
    ]


def provider_rows() -> list[dict]:
    return [
        {"route_id": "SHOP-01", "provider": "SendCutSend", "location": "ONLINE / US", "capability": "flat laser/waterjet/CNC profiles; published 6061-T6 and Delrin stock; secondary services", "hr30_use": "prequote 45 DXF profiles after exact stock-thickness and drawing review", "current_constraint": "many HR-30 4.0 and 5.0 mm parts do not match published stock exactly", "contact_or_url": "https://sendcutsend.com/materials/", "selection_state": "SHORTLISTED FOR DFM/RFQ - NOT ORDER RELEASED", "authority": AUTHORITY},
        {"route_id": "SHOP-02", "provider": "Xometry US", "location": "ONLINE NETWORK", "capability": "CNC aluminum/polymer, custom material review, certification and inspection options", "hr30_use": "primary quotation route for exact-thickness and nonplanar parts", "current_constraint": "supplier, stock, tolerances, inspection and certificate requirements must be explicit in quote", "contact_or_url": "https://www.xometry.com/capabilities/cnc-machining-service/cnc-milling-service/", "selection_state": "SHORTLISTED FOR DFM/RFQ - NOT ORDER RELEASED", "authority": AUTHORITY},
        {"route_id": "SHOP-03", "provider": "Protolabs", "location": "ONLINE / US", "capability": "CNC and documented quality/inspection options", "hr30_use": "independent backup quote and DFM comparison", "current_constraint": "exact material, features, tolerances and reports require written quote", "contact_or_url": "https://www.protolabs.com/services/cnc-machining/", "selection_state": "SHORTLISTED FOR DFM/RFQ - NOT ORDER RELEASED", "authority": AUTHORITY},
        {"route_id": "SHOP-04", "provider": "Artisans Asylum", "location": "ALLSTON, BOSTON", "capability": "machine, metal, CNC plasma, finishing, electronics/robotics and digital-fabrication shops", "hr30_use": "local design review, fixtures, fit articles and supervised prototype operations", "current_constraint": "membership/day pass, instruction, tool testing, exact machine envelope and material approval required", "contact_or_url": "https://www.artisansasylum.com/home", "selection_state": "LOCAL CONTACT/TOUR RECOMMENDED - CAPABILITY CONFIRMATION REQUIRED", "authority": AUTHORITY},
        {"route_id": "SHOP-05", "provider": "FabVille", "location": "SOMERVILLE", "capability": "community fabrication lab and open shop", "hr30_use": "free learning, DFM discussion and nonproduction prototypes", "current_constraint": "official 2026 calendar posts summer closure until the school year; exact metal capability not established", "contact_or_url": "https://fabville.org/", "selection_state": "SEASONAL HOLD - CONFIRM REOPENING AND MACHINE BEFORE VISIT", "authority": AUTHORITY},
        {"route_id": "SHOP-06", "provider": "The Hive", "location": "CAMBRIDGE PUBLIC LIBRARY", "capability": "trained community access to digital/traditional fabrication", "hr30_use": "nonstructural printed fit articles, templates and learning", "current_constraint": "Minuteman card, safety training, reservations, exact equipment/material rules", "contact_or_url": "https://www.cambridgema.gov/departments/cambridgepubliclibrary/locations/mainlibrary/thehive", "selection_state": "LOCAL FIT-ARTICLE ROUTE - NOT PRODUCTION", "authority": AUTHORITY},
        {"route_id": "SHOP-07", "provider": "Boston Public Library", "location": "BOSTON BRANCHES", "capability": "MakerBot printing at selected locations", "hr30_use": "small nonstructural geometry coupons only", "current_constraint": "location-specific rules; KBLIC page currently reports printing temporarily unavailable", "contact_or_url": "https://www.bpl.org/faq/technology/", "selection_state": "LIMITED COUPON ROUTE - CONFIRM AVAILABILITY", "authority": AUTHORITY},
    ]


def build() -> dict:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    part_files = read_csv(MFG / "part-file-register.csv")
    if len(part_files) != 98:
        raise RuntimeError(f"expected 98 manufacturing parts, found {len(part_files)}")

    part_rows = []
    stock_rows = []
    route_counts: Counter[str] = Counter()
    batch_counts: Counter[str] = Counter()
    scs_6061 = [1.02, 1.60, 2.03, 2.54, 3.18, 4.75, 6.35, 8.00, 9.50, 12.70, 15.88, 19.05]
    scs_delrin = [3.18, 6.90]
    for row in part_files:
        route_id, route_name, shortlist = route_for(row)
        batch_id = batch_for(row, route_id)
        route_counts[route_id] += 1
        batch_counts[batch_id] += 1
        step = MFG / row["step_path"]
        svg = MFG / row["svg_path"]
        dxf = MFG / row["dxf_path"] if row["dxf_path"] else None
        stl = MFG / row["stl_path"] if row["stl_path"] else None
        for path in (step, svg, dxf, stl):
            if path is not None and not path.is_file():
                raise FileNotFoundError(path)
        part_rows.append({
            "part_id": row["part_id"],
            "module": row["module"],
            "role": row["role"],
            "quantity_candidate": "1",
            "quote_batch_id": batch_id,
            "route_id": route_id,
            "route_name": route_name,
            "provider_shortlist": shortlist,
            "material_candidate": row["material_candidate"],
            "bbox_mm": row["bbox_mm"],
            "step_upload_path": "../manufacturing-files/" + row["step_path"],
            "step_sha256": sha256(step),
            "svg_review_path": "../manufacturing-files/" + row["svg_path"],
            "dxf_upload_path": "../manufacturing-files/" + row["dxf_path"] if dxf else "",
            "stl_fit_article_path": "../manufacturing-files/" + row["stl_path"] if stl else "",
            "dfm_request": "RETURN WRITTEN DFM; IDENTIFY STOCK, SETUP, UNMACHINABLE FEATURES, ASSUMED TOLERANCES AND COST DRIVERS",
            "order_release_state": "PRE-RFQ PACKAGE ONLY - DRAWING/MATERIAL/TOLERANCE/STRUCTURAL RELEASE OPEN",
            "authority": AUTHORITY,
        })
        if dxf:
            nominal = min(dimensions(row["bbox_mm"]))
            material = row["material_candidate"].upper()
            available = scs_6061 if "6061" in material else scs_delrin if any(token in material for token in ("POM", "ACETAL")) else []
            nearest = min(available, key=lambda value: abs(value - nominal)) if available else None
            exact = nearest is not None and abs(nearest - nominal) <= 0.02
            stock_rows.append({
                "part_id": row["part_id"],
                "module": row["module"],
                "material_candidate": row["material_candidate"],
                "cad_nominal_thickness_mm": f"{nominal:.3f}",
                "nearest_published_sendcutsend_stock_mm": f"{nearest:.2f}" if nearest is not None else "NO MATCHING PUBLISHED MATERIAL FAMILY",
                "exact_stock_match_within_0_02_mm": str(exact).upper(),
                "difference_mm": f"{nearest - nominal:+.3f}" if nearest is not None else "",
                "disposition": "FLAT-CUT PREQUOTE ELIGIBLE AFTER DRAWING RELEASE" if exact else "DO NOT SUBSTITUTE - CNC TO NOMINAL OR REVISE AUTHORITATIVE CAD AFTER ENGINEERING REVIEW",
                "authority": AUTHORITY,
            })

    batch_descriptions = {
        "QB-01-STRUCTURAL-FLAT-6061": "structural/frame 6061 flat profiles",
        "QB-02-GRIPPER-POLYMER": "gripper polymer mechanisms and pad coupons",
        "QB-03-CNC-ALUMINUM": "nonplanar aluminum and tube/rail machining",
        "QB-05-COVERS-FIT-PRINT": "nonstructural cover fit articles",
        "QB-06-PRECISION-RODS": "precision guide rods",
    }
    batch_rows = [{
        "quote_batch_id": batch_id,
        "scope": batch_descriptions[batch_id],
        "part_count": batch_counts[batch_id],
        "recommended_first_action": "REQUEST DFM/NO-ORDER QUOTE; REQUIRE ALL ASSUMPTIONS IN WRITING",
        "quote_quantity": "1 AND 2 EACH FOR COST/SETUP COMPARISON",
        "required_return": "unit price; setup/NRE; lead time; exact stock/material/temper; process; assumed tolerances; inspection/cert options; DFM exceptions",
        "release_state": "NOT RELEASED FOR ORDER",
        "authority": AUTHORITY,
    } for batch_id in batch_descriptions]

    dfm_rows = [
        {"request_id": "DFM-01", "topic": "configuration", "question": "Confirm every quoted file SHA and part ID; identify any file conversion or geometry repair.", "required_response": "WRITTEN", "close_condition": "supplier response reconciled to controlled register", "state": "OPEN", "authority": AUTHORITY},
        {"request_id": "DFM-02", "topic": "material", "question": "State exact alloy/resin, temper/condition, stock form, producer and certificate/traceability options.", "required_response": "WRITTEN", "close_condition": "engineering accepts exact material and evidence", "state": "OPEN", "authority": AUTHORITY},
        {"request_id": "DFM-03", "topic": "stock thickness", "question": "Do not substitute stock thickness. Flag every mismatch against nominal CAD.", "required_response": "WRITTEN", "close_condition": "CAD/drawing is revised or exact finished thickness is quoted", "state": "OPEN", "authority": AUTHORITY},
        {"request_id": "DFM-04", "topic": "tolerances", "question": "List all assumed default tolerances and every feature that needs an explicit drawing tolerance or datum.", "required_response": "WRITTEN", "close_condition": "released drawing/GD&T or accepted quote-specific requirement", "state": "OPEN", "authority": AUTHORITY},
        {"request_id": "DFM-05", "topic": "features", "question": "Identify inaccessible corners, tool-radius limits, thin walls, unsupported print regions, threads, countersinks and post-machining needs.", "required_response": "MARKED-UP DFM", "close_condition": "authoritative CAD is dispositioned feature by feature", "state": "OPEN", "authority": AUTHORITY},
        {"request_id": "DFM-06", "topic": "edge safety", "question": "Quote deburring/edge-break options and identify edges that cannot receive consistent treatment.", "required_response": "WRITTEN", "close_condition": "edge-treatment drawing requirement and inspection method released", "state": "OPEN", "authority": AUTHORITY},
        {"request_id": "DFM-07", "topic": "inspection", "question": "Quote first-article, dimensional report, material certificate and traceability options separately.", "required_response": "WRITTEN", "close_condition": "qualified reviewer accepts inspection plan", "state": "OPEN", "authority": AUTHORITY},
        {"request_id": "DFM-08", "topic": "finish", "question": "Identify as-machined/cut/printed finish, cleaning, coating, masking and dimensional effects.", "required_response": "WRITTEN", "close_condition": "finish and post-process specification released", "state": "OPEN", "authority": AUTHORITY},
        {"request_id": "DFM-09", "topic": "lot control", "question": "State whether paired/bilateral parts can be made from one material lot and one setup.", "required_response": "WRITTEN", "close_condition": "lot/setup plan recorded", "state": "OPEN", "authority": AUTHORITY},
        {"request_id": "DFM-10", "topic": "authority", "question": "Treat uploaded files as quote/DFM inputs only; do not start manufacture without a later signed purchase release.", "required_response": "ACKNOWLEDGEMENT", "close_condition": "supplier acknowledges no-order boundary", "state": "OPEN", "authority": AUTHORITY},
    ]

    write_csv(OUT / "primary-source-register.csv", source_rows())
    write_csv(OUT / "shop-route-register.csv", provider_rows())
    write_csv(OUT / "part-to-shop-route.csv", part_rows)
    write_csv(OUT / "flat-stock-gap-register.csv", stock_rows)
    write_csv(OUT / "quote-batch-register.csv", batch_rows)
    write_csv(OUT / "dfm-request-register.csv", dfm_rows)

    exact_flat_matches = sum(row["exact_stock_match_within_0_02_mm"] == "TRUE" for row in stock_rows)
    status = {
        "identifier": IDENTIFIER,
        "part_count": len(part_rows),
        "module_count": len({row["module"] for row in part_rows}),
        "planar_dxf_count": len(stock_rows),
        "printed_fit_article_count": route_counts["FIT-PRINT"],
        "quote_batch_count": len(batch_rows),
        "provider_route_count": len(provider_rows()),
        "primary_source_count": len(source_rows()),
        "exact_sendcutsend_stock_match_count": exact_flat_matches,
        "stock_mismatch_or_unlisted_count": len(stock_rows) - exact_flat_matches,
        "every_part_has_step_hash_binding": True,
        "rfq_conversation_package_complete": True,
        "supplier_contact_executed": False,
        "quotes_received": False,
        "materials_selected": False,
        "tolerances_gdt_released": False,
        "dfm_complete": False,
        "fai_complete": False,
        "structural_capacity_validated": False,
        "procurement_authority": False,
        "fabrication_authority": False,
        "assembly_authority": False,
        "powered_test_authority": False,
        "motion_authority": False,
        "energization_authority": False,
        "warning": WARNING,
    }
    (OUT / "fabrication-sourcing-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    (OUT / "README.md").write_text(
        f"""# HR-30 whole-body fabrication sourcing P0.1

{WARNING}

This package turns all **{len(part_rows)}** existing whole-body manufacturing candidates into a controlled **pre-RFQ/DFM conversation**. It does not release a drawing, material, tolerance, purchase order, fabrication operation, or powered work.

The key practical result is a complete part-to-route allocation: {route_counts['FLAT-PROFILE']} flat profiles, {route_counts['CNC-METAL']} CNC/cut-drill metal parts, {route_counts['CNC-POLYMER']} machined polymer or elastomer candidates, {route_counts['PRECISION-ROD']} precision rods, and {route_counts['FIT-PRINT']} nonstructural printed fit articles. Every row points to the controlled STEP plus any existing DXF/STL derivative and records the STEP SHA-256.

The public-stock screen is intentionally fail-closed. Only {exact_flat_matches} of {len(stock_rows)} planar candidates match the reviewed SendCutSend nominal stock values within 0.02 mm. Every other row says **DO NOT SUBSTITUTE**: use an exact-finished-thickness CNC quote or revise the authoritative CAD after engineering review.

Recommended sequence: request no-order DFM quotes from two qualified suppliers for each batch; visit or contact Artisans Asylum for local machining/fixture discussion; use The Hive or another trained shop only for nonstructural fit articles; reconcile written DFM; then release materials, tolerances, inspection and purchase documents through qualified review.
""",
        encoding="utf-8",
    )
    write_index(part_rows, provider_rows(), batch_rows, status)
    shutil.copy2(Path(__file__), OUT / "fabrication-sourcing-source.py")
    manifest_and_release()
    integrate(status)
    return status


def write_index(parts: list[dict], providers: list[dict], batches: list[dict], status: dict) -> None:
    provider_cards = "".join(
        f'<article class="card"><h3>{html.escape(row["provider"])}</h3><p><strong>{html.escape(row["location"])}</strong></p><p>{html.escape(row["hr30_use"])}</p><p class="meta">{html.escape(row["current_constraint"])}</p><a href="{html.escape(row["contact_or_url"])}">Official capability page</a></article>'
        for row in providers
    )
    batch_rows = "".join(
        f'<tr><td>{html.escape(row["quote_batch_id"])}</td><td>{html.escape(row["scope"])}</td><td>{row["part_count"]}</td><td>{html.escape(row["required_return"])}</td></tr>'
        for row in batches
    )
    part_rows = "".join(
        f'<tr data-route="{html.escape(row["route_id"])}"><td>{html.escape(row["part_id"])}</td><td>{html.escape(row["module"])}</td><td>{html.escape(row["route_name"])}</td><td>{html.escape(row["material_candidate"])}</td><td><a href="{html.escape(row["step_upload_path"])}">STEP</a>{(" · <a href=\"" + html.escape(row["dxf_upload_path"]) + "\">DXF</a>") if row["dxf_upload_path"] else ""}{(" · <a href=\"" + html.escape(row["stl_fit_article_path"]) + "\">STL</a>") if row["stl_fit_article_path"] else ""}</td></tr>'
        for row in parts
    )
    route_buttons = "".join(
        f'<button data-route="{route}">{html.escape(route)} · {count}</button>'
        for route, count in sorted(Counter(row["route_id"] for row in parts).items())
    )
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 fabrication sourcing P0.1</title><style>:root{{--navy:#0d2d57;--blue:#159fe5;--sky:#d8f1ff;--gold:#f4b400;--paper:#f8fcff}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--navy);font:17px/1.55 system-ui,sans-serif}}header{{background:linear-gradient(135deg,var(--navy),#1b68aa);color:white;padding:32px max(20px,calc((100% - 1180px)/2))}}.warning{{background:var(--gold);color:#142746;padding:15px 18px;border-radius:14px;font-weight:850}}h1{{font-size:clamp(34px,5vw,62px);line-height:1.06;margin:.28em 0}}h2{{font-size:clamp(26px,3vw,39px);margin-top:48px}}main{{max-width:1180px;margin:auto;padding:28px 20px 72px}}.stats,.providers{{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:15px}}.card,.panel{{background:white;border:2px solid #9ed9f6;border-radius:17px;padding:19px;box-shadow:0 7px 20px #0d2d5714}}.metric{{font-size:31px;font-weight:850}}.hold{{border-left:9px solid var(--gold)}}.meta{{font-size:14px}}a{{color:#075f9f;font-weight:750}}.filters{{display:flex;gap:10px;flex-wrap:wrap;margin:15px 0}}button{{font:16px/1.35 inherit;padding:11px 14px;border:2px solid #8fcff1;border-radius:12px;background:white;color:var(--navy);cursor:pointer}}button.active{{border-color:var(--gold);box-shadow:0 0 0 3px #f4b40055}}.tablewrap{{overflow:auto;border:2px solid #9ed9f6;border-radius:16px;background:white}}table{{border-collapse:collapse;min-width:900px;width:100%}}th,td{{padding:13px 14px;border-bottom:1px solid #cdeafb;text-align:left;vertical-align:top}}th{{background:var(--navy);color:white;position:sticky;top:0;font-size:14px}}td{{font-size:16px}}@media(max-width:680px){{header{{padding:24px 18px}}main{{padding:20px 14px}}}}</style></head><body><header><div class="warning">{html.escape(WARNING)}</div><p>HR-30 · Whole-body P0.1</p><h1>Make every body part quotable</h1><p>All 98 controlled parts now have a real shop route, upload file, batch, and written DFM request—without pretending a quote is a fabrication release.</p></header><main><section class="stats"><article class="card"><div class="metric">98 / 98</div><p>parts bound to a sourcing route</p></article><article class="card"><div class="metric">45</div><p>planar DXF candidates screened against published stock</p></article><article class="card"><div class="metric">24</div><p>nonstructural cover fit-print candidates</p></article><article class="card hold"><div class="metric">0</div><p>materials, drawings, orders, or fabrication approvals</p></article></section><h2>The practical route</h2><div class="panel hold"><p><strong>Start with no-order DFM quotes.</strong> Upload the exact controlled files, request every assumption in writing, and do not permit stock-thickness substitution. Local makerspaces are valuable for training, fixtures, templates and fit articles; they are not automatically qualified production suppliers.</p><p><a href="part-to-shop-route.csv">All 98 part routes</a> · <a href="quote-batch-register.csv">Six quote batches</a> · <a href="dfm-request-register.csv">Ten mandatory DFM questions</a> · <a href="flat-stock-gap-register.csv">Stock mismatch screen</a> · <a href="primary-source-register.csv">Official-source record</a></p></div><h2>Boston and online routes</h2><section class="providers">{provider_cards}</section><h2>Six controlled quote batches</h2><div class="tablewrap"><table><thead><tr><th>Batch</th><th>Scope</th><th>Parts</th><th>Supplier must return</th></tr></thead><tbody>{batch_rows}</tbody></table></div><h2>Filter all 98 parts</h2><p>Select a route to narrow the table; select it again to restore all parts.</p><div class="filters">{route_buttons}</div><div class="tablewrap"><table><thead><tr><th>Part</th><th>Module</th><th>Route</th><th>Material candidate</th><th>Controlled files</th></tr></thead><tbody id="parts">{part_rows}</tbody></table></div><h2>What this closes—and what it does not</h2><div class="panel hold"><p>This closes the missing <em>path to a real quotation</em>: every body part has a controlled upload file, hash, process family, provider shortlist and DFM question set. It does not close structural loads, materials, tolerances, GD&amp;T, process qualification, FAI, physical proof, procurement, fabrication, assembly, motion, or energization.</p><p>Current public-stock result: <strong>{status['exact_sendcutsend_stock_match_count']}</strong> exact nominal matches and <strong>{status['stock_mismatch_or_unlisted_count']}</strong> mismatches or unlisted material families. Mismatches are not substitutions.</p></div></main><script>const buttons=[...document.querySelectorAll('[data-route]')].filter(x=>x.tagName==='BUTTON'),rows=[...document.querySelectorAll('#parts tr')];buttons.forEach(b=>b.addEventListener('click',()=>{{const on=!b.classList.contains('active');buttons.forEach(x=>x.classList.remove('active'));b.classList.toggle('active',on);rows.forEach(r=>r.hidden=on&&r.dataset.route!==b.dataset.route)}}));</script></body></html>'''
    # CSS font shorthand cannot combine a numeric size with an inherited family;
    # keep filter controls at the required 16 px functional-text minimum.
    page = page.replace(
        "button{font:16px/1.35 inherit;",
        "button{font:inherit;font-size:16px;line-height:1.35;",
    )
    page = page.replace("Six quote batches", "Five quote batches")
    page = page.replace("Six controlled quote batches", "Five controlled quote batches")
    (OUT / "index.html").write_text(page + "\n", encoding="utf-8")


def manifest_and_release() -> None:
    manifest = OUT / "file-manifest.csv"
    if manifest.exists():
        manifest.unlink()
    rows = [{"path": path.relative_to(OUT).as_posix(), "bytes": path.stat().st_size, "sha256": sha256(path), "warning": WARNING} for path in sorted(OUT.rglob("*")) if path.is_file()]
    write_csv(manifest, rows)
    if RELEASE.exists():
        shutil.rmtree(RELEASE)
    shutil.copytree(OUT, RELEASE)


def replace_marked(text: str, start_marker: str, end_marker: str, block: str) -> str:
    if start_marker in text:
        start = text.index(start_marker)
        end = text.index(end_marker, start) + len(end_marker)
        return text[:start] + block + text[end:]
    return text + "\n" + block + "\n"


def integrate(status: dict) -> None:
    readme_path = WB / "README.md"
    readme = readme_path.read_text(encoding="utf-8")
    marker = "## Whole-body fabrication sourcing P0.1"
    block = f"""{marker}

The [interactive fabrication sourcing guide](fabrication-sourcing-p0.1/index.html) binds all {status['part_count']} physical candidates to controlled upload files, exact SHA-256 values, five nonempty quote batches, seven Boston/online routes and ten mandatory written DFM questions. The public-stock screen prevents silent thickness substitution: only {status['exact_sendcutsend_stock_match_count']} of {status['planar_dxf_count']} planar candidates match the reviewed nominal stock values within 0.02 mm.

This is a route to quotation, not authority to buy or make parts. Materials, tolerances/GD&T, inspection, DFM disposition, structural capacity, FAI and physical proof remain open.
"""
    if marker in readme:
        start = readme.index(marker)
        end = readme.find("\n## ", start + len(marker))
        readme = readme[:start].rstrip() + "\n\n" + block.strip() + ("\n\n" + readme[end + 1:] if end >= 0 else "\n")
    else:
        readme = readme.rstrip() + "\n\n" + block.strip() + "\n"
    readme_path.write_text(readme, encoding="utf-8")

    section_start = "<!-- HR30-FABRICATION-SOURCING-P01-START -->"
    section_end = "<!-- HR30-FABRICATION-SOURCING-P01-END -->"
    section = f'''{section_start}<section id="fabrication-sourcing"><h2>Every body part now has a real quotation path</h2><div class="grid"><article class="card pass"><div class="metric">98 / 98</div><p>controlled parts bound to a shop route and exact upload file hash.</p></article><article class="card pass"><div class="metric">6</div><p>quote batches separate flat structural parts, machined parts, mechanisms, rods and fit articles.</p></article><article class="card pass"><div class="metric">7</div><p>verified Boston-area and online fabrication routes.</p></article><article class="card hold"><div class="metric">0</div><p>material, drawing, order or fabrication approvals.</p></article></div><p><a href="fabrication-sourcing-p0.1/index.html">Open the interactive sourcing/RFQ guide</a> · <a href="fabrication-sourcing-p0.1/part-to-shop-route.csv">98-part route register</a> · <a href="fabrication-sourcing-p0.1/flat-stock-gap-register.csv">stock mismatch screen</a>.</p></section>{section_end}'''
    section = section.replace('<div class="metric">6</div><p>quote batches', '<div class="metric">5</div><p>nonempty quote batches')
    index_path = WB / "index.html"
    page = index_path.read_text(encoding="utf-8")
    if section_start in page:
        page = replace_marked(page, section_start, section_end, section)
    else:
        anchor = "<!-- HR30-MANUFACTURING-FILES-P01-END -->"
        if anchor not in page:
            raise RuntimeError("whole-body manufacturing section anchor missing")
        page = page.replace(anchor, anchor + section, 1)
    index_path.write_text(page, encoding="utf-8")

    root_path = ROOT / "index.html"
    root_page = root_path.read_text(encoding="utf-8")
    link = '<li><a href="hr30/whole-body-p0.1/fabrication-sourcing-p0.1/index.html">Fabrication sourcing and RFQ guide</a></li>'
    if link not in root_page:
        anchor = '<li><a href="hr30/whole-body-p0.1/manufacturing-files/index.html">Individual manufacturing-candidate files</a></li>'
        if anchor not in root_page:
            raise RuntimeError("root manufacturing link anchor missing")
        root_page = root_page.replace(anchor, anchor + link, 1)
        root_path.write_text(root_page, encoding="utf-8")

    status_path = WB / "package-status.json"
    package_status = json.loads(status_path.read_text(encoding="utf-8"))
    package_status.update({
        "fabrication_sourcing_package_present": True,
        "fabrication_sourcing_part_count": status["part_count"],
        "fabrication_sourcing_provider_route_count": status["provider_route_count"],
        "fabrication_sourcing_quote_batch_count": status["quote_batch_count"],
        "fabrication_sourcing_exact_stock_match_count": status["exact_sendcutsend_stock_match_count"],
        "fabrication_sourcing_stock_mismatch_count": status["stock_mismatch_or_unlisted_count"],
        "fabrication_supplier_contact_executed": False,
        "fabrication_quotes_received": False,
        "fabrication_drawings_released": False,
        "fabrication_materials_selected": False,
    })
    status_path.write_text(json.dumps(package_status, indent=2) + "\n", encoding="utf-8")

    holds_path = WB / "open-holds.csv"
    holds = read_csv(holds_path)
    for row in holds:
        if row["hold_id"] == "HR30-P01-H06":
            row["unresolved_item"] = (
                "All 98 physical candidates have controlled STEP/SVG files, 45 planar DXFs, 24 cover STLs, and a seven-route Boston/online pre-RFQ allocation with exact file hashes, stock-mismatch screening, five nonempty quote batches and mandatory written DFM questions. Supplier contact/quotes, exact materials/stock, tolerances/GD&T, threads/inserts, edge treatment, process qualification, structural/impact proof, FAI and qualified review remain open."
            )
    write_csv(holds_path, holds)


def main() -> int:
    status = build()
    import generate_hr30_system_package_p01 as system_package
    system_package.refresh_manifest_and_release()
    print(json.dumps(status, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
