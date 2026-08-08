"""Generate the configuration-bound HR-V0 watchdog dependent-failure package."""

from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "safety" / "hr-v0-watchdog-ccf-p0.1"
CANONICAL_FMEA = ROOT / "safety" / "hr-v0-watchdog-boundary-fmea.csv"
RESULT_FORM = ROOT / "tests" / "forms" / "hr-v0-watchdog-fault-injection-template.csv"
INSPECTION_FORM = ROOT / "tests" / "forms" / "hr-v0-watchdog-separation-inspection-template.csv"
REVISION = "HR-V0-WD-CCF-P0.1"
CONFIGURATION = "Electrical V3-P1.12 / PCB-P0.5 / HR-V0-CP-P0.4"
WARNING = "PRELIMINARY - ANALYSIS AND UNEXECUTED TEST CONTROL ONLY - NOT APPROVED FOR FABRICATION OR ENERGIZATION"


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty CSV: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


PATHS = [
    ("WDP-001", "SF-01 channel 1", "02_estop_eligibility.kicad_sch", "SR1:S11 -> SR1_S11 -> S0:R-1/R-2 NC -> WD1_SAFETY_IN -> KWD1:11/14 NO -> SR1_S12 -> SR1:S12", "credited candidate input path; KWD1 contribution unresolved"),
    ("WDP-002", "SF-01 channel 2", "02_estop_eligibility.kicad_sch", "SR1:S21 -> SR1_S21 -> S0:L-1/L-2 NC -> WD2_SAFETY_IN -> KWD2:11/14 NO -> SR1_S22 -> SR1:S22", "credited candidate input path; KWD2 contribution unresolved"),
    ("WDP-003", "SR1 monitored reset", "02_estop_eligibility.kicad_sch", "SR1:S12 -> SR1_S12 -> S1:TBD-R1/TBD-R2 -> SR1_START_RETURN -> SR1:S34", "received RESET terminal map and qualified start-mode validation open"),
    ("WDP-004", "SR1 output to SRA1 channel 1", "02_estop_eligibility.kicad_sch;03_arm_watchdog_eligibility.kicad_sch", "SR1:13/14 -> SRA1_S11/SRA1_S12 -> SRA1:S11/S12", "direct safety-output candidate; application validation open"),
    ("WDP-005", "SR1 output to SRA1 channel 2", "02_estop_eligibility.kicad_sch;03_arm_watchdog_eligibility.kicad_sch", "SR1:23/24 -> SRA1_S21/SRA1_S22 -> SRA1:S21/S22", "direct safety-output candidate; application validation open"),
    ("WDP-006", "SRA1 ARM and EDM", "03_arm_watchdog_eligibility.kicad_sch;04_contactor_edm.kicad_sch", "SRA1:S12 -> SRA1_S12 -> S2:TBD-A1/TBD-A2 -> ARM_AFTER_S2 -> K1:21/22 NC -> EDM_K1_TO_K2 -> K2:21/22 NC -> SRA1_START_RETURN -> SRA1:S34", "received ARM and mirror-contact application evidence open"),
    ("WDP-007", "K1 coil command", "03_arm_watchdog_eligibility.kicad_sch;04_contactor_edm.kicad_sch", "SRA1:13/14 -> SRA1_K1_RAW -> FSR1:1/2 -> K1_A1 -> K1:A1; K1:A2 -> SAFETY_0V", "fuse link, conductor, contactor application and physical test open"),
    ("WDP-008", "K2 coil command", "03_arm_watchdog_eligibility.kicad_sch;04_contactor_edm.kicad_sch", "SRA1:23/24 -> SRA1_K2_RAW -> FSR2:1/2 -> K2_A1 -> K2:A1; K2:A2 -> SAFETY_0V", "fuse link, conductor, contactor application and physical test open"),
    ("WDP-009", "compute heartbeat", "07_watchdog_control.kicad_sch;09_compute_and_control_terminals.kicad_sch;11_watchdog_pcb_connectors.kicad_sch", "PI1:HDR40-11 -> PI_HEARTBEAT -> JWH1:1 -> RHB1 -> ISO1 LED; PI1:HDR40-06 -> COMPUTE_0V -> JWH1:2", "ordinary diagnostic; cable/runtime/waveform evidence open"),
    ("WDP-010", "isolated heartbeat receiver", "07_watchdog_control.kicad_sch", "ISO1:4 -> WD_HEARTBEAT -> WDCTRL1:4 with RHP1 pull-up to WD_3V3", "ordinary diagnostic; optocoupler failure is assumed"),
    ("WDP-011", "watchdog channel 1 drive", "07_watchdog_control.kicad_sch;11_watchdog_pcb_connectors.kicad_sch", "WDCTRL1:5 -> WD1_DRIVE -> UDRV1:1/16 -> WD1_COIL_N -> JWP1:3 -> KWD1:A2; KWD1:A1 -> SAFETY_24V", "ordinary diagnostic; shared controller and rails"),
    ("WDP-012", "watchdog channel 2 drive", "07_watchdog_control.kicad_sch;11_watchdog_pcb_connectors.kicad_sch", "WDCTRL1:6 -> WD2_DRIVE -> UDRV2:1/16 -> WD2_COIL_N -> JWP1:4 -> KWD2:A2; KWD2:A1 -> SAFETY_24V", "ordinary diagnostic; shared controller and rails"),
    ("WDP-013", "KWD1 feedback", "03_arm_watchdog_eligibility.kicad_sch;08_watchdog_feedback_interface.kicad_sch;11_watchdog_pcb_connectors.kicad_sch", "SAFETY_24V -> KWD1:21/22 NC -> WD1_NC_24V -> JWF1:1 -> UFB1 channel 1 -> WD1_NC_DIAG -> WDCTRL1:9", "read-only intent; internal/panel cross-fault consequence unresolved"),
    ("WDP-014", "KWD2 feedback", "03_arm_watchdog_eligibility.kicad_sch;08_watchdog_feedback_interface.kicad_sch;11_watchdog_pcb_connectors.kicad_sch", "SAFETY_24V -> KWD2:21/22 NC -> WD2_NC_24V -> JWF1:2 -> UFB1 channel 2 -> WD2_NC_DIAG -> WDCTRL1:10", "read-only intent; internal/panel cross-fault consequence unresolved"),
    ("WDP-015", "watchdog PCB power", "01_external_sources.kicad_sch;07_watchdog_control.kicad_sch;11_watchdog_pcb_connectors.kicad_sch", "F24:OUT -> SAFETY_24V -> JWP1:1/DC1:1; SAFETY_0V -> JWP1:2/DC1:2; DC1:3 -> WD_5V -> WDCTRL1:39", "shared ordinary/safety source boundary; F24 and brownout behavior open"),
    ("WDP-016", "watchdog debug", "07_watchdog_control.kicad_sch;12_watchdog_pcb_test_access.kicad_sch", "TP15 WD_SWDIO -> WDCTRL1:D3; TP16 WD_SWCLK -> WDCTRL1:D1; TP2 SAFETY_0V -> WDCTRL1:D2", "unpowered fixture only; no-back-power proof open"),
    ("WDP-017", "PCB test access", "12_watchdog_pcb_test_access.kicad_sch", "TP1..TP16 expose power, heartbeat, drive, coil, feedback and debug nets", "probe adjacency, retention and short-fixture controls open"),
    ("WDP-018", "panel physical allocation", "electrical/panel/hr-v0-control-panel-p0.4/backplate-layout.csv", "SR1 BP-005; SRA1 BP-006; KWD1 BP-007; KWD2 BP-008; WDPCB1 BP-012", "nominal envelopes only; no released routing, barriers, conductors or enclosure build"),
]
PATH_ROWS = [{"path_id": a, "function_or_boundary": b, "controlled_sheet_or_file": c, "exact_path": d, "current_disposition": e, "safety_credit": "ZERO FOR DF-01; SF-01/SF-03 QUALIFIED ALLOCATION REQUIRED", "warning": WARNING} for a, b, c, d, e in PATHS]


