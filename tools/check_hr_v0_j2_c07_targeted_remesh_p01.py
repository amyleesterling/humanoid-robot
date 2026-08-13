#!/usr/bin/env python3
"""Fail-closed checker for the R285 targeted C07 remesh package."""
import csv, hashlib, json
from datetime import datetime
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "mechanical/analysis/hr-v0-j2-c07-targeted-remesh-p0.1"
REL = ROOT / "release/hr-v0/j2-c07-targeted-remesh-p0.1"
WARNING = "PRELIMINARY - TARGETED CURVED-MESH METHOD EVIDENCE ONLY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"

def need(value, message):
    if not value: raise SystemExit(message)
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def rows(path):
    with path.open(newline="", encoding="utf-8-sig") as stream: return list(csv.DictReader(stream))
def verify(directory):
    record = rows(directory / "file-manifest.csv")
    actual = [p for p in directory.rglob("*") if p.is_file() and p.name != "file-manifest.csv"]
    need(len(record) == len(actual), f"manifest count {directory}")
    index = {r["relative_path"]: r for r in record}
    need(len(index) == len(record), f"duplicate manifest path {directory}")
    for path in actual:
        row = index.get(path.relative_to(directory).as_posix())
        need(row and row["sha256"] == sha(path) and int(row["bytes"]) == path.stat().st_size, f"manifest {path}")
    for path in directory.rglob("*.csv"):
        data = rows(path)
        need(data and "warning" in data[0] and all(r["warning"] == WARNING for r in data), f"warning {path}")
    for path in directory.rglob("*.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        need(data.get("warning") == WARNING, f"JSON warning {path}")
    need(f"> **{WARNING}**" in (directory / "README.md").read_text(encoding="utf-8"), f"README warning {directory}")

def main():
    for directory in (OUT, REL): need(directory.is_dir(), f"missing {directory}"); verify(directory)
    a = {p.relative_to(OUT).as_posix(): sha(p) for p in OUT.rglob("*") if p.is_file()}
    b = {p.relative_to(REL).as_posix(): sha(p) for p in REL.rglob("*") if p.is_file()}
    need(a == b, "source/release mismatch")
    status = json.loads((OUT / "analysis-status.json").read_text())
    need(status["identifier"] == "HR-V0-J2-C07-TARGETED-REMESH-P0.1" and status["round"] == "R285", "identity")
    need(status["warning"] == WARNING and status["runs_executed"] == 3, "status")
    need(status["all_fresh_process_return_codes_zero"] and status["all_runs_pass"] and status["independently_reconstructed_q4_q6_q8_pass"] and status["raw_arrays_exactly_repeatable"] and status["target_entity_discovery_exactly_repeatable"] and status["bounded_targeted_method_screen_pass"], "method/repeatability")
    need(not any(status[k] for k in ("surface_deviation_from_brep_complete", "exact_facet_map_complete", "exact_zone_clipped_histograms_complete", "full_domain_curved_jacobian_positivity_proven", "load_boundary_preservation_complete", "r279_c02_complete", "r278_h02_closed", "selected", "safety_credit", "capacity_credit", "work_authority", "fabrication_authorized", "powered_testing_authorized", "motion_authorized", "energization_authorized")), "credit/authority")
    summary = rows(OUT / "variant-summary.csv")
    need(len(summary) == 3, "summary count")
    need([r["run_id"] for r in summary] == ["run-a", "run-b-repeat", "run-c-repeat"], "summary run order")
    raw_by_run = {}
    target_by_run = {}
    for row in summary:
        need(row["high_order_optimizer"] == "NONE" and row["mesh_repair_pass"].lower() == "true", "variant pass")
        need(int(row["curved_wrong_or_zero_across_screens"]) == 0 and int(row["normalized_determinant_fail_across_screens"]) == 0, "Jacobian counts")
        need(row["r279_c02_complete"].lower() == "false" and row["r278_h02_closed"].lower() == "false", "credits")
        run = OUT / row["run_id"]
        corner_path = run / "corner-bijection-r285-confirmatory-targeted-v06-p01.csv"
        element_path = run / "element-corner-identity-r285-confirmatory-targeted-v06-p01.csv"
        edge_path = run / "edge-map-r285-confirmatory-targeted-v06-p01.csv"
        need(len(rows(corner_path)) == int(row["vertices"]), "corner rows")
        need(len(rows(element_path)) == int(row["tet10_elements"]), "element rows")
        need(len(rows(edge_path)) == int(row["global_edges"]), "midside rows")
        raw_path = ROOT / row["raw_npz"]
        need(sha(raw_path) == row["raw_npz_sha256"] and sha(edge_path) == row["edge_map_sha256"], "declared evidence hashes")
        raw = np.load(raw_path)
        raw_by_run[row["run_id"]] = {name: np.array(raw[name], copy=True) for name in raw.files}
        target_by_run[row["run_id"]] = rows(run / "exact-target-entity-register.csv")
        need(raw["tet10_connectivity"].shape == (int(row["tet10_elements"]), 10), "raw Tet10 shape")
        need(raw["linear_sicn"].shape == (int(row["tet10_elements"]),), "raw SICN shape")
        need(np.isfinite(raw["node_xyz"]).all() and np.isfinite(raw["linear_sicn"]).all(), "raw finite values")
        need(len(np.unique(raw["tet10_element_tags"])) == int(row["tet10_elements"]), "raw element tag uniqueness")
    reference = raw_by_run["run-a"]
    for run_id in ("run-b-repeat", "run-c-repeat"):
        candidate = raw_by_run[run_id]
        need(set(candidate) == set(reference), f"raw key set {run_id}")
        need(all(np.array_equal(reference[key], candidate[key]) for key in reference), f"recomputed raw repeatability {run_id}")
        need(target_by_run[run_id] == target_by_run["run-a"], f"target registry repeatability {run_id}")
    targets = target_by_run["run-a"]
    counts = {group: sum(r["feature_group"] == group for r in targets) for group in {r["feature_group"] for r in targets}}
    need(counts == {"BACKSIDE_BOSS_SURFACES": 4, "BACKSIDE_BOSS_BOUNDARY_CURVES": 20, "ORIGINAL_BORE_SURFACES": 6, "ORIGINAL_BORE_BOUNDARY_CURVES": 18, "TOP_RAIL_TRANSITION_SURFACES": 2, "TOP_RAIL_TRANSITION_BOUNDARY_CURVES": 8}, f"target counts {counts}")
    need(all(r["identity_match"].lower() == "true" for r in targets), "target identity")
    need(len({r["geometric_signature_sha256"] for r in targets}) == 58, "signature uniqueness")
    protocol = json.loads((OUT / "frozen-protocol.json").read_text())
    feature_root = ROOT / "mechanical/analysis/hr-v0-j2-c07-target-feature-identity-p0.1"
    prereg = json.loads((feature_root / "factor-model-feature-preregistration.json").read_text())
    expected = {"BACKSIDE_BOSS_SURFACES": 4, "BACKSIDE_BOSS_BOUNDARY_CURVES": 20, "ORIGINAL_BORE_SURFACES": 6, "ORIGINAL_BORE_BOUNDARY_CURVES": 18, "TOP_RAIL_TRANSITION_SURFACES": 2, "TOP_RAIL_TRANSITION_BOUNDARY_CURVES": 8}
    need({group: prereg["groups"][group]["expected_count"] for group in expected} == expected, "prereg counts")
    need(protocol["feature_identity_register_sha256"] == sha(feature_root / "exact-feature-identity-register.csv") and protocol["feature_preregistration_sha256"] == sha(feature_root / "factor-model-feature-preregistration.json"), "feature hashes")
    need(protocol["feature_identity_generator_sha256"] == sha(ROOT / "tools/generate_hr_v0_j2_c07_target_feature_identity_p01.py") and protocol["feature_identity_checker_sha256"] == sha(ROOT / "tools/check_hr_v0_j2_c07_target_feature_identity_p01.py"), "feature tool hashes")
    generator = ROOT / "tools/generate_hr_v0_j2_c07_targeted_remesh_p01.py"
    provenance = json.loads((OUT / "execution-provenance.json").read_text())
    need(provenance["generator_sha256"] == sha(generator) and provenance["frozen_protocol_sha256"] == sha(OUT / "frozen-protocol.json"), "execution provenance hashes")
    need(provenance["transitive_r283_generator_sha256"] == sha(ROOT / "tools/generate_hr_v0_j2_c07_curved_mesh_repair_p01.py"), "R283 generator hash")
    need(provenance["transitive_occ_field_generator_sha256"] == sha(ROOT / "tools/generate_hr_v0_j2_stop_refinement_execution_p01.py"), "OCC generator hash")
    need(provenance["localization_action_sha256"] == sha(ROOT / "mechanical/analysis/hr-v0-j2-c07-failure-localization-p0.1/actionable-meshing-correction.json"), "localization hash")
    need(provenance["feature_identity_register_sha256"] == sha(feature_root / "exact-feature-identity-register.csv") and provenance["feature_preregistration_sha256"] == sha(feature_root / "factor-model-feature-preregistration.json"), "provenance feature hashes")
    need(provenance["feature_identity_generator_sha256"] == sha(ROOT / "tools/generate_hr_v0_j2_c07_target_feature_identity_p01.py") and provenance["feature_identity_checker_sha256"] == sha(ROOT / "tools/check_hr_v0_j2_c07_target_feature_identity_p01.py"), "provenance feature tool hashes")
    need(provenance["variant_id"] == protocol["variant_id"] and provenance["general_num_threads"] == 1 and provenance["algorithm3d"] == 1 and provenance["linear_optimizer"] == "Netgen" and provenance["high_order_optimizer"] == "NONE", "execution options")
    need(protocol["fresh_process_runs"] == ["run-a", "run-b-repeat", "run-c-repeat"] and protocol["sampled_quadrature_orders"] == [4, 6, 8], "frozen run protocol")
    runtimes = []
    for run_id in ("run-a", "run-b-repeat", "run-c-repeat"):
        runtime = json.loads((OUT / run_id / "runtime-provenance.json").read_text())
        need(runtime["fresh_python_process"] is True and runtime["generator_sha256"] == sha(generator) and runtime["frozen_protocol_sha256"] == sha(OUT / "frozen-protocol.json"), f"runtime provenance {run_id}")
        need(runtime["run_id"] == run_id and runtime["variant_id"] == protocol["variant_id"], f"runtime identity {run_id}")
        need(runtime["command"][-2:] == ["--single-run", run_id], f"fresh-process command {run_id}")
        need(runtime["step_sha256"] == status["step_sha256"] and runtime["feature_identity_generator_sha256"] == protocol["feature_identity_generator_sha256"] and runtime["feature_identity_checker_sha256"] == protocol["feature_identity_checker_sha256"], f"runtime inputs {run_id}")
        started = datetime.fromisoformat(runtime["started_utc"]); completed = datetime.fromisoformat(runtime["completed_utc"])
        need(started < completed, f"runtime timestamps {run_id}")
        runtimes.append((started, completed))
    need(all(runtimes[i][1] <= runtimes[i + 1][0] for i in range(2)), "fresh processes not sequentially distinct")
    fresh = rows(OUT / "fresh-process-register.csv")
    need([r["run_id"] for r in fresh] == protocol["fresh_process_runs"] and all(int(r["return_code"]) == 0 for r in fresh), "fresh process records")
    repeat = rows(OUT / "repeatability-register.csv")
    need(repeat and all(r["present_both"].lower() == "true" and r["exactly_equal"].lower() == "true" and float(r["maximum_absolute_delta"]) == 0.0 for r in repeat), "repeat arrays")
    independent = rows(OUT / "independent-jacobian-register.csv")
    need(len(independent) == 9 and all(int(r["wrong_or_zero"]) == 0 and int(r["normalized_at_or_below_1e_10"]) == 0 for r in independent), "independent Jacobian")
    histogram = rows(OUT / "global-sicn-histogram.csv")
    need(len(histogram) == 30, "histogram rows")
    for run_id in ("run-a", "run-b-repeat", "run-c-repeat"):
        group = [r for r in histogram if r["run_id"] == run_id]
        need(len(group) == 10 and sum(int(r["count"]) for r in group) == int(group[0]["population"]), "histogram population")
    need("finite samples" in status["jacobian_evidence_scope"] and "not proof" in status["jacobian_evidence_scope"], "finite wording")
    print("PASS: R285 targeted C07 remesh repeated exactly; R279-C02/H02/B-Rep/facet/capacity/work credit remains open")
    return 0

if __name__ == "__main__": raise SystemExit(main())
