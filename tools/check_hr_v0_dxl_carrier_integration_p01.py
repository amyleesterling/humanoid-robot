"""Fail-closed checks for the R161 carrier-integrated ECAD candidate."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENG = ROOT / "electrical" / "integration" / "hr-v0-dxl-carrier-integration-p0.1"
OUT = ROOT / "release" / "hr-v0" / "dxl-carrier-integration-p0.1"
ELEC = ROOT / "electrical" / "kicad" / "project-button-v3-p1.15-carrier-candidate"
STAR = ROOT / "electrical" / "kicad" / "hr-v0-dxl-star-p0.2-carrier-candidate"
CARRIER = ROOT / "electrical" / "kicad" / "hr-v0-dxl-protection-carrier-p0.3"
WARNING = (
    "PRELIMINARY - NOT APPROVED FOR SUPPLIER UPLOAD, QUOTATION, PROCUREMENT, "
    "FABRICATION, ASSEMBLY, CONNECTION, MOTION, OR ENERGIZATION"
)


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    failures: list[str] = []

    def need(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    common = {
        "README.md", "package-status.json", "file-manifest.csv", "source-register.csv",
        "net-transition-matrix.csv", "panel-placement-screen.csv", "mounting-hole-screen.csv",
        "route-bound-screen.csv", "unresolved-selections.csv", "acceptance-matrix.csv",
    }
    for directory, expected in ((ENG, common), (OUT, common | {"index.html"})):
        actual = {p.relative_to(directory).as_posix() for p in directory.rglob("*") if p.is_file()}
        need(actual == expected, f"package membership mismatch: {directory.name}: {sorted(actual ^ expected)}")
        need(not any(p.suffix.lower() in {".zip", ".7z", ".rar"} for p in directory.rglob("*")), "archive found")

    status = json.loads((OUT / "package-status.json").read_text(encoding="utf-8"))
    need(status.get("identifier") == "HR-V0-DXL-CARRIER-INTEGRATION-P0.1", "identifier changed")
    need(status.get("round") == "R161", "round changed")
    for key, expected in {
        "candidate_carriers": 3, "net_transition_rows": 15, "placement_rows": 3,
        "mounting_hole_rows": 12, "route_rows": 6,
        "unresolved_selections": 12, "acceptance_rows": 24,
    }.items():
        need(status.get(key) == expected, f"status count changed: {key}")
    for key, value in status.items():
        if key.endswith(("_authorized", "_approved")) or key in {
            "physical_article_exists", "physical_test_executed", "qualified_review_complete",
            "supplier_contacted", "safety_credit", "buildable", "energization_ready",
        }:
            need(value is False, f"{key} must remain false")
    need(status.get("warning") == WARNING, "warning changed")

    source_paths = {
        "electrical/kicad/project-button-v3-p1.15-carrier-candidate/connector-schedule.csv": ELEC / "connector-schedule.csv",
        "electrical/kicad/project-button-v3-p1.15-carrier-candidate/net-schedule.csv": ELEC / "net-schedule.csv",
        "electrical/kicad/project-button-v3-p1.15-carrier-candidate/validation/project-button-v3-p1.15-carrier-candidate.net": ELEC / "validation" / "project-button-v3-p1.15-carrier-candidate.net",
        "electrical/kicad/hr-v0-dxl-star-p0.2-carrier-candidate/connector-schedule.csv": STAR / "connector-schedule.csv",
        "electrical/kicad/hr-v0-dxl-star-p0.2-carrier-candidate/hr-v0-dxl-star-p0.2-carrier-candidate.kicad_pcb": STAR / "hr-v0-dxl-star-p0.2-carrier-candidate.kicad_pcb",
        "electrical/kicad/hr-v0-dxl-protection-carrier-p0.3/terminal-schedule.csv": CARRIER / "terminal-schedule.csv",
        "electrical/kicad/hr-v0-dxl-protection-carrier-p0.3/hr-v0-dxl-protection-carrier-p0.3.kicad_pcb": CARRIER / "hr-v0-dxl-protection-carrier-p0.3.kicad_pcb",
        "electrical/panel/hr-v0-control-panel-p0.6/backplate-layout.csv": ROOT / "electrical" / "panel" / "hr-v0-control-panel-p0.6" / "backplate-layout.csv",
    }
    need(set(status.get("source_hashes", {})) == set(source_paths), "source hash membership changed")
    for key, path in source_paths.items():
        need(path.is_file(), f"source missing: {key}")
        if path.is_file():
            need(status["source_hashes"].get(key) == digest(path), f"source hash mismatch: {key}")

    erc = (ELEC / "validation" / "project-button-v3-p1.15-carrier-candidate-erc.rpt").read_text(encoding="utf-8-sig")
    need("ERC messages: 0  Errors 0  Warnings 0" in erc, "Electrical candidate ERC is not 0/0")
    star_erc = (STAR / "validation" / "hr-v0-dxl-star-p0.2-carrier-candidate-erc.rpt").read_text(encoding="utf-8-sig")
    star_drc = (STAR / "validation" / "hr-v0-dxl-star-p0.2-carrier-candidate-drc.rpt").read_text(encoding="utf-8-sig")
    need("ERC messages: 0  Errors 0  Warnings 0" in star_erc, "DXL-star candidate ERC is not 0/0")
    need("Found 0 DRC violations" in star_drc and "Found 0 unconnected pads" in star_drc, "DXL-star candidate DRC is not clean")

    connector_rows = rows(ELEC / "connector-schedule.csv")
    connectors = {(r["reference"], r["terminal"]): r["net"] for r in connector_rows}
    sheet_by_ref = {r["reference"]: r["sheet"] for r in connector_rows}
    need(not (ELEC / "06_branches_and_injection.kicad_sch").exists(), "crowded historical sheet remains in candidate")
    need((ELEC / "06_branches_and_limiters.kicad_sch").is_file(), "focused limiter sheet missing")
    for ref in ("F1", "F2", "F3", "LIM1", "LIM2", "LIM3"):
        need(sheet_by_ref.get(ref) == "06_branches_and_limiters.kicad_sch", f"{ref} not on focused limiter sheet")
    need(sheet_by_ref.get("INJ1") == "10_actuator_interfaces.kicad_sch", "INJ1 not on focused star/interface sheet")
    for index in (1, 2, 3):
        pre, post = f"J{index}_FUSED_PRELIMIT", f"J{index}_LIMITED_VDD"
        need(connectors.get((f"F{index}", "2")) == pre, f"F{index}.2 pre-limit mapping wrong")
        need(connectors.get((f"LIM{index}", "JIN1:1")) == pre, f"LIM{index} input positive mapping wrong")
        need(connectors.get((f"LIM{index}", "JOUT1:1")) == post, f"LIM{index} output positive mapping wrong")
        need(connectors.get((f"LIM{index}", "JIN1:2")) == "ACT_0V_PE_BONDED", f"LIM{index} input return mapping wrong")
        need(connectors.get((f"LIM{index}", "JOUT1:2")) == "ACT_0V_PE_BONDED", f"LIM{index} output return mapping wrong")
        need(connectors.get(("INJ1", f"PWR{index}:1")) == post, f"INJ1 branch {index} mapping wrong")
        need(connectors.get((f"J{index}", "2")) == post, f"J{index}.2 actuator mapping wrong")
    positive_text = "\n".join((
        (ELEC / "connector-schedule.csv").read_text(),
        (ELEC / "net-schedule.csv").read_text(),
        (ELEC / "validation" / "project-button-v3-p1.15-carrier-candidate.net").read_text(),
    ))
    for old in ("J1_VDD", "J2_VDD", "J3_VDD"):
        need(old not in positive_text, f"ambiguous legacy net remains: {old}")

    star_rows = {(r["reference"], r["terminal"]): r["net"] for r in rows(STAR / "connector-schedule.csv")}
    need(star_rows.get(("JC1", "2")) == "INTENTIONALLY_UNUSED_U2D2_VDD", "U2D2 VDD omission changed")
    for index in (1, 2, 3):
        post = f"J{index}_LIMITED_VDD"
        need(star_rows.get((f"JP{index}", "1")) == post, f"JP{index}.1 mapping wrong")
        need(star_rows.get((f"JA{index}", "2")) == post, f"JA{index}.2 mapping wrong")
        need(star_rows.get((f"JP{index}", "2")) == "ACT_0V_PE_BONDED", f"JP{index}.2 return wrong")

    transitions = rows(OUT / "net-transition-matrix.csv")
    need(len(transitions) == 15 and {r["axis"] for r in transitions} == {"J1", "J2", "J3"}, "transition matrix must contain 15 three-axis rows")
    need(all(r["warning"] == WARNING for r in transitions), "transition warning changed")
    placements = rows(OUT / "panel-placement-screen.csv")
    expected_placements = {"LIM1": (54.0, 538.0), "LIM2": (164.0, 538.0), "LIM3": (54.0, 608.0)}
    need(len(placements) == 3, "expected three placement rows")
    for row in placements:
        ref = row["reference"]
        need(ref in expected_placements and (float(row["x_mm"]), float(row["y_mm"])) == expected_placements[ref], f"placement changed: {ref}")
        need(row["boundary_result"] == "ANALYTICAL PASS" and row["overlap_result"] == "ANALYTICAL PASS", f"placement screen failed: {ref}")
        need(row["release_state"] == "PLACEMENT CANDIDATE - NO DRILLING", f"placement incorrectly released: {ref}")
    holes = rows(OUT / "mounting-hole-screen.csv")
    need(len(holes) == 12 and len({(r["carrier_reference"], r["hole_reference"]) for r in holes}) == 12, "mounting-hole screen changed")
    routes = rows(OUT / "route-bound-screen.csv")
    need(len(routes) == 6 and all(r["cut_length_mm"] == "SELECTION REQUIRED" and r["release_state"] == "ROUTE SCREEN ONLY - DO NOT CUT" for r in routes), "route screen released a cut length")
    unresolved = rows(OUT / "unresolved-selections.csv")
    need(len(unresolved) == 12 and all(r["state"] == "SELECTION REQUIRED" for r in unresolved), "twelve selections must remain open")
    acceptance = rows(OUT / "acceptance-matrix.csv")
    need(len(acceptance) == 24 and all(r["execution_state"] == "NOT EXECUTED" and r["result"] == "OPEN" and not r["approver"] for r in acceptance), "acceptance evidence must remain open")

    page = (OUT / "index.html").read_text(encoding="utf-8")
    for token in ("font:clamp(16px", "font-size:14px", "Every branch now has a before and an after.", "Coordinates do not authorize holes or mounting.", "24</b>open acceptance rows", WARNING):
        need(token in page, f"interactive guide token missing: {token}")
    for name in common - {"file-manifest.csv"}:
        need((ENG / name).read_bytes() == (OUT / name).read_bytes(), f"engineering/release mismatch: {name}")
    for directory in (ENG, OUT):
        manifest = rows(directory / "file-manifest.csv")
        actual = {p.relative_to(directory).as_posix() for p in directory.rglob("*") if p.is_file() and p.name != "file-manifest.csv"}
        need({r["path"] for r in manifest} == actual, f"manifest membership mismatch: {directory.name}")
        for row in manifest:
            path = directory / row["path"]
            need(row["sha256"] == digest(path) and int(row["bytes"]) == path.stat().st_size, f"manifest mismatch: {directory.name}/{row['path']}")

    if failures:
        print("HR-V0-DXL-CARRIER-INTEGRATION-P0.1 FAILED")
        for failure in failures:
            print("-", failure)
        return 1
    print("HR-V0-DXL-CARRIER-INTEGRATION-P0.1 PASS")
    print("  distinct fused-prelimit and limited-postcarrier nets; 3 placement candidates")
    print("  12 selections and 24 acceptance rows remain OPEN; no authority granted")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