FAILURES = [
    ("WDF-001", "PI heartbeat source", "stops toggling", "DF-01 should time out; physical timing open", "none if independent paths remain intact", "FI-001"),
    ("WDF-002", "PI heartbeat source", "stuck-valid or plausible erroneous toggling", "DF-01 can fail to demand stop", "none by claim; containment assumes this failure", "FI-002;FI-003"),
    ("WDF-003", "WDCTRL1 RP2040/firmware/clock", "both outputs commanded or stuck energized", "both KWD relays can remain picked", "E-stop and restart paths must remain effective", "FI-004"),
    ("WDF-004", "UDRV1 or WD1_DRIVE", "shorted on", "KWD1 can remain picked", "channel-1 E-stop path must still open; exact fault influence open", "FI-005"),
    ("WDF-005", "KWD1 contact 11-14", "welded/shorted closed", "DF-01 channel 1 lost", "S0 channel 1 must still command SR1 dropout", "FI-006;FI-019"),
    ("WDF-006", "KWD1 and KWD2 contacts 11-14", "both welded/bypassed", "DF-01 completely lost", "both S0 channels and restart prevention must remain effective", "FI-007;FI-020"),
    ("WDF-007", "KWD coil or conductor", "open", "nuisance diagnostic stop expected", "restart must remain inhibited after recovery", "FI-008"),
    ("WDF-008", "SR1 input return harness", "short bypasses S0 contact or bridges input path", "not a diagnostic-credit issue", "SF-01/SF-03 can be impaired; protected-routing decision required", "FI-021;FI-022"),
    ("WDF-009", "SAFETY_24V", "loss/brownout/recovery", "DF-01 unavailable; relay chatter possible", "dropout/recovery and no automatic restart must be proved", "FI-009;FI-010"),
    ("WDF-010", "UFB1 feedback", "false healthy/fault", "diagnostic indication lost", "must have no coil, RESET or ARM authority", "FI-011;FI-012"),
    ("WDF-011", "PCB/panel contamination", "cross-net leakage or conductive bridge", "unbounded ordinary behavior", "SF-01/SF-03 impairment possible; cleanliness/separation unresolved", "FI-023"),
    ("WDF-012", "KWD1 internal boundary", "A1 SAFETY_24V short to terminal 14/SR1_S12", "can inject voltage downstream of S0 channel 1", "potential single-channel SF-01 impairment; qualified circuit analysis required", "FI-024"),
    ("WDF-013", "KWD2 internal boundary", "A1 SAFETY_24V short to terminal 14/SR1_S22", "can inject voltage downstream of S0 channel 2", "potential single-channel SF-01 impairment; qualified circuit analysis required", "FI-025"),
    ("WDF-014", "KWD1 pole-to-pole boundary", "terminal 21 SAFETY_24V short to terminal 14", "feedback supply can reach SR1_S12", "potential channel-1 bypass; exact relay fault model open", "FI-024"),
    ("WDF-015", "KWD2 pole-to-pole boundary", "terminal 21 SAFETY_24V short to terminal 14", "feedback supply can reach SR1_S22", "potential channel-2 bypass; exact relay fault model open", "FI-025"),
    ("WDF-016", "adjacent KWD modules/panel wiring", "common bridge from SAFETY_24V to both 14 returns", "both SR1 returns may be forced", "potential two-channel SF-01 defeat; redesign or accepted exclusion required", "FI-026"),
    ("WDF-017", "JWP1", "pin 1 SAFETY_24V short to pin 3 or 4 coil sink", "one/both KWD relays may energize", "DF-01 lost; E-stop independence still must be proved", "FI-013"),
    ("WDF-018", "JWP1", "pin 3-to-4 bridge", "channels become coupled", "common-cause diagnostic loss; no safety credit", "FI-014"),
    ("WDF-019", "JWF1", "pin 1-to-2 bridge", "feedback channels become coupled", "must not affect E-stop, RESET or ARM authority", "FI-015"),
    ("WDF-020", "JWF1/PCB", "WDx_NC_24V short to SAFETY_0V", "branch fault/current and false indication", "F24/protection response and no safety-path damage open", "FI-016"),
    ("WDF-021", "ISO1", "LED/transistor short or loss of isolation", "heartbeat can be stuck or compute/safety returns coupled", "no credited path may depend on isolation; return coupling consequence open", "FI-017"),
    ("WDF-022", "DC1", "input-output short", "24 V may reach WD_5V/WDCTRL1", "ordinary PCB damage must not propagate into credited wiring", "FI-018"),
    ("WDF-023", "DC1/WD rails", "slow brownout or oscillatory restart", "spurious drive pulses possible", "no K1/K2 restoration without RESET then ARM", "FI-010;FI-027"),
    ("WDF-024", "TP15/TP16/TP2 debug fixture", "back-power or driven pin during source-off state", "WDCTRL1 can execute or drive outputs unexpectedly", "must not create contactor authority; unpowered fixture proof open", "FI-028"),
    ("WDF-025", "TP1..TP16 probe access", "adjacent or dropped-probe short", "multiple ordinary nets can be bridged", "fixture shall make hazardous bridges inaccessible or current-limited", "FI-023"),
    ("WDF-026", "shared enclosure", "moisture/metal swarf/loose strand", "cross-channel and safety/ordinary bridges possible", "environment and workmanship controls required; no fault exclusion accepted", "FI-023;FI-026"),
    ("WDF-027", "shared SAFETY_0V", "open/high impedance", "controllers/drivers/relays may chatter or float", "safe dropout and restart inhibition require physical proof", "FI-009;FI-027"),
    ("WDF-028", "KWD1/KWD2 replacement/service", "wrong module, polarity or terminal map", "contact/coil behavior may differ", "received identity and point-to-point verification mandatory", "FI-019;FI-020"),
    ("WDF-029", "unused KWD terminals 12/24", "field wiring or conductive contact added", "alternate contact paths introduced", "must remain isolated and inspected", "FI-021"),
    ("WDF-030", "RESET/ARM conductor proximity", "watchdog conductor bridges S1/S2/EDM return", "restart sequence can be corrupted", "SF-03 impairment possible; routing/barriers/fault injection open", "FI-022;FI-026"),
    ("WDF-031", "software feedback handling", "feedback falsely used as permission", "ordinary indication could gain motion authority", "code/config review must prove feedback is read-only", "FI-011;FI-012"),
    ("WDF-032", "configuration mismatch", "KiCad, panel, harness, PCB or firmware revisions mixed", "fault analysis no longer matches article", "authorization automatically revoked; exact manifest inspection required", "FI-019;FI-020"),
]
FAILURE_ROWS = [{"fmea_id": a, "item_or_boundary": b, "failure_mode": c, "df01_effect": d, "sf01_sf03_effect": e, "required_verification": f, "safe_by_design": "NO - OPEN UNTIL ANALYSIS/TEST" if a not in {"WDF-001", "WDF-007"} else "CONDITIONAL - PHYSICAL PROOF REQUIRED", "status": "OPEN", "warning": WARNING} for a, b, c, d, e, f in FAILURES]
CANONICAL_FAILURE_ROWS = [{"fmea_id": a, "item_or_boundary": b, "failure_mode": c, "local_effect": d, "df01_effect": d, "sf01_effect": e, "sf03_effect": e, "safe_by_design": "conditional" if a in {"WDF-001", "WDF-007"} else "no", "required_control": "Configuration-bound analysis, redesign or accepted fault control; no safety credit to diagnostic success", "verification": f, "status": "open"} for a, b, c, d, e, f in FAILURES]


