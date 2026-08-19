#!/usr/bin/env python3
"""Generate the HR-30 first-energization measurement harness package P0.1.

This package closes the paper design of the NI-side analog and sync cables.
Robot-side diagnostic terminals, fabrication, calibration, test limits and every
work authority remain open.
"""

from __future__ import annotations

import csv
import hashlib
import html
import json
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WHOLE = ROOT / "hr30" / "whole-body-p0.1"
OUT = WHOLE / "first-energization-measurement-harness-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / OUT.name
PANEL = WHOLE / "electrical" / "measurement-boundary-panel-p0.1"
INSTRUMENTS = WHOLE / "first-energization-instrumentation-p0.1"
TETHER = WHOLE / "electrical" / "tether-power-core-p0.1"
WHOLE_ECAD = WHOLE / "electrical" / "kicad" / "hr30-whole-body-electrical-p0.1"
IDENTIFIER = "HR30-FIRST-ENERGIZATION-MEASUREMENT-HARNESS-P0.1"
DATE = "2026-08-19"
WARNING = (
    "PRELIMINARY - UNBUILT MEASUREMENT HARNESS - ZERO SAFETY CREDIT - "
    "NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, "
    "POWERED TESTING, MOTION, WALKING OR ENERGIZATION"
)
AUTHORITY = "NONE"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise RuntimeError(f"refusing empty register: {path}")
    fields: list[str] = []
    for row in rows:
        for field in row:
            if field not in fields:
                fields.append(field)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


CHANNELS = [
    {
        "channel_id": "CH-AI-01", "panel": "J1O", "module": "INS-02", "ni_channel": "AI0",
        "signal": "ACT_MAIN_SOURCE_12V", "hi_net": "RAW_12V_POS", "lo_net": "RAW_0V",
        "source_sheet": "01_external_source_panel.kicad_sch", "hi_terminal": "PS1:+V", "lo_terminal": "PS1:-V",
        "physical_state": "LOGICAL NODE SELECTED; SOURCE-PROXIMAL DIAGNOSTIC TERMINAL/SHORT PROTECTION NOT PRESENT",
    },
    {
        "channel_id": "CH-AI-02", "panel": "J2O", "module": "INS-02", "ni_channel": "AI1",
        "signal": "ACT_MAIN_SAFE_12V", "hi_net": "TETHER_POS_SWITCHED", "lo_net": "RAW_0V",
        "source_sheet": "04_touch_safe_tether.kicad_sch", "hi_terminal": "XT1A:P1", "lo_terminal": "XT1A:P2",
        "physical_state": "LOGICAL/CONNECTOR NODE SELECTED; GUARDED DIAGNOSTIC PICKOFF AND NO-BYPASS REVIEW OPEN",
    },
    {
        "channel_id": "CH-AI-03", "panel": "J3O", "module": "INS-02", "ni_channel": "AI2",
        "signal": "TTL_LDIST_SAFE_9V", "hi_net": "TTL_LDIST_SAFE_9V", "lo_net": "ACT_0V_CONTROLLED",
        "source_sheet": "01_energy_precharge_conversion.kicad_sch", "hi_terminal": "REG_TTL_L:LOG-OUT", "lo_terminal": "REG_TTL_L:LOG-RET-OUT",
        "physical_state": "LOGICAL NODE SELECTED; REGULATOR OUTPUT TEST CONNECTOR NOT PRESENT",
    },
    {
        "channel_id": "CH-AI-04", "panel": "J4O", "module": "INS-02", "ni_channel": "AI3",
        "signal": "CTRL_5V", "hi_net": "CTRL_5V", "lo_net": "CTRL_GND",
        "source_sheet": "04_motion_controller_carrier_connectors.kicad_sch", "hi_terminal": "REG1:LOG-5V", "lo_terminal": "REG1:LOG-GND",
        "physical_state": "LOGICAL NODE SELECTED; REGULATOR OUTPUT TEST CONNECTOR NOT PRESENT",
    },
    {
        "channel_id": "CH-AI-05", "panel": "J5O", "module": "INS-03", "ni_channel": "AI0",
        "signal": "ESTOP_CH_A_24V", "hi_net": "S12_CH1", "lo_net": "SAFE_0V",
        "source_sheet": "02_estop_reset_safety_relay.kicad_sch", "hi_terminal": "SR1:S12", "lo_terminal": "SR1:A2",
        "physical_state": "LOGICAL/DEVICE TERMINALS SELECTED; LOADING/FAULT/NO-BYPASS REVIEW AND PROTECTED PICKOFF OPEN",
    },
    {
        "channel_id": "CH-AI-06", "panel": "J6O", "module": "INS-03", "ni_channel": "AI1",
        "signal": "HARDWIRED_PERMIT_24V", "hi_net": "HARDWIRED_PERMIT", "lo_net": "SAFE_0V",
        "source_sheet": "02_estop_reset_safety_relay.kicad_sch", "hi_terminal": "SR1:34", "lo_terminal": "SR1:A2",
        "physical_state": "LOGICAL/DEVICE TERMINALS SELECTED; LOADING/FAULT/NO-BYPASS REVIEW AND PROTECTED PICKOFF OPEN",
    },
    {
        "channel_id": "CH-AI-07", "panel": "J7O", "module": "INS-03", "ni_channel": "AI2",
        "signal": "K1_COIL_24V", "hi_net": "K1_COIL_POS", "lo_net": "SAFE_0V",
        "source_sheet": "03_redundant_dc_interruption.kicad_sch", "hi_terminal": "K1:A1", "lo_terminal": "K1:A2",
        "physical_state": "LOGICAL/DEVICE TERMINALS SELECTED; GUARDED PROTECTED PICKOFF HARDWARE OPEN",
    },
    {
        "channel_id": "CH-AI-08", "panel": "J8O", "module": "INS-03", "ni_channel": "AI3",
        "signal": "K2_COIL_24V", "hi_net": "K2_COIL_POS", "lo_net": "SAFE_0V",
        "source_sheet": "03_redundant_dc_interruption.kicad_sch", "hi_terminal": "K2:A1", "lo_terminal": "K2:A2",
        "physical_state": "LOGICAL/DEVICE TERMINALS SELECTED; GUARDED PROTECTED PICKOFF HARDWARE OPEN",
    },
]


