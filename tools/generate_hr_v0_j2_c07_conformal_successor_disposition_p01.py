#!/usr/bin/env python3
"""Publish the R292 fail-closed disposition of the R291 successor mesh."""
from __future__ import annotations
import csv, hashlib, html, json, shutil
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
R289=ROOT/"mechanical/analysis/hr-v0-j2-c07-conformal-zone-mesh-p0.1"
R291=ROOT/"mechanical/analysis/hr-v0-j2-c07-conformal-successor-mesh-p0.1"
PREREG=ROOT/"mechanical/analysis/hr-v0-j2-c07-conformal-successor-prereg-p0.1"
OUT=ROOT/"mechanical/analysis/hr-v0-j2-c07-conformal-successor-disposition-p0.1"
RELEASE=ROOT/"release/hr-v0/j2-c07-conformal-successor-disposition-p0.1"
IDENT="HR-V0-J2-C07-CONFORMAL-SUCCESSOR-DISPOSITION-P0.1"
WARNING="PRELIMINARY - CONFORMAL SUCCESSOR DISPOSITION ONLY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def write_csv(p:Path,rows:list[dict[str,object]])->None:
    fields=[]
    for r in rows:
        for k in r:
            if k not in fields:fields.append(k)
    with p.open("w",newline="",encoding="utf-8") as s:w=csv.DictWriter(s,fieldnames=fields,lineterminator="\n");w.writeheader();w.writerows(rows)
def table(rows:list[dict[str,object]],fields:list[str])->str:
    return "<div class='scroll'><table><thead><tr>"+"".join(f"<th>{html.escape(f.replace('_',' '))}</th>" for f in fields)+"</tr></thead><tbody>"+"".join("<tr>"+"".join(f"<td>{html.escape(str(r.get(f,'')))}</td>" for f in fields)+"</tr>" for r in rows)+"</tbody></table></div>"