CCF = [
    ("CCF-001", "WDCTRL1 firmware/clock/reset", "both drive channels", "shared controller can sustain both outputs", "assume both diagnostic channels failed; zero credit"),
    ("CCF-002", "SAFETY_24V/SAFETY_0V", "KWD coils, drivers, feedback, SR1/SRA1", "shared rails couple ordinary and credited boundaries", "brownout/fault study plus qualified allocation"),
    ("CCF-003", "DC1 WD_5V/WD_3V3", "controller, optocoupler receiver, drivers", "rail fault can create correlated outputs", "fault injection and no-back-power validation"),
    ("CCF-004", "PCB-P0.5", "both drivers and feedback channels", "same two-layer board, contamination and assembly process", "layout/workmanship/cleanliness review; no fault exclusion yet"),
    ("CCF-005", "JWP1 four-position connector", "power and both coil sinks", "adjacent pins and one removable body", "keying, ferrules, strain relief, short test and inspection"),
    ("CCF-006", "JWF1 two-position connector", "both energized feedback inputs", "adjacent channels share body", "short/cross test and protection evidence"),
    ("CCF-007", "KWD1/KWD2 adjacent DIN modules", "both safety-input returns and feedback", "common contamination, miswire, service action or bridge", "barrier/routing/terminal-cover decision and physical inspection"),
    ("CCF-008", "panel wire duct", "E-stop returns, RESET/ARM/EDM and ordinary conductors", "routing not released; loose strand/abrasion can bridge", "separate routes or accepted protected-wiring analysis"),
    ("CCF-009", "external 24 V adapter/F24", "all control and safety logic", "single source/foldback/recovery affects all channels", "source/protection/brownout characterization"),
    ("CCF-010", "debug/programming fixture", "WDCTRL1, shared 0 V and test points", "fixture can back-power or bridge nets", "unpowered current-limited keyed fixture and inspection"),
    ("CCF-011", "configuration/workmanship", "entire watchdog and safety interface", "wrong revision, swapped channels or mirrored terminal map", "manifest, two-person point-to-point and received mapping"),
    ("CCF-012", "environment/enclosure", "all panel channels", "temperature, condensation, swarf, vibration and loose hardware", "exact site/enclosure/environment limits and validation"),
]
CCF_ROWS = [{"ccf_id": a, "common_cause_group": b, "affected_boundary": c, "mechanism": d, "required_measure": e, "accepted_fault_exclusion": "NONE", "status": "OPEN", "warning": WARNING} for a, b, c, d, e in CCF]


