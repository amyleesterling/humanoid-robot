#!/usr/bin/env python3
"""HR-30 single-ID, read-only DYNAMIXEL inspector. No device-write API exists here."""
from __future__ import annotations
import argparse, hashlib, importlib.metadata, json
from datetime import datetime, timezone
from pathlib import Path

PROTOCOL_VERSION = 2.0
READS = {
    "model_number": (0, 2, 1), "firmware_version": (6, 1, 1),
    "configured_id": (7, 1, 1), "baud_rate_code": (8, 1, 1),
    "protocol_type": (13, 1, 1), "torque_enable": (64, 1, 1),
    "hardware_error_status": (70, 1, 1), "present_input_voltage": (144, 2, 0.1),
    "present_temperature": (146, 1, 1),
}

def parse_args(argv=None):
    p=argparse.ArgumentParser(description="Read one explicit DYNAMIXEL ID; never scan or write")
    p.add_argument("--port", required=True); p.add_argument("--baud", type=int, required=True)
    p.add_argument("--id", type=int, required=True, dest="device_id")
    p.add_argument("--output", type=Path); p.add_argument("--execute-read-only", action="store_true")
    a=p.parse_args(argv)
    if not 0 <= a.device_id <= 252: p.error("ID must be 0..252; broadcast/reserved IDs are prohibited")
    if a.baud <= 0: p.error("baud must be positive")
    return a

def _sdk_version():
    try: return importlib.metadata.version("dynamixel-sdk")
    except importlib.metadata.PackageNotFoundError: return "NOT INSTALLED"

def inspect(sdk, serial_port, baud, device_id):
    port=sdk.PortHandler(serial_port); packet=sdk.PacketHandler(PROTOCOL_VERSION)
    if not port.openPort(): raise RuntimeError("serial port did not open")
    try:
        if not port.setBaudRate(baud): raise RuntimeError("host baud was not set")
        ping_model, comm, device_error=packet.ping(port, device_id)
        if comm != sdk.COMM_SUCCESS or device_error: raise RuntimeError(f"ping failed: comm={comm} device_error={device_error}")
        values={}
        for name,(address,size,scale) in READS.items():
            reader={1:packet.read1ByteTxRx,2:packet.read2ByteTxRx}[size]
            raw,comm,device_error=reader(port,device_id,address)
            if comm != sdk.COMM_SUCCESS or device_error: raise RuntimeError(f"read {name} failed: comm={comm} device_error={device_error}")
            values[name]={"address":address,"size_bytes":size,"raw":raw,"scaled":raw*scale}
        return {"ping_model_number":ping_model,"values":values}
    finally: port.closePort()

def main(argv=None):
    a=parse_args(argv); source=Path(__file__)
    report={"warning":"PRELIMINARY - READ-ONLY INSPECTION ONLY - NO MOTION OR ENERGIZATION AUTHORITY",
            "timestamp_utc":datetime.now(timezone.utc).isoformat(),"port":a.port,"baud":a.baud,"device_id":a.device_id,
            "protocol":PROTOCOL_VERSION,"sdk_version":_sdk_version(),"inspector_sha256":hashlib.sha256(source.read_bytes()).hexdigest(),
            "device_write_path_present":False,"broadcast_or_scan_present":False,"executed":False}
    if a.execute_read_only:
        import dynamixel_sdk
        report["inspection"]=inspect(dynamixel_sdk,a.port,a.baud,a.device_id); report["executed"]=True
        report["torque_enable_zero_observed"]=report["inspection"]["values"]["torque_enable"]["raw"] == 0
    else: report["plan"]="DRY RUN ONLY; add --execute-read-only only under a separately approved connection procedure"
    text=json.dumps(report,indent=2)+"\n"
    if a.output: a.output.write_text(text,encoding="utf-8")
    print(text,end="")
    return 0 if not report["executed"] or report.get("torque_enable_zero_observed") else 3

if __name__ == "__main__": raise SystemExit(main())
