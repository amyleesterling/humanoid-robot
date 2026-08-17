"""Validate HR-30 nonadjacent-link pose collision and clearance artifacts."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "hr30" / "whole-body-p0.1"
REL = ROOT / "release" / "hr30" / "whole-body-p0.1"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def rows(name: str) -> list[dict]:
    with (SRC / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    pairs = rows("whole-body-collision-register.csv")
    summaries = rows("pose-collision-summary.csv")
    exclusions = rows("collision-exclusion-register.csv")
    require(len(summaries) == 10 and len(pairs) == 2900, "bilateral pose collision coverage incomplete")
    require(len(exclusions) == 35 and all("INTERFACE" in row["scope"] for row in exclusions), "collision exclusions drift or hide validation scope")
    require(all(int(row["checked_pair_count"]) == 290 for row in summaries), "checked pair count drift")
    require(all(int(row["interference_count"]) == 0 and row["result"] == "ZERO COMMON-VOLUME INTERFERENCE" for row in summaries), "nominal pose interference remains")
    require(all(float(row["common_volume_mm3"]) <= 0.5 and row["interference"] == "NO" for row in pairs), "pair register contains common-volume interference")
    require(all(float(row["clearance_mm"]) >= 8.0 and row["planning_clearance_state"] == "PASS" for row in pairs), "8 mm whole-body nominal clearance screen not closed")
    require(all(int(row["below_5mm_pair_count"]) == 0 and float(row["minimum_clearance_mm"]) >= 8.0 for row in summaries), "pose-level clearance summary drift")
    require(sha(SRC / "collision-architecture-source.py") == sha(ROOT / "tools" / "generate_hr30_whole_body_collision_architecture_p01.py"), "collision generator snapshot drift")
    page = (SRC / "index.html").read_text(encoding="utf-8")
    walking = (SRC / "walking-development-architecture.md").read_text(encoding="utf-8")
    require(page.count('id="collision-clearance"') == 1 and "whole-body-collision-register.csv" in page, "interactive collision summary missing")
    require("## Nominal self-collision result" in walking, "walking collision boundary missing")
    hold = next(row for row in rows("open-holds.csv") if row["hold_id"] == "HR30-P01-H08")
    require("2,900 checked" in hold["unresolved_item"] and "physical correlation remain unverified" in hold["unresolved_item"], "H08 collision progress/boundary not synchronized")
    status = json.loads((SRC / "package-status.json").read_text(encoding="utf-8"))
    require(status["whole_body_nominal_self_collision_screen_present"] and status["whole_body_pose_common_volume_interference_count"] == 0, "collision package status incomplete")
    require(not any(status[key] for key in ("tolerance_aware_collision_validated", "cable_cover_sweep_validated", "physical_collision_validated", "motion_authority", "energization_authority")), "collision validation/authority overclaim")
    for name in ("whole-body-collision-register.csv", "pose-collision-summary.csv", "collision-exclusion-register.csv", "whole-body-collision-architecture.md"):
        require((REL / name).exists() and sha(SRC / name) == sha(REL / name), f"release collision artifact drift: {name}")
    minimum = min(float(row["minimum_clearance_mm"]) for row in summaries)
    print(f"PASS: ten bilateral HR-30 articulated poses screen 2,900 nonexcluded link pairs with zero nominal common-volume interference and {minimum:.2f} mm minimum clearance; tolerance, covers, cables, tracking error and physical correlation remain open with no motion/safety authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
