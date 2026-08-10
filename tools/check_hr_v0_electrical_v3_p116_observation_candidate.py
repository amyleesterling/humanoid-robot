#!/usr/bin/env python3
"""Fail-closed checks for the P1.16 observation-integrated KiCad candidate.

These checks prove generated-source, native-netlist, export and warning parity.
They do not establish component suitability, safety integrity, fabrication
readiness, test authorization, or permission to energize.
"""

from __future__ import annotations

import csv
import hashlib
import re
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import generate_hr_v0_electrical_v3_p116_observation_candidate as wrapper  # noqa: E402

OUT = ROOT / "electrical" / "kicad" / "project-button-v3-p1.16-observation-candidate"
PROJECT = "project-button-v3-p1.16-observation-candidate"
REV = "V3-P1.16-OBSERVATION-CANDIDATE"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def balanced(text: str, head: str) -> list[str]:
    blocks: list[str] = []
    for match in re.finditer(rf"(?m)^\s*\({re.escape(head)}\s*$", text):
        start = text.find("(", match.start())
        depth = 0
        quoted = escaped = False
        for index in range(start, len(text)):
            char = text[index]
            if quoted:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == '"':
                    quoted = False
                continue
            if char == '"':
                quoted = True
            elif char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
                if depth == 0:
                    blocks.append(text[start:index + 1])
                    break
    return blocks