def channel_rows() -> list[dict]:
    rows = []
    for ch in CHANNELS:
        rows.append({
            **ch,
            "panel_hi_contact": f"{ch['panel']}.1",
            "panel_lo_contact": f"{ch['panel']}.2",
            "ni_hi_terminal": f"{ch['module']}/{ch['ni_channel']}+",
            "ni_lo_terminal": f"{ch['module']}/{ch['ni_channel']}-",
            "shared_signal_reference": "NONE",
            "ni_side_design_state": "EXACT CONTACT/WIRE/STRAIN-RELIEF CANDIDATE DEFINED",
            "robot_side_connection_released": "NO",
            "warning": WARNING,
        })
    return rows


def analog_contact_rows() -> list[dict]:
    rows: list[dict] = []
    for ch in CHANNELS:
        cable = f"MH-{ch['channel_id'].removeprefix('CH-')}"
        for polarity, color, panel_contact, ni_terminal in [
            ("HI/+", "WHITE", f"{ch['panel']}.1", f"{ch['module']}/{ch['ni_channel']}+"),
            ("LO/-", "BLACK", f"{ch['panel']}.2", f"{ch['module']}/{ch['ni_channel']}-"),
        ]:
            rows.append({
                "cable_id": cable, "channel_id": ch["channel_id"], "polarity": polarity,
                "conductor_color": color, "panel_endpoint": panel_contact,
                "panel_mating_plug": "Phoenix Contact 1757019",
                "panel_termination": "Phoenix Contact 3203066 AI 0,34-8 TQ ferrule candidate",
                "daq_endpoint": ni_terminal, "daq_plug": "NI-9976 196739-01 2-position screw plug",
                "daq_termination": "Phoenix Contact 3203053 AI 0,34-6 TQ ferrule candidate",
                "conductor": "Alpha Wire 5610B2201, 22 AWG stranded copper, 105 C",
                "finished_length_mm": 1000, "cut_length_mm": 1120,
                "strip_panel_mm": "FOLLOW FERRULE/CONNECTOR QUALIFIED PROCESS; 8 mm ferrule candidate",
                "strip_daq_mm": 6, "daq_terminal_torque_nm": "0.22-0.25",
                "daq_screw_flange_torque_nm": "0.20", "backshell": "NI-9971 196375-01",
                "shield_disposition": "DRAIN CUT BACK/INSULATED AT BOTH ENDS; NO SIGNAL/RETURN/CHASSIS BOND; EMC/NOISE VALIDATION OPEN",
                "assembly_state": "NOT BUILT", "connection_authority": AUTHORITY, "warning": WARNING,
            })
    return rows


