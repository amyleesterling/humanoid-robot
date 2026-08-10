"""Fail-closed libgpiod hardware and heartbeat backend for HR-V0.

PRELIMINARY - NOT APPROVED FOR INSTALLATION, CONNECTION, MOTION OR ENERGIZATION.

The module is safe to import on a development host: libgpiod is imported only
inside the selected factory, after the pure-file preflight has passed.  The
committed configuration deliberately leaves the GPIO chip, line allocation,
polarity, timing, package version and physical observation circuit unresolved.
"""

from __future__ import annotations

from importlib import metadata
from pathlib import Path
from typing import Any, Mapping, Protocol

from project_button_supervisor import HardwareSnapshot


INPUT_NAMES = (
    "control_power",
    "estop_healthy",
    "watchdog_healthy",
    "edm_healthy",
    "compute_undervoltage",
    "sr1_ready",
    "sra1_armed",
    "k1_feedback",
    "k2_feedback",
)


class HardwareBackendError(RuntimeError):
    """A GPIO selection, access, timing or observation failure."""


class LineAccess(Protocol):
    def set_heartbeat(self, active: bool) -> None: ...
    def read_inputs(self) -> Mapping[str, bool]: ...
    def close(self) -> None: ...


class HeartbeatScheduler:
    """Monotonic edge scheduler that removes output on lateness or time reversal."""

    def __init__(self, access: LineAccess, half_period_ms: int, maximum_lateness_ms: int) -> None:
        if half_period_ms <= 0:
            raise HardwareBackendError("heartbeat half-period must be positive")
        if maximum_lateness_ms < 0 or maximum_lateness_ms >= half_period_ms:
            raise HardwareBackendError("heartbeat lateness must be nonnegative and below the half-period")
        self.access = access
        self.half_period_ms = half_period_ms
        self.maximum_lateness_ms = maximum_lateness_ms
        self.enabled = False
        self.level = False
        self.next_edge_ms: int | None = None
        self.last_service_ms: int | None = None

    def service(self, now_ms: int, allowed: bool) -> None:
        if isinstance(now_ms, bool) or not isinstance(now_ms, int) or now_ms < 0:
            self.disable()
            raise HardwareBackendError("heartbeat service time is invalid")
        if self.last_service_ms is not None and now_ms < self.last_service_ms:
            self.disable()
            raise HardwareBackendError("heartbeat monotonic time moved backwards")
        self.last_service_ms = now_ms
        if not allowed:
            self.disable(reset_time=False)
            return
        if not self.enabled:
            self.enabled = True
            self.level = True
            self.access.set_heartbeat(True)
            self.next_edge_ms = now_ms + self.half_period_ms
            return
        assert self.next_edge_ms is not None
        if now_ms < self.next_edge_ms:
            return
        if now_ms > self.next_edge_ms + self.maximum_lateness_ms:
            self.disable(reset_time=False)
            raise HardwareBackendError("heartbeat edge missed its released lateness bound")
        self.level = not self.level
        self.access.set_heartbeat(self.level)
        self.next_edge_ms += self.half_period_ms

    def disable(self, *, reset_time: bool = True) -> None:
        try:
            self.access.set_heartbeat(False)
        finally:
            self.enabled = False
            self.level = False
            self.next_edge_ms = None
            if reset_time:
                self.last_service_ms = None


class GpiodHardware:
    """HardwareIO implementation with explicit logical input polarity."""

    def __init__(
        self,
        access: LineAccess,
        input_active_high: Mapping[str, bool],
        heartbeat_half_period_ms: int,
        maximum_edge_lateness_ms: int,
    ) -> None:
        if set(input_active_high) != set(INPUT_NAMES):
            raise HardwareBackendError("GPIO input allocation does not exactly match the runtime observation set")
        if any(not isinstance(value, bool) for value in input_active_high.values()):
            raise HardwareBackendError("every GPIO input polarity must be an exact boolean")
        self.access = access
        self.input_active_high = dict(input_active_high)
        self.heartbeat = HeartbeatScheduler(
            access, heartbeat_half_period_ms, maximum_edge_lateness_ms
        )
        self.closed = False

    def service_heartbeat(self, now_ms: int, allowed: bool) -> None:
        if self.closed:
            raise HardwareBackendError("GPIO backend is closed")
        self.heartbeat.service(now_ms, bool(allowed))

    def disable_heartbeat(self) -> None:
        self.heartbeat.disable()

    def snapshot(self, positions: Mapping[str, float]) -> HardwareSnapshot:
        if self.closed:
            raise HardwareBackendError("GPIO backend is closed")
        raw = dict(self.access.read_inputs())
        if set(raw) != set(INPUT_NAMES) or any(not isinstance(value, bool) for value in raw.values()):
            raise HardwareBackendError("GPIO readback is incomplete or not boolean")
        logical = {
            name: raw[name] if self.input_active_high[name] else not raw[name]
            for name in INPUT_NAMES
        }
        return HardwareSnapshot(
            control_power=logical["control_power"],
            estop_healthy=logical["estop_healthy"],
            watchdog_healthy=logical["watchdog_healthy"],
            edm_healthy=logical["edm_healthy"],
            bus_healthy=True,
            compute_undervoltage=logical["compute_undervoltage"],
            sr1_ready=logical["sr1_ready"],
            sra1_armed=logical["sra1_armed"],
            k1_feedback=logical["k1_feedback"],
            k2_feedback=logical["k2_feedback"],
            positions=dict(positions),
        )

    def close(self) -> None:
        if self.closed:
            return
        try:
            self.disable_heartbeat()
        finally:
            self.access.close()
            self.closed = True


