from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "cad" / "hr-v0" / "generated" / "fx104-c01-p0.1"
WEB = ROOT / "release" / "hr-v0" / "fx104-c01-p0.1"
KAISER = ROOT / "cad" / "vendor" / "kaiser" / "6061-t651-r105"


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> None:
    errors: list[str] = []
    required = ["FX104-C01_P0.1_fabrication_candidate.step","FX104-C01_P0.1_fabrication_candidate.glb","FX104-C01_P0.1_drawing.svg","feature-register.csv","analysis-register.csv","material-process-register.csv","inspection-plan.csv","source-register.csv","parent-artifact-register.csv","open-hold-register.csv","dfm-rfi.csv","geometry-check.json","package-status.json"]
    errors.extend(f"missing {name}" for name in required if not (OUT / name).exists())
    if not (WEB / "index.html").exists(): errors.append("missing interactive guide")
    if errors: raise SystemExit("\n".join(errors))

    expected = {
        KAISER / "Kaiser_Aluminum_6061_Sheet_Coil_and_Plate.pdf":"93BF49F80542098953171C9FB72E4AF72505AA8204AE39A4AFB97102A69EEC05",
        KAISER / "KaiserSelect_General_Engineering_Plate.pdf":"7E8CF6D3C71336519DB010D2C908BDBE732E47F7D9F4A4BA6F5CA67063040341",
    }
    for path, digest in expected.items():
        if not path.exists() or sha256(path) != digest: errors.append(f"controlled source changed: {path.name}")
    sources = rows("source-register.csv")
    if len(sources) != 4 or [r["sha256"] for r in sources[:2]] != list(expected.values()): errors.append("source register changed")
    features = rows("feature-register.csv")
    if len(features) != 10 or features[5]["nominal"] != "2X M6 x 1 - 6H at X=0, Y=±52 BASIC" or features[6]["nominal"] != "4X Ø6.6 THRU at X=±30, Y=±50 BASIC": errors.append("feature definition changed")
    if any(r["state"] != "DEFINED CANDIDATE" for r in features): errors.append("feature state promoted")
    analyses = rows("analysis-register.csv")
    if len(analyses) != 12: errors.append("analysis count changed")
    else:
        numeric = [float(r["result"].split()[0]) for r in analyses[:10]]
        if not math.isclose(numeric[0], 922.343747, abs_tol=1e-6): errors.append("mass screen changed")
        if not math.isclose(numeric[1], 17.212082, abs_tol=1e-6): errors.append("weight-moment screen changed")
        if not math.isclose(numeric[2], 8.2, abs_tol=1e-9): errors.append("torque screen changed")
        if not all(value > 0 for value in numeric): errors.append("nonpositive analysis result")
        if "not a minimum" not in analyses[10]["authority"].lower(): errors.append("typical-property caveat missing")
    process = rows("material-process-register.csv")
    if len(process) != 5 or "certificate" not in process[0]["evidence"]: errors.append("material/trace control changed")
    inspections = rows("inspection-plan.csv")
    if len(inspections) != 9 or any(r["result"] != "NOT EXECUTED" for r in inspections): errors.append("physical inspection asserted")
    parents = rows("parent-artifact-register.csv")
    if len(parents) != 3 or any(sha256(ROOT / r["artifact"]) != r["sha256"] for r in parents): errors.append("parent artifact changed")
    holds = rows("open-hold-register.csv")
    if len(holds) != 10 or sum(r["state"] == "PARTIAL" for r in holds) != 3 or sum(r["state"] == "OPEN" for r in holds) != 7: errors.append("hold state changed")
    rfis = rows("dfm-rfi.csv")
    if len(rfis) != 5 or any(r["state"] != "NOT SENT" for r in rfis): errors.append("RFI state changed")

    geometry = json.loads((OUT / "geometry-check.json").read_text(encoding="utf-8"))
    if geometry.get("identifier") != "HR-V0-FX104-C01-FAB-P0.1" or geometry.get("envelope_mm") != {"x":90.0,"y":160.0,"z":24.0}: errors.append("geometry identity/envelope changed")
    if geometry.get("upper_features",{}).get("axes_mm") != [[0,-52.0],[0,52.0]] or geometry.get("lower_features",{}).get("axes_mm") != [[-30.0,-50.0],[-30.0,50.0],[30.0,-50.0],[30.0,50.0]]: errors.append("hole axes changed")
    if not math.isclose(geometry.get("volume_mm3",0), 341608.795, abs_tol=0.01): errors.append("nominal CAD volume changed")
    if geometry.get("thread_geometry_in_step") is not False or geometry.get("drawing_controls_threads") is not True or geometry.get("fabrication_release") is not False or geometry.get("capacity_credit") is not False: errors.append("geometry boundary promoted")
    if sha256(OUT / "FX104-C01_P0.1_fabrication_candidate.step") != geometry.get("step_sha256"): errors.append("STEP hash mismatch")

    status = json.loads((OUT / "package-status.json").read_text(encoding="utf-8"))
    if status.get("part_definition_complete_for_independent_review") is not True or status.get("material_candidate_defined") is not True or status.get("feature_tolerances_defined") is not True or status.get("inspection_plan_defined") is not True: errors.append("candidate definition incomplete")
    for field in ("supplier_contacted","dfm_complete","qualified_analysis_approved","manufacturer_application_accepted","fasteners_selected","fai_executed","proof_executed"):
        if status.get(field) is not False: errors.append(f"fail-closed state promoted: {field}")
    if status.get("partial_hold_count") != 3 or status.get("open_hold_count") != 7 or status.get("rfi_count") != 5 or status.get("rfi_state") != "NOT SENT": errors.append("status counts changed")
    if any(v is not False for v in status.get("release_flags",{}).values()): errors.append("release flag promoted")

    drawing = (OUT / "FX104-C01_P0.1_drawing.svg").read_text(encoding="utf-8")
    for phrase in ("90.00 ±0.10","160.00 ±0.10","24.00 ±0.05","M6 x 1 - 6H","POSITION Ø0.20 | A | B | C","FLATNESS 0.05","DO NOT QUOTE, MACHINE, ASSEMBLE OR POWER","font-size:20px"):
        if phrase not in drawing: errors.append(f"drawing control missing: {phrase}")
    guide = (WEB / "index.html").read_text(encoding="utf-8")
    for phrase in ("real part definition","6061-T651","0.922 kg","17.21 N·m","8.20 N·m","not a machining release","font-size:14px","font-size:16px","No supplier was contacted"):
        if phrase not in guide: errors.append(f"guide control/readability missing: {phrase}")
    if errors: raise SystemExit("HR-V0 FX104 adapter check FAILED:\n- " + "\n- ".join(errors))
    print("HR-V0 FX104-C01 fabrication-candidate check: PASS")
    print("10 defined features; 12 calculation screens; 9 unexecuted inspections; 5 unsent RFIs")
    print("3 partial + 7 open holds; no DFM/FAI/proof/fastener/manufacturer acceptance; all release flags false")


if __name__ == "__main__":
    main()
