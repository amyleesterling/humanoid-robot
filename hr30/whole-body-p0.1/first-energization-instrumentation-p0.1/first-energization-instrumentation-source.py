#!/usr/bin/env python3
"""Generate the HR-30 first-energization instrumentation package P0.1.

The package defines a real, synchronized candidate measurement chain and an
exact external bench layout for stages E0-E7.  Limits remain provisional or
selection-required; no physical calibration, connection, test, motion, or
energization authority follows.
"""

from __future__ import annotations

import csv
import hashlib
import html
import json
import re
import shutil
import subprocess
from pathlib import Path

import cadquery as cq


ROOT = Path(__file__).resolve().parents[1]
WHOLE = ROOT / "hr30" / "whole-body-p0.1"
OUT = WHOLE / "first-energization-instrumentation-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / "first-energization-instrumentation-p0.1"
CAD_PYTHON = ROOT.parent / ".venvs" / "hr-v0-cad" / "Scripts" / "python.exe"
IDENTIFIER = "HR30-FIRST-ENERGIZATION-INSTRUMENTATION-P0.1"
DATE = "2026-08-18"
WARNING = (
    "PRELIMINARY - UNBUILT FIRST-ENERGIZATION INSTRUMENTATION CANDIDATE - "
    "ABORT LIMITS ARE NOT QUALIFIED OR RELEASED - NOT APPROVED FOR PROCUREMENT, "
    "CONNECTION, POWERED TESTING, MOTION, WALKING OR ENERGIZATION"
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path: Path, records: list[dict]) -> None:
    if not records:
        raise RuntimeError(f"refusing empty register: {path}")
    fields: list[str] = []
    for record in records:
        for field in record:
            if field not in fields:
                fields.append(field)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)


def box(center: tuple[float, float, float], size: tuple[float, float, float]) -> cq.Shape:
    return cq.Workplane("XY").box(*size).translate(center).val()


def cylinder(center: tuple[float, float, float], radius: float, length: float, axis: str = "Z") -> cq.Shape:
    plane = {"X": "YZ", "Y": "XZ", "Z": "XY"}[axis]
    return cq.Workplane(plane).circle(radius).extrude(length / 2, both=True).translate(center).val()


def clean_step(path: Path) -> None:
    path.write_bytes(re.sub(rb"[ \t]+(?=\r?\n)", b"", path.read_bytes()))


def instrument_records() -> list[dict]:
    return [
        {"instrument_id":"INS-01","role":"synchronized acquisition chassis","manufacturer":"NI","model":"cDAQ-9174","order_code":"781157-01","quantity":1,"acquisition":"BORROW/RENT PREFERRED; PURCHASE NOT RELEASED","verified_capability":"4-slot USB chassis; 12.5 ns timing resolution; 50 ppm sample-rate timing accuracy; 9-30 V input; 15 W max; 159.5 x 88.1 x 58.9 mm","calibration_state":"CHASSIS ID/SELF-TEST/SOFTWARE VERSION RECORD REQUIRED","connection_state":"NOT CONNECTED","warning":WARNING},
        {"instrument_id":"INS-02","role":"isolated simultaneous voltage bank A","manufacturer":"NI","model":"NI-9229 screw terminal","order_code":"779785-01","quantity":1,"acquisition":"BORROW/RENT PREFERRED; PURCHASE NOT RELEASED","verified_capability":"4 simultaneous 24-bit differential channels; nominal +/-60 V; 50 kS/s/channel; channel-to-channel isolation","calibration_state":"CURRENT CALIBRATION CERTIFICATE AND SELF-TEST REQUIRED","connection_state":"NOT CONNECTED","warning":WARNING},
        {"instrument_id":"INS-03","role":"isolated simultaneous voltage bank B","manufacturer":"NI","model":"NI-9229 screw terminal","order_code":"779785-01","quantity":1,"acquisition":"BORROW/RENT PREFERRED; PURCHASE NOT RELEASED","verified_capability":"4 simultaneous 24-bit differential channels; nominal +/-60 V; 50 kS/s/channel; channel-to-channel isolation","calibration_state":"CURRENT CALIBRATION CERTIFICATE AND SELF-TEST REQUIRED","connection_state":"NOT CONNECTED","warning":WARNING},
        {"instrument_id":"INS-04","role":"contact-temperature acquisition","manufacturer":"NI","model":"NI-9211","order_code":"779001-01","quantity":1,"acquisition":"BORROW/RENT PREFERRED; PURCHASE NOT RELEASED","verified_capability":"4 thermocouple channels; 24-bit; 14 S/s class; cold-junction compensation; 1-year calibration interval","calibration_state":"CURRENT CALIBRATION CERTIFICATE; ICE-POINT/REFERENCE CHECK REQUIRED","connection_state":"NOT CONNECTED","warning":WARNING},
        {"instrument_id":"INS-05","role":"battery-slate digital event capture","manufacturer":"NI","model":"NI-9401","order_code":"779351-01","quantity":1,"acquisition":"BORROW/RENT PREFERRED; PURCHASE NOT RELEASED","verified_capability":"8 bidirectional 5 V TTL channels; 100 ns propagation; no channel-to-channel isolation","calibration_state":"SELF-TEST AND KNOWN-PULSE CHECK REQUIRED","connection_state":"BATTERY-ONLY SYNC SLATE CANDIDATE; DIRECT ROBOT 24 V CONNECTION PROHIBITED","warning":WARNING},
        {"instrument_id":"INS-06","role":"whole-rail AC/DC current transient","manufacturer":"Tektronix","model":"TCP0150","order_code":"TCP0150","quantity":1,"acquisition":"BORROW/RENT; PURCHASE NOT RELEASED","verified_capability":"25 A and 150 A ranges; 150 A RMS max; 500 A peak pulse; DC-20 MHz; 3% warranted DC accuracy; TekVPI required","calibration_state":"IN-DATE CALIBRATION; DEGAUSS/AUTOZERO BEFORE EACH SESSION","connection_state":"NOT CLAMPED","warning":WARNING},
        {"instrument_id":"INS-07","role":"current/timing oscilloscope","manufacturer":"Tektronix","model":"3 Series MDO / MDO34 family","order_code":"CONFIGURATION/QUOTE REQUIRED","quantity":1,"acquisition":"BORROW/RENT; PURCHASE NOT RELEASED","verified_capability":"manufacturer lists 3 Series MDO as fully compatible with TCP0150 on analog inputs","calibration_state":"EXACT SERIAL/OPTIONS/FIRMWARE/CALIBRATION CERTIFICATE REQUIRED","connection_state":"NOT CONNECTED","warning":WARNING},
        {"instrument_id":"INS-08","role":"setup/polarity/reference DMM","manufacturer":"Fluke","model":"87V MAX CAL","order_code":"5206068","quantity":1,"acquisition":"PURCHASE/BORROW CANDIDATE; NOT RELEASED","verified_capability":"traceable calibration with data; DC voltage 0.1 mV-1000 V; +/-0.05% + 1; DC current 10 A, 20 A for 30 s only","calibration_state":"TRACEABLE CERTIFICATE/EXPIRY AND PRE-USE CHECK REQUIRED","connection_state":"WHOLE-RAIL CURRENT JACK USE PROHIBITED","warning":WARNING},
        {"instrument_id":"INS-09","role":"thermal survey camera","manufacturer":"Teledyne FLIR","model":"E8 Pro","order_code":"QUOTE/REGION SKU REQUIRED","quantity":1,"acquisition":"BORROW/RENT PREFERRED; PURCHASE NOT RELEASED","verified_capability":"320 x 240 IR; 9 Hz; -20 to 550 C; +/-2 C or +/-2% under stated conditions","calibration_state":"SERIAL/FIRMWARE/CALIBRATION STATUS; EMISSIVITY/REFLECTED-TEMP SETUP REQUIRED","connection_state":"NON-CONTACT ONLY","warning":WARNING},
        {"instrument_id":"INS-10","role":"visual event record","manufacturer":"SELECTION REQUIRED","model":"tripod camera with manual exposure and visible time slate","order_code":"SELECTION REQUIRED","quantity":2,"acquisition":"EXISTING EQUIPMENT PREFERRED","verified_capability":"CORRELATION AID ONLY; NOT CALIBRATED TIMING EVIDENCE","calibration_state":"CLOCK SLATE/FRAME-RATE/FILE CHECK REQUIRED","connection_state":"NOT INSTALLED","warning":WARNING},
        {"instrument_id":"INS-11","role":"type-K surface probes","manufacturer":"SELECTION REQUIRED","model":"electrically insulated surface thermocouple assembly","order_code":"SELECTION REQUIRED","quantity":4,"acquisition":"SELECTION REQUIRED","verified_capability":"ATTACHMENT, INSULATION, RANGE, LEAD AND UNCERTAINTY UNVERIFIED","calibration_state":"BATCH/PROBE CERTIFICATE AND REFERENCE CHECK REQUIRED","connection_state":"NOT INSTALLED","warning":WARNING},
    ]


