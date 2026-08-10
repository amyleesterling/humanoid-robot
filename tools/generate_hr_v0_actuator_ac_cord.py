"""Generate the held HR-V0 actuator-source AC-cord selection package."""

from __future__ import annotations

import csv
import html
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "electrical" / "ac-input" / "hr-v0-actuator-ac-cord-p0.1"
WEB = ROOT / "release" / "hr-v0" / "actuator-ac-cord-p0.1"
RECEIVING = ROOT / "tests" / "forms" / "hr-v0-actuator-ac-cord-receiving-template-p0.1.csv"
SITE = ROOT / "tests" / "forms" / "hr-v0-actuator-ac-cord-site-fit-template-p0.1.csv"
IDENTIFIER = "HR-V0-ACT-AC-CORD-P0.1"
DATE = "2026-08-09"
WARNING = "PRELIMINARY - NOT APPROVED FOR FABRICATION, CONNECTION, MOTION, OR ENERGIZATION"

SOURCES = [
    {
        "source_id": "ACCORD-SRC-001",
        "manufacturer": "MEAN WELL",
        "product": "GST280A series / GST280A12-C6P",
        "document": "GST280A-SPEC",
        "revision_or_date": "2026-04-03",
        "url": "https://www.meanwell.com/Upload/PDF/GST280A/GST280A-SPEC.PDF",
        "controlled_facts": "IEC320-C14 AC inlet; Class I; 85-264 VAC; 3 A typical at 115 VAC; 95 A cold-start inrush at 115 VAC; -V connected to AC FG; final-equipment compliance recheck required",
        "boundary": "Typical input and catalog inrush are not site branch, cord heating, PE continuity, EMC or application proof",
    },
    {
        "source_id": "ACCORD-SRC-002",
        "manufacturer": "Eaton Tripp Lite series",
        "product": "P006-006",
        "document": "Official product record",
        "revision_or_date": "accessed 2026-08-09",
        "url": "https://www.eaton.com/us/en-us/skuPage.P006-006.html",
        "controlled_facts": "NEMA 5-15P to IEC-320-C13; 10 A; 125 VAC; 18 AWG; three conductors; 6 ft / 1.83 m; 7.8 mm OD; SJT black PVC; VW-1; UL Listed; cUL Listed; -20 to 60 C",
        "boundary": "Catalog identity does not prove received construction, local code applicability, site receptacle, route, retention, temperature or source compatibility",
    },
]

CONTROLS = [
    ("ACC-001", "build/use location", "Boston, Massachusetts, USA", "User-frozen location only; exact premises and branch remain open"),
    ("ACC-002", "actuator source", "MEAN WELL GST280A12-C6P evaluation candidate", "Source itself remains unreceived and application-held"),
    ("ACC-003", "source AC inlet", "IEC320-C14", "Received inlet identity and fit required"),
    ("ACC-004", "source protection class", "Class I with earth pin", "No PE continuity or site bond credit until measured"),
    ("ACC-005", "cord candidate", "Eaton Tripp Lite series P006-006", "Exact catalog candidate on hold; no purchase authority"),
    ("ACC-006", "premises plug", "NEMA 5-15P", "Requires accepted matching site receptacle and branch"),
    ("ACC-007", "equipment connector", "IEC-320-C13", "Requires received C13-to-C14 fit and retention"),
    ("ACC-008", "catalog voltage", "125 VAC", "Use only on a reviewed compatible branch"),
    ("ACC-009", "catalog current", "10 A maximum", "Not a project branch or protection rating"),
    ("ACC-010", "construction", "18 AWG; three conductors; SJT; black PVC; VW-1", "Received markings and construction required"),
    ("ACC-011", "length", "6 ft / 1.83 m", "Final outlet/source placement and trip-free route required"),
    ("ACC-012", "catalog outer diameter", "7.8 mm", "Received diameter and bend/strain evidence required"),
    ("ACC-013", "catalog certification", "UL Listed; cUL Listed", "Received label and local applicability review required"),
    ("ACC-014", "catalog operating temperature", "-20 to 60 C", "Installed temperature remains unmeasured"),
    ("ACC-015", "nominal-current screen", "3 A GST typical / 10 A cord maximum = 0.300", "Typical-value screen only; not an ampacity or protection release"),
    ("ACC-016", "cold-start inrush", "95 A at 115 VAC from GST catalog", "Branch, contacts, connector behavior and nuisance-trip evidence remain open"),
    ("ACC-017", "source PE/DC relationship", "GST -V connected to AC FG", "System PE/DC0V/shield implementation remains under EG-016"),
    ("ACC-018", "final-equipment obligation", "MEAN WELL requires final equipment compliance reconfirmation", "Qualified electrical/code/EMC review remains mandatory"),
]

