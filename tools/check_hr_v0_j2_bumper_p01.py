#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; PKG=ROOT/"mechanical/stops/hr-v0-j2-soft-contact-pad-p0.1"; REL=ROOT/"release/hr-v0/j2-soft-contact-pad-p0.1"; WARNING="PRELIMINARY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
def rows(p):
    with p.open(newline="",encoding="utf-8-sig") as f:return list(csv.DictReader(f))
def need(x,m):
    if not x:raise SystemExit(m)
def mf(d):
    rs=rows(d/"file-manifest.csv"); fs=sorted(p for p in d.rglob("*") if p.is_file() and p.name!="file-manifest.csv"); need(len(rs)==len(fs),"manifest count"); by={r["relative_path"]:r for r in rs}
    for p in fs:
      n=p.relative_to(d).as_posix(); need(n in by and by[n]["sha256"]==hashlib.sha256(p.read_bytes()).hexdigest() and by[n]["warning"]==WARNING,f"manifest {n}")
def main():
    s=json.loads((PKG/"package-status.json").read_text(encoding="utf-8")); need(s["identifier"]=="HR-V0-J2-SOFT-CONTACT-PAD-P0.1" and s["round"]=="R275","identity")
    for k in ("candidate_selected","sole_structural_stop","procurement_authorized","assembly_authorized","powered_testing_authorized","motion_authorized","energization_authorized","safety_credit"):need(s[k] is False,k)
    need(len(rows(PKG/"source-register.csv"))==4 and len(rows(PKG/"dynamic-load-case-register.csv"))==6,"source/case count")
    need(rows(PKG/"candidate-definition.csv")[0]["product_number"]=="2300327","candidate")
    need(len(rows(PKG/"verification-matrix.csv"))==10,"test count")
    h=rows(PKG/"open-holds.csv");a=rows(PKG/"acceptance-matrix.csv");need(len(h)==12 and len(a)==12,"hold count");need(all(r["state"]=="OPEN" and r["execution"]=="NOT EXECUTED" for r in h),"hold closure");need(all(r["execution_state"]=="NOT EXECUTED" and r["result"]=="OPEN" for r in a),"acceptance closure")
    e=.5*.010144*math.radians(10)**2; work=189.721*.00075; need(abs(e-.000154502)<1e-9 and 920<work/e<922,"energy arithmetic")
    ht=(PKG/"index.html").read_text(encoding="utf-8");need("font:clamp(16px" in ht and "font-size:14px" in ht and WARNING in ht,"web floor")
    mf(PKG);mf(REL);c=json.loads((ROOT/"configuration/hr-v0-config-reconciliation-p0.39/package-status.json").read_text(encoding="utf-8"));need(c["identifier"]=="HR-V0-CONFIG-REC-P0.39" and c["motion_authorized"] is False,"config")
    print("HR-V0 J2 soft-contact pad P0.1 checks passed: 4 sources, 6 load cases, 12 holds, zero authority");return 0
if __name__=="__main__":raise SystemExit(main())
