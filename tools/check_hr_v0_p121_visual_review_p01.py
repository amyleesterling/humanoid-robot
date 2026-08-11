#!/usr/bin/env python3
"""Validate the R239 P1.21 project visual-review record."""
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"release/hr-v0/p121-visual-review-p0.1"; REVIEW=ROOT/"electrical/reviews/hr-v0-p121-visual-review-p0.1"
WARNING="PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
def rows(p):
    with p.open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def need(v,m):
    if not v:raise SystemExit(m)
def main():
    for d in (OUT,REVIEW):
        pages=rows(d/"sheet-visual-review.csv")
        need(len(pages)==13 and {r["page"] for r in pages}=={str(i) for i in range(13)},"page coverage")
        need(all(r["project_visual_result"]=="PASS" and r["clipping"]=="NONE_OBSERVED" and r["collision"]=="NONE_OBSERVED" for r in pages),"visual result")
        need({r["page"] for r in pages if r["browser_visual_executed"]=="YES"}=={"2","3"},"direct pages")
        need(all(r["independent_review"]=="OPEN" and r["qualified_electrical_review"]=="OPEN" for r in pages),"external review promoted")
        need(len(rows(d/"direct-observations.csv"))==2,"observations")
        holds=rows(d/"open-holds.csv");need(len(holds)==10 and all(r["state"]=="OPEN" for r in holds),"holds")
        need("P121C-H01" not in {r["hold_id"] for r in holds},"closed hold retained")
        need(len(rows(d/"source-register.csv"))==6,"sources")
        s=json.loads((d/"package-status.json").read_text(encoding="utf-8"))
        need(s["current_candidate"]=="V3-P1.15-CARRIER-CANDIDATE" and not s["p121_accepted"],"configuration promoted")
        need(s["project_visual_passes"]==13 and s["project_visual_findings"]==0 and s["open_holds"]==10,"status counts")
        need(not s["independent_review_complete"] and not s["qualified_review_complete"] and not s["functional_safety_approved"] and not s["work_authority"],"authority promoted")
        for name in ("sheet-visual-review.csv","direct-observations.csv","open-holds.csv","source-register.csv"):
            need(all(r["warning"]==WARNING for r in rows(d/name)),f"warning {name}")
    page=(OUT/"index.html").read_text(encoding="utf-8")
    for token in (WARNING,"The changed sheets fit and remain readable","PROJECT VISUAL PASS","P1.15 remains current","P1.21 remains unaccepted","font-size:14px"):need(token in page,f"guide {token}")
    need("font-size:12px" not in page and "font-size:11px" not in page,"undersized text")
    manifest={r["file"]:r for r in rows(OUT/"file-manifest.csv")}; actual={p.name:p for p in OUT.iterdir() if p.is_file() and p.name!="file-manifest.csv"}
    need(set(manifest)==set(actual),"manifest membership")
    for name,p in actual.items():
        b=p.read_bytes();need(manifest[name]["size_bytes"]==str(len(b)) and manifest[name]["sha256"]==hashlib.sha256(b).hexdigest().upper(),f"manifest {name}")
    print("PASS: R239 P1.21 project visual review complete; external authority remains open")
    print(WARNING)
if __name__=="__main__":main()
