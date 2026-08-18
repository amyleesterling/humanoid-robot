"""Generate the HR-30 first physical-build cart and execution guide.

The cart converts existing controlled engineering candidates into a deliberately
small first physical tranche.  It does not place orders and does not grant any
procurement, fabrication, connection, powered-test, motion, or energization
authority.
"""

from __future__ import annotations

import csv
import hashlib
import html
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WB = ROOT / "hr30" / "whole-body-p0.1"
OUT = WB / "first-build-cart-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / OUT.name
ACCESSED = "2026-08-17"
WARNING = (
    "PRELIMINARY - HUMAN APPROVAL REQUIRED BEFORE ANY ORDER OR PHYSICAL WORK - "
    "NOT APPROVED FOR PROCUREMENT, STRUCTURAL FABRICATION, CONNECTION, POWERED "
    "TESTING, MOTION, OR ENERGIZATION"
)


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
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def bind_sources() -> list[dict]:
    paths = [
        "boston-fabrication-route-p0.1/route-status.json",
        "boston-fabrication-route-p0.1/bpl-submission/HR30_G01_gripper_fit_plate_nonstructural.stl",
        "boston-fabrication-route-p0.1/makerspace-submission/HR30_complete_98_part_nonstructural_fit_check.zip",
        "first-fit-article-p0.1/fit-article-status.json",
        "first-fit-article-p0.1/HR30_G01_manual_fit_article_plate_candidate.stl",
        "first-fit-article-p0.1/HR30-G01-first-fit-article-p0.1.zip",
        "electrical/axis-commissioning-station-p0.1/candidate-bom.csv",
        "electrical/axis-commissioning-station-p0.1/bench-harness-p0.1/candidate-bom.csv",
        "electrical/logic-power-kit-p0.1/equipment-register.csv",
        "electrical/swd-adapter-p0.1/adapter-bom.csv",
        "harness/actuator-cable-coupon-p0.1/coupon-bom.csv",
        "harness/actuator-cable-coupon-p0.1/tooling-candidate-register.csv",
        "first-energization-readiness-p0.1/readiness-status.json",
        "first-energization-readiness-p0.1/open-holds.csv",
        "electrical/walking-power-successor-p0.1/walking-power-status.json",
    ]
    rows = []
    for sequence, relative in enumerate(paths, start=1):
        path = WB / relative
        if not path.is_file():
            raise RuntimeError(f"authoritative source missing: {relative}")
        rows.append({
            "sequence": sequence,
            "source_path": relative,
            "sha256": sha256(path),
            "bytes": path.stat().st_size,
            "role": "AUTHORITATIVE PROJECT INPUT",
            "warning": WARNING,
        })
    return rows


def project_source_checks() -> dict:
    boston = json.loads((WB / "boston-fabrication-route-p0.1/route-status.json").read_text(encoding="utf-8"))
    readiness = json.loads((WB / "first-energization-readiness-p0.1/readiness-status.json").read_text(encoding="utf-8"))
    fit_article = json.loads((WB / "first-fit-article-p0.1/fit-article-status.json").read_text(encoding="utf-8"))
    station = read_csv(WB / "electrical/axis-commissioning-station-p0.1/candidate-bom.csv")
    coupon = read_csv(WB / "harness/actuator-cable-coupon-p0.1/coupon-bom.csv")
    tools = read_csv(WB / "harness/actuator-cable-coupon-p0.1/tooling-candidate-register.csv")
    station_by_code = {row["order_code"]: row for row in station}
    coupon_by_id = {row["item_id"]: row for row in coupon}
    required_station = {"902-0132-000", "902-0145-001", "903-0244-000", "903-0249-000"}
    required_coupon = {f"ACC-B{i:02d}" for i in range(1, 12)}
    if required_station - set(station_by_code):
        raise RuntimeError("axis-station candidate BOM drift")
    if required_coupon != set(coupon_by_id):
        raise RuntimeError("actuator-coupon candidate BOM drift")
    if len(tools) != 4:
        raise RuntimeError("actuator-coupon tooling register drift")
    if boston["bpl_gripper_plate_part_count"] != 9 or boston["complete_fit_check_zip_stl_count"] != 98:
        raise RuntimeError("physical fit-check source drift")
    if fit_article["printable_part_count"] != 11 or fit_article["built_part_count"] != 0 or fit_article["energization_authority"]:
        raise RuntimeError("manual first-fit-article source drift")
    if readiness["first_energization_ready"] or readiness["connection_authority"]:
        raise RuntimeError("readiness boundary unexpectedly changed")
    return {
        "station": station_by_code,
        "coupon": coupon_by_id,
        "coupon_tools": tools,
        "boston": boston,
        "readiness": readiness,
        "fit_article": fit_article,
    }


