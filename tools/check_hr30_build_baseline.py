#!/usr/bin/env python3
"""Read-only HR-30 source audit. No CAD regeneration, network, or hardware access.

The default verifies three small pinned files and performs planning arithmetic.
--full-assets also hashes nine existing assets; it does not validate their physics.
A successful exit never means build, powered-test, or walking approval.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
import re
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path

BODY = "hr30/whole-body-p0.1/"
LEG_TYPES = ("HIP_YAW", "HIP_ROLL", "HIP_PITCH", "KNEE_PITCH", "ANKLE_PITCH", "ANKLE_ROLL")
ARM_TYPES = ("SHOULDER_PITCH", "SHOULDER_ROLL", "ELBOW_PITCH", "WRIST_ROTATION")
ROTARY_AXES = {"HEAD_PAN", "HEAD_TILT", "WAIST_YAW"} | {
    f"{side}_{kind}" for side in ("L", "R") for kind in LEG_TYPES + ARM_TYPES
}
LEG_AXES = {f"{s}_{k}" for s in ("L", "R") for k in LEG_TYPES}
FALSE_FIELDS = ("physical_mass_validated", "continuous_capacity_validated", "free_balance_validated",
                "connection_authority", "powered_test_authority", "motion_authority",
                "walking_authority", "energization_authority")

class AuditError(ValueError):
    """Invalid, incomplete or stale planning evidence."""

def require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditError(message)

def number(value: object, label: str, positive: bool = False) -> float:
    require(not isinstance(value, bool), f"{label}: boolean is not a number")
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise AuditError(f"{label}: invalid number") from exc
    require(math.isfinite(result), f"{label}: non-finite number")
    require(result > 0 if positive else result >= 0, f"{label}: invalid sign/zero")
    return result

def unique_rows(rows: list[dict], label: str) -> dict[str, dict]:
    result = {}
    for row in rows:
        key = row.get("axis_id")
        require(isinstance(key, str) and bool(key), f"{label}: missing axis_id")
        require(key not in result, f"{label}: duplicate axis {key}")
        result[key] = row
    return result

def money(value: object) -> Decimal:
    require(isinstance(value, str), "Money must be a decimal string")
    try:
        result = Decimal(value)
    except InvalidOperation as exc:
        raise AuditError("Invalid money") from exc
    require(result.is_finite() and result >= 0, "Invalid money sign or non-finite value")
    require(result.as_tuple().exponent >= -2, "Money has more than two decimal places")
    return result

def budget_totals(budget: dict) -> dict:
    require(budget.get("schema_version") == 1, "Unsupported budget schema")
    require(budget.get("currency") == "USD", "Budget currency must be USD")
    require(budget.get("purchasing_authority") is False, "Budget is not a purchase approval")
    require(budget.get("state") == "PLANNING_ONLY_NOT_A_QUOTE_OR_SPENDING_APPROVAL", "Budget scope changed")
    require(bool(budget.get("catalog_items")) and bool(budget.get("allowances")), "Incomplete budget")
    catalog = Decimal(0)
    for row in budget["catalog_items"]:
        qty = row.get("quantity")
        require(type(qty) is int and qty > 0, "Invalid catalog quantity")
        require(bool(row.get("source")) and bool(row.get("hold")), "Catalog provenance/hold absent")
        catalog += qty * money(row["unit_usd"])
    low = high = Decimal(0)
    for row in budget["allowances"]:
        lo, hi = money(row["low_usd"]), money(row["high_usd"])
        require(lo <= hi and bool(row.get("basis")), "Invalid allowance range/basis")
        low += lo
        high += hi
    return {"catalog_subtotal_usd": str(catalog.quantize(Decimal(".01"))),
            "planning_low_usd": str((catalog + low).quantize(Decimal(".01"))),
            "planning_high_usd": str((catalog + high).quantize(Decimal(".01"))),
            "tax_shipping_included": False, "supplier_quote": False}

def verified_path(root: Path, entry: dict) -> Path:
    require(isinstance(entry.get("path"), str), "Missing source path")
    require(re.fullmatch(r"[0-9a-f]{64}", entry.get("sha256", "")) is not None, "Invalid hash")
    path = (root / entry["path"]).resolve()
    require(path.is_relative_to(root.resolve()), "Source path escapes root")
    require(path.is_file(), f"Missing source: {entry['path']}")
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    require(digest.hexdigest() == entry["sha256"], f"Source drift: {entry['path']}")
    return path

def analyze(status: dict, demand_rows: list[dict], allocation_rows: list[dict], lock: dict) -> dict:
    require(lock.get("schema_version") == 1, "Unsupported baseline schema")
    require(lock.get("state") == "RECONCILIATION_CANDIDATE_NOT_BUILD_RELEASE", "Release boundary changed")
    permissions = lock.get("permissions", {})
    require(set(permissions) == {"purchasing", "fabrication", "energization", "motion"} and all(v is False for v in permissions.values()), "Permissions changed")
    require(status.get("identifier") == lock["baseline_id"], "Configuration identity mismatch")
    for field in FALSE_FIELDS:
        require(status.get(field) is False, f"{field}: explicit false required in this frozen candidate")
    mass = number(status.get("mass_kg"), "mass", True)
    require(abs(mass - number(lock["expected_mass_kg"], "expected mass", True)) < 1e-9, "Mass revision drift")
    ceiling = number(lock["mass_ceiling_kg"], "mass ceiling", True)
    require(mass < ceiling, "Planning mass exceeds ceiling")
    require(abs(number(status.get("margin_to_10kg_kg"), "margin") - (ceiling - mass)) < 1e-9, "Mass margin inconsistent")
    require(status.get("mass_reconciled_link_count") == lock["expected_links"], "Link count mismatch")
    require(status.get("hip_transmission_ratio") == lock["hip_ratio"] == 4.0, "Hip ratio drift")
    for role, field in (("whole_body_step", "whole_body_step_sha256"), ("whole_body_glb", "whole_body_glb_sha256")):
        require(status.get(field) == lock["assets"][role]["sha256"], f"{role}: source-binding drift")
    rows = unique_rows(demand_rows, "demand")
    require(set(rows) == ROTARY_AXES, "Demand must contain exactly the 23 named rotary axes; grippers are not torque rows")
    legs = []
    for axis, row in rows.items():
        peak = number(row.get("peak_contact_inverse_torque_nm"), f"{axis} peak")
        rms = number(row.get("rms_contact_inverse_torque_nm"), f"{axis} RMS")
        endpoint = number(row.get("candidate_current_endpoint_nm"), f"{axis} endpoint", True)
        require(rms <= peak + 1e-9, f"{axis}: RMS exceeds peak")
        ratio = peak / endpoint
        require(abs(ratio - number(row.get("peak_to_current_endpoint_ratio"), f"{axis} ratio")) < 1e-7, f"{axis}: inconsistent endpoint ratio")
        if axis in LEG_AXES:
            legs.append({"axis_id": axis, "peak_nm": peak, "rms_nm": rms, "endpoint_ratio": ratio})
    legs.sort(key=lambda r: (-r["endpoint_ratio"], r["axis_id"]))
    spec = lock["critical_joint"]
    require(legs[0]["axis_id"] == spec["axis_id"], "Critical-joint selection changed; review required")
    allocations = unique_rows(allocation_rows, "allocation")
    expected_drives = LEG_AXES - {"L_HIP_YAW", "R_HIP_YAW"}
    require(set(allocations) == expected_drives, "Reduced-leg allocation axis set mismatch")
    joint = allocations[spec["axis_id"]]
    require(joint.get("drive_id") == spec["drive_id"], "Selected drive changed")
    require(joint.get("ratio") == "2.500:1" and spec["ratio"] == 2.5, "Selected ratio changed")
    for field in ("motor_pulley", "output_pulley", "belt"):
        require(joint.get(field) == spec[field], f"Selected {field} changed")
    require(joint.get("horn_to_pulley_adapter", "").startswith(spec["adapter"] + " - "), "Wrong horn adapter")
    legacy = []
    for side in ("L", "R"):
        for kind, old in (("HIP_PITCH", "1.500:1"), ("HIP_ROLL", "2.000:1")):
            axis = f"{side}_{kind}"
            require(allocations[axis]["ratio"] == old, "Historical allocation changed; re-review disposition")
            legacy.append({"axis_id": axis, "historical_ratio": old, "active_ratio": 4.0})
    efficiency = number(spec["efficiency_assumption"], "efficiency", True)
    require(efficiency <= 1, "Impossible efficiency")
    estimate = number(spec["manufacturer_estimated_continuous_motor_nm"], "motor estimate", True)
    output_estimate = estimate * spec["ratio"] * efficiency
    return {"baseline_id": lock["baseline_id"], "source_commit": lock["source_commit"],
            "scope": "SOURCE_SNAPSHOT_AND_PLANNING_ARITHMETIC_ONLY",
            "mass_kg": mass, "mass_margin_kg": ceiling - mass,
            "rotary_axes_checked": len(rows), "leg_axes_compared": len(legs),
            "selected_joint": legs[0], "estimated_continuous_output_nm": output_estimate,
            "rms_to_manufacturer_heuristic_ratio": legs[0]["rms_nm"] / output_estimate,
            "heuristic_is_acceptance_limit": False,
            "legacy_hip_allocations_explicitly_superseded": legacy,
            "physical_tests_executed": 0, "build_release": False, "walking_validated": False}

def read_json(path: Path) -> dict:
    def reject_duplicates(pairs: list[tuple]) -> dict:
        result = {}
        for key, value in pairs:
            require(key not in result, f"Duplicate JSON key: {key}")
            result[key] = value
        return result
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicates)

def run(root: Path, lock: dict, budget: dict, full_assets: bool = False) -> dict:
    require(set(lock.get("small_inputs", {})) == {"status", "demand", "allocation"}, "Input roles changed")
    require(re.fullmatch(r"[0-9a-f]{40}", lock.get("source_commit", "")) is not None, "Invalid source commit")
    inputs = {role: verified_path(root, entry) for role, entry in lock["small_inputs"].items()}
    def read_csv(path: Path) -> list[dict]:
        with path.open(encoding="utf-8", newline="") as stream:
            return list(csv.DictReader(stream))
    result = analyze(read_json(inputs["status"]), read_csv(inputs["demand"]), read_csv(inputs["allocation"]), lock)
    result["budget"] = budget_totals(budget)
    result["source_files_sha256_verified"] = [e["path"] for e in lock["small_inputs"].values()]
    result["large_asset_hashes_checked"] = False
    if full_assets:
        for entry in lock["assets"].values():
            verified_path(root, entry)
        result["large_asset_hashes_checked"] = True
    result["cad_or_physics_rebuilt"] = False
    return result

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--lock", type=Path)
    parser.add_argument("--budget", type=Path)
    parser.add_argument("--full-assets", action="store_true")
    args = parser.parse_args()
    try:
        lock = read_json(args.lock or args.root / "hr30/build-release/baseline.lock.json")
        budget = read_json(args.budget or args.root / "hr30/build-release/first-tranche-budget.json")
        result = run(args.root, lock, budget, args.full_assets)
        print(json.dumps(result, indent=2, allow_nan=False))
        return 0
    except (AuditError, OSError, KeyError, TypeError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
