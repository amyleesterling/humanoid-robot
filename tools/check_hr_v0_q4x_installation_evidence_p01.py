#!/usr/bin/env python3
"""Validate the R186 Q4X installation-evidence and receiving package."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "test-equipment/hr-v0/q4x-installation-evidence-p0.1"
DOC = ROOT / "docs/hr-v0-q4x-installation-evidence-p0.1.md"
WEB = ROOT / "release/hr-v0/q4x-installation-evidence-p0.1"
FORM = ROOT / "tests/forms/hr-v0-q4x-hardware-receiving-template-p0.1.csv"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


checks: list[tuple[str, bool]] = []


def check(name: str, condition: bool) -> None:
    checks.append((name, condition))
    print(("PASS " if condition else "FAIL ") + name)


required = [
    PKG / "source-register.csv",
    PKG / "installation-evidence.csv",
    PKG / "receiving-lot.csv",
    PKG / "metrology-plan.csv",
    PKG / "closure-holds.csv",
    PKG / "vendor-file-hashes.csv",
    PKG / "package-status.json",
    DOC,
    WEB / "index.html",
    FORM,
]
for path in required:
    check(f"exists: {path.relative_to(ROOT)}", path.is_file())

sources = read_csv(PKG / "source-register.csv")
evidence = read_csv(PKG / "installation-evidence.csv")
lot = read_csv(PKG / "receiving-lot.csv")
plan = read_csv(PKG / "metrology-plan.csv")
holds = read_csv(PKG / "closure-holds.csv")
hashes = read_csv(PKG / "vendor-file-hashes.csv")
status = json.loads((PKG / "package-status.json").read_text(encoding="utf-8"))
doc = DOC.read_text(encoding="utf-8")
web = (WEB / "index.html").read_text(encoding="utf-8")

check("eight primary-source records", len(sources) == 8 and all(row["official_locator"].startswith("https://") for row in sources))
check("twelve installation-evidence rows", len(evidence) == 12)
check("manufacturer torque baseline", status["manufacturer_torque_baseline_Nm"] == 1.5 and any(row["manufacturer_value"] == "1.5 N m" for row in evidence))
check("separate locknut ambiguity retained", status["separate_locknut_torque_certificate_field"] == "blank" and any(row["disposition"] == "AMBIGUITY RETAINED" for row in evidence))
check("through-hole held", status["through_hole_diameter"] == "SELECTION REQUIRED" and any(row["parameter"] == "through-hole diameter and tolerance" and row["manufacturer_value"] == "SELECTION REQUIRED" for row in evidence))
check("ten exact receiving lines", len(lot) == 10 and status["receiving_lines"] == 10)
check("no purchase authority", all(row["purchase_authority"] == "NOT AUTHORIZED" for row in lot) and not status["procurement_authorized"])
check("no received article claims", all(row["receiving_state"] == "NOT RECEIVED" for row in lot))
check("ten blank metrology steps", len(plan) == 10 and status["metrology_steps"] == 10 and all(row["result"] == "NOT EXECUTED" for row in plan))
check("eleven open holds", len(holds) == 11 and status["open_holds"] == 11 and all(row["state"] == "OPEN" for row in holds))
check("official files hash-bound and not redistributed", len(hashes) == 2 and all(len(row["sha256"]) == 64 and row["redistributed"] == "no" for row in hashes))
check("zero physical authority", status["executed_physical_steps"] == 0 and not status["fabrication_authorized"] and not status["energization_authorized"])
check("document states zero gate closure", "closes no energization gate and no Sol R12 blocker" in doc)
check("web has four interactive views", all(f"data-tab='{tab}'" in web for tab in ("evidence", "lot", "plan", "holds")))
check("legible web type floors", "font:16px/1.55" in web and "font-size:14px" in web and "font-size:20px" in web)
check("web says zero released holes", "<strong>0</strong>released holes" in web)
check("warning preserved", all("NOT APPROVED" in path.read_text(encoding="utf-8", errors="ignore") for path in required if path.suffix.lower() in {".csv", ".json", ".md", ".html"}))

failed = [name for name, passed in checks if not passed]
print(f"summary: {len(checks) - len(failed)}/{len(checks)} passed")
if failed:
    raise SystemExit(1)
