#!/usr/bin/env python3
"""Publish R284 bounded constrained-high-order method evidence."""
import csv,hashlib,json,shutil,sys
from pathlib import Path
import gmsh,numpy,scipy,skfem
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/"mechanical/analysis/hr-v0-j2-c07-constrained-high-order-p0.1";REL=ROOT/"release/hr-v0/j2-c07-constrained-high-order-p0.1";WARNING="PRELIMINARY - CONSTRAINED HIGH-ORDER MESH METHOD EVIDENCE ONLY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write_csv(p,rec):
    with p.open("w",newline="",encoding="utf-8") as s:w=csv.DictWriter(s,fieldnames=list(rec[0]),lineterminator="\n");w.writeheader();w.writerows(rec)
def manifest(d):
    write_csv(d/"file-manifest.csv",[{"relative_path":p.relative_to(d).as_posix(),"sha256":sha(p),"bytes":p.stat().st_size,"warning":WARNING} for p in sorted(d.rglob("*")) if p.is_file() and p.name!="file-manifest.csv"])
def main():
    generator=ROOT/"tools/generate_hr_v0_j2_c07_constrained_high_order_p01.py";base=ROOT/"tools/generate_hr_v0_j2_stop_refinement_execution_p01.py";step=ROOT/"cad/hr-v0/generated/arm-architecture-p0.13-pad-pocket-stop/parts/MV0-C07_J2_positive_fixed_catch_adapter.step"
    options={"General.NumThreads":1,"Mesh.Algorithm3D":1,"Mesh.MeshSizeMin":0.7,"Mesh.MeshSizeMax":4.0,"Mesh.MeshSizeFromPoints":0,"Mesh.MeshSizeFromCurvature":0,"Mesh.MeshSizeExtendFromBoundary":1,"linear_optimizer":"Netgen","element_order":2,"high_order_optimizer":"HighOrder","pre_restore_bijection_tolerance_mm":0.1,"post_restore_tolerance_mm":1e-12,"normalized_determinant_floor":1e-10,"linear_abs_determinant_floor":1e-14,"sampled_quadrature_orders":[4,6,8]}
    write_csv(OUT/"runtime-input-register.csv",[{"input":"baseline commit","value":"d36bb8d5979364c9fcf5a46101fcf79500c61f99","sha256":"N/A","warning":WARNING},{"input":step.relative_to(ROOT).as_posix(),"value":"exact STEP identity","sha256":sha(step),"warning":WARNING},{"input":generator.relative_to(ROOT).as_posix(),"value":"R284 generator","sha256":sha(generator),"warning":WARNING},{"input":base.relative_to(ROOT).as_posix(),"value":"shared exact OCC/local field source","sha256":sha(base),"warning":WARNING},{"input":"Python","value":sys.version.replace("\n"," "),"sha256":"N/A","warning":WARNING},{"input":"gmsh/numpy/scipy/skfem","value":f"{gmsh.__version__}/{numpy.__version__}/{scipy.__version__}/{skfem.__version__}","sha256":"N/A","warning":WARNING}])
    (OUT/"execution-options.json").write_text(json.dumps(options,indent=2)+"\n",encoding="utf-8")
    st=json.loads((OUT/"analysis-status.json").read_text());st.update({"execution_options_sha256":sha(OUT/"execution-options.json"),"generator_sha256":sha(generator),"transitive_base_sha256":sha(base),"runtime_input_register_sha256":sha(OUT/"runtime-input-register.csv")});(OUT/"analysis-status.json").write_text(json.dumps(st,indent=2)+"\n",encoding="utf-8");(OUT/"README.md").write_text(f"# {st['identifier']}\n\n> **{WARNING}**\n\nR284 demonstrates one bounded constrained-high-order C07 meshing route. HighOrder-optimized midsides are retained while all 8,999 linear corners are restored exactly. Linear SICN, connectivity/orientation, OCC corner membership and finite samples at Q4/Q6/Q8 curved/normalized determinant rules pass. These samples are not a proof over each full curved element and are not actual future structural quadrature unless that solver chooses the same rules. Corner restoration has not been revalidated against the exact B-Rep curved entities; exact facet mapping and surface deviation remain open. This is meshing-method evidence only: full R279-C02, H02, selection, safety, capacity and work authority remain open.\n",encoding="utf-8");manifest(OUT)
    if REL.exists():shutil.rmtree(REL)
    shutil.copytree(OUT,REL);manifest(REL);print(json.dumps(st,indent=2));return 0
if __name__=="__main__":raise SystemExit(main())
