#!/usr/bin/env python3
"""Bounded iterative P2 feasibility solves for exact P0.13 C07 paths."""
from __future__ import annotations

import csv
import json
import shutil
import time
from pathlib import Path

import numpy as np
from scipy.sparse.linalg import LinearOperator,cg
from skfem import Basis,ElementTetP2,ElementVector,FacetBasis,LinearForm,asm,condense
from skfem.models.elasticity import lame_parameters,linear_elasticity

import generate_hr_v0_j2_stop_refinement_execution_p01 as base


ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"mechanical/analysis/hr-v0-j2-c07-iterative-solver-p0.1"
IDENT="HR-V0-J2-C07-ITERATIVE-SOLVER-P0.1"
WARNING="PRELIMINARY - NUMERICAL SOLVER FEASIBILITY ONLY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
INITIAL_ATTEMPTS=[
    {"attempt_id":"R281-C07-ATTEMPT-01","case_id":"C07_METAL_PERIMETER_EXACT_NORMAL","cg_info":0,"iterations":2590,"requested_rtol":5e-11,"postcomputed_relative_residual":8.996679030930099e-11,"normalized_full_force_balance_error":5.807143056957282e-13,"result":"PASS BOUNDED SOLVER FEASIBILITY","credit":"NONE - SINGLE COARSE CASE","warning":WARNING},
    {"attempt_id":"R281-C07-ATTEMPT-01","case_id":"C07_POCKET_FLOOR_EXACT_NORMAL","cg_info":0,"iterations":2636,"requested_rtol":5e-11,"postcomputed_relative_residual":3.47623501387561e-10,"normalized_full_force_balance_error":5.408437535970067e-13,"result":"FAIL TRUE RESIDUAL GATE DESPITE CG INFO ZERO","credit":"NONE","warning":WARNING},
]


def write_csv(path:Path,records:list[dict[str,object]])->None:
    with path.open("w",newline="",encoding="utf-8") as stream:
        writer=csv.DictWriter(stream,fieldnames=list(records[0]),lineterminator="\n");writer.writeheader();writer.writerows(records)


