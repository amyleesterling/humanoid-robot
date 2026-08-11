#!/usr/bin/env python3
"""Generate P1.17 with the R211/P0.5 observation carrier bound explicitly."""

from __future__ import annotations

import csv
import hashlib
import shutil
import sys
import types
from pathlib import Path

from generate_hr_v0_electrical_v3_p116_observation_candidate import transformed_source as p116_source


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "electrical" / "kicad" / "project-button-v3-p1.17-observation-p05-candidate"
PROJECT = "project-button-v3-p1.17-observation-p05-candidate"
REV = "V3-P1.17-OBSERVATION-P0.5-CANDIDATE"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one source match, found {count}")
    return text.replace(old, new, 1)


def transformed_source() -> str:
    text = p116_source()
    text = text.replace("project-button-v3-p1.16-observation-candidate", PROJECT)
    text = once(text, 'REV = "V3-P1.16-OBSERVATION-CANDIDATE"', f'REV = "{REV}"', "revision")
    text = once(
        text,
        'PROJECT_SUBTITLE = "P1.15 limiter chain plus exact R202/R204 field and compute observation interfaces; zero safety credit."',
        'PROJECT_SUBTITLE = "P1.15 limiter chain plus R211/P0.5 open-drain observation carrier and R204 Pi interface; zero safety credit."',
        "subtitle",
    )
    text = once(
        text,
        'Component("OBS1", "HR-V0-RUNTIME-OBS-CARRIER-P0.2 diagnostic receiver assembly",',
        'Component("OBS1", "HR-V0-RUNTIME-OBS-CARRIER-P0.5 open-drain diagnostic receiver assembly",',
        "OBS1 identity",
    )
    text = once(
        text,
        '"R202 four-layer receiver assembly. Field and compute domains remain separated inside the subassembly; this system block assigns no safety credit and releases no fabrication, harness, connection or powered work.",',
        '"R211 P0.5 four-layer open-drain receiver assembly. Field and compute domains remain separated inside the subassembly; this system block assigns no safety credit and releases no fabrication, harness, connection or powered work.",',
        "OBS1 description",
    )
    text = once(
        text,
        '"electrical/kicad/hr-v0-runtime-observation-carrier-p0.2/",',
        '"electrical/kicad/hr-v0-runtime-observation-carrier-p0.5/",',
        "OBS1 source path",
    )
    text = once(
        text,
        '"R202 native source: five sheets, Phoenix item 1751280 at both boundaries, ERC/DRC 0; fourteen physical/application holds remain open.",',
        '"R211 native source: five sheets, exact SN74LVC1G07DBVR / 10k / 39k / 330k network, Phoenix item 1751280 at both boundaries, ERC/DRC 0; Pi acceptance and fourteen physical/application holds remain open.",',
        "OBS1 evidence",
    )
    text = once(
        text,
        '"INTENTIONALLY_UNUSED_OBS1_JFIELD1_6"',
        '"INTENTIONALLY_UNUSED_JFIELD1_6"',
        "P0.5 unused-terminal net identity",
    )
    text = text.replace("R202", "R211")
    text = text.replace("R206", "R212")
    text = once(
        text,
        '- Heartbeat restoration cannot restore contactors; SRA1 requires a new monitored ARM action.',
        '- OBS1 is bound to `HR-V0-RUNTIME-OBS-CARRIER-P0.5`: four exact open-drain `SN74LVC1G07DBVR` stages, 10.0 kohm pull-ups, 39.0 kohm GPIO limiters and 330 kohm fail-low biases. The external JFIELD1/JLOGIC1 map is unchanged. Pi 5/RP1 DC acceptance, STANDBY/ramp/brownout testing, DFM, first article and qualified review remain open. The observation chain receives zero safety credit.\n- Heartbeat restoration cannot restore contactors; SRA1 requires a new monitored ARM action.',
        "README P0.5 disposition",
    )
    return text


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def write_binding() -> None:
    p05 = ROOT / "electrical/kicad/hr-v0-runtime-observation-carrier-p0.5"
    pi = ROOT / "electrical/kicad/hr-v0-pi-observation-carrier-p0.1"
    fields = [
        "role", "configuration_id", "repository_path", "source_manifest_sha256",
        "connector_schedule_sha256", "interface", "acceptance_state", "warning",
    ]
    rows = [
        {
            "role": "system_ecad",
            "configuration_id": REV,
            "repository_path": OUT.relative_to(ROOT).as_posix() + "/",
            "source_manifest_sha256": "SELF-REFERENCE CONTROLLED BY SOURCE-MANIFEST.csv",
            "connector_schedule_sha256": digest(OUT / "connector-schedule.csv"),
            "interface": "OBS1 JFIELD1/JLOGIC1 and PIOBS1 JOBS1/JPI1",
            "acceptance_state": "CONNECTED CANDIDATE - PHYSICAL AND QUALIFIED REVIEW OPEN",
            "warning": WARNING,
        },
        {
            "role": "runtime_observation_carrier",
            "configuration_id": "HR-V0-RUNTIME-OBS-CARRIER-P0.5",
            "repository_path": p05.relative_to(ROOT).as_posix() + "/",
            "source_manifest_sha256": digest(p05 / "SOURCE-MANIFEST.csv"),
            "connector_schedule_sha256": digest(p05 / "connector-schedule.csv"),
            "interface": "JFIELD1:1-6 and JLOGIC1:1-6",
            "acceptance_state": "CURRENT CANDIDATE - PI/DFM/PHYSICAL/REVIEW HOLDS OPEN",
            "warning": WARNING,
        },
        {
            "role": "pi_observation_carrier",
            "configuration_id": "HR-V0-PI-OBS-CARRIER-P0.1",
            "repository_path": pi.relative_to(ROOT).as_posix() + "/",
            "source_manifest_sha256": digest(pi / "SOURCE-MANIFEST.csv"),
            "connector_schedule_sha256": digest(pi / "connector-schedule.csv"),
            "interface": "JOBS1:1-6 and JPI1 physical pins 15/16/17/18/20/22",
            "acceptance_state": "CURRENT CANDIDATE - STACK/HARNESS/PHYSICAL/REVIEW HOLDS OPEN",
            "warning": WARNING,
        },
    ]
    with (OUT / "observation-subassembly-binding.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    name = "observation_p05_integrated_electrical_generator"
    module = types.ModuleType(name)
    module.__file__ = str(ROOT / "tools/generate_hr_v0_electrical_v3.py")
    sys.modules[name] = module
    exec(compile(transformed_source(), module.__file__, "exec"), module.__dict__)
    footprint_source = ROOT / "electrical/kicad/project-button-v3/PBV3_Footprints.pretty"
    footprint_target = module.OUT / "PBV3_Footprints.pretty"
    footprint_target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(footprint_source, footprint_target, dirs_exist_ok=True)
    result = int(module.main())
    write_binding()
    module.manifest()
    return result


if __name__ == "__main__":
    raise SystemExit(main())
