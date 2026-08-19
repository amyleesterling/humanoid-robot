#!/usr/bin/env python3
"""Fail-closed checker for HR-30 first-energization measurement harness P0.1."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WHOLE = ROOT / "hr30" / "whole-body-p0.1"
OUT = WHOLE / "first-energization-measurement-harness-p0.1"
REL = ROOT / "release" / "hr30" / "whole-body-p0.1" / OUT.name
WARNING = "PRELIMINARY - UNBUILT MEASUREMENT HARNESS - ZERO SAFETY CREDIT - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, WALKING OR ENERGIZATION"


def need(value: bool, message: str) -> None:
    if not value:
        raise RuntimeError(message)


def rows(name: str) -> list[dict]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    channels = rows("channel-endpoint-register.csv")
    analog = rows("analog-contact-map.csv")
    sync = rows("sync-contact-map.csv")
    cables = rows("cable-assembly-register.csv")
    bom = rows("candidate-bom.csv")
    holds = rows("open-holds.csv")
    sources = rows("primary-source-register.csv")
    status = json.loads((OUT / "harness-status.json").read_text(encoding="utf-8"))
    need(len(channels) == 8 and {r["channel_id"] for r in channels} == {f"CH-AI-{i:02d}" for i in range(1,9)}, "eight-channel register mismatch")
    need(len(analog) == 16 and len({(r["channel_id"],r["polarity"]) for r in analog}) == 16, "analog conductor map mismatch")
    need(all(r["shared_signal_reference"] == "NONE" for r in channels), "shared analog reference introduced")
    need(all(r["conductor"].startswith("Alpha Wire 5610B2201") for r in analog), "analog cable selection drift")
    need(all(r["daq_plug"] == "NI-9976 196739-01 2-position screw plug" for r in analog), "NI-9976 selection drift")
    need(all(r["backshell"] == "NI-9971 196375-01" for r in analog), "NI-9971 selection drift")
    need(all(r["daq_terminal_torque_nm"] == "0.22-0.25" and r["strip_daq_mm"] == "6" for r in analog), "NI-9229 termination rule drift")
    sync_by_to = {r["to"]: r for r in sync}
    need(sync_by_to["NI-9924 terminal 14"]["ni9401_function"] == "DIO0", "terminal 14 is not DIO0")
    need(sync_by_to["NI-9924 terminal 1"]["ni9401_function"] == "COM", "terminal 1 is not COM")
    need(sync_by_to["NI-9924 terminal 15"]["state"] == "MUST REMAIN EMPTY", "terminal 15 NC is populated")
    need(sync_by_to["NI-9924 SH"]["signal"] == "CABLE SHIELD", "NI-9924 shield disposition missing")
    need(len(cables) == 9 and all(float(r["temperature_rating_c"]) >= 90 for r in cables), "cable count/temperature mismatch")
    need(any(r["order_code"] == "782803-01" for r in bom), "NI-9401 ferrite missing")
    need(len(sources) >= 8 and all(r["url"].startswith("https://") for r in sources), "primary source register incomplete")
    need(len(holds) == 8 and all(r["state"] == "OPEN" for r in holds), "open hold state drift")
    need(status["channel_label_corrections"] == ["TTL_LDIST_SAFE_9V","CTRL_5V","HARDWIRED_PERMIT_24V","K1_COIL_24V","K2_COIL_24V"], "channel correction list drift")
    need(status["robot_logical_nodes_bound"] is True and status["robot_physical_pickoffs_released"] is False, "robot pickoff boundary drift")
    for key in ["functional_safety_credit","procurement_authority","fabrication_authority","assembly_authority","connection_authority","powered_test_authority","motion_authority","walking_authority","energization_authority","fer_g11_closed"]:
        need(status[key] is False, f"unsafe authority/status true: {key}")
    binding = json.loads((OUT / "source-binding.json").read_text(encoding="utf-8"))
    bound = [
        (WHOLE / "electrical/measurement-boundary-panel-p0.1/panel-status.json", "measurement_panel_status_sha256"),
        (WHOLE / "electrical/measurement-boundary-panel-p0.1/connector-contact-map.csv", "measurement_panel_contact_map_sha256"),
        (WHOLE / "first-energization-instrumentation-p0.1/instrumentation-status.json", "instrumentation_status_sha256"),
        (WHOLE / "electrical/tether-power-core-p0.1/net-schedule.csv", "tether_power_net_schedule_sha256"),
        (WHOLE / "electrical/kicad/hr30-whole-body-electrical-p0.1/connector-schedule.csv", "whole_body_connector_schedule_sha256"),
    ]
    for path, key in bound:
        need(binding[key] == digest(path), f"source binding drift: {key}")
    manifest = rows("file-manifest.csv")
    expected = sorted(p.relative_to(OUT).as_posix() for p in OUT.rglob("*") if p.is_file() and p.name != "file-manifest.csv")
    need(sorted(r["path"] for r in manifest) == expected, "package manifest file set drift")
    for row in manifest:
        path = OUT / row["path"]
        need(int(row["bytes"]) == path.stat().st_size and row["sha256"] == digest(path), f"manifest mismatch: {path}")
        need(row["warning"] == WARNING, f"manifest warning drift: {path}")
    source_files = sorted(p.relative_to(OUT).as_posix() for p in OUT.rglob("*") if p.is_file())
    release_files = sorted(p.relative_to(REL).as_posix() for p in REL.rglob("*") if p.is_file())
    need(source_files == release_files, "source/release file set drift")
    for rel in source_files:
        need((OUT/rel).read_bytes() == (REL/rel).read_bytes(), f"source/release byte drift: {rel}")
    root_page = (WHOLE / "index.html").read_text(encoding="utf-8")
    root_readme = (WHOLE / "README.md").read_text(encoding="utf-8")
    need(f'{OUT.name}/index.html' in root_page and f'{OUT.name}/index.html' in root_readme, "whole-body links missing")
    need("font:17px" in (OUT / "index.html").read_text(encoding="utf-8"), "legible body font baseline missing")
    print("PASS: 8 floating analog pairs and exact battery-slate NI contact map; robot pickoffs/FER-G11/authority open")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
