"""Fail-closed checks for the current HR-V0 Boston fabrication sourcing boundary."""

from __future__ import annotations

import csv
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "hr-v0-fabrication-sourcing-boston.md"
HISTORICAL = ROOT / "docs" / "hr-v0-flat-plate-manufacturing-p0.1.md"
REGISTER = ROOT / "cad" / "hr-v0" / "manufacturing" / "hr-v0-r57-fabrication-route-register.csv"
FORM = ROOT / "tests" / "forms" / "hr-v0-r57-fabrication-inquiry-template.csv"

WARNING = "PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    errors: list[str] = []
    doc = DOC.read_text(encoding="utf-8")
    historical = HISTORICAL.read_text(encoding="utf-8")
    routes = read_csv(REGISTER)
    forms = read_csv(FORM)

    for required in (
        "HR-V0-ARM-ARCH-P0.4",
        "four identical `MV0-C01`",
        "Artisans Asylum",
        "no current profile-only upload artifact exists",
        "100 g foam-object payload",
    ):
        if required not in doc:
            errors.append(f"current sourcing document omits: {required}")

    if "must not be quoted, cut, or uploaded" not in doc:
        errors.append("current sourcing document does not fail closed on withdrawn geometry")
    if "WITHDRAWN BY R53" not in historical:
        errors.append("historical flat-plate document lacks the R53 withdrawal banner")

    expected_ids = {f"R57-FAB-{index:03d}" for index in range(1, 9)}
    actual_ids = {row.get("route_id", "") for row in routes}
    if len(routes) != 8 or actual_ids != expected_ids:
        errors.append(f"expected exactly R57-FAB-001..008, found {sorted(actual_ids)}")

    for row in routes:
        route_id = row.get("route_id", "UNKNOWN")
        if row.get("warning") != WARNING:
            errors.append(f"{route_id} lacks the exact preliminary warning")
        state = row.get("release_state", "")
        if not (state.startswith("HOLD") or state in {"SITE HOLD", "EXCLUDED FROM PRIMARY STRUCTURAL LOAD PATH"}):
            errors.append(f"{route_id} has non-fail-closed release state {state!r}")
        if "authorization" in row.get("allowed_current_action", "").lower():
            errors.append(f"{route_id} allowed action could be read as work authorization")

    route_3 = next((row for row in routes if row.get("route_id") == "R57-FAB-003"), {})
    combined_3 = " ".join(route_3.values()).lower()
    for required in ("no upload artifact", "without holes or countersinks", "secondary"):
        if required not in combined_3:
            errors.append(f"R57-FAB-003 omits profile-route control: {required}")

    expected_form_ids = {f"R57-FAB-{index:03d}" for index in range(1, 8)}
    actual_form_ids = {row.get("route_id", "") for row in forms}
    if len(forms) != 7 or actual_form_ids != expected_form_ids:
        errors.append(f"inquiry form expected R57-FAB-001..007, found {sorted(actual_form_ids)}")
    for row in forms:
        route_id = row.get("route_id", "UNKNOWN")
        if row.get("record_id") != "NOT-EXECUTED" or row.get("status") != "NOT EXECUTED":
            errors.append(f"{route_id} contains executed-looking inquiry evidence")
        if row.get("warning") != WARNING:
            errors.append(f"{route_id} inquiry row lacks the exact preliminary warning")
        if row.get(None):
            errors.append(f"{route_id} inquiry row has extra CSV fields")

    if errors:
        print("HR-V0 R57 fabrication-sourcing check FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print("HR-V0 R57 fabrication-sourcing check passed: 8 held routes; 7 unexecuted inquiry rows")
    print("No withdrawn geometry, supplier selection, upload artifact, first article, or fabrication release is active")
    print(WARNING)
    return 0


if __name__ == "__main__":
    sys.exit(main())