CASES = [
    ("FI-001", "interrupt PI_HEARTBEAT toggling", "DF-01 nominal dropout only"),
    ("FI-002", "hold PI_HEARTBEAT static high", "assume diagnostic may remain healthy or fail"),
    ("FI-003", "supply plausible erroneous toggling", "diagnostic failure assumed"),
    ("FI-004", "force both WDCTRL1 drive outputs asserted", "S0 action must still remove SR1 eligibility"),
    ("FI-005", "force one UDRV output continuously sinking", "same-channel S0 action must remain effective"),
    ("FI-006", "simulate one KWD 11-14 welded closed with approved fixture", "one S0 channel must still be recognized; exact acceptance qualified"),
    ("FI-007", "simulate both KWD 11-14 contacts closed", "both S0 channels and manual restart sequence remain effective"),
    ("FI-008", "open each coil/conductor separately then restore", "restoration alone never energizes K1/K2"),
    ("FI-009", "remove SAFETY_24V and SAFETY_0V separately", "safe dropout; recovery alone no K1/K2"),
    ("FI-010", "sweep/ramp control voltage through brownout and recovery", "no chatter or restart outside qualified limits"),
    ("FI-011", "force WD1_NC_DIAG false high/low", "no RESET, ARM, coil or motion authority"),
    ("FI-012", "force WD2_NC_DIAG false high/low", "no RESET, ARM, coil or motion authority"),
    ("FI-013", "approved JWP1 pin1-to-pin3 and pin1-to-pin4 fault simulation", "effects contained; S0 remains effective; protection limits open"),
    ("FI-014", "approved JWP1 pin3-to-pin4 bridge", "diagnostic common cause only; S0 remains effective"),
    ("FI-015", "approved JWF1 pin1-to-pin2 bridge", "feedback corruption only; no authority"),
    ("FI-016", "approved WD1/WD2_NC_24V short-to-0V simulations", "protection response does not damage credited paths"),
    ("FI-017", "simulate ISO1 open/short/loss-of-isolation equivalents", "assume diagnostic failure; credited paths unaffected"),
    ("FI-018", "analyze then simulate DC1 input-output fault with approved protected fixture", "no propagation capable of impairing credited path"),
    ("FI-019", "swap/remove KWD1 and verify received terminal map", "configuration error detected before connection"),
    ("FI-020", "swap/remove KWD2 and verify received terminal map", "configuration error detected before connection"),
    ("FI-021", "inspect/test unused 12/24 terminals and single-channel bypass access", "unused terminals isolated; no hidden bridge"),
    ("FI-022", "simulate accessible watchdog-to-RESET/ARM/EDM conductor bridge", "no automatic or out-of-order restart"),
    ("FI-023", "probe-fixture and contamination bridge matrix", "every accessible bridge analyzed and safely dispositioned"),
    ("FI-024", "analyze KWD1 A1/21-to-14 internal-equivalent injection before any physical simulation", "no test until qualified method; redesign if SF-01 impairment cannot be excluded/controlled"),
    ("FI-025", "analyze KWD2 A1/21-to-14 internal-equivalent injection before any physical simulation", "no test until qualified method; redesign if SF-01 impairment cannot be excluded/controlled"),
    ("FI-026", "analyze/simulate common SAFETY_24V bridge to both SR1 return nodes", "must not be accepted without qualified architecture disposition"),
    ("FI-027", "interrupt/reconnect shared 0 V under controlled no-load conditions", "no uncontrolled relay pickup or automatic restart"),
    ("FI-028", "unpowered debug fixture back-power/adjacent-short matrix", "no controller execution, relay drive or stored-energy hazard"),
]
CASE_ROWS = [{"case_id": a, "injection_or_analysis": b, "minimum_acceptance_boundary": c, "fixture": "SELECTION REQUIRED", "instrumentation": "SELECTION REQUIRED", "numerical_limit": "SELECTION REQUIRED", "execution_state": "NOT EXECUTED", "authorization": "NOT AUTHORIZED", "warning": WARNING} for a, b, c in CASES]