def sync_rows() -> list[dict]:
    return [
        {"contact_id":"SYNC-01","from":"JTTL.1","signal":"SLATE_OUT","wire_color":"WHITE","to":"NI-9924 terminal 14","ni9401_function":"DIO0","state":"EXACT CANDIDATE MAP","warning":WARNING},
        {"contact_id":"SYNC-02","from":"JTTL.2","signal":"SLATE_BAT_RET","wire_color":"BLACK","to":"NI-9924 terminal 1","ni9401_function":"COM","state":"EXACT CANDIDATE MAP","warning":WARNING},
        {"contact_id":"SYNC-03","from":"Alpha 5610B2201 drain","signal":"CABLE SHIELD","wire_color":"BARE/TINNED","to":"NI-9924 SH","ni9401_function":"SHIELD ONLY; NOT COM","state":"EXACT CANDIDATE MAP; PANEL END INSULATED","warning":WARNING},
        {"contact_id":"SYNC-04","from":"NO CONDUCTOR","signal":"NC","wire_color":"NONE","to":"NI-9924 terminal 15","ni9401_function":"NC","state":"MUST REMAIN EMPTY","warning":WARNING},
    ]


def cable_rows() -> list[dict]:
    rows = []
    for ch in CHANNELS:
        rows.append({
            "cable_id": f"MH-{ch['channel_id'].removeprefix('CH-')}", "service": ch["signal"],
            "quantity": 1, "cable_order_code": "Alpha Wire 5610B2201",
            "construction": "1 twisted pair, 22 AWG 7/30 bare copper, overall foil shield, 22 AWG tinned drain, PVC jacket",
            "temperature_rating_c": 105, "voltage_rating_vrms": 300, "nominal_od_mm": 4.88,
            "minimum_bend_radius_mm": 48.8, "finished_length_mm": 1000,
            "route": "MEASUREMENT PANEL TO cDAQ BENCH ONLY; CLAMP AT PANEL AND NI-9971 BACKSHELL",
            "moving_service": "NO", "built": "NO", "warning": WARNING,
        })
    rows.append({
        "cable_id":"MH-SYNC-01","service":"battery-only timing slate","quantity":1,
        "cable_order_code":"Alpha Wire 5610B2201","construction":"1 twisted pair, 22 AWG 7/30 bare copper, foil shield and drain",
        "temperature_rating_c":105,"voltage_rating_vrms":300,"nominal_od_mm":4.88,"minimum_bend_radius_mm":48.8,
        "finished_length_mm":1000,"route":"JTTL TO NI-9924; drain to SH at NI end only; NI ferrite 782803-01 adjacent to module",
        "moving_service":"NO","built":"NO","warning":WARNING,
    })
    return rows


def bom_rows() -> list[dict]:
    return [
        {"item":"CABLE-ANALOG","manufacturer":"Alpha Wire","order_code":"5610B2201","quantity":"8 x 1.12 m cut","use":"eight independent analog twisted-pair cables","selection_state":"EXACT CANDIDATE; STOCK/LOT QUOTE REQUIRED","procurement_released":"NO","warning":WARNING},
        {"item":"CABLE-SYNC","manufacturer":"Alpha Wire","order_code":"5610B2201","quantity":"1 x 1.12 m cut","use":"battery-slate TTL/COM plus shield drain","selection_state":"EXACT CANDIDATE; STOCK/LOT QUOTE REQUIRED","procurement_released":"NO","warning":WARNING},
        {"item":"PANEL-PLUG","manufacturer":"Phoenix Contact","order_code":"1757019","quantity":9,"use":"J1O-J8O and JTTL mating plugs","selection_state":"EXACT CANDIDATE","procurement_released":"NO","warning":WARNING},
        {"item":"PANEL-FERRULE","manufacturer":"Phoenix Contact","order_code":"3203066","quantity":18,"use":"0.34 mm2, 8 mm ferrule candidate at panel plugs","selection_state":"EXACT CANDIDATE; TERMINATION PROCESS VALIDATION REQUIRED","procurement_released":"NO","warning":WARNING},
        {"item":"DAQ-FERRULE","manufacturer":"Phoenix Contact","order_code":"3203053","quantity":16,"use":"0.34 mm2, 6 mm ferrule candidate at NI-9976","selection_state":"EXACT CANDIDATE; CRIMP VALIDATION REQUIRED","procurement_released":"NO","warning":WARNING},
        {"item":"DAQ-PLUG","manufacturer":"NI","order_code":"196739-01","quantity":"2 kits / 8 plugs (modules normally include plugs)","use":"NI-9976 two-position screw plugs","selection_state":"EXACT SERVICE-SPARE CANDIDATE; RECEIPT INVENTORY REQUIRED","procurement_released":"NO","warning":WARNING},
        {"item":"DAQ-BACKSHELL","manufacturer":"NI","order_code":"196375-01","quantity":"2 kits / 8 backshells","use":"NI-9971 strain relief/operator protection for all analog channels","selection_state":"EXACT CANDIDATE","procurement_released":"NO","warning":WARNING},
        {"item":"SYNC-BLOCK","manufacturer":"NI","order_code":"781922-01","quantity":1,"use":"NI-9924 D-sub to screw-terminal block","selection_state":"EXACT CANDIDATE","procurement_released":"NO","warning":WARNING},
        {"item":"SYNC-FERRITE","manufacturer":"NI","order_code":"782803-01","quantity":1,"use":"NI-9401 clamp-on ferrite installed adjacent to module","selection_state":"EXACT DOCUMENTED EMC ACCESSORY","procurement_released":"NO","warning":WARNING},
        {"item":"LABELS","manufacturer":"Brady or equivalent","order_code":"SELECTION REQUIRED","quantity":"18 endpoint plus 9 cable labels","use":"channel, polarity, cable ID and NO ROBOT 24 V labels","selection_state":"SELECTION REQUIRED","procurement_released":"NO","warning":WARNING},
    ]


