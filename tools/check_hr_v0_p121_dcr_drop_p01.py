#!/usr/bin/env python3
"""Validate R244 nominal DCR/drop evidence and configuration P0.8."""
from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENG = ROOT / "electrical/routing/hr-v0-p121-dcr-drop-p0.1"
OUT = ROOT / "release/hr-v0/p121-dcr-drop-p0.1"
CFG_ENG = ROOT / "configuration/hr-v0-config-reconciliation-p0.8"
CFG_OUT = ROOT / "release/hr-v0/configuration-reconciliation-p0.8"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def rows(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_dir(directory: Path, expected: set[str], fail) -> None:
    fail(not directory.is_dir() or {p.name for p in directory.iterdir() if p.is_file()} != expected, f"membership: {directory}")
    manifest = rows(directory / "file-manifest.csv")
    actual = {p.name for p in directory.iterdir() if p.is_file() and p.name != "file-manifest.csv"}
    fail({row["path"] for row in manifest} != actual, f"manifest membership: {directory}")
    for row in manifest:
        path = directory / row["path"]
        fail(not path.is_file() or path.stat().st_size != int(row["bytes"]) or digest(path) != row["sha256"], f"manifest mismatch: {path}")


def main() -> int:
    errors: list[str] = []
    fail = lambda condition, message: errors.append(message) if condition else None
    common = {"README.md","source-register.csv","dcr-conversion.csv","route-resistance-coefficients.csv","nominal-voltage-drop-screen.csv","driver-bit-disposition.csv","prior-hold-disposition.csv","open-holds.csv","package-status.json","file-manifest.csv"}
    check_dir(ENG, common, fail); check_dir(OUT, common | {"index.html"}, fail)
    for name in common - {"file-manifest.csv"}:
        fail((ENG / name).read_bytes() != (OUT / name).read_bytes(), f"engineering/release mismatch: {name}")
    status = json.loads((OUT / "package-status.json").read_text(encoding="utf-8"))
    for key,value in {"identifier":"HR-V0-P121-DCR-DROP-P0.1","round":"R244","nominal_dcr_ohm_per_1000ft_at_20C":4.4,"numeric_path_screens":4,"uncalculated_path_screens":1,"open_holds":12,"warning":WARNING}.items():
        fail(status.get(key) != value, f"status: {key}")
    for key in ("r242_h03_closed","pilz_bit_selected","phoenix_bit_selected","received_dcr_exists","actual_cut_lengths_released","complete_circuit_voltage_budget_accepted","physical_evidence_exists","qualified_review_complete","procurement_authorized","fabrication_authorized","assembly_authorized","connection_authorized","powered_testing_authorized","motion_authorized","energization_authorized","safety_credit"):
        fail(status.get(key) is not False, f"{key} must be false")
    conv = rows(OUT / "dcr-conversion.csv")
    expected_dcr = 4.4 / 304.8
    fail(len(conv) != 1 or not math.isclose(float(conv[0]["nominal_ohm_per_m"]), expected_dcr, rel_tol=0, abs_tol=5e-13), "DCR conversion")
    routes = rows(OUT / "route-resistance-coefficients.csv")
    fail(len(routes) != 7 or {row["conductor_id"] for row in routes} != {f"C-{n:02d}" for n in range(1,8)}, "seven route coefficients")
    fail(not math.isclose(sum(float(row["planning_centerline_m"]) for row in routes), 6.72325, abs_tol=5e-8), "route length sum")
    fail(not math.isclose(sum(float(row["conditional_nominal_centerline_resistance_ohm"]) for row in routes), 6.72325 * expected_dcr, abs_tol=4e-9), "route resistance sum")
    fail(any("NOT AN INSTALLED RESISTANCE BOUND" not in row["classification"] or row["release_result"] != "NOT ACCEPTED" for row in routes), "route coefficient boundary")
    screens = {r["screen_id"]:r for r in rows(OUT / "nominal-voltage-drop-screen.csv")}
    fail(set(screens) != {"VDN-001","VDN-002","VDN-003","VDN-004","VDN-005"}, "screen membership")
    expectations = {"VDN-001":(1.37025,2.5/24,0.5),"VDN-002":(1.30025,.018,None),"VDN-003":(1.50425,2.5/24,.5),"VDN-004":(1.27425,.018,None)}
    for sid,(length,current,pulse) in expectations.items():
        row = screens[sid]; resistance = length * expected_dcr
        fail(not math.isclose(float(row["nominal_conductor_resistance_ohm"]), resistance, abs_tol=5e-10), f"resistance: {sid}")
        fail(not math.isclose(float(row["nominal_conductor_only_drop_V"]), resistance * current, abs_tol=5e-10), f"drop: {sid}")
        fail("ONE-WAY CENTERLINE" not in row["classification"] or "NOT ACCEPTED" not in row["release_result"], f"boundary: {sid}")
        if pulse is not None:
            fail(not math.isclose(float(row["nominal_pulse_conductor_only_drop_V"]), resistance * pulse, abs_tol=5e-10), f"pulse: {sid}")
    fail(screens["VDN-005"]["nominal_conductor_only_drop_V"] != "NOT CALCULATED", "VDN-005 must stay uncalculated")
    bits = rows(OUT / "driver-bit-disposition.csv")
    fail(len(bits) != 2 or any(row["state"] not in {"OPEN","SELECTION REQUIRED"} for row in bits), "bit rows open")
    fail(any("SELECTION REQUIRED" not in row["candidate_bit"] and "strongest held candidate" not in row["candidate_bit"] for row in bits), "bit selection language")
    disp = {row["prior_hold"]:row for row in rows(OUT / "prior-hold-disposition.csv")}
    fail(set(disp) != {"R242-H03","R243-H03","R243-H04"}, "hold disposition set")
    fail(disp.get("R242-H03",{}).get("disposition") != "PARTIALLY ADDRESSED - OPEN", "R242-H03 must remain open")
    fail(len(rows(OUT / "open-holds.csv")) != 12 or any(row["state"] != "OPEN" for row in rows(OUT / "open-holds.csv")), "twelve holds open")
    source_text = " ".join(" ".join(row.values()) for row in rows(OUT / "source-register.csv"))
    for token in ("4.4 ohm/1000 ft","21396-EN-23","2967060","1212224","1212568","1212569"):
        fail(token not in source_text, f"source token: {token}")
    page = (OUT / "index.html").read_text(encoding="utf-8")
    for token in (WARNING,"font:clamp(16px","font-size:14px","4 numeric path screens","R242-H03 remains open","SELECTION REQUIRED"):
        fail(token not in page, f"web token: {token}")
    cfg_common = {"README.md","current-configuration-map.csv","supersession-map.csv","bom-integration-map.csv","gate-impact.csv","open-holds.csv","acceptance-matrix.csv","package-status.json","source-hash-register.csv","file-manifest.csv"}
    check_dir(CFG_ENG, cfg_common, fail); check_dir(CFG_OUT, cfg_common | {"index.html"}, fail)
    cfg = json.loads((CFG_OUT / "package-status.json").read_text(encoding="utf-8"))
    for key,value in {"identifier":"HR-V0-CONFIG-REC-P0.8","round":"R244","system_bom_groups":98,"current_records":27,"supersession_records":15,"bom_integration_records":18,"gate_records":11,"open_holds":38,"acceptance_rows":47}.items():
        fail(cfg.get(key) != value, f"config: {key}")
    fail(cfg.get("current_core_electrical_identifier") != "Project Button Electrical V3-P1.15-CARRIER-CANDIDATE", "P1.15 current")
    fail(cfg.get("unaccepted_panel_topology_candidate") != "V3-P1.21-SRA1-SUPPLY-WATCHDOG-CANDIDATE", "P1.21 unaccepted")
    sources = rows(CFG_OUT / "source-hash-register.csv")
    fail(len(sources) != 27, "configuration source count")
    for row in sources:
        source = ROOT / row["source_path"]
        if row["source_path"] in {"bom/bom.csv","release/hr-v0/release-candidate.json"}: fail(len(row["sha256"]) != 64, f"historical mutable-source hash format: {row['source_path']}")
        else: fail(not source.is_file() or digest(source) != row["sha256"], f"configuration source hash: {row['source_path']}")
    bom = rows(ROOT / "bom/bom.csv"); closure = rows(ROOT / "bom/hr-v0-bom-closure.csv")
    fail(len(bom) < 98 or len(closure) < 98 or {row["item_id"] for row in bom} != {row["item_id"] for row in closure}, "current BOM must retain the R244 98-group subset with full closure parity")
    release = json.loads((ROOT / "release/hr-v0/release-candidate.json").read_text(encoding="utf-8"))
    electrical = next(p for p in release["current_products"] if p["domain"] == "electrical")
    bill = next(p for p in release["current_products"] if p["domain"] == "bill_of_materials")
    fail(electrical.get("p121_dcr_drop_dossier") != "HR-V0-P121-DCR-DROP-P0.1" or "HR-V0-CONFIG-REC-P0.8" not in electrical.get("supporting_identifiers", []), "electrical release metadata must retain the R244 dossier and configuration history")
    fail(bill.get("system_group_count", 0) < 98 or "HR-V0-CONFIG-REC-P0.8" not in bill.get("supporting_identifiers", []), "BOM release metadata must retain the R244 baseline while permitting controlled successors")
    if errors:
        print("HR-V0 R244 nominal DCR/drop package: FAIL")
        for error in errors: print("-", error)
        return 1
    print("HR-V0 R244 nominal DCR/drop package: PASS")
    print("4 numeric one-way centerline conductor-only screens; 1 uncalculated; 12 holds; both exact bits open")
    print("No procurement, fabrication, assembly, connection, powered test, motion, safety credit or energization authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