def channel_records() -> list[dict]:
    channels = [
        ("CH-AI-01","INS-02/AI0","ACT_MAIN_SOURCE_12V","source output before interruption","differential voltage","+/-60 V","50 kS/s","E0-E7"),
        ("CH-AI-02","INS-02/AI1","ACT_MAIN_SAFE_12V","robot inlet after dual interruption","differential voltage","+/-60 V","50 kS/s","E0-E7"),
        ("CH-AI-03","INS-02/AI2","TTL_LDIST_SAFE_9V","left distal regulated 9 V rail","differential voltage","+/-60 V","50 kS/s","E2-E7"),
        ("CH-AI-04","INS-02/AI3","CTRL_5V","logic/control rail","differential voltage","+/-60 V","50 kS/s","E1-E7"),
        ("CH-AI-05","INS-03/AI0","ESTOP_CH_A_24V","E-stop channel A diagnostic voltage","differential voltage","+/-60 V","50 kS/s","E3-E7"),
        ("CH-AI-06","INS-03/AI1","HARDWIRED_PERMIT_24V","PNOZ hardwired permit status","differential voltage","+/-60 V","50 kS/s","E3-E7"),
        ("CH-AI-07","INS-03/AI2","K1_COIL_24V","K1 A1-to-A2 coil voltage","differential voltage","+/-60 V","50 kS/s","E3-E7"),
        ("CH-AI-08","INS-03/AI3","K2_COIL_24V","K2 A1-to-A2 coil voltage","differential voltage","+/-60 V","50 kS/s","E3-E7"),
        ("CH-TC-01","INS-04/TC0","T_SOURCE_CONNECTOR","external source/connector hotspot","type-K temperature","PROBE SELECTION REQUIRED","14 S/s class","E2-E7"),
        ("CH-TC-02","INS-04/TC1","T_CONTACTOR_PAIR","dual-interruption assembly hotspot","type-K temperature","PROBE SELECTION REQUIRED","14 S/s class","E3-E7"),
        ("CH-TC-03","INS-04/TC2","T_SELECTED_BRANCH","selected branch/protection hotspot","type-K temperature","PROBE SELECTION REQUIRED","14 S/s class","E4-E7"),
        ("CH-TC-04","INS-04/TC3","T_SELECTED_ACTUATOR","selected actuator case/connector","type-K temperature","PROBE SELECTION REQUIRED","14 S/s class","E5-E7"),
        ("CH-I-01","INS-06 + INS-07/CH1","ACT_MAIN_SOURCE_CONDUCTOR","clamp around one source conductor only","AC/DC current","150 A range for initial whole-body rail","scope >=1 MS/s candidate","E2-E7"),
        ("CH-SCOPE-02","INS-07/CH2","ACT_MAIN_SAFE_12V_COPY","isolated voltage-probe interface selection required","voltage transient","PROBE SELECTION REQUIRED","scope >=1 MS/s candidate","E2-E7"),
        ("CH-DIO-01","INS-05/DIO0","TIME_ZERO_BATTERY_TTL","independent battery-slate event pulse","5 V TTL","0-5.25 V max","hardware timed","E0-E7"),
        ("CH-VIDEO-01","INS-10/A","CELL_OVERVIEW","doors/operator/robot/cell","video correlation","N/A",">=30 fps candidate","E0-E7"),
        ("CH-VIDEO-02","INS-10/B","PDU_CLOSEUP","source/interruption/instruments","video correlation","N/A",">=30 fps candidate","E0-E7"),
        ("CH-IR-01","INS-09","THERMAL_OVERVIEW","selected electrical/mechanical region","radiometric image","-20 to 550 C","9 Hz","E2-E7"),
    ]
    return [{"channel_id":a,"hardware_channel":b,"signal_or_target":c,"measurement_point":d,"measurement":e,"range":f,"sample_rate":g,"required_stages":h,"physical_point_released":"NO","calibration_evidence_present":"NO","warning":WARNING} for a,b,c,d,e,f,g,h in channels]


