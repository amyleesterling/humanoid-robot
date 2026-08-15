#!/usr/bin/env python3
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
