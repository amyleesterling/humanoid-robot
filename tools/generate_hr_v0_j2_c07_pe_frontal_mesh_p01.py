#!/usr/bin/env python3
"""Execute the single preregistered R295 Frontal mesh candidate."""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import shutil
from pathlib import Path


ROOT=Path(__file__).resolve().parents[1]
PRIOR_GENERATOR=ROOT/"tools/generate_hr_v0_j2_c07_conformal_successor_mesh_p01.py"
BASE_GENERATOR=ROOT/"tools/generate_hr_v0_j2_c07_conformal_zone_mesh_p01.py"
PREREG=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-frontal-prereg-p0.1"
R293=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-topology-mesh-p0.1"
OUT=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-frontal-mesh-p0.1"
RELEASE=ROOT/"release/hr-v0/j2-c07-pe-frontal-mesh-p0.1"
IDENT="HR-V0-J2-C07-PE-FRONTAL-MESH-P0.1"
ROUND="R295"
WARNING="PRELIMINARY - PREREGISTERED FRONTAL TETRAHEDRALIZATION EVIDENCE ONLY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def write_csv(path:Path,rows:list[dict[str,object]])->None:
    fields=[]
    for row in rows:
        for field in row:
            if field not in fields:fields.append(field)
    with path.open("w",newline="",encoding="utf-8") as s:
        w=csv.DictWriter(s,fieldnames=fields,lineterminator="\n");w.writeheader();w.writerows(rows)
def load_prior():
    spec=importlib.util.spec_from_file_location("r291_execution_for_r295",PRIOR_GENERATOR)
    if spec is None or spec.loader is None:raise RuntimeError("cannot load R291 generator")
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
def main()->int:
    protocol_path=PREREG/"frozen-frontal-protocol.json";protocol=json.loads(protocol_path.read_text(encoding="utf-8"));pstatus=json.loads((PREREG/"analysis-status.json").read_text(encoding="utf-8"))
    if protocol["candidate_id"]!="R295-C07-PE-FRONTAL-V01" or protocol["linear_mesh_method"]["algorithm3d"]!=4:raise RuntimeError("R295 protocol drift")
    if pstatus["mesh_executed"] or not pstatus["single_candidate_frozen"]:raise RuntimeError("R295 preregistration state")
    prior=load_prior();original_load=prior.load_base;algorithm_calls=[]
    def load_base_frontal():
        base=original_load();original_set=base.gmsh.option.setNumber
        def set_number(name:str,value:float)->None:
            if name=="Mesh.Algorithm3D":
                if int(value)!=1:raise RuntimeError(f"unexpected inherited Algorithm3D {value}")
                value=4;algorithm_calls.append(4)
            original_set(name,value)
        base.gmsh.option.setNumber=set_number
        return base
    prior.load_base=load_base_frontal;prior.OUT=OUT;prior.RELEASE=RELEASE;prior.IDENT=IDENT;prior.ROUND=ROUND;prior.WARNING=WARNING
    return_code=prior.main()
    if algorithm_calls!=[4]:raise RuntimeError(f"Frontal algorithm execution drift {algorithm_calls}")
    old=OUT/"frozen-successor-protocol.json"
    if old.exists():old.unlink()
    shutil.copy2(protocol_path,OUT/"frozen-frontal-protocol.json")
    status_path=OUT/"analysis-status.json";status=json.loads(status_path.read_text(encoding="utf-8"));status.update({
        "identifier":IDENT,"round":ROUND,"candidate_id":protocol["candidate_id"],"preregistration_sha256":sha(protocol_path),
        "r293_baseline_status_sha256":sha(R293/"analysis-status.json"),"algorithm3d":4,"algorithm_name":"Frontal",
        "linear_optimizer_sequence":["Netgen"],"relocate3d":False,"high_order_optimizer":"NONE","thresholds_unchanged":True,
        "single_preregistered_execution_complete":True,"warning":WARNING,
    });status_path.write_text(json.dumps(status,indent=2)+"\n",encoding="utf-8")
    provenance_path=OUT/"execution-provenance.json";prov=json.loads(provenance_path.read_text(encoding="utf-8"));prov.update({
        "identifier":IDENT,"generator_path":Path(__file__).resolve().relative_to(ROOT).as_posix(),"generator_sha256":sha(Path(__file__).resolve()),
        "transitive_r291_generator_sha256":sha(PRIOR_GENERATOR),"transitive_r289_generator_sha256":sha(BASE_GENERATOR),
        "preregistration_path":protocol_path.relative_to(ROOT).as_posix(),"preregistration_sha256":sha(protocol_path),
        "algorithm3d":4,"algorithm_name":"Frontal","linear_optimizer":"Netgen","linear_optimizer_sequence":["Netgen"],
        "relocate3d":False,"high_order_optimizer":"NONE","thresholds_unchanged":True,"warning":WARNING,
    });provenance_path.write_text(json.dumps(prov,indent=2)+"\n",encoding="utf-8")
    write_csv(OUT/"method-execution-register.csv",[{"candidate_id":protocol["candidate_id"],"algorithm3d":4,"algorithm_name":"Frontal","linear_optimizer":"Netgen","relocate3d":False,"high_order_optimizer":"NONE","execution_count":1,"thresholds_unchanged":True,"global_sicn_gate":status["global_sicn_gate"],"monitored_zone_gate":status["monitored_zone_minimum_gate"],"actual_quadrature_jacobian_gate":status["actual_quadrature_signed_jacobian_gate"],"r279_c02_complete":status["r279_c02_complete"],"warning":WARNING}])
    write_csv(OUT/"method-baseline-register.csv",[{"baseline_id":"R293-C07-PE-TOPOLOGY-V01","baseline_status_sha256":sha(R293/"analysis-status.json"),"algorithm3d":1,"optimizer_sequence":"Netgen,Relocate3D","r279_c02_complete":False,"retention":"IMMUTABLE FAILED METHOD BASELINE","warning":WARNING}])
    failed=OUT/"failed-baseline-register.csv"
    if failed.exists():failed.unlink()
    (OUT/"README.md").write_text(f"# {IDENT}\n\n**{WARNING}**\n\nR295 executes exactly one preregistered linear-topology candidate: Gmsh Frontal `Algorithm3D=4`, Netgen linear optimization, and then Tet10 conversion. Exact CAD, targets, size fields, and acceptance thresholds remain unchanged; Relocate3D and high-order optimization are absent.\n\nThis is mesh-method evidence only. Even an R279-C02 pass does not execute structural fields, establish convergence or capacity, close H02, or grant work authority.\n",encoding="utf-8")
    manifest=[]
    for path in sorted(OUT.iterdir()):
        if path.is_file() and path.name!="file-manifest.csv":manifest.append({"relative_path":path.name,"sha256":sha(path),"bytes":path.stat().st_size,"warning":WARNING})
    write_csv(OUT/"file-manifest.csv",manifest)
    if RELEASE.exists():shutil.rmtree(RELEASE)
    RELEASE.parent.mkdir(parents=True,exist_ok=True);shutil.copytree(OUT,RELEASE)
    print(json.dumps(status,indent=2));return return_code
if __name__=="__main__":raise SystemExit(main())