def stage_bindings() -> list[dict]:
    return [
        {"stage":stage,"stage_name":name,"mandatory_channels":channels,"mandatory_precheck":precheck,"provisional_abort_basis":abort,"execution_state":"NOT EXECUTED","test_lead_signoff":"REQUIRED","warning":WARNING}
        for stage,name,channels,precheck,abort in [
            ("E0","unpowered inspection and continuity","CH-AI-01..08; CH-VIDEO-01..02","all probes disconnected for resistance/continuity work; DMM current jack empty","any unexpected continuity, polarity ambiguity, damaged lead or stale calibration => STOP"),
            ("E1","logic-only source","CH-AI-04..08; CH-VIDEO-01..02","actuator rail physically isolated and zero-motion boundary verified","rail outside qualified E1 source window, unintended permit/coil state or reset-command coupling => REMOVE SOURCE"),
            ("E2","main source no downstream load","CH-AI-01..04; CH-I-01; CH-TC-01; CH-VIDEO-01..02; CH-IR-01","current probe zeroed; source current limit set to approved dummy-load plan","any unexpected output current, reverse polarity, smoke/odor/arcing or voltage outside qualified window => E-STOP/REMOVE SOURCE"),
            ("E3","dual interruption dry exercise","CH-AI-01..08; CH-I-01; CH-TC-01..02; CH-VIDEO-01..02","contact-point selection reviewed; no actuator branch connected","failure to interrupt, mirror/coil disagreement, reset causing permit, or timing outside approved test sheet => E-STOP/REMOVE SOURCE"),
            ("E4","one protected branch dummy load","CH-AI-01..08; CH-I-01; CH-TC-01..03; CH-VIDEO-01..02; CH-IR-01","dummy load and branch protection selected/verified","current/voltage/temperature beyond signed branch test sheet or unstable oscillation => E-STOP/REMOVE SOURCE"),
            ("E5","one actuator torque disabled","ALL EXCEPT UNUSED DIO; selected actuator telemetry additionally logged","actuator restrained; torque enable write prohibited; bus watchdog configured/read back","any motion, torque-enable state, unexplained current, communication loss or temperature beyond signed sheet => E-STOP/REMOVE SOURCE"),
            ("E6","incremental no-motion population","ALL APPLICABLE CHANNELS","only signed branch increment; mass/thermal/current budget updated","any deviation from signed population plan, unexplained current step, thermal trend or permit fault => E-STOP/REMOVE SOURCE"),
            ("E7","whole robot torque disabled in static cell","ALL 18 CHANNELS","all FER gates separately closed; complete cell and restraint accepted","any motion, permit fault, guard/interlock breach, unexpected current/temperature/voltage or observer call => E-STOP/REMOVE SOURCE"),
        ]
    ]


def abort_records() -> list[dict]:
    return [
        {"limit_id":"AL-01","signal":"ACT_MAIN_SOURCE_12V","equipment_boundary":"RSP-500-12 adjustment range 10-13.2 V; exact setup 12.00 V candidate","provisional_observation":"flag outside 11.70-12.30 V only as an engineering review band","automatic_trip":"NONE DEFINED","qualified_limit":"SELECTION REQUIRED","action":"manual E-stop/source removal on unexpected excursion","status":"OPEN - NOT RELEASED","warning":WARNING},
        {"limit_id":"AL-02","signal":"ACT_MAIN_SAFE_12V","equipment_boundary":"downstream XH/XM candidates accept 10.0-14.8 V; system source remains 12 V nominal","provisional_observation":"flag outside 11.5-12.5 V only as an engineering review band","automatic_trip":"NONE DEFINED","qualified_limit":"SELECTION REQUIRED","action":"manual E-stop/source removal; investigate drop/overshoot","status":"OPEN - NOT RELEASED","warning":WARNING},
        {"limit_id":"AL-03","signal":"TTL_LDIST_SAFE_9V","equipment_boundary":"Pololu S18V20F9 candidate fixed 9 V; XC330 accepts 6.5-12.0 V","provisional_observation":"flag outside 8.7-9.3 V only as an engineering review band","automatic_trip":"NONE DEFINED","qualified_limit":"SELECTION REQUIRED","action":"remove source; do not connect actuator until converter/load validation closes","status":"OPEN - NOT RELEASED","warning":WARNING},
        {"limit_id":"AL-04","signal":"CTRL_5V","equipment_boundary":"exact final compute/control converter and loads unresolved","provisional_observation":"NONE - equipment-specific window missing","automatic_trip":"NONE DEFINED","qualified_limit":"SELECTION REQUIRED","action":"remove logic source on unexpected behavior or qualified-sheet excursion","status":"OPEN - NOT RELEASED","warning":WARNING},
        {"limit_id":"AL-05","signal":"ACT_MAIN_SOURCE_CURRENT","equipment_boundary":"RSP-500-12 rated output 41.7 A; project provisional peak demand 60.58 A exceeds source","provisional_observation":"NO NUMERIC ABORT CURRENT RELEASED","automatic_trip":"SOURCE CURRENT LIMIT IS NOT A VALIDATED BRANCH PROTECTION FUNCTION","qualified_limit":"REQUIRES DUMMY-LOAD/BRANCH DATA, FAULT CURRENT, PROTECTION COORDINATION AND DUTY CYCLE","action":"test lead uses signed stage sheet; unexplained current at any level is STOP","status":"OPEN - NOT RELEASED","warning":WARNING},
        {"limit_id":"AL-06","signal":"CONTACT TEMPERATURES","equipment_boundary":"component/connector/probe-specific allowable temperatures unresolved","provisional_observation":"trend and hotspot observation only; no universal Celsius limit invented","automatic_trip":"NONE DEFINED","qualified_limit":"REQUIRES RECEIVED COMPONENT RATINGS, AMBIENT, PROBE ERROR, LOCATION AND QUALIFIED LIMIT","action":"smoke, odor, discoloration, rapid unexplained rise or observer concern => STOP","status":"OPEN - NOT RELEASED","warning":WARNING},
        {"limit_id":"AL-07","signal":"PERMIT/CONTACTOR TIMING","equipment_boundary":"total stopping/interruption-time requirement not yet allocated or physically measured","provisional_observation":"record edge order and raw latency; no pass threshold","automatic_trip":"NONE DEFINED","qualified_limit":"REQUIRES SAFETY REQUIREMENTS SPECIFICATION AND QUALIFIED VALIDATION","action":"wrong sequence, reset-created permit, missing interruption or channel disagreement => STOP","status":"OPEN - NOT RELEASED","warning":WARNING},
        {"limit_id":"AL-08","signal":"ANY VISIBLE MOTION E0-E7","equipment_boundary":"all stages are no-motion; E7 torque disabled","provisional_observation":"zero intentional motion","automatic_trip":"local deterministic torque-disable/E-stop path must be separately validated","qualified_limit":"ANY OBSERVED MOTION IS ABORT FOR THIS PACKAGE","action":"E-stop then source removal; do not reset until cause reviewed","status":"PROCEDURAL ABORT - NOT SAFETY VALIDATION","warning":WARNING},
        {"limit_id":"AL-09","signal":"OPERATOR/OBSERVER CALL","equipment_boundary":"human stop call has no numeric threshold","provisional_observation":"any person may call STOP","automatic_trip":"NONE","qualified_limit":"IMMEDIATE ABORT","action":"E-stop/source removal and preserve data","status":"PROCEDURAL ABORT","warning":WARNING},
    ]


