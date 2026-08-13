#!/usr/bin/env python3
"""Fail-closed checker for the R285 target-feature identity freeze."""
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/"mechanical/analysis/hr-v0-j2-c07-target-feature-identity-p0.1";RELEASE=ROOT/"release/hr-v0/j2-c07-target-feature-identity-p0.1"
def need(x,m):
    if not x:raise SystemExit(m)
def rows(p):
    with p.open(newline="",encoding="utf-8-sig") as s:return list(csv.DictReader(s))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    status=json.loads((OUT/"analysis-status.json").read_text());need(status["identifier"]=="HR-V0-J2-C07-TARGET-FEATURE-IDENTITY-P0.1","identity");need(status["surface_entities"]==12 and status["boundary_curve_entities"]==46 and status["feature_topology_gate"] is True,"counts")
    for key in ("mesh_generated","curved_jacobian_screen_executed","structural_solution_executed","mesh_convergence_complete","r278_h02_closed","capacity_credit","work_authority"):need(status[key] is False,key)
    entities=rows(OUT/"exact-feature-identity-register.csv");need(len(entities)==58,"entity rows");need(len({r["geometric_signature_sha256"] for r in entities})==58,"signature uniqueness");need(all(len(r["geometric_signature_sha256"])==64 and "OCC tag diagnostic only" in r["identity_rule"] for r in entities),"stable identity")
    counts={}
    roles={}
    for r in entities:counts[r["feature_group"]]=counts.get(r["feature_group"],0)+1;roles[r["entity_role"]]=roles.get(r["entity_role"],0)+1
    need(counts=={"BACKSIDE_BOSS_SURFACES":4,"BACKSIDE_BOSS_BOUNDARY_CURVES":20,"ORIGINAL_BORE_SURFACES":6,"ORIGINAL_BORE_BOUNDARY_CURVES":18,"TOP_RAIL_TRANSITION_SURFACES":2,"TOP_RAIL_TRANSITION_BOUNDARY_CURVES":8},"group counts")
    need(roles["BACK_RIM"]==4 and roles["FRONT_INTERSECTION_RIM"]==12 and roles["BORE_RIM"]==12 and roles["LOWER_R2_ARC"]==2 and roles["UPPER_R2_ARC"]==2 and roles["AXIAL_SEAM"]==14,"topology roles")
    topology=rows(OUT/"feature-topology-summary.csv");need(len(topology)==3 and all(r["topology_gate"]=="PASS" for r in topology),"topology summary")
    surfaces=[r for r in entities if r["dimension"]=="2"];need(all(json.loads(r["axis_direction_json"])==[0.0,1.0,0.0] and len(json.loads(r["axis_xz_mm_json"]))==2 and float(r["radius_mm"])>0 and float(r["measure_mm_or_mm2"])>0 for r in surfaces),"axis/radius/area")
    symmetry=rows(OUT/"symmetry-pair-register.csv");need(len(symmetry)==7 and all(r["gate"]=="PASS" and r["bbox_x_mirror_match"]=="True" for r in symmetry),"full symmetry")
    fields={r["field_id"]:r for r in rows(OUT/"recommended-distance-fields.csv")};need(set(fields)=={"R285-F01","R285-F02","R285-F03","R285-F04"},"fields");need(float(fields["R285-F01"]["size_min_mm"])==0.75 and float(fields["R285-F02"]["size_min_mm"])==0.75 and float(fields["R285-F03"]["size_min_mm"])==0.50 and float(fields["R285-F04"]["size_min_mm"])==0.35,"field sizes")
    prereg=json.loads((OUT/"factor-model-feature-preregistration.json").read_text());need(prereg["step_sha256"]==status["step_sha256"] and prereg["authority"]=={"mesh_generation":False,"h02":False,"capacity":False,"work":False},"prereg boundary");need(set(prereg["groups"])==set(counts),"prereg groups")
    for group,count in counts.items():need(prereg["groups"][group]["expected_count"]==count and len(prereg["groups"][group]["geometric_signatures_sha256"])==count,f"prereg {group}")
    provenance=json.loads((OUT/"execution-provenance.json").read_text());need(provenance["generator_sha256"]==sha(ROOT/"tools/generate_hr_v0_j2_c07_target_feature_identity_p01.py"),"generator hash");need(provenance["step_sha256"]==sha(ROOT/provenance["step_path"]),"STEP hash")
    manifest=rows(OUT/"file-manifest.csv");actual=[p for p in OUT.iterdir() if p.is_file() and p.name!="file-manifest.csv"];mapped={r["relative_path"]:r for r in manifest};need(len(manifest)==len(actual),"manifest count")
    for p in actual:need(mapped[p.name]["sha256"]==sha(p) and int(mapped[p.name]["bytes"])==p.stat().st_size,f"manifest {p.name}")
    need(RELEASE.is_dir() and {p.name for p in RELEASE.iterdir() if p.is_file()}=={p.name for p in OUT.iterdir() if p.is_file()},"release files")
    for p in OUT.iterdir():
        if p.is_file():need(sha(p)==sha(RELEASE/p.name),f"release {p.name}")
    print("PASS: R285 exact C07 target feature identities and bounded field prescriptions frozen; no mesh, H02, capacity, or authority")
if __name__=="__main__":main()
