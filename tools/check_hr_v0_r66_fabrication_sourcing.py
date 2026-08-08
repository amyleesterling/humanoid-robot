"""Fail-closed checks for the R69 Boston fabrication-sourcing boundary."""

from __future__ import annotations

import csv
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "hr-v0-fabrication-sourcing-boston.md"
REGISTER = ROOT / "cad" / "hr-v0" / "manufacturing" / "hr-v0-r69-fabrication-route-register.csv"
FORM = ROOT / "tests" / "forms" / "hr-v0-r69-fabrication-inquiry-template.csv"
WARNING = "PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    errors: list[str] = []
    doc = DOC.read_text(encoding="utf-8")
    routes = rows(REGISTER)
    forms = rows(FORM)
    for token in ("HR-V0-FAB-SRC-P0.5", "HR-V0-ARM-ARCH-P0.7", "one `MV0-C01`", "one H104-specific `MV0-C04`", "one `MV0-C05`", "one `MV0-C06`", "one `MV0-C07`", "no current profile-only upload artifact exists", "100 g foam-object payload", "Do not upload, quote, order or substitute 4.75 mm stock", "SendCutSend is therefore excluded as a finished-part route", "Bridgeport CNC mill"):
        if token not in doc:
            errors.append(f"sourcing document omits {token}")
    expected_routes = [f"R69-FAB-{index:03d}" for index in range(1, 13)]
    if [row.get("route_id") for row in routes] != expected_routes:
        errors.append("route register is not exactly R69-FAB-001 through 012")
    for row in routes:
        if row.get("warning") != WARNING:
            errors.append(f"{row.get('route_id')} warning changed")
        state = row.get("release_state", "")
        if not (state.startswith("HOLD") or state in {"SITE HOLD", "EXCLUDED FROM PRIMARY STRUCTURAL LOAD PATH"}):
            errors.append(f"{row.get('route_id')} is not fail-closed")
    sendcutsend = next((row for row in routes if row.get("route_id") == "R69-FAB-007"), {})
    sendcutsend_text = " ".join(sendcutsend.values())
    for token in ("9.53 mm", "+/-0.381 mm", "10 mm M5 countersink", "direct finished-part route excluded"):
        if token not in sendcutsend_text:
            errors.append(f"R69-FAB-007 omits corrected control: {token}")
    artisans = next((row for row in routes if row.get("route_id") == "R69-FAB-008"), {})
    if "Bridgeport CNC mill" not in " ".join(artisans.values()) or "APPLICATION CAPABILITY UNVERIFIED" not in artisans.get("release_state", ""):
        errors.append("R69-FAB-008 does not preserve the verified-machine / unverified-application boundary")
    if [row.get("route_id") for row in forms] != expected_routes[:11]:
        errors.append("inquiry template is not exactly R69-FAB-001 through 011")
    for row in forms:
        if row.get("record_id") != "NOT-EXECUTED" or row.get("status") != "NOT EXECUTED" or row.get("warning") != WARNING or row.get(None):
            errors.append(f"{row.get('route_id')} contains executed, malformed, or unbounded evidence")
    if errors:
        print("HR-V0 R66 fabrication-sourcing check FAILED", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("HR-V0 R69 fabrication-sourcing check passed: 12 held/excluded routes; 11 unexecuted inquiry rows")
    print("No supplier selection, upload artifact, quote, first article, or fabrication release is active")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