def calibration_records() -> list[dict]:
    return [
        {"check_id":ident,"item":item,"required_evidence":evidence,"frequency":frequency,"state":"NOT EXECUTED","acceptance_authority":"TEST LEAD + QUALIFIED REVIEW WHERE APPLICABLE","warning":WARNING}
        for ident,item,evidence,frequency in [
            ("CAL-01","cDAQ chassis/modules","serials, DAQmx version, self-test, calibration certificates and expiry","before first use and every session identity check"),
            ("CAL-02","NI-9229 voltage channels","zero and known traceable low-voltage source check; polarity; channel map","before each session"),
            ("CAL-03","NI-9211 + four probes","probe identity, open-probe detection, room/reference comparison, attachment photo","before each session and after relocation"),
            ("CAL-04","TCP0150 + scope","serials/certificates, 150 A range, degauss, autozero, closed-jaw zero capture","before each stage that measures current"),
            ("CAL-05","Fluke 87V MAX CAL","traceable certificate with data, lead/fuse inspection, current jack empty","before each session"),
            ("CAL-06","FLIR E8 Pro","serial/firmware/calibration status, emissivity/reflected temperature/distance and visual reference","before each thermal survey"),
            ("CAL-07","time correlation","single visible/electrical slate pulse recorded by DAQ/scope/video; offset table retained","before each session"),
            ("CAL-08","abort rehearsal","unpowered verbal call, E-stop reach, source disconnect, fire response and data preservation","before each powered session"),
        ]
    ]


def trigger_records() -> list[dict]:
    return [
        {"record_id":"TR-01","system":"cDAQ analog","timebase":"cDAQ-9174 chassis; NI-9229 simultaneous channels; module timing per NI specifications","trigger":"software pre-arm then isolated event edge/analog threshold candidate","pretrigger":">=1 s candidate","posttrigger":">=5 s candidate","released":"NO","warning":WARNING},
        {"record_id":"TR-02","system":"Tektronix scope","timebase":"scope internal; exact MDO34 option/firmware/calibration required","trigger":"TCP0150 current edge or isolated rail-voltage edge","pretrigger":">=20% record candidate","posttrigger":"stage dependent","released":"NO","warning":WARNING},
        {"record_id":"TR-03","system":"cross-system correlation","timebase":"not inherently common between cDAQ, scope, video and FLIR","trigger":"one isolated electrical slate plus visible LED slate; interface selection required","pretrigger":"all recorders rolling before slate","posttrigger":"retain second slate after test","released":"NO - measured offsets/uncertainty required","warning":WARNING},
        {"record_id":"TR-04","system":"video/FLIR","timebase":"camera clocks are correlation aids only","trigger":"continuous recording with visible slate","pretrigger":">=10 s candidate","posttrigger":">=10 s candidate","released":"NO","warning":WARNING},
    ]


def connection_records() -> list[dict]:
    points = [
        ("PC-01","CH-AI-01","source output diagnostic terminals","fused differential leads; exact test-point connector and inline protection selection required"),
        ("PC-02","CH-AI-02","robot inlet after K1/K2","fused differential leads; test point must not bypass interruption"),
        ("PC-03","CH-AI-03","one selected regulated 9 V bus","breakout/test point selection required; other 9 V buses remain disconnected"),
        ("PC-04","CH-AI-04","5 V logic test point","converter/source identity selection required"),
        ("PC-05","CH-AI-05","E-stop A diagnostic node","high-impedance measurement only; exact terminal and protection required"),
        ("PC-06","CH-AI-06","watchdog permit diagnostic node","measurement must not source/hold permit"),
        ("PC-07","CH-AI-07","K1 coil or mirror diagnostic node","exact measured state and terminal selection required"),
        ("PC-08","CH-AI-08","K2 coil or mirror diagnostic node","exact measured state and terminal selection required"),
        ("PC-09","CH-I-01","single ACT_MAIN_SOURCE conductor","split core fully latched; arrow/polarity photographed; no two-conductor clamp"),
        ("PC-10","CH-TC-01..04","four named surfaces","electrically insulated attachment and strain relief selection required"),
        ("PC-11","CH-DIO-01","isolated time-zero interface","direct 24 V connection to NI-9401 prohibited"),
        ("PC-12","CH-SCOPE-02","isolated voltage probe interface","probe/order code and common-mode rating selection required"),
    ]
    return [{"connection_id":a,"channel":b,"physical_boundary":c,"method":d,"connector_pinout_released":"NO","probe_protection_released":"NO","installed":"NO","warning":WARNING} for a,b,c,d in points]


def data_schema() -> list[dict]:
    return [
        {"field":field,"type":kind,"required":"YES","description":description,"warning":WARNING}
        for field,kind,description in [
            ("run_id","string","immutable project run identifier"),("stage","enum E0-E7","energization stage"),
            ("configuration_commit","git SHA","exact repository configuration"),("operator_test_lead","string","named test lead"),
            ("instrument_serials","JSON","every instrument/module/probe serial"),("calibration_records","JSON","certificate identifiers and expiry"),
            ("channel_map_sha256","SHA-256","measurement-channel register identity"),("utc_start","ISO-8601","acquisition start"),
            ("sample_time_s","float64","raw time from acquisition start"),("channel_id","string","controlled channel ID"),
            ("raw_value","float64","unfiltered raw sample"),("engineering_value","float64","scaled value"),
            ("unit","string","engineering unit"),("uncertainty","string","declared calibration/scaling uncertainty or UNRESOLVED"),
            ("event_code","string","operator/trigger/E-stop/abort marker"),("artifact_sha256","SHA-256","hash of raw data/video/image artifact"),
        ]
    ]


def proof_traveler() -> list[dict]:
    return [
        {"step":i,"action":action,"required_record":record,"abort_on_failure":"YES","state":"NOT EXECUTED","warning":WARNING}
        for i,action,record in [
            (1,"verify signed stage sheet, FER gates applicable to stage, site and roles","signed authorization packet"),
            (2,"record repository SHA and freeze channel/limit register hashes","run metadata"),
            (3,"inspect leads, fuses, clamps, probe insulation, strain relief and routing","inspection photos/checklist"),
            (4,"record serials, calibration expiry, firmware/software and self-tests","calibration register"),
            (5,"connect only with all sources locked out and prove absence of voltage","LOTO/absence-of-voltage record"),
            (6,"continuity/polarity/channel injection check without robot power","channel verification file"),
            (7,"rehearse STOP call, E-stop, source removal, fire response and data preservation","rehearsal witness record"),
            (8,"arm DAQ/scope/video/thermal systems and perform correlation slate","time-offset record"),
            (9,"execute only the signed stage while two-person control is maintained","raw synchronized evidence"),
            (10,"abort or complete; remove source; prove absence of voltage before touching probes","shutdown record"),
            (11,"hash raw evidence immediately and write immutable run manifest","data manifest"),
            (12,"review anomalies; no next-stage progression without signed disposition","review disposition"),
        ]
    ]