def main()->int:
    if OUT.exists():shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    write_csv(OUT/"initial-attempt-register.csv",INITIAL_ATTEMPTS)
    mesh,meta,exact_nodes,_samples,_entities=base.build_mesh("C07",base.LEVELS["P2C"],algorithm3d=1,optimize_method="Netgen")
    quality_pass=float(meta["min_sicn"])>=0.10 and float(meta["fraction_sicn_below_0p20"])<=0.001
    if not quality_pass:raise RuntimeError(f"C07 P2C mesh quality failed: {meta}")
    fixed_facets=base.tagged_facets(mesh,exact_nodes["holes"]);element=ElementVector(ElementTetP2());basis=Basis(mesh,element)
    lam,mu=lame_parameters(base.E_MPA,base.POISSON);t0=time.perf_counter();stiffness=asm(linear_elasticity(lam,mu),basis);assembly_s=time.perf_counter()-t0
    fixed_dofs=basis.get_dofs(facets=fixed_facets).all();force=np.asarray([0.0,-223.9218979819317,-119.06088380811465]);requested_rtol=5e-11
    results=[]
    for case in ("C07_METAL_PERIMETER_EXACT_NORMAL","C07_POCKET_FLOOR_EXACT_NORMAL"):
        if case.startswith("C07_METAL"):
            loaded=base.tagged_facets(mesh,exact_nodes["metal_face"]);centers=mesh.p[:,mesh.facets[:,loaded]].mean(axis=1);loaded=loaded[centers[0]>34.0]
        else:loaded=base.tagged_facets(mesh,exact_nodes["pocket_floor"])
        area=base.area(mesh,loaded);traction=force/area
        @LinearForm
        def load(v,_w):return traction[0]*v[0]+traction[1]*v[1]+traction[2]*v[2]
        load_vector=asm(load,FacetBasis(mesh,element,facets=loaded));a,b,x,free=condense(stiffness,load_vector,D=fixed_dofs)
        diagonal=a.diagonal();nonpositive=int(np.count_nonzero(diagonal<=0.0))
        if nonpositive:raise RuntimeError(f"nonpositive diagonal: {nonpositive}")
        inverse=1.0/diagonal;preconditioner=LinearOperator(a.shape,matvec=lambda value:inverse*value,dtype=a.dtype);iterations=0
        def callback(_iterate):
            nonlocal iterations
            iterations+=1
        start=time.perf_counter();solution,info=cg(a,b,M=preconditioner,rtol=requested_rtol,atol=0.0,maxiter=20000,callback=callback)
        residual=b-a@solution;relative=float(np.linalg.norm(residual)/np.linalg.norm(b));correction_passes=0;correction_iterations=0
        # CG's recursive stopping residual can differ from the explicitly
        # recomputed residual.  Apply no more than two correction solves to the
        # true residual; never relax the postcomputed 1e-10 acceptance gate.
        while info==0 and relative>1e-10 and correction_passes<2:
            local_iterations=0
            def correction_callback(_iterate):
                nonlocal local_iterations
                local_iterations+=1
            correction,correction_info=cg(a,residual,M=preconditioner,rtol=1e-6,atol=0.0,maxiter=10000,callback=correction_callback)
            correction_passes+=1;correction_iterations+=local_iterations;solution+=correction;residual=b-a@solution;relative=float(np.linalg.norm(residual)/np.linalg.norm(b))
            if correction_info!=0:
                info=correction_info
        solve_s=time.perf_counter()-start;x[free]=solution;displacement=x
        reaction=stiffness@displacement-load_vector;applied=load_vector.reshape((-1,3)).sum(axis=0);reacted=reaction.reshape((-1,3)).sum(axis=0);equilibrium=float(np.linalg.norm(applied+reacted)/np.linalg.norm(applied))
        passed=bool(info==0 and relative<=1e-10 and equilibrium<=1e-8)
        results.append({"identifier":IDENT,"case_id":case,"part":"C07","level":"P2C","solution_order":2,"solution_dofs":int(basis.N),"free_dofs":int(len(free)),"matrix_nonzeros":int(a.nnz),"preconditioner":"Jacobi inverse diagonal","requested_rtol":requested_rtol,"postcomputed_acceptance_relative_residual":1e-10,"maximum_iterations":20000,"cg_info":int(info),"initial_iterations":int(iterations),"true_residual_correction_passes":correction_passes,"true_residual_correction_iterations":correction_iterations,"relative_condensed_residual":relative,"normalized_full_force_balance_error":equilibrium,"strain_energy_n_mm":float(0.5*displacement@stiffness@displacement),"maximum_solution_dof_displacement_mm":float(np.max(np.linalg.norm(displacement.reshape((-1,3)),axis=1))),"loaded_area_mm2":area,"assembly_seconds_shared":assembly_s,"solve_seconds":solve_s,"bounded_solver_feasibility":"PASS" if passed else "FAIL","convergence_or_capacity_credit":"NONE - single coarse straight-sided P2-displacement feasibility solve","warning":WARNING})
    write_csv(OUT/"solver-results.csv",results);write_csv(OUT/"mesh-register.csv",[meta])
    all_pass=all(r["bounded_solver_feasibility"]=="PASS" for r in results)
    status={"identifier":IDENT,"round":"R281-PROTOTYPE","cad_identifier":"HR-V0-ARM-ARCH-P0.13-PAD-POCKET-STOP-CANDIDATE","mesh_method":"Gmsh Delaunay algorithm 1 plus Netgen optimization","mesh_quality_pass":quality_pass,"backend":"SciPy conjugate gradient with Jacobi diagonal preconditioner","bounded_solver_cases_pass":all_pass,"case_count":2,"solution_order":2,"geometry_order":1,"mesh_convergence_complete":False,"r278_h02_closed":False,"nonlinear_contact_complete":False,"joined_joint_complete":False,"selected":False,"fabrication_authorized":False,"powered_testing_authorized":False,"motion_authorized":False,"energization_authorized":False,"safety_credit":False,"warning":WARNING}
    (OUT/"analysis-status.json").write_text(json.dumps(status,indent=2)+"\n",encoding="utf-8");print(json.dumps(results,indent=2));print(json.dumps(status,indent=2));return 0 if all_pass else 2


if __name__=="__main__":raise SystemExit(main())
