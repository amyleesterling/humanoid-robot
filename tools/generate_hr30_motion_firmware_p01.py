"""Generate the HR-30 deterministic FIRST_POWER_NO_MOTION firmware package."""

from __future__ import annotations

import csv
import hashlib
import html
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WHOLE = ROOT / "hr30" / "whole-body-p0.1"
SOURCE = ROOT / "firmware" / "hr30-motion-controller"
OUT = WHOLE / "firmware" / "hr30-motion-controller-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / "firmware" / "hr30-motion-controller-p0.1"
WARNING = "PRELIMINARY - HOST AND UNFLASHED TARGET NO-MOTION EVIDENCE ONLY - NOT APPROVED FOR CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
AUTHORITY = "NO CONNECTION, POWERED-TEST, MOTION, OR ENERGIZATION AUTHORITY"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise RuntimeError(f"refusing empty CSV: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def axis_rows() -> list[dict[str, object]]:
    commission = read_csv(WHOLE / "electrical/axis-commissioning-station-p0.1/axis-commissioning-matrix.csv")
    binding = {row["axis_id"]: row for row in read_csv(WHOLE / "actuator-bus-axis-binding.csv")}
    if len(commission) != 25 or set(binding) != {row["axis_id"] for row in commission}:
        raise RuntimeError("25-axis commissioning/bus bindings do not agree")
    return [{
        "axis_index": index,
        "axis_id": row["axis_id"],
        "provisional_global_id": row["proposed_global_id"],
        "bus_id": binding[row["axis_id"]]["bus_id"],
        "family": row["family"],
        "expected_first_readback": row["required_initial_readback"],
        "torque_command": "COMPILE-TIME DISABLED",
        "bus_transmit": "COMPILE-TIME DISABLED",
        "id_write": "PROHIBITED",
        "authority": AUTHORITY,
        "warning": WARNING,
    } for index, row in enumerate(commission)]


def bus_rows() -> list[dict[str, object]]:
    topology = read_csv(WHOLE / "actuator-bus-topology.csv")
    pins = read_csv(WHOLE / "electrical/motion-controller-p0.1/uart-pin-map.csv")
    by_bus: dict[str, list[dict[str, str]]] = {}
    for row in pins:
        by_bus.setdefault(row["bus_id"], []).append(row)
    if len(topology) != 8 or set(by_bus) != {row["bus_id"] for row in topology}:
        raise RuntimeError("eight-bus topology/UART bindings do not agree")
    result = []
    for index, row in enumerate(topology):
        signals = by_bus[row["bus_id"]]
        result.append({
            "bus_index": index,
            "bus_id": row["bus_id"],
            "protocol": row["protocol"],
            "axis_count": row["axis_count"],
            "mcu_signal_pins": "; ".join(f"{s['signal']}={s['mcu_port']}/LQFP144-{s['lqfp144_package_pin']}" for s in signals),
            "transmit_enable": "COMPILE-TIME DISABLED",
            "unexpected_tx_response": "LATCHED FAULT",
            "authority": AUTHORITY,
            "warning": WARNING,
        })
    return result


def io_rows() -> list[dict[str, str]]:
    rows = read_csv(WHOLE / "electrical/motion-controller-p0.1/control-gpio-map.csv")
    if len(rows) != 10:
        raise RuntimeError("ten control GPIO bindings required")
    return [{**row, "first_power_boot_state": (
        "INPUT / OBSERVE ONLY" if "INPUT" in row["deterministic_role"] else "INACTIVE BEFORE PERIPHERAL CONFIGURATION"
    ), "authority": AUTHORITY} for row in rows]


def action_rows() -> list[dict[str, str]]:
    schema = json.loads((WHOLE / "structured-action-request.schema.json").read_text(encoding="utf-8"))
    actions = schema["properties"]["action"]["enum"]
    if len(actions) != 10:
        raise RuntimeError("action schema drift")
    return [{
        "action": action,
        "first_power_profile_disposition": "ACCEPT AS NO-OP / ZERO OUTPUT" if action == "STOP_REQUEST" else "REJECT PROFILE_LOCKED",
        "torque_enable_mask": "0x00000000",
        "bus_tx_enable_mask": "0x0000",
        "motion_possible": "NO",
        "warning": WARNING,
    } for action in actions]


def fault_rows() -> list[dict[str, str]]:
    data = [
        ("CONFIGURATION", "configuration digest mismatch", "latched fault; outputs inactive"),
        ("UNEXPECTED_TORQUE", "any of 25 torque-enable feedback bits set", "latched fault; outputs inactive"),
        ("UNEXPECTED_BUS_TX", "any of eight bus-transmit observations set", "latched fault; outputs inactive"),
        ("PERMIT_DROPOUT", "hardwired permit falls after observation", "latched fault; outputs inactive"),
        ("CLOCK_ROLLBACK", "monotonic scheduler time decreases", "latched fault; outputs inactive"),
        ("INPUT_INVALID", "controller or input pointer invalid", "latched fault when controller storage is available"),
    ]
    return [{"fault": f, "trigger": t, "response": r, "reset_precondition": "permit low; torque disabled; bus TX absent; explicit reset", "target_hil": "NOT EXECUTED", "warning": WARNING} for f, t, r in data]


def hold_rows() -> list[dict[str, str]]:
    data = [
        ("FW-H01", "STM32H743 startup and fail-low GPIO behavior not physically verified", "flash received target; capture reset-to-main GPIO, clock and heartbeat traces; inject startup faults"),
        ("FW-H02", "reproducible target binary lacks independent release approval", "independent target-code review plus signed ELF/BIN/configuration hashes"),
        ("FW-H03", "hardware-in-loop boot and GPIO behavior", "received controller, oscilloscope traces and fault injection"),
        ("FW-H04", "DYNAMIXEL read-only transport", "approved bus timing, packet implementation and proof of zero writes"),
        ("FW-H05", "structured-action authentication transport", "key provisioning, replay storage, SPI framing and security review"),
        ("FW-H06", "physical torque-disable feedback", "defined feedback source and verified 25-axis readback"),
        ("FW-H07", "scheduler and watchdog timing", "WCET, clock/interrupt behavior, jitter and target watchdog evidence"),
        ("FW-H08", "functional-safety allocation", "qualified SRS/risk allocation and validation; this firmware receives zero safety credit"),
        ("FW-H09", "controls review and approved hash", "independent source review plus signed identical build/configuration record"),
        ("FW-H10", "connection/powered work", "all FER-G01 through FER-G12 completed and separately authorized"),
        ("FW-H11", "RS-485 direction pins lack a verified reset-gap hardware pull-down", "as-built carrier inspection plus reset-to-firmware oscilloscope proof or approved fail-low hardware revision"),
    ]
    return [{"hold_id": i, "unresolved_item": item, "closure_evidence": evidence, "state": "OPEN - NOT EXECUTED", "authority": AUTHORITY, "warning": WARNING} for i, item, evidence in data]


def state_svg() -> str:
    return '''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="520" viewBox="0 0 1200 520" role="img" aria-labelledby="title desc"><title id="title">HR-30 first-power no-motion state machine</title><desc id="desc">Boot hold advances to safe hold and permit-observed no-motion. Any fault reaches a latched fault. Reset is possible only with permit low and all outputs inactive.</desc><style>text{font:600 18px system-ui;fill:#102a43}.title{font-size:30px;font-weight:900}.box{fill:#fff;stroke:#0b4f91;stroke-width:4}.fault{fill:#fff0b5;stroke:#982520}.arrow{stroke:#0b4f91;stroke-width:4;fill:none;marker-end:url(#m)}.label{font-size:15px}</style><defs><marker id="m" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#0b4f91"/></marker></defs><text class="title" x="45" y="50">FIRST_POWER_NO_MOTION</text><rect class="box" x="55" y="120" rx="18" width="235" height="120"/><text x="92" y="177">BOOT_HOLD</text><text class="label" x="82" y="207">3 valid samples; outputs 0</text><rect class="box" x="385" y="120" rx="18" width="235" height="120"/><text x="430" y="177">SAFE_HOLD</text><text class="label" x="423" y="207">permit low; outputs 0</text><rect class="box" x="715" y="120" rx="18" width="390" height="120"/><text x="760" y="167">PERMIT_OBSERVED</text><text class="label" x="760" y="200">still no torque, bus TX, precharge or motion</text><rect class="box fault" x="385" y="350" rx="18" width="390" height="120"/><text x="490" y="407">LATCHED_FAULT</text><text class="label" x="450" y="440">reset only de-energized; outputs remain 0</text><path class="arrow" d="M290 180H385"/><text class="label" x="308" y="165">validated</text><path class="arrow" d="M620 180H715"/><text class="label" x="642" y="165">permit</text><path class="arrow" d="M200 240Q250 410 385 410"/><path class="arrow" d="M500 240V350"/><path class="arrow" d="M910 240Q870 410 775 410"/><text class="label" x="810" y="330">any monitored fault</text><path class="arrow" d="M385 445Q300 470 310 250Q315 210 385 210"/><text class="label" x="95" y="485">explicit reset + permit low + zero observed activity</text></svg>'''


def render(status: dict[str, object], actions: list[dict[str, str]], faults: list[dict[str, str]]) -> str:
    action_cards = "".join(f"<article><h3>{html.escape(r['action'])}</h3><p>{html.escape(r['first_power_profile_disposition'])}</p></article>" for r in actions)
    fault_items = "".join(f"<li><b>{html.escape(r['fault'])}</b><span>{html.escape(r['trigger'])}</span><em>{html.escape(r['response'])}</em></li>" for r in faults)
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 no-motion firmware</title><style>:root{{--deep:#071d36;--blue:#0b4f91;--sky:#d9f2ff;--gold:#f2b91d;--paper:#f7fbff;--ink:#142a40;--line:#82c4e6;--red:#982520}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.55 system-ui,Segoe UI,sans-serif}}header,main,footer{{padding:clamp(24px,5vw,64px) max(18px,calc((100vw - 1280px)/2))}}header,footer{{background:linear-gradient(135deg,var(--deep),var(--blue));color:white}}h1{{font-size:clamp(38px,6vw,70px);line-height:1.04;max-width:19ch}}h2{{font-size:clamp(28px,4vw,44px)}}h3{{font-size:21px}}.warning{{background:var(--gold);color:#17243a;border:3px solid #805600;padding:16px;font-weight:900}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(235px,1fr));gap:18px}}article,.panel,li{{background:white;border:2px solid var(--line);border-radius:16px;padding:19px}}.metric{{font-size:clamp(34px,5vw,54px);font-weight:900;color:var(--blue)}}object{{display:block;width:100%;min-width:900px}}.scroll{{overflow:auto;border:2px solid var(--line);border-radius:16px;background:white}}ul{{display:grid;gap:12px;padding:0;list-style:none}}li{{display:grid;grid-template-columns:minmax(150px,.7fr) 1.4fr 1.4fr;gap:14px}}li em{{color:var(--red);font-style:normal}}a{{color:#075b9b;font-weight:800}}code{{font-size:16px}}small{{font-size:14px}}@media(max-width:650px){{body{{font-size:16px}}li{{grid-template-columns:1fr}}}}</style></head><body><header><div class="warning">{html.escape(WARNING)}</div><p>HR-30 whole-body P0.1</p><h1>The controller now boots with nowhere to move.</h1><p>This compiled deterministic core binds the 25-axis/eight-bus architecture while keeping every torque, transmit, precharge and action-ready output inactive.</p></header><main><section class="grid"><article><div class="metric">25</div><p>axis bits forced inactive</p></article><article><div class="metric">8</div><p>bus transmit paths forced inactive</p></article><article><div class="metric">2×</div><p>byte-identical host builds</p></article><article><div class="metric">0</div><p>target or physical HIL executions</p></article></section><section><h2>Fail-closed state machine</h2><div class="scroll"><object data="state-machine.svg" type="image/svg+xml" aria-label="No-motion controller state machine"></object></div></section><section><h2>Every structured action</h2><div class="grid">{action_cards}</div></section><section><h2>Latched software faults</h2><ul>{fault_items}</ul></section><section class="panel"><h2>What the evidence proves</h2><p>The portable C core compiles with warnings-as-errors, reproduces byte-for-byte across two clean host builds, and passes the committed vector runner. It proves source-level no-motion behavior for this host configuration only.</p><p><strong>It does not prove STM32 startup, target timing, bus behavior, GPIO polarity, HIL performance, safety integrity, or permission to connect or energize hardware.</strong></p><p><a href="firmware-status.json">Status</a> · <a href="axis-binding.csv">25-axis binding</a> · <a href="bus-binding.csv">eight buses</a> · <a href="action-disposition.csv">action gate</a> · <a href="fault-response.csv">faults</a> · <a href="output/host-p0.1/build-evidence.json">compiled evidence</a> · <a href="open-holds.csv">open holds</a></p></section></main><footer>{html.escape(WARNING)}</footer></body></html>'''


def render_target(status: dict[str, object], actions: list[dict[str, str]], faults: list[dict[str, str]]) -> str:
    action_cards = "".join(f"<article><h3>{html.escape(r['action'])}</h3><p>{html.escape(r['first_power_profile_disposition'])}</p></article>" for r in actions)
    fault_items = "".join(f"<li><b>{html.escape(r['fault'])}</b><span>{html.escape(r['trigger'])}</span><em>{html.escape(r['response'])}</em></li>" for r in faults)
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 no-motion firmware</title><style>:root{{--deep:#071d36;--blue:#0b4f91;--sky:#d9f2ff;--gold:#f2b91d;--paper:#f7fbff;--ink:#142a40;--line:#82c4e6;--red:#982520}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.55 system-ui,Segoe UI,sans-serif}}header,main,footer{{padding:clamp(24px,5vw,64px) max(18px,calc((100vw - 1280px)/2))}}header,footer{{background:linear-gradient(135deg,var(--deep),var(--blue));color:white}}h1{{font-size:clamp(38px,6vw,70px);line-height:1.04;max-width:19ch}}h2{{font-size:clamp(28px,4vw,44px)}}h3{{font-size:21px}}.warning{{background:var(--gold);color:#17243a;border:3px solid #805600;padding:16px;font-weight:900}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(235px,1fr));gap:18px}}article,.panel,li{{background:white;border:2px solid var(--line);border-radius:16px;padding:19px}}.metric{{font-size:clamp(34px,5vw,54px);font-weight:900;color:var(--blue)}}object{{display:block;width:100%;min-width:900px}}.scroll{{overflow:auto;border:2px solid var(--line);border-radius:16px;background:white}}ul{{display:grid;gap:12px;padding:0;list-style:none}}li{{display:grid;grid-template-columns:minmax(150px,.7fr) 1.4fr 1.4fr;gap:14px}}li em{{color:var(--red);font-style:normal}}a{{color:#075b9b;font-weight:800}}code{{font-size:16px}}small{{font-size:14px}}@media(max-width:650px){{body{{font-size:16px}}li{{grid-template-columns:1fr}}}}</style></head><body><header><div class="warning">{html.escape(WARNING)}</div><p>HR-30 whole-body P0.1</p><h1>The controller target now exists—with every motion path held inactive.</h1><p>The portable core and a reproducible STM32H743 image bind the 25-axis/eight-bus architecture while holding torque, UART clocks, direction pins, precharge and action-ready inactive.</p></header><main><section class="grid"><article><div class="metric">25</div><p>axis bits forced inactive</p></article><article><div class="metric">8</div><p>UART clocks disabled and direction pins low</p></article><article><div class="metric">2×</div><p>byte-identical host and target builds</p></article><article><div class="metric">0</div><p>target flashes or physical HIL executions</p></article></section><section><h2>Fail-closed state machine</h2><div class="scroll"><object data="state-machine.svg" type="image/svg+xml" aria-label="No-motion controller state machine"></object></div></section><section><h2>Every structured action</h2><div class="grid">{action_cards}</div></section><section><h2>Latched software faults</h2><ul>{fault_items}</ul></section><section class="panel"><h2>What the evidence proves</h2><p>The portable C core and freestanding Cortex-M7 target compile with warnings-as-errors, reproduce byte-for-byte across two clean builds, and pass compiled core and register-level MMIO vectors. The ELF contains the 166-entry vector table, project startup, fail-low GPIO initialization, polled 1 ms timebase and the 100 ms controller loop.</p><p><strong>The target has not been flashed. GPIO voltage and reset timing, UART inactivity, heartbeat timing, physical torque state and fault response still require oscilloscope and hardware-in-loop evidence. This build grants no safety credit or permission to connect or energize hardware.</strong></p><p><a href="firmware-status.json">Status</a> · <a href="axis-binding.csv">25-axis binding</a> · <a href="bus-binding.csv">eight buses</a> · <a href="action-disposition.csv">action gate</a> · <a href="fault-response.csv">faults</a> · <a href="output/host-p0.1/build-evidence.json">host evidence</a> · <a href="output/stm32h743-p0.1/build-evidence.json">target evidence</a> · <a href="open-holds.csv">open holds</a></p></section></main><footer>{html.escape(WARNING)}</footer></body></html>'''


def integrate_root(status: dict[str, object]) -> None:
    status_path = WHOLE / "package-status.json"
    root_status = json.loads(status_path.read_text(encoding="utf-8"))
    root_status.update({
        "hr30_no_motion_firmware_present": True,
        "hr30_no_motion_firmware_axis_count": 25,
        "hr30_no_motion_firmware_bus_count": 8,
        "hr30_no_motion_host_vectors_pass": True,
        "hr30_no_motion_stm32_target_built": True,
        "hr30_no_motion_stm32_target_flashed": False,
        "hr30_no_motion_target_hil_executed": False,
        "hr30_no_motion_firmware_approved": False,
        "motion_authority": False,
        "energization_authority": False,
    })
    status_path.write_text(json.dumps(root_status, indent=2) + "\n", encoding="utf-8")
    readme = WHOLE / "README.md"
    text = readme.read_text(encoding="utf-8")
    start, end = "<!-- HR30-NO-MOTION-FW-P01-README-START -->", "<!-- HR30-NO-MOTION-FW-P01-README-END -->"
    if start in text and end in text:
        text = text.split(start, 1)[0] + text.split(end, 1)[1]
    block = f'''{start}\n## Deterministic no-motion firmware\n\nThe [HR-30 no-motion firmware guide](firmware/hr30-motion-controller-p0.1/index.html) binds all 25 axes and eight buses to a compiled `FIRST_POWER_NO_MOTION` state machine. Every torque-enable, bus-transmit, precharge and action-ready output remains zero; all motion requests are rejected and STOP is a no-op. Two clean host builds and two clean freestanding STM32H743 builds are byte-identical, and the compiled core/MMIO vector suites pass. The target is unflashed; HIL, physical timing, reset-state proof and qualified approval remain open, so this creates no powered-work or motion authority.\n{end}\n'''
    marker = "<!-- HR30-FIRST-ENERGIZATION-P01-README-START -->"
    readme.write_text(text.replace(marker, block + marker), encoding="utf-8", newline="\n")
    page = WHOLE / "index.html"
    text = page.read_text(encoding="utf-8")
    start, end = "<!-- HR30-NO-MOTION-FW-P01-START -->", "<!-- HR30-NO-MOTION-FW-P01-END -->"
    if start in text and end in text:
        text = text.split(start, 1)[0] + text.split(end, 1)[1]
    section = f'''{start}<section id="no-motion-firmware"><h2>The whole-body controller now has a real unflashed STM32 target</h2><div class="grid"><article class="card pass"><div class="metric">25</div><p>axis torque bits forced inactive</p></article><article class="card pass"><div class="metric">8</div><p>UART clocks disabled and direction pins low</p></article><article class="card pass"><h3>Reproducible host and target builds</h3><p>The freestanding Cortex-M7 ELF/BIN and compiled vector evidence reproduce byte-for-byte.</p></article><article class="card hold"><h3>Flash and HIL remain open</h3><p>The binary has never run on hardware; no connection or powered-work authority follows.</p></article></div><p><a href="firmware/hr30-motion-controller-p0.1/index.html">Open the deterministic no-motion firmware guide</a>.</p></section>{end}'''
    marker = "<!-- HR30-FIRST-ENERGIZATION-P01-START -->"
    page.write_text(text.replace(marker, section + marker), encoding="utf-8", newline="\n")


def main() -> int:
    required = [
        SOURCE / "include/hr30_motion.h", SOURCE / "src/hr30_motion.c",
        SOURCE / "tests/hr30_motion_vector_runner.c", SOURCE / "platform/stm32h743/hr30_stm32h743_io.h",
        SOURCE / "output/host-p0.1/build-evidence.json", SOURCE / "output/host-p0.1/hr30_motion_vector_runner.exe",
        SOURCE / "tests/hr30_stm32h743_mmio_runner.c", SOURCE / "platform/stm32h743/hr30_stm32h743_target.c",
        SOURCE / "platform/stm32h743/startup_hr30_stm32h743.S", SOURCE / "platform/stm32h743/stm32h743zit6_hr30.ld",
        SOURCE / "target-toolchain-lock.json", SOURCE / "output/stm32h743-p0.1/build-evidence.json",
        SOURCE / "output/stm32h743-p0.1/hr30-motion-controller-stm32h743.elf",
    ]
    for path in required:
        if not path.is_file():
            raise FileNotFoundError(path)
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    for directory in ["include", "src", "tests", "platform", "output"]:
        shutil.copytree(SOURCE / directory, OUT / directory)
    shutil.copy2(SOURCE / "target-toolchain-lock.json", OUT / "target-toolchain-lock.json")
    evidence = json.loads((OUT / "output/host-p0.1/build-evidence.json").read_text(encoding="utf-8-sig"))
    if not evidence["two_clean_builds_byte_identical"] or evidence["vector_result"] != "PASS":
        raise RuntimeError("compiled host evidence did not pass")
    target_evidence = json.loads((OUT / "output/stm32h743-p0.1/build-evidence.json").read_text(encoding="utf-8-sig"))
    if not target_evidence["two_clean_target_builds_byte_identical"] or target_evidence["core_compiled_vectors"] != "PASS" or target_evidence["mmio_compiled_vectors"] != "PASS":
        raise RuntimeError("compiled STM32 target evidence did not pass")
    axes, buses, ios = axis_rows(), bus_rows(), io_rows()
    actions, faults, holds = action_rows(), fault_rows(), hold_rows()
    write_csv(OUT / "axis-binding.csv", axes)
    write_csv(OUT / "bus-binding.csv", buses)
    write_csv(OUT / "io-binding.csv", ios)
    write_csv(OUT / "action-disposition.csv", actions)
    write_csv(OUT / "fault-response.csv", faults)
    write_csv(OUT / "open-holds.csv", holds)
    sources = []
    for role, path in [
        ("motion-controller native ECAD GPIO", WHOLE / "electrical/motion-controller-p0.1/control-gpio-map.csv"),
        ("motion-controller native ECAD UART", WHOLE / "electrical/motion-controller-p0.1/uart-pin-map.csv"),
        ("25-axis bus binding", WHOLE / "actuator-bus-axis-binding.csv"),
        ("eight-bus topology", WHOLE / "actuator-bus-topology.csv"),
        ("25-axis commissioning matrix", WHOLE / "electrical/axis-commissioning-station-p0.1/axis-commissioning-matrix.csv"),
        ("structured action schema", WHOLE / "structured-action-request.schema.json"),
        ("portable C state machine", SOURCE / "src/hr30_motion.c"),
        ("portable C interface", SOURCE / "include/hr30_motion.h"),
        ("compiled host evidence", SOURCE / "output/host-p0.1/build-evidence.json"),
        ("STM32 target source", SOURCE / "platform/stm32h743/hr30_stm32h743_target.c"),
        ("STM32 startup", SOURCE / "platform/stm32h743/startup_hr30_stm32h743.S"),
        ("STM32 linker script", SOURCE / "platform/stm32h743/stm32h743zit6_hr30.ld"),
        ("STM32 toolchain lock", SOURCE / "target-toolchain-lock.json"),
        ("compiled STM32 target evidence", SOURCE / "output/stm32h743-p0.1/build-evidence.json"),
        ("firmware generator", Path(__file__)),
        ("host build script", ROOT / "tools/build_hr30_motion_host_runner.ps1"),
        ("STM32 target build script", ROOT / "tools/build_hr30_motion_stm32_target.ps1"),
    ]:
        sources.append({"role": role, "path": path.relative_to(ROOT).as_posix(), "sha256": sha(path), "warning": WARNING})
    write_csv(OUT / "source-binding.csv", sources)
    status = {
        "identifier": "HR30-MOTION-FIRST-POWER-NO-MOTION-P0.1", "warning": WARNING,
        "profile": "FIRST_POWER_NO_MOTION", "axis_count": len(axes), "bus_count": len(buses),
        "structured_action_count": len(actions), "fault_count": len(faults), "open_hold_count": len(holds),
        "host_compiled": True, "host_vector_result": "PASS", "two_clean_host_builds_byte_identical": True,
        "torque_enable_mask_constant": "0x00000000", "bus_tx_enable_mask_constant": "0x0000",
        "precharge_request_constant": False, "action_ready_constant": False,
        "all_motion_actions_rejected": True, "stop_request_is_no_op": True,
        "stm32_target_binary_built": True, "stm32_target_build_reproducible": True,
        "stm32_target_core_vectors_pass": True, "stm32_target_mmio_vectors_pass": True,
        "stm32_target_elf_sha256": target_evidence["artifacts"][0]["sha256"],
        "stm32_target_bin_sha256": target_evidence["artifacts"][1]["sha256"],
        "stm32_target_configuration_binding_sha256": target_evidence["configuration_binding_sha256"],
        "stm32_target_binary_flashed": False, "target_hil_executed": False,
        "oscilloscope_boot_state_verified": False, "physical_uart_write_path_audited": False,
        "physical_torque_disabled_verified": False, "firmware_approved": False,
        "functional_safety_credit": False, "connection_authority": False, "powered_test_authority": False,
        "motion_authority": False, "energization_authority": False,
    }
    (OUT / "firmware-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    (OUT / "state-machine.svg").write_text(state_svg(), encoding="utf-8", newline="\n")
    (OUT / "index.html").write_text(render_target(status, actions, faults), encoding="utf-8", newline="\n")
    (OUT / "README.md").write_text(f"# HR-30 deterministic motion-controller firmware P0.1\n\n**{WARNING}**\n\nThis package contains the portable C `FIRST_POWER_NO_MOTION` core and an actual, reproducible, unflashed STM32H743 target image for the 25-axis/eight-bus controller boundary. Host, core and register-level MMIO vectors pass. Physical flash/HIL evidence and every powered-work authority remain open. See [index.html](index.html), `firmware-status.json`, and `open-holds.csv`.\n", encoding="utf-8", newline="\n")
    shutil.copy2(Path(__file__), OUT / "firmware-package-source.py")
    manifest = [{"path": p.relative_to(OUT).as_posix(), "bytes": p.stat().st_size, "sha256": sha(p), "warning": WARNING} for p in sorted(OUT.rglob("*")) if p.is_file() and p.name != "file-manifest.csv"]
    write_csv(OUT / "file-manifest.csv", manifest)
    integrate_root(status)
    import generate_hr30_system_package_p01 as system_package
    system_package.refresh_manifest_and_release()
    print(json.dumps(status, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
