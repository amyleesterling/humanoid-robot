#!/usr/bin/env python3
"""Validate R245 integrated mechanical and firmware source bindings."""
from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
MANIFEST_SHA = "5adc34ff41f2f84b1d8cf60e2a95b6f93ebc8eba1f2ac6b93642dd429b237c8a"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def need(value: bool, message: str) -> None:
    if not value:
        raise AssertionError(message)


def main() -> int:
    try:
        binding = read(ROOT / "bom/hr-v0-mechanical-custom-part-binding-p0.3.csv")
        need(len(binding) == 5, "P0.3 binding count differs")
        need({r["part_id"] for r in binding} == {"MV0-C01", "MV0-C04", "MV0-C05", "MV0-C06", "MV0-C07"}, "part set differs")
        need(all(r["architecture_id"] == "HR-V0-ARM-ARCH-P0.8-DWG-INTEGRATED-CANDIDATE" for r in binding), "stale architecture remains")
        need(all(r["quotation_authorized"] == r["fabrication_authorized"] == "FALSE" and r["warning"] == WARNING for r in binding), "work boundary changed")
        for row in binding:
            for field in ("step_path", "dxf_path", "drawing_path"):
                path = ROOT / row[field]
                need(path.is_file() and digest(path) == row[field.replace("_path", "_sha256")], f"artifact differs: {row['part_id']} {field}")

        manifest_path = ROOT / "configuration/hr-v0-firmware-mechanical-source-binding-p0.1/source-binding-manifest.json"
        need(digest(manifest_path) == MANIFEST_SHA, "source-binding manifest hash differs")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        need(manifest["custom_part_manufacturing_revision"] == "HR-V0-MECH-BOM-BIND-P0.3", "manifest uses stale manufacturing binding")
        need(len(manifest["sources"]) == 8, "source manifest count differs")
        for row in manifest["sources"]:
            path = ROOT / row["path"]
            need(path.is_file() and digest(path) == row["sha256"], f"bound source differs: {row['path']}")

        for name in ("supervisor-config.json", "actuator-config.json"):
            config = json.loads((ROOT / "firmware/supervisor" / name).read_text(encoding="utf-8"))
            block = config["mechanical_limit_binding"]
            need(block["source_binding_identifier"] == "HR-V0-FW-MECH-SRC-BIND-P0.1", f"{name} binding id differs")
            need(block["source_binding_manifest_sha256"] == MANIFEST_SHA, f"{name} manifest hash differs")
            need(block["custom_part_manufacturing_revision"] == "HR-V0-MECH-BOM-BIND-P0.3", f"{name} manufacturing id differs")
            need(block["release_state"] == "CANDIDATE-NOT-RELEASED", f"{name} was released")
            need(block["acceptance_evidence_hash"] == "SELECTION REQUIRED", f"{name} physical acceptance was inferred")

        for directory in (ROOT / "configuration/hr-v0-firmware-mechanical-source-binding-p0.1", ROOT / "release/hr-v0/firmware-mechanical-source-binding-p0.1", ROOT / "release/hr-v0/mechanical-bom-binding-p0.3", ROOT / "configuration/hr-v0-config-reconciliation-p0.9", ROOT / "release/hr-v0/configuration-reconciliation-p0.9"):
            need(directory.is_dir(), f"missing package {directory}")
            status = json.loads((directory / "package-status.json").read_text(encoding="utf-8"))
            need(status["warning"] == WARNING and not status["energization_authorized"], f"unsafe status in {directory}")
            for row in read(directory / "file-manifest.csv"):
                target = directory / row["path"]
                need(target.is_file() and digest(target) == row["sha256"], f"file manifest mismatch: {target}")

        cfg = json.loads((ROOT / "release/hr-v0/configuration-reconciliation-p0.9/package-status.json").read_text(encoding="utf-8"))
        need(cfg["current_custom_part_binding"] == "HR-V0-MECH-BOM-BIND-P0.3" and cfg["firmware_mechanical_source_binding"] == "HR-V0-FW-MECH-SRC-BIND-P0.1", "P0.9 configuration identity differs")
        need(cfg["system_bom_groups"] == 98 and cfg["open_holds"] == 38 and not cfg["motion_authorized"], "P0.9 counts or authority differ")

        tests = __import__("subprocess").run([sys.executable, "-m", "unittest", "discover", "-s", "firmware/supervisor/tests"], cwd=ROOT, stdout=__import__("subprocess").PIPE, stderr=__import__("subprocess").STDOUT, text=True, check=False)
        need(tests.returncode == 0, "firmware unit tests failed\n" + tests.stdout)
        print("R245 firmware/mechanical source binding PASS")
        print("  5 parts / 15 unchanged identities / 8 bound sources / 2 fail-closed firmware configurations")
        return 0
    except Exception as exc:
        print(f"R245 firmware/mechanical source binding FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
