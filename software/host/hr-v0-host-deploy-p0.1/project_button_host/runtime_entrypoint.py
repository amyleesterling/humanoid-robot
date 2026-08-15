#!/usr/bin/env python3
"""Configuration-bound HR-V0 runtime entrypoint for a future isolated HIL image.

PRELIMINARY—NOT APPROVED FOR INSTALLATION, CONNECTION, MOTION OR ENERGIZATION.

The committed host configuration exits during pure-file preflight.  Backend
modules are imported only after host, supervisor, actuator, kinematic and
evidence selections are closed and hash-bound.
"""

from __future__ import annotations

import importlib
import json
import re
import signal
import sys
import time
from pathlib import Path
from typing import Any, Callable, Mapping

from project_button_host.preflight import evaluate


EXIT_CONFIGURATION = 78
BACKEND_SPEC = re.compile(r"^[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*:[A-Za-z_]\w*$")


def _target(root: Path, absolute: str) -> Path:
    if not isinstance(absolute, str) or not absolute.startswith("/"):
        raise ValueError("target path is not absolute")
    return root / absolute.lstrip("/")


def _factory(specification: str) -> Callable[..., Any]:
    if not isinstance(specification, str) or not BACKEND_SPEC.fullmatch(specification):
        raise ValueError("backend must be an exact module:factory specification")
    module_name, attribute = specification.split(":", 1)
    factory = getattr(importlib.import_module(module_name), attribute)
    if not callable(factory):
        raise TypeError("selected backend attribute is not callable")
    return factory


def _boot_session(path: Path) -> str:
    value = path.read_text(encoding="utf-8").strip()
    if not value or len(value) > 128 or not re.fullmatch(r"[A-Za-z0-9._-]+", value):
        raise ValueError("boot/session identifier is absent or malformed")
    return value


def run(config_path: Path, root: Path = Path("/")) -> int:
    """Run only a fully released isolated-HIL configuration."""

    result = evaluate(config_path, root)
    if not result.ready:
        print(json.dumps(result.as_dict(), sort_keys=True))
        return EXIT_CONFIGURATION

    executive = None
    hardware = None
    commands = None
    evidence = None
    try:
        host: Mapping[str, Any] = json.loads(config_path.read_text(encoding="utf-8"))
        from project_button_supervisor import (
            ActuatorConfiguration,
            DynamixelBusController,
            EvidenceContext,
            HashChainedJsonlSink,
            RuntimeExecutive,
            Supervisor,
        )

        supervisor_path = _target(root, str(host["supervisor_config_path"]))
        actuator_path = _target(root, str(host["actuator_config_path"]))
        boot_id_path = _target(root, str(host["boot_id_path"]))
        session_id = _boot_session(boot_id_path)
        supervisor = Supervisor.from_json(supervisor_path, session_id)
        actuators = ActuatorConfiguration.from_json(actuator_path)
        if not supervisor.config.selections_closed:
            raise ValueError("supervisor selections remain open")
        if not actuators.release_selections_closed:
            raise ValueError("actuator selections remain open")
        if actuators.transport.get("device") != host.get("serial_device"):
            raise ValueError("host and actuator serial-device selections disagree")

        period = host.get("runtime_cycle_period_ms")
        if isinstance(period, bool) or not isinstance(period, int) or not 1 <= period <= 10:
            raise ValueError("runtime cycle period is not released in the 1..10 ms logging bound")

        log_config = host["evidence_log"]
        context = EvidenceContext(
            session_id=session_id,
            identities=dict(log_config["identities"]),
            hashes=dict(log_config["hashes"]),
        )
        log_directory = _target(root, str(log_config["directory"]))
        now_ms = time.monotonic_ns() // 1_000_000
        evidence = HashChainedJsonlSink(
            log_directory / f"{session_id}.jsonl", context, now_ms
        )

        # Selected modules are first imported here, after every pure-file and
        # source-configuration condition above has closed.
        hardware = _factory(str(host["gpio_backend"]))(host, root)
        commands = _factory(str(host["runtime_backend"]))(host, root)
        from project_button_supervisor.sdk_transport import SdkTransport

        transport = SdkTransport(
            str(host["serial_device"]), int(actuators.transport["baud_rate"])
        )
        bus = DynamixelBusController(transport, actuators)
        executive = RuntimeExecutive(supervisor, bus, hardware, commands, evidence)

        stop_requested = False

        def request_stop(signum, frame) -> None:  # noqa: ARG001
            nonlocal stop_requested
            stop_requested = True

        signal.signal(signal.SIGTERM, request_stop)
        signal.signal(signal.SIGINT, request_stop)
        executive.start(time.monotonic_ns() // 1_000_000)
        while not stop_requested:
            executive.cycle(time.monotonic_ns() // 1_000_000)
            time.sleep(period / 1000.0)
        return 0
    except Exception as exc:
        print(
            json.dumps(
                {
                    "ready": False,
                    "holds": [f"runtime failed closed: {type(exc).__name__}: {exc}"],
                    "motion_authority": "NONE",
                },
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return EXIT_CONFIGURATION
    finally:
        if executive is not None:
            try:
                executive.shutdown(time.monotonic_ns() // 1_000_000)
            except Exception as shutdown_exc:
                print(
                    json.dumps(
                        {"ready": False, "holds": [f"shutdown cleanup failure: {shutdown_exc}"], "motion_authority": "NONE"},
                        sort_keys=True,
                    ),
                    file=sys.stderr,
                )
        else:
            cleanup_errors = []
            if commands is not None:
                try:
                    commands.close()
                except Exception as cleanup_exc:
                    cleanup_errors.append(f"commands: {cleanup_exc}")
            if hardware is not None:
                try:
                    hardware.disable_heartbeat()
                except Exception as cleanup_exc:
                    cleanup_errors.append(f"heartbeat: {cleanup_exc}")
                try:
                    hardware.close()
                except Exception as cleanup_exc:
                    cleanup_errors.append(f"hardware: {cleanup_exc}")
            if evidence is not None:
                try:
                    evidence.close(time.monotonic_ns() // 1_000_000)
                except Exception as cleanup_exc:
                    cleanup_errors.append(f"evidence: {cleanup_exc}")
            if cleanup_errors:
                print(
                    json.dumps(
                        {"ready": False, "holds": ["partial-start cleanup failures: " + "; ".join(cleanup_errors)], "motion_authority": "NONE"},
                        sort_keys=True,
                    ),
                    file=sys.stderr,
                )


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--root", type=Path, default=Path("/"))
    args = parser.parse_args()
    return run(args.config, args.root)


if __name__ == "__main__":
    raise SystemExit(main())
