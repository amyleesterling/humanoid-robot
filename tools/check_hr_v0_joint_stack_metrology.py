"""Fail-closed validation for HR-V0-JOINT-MET-P0.1."""

from __future__ import annotations

import csv
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "test-fixtures" / "hr-v0" / "joint-stack-metrology-p0.1"
FORM = ROOT / "tests" / "forms" / "hr-v0-joint-stack-metrology-template.csv"
REVISION = "HR-V0-JOINT-MET-P0.1"
EXPECTED = {"HR-V0_joint-stack-metrology-guide.html", "HR-V0_joint-stack-metrology.svg", "article-allocation.csv", "hold-point-register.csv", "hsi-trace.csv", "instrument-capability-register.csv", "operation-sequence.csv", "package-status.json", "source-register.csv"}


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    errors: list[str] = []
    if not OUT.is_dir() or {p.name for p in OUT.iterdir() if p.is_file()} != EXPECTED:
        errors.append("artifact directory is absent or membership changed")
    if not FORM.is_file():
        errors.append("raw record template is absent")
    if not errors:
        articles = rows(OUT / "article-allocation.csv")
        instruments = rows(OUT / "instrument-capability-register.csv")
        holds = rows(OUT / "hold-point-register.csv")
        operations = rows(OUT / "operation-sequence.csv")
        hsi = rows(OUT / "hsi-trace.csv")
        sources = rows(OUT / "source-register.csv")
        form = rows(FORM)
        status = json.loads((OUT / "package-status.json").read_text(encoding="utf-8"))
        if len(articles) != 6 or [r["article_id"] for r in articles] != [f"JSM-ART-{i:03d}" for i in range(1, 7)]:
            errors.append("six-article J1/J2 allocation changed")
        if sum("XM540-W270-T" in r["exact_identity"] for r in articles) != 2 or sum("FR13-H101K" in r["exact_identity"] for r in articles) != 2 or sum("FR13-S102K" in r["exact_identity"] for r in articles) != 2:
            errors.append("exact two-actuator/two-H101/two-S102 allocation changed")
        if not all("PROGRAM OWNER APPROVAL REQUIRED" in r["initial_state"] for r in articles):
            errors.append("article purchase hold weakened")
        if not all("HNX540-C101" in r["substitution_rule"] for r in articles if "H101K" in r["exact_identity"]):
            errors.append("incompatible clamping-horn substitution exclusion changed")
        if len(instruments) != 6 or instruments[4]["status"] != "HARD HOLD" or "No numeric torque" not in instruments[4]["provisional_screening_capability"]:
            errors.append("instrument controls or torque hold changed")
        if len(holds) != 8 or any(r["state"] != "OPEN" for r in holds):
            errors.append("eight open hold points changed")
        if len(operations) != 18 or [r["operation_id"] for r in operations] != [f"JSM-OP-{i:03d}" for i in range(1, 19)]:
            errors.append("operation sequence changed")
        if operations[1]["state"] != "NOT AUTHORIZED" or operations[8]["state"] != "NOT AUTHORIZED":
            errors.append("purchase or temporary assembly was authorized")
        if "without reading or inferring encoder" not in operations[11]["action"]:
            errors.append("unpowered encoder boundary changed")
        if len(hsi) != 20 or [r["hsi"] for r in hsi] != [f"HSI-{i:03d}" for i in range(1, 21)] or any(r["state"] != "OPEN - NOT EXECUTED" for r in hsi):
            errors.append("HSI trace membership or open state changed")
        if len(sources) != 5 or not all(r["revision_or_date"].endswith("2026-08-08") for r in sources[:4]):
            errors.append("primary-source register changed")
        if len(form) != 1 or form[0].get("record_id") != "NOT-EXECUTED" or form[0].get("disposition") != "NOT EXECUTED":
            errors.append("raw form was promoted without evidence")
        if status != {"revision": REVISION, "parent": "HR-V0-STOP-REGION-P0.1 / HR-V0-MECH-EVAL-P0.1", "article_count": 6, "instrument_count": 6, "hold_count": 8, "operation_count": 18, "hsi_count": 20, "hsi_closed": 0, "purchase_authorized": False, "temporary_assembly_authorized": False, "power_or_motion_authorized": False, "interpretation": "Executable staged evidence plan only. No physical article, measurement or accepted result exists.", "warning": "PRELIMINARY - UNPOWERED METROLOGY ONLY - NO PURCHASE, ASSEMBLY-USE, MOTION OR ENERGIZATION RELEASE"}:
            errors.append("package status or release boundary changed")
        try:
            root = ET.parse(OUT / "HR-V0_joint-stack-metrology.svg").getroot()
            text = " ".join(n.text or "" for n in root.iter() if n.tag.endswith("text"))
            for token in (REVISION, "Hard holds before assembly", "0 of 20 HSI rows closed", "Do not order, assemble for use, connect, power, move or energize"):
                if token not in text:
                    errors.append(f"SVG omits {token}")
            style = " ".join(n.text or "" for n in root.iter() if n.tag.endswith("style"))
            if "font-size:18px" not in style or "font-size:36px" not in style:
                errors.append("SVG legibility controls changed")
        except ET.ParseError as exc:
            errors.append(f"SVG does not parse: {exc}")
        html = (OUT / "HR-V0_joint-stack-metrology-guide.html").read_text(encoding="utf-8")
        for token in (REVISION, "18 sequenced operations", "eight hard holds", "font:clamp(16px", "data-filter=\"NO\""):
            if token not in html:
                errors.append(f"HTML omits {token}")
    if errors:
        print(f"{REVISION} validation: FAIL", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"{REVISION} validation: PASS")
    print("6 exact articles; 18 operations; 8 open hold points; 20 HSI routes; 0 physical results")
    print("PRELIMINARY - UNPOWERED METROLOGY ONLY - NO PURCHASE, ASSEMBLY-USE, MOTION OR ENERGIZATION RELEASE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