def main() -> int:
    failures: list[str] = []

    def need(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    namespace: dict[str, object] = {"__file__": str(ROOT / "tools" / "generate_hr_v0_electrical_v3.py")}
    exec(compile(wrapper.transformed_source(), str(namespace["__file__"]), "exec"), namespace)
    sheets = namespace["sheets"]()  # type: ignore[index,operator]
    components = {component.ref: component for sheet in sheets for component in sheet.components}
    pins = [(sheet, component, pin) for sheet in sheets for component in sheet.components for pin in component.pins]
    need(namespace["PROJECT"] == PROJECT and namespace["REV"] == REV, "generator identity changed")
    need(namespace["WARNING"] == WARNING, "controlled warning changed")
    need(len(sheets) == 13, f"expected 13 child sheets, found {len(sheets)}")
    need(len(components) == 81, f"expected 81 component blocks, found {len(components)}")
    need(len(pins) == 332, f"expected 332 modeled terminals, found {len(pins)}")
    need(sheets[-1].filename == "13_runtime_observation_system.kicad_sch", "observation sheet missing or reordered")

    expected_files = {f"{PROJECT}.kicad_sch", *(sheet.filename for sheet in sheets)}
    need({path.name for path in OUT.glob("*.kicad_sch")} == expected_files, "native schematic membership differs from model")
    root_text = (OUT / f"{PROJECT}.kicad_sch").read_text(encoding="utf-8-sig")
    need(root_text.count('(property "Sheetfile"') == 13, "root hierarchy does not contain 13 child sheets")
    need('"13_runtime_observation_system.kicad_sch"' in root_text, "root hierarchy omits page 13")
    need(WARNING in root_text, "root schematic warning missing")

    expected_field = {
        "JFIELD1:1": "SR1_STATUS", "JFIELD1:2": "SRA1_STATUS",
        "JFIELD1:3": "K1_STATUS", "JFIELD1:4": "K2_STATUS",
        "JFIELD1:5": "SAFETY_0V", "JFIELD1:6": "INTENTIONALLY_UNUSED_OBS1_JFIELD1_6",
    }
    expected_logic = {
        "JLOGIC1:1": "PI_3V3_CANDIDATE", "JLOGIC1:2": "COMPUTE_0V",
        "JLOGIC1:3": "OBS_SR1_PI", "JLOGIC1:4": "OBS_SRA1_PI",
        "JLOGIC1:5": "OBS_K1_PI", "JLOGIC1:6": "OBS_K2_PI",
    }
    expected_pi = {
        "JPI1:17": "PI_3V3_CANDIDATE", "JPI1:20": "COMPUTE_0V",
        "JPI1:15": "OBS_SR1_PI", "JPI1:16": "OBS_SRA1_PI",
        "JPI1:18": "OBS_K1_PI", "JPI1:22": "OBS_K2_PI",
    }
    pinmap = lambda ref: {pin.number: pin.net for pin in components[ref].pins}
    need({key: pinmap("OBS1")[key] for key in expected_field} == expected_field, "OBS1 field mapping changed")
    need({key: pinmap("OBS1")[key] for key in expected_logic} == expected_logic, "OBS1 logic mapping changed")
    need({key: pinmap("PIOBS1")[key] for key in expected_pi} == expected_pi, "Pi physical-pin mapping changed")
    need({key: pinmap("PIOBS1")[key.replace("JLOGIC1", "JOBS1")] for key in expected_logic} == expected_logic,
         "R202-to-R204 one-for-one compute mapping changed")
    need(pinmap("JWH1") == {"1": "PI_HEARTBEAT", "2": "COMPUTE_0V"}, "heartbeat interface changed")
    need(pinmap("PI1").get("HDR40-11") == "PI_HEARTBEAT", "heartbeat no longer uses Pi physical pin 11")
    need("PI_HEARTBEAT" not in set(expected_logic.values()), "heartbeat was merged into observation logic")
    for ref in ("OBS1", "PIOBS1"):
        text = (components[ref].description + " " + components[ref].status).lower()
        need("safety credit" in text and any(term in text for term in ("zero", "no safety")), f"{ref} diagnostic-only boundary missing")

    connector = rows("connector-schedule.csv")
    need(len(connector) == 332, "connector schedule row count changed")
    expected_connector = Counter((sheet.filename, component.ref, pin.number, pin.name, pin.net, component.status)
                                 for sheet, component, pin in pins)
    actual_connector = Counter((row["sheet"], row["reference"], row["terminal"], row["pin_name"], row["net"], row["status"])
                               for row in connector)
    need(actual_connector == expected_connector, "connector schedule differs from generated model")
    need(len(rows("bom.csv")) == 79, "BOM row count changed")
    need(len(rows("net-schedule.csv")) == 112, "net schedule row count changed")
    need(len(rows("wire-number-table.csv")) == 292, "wire-number table row count changed")
    need(len(rows("unresolved-selections.csv")) == 63, "unresolved-selection row count changed")

    net_text = (OUT / "validation" / f"{PROJECT}.net").read_text(encoding="utf-8-sig")
    refs = set(re.findall(r'\(comp\s+\(ref "([^"]+)"\)', net_text))
    need(refs == set(components), "native netlist component set differs from generator")
    nodes: dict[tuple[str, str], str] = {}
    for block in balanced(net_text, "net"):
        name = re.search(r'\(name "([^"]+)"\)', block)
        if name:
            for ref, pin in re.findall(r'\(node\s+\(ref "([^"]+)"\)\s+\(pin "([^"]+)"\)', block):
                nodes[(ref, pin)] = name.group(1)
    for ref, mapping in (("OBS1", expected_field | expected_logic), ("PIOBS1", {key.replace("JLOGIC1", "JOBS1"): value for key, value in expected_logic.items()} | expected_pi)):
        for terminal, net in mapping.items():
            native = nodes.get((ref, terminal), "")
            if net.startswith("INTENTIONALLY_UNUSED"):
                need(native.startswith("unconnected-("), f"{ref}:{terminal} is not deliberately unconnected natively")
            else:
                need(native == net, f"native net mismatch at {ref}:{terminal}: {native or 'MISSING'}")
    need('(tool "Eeschema 10.0.5")' in net_text and f'(rev "{REV}")' in net_text, "native tool/revision stamp changed")

    erc = (OUT / "validation" / f"{PROJECT}-erc.rpt").read_text(encoding="utf-8-sig")
    need("ERC messages: 0  Errors 0  Warnings 0" in erc, "ERC is not 0 errors / 0 warnings")
    need("/13 Runtime diagnostic observation interfaces/" in erc, "ERC did not parse page 13")
    log = (OUT / "validation" / "kicad-cli.log").read_text(encoding="utf-8-sig")
    need(log.count("exit=0") == 4, "one or more KiCad CLI operations failed")
    svgs = sorted((OUT / "output").glob("*.svg"))
    need(len(svgs) == 14, f"expected root plus 13 SVG exports, found {len(svgs)}")
    need(any("13 Runtime diagnostic observation interfaces" in path.name for path in svgs), "page 13 SVG missing")
    for path in svgs:
        need(WARNING.encode() in path.read_bytes(), f"controlled warning missing: {path.name}")
    page13 = next((path for path in svgs if "13 Runtime diagnostic observation interfaces" in path.name), None)
    if page13:
        text = page13.read_text(encoding="utf-8-sig")
        for token in ("OBS1", "PIOBS1", "JFIELD1:6", "diagnostic only", "zero functional-safety credit"):
            need(token in text, f"page 13 export token missing: {token}")

    manifest = {row["file"]: row["sha256"] for row in rows("SOURCE-MANIFEST.csv")}
    actual = {path.relative_to(OUT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest().upper()
              for path in OUT.rglob("*") if path.is_file() and path.name != "SOURCE-MANIFEST.csv"}
    need(manifest == actual, "source manifest differs from current package")
    readme = (OUT / "README.md").read_text(encoding="utf-8-sig")
    need(WARNING in readme and REV in readme and "Generated ERC proves only modeled connectivity/annotation" in readme,
         "README warning, revision, or ERC caveat missing")

    if failures:
        print("HR-V0 P1.16 observation candidate: FAIL")
        for failure in failures:
            print("-", failure)
        return 1
    print("HR-V0 P1.16 observation candidate: PASS")
    print("  14 native pages / 81 blocks / 332 terminals / 0 ERC violations")
    print("  exact XT1-to-R202-to-R204-to-Pi diagnostic mapping; heartbeat remains separate")
    print("  no fabrication, test, safety, motion, or energization credit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