HOLDS = [
    ("ACCORD-HOLD-001", "Exact premises, outlet, nominal voltage/frequency, branch rating and protection surveyed"),
    ("ACCORD-HOLD-002", "Applicable Boston/MA/US code and makerspace policy reviewed by a qualified person"),
    ("ACCORD-HOLD-003", "Program owner separately authorizes exact purchase line and maximum spend"),
    ("ACCORD-HOLD-004", "Received P006-006 identity, UL/cUL markings, construction and condition accepted"),
    ("ACCORD-HOLD-005", "Received GST280A12-C6P C14 inlet identity and C13 engagement accepted"),
    ("ACCORD-HOLD-006", "Unpowered conductor mapping, PE continuity and conductor isolation measured without inferred pinout"),
    ("ACCORD-HOLD-007", "Six-foot route is trip-free, protected, strain-relieved and serviceable"),
    ("ACCORD-HOLD-008", "Received bend radius, retention and source-inlet mechanical support accepted"),
    ("ACCORD-HOLD-009", "GST 95 A catalog inrush reconciled to the exact branch, receptacle and connection hardware"),
    ("ACCORD-HOLD-010", "Cord/source temperature and abnormal-condition plan accepted before powered use"),
    ("ACCORD-HOLD-011", "No substitution or extension cord accepted without separate configuration review"),
    ("ACCORD-HOLD-012", "Qualified electrical reviewer signs the installed AC-input/PE configuration"),
]

RECEIVING_STEPS = [
    ("ACR-001", "Purchase authority", "Signed exact-line purchase decision and candidate commit exist"),
    ("ACR-002", "Quarantine", "Cord remains segregated and unconnected"),
    ("ACR-003", "Package identity", "Manufacturer, P006-006 and package label photographed"),
    ("ACR-004", "Certification markings", "Received UL/cUL and cord markings photographed; ambiguity quarantined"),
    ("ACR-005", "Connector identity", "Received NEMA 5-15P and C13 identities independently confirmed without connection"),
    ("ACR-006", "Conductor/jacket markings", "18 AWG, three-conductor, SJT/VW-1 markings recorded where present"),
    ("ACR-007", "Length", "Received length measured and uncertainty recorded"),
    ("ACR-008", "Outer diameter", "Received OD measured and uncertainty recorded"),
    ("ACR-009", "Condition", "No unaccepted cuts, crushing, exposed conductor, bent pins or molding damage"),
    ("ACR-010", "Unpowered mapping method", "Qualified method identifies conductor continuity without assuming terminal positions"),
    ("ACR-011", "Protective-earth continuity", "Measured result and acceptance limit recorded by qualified reviewer"),
    ("ACR-012", "Conductor isolation", "L/N/PE isolation result recorded unpowered"),
    ("ACR-013", "C13 retention", "Fit/retention test deferred until exact received source and authorized unpowered procedure"),
    ("ACR-014", "Evidence integrity", "Photographs and raw records carry SHA-256 identities"),
    ("ACR-015", "Independent check", "Second named person reconciles identity and results"),
    ("ACR-016", "Disposition", "QUARANTINE, REJECT or ACCEPTED FOR NAMED UNPOWERED FIT ONLY"),
]

