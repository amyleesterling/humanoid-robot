#!/usr/bin/env python3
"""Generate R258 deterministic, recipient-isolated, UNSENT Lot A bundles."""
from __future__ import annotations

import csv
import hashlib
import html
import io
import json
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import generate_hr_v0_lot_a_inquiry_p03 as inquiry  # noqa: E402

ID = "HR-V0-LOT-A-TX-BUNDLE-P0.1"
CID = "HR-V0-CONFIG-REC-P0.22"
WARNING = inquiry.WARNING
OUT = ROOT / "procurement/hr-v0/lot-a-transmission-bundles-p0.1"
REL = ROOT / "release/hr-v0/lot-a-transmission-bundles-p0.1"
SOURCE = ROOT / "procurement/hr-v0/lot-a-inquiry-p0.3"
CFG0 = ROOT / "configuration/hr-v0-config-reconciliation-p0.21"
CFG = ROOT / "configuration/hr-v0-config-reconciliation-p0.22"
CFGR = ROOT / "release/hr-v0/configuration-reconciliation-p0.22"
FIXED_ZIP_TIME = (1980, 1, 1, 0, 0, 0)


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def csv_bytes(fields: list[str], rows: list[dict[str, object]]) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows({field: row.get(field, "") for field in fields} for row in rows)
    return stream.getvalue().encode("utf-8")


def zip_info(name: str) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, FIXED_ZIP_TIME)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.create_system = 3
    info.external_attr = 0o100644 << 16
    info.flag_bits = 0x800
    return info


def route_payload(route: dict[str, str]) -> dict[str, bytes]:
    route_id = route["route_id"]
    organization = route["organization"]
    members: dict[str, bytes] = {}
    if route_id == "R257-RT-01":
        question_range = "R257-RQ-01..08"
        purpose = "sales/order identity, contents, allocation, quote, condition, substitution and shipping questions"
    elif route_id == "R257-RT-02":
        question_range = "R257-RQ-09..12"
        purpose = "technical assembly-document, hardware, torque/locking/reuse and response-authority questions"
    else:
        question_range = "33 route-specific questions plus R256-MZ-001..018"
        purpose = "exact-feature task-specific metrology capability and quotation"
    message = f"""# UNSENT Project Button Lot A inquiry — {route_id}

> **{WARNING}**

Intended organization: **{organization}**

Official public route: **{route['official_route']}**
Controlled scope: **{question_range}** — {purpose}.

This recipient-specific bundle is a frozen review candidate. It is **NOT AUTHORIZED** and **NOT SENT**. It is not an order, reservation, shipment instruction, work authorization, acceptance limit, assembly instruction or safety approval. Sender identity and reply address remain `SELECTION REQUIRED`.

Return only the included response workbooks with attributable, dated evidence. Do not substitute products, receive articles, incur cost, subcontract work or begin measurement without later configuration-specific written authority.
"""
    members["00-CONTROL/UNSENT-message.md"] = message.encode("utf-8")

    control = {
        "identifier": ID,
        "round": "R258",
        "date": "2026-08-12",
        "source_inquiry": "HR-V0-LOT-A-INQUIRY-P0.3",
        "route_id": route_id,
        "organization": organization,
        "official_public_route": route["official_route"],
        "sender_identity": "SELECTION REQUIRED",
        "reply_address": "SELECTION REQUIRED",
        "send_authorization": "NOT AUTHORIZED",
        "sent_state": "NOT SENT",
        "procurement_authorized": False,
        "work_authorized": False,
        "warning": WARNING,
    }
    members["00-CONTROL/bundle-control.json"] = (json.dumps(control, indent=2) + "\n").encode("utf-8")

    questions = [row for row in inquiry.old.read_csv(SOURCE / "robotis-question-register.csv")[0] if row["route_id"] == route_id]
    if route_id not in {"R257-RT-01", "R257-RT-02"}:
        questions = [row for row in inquiry.old.read_csv(SOURCE / "metrology-question-register.csv")[0] if row["route_id"] == route_id]
    question_fields = list(questions[0])
    members["01-RESPONSE/question-response.csv"] = csv_bytes(question_fields, questions)

    if route_id not in {"R257-RT-01", "R257-RT-02"}:
        characteristic = [row for row in inquiry.old.read_csv(SOURCE / "characteristic-bid-schedule.csv")[0] if row["route_id"] == route_id]
        methods = [row for row in inquiry.old.read_csv(SOURCE / "method-bid-schedule.csv")[0] if row["route_id"] == route_id]
        members["01-RESPONSE/characteristic-bid-response.csv"] = csv_bytes(list(characteristic[0]), characteristic)
        members["01-RESPONSE/method-bid-response.csv"] = csv_bytes(list(methods[0]), methods)
        attachments = inquiry.old.read_csv(SOURCE / "attachment-manifest.csv")[0]
        members["02-SCOPE/attachment-manifest.csv"] = csv_bytes(list(attachments[0]), attachments)
        for attachment in attachments:
            source_path = ROOT / attachment["path"]
            members[f"02-SCOPE/{attachment['attachment_id']}/{source_path.name}"] = source_path.read_bytes()

    readme = f"""{WARNING}

Bundle: {ID}
Route: {route_id}
Organization: {organization}
State: NOT AUTHORIZED / NOT SENT

Verify payload-manifest.csv before review. No file grants permission to contact, purchase, ship, assemble, connect, power, move or energize anything.
"""
    members["README.txt"] = readme.encode("utf-8")
    return members