SEPARATION = [
    ("SEP-001", "S0 channel 1 conductors versus SAFETY_24V", "route/barrier prevents a single bridge from forcing SR1_S12"),
    ("SEP-002", "S0 channel 2 conductors versus SAFETY_24V", "route/barrier prevents a single bridge from forcing SR1_S22"),
    ("SEP-003", "channel 1 versus channel 2 E-stop returns", "separate terminals/routes and no common jumper"),
    ("SEP-004", "KWD1 A1/21 versus terminal 14", "qualified relay/internal-fault disposition plus external routing control"),
    ("SEP-005", "KWD2 A1/21 versus terminal 14", "qualified relay/internal-fault disposition plus external routing control"),
    ("SEP-006", "KWD1 versus KWD2 module boundary", "barrier/spacing/cover and service controls selected"),
    ("SEP-007", "JWP1 power versus coil-sink pins", "connector/ferrule/strain-relief and short control accepted"),
    ("SEP-008", "JWF1 energized feedback channels", "protection and cross-channel consequence accepted"),
    ("SEP-009", "watchdog PCB versus SR1/SRA1/RESET/ARM conductors", "separate duct/entry and secured harness"),
    ("SEP-010", "test points TP1..TP16", "shrouded/keyed fixture and dropped-probe exclusion"),
    ("SEP-011", "debug fixture", "unpowered-only connection, series limiting and no-back-power proof"),
    ("SEP-012", "SAFETY_24V and SAFETY_0V distribution", "exact protection/terminal/return topology and fault-current evidence"),
    ("SEP-013", "unused KWD terminals 12/24", "no conductor; insulated marker/cover; inspection"),
    ("SEP-014", "panel wire duct and bend/service zones", "released routing drawing and measured fill/bend/clearance"),
    ("SEP-015", "enclosure contamination controls", "IP/environment/workmanship/cleaning and post-work inspection"),
    ("SEP-016", "configuration identity", "exact commit, ECAD, PCB, panel, firmware and harness hashes match"),
]
SEPARATION_ROWS = [{"control_id": a, "boundary": b, "required_condition": c, "released_value_or_method": "SELECTION REQUIRED", "inspection_state": "NOT EXECUTED", "qualified_disposition": "NOT EXECUTED", "warning": WARNING} for a, b, c in SEPARATION]


