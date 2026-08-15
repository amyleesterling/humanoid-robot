#!/usr/bin/env python3
"""Execute the one preregistered R308 exact facet/B-Rep/load evaluation."""
from __future__ import annotations
import csv,hashlib,json,shutil
from pathlib import Path
import numpy as np
import generate_hr_v0_j2_c07_brep_facet_load_p01 as base
from hr_v0_mesh_raw_shards import load_shards

ROOT=Path(__file__).resolve().parents[1];R307=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-cad-curving-mesh-p0.1";PREREG=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-cad-curving-facet-prereg-p0.1"
OUT=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-cad-curving-facet-p0.1";RELEASE=ROOT/"release/hr-v0/j2-c07-pe-cad-curving-facet-p0.1"
IDENT="HR-V0-J2-C07-PE-CAD-CURVING-FACET-P0.1";ROUND="R308";WARNING="PRELIMINARY - R307 EXACT FACET/B-REP/LOAD REVALIDATION EVIDENCE ONLY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
def sha(path:Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()
def rows(path:Path)->list[dict[str,str]]:
    with path.open(newline="",encoding="utf-8") as stream:return list(csv.DictReader(stream))
def write_csv(path:Path,data:list[dict[str,object]])->None:
    fields=[]
    for row in data:
        for field in row:
            if field not in fields:fields.append(field)
    with path.open("w",newline="",encoding="utf-8") as stream:w=csv.DictWriter(stream,fieldnames=fields,lineterminator="\n");w.writeheader();w.writerows(data)
def main()->int:
    protocol_path=PREREG/"frozen-protocol.json";protocol=json.loads(protocol_path.read_text(encoding="utf-8"));status=json.loads((R307/"analysis-status.json").read_text(encoding="utf-8"))
    if protocol["exact_facet_revalidation_executed"] or protocol["executor_sha256"]!=sha(Path(__file__).resolve()) or not status["sampled_cad_curving_candidate_pass"]:raise RuntimeError("R308 prereg/source state")
    raw=load_shards(R307);original_load=base.np.load
    def virtual_load(path,*args,**kwargs):
        if Path(path).resolve()==(R307/"analysis-status.json").resolve():return raw
        return original_load(path,*args,**kwargs)
    base.OUT=OUT;base.RELEASE=RELEASE;base.RAW=R307/"analysis-status.json";base.R285=PREREG;base.IDENT=IDENT;base.ROUND=ROUND;base.RAW_LABEL="retained R307 lossless raw shards";base.WARNING=WARNING
    base.ADDITIONAL_INPUTS=[("R307 raw linear shard",R307/"raw-linear-mesh.npz"),("R307 raw Tet10 shard",R307/"raw-tet10-mesh.npz"),("R307 frozen CAD-curving protocol",R307/"frozen-cad-curving-protocol.json"),("R308 wrapper",Path(__file__).resolve())]
    base.np.load=virtual_load
    try:code=base.main()
    finally:base.np.load=original_load
    out_status_path=OUT/"analysis-status.json";out_status=json.loads(out_status_path.read_text(encoding="utf-8"));face_rows=rows(OUT/"face-fidelity-summary.csv")
    per_face_area=all(float(row["relative_area_error"])<=base.SURFACE_AREA_REL_LIMIT for row in face_rows)
    exact_gate=bool(out_status["exact_facet_map_complete"] and out_status["surface_deviation_screen_pass"] and per_face_area and out_status["single_level_load_geometry_pass"])
    out_status.update({"identifier":IDENT,"round":ROUND,"candidate_id":protocol["candidate_id"],"preregistration_sha256":sha(protocol_path),"r307_status_sha256":sha(R307/"analysis-status.json"),"r307_raw_linear_sha256":sha(R307/"raw-linear-mesh.npz"),"r307_raw_tet10_sha256":sha(R307/"raw-tet10-mesh.npz"),"sampled_r307_candidate_pass":True,"all_per_face_area_gates_pass":per_face_area,"exact_facet_revalidation_executed":True,"exact_facet_revalidation_pass":exact_gate,"r279_c02_complete":False,"structural_solution_executed":False,"r278_h02_closed":False,"capacity_credit":False,"selected":False,"safety_credit":False,"procurement_authorized":False,"fabrication_authorized":False,"assembly_authorized":False,"connection_authorized":False,"powered_testing_authorized":False,"motion_authorized":False,"energization_authorized":False,"warning":WARNING})
    out_status_path.write_text(json.dumps(out_status,indent=2)+"\n",encoding="utf-8")
    provenance_path=OUT/"execution-provenance.json";provenance=json.loads(provenance_path.read_text(encoding="utf-8"));provenance.update({"identifier":IDENT,"wrapper_path":Path(__file__).resolve().relative_to(ROOT).as_posix(),"wrapper_sha256":sha(Path(__file__).resolve()),"transitive_evaluator_sha256":sha(Path(base.__file__).resolve()),"preregistration_sha256":sha(protocol_path),"r307_status_sha256":sha(R307/"analysis-status.json"),"r307_raw_linear_sha256":sha(R307/"raw-linear-mesh.npz"),"r307_raw_tet10_sha256":sha(R307/"raw-tet10-mesh.npz"),"warning":WARNING});provenance_path.write_text(json.dumps(provenance,indent=2)+"\n",encoding="utf-8")
    for path in OUT.iterdir():
        if path.suffix==".csv":
            data=rows(path)
            for row in data:
                if "warning" in row:row["warning"]=WARNING
            write_csv(path,data)
    result="passes" if exact_gate else "does not pass"
    (OUT/"README.md").write_text(f"# {IDENT}\n\n> **{WARNING}**\n\nR308 maps every exterior R307 Tet10 facet to exact C07 OCC faces and checks sampled Q8 surface deviation, every face area, and the exact clipped load patch using the frozen R307 thresholds. The combined exact-facet revalidation {result}. See the validation and face tables for the observed measurements.\n\nR279-C02 remains false pending formal disposition and independent acceptance. Full-domain positivity, structural fields, convergence, H02, capacity, physical validation and every work authority remain open.\n",encoding="utf-8")
    manifest=[]
    for path in sorted(OUT.iterdir()):
        if path.is_file() and path.name!="file-manifest.csv":manifest.append({"relative_path":path.name,"sha256":sha(path),"bytes":path.stat().st_size,"warning":WARNING})
    write_csv(OUT/"file-manifest.csv",manifest)
    if RELEASE.exists():shutil.rmtree(RELEASE)
    RELEASE.parent.mkdir(parents=True,exist_ok=True);shutil.copytree(OUT,RELEASE)
    print(json.dumps(out_status,indent=2));return code
if __name__=="__main__":raise SystemExit(main())
