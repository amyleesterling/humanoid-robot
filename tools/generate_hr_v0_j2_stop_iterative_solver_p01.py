#!/usr/bin/env python3
"""Bounded iterative P2 feasibility solve for the exact P0.13 C06 stop.

This tests whether a Jacobi-preconditioned conjugate-gradient backend can
replace the resource-prohibitive direct factorization recorded in R280.  One
coarse case is solver verification evidence only, never convergence/capacity.
"""
from __future__ import annotations

import csv
import json
import shutil
import time
from pathlib import Path

import numpy as np
from scipy.sparse.linalg import LinearOperator, cg
from skfem import Basis, ElementTetP2, ElementVector, FacetBasis, LinearForm, asm, condense
from skfem.models.elasticity import lame_parameters, linear_elasticity

import generate_hr_v0_j2_stop_refinement_execution_p01 as r280


ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"mechanical/analysis/hr-v0-j2-stop-iterative-solver-p0.1"
IDENT="HR-V0-J2-STOP-ITERATIVE-SOLVER-P0.1"
WARNING="PRELIMINARY - NUMERICAL SOLVER FEASIBILITY ONLY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
INITIAL_ATTEMPT={"attempt_id":"R281-C06-ATTEMPT-01","case_id":"C06_EXACT_NORMAL_TOP","cg_info":0,"iterations":2735,"requested_rtol":1e-10,"postcomputed_relative_residual":1.0136109956384771e-10,"normalized_full_force_balance_error":1.6113670141834237e-13,"result":"FAIL TRUE RESIDUAL GATE BY 1.36 PERCENT DESPITE CG INFO ZERO","credit":"NONE","warning":WARNING}


def write_csv(path:Path,records:list[dict[str,object]])->None:
    with path.open("w",newline="",encoding="utf-8") as stream:
        writer=csv.DictWriter(stream,fieldnames=list(records[0]),lineterminator="\n");writer.writeheader();writer.writerows(records)


def main()->int:
    if OUT.exists():shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    write_csv(OUT/"initial-attempt-register.csv",[INITIAL_ATTEMPT])
    level=r280.LEVELS["P2C"]
    mesh,meta,exact_nodes,_samples,_entities=r280.build_mesh("C06",level)
    fixed_facets=r280.tagged_facets(mesh,exact_nodes["holes"]);loaded_facets=r280.tagged_facets(mesh,exact_nodes["load"])
    load_area=r280.area(mesh,loaded_facets);force=np.asarray([0.0,2.186583449470536e-9,-r280.FORCE_N]);traction=force/load_area
    element=ElementVector(ElementTetP2());basis=Basis(mesh,element);lam,mu=lame_parameters(r280.E_MPA,r280.POISSON)
    t0=time.perf_counter();stiffness=asm(linear_elasticity(lam,mu),basis);assembly_s=time.perf_counter()-t0

    @LinearForm
    def load(v,_w):return traction[0]*v[0]+traction[1]*v[1]+traction[2]*v[2]

    load_vector=asm(load,FacetBasis(mesh,element,facets=loaded_facets));fixed_dofs=basis.get_dofs(facets=fixed_facets).all()
    a,b,x,free=condense(stiffness,load_vector,D=fixed_dofs)
    diagonal=a.diagonal();nonpositive=int(np.count_nonzero(diagonal<=0.0))
    if nonpositive:raise RuntimeError(f"nonpositive condensed diagonal entries: {nonpositive}")
    inverse=1.0/diagonal;preconditioner=LinearOperator(a.shape,matvec=lambda value:inverse*value,dtype=a.dtype)
    iterations=0
    def callback(_iterate):
        nonlocal iterations
        iterations+=1
    requested_rtol=5e-11
    solve_start=time.perf_counter();solution,info=cg(a,b,M=preconditioner,rtol=requested_rtol,atol=0.0,maxiter=20000,callback=callback);solve_s=time.perf_counter()-solve_start
    residual=b-a@solution;absolute=float(np.linalg.norm(residual));relative=absolute/float(np.linalg.norm(b))
    x[free]=solution;displacement=x
    reaction=stiffness@displacement-load_vector;applied=load_vector.reshape((-1,3)).sum(axis=0);reacted=reaction.reshape((-1,3)).sum(axis=0)
    equilibrium=float(np.linalg.norm(applied+reacted)/np.linalg.norm(applied));energy=float(0.5*displacement@stiffness@displacement)
    result={"identifier":IDENT,"part":"C06","level":"P2C","solution_order":2,"solution_dofs":int(basis.N),"free_dofs":int(len(free)),"matrix_nonzeros":int(a.nnz),"preconditioner":"Jacobi inverse diagonal","requested_rtol":requested_rtol,"postcomputed_acceptance_relative_residual":1e-10,"atol":0.0,"maximum_iterations":20000,"cg_info":int(info),"iterations":int(iterations),"absolute_condensed_residual_n":absolute,"relative_condensed_residual":relative,"normalized_full_force_balance_error":equilibrium,"strain_energy_n_mm":energy,"maximum_solution_dof_displacement_mm":float(np.max(np.linalg.norm(displacement.reshape((-1,3)),axis=1))),"assembly_seconds":assembly_s,"solve_seconds":solve_s,"convergence_or_capacity_credit":"NONE - single coarse straight-sided P2-displacement feasibility solve","warning":WARNING}
    write_csv(OUT/"solver-result.csv",[result]);write_csv(OUT/"mesh-register.csv",[meta])
    accepted=bool(info==0 and relative<=1e-10 and equilibrium<=1e-8)
    status={"identifier":IDENT,"round":"R281-PROTOTYPE","cad_identifier":"HR-V0-ARM-ARCH-P0.13-PAD-POCKET-STOP-CANDIDATE","backend":"SciPy conjugate gradient with Jacobi diagonal preconditioner","bounded_solver_feasibility_pass":accepted,"solution_order":2,"geometry_order":1,"mesh_convergence_complete":False,"r278_h02_closed":False,"c07_mesh_quality_closed":False,"nonlinear_contact_complete":False,"joined_joint_complete":False,"selected":False,"fabrication_authorized":False,"powered_testing_authorized":False,"motion_authorized":False,"energization_authorized":False,"safety_credit":False,"warning":WARNING}
    (OUT/"analysis-status.json").write_text(json.dumps(status,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2));print(json.dumps(status,indent=2));return 0 if accepted else 2


if __name__=="__main__":raise SystemExit(main())
