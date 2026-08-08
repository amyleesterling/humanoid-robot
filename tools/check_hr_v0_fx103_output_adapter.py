"""Validate the R106 FX103 two-piece output-adapter candidate."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "cad" / "hr-v0" / "generated" / "fx103-output-adapter-p0.2"
WEB = ROOT / "release" / "hr-v0" / "fx103-output-adapter-p0.2" / "index.html"
CARPENTER = ROOT / "cad" / "vendor" / "carpenter" / "custom-630-r106"
IDENTIFIER = "HR-V0-FX103-OUTPUT-ADAPTER-FAB-P0.2"
EXPECTED_CARPENTER_SHA256 = "BCE080D21EE992F6220A7346E7FF6BE3849543F41EF258EAF44DC17A82E44640"
MODEL_VIEWER = ROOT / "release" / "vendor" / "model-viewer" / "4.1.0"
EXPECTED_MODEL_VIEWER_SHA256 = "8367184A607FBE07A78B650C0D359E5EBBD96F7E2B22F95F761F559B63430386"
EXPECTED_MODEL_VIEWER_LICENSE_SHA256 = "CFC7749B96F63BD31C3C42B5C471BF756814053E847C10F3EB003417BC523D30"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    expected_files = [
        "FX103-C01_P0.2_horn_flange.step",
        "FX103-C02_P0.1_shaft_flange.step",
        "FX103_output_adapter_P0.2_review.step",
        "FX103_output_adapter_P0.2_review.glb",
        "FX103_output_adapter_P0.2_drawing.svg",
        "feature-register.csv",
        "analysis-register.csv",
        "material-process-register.csv",
        "inspection-plan.csv",
        "source-register.csv",
        "parent-artifact-register.csv",
        "open-hold-register.csv",
        "dfm-rfi.csv",
        "geometry-check.json",
        "package-status.json",
    ]
    for name in expected_files:
        require((OUT / name).is_file() and (OUT / name).stat().st_size > 0, f"missing/empty {name}")
    require(WEB.is_file(), "interactive guide missing")
    require(sha256(MODEL_VIEWER / "model-viewer.min.js") == EXPECTED_MODEL_VIEWER_SHA256, "model-viewer runtime hash changed")
    require(sha256(MODEL_VIEWER / "LICENSE") == EXPECTED_MODEL_VIEWER_LICENSE_SHA256, "model-viewer license hash changed")

    carpenter_pdf = CARPENTER / "Carpenter_Custom_630_17-4_PH.pdf"
    require(sha256(carpenter_pdf) == EXPECTED_CARPENTER_SHA256, "Carpenter source hash changed")
    source_md = (CARPENTER / "SOURCE.md").read_text(encoding="utf-8")
    for token in ("ASTM A564/A564M", "H1150", "typical", "2024-10-03", EXPECTED_CARPENTER_SHA256):
        require(token in source_md, f"source-control note missing {token}")

    features = rows("feature-register.csv")
    require(len(features) == 15, f"expected 15 features, found {len(features)}")
    require({row["part"] for row in features} == {"FX103-C01 P0.2", "FX103-C02 P0.1", "both"}, "part feature coverage changed")
    feature_text = "\n".join(" ".join(row.values()) for row in features)
    for token in ("Ø10 h6", "Ø10 H7", "Ø15.000 +0/-0.013", "M4 x 0.7 - 6H", "PCD Ø16", "PCD Ø28", "condition A finished parts prohibited"):
        require(token in feature_text, f"feature control missing {token}")

    analysis = {row["screen"]: row for row in rows("analysis-register.csv")}
    require(len(analysis) == 15, f"expected 15 analysis screens, found {len(analysis)}")
    numeric_expectations = {
        "R106-A01": 0.6,
        "R106-A02": 1.4,
        "R106-A03": 1.1,
        "R106-A04": 2.35,
        "R106-A05": 3.0,
        "R106-A06": 5.05,
    }
    for screen, expected in numeric_expectations.items():
        actual = float(analysis[screen]["result"].split()[0])
        require(abs(actual - expected) < 1e-6, f"{screen} arithmetic changed: {actual}")
    require("REJECTED" in analysis["R106-A01"]["authority"], "old one-piece rejection lost")
    require("0 N m positive torque-transfer credit" in analysis["R106-A15"]["result"], "pilot zero-torque-credit rule lost")
    require("TYPICAL" in analysis["R106-A14"]["authority"], "typical-property caveat lost")

    inspections = rows("inspection-plan.csv")
    require(len(inspections) == 14, f"expected 14 inspections, found {len(inspections)}")
    require(all(row["result"] == "NOT EXECUTED" for row in inspections), "inspection falsely executed")
    require(any(row["acceptance"] == "SELECTION REQUIRED" for row in inspections), "proof/alignment acceptance incorrectly frozen")

    rfis = rows("dfm-rfi.csv")
    require(len(rfis) == 7 and all(row["state"] == "NOT SENT" for row in rfis), "RFI state/count changed")
    holds = rows("open-hold-register.csv")
    require(sum(row["state"] == "PARTIAL" for row in holds) == 3, "partial hold count changed")
    require(sum(row["state"] == "OPEN" for row in holds) == 8, "open hold count changed")
    require(all("ENERGIZATION" in row["effect"] for row in holds), "a hold lost the energization block")

    material = rows("material-process-register.csv")
    require(len(material) == 6, "material/process control count changed")
    material_text = "\n".join(" ".join(row.values()) for row in material)
    for token in ("ASTM A564/A564M Type 630", "H1150", "Condition A prohibited", "SELECTION REQUIRED", "no welding"):
        require(token.lower() in material_text.lower(), f"material/process boundary missing {token}")

    sources = rows("source-register.csv")
    require(len(sources) == 6, "source count changed")
    carpenter = next(row for row in sources if row["organization"] == "Carpenter Technology")
    require(carpenter["sha256"] == EXPECTED_CARPENTER_SHA256, "source register Carpenter hash mismatch")
    require("2024-10-03" in carpenter["revision_date"], "Carpenter metadata date missing")
    require(any(row["organization"] == "ROBOTIS" and "live page" in row["revision_date"] for row in sources), "ROBOTIS live source missing")
    ruland = [row for row in sources if row["organization"] == "Ruland Manufacturing"]
    require(len(ruland) == 2, "exact Ruland hub and bundle sources are both required")
    require(any(row["locator"].endswith("/mjc33-15-a.html") for row in ruland), "exact MJC33-15-A hub source missing")
    require(any("/de/mjc33-15-a-jd21-33-92y.html" in row["locator"] for row in ruland), "exact two-clamp 92Y bundle source missing")

    parents = rows("parent-artifact-register.csv")
    require(len(parents) == 3, "parent register count changed")
    for row in parents:
        parent_path = ROOT / row["artifact"]
        require(parent_path.is_file(), f"parent artifact missing: {row['artifact']}")
        require(sha256(parent_path) == row["sha256"], f"parent artifact changed: {row['artifact']}")

    geometry = json.loads((OUT / "geometry-check.json").read_text(encoding="utf-8"))
    require(geometry["identifier"] == IDENTIFIER, "geometry identifier mismatch")
    require(geometry["old_one_piece_rejected"] is True, "old one-piece geometry not rejected")
    require(abs(geometry["old_one_piece_hole_stub_overlap_mm"] - 0.6) < 1e-9, "old overlap changed")
    require(geometry["nominal_intersections_mm3"]["c01_c02"] < 1e-6, "C01/C02 nominal solids intersect")
    require(geometry["nominal_intersections_mm3"]["c02_hub"] < 1e-6, "C02/hub nominal solids intersect")
    require(geometry["c01"]["volume_mm3"] > 0 and geometry["c02"]["volume_mm3"] > 0, "part volume invalid")
    require(geometry["c01"]["step_sha256"] == sha256(OUT / "FX103-C01_P0.2_horn_flange.step"), "C01 STEP hash mismatch")
    require(geometry["c02"]["step_sha256"] == sha256(OUT / "FX103-C02_P0.1_shaft_flange.step"), "C02 STEP hash mismatch")
    require(geometry["thread_geometry_in_step"] is False, "thread-model boundary changed")
    require(geometry["fabrication_release"] is False and geometry["capacity_credit"] is False, "geometry claims release/capacity")

    status = json.loads((OUT / "package-status.json").read_text(encoding="utf-8"))
    require(status["identifier"] == IDENTIFIER, "status identifier mismatch")
    require(status["old_one_piece_geometry_rejected"] is True, "status does not reject old geometry")
    require(status["two_piece_part_definition_complete_for_independent_review"] is True, "review definition missing")
    for field in ("supplier_contacted", "dfm_complete", "qualified_analysis_approved", "manufacturer_application_accepted", "exact_fasteners_selected", "fai_executed", "proof_executed", "assembled_alignment_verified"):
        require(status[field] is False, f"{field} falsely true")
    require(status["partial_hold_count"] == 3 and status["open_hold_count"] == 8, "status hold counts changed")
    require(status["rfi_count"] == 7 and status["rfi_state"] == "NOT SENT", "status RFI state changed")
    require(all(value is False for value in status["release_flags"].values()), "a release flag is true")
    require("NOT RELEASED" in status["warning"] and "ENERGIZATION" in status["warning"], "warning weakened")

    html = WEB.read_text(encoding="utf-8")
    svg = (OUT / "FX103_output_adapter_P0.2_drawing.svg").read_text(encoding="utf-8")
    for token in (IDENTIFIER, "0.60 mm", "two-piece", "not a machining", "Every release flag remains false"):
        require(token.lower() in html.lower(), f"interactive guide missing {token}")
    require('../../vendor/model-viewer/4.1.0/model-viewer.min.js' in html, "guide is not pinned to the local model-viewer runtime")
    require(".drawing-scroll" in html and "width:1200px" in html and "12-pixel annotation floor" in html, "drawing mobile legibility control missing")
    for token in ("font:17px", "font-size:16px", "font-size:14px"):
        require(token in html, f"interactive guide typography missing {token}")
    require("font-size:20px" in svg and "font-size:21px" in svg, "drawing functional text below controlled minimum")
    require("R103 ONE-PIECE FX103-C01 IS REJECTED" in svg, "drawing rejection note missing")
    require("FLANGE Ø40.00 ±0.05 × 8.00 ±0.03" in svg and "STUB LENGTH 20.00 ±0.05" in svg, "drawing envelope/thickness callouts missing")
    require("NOT RELEASED" in svg and "ENERGIZATION" in svg, "drawing warning weakened")

    print("HR-V0 FX103 output-adapter check passed: one-piece overlap rejected; 15 features; 15 screens; 14 unexecuted inspections; 7 unsent RFIs; 3 partial + 8 open holds; all release flags false")
    print("PRELIMINARY - NOT RELEASED FOR FABRICATION OR ENERGIZATION")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
