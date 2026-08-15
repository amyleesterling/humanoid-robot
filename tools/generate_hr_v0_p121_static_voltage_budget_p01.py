#!/usr/bin/env python3
"""Generate the R246 P1.21 static control-rail voltage-budget evidence package."""
from __future__ import annotations

import csv
import hashlib
import html
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IDENT = "HR-V0-P121-STATIC-VOLTAGE-BUDGET-P0.1"
CFG_IDENT = "HR-V0-CONFIG-REC-P0.10"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
ENG = ROOT / "electrical/analysis/hr-v0-p121-static-voltage-budget-p0.1"
REL = ROOT / "release/hr-v0/p121-static-voltage-budget-p0.1"
CFG_OLD = ROOT / "configuration/hr-v0-config-reconciliation-p0.9"
CFG = ROOT / "configuration/hr-v0-config-reconciliation-p0.10"
CFG_REL = ROOT / "release/hr-v0/configuration-reconciliation-p0.10"


def write_csv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fields})


def read_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader), list(reader.fieldnames or [])


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def manifest(directory: Path) -> None:
    rows = []
    for path in sorted(p for p in directory.iterdir() if p.is_file() and p.name != "file-manifest.csv"):
        rows.append({"path": path.name, "bytes": path.stat().st_size, "sha256": digest(path)})
    write_csv(directory / "file-manifest.csv", ["path", "bytes", "sha256"], rows)


def table(title: str, path: Path) -> str:
    rows, fields = read_csv(path)
    heads = "".join(f"<th>{html.escape(field.replace('_', ' '))}</th>" for field in fields)
    body = "".join("<tr>" + "".join(f"<td>{html.escape(str(row[field]))}</td>" for field in fields) + "</tr>" for row in rows)
    return f"<section><h2>{html.escape(title)}</h2><div class='table'><table><thead><tr>{heads}</tr></thead><tbody>{body}</tbody></table></div></section>"


def page(title: str, intro: str, sections: list[tuple[str, Path]], metrics: list[tuple[str, str]]) -> str:
    cards = "".join(f"<article><b>{html.escape(value)}</b><span>{html.escape(label)}</span></article>" for label, value in metrics)
    content = "".join(table(name, path) for name, path in sections)
    return f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>{html.escape(title)}</title><style>
