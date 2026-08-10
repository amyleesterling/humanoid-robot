#!/usr/bin/env python3
"""Generate the R186 Q4X box installation-evidence and receiving package."""

from __future__ import annotations

import csv
import json
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IDENTIFIER = "HR-V0-Q4X-INSTALL-EVIDENCE-P0.1"
DATE = "2026-08-10"
WARNING = (
    "PRELIMINARY - RECEIVING AND METROLOGY PLAN ONLY - NOT APPROVED FOR "
    "PROCUREMENT, FABRICATION, DRILLING, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
)
PKG = ROOT / "test-equipment/hr-v0/q4x-installation-evidence-p0.1"
WEB = ROOT / "release/hr-v0/q4x-installation-evidence-p0.1"
DOC = ROOT / "docs/hr-v0-q4x-installation-evidence-p0.1.md"
FORM = ROOT / "tests/forms/hr-v0-q4x-hardware-receiving-template-p0.1.csv"


def write_csv(path: Path, fields: list[str], records: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)


sources = [
    {
        "source_id": "QIS-001",
        "manufacturer": "LAPP",
        "document": "SKINTOP ST-M/STR-M instruction sheet",
        "revision_or_date": "99990621 / BS00/2622 VS20; checked 2026-08-10",
        "official_locator": "https://imager.lapp.com/e/lapp/a6G4nvkL02p-wg_DJCmXyg~~/BZ99990621DE_EN.pdf",
        "controlled_use": "installation sequence, M12 torque table, locknut/threaded-hub rule, rating and cable-sheath caveat",
    },
    {
        "source_id": "QIS-002",
        "manufacturer": "LAPP / VDE",
        "document": "VDE certificate 40010604 appendix 200A",
        "revision_or_date": "updated 2022-10-21; checked 2026-08-10",
        "official_locator": "https://imager.lapp.com/e/lapp/I-jAJeCB8_Z5aYSZByOVig~~/ZV53111000DE_EN.pdf",
        "controlled_use": "M12 installation and cap-nut torque; explicit blank separate locknut-torque field",
    },
    {
        "source_id": "QIS-003",
        "manufacturer": "LAPP",
        "document": "53111000 data sheet",
        "revision_or_date": "DB53111000EN version 17; valid 2023-06-20; checked 2026-08-10",
        "official_locator": "https://dam-media.lapp.com/9/917/91782/32f1ce4e45eb4b69b2dd28b70730b82a.pdf",
        "controlled_use": "M12x1.5 thread, 8 mm thread length, body and cable-range geometry",
    },
    {
        "source_id": "QIS-004",
        "manufacturer": "LAPP",
        "document": "53119000 locknut data sheet",
        "revision_or_date": "DB53119000EN version 09; valid 2019-02-19; checked 2026-08-10",
        "official_locator": "https://imager.lapp.com/e/lapp/IxNMTvvLiYtWEfUsJRUaNg~~/DB53119000EN.pdf",
        "controlled_use": "M12x1.5 locknut identity and envelope",
    },
    {
        "source_id": "QIS-005",
        "manufacturer": "Hammond Manufacturing",
        "document": "PJ1084T product and drawing",
        "revision_or_date": "drawing issue 2014-06-04; checked 2026-08-10",
        "official_locator": "https://www.hammfg.com/part/PJ1084T",
        "controlled_use": "enclosure identity and catalog geometry; received wall survey still required",
    },
    {
        "source_id": "QIS-006",
        "manufacturer": "Hammond Manufacturing",
        "document": "14F0907 product and drawing",
        "revision_or_date": "drawing issue 2020-01-29; checked 2026-08-10",
        "official_locator": "https://www.hammfg.com/part/14F0907",
        "controlled_use": "panel identity, geometry and four-hole pattern",
    },
    {
        "source_id": "QIS-007",
        "manufacturer": "Phoenix Contact",
        "document": "1207650 live product record",
        "revision_or_date": "live record; checked 2026-08-10",
        "official_locator": "https://www.phoenixcontact.com/en-pc/products/din-rail-perforated-ns-35-75-perf-500mm-1207650",
        "controlled_use": "rail identity, dimensions, perforation and catalog tolerances",
    },
    {
        "source_id": "QIS-008",
        "manufacturer": "Phoenix Contact",
        "document": "PTCB and terminal live product records",
        "revision_or_date": "live records; checked 2026-08-10",
        "official_locator": "https://www.phoenixcontact.com/en-us/products/electronic-circuit-breaker-ptcb-e1-24dc-01a-no-1464484",
        "controlled_use": "catalog installed-width and height envelopes only",
    },
]
for record in sources:
    record["warning"] = WARNING

