#!/usr/bin/env python3
"""Bounded exact-CAD direct-versus-CG backend comparison for R281-ACC-04."""
from __future__ import annotations
import csv,json,shutil,time
from pathlib import Path
import numpy as np
from scipy.sparse.linalg import LinearOperator,cg,spsolve
from skfem import Basis,ElementTetP2,ElementVector,FacetBasis,LinearForm,MeshTet,asm,condense
from skfem.models.elasticity import lame_parameters,linear_elasticity
import generate_hr_v0_j2_stop_refinement_execution_p01 as base

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/"mechanical/analysis/hr-v0-j2-backend-crosscheck-p0.1"
IDENT="HR-V0-J2-BACKEND-CROSSCHECK-P0.1";WARNING="PRELIMINARY - NUMERICAL BACKEND CROSS-CHECK ONLY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"

def write_csv(path,rows):
    with path.open("w",newline="",encoding="utf-8") as s:w=csv.DictWriter(s,fieldnames=list(rows[0]),lineterminator="\n");w.writeheader();w.writerows(rows)

def main():
    if OUT.exists():shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    level=base.Level("XCHK",8.0,2.5,1.6,2.0)
    mesh,meta,nodes,_samples,_entities=base.build_mesh("C06",level)
    fixed=base.tagged_facets(mesh,nodes["holes"]);loaded=base.tagged_facets(mesh,nodes["load"]);area=base.area(mesh,loaded)
    force=np.asarray([0.0,2.186583449470536e-9,-base.FORCE_N]);traction=force/area;element=ElementVector(ElementTetP2());basis=Basis(mesh,element);lam,mu=lame_parameters(base.E_MPA,base.POISSON)
    k=asm(linear_elasticity(lam,mu),basis)
    @LinearForm
    def load(v,_w):return traction[0]*v[0]+traction[1]*v[1]+traction[2]*v[2]
    rhs=asm(load,FacetBasis(mesh,element,facets=loaded));a,b,x,free=condense(k,rhs,D=basis.get_dofs(facets=fixed).all())
    t=time.perf_counter();ud=spsolve(a,b);direct_s=time.perf_counter()-t
    iterations=0
    def cb(_):
        nonlocal iterations;iterations+=1
    M=LinearOperator(a.shape,matvec=lambda value:value/a.diagonal(),dtype=a.dtype)
    t=time.perf_counter();ui,info=cg(a,b,M=M,rtol=5e-11,atol=0,maxiter=20000,callback=cb);iter_s=time.perf_counter()-t
    rows=[]
    solutions={"SCIPY_SUPERLU_DIRECT":ud,"SCIPY_CG_JACOBI":ui}
    for name,sol in solutions.items():
        u=x.copy();u[free]=sol;reaction=k@u-rhs;applied=rhs.reshape((-1,3)).sum(axis=0);reacted=reaction.reshape((-1,3)).sum(axis=0)
        rows.append({"solver":name,"solution_order":2,"geometry_order":1,"solution_dofs":basis.N,"free_dofs":len(free),"matrix_nonzeros":a.nnz,"relative_true_residual":float(np.linalg.norm(a@sol-b)/np.linalg.norm(b)),"normalized_force_balance":float(np.linalg.norm(applied+reacted)/np.linalg.norm(applied)),"strain_energy_n_mm":float(.5*u@k@u),"maximum_dof_displacement_mm":float(np.max(np.linalg.norm(u.reshape((-1,3)),axis=1))),"iterations":0 if name.endswith("DIRECT") else iterations,"seconds":direct_s if name.endswith("DIRECT") else iter_s,"warning":WARNING})
    d,i=rows
    agreement={"identifier":IDENT,"case":"C06 exact CAD deliberately coarse P2-displacement/linear-geometry","cg_info":int(info),"solution_relative_l2_difference":float(np.linalg.norm(ui-ud)/np.linalg.norm(ud)),"energy_relative_difference":abs(float(i["strain_energy_n_mm"])-float(d["strain_energy_n_mm"]))/abs(float(d["strain_energy_n_mm"])),"max_displacement_relative_difference":abs(float(i["maximum_dof_displacement_mm"])-float(d["maximum_dof_displacement_mm"]))/abs(float(d["maximum_dof_displacement_mm"])),"acceptance_tolerance":1e-8,"direct_true_residual_gate":1e-10,"iterative_true_residual_gate":1e-10,"backend_crosscheck_pass":False,"affine_patch_test_executed":True,"r281_acc_04_closed":False,"r278_h02_closed":False,"capacity_credit":False,"work_authority":False,"warning":WARNING}
    agreement["backend_crosscheck_pass"]=bool(info==0 and max(agreement["solution_relative_l2_difference"],agreement["energy_relative_difference"],agreement["max_displacement_relative_difference"])<=1e-8 and all(float(r["relative_true_residual"])<=1e-10 for r in rows))
    # Analytic affine 3D elasticity patch: the exact field lies in P2.
    pm=MeshTet.init_tensor(np.asarray([0.,.5,1.]),np.asarray([0.,.5,1.]),np.asarray([0.,.5,1.]))
    pb=Basis(pm,ElementVector(ElementTetP2()));pk=asm(linear_elasticity(lam,mu),pb)
    aa,bb,cc,gg=1.2e-4,-0.7e-4,0.9e-4,0.4e-4
    exact=np.zeros(pb.N);loc=pb.doflocs
    exact[0::3]=aa*loc[0,0::3]+gg*loc[1,0::3];exact[1::3]=bb*loc[1,1::3];exact[2::3]=cc*loc[2,2::3]
    boundary=pb.get_dofs().all();pa,pbvec,px,pfree=condense(pk,np.zeros(pb.N),x=exact,D=boundary)
    pd=spsolve(pa,pbvec);piters=0
    def pcb(_):
        nonlocal piters;piters+=1
    pM=LinearOperator(pa.shape,matvec=lambda value:value/pa.diagonal(),dtype=pa.dtype);pi,pinfo=cg(pa,pbvec,M=pM,rtol=1e-12,atol=0,maxiter=10000,callback=pcb)
    eps=np.asarray([[aa,gg/2,0],[gg/2,bb,0],[0,0,cc]]);sig=2*mu*eps+lam*np.trace(eps)*np.eye(3);analytic_energy=float(.5*np.sum(eps*sig))
    patch=[]
    for name,sol in (("SCIPY_SUPERLU_DIRECT",pd),("SCIPY_CG_JACOBI",pi)):
        pu=px.copy();pu[pfree]=sol;pr=pk@pu;forces=pr.reshape((-1,3));coords=loc[:,0::3].T
        patch.append({"solver":name,"cg_info":0 if name.endswith("DIRECT") else int(pinfo),"iterations":0 if name.endswith("DIRECT") else piters,"relative_dof_error":float(np.linalg.norm(pu-exact)/np.linalg.norm(exact)),"computed_energy":float(.5*pu@pk@pu),"analytic_energy":analytic_energy,"relative_energy_error":abs(float(.5*pu@pk@pu)-analytic_energy)/analytic_energy,"reaction_resultant_norm_n":float(np.linalg.norm(forces.sum(axis=0))),"reaction_moment_origin_norm_n_mm":float(np.linalg.norm(np.cross(coords,forces).sum(axis=0))),"warning":WARNING})
    agreement["affine_patch_test_pass"]=bool(all(float(r["relative_dof_error"])<=1e-11 and float(r["relative_energy_error"])<=1e-11 and float(r["reaction_resultant_norm_n"])<=1e-10 and float(r["reaction_moment_origin_norm_n_mm"])<=1e-10 for r in patch))
    # ACC-04 remains open pending independent reviewer acceptance of method and thresholds.
    write_csv(OUT/"solver-register.csv",rows);write_csv(OUT/"agreement-register.csv",[agreement]);write_csv(OUT/"affine-patch-register.csv",patch);write_csv(OUT/"mesh-register.csv",[meta]);(OUT/"analysis-status.json").write_text(json.dumps(agreement,indent=2,default=lambda v:v.item())+"\n",encoding="utf-8");print(json.dumps({"solvers":rows,"agreement":agreement,"patch":patch},indent=2,default=lambda v:v.item()));return 0 if agreement["backend_crosscheck_pass"] and agreement["affine_patch_test_pass"] else 2
if __name__=="__main__":raise SystemExit(main())
