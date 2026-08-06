"""Executable specification for the non-safety HR-V0 watchdog logic."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


WARNING = "PRELIMINARY—NOT APPROVED FOR FABRICATION OR ENERGIZATION"


@dataclass(frozen=True)
class WatchdogConfig:
    heartbeat_nominal_edge_ms: int
    heartbeat_timeout_ms: int
    heartbeat_minimum_edge_ms: int
    startup_valid_edges: int
    relay_feedback_settle_ms: int

    @classmethod
    def from_json(cls, path: Path) -> "WatchdogConfig":
        raw = json.loads(path.read_text(encoding="utf-8"))
        return cls(**{field: int(raw[field]) for field in cls.__dataclass_fields__})


@dataclass(frozen=True)
class WatchdogOutputs:
    relay1_drive: bool
    relay2_drive: bool
    heartbeat_fresh: bool
    fault_latched: bool
    fault_reason: str | None
    valid_edges: int


class WatchdogModel:
    """Default-off two-output watchdog with diagnostic NC feedback checking."""

    def __init__(self, config: WatchdogConfig):
        if config.heartbeat_timeout_ms != 3 * config.heartbeat_nominal_edge_ms:
            raise ValueError("controlled timeout must equal three nominal heartbeat edges")
        if config.heartbeat_minimum_edge_ms <= 0 or config.heartbeat_minimum_edge_ms >= config.heartbeat_nominal_edge_ms:
            raise ValueError("minimum edge interval must be positive and below nominal")
        self.config = config
        self._initialized = False
        self._last_now_ms = 0
        self._last_heartbeat_level = False
        self._last_edge_ms: int | None = None
        self._valid_edges = 0
        self._relay1_drive = False
        self._relay2_drive = False
        self._drive_change_ms = 0
        self._fault_reason: str | None = None

    def step(self, now_ms: int, heartbeat_level: bool, relay1_nc: bool, relay2_nc: bool) -> WatchdogOutputs:
        if not self._initialized:
            self._initialized = True
            self._last_now_ms = now_ms
            self._last_heartbeat_level = heartbeat_level
            self._drive_change_ms = now_ms
            return self.outputs(now_ms)

        if now_ms < self._last_now_ms:
            self._latch("monotonic clock moved backward")
        self._last_now_ms = now_ms

        if now_ms - self._drive_change_ms >= self.config.relay_feedback_settle_ms:
            if relay1_nc != (not self._relay1_drive):
                self._latch("relay 1 NC feedback disagrees with command")
            if relay2_nc != (not self._relay2_drive):
                self._latch("relay 2 NC feedback disagrees with command")

        if heartbeat_level != self._last_heartbeat_level:
            if self._last_edge_ms is not None and now_ms - self._last_edge_ms < self.config.heartbeat_minimum_edge_ms:
                self._latch("heartbeat edge interval below configured minimum")
            else:
                self._valid_edges += 1
                self._last_edge_ms = now_ms
            self._last_heartbeat_level = heartbeat_level

        fresh = self._last_edge_ms is not None and now_ms - self._last_edge_ms < self.config.heartbeat_timeout_ms
        if not fresh:
            self._valid_edges = 0
        desired = self._fault_reason is None and fresh and self._valid_edges >= self.config.startup_valid_edges
        if desired != self._relay1_drive or desired != self._relay2_drive:
            self._relay1_drive = desired
            self._relay2_drive = desired
            self._drive_change_ms = now_ms
        return self.outputs(now_ms)

    def outputs(self, now_ms: int) -> WatchdogOutputs:
        fresh = self._last_edge_ms is not None and now_ms - self._last_edge_ms < self.config.heartbeat_timeout_ms
        return WatchdogOutputs(
            relay1_drive=self._relay1_drive,
            relay2_drive=self._relay2_drive,
            heartbeat_fresh=fresh,
            fault_latched=self._fault_reason is not None,
            fault_reason=self._fault_reason,
            valid_edges=self._valid_edges,
        )

    def _latch(self, reason: str) -> None:
        if self._fault_reason is None:
            self._fault_reason = reason
        if self._relay1_drive or self._relay2_drive:
            self._relay1_drive = False
            self._relay2_drive = False
            self._drive_change_ms = self._last_now_ms