def source_rows() -> list[dict]:
    return [
        {"source_id":"MH-S01","manufacturer":"NI","document":"NI-9229 Datasheet 374184C-02","revision_or_date":"374184C-02; accessed 2026-08-19","url":"https://download.ni.com/support/manuals/374184c_02.pdf","verified_scope":"AI labels, 30-14 AWG copper, 6 mm strip, 90 C minimum wire, 0.22-0.25 N m terminals, 0.20 N m flanges, 0.25-1.5 mm2 ferrules","warning":WARNING},
        {"source_id":"MH-S02","manufacturer":"NI","document":"C Series screw-terminal accessory compatibility guide","revision_or_date":"updated 2026-06-30; accessed 2026-08-19","url":"https://www.ni.com/en/support/documentation/cable-accessory-guide/c-series-i-o-cable-accessory-compatibility-guide/c-series-with-screw-terminal-front-connection--i-o-cable---acces.html","verified_scope":"NI-9229 uses NI-9976 196739-01 and NI-9971 196375-01","warning":WARNING},
        {"source_id":"MH-S03","manufacturer":"NI","document":"NI-9924 User Guide and Specifications","revision_or_date":"375924B-01 Apr12; accessed 2026-08-19","url":"https://download.ni.com/support/manuals/375924b.pdf","verified_scope":"terminal numbers, SH use, 16-26 AWG, 4.5 mm strip, 0.4 N m maximum, strain-relief holes","warning":WARNING},
        {"source_id":"MH-S04","manufacturer":"NI","document":"NI-9401 Getting Started Guide","revision_or_date":"374068G-01 Dec15; accessed 2026-08-19","url":"https://download.ni.com/support/manuals/374068g.pdf","verified_scope":"pin 14 DIO0, pin 1 COM, pin 15 NC; shielded cable and ferrite 782803-01 required for specified EMC performance","warning":WARNING},
        {"source_id":"MH-S05","manufacturer":"Alpha Wire","document":"5610B2201 product record","revision_or_date":"live official record; accessed 2026-08-19","url":"https://www.alphawire.com/products/cable/alpha-essentials/tray-cable/5610b2201","verified_scope":"one 22 AWG twisted pair, shield/drain, 105 C, 300 Vrms, 4.88 mm maximum OD class, 10x diameter bend radius","warning":WARNING},
        {"source_id":"MH-S06","manufacturer":"Phoenix Contact","document":"AI 0,34-6 TQ ferrule 3203053","revision_or_date":"live official record; accessed 2026-08-19","url":"https://www.phoenixcontact.com/en-us/products/ferrule-ai-034-6-tq-3203053","verified_scope":"0.34 mm2 / 22 AWG, 6 mm contact range candidate for NI-9976","warning":WARNING},
        {"source_id":"MH-S07","manufacturer":"Phoenix Contact","document":"AI 0,34-8 TQ ferrule 3203066","revision_or_date":"live official record; accessed 2026-08-19","url":"https://www.phoenixcontact.com/en-us/products/ferrule-ai-034-8-tq-3203066","verified_scope":"0.34 mm2 / 22 AWG, 8 mm contact range candidate for panel plug","warning":WARNING},
        {"source_id":"MH-S08","manufacturer":"Phoenix Contact","document":"MSTB 2,5/2-ST-5,08 1757019","revision_or_date":"live official record; accessed 2026-08-19","url":"https://www.phoenixcontact.com/en-us/products/pcb-connector-mstb-25-2-st-508-1757019","verified_scope":"24-12 AWG; 0.25-2.5 mm2 flexible with ferrule; 7 mm strip; 0.5-0.6 N m; do not mate under load","warning":WARNING},
    ]


