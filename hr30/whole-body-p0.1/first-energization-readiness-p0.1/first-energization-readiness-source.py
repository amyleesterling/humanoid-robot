"""Generate the fail-closed HR-30 first-energization readiness package.

This package joins existing whole-body engineering artifacts into a controlled
execution ladder.  It does not execute a physical test or grant authority.
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
OUT = WHOLE / "first-energization-readiness-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / OUT.name
IDENTIFIER = "HR30-FIRST-ENERGIZATION-READINESS-P0.1"
WARNING = "PRELIMINARY - READINESS PLAN ONLY - NOT APPROVED FOR CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
AUTHORITY = "NO CONNECTION, POWERED-TEST, MOTION, OR ENERGIZATION AUTHORITY"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise RuntimeError(f"refusing empty CSV: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def common(row: dict) -> dict:
    return {**row, "state": "OPEN - NOT EXECUTED", "authority": AUTHORITY, "warning": WARNING}


def source_rows() -> list[dict]:
    items = [
        ("motion controller native ECAD status", "electrical/motion-controller-p0.1/controller-status.json"),
        ("actuator interface carrier native ECAD status", "electrical/carriers-p0.1/carrier-status.json"),
        ("25-channel actuator PDU native ECAD status", "electrical/actuator-branch-pdu-p0.1/pdu-status.json"),
        ("energy and safety architecture status", "energy-safety-spine-p0.1/energy-safety-status.json"),
        ("external tether power core status", "electrical/tether-power-core-p0.1/power-core-status.json"),
        ("whole-robot physical harness status", "harness/physical-p0.1/physical-harness-status.json"),
        ("physical head HMI harness candidate status", "harness/head-hmi-harness-p0.1/head-hmi-status.json"),
        ("25-axis harness/current policy status", "harness/current-policy-binding-p0.1/status.json"),
        ("25-axis actuator cable-kit status", "harness/actuator-cable-kit-p0.1/actuator-cable-kit-status.json"),
        ("actuator cable coupon and as-built route-measurement status", "harness/actuator-cable-coupon-p0.1/coupon-status.json"),
        ("one-axis commissioning station status", "electrical/axis-commissioning-station-p0.1/commissioning-status.json"),
        ("bench harness status", "electrical/axis-commissioning-station-p0.1/bench-harness-p0.1/harness-status.json"),
        ("torque-disabled inspection fixture status", "electrical/axis-commissioning-station-p0.1/no-motion-inspection-p0.1/inspection-status.json"),
        ("whole-body logical ECAD status", "electrical/kicad/hr30-whole-body-electrical-p0.1/electrical-status.json"),
        ("whole-body assembly traveler status", "assembly-guide-p0.1/assembly-status.json"),
        ("manufacturing artifact status", "manufacturing-files/manufacturing-files-status.json"),
        ("compiled whole-body no-motion firmware status", "firmware/hr30-motion-controller-p0.1/firmware-status.json"),
        ("no-actuator STM32 target bring-up status", "firmware/stm32-target-bringup-p0.1/bringup-status.json"),
        ("logic-only controller power-kit status", "electrical/logic-power-kit-p0.1/logic-power-status.json"),
        ("whole-robot grounding and DC-reference candidate status", "electrical/grounding-reference-architecture-p0.1/grounding-reference-status.json"),
        ("physical protective-bonding implementation candidate status", "electrical/protective-bonding-implementation-p0.1/physical-bond-status.json"),
    ]
    rows = []
    for number, (role, relative) in enumerate(items, 1):
        path = WHOLE / relative
        if not path.is_file():
            raise FileNotFoundError(path)
        rows.append({"source_id": f"FER-S{number:02d}", "path": path.relative_to(ROOT).as_posix(), "sha256": sha(path), "role": role, "warning": WARNING})
    return rows


def gate_rows() -> list[dict]:
    data = [
        ("FER-G01", "Frozen as-built configuration", "exact CAD/ECAD/firmware/software hashes and received-part identifiers agree with the traveler", "configuration controller"),
        ("FER-G02", "Mechanical restraint and guards", "received assembly inspected; restraint, guards, feet, support frame and exclusion zone signed", "mechanical reviewer"),
        ("FER-G03", "Protective-earth and DC reference", "jurisdiction and enclosure assumptions frozen; PE continuity and the single proposed DC 0 V/PE bond measured", "qualified electrical reviewer"),
        ("FER-G04", "External interruption chain", "source disconnect, two contactors, E-stop channels, monitored reset, EDM and service disconnect physically verified", "functional-safety reviewer"),
        ("FER-G05", "Branch protection coordination", "main and all branch protection selected from measured fault/inrush/regeneration evidence and documented clearing limits", "qualified electrical reviewer"),
        ("FER-G06", "Harness acceptance", "25 power pairs and all signal links pass conductor, crimp, polarity, insulation, continuity, retention, flex and no-backfeed inspections", "harness inspector"),
        ("FER-G07", "Received-board inspection", "controller, carriers and PDU match released candidates and pass assembly, isolation, polarity and unpowered checks", "electronics reviewer"),
        ("FER-G08", "Safety fault injection", "E-stop, reset, EDM, watchdog, dual-contactors and welded/stuck/open fault cases pass the frozen procedure", "functional-safety reviewer"),
        ("FER-G09", "No-motion software boundary", "approved target hash boots with all 25 torque bits, eight bus transmit paths, precharge request and action-ready output inactive; host logic is only precursor evidence", "controls reviewer"),
        ("FER-G10", "Test environment", "guarded area, fall restraint, fire response, thermal monitoring, observers and stop roles are physically ready", "test lead"),
        ("FER-G11", "Instrumentation and limits", "calibration records, probes, shunts, current/voltage/temperature limits and abort criteria are frozen", "test lead"),
        ("FER-G12", "Qualified release-to-test signoff", "electrical, functional-safety, mechanical, controls and test owners sign the same frozen configuration", "configuration controller"),
    ]
    return [common({"gate_id": i, "gate": name, "objective_evidence": evidence, "responsible_role": role, "completion_record": "NONE"}) for i, name, evidence, role in data]


def state_rows() -> list[dict]:
    data = [
        ("FER-E0", "Unpowered received-assembly inspection", "all electrical sources physically absent", "visual, dimensional, fastener, guard and configuration inspection", "remain unpowered"),
        ("FER-E1", "Continuity and insulation only", "source and storage physically absent; discharge verified", "PE, DC reference, insulation, continuity, polarity and no-backfeed measurements", "isolate and investigate any unexpected continuity"),
        ("FER-E2", "Logic-only 5 V", "actuator source disconnected and locked out; motor connectors absent", "compute/controller boot, watchdog state and communications without actuator energy", "remove 5 V on unexpected output or temperature"),
        ("FER-E3", "Safety-control dry test", "actuator bus physically absent; contactor load side de-energized", "E-stop/reset/EDM/watchdog coil logic and mirror-contact observation", "remove control power on any unsafe transition"),
        ("FER-E4", "Isolated one-axis bench station", "separate guarded fixture; one actuator maximum; 11.0 V and 0.25 A candidate limit", "read-only identity/telemetry with torque disabled", "bench station only; never connected to whole-body power"),
        ("FER-E5", "PDU branch load injection", "no actuators attached; isolated current-limited load; one branch at a time", "polarity, current sensing, interruption and telemetry correlation", "disconnect on limit, heating or unexpected adjacent-branch voltage"),
        ("FER-E6", "Installed-robot passive branch check", "all actuators disconnected; source current-limited below selected safe inspection value", "branch-by-branch polarity and unintended cross-feed checks", "remove source before mating any actuator"),
        ("FER-E7", "First actuator-rail energization", "all G01-G12 complete; whole robot restrained; torque disabled; zero motion request", "controlled rail voltage/current/temperature observation only", "dual interruption on any motion, limit or state mismatch"),
    ]
    return [common({"state_id": i, "state": name, "required_isolation": isolation, "permitted_activity": permitted, "abort_action": abort, "motion_permitted": "NO"}) for i, name, isolation, permitted, abort in data]


def traveler_rows() -> list[dict]:
    checks = [
        ("T01", "Record branch, commit, package manifests and software hashes", "FER-G01"),
        ("T02", "Record received serial/lot/revision for every energized assembly", "FER-G01"),
        ("T03", "Inspect frame, covers, sharp edges and service access", "FER-G02"),
        ("T04", "Verify physical fall restraint independently supports the robot", "FER-G02"),
        ("T05", "Verify feet/support base and exclusion-zone dimensions", "FER-G02"),
        ("T06", "Confirm enclosure, mains category and jurisdiction assumptions", "FER-G03"),
        ("T07", "Measure PE continuity to every exposed conductive part", "FER-G03"),
        ("T08", "Verify exactly one controlled DC 0 V/PE bond, or record approved alternate", "FER-G03"),
        ("T09", "Inspect external source, service disconnect and dual contactors", "FER-G04"),
        ("T10", "Confirm all energy storage is absent or discharged before passive checks", "FER-G04"),
        ("T11", "Record selected main and branch protection identifiers and ratings", "FER-G05"),
        ("T12", "Review fault-current, cable, ambient, bundling, inrush and duty inputs", "FER-G05"),
        ("T13", "Inspect all 25 actuator power pairs against controlled contact maps", "FER-G06"),
        ("T14", "Continuity-check every conductor and shield bond", "FER-G06"),
        ("T15", "Insulation-test power-to-data, power-to-frame and branch-to-branch", "FER-G06"),
        ("T16", "Verify data-only inter-actuator links contain no VDD backfeed path", "FER-G06"),
        ("T17", "Inspect controller, carriers and PDU for assembly/revision defects", "FER-G07"),
        ("T18", "Verify no solder bridge across isolation moats or protected branches", "FER-G07"),
        ("T19", "Load approved torque-disabled firmware and record its hash", "FER-G09"),
        ("T20", "Verify local boot state requests zero torque and zero motion", "FER-G09"),
        ("T21", "Verify conversational agent cannot directly address actuator buses", "FER-G09"),
        ("T22", "Stage guards, observers, E-stop operator and fire response", "FER-G10"),
        ("T23", "Record instrument models, serials and calibration dates", "FER-G11"),
        ("T24", "Freeze voltage/current/temperature/time abort limits", "FER-G11"),
        ("T25", "Execute and attach every fault-injection result", "FER-G08"),
        ("T26", "Collect all five qualified signoffs on one configuration", "FER-G12"),
    ]
    return [common({"check_id": i, "inspection_or_action": text, "gate_id": gate, "recorded_value": "NONE", "performed_by": "UNASSIGNED", "witness": "UNASSIGNED", "timestamp": "NOT RECORDED"}) for i, text, gate in checks]


def fault_rows() -> list[dict]:
    cases = [
        ("F01", "open E-stop channel A", "both actuator-energy contactors open; reset cannot restore without corrected channel"),
        ("F02", "open E-stop channel B", "same fail-safe interruption as channel A"),
        ("F03", "cross-channel discrepancy", "permit withheld and diagnostic latched"),
        ("F04", "E-stop release without manual reset", "no contactor closure and no motion request"),
        ("F05", "held or bypassed reset", "monitored-start logic refuses permit"),
        ("F06", "welded/stuck primary contactor simulation", "mirror/EDM prevents restart and second contactor interrupts"),
        ("F07", "welded/stuck secondary contactor simulation", "mirror/EDM prevents restart and first contactor interrupts"),
        ("F08", "watchdog heartbeat removed", "permit drops within selected measured limit"),
        ("F09", "watchdog output stuck/bypassed", "independent safety chain still interrupts energy; fault detected before restart"),
        ("F10", "motion controller reset/brownout", "all 25 torque bits and eight bus transmit paths remain inactive; contactor permit remains external/absent after reboot"),
        ("F11", "loss of communications or agent process", "deterministic local layer requests safe stop; no autonomous retry to motion"),
        ("F12", "unexpected adjacent-branch voltage/backfeed", "source removed and configuration quarantined"),
    ]
    return [common({"fault_id": i, "injected_condition": condition, "required_response": response, "measured_response": "NONE", "pass_fail": "NOT EXECUTED", "evidence_path": "NONE"}) for i, condition, response in cases]


def measurement_rows() -> list[dict]:
    data = [
        ("M01", "PE continuity", "ohm", "SELECTION REQUIRED - jurisdiction/enclosure/reviewer"),
        ("M02", "power-to-frame insulation", "Mohm", "SELECTION REQUIRED - equipment and circuit category"),
        ("M03", "branch-to-branch insulation", "Mohm", "SELECTION REQUIRED - equipment and circuit category"),
        ("M04", "DC 0 V/PE bond resistance and location", "ohm", "SELECTION REQUIRED - approved grounding scheme"),
        ("M05", "available source fault current", "A", "SELECTION REQUIRED - source/impedance/test method"),
        ("M06", "contactor drop-out time", "ms", "SELECTION REQUIRED - stopping-time allocation"),
        ("M07", "watchdog permit drop time", "ms", "SELECTION REQUIRED - safety requirements specification"),
        ("M08", "logic-only source current", "A", "SELECTION REQUIRED - frozen as-built load"),
        ("M09", "PDU one-branch current and voltage drop", "A/V", "SELECTION REQUIRED - branch device/protection"),
        ("M10", "first rail current/voltage/temperature observation", "A/V/degC", "SELECTION REQUIRED - qualified test plan"),
    ]
    return [common({"measurement_id": i, "measurement": name, "unit": unit, "acceptance_limit": limit, "instrument_id": "UNASSIGNED", "measured_value": "NONE", "evidence_path": "NONE"}) for i, name, unit, limit in data]


def signoff_rows() -> list[dict]:
    roles = ["qualified electrical reviewer", "functional-safety reviewer", "mechanical reviewer", "controls/test lead", "configuration owner"]
    return [common({"signoff_id": f"FER-SO{i:02d}", "role": role, "person": "UNASSIGNED", "qualification_or_basis": "UNRECORDED", "configuration_hash": "NONE", "decision": "NOT SIGNED", "date": "NOT RECORDED"}) for i, role in enumerate(roles, 1)]


def hold_rows() -> list[dict]:
    data = [
        ("FER-H01", "received as-built robot does not yet exist", "fabricated assembly, inspection records and frozen serial/lot configuration"),
        ("FER-H02", "protective-earth/DC-reference and physical bonding candidates are defined but not approved", "topology plus enclosure, panel-terminal, tether-contact and fixed-wire families are bound; fault sizing, AHJ disposition, moving-joint jumpers, received hardware, installation, measurements and qualified electrical disposition remain required"),
        ("FER-H03", "fuse/eFuse/conductor/contact ratings unresolved", "fault current, lengths, ambient, bundling, connector limits, inrush, regeneration and duty"),
        ("FER-H04", "physical harness and actuator cable kit are not built or tested; tooling and coupon travelers now exist but record zero execution and zero production cut lengths", "received-lot CF9/JST coupon results, accepted AWG24 current/thermal derating, qualified crimp process, continuity, insulation, flex/torsion, retention, signal-reference, shield/no-backfeed evidence, and measured 25-axis as-built routes"),
        ("FER-H05", "safety requirements and PLr/SIL allocation open", "SRS, risk assessment, common-cause analysis and qualified validation plan"),
        ("FER-H06", "total stopping time/distance unallocated", "measured sensor/logic/contactor/drive decay plus mechanical overtravel"),
        ("FER-H07", "boards unbuilt and uninspected", "received PCB/assembly inspection, coupons, isolation, thermal and fault testing"),
        ("FER-H08", "unflashed torque-disabled STM32 target configuration remains unapproved", "reproducible target ELF/BIN and static startup/GPIO evidence exist; independent review, approved hash, flashing, reset-state traces, HIL boot/fault behavior and physical write-path audit remain required"),
        ("FER-H09", "test site/restraint/fire response not commissioned", "physical readiness inspection and named trained operators"),
        ("FER-H10", "qualified multi-discipline signoff absent", "all five signoffs on the identical frozen configuration"),
    ]
    return [common({"hold_id": i, "unresolved_item": item, "evidence_required": evidence}) for i, item, evidence in data]


def render(gates: list[dict], states: list[dict]) -> str:
    gate_cards = "".join(f"<article><span>{html.escape(r['gate_id'])}</span><h3>{html.escape(r['gate'])}</h3><p>{html.escape(r['objective_evidence'])}</p><strong>OPEN</strong></article>" for r in gates)
    ladder = "".join(f"<li><b>{html.escape(r['state_id'])}: {html.escape(r['state'])}</b><p>{html.escape(r['permitted_activity'])}</p><em>Motion: NO · Authority: NO</em></li>" for r in states)
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 first-energization readiness</title><style>:root{{--deep:#071d36;--blue:#0b4f91;--sky:#d9f2ff;--gold:#f2b91d;--paper:#f7fbff;--ink:#142a40;--line:#82c4e6;--red:#982520}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.55 system-ui,Segoe UI,sans-serif}}header,main,footer{{padding:clamp(24px,5vw,64px) max(18px,calc((100vw - 1280px)/2))}}header,footer{{background:linear-gradient(135deg,var(--deep),var(--blue));color:white}}h1{{font-size:clamp(38px,6vw,70px);line-height:1.04;max-width:18ch}}h2{{font-size:clamp(28px,4vw,44px)}}h3{{font-size:21px}}.warning{{background:var(--gold);color:#17243a;border:3px solid #805600;padding:16px;font-weight:900}}.summary,.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:18px}}article,.panel,li{{background:white;border:2px solid var(--line);border-radius:16px;padding:19px}}article span{{font-weight:900;color:var(--blue)}}article strong,em{{color:var(--red)}}.metric{{font-size:clamp(34px,5vw,54px);font-weight:900;color:var(--blue)}}ol{{display:grid;gap:15px;padding:0;list-style:none}}a{{color:#075b9b;font-weight:800}}.links{{display:flex;flex-wrap:wrap;gap:12px}}.links a{{background:white;border:2px solid var(--line);border-radius:10px;padding:12px}}small{{font-size:14px}}@media(max-width:560px){{body{{font-size:16px}}}}</style></head><body><header><div class="warning">{html.escape(WARNING)}</div><p>HR-30 whole-body P0.1</p><h1>A controlled route to first power—not permission to power it.</h1><p>This guide joins the complete humanoid design, native ECAD, harness, safety architecture and one-axis commissioning station into one fail-closed execution path.</p></header><main><section class="summary"><article><div class="metric">12</div><p>release gates; all open</p></article><article><div class="metric">8</div><p>staged power states; all unauthorized</p></article><article><div class="metric">0</div><p>executed physical gates</p></article><article><div class="metric">0</div><p>qualified signoffs</p></article></section><section><h2>Release gates</h2><div class="grid">{gate_cards}</div></section><section><h2>Power-state ladder</h2><div class="panel"><p>Each state requires its own signed procedure. Advancing one state does not authorize the next. Motion is outside this ladder and remains prohibited.</p></div><ol>{ladder}</ol></section><section><h2>Executable records</h2><div class="links"><a href="energization-gate-register.csv">Gate register</a><a href="power-state-ladder.csv">Power states</a><a href="pre-energization-inspection-traveler.csv">Inspection traveler</a><a href="fault-injection-register.csv">Fault injection</a><a href="measurement-record.csv">Measurements</a><a href="qualified-signoff-register.csv">Signoffs</a><a href="configuration-baseline.csv">Configuration baseline</a><a href="open-holds.csv">Open holds</a></div><p><small>Every execution field is intentionally blank or NOT EXECUTED. An engineer must record real measurements and signatures against one frozen as-built configuration.</small></p></section></main><footer>{html.escape(WARNING)}</footer></body></html>'''


def integrate_root(gates: list[dict], states: list[dict], traveler: list[dict], faults: list[dict]) -> None:
    status_path = WHOLE / "package-status.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    status.update({
        "first_energization_readiness_package_present": True,
        "first_energization_gate_count": len(gates),
        "first_energization_power_state_count": len(states),
        "first_energization_inspection_check_count": len(traveler),
        "first_energization_fault_injection_case_count": len(faults),
        "first_energization_physical_gate_executed_count": 0,
        "first_energization_qualified_signoff_count": 0,
        "first_energization_ready": False,
        "connection_authority": False,
        "powered_test_authority": False,
        "motion_authority": False,
        "energization_authority": False,
    })
    status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")

    readme = WHOLE / "README.md"
    text = readme.read_text(encoding="utf-8")
    start, end = "<!-- HR30-FIRST-ENERGIZATION-P01-README-START -->", "<!-- HR30-FIRST-ENERGIZATION-P01-README-END -->"
    if start in text and end in text:
        text = text.split(start, 1)[0] + text.split(end, 1)[1]
    block = f'''{start}\n## First-energization readiness\n\nThe [interactive first-energization guide](first-energization-readiness-p0.1/index.html) joins the existing whole-body CAD, native ECAD, harness, safety architecture and one-axis bench station into **{len(gates)} objective release gates**, **{len(states)} staged power states**, a {len(traveler)}-item inspection traveler and {len(faults)} fault-injection cases. All physical execution and signoff fields remain open. This makes the path auditable; it does **not** authorize connection, powered testing, motion or energization.\n{end}\n'''
    marker = "<!-- HR30-HARNESS-CURRENT-BINDING-P01-README-START -->"
    readme.write_text(text.replace(marker, block + marker), encoding="utf-8", newline="\n")

    page = WHOLE / "index.html"
    text = page.read_text(encoding="utf-8")
    start, end = "<!-- HR30-FIRST-ENERGIZATION-P01-START -->", "<!-- HR30-FIRST-ENERGIZATION-P01-END -->"
    if start in text and end in text:
        text = text.split(start, 1)[0] + text.split(end, 1)[1]
    section = f'''{start}<section id="first-energization"><h2>The path to first power is now explicit</h2><div class="grid"><article class="card"><div class="metric">{len(gates)}</div><p>objective release gates</p></article><article class="card"><div class="metric">{len(states)}</div><p>staged power states; motion excluded</p></article><article class="card hold"><div class="metric">0</div><p>executed physical gates</p></article><article class="card hold"><div class="metric">0</div><p>qualified signoffs</p></article></div><p><a href="first-energization-readiness-p0.1/index.html">Open the interactive first-energization readiness guide</a>. It is a controlled plan, not permission to connect or energize hardware.</p></section>{end}'''
    marker = "<!-- HR30-HARNESS-CURRENT-BINDING-P01-START -->"
    page.write_text(text.replace(marker, section + marker), encoding="utf-8", newline="\n")


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    sources = source_rows()
    gates, states = gate_rows(), state_rows()
    traveler, faults = traveler_rows(), fault_rows()
    measurements, signoffs, holds = measurement_rows(), signoff_rows(), hold_rows()
    baseline = [{"baseline_id": "HR30-FER-B01", "configuration": "HR-30 whole-body P0.1 tether-first candidate", "branch": "RECORDED AT EXECUTION", "commit": "RECORDED AT EXECUTION - NOT FROZEN BY GENERATION", "as_built_serial": "NONE - ROBOT NOT BUILT", "firmware_hash": "REPRODUCIBLE UNFLASHED TARGET EVIDENCE PRESENT; APPROVED EXECUTION HASH SELECTION REQUIRED", "software_hash": "NONE - SELECTION REQUIRED", "physical_configuration_frozen": "NO", "authority": AUTHORITY, "warning": WARNING}]
    write_csv(OUT / "source-binding.csv", sources)
    write_csv(OUT / "configuration-baseline.csv", baseline)
    write_csv(OUT / "energization-gate-register.csv", gates)
    write_csv(OUT / "power-state-ladder.csv", states)
    write_csv(OUT / "pre-energization-inspection-traveler.csv", traveler)
    write_csv(OUT / "fault-injection-register.csv", faults)
    write_csv(OUT / "measurement-record.csv", measurements)
    write_csv(OUT / "qualified-signoff-register.csv", signoffs)
    write_csv(OUT / "open-holds.csv", holds)
    status = {
        "identifier": IDENTIFIER, "warning": WARNING,
        "source_binding_count": len(sources), "release_gate_count": len(gates), "power_state_count": len(states),
        "inspection_check_count": len(traveler), "fault_injection_case_count": len(faults), "measurement_record_count": len(measurements),
        "qualified_signoff_role_count": len(signoffs), "open_hold_count": len(holds),
        "physical_gate_executed_count": 0, "fault_injection_executed_count": 0, "qualified_signoff_count": 0,
        "host_no_motion_firmware_evidence_present": True, "stm32_target_binary_built": True,
        "actuator_cable_coupon_plan_present": True, "actuator_cable_coupon_built_count": 0,
        "actuator_cable_final_cut_length_count": 0,
        "stm32_target_bringup_plan_present": True, "stm32_target_bringup_flash_executed": False,
        "stm32_target_binary_flashed": False, "target_no_motion_firmware_approved": False,
        "first_energization_ready": False, "motion_in_scope": False, "configuration_frozen": False,
        "connection_authority": False, "powered_test_authority": False, "motion_authority": False, "energization_authority": False,
    }
    (OUT / "readiness-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    (OUT / "README.md").write_text(f"# HR-30 first-energization readiness P0.1\n\n**{WARNING}**\n\nThis package turns the current whole-body engineering set into a staged, measurable readiness path. It records no physical pass and grants no authority. Use [index.html](index.html) for the web guide.\n", encoding="utf-8", newline="\n")
    (OUT / "index.html").write_text(render(gates, states), encoding="utf-8", newline="\n")
    shutil.copy2(Path(__file__), OUT / "first-energization-readiness-source.py")
    manifest_rows = [{"path": p.relative_to(OUT).as_posix(), "bytes": p.stat().st_size, "sha256": sha(p), "warning": WARNING} for p in sorted(OUT.rglob("*")) if p.is_file() and p.name != "file-manifest.csv"]
    write_csv(OUT / "file-manifest.csv", manifest_rows)
    if RELEASE.exists():
        shutil.rmtree(RELEASE)
    shutil.copytree(OUT, RELEASE)
    integrate_root(gates, states, traveler, faults)
    import generate_hr30_system_package_p01 as system_package
    system_package.refresh_manifest_and_release()
    print(json.dumps(status, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