def build_bundle(route: dict[str, str]) -> tuple[bytes, list[dict[str, object]]]:
    members = route_payload(route)
    manifest_rows = [{"path": name, "bytes": len(data), "sha256": sha_bytes(data), "route_id": route["route_id"], "state": "UNSENT / NOT AUTHORIZED", "warning": WARNING} for name, data in sorted(members.items())]
    manifest_data = csv_bytes(list(manifest_rows[0]), manifest_rows)
    members["payload-manifest.csv"] = manifest_data
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in sorted(members.items()):
            archive.writestr(zip_info(name), data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    all_rows = manifest_rows + [{"path": "payload-manifest.csv", "bytes": len(manifest_data), "sha256": sha_bytes(manifest_data), "route_id": route["route_id"], "state": "UNSENT / NOT AUTHORIZED", "warning": WARNING}]
    return stream.getvalue(), all_rows


def table(title: str, rows: list[dict[str, object]], fields: list[str]) -> str:
    head = "".join(f"<th>{html.escape(field.replace('_', ' ').title())}</th>" for field in fields)
    body = "".join("<tr>" + "".join(f"<td>{html.escape(str(row.get(field, '')))}</td>" for field in fields) + "</tr>" for row in rows)
    return f"<section><h2>{html.escape(title)}</h2><div class='scroll'><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div></section>"


def guide(bundles: list[dict[str, object]], gates: list[dict[str, object]], events: list[dict[str, object]]) -> str:
    cards = "".join(f"<article><h2>{row['route_id']}</h2><p>{html.escape(str(row['organization']))}</p><p><strong>{row['member_count']} files · {int(row['archive_bytes']) / 1024:.1f} KiB</strong></p><p><a href='{row['archive_path']}'>Inspect/download frozen UNSENT ZIP</a></p><code>{row['archive_sha256']}</code><p class='state'>NOT AUTHORIZED · NOT SENT</p></article>" for row in bundles)
    return f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>{ID}</title><style>:root{{--sky:#dff3ff;--blue:#092f57;--gold:#f3bd28;--ink:#102338;--paper:#f8fbfe;--line:#8eb9d8;--danger:#8d1721}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:clamp(16px,1.15vw,19px)/1.55 system-ui,sans-serif}}header{{padding:clamp(24px,5vw,68px);background:linear-gradient(135deg,var(--sky),#fff);border-bottom:8px solid var(--gold)}}main{{max-width:1500px;margin:auto;padding:24px}}h1{{font-size:clamp(34px,5vw,70px);line-height:1.05;color:var(--blue)}}h2{{font-size:clamp(23px,2.3vw,34px);color:var(--blue)}}.warn{{background:#fff4c7;border:3px solid var(--gold);padding:16px;font-weight:800}}.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px;margin:24px 0}}article,section{{background:#fff;border:2px solid var(--line);border-radius:14px;padding:18px;margin:18px 0}}article h2{{font-size:24px}}code{{display:block;overflow-wrap:anywhere;font-size:14px;line-height:1.45}}.state{{font-weight:850;color:var(--danger)}}a{{font-size:16px;font-weight:750;color:#075ea8}}.scroll{{overflow:auto}}table{{width:100%;border-collapse:collapse;min-width:980px;font-size:14px}}th,td{{text-align:left;vertical-align:top;padding:11px;border-bottom:1px solid #bed5e6;line-height:1.45}}th{{background:var(--blue);color:#fff;position:sticky;top:0}}@media(max-width:700px){{main{{padding:12px}}}}</style></head><body><header><p class='warn'>{WARNING}</p><h1>Recipient-isolated transmission bundles</h1><p>Five deterministic review archives. No archive is authorized or sent.</p></header><main><section><h2>Critical boundary</h2><p>These ZIP files exist for internal configuration review. External transmission remains prohibited until the exact archive, recipient, sender, reply address, malware scan, vendor-CAD redistribution rights and one-time authorization are accepted.</p></section><div class='cards'>{cards}</div>{table('Transmission decision gates',gates,['gate_id','decision','evidence_required','owner_role','state'])}{table('Blank transmission event register',events,['event_id','bundle_id','route_id','archive_sha256','authorization_evidence_uri','transport','recipient','sender','sent_utc','state'])}<section><h2>How to verify</h2><p>Every ZIP contains a route-specific message, fail-closed control JSON and payload manifest. The checker rebuilds every archive byte-for-byte, verifies CRCs and timestamps, and rejects cross-route question or bid leakage.</p></section></main></body></html>"""


def main() -> None:
    for directory in (OUT, REL, CFG, CFGR):
        if directory.exists():
            shutil.rmtree(directory)
    OUT.mkdir(parents=True)
    routes = inquiry.old.read_csv(SOURCE / "inquiry-route-register.csv")[0]
    bundle_rows = []
    member_rows = []
    for route in routes:
        route_id = route["route_id"]
        data, members = build_bundle(route)
        filename = f"UNSENT-{route_id}-payload.zip"
        (OUT / filename).write_bytes(data)
        bundle_rows.append({"bundle_id": f"R258-BDL-{route_id[-2:]}", "route_id": route_id, "organization": route["organization"], "official_public_route": route["official_route"], "archive_path": filename, "archive_bytes": len(data), "archive_sha256": sha_bytes(data), "member_count": len(members), "sender_identity": "SELECTION REQUIRED", "reply_address": "SELECTION REQUIRED", "authorization": "NOT AUTHORIZED", "transmission_state": "NOT SENT"})
        for member in members:
            member_rows.append({"bundle_id": f"R258-BDL-{route_id[-2:]}", **member})
    inquiry.old.write_csv(OUT / "bundle-register.csv", list(bundle_rows[0]) + ["warning"], inquiry.old.warned(bundle_rows))
    inquiry.old.write_csv(OUT / "bundle-member-register.csv", list(member_rows[0]) + ["warning"], inquiry.old.warned(member_rows))

    gates = [
        ("R258-GT-01", "Verify exact archive SHA-256 and deterministic reproduction", "dedicated checker and independent hash record", "CONFIGURATION"),
        ("R258-GT-02", "Confirm intended organization and current public route", "same-day attributable route check", "PROGRAM OWNER"),
        ("R258-GT-03", "Select sender identity and monitored reply address", "named adult-controlled identities", "PROGRAM OWNER"),
        ("R258-GT-04", "Review route-specific message and attachments", "signed no-leakage/content review", "CONFIGURATION + TECHNICAL"),
        ("R258-GT-05", "Scan exact archive before transmission", "current malware/content scan record", "INFORMATION SECURITY"),
        ("R258-GT-06", "Authorize one exact transmission", "signed route, archive hash, recipient, sender and expiry", "PROGRAM OWNER"),
        ("R258-GT-07", "Record actual transmission event", "timestamp, transport, recipient and archive hash", "SENDER"),
        ("R258-GT-08", "Verify provider receipt without authorizing work", "attributable receipt acknowledgement", "PROGRAM OWNER"),
        ("R258-GT-09", "Ingest and hash returned evidence", "immutable response register; no technical acceptance inferred", "CONFIGURATION"),
        ("R258-GT-10", "Prohibit stale/superseded bundle use", "P0.1/current-commit verification immediately before any send", "SENDER + CONFIGURATION"),
        ("R258-GT-11", "Accept redistribution authority for the three vendor STEP files", "current license/permission evidence covering external transmission to the exact recipient", "PROGRAM OWNER + LEGAL/CONFIGURATION"),
    ]
    gate_rows = [{"gate_id": gate, "decision": decision, "evidence_required": evidence, "owner_role": owner, "state": "OPEN"} for gate, decision, evidence, owner in gates]
    acceptance = [{"acceptance_id": f"R258-ACC-{index:02d}", "criterion": row["decision"], "execution_state": "NOT EXECUTED", "result": "OPEN", "evidence_uri": "", "approver": ""} for index, row in enumerate(gate_rows, 1)]
    events = [{"event_id": f"R258-EVT-{index:02d}", "bundle_id": row["bundle_id"], "route_id": row["route_id"], "archive_sha256": row["archive_sha256"], "authorization_evidence_uri": "", "transport": "", "recipient": "", "sender": "", "sent_utc": "", "receipt_evidence_uri": "", "state": "NOT SENT"} for index, row in enumerate(bundle_rows, 1)]
    inquiry.old.write_csv(OUT / "decision-gate.csv", list(gate_rows[0]) + ["warning"], inquiry.old.warned(gate_rows))
    inquiry.old.write_csv(OUT / "acceptance-matrix.csv", list(acceptance[0]) + ["warning"], inquiry.old.warned(acceptance))
    inquiry.old.write_csv(OUT / "transmission-event-register.csv", list(events[0]) + ["warning"], inquiry.old.warned(events))
    sources = [
        {"source_id": "R258-SRC-01", "source": "Lot A exact-feature inquiry P0.3", "path": "release/hr-v0/lot-a-inquiry-p0.3/package-status.json", "sha256": inquiry.old.sha(ROOT / "release/hr-v0/lot-a-inquiry-p0.3/package-status.json"), "use": "current unsent inquiry scope"},
        {"source_id": "R258-SRC-02", "source": "Joint measurement definition P0.1", "path": "release/hr-v0/joint-measurement-definition-p0.1/package-status.json", "sha256": inquiry.old.sha(ROOT / "release/hr-v0/joint-measurement-definition-p0.1/package-status.json"), "use": "79 features and 18 characteristics"},
    ]
    inquiry.old.write_csv(OUT / "source-register.csv", list(sources[0]) + ["warning"], inquiry.old.warned(sources))
    status = {"identifier": ID, "round": "R258", "date": "2026-08-12", "source_inquiry": "HR-V0-LOT-A-INQUIRY-P0.3", "recipient_bundles": 5, "deterministic_archives": True, "route_isolation_checked": True, "transmissions_authorized": 0, "messages_sent": 0, "responses_received": 0, "sender_identity_selected": False, "reply_address_selected": False, "provider_selected": False, "purchase_authorized": False, "work_authorized": False, "physical_articles_received": False, "assembly_authorized": False, "connection_authorized": False, "powered_testing_authorized": False, "motion_authorized": False, "energization_authorized": False, "qualified_review_complete": False, "safety_credit": False, "warning": WARNING}
    (OUT / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    (OUT / "index.html").write_text(guide(bundle_rows, gate_rows, events), encoding="utf-8")
    inquiry.old.manifest(OUT)
    shutil.copytree(OUT, REL)
    inquiry.old.manifest(REL)

    shutil.copytree(CFG0, CFG)
    current, fields = inquiry.old.read_csv(CFG / "current-configuration-map.csv")
    current.append({"record_id": "CFG-41", "role": "Deterministic recipient-isolated Lot A transmission bundles", "identifier": ID, "source_path": "release/hr-v0/lot-a-transmission-bundles-p0.1/package-status.json", "configuration_state": "CURRENT CONTROLLED DRAFT - FIVE ARCHIVES UNSENT", "release_boundary": "exact route-specific payloads; sender/reply/authorization/transmission open", "warning": WARNING})
    inquiry.old.write_csv(CFG / "current-configuration-map.csv", fields, current)
    supersession, fields = inquiry.old.read_csv(CFG / "supersession-map.csv")
    supersession.append({"record_id": "SUP-34", "prior_identifier": "HR-V0-CONFIG-REC-P0.21", "current_or_required_successor": CID, "disposition": "SUPERSEDED BY R258 CONFIGURATION RECORD ONLY", "use_authorized": "NO", "warning": WARNING})
    inquiry.old.write_csv(CFG / "supersession-map.csv", fields, supersession)
    holds, fields = inquiry.old.read_csv(CFG / "open-holds.csv")
    for index, gate in enumerate(gate_rows, 126):
        holds.append({"hold_id": f"HOLD-{index:03d}", "hold": f"{ID}: {gate['decision']}", "state": "OPEN", "closure_evidence": gate["evidence_required"], "warning": WARNING})
    inquiry.old.write_csv(CFG / "open-holds.csv", fields, holds)
    config_acceptance, fields = inquiry.old.read_csv(CFG / "acceptance-matrix.csv")
    for index, row in enumerate(acceptance, 159):
        config_acceptance.append({"acceptance_id": f"ACC-{index:03d}", "criterion": f"{ID}: {row['criterion']}", "execution_state": "NOT EXECUTED", "result": "OPEN", "evidence_uri": "", "approver": "", "warning": WARNING})
    inquiry.old.write_csv(CFG / "acceptance-matrix.csv", fields, config_acceptance)
    hashes, fields = inquiry.old.read_csv(CFG / "source-hash-register.csv")
    hashes.append({"source_path": "release/hr-v0/lot-a-transmission-bundles-p0.1/package-status.json", "sha256": inquiry.old.sha(REL / "package-status.json"), "role": "Recipient-isolated transmission bundle contract", "warning": WARNING})
    inquiry.old.write_csv(CFG / "source-hash-register.csv", fields, hashes)
    config_status = json.loads((CFG / "package-status.json").read_text(encoding="utf-8"))
    config_status.update({"identifier": CID, "round": "R258", "date": "2026-08-12", "current_records": 41, "supersession_records": 34, "open_holds": 136, "acceptance_rows": 169, "lot_a_transmission_bundles": ID})
    (CFG / "package-status.json").write_text(json.dumps(config_status, indent=2) + "\n", encoding="utf-8")
    (CFG / "README.md").write_text(f"# {CID}\n\n> **{WARNING}**\n\nR258 adds {ID}. Five deterministic archives exist, but all remain UNSENT and NOT AUTHORIZED. Vendor-CAD redistribution authority remains open. 136 holds and 169 unexecuted acceptances remain.\n", encoding="utf-8")
    (CFG / "index.html").write_text(guide(bundle_rows, gate_rows, events), encoding="utf-8")
    inquiry.old.manifest(CFG)
    shutil.copytree(CFG, CFGR)
    inquiry.old.manifest(CFGR)
    print(f"Generated {ID}: five deterministic isolated archives; zero transmissions/authority")


if __name__ == "__main__":
    main()
