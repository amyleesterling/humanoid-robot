#!/usr/bin/env python3
"""Fail-closed checker for HR-V0-ELBOW-TRADE-P0.1."""
from __future__ import annotations

import csv
import hashlib
import json
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "release" / "hr-v0" / "elbow-actuator-trade-p0.1"
VENDOR = ROOT / "cad" / "vendor" / "robotis" / "x430-fr12-r91"


def rows(name: str) -> list[dict[str, str]]:
    with (PKG / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    errors: list[str] = []
    status = json.loads((PKG / "package-status.json").read_text(encoding="utf-8"))
    trade = rows("trade-study.csv")
    sources = rows("source-register.csv")
    files = rows("vendor-file-register.csv")
    holds = rows("architecture-holds.csv")

    if len(trade) != 4 or len(sources) != 6 or len(files) != 5 or len(holds) != 12:
        errors.append("controlled package counts changed")
    if status.get("p0_7_remains_controlled") is not True or status.get("xm430_elbow_selected") is not False:
        errors.append("configuration/supersession boundary changed")
    authorization_keys = [k for k in status if k.endswith("_authorized")]
    if not authorization_keys or any(status[k] is not False for k in authorization_keys):
        errors.append("an authorization flag is missing or not false")
    if any(row["state"] != "OPEN" for row in holds):
        errors.append("an architecture hold is not OPEN")

    expected = {
        "ELB-01": (Decimal("692.758"), Decimal("57.242"), Decimal("11.100")),
        "ELB-02": (Decimal("634.775"), Decimal("115.225"), Decimal("11.100")),
        "ELB-03": (Decimal("609.758"), Decimal("140.242"), Decimal("9.000")),
        "ELB-04": (Decimal("551.775"), Decimal("198.225"), Decimal("9.000")),
    }
    for row in trade:
        key = row["option_id"]
        actual = tuple(Decimal(row[name]) for name in ("incomplete_known_mass_g", "headroom_to_750_g", "total_three_actuator_catalog_stall_current_a"))
        if expected.get(key) != actual:
            errors.append(f"trade arithmetic changed for {key}: {actual}")
        if Decimal(row["incomplete_known_mass_g"]) + Decimal(row["headroom_to_750_g"]) != Decimal("750.000"):
            errors.append(f"mass/headroom does not close to 750 g for {key}")
    if Decimal(trade[2]["j2_actuator_mass_g"]) - Decimal(trade[0]["j2_actuator_mass_g"]) != Decimal("-83.000"):
        errors.append("X430 actuator mass sensitivity is not -83 g")

    for row in files:
        path = ROOT / row["local_path"]
        if not path.is_file():
            errors.append(f"missing vendor file {path}")
            continue
        if path.stat().st_size != int(row["bytes"]) or sha256(path) != row["sha256"]:
            errors.append(f"vendor file identity mismatch: {path.name}")
        if path.suffix.lower() == ".stp" and not path.read_bytes().startswith(b"ISO-10303-21;"):
            errors.append(f"vendor STEP header invalid: {path.name}")
        if path.suffix.lower() == ".pdf" and not path.read_bytes().startswith(b"%PDF-"):
            errors.append(f"vendor PDF header invalid: {path.name}")

    html = (PKG / "index.html").read_text(encoding="utf-8")
    doc = (ROOT / "docs" / "hr-v0-elbow-actuator-trade-p0.1.md").read_text(encoding="utf-8")
    for token in ("57.242", "115.225", "140.242", "198.225", "stall-endpoint ratio", "P0.7 remains"):
        if token not in html or token not in doc:
            errors.append(f"controlled explanatory token missing: {token}")
    for unsafe in ("approved for energization", "XM430 is selected", "continuous torque margin"):
        if unsafe.lower() in (html + doc).lower():
            errors.append(f"unsafe release claim present: {unsafe}")
    if "font:17px" not in html or "font-size:13px" not in html:
        errors.append("interactive text-size floor changed")

    if errors:
        print("HR-V0 elbow actuator trade check: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("HR-V0 elbow actuator trade check: PASS")
    print("4 options; 6 primary sources; 5 hash-controlled vendor files; 12 open holds; all authorization flags false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
