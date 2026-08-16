#!/usr/bin/env python3
"""Fail-closed checks for the HR-30 actuator cable-kit candidate."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WHOLE = ROOT / "hr30" / "whole-body-p0.1"
OUT = WHOLE / "harness" / "actuator-cable-kit-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / "harness" / OUT.name
GEN = ROOT / "tools" / "generate_hr30_actuator_cable_kit_p01.py"
WARNING = "PRELIMINARY - UNBUILT ACTUATOR CABLE-KIT CANDIDATE - NOT APPROVED FOR PROCUREMENT, FABRICATION, CONNECTION, POWERED TESTING, MOTION OR ENERGIZATION"


def need(value: bool, message: str) -> None:
    if not value:
        raise RuntimeError(message)


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    need(OUT.is_dir() and RELEASE.is_dir(), "source/release package missing")
    sources = rows(OUT / "primary-source-register.csv")
    connectors = rows(OUT / "connector-family-disposition.csv")
    axes = rows(OUT / "axis-power-cable-candidate.csv")
    data = rows(OUT / "data-cable-candidate.csv")
    cavities = rows(OUT / "connector-cavity-population.csv")
    tests = rows(OUT / "inspection-test-plan.csv")
    holds = rows(OUT / "open-holds.csv")
    status = json.loads((OUT / "actuator-cable-kit-status.json").read_text(encoding="utf-8"))

    need(len(sources) == 9 and len(connectors) == 4, "source/connector coverage drift")
    need(len(axes) == 25 and len({r["axis_id"] for r in axes}) == 25, "25 unique axis candidates required")
    need(len(data) == 4 and len(tests) == 12 and len(holds) == 10, "candidate/test/hold coverage drift")
    need(len(cavities) == 159 and len({r["cavity_id"] for r in cavities}) == 159, "159 unique cavity records required")
    all_rows = sources + connectors + axes + data + cavities + tests + holds
    need(all(r["execution_state"] == "NOT EXECUTED" and r["warning"] == WARNING for r in all_rows), "execution/warning overclaim")
    need(all(r["state"] == "OPEN" for r in holds), "hold falsely closed")
    need(all(r["result"] == "NOT EXECUTED" and r["measured_value"] == "NONE" for r in tests), "test execution overclaim")

    local_sources = sources[:4]
    need(all(r["sha256"] == sha(ROOT / r["official_url_or_path"]) for r in local_sources), "local source hash drift")
    need(any(r["candidate_housing"] == "JST EHR-4" and r["candidate_contact"] == "JST SEH-001T-P0.6" for r in connectors), "RS-485 connector family missing")
    need(any(r["candidate_housing"] == "JST EHR-3" and r["candidate_contact"] == "JST SEH-001T-P0.6" for r in connectors), "TTL connector family missing")
    need(any("LOW-INSERTION-FORCE" in r["disposition"] and "REJECTED" in r["disposition"] for r in connectors), "vibration contact disposition missing")

    cap_sum = sum(float(r["candidate_internal_limit_a"]) for r in axes)
    stall_sum = sum(float(r["published_stall_endpoint_a"]) for r in axes)
    need(abs(cap_sum - 46.67779) < 1e-6 and abs(stall_sum - 71.88) < 1e-9, "current boundaries drift")
    need(all(float(r["candidate_internal_limit_a"]) <= 2.499010 + 1e-9 for r in axes), "per-axis cap exceeds frozen candidate")
    need(all(r["stall_is_normal_demand"] == "NO" for r in axes), "stall endpoint promoted to demand")
    need(all("0.34 mm2" in r["power_pair_test_coupon_candidate"] and "0.33 mm2" in r["jst_eh_published_conductor_range"] for r in axes), "wire/contact cross-section evidence missing")
    need(all(r["wire_contact_compatibility"].startswith("OPEN") and r["branch_protection"] == "SELECTION REQUIRED" for r in axes), "physical selection overclaimed")
    need(all("NOT CALCULATED" in r["voltage_drop"] for r in axes), "unreleased voltage-drop calculation claimed")

    counts = Counter(r["connector_role"] for r in cavities)
    need(counts == Counter({"ACTUATOR INPUT": 94, "DATA-ONLY OUTGOING": 65}), "input/outgoing cavity coverage drift")
    empty = [r for r in cavities if r["required_population"] == "EMPTY"]
    need(len(empty) == 34 and all(r["pin"] in {"1", "2"} and r["connector_role"] == "DATA-ONLY OUTGOING" for r in empty), "outgoing GND/VDD empty rule drift")
    need(all(r["actual_population"] == "NOT INSPECTED" for r in cavities), "physical inspection overclaim")
    incoming = [r for r in cavities if r["connector_role"] == "ACTUATOR INPUT"]
    need(sum(r["signal"] == "VDD" for r in incoming) == 25 and sum(r["signal"] == "GND" for r in incoming) == 25, "individual input power coverage drift")
    need(all(r["disposition"] == "REJECT" for r in data if "ROBOTIS" in r["candidate"]), "standard ROBOTIS powered daisy cable not rejected")
    need(any(r["service"] == "RS-485 data plus reference" and r["disposition"] == "HOLD" for r in data), "RS-485 data cable uncertainty missing")

    for key in ["cf130_jst_cross_section_compatibility", "power_cable_selected", "data_cable_selected", "crimp_process_selected", "procurement_authority", "fabrication_authority", "connection_authority", "powered_test_authority", "motion_authority", "energization_authority"]:
        need(status[key] is False, f"fail-closed status violated: {key}")
    need(status["current_caps_propagated"] and status["canonical_jst_order_code_family_bound"], "material advancement missing")
    need(status["built_cable_count"] == status["executed_test_count"] == 0, "physical evidence overclaim")

    need((OUT / "actuator-cable-kit-source.py").read_bytes() == GEN.read_bytes(), "generator snapshot drift")
    manifest = rows(OUT / "file-manifest.csv")
    expected = sorted(p.relative_to(OUT).as_posix() for p in OUT.rglob("*") if p.is_file() and p.name != "file-manifest.csv")
    need(sorted(r["path"] for r in manifest) == expected, "manifest membership drift")
    need(all(int(r["bytes"]) == (OUT / r["path"]).stat().st_size and r["sha256"] == sha(OUT / r["path"]) for r in manifest), "manifest hash/size drift")
    source_files = sorted(p.relative_to(OUT).as_posix() for p in OUT.rglob("*") if p.is_file())
    release_files = sorted(p.relative_to(RELEASE).as_posix() for p in RELEASE.rglob("*") if p.is_file())
    need(source_files == release_files and all(sha(OUT / p) == sha(RELEASE / p) for p in source_files), "source/release parity drift")

    page = (OUT / "index.html").read_text(encoding="utf-8")
    svg = (OUT / "actuator-cable-kit.svg").read_text(encoding="utf-8")
    need("font:17px" in page and "font-size:16px" in page and "min-width:1180px" in page, "web legibility/overflow drift")
    need("font-size:16px" in svg and "font-size:34px" in svg, "drawing legibility drift")
    need("The 25 actuator cables now have explicit pin populations" in page and "Do not crimp" in page, "guide purpose/warning drift")
    root_page = (WHOLE / "index.html").read_text(encoding="utf-8")
    need("HR30-ACTUATOR-CABLE-KIT-P01-START" in root_page and "159" in root_page, "root guide integration missing")
    root_readme = (WHOLE / "README.md").read_text(encoding="utf-8")
    need(root_readme.count("HR30-ACTUATOR-CABLE-KIT-P01-README-START") == 1 and root_readme.count("HR30-ACTUATOR-CABLE-KIT-P01-README-END") == 1, "cable-kit README marker drift")
    need(root_readme.count("HR30-AXIS-COMMISSION-START") == 1 and root_readme.count("HR30-AXIS-COMMISSION-END") == 1, "axis-commissioning README marker drift")
    root_status = json.loads((WHOLE / "package-status.json").read_text(encoding="utf-8"))
    need(root_status["actuator_cable_kit_axis_count"] == 25 and root_status["actuator_cable_kit_cavity_record_count"] == 159, "root status integration missing")
    need(root_status["actuator_cable_kit_current_caps_propagated"] and not root_status["energization_authority"], "root advancement/authority drift")
    print("PASS: HR-30 actuator cable kit binds 25 current-capped feeds, 159 cavity records and 34 required empty outgoing power cavities; wire/crimp/protection/authority remain open")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
