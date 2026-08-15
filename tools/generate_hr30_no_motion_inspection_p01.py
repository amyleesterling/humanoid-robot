#!/usr/bin/env python3
"""Generate the HR-30 guarded no-motion actuator inspection package P0.1."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import cadquery as cq


ROOT = Path(__file__).resolve().parents[1]
WB = ROOT / "hr30" / "whole-body-p0.1"
STATION = WB / "electrical" / "axis-commissioning-station-p0.1"
OUT = STATION / "no-motion-inspection-p0.1"
REL_STATION = ROOT / "release" / "hr30" / "whole-body-p0.1" / "electrical" / "axis-commissioning-station-p0.1"
WARNING = "PRELIMINARY - NO-MOTION INSPECTION CANDIDATE - NOT APPROVED FOR CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
WHOLE_WARNING = "PRELIMINARY - CONFIGURATION AND PACKAGING CAD ONLY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, POWERED TESTING, MOTION, OR ENERGIZATION"

MODELS = [
    {
        "model": "XH540-W270-R", "family": "ROBOTIS-540", "form": "540",
        "step": ROOT / "cad/vendor/robotis/XMHD-540.N101.I101.STP",
        "sha": "6e0df65638b3a23b12c7ee1114d4d06f5ec2de9e84e3ffddd7e115e8f8faf39f",
        "bus": "RS-485 X4P", "mass_g": 165, "official": "https://docs.robotis.com/docs/dxl/model_reference/x_series/xh_series/xh540-w270/",
    },
    {
        "model": "XM540-W270-R", "family": "ROBOTIS-540", "form": "540",
        "step": ROOT / "cad/vendor/robotis/XMHD-540.N101.I101.STP",
        "sha": "6e0df65638b3a23b12c7ee1114d4d06f5ec2de9e84e3ffddd7e115e8f8faf39f",
        "bus": "RS-485 X4P", "mass_g": 165, "official": "https://docs.robotis.com/docs/dxl/model_reference/x_series/xm_series/xm540-w270/",
    },
    {
        "model": "XM430-W350-R", "family": "ROBOTIS-X430", "form": "X430",
        "step": ROOT / "cad/vendor/robotis/x430-fr12-r91/x-430_idle.stp",
        "sha": "7ff4e39475245d5c1fc4f703e9241fca1a09d57aed920274498dbe2cd5e31e22",
        "bus": "RS-485 X4P", "mass_g": 82, "official": "https://docs.robotis.com/docs/dxl/model_reference/x_series/xm_series/xm430-w350/",
    },
    {
        "model": "XC330-T288-T", "family": "ROBOTIS-XC330", "form": "XC330",
        "step": ROOT / "cad/vendor/robotis/xc330/XL-XC-330-official-source.stp",
        "sha": "e2f7b060801a1d6a21f23bca2554f29a402f7d73b8498cb201c9e6adf3139eb6",
        "bus": "TTL X3P", "mass_g": 23, "official": "https://docs.robotis.com/docs/dxl/model_reference/x_series/xc_series/xc330-t288/",
    },
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise RuntimeError(f"refusing empty CSV: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def box(w: float, d: float, h: float, x: float, y: float, z: float) -> cq.Shape:
    return cq.Workplane("XY").box(w, d, h, centered=(True, True, False)).translate((x, y, z)).val()


def fixture(shape: cq.Shape, form: str) -> tuple[cq.Shape, cq.Shape, cq.Shape, dict]:
    b = shape.BoundingBox()
    cx, cy = (b.xmin + b.xmax) / 2, (b.ymin + b.ymax) / 2
    clearance, wall, floor_t = 2.5, 3.0, 5.0
    outer_w, outer_d = b.xlen + 2 * (clearance + wall), b.ylen + 2 * (clearance + wall)
    floor_z = b.zmin - 6.0
    floor = box(outer_w + 18, outer_d + 18, floor_t, cx, cy, floor_z)
    # Four bench holes and four cover-retention holes are explicit and separate.
    for px in (cx - outer_w / 2 - 5, cx + outer_w / 2 + 5):
        for py in (cy - outer_d / 2 - 5, cy + outer_d / 2 + 5):
            floor = floor.cut(cq.Workplane("XY").circle(2.75).extrude(floor_t + 2).translate((px, py, floor_z - 1)).val())
    for px in (cx - outer_w / 2 + 4, cx + outer_w / 2 - 4):
        for py in (cy - outer_d / 2 + 4, cy + outer_d / 2 - 4):
            floor = floor.cut(cq.Workplane("XY").circle(2.15).extrude(floor_t + 2).translate((px, py, floor_z - 1)).val())
    # A 1 mm-deep locating pocket controls X/Y but does not claim received-part fit.
    pocket = box(b.xlen + 1.5, b.ylen + 1.5, 1.2, cx, cy, floor_z + floor_t - 0.2)
    base = floor.cut(pocket)
    # Four external stops and two strap-slot pairs retain the actuator body without a horn/link.
    stop_h = 7.0
    for px in (b.xmin - clearance - wall / 2, b.xmax + clearance + wall / 2):
        base = base.fuse(box(wall, b.ylen + 2 * clearance, stop_h, px, cy, floor_z + floor_t))
    for py in (b.ymin - clearance - wall / 2, b.ymax + clearance + wall / 2):
        base = base.fuse(box(b.xlen + 2 * clearance, wall, stop_h, cx, py, floor_z + floor_t))
    strap_ys = (cy - b.ylen * 0.24, cy + b.ylen * 0.24)
    for sy in strap_ys:
        for sx in (cx - outer_w / 2 + 5.0, cx + outer_w / 2 - 5.0):
            slot = box(3.0, 13.0, floor_t + 2, sx, sy, floor_z - 1)
            base = base.cut(slot)
    cover_z0 = floor_z + floor_t
    cover_top = b.zmax + 10.0
    cover_h = cover_top - cover_z0
    outer = box(outer_w, outer_d, cover_h, cx, cy, cover_z0)
    inner = box(outer_w - 2 * wall, outer_d - 2 * wall, cover_h - wall, cx, cy, cover_z0 - 0.5)
    cover = outer.cut(inner)
    # Rear cable exit remains below the guarded output plane; output top is fully enclosed.
    cable_exit = box(min(22.0, b.xlen * 0.75), wall + 4, 15.0, cx, cy + outer_d / 2, b.zmin + 4)
    cover = cover.cut(cable_exit)
    # Side ventilation openings, all at least 12 mm below the output-guard roof.
    for zc in (b.zmin + b.zlen * 0.28, b.zmin + b.zlen * 0.55):
        for side in (-1, 1):
            vent = box(wall + 4, max(12.0, outer_d * 0.38), 5.0, cx + side * outer_w / 2, cy, zc)
            cover = cover.cut(vent)
    # Cover screw clearances align to the base holes.
    for px in (cx - outer_w / 2 + 4, cx + outer_w / 2 - 4):
        for py in (cy - outer_d / 2 + 4, cy + outer_d / 2 - 4):
            cover = cover.cut(cq.Workplane("XY").circle(2.15).extrude(cover_h + 2).translate((px, py, cover_z0 - 1)).val())
    straps = [box(b.xlen + 4, 12.0, 1.5, cx, sy, b.zmax + 1.0) for sy in strap_ys]
    assembly = cq.Compound.makeCompound([base, cover, shape, *straps])
    dims = {
        "form_factor": form, "vendor_bbox_x_mm": round(b.xlen, 6), "vendor_bbox_y_mm": round(b.ylen, 6),
        "vendor_bbox_z_mm": round(b.zlen, 6), "base_x_mm": round(outer_w + 18, 3),
        "base_y_mm": round(outer_d + 18, 3), "overall_z_mm": round(cover_top - floor_z, 3),
        "body_xy_clearance_per_side_mm": clearance, "cover_wall_mm": wall,
        "output_guard_clearance_above_vendor_bbox_mm": 10.0,
        "strap_width_mm": 12.0, "bench_hole_diameter_mm": 5.5,
        "cover_hole_diameter_mm": 4.3, "cable_exit_max_width_mm": min(22.0, b.xlen * 0.75),
    }
    return base, cover, assembly, dims


def inspector_source() -> str:
    return r'''#!/usr/bin/env python3
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
'''


def test_source() -> str:
    return r'''#!/usr/bin/env python3
"""Offline-only test for the HR-30 read-only inspector."""
import contextlib, io
import importlib.util
from pathlib import Path
P=Path(__file__).with_name("hr30_read_only_inspector.py")
s=importlib.util.spec_from_file_location("inspector",P); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
class Port:
    def __init__(self,name): self.name=name; self.calls=[]
    def openPort(self): self.calls.append("open"); return True
    def setBaudRate(self,b): self.calls.append(("host_baud",b)); return True
    def closePort(self): self.calls.append("close")
class Packet:
    def __init__(self,p): self.calls=[]
    def ping(self,p,i): self.calls.append(("ping",i)); return 1100,0,0
    def read1ByteTxRx(self,p,i,a): self.calls.append(("read1",i,a)); return (0 if a in (64,70) else 1),0,0
    def read2ByteTxRx(self,p,i,a): self.calls.append(("read2",i,a)); return (110 if a==144 else 1100),0,0
class SDK:
    COMM_SUCCESS=0
    PortHandler=Port
    PacketHandler=Packet
r=m.inspect(SDK,"SIMULATED",57600,1)
assert r["ping_model_number"]==1100 and r["values"]["torque_enable"]["raw"]==0
assert set(r["values"])==set(m.READS)
with contextlib.redirect_stderr(io.StringIO()):
    try: m.parse_args(["--port","SIM","--baud","57600","--id","254"])
    except SystemExit: pass
    else: raise AssertionError("broadcast ID accepted")
print("PASS: offline fake transport exercised ping + nine single-ID reads; no hardware accessed")
'''


def build() -> None:
    if OUT.exists(): shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    unique_shapes: dict[str, cq.Shape] = {}
    dimension_rows, model_rows, part_rows = [], [], []
    lineup = cq.Assembly(name="HR30_NO_MOTION_INSPECTION_P01_NOT_RELEASED")
    offsets = [-150, -50, 50, 150]
    for index, model in enumerate(MODELS):
        if sha(model["step"]) != model["sha"]: raise RuntimeError(f"vendor STEP hash drift: {model['model']}")
        native = cq.importers.importStep(str(model["step"])).val()
        base, cover, assembly, dims = fixture(native, model["form"])
        stem = model["model"].lower().replace("-", "_")
        cq.exporters.export(base, str(OUT / f"{stem}_restraint_base.step"))
        cq.exporters.export(cover, str(OUT / f"{stem}_output_guard.step"))
        cq.exporters.export(base, str(OUT / f"{stem}_restraint_base.stl"), tolerance=0.1)
        cq.exporters.export(cover, str(OUT / f"{stem}_output_guard.stl"), tolerance=0.1)
        cq.exporters.export(assembly, str(OUT / f"{stem}_guarded_fixture.step"))
        location = cq.Location(cq.Vector(offsets[index], 0, 35))
        lineup.add(base.moved(location), name=f"{model['model']}_RESTRAINT_BASE", color=cq.Color(0.03,0.20,0.38,1.0))
        lineup.add(native.moved(location), name=f"{model['model']}_VENDOR_ACTUATOR", color=cq.Color(0.95,0.66,0.08,1.0))
        lineup.add(cover.moved(location), name=f"{model['model']}_OUTPUT_GUARD", color=cq.Color(0.43,0.78,0.94,0.42))
        dimension_rows.append({"model":model["model"], **dims, "dimension_basis":"SHA-bound vendor STEP; native +Z output datum"})
        model_rows.append({
            "model":model["model"],"form_factor":model["form"],"bus":model["bus"],"candidate_mass_g":model["mass_g"],
            "vendor_step":model["step"].relative_to(ROOT).as_posix(),"vendor_step_sha256":model["sha"],"native_output_axis":"+Z through native origin",
            "horn_or_body_link_installed":"NO","output_guard_present":"YES - CAD CANDIDATE","restraint_state":"UNVALIDATED - RECEIVED FIT AND BENCH TEST REQUIRED",
            "official_source":model["official"],"source_accessed":"2026-08-15","authority":"NO CONNECTION, POWERED TEST, MOTION OR ENERGIZATION AUTHORITY",
        })
        part_rows += [
            {"model":model["model"],"part":f"{stem}_restraint_base","candidate_material":"PETG or polycarbonate - SELECTION REQUIRED","quantity":1,"function":"bench bolting, XY pocket and dual strap slots","validation":"PRINT / FIT / RETENTION TEST REQUIRED"},
            {"model":model["model"],"part":f"{stem}_output_guard","candidate_material":"transparent polycarbonate preferred - SELECTION REQUIRED","quantity":1,"function":"fully cover +Z output region while preserving side ventilation and cable exit","validation":"PRINT / FIT / ACCESS PROBE TEST REQUIRED"},
            {"model":model["model"],"part":"12 mm nonconductive hook-and-loop strap","candidate_material":"SELECTION REQUIRED","quantity":2,"function":"retain actuator body to base without a horn or robot link","validation":"RECEIVED STRAP / SLIP / HEAT TEST REQUIRED"},
            {"model":model["model"],"part":"M4 cover fastener + captive insert","candidate_material":"SELECTION REQUIRED","quantity":4,"function":"retain output guard to base","validation":"TORQUE / PULL / RETENTION TEST REQUIRED"},
        ]
    lineup.save(str(OUT / "HR30_four_model_guarded_fixture_lineup.glb"))
    cq.exporters.export(cq.Compound.makeCompound([cq.importers.importStep(str(OUT / f"{m['model'].lower().replace('-', '_')}_guarded_fixture.step")).val().translate((offsets[i],0,35)) for i,m in enumerate(MODELS)]), str(OUT / "HR30_four_model_guarded_fixture_lineup.step"))
    write_csv(OUT / "actuator-fixture-register.csv", model_rows)
    write_csv(OUT / "fixture-dimension-register.csv", dimension_rows)
    write_csv(OUT / "fixture-part-register.csv", part_rows)
    source_rows = [{"source_id":m["model"],"official_url":m["official"],"record":"current ROBOTIS model page and SHA-bound manufacturer STEP","revision_or_date":"live official Docs; accessed 2026-08-15; visible page revision not stated"} for m in MODELS]
    source_rows += [
        {"source_id":"DXL-PROTOCOL-2","official_url":"https://docs.robotis.com/docs/dxl/protocol/protocol2/","record":"Protocol 2.0 read instruction and explicit device addressing","revision_or_date":"live official Docs; accessed 2026-08-15"},
        {"source_id":"DXL-SDK","official_url":"https://docs.robotis.com/docs/software/dynamixel_sdk/overview/","record":"official Python-capable DYNAMIXEL SDK overview","revision_or_date":"live official Docs; accessed 2026-08-15"},
        {"source_id":"DXL-SDK-SOURCE","official_url":"https://github.com/ROBOTIS-GIT/DynamixelSDK","record":"official source repository; release 4.0.5 shown 2026-05-06","revision_or_date":"accessed 2026-08-15; exact installed version remains approval input"},
    ]
    write_csv(OUT / "primary-source-register.csv", source_rows)
    write_csv(OUT / "inspection-field-register.csv", [
        {"field":n,"address":a,"size_bytes":s,"scale":scale,"access_used":"READ ONLY","model_scope":"all four candidates; received firmware/control-table match required"}
        for n,(a,s,scale) in {"model_number":(0,2,1),"firmware_version":(6,1,1),"configured_id":(7,1,1),"baud_rate_code":(8,1,1),"protocol_type":(13,1,1),"torque_enable":(64,1,1),"hardware_error_status":(70,1,1),"present_input_voltage":(144,2,0.1),"present_temperature":(146,1,1)}.items()
    ])
    (OUT / "hr30_read_only_inspector.py").write_text(inspector_source(), encoding="utf-8")
    (OUT / "test_read_only_inspector.py").write_text(test_source(), encoding="utf-8")
    (OUT / "inspection-status.json").write_text(json.dumps({
        "identifier":"HR30-NO-MOTION-INSPECTION-P0.1","warning":WARNING,"model_count":4,"physical_form_factor_count":3,
        "sha_bound_vendor_geometry":True,"guarded_fixture_cad_present":True,"read_only_inspector_present":True,"device_write_api_present":False,
        "broadcast_or_scan_path_present":False,"offline_simulation_passed":False,"received_fit_validated":False,"fixture_retention_validated":False,
        "software_environment_approved":False,"hardware_inspection_executed":False,"connection_authority":False,"powered_test_authority":False,
        "motion_authority":False,"energization_authority":False,
    },indent=2)+"\n",encoding="utf-8")
    rows = "".join(f"<tr><td>{m['model']}</td><td>{m['bus']}</td><td>{m['form']}</td><td>+Z fully guarded</td><td>received fit required</td></tr>" for m in MODELS)
    (OUT / "index.html").write_text(f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 no-motion inspection fixtures</title><script type="module" src="https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js"></script><style>:root{{--navy:#082f58;--blue:#14689c;--sky:#d6f1ff;--gold:#f2b928;--paper:#f8fcff}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--navy);font:clamp(16px,1.15vw,19px)/1.55 system-ui,sans-serif}}header{{padding:clamp(1.5rem,5vw,4rem);background:linear-gradient(135deg,var(--sky),#fff);border-bottom:7px solid var(--gold)}}header>div,main{{max-width:1200px;margin:auto}}h1{{font-size:clamp(2.2rem,6vw,4.8rem);line-height:1.04;max-width:18ch}}h2{{font-size:clamp(1.7rem,3vw,2.8rem)}}main{{padding:2rem clamp(1rem,4vw,3rem) 5rem}}.warning,.hold{{border:3px solid #a86f00;background:#fff0b5;border-radius:16px;padding:1rem;font-weight:800}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,260px),1fr));gap:1rem;margin:1.5rem 0}}article,.panel{{padding:1rem;background:#fff;border:2px solid var(--blue);border-radius:16px}}model-viewer{{width:100%;height:560px;background:#fff;border:2px solid #8bc5e5}}.tablewrap{{overflow:auto;border:2px solid var(--blue);border-radius:16px}}table{{border-collapse:collapse;width:100%;min-width:780px;background:#fff}}th,td{{padding:.8rem;border-bottom:1px solid #c7dfec;text-align:left;font-size:14px}}th{{background:var(--navy);color:#fff}}code{{font-size:14px}}a{{color:#075d98;font-weight:800}}</style></head><body><header><div><p class="warning">{WARNING}</p><h1>Guard the output. Read one ID. Send no motion.</h1><p>Four HR-30 actuator candidates are covered by three fixture sizes derived from the exact manufacturer STEP envelopes. Every station is body-restrained, horn-free and enclosed above the native +Z output.</p></div></header><main><div class="hold"><h2>Still not permission to connect</h2><p>The CAD, software and control-table map are engineering candidates. Print quality, received fit, guard retention, approved SDK environment, electrical review and a separately signed connection procedure remain open.</p></div><h2>Interactive guarded lineup</h2><model-viewer src="HR30_four_model_guarded_fixture_lineup.glb" camera-controls shadow-intensity="0.9" alt="Four guarded DYNAMIXEL actuator inspection fixtures"></model-viewer><p><a href="HR30_four_model_guarded_fixture_lineup.step">lineup STEP</a> · <a href="actuator-fixture-register.csv">fixture register</a> · <a href="fixture-dimension-register.csv">dimensions</a> · <a href="fixture-part-register.csv">parts</a></p><h2>Physical boundary</h2><div class="grid"><article><h3>No horn or body link</h3><p>The fixture holds only the actuator body. The output cannot be attached to the humanoid during this inspection.</p></article><article><h3>Closed output roof</h3><p>The guard roof remains 10 mm above the vendor bounding box and cannot be removed while the station is connected.</p></article><article><h3>Separate cable exit</h3><p>The rear exit is below the guarded output plane. Side vents preserve airflow while preventing direct top access.</p></article></div><div class="tablewrap"><table><thead><tr><th>Model</th><th>Bus</th><th>Fixture</th><th>Output</th><th>Status</th></tr></thead><tbody>{rows}</tbody></table></div><h2>Read-only inspector</h2><div class="panel"><p><a href="hr30_read_only_inspector.py">Python source</a> · <a href="test_read_only_inspector.py">offline test</a> · <a href="inspection-field-register.csv">nine-field register</a> · <a href="primary-source-register.csv">primary sources</a></p><p>Dry run: <code>python hr30_read_only_inspector.py --port COM5 --baud 57600 --id 1</code></p><p>Hardware execution additionally requires <code>--execute-read-only</code>. The program accepts one explicit ID from 0–252, rejects broadcast/reserved IDs, never scans, and exposes only ping plus one- and two-byte read calls. There is no device-write, reboot, reset, firmware, goal, torque-enable, Sync Write or Bulk Write call path.</p></div></main></body></html>''',encoding="utf-8")
    (OUT / "README.md").write_text(f"# HR-30 guarded no-motion inspection P0.1\n\n**{WARNING}**\n\nThis package provides four explicit actuator inspection fixtures across three exact vendor form factors, plus a single-ID Protocol 2.0 inspector with no device-write path. It is a candidate for closing the design side of station holds CS-H06 and CS-H07; received fit, retention, approved software environment, executed inspection and every connection/powered-test/motion/energization authority remain open.\n",encoding="utf-8")


def integrate() -> None:
    status_path = OUT / "inspection-status.json"
    status = json.loads(status_path.read_text(encoding="utf-8")); status["offline_simulation_passed"] = True
    status_path.write_text(json.dumps(status,indent=2)+"\n",encoding="utf-8")
    station_status_path = STATION / "commissioning-status.json"
    ss = json.loads(station_status_path.read_text(encoding="utf-8")); ss.update({
        "no_motion_fixture_design_present":True,"guarded_actuator_model_count":4,"guarded_fixture_form_factor_count":3,
        "read_only_inspector_present":True,"read_only_inspector_device_write_api_present":False,"read_only_inspector_offline_test_passed":True,
        "mechanical_restraint_physically_validated":False,"host_software_environment_approved":False,
    }); station_status_path.write_text(json.dumps(ss,indent=2)+"\n",encoding="utf-8")
    holds_path = STATION / "open-holds.csv"
    with holds_path.open(encoding="utf-8",newline="") as h: holds=list(csv.DictReader(h))
    for row in holds:
        if row["hold_id"] == "CS-H06": row["unresolved_evidence"] = "print, received-fit, strap-slip, cover-retention and access-probe validation of the four-model no-motion fixture design"
        if row["hold_id"] == "CS-H07": row["unresolved_evidence"] = "approved host OS, exact DYNAMIXEL SDK version, code hash, operator review and log disposition for the write-free inspector"
    write_csv(holds_path, holds)
    marker_a, marker_b = "<!-- NO-MOTION-P01 START -->", "<!-- NO-MOTION-P01 END -->"
    station_page = STATION / "index.html"; text = re.sub(re.escape(marker_a)+r"[\s\S]*?"+re.escape(marker_b),"",station_page.read_text(encoding="utf-8"))
    block = f'''{marker_a}<h2>No-motion fixture and write-free inspector</h2><div class="panel"><p>The station now has exact-envelope restraint and output-guard CAD for XH540, XM540, XM430 and XC330, plus a single-ID inspector whose AST contains no DYNAMIXEL device-write method. These artifacts do not close received-fit, software approval or connection authority.</p><p><a href="no-motion-inspection-p0.1/index.html">Open the interactive no-motion guide</a> · <a href="no-motion-inspection-p0.1/HR30_four_model_guarded_fixture_lineup.step">fixture STEP</a> · <a href="no-motion-inspection-p0.1/hr30_read_only_inspector.py">inspector source</a>.</p></div>{marker_b}'''
    station_page.write_text(text.replace("</main>",block+"</main>"),encoding="utf-8")
    station_readme = STATION / "README.md"; text = re.sub(re.escape(marker_a)+r"[\s\S]*?"+re.escape(marker_b),"",station_readme.read_text(encoding="utf-8")).rstrip()
    station_readme.write_text(text+f"\n\n{marker_a}\n## No-motion inspection fixture\n\nExact vendor-envelope guards and a write-free single-ID inspector are in `no-motion-inspection-p0.1/`. Physical fit, retention, approved software environment and all connection/power/motion authority remain open.\n{marker_b}\n",encoding="utf-8")
    root_status_path=WB/"package-status.json"; rs=json.loads(root_status_path.read_text(encoding="utf-8")); rs.update({
        "axis_commissioning_no_motion_fixture_present":True,"axis_commissioning_guarded_model_count":4,"axis_commissioning_read_only_inspector_present":True,
        "axis_commissioning_device_write_api_present":False,"axis_commissioning_fixture_physically_validated":False,"axis_commissioning_host_software_approved":False,
        "axis_commissioning_connection_authority":False,"axis_commissioning_energization_authority":False,
    }); root_status_path.write_text(json.dumps(rs,indent=2)+"\n",encoding="utf-8")
    root_page=WB/"index.html"; text=re.sub(re.escape(marker_a)+r"[\s\S]*?"+re.escape(marker_b),"",root_page.read_text(encoding="utf-8"))
    root_block=f'''{marker_a}<section id="no-motion-inspection"><h2>Guarded actuator inspection</h2><div class="grid"><article class="card pass"><h3>4 explicit models</h3><p>Three fixture sizes derive from SHA-bound vendor geometry and fully cover the native output region.</p></article><article class="card pass"><h3>No device-write API</h3><p>The single-ID inspector exposes ping and read calls only; broadcast and scan paths are absent.</p></article><article class="card hold"><h3>Physical approval open</h3><p>Received fit, print quality, retention, SDK lock and connection authority are not yet validated.</p></article></div><p><a href="electrical/axis-commissioning-station-p0.1/no-motion-inspection-p0.1/index.html">Open the interactive fixture and inspector guide</a>.</p></section>{marker_b}'''
    root_page.write_text(text.replace("</main>",root_block+"</main>"),encoding="utf-8")
    root_readme=WB/"README.md"; text=re.sub(re.escape(marker_a)+r"[\s\S]*?"+re.escape(marker_b),"",root_readme.read_text(encoding="utf-8")).rstrip()
    root_readme.write_text(text+f"\n\n{marker_a}\n## Guarded actuator inspection\n\nThe whole-body commissioning path now includes exact-envelope, horn-free output guards for all four candidate actuator models and a single-ID Protocol 2.0 inspector with no device-write API. Physical fit, fixture retention, software approval and all connection/powered-test/motion/energization authority remain open.\n{marker_b}\n",encoding="utf-8")


def manifests_and_release() -> None:
    shutil.copy2(Path(__file__), OUT / "no-motion-inspection-source.py")
    files=sorted(p for p in OUT.rglob("*") if p.is_file() and p.name!="file-manifest.csv")
    write_csv(OUT/"file-manifest.csv",[{"path":p.relative_to(OUT).as_posix(),"bytes":p.stat().st_size,"sha256":sha(p),"warning":WARNING} for p in files])
    station_files=sorted(p for p in STATION.rglob("*") if p.is_file() and p!=STATION/"file-manifest.csv")
    write_csv(STATION/"file-manifest.csv",[{"path":p.relative_to(STATION).as_posix(),"bytes":p.stat().st_size,"sha256":sha(p),"warning":WARNING} for p in station_files])
    if REL_STATION.exists(): shutil.rmtree(REL_STATION)
    shutil.copytree(STATION,REL_STATION)
    root_manifest=WB/"file-manifest.csv"; root_files=sorted(p for p in WB.rglob("*") if p.is_file() and p!=root_manifest)
    write_csv(root_manifest,[{"path":p.relative_to(WB).as_posix(),"bytes":p.stat().st_size,"sha256":sha(p),"warning":WHOLE_WARNING} for p in root_files])
    release_root=ROOT/"release/hr30/whole-body-p0.1"; release_root.mkdir(parents=True,exist_ok=True)
    for name in ("README.md","index.html","package-status.json","file-manifest.csv"): shutil.copy2(WB/name,release_root/name)


def main() -> int:
    build()
    test_env = dict(os.environ); test_env["PYTHONDONTWRITEBYTECODE"] = "1"
    test = subprocess.run([sys.executable, str(OUT / "test_read_only_inspector.py")], cwd=OUT, capture_output=True, text=True, env=test_env)
    (OUT / "offline-test.log").write_text(test.stdout + test.stderr, encoding="utf-8")
    if test.returncode or "PASS:" not in test.stdout:
        raise RuntimeError("offline inspector test failed")
    integrate(); manifests_and_release()
    print(f"generated {OUT}")
    return 0


if __name__ == "__main__": raise SystemExit(main())
