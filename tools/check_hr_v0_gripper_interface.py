"""Fail-closed source and KiCad checks for HR-V0-GRIP-ELEC-P0.1."""

from __future__ import annotations

import csv
import hashlib
import re
from pathlib import Path

import cadquery as cq


ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT / "electrical/kicad/hr-v0-gripper-interface"


def rows(path: Path):
    with path.open(encoding="utf-8",newline="") as handle:
        return list(csv.DictReader(handle))


def digest(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> int:
    manifests = rows(ROOT / "cad/vendor/pololu/maestro-1350-r112/source-manifest-p0.1.csv") + rows(ROOT / "electrical/vendor/pololu/d24v22f6-2859-r112/source-manifest-p0.1.csv")
    expected={
        "R112-MAE-001":ROOT/"cad/vendor/pololu/maestro-1350-r112/maestro.pdf",
        "R112-MAE-002":ROOT/"cad/vendor/pololu/maestro-1350-r112/micro-maestro-dimensions.pdf",
        "R112-MAE-003":ROOT/"cad/vendor/pololu/maestro-1350-r112/micro-maestro.step",
        "R112-REG-001":ROOT/"electrical/vendor/pololu/d24v22f6-2859-r112/d24v22fx-dimensions.pdf",
        "R112-REG-002":ROOT/"electrical/vendor/pololu/d24v22f6-2859-r112/d24v22fx.step",
    }
    for row in manifests:
        path=expected[row["artifact_id"]]
        assert path.stat().st_size == int(row["size_bytes"])
        assert digest(path) == row["sha256"]
        assert row["access_date"] == "2026-08-08"
    maestro=cq.importers.importStep(str(ROOT/"cad/vendor/pololu/maestro-1350-r112/micro-maestro.step"))
    assert len(maestro.solids().vals()) == 3
    mb=maestro.val().BoundingBox()
    assert all(abs(a-b)<1e-4 for a,b in zip((mb.xlen,mb.ylen,mb.zlen),(31.2420001,21.5900002,11.5)))
    regulator=cq.importers.importStep(str(ROOT/"electrical/vendor/pololu/d24v22f6-2859-r112/d24v22fx.step"))
    assert len(regulator.solids().vals()) == 1
    rb=regulator.val().BoundingBox()
    assert all(abs(a-b)<1e-4 for a,b in zip((rb.xlen,rb.ylen,rb.zlen),(17.7800002,17.7800002,8.21924377)))
    erc=(OUT/"validation/hr-v0-gripper-interface-erc.rpt").read_text(encoding="utf-8-sig")
    assert re.search(r"ERC messages:\s+0\s+Errors\s+0\s+Warnings",erc)
    net=(OUT/"validation/hr-v0-gripper-interface.net").read_text(encoding="utf-8-sig")
    for token in ("POST_K1_K2_24V","GRIP_24V_PROTECTED","GRIP_6V","GRIP_PWM","GRIP_FB","GRIP_PG_SENSE","unconnected-(DCGRIP1-ENABLE"):
        assert token in net
    bom=rows(OUT/"bom.csv")
    assert [r["reference"] for r in bom] == ["JGIN1","FGRIP1","DCGRIP1","JUSB1","UGRIP1","RPG1","MGRIP1"]
    assert all("APPROVED" in r["warning"] for r in bom)
    sch=(OUT/"01_gripper_interface.kicad_sch").read_text(encoding="utf-8")
    for token in ("LOGICAL TERMINALS ONLY","No restart motion","SELECTION REQUIRED","ZERO SAFETY CREDIT"):
        assert token in sch
    readme=(OUT/"README.md").read_text(encoding="utf-8")
    for token in ("zero safety credit","startup/error Off","SELECTION REQUIRED","cannot itself issue a PWM command"):
        assert token in readme
    assert (OUT/"output/hr-v0-gripper-interface-preliminary.pdf").stat().st_size > 10000
    assert len(list((OUT/"output").glob("*.svg"))) == 2
    manifest=rows(OUT/"SOURCE-MANIFEST.csv")
    assert len(manifest) >= 12 and all(len(r["sha256"])==64 for r in manifest)
    guide=(ROOT/"release/hr-v0/gripper-interface-p0.1/index.html").read_text(encoding="utf-8")
    for token in ("font:16px", "font-size:14px", "PRELIMINARY", "0 errors / 0 warnings", "zero functional-safety credit", "data-view", "addEventListener"):
        assert token in guide
    assert "@media(max-width:700px)" in guide
    print("HR-V0 gripper interface check passed: 5 manufacturer payloads hash-checked; 4 STEP solids parsed; native KiCad ERC 0 errors / 0 warnings")
    print("PRELIMINARY - ORDINARY CONTROL ONLY - NOT APPROVED FOR FABRICATION OR ENERGIZATION")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