def main()->int:
    if OUT.exists():shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    s289=json.loads((R289/"analysis-status.json").read_text(encoding="utf-8"));s291=json.loads((R291/"analysis-status.json").read_text(encoding="utf-8"))
    if s289["r279_c02_complete"] or s291["r279_c02_complete"]:raise RuntimeError("failed-baseline disposition identity drift")
    raw=np.load(R291/"raw-conformal-zone-mesh.npz");names=sorted(r["zone_id"] for r in csv.DictReader((R291/"zone-quality-summary.csv").open(newline="",encoding="utf-8")))
    node_tags=raw["linear_node_tags"];node_xyz=raw["linear_node_xyz"];connectivity=raw["linear_tet4_connectivity"];quality=raw["linear_sicn"];element_tags=raw["linear_element_tags"];zone_codes=raw["element_zone_code"]
    xyz={int(tag):node_xyz[i] for i,tag in enumerate(node_tags)};low=np.flatnonzero(quality<.20);low_rows=[]
    for i in low:
        corners=np.vstack([xyz[int(tag)] for tag in connectivity[i]]);center=np.mean(corners,axis=0)
        low_rows.append({"element_tag":int(element_tags[i]),"exact_zone_id":names[int(zone_codes[i])],"sicn":float(quality[i]),"centroid_x_mm":float(center[0]),"centroid_y_mm":float(center[1]),"centroid_z_mm":float(center[2]),"warning":WARNING})
    write_csv(OUT/"r291-low-sicn-localization.csv",low_rows)
    comparison=[
        {"metric":"tetrahedra","R289":s289["linear_tetrahedra"],"R291":s291["linear_tetrahedra"],"disposition":"resource growth +31.3%","warning":WARNING},
        {"metric":"global minimum SICN","R289":s289["global_sicn_minimum"],"R291":s291["global_sicn_minimum"],"disposition":"REGRESSED below unchanged 0.10 floor","warning":WARNING},
        {"metric":"cells SICN <0.20","R289":18,"R291":len(low_rows),"disposition":"REGRESSED 18 -> 19","warning":WARNING},
        {"metric":"monitored failed zones","R289":len(s289["monitored_zone_failures"]),"R291":len(s291["monitored_zone_failures"]),"disposition":"UNCHANGED four pocket-straight zones","warning":WARNING},
        {"metric":"actual-quadrature curved Jacobian gate","R289":s289["actual_quadrature_signed_jacobian_gate"],"R291":s291["actual_quadrature_signed_jacobian_gate"],"disposition":"ADVANCED false -> true","warning":WARNING},
        {"metric":"R279-C02","R289":False,"R291":False,"disposition":"OPEN","warning":WARNING},
    ];write_csv(OUT/"r289-r291-comparison.csv",comparison)
    next_protocol={"identifier":IDENT,"round":"R292","date":"2026-08-13","retained_success":"R291 symmetry-closed cylinder-face refinement eliminates all sampled actual-quadrature curved Jacobian failures","rejected_method":"further pocket-straight-only size reduction; R291 showed nonmonotone SICN regression","required_next_preregistration":"preserve R291 face refinement and exact zone CAD; change the linear mesh optimization/topology method at the PE tangent junctions under a single frozen candidate; suggested bounded screen Netgen followed by Relocate3D, with no threshold changes","acceptance_thresholds_unchanged":True,"next_mesh_executed":False,"r279_c02_complete":False,"r278_h02_closed":False,"capacity_credit":False,"safety_credit":False,"work_authority":False,"warning":WARNING}
    (OUT/"next-method-boundary.json").write_text(json.dumps(next_protocol,indent=2)+"\n",encoding="utf-8")
    status={"identifier":IDENT,"round":"R292","r289_status_sha256":sha(R289/"analysis-status.json"),"r291_status_sha256":sha(R291/"analysis-status.json"),"r291_low_sicn_elements":len(low_rows),"r291_curved_jacobian_gate":True,"pocket_refinement_method_rejected":True,"next_mesh_executed":False,"r279_c02_complete":False,"r278_h02_closed":False,"capacity_credit":False,"safety_credit":False,"fabrication_authorized":False,"powered_testing_authorized":False,"motion_authorized":False,"energization_authorized":False,"warning":WARNING}
    (OUT/"analysis-status.json").write_text(json.dumps(status,indent=2)+"\n",encoding="utf-8")
    (OUT/"execution-provenance.json").write_text(json.dumps({"generator_sha256":sha(Path(__file__).resolve()),"r289_status_sha256":sha(R289/"analysis-status.json"),"r291_status_sha256":sha(R291/"analysis-status.json"),"r291_raw_sha256":sha(R291/"raw-conformal-zone-mesh.npz"),"r291_prereg_sha256":sha(PREREG/"frozen-successor-protocol.json"),"warning":WARNING},indent=2)+"\n",encoding="utf-8")
    cmp=table(comparison,["metric","R289","R291","disposition"]);loc=table(low_rows,["exact_zone_id","element_tag","sicn","centroid_x_mm","centroid_y_mm","centroid_z_mm"])
    guide=f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>{IDENT}</title><style>:root{{--navy:#082b55;--blue:#245aa6;--sky:#8ed8f8;--gold:#f4b942;--paper:#f7fbff;--ink:#102a43;--line:#9ccfe8}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.55 system-ui,sans-serif}}header{{background:linear-gradient(135deg,var(--navy),var(--blue));color:white;padding:clamp(28px,6vw,68px) 20px}}header>div,main{{max-width:1240px;margin:auto}}main{{padding:28px 20px 80px}}h1{{font-size:clamp(34px,6vw,64px);line-height:1.08}}h2{{font-size:clamp(25px,3vw,38px);color:var(--navy)}}.warning{{background:var(--gold);color:#17243a;border:3px solid #805800;padding:15px 18px;font-weight:900;font-size:16px}}.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px}}.card{{background:white;border:2px solid var(--sky);border-radius:14px;padding:18px}}.metric{{font-size:clamp(30px,5vw,48px);font-weight:900;color:var(--blue)}}.scroll{{overflow-x:auto;border:2px solid var(--line);border-radius:10px;margin:14px 0}}table{{border-collapse:collapse;width:100%;min-width:900px}}th,td{{padding:12px 14px;text-align:left;vertical-align:top;border-bottom:1px solid var(--line);font-size:16px}}th{{background:var(--navy);color:white}}@media(max-width:620px){{main{{padding-inline:14px}}}}</style></head><body><header><div><p class='warning'>{WARNING}</p><p>R291 → R292 disposition</p><h1>Curved elements fixed. Pocket-junction quality still fails.</h1><p>The next change targets the meshing method—not the acceptance thresholds.</p></div></header><main><section class='cards'><article class='card'><div class='metric'>0</div><p>failed actual-quadrature Jacobian samples after R291</p></article><article class='card'><div class='metric'>{len(low_rows)}</div><p>cells below SICN 0.20</p></article><article class='card'><div class='metric'>{s291['global_sicn_minimum']:.4f}</div><p>global minimum versus required 0.10</p></article></section><h2>Controlled comparison</h2>{cmp}<h2>R291 low-quality cells</h2>{loc}<h2>Next method boundary</h2><p>{html.escape(next_protocol['required_next_preregistration'])}</p><p>R279-C02, structural convergence, H02, capacity, safety credit and every work authority remain open.</p></main></body></html>"""
    (OUT/"index.html").write_text(guide,encoding="utf-8");(OUT/"README.md").write_text(f"# {IDENT}\n\n**{WARNING}**\n\nR292 records the split R291 result: sampled curved-Jacobian failures are eliminated, while pocket-junction SICN regresses. More straight-only refinement is rejected; a separately preregistered optimization/topology-method candidate is required.\n",encoding="utf-8")
    manifest=[]
    for p in sorted(OUT.iterdir()):
        if p.name!="file-manifest.csv":manifest.append({"relative_path":p.name,"sha256":sha(p),"bytes":p.stat().st_size,"warning":WARNING})
    write_csv(OUT/"file-manifest.csv",manifest)
    if RELEASE.exists():shutil.rmtree(RELEASE)
    RELEASE.parent.mkdir(parents=True,exist_ok=True);shutil.copytree(OUT,RELEASE);print(json.dumps(status,indent=2));return 0
if __name__=="__main__":raise SystemExit(main())