evidence = [
    ("QIE-001", "gland connecting thread", "M12 x 1.5", "QIS-003", "SOURCE VERIFIED", "not a through-hole diameter"),
    ("QIE-002", "gland thread length", "8 mm", "QIS-003; QIS-002", "SOURCE VERIFIED", "received wall/locknut engagement remains unverified"),
    ("QIE-003", "cable sealing range", "3.5 to 7.0 mm", "QIS-003; QIS-002", "SOURCE VERIFIED", "exact cable OD and sheath remain receiving inputs"),
    ("QIE-004", "installation torque M", "1.5 N m", "QIS-001; QIS-002", "MANUFACTURER BASELINE / APPLICATION HELD", "instruction applies M to threaded housing or locknut installation"),
    ("QIE-005", "cap-nut torque M", "1.5 N m", "QIS-001; QIS-002", "MANUFACTURER BASELINE / APPLICATION HELD", "LAPP warns cable constructions may require different torque to avoid sheath damage"),
    ("QIE-006", "separate locknut-torque certificate field", "blank / dash", "QIS-002", "AMBIGUITY RETAINED", "do not claim a separately certified 53119000 locknut torque"),
    ("QIE-007", "installation without locknut", "threaded hub only", "QIS-001", "SOURCE VERIFIED", "Project Button proposes a through-hole plus locknut; threaded-hub route is not selected"),
    ("QIE-008", "through-hole diameter and tolerance", "SELECTION REQUIRED", "QIS-001; QIS-002; QIS-003; QIS-004", "NOT PUBLISHED IN REVIEWED RECORDS", "received stack, qualified fit decision and coupon/inspection evidence required"),
    ("QIE-009", "gland body / locknut wrench envelopes", "15 mm / 17 mm across flats", "QIS-003; QIS-004", "SOURCE VERIFIED", "tool access and molded-wall clearance remain unverified"),
    ("QIE-010", "rail perforation", "15 x 6.2 mm at 25 mm pitch", "QIS-007", "SOURCE VERIFIED", "exact fastener and received slot realization remain open"),
    ("QIE-011", "rail dimensional tolerance", "+/-0.5 mm published categories", "QIS-007", "SOURCE VERIFIED", "measure the received cut datum and first/last slot centers"),
    ("QIE-012", "completed modified-enclosure rating", "SELECTION REQUIRED", "QIS-001; QIS-005", "NOT TRANSFERRED", "component/enclosure catalog ratings do not approve the drilled assembly"),
]
evidence_records = [
    {
        "record_id": item[0],
        "parameter": item[1],
        "manufacturer_value": item[2],
        "source_ids": item[3],
        "disposition": item[4],
        "application_boundary": item[5],
        "warning": WARNING,
    }
    for item in evidence
]

