#!/usr/bin/env python3
"""Fail-closed source, native-net and cross-subassembly checks for P1.17."""

from __future__ import annotations

import csv
import hashlib
import re
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import generate_hr_v0_electrical_v3_p117_observation_candidate as wrapper  # noqa: E402
import generate_hr_v0_electrical_v3_p115_carrier_candidate as core_wrapper  # noqa: E402

OUT = ROOT / "electrical/kicad/project-button-v3-p1.17-observation-p05-candidate"
PROJECT = "project-button-v3-p1.17-observation-p05-candidate"
REV = "V3-P1.17-OBSERVATION-P0.5-CANDIDATE"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


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


def interface_map(path: Path, references: set[str]) -> dict[tuple[str, str], str]:
    result: dict[tuple[str, str], str] = {}
    for row in rows(path):
        reference = row["reference"]
        terminal = row.get("terminal", row.get("pin", ""))
        if reference in references:
            result[(reference, terminal)] = row["net"]
    return result


def main() -> int:
    failures: list[str] = []

    def need(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    namespace: dict[str, object] = {"__file__": str(ROOT / "tools/generate_hr_v0_electrical_v3.py")}
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

    core_namespace: dict[str, object] = {"__file__": str(ROOT / "tools/generate_hr_v0_electrical_v3.py")}
    exec(compile(core_wrapper.transformed_source(), str(core_namespace["__file__"]), "exec"), core_namespace)
    core_sheets = core_namespace["sheets"]()  # type: ignore[index,operator]
    core_components = {component.ref: component for sheet in core_sheets for component in sheet.components}
    need(len(core_sheets) == 12 and len(core_components) == 79, "P1.15 core model count changed")
    need(set(components) - set(core_components) == {"OBS1", "PIOBS1"}, "P1.17 added or removed an unexpected core reference")
    need(set(core_components) <= set(components), "P1.17 omits a P1.15 core reference")

    def signature(component: object) -> tuple[object, ...]:
        return (
            component.value, component.quantity, component.status, component.description,
            component.datasheet, component.evidence,
            tuple((pin.number, pin.name, pin.net, pin.side) for pin in component.pins),
        )

    for reference, component in core_components.items():
        need(signature(components[reference]) == signature(component), f"P1.17 core component differs from P1.15: {reference}")

    need("HR-V0-RUNTIME-OBS-CARRIER-P0.5" in components["OBS1"].value, "OBS1 is not bound to P0.5")
    need("SN74LVC1G07" in components["OBS1"].evidence, "OBS1 evidence omits the G07 correction")
    need("p0.5" in components["OBS1"].datasheet.lower(), "OBS1 source path is not P0.5")
    need("safety credit" in (components["OBS1"].description + components["OBS1"].status).lower(), "OBS1 safety boundary missing")

    p05_map = interface_map(
        ROOT / "electrical/kicad/hr-v0-runtime-observation-carrier-p0.5/connector-schedule.csv",
        {"JFIELD1", "JLOGIC1"},
    )
    system_obs = {tuple(pin.number.split(":", 1)): pin.net for pin in components["OBS1"].pins}
    need(system_obs == p05_map, "system OBS1 terminal/net map differs from native P0.5 connector schedule")
    pi_map = interface_map(
        ROOT / "electrical/kicad/hr-v0-pi-observation-carrier-p0.1/connector-schedule.csv",
        {"JOBS1", "JPI1"},
    )
    pi_map = {key: net for key, net in pi_map.items() if net != "NO_NET"}
    system_pi = {tuple(pin.number.split(":", 1)): pin.net for pin in components["PIOBS1"].pins}
    need(system_pi == pi_map, "system PIOBS1 terminal/net map differs from native Pi-carrier schedule")
    need({pin.number: pin.net for pin in components["JWH1"].pins} == {"1": "PI_HEARTBEAT", "2": "COMPUTE_0V"}, "heartbeat interface changed")

    connector = rows(OUT / "connector-schedule.csv")
    expected_connector = Counter((sheet.filename, component.ref, pin.number, pin.name, pin.net, component.status)
                                 for sheet, component, pin in pins)
    actual_connector = Counter((row["sheet"], row["reference"], row["terminal"], row["pin_name"], row["net"], row["status"])
                               for row in connector)
    need(actual_connector == expected_connector, "connector schedule differs from generated model")
    need(len(rows(OUT / "bom.csv")) == 79, "BOM row count changed")
    need(len(rows(OUT / "net-schedule.csv")) == 112, "net schedule row count changed")
    need(len(rows(OUT / "wire-number-table.csv")) == 292, "wire-number table row count changed")
    need(len(rows(OUT / "unresolved-selections.csv")) == 63, "unresolved-selection row count changed")

    root_text = (OUT / f"{PROJECT}.kicad_sch").read_text(encoding="utf-8-sig")
    need(root_text.count('(property "Sheetfile"') == 13, "root hierarchy does not contain 13 child sheets")
    need(WARNING in root_text and REV in root_text, "root warning or revision missing")
    net_text = (OUT / "validation" / f"{PROJECT}.net").read_text(encoding="utf-8-sig")
    refs = set(re.findall(r'\(comp\s+\(ref "([^"]+)"\)', net_text))
    need(refs == set(components), "native netlist component set differs from generator")
    nodes: dict[tuple[str, str], str] = {}
    for block in balanced(net_text, "net"):
        name = re.search(r'\(name "([^"]+)"\)', block)
        if name:
            for reference, pin in re.findall(r'\(node\s+\(ref "([^"]+)"\)\s+\(pin "([^"]+)"\)', block):
                nodes[(reference, pin)] = name.group(1)
    for component in (components["OBS1"], components["PIOBS1"]):
        for pin in component.pins:
            native = nodes.get((component.ref, pin.number), "")
            if pin.net.startswith("INTENTIONALLY_UNUSED"):
                need(native.startswith("unconnected-("), f"{component.ref}:{pin.number} is not deliberately unconnected")
            else:
                need(native == pin.net, f"native net mismatch at {component.ref}:{pin.number}: {native or 'MISSING'}")
    need('(tool "Eeschema 10.0.5")' in net_text and f'(rev "{REV}")' in net_text, "native tool/revision stamp changed")

    erc = (OUT / "validation" / f"{PROJECT}-erc.rpt").read_text(encoding="utf-8-sig")
    need("ERC messages: 0  Errors 0  Warnings 0" in erc, "ERC is not 0 errors / 0 warnings")
    need("/13 Runtime diagnostic observation interfaces/" in erc, "ERC did not parse page 13")
    log = (OUT / "validation/kicad-cli.log").read_text(encoding="utf-8-sig")
    need(log.count("exit=0") == 4, "one or more KiCad CLI operations failed")
    svgs = sorted((OUT / "output").glob("*.svg"))
    need(len(svgs) == 14, f"expected root plus 13 SVG exports, found {len(svgs)}")
    for path in svgs:
        need(WARNING.encode() in path.read_bytes(), f"controlled warning missing: {path.name}")

    binding = rows(OUT / "observation-subassembly-binding.csv")
    need(len(binding) == 3, "binding register must contain three rows")
    by_role = {row["role"]: row for row in binding}
    p05 = ROOT / "electrical/kicad/hr-v0-runtime-observation-carrier-p0.5"
    pi = ROOT / "electrical/kicad/hr-v0-pi-observation-carrier-p0.1"
    need(by_role.get("runtime_observation_carrier", {}).get("configuration_id") == "HR-V0-RUNTIME-OBS-CARRIER-P0.5", "binding register P0.5 identity changed")
    need(by_role.get("runtime_observation_carrier", {}).get("source_manifest_sha256") == digest(p05 / "SOURCE-MANIFEST.csv"), "binding register P0.5 manifest hash changed")
    need(by_role.get("runtime_observation_carrier", {}).get("connector_schedule_sha256") == digest(p05 / "connector-schedule.csv"), "binding register P0.5 connector hash changed")
    need(by_role.get("pi_observation_carrier", {}).get("source_manifest_sha256") == digest(pi / "SOURCE-MANIFEST.csv"), "binding register Pi manifest hash changed")
    need(by_role.get("system_ecad", {}).get("connector_schedule_sha256") == digest(OUT / "connector-schedule.csv"), "binding register system connector hash changed")
    need(all(row.get("warning") == WARNING for row in binding), "binding warning changed")

    manifest = {row["file"]: row["sha256"] for row in rows(OUT / "SOURCE-MANIFEST.csv")}
    actual = {path.relative_to(OUT).as_posix(): digest(path)
              for path in OUT.rglob("*") if path.is_file() and path.name != "SOURCE-MANIFEST.csv"}
    need(manifest == actual, "source manifest differs from current package")
    readme = (OUT / "README.md").read_text(encoding="utf-8-sig")
    for token in (WARNING, REV, "HR-V0-RUNTIME-OBS-CARRIER-P0.5", "SN74LVC1G07DBVR", "Generated ERC proves only modeled connectivity/annotation"):
        need(token in readme, f"README token missing: {token}")

    if failures:
        print("HR-V0 P1.17 observation P0.5 candidate: FAIL")
        for failure in failures:
            print("-", failure)
        return 1
    print("HR-V0 P1.17 observation P0.5 candidate: PASS")
    print("  14 native pages / 81 blocks / 332 terminals / ERC 0/0")
    print("  P0.5 and Pi-carrier terminal maps plus source hashes bound exactly")
    print("  no procurement, fabrication, connection, test, safety, motion, or energization credit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
