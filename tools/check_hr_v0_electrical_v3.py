"""Validate the generated HR-V0 Electrical V3 connected candidate.

This checker proves generated-source consistency and KiCad export health only.
It does not validate component suitability, functional safety, fabrication, or
permission to energize.
"""

from __future__ import annotations

import csv
import hashlib
import re
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import generate_hr_v0_electrical_v3 as gen  # noqa: E402


OUT = ROOT / "electrical" / "kicad" / "project-button-v3"
WARNING = "PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION"


def read_csv(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def pin_map(components: dict[str, gen.Component], ref: str) -> dict[str, str]:
    return {pin.number: pin.net for pin in components[ref].pins}


def sexpr_blocks(text: str, head: str) -> list[str]:
    """Return balanced top-level blocks whose opening line is ``(head``."""
    blocks: list[str] = []
    for match in re.finditer(rf"(?m)^\s*\({re.escape(head)}\s*$", text):
        start = text.find("(", match.start())
        depth = 0
        in_string = False
        escaped = False
        for index in range(start, len(text)):
            char = text[index]
            if in_string:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == '"':
                    in_string = False
                continue
            if char == '"':
                in_string = True
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
    sheets = gen.sheets()
    components = {comp.ref: comp for sheet in sheets for comp in sheet.components}
    all_components = [(sheet, comp) for sheet in sheets for comp in sheet.components]
    all_pins = [(sheet, comp, pin) for sheet, comp in all_components for pin in comp.pins]

    require(len(sheets) == 9, f"expected 9 child sheets, found {len(sheets)}", failures)
    require(len(components) == 41, f"expected 41 unique component blocks, found {len(components)}", failures)
    require(len(all_components) == len(components), "duplicate component reference exists", failures)
    require(len(all_pins) == 198, f"expected 198 modeled terminals, found {len(all_pins)}", failures)
    require(all(re.fullmatch(r"[A-Za-z]+[0-9]+", ref) for ref in components),
            "one or more references violate KiCad annotation syntax", failures)

    expected_schematics = {f"{gen.PROJECT}.kicad_sch", *(sheet.filename for sheet in sheets)}
    actual_schematics = {path.name for path in OUT.glob("*.kicad_sch")}
    require(actual_schematics == expected_schematics,
            f"schematic file set mismatch: expected {sorted(expected_schematics)}, found {sorted(actual_schematics)}", failures)

    manifest_rows = read_csv("SOURCE-MANIFEST.csv")
    actual_manifest = {row["file"]: row["sha256"] for row in manifest_rows}
    expected_manifest = {
        path.relative_to(OUT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest().upper()
        for path in OUT.rglob("*")
        if path.is_file() and path.name != "SOURCE-MANIFEST.csv"
    }
    require(actual_manifest == expected_manifest, "source manifest differs from the current V3 file set", failures)

    connector_rows = read_csv("connector-schedule.csv")
    expected_connector = Counter(
        (sheet.filename, comp.ref, pin.number, pin.name, pin.net, comp.status)
        for sheet, comp, pin in all_pins
    )
    actual_connector = Counter(
        (row["sheet"], row["reference"], row["terminal"], row["pin_name"], row["net"], row["status"])
        for row in connector_rows
    )
    require(actual_connector == expected_connector, "connector schedule differs from generated model", failures)
    require(sum(row["terminal"].startswith("TBD-") for row in connector_rows) == 85,
            "controlled TBD-terminal count changed; review and update checker intentionally", failures)

    expected_net_counts = Counter(pin.net for _, _, pin in all_pins)
    expected_wire_numbers = gen.build_wire_numbers(sheets, expected_net_counts)
    wire_rows = read_csv("wire-number-table.csv")
    expected_wires = Counter(
        (wire_number, sheet.filename, comp.ref, pin.number, pin.name, pin.net)
        for sheet, comp, pin in all_pins
        if (wire_number := expected_wire_numbers.get((comp.ref, pin.number))) is not None
    )
    actual_wires = Counter(
        (row["wire_number"], row["sheet"], row["reference"], row["terminal"], row["pin_name"], row["net"])
        for row in wire_rows
    )
    require(actual_wires == expected_wires, "wire-number table differs from generated schematic labels", failures)
    require(len(wire_rows) == 175, f"expected 175 labeled connected terminals, found {len(wire_rows)}", failures)
    require(len({row["wire_number"] for row in wire_rows}) == len(wire_rows),
            "wire numbers are not unique", failures)

    expected_nets: dict[str, list[str]] = {}
    for sheet, comp, pin in all_pins:
        expected_nets.setdefault(pin.net, []).append(f"{sheet.filename}:{comp.ref}:{pin.number}")
    net_rows = read_csv("net-schedule.csv")
    actual_nets = {
        row["net"]: (int(row["connection_count"]), row["connections"].split(" | "))
        for row in net_rows
    }
    require(set(actual_nets) == set(expected_nets), "net schedule name set differs from generated model", failures)
    for net, connections in expected_nets.items():
        count, actual_connections = actual_nets.get(net, (-1, []))
        require(count == len(connections) and actual_connections == connections,
                f"net schedule mismatch for {net}", failures)
    require(len(expected_nets) == 76, f"expected 76 modeled nets, found {len(expected_nets)}", failures)

    native_text = (OUT / "validation" / f"{gen.PROJECT}.net").read_text(encoding="utf-8-sig")
    native_refs = set(re.findall(r'\(comp\s+\(ref "([^"]+)"\)', native_text))
    require(native_refs == set(components), "native KiCad netlist component set differs from generator", failures)
    native_node_net: dict[tuple[str, str], str] = {}
    native_net_names: list[str] = []
    for block in sexpr_blocks(native_text, "net"):
        name_match = re.search(r'\(name "([^"]+)"\)', block)
        require(name_match is not None, "native KiCad net without a name", failures)
        if name_match is None:
            continue
        name = name_match.group(1)
        native_net_names.append(name)
        for ref, pin in re.findall(r'\(node\s+\(ref "([^"]+)"\)\s+\(pin "([^"]+)"\)', block):
            key = (ref, pin)
            require(key not in native_node_net, f"native terminal {ref}:{pin} appears on multiple nets", failures)
            native_node_net[key] = name
    require(len(native_net_names) == 76, f"expected 76 native KiCad nets, found {len(native_net_names)}", failures)
    require(sum(name.startswith("unconnected-(") for name in native_net_names) == 23,
            "expected 23 deliberate native unconnected nets", failures)
    require(len(native_node_net) == 198, f"expected 198 native KiCad netlist nodes, found {len(native_node_net)}", failures)
    for _, comp, pin in all_pins:
        native_name = native_node_net.get((comp.ref, pin.number), "")
        if expected_net_counts[pin.net] == 1:
            require(native_name.startswith("unconnected-("),
                    f"singleton terminal {comp.ref}:{pin.number} is not a native unconnected net", failures)
        else:
            require(native_name == pin.net,
                    f"native net mismatch at {comp.ref}:{pin.number}: expected {pin.net}, found {native_name or 'MISSING'}", failures)
    require('(tool "Eeschema 10.0.5")' in native_text, "native netlist tool version is not Eeschema 10.0.5", failures)

    bom_rows = read_csv("bom.csv")
    expected_bom_refs = {comp.ref for _, comp in all_components if comp.quantity}
    require({row["reference"] for row in bom_rows} == expected_bom_refs,
            "V3 BOM reference set differs from nonzero-quantity generated components", failures)
    require(len(bom_rows) == 39, f"expected 39 BOM records, found {len(bom_rows)}", failures)

    unresolved_rows = read_csv("unresolved-selections.csv")
    unresolved_keys = ("SELECTION REQUIRED", "DESIGN REQUIRED", "CONFIRMATION REQUIRED", "VERIFICATION REQUIRED", "RELEASE OPEN")
    expected_unresolved = {
        (sheet.filename, comp.ref, comp.status, comp.description)
        for sheet, comp in all_components
        if any(key in comp.status for key in unresolved_keys)
    }
    actual_unresolved = {
        (row["sheet"], row["reference"], row["status"], row["evidence_needed"])
        for row in unresolved_rows
    }
    require(actual_unresolved == expected_unresolved, "unresolved-selection register differs from model", failures)
    require(len(unresolved_rows) == 29, f"expected 29 unresolved component/interface rows, found {len(unresolved_rows)}", failures)

    require(pin_map(components, "S0") == {
        "TBD-C1A": "SR1_S11", "TBD-C1B": "SR1_S12",
        "TBD-C2A": "SR1_S21", "TBD-C2B": "SR1_S22",
    }, "E-stop channel mapping changed", failures)
    require(pin_map(components, "S1")["TBD-R2"] == "SR1_START_RETURN",
            "RESET no longer returns only to SR1 monitored start", failures)
    require(pin_map(components, "S2")["TBD-A2"] == "ARM_AFTER_S2",
            "ARM output mapping changed", failures)
    require(pin_map(components, "K1")["22"] == "EDM_K1_OUT" and
            pin_map(components, "K2")["21"] == "EDM_K1_OUT" and
            pin_map(components, "K2")["22"] == "SRA1_START_RETURN",
            "K1/K2 mirror-contact EDM chain changed", failures)
    require(pin_map(components, "KWD1")["TBD-COIL+"] == "SAFETY_24V" and
            pin_map(components, "KWD1")["TBD-COIL-"] == "WD1_COIL_N" and
            pin_map(components, "Q1")["TBD-COIL"] == "WD1_COIL_N" and
            pin_map(components, "KWD2")["TBD-COIL+"] == "SAFETY_24V" and
            pin_map(components, "KWD2")["TBD-COIL-"] == "WD2_COIL_N" and
            pin_map(components, "Q2")["TBD-COIL"] == "WD2_COIL_N",
            "watchdog relay low-side coil routing changed", failures)
    require(pin_map(components, "KP1") == {
        "1L1": "K1_P1_IN", "2T1": "K1_J12", "3L2": "K1_J12",
        "4T2": "K1_J23", "5L3": "K1_J23", "6T3": "K1_OUT",
    }, "K1 three-pole series representation changed", failures)
    require(pin_map(components, "KP2") == {
        "1L1": "K1_OUT", "2T1": "K2_J12", "3L2": "K2_J12",
        "4T2": "K2_J23", "5L3": "K2_J23", "6T3": "ACT_12V_BUS",
    }, "K2 three-pole series representation changed", failures)
    require(pin_map(components, "U1")["TTL-2"].startswith("INTENTIONALLY_UNUSED"),
            "U2D2 VDD is no longer explicitly omitted", failures)
    require(pin_map(components, "U1")["TTL-1"] == "ACT_0V_PE_BONDED" and
            all(pin_map(components, ref)["TBD-BI-G"] == "ACT_0V_PE_BONDED" for ref in ("INJ1", "INJ2", "INJ3")),
            "TTL bus no longer shares the explicit actuator reference ground", failures)
    require({pin_map(components, ref)["2"] for ref in ("J1", "J2", "J3")} == {"J1_VDD", "J2_VDD", "J3_VDD"},
            "actuator VDD branches are no longer separate", failures)
    require({pin_map(components, ref)["3"] for ref in ("J1", "J2", "J3")} == {"DXL_TTL_DATA"},
            "actuator data net is no longer common", failures)
    require(components["SP1"].status.startswith("DNP - PROHIBITED"),
            "prohibited extra 0V/PE star point is no longer DNP", failures)
    for ref in ("F0", "F1", "F2", "F3", "FSR1", "FSR2"):
        require("SELECTION REQUIRED" in components[ref].status,
                f"{ref} appears released despite unresolved sizing", failures)

    erc = (OUT / "validation" / f"{gen.PROJECT}-erc.rpt").read_text(encoding="utf-8-sig")
    require("ERC messages: 0  Errors 0  Warnings 0" in erc, "KiCad ERC is not 0 errors / 0 warnings", failures)
    log = (OUT / "validation" / "kicad-cli.log").read_text(encoding="utf-8-sig")
    require(log.count("exit=0") == 4, "not all four KiCad CLI validation/export commands exited 0", failures)
    require("annotation errors" not in log.lower(), "KiCad reported annotation errors", failures)

    svg_files = sorted((OUT / "output").glob("*.svg"))
    require(len(svg_files) == 10, f"expected 10 SVG pages including index, found {len(svg_files)}", failures)
    for path in svg_files:
        require(WARNING.encode() in path.read_bytes(), f"warning missing from {path.name}", failures)
    pdf = OUT / "output" / f"{gen.PROJECT}-preliminary.pdf"
    require(pdf.is_file() and pdf.stat().st_size > 100_000, "native PDF export missing or unexpectedly small", failures)
    readme = (OUT / "README.md").read_text(encoding="utf-8-sig")
    require(WARNING in readme and "ERC proves only modeled connectivity/annotation" in readme,
            "README warning/ERC caveat missing", failures)

    if failures:
        print("HR-V0 Electrical V3 validation: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("HR-V0 Electrical V3 validation: PASS")
    print("10 native pages; 41 component blocks; 198 terminals; 53 named connected + 23 unconnected nets; 175 unique wire labels; 29 unresolved rows")
    print(WARNING)
    print("ERC/export consistency is not design approval or permission to energize.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
