#!/usr/bin/env python3
"""Generate R244 nominal DCR/drop evidence and configuration P0.8."""
from __future__ import annotations

import csv
import hashlib
import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENG = ROOT / "electrical/routing/hr-v0-p121-dcr-drop-p0.1"
OUT = ROOT / "release/hr-v0/p121-dcr-drop-p0.1"
CFG_SOURCE = ROOT / "configuration/hr-v0-config-reconciliation-p0.7"
CFG_ENG = ROOT / "configuration/hr-v0-config-reconciliation-p0.8"
CFG_OUT = ROOT / "release/hr-v0/configuration-reconciliation-p0.8"
IDENT = "HR-V0-P121-DCR-DROP-P0.1"
CFG_IDENT = "HR-V0-CONFIG-REC-P0.8"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
DCR_OHM_PER_1000FT = 4.4
DCR_OHM_PER_M = DCR_OHM_PER_1000FT / 304.8


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        raise ValueError(f"refusing headerless CSV: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def put(path: Path, value: str) -> None:
    path.write_text(value, encoding="utf-8", newline="\n")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def warned(row: dict[str, str]) -> dict[str, str]:
    return {**row, "warning": WARNING}


def manifest(directory: Path) -> None:
    files = sorted(p for p in directory.iterdir() if p.is_file() and p.name != "file-manifest.csv")
    write(directory / "file-manifest.csv", [{"path": p.name, "bytes": str(p.stat().st_size), "sha256": digest(p)} for p in files])


def records() -> dict[str, list[dict[str, str]]]:
    sources = [
        warned({"source_id":"R244-SRC-001","manufacturer_or_owner":"Alpha Wire / Belden","artifact":"3057 current official product record","revision_or_date":"current official page accessed 2026-08-11","official_or_controlled_uri":"https://www.alphawire.com/products/wire/hook-up-wire/premium/3057","controlled_fact":"16 AWG 26/30 tinned-copper PVC wire; nominal conductor DC resistance 4.4 ohm/1000 ft at 20 C; electrical properties are for engineering purposes only","does_not_establish":"received-lot resistance, installed temperature, actual cut length, return-path drop, terminal/contact drop, source tolerance, maximum load, protection, thermal or application release"}),
        warned({"source_id":"R244-SRC-002","manufacturer_or_owner":"Belden","artifact":"3057 live product record","revision_or_date":"revision 0.120 dated 2026-06-30; accessed 2026-08-11","official_or_controlled_uri":"https://www.belden.com/products/cable/electronic-wire-cable/lead-wire-hook-up-wire/3057","controlled_fact":"3057 BL005 active blue 100 ft candidate; 16 AWG 26x30 tinned copper; nominal OD 2.3 mm","does_not_establish":"received-lot DCR, installed ampacity, cut length, voltage drop, temperature or application release"}),
        warned({"source_id":"R244-SRC-003","manufacturer_or_owner":"Pilz","artifact":"PNOZ s4 operating manual","revision_or_date":"21396-EN-23; imprint 2026-05; portal date 2026-06-22; accessed 2026-08-11","official_or_controlled_uri":"https://www.pilz.com/download/open/OM_PNOZ_s4_21396-EN-23.pdf","controlled_fact":"750104 uses screw terminals; 7 mm strip; 0.5 N m tightening torque; 24 V unit has 2.5 W DC consumption and 0.5 A for 5 ms inrush","does_not_establish":"terminal drive form, exact driver bit, access envelope, received voltage or achieved safety performance"}),
        warned({"source_id":"R244-SRC-004","manufacturer_or_owner":"Phoenix Contact","artifact":"PLC-RSC-24DC/21-21 item 2967060","revision_or_date":"product data maintained 2026-04-01; current PDF generated 2026-08-11","official_or_controlled_uri":"https://www.phoenixcontact.com/en-us/products/relay-module-plc-rsc-24dc21-21-2967060?type=pdf","controlled_fact":"24 VDC coil typical current 18 mA; M3 screw connection; 8 mm strip; 0.6 to 0.8 N m tightening torque","does_not_establish":"maximum coil current, terminal drive form, compatible bit, access depth or application release"}),
        warned({"source_id":"R244-SRC-005","manufacturer_or_owner":"Phoenix Contact","artifact":"TSD-M 1,2NM item 1212224","revision_or_date":"current PDF generated 2026-07-29; accessed 2026-08-11","official_or_controlled_uri":"https://www.phoenixcontact.com/en-us/products/torque-tool-tsd-m-12nm-1212224?type=pdf","controlled_fact":"0.3 to 1.2 N m range; plus or minus 6 percent; hexagonal fast-connection holder","does_not_establish":"calibration state, exact compatible bit, terminal access or witnessed torque"}),
        warned({"source_id":"R244-SRC-006","manufacturer_or_owner":"Phoenix Contact","artifact":"SF-BIT-SL 0,6X3,5-50 item 1212568","revision_or_date":"current PDF generated 2026-04-14; accessed 2026-08-11","official_or_controlled_uri":"https://www.phoenixcontact.com/en-us/products/screwdriver-tools-sf-bit-sl-06x35-50-1212568?type=pdf","controlled_fact":"slotted 0.6 x 3.5 x 50 mm bit; E6.3 / 1/4 inch shank; Phoenix identifies it as a torque-screwdriver bit in its official 2023-07-05 brochure","does_not_establish":"current explicit compatibility with item 2967060, required reach or access clearance"}),
        warned({"source_id":"R244-SRC-007","manufacturer_or_owner":"Phoenix Contact","artifact":"SF-BIT-SL 0,6X3,5-70 item 1212569","revision_or_date":"current PDF generated 2026-06-18; accessed 2026-08-11","official_or_controlled_uri":"https://www.phoenixcontact.com/en-gb/products/screwdriver-tools-sf-bit-sl-06x35-70-1212569?type=pdf","controlled_fact":"slotted 0.6 x 3.5 x 70 mm bit; E6.3 / 1/4 inch shank","does_not_establish":"current explicit compatibility with item 2967060, required reach or access clearance"}),
        warned({"source_id":"R244-SRC-008","manufacturer_or_owner":"Project Button","artifact":"R242/R243 controlled packages","revision_or_date":"HR-V0-P121-CONDUCTOR-FILL-P0.1 and HR-V0-P121-TERM-P0.1; 2026-08-11","official_or_controlled_uri":"release/hr-v0/p121-conductor-fill-p0.1/p121-conductor-schedule.csv","controlled_fact":"seven held conductor routes, nominal centerline lengths, published load inputs and fourteen held termination candidates","does_not_establish":"actual cuts, received DCR, installed termination/contact resistance, source tolerance, maximum relay current, feedback burden or physical result"}),
    ]
    conversions = [warned({
        "record_id":"DCR-CONV-001","published_value":"4.4 ohm/1000 ft at 20 C nominal","conversion":"4.4 / 304.8","nominal_ohm_per_m":f"{DCR_OHM_PER_M:.12f}",
        "classification":"MANUFACTURER-NOMINAL ENGINEERING INPUT ONLY","received_lot_measurement":"NOT EXECUTED","accepted_for_release":"NO"
    })]
    route_specs = [
        ("C-01","RT-P035",1.37025),("C-02","RT-P039",1.30025),("C-03","RT-P040",1.30025),
        ("C-04","RT-P042",1.27425),("C-05","RT-P043",1.27425),("C-06","RT-P015",0.08600),("C-07","RT-P005",0.11800),
    ]
    route_coefficients = [warned({
        "conductor_id":cid,"route_id":route,"planning_centerline_m":f"{length:.5f}",
        "nominal_dcr_ohm_per_m_at_20C":f"{DCR_OHM_PER_M:.12f}",
        "conditional_nominal_centerline_resistance_ohm":f"{length * DCR_OHM_PER_M:.9f}",
        "conditional_nominal_centerline_mV_per_A":f"{1000 * length * DCR_OHM_PER_M:.6f}",
        "classification":"COEFFICIENT ONLY - NOT AN INSTALLED RESISTANCE BOUND","release_result":"NOT ACCEPTED"
    }) for cid,route,length in route_specs]
    specs = [
        ("VDN-001","C-01","XD24:02 to SR1:A1",1.37025,2.5/24,0.5,"5 ms","Pilz published/derived inputs"),
        ("VDN-002","C-02","XD24:06 to KWD1:A1",1.30025,0.018,None,"","Phoenix typical coil current only; maximum unresolved"),
        ("VDN-003","C-03+C-06+C-07","XD24:07 through KWD1/KWD2 to SRA1:A1",1.50425,2.5/24,0.5,"5 ms","Pilz load through one-way series conductor and two ordinary contacts"),
        ("VDN-004","C-04","XD24:09 to KWD2:A1",1.27425,0.018,None,"","Phoenix typical coil current only; maximum unresolved"),
    ]
    screen = []
    for sid, conductors, path, length, typical, pulse, pulse_duration, basis in specs:
        resistance = length * DCR_OHM_PER_M
        screen.append(warned({
            "screen_id":sid,"conductors":conductors,"path":path,"planning_centerline_m":f"{length:.5f}",
            "nominal_dcr_ohm_per_m_at_20C":f"{DCR_OHM_PER_M:.12f}","nominal_conductor_resistance_ohm":f"{resistance:.9f}",
            "current_basis":basis,"typical_or_derived_current_A":f"{typical:.9f}","nominal_conductor_only_drop_V":f"{resistance * typical:.9f}",
            "pulse_current_A":"" if pulse is None else f"{pulse:.3f}","pulse_duration":"" if pulse is None else pulse_duration,
            "nominal_pulse_conductor_only_drop_V":"" if pulse is None else f"{resistance * pulse:.9f}",
            "classification":"ONE-WAY CENTERLINE / NOMINAL 20 C / CONDUCTOR-ONLY PLANNING SCREEN",
            "release_result":"NOT ACCEPTED - actual cut, received DCR, temperature, contact/return/source/load limits and acceptance criterion open"
        }))
    unresolved = [warned({
        "screen_id":"VDN-005","conductors":"C-05","path":"XD24:10 to KWD2:21 feedback","planning_centerline_m":"1.27425",
        "nominal_dcr_ohm_per_m_at_20C":f"{DCR_OHM_PER_M:.12f}","nominal_conductor_resistance_ohm":f"{1.27425 * DCR_OHM_PER_M:.9f}",
        "current_basis":"complete feedback burden SELECTION REQUIRED","typical_or_derived_current_A":"SELECTION REQUIRED","nominal_conductor_only_drop_V":"NOT CALCULATED",
        "pulse_current_A":"","pulse_duration":"","nominal_pulse_conductor_only_drop_V":"",
        "classification":"LOAD INPUT MISSING","release_result":"NOT CALCULATED / NOT ACCEPTED"
    })]
    bit_rows = [
        warned({"interface":"Pilz 750104 / SR1 and SRA1","published_terminal_data":"screw terminal; 0.5 N m; 7 mm strip","candidate_tool":"TSD-M 1,2NM 1212224 covers torque range","candidate_bit":"SELECTION REQUIRED","why_not_selected":"current Pilz manual and product page publish no drive form, blade dimensions, access envelope or approved bit","closure_evidence":"written Pilz geometry/tool confirmation plus unpowered received-terminal fit/access and calibrated witnessed torque","state":"OPEN"}),
        warned({"interface":"Phoenix 2967060 / KWD1 and KWD2","published_terminal_data":"M3 screw; 0.6 to 0.8 N m; 8 mm strip","candidate_tool":"TSD-M 1,2NM 1212224 covers torque range","candidate_bit":"1212568 0.6 x 3.5 x 50 mm strongest held candidate; 1212569 70 mm alternative","why_not_selected":"current 2967060 data does not state drive profile or pair either bit; required reach is unpublished","closure_evidence":"written Phoenix confirmation of 2967060 + 1212224 + exact bit/reach plus unpowered fit/access and calibrated witnessed torque","state":"SELECTION REQUIRED"}),
    ]
    inputs = [
        ("R244-H01","Received-lot Belden 3057 identity and calibrated four-wire DCR at recorded conductor temperature"),
        ("R244-H02","Actual seven-wire cut lengths including terminal entry, bend arcs, service allowance and routing tolerance"),
        ("R244-H03","Complete circuit return paths, source tolerance/droop and all terminal/contact resistances"),
        ("R244-H04","Maximum KWD coil current across voltage and temperature, not typical current alone"),
        ("R244-H05","Complete KWD2:21 feedback burden and worst-case state"),
        ("R244-H06","Qualified minimum-voltage and maximum-drop acceptance at every load during steady, inrush, reset and fault cases"),
        ("R244-H07","Ambient, conductor temperature coefficient, bundling, duty, enclosure heating and measured thermal validation"),
        ("R244-H08","F24/site fault-current and time-current coordination with conductor, terminal and connector limits"),
        ("R244-H09","Exact compatible Pilz 750104 bit and terminal access proof"),
        ("R244-H10","Exact compatible Phoenix 2967060 bit/reach and terminal access proof"),
        ("R244-H11","Installed continuity, voltage, temperature, torque, retention and photographic evidence"),
        ("R244-H12","Qualified electrical/functional-safety review, P1.21 acceptance and signed work authorization"),
    ]
    holds = [warned({"hold_id":hid,"hold":hold,"state":"OPEN","evidence":"SELECTION REQUIRED / NOT EXECUTED"}) for hid,hold in inputs]
    dispositions = [
        warned({"prior_hold":"R242-H03","disposition":"PARTIALLY ADDRESSED - OPEN","evidence_added":"current manufacturer nominal 4.4 ohm/1000 ft at 20 C and reproducible SI conversion","remaining":"received-lot calibrated four-wire DCR measurement at recorded temperature; actual cuts; thermal and qualified acceptance"}),
        warned({"prior_hold":"R243-H03","disposition":"OPEN - NO EXACT BIT CLAIM","evidence_added":"current Pilz documentation checked","remaining":"manufacturer geometry/tool confirmation and received fit/access proof"}),
        warned({"prior_hold":"R243-H04","disposition":"PARTIALLY ADDRESSED - OPEN","evidence_added":"exact 1212568/1212569 candidate geometry and TSD-M interface controlled","remaining":"current explicit 2967060 pairing, required reach and received fit/access proof"}),
    ]
    return {"source-register.csv":sources,"dcr-conversion.csv":conversions,"route-resistance-coefficients.csv":route_coefficients,"nominal-voltage-drop-screen.csv":screen + unresolved,"driver-bit-disposition.csv":bit_rows,"prior-hold-disposition.csv":dispositions,"open-holds.csv":holds}


def guide(data: dict[str, list[dict[str, str]]]) -> str:
    drop_rows = "".join(f"<tr><td>{html.escape(r['screen_id'])}</td><td>{html.escape(r['conductors'])}</td><td>{html.escape(r['planning_centerline_m'])}</td><td>{html.escape(r['nominal_conductor_resistance_ohm'])}</td><td>{html.escape(r['nominal_conductor_only_drop_V'])}</td><td>{html.escape(r['release_result'])}</td></tr>" for r in data["nominal-voltage-drop-screen.csv"])
    bit_rows = "".join(f"<tr><td>{html.escape(r['interface'])}</td><td>{html.escape(r['candidate_bit'])}</td><td>{html.escape(r['why_not_selected'])}</td><td>{html.escape(r['state'])}</td></tr>" for r in data["driver-bit-disposition.csv"])
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>R244 DCR and voltage-drop screen</title><style>:root{{--sky:#8bd7f7;--navy:#082b4c;--blue:#1268a8;--gold:#f3b61f;--paper:#f7fbfe}}*{{box-sizing:border-box}}body{{margin:0;color:var(--navy);background:var(--paper);font:clamp(16px,1.15vw,19px)/1.5 Arial,sans-serif}}header{{padding:clamp(1.5rem,5vw,4rem);background:linear-gradient(135deg,var(--sky),#effaff);border-bottom:7px solid var(--gold)}}h1{{font-size:clamp(2rem,5vw,4.2rem);line-height:1.05;max-width:21ch}}main{{max-width:1450px;margin:auto;padding:2rem clamp(1rem,4vw,3rem)}}.warning{{padding:1rem;border:3px solid #9b6d00;background:#fff3c4;border-radius:.8rem;font-weight:800}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:1rem;margin:1.5rem 0}}.card{{background:#fff;border:2px solid var(--blue);border-radius:.8rem;padding:1rem}}.note{{border-left:7px solid var(--gold);padding:1rem;background:#fff}}.table{{overflow:auto;margin:1rem 0}}table{{width:100%;border-collapse:collapse;min-width:1050px;background:#fff}}th,td{{padding:.85rem;text-align:left;vertical-align:top;border-bottom:1px solid #9bb}}th{{background:var(--navy);color:#fff}}code{{font-size:14px}}.tag{{display:inline-block;background:#fff0b3;border:2px solid #9b6d00;border-radius:999px;padding:.3rem .7rem;font-size:14px;font-weight:700}}</style></head><body><header><strong>{IDENT} · R244</strong><h1>A useful number, with its limits attached.</h1><div class="warning">{WARNING}</div></header><main><div class="grid"><article class="card"><b>4.4 Ω/1000 ft at 20 °C</b><br>Manufacturer-nominal engineering input</article><article class="card"><b>{DCR_OHM_PER_M:.12f} Ω/m</b><br>Traceable SI conversion</article><article class="card"><b>4 numeric path screens</b><br>One-way, centerline, conductor-only</article><article class="card"><b>12 open holds</b><br>No accepted circuit voltage budget</article></div><p class="note">These tiny calculated drops are not a circuit acceptance result. They omit the return conductor, actual cut length, received-lot resistance, temperature, source droop, terminal/contact resistance and several worst-case load inputs.</p><span class="tag">R242-H03 remains open</span><h2>Nominal planning screen</h2><div class="table"><table><thead><tr><th>ID</th><th>Conductor(s)</th><th>Centerline m</th><th>Nominal Ω</th><th>Nominal drop V</th><th>Disposition</th></tr></thead><tbody>{drop_rows}</tbody></table></div><h2>Driver-bit evidence</h2><div class="table"><table><thead><tr><th>Interface</th><th>Candidate</th><th>Why not selected</th><th>State</th></tr></thead><tbody>{bit_rows}</tbody></table></div><p>Pilz publishes no tightening-drive geometry. Phoenix item 1212568 is the strongest relay-terminal candidate, but current Phoenix data does not explicitly pair it with 2967060 or resolve 50 mm versus 70 mm reach. Both remain selection tasks, not purchasing instructions.</p><h2>What closes this</h2><p>Measure the received wire with calibrated four-wire equipment at a recorded temperature; release actual cuts and complete return/contact/source/load models; set qualified voltage limits; close F24 coordination and thermal evidence; confirm exact bits in writing; then execute and independently accept the physical tests.</p></main></body></html>'''


def config_data() -> dict[str, list[dict[str, str]]]:
    names = ("current-configuration-map.csv","supersession-map.csv","bom-integration-map.csv","gate-impact.csv","open-holds.csv","acceptance-matrix.csv")
    cfg = {name:read(CFG_SOURCE / name) for name in names}
    cfg["current-configuration-map.csv"].append(warned({"record_id":"CFG-27","role":"P1.21 nominal DCR/drop and driver-bit evidence","identifier":IDENT,"source_path":"release/hr-v0/p121-dcr-drop-p0.1/package-status.json","configuration_state":"CURRENT NOMINAL PLANNING SCREEN","release_boundary":"manufacturer-nominal DCR and conductor-only centerline arithmetic; received, actual-circuit, bit, physical and qualified acceptance open"}))
    cfg["supersession-map.csv"].append(warned({"record_id":"SUP-15","prior_identifier":"HR-V0-CONFIG-REC-P0.7","current_or_required_successor":CFG_IDENT,"disposition":"P0.7 remains immutable R243 snapshot; P0.8 adds R244 without changing the 98-group BOM, promoting P1.21 or closing work gates","use_authorized":"NO"}))
    for row in cfg["gate-impact.csv"]:
        row["evidence_added"] = IDENT
        row["remaining_evidence"] += "; R244 received DCR/cuts/complete-circuit limits, exact bits, physical and qualified acceptance"
        row["gate_closed"] = "NO"
    for n,value in enumerate((
        "Received-lot DCR, actual cuts and temperature-normalized conductor evidence",
        "Complete source/return/contact/load voltage budget and qualified acceptance limits",
        "Exact Pilz/Phoenix bits, physical fit, installed voltage/thermal evidence and signed acceptance",
    ),36):
        cfg["open-holds.csv"].append(warned({"hold_id":f"HOLD-{n:02d}","hold":value,"state":"NOT EXECUTED","closure_evidence":"signed source-backed physical and qualified record"}))
    for n,criterion in enumerate((
        "The 4.4 ohm/1000 ft at 20 C nominal source and SI conversion are independently reproduced",
        "All planning lengths and four numeric calculations match controlled R242 routes",
        "Every calculation is labeled one-way centerline conductor-only and not accepted",
        "Pilz and Phoenix exact driver bits remain selection required absent explicit current pairing",
        "Received DCR, cuts, return/contact/source/load/temperature/protection inputs are accepted",
        "P1.15 remains current and P1.21/R244 remain unaccepted until formal disposition",
    ),42):
        cfg["acceptance-matrix.csv"].append(warned({"acceptance_id":f"ACC-{n:02d}","criterion":criterion,"execution_state":"NOT EXECUTED","result":"OPEN","evidence_uri":"","approver":""}))
    return cfg


def main() -> None:
    data = records()
    for directory in (ENG, OUT):
        directory.mkdir(parents=True, exist_ok=True)
        for name, rows in data.items():
            write(directory / name, rows)
        put(directory / "README.md", f"# {IDENT}\n\n> **{WARNING}**\n\nR244 records a manufacturer-nominal 20 C DCR input, four one-way centerline conductor-only planning calculations and an explicit no-inference driver-bit disposition. Received and complete-circuit evidence remains open.\n")
        status = {"identifier":IDENT,"round":"R244","date":"2026-08-11","nominal_dcr_ohm_per_1000ft_at_20C":4.4,"nominal_dcr_ohm_per_m_at_20C":round(DCR_OHM_PER_M,12),"numeric_path_screens":4,"uncalculated_path_screens":1,"open_holds":12,"r242_h03_closed":False,"pilz_bit_selected":False,"phoenix_bit_selected":False,"received_dcr_exists":False,"actual_cut_lengths_released":False,"complete_circuit_voltage_budget_accepted":False,"physical_evidence_exists":False,"qualified_review_complete":False,"procurement_authorized":False,"fabrication_authorized":False,"assembly_authorized":False,"connection_authorized":False,"powered_testing_authorized":False,"motion_authorized":False,"energization_authorized":False,"safety_credit":False,"warning":WARNING}
        put(directory / "package-status.json", json.dumps(status, indent=2) + "\n")
    put(OUT / "index.html", guide(data))
    manifest(ENG); manifest(OUT)

    cfg = config_data()
    for directory in (CFG_ENG, CFG_OUT):
        directory.mkdir(parents=True, exist_ok=True)
        for name, rows in cfg.items():
            write(directory / name, rows)
        put(directory / "README.md", f"# {CFG_IDENT}\n\n> **{WARNING}**\n\nR244 adds {IDENT} without changing the 98-group BOM. P1.15 remains current; P1.21 is unaccepted; no work gate closes.\n")
        status = {"identifier":CFG_IDENT,"round":"R244","date":"2026-08-11","current_core_electrical_identifier":"Project Button Electrical V3-P1.15-CARRIER-CANDIDATE","unaccepted_panel_topology_candidate":"V3-P1.21-SRA1-SUPPLY-WATCHDOG-CANDIDATE","system_bom_groups":98,"current_records":27,"supersession_records":15,"bom_integration_records":18,"gate_records":11,"open_holds":38,"acceptance_rows":47,"all_acceptance_executed":False,"physical_article_exists":False,"physical_test_executed":False,"qualified_review_complete":False,"procurement_authorized":False,"fabrication_authorized":False,"assembly_authorized":False,"connection_authorized":False,"powered_testing_authorized":False,"motion_authorized":False,"energization_authorized":False,"safety_credit":False,"warning":WARNING}
        put(directory / "package-status.json", json.dumps(status, indent=2) + "\n")
    cfg_sources = [warned({"source_path":row["source_path"],"sha256":digest(ROOT / row["source_path"]),"role":"current configuration evidence"}) for row in cfg["current-configuration-map.csv"]]
    for directory in (CFG_ENG, CFG_OUT):
        write(directory / "source-hash-register.csv", cfg_sources)
        manifest(directory)
    put(CFG_OUT / "index.html", f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{CFG_IDENT}</title><style>body{{margin:0;background:#f7fbfe;color:#082b4c;font:clamp(16px,1.2vw,19px)/1.5 Arial,sans-serif}}main{{max-width:1100px;margin:auto;padding:32px 20px}}h1{{font-size:clamp(32px,5vw,58px)}}.warning{{padding:16px;background:#fff3c4;border:3px solid #9b6d00;font-weight:800}}.card{{padding:18px;margin:18px 0;background:#fff;border:2px solid #1268a8;border-radius:12px}}</style></head><body><main><div class="warning">{WARNING}</div><h1>{CFG_IDENT}</h1><div class="card"><b>98 covered BOM groups</b><p>R244 adds calculation and tool-disposition evidence only. It adds no new robot BOM item and releases no purchase.</p></div><div class="card"><b>P1.15 remains current</b><p>P1.21 and R244 remain unaccepted. No fabrication, wiring, powered test, motion or energization is authorized.</p></div></main></body></html>''')
    manifest(CFG_OUT)
    print(f"{IDENT}: 4 nominal path drops + 1 unresolved; 12 holds; both bit selections open")
    print(f"{CFG_IDENT}: 98 BOM groups; P1.15 current; P1.21 unaccepted")


if __name__ == "__main__":
    main()
