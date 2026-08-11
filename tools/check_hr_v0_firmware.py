"""Validate the preliminary HR-V0 watchdog and supervisor source package.

This proves source/configuration consistency, executable reference-model tests,
and integrity of the controlled RP2040 build evidence. It does not flash a
target, perform HIL testing, establish functional-safety integrity, or
authorize energization.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIRMWARE = ROOT / "firmware"
MANIFEST = FIRMWARE / "SOURCE-MANIFEST.csv"
WARNING = "PRELIMINARY—NOT APPROVED FOR FABRICATION OR ENERGIZATION"


def controlled_files() -> list[Path]:
    return [
        path for path in sorted(FIRMWARE.rglob("*"))
        if path.is_file()
        and path != MANIFEST
        and "__pycache__" not in path.parts
        and path.suffix != ".pyc"
    ]


def current_hashes() -> dict[str, str]:
    return {
        path.relative_to(FIRMWARE).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest().upper()
        for path in controlled_files()
    }


def write_manifest() -> None:
    with MANIFEST.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["file", "sha256"])
        writer.writerows(current_hashes().items())


def load_manifest() -> dict[str, str]:
    if not MANIFEST.is_file():
        return {}
    with MANIFEST.open(newline="", encoding="utf-8-sig") as handle:
        return {row["file"]: row["sha256"] for row in csv.DictReader(handle)}


def run_tests(path: str) -> tuple[bool, str]:
    result = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", path, "-v"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    return result.returncode == 0, result.stdout + result.stderr


def main() -> int:
    if "--write-manifest" in sys.argv:
        write_manifest()

    failures: list[str] = []
    watchdog_ok, watchdog_log = run_tests("firmware/watchdog/tests")
    supervisor_ok, supervisor_log = run_tests("firmware/supervisor/tests")
    if not watchdog_ok:
        failures.append("watchdog reference-model tests failed\n" + watchdog_log)
    if not supervisor_ok:
        failures.append("supervisor tests failed\n" + supervisor_log)

    watchdog_config = json.loads((FIRMWARE / "watchdog" / "watchdog-config.json").read_text(encoding="utf-8"))
    expected_gpio = {
        "heartbeat_input": {"gpio": 2, "physical_pin": 4},
        "relay1_drive": {"gpio": 3, "physical_pin": 5},
        "relay2_drive": {"gpio": 4, "physical_pin": 6},
        "relay1_nc_feedback": {"gpio": 6, "physical_pin": 9},
        "relay2_nc_feedback": {"gpio": 7, "physical_pin": 10},
    }
    if watchdog_config.get("configuration_id") != "HR-V0-WD-P0.4":
        failures.append("watchdog configuration ID is not HR-V0-WD-P0.4")
    if watchdog_config.get("gpio_assignments") != expected_gpio:
        failures.append("watchdog GPIO assignment differs from the Electrical V3-P0.4 candidate")
    if watchdog_config.get("feedback_front_end") != "TI_ISO1212DBQ_P0.1":
        failures.append("watchdog feedback front end differs from the Electrical V3-P0.4 candidate")
    if watchdog_config.get("heartbeat_front_end") != "VISHAY_VO618A-4X017T_R910_PULLUP10K_P0.1":
        failures.append("watchdog heartbeat front end differs from the Electrical V3-P1.0 candidate")
    if watchdog_config.get("relay_driver") != "2X_TI_TPL7407LPWR_OUT1_P0.1":
        failures.append("watchdog relay drivers differ from the Electrical V3-P1.0 candidate")
    if watchdog_config.get("feedback_gpio_active_high") is not True:
        failures.append("watchdog feedback GPIO polarity is not active-high for KWD NC closed")
    if watchdog_config.get("processor_watchdog_timeout_ms") != 100:
        failures.append("processor watchdog timeout is not the 100 ms platform candidate")
    if watchdog_config.get("polling_period_us") != 1000:
        failures.append("watchdog polling period is not the 1 ms platform candidate")
    if watchdog_config.get("platform_binding") != "RASPBERRY_PI_PICO_SC0915_PICO_SDK_2.3.0_P0.2":
        failures.append("watchdog platform binding differs from the compiled Pico P0.2 candidate")
    if watchdog_config.get("platform_binding_status") != "SOURCE-CANDIDATE-HIL-REQUIRED":
        failures.append("watchdog platform binding no longer preserves the HIL-required boundary")
    header = (FIRMWARE / "watchdog" / "include" / "pb_watchdog.h").read_text(encoding="utf-8")
    source = (FIRMWARE / "watchdog" / "src" / "pb_watchdog.c").read_text(encoding="utf-8")
    define_names = {
        "heartbeat_nominal_edge_ms": "PB_WD_HEARTBEAT_NOMINAL_EDGE_MS",
        "heartbeat_timeout_ms": "PB_WD_HEARTBEAT_TIMEOUT_MS",
        "heartbeat_minimum_edge_ms": "PB_WD_HEARTBEAT_MINIMUM_EDGE_MS",
        "startup_valid_edges": "PB_WD_STARTUP_VALID_EDGES",
        "relay_feedback_settle_ms": "PB_WD_RELAY_FEEDBACK_SETTLE_MS",
    }
    for json_name, define_name in define_names.items():
        match = re.search(rf"#define\s+{define_name}\s+(\d+)u", header)
        if match is None or int(match.group(1)) != int(watchdog_config[json_name]):
            failures.append(f"watchdog C constant {define_name} differs from watchdog-config.json")
    for required in (
        "_Static_assert(PB_WD_HEARTBEAT_TIMEOUT_MS == 3u * PB_WD_HEARTBEAT_NOMINAL_EDGE_MS",
        "state->relay1_drive = false;",
        "state->relay2_drive = false;",
        "state->valid_edges >= PB_WD_STARTUP_VALID_EDGES",
        "inputs.relay1_nc != !state->relay1_drive",
        "inputs.relay2_nc != !state->relay2_drive",
        "PB_WD_FAULT_CLOCK_REGRESSION",
        "clock_regressed(inputs.now_ms, state->last_now_ms)",
    ):
        if required not in source:
            failures.append(f"portable watchdog source invariant missing: {required}")

    platform_source = (FIRMWARE / "watchdog" / "platform" / "pico" / "main.c").read_text(encoding="utf-8")
    for required in (
        "#define PB_WD_GPIO_HEARTBEAT 2u",
        "#define PB_WD_GPIO_RELAY1_DRIVE 3u",
        "#define PB_WD_GPIO_RELAY2_DRIVE 4u",
        "#define PB_WD_GPIO_RELAY1_NC 6u",
        "#define PB_WD_GPIO_RELAY2_NC 7u",
        "#define PB_WD_PROCESSOR_WATCHDOG_MS 100u",
        "#define PB_WD_LOOP_PERIOD_US 1000u",
        "gpio_put(gpio, false);",
        "gpio_set_dir(gpio, GPIO_OUT);",
        "watchdog_enable(PB_WD_PROCESSOR_WATCHDOG_MS, false);",
        "gpio_put_masked(PB_WD_DRIVE_MASK, drive_value);",
    ):
        if required not in platform_source:
            failures.append(f"Pico watchdog platform invariant missing: {required}")
    low_index = platform_source.find("gpio_put(gpio, false);")
    output_index = platform_source.find("gpio_set_dir(gpio, GPIO_OUT);")
    if low_index >= 0 and output_index >= 0 and low_index > output_index:
        failures.append("Pico relay drive is not set low before GPIO output direction")

    toolchain_lock_path = FIRMWARE / "watchdog" / "toolchain-lock.json"
    toolchain_lock = json.loads(toolchain_lock_path.read_text(encoding="utf-8"))
    if toolchain_lock.get("release_id") != "HR-V0-WD-BUILD-P0.2":
        failures.append("target toolchain lock release ID is not HR-V0-WD-BUILD-P0.2")
    expected_tools = {
        "Raspberry Pi Pico SDK": ("2.3.0", "98a542c1a62fb549ffb5d66a3e5892b06276b670"),
        "Arm GNU Toolchain": ("14.3.rel1 / GCC 14.3.1 build arm-14.174", "836ebe51fd71b6542dd7884c8fb2011192464b16c28e4b38fddc9350daba5ee8"),
        "CMake": ("4.3.3", "935ade9e5e8723583c07f44c5592cea2a1c8f65c56ca7e07b34c025c880e0bd6"),
        "Ninja": ("1.13.2", "07fc8261b42b20e71d1720b39068c2e14ffcee6396b76fb7a795fb460b78dc65"),
        "Raspberry Pi picotool prebuilt": ("2.3.0 / pico-sdk-tools v2.3.0-0", "4dcad3bfbc9d126bdb3870bbce0668f5d300d0f2f505ce775b3444bfdd5eaa79"),
        "Python embeddable package": ("3.13.14", "90b4e5b9898b72d744650524bff92377c367f44bd5fbd09e3148656c080ad907"),
    }
    tools_by_name = {item["name"]: item for item in toolchain_lock.get("dependencies", [])}
    for name, (version, revision_or_hash) in expected_tools.items():
        item = tools_by_name.get(name, {})
        if item.get("version") != version:
            failures.append(f"toolchain lock version differs at {name}")
        actual_identity = item.get("git_revision", item.get("sha256", "")).lower()
        if actual_identity != revision_or_hash.lower():
            failures.append(f"toolchain lock revision/hash differs at {name}")
    if toolchain_lock.get("build_controls", {}).get("source_date_epoch") != 1786060800:
        failures.append("toolchain lock does not freeze the R39 SOURCE_DATE_EPOCH")
    build_script = (ROOT / "tools" / "build_hr_v0_watchdog.ps1").read_text(encoding="utf-8")
    if '$env:SOURCE_DATE_EPOCH = "1786060800"' not in build_script:
        failures.append("watchdog build script does not enforce the locked SOURCE_DATE_EPOCH")
    attributes = (ROOT / ".gitattributes").read_text(encoding="utf-8")
    for required in (
        "firmware/**/*.map text eol=lf",
        "firmware/**/*.dis text eol=lf",
        "firmware/**/*.bin binary",
        "firmware/**/*.elf binary",
        "firmware/**/*.exe binary",
        "firmware/**/*.hex text eol=crlf",
        "firmware/**/*.uf2 binary",
    ):
        if required not in attributes:
            failures.append(f"firmware Git checkout control missing: {required}")

    output_dir = FIRMWARE / "watchdog" / "output" / "P0.2"
    artifact_manifest_path = output_dir / "artifact-manifest.csv"
    with artifact_manifest_path.open(newline="", encoding="utf-8-sig") as handle:
        artifact_rows = list(csv.DictReader(handle))
    for row in artifact_rows:
        artifact = output_dir / row["file"]
        if not artifact.is_file():
            failures.append(f"controlled watchdog artifact missing: {row['file']}")
            continue
        if artifact.stat().st_size != int(row["bytes"]):
            failures.append(f"controlled watchdog artifact size differs: {row['file']}")
        if hashlib.sha256(artifact.read_bytes()).hexdigest().lower() != row["sha256"].lower():
            failures.append(f"controlled watchdog artifact hash differs: {row['file']}")
        if row["build_a_matches_build_b"].lower() != "true":
            failures.append(f"controlled watchdog artifact lacks two-build match: {row['file']}")

    build_evidence = json.loads((output_dir / "build-evidence.json").read_text(encoding="utf-8"))
    if build_evidence.get("source_date_epoch") != 1786060800:
        failures.append("watchdog build evidence does not record the locked SOURCE_DATE_EPOCH")
    source_hashes = build_evidence.get("source_hashes", {})
    for relative, expected_hash in source_hashes.items():
        path = ROOT / relative
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest().lower() != expected_hash.lower():
            failures.append(f"watchdog build source hash differs: {relative}")
    reproducibility = build_evidence.get("reproducibility", {})
    for key in (
        "elf_match",
        "uf2_match",
        "bin_match",
        "hex_match",
        "linker_map_match",
        "canonical_disassembly_match",
        "stack_usage_match",
        "canonical_size_match",
    ):
        if reproducibility.get(key) is not True:
            failures.append(f"watchdog reproducibility evidence is not true: {key}")
    if build_evidence.get("verification_boundary", {}).get("gate_disposition") != (
        "EG-017 remains partial; no permission to flash, fabricate or energize."
    ):
        failures.append("watchdog build evidence no longer preserves the EG-017 partial gate")

    host_lock = json.loads((FIRMWARE / "watchdog" / "host-test-toolchain-lock.json").read_text(encoding="utf-8"))
    compiler = host_lock.get("compiler", {})
    if host_lock.get("release_id") != "HR-V0-WD-HOST-VECTOR-P0.1":
        failures.append("host-vector toolchain lock release ID differs")
    if (compiler.get("release"), compiler.get("llvm_version"), compiler.get("target")) != (
        "20260616",
        "22.1.8",
        "x86_64-w64-windows-gnu",
    ):
        failures.append("host-vector compiler identity differs from the pinned release")
    if compiler.get("archive_sha256") != "b9b68a4d276e16fa25802aaba458e4638f64b3884c290aaccdc2d87083b6ca35":
        failures.append("host-vector compiler archive hash differs from the publisher digest")

    host_output = FIRMWARE / "watchdog" / "output" / "host-vector" / "P0.1"
    host_manifest_path = host_output / "artifact-manifest.csv"
    with host_manifest_path.open(newline="", encoding="utf-8-sig") as handle:
        host_rows = list(csv.DictReader(handle))
    if len(host_rows) != 1:
        failures.append("host-vector artifact manifest does not contain exactly one executable")
    else:
        row = host_rows[0]
        artifact = host_output / row["file"]
        if not artifact.is_file():
            failures.append("controlled compiled-C vector runner is missing")
        else:
            if artifact.stat().st_size != int(row["bytes"]):
                failures.append("controlled compiled-C vector runner size differs")
            if hashlib.sha256(artifact.read_bytes()).hexdigest().lower() != row["sha256"].lower():
                failures.append("controlled compiled-C vector runner hash differs")
            if row["build_a_matches_build_b"].lower() != "true":
                failures.append("compiled-C vector runner lacks two-build match")

    host_evidence = json.loads((host_output / "build-evidence.json").read_text(encoding="utf-8"))
    if host_evidence.get("release_id") != "HR-V0-WD-HOST-VECTOR-P0.1":
        failures.append("compiled-C host evidence release ID differs")
    for relative, expected_hash in host_evidence.get("source_hashes", {}).items():
        path = ROOT / relative
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest().lower() != expected_hash.lower():
            failures.append(f"compiled-C host evidence source hash differs: {relative}")
    execution = host_evidence.get("differential_execution", {})
    if (execution.get("result"), execution.get("scenario_count"), execution.get("step_count")) != ("PASS", 9, 44):
        failures.append("compiled-C differential execution evidence differs from 9 scenarios / 44 steps")
    if host_evidence.get("verification_boundary", {}).get("gate_disposition") != (
        "EG-017 remains partial; host execution closes no target-HIL requirement."
    ):
        failures.append("compiled-C host evidence no longer preserves the target-HIL boundary")

    supervisor_config = json.loads((FIRMWARE / "supervisor" / "supervisor-config.json").read_text(encoding="utf-8"))
    if supervisor_config.get("configuration_id") != "HR-V0-SUP-P0.3":
        failures.append("supervisor configuration ID is not HR-V0-SUP-P0.3")
    expected_binding = {
        "limit_set_id": "HR-V0-LIMITS-P0.2",
        "mechanical_revision": "HR-V0-ARM-ARCH-P0.8-DWG-INTEGRATED-CANDIDATE",
        "arm_architecture_revision": "HR-V0-ARM-ARCH-P0.8-DWG-INTEGRATED-CANDIDATE",
        "kinematic_basis_revision": "HR-V0-ARM-ARCH-P0.7",
        "custom_part_manufacturing_revision": "HR-V0-MECH-BOM-BIND-P0.2",
        "hard_stop_revision": "HR-V0-HS-P0.3",
        "release_state": "CANDIDATE-NOT-RELEASED",
        "acceptance_evidence_hash": "SELECTION REQUIRED",
    }
    if supervisor_config.get("mechanical_limit_binding") != expected_binding:
        failures.append("supervisor mechanical-limit binding differs from the unreleased integrated P0.8 candidate with inherited P0.7 kinematic basis")
    if supervisor_config.get("joints", {}).get("J2") != {
        "minimum": 15.0,
        "maximum": 115.0,
        "unit": "deg",
        "start_tolerance": None,
        "terminal_tolerance": None,
    }:
        failures.append("supervisor J2 candidate is not the fail-closed 15..115 degree envelope")
    for field in ("configuration_hash", "kinematic_model_hash"):
        value = supervisor_config[field].upper()
        if "SELECTION" not in value or "REQUIRED" not in value:
            failures.append(f"unreleased supervisor {field} is no longer fail-closed SELECTION REQUIRED")
    model = (FIRMWARE / "supervisor" / "project_button_supervisor" / "model.py").read_text(encoding="utf-8")
    for required in (
        "torque_enable_request=self.state is OperatingState.DRIVE_ENABLED",
        "if not self.config.selections_closed:",
        "self._invalidate_target()",
        "UNEXPECTED_ARM_ORDER",
        "HARDWARE_PERMIT_DROPPED",
        "command.session_id != self.session_id",
        "waiting for three valid watchdog heartbeat edges",
        "computed TCP speed outside configured limit",
        "trajectory sample count exceeds the released bound",
        "trajectory duration exceeds the released bound",
        "execution deadline slack exceeds the released bound",
        "limits_current",
        "evidence_is_accepted(self.mechanical_limit_binding)",
    ):
        if required not in model:
            failures.append(f"supervisor fail-closed invariant missing: {required}")

    actuator_config = json.loads((FIRMWARE / "supervisor" / "actuator-config.json").read_text(encoding="utf-8"))
    if actuator_config.get("configuration_id") != "HR-V0-ACT-P0.3":
        failures.append("actuator configuration ID is not HR-V0-ACT-P0.3")
    if actuator_config.get("mechanical_limit_binding") != expected_binding:
        failures.append("actuator mechanical-limit binding differs from the unreleased integrated P0.8 candidate with inherited P0.7 kinematic basis")
    if actuator_config.get("external_branch_current_limit_a") != "SELECTION REQUIRED":
        failures.append("external branch-current limit was released without physical evidence")
    if actuator_config.get("current_envelope_binding") != {
        "identifier": "HR-V0-DXL-CURRENT-ENV-P0.1",
        "release_state": "CANDIDATE-NOT-RELEASED",
        "acceptance_evidence_hash": "SELECTION REQUIRED",
    }:
        failures.append("actuator current-envelope binding is missing or no longer fail-closed")
    if actuator_config.get("operating_mode") != 5:
        failures.append("actuator candidate is not current-based position control mode 5")
    if actuator_config.get("startup_torque_on") is not False:
        failures.append("actuator startup-torque candidate is not fail-off")
    if actuator_config.get("torque_on_by_goal_update") is not False:
        failures.append("actuator goal-update torque candidate is not fail-off")
    expected_actuators = {
        "J1": (1, "XM540-W270-T", 800, -20.0, 70.0, "deg"),
        "J2": (2, "XM540-W270-T", 800, 15.0, 115.0, "deg"),
        "GRIPPER": (3, "XM430-W350-T", 300, 20.0, 75.0, "mm"),
    }
    for joint, (actuator_id, model_name, raw_limit, minimum, maximum, unit) in expected_actuators.items():
        item = actuator_config.get("actuators", {}).get(joint, {})
        if (item.get("id"), item.get("model"), item.get("current_limit_raw_candidate")) != (actuator_id, model_name, raw_limit):
            failures.append(f"actuator candidate differs at {joint}")
        if (item.get("minimum_engineering"), item.get("maximum_engineering"), item.get("engineering_unit")) != (minimum, maximum, unit):
            failures.append(f"actuator engineering envelope differs at {joint}")
        if isinstance(item.get("model_number"), int) or isinstance(item.get("firmware_version"), int):
            failures.append(f"received identity was inferred before inspection at {joint}")
    actuator_model = (FIRMWARE / "supervisor" / "project_button_supervisor" / "actuator_config.py").read_text(encoding="utf-8")
    for required in (
        "RELEASE_SELECTIONS_OPEN",
        "TORQUE_ALREADY_ENABLED",
        "TORQUE_ON_GOAL_UPDATE_MISMATCH",
        "STARTUP_TORQUE_MISMATCH",
        "CURRENT_LIMIT_MISMATCH",
        "GOAL_CURRENT_EXCEEDS_CANDIDATE",
        "HARDWARE_ERROR_PRESENT",
        "DRIVE_MODE_MISMATCH",
        "def engineering_to_raw",
        "def raw_to_engineering",
        "actuator transport/calibration selections remain open",
        "engineering target outside controlled motion envelope",
        "evidence_is_accepted(self.mechanical_limit_binding)",
        "current_envelope_evidence_is_accepted(self.current_envelope_binding)",
        "EXPECTED_CURRENT_ENVELOPE_ID",
    ):
        if required not in actuator_model:
            failures.append(f"actuator fail-closed invariant missing: {required}")

    dynamixel_bus = (FIRMWARE / "supervisor" / "project_button_supervisor" / "dynamixel_bus.py").read_text(encoding="utf-8")
    for required in (
        "configured_current_limit_raw=self._read(actuator_id, CURRENT_LIMIT)",
        "active_goal_current_raw=self._read(actuator_id, GOAL_CURRENT)",
        "configured-current-limit readback changed during execution",
        "goal-current readback disagrees with torque state",
        "torque is enabled outside motion authority",
        "self._best_effort_goal_current_zero",
        "Read all execution invariants and force torque-off on any failure.",
    ):
        if required not in dynamixel_bus:
            failures.append(f"continuous DXL current-bound invariant missing: {required}")

    transport_config = actuator_config.get("transport", {})
    if transport_config != {
        "implementation": "ROBOTIS DYNAMIXEL SDK",
        "sdk_version": "4.0.5",
        "protocol": 2.0,
        "baud_rate": 1_000_000,
        "device": "SELECTION REQUIRED",
    }:
        failures.append("DYNAMIXEL transport configuration is not the pinned fail-closed candidate")
    if actuator_config.get("bus_watchdog_raw_candidate") != 5:
        failures.append("DYNAMIXEL bus-watchdog candidate is not 5 raw / nominal 100 ms")
    for joint, item in actuator_config.get("actuators", {}).items():
        for field in (
            "profile_velocity_raw_candidate",
            "profile_acceleration_raw_candidate",
            "position_zero_raw",
            "position_zero_engineering",
            "raw_per_unit",
            "direction",
            "minimum_raw",
            "maximum_raw",
            "start_tolerance_raw",
            "minimum_input_voltage_raw",
            "maximum_input_voltage_raw",
            "maximum_temperature_c",
        ):
            if isinstance(item.get(field), (int, float)):
                failures.append(f"received/physical DYNAMIXEL field was inferred before evidence at {joint}.{field}")

    sdk_lock = json.loads((FIRMWARE / "supervisor" / "dynamixel-sdk-lock.json").read_text(encoding="utf-8"))
    if (
        sdk_lock.get("release_id"),
        sdk_lock.get("distribution"),
        sdk_lock.get("version"),
        sdk_lock.get("upstream_tag"),
        sdk_lock.get("upstream_commit"),
        sdk_lock.get("installation"),
    ) != (
        "HR-V0-DXL-TRANSPORT-P0.3",
        "dynamixel-sdk",
        "4.0.5",
        "4.0.5",
        "2ded684",
        "NOT INSTALLED OR EXECUTED ON TARGET",
    ):
        failures.append("DYNAMIXEL SDK lock identity or installation boundary differs")

    bus_source = (FIRMWARE / "supervisor" / "project_button_supervisor" / "dynamixel_bus.py").read_text(encoding="utf-8")
    for required in (
        "release selections remain open; serial port will not be opened",
        "self._torque_off_ids(expected_ids, verify=True)",
        "set(discovered) != expected_ids",
        "fresh matching supervisor motion authority is absent",
        "self._sync_write(GOAL_POSITION, raw_targets)",
        "self._sync_write(TORQUE_ENABLE",
        "bus watchdog expired",
        "input-voltage readback is outside the released envelope",
        "temperature readback exceeds the released limit",
        "self._best_effort_torque_off",
    ):
        if required not in bus_source:
            failures.append(f"DYNAMIXEL bus fail-closed invariant missing: {required}")
    if bus_source.find("self._sync_write(GOAL_POSITION, raw_targets)") > bus_source.find("self._sync_write(TORQUE_ENABLE"):
        failures.append("DYNAMIXEL torque enable appears before the zero-jump start target")

    runtime_source = (FIRMWARE / "supervisor" / "project_button_supervisor" / "runtime.py").read_text(encoding="utf-8")
    for required in (
        "maximum sample lateness remains SELECTION REQUIRED",
        "self.hardware.disable_heartbeat()",
        "self.hardware.service_heartbeat(now_ms, outputs.heartbeat_allowed)",
        "self.bus.connect_and_configure()",
        "self.supervisor.observe_hardware(snapshot, now_ms)",
        "self.bus.start_trajectory",
        "missed its released lateness bound",
        "self.supervisor.complete_trajectory",
        "self.bus.stop()",
    ):
        if required not in runtime_source:
            failures.append(f"runtime execution invariant missing: {required}")

    sdk_source = (FIRMWARE / "supervisor" / "project_button_supervisor" / "sdk_transport.py").read_text(encoding="utf-8")
    for required in (
        'PINNED_VERSION = "4.0.5"',
        "installed_version = metadata.version(PINNED_DISTRIBUTION)",
        "except metadata.PackageNotFoundError",
        "installed_version != PINNED_VERSION",
        "self.sdk.PacketHandler(PROTOCOL_VERSION)",
        "self.sdk.GroupSyncWrite",
        "self._check_comm",
    ):
        if required not in sdk_source:
            failures.append(f"pinned SDK adapter invariant missing: {required}")

    hil_path = ROOT / "tests" / "forms" / "hr-v0-dynamixel-transport-hil-template.csv"
    with hil_path.open(newline="", encoding="utf-8-sig") as handle:
        hil_rows = list(csv.DictReader(handle))
    expected_hil_cases = {
        "UNRESOLVED_CONFIG_PORT_OPEN_INHIBIT",
        "TORQUE_OFF_BEFORE_DISCOVERY",
        "UNEXPECTED_OR_DUPLICATE_ID",
        "PACKET_TIMEOUT_OR_CRC_ERROR",
        "USB_UNPLUG_AND_RECONNECT",
        "BUS_WATCHDOG_EXPIRY",
        "PROCESS_CRASH_OR_KILL",
        "BROWNOUT_OR_ACTUATOR_REBOOT",
        "AUTHORITY_OR_TRAJECTORY_ID_LOSS",
    }
    actual_hil_cases = {row.get("test_case", "") for row in hil_rows}
    required_warning = "PRELIMINARY - NOT APPROVED FOR CONNECTION OR ENERGIZATION"
    if (
        len(hil_rows) != 9
        or actual_hil_cases != expected_hil_cases
        or any(row.get("firmware_id") != "HR-V0-FW-P0.4" for row in hil_rows)
        or any(row.get("transport_id") != "HR-V0-DXL-TRANSPORT-P0.3" for row in hil_rows)
        or any(row.get("result") != "NOT EXECUTED" for row in hil_rows)
        or any(row.get("warning") != required_warning for row in hil_rows)
    ):
        failures.append("DYNAMIXEL HIL template must contain the exact nine unexecuted warned fault cases")

    if load_manifest() != current_hashes():
        failures.append("firmware SOURCE-MANIFEST.csv does not match the controlled source tree")

    requirements = (ROOT / "requirements" / "requirements.csv").read_text(encoding="utf-8-sig")
    if "distinct software ARM action" in requirements:
        failures.append("SAFE-003 still conflicts with the physical V3 ARM architecture")

    if failures:
        print("HR-V0 firmware validation: FAIL")
        for failure in failures:
            print("- " + failure)
        return 1

    test_count = watchdog_log.count(" ... ok") + supervisor_log.count(" ... ok")
    print(f"HR-V0 firmware source validation: PASS ({test_count} executable unit tests)")
    print("Pico binding and controlled two-build binary evidence: PASS (source/build integrity only)")
    print("Target flash, received-hardware execution and HIL: NOT PERFORMED")
    print(WARNING)
    print("Source tests and hashes are not functional-safety approval or permission to energize.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