lot = [
    ("QRL-001", "PJ1084T", "Hammond Manufacturing", "1", "enclosure survey article"),
    ("QRL-002", "14F0907", "Hammond Manufacturing", "1", "panel survey article"),
    ("QRL-003", "1207650", "Phoenix Contact", "1 usable 500 mm rail; supplier pack quantity SELECTION REQUIRED", "rail survey/cut-planning article"),
    ("QRL-004", "53111000", "LAPP", "2", "G1/G2 gland fit articles"),
    ("QRL-005", "53119000", "LAPP", "2", "G1/G2 locknut fit articles"),
    ("QRL-006", "1464484", "Phoenix Contact", "1", "catalog-envelope/device-retention article"),
    ("QRL-007", "3209578", "Phoenix Contact", "1", "PT 2.5-QUATTRO catalog-envelope article"),
    ("QRL-008", "3209510", "Phoenix Contact", "5", "PT 2.5 catalog-envelope articles"),
    ("QRL-009", "3030417", "Phoenix Contact", "2", "D-ST 2.5 end-cover articles"),
    ("QRL-010", "3022218", "Phoenix Contact", "2", "CLIPFIX 35 end-bracket articles"),
]
lot_records = [
    {
        "line_id": item[0],
        "manufacturer_part_number": item[1],
        "manufacturer": item[2],
        "evaluation_quantity": item[3],
        "purpose": item[4],
        "seller": "SELECTION REQUIRED",
        "price_and_availability": "SELECTION REQUIRED",
        "purchase_authority": "NOT AUTHORIZED",
        "receiving_state": "NOT RECEIVED",
        "warning": WARNING,
    }
    for item in lot
]

metrology = [
    ("QMP-001", "configuration freeze", "accepted commit, signed acquisition line IDs, supplier and lot records", "all exact identities and quantities match", "configuration manager"),
    ("QMP-002", "package/marking inspection", "labels, order codes, quantity, damage and traceability photographs", "every line reconciles or remains quarantined", "receiver"),
    ("QMP-003", "panel geometry", "X/Y/thickness, four-hole diameter and center spans", "compare with R185 without assuming catalog tolerance", "qualified dimensional inspector"),
    ("QMP-004", "enclosure wall map", "wall flats, ribs, bosses, feet, hinge/latch zones, local thickness and lid clearance", "complete coordinate map with uncertainty", "qualified dimensional inspector"),
    ("QMP-005", "rail realization", "overall width/depth, first/last slot centers, pitch and burr/cut-datum observations", "received values and uncertainty recorded", "qualified dimensional inspector"),
    ("QMP-006", "gland geometry", "thread major diameter/pitch/length, body envelope and wrench access", "two articles measured and reconciled", "qualified dimensional inspector"),
    ("QMP-007", "locknut geometry", "thread, across-flats/corners and thickness", "two articles measured and reconciled", "qualified dimensional inspector"),
    ("QMP-008", "dry device-group fit", "orientation, installed width, end-cover side/count, CLIPFIX retention and marker access", "fit documented without panel drilling", "qualified electrical assembler"),
    ("QMP-009", "bore decision", "received stack, material/process review, tool capability and inspection method", "signed diameter/tolerance/edge-finish decision", "qualified mechanical/electrical reviewers"),
    ("QMP-010", "installation process", "calibrated torque tool, exact cable/sheath, wrench access and coupon evidence if required", "signed process resolves QIE-004..008 without damage or unsupported rating claim", "qualified mechanical/electrical reviewers"),
]
metrology_records = [
    {
        "step_id": item[0],
        "activity": item[1],
        "required_evidence": item[2],
        "acceptance_boundary": item[3],
        "required_role": item[4],
        "executor": "SELECTION REQUIRED",
        "instrument_and_calibration": "SELECTION REQUIRED",
        "result": "NOT EXECUTED",
        "evidence_uri": "NOT EXECUTED",
        "decision": "NOT APPROVED",
        "warning": WARNING,
    }
    for item in metrology
]

