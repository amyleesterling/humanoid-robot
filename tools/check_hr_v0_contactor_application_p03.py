#!/usr/bin/env python3
"""Validate R226 K1/K2 application/configuration binding fail closed."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
P115 = ROOT / "electrical/kicad/project-button-v3-p1.15-carrier-candidate"
P118 = ROOT / "electrical/kicad/project-button-v3-p1.18-panel-topology-candidate"
ENG = ROOT / "electrical/reviews/hr-v0-contactor-application-p0.3"
OUT = ROOT / "release/hr-v0/contactor-application-p0.3"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def net_members(path: Path) -> dict[str, set[tuple[str, str]]]:
    text = path.read_text(encoding="utf-8")
    result: dict[str, set[tuple[str, str]]] = {}
    current: list[str] | None = None
    depth = 0
    in_nets = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped == "(nets":
            in_nets = True
            continue
        if in_nets and current is None and stripped == "(net":
            current = [line]
            depth = line.count("(") - line.count(")")
            continue
        if current is not None:
            current.append(line)
            depth += line.count("(") - line.count(")")
            if depth == 0:
                block = "\n".join(current)
                name = re.search(r'\(name "([^"]+)"\)', block)
                if name:
                    result[name.group(1)] = set(re.findall(r'\(node\s+\(ref "([^"]+)"\)\s+\(pin "([^"]+)"\)', block, flags=re.S))
                current = None
    return result


def main() -> int:
    failures: list[str] = []
    need = lambda condition, message: failures.append(message) if not condition else None
    common = {"README.md", "parity-register.csv", "power-chain-register.csv", "application-evidence-register.csv", "open-holds.csv", "source-register.csv", "authority-boundary.csv", "package-status.json", "file-manifest.csv"}
    for directory, expected in ((ENG, common), (OUT, common | {"index.html"})):
        actual = {p.name for p in directory.iterdir() if p.is_file()} if directory.is_dir() else set()
        need(actual == expected, f"package membership mismatch: {directory}")
        need(not any(p.suffix.lower() in {".pdf", ".zip", ".7z", ".rar"} for p in directory.iterdir()), f"archive/PDF prohibited: {directory}")
        manifest = rows(directory / "file-manifest.csv")
        controlled = {p.name for p in directory.iterdir() if p.is_file() and p.name != "file-manifest.csv"}
        need({r["path"] for r in manifest} == controlled, f"manifest membership mismatch: {directory}")
        for row in manifest:
            path = directory / row["path"]
            need(path.is_file() and path.stat().st_size == int(row["bytes"]) and digest(path) == row["sha256"], f"manifest mismatch: {path}")
    for name in common - {"file-manifest.csv"}:
        need((ENG / name).read_bytes() == (OUT / name).read_bytes(), f"engineering/release mismatch: {name}")

    p115_rows = rows(P115 / "wire-number-table.csv")
    p118_rows = rows(P118 / "wire-number-table.csv")
    contactor_sheets = {"04_contactor_edm.kicad_sch": 16, "05_actuator_interruption.kicad_sch": 16}
    for sheet, count in contactor_sheets.items():
        a = [r for r in p115_rows if r["sheet"] == sheet]
        b = [r for r in p118_rows if r["sheet"] == sheet]
        need(len(a) == count and len(b) == count, f"terminal-row count changed: {sheet}")
        need(a == b, f"P1.15/P1.18 parity changed: {sheet}")
    parity = rows(OUT / "parity-register.csv")
    need(len(parity) == 32, "parity register must contain 32 rows")
    need(sum(r["domain"] == "coil_edm" for r in parity) == 16, "coil/EDM parity count changed")
    need(sum(r["domain"] == "power_path" for r in parity) == 16, "power-path parity count changed")
    need(all(r["comparison"] == "IDENTICAL" and r["p115_state"] == r["p118_state"] == "EXACT" for r in parity), "parity overclaim or mismatch")

    exact_internal = {
        "K1_P1_IN": {("SD1", "TBD-OUT"), ("KP1", "1L1")},
        "K1_J12": {("KP1", "2T1"), ("KP1", "3L2")},
        "K1_J23": {("KP1", "4T2"), ("KP1", "5L3")},
        "K1_OUT": {("KP1", "6T3"), ("KP2", "1L1")},
        "K2_J12": {("KP2", "2T1"), ("KP2", "3L2")},
        "K2_J23": {("KP2", "4T2"), ("KP2", "5L3")},
        "EDM_K1_OUT": {("K1", "22"), ("K2", "21")},
        "K1_A1": {("FSR1", "2"), ("K1", "A1")},
        "K2_A1": {("FSR2", "2"), ("K2", "A1")},
    }
    required_subsets = {
        "ACT_12V_RAW": {("F0", "1")},
        "ACT_12V_FUSED": {("F0", "2"), ("SD1", "TBD-IN")},
        "ACT_12V_BUS": {("KP2", "6T3")},
        "ARM_AFTER_S2": {("K1", "21")},
        "SRA1_START_RETURN": {("K2", "22")},
        "SAFETY_24V": {("K1", "13"), ("K2", "13")},
        "SAFETY_0V": {("K1", "A2"), ("K2", "A2")},
    }
    for project in (P115, P118):
        netfile = next((project / "validation").glob("*.net"))
        nets = net_members(netfile)
        for name, expected in exact_internal.items():
            need(nets.get(name) == expected, f"exact net changed in {project.name}: {name}")
        for name, expected in required_subsets.items():
            need(expected <= nets.get(name, set()), f"required endpoint missing in {project.name}: {name}")
        sheet_tokens = {
            "04_contactor_edm.kicad_sch": ("LC1D25BD", "Loaded DC interruption", "critical-current"),
            "05_actuator_interruption.kicad_sch": ("K1 three main poles represented in series", "K2 three main poles represented in series", "lower-current application boundary"),
        }
        for sheet, tokens in sheet_tokens.items():
            text = (project / sheet).read_text(encoding="utf-8")
            for token in tokens:
                need(token in text, f"native warning/identity missing in {project.name}/{sheet}: {token}")

    source_rows = {r["source_id"]: r for r in rows(OUT / "source-register.csv")}
    need(len(source_rows) == 13, "source register must contain 13 rows")
    local_paths = [
        P115 / "04_contactor_edm.kicad_sch", P115 / "05_actuator_interruption.kicad_sch", P115 / "wire-number-table.csv", P115 / "validation/project-button-v3-p1.15-carrier-candidate.net",
        P118 / "04_contactor_edm.kicad_sch", P118 / "05_actuator_interruption.kicad_sch", P118 / "wire-number-table.csv", P118 / "validation/project-button-v3-p1.18-panel-topology-candidate.net",
        ROOT / "electrical/contactor/hr-v0-lc1d25bd-application-inputs-p0.2.csv", ROOT / "docs/hr-v0-contactor-application-p0.2.md",
    ]
    for index, path in enumerate(local_paths, 1):
        need(source_rows.get(f"KAP3-SRC-{index:03d}", {}).get("sha256") == digest(path), f"local source hash changed: {path}")
    need("version 17.1" in source_rows.get("KAP3-SRC-011", {}).get("revision_or_date", ""), "current catalog identity missing")
    need("2017-09-13" in source_rows.get("KAP3-SRC-012", {}).get("revision_or_date", ""), "product-sheet date missing")
    need("not a Project Button application disposition" in source_rows.get("KAP3-SRC-011", {}).get("boundary", ""), "catalog boundary weakened")

    chain = rows(OUT / "power-chain-register.csv")
    need(len(chain) == 16 and [r["step"] for r in chain] == [str(i) for i in range(1, 17)], "power-chain sequence changed")
    need(chain[0]["endpoint"] == "F0:1" and chain[-1]["endpoint"] == "KP2:6T3", "power-chain endpoints changed")
    need(all(r["configuration_result"] == "P1.15/P1.18 IDENTICAL" and r["application_result"] == "NOT APPROVED" for r in chain), "chain application boundary weakened")
    app = rows(OUT / "application-evidence-register.csv")
    need(len(app) == 12 and all(r["gate"] == "EG-013 PARTIAL" for r in app), "application register gate state changed")
    need(not any(r["state"] in {"APPROVED", "RELEASED", "PASS", "CLOSED"} for r in app), "application evidence falsely closed")
    holds = rows(OUT / "open-holds.csv")
    need(len(holds) == 11 and all(r["state"] == "OPEN" and r["accepted"] == "FALSE" for r in holds), "hold falsely closed")
    authority = rows(OUT / "authority-boundary.csv")
    need(len(authority) == 4 and sum(r["permitted"] == "TRUE" for r in authority) == 1, "authority boundary changed")

    status = json.loads((OUT / "package-status.json").read_text(encoding="utf-8"))
    for key, value in {"identifier": "HR-V0-K1K2-APP-P0.3", "round": "R226", "coil_edm_rows_identical": 16, "power_path_rows_identical": 16, "open_holds": 11, "eg_013_status": "partial"}.items():
        need(status.get(key) == value, f"status mismatch: {key}")
    for key in ("p118_accepted", "dc_application_approved", "manufacturer_disposition_received", "physical_tests_executed", "qualified_review_received", "procurement_authorized", "fabrication_authorized", "assembly_authorized", "connection_authorized", "powered_testing_authorized", "motion_authorized", "energization_authorized"):
        need(status.get(key) is False, f"{key} must remain false")
    gates = {r["gate_id"]: r for r in rows(ROOT / "requirements/hr-v0-energization-gates.csv")}
    for gate_id in ("EG-002", "EG-004", "EG-013"):
        need(gates.get(gate_id, {}).get("status") == "partial", f"{gate_id} must remain partial")
        need("docs/hr-v0-contactor-application-p0.3.md" in gates.get(gate_id, {}).get("evidence_location", ""), f"{gate_id} lacks R226 evidence")
    release = json.loads((ROOT / "release/hr-v0/release-candidate.json").read_text(encoding="utf-8"))
    electrical = next(r for r in release["current_products"] if r["domain"] == "electrical")
    need("HR-V0-K1K2-APP-P0.3" in electrical["supporting_identifiers"], "release metadata lacks P0.3")
    need(electrical.get("contactor_application_record") == "HR-V0-K1K2-APP-P0.3", "current contactor record missing")
    page = (OUT / "index.html").read_text(encoding="utf-8")
    for token in (WARNING, "font:clamp(16px", "font-size:14px", "all 32 rows", "EG-013 remains PARTIAL", "addEventListener", "11 open holds"):
        need(token in page, f"web guide missing token: {token}")
    for filename in ("parity-register.csv", "power-chain-register.csv", "application-evidence-register.csv", "open-holds.csv", "source-register.csv", "authority-boundary.csv"):
        need(all(r.get("warning") == WARNING for r in rows(OUT / filename)), f"warning missing: {filename}")

    if failures:
        print("HR-V0 K1/K2 application P0.3: FAIL")
        for failure in failures:
            print("-", failure)
        return 1
    print("HR-V0 K1/K2 application P0.3: PASS")
    print("16 coil/EDM + 16 power-path rows identical across P1.15/P1.18; 11 holds; EG-013 partial")
    print("No DC application approval, physical test, qualified review, or work authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
