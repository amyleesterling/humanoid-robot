from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "cad" / "hr-v0" / "generated" / "fr12-moving-mass-metrology-p0.1"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def close(a: float, b: float, tol: float = 1e-9) -> bool:
    return abs(a - b) <= tol


def main() -> None:
    errors: list[str] = []
    required = [
        OUT / "frame-geometry-audit.json", OUT / "commerce-weight-conflict.csv",
        OUT / "evaluation-article-allocation.csv", OUT / "received-measurement-plan.csv",
        OUT / "mass-radius-bound-sensitivity.csv", OUT / "source-register.csv",
        OUT / "package-status.json",
        ROOT / "tests" / "forms" / "hr-v0-fr12-moving-subassembly-measurement-template.csv",
        ROOT / "tests" / "forms" / "hr-v0-fr12-mass-repeat-template.csv",
        ROOT / "release" / "hr-v0" / "fr12-moving-mass-metrology-p0.1" / "index.html",
        ROOT / "docs" / "hr-v0-fr12-moving-mass-metrology-p0.1.md",
        ROOT / "docs" / "reviews" / "2026-08-08-r97-validation-record.md",
        ROOT / "docs" / "reviews" / "2026-08-08-fr12-moving-mass-metrology-p0.1-independent-review-request.md",
        ROOT / "docs" / "reviews" / "2026-08-08-sol-r12-post-r97-status.md",
    ]
    errors.extend(f"missing {path.relative_to(ROOT)}" for path in required if not path.exists())
    if errors:
        raise SystemExit("\n".join(errors))

    geometry = json.loads((OUT / "frame-geometry-audit.json").read_text(encoding="utf-8"))
    if geometry.get("identifier") != "HR-V0-FR12-MASS-MET-P0.1":
        errors.append("geometry identifier changed")
    if geometry.get("source_sha256") != sha256(ROOT / geometry["source_step"]):
        errors.append("FR12 STEP hash mismatch")
    if not close(float(geometry["volume_mm3"]), 2854.117032171, 1e-6):
        errors.append("FR12 frame volume changed")
    if not close(float(geometry["conservative_bbox_corner_radius_about_j2_x_mm"]), math.hypot(28.0, 12.0), 1e-6):
        errors.append("FR12 bounding radius changed")
    if "FRAME GEOMETRY ONLY" not in geometry.get("boundary", ""):
        errors.append("frame-only evidence boundary missing")

    conflict = rows(OUT / "commerce-weight-conflict.csv")
    if len(conflict) != 2 or {item["commerce_weight_field"] for item in conflict} != {"0.10 lb", "0.20 lb"}:
        errors.append("commerce-weight conflict changed")
    if any(item["disposition"] != "REJECT FOR MASS CREDIT" for item in conflict):
        errors.append("storefront mass credit was introduced")

    plan = rows(OUT / "received-measurement-plan.csv")
    if len(plan) != 12 or sum(item["state"] == "OPEN" for item in plan) != 2 or any(item["state"] not in {"OPEN", "NOT EXECUTED"} for item in plan):
        errors.append("measurement plan state/count changed")
    allocation = rows(OUT / "evaluation-article-allocation.csv")
    if len(allocation) != 3 or any("APPROVAL REQUIRED" not in item["state"] and item["state"] != "NOT ALLOCATED" for item in allocation):
        errors.append("evaluation article allocation was promoted")

    form = rows(ROOT / "tests" / "forms" / "hr-v0-fr12-moving-subassembly-measurement-template.csv")
    repeats = rows(ROOT / "tests" / "forms" / "hr-v0-fr12-mass-repeat-template.csv")
    if len(form) != 3 or any(item["execution_state"] != "NOT EXECUTED" or item["mean_mass_g"] for item in form):
        errors.append("result template contains executed or numeric mass evidence")
    if len(repeats) != 30 or any(item["execution_state"] != "NOT EXECUTED" or item["balance_reading_g"] for item in repeats):
        errors.append("raw repeat template contains executed evidence")

    sensitivities = rows(OUT / "mass-radius-bound-sensitivity.csv")
    if len(sensitivities) != 25:
        errors.append("mass/radius sensitivity count changed")
    else:
        for item in sensitivities:
            m = float(item["mass_upper_g"]) / 1000.0
            r = float(item["radius_upper_mm"]) / 1000.0
            if not close(float(item["ixx_upper_bound_kg_m2"]), m * r * r, 1e-12):
                errors.append("inertia-bound arithmetic mismatch")
                break
            if not close(float(item["gravity_upper_bound_nm"]), m * 9.80665 * r, 1e-9):
                errors.append("gravity-bound arithmetic mismatch")
                break

    sources = rows(OUT / "source-register.csv")
    if len(sources) != 6:
        errors.append("source register count changed")
    for item in sources:
        if item["sha256"] not in {"LIVE PRIMARY PAGE - NO LOCAL SNAPSHOT", "LIVE PRIMARY PAGE - LOCAL FILES HASHED SEPARATELY"}:
            path = ROOT / item["locator"]
            if not path.exists() or sha256(path) != item["sha256"]:
                errors.append(f"source hash mismatch: {item['source_id']}")

    status = json.loads((OUT / "package-status.json").read_text(encoding="utf-8"))
    false_keys = ["commerce_weight_credit", "received_article_exists", "measurement_executed", "load_open_01_closed", "mass_closed", "com_closed", "inertia_closed", "x430_selected", "p1_1_selected", "fabrication_released", "motion_released", "connection_released", "energization_released"]
    if any(status.get(key) is not False for key in false_keys) or status.get("open_holds") != ["FR12-HOLD-01", "FR12-HOLD-02"]:
        errors.append("fail-closed package state changed")

    guide = (ROOT / "release" / "hr-v0" / "fr12-moving-mass-metrology-p0.1" / "index.html").read_text(encoding="utf-8")
    for phrase in ("NO MASS CREDIT", "LOAD-OPEN-01 remains OPEN", "NOT APPROVED FOR PURCHASE", "font-size:13px", "th,td{font-size:16px"):
        if phrase not in guide:
            errors.append(f"guide boundary/style missing: {phrase}")
    for path in required[-4:-1]:
        text = path.read_text(encoding="utf-8")
        if "NOT APPROVED" not in text and "No purchase" not in text:
            errors.append(f"preliminary boundary missing in {path.relative_to(ROOT)}")

    if errors:
        raise SystemExit("HR-V0 FR12 mass-metrology check FAILED:\n- " + "\n- ".join(errors))
    print("HR-V0 FR12 moving-mass metrology check: PASS")
    print("Official 0.10/0.20 lb commerce fields rejected; zero mass credit")
    print(f"Frame STEP {geometry['volume_mm3']:.6f} mm3; conservative frame-only radius {geometry['conservative_bbox_corner_radius_about_j2_x_mm']:.6f} mm")
    print("12-step unpowered route; 3 result rows and 30 repeat rows remain NOT EXECUTED; LOAD-OPEN-01 OPEN")


if __name__ == "__main__":
    main()
