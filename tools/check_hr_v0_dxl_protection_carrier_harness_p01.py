"""Validate R160 carrier harness package without granting work authority."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENG = ROOT / "electrical" / "harness" / "hr-v0-dxl-protection-carrier-harness-p0.1"
OUT = ROOT / "release" / "hr-v0" / "dxl-protection-carrier-harness-p0.1"
WARNING = (
    "PRELIMINARY - NOT APPROVED FOR SUPPLIER UPLOAD, QUOTATION, PROCUREMENT, "
    "FABRICATION, ASSEMBLY, CONNECTION, MOTION, OR ENERGIZATION"
)
SOURCES = {
    "electrical/kicad/hr-v0-dxl-protection-carrier-p0.3/terminal-schedule.csv": ROOT / "electrical" / "kicad" / "hr-v0-dxl-protection-carrier-p0.3" / "terminal-schedule.csv",
    "electrical/kicad/hr-v0-dxl-protection-carrier-p0.3/bom.csv": ROOT / "electrical" / "kicad" / "hr-v0-dxl-protection-carrier-p0.3" / "bom.csv",
    "electrical/kicad/hr-v0-dxl-star/connector-schedule.csv": ROOT / "electrical" / "kicad" / "hr-v0-dxl-star" / "connector-schedule.csv",
    "electrical/kicad/project-button-v3/connector-schedule.csv": ROOT / "electrical" / "kicad" / "project-button-v3" / "connector-schedule.csv",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    failures: list[str] = []

    def need(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    common = {"README.md", "package-status.json", "file-manifest.csv", "primary-source-register.csv", "harness-bom.csv", "interface-control.csv", "cut-crimp-schedule.csv", "manufacturing-process.csv", "acceptance-matrix.csv", "unresolved-selections.csv"}
    for directory, expected in ((ENG, common), (OUT, common | {"index.html"})):
        actual = {path.relative_to(directory).as_posix() for path in directory.rglob("*") if path.is_file()}
        need(actual == expected, f"package membership mismatch in {directory.name}: {sorted(actual ^ expected)}")
        need(not any(path.suffix.lower() in {".zip", ".7z", ".rar"} for path in directory.rglob("*")), "archive must not exist")

    status = json.loads((OUT / "package-status.json").read_text(encoding="utf-8"))
    need(status.get("identifier") == "HR-V0-DXL-PROT-CARRIER-HARNESS-P0.1" and status.get("round") == "R160", "identity/round mismatch")
    for key, value in {"harnesses": 2, "interface_rows": 8, "exact_candidate_bom_rows": 5, "selection_required_bom_rows": 2, "acceptance_rows": 18, "open_acceptance_rows": 18, "unresolved_selections": 9}.items():
        need(status.get(key) == value, f"status count changed: {key}")
    for key in ("input_source_side_termination_selected", "cut_lengths_selected", "crimp_process_released", "harness_buildable", "harness_fabricated", "physical_test_executed", "qualified_review_complete", "supplier_contacted", "procurement_authorized", "fabrication_authorized", "assembly_authorized", "connection_authorized", "motion_authorized", "energization_authorized", "safety_credit"):
        need(status.get(key) is False, f"{key} must remain false")
    need(status.get("warning") == WARNING, "warning changed")
    need(set(status.get("source_hashes", {})) == set(SOURCES), "source-hash membership changed")
    for key, path in SOURCES.items():
        need(status["source_hashes"].get(key) == sha256(path), f"source hash mismatch: {key}")

    carrier = {(r["reference"], r["terminal"]): r for r in read_csv(SOURCES["electrical/kicad/hr-v0-dxl-protection-carrier-p0.3/terminal-schedule.csv"])}
    need(carrier.get(("JIN1", "1"), {}).get("net") == "BRANCH_FUSED_IN", "JIN1.1 net changed")
    need(carrier.get(("JIN1", "2"), {}).get("net") == "ACT_0V_PE_BONDED", "JIN1.2 net changed")
    need(carrier.get(("JOUT1", "1"), {}).get("net") == "BRANCH_LIMITED_OUT", "JOUT1.1 net changed")
    need(carrier.get(("JOUT1", "2"), {}).get("net") == "ACT_0V_PE_BONDED", "JOUT1.2 net changed")
    carrier_bom = {r["reference"]: r for r in read_csv(SOURCES["electrical/kicad/hr-v0-dxl-protection-carrier-p0.3/bom.csv"])}
    need(carrier_bom.get("JIN1", {}).get("manufacturer_part_number") == "B2P-VH" and carrier_bom.get("JOUT1", {}).get("manufacturer_part_number") == "B2P-VH", "carrier headers changed")

    star = read_csv(SOURCES["electrical/kicad/hr-v0-dxl-star/connector-schedule.csv"])
    for ref, net in (("JP1", "J1_VDD"), ("JP2", "J2_VDD"), ("JP3", "J3_VDD")):
        need(any(r["reference"] == ref and r["terminal"] == "1" and r["net"] == net for r in star), f"{ref}.1 mapping changed")
        need(any(r["reference"] == ref and r["terminal"] == "2" and r["net"] == "ACT_0V_PE_BONDED" for r in star), f"{ref}.2 mapping changed")

    sources = read_csv(OUT / "primary-source-register.csv")
    need(len(sources) == 4 and all(r["url"].startswith("https://") and "accessed 2026-08-09" in r["revision_or_date"] for r in sources), "source register incomplete")
    need(any("AWG 22 to 18" in r["controlled_fact"] and "strip length" in r["not_proved"] for r in sources), "JST evidence boundary missing")
    need(any("9918 002100" in r["controlled_fact"] and "9918 010100" in r["controlled_fact"] for r in sources), "Belden exact color identities missing")

    bom = read_csv(OUT / "harness-bom.csv")
    need(len(bom) == 7 and {r["manufacturer_part_number"] for r in bom[:5]} >= {"VHR-2N", "SVH-21T-P1.1", "9918 002100", "9918 010100"}, "harness candidate BOM changed")
    need(sum(r["status"] == "SELECTION REQUIRED" for r in bom) == 2, "two BOM rows must remain selection required")
    interfaces = read_csv(OUT / "interface-control.csv")
    need(len(interfaces) == 8 and {r["harness_id"] for r in interfaces} == {"HAR-CIN", "HAR-COUT"}, "interface membership changed")
    for harness in ("HAR-CIN", "HAR-COUT"):
        end_b = [r for r in interfaces if r["harness_id"] == harness and r["end"] == "B"]
        need(any(r["cavity_or_terminal"] == "1" and "red" in r["conductor"] for r in end_b), f"{harness} positive mapping missing")
        need(any(r["cavity_or_terminal"] == "2" and "black" in r["conductor"] for r in end_b), f"{harness} return mapping missing")
    need(sum(r["population"] == "SELECTION REQUIRED" for r in interfaces) == 2, "HAR-CIN far end must remain unresolved")

    cuts = read_csv(OUT / "cut-crimp-schedule.csv")
    need(len(cuts) == 4 and all(r["cut_length_mm"] == "SELECTION REQUIRED" and r["status"] == "DO NOT CUT OR CRIMP" for r in cuts), "cut schedule must remain held")
    need(all(r["strip_length_end_a_mm"] == "SELECTION REQUIRED" and r["strip_length_end_b_mm"] == "SELECTION REQUIRED" for r in cuts), "strip lengths must remain unresolved")
    process = read_csv(OUT / "manufacturing-process.csv")
    need(len(process) == 10 and all(r["state"] == "NOT EXECUTED" and not r["evidence_uri"] for r in process), "manufacturing process must remain unexecuted")
    acceptance = read_csv(OUT / "acceptance-matrix.csv")
    need(len(acceptance) == 18 and all(r["execution_state"] == "NOT EXECUTED" and r["result"] == "OPEN" and not r["approver"] for r in acceptance), "acceptance matrix must remain open")
    unresolved = read_csv(OUT / "unresolved-selections.csv")
    need(len(unresolved) == 9 and all(r["state"] == "SELECTION REQUIRED" for r in unresolved), "nine selections must remain unresolved")
    need(any("post-carrier net naming" in r["topic"] for r in unresolved), "system-net revision hold missing")

    page = (OUT / "index.html").read_text(encoding="utf-8")
    for token in ("font:clamp(16px", "font-size:14px", "The plugs are known. The route is not.", "Do not cut, crimp, mate or power", "9</b>unresolved selections", "0</b>executed acceptance rows"):
        need(token in page, f"guide token missing: {token}")
    need(page.count("CHU-") == 9, "guide must display all unresolved selections")

    for name in ("primary-source-register.csv", "harness-bom.csv", "interface-control.csv", "cut-crimp-schedule.csv", "manufacturing-process.csv", "acceptance-matrix.csv", "unresolved-selections.csv", "package-status.json", "README.md"):
        need((ENG / name).read_bytes() == (OUT / name).read_bytes(), f"engineering/release mismatch: {name}")
    for directory in (ENG, OUT):
        manifest = read_csv(directory / "file-manifest.csv")
        actual = {path.relative_to(directory).as_posix() for path in directory.rglob("*") if path.is_file() and path.name != "file-manifest.csv"}
        need({r["path"] for r in manifest} == actual, f"manifest membership mismatch: {directory.name}")
        for row in manifest:
            path = directory / row["path"]
            need(row["sha256"] == sha256(path) and int(row["bytes"]) == path.stat().st_size, f"manifest mismatch: {directory.name}/{row['path']}")

    if failures:
        print("HR-V0-DXL-PROT-CARRIER-HARNESS-P0.1 check FAILED")
        for failure in failures:
            print("-", failure)
        return 1
    print("HR-V0-DXL-PROT-CARRIER-HARNESS-P0.1 PASS")
    print("  exact carrier-side JST/Belden candidates; route/crimp/source end remain held")
    print("  18 acceptance rows OPEN; no cut/crimp/assembly/connection/energization authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
