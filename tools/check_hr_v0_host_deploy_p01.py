#!/usr/bin/env python3
"""Fail-closed checks for HR-V0-HOST-DEPLOY-P0.1.

Passing proves controlled source consistency and reference behavior only. It
does not install, enable, connect, image, power or energize anything.
"""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "software/host/hr-v0-host-deploy-p0.1"
MANIFEST = PACKAGE / "SOURCE-MANIFEST.csv"
IDENTIFIER = "HR-V0-HOST-DEPLOY-P0.1"
WARNING = "PRELIMINARY - NOT APPROVED FOR INSTALLATION CONNECTION POWERED TEST MOTION OR ENERGIZATION"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def controlled_files() -> list[Path]:
    return [
        path for path in sorted(PACKAGE.rglob("*"))
        if path.is_file()
        and path != MANIFEST
        and "__pycache__" not in path.parts
        and path.suffix != ".pyc"
    ]


def current_hashes() -> dict[str, str]:
    return {
        path.relative_to(PACKAGE).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest().upper()
        for path in controlled_files()
    }


def write_manifest() -> None:
    with MANIFEST.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["file", "sha256"])
        writer.writerows(current_hashes().items())


def main() -> None:
    if "--write-manifest" in sys.argv:
        write_manifest()

    failures: list[str] = []

    def require(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    config = json.loads((PACKAGE / "host-deploy-config.json").read_text(encoding="utf-8"))
    overlay = read_csv(PACKAGE / "overlay-manifest.csv")
    holds = read_csv(PACKAGE / "hold-register.csv")
    execution = read_csv(ROOT / "tests/forms/hr-v0-host-deployment-template-p0.1.csv")
    supplement = read_csv(ROOT / "requirements/hr-v0-gate-evidence-supplement-r171.csv")
    gates = {row["gate_id"]: row for row in read_csv(ROOT / "requirements/hr-v0-energization-gates.csv")}
    guide = (ROOT / "release/hr-v0/host-deployment-p0.1/index.html").read_text(encoding="utf-8")
    doc = (ROOT / "docs/hr-v0-host-deployment-p0.1.md").read_text(encoding="utf-8")
    metadata = json.loads((ROOT / "release/hr-v0/release-candidate.json").read_text(encoding="utf-8"))

    require(config.get("identifier") == IDENTIFIER, "host deployment identifier changed")
    require(config.get("release_state") == "HOLD" and config.get("authorized_stage") == "NOT_AUTHORIZED", "committed host state is not fail-closed")
    require(config.get("motion_authority") == "NONE" and config.get("functional_safety_credit") == "NONE", "host package claims prohibited authority or safety credit")
    startup = config.get("startup_policy", {})
    require(startup.get("service_default") == "DISABLED" and startup.get("restart") == "NO", "disabled/no-restart policy changed")
    require(startup.get("heartbeat_initial_state") == "INPUT_OR_HIGH_IMPEDANCE", "heartbeat startup state changed")
    require(startup.get("serial_open_before_preflight") is False and startup.get("gpio_access_before_preflight") is False, "preflight hardware-access prohibition changed")
    require(startup.get("stale_motion_resume") is False, "stale motion resume is no longer prohibited")

    require(len(overlay) == 6, "overlay manifest must contain six proposed files")
    require(len(holds) == 18 and all(row["current_state"] == "OPEN" for row in holds), "host hold register must contain eighteen open holds")
    require(len(execution) == 21, "host deployment execution template must contain twenty-one rows")
    require(all(row["authorization"] == "NOT_AUTHORIZED" and row["state"] == "NOT_EXECUTED" and not row["actual_result"] and not row["evidence_hash"] for row in execution), "execution template contains authority or result evidence")
    require(len(supplement) == 3 and {row["gate_id"] for row in supplement} == {"EG-003", "EG-017", "EG-021"}, "R171 gate supplement changed")
    require(all(row["disposition"] == "REMAINS PARTIAL" for row in supplement), "R171 improperly advances a gate")
    require(all(gates.get(gate, {}).get("status") == "partial" for gate in ("EG-003", "EG-017", "EG-021")), "host-related gate was improperly closed")

    proposed_sources = {row["source"] for row in overlay}
    require(proposed_sources == {
        "host-deploy-config.json",
        "project_button_host/__init__.py",
        "project_button_host/preflight.py",
        "project_button_host/launcher.py",
        "systemd/project-button-supervisor.service",
        "systemd/00-project-button.preset",
    }, "overlay source set changed")
    require(all(row["install_state"] == "NOT_AUTHORIZED" and row["warning"] == WARNING for row in overlay), "overlay contains an authorized row or changed warning")
    require(all(row["warning"] == WARNING for row in holds), "hold warning changed")

    unit = (PACKAGE / "systemd/project-button-supervisor.service").read_text(encoding="utf-8")
    preset = (PACKAGE / "systemd/00-project-button.preset").read_text(encoding="utf-8")
    require(preset.strip() == "disable project-button-supervisor.service", "systemd service is not disabled by preset")
    for invariant in ("Restart=no", "NoNewPrivileges=true", "ProtectSystem=strict", "ExecStart=/usr/bin/python3 /opt/project-button/lib/project_button_host/launcher.py"):
        require(invariant in unit, f"systemd invariant missing: {invariant}")

    host_source = "\n".join((PACKAGE / "project_button_host" / name).read_text(encoding="utf-8") for name in ("preflight.py", "launcher.py"))
    for forbidden in ("import gpiod", "import gpiozero", "import serial", "import dynamixel_sdk"):
        require(forbidden not in host_source, f"hardware backend import present: {forbidden}")
    require("subprocess.run" in host_source and host_source.find("evaluate(config_path") < host_source.find("subprocess.run"), "launcher does not visibly gate subprocess behind preflight")

    tests = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", str(PACKAGE / "tests"), "-v"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    require(tests.returncode == 0, "host deployment unit tests failed\n" + tests.stdout + tests.stderr)

    recorded = {row["file"]: row["sha256"] for row in read_csv(MANIFEST)} if MANIFEST.is_file() else {}
    require(recorded == current_hashes(), "host SOURCE-MANIFEST.csv is stale or incomplete")

    firmware_product = next((item for item in metadata.get("current_products", []) if item.get("domain") == "firmware"), {})
    require(IDENTIFIER in firmware_product.get("supporting_identifiers", []), "release metadata lacks host deployment identifier")
    require(IDENTIFIER in doc and IDENTIFIER in guide, "document or guide lacks identifier")
    require("23" in doc and "eighteen" in doc.lower() and "21" in doc, "documented hold/evidence counts changed")
    require("font:16px" in guide and "font-size:16px" in guide and "font-size:14px" in guide, "guide text floors are not explicit")
    require(guide.count("data-filter=") == 4 and guide.count("data-kind=") == 4, "guide filter/card structure changed")
    for token in ("disabled", "exit 78", "no GPIO", "no serial", "zero functional-safety credit", "not approved"):
        require(token.lower() in (doc + guide).lower(), f"required boundary missing: {token}")

    if failures:
        raise SystemExit("HR-V0 host deployment P0.1 check failed:\n- " + "\n- ".join(failures))
    print("HR-V0 host deployment P0.1 check passed: 6-file disabled overlay, 23 current preflight holds, 18 open closure holds, 21 unexecuted evidence rows, 6 source tests")
    print("EG-017 remains PARTIAL; no target image, installation, GPIO/serial backend, HIL, motion or energization authority exists")
    print(WARNING)


if __name__ == "__main__":
    main()
