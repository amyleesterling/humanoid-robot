#!/usr/bin/env python3
"""Generate the R239 P1.21 project visual-review record."""
from __future__ import annotations
import csv, hashlib, html, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
P121=ROOT/"electrical/kicad/project-button-v3-p1.21-sra1-supply-watchdog-candidate"
R238=ROOT/"release/hr-v0/p121-consolidated-review-p0.1"
OUT=ROOT/"release/hr-v0/p121-visual-review-p0.1"
REVIEW=ROOT/"electrical/reviews/hr-v0-p121-visual-review-p0.1"
ID="HR-V0-P121-VISUAL-REVIEW-P0.1"
WARNING="PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"

def read(path):
    with path.open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def write(path,fields,rows):
    with path.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields,lineterminator="\n");w.writeheader();w.writerows(rows)
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest().upper()

def main():
    for d in (OUT,REVIEW):d.mkdir(parents=True,exist_ok=True)
    pages=[]
    for r in read(R238/"sheet-review-register.csv"):
        n=int(r["page"]); direct=n in {2,3}
        pages.append({"page":n,"title":r["title"],"paper":r["paper"],"svg":r["p121_svg"],"sha256":r["p121_sha256"],
            "review_basis":"DIRECT_BROWSER_FULL_SHEET_2026-08-11" if direct else "R230_PASS_PLUS_TRANSITIVE_P121_LAYOUT_INHERITANCE",
            "project_visual_result":"PASS","browser_visual_executed":"YES" if direct else "NO_INHERITED_LAYOUT",
            "clipping":"NONE_OBSERVED","collision":"NONE_OBSERVED","frame_title_warning":"PASS",
            "independent_review":"OPEN","qualified_electrical_review":"OPEN","warning":WARNING})
    holds=[dict(r) for r in read(R238/"open-holds.csv") if r["hold_id"]!="P121C-H01"]
    if len(pages)!=13 or len(holds)!=10:raise RuntimeError("R238 visual/hold basis changed")
    observations=[
        {"observation_id":"VIS-002","page":2,"scope":"complete native SVG at full-sheet scale","result":"PASS","finding":"No clipped frame, warning, title, component field, net label or note; no symbol/text collision observed.","limitation":"Project-owned inspection only; terminal correctness and independent review remain open.","warning":WARNING},
        {"observation_id":"VIS-003","page":3,"scope":"complete native SVG at full-sheet scale","result":"PASS","finding":"No clipped frame, warning, title, component field, net label or note; series SRA1 supply-gate labels remain visually distinct.","limitation":"Project-owned inspection only; application correctness and independent review remain open.","warning":WARNING}]
    srcs=[R238/"sheet-review-register.csv",R238/"open-holds.csv",P121/"02_estop_eligibility.kicad_sch",P121/"03_arm_watchdog_eligibility.kicad_sch",
        P121/"output/project-button-v3-p1.21-sra1-supply-watchdog-candidate-02 Dual-channel E-stop and RESET eligibility.svg",
        P121/"output/project-button-v3-p1.21-sra1-supply-watchdog-candidate-03 Distinct ARM and SRA1 diagnostic supply gate.svg"]
    sources=[{"path":p.relative_to(ROOT).as_posix(),"sha256":digest(p),"bytes":p.stat().st_size,"warning":WARNING} for p in srcs]
    status={"identifier":ID,"round":"R239","date":"2026-08-11","candidate":"V3-P1.21-SRA1-SUPPLY-WATCHDOG-CANDIDATE","current_candidate":"V3-P1.15-CARRIER-CANDIDATE",
        "native_sheets":13,"direct_browser_visual_pages":[2,3],"project_visual_passes":13,"project_visual_findings":0,"open_holds":10,"p121_accepted":False,
        "independent_review_complete":False,"qualified_review_complete":False,"functional_safety_approved":False,"work_authority":False,"warning":WARNING}
    sets={
        "sheet-visual-review.csv":(("page","title","paper","svg","sha256","review_basis","project_visual_result","browser_visual_executed","clipping","collision","frame_title_warning","independent_review","qualified_electrical_review","warning"),pages),
        "direct-observations.csv":(("observation_id","page","scope","result","finding","limitation","warning"),observations),
        "open-holds.csv":(("hold_id","closure_evidence","state","warning"),holds),
        "source-register.csv":(("path","sha256","bytes","warning"),sources)}
    p2="../../../"+pages[2]["svg"];p3="../../../"+pages[3]["svg"]
    trs="".join(f"<tr><td>{r['page']}</td><td>{html.escape(r['title'])}</td><td>{r['paper']}</td><td>{html.escape(r['review_basis'])}</td><td><b>PASS</b></td><td>OPEN</td></tr>" for r in pages)
    page=f'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>P1.21 visual review</title><style>:root{{--sky:#82d4f6;--navy:#082b4c;--blue:#155d91;--gold:#f3b61f}}*{{box-sizing:border-box}}body{{margin:0;color:var(--navy);font:clamp(16px,1.15vw,19px)/1.5 Arial,sans-serif}}header{{padding:clamp(1.5rem,5vw,4rem);background:linear-gradient(135deg,var(--sky),#eefaff);border-bottom:7px solid var(--gold)}}h1{{font-size:clamp(2rem,5vw,4.2rem);line-height:1.04}}main{{max-width:1500px;margin:auto;padding:2rem clamp(1rem,4vw,3rem)}}.warning{{padding:1rem;border:3px solid #9b6d00;background:#fff3c4;border-radius:.8rem;font-weight:700}}.pass{{display:inline-block;padding:.35rem .7rem;background:#daf5e4;border:2px solid #207044;border-radius:999px;font-weight:700;font-size:14px}}figure{{margin:1.5rem 0;border:3px solid var(--blue);border-radius:.8rem;overflow:auto}}figure img{{display:block;width:100%;min-width:900px}}figcaption{{position:sticky;left:0;padding:.8rem 1rem;background:var(--navy);color:white;font-weight:700}}.table{{overflow:auto}}table{{width:100%;border-collapse:collapse;min-width:1050px}}th,td{{padding:.8rem;text-align:left;border-bottom:1px solid #aac}}th{{background:var(--navy);color:white}}</style></head><body><header><strong>{ID} / R239</strong><h1>The changed sheets fit and remain readable</h1><div class="warning">{WARNING}</div></header><main><p><span class="pass">PROJECT VISUAL PASS</span> Pages 2 and 3 were freshly inspected as complete native exports. The other eleven layouts inherit the completed P1.19 project pass. This is not independent acceptance.</p><figure><figcaption>Page 2 — E-stop and RESET eligibility</figcaption><img src="{html.escape(p2)}"></figure><figure><figcaption>Page 3 — ARM and SRA1 supply gate</figcaption><img src="{html.escape(p3)}"></figure><h2>Thirteen-page disposition</h2><div class="table"><table><thead><tr><th>Page</th><th>Title</th><th>Paper</th><th>Basis</th><th>Project</th><th>Independent</th></tr></thead><tbody>{trs}</tbody></table></div><h2>Boundary</h2><p>P1.15 remains current and P1.21 remains unaccepted. Ten substantive holds, independent and qualified review, and all work authority remain open.</p></main></body></html>'''
    for d in (OUT,REVIEW):
        for name,(fields,rows) in sets.items():write(d/name,fields,rows)
        (d/"package-status.json").write_text(json.dumps(status,indent=2)+"\n",encoding="utf-8")
        (d/"README.md").write_text(f"# {ID}\n\n> **{WARNING}**\n\nR239 records thirteen project visual passes. P1.15 remains current; P1.21 remains unaccepted; ten holds remain open.\n",encoding="utf-8")
    (OUT/"index.html").write_text(page,encoding="utf-8")
    manifest=[{"file":p.name,"size_bytes":p.stat().st_size,"sha256":digest(p),"warning":WARNING} for p in sorted(OUT.iterdir()) if p.is_file() and p.name!="file-manifest.csv"]
    write(OUT/"file-manifest.csv",("file","size_bytes","sha256","warning"),manifest)
    print(f"Wrote {ID}: 13 project visual passes, 2 direct pages, 10 open holds")
if __name__=="__main__":main()
