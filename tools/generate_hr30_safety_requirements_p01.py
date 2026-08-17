"""Generate the HR-30 whole-body safety requirements candidate.

This package turns the existing risk controls into a reviewable SRS and
validation plan.  It deliberately does not calculate or claim an achieved
performance level, execute a test, or grant work authority.
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
OUT = WHOLE / "safety-requirements-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / OUT.name
IDENTIFIER = "HR30-WHOLE-BODY-SRS-P0.1"
WARNING = "PRELIMINARY - SAFETY REQUIREMENTS CANDIDATE ONLY - NOT FUNCTIONALLY SAFETY VALIDATED - NOT APPROVED FOR CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
AUTHORITY = "NO CONNECTION, POWERED-TEST, MOTION, OR ENERGIZATION AUTHORITY"
ACCESS_DATE = "2026-08-16"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise RuntimeError(f"refusing empty CSV: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def common(row: dict) -> dict:
    return {**row, "validation_state": "NOT VALIDATED", "authority": AUTHORITY, "warning": WARNING}


def source_rows() -> list[dict]:
    official = [
        ("SRC-ISO-12100", "ISO", "ISO 12100:2010", "Edition 1; published 2010-11; current publication is marked to be revised", "machinery risk assessment and risk reduction methodology", "https://www.iso.org/standard/51528.html"),
        ("SRC-ISO-13849-1", "ISO", "ISO 13849-1:2023", "Edition 4; published 2023-04", "SRP/CS design and performance-level methodology; does not prescribe this robot's PLr", "https://www.iso.org/standard/73481.html"),
        ("SRC-ISO-13849-2", "ISO", "ISO 13849-2:2012", "Edition 2; published 2012-10; current while a replacement is under development", "validation by analysis and test", "https://www.iso.org/standard/53640.html"),
        ("SRC-ISO-13850", "ISO", "ISO 13850:2015", "Edition 3; published 2015-11", "emergency-stop design principles", "https://www.iso.org/standard/59970.html"),
        ("SRC-IEC-60204-1", "IEC", "IEC 60204-1:2016+AMD1:2021 CSV", "Edition 6.1; amendment published 2021-09-15; valid; stability date 2027", "machine electrical equipment, protective bonding, control and emergency-stop boundary", "https://webstore.iec.ch/en/publication/66124"),
        ("SRC-ISO-13482", "ISO", "ISO 13482:2014", "Edition 1; published 2014-02; revision in development", "service/personal-care robot hazard reference; no conformity claim", "https://www.iso.org/standard/53820.html"),
        ("SRC-ISO-23482-1", "ISO", "ISO/TR 23482-1:2020", "Edition 1; published 2020-02", "safety-related test-method guidance for personal-care robots", "https://www.iso.org/standard/71564.html"),
        ("SRC-ISO-23482-2", "ISO", "ISO/TR 23482-2:2019", "Edition 1; published 2019-03", "application guidance for ISO 13482", "https://www.iso.org/standard/71627.html"),
        ("SRC-ISO-13855", "ISO", "ISO 13855:2024", "Edition 3; published 2024-11", "safeguard-position reference; applies to persons age 14+ and excludes gravity falls", "https://www.iso.org/standard/80590.html"),
        ("SRC-ISO-13854", "ISO", "ISO 13854:2017", "Edition 2; published 2017-11; confirmed", "minimum-gap reference for crushing only", "https://www.iso.org/standard/66459.html"),
        ("SRC-PILZ-PNOZ-S4", "Pilz", "PNOZ s4 operating manual 21396-EN-23", "official product page lists manual dated 2026-06-22", "candidate safety relay manual; component capability is not system PL", "https://www.pilz.com/en-US/eshop/product/750104"),
        ("SRC-SCHNEIDER-LC1D40ABD", "Schneider Electric", "TeSys Deca LC1D40ABD and catalog MKTED210011EN", "catalog v17.1 dated 2026-07-10; product page accessed 2026-08-16", "three main poles, 24 VDC coil, mirror-certified 21-22 NC auxiliary and DC table boundary; component capability is not whole-machine PL", "https://shop.se.com/pro/us/en/product/iec-contactor-tesys-deca-nonreversing-40a-30hp-at-480vac-up-to-100ka-sccr-3-phase-3-no-24vdc-coil-open-style/"),
    ]
    rows = [
        {
            "source_id": sid,
            "source_type": "OFFICIAL EXTERNAL",
            "publisher": publisher,
            "document": document,
            "revision_or_date": revision,
            "use": use,
            "path_or_url": url,
            "sha256": "REMOTE DOCUMENT - NOT VENDORED",
            "access_date": ACCESS_DATE,
            "warning": WARNING,
        }
        for sid, publisher, document, revision, use, url in official
    ]
    local = [
        ("SRC-LOCAL-01", "energy/safety status", "energy-safety-spine-p0.1/energy-safety-status.json"),
        ("SRC-LOCAL-02", "existing safety-function boundary", "energy-safety-spine-p0.1/safety-function-boundary.csv"),
        ("SRC-LOCAL-03", "existing fault-response boundary", "energy-safety-spine-p0.1/fault-response-register.csv"),
        ("SRC-LOCAL-04", "tether power-core status", "electrical/tether-power-core-p0.1/power-core-status.json"),
        ("SRC-LOCAL-05", "whole-body physical harness status", "harness/physical-p0.1/physical-harness-status.json"),
        ("SRC-LOCAL-06", "grounding/reference status", "electrical/grounding-reference-architecture-p0.1/grounding-reference-status.json"),
        ("SRC-LOCAL-07", "physical protective-bonding status", "electrical/protective-bonding-implementation-p0.1/physical-bond-status.json"),
        ("SRC-LOCAL-08", "compiled no-motion controller status", "firmware/hr30-motion-controller-p0.1/firmware-status.json"),
        ("SRC-LOCAL-09", "current-policy status", "current-constrained-actuation-p0.1/status.json"),
        ("SRC-LOCAL-10", "25-axis allocation", "actuator-transmission-allocation.csv"),
        ("SRC-LOCAL-11", "standing/walking architecture", "walking-development-architecture.md"),
        ("SRC-LOCAL-12", "whole-body pose register", "whole-body-pose-register.csv"),
    ]
    for sid, role, relative in local:
        path = WHOLE / relative
        if not path.is_file():
            raise FileNotFoundError(path)
        rows.append({
            "source_id": sid,
            "source_type": "LOCAL CONFIGURATION",
            "publisher": "Project Button",
            "document": role,
            "revision_or_date": IDENTIFIER,
            "use": role,
            "path_or_url": path.relative_to(ROOT).as_posix(),
            "sha256": sha(path),
            "access_date": ACCESS_DATE,
            "warning": WARNING,
        })
    return rows


def lifecycle_rows() -> list[dict]:
    data = [
        ("LM-01", "storage/transport", "all sources isolated; joints mechanically secured", "trained handlers only", "NO"),
        ("LM-02", "unpowered assembly", "sources absent and discharged", "trained builders; supported robot", "NO"),
        ("LM-03", "E0 unpowered inspection", "all electrical sources absent", "qualified inspection team", "NO"),
        ("LM-04", "E1 passive electrical tests", "sources absent; discharge verified", "qualified electrical team", "NO"),
        ("LM-05", "E2 logic-only power", "actuator source locked out and motor connectors absent", "guarded bench team", "NO"),
        ("LM-06", "E3 safety-control dry test", "actuator load side de-energized", "guarded bench team", "NO"),
        ("LM-07", "E4 one-axis commissioning", "one actuator in separate guarded fixture", "qualified test team", "NO - read-only torque-disabled"),
        ("LM-08", "E5/E6 branch checks", "no actuators attached", "qualified electrical test team", "NO"),
        ("LM-09", "E7 first whole-body actuator rail", "restrained robot; torque disabled; fresh motion command impossible", "qualified team outside exclusion zone", "NO"),
        ("LM-10", "S1 individual suspended joint", "future separately released motion stage", "qualified motion-test team", "FUTURE - PROHIBITED BY THIS SRS RELEASE"),
        ("LM-11", "S2-S6 restrained standing/walking", "future guarded motion stages", "no public/child access", "FUTURE - PROHIBITED BY THIS SRS RELEASE"),
        ("LM-12", "S7 untethered walking", "future program gate", "not defined", "PROHIBITED"),
        ("LM-13", "maintenance/service", "LOTO; stored energy removed; supports installed", "trained service personnel", "NO"),
        ("LM-14", "public/child interaction", "not part of P0.1 validation envelope", "public/children", "PROHIBITED"),
    ]
    return [common({"mode_id": i, "mode": mode, "required_energy_state": energy, "permitted_personnel": people, "motion_scope": motion}) for i, mode, energy, people, motion in data]


def hazard_rows() -> list[dict]:
    data = [
        ("HZ-01", "E2-E7", "unexpected joint motion during boot or rail application", "impact, crush, shear or fall", "test team", "S2", "F1", "P1", "d", "torque-disabled firmware, physical restraint, exclusion zone, dual interruption"),
        ("HZ-02", "E3-E7", "E-stop release or reset initiates motion", "unexpected impact or fall", "test team", "S2", "F1", "P1", "d", "monitored reset restores eligibility only; fresh deterministic motion command remains separate"),
        ("HZ-03", "E3-E7", "one E-stop channel fails open/closed/crossed", "failure to interrupt actuator energy", "test team", "S2", "F1", "P1", "d", "dual direct-opening channels and discrepancy detection candidate"),
        ("HZ-04", "E3-E7", "one contactor welds or fails to open", "continued actuator energy", "test team", "S2", "F1", "P1", "d", "two series contactors plus mirror-contact EDM candidate"),
        ("HZ-05", "E2-E7", "motion-controller reset, brownout or corrupted configuration", "unexpected output or failed stop", "test team", "S2", "F1", "P1", "d", "fail-low initialization, hash/configuration gate, external safety chain"),
        ("HZ-06", "E2-E7", "watchdog heartbeat or output fault", "failure to request stop", "test team", "S2", "F1", "P1", "d", "watchdog is diagnostic only and cannot bypass independent E-stop chain"),
        ("HZ-07", "E5-E7", "branch short, overload or reverse polarity", "fire, burns, conductor damage", "test team", "S2", "F1", "P1", "N/A", "individual branch boundaries; protection and conductor coordination remain open"),
        ("HZ-08", "E1-E7", "mains/PE or exposed-conductive-part fault", "electric shock or fire", "test team", "S2", "F1", "P1", "N/A", "external enclosed mains equipment; protective bonding candidate; qualified approval open"),
        ("HZ-09", "E1-E7", "actuator VDD backfeeds through serial harness", "uncontrolled energization or overload", "test team", "S2", "F1", "P1", "d", "25 individual power pairs; inter-actuator GND/VDD cavities empty; no-backfeed test required"),
        ("HZ-10", "S1-S7", "whole robot tips or falls", "head/body impact, crush or equipment damage", "test team/bystanders", "S2", "F2", "P2", "d", "rated overhead restraint and exclusion zone required; design and proof open"),
        ("HZ-11", "S1-S7", "fall-restraint or attachment fails", "uncontrolled fall", "test team/bystanders", "S2", "F2", "P2", "d", "restraint is uncredited until WLL, dynamic arrest, inspection and proof are accepted"),
        ("HZ-12", "assembly/S1-S7", "joint pinch or crushing gap", "finger/hand injury", "builder/test team", "S2", "F2", "P1", "d", "guards, access controls, slow staged motion and gap review required"),
        ("HZ-13", "S1-S7", "gripper pinch/shear or unexpected release", "finger injury or dropped object", "test team", "S2", "F2", "P1", "c", "force/current limits and guarded test objects; physical grip proof open"),
        ("HZ-14", "S1-S7", "robot link collision with person", "impact injury", "test team/bystanders", "S2", "F2", "P2", "d", "no person in motion envelope; collaborative operation not claimed"),
        ("HZ-15", "S2-S7", "foot traps or strikes a person", "foot/ankle injury", "test team/bystanders", "S2", "F2", "P2", "d", "guarded level test area and exclusion zone; no public access"),
        ("HZ-16", "future onboard power", "battery fault, charger conflict or thermal event", "fire, burns, toxic smoke", "users/test team", "S2", "F1", "P1", "d", "onboard battery and charging are out of first-energization scope"),
        ("HZ-17", "E2-S7", "hot actuator, conductor, supply or electronics", "burn or fire", "builder/test team", "S2", "F2", "P1", "c", "temperature instrumentation and abort limits must be frozen"),
        ("HZ-18", "assembly/service", "sharp edge or burr", "laceration", "builder/service team", "S1", "F2", "P1", "b", "deburr/edge inspection and covers"),
        ("HZ-19", "S1-S7", "fastener or component loosens/ejects", "impact, joint collapse or electrical fault", "test team", "S2", "F1", "P1", "c", "fastener selection, torque, locking and witness marks remain open"),
        ("HZ-20", "E7/S1-S7", "loss of source causes gravity collapse or uncontrolled coast", "crush, fall or structural damage", "test team", "S2", "F2", "P2", "d", "passive support/restraint and measured decay/overtravel required"),
        ("HZ-21", "E2-S7", "network or conversational-agent request reaches actuator path directly", "unbounded or unexpected motion", "test team/public", "S2", "F2", "P2", "d", "structured requests terminate at deterministic local controller; direct bus access prohibited"),
        ("HZ-22", "S2-S7", "bad COM/contact/state estimate", "loss of balance and fall", "test team", "S2", "F2", "P2", "d", "future measured estimator and support-polygon validation; motion remains prohibited"),
        ("HZ-23", "S1-S7", "joint overspeed, limit overrun or encoder disagreement", "impact, pinch or structural overload", "test team", "S2", "F2", "P2", "d", "future safety-related speed/travel architecture is not implemented"),
        ("HZ-24", "service", "stored electrical/mechanical energy remains during service", "shock, burn, pinch or unexpected movement", "service team", "S2", "F2", "P1", "c", "LOTO, discharge verification and mechanical supports"),
    ]
    rows = []
    for i, mode, event, consequence, people, severity, frequency, avoidance, plr, controls in data:
        rows.append(common({
            "hazard_id": i,
            "mode_scope": mode,
            "hazardous_event": event,
            "credible_consequence": consequence,
            "exposed_person": people,
            "project_severity_class": severity,
            "project_frequency_class": frequency,
            "project_avoidance_class": avoidance,
            "candidate_required_pl": plr,
            "existing_or_required_controls": controls,
            "residual_risk_disposition": "OPEN - QUALIFIED RISK ASSESSMENT AND VALIDATION REQUIRED",
        }))
    return rows


def function_rows() -> list[dict]:
    data = [
        ("SFR-01", "Emergency-stop demand removes actuator energy", "E3-E7", "both K1/K2 main paths open", "dual NC E-stop", "PNOZ s4 candidate", "two independent LC1D40ABD contactors with three main poles in series per device", "manual reset plus fresh motion command", "d", "Category 3 candidate", "IMPLEMENTED AS UNVALIDATED TOPOLOGY", "NO"),
        ("SFR-02", "Prevention of unexpected restart", "E3-E7", "actuator permit absent and motion state inactive", "E-stop/reset/EDM/configuration state", "PNOZ monitored start plus deterministic controller", "contactor coils and motion-enable boundary", "reset cannot command motion", "d", "Category 3 candidate", "IMPLEMENTED AS UNVALIDATED TOPOLOGY", "NO"),
        ("SFR-03", "External-device monitoring", "E3-E7", "restart inhibited after failed opening", "K1/K2 built-in 21-22 mirror-certified NC contacts", "PNOZ S34 monitored feedback loop candidate", "safety-output eligibility", "fault cleared and manual reset", "d", "Category 3 candidate", "IMPLEMENTED AS UNVALIDATED TOPOLOGY", "NO"),
        ("SFR-04", "Control-power loss enters safe state", "E2-E7", "all torque/TX/precharge/action-ready outputs inactive", "supply/reset supervision", "fail-low STM32 initialization plus external chain", "logic outputs and contactor permit", "fresh configuration check and manual reset", "d", "Category 3 target; architecture incomplete", "PARTIAL - HARDWARE/HIL NOT EXECUTED", "NO"),
        ("SFR-05", "Actuator VDD backfeed prevention", "E1-E7", "every non-target branch remains de-energized", "physical split-harness cavities", "physical wiring segregation", "25 individual power pairs", "inspection before remating", "d", "Category 3 target; physical architecture", "DEFINED - UNBUILT", "NO"),
        ("SFR-06", "Branch overcurrent interruption", "E5-E7", "faulted branch isolated without unsafe heating", "branch current/fault", "protection device selection required", "individual branch feed", "inspection and replacement", "N/A", "electrical protection study", "NOT IMPLEMENTED", "NO"),
        ("SFR-07", "Watchdog loss requests safe stop", "E2-E7", "deterministic motion enable removed", "heartbeat", "watchdog/MCU diagnostic path", "permit request only", "manual reset plus fresh command", "NOT ALLOCATED", "diagnostic only", "DEFINED - NO SAFETY CREDIT", "NO"),
        ("SFR-08", "Torque-disable command", "E4-E7", "all actuator torque commands inactive", "controller state", "deterministic firmware", "serial command path", "fresh bounded command after separate authorization", "NOT ALLOCATED", "standard control only", "COMPILED - UNFLASHED", "NO"),
        ("SFR-09", "Charger interlock", "future onboard", "actuator permit absent while charging", "charger-present contact", "hardwired interlock candidate", "safety eligibility", "unplug plus manual reset", "c", "Category 2/3 selection required", "FUTURE - OUT OF SCOPE", "NO"),
        ("SFR-10", "Fall restraint prevents head/floor contact", "S1-S6", "robot arrested within accepted envelope", "mechanical fall", "rated restraint system", "gantry/harness/attachment", "inspection after demand", "N/A", "mechanical protective measure", "NOT SELECTED OR PROVED", "NO"),
        ("SFR-11", "Safety-related speed/travel limiting", "S1-S7", "joint remains within accepted speed/travel envelope", "redundant position/speed evidence", "future safety controller", "independent torque/energy interruption", "manual reset plus investigation", "d", "Category 3 target", "NOT IMPLEMENTED - MOTION PROHIBITED", "NO"),
        ("SFR-12", "Power-loss collapse containment", "S1-S7", "no person contact or head/floor impact", "rail/supply loss", "passive supports/restraint plus future braking", "mechanical capture", "inspection after demand", "d", "mixed mechanical/SRP-CS target", "NOT IMPLEMENTED - MOTION PROHIBITED", "NO"),
    ]
    return [common({
        "function_id": i,
        "safety_function": name,
        "applicable_stage": stage,
        "safe_state": safe,
        "input_subsystem": inp,
        "logic_subsystem": logic,
        "output_subsystem": output,
        "restart_inhibition": restart,
        "candidate_plr": plr,
        "architecture_candidate": category,
        "implementation_state": implementation,
        "achieved_pl_claimed": achieved,
    }) for i, name, stage, safe, inp, logic, output, restart, plr, category, implementation, achieved in data]


def plr_input_rows(functions: list[dict]) -> list[dict]:
    rows = []
    for function in functions:
        rows.append(common({
            "function_id": function["function_id"],
            "candidate_plr": function["candidate_plr"],
            "category": "SELECTION REQUIRED / REVIEW REQUIRED",
            "mttfd_or_b10d_inputs": "SELECTION REQUIRED",
            "annual_operations_nop": "SELECTION REQUIRED",
            "diagnostic_coverage_dcavg": "SELECTION REQUIRED",
            "common_cause_score": "SELECTION REQUIRED",
            "mission_time_years": "SELECTION REQUIRED",
            "software_measures": "SELECTION REQUIRED",
            "excluded_faults": "NONE ACCEPTED",
            "pfhd": "NOT CALCULATED",
            "achieved_pl": "NOT CALCULATED",
            "reviewer_disposition": "NOT REVIEWED",
        }))
    return rows


def ccf_rows() -> list[dict]:
    data = [
        ("CCF-01", "physical separation of E-stop channels and K1/K2 wiring", "routing and terminal inspection", "OPEN"),
        ("CCF-02", "independent series interruption devices", "received order code, DC duty and welded-contact fault tests", "OPEN"),
        ("CCF-03", "separate mirror contacts in EDM", "contact semantics, wiring and injected stuck-contact tests", "OPEN"),
        ("CCF-04", "environmental limits and enclosure", "temperature, contamination, vibration and ingress evidence", "OPEN"),
        ("CCF-05", "supply and coil suppression interactions", "brownout, suppression, release-time and regeneration measurements", "OPEN"),
        ("CCF-06", "software/AI independence from hardwired E-stop", "code, interface and physical write-path review", "PARTIAL"),
        ("CCF-07", "systematic component/data-sheet traceability", "received revisions plus safety characteristic records", "OPEN"),
        ("CCF-08", "maintenance and bypass control", "keying, seals, inspection, configuration and bypass register", "OPEN"),
        ("CCF-09", "fault exclusion discipline", "qualified written justification; none assumed by this package", "OPEN"),
        ("CCF-10", "independent validation", "qualified analyst plus test witness on frozen configuration", "OPEN"),
    ]
    return [common({"ccf_id": i, "control": control, "required_evidence": evidence, "current_state": state}) for i, control, evidence, state in data]


def zero_motion_rows() -> list[dict]:
    data = [
        ("ZMI-01", "E0-E3", "actuator source physically absent or load side de-energized", "physical isolation and voltage measurement", "zero actuator-rail voltage within selected instrument tolerance"),
        ("ZMI-02", "E2-E3", "motor connectors physically absent", "connector census and photographs", "all 25 actuator power inputs disconnected"),
        ("ZMI-03", "E2-E7", "all 25 torque-enable states initialize inactive", "target/HIL readback", "25/25 inactive before and after reset"),
        ("ZMI-04", "E2-E7", "all eight actuator TX paths initialize inactive", "oscilloscope/logic-analyzer measurement", "8/8 no transmit activity until separately authorized"),
        ("ZMI-05", "E2-E7", "precharge request initializes inactive", "GPIO measurement", "inactive through boot, reset and brownout"),
        ("ZMI-06", "E2-E7", "action-ready initializes inactive", "GPIO/state measurement", "inactive until all configuration gates pass"),
        ("ZMI-07", "E2-E7", "OpenAI/conversational process has no direct actuator-bus path", "interface and network rule audit", "only structured high-level requests reach deterministic controller"),
        ("ZMI-08", "E3-E7", "manual safety reset cannot create a motion request", "state-transition/fault-injection test", "eligibility may change; torque/TX/motion remain inactive"),
        ("ZMI-09", "E3-E7", "E-stop release cannot create a motion request", "state-transition/fault-injection test", "no automatic restart"),
        ("ZMI-10", "E3-E7", "permit restoration still requires a fresh bounded motion command", "state-machine/HIL test", "stale or queued commands rejected"),
        ("ZMI-11", "E2-E7", "reset/brownout cannot pulse outputs active", "oscilloscope capture over all supply/reset sequences", "no active pulse within measured bandwidth"),
        ("ZMI-12", "E2-E7", "configuration/hash/identity mismatch is fail-closed", "negative configuration tests", "permit and all motion outputs remain inactive"),
        ("ZMI-13", "E7", "whole robot is mechanically supported and restrained before rail application", "independent mechanical inspection", "restraint carries any gravity motion without person contact"),
        ("ZMI-14", "E7", "no physical joint displacement after rail application", "25-axis encoder plus external witness measurement", "no displacement beyond a predeclared instrument/restraint tolerance; threshold SELECTION REQUIRED"),
        ("ZMI-15", "E0-E7", "motion is outside the first-energization ladder", "traveler and command review", "every motion request rejected; later S1 requires a separate release"),
    ]
    return [common({"invariant_id": i, "stage_scope": stage, "invariant": invariant, "verification_method": method, "acceptance_requirement": acceptance, "physical_result": "NOT EXECUTED"}) for i, stage, invariant, method, acceptance in data]


def timing_rows() -> list[dict]:
    data = [
        ("ST-01", "t_input", "hazard/E-stop actuation to valid safety-input state", "ms", "MEASURED VALUE REQUIRED", "oscilloscope at E-stop and PNOZ inputs"),
        ("ST-02", "t_logic", "safety relay input recognition to output release", "ms", "MANUFACTURER BOUND PLUS MEASURED VALUE REQUIRED", "PNOZ manual and oscilloscope"),
        ("ST-03", "t_output", "safety output release to K1/K2 coil decay", "ms", "MEASURED VALUE REQUIRED", "coil voltage/current trace"),
        ("ST-04", "t_contactor", "coil decay to both main contacts confirmed open", "ms", "MEASURED VALUE REQUIRED", "main/mirror contact trace under representative DC load"),
        ("ST-05", "t_bus", "main contact opening to actuator rail below selected safe-voltage threshold", "ms", "SAFE-VOLTAGE THRESHOLD AND MEASURED VALUE REQUIRED", "rail voltage trace with capacitance/regeneration represented"),
        ("ST-06", "t_torque", "rail/torque-off demand to actuator current below selected residual-torque threshold", "ms", "CURRENT/TORQUE THRESHOLD AND MEASURED VALUE REQUIRED", "phase/supply current plus load-cell/torque evidence"),
        ("ST-07", "t_mechanical", "torque removal to end of coast/overtravel/restraint motion", "ms", "MOTION-STAGE-SPECIFIC VALUE REQUIRED", "encoder, high-speed video and restraint/load evidence"),
        ("ST-08", "T_total", "t_input + t_logic + t_output + t_contactor + t_bus + t_torque + t_mechanical", "ms", "NUMERICAL LIMIT SELECTION REQUIRED BEFORE ANY MOTION", "synchronized trace and uncertainty budget"),
    ]
    return [common({"timing_id": i, "symbol": symbol, "interval": interval, "unit": unit, "allocated_max": "SELECTION REQUIRED", "current_requirement": requirement, "measurement_method": method, "measured_value": "NONE", "uncertainty": "NONE"}) for i, symbol, interval, unit, requirement, method in data]


def stopping_rows() -> list[dict]:
    axes = []
    with (WHOLE / "actuator-transmission-allocation.csv").open(encoding="utf-8", newline="") as handle:
        axes = list(csv.DictReader(handle))
    rows = []
    for axis in axes:
        axis_id = axis.get("axis_id") or axis.get("joint_id") or next(iter(axis.values()))
        rows.append(common({
            "axis_id": axis_id,
            "approach_speed_rad_s": "SELECTION REQUIRED",
            "total_stop_time_ms": "SELECTION REQUIRED",
            "angular_overtravel_formula": "theta_stop = integral(omega(t), 0..T_total)",
            "angular_overtravel_deg": "NOT CALCULATED",
            "endpoint_model": "whole-body forward kinematics plus structural/restraint compliance",
            "endpoint_overtravel_mm": "NOT CALCULATED",
            "fall_or_gravity_term": "REQUIRED FOR LEGS/WAIST/LOAD-BEARING POSES",
            "accepted_limit": "SELECTION REQUIRED BEFORE MOTION",
            "measured_result": "NOT EXECUTED",
        }))
    return rows


def validation_rows() -> list[dict]:
    data = [
        ("SV-01", "SFR-01", "analysis", "trace dual E-stop channels through PNOZ and both contactors", "pin-level as-built drawing and continuity evidence"),
        ("SV-02", "SFR-01", "fault injection", "open each E-stop channel separately and together", "synchronized input/output/main-contact traces"),
        ("SV-03", "SFR-02", "fault injection", "release E-stop without reset and hold/bypass reset", "zero restart and zero motion-output evidence"),
        ("SV-04", "SFR-02", "fault injection", "reset after valid stop with stale queued action present", "stale action rejected; fresh command required"),
        ("SV-05", "SFR-03", "fault injection", "simulate each welded/stuck contactor independently", "other channel opens and EDM blocks restart"),
        ("SV-06", "SFR-04", "hardware test", "power-up, reset, brownout and interrupted boot sweeps", "no active output pulse and deterministic safe state"),
        ("SV-07", "SFR-05", "inspection/test", "verify every outgoing inter-actuator GND/VDD cavity empty", "contact-map inspection plus no-backfeed measurement"),
        ("SV-08", "SFR-06", "electrical test", "representative branch overload and short-circuit tests", "clearing, temperature and adjacent-branch results"),
        ("SV-09", "SFR-07", "fault injection", "remove heartbeat and force watchdog output faults", "measured permit response; independent E-stop still effective"),
        ("SV-10", "SFR-08", "HIL", "read every axis torque state before/after boot/reset/fault", "25/25 inactive; no TX until separately authorized"),
        ("SV-11", "SFR-09", "future fault injection", "charger-present/open/short fault matrix", "permit remains absent; manual restart required"),
        ("SV-12", "SFR-10", "mechanical proof", "static proof and dynamic arrest across declared envelope", "rated system, no head/floor contact, accepted attachment loads"),
        ("SV-13", "SFR-11", "future HIL/physical", "speed, encoder and limit disagreement matrix", "independent interruption inside accepted stopping envelope"),
        ("SV-14", "SFR-12", "future physical", "representative whole-body power-loss poses", "capture without person contact or floor/head impact"),
        ("SV-15", "ALL", "calculation", "ISO 13849 architecture/MTTFd/DCavg/CCF/software calculation", "qualified report on frozen received configuration"),
        ("SV-16", "ALL", "independent review", "validate safety functions and categories under ISO 13849-2", "signed independent analysis and witnessed tests"),
        ("SV-17", "ALL", "timing", "measure every ST-01..ST-08 interval with common clock", "traceable timing and uncertainty budget"),
        ("SV-18", "ALL", "configuration", "repeat tests after any safety-relevant revision", "new hash-bound result set; no inheritance by assumption"),
        ("SV-19", "ALL", "cyber/AI boundary", "attempt direct bus access, replay and stale command injection", "deterministic rejection and no safety-chain bypass"),
        ("SV-20", "ALL", "site acceptance", "verify guards, exclusion zone, E-stop access, restraint and emergency response", "signed site-specific readiness record"),
    ]
    return [common({"validation_id": i, "function_id": function, "method": method, "test_or_analysis": test, "required_evidence": evidence, "result": "NOT EXECUTED", "reviewer": "UNASSIGNED"}) for i, function, method, test, evidence in data]


def hold_rows() -> list[dict]:
    data = [
        ("SRS-H01", "qualified ISO 12100 risk assessment not accepted", "qualified multidisciplinary review of intended use, foreseeable misuse, lifecycle and persons exposed"),
        ("SRS-H02", "candidate PLr allocations are project-owned and unapproved", "qualified selection of PLr and category for every credited function"),
        ("SRS-H03", "achieved PL/PFHd not calculated", "received component safety data, nop, MTTFd/B10d, DCavg, CCF, mission time and software measures"),
        ("SRS-H04", "common-cause measures unverified", "as-built separation, environment, supply, wiring, maintenance and fault-injection evidence"),
        ("SRS-H05", "stopping-time intervals and total are unmeasured", "synchronized ST-01 through ST-08 traces with uncertainty"),
        ("SRS-H06", "joint and endpoint stopping distances are unallocated", "stage-specific speed, inertia, torque decay, compliance, gravity, restraint and overtravel measurements"),
        ("SRS-H07", "PNOZ/contactors and DC opening duty are unvalidated as a system", "received LC1D40ABD identity/terminal inspection, frozen as-built circuit, HR-30 fault current and L/R, DC-load life/duty, suppression, timing and welded-contact tests"),
        ("SRS-H08", "whole-body fall restraint has no rated design or proof", "WLL, dynamic arrest, attachment load path, inspection and qualified mechanical acceptance"),
        ("SRS-H09", "safety-related speed/travel monitoring is absent", "independent architecture and validation before S1-S7 motion"),
        ("SRS-H10", "public and child interaction safety is outside P0.1", "new intended-use risk assessment under the then-current service-robot standard and physical validation"),
        ("SRS-H11", "electrical protection and protective bonding remain open", "fault current, coordination, conductor/contact thermal evidence, PE/0 V approval and measurements"),
        ("SRS-H12", "no physical safety test or qualified validation has executed", "complete SV-01 through SV-20 evidence on one frozen as-built robot/site configuration"),
    ]
    return [common({"hold_id": i, "open_item": item, "closure_evidence": evidence, "state": "OPEN"}) for i, item, evidence in data]


def diagram() -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="920" viewBox="0 0 1600 920" role="img" aria-labelledby="t d"><title id="t">HR-30 safety requirements architecture</title><desc id="d">Hardwired emergency stop and contactors remain independent of the standard motion controller and conversational agent.</desc><style>text{{font-family:system-ui,Segoe UI,sans-serif;fill:#142a40}}.h{{font-size:34px;font-weight:900}}.b{{font-size:20px;font-weight:800}}.s{{font-size:16px}}.box{{fill:#fff;stroke:#0b4f91;stroke-width:4}}.safe{{fill:#fff3bd;stroke:#8a6200;stroke-width:5}}.open{{fill:#ffe6e3;stroke:#982520;stroke-width:4}}.line{{fill:none;stroke:#0b4f91;stroke-width:7}}.hard{{fill:none;stroke:#982520;stroke-width:9}}</style><rect width="1600" height="920" fill="#f7fbff"/><rect x="35" y="25" width="1530" height="92" rx="14" fill="#f2b91d" stroke="#805600" stroke-width="3"/><text x="65" y="65" class="b">PRELIMINARY - SAFETY REQUIREMENTS CANDIDATE ONLY - NO VALIDATED PL OR WORK AUTHORITY</text><text x="65" y="96" class="s">E-stop/reset may restore eligibility only; neither may command motion.</text><text x="55" y="170" class="h">Independent stop path</text><rect x="55" y="205" width="260" height="150" rx="18" class="safe"/><text x="85" y="250" class="b">Dual E-stop</text><text x="85" y="285" class="s">two direct-opening channels</text><text x="85" y="318" class="s">manual reset is separate</text><rect x="435" y="205" width="280" height="150" rx="18" class="safe"/><text x="465" y="250" class="b">PNOZ s4 candidate</text><text x="465" y="285" class="s">monitored start + EDM</text><text x="465" y="318" class="s">candidate PLr d / Cat 3</text><rect x="835" y="205" width="280" height="150" rx="18" class="safe"/><text x="865" y="250" class="b">K1 + K2 series</text><text x="865" y="285" class="s">mirror contacts to EDM</text><text x="865" y="318" class="s">DC duty/test remains open</text><rect x="1235" y="205" width="300" height="150" rx="18" class="safe"/><text x="1265" y="250" class="b">25 actuator feeds</text><text x="1265" y="285" class="s">safe state: source removed</text><text x="1265" y="318" class="s">torque/current decay unmeasured</text><path d="M315 280 H435 M715 280 H835 M1115 280 H1235" class="hard"/><text x="55" y="455" class="h">Standard control path - no safety credit</text><rect x="55" y="490" width="300" height="150" rx="18" class="box"/><text x="85" y="535" class="b">OpenAI agent</text><text x="85" y="570" class="s">structured requests only</text><text x="85" y="603" class="s">no direct actuator bus</text><rect x="475" y="490" width="320" height="150" rx="18" class="box"/><text x="505" y="535" class="b">Deterministic controller</text><text x="505" y="570" class="s">25 torque bits / 8 TX paths</text><text x="505" y="603" class="s">first-power state inactive</text><rect x="915" y="490" width="300" height="150" rx="18" class="box"/><text x="945" y="535" class="b">Watchdog request</text><text x="945" y="570" class="s">diagnostic stop request</text><text x="945" y="603" class="s">cannot bypass E-stop</text><rect x="1335" y="490" width="200" height="150" rx="18" class="box"/><text x="1365" y="535" class="b">Actuators</text><text x="1365" y="570" class="s">not safety-rated</text><text x="1365" y="603" class="s">motion prohibited</text><path d="M355 565 H475 M795 565 H915 M1215 565 H1335" class="line"/><rect x="120" y="730" width="1360" height="125" rx="18" class="open"/><text x="150" y="775" class="b">Still open: achieved PL/PFHd, CCF, exact stopping time/distance, DC contactor duty, restraint proof and physical validation</text><text x="150" y="815" class="s">A qualified reviewer must accept one frozen as-built configuration before connection, powered testing, motion or energization.</text></svg>'''


def srs_markdown(hazards: list[dict], functions: list[dict]) -> str:
    return f'''# HR-30 whole-body Safety Requirements Specification P0.1

**{WARNING}**

## Purpose and boundary

This candidate SRS covers the 762 mm, 25-axis HR-30 whole-body P0.1 through unpowered assembly and the E0-E7 first-energization ladder. Motion stages S1-S7 and public/child interaction are explicitly outside this release. The document provides reviewable requirements; it does not establish conformity, an achieved performance level, or permission to work on hardware.

## Intended use for this revision

- laboratory engineering prototype on a level, guarded site in Boston, Massachusetts;
- trained adults only inside the controlled test process;
- tether-first power architecture with the robot mechanically supported and restrained;
- E0-E7 power states only, with every motion request rejected;
- no lifting or carrying people, no public operation, and no child access;
- no onboard battery or charging during first energization.

## Normative-method candidate

ISO 12100:2010 is the risk-assessment framework candidate. ISO 13849-1:2023 is the SRP/CS design method candidate and does not itself choose the PLr for this robot. ISO 13849-2:2012 is the validation-method candidate. ISO 13850:2015 and IEC 60204-1:2016+AMD1:2021 inform the emergency-stop/electrical boundary. ISO 13482:2014 and its application/test reports are informative service-robot references; the standard is under revision and no conformity claim is made.

## Safety strategy

1. Eliminate motion from first energization: torque, bus transmit, precharge and action-ready outputs remain inactive.
2. Keep people out of the motion/fall envelope and support the complete robot mechanically.
3. Use a hardwired dual-channel emergency-stop and two monitored series interruption devices independently of the AI and standard motion controller.
4. Make reset restore eligibility only; require a fresh, bounded motion command in a later separately released state.
5. Treat the watchdog, actuator firmware, torque-disable commands and conversational layer as standard control with zero safety credit until separately validated.
6. Measure the complete stopping chain before allocating any motion envelope or safeguard distance.

## Candidate allocations

This package contains **{len(hazards)} open hazards** and **{len(functions)} safety/control functions**. PLr d / Category 3 is a conservative project candidate for the credited E-stop, restart-inhibition, EDM and fail-safe control-power boundaries. It is not approved: MTTFd/B10d, DCavg, CCF, mission time, PFHd, systematic capability, exact category, and independent validation are blank.

## Restart invariant

E-stop release, manual reset, restored power, restored communications, watchdog recovery, or controller reboot shall never create a motion request. They may only restore eligibility. Any later motion requires a fresh request accepted by the deterministic local controller after a separately authorized motion-stage gate.

## Stopping requirement

The total stop time is `T_total = t_input + t_logic + t_output + t_contactor + t_bus + t_torque + t_mechanical`. Every term must be measured with a common time base on the received configuration. Angular and Cartesian overtravel must be computed from measured velocity histories and whole-body kinematics, including gravity, compliance, restraint and fall behavior. No single arbitrary multiplier or component response time may stand in for the system measurement.

## Acceptance boundary

All rows remain NOT VALIDATED. A qualified functional-safety reviewer, electrical reviewer, mechanical reviewer, controls/test lead and configuration owner must accept the same hash-bound as-built configuration and witnessed evidence. Until then, connection, powered testing, motion and energization remain prohibited.
'''


def render(hazards: list[dict], functions: list[dict], timings: list[dict], holds: list[dict]) -> str:
    fn_rows = "".join(f"<tr><td>{html.escape(r['function_id'])}</td><td>{html.escape(r['safety_function'])}</td><td>{html.escape(r['candidate_plr'])}</td><td>{html.escape(r['implementation_state'])}</td><td>{html.escape(r['achieved_pl_claimed'])}</td></tr>" for r in functions)
    time_rows = "".join(f"<tr><td>{html.escape(r['symbol'])}</td><td>{html.escape(r['interval'])}</td><td>{html.escape(r['allocated_max'])}</td><td>{html.escape(r['measured_value'])}</td></tr>" for r in timings)
    hold_cards = "".join(f"<article><h3>{html.escape(r['hold_id'])}</h3><p>{html.escape(r['open_item'])}</p><strong>OPEN</strong></article>" for r in holds)
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 whole-body safety requirements</title><style>:root{{--deep:#071d36;--blue:#0b4f91;--sky:#d9f2ff;--gold:#f2b91d;--paper:#f7fbff;--ink:#142a40;--line:#82c4e6;--red:#982520}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.55 system-ui,Segoe UI,sans-serif}}header,main,footer{{padding:clamp(24px,5vw,64px) max(18px,calc((100vw - 1280px)/2))}}header,footer{{background:linear-gradient(135deg,var(--deep),var(--blue));color:white}}h1{{font-size:clamp(38px,6vw,70px);line-height:1.04;max-width:18ch}}h2{{font-size:clamp(28px,4vw,44px)}}h3{{font-size:21px}}.warning{{background:var(--gold);color:#17243a;border:3px solid #805600;padding:16px;font-weight:900}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:18px}}article,.panel{{background:white;border:2px solid var(--line);border-radius:16px;padding:19px}}article strong{{color:var(--red)}}.metric{{font-size:clamp(34px,5vw,54px);font-weight:900;color:var(--blue)}}.scroll{{overflow:auto;border:2px solid var(--line);border-radius:16px;background:white}}table{{border-collapse:collapse;width:100%;min-width:900px}}th,td{{font-size:16px;line-height:1.45;text-align:left;vertical-align:top;padding:14px;border-bottom:1px solid var(--line)}}th{{background:var(--deep);color:white;position:sticky;top:0}}img{{display:block;width:100%;height:auto;border:2px solid var(--line);border-radius:16px}}a{{color:#075b9b;font-weight:800}}small{{font-size:14px}}@media(max-width:560px){{body{{font-size:16px}}}}</style></head><body><header><div class="warning">{html.escape(WARNING)}</div><p>Project Button · HR-30 whole-body P0.1</p><h1>Define the safe state before applying power.</h1><p>The existing stop hardware, no-motion firmware, restraint boundary and first-power ladder now have one traceable candidate SRS. Every achieved-performance and physical-result field is still open.</p></header><main><section class="grid"><article><div class="metric">{len(hazards)}</div><p>whole-robot hazards; none accepted</p></article><article><div class="metric">{len(functions)}</div><p>safety/control function records</p></article><article><div class="metric">{len(timings)}</div><p>stopping-time intervals to measure</p></article><article><div class="metric">0</div><p>achieved PL claims or executed validations</p></article></section><section><h2>Architecture boundary</h2><img src="safety-architecture.svg" alt="Hardwired HR-30 emergency-stop path separated from standard controller and AI request path"></section><section><h2>Candidate safety functions</h2><div class="scroll"><table><thead><tr><th>ID</th><th>Function</th><th>Candidate PLr</th><th>Implementation</th><th>Achieved PL</th></tr></thead><tbody>{fn_rows}</tbody></table></div></section><section><h2>System stopping-time model</h2><div class="panel"><p><code>T_total = t_input + t_logic + t_output + t_contactor + t_bus + t_torque + t_mechanical</code></p><p>No numerical stopping limit or distance is released. Every interval, joint velocity, gravity/fall contribution and uncertainty must be measured before any motion stage.</p></div><div class="scroll"><table><thead><tr><th>Term</th><th>Interval</th><th>Allocation</th><th>Result</th></tr></thead><tbody>{time_rows}</tbody></table></div></section><section><h2>Open safety holds</h2><div class="grid">{hold_cards}</div></section><section class="panel"><h2>Controlled records</h2><p><a href="HR30-SRS-P0.1.md">SRS</a> · <a href="hazard-register.csv">hazards</a> · <a href="safety-function-register.csv">functions</a> · <a href="plr-calculation-input-register.csv">PL inputs</a> · <a href="common-cause-control-register.csv">CCF</a> · <a href="zero-motion-invariant-register.csv">zero-motion invariants</a> · <a href="stopping-time-budget.csv">timing</a> · <a href="stopping-distance-register.csv">25 axes</a> · <a href="validation-plan.csv">validation</a> · <a href="open-holds.csv">holds</a> · <a href="source-register.csv">sources</a></p><small>External standards are referenced by official publication pages and access date. Their copyrighted full text is not reproduced.</small></section></main><footer>{html.escape(WARNING)}</footer></body></html>'''


def integrate_root(hazards: list[dict], functions: list[dict], timings: list[dict], validations: list[dict]) -> None:
    status_path = WHOLE / "package-status.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    status.update({
        "whole_body_srs_candidate_present": True,
        "whole_body_hazard_count": len(hazards),
        "whole_body_safety_function_count": len(functions),
        "whole_body_stopping_time_interval_count": len(timings),
        "whole_body_safety_validation_case_count": len(validations),
        "candidate_plr_allocation_present": True,
        "candidate_plr_approved": False,
        "achieved_performance_level_calculated": False,
        "stopping_time_measured": False,
        "stopping_distance_allocated": False,
        "functional_safety_validated": False,
        "connection_authority": False,
        "powered_test_authority": False,
        "motion_authority": False,
        "energization_authority": False,
    })
    status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")

    readme = WHOLE / "README.md"
    text = readme.read_text(encoding="utf-8")
    start, end = "<!-- HR30-SRS-P01-README-START -->", "<!-- HR30-SRS-P01-README-END -->"
    if start in text and end in text:
        text = text.split(start, 1)[0] + text.split(end, 1)[1]
    block = f'''{start}\n## Whole-body safety requirements P0.1\n\nThe [interactive safety-requirements guide](safety-requirements-p0.1/index.html) converts the existing whole-robot stop topology, first-power firmware and restraint boundary into {len(hazards)} open hazards, {len(functions)} safety/control functions, a candidate PLr allocation, {len(timings)} explicit stopping-time intervals and {len(validations)} validation cases. Achieved PL/PFHd, common-cause evidence, numerical stopping limits, physical results and qualified approval remain open. It is a reviewable SRS candidate, not permission to connect, power or move the robot.\n{end}\n'''
    marker = "<!-- HR30-FIRST-ENERGIZATION-P01-README-START -->"
    if marker in text:
        text = text.replace(marker, block + marker)
    else:
        # A clean dependency-ordered build creates the SRS before the
        # first-energization package.  Append now; the later generator will
        # add its own controlled block without requiring stale prior output.
        text = text.rstrip() + "\n\n" + block
    readme.write_text(text, encoding="utf-8", newline="\n")

    page = WHOLE / "index.html"
    text = page.read_text(encoding="utf-8")
    start, end = "<!-- HR30-SRS-P01-START -->", "<!-- HR30-SRS-P01-END -->"
    if start in text and end in text:
        text = text.split(start, 1)[0] + text.split(end, 1)[1]
    section = f'''{start}<section id="safety-requirements"><h2>The whole robot now has a candidate SRS</h2><div class="grid"><article class="card"><div class="metric">{len(hazards)}</div><p>open whole-robot hazards</p></article><article class="card"><div class="metric">{len(functions)}</div><p>safety/control function records</p></article><article class="card"><div class="metric">{len(timings)}</div><p>stopping-time intervals to measure</p></article><article class="card hold"><div class="metric">0</div><p>validated PL claims or physical safety tests</p></article></div><p><a href="safety-requirements-p0.1/index.html">Open the interactive whole-body SRS</a>. Candidate PLr d / Category 3 allocations remain unapproved; motion and energization remain prohibited.</p></section>{end}'''
    marker = "<!-- HR30-FIRST-ENERGIZATION-P01-START -->"
    if marker in text:
        text = text.replace(marker, section + marker)
    elif "</main>" in text:
        text = text.replace("</main>", section + "</main>", 1)
    else:
        raise RuntimeError("root page main boundary missing")
    page.write_text(text, encoding="utf-8", newline="\n")


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    sources = source_rows()
    lifecycle = lifecycle_rows()
    hazards = hazard_rows()
    functions = function_rows()
    plr = plr_input_rows(functions)
    ccf = ccf_rows()
    zero_motion = zero_motion_rows()
    timings = timing_rows()
    stopping = stopping_rows()
    validations = validation_rows()
    holds = hold_rows()
    write_csv(OUT / "source-register.csv", sources)
    write_csv(OUT / "lifecycle-mode-register.csv", lifecycle)
    write_csv(OUT / "hazard-register.csv", hazards)
    write_csv(OUT / "safety-function-register.csv", functions)
    write_csv(OUT / "plr-calculation-input-register.csv", plr)
    write_csv(OUT / "common-cause-control-register.csv", ccf)
    write_csv(OUT / "zero-motion-invariant-register.csv", zero_motion)
    write_csv(OUT / "stopping-time-budget.csv", timings)
    write_csv(OUT / "stopping-distance-register.csv", stopping)
    write_csv(OUT / "validation-plan.csv", validations)
    write_csv(OUT / "open-holds.csv", holds)
    (OUT / "HR30-SRS-P0.1.md").write_text(srs_markdown(hazards, functions), encoding="utf-8", newline="\n")
    (OUT / "safety-architecture.svg").write_text(diagram(), encoding="utf-8", newline="\n")
    (OUT / "index.html").write_text(render(hazards, functions, timings, holds), encoding="utf-8", newline="\n")
    status = {
        "identifier": IDENTIFIER,
        "warning": WARNING,
        "official_source_count": sum(r["source_type"] == "OFFICIAL EXTERNAL" for r in sources),
        "local_source_count": sum(r["source_type"] == "LOCAL CONFIGURATION" for r in sources),
        "lifecycle_mode_count": len(lifecycle),
        "hazard_count": len(hazards),
        "accepted_residual_risk_count": 0,
        "safety_function_count": len(functions),
        "candidate_plr_d_function_count": sum(r["candidate_plr"] == "d" for r in functions),
        "achieved_pl_claim_count": 0,
        "plr_calculation_input_count": len(plr),
        "ccf_control_count": len(ccf),
        "zero_motion_invariant_count": len(zero_motion),
        "stopping_time_interval_count": len(timings),
        "stopping_distance_axis_count": len(stopping),
        "validation_case_count": len(validations),
        "executed_validation_count": 0,
        "open_hold_count": len(holds),
        "candidate_plr_allocation_present": True,
        "candidate_plr_approved": False,
        "achieved_performance_level_calculated": False,
        "stopping_time_model_present": True,
        "stopping_time_measured": False,
        "stopping_distance_allocated": False,
        "functional_safety_validated": False,
        "qualified_review_complete": False,
        "connection_authority": False,
        "powered_test_authority": False,
        "motion_authority": False,
        "energization_authority": False,
    }
    (OUT / "srs-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    (OUT / "README.md").write_text(f"# HR-30 whole-body safety requirements P0.1\n\n**{WARNING}**\n\nThis package is the candidate SRS for the complete HR-30 P0.1 through the E0-E7 zero-motion first-energization ladder. It records no achieved PL, accepted risk, physical test, qualified approval or work authority. Open [index.html](index.html) for the readable guide.\n", encoding="utf-8", newline="\n")
    shutil.copy2(Path(__file__), OUT / "safety-requirements-source.py")
    manifest = [{"path": p.relative_to(OUT).as_posix(), "bytes": p.stat().st_size, "sha256": sha(p), "warning": WARNING} for p in sorted(OUT.rglob("*")) if p.is_file() and p.name != "file-manifest.csv"]
    write_csv(OUT / "file-manifest.csv", manifest)
    if RELEASE.exists():
        shutil.rmtree(RELEASE)
    shutil.copytree(OUT, RELEASE)
    integrate_root(hazards, functions, timings, validations)
    import generate_hr30_system_package_p01 as system_package
    system_package.refresh_manifest_and_release()
    print(json.dumps(status, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
