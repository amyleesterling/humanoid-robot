"""Validate the R107 FX103 output-adapter P0.3 correction candidate."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "cad" / "hr-v0" / "generated" / "fx103-output-adapter-p0.3"
WEB = ROOT / "release" / "hr-v0" / "fx103-output-adapter-p0.3" / "index.html"
MISUMI = ROOT / "cad" / "vendor" / "misumi" / "fasteners-r107"
IDENTIFIER = "HR-V0-FX103-OUTPUT-ADAPTER-FAB-P0.3"
EXPECTED_MISUMI_SHA256 = "B4EFA4D078609D61762BBA80B8E560767141B9E52BE4B5FEBD8337CA8C974102"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    expected = {
        "FX103-C01_P0.3_horn_flange.step",
        "FX103-C02_P0.1_shaft_flange.step",
        "FX103_output_adapter_P0.3_drawing.svg",
        "FX103_output_adapter_P0.3_review.glb",
        "FX103_output_adapter_P0.3_review.step",
        "analysis-register.csv",
        "assembly-sequence.csv",
        "dfm-rfi.csv",
        "fastener-candidate-register.csv",
        "feature-register.csv",
        "geometry-check.json",
        "inspection-plan.csv",
        "material-process-register.csv",
        "open-hold-register.csv",
        "package-status.json",
        "parent-artifact-register.csv",
        "source-register.csv",
    }
    require({path.name for path in OUT.iterdir() if path.is_file()} == expected, "P0.3 artifact set changed")
    for name in ("FX103-C01_P0.3_horn_flange.step", "FX103-C02_P0.1_shaft_flange.step", "FX103_output_adapter_P0.3_review.step"):
        text = (OUT / name).read_text(encoding="utf-8", errors="strict")
        require(text.startswith("ISO-10303-21;"), f"{name} is not a STEP exchange file")
        require("END-ISO-10303-21;" in text[-128:], f"{name} STEP trailer missing")
    require((OUT / "FX103_output_adapter_P0.3_review.glb").read_bytes()[:4] == b"glTF", "review GLB header invalid")

    pdf = MISUMI / "MISUMI_CB_socket_head_cap_screws.pdf"
    require(sha256(pdf) == EXPECTED_MISUMI_SHA256, "controlled MISUMI PDF hash changed")
    source_note = (MISUMI / "SOURCE.md").read_text(encoding="utf-8")
    for token in (EXPECTED_MISUMI_SHA256, "2015-11-05", "CB4-15", "SCB2-8"):
        require(token in source_note, f"MISUMI source-control note missing {token}")
    require("current orderability" in source_note.lower(), "MISUMI orderability caveat missing")

    geometry = json.loads((OUT / "geometry-check.json").read_text(encoding="utf-8"))
    require(geometry["identifier"] == IDENTIFIER, "identifier mismatch")
    require(geometry["supersession"]["rejected"].startswith("FX103-C01 P0.2 fastener stack"), "P0.2 reach defect not rejected")
    require(abs(geometry["p02_supplied_m2_shortfall_mm"] - 2.8) < 1e-9, "P0.2 M2 shortfall changed")
    require(abs(geometry["c01"]["counterbore_depth_mm"] - 3.0) < 1e-9, "corrected counterbore depth changed")
    require(geometry["fastener_candidates"] == {"horn":"SCB2-8", "transfer":"CB4-15", "selected_for_release":False}, "fastener candidate state changed")
    require(geometry["nominal_engagement_mm"] == {"horn":3.0, "transfer":7.0}, "nominal fastener engagement changed")
    require(geometry["nominal_intersections_mm3"] == {"c01_c02":0.0, "c02_hub":0.0}, "nominal solid intersection changed")
    require(geometry["fabrication_release"] is False and geometry["capacity_credit"] is False, "geometry falsely releases work or capacity")

    features = rows("feature-register.csv")
    require(len(features) == 15, "feature count changed")
    c01f04 = next(row for row in features if row["feature"] == "C01-F04")
    require("3.00 ±0.05" in c01f04["nominal"] and "SCB2-8 HELD" in c01f04["state"], "corrected M2 feature control missing")
    c01f05 = next(row for row in features if row["feature"] == "C01-F05")
    require("CB4-15 HELD" in c01f05["state"], "M4 candidate feature state missing")

    analysis = {row["screen"]: row for row in rows("analysis-register.csv")}
    require(len(analysis) == 19, "analysis-screen count changed")
    expected_results = {"R107-A16":"2.800000", "R107-A17":"3.000000", "R107-A18":"7.000000", "R107-A19":"1.050000"}
    for screen, token in expected_results.items():
        require(token in analysis[screen]["result"], f"{screen} result changed")
    require("REJECTED" in analysis["R107-A16"]["authority"], "P0.2 stack not fail-closed")
    require("PHYSICAL PROOF OPEN" in analysis["R107-A19"]["authority"], "hub/service screen overclaims closure")

    fasteners = rows("fastener-candidate-register.csv")
    require([row["candidate"] for row in fasteners] == ["SCB2-8", "CB4-15"], "fastener candidate identities changed")
    require(all(row["state"] == "EXACT CANDIDATE HOLD" for row in fasteners), "fastener candidate falsely released")
    require(all(row["open"] for row in fasteners), "fastener open evidence missing")

    sequence = rows("assembly-sequence.csv")
    require(len(sequence) == 6 and all("NOT EXECUTED" in row["authority"] for row in sequence), "assembly sequence state/count changed")
    require("remove hub" in sequence[-1]["operation"].lower(), "M4 service sequence lost")

    inspections = rows("inspection-plan.csv")
    require(len(inspections) == 17 and all(row["result"] == "NOT EXECUTED" for row in inspections), "inspection state/count changed")
    require({"FAI-15", "FAI-16", "FAI-17"}.issubset({row["record"] for row in inspections}), "fastener/stack inspections missing")

    sources = rows("source-register.csv")
    require(len(sources) == 8, "source count changed")
    misumi_sources = [row for row in sources if row["organization"] == "MISUMI USA"]
    require(len(misumi_sources) == 2, "both MISUMI source records required")
    require(any("HissuCode=SCB2-8" in row["locator"] for row in misumi_sources), "exact SCB2-8 live source missing")
    require(any(row["sha256"] == EXPECTED_MISUMI_SHA256 for row in misumi_sources), "controlled CB catalog hash missing")

    parents = rows("parent-artifact-register.csv")
    require(len(parents) == 5, "parent register count changed")
    for row in parents:
        path = ROOT / row["artifact"]
        require(path.is_file() and sha256(path) == row["sha256"], f"parent artifact mismatch: {row['artifact']}")

    holds = rows("open-hold-register.csv")
    require(sum(row["state"] == "PARTIAL" for row in holds) == 4, "partial hold count changed")
    require(sum(row["state"] == "OPEN" for row in holds) == 7, "open hold count changed")
    require(next(row for row in holds if row["hold_id"] == "OA-HOLD-05")["state"] == "PARTIAL", "fastener hold must remain partial")
    rfis = rows("dfm-rfi.csv")
    require(len(rfis) == 7 and all(row["state"] == "NOT SENT" for row in rfis), "RFI state/count changed")

    status = json.loads((OUT / "package-status.json").read_text(encoding="utf-8"))
    require(status["identifier"] == IDENTIFIER, "status identifier mismatch")
    require(status["p02_fastener_stack_rejected"] is True and status["exact_fastener_candidates_identified"] is True, "correction state missing")
    require(status["exact_fasteners_selected"] is False, "fasteners falsely selected for release")
    require(status["partial_hold_count"] == 4 and status["open_hold_count"] == 7, "status hold counts changed")
    require(all(value is False for value in status["release_flags"].values()), "release flag enabled")

    drawing = (OUT / "FX103_output_adapter_P0.3_drawing.svg").read_text(encoding="utf-8")
    for token in (IDENTIFIER, "↧3.00 ±0.05", "SCB2-8", "CB4-15", "Hub removal is required", "NOT RELEASED"):
        require(token in drawing, f"drawing missing {token}")
    html = WEB.read_text(encoding="utf-8")
    for token in (IDENTIFIER, "supplied M2x3 screws stopped 2.80 mm", "3.00 mm", "7.00 mm", "SCB2-8", "CB4-15", "../../vendor/model-viewer/4.1.0/model-viewer.min.js", "NOT RELEASED"):
        require(token in html, f"guide missing {token}")
    require("fx103-output-adapter-p0.3" in html and "FX103_output_adapter_P0.3_review.glb" in html, "guide path not synchronized")
    require("hr-v0-fx103-output-adapter-fabrication-candidate-p0.3.md" in html, "guide design-record link not synchronized")

    print("HR-V0 FX103 P0.3 check passed: P0.2 M2 reach defect rejected; SCB2-8/CB4-15 held; 19 screens; 17 unexecuted inspections; 4 partial + 7 open holds; all release flags false")
    print("PRELIMINARY - NOT RELEASED FOR FABRICATION OR ENERGIZATION")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