def inspection_rows() -> list[dict]:
    tests = [
        ("MH-T01","Incoming identity","Record cable/ferrule/accessory lot and received markings against exact order codes."),
        ("MH-T02","Cut and strip","Record cut length, finished length, strip length and insulation damage for all 18 conductors."),
        ("MH-T03","Crimp pull/section","Qualify the selected crimper/die with sample pull and visual crimp evidence before production terminations."),
        ("MH-T04","Point-to-point","Verify every panel-to-NI contact against the 16-row analog map and four-row sync map."),
        ("MH-T05","Isolation","With all ends disconnected, each analog pair is open to every other pair, shield, slate, enclosure and PE at the approved test threshold."),
        ("MH-T06","Shield disposition","Verify all analog drains are cut back/insulated; sync drain lands only at NI-9924 SH."),
        ("MH-T07","Mechanical retention","NI-9971/flange/plug/zip-tie retention, bend radius and endpoint labels inspected; torque values recorded."),
        ("MH-T08","Sync voltage","With approved cells, measure JTTL and NI-9924 terminal 14 to terminal 1; maximum remains below the NI-9401 input limit."),
        ("MH-T09","Ferrite","NI 782803-01 is installed on the sync cable immediately adjacent to the NI-9401."),
        ("MH-T10","Noise/calibration","Calibrate every analog channel with the complete panel+cable+NI chain and retain raw zero/gain/crosstalk evidence."),
        ("MH-T11","Robot pickoff review","Qualified electrical review accepts physical protected pickoffs without bypassing safety or protection conductors."),
        ("MH-T12","Dry rehearsal","All cables routed and labeled with robot sources absent; mismatch or ambiguity stops the procedure."),
    ]
    return [{"test_id":a,"test":b,"acceptance":c,"result":"NOT EXECUTED","evidence":"REQUIRED","authority":AUTHORITY,"warning":WARNING} for a,b,c in tests]


def open_holds() -> list[dict]:
    holds = [
        ("MH-H01","robot-side protected diagnostic pickoffs","exact terminal hardware, source-proximal short protection, enclosure location and no-bypass fault review for all eight pairs"),
        ("MH-H02","cable/ferrule process","selected crimp tool/die, sample validation, pull evidence and finished-harness inspection"),
        ("MH-H03","analog shield/noise disposition","qualified review of insulated analog drains and measured noise/crosstalk/EMC performance"),
        ("MH-H04","sync cable physical validation","built cable, terminal torque, SH bond, ferrite placement, battery voltage and known-pulse test"),
        ("MH-H05","calibration and uncertainty","complete panel+cable+NI per-channel gain, offset, crosstalk and timing uncertainty"),
        ("MH-H06","independent electrical review","qualified review of source documents, channel identity, terminal maps, loading and fault behavior"),
        ("MH-H07","stage limits and procedure","signed abort limits and stage-specific procedure using the as-built measurement chain"),
        ("MH-H08","FER-G11 physical closure","installed protected points, in-date instruments, dry rehearsal, records and qualified signoff"),
    ]
    return [{"hold_id":a,"item":b,"closure_evidence":c,"state":"OPEN","authority":AUTHORITY,"warning":WARNING} for a,b,c in holds]


def make_svg() -> None:
    lane_y = [150 + i * 62 for i in range(8)]
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1500" height="800" viewBox="0 0 1500 800">',
        '<rect width="1500" height="800" fill="#f7fbff"/>',
        '<style>text{font-family:system-ui,Segoe UI,sans-serif;fill:#0b1d35}.t{font-size:24px;font-weight:800}.s{font-size:16px}.box{fill:#fff;stroke:#082d67;stroke-width:3}.wire{stroke:#145ca8;stroke-width:4;fill:none}.lo{stroke:#4d6f8f}.warn{fill:#ffc83d;stroke:#6e4d00;stroke-width:3}</style>',
        '<text x="50" y="55" font-size="34" font-weight="900">HR-30 first-energization measurement harness P0.1</text>',
        '<rect class="warn" x="50" y="76" width="1400" height="48" rx="8"/><text x="70" y="108" font-size="18" font-weight="900">PRELIMINARY — UNBUILT — ZERO SAFETY CREDIT — NO CONNECTION OR ENERGIZATION AUTHORITY</text>',
        '<rect class="box" x="60" y="145" width="260" height="510" rx="18"/><text class="t" x="90" y="185">Measurement panel</text>',
        '<rect class="box" x="1160" y="145" width="280" height="510" rx="18"/><text class="t" x="1190" y="185">Two NI-9229 modules</text>',
    ]
    for i, (ch, y) in enumerate(zip(CHANNELS, lane_y)):
        parts += [
            f'<text class="s" x="90" y="{y+7}">{html.escape(ch["channel_id"])} · {html.escape(ch["signal"])}</text>',
            f'<path class="wire" d="M320 {y-8} H1160"/><path class="wire lo" d="M320 {y+14} H1160"/>',
            f'<text class="s" x="545" y="{y-15}">Alpha 5610B2201 · 1.0 m · white HI / black LO</text>',
            f'<text class="s" x="1185" y="{y+7}">{ch["module"]} / {ch["ni_channel"]}+ −</text>',
        ]
    parts += [
        '<rect class="box" x="365" y="680" width="380" height="85" rx="14"/><text class="t" x="390" y="716">Battery-only sync slate</text><text class="s" x="390" y="745">JTTL.1 event · JTTL.2 return · no robot power</text>',
        '<path class="wire" d="M745 714 H1100"/><path class="wire lo" d="M745 738 H1100"/>',
        '<rect class="box" x="1100" y="680" width="340" height="85" rx="14"/><text class="t" x="1125" y="716">NI-9924 → NI-9401</text><text class="s" x="1125" y="745">14=DIO0 · 1=COM · 15=NC · drain=SH</text>',
        '</svg>',
    ]
    (OUT / "measurement-harness.svg").write_text("\n".join(parts) + "\n", encoding="utf-8")