def write_records(inputs: dict) -> dict:
    sources = [
        {"source_id": "FBC-S01", "organization": "ROBOTIS", "subject": "U2D2 product / price", "url": "https://www.robotis.us/u2d2/", "revision_date": "live product page; revision not stated", "accessed_date": ACCESSED, "verified_fact": "SKU 902-0132-000; USD 36.92; USB-C upgrade statement; U2D2 does not power actuators"},
        {"source_id": "FBC-S02", "organization": "ROBOTIS", "subject": "U2D2 current technical documentation", "url": "https://docs.robotis.com/docs/parts/interface/u2d2/", "revision_date": "ROBOTIS Docs current page; revision not shown", "accessed_date": ACCESSED, "verified_fact": "communication interface only; external actuator power required; current connector/pin documentation"},
        {"source_id": "FBC-S03", "organization": "ROBOTIS", "subject": "U2D2 Power Hub product / price", "url": "https://robotis.us/u2d2-power-hub-board-set/", "revision_date": "live product page; revision not stated", "accessed_date": ACCESSED, "verified_fact": "SKU 902-0145-001; USD 21.85; 3.5-24 V; 10 A maximum; X3P/X4P 100 mm cables included"},
        {"source_id": "FBC-S04", "organization": "ROBOTIS", "subject": "U2D2 Power Hub technical documentation", "url": "https://docs.robotis.com/docs/parts/interface/u2d2_power_hub/", "revision_date": "ROBOTIS Docs current page; revision not shown", "accessed_date": ACCESSED, "verified_fact": "10 A aggregate maximum and only one power input at a time"},
        {"source_id": "FBC-S05", "organization": "ROBOTIS", "subject": "X3P 180 mm cable pack", "url": "https://www.robotis.us/robot-cable-x3p-180mm-10pcs/", "revision_date": "live product page; revision not stated", "accessed_date": ACCESSED, "verified_fact": "SKU 903-0249-000; ten TTL cables; USD 21.85"},
        {"source_id": "FBC-S06", "organization": "ROBOTIS", "subject": "X4P 180 mm cable pack", "url": "https://robotis.us/robot-cable-x4p-180mm-10pcs/", "revision_date": "live product page; revision not stated", "accessed_date": ACCESSED, "verified_fact": "SKU 903-0244-000; ten RS-485 cables; USD 23.23"},
        {"source_id": "FBC-S07", "organization": "igus", "subject": "CF130.03.02.UL", "url": "https://www.igus.com/product/CF130_UL", "revision_date": "live product page; revision not stated", "accessed_date": ACCESSED, "verified_fact": "2 x 22 AWG / 0.34 mm2 medium-duty chainflex evaluation candidate; free-sample route shown"},
        {"source_id": "FBC-S08", "organization": "igus", "subject": "CF9.UL.02.02", "url": "https://toolbox.igus.com/wp-content/uploads/2023/08/chainflex-control-cables-catalog.pdf", "revision_date": "official chainflex control-cable catalog", "accessed_date": ACCESSED, "verified_fact": "2 x 0.25 mm2 / 24 AWG data/flex coupon candidate"},
        {"source_id": "FBC-S09", "organization": "JST", "subject": "EH connector family", "url": "https://www.jst-mfg.com/product/index.php?lang=2&series=58", "revision_date": "live manufacturer family page; revision not stated", "accessed_date": ACCESSED, "verified_fact": "EHR-3/EHR-4 housings and EH contact family identifiers"},
        {"source_id": "FBC-S10", "organization": "Molex", "subject": "Micro-Fit 3.0 family", "url": "https://www.molex.com/en-us/products/connectors/wire-to-board-connectors/micro-fit-connectors", "revision_date": "live manufacturer family page; revision not stated", "accessed_date": ACCESSED, "verified_fact": "fixed transition connector family; exact received-part/tool/process validation remains required"},
        {"source_id": "FBC-S11", "organization": "Boston Public Library", "subject": "KBLIC 3D printing", "url": "https://www.bpl.org/about-the-bpl/official-policies/kirstein-business-library-innovation-center-3d-printing-guidelines/", "revision_date": "current policy page", "accessed_date": ACCESSED, "verified_fact": "service currently says temporarily unavailable; do not submit yet"},
        {"source_id": "FBC-S12", "organization": "Artisans Asylum", "subject": "Boston-area maker facilities", "url": "https://www.artisansasylum.com/home", "revision_date": "current official site", "accessed_date": ACCESSED, "verified_fact": "local digital fabrication, machine, metal, electronics and robotics capabilities; exact access/capability confirmation required"},
    ]
    write_csv(OUT / "primary-source-register.csv", sources)

    purchase = [
        {"cart_id": "FBC-P01", "disposition": "HUMAN APPROVAL REQUIRED", "manufacturer": "ROBOTIS", "order_code": "902-0132-000", "description": "U2D2 USB communication interface; reusable single-actuator commissioning tool", "quantity": 1, "unit_price_usd": "36.92", "extended_price_usd": "36.92", "shipping_tax": "NOT INCLUDED", "availability": "LISTED FOR SALE; NUMERIC STOCK NOT STATED", "source_id": "FBC-S01", "project_use": "ONE DISCONNECTED ACTUATOR ONLY; NOT A WHOLE-BODY BUS CONTROLLER", "authority": "NO ORDER PLACED / NO CONNECTION OR POWER AUTHORITY"},
        {"cart_id": "FBC-P02", "disposition": "HUMAN APPROVAL REQUIRED", "manufacturer": "ROBOTIS", "order_code": "902-0145-001", "description": "U2D2 Power Hub Board Set; reusable current-limited single-actuator bench interface", "quantity": 1, "unit_price_usd": "21.85", "extended_price_usd": "21.85", "shipping_tax": "NOT INCLUDED", "availability": "LISTED FOR SALE; NUMERIC STOCK NOT STATED", "source_id": "FBC-S03", "project_use": "ONE ACTUATOR ONLY; REJECTED FOR SUMMED ROBOT POWER", "authority": "NO ORDER PLACED / NO CONNECTION OR POWER AUTHORITY"},
    ]
    write_csv(OUT / "purchase-candidate-register.csv", purchase)

    samples = []
    sample_map = [
        ("FBC-Q01", "ACC-B01", "REQUEST SAMPLE / QUOTE", "5 m supplier-cut data/flex evaluation sample"),
        ("FBC-Q02", "ACC-B09", "REQUEST SAMPLE / QUOTE", "10 m supplier-cut dynamic power-pair coupon"),
        ("FBC-Q03", "ACC-B08", "REQUEST CUT-LENGTH QUOTE", "5 m red plus 5 m black static coupon wire"),
        ("FBC-Q04", "ACC-B02", "REQUEST GENUINE LOT / QUOTE", "50 loose-piece EH contacts"),
        ("FBC-Q05", "ACC-B04", "REQUEST GENUINE LOT / QUOTE", "10 EHR-3 housings"),
        ("FBC-Q06", "ACC-B05", "REQUEST GENUINE LOT / QUOTE", "10 EHR-4 housings"),
        ("FBC-Q07", "ACC-B10", "REQUEST GENUINE LOT / QUOTE", "30 Micro-Fit receptacles plus 100 female terminals"),
        ("FBC-Q08", "ACC-B11", "REQUEST GENUINE LOT / QUOTE", "30 panel plugs plus 100 male terminals"),
    ]
    for quote_id, item_id, disposition, request in sample_map:
        row = inputs["coupon"][item_id]
        samples.append({
            "quote_id": quote_id,
            "source_item_id": item_id,
            "disposition": disposition,
            "manufacturer": row["manufacturer"],
            "order_code": row["order_code"],
            "request_quantity": request,
            "required_response": "price; lead time; MOQ; lot traceability/CoC; exact current order code; shipping to Boston MA",
            "selection_state": "CANDIDATE ONLY - DO NOT PRODUCTION-CUT",
            "authority": "NO ORDER PLACED / NO PRODUCTION FABRICATION AUTHORITY",
        })
    write_csv(OUT / "sample-quote-register.csv", samples)

    borrow = [
        {"tool_id": "FBC-T01", "source": "AXIS COMMISSIONING STATION", "manufacturer": "Keysight", "order_code": "E36313A", "purpose": "programmable isolated current-limited source; use output 2 or 3", "disposition": "BORROW / MAKERSPACE AVAILABILITY CHECK", "why_not_buy_now": "expensive bench equipment; equivalent must be qualified against the station requirements", "required_evidence": "model/serial; calibration state; output isolation; programmed 0.25 A limit behavior; operator competence"},
        {"tool_id": "FBC-T02", "source": "BENCH HARNESS", "manufacturer": "Molex", "order_code": "63819-0901", "purpose": "Mini-Fit Jr 18 AWG hand crimp", "disposition": "BORROW OR CONTRACT HARNESS SHOP", "why_not_buy_now": "specialized tooling requires receipt/calibration/process validation", "required_evidence": "tool condition/calibration; exact terminal/wire compatibility; destructive pull coupons"},
        {"tool_id": "FBC-T03", "source": "ACTUATOR COUPON", "manufacturer": "JST", "order_code": "YC-260R", "purpose": "loose-piece EH coupon crimp", "disposition": "BORROW OR CONTRACT HARNESS SHOP", "why_not_buy_now": "candidate process is not selected; production applicator path may be preferable", "required_evidence": "tool condition; crimp-height setup; received wire/contact coupons and pull results"},
        {"tool_id": "FBC-T04", "source": "BENCH HARNESS", "manufacturer": "Mitutoyo", "order_code": "342-271-30", "purpose": "crimp-height measurement", "disposition": "BORROW / METROLOGY SERVICE", "why_not_buy_now": "specialized measurement system; calibration and method suitability still required", "required_evidence": "current calibration; measurement-system check; recorded crimp heights"},
        {"tool_id": "FBC-T05", "source": "BENCH HARNESS", "manufacturer": "Mark-10", "order_code": "WT-205M + CERT", "purpose": "controlled axial crimp pull tests", "disposition": "CONTRACT TEST / BORROW QUALIFIED LAB", "why_not_buy_now": "high-cost dedicated tester; grip and method still require validation", "required_evidence": "calibration certificate; grip suitability; 25 +/-6 mm/min test evidence"},
        {"tool_id": "FBC-T06", "source": "BENCH HARNESS", "manufacturer": "KNIPEX", "order_code": "95 11 165 + 12 12 14", "purpose": "clean lead cutting and controlled stripping", "disposition": "BORROW OR BUY ONLY WITH PROCESS OWNER", "why_not_buy_now": "tool setup must be proven on received conductor construction", "required_evidence": "zero nicked/cut strands; measured strip length; coupon inspection"},
    ]
    write_csv(OUT / "borrow-contract-register.csv", borrow)

    hold = [
        {"hold_id": "FBC-H01", "item": "all 25 production actuators", "reason": "mechanical fit articles, final actuator/transmission selection and representative bench characterization are incomplete", "release_evidence": "printed/inspected fit check plus frozen axis allocation and approved representative commissioning sequence", "state": "DO NOT BUY YET"},
        {"hold_id": "FBC-H02", "item": "eight walking-power board assemblies", "reason": "production stackup, TPS259482L paired application acceptance, thresholds, brake/dump and thermal validation remain open", "release_evidence": "manufacturer application disposition; DFM; FAI/X-ray; bench power/regeneration/thermal evidence", "state": "DO NOT BUY YET"},
        {"hold_id": "FBC-H03", "item": "full structural metal package", "reason": "materials, tolerances, received actuator fit and structural capacity are not released", "release_evidence": "maker/commercial DFM, controlled drawings, material records, fit coupon and qualified review", "state": "QUOTE ONLY - DO NOT FABRICATE"},
        {"hold_id": "FBC-H04", "item": "onboard battery, BMS, charger and onboard-energy hardware", "reason": "active development configuration is tether-first; energy/protection/charge architecture remains unresolved", "release_evidence": "selected source/protection/charger/interlock/thermal architecture and qualified review", "state": "DO NOT BUY YET"},
        {"hold_id": "FBC-H05", "item": "production-length custom harness", "reason": "cable coupons, crimp processes, final measured routes and hot-current/fault derating are unexecuted", "release_evidence": "accepted coupons, route measurements, derating, continuity/insulation/flex/retention evidence", "state": "SAMPLES ONLY - DO NOT PRODUCTION-CUT"},
        {"hold_id": "FBC-H06", "item": "DYNAMIXEL Starter Set as the energization source", "reason": "the bundled fixed 12 V supply is not the project-required programmable 0.25 A first-power current-limit evidence", "release_evidence": "use a qualified programmable isolated source; starter supply receives no first-power credit", "state": "REJECT FOR FIRST ENERGIZATION"},
        {"hold_id": "FBC-H07", "item": "extra X3P/X4P 10-packs for the first bench", "reason": "U2D2 and Power Hub packages already include short/convertible cable candidates sufficient for a one-actuator interface preflight", "release_evidence": "received contents inspection and later production harness quantity definition", "state": "NOT NEEDED IN FIRST CART"},
        {"hold_id": "FBC-H08", "item": "specialist crimp/pull/metrology tool purchases", "reason": "process route is not selected and contract/borrow options avoid premature multi-thousand-dollar tooling", "release_evidence": "process-owner make/buy decision after supplier/harness-shop capability responses", "state": "BORROW / CONTRACT FIRST"},
    ]
    write_csv(OUT / "do-not-buy-yet-register.csv", hold)

    actions = [
        {"sequence": 1, "action_id": "FBC-A01", "lane": "PRINT", "action": "Send the controlled eleven-part manual G01 fit-article ZIP and clearance coupon to Artisans Asylum or another confirmed local printer; BPL remains unavailable", "input": "first-fit-article-p0.1 ZIP and plate STL SHA-bound below", "completion_evidence": "quote/profile/slicer screenshot; coupon plus eleven labeled parts; assembled manual mechanism; photographs and completed fit-article traveler", "state": "OPEN - NO FILE SENT"},
        {"sequence": 2, "action_id": "FBC-A02", "lane": "QUOTE", "action": "Send the eight cable/connector sample requests without authorizing production lengths", "input": "sample-quote-register.csv and vendor-request-templates.md", "completion_evidence": "dated quotes with exact order codes, MOQ, lead time, lot/CoC and shipping", "state": "OPEN - NO REQUEST SENT"},
        {"sequence": 3, "action_id": "FBC-A03", "lane": "BORROW", "action": "Ask the makerspace or a harness shop which exact crimp, pull-test, metrology and programmable-supply equipment is available", "input": "borrow-contract-register.csv", "completion_evidence": "dated capability response with model, tooling condition, calibration and operator/process constraints", "state": "OPEN - NO FACILITY CONFIRMATION"},
        {"sequence": 4, "action_id": "FBC-A04", "lane": "BUY", "action": "After human approval only, order one U2D2 and one Power Hub as reusable one-actuator commissioning tools", "input": "purchase-candidate-register.csv", "completion_evidence": "purchase record plus received SKU/USB revision/package-content inspection", "state": "OPEN - NO ORDER PLACED"},
        {"sequence": 5, "action_id": "FBC-A05", "lane": "BUILD", "action": "Build and destructively qualify cable coupons before cutting any production harness", "input": "existing actuator-cable-coupon traveler", "completion_evidence": "completed traveler, crimp heights, pull results, conductor/OD/retention/flex observations and disposition", "state": "OPEN - ZERO COUPONS BUILT"},
        {"sequence": 6, "action_id": "FBC-A06", "lane": "HOLD", "action": "Keep actuators, walking-power boards, batteries and structural metal out of the cart until their release evidence closes", "input": "do-not-buy-yet-register.csv", "completion_evidence": "no premature purchase plus later signed gate disposition", "state": "ACTIVE HOLD"},
    ]
    write_csv(OUT / "first-build-action-register.csv", actions)

    inspection = [
        {"inspection_id": "FBC-I01", "item": "G01 manual fit article", "check": "clearance coupon plus exactly eleven labeled parts; 1:1 millimetre scale; no unintended slicer scaling", "record": "photos, slicer profile, hardware identities, fit-article traveler, measurements and issue log", "state": "NOT EXECUTED"},
        {"inspection_id": "FBC-I02", "item": "ROBOTIS 902-0132-000", "check": "received SKU; USB connector revision; included cable identities; no shipping damage", "record": "receiving photo and serial/lot where present", "state": "NOT RECEIVED"},
        {"inspection_id": "FBC-I03", "item": "ROBOTIS 902-0145-001", "check": "received SKU; hub/support hardware; X3P/X4P 100 mm cables; exposed underside protected", "record": "receiving photo and continuity-only preflight record", "state": "NOT RECEIVED"},
        {"inspection_id": "FBC-I04", "item": "igus cable samples", "check": "exact jacket marking/order code, received length, OD, conductor count/construction and traceability", "record": "lot/CoC, dimensional record and retained sample ID", "state": "NOT RECEIVED"},
        {"inspection_id": "FBC-I05", "item": "JST/Molex coupon components", "check": "exact genuine order codes, quantity, plating/lot/packaging and mating fit", "record": "receiving register and controlled sample IDs", "state": "NOT RECEIVED"},
        {"inspection_id": "FBC-I06", "item": "borrowed equipment", "check": "exact model/serial, calibration state, accessories, isolation/current-limit behavior and operator approval", "record": "dated facility capability and pre-use inspection", "state": "NOT CONFIRMED"},
        {"inspection_id": "FBC-I07", "item": "first actuator candidate", "check": "not yet in cart; exact model/interface/voltage/received condition required before later bench work", "record": "future selected-axis receiving record", "state": "BLOCKED / NOT SELECTED"},
    ]
    write_csv(OUT / "receiving-inspection-register.csv", inspection)

    template = f"""# HR-30 first-build request templates

{WARNING}

## Printer / makerspace request

Please quote and preflight the attached `HR30-G01-first-fit-article-p0.1.zip` at 100% scale in millimetres. It contains one clearance coupon and one eleven-part, unpowered, nonstructural manual gripper fit article. Print the coupon first. Please report printer, material, layer height, support plan, estimated time, price and any geometry concerns. Do not alter scale, install an actuator, or manufacture further robot parts without a separate instruction.

## Cable and connector sample request

Please quote only the exact sample quantities in `sample-quote-register.csv`. Return manufacturer, exact current order code, MOQ, cut-length policy, price, lead time, lot traceability/CoC availability and shipping to Boston, Massachusetts. Do not substitute wire gauge, conductor construction, insulation, contact plating or connector family without written disposition.

## Harness-shop / makerspace capability request

Please identify whether you have the exact candidate tools or qualified equivalents in `borrow-contract-register.csv`. Include model, applicable terminals/wires, calibration/inspection state, pull-test capability, operator/process requirements and estimated service cost. This inquiry does not authorize production harness fabrication.
"""
    (OUT / "vendor-request-templates.md").write_text(template, encoding="utf-8", newline="\n")
    return {
        "sources": sources,
        "purchase": purchase,
        "samples": samples,
        "borrow": borrow,
        "hold": hold,
        "actions": actions,
        "inspection": inspection,
    }


