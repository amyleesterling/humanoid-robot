"""Fail-closed validation for HR-V0-STOP-REGION-P0.1."""

from __future__ import annotations

import csv
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "cad" / "hr-v0" / "generated" / "stop-region-clearance-p0.1"
REVISION = "HR-V0-STOP-REGION-P0.1"
EXPECTED_FILES = {
    "HR-V0_stop-region-acquisition.svg",
    "HR-V0_stop-region-guide.html",
    "stop-interface-measurement-register.csv",
    "stop-region-clearance-analysis.json",
    "stop-region-clearance-samples.csv",
    "stop-region-continuous-cells.csv",
    "stop-region-continuous-summary.csv",
    "stop-topology-decision-register.csv",
}


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    errors: list[str] = []
    if not OUT.is_dir():
        errors.append("output directory is absent")
    elif {path.name for path in OUT.iterdir() if path.is_file()} != EXPECTED_FILES:
        errors.append("artifact membership changed")

    if not errors:
        analysis = json.loads((OUT / "stop-region-clearance-analysis.json").read_text(encoding="utf-8"))
        if analysis.get("revision") != REVISION or analysis.get("parent_arm_revision") != "HR-V0-ARM-ARCH-P0.7":
            errors.append("revision or parent binding changed")
        if analysis.get("sample_increment_deg") != 0.5 or analysis.get("sample_count") != 6411:
            errors.append("sample schedule changed")
        if analysis.get("maximum_sampled_intersection_mm3") != 0.0:
            errors.append("a nominal collision exists in a stop-region sample")
        if analysis.get("continuous_certificate_count") != 131 or analysis.get("continuous_leaf_cell_count") != 133:
            errors.append("continuous certificate coverage changed")
        if analysis.get("minimum_guaranteed_clearance_mm") != 5.743912 or analysis.get("required_guaranteed_clearance_mm") != 0.75:
            errors.append("continuous clearance result or acceptance floor changed")
        if analysis.get("measurement_inputs_open") != 20 or analysis.get("stop_topology_selected") is not False:
            errors.append("physical-input hold or topology-selection boundary changed")
        if "does not select" not in analysis.get("interpretation", "") or "PHYSICAL INTERFACE ACQUISITION" not in analysis.get("status", ""):
            errors.append("nominal-only interpretation was weakened")

        samples = rows("stop-region-clearance-samples.csv")
        if len(samples) != 6411:
            errors.append("sample-row count changed")
        region_counts = {
            region: sum(row.get("region") == region for row in samples)
            for region in ("J1_MIN_REGION", "J1_MAX_REGION", "J2_MIN_REGION")
        }
        if region_counts != {"J1_MIN_REGION": 2100, "J1_MAX_REGION": 2100, "J2_MIN_REGION": 2211}:
            errors.append("stop-region sample coverage changed")
        if any(row.get("result") != "PASS_NOMINAL" or float(row.get("sampled_pairwise_intersection_mm3", "1")) > 1e-5 for row in samples):
            errors.append("sample screen contains a collision or non-pass result")
        if any("cables, guards, tolerances" not in row.get("scope", "") for row in samples):
            errors.append("sample scope lost its physical-evidence exclusions")

        summaries = rows("stop-region-continuous-summary.csv")
        cells = rows("stop-region-continuous-cells.csv")
        if len(summaries) != 131 or len(cells) != 133:
            errors.append("continuous summary/cell count changed")
        if any(float(row.get("minimum_guaranteed_clearance_mm", "0")) < 0.75 for row in summaries):
            errors.append("continuous summary falls below the nominal floor")
        if any(float(row.get("guaranteed_clearance_mm", "0")) < 0.75 for row in cells):
            errors.append("continuous leaf cell falls below the nominal floor")
        prefixes = {row.get("pair_id", "").split(":", 1)[0] for row in summaries}
        if prefixes != {"J1_MIN_REGION", "J1_MAX_REGION", "J2_MIN_REGION"}:
            errors.append("continuous certificate lost a stop region")

        measurements = rows("stop-interface-measurement-register.csv")
        if len(measurements) != 20 or [row.get("measurement_id") for row in measurements] != [f"HSI-{index:03d}" for index in range(1, 21)]:
            errors.append("physical-input register membership changed")
        if any(row.get("status") != "OPEN" or row.get("value") != "NOT EXECUTED" for row in measurements):
            errors.append("physical-input record was promoted without evidence")
        if any("NO STOP OR MOTION RELEASE" not in row.get("warning", "") for row in measurements):
            errors.append("physical-input warning changed")

        topologies = rows("stop-topology-decision-register.csv")
        if len(topologies) != 5 or [row.get("topology_id") for row in topologies] != [f"HST-{index:03d}" for index in range(1, 6)]:
            errors.append("topology register membership changed")
        if [row.get("disposition") for row in topologies] != [
            "CANDIDATE ROUTE - NOT SELECTED",
            "CANDIDATE ROUTE - NOT SELECTED",
            "CANDIDATE ROUTE - NOT SELECTED",
            "REJECTED",
            "REJECTED",
        ]:
            errors.append("a stop topology was selected or a prohibited route was restored")

        try:
            root = ET.parse(OUT / "HR-V0_stop-region-acquisition.svg").getroot()
            text = " ".join(node.text or "" for node in root.iter() if node.tag.endswith("text"))
            for token in (REVISION, "What the nominal CAD now establishes", "What remains physically unknown", "No topology or stop angle is released", "Do not order, fabricate, connect, move or energize"):
                if token not in text:
                    errors.append(f"readable SVG omits {token}")
            style = " ".join(node.text or "" for node in root.iter() if node.tag.endswith("style"))
            if "font-size:18px" not in style or "font-size:36px" not in style:
                errors.append("readable SVG lost its 18 px body-text control")
        except ET.ParseError as exc:
            errors.append(f"readable SVG does not parse: {exc}")

        html = (OUT / "HR-V0_stop-region-guide.html").read_text(encoding="utf-8")
        for token in (REVISION, "6,411 sampled boundary poses", "131 continuous pair-region certificates", "20 physical inputs still open", "font:clamp(16px", "data-filter=\"ATTACHMENT\""):
            if token not in html:
                errors.append(f"interactive guide omits {token}")

    if errors:
        print("HR-V0 stop-region clearance validation: FAIL", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("HR-V0 stop-region clearance validation: PASS")
    print("6,411 sampled poses; 131 continuous certificates; 5.743912 mm conservative nominal floor; 20 received/interface inputs remain open")
    print("PRELIMINARY - NOMINAL CAD EVIDENCE ONLY - NO STOP, FABRICATION, MOTION OR ENERGIZATION RELEASE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