def table_html(filename: str, title: str) -> str:
    rows = list(csv.DictReader((OUT / filename).open(encoding="utf-8", newline="")))
    fields = list(rows[0])
    head = "".join(f"<th>{html.escape(x.replace('_',' ').title())}</th>" for x in fields)
    body = "".join("<tr>" + "".join(f"<td>{html.escape(row[x])}</td>" for x in fields) + "</tr>" for row in rows)
    return f'<section><h2>{html.escape(title)}</h2><div class="table"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div></section>'


def make_html() -> None:
    tables = "".join([
        table_html("channel-endpoint-register.csv", "Eight channels, now bound to real HR-30 nets"),
        table_html("analog-contact-map.csv", "Every analog conductor"),
        table_html("sync-contact-map.csv", "Battery-slate sync contacts"),
        table_html("candidate-bom.csv", "Candidate cable BOM"),
        table_html("inspection-test-register.csv", "Build and verification traveler"),
        table_html("open-holds.csv", "Still open before any connection"),
    ])
    (OUT / "index.html").write_text(f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 measurement harness</title><style>:root{{--sky:#9ddcff;--blue:#082d67;--mid:#145ca8;--gold:#ffc83d;--ink:#0b1d35;--paper:#f7fbff;--line:#85bee4}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.55 system-ui,Segoe UI,sans-serif}}header{{padding:clamp(28px,6vw,72px);background:linear-gradient(135deg,var(--blue),var(--mid));color:#fff}}header h1{{font-size:clamp(38px,6vw,70px);line-height:1.03;margin:.3em 0}}main{{max-width:1500px;margin:auto;padding:clamp(18px,4vw,52px)}}.warning{{background:var(--gold);color:#221800;padding:16px;border:3px solid #6e4d00;font-weight:900}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:18px}}article{{background:#fff;border:2px solid var(--blue);border-radius:16px;padding:20px;box-shadow:6px 6px 0 var(--sky)}}.hold{{background:#fff3c8}}.metric{{font-size:clamp(32px,4vw,54px);font-weight:900;color:var(--blue)}}section{{margin:44px 0}}h2{{font-size:clamp(28px,3vw,42px);color:var(--blue)}}.diagram,.table{{overflow:auto;background:#fff;border:2px solid var(--blue);border-radius:14px}}object{{display:block;width:100%;min-width:1000px;min-height:540px}}table{{border-collapse:collapse;width:max-content;min-width:100%}}th,td{{padding:12px 14px;border-bottom:1px solid #a8c4e4;vertical-align:top;max-width:500px;white-space:normal}}th{{position:sticky;top:0;background:var(--blue);color:#fff;font-size:14px;text-align:left}}td{{font-size:16px}}a{{color:#064e9d;font-weight:800}}@media(max-width:650px){{body{{font-size:16px}}th,td{{min-width:180px}}}}</style></head><body><header><div class="warning">{html.escape(WARNING)}</div><p>HR-30 / FER-G11 / NI-side cable definition</p><h1>The measurement panel now reaches exact DAQ terminals.</h1><p>Sixteen analog conductors keep their independent differential paths. The battery slate reaches DIO0 through the exact NI-9924 contacts, shield terminal and required ferrite.</p></header><main><section class="grid"><article><div class="metric">16</div><h2>analog conductors</h2><p>Every HI and LO has a panel contact, color, cable, ferrule and NI terminal.</p></article><article><div class="metric">14 / 1</div><h2>DIO0 / COM</h2><p>NI-9924 terminal 14 is DIO0; terminal 1 is COM. Terminal 15 remains empty.</p></article><article><div class="metric">105 °C</div><h2>cable rating</h2><p>The exact Alpha Wire candidate exceeds NI's 90 °C minimum.</p></article><article class="hold"><div class="metric">0</div><h2>authorized connections</h2><p>Robot-side protected pickoffs, build, review and calibration remain open.</p></article></section><section><h2>Complete bench cable map</h2><div class="diagram"><object data="measurement-harness.svg" type="image/svg+xml" aria-label="Eight analog cable pairs and one battery-only sync cable"></object></div></section><section class="grid"><article><h2>Analog independence</h2><p>Each channel uses its own twisted pair and its own isolated NI-9229 input. Analog drain wires remain insulated in this candidate pending measured noise and EMC review.</p></article><article><h2>Sync EMC path</h2><p>The sync drain bonds only to NI-9924 SH, and NI ferrite 782803-01 sits adjacent to the NI-9401. The slate never touches robot power.</p></article><article class="hold"><h2>The last dangerous gap</h2><p>Logical HR-30 nodes are selected, but guarded, source-proximal, short-protected physical pickoff terminals do not yet exist.</p></article></section>{tables}<section><h2>Files</h2><p><a href="channel-endpoint-register.csv">channel endpoints</a> · <a href="analog-contact-map.csv">analog contacts</a> · <a href="sync-contact-map.csv">sync contacts</a> · <a href="cable-assembly-register.csv">cable assemblies</a> · <a href="candidate-bom.csv">BOM</a> · <a href="primary-source-register.csv">sources</a> · <a href="README.md">engineering note</a></p></section></main></body></html>''', encoding="utf-8")


def integrate() -> None:
    status_path = WHOLE / "package-status.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    status.update({
        "first_energization_measurement_harness_present": True,
        "measurement_harness_analog_conductor_map_complete": True,
        "measurement_harness_sync_contact_map_complete": True,
        "measurement_harness_robot_pickoffs_released": False,
        "measurement_harness_built": False,
        "measurement_harness_calibrated": False,
        "fer_g11_closed": False,
        "connection_authority": False,
        "energization_authority": False,
    })
    status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    start, end = "<!-- HR30-MEASUREMENT-HARNESS-P01-START -->", "<!-- HR30-MEASUREMENT-HARNESS-P01-END -->"
    readme = WHOLE / "README.md"
    text = readme.read_text(encoding="utf-8")
    if start in text and end in text:
        text = text.split(start, 1)[0] + text.split(end, 1)[1]
    block = f'''{start}\n## First-energization measurement harness\n\nThe [interactive measurement-harness guide]({OUT.name}/index.html) defines all **16 analog conductors** from the measurement panel to two NI-9229 modules and the exact battery-slate path through NI-9924 terminal 14 (DIO0), terminal 1 (COM), SH and ferrite 782803-01. It also corrects the earlier ambiguous channels to `HARDWIRED_PERMIT`, `K1_COIL_POS` and `K2_COIL_POS`. Robot-side protected diagnostic pickoffs, build, review, calibration and FER-G11 remain open; no connection or energization authority follows.\n{end}\n'''
    readme.write_text(text.rstrip() + "\n\n" + block, encoding="utf-8")
    page = WHOLE / "index.html"
    text = page.read_text(encoding="utf-8")
    if start in text and end in text:
        text = text.split(start, 1)[0] + text.split(end, 1)[1]
    section = f'''{start}<section id="measurement-harness"><h2>The floating measurement panel now has exact NI-side cables</h2><div class="grid"><article class="card pass"><div class="metric">16</div><p>analog conductors individually mapped from panel contacts to NI-9229 terminals.</p></article><article class="card pass"><h3>14 = DIO0, 1 = COM</h3><p>The battery-only slate has an exact NI-9924 contact map, SH termination and required NI ferrite.</p></article><article class="card hold"><h3>Robot pickoffs stay open</h3><p>Protected physical diagnostic terminals, build, calibration and FER-G11 still block connection.</p></article></div><p><a href="{OUT.name}/index.html">Open the interactive measurement-harness guide</a>.</p></section>{end}'''
    text = text.replace("</main>", section + "</main>", 1)
    page.write_text(text, encoding="utf-8")


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    write_csv(OUT / "channel-endpoint-register.csv", channel_rows())
    write_csv(OUT / "analog-contact-map.csv", analog_contact_rows())
    write_csv(OUT / "sync-contact-map.csv", sync_rows())
    write_csv(OUT / "cable-assembly-register.csv", cable_rows())
    write_csv(OUT / "candidate-bom.csv", bom_rows())
    write_csv(OUT / "primary-source-register.csv", source_rows())
    write_csv(OUT / "inspection-test-register.csv", inspection_rows())
    write_csv(OUT / "open-holds.csv", open_holds())
    binding = {
        "identifier": IDENTIFIER, "date": DATE, "warning": WARNING,
        "measurement_panel_status_sha256": sha(PANEL / "panel-status.json"),
        "measurement_panel_contact_map_sha256": sha(PANEL / "connector-contact-map.csv"),
        "instrumentation_status_sha256": sha(INSTRUMENTS / "instrumentation-status.json"),
        "tether_power_net_schedule_sha256": sha(TETHER / "net-schedule.csv"),
        "whole_body_connector_schedule_sha256": sha(WHOLE_ECAD / "connector-schedule.csv"),
        "scope": "NI-SIDE HARNESS DESIGN AND LOGICAL ROBOT-NODE BINDING ONLY; PHYSICAL PICKOFFS/BUILD/TEST OPEN",
    }
    (OUT / "source-binding.json").write_text(json.dumps(binding, indent=2) + "\n", encoding="utf-8")
    status = {
        "identifier": IDENTIFIER, "date": DATE, "warning": WARNING,
        "analog_channel_count": 8, "analog_conductor_count": 16, "analog_cable_count": 8,
        "sync_cable_count": 1, "ni9229_module_count": 2,
        "ni9976_contact_map_complete": True, "ni9971_back_shells_specified": True,
        "ni9924_dio0_terminal": 14, "ni9924_com_terminal": 1, "ni9924_nc_terminal": 15,
        "ni9924_shield_terminal_used": True, "ni9401_ferrite_order_code": "782803-01",
        "channel_label_corrections": ["TTL_LDIST_SAFE_9V", "CTRL_5V", "HARDWIRED_PERMIT_24V", "K1_COIL_24V", "K2_COIL_24V"],
        "robot_logical_nodes_bound": True, "robot_physical_pickoffs_released": False,
        "harness_built": False, "inspection_executed": False, "calibration_executed": False,
        "fer_g11_closed": False, "functional_safety_credit": False,
        "procurement_authority": False, "fabrication_authority": False, "assembly_authority": False,
        "connection_authority": False, "powered_test_authority": False, "motion_authority": False,
        "walking_authority": False, "energization_authority": False,
    }
    (OUT / "harness-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    (OUT / "README.md").write_text(f'''# HR-30 first-energization measurement harness P0.1\n\n**{WARNING}**\n\nThis package replaces the earlier generic DAQ-end labels with a complete NI-side cable candidate. Eight separate Alpha Wire 5610B2201 twisted pairs carry the sixteen analog conductors from panel J1O-J8O to two NI-9229 modules through NI-9976 plugs and NI-9971 backshells. No analog signal or return is shared. The independent battery-slate cable maps JTTL.1 to NI-9924 terminal 14 / NI-9401 DIO0, JTTL.2 to terminal 1 / COM, its drain to SH, and leaves terminal 15 empty; NI ferrite 782803-01 is required adjacent to the module.\n\nThe package also corrects ambiguous instrumentation names: channel 6 is the PNOZ `HARDWIRED_PERMIT`, and channels 7/8 are K1/K2 coil voltages rather than unspecified “coil or mirror” points. The exact HR-30 logical nodes are selected, but the robot and source panels still lack released guarded, source-proximal, short-protected diagnostic terminals. The cable assemblies are unbuilt, inspections and calibration are unexecuted, FER-G11 remains open, and no work authority follows.\n''', encoding="utf-8")
    make_svg()
    make_html()
    shutil.copy2(Path(__file__), OUT / "measurement-harness-source.py")
    shutil.copy2(ROOT / "tools" / "check_hr30_measurement_harness_p01.py", OUT / "measurement-harness-checker.py")
    files = [p for p in OUT.rglob("*") if p.is_file() and p.name != "file-manifest.csv"]
    write_csv(OUT / "file-manifest.csv", [{"path":p.relative_to(OUT).as_posix(),"bytes":p.stat().st_size,"sha256":sha(p),"warning":WARNING} for p in sorted(files)])
    if RELEASE.exists():
        shutil.rmtree(RELEASE)
    shutil.copytree(OUT, RELEASE)
    integrate()
    code = "import sys;sys.path.insert(0,'tools');import generate_hr30_system_package_p01 as s;s.refresh_manifest_and_release()"
    cad_python = ROOT.parent / ".venvs" / "hr-v0-cad" / "Scripts" / "python.exe"
    cp = subprocess.run([str(cad_python), "-c", code], cwd=ROOT, check=False)
    if cp.returncode:
        raise RuntimeError("whole-body manifest/release refresh failed")
    print(json.dumps({"identifier":IDENTIFIER,"analog_channels":8,"analog_conductors":16,"sync_map":"14=DIO0,1=COM,SH=shield","fer_g11_closed":False,"authorities":0}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