def write_page(records: dict, status: dict) -> None:
    def rows(data: list[dict], columns: list[tuple[str, str]]) -> str:
        return "".join(
            "<tr>" + "".join(f"<td>{html.escape(str(row[key]))}</td>" for key, _ in columns) + "</tr>"
            for row in data
        )

    action_cols = [("sequence", "#"), ("lane", "Lane"), ("action", "Action"), ("completion_evidence", "Completion evidence"), ("state", "State")]
    purchase_cols = [("manufacturer", "Manufacturer"), ("order_code", "Order code"), ("description", "Item"), ("quantity", "Qty"), ("unit_price_usd", "Unit USD"), ("extended_price_usd", "Extended USD"), ("project_use", "Boundary")]
    sample_cols = [("disposition", "Disposition"), ("manufacturer", "Manufacturer"), ("order_code", "Order code"), ("request_quantity", "Request"), ("required_response", "Required response")]
    borrow_cols = [("disposition", "Disposition"), ("manufacturer", "Manufacturer"), ("order_code", "Order code"), ("purpose", "Purpose"), ("required_evidence", "Evidence")]
    hold_cols = [("item", "Do not buy yet"), ("reason", "Why"), ("release_evidence", "What releases it"), ("state", "State")]
    cards = "".join(
        f'<article class="step" data-lane="{html.escape(row["lane"])}"><label><input type="checkbox" data-action="{row["action_id"]}"><span><strong>{row["sequence"]}. {html.escape(row["lane"])}</strong><br>{html.escape(row["action"])}<small>{html.escape(row["state"])}</small></span></label></article>'
        for row in records["actions"]
    )
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 first physical-build cart</title><style>
:root{{--deep:#071d36;--blue:#0b4f91;--sky:#d9f2ff;--gold:#f2b91d;--paper:#f6fbff;--ink:#142a40;--line:#91cbe7;--red:#8f2600}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.55 system-ui,Segoe UI,sans-serif}}header,main,footer{{padding:clamp(24px,5vw,64px) max(18px,calc((100vw - 1280px)/2))}}header,footer{{background:linear-gradient(135deg,var(--deep),var(--blue));color:#fff}}h1{{font-size:clamp(38px,6vw,68px);line-height:1.05}}h2{{font-size:clamp(28px,4vw,42px)}}.warning{{background:var(--gold);color:#17243a;border:3px solid #805600;padding:16px;font-weight:900}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px}}article,.panel{{background:#fff;border:2px solid var(--line);border-radius:16px;padding:19px}}.metric{{font-size:clamp(30px,5vw,48px);font-weight:900;color:var(--blue)}}.hold{{border-color:#c15b32;background:#fff4ee}}.steps{{display:grid;gap:12px}}.step label{{display:flex;gap:15px;cursor:pointer}}.step input{{width:26px;height:26px;flex:0 0 auto}}.step small{{display:block;margin-top:7px;color:#445;line-height:1.4}}.step:has(input:checked){{opacity:.64;background:#e4f7ea}}.toolbar{{display:flex;gap:9px;flex-wrap:wrap;margin:14px 0}}button{{font:700 16px system-ui;padding:10px 14px;border:2px solid var(--blue);border-radius:9px;background:#fff;color:var(--blue);cursor:pointer}}button.active{{background:var(--blue);color:#fff}}.scroll{{overflow:auto;border:2px solid var(--line);border-radius:14px;background:#fff}}table{{border-collapse:collapse;width:100%;min-width:1050px}}th,td{{padding:14px;text-align:left;vertical-align:top;border-bottom:1px solid var(--line);font-size:16px}}th{{background:var(--deep);color:#fff;position:sticky;top:0}}a{{color:#075b9b;font-weight:800}}code{{font-size:15px;overflow-wrap:anywhere}}@media(max-width:560px){{body{{font-size:16px}}}}
</style></head><body><header><div class="warning">{html.escape(WARNING)}</div><p>Boston, Massachusetts · supplier review {ACCESSED}</p><h1>Buy less. Build the first evidence.</h1><p>This is the controlled bridge from a complete digital robot to the first physical fit article and cable coupons. It is a planning cart—not an automatic order.</p></header><main>
<section class="grid"><article><div class="metric">$58.77</div><p>two reusable ROBOTIS bench candidates before shipping and tax; human approval required.</p></article><article><div class="metric">11 parts</div><p>one assemblable manual G01 fit article plus clearance coupon ready for a printer quote.</p></article><article><div class="metric">8 quotes</div><p>cut-length cable and genuine connector coupon requests.</p></article><article class="hold"><div class="metric">0 ordered</div><p>no vendor contact, purchase, print, build or power work has occurred.</p></article></section>
<section><h2>Six actions, in order</h2><p>These checkboxes are stored only in this browser; they are not engineering evidence.</p><div class="toolbar"><button class="active" data-filter="ALL">All</button><button data-filter="PRINT">Print</button><button data-filter="QUOTE">Quote</button><button data-filter="BORROW">Borrow</button><button data-filter="BUY">Buy</button><button data-filter="BUILD">Build</button><button data-filter="HOLD">Hold</button></div><div class="steps">{cards}</div></section>
<section><h2>The only priced purchase candidates</h2><div class="warning">Do not click through or order until Amy approves the cart. These are commissioning tools, not permission to connect or power an actuator.</div><div class="scroll"><table><thead><tr>{''.join(f'<th>{label}</th>' for _,label in purchase_cols)}</tr></thead><tbody>{rows(records['purchase'],purchase_cols)}</tbody></table></div><p><a href="purchase-candidate-register.csv">Download the purchase register</a>.</p></section>
<section><h2>Request samples and quotes</h2><div class="scroll"><table><thead><tr>{''.join(f'<th>{label}</th>' for _,label in sample_cols)}</tr></thead><tbody>{rows(records['samples'],sample_cols)}</tbody></table></div><p><a href="sample-quote-register.csv">Download the sample register</a> · <a href="vendor-request-templates.md">copy the request templates</a>.</p></section>
<section><h2>Borrow or contract specialist equipment</h2><div class="scroll"><table><thead><tr>{''.join(f'<th>{label}</th>' for _,label in borrow_cols)}</tr></thead><tbody>{rows(records['borrow'],borrow_cols)}</tbody></table></div><p><a href="borrow-contract-register.csv">Download the tool/capability register</a>.</p></section>
<section><h2>The expensive mistakes this cart blocks</h2><div class="scroll"><table><thead><tr>{''.join(f'<th>{label}</th>' for _,label in hold_cols)}</tr></thead><tbody>{rows(records['hold'],hold_cols)}</tbody></table></div><p><a href="do-not-buy-yet-register.csv">Download the hold register</a>.</p></section>
<section><h2>Controlled source and receiving records</h2><div class="panel"><p><a href="first-build-action-register.csv">Actions</a> · <a href="receiving-inspection-register.csv">Receiving checks</a> · <a href="primary-source-register.csv">Current supplier sources</a> · <a href="project-source-binding.csv">Project source hashes</a> · <a href="cart-status.json">Status</a>.</p><p>The U2D2 listing says USB-C upgrade but still lists a Micro USB cable in package contents; receipt inspection is mandatory. The Power Hub is limited to a single-actuator commissioning role here and is rejected as a whole-body power aggregator.</p></div></section>
</main><footer>{html.escape(WARNING)}</footer><script>
const boxes=[...document.querySelectorAll('[data-action]')];boxes.forEach(b=>{{b.checked=localStorage.getItem('hr30-'+b.dataset.action)==='1';b.addEventListener('change',()=>localStorage.setItem('hr30-'+b.dataset.action,b.checked?'1':'0'))}});document.querySelectorAll('[data-filter]').forEach(btn=>btn.addEventListener('click',()=>{{document.querySelectorAll('[data-filter]').forEach(x=>x.classList.remove('active'));btn.classList.add('active');const f=btn.dataset.filter;document.querySelectorAll('.step').forEach(card=>card.hidden=f!=='ALL'&&card.dataset.lane!==f)}}));
</script></body></html>'''
    (OUT / "index.html").write_text(page + "\n", encoding="utf-8", newline="\n")


def replace_marked(text: str, start: str, end: str, block: str) -> str:
    if start in text:
        left = text.index(start)
        right = text.index(end, left) + len(end)
        return text[:left] + block + text[right:]
    return text.rstrip() + "\n\n" + block + "\n"


def integrate(status: dict) -> None:
    start = "<!-- HR30-FIRST-BUILD-CART-P01-START -->"
    end = "<!-- HR30-FIRST-BUILD-CART-P01-END -->"
    readme_path = WB / "README.md"
    readme = readme_path.read_text(encoding="utf-8")
    block = f'''{start}
## First physical-build cart P0.1

The [interactive first-build cart](first-build-cart-p0.1/index.html) converts the existing fit-check, cable-coupon and one-actuator commissioning packages into a deliberately small first tranche: one clearance coupon and eleven-part manually operable G01 fit article, eight sample/quote requests, borrowed or contracted specialist tooling, and two reusable ROBOTIS bench candidates totaling USD 58.77 before tax and shipping. No order, vendor contact, print, physical test, connection or energization is claimed.
{end}'''
    readme_path.write_text(replace_marked(readme, start, end, block), encoding="utf-8", newline="\n")

    index_path = WB / "index.html"
    page = index_path.read_text(encoding="utf-8")
    section = f'''{start}<section id="first-build-cart"><h2>The first-build cart is intentionally small</h2><div class="grid"><article class="card pass"><div class="metric">$58.77</div><p>two reusable one-actuator bench candidates; human approval required.</p></article><article class="card pass"><div class="metric">11 parts</div><p>one assemblable manual G01 fit article plus clearance coupon.</p></article><article class="card pass"><div class="metric">8 quotes</div><p>cable and connector coupon requests.</p></article><article class="card hold"><div class="metric">0 ordered</div><p>full actuators, power boards, batteries and production harnesses remain held.</p></article></div><p><a href="first-build-cart-p0.1/index.html">Open the interactive first physical-build cart</a>.</p></section>{end}'''
    if start in page:
        page = replace_marked(page, start, end, section)
    else:
        anchor = "<!-- HR30-BOSTON-FABRICATION-ROUTE-P01-END -->"
        if anchor not in page:
            raise RuntimeError("Boston fabrication integration anchor missing")
        page = page.replace(anchor, anchor + section, 1)
    index_path.write_text(page, encoding="utf-8", newline="\n")

    root_path = ROOT / "index.html"
    root_page = root_path.read_text(encoding="utf-8")
    link = '<li><a href="hr30/whole-body-p0.1/first-build-cart-p0.1/index.html">Interactive first physical-build cart</a></li>'
    if link not in root_page:
        anchor = '<li><a href="hr30/whole-body-p0.1/boston-fabrication-route-p0.1/index.html">Boston fabrication execution route</a></li>'
        if anchor not in root_page:
            raise RuntimeError("root Boston route link missing")
        root_path.write_text(root_page.replace(anchor, anchor + link, 1), encoding="utf-8", newline="\n")

    status_path = WB / "package-status.json"
    package_status = json.loads(status_path.read_text(encoding="utf-8"))
    package_status.update({
        "first_build_cart_present": True,
        "first_build_cart_priced_candidate_count": status["priced_purchase_candidate_count"],
        "first_build_cart_priced_subtotal_usd": status["priced_candidate_subtotal_usd"],
        "first_build_cart_sample_quote_count": status["sample_quote_count"],
        "first_build_cart_borrow_contract_tool_count": status["borrow_contract_tool_count"],
        "first_build_cart_do_not_buy_count": status["do_not_buy_count"],
        "first_build_cart_orders_placed": 0,
        "first_build_cart_supplier_contacts_executed": 0,
        "first_build_cart_physical_actions_completed": 0,
        "first_build_cart_procurement_authority": False,
    })
    status_path.write_text(json.dumps(package_status, indent=2) + "\n", encoding="utf-8", newline="\n")


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


def build() -> dict:
    inputs = project_source_checks()
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    write_csv(OUT / "project-source-binding.csv", bind_sources())
    records = write_records(inputs)
    subtotal = round(sum(float(row["extended_price_usd"]) for row in records["purchase"]), 2)
    status = {
        "identifier": "HR30-FIRST-BUILD-CART-P0.1",
        "date": ACCESSED,
        "warning": WARNING,
        "project_source_binding_count": 15,
        "primary_source_count": len(records["sources"]),
        "priced_purchase_candidate_count": len(records["purchase"]),
        "priced_candidate_subtotal_usd": subtotal,
        "shipping_tax_included": False,
        "sample_quote_count": len(records["samples"]),
        "borrow_contract_tool_count": len(records["borrow"]),
        "do_not_buy_count": len(records["hold"]),
        "action_count": len(records["actions"]),
        "receiving_inspection_count": len(records["inspection"]),
        "gripper_fit_plate_part_count": 11,
        "first_fit_article_part_count": 11,
        "first_fit_article_coupon_count": 1,
        "whole_body_fit_check_stl_count": 98,
        "human_purchase_approval_required": True,
        "orders_placed": 0,
        "supplier_contacts_executed": 0,
        "quotes_received": 0,
        "parts_printed": 0,
        "coupons_built": 0,
        "physical_tests_executed": 0,
        "procurement_authority": False,
        "fabrication_authority": False,
        "connection_authority": False,
        "powered_test_authority": False,
        "motion_authority": False,
        "energization_authority": False,
    }
    (OUT / "cart-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n")
    (OUT / "README.md").write_text(
        f"# HR-30 first physical-build cart P0.1\n\n{WARNING}\n\n"
        "This package creates a small, human-approved first physical tranche from the current whole-body release: one clearance coupon and eleven-part manual G01 fit article, two reusable ROBOTIS bench-interface candidates, eight sample/quote requests, six borrow/contract equipment paths and eight explicit do-not-buy holds. No order or physical work has been executed.\n",
        encoding="utf-8",
        newline="\n",
    )
    shutil.copy2(Path(__file__), OUT / "first-build-cart-source.py")
    write_page(records, status)
    integrate(status)
    manifest_and_release()
    return status


def main() -> int:
    print(json.dumps(build(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