:root{{--ink:#082a4a;--blue:#075ea8;--sky:#dff3ff;--gold:#f3bd28;--paper:#f8fbfd;--line:#9bc6e4;--danger:#8d1721}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:clamp(16px,1.2vw,18px)/1.55 system-ui,sans-serif}}header,main{{max-width:1500px;margin:auto;padding:clamp(18px,3vw,42px)}}header{{background:linear-gradient(135deg,var(--ink),var(--blue));color:white;max-width:none}}header>div{{max-width:1500px;margin:auto}}.warning{{font-size:clamp(16px,1.3vw,20px);font-weight:800;color:#fff2bd;border:3px solid var(--gold);padding:14px;border-radius:12px}}h1{{font-size:clamp(32px,5vw,62px);line-height:1.05;margin:.5em 0 .2em}}h2{{font-size:clamp(24px,2.6vw,36px);margin-top:1.7em}}.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:14px;margin:26px 0}}article{{background:white;border:2px solid var(--line);border-radius:14px;padding:18px}}article b{{display:block;font-size:clamp(24px,3vw,40px);color:var(--blue)}}article span{{font-size:16px}}.table{{overflow:auto;background:white;border:2px solid var(--line);border-radius:12px}}table{{border-collapse:collapse;width:100%;min-width:1000px}}th,td{{padding:12px 14px;text-align:left;vertical-align:top;border-bottom:1px solid #cce1ef;font-size:14px;line-height:1.45}}th{{position:sticky;top:0;background:var(--sky);color:var(--ink);font-size:14px}}code{{font-size:14px}}a{{color:var(--blue)}}.status{{font-weight:800;color:var(--danger)}}@media(max-width:600px){{header,main{{padding:18px}}h1{{font-size:34px}}}}
</style></head><body><header><div><p class='warning'>{html.escape(WARNING)}</p><h1>{html.escape(title)}</h1><p>{html.escape(intro)}</p></div></header><main><div class='cards'>{cards}</div><p class='status'>PARTIAL / NOT ACCEPTED. Raw source headroom is not an installed load-terminal voltage guarantee.</p>{content}</main></body></html>"""


def base_rows() -> dict[str, tuple[list[str], list[dict[str, object]]]]:
    source_fields = ["source_id","manufacturer","document","revision_date","official_url","verified_fact","excluded_inference","status","warning"]
    sources = [
        {"source_id":"SRC-001","manufacturer":"GlobTek","document":"WR9QI1660YL4NKITR6B specification","revision_date":"Rev B; generated/current record rechecked 2026-08-11","official_url":"https://spec.globtek.info/spec/?id=01t0c000008jfZg","verified_fact":"24 V, 1.66 A, 40 W; output regulation +/-5% at output connector; ripple 1% or 100 mV; turn-on/off overshoot 5%","excluded_inference":"Ripple/overshoot inclusion in regulation and dynamic undershoot/foldback are not established","status":"CURRENT PRIMARY INPUT"},
        {"source_id":"SRC-002","manufacturer":"Pilz","document":"PNOZ s4 operating manual 21396-EN-23","revision_date":"Imprint 2026-05; portal 2026-06-22","official_url":"https://www.pilz.com/en-US/eshop/Relay-modules/Safety-relays-protection-relays/PNOZsigma-safety-relays/PNOZ-s4-24VDC-3-n-o-1-n-c/p/750104","verified_fact":"24 VDC -15%/+10% (20.4-26.4 V); 2.5 W; A1 pulse 0.5 A for 5 ms; Y32 max 20 mA with up to 5 V internal drop","excluded_inference":"No project loop drop or installed terminal voltage is approved","status":"CURRENT PRIMARY INPUT"},
        {"source_id":"SRC-003","manufacturer":"Phoenix Contact","document":"PLC-RSC-24DC/21 item 2967060 product data","revision_date":"Last data management 2026-04-01; rechecked 2026-08-11","official_url":"https://www.phoenixcontact.com/en-us/products/relay-module-plc-rsc-24dc-21-2967060","verified_fact":"20.2-33.6 V at 20 C; 18 mA typical; 0.43 W maximum power dissipation; contact minimum 5 V/10 mA","excluded_inference":"No maximum module current or guaranteed closed-contact voltage drop was found","status":"CURRENT PRIMARY INPUT"},
        {"source_id":"SRC-004","manufacturer":"Texas Instruments","document":"TPL7407L datasheet SLRS066D","revision_date":"Revised 2016-03; rechecked 2026-08-11","official_url":"https://www.ti.com/lit/ds/symlink/tpl7407l.pdf","verified_fact":"Maximum VOL 0.320 V at 100 mA and 0.650 V at 200 mA under published conditions","excluded_inference":"No interpolation is accepted at an unbounded relay-module current","status":"CURRENT PRIMARY INPUT"},
        {"source_id":"SRC-005","manufacturer":"Schneider Electric","document":"LC1D25BD product data sheet SQD-LC1D25BD","revision_date":"2017-09-13; rechecked 2026-08-11","official_url":"https://iportal.se.com/Contents/docs/SQD-LC1D25BD.PDF","verified_fact":"24 VDC coil; operational limit 0.7-1.25 Uc through 60 C (16.8-30.0 V); 5.4 W at 20 C","excluded_inference":"5.4 W is not a maximum-current bound and does not prove project DC interruption duty","status":"CURRENT PRIMARY INPUT"},
        {"source_id":"SRC-006","manufacturer":"TRACO POWER","document":"TSR 1 datasheet","revision_date":"2024-02-07; rechecked 2026-08-11","official_url":"https://www.tracopower.com/tsr1-datasheet","verified_fact":"TSR 1-2450 input 6.5-36 VDC; 94% typical efficiency","excluded_inference":"Typical efficiency is not a guaranteed watchdog-board input-current bound","status":"CURRENT PRIMARY INPUT"},
        {"source_id":"SRC-007","manufacturer":"Kycon","document":"KPJX-PM-4S drawing","revision_date":"Rev C2 2026-01-08; rechecked 2026-08-11","official_url":"https://www.kycon.com/Pub_Eng_Draw/KPJX-PM-4S.pdf","verified_fact":"7.5 A per pin; 30 milliohm maximum contact resistance","excluded_inference":"Conditional 99.6 mV pair drop at 1.66 A is not assigned until received mating identity and current path are verified","status":"CURRENT PRIMARY INPUT"},
        {"source_id":"SRC-008","manufacturer":"MEAN WELL","document":"GST280A series specification","revision_date":"2026-04-03; rechecked 2026-08-11","official_url":"https://www.meanwell.com/Upload/PDF/GST280A/GST280A-SPEC.PDF","verified_fact":"GST280A12-C6P is the separate 12 V actuator-source candidate","excluded_inference":"It is excluded from every 24 V control-rail budget calculation","status":"EXCLUDED SOURCE BOUNDARY"},
    ]
    for row in sources: row["warning"] = WARNING

    loop_fields = ["loop_id","load","forward_terminal_net_path","return_terminal_net_path","source","calculation_state","warning"]
    loops = [
        ("LOOP-001","SR1 PNOZ s4 A1/A2","PSU2:YL4-1 > J24:1 > SAFETY_24V_RAW > F24:IN/OUT > SAFETY_24V > XD24:LINE > XD24:02 > C-01 / RT-P035 / P2P-035 > SR1:A1","SR1:A2 > P2P-049 > XD0:01 > XD0:LINE > P2P-048 > J24:3 > PSU2:YL4-3","GlobTek 24 V only","PARTIAL"),
        ("LOOP-002","SRA1 PNOZ s4 A1/A2","common source > XD24:07 > C-03 / RT-P040 / P2P-040 > KWD1:11-14 NO > C-06 / RT-P015 / P2P-015 > KWD2:11-14 NO > C-07 / RT-P005 / P2P-005 > SRA1:A1","SRA1:A2 > P2P-051 > XD0:03 > common return","GlobTek 24 V only","PARTIAL"),
        ("LOOP-003","KWD1 PLC-RSC-24DC/21 coil/module","common source > XD24:06 > C-02 / RT-P039 / P2P-039 > KWD1:A1","KWD1:A2 > WD1_COIL_N > P2P-029 / JWP1:3 > PCB > UDRV1:16 > low-side sink > UDRV1:8 > PCB > JWP1:2 > P2P-055 > XD0:07 > common return","GlobTek 24 V only","PARTIAL"),
        ("LOOP-004","KWD2 PLC-RSC-24DC/21 coil/module","common source > XD24:09 > C-04 / RT-P042 / P2P-042 > KWD2:A1","KWD2:A2 > WD2_COIL_N > P2P-030 / JWP1:4 > PCB > UDRV2 low-side sink > JWP1:2 > P2P-055 > XD0:07 > common return","GlobTek 24 V only","PARTIAL"),
        ("LOOP-005","K1 LC1D25BD coil","XD24:03 > SRA1:13-14 > FSR1:1-2 > K1:A1","K1:A2 > XD0:04 > common return","GlobTek 24 V only","TOPOLOGY ONLY"),
        ("LOOP-006","K2 LC1D25BD coil","XD24:04 > SRA1:23-24 > FSR2:1-2 > K2:A1","K2:A2 > XD0:05 > common return","GlobTek 24 V only","TOPOLOGY ONLY"),
        ("LOOP-007","WDPCB1 / TSR 1-2450 input","XD24:14 > JWP1:1 > DC1:1","DC1:2 > JWP1:2 > P2P-055 > XD0:07 > common return","GlobTek 24 V only","TOPOLOGY ONLY"),
        ("LOOP-008","H1 indicator","SR1:Y32 > XN3:1/2 > H1:TBD-HA/HB","H1 return > XD0:02 > common return","Pilz Y32 output from GlobTek-powered SR1","TOPOLOGY ONLY"),
    ]
    loop_rows = [dict(zip(loop_fields[:-1], row), warning=WARNING) for row in loops]

    env_fields = ["load_id","device","published_min_V","published_max_V","source_low_V","source_high_V","raw_low_headroom_V","raw_high_headroom_V","boundary","status","warning"]
    env_data = [
        ("ENV-001","SR1/SRA1 PNOZ s4",20.4,26.4,22.8,25.2,2.4,1.2,"Before every project series loss and transient","PARTIAL"),
        ("ENV-002","KWD1/KWD2 PLC-RSC-24DC/21",20.2,33.6,22.8,25.2,2.6,8.4,"20 C published range only; max current and contact path unbounded","PARTIAL"),
        ("ENV-003","K1/K2 LC1D25BD coil",16.8,30.0,22.8,25.2,6.0,4.8,"Published through 60 C; actual current and loop loss unbounded","PARTIAL"),
        ("ENV-004","WDPCB1 TSR 1-2450 input",6.5,36.0,22.8,25.2,16.3,10.8,"Converter input only; board current/startup/brownout unbounded","PARTIAL"),
    ]
    env_rows = [dict(zip(env_fields[:-1], row), warning=WARNING) for row in env_data]

    series_fields = ["element_id","applies_to","terminal_or_path","published_or_prior_value","usable_bound","missing_evidence","disposition","warning"]
    series_data = [
        ("SER-001","all loops","GlobTek regulation point at output connector","22.8-25.2 V","YES - source connector only","Installed dynamic behavior","INCLUDED"),
        ("SER-002","all loops","factory YL4/C40337 cord","Regulation stated at output connector","NO ADDITIONAL DROP ASSIGNED","Received identity and definition of regulation point","DO NOT DOUBLE COUNT"),
        ("SER-003","all loops","J24 mating contacts","Kycon candidate max 30 milliohm/contact","NO","Received plug equality, pin path, temperature and mating condition","SELECTION REQUIRED"),
        ("SER-004","all loops","J24:1 to F24:IN","No controlled P2P record","NO","Conductor, length, terminations and DCR","SELECTION REQUIRED"),
        ("SER-005","all loops","F24 link and holder","No value/order code released","NO","Cold/hot resistance, time-current, interrupting and coordination","SELECTION REQUIRED"),
        ("SER-006","all loops","P2P-033 F24:OUT to XD24:LINE","No released length/conductor","NO","Installed route and resistance","SELECTION REQUIRED"),
        ("SER-007","all loops","XD24 distribution","No maximum path resistance","NO","Received terminal/jumper identity and path measurement","SELECTION REQUIRED"),
        ("SER-008","SR1","C-01 forward conductor","0.019780512 ohm nominal centerline at 20 C","NO - planning only","Actual cut, return, temperature, terminations and received DCR","PARTIAL"),
        ("SER-009","SRA1","C-03+C-06+C-07 forward conductors","0.021714895 ohm nominal centerline at 20 C","NO - planning only","Actual cuts, KWD contacts, return, temperature and terminations","PARTIAL"),
        ("SER-010","KWD1","C-02 forward conductor","0.018770013 ohm nominal centerline at 20 C","NO - planning only","Actual cut, return and full module current bound","PARTIAL"),
        ("SER-011","KWD2","C-04 forward conductor","0.018394685 ohm nominal centerline at 20 C","NO - planning only","Actual cut, return and full module current bound","PARTIAL"),
        ("SER-012","SRA1","KWD1/KWD2 11-14 contacts","No maximum closed-contact drop found","NO","Manufacturer/application response and received measurement","SELECTION REQUIRED"),
        ("SER-013","K1/K2","FSR1/FSR2 links and holders","No value/order code released","NO","Resistance, coordination, thermal and time-current","SELECTION REQUIRED"),
        ("SER-014","KWD1/KWD2","JWP1 contacts and PCB copper/vias","No accepted bound","NO","Connector, fabrication stack, copper path and temperature","SELECTION REQUIRED"),
        ("SER-015","KWD1/KWD2","TPL7407L low-side sink","0.320 V max at 100 mA; 0.650 V max at 200 mA","NO AT ACTUAL CURRENT","Guaranteed current/temperature operating point","SELECTION REQUIRED"),
        ("SER-016","all loops","XD0 return distribution","No maximum path resistance","NO","Received terminal/jumper identity and path measurement","SELECTION REQUIRED"),
        ("SER-017","all loops","P2P-048 J24:3 to XD0:LINE","No released length/conductor","NO","Installed route and resistance","SELECTION REQUIRED"),
        ("SER-018","SR1/SRA1/KWD","P2P-049/051/029/030/055 returns","No released resistance bounds","NO","Conductor, length, terminations and installed DCR","SELECTION REQUIRED"),
    ]
    series_rows = [dict(zip(series_fields[:-1], row), warning=WARNING) for row in series_data]

    screen_fields = ["screen_id","load","source_low_V","published_load_min_V","raw_headroom_V","known_nominal_forward_drop_V","residual_after_known_nominal_forward_drop_V","accepted_installed_margin_V","result","warning"]
    screens = [
        ("SCR-001","SR1",22.8,20.4,2.4,0.002060,2.397940,"NOT CALCULABLE","PARTIAL - missing return/contact/protection/thermal/transient terms"),
        ("SCR-002","SRA1",22.8,20.4,2.4,0.002262,2.397738,"NOT CALCULABLE","PARTIAL - KWD contact and all common/return terms unbounded"),
        ("SCR-003","KWD1",22.8,20.2,2.6,0.000338,2.599662,"NOT CALCULABLE","PARTIAL - 20 C only; driver/current/return/common terms unbounded"),
        ("SCR-004","KWD2",22.8,20.2,2.6,0.000331,2.599669,"NOT CALCULABLE","PARTIAL - 20 C only; driver/current/return/common terms unbounded"),
        ("SCR-005","K1/K2",22.8,16.8,6.0,"NOT CALCULATED","NOT CALCULABLE","NOT CALCULABLE","PARTIAL - fuse/contact/coil-current/route terms unbounded"),
        ("SCR-006","WDPCB1",22.8,6.5,16.3,"NOT CALCULATED","NOT CALCULABLE","NOT CALCULABLE","PARTIAL - board current/startup/brownout/route terms unbounded"),
    ]
    screen_rows = [dict(zip(screen_fields[:-1], row), warning=WARNING) for row in screens]

    transient_fields = ["case_id","condition","required_input","current_evidence","result","closure_evidence","warning"]
    transient_data = [
        ("TRN-001","all loads steady simultaneous","Guaranteed maximum load current by state","Typical/derived planning values only","NOT CALCULABLE","Manufacturer maxima plus measured state table"),
        ("TRN-002","SR1/SRA1 pickup","0.5 A / 5 ms plus simultaneous loads and source response","Pilz pulse published; source response absent","NOT CALCULABLE","Oscilloscope traces at source and A1/A2"),
        ("TRN-003","K1/K2 simultaneous pickup","Maximum coil pickup current and source sag","5.4 W at 20 C only","NOT CALCULABLE","Received coil current and voltage traces"),
        ("TRN-004","watchdog converter startup","Input current waveform and UVLO/recovery","6.5-36 V input only","NOT CALCULABLE","Board-level startup and slow-ramp tests"),
        ("TRN-005","brownout/recovery","Source foldback, recovery and logic state","No dynamic source curve","NOT CALCULABLE","Fault-injection trace with no unintended restart"),
        ("TRN-006","ripple/tolerance composition","Whether ripple is included in +/-5% regulation","Not stated in controlled source record","NOT CALCULABLE","GlobTek written answer or conservative accepted bound"),
        ("TRN-007","turn-on/off overshoot","Upper rail exposure and load state","5% source overshoot only","NOT CALCULABLE","Definition plus installed trace at worst line/load"),
        ("TRN-008","fuse clearing/fault","Fault current, I2t, voltage dip and recovery","F24/FSR values unselected","NOT CALCULABLE","Selected protection coordination and fault test"),
    ]
    transient_rows = [dict(zip(transient_fields[:-1], row), warning=WARNING) for row in transient_data]

    missing_fields = ["missing_id","input","affected_loops","classification","evidence_to_close","state","warning"]
    missing_data = [
        ("MIS-001","F24/FSR1/FSR2 exact links and holders including hot resistance","ALL/K1/K2","PROTECTION","Selected order codes and primary data plus coordination","SELECTION REQUIRED"),
        ("MIS-002","J24 received mating identity, continuity and contact resistance","ALL","INTERFACE","Receiving record and four-wire measurement","SELECTION REQUIRED"),
        ("MIS-003","Common forward and return conductor identities/lengths","ALL","HARNESS","Released P2P routes and as-built cuts","SELECTION REQUIRED"),
        ("MIS-004","XD24/XD0 path resistance and jumper topology","ALL","DISTRIBUTION","Received identity and measured worst path","SELECTION REQUIRED"),
        ("MIS-005","Actual conductor DCR versus temperature and installation","ALL","THERMAL","Four-wire measurements and accepted correction","NOT EXECUTED"),
        ("MIS-006","Phoenix maximum current and minimum operate voltage outside 20 C","KWD1/KWD2","MANUFACTURER","Written manufacturer application response","SELECTION REQUIRED"),
        ("MIS-007","Phoenix 11-14 maximum closed-contact drop/resistance/endurance","SRA1","MANUFACTURER","Written response and received test","SELECTION REQUIRED"),
        ("MIS-008","JWP1 plus PCB copper/via resistance and thermal rise","KWD1/KWD2/WDPCB1","PCB","Accepted stackup and physical measurement","SELECTION REQUIRED"),
        ("MIS-009","TPL7407L guaranteed VOL at actual current/temperature","KWD1/KWD2","DRIVER","Bound max module current and applicable datasheet point or test","SELECTION REQUIRED"),
        ("MIS-010","Maximum simultaneous rail current by machine state","ALL","LOAD BUDGET","State-aware maximum-current table","SELECTION REQUIRED"),
        ("MIS-011","GlobTek dynamic undershoot/foldback/recovery","ALL","SOURCE DYNAMIC","Written response and installed traces","SELECTION REQUIRED"),
        ("MIS-012","GlobTek ripple/tolerance/overshoot composition","ALL","SOURCE STATIC/DYNAMIC","Written response or conservative accepted rule","SELECTION REQUIRED"),
        ("MIS-013","H1 exact current, polarity and operating range","H1","LOAD","Exact order code and primary data","SELECTION REQUIRED"),
        ("MIS-014","Measurement uncertainty, aging and design margin policy","ALL","ACCEPTANCE","Qualified accepted calculation/test rule","SELECTION REQUIRED"),
        ("MIS-015","Installed ambient, enclosure temperature and bundling","ALL","ENVIRONMENT","Frozen site/install conditions and thermal test","SELECTION REQUIRED"),
        ("MIS-016","Received hardware voltage traces at every load","ALL","PHYSICAL","Configuration-bound test record","NOT EXECUTED"),
        ("MIS-017","No-unintended-restart brownout and recovery evidence","ALL","FUNCTIONAL","Fault-injection record","NOT EXECUTED"),
        ("MIS-018","Qualified electrical and functional-safety disposition","ALL","AUTHORITY","Signed review against frozen configuration","NOT EXECUTED"),
    ]
    missing_rows = [dict(zip(missing_fields[:-1], row), warning=WARNING) for row in missing_data]

    question_fields = ["question_id","recipient","question","required_response","state","warning"]
    question_data = [
        ("Q-001","GlobTek","Does +/-5% output regulation include ripple and line/load/temperature variation?","Written exact-model answer","UNSENT"),
        ("Q-002","GlobTek","What minimum dynamic output and recovery apply during 0.5 A/5 ms and simultaneous pickup?","Waveform/test conditions or guaranteed bound","UNSENT"),
        ("Q-003","GlobTek","What foldback, hiccup and restart behavior applies to the exact model?","Protection thresholds and recovery behavior","UNSENT"),
        ("Q-004","GlobTek","Is regulation specified at the YL4 mating connector and does it include factory-cord drop?","Definition of measurement point","UNSENT"),
        ("Q-005","Phoenix Contact","What maximum input current and minimum operate voltage apply across rated temperature for 2967060?","Guaranteed limits","UNSENT"),
        ("Q-006","Phoenix Contact","What maximum closed voltage drop/resistance applies to 11-14 at the Pilz A1 pulse and steady currents?","Guaranteed application limit","UNSENT"),
        ("Q-007","Phoenix Contact","Is 2967060 suitable for repeated switching of the proposed PNOZ s4 A1 input waveform?","Written application disposition","UNSENT"),
        ("Q-008","Pilz","Confirm acceptable PNOZ s4 behavior for the measured source sag/ripple/brownout envelope once available.","Written application disposition","UNSENT"),
        ("Q-009","Schneider Electric","Provide maximum LC1D25BD coil pickup/hold current versus temperature and minimum voltage at coil terminals.","Guaranteed coil envelope","UNSENT"),
        ("Q-010","TRACO POWER","Provide worst-case TSR 1-2450 input/startup current for the frozen watchdog-board load.","Guaranteed or application-specific envelope","UNSENT"),
    ]
    question_rows = [dict(zip(question_fields[:-1], row), warning=WARNING) for row in question_data]

    hold_fields = ["hold_id","hold","affected_gate","state","closure_evidence","warning"]
    hold_data = [
        ("R246-H01","Complete installed forward and return resistance budget","EG-004/015/020","OPEN","Selected parts, released routes and received measurements"),
        ("R246-H02","State-aware guaranteed maximum control-load current","EG-004/020","OPEN","Manufacturer maxima and frozen simultaneous-state table"),
        ("R246-H03","Source dynamic sag/foldback/recovery and ripple composition","EG-004/020","OPEN","Written GlobTek evidence and installed traces"),
        ("R246-H04","KWD module current and 11-14 contact drop/endurance","EG-004/012","OPEN","Phoenix written response and physical test"),
        ("R246-H05","Driver/PCB/JWP1 return-path bound","EG-004/020","OPEN","Accepted stackup, connector and worst-case VOL evidence"),
        ("R246-H06","F24/FSR1/FSR2 selection and coordination","EG-003/004/010","OPEN","Exact order codes and protection study"),
        ("R246-H07","Temperature, bundling, aging and measurement uncertainty","EG-015/020","OPEN","Qualified accepted derating and measurement plan"),
        ("R246-H08","Received no-load and simultaneous-pickup traces","EG-018/020","OPEN","Configuration-bound physical records"),
        ("R246-H09","Brownout/recovery no-unintended-start fault injection","EG-012/022","OPEN","Configuration-bound fault record"),
        ("R246-H10","Qualified electrical and functional-safety review","EG-022","OPEN","Signed disposition against frozen configuration"),
    ]
    hold_rows = [dict(zip(hold_fields[:-1], row), warning=WARNING) for row in hold_data]

    acceptance_fields = ["acceptance_id","criterion","execution_state","result","evidence_uri","approver","warning"]
    acceptance_data = [
        ("R246-ACC-01","All loop terminal/net paths match P1.21 schedules","NOT EXECUTED","OPEN","",""),
        ("R246-ACC-02","Every series element has a conservative accepted maximum drop","NOT EXECUTED","OPEN","",""),
        ("R246-ACC-03","Every load remains within published limits in every allowed state","NOT EXECUTED","OPEN","",""),
        ("R246-ACC-04","Simultaneous pickup and brownout/recovery pass without unintended restart","NOT EXECUTED","OPEN","",""),
        ("R246-ACC-05","Protection coordination and conductor thermal limits are accepted","NOT EXECUTED","OPEN","",""),
        ("R246-ACC-06","Received voltage traces and uncertainty satisfy frozen limits","NOT EXECUTED","OPEN","",""),
        ("R246-ACC-07","Independent and qualified reviewers sign the frozen package","NOT EXECUTED","OPEN","",""),
    ]
    acceptance_rows = [dict(zip(acceptance_fields[:-1], row), warning=WARNING) for row in acceptance_data]

    return {
        "source-register.csv": (source_fields, sources),
        "loop-topology-register.csv": (loop_fields, loop_rows),
        "manufacturer-operating-envelope.csv": (env_fields, env_rows),
        "series-element-register.csv": (series_fields, series_rows),
        "static-headroom-screen.csv": (screen_fields, screen_rows),
        "transient-case-register.csv": (transient_fields, transient_rows),
        "missing-input-register.csv": (missing_fields, missing_rows),
        "manufacturer-question-addendum.csv": (question_fields, question_rows),
        "open-holds.csv": (hold_fields, hold_rows),
        "acceptance-matrix.csv": (acceptance_fields, acceptance_rows),
    }


def generate_voltage_package() -> None:
    for directory in (ENG, REL):
        if directory.exists(): shutil.rmtree(directory)
        directory.mkdir(parents=True)
    datasets = base_rows()
    for name, (fields, rows) in datasets.items():
        write_csv(ENG / name, fields, rows)
    status = {
        "identifier": IDENT, "round": "R246", "date": "2026-08-11", "status": "PARTIAL / NOT ACCEPTED",
        "source_boundary": "GlobTek WR9QI1660YL4NKITR6B is the 24 V control source; Mean Well GST280A12-C6P is a separate 12 V actuator source and is excluded",
        "loop_records": 8, "manufacturer_sources": 8, "series_elements": 18, "static_screens": 6,
        "transient_cases": 8, "missing_inputs": 18, "manufacturer_questions": 10, "open_holds": 10,
        "accepted_installed_voltage_budget": False, "p115_current": True, "p121_accepted": False,
        "physical_evidence_exists": False, "qualified_review_complete": False, "procurement_authorized": False,
        "fabrication_authorized": False, "assembly_authorized": False, "connection_authorized": False,
        "powered_testing_authorized": False, "motion_authorized": False, "energization_authorized": False,
        "safety_credit": False, "warning": WARNING,
    }
    (ENG / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n")
    readme = f"""# {IDENT}\n\n> **{WARNING}**\n\nThis R246 package traces eight P1.21 24 V control loops, verifies the source/load operating envelopes from current primary documents and calculates raw source-connector headroom. It deliberately does not turn nominal conductor screens into installed bounds.\n\nThe result is **PARTIAL / NOT ACCEPTED**. Every project series loss, simultaneous-pickup condition, source transient, temperature effect and received measurement must close before an installed minimum voltage can be accepted. `GST280A12-C6P` is a separate 12 V actuator source and is excluded. P1.15 remains current; P1.21 remains unaccepted.\n"""
    (ENG / "README.md").write_text(readme, encoding="utf-8", newline="\n")
    for path in ENG.iterdir():
        if path.is_file(): shutil.copy2(path, REL / path.name)
    sections = [(name.replace(".csv", "").replace("-", " ").title(), REL / name) for name in datasets]
    (REL / "index.html").write_text(page("P1.21 static 24 V control-rail budget", "Eight exact loop traces, primary-source envelopes, raw headroom screens and every missing closure input.", sections, [("loops","8"),("static screens","6"),("missing inputs","18"),("open holds","10")]), encoding="utf-8", newline="\n")
    manifest(ENG); manifest(REL)


def generate_configuration() -> None:
    for directory in (CFG, CFG_REL):
        if directory.exists(): shutil.rmtree(directory)
        shutil.copytree(CFG_OLD, directory)
    current, fields = read_csv(CFG / "current-configuration-map.csv")
    current.append({"record_id":"CFG-30","role":"P1.21 static 24 V control-rail budget","identifier":IDENT,"source_path":"release/hr-v0/p121-static-voltage-budget-p0.1/package-status.json","configuration_state":"CURRENT SUPPORTING EVIDENCE - PARTIAL / NOT ACCEPTED","release_boundary":"Raw headroom only; complete installed static/dynamic circuit budget and physical evidence remain open","warning":WARNING})
    write_csv(CFG / "current-configuration-map.csv", fields, current)
    supersession, fields = read_csv(CFG / "supersession-map.csv")
    supersession.append({"record_id":"SUP-17","prior_identifier":"HR-V0-CONFIG-REC-P0.9","current_or_required_successor":CFG_IDENT,"disposition":"SUPERSEDED BY R246 CONFIGURATION RECORD ONLY","use_authorized":"NO","warning":WARNING})
    write_csv(CFG / "supersession-map.csv", fields, supersession)
    holds, fields = read_csv(CFG / "open-holds.csv")
    holds.extend([
        {"hold_id":"HOLD-39","hold":"Complete installed P1.21 control-loop static resistance and voltage-drop bound","state":"SELECTION REQUIRED","closure_evidence":"Selected series parts, released routes, temperature/aging/uncertainty policy and received four-wire measurements","warning":WARNING},
        {"hold_id":"HOLD-40","hold":"P1.21 simultaneous pickup, brownout, foldback and recovery behavior","state":"NOT EXECUTED","closure_evidence":"Source/manufacturer limits plus configuration-bound installed traces and fault injection","warning":WARNING},
        {"hold_id":"HOLD-41","hold":"Qualified review of complete P1.21 supply/watchdog application","state":"NOT EXECUTED","closure_evidence":"Signed electrical and functional-safety disposition against frozen source, wiring and evidence","warning":WARNING},
    ])
    write_csv(CFG / "open-holds.csv", fields, holds)
    acceptance, fields = read_csv(CFG / "acceptance-matrix.csv")
    for number, criterion in enumerate([
        "R246 exact terminal/net loop trace independently reproduced",
        "R246 every series-element maximum drop accepted",
        "R246 state-aware maximum current and steady voltage budget accepted",
        "R246 transient pickup/brownout/recovery tests passed",
        "R246 received voltage evidence and uncertainty accepted",
        "R246 qualified electrical and functional-safety review signed",
    ], start=52):
        acceptance.append({"acceptance_id":f"ACC-{number:02d}","criterion":criterion,"execution_state":"NOT EXECUTED","result":"OPEN","evidence_uri":"","approver":"","warning":WARNING})
    write_csv(CFG / "acceptance-matrix.csv", fields, acceptance)
    impacts, fields = read_csv(CFG / "gate-impact.csv")
    for row in impacts:
        if row["gate_id"] in {"EG-002","EG-004","EG-010","EG-014","EG-015","EG-018","EG-020","EG-022"}:
            row["evidence_added"] += f"; {IDENT} exact loop/source/headroom/missing-input register"
            row["remaining_evidence"] += "; accepted installed static/dynamic voltage budget and physical/qualified evidence"
            row["gate_closed"] = "NO"
    write_csv(CFG / "gate-impact.csv", fields, impacts)
    status = json.loads((CFG / "package-status.json").read_text(encoding="utf-8"))
    status.update({"identifier":CFG_IDENT,"round":"R246","current_records":30,"supersession_records":17,"open_holds":41,"acceptance_rows":57,"p121_static_voltage_budget":IDENT})
    (CFG / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n")
    (CFG / "README.md").write_text(f"# {CFG_IDENT}\n\n> **{WARNING}**\n\nR246 carries P0.9 forward and adds the partial/not-accepted P1.21 static voltage-budget evidence. P1.15 remains current; P1.21 remains unaccepted. Forty-one holds and fifty-seven unexecuted acceptance rows remain.\n", encoding="utf-8", newline="\n")
    source_rows = []
    for row in current:
        source = ROOT / row["source_path"]
        if not source.is_file(): raise SystemExit(f"missing configuration source: {source}")
        source_rows.append({"source_path":row["source_path"],"sha256":digest(source),"role":row["role"],"warning":WARNING})
    write_csv(CFG / "source-hash-register.csv", ["source_path","sha256","role","warning"], source_rows)
    manifest(CFG)
    for path in CFG.iterdir():
        if path.is_file(): shutil.copy2(path, CFG_REL / path.name)
    sections = [(name.replace(".csv", "").replace("-", " ").title(), CFG_REL / name) for name in ("current-configuration-map.csv","supersession-map.csv","gate-impact.csv","open-holds.csv","acceptance-matrix.csv")]
    (CFG_REL / "index.html").write_text(page("HR-V0 configuration reconciliation P0.10", "Current identifiers, supersession, gate effects, open holds and acceptance requirements after R246.", sections, [("current records","30"),("BOM groups","98"),("open holds","41"),("acceptance rows","57")]), encoding="utf-8", newline="\n")
    manifest(CFG_REL)


def main() -> None:
    generate_voltage_package()
    generate_configuration()
    print(f"Generated {IDENT} and {CFG_IDENT}: partial/not accepted; P1.15 current; P1.21 unaccepted")


if __name__ == "__main__": main()
