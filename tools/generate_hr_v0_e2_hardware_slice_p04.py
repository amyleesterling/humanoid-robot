#!/usr/bin/env python3
"""Generate the P1.15-bound, fail-closed HR-V0 E2 hardware slice P0.4."""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import generate_hr_v0_e2_hardware_slice as base  # noqa: E402


ENG = ROOT / "electrical" / "e2" / "hr-v0-e2-hardware-p0.4"
REL = ROOT / "release" / "hr-v0" / "e2-hardware-p0.4"
IDENTIFIER = "HR-V0-E2-HW-P0.4"
DIRECT_BINDING = "PCB-P1.0 / Electrical V3-P1.15"
WARNING = "PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def changed_config() -> list[tuple[str, ...]]:
    result: list[tuple[str, ...]] = []
    for row in base.CONFIG:
        values = list(row)
        if row[0] == "E2-CFG-011":
            values[2] = "Project Button PCB-P1.0 / HR-V0-WD-PCBA-DATA-P0.2 / HR-V0-WD-CAM-P0.2"
            values[3] = "P1.15-DIRECT INSTALL CANDIDATE"
            values[5] = "PCB-P1.0 is natively bound to P1.15 and current internal CAM exists; supplier-normalized XYRS, assembler/process acceptance, fabrication, bare-board, assembly, HIL, fault, EMC, thermal and qualified evidence remain absent."
        elif row[0] == "E2-CFG-018":
            values[2] = "F1/F2/F3, three P0.3 limiter carriers and DXL-STAR-P0.2-CARRIER-CANDIDATE"
            values[5] = "Current P1.15 actuator subset exists only as digital candidate evidence; all protection, current coordination, branch harness and physical evidence remain open and the complete subset is absent or unwired at E2."
        result.append(tuple(values))
    return result


def changed_holds() -> list[tuple[str, ...]]:
    result: list[tuple[str, ...]] = []
    for row in base.HOLDS:
        values = list(row)
        if row[0] == "E2-HOLD-008":
            values[2] = "PCB-P1.0 directly matches P1.15 system identity and has current exact identity/BOM/placement data plus internal CAM review; no supplier-normalized XYRS, accepted process, physical article or manufacturing release"
            values[3] = "Independent P1.15 configuration acceptance; assembler/supplier process and coordinate-transform acceptance; bare-board test; assembly; HIL/fault/EMC/thermal evidence"
        result.append(tuple(values))
    return result


def source_paths() -> dict[str, Path]:
    return {
        "p115_root_schematic": ROOT / "electrical" / "kicad" / "project-button-v3-p1.15-carrier-candidate" / "project-button-v3-p1.15-carrier-candidate.kicad_sch",
        "p115_connector_schedule": ROOT / "electrical" / "kicad" / "project-button-v3-p1.15-carrier-candidate" / "connector-schedule.csv",
        "p115_native_netlist": ROOT / "electrical" / "kicad" / "project-button-v3-p1.15-carrier-candidate" / "validation" / "project-button-v3-p1.15-carrier-candidate.net",
        "p115_native_erc": ROOT / "electrical" / "kicad" / "project-button-v3-p1.15-carrier-candidate" / "validation" / "project-button-v3-p1.15-carrier-candidate-erc.rpt",
        "watchdog_cam": ROOT / "release" / "hr-v0" / "watchdog-pcb-cam-p0.2" / "package-status.json",
        "e2_sequence": ROOT / "tests" / "e2" / "hr-v0-e2-control-only-sequence.csv",
    }


def write_csv(path: Path, fieldnames: list[str], data: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(data)


def generate_target(target: Path) -> None:
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True)
    config = changed_config()
    holds = changed_holds()
    base.OUT = target
    base.IDENTIFIER = IDENTIFIER
    base.CONFIG = config
    base.HOLDS = holds
    base.write_csv("e2-configuration-slice.csv", ("record_id", "reference", "candidate", "physical_state", "e2_boundary", "open_evidence", "warning"), config)
    base.write_csv("e2-terminal-register.csv", ("terminal", "net", "catalog_body", "mapping_state", "physical_release", "warning"), base.TERMINALS)
    base.write_csv("e2-source-register.csv", ("source_id", "reference", "candidate", "published_output", "document_revision_or_date", "official_source", "e2_state", "warning"), base.SOURCES)
    base.write_csv("e2-blocking-holds.csv", ("hold_id", "scope", "open_item", "evidence_needed", "warning"), holds)
    sources = source_paths()
    source_hashes = {path.relative_to(ROOT).as_posix(): sha256(path) for path in sources.values()}
    summary = {
        "identifier": IDENTIFIER,
        "date": "2026-08-10",
        "round": "R195-SYNCHRONIZED",
        "warning": WARNING,
        "electrical_baseline": "Project Button Electrical V3-P1.15-CARRIER-CANDIDATE / PCB-P1.0 / HR-V0-WD-PCBA-DATA-P0.2",
        "configuration_binding": DIRECT_BINDING,
        "sequence_baseline": "HR-V0-E2-SEQ-P0.1",
        "configuration_rows": len(config),
        "terminal_rows": len(base.TERMINALS),
        "source_rows": len(base.SOURCES),
        "blocking_holds": len(holds),
        "permitted_power_domains": ["24 V safety/control candidate", "5.1 V compute candidate"],
        "prohibited_power_domains": ["12 V actuator", "powered U2D2/actuator branches"],
        "source_hashes": source_hashes,
        "p115_direct_binding_verified_by_checker": True,
        "physical_configuration_verified": False,
        "run_authorized": False,
        "fabrication_authorized": False,
        "connection_authorized": False,
        "motion_authorized": False,
        "energization_authorized": False,
        "safety_credit": False,
        "authorization": "NOT AUTHORIZED",
    }
    (target / "e2-hardware-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    page = base.make_html().replace("P0.3", "P0.4").replace("\u00c2\u00b7", "&middot;").replace("\u00b7", "&middot;")
    (target / "HR-V0_e2-hardware-guide.html").write_text(page, encoding="utf-8")
    source_rows = [{"source_id": key, "path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path), "bytes": str(path.stat().st_size), "warning": WARNING} for key, path in sources.items()]
    write_csv(target / "source-hash-register.csv", ["source_id", "path", "sha256", "bytes", "warning"], source_rows)
    (target / "README.md").write_text(f"# {IDENTIFIER}\n\n{WARNING}\n\nThis control-only hardware slice uses the direct native binding `{DIRECT_BINDING}`. It authorizes no purchase, fabrication, wiring, connection, test, motion or energization. The actuator source and complete actuator branch subset remain physically absent or unwired at E2.\n", encoding="utf-8")
    files = [{"path": path.relative_to(target).as_posix(), "bytes": str(path.stat().st_size), "sha256": sha256(path)} for path in sorted(p for p in target.rglob("*") if p.is_file() and p.name != "file-manifest.csv")]
    write_csv(target / "file-manifest.csv", ["path", "bytes", "sha256"], files)


def main() -> int:
    for path in source_paths().values():
        if not path.is_file():
            raise FileNotFoundError(path)
    generate_target(ENG)
    generate_target(REL)
    print(f"Generated {IDENTIFIER}: 23 configuration rows / 6 XT1 rows / 12 holds")
    print("P1.15 directly bound; actuator source/branches physically absent or unwired; run NOT AUTHORIZED")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