DECISIONS = [
    ("WDD-001", "Current KWD A1/21-to-14 injection vulnerability", "Choose redesign, accepted fault control/allocation, or removal of KWD contacts from credited input loops", "BLOCKER"),
    ("WDD-002", "SF-01/SF-03 PLr/category/architecture", "Qualified ISO 12100/ISO 13849 allocation and calculation", "BLOCKER"),
    ("WDD-003", "KWD internal fault model and application", "Manufacturer evidence plus qualified circuit-fault analysis; no inferred exclusion", "BLOCKER"),
    ("WDD-004", "Panel separation/protected routing", "Released conductor/terminal/barrier/duct drawing and physical inspection", "BLOCKER"),
    ("WDD-005", "F24 and conductor/protection coordination", "Fault current, inrush, cable, ambient, bundling, terminals and jurisdiction", "BLOCKER"),
    ("WDD-006", "Brownout/recovery numerical limits", "Measured source/relay/controller behavior and accepted timing budget", "MAJOR"),
    ("WDD-007", "Fault-injection fixture/method/limits", "Qualified approved no-load fixture, instruments and acceptance values", "BLOCKER"),
    ("WDD-008", "Guarded containment with DF-01 failed", "Released PG-01 guard/receiver and physical proof", "BLOCKER"),
]
DECISION_ROWS = [{"decision_id": a, "unresolved_selection": b, "evidence_needed": c, "priority": d, "state": "SELECTION REQUIRED", "warning": WARNING} for a, b, c, d in DECISIONS]