def sources() -> list[dict]:
    records = [
        ("SRC-01","NI","cDAQ-9174 product page and specifications 374045A","https://www.ni.com/en/shop/hardware/compactdaq-chassis/model-cdaq-9174","live product page + official specification PDF; accessed 2026-08-18","part 781157-01; 4 slots; timing; power; dimensions"),
        ("SRC-02","NI","NI-9229 product page and datasheet 374184C-02","https://www.ni.com/en/shop/hardware/voltage/model-ni-9229","live product page + official datasheet; accessed 2026-08-18","part 779785-01; 4 simultaneous +/-60 V channels; 50 kS/s/ch; isolation"),
        ("SRC-03","NI","NI-9211 product page and datasheet 373466A-02","https://www.ni.com/en-il/shop/model/ni-9211.html","live product page + official datasheet; accessed 2026-08-18","part 779001-01; 4 thermocouple channels; calibration interval 1 year"),
        ("SRC-04","NI","NI-9401 product page and specifications updated 2024-11-05","https://www.ni.com/docs/en-US/bundle/ni-9401-specs/page/specs.html","official live documentation; accessed 2026-08-18","8 TTL DIO; 5.25 V max normal input; no channel-to-channel isolation"),
        ("SRC-05","Tektronix","TCP0150 datasheet 51W-20815-7","https://download.tek.com/datasheet/TCP0150-Datasheet_51W208157.pdf","released 2023-02-06; accessed 2026-08-18","25/150 A ranges; 150 A RMS; 500 A pulse; DC-20 MHz; TekVPI"),
        ("SRC-06","Tektronix","current-probe compatibility page","https://www.tek.com/en/products/oscilloscopes/oscilloscope-probes/current-probes","live official page; accessed 2026-08-18","3 Series MDO listed fully compatible with TCP0150"),
        ("SRC-07","Fluke","87V MAX product page","https://www.fluke.com/en-us/product/electrical-testing/digital-multimeters/87v-max","live official page; accessed 2026-08-18","87V MAX CAL part 5206068; DMM ranges and accuracy"),
        ("SRC-08","Teledyne FLIR","E8 Pro product page","https://www.flir.com/products/e8-pro","live official page; accessed 2026-08-18","320 x 240 IR; 9 Hz; accuracy/range/environment"),
        ("SRC-09","Mean Well","RSP-500 specification","https://www.meanwell.com/Upload/PDF/RSP-500/RSP-500-SPEC.PDF","current official PDF linked by project; accessed 2026-08-18","RSP-500-12 12 V/41.7 A and 10-13.2 V adjustment domain"),
        ("SRC-10","ROBOTIS","XC330-T288 official docs","https://docs.robotis.com/docs/dxl/model_reference/x_series/xc_series/xc330-t288/","live official docs; accessed 2026-08-18","6.5-12.0 V actuator operating range"),
        ("SRC-11","Pololu","S18V20F9 item 2576 product page","https://www.pololu.com/product/2576","live official page; accessed 2026-08-18","9 V regulator candidate identity; installed validation remains open"),
    ]
    return [{"source_id":a,"manufacturer":b,"document":c,"url":d,"revision_or_access_date":e,"verified_scope":f,"system_suitability_verified":"NO","warning":WARNING} for a,b,c,d,e,f in records]


def open_holds() -> list[dict]:
    holds = [
        ("H-01","instrument availability and exact serial/configuration","borrow/rental confirmations, exact scope options and all received serials"),
        ("H-02","calibration status","in-date certificates and pre-use checks for every measurement chain"),
        ("H-03","physical test points and protected probes","released terminal/pin map, fused leads, connectors and strain relief"),
        ("H-04","current and branch abort limits","dummy-load data, fault current, branch protection coordination, inrush and duty cycle"),
        ("H-05","temperature abort limits","received component/connector ratings, probe location/error, ambient and qualified thresholds"),
        ("H-06","interruption/stopping timing limits","safety requirements specification, allocated response limits and validated timing model"),
        ("H-07","digital isolation interface","24 V-to-TTL interface selection, schematic, fault analysis and validation"),
        ("H-08","scope voltage probe","isolated/differential probe exact order code, range, common-mode and calibration"),
        ("H-09","thermocouple probe system","probe type/order code, electrical insulation, attachment, uncertainty and routing"),
        ("H-10","time correlation uncertainty","implemented slate interface and measured DAQ/scope/video/thermal offsets"),
        ("H-11","data acquisition software","frozen DAQmx/FlexLogger or equivalent version, configuration, raw format and alarm behavior"),
        ("H-12","qualified test procedure and signoff","test-lead, electrical and functional-safety review of limits/procedure"),
    ]
    return [{"hold_id":a,"item":b,"closure_evidence":c,"state":"OPEN - SELECTION/EXECUTION REQUIRED","authority":"NONE","warning":WARNING} for a,b,c in holds]


def build_cad() -> dict:
    # Project-defined 900 x 600 mm external bench panel. Instrument geometries are
    # conservative interface envelopes, never manufacturer/fabrication geometry.
    base = box((0,0,15),(900,600,30))
    back = box((0,285,280),(900,30,500))
    rail_a = box((-215,250,200),(430,35,20)); rail_b = box((235,250,200),(430,35,20))
    instruments = {
        "BENCH_BASE": base, "BACK_PANEL": back, "CABLE_RAIL_A": rail_a, "CABLE_RAIL_B": rail_b,
        "CDAQ_9174": box((-270,225,330),(160,90,60)),
        "MDO34_SCOPE": box((60,205,350),(360,160,210)),
        "FLUKE_87VMAX": box((330,130,125),(105,65,220)),
        "TCP0150_CLAMP": cq.Compound.makeCompound([cylinder((-270,145,150),45,32,"Y"),box((-270,160,75),(45,50,100))]),
        "FLIR_E8_PRO": cq.Compound.makeCompound([box((-360,-115,125),(140,95,245)),box((-360,-90,-5),(55,55,120))]),
        "VIDEO_A": box((-170,-230,70),(110,80,80)), "VIDEO_B": box((170,-230,70),(110,80,80)),
        "TERMINAL_GUARD": box((0,60,45),(500,120,60)),
        "E_STOP_REPEATER_ENVELOPE": cylinder((380,-220,65),38,45,"Z"),
    }
    compound = cq.Compound.makeCompound(list(instruments.values()))
    step = OUT / "HR30_first_energization_instrument_bench_candidate.step"
    cq.exporters.export(compound, str(step)); clean_step(step)
    assembly = cq.Assembly()
    colors = [cq.Color(.05,.20,.45,1),cq.Color(.25,.55,.85,1),cq.Color(.98,.72,.08,1),cq.Color(.30,.32,.36,1)]
    for index,(name,shape) in enumerate(instruments.items()):
        assembly.add(shape,name=name,color=colors[index % len(colors)])
    assembly.save(str(OUT / "HR30_first_energization_instrument_bench_candidate.glb"),tolerance=.7,angularTolerance=.2)
    rows=[]
    for name,shape in instruments.items():
        bb=shape.BoundingBox()
        rows.append({"item_id":name,"representation":"PROJECT BENCH GEOMETRY" if name in {"BENCH_BASE","BACK_PANEL","CABLE_RAIL_A","CABLE_RAIL_B","TERMINAL_GUARD"} else "INSTRUMENT INTERFACE ENVELOPE ONLY","xmin_mm":round(bb.xmin,3),"xmax_mm":round(bb.xmax,3),"ymin_mm":round(bb.ymin,3),"ymax_mm":round(bb.ymax,3),"zmin_mm":round(bb.zmin,3),"zmax_mm":round(bb.zmax,3),"manufacturing_source":"NO","warning":WARNING})
    write_csv(OUT/"bench-layout-register.csv",rows)
    return {"bench_extent_mm":[round(compound.BoundingBox().xlen,3),round(compound.BoundingBox().ylen,3),round(compound.BoundingBox().zlen,3)],"modeled_item_count":len(instruments)}


