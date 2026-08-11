#!/usr/bin/env python3
"""Check the R200 fail-closed runtime-observation correction."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WARNING = "PRELIMINARY - NOT APPROVED FOR CONNECTION MOTION OR ENERGIZATION"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    failures: list[str] = []

    def need(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    mapping = rows(ROOT / "controls/hr-v0-runtime-observation-map-p0.1.csv")
    holds = rows(ROOT / "controls/hr-v0-runtime-observation-holds-p0.1.csv")
    need(len(mapping) == 10, "observation map must contain ten distinct runtime semantics")
    need(len({row["software_semantic"] for row in mapping}) == 10, "observation semantic duplicated")
    need(sum(row["provider_class"] == "positive panel status" for row in mapping) == 4, "exactly four positive panel statuses required")
    need(sum(row["current_disposition"] == "SELECTION REQUIRED" for row in mapping) == 5, "exactly five health providers must remain selection-required")
    need(all(row["warning"] == WARNING for row in mapping), "observation warning changed")
    need(len(holds) == 12 and sum(row["state"] == "OPEN" for row in holds) == 11 and sum(row["state"] == "PARTIAL" for row in holds) == 1, "observation holds must contain eleven open and one partial")
    need(next(row for row in holds if row["hold_id"] == "ROH-006")["state"] == "PARTIAL", "GPIO allocation hold did not advance only to partial")
    need(all(row["warning"] == WARNING for row in holds), "hold warning changed")

    model = (ROOT / "firmware/supervisor/project_button_supervisor/model.py").read_text(encoding="utf-8")
    backend = (ROOT / "software/host/hr-v0-host-deploy-p0.1/project_button_host/gpiod_hardware.py").read_text(encoding="utf-8")
    for token in ("control_power: bool | None", "OBSERVATION_HOLD", "snapshot.control_power is True", "snapshot.compute_undervoltage is False"):
        need(token in model, f"fail-closed model invariant missing: {token}")
    need("PHYSICAL_INPUT_NAMES" in backend, "four-status backend schema absent")
    for token in ("sr1_status", "sra1_status", "k1_status", "k2_status"):
        need(token in backend, f"positive status missing from backend: {token}")
    for token in ("control_power=None", "estop_healthy=None", "watchdog_healthy=None", "edm_healthy=None", "compute_undervoltage=None"):
        need(token in backend, f"unavailable provider is not explicit: {token}")
    need("sr1_diag_nc" not in backend and "sra1_diag_nc" not in backend, "NC contact is incorrectly inverted into positive state")

    config = json.loads((ROOT / "software/host/hr-v0-host-deploy-p0.1/host-deploy-config.json").read_text(encoding="utf-8"))
    need(set(config["gpio"]["inputs"]) == {"sr1_status", "sra1_status", "k1_status", "k2_status"}, "host GPIO schema changed")
    need(set(config["required_observation_providers"]) == {"control_power", "estop_healthy", "watchdog_healthy", "edm_healthy", "compute_undervoltage"}, "health-provider schema changed")
    need(all(value == "SELECTION REQUIRED" for value in config["required_observation_providers"].values()), "health provider was released without evidence")

    page = (ROOT / "release/hr-v0/runtime-observation-p0.1/index.html").read_text(encoding="utf-8")
    for token in ("font:16px", "font-size:14px", "data-filter=\"all\"", "data-kind=\"panel\"", "zero functional-safety credit"):
        need(token.lower() in page.lower(), f"guide invariant missing: {token}")
    need("font-size:11" not in page and "font-size:10" not in page, "guide contains undersized text")

    tests = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "firmware/supervisor/tests"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    need(tests.returncode == 0 and "Ran 75 tests" in tests.stderr, "75 supervisor/runtime/logging tests did not pass")
    host = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "software/host/hr-v0-host-deploy-p0.1/tests"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    need(host.returncode == 0 and "Ran 16 tests" in host.stderr, "16 host tests did not pass")

    if failures:
        raise SystemExit("HR-V0 runtime observation P0.1 check failed:\n- " + "\n- ".join(failures))
    print("HR-V0 runtime observation P0.1 check passed: 4 positive panel statuses, 5 unavailable health providers, 1 software bus result, 11 open plus 1 partial hold, 75 supervisor/runtime/logging tests, 16 host tests")
    print("GPIO lines are source-bound; no connected receiver/harness, target gpiochip, health provider, HIL evidence, safety credit or work authority exists")
    print(WARNING)


if __name__ == "__main__":
    main()