SOURCES = [
    ("WDS-001", "Project Button", "Electrical V3 net/connector/wire schedules", "V3-P1.12 generated source; reviewed 2026-08-08", "electrical/kicad/project-button-v3/", "exact project connectivity; physical article absent"),
    ("WDS-002", "Project Button", "PCB-P0.5 test-access evidence", "generated 2026-08-06", "electrical/kicad/project-button-v3/validation/project-button-v3-pcb-test-access-evidence.json", "encoded PCB geometry only"),
    ("WDS-003", "Phoenix Contact", "PLC-RSC-24DC/21-21 item 2967060 product record", "official product PDF data-maintenance 2026-04-01; rechecked 2026-08-08", "https://www.phoenixcontact.com/en-pc/products/relay-module-plc-rsc-24dc-21-21-2967060?type=pdf", "terminal/contact/coil identity; no project safety approval"),
    ("WDS-004", "Texas Instruments", "TPL7407L datasheet SLRS066D", "Revision D, March 2016; product page rechecked 2026-08-08", "https://www.ti.com/lit/ds/symlink/tpl7407l.pdf", "ordinary low-side driver behavior; catalog device"),
    ("WDS-005", "Texas Instruments", "ISO1211/ISO1212 datasheet SLLSEY7G", "Revision G, February 2025; rechecked 2026-08-08", "https://www.ti.com/lit/ds/symlink/iso1212.pdf", "feedback receiver behavior; no project safety credit"),
    ("WDS-006", "Raspberry Pi", "RP2040/Pico product information", "official portal updated 2025-10-06; rechecked 2026-08-08", "https://pip.raspberrypi.com/categories/814-rp2040", "ordinary controller hardware; no safety designation inferred"),
    ("WDS-007", "Pilz", "PNOZ s4 operating manual 21396-EN-23", "English revision 23, colophon 2026-02; project record rechecked 2026-08-08", "https://www.pilz.com/download/open/OM_PNOZ_s4_21396-EN-23.pdf", "candidate terminal/mode evidence only; application validation open"),
    ("WDS-008", "ISO", "ISO 13849-1:2023 official record", "Edition 4, published 2023-04; rechecked 2026-08-08", "https://www.iso.org/standard/73481.html", "method/revision identification only; controlled standard required"),
]
SOURCE_ROWS = [{"source_id": a, "authority": b, "document": c, "revision_or_date": d, "url_or_path": e, "use_and_boundary": f, "warning": WARNING} for a, b, c, d, e, f in SOURCES]


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    write_csv(OUT / "exact-path-register.csv", PATH_ROWS)
    write_csv(OUT / "failure-mode-register.csv", FAILURE_ROWS)
    write_csv(CANONICAL_FMEA, CANONICAL_FAILURE_ROWS)
    write_csv(OUT / "common-cause-group-register.csv", CCF_ROWS)
    write_csv(OUT / "fault-injection-matrix.csv", CASE_ROWS)
    write_csv(OUT / "separation-control-register.csv", SEPARATION_ROWS)
    write_csv(OUT / "open-decision-register.csv", DECISION_ROWS)
    write_csv(OUT / "source-register.csv", SOURCE_ROWS)
    write_csv(RESULT_FORM, [{**row, "source_commit": "NOT EXECUTED", "article_configuration": "NOT EXECUTED", "operator": "NOT EXECUTED", "witness": "NOT EXECUTED", "raw_evidence": "NOT EXECUTED", "result": "NOT EXECUTED", "nonconformance": "NOT EXECUTED", "qualified_disposition": "NOT EXECUTED"} for row in CASE_ROWS])
    write_csv(INSPECTION_FORM, [{**row, "source_commit": "NOT EXECUTED", "as_built_reference": "NOT EXECUTED", "instrument": "NOT EXECUTED", "observed_result": "NOT EXECUTED", "raw_evidence": "NOT EXECUTED", "result": "NOT EXECUTED"} for row in SEPARATION_ROWS])
    status = {
        "revision": REVISION,
        "configuration": CONFIGURATION,
        "exact_path_count": len(PATH_ROWS),
        "failure_mode_count": len(FAILURE_ROWS),
        "common_cause_group_count": len(CCF_ROWS),
        "fault_case_count": len(CASE_ROWS),
        "separation_control_count": len(SEPARATION_ROWS),
        "open_decision_count": len(DECISION_ROWS),
        "df01_safety_credit": "ZERO",
        "sf01_sf03_allocation": "SELECTION REQUIRED",
        "current_topology_noninterference_proved": False,
        "physical_test_executed": False,
        "qualified_review_executed": False,
        "energization_authorized": False,
        "warning": WARNING,
    }
    (OUT / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n")
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="980" viewBox="0 0 1600 980"><style>text{{font-family:Arial,sans-serif;fill:#082b4c;font-size:18px}}.title{{font-size:34px;font-weight:700}}.head{{font-size:23px;font-weight:700}}.warn{{font-size:20px;font-weight:700;fill:#7a3500}}.box{{fill:#f4faff;stroke:#0b4f8a;stroke-width:3}}.block{{fill:#fff3cc;stroke:#c48700;stroke-width:4}}.line{{stroke:#0b4f8a;stroke-width:4;fill:none}}.red{{stroke:#b42318;stroke-width:5;stroke-dasharray:12 8;fill:none}}</style><rect width="1600" height="980" fill="#eef8ff"/><text x="60" y="60" class="title">HR-V0 watchdog non-interference boundary</text><text x="60" y="100" class="warn">{WARNING}</text><rect x="60" y="160" width="330" height="150" rx="16" class="box"/><text x="85" y="205" class="head">Credited candidate SF-01</text><text x="85" y="245">SR1 S11 / S21</text><text x="85" y="280">E-stop S0 dual NC</text><path d="M390 235 H520" class="line"/><rect x="520" y="160" width="400" height="150" rx="16" class="block"/><text x="545" y="205" class="head">Ordinary KWD boundary</text><text x="545" y="245">11-14 contact in each return</text><text x="545" y="280">A1 and 21 carry SAFETY_24V</text><path d="M920 235 H1050" class="line"/><rect x="1050" y="160" width="430" height="150" rx="16" class="box"/><text x="1075" y="205" class="head">SR1 return and restart chain</text><text x="1075" y="245">S12 / S22 then monitored RESET</text><text x="1075" y="280">Later SRA1 ARM + K1/K2 EDM</text><path d="M690 160 C700 95 875 95 885 160" class="red"/><text x="660" y="82" class="warn">A1/21-to-14 injection path: OPEN BLOCKER</text><rect x="60" y="380" width="1420" height="240" rx="16" class="box"/><text x="90" y="430" class="head">What is proved from repository source</text><text x="90" y="475">• DF-01 has zero safety credit and shares controller, power, PCB and enclosure dependencies.</text><text x="90" y="515">• Nominal heartbeat dropout opens one ordinary contact in each SR1 input return.</text><text x="90" y="555">• Nominal recovery still requires physical RESET, later physical ARM and a fresh trajectory.</text><text x="90" y="595">• PCB-P0.5 does not route the S0-to-KWD contact conductors, but panel routing is not released.</text><rect x="60" y="660" width="1420" height="230" rx="16" class="block"/><text x="90" y="710" class="head">What remains unproved</text><text x="90" y="755">• Internal KWD or panel bridges from SAFETY_24V to SR1 return nodes.</text><text x="90" y="795">• PLr/category, relay contribution, protected routing, CCF measures and accepted fault exclusions.</text><text x="90" y="835">• Brownout, contamination, debug back-power, physical fault injection and guard containment.</text><text x="90" y="875" class="warn">No physical injection is authorized until the fixture, method, limits and qualified reviewers are accepted.</text></svg>'''
    (OUT / "watchdog-boundary.svg").write_text(svg, encoding="utf-8", newline="\n")
    html = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{REVISION}</title><style>:root{{--sky:#dff3ff;--blue:#082b4c;--mid:#0b4f8a;--gold:#f2bd2d;--paper:#fff}}*{{box-sizing:border-box}}body{{margin:0;background:var(--sky);color:var(--blue);font:16px/1.55 system-ui,sans-serif}}main{{max-width:1180px;margin:auto;padding:32px}}h1{{font-size:clamp(32px,5vw,56px);line-height:1.08}}h2{{font-size:28px}}.warning{{background:#fff3cc;border:3px solid #c48700;padding:18px;font-weight:800;font-size:18px}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:18px}}.card{{background:var(--paper);border:2px solid var(--mid);border-radius:16px;padding:20px}}.n{{font-size:36px;font-weight:800;color:var(--mid)}}table{{width:100%;border-collapse:collapse;background:white}}th,td{{padding:12px;border:1px solid #7aa7c7;text-align:left;vertical-align:top}}th{{background:#ccecff}}details{{background:white;border:2px solid var(--mid);border-radius:12px;margin:14px 0;padding:14px}}summary{{font-weight:800;font-size:18px;cursor:pointer}}code{{font-size:14px}}@media(max-width:700px){{main{{padding:18px}}table{{display:block;overflow:auto}}}}</style></head><body><main><p class="warning">{WARNING}</p><h1>Watchdog dependent-failure review</h1><p><strong>{CONFIGURATION}</strong></p><p>This guide maps the ordinary heartbeat diagnostic onto the exact V3 terminals and exposes faults that could negatively affect candidate safety functions. It assigns no PL/SIL and authorizes no test.</p><div class="grid"><div class="card"><div class="n">18</div>exact paths</div><div class="card"><div class="n">32</div>failure modes</div><div class="card"><div class="n">12</div>common-cause groups</div><div class="card"><div class="n">28</div>unexecuted cases</div></div><h2>Blocking topology question</h2><div class="warning">KWD1/KWD2 each carry SAFETY_24V at A1 and 21 while terminal 14 returns to SR1 after an E-stop NC contact. A short to 14 could inject voltage downstream of the E-stop contact. The project has not proved this safe and must redesign or obtain a qualified allocation/control disposition.</div><h2>Nominal sequence</h2><ol><li>S0 channels and KWD 11-14 contacts complete SR1 input returns.</li><li>SR1 requires monitored physical RESET.</li><li>SR1 outputs enable SRA1 input eligibility.</li><li>SRA1 requires a distinct physical ARM through K1/K2 mirror-contact EDM.</li><li>A fresh validated trajectory is still required by control logic.</li></ol><details open><summary>What the package controls</summary><ul><li>Exact paths: <code>exact-path-register.csv</code></li><li>Failure modes: <code>failure-mode-register.csv</code></li><li>Common causes: <code>common-cause-group-register.csv</code></li><li>Unexecuted cases: <code>fault-injection-matrix.csv</code></li><li>Separation controls: <code>separation-control-register.csv</code></li><li>Open decisions: <code>open-decision-register.csv</code></li></ul></details><details><summary>Zero-credit boundary</summary><p>WDCTRL1, firmware, both drivers, both KWD relays and UFB1 feedback remain ordinary controls. Their nominal dropout is useful, but the risk assessment assumes that dropout can fail. The guard and hard stops must contain that assumed failure unless a separately allocated safety function is selected.</p></details><details><summary>Physical execution boundary</summary><p>All 28 cases are NOT EXECUTED and NOT AUTHORIZED. Actuator power must remain physically absent for the later E2 logic subset. Internal-equivalent injection, brownout and bridge tests need an accepted fixture, calibrated instrumentation, numerical limits, two-person control and qualified electrical/functional-safety approval.</p></details><img src="watchdog-boundary.svg" alt="Watchdog boundary diagram showing the open voltage-injection blocker" style="width:100%;height:auto;background:white;border:2px solid #0b4f8a;border-radius:12px"><p class="warning">DF-01 SAFETY CREDIT: ZERO. SF-01/SF-03 ALLOCATION: SELECTION REQUIRED.</p></main></body></html>'''
    (OUT / "index.html").write_text(html, encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
