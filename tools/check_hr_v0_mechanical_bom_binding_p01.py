#!/usr/bin/env python3
"""Fail-closed validation for HR-V0-MECH-BOM-BIND-P0.1."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release" / "hr-v0" / "mechanical-bom-binding-p0.1"
BINDING = ROOT / "bom" / "hr-v0-mechanical-custom-part-binding.csv"
WARNING = "PRELIMINARY - NOT APPROVED FOR QUOTATION, FABRICATION, ASSEMBLY, MOTION, OR ENERGIZATION"
PART_IDS = ["MV0-C01", "MV0-C04", "MV0-C05", "MV0-C06", "MV0-C07"]


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    errors: list[str] = []
    successor_exists = (ROOT / "release" / "hr-v0" / "mechanical-bom-binding-p0.2" / "package-status.json").is_file()
    binding = rows(BINDING)
    bom = {row["item_id"]: row for row in rows(ROOT / "bom" / "bom.csv")}
    closure = {row["item_id"]: row for row in rows(ROOT / "bom" / "hr-v0-bom-closure.csv")}
    dfm_geometry = rows(ROOT / "release" / "hr-v0" / "mechanical-dfm-data-p0.1" / "geometry-file-register.csv")
    dfm_holds = rows(ROOT / "release" / "hr-v0" / "mechanical-dfm-data-p0.1" / "hold-register.csv")
    status = json.loads((OUT / "package-status.json").read_text(encoding="utf-8"))
    guide = (OUT / "index.html").read_text(encoding="utf-8")
    release = json.loads((ROOT / "release" / "hr-v0" / "release-candidate.json").read_text(encoding="utf-8"))
    gates = {row["gate_id"]: row for row in rows(ROOT / "requirements" / "hr-v0-energization-gates.csv")}

    if [row.get("part_id") for row in binding] != PART_IDS:
        errors.append("binding is not exactly C01/C04/C05/C06/C07 in controlled order")
    if any(row.get("quantity_candidate") != "1" for row in binding) or sum(int(row.get("quantity_candidate", "0")) for row in binding) != 5:
        errors.append("candidate quantity is not exactly one of each / five total")
    geometry_by_part: dict[str, dict[str, dict[str, str]]] = {part: {} for part in PART_IDS}
    for row in dfm_geometry:
        geometry_by_part.setdefault(row["part_id"], {})[row["artifact_role"]] = row
    role_columns = {
        "3D candidate": ("step_path", "step_sha256"),
        "profile reference": ("dxf_path", "dxf_sha256"),
        "readable control drawing": ("drawing_path", "drawing_sha256"),
    }
    for row in binding:
        part = row["part_id"]
        if row.get("bom_item_id") != "BOM-027" or row.get("architecture_id") != "HR-V0-ARM-ARCH-P0.7":
            errors.append(f"{part}: incorrect BOM or architecture binding")
        if row.get("quotation_authorized") != "FALSE" or row.get("fabrication_authorized") != "FALSE" or row.get("warning") != WARNING:
            errors.append(f"{part}: external-action boundary weakened")
        for role, (path_field, hash_field) in role_columns.items():
            expected = geometry_by_part.get(part, {}).get(role, {})
            if row.get(path_field) != expected.get("repository_path") or row.get(hash_field) != expected.get("sha256"):
                errors.append(f"{part}: {role} differs from controlled DFM identity")
                continue
            path = ROOT / row[path_field]
            if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != row[hash_field]:
                errors.append(f"{part}: {role} repository file/hash mismatch")

    item = bom.get("BOM-027", {})
    expected_mpn = "HR-V0-ARM-ARCH-P0.7 held custom set: MV0-C01 x1; MV0-C04 x1; MV0-C05 x1; MV0-C06 x1; MV0-C07 x1; 6061-T651 9.525 mm nominal candidate"
    if not successor_exists and (item.get("manufacturer") != "Custom CNC / provider SELECTION REQUIRED" or item.get("manufacturer_part_number") != expected_mpn or item.get("quantity") != "5" or item.get("baseline_status") != "exact_candidate_hold"):
        errors.append("BOM-027 does not carry the exact held P0.7 five-part identity")
    closed = closure.get("BOM-027", {})
    if not successor_exists and (closed.get("closure_class") != "exact_candidate_hold" or closed.get("order_code_state") != "EXACT CANDIDATE" or closed.get("allowed_action") != "HOLD"):
        errors.append("BOM-027 closure state is not exact-candidate hold")
    if len(dfm_holds) != 15 or any(row.get("status") != "OPEN" for row in dfm_holds):
        errors.append("the fifteen inherited DFM holds are not all open")
    for key in ("provider_contacted", "upload_authorized", "quotation_authorized", "purchase_authorized", "fabrication_authorized", "assembly_authorized", "motion_authorized", "energization_authorized"):
        if status.get(key) is not False:
            errors.append(f"package status {key} is not false")
    for key, expected in (("identifier", "HR-V0-MECH-BOM-BIND-P0.1"), ("part_count", 5), ("total_candidate_quantity", 5), ("geometry_identity_count", 15), ("inherited_open_hold_count", 15)):
        if status.get(key) != expected:
            errors.append(f"package status {key} != {expected!r}")
    source_hashes = status.get("source_hashes", {})
    if len(source_hashes) != 5:
        errors.append("package status does not bind exactly five source/register files")
    historical_mutable = {"bom/bom.csv", "bom/hr-v0-bom-closure.csv"}
    for relative, expected_hash in source_hashes.items():
        path = ROOT / relative
        if not path.is_file() or (hashlib.sha256(path.read_bytes()).hexdigest() != expected_hash and not (successor_exists and relative in historical_mutable)):
            errors.append(f"package source hash mismatch: {relative}")
    products = release.get("current_products", [])
    mechanical = next((x for x in products if x.get("domain") == "mechanical"), {})
    bom_product = next((x for x in products if x.get("domain") == "bill_of_materials"), {})
    for product, label in ((mechanical, "mechanical"), (bom_product, "BOM")):
        expected_support = "HR-V0-MECH-BOM-BIND-P0.2" if successor_exists else "HR-V0-MECH-BOM-BIND-P0.1"
        if expected_support not in product.get("supporting_identifiers", []):
            errors.append(f"release candidate {label} domain omits the binding")
    eg003 = gates.get("EG-003", {})
    if eg003.get("status") != "partial" or "bom/hr-v0-mechanical-custom-part-binding.csv" not in eg003.get("evidence_location", ""):
        errors.append("EG-003 does not retain partial status with binding evidence")
    for token in ("font:clamp(16px", "Five BOM parts", "fifteen inherited DFM holds remain open", "provider contact", "Upload authorized"):
        if token not in guide:
            errors.append(f"interactive guide omits {token!r}")

    if errors:
        print("HR-V0 mechanical BOM binding P0.1 check FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    suffix = " (historical; P0.2 successor current)" if successor_exists else ""
    print("HR-V0-MECH-BOM-BIND-P0.1 PASS" + suffix + ": BOM-027 binds one each C01/C04/C05/C06/C07 to 15 exact geometry identities")
    print("BOM-027 exact-candidate hold; 15 inherited DFM holds open; no provider contact, quote, upload, fabrication or energization authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