def table_html(filename: str, title: str) -> str:
    with (OUT/filename).open(encoding="utf-8",newline="") as handle:
        records=list(csv.DictReader(handle))
    fields=list(records[0])
    head="".join(f"<th>{html.escape(f.replace('_',' ').title())}</th>" for f in fields)
    body="".join("<tr>"+"".join(f"<td>{html.escape(str(row[f]))}</td>" for f in fields)+"</tr>" for row in records)
    return f"<section><h2>{html.escape(title)}</h2><div class='table-wrap'><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div></section>"


def make_html() -> None:
    tables="".join([
        table_html("instrument-register.csv","Candidate instruments"),table_html("measurement-channel-register.csv","Measurement channels"),
        table_html("stage-instrument-binding.csv","E0-E7 measurement binding"),table_html("provisional-abort-limit-register.csv","Abort limits and unresolved thresholds"),
        table_html("probe-connection-register.csv","Probe connection plan"),table_html("calibration-and-verification-register.csv","Calibration and pre-use checks"),
        table_html("trigger-and-timebase-register.csv","Triggers and time correlation"),table_html("dry-rehearsal-traveler.csv","Dry rehearsal traveler"),
        table_html("open-holds.csv","Open holds"),table_html("candidate-bom.csv","Candidate acquisition list"),
    ])
    text=f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>HR-30 energization instrumentation P0.1</title><script type='module' src='https://ajax.googleapis.com/ajax/libs/model-viewer/4.0.0/model-viewer.min.js'></script><style>
