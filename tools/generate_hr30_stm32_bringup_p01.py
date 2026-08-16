"""Generate the HR-30 STM32 no-actuator target bring-up package.

This package defines a physical SWD boundary and an executable traveler.  It
does not claim that an adapter, cable, controller, flash, or HIL test exists.
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
OUT = WHOLE / "firmware" / "stm32-target-bringup-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / "firmware" / OUT.name
IDENTIFIER = "HR30-STM32-TARGET-BRINGUP-P0.1"
WARNING = "PRELIMINARY - UNEXECUTED NO-ACTUATOR BRING-UP PLAN - NOT APPROVED FOR CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
AUTHORITY = "NO CONNECTION, POWERED-TEST, MOTION, OR ENERGIZATION AUTHORITY"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise RuntimeError(f"refusing empty CSV: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def common(row: dict[str, object]) -> dict[str, object]:
    return {**row, "execution_state": "NOT EXECUTED", "authority": AUTHORITY, "warning": WARNING}


def primary_sources() -> list[dict[str, object]]:
    return [
        {"source_id": "BR-S01", "manufacturer": "STMicroelectronics", "document_or_page": "UM2910 STLINK-V3MINIE user manual", "revision_or_date": "UM2910 Rev 5", "accessed": "2026-08-16", "url": "https://www.st.com/resource/en/user_manual/um2910-stlinkv3minie-debuggerprogrammer-tiny-probe-for-stm32-microcontrollers-stmicroelectronics.pdf", "verified_use": "STDC14 contact assignment; target-voltage range; probe supplies no target power; order code", "warning": WARNING},
        {"source_id": "BR-S02", "manufacturer": "STMicroelectronics", "document_or_page": "STM32CubeProgrammer software description", "revision_or_date": "UM2237 Rev 30; CubeProgrammer v2.23.0 current release", "accessed": "2026-08-16", "url": "https://www.st.com/resource/en/user_manual/dm00403500-stm32cubeprogrammer-software-description-stmicroelectronics.pdf", "verified_use": "SWD connect, download, and verify command workflow; not production programming approval", "warning": WARNING},
        {"source_id": "BR-S03", "manufacturer": "JST", "document_or_page": "GH connector catalogue", "revision_or_date": "revision/date not stated", "accessed": "2026-08-16", "url": "https://www.jst-mfg.com/product/pdf/eng/eGH.pdf", "verified_use": "BM05B-GHS-TBT; GHR-05V-S; SSHL-002T-P0.2; AWG30-26; 1 A at AWG26", "warning": WARNING},
        {"source_id": "BR-S04", "manufacturer": "Samtec", "document_or_page": "FTSH-107-01-L-DV-K-A product page", "revision_or_date": "live product page; revision/date not stated", "accessed": "2026-08-16", "url": "https://www.samtec.com/products/ftsh-107-01-l-dv-k-a", "verified_use": "candidate mating STDC14 board header order code", "warning": WARNING},
    ]


def source_bindings() -> list[dict[str, object]]:
    items = [
        ("BR-B01", "motion-controller ECAD status", WHOLE / "electrical/motion-controller-p0.1/controller-status.json"),
        ("BR-B02", "motion-controller terminal register", WHOLE / "electrical/motion-controller-p0.1/terminal-register.csv"),
        ("BR-B03", "no-motion firmware status", WHOLE / "firmware/hr30-motion-controller-p0.1/firmware-status.json"),
        ("BR-B04", "target build evidence", WHOLE / "firmware/hr30-motion-controller-p0.1/output/stm32h743-p0.1/build-evidence.json"),
        ("BR-B05", "target artifact manifest", WHOLE / "firmware/hr30-motion-controller-p0.1/output/stm32h743-p0.1/artifact-manifest.csv"),
        ("BR-B06", "target ELF", WHOLE / "firmware/hr30-motion-controller-p0.1/output/stm32h743-p0.1/hr30-motion-controller-stm32h743.elf"),
        ("BR-B07", "target BIN", WHOLE / "firmware/hr30-motion-controller-p0.1/output/stm32h743-p0.1/hr30-motion-controller-stm32h743.bin"),
    ]
    return [{"binding_id": i, "role": role, "path": path.relative_to(ROOT).as_posix(), "sha256": sha(path), "bytes": path.stat().st_size, "warning": WARNING} for i, role, path in items]


def debug_contacts() -> list[dict[str, object]]:
    rows = [
        ("TVCC", "CN4", 3, "target voltage input", "JDBG1", 2, "CTRL_3V3", "SENSE ONLY - ST-LINK MUST NOT POWER TARGET"),
        ("SWDIO", "CN4", 4, "T_SWDIO", "JDBG1", 3, "SWDIO", "BIDIRECTIONAL DEBUG DATA"),
        ("GND-A", "CN4", 5, "GND", "JDBG1", 1, "CTRL_GND", "GROUND REFERENCE"),
        ("SWCLK", "CN4", 6, "T_SWCLK", "JDBG1", 4, "SWCLK", "DEBUG CLOCK"),
        ("GND-B", "CN4", 7, "GND", "JDBG1", 1, "CTRL_GND", "SECOND GROUND; TIED ON ADAPTER"),
        ("NRST", "CN4", 12, "T_NRST", "JDBG1", 5, "MCU_NRST", "TARGET RESET"),
    ]
    result = [common({"map_id": f"BR-M{index:02d}", "signal": signal, "probe_connector": pc, "probe_contact": pp, "probe_function": pf, "target_connector": tc, "target_contact": tp, "target_net": net, "wiring_rule": rule, "physical_validation": "REQUIRED"}) for index, (signal, pc, pp, pf, tc, tp, net, rule) in enumerate(rows, 1)]
    result.append(common({"map_id": "BR-M07", "signal": "GNDDETECT", "probe_connector": "CN4", "probe_contact": 11, "probe_function": "GNDDETECT - manual table interpretation not released here", "target_connector": "NONE", "target_contact": "NONE", "target_net": "NONE", "wiring_rule": "SELECTION REQUIRED - DO NOT CONNECT BY INFERENCE", "physical_validation": "REQUIRED"}))
    return result


def bom_rows() -> list[dict[str, object]]:
    data = [
        ("BR-P01", "debug probe", "STMicroelectronics", "STLINK-V3MINIE", 1, "manufacturer order code verified", "PROPOSED"),
        ("BR-P02", "probe cable", "STMicroelectronics", "STDC14 cable included with STLINK-V3MINIE", 1, "receipt inspection required", "PROPOSED"),
        ("BR-P03", "adapter STDC14 header", "Samtec", "FTSH-107-01-L-DV-K-A", 1, "manufacturer product page verified", "PROPOSED"),
        ("BR-P04", "adapter JST header", "JST", "BM05B-GHS-TBT", 1, "manufacturer catalogue verified", "PROPOSED"),
        ("BR-P05", "cable housing", "JST", "GHR-05V-S", 2, "manufacturer catalogue verified", "PROPOSED"),
        ("BR-P06", "crimp contact", "JST", "SSHL-002T-P0.2", 10, "manufacturer catalogue verified", "PROPOSED"),
        ("BR-P07", "five-conductor cable", "SELECTION REQUIRED", "AWG30-26 within JST catalogue range", 1, "length, flex, insulation, colors and supplier unresolved", "SELECTION REQUIRED"),
        ("BR-P08", "SWD adapter PCB", "PROJECT-OWNED", "native layout and released fabrication data required", 1, "not yet designed; schematic contact map is not a PCB", "SELECTION REQUIRED"),
        ("BR-P09", "logic-only target supply", "SELECTION REQUIRED", "isolated/current-limited supply compatible with received controller", 1, "voltage/current/grounding/protection unresolved", "SELECTION REQUIRED"),
    ]
    return [common({"item_id": i, "function": fn, "manufacturer": m, "candidate_order_code": p, "quantity": q, "evidence_or_gap": e, "selection_state": s, "procurement_released": "NO"}) for i, fn, m, p, q, e, s in data]


def freeze_rows(bindings: list[dict[str, object]]) -> list[dict[str, object]]:
    firmware = json.loads((WHOLE / "firmware/hr30-motion-controller-p0.1/firmware-status.json").read_text(encoding="utf-8"))
    data = [
        ("BR-C01", "MCU target", "STM32H743ZIT6", "FROZEN BY TARGET BUILD"),
        ("BR-C02", "profile", "FIRST_POWER_NO_MOTION", "FROZEN BY TARGET BUILD"),
        ("BR-C03", "ELF SHA-256", firmware["stm32_target_elf_sha256"], "FROZEN INPUT; UNFLASHED"),
        ("BR-C04", "BIN SHA-256", firmware["stm32_target_bin_sha256"], "FROZEN INPUT; UNFLASHED"),
        ("BR-C05", "configuration binding SHA-256", firmware["stm32_target_configuration_binding_sha256"], "FROZEN INPUT"),
        ("BR-C06", "configuration word", "0x6764f016", "FROZEN INPUT"),
        ("BR-C07", "probe", "STLINK-V3MINIE", "PROPOSED; RECEIPT REQUIRED"),
        ("BR-C08", "programmer", "STM32CubeProgrammer v2.23.0", "PROPOSED; INSTALLED VERSION RECORD REQUIRED"),
    ]
    return [common({"configuration_id": i, "parameter": p, "value": v, "state": s, "source_binding_set_sha256": hashlib.sha256("".join(str(r["sha256"]) for r in bindings).encode()).hexdigest()}) for i, p, v, s in data]


def gate_rows() -> list[dict[str, object]]:
    data = [
        ("BR-G01", "Received target identity", "controller part/revision/serial and JDBG1 orientation photographed and checked against ECAD"),
        ("BR-G02", "Adapter and cable acceptance", "native PCB released; continuity, shorts, orientation, retention and pin-one inspections pass"),
        ("BR-G03", "Logic supply acceptance", "voltage, current limit, isolation/reference, protection and wiring approved for received board"),
        ("BR-G04", "No-actuator boundary", "all carrier, actuator-power, actuator-bus, precharge and action connectors physically absent"),
        ("BR-G05", "Tool/configuration identity", "CubeProgrammer version, probe serial, target ELF/BIN/configuration hashes recorded"),
        ("BR-G06", "Unpowered continuity", "TVCC sense, SWDIO, SWCLK, NRST and both grounds match the contact map; GNDDETECT unresolved contact remains open"),
        ("BR-G07", "Controlled flash and verify", "one approved operator downloads and verifies the frozen ELF without option-byte writes or mass erase"),
        ("BR-G08", "Boot-state measurement", "all direction pins low; precharge/action-ready inactive; UART clocks disabled; heartbeat/fault signals match plan"),
        ("BR-G09", "Fault-injection HIL", "permit sequence and dropout latch fault, withdraw heartbeat and leave every motion output inactive"),
        ("BR-G10", "Independent disposition", "controls/electrical reviewers accept evidence against exact hashes; no further stage is implied"),
    ]
    return [common({"gate_id": i, "gate": gate, "objective_evidence": evidence, "completion_record": "NONE", "pass_fail": "NOT EXECUTED"}) for i, gate, evidence in data]


def command_rows() -> list[dict[str, object]]:
    data = [
        ("BR-CMD01", "inventory", "STM32_Programmer_CLI --version", "record exact installed version; no target connected"),
        ("BR-CMD02", "probe discovery", "STM32_Programmer_CLI -l", "record ST-LINK serial/firmware; target still unpowered"),
        ("BR-CMD03", "connect under reset", "STM32_Programmer_CLI -c port=SWD mode=UR reset=HWrst", "run only after BR-G01 through BR-G06 pass"),
        ("BR-CMD04", "download and verify", "STM32_Programmer_CLI -c port=SWD mode=UR reset=HWrst -d <FROZEN_ELF_ABSOLUTE_PATH> -v", "template from official workflow; confirm syntax in installed v2.23.0 before execution"),
        ("BR-CMD05", "post-flash readback", "SELECTION REQUIRED - approved non-mutating readback command", "do not invent address/range; bind to approved target review"),
    ]
    return [common({"command_id": i, "stage": stage, "command_template": command, "rule": rule, "executed_by": "UNASSIGNED", "timestamp": "NOT RECORDED", "return_code": "NONE", "evidence_path": "NONE"}) for i, stage, command, rule in data]


def measurement_rows() -> list[dict[str, object]]:
    data = [
        ("BR-T01", "target supply voltage before connection", "V", "SELECTION REQUIRED"),
        ("BR-T02", "logic-only steady current", "A", "SELECTION REQUIRED"),
        ("BR-T03", "logic-only inrush/current-limit response", "A/ms", "SELECTION REQUIRED"),
        ("BR-T04", "reset to all eight direction pins low", "ms", "SELECTION REQUIRED; include reset gap"),
        ("BR-T05", "UART peripheral clocks/register state", "register/readback", "all disabled; physical review required"),
        ("BR-T06", "heartbeat edge interval", "ms", "candidate nominal 100 ms; acceptance tolerance SELECTION REQUIRED"),
        ("BR-T07", "heartbeat full period", "ms", "candidate nominal 200 ms; acceptance tolerance SELECTION REQUIRED"),
        ("BR-T08", "precharge request", "V", "inactive level; exact voltage limit SELECTION REQUIRED"),
        ("BR-T09", "action-ready", "V", "inactive level; exact voltage limit SELECTION REQUIRED"),
        ("BR-T10", "fault diagnostic healthy/fault", "V", "polarity follows ECAD/firmware; exact voltage limits SELECTION REQUIRED"),
        ("BR-T11", "controller temperature", "degC", "SELECTION REQUIRED"),
        ("BR-T12", "all actuator-carrier interfaces", "inspection", "physically disconnected throughout"),
    ]
    return [common({"measurement_id": i, "measurement": m, "unit": u, "candidate_acceptance": a, "instrument_id": "UNASSIGNED", "calibration_due": "UNRECORDED", "measured_value": "NONE", "evidence_path": "NONE", "pass_fail": "NOT EXECUTED"}) for i, m, u, a in data]


def fault_rows() -> list[dict[str, object]]:
    data = [
        ("BR-F01", "boot with permit low", "after three valid samples enter SAFE_HOLD; heartbeat may run; every motion/precharge/action output inactive"),
        ("BR-F02", "apply permit high after SAFE_HOLD", "PERMIT_OBSERVED_NO_MOTION; still no torque, bus TX, precharge or action-ready"),
        ("BR-F03", "remove permit after observation", "latch fault; heartbeat low; fault diagnostic high; every motion output remains inactive"),
        ("BR-F04", "reset with permit high", "must not clear latched fault or command motion"),
        ("BR-F05", "reset with permit low", "returns through boot hold with all outputs inactive; no autonomous motion retry"),
        ("BR-F06", "interrupt debugger or host process", "target remains deterministic; loss of debug cannot create motion or precharge request"),
    ]
    return [common({"fault_id": i, "injected_condition": condition, "required_response": response, "measured_response": "NONE", "pass_fail": "NOT EXECUTED", "evidence_path": "NONE"}) for i, condition, response in data]


def hold_rows() -> list[dict[str, object]]:
    data = [
        ("BR-H01", "received motion-controller PCB", "serial/revision inspection against native PCB and BOM"),
        ("BR-H02", "native SWD adapter PCB and cable", "released layout/fabrication data, assembled cable, pin-one and continuity evidence"),
        ("BR-H03", "logic-only power source", "exact supply/protection/current-limit/reference selection and review"),
        ("BR-H04", "GNDDETECT disposition", "confirmed ST documentation and approved adapter connection/no-connect rule"),
        ("BR-H05", "installed CubeProgrammer and probe", "version, serial, probe firmware and receipt record"),
        ("BR-H06", "flash and verify", "executed log against frozen ELF/BIN/configuration hashes"),
        ("BR-H07", "reset/GPIO/UART physical evidence", "oscilloscope/register captures including reset gap and eight direction pins"),
        ("BR-H08", "fault-injection HIL", "all six cases executed with raw traces and zero actuator connections"),
        ("BR-H09", "physical torque state", "remains unverified; software zero masks are not physical feedback"),
        ("BR-H10", "independent release disposition", "controls and electrical reviewers sign identical evidence set"),
        ("BR-H11", "next-stage powered-work authority", "separate first-energization gates; bring-up completion alone grants none"),
    ]
    return [common({"hold_id": i, "unresolved_item": item, "closure_evidence": evidence, "state": "OPEN"}) for i, item, evidence in data]


def debug_svg() -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="640" viewBox="0 0 1280 640" role="img" aria-labelledby="t d"><title id="t">HR-30 controlled SWD path</title><desc id="d">A separately powered controller connects through JDBG1 and a project adapter to STLINK-V3MINIE. Actuator carriers remain disconnected.</desc><style>text{{font:600 18px system-ui;fill:#12263a}}.h{{font-size:28px;font-weight:900}}.b{{fill:#fff;stroke:#0b4f91;stroke-width:4}}.hold{{fill:#fff0b5;stroke:#982520;stroke-width:4}}.a{{stroke:#0b4f91;stroke-width:4;fill:none;marker-end:url(#m)}}.s{{font-size:15px}}</style><defs><marker id="m" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0 0L0 6L9 3z" fill="#0b4f91"/></marker></defs><text class="h" x="45" y="48">No-actuator SWD bring-up boundary</text><rect class="b" x="45" y="120" width="235" height="180" rx="18"/><text x="75" y="170">STLINK-V3MINIE</text><text class="s" x="75" y="205">CN4 / STDC14</text><text class="s" x="75" y="235">does not power target</text><rect class="hold" x="375" y="120" width="235" height="180" rx="18"/><text x="410" y="170">Project adapter</text><text class="s" x="410" y="205">native PCB required</text><text class="s" x="410" y="235">6 mapped conductors</text><text class="s" x="410" y="265">GNDDETECT open</text><rect class="b" x="705" y="120" width="235" height="180" rx="18"/><text x="750" y="170">JDBG1</text><text class="s" x="740" y="205">JST GH 5-contact</text><text class="s" x="740" y="235">TVCC sense + SWD</text><rect class="b" x="1035" y="120" width="200" height="180" rx="18"/><text x="1062" y="170">STM32H743</text><text class="s" x="1062" y="205">separate logic supply</text><text class="s" x="1062" y="235">FIRST_POWER_</text><text class="s" x="1062" y="258">NO_MOTION</text><path class="a" d="M280 210H375"/><path class="a" d="M610 210H705"/><path class="a" d="M940 210H1035"/><rect class="hold" x="705" y="410" width="530" height="150" rx="18"/><text x="750" y="455">Actuator carriers, buses and power</text><text x="750" y="492">PHYSICALLY DISCONNECTED</text><text class="s" x="750" y="525">No software flag substitutes for this boundary.</text><path class="a" d="M1135 300V410" stroke-dasharray="12 10"/><text class="s" x="905" y="375">no connection</text></svg>'''


def render() -> str:
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 STM32 bring-up</title><style>:root{{--deep:#071d36;--blue:#0b4f91;--sky:#d9f2ff;--gold:#f2b91d;--paper:#f7fbff;--ink:#142a40;--line:#82c4e6;--red:#982520}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.55 system-ui,Segoe UI,sans-serif}}header,main,footer{{padding:clamp(24px,5vw,64px) max(18px,calc((100vw - 1280px)/2))}}header,footer{{background:linear-gradient(135deg,var(--deep),var(--blue));color:white}}h1{{font-size:clamp(38px,6vw,70px);line-height:1.04;max-width:18ch}}h2{{font-size:clamp(28px,4vw,44px)}}h3{{font-size:22px}}.warning{{background:var(--gold);color:#17243a;border:3px solid #805600;padding:16px;font-weight:900}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:18px}}article,.panel{{background:white;border:2px solid var(--line);border-radius:16px;padding:19px}}.metric{{font-size:clamp(34px,5vw,54px);font-weight:900;color:var(--blue)}}.hold{{border-color:var(--red)}}.scroll{{overflow:auto;border:2px solid var(--line);border-radius:16px;background:white}}object{{display:block;width:100%;min-width:900px}}a{{color:#075b9b;font-weight:800}}code{{font-size:16px}}small{{font-size:14px}}@media(max-width:560px){{body{{font-size:16px}}}}</style></head><body><header><div class="warning">{html.escape(WARNING)}</div><p>HR-30 whole-body P0.1</p><h1>Flash the brain without connecting the muscles.</h1><p>This traveler binds the built STM32 image to an exact SWD contact map, proposed adapter BOM, measurements and fault injections. Every physical result is still blank.</p></header><main><section class="grid"><article><div class="metric">5</div><p>target debug contacts</p></article><article><div class="metric">10</div><p>bring-up release gates</p></article><article><div class="metric">12</div><p>planned measurements</p></article><article class="hold"><div class="metric">0</div><p>flashes, HIL runs or authorities</p></article></section><section><h2>Physical boundary</h2><div class="scroll"><object data="debug-path.svg" type="image/svg+xml" aria-label="Controlled SWD debug path"></object></div></section><section><h2>Use the records in order</h2><div class="grid"><article><h3>1. Freeze</h3><p><a href="configuration-freeze.csv">Bind the target and hashes</a>, then inspect <a href="source-binding.csv">source identity</a>.</p></article><article><h3>2. Build the fixture</h3><p>Use the <a href="debug-path-contact-map.csv">contact map</a> and <a href="debug-adapter-bom.csv">candidate BOM</a>. The adapter PCB is still an open design.</p></article><article><h3>3. Release the operation</h3><p>Close the <a href="bringup-gate-register.csv">ten gates</a>. A command template is not authority.</p></article><article><h3>4. Record raw evidence</h3><p>Complete the <a href="measurement-plan.csv">measurements</a> and <a href="fault-injection-plan.csv">fault injections</a>; preserve logs and traces.</p></article></div></section><section class="panel hold"><h2>What this still does not prove</h2><p>The target is unflashed. The adapter PCB and cable do not exist. Reset-state voltages, UART inactivity, heartbeat timing, physical torque state and permit-dropout behavior are unmeasured. This package grants no connection, powered-test, motion, safety or energization authority.</p><p><a href="bringup-status.json">Machine-readable status</a> · <a href="command-plan.csv">Command plan</a> · <a href="open-holds.csv">Open holds</a> · <a href="primary-source-register.csv">Primary sources</a></p></section></main><footer>{html.escape(WARNING)}</footer></body></html>'''


def integrate_root(status: dict[str, object]) -> None:
    path = WHOLE / "package-status.json"
    root_status = json.loads(path.read_text(encoding="utf-8"))
    root_status.update({
        "stm32_target_bringup_package_present": True,
        "stm32_target_bringup_gate_count": 10,
        "stm32_target_bringup_measurement_count": 12,
        "stm32_target_bringup_flash_executed": False,
        "stm32_target_bringup_hil_executed": False,
        "stm32_target_bringup_approved": False,
        "connection_authority": False,
        "powered_test_authority": False,
        "motion_authority": False,
        "energization_authority": False,
    })
    path.write_text(json.dumps(root_status, indent=2) + "\n", encoding="utf-8")

    readme = WHOLE / "README.md"
    text = readme.read_text(encoding="utf-8")
    start, end = "<!-- HR30-STM32-BRINGUP-P01-README-START -->", "<!-- HR30-STM32-BRINGUP-P01-README-END -->"
    if start in text and end in text:
        text = text.split(start, 1)[0] + text.split(end, 1)[1]
    block = f'''{start}\n## STM32 no-actuator bring-up\n\nThe [interactive target bring-up guide](firmware/stm32-target-bringup-p0.1/index.html) binds the reproducible STM32H743 image to the controller's exact five-contact SWD boundary, a proposed STLINK-V3MINIE adapter/cable BOM, ten release gates, twelve measurements and six fault injections. The target remains unflashed; the adapter PCB remains unbuilt; all physical results and work authority remain open.\n{end}\n'''
    marker = "<!-- HR30-FIRST-ENERGIZATION-P01-README-START -->"
    readme.write_text(text.replace(marker, block + marker), encoding="utf-8", newline="\n")

    page = WHOLE / "index.html"
    text = page.read_text(encoding="utf-8")
    start, end = "<!-- HR30-STM32-BRINGUP-P01-START -->", "<!-- HR30-STM32-BRINGUP-P01-END -->"
    if start in text and end in text:
        text = text.split(start, 1)[0] + text.split(end, 1)[1]
    section = f'''{start}<section id="stm32-bringup"><h2>The target now has a no-actuator bring-up path</h2><div class="grid"><article class="card"><div class="metric">5</div><p>exact JDBG1 debug contacts</p></article><article class="card"><div class="metric">10</div><p>controlled release gates</p></article><article class="card"><div class="metric">12</div><p>planned physical measurements</p></article><article class="card hold"><div class="metric">0</div><p>flashes or HIL executions</p></article></div><p><a href="firmware/stm32-target-bringup-p0.1/index.html">Open the interactive STM32 target bring-up guide</a>. Actuator carriers remain physically disconnected and all authority remains withheld.</p></section>{end}'''
    marker = "<!-- HR30-FIRST-ENERGIZATION-P01-START -->"
    page.write_text(text.replace(marker, section + marker), encoding="utf-8", newline="\n")


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    sources, bindings = primary_sources(), source_bindings()
    contacts, bom = debug_contacts(), bom_rows()
    freezes, gates = freeze_rows(bindings), gate_rows()
    commands, measurements = command_rows(), measurement_rows()
    faults, holds = fault_rows(), hold_rows()
    datasets = {
        "primary-source-register.csv": sources,
        "source-binding.csv": bindings,
        "debug-path-contact-map.csv": contacts,
        "debug-adapter-bom.csv": bom,
        "configuration-freeze.csv": freezes,
        "bringup-gate-register.csv": gates,
        "command-plan.csv": commands,
        "measurement-plan.csv": measurements,
        "fault-injection-plan.csv": faults,
        "open-holds.csv": holds,
    }
    for name, rows in datasets.items():
        write_csv(OUT / name, rows)
    status = {
        "identifier": IDENTIFIER,
        "warning": WARNING,
        "primary_source_count": len(sources),
        "source_binding_count": len(bindings),
        "mapped_debug_contact_count": 6,
        "unresolved_debug_contact_count": 1,
        "candidate_bom_item_count": len(bom),
        "bringup_gate_count": len(gates),
        "measurement_count": len(measurements),
        "fault_injection_count": len(faults),
        "open_hold_count": len(holds),
        "stm32_target_binary_built": True,
        "stm32_target_binary_flashed": False,
        "adapter_pcb_designed": False,
        "adapter_cable_built": False,
        "logic_supply_selected": False,
        "physical_gate_executed_count": 0,
        "measurement_executed_count": 0,
        "fault_injection_executed_count": 0,
        "target_hil_executed": False,
        "physical_torque_disabled_verified": False,
        "functional_safety_credit": False,
        "connection_authority": False,
        "powered_test_authority": False,
        "motion_authority": False,
        "energization_authority": False,
    }
    (OUT / "bringup-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    (OUT / "debug-path.svg").write_text(debug_svg(), encoding="utf-8", newline="\n")
    (OUT / "index.html").write_text(render(), encoding="utf-8", newline="\n")
    (OUT / "README.md").write_text(f"# HR-30 STM32 target bring-up P0.1\n\n**{WARNING}**\n\nThis is an unexecuted, no-actuator SWD flash/measurement/fault-injection traveler tied to the existing STM32H743 target artifacts. The adapter PCB is still an open design; use [index.html](index.html) for the interactive guide.\n", encoding="utf-8", newline="\n")
    shutil.copy2(Path(__file__), OUT / "stm32-target-bringup-source.py")
    write_csv(OUT / "file-manifest.csv", [{"path": p.relative_to(OUT).as_posix(), "bytes": p.stat().st_size, "sha256": sha(p), "warning": WARNING} for p in sorted(OUT.rglob("*")) if p.is_file() and p.name != "file-manifest.csv"])
    if RELEASE.exists():
        shutil.rmtree(RELEASE)
    shutil.copytree(OUT, RELEASE)
    integrate_root(status)
    import generate_hr30_system_package_p01 as system_package
    system_package.refresh_manifest_and_release()
    print(json.dumps(status, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
