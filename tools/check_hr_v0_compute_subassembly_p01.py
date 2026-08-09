#!/usr/bin/env python3
"""Fail-closed checks for HR-V0-COMPUTE-SUBASM-P0.1."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT FABRICATION OR ENERGIZATION"
IMAGE_HASH = "acff736ca7945e3b305f07cda4abdb870910e12634991da69783611756e381b3"


def read_csv(relative: str) -> list[dict[str, str]]:
    with (ROOT / relative).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    failures: list[str] = []

    def require(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    sources = read_csv("electrical/vendor/raspberry-pi/compute-r120/source-manifest-p0.1.csv")
    stack = read_csv("bom/hr-v0-compute-subassembly-p0.1.csv")
    interfaces = read_csv("electrical/interfaces/hr-v0-compute-subassembly-p0.1.csv")
    receiving = read_csv("tests/forms/hr-v0-compute-subassembly-receiving-template-p0.1.csv")
    image_build = read_csv("tests/forms/hr-v0-compute-image-build-template-p0.1.csv")
    bom = {row["item_id"]: row for row in read_csv("bom/bom.csv")}
    closure = {row["item_id"]: row for row in read_csv("bom/hr-v0-bom-closure.csv")}
    gates = {row["gate_id"]: row for row in read_csv("requirements/hr-v0-energization-gates.csv")}
    image = json.loads((ROOT / "software/images/hr-v0-rpi-os-lite-p0.1.json").read_text(encoding="utf-8"))
    guide = (ROOT / "release/hr-v0/compute-subassembly-p0.1/index.html").read_text(encoding="utf-8")
    doc = (ROOT / "docs/hr-v0-compute-subassembly-p0.1.md").read_text(encoding="utf-8")
    metadata = json.loads((ROOT / "release/hr-v0/release-candidate.json").read_text(encoding="utf-8"))

    require(len(sources) == 10, "source manifest must contain ten primary Raspberry Pi records")
    require(len(stack) == 5, "stack register must contain five controlled lines")
    require(len(interfaces) == 18, "interface register must contain eighteen rows")
    require(len(receiving) == 24, "receiving template must contain twenty-four rows")
    require(len(image_build) == 18, "image build template must contain eighteen rows")
    require({row["reference"] for row in stack} == {"PI1", "PSU3", "COOL1", "STORE1", "IMAGE1"}, "stack reference set changed")
    require(next(row for row in stack if row["reference"] == "COOL1")["exact_candidate"].endswith("SC1148"), "SC1148 cooler identity missing")
    store = next(row for row in stack if row["reference"] == "STORE1")
    require(store["order_code_state"] == "SELECTION REQUIRED" and store["application_state"] == "OPEN", "storage must remain fail-closed")
    require(bom.get("BOM-079", {}).get("manufacturer_part_number") == "SC1148", "BOM-079 exact cooler identity missing")
    require("exact order code SELECTION REQUIRED" in bom.get("BOM-064", {}).get("manufacturer_part_number", ""), "BOM-064 improperly claims an exact card order code")
    require(closure.get("BOM-079", {}).get("closure_class") == "exact_candidate_hold" and closure.get("BOM-079", {}).get("allowed_action") == "HOLD", "BOM-079 is not an exact-candidate hold")
    require(closure.get("BOM-064", {}).get("closure_class") == "selection_required", "BOM-064 must remain selection required")
    require(image["official_sha256_published"] == IMAGE_HASH and image["release_date"] == "2026-06-18", "pinned OS identity changed")
    require(all(image[key] == "NOT_EXECUTED" for key in ("local_download_state", "local_sha256_state", "media_write_state", "readback_verification_state", "boot_validation_state", "power_loss_recovery_state")), "image record contains executed evidence")
    require(all(row["authorization"] == "NOT_AUTHORIZED" and row["state"] == "NOT_EXECUTED" and not row["actual"] and not row["evidence_hash"] for row in receiving), "receiving template contains an executed or authorized result")
    require(all(row["authorization"] == "NOT_AUTHORIZED" and row["state"] == "NOT_EXECUTED" and not row["actual_result"] and not row["evidence_hash"] for row in image_build), "image template contains an executed or authorized result")
    require(sum(row["state"] == "EXACT_CANDIDATE" for row in interfaces) == 3, "exact interface candidate count changed")
    require(sum(row["state"] == "OPEN" for row in interfaces) == 10, "open interface count changed")
    require(sum(row["state"] == "PARTIAL" for row in interfaces) == 4, "partial interface count changed")
    require(sum(row["state"] == "PINNED_NOT_EXECUTED" for row in interfaces) == 1, "pinned image interface missing")
    require(all(row["warning"] == WARNING for row in sources + stack + interfaces + receiving), "controlled CSV warning missing or changed")
    require(all("NOT APPROVED" in row["warning"] for row in image_build), "image-build warning missing")
    for gate_id in ("EG-003", "EG-010", "EG-017"):
        require(gates.get(gate_id, {}).get("status") == "partial", f"{gate_id} must remain partial")
        require("compute-subassembly-p0.1" in gates[gate_id]["evidence_location"], f"{gate_id} evidence is not synchronized")
    electrical = next((item for item in metadata.get("current_products", []) if item.get("domain") == "electrical"), {})
    require("HR-V0-COMPUTE-SUBASM-P0.1" in electrical.get("supporting_identifiers", []), "release metadata lacks compute-subassembly identifier")
    combined = doc + guide + json.dumps(image) + "\n".join(str(value) for row in sources + stack + interfaces + receiving + image_build for value in row.values())
    for token in ("SC1112", "SC1158", "SC1148", IMAGE_HASH, "SELECTION REQUIRED", "NOT_EXECUTED", "NOT_AUTHORIZED", "zero functional-safety credit", "Sol R12"):
        require(token.lower() in combined.lower(), f"required token missing: {token}")
    require("font:16px" in guide and "font-size:14px" in guide and "font-size:12px" in guide, "guide text floors are not explicit")
    require("R120" in guide and "HR-V0-COMPUTE-SUBASM-P0.1" in guide, "guide configuration identity missing")

    if failures:
        raise SystemExit("HR-V0 compute-subassembly check failed:\n- " + "\n- ".join(failures))
    print("HR-V0 compute-subassembly check passed: three exact hardware candidates, one selection-required storage branch and one pinned/unexecuted OS image")
    print("EG-003, EG-010 and EG-017 remain PARTIAL; no procurement, connection, powered-test or energization authority")
    print(WARNING)


if __name__ == "__main__":
    main()
