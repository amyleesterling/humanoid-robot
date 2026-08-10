#!/usr/bin/env python3
"""Check the R189 clean-clone reproducibility evidence package."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "configuration/hr-v0-clean-clone-audit-p0.1"
WARNING = "PRELIMINARY - CONFIGURATION EVIDENCE ONLY - NOT APPROVED FOR PROCUREMENT, FABRICATION, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def main() -> None:
    summary = json.loads((OUT / "audit-summary.json").read_text(encoding="utf-8"))
    with (OUT / "failure-disposition.csv").open(encoding="utf-8", newline="") as handle:
        attempts = list(csv.DictReader(handle))

    assert summary["schema"] == "project-button-hr-v0-clean-clone-audit-p0.1"
    assert summary["status"] == WARNING
    assert summary["audited_source_commit"] == "221035ed307f4e3501abad82cf7afa42f6e7cc36"
    final = summary["final_result"]
    assert final["checker_count"] == 145
    assert final["non_pcbnew_pass"] == final["non_pcbnew_total"] == 132
    assert final["pcbnew_pass"] == final["pcbnew_total"] == 13
    assert final["failure_count"] == 0
    assert final["clone_clean_after_execution"] is True
    assert final["release_manifest_file_count"] == 3206
    assert final["release_manifest_require_clean_pass"] is True
    assert summary["gate_effect"]["gate_id"] == "EG-002"
    assert summary["gate_effect"]["closed"] is False
    assert summary["physical_evidence_created"] is False
    assert summary["energization_authority"] is False

    assert len(attempts) == 4
    assert [row["passed"] for row in attempts] == ["112", "99", "144", "145"]
    assert [row["failed"] for row in attempts] == ["33", "46", "1", "0"]
    assert all(row["authority"] == "NONE" for row in attempts)

    attrs = (ROOT / ".gitattributes").read_text(encoding="utf-8")
    block = attrs.split("# BEGIN GENERATED CHECKOUT EOL CONTRACT", 1)[1].split("# END GENERATED CHECKOUT EOL CONTRACT", 1)[0]
    assert "# 989 exact CRLF paths" in block
    assert "# 5 exact mixed-EOL paths" in block
    assert block.count(" text eol=crlf") == 989
    assert block.count(" -text") == 5

    synthetic = ROOT / "analysis/hr-v0/dynamic-trace-p0.2/synthetic"
    for result_path in sorted(synthetic.glob("*result.json")):
        result = json.loads(result_path.read_text(encoding="utf-8"))
        assert result["trace"].startswith("analysis/hr-v0/dynamic-trace-p0.2/synthetic/")
        assert result["config"].startswith("analysis/hr-v0/dynamic-trace-p0.2/synthetic/")
        assert ":/Users/" not in result["trace"] and ":/Users/" not in result["config"]

    analyzer = (ROOT / "tools/analyze_hr_v0_dynamic_trace_p02.py").read_text(encoding="utf-8")
    assert "def repository_path" in analyzer and "relative_to(ROOT)" in analyzer
    for doc in (
        ROOT / "docs/hr-v0-clean-clone-audit-p0.1.md",
        ROOT / "docs/reviews/2026-08-10-r189-validation-record.md",
        ROOT / "docs/reviews/2026-08-10-r189-independent-review-request.md",
        ROOT / "docs/reviews/2026-08-10-sol-r12-post-r189-status.md",
    ):
        text = doc.read_text(encoding="utf-8")
        assert "PRELIMINARY" in text and "ENERGIZATION" in text

    print("PASS: R189 clean-clone reproducibility evidence")
    print("145/145 audited checks; source commit 221035ed307f4e3501abad82cf7afa42f6e7cc36")
    print("EG-002 REMAINS PARTIAL; NO PHYSICAL OR ENERGIZATION AUTHORITY")


if __name__ == "__main__":
    main()
