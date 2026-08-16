#!/usr/bin/env python3
"""Generate the HR-30 physical protective-bonding implementation candidate.

The package selects only manufacturer-supported candidate hardware whose
interface is known. It intentionally leaves conductor capacity, moving-joint
jumpers, installation, measurements, review, and work authority open.
"""

from __future__ import annotations

import csv
import hashlib
import html
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WHOLE = ROOT / "hr30" / "whole-body-p0.1"
OUT = WHOLE / "electrical" / "protective-bonding-implementation-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / "electrical" / OUT.name
IDENTIFIER = "HR30-PROTECTIVE-BONDING-IMPLEMENTATION-P0.1"
DATE = "2026-08-16"
WARNING = "PRELIMINARY - UNBUILT BONDING IMPLEMENTATION CANDIDATE - NOT APPROVED FOR CONNECTION, POWERED TESTING, MOTION OR ENERGIZATION"
AUTHORITY = "NO PROCUREMENT, FABRICATION, CONNECTION, POWERED-TEST, MOTION OR ENERGIZATION AUTHORITY"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise RuntimeError(f"refusing empty CSV: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def common(row: dict[str, object]) -> dict[str, object]:
    return {**row, "execution_state": "NOT EXECUTED", "authority": AUTHORITY, "warning": WARNING}


def primary_sources() -> list[dict[str, object]]:
    data = [
        ("PB-S01", "Commonwealth of Massachusetts", "Massachusetts Electrical Code", "current page; accessed 2026-08-16", "https://www.mass.gov/info-details/massachusetts-electrical-code", "Massachusetts code basis; exact applicability and adopted amendments require AHJ/qualified review"),
        ("PB-S02", "City of Boston", "Electrical Permits", "current page; accessed 2026-08-16", "https://search.boston.gov/boston-permitting/permits/electrical-permits", "licensed-contractor, permit-before-work, and inspection process for covered electrical installations; applicability to this portable prototype remains an AHJ question"),
        ("PB-S03", "Hammond Manufacturing", "1418N4C6 product page", "live product page; accessed 2026-08-16", "https://www.hammfg.com/part/1418N4C6", "20 x 16 x 6 inch steel Type 4 enclosure candidate; UL file E65324; CSA LR21001; stocked-part discontinuation warning"),
        ("PB-S04", "Hammond Manufacturing", "1418N4 series product page", "live series page; accessed 2026-08-16", "https://www.hammfg.com/electrical/products/industrial/1418n4", "14-gauge steel body, 12-gauge panel, Type 4/IP66, door bonding stud and enclosure grounding stud"),
        ("PB-S05", "Hammond Manufacturing", "1418N4C6 dimensional drawing", "drawing dated 2019-03-24; accessed 2026-08-16", "https://www.hammfg.com/files/parts/pdf/1418N4C6.pdf?v=1697661930", "exact enclosure outline and factory grounding-stud locations; received revision still requires inspection"),
        ("PB-S06", "Phoenix Contact", "UT 10-PE protective conductor terminal", "item 3044173; manufacturer PDF generated 2026-06-24", "https://www.phoenixcontact.com/en-us/products/ground-terminal-block-ut-10-pe-3044173?type=pdf", "10 mm2 rated cross-section; 0.5-16 mm2 rigid/flexible; AWG 20-6 converted; M4; 1.5-1.8 Nm; IEC 60947-7-2; DIN-rail capacity caveat"),
        ("PB-S07", "Alpha Wire", "Premium hook-up wire 460619", "live official product page; accessed 2026-08-16", "https://www.alphawire.com/products/wire/hook-up-wire/premium/460619", "6 AWG, 19-strand bare copper, PVC, 600 V family; exact green/yellow order suffix and application release remain open"),
        ("PB-S08", "Anderson Power", "SBS assembly instructions", "1S6417; accessed 2026-08-16", "https://www.andersonpower.com/content/dam/app/ecommerce/product-pdfs/SBS75G/1s6417-SBS-Assembly-Instructions.pdf", "SBS75GBLK and 1340G1 6 AWG pre-mate contact family; crimp tooling, received parts and finished assembly require validation"),
    ]
    return [common({"source_id": i, "publisher": p, "document": d, "revision_or_date": rev, "accessed": DATE, "official_url": url, "verified_scope": scope}) for i, p, d, rev, url, scope in data]


def bindings() -> list[dict[str, object]]:
    data = [
        ("PB-B01", "authoritative PE/DC-reference topology", "electrical/grounding-reference-architecture-p0.1/grounding-reference-status.json"),
        ("PB-B02", "external panel and tether candidate", "electrical/tether-power-core-p0.1/power-core-status.json"),
        ("PB-B03", "tether cavity/contact assignments", "electrical/tether-power-core-p0.1/connector-contact-map.csv"),
        ("PB-B04", "whole-body harness boundary", "harness/physical-p0.1/physical-harness-status.json"),
        ("PB-B05", "whole-body logical ECAD boundary", "electrical/kicad/hr30-whole-body-electrical-p0.1/electrical-status.json"),
    ]
    rows = []
    for ident, role, rel in data:
        path = WHOLE / rel
        if not path.is_file():
            raise FileNotFoundError(path)
        rows.append(common({"binding_id": ident, "role": role, "path": path.relative_to(ROOT).as_posix(), "sha256": sha(path), "bytes": path.stat().st_size}))
    return rows


def site_basis() -> list[dict[str, object]]:
    data = [
        ("PB-J01", "location", "Boston, Massachusetts, USA", "FROZEN BY OWNER", "physical test address and supplying facility still required"),
        ("PB-J02", "code basis", "current Massachusetts Electrical Code", "AHJ CONFIRMATION REQUIRED", "qualified reviewer must freeze edition, amendments and applicability for the actual site"),
        ("PB-J03", "permit/inspection", "Boston electrical-permit process reviewed", "AHJ DETERMINATION REQUIRED", "do not infer that a portable experimental machine is exempt or covered; obtain written determination"),
        ("PB-J04", "facility supply", "not selected", "SELECTION REQUIRED", "receptacle, branch OCPD, grounding system, available fault current and disconnect arrangement"),
        ("PB-J05", "enclosure", "Hammond 1418N4C6 candidate", "CANDIDATE - RECEIPT/AVAILABILITY REQUIRED", "part is being discontinued; exact received enclosure, panel and factory studs must be inspected"),
    ]
    return [common({"basis_id": i, "topic": topic, "current_basis": basis, "disposition": disposition, "closure_evidence": evidence}) for i, topic, basis, disposition, evidence in data]


def hardware() -> list[dict[str, object]]:
    data = [
        ("PB-HW01", "external enclosure", "Hammond", "1418N4C6", "CANDIDATE", "factory body grounding stud", "received identity, stud size/finish, availability and qualified installation review"),
        ("PB-HW02", "enclosure door bond point", "Hammond", "factory door bonding stud on 1418N4 series", "CANDIDATE", "dedicated door jumper landing", "received identity, stud size/finish and door-jumper selection"),
        ("PB-HW03", "panel PE terminal", "Phoenix Contact", "UT 10-PE / 3044173", "CANDIDATE", "NS 35 DIN-rail protective conductor terminal", "rail selection/capacity, conductor fit, ferrule disposition, torque and qualified sizing"),
        ("PB-HW04", "panel PE conductor family", "Alpha Wire", "460619 family / exact green-yellow order code SELECTION REQUIRED", "CANDIDATE FAMILY", "fixed protected internal panel routing; 6 AWG", "color-specific order code, ampacity/fault sizing, bend/routing, terminal/contact compatibility and supplier CoC"),
        ("PB-HW05", "tether pre-mate PE contact", "Anderson Power", "1340G1 in SBS75GBLK G cavity", "CANDIDATE", "6 AWG pre-mate contact family", "crimp tool/die, pull test, conductor fit, contact retention, polarity and received assembly"),
        ("PB-HW06", "robot pelvis bond hub", "SELECTION REQUIRED", "SELECTION REQUIRED", "UNSELECTED", "single serviceable frame-bond hub at pelvis", "stud/terminal material, anti-rotation, corrosion, torque, cover, access and drawing"),
        ("PB-HW07", "moving-joint bond jumper", "SELECTION REQUIRED", "high-flex green-yellow conductor plus terminations", "UNSELECTED", "bypass every non-credited bearing/joint interface", "fault sizing, continuous-flex life, bend radius, strand fatigue, lugs, retention and supplier data"),
        ("PB-HW08", "BR1 removable DC-return/PE link", "SELECTION REQUIRED", "labeled service-removable link at RB0", "UNSELECTED", "sole proposed intentional DC-return/frame bond", "hardware, touch protection, current/fault/EMC analysis, removal controls and qualified approval"),
        ("PB-HW09", "bond fasteners/contact preparation", "SELECTION REQUIRED", "SELECTION REQUIRED", "UNSELECTED", "dedicated studs, locking hardware and controlled conductive surface", "substrate/coating stack, galvanic compatibility, washer/locking method, torque and corrosion protection"),
    ]
    return [common({"hardware_id": i, "function": function, "manufacturer": maker, "candidate": candidate, "disposition": disposition, "controlled_use": use, "remaining_evidence": evidence, "procurement_released": "NO"}) for i, function, maker, candidate, disposition, use, evidence in data]


def sizing_inputs() -> list[dict[str, object]]:
    data = [
        ("PB-SZ01", "available fault current at facility/panel", "A", "SELECTION REQUIRED"),
        ("PB-SZ02", "upstream protective-device type/rating/curve", "identifier", "SELECTION REQUIRED"),
        ("PB-SZ03", "maximum permitted clearing time", "s", "SELECTION REQUIRED"),
        ("PB-SZ04", "each bond-path length including tether", "m", "SELECTION REQUIRED"),
        ("PB-SZ05", "ambient temperature and enclosure rise", "degC", "SELECTION REQUIRED"),
        ("PB-SZ06", "bundling, conduit and installation method", "classification", "SELECTION REQUIRED"),
        ("PB-SZ07", "terminal/contact/lug conductor limits", "mm2/AWG", "SELECTION REQUIRED"),
        ("PB-SZ08", "flex duty, bend radius and cycle target", "cycles/mm", "SELECTION REQUIRED"),
        ("PB-SZ09", "material, plating, corrosion and contamination environment", "classification", "SELECTION REQUIRED"),
        ("PB-SZ10", "jurisdictional conductor-sizing rule and qualified calculation", "document", "SELECTION REQUIRED"),
    ]
    return [common({"input_id": i, "required_input": name, "unit": unit, "current_value": value, "calculation_released": "NO"}) for i, name, unit, value in data]


def bond_zones() -> list[dict[str, object]]:
    data = [
        ("PB-Z01", "external panel body", "factory enclosure grounding stud", "UT 10-PE panel hub", "fixed jumper", "PB-HW04/PB-HW09"),
        ("PB-Z02", "external panel door", "factory door bonding stud", "panel body/PE hub", "door flex jumper", "SELECTION REQUIRED"),
        ("PB-Z03", "RSP-500-12 frame/FG", "manufacturer FG terminal", "UT 10-PE panel hub", "fixed jumper", "SELECTION REQUIRED"),
        ("PB-Z04", "SD-15A-24 frame/FG", "manufacturer FG terminal", "UT 10-PE panel hub", "fixed jumper", "SELECTION REQUIRED"),
        ("PB-Z05", "tether PE", "XT1A/XT1B center G cavity", "panel hub to pelvis hub", "SBS75G + tether conductor", "PB-HW04/PB-HW05"),
        ("PB-Z06", "pelvis", "single accessible frame-bond hub", "XT1B G and all robot jumpers", "hub", "PB-HW06"),
        ("PB-Z07", "torso", "upper-pelvis/torso conductive tray", "pelvis hub", "fixed or flex jumper", "PB-HW07/PB-HW09"),
        ("PB-Z08", "head and neck", "head carrier conductive zone", "torso", "neck bypass jumper", "PB-HW07/PB-HW09"),
        ("PB-Z09", "left arm and hand", "proximal/distal conductive zones", "torso", "shoulder/elbow/wrist bypasses", "PB-HW07/PB-HW09"),
        ("PB-Z10", "right arm and hand", "proximal/distal conductive zones", "torso", "shoulder/elbow/wrist bypasses", "PB-HW07/PB-HW09"),
        ("PB-Z11", "left leg and foot", "thigh/shank/foot conductive zones", "pelvis", "hip/knee/ankle bypasses", "PB-HW07/PB-HW09"),
        ("PB-Z12", "right leg and foot", "thigh/shank/foot conductive zones", "pelvis", "hip/knee/ankle bypasses", "PB-HW07/PB-HW09"),
        ("PB-Z13", "DC return bus RB0", "covered service point", "pelvis bond hub", "one removable BR1 only", "PB-HW08"),
    ]
    return [common({"zone_id": i, "module_or_zone": module, "candidate_landing": landing, "bonded_to": bonded, "path_type": path_type, "hardware_binding": binding, "installed": "NO", "measured": "NO"}) for i, module, landing, bonded, path_type, binding in data]


def bypasses() -> list[dict[str, object]]:
    names = ["neck", "waist", "left shoulder", "right shoulder", "left elbow", "right elbow", "left wrist", "right wrist", "left hip", "right hip", "left knee", "right knee", "left ankle", "right ankle"]
    return [common({"bypass_id": f"PB-JB{i:02d}", "moving_interface": name, "bearing_or_joint_conductivity_credited": "NO", "candidate_route": "external serviceable slack loop outside pinch envelope", "jumper_product": "SELECTION REQUIRED", "bend_radius_and_slack": "SELECTION REQUIRED", "retention": "SELECTION REQUIRED", "worst_pose_tested": "NO"}) for i, name in enumerate(names, 1)]


def installation_steps() -> list[dict[str, object]]:
    steps = [
        ("PB-I01", "Receive and photograph enclosure, panel, factory body stud and door stud; record revision/serial/finish"),
        ("PB-I02", "Obtain written AHJ/site applicability determination and qualified electrical basis"),
        ("PB-I03", "Measure facility supply, branch protection and available fault-current inputs using an approved method"),
        ("PB-I04", "Complete and approve the protective-conductor sizing/clearing calculation"),
        ("PB-I05", "Release exact conductor, ferrule/lug, DIN rail, terminal, stud and locking hardware"),
        ("PB-I06", "Install DIN rail and UT 10-PE terminal per manufacturer and panel drawing"),
        ("PB-I07", "Prepare only controlled bonding surfaces; preserve corrosion protection outside the contact zone"),
        ("PB-I08", "Install panel body, door, source FG and tether-G bonds; record torque and witness"),
        ("PB-I09", "Crimp SBS75G G contact with released tooling; inspect, measure and pull-test coupon/assembly"),
        ("PB-I10", "Install a covered, labeled pelvis frame-bond hub and the tether-G landing"),
        ("PB-I11", "Install every fixed module bond and every articulated-joint bypass without entering pinch/cable envelopes"),
        ("PB-I12", "Install BR1 only after its qualified disposition; otherwise keep it absent and record configuration open"),
        ("PB-I13", "Label PE, frame hub, BR1 and every module jumper at both ends"),
        ("PB-I14", "Inspect conductor routing, bend radius, abrasion, service loops, retention and touch protection"),
        ("PB-I15", "Execute unpowered continuity, insulation and single-bond-count measurements at worst joint poses"),
        ("PB-I16", "Freeze as-built photos, serials, torque records, measurement files and qualified disposition before any separate connection request"),
    ]
    return [common({"step_id": i, "operation": text, "performed_by": "UNASSIGNED", "witness": "UNASSIGNED", "record": "NONE", "complete": "NO"}) for i, text in steps]


def inspections() -> list[dict[str, object]]:
    data = [
        ("PB-T01", "panel body to PE hub continuity", "ohm", "SELECTION REQUIRED"),
        ("PB-T02", "door to PE hub continuity through full door travel", "ohm", "SELECTION REQUIRED"),
        ("PB-T03", "source FG terminals to PE hub continuity", "ohm", "SELECTION REQUIRED"),
        ("PB-T04", "SBS G contact end-to-end continuity and mate sequence", "ohm/event", "SELECTION REQUIRED"),
        ("PB-T05", "pelvis hub to each of 12 whole-body modules", "ohm", "SELECTION REQUIRED"),
        ("PB-T06", "each of 14 moving-interface bypasses at worst pose", "ohm", "SELECTION REQUIRED"),
        ("PB-T07", "intentional DC-return/frame bond count", "count", "EXACTLY ONE ONLY IF BR1 IS APPROVED"),
        ("PB-T08", "power-to-frame insulation with BR1 removed", "Mohm", "SELECTION REQUIRED"),
        ("PB-T09", "frame current under approved current-limited test", "mA", "SELECTION REQUIRED"),
        ("PB-T10", "bond-path temperature rise under approved test", "degC", "SELECTION REQUIRED"),
        ("PB-T11", "jumper retention and abrasion after flex cycle", "N/visual", "SELECTION REQUIRED"),
        ("PB-T12", "USB/SWD/oscilloscope accessory reference matrix", "ohm", "SELECTION REQUIRED"),
    ]
    return [common({"test_id": i, "inspection_or_measurement": item, "unit": unit, "acceptance_limit": limit, "instrument": "UNASSIGNED", "measured_value": "NONE", "result": "NOT EXECUTED", "evidence": "NONE"}) for i, item, unit, limit in data]


def holds() -> list[dict[str, object]]:
    data = [
        ("PB-OH01", "AHJ, facility supply, branch protection and enclosure applicability not frozen", "written AHJ/site determination and qualified electrical basis"),
        ("PB-OH02", "fault current and protective-device clearing behavior unmeasured", "approved measurement/calculation with source and upstream-device evidence"),
        ("PB-OH03", "protective conductor and termination sizing not released", "all ten sizing inputs, manufacturer limits and qualified calculation"),
        ("PB-OH04", "1418N4C6 availability and received grounding-stud construction unverified", "supplier confirmation plus incoming inspection against current drawing"),
        ("PB-OH05", "Alpha Wire 460619 exact green/yellow order code and SBS crimp compatibility open", "manufacturer/distributor quotation, conductor construction, tool/die and pull-test evidence"),
        ("PB-OH06", "pelvis hub, BR1 link and bond fasteners unselected", "dimensioned hardware drawing, material/coating/locking/torque and qualified review"),
        ("PB-OH07", "moving-joint high-flex jumper unselected", "manufacturer continuous-flex data, sizing, routing, fatigue and termination validation"),
        ("PB-OH08", "shield and external-instrument reference paths unresolved", "received-cable/accessory continuity matrix and EMC disposition"),
        ("PB-OH09", "acceptance limits, instruments and procedures unreleased", "qualified procedure, calibration, ratings and evidence templates"),
        ("PB-OH10", "nothing is installed, measured or signed", "fabricated as-built system, completed traveler, measurements and separate signed work release"),
    ]
    return [common({"hold_id": i, "unresolved_item": item, "closure_evidence": evidence, "state": "OPEN"}) for i, item, evidence in data]


def drawing() -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="940" viewBox="0 0 1600 940" role="img" aria-labelledby="title desc"><title id="title">HR-30 physical protective-bonding candidate</title><desc id="desc">Candidate panel and robot protective-earth implementation with selected interface families and unresolved conductor sizing.</desc><style>text{{font:600 18px system-ui;fill:#102b46}}.h{{font-size:31px;font-weight:900}}.s{{font-size:16px}}.box{{fill:#fff;stroke:#0b4f91;stroke-width:4}}.pe{{stroke:#16804a;stroke-width:10;fill:none}}.open{{stroke:#f2b91d;stroke-width:8;stroke-dasharray:16 10;fill:none}}.warn{{fill:#fff0b5;stroke:#982520;stroke-width:4}}</style><rect width="1600" height="940" fill="#eef8ff"/><text class="h" x="45" y="56">Physical protective-bonding candidate — unbuilt, unmeasured, unauthorized</text><rect class="box" x="45" y="115" width="435" height="430" rx="18"/><text x="75" y="158">External Hammond 1418N4C6 panel</text><text class="s" x="75" y="196">PB-HW03: UT 10-PE / 3044173 candidate hub</text><text class="s" x="75" y="230">factory body grounding stud</text><text class="s" x="75" y="264">factory door bonding stud + jumper (open)</text><text class="s" x="75" y="298">RSP-500-12 FG + SD-15A-24 FG</text><text class="s" x="75" y="332">PB-HW04: Alpha 460619 6 AWG family</text><text class="s" x="75" y="366">exact green/yellow order code: open</text><text class="s" x="75" y="400">fault/clearing/route sizing: open</text><rect class="box" x="600" y="115" width="360" height="260" rx="18"/><text x="630" y="158">Tether boundary</text><text class="s" x="630" y="198">SBS75GBLK center G cavity</text><text class="s" x="630" y="232">1340G1 6 AWG pre-mate contact</text><text class="s" x="630" y="266">tool/die/crimp/pull test: open</text><path class="pe" d="M480 260H600"/><rect class="box" x="1080" y="115" width="470" height="430" rx="18"/><text x="1110" y="158">Robot pelvis frame-bond hub</text><text class="s" x="1110" y="198">exact hub and fasteners: selection required</text><text class="s" x="1110" y="232">14 moving-joint bypass obligations</text><text class="s" x="1110" y="266">bearings/joints receive zero bond credit</text><text class="s" x="1110" y="300">head, torso, arms, hands, legs and feet</text><text class="s" x="1110" y="334">must pass worst-pose continuity</text><path class="pe" d="M960 260H1080"/><rect class="box" x="600" y="610" width="360" height="150" rx="18"/><text x="630" y="655">Robot DC return bus RB0</text><text class="s" x="630" y="694">normal current stays off frame</text><path class="open" d="M780 610V375"/><text x="805" y="515">BR1 — sole proposed link</text><text class="s" x="805" y="546">hardware + approval open</text><rect class="warn" x="45" y="820" width="1505" height="80" rx="18"/><text x="75" y="857">No conductor size is released until fault current, clearing time, route, ambient, flex, terminal limits and jurisdiction are frozen.</text><text class="s" x="75" y="884">No installation, test, connection or energization authority follows from this drawing.</text></svg>'''


def page(hw: list[dict[str, object]], zones: list[dict[str, object]], bypass: list[dict[str, object]], open_rows: list[dict[str, object]]) -> str:
    cards = "".join(f'<article><b>{html.escape(str(r["hardware_id"]))}</b><h3>{html.escape(str(r["function"]))}</h3><p>{html.escape(str(r["candidate"]))}</p><strong>{html.escape(str(r["disposition"]))}</strong></article>' for r in hw)
    holds_html = "".join(f'<li><b>{html.escape(str(r["hold_id"]))}</b> {html.escape(str(r["unresolved_item"]))}</li>' for r in open_rows)
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 protective-bonding implementation</title><style>:root{{--deep:#071d36;--blue:#0b4f91;--sky:#d9f2ff;--gold:#f2b91d;--paper:#f7fbff;--ink:#142a40;--line:#82c4e6;--red:#982520}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.55 system-ui,Segoe UI,sans-serif}}header,main,footer{{padding:clamp(24px,5vw,64px) max(18px,calc((100vw - 1280px)/2))}}header,footer{{background:linear-gradient(135deg,var(--deep),var(--blue));color:white}}h1{{font-size:clamp(38px,6vw,70px);line-height:1.04;max-width:18ch}}h2{{font-size:clamp(28px,4vw,44px)}}h3{{font-size:22px}}.warning{{background:var(--gold);color:#17243a;border:3px solid #805600;padding:16px;font-weight:900}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:18px}}article,.panel,li{{background:white;border:2px solid var(--line);border-radius:16px;padding:19px}}article strong{{color:var(--red)}}.metric{{font-size:clamp(34px,5vw,54px);font-weight:900;color:var(--blue)}}.scroll{{overflow:auto;border:2px solid var(--line);border-radius:16px;background:white}}object{{display:block;width:100%;min-width:1000px}}a{{color:#075b9b;font-weight:800}}li{{margin:12px 0}}small{{font-size:14px}}@media(max-width:560px){{body{{font-size:16px}}}}</style></head><body><header><div class="warning">{html.escape(WARNING)}</div><p>HR-30 whole-body P0.1</p><h1>The grounding topology now has an installable candidate kit.</h1><p>Manufacturer-supported enclosure, PE-terminal, tether-contact and fixed-panel conductor families are bound to real locations. Moving-joint jumpers, fault sizing and all physical proof remain open.</p></header><main><section class="grid"><article><div class="metric">{len(hw)}</div><p>hardware candidate or selection records</p></article><article><div class="metric">{len(zones)}</div><p>whole-robot bond zones</p></article><article><div class="metric">{len(bypass)}</div><p>moving-joint bypass obligations</p></article><article><div class="metric">0</div><p>installed or measured bonds</p></article></section><section><h2>Physical implementation drawing</h2><div class="scroll"><object data="protective-bonding-layout.svg" type="image/svg+xml" aria-label="Protective-bonding physical implementation candidate"></object></div></section><section><h2>Candidate hardware</h2><div class="grid">{cards}</div></section><section class="panel"><h2>Build and inspection records</h2><p><a href="bond-hardware-register.csv">Hardware register</a> · <a href="conductor-sizing-basis.csv">Sizing inputs</a> · <a href="robot-bond-zone-register.csv">Bond zones</a> · <a href="joint-bypass-obligation.csv">Joint bypasses</a> · <a href="installation-traveler.csv">Installation traveler</a> · <a href="inspection-measurement-plan.csv">Blank inspection plan</a> · <a href="primary-source-register.csv">Primary sources</a></p></section><section class="panel"><h2>Open holds</h2><ul>{holds_html}</ul><p><small>Candidate means suitable for controlled engineering review, not released for purchase or installation.</small></p></section></main><footer>{html.escape(WARNING)}</footer></body></html>'''


def integrate_root(hw_count: int, zone_count: int, bypass_count: int) -> None:
    status_path = WHOLE / "package-status.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    status.update({
        "protective_bonding_implementation_present": True,
        "protective_bonding_hardware_record_count": hw_count,
        "protective_bonding_zone_count": zone_count,
        "protective_bonding_joint_bypass_count": bypass_count,
        "protective_bonding_installed_count": 0,
        "protective_bonding_measurement_count": 0,
        "protective_bonding_approved": False,
        "connection_authority": False,
        "powered_test_authority": False,
        "motion_authority": False,
        "energization_authority": False,
    })
    status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")

    readme = WHOLE / "README.md"
    text = readme.read_text(encoding="utf-8")
    start, end = "<!-- HR30-PROTECTIVE-BONDING-P01-README-START -->", "<!-- HR30-PROTECTIVE-BONDING-P01-README-END -->"
    if start in text and end in text:
        text = text.split(start, 1)[0] + text.split(end, 1)[1]
    block = f'''{start}\n## Physical protective-bonding implementation\n\nThe [interactive protective-bonding guide](electrical/protective-bonding-implementation-p0.1/index.html) binds the PE/reference architecture to **{hw_count} hardware records**, **{zone_count} whole-robot bond zones**, **{bypass_count} articulated-joint bypass obligations**, a 16-step installation traveler and a blank 12-test inspection plan. Hammond enclosure studs, Phoenix Contact UT 10-PE, Anderson 1340G1 and an Alpha Wire 6 AWG fixed-panel family are candidate interfaces only. Fault sizing, moving-joint cable, installation, measurements, AHJ disposition and qualified release remain open.\n{end}\n'''
    marker = "<!-- HR30-STM32-BRINGUP-P01-README-START -->"
    text = text.replace(marker, block + marker) if marker in text else text.rstrip() + "\n\n" + block
    readme.write_text(text, encoding="utf-8", newline="\n")

    root_page = WHOLE / "index.html"
    text = root_page.read_text(encoding="utf-8")
    start, end = "<!-- HR30-PROTECTIVE-BONDING-P01-START -->", "<!-- HR30-PROTECTIVE-BONDING-P01-END -->"
    if start in text and end in text:
        text = text.split(start, 1)[0] + text.split(end, 1)[1]
    section = f'''{start}<section id="protective-bonding"><h2>The grounding drawing now maps to physical candidate hardware</h2><div class="grid"><article class="card"><div class="metric">{hw_count}</div><p>hardware candidate/selection records</p></article><article class="card"><div class="metric">{zone_count}</div><p>whole-robot bond zones</p></article><article class="card"><div class="metric">{bypass_count}</div><p>joint-bypass obligations</p></article><article class="card hold"><div class="metric">0</div><p>installed or measured bonds</p></article></div><p><a href="electrical/protective-bonding-implementation-p0.1/index.html">Open the interactive protective-bonding implementation guide</a>. Exact sizing, installation, tests and authority remain open.</p></section>{end}'''
    marker = "<!-- HR30-STM32-BRINGUP-P01-START -->"
    text = text.replace(marker, section + marker) if marker in text else text.replace("</main>", section + "</main>", 1)
    root_page.write_text(text, encoding="utf-8", newline="\n")


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    sources, source_bindings = primary_sources(), bindings()
    site, hw, sizing = site_basis(), hardware(), sizing_inputs()
    zones, bypass = bond_zones(), bypasses()
    traveler, tests, open_rows = installation_steps(), inspections(), holds()
    write_csv(OUT / "primary-source-register.csv", sources)
    write_csv(OUT / "source-binding.csv", source_bindings)
    write_csv(OUT / "site-jurisdiction-basis.csv", site)
    write_csv(OUT / "bond-hardware-register.csv", hw)
    write_csv(OUT / "conductor-sizing-basis.csv", sizing)
    write_csv(OUT / "robot-bond-zone-register.csv", zones)
    write_csv(OUT / "joint-bypass-obligation.csv", bypass)
    write_csv(OUT / "installation-traveler.csv", traveler)
    write_csv(OUT / "inspection-measurement-plan.csv", tests)
    write_csv(OUT / "open-holds.csv", open_rows)
    status = {
        "identifier": IDENTIFIER,
        "warning": WARNING,
        "primary_source_count": len(sources),
        "source_binding_count": len(source_bindings),
        "site_basis_count": len(site),
        "hardware_record_count": len(hw),
        "sizing_input_count": len(sizing),
        "bond_zone_count": len(zones),
        "joint_bypass_count": len(bypass),
        "installation_step_count": len(traveler),
        "inspection_test_count": len(tests),
        "open_hold_count": len(open_rows),
        "candidate_panel_pe_terminal_selected": True,
        "candidate_tether_pe_contact_selected": True,
        "candidate_fixed_panel_conductor_family_selected": True,
        "moving_joint_jumper_selected": False,
        "conductor_sizing_released": False,
        "br1_hardware_selected": False,
        "installed_bond_count": 0,
        "executed_measurement_count": 0,
        "qualified_signoff_count": 0,
        "procurement_authority": False,
        "fabrication_authority": False,
        "connection_authority": False,
        "powered_test_authority": False,
        "motion_authority": False,
        "energization_authority": False,
    }
    (OUT / "physical-bond-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    (OUT / "protective-bonding-layout.svg").write_text(drawing(), encoding="utf-8", newline="\n")
    (OUT / "index.html").write_text(page(hw, zones, bypass, open_rows), encoding="utf-8", newline="\n")
    (OUT / "README.md").write_text(f"# HR-30 protective-bonding implementation P0.1\n\n**{WARNING}**\n\nThis package maps the whole-robot grounding topology to candidate physical hardware, installation obligations and blank inspection records. It records no installation, measurement, signoff or work authority. Use [index.html](index.html) for the interactive guide.\n", encoding="utf-8", newline="\n")
    shutil.copy2(Path(__file__), OUT / "protective-bonding-source.py")
    manifest = [common({"path": p.relative_to(OUT).as_posix(), "bytes": p.stat().st_size, "sha256": sha(p)}) for p in sorted(OUT.rglob("*")) if p.is_file() and p.name != "file-manifest.csv"]
    write_csv(OUT / "file-manifest.csv", manifest)
    if RELEASE.exists():
        shutil.rmtree(RELEASE)
    shutil.copytree(OUT, RELEASE)
    integrate_root(len(hw), len(zones), len(bypass))
    import generate_hr30_system_package_p01 as system_package
    system_package.refresh_manifest_and_release()
    print(json.dumps(status, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
