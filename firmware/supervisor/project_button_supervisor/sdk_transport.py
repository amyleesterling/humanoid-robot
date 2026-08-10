"""Pinned ROBOTIS DYNAMIXEL SDK 4.0.5 transport adapter.

PRELIMINARY—NOT APPROVED FOR FABRICATION OR ENERGIZATION.

Importing this module does not open a port.  Construction verifies the
installed distribution version before any PortHandler is created.  The
repository configuration still contains ``device = SELECTION REQUIRED``, so
the higher-level bus controller refuses to instantiate an active session.
"""

from __future__ import annotations

import importlib
from importlib import metadata
from typing import Mapping

from .dynamixel_bus import BusError


PINNED_DISTRIBUTION = "dynamixel-sdk"
PINNED_VERSION = "4.0.5"
PROTOCOL_VERSION = 2.0


def _encoded(value: int, size: int, signed: bool) -> int:
    minimum = -(1 << (size * 8 - 1)) if signed else 0
    maximum = (1 << (size * 8 - (1 if signed else 0))) - 1
    if not minimum <= int(value) <= maximum:
        raise BusError(f"value {value} does not fit {'signed' if signed else 'unsigned'} {size}-byte register")
    return int(value) & ((1 << (size * 8)) - 1)


def _decoded(value: int, size: int, signed: bool) -> int:
    value = int(value) & ((1 << (size * 8)) - 1)
    sign_bit = 1 << (size * 8 - 1)
    return value - (1 << (size * 8)) if signed and value & sign_bit else value


class SdkTransport:
    """Protocol-2.0 transport with checked communication and packet errors."""

    def __init__(self, device: str, baud_rate: int = 1_000_000) -> None:
        try:
            installed_version = metadata.version(PINNED_DISTRIBUTION)
        except metadata.PackageNotFoundError as exc:
            raise BusError(f"{PINNED_DISTRIBUTION} {PINNED_VERSION} is required") from exc
        if installed_version != PINNED_VERSION:
            raise BusError(f"{PINNED_DISTRIBUTION} {PINNED_VERSION} is required")
        if not device or "SELECTION" in device.upper() or "REQUIRED" in device.upper():
            raise BusError("a released serial device path is required")
        self.sdk = importlib.import_module("dynamixel_sdk")
        self.device = device
        self.baud_rate = int(baud_rate)
        self.port = self.sdk.PortHandler(device)
        self.packet = self.sdk.PacketHandler(PROTOCOL_VERSION)
        self._opened = False

    def open(self) -> None:
        if not self.port.openPort():
            raise BusError(f"failed to open DYNAMIXEL port {self.device}")
        self._opened = True
        if not self.port.setBaudRate(self.baud_rate):
            self.close()
            raise BusError(f"failed to set DYNAMIXEL baud rate {self.baud_rate}")

    def close(self) -> None:
        if self._opened:
            self.port.closePort()
            self._opened = False

    def discover(self) -> Mapping[int, int]:
        data, comm_result = self.packet.broadcastPing(self.port)
        self._check_comm(comm_result, 0, "broadcast ping")
        return {int(actuator_id): int(values[0]) for actuator_id, values in data.items()}

    def read(self, actuator_id: int, address: int, size: int, *, signed: bool = False) -> int:
        method = {
            1: self.packet.read1ByteTxRx,
            2: self.packet.read2ByteTxRx,
            4: self.packet.read4ByteTxRx,
        }.get(size)
        if method is None:
            raise BusError(f"unsupported DYNAMIXEL register size {size}")
        value, comm_result, packet_error = method(self.port, actuator_id, address)
        self._check_comm(comm_result, packet_error, f"read ID {actuator_id} address {address}")
        return _decoded(value, size, signed)

    def write(self, actuator_id: int, address: int, size: int, value: int, *, signed: bool = False) -> None:
        method = {
            1: self.packet.write1ByteTxRx,
            2: self.packet.write2ByteTxRx,
            4: self.packet.write4ByteTxRx,
        }.get(size)
        if method is None:
            raise BusError(f"unsupported DYNAMIXEL register size {size}")
        comm_result, packet_error = method(
            self.port, actuator_id, address, _encoded(value, size, signed)
        )
        self._check_comm(comm_result, packet_error, f"write ID {actuator_id} address {address}")

    def sync_write(self, address: int, size: int, values: Mapping[int, int], *, signed: bool = False) -> None:
        if not values:
            raise BusError("empty synchronous write is prohibited")
        group = self.sdk.GroupSyncWrite(self.port, self.packet, address, size)
        for actuator_id, value in sorted(values.items()):
            encoded = _encoded(value, size, signed)
            data = [(encoded >> (8 * index)) & 0xFF for index in range(size)]
            if not group.addParam(int(actuator_id), data):
                group.clearParam()
                raise BusError(f"failed to add ID {actuator_id} to synchronous write")
        comm_result = group.txPacket()
        group.clearParam()
        self._check_comm(comm_result, 0, f"sync write address {address}")

    def _check_comm(self, comm_result: int, packet_error: int, operation: str) -> None:
        if comm_result != self.sdk.COMM_SUCCESS:
            raise BusError(f"{operation}: {self.packet.getTxRxResult(comm_result)}")
        if packet_error:
            raise BusError(f"{operation}: {self.packet.getRxPacketError(packet_error)}")
