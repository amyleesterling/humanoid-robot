"""Generate the HR-30 safety-function implementation map P0.1.

This is an implementation design artifact, not a validation record.  It binds
the whole-body SRS to exact current circuit terminals where they exist and
states fail-closed gaps where they do not.
"""

from __future__ import annotations

import csv
import hashlib
import html
import json
import re
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WHOLE = ROOT / "hr30" / "whole-body-p0.1"
OUT = WHOLE / "safety-function-implementation-p0.1"
REL = ROOT / "release" / "hr30" / "whole-body-p0.1" / OUT.name
IDENTIFIER = "HR30-SAFETY-FUNCTION-IMPLEMENTATION-P0.1"
WARNING = "PRELIMINARY - IMPLEMENTATION MAP ONLY - NOT FUNCTIONALLY SAFETY VALIDATED - NOT APPROVED FOR CONNECTION, POWERED TESTING, MOTION OR ENERGIZATION"
AUTHORITY = "NO CONNECTION, POWERED-TEST, MOTION OR ENERGIZATION AUTHORITY"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise RuntimeError(f"refusing empty register {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def implementation_rows() -> list[dict]:
    data = [
        ("SFR-01", "Emergency-stop demand removes actuator energy", "S0 NC1-A/NC1-B and NC2-A/NC2-B", "SR1 S11/S12 and S21/S22", "SR1 13-14 to K1 A1; SR1 23-24 to K2 A1; K1/K2 A2 to SAFE_0V", "K1 and K2 each use 1/L1-2/T1-3/L2-4/T2-5/L3-6/T3 in series", "K1/K2 21-22 mirror NC chain to S34", "ECAD CONNECTED - UNVALIDATED", "DC application, timing, diagnostic coverage, fault exclusions, CCF and physical tests"),
        ("SFR-02", "Prevention of unexpected restart", "S1 NO-A/NO-B plus healthy E-stop and EDM state", "SR1 S34 monitored start plus MCU1 deterministic state", "K1/K2 coils and MOTION_PERMIT_INPUT", "permit restoration does not create FRESH_MOTION_REQUEST", "PNOZ status is diagnostic only; fresh command is separate", "ECAD CONNECTED / FIRMWARE BOUNDARY DEFINED - UNVALIDATED", "falling-edge behavior, power-cycle/brownout/HIL and physical zero-motion proof"),
        ("SFR-03", "External-device monitoring", "K1 21-22 and K2 21-22 built-in mirror NC contacts", "series RESET_EDM feedback to SR1 S34", "safety-output eligibility blocked after failed opening", "no motion command path", "received-device identity and each independent welded/stuck fault", "ECAD CONNECTED - UNVALIDATED", "diagnostic coverage, timing, fault injection, CCF and qualified validation"),
        ("SFR-04", "Control-power loss enters safe state", "PS2 SAFE_24V loss; MCU reset/brownout", "PNOZ de-energization plus fail-low controller initialization", "K1/K2 coils de-energized; torque/TX/action-ready inactive", "physical actuator decay and gravity response unresolved", "power-cycle and brownout traces required", "PARTIAL ARCHITECTURE", "as-built supply decay, firmware/HIL, contactor opening, actuator torque decay and collapse containment"),
        ("SFR-05", "Actuator VDD backfeed prevention", "split-harness physical cavities", "physical segregation only", "25 individual protected power pairs", "standard ROBOTIS daisy cables carry VDD and are not acceptable as-is", "continuity/backfeed fault injection", "NOT IMPLEMENTED - HARNESS BLOCKER", "custom/de-pinned data-only links, 283-terminal physical bindings, 25 branch feeds and as-built tests"),
        ("SFR-06", "Branch overcurrent interruption", "branch current/fault", "protection device selection required", "one main plus five PDU holders now; 25 actuator branch protections unresolved", "no fuse value or conductor released", "coordination and thermal test", "NOT IMPLEMENTED", "fault current, wire length, ambient, bundling, inrush, duty, connector limits, regeneration and jurisdiction"),
        ("SFR-07", "Watchdog loss requests safe stop", "heartbeat", "watchdog/MCU diagnostic path", "permit request only", "cannot bypass E-stop or directly energize K1/K2", "fault log only", "DEFINED - NO SAFETY CREDIT", "hardware implementation, fault response and any future safety allocation"),
        ("SFR-08", "Torque-disable command", "deterministic controller state", "compiled local firmware", "serial torque-disable commands", "not an independent energy-isolation function", "readback and physical torque test", "COMPILED - UNFLASHED - STANDARD CONTROL", "flash, bench test, all 25 axes, bus loss, timeout and torque-decay evidence"),
        ("SFR-09", "Charger interlock", "charger-present contact", "future hardwired interlock", "safety eligibility", "not present in tether-first configuration", "unplug/reset sequence", "FUTURE - NOT IMPLEMENTED", "onboard source/charger architecture and fault-tested hardwired interlock"),
        ("SFR-10", "Fall restraint prevents head/floor contact", "mechanical fall", "rated restraint system", "gantry/harness/robot attachment", "no current rated design", "dynamic arrest proof", "NOT SELECTED OR PROVED", "WLL, arrest energy, travel, attachment loads, inspection and qualified mechanical acceptance"),
        ("SFR-11", "Safety-related speed/travel limiting", "redundant position/speed evidence", "future safety controller", "independent torque/energy interruption", "standard actuator limits receive no safety credit", "overspeed/limit fault injection", "NOT IMPLEMENTED - MOTION PROHIBITED", "architecture, PLr allocation, independent sensing, response time and validation"),
        ("SFR-12", "Power-loss collapse containment", "rail/supply loss", "passive supports/restraint plus future braking", "mechanical capture", "no validated whole-body power-loss strategy", "drop/coast/overtravel proof", "NOT IMPLEMENTED - MOTION PROHIBITED", "accepted restraint, joint decay, gravity motion, braking, rebound, overtravel and physical proof"),
    ]
    return [{"function_id": i, "safety_function": name, "physical_input": inp, "logic_or_measure": logic, "physical_output": output, "independence_or_safe_state": independence, "diagnostic_or_validation_interface": diagnostic, "implementation_state": state, "remaining_closure": closure, "achieved_pl_claimed": "NO", "validation_state": "NOT VALIDATED", "authority": AUTHORITY, "warning": WARNING} for i, name, inp, logic, output, independence, diagnostic, state, closure in data]


def exact_circuit_rows() -> list[dict]:
    data = [
        ("SFR-01", "input channel 1", "S0", "NC1-A/NC1-B", "SAFE_24V / S12_CH1", "SR1 S11/S12"),
        ("SFR-01", "input channel 2", "S0", "NC2-A/NC2-B", "S21_TEST / S22_CH2", "SR1 S21/S22"),
        ("SFR-01", "output channel 1", "SR1/K1", "13-14 / A1-A2", "K1_COIL_POS / SAFE_0V", "K1 independent coil"),
        ("SFR-01", "output channel 2", "SR1/K2", "23-24 / A1-A2", "K2_COIL_POS / SAFE_0V", "K2 independent coil"),
        ("SFR-01", "power interruption K1", "K1", "1/L1-2/T1-3/L2-4/T2-5/L3-6/T3", "RAW_12V_POS to K1_OUT", "three main poles in series"),
        ("SFR-01", "power interruption K2", "K2", "1/L1-2/T1-3/L2-4/T2-5/L3-6/T3", "K1_OUT to TETHER_POS_SWITCHED", "three main poles in series"),
        ("SFR-02", "monitored reset", "S1/SR1", "NO-A/NO-B to S34", "S12_CH1 / RESET_EDM", "eligibility only"),
        ("SFR-02", "fresh motion boundary", "MCU1", "PERMIT/CMD/ENABLE", "MOTION_PERMIT_INPUT / FRESH_MOTION_REQUEST / PDU_ENABLE_BOUNDARY", "permit and fresh request are distinct"),
        ("SFR-03", "K1 mirror feedback", "K1", "21-22", "RESET_EDM to EDM_K1_OUT", "IEC mirror contact candidate"),
        ("SFR-03", "K2 mirror feedback", "K2", "21-22", "EDM_K1_OUT to RESET_EDM", "IEC mirror contact candidate"),
        ("SFR-03", "feedback logic", "SR1", "S34", "RESET_EDM", "monitored start/feedback input"),
        ("SFR-01", "status only", "SR1", "33-34 / 41-42 / Y32", "HARDWIRED_PERMIT / PNOZ_AUX_STATUS / PNOZ_Y32_STATUS", "41-42 and Y32 receive no safety credit"),
    ]
    return [{"function_id": i, "interface_role": role, "reference": ref, "terminal_or_pin": terminal, "net_path": net, "implementation_note": note, "physical_validation": "NOT EXECUTED", "authority": AUTHORITY, "warning": WARNING} for i, role, ref, terminal, net, note in data]


def build() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    srs = read_csv(WHOLE / "safety-requirements-p0.1" / "safety-function-register.csv")
    impl = implementation_rows()
    if {r["function_id"] for r in srs} != {r["function_id"] for r in impl}:
        raise RuntimeError("SRS implementation coverage drift")
    write_csv(OUT / "safety-function-implementation-matrix.csv", impl)
    write_csv(OUT / "exact-circuit-interface-map.csv", exact_circuit_rows())
    bindings = []
    for role, relative in [
        ("whole-body SRS", "safety-requirements-p0.1/safety-function-register.csv"),
        ("tether power terminal schedule", "electrical/tether-power-core-p0.1/connector-schedule.csv"),
        ("tether power net schedule", "electrical/tether-power-core-p0.1/net-schedule.csv"),
        ("power-core status", "electrical/tether-power-core-p0.1/power-core-status.json"),
        ("energy/safety boundary", "energy-safety-spine-p0.1/safety-function-boundary.csv"),
        ("motion-controller status", "firmware/hr30-motion-controller-p0.1/firmware-status.json"),
    ]:
        path = WHOLE / relative
        bindings.append({"role": role, "path": path.relative_to(ROOT).as_posix(), "sha256": sha(path), "warning": WARNING})
    write_csv(OUT / "source-binding.csv", bindings)
    holds = [
        ("SFI-H01", "qualified PLr/category allocation and achieved PL/PFHd calculation"),
        ("SFI-H02", "received LC1D40ABD identity, terminal and mirror-contact inspection"),
        ("SFI-H03", "fault current, L/R, protection, DC durability, regeneration and opening-time evidence"),
        ("SFI-H04", "full 283-terminal physical harness and 25 independent actuator power branches"),
        ("SFI-H05", "as-built CCF, diagnostic coverage, fault exclusions and environmental evidence"),
        ("SFI-H06", "measured total stopping time and all-axis stopping distance"),
        ("SFI-H07", "rated whole-body fall restraint and power-loss collapse strategy"),
        ("SFI-H08", "safety-related speed/travel architecture before motion"),
        ("SFI-H09", "physical zero-motion, welded-contact, brownout, backfeed and branch-fault tests"),
        ("SFI-H10", "qualified electrical and functional-safety review of one frozen as-built configuration"),
    ]
    write_csv(OUT / "open-implementation-holds.csv", [{"hold_id": i, "open_item": item, "state": "OPEN", "authority": AUTHORITY, "warning": WARNING} for i, item in holds])
    rows_html = "".join(f"<tr><td>{html.escape(r['function_id'])}</td><td>{html.escape(r['safety_function'])}</td><td>{html.escape(r['implementation_state'])}</td><td>{html.escape(r['remaining_closure'])}</td></tr>" for r in impl)
    (OUT / "index.html").write_text(f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 safety-function implementation map</title><style>:root{{--navy:#0d2d57;--blue:#167ab8;--sky:#d8f1ff;--gold:#f4b400;--paper:#f7fcff}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--navy);font:17px/1.55 system-ui,sans-serif}}header,main{{padding:clamp(20px,4vw,48px);max-width:1280px;margin:auto}}.warning{{background:#fff1b8;border:3px solid #8b6200;padding:16px;border-radius:14px;font-weight:850}}h1{{font-size:clamp(36px,6vw,72px);line-height:1.02}}table{{width:100%;border-collapse:collapse;background:white}}th,td{{border:1px solid #8cbdd8;padding:14px;text-align:left;vertical-align:top}}th{{background:var(--sky);font-size:16px}}td{{font-size:16px}}.scroll{{overflow-x:auto;border:2px solid var(--blue);border-radius:14px}}a{{color:#075f9f;font-weight:750}}@media(max-width:650px){{body{{font-size:16px}}th,td{{min-width:190px}}}}</style></head><body><header><p class="warning">{html.escape(WARNING)}</p><h1>What is implemented, exactly?</h1><p>Every SRS function is mapped to current physical terminals or marked absent. ERC cleanliness is not treated as functional-safety validation.</p></header><main><div class="scroll"><table><thead><tr><th>ID</th><th>Safety function</th><th>Current implementation</th><th>Required closure</th></tr></thead><tbody>{rows_html}</tbody></table></div><h2>Exact current circuit</h2><p><a href="exact-circuit-interface-map.csv">Open the terminal/net map</a> / <a href="safety-function-implementation-matrix.csv">download the full implementation matrix</a> / <a href="open-implementation-holds.csv">open holds</a>.</p><h2>Current conclusion</h2><p>Only SFR-01 through SFR-03 have a connected candidate circuit, and it remains unvalidated. SFR-04 is partial. SFR-05 and SFR-06 expose unresolved harness/protection blockers. SFR-07 and SFR-08 are standard-control paths with no safety credit. SFR-09 through SFR-12 are not implemented.</p></main></body></html>''', encoding="utf-8")
    (OUT / "README.md").write_text(f"# HR-30 safety-function implementation map P0.1\n\n**{WARNING}**\n\nThis package binds all 12 whole-body SRS functions to current physical terminals, nets, controller boundaries and open evidence. SFR-01 through SFR-03 now name the exact PNOZ and LC1D40ABD interfaces. It does not claim an achieved PL, completed validation or any work authority.\n", encoding="utf-8")
    status = {"identifier": IDENTIFIER, "warning": WARNING, "safety_function_count": 12, "exact_circuit_interface_count": 12, "connected_unvalidated_function_count": 3, "partial_function_count": 1, "functional_safety_validated": False, "achieved_pl_calculated": False, "qualified_review_complete": False, "connection_authority": False, "powered_test_authority": False, "motion_authority": False, "energization_authority": False}
    (OUT / "implementation-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    shutil.copy2(Path(__file__), OUT / "safety-function-implementation-source.py")
    files = sorted(p for p in OUT.rglob("*") if p.is_file() and p.name != "file-manifest.csv")
    write_csv(OUT / "file-manifest.csv", [{"path": p.relative_to(OUT).as_posix(), "bytes": p.stat().st_size, "sha256": sha(p), "warning": WARNING} for p in files])
    if REL.exists():
        shutil.rmtree(REL)
    shutil.copytree(OUT, REL)

    status_path = WHOLE / "package-status.json"
    root_status = json.loads(status_path.read_text(encoding="utf-8"))
    root_status.update({"safety_function_implementation_map_present": True, "safety_function_implementation_count": 12, "safety_functions_connected_unvalidated_count": 3, "safety_function_implementation_validated": False})
    status_path.write_text(json.dumps(root_status, indent=2) + "\n", encoding="utf-8")
    readme_path = WHOLE / "README.md"
    text = readme_path.read_text(encoding="utf-8")
    start, end = "<!-- HR30-SFI-P01-START -->", "<!-- HR30-SFI-P01-END -->"
    text = re.sub(re.escape(start) + r"[\s\S]*?" + re.escape(end), "", text).rstrip()
    text += f"\n\n{start}\n## Safety-function implementation map\n\nThe [interactive implementation map](safety-function-implementation-p0.1/index.html) binds all 12 SRS functions to current terminals and nets or marks them absent. Only SFR-01 through SFR-03 have connected candidate circuitry, and none is validated.\n{end}\n"
    readme_path.write_text(text, encoding="utf-8")
    page_path = WHOLE / "index.html"
    page = page_path.read_text(encoding="utf-8")
    pstart, pend = "<!-- HR30-SFI-P01-START -->", "<!-- HR30-SFI-P01-END -->"
    page = re.sub(re.escape(pstart) + r"[\s\S]*?" + re.escape(pend), "", page)
    section = f'''{pstart}<section id="safety-function-implementation"><h2>Every safety function now has an implementation disposition</h2><div class="grid"><article class="card pass"><h3>3 connected candidates</h3><p>E-stop energy removal, restart prevention and EDM have exact current circuit bindings. They remain unvalidated.</p></article><article class="card hold"><h3>9 incomplete or uncredited</h3><p>Harness backfeed, protection, restraint, speed/travel and power-loss functions still have material implementation gaps.</p></article></div><p><a href="safety-function-implementation-p0.1/index.html">Open the safety-function implementation map</a>.</p></section>{pend}'''
    page_path.write_text(page.replace("</main>", section + "</main>"), encoding="utf-8")
    release_root = ROOT / "release" / "hr30" / "whole-body-p0.1"
    for name in ("README.md", "index.html", "package-status.json"):
        shutil.copy2(WHOLE / name, release_root / name)
    import sys
    sys.path.insert(0, str(ROOT / "tools"))
    import generate_hr30_system_package_p01 as system_package
    system_package.refresh_manifest_and_release()
    print(json.dumps(status, indent=2))


if __name__ == "__main__":
    build()
