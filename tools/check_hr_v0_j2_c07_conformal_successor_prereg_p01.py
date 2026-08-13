#!/usr/bin/env python3
"""Checker for the frozen R291 successor mesh prescription."""
from __future__ import annotations
import csv, hashlib, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"mechanical/analysis/hr-v0-j2-c07-conformal-successor-prereg-p0.1"
RELEASE=ROOT/"release/hr-v0/j2-c07-conformal-successor-prereg-p0.1"
GEN=ROOT/"tools/generate_hr_v0_j2_c07_conformal_successor_prereg_p01.py"
WARNING="PRELIMINARY - SUCCESSOR MESH PREREGISTRATION ONLY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def fail(m:str)->None:raise SystemExit(f"R291 prereg check failed: {m}")
def rows(name:str)->list[dict[str,str]]:
    with (OUT/name).open(newline="",encoding="utf-8") as s:return list(csv.DictReader(s))
def main()->int:
    required={"README.md","analysis-status.json","exact-face-target-register.csv","exact-volume-target-register.csv","execution-provenance.json","file-manifest.csv","frozen-successor-protocol.json"}
    if {p.name for p in OUT.iterdir()}!=required or {p.name for p in RELEASE.iterdir()}!=required:fail("file set drift")
    manifest=rows("file-manifest.csv")
    if {r["relative_path"] for r in manifest}!=required-{"file-manifest.csv"}:fail("manifest membership")
    for r in manifest:
        p=OUT/r["relative_path"]
        if sha(p)!=r["sha256"] or p.stat().st_size!=int(r["bytes"]):fail(f"manifest drift {p}")
    for name in required:
        if sha(OUT/name)!=sha(RELEASE/name):fail(f"mirror drift {name}")
    faces=rows("exact-face-target-register.csv");volumes=rows("exact-volume-target-register.csv")
    if len(faces)!=6 or len({r["geometric_signature_sha256"] for r in faces})!=6:fail("face target identity/count")
    if sum(r["selection_basis"]=="R290_OBSERVED_FAILURE_FACE" for r in faces)!=4 or sum(r["selection_basis"]=="X_MIRROR_CLOSURE" for r in faces)!=2:fail("mirror closure count")
    if len(volumes)!=4 or {r["exact_zone_id"] for r in volumes}!={"C07-PE-EAST-STRAIGHT","C07-PE-NORTH-STRAIGHT","C07-PE-SOUTH-STRAIGHT","C07-PE-WEST-STRAIGHT"}:fail("volume target identity/count")
    protocol=json.loads((OUT/"frozen-successor-protocol.json").read_text(encoding="utf-8"));status=json.loads((OUT/"analysis-status.json").read_text(encoding="utf-8"))
    if protocol["additional_volume_field"]["size_min_mm"]!=0.18 or protocol["additional_face_field"]["size_min_mm"]!=0.35:fail("frozen field drift")
    if not protocol["stop_rule"].startswith("one execution only") or not status["thresholds_unchanged"]:fail("stop/threshold rule drift")
    for key in ("mesh_executed","r279_c02_complete","r278_h02_closed","capacity_credit","safety_credit","work_authority"):
        if status[key] is not False:fail(f"fail-closed status {key}")
    provenance=json.loads((OUT/"execution-provenance.json").read_text(encoding="utf-8"))
    if provenance["generator_sha256"]!=sha(GEN):fail("generator provenance")
    print("PASS: R291 successor prereg frozen; 4 exact failed volumes + 6 symmetry-closed exact faces; no mesh/credit/authority")
    return 0
if __name__=="__main__":raise SystemExit(main())
