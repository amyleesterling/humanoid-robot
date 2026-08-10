from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "test-fixtures" / "hr-v0" / "x430-output-interface-p0.1"
WEB = ROOT / "release" / "hr-v0" / "x430-output-interface-p0.1"
HN12 = ROOT / "cad" / "vendor" / "robotis" / "hn12-n101-r103"


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> None:
    errors: list[str] = []
    required = [
        "FX103-C01_HN12_to_15mm_stub_review.step",
        "HR-V0_X430_output_interface_P0.1_review.step",
        "HR-V0_X430_output_interface_P0.1_review.glb",
        "output-interface-layout.svg", "topology-trade.csv", "candidate-bom.csv",
        "adapter-feature-register.csv", "calculation-screen.csv",
        "interface-tolerance-register.csv", "collision-register.csv", "vendor-rfi.csv",
        "open-hold-register.csv", "received-inspection-template.csv", "source-register.csv",
        "geometry-check.json", "package-status.json",
    ]
    errors.extend(f"missing {name}" for name in required if not (OUT / name).exists())
    if not (WEB / "index.html").exists():
        errors.append("missing interactive guide")
    if errors:
        raise SystemExit("\n".join(errors))

    expected_sources = {
        "HN12-N101-official.step": "6DE6851B85132EC496F24A177729ECA5CE43416707652E79183BFA51E7F978FD",
        "HN12-N101-official.pdf": "0D6C309F8A45D81FFAABDB45982B7DE0B6E7F74742CAE850CFF4E938B86A81FA",
    }
    for name, expected in expected_sources.items():
        if not (HN12 / name).exists() or sha256(HN12 / name) != expected:
            errors.append(f"controlled ROBOTIS source changed: {name}")

    trade = rows("topology-trade.csv")
    if len(trade) != 4 or trade[0]["disposition"] != "PREFERRED INQUIRY - NOT SELECTED":
        errors.append("preferred topology changed")
    if trade[2]["disposition"] != "REJECTED FROM CURRENT BASELINE" or trade[3]["disposition"] != "PROHIBITED FOR POWERED CHARACTERIZATION":
        errors.append("unsafe topology disposition changed")
    bom = rows("candidate-bom.csv")
    if len(bom) != 6 or bom[3]["quantity"] != "2" or "MJC33-15-A" not in bom[3]["order_identity"]:
        errors.append("two-clamp-hub BOM changed")
    features = rows("adapter-feature-register.csv")
    if len(features) != 8 or "8 x Ø2.2" not in features[1]["definition"] or "PCD Ø16" not in features[1]["definition"]:
        errors.append("adapter hole-pattern boundary changed")
    if "NOT TOLERANCED OR RELEASED" not in {r["state"] for r in features}:
        errors.append("adapter release boundary missing")
    calculations = rows("calculation-screen.csv")
    expected = [50.0, 64.0625, 123.4375, 16 * 3.2e3 / (math.pi * 15**3), 16 * 4.1e3 / (math.pi * 15**3), 16 * 7.9e3 / (math.pi * 15**3), 14.95]
    actual = [float(r["result"].split()[0]) for r in calculations]
    if len(actual) != 7 or any(not math.isclose(a, b, abs_tol=1e-6) for a, b in zip(actual, expected)):
        errors.append("bounded interface arithmetic changed")
    interfaces = rows("interface-tolerance-register.csv")
    if len(interfaces) != 5 or sum(r["state"] == "PARTIAL" for r in interfaces) != 1 or sum(r["state"] == "OPEN" for r in interfaces) != 4:
        errors.append("interface state changed")
    collisions = rows("collision-register.csv")
    if len(collisions) != 4 or any(r["nominal_intersection_mm3"] != "0.000000" for r in collisions[:3]):
        errors.append("nominal collision record changed")
    rfi = rows("vendor-rfi.csv")
    if len(rfi) != 8 or any(r["state"] != "NOT SENT" for r in rfi):
        errors.append("RFI state changed")
    holds = rows("open-hold-register.csv")
    if len(holds) != 12 or sum(r["state"] == "PARTIAL" for r in holds) != 1 or sum(r["state"] == "OPEN" for r in holds) != 11:
        errors.append("hold state changed")
    received = rows("received-inspection-template.csv")
    if len(received) != 6 or any(r["result"] != "NOT EXECUTED" for r in received):
        errors.append("received inspection was asserted")
    sources = rows("source-register.csv")
    if len(sources) != 5 or sources[0]["local_sha256"] != expected_sources["HN12-N101-official.step"] or sources[1]["local_sha256"] != expected_sources["HN12-N101-official.pdf"]:
        errors.append("source register changed")

    geometry = json.loads((OUT / "geometry-check.json").read_text(encoding="utf-8"))
    if geometry.get("candidate_hole_count") != 8 or geometry.get("candidate_hole_diameter_mm") != 2.2 or geometry.get("candidate_pcd_mm") != 16.0:
        errors.append("geometry definition changed")
    if not math.isclose(geometry.get("stub_penetration_mm", 0), 14.95, abs_tol=1e-9):
        errors.append("stub penetration changed")
    if any(abs(v) > 1e-7 for v in geometry.get("nominal_intersections_mm3", {}).values()):
        errors.append("nominal B-Rep collision detected")
    if geometry.get("tolerance_credit") is not False or geometry.get("capacity_credit") is not False:
        errors.append("geometry incorrectly promoted to capacity evidence")

    status = json.loads((OUT / "package-status.json").read_text(encoding="utf-8"))
    if status.get("identifier") != "HR-V0-X430-OUTPUT-IF-P0.1" or status.get("preferred_route") != "OUT-A":
        errors.append("package identity changed")
    if status.get("exact_hn12_geometry_present") is not True or status.get("adapter_review_geometry_present") is not True:
        errors.append("geometry evidence missing")
    for field in ("adapter_fabrication_release_present", "fastener_selection_complete", "material_selection_complete", "manufacturer_application_acceptance"):
        if status.get(field) is not False:
            errors.append(f"fail-closed field promoted: {field}")
    if status.get("open_hold_count") != 11 or status.get("partial_hold_count") != 1 or status.get("rfi_count") != 8 or status.get("rfi_state") != "NOT SENT":
        errors.append("package hold/RFI state changed")
    if status.get("configured_h101_test_still_required") is not True:
        errors.append("configured H101 test boundary changed")
    if any(value is not False for value in status.get("release_flags", {}).values()):
        errors.append("release flag promoted")

    guide = (WEB / "index.html").read_text(encoding="utf-8")
    for phrase in ("The anonymous shaft is gone", "Preferred inquiry, not selected", "One partial geometry hold and eleven open holds", "font-size:14px", "font-size:16px", "No supplier was contacted"):
        if phrase not in guide:
            errors.append(f"guide boundary/readability missing: {phrase}")
    drawing = (OUT / "output-interface-layout.svg").read_text(encoding="utf-8")
    for phrase in ("max-width:100%;height:auto", "DO NOT MACHINE, ASSEMBLE OR POWER FROM THIS DRAWING", "No fastener, material, tolerance, fatigue"):
        if phrase not in drawing:
            errors.append(f"layout boundary missing: {phrase}")
    if errors:
        raise SystemExit("HR-V0 X430 output-interface check FAILED:\n- " + "\n- ".join(errors))
    print("HR-V0 X430 output-interface check: PASS")
    print("exact HN12 source hashes; 4 routes; 6 BOM rows; 7 screens; 8 unsent RFIs")
    print("1 partial + 11 open holds; configured H101 test required; all release flags false")


if __name__ == "__main__":
    main()