holds = [
    ("QIH-001", "program purchase decision", "signed line-level acquisition authority, seller, price ceiling, ship-to and receiving owner"),
    ("QIH-002", "supplier and pack form", "dated cart/quote confirms exact MPNs, quantities, pack sizes, seller and no substitution"),
    ("QIH-003", "received identities", "complete QMP-001..007 records with photographs, calibration and quarantine disposition"),
    ("QIH-004", "gland bore", "qualified received-stack diameter/tolerance/edge/tool and inspection decision"),
    ("QIH-005", "gland coordinates", "received enclosure wall map, tool access, cable separation/bend and no-interference review"),
    ("QIH-006", "rail coordinates and hardware", "received slot map plus exact screw/nut/washer/retention stack and panel-bearing review"),
    ("QIH-007", "torque process", "resolve instruction-sheet/VDE locknut wording, exact cable/sheath response and calibrated-tool method"),
    ("QIH-008", "modified enclosure", "ingress, strain relief, thermal, service access, labels and finished-rating disposition"),
    ("QIH-009", "grounding/isolation", "qualified Boston review of isolated rail, drain park, analog ground and robot-domain separation"),
    ("QIH-010", "physical work authority", "separate signed drilling/cutting/assembly authorization bound to final drawing and evidence"),
    ("QIH-011", "qualified release review", "mechanical and electrical reviewers accept final drawing, stack, process and inspection plan"),
]
hold_records = [
    {"hold_id": item[0], "scope": item[1], "evidence_required": item[2], "state": "OPEN", "warning": WARNING}
    for item in holds
]

hashes = [
    {
        "file_role": "LAPP instruction sheet",
        "official_locator": sources[0]["official_locator"],
        "sha256": "AD85793D470B538D5007E01A5A0F58F561C59B0EE8E4DC4DFAD764451F7A0646",
        "redistributed": "no",
        "checked": DATE,
        "warning": WARNING,
    },
    {
        "file_role": "LAPP / VDE certificate",
        "official_locator": sources[1]["official_locator"],
        "sha256": "5CA80372044C2E456266D5E3AAC671174749E48388238FAF2E7ADFA6A87C6E29",
        "redistributed": "no",
        "checked": DATE,
        "warning": WARNING,
    },
]

write_csv(PKG / "source-register.csv", list(sources[0]), sources)
write_csv(PKG / "installation-evidence.csv", list(evidence_records[0]), evidence_records)
write_csv(PKG / "receiving-lot.csv", list(lot_records[0]), lot_records)
write_csv(PKG / "metrology-plan.csv", list(metrology_records[0]), metrology_records)
write_csv(PKG / "closure-holds.csv", list(hold_records[0]), hold_records)
write_csv(PKG / "vendor-file-hashes.csv", list(hashes[0]), hashes)
write_csv(FORM, list(metrology_records[0]), metrology_records)

