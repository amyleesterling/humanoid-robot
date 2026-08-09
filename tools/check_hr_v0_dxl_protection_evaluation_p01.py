from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release" / "hr-v0" / "dxl-protection-evaluation-p0.1"
KICAD = ROOT / "electrical" / "kicad" / "hr-v0-dxl-protection-eval"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, MOTION, OR ENERGIZATION"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def verify_manifest(base: Path, name: str) -> bool:
    recorded = {row["file"]: (row["sha256"], int(row["size_bytes"])) for row in rows(base / name)}
    actual = {
        path.relative_to(base).as_posix(): (digest(path), path.stat().st_size)
        for path in base.rglob("*") if path.is_file() and path.name != name
    }
    return recorded == actual


def main() -> int:
    errors: list[str] = []

    def need(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    expected = {
        "README.md", "acceptance-matrix.csv", "calculation-register.csv",
        "candidate-decision-register.csv", "file-manifest.csv", "index.html",
        "package-status.json", "primary-source-register.csv", "residual-holds.csv",
        "system-interface-map.csv", "test-data-template.csv", "test-plan.csv",
    }
    actual = {path.name for path in OUT.iterdir() if path.is_file()}
    need(actual == expected, f"release membership changed: {sorted(actual ^ expected)}")

    status = json.loads((OUT / "package-status.json").read_text(encoding="utf-8"))
    need(status.get("identifier") == "HR-V0-DXL-PROT-EVAL-P0.1", "identifier changed")
    need(status.get("round") == "R155", "round changed")
    need(status.get("warning") == WARNING, "warning changed")
    for key, expected_value in {
        "native_kicad_sheets": 5, "exact_evaluation_devices": 2,
        "open_holds": 18, "physical_tests_executed": 0,
    }.items():
        need(status.get(key) == expected_value, f"status count changed: {key}")
    for key in (
        "selected_for_robot", "external_current_limit_released", "pcb_released",
        "procurement_authorized", "fabrication_authorized", "assembly_authorized",
        "connection_authorized", "motion_authorized", "energization_authorized", "safety_credit",
    ):
        need(status.get(key) is False, f"fail-closed flag changed: {key}")

    sheets = list(KICAD.glob("*.kicad_sch"))
    need(len(sheets) == 5, f"native sheet count changed: {len(sheets)}")
    erc = (KICAD / "validation" / "hr-v0-dxl-protection-eval-erc.rpt").read_text(encoding="utf-8")
    need("ERC messages: 0  Errors 0  Warnings 0" in erc, "native ERC is not 0/0")
    need((KICAD / "output" / "hr-v0-dxl-protection-eval-preliminary.pdf").is_file(), "native PDF export missing")
    need(len(list((KICAD / "output").glob("*.svg"))) == 5, "native SVG export count changed")

    bom = rows(KICAD / "bom.csv")
    refs = {row["reference"]: row for row in bom}
    need(len(bom) == 47 and sum(int(row["quantity"]) for row in bom) == 44, "KiCad BOM count changed")
    for index in (1, 2, 3):
        need(refs.get(f"U{index}", {}).get("value") == "TI TPS259461LRPWR latch-off bidirectional-on-state eFuse", f"U{index} exact candidate changed")
        need(refs.get(f"U{index}G", {}).get("quantity") == "0", f"U{index} GND cross-reference became a BOM device")
        need("JST B2P-VH" in refs.get(f"JIN{index}", {}).get("value", ""), f"JIN{index} family changed")
    need(refs.get("SH1", {}).get("value") == "Pololu item 3771 13.2 V 1.50 Ohm 15 W shunt regulator", "shunt candidate changed")
    terminals = rows(KICAD / "terminal-schedule.csv")
    need(len(terminals) == 104, "terminal count changed")
    need(any(row["reference"] == "U1" and row["terminal"] == "10" and row["net"] == "INTENTIONALLY_OPEN_B1_ITIMER" for row in terminals), "ITIMER deliberate-open allocation changed")

    decisions = {row["decision_id"]: row for row in rows(OUT / "candidate-decision-register.csv")}
    need(len(decisions) == 5, "decision count changed")
    need(decisions.get("DEC-002", {}).get("disposition") == "REJECT FOR CURRENT REGENERATIVE PATH", "reverse-blocking option disposition changed")
    need(decisions.get("DEC-005", {}).get("disposition") == "NO CHANGE", "robot baseline changed")
    need("reverse current is not limited" in decisions.get("DEC-001", {}).get("remaining_boundary", "").lower(), "forward-only limitation missing")

    calculations = {row["calculation_id"]: row for row in rows(OUT / "calculation-register.csv")}
    need(len(calculations) == 10, "calculation count changed")
    exact_calculations = {
        "CAL-001": ("1.782178", "2.222222", "A"),
        "CAL-002": ("0.841584", "1.161616", "A"),
        "CAL-005": ("12.804000", "13.596000", "V"),
        "CAL-008": ("0.084000", "", "V"),
        "CAL-009": ("8.800000", "", "A"),
        "CAL-010": ("116.160000", "", "W"),
    }
    for key, (minimum, maximum, unit) in exact_calculations.items():
        row = calculations.get(key, {})
        need((row.get("minimum"), row.get("maximum"), row.get("unit")) == (minimum, maximum, unit), f"calculation changed: {key}")

    sources = rows(OUT / "primary-source-register.csv")
    need(len(sources) == 7, "primary-source count changed")
    urls = {row["url"] for row in sources}
    for url in (
        "https://www.ti.com/lit/ds/symlink/tps25946.pdf",
        "https://www.ti.com/product/TPS25946/part-details/TPS259461LRPWR",
        "https://www.pololu.com/product/3771",
        "https://www.meanwell.com/Upload/PDF/GST280A/GST280A-SPEC.PDF",
        "https://www.jst-mfg.com/product/pdf/eng/eEH.pdf",
        "https://www.jst-mfg.com/product/pdf/eng/eVH.pdf",
    ):
        need(url in urls, f"primary source missing: {url}")

    tests = rows(OUT / "test-plan.csv")
    evidence = rows(OUT / "test-data-template.csv")
    acceptance = rows(OUT / "acceptance-matrix.csv")
    holds = rows(OUT / "residual-holds.csv")
    need(len(tests) == len(evidence) == 14, "physical test row count changed")
    need(all(row["result"] == "NOT EXECUTED" and row["authorization"] == "NOT AUTHORIZED" for row in tests), "test execution or authorization inferred")
    need(all(row["result"] == "NOT EXECUTED" and not row["data_uri"] for row in evidence), "physical evidence inferred")
    need(len(acceptance) == len(holds) == 18, "acceptance/hold count changed")
    need(all(row["result"] == "NOT EXECUTED" and not row["evidence_uri"] and not row["approver"] for row in acceptance), "acceptance evidence inferred")
    need(all(row["state"] == "OPEN" and row["warning"] == WARNING for row in holds), "a hold closed or lost its warning")

    config = json.loads((ROOT / "firmware" / "supervisor" / "actuator-config.json").read_text(encoding="utf-8"))
    need(config.get("external_branch_current_limit_a") == "SELECTION REQUIRED", "firmware external branch limit was released")
    need(config.get("current_envelope_binding", {}).get("release_state") == "CANDIDATE-NOT-RELEASED", "firmware current-envelope hold changed")
    system_bom = (ROOT / "bom" / "hr-v0-bom-closure.csv").read_text(encoding="utf-8")
    need("TPS259461LRPWR" not in system_bom and "Pololu item 3771" not in system_bom, "evaluation candidate entered robot BOM")
    release_candidate = json.loads((ROOT / "release" / "hr-v0" / "release-candidate.json").read_text(encoding="utf-8"))
    electrical_product = next((row for row in release_candidate.get("current_products", []) if row.get("domain") == "electrical"), {})
    need(electrical_product.get("identifier") == "Project Button Electrical V3-P1.14", "main electrical revision changed")

    page = (OUT / "index.html").read_text(encoding="utf-8")
    for token in (
        WARNING, "The decisive limitation", "Eighteen holds remain open",
        "font:clamp(16px", "font-size:14px", "overflow:auto", "<iframe",
    ):
        need(token in page, f"interactive guide content/style missing: {token}")
    need(page.count("data-src=") == 4, "diagram tab count changed")
    need(not re.search(r"font-size\s*:\s*(?:[0-9]|1[01])px", page), "interactive guide contains text below 12 px")

    need(verify_manifest(OUT, "file-manifest.csv"), "release manifest stale or incomplete")
    need(verify_manifest(KICAD, "SOURCE-MANIFEST.csv"), "KiCad source manifest stale or incomplete")

    if errors:
        print("HR-V0 DXL protection evaluation P0.1 check failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("HR-V0-DXL-PROT-EVAL-P0.1 PASS: 5 native sheets / ERC 0/0 / 14 blank tests / 18 holds OPEN")
    print("Three TPS259461LRPWR branch candidates plus Pololu 3771 shunt remain evaluation-only; reverse current is unbounded by the eFuse")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