:root{{--sky:#9ddcff;--blue:#082d67;--mid:#145ca8;--gold:#ffc83d;--ink:#0b1d35;--paper:#f7fbff;--hold:#fff0b8}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.55 system-ui,sans-serif}}header{{padding:clamp(28px,6vw,72px);background:linear-gradient(135deg,var(--blue),var(--mid));color:white}}header h1{{font-size:clamp(34px,6vw,68px);line-height:1.03;margin:.25em 0}}header p{{max-width:82ch}}.warning{{background:var(--gold);color:#221800;padding:16px;border:3px solid #6e4d00;font-weight:850}}main{{max-width:1500px;margin:auto;padding:clamp(18px,4vw,52px)}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:18px}}.card{{background:white;border:2px solid var(--blue);border-radius:16px;padding:20px;box-shadow:6px 6px 0 var(--sky)}}.hold{{background:var(--hold)}}.metric{{font-size:clamp(30px,4vw,52px);font-weight:900;color:var(--blue)}}model-viewer{{width:100%;height:min(70vh,700px);min-height:480px;background:linear-gradient(#dff4ff,#fff);border:3px solid var(--blue);border-radius:18px}}section{{margin:46px 0}}h2{{font-size:clamp(26px,3vw,40px);color:var(--blue)}}.table-wrap{{overflow:auto;border:2px solid var(--blue);border-radius:12px;background:white}}table{{border-collapse:collapse;width:max-content;min-width:100%}}th,td{{padding:12px 14px;border-bottom:1px solid #a8c4e4;vertical-align:top;max-width:460px;white-space:normal}}th{{position:sticky;top:0;background:var(--blue);color:white;font-size:14px;text-align:left}}td{{font-size:16px}}a{{color:#064e9d;font-weight:750}}@media(max-width:650px){{model-viewer{{min-height:420px}}th,td{{min-width:180px}}}}
</style></head><body><header><div class='warning'>{html.escape(WARNING)}</div><p>HR-30 / whole-body P0.1 / FER-G11</p><h1>Measure first. Energize later.</h1><p>This package turns six generic instrument placeholders into a real channel architecture for rail voltage/current, permit and contactor timing, contact temperature, thermal imaging and video correlation. It does not close FER-G11.</p></header><main><section><div class='grid'><article class='card'><div class='metric'>18</div><h2>controlled channels</h2><p>Eight isolated analog, four temperature, current, scope, digital, thermal and video channels.</p></article><article class='card'><div class='metric'>E0-E7</div><h2>bound stages</h2><p>Every stage says what must be measured, checked and preserved.</p></article><article class='card hold'><div class='metric'>0</div><h2>qualified numeric trips</h2><p>No fuse, current, temperature or stopping-time limit is invented.</p></article></div></section><section><h2>External instrument bench</h2><model-viewer src='HR30_first_energization_instrument_bench_candidate.glb' camera-controls shadow-intensity='1' exposure='1.05' camera-orbit='30deg 68deg 105%'></model-viewer><p><a href='HR30_first_energization_instrument_bench_candidate.step'>Download editable STEP</a>. Instrument bodies are interface envelopes; received hardware controls.</p></section><section><h2>Hard boundaries</h2><div class='grid'><article class='card'><h3>No DMM rail current</h3><p>The Fluke input is limited to 10 A continuously, so whole-rail current must use the 150 A clamp chain.</p></article><article class='card'><h3>No direct 24 V into TTL</h3><p>The NI-9401 remains disconnected until an isolated, protected 24 V-to-TTL interface is selected and verified.</p></article><article class='card'><h3>No universal temperature number</h3><p>Actual component ratings, probe error, ambient and attachment location must set each threshold.</p></article></div></section>{tables}</main></body></html>"""
    (OUT/"index.html").write_text(text,encoding="utf-8")


def publish(meta: dict) -> None:
    write_csv(OUT/"instrument-register.csv",instrument_records())
    write_csv(OUT/"measurement-channel-register.csv",channel_records())
    write_csv(OUT/"stage-instrument-binding.csv",stage_bindings())
    write_csv(OUT/"provisional-abort-limit-register.csv",abort_records())
    write_csv(OUT/"calibration-and-verification-register.csv",calibration_records())
    write_csv(OUT/"trigger-and-timebase-register.csv",trigger_records())
    write_csv(OUT/"probe-connection-register.csv",connection_records())
    write_csv(OUT/"data-file-schema.csv",data_schema())
    write_csv(OUT/"dry-rehearsal-traveler.csv",proof_traveler())
    write_csv(OUT/"primary-source-register.csv",sources())
    write_csv(OUT/"open-holds.csv",open_holds())
    bom = [
        ("B-01","NI cDAQ-9174 chassis","781157-01",1,"BORROW/RENT PREFERRED"),("B-02","NI-9229 screw-terminal module","779785-01",2,"BORROW/RENT PREFERRED"),
        ("B-03","NI-9211 thermocouple module","779001-01",1,"BORROW/RENT PREFERRED"),("B-04","NI-9401 TTL DIO module","779351-01",1,"BORROW/RENT; HOLD DISCONNECTED"),
        ("B-05","TCP0150 current probe","TCP0150",1,"BORROW/RENT"),("B-06","compatible 3 Series MDO oscilloscope","MDO34 CONFIGURATION REQUIRED",1,"BORROW/RENT"),
        ("B-07","Fluke 87V MAX CAL","5206068",1,"PURCHASE/BORROW CANDIDATE"),("B-08","FLIR E8 Pro","REGION SKU/QUOTE REQUIRED",1,"BORROW/RENT"),
        ("B-09","insulated type-K surface probes","SELECTION REQUIRED",4,"SELECTION REQUIRED"),("B-10","protected differential lead sets","SELECTION REQUIRED",8,"SELECTION REQUIRED"),
        ("B-11","isolated 24 V-to-TTL event interface","SELECTION REQUIRED",1,"SELECTION REQUIRED"),("B-12","isolated scope voltage probe","SELECTION REQUIRED",1,"SELECTION REQUIRED"),
        ("B-13","tripod video cameras","SELECTION REQUIRED",2,"EXISTING EQUIPMENT PREFERRED"),("B-14","900 x 600 instrument bench/guard fixture","PROJECT CAD CANDIDATE",1,"DFM/ASSEMBLY SELECTION REQUIRED"),
    ]
    write_csv(OUT/"candidate-bom.csv",[{"item_id":a,"item":b,"candidate_order_code":c,"quantity":d,"acquisition":e,"procurement_released":"NO","warning":WARNING} for a,b,c,d,e in bom])
    status={"identifier":IDENTIFIER,"date":DATE,"warning":WARNING,**meta,"instrument_candidate_count":11,"controlled_channel_count":18,"stage_count":8,"abort_record_count":9,"generic_instrument_placeholders_replaced":True,"synchronized_voltage_architecture_defined":True,"whole_rail_current_path_defined":True,"dmm_whole_rail_current_prohibited":True,"direct_24v_to_ttl_prohibited":True,"numeric_current_abort_released":False,"numeric_temperature_abort_released":False,"stopping_time_limit_released":False,"physical_test_points_released":False,"calibration_evidence_present":False,"dry_rehearsal_executed":False,"fer_g11_closed":False,"procurement_authority":False,"connection_authority":False,"powered_test_authority":False,"motion_authority":False,"walking_authority":False,"energization_authority":False}
    (OUT/"instrumentation-status.json").write_text(json.dumps(status,indent=2)+"\n",encoding="utf-8")
    binding={"identifier":IDENTIFIER,"warning":WARNING,"authoritative_fer_register":"hr30/whole-body-p0.1/first-energization-readiness-p0.1/energization-gate-register.csv","authoritative_fer_register_sha256":sha(WHOLE/"first-energization-readiness-p0.1"/"energization-gate-register.csv"),"power_budget":"hr30/whole-body-p0.1/energy-safety-spine-p0.1/current-power-budget.csv","power_budget_sha256":sha(WHOLE/"energy-safety-spine-p0.1"/"current-power-budget.csv"),"scope":"FER-G11 DESIGN EVIDENCE ONLY; PHYSICAL EXECUTION/QUALIFICATION OPEN"}
    (OUT/"source-binding.json").write_text(json.dumps(binding,indent=2)+"\n",encoding="utf-8")
    (OUT/"README.md").write_text(f"""# HR-30 first-energization instrumentation P0.1

**{WARNING}**

This package replaces the earlier generic instrument placeholders with an exact candidate architecture: a cDAQ-9174 chassis, two isolated NI-9229 voltage banks, NI-9211 temperature acquisition, a held-disconnected NI-9401, a TCP0150/MDO34 current-transient chain, a calibrated DMM candidate, thermal camera and two video views. Eighteen channels are bound to stages E0-E7 and an editable external bench STEP/GLB shows the physical layout.

The package intentionally does **not** invent fuse, current, temperature or stopping-time limits. The voltage bands are engineering observation bands only. FER-G11 remains open until exact instruments are received, calibration evidence is current, protected test points are released, the dry rehearsal is executed, and qualified reviewers freeze the stage-specific limits and procedure.

Open `index.html` for the interactive guide.
""",encoding="utf-8")
    make_html()


def integrate() -> None:
    status_path=WHOLE/"package-status.json"; status=json.loads(status_path.read_text(encoding="utf-8"))
    status.update({"first_energization_instrumentation_present":True,"first_energization_instrumentation_channel_architecture_defined":True,"first_energization_instrumentation_physical_evidence_present":False,"first_energization_instrumentation_limits_qualified":False,"fer_g11_closed":False})
    status_path.write_text(json.dumps(status,indent=2)+"\n",encoding="utf-8")
    start,end="<!-- HR30-FER-INSTRUMENTS-P01-START -->","<!-- HR30-FER-INSTRUMENTS-P01-END -->"
    readme=WHOLE/"README.md"; text=readme.read_text(encoding="utf-8")
    if start in text and end in text: text=text.split(start,1)[0]+text.split(end,1)[1]
    block=f"""{start}
## First-energization instrumentation

The [interactive instrumentation guide](first-energization-instrumentation-p0.1/index.html) defines an **18-channel E0-E7 measurement architecture**: eight isolated analog channels, four contact temperatures, a 150 A current-probe chain, scope voltage, a held-disconnected digital timing input, thermal imaging and two video views. It includes an external bench STEP/GLB, exact candidate order codes, calibration checks, protected connection obligations, time-correlation method, raw-data schema and dry-rehearsal traveler. Numeric current, temperature and stopping-time limits remain unresolved; no physical calibration or rehearsal has been executed, so FER-G11 remains open.
{end}
"""
    readme.write_text(text.rstrip()+"\n\n"+block,encoding="utf-8")
    page=WHOLE/"index.html"; text=page.read_text(encoding="utf-8")
    if start in text and end in text: text=text.split(start,1)[0]+text.split(end,1)[1]
    section=f"""{start}<section id='fer-instruments'><h2>The first-energization stages now have a real measurement architecture</h2><div class='grid'><article class='card pass'><div class='metric'>18</div><p>controlled channels cover voltage, current, timing, temperature, thermal and video evidence.</p></article><article class='card pass'><h3>Instrumented E0-E7</h3><p>Every stage names mandatory channels, prechecks, abort conditions and retained evidence.</p></article><article class='card hold'><h3>FER-G11 stays open</h3><p>Calibration, protected test points and qualified numeric current, temperature and timing limits are not yet physical evidence.</p></article></div><p><a href='first-energization-instrumentation-p0.1/index.html'>Open the interactive instrumentation guide</a>.</p></section>{end}"""
    text=text.replace("</main>",section+"</main>",1); page.write_text(text,encoding="utf-8")


def bind_measurement_boundary_panel() -> None:
    panel = WHOLE / "electrical" / "measurement-boundary-panel-p0.1"
    panel_status = panel / "panel-status.json"
    if not panel_status.exists():
        return
    probe_path = OUT / "probe-connection-register.csv"
    with probe_path.open(encoding="utf-8", newline="") as handle:
        probe_rows = list(csv.DictReader(handle))
    for row in probe_rows:
        if row["channel"].startswith("CH-AI-"):
            number = int(row["channel"].split("-")[-1])
            row["method"] = f"route through measurement panel J{number}I -> J{number}O; exact field and NI harnesses remain open"
            row["connector_pinout_released"] = "PANEL CONTACTS RELEASED; FIELD/DAQ ENDS OPEN"
            row["probe_protection_released"] = "CURRENT-LIMITING DESIGN PRESENT; NOT PHYSICALLY VALIDATED"
            row["installed"] = "NO"
        elif row["channel"] == "CH-DIO-01":
            row["method"] = "independent battery sync slate JTTL -> NI-9924 DIO0/COM; direct robot 24 V remains prohibited"
            row["connector_pinout_released"] = "PANEL CONTACTS RELEASED; NI CONTACTS OPEN"
            row["probe_protection_released"] = "BATTERY-ONLY 1K SERIES DESIGN PRESENT; NOT PHYSICALLY VALIDATED"
            row["installed"] = "NO"
    write_csv(probe_path, probe_rows)
    status_path = OUT / "instrumentation-status.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    status.update({
        "measurement_boundary_panel_design_present": True,
        "measurement_boundary_panel_installed": False,
        "measurement_boundary_panel_calibrated": False,
        "physical_test_points_released": False,
        "fer_g11_closed": False,
    })
    status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    binding_path = OUT / "source-binding.json"
    binding = json.loads(binding_path.read_text(encoding="utf-8"))
    binding.update({
        "measurement_boundary_panel": "hr30/whole-body-p0.1/electrical/measurement-boundary-panel-p0.1",
        "measurement_boundary_panel_status_sha256": sha(panel_status),
        "measurement_boundary_scope": "PANEL CONTACT MAP/DESIGN PRESENT; FIELD HARNESS, INSTALLATION, CALIBRATION AND QUALIFICATION OPEN",
    })
    binding_path.write_text(json.dumps(binding, indent=2) + "\n", encoding="utf-8")
    bom_path = OUT / "candidate-bom.csv"
    with bom_path.open(encoding="utf-8", newline="") as handle:
        bom = [row for row in csv.DictReader(handle) if row["item_id"] != "B-15"]
    bom.append({"item_id":"B-15","item":"eight-channel floating measurement boundary panel + battery sync slate","candidate_order_code":"PROJECT NATIVE KICAD/CAD P0.1; PASSIVE ORDER CODES OPEN","quantity":"1","acquisition":"FABRICATION/ASSEMBLY NOT RELEASED","procurement_released":"NO","warning":WARNING})
    write_csv(bom_path, bom)
    marker_start, marker_end = "<!-- HR30-MEASUREMENT-BOUNDARY-P01-START -->", "<!-- HR30-MEASUREMENT-BOUNDARY-P01-END -->"
    readme_path = OUT / "README.md"; readme = readme_path.read_text(encoding="utf-8")
    if marker_start in readme and marker_end in readme:
        readme = readme.split(marker_start, 1)[0] + readme.split(marker_end, 1)[1]
    readme += f"\n{marker_start}\n## Physical measurement boundary\n\nThe [measurement-boundary panel](../electrical/measurement-boundary-panel-p0.1/index.html) now defines the eight floating analog panel contacts and independent battery sync-slate output. Field/DAQ harnesses, fabrication, calibration, timing uncertainty and qualified limits remain open; FER-G11 remains open.\n{marker_end}\n"
    readme_path.write_text(readme, encoding="utf-8")
    page_path = OUT / "index.html"; page = page_path.read_text(encoding="utf-8")
    if marker_start in page and marker_end in page:
        page = page.split(marker_start, 1)[0] + page.split(marker_end, 1)[1]
    section = f'''{marker_start}<section><h2>A physical panel now replaces generic voltage clips</h2><div class="grid"><article class="card"><div class="metric">8 x 2</div><p>mutually floating, current-limited analog conductors.</p></article><article class="card"><h2>Battery sync slate</h2><p>The visible LED and TTL event have no robot electrical connection.</p></article><article class="card hold"><h2>Still unbuilt</h2><p>Harnesses, calibration and qualified limits remain open; FER-G11 is not closed.</p></article></div><p><a href="../electrical/measurement-boundary-panel-p0.1/index.html">Open the measurement-boundary panel guide</a>.</p></section>{marker_end}'''
    page_path.write_text(page.replace("</main>", section + "</main>", 1), encoding="utf-8")


def manifest_release() -> None:
    shutil.copy2(Path(__file__),OUT/"first-energization-instrumentation-source.py")
    files=[p for p in OUT.rglob("*") if p.is_file() and p.name!="file-manifest.csv"]
    write_csv(OUT/"file-manifest.csv",[{"path":p.relative_to(OUT).as_posix(),"bytes":p.stat().st_size,"sha256":sha(p),"warning":WARNING} for p in sorted(files)])
    if RELEASE.exists(): shutil.rmtree(RELEASE)
    shutil.copytree(OUT,RELEASE)
    code="import sys;sys.path.insert(0,'tools');import generate_hr30_system_package_p01 as s;s.refresh_manifest_and_release()"
    result=subprocess.run([str(CAD_PYTHON),"-c",code],cwd=ROOT)
    if result.returncode: raise RuntimeError("whole-body manifest/release refresh failed")


def main() -> int:
    if OUT.exists(): shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    meta=build_cad(); publish(meta); bind_measurement_boundary_panel(); integrate(); manifest_release()
    print(json.dumps({"identifier":IDENTIFIER,**meta,"instrument_candidates":11,"channels":18,"authorities":0},indent=2))
    return 0


if __name__=="__main__": raise SystemExit(main())