SITE_STEPS = [
    ("ACS-001", "Premises", "Exact Boston premises and responsible site authority recorded"),
    ("ACS-002", "Receptacle", "Receptacle type, condition and grounding configuration verified by qualified person"),
    ("ACS-003", "Branch", "Nominal voltage/frequency, breaker, shared loads and available fault information recorded"),
    ("ACS-004", "Policy/code", "Makerspace policy, NEC/MA amendments and inspection obligations disposition recorded"),
    ("ACS-005", "Source placement", "GST location stable, ventilated, dry and protected from impact/spill"),
    ("ACS-006", "Route length", "Six-foot cord reaches without extension, tension or unsupported inlet load"),
    ("ACS-007", "Trip/abrasion", "Route avoids walking paths, sharp edges, pinch and moving robot zones"),
    ("ACS-008", "Service access", "Plug can be removed without entering robot hazard space"),
    ("ACS-009", "C13/C14 fit", "Authorized unpowered fit and retention result recorded on received articles"),
    ("ACS-010", "PE path", "Installed protective-earth continuity test method and acceptance limit approved"),
    ("ACS-011", "Inrush", "95 A catalog cold-start inrush reviewed against branch/receptacle/contact behavior"),
    ("ACS-012", "Thermal", "Powered temperature channels and abort limits defined but not executed"),
    ("ACS-013", "Label/retention", "Cord source and disconnect relationship labeled without obstructing removal"),
    ("ACS-014", "Qualified disposition", "Electrical reviewer accepts or rejects the complete installed AC-input configuration"),
]


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    if WEB.exists():
        shutil.rmtree(WEB)
    OUT.mkdir(parents=True)
    WEB.mkdir(parents=True)

    write_csv(OUT / "source-register.csv", SOURCES)
    write_csv(OUT / "interface-control.csv", [{
        "control_id": control_id,
        "parameter": parameter,
        "candidate_value": value,
        "release_boundary": boundary,
        "state": "CATALOG CANDIDATE - APPLICATION HOLD",
        "warning": WARNING,
    } for control_id, parameter, value, boundary in CONTROLS])
    write_csv(OUT / "selection-holds.csv", [{
        "hold_id": hold_id,
        "closure_evidence": evidence,
        "owner_role": "SELECTION REQUIRED",
        "named_owner": "SELECTION REQUIRED",
        "state": "OPEN",
        "evidence_uri": "NOT EXECUTED",
        "warning": WARNING,
    } for hold_id, evidence in HOLDS])

    def form_rows(records: list[tuple[str, str, str]]) -> list[dict[str, str]]:
        return [{
            "record_id": record_id,
            "inspection_or_test": name,
            "acceptance_boundary": acceptance,
            "configuration_commit": "NOT EXECUTED",
            "article_or_site_identity": "NOT EXECUTED",
            "instrument_and_calibration": "NOT EXECUTED",
            "result": "NOT EXECUTED",
            "evidence_uri": "NOT EXECUTED",
            "operator": "SELECTION REQUIRED",
            "independent_reviewer": "SELECTION REQUIRED",
            "authorization": "NOT AUTHORIZED",
            "disposition": "NOT EXECUTED",
            "warning": WARNING,
        } for record_id, name, acceptance in records]

    write_csv(RECEIVING, form_rows(RECEIVING_STEPS))
    write_csv(SITE, form_rows(SITE_STEPS))
    status = {
        "identifier": IDENTIFIER,
        "date": DATE,
        "build_location_basis": "Boston, Massachusetts, USA",
        "source_candidate": "MEAN WELL GST280A12-C6P",
        "cord_candidate": "Eaton Tripp Lite series P006-006",
        "interface_control_count": len(CONTROLS),
        "open_hold_count": len(HOLDS),
        "receiving_record_count": len(RECEIVING_STEPS),
        "site_fit_record_count": len(SITE_STEPS),
        "catalog_candidate_identified": True,
        "application_selected": False,
        "purchase_authorized": False,
        "received_evidence_present": False,
        "site_evidence_present": False,
        "connection_authorized": False,
        "motion_authorized": False,
        "energization_authorized": False,
        "warning": WARNING,
    }
    (OUT / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n")

    controls_html = ''.join(f'<tr><td>{control_id}</td><td>{html.escape(parameter)}</td><td>{html.escape(value)}</td><td>{html.escape(boundary)}</td></tr>' for control_id, parameter, value, boundary in CONTROLS)
    holds_html = ''.join(f'<li><strong>{hold_id}</strong> — {html.escape(evidence)}</li>' for hold_id, evidence in HOLDS)
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-V0 actuator AC cord candidate</title><style>:root{{--sky:#7bd0f5;--navy:#082f58;--blue:#11649f;--gold:#f3b61f;--paper:#f4faff;--hold:#fff1b5}}*{{box-sizing:border-box}}body{{margin:0;color:var(--navy);font:clamp(16px,1.15vw,19px)/1.5 Arial,sans-serif}}header{{padding:clamp(1.5rem,5vw,4rem);background:linear-gradient(135deg,var(--sky),#eefaff);border-bottom:7px solid var(--gold)}}h1{{font-size:clamp(2.2rem,5.5vw,4.8rem);line-height:1.04;max-width:18ch;margin:.25rem 0 1rem}}h2{{font-size:clamp(1.5rem,3vw,2.6rem)}}main{{max-width:1380px;margin:auto;padding:2rem clamp(1rem,4vw,3.5rem)}}.warning{{background:var(--hold);border:3px solid #b67d00;border-radius:.8rem;padding:1rem;font-weight:800}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,230px),1fr));gap:1rem;margin:2rem 0}}.card{{border:3px solid var(--blue);border-radius:1rem;padding:1.1rem;background:var(--paper)}}.metric{{font-size:clamp(2rem,4vw,3.4rem);font-weight:800}}.table-wrap{{overflow:auto;border:2px solid #93b8ce;border-radius:.7rem}}table{{border-collapse:collapse;width:100%;min-width:1000px}}th,td{{padding:.8rem;text-align:left;vertical-align:top;border-bottom:1px solid #bdd0dc}}th{{background:var(--navy);color:white}}.boundary{{border-left:7px solid var(--gold);padding-left:1rem;margin:2rem 0}}li{{margin:.7rem 0}}a{{color:#075d98}}</style></head><body><header><div>{IDENTIFIER} · R147 · {DATE}</div><h1>One exact AC cord candidate. Twelve reasons it stays on hold.</h1><div class="warning">{WARNING}. P006-006 is not approved for purchase, connection, or use until the received and site-specific holds close.</div></header><main><p>The candidate matches the catalog connector/rating envelope: GST280A12-C6P uses a Class-I C14 inlet; Eaton P006-006 provides a NEMA 5-15P to C13, 10 A/125 V, three-conductor 18 AWG connection for a North-American site. That is selection evidence, not installed-system proof.</p><section class="grid"><article class="card"><div class="metric">3 A</div>GST typical input at 115 VAC</article><article class="card"><div class="metric">10 A</div>P006-006 catalog maximum</article><article class="card"><div class="metric">95 A</div>GST catalog cold-start inrush at 115 VAC</article><article class="card"><div class="metric">0</div>executed physical records</article></section><div class="boundary"><h2>Why the 0.300 screen is not approval</h2><p>Three amperes divided by ten amperes is 0.300, but the source value is typical and the cord rating does not select branch protection or prove contact/inrush, temperature, PE, code, route or abnormal behavior. Those decisions require the exact site and received articles.</p></div><h2>Controlled interface</h2><div class="table-wrap"><table><thead><tr><th>ID</th><th>Parameter</th><th>Candidate</th><th>Release boundary</th></tr></thead><tbody>{controls_html}</tbody></table></div><h2>Twelve open holds</h2><ol>{holds_html}</ol><div class="boundary"><h2>Next admissible work</h2><p>Independent catalog review may proceed now. Purchase requires a separate signed decision. After receipt, perform only the unpowered receiving and site-fit procedures. Do not connect the cord or source until the complete AC-input/PE configuration is accepted by a qualified electrical reviewer under the staged energization process.</p></div><p><a href="../../../electrical/ac-input/hr-v0-actuator-ac-cord-p0.1/interface-control.csv">Interface register</a> · <a href="../../../electrical/ac-input/hr-v0-actuator-ac-cord-p0.1/selection-holds.csv">Hold register</a> · <a href="../../../tests/forms/hr-v0-actuator-ac-cord-receiving-template-p0.1.csv">Receiving form</a> · <a href="../../../tests/forms/hr-v0-actuator-ac-cord-site-fit-template-p0.1.csv">Site-fit form</a></p></main></body></html>'''
    (WEB / "index.html").write_text(page, encoding="utf-8", newline="\n")
    print(f"{IDENTIFIER}: {len(CONTROLS)} controls / {len(HOLDS)} open holds / {len(RECEIVING_STEPS) + len(SITE_STEPS)} unexecuted records")
    print("P006-006 catalog candidate only; application, purchase, connection and energization remain false")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