status = {
    "identifier": IDENTIFIER,
    "round": "R186",
    "date": DATE,
    "manufacturer_torque_baseline_Nm": 1.5,
    "through_hole_diameter": "SELECTION REQUIRED",
    "separate_locknut_torque_certificate_field": "blank",
    "receiving_lines": len(lot_records),
    "metrology_steps": len(metrology_records),
    "open_holds": len(hold_records),
    "executed_physical_steps": 0,
    "procurement_authorized": False,
    "fabrication_authorized": False,
    "energization_authorized": False,
    "warning": WARNING,
}
PKG.mkdir(parents=True, exist_ok=True)
(PKG / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")

DOC.parent.mkdir(parents=True, exist_ok=True)
DOC.write_text(
    f"""# HR-V0 Q4X installation evidence and receiving package P0.1

> **{WARNING}**

Artifact: **{IDENTIFIER}**

Round: **R186**

Date: **{DATE}**

## Outcome

R186 makes the next physical-evidence step executable on paper without releasing a purchase or a hole. LAPP instruction `99990621 / BS00/2622 VS20` applies torque `M = 1.5 N m` to M12 gland installation into a housing or with a locknut and to the cap nut. The VDE certificate updated 2022-10-21 also lists 1.5 N m installation and cap-nut torque, but its separate locknut-torque field is blank. The package preserves that distinction.

No reviewed LAPP record gives a Project Button through-hole diameter or tolerance. The bore, G1/G2 coordinates, rail hardware, modified-enclosure rating and physical work authority therefore remain `SELECTION REQUIRED`.

## What can happen next

Only after a separately signed acquisition decision may the exact ten-line evaluation lot be purchased and received. The ten-step metrology plan then records the enclosure wall map, panel, rail-slot realization, gland/locknut geometry and a dry DIN-device fit. All result fields are blank and `NOT EXECUTED`.

The final bore and drilling drawing require received measurements, calibrated tools, exact cable/sheath evidence and qualified mechanical/electrical review. Catalog torque is an installation input, not proof that a drilled fiberglass enclosure retains any catalog rating.

## Controlled artifacts

- source, installation, lot, metrology, hash and hold registers: `test-equipment/hr-v0/q4x-installation-evidence-p0.1/`;
- blank receiving/metrology form: `tests/forms/hr-v0-q4x-hardware-receiving-template-p0.1.csv`; and
- interactive evidence guide: `release/hr-v0/q4x-installation-evidence-p0.1/index.html`.

## Gate effect

R186 closes no energization gate and no Sol R12 blocker. It reduces an undocumented torque question to a bounded manufacturer/application decision, but all eleven `QIH-*` holds remain open. `EG-025` remains open and `EG-026` remains partial.
""",
    encoding="utf-8",
)


def table(records: list[dict[str, object]], columns: list[str]) -> str:
    head = "".join(f"<th>{escape(c.replace('_', ' ').title())}</th>" for c in columns)
    body = "".join(
        "<tr>" + "".join(f"<td>{escape(str(row[c]))}</td>" for c in columns) + "</tr>"
        for row in records
    )
    return f"<div class='table-wrap'><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>"


WEB.mkdir(parents=True, exist_ok=True)
html = f"""<!doctype html>
<html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
<title>{IDENTIFIER}</title><style>
:root{{--sky:#dff4ff;--blue:#092f63;--mid:#1469a8;--gold:#f5bf27;--ink:#102033;--paper:#f7fbff;--line:#8bb6d3;--red:#9b2335}}
*{{box-sizing:border-box}}html,body{{max-width:100%}}body{{margin:0;font:16px/1.55 system-ui,sans-serif;color:var(--ink);background:var(--paper);overflow-x:hidden}}
header{{padding:clamp(24px,5vw,64px);background:linear-gradient(135deg,var(--sky),#fff);border-bottom:8px solid var(--gold)}}
main{{max-width:1240px;margin:auto;padding:clamp(18px,4vw,48px)}}h1{{font-size:clamp(34px,6vw,68px);line-height:1.05;color:var(--blue);margin:.3rem 0;overflow-wrap:anywhere}}
h2{{font-size:clamp(26px,3vw,40px);color:var(--blue);margin-top:2.4rem}}.lead{{font-size:20px;max-width:950px}}.warn{{background:#fff2bd;border:3px solid #765800;padding:18px;font-weight:800;color:#473400;overflow-wrap:anywhere}}
.metrics,.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,250px),1fr));gap:16px}}.metric,article{{background:#fff;border:2px solid var(--line);border-radius:14px;padding:18px;box-shadow:0 5px 0 #d3eaf7}}
.metric strong{{display:block;color:var(--blue);font-size:30px}}.badge{{display:inline-block;max-width:100%;font-size:14px;font-weight:800;background:var(--gold);color:#17253b;border-radius:999px;padding:6px 10px;white-space:normal;overflow-wrap:anywhere}}
.decision{{border-left:9px solid var(--gold)}}.hold{{border-left:9px solid var(--red)}}.tabs{{display:flex;gap:8px;flex-wrap:wrap;margin:20px 0 12px}}button{{font:inherit;font-weight:750;border:2px solid var(--blue);background:#fff;color:var(--blue);padding:10px 14px;border-radius:9px;cursor:pointer}}button[aria-selected='true']{{background:var(--blue);color:#fff}}
.panel{{display:none}}.panel.active{{display:block}}.table-wrap{{max-width:100%;overflow:auto;border:2px solid var(--line);border-radius:12px}}table{{border-collapse:collapse;width:100%;min-width:1050px;background:#fff}}th,td{{text-align:left;vertical-align:top;padding:12px;border-bottom:1px solid #c6dce9;font-size:14px}}th{{background:var(--blue);color:#fff}}
footer{{margin-top:36px;padding:24px;background:var(--blue);color:#fff;overflow-wrap:anywhere}}@media(max-width:720px){{header,main{{padding:18px}}.lead{{font-size:18px}}}}
</style></head><body><header><span class='badge'>R186 · RECEIVING AND METROLOGY PLAN</span><h1>One torque value is documented. The hole is still not.</h1>
<p class='lead'>The exact LAPP records now bound the M12 installation process while preserving the missing bore and separate-locknut evidence. This is the bridge to received-part metrology, not a shortcut around it.</p></header><main>
<p class='warn'>{escape(WARNING)}</p>
<section class='metrics'><div class='metric'><strong>1.5 N·m</strong>LAPP M12 installation/cap-nut baseline</div><div class='metric'><strong>10</strong>exact receiving lines</div><div class='metric'><strong>10</strong>unexecuted metrology steps</div><div class='metric'><strong>0</strong>released holes</div></section>
<h2>The source boundary</h2><section class='grid'><article class='decision'><h3>Manufacturer statement</h3><p>The instruction applies torque M to gland installation with a locknut and to the cap nut. For M12, M is 1.5 N·m.</p></article><article class='hold'><h3>What stays open</h3><p>The VDE table leaves separate locknut torque blank. No reviewed record provides the through-hole diameter. Exact cable/sheath behavior and completed-enclosure rating require evidence.</p></article></section>
<div class='tabs' role='tablist'><button data-tab='evidence' aria-selected='true'>Installation evidence</button><button data-tab='lot' aria-selected='false'>Receiving lot</button><button data-tab='plan' aria-selected='false'>Metrology plan</button><button data-tab='holds' aria-selected='false'>Open holds</button></div>
<section id='evidence' class='panel active'>{table(evidence_records, ['record_id','parameter','manufacturer_value','source_ids','disposition','application_boundary'])}</section>
<section id='lot' class='panel'>{table(lot_records, ['line_id','manufacturer_part_number','manufacturer','evaluation_quantity','purpose','seller','purchase_authority','receiving_state'])}</section>
<section id='plan' class='panel'>{table(metrology_records, ['step_id','activity','required_evidence','acceptance_boundary','required_role','instrument_and_calibration','result','decision'])}</section>
<section id='holds' class='panel'>{table(hold_records, ['hold_id','scope','evidence_required','state'])}</section>
<footer>{escape(WARNING)} · Artifact {IDENTIFIER}</footer></main><script>
const buttons=[...document.querySelectorAll('[data-tab]')];buttons.forEach(button=>button.addEventListener('click',()=>{{buttons.forEach(b=>b.setAttribute('aria-selected','false'));document.querySelectorAll('.panel').forEach(p=>p.classList.remove('active'));button.setAttribute('aria-selected','true');document.getElementById(button.dataset.tab).classList.add('active')}}));
</script></body></html>"""
(WEB / "index.html").write_text(html + "\n", encoding="utf-8")

print(
    f"generated {IDENTIFIER}: {len(evidence_records)} evidence rows, "
    f"{len(lot_records)} receiving lines, {len(metrology_records)} blank steps, "
    f"{len(hold_records)} open holds"
)