class LibgpiodLineAccess:
    """Small adapter around the documented libgpiod 2.x Python API."""

    def __init__(
        self,
        gpiod: Any,
        chip_path: str,
        heartbeat_line: int,
        input_lines: Mapping[str, int],
    ) -> None:
        self.gpiod = gpiod
        self.heartbeat_line = heartbeat_line
        self.input_lines = dict(input_lines)
        output = gpiod.LineSettings(
            direction=gpiod.line.Direction.OUTPUT,
            output_value=gpiod.line.Value.INACTIVE,
            drive=gpiod.line.Drive.PUSH_PULL,
        )
        input_settings = gpiod.LineSettings(
            direction=gpiod.line.Direction.INPUT,
            bias=gpiod.line.Bias.DISABLED,
        )
        self.request = gpiod.request_lines(
            chip_path,
            consumer="project-button-ordinary-control",
            config={heartbeat_line: output, tuple(input_lines.values()): input_settings},
            output_values={heartbeat_line: gpiod.line.Value.INACTIVE},
        )

    def set_heartbeat(self, active: bool) -> None:
        value = self.gpiod.line.Value.ACTIVE if active else self.gpiod.line.Value.INACTIVE
        self.request.set_value(self.heartbeat_line, value)

    def read_inputs(self) -> Mapping[str, bool]:
        values = self.request.get_values(list(self.input_lines.values()))
        return {
            name: value is self.gpiod.line.Value.ACTIVE
            for name, value in zip(self.input_lines, values, strict=True)
        }

    def close(self) -> None:
        self.request.release()


def _selected_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip() or "SELECTION" in value.upper() or "REQUIRED" in value.upper():
        raise HardwareBackendError(f"{label} remains SELECTION REQUIRED")
    return value


def _selected_int(value: Any, label: str, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise HardwareBackendError(f"{label} remains SELECTION REQUIRED")
    return value


def factory(host: Mapping[str, Any], root: Path) -> GpiodHardware:
    """Construct only from an exact, preflight-approved GPIO allocation."""

    gpio = host.get("gpio")
    if not isinstance(gpio, dict):
        raise HardwareBackendError("GPIO allocation remains SELECTION REQUIRED")
    distribution = _selected_text(gpio.get("distribution"), "GPIO distribution")
    version = _selected_text(gpio.get("version"), "GPIO distribution version")
    try:
        installed = metadata.version(distribution)
    except metadata.PackageNotFoundError as exc:
        raise HardwareBackendError(f"required GPIO distribution {distribution} is absent") from exc
    if installed != version:
        raise HardwareBackendError(f"GPIO distribution must be exactly {distribution} {version}")

    chip = _selected_text(gpio.get("chip_path"), "GPIO chip path")
    if not chip.startswith("/"):
        raise HardwareBackendError("GPIO chip path must be absolute")
    chip_path = str(root / chip.lstrip("/"))
    heartbeat_line = _selected_int(gpio.get("heartbeat_line"), "heartbeat line")
    half_period = _selected_int(gpio.get("heartbeat_half_period_ms"), "heartbeat half-period", 1)
    lateness = _selected_int(gpio.get("maximum_edge_lateness_ms"), "heartbeat edge lateness")
    inputs = gpio.get("inputs")
    if not isinstance(inputs, dict) or set(inputs) != set(INPUT_NAMES):
        raise HardwareBackendError("runtime GPIO inputs remain SELECTION REQUIRED")
    input_lines: dict[str, int] = {}
    active_high: dict[str, bool] = {}
    for name in INPUT_NAMES:
        item = inputs[name]
        if not isinstance(item, dict):
            raise HardwareBackendError(f"GPIO input {name} remains SELECTION REQUIRED")
        input_lines[name] = _selected_int(item.get("line"), f"GPIO input {name} line")
        if not isinstance(item.get("active_high"), bool):
            raise HardwareBackendError(f"GPIO input {name} polarity remains SELECTION REQUIRED")
        active_high[name] = item["active_high"]
    all_lines = [heartbeat_line, *input_lines.values()]
    if len(all_lines) != len(set(all_lines)):
        raise HardwareBackendError("GPIO line allocation contains duplicates")

    import importlib

    gpiod = importlib.import_module("gpiod")
    access = LibgpiodLineAccess(gpiod, chip_path, heartbeat_line, input_lines)
    return GpiodHardware(access, active_high, half_period, lateness)


__all__ = [
    "GpiodHardware",
    "HardwareBackendError",
    "HeartbeatScheduler",
    "INPUT_NAMES",
    "factory",
]
