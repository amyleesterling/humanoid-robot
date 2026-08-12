#!/usr/bin/env python3
"""Fail-closed checks for R260 observation mounting-stack correction."""
from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path

import generate_hr_v0_observation_mount_stack_p01 as gen


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    errors: list[str] = []
    def need(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    expected_files = {
        "README.md","package-status.json","index.html","source-register.csv",
        "hardware-candidate-register.csv","stack-calculation.csv","hole-coordinate-register.csv",
        "unresolved-selections.csv","fit-and-acceptance-form.csv","acceptance-matrix.csv","file-manifest.csv",
    }
    for directory in (gen.ENG, gen.REL):
        need({p.name for p in directory.iterdir() if p.is_file()} == expected_files, f"package membership mismatch: {directory}")
        for row in rows(directory / "file-manifest.csv"):
            path = directory / row["path"]
            need(path.is_file() and row["sha256"] == sha(path) and row["bytes"] == str(path.stat().st_size), f"manifest mismatch: {path}")
    for directory in (gen.CFG, gen.CFGR):
        for row in rows(directory / "file-manifest.csv"):
            path = directory / row["path"]
            need(path.is_file() and row["sha256"] == sha(path) and row["bytes"] == str(path.stat().st_size), f"config manifest mismatch: {path}")

    hardware = rows(gen.ENG / "hardware-candidate-register.csv")
    need(len(hardware) == 4 and sum(int(row["quantity"]) for row in hardware) == 24, "hardware quantities changed")
    for token in ("TNM3-6.5-10-1","0120070000VR","300251659935","50M025045P006"):
        need(any(token in row["manufacturer_part_number"] for row in hardware), f"hardware candidate missing: {token}")
    need(all("NOT RELEASED" in row["state"] for row in hardware), "hardware improperly released")

    stack = {row["screen_id"]: row for row in rows(gen.ENG / "stack-calculation.csv")}
    expected = {"STK-OBS-01":"4.4","STK-OBS-02":"3.46","STK-OBS-03":"1.25","STK-OBS-04":"4.4","STK-OBS-05":"0.5","STK-OBS-06":"0.13"}
    need(len(stack) == 6, "stack-screen count changed")
    for key, value in expected.items():
        need(float(stack.get(key, {}).get("result_mm", "nan")) == float(value), f"stack result changed: {key}")
    need("MISMATCH" in stack["STK-OBS-06"]["acceptance"], "Pi stack mismatch hidden")

    holes = rows(gen.ENG / "hole-coordinate-register.csv")
    need(len(holes) == 8 and all("DO NOT DRILL" in row["state"] or "NO ASSEMBLY" in row["state"] for row in holes), "mounting geometry promoted")
    need({(row["candidate_panel_x_mm"],row["candidate_panel_y_mm"]) for row in holes if row["assembly"] == "runtime"} == {("437.5","304.5"),("437.5","415.5"),("518.5","304.5"),("518.5","415.5")}, "runtime panel centers changed")

    sources = rows(gen.ENG / "source-register.csv")
    need(len(sources) == 8 and all(row["revision_or_date"] and row["url"].startswith("https://") for row in sources), "primary source register incomplete")
    for domain in ("raspberrypi.com","samtec.com","essentracomponents.com"):
        need(any(domain in row["url"] for row in sources), f"primary manufacturer source missing: {domain}")

    holds = rows(gen.ENG / "unresolved-selections.csv")
    fit = rows(gen.ENG / "fit-and-acceptance-form.csv")
    acceptance = rows(gen.ENG / "acceptance-matrix.csv")
    need(len(holds) == 9, "open-hold count changed")
    need(len(fit) == 10 and all(row["execution_state"] == "NOT EXECUTED" and row["result"] == "OPEN" and not row["operator"] and not row["reviewer"] for row in fit), "fit evidence falsely completed")
    need(len(acceptance) == 12 and all(row["execution_state"] == "NOT EXECUTED" and row["result"] == "OPEN" and not row["approver"] for row in acceptance), "acceptance falsely completed")

    bom = {row["item_id"]: row for row in rows(gen.BOM)}
    closure = {row["item_id"]: row for row in rows(gen.CLOSURE)}
    need(len(bom) >= 108 and set(bom) == set(closure), "108-group minimum BOM parity failed")
    need(bom["BOM-107"]["baseline_status"] == "exact_candidate_hold" and "TNM3-6.5-10-1" in bom["BOM-107"]["manufacturer_part_number"], "BOM-107 not advanced correctly")
    need(bom["BOM-108"]["baseline_status"] == "exact_candidate_hold" and "300251659935" in bom["BOM-108"]["manufacturer_part_number"], "BOM-108 not advanced correctly")
    need("existing customers" in bom["BOM-104"]["selection_basis"] and "16.13" in bom["BOM-104"]["selection_basis"], "BOM-104 procurement/stack hold missing")

    status = json.loads((gen.REL / "package-status.json").read_text(encoding="utf-8"))
    need(status.get("identifier") == gen.ID and status.get("exact_mounting_hardware_candidates_defined") is True, "package identity/candidate state changed")
    false_keys = (
        "mounting_hardware_selected","samtec_general_orderability_confirmed","mounting_stack_physically_accepted",
        "panel_holes_released","cut_lengths_selected","physical_article_exists","physical_test_executed",
        "qualified_review_complete","procurement_authorized","fabrication_authorized","assembly_authorized",
        "connection_authorized","powered_testing_authorized","motion_authorized","energization_authorized","safety_credit",
    )
    need(all(status.get(key) is False for key in false_keys), "package authority/evidence improperly promoted")

    cfg_status = json.loads((gen.CFG / "package-status.json").read_text(encoding="utf-8"))
    expected_counts = {"identifier":gen.CID,"current_records":43,"supersession_records":36,"bom_integration_records":28,"gate_records":11,"open_holds":153,"acceptance_rows":191}
    need(all(cfg_status.get(key) == value for key, value in expected_counts.items()), "configuration counts changed")
    hold15 = next(row for row in rows(gen.CFG / "open-holds.csv") if row["hold_id"] == "HOLD-15")
    need(hold15["state"] == "PARTIALLY ADDRESSED - OPEN" and gen.ID in hold15["closure_evidence"], "HOLD-15 improperly closed/hidden")
    current = rows(gen.CFG / "current-configuration-map.csv")
    source_hashes = {row["source_path"]: row["sha256"] for row in rows(gen.CFG / "source-hash-register.csv")}
    successor_mutable = {"bom/bom.csv", "release/hr-v0/release-candidate.json"}
    need(
        len(current) == 43
        and len(source_hashes) == 43
        and all(
            row["source_path"] in successor_mutable
            or source_hashes.get(row["source_path"]) == sha(gen.ROOT / row["source_path"])
            for row in current
        ),
        "current-source hash parity failed outside successor-controlled BOM/release metadata",
    )

    release = json.loads(gen.RELEASE.read_text(encoding="utf-8"))
    for domain in ("electrical","bill_of_materials","assembly"):
        product = next(row for row in release["current_products"] if row.get("domain") == domain)
        need(product.get("configuration_reconciliation") in {gen.CID, "HR-V0-CONFIG-REC-P0.25", "HR-V0-CONFIG-REC-P0.26", "HR-V0-CONFIG-REC-P0.27", "HR-V0-CONFIG-REC-P0.28", "HR-V0-CONFIG-REC-P0.29", "HR-V0-CONFIG-REC-P0.30", "HR-V0-CONFIG-REC-P0.31"} and product.get("observation_mount_stack") == gen.ID and gen.ID in product.get("supporting_identifiers", []), f"release metadata stale: {domain}")
    page = (gen.REL / "index.html").read_text(encoding="utf-8")
    for token in (gen.WARNING,"font:clamp(16px","font-size:14px","0.13 mm","0</div><strong>released purchases or holes","DO NOT DRILL","data-view='pi'"):
        need(token in page, f"web guide token missing: {token}")
    need((gen.ENG / "index.html").read_bytes() == (gen.REL / "index.html").read_bytes(), "engineering/release page mismatch")

    if errors:
        print("R260 observation mounting-stack correction: FAIL", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("R260 observation mounting-stack correction: PASS")
    print("  two exact-candidate mounting interfaces; 9 holds and 12 acceptances remain open")
    print(gen.WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
